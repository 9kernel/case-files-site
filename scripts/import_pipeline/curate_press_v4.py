# curate_press_v4.py — complementação de 5 conversas existentes (set-out/2026)
"""Rodada 2026-10 (2): lacunas apontadas pelo editor, comparadas registro por
registro contra as reportagens. Só entra mensagem com citação literal; relatos
e fragmentos curtos dentro de fala indireta viram eventos.

- flavio-bolsonaro: piauí (fonte original da thread) — diff fechou em 5 novas
  (4 trechos do áudio de 08/09/2025 + 'Quarta 14h30?'); as '96 mensagens'
  completas não são divulgadas literalmente pela reportagem.
- luciano-huck: Poder360 30/09 — o literal já estava no site; novo = eventos.
- hugo-motta: Folha 28/09 (espelho JB) — fragmentos curtos -> eventos.
- luiz-renno: CNN 15/09 — 6 mensagens literais + eventos (defesas registradas).
- walfrido-warde: UOL (espelho Metro1 01/10) — 6 mensagens literais + eventos.
- fabiano-zettel (bônus da mesma apuração UOL): 4 mensagens do aporte Tayayá.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press2-20261016"
T = REPO / "data" / "threads"

PIAUI = ("Revista piauí", "2026-10-01", "https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/")
PODER = ("Poder360", "2026-09-30", "https://www.poder360.com.br/poder-gente/leia-as-mensagens-entre-luciano-huck-e-daniel-vorcaro")
FOLHA_MOTTA = ("Folha de S.Paulo", "2026-09-28",
               "https://www1.folha.uol.com.br/poder/2026/09/mensagens-de-motta-com-vorcaro-citam-sociedade-em-negocio-e-discussao-sobre-projeto-de-lei-na-camara.shtml")
JB = ("Jornal do Brasil (apuração espelhada da Folha)", "2026-10-01",
      "https://www.jb.com.br/brasil/policia/2026/09/1061056-pf-encontra-mensagens-entre-hugo-motta-e-daniel-vorcaro-sobre-terreno-em-joao-pessoa.html")
CNN = ("CNN Brasil", "2026-09-15",
       "https://www.cnnbrasil.com.br/politica/dialogos-de-vorcaro-citam-suposta-mesada-de-r-500-mil-para-filho-de-nunes")
UOL_TAY = ("UOL (apuração espelhada pelo Metro1)", "2026-10-01",
           "https://www.metro1.com.br/noticias/politica/189165")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}

# (thread, [(date|None, time|None, sender, content, note, src), ...])
NEW_MSGS = {
  "flavio-bolsonaro": [
    ("2025-09-08", None, "flavio-bolsonaro", "está na mão de Deus aí",
     "Trecho do áudio de 08/09/2025 cobrando parcelas do filme, transcrito pela piauí.", PIAUI),
    ("2025-09-08", None, "flavio-bolsonaro", "eu fico sem graça de ficar te cobrando",
     "Trecho do mesmo áudio transcrito pela piauí.", PIAUI),
    ("2025-09-08", None, "flavio-bolsonaro", "tá todo mundo tenso",
     "Trecho do mesmo áudio transcrito pela piauí.", PIAUI),
    ("2025-09-08", None, "flavio-bolsonaro", "Imagina a gente dando calote num Jim Caviezel",
     "Trecho do mesmo áudio transcrito pela piauí; Caviezel é o ator da cinebiografia.", PIAUI),
    ("2025-09", None, "daniel-vorcaro", "Quarta 14h30?",
     "Após 15/09/2025, seguido de ligação de 1min50s, segundo a reportagem.", PIAUI),
  ],
  "luiz-renno": [
    ("2024-10", None, "luiz-renno", "vencemos Alcídia",
     "Após decisão do STF no caso dos precatórios (destilaria Alcídia/Atvos), segundo a CNN.", CNN),
    ("2024-10", None, "luiz-renno", "Dominado aqui",
     "Na sequência, compartilhou o contato de Kevin Marques, filho do ministro Nunes Marques, segundo a reportagem.", CNN),
    ("2025-07", None, "luiz-renno", "Esse aqui - 500 mil mês - mantém? kkkkkkk. Então esse aqui já era",
     "Ao reenviar o contato do filho do ministro; a reportagem caracteriza os valores como alegação negada pelas defesas.", CNN),
    ("2025-07", None, "daniel-vorcaro", "kkkkkkk", "Resposta na mesma sequência.", CNN),
    ("2025-08", None, "luiz-renno", "Dos pagamentos essenciais está faltando a consult",
     "Segundo a reportagem, em referência à Consult Inteligência Tributária.", CNN),
    ("2025-08", None, "luiz-renno", "Esse aí. Único 'meu' que faltou",
     "Encaminhando novamente o contato de Kevin Marques, segundo a reportagem.", CNN),
  ],
  "walfrido-warde": [
    ("2024-08", None, "daniel-vorcaro", "Agora recebi uma info bem chata da Roberta",
     "Sobre Roberta Rangel, então mulher do ministro Dias Toffoli, segundo a apuração do UOL.", UOL_TAY),
    ("2024-08", None, "daniel-vorcaro", "Falou mal demais de mim ontem em BSB. E não entendi nada.", None, UOL_TAY),
    ("2024-08", None, "daniel-vorcaro", "Ela entrou numa ação contra mim", None, UOL_TAY),
    ("2024-08", None, "daniel-vorcaro", "Eu fui lá nela. Deixei de lado porque ela não quis desistir.", None, UOL_TAY),
    (None, None, "daniel-vorcaro", "Tá travado em vc. Eu fiz e vcs não passaram quem vai no contrato",
     "Sobre o aporte no fundo ligado ao resort Tayayá, segundo a apuração.", UOL_TAY),
    (None, None, "walfrido-warde", "Lippi acaba de dizer que ele quem está travando",
     "No contexto da reportagem, com referência a Toffoli.", UOL_TAY),
  ],
  "fabiano-zettel": [
    ("2024-05-24", None, "daniel-vorcaro", "Vc nao resolveu o aporte no fundo",
     "Sobre o aporte no fundo ligado ao resort Tayayá, segundo a apuração do UOL.", UOL_TAY),
    ("2024-05-24", None, "daniel-vorcaro", "Tayaya", None, UOL_TAY),
    ("2024-05-24", None, "daniel-vorcaro", "Estou em situação ruim", None, UOL_TAY),
    ("2024-05-24", None, "fabiano-zettel", "Aportamos os 15. Agora só falta transferir",
     "Resposta na mesma sequência, sobre os R$ 15 milhões, segundo a apuração.", UOL_TAY),
  ],
}

NEW_EVENTS = {
  "flavio-bolsonaro": [
    (None, "A extração da PF contabiliza 110 registros no período (50 mensagens de Flávio, 46 de Vorcaro, 14 ligações); há hiato por mensagens temporárias apagadas após 90 dias. Dos US$ 24 milhões prometidos para o filme, US$ 12,3 milhões teriam seguido ao fundo Havengate, segundo a piauí. Flávio negou publicamente conversas e dinheiro do Master — versão contestada pela reportagem, que diz não ter obtido resposta dele.", PIAUI),
  ],
  "luciano-huck": [
    ("2023-11-05", "Início dos registros do diálogo entre Huck e Vorcaro, em novembro de 2023, tratando de encontro em São Paulo, segundo o Poder360.", PODER),
    ("2024-05-04", "Huck convida Vorcaro para o show de Madonna no Copacabana Palace; em 14/12/2024, para uma 'pizza' com Ronaldo Fenômeno — Vorcaro não teria respondido, segundo a reportagem.", PODER),
    ("2024-12-01", "Fechamento do contrato de patrocínio do Will Bank com o grupo de Huck; a assessoria afirma que a interação 'se deu em torno da captação e da gestão do patrocínio', com contrato, notas e impostos, rescindido antes da intervenção do BC.", PODER),
    ("2025-10-28", "Huck cita em mensagem investimento de R$ 83 milhões do banco em mídia (Globo) e outros R$ 26 milhões ligados a um 'contrato pessoal', segundo a reportagem — que registra não haver, nos diálogos, indicação de ilegalidade cometida por Huck.", PODER),
    ("2025-11-17", "Na véspera da prisão de Vorcaro, Huck envia a última mensagem da série, parabenizando-o pelo anúncio da venda do Master, segundo a reportagem.", PODER),
  ],
  "hugo-motta": [
    ("2024-03", "Início do diálogo: a cunhada de Motta obtém crédito de ao menos R$ 22 milhões junto ao Master que financia, em abril, a compra de área de 400+ hectares em João Pessoa por R$ 45 milhões, segundo a reportagem.", FOLHA_MOTTA),
    ("2024-03-15", "Concluída a operação, Motta agradece a Vorcaro pela 'confiança e a parceria'; Vorcaro responde que está 'muito feliz' e chama a iniciativa de 'parceria de vida' — fragmentos citados pela reportagem, que registra tratamento de 'amigo' e 'irmão' entre os dois.", FOLHA_MOTTA),
    (None, "Vorcaro busca apoio de Motta para o projeto de lei do mercado de carbono; Motta pede estudo sobre o Fundo Garantidor de Créditos e sugere retomar o tema em Brasília, segundo a reportagem.", FOLHA_MOTTA),
    (None, "Vorcaro disponibiliza aeronave para trecho Guarulhos–Brasília de Motta. Em nota, Motta nega 'nenhum ilícito' e afirma que o empréstimo ocorreu antes de as investigações do Master se tornarem públicas.", FOLHA_MOTTA),
  ],
  "luiz-renno": [
    (None, "As mensagens fazem parte do material da PF enviado a ministros do STF; a reportagem liga os diálogos à carteira de precatórios sucroalcooleiros (acima de R$ 10 bilhões, segundo a PF) e ao julgamento da Alcídia, em que Nunes Marques votou a favor da usina após declarar-se inicialmente impedido.", CNN),
    (None, "Nunes Marques negou que o filho tenha prestado serviços ao Master e afirmou 'nunca' ter trocado mensagens com Vorcaro; a assessoria de Kevin Marques foi procurada. A defesa contesta as informações, segundo a reportagem.", CNN),
  ],
  "walfrido-warde": [
    (None, "Roberta Rangel, então mulher de Toffoli, defendia empresa que cobrava dívida milionária da família Vorcaro; havia sido sócia de Warde até 2022 e, segundo Vorcaro na conversa, seguia remunerada pelo Master. Os dois se separaram em 2025.", UOL_TAY),
    (None, "Início de 2024: Toffoli manifesta interesse em recomprar o fundo Arleen e retomar participação no resort Tayayá — vendida por R$ 20 milhões a fundo ligado a Vorcaro e Zettel —, condicionada a aporte de R$ 15 milhões. A negociação ganhou urgência quando Vorcaro soube de risco de mudança de posição de Toffoli em processo do Master no STF. Toffoli indicou Alberto Leite como comprador; o patrimônio do fundo foi transferido para empresa nas Ilhas Virgens Britânicas. Em nota, o gabinete de Toffoli afirma que as operações foram declaradas e por valores de mercado; o escritório de Warde diz que saiu da negociação antes da conclusão.", UOL_TAY),
  ],
  "fabiano-zettel": [
    (None, "Aporte de R$ 15 milhões no fundo ligado ao resort Tayayá concluído por Zettel, dentro da negociação envolvendo a recompra pelo grupo ligado a Toffoli, segundo a apuração do UOL.", UOL_TAY),
  ],
}

MONTH_PRECISION = ("flavio-bolsonaro",)  # 'Quarta 14h30?' usa mês


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def main():
    for tid in sorted(set(NEW_MSGS) | set(NEW_EVENTS)):
        new_msgs = NEW_MSGS.get(tid, [])
        p = T / f"{tid}-daniel-vorcaro.json"
        t = json.loads(p.read_text(encoding="utf-8"))
        have = {norm(m["content"]) for m in t["messages"]}
        added = 0
        for date, time, sender, content, note, src in new_msgs:
            if norm(content) in have:
                continue
            prec = "minute" if time else ("month" if date and len(date) == 7 else ("date" if date else None))
            m = {
                "id": "m-TEMP", "date": date, "time": time,
                "timestamp_precision": prec,
                "sender_id": sender, "content_kind": "verbatim_excerpt",
                "content": content,
                "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
                "verification": dict(VER),
                "sources": {"primary": None,
                            "secondary": [{"publication": src[0], "date": src[1], "url": src[2]}]},
                "source_ref": f"Mensagem divulgada por {src[0]} ({src[1]})",
                "added_in": ADDED_IN,
            }
            if date is None:
                m.pop("time"); m.pop("timestamp_precision")
            t["messages"].append(m)
            added += 1
        evs = NEW_EVENTS.get(tid, [])
        base = len(t.get("timeline_events") or [])
        for i, (date, content, src) in enumerate(evs, base + 1):
            e = {
                "id": f"e-{i:05d}", "date": date, "time": None,
                "timestamp_precision": ("month" if date and len(date) == 7 else "date") if date else None,
                "content": content, "event_kind": "editorial_context",
                "verification": dict(VER),
                "sources": {"primary": None,
                            "secondary": [{"publication": src[0], "date": src[1], "url": src[2]}]},
                "source_ref": f"Relato de {src[0]} ({src[1]})",
                "added_in": ADDED_IN,
            }
            if date is None:
                e.pop("time"); e.pop("timestamp_precision")
            t.setdefault("timeline_events", []).append(e)
        # reordena e renumera
        t["messages"].sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
        for i, m in enumerate(t["messages"], 1):
            m["id"] = f"m-{i:05d}"
        if t.get("timeline_events"):
            t["timeline_events"].sort(key=lambda e: (e.get("date") or "9999-99", e.get("time") or "~"))
            for i, e in enumerate(t["timeline_events"], 1):
                e["id"] = f"e-{i:05d}"
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v4] {tid}: +{added} msgs, +{len(evs)} eventos (total {len(t['messages'])}/{len(t['timeline_events'])})")

    # índice (contagens)
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    for entry in index:
        p = T / f"{entry['id']}.json"
        if not p.exists():
            continue
        t = json.loads(p.read_text(encoding="utf-8"))
        if entry["message_count"] != len(t["messages"]):
            entry["message_count"] = len(t["messages"])
            entry["last_message_preview"] = t["messages"][-1]["content"][:80]
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v4] índice atualizado")


if __name__ == "__main__":
    main()
