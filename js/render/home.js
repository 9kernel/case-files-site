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
        <h1>${esc(CONFIG.CASE_NAME)}</h1>
        <p>Navegação cronológica dos diálogos divulgados publicamente nos autos,
           no formato original das conversas. Feito para jornalistas, advogados
           e público geral — sem paraphrase, sem resumo: só transcrição fiel
           com a fonte de cada mensagem.</p>
      </section>

      <section class="notice" aria-label="Aviso editorial">
        <strong>Aviso editorial</strong>
        Conteúdo reproduzido fielmente de documentos públicos.
        Última atualização: ${esc(formatDateLong(CONFIG.LAST_UPDATED))}.
        Cada mensagem exibe sua referência de origem (documento e folha).
        Instalação de demonstração: as conversas deste scaffold são
        <em>fictícias</em> e servem apenas para validar a ferramenta.
      </section>

      ${
        cards
          ? `<h2 class="section-title">Destaques</h2><div class="cards-grid">${cards}</div>`
          : ''
      }

      <h2 class="section-title">Como citar</h2>
      <section class="howto">
        <p>Em cada mensagem há dois botões:</p>
        <ol>
          <li><strong>Copiar link</strong> — deep-link direto da mensagem
              (ex.: <code>#/thread/grupo-comite-executivo/m-00014</code>);</li>
          <li><strong>Copiar citação</strong> — no formato
              <code>${esc(CONFIG.CASE_NAME)} — ${esc(CONFIG.PROCESS_LABEL)}, fl. 123, msg m-00014</code>.</li>
        </ol>
        <p style="margin-top:8px">A fonte completa (documento e folha) abre no botão
        de referência abaixo de cada bolha, com link para o documento original em
        <a href="${esc(CONFIG.SOURCE_URL)}" target="_blank" rel="noopener">${esc(CONFIG.SOURCE_URL)}</a>.</p>
      </section>

      <h2 class="section-title">Regras editoriais</h2>
      <section class="howto">
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li>Só transcrição fiel: proibido parafrasear, resumir ou "corrigir" os diálogos.</li>
          <li>Só material de fonte pública/oficial, sempre com <code>source_ref</code>.</li>
          <li>Nomes de pessoas privadas apenas se constarem nos documentos públicos.</li>
          <li>Mensagens <code>pending-review</code> não são publicadas até revisão humana.</li>
        </ul>
      </section>
    </div>
  </div>`;
}
