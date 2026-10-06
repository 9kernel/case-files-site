#!/usr/bin/env python3
"""Gera as mídias de demonstração (sem dependências externas obrigatórias):
WAVs, PDF mínimo e — se o pacote opcional imageio-ffmpeg estiver instalado —
os vídeos MP4 com trilha de áudio.

Uso:  python scripts/make-demo-media.py
Os arquivos são placeholders — no caso real, substituir pelas mídias dos autos.
"""
from __future__ import annotations

import math
import struct
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "public" / "media"


def make_wav(path: Path, seconds: float, freq: float) -> None:
    rate = 8000
    n = int(rate * seconds)
    frames = bytearray()
    for i in range(n):
        fade = min(1.0, (n - i) / (rate * 0.1))  # fade-out simples
        value = int(520 * fade * math.sin(2 * math.pi * freq * i / rate))
        frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


def make_pdf(path: Path) -> None:
    lines = [
        "Laudo Tecnico - Bloco B (DEMONSTRACAO)",
        "",
        "Documento ficticio gerado para o scaffold do",
        "Arquivo Publico de Dialogos.",
        "",
        "Nao constitui documento real e serve apenas para",
        "demonstrar o card de documento da interface.",
    ]

    def esc(s: str) -> str:
        return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    parts = ["BT", "/F1 14 Tf", "1 0 0 1 72 740 Tm", "20 TL"]
    for line in lines:
        parts.append(f"({esc(line)}) Tj T*")
    parts.append("ET")
    stream = "\n".join(parts)

    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{obj}\nendobj\n".encode("latin-1")

    xref_pos = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("ascii")
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF"
    ).encode("ascii")
    path.write_bytes(bytes(out))


def make_videos() -> bool:
    """Gera os MP4 de demonstração (H.264 + AAC, com som) usando o binário
    estático do pacote opcional imageio-ffmpeg. Retorna True se gerou."""
    try:
        import imageio_ffmpeg  # type: ignore

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("aviso: imageio-ffmpeg não instalado — vídeos não regenerados "
              "(pip install imageio-ffmpeg)")
        return False

    specs = [
        # (arquivo, filtro de vídeo, frequência do tom, duração)
        ("video-001.mp4", "testsrc2=size=480x270:rate=12:duration=4", 440, 4),
        ("video-002.mp4", "smptebars=size=480x270:rate=12:duration=3", 523, 3),
    ]
    for name, vf, freq, dur in specs:
        subprocess.run(
            [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", vf,
                "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={dur}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-profile:v", "baseline", "-level", "3.0",
                "-c:a", "aac", "-b:a", "64k",
                "-movflags", "+faststart", "-shortest",
                str(MEDIA / name),
            ],
            check=True,
        )
    return True


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    make_wav(MEDIA / "audio-001.wav", 3.0, 440.0)
    make_wav(MEDIA / "audio-002.wav", 2.0, 523.25)
    make_pdf(MEDIA / "doc-001.pdf")
    make_videos()
    for f in sorted(MEDIA.iterdir()):
        print(f"ok: {f.relative_to(ROOT)} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
