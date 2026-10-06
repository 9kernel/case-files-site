#!/usr/bin/env node
// validate.mjs — validador dos JSONs de /data, Node puro, sem dependências.
//
// Uso:  node scripts/validate.mjs [dataDir]      (padrão: <repo>/data)
// Exit 1 se houver QUALQUER erro; warnings não derrubam o CI.
//
// Regras que geram ERRO (CI vermelho):
//   E_JSON_PARSE          qualquer JSON inválido (JSON.parse em try/catch)
//   E_MISSING_SOURCE_REF  mensagem sem source_ref
//   E_MISSING_STATUS      mensagem sem status
//   E_BAD_STATUS          status fora de confirmed | pending-review
//   E_UNKNOWN_SENDER      sender_id inexistente em participants.json
//   E_MISSING_SENDER      mensagem sem sender_id
//   E_TIMESTAMP_ORDER     timestamps fora de ordem cronológica na thread
//   E_BAD_TIMESTAMP       timestamp ausente ou fora do formato ISO 8601 c/ offset
//   E_DUPLICATE_ID        ids de mensagem duplicados
//   E_BAD_ID / E_MISSING_ID  id ausente ou fora do padrão m-NNNNN
//   E_BAD_TYPE            type fora da lista permitida
//   E_MISSING_ADDED_IN    mensagem sem added_in
//   E_BAD_CONTENT         content não é string
//   E_BAD_REPLY_TO        reply_to aponta para mensagem inexistente na thread
//   E_MISSING_MEDIA_FILE  media.url aponta para arquivo inexistente em /public
//   E_THREAD_FIELD        thread sem id/title/participants_ids/source válidos
//   E_ID_MISMATCH         thread.id difere do nome do arquivo
//   E_UNKNOWN_PARTICIPANT participants_ids cita id fora de participants.json
//   E_DUP_PARTICIPANT     participants.json com ids duplicados
//   E_INDEX_MISMATCH      threads.json e threads/*.json fora de sincronia
//
// Warnings (não bloqueiam): E_COUNT_MISMATCH (contagem no índice desatualizada).

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ALLOWED_TYPES = new Set(['text', 'image', 'audio', 'video', 'document', 'call', 'system']);
const ALLOWED_STATUS = new Set(['confirmed', 'pending-review']);
const ISO_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$/;
const ID_RE = /^m-\d{5,}$/;

/**
 * Valida o diretório de dados. Retorna { errors, warnings, stats }.
 * @param {string} dataDir  diretório com participants.json e threads/
 * @param {string} [rootDir] raiz do repositório (para checar mídia em /public)
 */
export function validateData(dataDir, rootDir) {
  const errors = [];
  const warnings = [];
  const err = (code, file, message) => errors.push({ code, file, message });
  const warn = (code, file, message) => warnings.push({ code, file, message });

  rootDir = rootDir || path.resolve(dataDir, '..');
  const threadsDir = path.join(dataDir, 'threads');

  /* ---------- participants.json ---------- */
  let participants;
  const pFile = path.join(dataDir, 'participants.json');
  try {
    participants = JSON.parse(fs.readFileSync(pFile, 'utf8'));
  } catch (e) {
    err('E_JSON_PARSE', 'data/participants.json', `JSON inválido: ${e.message}`);
    return { errors, warnings, stats: { threads: 0, messages: 0 } };
  }
  const participantIds = new Set();
  if (!Array.isArray(participants)) {
    err('E_THREAD_FIELD', 'data/participants.json', 'participants.json deve ser um array.');
    participants = [];
  }
  for (const p of participants) {
    if (!p || typeof p.id !== 'string' || !p.id) {
      err('E_THREAD_FIELD', 'data/participants.json', 'Participante sem "id".');
      continue;
    }
    if (participantIds.has(p.id)) {
      err('E_DUP_PARTICIPANT', 'data/participants.json', `id de participante duplicado: "${p.id}"`);
    }
    participantIds.add(p.id);
  }

  /* ---------- threads/index (threads.json) ---------- */
  const indexFile = path.join(dataDir, 'threads.json');
  let indexIds = new Set();
  if (fs.existsSync(indexFile)) {
    try {
      const index = JSON.parse(fs.readFileSync(indexFile, 'utf8'));
      if (!Array.isArray(index)) {
        err('E_THREAD_FIELD', 'data/threads.json', 'threads.json deve ser um array.');
      } else {
        for (const entry of index) {
          if (entry?.id) indexIds.add(entry.id);
          else err('E_THREAD_FIELD', 'data/threads.json', 'Entrada do índice sem "id".');
        }
      }
    } catch (e) {
      err('E_JSON_PARSE', 'data/threads.json', `JSON inválido: ${e.message}`);
    }
  }

  /* ---------- threads/*.json ---------- */
  if (!fs.existsSync(threadsDir)) {
    err('E_THREAD_FIELD', 'data/threads/', 'Diretório data/threads não existe.');
    return { errors, warnings, stats: { threads: 0, messages: 0 } };
  }

  const files = fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort();
  const fileIds = new Set();
  let totalMessages = 0;

  for (const file of files) {
    const rel = `data/threads/${file}`;
    const full = path.join(threadsDir, file);
    let thread;
    try {
      thread = JSON.parse(fs.readFileSync(full, 'utf8'));
    } catch (e) {
      err('E_JSON_PARSE', rel, `JSON inválido: ${e.message}`);
      continue;
    }

    // estrutura de topo
    if (typeof thread.id !== 'string' || !thread.id) {
      err('E_THREAD_FIELD', rel, 'Thread sem "id".');
    } else {
      fileIds.add(thread.id);
      if (thread.id !== path.basename(file, '.json')) {
        err('E_ID_MISMATCH', rel, `thread.id "${thread.id}" difere do nome do arquivo "${file}".`);
      }
    }
    if (typeof thread.title !== 'string' || !thread.title) err('E_THREAD_FIELD', rel, 'Thread sem "title".');
    const pIds = Array.isArray(thread.participants_ids) ? thread.participants_ids : null;
    if (!pIds || !pIds.length) {
      err('E_THREAD_FIELD', rel, 'Thread sem "participants_ids".');
    } else {
      for (const pid of pIds) {
        if (!participantIds.has(pid)) {
          err('E_UNKNOWN_PARTICIPANT', rel, `participants_ids cita "${pid}", ausente em participants.json.`);
        }
      }
    }
    const src = thread.source;
    if (!src || typeof src !== 'object' || typeof src.document !== 'string' || !src.document ||
        typeof src.url !== 'string' || typeof src.pages !== 'string') {
      err('E_THREAD_FIELD', rel, 'Thread sem "source" completo (document, url, pages).');
    }
    if (!Array.isArray(thread.messages)) {
      err('E_THREAD_FIELD', rel, 'Thread sem array "messages".');
      continue;
    }

    // coleta ids para validar reply_to depois
    const ids = new Set(thread.messages.map((m) => m?.id).filter(Boolean));
    const seenIds = new Set(); // duplicatas são por thread (ids reiniciam em cada arquivo)
    let prevTime = null;
    totalMessages += thread.messages.length;

    for (let i = 0; i < thread.messages.length; i++) {
      const m = thread.messages[i];
      const where = `${rel} · messages[${i}]`;
      if (!m || typeof m !== 'object') {
        err('E_THREAD_FIELD', where, 'Elemento não é um objeto.');
        continue;
      }

      // id
      if (m.id == null || m.id === '') {
        err('E_MISSING_ID', where, 'Mensagem sem "id".');
      } else if (!ID_RE.test(m.id)) {
        err('E_BAD_ID', where, `id "${m.id}" fora do padrão m-NNNNN sequencial.`);
      }

      // duplicidade (Set local por thread)
      if (m.id && seenIds.has(m.id)) {
        err('E_DUPLICATE_ID', where, `id de mensagem duplicado: "${m.id}"`);
      }
      if (m.id) seenIds.add(m.id);

      // sender
      if (m.sender_id == null || m.sender_id === '') {
        err('E_MISSING_SENDER', where, 'Mensagem sem "sender_id".');
      } else if (!participantIds.has(m.sender_id)) {
        err('E_UNKNOWN_SENDER', where, `sender_id "${m.sender_id}" não existe em participants.json.`);
      }

      // type
      if (!ALLOWED_TYPES.has(m.type)) {
        err('E_BAD_TYPE', where, `type "${m.type}" fora da lista permitida (${[...ALLOWED_TYPES].join(', ')}).`);
      }

      // timestamp
      if (m.timestamp == null || m.timestamp === '') {
        err('E_BAD_TIMESTAMP', where, 'Mensagem sem "timestamp".');
      } else if (typeof m.timestamp !== 'string' || !ISO_RE.test(m.timestamp) || Number.isNaN(Date.parse(m.timestamp))) {
        err('E_BAD_TIMESTAMP', where, `timestamp "${m.timestamp}" não é ISO 8601 com offset (ex.: 2024-03-12T14:02:00-03:00).`);
      } else {
        const t = Date.parse(m.timestamp);
        if (prevTime !== null && t < prevTime) {
          err('E_TIMESTAMP_ORDER', where, `timestamp ${m.timestamp} anterior ao da mensagem anterior (${new Date(prevTime).toISOString()}).`);
        }
        prevTime = t;
      }

      // campos obrigatórios de rastreabilidade
      if (m.source_ref == null || String(m.source_ref).trim() === '') {
        err('E_MISSING_SOURCE_REF', where, 'Mensagem sem "source_ref".');
      }
      if (m.status == null || m.status === '') {
        err('E_MISSING_STATUS', where, 'Mensagem sem "status".');
      } else if (!ALLOWED_STATUS.has(m.status)) {
        err('E_BAD_STATUS', where, `status "${m.status}" deve ser confirmed | pending-review.`);
      }
      if (m.added_in == null || String(m.added_in).trim() === '') {
        err('E_MISSING_ADDED_IN', where, 'Mensagem sem "added_in" (hash curto do commit de inserção).');
      }
      if (typeof m.content !== 'string') {
        err('E_BAD_CONTENT', where, '"content" deve ser string (pode ser vazia em mídia).');
      }

      // reply_to
      if (m.reply_to != null && !ids.has(m.reply_to)) {
        err('E_BAD_REPLY_TO', where, `reply_to "${m.reply_to}" não existe nesta thread.`);
      }

      // mídia
      if (m.media && typeof m.media.url === 'string' && m.media.url) {
        const relUrl = m.media.url.replace(/^\/+/, '');
        if (relUrl.startsWith('public/media/')) {
          if (!fs.existsSync(path.join(rootDir, relUrl))) {
            err('E_MISSING_MEDIA_FILE', where, `media.url "${m.media.url}" não existe no repositório.`);
          }
        } else if (!/^https?:\/\//.test(relUrl)) {
          warn('E_MISSING_MEDIA_FILE', where, `media.url "${m.media.url}" fora de /public/media e sem http(s) — não verificada.`);
        }
      }
    }
  }

  /* ---------- índice x arquivos ---------- */
  if (fs.existsSync(indexFile)) {
    for (const id of fileIds) {
      if (!indexIds.has(id)) {
        err('E_INDEX_MISMATCH', 'data/threads.json', `Thread "${id}" existe em data/threads/ mas falta no índice.`);
      }
    }
    for (const id of indexIds) {
      if (!fileIds.has(id)) {
        err('E_INDEX_MISMATCH', 'data/threads.json', `Índice lista "${id}", mas data/threads/${id}.json não existe.`);
      }
    }
    // contagens desatualizadas são apenas warning
    try {
      const index = JSON.parse(fs.readFileSync(indexFile, 'utf8'));
      for (const entry of index) {
        if (!entry?.id) continue;
        const full = path.join(threadsDir, `${entry.id}.json`);
        if (!fs.existsSync(full)) continue;
        const t = JSON.parse(fs.readFileSync(full, 'utf8'));
        const confirmed = (t.messages || []).filter((m) => m?.status === 'confirmed').length;
        if (typeof entry.message_count === 'number' && entry.message_count !== confirmed) {
          warn('E_COUNT_MISMATCH', 'data/threads.json',
            `Thread "${entry.id}": message_count=${entry.message_count}, confirmadas=${confirmed}.`);
        }
      }
    } catch {
      /* já reportado acima */
    }
  }

  return { errors, warnings, stats: { threads: files.length, messages: totalMessages } };
}

/* ---------- CLI ---------- */

function main() {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const dataDir = path.resolve(process.argv[2] || path.join(scriptDir, '..', 'data'));

  if (!fs.existsSync(dataDir)) {
    console.error(`[validate] Diretório de dados não encontrado: ${dataDir}`);
    process.exit(1);
  }

  const { errors, warnings, stats } = validateData(dataDir);

  for (const w of warnings) {
    console.warn(`[warn]  ${w.code} — ${w.file}\n        ${w.message}`);
  }
  for (const e of errors) {
    console.error(`[error] ${e.code} — ${e.file}\n        ${e.message}`);
  }

  console.log(`[validate] ${stats.threads} thread(s), ${stats.messages} mensagem(ns), ` +
    `${errors.length} erro(s), ${warnings.length} warning(s).`);

  if (errors.length) {
    console.error('[validate] FALHOU — CI vermelho.');
    process.exit(1);
  }
  console.log('[validate] OK.');
}

// executa como CLI, não quando importado por testes
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (e) {
    console.error('[validate] erro inesperado:', e);
    process.exit(1);
  }
}
