// chatList.js — lista lateral de conversas (coluna sempre visível).
// Busca instantânea local por título/participante E, sob demanda, dentro
// das mensagens públicas (data/search-index.json, build-search-index.mjs).

import { getThreadIndex, getParticipants, participantMap, getSearchIndex, getWhatsNew } from '../api.js';
import { state } from '../state.js';
import { openProfileDialog, wireProfileDialog } from './profile.js';
import { escapeHtml as esc, normalize, formatDateBR, initials, hashHue, debounce, avatarPhotoHtml } from '../utils.js';

let participants = null;
let whatsNew = null;

function matches(entry, pmap, query) {
  if (!query) return true;
  if (normalize(entry.title || '').includes(query)) return true;
  return (entry.participants_ids || []).some((id) => {
    const p = pmap.get(id);
    const hay = normalize([p?.name || '', ...(p?.aliases || [])].join(' '));
    return hay.includes(query);
  });
}

/**
 * Busca acento-insensível com mapa de posição: varre o texto bruto dobrando
 * caractere a caractere (NFD sem diacríticos) e devolve o intervalo do 1º
 * trecho que casa — os índices referem-se ao texto ORIGINAL, para destacar.
 */
function findHit(raw, query) {
  const folded = [];
  const map = [];
  let i = 0;
  for (const ch of String(raw)) {
    const f = normalize(ch);
    for (const c of f) {
      folded.push(c);
      map.push(i);
    }
    i += 1;
  }
  const at = folded.join('').indexOf(query);
  if (at < 0) return null;
  const start = map[at];
  const endRaw = map[Math.min(at + query.length - 1, map.length - 1)] + 1;
  return { start, end: endRaw };
}

/**
 * Procura o termo dentro das mensagens públicas de uma conversa.
 * Retorna { snippetHtml, hitCount } ou null. O trecho é truncado em torno
 * da 1ª ocorrência com o termo destacado (<mark>), tudo escapado por partes.
 */
function contentSearch(messages, query) {
  if (!messages?.length) return null;
  let hitCount = 0;
  let first = null;
  for (const raw of messages) {
    const hit = findHit(raw, query);
    if (!hit) continue;
    hitCount += 1;
    if (!first) first = { raw, hit };
  }
  if (!first) return null;

  const { raw, hit } = first;
  const PAD = 42;
  const from = Math.max(0, hit.start - PAD);
  const to = Math.min(raw.length, hit.end + PAD);
  const prefix = (from > 0 ? '…' : '') + raw.slice(from, hit.start);
  const term = raw.slice(hit.start, hit.end);
  const suffix = raw.slice(hit.end, to) + (to < raw.length ? '…' : '');
  const snippetHtml = `${esc(prefix)}<mark>${esc(term)}</mark>${esc(suffix)}`;
  return { snippetHtml, hitCount };
}

/** Inclusões da conversa nos lotes correntes (current_batches do whatsnew.json). */
function recentCount(threadId) {
  const buckets = whatsNew?.threads?.[threadId];
  const current = whatsNew?.current_batches;
  if (!buckets || !Array.isArray(current) || !current.length) return 0;
  return current.reduce((n, label) => n + (buckets[label] || 0), 0);
}

function itemHtml(entry, pmap, activeId, searchCtx) {
  const count = entry.message_count ?? 0;
  const date = formatDateBR(entry.last_message_date);
  const preview = entry.last_message_preview || `${count} mensagem${count === 1 ? '' : 's'}`;
  // contato = primeiro participante que não é o dono da conversa (participants_ids[0])
  const pids = entry.participants_ids || [];
  const contactId = pids.find((id) => id !== pids[0]) || pids[0] || entry.id;
  const contactName = pmap.get(contactId)?.name || contactId;
  const previewHtml = searchCtx
    ? `<span class="preview-hit">${searchCtx.snippetHtml}</span>`
    : esc(preview);
  const badge = searchCtx
    ? `<span class="badge-count hit" title="${searchCtx.hitCount} mensagem(ns) com este termo">${searchCtx.hitCount}</span>`
    : `<span class="badge-count">${count}</span>`;
  const news = recentCount(entry.id);
  const newChip = news
    ? `<span class="new-flag" title="${news} registro(s) incluído(s) na última atualização do acervo">novo</span>`
    : '';
  return `<li>
    <a class="chat-item ${entry.id === activeId ? 'active' : ''}" href="#/thread/${esc(entry.id)}" data-thread-id="${esc(entry.id)}">
      <span class="avatar avatar-btn" data-profile="${esc(contactId)}" role="button" tabindex="0"
        aria-label="Ver perfil de ${esc(contactName)}" title="Ver perfil de ${esc(contactName)}"
        style="--av-color:hsl(${hashHue(contactId)}, 38%, 42%)">${esc(initials(contactName))}${avatarPhotoHtml(participants.get(contactId))}</span>
      <span class="chat-item-main">
        <span class="chat-item-top">
          <span class="chat-item-title">${esc(entry.title || entry.id)}</span>${newChip}
        </span>
        <span class="chat-item-bottom">
          <span class="chat-item-preview">${previewHtml}</span>
          <span class="chat-item-date">${date}</span>${badge}
        </span>
      </span>
    </a>
  </li>`;
}

/** Renderiza (ou atualiza) a lista lateral a partir do filtro atual. */
export async function renderChatList() {
  const ul = document.getElementById('chatlist-items');
  if (!ul) return;

  if (!participants) {
    participants = participantMap(await getParticipants());
  }
  if (!whatsNew) {
    try {
      whatsNew = await getWhatsNew();
    } catch {
      whatsNew = { threads: {} }; // sem artefato: lista segue sem o selo
    }
  }
  const index = await getThreadIndex();
  const query = normalize(state.chatListQuery);
  const activeId = state.threadId;

  // índice de conteúdo só entra em cena quando há termo de busca
  let contentMap = null;
  if (query) {
    try {
      const si = await getSearchIndex();
      contentMap = new Map((si.threads || []).map((t) => [t.id, t.messages || []]));
    } catch {
      contentMap = new Map(); // sem índice: busca cai para nomes/títulos
    }
  }

  const ctx = new Map();
  const items = index.filter((entry) => {
    if (!query) return true;
    if (matches(entry, participants, query)) return true;
    const found = contentSearch(contentMap?.get(entry.id), query);
    if (found) {
      ctx.set(entry.id, found);
      return true;
    }
    return false;
  });
  ul.innerHTML = items.length
    ? items.map((entry) => itemHtml(entry, participants, activeId, ctx.get(entry.id))).join('')
    : `<li><div class="chatlist-empty">Nenhuma conversa encontrada${state.chatListQuery ? ` para “${esc(state.chatListQuery)}”` : ''}.</div></li>`;

  // clique no avatar abre o card de perfil (sem navegar) — ligado uma vez
  if (!ul.dataset.profileWired) {
    ul.dataset.profileWired = '1';
    wireProfileDialog();
    const open = (e, btn) => {
      e.preventDefault();
      e.stopPropagation();
      openProfileDialog(participants.get(btn.getAttribute('data-profile')));
    };
    ul.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-profile]');
      if (btn) open(e, btn);
    });
    ul.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const btn = e.target.closest('[data-profile]');
      if (btn) open(e, btn);
    });
  }
}

/** Destaca a conversa ativa sem recarregar a lista. */
export function setActiveThread(threadId) {
  state.threadId = threadId;
  document.querySelectorAll('#chatlist-items .chat-item').forEach((item) => {
    item.classList.toggle('active', item.getAttribute('data-thread-id') === threadId);
  });
}

/** Liga o campo de filtro lateral (chamado uma vez pelo main.js). */
export function initChatListSearch() {
  const input = document.getElementById('chatlist-search');
  if (!input) return;
  input.addEventListener('input', debounce(() => {
    state.chatListQuery = input.value.trim();
    renderChatList();
  }, 120));
}
