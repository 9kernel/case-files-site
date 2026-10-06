// home.js — rota #/: aviso editorial, destaques e orientações de citação.

import { CONFIG } from '../config.js';
import { getThreadIndex } from '../api.js';
import { escapeHtml as esc, formatDateLong } from '../utils.js';

export async function renderHome(container) {
  let featured = [];
  try {
    featured = (await getThreadIndex()).filter((t) => t.featured);
  } catch {
    featured = [];
  }

  const cards = featured
    .map(
      (t) => `<a class="hl-card" href="#/thread/${esc(t.id)}">
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.note || t.source?.pages || '')}</p>
        <span class="hl-meta">${t.message_count ?? 0} mensagens publicadas · ${esc(t.source?.document || '')} · ${esc(t.source?.pages || '')}</span>
      </a>`
    )
    .join('');

  container.innerHTML = `
  <div class="home">
    <div class="home-inner">
      <section class="hero">
        <h1>O WhatsApp de Daniel Vorcaro</h1>
        <p>Réplica de navegação das conversas do celular de <strong>Daniel Vorcaro</strong>,
           ex-controlador do Banco Master, extraídas pela Polícia Federal em 18/11/2025.
           As conversas aparecem como no aparelho — as mensagens do banqueiro à direita —
           e cada mensagem aponta <strong>exatamente de onde foi retirada</strong>.
           Feito para jornalistas, advogados e público geral.</p>
      </section>

      <section class="notice" aria-label="Aviso editorial">
        <strong>Aviso editorial</strong>
        Conteúdo reproduzido fielmente de <strong>reportagens jornalísticas</strong> que publicaram
        trechos da extração forense da PF — <em>não</em> temos acesso aos autos originais.
        Última atualização: ${esc(formatDateLong(CONFIG.LAST_UPDATED))}.
        O texto entre [colchetes] é conectivo editorial; “…” indica corte na citação; horários não
        divulgados pela reportagem aparecem como 12:00. Estas mensagens <strong>não constituem
        conclusão de culpa ou inocência</strong>: as investigações seguem em curso e as partes citadas
        podem apresentar contestações.
      </section>

      ${
        cards
          ? `<h2 class="section-title">Destaques</h2><div class="cards-grid">${cards}</div>`
          : ''
      }

      <h2 class="section-title">Fontes</h2>
      <section class="howto">
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li><a href="https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/" target="_blank" rel="noopener">piauí — “As 96 mensagens entre Flávio e Vorcaro, 90 dias antes da prisão” (01/10/2026)</a> — Ana Clara Costa, João Batista Jr. e Breno Pires;</li>
          <li><a href="https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html" target="_blank" rel="noopener">Terra / Poder360 — cobranças de Roberto Justus por aporte (02/10/2026)</a>;</li>
          <li><a href="https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html" target="_blank" rel="noopener">Correio Braziliense / O Globo — “Vorcaro disse que Haddad era um de seus ‘maiores opositores’” (03/10/2026)</a> — Pedro José Borges.</li>
        </ul>
        <p style="margin-top:8px">A referência de cada mensagem abre, no botão abaixo da bolha, o
        diálogo com a reportagem de origem e o link para o texto completo.</p>
      </section>

      <h2 class="section-title">Como citar</h2>
      <section class="howto">
        <p>Em cada mensagem há dois botões:</p>
        <ol>
          <li><strong>Copiar link</strong> — deep-link direto da mensagem
              (ex.: <code>#/thread/flavio-bolsonaro-daniel-vorcaro/m-00024</code>);</li>
          <li><strong>Copiar citação</strong> — no formato
              <code>Banco Master — piauí, 01/10/2026, msg m-00024</code>.</li>
        </ol>
      </section>

      <h2 class="section-title">Regras editoriais</h2>
      <section class="howto">
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li>Só transcrição fiel do que a reportagem publicou: proibido parafrasear, resumir ou "corrigir" os diálogos.</li>
          <li>[Colchetes] marcam palavras nossas usadas apenas como conectivo; “…” marca corte na citação.</li>
          <li>Só material de fonte pública (reportagens identificadas), sempre com <code>source_ref</code> e link.</li>
          <li>Nomes citados constam das reportagens publicadas; nada é inferido ou completado.</li>
          <li>Mensagens <code>pending-review</code> não são publicadas até revisão humana.</li>
        </ul>
      </section>
    </div>
  </div>`;
}
