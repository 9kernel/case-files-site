# batch.py — orquestrador do pipeline em lotes, com checkpoint e retomada
"""Uso: python -m scripts.import_pipeline.batch [--docs N] [--dry-run]

Fluxo por lote (§2, §21, §23, §31):
  discover → index → parse (cache) → extract (candidatos) → export revisão
  → validate.mjs (integridade dos dados públicos) → checkpoint → relatório.

Retomável: docs já 'extracted' são pulados; falhas isoladas não interrompem.
NADA entra em data/threads automaticamente (§24): candidatos vão para
data/review/ (gitignored) e a promoção é feita pelo importer após aprovação.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from .common import AUDIT_DIR, REVIEW_DIR, atomic_write_json, batch_id, conn, now
from . import extractor as extractor_mod
from . import inventory as inventory_mod
from . import parser as parser_mod

REPO = Path(__file__).resolve().parents[2]


def export_review(results: list[dict]) -> None:
    """data/review/: candidatos por documento (gitignored, área não pública)."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    msgs, events = [], []
    for r in results:
        for q in r["candidate_quotes"]:
            msgs.append({
                "candidate_id": f"cand-{q['doc_id']}-p{q['page']}-{len(msgs)+1:05d}",
                "provenance": {"document_id": q["doc_id"], "page": q["page"],
                               "figure": q["figure_hint"]},
                "quote": q["quote"], "context": q["context"],
                "sender_hint": q["sender_hint"], "date_hint": q["date_hint"],
                "time_hint": q["time_hint"], "confidence": q["confidence"],
                "state": "extracted",  # extracted → verified → approved_for_import
            })
        for e in r["candidate_events"]:
            events.append({"document_id": e["doc_id"], "page": e["page"],
                           "date": e["date"], "time": e["time"], "summary": e["summary"],
                           "state": "extracted"})
    atomic_write_json(REVIEW_DIR / "candidate_messages.json",
                      {"note": "Candidatos extraídos — NÃO publicar; revisão humana obrigatória (missão §24/§25)",
                       "count": len(msgs), "candidates": msgs})
    atomic_write_json(REVIEW_DIR / "candidate_events.json",
                      {"note": "Eventos narrativos com timestamp — revisão humana obrigatória",
                       "count": len(events), "candidates": events})


def media_review(c) -> dict:
    rows = [dict(r) for r in c.execute(
        "SELECT doc_id,page,kind,name,ref FROM media_cand ORDER BY doc_id,page")]
    by_kind: dict[str, int] = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    atomic_write_json(REVIEW_DIR / "candidate_media.json",
                      {"note": "Mídias referenciadas (prints/áudios) — extração e publicação exigem revisão",
                       "by_kind": by_kind, "items": rows})
    return by_kind


def run_validation() -> tuple[bool, str]:
    p = subprocess.run(["node", "scripts/validate.mjs", "data"], cwd=str(REPO),
                       capture_output=True, text=True, shell=(sys.platform == "win32"))
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode == 0, out.strip().splitlines()[-1] if out.strip() else ""


def write_batch_report(bid, stats, docs, media_kinds, validation) -> Path:
    rep = REPO / f"BATCH-{bid.split('-')[1].upper()}.md"
    lines = [
        f"# Relatório do lote {bid}",
        "",
        f"- Gerado em: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Documentos analisados: {stats['docs']}",
        f"- Páginas analisadas: {stats['pages']}",
        f"- Citações literais candidatas: {stats['quotes']}",
        f"- Eventos narrativos com timestamp: {stats['events']}",
        f"- Referências de mídia: {stats['media']} ({', '.join(f'{k}={v}' for k, v in sorted(media_kinds.items())) or 'nenhuma'})",
        f"- Erros de processamento: {stats['errors']}",
        f"- Mensagens importadas para o site: 0 (bloqueio de publicidade — missão §24)",
        f"- Duração: {stats['secs']:.1f}s",
        "",
        "## Documentos do lote",
        "",
        "| doc_id | peça | págs. | status | publicidade |",
        "|---|---|---|---|---|",
    ]
    for d in docs:
        lines.append(f"| `{d['doc_id']}` | {d['header_ref']} | {d['pages']} | {d['status']} | {d['public_access']} |")
    lines += [
        "",
        "## Validação",
        "",
        f"`node scripts/validate.mjs data` → {'OK' if validation[0] else 'FALHA'} — {validation[1]}",
        "",
        "Candidatos completos em `data/review/` (fora do build público).",
    ]
    rep.write_text("\n".join(lines), encoding="utf-8")
    return rep


def write_state(c, bid, stats) -> None:
    rows = [dict(r) for r in c.execute("SELECT doc_id,status,pages FROM docs")]
    atomic_write_json(AUDIT_DIR / "import-state.json", {
        "last_batch": bid,
        "status": "completed",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "documents": {r["doc_id"]: {"status": r["status"], "pages": r["pages"]} for r in rows},
        "totals": {"documents_processed": stats["docs"], "pages_processed": stats["pages"],
                   "messages_extracted": stats["quotes"] + stats["events"],
                   "messages_imported": 0, "messages_pending_review": stats["quotes"]},
        "errors": stats["error_list"],
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=30, help="tamanho do lote (docs)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    print("[batch] etapa 1/4: inventário")
    inventory_mod.run()

    c = conn()
    pending = [dict(r) for r in c.execute(
        "SELECT doc_id,status,pages,header_ref,public_access FROM docs"
        " WHERE status IN ('discovered','indexed','parsed')"
        " ORDER BY COALESCE(pages, 999999) ASC, updated_at LIMIT ?",
        (args.docs,))]
    if args.dry_run:
        for d in pending:
            print(f"[dry-run] {d['doc_id']} ({d['status']})")
        return 0
    if not pending:
        print("[batch] nada a processar — acervo em dia (retome quando chegarem novos arquivos)")
        write_state(c, batch_id(0), {"docs": 0, "pages": 0, "quotes": 0, "events": 0,
                                     "media": 0, "errors": 0, "error_list": [], "secs": 0})
        return 0

    bid_num = (c.execute("SELECT COUNT(*) n FROM batches").fetchone()["n"] or 0) + 1
    bid = batch_id(bid_num)
    c.execute("INSERT INTO batches(id,started_at,status,doc_ids) VALUES(?,?, 'running',?)",
              (bid, now(), json.dumps([d["doc_id"] for d in pending])))
    c.commit()
    print(f"[batch] {bid}: {len(pending)} documento(s)")

    print("[batch] etapa 2/4: parse (texto por página)")
    parser_mod.run(only=[d["doc_id"] for d in pending])

    print("[batch] etapa 3/4: extração de candidatos")
    results = extractor_mod.run(only=[d["doc_id"] for d in pending])

    print("[batch] etapa 4/4: export de revisão + validação")
    export_review(results)
    media_kinds = media_review(c)
    validation = run_validation()

    c = conn()
    pages = sum((r["pages"] or 0) for r in c.execute(
        f"SELECT pages FROM docs WHERE doc_id IN ({','.join('?'*len(pending))})",
        [d["doc_id"] for d in pending]))
    quotes = sum(len(r["candidate_quotes"]) for r in results)
    events = sum(len(r["candidate_events"]) for r in results)
    failed = [d["doc_id"] for d in c.execute(
        "SELECT doc_id FROM docs WHERE status='failed'")]
    stats = {"docs": len(pending), "pages": pages, "quotes": quotes, "events": events,
             "media": sum(media_kinds.values()), "errors": len(failed), "error_list": failed,
             "secs": time.time() - t0}
    c.execute("UPDATE batches SET finished_at=?, pages=?, quotes=?, events=?, media=?,"
              " errors=?, status='completed' WHERE id=?",
              (now(), pages, quotes, events, stats["media"], len(failed), bid))
    c.commit()

    docs_final = [dict(r) for r in c.execute(
        f"SELECT doc_id,header_ref,pages,status,public_access FROM docs"
        f" WHERE doc_id IN ({','.join('?'*len(pending))})", [d["doc_id"] for d in pending])]
    rep = write_batch_report(bid, stats, docs_final, media_kinds, validation)
    write_state(c, bid, stats)
    c.close()

    print(f"[batch] {bid} concluído em {stats['secs']:.1f}s — relatório: {rep.name}")
    print(f"[batch] citações candidatas: {quotes} | eventos: {events} | mídias: {stats['media']} | erros: {len(failed)}")
    if failed:
        print(f"[batch] falhas isoladas (registradas, pipeline segue): {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
