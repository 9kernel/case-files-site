#!/usr/bin/env node
// migrate-provenance.mjs — migração de schema antigo → novo + auditoria de proveniência.
//
// Uso:
//   node scripts/migrate-provenance.mjs            # converte (idempotente) + audita + escreve migration-report.json
//   node scripts/migrate-provenance.mjs --dry-run  # só mostra o que faria
//   node scripts/migrate-provenance.mjs --audit    # apenas audita o estado atual (não escreve em data/)
//
// O que a FASE DE CONVERSÃO faz (mecânico, sem decisão editorial):
//   - timestamp ISO          → { date, time, timestamp_precision }
//                              (hora "12:00" sintética → time null + precision "date";
//                               nunca gera horário; verificação humana via relatório)
//   - type                   → content_kind
//                              (text→verbatim, image/video/document→media com media.kind,
//                               audio→audio_transcript + transcription_complete:false,
//                               call→call, system→timeline_events)
//   - status                 → verification.level "pending_review"
//                              (NUNCA promove a official_document — isso exige revisão humana)
//   - adiciona               → editorial_note: null, sources {primary:null, secondary:[…]}
//                              a partir da publicação de origem da thread
//   - NÃO altera textos: content é preservado byte a byte; registros com [colchetes]
//     são apenas SINALIZADOS no relatório para separação manual.
//
// O que a FASE DE AUDITORIA produz (migration-report.json):
//   fake_time_candidates     horários 12:00 convertidos para "horário não divulgado"
//   editorial_brackets       registros com [colchetes] no content (revisão manual)
//   official_document_candidates  mensagens já classificadas official_document
//   secondary_source_only    threads cujas mensagens dependem só de reportagem
//   manual_review_required   tudo que exige decisão humana antes da publicação
//   counts                   mensagens por thread e por verification.level

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '..');
const dataDir = path.join(root, 'data');
const threadsDir = path.join(dataDir, 'threads');
const reportPath = path.join(root, 'migration-report.json');

const DRY_RUN = process.argv.includes('--dry-run');
const AUDIT_ONLY = process.argv.includes('--audit');

/** Publicações secundárias conhecidas (thread → fonte jornalística da descoberta). */
const PUBLICATIONS = [
  {
    match: /piauí/i,
    publication: 'Revista piauí',
    date: '2026-10-01',
    url: 'https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/',
  },
  {
    match: /Terra/i,
    publication: 'Terra / Poder360',
    date: '2026-10-02',
    url: 'https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html',
  },
  {
    match: /Correio Braziliense/i,
    publication: 'Correio Braziliense / O Globo',
    date: '2026-10-03',
    url: 'https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html',
  },
  {
    match: /R7|Guaíba/i,
    publication: 'R7 (reproduzido pela Rádio Guaíba)',
    date: '2026-09-01',
    url: 'https://guaiba.com.br/politica/mendonca-tira-sigilo-e-pf-revela-pedidos-de-vorcaro-a-moraes',
  },
];

const SYNTHETIC_TIME = '12:00'; // convenção do schema antigo para "hora não divulgada"

function publicationFor(thread) {
  const hay = `${thread.source?.document || ''} ${thread.source?.url || ''}`;
  return PUBLICATIONS.find((p) => p.match.test(hay)) || null;
}

function verificationPending() {
  return {
    level: 'pending_review',
    origin: 'PF extraction',
    authority: null,
    court: null,
    case: null,
    document: null,
    page: null,
    figure: null,
    official_url: null,
    primary_document_located: false,
    verified_at: null,
  };
}

/** timestamp ISO antigo → { date, time, timestamp_precision } sem inventar hora. */
function splitTimestamp(timestamp) {
  const m = /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})/.exec(String(timestamp || ''));
  if (!m) return { date: null, time: null, timestamp_precision: 'date' };
  const [, date, hh, mm] = m;
  const time = `${hh}:${mm}`;
  if (time === SYNTHETIC_TIME) {
    // 12:00 era a aproximação do schema antigo: descarta, horário não divulgado
    return { date, time: null, timestamp_precision: 'date' };
  }
  return { date, time, timestamp_precision: 'minute' };
}

function kindForType(type) {
  switch (type) {
    case 'text': return 'verbatim';
    case 'image':
    case 'video':
    case 'document': return 'media';
    case 'audio': return 'audio_transcript';
    case 'call': return 'call';
    case 'system': return 'editorial_event';
    default: return 'verbatim';
  }
}

function orderMessage(m) {
  const out = {
    id: m.id,
    date: m.date,
    time: m.time,
    timestamp_precision: m.timestamp_precision,
  };
  if (m.sender_id != null) out.sender_id = m.sender_id;
  out.content_kind = m.content_kind;
  out.content = m.content;
  out.editorial_note = m.editorial_note ?? null;
  if (m.transcription_complete !== undefined) out.transcription_complete = m.transcription_complete;
  if (m.literal_brackets !== undefined) out.literal_brackets = m.literal_brackets;
  if (m.media) out.media = m.media;
  if (m.call_info) out.call_info = m.call_info;
  if (m.reply_to != null) out.reply_to = m.reply_to;
  out.verification = m.verification;
  out.sources = m.sources;
  out.source_ref = m.source_ref;
  out.added_in = m.added_in;
  return out;
}

function isOldSchema(thread) {
  return (thread.messages || []).some((m) => m && ('timestamp' in m || 'status' in m || 'type' in m));
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

/* ---------- conversão ---------- */

function convertThread(thread, report) {
  const publication = publicationFor(thread);
  const secondary = publication
    ? [{ publication: publication.publication, date: publication.date, url: publication.url }]
    : [];
  const events = Array.isArray(thread.timeline_events) ? [...thread.timeline_events] : [];
  const messages = [];
  let eventSeq = events.length;

  for (const m of thread.messages || []) {
    if (!m) continue;
    if (!('timestamp' in m || 'status' in m || 'type' in m)) {
      // já em schema novo (re-execução): mantém como está
      messages.push(m);
      continue;
    }
    const { date, time, timestamp_precision } = splitTimestamp(m.timestamp);
    if (time === null && /T12:00/.test(String(m.timestamp))) {
      report.fake_time_candidates.push({
        thread: thread.id, id: m.id, was: m.timestamp,
        action: '12:00 sintético descartado — horário não divulgado',
      });
    }
    const kind = kindForType(m.type);

    if (kind === 'editorial_event') {
      // system do schema antigo vira evento editorial: nunca mais bolha de mensagem
      eventSeq += 1;
      events.push({
        id: `e-${String(eventSeq).padStart(5, '0')}`,
        date,
        time,
        timestamp_precision,
        content: m.content,
        event_kind: 'editorial_context',
        verification: verificationPending(),
        source_ref: m.source_ref,
        added_in: m.added_in,
      });
      report.manual_review_required.push({
        thread: thread.id, id: m.id,
        reason: `convertido de system para timeline_event (${thread.id}); revisar conteúdo e data`,
      });
      continue;
    }

    const converted = {
      id: m.id,
      date,
      time,
      timestamp_precision,
      sender_id: m.sender_id,
      content_kind: kind,
      content: m.content,
      editorial_note: null,
      ...(kind === 'audio_transcript' ? { transcription_complete: false } : {}),
      ...(m.media ? { media: m.type && ['image', 'video', 'document'].includes(m.type) ? { kind: m.type, ...m.media } : m.media } : {}),
      ...(m.call_info ? { call_info: m.call_info } : {}),
      ...(m.reply_to != null ? { reply_to: m.reply_to } : {}),
      verification: verificationPending(),
      sources: { primary: null, secondary },
      source_ref: m.source_ref,
      added_in: m.added_in,
    };
    messages.push(orderMessage(converted));
  }

  return { ...thread, messages, timeline_events: events.length ? events : undefined };
}

/* ---------- auditoria ---------- */

function audit(thread, report) {
  const levels = {};
  const bracketsOf = (content) => {
    const s = String(content || '');
    const i = s.search(/[[\]]/);
    return i === -1 ? null : s.slice(Math.max(0, i - 30), Math.min(s.length, i + 50));
  };

  for (const m of thread.messages || []) {
    const level = m?.verification?.level || '(sem nível)';
    levels[level] = (levels[level] || 0) + 1;
    if (level === 'official_document') {
      report.official_document_candidates.push({
        thread: thread.id, id: m.id,
        document: m.verification.document, page: m.verification.page,
      });
    }
    const excerpt = bracketsOf(m.content);
    if (excerpt != null && !m.literal_brackets) {
      // colchetes de completição em transcrição de áudio parcial são legítimos
      // (inerentes ao gênero); nos demais kinds exigem revisão editorial
      if (m.content_kind === 'audio_transcript') {
        report.audio_brackets_kept.push({ thread: thread.id, id: m.id, excerpt: `…${excerpt}…` });
      } else {
        report.editorial_brackets.push({ thread: thread.id, id: m.id, excerpt: `…${excerpt}…` });
      }
    }
    if (level === 'pending_review') {
      report.manual_review_required.push({
        thread: thread.id, id: m.id, reason: 'verification.level = pending_review',
      });
    }
  }
  for (const ev of thread.timeline_events || []) {
    const excerpt = bracketsOf(ev.content);
    if (excerpt != null) {
      report.editorial_brackets.push({ thread: thread.id, id: ev.id, excerpt: `…${excerpt}…` });
    }
  }

  const msgs = thread.messages || [];
  const allSecondary = msgs.length > 0 && msgs.every((m) => m?.verification?.level === 'secondary_source');
  if (allSecondary) report.secondary_source_only.push(thread.id);

  return levels;
}

/* ---------- índice (threads.json) ---------- */

function updateIndex(report) {
  const indexPath = path.join(dataDir, 'threads.json');
  if (!fs.existsSync(indexPath)) return;
  const index = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
  for (const entry of index) {
    const file = path.join(threadsDir, `${entry.id}.json`);
    if (!fs.existsSync(file)) continue;
    const thread = JSON.parse(fs.readFileSync(file, 'utf8'));
    const msgs = thread.messages || [];
    entry.message_count = msgs.length;
    const last = msgs[msgs.length - 1];
    // campo antigo last_message_at (ISO) → last_message_date (YYYY-MM-DD; hora só se divulgada)
    if (last) {
      entry.last_message_date = last.date;
      delete entry.last_message_at;
    }
    if (entry.last_message_preview && /[[\]]/.test(entry.last_message_preview)) {
      report.manual_review_required.push({
        thread: entry.id, id: '(índice)',
        reason: 'last_message_preview contém [colchetes] editoriais',
      });
    }
  }
  if (!DRY_RUN && !AUDIT_ONLY) writeJson(indexPath, index);
}

/* ---------- main ---------- */

function main() {
  const report = {
    generated_at: new Date().toISOString().slice(0, 10),
    fake_time_candidates: [],
    editorial_brackets: [],
    audio_brackets_kept: [],
    official_document_candidates: [],
    secondary_source_only: [],
    manual_review_required: [],
    counts: { byThread: {} },
  };

  const files = fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort();
  for (const file of files) {
    const full = path.join(threadsDir, file);
    const thread = JSON.parse(fs.readFileSync(full, 'utf8'));
    let current = thread;

    if (!AUDIT_ONLY && isOldSchema(thread)) {
      const converted = convertThread(thread, report);
      if (!DRY_RUN) writeJson(full, converted);
      current = converted;
      console.log(`[migrate] ${file}: convertido para o schema de proveniência`);
    }
    report.counts.byThread[current.id] = {
      messages: (current.messages || []).length,
      events: (current.timeline_events || []).length,
      byLevel: audit(current, report),
    };
  }

  updateIndex(report);

  if (!DRY_RUN) {
    writeJson(reportPath, report);
    console.log(`[migrate] relatório: ${path.relative(root, reportPath)}`);
  }

  const nPending = report.manual_review_required.length;
  const nBrackets = report.editorial_brackets.length;
  const nTimes = report.fake_time_candidates.length;
  console.log(`[migrate] horários sintéticos: ${nTimes} · colchetes editoriais: ${nBrackets} · revisão manual: ${nPending}`);
  if (DRY_RUN) console.log('[migrate] dry-run: nada foi escrito.');
}

main();
