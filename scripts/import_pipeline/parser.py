# parser.py — extração de texto por página (cache) e referências de mídia
"""Etapa 2: para cada doc 'indexed', extrai texto página a página com pdfplumber
(cache em data/cache/pages/{doc_id}.json) e cataloga imagens por página
(sem extrair arquivos — só contagem/ref; extração de bytes sob demanda).

O cache é a "evidência de trabalho" (§6): preserva o texto bruto para
auditoria sem reprocessar o PDF a cada execução.
"""

from __future__ import annotations

import json

from .common import CACHE_DIR, AUDIREF_RE, FIGURA_RE, conn, now


def cache_path(doc_id: str):
    return CACHE_DIR / f"{doc_id}.json"


def parse_doc(c, doc_id: str) -> dict:
    import pdfplumber

    row = c.execute("SELECT * FROM docs WHERE doc_id=?", (doc_id,)).fetchone()

    # cache válido (mesmo sha256)? reaproveita o texto; contagem de imagens por
    # página exige abrir o PDF, então refs textuais são re-mineradas do cache e
    # as de imagem só existem quando o PDF foi aberto neste banco
    cp = cache_path(doc_id)
    if cp.exists():
        try:
            cached = json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            cached = None
    else:
        cached = None
    if cached and cached.get("sha256") == row["sha256"]:
        pages_text = cached["pages"]
        media = []
        for i, text in pages_text.items():
            for m2 in FIGURA_RE.finditer(text):
                media.append({"page": int(i), "kind": "figure_ref",
                              "name": f"figura-{m2.group(1)}" + (f"-{m2.group(2)}" if m2.group(2) else ""),
                              "ref": m2.group(0)})
            for m2 in AUDIREF_RE.finditer(text):
                media.append({"page": int(i), "kind": "audio_ref", "name": m2.group(0), "ref": m2.group(0)})
        c.executemany(
            """INSERT INTO media_cand(doc_id,page,kind,name,sha256,ref) VALUES(?,?,?,?,NULL,?)
               ON CONFLICT(doc_id,page,kind,ifnull(name,'')) DO NOTHING""",
            [(doc_id, m["page"], m["kind"], m["name"], m["ref"]) for m in media],
        )
        c.execute("UPDATE docs SET status='parsed', updated_at=? WHERE doc_id=?", (now(), doc_id))
        return {"doc_id": doc_id, "pages": len(pages_text), "media_refs": len(media), "cache": "hit"}

    pages_text, media = {}, []
    with pdfplumber.open(row["path"]) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as e:
                text = ""
                c.execute("UPDATE docs SET error=COALESCE(error,'')||? WHERE doc_id=?",
                          (f"pág {i}: {e}; ", doc_id))
            pages_text[str(i)] = text
            # imagens embutidas na página (prints) — contagem, sem bytes
            try:
                n_img = len(page.images)
            except Exception:
                n_img = 0
            if n_img:
                for k in range(n_img):
                    media.append({"page": i, "kind": "image", "name": f"img-{i}-{k+1}", "ref": None})
            # referências textuais: figuras e áudios nomeados
            for m in FIGURA_RE.finditer(text):
                media.append({"page": i, "kind": "figure_ref",
                              "name": f"figura-{m.group(1)}" + (f"-{m.group(2)}" if m.group(2) else ""),
                              "ref": m.group(0)})
            for m in AUDIREF_RE.finditer(text):
                media.append({"page": i, "kind": "audio_ref", "name": m.group(0), "ref": m.group(0)})

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"doc_id": doc_id, "sha256": row["sha256"], "pages": pages_text}
    tmp = cache_path(doc_id).with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(cache_path(doc_id))

    c.executemany(
        """INSERT INTO media_cand(doc_id,page,kind,name,sha256,ref) VALUES(?,?,?,?,NULL,?)
           ON CONFLICT(doc_id,page,kind,ifnull(name,'')) DO NOTHING""",
        [(doc_id, m["page"], m["kind"], m["name"], m["ref"]) for m in media],
    )
    c.execute("UPDATE docs SET status='parsed', updated_at=? WHERE doc_id=?", (now(), doc_id))
    return {"doc_id": doc_id, "pages": len(pages_text), "media_refs": len(media)}


def run(only: list[str] | None = None) -> list[dict]:
    c = conn()
    q = "SELECT doc_id,status FROM docs WHERE status IN ('discovered','indexed')"
    if only:
        q += f" AND doc_id IN ({','.join('?' * len(only))})"
        rows = c.execute(q, only).fetchall()
    else:
        rows = c.execute(q).fetchall()
    out = []
    for r in rows:
        try:
            res = parse_doc(c, r["doc_id"])
            c.commit()
            print(f"[parser] {r['doc_id']}: {res['pages']} págs, {res['media_refs']} refs de mídia")
            out.append(res)
        except Exception as e:
            c.execute("UPDATE docs SET status='failed', error=?, updated_at=? WHERE doc_id=?",
                      (str(e), now(), r["doc_id"]))
            c.commit()
            print(f"[parser] FALHA {r['doc_id']}: {e}")
            out.append({"doc_id": r["doc_id"], "error": str(e)})
    c.close()
    return out


if __name__ == "__main__":
    run()
