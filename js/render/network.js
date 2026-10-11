// network.js — mapa de conexões da home: Vorcaro no centro, contatos ao redor,
// arcos de menções (pessoa↔pessoa e pessoa↔instituição) extraídos das
// mensagens publicadas por scripts/build-network.mjs (data/network.json).
//
// Interação: passar o mouse em um nó destaca suas conexões; clicar num contato
// abre a conversa; clicar numa aresta de menção mostra as mensagens que a
// fundamentam (deep-link direto #/thread/{id}/{msgId}).

import { getNetwork, getParticipants } from '../api.js';
import { escapeHtml as esc, initials } from '../utils.js';

const W = 900;
const H = 880;
const CX = W / 2;
const CY = 420;
const R_CONTACT = 245;   // anel de contatos
const R_INST = 372;      // anel de instituições
const MAX_EVIDENCE = 6;

const svgEl = (tag, attrs = {}, parent = null) => {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (parent) parent.appendChild(el);
  return el;
};

export async function renderNetwork(container) {
  const [net, participants] = await Promise.all([getNetwork(), getParticipants()]);
  const pmap = new Map(participants.map((p) => [p.id, p]));
  const instById = new Map(net.institutions.map((i) => [i.id, i]));

  container.innerHTML = `
    <div class="network-scroll">
      <svg class="network-svg" viewBox="0 0 ${W} ${H}" role="img"
           aria-label="Mapa de conexões: Daniel Vorcaro no centro, contatos ao redor e menções entre conversas"></svg>
    </div>
    <div class="network-tooltip" hidden></div>
    <p class="network-note">
      Menções extraídas automaticamente do texto das mensagens publicadas (normalizadas, sem acento;
      ambiguidades subtraídas). Não exaustivo — nomes que não aparecem no texto de nenhuma conversa não
      geram conexão. Clique em um contato para abrir a conversa ou numa conexão para ver as mensagens
      que a fundamentam.
    </p>`;

  const svg = container.querySelector('.network-svg');
  const tooltip = container.querySelector('.network-tooltip');
  const layers = {
    edges: svgEl('g', { class: 'net-edges' }, svg),
    hit: svgEl('g', { class: 'net-hits' }, svg),
    nodes: svgEl('g', { class: 'net-nodes' }, svg),
  };

  /* ---------- posições ---------- */
  const pos = new Map();
  // contatos: ordenados por nº de mensagens (mais volumosas começam no topo, sentido horário)
  const contacts = net.contacts;
  contacts.forEach((c, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / contacts.length;
    pos.set(c.id, { x: CX + R_CONTACT * Math.cos(a), y: CY + R_CONTACT * Math.sin(a), a });
  });
  net.institutions.forEach((inst, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * (i + 0.5)) / net.institutions.length;
    pos.set(inst.id, { x: CX + R_INST * Math.cos(a), y: CY + R_INST * Math.sin(a), a });
  });
  pos.set('daniel-vorcaro', { x: CX, y: CY, a: -Math.PI / 2 });

  /* ---------- dados agregados p/ tooltip ---------- */
  const mentionByNode = new Map();
  for (const e of net.edges) {
    for (const key of [e.from, e.to]) {
      if (!mentionByNode.has(key)) mentionByNode.set(key, []);
      mentionByNode.get(key).push(e);
    }
  }

  /* ---------- arestas ---------- */
  const spokeW = (n) => 1 + Math.min(3, Math.log2(1 + n) * 0.9);

  for (const c of contacts) {
    const p = pos.get(c.id);
    svgEl('line', {
      class: 'net-spoke', x1: CX, y1: CY, x2: p.x, y2: p.y,
      'stroke-width': spokeW(c.msg_count), 'data-nodes': `daniel-vorcaro,${c.id}`,
    }, layers.edges);
  }

  for (const e of net.edges) {
    const p1 = pos.get(e.from);
    const p2 = pos.get(e.to);
    if (!p1 || !p2) continue;
    const isInst = instById.has(e.to);
    if (isInst) {
      svgEl('line', {
        class: 'net-mention net-mention-inst', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
        'stroke-width': 1 + Math.min(2.5, e.count * 0.5), 'data-edge': e.thread + '|' + e.from + '|' + e.to,
        'data-nodes': `${e.from},${e.to}`,
      }, layers.edges);
    } else {
      // arco curvado para fora do centro
      const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
      const dx = mx - CX, dy = my - CY;
      const len = Math.hypot(dx, dy) || 1;
      const k = 1 + 90 / len;
      const cx2 = CX + dx * k, cy2 = CY + dy * k;
      svgEl('path', {
        class: 'net-mention net-mention-person', d: `M ${p1.x} ${p1.y} Q ${cx2} ${cy2} ${p2.x} ${p2.y}`,
        fill: 'none', 'stroke-width': 1.4 + Math.min(3, e.count * 0.55),
        'data-edge': e.thread + '|' + e.from + '|' + e.to, 'data-nodes': `${e.from},${e.to}`,
      }, layers.edges);
    }
  }

  /* ---------- nós ---------- */
  const drawContact = (c) => {
    const p = pos.get(c.id);
    const g = svgEl('g', { class: 'net-node net-contact', 'data-id': c.id, transform: `translate(${p.x},${p.y})` }, layers.nodes);
    const p0 = pmap.get(c.id);
    svgEl('circle', { r: 17, class: 'net-avatar-bg' }, g);
    if (p0?.photo) {
      const cp = svgEl('clipPath', { id: `netclip-${c.id}` }, svg.querySelector('defs') || svgEl('defs', {}, svg));
      svgEl('circle', { r: 16, cx: 0, cy: 0 }, cp);
      svgEl('image', {
        href: `public/media/people/${p0.photo}`, x: -16, y: -16, width: 32, height: 32,
        'clip-path': `url(#netclip-${c.id})`, preserveAspectRatio: 'xMidYMid slice',
      }, g);
    } else {
      svgEl('text', { class: 'net-initials', 'text-anchor': 'middle', dy: '0.35em' }, g).textContent = initials(c.name);
    }
    const lx = Math.cos(p.a) * 28, ly = Math.sin(p.a) * 28;
    const anchor = Math.abs(Math.cos(p.a)) < 0.3 ? 'middle' : (Math.cos(p.a) > 0 ? 'start' : 'end');
    const label = svgEl('text', {
      class: 'net-label', x: lx, y: ly, 'text-anchor': anchor, dy: '0.35em',
    }, g);
    // nomes longos quebram em duas linhas (tspan) em vez de cortar com …
    const words = c.name.split(' ');
    if (c.name.length > 15 && words.length > 1) {
      let best = 1, diff = Infinity;
      for (let i = 1; i < words.length; i++) {
        const a = words.slice(0, i).join(' ').length;
        const b = words.slice(i).join(' ').length;
        if (Math.abs(a - b) < diff) { diff = Math.abs(a - b); best = i; }
      }
      const l1 = words.slice(0, best).join(' ');
      let l2 = words.slice(best).join(' ');
      if (l2.length > 18) l2 = l2.slice(0, 17) + '…';
      const t1 = svgEl('tspan', { x: lx, dy: '-0.45em' }, label);
      t1.textContent = l1;
      const t2 = svgEl('tspan', { x: lx, dy: '1.15em' }, label);
      t2.textContent = l2;
    } else {
      label.textContent = c.name;
    }
    return g;
  };

  const drawInstitution = (inst) => {
    const p = pos.get(inst.id);
    const g = svgEl('g', { class: 'net-node net-inst', 'data-id': inst.id, transform: `translate(${p.x},${p.y})` }, layers.nodes);
    svgEl('rect', { x: -13, y: -10, width: 26, height: 20, rx: 4, class: 'net-inst-box' }, g);
    svgEl('text', { class: 'net-inst-sigla', 'text-anchor': 'middle', dy: '0.35em' }, g)
      .textContent = instSigla(inst);
    const anchor = Math.cos(p.a) >= 0 ? 'start' : 'end';
    svgEl('text', { class: 'net-label net-label-inst', x: Math.cos(p.a) * 22, y: Math.sin(p.a) * 22, 'text-anchor': anchor, dy: '0.35em' }, g)
      .textContent = inst.label;
    return g;
  };

  const instSigla = (inst) => {
    const map = { 'bc': 'BC', 'stf': 'STF', 'stj': 'STJ', 'tse': 'TSE', 'banco-master': 'BM', 'will-bank': 'WB', 'fgc': 'FGC', 'brb': 'BRB', 'pf': 'PF', 'senado': 'SEN', 'camara': 'CD' };
    return map[inst.id] || inst.label.slice(0, 2).toUpperCase();
  };

  for (const inst of net.institutions) drawInstitution(inst);
  for (const c of contacts) drawContact(c);

  /* ---------- centro (Vorcaro) ---------- */
  const centerG = svgEl('g', { class: 'net-node net-center', 'data-id': 'daniel-vorcaro', transform: `translate(${CX},${CY})` }, layers.nodes);
  svgEl('circle', { r: 34, class: 'net-center-ring' }, centerG);
  const vPhoto = pmap.get('daniel-vorcaro')?.photo;
  if (vPhoto) {
    const cp = svgEl('clipPath', { id: 'netclip-center' }, svg.querySelector('defs') || svgEl('defs', {}, svg));
    svgEl('circle', { r: 30, cx: 0, cy: 0 }, cp);
    svgEl('image', { href: `public/media/people/${vPhoto}`, x: -30, y: -30, width: 60, height: 60, 'clip-path': 'url(#netclip-center)', preserveAspectRatio: 'xMidYMid slice' }, centerG);
  } else {
    svgEl('text', { class: 'net-initials net-initials-big', 'text-anchor': 'middle', dy: '0.35em' }, centerG).textContent = 'DV';
  }
  svgEl('text', { class: 'net-label net-label-center', y: 52, 'text-anchor': 'middle' }, centerG)
    .textContent = net.center_name;

  /* ---------- camada de clique das arestas ---------- */
  for (const e of net.edges) {
    const key = e.thread + '|' + e.from + '|' + e.to;
    const visual = layers.edges.querySelector(`[data-edge="${CSS.escape(key)}"]`);
    if (!visual) continue;
    const hitEl = visual.cloneNode(false);
    hitEl.setAttribute('class', 'net-hit');
    hitEl.setAttribute('stroke-width', 14);
    hitEl.setAttribute('data-edge', key);
    hitEl.removeAttribute('data-nodes');
    layers.hit.appendChild(hitEl);
  }

  /* ---------- interação ---------- */
  const allSvg = container.querySelectorAll('.net-node, .net-spoke, .net-mention');
  const nameOf = (id) => pmap.get(id)?.name || instById.get(id)?.label || id;

  let hideTimer = null;
  const cancelHide = () => { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } };
  const showTooltip = (html, ref) => {
    cancelHide();
    tooltip.innerHTML = html;
    tooltip.hidden = false;
    const wrap = container.closest('.network-wrap') || container;
    const wr = wrap.getBoundingClientRect();
    const rr = ref.getBoundingClientRect();
    let x = rr.left - wr.left + rr.width / 2;
    let y = rr.bottom - wr.top + 8;
    tooltip.style.left = `${Math.max(8, Math.min(x - 140, wr.width - 300))}px`;
    if (y + 180 > wr.height) y = Math.max(8, rr.top - wr.top - 170);
    tooltip.style.top = `${y}px`;
  };
  const hideTooltip = () => { tooltip.hidden = true; };
  const scheduleHide = () => { cancelHide(); hideTimer = setTimeout(hideTooltip, 180); };
  tooltip.addEventListener('mouseenter', cancelHide);
  tooltip.addEventListener('mouseleave', scheduleHide);

  const highlight = (idOrPair) => {
    const want = (el) => {
      if (!idOrPair) return true;
      if (el.classList.contains('net-node')) return el.dataset.id === idOrPair;
      const nodes = (el.dataset.nodes || '').split(',');
      return nodes.includes(idOrPair);
    };
    allSvg.forEach((el) => el.classList.toggle('dim', idOrPair ? !want(el) : false));
  };

  // nós
  layers.nodes.querySelectorAll('.net-node').forEach((node) => {
    node.addEventListener('mouseenter', () => {
      highlight(node.dataset.id);
      const c = contacts.find((x) => x.id === node.dataset.id);
      if (c) {
        const ms = mentionByNode.get(c.id) || [];
        const cited = ms.filter((e) => e.from === c.id).reduce((a, e) => a + e.count, 0);
        const citedBy = ms.filter((e) => e.to === c.id).reduce((a, e) => a + e.count, 0);
        showTooltip(`
          <strong>${esc(c.name)}</strong><br>
          <span class="ntt-sub">${esc(pmap.get(c.id)?.role || '')}</span>
          <div class="ntt-row">Conversa: ${c.msg_count} mensagem(ns)</div>
          <div class="ntt-row">Citou outros/instituições: ${cited} menção(ões)</div>
          <div class="ntt-row">Citado em outras conversas: ${citedBy} menção(ões)</div>
          <a class="ntt-link" href="#/thread/${esc(c.thread)}">Abrir conversa →</a>
        `, node);
      } else if (node.dataset.id === 'daniel-vorcaro') {
        showTooltip(`<strong>${esc(net.center_name)}</strong><br><span class="ntt-sub">Centro do arquivo — ${contacts.length} conversas publicadas</span>`, node);
      } else {
        const inst = instById.get(node.dataset.id);
        const ms = (mentionByNode.get(node.dataset.id) || []).filter((e) => e.to === node.dataset.id);
        const total = ms.reduce((a, e) => a + e.count, 0);
        const threads = [...new Set(ms.map((e) => e.thread))];
        showTooltip(`
          <strong>${esc(inst.label)}</strong>
          <div class="ntt-row">Mencionada em ${threads.length} conversa(s) — ${total} menção(ões)</div>
          ${threads.slice(0, 5).map((t) => { const ct = contacts.find((c) => c.thread === t); return ct ? `<div class="ntt-row ntt-small">· conversa com ${esc(ct.name)}</div>` : ''; }).join('')}
        `, node);
      }
    });
    node.addEventListener('mouseleave', () => { highlight(null); scheduleHide(); });
    node.addEventListener('click', () => {
      const c = contacts.find((x) => x.id === node.dataset.id);
      if (c) location.hash = `#/thread/${c.thread}`;
    });
  });

  svg.addEventListener('click', () => hideTooltip());

  // arestas
  layers.hit.querySelectorAll('.net-hit').forEach((hit) => {
    const key = hit.dataset.edge;
    const edge = net.edges.find((e) => e.thread + '|' + e.from + '|' + e.to === key);
    if (!edge) return;
    const visual = layers.edges.querySelector(`[data-edge="${CSS.escape(key)}"]`);
    hit.addEventListener('mouseenter', () => {
      highlight(null);
      visual.classList.add('active');
      const contact = contacts.find((c) => c.id === edge.from);
      const evs = edge.evidence.slice(0, MAX_EVIDENCE).map((v) => {
        const d = v.date ? `${v.date.split('-')[2]}/${v.date.split('-')[1]}/${v.date.split('-')[0]}` : 's/ data';
        return `<a class="ntt-ev" href="#/thread/${esc(edge.thread)}/${esc(v.id)}">${d} · ${esc(nameOf(v.sender))} → ver mensagem</a>`;
      }).join('');
      showTooltip(`
        <strong>${esc(nameOf(edge.from))} → ${esc(nameOf(edge.to))}</strong>
        <div class="ntt-row">${edge.count} menção(ões) na conversa com ${esc(contact?.name || '')}</div>
        ${evs}
        ${edge.evidence.length > MAX_EVIDENCE ? `<div class="ntt-small">+ ${edge.evidence.length - MAX_EVIDENCE} outra(s)</div>` : ''}
      `, hit);
    });
    hit.addEventListener('mouseleave', () => {
      visual.classList.remove('active');
      scheduleHide();
    });
    hit.addEventListener('click', (ev) => {
      ev.stopPropagation();
      hit.dispatchEvent(new MouseEvent('mouseenter'));
    });
  });
}
