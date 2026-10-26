#!/usr/bin/env node
// test-whatsnew.mjs — invariante do selo "novo" (pill) do whatsnew.
//
// O selo "novo" da UI acende APENAS nos registros cujo added_in está listado em
// CURRENT_BATCHES (scripts/build-whatsnew.mjs), replicado em data/whatsnew.json.
// A lista é atualizada À MÃO a cada rodada de inclusão — e já foi esquecida
// (26/10/2026: 120 registros inseridos sem selo até a correção). Este teste
// fecha essa lacuna falando o CI sempre que:
//
//   1. houver nos dados um lote added_in (sufixo YYYYMMDD) MAIS RECENTE que os
//      lotes listados em CURRENT_BATCHES — ou seja, alguém inseriu registros e
//      não atualizou a lista do selo;
//   2. data/whatsnew.json estiver com current_batches divergente do script —
//      ou seja, o artefato não foi regenerado após a edição.
//
// Uso:  node scripts/test-whatsnew.mjs    (exit 1 se qualquer invariante falhar)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const threadsDir = path.join(rootDir, 'data', 'threads');
const buildScript = path.join(rootDir, 'scripts', 'build-whatsnew.mjs');
const artifact = path.join(rootDir, 'data', 'whatsnew.json');

let ok = true;
const fail = (msg) => { console.error(`✗ ${msg}`); ok = false; };

/* --- 1. lotes usados nos dados (rótulos added_in com sufixo de data) --- */
const datedLabel = (r) => (/\d{8}$/.test(String(r?.added_in || '')) ? r.added_in : null);
const labels = new Set();
for (const file of fs.readdirSync(threadsDir).filter((f) => f.endsWith('.json'))) {
  let t;
  try {
    t = JSON.parse(fs.readFileSync(path.join(threadsDir, file), 'utf8'));
  } catch {
    continue; // JSON inválido é erro do validate.mjs, não daqui
  }
  for (const r of [...(t.messages || []), ...(t.timeline_events || [])]) {
    const label = datedLabel(r);
    if (label) labels.add(label);
  }
}

/* --- 2. CURRENT_BATCHES declarado no build-whatsnew.mjs --- */
const src = fs.readFileSync(buildScript, 'utf8');
const m = src.match(/const CURRENT_BATCHES\s*=\s*\[([^\]]*)\]/);
const currentBatches = m
  ? [...m[1].matchAll(/'([^']+)'|"([^"]+)"/g)].map((x) => x[1] || x[2])
  : [];
if (!m) fail('scripts/build-whatsnew.mjs sem CURRENT_BATCHES parseável.');

/* --- 3. invariante 1: todo lote da data MAIS RECENTE deve estar no selo --- */
const dateOf = (l) => Number(String(l).match(/(\d{8})$/)[1]);
if (labels.size) {
  const maxDate = Math.max(...[...labels].map(dateOf));
  const latest = [...labels].filter((l) => dateOf(l) === maxDate).sort();
  const missing = latest.filter((l) => !currentBatches.includes(l));
  if (missing.length) {
    fail(
      `lote(s) mais recente(s) nos dados fora de CURRENT_BATCHES: ${missing.join(', ')}. ` +
      `Atualize CURRENT_BATCHES em scripts/build-whatsnew.mjs e rode ` +
      `node scripts/build-whatsnew.mjs — sem isso os registros novos NÃO ganham o selo "novo" na UI.`
    );
  } else {
    console.log(`✓ lote(s) corrente(s) no selo: ${latest.join(', ')}`);
  }
} else {
  console.log('✓ nenhum lote datado nos dados (nada a verificar)');
}

/* --- 4. invariante 2: artefato data/whatsnew.json em sincronia com o script --- */
if (fs.existsSync(artifact)) {
  let payload;
  try {
    payload = JSON.parse(fs.readFileSync(artifact, 'utf8'));
  } catch {
    payload = null;
  }
  const artifactBatches = payload?.current_batches;
  if (!Array.isArray(artifactBatches) || artifactBatches.length !== currentBatches.length ||
      !currentBatches.every((l) => artifactBatches.includes(l))) {
    fail(
      `data/whatsnew.json com current_batches divergente do script ` +
      `(${JSON.stringify(artifactBatches)} vs ${JSON.stringify(currentBatches)}) — ` +
      `rode node scripts/build-whatsnew.mjs e comite o artefato regenerado.`
    );
  } else {
    console.log('✓ data/whatsnew.json em sincronia com CURRENT_BATCHES');
  }
} else {
  fail('data/whatsnew.json inexistente — rode node scripts/build-whatsnew.mjs.');
}

console.log(ok ? '\n[test-whatsnew] OK.' : '\n[test-whatsnew] FALHOU.');
process.exit(ok ? 0 : 1);
