# AGENTS.md — regras de desenvolvimento do case-files-site

Instruções obrigatórias para qualquer agente (IA ou humano) que altere este repositório.
O `README.md` documenta a missão editorial e o fundamento do projeto; **este arquivo documenta
como trabalhar no repositório sem quebrar as regras**. Em caso de conflito, prevalece o
princípio editorial: *nenhuma mensagem pode ser apresentada como literal sem correspondência
verificável com a fonte publicada; nenhuma alegação pode ser apresentada como fato comprovado
sem evidência suficiente.*

---

## 0. Regras de ouro (valem para qualquer alteração em `data/`)

1. **Fonte primeiro, sempre.** Antes de criar/corrigir qualquer mensagem, buscar a reportagem
   ou peça original e conferir: texto literal, remetente, destinatário, data/hora e se é texto
   ou áudio transcrito. Se a fonte não estiver acessível, **não publique o registro**.
2. **Nada é inventado:** sem mensagens, datas, horários, remetentes, documentos ou páginas
   imaginados. Horário jamais é estimado; derivação determinística (ex.: "dois dias depois"
   de uma data divulgada) exige nota editorial explicando a derivação.
3. **Força da afirmação = força da evidência.** Proposta ≠ transferência; negociação ≠
   aquisição; plano ≠ execução; alegação de acesso ≠ acesso comprovado; suspeita ≠ condenação.
4. **Privacidade:** nunca publicar contatos privados, dados bancários pessoais, comprovantes,
   informações de crianças/familiares, endereços, credenciais, detalhes de vigilância sobre
   terceiros vulneráveis ou quebras individualizadas de dados financeiros. Resumir em evento
   editorial quando houver interesse público.
5. **Contraditório:** manifestações da defesa e dos envolvidos (e negativas das empresas)
   são registradas junto às alegações.
6. **Terceiros citados em mensagens de outros não ganham conversa própria** nem mensagens
   atribuídas por inferência (ex.: "Léo" não identificado permanece sem identificação).
7. Fala indireta/fragmentos citados pela imprensa **não** viram mensagem literal — viram
   contexto em `editorial_note` ou evento editorial.

## 1. Esquema e validação

- Fonte da verdade do esquema: `scripts/validate.mjs` (cabeçalho comenta todos os códigos de
  erro). Níveis de `verification.level`: `official_document` (exige peça pública individual,
  `public_access_verified=true` em `data/documents.json`), `public_investigation` (exige
  procedimento declarado em `verification.proceeding` ou referência documental — reportagem
  pura sem cadeia de origem declarada **não** sustenta este nível), `secondary_source`, `pending_review`.
- `content_kind` de fala literal: `verbatim`/`verbatim_excerpt`; áudio transcrito pelo veículo
  usa `verbatim_excerpt` + nota "trecho de áudio transcrito pela reportagem" (convenção atual),
  ou `audio_transcript` com `transcription`/`media` completos.
- **Colchetes:** `literal_brackets: true` significa que os colchetes **constam do original**.
  Inserção de palavra pelo veículo (`[nos]`, `[de]`, `[Nikolas]`) deve ser **removida do
  `content`** e movida para `editorial_note`. Marcador de corte (`[…]`) e supressões de
  privacidade do projeto permanecem visíveis entre colchetes, documentados em nota.
- **Ordem cronológica** (`E_TIMESTAMP_ORDER`): cada registro comparável (precisão
  `minute`/`date`) é confrontado com o **último registro comparável anterior** — mesmo que
  haja registros intermediários sem data ou com precisão `month`/`approximate`, que não
  participam da comparação mas **também não interrompem a cadeia** (uma inversão além deles
  continua detectável; fix 29/10/2026). No mesmo dia, a hora só é comparada quando ambos os
  registros a têm; horário jamais é estimado — datas parcialmente divulgadas entram com a
  precisão comprovada (`month`) ou sem data (`null` honesto).
- Escrita dos JSON: `indent=1`, UTF-8 sem escapes (`ensure_ascii=False`), LF, uma linha em
  branco no fim (replicar o formato existente para diffs limpos).

## 2. Fluxo obrigatório de qualquer alteração em `data/`

**(a) Preservação do ambiente**
```bash
git status --short && git branch --show-current && git rev-parse HEAD
git fetch origin && git log --oneline HEAD..origin/main && git diff --stat
python scripts/backup_local.py   # backup ANTES de mexer
```
Nunca executar `git reset --hard`/`git clean`; nunca sobrescrever alterações locais; nunca
push/PR/commit sem **autorização expressa** do responsável.

**(b) Edição** — preferir script reprodutível em `scripts/import_pipeline/` (nome do lote no
nome do arquivo), lendo e gravando os JSONs programaticamente. Todo registro novo precisa de:
`added_in` (rótulo do lote, ex.: `ingest-press9-20261026`), `source_ref`, `sources`,
`verification`, e `editorial_note` com data "[Corrigido AAAA-MM-DD: …]" quando for correção
de registro existente (mantendo o `added_in` original — o lote marca a inclusão, não a edição).

**(c) Efeitos colaterais que NÃO podem ficar esquecidos** *(a checagem final é sua — nada disso
é automático)*:

- [ ] **Selo "novo" (pill):** atualizar `CURRENT_BATCHES` em `scripts/build-whatsnew.mjs` com o
  rótulo `added_in` da rodada corrente e rodar o script. Sem isso os registros novos **não
  ganham o selo** na UI (o selo acende apenas para os lotes listados; a UI lê
  `current_batches` de `data/whatsnew.json`). Lembretes: o rótulo é o `added_in` integral;
  edições sem novos registros (ex.: só correções) não precisam de lote novo, mas se houver
  qualquer inclusão, a lista deve apontar para o lote mais recente. **Este passo é
  verificado automaticamente** por `scripts/test-whatsnew.mjs` (no CI): ele falha se o lote
  mais recente dos dados não estiver em `CURRENT_BATCHES` ou se `whatsnew.json` estiver
  dessincronizado — a mensagem de erro diz exatamente o que fazer.
- [ ] **`data/threads.json`**: `message_count` e `last_message_preview` das conversas alteradas
  (validador só dá *warning*, mas o índice alimenta a listagem) e entrada completa para
  conversa nova (id, título, participantes, contagem, preview, `featured`, `note`).
- [ ] **`data/participants.json`**: participante novo (mantendo a ordem existente do arquivo —
  não reordenar) e resumos afetados pelas correções, sempre com `profile_sources`.
- [ ] **`README.md`**: bloco "*Números correntes*" com data do dia e totais novos.
- [ ] **`PUBLIC-PROVENANCE-AUDIT.md`** e `data/audit/public-provenance-audit.json` são
  regenerados pelo próprio `audit-public-provenance.mjs`.

**(d) Suíte completa de verificação (tudo precisa passar):**
```bash
node scripts/build-network.mjs
node scripts/build-search-index.mjs
node scripts/build-whatsnew.mjs
node scripts/validate.mjs data          # 0 erros, 0 warnings
node scripts/test-validate.mjs          # TODOS OS CASOS PASSARAM
node scripts/test-whatsnew.mjs          # selo "novo" cobre o lote mais recente
node scripts/audit-public-provenance.mjs
node scripts/check-email-leak.mjs
```
Não há `package.json`; esses oito comandos são a suíte completa (os mesmos do CI, ver
`.github/workflows/ci.yml`). Aprovação estrutural **não** equivale a fidelidade literal —
a conferência com a fonte é sempre manual.

## 3. Armadilhas conhecidas (erros já cometidos neste projeto)

- **Pill "novo" apagada/esquecida:** esquecer de atualizar `CURRENT_BATCHES` (aconteceu em
  26/10/2026 — 120 registros inseridos sem selo até a correção). Sempre conferir a linha final
  do build: `selo 'novo' em N registros` deve bater com a contagem de registros do lote corrente.
- **Reordenar `participants.json` alfabeticamente** gera diff gigante e sem sentido — edite
  in-place respeitando a ordem histórica do arquivo.
- **Inserir mensagem datada no meio do array** pode violar `E_TIMESTAMP_ORDER` — conferir o
  **último registro comparável anterior** (precisão `minute`/`date`; não apenas o vizinho
  imediato, pois registros sem data/mês não interrompem a cadeia) antes de escolher a posição.
- **Confiança em transcrição anterior:** corrigir "só o ano" de uma mensagem errada não
  resolve se o texto também não bate com a fonte — confrontar texto, remetente, data e hora.
- **Reutilizar página de documento oficial** para sustentar mensagens publicadas pela imprensa
  que não constam daquela peça (ex.: mensagens de julho/2024 da Folha vs. peça de março/2025).
- **Identidade por homonímia/proximidade:** quando a correspondência entre o contato do
  relatório e a pessoa citada pela imprensa for plausível mas não comprovada, registrar com
  ressalva explícita (nota + perfil), nunca silenciosamente.
- **Duplicação entre veículos:** a mesma mensagem pode aparecer em duas reportagens com
  transcrições divergentes (ex.: "você" vs. "vc") — manter a transcrição da fonte citada no
  registro e não duplicar o registro.

## 4. Quando não alterar nada

Se a verificação mostrar que a pendência já está implementada, ou que a evidência é
insuficiente, **não alterar** — registrar a pendência no relatório da rodada e manter os
arquivos intactos. Relatórios de rodada ficam na raiz (ex.: `AUDIT-REPORT-2026-10-26.md`).
