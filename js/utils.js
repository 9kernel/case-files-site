// utils.js — helpers puros: escape, normalização, datas pt-BR, clipboard, toast.

const ESC_MAP = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

/** Escapa texto antes de qualquer innerHTML (proteção XSS a partir do JSON). */
export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (c) => ESC_MAP[c]);
}

export function escapeAttr(value) {
  return escapeHtml(value);
}

/** Escapa e converte quebras de linha em <br>. */
export function nl2br(escapedText) {
  return escapedText.replace(/\r?\n/g, '<br>');
}

/** minúsculas + sem acentos (NFD) — mesma normalização dos dois lados da busca. */
export function normalize(text) {
  return String(text ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

export function debounce(fn, waitMs = 150) {
  let timer = null;
  return function debounced(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), waitMs);
  };
}

/** Tokens normalizados para o índice invertido. */
export function tokenize(text) {
  return normalize(text)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length > 1);
}

/* ---------- datas (sem conversão de fuso: o horário exibido é o do documento) ---------- */

const ISO_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/;

/** Extrai componentes do ISO SEM aplicar fuso do navegador. */
export function isoParts(iso) {
  const m = ISO_RE.exec(String(iso ?? ''));
  if (!m) return null;
  return { y: m[1], mo: m[2], d: m[3], hh: m[4], mm: m[5] };
}

/** 'YYYY-MM-DD' no fuso original do documento. */
export function dayKey(iso) {
  return String(iso ?? '').slice(0, 10);
}

function localDayKey(date) {
  const p = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}`;
}

/** dd/mm/yyyy a partir do ISO do documento. */
export function formatDateBR(iso) {
  const p = isoParts(iso);
  return p ? `${p.d}/${p.mo}/${p.y}` : '';
}

/** HH:MM no fuso original do documento. */
export function formatTime(iso) {
  const p = isoParts(iso);
  return p ? `${p.hh}:${p.mm}` : '';
}

/** Rótulo do separador de data: HOJE / ONTEM / dd/mm/yyyy. */
export function dayLabel(key) {
  const today = new Date();
  if (key === localDayKey(today)) return 'HOJE';
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  if (key === localDayKey(yesterday)) return 'ONTEM';
  return `${key.slice(8, 10)}/${key.slice(5, 7)}/${key.slice(0, 4)}`;
}

const MONTHS_SHORT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

/** Rótulo curto de mês para a TimelineNav: 'mar/24'. */
export function monthLabel(iso) {
  const p = isoParts(iso);
  if (!p) return '';
  return `${MONTHS_SHORT[Number(p.mo) - 1]}/${p.y.slice(2)}`;
}

/** Data completa em pt-BR para a home: '6 de outubro de 2026'. */
export function formatDateLong(isoDate) {
  const d = new Date(`${isoDate}T12:00:00Z`);
  return new Intl.DateTimeFormat('pt-BR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(d);
}

/** Segundos -> 'm:ss'. */
export function formatDuration(sec) {
  const n = Number(sec);
  if (!Number.isFinite(n) || n < 0) return '';
  const m = Math.floor(n / 60);
  const s = Math.round(n % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

/* ---------- deep-link / citação / clipboard ---------- */

/** URL absoluta de deep-link para uma mensagem. */
export function messageUrl(threadId, msgId) {
  return `${location.origin}${location.pathname}#/thread/${encodeURIComponent(threadId)}/${encodeURIComponent(msgId)}`;
}

/**
 * Citação no formato "{{Caso}} — IP {{nº}}, fl. 123, msg {{id}}".
 * source_ref usa '·' como separador; a citação usa vírgula.
 */
export function buildCitation(caseName, sourceRef, msgId) {
  const ref = String(sourceRef ?? '').replace(/\s*·\s*/, ', ');
  return `${caseName} — ${ref}, msg ${msgId}`;
}

/** Clipboard com fallback para contextos sem Clipboard API (http simples/file://). */
export async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* cai no fallback */
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    return ok;
  } catch {
    return false;
  }
}

let toastTimer = null;
export function showToast(message) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.hidden = true;
  }, 2200);
}

/** Tratamento de erro de carregamento de mídia (usado via onerror inline). */
export function installMediaErrorHandler() {
  window.__mediaError = (el) => {
    const wrap = el?.closest?.('.media, .audio-card');
    if (wrap) wrap.classList.add('media-broken');
  };
}

/** Iniciais para avatar (máx. 2 letras). */
export function initials(text) {
  const words = String(text ?? '')
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter(Boolean);
  if (!words.length) return '?';
  const first = words[0][0] || '';
  const second = words.length > 1 ? words[words.length - 1][0] || '' : (words[0][1] || '');
  return (first + second).toUpperCase();
}

/** Cor estável a partir de uma string (avatar, nome de remetente). */
export function hashHue(text) {
  let h = 0;
  for (const ch of String(text ?? '')) {
    h = (h * 31 + ch.codePointAt(0)) >>> 0;
  }
  return h % 360;
}
