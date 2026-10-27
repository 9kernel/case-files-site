# ingest_publica_20261026.py — rodada incremental de 26/10/2026 (fonte: Agência Pública 18/10)
#
# Pendências implementadas (auditoria incremental 26/10/2026):
#   1. André Valadão × Vorcaro: sequência de abril/2024 (reação à postagem de Nikolas
#      Ferreira de 27/04/2024) — 5 mensagens literais (Agência Pública, 18/10/2026).
#      Datas/horas somente as divulgadas: carimbos visíveis na captura publicada
#      (2024-04-29 13:42:17 e 13:42:59 -03:00); demais em precisão de mês, com nota
#      de derivação. "[Gaspar]" e "[Nikolas]" são esclarecimentos do veículo — não
#      constam do original e ficam documentados em nota (convenção AGENTS.md §1).
#   2. Valadão m-00027: ano 17/09 confirmado pela captura publicada (a matéria de
#      24/10 não explicita o ano no texto); remetente reatribuído a Vorcaro (a
#      transcrição completa da captura — "aquele fundo que você mencionou" — e a
#      bolha enviada por DV identificam o autor; antes registrada como Valadão,
#      apenas pelo fragmento citado no texto corrido); transcrição ampliada e hora
#      09:13 acrescentada. m-00023 (réplica imediata na captura, 09:12:33) ganha
#      data/hora e posição; m-00026 ganha hora 12:36 (carimbo da captura).
#   3. Colchetes editoriais de lotes antigos (pendência da auditoria de 26/10):
#      13 registros corrigidos após conferência fonte a fonte (UOL 15/10 e 13/10,
#      Pública 15/10, Folha 05/03 e 30/09) — inserções/marcações do veículo
#      separadas do campo literal, com nota "[Corrigido 2026-10-26: ...]".
#      Mantidos: cortes ([…]/[...]), supressões de privacidade e o registro
#      felipe-mourao m-00057, cujos colchetes constam da transcrição do documento
#      oficial da PF (IPJ-A 1020625/2026, fl. 45, fig. 53 — conferido no PDF local).
#
# NÃO implementado (evidência insuficiente): áudio de Nikolas de março/2025 — a
# própria reportagem diz que a mensagem de voz foi encaminhada "a Valadão" (não a
# Vorcaro), e o conteúdo do áudio trata Valadão em terceira pessoa; destinatário
# não individualmente demonstrável — registrado como pendência, sem inserção.

import json

BATCH = "ingest-publica-20261026"
SEC = [{"publication": "Agência Pública", "date": "2026-10-18",
        "url": "https://apublica.org/2026/10/banco-master-a-amigo-vorcaro-se-disse-apoiador-da-direita/"}]
PROC = ("PF — mensagens interceptadas pela Polícia Federal às quais a Agência Pública "
        "teve acesso (reportagem de 18/10/2026); a reportagem não nomeia a operação "
        "e não publica a peça individualmente")


def verif():
    return {"level": "public_investigation", "origin": "press report", "authority": "Polícia Federal",
            "court": None, "case": None, "document": None, "page": None, "figure": None,
            "official_url": None, "primary_document_located": False, "verified_at": "2026-10-26",
            "proceeding": PROC}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def msg(mid, sender, content, note, date, precision, time=None):
    m = {"id": mid, "date": date, "time": time, "timestamp_precision": precision,
         "sender_id": sender, "content_kind": "verbatim", "content": content,
         "editorial_note": note, "verification": verif(),
         "sources": {"primary": None, "secondary": [dict(s) for s in SEC]},
         "source_ref": "Mensagem divulgada por Agência Pública (2026-10-18)",
         "added_in": BATCH}
    return m


def fix_bracket(t, mid, new_content, new_note, keep_lb=False):
    m = next(x for x in t["messages"] if x["id"] == mid)
    old = m["content"]
    m["content"] = new_content
    if not keep_lb:
        m.pop("literal_brackets", None)
    m["editorial_note"] = new_note
    return f"  {mid}: “{old}” -> “{new_content}”"


# ---------------------------------------------------------------- Valadão
path = "data/threads/andre-valadao-daniel-vorcaro.json"
t = load(path)

new_msgs = [
    msg("m-00029", "daniel-vorcaro",
        "Nikolas repostou a Malu. Loucura isso. Aliás, narrativa ruim pra ele mesmo",
        "Reação de Vorcaro à postagem de Nikolas Ferreira de 27/04/2024 (repost de reportagem de Malu Gaspar "
        "sobre o evento jurídico em Londres); a reportagem não indica o dia desta mensagem — precisão de mês. "
        "Publicado com “[Gaspar]” como esclarecimento do veículo (sobrenome da jornalista), não constando do "
        "original e removido do campo literal. Procurado, Vorcaro não havia se manifestado até a publicação "
        "(a assessoria anunciou nota para 19/10).",
        "2024-04", "month"),
    msg("m-00030", "daniel-vorcaro",
        "Quem me mandou foi um blog de esquerda, que sabe que apoiamos a direita. Olha a bola de neve que pode virar",
        "Na mesma sequência da postagem de 27/04/2024; data e hora conforme o carimbo visível na captura "
        "publicada pela reportagem (2024-04-29 13:42:17 -03:00).",
        "2024-04-29", "minute", "13:42"),
    msg("m-00031", "andre-valadao",
        "Sim",
        "Mensagem não citada no texto corrido da reportagem; transcrita da captura publicada (carimbo "
        "2024-04-29 13:42:59 -03:00), na sequência imediata da mensagem anterior.",
        "2024-04-29", "minute", "13:42"),
    msg("m-00032", "daniel-vorcaro",
        "Eu apoio diversos eventos, e nesse caso o apoio foi com a palestra do Tony Blair com quem tive um debate "
        "de altíssimo nível. No evento, várias pessoas de direita, apoiadores do evento inclusive vários que "
        "apoiaram ele, como nós. Acaba ficando ruim ele incentivar e propagar um ataque a mim, como fez agora. "
        "Só preciso saber se estamos do mesmo lado ou agora estamos um contra o outro",
        "Contexto: apoio do Master à palestra de Tony Blair (evento jurídico em Londres citado na postagem de "
        "Nikolas). Publicado com “[Nikolas]” como esclarecimento do veículo, não constando do original e "
        "removido do campo literal. Declaração de apoio político é fala atribuída a Vorcaro — não comprova "
        "financiamento, contrato ou favorecimento.",
        "2024-04", "month"),
    msg("m-00033", "andre-valadao",
        "Resumindo, ele nem sabia sobre o banco e você, \"palavras dele né\", e daí pediu perdão demais e vai "
        "contornar tudo. Deve te chamar também, ele me disse. Disse da gratidão com você e por aí vai.",
        "Horas depois, conforme a reportagem; o dia não foi divulgado — precisão de mês. Publicado com "
        "“[Nikolas]” como esclarecimento do veículo, removido do campo literal. Relato de Valadão sobre a "
        "conversa dele com Nikolas: fala indireta de terceiro — não gera mensagem própria de Nikolas nem é "
        "atribuível a Vorcaro.",
        "2024-04", "month"),
]

idx = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00015")
for j, m in enumerate(new_msgs):
    t["messages"].insert(idx + j, m)

by_id = {m["id"]: m for m in t["messages"]}

# m-00027 — ano confirmado na captura; remetente corrigido; transcrição ampliada; hora
m27 = by_id["m-00027"]
m27["sender_id"] = "daniel-vorcaro"
m27["content_kind"] = "verbatim"
m27["content"] = ("Preciso falar contigo sobre alguns assuntos, inclusive aquele fundo que você mencionou "
                  "e depois falamos sobre o sistema de pagamentos e que sobre a fintech, que por sinal tá indo "
                  "super bem e sem dúvida é algo que pode ficar grande demais")
m27["time"] = "09:13"
m27["timestamp_precision"] = "minute"
m27["editorial_note"] = (
    "[Corrigido 2026-10-26: remetente reatribuído a Vorcaro e transcrição ampliada.] A reportagem situa o "
    "pedido como de Vorcaro (“ele pede para falar com o amigo”; o remetente menciona “aquele fundo que você "
    "mencionou”, pedido antes feito por Valadão) e a captura publicada mostra a mensagem como bolha enviada "
    "por DV com carimbo 2024-09-17 09:13:16 -03:00 — antes atribuída a Valadão e registrada apenas pelo "
    "fragmento citado no texto corrido. Ano 17/09/2024 confirmado pela captura (a passagem do texto não "
    "explicita o ano); hora acrescentada a partir do carimbo. Seguida de duas ligações de cerca de 15 "
    "minutos, conforme a reportagem.")

# m-00023 — data/hora da captura e posição (imediatamente antes do pedido de 09:13:16)
m23 = by_id["m-00023"]
m23["date"] = "2024-09-17"
m23["time"] = "09:12"
m23["timestamp_precision"] = "minute"
m23["editorial_note"] = (m23.get("editorial_note") or "").rstrip() + (
    " [Data e hora acrescentadas 2026-10-26 a partir do carimbo da captura publicada "
    "(2024-09-17 09:12:33 -03:00), que mostra esta mensagem imediatamente antes do pedido de 09:13:16; "
    "posição ajustada conforme a captura. Autoria mantida conforme o texto da reportagem "
    "(“responde o ex-banqueiro”).]")
t["messages"].remove(m23)
t["messages"].insert(next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00027"), m23)

# m-00026 — hora do carimbo da captura (2024-08-15 12:36:36 -03:00)
m26 = by_id["m-00026"]
m26["time"] = "12:36"
m26["timestamp_precision"] = "minute"
m26["editorial_note"] = (m26.get("editorial_note") or "").rstrip() + (
    " [Hora acrescentada 2026-10-26 a partir do carimbo da captura publicada (2024-08-15 12:36:36 -03:00).]")

save(path, t)
print("[valadao] +5 mensagens (m-00029..m-00033); m-00023 data/hora/posição; m-00026 hora; m-00027 remetente/transcrição/hora")

# ------------------------------------------------------- colchetes editoriais
fixes = []

t = load("data/threads/ana-matos-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00002", "Coisa mais importante nossa vida é esse Metrópoles",
    "Resposta na mesma sequência. Atribuição conferida pelo editor nas capturas da reportagem: a troca é com "
    "a diretora de marketing Ana Matos (o texto corrido do UOL a chama apenas de 'a diretora'; é ela quem "
    "processa o pagamento — daí o 'tá caro' e o 'dei ok pra Lilian'). [Corrigido 2026-10-26: colchete "
    "editorial separado do conteúdo literal.] Publicado pelo UOL como “Coisa mais importante [da] nossa vida "
    "é esse Metrópoles”; o “[da]” é ajuste editorial do veículo, não constando do original, e foi removido "
    "do campo literal."))
save("data/threads/ana-matos-daniel-vorcaro.json", t)

t = load("data/threads/diogo-batista-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00018", "Mando? Nossas refugiadas?",
    "[Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado pelo UOL como "
    "“Mando [as duas]? Nossas refugiadas?”; o “[as duas]” é inserção esclarecedora do veículo, não constando "
    "do original, e foi removido do campo literal. Sobre as 'figurantes' mandadas para um jantar de Vorcaro "
    "com convidados no Pappa Bar, nos Jardins."))
save("data/threads/diogo-batista-daniel-vorcaro.json", t)

t = load("data/threads/frederic-kachar-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00024",
    "Para não te deixar na mão, te bonifico um branded content [...] da marca na Glamour e na Vogue",
    "[Corrigido 2026-10-26: colchetes editoriais separados do conteúdo literal.] Publicado pela Agência "
    "Pública como “...te bonifico um branded content [conteúdo patrocinado, ou, em bom português, matéria "
    "paga] da marca na Glamour e na Vogue [Brasil], mas desatrelados do Baile [da Vogue]”; os colchetes são "
    "inserções do veículo: “[Brasil]” foi removido do campo literal e os demais esclarecimentos não são "
    "reproduzidos — o “[...]” marca o corte (o trecho final publicado permaneceu fora do registro).",
    keep_lb=True))
fixes.append(fix_bracket(
    t, "m-00026", "Estou no voo com Lauro, que vai conhecer sua sede nova antes de mim.",
    "[Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado pela Agência Pública "
    "como “Estou no voo com Lauro [Jardim], que vai conhecer sua sede nova antes de mim. Desnecessário dizer "
    "que estou com ciúmes.”; o “[Jardim]” é inserção do veículo (sobrenome), não constando do original, e foi "
    "removido do campo literal; a frase final publicada permaneceu fora do registro (trecho)."))
fixes.append(fix_bracket(
    t, "m-00031", "O Álvaro incluiu aspas suas nessa análise. Vamos falar amanhã?",
    "Duas horas depois. [Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado "
    "pela Agência Pública como “O Álvaro [Campos] incluiu aspas suas nessa análise. Vamos falar amanhã?”; o "
    "“[Campos]” é inserção do veículo (sobrenome), não constando do original, e foi removido do campo literal."))
fixes.append(fix_bracket(
    t, "m-00032", "Não vale a pena pra mim falar. Vira (sic) o caso Malu. Tudo que eu falo usam contra mim.",
    "'(sic)' consta da transcrição. [Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] "
    "Publicado pela Agência Pública como “Vira (sic) o caso Malu [Gaspar]”; o “[Gaspar]” é inserção do veículo "
    "(sobrenome), não constando do original, e foi removido do campo literal. Referência ao episódio "
    "registrado em evento na conversa com Thiago Miranda."))
save("data/threads/frederic-kachar-daniel-vorcaro.json", t)

t = load("data/threads/tiago-polo-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00001", "O Diogo disse a ideia da agência seria uma forma de ajustar as meninas indiretamente",
    "Explicando a Vorcaro para que serviria a agência. [Corrigido 2026-10-26: colchete editorial separado do "
    "conteúdo literal.] Publicado pelo UOL como “O Diogo disse [que] a ideia da agência seria uma forma de "
    "ajustar as meninas indiretamente”; o “[que]” é inserção do veículo, não constando do original, e foi "
    "removido do campo literal."))
save("data/threads/tiago-polo-daniel-vorcaro.json", t)

t = load("data/threads/walfrido-mares-guia-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00009", "O indicado para presidir a Anvisa é nosso aliado no Min da Saude.Conhece tudo sobre a Biomm",
    "As indicações para a agência foram anunciadas em agosto/2025 (evento abaixo). [Corrigido 2026-10-26: "
    "colchetes editoriais separados do conteúdo literal.] Na publicação da Folha, “Anvisa” aparece entre "
    "colchetes como marcação editorial do veículo (link para o tópico); a palavra consta da mensagem "
    "original — mantida a palavra, removidos os colchetes."))
save("data/threads/walfrido-mares-guia-daniel-vorcaro.json", t)

t = load("data/threads/martha-graeff-daniel-vorcaro.json")
fixes.append(fix_bracket(
    t, "m-00014", "Tô num jantar na residência oficial com Hugo e seis empresários",
    "Jantar na residência oficial da Câmara, com o então presidente Hugo Motta. [Corrigido 2026-10-26: "
    "colchete editorial separado do conteúdo literal.] Publicado pela Folha como “com Hugo [Motta, eleito "
    "presidente da Câmara no início daquele mês] e seis empresários”; o colchete é inserção explicativa do "
    "veículo e foi removido do campo literal."))
fixes.append(fix_bracket(
    t, "m-00017", "Indo encontrar Alexandre Moraes aqui perto de casa",
    "Citação literal conforme transcrita pela reportagem indicada nas fontes. [Corrigido 2026-10-26: colchete "
    "editorial separado do conteúdo literal.] Publicado pela Folha como “Alexandre [de] Moraes”; o “[de]” é "
    "inserção do veículo, não constando do original, e foi removido do campo literal."))
fixes.append(fix_bracket(
    t, "m-00020", "quem era o primeiro cara",
    "Citação literal conforme transcrita pela reportagem indicada nas fontes. [Corrigido 2026-10-26: marcação "
    "editorial “[?]” do veículo (indício de dúvida de transcrição) separada do conteúdo literal e removida do "
    "campo literal.]"))
fixes.append(fix_bracket(
    t, "m-00021", "Alexandre Moraes",
    "Citação literal conforme transcrita pela reportagem indicada nas fontes. [Corrigido 2026-10-26: colchete "
    "editorial separado do conteúdo literal.] Publicado pela Folha como “Alexandre [de] Moraes”; o “[de]” é "
    "inserção do veículo, não constando do original, e foi removido do campo literal."))
fixes.append(fix_bracket(
    t, "m-00023", "Sin. Falou que é bem melhor. E ele adorava apto",
    "[Corrigido 2026-10-26: marcações editoriais separadas do conteúdo literal.] Publicado pela Folha como "
    "“Sin [sic]. Falou que é [sic] bem melhor. E ele adorava apto [apartamento]”; os “[sic]” são marcações do "
    "veículo e o “[apartamento]” é expansão editorial do veículo para “apto” — nenhum deles consta do "
    "original; todos removidos do campo literal."))
save("data/threads/martha-graeff-daniel-vorcaro.json", t)

print("[colchetes] 13 correções:")
for f in fixes:
    print(f)

# ---------------------------------------------------------------- índice
idx_path = "data/threads.json"
idx = load(idx_path)
e = next(x for x in idx if x["id"] == "andre-valadao-daniel-vorcaro")
e["message_count"] = 33
last = t_valadao = load("data/threads/andre-valadao-daniel-vorcaro.json")["messages"][-1]
e["last_message_preview"] = (last.get("content") or "").replace("\n", " ")[:80]
save(idx_path, idx)
print(f"[threads.json] andre-valadao: message_count=33, preview atualizada")
