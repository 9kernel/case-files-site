# curate_group_cdfh.py — grupo "Ciro Daniel Fábio Hugo" (UOL 30/09/2026)
"""Primeira conversa em GRUPO do acervo: grupo criado por Ciro Nogueira em
abril/2024, com Vorcaro, Hugo Motta e Fábio Faria, para organizar encontros
(UOL, coluna Cezar Feitoza, 30/09/2026; citações verificadas na apuração
espelhada pela Gazeta do Povo, Grandi/Manfrin, mesma data).

Mesmas regras editoriais: só citação literal vira mensagem; relatos viram
eventos; sic do original preservado (literal_brackets).
"""
from __future__ import annotations

import json
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press-grupo-20261015"

UOL = ("UOL — coluna Cezar Feitoza", "2026-09-30",
       "https://noticias.uol.com.br/colunas/cezar-feitoza/2026/09/30/grupo-de-zap-para-organizar-encontros-reunia-vorcaro-ciro-motta-e-faria.htm")
GAZETA = ("Gazeta do Povo (apuração espelhada do UOL)", "2026-09-30",
          "https://www.gazetadopovo.com.br/republica/vorcaro-grupo-motta-ciro-nogueira-fabio-faria-organizar-encontros")

MSGS = [
    ("2025-08-28", "ciro-nogueira", "Acho que encima (sic) do Beto",
     "Comentário a notícia da Operação Carbono Oculto, segundo a reportagem."),
    ("2025-08-28", "ciro-nogueira", "Avisa quando tiverem indo hangar",
     "Sobre deslocamento no avião de Vorcaro, segundo a reportagem."),
    ("2025-08-28", "fabio-faria", "To indo agora", "Resposta na mesma sequência."),
    (None, "ciro-nogueira", "Amigos acho qeu (sic) eu e hugo vamos ter problemas no jantar quinta",
     "Sobre o jantar de 4/9/2025 em Brasília, adiado pela posse de Carlos Brandão no STJ, segundo a reportagem."),
    (None, "hugo-motta", "Verdade. Tinha esquecido", "Resposta à mensagem anterior."),
    ("2025-11-17", "fabio-faria", "Parabéns irmão",
     "Na noite da prisão de Vorcaro, ao enviar reportagem sobre a proposta envolvendo o grupo Fictor; Ciro Nogueira respondeu com uma figurinha, segundo a reportagem."),
]

EVENTS = [
    ("2024-04", "O grupo é criado por Ciro Nogueira com Vorcaro, Hugo Motta e Fábio Faria para organizar encontros; registros vão até 17/11/2025, dia da prisão de Vorcaro em Guarulhos, segundo a reportagem."),
    ("2025-09-04", "Jantar em Brasília entre Ciro, Motta e Vorcaro seguido de viagem planejada a Trancoso com familiares — adiado em função da posse de Carlos Brandão no STJ, segundo a reportagem."),
    (None, "A reportagem relata contexto de negócios entre Vorcaro e os integrantes: compra de projeto eólico de Fábio Faria por R$ 67,5 milhões, suspeita (negada ou não comentada) de mesadas a Ciro Nogueira, e apresentação de Motta a Vorcaro para terreno em João Pessoa e projeto de mercado de carbono. Assessorias de Motta e Ciro não se pronunciaram; a defesa de Vorcaro foi procurada; a de Fábio Faria não foi localizada."),
]


def main():
    secs = [{"publication": p, "date": d, "url": u} for p, d, u in (UOL, GAZETA)]
    msgs = []
    ordered = sorted(MSGS, key=lambda x: (x[0] or "9999-99"))
    for i, (date, sender, content, note) in enumerate(ordered, 1):
        m = {
            "id": f"m-{i:05d}", "date": date, "time": None,
            "timestamp_precision": "date" if date else None,
            "sender_id": sender,
            "content_kind": "verbatim_excerpt",
            "content": content,
            "editorial_note": note,
            "verification": {
                "level": "public_investigation", "origin": "press report",
                "authority": "Polícia Federal", "court": None, "case": None,
                "document": None, "page": None, "figure": None,
                "official_url": None, "primary_document_located": False,
                "verified_at": "2026-10-15",
            },
            "sources": {"primary": None, "secondary": secs},
            "source_ref": f"Mensagem divulgada por {UOL[0]} ({UOL[1]})",
            "added_in": ADDED_IN,
        }
        if "[" in content:
            m["literal_brackets"] = True
        if date is None:
            m.pop("timestamp_precision")
            m.pop("time")
        msgs.append(m)
    events = []
    for i, (date, content) in enumerate(EVENTS, 1):
        e = {
            "id": f"e-{i:05d}", "date": date, "time": None,
            "timestamp_precision": ("month" if date and len(date) == 7 else "date") if date else None,
            "content": content, "event_kind": "editorial_context",
            "verification": msgs[0]["verification"],
            "sources": {"primary": None, "secondary": secs[:1]},
            "source_ref": f"Relato de {UOL[0]} ({UOL[1]})",
            "added_in": ADDED_IN,
        }
        if date is None:
            e.pop("time"); e.pop("timestamp_precision")
        events.append(e)

    thread = {
        "id": "grupo-ciro-daniel-fabio-hugo",
        "title": "Ciro Daniel Fábio Hugo",
        "participants_ids": ["daniel-vorcaro", "ciro-nogueira", "hugo-motta", "fabio-faria"],
        "source": {
            "document": "UOL (coluna Cezar Feitoza), 30/09/2026: grupo de WhatsApp criado por Ciro Nogueira em abril/2024 com Vorcaro, Hugo Motta e Fábio Faria para organizar encontros; citações verificadas também na apuração espelhada pela Gazeta do Povo (mesma data).",
            "url": UOL[2],
            "pages": "Mensagens conforme transcrições divulgadas; relatos sem citação literal aparecem como eventos editoriais.",
        },
        "messages": msgs,
        "timeline_events": events,
    }
    out = REPO / "data" / "threads" / "grupo-ciro-daniel-fabio-hugo.json"
    out.write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[grupo] grupo-ciro-daniel-fabio-hugo: {len(msgs)} mensagens, {len(events)} eventos")

    # participante novo: Ciro Nogueira (distinto do advogado Ciro Soares)
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    if not any(p["id"] == "ciro-nogueira" for p in people):
        people.append({
            "id": "ciro-nogueira", "name": "Ciro Nogueira", "photo": None,
            "role": "Senador (PP-PI); ex-ministro da Casa Civil",
            "aliases": ["Ciro"],
            "summary": "Criador do grupo 'Ciro Daniel Fábio Hugo', segundo o UOL (30/09/2026). A reportagem relata suspeita de mesadas — não confirmada — e negócios com Vorcaro; sua assessoria não comentou o conteúdo das conversas. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.",
        })
        pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("[grupo] +participante ciro-nogueira")

    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    if not any(t["id"] == "grupo-ciro-daniel-fabio-hugo" for t in index):
        index.append({
            "id": "grupo-ciro-daniel-fabio-hugo", "title": "Ciro Daniel Fábio Hugo",
            "participants_ids": thread["participants_ids"],
            "message_count": len(msgs),
            "last_message_preview": msgs[-1]["content"][:80],
            "featured": False,
            "note": "Grupo de WhatsApp criado por Ciro Nogueira em abril/2024 com Vorcaro, Hugo Motta e Fábio Faria para organizar encontros, deslocamentos e compartilhar notícias (UOL, 30/09/2026).",
        })
        ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("[grupo] +índice")


if __name__ == "__main__":
    main()
