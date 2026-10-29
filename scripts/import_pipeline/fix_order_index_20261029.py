# -*- coding: utf-8 -*-
"""
fix_order_index_20261029.py — rodada de 29/10/2026 (auditoria incremental).

(1) Corrige as QUATRO inversões cronológicas confirmadas (blocos movidos por IDs;
    textos, notas, IDs e proveniências preservados — nenhuma renumeração):
      - ana-matos: bloco 2024-04..10-01 para o início; bloco 2025-03-31..04-14
        desmembrado nas posições cronológicas (31/03+03/04 antes de 04/04;
        05/04 após o bloco 04/04..05/04; 14/04 antes de 18/04).
      - fabiano-zettel: [m-00034 (~ago/2024, >16/08), m-00033 (02/10/2024 12h58)]
        para entre 05/06/2024 e o bloco 2024-10.
      - paulo-henrique: bloco m-00014..m-00059 (negociação 30/04..22/05/2025,
        IPJ-A/UOL) para antes de 19/08/2025.
      - walfrido-warde: bloco m-00027..m-00043 (set/2024..22/01/2025, Veja)
        para após o bloco 2024-08, antes de 2024-11.
(2) threads.json: last_message_date das 7 conversas inconsistentes passa a ser
    a ÚLTIMA DATA CONHECIDA da conversa (máximo âncora temporal comprovado;
    mês parcial permanece YYYY-MM); previews das conversas cuja última mensagem
    do array mudou com a reordenação.

Verifica pós-movimento: conjuntos de IDs idênticos, conteúdo/nota idênticos
(hash), zero inversões sob a regra nova do validador (comparação além de
registros sem data).
"""

import json
import io
import os
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")


def load(rel):
    with io.open(os.path.join(DATA, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def save(rel, obj):
    with io.open(os.path.join(DATA, rel), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def by_id(msgs):
    return {m["id"]: m for m in msgs}


def fingerprint(msgs):
    return {m["id"]: hashlib.sha256(
        (json.dumps([m.get("content"), m.get("editorial_note"), m.get("date"),
                     m.get("time"), m.get("timestamp_precision")],
                    ensure_ascii=False)).encode("utf-8")).hexdigest()
            for m in msgs}


def new_rule_violations(items):
    """Regra nova do validador: compara registros datados além de registros
    sem data / precisão month|approximate que estejam entre eles."""
    last, out = None, []
    for it in items:
        if it.get("timestamp_precision") not in ("date", "minute"):
            continue
        d = it.get("date")
        if last:
            if d < last["date"]:
                out.append(f"{it['id']} ({d}) anterior a {last['id']} ({last['date']})")
            elif d == last["date"] and it.get("time") and last.get("time") and it["time"] < last["time"]:
                out.append(f"{it['id']} ({d} {it['time']}) antes de {last['id']} ({last['time']})")
        last = it
    return out


def reorder(tid, target_id_order):
    rel = f"threads/{tid}.json"
    t = load(rel)
    msgs = t["messages"]
    ids_before = [m["id"] for m in msgs]
    map_ = by_id(msgs)
    assert set(target_id_order) == set(ids_before) and len(target_id_order) == len(ids_before), \
        f"{tid}: conjunto de IDs divergente"
    fp_before = fingerprint(msgs)
    t["messages"] = [map_[i] for i in target_id_order]
    assert fingerprint(t["messages"]) == fp_before, f"{tid}: conteúdo alterado"
    v = new_rule_violations(t["messages"])
    assert not v, f"{tid}: inversões remanescentes: {v}"
    save(rel, t)
    print(f"[order] {tid}: {len(msgs)} mensagens reordenadas; 0 inversões (regra nova)")
    return t


# ============================================================
# (1) REORDENAÇÕES
# ============================================================

# ANA MATOS — ordem-alvo por trechos de IDs (blocos contíguos preservados)
ana = (
    # bloco 2024-04..2024-10-01 (deslocado para o início; ordem interna atual
    # já é cronológica: 19/08, 09/09, 18/09, 26..29/09, 01/10)
    ["m-00014", "m-00022", "m-00023", "m-00024", "m-00025", "m-00026",
     "m-00015", "m-00016", "m-00017",
     "m-00027", "m-00028", "m-00029",
     "m-00030", "m-00031", "m-00032", "m-00033", "m-00034",
     "m-00035", "m-00036", "m-00037"]
    + ["m-00001", "m-00002", "m-00003"]                       # 2024-11
    + [f"m-{i:05d}" for i in range(38, 47)]                   # 31/03 + 03/04/2025
    + [f"m-{i:05d}" for i in range(54, 61)]                   # 04/04..05/04
    + ["m-00048", "m-00049", "m-00050", "m-00051", "m-00052", "m-00053",
       "m-00018", "m-00019"]                                  # 05/04
    + ["m-00061", "m-00062"]                                  # 06..07/04
    + ["m-00004", "m-00005"]                                  # 11/04
    + ["m-00047"]                                             # 14/04
    + ["m-00063", "m-00064", "m-00065"]                       # 18/04
    + ["m-00066", "m-00067"]                                  # 28..29/05
    + [f"m-{i:05d}" for i in range(6, 13)]                    # 10..22/07
    + ["m-00013"]                                             # sem data (contexto Metrópoles, anexo ao bloco)
    + [f"m-{i:05d}" for i in range(68, 73)]                   # 28..30/07
    + ["m-00020", "m-00021"]                                  # 2025-09 (mês)
    + ["m-00073", "m-00074", "m-00075"]                       # 01/09
)
reorder("ana-matos-daniel-vorcaro", ana)

# FABIANO ZETTEL — [m-00034 (~ago/2024, "dias depois de 16/08"), m-00033 (02/10 12h58)]
# entre 05/06/2024 (m-00007) e o bloco 2024-10
zettel_msgs = load("threads/fabiano-zettel-daniel-vorcaro.json")["messages"]
z_ids = [m["id"] for m in zettel_msgs]
tail = [i for i in z_ids[z_ids.index("m-00037") + 4:] if i not in ("m-00033", "m-00034")]
z = (z_ids[:7]                       # m-00001..07 (24/05..05/06/2024)
     + ["m-00034", "m-00033"]        # ~ago/2024 e 02/10/2024
     + ["m-00037", "m-00038", "m-00039", "m-00040"]   # 2024-10
     + tail)                         # m-00008..32 (2025-01..03) na ordem atual
reorder("fabiano-zettel-daniel-vorcaro", z)

# PAULO HENRIQUE — bloco m-00014..59 (fl.5/6 IPJ-A + UOL 30/04..22/05/2025)
# para antes de m-00008 (19/08/2025)
ph = ([f"m-{i:05d}" for i in range(1, 8)]      # 2024-07..10-31
      + [f"m-{i:05d}" for i in range(14, 60)]  # negociação 30/04..22/05/2025
      + ["m-00008", "m-00009", "m-00010", "m-00011", "m-00012", "m-00060", "m-00013"])  # 19/08, 2025-08, 12/11
reorder("paulo-henrique-daniel-vorcaro", ph)

# WALFRIDO WARDE — bloco m-00027..43 (set/2024..22/01/2025, Veja) após 2024-08
ww = (["m-00048", "m-00049", "m-00050", "m-00001", "m-00002", "m-00003", "m-00004"]
      + [f"m-{i:05d}" for i in range(27, 44)]   # 2024-09..2025-01-22
      + ["m-00051", "m-00052", "m-00053", "m-00054", "m-00055", "m-00056", "m-00057"]
      + ["m-00005", "m-00006", "m-00007", "m-00008", "m-00058", "m-00059"]
      + [f"m-{i:05d}" for i in range(9, 27)])    # 17/11/2025 + sem data
reorder("walfrido-warde-daniel-vorcaro", ww)

# ============================================================
# (2) threads.json — last_message_date (última data conhecida) e previews
# ============================================================

def max_anchor(t):
    """Último âncora temporal conhecido: compara data plena e âncora de mês e
    devolve o MAIS RECENTE (mês posterior a toda data plena vence; mês igual
    perde para a data plena, que é mais precisa)."""
    best_date, best_month = None, None
    for m in t["messages"]:
        p = m.get("timestamp_precision")
        d = m.get("date")
        if p in ("date", "minute") and d and (best_date is None or d > best_date):
            best_date = d
        elif p in ("month", "approximate") and d and (best_month is None or d > best_month):
            best_month = d
    if best_month and (best_date is None or best_month > best_date[:7]):
        return best_month
    return best_date


rel = "threads.json"
idx = load(rel)
for e in idx:
    t = load(f"threads/{e['id']}.json")
    anchor = max_anchor(t)
    # data: atualiza quando o campo existe e diverge do máximo âncora conhecido
    if "last_message_date" in e and e["last_message_date"] != anchor:
        print(f"[index] {e['id']}: last_message_date {e['last_message_date']} -> {anchor}")
        e["last_message_date"] = anchor
    # preview: conversas cuja última mensagem do array mudou com a reordenação
    if e["id"] in ("fabiano-zettel-daniel-vorcaro", "paulo-henrique-daniel-vorcaro",
                   "walfrido-warde-daniel-vorcaro"):
        new_prev = t["messages"][-1]["content"]
        if e.get("last_message_preview") != new_prev:
            print(f"[index] {e['id']}: preview -> {new_prev[:50]!r}")
            e["last_message_preview"] = new_prev
save(rel, idx)

# ============================================================
# checagem final: regra nova em TODAS as conversas (mensagens e eventos)
# ============================================================
bad = 0
import glob
for f in sorted(glob.glob(os.path.join(DATA, "threads", "*.json"))):
    t = json.load(open(f, encoding="utf-8"))
    for coll in ("messages", "timeline_events"):
        v = new_rule_violations(t.get(coll, []))
        if v:
            bad += len(v)
            print(f"[FALHA] {t['id']} ({coll}): {v}")
print("=" * 60)
print("inversões restantes no repositório (regra nova):", bad)
assert bad == 0
print("OK")
