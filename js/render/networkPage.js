// networkPage.js — rota #/conexoes: mapa de conexões em página própria,
// em tela cheia, seguido da lista completa de conexões com evidência.

import { getNetwork, getParticipants } from '../api.js';
import { renderNetwork } from './network.js';
import { escapeHtml as esc } from '../utils.js';

const fmtDate = (d) => (d ? `${d.slice(8, 10)}/${d.slice(5, 7)}/${d.slice(0, 4)}` : 's/ data');

export async function renderNetworkPage(container) {
  const [net, participants] = await Promise.all([getNetwork(), getParticipants()]);
  const pmap = new Map(participants.map((p) => [p.id, p]));
  const instById = new Map(net.institutions.map((i) => [i.id, i]));
  const contactById = new Map(net.contacts.map((c) => [c.id, c]));
  const nameOf = (id) => pmap.get(id)?.name || instById.get(id)?.label || id;

  container.innerHTML = `
  <div class="home">
    <div class="home-inner network-page">
      <section class="hero">
        <h1>Mapa de conexões</h1>
        <p>Daniel Vorcaro no centro, com as ${net.contacts.length} conversas publicadas ao redor.
           <strong>Arcos verdes</strong> ligam pessoas citadas em conversas de outras pessoas;
           <strong>linhas tracejadas</strong> ligam conversas às instituições mencionadas
           (BC, STF, PF, FGC…); a espessura dos raios cinzas acompanha o volume de mensagens.
           Passe o mouse (ou toque) para destacar; clique numa conexão para ver as mensagens
           que a fundamentam, com link direto para cada uma.</p>
      </section>

      <div class="network-wrap" id="netpage-wrap">
        <div id="netpage-mount"></div>
      </div>

      <h2 class="section-title">Todas as conexões registradas</h2>
      <p class="network-note" style="margin-top:0">
        ${net.edges.length} conexões extraídas do texto das mensagens publicadas — cada uma com a
        mensagem de origem. Menções ambíguas são descartadas na extração (ex.: “Moraes” dentro de
        “Viviane de Moraes” não conta).
      </p>
      <ul class="netpage-list" id="netpage-list"></ul>
    </div>
  </div>`;

  const mount = container.querySelector('#netpage-mount');
  await renderNetwork(mount, { w: 1160, h: 1010, cy: 470, rContact: 312, rInst: 466 });

  const personEdges = net.edges.filter((e) => !instById.has(e.to));
  const instEdges = net.edges.filter((e) => instById.has(e.to));
  const ul = container.querySelector('#netpage-list');

  const item = (e) => {
    const contact = contactById.get(e.from);
    const evs = e.evidence.map((v) =>
      `<a class="ntt-ev" href="#/thread/${esc(e.thread)}/${esc(v.id)}">${fmtDate(v.date)} · ${esc(nameOf(v.sender))} — ver mensagem</a>`
    ).join('');
    return `<li class="netpage-item">
      <div class="netpage-head">
        <span class="netpage-names"><strong>${esc(nameOf(e.from))}</strong>
          <span class="netpage-arrow">→</span> <strong>${esc(nameOf(e.to))}</strong></span>
        <span class="badge-count">${e.count}</span>
      </div>
      <div class="netpage-thread">citado na conversa com ${esc(contact?.name || '')}</div>
      <div class="netpage-evs">${evs}</div>
    </li>`;
  };

  ul.innerHTML = `
    ${personEdges.length ? `<li class="netpage-sep">Entre pessoas</li>` : ''}
    ${personEdges.map(item).join('')}
    ${instEdges.length ? `<li class="netpage-sep">Com instituições</li>` : ''}
    ${instEdges.map(item).join('')}`;
}
