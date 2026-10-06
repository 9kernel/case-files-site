# Arquivo Público de Diálogos — Caso Aurora (scaffold)

Site **100% estático** (HTML + CSS + JavaScript puro, sem frameworks, sem build,
sem npm) que reproduz a interface do WhatsApp para navegação cronológica dos
diálogos divulgados publicamente nos autos de um caso. Nesta instalação de
demonstração, o caso e todas as conversas são **fictícios** ("Caso Aurora",
IP 2024/0123) — substitua pelos dados reais seguindo as regras editoriais.

> **Aviso editorial**: o site só publica material de fonte pública/oficial,
> sempre com `source_ref` (documento + folha) em cada mensagem. Mensagens
> `pending-review` nunca são renderizadas.

---

## 1. Executando localmente

Os dados em `/data` são carregados via `fetch()`, que **não funciona abrindo
`index.html` direto (`file://`)** — o navegador bloqueia por CORS. Use um
servidor local:

```bash
cd case-files-site
python -m http.server 8080
# abra http://localhost:8080
```

Todas as rotas são por hash e funcionam direto, sem fallback de 404:

| Rota | O que faz |
|---|---|
| `#/` | Home com aviso editorial e destaques |
| `#/thread/grupo-comite-executivo` | Conversa (abre no fim, como no WhatsApp) |
| `#/thread/grupo-comite-executivo/m-00014` | **Deep-link**: abre na mensagem destacada |
| `#/search/pauta` | Busca global (agrupada por thread, trechos em `<mark>`) |

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

A fixture é **gitignored** (só para teste local). Com ela carregada, a view de
busca exibe o tempo de resposta — referência exigida: **< 200 ms**. O scroll da
thread longa fica fluido porque o `chatWindow.js` renderiza em chunks de 100
mensagens via `IntersectionObserver` (nas duas pontas).

---

## 2. Deploy no GitHub Pages

1. Suba o repositório (`git init && git add -A && git commit && git remote add origin …`).
2. **Settings → Pages → Source: GitHub Actions**.
3. O workflow `.github/workflows/ci.yml` faz o resto:
   - **job `validate`**: roda `validate.mjs` e `test-validate.mjs` em todo push/PR;
   - **job `deploy`**: no merge na `main`, publica a **raiz do repo** via
     `actions/upload-pages-artifact` + `actions/deploy-pages` — **sem build**:
     o que está no repo é o que vai ao ar.

### Placeholders a substituir antes de publicar um caso real

- `js/config.js` — `CASE_NAME`, `PROCESS_LABEL`, `LAST_UPDATED`, `SOURCE_URL`, `REPO_URL`;
- `index.html` — `<title>`, `og:url`, `og:description`;
- `sitemap.xml` e `robots.txt` — domínio final;
- `data/` — participantes, threads e mídias reais.

---

## 3. Estrutura

```
case-files-site/
├── index.html               # única página (SPA por hash routing)
├── 404.html                 # erro estático do GitHub Pages
├── css/                     # reset · theme (custom properties) · layout · components
├── js/
│   ├── main.js              # bootstrap, topbar, drawer, warmup do índice
│   ├── router.js            # parse do hash + dispatch das views
│   ├── api.js               # fetch + cache (Map) + filtro pending-review
│   ├── search.js            # índice invertido + busca + <mark>
│   ├── utils.js             # escapeHtml, datas pt-BR, clipboard, toast…
│   ├── state.js             # estado de UI em memória
│   ├── config.js            # constantes editoriais (nome do caso, datas)
│   └── render/              # chatList · chatWindow · message · searchView · home
├── data/
│   ├── participants.json    # participantes (id, nome, aliases, contexto)
│   ├── threads.json         # ÍNDICE leve para a ChatList (ver adiante)
│   └── threads/{{id}}.json  # uma conversa por arquivo
├── public/media/            # mídias dos autos referenciadas nos JSONs
├── scripts/
│   ├── ingest.py            # parser PDF → JSON (ferramenta do agente; demo sem deps)
│   ├── validate.mjs         # validador (Node puro) — regras da seção 4
│   ├── test-validate.mjs    # testa cada regra de rejeição
│   ├── generate-fixture.mjs # fixture sintética de 65 mil mensagens
│   ├── make-demo-media.py   # gera WAV/PDF de demonstração (stdlib)
│   └── sources.yaml         # fontes monitoradas pelo agente
└── .github/workflows/ci.yml # job 1: validação · job 2: deploy Pages
```

### Desvios conscientes da especificação (e por quê)

- **`data/threads.json`** — índice leve (título, contagem, última data). Sem ele,
  a ChatList teria que baixar todas as threads (com a fixture de 65 mil msgs isso
  inviabiliza a primeira renderização). O `validate.mjs` cruza índice × arquivos
  (`E_INDEX_MISMATCH`) e avisa se a contagem dessincronizar.
- **`js/config.js`** — concentra os placeholders `{{...}}` do caso em um lugar só.
- **`call_info`** (opcional nas mensagens de chamada) — `{direction: in|out|missed,
  duration_sec}`. O `content` continua sendo a transcrição literal da linha do
  documento ("Chamada de voz perdida"); `call_info` é apenas dica de renderização
  (seta/cor). O validador ignora campos extras.
- **`scripts/test-validate.mjs`** e **`generate-fixture.mjs`** — exigidos pelos
  critérios de aceite (testar cada regra; fixture de 65 mil).

---

## 4. Schema de dados

`data/participants.json` — array de `{id, name, role, aliases, summary}`.

`data/threads/{{id}}.json`:

```jsonc
{
  "id": "grupo-comite-executivo",        // = nome do arquivo
  "title": "…",
  "participants_ids": ["ana-cardoso"],   // o 1º é o dono da conversa (bolha verde, direita)
  "source": { "document": "IP 2024/0123", "url": "https://…", "pages": "fl. 120–133" },
  "messages": [{
    "id": "m-00014",                     // sequencial na thread (m-NNNNN)
    "timestamp": "2024-03-12T14:02:00-03:00",  // ISO 8601 COM offset
    "sender_id": "ana-cardoso",
    "type": "text|image|audio|video|document|call|system",
    "content": "transcrição fiel (pode ser vazia em mídia)",
    "media": { "url": "/public/media/…", "filename": "…", "duration_sec": 3 },
    "reply_to": "m-00010",
    "source_ref": "IP 2024/0123 · fl. 125",  // OBRIGATÓRIO em TODA mensagem
    "status": "confirmed | pending-review",  // OBRIGATÓRIO
    "added_in": "a1b2c3d"                    // hash curto do commit que inseriu
  }]
}
```

O `validate.mjs` rejeita (CI vermelho): JSON inválido; mensagem sem `source_ref`,
`status`, `sender_id`, `added_in` ou `id` válido; `sender_id` inexistente em
participants.json; timestamps fora de ordem ou fora do ISO 8601 com offset; ids
duplicados; `type` fora da lista; `reply_to` inexistente; `media.url` sem arquivo;
thread sem `title`/`participants_ids`/`source`; índice dessincronizado.

**Regra de imutabilidade**: mensagem nunca é editada — correção = novo commit no
JSON, com o `added_in` do commit novo.

---

## 5. Pipeline de ingestão (agente catalogador)

1. **DETECÇÃO** — o agente monitora as fontes listadas em `scripts/sources.yaml`
   (URLs oficiais dos PDFs/decisões). Mantenha o arquivo atualizado.
2. **EXTRAÇÃO** — `scripts/ingest.py` converte trechos de conversa para o schema,
   preenchendo `source_ref` com documento + folha. Sem PDF, use `--demo`:

   ```bash
   python scripts/ingest.py --demo --thread-id demo-nova --title "Demo" \
       --document-name "IP 2024/0123" --pages 140-145 --source-url https://example.org/x.pdf
   ```

   Com PDF real: `pip install pdfplumber` e `python scripts/ingest.py --pdf autos.pdf …`.
   Remetentes são resolvidos via participants.json; nome desconhecido **aborta**
   (não inventamos participantes).
3. **REVISÃO** — a saída entra com status `pending-review` (e `added_in: "pending"`).
   O revisor confere o diff do PR contra o PDF original, muda para `confirmed` e
   troca `added_in` pelo hash curto do commit — **no mesmo PR**.
4. **VERSIONAMENTO** — cada lote = 1 commit `ingest: {{fonte}} · {{n}} msgs`.
   Se a conversa for nova, atualize também `data/threads.json`.
5. **CI** — `validate.mjs` + `test-validate.mjs` rodam no PR; no merge na `main`
   o Pages publica automaticamente (sem build).

---

## 6. Regras editoriais (hard rules)

- Proibido parafrasear, resumir ou "corrigir" os diálogos: **só transcrição fiel**,
  com `source_ref`.
- Proibido incluir material que não seja de fonte pública/oficial.
- Nomes de pessoas privadas só se constarem nos documentos públicos.
- Todo dado em `/data` rastreável até um documento citado (e uma entrada em
  `sources.yaml`).

## 7. Fora de escopo

Login/contas, comentários, envio de mensagens (qualquer escrita), backend,
APIs dinâmicas, banco de dados e download em massa do corpus.

## 8. Notas de performance e compatibilidade

- **Busca**: índice invertido (`Map` token → mensagens) construído após o primeiro
  paint (`requestIdleCallback`); query e conteúdo normalizados (sem acento/caixa).
  Multi-termo = AND. Com a fixture de 65 mil, o tempo exibido na view de busca
  serve de verificação do critério (< 200 ms).
- **Scroll**: chunks de 100 mensagens; sentinels no topo e no rodapé com
  `IntersectionObserver` (preserva a posição do scroll ao adicionar acima).
- **Deep-link**: abre o chunk que contém a mensagem, centra com
  `scrollIntoView` e aplica destaque temporário.
- **Segurança**: todo conteúdo do JSON passa por `escapeHtml()` antes de
  `innerHTML`.
- **Compatibilidade**: últimos 2 anos de Chrome/Firefox/Safari/Edge (desktop e
  mobile). Layout responsivo com drawer abaixo de 768px. Tipografia e ícones
  não usam recursos externos.

## 9. Fidelidade visual e mídia (estilo WhatsApp)

- **Visualizador de imagens (lightbox)**: clique na imagem da bolha abre o
  diálogo de mídia com a foto ampliada, legenda, `source_ref` da mensagem e
  link para o arquivo; clique na imagem alterna o zoom (1,75×); `Esc`, botão ✕
  ou clique fora fecham.
- **Vídeos com áudio**: mensagens do tipo `video` com `media.url` renderizam
  `<video controls playsinline>` (controles com volume = som). Os MP4 de
  demonstração são sintéticos (H.264 + AAC) e podem ser regenerados com
  `python scripts/make-demo-media.py` (requer `pip install imageio-ffmpeg`,
  que traz um binário ffmpeg estático — não altera o PATH).
- **Emojis**: as fontes de emoji do sistema (Apple Color Emoji / Segoe UI Emoji /
  Noto Color Emoji) fazem parte da pilha tipográfica; as transcrições demo
  incluem emojis, que são renderizados como texto comum (não são tokens de
  busca).
- **Interface**: fundo de conversa com padrão de "doodles" sutil, duplo check
  azul nas bolhas do dono, prévia da última mensagem na lista lateral,
  ícones de chamada/vídeo no header (desabilitados — o arquivo é somente
  leitura) e barra de entrada decorativa "Arquivo somente leitura" — envio de
  mensagens segue fora de escopo por decisão editorial (seção 7).
