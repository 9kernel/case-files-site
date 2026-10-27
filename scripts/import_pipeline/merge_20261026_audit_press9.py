# merge_20261026_audit_press9.py — resolução do merge main x origin/main (26/10/2026)
#
# Contexto: o branch local carrega a auditoria 17-19/10 (lote audit-20261017/19) e o
# origin/main carrega os lotes de imprensa 22-26/10 (ingest-press8/press9). Ambos os
# lados appendaram registros a partir do mesmo próximo ID nos mesmos threads — os IDs
# colidem mas os registros são MENSAGENS DISTINTAS (fontes jornalísticas diferentes).
#
# Estratégia (documentada no commit de merge):
#   1. Base de cada thread conflitada = versão do origin/main (theirs), que já passou
#      pelo CI e pelas correções de proveniência de 23-26/10.
#   2. Registros editados nos dois lados → versão de theirs (correção mais recente:
#      acm e-00003 e julio m-00023/m-00027/m-00028/e-00002 rebaixados/reescritos em
#      2026-10-23), EXCETO a remoção por privacidade acm m-00004 (revisão de 17/10:
#      detalhes familiares) — aplicada, com o evento minimizado e-00005 do local.
#   3. Toda adição do lado local é reinserida na posição cronológica correta da lista
#      de theirs (mensagens e eventos); registros com ID em colisão recebem novo ID
#      (próximo livre — IDs são chaves por thread, em ordem de inserção, não precisam
#      ser cronológicos: precedente no próprio origin/main).
#
# Convenção de escrita: indent=1, UTF-8 sem escapes, LF, linha em branco no fim.

import json
import re
import subprocess
import sys
from datetime import date
import calendar

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()

THREADS = [
    'acm-neto-daniel-vorcaro',
    'ana-matos-daniel-vorcaro',
    'augusto-lima-daniel-vorcaro',
    'fabiano-zettel-daniel-vorcaro',
    'felipe-mourao-daniel-vorcaro',
    'julio-cezar-daniel-vorcaro',
    'luiz-renno-daniel-vorcaro',
    'paulo-henrique-daniel-vorcaro',
    'paulo-sergio-daniel-vorcaro',
    'walfrido-warde-daniel-vorcaro',
]

# Registros presentes na base e editados nos dois lados: fica a versão de theirs
# (correção de proveniência 2026-10-23). {(thread, id): None}
EDIT_BOTH_TAKE_THEIRS = {
    ('acm-neto-daniel-vorcaro', 'e-00003'),
    ('julio-cezar-daniel-vorcaro', 'm-00023'),
    ('julio-cezar-daniel-vorcaro', 'm-00027'),
    ('julio-cezar-daniel-vorcaro', 'm-00028'),
    ('julio-cezar-daniel-vorcaro', 'e-00002'),
}

# Remoções aplicadas só pelo lado local (decisão editorial que prevalece):
# privacidade — AGENTS.md regra de ouro 4. {(thread, id): motivo}
OURS_REMOVALS_APPLY = {
    ('acm-neto-daniel-vorcaro', 'm-00004'):
        'privacidade (revisão 17/10: detalhes familiares; substituída pelo evento minimizado e-00005)',
}

# Registros da base editados SÓ pelo lado local (theirs não tocou): a versão
# auditada do local substitui a da base no lugar em que estiver na lista de
# theirs. {(thread, id): motivo}
OURS_EDITS_APPLY = {
    ('augusto-lima-daniel-vorcaro', 'm-00001'): 'correção/nota + fonte UOL (auditoria 19/10)',
    ('paulo-henrique-daniel-vorcaro', 'm-00009'): 'autoria reatribuída a Paulo Henrique com justificativa (auditoria 19/10)',
    ('walfrido-warde-daniel-vorcaro', 'e-00002'): 'conteúdo ampliado + fontes (auditoria 19/10)',
}

# Deduplicação entre os lados (AGENTS.md §3: a mesma mensagem em reportagens com
# transcrições divergentes não se duplica): a auditoria 19/10 (Veja 09-18/10) e o
# ingest-press8 (Veja 22/10, transcrição mais completa e datas melhores) registraram
# as MESMAS mensagens do thread Warde. Fica o registro de theirs, com as fontes da
# versão do local unificadas e nota de deduplicação (precedente julio-cezar 23/10).
# {(thread, id_no_local): id_no_remoto}
DEDUP_KEEP_THEIRS = {
    ('walfrido-warde-daniel-vorcaro', 'm-00030'): 'm-00027',
    ('walfrido-warde-daniel-vorcaro', 'm-00031'): 'm-00028',
    ('walfrido-warde-daniel-vorcaro', 'm-00032'): 'm-00029',
    ('walfrido-warde-daniel-vorcaro', 'm-00034'): 'm-00031',
    ('walfrido-warde-daniel-vorcaro', 'm-00035'): 'm-00032',
    ('walfrido-warde-daniel-vorcaro', 'm-00036'): 'm-00034',
    ('walfrido-warde-daniel-vorcaro', 'm-00038'): 'm-00035',
    ('walfrido-warde-daniel-vorcaro', 'm-00039'): 'm-00037',
    ('walfrido-warde-daniel-vorcaro', 'm-00040'): 'm-00038',
}


def git_show(ref, path):
    out = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, text=True, encoding='utf-8', check=True).stdout
    return json.loads(out)


def ordered(rec):
    """Participa da comparação de ordem do validador (checkOrder): adjacência no
    array + timestamp_precision em (minute, date). Registros month/sem data
    flutuam — são a ponte editorial entre blocos, espelhando o validate.mjs."""
    return rec.get('timestamp_precision') in ('minute', 'date')


def must_precede(cand, other):
    """True se cand precisa vir antes de other por cronologia comparável
    (ambos ordered; no mesmo dia, só compara hora se ambos a tiverem —
    espelha E_TIMESTAMP_ORDER / 'mesmo dia com hora ausente não compara')."""
    if not (ordered(cand) and ordered(other)):
        return False
    if cand['date'] < other['date']:
        return True
    if cand['date'] > other['date']:
        return False
    ct, ot = cand.get('time'), other.get('time')
    if ct and ot:
        return ct < ot
    return False


def month_end(rec):
    m = re.fullmatch(r'(\d{4})-(\d{2})', rec.get('date') or '')
    if not m:
        return None
    y, mo = int(m.group(1)), int(m.group(2))
    return date(y, mo, calendar.monthrange(y, mo)[1])


def strictly_later(r, cand):
    """True se r é editorialmente posterior a cand (para escolher ponto de
    inserção): datado com cronologia comparável posterior, OU registro de
    mês-precisão de mês estritamente posterior ao de cand."""
    if r.get('timestamp_precision') == 'month':
        cmonth = (cand.get('date') or '')[:7]
        if not cmonth:
            return False
        rmonth = (r.get('date') or '')[:7]
        return bool(rmonth) and rmonth > cmonth and rmonth > (cand['date'][:7] if ordered(cand) else cmonth)
    if ordered(r) and ordered(cand):
        return must_precede(cand, r)
    if ordered(r) and cand.get('timestamp_precision') == 'month':
        me = month_end(cand)
        return me is not None and r.get('date') and r['date'] > me.isoformat()
    return False


def insert_pos(lst, cand):
    """Posição de inserção de cand na lista (semântica do validador: só pares
    adjacentes com precision minute/date são comparados):
    - ordered: antes do primeiro registro ordered que precisa vir depois — os
      registros ordered anteriores ao ponto garantidamente não ultrapassam cand;
    - month: antes do primeiro registro ordered estritamente posterior ao fim do
      mês (posicionamento editorial; month não participa da validação);
    - em ambos os casos, também para em registros month de mês estritamente
      posterior (posicionamento editorial junto ao bloco correto);
    - sem data/approximate: no fim (como estava no arquivo do lote de origem)."""
    if not cand.get('date'):
        return len(lst)
    for i, r in enumerate(lst):
        if strictly_later(r, cand):
            return i
    if ordered(cand):
        # datado sem nenhum registro posterior comparável: fim (não há
        # registro ordered à frente que precise vir depois)
        return len(lst)
    return len(lst)


def next_free_id(lst, prefix):
    mx = 0
    for r in lst:
        m = re.fullmatch(re.escape(prefix) + r'-(\d+)', r.get('id') or '')
        if m:
            mx = max(mx, int(m.group(1)))
    return mx


def merge_sources_into(rec, other):
    """Unifica em rec as fontes secundárias de other (por URL), sem duplicar."""
    sec = rec.setdefault('sources', {}).setdefault('secondary', [])
    have = {s.get('url') for s in sec}
    for s in (other.get('sources', {}) or {}).get('secondary') or []:
        if s.get('url') and s['url'] not in have:
            sec.append(s)
            have.add(s['url'])


def merge_thread(name):
    path = f'data/threads/{name}.json'
    base = git_show('200148f', path)
    ours = git_show('HEAD', path)
    theirs = git_show('origin/main', path)

    merged = dict(theirs)  # campos de nível de thread: versão publicada
    report = []

    for key, prefix in (('messages', 'm'), ('timeline_events', 'e')):
        b = {r['id']: r for r in base.get(key) or []}
        o = {r['id']: r for r in ours.get(key) or []}
        t_list = list(theirs.get(key) or [])
        t_ids = {r['id'] for r in t_list}

        # 1. remoções só do lado local (decisões editoriais que prevalecem)
        t_list = [r for r in t_list if (name, r['id']) not in OURS_REMOVALS_APPLY]

        # 2. edições só do local sobre registros da base: versão auditada no lugar
        for i, r in enumerate(t_list):
            if (name, r['id']) in OURS_EDITS_APPLY and r['id'] in o:
                t_list[i] = o[r['id']]
                report.append(f'  ~ {key} {r["id"]} := versão auditada do local')

        # 3. adições do lado local (ID fora da base), em ordem do arquivo local
        o_adds = [r for r in (ours.get(key) or []) if r['id'] not in b]

        # 3a. deduplicação: a mesma mensagem registrada pelos dois lados — fica a
        #     de theirs (transcrição mais completa), fontes do local unificadas + nota
        keep = []
        for r in o_adds:
            tid = DEDUP_KEEP_THEIRS.get((name, r['id']))
            if not tid:
                keep.append(r)
                continue
            idx = next((i for i, x in enumerate(t_list) if x['id'] == tid), None)
            if idx is None:
                keep.append(r)  # alvo inesperadamente ausente: não descarta
                continue
            merge_sources_into(t_list[idx], r)
            note = (f' [Deduplicado 2026-10-26 (merge): a auditoria de 19/10 registrara esta mesma '
                    f'mensagem em transcrição parcial (ex-{r["id"]}, lote {r.get("added_in")}); '
                    f'consolidada nesta transcrição; fontes unificadas.]')
            t_list[idx]['editorial_note'] = (t_list[idx].get('editorial_note') or '') + note
            report.append(f'  = {key} {tid} mantém de theirs; ex-local {r["id"]} consolidado (fontes+nota)')
        o_adds = keep

        # 3b. renumeração das colisões: ID já usado por theirs ou por adições
        #     do local que conservam o ID original (reservados antes)
        kept_ids = {r['id'] for r in o_adds if r['id'] not in t_ids}
        used = set(t_ids) | kept_ids
        counter = max((int(m.group(1)) for r in used
                       if (m := re.fullmatch(re.escape(prefix) + r'-(\d+)', r))), default=0)
        renumbered = {}
        for r in o_adds:
            if r['id'] in used:
                counter += 1
                while f'{prefix}-{counter:05d}' in used:
                    counter += 1
                new_id = f'{prefix}-{counter:05d}'
                used.add(new_id)
                renumbered[new_id] = r
            else:
                used.add(r['id'])
                renumbered[r['id']] = r

        for rid, r in renumbered.items():
            pos = insert_pos(t_list, r)
            rec = dict(r)
            old_id = r['id']
            rec['id'] = rid
            t_list.insert(pos, rec)
            where = 'fim' if pos == len(t_list) - 1 else f'antes de {t_list[pos + 1]["id"]}'
            note = f' (renumerado de {old_id})' if rid != old_id else ''
            report.append(f'  + {key} {rid}{note} @ {where}')

        # 4. sanidade: IDs únicos e ordem cronológica — espelha exatamente o
        #    checkOrder do validate.mjs (só pares adjacentes, precision minute/date)
        ids = [r['id'] for r in t_list]
        assert len(ids) == len(set(ids)), f'{name}/{key}: IDs duplicados após merge'
        for r1, r2 in zip(t_list, t_list[1:]):
            if not (ordered(r1) and ordered(r2)):
                continue
            if r1['date'] != r2['date']:
                assert r1['date'] < r2['date'], f'{name}/{key}: {r1["id"]} ({r1["date"]}) depois vira {r2["id"]} ({r2["date"]})'
            elif r1.get('time') and r2.get('time'):
                assert r1['time'] <= r2['time'], f'{name}/{key}: {r1["id"]}/{r1["time"]} > {r2["id"]}/{r2["time"]}'

        merged[key] = t_list

    out = json.dumps(merged, ensure_ascii=False, indent=1) + '\n'
    with open(f'{ROOT}/{path}', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(out)

    n_b = len(base.get('messages') or []) + len(base.get('timeline_events') or [])
    n_o = len(ours.get('messages') or []) + len(ours.get('timeline_events') or [])
    n_t = len(theirs.get('messages') or []) + len(theirs.get('timeline_events') or [])
    n_m = len(merged.get('messages') or []) + len(merged.get('timeline_events') or [])
    print(f'{name}: base={n_b} ours={n_o} theirs={n_t} -> MERGED={n_m}')
    for line in report:
        print(line)
    return n_m


if __name__ == '__main__':
    total = sum(merge_thread(t) for t in THREADS)
    print(f'\nTOTAL registros (msgs+eventos) nos threads resolvidos: {total}')
