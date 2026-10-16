// build-whatsnew.mjs — mapa de inclusões recentes por conversa
// Gera data/whatsnew.json: por thread, quantos registros (mensagens + eventos
// públicos) entraram no acervo em cada LOTE (rótulo added_in integral — a data
// sozinha não distingue rodadas do mesmo dia) e quais são os lotes correntes.
// O selo "novo" acende APENAS nos registros dos lotes correntes — "adicionadas
// por último" = a última rodada de inclusão, declarada abaixo.
// A cada rodada nova: atualize CURRENT_BATCHES com o(s) rótulo(s) usados no
// campo added_in dessa rodada e comite o artefato regenerado (CI confere).
// CI: node scripts/build-whatsnew.mjs && git diff --exit-code data/whatsnew.json

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const threadsDir = path.join(rootDir, 'data', 'threads');
const outFile = path.join(rootDir, 'data', 'whatsnew.json');

// lotes correntes (rótulos added_in da ÚLTIMA rodada de inclusão)
const CURRENT_BATCHES = ['audit-fix2-20261016'];

const isPublic = (r) => r?.verification?.level !== 'pending_review';
const batchLabel = (r) => (/\d{8}$/.test(String(r?.added_in || '')) ? r.added_in : null);

const threads = {};
for (const file of fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort()) {
  let t;
  try {
    t = JSON.parse(fs.readFileSync(path.join(threadsDir, file), 'utf8'));
  } catch {
    console.error(`[whatsnew] JSON inválido ignorado: ${file}`);
    continue;
  }
  const buckets = {};
  for (const r of [...(t.messages || []), ...(t.timeline_events || [])]) {
    if (!isPublic(r)) continue;
    const label = batchLabel(r);
    if (!label) continue;
    buckets[label] = (buckets[label] || 0) + 1;
  }
  if (Object.keys(buckets).length) threads[t.id] = buckets;
}

const payload = {
  generated_at: new Date().toISOString().slice(0, 10),
  current_batches: CURRENT_BATCHES,
  note: 'Inclusões por lote (added_in integral) por conversa; current_batches declara a última rodada de inclusão. O selo "novo" acende apenas nos registros desses lotes. pending_review excluído.',
  threads,
};
fs.writeFileSync(outFile, JSON.stringify(payload, null, 1) + '\n', 'utf8');
const flagged = Object.values(threads)
  .reduce((s, b) => s + CURRENT_BATCHES.reduce((x, l) => x + (b[l] || 0), 0), 0);
console.log(`[whatsnew] ${Object.keys(threads).length} conversas; selo 'novo' em ${flagged} registros dos lotes correntes -> data/whatsnew.json`);
