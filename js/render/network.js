// network.js — mapa de conexões: Vorcaro no centro, contatos ao redor,
// arcos de menções (pessoa↔pessoa e pessoa↔instituição) extraídos das
// mensagens publicadas por scripts/build-network.mjs (data/network.json).
//
// A roda inteira gira devagar ao redor do Vorcaro ("ciranda"); avatares e
// rótulos contra-giram para permanecerem em pé. Ao interagir (mouse/toque)
// a rotação pausa. Clicar num contato abre a conversa direto (sem modal);
// conexões e instituições mantêm tooltip com a evidência.

import { getNetwork, getParticipants } from '../api.js';
import { escapeHtml as esc, initials } from '../utils.js';

const svgEl = (tag, attrs = {}, parent = null) => {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (parent) parent.appendChild(el);
  return el;
};

export async function renderNetwork(container, opts = {}) {
  const [net, participants] = await Promise.all([getNetwork(), getParticipants()]);
  const pmap = new Map(participants.map((p) => [p.id, p]));
  const instById = new Map(net.institutions.map((i) => [i.id, i]));
  const partyById = new Map((net.parties || []).map((i) => [i.id, i]));
  const outerNodes = [...net.institutions, ...(net.parties || [])];
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

  const W = opts.w || 900;
  const H = opts.h || 880;
  const CX = W / 2;
  const CY = opts.cy ?? 420;
  const R_CONTACT = opts.rContact || 245;   // anel de contatos
  const R_INST = opts.rInst || 372;         // anel de instituições
  const NODE_R = opts.nodeR || 21;          // raio dos avatares
  const CENTER_R = NODE_R + 16;             // nó central
  const ORBIT_SEC = opts.orbitSeconds || 240; // duração de uma volta
  const MAX_EVIDENCE = 6;

  container.innerHTML = `
    <div class="network-scroll">
      <svg class="network-svg${opts.compact ? ' net-compact' : ''}" viewBox="0 0 ${W} ${H}" role="img"
           aria-label="Mapa de conexões: Daniel Vorcaro no centro, contatos ao redor e menções entre conversas"></svg>
    </div>
    <div class="network-tooltip" hidden></div>
    <p class="network-note">
      Menções extraídas do texto das mensagens publicadas (normalizadas, sem acento;
      ambiguidades subtraídas). Não exaustivo. Partidos (caixas âmbar) ligam-se
      aos políticos filiados por registro público, não por menção. Toque num
      contato para abrir a conversa; toque numa conexão (linha) para ver as
      mensagens que a fundamentam.
    </p>`;

  const svg = container.querySelector('.network-svg');
  const tooltip = container.querySelector('.network-tooltip');

  svgEl('defs', {}, svg);
  // roda: raios, arcos e nós giram juntos; o centro fica parado
  const orbit = svgEl('g', { class: 'net-orbit' }, svg);
  const layers = {
    edges: svgEl('g', { class: 'net-edges' }, orbit),
    hit: svgEl('g', { class: 'net-hits' }, orbit),
    nodes: svgEl('g', { class: 'net-nodes' }, orbit),
  };

  /* ---------- posições ---------- */
  const pos = new Map();
  const contacts = net.contacts;
  contacts.forEach((c, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / contacts.length;
    pos.set(c.id, { x: CX + R_CONTACT * Math.cos(a), y: CY + R_CONTACT * Math.sin(a), a });
  });
  outerNodes.forEach((inst, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * (i + 0.5)) / outerNodes.length;
    pos.set(inst.id, { x: CX + R_INST * Math.cos(a), y: CY + R_INST * Math.sin(a), a });
  });

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
    if (e.type === 'affiliation') {
      svgEl('line', {
        class: 'net-affiliation', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
        'data-edge': `affil|${e.from}|${e.to}`, 'data-nodes': `${e.from},${e.to}`,
      }, layers.edges);
      continue;
    }
    if (instById.has(e.to)) {
      svgEl('line', {
        class: 'net-mention net-mention-inst', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
        'stroke-width': 1 + Math.min(2.5, e.count * 0.5), 'data-edge': e.thread + '|' + e.from + '|' + e.to,
        'data-nodes': `${e.from},${e.to}`,
      }, layers.edges);
    } else {
      const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
      const dx = mx - CX, dy = my - CY;
      const len = Math.hypot(dx, dy) || 1;
      const k = 1 + 90 / len;
      svgEl('path', {
        class: 'net-mention net-mention-person',
        d: `M ${p1.x} ${p1.y} Q ${CX + dx * k} ${CY + dy * k} ${p2.x} ${p2.y}`,
        fill: 'none', 'stroke-width': 1.4 + Math.min(3, e.count * 0.55),
        'data-edge': e.thread + '|' + e.from + '|' + e.to, 'data-nodes': `${e.from},${e.to}`,
      }, layers.edges);
    }
  }

  /* ---------- nós com contra-rotação (conteúdo sempre em pé) ---------- */
  const spinGroup = (parent) => {
    const g = svgEl('g', { class: 'net-spin' }, parent);
    if (!reduceMotion) {
      svgEl('animateTransform', {
        attributeName: 'transform', type: 'rotate',
        from: '0', to: '-360', dur: `${ORBIT_SEC}s`, repeatCount: 'indefinite',
      }, g);
    }
    return g;
  };

  const drawContact = (c) => {
    const p = pos.get(c.id);
    const g = svgEl('g', { class: 'net-node net-contact', 'data-id': c.id, transform: `translate(${p.x},${p.y})` }, layers.nodes);
    const spin = spinGroup(g);
    const p0 = pmap.get(c.id);
    svgEl('circle', { r: NODE_R, class: 'net-avatar-bg' }, spin);
    if (p0?.photo) {
      const cp = svgEl('clipPath', { id: `netclip-${c.id}` }, svg.querySelector('defs'));
      svgEl('circle', { r: NODE_R - 1.5, cx: 0, cy: 0 }, cp);
      svgEl('image', {
        href: `public/media/people/${p0.photo}`,
        x: -(NODE_R - 1.5), y: -(NODE_R - 1.5), width: (NODE_R - 1.5) * 2, height: (NODE_R - 1.5) * 2,
        'clip-path': `url(#netclip-${c.id})`, preserveAspectRatio: 'xMidYMid slice',
      }, spin);
    } else {
      svgEl('text', { class: 'net-initials', 'text-anchor': 'middle', dy: '0.35em' }, spin).textContent = initials(c.name);
    }
    const off = NODE_R + 9;
    const lx = Math.cos(p.a) * off, ly = Math.sin(p.a) * off;
    const anchor = Math.abs(Math.cos(p.a)) < 0.3 ? 'middle' : (Math.cos(p.a) > 0 ? 'start' : 'end');
    const label = svgEl('text', { class: 'net-label', x: lx, y: ly, 'text-anchor': anchor, dy: '0.35em' }, spin);
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
      svgEl('tspan', { x: lx, dy: '-0.45em' }, label).textContent = l1;
      svgEl('tspan', { x: lx, dy: '1.15em' }, label).textContent = l2;
    } else {
      label.textContent = c.name;
    }
    return g;
  };

  const instSigla = (inst) => inst.sigla || inst.label.slice(0, 3).toUpperCase();

  const drawInstitution = (inst) => {
    const p = pos.get(inst.id);
    const isParty = partyById.has(inst.id);
    const g = svgEl('g', {
      class: `net-node net-inst${isParty ? ' net-party' : ''}`,
      'data-id': inst.id, transform: `translate(${p.x},${p.y})`,
    }, layers.nodes);
    const spin = spinGroup(g);
    const bw = NODE_R + 12, bh = NODE_R - 2;
    svgEl('rect', { x: -bw / 2, y: -bh / 2, width: bw, height: bh, rx: 5, class: 'net-inst-box' }, spin);
    svgEl('text', { class: 'net-inst-sigla', 'text-anchor': 'middle', dy: '0.35em' }, spin)
      .textContent = instSigla(inst);
    const off = NODE_R + 14;
    const anchor = Math.cos(p.a) >= 0 ? 'start' : 'end';
    svgEl('text', { class: 'net-label net-label-inst', x: Math.cos(p.a) * off, y: Math.sin(p.a) * off, 'text-anchor': anchor, dy: '0.35em' }, spin)
      .textContent = inst.label;
    return g;
  };

  for (const inst of outerNodes) drawInstitution(inst);
  for (const c of contacts) drawContact(c);

  /* ---------- centro (Vorcaro) — parado ---------- */
  const centerG = svgEl('g', { class: 'net-node net-center', 'data-id': 'daniel-vorcaro', transform: `translate(${CX},${CY})` }, svg);
  svgEl('circle', { r: CENTER_R, class: 'net-center-ring' }, centerG);
  const vPhoto = pmap.get('daniel-vorcaro')?.photo;
  if (vPhoto) {
    const cp = svgEl('clipPath', { id: 'netclip-center' }, svg.querySelector('defs'));
    svgEl('circle', { r: CENTER_R - 4, cx: 0, cy: 0 }, cp);
    svgEl('image', {
      href: `public/media/people/${vPhoto}`,
      x: -(CENTER_R - 4), y: -(CENTER_R - 4), width: (CENTER_R - 4) * 2, height: (CENTER_R - 4) * 2,
      'clip-path': 'url(#netclip-center)', preserveAspectRatio: 'xMidYMid slice',
    }, centerG);
  } else {
    svgEl('text', { class: 'net-initials net-initials-big', 'text-anchor': 'middle', dy: '0.35em' }, centerG).textContent = 'DV';
  }
  svgEl('text', { class: 'net-label net-label-center', y: CENTER_R + 18, 'text-anchor': 'middle' }, centerG)
    .textContent = net.center_name;

  /* ---------- a ciranda ---------- */
  if (!reduceMotion) {
    svgEl('animateTransform', {
      attributeName: 'transform', type: 'rotate',
      from: `0 ${CX} ${CY}`, to: `360 ${CX} ${CY}`,
      dur: `${ORBIT_SEC}s`, repeatCount: 'indefinite',
    }, orbit);
    // pausa enquanto o usuário interage — precisão de hover e clique
    svg.addEventListener('mouseenter', () => svg.pauseAnimations());
    svg.addEventListener('mouseleave', () => svg.unpauseAnimations());
    svg.addEventListener('touchstart', () => svg.pauseAnimations(), { passive: true });
    const resumeSoon = () => setTimeout(() => svg.unpauseAnimations(), 3000);
    svg.addEventListener('touchend', resumeSoon);
    svg.addEventListener('click', resumeSoon);
  }

  /* ---------- camada de clique das arestas ---------- */
  for (const e of net.edges) {
    const key = e.type === 'affiliation'
      ? `affil|${e.from}|${e.to}`
      : e.thread + '|' + e.from + '|' + e.to;
    const visual = layers.edges.querySelector(`[data-edge="${CSS.escape(key)}"]`);
    if (!visual) continue;
    const hitEl = visual.cloneNode(false);
    hitEl.setAttribute('class', 'net-hit');
    hitEl.setAttribute('stroke-width', 16);
    hitEl.setAttribute('data-edge', key);
    hitEl.removeAttribute('data-nodes');
    layers.hit.appendChild(hitEl);
  }

  /* ---------- interação ---------- */
  const allSvg = container.querySelectorAll('.net-node, .net-spoke, .net-mention');
  const nameOf = (id) => pmap.get(id)?.name || instById.get(id)?.label || id;

  let hideTimer = null;
  const showTooltip = (html, ref) => {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
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
  const scheduleHide = () => { if (hideTimer) clearTimeout(hideTimer); hideTimer = setTimeout(hideTooltip, 180); };
  tooltip.addEventListener('mouseenter', () => { if (hideTimer) clearTimeout(hideTimer); });
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

  // contatos: clique vai DIRETO para a conversa — sem modal, sem tooltip
  layers.nodes.querySelectorAll('.net-contact').forEach((node) => {
    node.addEventListener('mouseenter', () => highlight(node.dataset.id));
    node.addEventListener('mouseleave', () => highlight(null));
    node.addEventListener('click', () => {
      const c = contacts.find((x) => x.id === node.dataset.id);
      if (c) location.hash = `#/thread/${c.thread}`;
    });
  });

  // centro e instituições: resumo no hover
  svg.querySelectorAll('.net-center, .net-inst').forEach((node) => {
    node.addEventListener('mouseenter', () => {
      highlight(node.dataset.id);
      if (node.dataset.id === 'daniel-vorcaro') {
        showTooltip(`<strong>${esc(net.center_name)}</strong><br><span class="ntt-sub">Centro do arquivo — ${contacts.length} conversas publicadas</span>`, node);
      } else if (partyById.has(node.dataset.id)) {
        const party = partyById.get(node.dataset.id);
        const members = net.edges.filter((e) => e.type === 'affiliation' && e.to === node.dataset.id);
        showTooltip(`
          <strong>${esc(party.label)} (${esc(party.sigla)})</strong>
          <div class="ntt-row">Filiados neste arquivo:</div>
          ${members.map((e) => `<div class="ntt-row ntt-small">· ${esc(nameOf(e.from))}</div>`).join('')}
          <div class="ntt-small" style="margin-top:6px">Filiação: registro público (verbete da pessoa).</div>
        `, node);
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
  });

  // arestas: evidência com deep-link
  layers.hit.querySelectorAll('.net-hit').forEach((hit) => {
    const key = hit.dataset.edge;
    const edge = net.edges.find((e) => e.thread + '|' + e.from + '|' + e.to === key);
    if (!edge) return;
    const visual = layers.edges.querySelector(`[data-edge="${CSS.escape(key)}"]`);
    hit.addEventListener('mouseenter', () => {
      highlight(null);
      visual.classList.add('active');
      if (edge.type === 'affiliation') {
        showTooltip(`
          <strong>${esc(nameOf(edge.from))} → ${esc(nameOf(edge.to))}</strong>
          <div class="ntt-row">Filiação partidária</div>
          <a class="ntt-ev" href="${esc(edge.source.url)}" target="_blank" rel="noopener">Fonte: ${esc(edge.source.label)} ↗</a>
        `, hit);
        return;
      }
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

  svg.addEventListener('click', () => hideTooltip());
}
