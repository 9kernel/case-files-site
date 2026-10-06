// chatWindow.js — janela da conversa: chunked rendering, separadores de data,
// filtros, TimelineNav, deep-link com destaque, cópia de link/citação e dialog
// de fonte. Nunca renderiza a thread inteira de uma vez (IntersectionObserver).

import { CONFIG } from '../config.js';
import { getThreadRaw, getParticipants, participantMap } from '../api.js';
import { state, freshFilters } from '../state.js';
import { renderMessage, icons } from './message.js';
import { openProfileDialog } from './profile.js';
import {
  escapeHtml as esc,
  dayKey,
  dayLabel,
  monthLabel,
  formatDateBR,
  messageUrl,
  buildCitation,
  copyText,
  showToast,
  initials,
  hashHue,
} from '../utils.js';

const CHUNK = CONFIG.CHUNK_SIZE;

// contexto da renderização corrente (módulo — uma janela por vez)
let ctx = null;
let filtered = [];
let rendered = { start: 0, end: 0 };
let observer = null;
let els = null;
let threadData = null;

const TYPE_OPTIONS = ['text', 'image', 'audio', 'video', 'document', 'call', 'system'];

function applyFilters(list, f) {
  return list.filter((m) => {
    if (f.participant && m.sender_id !== f.participant) return false;
    const dk = dayKey(m.timestamp);
    if (f.from && dk < f.from) return false;
    if (f.to && dk > f.to) return false;
    if (f.types.size && !f.types.has(m.type)) return false;
    return true;
  });
}

function dateSepHtml(key) {
  return `<div class="date-sep"><span>${esc(dayLabel(key))}</span></div>`;
}

/** HTML das mensagens de [from, to), com separadores de data. */
function renderRange(from, to, initialLastDay = null) {
  let html = '';
  let last = initialLastDay;
  for (let i = from; i < to; i++) {
    const m = filtered[i];
    const dk = dayKey(m.timestamp);
    if (dk !== last) {
      html += dateSepHtml(dk);
      last = dk;
    }
    html += renderMessage(m, ctx);
  }
  return html;
}

function updateSentinels() {
  els.topSentinelWrap.style.display = rendered.start > 0 ? '' : 'none';
  els.bottomSentinel.style.display = rendered.end < filtered.length ? '' : 'none';
}

function renderAt(start) {
  const to = Math.min(filtered.length, start + CHUNK);
  const lastDay = start > 0 ? dayKey(filtered[start - 1].timestamp) : null;
  els.list.innerHTML = renderRange(start, to, lastDay);
  rendered = { start, end: to };
  updateSentinels();
  markActiveChip();
}

function appendNext() {
  if (rendered.end >= filtered.length) return;
  const to = Math.min(filtered.length, rendered.end + CHUNK);
  const lastDay = dayKey(filtered[rendered.end - 1].timestamp);
  els.list.insertAdjacentHTML('beforeend', renderRange(rendered.end, to, lastDay));
  rendered = { ...rendered, end: to };
  updateSentinels();
  markActiveChip();
}

function prependPrev() {
  if (rendered.start <= 0) return;
  const start = Math.max(0, rendered.start - CHUNK);
  const frag = renderRange(start, rendered.start);
  const prevHeight = els.scroll.scrollHeight;
  const prevTop = els.scroll.scrollTop;
  els.list.insertAdjacentHTML('afterbegin', frag);
  rendered = { ...rendered, start };
  els.scroll.scrollTop = prevTop + (els.scroll.scrollHeight - prevHeight);
  updateSentinels();
  markActiveChip();
}

/* ---------- TimelineNav ---------- */

function buildMonths() {
  const months = [];
  let lastKey = null;
  filtered.forEach((m, i) => {
    const key = m.timestamp.slice(0, 7);
    if (key !== lastKey) {
      months.push({ key, idx: i, label: monthLabel(m.timestamp) });
      lastKey = key;
    }
  });
  return months;
}

function renderRail() {
  const months = buildMonths();
  els.nav.innerHTML = months
    .map((mo) => `<button type="button" class="tl-chip" data-idx="${mo.idx}" title="Ir para ${esc(mo.key)}">${esc(mo.label)}</button>`)
    .join('');
}

function markActiveChip() {
  const idx = rendered.start;
  let activeKey = null;
  for (const chip of els.nav.querySelectorAll('.tl-chip')) {
    const chipIdx = Number(chip.dataset.idx);
    if (chipIdx <= idx) activeKey = chip.dataset.idx;
  }
  els.nav.querySelectorAll('.tl-chip').forEach((chip) => {
    chip.classList.toggle('active', chip.dataset.idx === activeKey);
  });
}

/* ---------- dialog de fonte ---------- */

export function openSourceDialog(message, thread) {
  const dlg = document.getElementById('source-dialog');
  if (!dlg) return;
  dlg.querySelector('#sd-ref').textContent = message
    ? message.source_ref
    : `${thread.source.document} · ${thread.source.pages || 'sem paginação'}`;
  dlg.querySelector('#sd-doc').textContent = thread.source.document;
  dlg.querySelector('#sd-pages').textContent = thread.source.pages || '—';
  const link = dlg.querySelector('#sd-url');
  if (thread.source.url) {
    link.href = thread.source.url;
    link.hidden = false;
  } else {
    link.hidden = true;
  }
  dlg.showModal();
}

/* ---------- dialog de mídia (lightbox) ---------- */

export function openMediaDialog(message) {
  const url = message?.media?.url;
  if (!url) return;
  const dlg = document.getElementById('media-dialog');
  if (!dlg) return;

  const img = dlg.querySelector('#md-img');
  img.src = String(url).replace(/^\/+/, '');
  img.alt = message.media?.filename || message.content || 'Mídia dos autos';
  dlg.classList.remove('zoomed');

  const caption = dlg.querySelector('#md-caption');
  caption.textContent = message.content || message.media?.filename || '';

  const ref = dlg.querySelector('#md-ref');
  ref.textContent = `${message.source_ref} · msg ${message.id}`;

  const open = dlg.querySelector('#md-open');
  open.href = img.src;

  dlg.showModal();
}

function wireMediaDialog() {
  const dlg = document.getElementById('media-dialog');
  if (!dlg || dlg.dataset.wired) return;
  dlg.dataset.wired = '1';

  dlg.querySelector('#md-close').addEventListener('click', () => dlg.close());
  dlg.querySelector('#md-img').addEventListener('click', () => {
    dlg.classList.toggle('zoomed');
  });
  // clique no fundo escuro fecha (fora do conteúdo central)
  dlg.addEventListener('click', (e) => {
    if (e.target === dlg) dlg.close();
  });
}

/* ---------- filtros ---------- */

function filterBarHtml() {
  const f = state.filters;
  const options = threadData.participants_ids
    .map((id) => {
      const name = ctx.pmap.get(id)?.name || id;
      return `<option value="${esc(id)}" ${f.participant === id ? 'selected' : ''}>${esc(name)}</option>`;
    })
    .join('');
  const checks = TYPE_OPTIONS
    .map((t) => `<label><input type="checkbox" name="ft-type" value="${t}" ${f.types.has(t) ? 'checked' : ''}> ${t}</label>`)
    .join('');
  return `
  <div class="filter-grid">
    <label class="field">Participante
      <select id="ft-participant">
        <option value="">Todos</option>${options}
      </select>
    </label>
    <label class="field">De <input type="date" id="ft-from" value="${esc(f.from)}"></label>
    <label class="field">Até <input type="date" id="ft-to" value="${esc(f.to)}"></label>
    <div class="field">Tipo<span class="type-checks">${checks}</span></div>
    <button type="button" class="btn btn-primary" id="ft-apply">Aplicar filtros</button>
    <button type="button" class="btn btn-ghost" id="ft-clear">Limpar</button>
  </div>`;
}

/* ---------- banner de deep-link ---------- */

function warnBanner(html) {
  return `<div class="banner" role="status">${html}</div>`;
}

/* ---------- render principal ---------- */

export async function renderChatWindow(container, threadId, targetMsgId) {
  const raw = await getThreadRaw(threadId).catch(() => null);
  if (!raw || !Array.isArray(raw.messages)) {
    container.innerHTML = `<div class="error-card"><h3>Conversa não encontrada</h3>
      <p>Não há dados publicados para <code>${esc(threadId)}</code>.</p>
      <a class="btn btn-primary" href="#/">Voltar ao início</a></div>`;
    return;
  }

  if (state.threadId !== threadId) {
    state.threadId = threadId;
    state.filters = freshFilters();
  }

  threadData = raw;
  const confirmed = raw.messages.filter((m) => m.status === 'confirmed');
  const pmap = participantMap(await getParticipants());
  const byId = new Map(raw.messages.map((m) => [m.id, m]));
  filtered = applyFilters(confirmed, state.filters);
  ctx = { threadId, ownerId: raw.participants_ids[0], pmap, byId, isGroup: raw.participants_ids.length > 2 };

  // resolução do deep-link
  let banner = '';
  let targetIdx = -1;
  if (targetMsgId) {
    const target = byId.get(targetMsgId);
    if (!target) {
      banner = warnBanner(`Mensagem <strong>${esc(targetMsgId)}</strong> não encontrada nesta conversa.`);
    } else if (target.status !== 'confirmed') {
      banner = warnBanner(
        `A mensagem <strong>${esc(targetMsgId)}</strong> existe nos dados, mas está com status
         <strong>pending-review</strong> e ainda não é publicada no site.`
      );
    } else {
      targetIdx = filtered.findIndex((m) => m.id === targetMsgId);
      if (targetIdx === -1) {
        banner = warnBanner(
          `A mensagem <strong>${esc(targetMsgId)}</strong> está oculta pelos filtros ativos.
           <button type="button" class="linklike" id="banner-clear">Limpar filtros</button>`
        );
      }
    }
  }

  const len = filtered.length;
  const title = raw.title || threadId;
  // como no WhatsApp: em 1:1 o subtítulo é o cargo/status do contato; em grupo, todos
  const others = raw.participants_ids.filter((id) => id !== ctx.ownerId);
  const contactId = others[0] || raw.participants_ids[0] || threadId;
  const contact = ctx.pmap.get(contactId);
  const contactName = contact?.name || contactId;
  const participantsLine = (ctx.isGroup
    ? raw.participants_ids.map((id) => pmap.get(id)?.name || id)
    : others.map((id) => pmap.get(id)?.role || pmap.get(id)?.name || id)
  ).join(', ');

  container.innerHTML = `
  <section class="chat">
    <header class="chat-header">
      <button type="button" class="icon-btn only-mobile" id="btn-back" aria-label="Voltar">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
      </button>
      <button type="button" class="avatar avatar-btn only-desktop" id="hdr-avatar" data-profile="${esc(contactId)}"
        aria-label="Ver perfil de ${esc(contactName)}" title="Ver perfil de ${esc(contactName)}"
        style="--av-color:hsl(${hashHue(contactId)}, 38%, 42%)">${esc(initials(contactName))}</button>
      <div class="chat-title">
        <h2>${esc(title)}</h2>
        <p>${esc(participantsLine)}</p>
      </div>
      <button type="button" class="chat-source-link" id="chat-source" title="Ver fonte do documento">${esc(raw.source?.document || '')}${raw.source?.pages ? ` · ${esc(raw.source.pages)}` : ''}</button>
      <button type="button" class="icon-btn only-desktop" disabled title="Chamadas não fazem parte do arquivo" aria-label="Chamada (indisponível no arquivo)">${icons.phoneHeader}</button>
      <button type="button" class="icon-btn only-desktop" disabled title="Videochamadas não fazem parte do arquivo" aria-label="Videochamada (indisponível no arquivo)">${icons.videocam}</button>
      <button type="button" class="icon-btn" id="hdr-search" title="Buscar no arquivo" aria-label="Buscar no arquivo">${icons.search}</button>
      <button type="button" class="icon-btn" id="btn-filters" aria-expanded="false" aria-controls="filter-bar" title="Filtros">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16"/><path d="M7 12h10"/><path d="M10 18h4"/></svg>
      </button>
    </header>
    <div class="filter-bar" id="filter-bar" hidden>${filterBarHtml()}</div>
    <div class="chat-main">
      <div class="chat-scroll" id="chat-scroll" tabindex="0" aria-label="Mensagens da conversa">
        <div class="banner-slot" id="banner-slot">${banner}</div>
        <div id="top-sentinel-wrap"><div class="sentinel" id="top-sentinel"></div></div>
        <div id="msg-list" aria-live="polite"></div>
        <div class="sentinel" id="bottom-sentinel"></div>
      </div>
      <nav class="timeline-nav" id="timeline-nav" aria-label="Índice de meses da conversa"></nav>
    </div>
    <div class="chat-inputbar" aria-label="Arquivo somente leitura">
      <button type="button" class="icon-btn" disabled title="Emoji (indisponível no arquivo)" aria-label="Emoji (indisponível no arquivo)">${icons.smiley}</button>
      <button type="button" class="icon-btn" disabled title="Anexar (indisponível no arquivo)" aria-label="Anexar (indisponível no arquivo)">${icons.clip}</button>
      <div class="chat-input-fake">Arquivo somente leitura — mensagens reproduzidas dos autos</div>
      <button type="button" class="icon-btn input-mic" disabled title="Gravar áudio (indisponível no arquivo)" aria-label="Gravar áudio (indisponível no arquivo)">${icons.mic}</button>
    </div>
  </section>`;

  els = {
    scroll: container.querySelector('#chat-scroll'),
    list: container.querySelector('#msg-list'),
    topSentinelWrap: container.querySelector('#top-sentinel-wrap'),
    topSentinel: container.querySelector('#top-sentinel'),
    bottomSentinel: container.querySelector('#bottom-sentinel'),
    nav: container.querySelector('#timeline-nav'),
    filterBar: container.querySelector('#filter-bar'),
  };

  // cabeçalho e filtros
  container.querySelector('#hdr-avatar')?.addEventListener('click', () => {
    openProfileDialog(ctx.pmap.get(contactId));
  });
  container.querySelector('#chat-source').addEventListener('click', () => openSourceDialog(null, raw));
  const btnFilters = container.querySelector('#btn-filters');
  btnFilters.addEventListener('click', () => {
    const willOpen = els.filterBar.hidden;
    els.filterBar.hidden = !willOpen;
    btnFilters.setAttribute('aria-expanded', String(willOpen));
  });

  const applyFiltersFromInputs = () => {
    const types = new Set();
    els.filterBar.querySelectorAll('input[name="ft-type"]:checked').forEach((c) => types.add(c.value));
    state.filters = {
      participant: els.filterBar.querySelector('#ft-participant').value,
      from: els.filterBar.querySelector('#ft-from').value,
      to: els.filterBar.querySelector('#ft-to').value,
      types,
    };
    renderChatWindow(container, threadId, null);
  };
  els.filterBar.querySelector('#ft-apply').addEventListener('click', applyFiltersFromInputs);
  els.filterBar.querySelector('#ft-clear').addEventListener('click', () => {
    state.filters = freshFilters();
    renderChatWindow(container, threadId, null);
  });
  container.querySelector('#banner-clear')?.addEventListener('click', () => {
    state.filters = freshFilters();
    renderChatWindow(container, threadId, targetMsgId);
  });

  container.querySelector('#btn-back').addEventListener('click', () => {
    if (history.length > 1) history.back();
    else location.hash = '#/';
  });

  // ícone de busca do header -> foca a busca global
  container.querySelector('#hdr-search')?.addEventListener('click', () => {
    document.getElementById('global-search-input')?.focus();
  });
  wireMediaDialog();

  // timeline nav
  renderRail();
  els.nav.addEventListener('click', (e) => {
    const chip = e.target.closest('.tl-chip');
    if (!chip) return;
    const idx = Number(chip.dataset.idx);
    renderAt(idx);
    els.scroll.scrollTop = 0;
    history.replaceState(null, '', `#/thread/${encodeURIComponent(threadId)}/${encodeURIComponent(filtered[idx].id)}`);
  });

  // render inicial (chunk do alvo ou do fim)
  const start = targetIdx >= 0 ? Math.max(0, targetIdx - 10) : Math.max(0, len - CHUNK);
  if (len === 0) {
    els.list.innerHTML = `<div class="empty-state"><h3>Nenhuma mensagem</h3>
      <p>Nenhuma mensagem corresponde aos filtros ativos.</p>
      <button type="button" class="btn btn-ghost" id="empty-clear">Limpar filtros</button></div>`;
    container.querySelector('#empty-clear').addEventListener('click', () => {
      state.filters = freshFilters();
      renderChatWindow(container, threadId, null);
    });
  } else {
    renderAt(start);
  }

  // scroll inicial: deep-link -> centra e destaca; sem alvo -> fim da conversa
  if (targetIdx >= 0) {
    const focusTarget = () => {
      const el = document.getElementById(`msg-${CSS.escape(targetMsgId)}`);
      if (!el) return false;
      el.scrollIntoView({ block: 'center' });
      el.classList.add('msg-highlight');
      return true;
    };
    focusTarget();
    // reforço: garante o destaque mesmo se o layout assentar depois
    setTimeout(() => {
      const el = document.querySelector('.msg-highlight');
      if (!el) focusTarget();
    }, 80);
    setTimeout(() => {
      document.querySelector('.msg-highlight')?.classList.remove('msg-highlight');
    }, 2600);
  } else if (len > 0) {
    els.scroll.scrollTop = els.scroll.scrollHeight;
  }

  // IntersectionObserver: chunks progressivos nas duas pontas
  observer?.disconnect();
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        if (entry.target === els.bottomSentinel) appendNext();
        else if (entry.target === els.topSentinel) prependPrev();
      }
    },
    { root: els.scroll, rootMargin: '400px 0px' }
  );
  observer.observe(els.topSentinel);
  observer.observe(els.bottomSentinel);

  // delegação de ações: copiar link / citação / abrir fonte
  els.list.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const row = btn.closest('[data-msg-id]');
    const msgId = row?.getAttribute('data-msg-id');
    const message = byId.get(msgId);
    if (!message) return;

    switch (btn.dataset.action) {
      case 'copy-link': {
        const ok = await copyText(messageUrl(threadId, msgId));
        showToast(ok ? 'Link da mensagem copiado.' : 'Não foi possível copiar o link.');
        break;
      }
      case 'copy-citation': {
        const citation = buildCitation(CONFIG.CASE_NAME, message.source_ref, msgId);
        const ok = await copyText(citation);
        showToast(ok ? 'Citação copiada.' : 'Não foi possível copiar a citação.');
        break;
      }
      case 'source':
        openSourceDialog(message, raw);
        break;
      case 'view-media':
        openMediaDialog(message);
        break;
    }
  });
}
