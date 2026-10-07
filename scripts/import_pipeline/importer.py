# importer.py — promove candidatos APROVADOS para as threads do site
"""Uso (após revisão humana marcar os candidatos):

  1. Em data/review/candidate_messages.json, adicione ao candidato:
       "approved": true,
       "target": { "thread_id": "felipe-mourao-daniel-vorcaro",
                   "sender_id": "felipe-mourao" }
     (thread existente ou nova; sender_id deve existir em participants.json
      — crie o participante antes, sem inventar biografia, §12)
  2. python -m scripts.import_pipeline.importer
  3. Revisar o diff; rodar node scripts/validate.mjs data

Toda mensagem importada entra como verification.level=pending_review:
 fica visível apenas no arquivo bruto/deep-link, NUNCA na renderização
 pública (filtro em js/api.js) até revisão humana promover o nível
 (missão §23/§24 — estados separados: extraído ≠ aprovado ≠ publicado).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .common import REVIEW_DIR, REPO, atomic_write_json, conn

THREADS = REPO / "data" / "threads"


def build_message(cand: dict, seq: int) -> dict:
    p = cand["provenance"]
    d = cand.get("date_hint")
    t = cand.get("time_hint")
    # horário nunca é estimado (§ "horários nunca são estimados"): sem
    # time_hint documentado, fica null e a UI mostra "horário não divulgado"
    msg = {
        "id": f"m-{seq:05d}",
        "sender_id": cand["target"]["sender_id"],
        "content": cand["quote"],
        "content_kind": "verbatim_excerpt",  # citação em narrativa = trecho
        "date": d,
        "time": t if (t and d) else None,
        "source": {
            "document_id": p["document_id"],
            "page": p["page"],
            "figure": p.get("figure"),
        },
        "verification": {
            "level": "pending_review",
            "origin": "pipeline pf-mass (lote batch)",
            "document": p["document_id"],
            "page": p["page"],
            "verified_at": None,
        },
        "sources": {"primary": {"document_id": p["document_id"], "page": p["page"]}},
        "editorial_note": "Extraído automaticamente de citação em narrativa policial; aguarda conferência no documento e definição de remetente.",
    }
    if cand.get("figure_hint"):
        msg["source"]["figure"] = cand["figure_hint"]
    return msg


def next_seq(existing: list[dict]) -> int:
    nums = [int(m["id"].split("-")[1]) for m in existing if "-" in m.get("id", "")]
    return (max(nums) + 1) if nums else 1


def run() -> int:
    src = REVIEW_DIR / "candidate_messages.json"
    if not src.exists():
        print("[importer] sem candidatos — rode o batch antes")
        return 1
    data = json.loads(src.read_text(encoding="utf-8"))
    approved = [c for c in data.get("candidates", []) if c.get("approved")]
    if not approved:
        print("[importer] nenhum candidato marcado como approved — nada a fazer")
        return 0

    by_thread: dict[str, list[dict]] = {}
    for c in approved:
        by_thread.setdefault(c["target"]["thread_id"], []).append(c)

    for thread_id, cands in by_thread.items():
        path = THREADS / f"{thread_id}.json"
        if path.exists():
            thread = json.loads(path.read_text(encoding="utf-8"))
            created = False
        else:
            print(f"[importer] thread nova '{thread_id}' — crie o JSON base e o "
                  f"participante antes de importar (§12: sem biografias inventadas)")
            continue
        seq = next_seq(thread["messages"])
        for c in cands:
            thread["messages"].append(build_message(c, seq))
            seq += 1
        atomic_write_json(path, thread)
        print(f"[importer] +{len(cands)} registro(s) pending_review em {thread_id}")

    p = subprocess.run(["node", "scripts/validate.mjs", "data"], cwd=str(REPO),
                       capture_output=True, text=True, shell=(sys.platform == "win32"))
    print((p.stdout or "").strip() or (p.stderr or "").strip())
    return p.returncode


if __name__ == "__main__":
    sys.exit(run())
