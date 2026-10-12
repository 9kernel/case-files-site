// about.js — rota #/sobre: apresentação do projeto, legenda de proveniência e fontes.
// Era o conteúdo da home; ganhou página própria (ícone ⓘ na barra).

import { escapeHtml as esc } from '../utils.js';

export async function renderAbout(container) {
  container.innerHTML = `
  <div class="home">
    <div class="home-inner">
      <section class="hero">
        <h1>O WhatsApp de Daniel Vorcaro</h1>
        <p>Arquivo documental das conversas do celular de <strong>Daniel Vorcaro</strong>,
           ex-controlador do Banco Master, registradas em relatórios da Polícia Federal que
           integram autos públicos (pacote «Arquivos Pet 16704» do STF) e em reportagens
           jornalísticas. As conversas aparecem como no aparelho — as mensagens do banqueiro
           à direita — e cada mensagem indica <strong>exatamente de onde veio e com que grau
           de verificação</strong>. Feito para jornalistas, advogados e público geral.</p>
        <p style="margin-top:6px"><strong>Projeto independente.</strong> Não afiliado à
           Polícia Federal, ao STF, ao WhatsApp ou à Meta.</p>
      </section>

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
          <li>Estas mensagens não constituem acusação nem conclusão de culpa ou inocência; as investigações seguem em curso. Veja a <a href="#/policy">Política de correções e fontes</a>.</li>
        </ul>
      </section>

      <h2 class="section-title">Fontes</h2>
      <section class="howto">
        <ul style="list-style:disc; padding-left:20px; display:grid; gap:6px">
          <li><strong>Documentos públicos</strong> — pacote «Arquivos Pet 16704» disponibilizado pelo STF após levantamento de sigilo (10/09/2026): relatórios da PF que fundamentam as conversas marcadas como <span class="prov-badge prov-official">✓ Documento oficial</span> (<a href="https://stfjusbr.sharepoint.com/:f:/s/STI--CRCS/IgDNcXLZ-Q0SQaDPoCO8FWPyAX1MERPDqK0aWoll9fKADYc" target="_blank" rel="noopener">navegação por peça — SharePoint do STF</a>; <a href="https://docspublicos.stf.jus.br/processos-publicos/Pet16704/Pet16704.7z" target="_blank" rel="noopener">pacote completo — docspublicos.stf.jus.br</a>);</li>
          <li><a href="https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/" target="_blank" rel="noopener">piauí — “As 96 mensagens entre Flávio e Vorcaro, 90 dias antes da prisão” (01/10/2026)</a> — Ana Clara Costa, João Batista Jr. e Breno Pires;</li>
          <li><a href="https://www.terra.com.br/noticias/justica/mensagens-extraidas-do-celular-de-vorcaro-mostram-cobrancas-de-roberto-justus-por-aporte-diz-site,194f7d93247c6509ad2ce2b12e3aeb47egbsfyq7.html" target="_blank" rel="noopener">Terra / Poder360 — cobranças de Roberto Justus por aporte (02/10/2026)</a>;</li>
          <li><a href="https://www.correiobraziliense.com.br/politica/2026/10/7513807-vorcaro-disse-que-haddad-era-um-de-seus-maiores-opositores-revelam-mensagens.html" target="_blank" rel="noopener">Correio Braziliense / O Globo — “Vorcaro disse que Haddad era um de seus ‘maiores opositores’” (03/10/2026)</a> — Pedro José Borges;</li>
          <li><a href="https://guaiba.com.br/politica/mendonca-tira-sigilo-e-pf-revela-pedidos-de-vorcaro-a-moraes" target="_blank" rel="noopener">Rádio Guaíba / R7 — relatório da PF desclassificado (01/09/2026)</a> — base da conversa com Alexandre de Moraes, cujas mensagens foram localizadas no documento da PF (IPJ-A nº 3298613/2026, PET 16662/STF);</li>
          <li><a href="https://www.poder360.com.br/poder-gente/leia-as-mensagens-entre-luciano-huck-e-daniel-vorcaro/" target="_blank" rel="noopener">Poder360 — mensagens entre Luciano Huck e Vorcaro (30/09/2026)</a>;</li>
          <li><a href="https://noticias.uol.com.br/politica/ultimas-noticias/2026/09/30/mensagens-senador-do-psd-to-para-vorcaro.ghtm" target="_blank" rel="noopener">UOL / O Globo (coluna Lauro Jardim) — mensagens de Irajá a Vorcaro (30/09/2026)</a> e <a href="https://noticias.uol.com.br/politica/ultimas-noticias/2026/10/01/mensagens-vorcaro-antonio-rueda.ghtm" target="_blank" rel="noopener">cessão de aeronaves a Antonio Rueda (01/10/2026)</a>;</li>
          <li><a href="https://c-level.folha.uol.com.br/financas/2026/10/mensagens-mostram-que-campos-neto-convidou-vorcaro-para-encontro-em-casa-quando-presidia-bc.shtml" target="_blank" rel="noopener">C-Level/Folha — mensagens com Roberto Campos Neto (01/10/2026)</a>;</li>
          <li><a href="https://g1.globo.com/politica/noticia/2026/09/04/nikolas-e-vorcaro-ouca-audio-leia-transcricao-e-veja-o-que-ex-deputado-falou-sobre-as-mensagens.ghtml" target="_blank" rel="noopener">g1/GloboNews — áudio e transcrição de Nikolas Ferreira (04/09/2026)</a>;</li>
          <li><a href="https://veja.abril.com.br/brasil/mensagens-da-pf-revelam-amizade-cheia-de-aventuras-de-vorcaro-com-yasmin-brunet/" target="_blank" rel="noopener">Veja — mensagens com Yasmin Brunet (02/10/2026)</a>;</li>
          <li><a href="https://www.cnnbrasil.com.br/blogs/gustavo-uribe/politica/em-mensagem-doria-se-diz-preocupado-com-vorcaro-e-pede-conversa-reservada/" target="_blank" rel="noopener">CNN Brasil — mensagem de João Doria (05/03/2026)</a> e <a href="https://www.cnnbrasil.com.br/blogs/matheus-teixeira/politica/mensagens-apontam-relacao-de-amizade-entre-vorcaro-e-alcolumbre/" target="_blank" rel="noopener">relação com Davi Alcolumbre (25/09/2026)</a>;</li>
          <li><a href="https://jovempan.com.br/politica/tapete-vermelho-irmao-filho-de-fux-trocou-mensagens-e-participou-de-eventos-com-vorcaro/" target="_blank" rel="noopener">Jovem Pan/UOL — mensagens com Rodrigo Fux (15/09/2026)</a>;</li>
          <li><a href="https://www.cartacapital.com.br/justica/mensagens-indicam-encontro-entre-vorcaro-e-andre-mendonca-em-sao-paulo/" target="_blank" rel="noopener">CartaCapital — encontro articulado por Cezinha de Madureira (02/09/2026)</a>.</li>
        </ul>
        <p style="margin-top:8px">O botão abaixo de cada mensagem abre o painel com a
           proveniência completa e o link para a fonte.</p>
      </section>
    </div>
  </div>`;
}
