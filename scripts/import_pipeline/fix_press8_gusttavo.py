# -*- coding: utf-8 -*-
"""fix_press8_gusttavo.py — correções na conversa gusttavo-lima-daniel-vorcaro.

Conforme auditoria de 26/10/2026 e confronto com a fonte original
(Agência Pública, 21/10/2026):
- m-00001: nota editorial corrigida — a reportagem do Fantástico (09/09/2024)
  tratava de bloqueio de R$ 20 milhões e sequestro de bens da BALADA EVENTOS,
  empresa de Gusttavo Lima, investigada pela Polícia Civil de Pernambuco por
  lavagem ligada a jogos de azar — e não de Vorcaro.
- m-00005: "[nos]" é inserção do veículo; removido do conteúdo literal e
  registrado em nota; literal_brackets removido (colchetes não constam do
  original).
- m-00006: transcrição completada com o restante do trecho publicado do áudio
  de 9 segundos ("Tá doido?! Vai me matar de saudade").
- m-00016: "[de]" é inserção do veículo; mesmo tratamento de m-00005.
Transcrição literal de m-00001–m-00004, datas e demais campos preservados.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
path = os.path.join(ROOT, "data", "threads", "gusttavo-lima-daniel-vorcaro.json")
t = json.load(open(path, encoding="utf-8"))
by_id = {m["id"]: m for m in t["messages"]}

# m-00001 — correção do contexto editorial
m = by_id["m-00001"]
m["editorial_note"] = ("[Corrigido 2026-10-26: a versão anterior afirmava que a reportagem do Fantástico "
                       "tratava de Vorcaro.] No dia anterior (09/09/2024), o Fantástico (TV Globo) mostrou que a "
                       "Justiça determinou bloqueio de R$ 20 milhões e sequestro de imóveis e embarcações da "
                       "empresa Balada Eventos, de Gusttavo Lima, investigada pela Polícia Civil de Pernambuco "
                       "por suspeita de lavagem de dinheiro proveniente de jogos de azar; no dia seguinte, Lima "
                       "buscou contato com Vorcaro, segundo a reportagem.")

# m-00005 — colchete editorial "[nos]" separado do conteúdo literal
m = by_id["m-00005"]
m["content"] = "Saudades de ti. Vamos encontrar para avançar nos temas"
m.pop("literal_brackets", None)
m["editorial_note"] = ("[Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado pela "
                       "Agência Pública como “Vamos [nos] encontrar para avançar nos temas”; o “[nos]” é inserção "
                       "do veículo, não constando do original, e foi removido do campo literal.")

# m-00006 — transcrição do áudio completada conforme o trecho publicado
m = by_id["m-00006"]
m["content"] = "Uai, urgente, bebê. Cheguei, tô no Brasil, cheguei hoje. Saudades, cara. Tá doido?! Vai me matar de saudade"
m["editorial_note"] = ("[Corrigido 2026-10-26: transcrição completada com o restante do trecho publicado.] "
                       "Trecho integral do áudio de 9 segundos transcrito pela reportagem, em resposta à mensagem "
                       "anterior de 28/10/2024; nada além do trecho publicado foi reconstruído.")

# m-00016 — colchete editorial "[de]" separado do conteúdo literal
m = by_id["m-00016"]
m["content"] = "meio pagamento. Bora explodir ele. Super BH"
m.pop("literal_brackets", None)
m["editorial_note"] = ("[Corrigido 2026-10-26: colchete editorial separado do conteúdo literal.] Publicado pela "
                       "Agência Pública como “meio [de] pagamento. Bora explodir ele. Super BH”; o “[de]” é "
                       "inserção do veículo, não constando do original, e foi removido do campo literal. No dia "
                       "seguinte ao áudio das taxas, segundo a reportagem; data não divulgada.")

with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("[ok] gusttavo-lima corrigido (m-00001, m-00005, m-00006, m-00016)")
