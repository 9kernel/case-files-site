// policy.js — rota #/policy: Política de correções e fontes (§27).
// Explica o compromisso de fidelidade documental, os níveis de proveniência,
// o direito de contestação e como pedir correção.

import { CONFIG } from '../config.js';
import { escapeHtml as esc } from '../utils.js';

export function renderPolicy(container) {
  const contact = CONFIG.CORRECTIONS_CONTACT;
  const contactHtml = contact
    ? `Canal de correção: <a href="mailto:${esc(contact)}">${esc(contact)}</a>`
    : `Canal de correção: <strong>a definir pelo responsável pelo projeto</strong> —
       o endereço será publicado em <code>js/config.js</code> assim que definido.`;

  container.innerHTML = `
  <div class="home">
    <div class="home-inner">
      <section class="hero">
        <h1>Política de correções e fontes</h1>
        <p>Como este arquivo organiza, verifica e corrige as informações que publica.</p>
      </section>

      <section class="howto" aria-label="Compromisso">
        <h2 class="section-title">Compromisso</h2>
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li>O projeto busca <strong>fidelidade documental</strong>: cada mensagem
              reproduz o que a fonte publicou, sem paráfrase, correção de português
              ou complemento de frases.</li>
          <li>A existência de uma mensagem no arquivo <strong>não constitui acusação,
              conclusão de culpa ou inocência</strong>, nem confirma interpretações de
              terceiros sobre o seu conteúdo.</li>
          <li>Quando o documento primário público está disponível, ele prevalece sobre
              qualquer reportagem.</li>
          <li>Nenhum horário, página, número de documento ou e-Doc é inferido ou
              estimado: o que não consta da fonte aparece como não divulgado.</li>
          <li><strong>Projeto independente. Não afiliado à Polícia Federal, ao STF,
              ao WhatsApp ou à Meta</strong> — os nomes aparecem apenas como referência
              às instituições de origem dos documentos e da plataforma reproduzida.</li>
        </ul>
      </section>

      <section class="howto" aria-label="Proveniência">
        <h2 class="section-title">Níveis de proveniência</h2>
        <p>Cada registro carrega um nível de verificação, exibido junto à mensagem:</p>
        <ul style="list-style:none; padding-left:0; display:grid; gap:8px">
          <li><span class="prov-badge prov-official">✓ Documento oficial</span> — a mensagem foi localizada no documento primário público, com página e figura citadas.</li>
          <li><span class="prov-badge prov-investigation">◉ Investigação pública</span> — o material integra procedimento público, mas a peça primária da mensagem ainda não foi localizada.</li>
          <li><span class="prov-badge prov-secondary">○ Fonte jornalística</span> — a mensagem foi publicada por reportagem; o documento primário ainda não foi localizado.</li>
          <li><span class="prov-badge prov-pending">◌ Em revisão</span> — aguarda revisão humana e não é exibido no site.</li>
        </ul>
        <p style="margin-top:8px">Os níveis não são permanentes: registros são promovidos
           <em>apenas</em> mediante evidência documental localizada.</p>
      </section>

      <section class="howto" aria-label="Correções">
        <h2 class="section-title">Correções e contestação</h2>
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li>Erros de transcrição podem ser apontados e serão conferidos contra a fonte.</li>
          <li>Pessoas citadas podem indicar <strong>erro factual</strong> ou apresentar
              <strong>fonte contraditória</strong> (inclusive o documento primário, quando
              tiver acesso).</li>
          <li>Toda correção fica <strong>registrada no histórico do repositório</strong>
              (Git) — nada é alterado silenciosamente.</li>
          <li>O projeto não determina culpa ou inocência de ninguém.</li>
        </ul>
        <p style="margin-top:10px">${contactHtml}</p>
      </section>

      <section class="howto" aria-label="Dados pessoais">
        <h2 class="section-title">Seus dados (LGPD)</h2>
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li><strong>Base da publicação:</strong> este arquivo reproduz exclusivamente
              conteúdo de peças públicas de processos no STF (levantamento de sigilo de
              10/09/2026, pacote «Arquivos Pet 16704») e reportagens com citação da fonte —
              tratamento necessário ao exercício de direitos e ao escrutínio de atos
              públicos (LGPD, art. 7º, VI e art. 11, II).</li>
          <li><strong>Minimização:</strong> dados pessoais não essenciais à compreensão
              documental (telefones, CPF, contas) nunca são publicados, mesmo quando
              constem dos originais; pessoas não investigadas citadas na narrativa
              aparecem apenas por iniciais.</li>
          <li><strong>Direitos do titular:</strong> qualquer pessoa citada pode solicitar
              <strong>acesso, correção, anonimização ou exclusão</strong> de dados pessoais
              que não sejam essenciais ao registro documental de fatos públicos, pelo canal
              oficial do projeto (divulgado abaixo assim que implantado). Resposta em até
              <strong>15 dias</strong> contados do recebimento.</li>
          <li><strong>Política link-only (07/10/2026):</strong> o projeto não redistribui
              peças dos autos — nenhuma cópia de documento é hospedada; toda leitura é
              feita na origem pública externa ou no pacote oficial do STF, por deep-link
              com a página da mensagem.</li>
        </ul>
        <p style="margin-top:10px">${contactHtml}</p>
      </section>

      <section class="howto" aria-label="Mídia">
        <h2 class="section-title">Mídia (imagens, áudios e vídeos)</h2>
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li><strong>Nenhuma mídia dos autos é publicada</strong> sem revisão
              individual — hoje o site publica zero arquivos de imagem, áudio ou
              vídeo; as conversas chegam por transcrição/citação das peças.</li>
          <li>As figuras (prints) catalogadas nos relatórios permanecem
              <em>não publicadas</em>: qualquer publicação futura exigirá revisão
              caso a caso de dados pessoais visíveis (terceiros não-envolvidos,
              menores, dados sensíveis), registro da decisão e motivação.</li>
          <li><strong>Áudios</strong> nunca são baixados ou re-hospedados: quando
              existem, são ouvidos no player da origem jornalística que os publicou
              (link externo), com a transcrição disponível devidamente atribuída.</li>
          <li>Nenhuma mídia de pessoas não-envolvidas nas conversas documentadas
              é publicada sob qualquer hipótese.</li>
        </ul>
      </section>

      <p class="howto" style="margin-top:4px">
        <a class="btn btn-ghost" href="#/">Voltar ao início</a>
      </p>
    </div>
  </div>`;
}
