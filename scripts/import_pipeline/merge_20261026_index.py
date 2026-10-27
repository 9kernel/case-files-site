# merge_20261026_index.py — resolução do merge para os índices data/threads.json
# e data/participants.json (26/10/2026).
#
# Regras (AGENTS.md §2c: ordem histórica dos arquivos é preservada, nada reordenado):
#   1. Lista-base = versão do origin/main (theirs), que já traz seus participantes/
#      conversas novas; adições só do lado local são inseridas:
#      - threads.json: em posição alfabética entre as entradas vizinhas (o índice é
#        alfabético por id);
#      - participants.json: imediatamente após o último vizinho comum que as antecede
#        no arquivo local (o arquivo NÃO é alfabético — ordem histórica).
#   2. Entradas comuns: campo a campo, versão de theirs; se o lado local editou um
#        campo que theirs não tocou (vs. base), vale a versão auditada do local.
#        Campos editados pelos DOIS lados são reportados para decisão manual.
#   3. message_count/last_message_date/last_message_preview são recalculados a partir
#        dos data/threads/*.json já mergeados (validador exige contagem exata).

import json
import re
import subprocess

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()


def git_show(ref, path):
    out = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, text=True, encoding='utf-8', check=True).stdout
    return json.loads(out)


def load(path):
    with open(f'{ROOT}/{path}', encoding='utf-8') as fh:
        return json.load(fh)


def dump(path, data):
    with open(f'{ROOT}/{path}', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


def merge_entries(base_list, ours_list, theirs_list, keyfield, label, manual_conflicts):
    base = {e[keyfield]: e for e in base_list}
    ours = {e[keyfield]: e for e in ours_list}
    theirs = {e[keyfield]: e for e in theirs_list}

    result = [dict(e) for e in theirs_list]
    theirs_order = [e[keyfield] for e in theirs_list]

    # entradas só do local: inserir (em ordem do arquivo local, preservando a
    # ordem relativa entre adjacentes)
    ours_only = [e for e in ours_list if e[keyfield] not in theirs]
    inserted = {}  # id -> posição no result
    for e in ours_only:
        pos = len(result)
        if label == 'threads.json':
            for i, tid in enumerate(theirs_order):
                if tid > e[keyfield]:
                    pos = i
                    break
        else:
            # participants.json: após o último vizinho (comum ou já inserido) que
            # antecede no arquivo local
            ours_order = [x[keyfield] for x in ours_list]
            idx = ours_order.index(e[keyfield])
            anchor = next((x for x in reversed(ours_order[:idx]) if x in theirs or x in inserted), None)
            if anchor in inserted:
                pos = inserted[anchor] + 1
            elif anchor in theirs:
                pos = theirs_order.index(anchor) + 1
            else:
                pos = len(result)
        # compensa inserções anteriores neste mesmo ponto ou antes
        shift = sum(1 for p in inserted.values() if p <= pos)
        pos += shift
        result.insert(pos, dict(e))
        inserted[e[keyfield]] = pos
        print(f'  + {label}: entrada {e[keyfield]} inserida @ pos {pos}')

    # entradas comuns: mesclar campos
    for i, e in enumerate(result):
        k = e[keyfield]
        if k not in ours or k not in base:
            continue
        o, b = ours[k], base[k]
        for field in set(list(o.keys()) + list(b.keys())):
            ov, bv, tv = o.get(field), b.get(field), e.get(field)
            ours_changed = json.dumps(ov, sort_keys=True) != json.dumps(bv, sort_keys=True)
            theirs_changed = json.dumps(tv, sort_keys=True) != json.dumps(bv, sort_keys=True)
            if ours_changed and not theirs_changed and field not in ('message_count', 'last_message_date', 'last_message_preview'):
                e[field] = ov
            elif ours_changed and theirs_changed and json.dumps(ov, sort_keys=True) != json.dumps(tv, sort_keys=True):
                if field not in ('message_count', 'last_message_date', 'last_message_preview'):
                    manual_conflicts.append(f'{label} {k}.{field}: ours={json.dumps(ov)[:120]} theirs={json.dumps(tv)[:120]}')
        result[i] = e
    return result


def recompute_threads_stats(index):
    """Recalcula message_count de TODAS as entradas contra os arquivos (validador
    exige exato), mas só reescreve last_message_date/last_message_preview nas
    conversas cujo arquivo foi alterado pelo merge — nas demais, os valores
    publicados de origin/main são preservados (convenção dos mantenedores)."""
    import os
    changed_files = set()
    threads_dir = f'{ROOT}/data/threads'
    for f in os.listdir(threads_dir):
        if not f.endswith('.json'):
            continue
        with open(os.path.join(threads_dir, f), encoding='utf-8') as fh:
            current = fh.read()
        r = subprocess.run(['git', 'show', f'origin/main:data/threads/{f}'], capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0 or r.stdout != current:
            changed_files.add(f[:-5])

    for e in index:
        p = os.path.join(threads_dir, f"{e['id']}.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            t = json.load(fh)
        msgs = t.get('messages') or []
        e['message_count'] = len(msgs)
        if e['id'] in changed_files and msgs:
            last = msgs[-1]
            content = (last.get('content') or '').replace('\n', ' ')
            e['last_message_preview'] = content[:80]
            if last.get('date'):
                e['last_message_date'] = last['date']
    print(f'  [stats] {len(changed_files)} arquivos de thread alterados vs origin/main')
    return index


if __name__ == '__main__':
    manual = []

    # threads.json
    for path, key in (('data/threads.json', 'id'), ('data/participants.json', 'id')):
        base_list = git_show('200148f', path)
        ours_list = git_show('HEAD', path)
        theirs_list = git_show('origin/main', path)
        print(f'\n== {path} ==  base={len(base_list)} ours={len(ours_list)} theirs={len(theirs_list)}')
        merged = merge_entries(base_list, ours_list, theirs_list, key, path.split('/')[-1], manual)
        if path == 'data/threads.json':
            merged = recompute_threads_stats(merged)
        dump(path, merged)
        print(f'   -> {len(merged)} entradas gravadas')

    print('\n== conflitos campo-a-campo para decisão manual ==')
    for m in manual:
        print('  !!', m)
    if not manual:
        print('  (nenhum)')
