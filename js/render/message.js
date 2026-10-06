// message.js — renderização de uma mensagem por tipo (bolha WhatsApp).
// TODO conteúdo dinâmico passa por escapeHtml antes de innerHTML.
// Ícones: SVGs inline mínimos (sem biblioteca).

import { escapeHtml as esc, escapeAttr, nl2br, formatTime, formatDuration, hashHue } from '../utils.js';

const I = {
  link: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
  quote: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  doc: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>`,
  docSmall: `<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>`,
  mic: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v4"/></svg>`,
  play: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M10 8l6 4-6 4z"/></svg>`,
  imgPh: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>`,
  phone: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
  arrowIn: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 7L7 17"/><path d="M7 9v8h8"/></svg>`,
  arrowOut: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7"/><path d="M9 7h8v8"/></svg>`,
  ticks: `<svg class="ticks" viewBox="0 0 18 12" width="15" height="10" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 6.5 4.5 10 11 2"/><path d="M7.5 9.5l1 1L16 2"/></svg>`,
  smiley: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8.5 9.5h.01M15.5 9.5h.01"/><path d="M8.5 14.5c1 1.2 2.2 1.8 3.5 1.8s2.5-.6 3.5-1.8"/></svg>`,
  clip: `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>`,
  phoneHeader: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
  videocam: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>`,
  search: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>`,
  close: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>`,
};

export const icons = I;

const NAME_COLORS = ['#C2185B', '#0288D1', '#7B1FA2', '#00897B', '#EF6C00', '#5D4037', '#455A64'];

export function nameColor(id) {
  return NAME_COLORS[hashHue(id) % NAME_COLORS.length];
}

/** caminho de mídia sempre relativo (funciona em project-pages de subpasta) */
function mediaSrc(m) {
  const url = m?.media?.url;
  return url ? String(url).replace(/^\/+/, '') : '';
}

function captionHtml(m) {
  return m.content ? `<div class="msg-text">${nl2br(esc(m.content))}</div>` : '';
}

function altFor(m) {
  return m.media?.filename || m.content || 'Mídia dos autos';
}

function bodyFor(m) {
  const src = mediaSrc(m);
  switch (m.type) {
    case 'text':
      return `<div class="msg-text">${nl2br(esc(m.content || ''))}</div>`;

    case 'image':
      return `<figure class="media">${
        src
          ? `<button type="button" class="media-zoom" data-action="view-media" aria-label="Ampliar imagem" title="Clique para ampliar">
               <img src="${esc(src)}" alt="${esc(altFor(m))}" loading="lazy" decoding="async"
                 onerror="window.__mediaError && window.__mediaError(this)">
             </button>`
          : `<div class="media-placeholder">${I.imgPh}<span>Imagem — ${esc(m.media?.filename || 'arquivo dos autos')}</span><small>disponível no documento original</small></div>`
      }${captionHtml(m)}</figure>`;

    case 'audio': {
      const dur = formatDuration(m.media?.duration_sec);
      const card = src
        ? `<div class="audio-card">${I.mic}<audio controls preload="metadata" src="${esc(src)}"></audio></div>`
        : `<div class="media-placeholder">${I.mic}<span>Áudio — ${esc(m.media?.filename || 'nota de voz')}</span><small>disponível no documento original</small></div>`;
      return `${card}${dur ? `<span class="audio-dur">Duração: ${esc(dur)}</span>` : ''}${captionHtml(m)}`;
    }

    case 'video':
      return `<figure class="media">${
        src
          ? `<video controls playsinline preload="metadata" src="${esc(src)}"></video>`
          : `<div class="media-placeholder">${I.play}<span>Vídeo — ${esc(m.media?.filename || 'gravação')}</span><small>disponível no documento original</small></div>`
      }${captionHtml(m)}</figure>`;

    case 'document': {
      const filename = m.media?.filename || 'documento';
      const card = src
        ? `<a class="doc-card" href="${esc(src)}" target="_blank" rel="noopener">${I.doc}<span><span class="doc-name">${esc(filename)}</span><span class="doc-hint">Documento dos autos — abrir</span></span></a>`
        : `<div class="doc-card">${I.doc}<span><span class="doc-name">${esc(filename)}</span><span class="doc-hint">Documento dos autos</span></span></div>`;
      return `${card}${captionHtml(m)}`;
    }

    case 'call': {
      const dir = m.call_info?.direction || 'in';
      const arrow = dir === 'out' ? I.arrowOut : I.arrowIn;
      const dur = m.call_info?.duration_sec ? `<span class="call-dur">Duração: ${esc(formatDuration(m.call_info.duration_sec))}</span>` : '';
      return `<div class="call-card ${esc(dir)}">${I.phone}${arrow}<span><span class="call-label">${esc(m.content || 'Chamada de voz')}</span>${dur}</span></div>`;
    }

    default:
      return `<div class="msg-text">${nl2br(esc(m.content || ''))}</div>`;
  }
}

function quoteFor(m, ctx) {
  if (!m.reply_to) return '';
  const original = ctx.byId.get(m.reply_to);
  if (!original) {
    return `<div class="quote quote-missing"><span>Mensagem original não publicada</span></div>`;
  }
  const sender = ctx.pmap.get(original.sender_id)?.name || original.sender_id;
  const preview = (original.content || `[${original.type}]`).slice(0, 110);
  return `<a class="quote" href="#/thread/${esc(ctx.threadId)}/${esc(original.id)}">
    <strong>${esc(sender)}</strong><span>${esc(preview)}</span></a>`;
}

function sourceBadgeHtml(m) {
  return `<button type="button" class="source-badge" data-action="source"
    title="Ver fonte da mensagem (documento e folha)">${I.docSmall}<span>${esc(m.source_ref)}</span></button>`;
}

function actionButtonsHtml() {
  return `<button type="button" class="mini-btn" data-action="copy-link" title="Copiar link da mensagem" aria-label="Copiar link da mensagem">${I.link}</button>
  <button type="button" class="mini-btn" data-action="copy-citation" title="Copiar citação" aria-label="Copiar citação">${I.quote}</button>`;
}

function systemRow(m) {
  return `<div class="sys-row" id="msg-${esc(m.id)}" data-msg-id="${esc(m.id)}">
    <span class="sys-capsule">${nl2br(esc(m.content || ''))}</span>
    <div class="msg-side">${sourceBadgeHtml(m)}</div>
  </div>`;
}

/**
 * Renderiza uma mensagem como HTML string.
 * ctx = { threadId, ownerId, pmap, byId, isGroup }
 */
export function renderMessage(m, ctx) {
  if (m.type === 'system') return systemRow(m);

  const out = m.sender_id === ctx.ownerId;
  const sender = ctx.pmap.get(m.sender_id)?.name || m.sender_id;
  const senderLabel = !out && ctx.isGroup
    ? `<div class="sender-name" style="color:${nameColor(m.sender_id)}">${esc(sender)}</div>`
    : '';

  return `<div class="msg-row ${out ? 'out' : 'in'}" id="msg-${esc(m.id)}" data-msg-id="${esc(m.id)}">
    <div class="bubble-col">
      <div class="bubble">
        ${senderLabel}${quoteFor(m, ctx)}${bodyFor(m)}
        <span class="bubble-meta"><time datetime="${esc(m.timestamp)}">${esc(formatTime(m.timestamp))}</time>${out ? I.ticks : ''}</span>
      </div>
      <div class="msg-side">${sourceBadgeHtml(m)}${actionButtonsHtml()}</div>
    </div>
  </div>`;
}

export { escapeAttr };
