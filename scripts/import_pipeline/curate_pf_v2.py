# curate_pf_v2.py — curadoria das conversas demonstradas nos novos IPJ-A/PET
"""Extrai citações literais com remetente nomeado e monta threads no schema
do site, roteando cada citação para a conversa declarada na legenda da
figura da própria página ("Conversa entre X e Y").

Fidelidade (missão §7-§8):
- quote = substring exata do texto extraído da página (só normalização de
  quebras de linha do PDF);
- data/hora apenas quando na MESMA frase do documento;
- sender apenas quando nomeado pelo verbo de fala na frase;
- conversa direta apenas quando o próprio documento a declara.

Gera: data/threads/{felipe-mourao,walfrido-warde,fabiano-zettel}-daniel-vorcaro.json
      + participantes + documents.json + índice (append).
Reexecutável: idempotente por lote added_in.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .common import REPO

ADDED_IN = "ingest-pf-20261007"
DOCS = {
    "pf-ipja-1070759-2026": {"authority": "Polícia Federal", "document": "IPJ-A nº 1070759/2026",
                              "unit": "NADIP/DFIN/CGRC/DICOR/PF", "pages": 198},
    "pf-ipja-1020625-2026": {"authority": "Polícia Federal", "document": "IPJ-A nº 1020625/2026",
                              "unit": "NADIP/DFIN/CGRC/DICOR/PF", "pages": 126},
    "pf-repr-pet15-499": {"authority": "Polícia Federal", "document": "Representação PF (PET 15.499/STF)",
                           "unit": "CINQ/CGRC/DICOR/PF", "pages": 238},
}
PROCESS_ORDER = ["pf-ipja-1070759-2026", "pf-ipja-1020625-2026", "pf-repr-pet15-499"]

SPK = re.compile(
    r'(?:([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{3,38})|([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ\u2019\']+'
    r'(?:\s+(?:de|da|do|dos|das)\s+)?(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ\u2019\']+){1,4}))'
    r'\s*(?:afirma\w*|confirma\w*|diz|pergunta\w*|responde\w*|reitera\w*|concorda\w*|'
    r'sinaliza\w*|explica\w*|escreve\w*|complementa\w*|acrescenta\w*|indaga\w*|'
    r'conclui\w*|orienta\w*|questiona\w*|cobra\w*|'
    r'encaminha\w*(?:\s+uma?\s+\w+){0,3}|envia\w*(?:\s+uma?\s+\w+){0,3}|pediu)'
    r'[^"“\n]{0,220}?["\u201c]([^"”\u201d]{3,400})["\u201d]', re.UNICODE)
DATE = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
TIME = re.compile(r"\bàs\s+(\d{1,2}:\d{2}(?::\d{2})?)\b")
FIG = re.compile(r"Figura\s+(\d+)")
CAPTION = re.compile(r"[Cc]onversas?\s+entre\s+([^,;.\n]{3,80}?)\s+e\s+([^,;.\n]{3,80}?)(?=,|\.|$|\n)", re.UNICODE)
# verbo de fala com sujeito em pronome ("Na sequência, afirmou: ...") — o sujeito
# nominal vem antes na narrativa; só aceitamos um dos nomes conhecidos do caso
VERB_STEM = r"(?:afirma\w*|confirma\w*|diz|pergunta\w*|responde\w*|reitera\w*|concorda\w*|sinaliza\w*|explica\w*|escreve\w*|complementa\w*|acrescenta\w*|indaga\w*|conclui\w*|orienta\w*|questiona\w*|cobra\w*|encaminha\w*|envia\w*|pediu)"
PRON_VERB = re.compile(VERB_STEM + r'[^"“\n]{0,220}?["\u201c]([^"”\u201d]{3,400})["\u201d]', re.UNICODE)
NAME_TOKENS = {
    "daniel-vorcaro": re.compile(r"\b(?:DANIEL BUENO VORCARO|DANIEL VORCARO|DANIEL BUENO|VORCARO)\b"),
    "felipe-mourao": re.compile(r"\bFELIPE MOUR[ÃA]O\b"),
    "walfrido-warde": re.compile(r"\b(?:WALFRIDO WARDE|WALFRIDO|WALFIDRO|WARDE)\b"),
    "fabiano-zettel": re.compile(r"\bFABIANO (?:CAMPOS )?ZETTEL\b"),
}


def sender_of(raw: str) -> str | None:
    s = re.sub(r"[^A-Za-zÀ-ÿ ]", " ", raw).strip()
    if re.match(r"(?i)^(daniel\s+)?(bueno\s+)?vorcaro", s):
        return "daniel-vorcaro"
    if re.match(r"(?i)^felipe\s+mour", s):
        return "felipe-mourao"
    if re.match(r"(?i)^walfrid|^ward", s):
        return "walfrido-warde"
    if re.match(r"(?i)^fabiano\s+zettel", s):
        return "fabiano-zettel"
    return None


def chat_of_caption(a: str, b: str) -> str | None:
    pair = f"{a} {b}"
    if re.search(r"(?i)vorcar", pair):
        if re.search(r"(?i)walfrid|warde", pair):
            return "walfrido-warde"
        if re.search(r"(?i)zettel", pair):
            return "fabiano-zettel"
        if re.search(r"(?i)mour", pair):
            return "felipe-mourao"
    return None


def page_chats(text: str) -> list[str]:
    return [c for c in (chat_of_caption(a, b) for a, b in CAPTION.findall(text)) if c]


def clean(s: str) -> str:
    return " ".join(s.split())


# ---- revisão humana (auditoria 2026-10-07) --------------------------------
# correções sobre a extração automática, cada uma conferida no texto da página
SENDER_FIX = {  # quote (início, caixa-baixa) -> remetente documentalmente correto
    "se quiser adicionar + gente": "felipe-mourao",  # fl.20: "FELIPE MOURAO encaminha... a mensagem"
    "se vc quiser vou com o pessoal do rio": "felipe-mourao",  # fl.50: FM fala com Vorcaro
}
DROP_QUOTES = [  # conteúdo de captura (não mensagem), duplicata ou fragmento
    "usuária de nome não reproduzido",      # texto da consulta anexada, não mensagem do chat
    "boa vc é foda",               # dup. da ocorrência datada no IPJ-A («Boa vc e foda»)
    "o tiro saiu pela culatra",    # fragmento da ocorrência completa
    "mas o principal é o primeiro",# fragmento de «Esse outro foi na onda…»
    "estamos no aguardo",          # fragmento; a frase completa entra à mão (fl. 11)
]
# seção do advogado (fls. 103-120 do IPJ-A 1020625): toda a conversa é Warde<->Vorcaro
WARDE_SECTION = ("pf-ipja-1020625-2026", range(103, 121))

# mensagens conferidas à mão: (quote, página, hora|None, data|None, remetente, chat)
# data/hora apenas quando o documento registra; semântica "me liga": enviado
# várias vezes pelo advogado — cada ocorrência com sua página
HAND_MESSAGES = [
    # Warde -> Vorcaro (IPJ-A 1020625, fls. 106-119; seção do dia 17/11/2025)
    ("Bom dia", 106, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("Me liga", 106, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("Ou marcamos amanha", 107, None, None, "walfrido-warde", "walfrido-warde"),
    ("me liga", 109, "09:42", "2025-11-17", "walfrido-warde", "walfrido-warde"),  # "Às 09h42min"
    ("Qual Hangar?", 108, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("mudou algo", 108, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("Será que decola??", 109, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("estão protocolando", 115, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("já estão se falando", 115, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("tudo em curso", 115, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("me liga", 118, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("Mandamos pro juiz também", 119, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    ("Estamos infernizando o cara", 119, None, "2025-11-17", "walfrido-warde", "walfrido-warde"),
    # Vorcaro -> Warde (fl. 107: "DV respondeu…"; fl. 108: "VORCARO prontamente responde")
    ("Nao marca mais a reuniao pq agora mudei o roteiro", 107, None, None, "daniel-vorcaro", "walfrido-warde"),
    ("Voar 1", 108, None, "2025-11-17", "daniel-vorcaro", "walfrido-warde"),
    # frase completa reencaminhada por FM (IPJ-A 1070759, fl. 11, fig. 2 — 24/10/2023)
    ("Opa! Estamos no aguardo aqui", 11, None, "2023-10-24", "felipe-mourao", "felipe-mourao"),
]
# ocorrências automáticas substituídas pelas conferidas à mão acima
HAND_REPLACE = [
    "me liga", "nao marca mais a reuniao", "qual hangar", "será que decola",
    "mudou algo", "estão protocolando", "já estão se falando", "tudo em curso",
    "mandamos pro juiz", "estamos infernizando", "bom dia", "ou marcamos", "voar 1",
]


def mine():
    """[(chat, sender, quote, date, time, doc, page, figure, context)]"""
    out = []
    for doc in PROCESS_ORDER:
        pages = json.loads((REPO / "data" / "cache" / "pages" / f"{doc}.json").read_text(encoding="utf-8"))["pages"]
        for p, t in sorted(pages.items(), key=lambda kv: int(kv[0])):
            chats = page_chats(t)
            page_chat = None
            if chats:
                # página declarada para UMA conversa (ou majoritária)
                page_chat = max(set(chats), key=chats.count)
            # 1ª passada: falante nomeado; 2ª passada: sujeito por pronome
            hits = []
            for m in SPK.finditer(t):
                hits.append((m, sender_of(m.group(1) or m.group(2) or "")))
            pron_subj_used = []
            for m in PRON_VERB.finditer(t):
                # ignora os já capturados com nome (sobreposição de posição)
                if any(h.start() - 20 <= m.start() <= h.end() + 20 for h, _ in hits):
                    continue
                # sujeito: último nome conhecido citado até 320 chars antes do verbo
                back = t[max(0, m.start() - 320):m.start()]
                cand = [(back.rfind(tok), pid) for pid, rx in NAME_TOKENS.items()
                        for tok in [m2.group(0) for m2 in rx.finditer(back)]]
                cand = [(pos, pid) for pos, pid in cand if pos != -1]
                if not cand:
                    continue
                pos, pid = max(cand)
                # pronome só vale se nenhum OUTRO nome conhecido aparecer depois
                # desse até o verbo (senão o sujeito é o outro)
                after = back[pos:]
                others = [p2 for p2 in NAME_TOKENS if p2 != pid and NAME_TOKENS[p2].search(after)]
                if others:
                    continue
                hits.append((m, pid))
                pron_subj_used.append(m.start())
            for m, sender in hits:
                if not sender:
                    continue
                # normaliza: para SPK o grupo da citação é o 3; para PRON_VERB é o 1
                quote = clean(m.group(3) if m.re is SPK else m.group(1))
                if len(quote.split()) < 2:
                    continue
                sent = t[max(0, m.start() - 220):m.end() + 120]
                d = DATE.search(sent)
                tm = TIME.search(sent)
                figs = FIG.finditer(t)
                fig = min(figs, key=lambda fm: abs(fm.start() - m.start()), default=None)
                # roteamento: a própria frase/narrativa declara a conversa
                # ("Na conversa entre X e Y, este afirma..."); senão, a legenda da página
                win_chat = None
                wide = t[max(0, m.start() - 520):m.start()]
                cm = CAPTION.search(wide) or CAPTION.search(sent)
                if cm:
                    win_chat = chat_of_caption(cm.group(1), cm.group(2))
                chat = win_chat or page_chat
                if chat is None:
                    chat = "felipe-mourao" if sender in ("daniel-vorcaro", "felipe-mourao") else sender
                # revisão humana: correções e descartes
                low = quote.lower()
                for frag, right in SENDER_FIX.items():
                    if low.startswith(frag):
                        sender = right
                if any(low.startswith(frag) for frag in DROP_QUOTES):
                    continue
                # fala do Mourão endereçada a Vorcaro não mora no chat do Zettel
                if sender == "felipe-mourao" and chat == "fabiano-zettel":
                    chat = "felipe-mourao"
                if doc == WARDE_SECTION[0] and int(p) in WARDE_SECTION[1]:
                    chat = "walfrido-warde"
                out.append({
                    "chat": chat, "sender": sender, "quote": quote,
                    "date": f"{d.group(3)}-{d.group(2)}-{d.group(1)}" if d else None,
                    "time": tm.group(1) if tm else None,
                    "doc": doc, "page": int(p),
                    "figure": int(fig.group(1)) if fig else None,
                    "context": clean(sent)[:320],
                })
    # dedup entre documentos: mantém a 1ª ocorrência (1070759 > 1020625 > repr)
    seen: dict[str, dict] = {}
    final = []
    for q in out:
        key = re.sub(r"\W", "", q["quote"].lower())[:60]
        if key in seen:
            seen[key].setdefault("also", []).append(f'{q["doc"]} fl. {q["page"]}')
            continue
        seen[key] = q
        final.append(q)
    return final


def build_message(seq, q):
    d = DOCS[q["doc"]]
    prec = "minute" if q["time"] else ("date" if q["date"] else None)
    msg = {
        "id": f"m-{seq:05d}",
        "date": q["date"],
        "time": q["time"],
        "timestamp_precision": prec,
        "sender_id": q["sender"],
        "content_kind": "verbatim_excerpt",
        "content": q["quote"],
        "editorial_note": f"Contexto do relatório: {q['context']}",
        "source": {"document_id": q["doc"], "page": q["page"], "figure": q["figure"]},
        "verification": {
            "level": "official_document",
            "origin": "PF extraction",
            "authority": d["authority"],
            "court": "STF",
            "case": "PET 15.499/STF" if q["doc"] == "pf-repr-pet15-499" else None,
            "document": d["document"],
            "page": q["page"],
            "figure": q["figure"],
            "official_url": None,
            "primary_document_located": True,
            "verified_at": "2026-10-07",
        },
        "sources": {
            "primary": {
                "type": "official_document",
                "document_id": q["doc"],
                "authority": d["authority"],
                "court": "STF",
                "case": "PET 15.499/STF" if q["doc"] == "pf-repr-pet15-499" else None,
                "document": d["document"],
                "page": q["page"],
                "figure": q["figure"],
                "url": None,
            },
            "secondary": [],
        },
        "source_ref": f'PF · {d["document"]} · fl. {q["page"]}' + (f' · fig. {q["figure"]}' if q["figure"] else ""),
        "added_in": ADDED_IN,
    }
    if prec is None:
        msg.pop("timestamp_precision")
    if q["time"] is None:
        msg.pop("time")
    if "[" in q["quote"]:
        # colchetes constam do documento original (glosa da própria PF)
        msg["literal_brackets"] = True
    if q.get("also"):
        msg["editorial_note"] += " A mesma mensagem consta também em: " + "; ".join(dict.fromkeys(q["also"])) + "."
    return msg


def order_messages(msgs, raw):
    dated = [m for m in msgs if m["date"]]
    undated = [m for m in msgs if not m["date"]]
    dated.sort(key=lambda m: (m["date"], m.get("time") or "~"))
    undated.sort(key=lambda m: (PROCESS_ORDER.index(next(q["doc"] for q in raw if q["quote"] == m["content"])),
                                next(q["page"] for q in raw if q["quote"] == m["content"])))
    return dated + undated


THREAD_META = {
    "felipe-mourao": {
        "title": "Felipe Mourão",
        "source_doc": "PF · IPJ-A nº 1070759/2026 (análise do celular de Vorcaro) e IPJ-A nº 1020625/2026, com reprodução na Representação PF da PET 15.499/STF",
        "note": "O relatório da PF documenta conversa direta prolongada entre Vorcaro e Felipe Mourão, identificado no próprio documento como agente cooptador (tese da PF). Citações literais conforme transcritas na narrativa policial; datas e horários apenas quando documentados.",
        "events": [
            ("2024-06-20", "Felipe Mourão encaminha processos reservados dos sistemas do MPF (GRU-DANIEL.pdf, PROCESSO SIGILO 2.pdf), segundo o relatório (fl. 21, fig. 26).", "pf-ipja-1020625-2026", 21, 26),
            (None, "Mourão compartilha consulta do Sistema Aptus do MPF registrada sob o login de uma servidora do MPF, conforme análise da PF (fl. 20, fig. 24).", "pf-ipja-1020625-2026", 20, 24),
            (None, "Mourão encaminha lista de nomes para consulta de processos sigilosos; Vorcaro responde pedindo para 'adicionar + gente' (fls. 20-21).", "pf-ipja-1020625-2026", 20, 25),
        ],
    },
    "walfrido-warde": {
        "title": "Walfrido Warde",
        "source_doc": "PF · IPJ-A nº 1020625/2026, fls. 103-119 (conversa declarada nas legendas das figuras)",
        "note": "Advogado de Vorcaro, segundo o relatório. A conversa retomada no dia 17/11/2025 — data da prisão — acompanha a protocolização da petição e o encaminhamento de reportagens, conforme a análise da PF.",
        "events": [
            ("2025-11-17", "No dia da prisão de Vorcaro, Warde acompanha a protocolização da petição e o encaminhamento das reportagens, segundo o relatório (fls. 112-119).", "pf-ipja-1020625-2026", 116, 133),
        ],
    },
    "fabiano-zettel": {
        "title": "Fabiano Zettel",
        "source_doc": "PF · Representação PF (PET 15.499/STF) e IPJ-A nº 1020625/2026 (conversas declaradas no texto e nas legendas)",
        "note": "Cunhado de Vorcaro, segundo o relatório. A PF descreve combinações de 'pressão' sobre o ex-chefe de cozinha e o ex-capitão do barco de Vorcaro (fls. 48-53).",
        "events": [
            (None, "A PF descreve combinação de 'pressão' sobre o ex-chefe de cozinha e o ex-capitão do barco de Vorcaro envolvendo Vorcaro, Zettel e Mourão (fls. 48-50, figs. 56-58).", "pf-ipja-1020625-2026", 49, 57),
        ],
    },
}

PARTICIPANTS_NEW = [
    {
        "id": "felipe-mourao", "name": "Felipe Mourão", "photo": None,
        "role": "Interlocutor de Vorcaro identificado no relatório da PF como agente cooptador (tese da PF)",
        "aliases": ["Sicário"],
        "summary": "Apelidado de 'Sicário' nas conversas, conforme registra o relatório. A PF atribui a ele a execução de demandas de Vorcaro junto ao núcleo que o documento chama de 'Os Meninos'. Perfil resumido exclusivamente a partir dos documentos linkados; não constitui acusação nem conclusão sobre responsabilidade individual.",
    },
    {
        "id": "walfrido-warde", "name": "Walfrido Warde", "photo": None,
        "role": "Advogado de Daniel Vorcaro",
        "aliases": ["Walfidro", "Warde"],
        "summary": "Advogado de Vorcaro que, segundo o relatório, não mantinha contato com o cliente desde 03/08/2025 e retomou a comunicação no dia 17/11/2025, data da prisão, acompanhando a protocolização de petição e o encaminhamento de reportagens. Perfil resumido exclusivamente a partir dos documentos linkados.",
    },
    {
        "id": "fabiano-zettel", "name": "Fabiano Zettel", "photo": None,
        "role": "Cunhado de Vorcaro; identificado no relatório como operador financeiro (tese da PF)",
        "aliases": ["F.Z.", "Fabiano"],
        "summary": "Citado na conversa com Fábio Faria ('OK para F.Z') e nas análises da PF, que descrevem sua atuação em ações descritas como 'pressão' e em pagamentos por empresa ligada a ele. Perfil resumido exclusivamente a partir dos documentos linkados; não constitui acusação nem conclusão sobre responsabilidade individual.",
    },
]

DOCUMENTS_NEW = [
    {
        "id": "pf-ipja-1070759-2026",
        "title": "IPJ-A nº 1070759/2026 — Análise do conteúdo extraído do celular de Daniel Bueno Vorcaro",
        "authority": "Polícia Federal", "unit": "NADIP/DFIN/CGRC/DICOR/PF",
        "date": None, "court": "STF", "case": "IPL 2025.0087917-DELEINQUE/DRPJ/SR/PF/DF",
        "reporting_judge": None, "pages": 198,
        "official_process_url": None, "public_copy_url": None, "copy_kind": None,
        "copy_note": "Peça obtida pelo editor do projeto em 2026-10-06; situação de publicidade em verificação — por isso sem cópia hospedada. Mensagens que a citam trazem página/figura verificadas contra este arquivo (SHA-256 registrado).",
        "sha256": None, "bytes": None, "local_copy": None, "hash_note": None,
    },
    {
        "id": "pf-ipja-1020625-2026",
        "title": "IPJ-A nº 1020625/2026 — Análise de material apreendido (IPL 2025.0087917)",
        "authority": "Polícia Federal", "unit": "NADIP/DFIN/CGRC/DICOR/PF",
        "date": None, "court": "STF", "case": "IPL 2025.0087917-DELEINQUE/DRPJ/SR/PF/DF",
        "reporting_judge": None, "pages": 126,
        "official_process_url": None, "public_copy_url": None, "copy_kind": None,
        "copy_note": "Peça obtida pelo editor do projeto em 2026-10-06; situação de publicidade em verificação — por isso sem cópia hospedada. Mensagens que a citam trazem página/figura verificadas contra este arquivo (SHA-256 registrado).",
        "sha256": None, "bytes": None, "local_copy": None, "hash_note": None,
    },
    {
        "id": "pf-ipj-1752768-2026",
        "title": "IPJ nº 1752768/2026 — Operação Compliance Zero 3 (laudo SETEC 8381/2026)",
        "authority": "Polícia Federal", "unit": "CINQ/DICOR/PF",
        "date": "2026-03-18", "court": "STF", "case": "PET 15.562/STF",
        "reporting_judge": None, "pages": 117,
        "official_process_url": None, "public_copy_url": None, "copy_kind": None,
        "copy_note": "Peça obtida pelo editor do projeto em 2026-10-06; publicidade em verificação; sem conteúdo importado até agora.",
        "sha256": None, "bytes": None, "local_copy": None, "hash_note": None,
    },
    {
        "id": "pf-repr-pet15-499",
        "title": "Representação da PF ao STF (Min. André Mendonça) — PET 15.499 / INQ 5.026",
        "authority": "Polícia Federal", "unit": "CINQ/CGRC/DICOR/PF",
        "date": None, "court": "STF", "case": "PET 15.499/STF · INQ 5.026",
        "reporting_judge": "Min. André Mendonça", "pages": 238,
        "official_process_url": None, "public_copy_url": None, "copy_kind": None,
        "copy_note": "Peça obtida pelo editor do projeto em 2026-10-06; publicidade em verificação. Reproduz trechos dos IPJ-A; usada para verificação cruzada de citações.",
        "sha256": None, "bytes": None, "local_copy": None, "hash_note": None,
    },
]


def event_obj(seq, date, content, doc_id, page, figure):
    d = DOCS[doc_id]
    ev = {
        "id": f"e-{seq:05d}",
        "date": date, "time": None,
        "timestamp_precision": "date" if date else None,
        "content": content,
        "event_kind": "editorial_context",
        "source": {"document_id": doc_id, "page": page, "figure": figure},
        "verification": {
            "level": "official_document", "origin": "PF extraction",
            "authority": d["authority"], "court": "STF",
            "case": "PET 15.499/STF" if doc_id == "pf-repr-pet15-499" else None,
            "document": d["document"], "page": page, "figure": figure,
            "official_url": None, "primary_document_located": True,
            "verified_at": "2026-10-07",
        },
        "source_ref": f'PF · {d["document"]} · fl. {page}' + (f' · fig. {figure}' if figure else ''),
        "added_in": ADDED_IN,
    }

    if date is None:
        ev.pop("time")
        ev.pop("timestamp_precision")
    return ev


def main():
    raw = mine()
    # revisão humana: substitui ocorrências automáticas pelas conferidas à mão
    raw = [q for q in raw
           if not any(re.sub(r"\W", "", q["quote"].lower()).startswith(re.sub(r"\W", "", f)) for f in HAND_REPLACE)]
    for quote, page, tm, dt, sender, chat in HAND_MESSAGES:
        entry = {
            "chat": chat, "sender": sender, "quote": quote, "date": dt, "time": tm,
            "doc": "pf-ipja-1070759-2026" if chat == "felipe-mourao" else "pf-ipja-1020625-2026",
            "page": page, "figure": 2 if quote.startswith("Opa!") else None,
            "context": ("Frase reencaminhada por Felipe Mourão, segundo a narrativa da fl. 11."
                        if chat == "felipe-mourao" else
                        "Conversa de Vorcaro com seu advogado na seção das fls. 106-119 (17/11/2025, data da prisão)."),
        }
        raw.append(entry)
    by_chat: dict[str, list] = {}
    for q in raw:
        by_chat.setdefault(q["chat"], []).append(q)

    for chat, qs in by_chat.items():
        msgs = [build_message(i + 1, q) for i, q in enumerate(qs)]
        msgs = order_messages(msgs, raw)
        for i, m in enumerate(msgs, 1):
            m["id"] = f"m-{i:05d}"
        meta = THREAD_META[chat]
        events = [event_obj(i + 1, *ev) for i, ev in enumerate(meta["events"])]
        thread = {
            "id": f"{chat}-daniel-vorcaro",
            "title": meta["title"],
            "participants_ids": ["daniel-vorcaro", chat],
            "source": {"document": meta["source_doc"], "url": "", "pages": meta["note"]},
            "messages": msgs,
            "timeline_events": events,
        }
        out = REPO / "data" / "threads" / f"{chat}-daniel-vorcaro.json"
        out.write_text(json.dumps(thread, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        dated = sum(1 for m in msgs if m["date"])
        print(f"[curate] {thread['id']}: {len(msgs)} mensagens ({dated} com data), "
              f"{len(events)} eventos -> {out.name}")


def apply_registry():
    """participantes, documents.json e índice — upsert idempotente."""
    pfile = REPO / "data" / "participants.json"
    participants = json.loads(pfile.read_text(encoding="utf-8"))
    ids = {p["id"] for p in participants}
    for np in PARTICIPANTS_NEW:
        if np["id"] not in ids:
            participants.append(np)
            print(f"[registry] +participante {np['id']}")
    pfile.write_text(json.dumps(participants, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    dfile = REPO / "data" / "documents.json"
    docs = json.loads(dfile.read_text(encoding="utf-8"))
    have = {d["id"] for d in docs}
    # hashes/tamanhos reais do inventário
    import sqlite3
    from .common import DB_PATH
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    inv = {r["doc_id"]: dict(r) for r in c.execute("SELECT * FROM docs")}
    c.close()
    for nd in DOCUMENTS_NEW:
        if nd["id"] in have:
            continue
        real = inv.get(nd["id"])
        if real:
            nd["sha256"] = real["sha256"]
            nd["bytes"] = real["bytes"]
        docs.append(nd)
        print(f"[registry] +documento {nd['id']} (sha256 {'ok' if real else 'PENDENTE'})")
    dfile.write_text(json.dumps(docs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    ifile = REPO / "data" / "threads.json"
    index = json.loads(ifile.read_text(encoding="utf-8"))
    have_t = {t["id"] for t in index}
    for chat, meta in THREAD_META.items():
        tid = f"{chat}-daniel-vorcaro"
        if tid in have_t:
            continue
        th = json.loads((REPO / "data" / "threads" / f"{tid}.json").read_text(encoding="utf-8"))
        last = th["messages"][-1]["content"][:80]
        index.append({
            "id": tid, "title": meta["title"],
            "participants_ids": ["daniel-vorcaro", chat],
            "message_count": len(th["messages"]),
            "last_message_preview": last,
            "featured": False,
            "note": meta["note"][:200],
        })
        print(f"[registry] +índice {tid}")
    ifile.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    apply_registry()
