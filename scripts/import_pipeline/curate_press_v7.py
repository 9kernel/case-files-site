# curate_press_v7.py — rodada da tabela de prioridades (Folha/Metrópoles/Veja, set-out/2026)
"""Itens da tabela do editor:

1. walfrido-mares-guia — NOVA (Folha 30/09, espelho Times Brasil; 1 literal
   adicional na Veja 09/10): Biomm, Anvisa, jantar Padilha/Noleto, Lula.
2. jose-maria-meira — NOVA (Metrópoles 30/09): orientações de Vorcaro ao chef
   do almoço de Moraes em Campos do Jordão (30/12/2023).
3. augusto-lima — COMPLEMENTAR (Veja 09/10): diálogo da 'lista exaustiva'
   (29/04/2024) + alegações de Vorcaro na delação rejeitada, com defesas.
4. fabio-faria — COMPLEMENTAR (coluna Igor Gadelha/Metrópoles 30/09):
   articulação do almoço de 30/12/2023.
5. julio-cezar — COMPLEMENTAR (mesma Veja 09/10): +9 literais (Petros/BB,
   pressão por adiantamento, frustração de 2025) + defesas.
6. geraldo CONSOLIDAÇÃO: o contato 'Geraldo Brazil Journal' dos autos da PF
   (IPJ-A 3298613, PET 16662) é o mesmo Geraldo Samor — mesmo episódio Blair
   já documentado na thread dele pela apuração do UOL. A mensagem oficial
   migra para a thread geraldo-samor mantendo a proveniência (documento,
   página, figura); participante e thread antigos são removidos.
7. alberto-felix — verificado: pp. 155-157 do IPJ-A trazem apenas a narrativa
   do relatório (mensagens estão em screenshots, sem transcrição no texto);
   pela regra §6 (OCR só com verificação humana), nada a acrescentar.

Regras das rodadas anteriores mantidas (literal entre aspas = mensagem;
relato = evento; defesas sempre registradas).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press5-20261016"
T = REPO / "data" / "threads"

FOLHA_MG = ("Folha de S.Paulo", "2026-09-30",
            "https://www1.folha.uol.com.br/poder/2026/09/vorcaro-teve-jantar-restrito-com-padilha-antes-de-encontro-com-lula-em-2024-indicam-mensagens.shtml")
TIMES_MG = ("Times Brasil (espelho da apuração da Folha)", "2026-09-30",
            "https://timesbrasil.com.br/brasil/vorcaro-recebeu-alexandre-padilha-em-jantar-e-dois-dias-depois-disse-a-mares-guia-que-precisava-muito-ver-o-lula")
METRO_ZE = ("Metrópoles (Evellyn Paola e Igor Gadelha)", "2026-09-30",
            "https://www.metropoles.com/brasil/evita-falar-nome-ate-o-meu-alertou-vorcaro-a-chef-de-almoco-para-moraes")
METRO_FF = ("Metrópoles — coluna Igor Gadelha", "2026-09-30",
            "https://www.metropoles.com/colunas/igor-gadelha/caviar-e-trufa-almoco-de-moraes-foi-articulado-por-fabio-faria-com-vorcaro")
VEJA_AL = ("Veja", "2026-10-09",
           "https://veja.abril.com.br/politica/vorcaro-conta-que-liberou-dinheiro-para-filme-sobre-lula-por-negocios-no-governo")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}

THREADS = {
  "walfrido-mares-guia": {
    "title": "Walfrido dos Mares Guia",
    "src_note": ("Folha de S.Paulo, 30/09/2026 (espelhada pelo Times Brasil): mensagens da PF entre Vorcaro e o "
                 "ex-ministro Walfrido dos Mares Guia — acionista relevante da biotecnológica Biomm — tratando de "
                 "inauguração de fábrica com Lula, pedido de ajuda para ver o presidente (25/10/2024), PDP da insulina "
                 "e indicações para a Anvisa. Defesas de Mares Guia, Anvisa, Padilha e Noleto registradas nos eventos."),
    "secs": [FOLHA_MG],
    "msgs": [
      ("2024-03", None, "walfrido-mares-guia", "Olavo me enviou mensagem falando que gostou muito de você",
       "Sobre Olavo Noleto, então secretário-executivo do Ministério da Saúde; transcrição conforme a Veja — a Folha publica o original com erros de digitação, identificando Noleto como 'braço direito' do ministro Padilha.", VEJA_AL),
      ("2024-03", None, "daniel-vorcaro", "Grande amigo. Ja te chamo em seguida", "Resposta na mesma sequência, segundo a reportagem.", FOLHA_MG),
      ("2024-04-11", None, "daniel-vorcaro", "De toda forma estarei torcendo a distancia para que o evento de inauguração marque inicio novo tempo da companhia",
       "Chateado por não poder ir à inauguração da fábrica da Biomm em Nova Lima (MG), por estar em Londres, segundo a reportagem.", FOLHA_MG),
      ("2024-04-11", None, "walfrido-mares-guia", "Fico mais chateado ainda em nào ter nosso mais entusiasmado socio conosco no dia 26.",
       "Erro de digitação ('nào') consta da transcrição da Folha.", FOLHA_MG),
      ("2024-04-11", None, "walfrido-mares-guia", "Virá muita gente mas vc fará falta.",
       "Na mesma mensagem, informa que Lula confirmou presença na inauguração de 26/4, às 10h, segundo a reportagem.", FOLHA_MG),
      ("2024-10-25", None, "daniel-vorcaro", "Que otimo. Estamos precisando muito ver o Lula, por conta desses ataques que tenho sofrido. Depois queria sua ajuda.",
       "Ao saber que Mares Guia teria audiências com Geraldo Alckmin e com Lula em Brasília; convida para falar ao fim do dia em sua casa, segundo a reportagem.", FOLHA_MG),
      ("2024-10-25", None, "daniel-vorcaro", "19 horas",
       "Complementando o convite, conforme espelho da apuração.", TIMES_MG),
      ("2024-12", None, "walfrido-mares-guia", "Ja tivemos o primeiro pedido da PDP da insulina humana",
       "PDP: Parcerias para o Desenvolvimento Produtivo; o espelho da apuração data a mensagem em 17/12/2024.", FOLHA_MG),
      ("2024-12", None, "walfrido-mares-guia", "O indicado para presidir a [Anvisa] é nosso aliado no Min da Saude.Conhece tudo sobre a Biomm",
       "Colchetes constam da transcrição da Folha; as indicações para a agência foram anunciadas em agosto/2025 (evento abaixo).", FOLHA_MG),
      ("2024-12", None, "walfrido-mares-guia", "A nova diretora Daniela Marreco tb otima pessoa e conhece a Biomm", None, FOLHA_MG),
    ],
    "events": [
      ("2024-04-26", "Lula inaugura a fábrica da Biomm em Nova Lima (MG), com presença confirmada às 10h; Vorcaro não compareceu.", FOLHA_MG),
      ("2024-10-23", "Jantar na casa de Vorcaro em Brasília, às 22h, com cinco convidados: o então ministro Alexandre Padilha (Relações Institucionais), o secretário-executivo Olavo Noleto, 'Fernando (primo)', um assessor de Padilha e Júlio Cezar; não constou da agenda pública de Padilha, segundo a reportagem.", FOLHA_MG),
      ("2024-12-04", "Vorcaro é recebido por Lula no Planalto, encontro intermediado por Guido Mantega; reclamou da concentração bancária, e Lula teria encaminhado o tema ao Banco Central (Gabriel Galípolo), segundo a reportagem.", FOLHA_MG),
      (None, "Contratos do Ministério da Saúde com a Biomm: R$ 34,3 milhões (insulina regular, abril/2024) e R$ 20,6 milhões (insulina glargina, dezembro/2024); PDP com Bio-Manguinhos/Fiocruz, Biomm e Gan & Lee aprovada em fevereiro/2025. Em agosto/2025, os nomes de Safatle e Daniela Marreco foram escolhidos para a Anvisa; Safatle é o diretor-presidente da agência.", FOLHA_MG),
      (None, "Defesas: a Anvisa diz que Safatle nunca teve relação ou contato com Vorcaro e que a Biomm recebeu tratamento igual ao das demais; Mares Guia afirma não ter intimidade com Vorcaro — contatos por causa da Biomm — e nega ter intermediado reunião com Lula; sobre o jantar, Padilha e Noleto dizem tratar-se de atividade rotineira do cargo, que Padilha não era ministro da Saúde em 2024 e que não havia acusações contra o Master à época.", FOLHA_MG),
    ],
  },
  "jose-maria-meira": {
    "title": "José Maria Meira (Zé Maria)",
    "src_note": ("Metrópoles, 30/09/2026 (Evellyn Paola e Igor Gadelha): orientações de Vorcaro ao chef Zé Maria na "
                 "organização do almoço oferecido ao ministro Alexandre de Moraes em 30/12/2023, em Campos do Jordão — "
                 "discrição sobre nomes, cardápio de luxo e o episódio da foto. Caso inicialmente revelado por O Globo."),
    "secs": [METRO_ZE],
    "msgs": [
      (None, None, "daniel-vorcaro", "Outra coisa, evitar falar nome, até o meu, pra não constranger o convidado principal. Só se ele perguntar algo de mim aí pode...",
       "Nas orientações para o almoço de 30/12/2023; segundo a reportagem, para que o momento parecesse ser do convidado.", METRO_ZE),
      (None, None, "jose-maria-meira", "Posso deitar o cabelo… kkkk trufa, caviar, vieiras, foie, wagyu",
       "Sobre o cardápio sugerido para o almoço, segundo a reportagem.", METRO_ZE),
      (None, None, "daniel-vorcaro", "Precisa pegar 4 vinhos top na minha adega. 5 na verdade",
       "Sobre os vinhos da adega pessoal de Vorcaro para o almoço, segundo a reportagem.", METRO_ZE),
      (None, None, "daniel-vorcaro", "Isso não podia, né. Fale com ele pra mim que eu não vou gostar disso",
       "Insatisfeito ao saber da foto do chef com o ministro, segundo a reportagem.", METRO_ZE),
      (None, None, "daniel-vorcaro", "Se o ministro pediu tudo bem. Menos mal",
       "Aliviado ao ser informado de que o pedido da foto teria partido do próprio ministro, segundo a reportagem.", METRO_ZE),
    ],
    "events": [
      ("2023-12-30", "Almoço para o ministro Alexandre de Moraes em residência na área do hotel Six Senses Botanique, em Campos do Jordão (SP), articulado por Fábio Faria; menu com caviar beluga, vieiras com ovas de salmão, ovo trufado, foie gras, carne dry aged, wagyu e trufas, com vinhos raros (Château Mouton Rothschild, Haut-Brion, Cheval Blanc) da adega pessoal de Vorcaro; nove convidados e quatro seguranças. Vorcaro chamou Moraes de seu 'convidado mais importante até hoje' e não compareceu, segundo a reportagem.", [METRO_ZE, METRO_FF]),
      (None, "O chef José Maria Meira e a equipe recebiam R$ 120 mil mensais de Vorcaro para eventos privados; convidados do almoço receberam caixas de vinhos, segundo a reportagem.", METRO_FF),
      (None, "Episódio da foto: o chef tirou foto com Moraes; Vorcaro reagiu mal, mas funcionário ('Michael') relatou que o pedido partiu do próprio ministro, segundo a reportagem.", METRO_ZE),
      (None, "Em janeiro/2024, o escritório de Viviane Barci de Moraes fechou contrato de R$ 129 milhões com o Banco Master — em resposta, ela afirma que nunca conduziu causa do banco no STF e lista 36 pareceres, equipe de 15 advogados e 94 reuniões (79 presenciais).", METRO_ZE),
    ],
  },
}

PARTICIPANTS_NEW = [
    {"id": "walfrido-mares-guia", "name": "Walfrido dos Mares Guia", "photo": None,
     "role": "Ex-ministro; acionista da biotecnológica Biomm",
     "aliases": ["Mares Guia"],
     "summary": ("Ex-ministro e amigo de Lula, mineiro como Vorcaro. Segundo a Folha (30/09/2026), trocaram mensagens "
                 "sobre a Biomm (fábrica inaugurada por Lula em abril/2024, contratos com o Ministério da Saúde e PDP da "
                 "insulina), um jantar com Padilha e Olavo Noleto (23/10/2024) e o pedido de ajuda para ver Lula; em "
                 "dezembro/2024, anunciou-lhe o primeiro pedido da PDP e falou de indicações para a Anvisa. Nega "
                 "intimidade e ter intermediado reunião com Lula. Perfil resumido exclusivamente a partir das reportagens "
                 "linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "jose-maria-meira", "name": "José Maria Meira (Zé Maria)", "photo": None,
     "role": "Chef de cozinha; organizava eventos privados de Vorcaro",
     "aliases": ["Zé Maria"],
     "summary": ("Chef e equipe recebiam R$ 120 mil mensais de Vorcaro para eventos privados, segundo o Metrópoles "
                 "(30/09/2026). Organizou o almoço oferecido ao ministro Alexandre de Moraes em 30/12/2023, em Campos do "
                 "Jordão, seguindo orientações de discrição de Vorcaro. Perfil resumido exclusivamente a partir das "
                 "reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
]

# ------------------------------------------------------------- complementações
AUGUSTO_MSGS = [
    ("2024-04-29", None, "augusto-lima", "Entramos na lista exaustiva. Resolvido",
     "Sobre a inclusão do Banco Master na lista de bancos autorizados a operar com recursos de fundos de pensão e RPPS; no mesmo dia, segundo a reportagem, Júlio Cezar cobrou de Vorcaro o adiantamento de R$ 500 mil."),
    ("2024-04-29", None, "daniel-vorcaro", "Você é foda", "Resposta na mesma sequência, segundo a reportagem."),
]
AUGUSTO_EVENTS = [
    (None, "Na proposta de delação rejeitada pela PGR e pela PF, Vorcaro alega que Augusto Lima, 'através dos caciques do PT da Bahia, se reuniu com João Vaccari Neto', e que pagamentos de cerca de R$ 30 milhões em espécie, 'por fora', teriam sido exigidos para um documentário no exterior sobre Lula, além de valores ao Instituto Lula. Em áudio citado pela reportagem, Vorcaro diz: 'O Augusto adianta ali para o Okamotto do Instituto Lula…'. As autoridades descartaram o material por falta de provas."),
    (None, "Defesa de Augusto Lima: os relatos são 'mentirosos, falsos e delirantes', de proposta de delação recusada pelas autoridades, sem valor probatório; pede investigação rigorosa do vazamento. Lula nega ter solicitado ou recebido qualquer vantagem; Padilha nega relação com Vorcaro; Olavo Noleto nega relação com Vorcaro ou recebimento de recursos."),
]
FABIO_MSGS = [
    ("2023-12-27", None, "fabio-faria", "Pode ser dia 30 o almoço?",
     "Mensagem encaminhada por Fábio Faria a Vorcaro, na articulação do almoço, segundo a reportagem."),
    ("2023-12-27", None, "fabio-faria", "Irmão, Alex quer ir almoçar lá no dia 30", None),
    ("2023-12-27", None, "daniel-vorcaro", "Pode", "Resposta na mesma sequência, segundo a reportagem."),
    ("2023-12-30", None, "fabio-faria", "Já estamos aqui, obrigado (sic)",
     "Encaminhada por Fábio no dia do almoço, por volta das 14h15, com mensagem aparentemente do próprio ministro; '(sic)' consta da reportagem."),
    ("2023-12-30", None, "daniel-vorcaro", "Opa. Parece que sim. Ele me ligou. E a turma lá disse que foi tudo certo. Ainda estão lá",
     "Por volta das 18h30, segundo a reportagem."),
    ("2023-12-30", None, "fabio-faria", "Campos? Top! Bom demais", "Resposta na mesma sequência, segundo a reportagem."),
]
JULIO_MSGS = [
    ("2024-04", None, "daniel-vorcaro", "Vamos tentar concluir os que abrimos",
     "Na sequência de 08/04/2024 sobre Petros e Postalis, segundo a reportagem."),
    ("2024-10", None, "julio-cezar", "Daniel, desculpa tá apertando, mas é que você é a única pessoa que eu possa falar isso!!… Quero ir pro jantar tranquilo",
     "Na cobrança do adiantamento de R$ 500 mil, à véspera do jantar de 23/10/2024 em Brasília, segundo a reportagem."),
    ("2024-10", None, "julio-cezar", "Daniel, tô insistindo aqui porque já conversaram com PR e ele gostou da conversa! Olavo pediu pra retornar…",
     "Sobre a articulação com o grupo de Padilha, segundo a reportagem."),
    ("2024-10", None, "julio-cezar", "Daniel, não esquece do Olavo. Ele vai te passar informações. E fazer agenda. Porque semana que vem é sua reunião importante", None),
    ("2025-06", None, "daniel-vorcaro", "Estamos já há mais de 12 meses tentando uma boleta (investimento). Não dá pra mobilizar a equipe…",
     "Parêntese de explicação consta da reportagem."),
    (None, None, "daniel-vorcaro", "Falhou de novo o negócio?", "Entre junho e agosto de 2025, segundo a reportagem."),
    ("2025-08", None, "daniel-vorcaro", "Cara, essa é a última chance. Se não entrar nada até final da semana que vem, eu gostaria que você encerrasse o trabalho…", None),
    ("2025-08", None, "julio-cezar", "Concordo!", "Resposta na mesma sequência, segundo a reportagem."),
    ("2025-08", None, "daniel-vorcaro", "Sexta que vem — não entrando — vida que segue. Lá na frente bolamos outra coisa juntos", None),
]
JULIO_EVENTS = [
    (None, "Notas à reportagem: Lula afirma que 'jamais solicitou ou recebeu qualquer vantagem financeira nem autorizou terceiros a receber recursos de Vorcaro em seu nome'; Padilha nega relação com Vorcaro; Olavo Noleto nega qualquer relação com Vorcaro ou recebimento de recursos; a PGR registra que as tratativas de colaboração foram mediadas por advogados de Vorcaro, 'sem juízo nem recusas prévias'."),
]

COMPLEMENTS = [
    ("augusto-lima", VEJA_AL, AUGUSTO_MSGS, AUGUSTO_EVENTS),
    ("fabio-faria", METRO_FF, FABIO_MSGS, []),
    ("julio-cezar", VEJA_AL, JULIO_MSGS, JULIO_EVENTS),
]


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date, time):
    if time:
        return "minute"
    if not date:
        return None
    return "month" if len(date) == 7 else "date"


def secs(src):
    return [{"publication": p, "date": d, "url": u} for p, d, u in (src if isinstance(src, list) else [src])]


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
    if date and len(date) == 4:
        date = None
    prec = prec_of(date, None)
    e = {
        "id": "e-TEMP", "date": date, "time": None,
        "timestamp_precision": prec,
        "content": content, "event_kind": "editorial_context",
        "verification": dict(VER),
        "sources": {"primary": None, "secondary": secs(src)},
        "source_ref": f"Relato de {secs(src)[0]['publication']} ({secs(src)[0]['date']})",
        "added_in": ADDED_IN,
    }
    if prec is None:
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
    # 1) threads novas
    for pid, spec in THREADS.items():
        msgs = [new_msg(d, tm, s, c, n, src) for d, tm, s, c, n, src in spec["msgs"]]
        events = [new_event(d, c, src) for d, c, src in spec["events"]]
        thread = {
            "id": f"{pid}-daniel-vorcaro",
            "title": spec["title"],
            "participants_ids": ["daniel-vorcaro", pid],
            "source": {"document": spec["src_note"], "url": spec["secs"][0][2],
                       "pages": "Mensagens conforme transcrição da(s) reportagem(ns) indicada(s) em cada registro; nada além do que foi divulgado é inferido."},
            "messages": msgs,
            "timeline_events": events,
        }
        finalize(thread)
        (T / f"{pid}-daniel-vorcaro.json").write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v7] {pid}: {len(msgs)} mensagens, {len(events)} eventos")

    # 2) complementações
    for tid, src, new_msgs, new_events in COMPLEMENTS:
        p = T / f"{tid}-daniel-vorcaro.json"
        t = json.loads(p.read_text(encoding="utf-8"))
        have = {norm(m["content"]) for m in t["messages"]}
        added = 0
        for d, tm, s, c, n in new_msgs:
            if norm(c) in have:
                continue
            t["messages"].append(new_msg(d, tm, s, c, n, src))
            added += 1
        for d, c in new_events:
            t.setdefault("timeline_events", []).append(new_event(d, c, src))
        finalize(t)
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v7] {tid}: +{added} msgs (total {len(t['messages'])}), eventos {len(t['timeline_events'])}")

    # 3) consolidação Geraldo: contato 'Geraldo Brazil Journal' (PF) = Geraldo Samor
    bj_path = T / "geraldo-brazil-journal-daniel-vorcaro.json"
    bj = json.loads(bj_path.read_text(encoding="utf-8"))
    samor_path = T / "geraldo-samor-daniel-vorcaro.json"
    t = json.loads(samor_path.read_text(encoding="utf-8"))
    moved = 0
    for m in bj["messages"]:  # proveniência integral preservada (PF, página, figura)
        if norm(m["content"]) not in {norm(x["content"]) for x in t["messages"]}:
            t["messages"].append(m)
            moved += 1
    for e in bj.get("timeline_events", []):
        t.setdefault("timeline_events", []).append(e)
    t["source"]["document"] += (" Registro adicional: contato salvo como 'Geraldo Brazil Journal' no IPJ-A nº 3298613/2026 "
                                "(PET 16662/STF) — mesmo jornalista, conforme consolidado em 2026-10.")
    finalize(t)
    samor_path.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bj_path.unlink()
    print(f"[v7] geraldo: {moved} mensagem(ns) da PF migrada(s) para geraldo-samor; thread 'geraldo-brazil-journal' removida")

    # 4) participantes
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    have = {x["id"] for x in people}
    for np_ in PARTICIPANTS_NEW:
        if np_["id"] not in have:
            people.append(np_)
    bj_person = next((x for x in people if x["id"] == "geraldo-brazil-journal"), None)
    samor = next(x for x in people if x["id"] == "geraldo-samor")
    if bj_person and samor:
        for alias in bj_person.get("aliases", []):
            if alias not in samor["aliases"]:
                samor["aliases"].append(alias)
        samor.setdefault("profile_sources", [])
        for ps in bj_person.get("profile_sources", []):
            if ps not in samor["profile_sources"]:
                samor["profile_sources"].append(ps)
        samor["summary"] = ("Contato salvo no celular de Vorcaro como 'Geraldo Brazil Journal' — consolidado em 2026-10 "
                            "como o jornalista Geraldo Samor, fundador do Brazil Journal, após cruzamento do episódio Tony Blair "
                            "(IPJ-A nº 3298613/2026 e apuração do UOL). " + samor["summary"])
        people = [x for x in people if x["id"] != "geraldo-brazil-journal"]
        print("[v7] participante geraldo-brazil-journal consolidado em geraldo-samor")
    pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 5) índice
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    index = [e for e in index if e["id"] != "geraldo-brazil-journal-daniel-vorcaro"]
    have_t = {e["id"] for e in index}
    for pid, spec in THREADS.items():
        tid = f"{pid}-daniel-vorcaro"
        if tid in have_t:
            continue
        th = json.loads((T / f"{tid}.json").read_text(encoding="utf-8"))
        index.append({
            "id": tid, "title": spec["title"],
            "participants_ids": ["daniel-vorcaro", pid],
            "message_count": len(th["messages"]),
            "last_message_preview": th["messages"][-1]["content"][:80],
            "featured": False,
            "note": spec["src_note"][:200],
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
    print(f"[v7] índice: {len(index)} conversas")


if __name__ == "__main__":
    main()
