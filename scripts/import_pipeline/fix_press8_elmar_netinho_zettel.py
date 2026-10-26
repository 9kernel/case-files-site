# -*- coding: utf-8 -*-
"""fix_press8_elmar_netinho_zettel.py — correções críticas de 26/10/2026.

Fonte: UOL — coluna Natália Portinari (22/10/2026):
"Deputado agradece Vorcaro após receber pacote na eleição: 'Salvou a pátria'".

ELMAR: m-00001 anterior (25/10/2024 09:30, "Filho, ontem o senhor salvou a
pátria!!") não corresponde à fonte. A reportagem documenta: pedido de apoio ao
festival em 15/08/2024; entrega do volume pelo motorista às 19h11 de 02/10/2024;
agradecimento à tarde de 03/10/2024 ("Muito obrigado amigo. Vc salvou a Pátria.
Vamos marcar semana que vem. Aqui vou ganhar quase tudo"); resultado em 07/10/2024.
Conversa reescrita com 8 mensagens literais; horário do agradecimento não
inventado; contatos do motorista e conteúdo do volume não publicados.

NETINHO: m-00001–m-00004 e e-00001 anteriores não foram localizados na fonte
citada (nem em outra fonte cadastrada) — removidos. Inseridas as mensagens
publicadas (16/08/2024 e seguintes). Festival: Campo Formoso (BA), 5–7/09/2024.

ZETTEL: m-00033–m-00035 (setembro/2025, transcrições não localizáveis na fonte)
removidos. Inseridas as duas falas de Vorcaro a Zettel publicadas (02/10/2024
12h58 e instrução "1mm").
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "data")
UOL = "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/22/deputado-agradece-vorcaro-por-salvar-a-patria-apos-entrega-na-eleicao.htm"
SEC = [{"publication": "UOL — coluna Natália Portinari", "date": "2026-10-22", "url": UOL}]
PROCEEDING = "Operação Compliance Zero — PF/STF (material do celular de Vorcaro, reportado pela imprensa)"
V = "daniel-vorcaro"


def verification(level="public_investigation"):
    return {
        "level": level,
        "origin": "press report",
        "authority": "Polícia Federal" if level == "public_investigation" else None,
        "court": None, "case": None, "document": None, "page": None, "figure": None,
        "official_url": None, "primary_document_located": False,
        "verified_at": "2026-10-26",
        "proceeding": PROCEEDING if level == "public_investigation" else None,
    }


def msg(mid, sender, content, note, date=None, time=None, precision=None, added="ingest-press9-20261026"):
    m = {
        "id": mid, "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content, "editorial_note": note,
        "verification": verification(),
        "sources": {"primary": None, "secondary": [dict(s) for s in SEC]},
        "source_ref": "Mensagem divulgada por UOL — coluna Natália Portinari (2026-10-22)",
        "added_in": added,
    }
    if date is not None:
        m["date"] = date
    if time is not None:
        m["time"] = time
    if precision is not None:
        m["timestamp_precision"] = precision
    return m


def event(eid, content, note=None):
    e = {
        "id": eid, "content": content, "event_kind": "editorial_context",
        "verification": verification("secondary_source"),
        "sources": {"primary": None, "secondary": [dict(s) for s in SEC]},
        "source_ref": "Relato de UOL — coluna Natália Portinari (2026-10-22)",
        "added_in": "ingest-press9-20261026",
    }
    if note is not None:
        e["editorial_note"] = note
    return e


def save(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


# ============================ ELMAR ============================
p = os.path.join(DATA, "threads", "elmar-nascimento-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
E = "elmar-nascimento"
t["messages"] = [
    msg("m-00001", E,
        "Essa festa é na minha terra. Onde meu irmão é prefeito. Netinho que tá coordenando. Se puder ajudar eu te agradeço",
        "No encaminhamento do projeto do 3º Festival das Esmeraldas (documento não reproduzido); a festa ocorreu em Campo Formoso (BA), de 5 a 7/09/2024, um mês antes da eleição, e o irmão citado é Elmo Nascimento (União), então prefeito da cidade, conforme a reportagem.",
        date="2024-08-15", precision="date"),
    msg("m-00002", V, "Pode contar comigo!",
        "Resposta na mesma sequência de 15/08/2024, segundo a reportagem.",
        date="2024-08-15", precision="date"),
    msg("m-00003", V, "Sim. Já te passa.",
        "À noite de 01/10/2024, respondendo a Elmar, que perguntara se Vorcaro já tinha “o contato da pessoa que vai ser procurado” (a reportagem cita o trecho da pergunta apenas em fala indireta/legenda; a pergunta integral não foi transcrita e não é registrada como mensagem).",
        date="2024-10-01", precision="date"),
    msg("m-00004", E, "Pedro vai ligar",
        "Em 02/10/2024: após ligação de 48 segundos encerrada às 7h51, Vorcaro enviou, quatro minutos depois, o contato do seu motorista em São Paulo, Pedro (contato privado não reproduzido), segundo a reportagem.",
        date="2024-10-02", precision="date"),
    msg("m-00005", E,
        "Muito obrigado amigo. Vc salvou a Pátria. Vamos marcar semana que vem. Aqui vou ganhar quase tudo",
        "[Corrigido 2026-10-26: a versão anterior registrava 25/10/2024, 9h30, com transcrição “Filho, ontem o senhor salvou a pátria!!” — texto, data e horário inexistentes na fonte.] Agradecimento enviado na tarde de 03/10/2024, no dia seguinte à entrega de um volume pelo motorista de Vorcaro a uma pessoa indicada pelo deputado em São Paulo, às 19h11 de 02/10/2024. Horário do agradecimento não divulgado; conteúdo do volume não identificado pela reportagem.",
        date="2024-10-03", precision="date", added="ingest-press8-20261023"),
    msg("m-00006", V, "Boa. Fico feliz. Estamos juntos",
        "Resposta na mesma sequência de 03/10/2024, segundo a reportagem.",
        date="2024-10-03", precision="date"),
    msg("m-00007", E, "Pra te mostrar como é campanha na BA",
        "Após tentativa de chamada de vídeo de Elmar não atendida por Vorcaro, na sequência de 03/10/2024, conforme a reportagem.",
        date="2024-10-03", precision="date"),
    msg("m-00008", E, "Obrigado amigo. Ganhei tudo aqui. 35 prefeitos",
        "Na segunda-feira seguinte à eleição de 06/10/2024, ou seja, 07/10/2024, conforme a reportagem.",
        date="2024-10-07", precision="date"),
]
t["timeline_events"] = [
    event("e-00001",
          "[Corrigido 2026-10-26: a versão anterior situava a entrega em 24/10/2024 às 23h27, na véspera do 2º turno, e o agradecimento em 25/10/2024 às 9h30 — cronologia incompatível com a fonte.] Segundo o UOL (22/10/2026), na manhã de 01/10/2024 Elmar e Vorcaro falaram por menos de um minuto; à noite, o deputado pediu o contato de “a pessoa que vai ser procurada”. Em 02/10/2024, após ligação de 48s às 7h51, Vorcaro enviou o contato do seu motorista em São Paulo (não reproduzido); às 12h58 escreveu a Zettel: “Assim que mineiro liberar me avise. Pra programarmos” (registrada na conversa própria) — “Mineiro” é Antônio Carlos Freixo Júnior, apontado pela investigação como gerador de dinheiro vivo para Vorcaro. No fim da tarde, o motorista perguntou se seriam “os dois volumes para a pessoa”; Vorcaro disse que era um (“qq uma”, indicando volumes idênticos — troca com o motorista, não registrada como mensagem desta conversa) e, às 19h11, o motorista anunciou o volume “entregue”. Na tarde de 03/10/2024, Elmar agradeceu (“Vc salvou a Pátria”); a eleição ocorreu em 06/10/2024 e, em 07/10, Elmar relatou 35 prefeitos eleitos. A PF apura a entrega em período eleitoral; o conteúdo do volume segue sem identificação pública e não se afirma que continha dinheiro. Em dezembro de 2024, Elmar ativou mensagens temporárias por 7 dias; em novembro de 2025, reduzidas a 24 horas. Procurado, Elmar não respondeu ao UOL."),
    event("e-00002",
          "Pedido de apoio ao 3º Festival das Esmeraldas (15/08/2024): Elmar encaminhou o projeto do festival, realizado de 5 a 7/09/2024 em Campo Formoso (BA) — cidade governada por seu irmão, Elmo Nascimento (União) —, um mês antes da eleição municipal. Vorcaro aceitou (“Pode contar comigo!”) e, no dia seguinte, levou o pedido a Netinho Lins, coordenador do evento, fechando a cota “Ouro” de R$ 1 milhão, quitada por Pix da Super Empreendimentos e Participações à DuBem Business Marketing (ver conversas próprias de Netinho Lins e Fabiano Zettel)."),
]
save(p, t)
print("[ok] elmar-nascimento reescrito: 8 mensagens, 2 eventos")

# ============================ NETINHO ============================
p = os.path.join(DATA, "threads", "netinho-lins-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
N = "netinho-lins"
t["messages"] = [
    msg("m-00001", V, "Festa lá do Elmar. Falou pra ajudar. Como faço",
        "Em 16/08/2024, no dia seguinte ao pedido de Elmar Nascimento, Vorcaro procurou o empresário, salvo no celular como “Nettinho Bet”, conforme a reportagem; Netinho é investigado na Operação Overclean, da PF.",
        date="2024-08-16", precision="date"),
    msg("m-00002", V, "1k então",
        "Horas depois, após Netinho responder com o convite e Vorcaro pedir a maior cota de patrocínio disponível — a “Ouro”, de R$ 1 milhão; “1k” conforme a transcrição publicada.",
        date="2024-08-16", precision="date"),
    msg("m-00003", N, "Festa do Elmar",
        "Dias depois, na legenda do envio dos dados da sua empresa, a DuBem Business Marketing (dados não reproduzidos), segundo a reportagem; data não divulgada."),
    msg("m-00004", N, "1k. Foi o q vc acertou comigo.",
        "Corrigindo Vorcaro, que perguntara se o valor seria “1,5” (pergunta citada em fala indireta pela reportagem). No mesmo minuto, Vorcaro encaminhou os dados a Fabiano Zettel com a instrução “1mm” (ver conversa própria)."),
]
t["timeline_events"] = [
    event("e-00001",
          "3º Festival das Esmeraldas, realizado de 5 a 7/09/2024 em Campo Formoso (BA), terra de Elmar Nascimento, cujo irmão Elmo Nascimento (União) era o prefeito; coordenação de Netinho Lins, empresário investigado na Operação Overclean. Em 16/08/2024, um mês antes da eleição municipal, Vorcaro fechou com Netinho a cota “Ouro” de R$ 1 milhão; dias depois, no mesmo minuto em que Netinho corrigiu o valor combinado (“1k”), Vorcaro encaminhou à Zettel a instrução de pagamento, e, no dia seguinte, a Super Empreendimentos e Participações efetuou Pix de R$ 1 milhão à DuBem Business Marketing, conforme comprovante empresarial enviado por Zettel à reportagem — comprovante apresentado à imprensa não equivale a documento oficial público individualmente localizado.",
          note="[Corrigido 2026-10-26: a versão anterior registrava quatro mensagens de outubro/2024 e saída de R$ 2 milhões de conta “Master Distributed Orc Cloud” em 10/10/2024 — registros não localizados na fonte citada (UOL, 22/10/2026) nem em outra fonte cadastrada, removidos; o festival constava como Angatuba (SP) e setembro/2025, em desacordo com a fonte.]"),
]
save(p, t)
print("[ok] netinho-lins reescrito: 4 mensagens, 1 evento")

# ============================ ZETTEL ============================
p = os.path.join(DATA, "threads", "fabiano-zettel-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
removed = [m["id"] for m in t["messages"] if m["id"] in ("m-00033", "m-00034", "m-00035")]
t["messages"] = [m for m in t["messages"] if m["id"] not in ("m-00033", "m-00034", "m-00035")]
t["messages"].append(
    msg("m-00033", V, "Assim que mineiro liberar me avise. Pra programarmos",
        "Às 12h58 de 02/10/2024, no contexto da entrega de um volume pelo motorista de Vorcaro a pessoa indicada por Elmar Nascimento (ver conversa própria); “Mineiro” é Antônio Carlos Freixo Júnior, apontado pela investigação como gerador de dinheiro vivo para Vorcaro, conforme a reportagem.",
        date="2024-10-02", time="12:58", precision="minute"))
t["messages"].append(
    msg("m-00034", V, "1mm",
        "Instrução enviada a Zettel no encaminhamento dos dados da DuBem Business Marketing, de Netinho Lins (dados bancários não reproduzidos), dias depois de 16/08/2024, segundo a reportagem; data não divulgada. Antes, Vorcaro perguntara a Netinho se o valor seria “1,5” (ver conversa própria). No dia seguinte, a Super Empreendimentos e Participações efetuou Pix de R$ 1 milhão à DuBem."))
t["timeline_events"].append(
    event("e-00006",
          "Patrocínio de R$ 1 milhão ao 3º Festival das Esmeraldas (Campo Formoso/BA, 5–7/09/2024): em agosto de 2024, Vorcaro encaminhou a Zettel os dados da DuBem Business Marketing com a instrução “1mm”; no dia seguinte, a Super Empreendimentos e Participações efetuou Pix de R$ 1 milhão à DuBem, conforme comprovante enviado por Zettel à reportagem do UOL. O comprovante empresarial apresentado a um jornalista não é tratado como documento oficial público individualmente localizado.",
          note="[Corrigido 2026-10-26: as mensagens m-00033–m-00035 anteriores, datadas de 24–25/09/2025 com transcrições não localizáveis na fonte citada, foram removidas; a negociação do patrocínio situa-se em agosto de 2024, conforme o UOL.]"))
save(p, t)
print(f"[ok] fabiano-zettel: removidos {removed}; adicionadas m-00033/m-00034 e e-00006 (total {len(t['messages'])} mensagens)")

# ==================== threads.json (contagens/previews) ====================
ip = os.path.join(DATA, "threads.json")
idx = json.load(open(ip, encoding="utf-8"))
updates = {
    "elmar-nascimento-daniel-vorcaro": (8, "Obrigado amigo. Ganhei tudo aqui. 35 prefeitos"),
    "netinho-lins-daniel-vorcaro": (4, "1k. Foi o q vc acertou comigo."),
    "fabiano-zettel-daniel-vorcaro": (34, None),
}
for e in idx:
    if e["id"] in updates:
        cnt, prev = updates[e["id"]]
        e["message_count"] = cnt
        if prev is not None:
            e["last_message_preview"] = prev
save(ip, idx)
print("[ok] threads.json atualizado (contagens/previews)")
