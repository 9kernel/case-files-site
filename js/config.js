// config.js — constantes editoriais do site.
// Ao adaptar o scaffold para um caso real, troque TODOS os valores abaixo.
export const CONFIG = Object.freeze({
  CASE_NAME: 'Banco Master',
  PROCESS_LABEL: 'Operação Compliance Zero (PF)',
  SITE_TITLE: 'Arquivo Público de Diálogos',
  // Título da home (aba do navegador) — a visão "WhatsApp de Vorcaro".
  HOME_TITLE: 'O WhatsApp de Daniel Vorcaro',
  // Atualizar a cada publicação (formato ISO; exibido em pt-BR na home).
  LAST_UPDATED: '2026-10-06',
  // Fonte principal do material publicado até agora.
  SOURCE_URL: 'https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/',
  // URL do repositório (usada na home e no README).
  REPO_URL: 'https://github.com/usuario/case-files-site',
  // Quantidade de mensagens renderizadas por chunk (renderização progressiva).
  CHUNK_SIZE: 100,
  // Canal de correções exibido na página "Política de correções e fontes"
  // (#/policy). PLACEHOLDER: não inventar e-mail — preencher quando o
  // responsável definir o canal (ex.: 'correcoes@exemplo.org').
  CORRECTIONS_CONTACT: null,
});
