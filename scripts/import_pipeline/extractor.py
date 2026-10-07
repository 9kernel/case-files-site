# extractor.py — minera candidatos a mensagem/evento no texto das páginas
"""Etapa 3: transforma o texto cacheado em CANDIDATOS com proveniência.

O documento PF é narrativo: mensagens literais aparecem entre aspas dentro
de frases da polícia. O extrator NUNCA promove candidato a mensagem —
ele registra citação, contexto, pista de remetente e pista de horário com
página/figura, e a promoção é sempre revisão humana (§7, §11, §24).

Regras de fidelidade (§7): a citação é preservada byte a byte do texto
extraído; nada é corrigido, expandido ou pontuado.
"""

from __future__ import annotations

import json
import re
import unicodedata

from .common import CACHE_DIR, DATE_RE, FIGURA_RE, TIME_RE, conn, now

# aspas curvas (padrão dos relatórios) e retas
QUOTE_RE = re.compile(r'[“"]([^“”"]{8,500})[”"]')

# verbos de fala antes da citação → pista de remetente
SPEAK_RE = re.compile(
    r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'’]{2,}(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'’]{2,}){0,3})"
    r"[^\w.!?]{0,30}?(?:disse|reiterou|pediu|afirmou|respondeu|perguntou|"
    r"enviou|encaminhou|reencaminhou|escreveu|informou|sinalizou|cobrou|falou)",
    re.IGNORECASE,
)

MIN_QUOTE_WORDS = 2


def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s)


def sentence_span(text: str, pos: int) -> tuple[int, int]:
    """Delimita a frase que contém `pos` (prosa da PF)."""
    start = max(text.rfind(".", 0, pos), text.rfind("\n", 0, pos)) + 1
    end_candidates = [x for x in (text.find(".", pos), text.find("\n", pos)) if x != -1]
    end = min(end_candidates) if end_candidates else len(text)
    return start, end


def mine_page(doc_id: str, page: int, text: str) -> tuple[list[dict], list[dict]]:
    quotes, events = [], []
    for m in QUOTE_RE.finditer(text):
        quote = m.group(1).strip()
        if len(quote.split()) < MIN_QUOTE_WORDS:
            continue
        # descarta sumários/rodapes/índices
        if re.match(r"^[\d.\s–-]+$", quote):
            continue
        s0, s1 = sentence_span(text, m.start())
        sentence = text[s0:s1].strip()
        # janela de parágrafo: nos relatórios da PF o timestamp e o remetente
        # frequentemente vêm na frase ANTERIOR à citação ("No dia X, às H,
        # Fulano disse ... :"), e a figura vem logo DEPOIS ("veja-se: Figura N")
        win_before = text[max(0, m.start() - 800):m.start()]
        win_after = text[m.end():m.end() + 300]
        speaker = SPEAK_RE.search(win_before[-260:])
        sender_hint = speaker.group(1) if speaker else None
        date = DATE_RE.search(win_before) or DATE_RE.search(sentence)
        time = TIME_RE.search(win_before) or TIME_RE.search(sentence)
        fig = FIGURA_RE.search(win_after) or FIGURA_RE.search(sentence)
        conf = 0.2
        if sender_hint:
            conf += 0.25
        if date and time:
            conf += 0.35
        elif date or time:
            conf += 0.1
        if fig:
            conf += 0.1
        quotes.append({
            "doc_id": doc_id, "page": page,
            "quote": quote,
            "context": sentence[:600],
            "sender_hint": sender_hint,
            "date_hint": date.group(1) if date else None,
            "time_hint": time.group(1) if time else None,
            "figure_hint": fig.group(1) if fig else None,
            "confidence": round(conf, 2),
        })
    # eventos narrativos com timestamp preciso ("No dia X, às H, ...")
    for m in re.finditer(r"(?:No dia|Em)\s+(\d{2}/\d{2}/\d{4})[^\n.]{0,200}", text):
        frag = m.group(0)
        t = TIME_RE.search(frag)
        events.append({
            "doc_id": doc_id, "page": page,
            "date": m.group(1), "time": t.group(1) if t else None,
            "summary": frag.strip()[:600],
        })
    return quotes, events


def extract_doc(c, doc_id: str) -> dict:
    path = CACHE_DIR / f"{doc_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"cache ausente para {doc_id} — rode o parser antes")
    payload = json.loads(path.read_text(encoding="utf-8"))
    quotes, events = [], []
    for pstr, text in payload["pages"].items():
        q, e = mine_page(doc_id, int(pstr), text)
        quotes.extend(q)
        events.extend(e)

    # dedup intra-doc (§11): mesma citação na mesma página = uma ocorrência;
    # citação repetida em outra página mantém AMBAS (fontes distintas)
    seen, uniq = set(), []
    for q in quotes:
        key = (q["page"], norm(q["quote"]))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(q)

    row = c.execute("SELECT header_ref FROM docs WHERE doc_id=?", (doc_id,)).fetchone()
    out = {"doc_id": doc_id, "header_ref": row["header_ref"] if row else doc_id,
           "candidate_quotes": uniq, "candidate_events": events}
    c.execute("UPDATE docs SET status='extracted', updated_at=? WHERE doc_id=?", (now(), doc_id))
    return out


def run(only: list[str] | None = None) -> list[dict]:
    c = conn()
    q = "SELECT doc_id FROM docs WHERE status='parsed'"
    if only:
        q += f" AND doc_id IN ({','.join('?' * len(only))})"
        rows = c.execute(q, only).fetchall()
    else:
        rows = c.execute(q).fetchall()
    out = []
    for r in rows:
        try:
            res = extract_doc(c, r["doc_id"])
            c.commit()
            print(f"[extractor] {r['doc_id']}: {len(res['candidate_quotes'])} citações, "
                  f"{len(res['candidate_events'])} eventos")
            out.append(res)
        except Exception as e:
            c.execute("UPDATE docs SET status='failed', error=?, updated_at=? WHERE doc_id=?",
                      (str(e), now(), r["doc_id"]))
            c.commit()
            print(f"[extractor] FALHA {r['doc_id']}: {e}")
    c.close()
    return out


if __name__ == "__main__":
    run()
