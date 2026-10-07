#!/usr/bin/env node
// validate.mjs — validador dos JSONs de /data, Node puro, sem dependências.
//
// Uso:  node scripts/validate.mjs [dataDir]      (padrão: <repo>/data)
// Exit 1 se houver QUALQUER erro; warnings não derrubam o CI.
//
// PRINCÍPIO EDITORIAL CENTRAL:
//   A interface nunca deve fazer uma reconstrução editorial parecer uma
//   mensagem literal enviada por uma pessoa. O schema separa:
//     - natureza do conteúdo (content_kind: verbatim, verbatim_excerpt,
//       audio_transcript, media, call, editorial_event, system);
//     - precisão temporal (timestamp_precision: minute, date, month,
//       approximate — horário NUNCA é estimado);
//     - proveniência documental (verification.level: official_document,
//       public_investigation, secondary_source, pending_review);
//     - nota editorial (editorial_note) FORA da fala atribuída.
//
// Regras que geram ERRO (CI vermelho):
//   E_JSON_PARSE              JSON inválido
//   E_THREAD_FIELD            thread sem id/title/participants_ids/source/messages
//   E_ID_MISMATCH             thread.id difere do nome do arquivo
//   E_UNKNOWN_PARTICIPANT     participants_ids cita id fora de participants.json
//   E_DUP_PARTICIPANT         participants.json com ids duplicados
//   E_INDEX_MISMATCH          threads.json x threads/*.json fora de sincronia
//   E_MISSING_ID / E_BAD_ID / E_DUPLICATE_ID   ids de mensagem ausentes/inválidos/repetidos
//   E_MISSING_SENDER          mensagem (não-evento) sem sender_id
//   E_EVENT_SENDER            evento editorial com sender_id (evento não tem autor)
//   E_UNKNOWN_SENDER          sender_id inexistente em participants.json
//   E_BAD_DATE                date ausente/fora de YYYY-MM-DD (ou YYYY-MM p/ month)
//   E_BAD_TIME                time fora de HH:MM
//   E_BAD_PRECISION           timestamp_precision fora da lista permitida
//   E_TIME_PRECISION_MISMATCH precisão x time inconsistentes (ex.: precision=date
//                             com hora inventada; precision=minute sem hora)
//   E_TIMESTAMP_ORDER         ordem cronológica violada QUANDO determinável
//                             (mesmo dia com hora ausente em qualquer lado não compara)
//   E_MISSING_SOURCE_REF      mensagem/evento sem source_ref
//   E_MISSING_ADDED_IN        registro sem added_in
//   E_BAD_CONTENT             content não é string (mensagem) / vazio (evento)
//   E_BAD_CONTENT_KIND        content_kind fora da lista permitida
//   E_AUDIO_NEEDS_FLAGS       audio_transcript sem transcription_complete
//   E_EDITORIAL_BRACKETS      [colchetes] editoriais em content_kind verbatim/
//                             verbatim_excerpt sem literal_brackets: true
//   E_FORWARDED_ATTR          forwarded_message sem forwarded_attribution válida
//                             (name + verified_direct_contact: false)
//   E_UNKNOWN_DOCUMENT        source.document_id ausente em data/documents.json
//   E_DOCUMENT_FIELD          entrada inválida em documents.json (inclui o campo
//                             proibido official_pdf_url; cópia pública sem processo)
//   E_TRANSCRIPTION_SHAPE     transcription sem kind/complete/atribuição corretos
//   E_MEDIA_STATUS            media.status fora da lista; objeto inválido
//   E_MEDIA_OFFICIAL          official_media sem arquivo+sha256+fonte oficial,
//                             ou com publisher (URL jornalística não gera oficial)
//   E_MEDIA_SECONDARY         secondary_media sem publisher/official_media_located
//   E_MEDIA_TRANSCRIPT_ONLY   transcript_only apontando arquivo ou sem transcrição
//   E_MEDIA_REFERENCE         media_reference_only com local_file
//   E_MEDIA_LOCAL_HASH        mídia local sem sha256/bytes; derivada sem derived_from
//   E_MEDIA_ORIGINAL_FILE     original_file: true sem source_document_id
//   E_MEDIA_MISSING           audio_transcript sem objeto media
//   E_BAD_REPLY_TO            reply_to aponta para mensagem inexistente na thread
//   E_MISSING_MEDIA_FILE      media.url aponta para arquivo inexistente em /public
//   E_MISSING_VERIFICATION    sem objeto verification
//   E_BAD_VERIFICATION_LEVEL  verification.level fora da lista permitida
//   E_VERIFICATION_SHAPE      official_document sem authority/document/page ou com
//                             primary_document_located=false; nível != official_document
//                             com primary_document_located=true
//   E_VERIFICATION_SECONDARY  secondary_source sem ao menos 1 fonte secundária válida
//   E_BAD_EVENT_ID            id de evento fora do padrão e-NNNNN
//   E_BAD_EVENT_KIND          event_kind fora da lista permitida
//   E_LEGACY_FIELD            campo do schema antigo (timestamp/status/type) presente
//
// Warnings (não bloqueiam): E_COUNT_MISMATCH (contagem no índice desatualizada).

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ALLOWED_KINDS = new Set(['verbatim', 'verbatim_excerpt', 'audio_transcript', 'media', 'call', 'forwarded_message', 'editorial_event', 'system']);
const ALLOWED_LEVELS = new Set(['official_document', 'public_investigation', 'secondary_source', 'pending_review']);
const ALLOWED_PRECISIONS = new Set(['minute', 'date', 'month', 'approximate']);
const ALLOWED_EVENT_KINDS = new Set(['editorial_context', 'system']);
const ALLOWED_MEDIA_STATUS = new Set(['official_media', 'secondary_media', 'embedded_media', 'transcript_only', 'media_reference_only']);
const ALLOWED_TRANSCRIPTION_KINDS = new Set(['publisher_transcription', 'document_transcription', 'project_transcription']);
const SHA256_RE = /^[0-9a-f]{64}$/;
/** content_kinds que não são fala de pessoa ( dispensam sender_id ) */
const NO_SENDER_KINDS = new Set(['editorial_event', 'system']);
/** campos do schema antigo — sua presença é erro de regressão */
const LEGACY_FIELDS = ['timestamp', 'status', 'type'];

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const MONTH_RE = /^\d{4}-\d{2}$/;
const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;
const ID_RE = /^m-\d{5,}$/;
const EVENT_ID_RE = /^e-\d{5,}$/;

function isValidDate(date) {
  if (!DATE_RE.test(date)) return false;
  const [y, mo, d] = date.split('-').map(Number);
  const dt = new Date(Date.UTC(y, mo - 1, d));
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === d;
}

function isValidMonth(date) {
  if (!MONTH_RE.test(date)) return false;
  const [y, mo] = date.split('-').map(Number);
  return mo >= 1 && mo <= 12 && String(y).length === 4;
}

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

  /* ---------- documents.json (registro central de documentos) ---------- */
  const documentIds = new Set();
  const docsFile = path.join(dataDir, 'documents.json');
  if (fs.existsSync(docsFile)) {
    let docs;
    try {
      docs = JSON.parse(fs.readFileSync(docsFile, 'utf8'));
    } catch (e) {
      err('E_JSON_PARSE', 'data/documents.json', `JSON inválido: ${e.message}`);
      docs = [];
    }
    if (!Array.isArray(docs)) {
      err('E_DOCUMENT_FIELD', 'data/documents.json', 'documents.json deve ser um array.');
      docs = [];
    }
    for (const d of docs) {
      if (!d || typeof d.id !== 'string' || !d.id || typeof d.title !== 'string' || !d.title ||
          typeof d.authority !== 'string' || !d.authority) {
        err('E_DOCUMENT_FIELD', 'data/documents.json', 'Documento sem id/title/authority válidos.');
        continue;
      }
      if (documentIds.has(d.id)) {
        err('E_DOCUMENT_FIELD', 'data/documents.json', `id de documento duplicado: "${d.id}"`);
      }
      documentIds.add(d.id);
      // cópia pública de reprodução jornalística NUNCA é registrada como oficial
      if ('official_pdf_url' in d) {
        err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}" usa o campo proibido "official_pdf_url" — use public_copy_url + copy_kind.`);
      }
      if (d.public_copy_url && d.copy_kind !== 'public_reproduction' && d.copy_kind !== 'official_original') {
        err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}" com public_copy_url exige copy_kind (public_reproduction | official_original).`);
      }
      if (d.copy_kind === 'public_reproduction' && !d.official_process_url) {
        err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}" é reprodução pública e exige official_process_url (o processo que comprova a origem).`);
      }
      if (d.sha256 != null && !SHA256_RE.test(d.sha256)) {
        err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}" com sha256 inválido (64 hex minúsculos).`);
      }
      // cópia hospedada pelo projeto: sempre caminho relativo em public/docs/
      // (mesma origem), arquivo presente no repositório e hash igual ao declarado
      if (d.hosted_copy_url != null) {
        const rel = String(d.hosted_copy_url).replace(/^\/+/, '');
        if (!rel.startsWith('public/docs/') || /^https?:\/\//.test(d.hosted_copy_url)) {
          err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}": hosted_copy_url deve ser caminho relativo em public/docs/ (nunca URL externa — para origem use public_copy_url).`);
        } else {
          const full = path.join(rootDir, rel);
          if (!fs.existsSync(full)) {
            err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}": hosted_copy_url "${rel}" não existe no repositório.`);
          } else if (d.sha256) {
            const h = fs.readFileSync(full);
            const actual = crypto.createHash('sha256').update(h).digest('hex');
            if (actual !== d.sha256) {
              err('E_DOCUMENT_FIELD', 'data/documents.json', `Documento "${d.id}": hosted_copy_url diverge do sha256 declarado (arquivo: ${actual}).`);
            }
          }
        }
      }
    }
  }

  /* ---------- participants.json ---------- */
  let participants;
  const pFile = path.join(dataDir, 'participants.json');
  try {
    participants = JSON.parse(fs.readFileSync(pFile, 'utf8'));
  } catch (e) {
    err('E_JSON_PARSE', 'data/participants.json', `JSON inválido: ${e.message}`);
    return { errors, warnings, stats: { threads: 0, messages: 0, events: 0, byLevel: {} } };
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
    return { errors, warnings, stats: { threads: 0, messages: 0, events: 0, byLevel: {} } };
  }

  const files = fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort();
  const fileIds = new Set();
  let totalMessages = 0;
  let totalEvents = 0;
  const byLevel = {};

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
    let prevMsg = null; // { date, time, precision } do registro anterior
    totalMessages += thread.messages.length;

    for (let i = 0; i < thread.messages.length; i++) {
      const m = thread.messages[i];
      const where = `${rel} · messages[${i}]`;
      if (!m || typeof m !== 'object') {
        err('E_THREAD_FIELD', where, 'Elemento não é um objeto.');
        continue;
      }

      // campos do schema antigo são erro de regressão
      for (const legacy of LEGACY_FIELDS) {
        if (legacy in m) {
          err('E_LEGACY_FIELD', where, `campo legado "${legacy}" presente — use o novo schema (date/time/timestamp_precision, content_kind, verification).`);
        }
      }

      // id
      if (m.id == null || m.id === '') {
        err('E_MISSING_ID', where, 'Mensagem sem "id".');
      } else if (!ID_RE.test(m.id)) {
        err('E_BAD_ID', where, `id "${m.id}" fora do padrão m-NNNNN.`);
      }

      // duplicidade (Set local por thread)
      if (m.id && seenIds.has(m.id)) {
        err('E_DUPLICATE_ID', where, `id de mensagem duplicado: "${m.id}"`);
      }
      if (m.id) seenIds.add(m.id);

      // content_kind
      if (m.content_kind == null) {
        err('E_BAD_CONTENT_KIND', where, 'Mensagem sem "content_kind".');
      } else if (!ALLOWED_KINDS.has(m.content_kind)) {
        err('E_BAD_CONTENT_KIND', where, `content_kind "${m.content_kind}" fora da lista permitida (${[...ALLOWED_KINDS].join(', ')}).`);
      }
      const kind = ALLOWED_KINDS.has(m.content_kind) ? m.content_kind : null;

      // sender: exigido em fala; proibido em evento editorial
      if (kind && NO_SENDER_KINDS.has(kind)) {
        if (m.sender_id != null) {
          err('E_EVENT_SENDER', where, `content_kind "${kind}" não pode ter sender_id — evento editorial não é fala de pessoa.`);
        }
      } else if (m.sender_id == null || m.sender_id === '') {
        err('E_MISSING_SENDER', where, 'Mensagem sem "sender_id".');
      } else if (!participantIds.has(m.sender_id)) {
        err('E_UNKNOWN_SENDER', where, `sender_id "${m.sender_id}" não existe em participants.json.`);
      }

      // data / hora / precisão
      const tCheck = checkTemporal(m, where, err);
      if (tCheck) {
        checkOrder(prevMsg, m, where, err);
        prevMsg = m;
      }

      // transcription_complete obrigatório em transcrição de áudio
      if (kind === 'audio_transcript' && typeof m.transcription_complete !== 'boolean') {
        err('E_AUDIO_NEEDS_FLAGS', where, 'content_kind "audio_transcript" exige "transcription_complete" (boolean).');
      }

      // texto editorial jamais dentro de fala literal (§1/§19): colchetes são
      // sinalizadores de inserção editorial; salvo literal_brackets explícito
      // para os casos raros em que os colchetes existem no original
      if ((kind === 'verbatim' || kind === 'verbatim_excerpt' || kind === 'forwarded_message') && !m.literal_brackets &&
          /[[\]]/.test(String(m.content ?? ''))) {
        err('E_EDITORIAL_BRACKETS', where,
          `content contém [colchetes] em content_kind "${kind}" — mova o texto editorial para editorial_note (ou declare literal_brackets: true se os colchetes constam do original).`);
      }

      // encaminhada: atribuição de terceiro NUNCA vira contato direto
      if (kind === 'forwarded_message') {
        const fa = m.forwarded_attribution;
        if (!fa || typeof fa !== 'object' || Array.isArray(fa) ||
            !(fa.name === null || typeof fa.name === 'string') ||
            fa.verified_direct_contact !== false) {
          err('E_FORWARDED_ATTR', where,
            'content_kind "forwarded_message" exige forwarded_attribution { name: string|null, verified_direct_contact: false } — atribuição não comprovada documentalmente.');
        }
      }

      // referência ao documento central (§25): o id precisa existir
      if (m.source?.document_id != null && !documentIds.has(m.source.document_id)) {
        err('E_UNKNOWN_DOCUMENT', where, `source.document_id "${m.source.document_id}" não existe em data/documents.json.`);
      }

      // transcrição: quem fez e se é completa (§12)
      if (m.transcription != null) {
        const tr = m.transcription;
        if (typeof tr !== 'object' || Array.isArray(tr) || !ALLOWED_TRANSCRIPTION_KINDS.has(tr.kind) ||
            typeof tr.complete !== 'boolean') {
          err('E_TRANSCRIPTION_SHAPE', where,
            `"transcription" exige { kind: ${[...ALLOWED_TRANSCRIPTION_KINDS].join('|')}, complete: boolean }.`);
        } else if (tr.kind === 'publisher_transcription' && (typeof tr.source !== 'string' || !tr.source)) {
          err('E_TRANSCRIPTION_SHAPE', where, 'transcription.kind "publisher_transcription" exige "source" (veículo).');
        } else if (tr.kind === 'document_transcription' && (typeof tr.document !== 'string' || !tr.document)) {
          err('E_TRANSCRIPTION_SHAPE', where, 'transcription.kind "document_transcription" exige "document".');
        }
      }

      // mídia: cadeia de proveniência (§28-§35)
      checkMedia(m, where, err);

      // campos obrigatórios de rastreabilidade
      if (m.source_ref == null || String(m.source_ref).trim() === '') {
        err('E_MISSING_SOURCE_REF', where, 'Mensagem sem "source_ref".');
      }
      if (m.added_in == null || String(m.added_in).trim() === '') {
        err('E_MISSING_ADDED_IN', where, 'Mensagem sem "added_in" (hash curto do commit de inserção).');
      }
      if (typeof m.content !== 'string') {
        err('E_BAD_CONTENT', where, '"content" deve ser string (pode ser vazia em mídia).');
      }
      if (m.editorial_note != null && typeof m.editorial_note !== 'string') {
        err('E_BAD_CONTENT', where, '"editorial_note" deve ser string ou null.');
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

      // proveniência
      checkVerification(m, where, err, { isMessage: true });
      if (m.verification && ALLOWED_LEVELS.has(m.verification.level)) {
        byLevel[m.verification.level] = (byLevel[m.verification.level] || 0) + 1;
      }
    }

    /* ---------- timeline_events ---------- */
    if (thread.timeline_events != null) {
      if (!Array.isArray(thread.timeline_events)) {
        err('E_THREAD_FIELD', rel, '"timeline_events" deve ser um array.');
      } else {
        let prevEvt = null;
        const seenEventIds = new Set();
        totalEvents += thread.timeline_events.length;
        for (let i = 0; i < thread.timeline_events.length; i++) {
          const ev = thread.timeline_events[i];
          const where = `${rel} · timeline_events[${i}]`;
          if (!ev || typeof ev !== 'object') {
            err('E_THREAD_FIELD', where, 'Elemento não é um objeto.');
            continue;
          }
          for (const legacy of LEGACY_FIELDS) {
            if (legacy in ev) {
              err('E_LEGACY_FIELD', where, `campo legado "${legacy}" presente.`);
            }
          }
          if (ev.id == null || ev.id === '') {
            err('E_BAD_EVENT_ID', where, 'Evento sem "id".');
          } else if (!EVENT_ID_RE.test(ev.id)) {
            err('E_BAD_EVENT_ID', where, `id "${ev.id}" fora do padrão e-NNNNN.`);
          } else if (seenEventIds.has(ev.id)) {
            err('E_DUPLICATE_ID', where, `id de evento duplicado: "${ev.id}"`);
          } else {
            seenEventIds.add(ev.id);
          }
          if (ev.sender_id != null) {
            err('E_EVENT_SENDER', where, 'Evento editorial não pode ter sender_id — nunca é renderizado como mensagem de alguém.');
          }
          if (ev.event_kind != null && !ALLOWED_EVENT_KINDS.has(ev.event_kind)) {
            err('E_BAD_EVENT_KIND', where, `event_kind "${ev.event_kind}" fora da lista permitida (${[...ALLOWED_EVENT_KINDS].join(', ')}).`);
          }
          if (typeof ev.content !== 'string' || !ev.content.trim()) {
            err('E_BAD_CONTENT', where, 'Evento editorial exige "content" não vazio.');
          }
          if (ev.source_ref == null || String(ev.source_ref).trim() === '') {
            err('E_MISSING_SOURCE_REF', where, 'Evento editorial sem "source_ref".');
          }
          if (ev.source?.document_id != null && !documentIds.has(ev.source.document_id)) {
            err('E_UNKNOWN_DOCUMENT', where, `source.document_id "${ev.source.document_id}" não existe em data/documents.json.`);
          }
          if (ev.added_in == null || String(ev.added_in).trim() === '') {
            err('E_MISSING_ADDED_IN', where, 'Evento editorial sem "added_in".');
          }
          const tCheck = checkTemporal(ev, where, err);
          if (tCheck) {
            checkOrder(prevEvt, ev, where, err);
            prevEvt = ev;
          }
          checkVerification(ev, where, err, { isMessage: false });
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
        const count = (t.messages || []).length;
        if (typeof entry.message_count === 'number' && entry.message_count !== count) {
          warn('E_COUNT_MISMATCH', 'data/threads.json',
            `Thread "${entry.id}": message_count=${entry.message_count}, mensagens=${count}.`);
        }
      }
    } catch {
      /* já reportado acima */
    }
  }

  return {
    errors,
    warnings,
    stats: { threads: files.length, messages: totalMessages, events: totalEvents, byLevel },
  };
}

/* ---------- data / hora / precisão ---------- */

function checkTemporal(m, where, err) {
  const precision = m.timestamp_precision;
  // timestamp integralmente não divulgado: data/hora/precisão todas null
  // ("na dúvida, null" — § horários nunca são estimados). Exige coerência:
  // qualquer campo presente ativa a checagem completa.
  if (precision == null && m.date == null && m.time == null) {
    if ('timestamp_precision' in m || 'time' in m) {
      err('E_BAD_PRECISION', where, 'timestamp sem data divulgada deve omitir precision/time (todos null).');
      return false;
    }
    return true;
  }
  if (precision == null || !ALLOWED_PRECISIONS.has(precision)) {
    err('E_BAD_PRECISION', where, `timestamp_precision "${precision}" inválida (use ${[...ALLOWED_PRECISIONS].join(', ')}).`);
    return false;
  }
  const date = m.date;
  if (typeof date !== 'string' || !(precision === 'month' ? isValidMonth(date) : isValidDate(date))) {
    err('E_BAD_DATE', where, `date "${date}" inválida para precision "${precision}" (esperado ${precision === 'month' ? 'YYYY-MM' : 'YYYY-MM-DD'}).`);
    return false;
  }
  const time = m.time;
  if (time != null && (typeof time !== 'string' || !TIME_RE.test(time))) {
    err('E_BAD_TIME', where, `time "${time}" fora do formato HH:MM.`);
    return false;
  }
  if (precision === 'minute' && time == null) {
    err('E_TIME_PRECISION_MISMATCH', where, 'timestamp_precision "minute" exige time HH:MM não nulo.');
    return false;
  }
  if (precision !== 'minute' && time != null) {
    // horário nunca é estimado: precisão menor que minuto proíbe hora
    err('E_TIME_PRECISION_MISMATCH', where, `timestamp_precision "${precision}" exige time null — horário não divulgado não pode ser inventado.`);
    return false;
  }
  return true;
}

/**
 * Ordem cronológica só é exigida quando determinável:
 * datas diferentes bastam; mesmo dia só compara se AMBOS têm hora.
 * Precisões month/approximate não participam da comparação.
 */
function checkOrder(prev, cur, where, err) {
  if (!prev) return;
  const ordered = (x) => x.timestamp_precision === 'minute' || x.timestamp_precision === 'date';
  if (!ordered(prev) || !ordered(cur)) return;
  if (prev.date !== cur.date) {
    if (cur.date < prev.date) {
      err('E_TIMESTAMP_ORDER', where, `date ${cur.date} anterior à do registro anterior (${prev.date}).`);
    }
    return;
  }
  if (prev.time != null && cur.time != null && cur.time < prev.time) {
    err('E_TIMESTAMP_ORDER', where, `time ${cur.time} anterior ao do registro anterior no mesmo dia (${prev.time}).`);
  }
}

/* ---------- mídia: cadeia de proveniência (§6-§8, §28-§35) ---------- */

function checkMedia(m, where, err) {
  const media = m.media;
  if (!media) {
    // transcrição de áudio exige registro de mídia (id ou justificativa transcript_only)
    if (m.content_kind === 'audio_transcript') {
      err('E_MEDIA_MISSING', where, 'content_kind "audio_transcript" exige objeto "media" (com id, ou status transcript_only como justificativa) — a transcrição nunca substitui o registro do áudio.');
    }
    return;
  }
  if (typeof media !== 'object' || Array.isArray(media)) {
    err('E_MEDIA_STATUS', where, '"media" deve ser um objeto.');
    return;
  }
  if (!ALLOWED_MEDIA_STATUS.has(media.status)) {
    err('E_MEDIA_STATUS', where, `media.status "${media.status}" inválido (${[...ALLOWED_MEDIA_STATUS].join(', ')}).`);
    return;
  }

  // mídia local exige hash/bytes (§33); derivada exige origem (§34)
  if (media.local_file) {
    if (!SHA256_RE.test(String(media.sha256 || ''))) {
      err('E_MEDIA_LOCAL_HASH', where, 'media.local_file exige media.sha256 (SHA-256 calculado localmente).');
    }
    if (typeof media.bytes !== 'number' || media.bytes < 1) {
      err('E_MEDIA_LOCAL_HASH', where, 'media.local_file exige media.bytes.');
    }
    if (String(media.local_file).includes('/derived/') && media.derived_from == null) {
      err('E_MEDIA_DERIVED', where, 'mídia derivada (local_file em /derived/) exige "derived_from" com o id do original.');
    }
  }

  switch (media.status) {
    case 'official_media':
      // somente com arquivo dos autos públicos / pacote oficial / URL institucional
      if (!media.local_file || !SHA256_RE.test(String(media.sha256 || ''))) {
        err('E_MEDIA_OFFICIAL', where, 'media.status "official_media" exige arquivo local + sha256 (evidência baixada de origem pública oficial).');
      }
      if (!(media.source_document_id || (media.source_authority && media.source_process))) {
        err('E_MEDIA_OFFICIAL', where, 'media.status "official_media" exige fonte oficial (source_document_id ou source_authority + source_process).');
      }
      if (media.publisher) {
        // URL/veículo jornalístico jamais gera official_media (§7/§35.9)
        err('E_MEDIA_OFFICIAL', where, 'media.status "official_media" não pode ter "publisher" — origem jornalística é secondary_media.');
      }
      break;
    case 'secondary_media':
      if (typeof media.publisher !== 'string' || !media.publisher.trim()) {
        err('E_MEDIA_SECONDARY', where, 'media.status "secondary_media" exige "publisher" (veículo que publicou o arquivo).');
      }
      if (media.official_media_located !== false) {
        err('E_MEDIA_SECONDARY', where, 'media.status "secondary_media" exige official_media_located: false.');
      }
      break;
    case 'transcript_only':
      // só há transcrição: jamais aponta arquivo (§35.4) nem apaga o texto (§35.10)
      if (media.local_file || media.external_url) {
        err('E_MEDIA_TRANSCRIPT_ONLY', where, 'media.status "transcript_only" não pode ter local_file/external_url — existe apenas a transcrição.');
      }
      if (typeof m.content !== 'string' || !m.content.trim()) {
        err('E_MEDIA_TRANSCRIPT_ONLY', where, 'media.status "transcript_only" exige transcrição em content — ausência de mídia nunca apaga a transcrição.');
      }
      break;
    case 'media_reference_only':
      if (media.local_file) {
        err('E_MEDIA_REFERENCE', where, 'media.status "media_reference_only" não pode ter local_file — o arquivo não foi obtido; referencie a página/figura.');
      }
      break;
    default:
      break;
  }

  if (media.original_file === true && media.source_document_id == null) {
    // original_file=true exige evidência documental (§31/§35.5)
    err('E_MEDIA_ORIGINAL_FILE', where, 'media.original_file: true exige source_document_id — arquivo só é "original" quando identificável nos autos.');
  }
  if (media.duration_seconds != null && typeof media.duration_seconds !== 'number') {
    err('E_MEDIA_STATUS', where, 'media.duration_seconds deve ser número ou null.');
  }
}

/* ---------- verification / sources ---------- */

function checkVerification(m, where, err, { isMessage }) {
  const v = m.verification;
  if (v == null || typeof v !== 'object' || Array.isArray(v)) {
    err('E_MISSING_VERIFICATION', where, 'Registro sem objeto "verification".');
    return;
  }
  if (!ALLOWED_LEVELS.has(v.level)) {
    err('E_BAD_VERIFICATION_LEVEL', where, `verification.level "${v.level}" fora da lista permitida (${[...ALLOWED_LEVELS].join(', ')}).`);
    return;
  }
  if (typeof v.primary_document_located !== 'boolean') {
    err('E_VERIFICATION_SHAPE', where, 'verification.primary_document_located deve ser boolean.');
  }

  if (v.level === 'official_document') {
    // mensagem localizada no documento primário exige referência documental mínima
    if (!v.authority || typeof v.authority !== 'string') {
      err('E_VERIFICATION_SHAPE', where, 'verification.level "official_document" exige "authority".');
    }
    if (!v.document || typeof v.document !== 'string') {
      err('E_VERIFICATION_SHAPE', where, 'verification.level "official_document" exige "document".');
    }
    if (typeof v.page !== 'number' || !Number.isInteger(v.page) || v.page < 1) {
      err('E_VERIFICATION_SHAPE', where, 'verification.level "official_document" exige "page" (número inteiro ≥ 1) — nunca inferida.');
    }
    if (v.primary_document_located !== true) {
      err('E_VERIFICATION_SHAPE', where, 'verification.level "official_document" exige primary_document_located = true.');
    }
    if (isMessage) {
      const primary = m.sources?.primary;
      if (!primary || typeof primary !== 'object' || typeof primary.document !== 'string' || !primary.document ||
          typeof primary.page !== 'number') {
        err('E_VERIFICATION_SHAPE', where, 'verification.level "official_document" exige sources.primary com document e page.');
      }
    }
  } else if (v.primary_document_located === true) {
    err('E_VERIFICATION_SHAPE', where, `verification.level "${v.level}" não pode ter primary_document_located = true.`);
  }

  if (isMessage && v.level === 'secondary_source') {
    const secondary = m.sources?.secondary;
    const ok = Array.isArray(secondary) && secondary.length > 0 &&
      secondary.every((s) => s && typeof s.publication === 'string' && s.publication.trim() !== '');
    if (!ok) {
      err('E_VERIFICATION_SECONDARY', where, 'verification.level "secondary_source" exige ao menos uma fonte em sources.secondary (publication obrigatória).');
    }
  }
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

  const levels = Object.entries(stats.byLevel).map(([k, n]) => `${k}=${n}`).join(', ');
  console.log(`[validate] ${stats.threads} thread(s), ${stats.messages} mensagem(ns), ${stats.events} evento(s) editoriais${levels ? ` · ${levels}` : ''}`);
  console.log(`[validate] ${errors.length} erro(s), ${warnings.length} warning(s).`);

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
