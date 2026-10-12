// home.js — rota #/: lista de conversas em destaque; a apresentação do projeto
// mora em #/sobre (ícone ⓘ na barra) e o mapa de conexões em #/conexoes.
// Aqui ficam só um lembrete mínimo de como usar o arquivo.

export async function renderHome(container) {
  container.innerHTML = `
  <div class="home-empty">
    <svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
    <h2>Zap do Vorcaro</h2>
    <p>Selecione uma conversa para ler as mensagens — cada uma mostra
       a fonte e o grau de verificação.</p>
    <div class="home-empty-actions">
      <a class="btn btn-primary" href="#/sobre">Sobre o projeto</a>
      <a class="btn btn-ghost" href="#/conexoes">Mapa de conexões</a>
    </div>
  </div>`;
}
