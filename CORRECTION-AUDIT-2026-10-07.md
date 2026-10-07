# CORRECTION-AUDIT — Correção de proveniência, privacidade e metadados (2026-10-07)

Relatório da tarefa «CORRIGIR PROVENIÊNCIA, PRIVACIDADE E METADADOS DO CASE FILES».
Estado anterior preservado em [`data/audit/pre-fix-audit.json`](data/audit/pre-fix-audit.json);
auditoria por mensagem em [`PUBLIC-PROVENANCE-AUDIT.md`](PUBLIC-PROVENANCE-AUDIT.md);
detalhe por peça em [`DOCUMENT-AUDIT.md §10`](DOCUMENT-AUDIT.md).

---

## Proveniência

```text
mensagens auditadas:          335 (+48 eventos editoriais = 383 registros)
official_document antes:      232 mensagens (+43 eventos)
official_document depois:     232 mensagens (+43 eventos)
public_investigation:         74
secondary_source:             29
pending_review:               0 (nada visível na versão pública)
```

**Nenhuma mensagem foi rebaixada** — a verificação documental confirmou que os
5 documentos com «publicidade em verificação» são, todos, **peças íntegras do
pacote público «Arquivos Pet 16704» do STF** (levantamento de sigilo de
10/09/2026, disponibilização documentada em 15/09/2026). A inconsistência
central da missão (mensagens `official_document` citando peças com publicidade
pendente) foi resolvida **pela evidência**, não pela reclassificação:
- 3 peças confirmadas por nome de arquivo/bytes idênticos na origem pública;
- 2 peças (IPJ 1752768 e Representação PET 15.499) confirmadas por **SHA-256
  recalculado na origem pública** (download da peça no pacote do STF e
  recálculo do hash — `1a23d4f0…` e `36d991a8…`, idênticos aos locais).

## Documentos

```text
documentos com publicidade confirmada: 6 de 7
  pf-ipja-3298613-2026   (PET 16662 — 01/09/2026, cópia pública Poder360)
  pf-ipja-1070759-2026   (PET 15.978 peça 3 · PET 15.556 peça 4 · +5 petições)
  pf-ipja-1020625-2026   (PET 15.978 peça 4 · PET 15.499 peça 2 · +6 petições)
  pf-ipj-1752768-2026    (PET 15.978 peça 14 — SHA-256 verificado na origem)
  pf-repr-pet15-499      (peça íntegra pública como PET 15.977 peça 2 — SHA-256 verificado)
  pf-ipja-1252786-2026   (INQ 5026 peça 792 · PETs 15771/15772/15773 peça 10)
documentos com publicidade não confirmada: 0
documentos com estado desconhecido (null): 1 — stf-inq-5070 (processo de
  referência; pasta pública existe no pacote, nenhuma peça atribuída, nenhuma
  mensagem o cita como fonte)
documentos com e-Doc/peça localizado: 4 (1070759→3, 1020625→4, 1752768→14,
  1252786→792 — referências da missão CONFIRMADAS contra os autos públicos)
documentos sem e-Doc: pf-repr-pet15-499 (e-Doc na própria PET 15.499 não
  localizado; publicidade comprovada via PET 15.977 peça 2) e
  pf-ipja-3298613-2026 (cópia pública jornalística sem e-Doc declarado)
```

As referências «PET 15.978 e-Doc 3/4/14» indicadas na missão foram
**confirmadas**: os arquivos públicos dessas peças são byte-idênticos (e, no
caso do e-Doc 14, SHA-256-idênticos) aos arquivos locais. Não foram aceitas
pela instrução — foram verificadas na origem. Duas associações de registro
estavam erradas e foram corrigidas: IPJ 1752768 (「PET 15.562」→ **PET 15.978**;
a peça não consta da pasta pública da 15.562) e IPJ-A 1252786 (「pacote OneDrive
da Pet 16704」→ **INQ 5026**; a Pet 16704 é o veículo oficial de publicação, não
um processo).

## Correções

```text
mensagens rebaixadas:        0 (não houve necessidade — evidência confirmou publicidade)
mensagens promovidas:        0
mensagens sem alteração:     335 (nenhum texto literal tocado)
metadados preenchidos:       125 registros com verification.case null → preenchido
                             275 registros com verification.official_url null → URL oficial
                             4 threads com source.url vazio → URL oficial do processo
redações de dados pessoais:  2 notas editoriais (telefone de contato e CPF de
                             terceiro no felipe-mourao) — 「não reproduzido」
```

Regras novas permanentes (impedem reincidência):
- `validate.mjs`: **E_OFFICIAL_UNVERIFIED_PUBLIC** — `official_document`
  (mensagem ou evento) exige `source.document_id` apontando para documento com
  `public_access_verified = true`; documents.json exige o campo estruturado
  (`true|false|null`) com `public_access_date`/`public_access_basis` quando
  `true` (strings vagas como 「publicidade em verificação」 são rejeitadas).
- `scripts/audit-public-provenance.mjs`: auditoria por registro (categorias
  OK_OFFICIAL / OK_PUBLIC_INVESTIGATION / OK_SECONDARY /
  INVALID_OFFICIAL_DOCUMENT / MISSING_DOCUMENT / MISSING_PAGE /
  PUBLIC_ACCESS_UNKNOWN / SOURCE_CONFLICT) → 383/383 OK.
- `scripts/check-email-leak.mjs` + `scripts/leak-check-config.json`: proíbe
  e-mails fora de domínios institucionais públicos/exemplo e substrings
  configuradas (padrões ficam na config, não no código).
- CI (`.github/workflows/ci.yml`) agora roda as duas novas checagens.

## Participantes

```text
perfis revisados:            27 (todos)
informações pessoais removidas: 2 em notas editoriais (telefone +55 (31)
                             8328-8156 e CPF de L.F.W. — 「não reproduzido」);
                             perfis de pessoas privadas já estavam minimizados
                             (sem telefone/CPF/endereço/e-mail/placas — varredura
                             por padrões confirmou zero ocorrências)
perfil eleitoral atualizado: flavio-bolsonaro — 「pré-candidato ao Planalto em
                             2026」 → 「Senador da República e candidato à
                             Presidência da República no segundo turno das
                             Eleições 2026」, com fonte oficial do TSE em
                             profile_sources e registro em profile_verification
identidade civil não inferida: mantido 「Marcio Conjur」, 「Fábio Faria」 e
                             「Angelo Silva」 exatamente como salvos no aparelho,
                             com a ressalva documental de não-identificação
```

## Git

```text
configuração atual user.name:  Angelo
configuração atual user.email: angelo.g***…@*****.***.**.br (endereço
                               CORPORATIVO de terceiro — domínio e local part
                               mascarados para não ampliar exposição; o valor
                               integral consta apenas do git config local)
                               O e-mail pessoal dos commits do histórico
                               (angel*******@*****.***) tampouco é opção.
commit bloqueado por email pessoal/corporativo: SIM — nenhuma commit foi criada
```

**Nenhuma commit foi feita.** Todas as alterações estão no working tree
(30 arquivos modificados + 6 novos). Para commitar:
1. o usuário deve fornecer o endereço `noreply` do GitHub (não foi fornecido —
   **não inventamos**); então `git config user.name "<nome de usuário escolhido
   pelo responsável>"` e `git config user.email "<noreply informado>"`;
2. a limpeza do histórico existente (commits com e-mail pessoal) é operação
   separada e NÃO foi executada (sem filter-repo/filter-branch/BFG/force-push).

## Documentos hospedados

```text
arquivos em public/docs: 1 — pf-ipja-3298613-2026.pdf (5.537.944 bytes)
arquivos mantidos:       1 — justificativa: base do painel documental integrado
                         (PDF#page=N por mensagem); SHA-256 recalculado local-
                         mente confere com o declarado (30e24f6d…); copy_kind
                         「public_reproduction」 honesto; public_copy_url
                         (Poder360) e official_process_url (STF) registrados;
                         sem dúvida sobre redistribuição (peça pública desde
                         01/09/2026, redistribuição já ampla)
arquivos removidos:      0
motivo:                  política §22-§23 atendida — o GitHub NÃO é mirror do
                         acervo (os 25 GB do pacote Pet 16704 permanecem só na
                         origem oficial do STF; peças sem cópia hospedada usam
                         as URLs oficiais registradas em documents.json)
```

## Site / metadados

- `meta description` e `og:description` reescritas (a descrição antiga dizia
  「extraídas pela PF em 18/11/2025 e divulgadas por reportagens」 — agora
  refletem o acervo real: documentos públicos de investigações + fontes
  jornalísticas, com proveniência por mensagem; nada afirma divulgação
  oficial pela PF para todo o corpus).
- Tagline do topo: 「WhatsApp de Daniel Vorcaro — extração PF 18/11/2025」 →
  「Conversas de Daniel Vorcaro — documentos públicos e fontes jornalísticas」.
- Disclaimer de não-afiliação adicionado em três pontos visíveis (home, rodapé
  da lista de conversas, política): **「Projeto independente. Não afiliado à
  Polícia Federal, ao STF, ao WhatsApp ou à Meta.」** Nenhum título/descrição
  sugere oficialidade da PF/STF ou afiliação ao WhatsApp/Meta.
- Fontes da home agora incluem o pacote público do STF (navegação por peça +
  pacote .7z oficial), além das reportagens.

## Pendências

```text
domínio final:             RESOLVIDO ainda em 2026-10-07 — domínio oficial
                           https://zapdovorcaro.com/ aplicado em index.html
                           (og:url/canonical), robots.txt e sitemap.xml; os
                           placeholders do GitHub Pages foram removidos
licença:                   repositório sem LICENSE — recomendação registrada:
                           se adicionar licença de CÓDIGO, deixar explícito que
                           ela NÃO se aplica a mensagens de terceiros, documentos
                           oficiais, reportagens, imagens, áudios e mídias
                           externas. Nenhuma licença foi adicionada (exige
                           decisão do usuário)
git noreply:               aguardando o endereço noreply do usuário para
                           configurar user.name/user.email e criar
                           a commit das alterações
limpeza futura do histórico: operação separada (filter-repo/BFG + force push)
                           para remover o e-mail pessoal dos commits antigos —
                           fora do escopo desta tarefa por decisão expressa
canal de correções:        CORRECTIONS_CONTACT em js/config.js permanece null
                           (placeholder 「a definir」; não inventamos endereço)
INQ 5070:                  localizar peças com mídia original na pasta pública
                           Inq5070 do pacote (94 itens) quando houver demanda
```

## Verificação final executada

```text
node scripts/validate.mjs data                → 0 erros, 0 warnings (25 threads,
                                                335 mensagens, 48 eventos)
node scripts/test-validate.mjs                → 114 casos OK
node scripts/audit-public-provenance.mjs      → 383/383 OK (0 problemas)
node scripts/check-email-leak.mjs             → 0 achados
python -m scripts.import_pipeline.batch --help → OK
```

Critério §34: toda mensagem `official_document` aponta para documento com
publicidade confirmada · mensagens de documentos não comprovadamente públicos
a reclassificar: nenhuma (todas comprovadas) · documents.json coerente ·
PF-MASS-IMPORT-REPORT.md coerente · DOCUMENT-AUDIT.md coerente (§10 novo) ·
perfil de Flávio Bolsonaro atualizado · pessoas privadas minimizadas ·
public/docs revisado · commits futuros protegidos contra e-mail pessoal/corporativo
(regra CI + instrução) · testes verdes · relatório produzido.

> Regra máxima mantida: a força da afirmação do site nunca é maior que a força
> da evidência documental — agora com o CI impedindo o regresso.
