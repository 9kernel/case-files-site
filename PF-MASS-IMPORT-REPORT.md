# PF-MASS-IMPORT-REPORT — Relatório consolidado da importação em massa

Gerado pelo pipeline `scripts/import_pipeline/` (branch `import/pf-mass`).
Estado em: **2026-10-07**. Números reais, medidos dos arquivos.

## 1. Inventário

Acervo em `pdf_pf/` no momento do relatório: **5 PDFs concluídos (~84 MB) +
2 downloads em andamento (.crdownload, ignorados pelo pipeline até
concluírem)**. O pipeline é incremental: novos arquivos entram nos próximos
lotes automaticamente (comando de retomada na seção 16).

| doc_id | peça | págs. | publicidade | status |
|---|---|---|---|---|
| `pf-ipja-3298613-2026` | IPJ-A nº 3298613/2026 (NADIP/DFIN) | 218 | **verificada** (cópia pública Poder360, hash confere com `documents.json`) | extracted |
| `pf-ipja-1070759-2026` | IPJ-A nº 1070759/2026 (NADIP/DFIN — análise do celular de Vorcaro) | 198 | pendente de verificação | extracted |
| `pf-ipja-1020625-2026` | IPJ-A nº 1020625/2026 (NADIP/DFIN — material apreendido) | 126 | pendente de verificação | extracted |
| `pf-ipj-1752768-2026` | IPJ nº 1752768/2026 (CINQ/DICOR — Compliance Zero 3, laudo SETEC 8381/2026) | 117 | pendente de verificação | extracted |
| `pf-repr-pet15-499` | Representação PF ao STF (Min. Mendonça — PET 15.499 / INQ 5.026) | 238 | pendente de verificação | extracted |

**897 páginas** processadas. As 4 peças novas exibem carimbo
"DOCUMENTO SIGILOSO": enquanto não houver confirmação da situação de
publicidade, **nenhum conteúdo delas entra na versão pública do site**
(missão §24) — ficam em `data/review/` (gitignored).

## 2. Documentos processados

Lotes executados: `batch-0001` (61,9s, descoberta completa) e `batch-0002`
(re-extração com janela de parágrafo, 1,1s com cache). Detalhes por lote em
`BATCH-0001.md` / `BATCH-0002.md`.

## 3–7. Extração (números reais do batch-0002)

- **753 citações literais candidatas** (aspas na narrativa policial),
  sendo **43 com remetente + data + hora documentados na vizinhança** e
  83 com remetente + data.
- **189 eventos narrativos com timestamp** ("No dia X, às H, …").
- **2.239 referências de mídia**: 1.633 imagens embutidas (prints),
  603 referências a figuras, 3 referências a arquivos de áudio
  (UUIDs `.opus` citados no texto — **sem anexos embutidos nos PDFs**).
- Mensagens importadas para o site: **0** (bloqueio de publicidade, §24).
- Erros de processamento: **0**.

## 8. Fontes oficiais

Registro público central em `data/documents.json` (inalterado neste lote:
IPJ-A 3298613 + INQ 5070). As peças novas só entram aí quando a publicidade
for verificada, com `copy_kind` honesto (nunca `official_pdf_url` apontando
para rehost jornalístico).

## 9–10. Áudios, imagens e vídeos

Nenhum arquivo de áudio/vídeo anexado aos PDFs (verificado no catálogo de
anexos de todos os 5). As 3 referências a `.opus` e as 1.633 imagens estão
catalogadas em `data/review/candidate_media.json` com página e referência —
extração de bytes e eventual publicação (com redação de dados pessoais,
§16) exigem revisão e autorização.

## 11–12. Duplicatas e problemas documentais

Deduplicação intra-documento ativa (mesma citação na mesma página = 1
ocorrência). Divergências entre documentos (a mesma mensagem citada em
peças distintas) ficam visíveis para revisão — as ocorrências por página
são mantidas separadas por design (§11).

## 13–14. Privacidade e itens aguardando revisão

Tudo que vem das 4 peças novas está em `data/review/` (gitignored):
`candidate_messages.json`, `candidate_events.json`, `candidate_media.json`.
Revisão humana: (a) confirmar publicidade de cada peça; (b) conferir
citações no documento; (c) definir remetente/thread; (d) só então marcar
`"approved": true` + `"target"` e rodar o importer (entra como
`pending_review`, fora da renderização pública).

## 15. Testes

`node scripts/validate.mjs data` → OK (21 threads, 206 mensagens, 40
eventos, 0 erros) e `node scripts/test-validate.mjs` → 100 casos OK,
após cada lote. Visualizador documental verificado no navegador (desktop
e mobile): abertura pela evidência, sincronização página/figura na
seleção de mensagem, fechamento por botão/ESC/troca de conversa.

## 16. Próximos lotes / retomada

```
python -m scripts.import_pipeline.batch --docs 30
```

Idempotente e incremental: indexa arquivos novos de `pdf_pf/`, pula os já
processados, retoma do último checkpoint (`.pipeline/import.db`). Quando os
downloads em andamento concluírem, rodar o comando acima processa o próximo
lote automaticamente. NÃO há processamento pendente agora — o acervo
presente está 100% extraído.
