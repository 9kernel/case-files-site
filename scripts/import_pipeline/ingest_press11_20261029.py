# -*- coding: utf-8 -*-
"""
ingest_press11_20261029.py — rodada de 29/10/2026 (lote ingest-press11-20261029).

Conteúdo (todas as citações verificadas em duas extrações independentes ou
confirmação dirigida; grafia original preservada; "(sic)" do veículo mantido):
  - ana-matos: +1 (15/10/2024, ICL) + extensão do evento de contexto CNN.
  - ciro-soares: +16 mensagens de fevereiro/2025 (Noites Húngaras/ICL) + evento
    com as notas do gabinete de Mendonça e de Ciro.
  - flavio-carneiro: +8 (04/09, 20/09, dez/2024, 14/05/2025, 17/07/2025 e
    par de abril/2024 dos voos) + correção de m-00002/03 (transcrição integral
    com grafia original do Estadão; data 20/09/2024) + m-00023 datado
    (abril/2024, mês) + evento com manifestação de Arthur Lira e silêncios.
  - lilian-tahan: +2 (02/04/2025, Estadão/Infoverus).
  - cezinha: +1 confirmação adicional de 13/03/2025 (ICL).
  - andre-valadao: +3 (pedido "De novo pedir sua ajuda", resposta e áudio do
    pastor — ICL/UOL) + m-00026 sem data completa (ano não comprovado) +
    notas de divergência de cronologia ICL x Pública.
  - nikolas: nota de m-00001 ganha a variante do ICL ("Um abraço, lindão");
    e-00002 ampliado com o contexto de 2022 do ICL.

Correções estruturais (fix_order_index_20261029.py) já aplicadas antes deste
script: reordenação das 4 conversas, índice de datas e validador endurecido.
"""

import json
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
BATCH = "ingest-press11-20261029"
TODAY = "2026-10-29"

URL_ICL_CNN = "https://iclnoticias.com.br/patrocinio-10-milhoes-vorcaro-cnn-entrevista/"
URL_ICL_NIK = "https://iclnoticias.com.br/nikolas-voos-vorcaro-mensagens-master/"
URL_ICL_VAZA = "https://iclnoticias.com.br/vaza-mendonca-mensagens-e-audios-ineditos/"
URL_INFOVERUS = "https://www.infoverus.com.br/politica/daniel-vorcaro-exigiu-que-sites-controlados-por-ele-poupassem-hugo-motta-lira-e-ciro-nogueira-sai-nada-sem-me-falar/37199"
URL_UOL_BJ = "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/brazil-journal-istoe-como-vorcaro-montou-rede-de-influencia-em-sites.htm"
URL_PUB18 = "https://apublica.org/2026/10/banco-master-a-amigo-vorcaro-se-disse-apoiador-da-direita/"
URL_PUB24 = "https://apublica.org/2026/10/daniel-vorcaro-e-os-lacos-com-andre-valadao-da-igreja-lagoinha/"


def load(rel):
    with io.open(os.path.join(DATA, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def save(rel, obj):
    with io.open(os.path.join(DATA, rel), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def ver(level, proceeding=None, origin="press report", authority="Polícia Federal"):
    return {
        "level": level,
        "origin": origin,
        "authority": authority if level == "public_investigation" else None,
        "court": None,
        "case": None,
        "document": None,
        "page": None,
        "figure": None,
        "official_url": None,
        "primary_document_located": False,
        "verified_at": TODAY,
        **({"proceeding": proceeding} if proceeding else {}),
    }


def sec(pub, date, url):
    return {"primary": None, "secondary": [{"publication": pub, "date": date, "url": url}]}


PROC_ICL_SERIE = (
    "PF — série do ICL Notícias (Núcleo Investigativo) sobre mensagens do celular de "
    "Vorcaro apreendidas pela PF; a reportagem não nomeia o procedimento individualmente"
)
PROC_VAZA = (
    "Material do celular de Vorcaro veiculado pela newsletter Noites Húngaras (Paulo "
    "Motoryn) e reproduzido pelo ICL Notícias (03/09/2026, atualizada em 28/10/2026); "
    "origem da extração não especificada na reportagem"
)
PROC_ESTADAO = (
    "PF — mensagens do celular de Vorcaro reportadas pela apuração do Estadão "
    "(23/10/2026, reproduzida pelo Infoverus) e pelo UOL (15/10/2026); procedimento "
    "individual não nomeado pelas reportagens"
)

n_msg = 0
n_evt = 0


def msg(mid, date, sender, content, note, pub, pubdate, url, source_ref,
        precision="date", time=None, proceeding=None, level="public_investigation"):
    global n_msg
    n_msg += 1
    return {
        "id": mid,
        "date": date,
        "time": time,
        "timestamp_precision": precision,
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note,
        "verification": ver(level, proceeding),
        "sources": sec(pub, pubdate, url),
        "source_ref": source_ref,
        "added_in": BATCH,
    }


# ============================================================
# ANA MATOS — 15/10/2024 + evento de contexto CNN ampliado
# ============================================================
rel = "threads/ana-matos-daniel-vorcaro.json"
t = load(rel)
new = msg(
    "m-00076", "2024-10-15", "daniel-vorcaro",
    "Cnn deu um ruido grande. Nao gostei postura joao. Estou avaliando o que fazer.",
    "Insatisfação com a postura de João Camargo (então presidente executivo do Conselho da "
    "CNN Brasil, identificado pela reportagem); no dia seguinte, Ana Matos relatou que o "
    "vice-presidente comercial dizia que o banco já teria feito “um primeiro aporte como "
    "acionistas” — ver evento de contexto; negociação não comprova participação societária "
    "concretizada (a CNN nega).",
    "ICL Notícias", "2026-10-19", URL_ICL_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)",
    proceeding=PROC_ICL_SERIE,
)
# posição cronológica: após m-00037 (2024-10-01), antes do bloco 2024-11 (m-00001)
pos = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00037") + 1
t["messages"][pos:pos] = [new]
for e in t["timeline_events"]:
    if e["id"] == "e-00003":
        e["content"] += (
            " [Ampliado 2026-10-29 (ICL, 19/10): em 15/10/2024 Vorcaro manifestou insatisfação "
            "com a postura de João Camargo; em 16/10/2024 Ana escreveu que a vice-presidência "
            "comercial dizia que o banco já tinha feito “um primeiro aporte como acionistas” — "
            "relato em fala indireta, sem transcrição integral publicada.]"
        )
save(rel, t)
print("[ana-matos] +1 mensagem (15/10/2024) + evento e-00003 ampliado")

# ============================================================
# CIRO SOARES — fevereiro de 2025 (Noites Húngaras/ICL)
# ============================================================
rel = "threads/ciro-soares-daniel-vorcaro.json"
t = load(rel)


def cmsg(mid, date, sender, content, note, precision="date", time=None):
    return msg(mid, date, sender, content, note,
               "ICL Notícias", "2026-09-03", URL_ICL_VAZA,
               "Mensagem divulgada por ICL Notícias (2026-09-03)", precision, time, PROC_VAZA)


ciro_new = [
    cmsg("m-00025", "2025-02-07", "ciro-soares", "Opa",
         "Após tentativas repetidas de ligação de Ciro a Vorcaro naquele dia, conforme a reportagem."),
    cmsg("m-00026", "2025-02-07", "ciro-soares", "me liga",
         "Na mesma sequência de 07/02/2025."),
    cmsg("m-00027", "2025-02-07", "ciro-soares", "Tô André M.",
         "Publicado como “Tô [com] André M.” — “(com)” é complementação inserida pelo veículo e "
         "foi removida do literal; “André M.” é André Mendonça conforme a reportagem.", "minute", "14:03"),
    cmsg("m-00028", "2025-02-08", "ciro-soares",
         "Fala, Vorcarinho, trabalhando por você! Levei o André lá no Vasco agora, pra fazer um terno.",
         "Trecho de áudio de 6 segundos transcrito pela reportagem; acompanhava foto ao lado de "
         "André Mendonça em alfaiataria (imagem não reproduzida)."),
    cmsg("m-00029", "2025-02-16", "ciro-soares",
         "Opa, Dani!!! Preciso muito falar com você. O A.M. quer recebê-lo. E preciso agendar o quanto antes",
         "“A.M.” é André Mendonça conforme a reportagem.", "minute", "17:47"),
    cmsg("m-00030", "2025-02-16", "ciro-soares",
         "Muito importante sua ida nele junto comigo",
         "Reforço na mesma sequência de 16/02/2025."),
    cmsg("m-00031", "2025-02-16", "daniel-vorcaro", "?",
         "Resposta na mesma sequência; horário não divulgado."),
    cmsg("m-00032", "2025-02-16", "daniel-vorcaro", "Marca quarta",
         "Resposta na mesma sequência; “quarta” = 19/02/2025."),
    cmsg("m-00033", "2025-02-16", "ciro-soares",
         "Você é meu irmão caçula, meu protegido",
         "Na troca de aniversário em que Vorcaro chamou Ciro de “irmão, anjo da guarda, parceiro, "
         "amigo de verdade” (fragmentos citados pela reportagem)."),
    cmsg("m-00034", "2025-02-16", "ciro-soares",
         "O André Mendonça fez uma homenagem pra mim do caralho no aniversário",
         "Trecho de áudio de 1min39s transcrito pela reportagem; o aniversário contou, segundo o "
         "relato, com a presença de Kassio Nunes Marques e Paulo Gonet."),
    cmsg("m-00035", "2025-02-16", "ciro-soares",
         "O André quer te receber. Acho que eu dei uma balançada nele naquele assunto.",
         "Trecho do mesmo áudio de 16/02/2025 transcrito pela reportagem."),
    cmsg("m-00036", "2025-02-16", "ciro-soares",
         "O André Mendonça disse que quer te receber junto comigo, me pediu até pra levar o Otto. "
         "Ele sabe, soube da situação do Banco Central toda. Eu contei. Ele já sabia que o Cezinha, "
         "Cezinha já tinha falado com ele.",
         "Trecho do mesmo áudio; RELATO de Ciro — não comprova interferência de André Mendonça no "
         "Banco Central nem conhecimento dele sobre o caso; “Otto” citado sem identificação "
         "adicional. Manifestações do gabinete e de Ciro no evento de contexto."),
    cmsg("m-00037", "2025-02-17", "ciro-soares",
         "Dani, estou saindo de BSB agora. Estava numa reunião. Preciso falar com você hoje. Podemos marcar às 18h",
         "Sequência de 17/02/2025."),
    cmsg("m-00038", "2025-02-17", "ciro-soares", "subindo",
         "Após ligação de 18 segundos, conforme a reportagem."),
    cmsg("m-00039", "2025-02-17", "ciro-soares", "Cezinha confirmou às 16h de quarta",
         "“Quarta” = 19/02/2025; Cezinha de Madureira, ver conversa própria.", "minute", "19:08"),
    cmsg("m-00040", "2025-02-19", "ciro-soares",
         "Ô, Dani, deixa eu te falar aqui, pede ao Bruno Bianco chegar aqui quatro e meia, pode ser? "
         "Que aí a gente faz uma apresentação aqui. Ou quatro e vinte",
         "Trecho de áudio transcrito pela reportagem; o material divulga o AGENDAMENTO, não a "
         "realização da reunião; Bruno Bianco citado sem identificação adicional."),
]
pos = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00006") + 1
t["messages"][pos:pos] = ciro_new
t["timeline_events"].append({
    "id": "e-00002",
    "event_kind": "editorial_context",
    "content": (
        "Contraditório (ICL Notícias, 03/09/2026, atualizada em 28/10): o gabinete de André "
        "Mendonça confirmou ter recebido Vorcaro uma única vez (março/2025), por iniciativa do "
        "próprio empresário, para tratar da STP 976 (precatórios), então com pedido de vista, "
        "alegando decisão contrária à posição do banco. Ciro Rocha Soares, em nota, afirmou que "
        "marcar conversas com magistrados é prática natural da advocacia, que Vorcaro não era "
        "investigado à época e que Mendonça não era relator do caso Master; classificou a "
        "veiculação como quebra de sigilo da relação advogado-cliente. Os relatos de Ciro não "
        "comprovam interferência de Mendonça no Banco Central."
    ),
    "verification": ver("public_investigation", PROC_VAZA),
    "source_ref": "ICL Notícias (2026-09-03)",
    "added_in": BATCH,
    "sources": sec("ICL Notícias", "2026-09-03", URL_ICL_VAZA),
})
save(rel, t)
print("[ciro-soares] +16 mensagens (fev/2025) + evento e-00002 (contraditório)")

# ============================================================
# FLÁVIO CARNEIRO — novas mensagens + correções m-00002/03/23
# ============================================================
rel = "threads/flavio-carneiro-daniel-vorcaro.json"
t = load(rel)


def fmsg(mid, date, sender, content, note, precision="date", time=None):
    return msg(mid, date, sender, content, note,
               "Estadão (reproduzido pelo Infoverus)", "2026-10-23", URL_INFOVERUS,
               "Mensagem divulgada pelo Estadão (2026-10-23)", precision, time, PROC_ESTADAO)


for m in t["messages"]:
    if m["id"] == "m-00002":
        m["content"] = "Qq coisa de ciro arthur hugo nao pode sair nada sem me flaar"
        m["date"] = "2024-09-20"
        m["timestamp_precision"] = "date"
        m["editorial_note"] = (
            "Sobre publicações envolvendo Ciro Nogueira, Arthur Lira e Hugo Motta, na sequência "
            "do pedido de retirada de publicação sobre Lira (m-00027). "
            "[Corrigido 2026-10-29: texto atualizado para a transcrição do Estadão (23/10), que "
            "preserva a grafia original (“Qq”, “flaar”) e a data individual 20/09/2024; a versão "
            "anterior registrava a transcrição normalizada do UOL (“Qualquer coisa de Ciro, Arthur, "
            "Hugo não pode sair nada sem me falar”) com precisão de mês — grafia original não é "
            "normalizável; fontes UOL e Estadão unificadas.]"
        )
        m["sources"]["secondary"].append(
            {"publication": "Estadão (reproduzido pelo Infoverus)", "date": "2026-10-23", "url": URL_INFOVERUS})
        m["verification"]["verified_at"] = TODAY
    if m["id"] == "m-00003":
        m["content"] = "Ok. Vou colocar o Lira nessa lista agora. Realmente nao tava"
        m["date"] = "2024-09-20"
        m["timestamp_precision"] = "date"
        m["editorial_note"] = (
            "Resposta na mesma sequência de 20/09/2024. "
            "[Corrigido 2026-10-29: transcrição completada conforme o Estadão (23/10) — a versão "
            "anterior (UOL) omitia “Ok.” e “Realmente nao tava”; data individual 20/09/2024.]"
        )
        m["sources"]["secondary"].append(
            {"publication": "Estadão (reproduzido pelo Infoverus)", "date": "2026-10-23", "url": URL_INFOVERUS})
        m["verification"]["verified_at"] = TODAY
    if m["id"] == "m-00023":
        m["date"] = "2024-04"
        m["timestamp_precision"] = "month"
        m["sources"]["secondary"].append(
            {"publication": "ICL Notícias", "date": "2026-09-03", "url": URL_ICL_NIK})
        m["verification"]["verified_at"] = TODAY
        m["editorial_note"] = (
            "Reclamação sobre os posts de Nikolas Ferreira, situada pelo ICL Notícias (03/09/2026) "
            "em abril de 2024; a Folha (21/10/2026) retomou a divulgação. A declaração de Vorcaro "
            "não especifica quantos voos nem qual período — não comprova pagamentos individualmente."
            " [Corrigido 2026-10-29: acrescentados fonte ICL e abril/2024 com precisão de mês — "
            "dia não divulgado; antes sem data.]"
        )

by_id = {m["id"]: m for m in t["messages"]}
flavio_new = {
    "m-00027": fmsg("m-00027", "2024-09-20", "daniel-vorcaro",
                    "Porra cara. Tira isso do ar agora",
                    "Sobre publicação envolvendo Arthur Lira, antes da orientação registrada em "
                    "m-00002; pedido de retirada não comprova retirada efetivamente realizada."),
    "m-00028": fmsg("m-00028", "2024-09-04", "daniel-vorcaro",
                    "So pra avisar. Nenhum de nossos veiculos pode falar NADA contra Hugo motta. "
                    "Estao tentando plantar coisas contra. Segure isso",
                    "A reportagem descreve sequência de quatro mensagens; a transcrição publicada é "
                    "reproduzida como um bloco. Orientação editorial sobre cobertura — não comprova "
                    "que Motta tenha solicitado proteção."),
    "m-00029": fmsg("m-00029", "2024-12", "daniel-vorcaro",
                    "Foda hein. Cara nem ta na operacao. Metropoles ta foda",
                    "Dezembro/2024, após operação da PF, comentando matéria do Metrópoles sobre "
                    "pessoa que não constava da operação (Hugo Motta, conforme o contexto da "
                    "apuração).", "month"),
    "m-00030": fmsg("m-00030", "2025-05-14", "daniel-vorcaro",
                    "Ou resolce isso agora em todos. Ou ta cancelado todo projeto. Isso passou dos linutes",
                    "Sobre vídeo envolvendo Ciro Nogueira; grafia original preservada (“resolce”, "
                    "“linutes”)."),
    "m-00031": fmsg("m-00031", "2025-05-14", "daniel-vorcaro",
                    "Nao da pra bancar agenda propria de caras contra o cara que é um irmao. "
                    "Unica resistencia fiel que tenho",
                    "Na mesma sequência sobre o vídeo envolvendo Ciro Nogueira; “o cara que é um "
                    "irmao” refere-se a Ciro Nogueira conforme o contexto da reportagem."),
    "m-00032": fmsg("m-00032", "2025-07-17", "daniel-vorcaro",
                    "Preciso que faca algumas materias falando bem do hugo. Cara ta apanhando demais "
                    "e injustamente",
                    "Pedido de cobertura favorável a Hugo Motta; pedidos não comprovam matérias "
                    "efetivamente publicadas a pedido."),
    "m-00033": fmsg("m-00033", "2025-07-17", "flavio-carneiro",
                    "Vou fazer uma agenda positiva ja !!!",
                    "Resposta na mesma sequência; a reportagem cita também fala sobre ter “muita "
                    "pauta boa pra fazer”."),
    "m-00034": fmsg("m-00034", "2024-04", "daniel-vorcaro",
                    "Vouch (sic) mandar soltsr isso",
                    "Mensagem seguinte a “Esse Nikolas eu banquei todos os voos dele” (m-00023), "
                    "sobre divulgar a informação; “(sic)” é marcação do veículo para a grafia "
                    "original, preservada. Áinda assim não comprova pagamentos individualmente.",
                    "month"),
}
# ordem-alvo do thread (m-00023 e par de abril movidos ao bloco inicial; bloco 20/09
# após 04/09; restante inalterado)
order = (
    ["m-00001", "m-00023", "m-00034"]
    + ["m-00024", "m-00025", "m-00026"]
    + ["m-00028", "m-00027", "m-00002", "m-00003"]
    + ["m-00004", "m-00005", "m-00006", "m-00007", "m-00008", "m-00009", "m-00010", "m-00011", "m-00012"]
    + ["m-00029"]
    + ["m-00013", "m-00014", "m-00015", "m-00016", "m-00017", "m-00018"]
    + ["m-00030", "m-00031"]
    + ["m-00032", "m-00033"]
    + ["m-00019", "m-00020", "m-00021", "m-00022"]
)
assert set(order) == (set(by_id) | set(flavio_new)) and len(order) == len(by_id) + len(flavio_new)
msgs = [by_id[i] for i in order if i in by_id] + []
out = []
for i in order:
    out.append(flavio_new[i] if i in flavio_new else by_id[i])
t["messages"] = out
t["timeline_events"].append({
    "id": "e-00006",
    "event_kind": "editorial_context",
    "content": (
        "Manifestações (Estadão, 23/10/2026): Arthur Lira, por assessoria, negou proximidade com "
        "Vorcaro, afirmou nunca ter trocado mensagens ou ligações com ele e nunca ter feito pedidos, "
        "e disse não poder responder por diálogos de terceiros; Hugo Motta e Ciro Nogueira, "
        "procurados, não se manifestaram. As mensagens trocadas entre Carneiro e Vorcaro não "
        "comprovam que os parlamentares tenham solicitado proteção editorial."
    ),
    "verification": ver("public_investigation", PROC_ESTADAO),
    "source_ref": "Estadão (reproduzido pelo Infoverus) (2026-10-23)",
    "added_in": BATCH,
    "sources": sec("Estadão (reproduzido pelo Infoverus)", "2026-10-23", URL_INFOVERUS),
})
save(rel, t)
print("[flavio-carneiro] +8 mensagens; m-00002/03 corrigidas (grafia original, 20/09); m-00023 datado (abr/2024) e reposicionado; +evento e-00006")

# ============================================================
# LILIAN TAHAN — complemento de 02/04/2025 (Estadão/Infoverus)
# ============================================================
rel = "threads/lilian-tahan-daniel-vorcaro.json"
t = load(rel)
tahan_new = [
    msg("m-00026", "2025-04-02", "daniel-vorcaro",
        "Mas tem que ser um jeito que nao pareça que nao tem interesse. So desmentir quem falou "
        "que tinha proposta de 1 real",
        "Orientação sobre a apresentação do desmentido da suposta proposta de R$ 1, na sequência "
        "de m-00001/m-00002.",
        "Estadão (reproduzido pelo Infoverus)", "2026-10-23", URL_INFOVERUS,
        "Mensagem divulgada pelo Estadão (2026-10-23)", proceeding=PROC_ESTADAO),
    msg("m-00027", "2025-04-02", "lilian-tahan", "Deixa comigo",
        "Resposta na mesma sequência de 02/04/2025 — registro distinto de m-00016 (agosto/2025, "
        "contexto Cappelli). O Estadão cita ainda resposta mais completa de Tahan (“Se tiver alguma "
        "incorreção, me avise!! Não tem pressa. No seu tempo. Não publicarei sem nos falarmos”); a "
        "correspondência dessa transcrição com m-00025 (situada pelo UOL em outro contexto) não é "
        "determinável — mantidas sem unificação.",
        "Estadão (reproduzido pelo Infoverus)", "2026-10-23", URL_INFOVERUS,
        "Mensagem divulgada pelo Estadão (2026-10-23)", proceeding=PROC_ESTADAO),
]
pos = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00002") + 1
t["messages"][pos:pos] = tahan_new
save(rel, t)
print("[lilian-tahan] +2 mensagens (02/04/2025)")

# ============================================================
# CEZINHA — confirmação adicional de 13/03/2025 (ICL)
# ============================================================
rel = "threads/cezinha-de-madureira-daniel-vorcaro.json"
t = load(rel)
cez = msg("m-00009", "2025-03-13", "cezinha-de-madureira",
          "Amanhã sexta-feira 14 às 17:00",
          "Confirmação adicional do dia e do horário do encontro de 14/03/2025 com o ministro "
          "André Mendonça; grafia original preservada (“14” = 14/03). O ICL situa-a em sequência "
          "diversa da transcrita pelo CartaCapital (que registra “Estarei lá para te receber” ao "
          "final) — mesma data, ordenação entre veículos não determinável. Endereço já registrado "
          "em m-00002; dados de localização não republicados.",
          "ICL Notícias", "2026-09-03", URL_ICL_VAZA,
          "Mensagem divulgada por ICL Notícias (2026-09-03)", proceeding=PROC_VAZA)
pos = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00005") + 1
t["messages"][pos:pos] = [cez]
save(rel, t)
print("[cezinha] +1 mensagem (13/03/2025)")

# ============================================================
# ANDRÉ VALADÃO — +3 (ICL/UOL) e m-00026 sem data completa
# ============================================================
rel = "threads/andre-valadao-daniel-vorcaro.json"
t = load(rel)
val_new = [
    msg("m-00033", "2024-04-27", "daniel-vorcaro",
        "De novo pedir sua ajuda com Nikolas. Estão usando a fala dele pra me atacar, por conta de "
        "patrocínio num evento em Londres. Acontece, que talvez ele não saiba, participaram vários "
        "membros da direita, como Ciro Nogueira, um dos líderes oposição",
        "Pedido de ajuda ao pastor na sequência do episódio de Londres (ICL Notícias, 03/09/2026, "
        "situa em 27/04/2024); grafia original preservada. [Proveniência revisada 2026-10-29: "
        "reportagem do ICL sem cadeia de origem declarada individualmente — nível secondary_source.]",
        "ICL Notícias", "2026-09-03", URL_ICL_NIK,
        "Mensagem divulgada por ICL Notícias (2026-09-03)",
        level="secondary_source", origin="PF extraction"),
    msg("m-00034", "2024-04-27", "andre-valadao",
        "Oi Dani. Claro amanhã falo com ele",
        "Resposta prometendo falar com Nikolas no dia seguinte (ICL Notícias, 03/09/2026). "
        "[Proveniência revisada 2026-10-29: reportagem do ICL sem cadeia de origem declarada "
        "individualmente — nível secondary_source.]",
        "ICL Notícias", "2026-09-03", URL_ICL_NIK,
        "Mensagem divulgada por ICL Notícias (2026-09-03)",
        level="secondary_source", origin="PF extraction"),
    msg("m-00035", "2024-04", "andre-valadao",
        "Eu falei com ele né, de todo apreço, de todo apoio que a gente tem e tudo, e que as coisas "
        "às vezes chegam pra ele de um jeito que não é a verdade. Ele vai me chamar aqui",
        "Trecho de áudio transcrito pela reportagem (ICL, 03/09/2026; também publicado pelo UOL, "
        "03/09/2026), na sequência de abril de 2024 — relato do pastor sobre a conversa com Nikolas "
        "Ferreira; precisão de mês, dia não divulgado individualmente. [Proveniência revisada "
        "2026-10-29: reportagem do ICL sem cadeia de origem declarada individualmente — nível "
        "secondary_source.]",
        "ICL Notícias", "2026-09-03", URL_ICL_NIK,
        "Mensagem divulgada por ICL Notícias (2026-09-03)", precision="month",
        level="secondary_source", origin="PF extraction"),
]
pos = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00031") + 1
t["messages"][pos:pos] = val_new
for m in t["messages"]:
    if m["id"] == "m-00026":
        m.pop("date", None)
        m.pop("timestamp_precision", None)
        m["editorial_note"] = (
            "Cobrança de resposta sobre o terreno em Orlando situada pela reportagem em 15 de "
            "agosto, sem ano explícito na passagem correspondente; as reticências constam do texto "
            "publicado. A reportagem não confirma a conclusão da aquisição. "
            "[Corrigido 2026-10-29: a data completa anterior (2024-08-15) era derivação da sequência "
            "narrativa — a própria reportagem situa as últimas discussões do terreno “dois meses” "
            "antes da prisão de novembro/2025, incompatível com agosto/2024 para aquele bloco; ano "
            "permanece indeterminado (2024 ou 2025), data completa removida. A correção de m-00027 "
            "(2026-10-27) segue mantida.]"
        )
    if m["id"] == "m-00031":
        m["editorial_note"] += (
            " [Nota 2026-10-29: o ICL Notícias (03/09/2026) apresenta a frase final (“Só preciso "
            "saber se estamos do mesmo lado ou agora estamos um contra o outro”) como mensagem "
            "posterior a 29/04/2024, quando Nikolas repercutiu nova publicação; a Agência Pública "
            "(18/10/2026) a transcreve como fecho desta mensagem de 27/04 — divergência entre "
            "fontes registrada, sem alteração de data.]"
        )
    if m["id"] == "m-00032":
        m["sources"]["secondary"].append(
            {"publication": "ICL Notícias", "date": "2026-09-03", "url": URL_ICL_NIK})
        m["editorial_note"] += (
            " [Nota 2026-10-29: o ICL Notícias (03/09/2026) publica a mesma mensagem em transcrição "
            "própria (“Resumindo. Ele nem sabia sobre o banco e vc ‘palavras dele né’ e daí pediu "
            "perdão demais e vai contornar tudo”), situando-a após áudio do pastor e sem data "
            "individual — mantida a transcrição e a data da fonte citada (Agência Pública).]"
        )
t["source"]["pages"] += " Mensagens de abril/2024 do episódio Nikolas/Londres também publicadas pelo ICL Notícias (03/09/2026)."
save(rel, t)
print("[andre-valadao] +3 mensagens; m-00026 sem data completa; notas de divergência ICL x Pública")

# ============================================================
# NIKOLAS — nota da despedida (variante ICL) + e-00002 ampliado
# ============================================================
rel = "threads/nikolas-ferreira-daniel-vorcaro.json"
t = load(rel)
for m in t["messages"]:
    if m["id"] == "m-00001":
        m["editorial_note"] = m["editorial_note"].replace(
            "transcrição oficial dos autos registra “lindão” — palavra negada "
            "publicamente por Nikolas; nenhuma variante é verificável nesta base.",
            "transcrição oficial dos autos registra “lindão” (também transcrita pelo ICL Notícias, "
            "03/09/2026: “Um abraço, lindão.”) — palavra negada publicamente por Nikolas; nenhuma "
            "variante é verificável nesta base.",
        )
        m["sources"]["secondary"].append(
            {"publication": "ICL Notícias", "date": "2026-09-03", "url": URL_ICL_NIK})
for e in t["timeline_events"]:
    if e["id"] == "e-00002":
        e["content"] += (
            " [Ampliado 2026-10-29 (ICL, 03/09): o uso da aeronave em 2022 teria ocorrido por cerca "
            "de dez dias do 2º turno, em nove estados e o DF, com o pastor Guilherme Batista.]"
        )
save(rel, t)
print("[nikolas] nota de m-00001 com variante ICL; e-00002 ampliado")

# ============================================================
# participants.json — perfil de ciro-soares estendido
# ============================================================
rel = "participants.json"
parts = load(rel)
for p in parts:
    if p["id"] == "ciro-soares":
        if "ICL Notícias" not in p["summary"]:
            p["summary"] += (
                " O ICL Notícias (03/09/2026, material veiculado pela newsletter Noites Húngaras) o "
                "descreve como advogado baiano próximo de Vorcaro (“irmão caçula”) e intermediário "
                "de contatos com o ministro André Mendonça (STF) — ver conversa própria; os relatos "
                "de Ciro não comprovam interferência do ministro no Banco Central."
            )
            p.setdefault("profile_sources", []).append(
                {"label": "ICL Notícias (Noites Húngaras) — 03/09/2026", "url": URL_ICL_VAZA})
save(rel, parts)
print("[participants] ciro-soares estendido")

# ============================================================
# threads.json — contagens, preview do flavio
# ============================================================
rel = "threads.json"
idx = load(rel)
for e in idx:
    tt = load(f"threads/{e['id']}.json")
    n = len(tt["messages"])
    if e.get("message_count") != n:
        print(f"[index] {e['id']}: message_count {e.get('message_count')} -> {n}")
        e["message_count"] = n
    if e["id"] == "flavio-carneiro-daniel-vorcaro":
        e["last_message_preview"] = tt["messages"][-1]["content"]
save(rel, idx)

print("=" * 60)
print(f"novas mensagens: {n_msg} | novos eventos: 2")
