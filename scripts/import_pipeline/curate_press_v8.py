# curate_press_v8.py — coluna Fabio Serapião/UOL 02/10/2026 (Motta × Câmara)
"""Complementação de 3 conversas a partir da mesma reportagem (UOL, 02/10/2026,
Fabio Serapião, Cézar Feitoza e Natália Portinari): bastidores da eleição da
Câmara (set-dez/2024), uso de imóvel e aeronave, e a declaração de influência
de Vorcaro um dia após a posse de Motta (fev/2025).

Regras aplicadas: só mensagem o que está entre aspas na reportagem (fragmentos
citados em fala indireta entram como verbatim_excerpt com nota explicando o
recorte); relatos viram eventos; defesas registradas (nota integral de Motta);
nenhuma data inventada — 'um dia após a vitória' fica no mês (2025-02), sem dia.

Dedupe (registro por registro): as threads de Fábio Faria e Hugo Motta não
tinham NADA de mai-dez/2024; Rennó nada de 2025-02.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press6-20261016"
T = REPO / "data" / "threads"

UOL_MOTTA = ("UOL — coluna Fabio Serapião (com Cézar Feitoza e Natália Portinari)", "2026-10-02",
             "https://noticias.uol.com.br/colunas/fabio-serapiao/2026/10/02/vorcaro-apoiou-ida-de-motta-a-presidencia-da-camara-e-ofereceu-aviao-e-casa.htm")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}

MOTTA_MSGS = [
    ("2024-09", None, "daniel-vorcaro", "Tenho muito orgulho de poder te chamar de amigo irmão. Estamos juntos sempre, para o que der e vier! Você tem aqui um irmão que te admira muito e estará sempre a seu lado pra qualquer guerra",
     "Trecho da mensagem de aniversário enviada a Motta em setembro/2024."),
    ("2024-09", None, "hugo-motta", "Eu que agradeço a oportunidade de conviver com uma pessoa tão correta como vc, saiba que tens um amigo para contar em todos os momentos e que estaremos sempre juntos para enfrentar os desafios que a vida nos impõe",
     "Resposta enviada tempos depois, chamando Vorcaro de irmão e agradecendo a lembrança, segundo a reportagem."),
    ("2024-10-21", None, "hugo-motta", "Posso chamar o Arthur aqui para tratar um assunto com ele?",
     "Sobre o imóvel de Vorcaro que Motta usava no período de campanha, inclusive para receber políticos — entre eles Arthur Lira, segundo a reportagem."),
    ("2024-10-21", None, "daniel-vorcaro", "Claro. Casa é sua", "Resposta na mesma sequência, segundo a reportagem."),
    ("2024-11-06", None, "daniel-vorcaro", "Ta tudo muito alinhado, ficar quieto agora e trabalhar bastidor",
     "Sobre a estratégia na disputa pela presidência da Câmara, após tratarem de convite a evento em Portugal; concordou com Motta em evitar exposição e sugeriu focar na eleição, segundo a reportagem."),
    ("2024-11-06", None, "hugo-motta", "Só o que tô procurando fazer, depois que concluir os partidos é partir para o individual com cada deputado. São 3 meses até a eleição, tempo demais", "Resposta na mesma sequência, segundo a reportagem."),
    ("2024-12-05", None, "hugo-motta", "Irmão, manda só uma msg para Arthur agradecendo que ele ligou para o Rodrigo hoje",
     "No contexto do uso do helicóptero do banqueiro por Motta e por Arthur Lira em dezembro/2024, segundo a reportagem."),
    ("2024-12-05", None, "hugo-motta", "Posso pegar o helicóptero em Congonhas?",
     "Sobre a aeronave que o levaria de São Paulo a Brasília; no mesmo dia, trataram de uso do helicóptero pelo deputado e por Arthur Lira, segundo a reportagem."),
    ("2024-12-05", None, "daniel-vorcaro", "Pode", "Resposta na mesma sequência, segundo a reportagem."),
]
MOTTA_EVENTS = [
    ("2024-09", "No início de setembro, Marcos Pereira (Republicanos-SP) retirou o nome da disputa pela presidência da Câmara, abrindo caminho para a candidatura de Motta; nos bastidores, a manobra para trocar Elmar Nascimento (candidato do grupo de Arthur Lira) por Motta foi creditada ao senador Ciro Nogueira, amigo de Vorcaro, segundo a reportagem. Além da troca de aniversário, Motta e Vorcaro conversaram ao menos quatro vezes em setembro (dias 18, 20, 24 e 25)."),
    (None, "Em outubro e novembro de 2024, com Motta já trabalhando pela Presidência da Câmara, o deputado usou um imóvel de Vorcaro, inclusive para receber políticos — entre eles Arthur Lira, um dos principais interessados na disputa, segundo a reportagem."),
    (None, "Nota de Hugo Motta: o contato com o empresariado e representantes da sociedade é 'inerente ao exercício da atividade de qualquer parlamentar'; 'os diálogos publicados não exteriorizam, portanto, qualquer tipo de mácula à minha atuação parlamentar, sendo certo que todos os meus contatos mantidos com integrantes do setor privado sempre foram pautados pela institucionalidade e pela probidade'; e a 'descontextualização proposital de conversas tem o único propósito viabilizar o desferimento de ataques pessoais às vésperas da eleição nacional de 2026'. Procurada, a defesa de Vorcaro não respondeu."),
]

FF_MSGS = [
    ("2024-05-10", None, "fabio-faria", "Isnalldinho, Dr Luizinho, Hugo etc",
     "Fragmento: Faria avisa Vorcaro sobre chamar para um encontro 'o Isnalldinho, Dr Luizinho, Hugo etc', segundo a reportagem."),
    ("2024-05-10", None, "daniel-vorcaro", "Decidir essa eleição da câmara hoje / No charuto / Kkkk",
     "Após liberar o convite do encontro a todos, sobre a eleição da Câmara, segundo a reportagem."),
    ("2024-05-24", None, "daniel-vorcaro", "só aumenta a fofoca",
     "Fragmento: pede a Faria que não toque no tema da 'fofoca da Câmara' citada em conversa anterior, porque 'só aumenta a fofoca', segundo a reportagem."),
    ("2024-05-24", None, "daniel-vorcaro", "Turma falando que eu to apoiando Hugo pra presidente da Câmara",
     "Na mesma conversa, sobre o encontro de Faria com 'Elmar e Esteves', segundo a reportagem."),
    ("2024-08-20", None, "fabio-faria", "Acho que o Artur passou um blefe no Ciro",
     "Quando a possibilidade de Motta entrar na disputa começava a surgir; o plano era atrair Lira, apoiador de Elmar Nascimento, com a promessa de que Marcos Pereira sairia caso ele apoiasse Motta, segundo a reportagem."),
    ("2024-08-20", None, "fabio-faria", "Falando q apoiaria Hugo", "Sequência da mesma mensagem, segundo a reportagem."),
    ("2024-09-03", None, "fabio-faria", "Parece que deu certo o Hugo",
     "Por volta das 20h do dia em que Marcos Pereira saiu oficialmente da disputa; em seguida, Faria enviou reportagem sobre a desistência, segundo a reportagem."),
    ("2024-09-03", None, "daniel-vorcaro", "Nossa cara", "Resposta na mesma sequência, segundo a reportagem."),
    ("2024-09-03", None, "daniel-vorcaro", "Vai ser demais se for", "Sequência da mesma conversa, segundo a reportagem."),
    ("2024-09-03", None, "fabio-faria", "Melhor q fazer o presidente. Cenário perfeito", "Resposta na mesma sequência, segundo a reportagem."),
]
FF_EVENTS = [
    ("2024-05-24", "Faria avisa Vorcaro sobre um encontro com Elmar Nascimento e Esteves e pede detalhes da 'fofoca da Câmara' citada em conversa anterior; Vorcaro pede que não toque no tema. A conversa registra que, já em maio/2024, circulava a informação de que Vorcaro apoiava Hugo Motta para a presidência da Câmara."),
]

RENNO_MSGS = [
    ("2025-02", None, "luiz-renno", "Com Hugo transita bem tbem?",
     "Um dia após a vitória de Motta na eleição da presidência da Câmara (fevereiro/2025), segundo a reportagem."),
    ("2025-02", None, "daniel-vorcaro", "Transito bem? Kkkk. Sou number 1. Amigo irmao",
     "Resposta 'em algumas mensagens seguidas', segundo a reportagem."),
    ("2025-02", None, "luiz-renno", "Boa. Então temos BC, Congresso, presidente. Trabalhar certo. Forte.",
     "Resposta otimista na mesma sequência, segundo a reportagem."),
]


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date, time):
    if time:
        return "minute"
    if not date:
        return None
    return "month" if len(date) == 7 else "date"


def new_msg(date, time, sender, content, note):
    prec = prec_of(date, time)
    m = {
        "id": "m-TEMP", "date": date, "time": time,
        "timestamp_precision": prec,
        "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": dict(VER),
        "sources": {"primary": None,
                    "secondary": [{"publication": UOL_MOTTA[0], "date": UOL_MOTTA[1], "url": UOL_MOTTA[2]}]},
        "source_ref": f"Mensagem divulgada por {UOL_MOTTA[0]} ({UOL_MOTTA[1]})",
        "added_in": ADDED_IN,
    }
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    if prec is None:
        m.pop("time"); m.pop("timestamp_precision")
    return m


def new_event(date, content):
    prec = prec_of(date, None)
    e = {
        "id": "e-TEMP", "date": date, "time": None,
        "timestamp_precision": prec,
        "content": content, "event_kind": "editorial_context",
        "verification": dict(VER),
        "sources": {"primary": None,
                    "secondary": [{"publication": UOL_MOTTA[0], "date": UOL_MOTTA[1], "url": UOL_MOTTA[2]}]},
        "source_ref": f"Relato de {UOL_MOTTA[0]} ({UOL_MOTTA[1]})",
        "added_in": ADDED_IN,
    }
    if prec is None:
        e.pop("time"); e.pop("timestamp_precision")
    return e


def finalize(t):
    t["messages"].sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
    for i, m in enumerate(t["messages"], 1):
        m["id"] = f"m-{i:05d}"
    if t.get("timeline_events"):
        t["timeline_events"].sort(key=lambda e: (e.get("date") or "9999-99", e.get("time") or "~"))
        for i, e in enumerate(t["timeline_events"], 1):
            e["id"] = f"e-{i:05d}"


def main():
    for tid, new_msgs, new_events in [
        ("hugo-motta", MOTTA_MSGS, MOTTA_EVENTS),
        ("fabio-faria", FF_MSGS, FF_EVENTS),
        ("luiz-renno", RENNO_MSGS, []),
    ]:
        p = T / f"{tid}-daniel-vorcaro.json"
        t = json.loads(p.read_text(encoding="utf-8"))
        have = {norm(m["content"]) for m in t["messages"]}
        added = 0
        for date, time, sender, content, note in new_msgs:
            if norm(content) in have:
                continue
            t["messages"].append(new_msg(date, time, sender, content, note))
            added += 1
        for date, content in new_events:
            t.setdefault("timeline_events", []).append(new_event(date, content))
        finalize(t)
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v8] {tid}: +{added} msgs (total {len(t['messages'])}), eventos {len(t['timeline_events'])}")

    # índice (contagens)
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    for entry in index:
        fp = T / f"{entry['id']}.json"
        if not fp.exists():
            continue
        th = json.loads(fp.read_text(encoding="utf-8"))
        if entry["message_count"] != len(th["messages"]):
            entry["message_count"] = len(th["messages"])
            entry["last_message_preview"] = th["messages"][-1]["content"][:80]
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v8] índice atualizado")


if __name__ == "__main__":
    main()
