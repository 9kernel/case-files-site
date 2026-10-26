# -*- coding: utf-8 -*-
"""ingest_press9_missing.py — mensagens ausentes identificadas na auditoria 26/10/2026.

Fontes:
- ICL Notícias (24/10/2026) "Exclusivo: Vorcaro diz que fez 'parceria boa' com
  Marçal enquanto ele disputava prefeitura de SP" — Rennó 17/08/2024 e
  Carneiro 02/09/2024.
- ICL Notícias (23/10/2026) "Nikolas omitiu nova conversa e pressão sob Vorcaro
  para negócio sobre ativo minerário" — Rennó 02 e 08/04/2025.
- ICL Notícias (19/10/2026) "Com patrocínio de R$ 10 mi por ano, Vorcaro exigiu
  combinar perguntas de entrevista na CNN" — Ana Matos, 19/08 e 18/09/2024,
  26/09/2024, 29/09/2024, 01/10/2024, 31/03/2025, 03 e 14/04/2025.
- ICL Notícias (20/10/2026) "Coach de Flávio Bolsonaro, Marçal defendeu Master
  a pedido de Vorcaro com entrevista da CNN" — Ana Matos, 05/04/2025.
- Folha/C-Level (22/10/2026) "Vorcaro pediu a ex-diretor do BC que pressionasse
  Caixa em caso de aporte barrado no Master" — Paulo Sérgio, 12/07/2024.
- BBC News Brasil (23/10/2026) "'Derruba esse site'..." — Mourão, 12/12/2023,
  janeiro/2024, 31/01/2024, 02 e 10 e 25/09/2024, 23/10/2025.

Regras: somente trechos literais publicados; remetentes conforme a reportagem;
"Léo" não identificado; sem dados privados; sem mensagens de terceiros criadas
a partir de relatos; contradições e negativas preservadas.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "data")
V = "daniel-vorcaro"


def sources(items):
    return {"primary": None, "secondary": [dict(i) for i in items]}


def verification(level, proceeding=None):
    v = {
        "level": level,
        "origin": "press report",
        "authority": "Polícia Federal" if level == "public_investigation" else None,
        "court": None, "case": None, "document": None, "page": None, "figure": None,
        "official_url": None, "primary_document_located": False,
        "verified_at": "2026-10-26",
    }
    if proceeding:
        v["proceeding"] = proceeding
    return v


def make_msg(mid, sender, content, note, sec, source_ref, level, proceeding=None,
             date=None, time=None, precision=None):
    m = {
        "id": mid, "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content, "editorial_note": note,
        "verification": verification(level, proceeding),
        "sources": sources(sec),
        "source_ref": source_ref,
        "added_in": "ingest-press9-20261026",
    }
    if date is not None:
        m["date"] = date
    if time is not None:
        m["time"] = time
    if precision is not None:
        m["timestamp_precision"] = precision
    return m


def make_event(eid, content, sec, source_ref, note=None):
    e = {
        "id": eid, "content": content, "event_kind": "editorial_context",
        "verification": verification("secondary_source"),
        "sources": sources(sec),
        "source_ref": source_ref,
        "added_in": "ingest-press9-20261026",
    }
    if note is not None:
        e["editorial_note"] = note
    return e


def save(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def insert_before(lst, anchor_id, new_items):
    idx = next(i for i, m in enumerate(lst) if m["id"] == anchor_id)
    return lst[:idx] + new_items + lst[idx:]


def insert_after(lst, anchor_id, new_items):
    idx = next(i for i, m in enumerate(lst) if m["id"] == anchor_id)
    return lst[: idx + 1] + new_items + lst[idx + 1 :]


# =====================================================================
# LUIZ RENNÓ — ICL (Marçal 24/10/2026; Nikolas 23/10/2026)
# =====================================================================
ICL_MARCAL = "https://iclnoticias.com.br/vorcaro-diz-que-fez-parceria-boa-com-marcal-enquanto-ele-disputava-a-prefeitura-de-sp/"
ICL_NIKOLAS = "https://iclnoticias.com.br/nikolas-vorcar-ativo-minerario-conversa-pressao/"
SEC_MARCAL = [{"publication": "ICL Notícias", "date": "2026-10-24", "url": ICL_MARCAL}]
SEC_NIKOLAS = [{"publication": "ICL Notícias", "date": "2026-10-23", "url": ICL_NIKOLAS}]
PROC_MARCAL = ("PF — mensagens do celular de Vorcaro apreendidas pela Polícia Federal e obtidas "
               "pelo Núcleo Investigativo do ICL Notícias (24/10/2026); a reportagem não nomeia o "
               "procedimento individualmente")
PROC_NIKOLAS = ("PF — mensagens do celular de Vorcaro apreendidas pela Polícia Federal e obtidas "
                "pelo Núcleo Investigativo do ICL Notícias (23/10/2026); a reportagem não nomeia o "
                "procedimento individualmente")

p = os.path.join(DATA, "threads", "luiz-renno-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
R = "luiz-renno"
marcal = [
    make_msg("m-00011", R, "Pablo marcal quer marcar um jantar com vc",
             "Em 17/08/2024, Rennó informa a Vorcaro o interesse de Pablo Marçal, então candidato à Prefeitura de São Paulo, em marcar um jantar, conforme a reportagem.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
    make_msg("m-00012", V, "Outro?",
             "Resposta na mesma sequência de 17/08/2024.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
    make_msg("m-00013", V, "Falando c ele todo dia",
             "Na mesma sequência de 17/08/2024.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
    make_msg("m-00014", V, "Acho que ele vai dar trabalho ainda na política e tera projecao no futuro",
             "Sobre Marçal, na mesma conversa de 17/08/2024; grafia conforme publicada.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
    make_msg("m-00015", V, "Fiz uma parceria boa",
             "Sobre Marçal, na mesma conversa de 17/08/2024; a reportagem não detalha a parceria nem comprova contrato, pagamento ou doação — ver evento de contexto.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
    make_msg("m-00016", V, "Com ele e partido",
             "Sequência imediata da mensagem anterior, esclarecendo que a parceria seria com Marçal e com o partido (PRTB), segundo a reportagem.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-08-17", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00001", marcal)

nikolas = [
    make_msg("m-00017", R, "confirma uma informação, Nicolas deputado, Thiago adv e mineração Capão!",
             "Às 14h02 de 02/04/2025, Rennó pede confirmação sobre Nikolas Ferreira, o advogado dele (Thiago) e a mineradora Capão, no contexto de proposta envolvendo ativo minerário apresentada por Nikolas e seu advogado, conforme a reportagem.",
             SEC_NIKOLAS, "Mensagem divulgada por ICL Notícias (2026-10-23)", "public_investigation", PROC_NIKOLAS,
             date="2025-04-02", time="14:02", precision="minute"),
    make_msg("m-00018", V, "Nikolas me pediu atendi 10 min aqui",
             "Resposta na mesma sequência de 02/04/2025.",
             SEC_NIKOLAS, "Mensagem divulgada por ICL Notícias (2026-10-23)", "public_investigation", PROC_NIKOLAS,
             date="2025-04-02", precision="date"),
    make_msg("m-00019", R, "Nao vale a pena ok!",
             "À noite de 02/04/2025, após expor avaliação comercial desfavorável que já tinha da área (a reportagem cita apenas o fragmento “análise dessa área”, não transcrito integralmente), segundo a reportagem.",
             SEC_NIKOLAS, "Mensagem divulgada por ICL Notícias (2026-10-23)", "public_investigation", PROC_NIKOLAS,
             date="2025-04-02", precision="date"),
    make_msg("m-00020", R, "Turma desse lado me cobrando! Falei que não tive tempo de olhar com vc! Negócio é ruim e entendo que não é o momento! Se pensar diferente me avise",
             "Em 08/04/2025; Vorcaro não respondeu, segundo a reportagem. A reportagem não esclarece integralmente o pedido, e nada indica que o negócio foi concluído.",
             SEC_NIKOLAS, "Mensagem divulgada por ICL Notícias (2026-10-23)", "public_investigation", PROC_NIKOLAS,
             date="2025-04-08", precision="date"),
]
t["messages"] = insert_before(t["messages"], "m-00007", nikolas)
t["timeline_events"].append(make_event(
    "e-00005",
    "Contexto Marçal (ICL, 24/10/2026): em 17/08/2024, Rennó transmitiu a Vorcaro o interesse de Pablo Marçal em um jantar; Vorcaro disse falar “todo dia” com ele e que fizera “uma parceria boa” “com ele e partido” (PRTB), na disputa da Prefeitura de São Paulo de 2024. A declaração de parceria não comprova contrato, pagamento ou doação eleitoral; o ICL informa ter checado as prestações de contas de Marçal, do PRTB e do Master sem localizar doações. Não há conversa direta entre Vorcaro e Marçal registrada neste arquivo.",
    SEC_MARCAL, "Relato de ICL Notícias (2026-10-24)"))
t["timeline_events"].append(make_event(
    "e-00006",
    "Contexto ativo minerário (ICL, 23/10/2026): em abril de 2025, Rennó e Vorcaro trataram de proposta envolvendo ativo minerário apresentada pelo deputado Nikolas Ferreira e por seu advogado; Rennó expôs avaliação comercial desfavorável (“Nao vale a pena ok!”) e, em 08/04/2025, relatou cobrança da outra parte. Vorcaro não respondeu. O áudio de Nikolas a Vorcaro de 30/03/2025 citado pela reportagem já está registrado na conversa própria de Nikolas (não duplicado). A reportagem não esclarece integralmente o pedido nem comprova conclusão do negócio.",
    SEC_NIKOLAS, "Relato de ICL Notícias (2026-10-23)"))
save(p, t)
print(f"[ok] luiz-renno: {len(t['messages'])} mensagens (10→20), +2 eventos")

# =====================================================================
# FLÁVIO CARNEIRO — ICL Marçal (02/09/2024)
# =====================================================================
p = os.path.join(DATA, "threads", "flavio-carneiro-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
C = "flavio-carneiro"
carneiro = [
    make_msg("m-00024", C,
             "Ontem Gustavo Lima chamou o Léo na casa dele depois da festa e apresentou o Marçal e pediu pra ele apoiar a campanha do cara. Alguma objeção nossa?",
             "Em 02/09/2024, Carneiro repassa a Vorcaro relato sobre episódio na casa de Gustavo Lima, no contexto do pedido de apoio à campanha de Pablo Marçal à Prefeitura de São Paulo. A reportagem não identifica quem é “Léo”; nenhuma associação a Leonardo Valverde ou a outra pessoa é feita ou inferida.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-09-02", precision="date"),
    make_msg("m-00025", V, "Nao podemos fazer isso pro marcal pelo pedido do gustavo ne",
             "Resposta na mesma sequência de 02/09/2024; grafia conforme publicada.",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-09-02", precision="date"),
    make_msg("m-00026", V, "A turma do leo tem que jogar pra mim",
             "Sequência de 02/09/2024; “leo” sem identificação na reportagem (grafia minúscula conforme publicada).",
             SEC_MARCAL, "Mensagem divulgada por ICL Notícias (2026-10-24)", "public_investigation", PROC_MARCAL,
             date="2024-09-02", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00003", carneiro)
t["timeline_events"].append(make_event(
    "e-00005",
    "Contexto Marçal (ICL, 24/10/2026): em 02/09/2024, Carneiro relatou a Vorcaro que, na casa de Gustavo Lima, um “Léo” foi apresentado a Pablo Marçal com pedido de apoio à campanha municipal de São Paulo de 2024; Vorcaro respondeu que não poderiam fazer isso “pro marcal” a pedido de Gusttavo Lima. O relato é de Carneiro sobre terceiros: não há mensagens de Marçal ou de Gusttavo Lima nesta conversa, e a reportagem não dá indícios de quem seja “Léo” — qualquer identificação seria inferência.",
    SEC_MARCAL, "Relato de ICL Notícias (2026-10-24)"))
save(p, t)
print(f"[ok] flavio-carneiro: {len(t['messages'])} mensagens (23→26), +1 evento")

# =====================================================================
# ANA MATOS — ICL CNN (19/10/2026) e influenciadores (20/10/2026)
# =====================================================================
ICL_CNN = "https://iclnoticias.com.br/patrocinio-10-milhoes-vorcaro-cnn-entrevista/"
ICL_INFL = "https://iclnoticias.com.br/coach-de-flavio-marcal-defendeu-master-vorcaro/"
SEC_CNN = [{"publication": "ICL Notícias", "date": "2026-10-19", "url": ICL_CNN}]
SEC_INFL = [{"publication": "ICL Notícias", "date": "2026-10-20", "url": ICL_INFL}]
PROC_CNN = ("PF — série do ICL Notícias (Núcleo Investigativo) sobre mensagens do celular de "
            "Vorcaro apreendidas pela PF; a reportagem não nomeia o procedimento individualmente")
PROC_INFL = PROC_CNN

p = os.path.join(DATA, "threads", "ana-matos-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
A = "ana-matos"
by_id = {m["id"]: m for m in t["messages"]}

# Correção de colchete editorial em m-00014: "[Nikolas]" é inserção do veículo
m14 = by_id["m-00014"]
m14["content"] = "Eu me dou muito bem com ele. Ele não citaria"
m14.pop("literal_brackets", None)
m14["editorial_note"] = ("[Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado com "
                         "“[Nikolas]” como esclarecimento do veículo (o ICL transcreve “ele (Nikolas)”); o "
                         "esclarecimento não constava do original e foi movido para esta nota. Final de abril de "
                         "2024: Ana Matos alertou Vorcaro de que Nikolas Ferreira compartilhara reportagem do O "
                         "Globo sobre o Master; Vorcaro respondia que se dava bem com ele.")

gA = [  # 19/08/2024
    make_msg("m-00022", A, "Eles me mandaram 4mm de patrocínio. Com a mensagem: Ana, consegue chegar em 4K? Achei muito. Ele me disse que tem o canal CNN Money vindo. Esse valor já não poderia estar dentro desse fee de patrocínio, que será $$$?",
             "Em 19/08/2024, sobre pedido de patrocínio da CNN Brasil ao Master; a mensagem citada (“Ana, consegue chegar em 4K?”) é transcrita dentro da própria mensagem, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-08-19", precision="date"),
    make_msg("m-00023", V, "Que isso", "Resposta na mesma sequência de 19/08/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-08-19", precision="date"),
    make_msg("m-00024", A, "Muita grana", "Na mesma sequência de 19/08/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-08-19", precision="date"),
    make_msg("m-00025", V, "Negocia aí", "Na mesma sequência de 19/08/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-08-19", precision="date"),
    make_msg("m-00026", A, "Oi. Fechei 1mm com a CNN. Não sei se eles vão ligar pra vc, mas tá fechado com o VP do João. Foi tudo bem",
             "Conclusão do patrocínio de R$ 1 milhão, horas depois, na mesma data, conforme a reportagem; “VP do João” refere-se ao então vice-presidente comercial João Camargo.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-08-19", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00014", gA)

gB = [  # 18/09, 26/09, 29/09, 01/10/2024
    make_msg("m-00027", V, "Ana, na verdade guarda isso com voce mas to entrando na cnn com o rubens menin.",
             "Em 18/09/2024, sobre plano de Vorcaro de entrar na CNN com o economista Paulo Gala; “rubens menin” conforme a transcrição publicada.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-18", precision="date"),
    make_msg("m-00028", V, "Mas cnn precisa aprovar. E eu entrar no conselho",
             "Na mesma sequência de 18/09/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-18", precision="date"),
    make_msg("m-00029", V, "Pq esse canal sera conteudo escolhido por nos. Vc participando do editorial. Do conselho editorial de tudo.",
             "Na mesma sequência de 18/09/2024; pretensão declarada na conversa — a CNN nega sociedade de Vorcaro e interferência editorial (ver evento de contexto).",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-18", precision="date"),
    make_msg("m-00030", A, "Para isso eles pedem 12mm por 12 meses",
             "Em 26/09/2024, sobre a cota de patrocínio da futura CNN Money, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-26", precision="date"),
    make_msg("m-00031", A, "Nós já temos 10mm com eles/ano em CNN News. Eu renovo com eles esse valor pra CNN Money. Faria essa cota fundador Money exclusiva banco master.",
             "Proposta de renovar o patrocínio anual de R$ 10 milhões como cota fundadora exclusiva da CNN Money, na mesma data, segundo a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-26", precision="date"),
    make_msg("m-00032", A, "Faria uma black list de quem não pode patrocinar. Colocaria alguém – pode ser eu – para entender conteúdo editorial do canal pra ver nossos interesses.",
             "Na mesma sequência de 26/09/2024; intenção declarada na conversa, não interferência comprovada — ver evento de contexto com o posicionamento da CNN.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-26", precision="date"),
    make_msg("m-00033", V, "Concordo com tudo",
             "Resposta na mesma sequência de 26/09/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-26", precision="date"),
    make_msg("m-00034", A, "me parece outro saco sem fundo de querer grana. Kk",
             "Em 29/09/2024, sobre a CNN, conforme a reportagem; grafia conforme publicada.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-09-29", precision="date"),
    make_msg("m-00035", A, "Oi. Eu vou estar num eve to agora q estará Joao e Cris Moreira do comercial CNN. Eles falaram sabre mais grana com vc esses dias? Porque eu disse que nao haveria dinheiro novo como patrocinadores. Que eu redirecionaria o valor que já temos mês com eles",
             "Em 01/10/2024; grafia conforme publicada (inclusive “sabre”).",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-10-01", precision="date"),
    make_msg("m-00036", V, "Não to sabendo", "Resposta em 01/10/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-10-01", precision="date"),
    make_msg("m-00037", A, "Tabom. Só pra estarmos alinhados porque eu não disse que nosso investimento permaneceria o que já temos. 10mm ano. Ao invés de CNN News vou direcionar pra Money",
             "Fechamento do alinhamento em 01/10/2024.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2024-10-01", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00017", gB)

gC = [  # 31/03/2025, 03/04/2025, 14/04/2025 (CNN)
    make_msg("m-00038", A, "Levantei todos os pontos positivos do balanço para o João Camargo, para veicular amanhã na CNN money",
             "Em 31/03/2025, sobre pauta da CNN Money, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-03-31", precision="date"),
    make_msg("m-00039", V, "Ana, falei c joao, acho que tenho que ir cnn falar do balanco e operacao",
             "Às 07h26 de 03/04/2025, sobre eventual ida de Vorcaro à CNN; grafia conforme publicada.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", time="07:26", precision="minute"),
    make_msg("m-00040", V, "O que acha", "Na mesma sequência de 03/04/2025.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", precision="date"),
    make_msg("m-00041", A, "Eu respondi que ele tem que combinar com a gente antes as perguntas do Naka. Todas. Antes",
             "Exigência de combinar previamente as perguntas da entrevista (“Naka”, apresentador da CNN), conforme a reportagem; a CNN nega interferência editorial — ver evento de contexto.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", precision="date"),
    make_msg("m-00042", A, "A gente dizer o que queremos falar. Tudo combinado. 100%. Eu vou com vc.",
             "Na mesma sequência de 03/04/2025.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", precision="date"),
    make_msg("m-00043", A, "Ainda assim temos que pensar que o João eh amigo de todo mundo. Sempre tem 2 agendas.",
             "Na mesma sequência de 03/04/2025.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", precision="date"),
    make_msg("m-00044", V, "O paulo falaria sobre balanço? Gala. Treinamos ele",
             "Na mesma sequência de 03/04/2025; Ana Matos disse ter feito um vídeo de treino com Paulo Gala (relato em fala indireta na reportagem).",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", precision="date"),
    make_msg("m-00045", V, "Vou deixar o paulo entrar. Mesmo. Ta muita batida em mim. Vamos deixar poeira abaixar na semana que vem eu entro",
             "Às 11h55 de 03/04/2025, desistindo de ir à entrevista, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", time="11:55", precision="minute"),
    make_msg("m-00046", A, "Paulo Gala hoje cnn",
             "Às 13h04 de 03/04/2025, confirmando a participação do economista na CNN Money, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-03", time="13:04", precision="minute"),
    make_msg("m-00047", A, "Eu pedi essa entrada hoje na pauta. Paulo seguiu meu briefing. Defendeu CDB via segurança do FGC, e abordou concentração que eh nossa pauta contínua",
             "Em 14/04/2025, sobre a participação de Paulo Gala na CNN Money, conforme a reportagem.",
             SEC_CNN, "Mensagem divulgada por ICL Notícias (2026-10-19)", "public_investigation", PROC_CNN,
             date="2025-04-14", precision="date"),
]
gD = [  # 05/04/2025 (influenciadores) — inseridos antes de m-00018 (19h33, já existente)
    make_msg("m-00048", A, "Além disso, por três meses (renováveis ou não) teremos cerca de 15 influenciadores com alto engajamento",
             "Às 15h03 de 05/04/2025, sobre estratégia de comunicação com influenciadores, conforme a reportagem.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", time="15:03", precision="minute"),
    make_msg("m-00049", A, "Os conteúdos desses influenciadores seguirão o formato 'Marcal', como o que compartilhei ontem no grupo",
             "Em sequência imediata na mesma data; aspas em “Marcal” conforme a publicação.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", precision="date"),
    make_msg("m-00050", A, "Eu fico pasmo como o PT quer politizar tudo. Um banco privado fecha um acordo com outro banco (público), dentro da lei, e já vem esquerda correndo pro Judiciário. É por isso que o país não anda.",
             "Roteiro de exemplo enviado na mesma mensagem, separado por público-alvo (“direita”); a reportagem transcreve também roteiros para públicos “de esquerda” e “de mercado”, não reproduzidos integralmente aqui.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", precision="date"),
    make_msg("m-00051", V, "Tira PT. Pessoas querem politizar.",
             "Aprovação da linha com ajuste, na mesma data, conforme a reportagem.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", precision="date"),
]
t["messages"] = insert_before(t["messages"], "m-00018", gC + gD)

gE = [  # 20h49 de 05/04/2025 — entre m-00018 (19h33) e m-00019 (23h43), já existentes
    make_msg("m-00052", V, "Falou com Pablo? Soltou mais um",
             "Às 20h49 de 05/04/2025, sobre novas postagens de Pablo Marçal, conforme a reportagem.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", time="20:49", precision="minute"),
]
t["messages"] = insert_after(t["messages"], "m-00018", gE)

gF = [  # resposta "Sim" após m-00019 (23h43, já existente)
    make_msg("m-00053", A, "Sim",
             "Resposta de Ana Matos na madrugada de 05/04/2025, após o pedido para que Marçal falasse de concentração bancária (m-00019), conforme a reportagem.",
             SEC_INFL, "Mensagem divulgada por ICL Notícias (2026-10-20)", "public_investigation", PROC_INFL,
             date="2025-04-05", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00019", gF)

t["timeline_events"].append(make_event(
    "e-00003",
    "Contexto CNN (ICL, 19/10/2026): o Master era anunciante da CNN Brasil; em 19/08/2024, Ana Matos relatou pedido de patrocínio e fechou R$ 1 milhão; em setembro/outubro de 2024, discutiu-se renovar os R$ 10 milhões anuais como cota fundadora da futura CNN Money (pedido da emissora: “12mm por 12 meses”), com pretensões registradas na conversa de Vorcaro entrar no “conselho editorial” e de Ana Matos montar “black list” de patrocinadores e acompanhar o conteúdo editorial. Em abril de 2025, exigiu-se combinar previamente as perguntas de entrevista; Vorcaro desistiu de participar e indiciu Paulo Gala, que entrevistou em 03/04 e voltou ao tema em 14/04 seguindo briefing de Ana. Em nota, a CNN negou ter tido “qualquer sociedade” com Vorcaro e qualquer interferência editorial na cobertura, confirmando o Master como anunciante; João Camargo (vice-presidente comercial) e Paulo Gala deixaram a emissora, e Gala negou permitir que o conteúdo editorial fosse orientado por anunciantes. As mensagens registram intenção e pressão comercial; interferência editorial efetivamente ocorrida não está demonstrada nos registros deste arquivo.",
    SEC_CNN, "Relato de ICL Notícias (2026-10-19)"))
t["timeline_events"].append(make_event(
    "e-00004",
    "Contexto influenciadores (ICL, 20/10/2026): em 05/04/2025, Ana Matos propôs contratar cerca de 15 influenciadores por três meses com roteiros separados por público (“formato Marcal”), aprovados por Vorcaro com o ajuste “Tira PT”; no mesmo dia, após post de Pablo Marçal sobre o banco, Vorcaro acionou Ana Matos para abordá-lo “delicadamente” (m-00018/m-00019) e repassou o contato de Marçal (número não reproduzido). Segundo a reportagem, em setembro de 2025 Marçal publicou defesa do Master após troca de mensagens com Vorcaro (reportagem original de O Globo, não transcrita integralmente pelo ICL) e viajou em jato cujo voo (R$ 1,17 milhão) foi pago pela Prime2, empresa de estrutura do Master ligada ao coach K. Vilanova; O Globo e o Poder360 não localizaram doações de Vorcaro à campanha de Marçal nas prestações de contas. Em 22/10/2026, Marçal negou ligação com Vorcaro e classificou a reportagem como “fake news”. Planejamento de conteúdo não comprova publicação efetiva nem pagamento individual verificado.",
    SEC_INFL, "Relato de ICL Notícias (2026-10-20)"))
save(p, t)
print(f"[ok] ana-matos: {len(t['messages'])} mensagens (21→53), m-00014 corrigido, +2 eventos")

# =====================================================================
# PAULO SÉRGIO — Folha C-Level (22/10/2026), 12/07/2024
# =====================================================================
FOLHA = "https://c-level.folha.uol.com.br/financas/2026/10/vorcaro-pediu-a-ex-diretor-do-bc-que-pressionasse-caixa-em-caso-de-aporte-barrado-no-master.shtml"
SEC_FOLHA = [{"publication": "Folha C-Level", "date": "2026-10-22", "url": FOLHA}]

p = os.path.join(DATA, "threads", "paulo-sergio-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
PS = "paulo-sergio"
folha = [
    make_msg("m-00002", V, "Já estava assinado, aprovado em comitê",
             "Sobre a operação da Caixa com o Master, na conversa de 12/07/2024, pouco antes de Vorcaro pedir a Souza ajuda do Banco Central, conforme a reportagem. Ressalva de identificação: a Folha identifica o interlocutor como Paulo Sérgio Neves de Souza, ex-diretor do BC; o contato “Paulo Sergio” do IPJ-A é identificado como “Diretor do Banco Central” — a correspondência entre ambos não é individualmente demonstrada nos documentos públicos disponíveis.",
             SEC_FOLHA, "Mensagem divulgada por Folha C-Level (2026-10-22)", "secondary_source",
             date="2024-07-12", precision="date"),
    make_msg("m-00003", V, "Eles devem fazer um comunicado dizendo que fizeram queixa-crime de vazamento do relatório e que o relatório não representa a opinião da Caixa",
             "Em 12/07/2024, após a publicação da primeira reportagem sobre o caso, Vorcaro pergunta se o Bacen não poderia pedir à Caixa para se posicionar (pergunta citada em fala indireta, não transcrita integralmente) e sugere o comunicado, conforme a reportagem.",
             SEC_FOLHA, "Mensagem divulgada por Folha C-Level (2026-10-22)", "secondary_source",
             date="2024-07-12", precision="date"),
    make_msg("m-00004", PS, "Nós já interpelamos a Caixa para incluir na apuração",
             "[Corrigido no registro: publicado como “Nós já interpelamos a Caixa para incluir na apuração [o vazamento de informações internas]”; o colchete é inserção do veículo e foi movido para esta nota.] Resposta um minuto depois, conforme a reportagem.",
             SEC_FOLHA, "Mensagem divulgada por Folha C-Level (2026-10-22)", "secondary_source",
             date="2024-07-12", precision="date"),
    make_msg("m-00005", V, "Estrago será imenso",
             "Sobre o impacto dos vazamentos e o cancelamento de operações (uma em vigor e outra em vias de aprovação), na mesma conversa, conforme a reportagem.",
             SEC_FOLHA, "Mensagem divulgada por Folha C-Level (2026-10-22)", "secondary_source",
             date="2024-07-12", precision="date"),
]
t["messages"] = insert_before(t["messages"], "m-00001", folha)
t.setdefault("timeline_events", []).append(make_event(
    "e-00001",
    "Contexto Caixa Asset (Folha C-Level, 22/10/2026): segundo a reportagem, em 10/07/2024 Souza perguntou a Vorcaro se algo tinha saído sobre descumprimento do compulsório no caso Master; em 11/07, Vorcaro disse ter sido questionado sobre “a parceria com a Caixa, que está para sair”; em 12/07, após a primeira reportagem, Vorcaro pediu ao ex-diretor do BC que pressionasse a Caixa a se posicionar publicamente (mensagens registradas acima). Em 16/07, Vorcaro afirmou que as duas operações estavam suspensas. Discutia-se possível aplicação de R$ 500 milhões da Caixa Asset no Master — a Caixa informou que a aplicação não ocorreu. Em nota, Souza disse que jamais protegeu interesses de Vorcaro; o BC e a defesa do ex-banqueiro não comentaram. As mensagens de julho de 2024 provêm de reportagem (não de peça oficial individualmente localizada) e não reutilizam a página documental da mensagem de março de 2025; ver ressalva de identificação no perfil do participante.",
    SEC_FOLHA, "Relato de Folha C-Level (2026-10-22)"))
save(p, t)
print(f"[ok] paulo-sergio: {len(t['messages'])} mensagens (1→5), +1 evento")

# =====================================================================
# FELIPE MOURÃO — BBC News Brasil (23/10/2026)
# =====================================================================
BBC = "https://www.bbc.com/portuguese/articles/cjy56grn51zzo"
SEC_BBC = [{"publication": "BBC News Brasil", "date": "2026-10-23", "url": BBC}]

p = os.path.join(DATA, "threads", "felipe-mourao-daniel-vorcaro.json")
t = json.load(open(p, encoding="utf-8"))
M = "felipe-mourao"


def bbc_msg(mid, sender, content, note, date=None, precision=None):
    return make_msg(mid, sender, content, note, SEC_BBC,
                    "Mensagem divulgada por BBC News Brasil (2026-10-23)", "secondary_source",
                    date=date, precision=precision)


g1 = [
    bbc_msg("m-00088", M, "Esses são os links positivos que ficaram,pede para dar uma olhada e se tiver algum que vc queira que retire ou que modifique algum me avise",
            "Legenda no envio do documento “720 Postagens”, em 12/12/2023, conforme a BBC; o documento não é reproduzido. Grafia conforme publicada. A BBC relata, em fala indireta, ligações entre esse material e a empresa Saftec e o site TechBusca (bloqueado pela Justiça em 2022), sem transcrever essas mensagens.",
            date="2023-12-12", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00004", g1)

g2 = [
    bbc_msg("m-00089", V, "Meu socio tava querendo que derrubasse",
            "Janeiro de 2024 (dia não divulgado), sobre vídeo de drone da Ilha do Topete (BA) publicado no canal My Phantom Toy, cujo sócio reclamou da exposição, conforme a BBC.",
            date="2024-01", precision="month"),
    bbc_msg("m-00090", V, "Pq ta expondo ilha dele",
            "Na mesma sequência, conforme a BBC.",
            date="2024-01", precision="month"),
    bbc_msg("m-00091", V, "Derrubar so esse link ne",
            "Respondendo a Mourão, que perguntara (em fala indireta na reportagem) se deveria “derrubar total”, conforme a BBC.",
            date="2024-01", precision="month"),
    bbc_msg("m-00092", M, "Banido mestre",
            "Cinco dias depois, anunciando a remoção, com o vídeo encaminhado (não reproduzido), conforme a BBC.",
            date="2024-01", precision="month"),
    bbc_msg("m-00093", V, "Derruba esse site",
            "Em 31/01/2024, no encaminhamento de nota sobre um bilionário na temporada de esqui na Suíça publicada pelo blog Nem Amigo Nem Inimigo, conforme a BBC; mais de uma hora depois, Mourão informou, em fala indireta, que o link estava fora do ar.",
            date="2024-01-31", precision="date"),
    bbc_msg("m-00094", V, "Urgente", "Na mesma sequência de 31/01/2024, conforme a BBC.",
            date="2024-01-31", precision="date"),
    bbc_msg("m-00095", V, "Mas deixa sempre no gatilho",
            "Recusando proposta posterior de Mourão de “tomar” o site e o domínio do blog (proposta descrita em fala indireta pela BBC); data não divulgada."),
    bbc_msg("m-00096", M, "Estamos dominando o site, vamos ficar monitorando, qualquer coisa que sair derrubamos tudo e se precisar, derrubamos o site.",
            "Na mesma tarde, conforme a BBC; a reportagem registra ainda, sem transcrevê-la, mensagem segundo a qual dados de login do blog estariam em nome de parente do jornalista responsável — detalhe de vigilância sobre terceiros não reproduzido neste arquivo."),
]
t["messages"] = insert_after(t["messages"], "m-00088", g2)

g3 = [
    bbc_msg("m-00097", M, "pode mandar derrubar esses dois links?",
            "Em 02/09/2024, no envio do link da reportagem da Folha sobre Vorcaro com a reprodução do trecho (link público da Folha; não reproduzido integralmente aqui), conforme a BBC.",
            date="2024-09-02", precision="date"),
    bbc_msg("m-00098", V, "Nao sei como vai derrubar folha",
            "Resposta na mesma sequência de 02/09/2024.",
            date="2024-09-02", precision="date"),
    bbc_msg("m-00099", M, "Já pedi os meninos,pode deixar",
            "Na mesma sequência; “meninos” é o termo usado por Mourão, segundo a BBC, para as pessoas que supostamente trabalhavam para derrubar sites e levantar dados de alvos. Grafia conforme publicada.",
            date="2024-09-02", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00019", g3)

g4 = [
    bbc_msg("m-00100", M, "Sobre o link da folha está em processo para ser removido, enquanto isso estamos em cima",
            "Oito dias depois de 02/09/2024 (data derivada de forma determinística), conforme a BBC.",
            date="2024-09-10", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00020", g4)

g5 = [
    bbc_msg("m-00101", M, "Estamos trabalhando para entrar na database do site da Folha de São Paulo para remover do backup. Assim faremos com os outros links também.",
            "Em 25/09/2024, proposta de acesso ao sistema da Folha para apagar também o backup, conforme a BBC. Dois dias depois, segundo a reportagem, Vorcaro mandou deixar o assunto de lado (em fala indireta, sem transcrição literal). A Folha afirma não ter registro de ataques; nenhum acesso está tecnicamente demonstrado na reportagem.",
            date="2024-09-25", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00100", g5)

g6 = [
    bbc_msg("m-00102", M, "Os meninos invaderam a revista piauí… Manda deletar os links e todas as matérias?",
            "Em 23/10/2025, conforme a BBC; Mourão disse em seguida que aguardava aprovação — não há resposta de Vorcaro autorizando a ação nem demonstração técnica do acesso. A piauí afirmou (29/09/2026) não ter identificado problema no site naquele dia.",
            date="2025-10-23", precision="date"),
]
t["messages"] = insert_after(t["messages"], "m-00032", g6)

t["timeline_events"].append(make_event(
    "e-00007",
    "Contexto BBC News Brasil (23/10/2026): levantamento da BBC identificou ao menos 189 pedidos de Vorcaro a Felipe Mourão para remover conteúdos entre 2023 e 2025, incluindo relatos de que ao menos 17 perfis e publicações do Instagram teriam sido derrubados — alegações de Mourão, sem demonstração técnica de como ocorreram. A série inclui: pedido de derrubada do blog Nem Amigo Nem Inimigo (31/01/2024) e recusa de proposta de “tomar” o site; pedido de derrubada de links da Folha (02/09/2024) e proposta de acessar o sistema do jornal para apagar o backup (25/09/2024), depois abandonada a mando de Vorcaro; alegação de invasão ao site da revista piauí (23/10/2025) sem resposta autorizando. A Folha negou ter registro dos ataques; a piauí não identificou problema no episódio; a BBC não demonstrou tecnicamente nenhum acesso realizado. A BBC relata ainda buscas de dados sobre autores de publicações e terceiros (TechBusca, site de busca de dados bloqueado pela Justiça em 2022, e Saftec) — mensagens com dados pessoais de terceiros monitorados não são reproduzidas neste arquivo. Caso anterior da jornalista que monitorava o jatinho de Vorcaro (já reportado pela BBC) não é duplicado aqui.",
    SEC_BBC, "Relato de BBC News Brasil (2026-10-23)"))
save(p, t)
print(f"[ok] felipe-mourao: {len(t['messages'])} mensagens (87→102), +1 evento")

# =====================================================================
# threads.json — atualização de contagens
# =====================================================================
ip = os.path.join(DATA, "threads.json")
idx = json.load(open(ip, encoding="utf-8"))
counts = {
    "luiz-renno-daniel-vorcaro": 20,
    "flavio-carneiro-daniel-vorcaro": 26,
    "ana-matos-daniel-vorcaro": 53,
    "paulo-sergio-daniel-vorcaro": 5,
    "felipe-mourao-daniel-vorcaro": 102,
}
for e in idx:
    if e["id"] in counts:
        e["message_count"] = counts[e["id"]]
save(ip, idx)
print("[ok] threads.json atualizado (contagens)")

