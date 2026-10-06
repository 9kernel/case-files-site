#!/usr/bin/env python3
"""ingest.py — parser PDF -> JSON no schema do site (ferramenta do agente catalogador).

Converte trechos de conversa (formato de exportação do WhatsApp usado nos autos)
para data/threads/{{thread-id}}.json, preenchendo source_ref com documento + folha.

Uso:
    # Modo demo (sem PDF): usa uma transcrição embutida e grava tudo pending-review
    python scripts/ingest.py --demo --thread-id demo-nova --title "Demo" \\
        --document-name "IP 2024/0123" --pages 140-145 --source-url https://example.org/x.pdf

    # PDF real (requer: pip install pdfplumber)
    python scripts/ingest.py --pdf caminho.pdf --pages 120-133 \\
        --thread-id grupo-x --title "Grupo X" \\
        --document-name "IP 2024/0123" --source-url https://example.org/x.pdf

Regras respeitadas:
  - NADA é parafraseado: o content é exatamente a linha do documento.
  - Toda mensagem entra com status "pending-review" (revisão humana confere
    o diff contra o PDF e muda para "confirmed" no mesmo PR).
  - Remetentes são resolvidos via data/participants.json (nome ou alias);
    nomes desconhecidos ABORTAM o script (não inventamos participantes).
  -added_in recebe o marcador "pending" e deve ser trocado pelo hash do
    commit no momento do versionamento.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
THREADS = DATA / "threads"

# Linha de mensagem: "11/03/2024 08:12 - Ana Cardoso: texto..."
MSG_RE = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4}) (?P<time>\d{2}:\d{2}) - (?P<sender>[^:]+): (?P<text>.*)$")
# Linha de sistema: "11/03/2024 08:05 - Mensagens e chamadas..."
SYS_RE = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4}) (?P<time>\d{2}:\d{2}) - (?P<text>.+)$")

DOC_HINTS = (".pdf", ".docx", ".doc", ".xlsx", ".csv")
IMG_HINTS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def demo_transcript() -> str:
    # Nomes resolvidos via participants.json (aliases reais do caso atual).
    return """08/12/2024 12:00 - Miranda: Flavio, bolso querem sentar com vc. Tem 40 minutos pra matarmos isso na quarta?
08/12/2024 12:05 - Miranda: Do filme do presidente e do SBT $$
08/12/2024 12:06 - Miranda: Flavio [Carneiro] está ciente de tudo
08/12/2024 17:00 - Miranda: Confirmei com o Flávio Bolsonaro. Quarta dia 11 às 17:30 aqui na sua casa de Brasília.
09/12/2024 20:00 - Vorcaro: Não fala dessa reunião bolso pra ninguém!
09/12/2024 20:01 - Vorcaro: Esse negócio acaba comigo.
10/12/2024 09:00 - Chamada de voz perdida
16/12/2024 12:49 - Flávio: Fala irmão. Tô com senador aqui. Pode falar ?!?
16/12/2024 12:50 - Vorcaro: Opa. Sim
20/12/2024 10:00 - Miranda: Analisou algo do filme? Deixamos para resolver em janeiro?
"""


def extract_pdf_text(pdf_path: Path, page_start: int, page_end: int) -> list[str]:
    """Extrai texto página a página (pdfplumber). Retorna lista por página."""
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        sys.exit(
            "[ingest] pdfplumber não instalado. Rode: pip install pdfplumber\n"
            "         (ou use --demo, que não precisa de dependências)."
        )
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for num in range(page_start, min(page_end, len(pdf.pages)) + 1):
            text = pdf.pages[num - 1].extract_text() or ""
            pages.append(text)
    return pages


def resolve_sender(name: str, participants: list[dict]) -> str | None:
    """Nome/alias -> participants.id. None se desconhecido (aborta depois)."""
    needle = name.strip().lower()
    for p in participants:
        candidates = {p["name"].lower(), *(a.lower() for a in p.get("aliases", []))}
        if needle in candidates:
            return p["id"]
    return None


def guess_type(text: str) -> str:
    low = text.lower()
    if any(h in low for h in DOC_HINTS):
        return "document"
    if any(h in low for h in IMG_HINTS) or "⌁" in text or "<mídia omitida>" in low:
        return "image"
    if "nota de voz" in low or "áudio" in low:
        return "audio"
    if low.startswith("chamada de voz"):
        return "call"
    return "text"


def filename_hint(text: str) -> str | None:
    for token in text.split():
        if token.lower().endswith(DOC_HINTS + IMG_HINTS + (".mp4", ".wav")):
            return token
    return None


def parse_lines(lines: list[str], participants: list[dict], tz: str) -> tuple[list[dict], list[str]]:
    """Converte linhas de exportação em mensagens no schema. Retorna (msgs, desconhecidos)."""
    messages: list[dict] = []
    unknown: set[str] = set()
    today = datetime(2024, 1, 1)

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        m = MSG_RE.match(line)
        is_system = False
        if not m:
            m = SYS_RE.match(line)
            is_system = True
            if not m:
                # continuação de mensagem multilinha: anexa à última
                if messages:
                    messages[-1]["content"] += "\n" + line
                continue

        date = datetime.strptime(m.group("date"), "%d/%m/%Y")
        hh, mm = m.group("time").split(":")
        ts = date.replace(hour=int(hh), minute=int(mm))
        # datas sem ano explícito no export? o export sempre tem ano; usamos o do documento.

        if is_system:
            messages.append(
                {
                    "timestamp": f"{ts.isoformat()}{tz}",
                    "sender_id": participants[0]["id"],  # sistema ancorado no 1º participante
                    "type": "system",
                    "content": m.group("text"),
                }
            )
            continue

        sender_name = m.group("sender")
        sender_id = resolve_sender(sender_name, participants)
        if sender_id is None:
            unknown.add(sender_name)
            continue

        text = m.group("text")
        msg = {
            "timestamp": f"{ts.isoformat()}{tz}",
            "sender_id": sender_id,
            "type": guess_type(text),
            "content": text,
        }
        fname = filename_hint(text)
        if fname and msg["type"] in ("document", "image", "audio", "video"):
            msg["media"] = {"filename": fname}
        messages.append(msg)

    return messages, sorted(unknown)


def main() -> None:
    ap = argparse.ArgumentParser(description="Parser de conversas -> JSON do site (demo)")
    ap.add_argument("--pdf", help="caminho do PDF dos autos")
    ap.add_argument("--pages", default="120-121", help="intervalo de folhas, ex.: 120-133")
    ap.add_argument("--thread-id", required=True, help="slug da conversa (nome do arquivo)")
    ap.add_argument("--title", required=True, help="título legível da conversa")
    ap.add_argument("--document-name", required=True, help='ex.: "Inquérito Policial 2024/0123"')
    ap.add_argument("--source-url", default="", help="URL oficial do PDF")
    ap.add_argument("--participants-file", default=str(DATA / "participants.json"))
    ap.add_argument("--tz", default="-03:00", help="offset do fuso dos timestamps")
    ap.add_argument("--out", default=str(THREADS), help="diretório de saída")
    ap.add_argument("--demo", action="store_true", help="usa transcrição embutida (sem PDF)")
    args = ap.parse_args()

    participants = json.loads(Path(args.participants_file).read_text(encoding="utf-8"))

    page_match = re.match(r"^(\d+)-(\d+)$", args.pages)
    if not page_match:
        sys.exit(f"[ingest] --pages inválido: {args.pages} (use 120-133)")
    page_start, page_end = int(page_match.group(1)), int(page_match.group(2))

    if args.demo:
        raw_lines = demo_transcript().splitlines()
    elif args.pdf:
        pages = extract_pdf_text(Path(args.pdf), page_start, page_end)
        # página -> linhas; form-feed natural do pdfplumber mantém a ordem
        raw_lines = [line for page in pages for line in page.splitlines()]
    else:
        sys.exit("[ingest] informe --pdf CAMINHO ou --demo")

    messages, unknown = parse_lines(raw_lines, participants, args.tz)
    if not messages:
        sys.exit("[ingest] nenhuma mensagem reconhecida — confira o formato do texto.")
    if unknown:
        sys.exit(
            "[ingest] ABORTADO: remetentes sem entrada em participants.json "
            f"(regra editorial: não inventamos participantes): {', '.join(unknown)}\n"
            "         Adicione-os ao participants.json e rode novamente."
        )

    # source_ref por página: distribui mensagens ao longo do intervalo de folhas
    span = max(1, page_end - page_start + 1)
    per_page = max(1, len(messages) // span)
    for i, msg in enumerate(messages):
        page = page_start + min(span - 1, i // per_page)
        msg["source_ref"] = f"{args.document_name} · fl. {page}"
        msg["status"] = "pending-review"  # nunca publica sem revisão humana
        msg["added_in"] = "pending"

    for i, msg in enumerate(messages, start=1):
        msg["id"] = f"m-{i:05d}"
        # reordena campos para leitura humana
        ordered = {
            "id": msg["id"],
            "timestamp": msg["timestamp"],
            "sender_id": msg["sender_id"],
            "type": msg["type"],
            "content": msg["content"],
        }
        if "media" in msg:
            ordered["media"] = msg["media"]
        ordered.update(
            source_ref=msg["source_ref"],
            status=msg["status"],
            added_in=msg["added_in"],
        )
        messages[i - 1] = ordered

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.thread_id}.json"
    payload = {
        "id": args.thread_id,
        "title": args.title,
        "participants_ids": [p["id"] for p in participants if any(
            m["sender_id"] == p["id"] for m in messages)],
        "source": {
            "document": args.document_name,
            "url": args.source_url,
            "pages": f"fl. {args.pages}",
        },
        "messages": messages,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[ingest] {len(messages)} mensagem(s) gravada(s) em {out_path.relative_to(ROOT)}")
    print("[ingest] TODAS com status 'pending-review' — revise contra o PDF original,")
    print("[ingest] mude para 'confirmed' e atualize added_in com o hash do commit.")
    print("[ingest] Lembre de adicionar a thread ao data/threads.json (índice da ChatList).")


if __name__ == "__main__":
    main()
