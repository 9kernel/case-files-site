// main.js — bootstrap: carrega participantes, liga UI global e inicia o router.

import { getParticipants } from './api.js';
import { startRouter } from './router.js';
import { installMediaErrorHandler } from './utils.js';

function errorCardHtml(err) {
  return `<div class="error-card"><h3>Não foi possível iniciar</h3>
    <p>${String(err?.message || err)}</p>
    <p style="margin-top:8px">Os dados em <code>/data</code> são carregados via <code>fetch()</code>:
    abra o site por um servidor local (<code>python -m http.server 8080</code>) —
    não funciona abrindo <code>index.html</code> direto (<code>file://</code>).</p></div>`;
}

async function init() {
  installMediaErrorHandler();

  try {
    await getParticipants(); // aquece cache compartilhado
    await startRouter();
  } catch (err) {
    document.getElementById('view').innerHTML = errorCardHtml(err);
    console.error('[main]', err);
  }
}

init();
