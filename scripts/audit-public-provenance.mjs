#!/usr/bin/env node
// audit-public-provenance.mjs — auditoria de publicidade/proveniência de TODAS as
// mensagens e eventos públicos (missão §13).
//
// Uso:  node scripts/audit-public-provenance.mjs [dataDir] [rootDir]
// Gera: data/audit/public-provenance-audit.json  (legível por máquina)
//       PUBLIC-PROVENANCE-AUDIT.md               (relatório legível)
//
// Categorias por registro:
//   OK_OFFICIAL               official_document → documento existe, com
//                             public_access_verified=true e página citada
//   OK_PUBLIC_INVESTIGATION   public_investigation (processo público, peça
//                             específica não localizada — nunca official_document)
//   OK_SECONDARY              secondary_source com fonte jornalística registrada
//   INVALID_OFFICIAL_DOCUMENT official_document apontando a peça com
//                             public_access_verified=false
//   MISSING_DOCUMENT          document_id inexistente em documents.json
//   MISSING_PAGE              official_document sem page (página obrigatória)
//   PUBLIC_ACCESS_UNKNOWN     official_document apontando a peça com
//                             public_access_verified=null/ausente
//   SOURCE_CONFLICT           nível de verificação em conflito com sources.*
//                             (ex.: pending_review visível, primary de outro doc)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.resolve(process.argv[2] || path.join(scriptDir, '..', 'data'));
const rootDir = path.resolve(process.argv[3] || path.join(dataDir, '..'));

const docs = JSON.parse(fs.readFileSync(path.join(dataDir, 'documents.json'), 'utf8'));
const docsById = new Map(docs.map((d) => [d.id, d]));
const threadsDir = path.join(dataDir, 'threads');
const files = fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort();

const records = [];
const byCategory = {};
const addRecord = (rec) => {
  byCategory[rec.category] = (byCategory[rec.category] || 0) + 1;
  records.push(rec);
};

function classify(level, source, sources, docExists, doc, isEvent = false, sourceRef = null) {
  const did = source?.document_id ?? null;
  const primary = sources?.primary ?? null;
  if (level === 'official_document') {
    if (did == null) return { category: 'SOURCE_CONFLICT', reason: 'official_document sem source.document_id' };
    if (!docExists) return { category: 'MISSING_DOCUMENT', reason: `document_id "${did}" ausente em documents.json` };
    if (doc.public_access_verified === false) return { category: 'INVALID_OFFICIAL_DOCUMENT', reason: `peça "${did}" com public_access_verified=false` };
    if (doc.public_access_verified !== true) return { category: 'PUBLIC_ACCESS_UNKNOWN', reason: `peça "${did}" sem public_access_verified=true` };
    if (source?.page == null) return { category: 'MISSING_PAGE', reason: 'official_document sem page (página obrigatória)' };
    if (primary && primary.document_id != null && primary.document_id !== did) {
      return { category: 'SOURCE_CONFLICT', reason: `sources.primary.document_id (${primary.document_id}) difere de source.document_id (${did})` };
    }
    return { category: 'OK_OFFICIAL', reason: null };
  }
  if (level === 'public_investigation') {
    if (primary && primary.document_id != null) {
      return { category: 'SOURCE_CONFLICT', reason: 'public_investigation não deve ter sources.primary.document_id (nível inferior a official_document)' };
    }
    return { category: 'OK_PUBLIC_INVESTIGATION', reason: null };
  }
  if (level === 'secondary_source') {
    if (isEvent) {
      // eventos editoriais citam a fonte jornalística em source_ref (não têm sources.*)
      if (sourceRef == null || String(sourceRef).trim() === '') {
        return { category: 'SOURCE_CONFLICT', reason: 'secondary_source em evento exige source_ref com a fonte jornalística' };
      }
      return { category: 'OK_SECONDARY', reason: null };
    }
    const sec = sources?.secondary;
    if (!Array.isArray(sec) || sec.length === 0 || sec.some((s) => !s?.publication)) {
      return { category: 'SOURCE_CONFLICT', reason: 'secondary_source exige sources.secondary válida (publication em cada entrada)' };
    }
    return { category: 'OK_SECONDARY', reason: null };
  }
  // pending_review nunca é visível na versão pública
  return { category: 'SOURCE_CONFLICT', reason: `nível "${level}" não deve aparecer no acervo público` };
}

for (const file of files) {
  const thread = JSON.parse(fs.readFileSync(path.join(threadsDir, file), 'utf8'));
  for (const m of thread.messages || []) {
    const did = m.source?.document_id ?? null;
    const doc = did != null ? docsById.get(did) : undefined;
    const { category, reason } = classify(
      m.verification?.level, m.source, m.sources, did != null ? doc !== undefined : false, doc,
    );
    addRecord({
      kind: 'message',
      thread: thread.id,
      message_id: m.id,
      sender_id: m.sender_id ?? null,
      content_kind: m.content_kind,
      verification_level: m.verification?.level ?? null,
      document_id: did,
      document_exists: did == null ? null : doc !== undefined,
      public_access_verified: doc ? doc.public_access_verified ?? null : null,
      page: m.source?.page ?? null,
      figure: m.source?.figure ?? null,
      case: doc?.case ?? m.verification?.case ?? null,
      primary_source: m.sources?.primary ? { type: m.sources.primary.type, document_id: m.sources.primary.document_id ?? null, url: m.sources.primary.url ?? null } : null,
      secondary_sources: (m.sources?.secondary ?? []).map((s) => s.publication ?? '(sem publication)'),
      category,
      reason,
    });
  }
  for (const ev of thread.timeline_events || []) {
    const did = ev.source?.document_id ?? null;
    const doc = did != null ? docsById.get(did) : undefined;
    const { category, reason } = classify(
      ev.verification?.level, ev.source, null, did != null ? doc !== undefined : false, doc, true, ev.source_ref,
    );
    addRecord({
      kind: 'event',
      thread: thread.id,
      message_id: ev.id,
      sender_id: null,
      content_kind: ev.event_kind ?? null,
      verification_level: ev.verification?.level ?? null,
      document_id: did,
      document_exists: did == null ? null : doc !== undefined,
      public_access_verified: doc ? doc.public_access_verified ?? null : null,
      page: ev.source?.page ?? null,
      figure: ev.source?.figure ?? null,
      case: doc?.case ?? ev.verification?.case ?? null,
      primary_source: null,
      secondary_sources: [],
      category,
      reason,
    });
  }
}

const okCount = (byCategory.OK_OFFICIAL || 0) + (byCategory.OK_PUBLIC_INVESTIGATION || 0) + (byCategory.OK_SECONDARY || 0);
const audit = {
  generated_at: new Date().toISOString().slice(0, 10),
  scope: 'todas as threads públicas de data/threads/',
  summary: {
    threads: files.length,
    records: records.length,
    ok: okCount,
    problems: records.length - okCount,
    by_category: byCategory,
  },
  documents: docs.map((d) => ({
    id: d.id,
    case: d.case,
    edoc: d.edoc ?? null,
    public_access_verified: d.public_access_verified ?? null,
    public_access_date: d.public_access_date ?? null,
    public_access_basis: d.public_access_basis ?? null,
    official_process_url: d.official_process_url ?? null,
    public_copy_url: d.public_copy_url ?? null,
    hosted_copy_url: d.hosted_copy_url ?? null,
    messages_using: records.filter((r) => r.kind === 'message' && r.document_id === d.id).length,
    events_using: records.filter((r) => r.kind === 'event' && r.document_id === d.id).length,
  })),
  records,
};

const auditDir = path.join(dataDir, 'audit');
fs.mkdirSync(auditDir, { recursive: true });
fs.writeFileSync(path.join(auditDir, 'public-provenance-audit.json'), JSON.stringify(audit, null, 1) + '\n');

/* ---------- relatório legível ---------- */
const problems = records.filter((r) => !r.category.startsWith('OK_'));
const lines = [];
lines.push('# PUBLIC-PROVENANCE-AUDIT — Auditoria de publicidade e proveniência por mensagem');
lines.push('');
lines.push(`Gerado por \`scripts/audit-public-provenance.mjs\` em **${audit.generated_at}**.`);
lines.push('Versão legível por máquina: [`data/audit/public-provenance-audit.json`](data/audit/public-provenance-audit.json).');
lines.push('');
lines.push('Regra máxima: a força da afirmação do site nunca pode ser maior que a força da');
lines.push('evidência documental. `official_document` exige peça com `public_access_verified = true`.');
lines.push('');
lines.push('## Resultado');
lines.push('');
lines.push(`- ${audit.summary.threads} threads · ${audit.summary.records} registros (${records.filter((r) => r.kind === 'message').length} mensagens + ${records.filter((r) => r.kind === 'event').length} eventos)`);
lines.push(`- **${audit.summary.ok} OK** · **${audit.summary.problems} com problema**`);
lines.push('');
lines.push('| Categoria | Registros |');
lines.push('|---|---|');
for (const cat of ['OK_OFFICIAL', 'OK_PUBLIC_INVESTIGATION', 'OK_SECONDARY', 'INVALID_OFFICIAL_DOCUMENT', 'MISSING_DOCUMENT', 'MISSING_PAGE', 'PUBLIC_ACCESS_UNKNOWN', 'SOURCE_CONFLICT']) {
  lines.push(`| ${cat} | ${byCategory[cat] || 0} |`);
}
lines.push('');
lines.push('## Documentos e publicidade');
lines.push('');
lines.push('| Documento | Processo | e-Doc/peça | Publicidade | Mensagens | Eventos |');
lines.push('|---|---|---|---|---|---|');
for (const d of audit.documents) {
  const pub = d.public_access_verified === true ? `**confirmada** (${d.public_access_date})` : d.public_access_verified === false ? 'não confirmada' : 'desconhecida (null)';
  lines.push(`| \`${d.id}\` | ${d.case ?? '—'} | ${d.edoc ?? '—'} | ${pub} | ${d.messages_using} | ${d.events_using} |`);
}
lines.push('');
if (problems.length === 0) {
  lines.push('## Registros com problema');
  lines.push('');
  lines.push('**Nenhum.** Toda mensagem `official_document` aponta para peça com publicidade');
  lines.push('confirmada; nenhum `pending_review` visível; nenhuma fonte em conflito.');
} else {
  lines.push('## Registros com problema');
  lines.push('');
  for (const r of problems) {
    lines.push(`- **${r.category}** · ${r.thread} · ${r.message_id} — ${r.reason ?? ''}`);
  }
}
lines.push('');
fs.writeFileSync(path.join(rootDir, 'PUBLIC-PROVENANCE-AUDIT.md'), lines.join('\n') + '\n');

console.log(`[audit] ${audit.summary.records} registros · OK=${audit.summary.ok} · problemas=${audit.summary.problems}`);
console.log(`[audit] categorias: ${JSON.stringify(byCategory)}`);
console.log(`[audit] escrito: data/audit/public-provenance-audit.json · PUBLIC-PROVENANCE-AUDIT.md`);
if (audit.summary.problems > 0) process.exit(1);
