// home.js — rota #/: aviso editorial, destaques, níveis de proveniência e
// orientações de citação.

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
        <span class="hl-meta">${t.message_count ?? 0} mensagens publicadas · ${esc(t.source?.document || '')}</span>
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
           e cada mensagem indica <strong>exatamente de onde veio e com que grau de
           verificação</strong>. Feito para jornalistas, advogados e público geral.</p>
      </section>

      <section class="notice" aria-label="Aviso editorial">
        <strong>Aviso editorial</strong>
        Conteúdo reproduzido de <strong>documentos públicos e reportagens jornalísticas</strong>
        que publicaram trechos da extração forense da PF. A existência de uma mensagem neste
        arquivo <strong>não constitui acusação, conclusão de culpa ou confirmação de
        interpretação de terceiros</strong>; as investigações seguem em curso.
        Última atualização: ${esc(formatDateLong(CONFIG.LAST_UPDATED))}.
        <a href="#/policy">Política de correções e fontes</a>.
      </section>

      ${
        cards
          ? `<h2 class="section-title">Destaques</h2><div class="cards-grid">${cards}</div>`
          : ''
      }

      <h2 class="section-title">Como ler este arquivo</h2>
      <section class="howto">
        <ul style="list-style:none; padding-left:0; display:grid; gap:8px">
          <li><span class="prov-badge prov-official">✓ Documento oficial</span> — mensagem localizada no documento primário público (página e figura citadas).</li>
          <li><span class="prov-badge prov-investigation">◉ Investigação pública</span> — material de procedimento público; peça primária da mensagem ainda não localizada.</li>
          <li><span class="prov-badge prov-secondary">○ Fonte jornalística</span> — mensagem publicada por reportagem; documento primário ainda não localizado.</li>
        </ul>
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px; margin-top:10px">
          <li><strong>Trecho da mensagem</strong> marca citação parcial — nunca fingimos ter a mensagem completa.</li>
          <li><strong>Transcrição parcial de áudio</strong> marca transcrições incompletas de áudios.</li>
          <li><strong>Notas editoriais</strong> (contexto atribuído pelas fontes) aparecem sempre <em>fora</em> da bolha de mensagem — nunca dentro da fala de alguém.</li>
          <li><strong>Horários nunca são estimados</strong>: quando a fonte não divulga, exibimos “horário não divulgado”.</li>
        </ul>
      </section>

      <h2 class="section-title">Fontes</h2>
      <section class="howto">
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li><a href="https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/" target="_blank" rel="noopener">piauí — “As 96 mensagens entre Flávio e Vorcaro, 90 dias antes da prisão” (01/10/2026)</a> — Ana Clara Costa, João Batista Jr. e Breno Pires;</li>
          <li><a href="https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html" target="_blank" rel="noopener">Terra / Poder360 — cobranças de Roberto Justus por aporte (02/10/2026)</a>;</li>
          <li><a href="https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html" target="_blank" rel="noopener">Correio Braziliense / O Globo — “Vorcaro disse que Haddad era um de seus ‘maiores opositores’” (03/10/2026)</a> — Pedro José Borges.</li>
          <li><a href="https://guaiba.com.br/politica/mendonca-tira-sigilo-e-pf-revela-pedidos-de-vorcaro-a-moraes" target="_blank" rel="noopener">Rádio Guaíba / R7 — relatório da PF desclassificado (01/09/2026)</a> — base da conversa com Alexandre de Moraes, cujas mensagens foram localizadas no documento da PF (IPJ-A nº 3298613/2026, PET 16662/STF).</li>
        </ul>
        <p style="margin-top:8px">O botão abaixo de cada mensagem abre o painel com a
           proveniência completa e o link para a fonte.</p>
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
    </div>
  </div>`;
}
