# RELATÓRIO FINAL — Auditoria incremental de 27/10/2026 (rodada press10)

**Repositório:** 9kernel/case-files-site · branch `main`
**HEAD inicial = HEAD final:** `e6546a96eab756c57d0f3ca81519e13c12fbc5eb` (= `origin/main`; `git fetch` sem novos commits; **sem commit, sem push e sem PR**, conforme autorização expressa exigida)
**Estado anterior:** 67 conversas · 1065 mensagens · 243 eventos · 1308 registros · 68 participantes
**Estado final:** **68 conversas · 1075 mensagens · 247 eventos · 1322 registros · 69 participantes**
**Backup pré-alteração:** `.backups/data-e6546a9-20261027-113104.zip` (74 arquivos, via `scripts/backup_local.py`)
**Script desta rodada (reprodutível):** `scripts/import_pipeline/ingest_press10_20261027.py` · lote de inserção: `ingest-press10-20261027` (14 registros novos, selo "novo" conferido)

---

## 1. HEAD, árvore e preservação

Árvore inicialmente limpa em `e6546a9`; sem commits locais não publicados, sem arquivos não rastreados a preservar (o diretório `.backups/` é gerado pelo próprio fluxo). Nenhum comando destrutivo (`reset --hard`, `clean`) executado; o remoto não foi alterado. Todas as alterações permanecem apenas na árvore de trabalho.

## 2. Auditoria do merge de 26/10 (`e6546a9`) — sem repetição das correções já feitas

- **Baseline da suíte completa** (8 comandos do CI) antes de qualquer alteração: tudo aprovado — validador 0 erros/0 warnings; auditoria de proveniência 1308 registros/0 problemas; leak-check 0; contagens batendo com o declarado no merge (67 · 1065 · 243; 275/786/247).
- **Unicidade de IDs:** verificada em todos os 67 threads (mensagens + eventos) — nenhuma duplicata.
- **Índices:** `threads.json` `message_count` conferido contra os arquivos reais para as 67 conversas — sincronizado; `whatsnew.json` sincronizado com `CURRENT_BATCHES` (teste dedicado passou).
- **IDs fora de ordem numérica** em 15 threads: verificados — convenção documentada do repositório (numeração por ordem de inserção, posicionamento cronológico), **preexistente em ambos os pais do merge** (`4265d3c` e `8957b45`); não é corrupção.
- **Deduplicação do Walfrido Warde:** exatamente **9 mensagens** com nota "[Deduplicado 2026-10-26 (merge)]", cada uma indicando o ex-ID consolidado — confere com o declarado; nenhuma duplicata remanescente.
- Índices regenerados no baseline produziram apenas ruído LF/CRLF (diff vazio) — **não havia dessincronização**; nada foi renumerado.

## 3. Pendências implementadas

### 3.1 André Valadão — mensagens de 27/04/2024 (alta · mensagens literais ausentes)

**Fonte:** Agência Pública, 18/10/2026 ("Master: Em mensagens, Vorcaro declarou lado sem margem para dúvida: 'apoiamos a direita'"), texto integral conferido. Inseridas **4 mensagens** (`m-00029`–`m-00032`, 2024-04-27, posição cronológica após `m-00005`): três de Vorcaro (reclamação da repostagem de Nikolas; "apoiamos a direita"; explicação do patrocínio do evento de Londres com Tony Blair e o "estamos do mesmo lado ou um contra o outro") e uma de Valadão ("Resumindo, ele nem sabia sobre o banco e você…", relatando a conversa e o pedido de desculpas de Nikolas). Colchetes `[Gaspar]`/`[Nikolas]` (inserções do veículo) removidos do literal e documentados em nota. O relato de Valadão **não** foi transformado em mensagem direta de Nikolas; declaração de apoio político não foi apresentada como prova de financiamento. Nível `public_investigation` (procedimento PF declarado; peça não publicada individualmente), no padrão do próprio thread.

### 3.2 Nikolas Ferreira — áudio de 30/03/2025 (crítica · risco de duplicação)

**Fontes:** g1/GloboNews (04/09/2026, transcrição conferida), UOL (03/09/2026), Folha (03/09/2026), Agência Pública (18/10/2026).

- **Continuidade confirmada por duas vias independentes:** a Folha ("Ainda na mensagem de voz…") e a Pública ("Em áudio de março de 2025…") situam o trecho de Londres/Valadão no **mesmo áudio de 30/03/2025**; o g1 publica transcrição única contendo pedido (ativo minerário) **e** retomada de Londres.
- **Achado crítico:** o `content` anterior de `m-00001` **não correspondia à transcrição publicada pelo g1** (era uma variante divergente — mencionava "TSE", "interceder" — embora o registro atribuísse o texto ao g1 e o declarasse integral). Substituído pela transcrição do g1, cujo trecho inicial é idêntico ao publicado pelo UOL na parte sobreposta (verificação cruzada).
- **Despedida suprimida do literal** (`[…]` do projeto + `literal_brackets: true`): a palavra final tem transcrições divergentes documentadas (g1: "Um abração aí, Dani"; UOL, em nota: não fica claro entre "abraço aí, Dani" e "um abraço, lindão"; transcrição oficial dos autos: "lindão", segundo a Folha; Nikolas nega) — nenhuma variante reproduzida como literal.
- **Abertura do UOL** ("Ei Dani, tudo bom? … é jogo rápido") não costurada à transcrição do g1 (transcritores distintos) — por isso `transcription.complete = false` (a transcrição é parcial em relação ao áudio).
- **Nenhuma segunda mensagem de áudio criada; `m-00002` não duplicada.** Fontes unificadas (g1 + UOL + Folha + Pública). Adicionada `m-00003` ("Deixa comigo", 30/03/2025, UOL — resposta ao áudio no mesmo dia) e a nota de `m-00002` corrigida (a resposta em visualização única é mensagem distinta, sem transcrição publicada).

### 3.3 Grupo "Master" (Banco Central) — alta · grupo documental ausente

**Fontes:** BBC News Brasil (Luiz Fernando Toledo, 11/09/2026, republicada pelo Estado de Minas — citações extraídas em duas passagens independentes com strings idênticas) e CNN Brasil (11/09/2026).

- Ausência reconfirmada no índice de 67 conversas → **thread criado:** `grupo-master-belline-paulo-sergio` (Vorcaro · Belline Santana · Paulo Sérgio Neves de Souza), criado em 02/10/2025 por Belline, conforme as duas reportagens.
- **3 mensagens literais:** criação ("Boa tarde. Criei esse grupo, no intuito de facilitar nossa interlocução", Belline, 02/10/2025); "Segue minuta para avaliação" e "Por favor, vejam se atende" (Vorcaro, 27/10/2025, esta após nova versão da minuta).
- **Chamada de voz de Belline (27/10/2025): sem transcrição publicada → evento editorial**, não mensagem. Conversas de 13/10/2025 (CNN, narradas) → evento editorial.
- **Nível `public_investigation`** com cadeia de origem declarada (representação PF ao STF de 27/02/2026, tornado pública após levantamento de sigilo — Min. André Mendonça, a pedido do presidente da corte, conforme CNN). **`official_document` não utilizado:** a peça individual não foi localizada — o pacote público «Arquivos Pet 16704» do STF está **inacessível a partir do ambiente de verificação** (falha de conexão a `docspublicos.stf.jus.br`); a limitação está registrada no `proceeding`. Sem páginas atribuídas.
- As conclusões da PF (favorecimento, pagamentos) permanecem como **alegações investigativas**, com as manifestações das defesas (Belline, Paulo Sérgio) e os silêncios (BC, BRB, Reag) registrados em evento de contexto.
- Participante **`belline-santana`** criado em `participants.json` (com `profile_sources`); conversas individuais anteriores a 02/10/2025 **não** atribuídas ao grupo.

### 3.4 Paulo Sérgio — mensagens individuais de 25/04/2025 (alta)

**Fonte:** BBC News Brasil, 11/09/2026. O pedido de Vorcaro e as sugestões de edição (troca de "captação de receitas" por "captação de recursos", referências ao BRB, correção de data) são **narração jornalística** → **evento editorial** (`e-00002`), sem transcrição publicada do pedido. As duas falas publicadas entre aspas entraram como **mensagens literais** (`m-00009` "Importante protocolar rapidamente"; `m-00010` "entendo imprudente citar problema no canal BRB", 25/04/2025) — troca **individual**, explicitamente anterior ao grupo "Master" (02/10/2025). Não se afirma que as recomendações foram adotadas. Ressalva de identidade do participante (contato do IPJ-A vs. ex-dirigente citado pela imprensa) preservada no perfil e citada nas notas. Perfil estendido com `profile_sources` (BBC).

### 3.5 Valadão `m-00027` — ano não comprovado (alta · precisão temporal)

Texto integral da Agência Pública (24/10/2026) conferido: a passagem menciona "17 de setembro" **sem ano**. A verificação encontrou evidência contrária à derivação anterior: a própria reportagem situa as últimas discussões do terreno "**dois meses**" antes da prisão de novembro/2025 — incompatível com setembro/2024 para aquele bloco (o "17 de setembro" da seção do terreno; o da fintech, embora em seção distinta, pode ser o mesmo dia). Como nem 2024 nem 2025 são individualmente comprováveis, **a data completa foi removida** (`m-00027` sem `date`), preservando "17 de setembro" na nota editorial com o registro da ambiguidade e da evidência. **Nenhuma outra data foi alterada** — ver pendência sobre `m-00026` no item 5.

### 3.6 Colchetes editoriais (alta · integridade editorial)

Todas as 24 ocorrências de `literal_brackets: true` foram inventariadas e classificadas; **13 registros corrigidos** (inserção do veículo confirmada na fonte, fonte a fonte):

| Thread · mensagem | Colchete | Fonte conferida |
|---|---|---|
| ana-matos `m-00002` | `[da]` | UOL (Agostini/Dantas), 15/10 |
| tiago-polo `m-00001` | `[que]` | UOL — coluna Portinari, 13/10 |
| diogo-batista `m-00018` | `[as duas]` | UOL — coluna Portinari, 13/10 |
| frederic-kachar `m-00024` | `[Brasil]` + glosa `[conteúdo patrocinado...]` | Agência Pública, 15/10 |
| frederic-kachar `m-00026` | `[Jardim]` | Agência Pública, 15/10 |
| frederic-kachar `m-00031` | `[Campos]` | Agência Pública, 15/10 |
| frederic-kachar `m-00032` | `[Gaspar]` | Agência Pública, 15/10 |
| martha-graeff `m-00014` | `[Motta…]` (publicação real: glosa completa) | Folha, 05/03 |
| martha-graeff `m-00017` / `m-00021` | `[de]` | Folha, 05/03 |
| martha-graeff `m-00020` | `[?]` (marcador de incerteza do veículo) | Folha, 05/03 |
| martha-graeff `m-00023` | `[sic]` ×2 + `[apartamento]` | Folha, 05/03 |
| walfrido-mares-guia `m-00009` | `[Anvisa]` | Folha, 30/09 |

Em todos: inserção removida do `content`, esclarecimento preservado em `editorial_note` com marcador "[Corrigido 2026-10-27: …]", `added_in` original mantido. **Mantidos sem alteração:** marcadores de corte (`[…]`/`(…)`: ana-matos `m-00016`, hamilton-buzelin `m-00001`, julio-cezar `m-00029`/`m-00030`, leonardo-serrano `m-00002`/`m-00008`/`m-00009`), supressão de privacidade do projeto (felipe-mourao `m-00029` `[nome suprimido]`) e o corte do projeto em frederic-kachar `m-00024` (`literal_brackets: true` mantido). Nenhum trecho omitido foi reconstruído.

### 3.7 Documentação

- `AUDIT-REPORT-2026-10-26.md`: **nota histórica acrescentada** distinguindo `b860897` (execução original), `3aef62e` (commit de incorporação) e `e6546a9` (merge posterior), sem reescrever resultados.
- `README.md`: bloco "*Números correntes*" atualizado (27/10/2026 · 68 · 1075 · 247 · 1322).
- `scripts/build-whatsnew.mjs`: `CURRENT_BATCHES` → `ingest-press10-20261027` (14 registros com selo, conferido pelo teste do CI).

## 4. Testes executados (pós-alterações) — todos aprovados

`build-network` (68 contatos) · `build-search-index` (68 conversas, 1306 textos) · `build-whatsnew` (selo em 14 registros do lote corrente) · **`validate`: 0 erros, 0 warnings** (68 threads · 1075 mensagens · 247 eventos; public_investigation=669, official_document=230, secondary_source=176) · `test-validate`: TODOS OS CASOS PASSARAM · `test-whatsnew`: OK · `audit-public-provenance`: **1322 registros · OK=1322 · problemas=0** (799/275/248) · `check-email-leak`: 0 achados.

## 5. Pendências sem evidência suficiente (registradas, sem alteração)

1. **`m-00026` (andre-valadao, "15 de agosto")**: a mesma ausência de ano da fonte afeta essa mensagem e o bloco do terreno ("31 de julho"–"17 de setembro"); a frase "dois meses após" sugere 2025 para o bloco do terreno. Instrução expressa desta rodada: não alterar datas de outras mensagens — **pendência aberta para o responsável**, com a evidência registrada na nota de `m-00027`.
2. **felipe-mourao `m-00057` `[Luis Felipe]`**: registro de nível documento oficial (IPJ-A 1020625/2026, fl. 45, fig. 53); sem acesso à peça nesta rodada, não é determinável se o colchete consta da transcrição da PF — mantido.
3. **Pacote «Arquivos Pet 16704» (STF)**: inacessível do ambiente de verificação; peça individual e páginas das mensagens do grupo "Master" e das trocas de abril/2025 de Paulo Sérgio permanecem por localizar (nível `official_document` permanece vedado até lá).
4. **Mensagens adicionais publicadas pela BBC** sem data individual ou fora do escopo desta rodada: "tá sendo um anjo na vida" (Vorcaro a Zettel sobre Paulo Sérgio) e "ruídos desnecessários" (Belline, fragmento) — não importadas (sem mandato específico/data; disponíveis na fonte).
5. **Despedida do áudio de Nikolas**: nenhuma variante verificável — controvérsia documentada em nota; supressão mantida.

---

**PRINCÍPIO CENTRAL OBSERVADO:** nenhuma mensagem foi apresentada como literal sem correspondência verificável com a fonte publicada; nenhuma alegação foi apresentada como fato comprovado sem evidência suficiente. **Nenhum commit, push ou PR executado** — alterações apenas na árvore de trabalho, aguardando autorização expressa.
