// build-whatsnew.mjs — mapa de inclusões recentes por conversa
// Gera data/whatsnew.json: por thread, quantos registros (mensagens + eventos
// públicos) entraram no acervo em cada data de lote (sufixo YYYYMMDD do campo
// added_in). O cliente soma os baldes dentro da janela rolante (window_days,
// padrão 7 dias) para acender o selo "novo" na bolha, no evento e na lista
// lateral — o selo apaga sozinho quando a inclusão envelhece, sem rebuild.
// A janela é curta de propósito: em acervo que cresce por rodadas, "novo" só
// discrimina se cobrir as últimas rodadas, não o acervo inteiro.
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

const payload = {
  generated_at: new Date().toISOString().slice(0, 10),
  window_days: 7,
  note: 'Inclusões por data de lote (added_in) por conversa — o cliente soma os baldes dentro da janela rolante para o selo "novo". pending_review excluído.',
  threads,
};
fs.writeFileSync(outFile, JSON.stringify(payload, null, 1) + '\n', 'utf8');
const total = Object.values(threads).reduce((s, b) => s + Object.values(b).reduce((x, y) => x + y, 0), 0);
console.log(`[whatsnew] ${Object.keys(threads).length} conversas, ${total} inclusões datadas -> data/whatsnew.json`);
