# backup_local.py — protocolo de backup local do acervo
"""Executar ANTES de qualquer rodada de mutação de dados (curadores, fixes,
varreduras). Cria .backups/data-<sha>-<timestamp>.zip com todo o acervo
curado (threads, índices, participantes, documentos, créditos). O git segue
sendo o backup primário (commitar a rodada anterior antes); o zip cobre o
estado PRÉ-mutação, permitindo restauração rápida sem refazer histórico.

Restaurar: descompacte o zip sobre a raiz do repositório (sobrescreve data/).
Execução: python scripts/backup_local.py
"""
from __future__ import annotations

import datetime
import glob
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    os.makedirs(os.path.join(ROOT, ".backups"), exist_ok=True)
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip() or "sem-commit"
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = os.path.join(ROOT, ".backups", f"data-{sha}-{ts}.zip")
    n = 0
    with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
        for pattern in ("data/threads/*.json", "data/*.json", "public/media/people/CREDITS.md"):
            for f in glob.glob(os.path.join(ROOT, pattern)):
                z.write(f, os.path.relpath(f, ROOT))
                n += 1
    print(f"[backup] {name} ({n} arquivos, {os.path.getsize(name) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
