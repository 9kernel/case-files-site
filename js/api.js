// api.js — fetch + cache em memória dos JSONs de /data.
// Cache global: um Map de promessas por caminho (evita refetch e races).

const cache = new Map();

/**
 * fetchJSON('data/threads.json') -> Promise<any>
 * Erros indicam problema de rede/404, com dica do servidor local.
 */
export function fetchJSON(path) {
  if (cache.has(path)) return cache.get(path);

  const promise = (async () => {
    let response;
    try {
      response = await fetch(path);
    } catch (err) {
      cache.delete(path);
      throw new Error(
        `Não foi possível carregar ${path}. Se você abriu o arquivo direto (file://), ` +
          `sirva a pasta com um servidor local: python -m http.server 8080`
      );
    }
    if (!response.ok) {
      cache.delete(path);
      throw new Error(`Falha ao carregar ${path} (HTTP ${response.status}).`);
    }
    try {
      return await response.json();
    } catch (err) {
      cache.delete(path);
      throw new Error(`Resposta inválida (não-JSON) em ${path}.`);
    }
  })();

  cache.set(path, promise);
  return promise;
}

/** Lista de participantes: data/participants.json */
export function getParticipants() {
  return fetchJSON('data/participants.json');
}

/** Índice leve de threads (título, contagem, última data): data/threads.json */
export function getThreadIndex() {
  return fetchJSON('data/threads.json');
}

/** Thread RAW (inclui mensagens pending-review) — uso interno/deep-link. */
export function getThreadRaw(id) {
  // slug simples para evitar traversal de caminho
  const safeId = String(id).replace(/[^a-zA-Z0-9._-]/g, '');
  return fetchJSON(`data/threads/${safeId}.json`);
}

/**
 * Thread para render: retorna uma CÓPIA com apenas as mensagens
 * status === 'confirmed' (pending-review fica só nos JSON, nunca no site).
 */
export async function getThread(id) {
  const raw = await getThreadRaw(id);
  return { ...raw, messages: raw.messages.filter((m) => m.status === 'confirmed') };
}

/** Map id -> participante. */
export function participantMap(participants) {
  return new Map(participants.map((p) => [p.id, p]));
}
