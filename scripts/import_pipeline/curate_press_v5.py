# curate_press_v5.py — rodada da tabela-final do editor (out/2026)
"""Tabela final de 17 fontes, conferida registro por registro:

- ACM Neto: conversa NOVA (Revista Oeste 02/10/2026, Isabela Jordão).
- Martha Graeff: +10 literais de 04/12/2024 (encontro com Lula) — G1 espelha
  a mesma apuração da Folha de 05/03/2026 já usada na thread.
- Luiz Rennó: Bergamo/Folha 15/09 não traz literal inédito (CNN já cobria),
  mas dá datas exatas -> upgrade de precisão + corroboração de fonte
  + eventos (decisão Alcídia e defesas Nunes Marques/Kevin Marques).
- Walfrido Warde: UOL 08/10 (material do Estadão) -> +4 literais de jul/2025
  (áudios sobre Mantega em Londres) + eventos (Mantega R$ 14 mi, audiência
  Wagner mar/2025, perguntas sobre Moraes/BRB).
- Poder360 Huck 'mensagens-mostram-proximidade': peça gêmea da já usada
  'leia-as-mensagens' (30/09), sem literais adicionais — nada a acrescentar.

Regras das rodadas anteriores mantidas: só é mensagem o que está entre
aspas na reportagem; relato vira evento editorial.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press3-20261016"
T = REPO / "data" / "threads"

OESTE = ("Revista Oeste", "2026-10-02",
         "https://revistaoeste.com/politica/vorcaro-mantinha-conversas-com-acm-neto-por-mensagens")
FOLHA_MARTHA = ("Folha de S.Paulo", "2026-03-05",
                "https://www1.folha.uol.com.br/mercado/2026/03/mensagens-de-vorcaro-mostram-transito-entre-stf-congresso-governo-e-empresarios.shtml")
G1_MARTHA = ("G1 (espelho da apuração da Folha)", "2026-03-05",
             "https://g1.globo.com/politica/noticia/2026/03/05/vorcaro-sugere-em-mensagem-que-encontro-com-lula-foi-otimo.ghtml")
BERGAMO = ("Folha de S.Paulo (coluna Mônica Bergamo)", "2026-09-15",
           "https://www1.folha.uol.com.br/colunas/monicabergamo/2026/09/dialogos-de-vorcaro-citam-filho-de-kassio-nunes-marques-e-pagamento-de-r-500-mil.shtml")
UOL_W = ("UOL (material apurado pelo Estado de S. Paulo)", "2026-10-08",
         "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/08/vorcaro-tentou-chegar-a-lula-e-moraes-para-proteger-o-master.ghtm")
GAZETA_W = ("Gazeta do Povo (resenha da apuração)", "2026-10-08",
            "https://www.gazetadopovo.com.br/republica/mensagens-revelam-que-banqueiro-tentou-nova-aproximacao-com-lula-e-moraes")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}

ACM_SRC_NOTE = ("Revista Oeste, 02/10/2026 — Isabela Jordão: diálogos obtidos pela PF no celular de "
                "Vorcaro registram encontros, troca de elogios e articulações com o então deputado "
                "ACM Neto (União Brasil-BA) e com Antônio Rueda, presidente nacional do União Brasil, "
                "entre 2023 e 2024. Apontamentos ao Coaf indicam R$ 3,6 milhões do Master e da gestora "
                "Reag a empresa ligada a ACM Neto (revelação inicial: coluna de Lauro Jardim, O Globo). "
                "ACM Neto nega ter cometido irregularidades.")

# (date|None, time|None, sender, content, note)
ACM_MSGS = [
    ("2023-10", None, "acm-neto", "Irmão, foi bom demais. Não vou mais tomar falta de jeito nenhum. Rsss",
     "Após reunião de 'conselho às quartas', segundo a reportagem."),
    ("2023-10", None, "acm-neto", "Valeu demais!!!!", None),
    ("2023-10", None, "daniel-vorcaro", "Boa. Vamos juntos. Bom estar contigo, energia boa demais", None),
    ("2024-07", None, "acm-neto",
     "Caro amigo, qd puder, pfv, me ligue. Tentei falar contigo, pois a bolsa de minha esposa rompeu e meu filho que iria nascer na sexta acabou nascendo nessa madrugada.",
     "Acrescentou, em fala indireta, que não poderia viajar a São Paulo e que um interlocutor cuidaria de remarcar ou realizar a reunião sem ele, segundo a reportagem."),
    ("2024-10-22", None, "acm-neto", "Irmão, Rueda pousa 18:30. Veja aonde e q hs deseja encontrar e me avise. Abs",
     "Sobre Antônio Rueda, presidente nacional do União Brasil, que chegaria a São Paulo às 18h30, segundo a reportagem."),
    ("2024-10-22", None, "daniel-vorcaro", "Ja no caruso?",
     "No contexto do encontro em tabacaria em São Paulo, segundo a reportagem."),
    ("2024-10-22", None, "acm-neto", "Isso. Chego em 7 lá", None),
    ("2024-10-22", None, "daniel-vorcaro", "Sala privada", None),
    ("2024-10-31", None, "acm-neto", "as coisas em Brasília estão consolidadas",
     "Fragmento citado pela reportagem em fala indireta."),
    ("2024-10-31", None, "acm-neto", "felizmente, saiu tudo como desejávamos na política",
     "Fragmento citado pela reportagem em fala indireta."),
    ("2024-10-31", None, "acm-neto", "Como sei que Rueda confirmou contigo na terça em Brasília, falamos todos juntos lá", None),
    ("2024-10-31", None, "daniel-vorcaro", "Parabéns pela condução. Você é um monstro, grande homem dessa nação",
     "Enviada após tentativa de ligação não atendida; Vorcaro diz ainda que estariam juntos na terça, segundo a reportagem."),
    ("2024-10-31", None, "acm-neto", "Depois, confirma o horário e o local que falamos", None),
]

ACM_EVENTS = [
    (None, "Os diálogos cobrem o período 2023–2024 e registram encontros periódicos entre os dois, com ACM Neto tratando Vorcaro de 'irmão' em várias conversas, segundo a reportagem.", OESTE),
    ("2024-10-22", "Encontro em tabacaria em São Paulo, com a chegada de Antônio Rueda, presidente nacional do União Brasil, anunciada para as 18h30; Vorcaro pede 'sala privada', segundo as mensagens.", OESTE),
    ("2024-10-31", "Dia do 2º turno das eleições municipais: nas mensagens, ACM Neto celebra o resultado político e combina para a terça seguinte encontro em Brasília com Rueda, com Vorcaro presente, segundo a reportagem.", OESTE),
    (None, "Apontamentos bancários reportados ao Coaf indicam R$ 3,6 milhões em pagamentos do Banco Master e da gestora Reag a empresa ligada a ACM Neto; a revelação inicial foi da coluna de Lauro Jardim, em O Globo. ACM Neto nega ter cometido irregularidades, segundo a reportagem.", OESTE),
]

MARTHA_MSGS = [
    ("2024-12-04", None, "daniel-vorcaro", "Acabou agora amor",
     "Logo após o encontro com o presidente Lula no Planalto, segundo a reportagem."),
    ("2024-12-04", None, "daniel-vorcaro", "Tudo bem?", None),
    ("2024-12-04", None, "martha-graeff", "Sim amor trabalhando", None),
    ("2024-12-04", None, "martha-graeff", "Como foi?!!", None),
    ("2024-12-04", None, "daniel-vorcaro", "Foi otimo", None),
    ("2024-12-04", None, "martha-graeff", "Yessssssssssssssss", None),
    ("2024-12-04", None, "martha-graeff", "To louca pra saber de tudo", None),
    ("2024-12-04", None, "daniel-vorcaro", "Muito forte", None),
    ("2024-12-04", None, "daniel-vorcaro", "Ele chamou presidente do banco central que vai entrar",
     "Sobre o encontro com Lula no Planalto no mesmo dia, com presença de ministros e de Gabriel Galípolo, então indicado ao Banco Central, segundo a reportagem."),
    ("2024-12-04", None, "daniel-vorcaro", "3 ministros", None),
]

MARTHA_EVENTS = [
    ("2024-12-04", "Vorcaro encontra-se com o presidente Lula no Planalto, a pedido do banqueiro e levado pelo ex-ministro Guido Mantega, com presença de ministros e de Gabriel Galípolo, então indicado ao Banco Central; o encontro não constava da agenda oficial. Lula confirmou o encontro em fevereiro de 2026 e afirmou ter dito a Vorcaro que não haveria posição política 'pró ou contra' o Master, apenas investigação técnica do Banco Central. As mensagens com Martha Graeff são do mesmo dia, segundo a reportagem.", G1_MARTHA),
]

# (conteúdo normalizado -> data exata; Bergamo 15/09/2026 corrobora a CNN)
RENNO_UPGRADE = {
    "Dominado aqui": "2024-10-01",
    "Esse aqui - 500 mil mês - mantém? kkkkkkk. Então esse aqui já era": "2025-07-04",
    "kkkkkkk": "2025-07-04",
    "Dos pagamentos essenciais está faltando a consult": "2025-08-08",
    "Esse aí. Único 'meu' que faltou": "2025-08-08",
}

RENNO_EVENTS = [
    ("2024-10-01", "O STF, por 3 votos a 2, acolhe tese favorável à destilaria Alcídia sobre responsabilidade da União por prejuízos a usinas nos anos 1980-90 — tema de indenizações bilionárias ligadas à carteira de precatórios sucroalcooleiros do Master, estimada em mais de R$ 10 bilhões pela PF. Votaram a favor Fachin, Toffoli e Nunes Marques; Nunes Marques, que se declarara inicialmente impedido, reverteu o posicionamento e desempatou, segundo a reportagem.", BERGAMO),
    (None, "A reportagem liga os diálogos a pagamentos mensais de R$ 500 mil que seriam feitos via Consult Inteligência Tributária. Em nota, a assessoria de Nunes Marques afirma que ele 'nunca votou a favor do Banco Master' e que o filho 'nunca recebeu dinheiro de Daniel Vorcaro'; a assessoria de Kevin Marques nega prestação de serviços ao Master ou recebimento de Vorcaro e informa pagamento de R$ 281,6 mil pela Consult por serviços tributários administrativos, sem relação com o STF.", BERGAMO),
]

WARDE_MSGS = [
    ("2025-07", None, "walfrido-warde",
     "Irmão, deixa te falar, o Guido está em Londres. Só daqui dez dias, mas eu acho que seria o caso de você mandar teu avião lá buscar ele...",
     "Trecho de áudio transcrito: sugere mandar o avião de Vorcaro buscar Guido Mantega em Londres para viabilizar reunião com Lula, segundo a reportagem."),
    ("2025-07", None, "walfrido-warde", "É urgente, ele vai falar com você sabe quem no domingo",
     "Dois dias depois, sobre videochamada com Mantega; a reportagem registra que Lula não é citado pelo nome na troca."),
    ("2025-07", None, "walfrido-warde", "Parabéns. Importante call. Vai dar certo",
     "Uma hora após ligação de 23 minutos entre os três, segundo a reportagem."),
    ("2025-07", None, "daniel-vorcaro", "Muito obrigado",
     "Resposta na mesma sequência, segundo a reportagem."),
]

WARDE_EVENTS = [
    ("2024-12", "Guido Mantega, contratado por Vorcaro por R$ 14 milhões como consultor para temas do governo federal, media o encontro entre Vorcaro e o presidente Lula em dezembro de 2024; o Planalto afirma que esse foi o único encontro entre os dois, segundo a reportagem.", UOL_W),
    ("2025-03", "Mensagens de Warde em março de 2025 citam possível audiência de Vorcaro com Lula com presença do senador Jaques Wagner (PT-BA), investigado na Operação Compliance Zero sob suspeita de receber benefícios para favorecer o Master no Congresso; o Planalto nega encontros além do de dezembro de 2024.", [UOL_W, GAZETA_W]),
    (None, "No fim de 2025, Vorcaro pergunta a Warde se o ministro Alexandre de Moraes teria contido atos que travavam a compra do Master pelo BRB (58% do capital) e oferece alterar viagem internacional para se encontrar com o ministro; pedia ainda que a PF fosse orientada a evitar que servidores de escalão inferior prejudicassem o banco, segundo a reportagem. O BC rejeitou a venda ao BRB em setembro de 2025 e o Master foi liquidado em novembro de 2025, um dia após a primeira prisão de Vorcaro.", UOL_W),
]

ACM_PARTICIPANT = {
    "id": "acm-neto", "name": "ACM Neto", "photo": None,
    "role": "Deputado federal (BA); ex-prefeito de Salvador",
    "aliases": ["Antônio Carlos Magalhães Neto"],
    "summary": ("Ex-prefeito de Salvador (2013–2020) e deputado federal. Segundo a Revista Oeste "
                "(02/10/2026), trocou com Vorcaro mensagens entre 2023 e 2024 com encontros, elogios e "
                "articulações envolvendo Antônio Rueda (União Brasil); apontamentos ao Coaf indicam "
                "R$ 3,6 milhões do Master e da gestora Reag a empresa a ele ligada. Nega ter cometido "
                "irregularidades. Perfil resumido exclusivamente a partir das reportagens linkadas; não "
                "constitui acusação nem conclusão sobre responsabilidade individual."),
}


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date, time):
    if time:
        return "minute"
    if not date:
        return None
    return "month" if len(date) == 7 else "date"


def secs(src):
    srcs = src if isinstance(src, list) else [src]
    return [{"publication": p, "date": d, "url": u} for p, d, u in srcs]


def new_msg(date, time, sender, content, note, src):
    prec = prec_of(date, time)
    ss = secs(src)
    m = {
        "id": "m-TEMP", "date": date, "time": time,
        "timestamp_precision": prec,
        "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": dict(VER),
        "sources": {"primary": None, "secondary": ss},
        "source_ref": f"Mensagem divulgada por {ss[0]['publication']} ({ss[0]['date']})",
        "added_in": ADDED_IN,
    }
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    if prec is None:
        m.pop("time"); m.pop("timestamp_precision")
    return m


def new_event(date, content, src):
    prec = prec_of(date, None)
    ss = secs(src)
    e = {
        "id": "e-TEMP", "date": date, "time": None,
        "timestamp_precision": prec,
        "content": content, "event_kind": "editorial_context",
        "verification": dict(VER),
        "sources": {"primary": None, "secondary": ss},
        "source_ref": f"Relato de {ss[0]['publication']} ({ss[0]['date']})",
        "added_in": ADDED_IN,
    }
    if date is None:
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
    # 1) thread nova: ACM Neto
    msgs = [new_msg(d, tm, s, c, n, OESTE) for d, tm, s, c, n in ACM_MSGS]
    msgs.sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
    for i, m in enumerate(msgs, 1):
        m["id"] = f"m-{i:05d}"
    events = []
    for i, (d, c, src) in enumerate(ACM_EVENTS, 1):
        e = new_event(d, c, src)
        e["id"] = f"e-{i:05d}"
        events.append(e)
    thread = {
        "id": "acm-neto-daniel-vorcaro",
        "title": "ACM Neto",
        "participants_ids": ["daniel-vorcaro", "acm-neto"],
        "source": {"document": ACM_SRC_NOTE, "url": OESTE[2],
                   "pages": "Mensagens conforme transcrição da(s) reportagem(ns) indicada(s) em cada registro; nada além do que foi divulgado é inferido."},
        "messages": msgs,
        "timeline_events": events,
    }
    out = T / "acm-neto-daniel-vorcaro.json"
    out.write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v5] acm-neto: {len(msgs)} mensagens, {len(events)} eventos")

    # 2) Martha: +10 (04/12/2024, encontro com Lula) + evento
    p = T / "martha-graeff-daniel-vorcaro.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    have = {norm(m["content"]) for m in t["messages"]}
    src_m = [FOLHA_MARTHA, G1_MARTHA]
    added = 0
    for d, tm, s, c, n in MARTHA_MSGS:
        if norm(c) in have:
            continue
        t["messages"].append(new_msg(d, tm, s, c, n, src_m))
        added += 1
    for d, c, src in MARTHA_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, src))
    finalize(t)
    p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v5] martha-graeff: +{added} msgs (total {len(t['messages'])}), eventos {len(t['timeline_events'])}")

    # 3) Rennó: upgrade de precisão (Bergamo corrobora) + eventos
    p = T / "luiz-renno-daniel-vorcaro.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    berg = {"publication": BERGAMO[0], "date": BERGAMO[1], "url": BERGAMO[2]}
    upgraded = 0
    for m in t["messages"]:
        want = RENNO_UPGRADE.get(m["content"])
        if not want:
            continue
        m["date"] = want
        m["timestamp_precision"] = "date"
        if not any(s.get("url") == BERGAMO[2] for s in m["sources"]["secondary"]):
            m["sources"]["secondary"].append(berg)
        upgraded += 1
    for d, c, src in RENNO_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, src))
    finalize(t)
    p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v5] luiz-renno: {upgraded} datas precisadas (Bergamo), total {len(t['messages'])} msgs, eventos {len(t['timeline_events'])}")

    # 4) Warde: +4 (jul/2025) + eventos
    p = T / "walfrido-warde-daniel-vorcaro.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    have = {norm(m["content"]) for m in t["messages"]}
    added = 0
    for d, tm, s, c, n in WARDE_MSGS:
        if norm(c) in have:
            continue
        t["messages"].append(new_msg(d, tm, s, c, n, UOL_W))
        added += 1
    for d, c, src in WARDE_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, src))
    finalize(t)
    p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v5] walfrido-warde: +{added} msgs (total {len(t['messages'])}), eventos {len(t['timeline_events'])}")

    # 5) participante novo
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    if not any(x["id"] == "acm-neto" for x in people):
        people.append(ACM_PARTICIPANT)
        print("[v5] +participante acm-neto")
    pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 6) índice: nova entrada + contagens
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    if not any(e["id"] == "acm-neto-daniel-vorcaro" for e in index):
        index.append({
            "id": "acm-neto-daniel-vorcaro", "title": "ACM Neto",
            "participants_ids": ["daniel-vorcaro", "acm-neto"],
            "message_count": len(msgs),
            "last_message_preview": msgs[-1]["content"][:80],
            "featured": False,
            "note": ACM_SRC_NOTE[:200],
        })
    for entry in index:
        fp = T / f"{entry['id']}.json"
        if not fp.exists():
            continue
        th = json.loads(fp.read_text(encoding="utf-8"))
        if entry["message_count"] != len(th["messages"]):
            entry["message_count"] = len(th["messages"])
            entry["last_message_preview"] = th["messages"][-1]["content"][:80]
    index.sort(key=lambda e: e["id"])
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v5] índice atualizado")


if __name__ == "__main__":
    main()
