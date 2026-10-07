# curate_ph_brb.py — conversa Vorcaro ↔ Paulo Henrique (BRB) + enriquecimento Angelo
"""Rodada 2026-10-07 (2): IPJ-A nº 1252786/2026 (pacote Pet 16704).

Todas as mensagens foram conferidas contra o texto extraído da página
(citação = substring exata; data/hora só quando documentada na frase).
«Só penso em comprarmos a XP.»: o fechamento das aspas não consta na
camada de texto do PDF — o corte é na fronteira de frase, anotado.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-pf2-20261007"
DOC = "pf-ipja-1252786-2026"
DOC_TITLE = "IPJ-A nº 1252786/2026 — Análise de conteúdo (conversa Vorcaro × Paulo Henrique/BRB)"
DOC_REF = "IPJ-A nº 1252786/2026"

# (quote, página, figura, data, hora, remetente)
MSGS = [
    ("Fechado", 5, 2, None, None, "paulo-henrique"),
    ("Bom dia, Daniel. Quando enviar a lista de ativos, por favor, dê um sinal aqui. Abs",
     5, 2, "2024-07-04", None, "paulo-henrique"),
    ("Bom dia tudo bem? Vou te mandar por aqui agora pra dar uma olhada. Ai depois envio o email formal. A taxa de curva já está atrativa, então fica a seu critério negociarmos em seguida um desagio, ou uma operação de swap garantindo uma outra taxa",
     5, 2, "2024-07-04", None, "daniel-vorcaro"),
    ("Vou usar esse fip especifico para isso, embaixo de um fim nosso", 6, 3, None, None, "daniel-vorcaro"),
    ("Ótimo. É um veículo excelente. Já estamos analisando as carteiras de CRI e CCB. A equipe também vai abrir discussão sobre aquisição de carteiras de consignado e cartão consignado benefícios. Vc prefere indicar alguém ou seguimos com os canais que já temos abertos?",
     6, 3, None, None, "paulo-henrique"),
    ("Sobre aquisição carteira e consignado vou te passar uma pessoa pra tratar no banco",
     7, 4, None, None, "daniel-vorcaro"),
    ("Bom demais. Estou animado", 10, 7, None, None, "daniel-vorcaro"),
    ("Eu também. Muito.", 10, 7, "2024-09-18", None, "paulo-henrique"),
    ("Só penso em comprarmos a XP.", 10, 7, "2024-09-19", None, "paulo-henrique"),
    ("precisaria dar menos explicação", 13, 10, None, None, "paulo-henrique"),
    ("Amigo, estamos juntos agora", 227, None, "2024-10-31", None, "daniel-vorcaro"),
    ("Vamos enfrentar muita coisa ainda em conjunto", 227, None, "2024-10-31", None, "daniel-vorcaro"),
    ("Estamos juntos mesmo para a vida", 227, None, "2024-10-31", None, "paulo-henrique"),
    ("Se mandarmos alguém para a Bahia no final de semana para ver com eles, não funciona?",
     36, 32, None, None, "paulo-henrique"),
    ("Sim", 77, 78, "2025-11-12", None, "daniel-vorcaro"),
]

EVENTS = [
    (None, "Paulo Henrique encaminha e-mail institucional e modelo de ofício de compromisso de investimento em ações do BRB, após a apresentação inicial de Vorcaro (fl. 5, fig. 2).", 5, 2),
    (None, "Vorcaro encaminha o contato de Alberto Felix para tratar aquisição de carteira e consignado no banco — ver conversa com Alberto Felix neste arquivo (fl. 7, fig. 4).", 7, 4),
    ("2024-07-12", "Paulo Henrique comunica a Vorcaro que o NPL fora fechado naquele dia (fl. 7).", 7, None),
]

# enriquecimento da conversa com Angelo (fl. 148, fig. 169)
ANGELO_MSGS = [
    ("da uma olhada no considerando...", 148, 169, None, None, "angelo-silva"),
    ("so tirot", 148, 169, None, None, "daniel-vorcaro"),
    ("No contrato foi tirado a referência do MOU com o Pereto e qq outra vinculação.",
     148, 169, None, None, "angelo-silva"),
]


def msg_obj(seq, quote, page, figure, date, time, sender, ctx):
    prec = "minute" if time else ("date" if date else None)
    m = {
        "id": f"m-{seq:05d}",
        "date": date, "time": time,
        "timestamp_precision": prec,
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": quote,
        "editorial_note": ctx,
        "source": {"document_id": DOC, "page": page, "figure": figure},
        "verification": {
            "level": "official_document", "origin": "PF extraction",
            "authority": "Polícia Federal", "court": "STF", "case": None,
            "document": DOC_REF, "page": page, "figure": figure,
            "official_url": None, "primary_document_located": True,
            "verified_at": "2026-10-07",
        },
        "sources": {
            "primary": {
                "type": "official_document", "document_id": DOC,
                "authority": "Polícia Federal", "court": "STF", "case": None,
                "document": DOC_REF, "page": page, "figure": figure, "url": None,
            },
            "secondary": [],
        },
        "source_ref": f"PF · {DOC_REF} · fl. {page}" + (f" · fig. {figure}" if figure else ""),
        "added_in": ADDED_IN,
    }
    if prec is None:
        m.pop("timestamp_precision")
    if time is None:
        m.pop("time")
    return m


def main():
    # ---- thread nova: Paulo Henrique ----
    notes = {
        "Fechado": "Resposta de Paulo Henrique à apresentação de Vorcaro; na sequência encaminha e-mail institucional com modelo de ofício do BRB (fl. 5).",
        "Só penso em comprarmos a XP.": "A camada de texto do PDF não fecha as aspas após esta frase; o corte foi feito na fronteira de sentença — o trecho seguinte é narrativa da PF.",
        "Sim": "Resposta de Vorcaro após o envio de reportagem sobre devolução de carteiras de crédito consignado pelo BRB e imagem de visualização única (fl. 77).",
        "Eu também. Muito.": "Após chamada de voz de 1min03s; a mensagem seguinte («Só penso em comprarmos a XP.») é do dia seguinte, 19/09/2024, conforme o relatório.",
    }
    msgs = []
    seq = 1
    ordered = sorted(
        [(dt or "9999", tm or "~", q, p, f, dt, tm, s) for q, p, f, dt, tm, s in MSGS],
        key=lambda x: (x[0], x[1]),
    )
    for _d, _t, q, p, f, dt, tm, s in ordered:
        msgs.append(msg_obj(seq, q, p, f, dt, tm, s, notes.get(q) or
                             "Citação literal conforme transcrita na narrativa do IPJ-A."))
        seq += 1
    events = []
    for i, (dt, content, page, fig) in enumerate(EVENTS, 1):
        e = {
            "id": f"e-{i:05d}", "date": dt, "time": None,
            "timestamp_precision": "date" if dt else None,
            "content": content, "event_kind": "editorial_context",
            "source": {"document_id": DOC, "page": page, "figure": fig},
            "verification": msgs[0]["verification"] | {"page": page, "figure": fig},
            "source_ref": f"PF · {DOC_REF} · fl. {page}" + (f" · fig. {fig}" if fig else ""),
            "added_in": ADDED_IN,
        }
        if dt is None:
            e.pop("time"); e.pop("timestamp_precision")
        events.append(e)

    thread = {
        "id": "paulo-henrique-daniel-vorcaro",
        "title": "Paulo Henrique (BRB)",
        "participants_ids": ["daniel-vorcaro", "paulo-henrique"],
        "source": {
            "document": f"PF · {DOC_TITLE} (pacote Pet 16704)",
            "url": "",
            "pages": "Conversa declarada nos 'trechos do bate-papo entre VORCARO e PAULO HENRIQUE' ao longo do relatório. Paulo Henrique Costa era o então presidente do BRB, segundo o próprio documento. Citações literais conforme a narrativa; datas apenas quando documentadas.",
        },
        "messages": msgs,
        "timeline_events": events,
    }
    (REPO / "data" / "threads" / "paulo-henrique-daniel-vorcaro.json").write_text(
        json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[curate] paulo-henrique-daniel-vorcaro: {len(msgs)} mensagens, {len(events)} eventos")

    # ---- enriquecimento: Angelo ----
    apath = REPO / "data" / "threads" / "angelo-silva-daniel-vorcaro.json"
    at = json.loads(apath.read_text(encoding="utf-8"))
    existing = {re.sub(r"\W", "", m["content"].lower())[:60] for m in at["messages"]}
    added = 0
    seq = max(int(m["id"].split("-")[1]) for m in at["messages"]) + 1
    for q, p, f, dt, tm, s in ANGELO_MSGS:
        if re.sub(r"\W", "", q.lower())[:60] in existing:
            continue
        ctx = ("A PF anota que «so tirot» seria provavelmente 'só tirou', com erros de grafia (fl. 148)."
               if q == "so tirot" else
               "Citação literal conforme a narrativa do IPJ-A 1252786/2026 (fl. 148, fig. 169).")
        at["messages"].append(msg_obj(seq, q, p, f, dt, tm, s, ctx))
        seq += 1
        added += 1
    at["messages"].sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
    for i, m in enumerate(at["messages"], 1):
        m["id"] = f"m-{i:05d}"
    apath.write_text(json.dumps(at, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[curate] angelo-silva: +{added} mensagens (total {len(at['messages'])})")


if __name__ == "__main__":
    main()
