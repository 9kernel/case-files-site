# RELATÓRIO FINAL — Auditoria incremental de 29/10/2026 (rodada press11)

**Repositório:** 9kernel/case-files-site · branch `main`
**HEAD inicial = HEAD final:** `0933219b93899d694e3096d931dcff6aa9448361` (= `origin/main`; fetch sem novos commits; **sem commit, sem push e sem PR**, conforme determina esta rodada — alterações apenas na árvore de trabalho)
**Estado anterior:** 68 conversas · 1075 mensagens · 247 eventos · 1322 registros · 69 participantes
**Estado final:** **68 conversas · 1106 mensagens · 249 eventos · 1355 registros · 69 participantes**
**Backup pré-alteração:** `.backups/data-0933219-20261029-123941.zip` (75 arquivos)
**Scripts desta rodada (reprodutíveis):** `scripts/import_pipeline/fix_order_index_20261029.py` (reordenação + índices) e `scripts/import_pipeline/ingest_press11_20261029.py` (lote `ingest-press11-20261029`, 33 registros novos, selo "novo" conferido)

---

## 1. HEAD, árvore e preservação

Árvore inicialmente limpa em `0933219`; remoto sem novos commits; nenhum comando destrutivo; backup executado antes da primeira modificação; AGENTS.md idêntico ao da rodada anterior (nenhum commit desde então).

## 2. Correções críticas — ordem cronológica (Seção 2 da auditoria)

Quatro conversas reordenadas **por blocos de IDs**, sem renumerar, sem tocar em textos/notas/proveniências (verificação por hash registro a registro no script):

| Conversa | Bloco movido | Destino |
|---|---|---|
| ana-matos | 2024-04..10-10 (m-00014, m-00022..37) | início, antes do bloco 2024-11 |
| ana-matos | 2025-03-31..04-14 (m-00038..46, m-00048..53, m-00018/19, m-00047) | desmembrado: 31/03+03/04 antes de 04/04; 05/04 após o bloco 04/04..05/04; 14/04 antes de 18/04 |
| fabiano-zettel | m-00034 (~ago/2024, ">16/08") e m-00033 (02/10/2024 12h58) | entre 05/06/2024 e o bloco 2024-10 |
| paulo-henrique | m-00014..59 (negociação 30/04..22/05/2025) | antes de 19/08/2025 |
| walfrido-warde | m-00027..43 (set/2024..22/01/2025, bloco Veja) | após o bloco 2024-08, antes de 2024-11 |

Justificativas documentadas: o bloco 2024 da ana-matos já estava internamente cronológico; `m-00013` (sem data) permaneceu anexo ao bloco de julho/2025; no zettel, `m-00034` antecede `m-00033` por sua nota ancorá-lo "dias depois de 16/08/2024"; no paulo-henrique, `m-00013` (fl. 77) e `m-00014` (fl. 5) são sequências documentais distintas do mesmo IPJ-A — separáveis; no warde, o bloco deslocado era contíguo. Escaneamento com a regra nova em todo o repositório (mensagens e eventos): **zero inversões remanescentes**.

## 3. Validador endurecido — E_TIMESTAMP_ORDER além de registros sem data (Seção 3)

- `checkOrder` agora compara contra o **último registro comparável** (date/minute): mensagens/eventos sem data ou com precisão month/approximate **não interrompem mais a cadeia**. Approximate continua nunca comparando nem servindo de referência; mesmo dia sem hora em qualquer lado continua sem comparação.
- **14 testes de regressão** em `test-validate.mjs`: os quatro casos reais (ana-matos, zettel, paulo-henrique, warde), inversão de hora além de registro sem data, inversão em eventos, e quatro casos legítimos que não geram erro (sem data em ordem crescente, mês intermediário, approximate, mês no índice).

## 4. Índices — last_message_date (Seção 4)

- Semântica fixada: `last_message_date` = **última data conhecida da conversa** (máximo âncora temporal comprovado; âncora de mês posterior a toda data plena vence; mês igual perde para a data plena).
- Corrigidas as 7 conversas sinalizadas **+ 3 achadas pelo recompute**: angelo-silva (→2025-02-28), fabio-faria (→2024-09-03), flavio-carneiro (→2025-08, mês), luiz-renno (→2025-08-08), paulo-henrique (→2025-11-12 + preview), walfrido-warde (→2025-11-17 + preview), yasmin-brunet (→2025-01, mês), antonio-rueda (2024-07→2024-07-12), augusto-lima (mês 2025-02 preservado como âncora mais recente), marcus-vinicius (null→2024-04).
- **Guarda permanente no validador**: `E_INDEX_DATE_BAD` (formato) e `E_INDEX_DATE_STALE` (data anterior à última conhecida) — o índice não pode mais regredir silenciosamente; mesmo mês com âncora de mês nunca é tratado como comprovável (dia desconhecido). 5 testes de regressão.
- UI: `formatDateBR` suporta âncora de mês (mm/yyyy, dia nunca inventado); o `chatList` exibe a data com título "Última data conhecida da conversa".

## 5. Ingestões de conteúdo (Seções 5-10) — 31 mensagens + 2 eventos

Todas as citações verificadas em **duas extrações independentes ou confirmação dirigida caractere a caractere**; grafia original preservada; `(sic)` do veículo mantido; colchetes de inserção do veículo removidos do literal.

**ana-matos (+1, ICL 19/10):** m-00076 (15/10/2024, "Cnn deu um ruido grande. Nao gostei postura joao…"; "joao" = João Camargo). As sequências de 18-26-29/09 e 01/10 **já existiam** (a busca da auditoria não as localizou por grafia) — não duplicadas. O "primeiro aporte como acionistas" (16/10) é fala indireta → ampliou o evento de contexto CNN (e-00003); a negativa da CNN ("nunca foi sócio") já estava registrada.

**ciro-soares (+16 + evento, Noites Húngaras/ICL 03-28/10):** sequência de fevereiro/2025 — 07/02 ("Opa", "me liga", "Tô André M." às 14h03, com "[com]" do veículo removido), 08/02 (áudio "Fala, Vorcarinho…"), 16/02 (17h47 "O.A.M. quer recebê-lo…", "?" e "Marca quarta" de Vorcaro, "irmão caçula", três trechos do áudio de 1min39s — inclusive o trecho sobre o Banco Central, com nota expressa de que o **relato de Ciro não comprova interferência de Mendonça no BC**), 17/02 (19h08 "Cezinha confirmou às 16h de quarta") e 19/02 (áudio do Bruno Bianco — **agendamento comprovado, realização não**). Evento com as notas do gabinete (uma reunião em março/2025, STP 976, por iniciativa do empresário) e de Ciro (sigilo advogado-cliente). Perfil do participante estendido com `profile_sources`. Nível `public_investigation` com a cadeia declarada (Noites Húngaras→ICL).

**flavio-carneiro (+8 + correções + evento, Estadão 23/10 via Infoverus e ICL 03/09):**
- **m-00002 corrigida**: transcrição do Estadão preserva a grafia original ("Qq coisa de ciro arthur hugu nao pode sair nada sem me flaar") e a data individual 20/09/2024 — a versão anterior (UOL, normalizada, mês) permanece documentada na nota; fontes unificadas, sem duplicação.
- **m-00003 corrigida**: completada ("Ok. … Realmente nao tava"), 20/09/2024.
- Novas: 04/09/2024 (orientação sobre Hugo Motta), 20/09/2024 ("Porra cara. Tira isso do ar agora" — pedido de retirada ≠ retirada comprovada), dez/2024 ("Foda hein…"), 14/05/2025 (vídeo de Ciro Nogueira, typos originais), 17/07/2025 (matérias favoráveis a Motta + resposta de Carneiro) e o par de abril/2024 dos voos ("Vouch (sic) mandar soltsr isso").
- **m-00023 datada**: abril/2024 (mês, ICL; dia não divulgado) + fonte ICL acrescentada; reposicionada no bloco inicial.
- Evento com a manifestação de Arthur Lira (negou proximidade, nunca trocou mensagens, não responde por diálogos de terceiros) e os silêncios de Motta e Ciro Nogueira. Não se afirma que parlamentares solicitaram proteção editorial.

**lilian-tahan (+2, Estadão 23/10):** complemento de 02/04/2025 ("Mas tem que ser um jeito que nao pareça que nao tem interesse…" e "Deixa comigo" — distinto do m-00016 de agosto); a resposta mais completa de Tahan citada pelo Estadão tem correspondência indeterminável com m-00025 (contexto distinto no UOL) — sem unificação; manifestação da executiva preservada.

**cezinha (+1, ICL):** confirmação adicional de 13/03/2025 ("Amanhã sexta-feira 14 às 17:00"); divergência de ordenação entre ICL e CartaCapital documentada; endereço não republicado.

**andre-valadao (+3 ICL + m-00026 sem data):** m-00033 (pedido "De novo pedir sua ajuda com Nikolas…", 27/04/2024), m-00034 ("Oi Dani. Claro amanhã falo com ele"), m-00035 (áudio do pastor "Eu falei com ele né…", abril/2024, mês). Nível `secondary_source` (o ICL não declara cadeia de origem identificável — mesmo critério dos registros g1/UOL). **m-00026: data completa removida** (a fonte diz "15 de agosto" sem ano; o "dois meses" antes da prisão de 11/2025 é incompatível com 2024 para o bloco do terreno; ano indeterminado — sem presumir 2025). Notas de divergência de cronologia ICL×Pública adicionadas a m-00031/m-00032 (o ICL situa "estamos do mesmo lado" após 29/04 e o "Resumindo" após o áudio; mantidas data e transcrição da fonte citada).

**nikolas:** a nota da despedida de m-00001 ganhou a variante do ICL ("Um abraço, lindão." — transcrição idêntica à dos autos), reforçando a controvérsia documentada; e-00002 ampliado com o contexto de 2022 (≈10 dias no 2º turno, 9 estados + DF, pastor Guilherme Batista).

## 6. Documentos oficiais (Seção 11)

- **Pacote «Arquivos Pet 16704» (STF):** nova tentativa de acesso — servidor permanece inacessível do ambiente de verificação (HTTP 000). Grupo "Master" **mantém** `public_investigation`; nada promovido a `official_document`; nenhuma página inventada.
- **felipe-mourao m-00057 `[Luis Felipe]`:** o IPJ-A 1020625/2026 tem URL de processo no portal do STF, mas **sem cópia pública direta** (public_copy_url nula) — sem acesso à folha 45/figura 53, a transcrição não foi alterada (pendência mantida).
- **Relatório parcial da PF (28/10, indiciamento de 15):** nenhuma versão pública integral localizada; nenhuma mensagem criada a partir da reportagem; reportagem não classificada como documento oficial.

## 7. Testes executados — todos aprovados

`build-network` (68 contatos) · `build-search-index` (68 conversas, 1339 textos) · `build-whatsnew` (selo em 33 registros do lote press11) · **`validate`: 0 erros, 0 warnings** (68 · 1106 · 249; public_investigation=697, official_document=230, secondary_source=179) · `test-validate`: TODOS OS CASOS PASSARAM (incl. 14+5 regressões novas) · `test-whatsnew`: OK · `audit-public-provenance`: **1355/1355 OK** (829/275/251) · `check-email-leak`: 0.

## 8. Pendências sem evidência suficiente

1. **Carneiro, mensagens longas de abril/2024** ("Babaquice isso…" e a da nota do Grupo Voto): duas extrações divergiram em um caractere ("sem medir das/as consequencias") e o miolo longo não pôde ser capturado com certeza — **não importadas**; exigem conferência direta das capturas.
2. **felipe-mourao m-00057**: colchete sem conferência na folha 45/fig. 53 (sem cópia pública acessível).
3. **PET 16704**: peça individual do grupo "Master" e das trocas de abril/2025 de Paulo Sérgio segue por localizar.
4. **m-00025 (tahan) × resposta completa do Estadão**: correspondência indeterminável — sem unificação.
5. **Relatório parcial da PF (28/10)**: sem versão pública integral — monitoramento.

---

**PRINCÍPIO CENTRAL OBSERVADO:** nenhuma mensagem apresentada como literal sem correspondência verificável com a fonte publicada; nenhuma alegação apresentada como fato comprovado sem evidência suficiente. **Nenhum commit, push ou PR executado** — árvore de trabalho aguardando autorização expressa.
