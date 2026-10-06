// chatList.js — lista lateral de conversas (coluna no desktop, drawer no mobile).
// Busca instantânea local por título/participante (não usa o índice invertido).

import { getThreadIndex, getParticipants, participantMap } from '../api.js';
import { state } from '../state.js';
import { escapeHtml as esc, normalize, formatDateBR, initials, hashHue, debounce } from '../utils.js';

let participants = null;

function matches(entry, pmap, query) {
  if (!query) return true;
  if (normalize(entry.title || '').includes(query)) return true;
  return (entry.participants_ids || []).some((id) => {
    const p = pmap.get(id);
    const hay = normalize([p?.name || '', ...(p?.aliases || [])].join(' '));
    return hay.includes(query);
  });
}

function itemHtml(entry, pmap, activeId) {
  const count = entry.message_count ?? 0;
  const date = formatDateBR(entry.last_message_at);
  const preview = entry.last_message_preview || `${count} mensagem${count === 1 ? '' : 's'}`;
  return `<li>
    <a class="chat-item ${entry.id === activeId ? 'active' : ''}" href="#/thread/${esc(entry.id)}" data-thread-id="${esc(entry.id)}">
      <span class="avatar" style="--av-color:hsl(${hashHue(entry.id)}, 38%, 42%)">${esc(initials(entry.title))}</span>
      <span class="chat-item-main">
        <span class="chat-item-top">
          <span class="chat-item-title">${esc(entry.title || entry.id)}</span>
          <span class="chat-item-date">${date}</span>
        </span>
        <span class="chat-item-bottom">
          <span class="chat-item-preview">${esc(preview)}</span>
          <span class="badge-count">${count}</span>
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
  const index = await getThreadIndex();
  const query = normalize(state.chatListQuery);
  const activeId = state.threadId;

  const items = index.filter((entry) => matches(entry, participants, query));
  ul.innerHTML = items.length
    ? items.map((entry) => itemHtml(entry, participants, activeId)).join('')
    : `<li><div class="chatlist-empty">Nenhuma conversa encontrada${state.chatListQuery ? ` para “${esc(state.chatListQuery)}”` : ''}.</div></li>`;
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
