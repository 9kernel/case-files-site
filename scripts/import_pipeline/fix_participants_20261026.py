# -*- coding: utf-8 -*-
"""fix_participants_20261026.py — correções de participantes (auditoria 26/10/2026).

- leonardo-valverde: NÃO foi presidente do BRB (cargo de Paulo Henrique Costa
  à época); corrigido papel e resumo conforme UOL (21/10/2026).
- netinho-lins: festival corrigido para Campo Formoso (BA), 5–7/09/2024;
  removidas alegações de Angatuba (SP)/setembro de 2025 e saída de R$ 2
  milhões sem suporte.
- elmar-nascimento: cronologia corrigida (entrega 02/10/2024; agradecimento
  03/10/2024; resultado 07/10/2024).
- paulo-sergio: acrescentada a fonte Folha (22/10/2026) com ressalva de
  identificação.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
path = os.path.join(ROOT, "data", "participants.json")
participants = json.load(open(path, encoding="utf-8"))
by_id = {p["id"]: p for p in participants}

UOL22 = "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/22/deputado-agradece-vorcaro-por-salvar-a-patria-apos-entrega-na-eleicao.htm"
UOL21 = "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/21/ibaneis-pilotou-operacao-brb-master-e-vorcaro-fala-em-propina-de-r-80-mi.htm"
FOLHA = "https://c-level.folha.uol.com.br/financas/2026/10/vorcaro-pediu-a-ex-diretor-do-bc-que-pressionasse-caixa-em-caso-de-aporte-barrado-no-master.shtml"

by_id["leonardo-valverde"]["role"] = ("Então “braço direito” do governador do DF Ibaneis Rocha, segundo descrição "
                                      "da PF no relato do UOL; não exerceu a presidência do BRB")
by_id["leonardo-valverde"]["summary"] = (
    "[Corrigido 2026-10-26: a versão anterior o descrevia como ex-presidente do BRB — cargo exercido por Paulo "
    "Henrique Costa; ver participante próprio.] Presente, segundo a PF, ao almoço de setembro de 2024 na casa de "
    "Vorcaro em que se discutiu o acerto da operação BRB-Master, descrito como “braço direito do gov” (Ibaneis "
    "Rocha). Na delação de Vorcaro, alega-se que teria recebido cerca de R$ 80 milhões em espécie entregues pelo "
    "motorista do banqueiro — alegação do delator, sem confirmação publicada. Em outubro de 2024, enviou a Vorcaro "
    "a proposta “Segue as empresas!”, com CNPJ e dados bancários de empresa que administra (documento não "
    "reproduzido), conforme o UOL. Procurado, não respondeu. Perfil resumido exclusivamente a partir das fontes "
    "linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")
by_id["leonardo-valverde"]["profile_sources"] = [
    {"label": "UOL — coluna Natália Portinari, 21/10/2026", "url": UOL21},
]

by_id["netinho-lins"]["aliases"] = ["Netinho", "Nettinho Bet"]
by_id["netinho-lins"]["summary"] = (
    "[Corrigido 2026-10-26: a versão anterior situava o festival em Angatuba (SP) em setembro de 2025 e citava "
    "saída de R$ 2 milhões de conta do Master em 10/10/2024 — sem suporte na fonte; removido.] Apresentador e "
    "empresário de eventos, investigado na Operação Overclean (PF). Coordenou o 3º Festival das Esmeraldas, "
    "realizado de 5 a 7/09/2024 em Campo Formoso (BA), cidade do então prefeito Elmo Nascimento, irmão do deputado "
    "Elmar Nascimento; o patrocínio “Ouro” de R$ 1 milhão de Vorcaro foi quitado por Pix da Super Empreendimentos "
    "e Participações à sua empresa DuBem Business Marketing, conforme comprovante enviado à reportagem. Salvo no "
    "celular de Vorcaro como “Nettinho Bet”. Perfil resumido exclusivamente a partir das fontes linkadas; não "
    "constitui acusação nem conclusão sobre responsabilidade individual.")
by_id["netinho-lins"]["profile_sources"] = [
    {"label": "UOL — coluna Natália Portinari, 22/10/2026", "url": UOL22},
]

by_id["elmar-nascimento"]["summary"] = (
    "[Corrigido 2026-10-26: cronologia anterior (entrega em 24/10/2024 às 23h27; agradecimento em 25/10/2024 às "
    "9h30 com transcrição diversa) não correspondia à fonte.] Deputado federal (União-BA). Em agosto de 2024, "
    "pediu a Vorcaro apoio ao 3º Festival das Esmeraldas, na sua terra, Campo Formoso (BA), então governada por "
    "seu irmão Elmo Nascimento. Segundo o UOL, na noite de 01/10/2024 pediu o contato de “a pessoa que vai ser "
    "procurada”; um volume foi entregue pelo motorista de Vorcaro às 19h11 de 02/10/2024 (conteúdo não identificado "
    "pela reportagem), e Elmar agradeceu na tarde de 03/10/2024: “Vc salvou a Pátria”. Após a eleição de 06/10/2024, "
    "relatou 35 prefeitos eleitos. A PF apura a entrega; Elmar não respondeu ao UOL. Perfil resumido exclusivamente "
    "a partir das fontes linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")
by_id["elmar-nascimento"]["profile_sources"] = [
    {"label": "UOL — coluna Natália Portinari, 22/10/2026", "url": UOL22},
]

ps = by_id["paulo-sergio"]
ps["summary"] = (
    "Identificado no IPJ-A nº 3298613/2026 (PET 16662/STF) como “Diretor do Banco Central” — contato de Vorcaro a "
    "quem escreveu, em 19/03/2025, que estava “com Moraes aqui”. A Folha (22/10/2026) publica diálogos de julho de "
    "2024 entre Vorcaro e Paulo Sérgio Neves de Souza, ex-diretor do BC, sobre posicionamento público da Caixa no "
    "caso Master; a correspondência entre o contato do IPJ-A e o ex-dirigente citado pela Folha é plausível, mas "
    "não individualmente demonstrada nos documentos públicos disponíveis — os registros de julho de 2024 desta "
    "conversa trazem essa ressalva. Souza disse à Folha que jamais protegeu interesses de Vorcaro; o BC e a defesa "
    "não comentaram; a Caixa informou que a aplicação de R$ 500 milhões da Caixa Asset no Master não ocorreu. Não "
    "confundir com o “Paulo” das notas de Vorcaro, associado pelo relatório a Paulo Gonet (PGR).")
if not any(s["url"] == FOLHA for s in ps.get("profile_sources", [])):
    ps["profile_sources"].append({"label": "Folha C-Level — 22/10/2026", "url": FOLHA})

with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(participants, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("[ok] participants.json corrigido: leonardo-valverde, netinho-lins, elmar-nascimento, paulo-sergio")
