// state.js — estado de UI em memória + mini barramento de eventos.

export const state = {
  /** thread aberta no momento (para resetar filtros ao trocar de conversa) */
  threadId: null,
  /** filtros da janela de conversa */
  filters: {
    participant: '',
    from: '', // 'YYYY-MM-DD'
    to: '',
    types: new Set(), // subconjunto dos tipos permitidos
  },
};

export function freshFilters() {
  return { participant: '', from: '', to: '', types: new Set() };
}

const listeners = new Map();

export function on(eventName, fn) {
  if (!listeners.has(eventName)) listeners.set(eventName, new Set());
  listeners.get(eventName).add(fn);
  return () => listeners.get(eventName)?.delete(fn);
}

export function emit(eventName, payload) {
  listeners.get(eventName)?.forEach((fn) => {
    try {
      fn(payload);
    } catch (err) {
      console.error(`[state] listener de "${eventName}" falhou`, err);
    }
  });
}
