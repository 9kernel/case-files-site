#!/usr/bin/env node
// build-network.mjs — gera data/network.json: grafo de conexões do arquivo.
//
// Nós: Vorcaro (centro), contatos (anel interno) e instituições (anel externo).
// Arestas:
//   spoke    — Vorcaro ↔ contato (peso = nº de mensagens da conversa)
//   mention  — contato ↔ entidade citada em mensagens DA CONVERSA dele
//              (com evidência: ids das mensagens e quem falou)
//
// Detecção por padrões curados (normalizados, sem acento), com subtração de
// ambiguidades (ex.: “Moraes” não vale dentro de “Viviane de Moraes”).
// Rodar:  node scripts/build-network.mjs   (após qualquer mudança em data/threads)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = path.join(root, 'data');

const norm = (s) =>
  s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

/* Padrões por participante: [regexNormalizada(subtrações)] */
const PEOPLE_PATTERNS = {
  'alexandre-moraes': [/alexandre de moraes/, /ministro alexandre/, [/\bmoraes\b/, /viviane de moraes/]],
  'flavio-bolsonaro': [[/\bflavio\b/, /flavio carneiro/], /flavio bolsonaro/],
  'thiago-miranda': [/thiago miranda/],
  'mario-frias': [/\bmario frias\b/, [/\bmario\b/, /mario frias/]],
  'flavio-carneiro': [/flavio carneiro/, [/\bcarneiro\b/, /flavio carneiro/]],
  'roberto-justus': [/roberto justus/, [/\bjustus\b/, /roberto justus/]],
  'vanessa-souza': [/vanessa souza/, [/\bvanessa\b/, /vanessa souza/]],
  'fabio-faria': [/fabio faria/, [/\bfabio\b/, /fabio faria/]],
  'viviane-de-moraes': [/viviane de moraes/, [/\bviviane\b/, /viviane de moraes/], [/\bvivi moraes\b/, /vivi\b/]],
  'ana-matos': [/ana matos/],
  'ciro-soares': [/ciro soares/, /ciro rocha/],
  'leonardo-palhares': [/leonardo palhares/, [/\bpalhares\b/, /leonardo palhares/]],
  'angelo-silva': [/angelo silva/, [/\bangelo\b/, /angelo silva/]],
  'marcos-da-mata': [/marcos da mata/],
  'romy-banco-master': [[/\bromy\b/]],
  'alberto-felix': [/alberto felix/, [/\balberto\b/, /alberto felix/]],
  'marcio-conjur': [/marcio conjur/, [/\bconjur\b/, /marcio conjur/]],
  'luiz-renno': [/luiz renno/, [/\brenno\b/, /luiz renno/], [/\brenó\b/]],
  'geraldo-brazil-journal': [/brazil journal/, [/geraldo do brazil journal/]],
  'paulo-sergio': [/paulo sergio/],
  'ana-claudia-financeiro': [/ana claudia/],
  'felipe-mourao': [/felipe mourao/, [/\bfelipe\b/, /felipe mourao/]],
  'walfrido-warde': [/walfrido warde/, [/\bwalfrido\b/, /walfrido warde/], [/\bwarde\b/, /walfrido warde/]],
  'fabiano-zettel': [/fabiano zettel/, [/\bzettel\b/, /fabiano zettel/], [/\bfabiano\b/, /fabiano zettel/]],
  'paulo-henrique': [/paulo henrique/],
  'luciano-huck': [[/\bhuck\b/], [/\bluciano\b/]],
  'joao-doria': [[/\bdoria\b/], /joao doria/],
  'hugo-motta': [/hugo motta/, [/\bhugo\b/, /hugo motta/]],
  'roberto-campos-neto': [/campos neto/, /roberto campos/],
  'rodrigo-fux': [/rodrigo fux/],
  'davi-alcolumbre': [[/\balcolumbre\b/], [/\bdavi\b/]],
  'iraja': [[/\biraja\b/]],
  'nikolas-ferreira': [[/\bnikolas\b/]],
  'antonio-rueda': [[/\brueda\b/]],
  'yasmin-brunet': [[/\byasmin\b/], [/\bbrunet\b/]],
  'cezinha-de-madureira': [[/\bcezinha\b/]],
  // 'marcus-vinicius' NÃO entra na detecção de menções: as fontes não provam
  // que o contato do chat é o mesmo "Marcus Vinicius da Mata" (Prime Aviation)
  // citado em relatório da PF na conversa do Felipe Mourão.
};

const INSTITUTIONS = {
  'bc': { label: 'Banco Central', re: [/banco central/, [/\bbc\b/]] },
  'stf': { label: 'STF', re: [/\bstf\b/, /supremo tribunal/] },
  'stj': { label: 'STJ', re: [/\bstj\b/] },
  'tse': { label: 'TSE', re: [/\btse\b/] },
  'banco-master': { label: 'Banco Master', re: [/banco master/, [/\bmaster\b/, /master whats/]] },
  'will-bank': { label: 'Will Bank', re: [/will bank/] },
  'fgc': { label: 'FGC', re: [/\bfgc\b/, /fundo garantidor/] },
  'brb': { label: 'BRB', re: [/\bbrb\b/] },
  'pf': { label: 'Polícia Federal', re: [/policia federal/, [/\bpf\b/]] },
  'senado': { label: 'Senado', re: [/\bsenado\b/] },
  'camara': { label: 'Câmara dos Deputados', re: [/camara dos deputados/, [/\bcamara\b/, /camara dos deputados/]] },
};

function countPattern(text, pat) {
  if (Array.isArray(pat)) {
    const [pos, ...negs] = pat;
    let t = text;
    for (const n of negs) t = t.replace(new RegExp(n, 'g'), ' ');
    return (t.match(new RegExp(pos, 'g')) || []).length;
  }
  return (text.match(new RegExp(pat, 'g')) || []).length;
}

const participants = JSON.parse(fs.readFileSync(path.join(dataDir, 'participants.json'), 'utf8'));
const byId = new Map(participants.map((p) => [p.id, p]));
const index = JSON.parse(fs.readFileSync(path.join(dataDir, 'threads.json'), 'utf8'));

const threads = fs.readdirSync(path.join(dataDir, 'threads'))
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(fs.readFileSync(path.join(dataDir, 'threads', f), 'utf8')));

const contacts = [];
const mentionEdges = new Map(); // key: threadId|from|to

for (const t of threads) {
  const contactId = t.participants_ids.find((id) => id !== 'daniel-vorcaro');
  const idx = index.find((e) => e.id === t.id);
  contacts.push({
    id: contactId,
    name: byId.get(contactId)?.name || contactId,
    thread: t.id,
    title: t.title,
    msg_count: (t.messages || []).length,
  });

  for (const m of t.messages || []) {
    const text = norm(`${m.content || ''} ${m.editorial_note || ''}`);
    if (!text) continue;

    for (const [personId, pats] of Object.entries(PEOPLE_PATTERNS)) {
      if (personId === contactId) continue; // auto-menção não gera aresta
      const n = pats.reduce((acc, pat) => acc + countPattern(text, pat), 0);
      if (n > 0) addMention(t.id, contactId, personId, m, n);
    }
    for (const [instId, def] of Object.entries(INSTITUTIONS)) {
      const n = def.re.reduce((acc, pat) => acc + countPattern(text, pat), 0);
      if (n > 0) addMention(t.id, contactId, instId, m, n);
    }
  }
}

function addMention(threadId, from, to, msg, n) {
  const key = `${threadId}|${from}|${to}`;
  const e = mentionEdges.get(key) || {
    type: 'mention', thread: threadId, from, to, count: 0, evidence: [],
  };
  e.count += n;
  if (e.evidence.length < 8) {
    e.evidence.push({ id: msg.id, sender: msg.sender_id, date: msg.date || null });
  }
  mentionEdges.set(key, e);
}

// fala do Vorcaro citando alguém também conecta (ele é o centro):
// mantemos a aresta contato↔citado, mas registramos o falante na evidência.

const out = {
  // sem carimbo de data: a saída é determinística e o CI pode conferir
  // se data/network.json está em sincronia com data/threads (git diff).
  center: 'daniel-vorcaro',
  center_name: byId.get('daniel-vorcaro').name,
  contacts: contacts.sort((a, b) => b.msg_count - a.msg_count),
  institutions: Object.entries(INSTITUTIONS).map(([id, d]) => ({ id, label: d.label })),
  edges: [...mentionEdges.values()].sort((a, b) => b.count - a.count),
};

const outFile = path.join(dataDir, 'network.json');
fs.writeFileSync(outFile, JSON.stringify(out, null, 1) + '\n', 'utf8');

const personEdges = out.edges.filter((e) => !INSTITUTIONS[e.to]).length;
const instEdges = out.edges.length - personEdges;
console.log(`[network] ${out.contacts.length} contatos · ${personEdges} arestas pessoa↔pessoa · ${instEdges} pessoa↔instituição`);
console.log(`[network] escrito: data/network.json`);
