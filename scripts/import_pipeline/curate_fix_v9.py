# curate_fix_v9.py — auditoria e correção (Metrópoles 09-10 e 16-04 + revisões)
"""Itens da rodada de auditoria do editor:

1. paulo-henrique +5 literais de 19/08/2025 (votação BRB na CLDF; Metrópoles
   09/10) — a nota de Edinho Silva é registrada como contestação; NADA presume
   contato direto com ele: a única fonte da 'acionamento' é a própria fala de
   Vorcaro, e assim a nota declara.
2. paulo-henrique +7 sequências (Metrópoles 16/04, coluna Grande Angular, que
   reproduz mensagens citadas na decisão do Min. André Mendonça que autorizou
   a prisão de Paulo Henrique na 4ª fase da Compliance Zero) — todas sem data
   na reportagem; suspeitas registradas como alegações investigativas.
   3º diálogo (Vorcaro → corretora, nome preservado) entra como EVENTO.
3. Thread NOVA daniel-monteiro (advogado) — 6 literais da mesma coluna.
4. felipe-mourao — correções de atribuição verificadas NO DOCUMENTO PRIMÁRIO
   (IPJ-A 1020625 p.5; repr PET 15.499 p.9 e p.104):
   - m-00033 'no momento em que estou...' é de HENRIQUE Vorcaro a MARILSON
     (p.9) — não pertence a esta conversa: REMOVIDA;
   - m-00088 'lá tem a sucinta...' é de MARILSON a WANDER (p.104) — REMOVIDA;
   - m-00034 'Vai ser 1mm como normalmente?' é pergunta de ANA CLAUDIA
     Financeiro a DV (p.5) — MOVIDA para a conversa dela, remetente corrigido;
   - m-00029: nome de familiar suprimido no conteúdo (a nota já prometia a
     supressão); supressão marcada entre colchetes, nunca como reprodução
     integral.
5. flavio-bolsonaro — m-00014..17 são trechos do MESMO áudio de 08/09/2025 já
   transcrito (parcialmente) em m-00009: trechos consolidados na transcrição
   única (na ordem em que a piauí os cita), mensagens duplicadas removidas.

Nada é promovido a official_document sem documento público localizado; as
novas de Paulo Henrique/Monteiro são public_investigation (fonte jornalística
que reproduz decisão judicial).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "audit-fix-20261016"
T = REPO / "data" / "threads"

METRO_BRB = ("Metrópoles (Gabriella Furquim; apuração do Fatos On-line)", "2026-10-09",
             "https://www.metropoles.com/brasil/vorcaro-disse-ter-acionado-presidente-do-pt-para-viabilizar-compra-do-master-diz-site")
METRO_GA = ("Metrópoles — coluna Grande Angular", "2026-04-16",
            "https://www.metropoles.com/colunas/grande-angular/veja-troca-de-mensagens-entre-vorcaro-e-paulo-henrique")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date):
    return "month" if date and len(date) == 7 else ("date" if date else None)


def secs(src):
    return [{"publication": p, "date": d, "url": u} for p, d, u in (src if isinstance(src, list) else [src])]


def new_msg(date, sender, content, note, src):
    prec = prec_of(date)
    ss = secs(src)
    m = {
        "id": "m-TEMP", "date": date,
        "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": dict(VER),
        "sources": {"primary": None, "secondary": ss},
        "source_ref": f"Mensagem divulgada por {ss[0]['publication']} ({ss[0]['date']})",
        "added_in": ADDED_IN,
    }
    if date:
        m["time"] = None
        m["timestamp_precision"] = prec
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    return m


def new_event(date, content, src):
    prec = prec_of(date)
    e = {
        "id": "e-TEMP", "date": date,
        "content": content, "event_kind": "editorial_context",
        "verification": dict(VER),
        "sources": {"primary": None, "secondary": secs(src)},
        "source_ref": f"Relato de {secs(src)[0]['publication']} ({secs(src)[0]['date']})",
        "added_in": ADDED_IN,
    }
    if date:
        e["time"] = None
        e["timestamp_precision"] = prec
    return e


def finalize(t):
    t["messages"].sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
    for i, m in enumerate(t["messages"], 1):
        m["id"] = f"m-{i:05d}"
    if t.get("timeline_events"):
        t["timeline_events"].sort(key=lambda e: (e.get("date") or "9999-99", e.get("time") or "~"))
        for i, e in enumerate(t["timeline_events"], 1):
            e["id"] = f"e-{i:05d}"


def load(tid):
    return json.loads((T / f"{tid}-daniel-vorcaro.json").read_text(encoding="utf-8"))


def save(tid, t):
    (T / f"{tid}-daniel-vorcaro.json").write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    # ---------- 1) Paulo Henrique: 19/08/2025 (votação BRB) ----------
    t = load("paulo-henrique")
    have = {norm(m["content"]) for m in t["messages"]}
    brb = [
        ("2025-08-19", "paulo-henrique", "Tem uma orientação do PT Nacional de obstruir a votação",
         "Sobre a votação, na CLDF, do projeto relativo à compra do Master pelo BRB, no dia 19/08/2025, segundo a reportagem."),
        ("2025-08-19", "daniel-vorcaro", "O presidente Lula apoia ou não a operação?", None),
        ("2025-08-19", "daniel-vorcaro", "Vou acionar a turma", None),
        ("2025-08-19", "paulo-henrique", "Essa é a maior disputa aqui", None),
        ("2025-08-19", "daniel-vorcaro", "Edinho avisado, disse que vai atuar",
         "Afirmação de Vorcaro a Paulo Henrique; a assessoria de Edinho Silva (presidente do PT) nega conhecimento do diálogo — ver evento. A existência de contato direto não está confirmada por outra fonte."),
    ]
    added = 0
    for date, sender, content, note in brb:
        if norm(content) in have:
            continue
        t["messages"].append(new_msg(date, sender, content, note, METRO_BRB))
        added += 1
    t.setdefault("timeline_events", []).append(new_event(
        None,
        "Contexto: no dia 19/08/2025, o projeto sobre a compra do Master pelo BRB foi votado na CLDF; segundo a reportagem, Vorcaro buscou evitar que deputados do PT obstruíssem a votação. Em nota, a assessoria de Edinho Silva afirmou que 'esse diálogo é de total desconhecimento do presidente Edinho Silva' e chamou o episódio de 'ilação sem lastro com a realidade'.",
        METRO_BRB))
    print(f"[v9] paulo-henrique BRB: +{added} msgs")

    # ---------- 2) Paulo Henrique: 7 sequências (Metrópoles 16/04) ----------
    have = {norm(m["content"]) for m in t["messages"]}
    ga = [
        # 1º diálogo
        (None, "paulo-henrique", "estou mais empolgado com o que vamos construir",
         "Fragmento: agradecimento pela conversa e alinhamento, mencionando lançar a operação, material pedido pelo governador e desenho de CEO da holding financeira, segundo a reportagem."),
        (None, "paulo-henrique", "Seria legal mostrar o apartamento para ela",
         "Sobre visita a São Paulo com a esposa e a data de 01/03, segundo a reportagem."),
        (None, "daniel-vorcaro", "Fala, amigo! Ótimo, também estou empolgado. Vou alinhar tudo com Daniel.", None),
        (None, "daniel-vorcaro", "Vou te passar uma pessoa que te mostrará o apto", None),
        (None, "paulo-henrique", "Fechado! Obrigado", None),
        # 2º diálogo
        (None, "paulo-henrique", "A esposa ainda está meio cismada. Seria ótimo olhar outro para construir uma referência", None),
        (None, "daniel-vorcaro", "Por quê?", None),
        (None, "paulo-henrique", "Hoje estava com a região toda fechada. Seria bom dar o parâmetro", None),
        (None, "daniel-vorcaro", "Ah, tá. Esse outro é uma cobertura. Já pensando trazer família", None),
        (None, "paulo-henrique", "Eu venho na frente mesmo e elas vêm depois. Boa", None),
        (None, "daniel-vorcaro", "Vale a pena ver", None),
        (None, "paulo-henrique", "Claro. Qual o empreendimento?", None),
        (None, "paulo-henrique", "Meu foco é nisso nessa semana.",
         "Na sequência, pergunta sobre carteira varejo/PJ, segundo a reportagem."),
        (None, "daniel-vorcaro", "Vou levantar aqui com minha turma. E te volto", None),
        # 4º diálogo
        (None, "paulo-henrique", "Fiz as contas para chegar ao valor que combinamos.",
         "A mesma fala cita o Casa Lafer e 'Apagando algumas mensagens', segundo a reportagem."),
        (None, "daniel-vorcaro", "Você diz casa Leopoldo, né? Cobertura que você foi. Pq o heritage melhor que o Lafer, não?", None),
        (None, "paulo-henrique", "Esse era enorme. A Cris nos levou no Casa Lafer, um apartamento tipo. Sim. Bem melhor", None),
        (None, "daniel-vorcaro", "E vamos ter os delas novos de agora", None),
        # 5º diálogo
        (None, "paulo-henrique", "Amigo, pessoal esperando seu de acordo sobre os imóveis de São Paulo. Pode ajudar?", None),
        (None, "daniel-vorcaro", "Do meu lado dei carta branca. Onde está travado. Pode me falar?", None),
        (None, "paulo-henrique", "Na equipe do Daniel. Mas disseram que é simples",
         "'Daniel' é o advogado Daniel Monteiro, conforme a própria reportagem — ver conversa própria."),
        # 6º diálogo
        (None, "paulo-henrique", "Desculpe dar trabalho. É que estou focado na agenda que combinamos...", None),
        (None, "daniel-vorcaro", "Nada. Isso não é trabalho. Eu sou resolvedor de problemas rsrs", None),
        (None, "paulo-henrique", "Estou tratando de carteira de outro lado", None),
        # 7º diálogo
        (None, "paulo-henrique", "Estou com você. Continuo no deal mode. Estou virando noite e tentando resolver", None),
    ]
    added2 = 0
    for date, sender, content, note in ga:
        if norm(content) in have:
            continue
        t["messages"].append(new_msg(date, sender, content, note, METRO_GA))
        added2 += 1
    evs = [
        (None, "3º diálogo da sequência: após decepção de Paulo Henrique por não visitar o apartamento, Vorcaro escreve à corretora (nome preservado pela reportagem e por este site): 'Preciso dele feliz [nome preservado]. Reverte isso aí'."),
        (None, "No 2º diálogo, após a pergunta sobre o empreendimento, Vorcaro menciona 'um gargalo de 300mm na quarta' e o desejo de 'bolar contigo' o que poderiam fazer, segundo a reportagem."),
        (None, "No 7º diálogo, Vorcaro pergunta sobre o 'interesse no deal', fala em 'um negócio de continuidade' e em 'centenas de ajustes ao longo da trajetória', segundo a reportagem."),
        (None, "As mensagens foram reproduzidas pela coluna como citadas na decisão do ministro André Mendonça (STF) que autorizou a prisão de Paulo Henrique, ex-presidente do BRB, na 4ª fase da Operação Compliance Zero (16/04/2026). Teses da investigação ali descritas — a serem comprovadas: seis imóveis avaliados em R$ 146,5 milhões teriam sido ofertados a Paulo Henrique como contrapartiga por atuar como 'mandatário' de Vorcaro no BRB, que comprava carteiras de crédito do Master estimadas em R$ 12,2 bilhões; o pagamento não teria sido concluído porque Vorcaro, ciente da investigação, ordenou ao advogado Daniel Monteiro não registrar as escrituras. A coluna não reproduz manifestação de defesa de Vorcaro, Paulo Henrique ou Monteiro."),
    ]
    for d, c in evs:
        t["timeline_events"].append(new_event(d, c, METRO_GA))
    finalize(t)
    save("paulo-henrique", t)
    print(f"[v9] paulo-henrique imóveis: +{added2} msgs (total {len(t['messages'])})")

    # ---------- 3) Thread nova: Daniel Monteiro ----------
    msgs = [
        new_msg(None, "daniel-monteiro", "O Paulo me procurou para dar andamento em estrutura de compra de imóveis para ele.",
                "Pergunta em seguida, em fala indireta, se deve dar andamento, segundo a reportagem.", METRO_GA),
        new_msg(None, "daniel-vorcaro", "Eu pedi isso anteontem. Pra dar foco nisso. Achei que já estava resolvido", None, METRO_GA),
        new_msg(None, "daniel-monteiro", "Ele só me contou agora cedo. Vou pedir os dados dos imóveis a ele e faço hj mesmo", None, METRO_GA),
        new_msg(None, "daniel-vorcaro", "Eu preciso assinar e pagar hoje. Os imóveis Paulo", None, METRO_GA),
        new_msg(None, "daniel-monteiro", "A documentação está pronta.",
                "Lista como pendências, segundo a reportagem: confirmar imóveis e valores, definir o diretor das sociedades e 'Descer o dinheiro do Astrato para o fundo dono das sociedades'.", METRO_GA),
    ]
    src_note = ("Metrópoles — coluna Grande Angular, 16/04/2026: mensagens entre Vorcaro e o advogado Daniel Monteiro sobre a "
                "estrutura de compra, pagamento e documentação dos imóveis ligados a Paulo Henrique (ex-BRB), citadas na "
                "decisão do Min. André Mendonça que autorizou a prisão de Paulo Henrique na 4ª fase da Compliance Zero. "
                "A coluna não reproduz manifestação de defesa de Monteiro; as teses investigativas estão registradas como "
                "alegações na conversa com Paulo Henrique.")
    thread = {
        "id": "daniel-monteiro-daniel-vorcaro",
        "title": "Daniel Monteiro",
        "participants_ids": ["daniel-vorcaro", "daniel-monteiro"],
        "source": {"document": src_note, "url": METRO_GA[2],
                   "pages": "Mensagens conforme transcrição da reportagem; nada além do que foi divulgado é inferido."},
        "messages": msgs,
        "timeline_events": [
            new_event(None, "Segundo a reportagem, com base na decisão do STF, o pagamento dos imóveis não foi concluído: Vorcaro, ciente da investigação, teria ordenado a Monteiro não registrar as escrituras — tese investigativa, não fato comprovado.", METRO_GA),
        ],
    }
    finalize(thread)
    save("daniel-monteiro", thread)
    print(f"[v9] daniel-monteiro: thread nova ({len(msgs)} msgs)")

    # participante
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    if not any(x["id"] == "daniel-monteiro" for x in people):
        people.append({
            "id": "daniel-monteiro", "name": "Daniel Monteiro", "photo": None,
            "role": "Advogado mencionado nas negociações de imóveis ligados a Paulo Henrique",
            "aliases": [],
            "summary": ("Advogado. Segundo o Metrópoles (16/04/2026), tratou com Vorcaro a estrutura de compra, pagamento e "
                        "documentação dos imóveis ligados a Paulo Henrique, ex-presidente do BRB, em mensagens citadas em "
                        "decisão do STF. A reportagem não reproduz manifestação sua. Perfil resumido exclusivamente a partir "
                        "das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual."),
        })
        pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("[v9] +participante daniel-monteiro")

    # ---------- 4) Felipe Mourão: atribuição e privacidade ----------
    t = load("felipe-mourao")
    msgs = t["messages"]
    by_id = {m["id"]: m for m in msgs}
    removed, moved = [], None

    # m-00033: Henrique Vorcaro -> Marilson (repr PET 15.499 p.9) — fora da conversa
    m33 = by_id.get("m-00033")
    if m33 and m33["content"].startswith("no momento em que estou"):
        msgs.remove(m33)
        removed.append(("m-00033", "fala de Henrique Vorcaro a Marilson Roseno (repr. PET 15.499, p. 9) — não pertence à conversa com Felipe Mourão"))
    # m-00088: Marilson -> Wander (repr PET 15.499 p.104) — fora da conversa
    m88 = by_id.get("m-00088")
    if m88 and m88["content"].startswith("lá tem a sucinta"):
        msgs.remove(m88)
        removed.append(("m-00088", "fala de Marilson Roseno a Wander (repr. PET 15.499, p. 104) — não pertence à conversa com Felipe Mourão"))
    # m-00034: pergunta de Ana Claudia Financeiro a DV (IPJ-A 1020625 p.5) — mover
    m34 = by_id.get("m-00034")
    if m34 and m34["content"].startswith("Vai ser 1mm"):
        m34["sender_id"] = "ana-claudia-financeiro"
        m34["editorial_note"] = ("Contexto do relatório (IPJ-A nº 1020625/2026, p. 5): após Vorcaro encaminhar os dados da "
                                 "empresa de Felipe Mourão para transferência bancária ao contato 'Ana Claudia Financeiro1', "
                                 "Ana Claudia pergunta e Vorcaro responde 'Sim'; ela então envia o comprovante.")
        moved = m34
        msgs.remove(m34)
    # m-00029: supressão do nome da familiar
    m29 = by_id.get("m-00029")
    if m29 and " com a stella minha filha" in m29["content"]:
        m29["content"] = m29["content"].replace("com a stella minha filha", "com a [nome suprimido] minha filha")
        m29["literal_brackets"] = True
        m29["editorial_note"] = (m29["editorial_note"].rstrip() +
                                 " Nome da familiar suprimido editorialmente (política de minimização — familiar que não é "
                                 "objeto da investigação); a supressão está marcada entre colchetes e o trecho não deve ser "
                                 "lido como reprodução integral.")
    finalize(t)
    save("felipe-mourao", t)
    print(f"[v9] felipe-mourao: {len(removed)} removidas, 1 suprimida no nome; total {len(t['messages'])}")

    if moved:
        ac = load("ana-claudia-financeiro")
        if norm(moved["content"]) not in {norm(m["content"]) for m in ac["messages"]}:
            moved["added_in"] = ADDED_IN  # proveniência original (documento/página/figura) preservada
            ac["messages"].append(moved)
        finalize(ac)
        save("ana-claudia-financeiro", ac)
        print(f"[v9] ana-claudia-financeiro: +1 movida (total {len(ac['messages'])})")

    # ---------- 5) Flávio: consolidar áudio 08/09/2025 ----------
    t = load("flavio-bolsonaro")
    m9 = next(m for m in t["messages"] if m["id"] == "m-00009")
    frag_ids = {"m-00014", "m-00015", "m-00016", "m-00017"}
    frags = [m for m in t["messages"] if m["id"] in frag_ids]
    if frags:
        # consolida na transcrição única, na ordem em que a piauí cita os trechos
        m9["content"] = ("Irmão, preferi te mandar o áudio aqui para você ouvir com calma. […] está na mão de Deus aí. "
                         "[…] eu fico sem graça de ficar te cobrando, tá? […] tá todo mundo tenso. […] Imagina a gente "
                         "dando calote num Jim Caviezel, num Cyrus [Nowrasteh]. […] tem muita conta para pagar esse mês. "
                         "[…] na reta final [não podemos perder] ator, diretor, equipe. […] Desculpa o áudio longo aí, tá? "
                         "Um abração, fica com Deus, cara.")
        m9["editorial_note"] = ("Áudio de 08/09/2025 publicado pelo Poder360 e pelo Terra; a PF negou publicamente ter sido a "
                               "origem do vazamento (UOL, 21/07/2026). Registro ÚNICO do áudio: transcrição parcial da piauí "
                               "— os trechos divulgados estão consolidados aqui, na ordem em que a reportagem os cita, com "
                               "elisões marcadas; não são mensagens independentes.")
        t["messages"] = [m for m in t["messages"] if m["id"] not in frag_ids]
        finalize(t)
        save("flavio-bolsonaro", t)
        print(f"[v9] flavio-bolsonaro: áudio consolidado em m-00009, {len(frags)} duplicatas removidas (total {len(t['messages'])})")

    # ---------- índice ----------
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    have_t = {e["id"] for e in index}
    if "daniel-monteiro-daniel-vorcaro" not in have_t:
        index.append({
            "id": "daniel-monteiro-daniel-vorcaro", "title": "Daniel Monteiro",
            "participants_ids": ["daniel-vorcaro", "daniel-monteiro"],
            "message_count": len(thread["messages"]),
            "last_message_preview": thread["messages"][-1]["content"][:80],
            "featured": False,
            "note": src_note[:200],
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
    print(f"[v9] índice: {len(index)} conversas")
    for rid, why in removed:
        print(f"[v9] REMOVIDA {rid}: {why}")


if __name__ == "__main__":
    main()
