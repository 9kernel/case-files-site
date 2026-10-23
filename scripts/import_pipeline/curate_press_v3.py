# curate_press_v3.py — 7 conversas com fontes públicas (imprensa, out/2026)
"""Rodada 2026-10: interlocutores ausentes, material de reportagens que
reproduzem mensagens da extração da PF (nível public_investigation, mesmo
padrão do precedente thiago-miranda: sources.primary null + secondary=[veículo]).

Regras aplicadas:
- só entra como MENSAGEM o que a reportagem cita literalmente entre aspas;
  o que ela apenas relata vira evento editorial (never paraphrase as literal);
- colchetes do original ([sic], [de], …) marcados com literal_brackets;
- datas/horas só quando a reportagem informa (month → precision month);
- os 3 interlocutores em revisão jurídica NÃO são publicados: ficam como
  rascunhos locais em data/review/legal-review-drafts/ (gitignored).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press-20261015"

# (publication, date, url)
VEJA = ("Veja", "2026-10-10",
        "https://veja.abril.com.br/brasil/em-audio-operador-de-propinas-do-planalto-diz-que-iria-colocar-vorcaro-na-boca-do-gol-no-bb")
FOLHA_MARTHA = ("Folha de S.Paulo", "2026-03-05",
        "https://www1.folha.uol.com.br/mercado/2026/03/mensagens-de-vorcaro-mostram-transito-entre-stf-congresso-governo-e-empresarios.shtml")
UOL_MASC = ("UOL — coluna Cezar Feitoza", "2026-10-12",
        "https://noticias.uol.com.br/colunas/cezar-feitoza/2026/10/12/master-entrou-em-lista-para-captar-fundos-publicos-apos-acao-de-acm-e-lupi.htm")
VESPEIRO = ("Vespeiro (resenha da reportagem do UOL)", "2026-10-12",
        "https://vespeiro.com/2026/10/12/ex-ministro-de-lula-carlos-lupi-ajudou-vorcaro-com-fundos-previdenciarios")
FOLHA_BA = ("Folha de S.Paulo", "2026-10-09",
        "https://www1.folha.uol.com.br/poder/2026/10/vorcaro-financiou-startup-de-filha-de-otto-alencar-e-negociou-obras-de-arte-com-aliado-de-jaques-wagner.shtml")
JP_AUGUSTO = ("Jovem Pan — coluna Bruno Pinheiro", "2026-09-25",
        "https://jovempan.com.br/colunistas/bruno-pinheiro/so-decepcao-em-conversa-com-ex-socio-vorcaro-desabafou-sobre-amizades")

THREADS = {
  "julio-cezar": {
    "title": "Júlio Cezar",
    "src_note": "Veja (coluna Radar), 10/10/2026 — Robson Bonin e Hugo Marques: mais de 450 mensagens e 180 telefonemas entre Vorcaro e Júlio Cezar, consultor de Goiânia apontado pela reportagem como operador do grupo do ministro Alexandre Padilha junto a fundos de pensão. Meta relatada de captar R$ 10 bilhões em fundos (Petros, Previ, Postalis, Funcef) com 10% de propina. Padilha, Olavo Noleto, Augusto Lima e Lula negam as acusações.",
    "secs": [VEJA],
    "msgs": [
      ("2024-03-01", None, "julio-cezar", "Daniel, já estou aqui no palácio", "Enviada às 14h10 de 1º/3/2024, segundo a reportagem.", "14:10"),
      ("2024-03-04", None, "julio-cezar", "Estou no café ao lado. Aguardando você", "Encontro no Planalto, segundo a reportagem.", None),
      ("2024-03-04", None, "daniel-vorcaro", "Estou quase chegando. Preciso falar antes com você", "Resposta na mesma sequência, segundo a reportagem.", None),
      ("2024-04", None, "daniel-vorcaro", "O e-mail que pediram Petros", "Sequência de 8/4/2024, segundo a reportagem.", None),
      ("2024-04", None, "julio-cezar", "Já repassei. Agora é o amigo com dever dele. Ontem estive com ele", None, None),
      ("2024-04", None, "daniel-vorcaro", "O da Petros já foi? Cobrando?", None, None),
      ("2024-04", None, "julio-cezar", "Vou te manter informado. Já sim", None, None),
      (None, None, "daniel-vorcaro", "Vamos pressionar pra boletar (…) Postalis evoluiu?", None, None),
      (None, None, "julio-cezar", "Evoluiu. Mandando e-mail também. Do BB essa semana resolve. Semana que vem reunião lá.", None, None),
      (None, None, "julio-cezar", "Amanhã ele vai travar a agenda do dia 2 de abril na parte da tarde só pra você!!!", "Sobre o Postalis, segundo a reportagem.", None),
      ("2024-05", None, "julio-cezar", "Daniel, o Henrique (Jäger) aqui, com o presidente (da Petros), tá numa reunião do conselho lá.", "Trecho de áudio transcrito pela reportagem.", None),
      ("2024-05", None, "julio-cezar", "qualquer coisinha, já estando ok, já ponho você na boca do gol", "Sobre o Banco do Brasil, em áudio transcrito pela reportagem; dá título à matéria.", None),
      ("2024-10", None, "julio-cezar", "Pediram cinco dias úteis pra liberar minha conta, te passo na hora que liberar!! Quero ir pro jantar tranquilo", "Contexto da cobrança de R$ 500 mil relatada pela reportagem.", None),
      ("2024-10", None, "daniel-vorcaro", "Quero ver agora você virar uma boleta de verdade", None, None),
      ("2024-10", None, "julio-cezar", "Pode deixar. É empenho de vida, Daniel, isso", None, None),
      ("2024-10", None, "julio-cezar", "Padilha e Olavo amanhã, às 22 horas, um jantar contigo em bsb (sic)… Vai 5 pessoas", "Véspera do segundo jantar em Brasília (23/10/2024), segundo a reportagem.", None),
      ("2024-10-24", None, "julio-cezar", "Daniel, liga pro Olavo… O Pr vai te receber…", None, None),
      ("2024-10-24", None, "julio-cezar", "já conversaram com PR e ele gostou da conversa!", None, None),
      ("2024-10-24", None, "julio-cezar", "não esquece do Olavo. Ele vai te passar informações.", None, None),
      ("2025-06", None, "daniel-vorcaro", "Estamos já há mais de 12 meses tentando uma boleta (…)", None, None),
      ("2025-06", None, "daniel-vorcaro", "Falhou de novo o negócio?", None, None),
      ("2025-08", None, "daniel-vorcaro", "Se não entrar nada até final da semana que vem, eu gostaria que você encerrasse o trabalho.", None, None),
      ("2025-08", None, "julio-cezar", "Concordo!", None, None),
      ("2025-08", None, "daniel-vorcaro", "Sexta que vem — não entrando — vida que segue.", None, None),
      ("2025-11", None, "julio-cezar", "Tenho uma estruturação para comprar suas 'LFs' (…) Consigo capitalizar através de fundos que tenho aqui", "Última mensagem do diálogo; Vorcaro não respondeu, segundo a reportagem.", None),
    ],
    "events": [
      ("2024-03-01", "Primeira reunião de Vorcaro com o ministro Alexandre Padilha no Planalto, com Olavo Noleto e Júlio Cezar, segundo a Veja; Padilha teria dito que tratar com Olavo era como tratar com ele (alegação negada pela defesa).", VEJA),
      ("2024-04-29", "O Master entra na 'lista exaustiva' de instituições autorizadas a receber recursos de fundos de pensão e, no mesmo dia, Vorcaro paga R$ 500 mil de adiantamento a Júlio Cezar, segundo a reportagem.", VEJA),
      (None, "A PF contabilizou mais de 450 mensagens e 180 telefonemas entre os dois, segundo a Veja; a meta relatada era captar R$ 10 bilhões em fundos de pensão de estatais, com 10% de propina. Acusados negam.", VEJA),
    ],
  },
  "martha-graeff": {
    "title": "Martha Graeff",
    "src_note": "Folha de S.Paulo, 05/03/2026: mensagens da quebra de sigilo da PF (autorizada pelo ministro André Mendonça) enviadas à CPI do INSS; conversas de 2024 a agosto de 2025 com a então companheira de Vorcaro relatando encontros com autoridades dos três Poderes e negociações patrimoniais.",
    "secs": [FOLHA_MARTHA],
    "msgs": [
      ("2024-05", None, "daniel-vorcaro", "Quero te apresentar. Um dos meus grandes amigos de vida", "Sobre Ciro Nogueira (PP), segundo a reportagem.", None),
      ("2024-08", None, "daniel-vorcaro", "Ciro soltou um projeto de lei agora que é uma bomba atômica no mercado financeiro!", "Sobre o projeto que elevava o FGC de R$ 250 mil para R$ 1 milhão ('emenda Master'), depois engavetado.", None),
      ("2024-08", None, "daniel-vorcaro", "Ajuda os bancos médios e diminui poder dos grandes! Está todo mundo louco", None, None),
      ("2025-02", None, "daniel-vorcaro", "Tô num jantar na residência oficial com Hugo [Motta…] e seis empresários", "Jantar na residência oficial da Câmara, com o então presidente Hugo Motta.", None),
      ("2025-03", None, "martha-graeff", "Me manda mensagem quando acabar aí. Você está com gente aí? Ou está me ignorando de propósito?", None, None),
      ("2025-03", None, "daniel-vorcaro", "Estou sim, acabou chegando Hugo e Ciro aqui pra falarem com Alexandre...", None, None),
      ("2025-04-19", None, "daniel-vorcaro", "Indo encontrar Alexandre [de] Moraes aqui perto de casa", None, None),
      ("2025-04-19", None, "martha-graeff", "Como assim amor. Ele está em Campos???? Ou foi pra te ver?", None, None),
      ("2025-04-19", None, "daniel-vorcaro", "Ele tá passando feriado", None, None),
      ("2025-04-29", None, "martha-graeff", "quem era o primeiro cara [?]", None, None),
      ("2025-04-29", None, "daniel-vorcaro", "Alexandre [de] Moraes", None, None),
      ("2025-04-29", None, "martha-graeff", "Morri. Ele gostou da casa amor!?? Tá muito mais astral", None, None),
      ("2025-04-29", None, "daniel-vorcaro", "Sin [sic]. Falou que é [sic] bem melhor. E ele adorava apto [apartamento]", None, None),
      ("2025-08", None, "daniel-vorcaro", "Foi bom", "Sobre encontro na residência oficial do Senado, segundo a reportagem.", None),
      ("2025-08", None, "daniel-vorcaro", "Terça teremos outra", None, None),
    ],
    "events": [
      (None, "As mensagens integram quebra de sigilo telefônico autorizada pelo ministro André Mendonça (20/2) e enviada pela PF à CPI do INSS; cobrem 2024 a agosto de 2025.", FOLHA_MARTHA),
      ("2024-08", "Ciro Nogueira apresenta o projeto apelidado de 'emenda Master' (elevação do teto do FGC), posteriormente engavetado, segundo a reportagem.", FOLHA_MARTHA),
      ("2025-04", "Vorcaro relata a Martha encontros com o ministro Alexandre de Moraes em Campos (RJ), incluindo visita à sua residência; o STF não comentou, segundo a reportagem.", FOLHA_MARTHA),
    ],
  },
  "fernando-mascarenhas": {
    "title": "Fernando Mascarenhas",
    "src_note": "UOL (coluna Cezar Feitoza, 12/10/2026), resenhado pelo Vespeiro: mensagens entre Vorcaro e Fernando Mascarenhas, então diretor comercial do Master, sobre a inclusão do banco na lista de instituições aptas a receber recursos de RPPS — articulação que, segundo a reportagem, envolveu ACM Neto e o então ministro Carlos Lupi. O ministério afirmou que a decisão foi técnica.",
    "secs": [UOL_MASC, VESPEIRO],
    "msgs": [
      ("2024-04-23", None, "fernando-mascarenhas", "Estamos sendo atacados de verdade! Precisamos contestar isso, eles não têm alçada para fazer isso", None, None),
      (None, None, "daniel-vorcaro", "Não interessa o Bacen pra nós agora. Você precisa levar a ata da assembleia em que o banco já elegeu.", "Orientação para contestar a exclusão da lista, segundo a reportagem.", None),
      ("2024-05-02", None, "fernando-mascarenhas", "A conclusão é de que o Banco Master cumpriu todos os requisitos e será incluído na lista exaustiva", "Após reunião com o então ministro Carlos Lupi, segundo a reportagem.", None),
      (None, None, "daniel-vorcaro", "Show", "Resposta à mensagem anterior.", None),
    ],
    "events": [
      ("2024-05", "O Master é reincluído na lista de instituições autorizadas a captar recursos de RPPS cerca de dez dias após a exclusão — único banco incluído na atualização, condicionado a comitê de auditoria, segundo a reportagem.", UOL_MASC),
      (None, "Antes da inclusão, o Master já havia recebido R$ 490 milhões de fundos previdenciários, e a articulação envolveu ACM Neto (reunião em 25/4/2024) e o então ministro Carlos Lupi (reunião em 2/5/2024), segundo a reportagem.", UOL_MASC),
    ],
  },
  "isadora-alencar": {
    "title": "Isadora Alencar",
    "src_note": "Folha de S.Paulo, 09/10/2026: mensagens sobre o investimento na startup Ecoari, de Isadora Alencar (filha do senador Otto Alencar, PSD-BA). Ela afirma que foi um empréstimo regular e que a compra do Master não se concretizou; Otto Alencar nega ter conversado com Vorcaro. A B3 alertou o Coaf três vezes sobre ativos da Ecoari no Master.",
    "secs": [FOLHA_BA],
    "msgs": [
      ("2024-09", None, "isadora-alencar", "Deu tudo certo com a abertura da conta! Ainda não assinamos o contrato, mas permaneço à disposição...", "Reticências constam da transcrição da reportagem.", None),
      ("2024-09", None, "isadora-alencar", "Assinamos o contrato e o banco já fez o repasse do valor! Gostaria de agradecer muito pela confiança e parceria...", None, None),
      ("2024-09", None, "daniel-vorcaro", "que bacana!", "Comentário às notícias da contratação, segundo a reportagem.", None),
      ("2025-09", None, "isadora-alencar", "Gostaria de agradecer pela presença ontem, de verdade! Também agradeço muito pela delicadeza nos presentes!...", None, None),
      ("2025-09", None, "daniel-vorcaro", "Fiquei muito feliz de estar com vocês! ... Família querida! Que seja um ciclo maravilhoso para você", None, None),
    ],
    "events": [
      ("2024-09", "Contrato assinado e repasse do investimento na Ecoari, que mantinha os recursos no Master; a chegada de Isadora teria sido por indicação de 'Ciro' (provável advogado Ciro Soares), segundo a reportagem.", FOLHA_BA),
      ("2024-10", "A B3 alertou o Coaf três vezes: ativos da Ecoari no Master incompatíveis com o porte da empresa — mais de R$ 9 milhões (out/nov 2024) e R$ 2,8 milhões (set 2025).", FOLHA_BA),
    ],
  },
  "guilherme-sodre": {
    "title": "Guilherme Sodré (Guiga)",
    "src_note": "Folha de S.Paulo, 09/10/2026: mensagens sobre negociação de obras de arte e encaminhamento do contato do senador Jaques Wagner (PT-BA), de quem Guiga é aliado (pai de Eduardo Sodré, secretário de Meio Ambiente da Bahia). A defesa de Wagner nega relação com Vorcaro.",
    "secs": [FOLHA_BA],
    "msgs": [
      ("2024-07", None, "daniel-vorcaro", "Maravilhosas!", "Sobre as obras apresentadas por Guiga (Guignard e Portinari).", None),
      ("2024-07", None, "guilherme-sodre", "Ao vivo são ainda mais lindas", None, None),
    ],
    "events": [
      ("2024-07", "Guiga envia informações sobre obras como 'Ouro Preto' (Guignard) e 'Casamento na Roça' (Portinari) em negociação com Vorcaro.", FOLHA_BA),
      ("2024-08", "Após telefonema de 2 minutos, Guiga encaminha a Vorcaro o telefone do senador Jaques Wagner e lhe deseja sorte, segundo a reportagem.", FOLHA_BA),
    ],
  },
  "hamilton-buzelin": {
    "title": "Hamilton Buzelin",
    "src_note": "Veja (coluna Radar), 10/10/2026: ex-diretor de Finanças Corporativas do Banco Máxima; aproximou Vorcaro de Júlio Cezar após reunião cancelada na Petros (fev/2024) e agendou o encontro no Planalto. As mensagens abaixo são transcrições da própria reportagem.",
    "secs": [VEJA],
    "msgs": [
      ("2024-02", None, "hamilton-buzelin", "Estou com uma demanda de falar com você com uma certa urgência (…) preciso que seja pessoalmente", "Reticências constam da transcrição da reportagem.", None),
      ("2024-02", None, "hamilton-buzelin", "o Júlio já vai indo para o palácio e vai te esperar lá", "Trecho de áudio transcrito pela reportagem, que registra confusão entre Alvorada e Planalto.", None),
    ],
    "events": [
      ("2024-02-28", "Encontro entre Buzelin e Vorcaro em São Paulo, após o qual ele aproximou Vorcaro de Júlio Cezar, segundo a reportagem.", VEJA),
    ],
  },
  "augusto-lima": {
    "title": "Augusto Lima",
    "src_note": "Jovem Pan (coluna Bruno Pinheiro), 25/09/2026: mensagens de 29/1/2025 com o ex-sócio e ex-diretor do Master (que comandava a originação de consignado e depois presidiu o Voiter/Pleno). A própria reportagem anota que o desabafo não permite ligá-lo a nenhum político ou autoridade específica; à PF, Vorcaro negou relação entre amizades e os fatos investigados.",
    "secs": [JP_AUGUSTO],
    "msgs": [
      ("2025-01-29", None, "daniel-vorcaro", "Na minha vida só sobrou você mesmo", None, None),
      ("2025-01-29", None, "daniel-vorcaro", "Só decepção", "Resumo do desabafo; disse não querer 'saber de mais ninguém', segundo a reportagem.", None),
      ("2025-01-29", None, "augusto-lima", "Não é quanto, é com quem", None, None),
      ("2025-01-29", None, "augusto-lima", "Vamos vencer", "Encerrou prometendo que estariam 'sempre juntos' e com 'te amo', segundo a reportagem.", None),
    ],
    "events": [
      (None, "Augusto Lima foi sócio e diretor do Master (crédito consignado) e depois presidiu o Banco Voiter, renomeado Pleno, segundo a reportagem; as mensagens integram material reunido pela PF.", JP_AUGUSTO),
    ],
  },
}

PARTICIPANTS_NEW = [
    {"id": "julio-cezar", "name": "Júlio Cezar", "photo": None,
     "role": "Consultor apontado pela Veja como operador do grupo de Padilha junto a fundos de pensão",
     "aliases": ["Júlio"],
     "summary": "Consultor de Goiânia. Segundo a Veja (10/10/2026), trocou mais de 450 mensagens e 180 telefonemas com Vorcaro buscando captação de R$ 10 bilhões em fundos de pensão, com propina de 10%. Negativas dos acusados na própria reportagem. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual."},
    {"id": "martha-graeff", "name": "Martha Graeff", "photo": None,
     "role": "Blogueira; então companheira de Daniel Vorcaro",
     "aliases": [],
     "summary": "Destinatária dos relatos de Vorcaro sobre encontros com autoridades dos três Poderes, nas mensagens da quebra de sigilo enviadas à CPI do INSS e reportadas pela Folha (05/03/2026). Perfil resumido exclusivamente a partir das reportagens linkadas."},
    {"id": "fernando-mascarenhas", "name": "Fernando Mascarenhas", "photo": None,
     "role": "Então diretor comercial do Banco Master",
     "aliases": [],
     "summary": "Interlocutor de Vorcaro no episódio de inclusão do Master na lista de instituições aptas a captar recursos de RPPS (maio/2024), conforme UOL (12/10/2026). Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual."},
    {"id": "isadora-alencar", "name": "Isadora Alencar", "photo": None,
     "role": "Empreendedora; filha do senador Otto Alencar (PSD-BA)",
     "aliases": [],
     "summary": "Sócia da startup Ecoari, que recebeu investimento de Vorcaro e mantinha recursos no Master, conforme a Folha (09/10/2026). Ela afirma que foi um empréstimo regular e que a compra do Master não se concretizou. Perfil resumido exclusivamente a partir das reportagens linkadas."},
    {"id": "guilherme-sodre", "name": "Guilherme Sodré (Guiga)", "photo": None,
     "role": "Aliado do senador Jaques Wagner (PT-BA); pai de Eduardo Sodré",
     "aliases": ["Guiga"],
     "summary": "Negociou obras de arte com Vorcaro e encaminhou o contato de Jaques Wagner, conforme a Folha (09/10/2026). A defesa de Wagner nega relação com Vorcaro. Perfil resumido exclusivamente a partir das reportagens linkadas."},
    {"id": "hamilton-buzelin", "name": "Hamilton Buzelin", "photo": None,
     "role": "Ex-diretor de Finanças Corporativas do Banco Máxima",
     "aliases": [],
     "summary": "Aproximou Vorcaro de Júlio Cezar e agendou encontro no Planalto, conforme a Veja (10/10/2026). Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual."},
    {"id": "augusto-lima", "name": "Augusto Lima", "photo": None,
     "role": "Ex-sócio e ex-diretor do Banco Master; depois presidente do Banco Voiter/Pleno",
     "aliases": [],
     "summary": "Comandava a originação de crédito consignado no Master, segundo relato de Vorcaro à PF reportado pela Jovem Pan (25/09/2026). Perfil resumido exclusivamente a partir das reportagens linkadas."},
]

UOL_LEGAL = ("UOL — coluna Natália Portinari", "2026-10-13",
             "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/13/vorcaro-era-socio-oculto-de-agencia-de-prostituicao-e-recrutou-refugiadas.htm")

# rascunhos sob revisão jurídica — NÃO publicar (ficam em data/review/, gitignored)
LEGAL_DRAFTS = {
    "diogo-batista": "Promotor de eventos; mensagens sobre organização e financiamento dos eventos investigados pela PF por possível exploração sexual (UOL, 13/10/2026).",
    "leonardo-serrano": "Mensagens sobre logística, contratos e pagamentos relacionados aos eventos investigados (UOL, 13/10/2026).",
    "tiago-polo": "Tratativas sobre a agência Allure e organização dos eventos (UOL, 13/10/2026).",
}


def prec_of(date, time):
    if time: return "minute"
    if not date: return None
    return "month" if len(date) == 7 else "date"


def msg_obj(seq, date, time, sender, content, note):
    prec = prec_of(date, time)
    m = {
        "id": f"m-{seq:05d}",
        "date": date, "time": time,
        "timestamp_precision": prec,
        "sender_id": sender,
        "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": {
            "level": "public_investigation", "origin": "press report",
            "authority": "Polícia Federal", "court": None, "case": None,
            "document": None, "page": None, "figure": None,
            "official_url": None, "primary_document_located": False,
            "verified_at": "2026-10-15",
        },
        "sources": {"primary": None, "secondary": None},  # preenchido por thread
        "source_ref": None,
        "added_in": ADDED_IN,
    }
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    if prec is None:
        m.pop("timestamp_precision"); m.pop("time")
    return m


def main():
    for pid, spec in THREADS.items():
        secs = [{"publication": p, "date": d, "url": u} for p, d, u in spec["secs"]]
        msgs = []
        ordered = sorted(spec["msgs"], key=lambda x: (x[0] or "9999-99", x[1] or "~"))
        for i, (date, _t, sender, content, note, time) in enumerate(ordered, 1):
            m = msg_obj(i, date, time, sender, content, note)
            m["sources"]["secondary"] = secs
            pub0 = secs[0]["publication"]
            m["source_ref"] = f"Mensagem divulgada por {pub0} ({secs[0]['date']})"
            msgs.append(m)
        events = []
        for i, (date, content, sec) in enumerate(spec["events"], 1):
            e = {
                "id": f"e-{i:05d}", "date": date, "time": None,
                "timestamp_precision": prec_of(date, None),
                "content": content, "event_kind": "editorial_context",
                "verification": msgs[0]["verification"],
                "sources": {"primary": None,
                            "secondary": [{"publication": sec[0], "date": sec[1], "url": sec[2]}]},
                "source_ref": f"Relato de {sec[0]} ({sec[1]})",
                "added_in": ADDED_IN,
            }
            if date is None:
                e.pop("time"); e.pop("timestamp_precision")
            elif e["timestamp_precision"] is None:
                e.pop("timestamp_precision")
            events.append(e)
        thread = {
            "id": f"{pid}-daniel-vorcaro",
            "title": spec["title"],
            "participants_ids": ["daniel-vorcaro", pid],
            "source": {"document": spec["src_note"], "url": spec["secs"][0][2],
                       "pages": "Mensagens conforme transcrição da(s) reportagem(ns) indicada(s) em cada registro; nada além do que foi divulgado é inferido."},
            "messages": msgs,
            "timeline_events": events,
        }
        out = REPO / "data" / "threads" / f"{pid}-daniel-vorcaro.json"
        out.write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        dated = sum(1 for m in msgs if m.get("date"))
        print(f"[press] {thread['id']}: {len(msgs)} mensagens ({dated} com data), {len(events)} eventos")

    # participantes
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    have = {p["id"] for p in people}
    for np in PARTICIPANTS_NEW:
        if np["id"] not in have:
            people.append(np)
            print(f"[press] +participante {np['id']}")
    pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # índice
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    have_t = {t["id"] for t in index}
    for pid, spec in THREADS.items():
        tid = f"{pid}-daniel-vorcaro"
        if tid in have_t:
            continue
        th = json.loads((REPO / "data" / "threads" / f"{tid}.json").read_text(encoding="utf-8"))
        index.append({
            "id": tid, "title": spec["title"],
            "participants_ids": ["daniel-vorcaro", pid],
            "message_count": len(th["messages"]),
            "last_message_preview": th["messages"][-1]["content"][:80],
            "featured": False,
            "note": spec["src_note"][:200],
        })
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # rascunhos jurídicos (locais, gitignored)
    drafts_dir = REPO / "data" / "review" / "legal-review-drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "note": "Interlocutores classificados pelo editor como 'revisão jurídica' — conteúdo sensível (investigação por exploração sexual). NÃO publicar sem go jurídico. Enquanto isso, permanecem fora de data/threads e do índice público.",
        "blocked_until": "revisão jurídica do editor",
        "source": {"publication": UOL_LEGAL[0], "date": UOL_LEGAL[1], "url": UOL_LEGAL[2]},
        "drafts": LEGAL_DRAFTS,
    }
    (drafts_dir / "README.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    for pid, desc in LEGAL_DRAFTS.items():
        (drafts_dir / f"{pid}.md").write_text(
            f"# Rascunho: {pid} × Vorcaro (REVISÃO JURÍDICA PENDENTE)\n\n{desc}\n\n"
            f"Fonte: {UOL_LEGAL[0]}, {UOL_LEGAL[1]} — {UOL_LEGAL[2]}\n\n"
            "Status: NÃO publicado. Para publicar após go jurídico: extrair citações literais da reportagem,\n"
            "criar data/threads/{pid}-daniel-vorcaro.json (nível public_investigation, secondary=[UOL]),\n"
            "adicionar participante e entrada em data/threads.json, rodar validate + build-search-index + build-network.\n",
            encoding="utf-8")
    print(f"[press] {len(LEGAL_DRAFTS)} rascunhos jurídicos em data/review/legal-review-drafts/ (locais)")


if __name__ == "__main__":
    main()
