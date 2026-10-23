# curate_press_v11.py — Agência Pública 15/10 (Kachar/Malu) + CartaCapital 21/09 (Dark Horse)
"""Rodada de complementação:

- frederic-kachar +22 (Agência Pública, 15/10/2026, Ed Wanderley e Thiago
  Domenici): correção do G1 de 31/05/2024, entrevista no Valor (abr/2024),
  capa Vogue para Martha (12/10/2024), patrocínios fev/2025 e a reação à
  análise do Valor de 29/03/2025. Duas quase-duplicatas descartadas no dedupe
  ('ficaram ótimas', 'próximo passo é uma capa' — variantes já cadastradas
  pela apuração do UOL).
- thiago-miranda +6 (CartaCapital, 21/09/2026): cobranças do Dark Horse de
  06/02, 12/03 e 18/08/2025. INCONSISTÊNCIA TEMPORAL documentada: a mensagem
  'Hoje é a data limite daquele primeiro aporte filme' consta 20/01 na fonte
  original da thread e 19/01 na CartaCapital — divergência anotada no
  registro, data original mantida.
- fabiano-zettel +20 (mesma CartaCapital): fluxo financeiro do filme
  jan-mar/2025 (empresa pagadora, câmbio, TED, Entre/Mineiro).
- Malu Gaspar (mar-abr/2025): falas de Vorcaro/Miranda e de Kachar publicadas
  em fala indireta pela Agência Pública — registradas como EVENTOS com as
  citações atribuídas, sem dados pessoais da jornalista e sem presumir que
  buscas tenham sido executadas.

Níveis: Agência Pública amarra o material às mensagens interceptadas pela PF
(→ public_investigation + proceeding); CartaCapital não ata a origem a
procedimento no trecho lido (→ secondary_source).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press7-20261016"
T = REPO / "data" / "threads"

AP = ("Agência Pública (Ed Wanderley e Thiago Domenici)", "2026-10-15",
      "https://apublica.org/2026/10/a-linha-direta-de-vorcaro-dentro-do-grupo-globo-quer-que-peca-pra-corrigir/")
CC = ("CartaCapital", "2026-09-21",
      "https://www.cartacapital.com.br/politica/pressao-para-liberar-recursos-a-dark-horse-foi-intensa-e-constante-revelam-mensagens-de-vorcaro/")

GERAL = "Operação Compliance Zero — PF/STF (material do celular de Vorcaro, reportado pela imprensa)"

VER_PI = {"level": "public_investigation", "origin": "press report", "authority": "Polícia Federal",
          "court": None, "case": None, "document": None, "page": None, "figure": None,
          "official_url": None, "primary_document_located": False, "verified_at": "2026-10-16",
          "proceeding": GERAL}
VER_SS = {"level": "secondary_source", "origin": "press report", "authority": None,
          "court": None, "case": None, "document": None, "page": None, "figure": None,
          "official_url": None, "primary_document_located": False, "verified_at": "2026-10-16"}


def norm(s):
    return re.sub(r"\W", "", (s or "").lower())[:45]


def prec_of(date):
    return "month" if date and len(date) == 7 else ("date" if date else None)


def secs(src):
    return [{"publication": src[0], "date": src[1], "url": src[2]}]


def new_msg(date, sender, content, note, src, ver):
    m = {
        "id": "m-TEMP", "date": date,
        "sender_id": sender, "content_kind": "verbatim_excerpt",
        "content": content,
        "editorial_note": note or "Citação literal conforme transcrita pela reportagem indicada nas fontes.",
        "verification": dict(ver),
        "sources": {"primary": None, "secondary": secs(src)},
        "source_ref": f"Mensagem divulgada por {src[0]} ({src[1]})",
        "added_in": ADDED_IN,
    }
    if date:
        m["time"] = None
        m["timestamp_precision"] = prec_of(date)
    if "[" in content or "(…)" in content:
        m["literal_brackets"] = True
    return m


def new_event(date, content, src, ver):
    e = {
        "id": "e-TEMP", "date": date,
        "content": content, "event_kind": "editorial_context",
        "verification": dict(ver),
        "sources": {"primary": None, "secondary": secs(src)},
        "source_ref": f"Relato de {src[0]} ({src[1]})",
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


KACHAR = [
    ("2024-04", "frederic-kachar", "Quer que a gente o entreviste no Valor?", None),
    ("2024-04", "frederic-kachar", "Não sabia que a Veste tinha esse ceo", None),
    ("2024-05-31", "frederic-kachar", "Entrou em supermercados também? Estás incontrolável rs!",
     "Sobre reportagem do G1 envolvendo o Banco Master e o setor de supermercados, segundo a reportagem."),
    ("2024-05-31", "daniel-vorcaro", "Info totalmente errada", None),
    ("2024-05-31", "frederic-kachar", "Quer que eu peça pra corrigir?", None),
    ("2024-05-31", "daniel-vorcaro", "Deve!", None),
    ("2024-05-31", "daniel-vorcaro", "Agora ficou certo",
     "Após a atualização do texto, segundo a reportagem — a correção da matéria está registrada em evento."),
    ("2024-07", "daniel-vorcaro", "amizade que supera negócios",
     "Fragmento: assim definiu a relação, em julho/2024, segundo a reportagem."),
    ("2024-10-12", "daniel-vorcaro", "De presente pra ela",
     "Ao pedir capa da Vogue para Martha Graeff, segundo a reportagem."),
    ("2024-10", "frederic-kachar", "Depois me diz se faltou algo",
     "Ao enviar os links das publicações sobre Martha Graeff, segundo a reportagem."),
    ("2024-10", "daniel-vorcaro", "só a Marie Claire deu uma batidinha no final rsrs esses repórteres são uma bênção",
     "Sobre as matérias publicadas; a reportagem do UOL registrara a reclamação em versão resumida ('deu uma batidinha no final')."),
    ("2025-02", "frederic-kachar", "Vamos poder curtir juntos amanhã?", None),
    ("2025-02", "frederic-kachar", "Querido, me dá um sinal de vida pra eu não ir e dar com a cara na porta rs?", None),
    ("2025-02", "frederic-kachar", "Para não te deixar na mão, te bonifico um branded content [...] da marca na Glamour e na Vogue [Brasil]",
     "Colchetes e reticências constam da transcrição da reportagem."),
    ("2025-02-25", "frederic-kachar", "fez falta no sábado", None),
    ("2025-02-25", "frederic-kachar", "Estou no voo com Lauro [Jardim], que vai conhecer sua sede nova antes de mim.",
     "Colchete consta da transcrição da reportagem."),
    ("2025-03-29", "daniel-vorcaro", "Matéria maldosa, malfeita. Isso é porque seu grupo deu o furo da operação. Parceria, como sempre, de uma via apenas",
     "Sobre a análise do Valor Econômico de 29/03/2025 sobre a negociação entre BRB e Master, segundo a reportagem."),
    ("2025-03-29", "daniel-vorcaro", "Com toda a liberdade de desabafo, me sinto por varias vezes um bobo focando na parceria aí", None),
    ("2025-03-29", "frederic-kachar", "O que concordo com você é que não poderia fazer análise sem sua visão do 'deal' e já reclamei", None),
    ("2025-03-29", "frederic-kachar", "Meu amigo, claro que não é pra ficar como está. Se a gente discorda em algumas coisas, temos de conversar", None),
    ("2025-03-29", "frederic-kachar", "O Álvaro [Campos] incluiu aspas suas nessa análise. Vamos falar amanhã?",
     "Duas horas depois; colchete consta da transcrição da reportagem."),
    ("2025-03-29", "daniel-vorcaro", "Não vale a pena pra mim falar. Vira (sic) o caso Malu [Gaspar]. Tudo que eu falo usam contra mim.",
     "'(sic)' e colchete constam da transcrição; referência ao episódio registrado em evento na conversa com Thiago Miranda."),
]
KACHAR_EVENTS = [
    ("2024-05-31", "Após o pedido de Vorcaro, a reportagem do G1 sobre o Master e o setor de supermercados foi corrigida/atualizada — 'Agora ficou certo', registrou o banqueiro."),
    ("2025-02", "Propostas de fevereiro/2025: R$ 1,79 milhão em participação e R$ 4,92 milhões para camarote na Sapucaí; Vorcaro pagou R$ 1,3 milhão pelos dois eventos, segundo a reportagem."),
    (None, "Falas de Kachar sobre a jornalista Malu Gaspar, publicadas em fala indireta: 'a Malu é livre. Ninguém a escala'; 'Eu não gosto do que ela postou, por isso reforcei que a cobertura do Globo é a que está no site'; sobre a piauí, que 'virou denuncista'. Sobre a independência dos jornalistas, a Agência Pública trata as interferências como apontadas pelas mensagens interceptadas pela PF — não como conclusão judicial."),
    (None, "Notas: a defesa de Vorcaro disse que se manifestaria após depoimento (sobre outras mensagens, afirmou que foram tiradas de contexto e que jamais determinou violência); Kachar não retornou; Álvaro Campos e Malu Gaspar preferiram não comentar; a nota do Grupo Globo sobre a demissão já está registrada no evento de 15/10/2026."),
]

ZETTEL = [
    ("2025-01-20", "fabiano-zettel", "O cara do 'filme' não sai da minha cola. Me mandou um fluxo gigante!", None),
    ("2025-01-21", "fabiano-zettel", "Irmão, fala comigo! Me dá um norte? Mesmo que seja 'não faz porra nenhuma até eu voltar'", None),
    ("2025-01", "fabiano-zettel", "Não. Porque o fluxo é gigante… 10 de 2.5 de dólares",
     "Resposta sobre a inclusão do filme no fluxo de R$ 55,5 milhões, segundo a reportagem."),
    ("2025-01", "daniel-vorcaro", "Não pode falhar mais",
     "Dias depois, definindo o filme como 'o mais importante disparado', segundo a reportagem."),
    ("2025-01-29", "fabiano-zettel", "A empresa que eu criei não tem cadastro suficiente pra mandar os câmbios do filme. Posso mandar Super?",
     "Sobre a identificação da empresa pagadora; em 30/01, o repasse tratado seria de 2 milhões de dólares, segundo a reportagem."),
    ("2025-01-29", "daniel-vorcaro", "Nossa senhora", None),
    ("2025-01-31", "fabiano-zettel", "preciso saber do filme",
     "Às 8h35, segundo a reportagem."),
    ("2025-01-31", "daniel-vorcaro", "vc fez o filme?",
     "Horas depois, cobrando, segundo a reportagem."),
    ("2025-01-31", "fabiano-zettel", "Amigo, Não faz assim que me dá dor de barriga. Estamos esperando você definir a empresa…", None),
    ("2025-02-03", "daniel-vorcaro", "Como ssim? Não fez sl? Nem filme", None),
    ("2025-02-03", "fabiano-zettel", "Amigo, Não faz assim comigo!! Eu te escrevo todo dia!! – preciso da empresa do filme. preciso liberar SL. Hoje vc mandou: Faz só esse!", None),
    ("2025-02-03", "daniel-vorcaro", "precisamos câmbio sl, filme", None),
    ("2025-02-03", "fabiano-zettel", "Libera a TED então.. E me fala que empresa faz filme", None),
    ("2025-02-03", "fabiano-zettel", "Mandei carta de 34M: – SL – Filme – Despesas", None),
    ("2025-02-05", "daniel-vorcaro", "e manda a grana",
     "Na sugestão de fazer a operação 'via Entre' (Entre Investimentos, do 'Mineiro'), com Zettel pedindo 'pro Minas', segundo a reportagem."),
    ("2025-02-05", "daniel-vorcaro", "Fundo? Vc não me deu noticia",
     "Após a resposta de que o pagamento lá fora seria a 'um fundo', segundo a reportagem."),
    ("2025-02-11", "daniel-vorcaro", "Preciso resolver HOJE. E possível", None),
    ("2025-02-11", "fabiano-zettel", "Passei pro Mineiro. Ele também estava com dificuldades. Tô na cola dele. Mas se vc mandar mensagem, me ajuda muito…", None),
    ("2025-02-11", "daniel-vorcaro", "Cara nao e possível. Não acredito", None),
    ("2025-03-12", "fabiano-zettel", "Vou pra cima do Mineiro. Passei o fluxo pra ele. Achei que ele tava fazendo.", None),
    ("2025-03-12", "daniel-vorcaro", "Precisa me ajudar controlae isso. Tem que pagar a segunda e a terceira",
     "Erro de digitação ('controlae') consta da transcrição; sobre as parcelas seguintes, segundo a reportagem."),
]
ZETTEL_EVENTS = [
    ("2025-02-11", "Zettel relata que o câmbio recusava a operação por cadastro e que 'as informações são meio estranhas…' — obstáculos cambiais descritos pela reportagem."),
    ("2025-02-14", "Documento citado pela reportagem: PDF com comprovante de transferência de US$ 2 milhões da Entre Investimentos e Participações (de Antonio Carlos Freixo Júnior, o 'Mineiro') ao Havengate Development Fund LP (Texas/EUA, ligado ao advogado Paulo Calixto, aliado de Eduardo Bolsonaro, segundo a reportagem)."),
    (None, "Contexto da reportagem: fluxo de R$ 55,5 milhões; 'carta de 34M'; mais de R$ 60 milhões pagos no acerto de cerca de R$ 134 milhões. A PF investiga lavagem de dinheiro, evasão de divisas e corrupção, com Flávio Bolsonaro citado como possível envolvido, em tese; a reportagem não registra defesa de Vorcaro ou de Flávio Bolsonaro (que teria minimizado a intensidade da pressão)."),
]

MIRANDA = [
    ("2025-02-06", "thiago-miranda", "Sobre o filme tá parado não andou, consegue liberar essa pauta com o Fabiano? Eles estão me cobrando", None),
    ("2025-02-06", "daniel-vorcaro", "Questão que já devolveram duas vezes. Estamos com problemas pra fazer o cambio e olha que estou fazendo interno", None),
    ("2025-02-06", "daniel-vorcaro", "Eu acho que hj resolvo se não der te aviso", None),
    ("2025-03-12", "thiago-miranda", "Sobre o filme só foi pago a primeira de janeiro",
     "Informação sobre parcelas não pagas, atribuída ao interlocutor; transferências efetivas só as documentadas em evento."),
    ("2025-08-18", "thiago-miranda", "Pessoal do filme me cobrou hoje. Não caiu as parcelas semana passada. Pode ver isso. Pfv. Acho que te lembrei já era no meio da semana", None),
    ("2025-08-18", "daniel-vorcaro", "pede desculpas os atrasos meu esforço tem sido máximo possível e prioridade total. Apesar de qq tempestade vou ate o fim com isso",
     "Transcrição da CartaCapital; mensagem de teor semelhante em 22/10/2025 (outra fonte) já consta nesta conversa."),
]
MIRANDA_EVENTS = [
    (None, "Março-abril/2025 (falas atribuídas pela Agência Pública, em fala indireta): Vorcaro disse que precisavam 'encontrar algo dessa mulher [Malu Gaspar] no pessoal'; Thiago Miranda respondeu não ter encontrado 'nem uma multa na CNH'. Não há comprovação de que buscas tenham sido executadas; dados pessoais da jornalista não são reproduzidos."),
]


def main():
    # Kachar
    t = load("frederic-kachar")
    have = {norm(m["content"]) for m in t["messages"]}
    added = skipped = 0
    for date, sender, content, note in KACHAR:
        if norm(content) in have:
            skipped += 1
            continue
        t["messages"].append(new_msg(date, sender, content, note, AP, VER_PI))
        added += 1
    for d, c in KACHAR_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, AP, VER_PI))
    finalize(t)
    save("frederic-kachar", t)
    print(f"[v11] frederic-kachar: +{added} msgs ({skipped} descartadas por duplicidade), ev {len(t['timeline_events'])}")

    # Zettel
    t = load("fabiano-zettel")
    have = {norm(m["content"]) for m in t["messages"]}
    added = 0
    for date, sender, content, note in ZETTEL:
        if norm(content) in have:
            continue
        t["messages"].append(new_msg(date, sender, content, note, CC, VER_SS))
        added += 1
    for d, c in ZETTEL_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, CC, VER_SS))
    finalize(t)
    save("fabiano-zettel", t)
    print(f"[v11] fabiano-zettel: +{added} msgs (total {len(t['messages'])})")

    # Miranda
    t = load("thiago-miranda")
    have = {norm(m["content"]) for m in t["messages"]}
    added = 0
    for date, sender, content, note in MIRANDA:
        if norm(content) in have:
            continue
        t["messages"].append(new_msg(date, sender, content, note, CC, VER_SS))
        added += 1
    for d, c in MIRANDA_EVENTS:
        t.setdefault("timeline_events", []).append(new_event(d, c, AP, VER_PI))
    # inconsistência temporal: 'data limite do aporte' 20/01 (fonte original) vs 19/01 (CartaCapital)
    for m in t["messages"]:
        if m["content"].startswith("Hoje é a data limite"):
            m["editorial_note"] = ((m.get("editorial_note") or "").rstrip()
                                   + " [Divergência temporal entre fontes: a CartaCapital (21/09/2026) data esta mensagem "
                                     "em 19/01/2025; a fonte original desta thread registra 20/01/2025 — data mantida, "
                                     "divergência documentada.]")
    finalize(t)
    save("thiago-miranda", t)
    print(f"[v11] thiago-miranda: +{added} msgs (total {len(t['messages'])}), divergência 19-20/01 anotada")

    # índice
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    for entry in index:
        fp = T / f"{entry['id']}.json"
        if not fp.exists():
            continue
        th = json.loads(fp.read_text(encoding="utf-8"))
        if entry["message_count"] != len(th["messages"]):
            entry["message_count"] = len(th["messages"])
            entry["last_message_preview"] = th["messages"][-1]["content"][:80]
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("[v11] índice atualizado")


if __name__ == "__main__":
    main()
