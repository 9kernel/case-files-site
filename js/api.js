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

/** Registro central de documentos: data/documents.json (§24) */
export function getDocuments() {
  return fetchJSON('data/documents.json').catch(() => []);
}

/** Map id -> documento. */
export function documentMap(documents) {
  return new Map((documents || []).map((d) => [d.id, d]));
}

/**
 * URL de deep-link para a página do PDF público (§26): PDF_URL#page=N.
 * Prefere a cópia hospedada pelo projeto (hosted_copy_url, mesma origem,
 * alta resolução) e cai para a cópia pública externa. null sem cópia/página.
 */
export function documentPageUrl(doc, page) {
  if (!page) return null;
  const base = doc?.hosted_copy_url || doc?.public_copy_url;
  if (!base) return null;
  return `${base}#page=${page}`;
}

/** Índice leve de threads (título, contagem, última data): data/threads.json */
export function getThreadIndex() {
  return fetchJSON('data/threads.json');
}

/** Thread RAW (inclui registros pending_review) — uso interno/deep-link. */
export function getThreadRaw(id) {
  // slug simples para evitar traversal de caminho
  const safeId = String(id).replace(/[^a-zA-Z0-9._-]/g, '');
  return fetchJSON(`data/threads/${safeId}.json`);
}

const isPublished = (r) => r?.verification?.level !== 'pending_review';

/**
 * Thread para render: retorna uma CÓPIA com apenas mensagens e eventos
 * publicados (verification.level != pending_review fica só nos JSON,
 * nunca no site).
 */
export async function getThread(id) {
  const raw = await getThreadRaw(id);
  return {
    ...raw,
    messages: (raw.messages || []).filter(isPublished),
    timeline_events: (raw.timeline_events || []).filter(isPublished),
  };
}

/** Map id -> participante. */
export function participantMap(participants) {
  return new Map(participants.map((p) => [p.id, p]));
}
