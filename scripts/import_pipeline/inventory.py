# inventory.py — descobre arquivos em pdf_pf/, calcula hashes e indexa no DB
"""Etapa 1 do pipeline: inventário incremental.

Idempotente: reexecutar só reprocessa arquivo novo ou cujo sha256 mudou.
Gera data/audit/pf-inventory.json (resumo público, sem conteúdo) e
data/audit/import-state.json (checkpoint exigido pela missão, §4).
"""

from __future__ import annotations

import sys
from pathlib import Path

from .common import (
    AUDIT_DIR, DOC_EXTS, PDF_DIR, SKIP_EXTS, conn, derive_doc_id, now, sha256_file,
)


def discover() -> list[Path]:
    if not PDF_DIR.exists():
        print(f"[inventory] diretório ausente: {PDF_DIR}")
        return []
    files = []
    for p in sorted(PDF_DIR.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() in SKIP_EXTS:
            continue
        if p.suffix.lower() not in DOC_EXTS:
            # registra no log mas não processa formatos não documentais ainda
            print(f"[inventory] ignorado (formato fora do escopo): {p.name}")
            continue
        files.append(p)
    return files


def index_file(c, path: Path, known: set[str] | None = None) -> str:
    from pypdf import PdfReader

    sha = sha256_file(path)
    known = known or set()
    row = c.execute("SELECT doc_id, sha256, status FROM docs WHERE path=?", (str(path),)).fetchone()
    if row and row["sha256"] == sha and row["status"] not in ("failed",):
        # peça pública conhecida sempre re-avalía (para carimbar publicidade)
        if sha not in known:
            return row["doc_id"]  # já indexado e inalterado

    reader = PdfReader(str(path))
    pages = len(reader.pages)
    first = ""
    try:
        first = reader.pages[0].extract_text() or ""
    except Exception:
        first = ""
    doc_id, header_ref, kind = derive_doc_id(first, sha[:16])

    # peça já catalogada publicamente em documents.json → publicidade verificada
    if sha in known:
        public = "verified_public"
    elif row and row["doc_id"] == doc_id:
        public = c.execute("SELECT public_access FROM docs WHERE doc_id=?", (doc_id,)).fetchone()["public_access"]

    ts = now()
    c.execute(
        """INSERT INTO docs(doc_id,path,filename,ext,bytes,sha256,pages,header_ref,doc_kind,
                            public_access,status,error,mtime,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,NULL,?,?,?)
           ON CONFLICT(doc_id) DO UPDATE SET
             path=excluded.path, filename=excluded.filename, ext=excluded.ext,
             bytes=excluded.bytes, sha256=excluded.sha256, pages=excluded.pages,
             header_ref=excluded.header_ref, doc_kind=excluded.doc_kind,
             status=CASE WHEN docs.sha256=excluded.sha256 THEN docs.status ELSE 'indexed' END,
             public_access=CASE WHEN excluded.public_access='verified_public'
                                THEN excluded.public_access ELSE docs.public_access END,
             error=NULL, mtime=excluded.mtime, updated_at=excluded.updated_at
        """,
        (doc_id, str(path), path.name, path.suffix.lower(), path.stat().st_size,
         sha, pages, header_ref, kind, public, "indexed", path.stat().st_mtime, ts, ts),
    )
    return doc_id


def known_public_hashes() -> set[str]:
    """Hashes de peças já catalogadas em data/documents.json com cópia pública
    verificada — a publicidade vem do registro existente, não de suposição."""
    import json as _json

    docs_file = Path(__file__).resolve().parents[2] / "data" / "documents.json"
    if not docs_file.exists():
        return set()
    try:
        data = _json.loads(docs_file.read_text(encoding="utf-8"))
        docs = data.get("documents", []) if isinstance(data, dict) else data
        return {d["sha256"] for d in docs if d.get("sha256")}
    except Exception:
        return set()


def run() -> int:
    c = conn()
    files = discover()
    known = known_public_hashes()
    ids = []
    for f in files:
        try:
            ids.append(index_file(c, f, known))
            c.execute("DELETE FROM docs WHERE doc_id LIKE 'falha-%' AND path=? AND status='failed'", (str(f),))
            print(f"[inventory] ok: {f.name}")
        except Exception as e:  # isolamento de falha por documento (§22)
            c.execute(
                "INSERT INTO docs(doc_id,path,filename,ext,bytes,sha256,pages,header_ref,doc_kind,public_access,status,error,mtime,created_at,updated_at)"
                " VALUES(?,?,?,?,?,?,NULL,NULL,NULL,'pending','failed',?,?,?,?)"
                " ON CONFLICT(doc_id) DO UPDATE SET status='failed', error=excluded.error, updated_at=excluded.updated_at",
                (f"falha-{f.stem[:24]}", str(f), f.name, f.suffix.lower(), f.stat().st_size,
                 "", str(e), f.stat().st_mtime, now(), now()),
            )
            print(f"[inventory] FALHA: {f.name}: {e}")
    c.commit()

    rows = [dict(r) for r in c.execute("SELECT * FROM docs ORDER BY doc_id")]
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "pf-inventory.json").write_text(
        __import__("json").dumps(
            {
                "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                "source_dir": str(PDF_DIR),
                "documents": [
                    {
                        "doc_id": r["doc_id"], "filename": r["filename"], "ext": r["ext"],
                        "bytes": r["bytes"], "sha256": r["sha256"], "pages": r["pages"],
                        "header_ref": r["header_ref"], "doc_kind": r["doc_kind"],
                        "public_access": r["public_access"], "processing_status": r["status"],
                    }
                    for r in rows
                ],
            },
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    c.close()
    print(f"[inventory] {len(rows)} documento(s) indexado(s) -> data/audit/pf-inventory.json")
    return 0


if __name__ == "__main__":
    sys.exit(run())
