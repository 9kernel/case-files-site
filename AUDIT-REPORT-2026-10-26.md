# RELATÓRIO FINAL — Auditoria incremental de 26/10/2026

**Repositório:** https://github.com/9kernel/case-files-site · branch `main`
**HEAD auditado e final:** `b860897596dafad139366f4a12d4a00ce474c989` (sem commits locais; **sem push e sem PR**, conforme autorização expressa exigida)
**Estado anterior:** 64 conversas · 861 mensagens · 208 eventos · 1.069 registros
**Estado final:** **65 conversas · 959 mensagens · 221 eventos · 1.180 registros · 66 participantes**
**Backup pré-alteração:** `.backups/data-b860897-20261026-115949.zip` (71 arquivos, via `scripts/backup_local.py`)
**Scripts desta rodada (reprodutíveis):** `scripts/import_pipeline/ingest_press9_valadao.py`, `fix_press8_gusttavo.py`, `fix_press8_elmar_netinho_zettel.py`, `fix_participants_20261026.py`, `ingest_press9_missing.py` · lote de inserção: `ingest-press9-20261026`

---

## 1. HEAD e integridade

HEAD inicial = HEAD final = `b860897`; `origin/main` sem novos commits; árvore de trabalho inicialmente limpa (nenhuma alteração local ou arquivo não rastreado a preservar). Nenhum comando destrutivo (`reset --hard`, `clean`) executado. Alterações mantidas apenas na árvore de trabalho.

## 2. Pendências implementadas

| Pendência da auditoria | Resultado |
|---|---|
| Conversa André Valadão ausente | **Criada** (28 mensagens literais + 4 eventos, Agência Pública 24/10/2026) |
| Gusttavo Lima m-00001 — contexto do Fantástico | **Corrigido** (Balada Eventos / Polícia Civil de PE / bloqueio de R$ 20 mi — não Vorcaro) |
| Gusttavo Lima m-00005 — `[nos]` editorial | **Corrigido** (colchete separado do literal; `literal_brackets` removido) |
| Gusttavo Lima m-00006 — transcrição parcial | **Completada** com o restante publicado ("Tá doido?! Vai me matar de saudade") |
| Gusttavo Lima m-00016 — `[de]` editorial | **Corrigido** (mesmo tratamento; achado na auditoria do lote press8) |
| Elmar — m-00001/e-00001 incorretos | **Reescritos** (transcrição, data e hora falsos substituídos; 03/10/2024 à tarde, sem hora inventada) |
| Netinho — m-00001–m-00004 e e-00001 sem fonte | **Removidos**; mensagens publicadas inseridas; festival corrigido para Campo Formoso (BA), 5–7/09/2024 |
| Zettel — m-00033–m-00035 sem fonte | **Removidos**; inseridas as falas comprovadas (02/10/2024 12h58 e "1mm") |
| Perfis Valverde / Netinho / Elmar | **Corrigidos** em `participants.json` (Valverde nunca foi presidente do BRB) |
| Rennó — Marçal 17/08/2024 | **Inseridas** 6 mensagens |
| Carneiro — Marçal 02/09/2024 | **Inseridas** 3 mensagens ("Léo" sem identificação) |
| Rennó — Nikolas 02 e 08/04/2025 | **Inseridas** 4 mensagens (na conversa de Rennó; áudio de Nikolas não duplicado) |
| Ana Matos — CNN Money e influenciadores | **Inseridas** 32 mensagens (2024–2025), deduplicadas com m-00018/m-00019; m-00014 (`[Nikolas]`) corrigido; ressalva de m-00019 preservada |
| Paulo Sérgio — Caixa Asset 12/07/2024 | **Inseridas** 4 mensagens como `secondary_source`, com ressalva de identificação; página documental de março/2025 não reutilizada |
| Mourão — sequências BBC (31/01/2024, 02 e 25/09/2024, 23/10/2025 e outras) | **Inseridas** 15 mensagens + 1 evento |
| Auditoria do lote `ingest-press8-20261023` | **Executada** (68 registros em 8 conversas: colchetes, duplicações, atribuição, datas — ver §5–§8) |

## 3. Conversa nova

**`andre-valadao-daniel-vorcaro`** — 28 mensagens, 4 eventos, participante `andre-valadao` criado (aliases: "Dede"). Fonte única: Agência Pública (24/10/2026). Datas atribuídas somente às divulgadas (09/12/2023, 16/04/2024, 14/07/2024, 16/07/2024 por derivação determinística de "dois dias depois", 23/07/2024, 15/08/2024, 17/09 com nota de derivação); demais sem data. Áudios registrados como `verbatim_excerpt` com nota de transcrição do veículo. Proposta de doação, negociações e planos registrados como propostas — nunca como transferência/aquisição/execução comprovadas.

## 4. Movimentação de mensagens (por conversa)

| Conversa | Antes → Depois | Removidas (sem evidência) | Adicionadas | Corrigidas |
|---|---|---|---|---|
| andre-valadao (nova) | 0 → 28 | — | 28 | — |
| gusttavo-lima | 17 → 17 | — | — | 4 (m-00001, m-00005, m-00006, m-00016) |
| elmar-nascimento | 1 → 8 | — (substituída) | 7 | 1 (m-00005, ex-m-00001) |
| netinho-lins | 4 → 4 | 4 | 4 | — |
| fabiano-zettel | 35 → 34 | 3 | 2 | — |
| luiz-renno | 10 → 20 | — | 10 | — |
| flavio-carneiro | 23 → 26 | — | 3 | — |
| ana-matos | 21 → 53 | — | 32 | 1 (m-00014) |
| paulo-sergio | 1 → 5 | — | 4 | — |
| felipe-mourao | 87 → 102 | — | 15 | — |
| **Total** | **861 → 959 (+98)** | **7** | **105** | **6** |

Eventos editoriais: 208 → 221 (+13; 1 evento de Netinho integralmente reescrito).

## 5. Correções de autoria e atribuição

- Nenhuma autoria invertida foi encontrada nas correções; todas as remetentes/destinatários das mensagens novas foram conferidos na fonte (incluindo "Dede" = Valadão e "Dani" = Vorcaro na reportagem da Pública, e o repasse de Carneiro a Vorcaro em 02/09/2024).
- **"Léo" (ICL, Carneiro 02/09/2024) mantido sem identificação** — a reportagem afirma não haver indícios de quem seja; nenhuma associação a Leonardo Valverde ou outro participante foi feita.
- Mensagens do motorista de Vorcaro e de Netinho citadas em fala indireta pelo UOL **não foram registradas como mensagens** de Elmar/Netinho (seria atribuição indevida); viraram contexto em eventos.
- Identidade "Paulo Sergio" (IPJ-A: "Diretor do Banco Central") vs. Paulo Sérgio Neves de Souza (Folha: ex-diretor): correspondência plausível, **não comprovada individualmente** — registrada como ressalva na conversa, no evento e no perfil.

## 6. Correções de datas

- Elmar: agradecimento 25/10/2024 09:30 → **03/10/2024 (tarde, sem hora)**; entrega 24/10 23h27 → **02/10/2024 19h11**; adicionadas 15/08, 01/10, 02/10 e 07/10/2024.
- Zettel/festival: setembro/2025 → **agosto/2024** (não apenas o ano corrigido: transcrições inexistentes removidas e o registro correto é de 16–17/08/2024).
- Netinho: outubro/2024 → **16/08/2024 e seguintes**; festival Angatuba (SP)/2025 → **Campo Formoso (BA), 5–7/09/2024**.
- Valadão: datas apenas as publicadas; "dois dias depois" (14/07) e "meses depois" tratados distintamente (derivável → 16/07/2024 com nota; não derivável → sem data).

## 7. Duplicações eliminadas

- Nenhuma duplicata de texto encontrada entre as inserções e os registros existentes. Casos verificados: `m-00018`/`m-00019` de Ana Matos (05/04/2025) já cobriam duas mensagens do ICL — não duplicadas (divergência de transcrição entre veículos preservada: cada registro cita a sua fonte); `m-00020` de Mourão provém de documento oficial da PF (IPJ-A 1020625/2026, fl. 79), distinto da sequência BBC de 02/09/2024; áudio de Nikolas (30/03/2025) não duplicado da conversa própria.

## 8. Proveniência

- Novas mensagens ICL/UOL/Pública: nível `public_investigation` com cadeia declarada em `verification.proceeding` (apreensão PF + obtenção pelo veículo; procedimento nomeado apenas quando a reportagem nomeia — Pública/Compliance Zero).
- Mensagens Folha (Paulo Sérgio) e BBC (Mourão): nível `secondary_source` — a força da afirmação não excede a evidência; **nenhuma** peça oficial ou página documental foi reutilizada para sustentar mensagens que não contém.
- Auditoria do lote `ingest-press8-20261023` (68 registros): colchetes editoriais corrigidos onde eram inserção de palavra do veículo (gusttavo m-00005/m-00016, ana-matos m-00014); marcador de corte `[…]` (ana-matos m-00016) mantido visível como corte, documentado em nota; supressões de privacidade do próprio projeto (acm-neto m-00004, mourao m-00029) mantidas; registros dos lotes anteriores (press3/4/5/7) com colchetes de veículo **fora do escopo** — listados como pendência de padronização.
- Resultado da auditoria estrutural: 1.180/1.180 OK — aprovação estrutural **não** tratada como prova de fidelidade literal; a conferência literal foi feita mensagem a mensagem contra as nove fontes abaixo.

## 9. Privacidade

Não publicados: contatos do motorista; dados bancários/CNPJ/contas (DuBem, proof of funds, comprovantes Pix); quebra individual do Coaf com nomes de familiares de Vorcaro (apenas agregado da entidade no evento da Lagoinha Belvedere); número de telefone de Marçal repassado por Vorcaro; dados de login/domínio em nome de parente do jornalista do blog; nome do jornalista do blog; sequência de vigilância sobre mulher (01/11/2023, BBC) e títulos de anexos TechBusca — resumidos em evento, sem transcrição. Contraditório preservado em todas as conversas tocadas (Valadão, defesa de Vorcaro, CNN, Paulo Sérgio/Caixa, Folha, piauí, Marçal, Elmar).

## 10. Fontes individuais utilizadas (conferência literal)

1. Agência Pública (24/10/2026) — Valadão/Lagoinha
2. Agência Pública (21/10/2026) — Gusttavo Lima/Super BH
3. UOL — coluna Natália Portinari (22/10/2026) — Elmar/Netinho/Zettel
4. UOL — coluna Natália Portinari (21/10/2026) — BRB-Master/Valverde (perfil)
5. ICL Notícias (24/10/2026) — Marçal (Rennó e Carneiro)
6. ICL Notícias (23/10/2026) — Nikolas/ativo minerário (Rennó)
7. ICL Notícias (19/10/2026) — CNN/Ana Matos
8. ICL Notícias (20/10/2026) — influenciadores/Marçal (Ana Matos)
9. Folha C-Level (22/10/2026) — Paulo Sérgio/Caixa Asset
10. BBC News Brasil (23/10/2026) — Mourão/remoção de conteúdo (versão canônica bbc.com; a reprodução do O POVO veio sem a introdução)

## 11. Testes executados (todos aprovados)

`build-network.mjs` (65 contatos) · `build-search-index.mjs` (1.164 textos) · `build-whatsnew.mjs` (120 selos) · `validate.mjs data` — **0 erros/0 warnings** · `test-validate.mjs` — todos os casos · `audit-public-provenance.mjs` — **1.180 registros, 0 problemas** · `check-email-leak.mjs` — 0 achados. Não existe `package.json` no repositório; a suíte acima é o conjunto completo de testes definidos. `README.md` e `PUBLIC-PROVENANCE-AUDIT.md` regenerados com os números de 26/10/2026.

**Selo "novo" (whatsnew):** o `CURRENT_BATCHES` de `scripts/build-whatsnew.mjs` foi atualizado de `ingest-press8-20261023` para `ingest-press9-20261026`, conforme exige a convenção do próprio script ("a cada rodada nova: atualize CURRENT_BATCHES") — sem isso, as 120 inclusões da rodada não receberiam o selo. As 9 conversas alteradas exibem agora os selos: ana-matos (34), andre-valadao (32), elmar (9), zettel (3), mourão (16), carneiro (4), rennó (12), netinho (5), paulo-sergio (5). Registros apenas **corrigidos** (ex.: gusttavo m-00001/05/06/16, ana-matos m-00014, elmar m-00005) mantêm o `added_in` original — a convenção do selo marca inclusões, não edições; as correções ficam documentadas nas notas "[Corrigido 2026-10-26]" de cada registro.

## 12. Pendências não implementadas por insuficiência de evidência

- Elmar 01/10/2024 (pergunta sobre "o contato da pessoa que vai ser procurado") e Vorcaro/Valadão ("com apetite pra isso", "análise dessa área"): apenas fragmentos em fala indireta — não registrados como mensagens.
- Agradecimento de Valadão após 16/07/2024 ("Amém Dani"/"Tô aqui Dani") e pedido de orientação jurídica de abril/2024: sem transcrição integral publicada — apenas contexto em eventos.
- Ano do "17 de setembro" (seção Orlando, Pública): ambíguo na fonte — o evento não compromete o ano; a mensagem do Clava Forte (m-00027) ficou 17/09/**2024** por derivação narrativa documentada em nota.
- Colchetes de inserção do veículo em lotes anteriores ao press8 (ana-matos m-00002 `[da]`; diogo-batista m-00018 `[as duas]`; martha-graeff; frederic-kachar; tiago-polo; walfrido-mares-guia): fora do escopo desta auditoria — recomenda-se padronização em rodada própria, com conferência fonte a fonte.
- `[…]` de ana-matos m-00016 mantido (remoção fabricaria continuidade de texto).
- Início da matéria do UOL (22/10) não acessível na versão pública lida (corte após o primeiro parágrafo); todo o material citado foi conferido na porção acessível, que contém todas as transcrições utilizadas.

---

**PRINCÍPIO CENTRAL OBSERVADO:** nenhuma mensagem foi apresentada como literal sem correspondência verificável com a fonte publicada; nenhuma alegação foi apresentada como fato comprovado sem evidência suficiente. Nenhuma alteração no remoto; commit/push pendentes de autorização expressa.
