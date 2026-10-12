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
  // filtro da lista lateral
  initChatListSearch();

  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('scrim');
  const btnMenu = document.getElementById('btn-menu');
  const setDrawer = (open) => {
    sidebar.classList.toggle('open', open);
    scrim.classList.toggle('visible', open);
    scrim.setAttribute('aria-hidden', String(!open));
  };

  // classes de rota no body controlam o layout; thread liga o modo gaveta
  const ROUTES = ['home', 'thread', 'policy', 'conexoes', 'sobre', 'notfound'];
  window.addEventListener('routechange', (e) => {
    const name = e.detail?.name || 'home';
    for (const r of ROUTES) document.body.classList.remove(`route-${r}`);
    document.body.classList.add(`route-${name}`);
    const inThread = name === 'thread';
    document.body.classList.toggle('thread-mode', inThread);
    btnMenu.hidden = !inThread;
    setDrawer(false);
    document.getElementById('btn-network')?.classList.toggle('active', name === 'conexoes');
    document.getElementById('btn-about')?.classList.toggle('active', name === 'sobre');
  });

  btnMenu?.addEventListener('click', () => setDrawer(!sidebar.classList.contains('open')));
  scrim?.addEventListener('click', () => setDrawer(false));
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) setDrawer(false);
  });
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
