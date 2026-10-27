# -*- coding: utf-8 -*-
"""ingest_press9_valadao.py — cria a conversa André Valadão ↔ Daniel Vorcaro.

Fonte única: Agência Pública (24/10/2026), Amanda Audi, Jéssica Ribeiro e
Ed Wanderley — "Vorcaro orquestrou venda de bens da Igreja Lagoinha e
prometeu expansão de R$ 100 milhões".
https://apublica.org/2026/10/daniel-vorcaro-e-os-lacos-com-andre-valadao-da-igreja-lagoinha/

Regras aplicadas (auditoria 26/10/2026):
- somente trechos literalmente publicados; autoria conforme a reportagem;
- datas apenas as divulgadas (09/12/2023, 16/04/2024, 14/07/2024, 23/07/2024,
  15/08/2024 e as deriváveis de forma determinística: "dois dias depois",
  "meses depois" não viram data);
- proposta de doação/negociação ≠ transferência/aquisição comprovada;
- sem dados bancários, familiares, endereços ou anexos privados;
- contraditório preservado (posição pública de Valadão; defesa de Vorcaro).
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "data")

URL = "https://apublica.org/2026/10/daniel-vorcaro-e-os-lacos-com-andre-valadao-da-igreja-lagoinha/"
PUB = {"publication": "Agência Pública", "date": "2026-10-24", "url": URL}
BATCH = "ingest-press9-20261026"
PROCEEDING = ("PF — Operação Compliance Zero; conversas interceptadas obtidas pela "
              "Agência Pública (24/10/2026); a reportagem não publica a peça individualmente")


def verification():
    return {
        "level": "public_investigation",
        "origin": "press report",
        "authority": "Polícia Federal",
        "court": None,
        "case": None,
        "document": None,
        "page": None,
        "figure": None,
        "official_url": None,
        "primary_document_located": False,
        "verified_at": "2026-10-26",
        "proceeding": PROCEEDING,
    }


def sources():
    return {"primary": None, "secondary": [dict(PUB)]}


def msg(mid, sender, content, note, date=None, time=None, precision=None):
    m = {
        "id": mid,
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note,
        "verification": verification(),
        "sources": sources(),
        "source_ref": "Mensagem divulgada por Agência Pública (2026-10-24)",
        "added_in": BATCH,
    }
    if date is not None:
        m["date"] = date
    if time is not None:
        m["time"] = time
    if precision is not None:
        m["timestamp_precision"] = precision
    return m


def event(eid, content, note=None, date=None, precision=None):
    e = {
        "id": eid,
        "content": content,
        "event_kind": "editorial_context",
        "verification": {
            "level": "secondary_source",
            "origin": "press report",
            "authority": None,
            "court": None,
            "case": None,
            "document": None,
            "page": None,
            "figure": None,
            "official_url": None,
            "primary_document_located": False,
            "verified_at": "2026-10-26",
        },
        "sources": sources(),
        "source_ref": "Relato de Agência Pública (2026-10-24)",
        "added_in": BATCH,
    }
    if date is not None:
        e["date"] = date
    if precision is not None:
        e["timestamp_precision"] = precision
    if note is not None:
        e["editorial_note"] = note
    return e


V = "daniel-vorcaro"
A = "andre-valadao"

messages = [
    # — áudio emocionado em resposta a felicitação de aniversário (data não divulgada) —
    msg("m-00001", A,
        "Ô, Daniel, que o senhor te dê sabedoria, te cubra, te guarde, que ele nos guie e guie você nesse momento a voz de Deus, sempre",
        "Trecho de áudio transcrito pela reportagem; a reportagem situa o áudio como resposta a uma felicitação de aniversário, sem divulgar a data."),
    msg("m-00002", A,
        "É no mundo todo, Dani. É no mundo todo que tá acontecendo, é muito forte, irmão",
        "Continuação do mesmo áudio transcrito pela reportagem, conforme a sequência publicada."),
    # — 09/12/2023: primeira menção ao banco interno (convite para show na Virada do Ano em Orlando) —
    msg("m-00003", A,
        "Ano que vem eu quero lançar um banco interno também da Lagoinha, principalmente para os pastores e para a igreja, não pro público diretamente primeiro",
        "Trecho de áudio transcrito pela reportagem. Segundo a reportagem, é a primeira menção, na conversa com Vorcaro, do que viria a ser o Clava Forte Bank, no contexto de convite para patrocinar show da virada do ano na Lagoinha de Orlando.",
        date="2023-12-09", precision="date"),
    # — 16/04/2024: proposta de doação —
    msg("m-00004", V,
        "Deus me incomodou para uma ação junto contigo. Vou colocar 100mm de reais de doação para abrir novas igrejas",
        "Proposta de doação de R$ 100 milhões para abertura de novas igrejas; a reportagem não registra transferência efetivada.",
        date="2024-04-16", precision="date"),
    msg("m-00005", V,
        "Queria que pensasse e orasse e depois me passasse um plano pra implementarmos",
        "Na mesma sequência de 16/04/2024, segundo a reportagem.",
        date="2024-04-16", precision="date"),
    # — diálogos sobre expansão (data não divulgada; reportagem situa a partir de abril de 2024) —
    msg("m-00006", A,
        "Ano que vem vamos dobrar, se Deus quiser",
        "Sobre as possibilidades financeiras do ecossistema da igreja, em diálogo situado pela reportagem a partir de abril de 2024; data não divulgada."),
    msg("m-00007", A,
        "Até 2030 fato só brasil vms passar de 1B ano. em ano de jesus.",
        "Na mesma sequência do diálogo anterior, segundo a reportagem; grafia conforme publicada, inclusive “vms”."),
    # — internacionalização de bens (áudio; data não divulgada) —
    msg("m-00008", A,
        "Uma das coisas que eu estou pensando é de internacionalizar os bens da Lagoinha toda, sabe? Porque o dinheiro nos EUA, o crédito é muito fácil, né, muito menos juros, né. O juros tá alto hoje, mas ainda assim é baixo. Então seria um ministério sem fins lucrativos, non for profit americano, que detém bens no mundo todo, Europa, África, Brasil, Estados Unidos também, Canadá. Tô fazendo essa mudança, sabe",
        "Trecho de áudio transcrito pela reportagem, sobre internacionalização patrimonial da igreja; plano discutido, não operação comprovada. Data não divulgada."),
    msg("m-00009", V,
        "Acho excelente ideia",
        "Resposta ao áudio anterior, segundo a reportagem; data não divulgada."),
    # — venda de imóveis e fundo imobiliário (data não divulgada) —
    msg("m-00010", A,
        "Como você me aconselhou, eu coloquei vários bens nossos à venda",
        "Sobre venda de imóveis da igreja seguindo orientação de Vorcaro, conforme a reportagem; data não divulgada."),
    msg("m-00011", A,
        "Tem um pessoal que me procurou também pra gente, tipo, criar um fundo com a quantidade de bens que a gente tem da Lagoinha, sabe? Mas eu acho que, como a maioria deles a gente nem paga imposto, acho que fazer um fundo, coisa assim, podia acabar sendo pior, né? Não sei o que você me aconselha a respeito",
        "Dúvida sobre possível fundo imobiliário com os bens da igreja; a reportagem não registra fundo constituído. Data não divulgada."),
    msg("m-00012", V,
        "Fundo não é vantagem pra você. Legal é fazer base USA e virar global mesmo",
        "Resposta na mesma sequência, segundo a reportagem; data não divulgada."),
    msg("m-00013", A,
        "Acho que deve ser um valor relevante e certo todo mês, às vezes dá pra acessar possibilidade de compra de imóveis e as igrejas pagarem direto, mas em compra do imóvel semelhante ao invés de aluguel",
        "Sobre alternativa aos aluguéis pagos pelas igrejas, conforme a reportagem; data não divulgada."),
    msg("m-00014", A,
        "O valor que pagamos talvez conseguiríamos de alguma formar um fundo para até construir prédio próprio e alugar para as igrejas. Ou comprar algo semelhante… ?",
        "Na mesma sequência; grafia conforme publicada, inclusive “formar”. A reportagem registra apenas que Vorcaro rebateu que no Brasil não haveria fundo “com apetite pra isso” — fragmento de fala não publicado integralmente e por isso não registrado como mensagem. Data não divulgada."),
    # — 14/07/2024: terreno em Orlando —
    msg("m-00015", V,
        "Dede, vamos pra cima.",
        "Sequência de 14/07/2024 sobre terreno à venda em Orlando (anúncio com oferta de US$ 10,8 milhões encaminhado por Valadão, conforme a reportagem; anúncio não reproduzido). Segundo a reportagem, “Dede” é como Vorcaro chamava Valadão.",
        date="2024-07-14", precision="date"),
    msg("m-00016", V,
        "Aquele valor que te falei tá comprometido",
        "Em 14/07/2024, respondendo à disposição de Valadão de vender um terreno em Belo Horizonte para comprarem o terreno de Orlando em conjunto; segundo a reportagem, refere-se aos R$ 100 milhões prometidos em doação.",
        date="2024-07-14", precision="date"),
    msg("m-00017", V,
        "Você tem que ver como melhor usar. São 20mm usd",
        "Publicado como “São 20mm usd [US$ 20 milhões]”; o colchete com a conversão é inserção do veículo e foi aqui movido para esta nota. Esclarecimento dos cálculos na sequência de 14/07/2024.",
        date="2024-07-14", precision="date"),
    msg("m-00018", A,
        "Faria a sede aqui com esses 20 com certeza. A compra e a construção",
        "Resposta de Valadão na sequência de 14/07/2024, projetando sede no terreno de Orlando com os US$ 20 milhões; proposta, não aquisição comprovada.",
        date="2024-07-14", precision="date"),
    msg("m-00019", V,
        "Então vamos fazer",
        "Retomada de Vorcaro na sequência de 14/07/2024, segundo a reportagem.",
        date="2024-07-14", precision="date"),
    msg("m-00020", A,
        "Se for isso que Deus colocar no seu coração, pra gente montar proposta aqui, você me fala que proposta que eu faço. Dani, você não tá entendendo",
        "Na sequência de 14/07/2024, após reação com emojis “aos prantos” (não reproduzidos) e antes do encaminhamento de mensagens do corretor e de imagens geradas por IA (não reproduzidas), conforme a reportagem.",
        date="2024-07-14", precision="date"),
    # — 16/07/2024: "dois dias depois" —
    msg("m-00021", V,
        "Pode seguir com a aquisição. Eu tô já movimentando. Pra te mandar o recurso",
        "Data derivada de forma determinística: “dois dias depois” de 14/07/2024, conforme a reportagem. Segundo a reportagem, Valadão respondeu com mensagem de gratidão (transcrição não publicada integralmente). Promessa de envio de recurso não equivale a transferência comprovada.",
        date="2024-07-16", precision="date"),
    # — 23/07/2024: ecossistema Lagoinha / CLAVA —
    msg("m-00022", A,
        "só no ecossistema da Lagoinha hoje tem : igrejas, pastores, funcionários, livrarias, seminário (só hoje, 12 mil alunos ativos), fundação oasis filantrópica que recebe recursos federais… tipo tudo que envolve o mundo da Lagoinha pra dentro do CLAVA.",
        "Dias antes da inauguração do Clava Forte (31/07/2024), Valadão anunciara em 23/07/2024 ao amigo um “sistema pay próprio Lagoinha Global” junto à empresa de pagamentos Dock; a mensagem acima segue esse anúncio, conforme a reportagem. Grafia e espaçamento conforme publicados.",
        date="2024-07-23", precision="date"),
    # — pacotes de serviços e FIDC ("meses depois"; data não divulgada) —
    msg("m-00023", V,
        "Depois me explica o que precisa",
        "Resposta a pedido de ajuda de Valadão sobre pacotes de serviços para o sistema da igreja e FIDC, meses após julho de 2024, conforme a reportagem; data não divulgada."),
    # — 31/07/2024 e seguintes: cobrança de telefonema —
    msg("m-00024", A,
        "Tô sempre à disposição com telefone na mão.",
        "Na sequência iniciada em 31/07/2024, quando Valadão relatou prazo de depósito de US$ 200 mil em cinco dias caso assinasse o contrato (relato em fala indireta na reportagem, sem transcrição literal publicada); data exata não divulgada."),
    # — entre 31/07/2024 e 15/08/2024: processo arquivado —
    msg("m-00025", V,
        "Que showwwwwww. Parabéns!!!",
        "Única resposta de Vorcaro no período, segundo a reportagem, dada quando Valadão anunciou o arquivamento de um processo em que respondia por homofobia; data não divulgada."),
    # — 15/08/2024 —
    msg("m-00026", A,
        "Dani sobre o terreno estamos finalizando e precisamos de 200k de dólares pra amarrar a proposta … e prosseguir com due diligence de até 80 dias para ter toda liberação da prefeitura para o projeto ou não",
        "Cobrança de resposta sobre o terreno em 15/08/2024, conforme a reportagem; as reticências constam do texto publicado. A reportagem não confirma a conclusão da aquisição.",
        date="2024-08-15", precision="date"),
    # — 17/09 (Clava Forte; ano 2024 conforme a sequência "meses depois" de julho de 2024) —
    msg("m-00027", A,
        "a fintech, que por sinal tá indo super bem e sem dúvida é algo que pode ficar grande demais",
        "Trecho transcrito dentro do pedido de conversa situado pela reportagem em 17 de setembro (meses após julho de 2024, na seção sobre o Clava Forte Bank), seguido de duas ligações de cerca de 15 minutos, conforme a reportagem.",
        date="2024-09-17", precision="date"),
    # — imóvel da Jorlan / igreja de Zettel (data não divulgada) —
    msg("m-00028", A,
        "Segunda feira vou em BH com Zettel ver o imóvel da Jorlan, em frente o BH shopping para ser a igreja dele. Será lindo. 4 mil lugares",
        "Sobre visita ao imóvel da Jorlan, em frente ao BH Shopping, para uma igreja a ser liderada por Fabiano Zettel, conforme a reportagem; ver conversa própria de Zettel e evento de contexto. Data não divulgada."),
]

events = [
    event("e-00001",
          "A Agência Pública (24/10/2026) descreve décadas de amizade entre André Valadão e Daniel Vorcaro registradas em conversas interceptadas pela PF na Operação Compliance Zero: trocas afetuosas (a reportagem conta ao menos 44 “eu te amo”), orientações financeiras e patrimoniais sobre bens da Igreja Batista da Lagoinha e a proposta de doação de R$ 100 milhões de 16/04/2024. Nos eventos de virada de ano da Lagoinha, o patrocínio solicitado de Vorcaro foi de US$ 350 mil (2023) e US$ 450 mil (2024), condicionados, segundo a reportagem, a “se Deus tocasse no coração”; a reportagem não registra se os depósitos ocorreram. Procurado, Valadão reconheceu a amizade de décadas, mas frisou que o relacionamento se restringia à igreja e não envolvia negócios; a defesa de Vorcaro disse que não iria comentar o assunto. Propostas e planos registrados na conversa não comprovam, por si, transferências ou operações realizadas.",
          date=None),
    event("e-00002",
          "O Clava Forte Bank, primeira fintech de uma igreja evangélica no Brasil, foi mencionado na conversa em 09/12/2023 e inaugurado em 31/07/2024, com a empresa de pagamentos Dock, definido por Valadão como “um banco para impulsionar os projetos do Reino de Deus”; Valadão investiu no projeto, segundo a reportagem, contrariando recomendação de Vorcaro. Em abril de 2024, Valadão pediu orientação jurídica sobre unificar o sistema financeiro das igrejas do grupo, que estimava movimentar internamente R$ 300 a 350 milhões. Em setembro de 2025, Valadão chamou a fintech de “melhor banco digital do Brasil”. Após a primeira prisão de Vorcaro (18/11/2025, em Guarulhos, rumo a Dubai), o aplicativo saiu do ar em 21/11/2025; Valadão atribuiu a saída a manutenção temporária contra ataques de hackers. Em vídeo de 14/09/2026, o deputado Rogério Correia (PT-MG) afirmou na CPMI do INSS que o ecossistema de Valadão recebeu recursos de aposentados, pedindo apuração (“Nós precisamos investigar isso”) — alegação parlamentar em investigação, não conclusão; o Congresso aponta proximidade entre Valadão e Felipe Machado Gomes, presidente de associação investigada no esquema do INSS e patrono do réveillon da Lagoinha de 2024. A Folha de S.Paulo relatou que Vorcaro patrocinou a festa de 2023 e foi à de 2024, quando a operação BRB-Master já era alvo de inquérito.",
          date=None),
    event("e-00003",
          "Negociação do terreno em Orlando (2024): a partir de 14/07/2024, Valadão encaminhou anúncio com oferta de US$ 10,8 milhões e imagens geradas por IA (não reproduzidas); em 31/07 relatou prazo de depósito de US$ 200 mil em cinco dias caso assinasse contrato (fala indireta na reportagem) e em 15/08 escreveu precisar de “200k de dólares pra amarrar a proposta”, com due diligence de até 80 dias. Segundo a reportagem, os dois trocaram dados de contas e instruções, como um modelo de “proof of funds” que Vorcaro se comprometeu a preencher com dados de suas empresas — dado bancário e comprovantes não reproduzidos. Quase um ano depois, o anúncio do terreno seguia no ar “sem dono”, e a reportagem não confirma a conclusão da aquisição; os valores indicados somavam cerca de US$ 12 milhões. Nenhuma aquisição comprovada consta do registro.",
          date=None),
    event("e-00004",
          "Contexto do imóvel da Jorlan (em frente ao BH Shopping, Belo Horizonte): Valadão anunciou na conversa uma visita com Fabiano Zettel para avaliar o imóvel como igreja de 4 mil lugares liderada por Zettel. Segundo a reportagem, a unidade tornou-se a Lagoinha Belvedere, e relatório do Coaf (RIF 140.515, obtido pela Agência Pública) apontou movimentações atípicas — receita presumida de cerca de R$ 950 mil/ano contra R$ 57,1 milhões recebidos entre dezembro de 2024 e dezembro de 2025 —, período em que Zettel é apontado pela PF como operador de caixa de Vorcaro (Operação Compliance Zero); a unidade foi fechada após a prisão de Zettel, em março de 2026. A reportagem registra que as mensagens analisadas não mostram Vorcaro pedindo a Zettel repasses específicos a Valadão. Detalhamento individualizado de origens dos recursos, envolvendo pessoas físicas, não é reproduzido neste arquivo por não haver necessidade documental demonstrada.",
          date=None),
]

thread = {
    "id": "andre-valadao-daniel-vorcaro",
    "title": "André Valadão",
    "participants_ids": ["daniel-vorcaro", "andre-valadao"],
    "source": {
        "document": ("Agência Pública (24/10/2026) — Amanda Audi, Jéssica Ribeiro e Ed Wanderley: "
                     "“Vorcaro orquestrou venda de bens da Igreja Lagoinha e prometeu expansão de R$ 100 milhões”"),
        "url": URL,
        "pages": ("Mensagens do celular de Vorcaro interceptadas pela PF (Operação Compliance Zero) conforme "
                  "transcrição da reportagem (áudios transcritos em trechos); datas e horários apenas os "
                  "divulgados; nada além do publicado é inferido."),
    },
    "messages": messages,
    "timeline_events": events,
}

path = os.path.join(DATA, "threads", "andre-valadao-daniel-vorcaro.json")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(thread, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(f"[ok] thread criada: {path} ({len(messages)} mensagens, {len(events)} eventos)")

# ---- participants.json: adicionar andre-valadao ----
ppath = os.path.join(DATA, "participants.json")
participants = json.load(open(ppath, encoding="utf-8"))
if not any(p["id"] == "andre-valadao" for p in participants):
    novo = {
        "id": "andre-valadao",
        "name": "André Valadão",
        "role": "Pastor e líder da Igreja Batista da Lagoinha (Belo Horizonte)",
        "aliases": ["Dede"],
        "summary": ("Pastor e líder da Igreja Batista da Lagoinha. Amigo de décadas de Vorcaro, segundo a Agência "
                    "Pública (24/10/2026): em conversas interceptadas pela PF, recebeu orientações sobre venda de "
                    "bens da igreja, internacionalização patrimonial e o terreno em Orlando, e a ele foi proposta "
                    "uma doação de R$ 100 milhões para abrir novas igrejas — proposta sem transferência comprovada "
                    "na reportagem. Coordenou a criação do Clava Forte Bank (2024). Procurado, disse que o "
                    "relacionamento se restringia à igreja e não envolvia negócios. Perfil resumido exclusivamente "
                    "a partir das fontes linkadas; não constitui acusação nem conclusão sobre responsabilidade individual."),
        "profile_sources": [
            {"label": "Agência Pública — reportagem de 24/10/2026", "url": URL},
        ],
    }
    participants.append(novo)
    participants.sort(key=lambda p: p["id"])
    with open(ppath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(participants, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[ok] participante andre-valadao adicionado (total {len(participants)})")
else:
    print("[skip] participante andre-valadao já existe")

# ---- threads.json: entrada do índice ----
ipath = os.path.join(DATA, "threads.json")
index = json.load(open(ipath, encoding="utf-8"))
if not any(e["id"] == "andre-valadao-daniel-vorcaro" for e in index):
    entry = {
        "id": "andre-valadao-daniel-vorcaro",
        "title": "André Valadão",
        "participants_ids": ["daniel-vorcaro", "andre-valadao"],
        "message_count": len(messages),
        "last_message_preview": "a fintech, que por sinal tá indo super bem e sem dúvida é algo que pode ficar grande demais",
        "featured": False,
        "note": ("Agência Pública (24/10/2026) — Amanda Audi, Jéssica Ribeiro e Ed Wanderley: “Vorcaro orquestrou "
                 "venda de bens da Igreja Lagoinha e prometeu expansão de R$ 100 milhões”"),
    }
    index.append(entry)
    index.sort(key=lambda e: e["id"])
    with open(ipath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[ok] índice atualizado (total {len(index)} conversas)")
else:
    print("[skip] índice já contém a conversa")
