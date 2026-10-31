# -*- coding: utf-8 -*-
# ingest_press12_20261030.py — rodada incremental de 30/10/2026.
#
# Pendências implementadas (auditoria incremental 30/10, contra HEAD 39dae63):
#
#  1. Paulo Henrique — sequência de janeiro/2025 (Metrópoles 09/10/2026):
#     +13 mensagens literais (20, 23 e 26/01/2025 — encontro em Zurique, jantar,
#     captação/DII, pós-jantar e preocupação com divulgação). Cadeia declarada:
#     relatório da PF encaminhado ao STF em 28/09/2026, sigilo derrubado em 09/10,
#     mensagens extraídas dos celulares apreendidos na Operação Compliance Zero —
#     DISTINTA do relatório parcial de 28/10/2026 (catalogado à parte). "Léo"
#     permanece sem identificação; encaminhamento de Lauro Jardim não vira
#     mensagem; proposta de compra de DII registrada como possibilidade, nunca
#     aquisição; defesa de Ibaneis preservada (nota de Kakay).
#  2. Paulo Henrique — outubro/2024 (Metrópoles 09/10): a matéria NÃO publica
#     mensagens literais completas dessa seção (apenas fragmentos em fala
#     indireta) → evento editorial de contexto (e-00010), sem registros literais.
#  3. Eventos editoriais: depoimento de Vorcaro à PF de 15/10 (e-00011, peça não
#     localizada individualmente — cobertura Congresso em Foco 30/10); perícia
#     particular da defesa sobre a cadeia de custódia do celular (e-00012,
#     Agência Brasil 29/10 — atribuição explícita à defesa, limitações
#     reconhecidas, nenhuma reclassificação automática); relatório parcial da PF
#     de 28/10 e indiciamentos (e-00013).
#  4. Documento: Relatório Parcial de Investigação Criminal — INQ 5026/STF,
#     28/10/2026, 703 p. Cópia pública (Poder360) BAIXADA E CONFERIDA nesta
#     rodada: SHA-256 idêntico ao da ficha do Novelo Master (4ce55e40…) e nº de
#     páginas confirmado. Cadastrada como public_reproduction (link-only, §2.3).
#  5. Flávio Carneiro — 4 mensagens de abril-maio/2024 (ICL 03/09): os dois
#     trechos longos ("Babaquice isso…" e nota do Grupo Voto) entram como
#     verbatim_excerpt CONFORME PUBLICADOS NO TEXTO (com corte do veículo),
#     documentando que a captura publicada exibe a primeira sob o cabeçalho
#     "27 de abril de 2024, 18h33" e resolve a divergência "das/as consequencias"
#     registrada em 29/10 (a captura mostra "as"); o miolo completo não é
#     reproduzido. Mais as duas mensagens de 04/05/2024 ("Nikolas tirou aquele
#     post…"; "Falei, tirou e ficou na categoria amigo"). Nível secondary_source
#     (ICL sem cadeia de origem declarada — critério da rodada de 29/10).
#  6. felipe-mourao m-00057: nota documenta a conferência feita na cópia local
#     do IPJ-A 1020625/2026 — o colchete "[Luis Felipe]" CONSTA da transcrição
#     oficial (fl. 45, fig. 53); literal_brackets mantido, transcrição inalterada.
#
# NÃO implementado (evidência insuficiente — documentado no relatório):
#  - "Fio do bigode" (Estado do Pará Online 30/10): trechos lidos no depoimento
#    de 15/10 sem acesso à gravação/transcrição documental da oitiva e sem data
#    individual das mensagens.
#  - Lilian Tahan m-00025 × resposta completa do Estadão: correspondência
#    indeterminável (mantida a decisão de 29/10).
#  - PET 16704: peça individual do grupo "Master" segue por localizar (pacote
#    público existe; peça não individualizada).
#
# AGENTS.md (documentação do E_TIMESTAMP_ORDER) e scripts/build-whatsnew.mjs
# (CURRENT_BATCHES) são ajustados à parte, fora deste script.

import json

BATCH = "ingest-press12-20261030"
URL_MET = "https://www.metropoles.com/colunas/manoela-alcantara/master-pf-aponta-interferencia-direta-de-ibaneis-na-conducao-do-brb"
URL_ICL = "https://iclnoticias.com.br/nikolas-voos-vorcaro-mensagens-master/"
URL_CF = "https://www.congressoemfoco.com.br/amp/noticia/129683/caso-master-brb-veja-a-integra-do-depoimento-de-daniel-vorcaro-a-pf"
URL_AB = "https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/defesa-diz-que-arquivos-do-celular-de-vorcaro-foram-modificados"

SEC_MET = [{"publication": "Metrópoles — coluna Manoela Alcântara", "date": "2026-10-09", "url": URL_MET}]
SEC_ICL = [{"publication": "ICL Notícias", "date": "2026-09-03", "url": URL_ICL}]
PROC_MET = ("PF — Operação Compliance Zero; relatório encaminhado ao STF em 28/09/2026 com sigilo "
            "derrubado em 09/10/2026, obtido pela coluna (Metrópoles, 09/10/2026); mensagens extraídas "
            "dos celulares apreendidos de Vorcaro e Paulo Henrique; a peça não é publicada "
            "integralmente e é DISTINTA do relatório parcial de 28/10/2026")


def load(rel):
    with open(rel, encoding="utf-8") as fh:
        return json.load(fh)


def save(rel, obj):
    with open(rel, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


def ver(level, proceeding=None, verified="2026-10-30"):
    v = {"level": level, "origin": "press report", "authority": "Polícia Federal" if level == "public_investigation" else None,
         "court": None, "case": None, "document": None, "page": None, "figure": None,
         "official_url": None, "primary_document_located": False, "verified_at": verified}
    if proceeding:
        v["proceeding"] = proceeding
    return v


def msg(mid, sender, content, note, date, precision, time=None, kind="verbatim_excerpt", lb=None, sec=SEC_MET):
    m = {"id": mid, "date": date, "time": time, "timestamp_precision": precision,
         "sender_id": sender, "content_kind": kind, "content": content,
         "editorial_note": note,
         "verification": ver("public_investigation", PROC_MET),
         "sources": {"primary": None, "secondary": [dict(s) for s in sec]},
         "source_ref": "Mensagem divulgada por Metrópoles — coluna Manoela Alcântara (2026-10-09)",
         "added_in": BATCH}
    if lb:
        m["literal_brackets"] = lb
    return m


def event(eid, date, precision, content, source_ref, level="secondary_source", sec=None, proceeding=None):
    return {"id": eid, "date": date, "time": None, "timestamp_precision": precision,
            "content": content, "event_kind": "editorial_context",
            "verification": ver(level, proceeding),
            "sources": {"primary": None, "secondary": [dict(s) for s in (sec or [])]},
            "source_ref": source_ref, "added_in": BATCH}


# ================================================================ Paulo Henrique
path = "data/threads/paulo-henrique-daniel-vorcaro.json"
t = load(path)

jan = [
    msg("m-00061", "paulo-henrique",
        "Amigo, quando vc vem a Zurique? O Governador pediu para marcarmos uma reunião",
        "Pedido de agendamento do encontro em Zurique; a reportagem não associa a solicitação a um ato "
        "comprovado do governador — é o relato de Paulo Henrique em mensagem.", "2025-01-20", "date"),
    msg("m-00062", "paulo-henrique",
        "Como está seu jantar na quinta?",
        "Na sequência do agendamento, conforme a reportagem.", "2025-01-20", "date"),
    msg("m-00063", "daniel-vorcaro",
        "Kronenhalle 20h30",
        "Indicação do restaurante e horário, com símbolo de confirmação descrito pela reportagem (o "
        "símbolo não é texto e não foi reproduzido); a reportagem relata ainda que Paulo Henrique "
        "informou que o jantar teria quatro participantes — fala indireta, sem transcrição.", "2025-01-23", "date"),
    msg("m-00064", "paulo-henrique",
        "Excelente! Marcado, meu amigo",
        "Confirmação do compromisso, em resposta à indicação de restaurante e horário.", "2025-01-23", "date"),
    msg("m-00065", "paulo-henrique",
        "Vou na frente com o Governador e o Léo para esse e te esperamos lá",
        "Enviada com link de restaurante encaminhado (não reproduzido). “Léo” permanece sem identificação "
        "nos registros — a reportagem não o identifica; a presença efetiva dos citados não é comprovada "
        "pela mensagem.", "2025-01-23", "date"),
    msg("m-00066", "paulo-henrique",
        "Vamos no seu restaurante",
        "Na mesma sequência do jantar.", "2025-01-23", "date"),
    msg("m-00067", "paulo-henrique",
        "Estamos com mais demanda de captação do que lastro. Talvez tenhamos uma oportunidade de comprar de DII do Master. Pedi para procurarem seu tesoureiro",
        "Possibilidade de operação entre BRB e Master registrada como PROPOSTA (“talvez tenhamos uma "
        "oportunidade”) — não como aquisição ou operação concluída; a reportagem não explica o termo "
        "“DII” e atribui a tratativa a uma nova operação entre os bancos. Grafia conforme publicada.", "2025-01-23", "date"),
    msg("m-00068", "paulo-henrique",
        "Já estou querendo dizer nosso tesoureiro",
        "Na mesma sequência da tratativa de captação; grafia conforme publicada.", "2025-01-23", "date"),
    msg("m-00069", "paulo-henrique",
        "Espero que tenha gostado do jantar",
        "Comentário posterior ao jantar.", "2025-01-23", "date"),
    msg("m-00070", "daniel-vorcaro",
        "Gostei muito",
        "Resposta ao comentário sobre o jantar.", "2025-01-23", "date"),
    msg("m-00071", "paulo-henrique",
        "De onde veio isso?",
        "Após Vorcaro encaminhar mensagem do jornalista Lauro Jardim (encaminhamento não reproduzido "
        "como mensagem própria — jornalista não é parte da conversa).", "2025-01-26", "date"),
    msg("m-00072", "paulo-henrique",
        "Não ampliamos em nada o escopo das pessoas envolvidas no deal",
        "Sobre o sigilo das tratativas, na troca motivada pela divulgação jornalística.", "2025-01-26", "date"),
    msg("m-00073", "paulo-henrique",
        "Voltei na sexta da Suíça e não sei se o Governador ou Léo estiveram com alguém",
        "Preocupação com a origem da informação divulgada; “Léo” sem identificação; o relato não comprova "
        "contato de quem quer que seja.", "2025-01-26", "date"),
]

idx46 = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00046")
for j, m in enumerate(jan):
    t["messages"].insert(idx46 + j, m)

t.setdefault("timeline_events", []).extend([
    event("e-00010", "2024-10", "month",
          "Contexto de outubro/2024 (Metrópoles, 09/10/2026, a partir de relatório da PF encaminhado ao STF "
          "em 28/09/2026): nas trocas próximas à autorização do aumento de capital do BRB (R$ 750 milhões, "
          "proporção 40/60), Paulo Henrique enfatiza a necessidade de “dar sinais ao mercado”; ao tratar com "
          "Vorcaro da reestruturação do Master e da entrada de novos sócios, apresenta o objetivo de preparar, "
          "em três meses, “a história toda que vamos contar” da consolidação e do novo banco, e relata: “ontem, "
          "na conversa com o governador, abordamos isso”, apresentando os novos sócios como algo que ajudaria "
          "ambos os bancos. Para a PF, isso evidenciaria ciência e validação política da estratégia antes dos "
          "atos formais — interpretação investigativa, não fato judicialmente comprovado. A matéria não publica "
          "mensagens literais completas desta seção (fragmentos em fala indireta). Contraditório: a defesa de "
          "Ibaneis Rocha (nota do advogado Antônio Carlos de Almeida Castro, Kakay) afirma que o então "
          "governador “não pressionou e tampouco teve qualquer ingerência nas operações realizadas pelo BRB”, "
          "que o contato “se deu em contexto natural, institucional e republicano” e que ele “não é interlocutor "
          "direto em nenhuma mensagem com Daniel Vorcaro” — por isso não há conversa própria de Ibaneis.",
          "Relato de Metrópoles — coluna Manoela Alcântara (2026-10-09)",
          level="public_investigation", sec=SEC_MET, proceeding=PROC_MET),
    event("e-00011", "2026-10-15", "date",
          "Depoimento de Daniel Vorcaro à Polícia Federal (15/10/2026), tornado público e encaminhado ao STF "
          "em 29/10: negou fraude nas operações com o BRB e pediu arquivamento do inquérito; sustentou que as "
          "operações questionadas foram desfeitas ou trocadas por outros ativos, sem prejuízo ao banco; "
          "classificou os apartamentos oferecidos a Paulo Henrique como moradia prevista para o executivo "
          "caso assumisse função de direção no grupo resultante da união das instituições — sem vantagem "
          "indevida e sem ocupação dos imóveis; negou ter dificultado fiscalização do Banco Central "
          "(centralizava comunicações para evitar erros, segundo ele) e questionou os valores de prejuízo "
          "apontados. A PF contestou: aponta negociação de carteiras avaliadas em R$ 12,2 bilhões sem "
          "comprovação de existência e sustenta que a substituição posterior de ativos não afasta a apuração. "
          "Trata-se de declaração do investigado em oitiva — não de mensagens de aplicativo; trechos de "
          "mensagens exibidos na oitiva (“acordos no fio do bigode”) aguardam transcrição documental "
          "acessível para eventual registro. Peça do depoimento não localizada individualmente; cobertura: "
          "Congresso em Foco (30/10/2026) e Estado do Pará Online (30/10/2026).",
          "Congresso em Foco (2026-10-30)",
          sec=[{"publication": "Congresso em Foco", "date": "2026-10-30", "url": URL_CF}]),
    event("e-00013", "2026-10-28", "date",
          "Relatório Parcial de Investigação Criminal da PF no INQ 5026/STF (28/10/2026): 15 indiciados — "
          "entre eles Daniel Vorcaro e Paulo Henrique — por gestão fraudulenta de instituição financeira, "
          "organização criminosa e lavagem de dinheiro, com pedido de prorrogação do inquérito por 60 dias. "
          "Indiciamento é ato policial: não é denúncia nem condenação. Cópia pública da peça (Poder360, 703 "
          "páginas, SHA-256 conferido localmente nesta rodada) catalogada em data/documents.json; o relatório "
          "é parcial e registra divergência de valores entre laudos, sem individualização completa de "
          "condutas. Comunicado oficial: PF/gov.br (28/10/2026).",
          "Comunicado da PF (2026-10-28)",
          sec=[{"publication": "Polícia Federal (gov.br) — comunicado", "date": "2026-10-28",
                "url": "https://www.gov.br/pf/pt-br/assuntos/noticias/2026/10/pf-apresenta-primeiros-indiciamentos-da-operacao-compliance-zero-em-relatorio-parcial-ao-stf"}]),
    event("e-00012", "2026-10-29", "date",
          "Cadeia de custódia — controvérsia: a defesa de Vorcaro apresentou ao STF perícia particular "
          "alegando que 657 arquivos do celular apreendido (17/11/2025) foram modificados e 436 criados "
          "após a apreensão, pedindo acesso aos dados originais. O próprio pedido reconhece que registros "
          "de modificação, isoladamente, não demonstram intervenção humana — evidenciam apenas alteração "
          "de estado do arquivo sob custódia estatal — e a defesa admite não ser possível avaliar o alcance "
          "das alterações. Nenhuma adulteração de mensagens específicas do acervo foi demonstrada; sem "
          "resposta pública da PF ou decisão do STF localizadas até esta rodada. As proveniências "
          "registradas não são rebaixadas por esta controvérsia (Agência Brasil, 29/10/2026).",
          "Agência Brasil (2026-10-29)",
          sec=[{"publication": "Agência Brasil", "date": "2026-10-29", "url": URL_AB}]),
])
save(path, t)
print(f"[paulo-henrique] {len(t['messages'])} mensagens (+13 jan/2025), +4 eventos")

# ================================================================ Flávio Carneiro
path = "data/threads/flavio-carneiro-daniel-vorcaro.json"
t = load(path)

def icl_msg(mid, sender, content, note, date, precision, time=None, lb=None):
    m = {"id": mid, "date": date, "time": time, "timestamp_precision": precision,
         "sender_id": sender, "content_kind": "verbatim_excerpt", "content": content,
         "editorial_note": note,
         "verification": ver("secondary_source"),
         "sources": {"primary": None, "secondary": [dict(s) for s in SEC_ICL]},
         "source_ref": "Mensagem divulgada por ICL Notícias (2026-09-03)",
         "added_in": BATCH}
    if lb:
        m["literal_brackets"] = lb
    return m

car = [
    icl_msg("m-00035", "flavio-carneiro",
            "Babaquice isso. Se não parar isso vai virar pauta de discussão no congresso mesmo. Eles estão usando isso para atacar os caras […]", None,  # note abaixo
            None, None),
    icl_msg("m-00036", "flavio-carneiro",
            "Acho que isso mata o tema do ponto de vista de transparência e de demanda. Além de todos veículos cobrirem os eventos dela […]",
            None, None, None),
    icl_msg("m-00037", "flavio-carneiro",
            "Nikolas tirou aquele post. Ele realmente não tr (sic) conectou no tema e não é ele mesmo que posta nada",
            None, None, None),
    icl_msg("m-00038", "flavio-carneiro",
            "Falei, tirou e ficou na categoria amigo",
            None, None, None),
]
car[0]["editorial_note"] = (
    "Reação às críticas ao evento jurídico de Londres, na sequência das postagens de Nikolas (abril/2024). "
    "Trecho conforme publicado pelo ICL (03/09/2026), com corte do próprio veículo (reticências), mantido "
    "como […]. A captura publicada exibe a mensagem sob o cabeçalho “27 de abril de 2024, 18h33” (data e "
    "hora acrescentadas a partir dela) e a continuação “sem medir as consequencias” — a divergência "
    "“das/as consequencias” registrada na auditoria de 29/10 fica resolvida pela captura (“as”, grafia do "
    "original); o miolo completo da mensagem não é reproduzido.")
car[0]["date"] = "2024-04-27"
car[0]["time"] = "18:33"
car[0]["timestamp_precision"] = "minute"
car[0]["literal_brackets"] = True
car[1]["editorial_note"] = (
    "Sobre a nota pública do Grupo Voto divulgada na sequência das críticas ao evento de Londres: o trecho "
    "citado pelo ICL (“Acho que isso mata o tema…”) e o contexto (cobertura dos eventos por outros veículos; "
    "“confraria”) conforme publicados, com corte do veículo mantido como […]. A captura publicada mostra "
    "mensagem associada iniciada por “Estamos voltando com tudo. O Voto divulgou nota oficial…”, não "
    "integralmente publicada no texto; data não divulgada individualmente — mês de abril/2024.")
car[1]["date"] = "2024-04"
car[1]["timestamp_precision"] = "month"
car[1]["literal_brackets"] = True
car[2]["editorial_note"] = (
    "Sobre a retirada da postagem de Nikolas; “(sic)” é marcação do veículo. O ICL situa a troca em 4 de "
    "maio de 2024; a retirada efetiva é relatada por Carneiro — declaração em mensagem, não verificação "
    "própria.")
car[2]["date"] = "2024-05-04"
car[2]["timestamp_precision"] = "date"
car[3]["editorial_note"] = (
    "Confirmando a conversa com o deputado sobre a retirada da postagem; “ficou na categoria amigo” é "
    "descrição de Carneiro, não verificação de relacionamento. Mesma troca situada em 4 de maio de 2024.")
car[3]["date"] = "2024-05-04"
car[3]["timestamp_precision"] = "date"

idx24 = next(i for i, m in enumerate(t["messages"]) if m["id"] == "m-00024")
for j, m in enumerate(car):
    t["messages"].insert(idx24 + j, m)
save(path, t)
print(f"[flavio-carneiro] {len(t['messages'])} mensagens (+4 abr-mai/2024)")

# ================================================================ felipe-mourao m-00057
path = "data/threads/felipe-mourao-daniel-vorcaro.json"
t = load(path)
m = next(x for x in t["messages"] if x["id"] == "m-00057")
m["editorial_note"] = (m.get("editorial_note") or "").rstrip() + (
    " [Conferido 2026-10-30: o colchete “[Luis Felipe]” CONSTA da transcrição oficial da PF na fl. 45, "
    "fig. 53 do IPJ-A 1020625/2026 — verificado diretamente na cópia do documento no repositório "
    "(pdf_pf/); “Luis Felipe” é inserção do próprio relatório policial dentro da citação. "
    "literal_brackets mantido; transcrição inalterada.]")
save(path, t)
print("[felipe-mourao] m-00057: nota de conferência acrescentada")

# ================================================================ documents.json
path = "data/documents.json"
docs = load(path)
docs.append({
    "id": "pf-relatorio-parcial-inq5026-2026",
    "title": "Relatório Parcial de Investigação Criminal — INQ 5026/STF (indiciamentos)",
    "authority": "Polícia Federal",
    "unit": "DELEINQUE/DRPJ/SR/PF/DF",
    "date": "2026-10-28",
    "court": "STF",
    "case": "INQ 5026",
    "reporting_judge": None,
    "pages": 703,
    "edoc": None,
    "edoc_case": None,
    "official_process_url": "https://portal.stf.jus.br/processos/detalhe.asp?incidente=7473347",
    "public_copy_url": "https://static.poder360.com.br/uploads/2026/10/Inq-5026-do-Indiciamento-Daniel-Vorcaro-e-Paulo-Henrique-Costa-BRB-Master-28-out-2026.pdf",
    "copy_kind": "public_reproduction",
    "copy_note": ("Cópia pública disponibilizada pelo Poder360 (veículo de imprensa). Ficha documental do "
                  "Novelo Master (fausel.adv.br) descreve a reprodução com 703 páginas; nesta rodada "
                  "(30/10/2026) o arquivo foi baixado e conferido localmente: SHA-256 idêntico ao informado "
                  "pela ficha, 703 páginas confirmadas e primeira página identificando “RELATÓRIO PARCIAL DE "
                  "INVESTIGAÇÃO CRIMINAL — INQ n. 5026/STF” (DELEINQUE/DRPJ/SR/PF/DF). NÃO é o arquivo "
                  "original assinado do tribunal; o projeto não redistribui peças dos autos (decisão "
                  "link-only, plano de risco §2.3). DISTINTO do relatório encaminhado ao STF em 28/09/2026 "
                  "citado pelo Metrópoles (09/10) — não presumir sobreposição de conteúdo."),
    "public_access_verified": True,
    "public_access_date": "2026-10-30",
    "public_access_basis": ("Cópia pública da peça divulgada pelo Poder360 (28-29/10/2026): URL ativa, hash "
                            "e número de páginas conferidos localmente em 30/10/2026; comunicado oficial da "
                            "PF (gov.br, 28/10/2026) confirma a entrega do relatório parcial ao STF, os 15 "
                            "indiciamentos e o pedido de prorrogação por 60 dias. Publicidade formal dos "
                            "autos (decisão publicada de desembargo de sigilo) não localizada — a verificação "
                            "vale para a reprodução jornalística, não para o byte-stream original do tribunal."),
    "sha256": "4ce55e4037d0b4f61e886d767576640e63b2b91f8dcb80d361c4a20894f1ac9e",
    "bytes": 10107175,
    "local_copy": None,
    "hosted_copy_url": None,
    "hash_note": ("SHA-256 da cópia pública externa (Poder360), calculado localmente em 30/10/2026; idêntico "
                  "ao informado pela ficha do Novelo Master."),
})
save(path, docs)
print(f"[documents] +1 (pf-relatorio-parcial-inq5026-2026) — total {len(docs)}")

# ================================================================ threads.json
path = "data/threads.json"
idx = load(path)
for tid, count in (("paulo-henrique-daniel-vorcaro", 73), ("flavio-carneiro-daniel-vorcaro", 38)):
    e = next(x for x in idx if x["id"] == tid)
    e["message_count"] = count
save(path, idx)
print("[threads.json] contagens atualizadas (paulo-henrique=73, flavio-carneiro=38)")

# ================================================================ sanidade
for f in ("paulo-henrique-daniel-vorcaro", "flavio-carneiro-daniel-vorcaro"):
    t = load(f"data/threads/{f}.json")
    for key in ("messages", "timeline_events"):
        lst = t.get(key) or []
        ids = [r["id"] for r in lst]
        assert len(ids) == len(set(ids)), f"{f}/{key}: IDs duplicados"
        for r1, r2 in zip(lst, lst[1:]):
            ordered = lambda r: r.get("timestamp_precision") in ("minute", "date")
            if not (ordered(r1) and ordered(r2)):
                continue
            if r1["date"] != r2["date"]:
                assert r1["date"] < r2["date"], f"{f}/{key}: {r1['id']}>{r2['id']}"
            elif r1.get("time") and r2.get("time"):
                assert r1["time"] <= r2["time"], f"{f}/{key}: {r1['id']}/{r1['time']}>{r2['id']}/{r2['time']}"
print("[sanidade] IDs únicos e ordem OK")
