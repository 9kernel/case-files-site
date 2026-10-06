# Arquivo Público de Diálogos — Caso Banco Master

Site **100% estático** (HTML + CSS + JavaScript puro, sem frameworks, sem build,
sem npm) que reproduz a interface do WhatsApp para navegação cronológica de
diálogos de interesse público. Nesta instalação, o acervo é o caso
**Banco Master**: mensagens do celular de **Daniel Vorcaro** extraídas pela
Polícia Federal (18/11/2025) e divulgadas por reportagens jornalísticas.

> **Aviso editorial**: o site reproduz **o que as reportagens publicaram**, com a
> fonte citada em cada mensagem — não temos acesso aos autos originais. O conteúdo
> não constitui conclusão de culpa ou inocência; as investigações seguem em curso.
> Mensagens `pending-review` nunca são renderizadas.

---

## 1. Acervo atual: caso Banco Master

### Fontes usadas (cada mensagem aponta a sua)

| Fonte | Data | Conversas no site |
|---|---|---|
| [piauí — "As 96 mensagens entre Flávio e Vorcaro, 90 dias antes da prisão"](https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/) (Ana Clara Costa, João Batista Jr., Breno Pires) | 01/10/2026 | Flávio Bolsonaro ↔ Vorcaro · Thiago Miranda ↔ Vorcaro · Mário Frias ↔ Vorcaro · Flávio Carneiro ↔ Vorcaro |
| [Terra / Poder360 — cobranças de Roberto Justus por aporte](https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html) | 02/10/2026 | Roberto Justus ↔ Vorcaro |
| [Correio Braziliense / O Globo — "Vorcaro disse que Haddad era um de seus 'maiores opositores'"](https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html) (Pedro José Borges) | 03/10/2026 | Vanessa Souza ↔ Vorcaro |
| [Rádio Guaíba / R7 — relatório da PF desclassificado pelo STF ("Mendonça tira sigilo")](https://guaiba.com.br/politica/mendonca-tira-sigilo-e-pf-revela-pedidos-de-vorcaro-a-moraes) | 01/09/2026 | Alexandre de Moraes ↔ Vorcaro |

**Documentos judiciais no acervo**: a conversa com Alexandre de Moraes vem de
**relatório da PF desclassificado pelo ministro André Mendonça (01/09/2026)** —
documento judicial tornado público e revelado pelo R7. Contexto judicial
monitorado em `sources.yaml`: delação de doleiro homologada por Mendonça
(set/2026, conforme Agência Brasil), inclusão de Flávio Bolsonaro como
investigado no inquérito do filme "Dark Horse" (set/2026) e decisões do STF
(portal.stf.jus.br) — quando inteiros teores públicos com mensagens forem
localizados, entram com `source_ref` de documento judicial.

### Convenções de transcrição

- **Transcrição literal** do que a reportagem publicou, entre aspas na origem.
- **[Colchetes]** = palavras nossas, apenas conectivo editorial (ex.: "[Pedindo
  desculpas:] semana passada foi muito dificil pra mim").
- **"…"** = corte na citação, conforme a reportagem.
- **Horários**: quando a reportagem indica (ex.: 17h22, 15h46), usamos o horário
  real; quando não indica, usamos **12:00** como aproximação — o campo `pages`
  de cada thread avisa isso, e o diálogo de fonte repete.
- **Mídia de visualização única / arquivos não divulgados**: a mensagem existe
  (com `type` correto) e o nome do arquivo descreve o que a reportagem registrou,
  sem inventar conteúdo.
- O campo `source_ref` de cada mensagem segue o padrão
  `veículo, data` (ex.: `piauí, 01/10/2026`) — é o que vai na citação copiável.

### Cuidados jurídicos (importantes)

- Publicar mensagens de pessoas reais envolve direito de resposta, direito de
  imagem e risco de decisões judiciais — **inclusive há precedente de site com
  essas mesmas mensagens derrubado por ordem judicial**, conforme a imprensa.
  Antes de publicar um domínio público, faça revisão jurídica e mantenha o aviso
  editorial visível.
- Só publique mensagem que exista **textualmente** em fonte verificável e
  identificável; quando a reportagem paraphrase, use conectivo entre [colchetes]
  ou não publique.
---

## 1. Executando localmente

Os dados em `/data` são carregados via `fetch()`, que **não funciona abrindo
`index.html` direto (`file://`)** — o navegador bloqueia por CORS. Use o
servidor de desenvolvimento incluído, que envia `Cache-Control: no-cache`
(evita o navegador servir JS/CSS antigos durante o desenvolvimento):

```bash
cd case-files-site
python scripts/dev-server.py 8080
# abra http://localhost:8080
```

(`python -m http.server 8080` também funciona, mas pode servir arquivos
estáticos de cache durante as edições.)

Todas as rotas são por hash e funcionam direto, sem fallback de 404:

| Rota | O que faz |
|---|---|
| `#/` | Home com aviso editorial, destaques e fontes |
| `#/thread/flavio-bolsonaro-daniel-vorcaro` | Conversa (abre no fim, como no WhatsApp) |
| `#/thread/flavio-bolsonaro-daniel-vorcaro/m-00024` | **Deep-link**: abre na mensagem destacada |
| `#/thread/alexandre-moraes-daniel-vorcaro` | Conversa com o ministro (relatório da PF desclassificado) |
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

### Placeholders a substituir antes de publicar num domínio público

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
│   └── render/              # chatList · chatWindow · message · profile · searchView · home
├── data/
│   ├── participants.json    # participantes (id, nome, aliases, contexto)
│   ├── threads.json         # ÍNDICE leve para a ChatList (ver adiante)
│   └── threads/{{id}}.json  # uma conversa por arquivo
├── public/media/            # mídias dos autos referenciadas nos JSONs (vazio: o caso ainda não tem mídia publicada)
├── scripts/
│   ├── ingest.py            # parser PDF → JSON (ferramenta do agente; demo sem deps)
│   ├── validate.mjs         # validador (Node puro) — regras da seção 4
│   ├── test-validate.mjs    # testa cada regra de rejeição
│   ├── generate-fixture.mjs # fixture sintética de 65 mil mensagens
│   ├── dev-server.py        # servidor local com Cache-Control: no-cache
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
  "id": "flavio-bolsonaro-daniel-vorcaro",   // = nome do arquivo
  "title": "…",
  "participants_ids": ["daniel-vorcaro", "flavio-bolsonaro"],  // o 1º é o dono (bolha verde, direita)
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
  `<video controls playsinline>` (controles com volume = som). O caso publicado
  até aqui não tem mídia divulgada (imagens/vídeos eram de "visualização única");
  quando uma reportagem publicar mídia, basta colocar o arquivo em
  `/public/media` e preencher `media.url` no JSON — o validador confere a existência.
- **Emojis**: as fontes de emoji do sistema (Apple Color Emoji / Segoe UI Emoji /
  Noto Color Emoji) fazem parte da pilha tipográfica; emojis nas transcrições
  são renderizados como texto comum (não são tokens de busca).
- **Card de perfil do contato**: clicar no avatar (na lista lateral ou no
  cabeçalho da conversa) abre um card com nome, cargo, contexto público e as
  **fontes linkadas** de onde cada informação foi retirada
  (`profile_sources` em `data/participants.json` — campo opcional; cada
  fato do resumo deve rastrear até uma das fontes listadas).
- **Interface**: fundo de conversa com padrão de "doodles" sutil, duplo check
  azul nas bolhas do dono, prévia da última mensagem na lista lateral,
  ícones de chamada/vídeo no header (desabilitados — o arquivo é somente
  leitura) e barra de entrada decorativa "Arquivo somente leitura" — envio de
  mensagens segue fora de escopo por decisão editorial (seção 7).
