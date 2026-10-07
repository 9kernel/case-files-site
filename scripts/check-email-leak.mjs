#!/usr/bin/env node
// check-email-leak.mjs — impede e-mail pessoal/corporativo e marcadores de
// afiliação em arquivos publicados (missão §26).
//
// Uso:  node scripts/check-email-leak.mjs [rootDir]
// Exit 1 se qualquer achado. Configurável em scripts/leak-check-config.json
// (domínios permitidos + substrings proibidas) — nada de dado pessoal no código.
//
// Regras:
//   E_EMAIL_FOUND        e-mail cujo domínio não está na lista de permitidos
//                        (institucional público/exemplo) — potencial dado pessoal
//   E_FORBIDDEN_SUBSTRING  substring configurada (marcador de afiliação
//                        corporativa/pessoal) presente em arquivo publicado

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(process.argv[2] || path.join(scriptDir, '..'));

const cfgPath = path.join(scriptDir, 'leak-check-config.json');
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const EMAIL_RE = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

const domainAllowed = (email) => {
  const domain = email.split('@')[1].toLowerCase();
  return cfg.allow_email_domains.some((d) => domain === d || domain.endsWith('.' + d));
};

const findings = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (cfg.skip_paths.includes(entry.name)) continue;
      walk(path.join(dir, entry.name));
      continue;
    }
    if (!cfg.scan_extensions.includes(path.extname(entry.name).toLowerCase())) continue;
    const full = path.join(dir, entry.name);
    const rel = path.relative(rootDir, full).replace(/\\/g, '/');
    if ((cfg.skip_files || []).includes(rel)) continue;
    const text = fs.readFileSync(full, 'utf8');
    const lines = text.split('\n');
    lines.forEach((line, i) => {
      for (const email of line.match(EMAIL_RE) || []) {
        if (!domainAllowed(email)) {
          findings.push({ code: 'E_EMAIL_FOUND', file: rel, line: i + 1, detail: email });
        }
      }
      for (const sub of cfg.forbidden_substrings) {
        if (sub && line.toLowerCase().includes(sub.toLowerCase())) {
          findings.push({ code: 'E_FORBIDDEN_SUBSTRING', file: rel, line: i + 1, detail: sub });
        }
      }
    });
  }
}

walk(rootDir);

for (const f of findings) {
  console.error(`[error] ${f.code} — ${f.file}:${f.line}\n        ${f.detail}`);
}
console.log(`[leak-check] ${findings.length} achado(s) em ${rootDir}.`);
if (findings.length) {
  console.error('[leak-check] FALHOU — dado pessoal potencial em arquivo publicado.');
  process.exit(1);
}
console.log('[leak-check] OK.');
