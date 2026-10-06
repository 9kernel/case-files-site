// search.js — índice invertido em memória + busca global com destaque.
//
// Índice: Map<token normalizado, Array<{t: threadId, i: índice na thread}>>.
// Construído de forma assíncrona no boot (uma thread por vez, fora do caminho
// crítico de render) para não derrubar o Lighthouse da rota principal.
// A busca normaliza acentos/caixa dos dois lados (query e conteúdo).

import { getThreadIndex, getThread } from './api.js';
import { tokenize, normalize, escapeHtml, escapeAttr, formatTime, dayKey } from './utils.js';

const MAX_RESULTS = 300;
const SNIPPET_RADIUS = 90;

let indexPromise = null;

/** Inicia a construção do índice (idempotente). */
export function warmupSearchIndex() {
  if (!indexPromise) {
    indexPromise = buildIndex().catch((err) => {
      indexPromise = null; // permite nova tentativa na próxima busca
      throw err;
    });
  }
  return indexPromise;
}

async function buildIndex() {
  const postings = new Map();
  const threads = await getThreadIndex();
  for (const entry of threads) {
    const thread = await getThread(entry.id); // só mensagens confirmed
    thread.messages.forEach((msg, i) => {
      // Set: um termo repetido no mesmo texto não deve duplicar o hit
      for (const token of new Set(tokenize(msg.content || ''))) {
        let arr = postings.get(token);
        if (!arr) {
          arr = [];
          postings.set(token, arr);
        }
        arr.push({ t: entry.id, i });
      }
    });
  }
  return postings;
}

/** Aguarda o índice ficar pronto (constrói sob demanda se necessário). */
export function searchReady() {
  return warmupSearchIndex();
}

/**
 * Busca global. Multi-termo = AND entre os postings de cada token.
 * Retorna { terms, hits: [{threadId, msgId, msg}], truncated }.
 */
export async function search(query) {
  const postings = await searchReady();
  const terms = tokenize(query);
  if (!terms.length) return { terms, hits: [], truncated: false };

  let entries;
  if (terms.length === 1) {
    entries = postings.get(terms[0]) || [];
  } else {
    const sets = terms.map((t) => {
      const arr = postings.get(t) || [];
      return new Set(arr.map((e) => `${e.t}#${e.i}`));
    });
    // intersecta a partir do menor conjunto
    let smallestIdx = 0;
    for (let k = 1; k < sets.length; k++) {
      if (sets[k].size < sets[smallestIdx].size) smallestIdx = k;
    }
    entries = [];
    outer: for (const key of sets[smallestIdx]) {
      for (let k = 0; k < sets.length; k++) {
        if (k !== smallestIdx && !sets[k].has(key)) continue outer;
      }
      const [t, i] = key.split('#');
      entries.push({ t, i: Number(i) });
    }
  }

  const capped = entries.slice(0, MAX_RESULTS);
  const hits = [];
  const threadCache = new Map(); // 1 fetch/promessa por thread, não por hit
  for (const e of capped) {
    let thread = threadCache.get(e.t);
    if (!thread) {
      thread = await getThread(e.t); // cache hit — já carregada no build
      threadCache.set(e.t, thread);
    }
    const msg = thread.messages[e.i];
    if (msg) {
      hits.push({ threadId: e.t, msgId: msg.id, msg });
    }
  }
  return { terms, hits, truncated: entries.length > MAX_RESULTS };
}

/* ---------- destaque / snippet ---------- */

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Escapa o trecho e envolve os termos em <mark>.
 * A busca por acento é normalizada no índice; o destaque usa
 * correspondência direta (maiúsculas/minúsculas ignoradas).
 */
export function highlightHtml(text, terms) {
  let html = escapeHtml(text);
  const patterns = (terms || [])
    .filter((t) => t.length > 1)
    .slice(0, 8)
    .map((t) => escapeRegex(t));
  if (!patterns.length) return html;
  const re = new RegExp(`(${patterns.join('|')})`, 'gi');
  return html.replace(re, '<mark>$1</mark>');
}

/** Janela de texto ao redor da 1ª ocorrência, pronta para destacar. */
export function snippetHtml(content, terms) {
  const raw = String(content ?? '');
  const lower = raw.toLowerCase();
  let pos = -1;
  for (const t of terms || []) {
    if (t.length > 1) {
      const idx = lower.indexOf(t);
      if (idx !== -1 && (pos === -1 || idx < pos)) pos = idx;
    }
  }
  let start = 0;
  let end = raw.length;
  let prefix = '';
  let suffix = '';
  if (pos > SNIPPET_RADIUS) {
    start = pos - SNIPPET_RADIUS / 2;
    prefix = '…';
  }
  if (end - start > SNIPPET_RADIUS * 2) {
    end = start + SNIPPET_RADIUS * 2;
    suffix = '…';
  }
  return prefix + highlightHtml(raw.slice(start, end), terms) + suffix;
}

/** Agrupa hits por thread preservando a ordem cronológica. */
export function groupByThread(hits) {
  const groups = new Map();
  for (const hit of hits) {
    let g = groups.get(hit.threadId);
    if (!g) {
      g = { threadId: hit.threadId, hits: [] };
      groups.set(hit.threadId, g);
    }
    g.hits.push(hit);
  }
  return [...groups.values()];
}

export { formatTime, dayKey };
