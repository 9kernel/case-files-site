// main.js — bootstrap: carrega participantes, liga UI global, inicia router
// e aquece o índice de busca fora do caminho crítico.

import { getParticipants } from './api.js';
import { renderChatList, initChatListSearch } from './render/chatList.js';
import { startRouter } from './router.js';
import { warmupSearchIndex } from './search.js';
import { installMediaErrorHandler } from './utils.js';
import { CONFIG } from './config.js';

function errorCardHtml(err) {
  return `<div class="error-card"><h3>Não foi possível iniciar</h3>
    <p>${String(err?.message || err)}</p>
    <p style="margin-top:8px">Os dados em <code>/data</code> são carregados via <code>fetch()</code>:
    abra o site por um servidor local (<code>python -m http.server 8080</code>) —
    não funciona abrindo <code>index.html</code> direto (<code>file://</code>).</p></div>`;
}

function submitGlobalSearch(input) {
  const q = input.value.trim();
  if (q) location.hash = `#/search/${encodeURIComponent(q)}`;
  input.blur();
}

function wireTopbar() {
  const form = document.getElementById('global-search');
  const input = document.getElementById('global-search-input');
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    submitGlobalSearch(input);
  });
  // Enter explícito: nem todo webview dispara o submit implícito do formulário
  input?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      submitGlobalSearch(input);
    }
  });

  // drawer mobile
  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('scrim');
  const setDrawer = (open) => {
    sidebar.classList.toggle('open', open);
    scrim.classList.toggle('visible', open);
    scrim.setAttribute('aria-hidden', String(!open));
  };
  document.getElementById('btn-menu')?.addEventListener('click', () => setDrawer(!sidebar.classList.contains('open')));
  scrim?.addEventListener('click', () => setDrawer(false));
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) setDrawer(false);
  });
  // fecha o drawer ao navegar para uma conversa
  window.addEventListener('routechange', () => setDrawer(false));

  // busca da lista lateral
  initChatListSearch();
}

async function init() {
  installMediaErrorHandler();
  wireTopbar();

  try {
    await getParticipants(); // aquece cache compartilhado
    await renderChatList();
    await startRouter();
  } catch (err) {
    document.getElementById('view').innerHTML = errorCardHtml(err);
    console.error('[main]', err);
    return;
  }

  // índice de busca: construído depois do primeiro paint
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 300));
  idle(() => {
    warmupSearchIndex().catch((err) => console.warn('[search] índice adiado:', err.message));
  });
}

init();
