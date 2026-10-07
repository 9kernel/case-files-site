# Zap do Vorcaro — arquivo documental do caso Banco Master

**https://zapdovorcaro.com/** — site estático que organiza, com **proveniência
por mensagem**, as conversas do celular de Daniel Vorcaro documentadas em
**peças públicas de processos no STF** e em **reportagens jornalísticas**.
Projeto independente, sem finalidade comercial: **não afiliado** à Polícia
Federal, ao STF, ao WhatsApp ou à Meta; sem anúncios, sem cadastro, sem
rastreadores e sem coleta de dados de visitantes.

> A existência de uma mensagem neste arquivo **não constitui acusação, conclusão
> de culpa ou de inocência**, nem confirma interpretação de terceiros — as
> investigações seguem em curso e vale a presunção de inocência (CF, art. 5º,
> LVII). Teses apresentadas pela PF em seus relatórios são identificadas como
> tese. Política completa: página **“Política de correções e fontes”** no site.

---

## 1. De onde vêm os dados

**Documentos públicos.** Após decisão de 10/09/2026 do Min. André Mendonça
(a pedido do Presidente do STF), o STF disponibilizou publicamente o pacote
**«Arquivos Pet 16704»**, com os procedimentos do caso Banco Master:

- Navegação por peça (SharePoint do STF):
  <https://stfjusbr.sharepoint.com/:f:/s/STI--CRCS/IgDNcXLZ-Q0SQaDPoCO8FWPyAX1MERPDqK0aWoll9fKADYc>
- Pacote oficial completo (.7z):
  <https://docspublicos.stf.jus.br/processos-publicos/Pet16704/Pet16704.7z>

As peças usadas como fonte primária tiveram a **publicidade confirmada contra
o pacote oficial** — por nome de arquivo, contagem de bytes e, nos casos
críticos, **SHA-256 recalculado na origem pública** (verificado em 07/10/2026):

| Peça | Processo (público) | Verificação |
|---|---|---|
| IPJ-A nº 3298613/2026 (218 fls.) | PET 16662/STF | cópia pública Poder360, SHA-256 `30e24f6d…` conferido |
| IPJ-A nº 1070759/2026 (198 fls.) | PET 15.978 (peça 3) · PET 15.556 (peça 4) | bytes idênticos na origem oficial |
| IPJ-A nº 1020625/2026 (126 fls.) | PET 15.978 (peça 4) · PET 15.556 (peça 3) | bytes idênticos na origem oficial |
| IPJ nº 1752768/2026 (117 fls.) | PET 15.978 (peça 14) | **SHA-256 recalculado na origem pública** |
| Representação PF — PET 15.499 / INQ 5.026 (238 fls.) | íntegra pública como PET 15.977, peça 2 | **SHA-256 recalculado na origem pública** |
| IPJ-A nº 1252786/2026 (228 fls.) | INQ 5026 (peça 792) | arquivo idêntico ao inventário da origem oficial |

**Reportagens.** Mensagens ainda não localizadas em peça pública primária vêm
de publicações jornalísticas, sempre citadas com link por mensagem: piauí
(“As 96 mensagens entre Flávio e Vorcaro”), Terra/Poder360, Correio
Braziliense/O Globo, R7/Rádio Guaíba e The Intercept.

**Regra inegociável**: nenhuma mensagem é publicada como “documento oficial”
apontando para peça sem `public_access_verified: true` — o CI do repositório
**rejeita o build** se isso acontecer. Nada provém de material sigiloso ou de
vazamento não oficial.

## 2. O que está no site é exatamente o que está nos autos e nas publicações

- **Citação literal, nunca paráfrase**: o texto dentro das bolhas é reproduzido
  exatamente como consta da fonte (erros de português, gírias e abreviações
  incluídos). Trechos parciais são marcados como trecho; transcrições de áudio
  declaram autoria e se são completas.
- **Cada mensagem carrega a evidência**: documento, página e — quando existe —
  figura, com deep-link direto (`PDF#page=N`) que abre a página exata da
  citação na origem pública. O botão “ver no documento” abaixo de cada mensagem
  permite conferir qualquer citação em segundos.
- **Horários e referências nunca são inventados**: o que a fonte não divulga
  aparece como “não divulgado”; na dúvida, o campo fica nulo.
- **Níveis de verificação por registro**: ✓ documento oficial (localizado na
  peça pública, com página) · ◉ investigação pública (procedimento público,
  peça específica ainda não localizada) · ○ fonte jornalística (reportagem
  citada). Promoções de nível exigem evidência documental — nunca automáticas.

**Auditorias realizadas (07/10/2026):**

- *Proveniência*: 384/384 registros verificados — toda mensagem
  `official_document` aponta para peça com publicidade confirmada; nenhum
  documento inexistente; nenhuma página faltante (relatório público:
  `PUBLIC-PROVENANCE-AUDIT.md`).
- *Fidelidade*: comparação citação-por-citação contra o texto das peças e das
  reportagens (método: extração por página + substring normalizada; figuras
  conferidas por timestamp e leitura visual): **zero divergências em 335
  mensagens**; 11 citações (em figuras/imagem ou matéria que bloqueia robôs)
  mantêm corroboração indireta registrada e pendência de leitura visual.
- **Imutável e rastreável**: mensagem nunca é editada em silêncio — toda
  alteração é um commit assinado e auditável.

## 3. Fundamento legal do projeto

Este arquivo existe e se apoia, em síntese, nos seguintes fundamentos
(enquadramento do próprio projeto; não substitui aconselhamento jurídico):

- **Constituição Federal**: liberdade de expressão, criação e informação sob
  qualquer forma (art. 5º, IX); direito à informação e acesso (art. 5º, XIV);
  direito de receber informações de interesse coletivo (art. 5º, XXXIII);
  **publicidade dos atos processuais** (art. 5º, LX e art. 93, IX); livre
  manifestação do pensamento e da informação (art. 220); presunção de
  inocência (art. 5º, LVII) — respeitada com rotulagem explícita de teses.
- **Lei de Acesso à Informação (Lei 12.527/2011)**: as peças utilizadas são
  **informações públicas**, disponibilizadas por decisão do próprio STF; a LAI
  assegura o acesso e não veda a reapresentação com citação da fonte.
- **LGPD (Lei 13.709/2018)**: o tratamento se apoia na necessidade de
  **tutela de direitos em processos judiciais** (art. 7º, VI e art. 11, II) e
  em dados **provenientes de fonte pública** (art. 12), com **minimização**
  (art. 6º, III): telefones, CPF, endereços e dados sensíveis nunca são
  publicados, mesmo quando constem dos originais; pessoas não investigadas
  citadas na narrativa aparecem apenas por iniciais. Direitos do titular e
  política de dados: página “Política de correções e fontes” no site.
- **Lei de Direitos Autorais (Lei 9.610/98)**: atos oficiais de autoridades —
  como os relatórios da PF integrantes dos autos — **não são protegidos** por
  direito autoral (art. 8º, I); trechos de reportagens aparecem como **citação
  com atribuição e link** (art. 46, VIII), sem re-hospedagem.
- **Jurisprudência do STF**: o direito ao esquecimento **não prevalece** sobre
  a publicação de **fatos verídicos de interesse público** (RE 1.010.606); a
  responsabilização de quem publica matéria de interesse público exige
  **efetivo dolo ou culpa grave** (ADPF 130).

## 4. Privacidade e minimização

Sem mídia dos autos publicada (política escrita: prints/áudios só após revisão
individual); sem fotos de pessoas; sem dados pessoais além do necessário à
compreensão documental; o projeto **não redistribui peças** (política
link-only: leitura sempre na origem pública). Correções e contestações: página
de política no site.

## 5. Verificação automatizada (CI)

Todo push roda, sem dependências externas (Node puro):

```bash
node scripts/validate.mjs data            # schema + regras editoriais (rejeita official_document sem peça pública)
node scripts/test-validate.mjs            # testa cada regra de rejeição
node scripts/audit-public-provenance.mjs  # auditoria de publicidade por registro
node scripts/check-email-leak.mjs         # impede dados pessoais em arquivos publicados
```

---

*Projeto independente. Não afiliado à Polícia Federal, ao STF, ao WhatsApp ou
à Meta. As marcas e instituições citadas aparecem apenas como referência às
fontes documentais.*
