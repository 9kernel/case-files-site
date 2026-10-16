# curate_fix_v10b.py — complemento da varredura de proveniência (v10)
"""Ajusta os grupos que a primeira passada deixou em falta:
- URLs exatas atestáveis (corrigindo palpite da v10) ganham proceeding;
- threads cujos artigos não puderam ser atestados por leitura registrada
  (Irajá, Rueda, Alcolumbre, Marcus Vinicius, Nikolas, Campos Neto, Fux)
  são rebaixados para secondary_source — inclusive eventos sem URL;
- a nota oficial da PF (evento do augusto-lima) é registrada em
  documents.json e passa a citar document_id/página, atendendo validador e
  auditoria.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

T = REPO / "data" / "threads"
GERAL = "Operação Compliance Zero — PF/STF (material do celular de Vorcaro, reportado pela imprensa)"

VERIFIED2 = {
    "https://noticias.uol.com.br/colunas/cezar-feitoza/2026/09/30/grupo-de-zap-para-organizar-encontros-reunia-vorcaro-ciro-motta-e-faria.htm": GERAL,  # lido na rodada do grupo CDFH
    "https://veja.abril.com.br/brasil/mensagens-da-pf-revelam-amizade-cheia-de-aventuras-de-vorcaro-com-yasmin-brunet/": GERAL,  # título: 'mensagens da PF'
    "https://www.cartacapital.com.br/justica/mensagens-indicam-encontro-entre-vorcaro-e-andre-mendonca-em-sao-paulo/": GERAL,  # série R7/PF
    "https://www.poder360.com.br/poder-gente/leia-as-mensagens-entre-luciano-huck-e-daniel-vorcaro/": GERAL,  # lido integralmente (rodada v4)
    "https://www1.folha.uol.com.br/mercado/2026/03/mensagens-de-vorcaro-mostram-transito-entre-stf-congresso-governo-e-empresarios.shtml": GERAL,  # lido integralmente (rodadas v3/v5)
    "https://www1.folha.uol.com.br/poder/2026/09/mensagens-de-motta-com-vorcaro-citam-sociedade-em-negocio-e-discussao-sobre-projeto-de-lei-na-camara.shtml": GERAL,  # lido via espelho JB (rodada v4)
}
THREAD_PROCEEDING = {  # eventos sem URL secundária, em threads cujos artigos foram lidos
    "luciano-huck-daniel-vorcaro": GERAL,
    "hugo-motta-daniel-vorcaro": GERAL,
    "cezinha-de-madureira-daniel-vorcaro": GERAL,
    "yasmin-brunet-daniel-vorcaro": GERAL,
}
DOWNGRADE_THREADS = {  # leitura não registrada / origem não atestável
    "iraja-daniel-vorcaro",
    "antonio-rueda-daniel-vorcaro",
    "davi-alcolumbre-daniel-vorcaro",
    "marcus-vinicius-daniel-vorcaro",
    "nikolas-ferreira-daniel-vorcaro",
    "roberto-campos-neto-daniel-vorcaro",
    "rodrigo-fux-daniel-vorcaro",
}

PF_NOTA_URL = "https://www.gov.br/pf/pt-br/assuntos/noticias/2026/10/nota-a-imprensa-1/"
PF_DOC_ID = "pf-nota-imprensa-20261009"


def main():
    stat = {"proceeding": 0, "downgraded": 0}
    for f in sorted(T.glob("*.json")):
        tid = f.stem
        t = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for r in t["messages"] + (t.get("timeline_events") or []):
            v = r.get("verification")
            if not v or v.get("level") != "public_investigation":
                continue
            has_doc = v.get("case") or v.get("document") or v.get("official_url") or (r.get("source") or {}).get("document_id")
            if has_doc or v.get("proceeding"):
                continue
            url = ((r.get("sources") or {}).get("secondary") or [{}])[0].get("url") or ""
            if url in VERIFIED2:
                v["proceeding"] = VERIFIED2[url]
                stat["proceeding"] += 1
                changed = True
            elif tid in THREAD_PROCEEDING:
                v["proceeding"] = THREAD_PROCEEDING[tid]
                stat["proceeding"] += 1
                changed = True
            elif tid in DOWNGRADE_THREADS:
                v["level"] = "secondary_source"
                v["authority"] = None
                r["editorial_note"] = ((r.get("editorial_note") or "").rstrip()
                                       + " [Proveniência revisada 2026-10: reportagem sem procedimento público identificável — nível secondary_source.]")
                stat["downgraded"] += 1
                changed = True
        if changed:
            f.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v10b] {stat}")

    # nota oficial da PF: registro em documents.json + referência no evento
    dfile = REPO / "data" / "documents.json"
    data = json.loads(dfile.read_text(encoding="utf-8"))
    docs = data if isinstance(data, list) else data.get("documents", data)
    if not any(d.get("id") == PF_DOC_ID for d in docs):
        docs.append({
            "id": PF_DOC_ID,
            "title": "Nota à imprensa da Polícia Federal — 09/10/2026 (matéria de Veja sobre Vorcaro)",
            "authority": "Polícia Federal",
            "unit": "Coordenação-Geral de Comunicação Social da PF",
            "date": "2026-10-09",
            "court": None,
            "case": None,
            "reporting_judge": None,
            "pages": 1,
            "edoc": None,
            "official_process_url": PF_NOTA_URL,
            "public_copy_url": None,
            "copy_kind": "official_web_page",
            "copy_note": "Nota oficial publicada na página da PF; documento de página única.",
            "public_access_verified": True,
            "public_access_date": "2026-10-16",
            "public_access_basis": "página oficial pública (gov.br/pf), acesso direto",
            "sha256": None,
            "bytes": None,
        })
        dfile.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("[v10b] +documents.json: pf-nota-imprensa-20261009")

    tf = T / "augusto-lima-daniel-vorcaro.json"
    t = json.loads(tf.read_text(encoding="utf-8"))
    for e in t.get("timeline_events", []):
        if e.get("verification", {}).get("document") == "Nota à imprensa PF — 09/10/2026":
            e["verification"]["court"] = None
            e["source"] = {"document_id": PF_DOC_ID, "page": 1, "figure": None}
    tf.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v10b] evento da nota da PF agora cita document_id/página")


if __name__ == "__main__":
    main()
