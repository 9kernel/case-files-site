// docPanel.js — painel de visualização documental ao lado do chat (§17-19)
// Drawer à direita (estilo WhatsApp Web) com o PDF público aberto na página
// da mensagem. Sem URL pública: estado informativo — caminhos locais NUNCA
// são expostos no site (missão §18).

import { getDocuments, documentMap, documentPageUrl } from '../api.js';
import { escapeHtml as esc } from '../utils.js';

let current = null; // { docId, page }

function panel() {
  return document.getElementById('doc-panel');
}

function setHeader(doc, page, figure) {
  const p = panel();
  p.querySelector('#dp-title').textContent = doc?.title || 'Documento';
  p.querySelector('#dp-sub').textContent = doc
    ? `${doc.authority || ''}${doc.case ? ` · ${doc.case}` : ''}`
    : '';
  p.querySelector('#dp-page').textContent = page
    ? `fl. ${page}${figure ? ` · figura ${figure}` : ''}`
    : '';
  const ext = p.querySelector('#dp-open');
  const url = documentPageUrl(doc, page);
  if (url) {
    ext.href = url;
    ext.hidden = false;
  } else {
    ext.hidden = true;
  }
}

export function openDocPanel(doc, page, figure) {
  const p = panel();
  if (!p || !doc) return;
  current = { docId: doc.id, page };

  const frameHost = p.querySelector('#dp-frame');
  const url = documentPageUrl(doc, page);
  if (url) {
    // link-only (§2.3): o projeto não redistribui peças — o PDF é exibido da
    // origem pública (cópia externa) ou de eventual cópia same-origin; o
    // visualizador nativo do navegador cuida de zoom/rolagem/busca e #page=N
    // abre direto na página da mensagem
    const external = /^https?:\/\//.test(url);
    let host = '';
    try { host = external ? new URL(url).hostname : ''; } catch { host = ''; }
    const banner = external
      ? `<div class="dp-ext">Cópia pública externa (${esc(host)}) — o projeto não redistribui peças dos autos (link-only).`
        + ` A conferência definitiva é sempre no documento original dos autos.</div>`
      : '';
    frameHost.innerHTML = banner + `<iframe src="${esc(url)}" title="${esc(doc.title)} — página ${page || '?'}"></iframe>`;
    p.querySelector('#dp-empty').hidden = true;
  } else {
    frameHost.innerHTML = '';
    p.querySelector('#dp-empty').hidden = false;
    p.querySelector('#dp-empty').innerHTML = `
      <p><strong>Cópia pública não catalogada.</strong></p>
      <p>Este documento ainda não possui URL pública catalogada para
      exibição. Consulte a peça na origem oficial do processo
      (ver diálogo de fontes da conversa).</p>`;
  }
  setHeader(doc, page, figure);
  p.hidden = false;
  document.body.classList.add('doc-panel-open');
}

export function closeDocPanel() {
  const p = panel();
  if (!p) return;
  current = null;
  // descarrega o PDF embutido (evita manter ~MBs na memória)
  p.querySelector('#dp-frame').innerHTML = '';
  p.hidden = true;
  document.body.classList.remove('doc-panel-open');
}

export function isDocPanelOpen() {
  return !!current;
}

/** §19: seleção de mensagem atualiza o painel aberto. */
export async function syncDocPanel(record) {
  if (!current || !record?.source?.document_id) return;
  if (record.source.document_id === current.docId && record.source.page === current.page) return;
  const docs = documentMap(await getDocuments());
  openDocPanel(docs.get(record.source.document_id), record.source.page, record.source.figure);
}

export function wireDocPanel() {
  const p = panel();
  if (!p || p.dataset.wired) return;
  p.dataset.wired = '1';
  p.querySelector('#dp-close').addEventListener('click', closeDocPanel);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !p.hidden) closeDocPanel();
  });
}
