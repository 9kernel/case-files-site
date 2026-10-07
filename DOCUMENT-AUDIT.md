# DOCUMENT-AUDIT — Auditoria documental da 2ª etapa (2026-10-06)

Versão legível por máquina: [`data/audit/document-audit.json`](data/audit/document-audit.json).

**Regra máxima aplicada em tudo abaixo**: nunca inferir o que não está
documentalmente demonstrado; a existência de uma transcrição não autoriza afirmar
que possuímos o arquivo de áudio original; reprodução jornalística de documento
oficial é registrada como `public_reproduction`, nunca como original.

---

## 1. Documentos consultados

| Documento | Papel | Hash (calculado localmente) | Acesso |
|---|---|---|---|
| **IPJ-A nº 3298613/2026** (NADIP/DFIN/CGRC/DICOR/PF, 27/08/2026, 218 fls., PET 16662/STF, Rel. Min. André Mendonça) | documento primário; base das novas extrações | `30e24f6d8abd6c033c50594ff2658a4ad72b2ac818f312ea3fe54e80a5d052d7` (5.537.944 bytes) | cópia pública do Poder360 baixada e conferida; **é reprodução jornalística do original oficial** — registrada como `copy_kind: public_reproduction` com o processo oficial linkado |
| **PET 16.662 (STF)** | processo oficial de origem | — | URL registrada (`incidente=7681133`); portal devolve 403 a cliente automatizado |
| **INQ 5.070** (único 0181367-57.2026.1.00.0000) | processo de referência (Dark Horse); alvo da busca por mídias originais | — | URL registrada (`incidente=7661993`); 403 a cliente automatizado; **peças com mídia não localizadas nesta etapa** |
| Nota à imprensa 47 do STF (~25,3 GB / ~4.000 arquivos da PET 15.556 e correlatos) | rota para mídias originais | — | acessível; download não realizado nesta etapa |
| Índices auxiliares (arkanto: Romy, Ana Matos) e catálogo novelo | **auxiliares de navegação apenas** | — | acessíveis; nenhuma publicação se baseou neles — toda citação veio do PDF primário |

Nenhum hash de terceiro foi copiado: o SHA-256 acima foi calculado localmente
após o download. Coincidência registrada: uma segunda cópia, baixada
independentemente pelo editor, produziu exatamente o mesmo hash.

## 2. Nova base após a extração

- **21 threads** (7 anteriores + **14 novas**), **206 mensagens**, **40 eventos editoriais**.
- Por nível de verificação: **103 `official_document`** · 74 `public_investigation` · 29 `secondary_source` (0 `pending_review`).
- Por natureza: 102 `verbatim` · 60 `verbatim_excerpt` · 16 `forwarded_message` · 15 `media` · 9 `call` · 4 `audio_transcript`.
- Mídia: 18 `media_reference_only` · **2 `secondary_media`** · 1 `transcript_only` · **0 `official_media`** (nenhum arquivo original localizado).

### Threads adicionadas (conversa direta demonstrada no documento)

Fábio Faria (20 msgs) · Viviane de Moraes (3) · Ana Matos (9) · Ciro Soares (24) ·
Leonardo Palhares (15) · Angelo Silva (2) · Marcos da Mata (8) · Romy (5) ·
Alberto Felix (0 msgs / 2 eventos — trecho sem citação literal) · Marcio Conjur (6) ·
Luiz Rennó (1) · Geraldo Brazil Journal (1) · Paulo Sergio (1) · Ana Claudia (1).
Todas com `verification.level = official_document`, página e figura por mensagem,
data/hora conforme o documento (horários em UTC-3) e link "ver no documento"
(`PDF#page=N`) + "abrir processo no STF" no painel de evidência.

### Reverificação da thread Moraes

As 7 referências da auditoria anterior foram **conferidas contra o PDF** (tabelas
de ações da PF): fl. 49/fig. 48 → 30/10 13:33 ✓ · fl. 61/fig. 60 → 04/11 17:41 ✓ ·
fl. 127/fig. 126 → 15/11 22:12 ✓ · fl. 129/fig. 128 → 15/11 22:28 ✓ ·
fl. 141/fig. 140 → 17/11 17:22 ✓ · fl. 143/fig. 142 → 17/11 17:26 ✓ ·
fl. 147/fig. 146 → 17/11 20:48 ✓. Nenhum texto foi alterado; cada mensagem ganhou
`source.document_id`. Dez eventos documentados foram adicionados (salvamento do
contato em 26/12/2023; as cinco mensagens de 17/11/2025 em modo de visualização
única — figs. 38-40; encontros de 2024-2025 com interlocutores privados
**minimizados**).

## 3. Áudios

| Áudio | Status | Origem | Duração | Notas |
|---|---|---|---|---|
| Flávio Bolsonaro → Vorcaro, 08/09/2025 (m-00008, thread Flávio) | **secondary_media** | player do Poder360 (link externo; Terra idem) | ~1min37s (97 s, conforme a publicação) | **PF negou publicamente ser a origem do vazamento (UOL, 21/07/2026)** — jamais rotulado como oficial; transcrição parcial da piauí mantida (`publisher_transcription`); nada re-hospedado |
| Mário Frias → Vorcaro, 11/12/2024 18:24 (m-10001, thread Frias) | **secondary_media** | player do Intercept (página 403 para bot — registrar e conferir em navegador) | não divulgada | sem transcrição publicada; sequência da reportagem adicionada como `secondary_source` ("Eu to numa ligação te chamo em seguida", "Blz", chamada ~2 min às 19:06) |
| Mário Frias → Vorcaro, 11/12/2024 18:30 (m-00004, piauí) | **transcript_only** | — | 17 s | transcrição parcial da piauí mantida como fallback |
| Fábio Faria → Vorcaro, 21/12/2023 (thread Fábio Faria) | media_reference_only | relatório da PF | — | **transcrito integralmente pela PF** (`document_transcription`, completa) |
| Ciro Soares → Vorcaro, 14/04/2024 (thread Ciro) | media_reference_only | relatório da PF | — | transcrito integralmente pela PF (`document_transcription`, completa) |

`official_media`: **nenhum** — nenhum arquivo foi localizado nos autos/pacotes
públicos do STF. Nenhuma mídia jornalística foi baixada ou re-hospedada
(regra §8); o site oferece "ouvir na origem" com link ao player do veículo.

## 4. Encaminhadas corretamente classificadas

16 mensagens `forwarded_message` com `forwarded_attribution{verified_direct_contact:
false}` — em destaque: mensagens de "Gonet" (PGR) **sempre encaminhadas por Ciro
Soares** (thread "Gonet ↔ Vorcaro" não existe e não foi criada — §17); recorte de
Viviane de Moraes encaminhado por Marcos; mensagens de "Alexandre" encaminhadas
por Fábio Faria; mensagens de interlocutor não identificado (Andrei/EPF Ana
Beatriz/Jarbas).

## 5. Privacidade e minimização (§23)

**Não publicadas**: threads de Martha Graeff (namorada — os encontros com o
ministro viraram eventos com identidade minimizada na thread Moraes), Gustavo
Motorista, Motorista Brasilia Sidney, Michael (funcionário do hotel), Stella
(filha), Thatiane Prime e Fabiano Zettel (fora das prioridades; citações
identificadas para extração futura nas fls. 24-25, 149, 171-172).

**Dados retidos**: placas de veículos, endereço do encontro de 02/02/2024,
terminais/telefones, nome da filha de Alexandre de Moraes, dados de contatos
pessoais. O PDF já traz vários desses campos ocultos na camada de texto —
mantivemos a omissão.

**Figuras sem data documental** (não publicáveis sem revisão humana): figs.
172-176 (Fábio Faria), 192-193, 196-201, 205-206 (Ana Matos), 178 (Sidney).

## 6. Divergências de duração

Nenhuma: nenhum arquivo de áudio foi baixado, logo não há duração medida
localmente para comparar (as durações exibidas vêm das publicações e estão
marcadas como tal).

## 7. URLs com problema

- `portal.stf.jus.br` (PET 16662 e INQ 5070): **403 para cliente automatizado** — conferir em navegador.
- `intercept.com.br` (áudio Frias): **403 para cliente automatizado** — conferir em navegador.

## 8. Itens para revisão humana

1. Conferir em navegador as páginas do STF e a matéria do Intercept (403 para bot).
2. Localizar as mídias originais nos pacotes públicos do STF (nota 47) para
   promover `secondary_media → official_media` — nunca automático.
3. Datar as figuras sem data documental (seção 5) se revisão humana o permitir.
4. Identidade civil de "Marcio Conjur" e de "Fábio Faria" não está estabelecida
   no documento — **não inferir**.
5. Possível identidade entre "Angelo Silva" (contato) e "Angelo Antonio Ribeiro
   da Silva" (assinante do contrato, fl. 34) **não foi afirmada** pelo relatório.
6. As notas de Vorcaro (figs. 208-210) citam "Andrei" e "Paulo": o próprio
   relatório diz que **podem indicar** Andrei Passos (DG/PF) e Paulo Gonet (PGR) —
   mantida a formulação condicional do documento.

## 9. Resultado dos testes

`validate.mjs`: **0 erros / 0 warnings** (21 threads, 206 mensagens, 40 eventos).
`test-validate.mjs`: **100 casos verdes**, incluindo as 10 regras de mídia do §35.
