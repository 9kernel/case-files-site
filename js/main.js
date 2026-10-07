// main.js — bootstrap: carrega participantes, liga UI global e inicia o router.

import { getParticipants } from './api.js';
import { renderChatList, initChatListSearch } from './render/chatList.js';
import { startRouter } from './router.js';
import { installMediaErrorHandler } from './utils.js';

function errorCardHtml(err) {
  return `<div class="error-card"><h3>Não foi possível iniciar</h3>
    <p>${String(err?.message || err)}</p>
    <p style="margin-top:8px">Os dados em <code>/data</code> são carregados via <code>fetch()</code>:
    abra o site por um servidor local (<code>python -m http.server 8080</code>) —
    não funciona abrindo <code>index.html</code> direto (<code>file://</code>).</p></div>`;
}

function wireTopbar() {
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

  // filtro da lista lateral
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
  }
}

init();
