#!/usr/bin/env python3
"""Servidor local de desenvolvimento com Cache-Control: no-cache.

Uso:  python scripts/dev-server.py [porta]     (padrão: 8080)

Igual ao `python -m http.server`, mas envia `Cache-Control: no-cache`, evitando
que o navegador sirva JS/CSS antigos durante o desenvolvimento (o http.server
padrão não envia cabeçalhos de cache e o Chromium aplica cache heurístico).
"""
import http.server
import sys
from pathlib import Path


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    root = Path(__file__).resolve().parent.parent
    import functools

    handler = functools.partial(NoCacheHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"[dev-server] http://localhost:{port}  (Cache-Control: no-cache)")
    server.serve_forever()


if __name__ == "__main__":
    main()
