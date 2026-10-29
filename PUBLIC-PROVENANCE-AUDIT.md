# PUBLIC-PROVENANCE-AUDIT — Auditoria de publicidade e proveniência por mensagem

Gerado por `scripts/audit-public-provenance.mjs` em **2026-10-29**.
Versão legível por máquina: [`data/audit/public-provenance-audit.json`](data/audit/public-provenance-audit.json).

Regra máxima: a força da afirmação do site nunca pode ser maior que a força da
evidência documental. `official_document` exige peça com `public_access_verified = true`.

`OK_PUBLIC_INVESTIGATION` exige, por registro, procedimento público declarado (ou
referência documental identificável) E fonte jornalística registrada. A peça primária
individual permanece NÃO localizada nesse nível: o OK certifica a estrutura da
proveniência — ausência de conflito e base declarada — e não autentica
individualmente cada mensagem. Registros sem base ou sem fonte viram
`INV_NO_BASIS`/`INV_NO_PRESS_SOURCE`.

## Resultado

- 68 threads · 1355 registros (1106 mensagens + 249 eventos)
- **1355 OK** · **0 com problema**

| Categoria | Registros |
|---|---|
| OK_OFFICIAL | 275 |
| OK_PUBLIC_INVESTIGATION | 829 |
| OK_SECONDARY | 251 |
| INV_NO_BASIS | 0 |
| INV_NO_PRESS_SOURCE | 0 |
| INVALID_OFFICIAL_DOCUMENT | 0 |
| MISSING_DOCUMENT | 0 |
| MISSING_PAGE | 0 |
| PUBLIC_ACCESS_UNKNOWN | 0 |
| SOURCE_CONFLICT | 0 |

## Documentos e publicidade

| Documento | Processo | e-Doc/peça | Publicidade | Mensagens | Eventos |
|---|---|---|---|---|---|
| `pf-ipja-3298613-2026` | PET 16662 | — | **confirmada** (2026-09-01) | 103 | 36 |
| `stf-inq-5070` | INQ 5070 | — | desconhecida (null) | 0 | 0 |
| `pf-ipja-1070759-2026` | PET 15978 | 3 | **confirmada** (2026-09-15) | 1 | 0 |
| `pf-ipja-1020625-2026` | PET 15978 | 4 | **confirmada** (2026-09-15) | 98 | 5 |
| `pf-ipj-1752768-2026` | PET 15978 | 14 | **confirmada** (2026-09-15) | 0 | 0 |
| `pf-repr-pet15-499` | PET 15499 · INQ 5026 | — | **confirmada** (2026-09-15) | 10 | 0 |
| `pf-ipja-1252786-2026` | INQ 5026 | 792 | **confirmada** (2026-09-15) | 18 | 3 |
| `pf-nota-imprensa-20261009` | — | — | **confirmada** (2026-10-16) | 0 | 1 |

## Registros com problema

**Nenhum.** Toda mensagem `official_document` aponta para peça com publicidade
confirmada; nenhum `pending_review` visível; nenhuma fonte em conflito;
nenhum `public_investigation` sem procedimento declarado e fonte jornalística.

