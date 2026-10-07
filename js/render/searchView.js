// searchView.js — rota #/search/{{q}}: resultados globais agrupados por thread.

import { getThreadIndex } from '../api.js';
import { search, snippetHtml, groupByThread } from '../search.js';
import { escapeHtml as esc, dateTimeLabel } from '../utils.js';

const PER_GROUP = 15;

export async function renderSearchView(container, query) {
  container.innerHTML = `
  <div class="search-page">
    <div class="search-head">
      <h2>Busca global</h2>
      <p class="search-status" id="search-status">Preparando índice…</p>
    </div>
    <div id="search-results"></div>
  </div>`;

  const statusEl = container.querySelector('#search-status');
  const resultsEl = container.querySelector('#search-results');
  const q = String(query || '').trim();

  if (!q) {
    statusEl.textContent = 'Digite um termo no campo de busca acima.';
    return;
  }

  const t0 = performance.now();
  const { terms, hits, truncated } = await search(q);
  const elapsed = Math.max(1, Math.round(performance.now() - t0));

  statusEl.textContent = hits.length
    ? `${hits.length} resultado${hits.length === 1 ? '' : 's'} para “${esc(q)}” em ${elapsed} ms${truncated ? ' (exibindo os primeiros)' : ''}`
    : `Nenhum resultado para “${esc(q)}” (${elapsed} ms)`;

  if (!hits.length) {
    resultsEl.innerHTML = `<div class="empty-state"><h3>Nada encontrado</h3>
      <p>A busca ignora acentos e maiúsculas/minúsculas. Termos múltiplos exigem
      que todos apareçam na mesma mensagem.</p></div>`;
    return;
  }

  const threads = await getThreadIndex();
  const titleOf = new Map(threads.map((t) => [t.id, t.title || t.id]));

  const groups = groupByThread(hits);
  resultsEl.innerHTML = groups
    .map((group) => {
      const shown = group.hits.slice(0, PER_GROUP);
      const extra = group.hits.length - shown.length;
      const rows = shown
        .map(
          (hit) => `<a class="search-hit" href="#/thread/${esc(hit.threadId)}/${esc(hit.msgId)}">
            <span class="hit-meta">${esc(dateTimeLabel(hit.msg))} · ${esc(hit.msg.source_ref)} · msg ${esc(hit.msgId)}</span>
            <span class="hit-snippet">${snippetHtml(hit.msg.content, terms)}</span>
          </a>`
        )
        .join('');
      return `<section class="search-group">
        <header class="search-group-head">
          <a href="#/thread/${esc(group.threadId)}">${esc(titleOf.get(group.threadId) || group.threadId)}</a>
          <span class="count">${group.hits.length} resultado${group.hits.length === 1 ? '' : 's'}${extra > 0 ? ` · +${extra}` : ''}</span>
        </header>
        ${rows}
      </section>`;
    })
    .join('');
}
