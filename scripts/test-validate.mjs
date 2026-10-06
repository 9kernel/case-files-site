#!/usr/bin/env node
// test-validate.mjs — testa CADA regra de rejeição do validate.mjs.
// Uso:  node scripts/test-validate.mjs
// Exit 1 se qualquer caso falhar. Roda no CI junto do validador.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { validateData } from './validate.mjs';

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'validate-test-'));
const dataDir = path.join(tmpRoot, 'data');
fs.mkdirSync(path.join(dataDir, 'threads'), { recursive: true });

const participants = [
  { id: 'p-ana', name: 'Ana', role: 'r', aliases: [], summary: 's' },
  { id: 'p-bruno', name: 'Bruno', role: 'r', aliases: [], summary: 's' },
];

function baseThread() {
  return {
    id: 'thread-teste',
    title: 'Thread de teste',
    participants_ids: ['p-ana', 'p-bruno'],
    source: { document: 'IP 0000/0000', url: 'https://example.org/x.pdf', pages: 'fl. 1–2' },
    messages: [
      {
        id: 'm-00001',
        timestamp: '2024-03-11T08:00:00-03:00',
        sender_id: 'p-ana',
        type: 'text',
        content: 'primeira mensagem',
        source_ref: 'IP 0000/0000 · fl. 1',
        status: 'confirmed',
        added_in: 'abc1234',
      },
      {
        id: 'm-00002',
        timestamp: '2024-03-11T08:05:00-03:00',
        sender_id: 'p-bruno',
        type: 'text',
        content: 'segunda mensagem',
        source_ref: 'IP 0000/0000 · fl. 1',
        status: 'confirmed',
        added_in: 'abc1234',
      },
    ],
  };
}

function writeData(thread, participantsData = participants) {
  fs.writeFileSync(path.join(dataDir, 'participants.json'), JSON.stringify(participantsData));
  fs.writeFileSync(path.join(dataDir, 'threads', 'thread-teste.json'), JSON.stringify(thread));
}

function runCase(name, mutate, expectedCodes) {
  const thread = baseThread();
  mutate(thread);
  writeData(thread);
  const { errors } = validateData(dataDir, tmpRoot);
  const codes = new Set(errors.map((e) => e.code));
  const missing = expectedCodes.filter((c) => !codes.has(c));
  if (missing.length) {
    console.error(`✗ ${name}: esperava ${expectedCodes.join(', ')}, obtive ${[...codes].join(', ') || '(nenhum erro)'}`);
    for (const e of errors) console.error(`    ${e.code}: ${e.message}`);
    return false;
  }
  console.log(`✓ ${name} → ${expectedCodes.join(', ')}`);
  return true;
}

let ok = true;

/* caso-base DEVE passar sem erros */
writeData(baseThread());
{
  const { errors, warnings } = validateData(dataDir, tmpRoot);
  if (errors.length) {
    console.error(`✗ caso-base deveria passar, mas gerou: ${errors.map((e) => `${e.code}: ${e.message}`).join('; ')}`);
    ok = false;
  } else {
    console.log(`✓ caso-base passa sem erros (${warnings.length} warning(s))`);
  }
}

/* cada regra de rejeição */
ok = runCase('sem source_ref', (t) => delete t.messages[0].source_ref, ['E_MISSING_SOURCE_REF']) && ok;
ok = runCase('source_ref vazio', (t) => { t.messages[0].source_ref = '  '; }, ['E_MISSING_SOURCE_REF']) && ok;
ok = runCase('sem status', (t) => delete t.messages[1].status, ['E_MISSING_STATUS']) && ok;
ok = runCase('status inválido', (t) => { t.messages[0].status = 'talvez'; }, ['E_BAD_STATUS']) && ok;
ok = runCase('sender inexistente', (t) => { t.messages[1].sender_id = 'p-fantasma'; }, ['E_UNKNOWN_SENDER']) && ok;
ok = runCase('sem sender', (t) => delete t.messages[0].sender_id, ['E_MISSING_SENDER']) && ok;
ok = runCase('timestamps fora de ordem', (t) => { t.messages[1].timestamp = '2024-03-11T07:00:00-03:00'; }, ['E_TIMESTAMP_ORDER']) && ok;
ok = runCase('timestamp em formato inválido', (t) => { t.messages[0].timestamp = '11/03/2024 08:00'; }, ['E_BAD_TIMESTAMP']) && ok;
ok = runCase('timestamp sem offset', (t) => { t.messages[0].timestamp = '2024-03-11T08:00:00'; }, ['E_BAD_TIMESTAMP']) && ok;
ok = runCase('id duplicado', (t) => { t.messages[1].id = 'm-00001'; }, ['E_DUPLICATE_ID']) && ok;
ok = runCase('id fora do padrão', (t) => { t.messages[0].id = 'msg1'; }, ['E_BAD_ID']) && ok;
ok = runCase('sem id', (t) => delete t.messages[0].id, ['E_MISSING_ID']) && ok;
ok = runCase('type fora da lista', (t) => { t.messages[0].type = 'sticker'; }, ['E_BAD_TYPE']) && ok;
ok = runCase('sem type', (t) => delete t.messages[0].type, ['E_BAD_TYPE']) && ok;
ok = runCase('sem added_in', (t) => delete t.messages[0].added_in, ['E_MISSING_ADDED_IN']) && ok;
ok = runCase('content não-string', (t) => { t.messages[0].content = 42; }, ['E_BAD_CONTENT']) && ok;
ok = runCase('reply_to inexistente', (t) => { t.messages[1].reply_to = 'm-99999'; }, ['E_BAD_REPLY_TO']) && ok;
ok = runCase('sender de thread inexistente em participants', (t) => { t.participants_ids = ['p-fantasma']; }, ['E_UNKNOWN_PARTICIPANT']) && ok;
ok = runCase('thread sem source', (t) => delete t.source, ['E_THREAD_FIELD']) && ok;
ok = runCase('media.url sem arquivo', (t) => { t.messages[0].type = 'image'; t.messages[0].media = { url: '/public/media/inexistente.png', filename: 'x.png' }; }, ['E_MISSING_MEDIA_FILE']) && ok;

/* JSON inválido */
writeData(baseThread());
fs.writeFileSync(path.join(dataDir, 'threads', 'quebrado.json'), '{ isto não é json ');
{
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_JSON_PARSE' && e.file.includes('quebrado.json'))) {
    console.log('✓ JSON inválido → E_JSON_PARSE');
  } else {
    console.error('✗ JSON inválido não foi detectado');
    ok = false;
  }
}

/* participants.json inválido */
fs.writeFileSync(path.join(dataDir, 'participants.json'), '[{]');
{
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_JSON_PARSE' && e.file.includes('participants.json'))) {
    console.log('✓ participants.json inválido → E_JSON_PARSE');
  } else {
    console.error('✗ participants.json inválido não foi detectado');
    ok = false;
  }
}

/* participante duplicado */
{
  const dup = [...participants, { id: 'p-ana', name: 'Outra Ana', role: 'r', aliases: [], summary: 's' }];
  writeData(baseThread(), dup);
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_DUP_PARTICIPANT')) {
    console.log('✓ participante duplicado → E_DUP_PARTICIPANT');
  } else {
    console.error('✗ participante duplicado não foi detectado');
    ok = false;
  }
}

fs.rmSync(tmpRoot, { recursive: true, force: true });

console.log(ok ? '\n[test-validate] TODOS OS CASOS PASSARAM.' : '\n[test-validate] FALHAS ENCONTRADAS.');
process.exit(ok ? 0 : 1);
