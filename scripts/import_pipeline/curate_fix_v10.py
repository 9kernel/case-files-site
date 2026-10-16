# curate_fix_v10.py — auditoria Tahan/Matos/Barros + proveniência (UOL/AE 15-10, PF 09-10)
"""Rodada de auditoria do editor:

1. AUTORIA (m-00001..03 da lilian-tahan): o trio 'Tá caro esse Metrópoles' /
   'Coisa mais importante...' / 'Dei ok pra Lilian' migra para a conversa com
   ANA MATOS — atribuição conferida pelo editor nas capturas da reportagem
   (o texto corrido do UOL é ambíguo: chama a interlocutora de 'a diretora';
   a coerência interna — quem paga diz 'tá caro' e o 'dei ok PRA Lilian' —
   sustenta a diretora de marketing, não a própria Tahan). A pergunta do
   pagamento ('20 mi no CNPJ banco ou divido com Kovr e Will?') sai do evento
   e vira mensagem DE Ana Matos, conforme a tabela do editor.
2. lilian-tahan +Série D (AE 26/06 e 02/07/2025) e +Estadão (20/08/2025):
   só literais; intenção de 'entrar com criminal' registrada como intenção
   manifestada, nunca como fato judicial; sister citada só no contexto
   jornalístico do evento (minimização).
3. lilian-tahan: +2 literais de ago/2025 reconstituídas na relitura do
   artigo principal ('Tiraria a última frase'; 'Vamos publicar, ok??') e
   evento do 'racha no Bacen'. Capturas de 29/11 e 11/12/2024: sem transcrição
   acessível no texto — PENDÊNCIA declarada (não se infere trecho não legível).
4. Thread NOVA guilherme-barros (1 literal de mai/2024, confirmada na
   releitura; sem respostas inventadas).
5. Flávio Carneiro / 'Foone 2': a reportagem traz a solução em fala indireta,
   SEM remetente identificável — mantida como evento (já existente); nada
   publicado como mensagem.
6. augusto-lima: nota oficial da PF (09/10/2026) registrada como contestação
   documental (documento oficial de página única); áudio da reportagem
   explicitado como de autenticidade não estabelecida.
7. PROVENIÊNCIA: registros public_investigation ganham verification.proceeding
   quando o artigo-base amarra o material à PF/STF (verificado na leitura
   integral de cada reportagem nas rodadas v3-v9); grupos puramente
   jornalísticos, sem procedimento público identificável no que foi lido,
   são rebaixados para secondary_source. Listas explícitas abaixo.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "audit-fix2-20261016"
T = REPO / "data" / "threads"

UOL_METRO = ("UOL (Renata Agostini e Tiago Dantas)", "2026-10-15",
             "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/vorcaro-editava-textos-do-site-metropoles-antes-de-irem-ao-ar.htm")
AE_SERIE_D = ("UOL — Estadão Conteúdo", "2026-10-15",
              "https://noticias.uol.com.br/ultimas-noticias/agencia-estado/2026/10/15/dialogos-mostram-como-ceo-do-metropoles-negociou-patrocinio-de-vorcaro-a-transmissao-da-serie-d.htm")
AE_ESTADAO = ("UOL — Estadão Conteúdo", "2026-10-15",
              "https://noticias.uol.com.br/ultimas-noticias/agencia-estado/2026/10/15/vorcaro-ameacou-reporter-do-estadao-por-revelar-crimes-do-master-entrar-com-criminal.htm")
PF_NOTA_URL = "https://www.gov.br/pf/pt-br/assuntos/noticias/2026/10/nota-a-imprensa-1/"

# procedimento público verificável por grupo de fonte (URL) — leitura integral v3-v9
PROCEEDING_GERAL = "Operação Compliance Zero — PF/STF (material do celular de Vorcaro, reportado pela imprensta)"  # noqa: typo guard
PROCEEDING_GERAL = "Operação Compliance Zero — PF/STF (material do celular de Vorcaro, reportado pela imprensa)"
PROCEEDING_GA = "Decisão do Min. André Mendonça (STF) que autorizou a prisão de Paulo Henrique, citada pela reportagem"
VERIFIED = {
    "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/13/vorcaro-era-socio-oculto-de-agencia-de-prostituicao-e-recrutou-refugiadas.ghtm": PROCEEDING_GERAL,
    "https://www.metropoles.com/colunas/grande-angular/veja-troca-de-mensagens-entre-vorcaro-e-paulo-henrique": PROCEEDING_GA,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/brazil-journal-istoe-como-vorcaro-montou-rede-de-influencia-em-sites.htm": PROCEEDING_GERAL,
    "https://veja.abril.com.br/brasil/em-audio-operador-de-propinas-do-planalto-diz-que-iria-colocar-vorcaro-na-boca-do-gol-no-bb": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/grupo-globo-demite-diretor-geral-apos-vazamento-de-conversas-com-vorcaro.htm": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/colunas/fabio-serapiao/2026/10/02/vorcaro-apoiou-ida-de-motta-a-presidencia-da-camara-e-ofereceu-aviao-e-casa.htm": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/15/vorcaro-pagou-parte-de-imovel-de-r-73-mi-para-presidente-da-febraban.ghtm": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/vorcaro-editava-textos-do-site-metropoles-antes-de-irem-ao-ar.htm": PROCEEDING_GERAL,
    "https://revistaoeste.com/politica/vorcaro-mantinha-conversas-com-acm-neto-por-mensagens": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/09/30/mensagens-senador-do-psd-da-bahia-trocava-mensagens-com-vorcaro.htm": PROCEEDING_GERAL,
    "https://veja.abril.com.br/politica/vorcaro-conta-que-liberou-dinheiro-para-filme-sobre-lula-por-negocios-no-governo": PROCEEDING_GERAL,
    "https://www.metro1.com.br/noticias/politica/189165": PROCEEDING_GERAL,
    "https://www1.folha.uol.com.br/poder/2026/09/vorcaro-teve-jantar-restrito-com-padilha-antes-de-encontro-com-lula-em-2024-indicam-mensagens.shtml": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/01/mensagens-vorcaro-antonio-rueda": PROCEEDING_GERAL,
    "https://www.cnnbrasil.com.br/blogs/matheus-teixeira/politica/mensagens-apontam-relacao-de": PROCEEDING_GERAL,
    "https://www.cartacapital.com.br/justica/mensagens-indicam-encontro-entre-vorcaro-e-andre-m": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/colunas/cezar-feitoza/2026/09/30/grupo-de-zap-para-organizar-e": PROCEEDING_GERAL,
    "https://www.metropoles.com/brasil/evita-falar-nome-ate-o-meu-alertou-vorcaro-a-chef-de-almoco-para-moraes": PROCEEDING_GERAL,
    "https://www.metropoles.com/colunas/igor-gadelha/caviar-e-trufa-almoco-de-moraes-foi-articulado-por-fabio-faria-com-vorcaro": PROCEEDING_GERAL,
    "https://www.cnnbrasil.com.br/politica/dialogos-de-vorcaro-citam-suposta-mesada-de-r-500-mil-para-filho-de-nunes": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/08/vorcaro-tentou-chegar-a-lula-e-moraes-para-proteger-o-master.ghtm": PROCEEDING_GERAL,
    "https://noticias.uol.com.br/colunas/cezar-feitoza/2026/10/12/master-entrou-em-lista-para-captar-fundos-publicos-apos-acao-de-acm-e-lupi.htm": PROCEEDING_GERAL,
    "https://www.poder360.com.br/poder-gente/leia-as-mensagens-entre-luciano-huck-e-daniel-vorcaro": PROCEEDING_GERAL,
    "https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/": PROCEEDING_GERAL,
    "https://www1.folha.uol.com.br/colunas/monicabergamo/2026/09/dialogos-de-vorcaro-citam-filho-de-kassio-nunes-marques-e-pagamento-de-r-500-mil.shtml": PROCEEDING_GERAL,
    "https://g1.globo.com/politica/noticia/2026/03/05/vorcaro-sugere-em-mensagem-que-encontro-com-lula-foi-otimo.ghtml": PROCEEDING_GERAL,
    "https://timesbrasil.com.br/brasil/vorcaro-recebeu-alexandre-padilha-em-jantar-e-dois-dias-depois-disse-a-mares-guia-que-precisava-muito-ver-o-lula": PROCEEDING_GERAL,
    "https://veja.abril.com.br/brasil/o-que-diz-daniel-vorcaro-sobre-pagamento-de-propina-ao-ministro-alexandre-padilha": PROCEEDING_GERAL,
}
# grupos puramente jornalísticos lidos: sem procedimento público identificável
# no material efetivamente publicado — rebaixados para secondary_source
DOWNGRADE_PREFIXES = (
    "https://noticias.uol.com.br/ultimas-noticias/agencia-estado/2026/10/15/dialogos-mostram-como-ceo-do-metropoles",  # Série D
    "https://noticias.uol.com.br/ultimas-noticias/agencia-estado/2026/10/15/vorcaro-ameacou-reporter",  # Estadão/repórter
    "https://www.cnnbrasil.com.br/blogs/gustavo-uribe/politica/em-mensagem-doria-se-diz-preocup",  # Dória
    "https://g1.globo.com/politica/noticia/2026/09/04/nikolas-e-vorcaro-ouca-audio",  # Nikolas (áudio próprio, não PF)
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/09/15/dialogos-de-vorcaro-que-c",  # Marcus Vinicius
    "https://c-level.folha.uol.com.br/financas/2026/10/mensagens-mostram-que-campos-neto-convid",  # Campos Neto
    "https://www1.folha.uol.com.br/poder/2026/10/vorcaro-financiou-startup-de-filha-de-otto-alencar",  # Isadora/Sodré
    "https://jornalgrandebahia.com.br/2026/09/deputado-hugo-motta-e-daniel-vorcaro-trocaram-202",  # espelho, origem não lida
    "https://www1.folha.uol.com.br/poder/2026/09/mensagens-de-motta-com-vorcaro-citam-sociedade",  # Folha Motta: origem não registrada
    "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/14/escritorio-de-temer",  # O Globo via UOL: origem não registrada
    "https://www.metropoles.com/brasil/vorcaro-disse-ter-acionado-presidente-do-pt",  # Fatos On-line: origem não registrada
    "https://jovempan.com.br/politica/tapete-vermelho-irmao-filho-de-fux-trocou-mensagens",  # Fux: origem não registrada
    "https://jovempan.com.br/colunistas/bruno-pinheiro/so-decepcao-em-conversa-com-ex-socio-vor",  # JP desabafo
)


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date):
    return "month" if date and len(date) == 7 else ("date" if date else None)


def secs(src):
    return [{"publication": p, "date": d, "url": u} for p, d, u in (src if isinstance(src, list) else [src])]


def ver(level="public_investigation"):
    v = {"level": level, "origin": "press report", "authority": "Polícia Federal" if level == "public_investigation" else None,
         "court": None, "case": None, "document": None, "page": None, "figure": None,
         "official_url": None, "primary_document_located": False, "verified_at": "2026-10-16"}
    if level == "public_investigation":
        v["proceeding"] = PROCEEDING_GERAL
    return v


def new_msg(date, time, sender, content, note, src, level="public_investigation"):
    prec = "minute" if time else prec_of(date)
    ss = secs(src)
    m = {
        "id": "m-TEMP", "date": date,
        "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": ver(level),
        "sources": {"primary": None, "secondary": ss},
        "source_ref": f"Mensagem divulgada por {ss[0]['publication']} ({ss[0]['date']})",
        "added_in": ADDED_IN,
    }
    if date:
        m["time"] = time
        m["timestamp_precision"] = prec
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    return m


def new_event(date, content, src, level="public_investigation"):
    e = {
        "id": "e-TEMP", "date": date,
        "content": content, "event_kind": "editorial_context",
        "verification": ver(level),
        "sources": {"primary": None, "secondary": secs(src)},
        "source_ref": f"Relato de {secs(src)[0]['publication']} ({secs(src)[0]['date']})",
        "added_in": ADDED_IN,
    }
    if date:
        e["time"] = None
        e["timestamp_precision"] = prec_of(date)
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
    # ---------- 1) autoria: trio migra para Ana Matos + pergunta vira mensagem ----------
    t = load("lilian-tahan")
    ana = load("ana-matos")
    trio = {"Tá caro esse Metrópoles", "Coisa mais importante [da] nossa vida é esse Metrópoles", "Dei ok pra Lilian"}
    moved = []
    for m in list(t["messages"]):
        if m["content"] in trio:
            m["editorial_note"] = ((m.get("editorial_note") or "").rstrip()
                                   + " Atribuição conferida pelo editor nas capturas da reportagem: a troca é com a "
                                     "diretora de marketing Ana Matos (o texto corrido do UOL a chama apenas de 'a diretora'; "
                                     "é ela quem processa o pagamento — daí o 'tá caro' e o 'dei ok pra Lilian').")
            moved.append(m)
            t["messages"].remove(m)
    have_ana = {norm(m["content"]) for m in ana["messages"]}
    for m in moved:
        if norm(m["content"]) not in have_ana:
            m["sender_id"] = "ana-matos" if m["content"].startswith("Tá caro") else "daniel-vorcaro"
            ana["messages"].append(m)
    # pergunta do pagamento: sai do evento e vira mensagem de Ana Matos
    pergunta = "O valor que fechamos com o Metrópoles (20 mi) eu faço todo no CNPJ banco ou divido com Kovr e Will?"
    if norm(pergunta) not in {norm(m["content"]) for m in ana["messages"]}:
        ana["messages"].append(new_msg(
            None, None, "ana-matos", pergunta,
            "Sobre o contrato de R$ 20 milhões; atribuição a Ana Matos conforme a tabela do editor (a reportagem a "
            "identifica como 'funcionária'/'diretora de marketing').", UOL_METRO))
    for e in t.get("timeline_events", []):
        if "O valor que fechamos com o Metrópoles" in e["content"]:
            e["content"] = ("Pagamentos do grupo ao Metrópoles: R$ 1 milhão (junho/2024), R$ 900 mil para 'educação "
                            "financeira' da Kovr e do Will (julho/2024) e contrato de R$ 20 milhões (novembro/2024), "
                            "quitado em 2025 em parcelas de R$ 5 milhões. O processamento do pagamento consta na "
                            "conversa com Ana Matos (diretora de marketing).")

    # ---------- 2/3) lilian-tahan: Série D, Estadão e complementos de ago/2025 ----------
    adds = [
        # Série D (AE — sem procedimento público identificável no texto: secondary_source)
        ("2025-06-26", None, "lilian-tahan",
         "A transmissão profissional destas disputas era um desejo antigo da CBF. Como temos uma excelente relação com eles, acabamos acolhendo a missão",
         "Apresentação da proposta de patrocínio à transmissão da Série D; o trecho citado pela reportagem continua, sem reprodução integral.", AE_SERIE_D, "secondary_source"),
        ("2025-06-26", None, "lilian-tahan",
         "...iniciando um projeto que, embora tenha um investimento grande de tempo e de recursos, abrirá uma nova frente de conteúdo esportivo",
         "Fragmento (a citação começa no meio da frase, conforme a reportagem).", AE_SERIE_D, "secondary_source"),
        ("2025-06-26", None, "daniel-vorcaro", "Pode contar comigo sempre", None, AE_SERIE_D, "secondary_source"),
        ("2025-07-02", None, "lilian-tahan", "Vamos seguir?! Posso procurar alguém do seu time para tratar?! ",
         None, AE_SERIE_D, "secondary_source"),
        ("2025-07-02", None, "daniel-vorcaro", "Pode falar com a ana!",
         "Encaminhando à equipe; 'a ana' é identificada, sem sobrenome, na reportagem.", AE_SERIE_D, "secondary_source"),
        # Estadão 20/08/2025 (secondary_source)
        ("2025-08-20", "08:24", "lilian-tahan", "Então, muito ruim a manchete do Estadão.",
         "Pela manhã; acrescentou ter pedido para verificarem 'como será a repercussão na parte da manhã'.", AE_ESTADAO, "secondary_source"),
        ("2025-08-20", None, "daniel-vorcaro", "Vamos entrar com criminal. Nao existe processo. Nao existe nada.",
         "Intenção manifestada na conversa — não há ação judicial comprovada na reportagem.", AE_ESTADAO, "secondary_source"),
        ("2025-08-20", None, "daniel-vorcaro", "Colocar que tem ligação com minha irma porque o escritorio contabilidade que a empresa usa é o mesmo.",
         "Reação a reportagem do Estadão sobre aportes a empresas ligadas à irmã do banqueiro; a irmã é citada apenas no contexto jornalístico (evento abaixo).", AE_ESTADAO, "secondary_source"),
        ("2025-08-20", None, "daniel-vorcaro", "Essas coisas nao da pra deixar mais", None, AE_ESTADAO, "secondary_source"),
        ("2025-08-20", None, "lilian-tahan", "Não tem nada mais chato para o repórter que responder criminal",
         "Sobre o impacto de ações criminais para jornalistas.", AE_ESTADAO, "secondary_source"),
        # relitura do artigo principal — ago/2025
        ("2025-08", None, "lilian-tahan", "Vamos publicar, ok??",
         "Sobre o perfil de Renato Gomes, após os pedidos de edição de Vorcaro.", UOL_METRO, "public_investigation"),
        ("2025-08", None, "daniel-vorcaro", "Tiraria a última frase",
         "Sobre texto do dia seguinte, a respeito de projeto de lei que permitiria ao Congresso demitir diretores do Banco Central.", UOL_METRO, "public_investigation"),
    ]
    have = {norm(m["content"]) for m in t["messages"]}
    added = 0
    for date, time, sender, content, note, src, level in adds:
        if norm(content) in have:
            continue
        t["messages"].append(new_msg(date, time, sender, content.strip(), note, src, level))
        added += 1
    t.setdefault("timeline_events", []).extend([
        new_event(None, "Contexto do dia 20/08/2025: o Estadão publicou reportagens apontando suspeita da CVM de R$ 2,1 bilhões em investimentos fraudulentos do Master (inflando seu valor antes da venda de 58% ao BRB) e R$ 1,2 bilhão em aportes a empresas ligadas à irmã de Vorcaro. Procurada, Lilian Tahan não respondeu ao Estadão, que mantém espaço aberto.", AE_ESTADAO, "secondary_source"),
        new_event(None, "Série D: acordo Metrópoles–CBF anunciado em 2-3/07/2025; primeiras transmissões (11ª rodada, 15 jogos) em 5-6/07, gratuitas no YouTube. Segundo o Estadão, o Master pagou R$ 838,8 mil ao Metrópoles no 2º semestre de 2024 — antes de o patrocínio ser proposto — e R$ 27 milhões no total entre 2024 e 2025. O Coaf classificou os pagamentos como suspeitos, apontando débito imediato do Metrópoles a empresas da família de Luiz Estevão. A CBF informou que não se manifestará; Estevão justificou os valores como patrocínio do Will Bank à transmissão e venda dos naming rights.", AE_SERIE_D, "secondary_source"),
        new_event(None, "Na sequência do perfil de Renato Gomes, Vorcaro sugeriu ainda mencionar um 'racha no Bacen' com o diretor contrário ao banco e especulações de que, após o mandato, estaria 'de malas prontas pra um dos bancões' — trechos citados em fala indireta pela reportagem.", UOL_METRO),
    ])
    finalize(t)
    save("lilian-tahan", t)
    finalize(ana)
    save("ana-matos", ana)
    print(f"[v10] lilian-tahan: -{len(moved)} movidas, +{added} msgs (total {len(t['messages'])})")
    print(f"[v10] ana-matos: +{len(moved) + 1} (total {len(ana['messages'])})")

    # ---------- 4) guilherme-barros ----------
    gb_msg = new_msg(None, None, "guilherme-barros",
                     "A Lilian gostou muito de vc. Foi muito bom ter te colocado com o Luis Estevão. Eu tenho o contato dele, mas acho melhor ela mesma fazer essa ponte, concorda?",
                     "No dia seguinte ao encontro com Lilian Tahan, em maio/2024, quando então consultor de Vorcaro; única mensagem divulgada — respostas de Vorcaro não foram publicadas.",
                     UOL_METRO)
    thread = {
        "id": "guilherme-barros-daniel-vorcaro",
        "title": "Guilherme Barros",
        "participants_ids": ["daniel-vorcaro", "guilherme-barros"],
        "source": {"document": "UOL (Renata Agostini e Tiago Dantas), 15/10/2026: mensagem de Guilherme Barros, então "
                               "consultor de Vorcaro, relatando a apresentação a Lilian Tahan e sugerindo o contato com "
                               "Luiz Estevão. Apenas esta mensagem foi divulgada; nenhuma resposta de Vorcaro foi publicada.",
                   "url": UOL_METRO[2],
                   "pages": "Mensagens conforme transcrição da reportagem; nada além do que foi divulgado é inferido."},
        "messages": [gb_msg],
        "timeline_events": [],
    }
    finalize(thread)
    save("guilherme-barros", thread)
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    if not any(x["id"] == "guilherme-barros" for x in people):
        people.append({"id": "guilherme-barros", "name": "Guilherme Barros", "photo": None,
                       "role": "Consultor; então assessor de Vorcaro",
                       "aliases": [],
                       "summary": ("Consultor de Vorcaro em 2024; apresentou o banqueiro a Lilian Tahan e sugeriu o contato "
                                   "com Luiz Estevão, conforme mensagem publicada pelo UOL (15/10/2026). Perfil resumido "
                                   "exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão "
                                   "sobre responsabilidade individual.")})
        pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v10] guilherme-barros: thread nova (1 msg)")

    # ---------- 6) augusto-lima: nota oficial da PF ----------
    t = load("augusto-lima")
    for e in t.get("timeline_events", []):
        if "Em áudio citado pela reportagem" in e["content"]:
            e["content"] = e["content"].replace(
                "Em áudio citado pela reportagem, Vorcaro diz:",
                "Em áudio citado pela reportagem — gravação de autenticidade não estabelecida —, Vorcaro diz:")
    t["timeline_events"].append({
        "id": "e-TEMP", "date": "2026-10-09", "time": None, "timestamp_precision": "date",
        "content": ("Nota oficial da Polícia Federal (09/10/2026): Daniel Vorcaro 'não prestou depoimento com o teor relatado "
                    "na matéria' da Veja nem entregou 'anexos, documentos ou informações com o conteúdo ali descrito'. As "
                    "propostas de colaboração da defesa 'não foram acolhidas em razão do não atendimento aos requisitos "
                    "legais', em decisão fundamentada conhecida da defesa. A PF registrou ainda ter recebido notícia-crime "
                    "sobre fatos relacionados à publicação e tê-la encaminhado à área técnica. A nota não menciona gravações "
                    "nem sua autenticidade. Fonte oficial: gov.br/pf (link em verification.official_url)."),
        "event_kind": "editorial_context",
        "verification": {"level": "official_document", "origin": "official statement", "authority": "Polícia Federal",
                         "court": None, "case": None, "document": "Nota à imprensa PF — 09/10/2026", "page": 1, "figure": None,
                         "official_url": PF_NOTA_URL, "primary_document_located": True, "verified_at": "2026-10-16"},
        "sources": {"primary": {"type": "official_statement", "document": "Nota à imprensa PF — 09/10/2026", "url": PF_NOTA_URL},
                    "secondary": [{"publication": "Polícia Federal (nota oficial)", "date": "2026-10-09", "url": PF_NOTA_URL}]},
        "source_ref": "Nota oficial da Polícia Federal (2026-10-09)",
        "added_in": ADDED_IN,
    })
    finalize(t)
    save("augusto-lima", t)
    print("[v10] augusto-lima: nota da PF registrada como contestação documental")

    # ---------- 7) varredura de proveniência ----------
    stat = {"proceeding": 0, "downgraded": 0, "mantidos": 0}
    for f in sorted(T.glob("*.json")):
        t = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for r in t["messages"] + (t.get("timeline_events") or []):
            v = r.get("verification")
            if not v or v.get("level") != "public_investigation":
                continue
            url = ((r.get("sources") or {}).get("secondary") or [{}])[0].get("url") or ""
            has_doc = v.get("case") or v.get("document") or v.get("official_url") or (r.get("source") or {}).get("document_id")
            if any(url.startswith(p) for p in DOWNGRADE_PREFIXES):
                v["level"] = "secondary_source"
                v["authority"] = None
                v.pop("proceeding", None)
                r["editorial_note"] = ((r.get("editorial_note") or "").rstrip()
                                       + " [Proveniência revisada 2026-10: reportagem sem procedimento público identificável — nível secondary_source.]")
                stat["downgraded"] += 1
                changed = True
            elif not has_doc:
                proc = VERIFIED.get(url)
                if proc:
                    v["proceeding"] = proc
                    stat["proceeding"] += 1
                    changed = True
                else:
                    stat["mantidos"] += 1
        if changed:
            f.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v10] proveniência: {stat}")

    # ---------- índice ----------
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    have_t = {e["id"] for e in index}
    if "guilherme-barros-daniel-vorcaro" not in have_t:
        index.append({
            "id": "guilherme-barros-daniel-vorcaro", "title": "Guilherme Barros",
            "participants_ids": ["daniel-vorcaro", "guilherme-barros"],
            "message_count": 1,
            "last_message_preview": "A Lilian gostou muito de vc. Foi muito bom ter te colocado com o Luis Estevão. Eu te",
            "featured": False,
            "note": "UOL (Renata Agostini e Tiago Dantas), 15/10/2026: mensagem do então consultor de Vorcaro relatando a",
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
    print(f"[v10] índice: {len(index)} conversas")


if __name__ == "__main__":
    main()
