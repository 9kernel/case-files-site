# PF-MASS-IMPORT-REPORT — Relatório consolidado da importação em massa

Gerado pelo pipeline `scripts/import_pipeline/`.
Estado em: **2026-10-07** (após verificação de publicidade). Números reais, medidos dos arquivos.

## 1. Inventário

Acervo processado pelo pipeline: **5 PDFs concluídos (~84 MB)** na rodada inicial
(+ pacote «Arquivos Pet 16704» do STF nas rodadas seguintes). O pipeline é
incremental: novos arquivos entram nos próximos lotes automaticamente (comando
de retomada na seção 16).

## 2. Publicidade das peças (VERIFICADA em 07/10/2026)

Todas as peças abaixo tiveram publicidade **confirmada contra o pacote público
«Arquivos Pet 16704» do STF** (levantamento de sigilo decidido em 10/09/2026
pelo Min. André Mendonça a pedido do Presidente Fachin; pacote documentado
publicamente em 15/09/2026). A verificação compara bytes e, nos casos críticos,
SHA-256 recalculado na origem pública — ver detalhes em
[`DOCUMENT-AUDIT.md`](DOCUMENT-AUDIT.md) e
[`PUBLIC-PROVENANCE-AUDIT.md`](PUBLIC-PROVENANCE-AUDIT.md).

| Documento | Processo | e-Doc/peça | Publicidade | Fonte da publicidade | Mensagens publicadas |
|---|---|---|---|---|---|
| `pf-ipja-3298613-2026` (IPJ-A nº 3298613/2026, 218 fls.) | PET 16662/STF | — | **confirmada** (01/09/2026) | Levantamento de sigilo STF (PET 16.662) + cópia pública Poder360 (hash conferido) | 103 (+35 eventos) |
| `pf-ipja-1070759-2026` (IPJ-A nº 1070759/2026, 198 fls.) | PET 15.978 (também anexada à PET 15.556 e correlatas) | peça 3 (PET 15.978) | **confirmada** (15/09/2026) | Pacote público «Arquivos Pet 16704» — pasta Pet15978 (bytes idênticos); pasta Pet 15556 (arquivo de nome idêntico ao inventário local) | 1 |
| `pf-ipja-1020625-2026` (IPJ-A nº 1020625/2026, 126 fls.) | PET 15.978 (também PET 15.499, PET 15.556 e correlatas) | peça 4 (PET 15.978) | **confirmada** (15/09/2026) | Pacote público «Arquivos Pet 16704» — pasta Pet15978 (bytes idênticos); Pet15499 peça 2, Pet 15556 peça 3 (arquivo idêntico) | 98 (+5 eventos) |
| `pf-ipj-1752768-2026` (IPJ nº 1752768/2026, 117 fls.) | PET 15.978 (e PETs 15.976/15.977/16.019) | peça 14 (PET 15.978) | **confirmada** (15/09/2026) | Pacote público «Arquivos Pet 16704» — pasta Pet15978, peça 14: **SHA-256 idêntico, recalculado na origem pública em 07/10/2026** | 0 (sem conteúdo importado) |
| `pf-repr-pet15-499` (Representação PF, 238 fls.) | PET 15.499 / INQ 5.026 | — (na PET 15.499); peça 2 da PET 15.977 | **confirmada** (15/09/2026) | Pacote público «Arquivos Pet 16704» — pasta Pet15977, peça 2: **SHA-256 idêntico, recalculado na origem pública em 07/10/2026**. A pasta pública da PET 15.499 (72 peças) não contém este PDF como arquivo discreto. | 12 |
| `pf-ipja-1252786-2026` (IPJ-A nº 1252786/2026, 228 fls.) | INQ 5.026 (também PETs 15771/15772/15773, peça 10) | peça 792 (INQ 5.026) | **confirmada** (15/09/2026) | Pacote público «Arquivos Pet 16704» — pasta Inq 5026 (arquivo de nome idêntico ao inventário local, bytes idênticos) | 18 (+3 eventos) |

Correções de registro aplicadas nesta verificação: a associação anterior do
IPJ 1752768 à «PET 15.562» não se sustentou (a peça não consta da pasta pública
dessa petição) e a do IPJ-A 1252786 ao «pacote OneDrive da Pet 16704» foi
reescrita — a Pet 16704 é o veículo oficial de disponibilização; o processo de
vinculação é o INQ 5.026 (tentativa de compra do Banco Master pelo BRB).

## 3–7. Extração (números reais do batch-0002)

- **753 citações literais candidatas** (aspas na narrativa policial), sendo
  **43 com remetente + data + hora documentados na vizinhança** e 83 com
  remetente + data.
- **189 eventos narrativos com timestamp** ("No dia X, às H, …").
- **2.239 referências de mídia**: 1.633 imagens embutidas (prints), 603
  referências a figuras, 3 referências a arquivos de áudio (UUIDs `.opus`
  citados no texto — **sem anexos embutidos nos PDFs**).
- Erros de processamento: **0**.

## 8. Fontes oficiais

Registro público central em `data/documents.json`: cada peça agora traz o
campo estruturado `public_access_verified` (+ `public_access_date`,
`public_access_basis`, `edoc`, `public_locations`, URLs oficiais do processo).
`copy_kind` continua honesto (a cópia do Poder360 é `public_reproduction`,
nunca `official_pdf_url`).

## 9–10. Áudios, imagens e vídeos

Nenhum arquivo de áudio/vídeo anexado aos PDFs (verificado no catálogo de
anexos de todos os 5). As 3 referências a `.opus` e as 1.633 imagens estão
catalogadas em `data/review/candidate_media.json` com página e referência —
extração de bytes e eventual publicação (com redação de dados pessoais)
exigem revisão e autorização.

## 11–12. Duplicatas e problemas documentais

Deduplicação intra-documento ativa (mesma citação na mesma página = 1
ocorrência). Divergências entre documentos ficam visíveis para revisão —
ocorrências por página são mantidas separadas por design.

## 13–14. Privacidade e itens aguardando revisão

Candidatos permanecem em `data/review/` (gitignored). Dados pessoais de
terceiros (telefone, CPF) encontrados em notas editoriais foram redigidos
em 07/10/2026 (ver `CORRECTION-AUDIT-2026-10-07.md`). Perfis de pessoas
privadas em `data/participants.json` revisados e minimizados.

## 15. Testes

`node scripts/validate.mjs data` → OK (25 threads, 335 mensagens, 48 eventos,
0 erros) · `node scripts/test-validate.mjs` → **114 casos OK** (inclui as
regras novas de publicidade) · `node scripts/audit-public-provenance.mjs` →
**383/383 registros OK** · `node scripts/check-email-leak.mjs` → OK.

## 16. Próximos lotes / retomada

```
python -m scripts.import_pipeline.batch --docs 30
```

Idempotente e incremental: indexa arquivos novos de `pdf_pf/`, pula os já
processados, retoma do último checkpoint (`.pipeline/import.db`).
