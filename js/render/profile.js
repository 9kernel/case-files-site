// profile.js — card de perfil do contato (estilo "info do contato" do WhatsApp).
// Aberto ao clicar no avatar na lista de conversas ou no cabeçalho da conversa.
// Todos os dados vêm de data/participants.json (campo opcional profile_sources).

import { escapeHtml as esc, initials, hashHue } from '../utils.js';

export function openProfileDialog(participant) {
  if (!participant) return;
  const dlg = document.getElementById('profile-dialog');
  if (!dlg) return;
  wireProfileDialog();

  const avatar = dlg.querySelector('#pf-avatar');
  avatar.textContent = initials(participant.name);
  avatar.style.setProperty('--av-color', `hsl(${hashHue(participant.id)}, 38%, 42%)`);

  dlg.querySelector('#pf-name').textContent = participant.name || participant.id;
  dlg.querySelector('#pf-role').textContent = participant.role || '';

  const aliases = dlg.querySelector('#pf-aliases');
  const aliasList = participant.aliases || [];
  if (aliasList.length) {
    aliases.hidden = false;
    aliases.textContent = `Também registrado como: ${aliasList.join(', ')}`;
  } else {
    aliases.hidden = true;
  }

  dlg.querySelector('#pf-summary').textContent = participant.summary || '';

  const sources = participant.profile_sources || [];
  const ul = dlg.querySelector('#pf-sources');
  ul.innerHTML = sources
    .map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a></li>`)
    .join('');
  dlg.querySelector('#pf-sources-empty').hidden = sources.length > 0;

  dlg.showModal();
}

export function wireProfileDialog() {
  const dlg = document.getElementById('profile-dialog');
  if (!dlg || dlg.dataset.wired) return;
  dlg.dataset.wired = '1';
  dlg.querySelector('#pf-close').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', (e) => {
    if (e.target === dlg) dlg.close();
  });
}
