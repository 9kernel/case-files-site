// router.js — parse do location.hash e dispatch das views.
// Rotas:
//   #/                        -> home
//   #/policy                  -> política de correções e fontes
//   #/thread/{{id}}           -> conversa (abre no fim)
//   #/thread/{{id}}/{{msgId}} -> conversa com deep-link na mensagem
//   qualquer outra            -> 404

import { renderHome } from './render/home.js';
import { renderChatWindow } from './render/chatWindow.js';
import { renderPolicy } from './render/policy.js';
import { setActiveThread } from './render/chatList.js';
import { closeDocPanel } from './render/docPanel.js';
import { CONFIG } from './config.js';

const view = () => document.getElementById('view');

function parseHash() {
  const hash = location.hash;
  if (!hash || hash === '#' || hash === '#/') return { name: 'home', params: {} };
  const parts = hash.replace(/^#\/?/, '').split('/').map((s) => {
    try {
      return decodeURIComponent(s);
    } catch {
      return s;
    }
  });

  if (parts[0] === 'thread' && parts[1]) {
    return { name: 'thread', params: { id: parts[1], msgId: parts[2] || null } };
  }
  if (parts[0] === 'policy') {
    return { name: 'policy', params: {} };
  }
  return { name: 'notfound', params: {} };
}

function errorCard(title, html) {
  return `<div class="error-card"><h3>${title}</h3>${html}</div>`;
}

export function renderError(err) {
  view().innerHTML = errorCard(
    'Não foi possível carregar',
    `<p>${String(err?.message || err)}</p>
     <p style="margin-top:8px">Os dados ficam em <code>/data</code> e são carregados via
     <code>fetch()</code>, que exige um servidor local (não funciona em <code>file://</code>).</p>
     <a class="btn btn-primary" href="#/">Voltar ao início</a>`
  );
}

let routeSeq = 0;

async function route() {
  const seq = ++routeSeq;
  const { name, params } = parseHash();
  const container = view();

  // estado visual global da rota
  setActiveThread(name === 'thread' ? params.id : null);
  // o painel do documento só existe dentro de uma conversa: qualquer
  // navegação para fora o fecha (abre APENAS por clique na evidência)
  if (name !== 'thread') closeDocPanel();
  window.dispatchEvent(new CustomEvent('routechange', { detail: { name, params } }));

  try {
    switch (name) {
      case 'home':
        document.title = `${CONFIG.HOME_TITLE || CONFIG.CASE_NAME} — ${CONFIG.SITE_TITLE}`;
        await renderHome(container);
        break;
      case 'thread':
        document.title = `Conversa — ${CONFIG.CASE_NAME}`;
        await renderChatWindow(container, params.id, params.msgId);
        break;
      case 'policy':
        document.title = `Política de correções e fontes — ${CONFIG.CASE_NAME}`;
        renderPolicy(container);
        break;
      default:
        document.title = `Página não encontrada — ${CONFIG.CASE_NAME}`;
        container.innerHTML = errorCard(
          'Página não encontrada',
          `<p>Este site usa rotas por hash (ex.: <code>#/thread/grupo-comite-executivo/m-00014</code>).
           Verifique o endereço ou volte ao início.</p>
           <a class="btn btn-primary" href="#/">Voltar ao início</a>`
        );
    }
  } catch (err) {
    console.error('[router]', err);
    if (seq === routeSeq) renderError(err);
  }

  if (name !== 'thread') container.scrollTop = 0;
  container.focus({ preventScroll: true });
}

export function startRouter() {
  window.addEventListener('hashchange', route);
  return route();
}
