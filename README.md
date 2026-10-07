# Zap do Vorcaro — Caso Banco Master

Site **100% estático** (HTML + CSS + JavaScript puro, sem frameworks, sem build,
sem npm) que reproduz a interface do WhatsApp para navegação cronológica de
diálogos de interesse público. Nesta instalação, o acervo é o caso
**Banco Master**: mensagens do celular de **Daniel Vorcaro** extraídas pela
Polícia Federal (18/11/2025) e divulgadas por documentos públicos e
reportagens jornalísticas.

> **Princípio editorial central**: a interface nunca deve fazer uma
> reconstrução editorial parecer uma mensagem literal enviada por uma pessoa.

---

## 1. Princípio editorial

O projeto organiza informações presentes em **documentos públicos e
reportagens** sobre investigações de interesse público.

A existência de uma mensagem no arquivo **não constitui**:

- acusação;
- conclusão de culpa (ou inocência);
- confirmação da interpretação apresentada por terceiros.

Texto editorial **nunca** é incorporado à fala atribuída aos participantes:
notas de contexto aparecem fora da bolha de mensagem, em bloco próprio
("Contexto editorial"), sempre citando a fonte responsável pela interpretação.
Erros de português, gírias e abreviações pertencem ao documento — nada é
corrigido, expandido ou completado.

## 2. Proveniência

Cada registro carrega um objeto `verification` com um nível, exibido na
interface como um badge discreto:

| Nível | Badge | Significado |
|---|---|---|
| `official_document` | ✓ Documento oficial | A mensagem foi localizada no documento primário público (authority, documento, página e — quando houver — figura citados). |
| `public_investigation` | ◉ Investigação pública | O material integra procedimento cujo sigilo foi levantado, mas a peça primária desta mensagem ainda não foi localizada. |
| `secondary_source` | ○ Fonte jornalística | Mensagem confirmada por reportagem; a peça pública primária ainda não foi localizada. |
| `pending_review` | ◌ Em revisão | Ainda não passou por revisão humana — **nunca é renderizada no site**. |

Os níveis **não são permanentes**. Promoções seguem sempre a ordem
`secondary_source → public_investigation → official_document` e ocorrem
**somente mediante evidência documental** localizada (página, e-Doc, URL
oficial). Nenhum validador, script ou ingest promove nível automaticamente.

Página/figura/e-Doc/horário **nunca são inferidos**: quando a fonte não
divulga, o campo fica `null`. É melhor não saber do que atribuir referência
errada. O painel "Fonte e proveniência" (botão abaixo de cada mensagem) mostra
a evidência disponível — e nunca usa linguagem que dê certeza maior que a
evidência.

## 3. Transcrição (content_kind)

Toda entrada indica a natureza do conteúdo:

| `content_kind` | Exibição | Significado |
|---|---|---|
| `verbatim` | (bolha comum) | Texto literalmente presente na mensagem. |
| `verbatim_excerpt` | tag "trecho da mensagem" | Somente parte da mensagem foi publicada — nunca fingimos ter a mensagem completa. |
| `audio_transcript` | tag "transcrição (parcial) de áudio" | Transcrição de áudio; `transcription_complete` informa se é integral. Colchetes de completição são inerentes ao gênero. |
| `media` | card de mídia | Imagem/vídeo/documento; quando o arquivo não foi divulgado, o card descreve o que a fonte registrou. |
| `call` | card de chamada | Registro de chamada (perdida/atendida, duração quando divulgada). |
| `forwarded_message` | tag "mensagem encaminhada" | Mensagem encaminhada com atribuição a terceiro (`forwarded_attribution`); **contato direto do terceiro com Vorcaro não é verificado** — atribuição nunca vira remetente. |
| `editorial_event` | card neutro "evento editorial" | Afirmação editorial/reportagem sobre a conversa — **nunca** renderizada como bolha, sem avatar, check ou lado. Vive em `timeline_events`. |
| `system` | card neutro | Linha de sistema da extração (também em `timeline_events`). |

## 4. Horários

**Horários nunca são estimados.** Cada registro declara:

```jsonc
{ "date": "2025-09-01", "time": null,    "timestamp_precision": "date" }    // só a data é conhecida
{ "date": "2025-09-01", "time": "17:02", "timestamp_precision": "minute" } // hora divulgada
{ "date": "2025-09",    "time": null,    "timestamp_precision": "month" }   // só o mês
```

Quando a fonte informa apenas a data, o site exibe **"horário não divulgado"**
— nunca `12:00` ou qualquer aproximação. A ordem de exibição dentro de um
mesmo dia não é afirmada quando a fonte não permite determiná-la (registros
sem hora mantêm a ordem da fonte; a chave de ordenação interna nunca aparece
na UI como fato documental). O validador rejeita `precision: "date"` com hora
preenchida e `precision: "minute"` sem hora.

## 5. Notas editoriais

`editorial_note` contextualiza a mensagem **fora da bolha** (bloco "Contexto
editorial", itálico, borda teal), sempre atribuindo a interpretação à fonte
responsável. Exemplo real do acervo:

> **Mensagem (trecho):** "semana passada foi muito dificil pra mim"
> **Contexto editorial:** Segundo a reportagem, a mensagem foi enviada em tom
> de pedido de desculpas.

## 6. Fontes do acervo atual

| Fonte | Tipo | Data | Conversas |
|---|---|---|---|
| PF · IPJ-A nº 3298613/2026 (PET 16662/STF), revelado pelo [R7/Rádio Guaíba](https://guaiba.com.br/politica/mendonca-tira-sigilo-e-pf-revela-pedidos-de-vorcaro-a-moraes) | documento oficial (via reportagem) | 01/09/2026 | Alexandre de Moraes ↔ Vorcaro |
| [piauí — "As 96 mensagens entre Flávio e Vorcaro"](https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/) (Ana Clara Costa, João Batista Jr., Breno Pires) | reportagem (extração INQ 5070/STF) | 01/10/2026 | Flávio Bolsonaro · Thiago Miranda · Mário Frias · Flávio Carneiro ↔ Vorcaro |
| [Terra / Poder360 — cobranças de Roberto Justus por aporte](https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html) | reportagem | 02/10/2026 | Roberto Justus ↔ Vorcaro |
| [Correio Braziliense / O Globo — "…maiores opositores"](https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html) (Pedro José Borges) | reportagem | 03/10/2026 | Vanessa Souza ↔ Vorcaro |

Fontes monitoradas para localização de peças primárias: `scripts/sources.yaml`
(diferencia `documento_oficial`, `processo_publico` e `reportagem`). Quando um
documento primário é localizado, a reportagem que permitiu achá-lo **permanece**
em `sources.secondary` — nunca substituída.

## 7. Correções e contestação

Ver a página **Política de correções e fontes** no site (rota `#/policy`). Em
resumo: erros de transcrição podem ser corrigidos (sempre conferidos contra a
fonte); pessoas citadas podem indicar erro factual ou fonte contraditória;
toda correção fica registrada no histórico do Git; prevalece o documento
primário quando disponível. O canal de contato é configurável em
`js/config.js` (`CORRECTIONS_CONTACT`, hoje um placeholder).

## 8. Executando localmente

Os dados em `/data` são carregados via `fetch()`, que **não funciona** abrindo
`index.html` direto (`file://`). Use o servidor de desenvolvimento incluído:

```bash
cd case-files-site
python scripts/dev-server.py 8080
# abra http://localhost:8080
```

| Rota | O que faz |
|---|---|
| `#/` | Home com aviso editorial, destaques e legenda de proveniência |
| `#/policy` | Política de correções e fontes |
| `#/thread/flavio-bolsonaro-daniel-vorcaro` | Conversa (abre no fim, como no WhatsApp) |
| `#/thread/…/m-00024` | Deep-link: abre na mensagem destacada |
| `#/search/mermão` | Busca global (agrupada por thread, trechos em `<mark>`) |

### Testes locais (Node puro, sem dependências)

```bash
node scripts/validate.mjs data      # valida todos os JSONs (exit 1 = CI vermelho)
node scripts/test-validate.mjs      # testa CADA regra de rejeição do validador
```

### Fixture de estresse (65 mil mensagens)

```bash
node scripts/generate-fixture.mjs              # gera data/threads/fixture-stress.json
node scripts/generate-fixture.mjs --remove     # remove e limpa o índice
```

A fixture é **gitignored** (teste local). Busca < 200 ms e scroll fluido
(chunks de 100 mensagens via `IntersectionObserver`).

## 9. Deploy no GitHub Pages

1. Suba o repositório; **Settings → Pages → Source: GitHub Actions**.
2. O workflow `.github/workflows/ci.yml`:
   - **job `validate`**: `validate.mjs` + `test-validate.mjs` em todo push/PR;
   - **job `deploy`**: no merge na `main`, publica a raiz do repo (sem build).

Tipografia ampliada (~20%) para leitura confortável em baixa visão.

Placeholders a substituir antes de domínio público: `js/config.js`
(`CORRECTIONS_CONTACT`). Domínio oficial já aplicado em `index.html`
(og:url/canonical), `sitemap.xml` e `robots.txt`: **https://zapdovorcaro.com/**.

## 10. Estrutura

```
case-files-site/
├── index.html               # única página (SPA por hash routing)
├── css/                     # reset · theme · layout · components
├── js/
│   ├── main.js              # bootstrap, topbar, drawer, warmup do índice
│   ├── router.js            # #/ · #/policy · #/thread/… · #/search/…
│   ├── api.js               # fetch + cache + filtro pending_review
│   ├── search.js            # índice invertido + busca + <mark>
│   ├── utils.js             # escapeHtml, datas pt-BR, sortKey, clipboard…
│   ├── state.js             # estado de UI em memória
│   ├── config.js            # constantes editoriais + canal de correção
│   └── render/              # chatList · chatWindow · message · profile · home · policy
├── data/
│   ├── participants.json    # participantes (+ profile_verification opcional)
│   ├── documents.json       # registro central de documentos (hash, cópia pública, processo)
│   ├── threads.json         # índice leve para a ChatList
│   ├── audit/document-audit.json  # auditoria documental legível por máquina
│   └── threads/{id}.json    # mensagens + timeline_events por conversa
├── DOCUMENT-AUDIT.md        # relatório da auditoria documental
├── migration-report.json    # relatório da migração de proveniência
├── public/media/            # mídias referenciadas (vazio: nada divulgado)
└── scripts/
    ├── ingest.py            # parser → JSON (nunca promove nível/página)
    ├── validate.mjs         # validador (regras da seção 12)
    ├── test-validate.mjs    # testa cada regra de rejeição
    ├── migrate-provenance.mjs # migração de schema + auditoria
    ├── generate-fixture.mjs # fixture sintética
    ├── dev-server.py        # servidor local (Cache-Control: no-cache)
    └── sources.yaml         # fontes monitoradas (documento_oficial/processo_publico/reportagem)
```

## 11. Registro de documentos e mídia

`data/documents.json` centraliza os documentos (§24): processo oficial
(`official_process_url`), cópia pública (`public_copy_url` + `copy_kind:
public_reproduction` — **nunca** `official_pdf_url` para arquivo hospedado por
veículo), SHA-256 **calculado localmente** e tamanho. Mensagens referenciam por
`source.document_id` + `page`/`figure`; o painel de evidência resolve links
diretos (`PDF#page=N` e "abrir processo no STF").

Mídia carrega cadeia de proveniência própria (§28), **independente da
proveniência do texto** (transcrição oficial + áudio de veículo é combinação
válida):

| `media.status` | Uso |
|---|---|
| `official_media` | Arquivo dos autos/pacote oficial — exige arquivo local + SHA-256 + fonte oficial; **jamais** com `publisher` (URL jornalística não gera oficial) |
| `secondary_media` | Publicado por veículo (player/link externo) — exige `publisher`; **não re-hospedado** (§8) |
| `embedded_media` | Player incorporado à origem |
| `transcript_only` | Existe apenas a transcrição — jamais aponta arquivo |
| `media_reference_only` | O documento registra a mídia (figura/página); arquivo não obtido |

Transcrições declaram autoria (`transcription.kind`: `document_transcription` /
`publisher_transcription` / `project_transcription`, com `complete`) e nunca são
apagadas pela presença/ausência de áudio (§37). `original_file: true` exige
`source_document_id`. Mídia local exige SHA-256 + bytes; derivada exige
`derived_from` (originais em `original/`, conversões em `derived/`).

## 12. Schema de dados

`data/threads/{id}.json`:

```jsonc
{
  "id": "flavio-bolsonaro-daniel-vorcaro",      // = nome do arquivo
  "title": "…",
  "participants_ids": ["daniel-vorcaro", "…"],  // o 1º é o dono (bolha verde, direita)
  "source": { "document": "…", "url": "…", "pages": "…" },
  "messages": [{
    "id": "m-00014",                     // m-NNNNN
    "date": "2024-03-12",                // YYYY-MM-DD (ou YYYY-MM se precision=month)
    "time": "14:02",                     // HH:MM ou null — NUNCA estimado
    "timestamp_precision": "minute",     // minute | date | month | approximate
    "sender_id": "ana-cardoso",
    "content_kind": "verbatim",          // §3 acima
    "content": "transcrição fiel",
    "editorial_note": null,              // contexto FORA da bolha
    "transcription_complete": false,     // exigido em audio_transcript
    "literal_brackets": true,            // só quando os colchetes são do original
    "media": { "kind": "image", "url": "/public/media/…", "filename": "…" },
    "call_info": { "direction": "out", "duration_sec": 158 },
    "verification": {
      "level": "official_document",      // §2 acima
      "origin": "PF extraction",
      "authority": "Polícia Federal", "court": "STF", "case": "PET 16662",
      "document": "IPJ-A nº 3298613/2026", "page": 143, "figure": 142,
      "official_url": null,
      "primary_document_located": true,  // true SÓ em official_document
      "verified_at": "2026-10-06"
    },
    "sources": {
      "primary": { /* espelha o documento localizado */ },
      "secondary": [ { "publication": "R7", "date": "2026-09-01", "url": "…" } ]
    },
    "source_ref": "PF · IPJ-A nº 3298613/2026 · fl. 143",  // citação legível
    "added_in": "a1b2c3d"
  }],
  "timeline_events": [{
    "id": "e-00001",                     // e-NNNNN — SEM sender_id
    "date": "2025-11-17", "time": null, "timestamp_precision": "date",
    "content": "A reportagem registra que…",
    "event_kind": "editorial_context",   // editorial_context | system
    "verification": { /* … */ }, "source_ref": "…", "added_in": "…"
  }]
}
```

## 13. O que o validador rejeita (CI vermelho)

JSON inválido; campos legados (`timestamp`, `status`, `type` — regressão ao
schema antigo); mensagem sem `sender_id` (ou evento **com** `sender_id`);
`content_kind`/`verification.level`/`timestamp_precision` fora das listas;
`precision: date` **com** hora inventada; `precision: minute` sem hora;
ordem cronológica violada quando determinável; `official_document` sem
`authority` + `document` + `page` (+ `sources.primary`); `secondary_source`
sem fonte em `sources.secondary`; **`[colchetes]` editoriais em `verbatim`/
`verbatim_excerpt`/`forwarded_message`** sem `literal_brackets: true`;
`forwarded_message` sem `forwarded_attribution` com `verified_direct_contact:
false`; `audio_transcript` sem `transcription_complete` **ou** sem registro de
mídia; mídia sem `status`; `official_media` sem arquivo+SHA-256+fonte oficial ou
com `publisher`; `secondary_media` sem `publisher`; `transcript_only` apontando
arquivo ou sem transcrição; mídia local sem SHA-256/bytes; derivada sem
`derived_from`; `original_file: true` sem `source_document_id`;
`source.document_id` inexistente; `documents.json` com `official_pdf_url` ou
cópia pública sem processo oficial; `reply_to`/`media.url` inválidos; índice
dessincronizado; ids duplicados/inválidos; mensagem sem `source_ref`/`added_in`.

**Imutabilidade**: mensagem nunca é editada em silêncio — correção = novo
commit, rastreável no Git (`added_in` marca o commit de inserção).

## 14. Pipeline de ingestão

1. **DETECÇÃO** — fontes em `scripts/sources.yaml`.
2. **EXTRAÇÃO** — `scripts/ingest.py` converte exportações/PDF para o schema:
   tudo sai `pending_review`, `page: null` (a página do PDF de origem da linha
   fica em `extraction.pdf_page`, metadado interno); remetente desconhecido
   **aborta**; linhas de sistema viram `timeline_events`.
3. **REVISÃO** — humano confere contra o documento, promove o nível e preenche
   página/figura **só quando localizados de fato**.
4. **VERSIONAMENTO** — lote = commit; índice atualizado.
5. **CI** — validador + testes; Pages publica no merge.

### 14.1 Importação em massa (`scripts/import_pipeline/`)

Para o acervo grande de PDFs PF/STF em `pdf_pf/` (incremental — novos
arquivos entram nos próximos lotes sozinhos):

```bash
python -m scripts.import_pipeline.batch --docs 30   # retomada exata
```

- **Inventário** (hash SHA-256, páginas, identificação da peça, publicidade)
  → `data/audit/pf-inventory.json` — **gitignored, nunca publicado**: o índice bruto
  expõe identificação de peças de pessoas/empresas fora da curadoria do site
  (decisão 2026-10-07); estado do pipeline em `.pipeline/import.db` (SQLite,
  gitignored) e `data/audit/import-state.json` (idem — interno, nunca publicado).
- **Extração**: texto por página com cache (`data/cache/`); citações literais
  entre aspas na narrativa policial com pista de remetente/data/hora/figura;
  eventos com timestamp; referências de mídia (prints/áudios).
- **Candidatos** em `data/review/` (gitignored — **nunca** no build público).
  Peça sem publicidade verificada não publica conteúdo, ponto (missão §24).
- **Promoção**: revisor marca `"approved": true` + `"target"` no candidato e
  roda `python -m scripts.import_pipeline.importer` — o registro entra na
  thread como `pending_review` (invisível na renderização pública) até
  verificação humana promover o nível.
- Relatórios: `BATCH-NNNN.md` por lote + `PF-MASS-IMPORT-REPORT.md`
  consolidado. Deps: `python -m pip install pdfplumber pypdf`.

## 15. Regras editoriais (hard rules)

- Proibido parafrasear, resumir, "corrigir" português, expandir abreviações,
  completar frases ou fundir/separar mensagens sem evidência documental.
- Descrição jornalística nunca vira citação: paráfrase fica em
  `editorial_note` (ou `timeline_events`), com a fonte citada.
- Proibido material que não seja de fonte pública/oficial.
- Nomes de pessoas privadas só se constarem dos documentos públicos.
- Todo dado em `/data` rastreia até uma entrada de `sources.yaml`.
- Nenhuma fonte, página, horário, e-Doc ou documento é inventado — na dúvida,
  `null` + nível compatível com a evidência.
- Transcrição não é áudio: possuir transcrição nunca autoriza afirmar que se
  possui o arquivo original; player jornalístico nunca é "arquivo oficial da PF".
- Mídia jornalística não é baixada/re-hospedada sem verificação de regime —
  link para a origem; sem yt-dlp/scraping/paywall-bypass.
- Reprodução jornalística de documento oficial é `public_reproduction`, sempre
  acompanhada do processo oficial que comprova a origem.
- Atribuição de terceiro em mensagem encaminhada jamais vira contato direto.
- Privacidade: sem threads de familiares/motoristas/funcionários com conteúdo
  pessoal; sem placas, endereços residenciais, telefones, CPF ou dados íntimos.

## 16. Fora de escopo

Login/contas, comentários, envio de mensagens, backend, APIs dinâmicas, banco
de dados, download em massa do corpus.

## 17. Notas de performance e compatibilidade

Busca com índice invertido pós-first-paint (multi-termo AND, normalizada);
scroll em chunks de 100; deep-link com destaque; todo conteúdo do JSON passa
por `escapeHtml()`; últimos 2 anos de Chrome/Firefox/Safari/Edge; sem
recursos externos (fontes/ícones inline).
