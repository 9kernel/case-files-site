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
  // filtro da lista lateral (coluna sempre visível — sem drawer no mobile)
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
