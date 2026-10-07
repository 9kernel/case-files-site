#!/usr/bin/env python3
"""ingest.py — parser PDF -> JSON no schema de proveniência do site.

Converte trechos de conversa (formato de exportação do WhatsApp usado nos autos)
para data/threads/{{thread-id}}.json.

Uso:
    # Modo demo (sem PDF): usa uma transcrição embutida e grava tudo pending_review
    python scripts/ingest.py --demo --thread-id demo-nova --title "Demo" \\
        --document-name "IP 2024/0123" --pages 140-145 --source-url https://example.org/x.pdf

    # PDF real (requer: pip install pdfplumber)
    python scripts/ingest.py --pdf caminho.pdf \\
        --thread-id grupo-x --title "Grupo X" \\
        --document-name "IP 2024/0123" --source-url https://example.org/x.pdf

Regras respeitadas:
  - NADA é parafraseado: o content é exatamente a linha do documento.
  - Toda mensagem entra com verification.level "pending_review"
    (revisão humana confere o diff contra o PDF e promove o nível NO MESMO PR).
    O ingest NUNCA promove conteúdo a official_document.
  - Horário nunca é inventado: se a linha do documento tem hora, usa
    (precision "minute"); sem hora, time null (precision "date").
  - Página do documento NUNCA é calculada por distribuição: se não soubermos
    a página real da mensagem, page = null. O metadado da página do PDF de
    onde cada linha foi extraída é preservado em extraction.pdf_page
    (metadado interno de auditoria — não é exibido como fato documental).
  - Linhas de sistema (sem remetente) viram timeline_events, nunca mensagens.
  - Remetentes são resolvidos via data/participants.json (nome ou alias);
    nomes desconhecidos ABORTAM o script (não inventamos participantes).
  - added_in recebe o marcador "pending" e deve ser trocado pelo hash do
    commit no momento do versionamento.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
THREADS = DATA / "threads"

# Linha de mensagem: "11/03/2024 08:12 - Ana Cardoso: texto..."
MSG_RE = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4}) (?P<time>\d{2}:\d{2}) - (?P<sender>[^:]+): (?P<text>.*)$")
# Linha sem hora: "11/03/2024 - Ana Cardoso: texto..."
MSG_NO_TIME_RE = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4}) - (?P<sender>[^:]+): (?P<text>.*)$")
# Linha de sistema: "11/03/2024 08:05 - Mensagens e chamadas..."
SYS_RE = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4})(?: (?P<time>\d{2}:\d{2}))? - (?P<text>.+)$")

DOC_HINTS = (".pdf", ".docx", ".doc", ".xlsx", ".csv")
IMG_HINTS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def demo_transcript() -> str:
    # Nomes resolvidos via participants.json (aliases reais do caso atual).
    # Sem colchetes editoriais: nota editorial nunca nasce dentro da fala.
    return """08/12/2024 12:00 - Miranda: Flavio, bolso querem sentar com vc. Tem 40 minutos pra matarmos isso na quarta?
08/12/2024 12:05 - Miranda: Do filme do presidente e do SBT $$
08/12/2024 12:06 - Miranda: Flavio Carneiro está ciente de tudo
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


def guess_kind(text: str) -> str:
    low = text.lower()
    if any(h in low for h in DOC_HINTS):
        return "media", "document"
    if any(h in low for h in IMG_HINTS) or "⌁" in text or "<mídia omitida>" in low:
        return "media", "image"
    if "nota de voz" in low or "áudio" in low:
        return "audio_transcript", None
    if low.startswith("chamada de voz"):
        return "call", None
    return "verbatim", None


def filename_hint(text: str) -> str | None:
    for token in text.split():
        if token.lower().endswith(DOC_HINTS + IMG_HINTS + (".mp4", ".wav")):
            return token
    return None


def verification_pending() -> dict:
    # Nível inicial fixo: promoção a official_document exige revisão humana.
    return {
        "level": "pending_review",
        "origin": "PF extraction",
        "authority": None,
        "court": None,
        "case": None,
        "document": None,
        "page": None,
        "figure": None,
        "official_url": None,
        "primary_document_located": False,
        "verified_at": None,
    }


def parse_lines(
    lines: list[tuple[str, int | None]], participants: list[dict]
) -> tuple[list[dict], list[dict], list[str]]:
    """Converte linhas (texto, página do PDF) em (mensagens, eventos, desconhecidos)."""
    messages: list[dict] = []
    events: list[dict] = []
    unknown: set[str] = set()

    for raw, pdf_page in lines:
        line = raw.rstrip()
        if not line.strip():
            continue

        m = MSG_RE.match(line) or MSG_NO_TIME_RE.match(line)
        is_system = False
        if not m:
            m = SYS_RE.match(line)
            is_system = True
            if not m:
                # continuação de mensagem multilinha: anexa à última
                if messages:
                    messages[-1]["content"] += "\n" + line
                continue

        date_br = m.group("date")
        date_iso = datetime.strptime(date_br, "%d/%m/%Y").strftime("%Y-%m-%d")
        time_iso = m.groupdict().get("time")  # None se a linha não tem hora

        if is_system:
            # linha de sistema nunca é mensagem de alguém -> evento editorial
            events.append(
                {
                    "date": date_iso,
                    "time": time_iso,
                    "timestamp_precision": "minute" if time_iso else "date",
                    "content": m.group("text"),
                    "event_kind": "system",
                    "verification": verification_pending(),
                }
            )
            continue

        sender_name = m.group("sender")
        sender_id = resolve_sender(sender_name, participants)
        if sender_id is None:
            unknown.add(sender_name)
            continue

        text = m.group("text")
        kind, media_kind = guess_kind(text)
        msg: dict = {
            "date": date_iso,
            "time": time_iso,
            "timestamp_precision": "minute" if time_iso else "date",
            "sender_id": sender_id,
            "content_kind": kind,
            "content": text,
            "editorial_note": None,
            "verification": verification_pending(),
            "_pdf_page": pdf_page,
        }
        fname = filename_hint(text)
        if fname and media_kind:
            msg["media"] = {"kind": media_kind, "filename": fname}
        messages.append(msg)

    return messages, events, sorted(unknown)


def main() -> None:
    ap = argparse.ArgumentParser(description="Parser de conversas -> JSON do site")
    ap.add_argument("--pdf", help="caminho do PDF dos autos")
    ap.add_argument("--pages", default="120-121", help="intervalo de páginas do PDF lidas, ex.: 120-133")
    ap.add_argument("--thread-id", required=True, help="slug da conversa (nome do arquivo)")
    ap.add_argument("--title", required=True, help="título legível da conversa")
    ap.add_argument("--document-name", required=True, help='ex.: "Inquérito Policial 2024/0123"')
    ap.add_argument("--source-url", default="", help="URL oficial do PDF")
    ap.add_argument("--participants-file", default=str(DATA / "participants.json"))
    ap.add_argument("--out", default=str(THREADS), help="diretório de saída")
    ap.add_argument("--demo", action="store_true", help="usa transcrição embutida (sem PDF)")
    args = ap.parse_args()

    participants = json.loads(Path(args.participants_file).read_text(encoding="utf-8"))

    page_match = re.match(r"^(\d+)-(\d+)$", args.pages)
    if not page_match:
        sys.exit(f"[ingest] --pages inválido: {args.pages} (use 120-133)")
    page_start, page_end = int(page_match.group(1)), int(page_match.group(2))

    if args.demo:
        raw_lines = [(line, None) for line in demo_transcript().splitlines()]
    elif args.pdf:
        pages = extract_pdf_text(Path(args.pdf), page_start, page_end)
        # preserva a página do PDF que originou cada linha (auditoria; não é
        # página do documento oficial, portanto nunca vira verification.page)
        raw_lines = [
            (line, page_start + pageno)
            for pageno, page in enumerate(pages)
            for line in page.splitlines()
        ]
    else:
        sys.exit("[ingest] informe --pdf CAMINHO ou --demo")

    messages, events, unknown = parse_lines(raw_lines, participants)
    if not messages and not events:
        sys.exit("[ingest] nenhuma linha reconhecida — confira o formato do texto.")
    if unknown:
        sys.exit(
            "[ingest] ABORTADO: remetentes sem entrada em participants.json "
            f"(regra editorial: não inventamos participantes): {', '.join(unknown)}\n"
            "         Adicione-os ao participants.json e rode novamente."
        )

    # rastreabilidade legível SEM página: page real só após conferência humana
    source_ref = f"{args.document_name}, extração revisada pendente"

    ordered_messages = []
    for i, msg in enumerate(messages, start=1):
        ordered_messages.append(
            {
                "id": f"m-{i:05d}",
                "date": msg["date"],
                "time": msg["time"],
                "timestamp_precision": msg["timestamp_precision"],
                "sender_id": msg["sender_id"],
                "content_kind": msg["content_kind"],
                "content": msg["content"],
                "editorial_note": msg["editorial_note"],
                **({"media": msg["media"]} if "media" in msg else {}),
                "verification": msg["verification"],
                "sources": {"primary": None, "secondary": []},
                "source_ref": source_ref,
                "added_in": "pending",
                # metadado interno de extração: página do PDF de origem da
                # linha (auditoria; não é a página do documento oficial)
                "extraction": {"pdf_page": msg.get("_pdf_page")},
            }
        )

    ordered_events = []
    for i, ev in enumerate(events, start=1):
        ordered_events.append(
            {
                "id": f"e-{i:05d}",
                "date": ev["date"],
                "time": ev["time"],
                "timestamp_precision": ev["timestamp_precision"],
                "content": ev["content"],
                "event_kind": ev["event_kind"],
                "verification": ev["verification"],
                "source_ref": source_ref,
                "added_in": "pending",
            }
        )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.thread_id}.json"
    payload = {
        "id": args.thread_id,
        "title": args.title,
        "participants_ids": [p["id"] for p in participants if any(
            m["sender_id"] == p["id"] for m in ordered_messages)],
        "source": {
            "document": args.document_name,
            "url": args.source_url,
            "pages": f"páginas {args.pages} do PDF lido na extração (referência por mensagem pendente de revisão)",
        },
        "messages": ordered_messages,
        **({"timeline_events": ordered_events} if ordered_events else {}),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n = len(ordered_messages)
    try:
        shown = str(out_path.relative_to(ROOT))
    except ValueError:
        shown = str(out_path)
    print(f"[ingest] {n} mensagem(ns) + {len(ordered_events)} evento(s) gravados em {shown}")
    print("[ingest] TODOS com verification.level 'pending_review' e page null —")
    print("[ingest] a promoção de nível (e página/figura reais) é decisão humana,")
    print("[ingest] registrada no mesmo PR que confere o diff contra o documento.")
    print("[ingest] Lembre de adicionar a thread ao data/threads.json (índice da ChatList).")


if __name__ == "__main__":
    main()
