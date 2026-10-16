// build-whatsnew.mjs — mapa de inclusões recentes por conversa
// Gera data/whatsnew.json: por thread, quantos registros (mensagens + eventos
// públicos) entraram no acervo em cada data de lote (sufixo YYYYMMDD do campo
// added_in) e qual é o lote mais recente do acervo (latest_batch).
// O selo "novo" acende APENAS nos registros do último lote inserido — definicao
// editorial: "novo" = a última rodada de inclusão, não uma janela de dias.
// Quando entrar uma rodada nova, o selo migra para ela sozinho, sem rebuild.
// CI: node scripts/build-whatsnew.mjs && git diff --exit-code data/whatsnew.json

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const threadsDir = path.join(rootDir, 'data', 'threads');
const outFile = path.join(rootDir, 'data', 'whatsnew.json');

const isPublic = (r) => r?.verification?.level !== 'pending_review';
const batchDate = (r) => (/\d{8}$/.exec(String(r?.added_in || '')) || [''])[0];

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
    const d = batchDate(r);
    if (!d) continue;
    buckets[d] = (buckets[d] || 0) + 1;
  }
  if (Object.keys(buckets).length) threads[t.id] = buckets;
}

const batches = Object.values(threads).flatMap((b) => Object.keys(b)).sort();
const payload = {
  generated_at: new Date().toISOString().slice(0, 10),
  latest_batch: batches.at(-1) || null,
  note: 'Inclusões por data de lote (added_in) por conversa; latest_batch é o lote mais recente do acervo. O selo "novo" acende apenas nos registros do latest_batch. pending_review excluído.',
  threads,
};
fs.writeFileSync(outFile, JSON.stringify(payload, null, 1) + '\n', 'utf8');
const total = Object.values(threads).reduce((s, b) => s + Object.values(b).reduce((x, y) => x + y, 0), 0);
console.log(`[whatsnew] ${Object.keys(threads).length} conversas, ${total} inclusões datadas -> data/whatsnew.json`);
