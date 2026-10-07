// config.js — constantes editoriais do site.
// Ao adaptar o scaffold para um caso real, troque TODOS os valores abaixo.
export const CONFIG = Object.freeze({
  CASE_NAME: 'Banco Master',
  PROCESS_LABEL: 'Operação Compliance Zero (PF)',
  SITE_TITLE: 'Zap do Vorcaro',
  // Título da home (aba do navegador) — a visão "WhatsApp de Vorcaro".
  HOME_TITLE: 'O WhatsApp de Daniel Vorcaro',
  // Atualizar a cada publicação (formato ISO; exibido em pt-BR na home).
  LAST_UPDATED: '2026-10-07',
  // Fonte principal do material publicado até agora.
  SOURCE_URL: 'https://piaui.uol.com.br/web/mensagens-celular-flavio-vorcaro/',
  // Quantidade de mensagens renderizadas por chunk (renderização progressiva).
  CHUNK_SIZE: 100,
  // Canal de correções exibido na página "Política de correções e fontes"
  // (#/policy) — canal oficial do projeto para contestação e direitos do
  // titular (LGPD art. 18). Mantido null até a caixa/redireção existir de
  // fato (correcoes@zapdovorcaro.com no provedor do domínio): publicar um
  // canal que não recebe e-mail é agravante, não mitigação. Quando criar a
  // caixa, basta preencher aqui e publicar.
  CORRECTIONS_CONTACT: null,
});
