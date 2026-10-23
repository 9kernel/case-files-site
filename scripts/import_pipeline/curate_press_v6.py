# curate_press_v6.py — rodada UOL 13-15/10/2026 (tabela do editor)
"""11 conversas novas + 2 complementações, todas de apurações do UOL.

Regras aplicadas (das rodadas anteriores):
- só é MENSAGEM o que a reportagem cita literalmente entre aspas; fragmentos
  citados dentro de fala indireta entram como verbatim_excerpt com nota;
  fragmentos muito curtos ficam apenas em eventos;
- relatos viram eventos editoriais; defesas sempre registradas;
- datas/horas só quando a reportagem informa (month -> precision month);
  referências só de ano ('em 2024') ficam sem data, com nota.

TRIAGEM DE SENSIBILIDADE (instrução do editor para os diálogos com possível
exploração sexual — Diogo Batista, Leonardo Serrano, Tiago Polo):
- publicamos apenas trechos de interesse público: estrutura do esquema
  (compra da Allure, vistos, faturas, empresas, controle de pagamentos),
  escala dos eventos e o recrutamento/retenção de refugiadas — núcleo da
  investigação preliminar da PF;
- EXCLUÍMOS deliberadamente: alcunhas e vocabulário degradantes ('escravas',
  'kengas', 'creche'), avaliações sexuais explícitas e o episódio
  individualizado da jovem de 19 anos ('Mucilon'), para preservar a
  dignidade e a privacidade das pessoas vulneráveis;
- nenhuma mulher é identificada por nome; onde a reportagem elide, mantemos
  a elisão entre colchetes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-press4-20261016"
T = REPO / "data" / "threads"

TAHAN = ("UOL (Renata Agostini e Tiago Dantas)", "2026-10-15",
         "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/vorcaro-editava-textos-do-site-metropoles-antes-de-irem-ao-ar.htm")
KACHAR = ("UOL (Renata Agostini e Tiago Dantas)", "2026-10-15",
          "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/grupo-globo-demite-diretor-geral-apos-vazamento-de-conversas-com-vorcaro.htm")
TEMER_UOL = ("UOL (apuração de O Globo)", "2026-10-14",
             "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/14/escritorio-de-temer-negociou-contrato-de-ate-r-30-milhoes-com-master.ghtm")
REDE = ("UOL (Renata Agostini e Tiago Dantas)", "2026-10-15",
        "https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/15/brazil-journal-istoe-como-vorcaro-montou-rede-de-influencia-em-sites.htm")
FEBRABAN = ("UOL — coluna Natália Portinari", "2026-10-15",
            "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/15/vorcaro-pagou-parte-de-imovel-de-r-73-mi-para-presidente-da-febraban.ghtm")
TRIO = ("UOL — coluna Natália Portinari", "2026-10-13",
        "https://noticias.uol.com.br/colunas/natalia-portinari/2026/10/13/vorcaro-era-socio-oculto-de-agencia-de-prostituicao-e-recrutou-refugiadas.ghtm")

VER = {"level": "public_investigation", "origin": "press report",
       "authority": "Polícia Federal", "court": None, "case": None,
       "document": None, "page": None, "figure": None, "official_url": None,
       "primary_document_located": False, "verified_at": "2026-10-16"}

SENSITIVE_NOTE = ("Curadoria restrita: publicados apenas os trechos de interesse público "
                  "(estrutura, pagamentos e o recrutamento de refugiadas); vocabulário "
                  "degradante e detalhes que individualizem mulheres vulneráveis foram "
                  "deliberadamente excluídos.")

# ---------------------------------------------------------------- conversas novas
THREADS = {
  "lilian-tahan": {
    "title": "Lilian Tahan",
    "src_note": ("UOL (Renata Agostini e Tiago Dantas), 15/10/2026: mensagens da PF mostram "
                 "Vorcaro com linha direta com a CEO do grupo Metrópoles — pelo menos 14 textos "
                 "enviados a ele antes de publicados, 11 alterados a pedido e 2 reportagens "
                 "publicadas a pedido do dono do Master. Contratos: R$ 1 milhão (jun/2024), "
                 "R$ 900 mil (jul/2024, Kovr/Will) e R$ 20 milhões (nov/2024). Defesa de Tahan "
                 "registrada nos eventos."),
    "secs": [TAHAN],
    "msgs": [
      (None, None, "lilian-tahan", "Se tiver alguma incorreção, me avise!! Não publicarei sem nos falarmos",
       "Ao enviar a Vorcaro, antes da publicação, perfil sobre ele, segundo a reportagem."),
      ("2024-11", None, "lilian-tahan", "Tá caro esse Metrópoles", "Sobre a proposta do contrato, segundo a reportagem."),
      ("2024-11", None, "daniel-vorcaro", "Coisa mais importante [da] nossa vida é esse Metrópoles",
       "Resposta na mesma sequência; colchete consta da transcrição da reportagem."),
      ("2024-11", None, "daniel-vorcaro", "Dei ok pra Lilian", "Dois dias depois, autorizando o contrato, segundo a reportagem."),
      ("2025-04-02", None, "daniel-vorcaro", "Proposta de 1 real nunca existiu!", None),
      ("2025-04-02", None, "lilian-tahan", "Tiramos", "Resposta na mesma sequência, segundo a reportagem."),
      ("2025-04-09", None, "lilian-tahan", "Aí depois se quiser eu comento como chegou", None),
      ("2025-04-10", None, "lilian-tahan", "Me diga o que acha: um comparativo entre o balanço dos bancos. Ajuda ou atrapalha?",
       "Sugestão de pauta enviada a Vorcaro, segundo a reportagem."),
      ("2025-04-10", None, "daniel-vorcaro", "Pode ser bom! Eu conseguiria dar uma olhada antes pra checar os dados", None),
      ("2025-04-10", None, "lilian-tahan", "Claro!", "Resposta na mesma sequência, segundo a reportagem."),
      ("2025-05", None, "daniel-vorcaro", "Pode retirar Hapvida do texto?",
       "Pedido de edição sobre reportagem do BTG, segundo a reportagem."),
      ("2025-08", None, "daniel-vorcaro", "Acho que o texto ta otimo. Mas eu nao falaria tanto do renato, concentraria essa materia no roberto. Senao perdemos o suspense da batida dele! Guardaria essa parte do texto sobre o renato pra materia dele!",
       "Sobre texto envolvendo Campos Neto e o diretor do BC Renato Gomes, segundo a reportagem."),
      ("2025-08", None, "daniel-vorcaro", "Eu retiraria a parte de falência do banco",
       "Sobre o perfil de Renato Gomes publicado pelo Metrópoles, segundo a reportagem."),
      ("2025-08", None, "daniel-vorcaro", "Esse Cappelli, você não consegue dar uma freada essa semana? Depois ele volta!",
       "Pedido de redução de cobertura sobre Ricardo Cappelli (ABDI), segundo a reportagem."),
      ("2025-08", None, "lilian-tahan", "Deixa comigo", "Resposta na mesma sequência, segundo a reportagem."),
      ("2025-11-17", None, "lilian-tahan", "Publicada hahahaha",
       "No dia da prisão de Vorcaro, após publicar matéria sobre a venda à Fictor, segundo a reportagem."),
    ],
    "events": [
      ("2024-05", "O consultor Guilherme Barros apresenta Vorcaro a Lilian Tahan; no dia seguinte escreve ao banqueiro: 'A Lilian gostou muito de vc. Foi muito bom ter te colocado com o Luis Estevão. Eu tenho o contato dele, mas acho melhor ela mesma fazer essa ponte, concorda?'. Metrópoles pertence ao ex-senador Luiz Estevão, condenado a 31 anos por desvio de recursos públicos.", TAHAN),
      (None, "Pagamentos do grupo ao Metrópoles: R$ 1 milhão (junho/2024), R$ 900 mil para 'educação financeira' da Kovr e do Will (julho/2024) e contrato de R$ 20 milhões (novembro/2024), quitado em 2025 em parcelas de R$ 5 milhões. Funcionária perguntou a Vorcaro: 'O valor que fechamos com o Metrópoles (20 mi) eu faço todo no CNPJ banco ou divido com Kovr e Will?'.", TAHAN),
      (None, "Pelo menos 14 textos foram enviados a Vorcaro antes de irem ao ar; 11 foram alterados a pedido dele e 2 reportagens publicadas a pedido do dono do Master, segundo a reportagem.", TAHAN),
      (None, "Em resposta escrita, Tahan afirma que checar com a fonte 'se a matéria reflete o contexto passado para o veículo' é prática adotada com empresários, políticos e Judiciário; nega vínculo entre o contrato de publicidade e a cobertura, citando matérias do Metrópoles que expuseram problemas de Master, Ambipar, Fictor e Oncoclínicas; sobre Renato Gomes, diz que era 'personagem relevante' por se opor à compra pelo BRB; sobre Cappelli, afirma que Luiz Estevão sempre foi crítico da compra do Master pelo BRB e forneceu a Cappelli análises sobre os balanços do BRB.", TAHAN),
    ],
  },
  "frederic-kachar": {
    "title": "Frederic Kachar",
    "src_note": ("UOL (Renata Agostini e Tiago Dantas), 15/10/2026: conversas de out/2023 a jul/2025 "
                 "entre Vorcaro e o então diretor-geral de Mídia Impressa e Rádio do Grupo Globo — "
                 "patrocínios (Baile da Vogue 2024: R$ 825 mil; camarote no Carnaval 2023: R$ 1,6 milhão), "
                 "pedidos de pauta e o código 'guerra na Ucrânia'. Kachar foi demitido em 15/10/2026, "
                 "após o vazamento; a nota oficial do Grupo Globo está registrada nos eventos."),
    "secs": [KACHAR],
    "msgs": [
      (None, None, "daniel-vorcaro", "De repente ver se você consegue uma capa pra ela na Vogue. Ela tem cancha pra isso",
       "Sobre Martha Graeff, então namorada de Vorcaro, segundo a reportagem."),
      (None, None, "frederic-kachar", "um processo mais longo",
       "Fragmento: Kachar respondeu que capa na Vogue era 'um processo mais longo', segundo a reportagem."),
      (None, None, "frederic-kachar", "Eu te asseguro um destaque importante pra Martha. E falarei de capa também com Marie Claire e Ela", None),
      (None, None, "frederic-kachar", "Vou pautar Vogue, Marie Claire e Ela", None),
      (None, None, "daniel-vorcaro", "Ficaram ótimas, obrigado",
       "Três dias depois, sobre as reportagens das três publicações sobre a Happy Aging, segundo a reportagem; ele reclamou apenas da Marie Claire, que 'deu uma batidinha no final'."),
      (None, None, "frederic-kachar", "Próximo passo é uma capa a Ela ou Marie Claire. Só precisamos de um fato novo", "Na semana seguinte, retomando a negociação, segundo a reportagem."),
      (None, None, "daniel-vorcaro", "Capa será muito legal", "Resposta na mesma sequência, segundo a reportagem."),
      (None, None, "frederic-kachar", "Estamos trabalhando pra isso!", "Resposta na mesma sequência, segundo a reportagem."),
      (None, None, "frederic-kachar", "destravar o uso do novo contrato",
       "Fragmento: pediu ajuda a Vorcaro para 'destravar o uso do novo contrato' de publicidade do banco com a editora, segundo a reportagem."),
      (None, None, "frederic-kachar", "Tínhamos um plano robusto pra outubro", None),
      (None, None, "daniel-vorcaro", "Será feito",
       "Vorcaro disse que tinha falado com a responsável e respondeu, segundo a reportagem."),
      (None, None, "frederic-kachar", "Tirei o banco nos dois casos",
       "Em 2025, com os problemas do Master aparecendo, sobre as propostas do Baile da Vogue e do camarote, segundo a reportagem."),
      (None, None, "frederic-kachar", "500k na Vogue e 800k no camarote",
       "Fragmento: valores combinados para 2025 com as marcas Desinchá e Happy Aging, de Vorcaro, no lugar do banco, segundo a reportagem."),
      ("2024-03", None, "frederic-kachar", "Já está na Ucrânia, rs?",
       "Horas depois de Vorcaro anunciar um 'plano ataque soviético'; 'guerra na Ucrânia' era a expressão do grupo de Vorcaro para festas com mulheres estrangeiras, segundo a reportagem."),
      ("2024-03", None, "frederic-kachar", "Temos guerra na Ucrânia nessa semana?", "Uma semana depois, segundo a reportagem."),
      ("2024-03", None, "daniel-vorcaro", "Tem hoje. Bora?", "Resposta na mesma sequência, segundo a reportagem."),
      ("2024-03", None, "frederic-kachar", "Se tiver, tô dentro",
       "Disse que não conseguiria ir naquele dia e perguntou se haveria na semana seguinte, segundo a reportagem."),
      ("2024-05", None, "frederic-kachar", "Dessa vez eu vou!",
       "Ao ser convidado para um camarote com a cúpula do Grupo Globo no show de Madonna; Vorcaro anunciou que haveria 'festa' na terça, segundo a reportagem."),
      ("2024-04", None, "frederic-kachar", "Se tiver algum erro na coluna da Malu, peço a correção imediata",
       "Após Vorcaro reclamar de post da colunista Malu Gaspar sobre o fórum de Londres, segundo a reportagem."),
      ("2024-04", None, "frederic-kachar", "Não estou entendendo esse seu tom comigo.", "Sequência da mesma conversa, segundo a reportagem."),
      ("2024-07", None, "frederic-kachar", "Não tem campanha alguma, claro",
       "Vorcaro dissera que Lauro Jardim havia publicado 'informação falsa' e perguntou se havia 'campanha corporativa' contra ele, segundo a reportagem."),
      ("2024-09", None, "frederic-kachar", "Eles colocaram os dois lados",
       "Sobre reportagem do Valor sobre os resultados do banco, segundo a reportagem."),
      ("2024-09", None, "frederic-kachar", "Não dá pra fazer matéria sem olhar pra todos os fatos.", "Sequência da mesma conversa, segundo a reportagem."),
    ],
    "events": [
      (None, "Patrocínios do Master ao grupo, conforme tabela enviada por Kachar: R$ 825 mil no Baile da Vogue de 2024 e R$ 1,6 milhão no camarote da editora no Carnaval de 2023. Em 2025, os materiais do baile foram impressos com as marcas Desinchá e Happy Aging, de Vorcaro.", KACHAR),
      (None, "'Guerra na Ucrânia' era a expressão usada no grupo de Vorcaro para festas com mulheres estrangeiras; como mostrou o UOL, refugiadas ucranianas integravam um negócio de prostituição financiado por Vorcaro, investigado pela PF.", KACHAR),
      ("2026-10-15", "O Grupo Globo comunica a demissão de Kachar da direção-geral de Mídia Impressa e Rádio após o vazamento. Em nota, o presidente João Roberto Marinho diz que as conversas (out/2023 a jul/2025) 'revelaram uma relação inadequada do executivo com um anunciante da Editora Globo', reafirma 'a absoluta independência editorial do jornalismo' e informa que Luís Henrique Guimarães acumula interinamente o cargo.", KACHAR),
    ],
  },
  "elsinho-mouco": {
    "title": "Elsinho Mouco",
    "src_note": ("UOL (apuração de O Globo), 14/10/2026: o publicitário Elsinho Mouco, interlocutor do "
                 "ex-presidente Michel Temer, enviou a Vorcaro e cobrou pagamentos do contrato de até "
                 "R$ 30 milhões entre o Master e o escritório de Temer, firmado em 03/09/2025 para "
                 "tentar viabilizar a venda do banco ao BRB — vetada pelo Banco Central."),
    "secs": [TEMER_UOL],
    "msgs": [
      (None, None, "daniel-vorcaro", "Estou no Banco Central hoje, consigo chamar somente mais tarde", None),
      (None, None, "elsinho-mouco", "Tranquilo. Depois checa com sua equipe se já fizeram o pagamento", "Resposta na mesma sequência, segundo a reportagem."),
      ("2025-09-04", None, "elsinho-mouco", "Assim que assinar o contrato e fizerem a transferência, me envia o comprovante. Vamos à luta!", None),
      ("2025-10-29", None, "daniel-vorcaro", "Minha vida tá uma loucura",
       "Relatando problemas para liberar pagamentos com o Master em dificuldades e a venda ao BRB já barrada, segundo a reportagem."),
      ("2025-10-29", None, "daniel-vorcaro", "Luta tá grande aqui pra ficar de pe", "Sequência do mesmo desabafo, segundo a reportagem."),
      ("2025-11-11", None, "elsinho-mouco", "Entrou a metade",
       "Segundo a reportagem, parte do dinheiro entrou poucos dias antes da prisão de Vorcaro, sem detalhamento de valores."),
    ],
    "events": [
      ("2025-09-03", "Contrato entre o Master e o escritório de Temer: R$ 10 milhões de honorários iniciais (R$ 5 milhões na assinatura e R$ 5 milhões após 30 dias) e R$ 20 milhões de êxito condicionados ao avanço da venda ao BRB. Cláusula: 'Assinado em definitivo o Contrato após autorização do Banco Central do Brasil, os honorários de êxito deverão ser pagos 20 dias após esse fato'. Frentes: ação judicial ligada ao BC, representação no TCU e mediação junto a 'todos os organismos competentes'. A transação dependia de autorização do BC, que vetou o negócio.", TEMER_UOL),
    ],
  },
  "michel-temer": {
    "title": "Michel Temer",
    "src_note": ("UOL (apuração de O Globo), 14/10/2026: contatos diretos entre o ex-presidente "
                 "Michel Temer (MDB) e Vorcaro nos dias seguintes ao contrato de até R$ 30 milhões "
                 "entre o Master e o escritório de Temer (03/09/2025). Em abril de 2026, Temer "
                 "confirmou a consultoria e a mediação, dizendo que o contrato foi encerrado sem "
                 "resultado."),
    "secs": [TEMER_UOL],
    "msgs": [
      (None, None, "daniel-vorcaro", "Presidente, aqui é o Daniel Vorcaro Banco Master. Salva meu contato. Nos falamos em breve. Um cordial abraço",
       "Em 2023, quando procurou o ex-presidente para tratar de um documentário, segundo a reportagem."),
      (None, None, "michel-temer", "Salvei. Bom dia", "Resposta na mesma sequência, segundo a reportagem."),
      ("2025-09-05", None, "michel-temer", "Qdo puder, me ligue",
       "Nos dias seguintes ao envio do contrato pelo escritório, segundo a reportagem."),
      (None, None, "michel-temer", "Acho que no dia 1/11 iremos a Dubai. Mario pede para vc se preparar para essa viagem. Avisaremos. Abs",
       "Início de novembro de 2025, sobre agenda de reuniões em Dubai organizada por Temer, segundo a reportagem."),
    ],
    "events": [
      (None, "O histórico de contato começou em 2023, quando Vorcaro procurou Temer para tratar de um documentário, segundo a reportagem.", TEMER_UOL),
      (None, "Em abril de 2026, em entrevista à CNN Brasil, Temer confirmou que foi contratado pelo Master para consultoria e mediação antes da liquidação do banco; disse ter recebido honorários e que o contrato foi encerrado sem resultado. Afirma ter participado de reunião em Brasília com Vorcaro, o então governador do DF Ibaneis Rocha (MDB) e o então presidente do BRB Paulo Henrique Costa, sem detalhar o conteúdo por confidencialidade profissional.", TEMER_UOL),
    ],
  },
  "manuela-carta": {
    "title": "Manuela Carta",
    "src_note": ("UOL (Renata Agostini e Tiago Dantas), 15/10/2026: a diretora da CartaCapital avisou "
                 "Vorcaro da necessidade de recursos para a folha de pagamentos; a revista fechou em "
                 "2021 contrato de patrocínio de cinco anos com o então Banco Máxima, que já havia "
                 "adiantado R$ 300 mil em dezembro de 2020. Negociação de compra da revista por "
                 "Vorcaro não se concretizou. Nota de CartaCapital registrada nos eventos."),
    "secs": [REDE],
    "msgs": [
      (None, None, "manuela-carta", "mais um recurso para a próxima folha de pagamentos",
       "Fragmento: no início de 2021, Carta avisou a Vorcaro que precisaria de 'mais um recurso para a próxima folha de pagamentos', segundo a reportagem."),
    ],
    "events": [
      ("2020-12", "O Banco Máxima (futuro Master) adianta R$ 300 mil à CartaCapital; em 2021, é firmado contrato de patrocínio de cinco anos. O dinheiro ajudava a pagar salários, segundo a reportagem.", REDE),
      ("2023-08", "Carta e Vorcaro se encontram para tratar da eventual entrada dele como sócio da revista, possibilidade discutida havia um ano; três dias depois, ela envia dados sobre a dívida da revista e sinaliza aguardar proposta. A negociação não se concretiza.", REDE),
      (None, "Em 2024, Carta pediu um 'adiantamento de publicidade', e Vorcaro se ofereceu para ajudar 'fora do banco', segundo a reportagem.", REDE),
      (None, "Em nota, Manuela Carta, publisher da CartaCapital, informou que o Banco Master 'fechou um contrato de publicidade com a editora em 2021 e anunciou na revista até 2023. Tratava-se de um contrato regular de veiculação de anúncio, conforme as regras do mercado publicitário'; que o grupo voltou a anunciar por meio da Kovr e do Will; e que Vorcaro nunca a procurou para pedir notícias positivas ou interferir em conteúdo jornalístico, 'o que, obviamente, seria um erro, dada a separação entre a área comercial e a redação'.", REDE),
    ],
  },
  "isaac-sidney": {
    "title": "Isaac Sidney",
    "src_note": ("UOL — coluna Natália Portinari, 15/10/2026: mensagens da PF sobre a interlocução de "
                 "Vorcaro com o presidente da Febraban — aluguel e compra do apartamento na Vila Olímpia "
                 "(com R$ 1,2 milhão pagos ao vendedor fora da escritura), processos da CVM, regras do "
                 "FGC e a consultoria de Henrique Meirelles. Proposta de delação de Vorcaro citava "
                 "Sidney; PGR e PF rejeitaram por ausência de provas. Defesa extensa registrada nos eventos."),
    "secs": [FEBRABAN],
    "msgs": [
      ("2019-02", None, "daniel-vorcaro", "Não precisa tratar nada de comercial. Deixa isso comigo. Valores etc.",
       "Ao negociar com o dono do imóvel a locação da cobertura para Isaac, então advogado do Master, segundo a reportagem."),
      ("2020-08", None, "isaac-sidney", "Achei duro",
       "Sobre parecer da área técnica da CVM contra acordo proposto por Vorcaro, que Isaac lhe enviara, segundo a reportagem."),
      ("2020-11", None, "isaac-sidney", "Falei com ele na quarta",
       "Ao enviar a Vorcaro, junto de minuta da escritura do apartamento, despacho da CVM em processo contra Vorcaro e o Máxima; sem dizer com quem falou, segundo a reportagem."),
      (None, None, "isaac-sidney", "Você nem imagina o que ouvi do presidente do BC e de um diretor, mas saí em sua defesa. Às vezes, o prestígio não é o que se vê, mas o que nem se sabe. Lealdade é o maior prestígio que posso lhe oferecer",
       "No fim de 2023, quando o BC preparava mudanças nas regras do FGC que atingiam o Master, em parte por pedido da própria Febraban, após Vorcaro reclamar que Isaac não lhe dava atenção, segundo a reportagem."),
      (None, None, "isaac-sidney", "para que vocês tivessem a oportunidade de mostrar a lisura da atuação do banco",
       "Fragmento: duas semanas depois, contou ter levado o diretor-executivo do FGC e o vice-presidente da ABBC ao Master, segundo a reportagem."),
      (None, None, "isaac-sidney", "Até um paper dos pontos críticos fiz chegar a você", "Sequência da mesma conversa, segundo a reportagem."),
      ("2024-04", None, "isaac-sidney", "Disseram a ele que o banco estava na mira do BC",
       "Sobre o ex-ministro Henrique Meirelles, convidado a prestar consultoria ao Master, que ligou para Isaac pedindo referências, segundo a reportagem."),
      ("2024-04", None, "isaac-sidney", "Penso que consegui desfazer os senões.", "Sequência da mesma conversa, segundo a reportagem."),
      ("2024-04", None, "isaac-sidney", "Pode deixar que vou dar um toque no Paulo e no Belline",
       "Vorcaro pedira que Meirelles ligasse também para 'o Belline ou Paulo', servidores da supervisão do BC suspeitos, segundo a proposta de delação de Vorcaro, de receberem propina."),
      ("2024-04", None, "isaac-sidney", "Foi boa a conversa do Meirelles com Paulo Sérgio", "No dia seguinte, segundo a reportagem."),
      ("2024-04", None, "daniel-vorcaro", "Se não tivesse você, seria um tiro bem ruim", "Agradecimento na mesma sequência, segundo a reportagem."),
    ],
    "events": [
      ("2018", None, FEBRABAN),  # placeholder, substituído abaixo
      (None, "Isaac Sidney foi chefe de gabinete de Henrique Meirelles no Banco Central, depois advogado do Banco Máxima/Master (aprovou-se junto ao BC a transferência do banco para Vorcaro) e assumiu a vice-presidência da Febraban em maio/2019 e a presidência em março/2020.", FEBRABAN),
      ("2019-02", "Locação da cobertura para Isaac: contrato formal de R$ 15 mil mensais registrou só a parte dele (R$ 174 mil adiantados pelo primeiro ano), mas o dono pedia R$ 50 mil; pela conta do vendedor, Vorcaro cobriria a diferença por 18 meses, mais impostos — 'Isso tudo dá 946', escreveu, em referência a R$ 946 mil. Vorcaro pagou entre março e abril de 2019. O aluguel antecipado cobre período em que Isaac já estava na Febraban.", FEBRABAN),
      ("2020-11", "Venda do apartamento a Isaac por R$ 7,3 milhões (escritura: R$ 1,8 milhão de recursos próprios e R$ 5,5 milhões de empréstimo do Master). Nos documentos no celular de Vorcaro constam ainda transferências do Master ao vendedor de R$ 1,2 milhão fora da escritura: R$ 535 mil (boleto Itaú, 17/11/2020), R$ 534 mil (sinal à construtora Yuny, 22/12) e R$ 131 mil à conta do vendedor. O vendedor cobrara um 'saldo' de R$ 665 mil dizendo que os valores não estavam documentados. O empréstimo foi quitado 13 meses depois, antes da primeira parcela.", FEBRABAN),
      (None, "Na proposta de delação apresentada à PF e à PGR, Vorcaro dedicou um capítulo a Isaac, afirmando que o apartamento foi pagamento 'em contrapartida à influência exercida junto ao Banco Central, em favor do Colaborador e do Banco Master'. A proposta foi rejeitada por ausência de provas; Sidney atribui a inclusão a retaliação por seu papel em denunciar as fraudes do Master em ofícios da Febraban ao BC.", FEBRABAN),
      (None, "Defesa: Sidney diz que desconhece os pagamentos fora da escritura, que 'é falsa e sórdida qualquer especulação' de benefício em troca de influência no BC ('Jamais recebi qualquer bem, nem houve transferência para meu nome'); que a escritura 'refletiu integralmente a negociação final'; que acompanhou o boleto do Itaú apenas porque 'sem a quitação do saldo devedor, o imóvel não poderia ser dado em garantia em novo crédito imobiliário'; que o contrato de locação é de março/2019, antes da Febraban; que as despesas do flat inicial foram pagas 'a título de honorários advocatícios'; que foi 'a primeira voz do setor bancário a alertar o Banco Central' sobre a concentração da captação garantida pelo FGC, em três ofícios assinados por ele, e o primeiro dirigente a apoiar a liquidação do Master; que as referências a 'lealdade' e 'defesa' refletem 'interlocuções institucionais com bancos associados'; que só atuou para o Máxima depois de cumprida a quarentena; e que, no episódio Meirelles, sugeriu que ele procurasse a área de fiscalização do BC, como faria com qualquer dirigente de banco.", FEBRABAN),
    ],
  },
  "eduardo-barcellos": {
    "title": "Eduardo Barcellos",
    "src_note": ("UOL — coluna Natália Portinari, 15/10/2026: conversas entre Vorcaro e o vendedor do "
                 "duplex da Vila Olímpia alugado e depois vendido ao presidente da Febraban Isaac "
                 "Sidney — com R$ 1,2 milhão pagos por fora da escritura. Procurado, Barcellos disse "
                 "não se lembrar da venda e desligou o telefone."),
    "secs": [FEBRABAN],
    "msgs": [
      ("2019-02", None, "eduardo-barcellos", "Isso tudo dá 946",
       "Pela conta do vendedor, os 18 meses de diferença de aluguel mais impostos somariam R$ 946 mil, segundo a reportagem."),
      (None, None, "eduardo-barcellos", "Aquele valor que a gente negociou é por fora, não tem IR",
       "Em áudio, tratando o acerto como sigiloso, segundo a reportagem."),
      ("2020-11", None, "daniel-vorcaro", "Queria combinar um detalhe com você pessoalmente",
       "Ao perguntar se podia pagar na data da assinatura da escritura o 'saldo' de R$ 665 mil que Barcellos cobrava, segundo a reportagem."),
      ("2020-11", None, "eduardo-barcellos", "Como não está documentado, eu preferia que fosse antes",
       "Resposta na mesma sequência; marcaram encontro no escritório de Vorcaro para o dia seguinte, segundo a reportagem."),
      ("2020-11", None, "daniel-vorcaro", "Foi pago ontem",
       "No dia seguinte ao encontro, informando o pagamento do boleto do Itaú; a escritura foi assinada dez dias depois, em 27/11/2020, registrando o financiamento quitado sem informar quem o pagou."),
    ],
    "events": [
      ("2018", None, FEBRABAN),  # placeholder
      ("2020-11", "Venda do apartamento a Isaac Sidney por R$ 7,3 milhões. Além do empréstimo do Master de R$ 5,5 milhões registrado em escritura, constam no celular de Vorcaro transferências de R$ 1,2 milhão ao vendedor fora da escritura: boleto do Itaú de R$ 535 mil pago em 17/11/2020, R$ 534 mil à construtora Yuny (comprovante enviado em 22/12) e R$ 131 mil direto à conta de Barcellos.", FEBRABAN),
      (None, "Procurado pelo UOL, Barcellos disse que não se lembra de ter vendido o apartamento; confrontado com os detalhes da conversa, desligou o telefone.", FEBRABAN),
    ],
  },
  "geraldo-samor": {
    "title": "Geraldo Samor",
    "src_note": ("UOL (Renata Agostini e Tiago Dantas), 15/10/2026: o fundador do Brazil Journal "
                 "consultava Vorcaro sobre reportagens do Master antes de publicá-las e atendia "
                 "pedidos de alteração. A participação do banqueiro se dava por terceiros: a Foone, "
                 "de Flávio Carneiro, ficou com 49,86% da BJ Conteúdo (2023). Samor foi procurado e "
                 "não respondeu."),
    "secs": [REDE],
    "msgs": [
      ("2024-02", None, "geraldo-samor", "Flávio acaba de me mandar o texto. Vou trabalhar. Você quer isso publicado amanhã cedo?", None),
      ("2024-02", None, "daniel-vorcaro", "A frase avenida pra agronegócio você pode tirar?", "Na manhã seguinte, com o texto ainda não publicado, segundo a reportagem."),
      ("2024-02", None, "geraldo-samor", "Atualizado", "Resposta na mesma sequência, segundo a reportagem."),
      ("2024-02", None, "daniel-vorcaro", "Me faz um favor, tira o nome Voiter, vamos falar só que anunciamos reorganização societária",
       "Dias depois, sobre a publicação da compra do Will Bank, segundo a reportagem."),
      ("2024-02", None, "geraldo-samor", "Mudei", "Resposta na mesma sequência, segundo a reportagem."),
      ("2024-04", None, "geraldo-samor", "Flávio falou que você queria ver antes",
       "Ao enviar o texto sobre o evento do Master em Londres com Tony Blair, segundo a reportagem."),
      ("2024-04", None, "geraldo-samor", "Na nossa opinião, perdeu muito. Mas entendemos a limitação",
       "Após enviar uma 'versão mais curta' a pedido do banqueiro, segundo a reportagem."),
    ],
    "events": [
      ("2023", None, REDE),  # placeholder
      ("2024-04", "No caso Blair, Vorcaro pediu que Samor acrescentasse que 'os três ministros do STF' (Toffoli, Alexandre de Moraes e Gilmar Mendes) teriam se reunido 'privadamente' com Blair antes do debate, segundo a reportagem.", REDE),
      (None, "Procurado pelo UOL, Samor não respondeu aos contatos da reportagem.", REDE),
    ],
  },
  "diogo-batista": {
    "title": "Diogo Batista",
    "src_note": ("UOL — coluna Natália Portinari, 13/10/2026: o promotor de eventos, que ganhava "
                 "R$ 120 mil por mês de Vorcaro, era o executor do esquema de agenciamento — um dos "
                 "principais investigados pela PF ao lado de Leonardo Serrano; nenhum dos dois "
                 "respondeu ao UOL. " + SENSITIVE_NOTE),
    "secs": [TRIO],
    "msgs": [
      ("2023-11", None, "diogo-batista", "Não quero sair e pagar pra elas sem vc mandar",
       "Na madrugada seguinte à festa de Halloween, segundo a reportagem."),
      ("2023-11", None, "daniel-vorcaro", "Vamos mandar embora. Depois trazemos quem quisermos. Ficou muito burburinho. Vamos zerar e recomeçar",
       "Ordem de renovação do grupo, segundo a reportagem."),
      ("2023-11", None, "diogo-batista", "Vc manda irmão", "Resposta na mesma sequência, segundo a reportagem."),
      ("2023-11-07", None, "diogo-batista", "Tem 3 refugiadas aqui? Ucranianas", None),
      ("2023-11-07", None, "daniel-vorcaro", "Tem que sobrar alguma refugiada pra mim", "Resposta na mesma sequência, segundo a reportagem."),
      ("2023-11", None, "diogo-batista", "Bora colocar elas na agência e daí lavamos as mãos",
       "No fim de novembro/2023, sobre a jovem refugiada que permaneceu no Brasil, segundo a reportagem."),
      ("2023-12-14", None, "daniel-vorcaro", "Tem quantas estrangeiras aí ainda?", None),
      ("2023-12-14", None, "diogo-batista", "1 só. Ela não tem pra onde ir. Estão bombardeando a cidade dela",
       "Sobre a refugiada ucraniana, que chegara ao grupo na festa de Halloween de 2023, segundo a reportagem."),
      ("2023-12", None, "diogo-batista", "Segurei ela pq ela ia sair pra se refugiar na Itália", None),
      ("2024-01", None, "diogo-batista", "Vamos fechar essa agência irmão? Ajuda muito pra segurar essas meninas? daí eu alugo uma casa tbm ou ap grande pela agência! Não fica atrelado à gente!",
       "Em janeiro/2024, insistindo na agência como estrutura desvinculada dos dois, segundo a reportagem."),
      ("2024-01", None, "diogo-batista", "Assim estamos blindados!",
       "Em janeiro/2024, ao avisar que o contrato de compra de 50% da Allure Eventos (R$ 1,5 milhão) estava assinado, segundo a reportagem."),
      ("2024-01", None, "daniel-vorcaro", "E funcionário só mulher",
       "Resposta ao pedido de Diogo de R$ 500 mil para 'pegar uma casa pras modelos', segundo a reportagem."),
      (None, None, "diogo-batista", "Que loucura. Tiago deve saber. Mas ninguém falou de você",
       "Sobre reclamação de Vorcaro de que um 'promoter' estava 'falando por aí que comprei Allure'; Tiago é Tiago Polo, que também agenciava modelos, segundo a reportagem."),
      ("2024-02", None, "daniel-vorcaro", "Fazer seleção. Vamos fazer uma só do Sul. Semana que vem. Arruma aí", None),
      ("2024-02", None, "daniel-vorcaro", "Já faz seleção, umas 20", None),
      ("2024-02", None, "daniel-vorcaro", "Vamos tirar visto Famiglia",
       "Mandou usar a agência para contratar as mulheres e tirar visto para elas, segundo a reportagem."),
      ("2024-02", None, "daniel-vorcaro", "Contratar todas Allure. E marca entrevista.", "Sequência da mesma ordem, segundo a reportagem."),
      ("2024-02", None, "diogo-batista", "Lógico. Deixa comigo", "Resposta na mesma sequência, segundo a reportagem."),
      ("2024-03", None, "diogo-batista", "Mando [as duas]? Nossas refugiadas?",
       "Sobre as 'figurantes' mandadas para um jantar de Vorcaro com convidados no Pappa Bar, nos Jardins; colchete consta da reportagem."),
      ("2024-03", None, "diogo-batista", "Quem vc escolheu pra Famiglia eu tô doutrinando muito", None),
      ("2024-03", None, "diogo-batista", "Vc tem uma Famiglia obediente", "Sequência da mesma conversa, segundo a reportagem."),
      ("2024-04", None, "diogo-batista", "Chefe precisa autorizar",
       "Sobre pagamentos às mulheres, que não ocorriam sem ordem de Vorcaro, segundo a reportagem."),
      ("2024-04-15", None, "daniel-vorcaro", "Ucrania e Russia vamos mandar embora", None),
      ("2024-04-15", None, "diogo-batista", "Mandamos embora então?",
       "Diogo observou que o país da jovem refugiada ainda estava em guerra; Vorcaro disse que faria uma 'seleção' de quem ficaria, segundo a reportagem."),
      (None, None, "diogo-batista", "Eu e vc somos o time! Vc é o chefe e eu seu Cavaleiro PitBull!", None),
      (None, None, "diogo-batista", "Chefe manda e a gente executa", None),
      ("2024-10", None, "diogo-batista", "Não podemos perder nosso talento que sempre foi operar as gatas? Eu não vou mais cobrar porcentagem das modelos? Sem essa de explorar elas como sempre foi",
       "Em outubro/2024, ao dizer que deixaria de cobrar porcentagem sobre o trabalho das modelos, segundo a reportagem."),
    ],
    "events": [
      (None, "Diogo Batista é promotor de eventos em São Paulo e ganhava R$ 120 mil por mês de Vorcaro; é um dos principais investigados pela PF no inquérito sobre o esquema, ao lado de Leonardo Serrano. Nenhum dos dois respondeu aos contatos do UOL. A PF apura possível tráfico internacional de pessoas — que exige violência ou coação, ponto ainda em apuração —; no Brasil, prostituição não é crime, mas cafetinagem sim.", TRIO),
      ("2023-10", "Festa de Halloween na boate Madame Satã: entre as estrangeiras levadas estava uma refugiada ucraniana de 19 anos. No início de novembro, Vorcaro anunciou que não pagaria mais hotel nem voo de quem quisesse ficar no Brasil; a jovem ficou, e dias depois Diogo enviou os dados do passaporte dela para embarque com o grupo ao Rio, relatando que ela não poderia voltar à Ucrânia porque a família considerava arriscado.", TRIO),
      ("2023-12", "Contrato para compra de 50% da Allure Eventos, de Felipe Nisti Cataldo, por R$ 1,5 milhão, enviado ao celular de Vorcaro; assinado em janeiro/2024, com primeira parcela de R$ 500 mil dias depois e outras duas entre fevereiro e maio/2024 — a última paga por Pix da Super Empreendimentos, empresa usada por Vorcaro, a Nisti. Procurado, Nisti disse que a tratativa não avançou, negou o acerto citado nas conversas e, sobre o Pix, que 'precisaria verificar' o motivo. Em nota, a Allure nega envolvimento e 'jamais' teve relacionamento societário, comercial ou contratual com Vorcaro.", TRIO),
      ("2024-05", "Diogo propôs dividir as mulheres em dois grupos: o 'Time Famiglia A', de convivência restrita, e o 'B', para 'eventos de volume', segundo a reportagem.", TRIO),
      (None, "Defesa de Vorcaro, em nota após a publicação: nega 'veementemente' que tenha 'em algum momento, explorado ou desrespeitado mulheres'; diz não reconhecer 'a autoria, a autenticidade e o contexto' de vários dos conteúdos vazados; afirma que os vazamentos 'expõem indevidamente' sua intimidade e apresentam 'uma história enviesada, sujeita ao uso político'; e reitera disposição de colaborar com as investigações 'para que todos conheçam a verdade por inteiro'.", TRIO),
    ],
  },
  "leonardo-serrano": {
    "title": "Leonardo Serrano",
    "src_note": ("UOL — coluna Natália Portinari, 13/10/2026: 'Leo' Serrano, dono da SL Consulting "
                 "(sede na Flórida), cuidava da logística internacional — voos, hotéis, 'flores' "
                 "(como chamava as garotas) e faturas: 21 notas de abr/2024 a mar/2025 somam cerca "
                 "de US$ 70 milhões, emitidas à Moriah Asset como 'orçamento antecipado'. É um dos "
                 "principais investigados pela PF; não respondeu ao UOL. " + SENSITIVE_NOTE),
    "secs": [TRIO],
    "msgs": [
      ("2023-11", None, "daniel-vorcaro", "O cara tá cheio de brasileira lá às minhas custas",
       "Na festa de Halloween de 2023, segundo a reportagem; Leo depois informou que eram 'mais de 120 meninas' trazidas por Diogo."),
      ("2023-11", None, "leonardo-serrano", "As passagens aéreas e hotel de todas essas meninas [...] vou faturar pra Prime",
       "Sobre a destinação das despesas com as mulheres no Brasil à empresa Prime You; reticências entre colchetes constam da reportagem."),
      ("2024-02", None, "leonardo-serrano", "Eu tô traficando é nada! Isso é trabalho do doidinho seu lá",
       "Tentando se distanciar de Diogo no recrutamento de estrangeiras, segundo a reportagem."),
      ("2024-03", None, "leonardo-serrano", "Posso considerar 5 pirulitos e 30 flores pro Annabels?",
       "'Flores' era como Leo se referia às garotas, segundo a reportagem; sobre casa noturna em Londres, em viagem que também contava com políticos."),
      ("2024-03", None, "daniel-vorcaro", "6 macacos 20/30 flores",
       "Resposta na mesma sequência; 'macacos' era como se referiam aos profissionais masculinos dos eventos, contratados em menor proporção."),
      ("2024-04", None, "leonardo-serrano", "Iremos tirar o celular de todas meninas",
       "Antes do evento de Londres, que contava com autoridades de Brasília; segundo a reportagem, 99 mulheres trabalharam no evento, sete trazidas do Brasil."),
      ("2024-10", None, "daniel-vorcaro", "Não é pra NENHUM homem entrar", "Sobre a festa em Roma, segundo a reportagem."),
      ("2024-10", None, "leonardo-serrano", "Turma Zoltan umas 30 [...] Turma Diogo umas 20 [...] Do Brasil foram 8",
       "A conta da festa de Roma; reticências entre colchetes constam da reportagem. De Roma, parte das mulheres seguiu para Dubai."),
      ("2024-10", None, "leonardo-serrano", "Eu NÃO vou me responsabilizar pelas pessoas que o Diogo mandar para a festa [...] não ganho nada com isso.",
       "Reclamando das mulheres enviadas pelo parceiro; reticências entre colchetes constam da reportagem."),
      ("2025-01", None, "daniel-vorcaro", "Não é pra ter pagamento nenhum seu de qualquer coisa de Diogo a partir deste ano",
       "Corte de pagamentos determinado a Leo, segundo a reportagem."),
    ],
    "events": [
      (None, "A SL Consulting, de Leonardo Serrano, cuidava da logística internacional: encomendava as garotas a promoters de cada cidade, reservava voos e hotéis e liberava dinheiro. As faturas (21 localizadas pelo UOL, de abril/2024 a março/2025, somando cerca de US$ 70 milhões) eram emitidas para a Moriah Asset, gestora de Belo Horizonte, como 'orçamento antecipado' para 'eventos, hospitalidade, hospedagem e fretamentos', e Vorcaro as repassava ao financeiro do Master. Despesas da 'turma do Diogo': faturas de R$ 350 mil (setembro/2024) e R$ 260 mil (outubro/2024) autorizadas por Leo.", TRIO),
      ("2023-11", "Halloween na boate Madame Satã: Leo contou 74 garotas; Diogo trouxe outras 40, hospedadas em 21 quartos do hotel Rosewood, segundo a reportagem.", TRIO),
      (None, "Em junho/2024, Leo propôs liberar 3 mil euros para compras a cada uma das oito mulheres de uma festa na França; Vorcaro autorizou 4 mil. Em fevereiro/2025, para o Carnaval, Diogo pediu 'umas 15 florzinhas de fora' para as festas no Rio. Em outra passagem, Leo disse que o promoter de Londres também trabalhava para festas de Leonardo DiCaprio.", TRIO),
      (None, "Leonardo Serrano é um dos principais investigados pela PF no inquérito; não respondeu aos contatos do UOL.", TRIO),
    ],
  },
  "tiago-polo": {
    "title": "Tiago Polo",
    "src_note": ("UOL — coluna Natália Portinari, 13/10/2026: Tiago Polo, que trabalhava agenciando "
                 "modelos, explicou a Vorcaro o propósito da agência e ofereceu a Allure e a Ford "
                 "Models (US$ 6,7 milhões). " + SENSITIVE_NOTE),
    "secs": [TRIO],
    "msgs": [
      ("2023-10", None, "tiago-polo", "O Diogo disse [que] a ideia da agência seria uma forma de ajustar as meninas indiretamente",
       "Explicando a Vorcaro para que serviria a agência; colchete consta da transcrição da reportagem."),
    ],
    "events": [
      (None, "Tiago Polo ofereceu a Vorcaro a compra da Allure e da Ford Models — que teria pedido cerca de US$ 6,7 milhões —, segundo a reportagem.", TRIO),
      ("2024-01", "Vorcaro pediu a Tiago que fosse ao Sul do país 'buscar umas gatas' para o 'cadastramento Allure', segundo a reportagem.", TRIO),
      (None, "Em conversa sobre a compra da Allure, Diogo Batista escreveu a Vorcaro, referindo-se a Tiago: 'Que loucura. Tiago deve saber. Mas ninguém falou de você'.", TRIO),
    ],
  },
}

# placeholders substituídos por eventos completos (evita duplicar texto longo)
THREADS["isaac-sidney"]["events"][0] = (
    "2018", "Vorcaro conhece o dono do duplex de 410 m² na Vila Olímpia ao querer alugar o imóvel para morar com a família, que desistiu de se mudar para São Paulo; em 2019, surge a ideia de alugá-lo a Isaac Sidney, então advogado do Master.", FEBRABAN)
THREADS["eduardo-barcellos"]["events"][0] = (
    "2018", "Vorcaro conhece o vendedor ao negociar o aluguel do duplex da Vila Olímpia para sua família; a ideia de alugá-lo a Isaac Sidney surge em 2019, quando ele ainda era advogado do Master.", FEBRABAN)
THREADS["geraldo-samor"]["events"][0] = (
    "2023", "Samor cria a BJ Conteúdo, empresa de vídeos e eventos do Brazil Journal; a Foone, de Flávio Carneiro, amigo de Vorcaro, fica com 49,86%. Em dezembro, Vorcaro e Carneiro discutem como incluir o dono da IstoÉ, Antônio Carlos Freixo Júnior (o 'Mineiro'), na Foone sem ligá-lo ao site: 'Não dá pra ele aparecer como sócio do Geraldo no Brazil Journal. Vai sujar a água', escreveu Carneiro (mensagem registrada na conversa com Flávio Carneiro). A solução sugerida foi 'fazer uma Foone 2 e pôr só o BJ lá'.", REDE)

PARTICIPANTS_NEW = [
    {"id": "lilian-tahan", "name": "Lilian Tahan", "photo": None,
     "role": "CEO do grupo Metrópoles",
     "aliases": [],
     "summary": ("Segundo o UOL (15/10/2026), mantinha linha direta com Vorcaro: ao menos 14 textos do Metrópoles "
                 "lhe foram enviados antes de publicados, 11 alterados a pedido dele. Contratos de publicidade "
                 "somam R$ 1 milhão (2024), R$ 900 mil (Kovr/Will) e R$ 20 milhões. Defende-se dizendo que checagem "
                 "com fontes é prática jornalística e negando vínculo entre contrato e cobertura. Perfil resumido "
                 "exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "frederic-kachar", "name": "Frederic Kachar", "photo": None,
     "role": "Ex-diretor-geral de Mídia Impressa e Rádio do Grupo Globo",
     "aliases": ["Fred Kachar"],
     "summary": ("Liderava O Globo, Extra, Valor, revistas da Editora Globo e o sistema de rádio. Segundo o UOL "
                 "(15/10/2026), negociava patrocínios com Vorcaro, pautava publicações a pedido dele e usava o código "
                 "'guerra na Ucrânia'. Foi demitido em 15/10/2026 após o vazamento; o Grupo Globo classificou a relação "
                 "como 'inadequada' com um anunciante e reafirmou a independência editorial. Perfil resumido exclusivamente "
                 "a partir das reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "elsinho-mouco", "name": "Elsinho Mouco", "photo": None,
     "role": "Publicitário; interlocutor de Michel Temer nas tratativas com o Master",
     "aliases": [],
     "summary": ("Fez a ponte entre Vorcaro e o escritório do ex-presidente Michel Temer no contrato de até R$ 30 milhões "
                 "para viabilizar a venda do Master ao BRB (setembro/2025), enviando o contrato e cobrando pagamentos, "
                 "conforme mensagens reportadas pelo UOL (14/10/2026). Perfil resumido exclusivamente a partir das reportagens "
                 "linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "michel-temer", "name": "Michel Temer", "photo": None,
     "role": "Ex-presidente da República (2016-2018); advogado",
     "aliases": ["Temer"],
     "summary": ("Seu escritório de advocacia firmou em setembro/2025 contrato de até R$ 30 milhões com o Master para consultoria "
                 "e mediação da venda ao BRB, barrada pelo BC. Confirmou em abril/2026 ter recebido honorários e que o contrato "
                 "terminou sem resultado. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação "
                 "nem conclusão sobre responsabilidade individual.")},
    {"id": "manuela-carta", "name": "Manuela Carta", "photo": None,
     "role": "Publisher e diretora da CartaCapital",
     "aliases": [],
     "summary": ("Segundo o UOL (15/10/2026), avisou Vorcaro da necessidade de recurso para a folha de pagamentos (2021) e tratou "
                 "de eventual sociedade com ele (2023), não concretizada. Em nota, afirma que o contrato com o banco era 'regular' "
                 "de publicidade e que Vorcaro nunca pediu interferência editorial. Perfil resumido exclusivamente a partir das "
                 "reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "isaac-sidney", "name": "Isaac Sidney", "photo": None,
     "role": "Presidente da Febraban; ex-diretor do BC e ex-advogado do Banco Máxima/Master",
     "aliases": ["Isaac"],
     "summary": ("Foi chefe de gabinete de Meirelles no BC, advogou para o Máxima na aprovação da transferência do controle a "
                 "Vorcaro e preside a Febraban desde 2020. Segundo o UOL (15/10/2026), Vorcaro pagou R$ 1,2 milhão fora da "
                 "escritura ao vendedor do apartamento dele e custeou parte do aluguel; a proposta de delação de Vorcaro o citou "
                 "— rejeitada por falta de provas. Nega qualquer benefício e diz ter alertado o BC sobre o Master em ofícios da "
                 "Febraban. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão "
                 "sobre responsabilidade individual.")},
    {"id": "eduardo-barcellos", "name": "Eduardo Barcellos", "photo": None,
     "role": "Empresário; vendedor do apartamento alugado e vendido a Isaac Sidney",
     "aliases": [],
     "summary": ("Tratou com Vorcaro o aluguel e a venda do duplex da Vila Olímpia ao presidente da Febraban; recebeu R$ 1,2 milhão "
                 "fora da escritura, segundo mensagens reportadas pelo UOL (15/10/2026). Procurado, disse não se lembrar da venda "
                 "e desligou o telefone. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação "
                 "nem conclusão sobre responsabilidade individual.")},
    {"id": "geraldo-samor", "name": "Geraldo Samor", "photo": None,
     "role": "Jornalista; fundador do Brazil Journal",
     "aliases": ["Samor"],
     "summary": ("Consultava Vorcaro sobre reportagens do Master antes da publicação e atendia pedidos de alteração, segundo o UOL "
                 "(15/10/2026); a participação do banqueiro no site se dava via Foone (49,86% da BJ Conteúdo). Não respondeu ao UOL. "
                 "Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão sobre "
                 "responsabilidade individual.")},
    {"id": "diogo-batista", "name": "Diogo Batista", "photo": None,
     "role": "Promotor de eventos em São Paulo",
     "aliases": ["Diogo"],
     "summary": ("Ganhava R$ 120 mil por mês de Vorcaro como executor do esquema de agenciamento investigado pela PF — um dos "
                 "principais investigados, ao lado de Leonardo Serrano; não respondeu ao UOL. Publicamos aqui apenas os trechos de "
                 "interesse público, preservando a privacidade das pessoas vulneráveis. Perfil resumido exclusivamente a partir das "
                 "reportagens linkadas; não constitui acusação nem conclusão sobre responsabilidade individual.")},
    {"id": "leonardo-serrano", "name": "Leonardo Serrano", "photo": None,
     "role": "Empresário de eventos; dono da SL Consulting (Flórida)",
     "aliases": ["Leo Serrano"],
     "summary": ("Cuidava da logística internacional dos eventos e emitia faturas (cerca de US$ 70 milhões em 21 notas) à Moriah "
                 "Asset, repassadas ao financeiro do Master, segundo o UOL (13/10/2026). Um dos principais investigados pela PF; "
                 "não respondeu ao UOL. Publicamos aqui apenas os trechos de interesse público, preservando a privacidade das pessoas "
                 "vulneráveis. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem conclusão "
                 "sobre responsabilidade individual.")},
    {"id": "tiago-polo", "name": "Tiago Polo", "photo": None,
     "role": "Intermediador que trabalhava agenciando modelos",
     "aliases": [],
     "summary": ("Explicou a Vorcaro o propósito da agência ('ajustar as meninas indiretamente') e ofereceu a Allure e a Ford Models, "
                 "segundo o UOL (13/10/2026). Publicamos aqui apenas os trechos de interesse público, preservando a privacidade das "
                 "pessoas vulneráveis. Perfil resumido exclusivamente a partir das reportagens linkadas; não constitui acusação nem "
                 "conclusão sobre responsabilidade individual.")},
]

# ------------------------------------------------------------- complementações
CARNEIRO_MSGS = [
    ("2023-12", None, "flavio-carneiro", "Não dá pra ele aparecer como sócio do Geraldo no Brazil Journal. Vai sujar a água",
     "Sobre como incluir Antônio Carlos Freixo Júnior (o 'Mineiro', dono da IstoÉ) na Foone sem ligá-lo ao site, segundo a reportagem."),
    (None, None, "daniel-vorcaro", "Na IstoÉ é que controlamos mais",
     "Em 2024, ao encomendar a Carneiro capa da IstoÉ Dinheiro sobre a farmacêutica Biomm, em que havia investido, segundo a reportagem."),
    ("2024-09", None, "daniel-vorcaro", "Qualquer coisa de Ciro, Arthur, Hugo não pode sair nada sem me falar",
     "Em setembro/2024, sobre publicações envolvendo Ciro Nogueira, Arthur Lira e Hugo Motta, segundo a reportagem."),
    ("2024-09", None, "flavio-carneiro", "Vou colocar o Lira nessa lista agora", "Resposta na mesma sequência, segundo a reportagem."),
    ("2025-03", None, "flavio-carneiro", "Vou te mandando as minutas e você analisa e publicamos",
     "Em março/2025, dois dias após o anúncio da compra do Master pelo BRB, sobre o site PlatôBR, segundo a reportagem."),
    ("2025-03", None, "flavio-carneiro", "Entra agora à noite!",
     "Ao enviar a Vorcaro a íntegra de entrevista do presidente do BRB, Paulo Henrique Costa, ao PlatôBR, segundo a reportagem."),
    ("2025-03", None, "daniel-vorcaro", "Colocar esse tema precatório no subtítulo também não é legal",
     "Reclamação da chamada da matéria; na manhã seguinte, com o texto já corrigido, voltou a reclamar do destaque aos precatórios, segundo a reportagem."),
    ("2025-03", None, "flavio-carneiro", "Vamo alterar agora", "Resposta na mesma sequência, segundo a reportagem."),
    ("2025-08", None, "daniel-vorcaro", "Não deixa Platô falar de Ciro e Rueda",
     "Em referência aos presidentes do PP, Ciro Nogueira, e do União Brasil, Antônio Rueda, segundo a reportagem."),
    ("2025-08", None, "daniel-vorcaro", "Tem que pegar o Platô e moer esse Cappelli",
     "Sobre Ricardo Cappelli, então presidente da ABDI e pré-candidato ao governo do DF, segundo a reportagem."),
    ("2025-08", None, "flavio-carneiro", "Vamo desancar esse desgraçado",
     "Resposta na mesma sequência; disse ainda que iria 'alinhar isso no Platô e no Correio', segundo a reportagem."),
]
CARNEIRO_EVENTS = [
    (None, "A Foone, empresa de Carneiro, é sócia do PlatôBR e teve 49,86% da BJ Conteúdo (Brazil Journal), criada em 2023; Carneiro também era investidor das publicações IstoÉ e IstoÉ Dinheiro, controladas por Antônio Carlos Freixo Júnior, o 'Mineiro', apontado pela reportagem como operador financeiro de Vorcaro.", REDE),
    (None, "Sobre a compra da Allure, a solução sugerida para incluir o 'Mineiro' foi 'fazer uma Foone 2 e pôr só o BJ lá', segundo a reportagem. Em abril/2025, quando o PlatôBR publicou notas negativas sobre o banco, Carneiro disse que pediria para tirar as reportagens do ar.", REDE),
    (None, "Segundo o UOL (15/10/2026, matéria sobre a demissão de Kachar), Vorcaro manifestou interesse em comprar espaço publicitário no Estadão e na Folha, mas comprou publicidade nos dois jornais através da Foone. Procurado sobre as mensagens e sua relação com PlatôBR e IstoÉ, Carneiro não se posicionou até a publicação.", KACHAR),
]
MOURAO_MSGS = [
    ("2024-10-21", None, "felipe-mourao", "Dcm está pago e fechado",
     "Confirmando o acordo com o site, segundo a reportagem."),
    ("2025-05", None, "daniel-vorcaro", "tirar isso imediato",
     "Sobre artigo crítico ao Master publicado pelo DCM; o texto foi apagado no mesmo dia, segundo mensagem de Mourão."),
]
MOURAO_EVENTS = [
    ("2024-10", "Após nota negativa, Vorcaro mandou Mourão fazer 'uma parceria direito' com o DCM (Diário do Centro do Mundo), com 'um valor mensal', sob a condição de não sair 'uma frase com meu nome ou Master'. Segundo Mourão, o diretor do site quis 'saber sobre os alvos' antes de fechar; dois dias depois o acordo estava firmado, o site removeria textos negativos e o grupo poderia publicar todo mês 'uma matéria positiva ou negativa de alguém'. O DCM foi procurado após a publicação.", REDE),
    (None, "Mourão já submetia a Vorcaro os textos que sairiam no site: em janeiro/2024, o banqueiro vetou menção ao pai, Henrique Vorcaro, e pediu que o nome dele fosse sempre desvinculado das reportagens.", REDE),
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
    if date and len(date) == 4:  # 'YYYY' -> sem precisão (o ano fica no texto do evento)
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
        ss = secs(spec["secs"])
        msgs = [new_msg(d, tm, s, c, n, spec["secs"]) for d, tm, s, c, n in spec["msgs"]]
        msgs.sort(key=lambda m: (m.get("date") or "9999-99", m.get("time") or "~"))
        for i, m in enumerate(msgs, 1):
            m["id"] = f"m-{i:05d}"
        events = []
        for d, c, src in spec["events"]:
            e = new_event(d, c, src)
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
        finalize(thread)
        out = T / f"{pid}-daniel-vorcaro.json"
        out.write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v6] {pid}: {len(msgs)} mensagens, {len(events)} eventos")

    # 2) complementações
    for tid, new_msgs, new_events in [
        ("flavio-carneiro", CARNEIRO_MSGS, CARNEIRO_EVENTS),
        ("felipe-mourao", MOURAO_MSGS, MOURAO_EVENTS),
    ]:
        p = T / f"{tid}-daniel-vorcaro.json"
        t = json.loads(p.read_text(encoding="utf-8"))
        have = {norm(m["content"]) for m in t["messages"]}
        added = 0
        for d, tm, s, c, n in new_msgs:
            if norm(c) in have:
                continue
            t["messages"].append(new_msg(d, tm, s, c, n, REDE))
            added += 1
        for d, c, src in new_events:
            t.setdefault("timeline_events", []).append(new_event(d, c, src))
        finalize(t)
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[v6] {tid}: +{added} msgs (total {len(t['messages'])}), eventos {len(t['timeline_events'])}")

    # 3) participantes
    pfile = REPO / "data" / "participants.json"
    people = json.loads(pfile.read_text(encoding="utf-8"))
    have = {x["id"] for x in people}
    for np_ in PARTICIPANTS_NEW:
        if np_["id"] not in have:
            people.append(np_)
    pfile.write_text(json.dumps(people, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[v6] participantes: {len(people)}")

    # 4) índice
    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
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
    print(f"[v6] índice: {len(index)} conversas")


if __name__ == "__main__":
    main()
