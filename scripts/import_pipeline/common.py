# common.py — caminhos, DB e gravação atômica do pipeline de importação
"""Infraestrutura compartilhada do importador em massa.

Estado de controle vive em SQLite (.pipeline/import.db, gitignored);
o texto extraído por página é cacheado em data/cache/pages/{doc_id}.json;
candidatos ficam em data/review/ (gitignored — nunca vão ao build público).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PDF_DIR = REPO / "pdf_pf"
DB_PATH = REPO / ".pipeline" / "import.db"
CACHE_DIR = REPO / "data" / "cache" / "pages"
REVIEW_DIR = REPO / "data" / "review"
AUDIT_DIR = REPO / "data" / "audit"

SCHEMA = """
CREATE TABLE IF NOT EXISTS docs(
  doc_id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  filename TEXT NOT NULL,
  ext TEXT NOT NULL,
  bytes INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  pages INTEGER,
  header_ref TEXT,
  doc_kind TEXT,
  public_access TEXT NOT NULL DEFAULT 'pending',
  status TEXT NOT NULL DEFAULT 'discovered',
  error TEXT,
  mtime REAL,
  created_at REAL,
  updated_at REAL
);
CREATE TABLE IF NOT EXISTS media_cand(
  id INTEGER PRIMARY KEY,
  doc_id TEXT NOT NULL,
  page INTEGER NOT NULL,
  kind TEXT NOT NULL,
  name TEXT,
  sha256 TEXT,
  ref TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_media ON media_cand(doc_id, page, kind, ifnull(name,''));
CREATE TABLE IF NOT EXISTS batches(
  id TEXT PRIMARY KEY,
  started_at REAL,
  finished_at REAL,
  doc_ids TEXT,
  pages INTEGER,
  quotes INTEGER,
  events INTEGER,
  media INTEGER,
  errors INTEGER,
  status TEXT
);
"""

# extensões aceitas como documentos; .crdownload/.part etc. são ignorados
DOC_EXTS = {".pdf"}
SKIP_EXTS = {".crdownload", ".part", ".tmp", ".download"}

AUDIREF_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    r"\.(?:opus|m4a|mp3|ogg|wav|aac)\b"
)
FIGURA_RE = re.compile(r"Figura\s+(\d+)(?:\s*[–-]\s*(Anexo\s+[IVXLC]+))?", re.IGNORECASE)
DATE_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b")


def conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def atomic_write_json(path: Path, data) -> None:
    """Gravação atômica: nunca deixa JSON pela metade (§4)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def derive_doc_id(first_page_text: str, sha16: str) -> tuple[str, str, str]:
    """Extrai (doc_id, header_ref, doc_kind) da primeira página; nunca inventa.

    Ordem importa: o campo de formulário ("Número da IPJ-A 1070759/2026") é
    autoritativo; menções soltas "IPJ-A nº X" em representações referem-se a
    ANEXOS, não à peça em si — por isso representações são detectadas antes.
    """
    t = (first_page_text or "").replace("\n", " ")

    if re.search(r"EXCELENT[ÍI]SSIMO", t, re.IGNORECASE) or (
        re.search(r"COORDENA[ÇC][ÃA]O DE INQU[ÉE]RITOS", t, re.IGNORECASE)
        and re.search(r"Refer[êe]ncias", t, re.IGNORECASE)
    ):
        m = re.search(r"PET\s*n?[ºo°]?\s*([\d.]+)", t, re.IGNORECASE)
        if m:
            ref = m.group(1).rstrip(".")
            sid = re.sub(r"[^\d]", "-", ref).strip("-")
            return f"pf-repr-pet{sid or sha16}", f"Representação PF (PET {ref})", "representacao"
        return f"pdf-{sha16}", "Representação PF sem PET identificada", "representacao"

    # campo de formulário dos IPJ/IPJ-A da NADIP/CINQ
    m = re.search(r"N[ÚU]MERO DA IPJ-?A[^\d]{0,30}(\d{4,9}/\d{4})", t)
    if m:
        num = m.group(1).replace("/", "-")
        return f"pf-ipja-{num}", f"IPJ-A nº {m.group(1)}", "ipja"
    m = re.search(r"N[úu]mero da IPJ-?A[^\d]{0,30}(\d{4,9}/\d{4})", t)
    if m:
        num = m.group(1).replace("/", "-")
        return f"pf-ipja-{num}", f"IPJ-A nº {m.group(1)}", "ipja"
    m = re.search(r"N[ÚU]MERO DA IPJ[^\d]{0,30}(\d{4,9}/\d{4})", t)
    if m:
        num = m.group(1).replace("/", "-")
        return f"pf-ipj-{num}", f"IPJ nº {m.group(1)}", "ipj"
    m = re.search(r"IPJ-?A[^\d]{0,40}n[ºo°]?\s*(\d{4,9}/\d{4})", t, re.IGNORECASE)
    if m:
        num = m.group(1).replace("/", "-")
        return f"pf-ipja-{num}", f"IPJ-A nº {m.group(1)}", "ipja"
    if re.search(r"INFORMA[ÇC][ÃA]O DE POL[ÍI]CIA JUDICI[ÁA]RIA", t, re.IGNORECASE):
        return f"pdf-{sha16}", "IPJ sem número identificado na 1ª página", "ipj"
    return f"pdf-{sha16}", "Documento PF não identificado na 1ª página", "desconhecido"


def batch_id(n: int) -> str:
    return f"batch-{n:04d}"


def now() -> float:
    return time.time()
