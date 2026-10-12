// build-search-index.mjs — índice de busca plena (mensagens + eventos públicos)
// Gera data/search-index.json: conteúdo textual bruto por conversa, para a
// busca da lista lateral procurar dentro dos diálogos, não só nos nomes.
// Registros pending_review NUNCA entram (mesma regra da renderização pública).
// CI: node scripts/build-search-index.mjs && git diff --exit-code data/search-index.json

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const threadsDir = path.join(rootDir, 'data', 'threads');
const outFile = path.join(rootDir, 'data', 'search-index.json');

const isPublic = (r) => r?.verification?.level !== 'pending_review';

const threads = [];
let msgTotal = 0;
for (const file of fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json')).sort()) {
  let t;
  try {
    t = JSON.parse(fs.readFileSync(path.join(threadsDir, file), 'utf8'));
  } catch {
    console.error(`[search-index] JSON inválido ignorado: ${file}`);
    continue;
  }
  const msgs = [];
  for (const m of t.messages || []) {
    if (!isPublic(m) || typeof m.content !== 'string' || !m.content.trim()) continue;
    msgs.push(m.content);
  }
  for (const ev of t.timeline_events || []) {
    if (!isPublic(ev) || typeof ev.content !== 'string' || !ev.content.trim()) continue;
    msgs.push(ev.content);
  }
  msgTotal += msgs.length;
  threads.push({ id: t.id, messages: msgs });
}

const payload = {
  generated_at: new Date().toISOString().slice(0, 10),
  note: 'Conteúdo textual público (mensagens + eventos) por conversa; busca acento-insensível no cliente. pending_review excluído.',
  threads,
};
fs.writeFileSync(outFile, JSON.stringify(payload, null, 1) + '\n', 'utf8');
console.log(`[search-index] ${threads.length} conversas, ${msgTotal} textos -> data/search-index.json`);
