# -*- coding: utf-8 -*-
"""
ingest_press10_20261027.py — rodada de 27/10/2026 (auditoria incremental).

Implementa:
  (1) Colchetes editoriais removidos do literal e documentados em nota
      (ana-matos, tiago-polo, diogo-batista, frederic-kachar, martha-graeff,
      walfrido-mares-guia) — inserções de veículo confirmadas na fonte.
  (2) André Valadão: 4 mensagens de 27/04/2024 (Agência Pública, 18/10/2026).
  (3) Nikolas Ferreira: m-00001 corrigido para a transcrição integral publicada
      pelo g1 (despedida suprimida por divergência de transcrição documentada);
      nova m-00003 ("Deixa comigo", UOL 03/09/2026); nota de m-00002 reescrita.
  (4) Grupo "Master" (Vorcaro·Belline·Paulo Sérgio): novo thread + participante
      belline-santana (BBC/CNN, 11/09/2026).
  (5) Paulo Sérgio: 2 mensagens literais de 25/04/2025 + evento editorial
      (BBC, 11/09/2026); ressalva de identidade preservada.
  (6) threads.json: contagens, previews e entrada nova.

Regras: AGENTS.md — fonte primeiro; nada inventado; colchetes editoriais fora
do literal; edições preservam added_in original e ganham [Corrigido 2026-10-27].
"""

import json
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
BATCH = "ingest-press10-20261027"
TODAY = "2026-10-27"

URL_PUB18 = "https://apublica.org/2026/10/banco-master-a-amigo-vorcaro-se-disse-apoiador-da-direita/"
URL_PUB24 = "https://apublica.org/2026/10/daniel-vorcaro-e-os-lacos-com-andre-valadao-da-igreja-lagoinha/"
URL_G1 = "https://g1.globo.com/politica/noticia/2026/09/04/nikolas-e-vorcaro-ouca-audio-leia-transcricao-e-veja-o-que-ex-deputado-falou-sobre-as-mensagens.ghtml"
URL_FOLHA_NIK = "https://www1.folha.uol.com.br/poder/2026/09/nikolas-pediu-ajuda-a-vorcaro-para-liberar-minerio-e-banqueiro-afirmou-bancar-voos-dele-diz-site.shtml"
URL_UOL_NIK = "https://noticias.uol.com.br/politica/ultimas-noticias/2026/09/03/nikolas-ferreira-audio-daniel-vorcaro.ghtm"
URL_BBC = "https://www.em.com.br/politica/2026/09/amp/7498392-vorcaro-tinha-grupo-de-whatsapp-para-pedir-orientacao-a-chefes-de-supervisao-do-banco-central-diz-pf.html"
URL_CNN = "https://www.cnnbrasil.com.br/politica/pf-vorcaro-participava-de-grupo-no-whatsapp-com-servidores-do-bc/"


def load(rel):
    with io.open(os.path.join(DATA, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def save(rel, obj):
    path = os.path.join(DATA, rel)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def ver_pub_investigation(proceeding):
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
        "verified_at": TODAY,
        "proceeding": proceeding,
    }


def ver_secondary(origin="PF extraction"):
    return {
        "level": "secondary_source",
        "origin": origin,
        "authority": None,
        "court": None,
        "case": None,
        "document": None,
        "page": None,
        "figure": None,
        "official_url": None,
        "primary_document_located": False,
        "verified_at": TODAY,
    }


PROC_BBC = (
    "PF — representação ao STF assinada em 27/02/2026, tornado pública em "
    "setembro/2026 após levantamento de sigilo (decisão do Min. André Mendonça "
    "a pedido do presidente da corte, Min. Edson Fachin, conforme CNN Brasil); "
    "reportagens BBC News Brasil (Luiz Fernando Toledo, 11/09/2026) e CNN "
    "Brasil (11/09/2026); peça individual não localizada nesta rodada (pacote "
    "público «Arquivos Pet 16704» do STF inacessível a partir do ambiente de "
    "verificação de 27/10/2026)"
)

PROC_PUB18 = (
    "PF — conversas interceptadas às quais a Agência Pública teve acesso "
    "(18/10/2026); a reportagem não publica a peça individualmente"
)

changes = []

# ============================================================
# (1) COLCHETES EDITORIAIS — inserções de veículo confirmadas
# ============================================================

BRACKET_FIXES = [
    # (arquivo, msg_id, conteúdo novo, texto do esclarecimento p/ nota)
    (
        "ana-matos-daniel-vorcaro.json",
        "m-00002",
        "Coisa mais importante nossa vida é esse Metrópoles",
        "“[da]” é complementação gramatical inserida pelo veículo na transcrição publicada "
        "(UOL, 15/10/2026); removida do literal",
    ),
    (
        "tiago-polo-daniel-vorcaro.json",
        "m-00001",
        "O Diogo disse a ideia da agência seria uma forma de ajustar as meninas indiretamente",
        "“[que]” é complementação gramatical inserida pelo veículo na transcrição publicada "
        "(UOL — coluna Natália Portinari, 13/10/2026); removida do literal",
    ),
    (
        "diogo-batista-daniel-vorcaro.json",
        "m-00018",
        "Mando? Nossas refugiadas?",
        "“[as duas]” é complementação inserida pelo veículo na transcrição publicada "
        "(UOL — coluna Natália Portinari, 13/10/2026); removida do literal",
    ),
    (
        "frederic-kachar-daniel-vorcaro.json",
        "m-00024",
        "Para não te deixar na mão, te bonifico um branded content […] da marca na Glamour e na Vogue",
        "a fonte publica “branded content [conteúdo patrocinado…] da marca na Glamour e na Vogue "
        "[Brasil], mas desatrelados do Baile [da Vogue]” — os colchetes são inserções editoriais "
        "do veículo (glosa e identificações), removidas do literal; o […] marca corte do projeto "
        "no ponto da glosa; a frase publicada prossegue além do trecho registrado",
    ),
    (
        "frederic-kachar-daniel-vorcaro.json",
        "m-00026",
        "Estou no voo com Lauro, que vai conhecer sua sede nova antes de mim.",
        "“[Jardim]” é identificação de sobrenome (Lauro Jardim) inserida pelo veículo na "
        "transcrição publicada (Agência Pública, 15/10/2026); removida do literal",
    ),
    (
        "frederic-kachar-daniel-vorcaro.json",
        "m-00031",
        "O Álvaro incluiu aspas suas nessa análise. Vamos falar amanhã?",
        "“[Campos]” é identificação de sobrenome (Álvaro Campos) inserida pelo veículo na "
        "transcrição publicada (Agência Pública, 15/10/2026); removida do literal",
    ),
    (
        "frederic-kachar-daniel-vorcaro.json",
        "m-00032",
        "Não vale a pena pra mim falar. Vira (sic) o caso Malu. Tudo que eu falo usam contra mim.",
        "“[Gaspar]” é identificação de sobrenome (Malu Gaspar) inserida pelo veículo na "
        "transcrição publicada (Agência Pública, 15/10/2026); removida do literal; o “(sic)” "
        "consta da publicação e foi preservado",
    ),
    (
        "martha-graeff-daniel-vorcaro.json",
        "m-00014",
        "Tô num jantar na residência oficial com Hugo e seis empresários",
        "a fonte publica “Hugo [Motta, eleito presidente da Câmara no início daquele mês]” — "
        "inserção editorial identificadora (Folha, 05/03/2026); removida do literal",
    ),
    (
        "martha-graeff-daniel-vorcaro.json",
        "m-00017",
        "Indo encontrar Alexandre Moraes aqui perto de casa",
        "“[de]” é complementação gramatical inserida pelo veículo na transcrição publicada "
        "(Folha, 05/03/2026); removida do literal",
    ),
    (
        "martha-graeff-daniel-vorcaro.json",
        "m-00020",
        "quem era o primeiro cara",
        "“[?]” é marcador de incerteza do veículo na transcrição publicada (Folha, 05/03/2026); "
        "removido do literal",
    ),
    (
        "martha-graeff-daniel-vorcaro.json",
        "m-00021",
        "Alexandre Moraes",
        "“[de]” é complementação gramatical inserida pelo veículo na transcrição publicada "
        "(Folha, 05/03/2026); removida do literal",
    ),
    (
        "martha-graeff-daniel-vorcaro.json",
        "m-00023",
        "Sin. Falou que é bem melhor. E ele adorava apto",
        "os marcadores “[sic]” e a glosa “[apartamento]” são inserções editoriais do veículo na "
        "transcrição publicada (Folha, 05/03/2026); removidos do literal — “Sin” e “apto” são a "
        "forma publicada da fala",
    ),
    (
        "walfrido-mares-guia-daniel-vorcaro.json",
        "m-00009",
        "O indicado para presidir a é nosso aliado no Min da Saude.Conhece tudo sobre a Biomm",
        "a fonte publica “presidir a [Anvisa]” — inserção editorial do veículo (Folha, 30/09/2026); "
        "removida do literal; o “a” pendente foi preservado como no texto divulgado",
    ),
]

for rel, mid, new_content, clarification in BRACKET_FIXES:
    t = load(os.path.join("threads", rel))
    for m in t["messages"]:
        if m["id"] == mid:
            old = m["content"]
            m["content"] = new_content
            note = m.get("editorial_note") or ""
            fix = (
                " [Corrigido 2026-10-27: colchete editorial confirmado na fonte e separado do "
                "literal — %s.]" % clarification
            )
            m["editorial_note"] = (note + fix).strip()
            if "[…]" not in new_content and "[...]" not in new_content:
                m.pop("literal_brackets", None)
            else:
                m["literal_brackets"] = True  # apenas o corte do projeto permanece
            changes.append(("bracket-fix", rel, mid, old, new_content))
    save(os.path.join("threads", rel), t)

# ============================================================
# (2) ANDRÉ VALADÃO — mensagens de 27/04/2024 (Pública 18/10)
# ============================================================

rel = "threads/andre-valadao-daniel-vorcaro.json"
av = load(rel)


def valadao_msg(mid, sender, content, note):
    return {
        "id": mid,
        "date": "2024-04-27",
        "time": None,
        "timestamp_precision": "date",
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note,
        "verification": ver_pub_investigation(PROC_PUB18),
        "sources": {
            "primary": None,
            "secondary": [
                {"publication": "Agência Pública", "date": "2026-10-18", "url": URL_PUB18}
            ],
        },
        "source_ref": "Mensagem divulgada por Agência Pública (2026-10-18)",
        "added_in": BATCH,
    }


new_av = [
    valadao_msg(
        "m-00029",
        "daniel-vorcaro",
        "Nikolas repostou a Malu. Loucura isso. Aliás, narrativa ruim pra ele mesmo",
        "Reclamação da repostagem, por Nikolas Ferreira, de publicação da jornalista Malu Gaspar "
        "sobre o evento jurídico realizado em Londres com patrocínio do Banco Master (26/04/2024); "
        "“[Gaspar]” (identificação do veículo) removido do literal. Declaração de apoio político "
        "não comprova financiamento eleitoral ou favorecimento.",
    ),
    valadao_msg(
        "m-00030",
        "daniel-vorcaro",
        "Quem me mandou foi um blog de esquerda, que sabe que apoiamos a direita. "
        "Olha a bola de neve que pode virar",
        "Sequência do mesmo dia, conforme a reportagem; autodeclaração de apoio à direita.",
    ),
    valadao_msg(
        "m-00031",
        "daniel-vorcaro",
        "Eu apoio diversos eventos e debates, e nesse caso o apoio foi com a palestra do Tony "
        "Blair com quem tive um debate de altíssimo nível. No evento, várias pessoas de direita, "
        "apoiadores do evento inclusive vários que apoiaram ele, como nós. Acaba ficando ruim ele "
        "incentivar e propagar um ataque a mim, como fez agora. Só preciso saber se estamos do "
        "mesmo lado ou agora estamos um contra o outro",
        "Explicação do patrocínio do evento de Londres e questionamento da posição do deputado; "
        "“[Nikolas]” (identificação do veículo) removido do literal. O UOL (03/09/2026) publica "
        "trecho da mesma mensagem com divergência de transcrição (“Discurso acaba ficando ruim, "
        "ele incentivou e propagar [sic] um ataque a mim”) — mantida a transcrição da fonte citada.",
    ),
    valadao_msg(
        "m-00032",
        "andre-valadao",
        "Resumindo, ele nem sabia sobre o banco e você, “palavras dele né”, e daí pediu perdão "
        "demais e vai contornar tudo. Deve te chamar também, ele me disse. Disse da gratidão com "
        "você e por aí vai.",
        "Resposta horas depois, relatando conversa com Nikolas Ferreira e o pedido de desculpas "
        "deste — relato de Valadão, não mensagem direta de Nikolas; “[Nikolas]” (identificação do "
        "veículo) removido do literal. Áudio posterior de Nikolas a Vorcaro (30/03/2025) retoma o "
        "episódio — ver thread de Nikolas Ferreira.",
    ),
]

# inserir em posição cronológica: após m-00005 (2024-04-16), antes do bloco sem data
pos = next(i for i, m in enumerate(av["messages"]) if m["id"] == "m-00005") + 1
av["messages"][pos:pos] = new_av
changes.append(("insert", rel, "m-00029..m-00032 (4 mensagens, 2024-04-27)", "", ""))

# ============================================================
# (6a) ANDRÉ VALADÃO — m-00027: data completa não sustentada
# ============================================================
for m in av["messages"]:
    if m["id"] == "m-00027":
        old_date = m.get("date")
        m.pop("date", None)
        m.pop("timestamp_precision", None)
        m["editorial_note"] = (
            "Trecho transcrito dentro do pedido de conversa situado pela reportagem em 17 de "
            "setembro, seguido de duas ligações de cerca de 15 minutos, conforme a reportagem. "
            "[Corrigido 2026-10-27: a fonte (Agência Pública, 24/10/2026) menciona “17 de setembro” "
            "sem explicitar o ano; a data completa anterior (2024-09-17) era derivação da sequência "
            "narrativa e não é sustentada individualmente — a própria reportagem situa as últimas "
            "discussões do terreno “dois meses” antes da prisão de novembro/2025, incompatível com "
            "setembro/2024 para aquele bloco; ano permanece indeterminado (2024 ou 2025), data "
            "completa removida.]"
        )
        changes.append(("date-fix", rel, "m-00027", old_date, "sem data (17/09, ano não explicitado)"))
        break

# atualizar source do thread: incluir a matéria de 18/10 entre as fontes
av["source"]["pages"] = (
    av["source"]["pages"]
    + " Mensagens de 27/04/2024 (episódio Nikolas Ferreira/Londres) publicadas pela Agência "
    "Pública em 18/10/2026 (“apoiamos a direita”) — ver fonte individual de cada registro."
)
save(rel, av)

# ============================================================
# (3) NIKOLAS FERREIRA — m-00001 integral (g1), m-00003 nova
# ============================================================

rel = "threads/nikolas-ferreira-daniel-vorcaro.json"
nik = load(rel)

G1_TRANSCRIPT = (
    "É o seguinte, meu amigo, meu advogado, enfim, irmão meu aqui, comentou comigo e falou "
    "daqui do seu nome. Eu falei: 'não conheço o Dani, enfim, não tenho a proximidade assim, "
    "até mesmo a que eu queria ter, enfim, de conversar e trocar ideia, mas eu o conheço'. "
    "Ele falou: 'cara, tô com um ativo minerário lá, inclusive já passou pela ficha técnica, "
    "o pessoal técnico dele, enfim, tá pendente lá, tem algumas pessoas que sabem disso lá na "
    "empresa'. E eu falei: 'não, ué, eu posso dar um toque nele'. Então assim, não sei nem do "
    "que se trata, mas enfim, como é uma pessoa, enfim, que eu confio totalmente, tô passando "
    "aí pra você, pra se for do teu interesse, passar o contato dele aqui pra vocês tocarem "
    "isso, beleza? No mais, qualquer coisa tô aqui à disposição. Troquei ideia lá com o Pastor "
    "Valadão naquela época, lá naquela postagem, eu falei: 'Pastor, eu não fazia ideia que era "
    "este o Banco do Dani etc. e tudo, se não, obviamente, eu não teria postado, já teria "
    "conversado anteriormente', mas enfim, acabou que a palavra dita não tem como voltar, né? "
    "Mas espero que tenha sido esclarecido, enfim, depois vamos marcar da gente se encontrar "
    "também, tá bem? […]"
)

for m in nik["messages"]:
    if m["id"] == "m-00001":
        m["content"] = G1_TRANSCRIPT
        m["literal_brackets"] = True
        m["editorial_note"] = (
            "Áudio de 30/03/2025 (domingo): pedido relativo ao ex-assessor/advogado Thiago "
            "Rodrigues de Faria e retomada do episódio de Londres/abril de 2024 (intermediação do "
            "pastor André Valadão). Transcrição publicada pelo g1/GloboNews (04/09/2026); trecho "
            "inicial do pedido idêntico ao publicado pelo UOL (03/09/2026) na parte sobreposta. "
            "[Corrigido 2026-10-27: o conteúdo anterior registrava apenas trecho inicial em "
            "transcrição divergente da publicada pelo g1 e sem o trecho final; substituído pela "
            "transcrição do g1 com a despedida suprimida.] O UOL publica abertura adicional "
            "anterior ao trecho (“Ei Dani, tudo bom? Como você está? … Desculpa te incomodar num "
            "domingo aí, é jogo rápido, também não quero tomar muito seu tempo”), não reproduzida "
            "aqui para não costurar transcrições de veículos distintos — daí a marcação de "
            "transcrição parcial. Despedida suprimida por divergência documentada: o g1 transcreve "
            "“Um abração aí, Dani”; o UOL registrou em nota que não fica claro no áudio se foi "
            "“abraço aí, Dani” ou “um abraço, lindão” (primeira versão), e, segundo a Folha "
            "(03/09/2026), a transcrição oficial dos autos registra “lindão” — palavra negada "
            "publicamente por Nikolas; nenhuma variante é verificável nesta base. Divergência "
            "menor entre veículos: “se não” (g1/Folha) vs. “senão” (Agência Pública, 18/10/2026). "
            "[Proveniência revisada 2026-10: reportagem sem procedimento público identificável — "
            "nível secondary_source.]"
        )
        m["verification"]["verified_at"] = TODAY
        m["sources"]["secondary"] = [
            {"publication": "g1/GloboNews", "date": "2026-09-04", "url": URL_G1},
            {"publication": "UOL", "date": "2026-09-03", "url": URL_UOL_NIK},
            {"publication": "Folha de S.Paulo", "date": "2026-09-03", "url": URL_FOLHA_NIK},
            {"publication": "Agência Pública", "date": "2026-10-18", "url": URL_PUB18},
        ]
        m["transcription"] = {
            "kind": "publisher_transcription",
            "source": "g1/GloboNews",
            "complete": False,
        }
        m["transcription_complete"] = False
        changes.append(("fix", rel, "m-00001", "trecho parcial divergente", "transcrição g1 c/ despedida suprimida"))
    if m["id"] == "m-00002":
        m["editorial_note"] = (
            "Resposta escrita após Nikolas enviar o contato de Thiago Rodrigues de Faria, na "
            "sequência do áudio de 30/03/2025; Vorcaro ainda respondeu ao áudio com mensagem de "
            "voz de visualização única (sem transcrição publicada) e, no mesmo dia, com “Deixa "
            "comigo” (m-00003). A data não foi divulgada individualmente. [Proveniência revisada "
            "2026-10: reportagem sem procedimento público identificável — nível secondary_source.] "
            "[Corrigido 2026-10-27: nota anterior a descrevia como resposta em mensagem de "
            "visualização única; a visualização única é resposta distinta, sem transcrição.]"
        )
        m["sources"]["secondary"] = [
            {"publication": "g1/GloboNews", "date": "2026-09-04", "url": URL_G1},
            {"publication": "UOL", "date": "2026-09-03", "url": URL_UOL_NIK},
        ]
        m["verification"]["verified_at"] = TODAY
        changes.append(("fix", rel, "m-00002 (nota)", "", ""))

nik_msg3 = {
    "id": "m-00003",
    "date": "2025-03-30",
    "time": None,
    "timestamp_precision": "date",
    "sender_id": "daniel-vorcaro",
    "content_kind": "verbatim_excerpt",
    "content": "Deixa comigo",
    "editorial_note": (
        "Resposta ao áudio de 30/03/2025, no mesmo dia, conforme mensagens obtidas pelo UOL; "
        "antecede o envio do contato de Thiago Rodrigues de Faria e a resposta “Amém, irmão. "
        "Estamos na guerra juntos” (m-00002)."
    ),
    "verification": ver_secondary(),
    "sources": {
        "primary": None,
        "secondary": [{"publication": "UOL", "date": "2026-09-03", "url": URL_UOL_NIK}],
    },
    "source_ref": "UOL, 03/09/2026",
    "added_in": BATCH,
}
pos = next(i for i, m in enumerate(nik["messages"]) if m["id"] == "m-00001") + 1
nik["messages"][pos:pos] = [nik_msg3]
changes.append(("insert", rel, "m-00003 (Deixa comigo, 2025-03-30)", "", ""))
save(rel, nik)

# ============================================================
# (4) GRUPO "MASTER" — novo thread (BBC/CNN, 11/09/2026)
# ============================================================

def grupo_msg(mid, date, sender, content, note):
    return {
        "id": mid,
        "date": date,
        "time": None,
        "timestamp_precision": "date",
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note,
        "verification": ver_pub_investigation(PROC_BBC),
        "sources": {
            "primary": None,
            "secondary": [
                {"publication": "BBC News Brasil (republicada pelo Estado de Minas)", "date": "2026-09-11", "url": URL_BBC},
                {"publication": "CNN Brasil", "date": "2026-09-11", "url": URL_CNN},
            ],
        },
        "source_ref": "Mensagem divulgada por BBC News Brasil (2026-09-11)",
        "added_in": BATCH,
    }


def grupo_event(eid, date, content, source_ref, url, publication, note=None):
    ev = {
        "id": eid,
        "event_kind": "editorial_context",
        "content": content,
        "verification": ver_pub_investigation(PROC_BBC),
        "source_ref": source_ref,
        "added_in": BATCH,
        "sources": {
            "primary": None,
            "secondary": [{"publication": publication, "date": "2026-09-11", "url": url}],
        },
    }
    if date:
        ev["date"] = date
        ev["timestamp_precision"] = "date"
    if note:
        ev["editorial_note"] = note
    return ev


grupo = {
    "id": "grupo-master-belline-paulo-sergio",
    "title": "Grupo “Master” — Vorcaro, Belline e Paulo Sérgio",
    "participants_ids": ["daniel-vorcaro", "belline-santana", "paulo-sergio"],
    "source": {
        "document": (
            "BBC News Brasil (Luiz Fernando Toledo), 11/09/2026 (republicada pelo Estado de "
            "Minas) e CNN Brasil, 11/09/2026 — grupo de WhatsApp “Master” criado em 02/10/2025 "
            "por Belline Santana (então chefe do Desup/BC) com Daniel Vorcaro e Paulo Sérgio "
            "Neves de Souza (chefe-adjunto), conforme representação da PF ao STF (27/02/2026) "
            "tornada pública em setembro/2026."
        ),
        "url": URL_BBC,
        "pages": (
            "Mensagens conforme transcrições publicadas; a chamada de voz de 27/10/2025 e as "
            "conversas de 13/10/2025 não têm transcrição literal publicada e figuram como "
            "eventos editoriais. Horários não divulgados. As conclusões da PF sobre "
            "favorecimento e pagamentos permanecem como alegações investigativas, com as "
            "manifestações das defesas registradas em evento de contexto."
        ),
    },
    "messages": [
        grupo_msg(
            "m-00001",
            "2025-10-02",
            "belline-santana",
            "Boa tarde. Criei esse grupo, no intuito de facilitar nossa interlocução",
            "Mensagem de criação do grupo “Master” em 02/10/2025, atribuída pela BBC News Brasil "
            "a Belline Santana; participação de Vorcaro e Paulo Sérgio Neves de Souza confirmada "
            "pela BBC e pela CNN.",
        ),
        grupo_msg(
            "m-00002",
            "2025-10-27",
            "daniel-vorcaro",
            "Segue minuta para avaliação",
            "Acompanhou o compartilhamento do arquivo “Ofício Banco Master ao Desup — atualização "
            "das ações”, conforme a BBC News Brasil.",
        ),
        grupo_msg(
            "m-00003",
            "2025-10-27",
            "daniel-vorcaro",
            "Por favor, vejam se atende",
            "Pedido posterior no mesmo dia, após chamada de voz de Belline (sem transcrição "
            "publicada — ver evento) e o envio de nova versão da minuta, conforme a BBC News "
            "Brasil.",
        ),
    ],
    "timeline_events": [
        grupo_event(
            "e-00001",
            None,
            "A PF descreve o grupo como canal de Vorcaro para pedir orientação a chefes da "
            "supervisão bancária e sustenta que Belline e Paulo Sérgio atuavam como "
            "“empregados” do banqueiro em troca de vantagens (contrato de consultoria, "
            "viagens, imóvel rural) — alegações investigativas, não fatos comprovados. "
            "Defesa de Belline nega “desvio de finalidade ou obtenção de vantagem indevida”; "
            "defesa de Paulo Sérgio afirma que ele atuou na identificação das irregularidades "
            "apuradas; BC, BRB e Reag não se manifestaram.",
            "BBC News Brasil (2026-09-11)",
            URL_BBC,
            "BBC News Brasil (republicada pelo Estado de Minas)",
            "Manifestações das defesas conforme a reportagem da BBC News Brasil.",
        ),
        grupo_event(
            "e-00002",
            "2025-10-13",
            "Em conversas de 13/10/2025 no grupo, Vorcaro cogitou que a Desup retirasse "
            "restrições do BRB à compra de carteiras de consignado; Paulo Sérgio avaliou como "
            "decisão difícil (competência da Procuradoria-Geral do BC) e sugeriu a elaboração "
            "de ofício alegando que o recebimento das carteiras estaria em poder do BRB — "
            "relato da CNN Brasil sem transcrição literal publicada.",
            "CNN Brasil (2026-09-11)",
            URL_CNN,
            "CNN Brasil",
        ),
        grupo_event(
            "e-00003",
            "2025-10-27",
            "Entre o envio da minuta e a versão atualizada, Belline fez uma chamada de voz no "
            "grupo; a BBC News Brasil publica a imagem do registro da chamada, sem transcrição "
            "— chamada sem transcrição não é registrada como mensagem.",
            "BBC News Brasil (2026-09-11)",
            URL_BBC,
            "BBC News Brasil (republicada pelo Estado de Minas)",
        ),
    ],
}
save("threads/grupo-master-belline-paulo-sergio.json", grupo)
changes.append(("new-thread", "grupo-master-belline-paulo-sergio.json", "3 mensagens + 3 eventos", "", ""))

# ============================================================
# (5) PAULO SÉRGIO — 2 mensagens literais de 25/04/2025 + evento
# ============================================================

rel = "threads/paulo-sergio-daniel-vorcaro.json"
ps = load(rel)


def ps_msg(mid, content, note):
    return {
        "id": mid,
        "date": "2025-04-25",
        "time": None,
        "timestamp_precision": "date",
        "sender_id": "paulo-sergio",
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note,
        "verification": ver_pub_investigation(PROC_BBC),
        "sources": {
            "primary": None,
            "secondary": [
                {"publication": "BBC News Brasil (republicada pelo Estado de Minas)", "date": "2026-09-11", "url": URL_BBC},
                {"publication": "CNN Brasil", "date": "2026-09-11", "url": URL_CNN},
            ],
        },
        "source_ref": "Mensagem divulgada por BBC News Brasil (2026-09-11)",
        "added_in": BATCH,
    }


ps["messages"].extend(
    [
        ps_msg(
            "m-00009",
            "Importante protocolar rapidamente",
            "Fechamento da revisão da minuta de resposta a termo de comparecimento, na troca "
            "individual de 25/04/2025 (ver evento e-00002); troca individual — anterior à criação "
            "do grupo “Master” (02/10/2025), ao qual não pertence. Ressalva de identidade do "
            "participante aplicável (ver perfil).",
        ),
        ps_msg(
            "m-00010",
            "entendo imprudente citar problema no canal BRB",
            "Recomendação sobre a menção ao BRB na mesma troca de 25/04/2025, conforme a BBC "
            "News Brasil; recomendação não implica que o Banco Master a tenha adotado.",
        ),
    ]
)

ps.setdefault("timeline_events", []).append(
    {
        "id": "e-00002",
        "date": "2025-04-25",
        "timestamp_precision": "date",
        "event_kind": "editorial_context",
        "content": (
            "Vorcaro pediu a Paulo Sérgio, em mensagens individuais, a revisão de minuta de "
            "resposta a termo de comparecimento; Paulo Sérgio propôs alterações (trocar “captação "
            "de receitas” por “captação de recursos”, referências ao controle/gestão do BRB e "
            "correção de data) — pedido e sugestões narrados pela BBC News Brasil, sem transcrição "
            "literal publicada; não é possível afirmar que foram adotadas."
        ),
        "verification": ver_pub_investigation(PROC_BBC),
        "source_ref": "BBC News Brasil (2026-09-11)",
        "added_in": BATCH,
        "editorial_note": "Anterior à criação do grupo “Master” (02/10/2025); troca individual.",
        "sources": {
            "primary": None,
            "secondary": [
                {"publication": "BBC News Brasil (republicada pelo Estado de Minas)", "date": "2026-09-11", "url": URL_BBC}
            ],
        },
    }
)
save(rel, ps)
changes.append(("insert", rel, "m-00009, m-00010, e-00002 (2025-04-25)", "", ""))

# ============================================================
# participants.json — belline-santana novo + resumo de paulo-sergio
# ============================================================

rel = "participants.json"
parts = load(rel)
plist = parts["participants"] if isinstance(parts, dict) else parts

if not any(p["id"] == "belline-santana" for p in plist):
    plist.append(
        {
            "id": "belline-santana",
            "name": "Belline Santana",
            "photo": None,
            "role": "Então chefe do Departamento de Supervisão (Desup) do Banco Central",
            "aliases": [],
            "summary": (
                "Identificado pela BBC News Brasil e pela CNN Brasil (11/09/2026) como então chefe "
                "do Desup (supervisão bancária) do Banco Central e criador, em 02/10/2025, do grupo "
                "de WhatsApp “Master” com Daniel Vorcaro e Paulo Sérgio Neves de Souza. A PF "
                "sustenta, em representação ao STF, que atuava em favor de Vorcaro em troca de "
                "vantagens (contrato de consultoria de R$ 500 mil por semestre e despesas em Paris) "
                "— alegação investigativa; sua defesa nega “desvio de finalidade ou obtenção de "
                "vantagem indevida” (nota de 04/2026) e afirma não saber que os pagamentos "
                "vinham do Master."
            ),
            "profile_sources": [
                {
                    "label": "BBC News Brasil (republicada pelo Estado de Minas) — 11/09/2026",
                    "url": URL_BBC,
                },
                {"label": "CNN Brasil — 11/09/2026", "url": URL_CNN},
            ],
        }
    )
    changes.append(("new-participant", rel, "belline-santana", "", ""))

for p in plist:
    if p["id"] == "paulo-sergio":
        if "BBC News Brasil" not in p["summary"]:
            p["summary"] += (
                " A BBC News Brasil (11/09/2026) o identifica como chefe-adjunto do Desup e "
                "participante, com Belline Santana e Vorcaro, do grupo de WhatsApp “Master” criado "
                "em 02/10/2025 (ver conversa própria); em 25/04/2025, em mensagens individuais, "
                "revisou a pedido de Vorcaro minuta de resposta a termo de comparecimento. A PF "
                "sustenta que recebeu vantagens de Vorcaro (imóvel rural de R$ 4,8 milhões, viagem "
                "a Disney) — alegação investigativa; sua defesa (08/2026) afirma que ele atuou na "
                "identificação das irregularidades do caso."
            )
            p.setdefault("profile_sources", []).append(
                {
                    "label": "BBC News Brasil (republicada pelo Estado de Minas) — 11/09/2026",
                    "url": URL_BBC,
                }
            )
            changes.append(("profile-update", rel, "paulo-sergio (resumo estendido)", "", ""))
save(rel, parts)

# ============================================================
# threads.json — contagens, previews, entrada nova
# ============================================================

rel = "threads.json"
idx = load(rel)
threads_list = idx["threads"] if isinstance(idx, dict) else idx


def counts(tid):
    t = load(os.path.join("threads", tid + ".json"))
    msgs = t["messages"]
    return len(msgs), (msgs[-1]["content"] if msgs else ""), msgs[-1].get("date")


for e in threads_list:
    if e["id"] == "andre-valadao-daniel-vorcaro":
        n, prev, _ = counts(e["id"])
        e["message_count"] = n
        e["last_message_preview"] = prev
    if e["id"] == "nikolas-ferreira-daniel-vorcaro":
        n, prev, d = counts(e["id"])
        e["message_count"] = n
        e["last_message_preview"] = prev
        if d:
            e["last_message_date"] = d
    if e["id"] == "paulo-sergio-daniel-vorcaro":
        n, prev, d = counts(e["id"])
        e["message_count"] = n
        e["last_message_preview"] = prev
        if d:
            e["last_message_date"] = d
        e["note"] = (
            "Diretor do Banco Central (segundo o IPJ-A). Em 28/02/2025, questiona uso de R$ 800 "
            "milhões do compulsório; em 19/03/2025, Vorcaro escreve que está “com Moraes aqui”. "
            "Em 25/04/2025, revisa a pedido de Vorcaro minuta de resposta a termo de "
            "comparecimento (BBC, 11/09/2026); participa do grupo “Master” (02/10/2025)."
        )

new_entry = {
    "id": "grupo-master-belline-paulo-sergio",
    "title": "Grupo “Master” — Vorcaro, Belline e Paulo Sérgio",
    "participants_ids": ["daniel-vorcaro", "belline-santana", "paulo-sergio"],
    "message_count": 3,
    "last_message_preview": "Por favor, vejam se atende",
    "last_message_date": "2025-10-27",
    "featured": False,
    "note": (
        "Grupo de WhatsApp criado em 02/10/2025 por Belline Santana (então chefe do Desup/BC) com "
        "Vorcaro e Paulo Sérgio Neves de Souza para interlocução sobre assuntos do Banco Master "
        "(BBC News Brasil e CNN Brasil, 11/09/2026)."
    ),
}
# inserir em ordem alfabética, logo após grupo-ciro-daniel-fabio-hugo
pos = next(i for i, e in enumerate(threads_list) if e["id"] == "grupo-ciro-daniel-fabio-hugo") + 1
threads_list[pos:pos] = [new_entry]
save(rel, idx)
changes.append(("index", rel, "grupo novo + contagens/preview atualizados", "", ""))

# ============================================================
print("=" * 64)
for c in changes:
    print(" [%s] %s · %s" % (c[0], c[1], c[2]))
print("=" * 64)
print("total de alterações:", len(changes))
