#!/usr/bin/env node
// generate-fixture.mjs — gera fixture sintética para teste de estresse
// (65 mil mensagens) em data/threads/fixture-stress.json.
//
// Uso:
//   node scripts/generate-fixture.mjs                     # gera (65.000 msgs)
//   node scripts/generate-fixture.mjs --messages 10000    # outro tamanho
//   node scripts/generate-fixture.mjs --remove            # remove e limpa o índice
//
// O arquivo é gitignored (teste local); o script também atualiza
// data/threads.json para que a thread apareça na lista lateral.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '..');
const dataDir = path.join(root, 'data');
const threadsDir = path.join(dataDir, 'threads');
const indexPath = path.join(dataDir, 'threads.json');
const THREAD_ID = 'fixture-stress';

function argValue(flag, fallback) {
  const i = process.argv.indexOf(flag);
  return i !== -1 && process.argv[i + 1] ? Number(process.argv[i + 1]) : fallback;
}

const TOTAL = argValue('--messages', 65000);
const REMOVE = process.argv.includes('--remove');

function readIndex() {
  try {
    return JSON.parse(fs.readFileSync(indexPath, 'utf8'));
  } catch {
    return [];
  }
}

function writeIndex(entries) {
  fs.writeFileSync(indexPath, JSON.stringify(entries, null, 2) + '\n');
}

if (REMOVE) {
  const file = path.join(threadsDir, `${THREAD_ID}.json`);
  if (fs.existsSync(file)) fs.unlinkSync(file);
  writeIndex(readIndex().filter((t) => t.id !== THREAD_ID));
  console.log('[fixture] removida e índice limpo.');
  process.exit(0);
}

/* RNG determinística (mulberry32) para conteúdo reproduzível */
let seed = 42;
function rand() {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

const WORDS = [
  'pauta', 'reuniao', 'relatorio', 'laudo', 'cronograma', 'aditivo', 'fiscalizacao',
  'vistoria', 'obra', 'bloco', 'anexo', 'medicao', 'pagamento', 'nota', 'fiscal',
  'empenho', 'processo', 'documento', 'prazo', 'equipe', 'parecer', 'juridico',
  'gestao', 'contrato', 'medida', 'provisorio', 'ata', 'pendencia', 'assinatura',
  'resposta', 'encaminhamento', 'protocolo',
];

const SENDERS = ['daniel-vorcaro', 'flavio-bolsonaro', 'thiago-miranda'];
const START = Date.UTC(2023, 0, 2, 11, 0, 0); // 08:00 em -03:00
const STEP_MS = 45 * 1000;

function isoAt(ms) {
  const d = new Date(ms);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}` +
         `T${p(d.getUTCHours())}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}-03:00`;
}

function sentence() {
  const n = 10 + Math.floor(rand() * 8);
  const words = [];
  for (let i = 0; i < n; i++) words.push(WORDS[Math.floor(rand() * WORDS.length)]);
  const s = words.join(' ');
  return s[0].toUpperCase() + s.slice(1) + '.';
}

console.time('[fixture] geração');
fs.mkdirSync(threadsDir, { recursive: true });

const messages = new Array(TOTAL);
for (let i = 0; i < TOTAL; i++) {
  const id = `m-${String(i + 1).padStart(5, '0')}`;
  const isSystem = rand() < 0.02;
  const page = 120 + Math.floor(i / 150);
  messages[i] = {
    id,
    timestamp: isoAt(START + i * STEP_MS),
    sender_id: SENDERS[i % SENDERS.length],
    type: isSystem ? 'system' : 'text',
    content: isSystem
      ? 'Mensagem de sistema da fixture sintética.'
      : `${sentence()} Mensagem ${i + 1}.`,
    source_ref: `IP 2024/0123 · fl. ${page}`,
    status: 'confirmed',
    added_in: 'fixture',
  };
}

const lastTs = messages[TOTAL - 1].timestamp;
const thread = {
  id: THREAD_ID,
  title: 'FIXTURE — Teste de estresse',
  participants_ids: SENDERS,
  source: {
    document: 'Fixture sintética (não é material de caso)',
    url: '',
    pages: 'fl. 120–554',
  },
  messages,
};

fs.writeFileSync(path.join(threadsDir, `${THREAD_ID}.json`), JSON.stringify(thread));

const index = readIndex().filter((t) => t.id !== THREAD_ID);
index.push({
  id: THREAD_ID,
  title: thread.title,
  participants_ids: SENDERS,
  message_count: TOTAL,
  last_message_at: lastTs,
  last_message_preview: messages[TOTAL - 1].content.slice(0, 90),
  source: thread.source,
});
writeIndex(index);
console.timeEnd('[fixture] geração');

const mb = (fs.statSync(path.join(threadsDir, `${THREAD_ID}.json`)).size / 1024 / 1024).toFixed(1);
console.log(`[fixture] ${TOTAL} mensagens escritas (${mb} MB). Abra o site e teste a busca — o tempo está exibido na view de resultados.`);
