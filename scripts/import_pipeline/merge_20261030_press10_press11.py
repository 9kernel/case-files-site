# merge_20261030_press10_press11.py — resolução do merge 8826004 (auditoria 26/10
# local) × origin/main 997e9ca (rodadas press10 27/10 + press11 29/10).
#
# As duas linhas implementaram em paralelo as mesmas pendências da auditoria de
# 26/10. Conferência registro a registro:
#
#   - Colchetes editoriais (6 threads): os dois lados chegaram a resultados
#     IDÊNTICOS de conteúdo → fica a versão de theirs (notas "[Corrigido
#     2026-10-27]" + adições próprias deles, ex.: ana-matos m-00076). EXCEÇÃO:
#     walfrido-mares-guia m-00009 — theirs removeu também a palavra "Anvisa",
#     quebrando a sintaxe ("presidir a é"); a palavra é original (o colchete da
#     Folha é marcação de link) → fica o registro do lado local.
#   - Valadão abril/2024: ambas as linhas inseriram as 4 mensagens da Pública
#     18/10 (duplicidade real). Fica a versão de theirs (transcrição correta —
#     "Eu apoio diversos eventos e debates" — e notas com cruzamentos UOL/ICL),
#     CORRIGIDA pela evidência das capturas publicadas, que o lado remoto não
#     consultou: m-00030 carimbada 2024-04-29 13:42:17 (não 27/04); m-00031 e
#     m-00032 rebaixadas a mês (seguem, na ordem de citação, a mensagem de
#     29/04 13:42 — 27/04 é impossível para elas); m-00033/m-00034 (ICL, 27/04)
#     reposicionadas antes do bloco de 29/04 para leitura cronológica; o "Sim"
#     de Valadão (visível só na captura, 13:42:59) entra como m-00036.
#   - Valadão m-00023/m-00026/m-00027: theirs removeu as datas por julgar o ano
#     indemonstrável no texto ("dois meses antes da prisão de novembro/2025");
#     os carimbos das capturas publicadas (2024-08-15 12:36:36 e 2024-09-17
#     09:13:16) confirmam o ano de 2024 na própria fonte → datas/horas
#     restauradas; m-00027 com remetente corrigido para Vorcaro e transcrição
#     ampliada ao texto completo da captura (lado local, conferido).
#   - Nikolas: resolução de theirs (m-00001 com transcrição integral g1 incluindo
#     o trecho de Londres) aceita sem alteração — resolve a pendência do áudio
#     de desculpas como parte do mesmo áudio de 30/03/2025.
#
# Arquivos derivados (network, search-index, whatsnew, auditoria) são
# regenerados pelos scripts após esta resolução.

import json
import subprocess

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()


def load(path):
    with open(f'{ROOT}/{path}', encoding='utf-8') as fh:
        return json.load(fh)


def save(path, data):
    with open(f'{ROOT}/{path}', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


def by_id(lst, mid):
    return next(x for x in lst if x['id'] == mid)


# ------------------------------------------------------------------ Valadão
path = 'data/threads/andre-valadao-daniel-vorcaro.json'
t = load(path)
msgs = t['messages']

# 1. m-00030 — carimbo da captura: 2024-04-29 13:42:17
m = by_id(msgs, 'm-00030')
m['date'] = '2024-04-29'
m['time'] = '13:42'
m['timestamp_precision'] = 'minute'
m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
    ' [Corrigido 2026-10-30 (merge): o carimbo visível na captura publicada pela reportagem registra '
    '2024-04-29 13:42:17 -03:00 — a postagem de Nikolas é de 27/04/2024 e esta mensagem é de 29/04, não '
    'do dia 27.]')

# 2. m-00031 e m-00032 — seguem a mensagem carimbada de 29/04 na ordem de citação:
#    27/04 é impossível; dia não individualmente demonstrável → mês
for mid in ('m-00031', 'm-00032'):
    m = by_id(msgs, mid)
    m['date'] = '2024-04'
    m['time'] = None
    m['timestamp_precision'] = 'month'
    m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
        ' [Corrigido 2026-10-30 (merge): na ordem de citação da reportagem esta mensagem segue a mensagem '
        'carimbada em 29/04/2024 13:42 — a data de 27/04 é incompatível; o dia não é individualmente '
        'demonstrável, precisão reduzida a mês.]')

# 3. m-00029 — contraditório da rodada local acrescentado à nota
m = by_id(msgs, 'm-00029')
m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
    ' Procurado, Vorcaro não havia se manifestado até a publicação (a assessoria anunciou nota para 19/10).')

# 4. m-00033/m-00034 (ICL, 27/04) reposicionadas antes do bloco de 29/04
for mid in ('m-00033', 'm-00034'):
    rec = by_id(msgs, mid)
    msgs.remove(rec)
    msgs.insert(msgs.index(by_id(msgs, 'm-00030')), rec)

# 5. m-00036 — o "Sim" de Valadão, visível apenas na captura publicada (13:42:59)
sim = {
    'id': 'm-00036', 'date': '2024-04-29', 'time': '13:42', 'timestamp_precision': 'minute',
    'sender_id': 'andre-valadao', 'content_kind': 'verbatim', 'content': 'Sim',
    'editorial_note': (
        'Mensagem não citada no texto corrido da reportagem; transcrita da captura publicada pela Agência '
        'Pública (carimbo 2024-04-29 13:42:59 -03:00), na sequência imediata da mensagem anterior. '
        'Incluída na resolução do merge de 30/10/2026.'),
    'verification': {
        'level': 'public_investigation', 'origin': 'press report', 'authority': 'Polícia Federal',
        'court': None, 'case': None, 'document': None, 'page': None, 'figure': None,
        'official_url': None, 'primary_document_located': False, 'verified_at': '2026-10-30',
        'proceeding': ('PF — conversas interceptadas às quais a Agência Pública teve acesso (18/10/2026); '
                       'a reportagem não publica a peça individualmente')},
    'sources': {'primary': None, 'secondary': [
        {'publication': 'Agência Pública', 'date': '2026-10-18',
         'url': 'https://apublica.org/2026/10/banco-master-a-amigo-vorcaro-se-disse-apoiador-da-direita/'}]},
    'source_ref': 'Captura publicada por Agência Pública (2026-10-18)',
    'added_in': 'ingest-publica-20261026',
}
msgs.insert(msgs.index(by_id(msgs, 'm-00030')) + 1, sim)

# 6. m-00023 — data/hora da captura (09:12:33) e posição antes do pedido de 09:13:16
m = by_id(msgs, 'm-00023')
m['date'] = '2024-09-17'
m['time'] = '09:12'
m['timestamp_precision'] = 'minute'
m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
    ' [Data e hora acrescentadas 2026-10-30 a partir do carimbo da captura publicada '
    '(2024-09-17 09:12:33 -03:00), imediatamente antes do pedido de 09:13:16; posição ajustada conforme '
    'a captura. Autoria conforme o texto da reportagem (“responde o ex-banqueiro”).]')
msgs.remove(m)
msgs.insert(msgs.index(by_id(msgs, 'm-00027')), m)

# 7. m-00026 — data/hora restauradas pelo carimbo (2024-08-15 12:36:36)
m = by_id(msgs, 'm-00026')
m['date'] = '2024-08-15'
m['time'] = '12:36'
m['timestamp_precision'] = 'minute'
m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
    ' [Corrigido 2026-10-30 (merge): data e hora restauradas a partir do carimbo da captura publicada '
    'junto à passagem (2024-08-15 12:36:36 -03:00) — o ano 2024 consta do carimbo, resolvendo a '
    'indeterminação registrada em 2026-10-29.]')

# 8. m-00027 — captura: bolha enviada por DV, 2024-09-17 09:13:16; texto completo
m = by_id(msgs, 'm-00027')
m['sender_id'] = 'daniel-vorcaro'
m['content_kind'] = 'verbatim'
m['content'] = ('Preciso falar contigo sobre alguns assuntos, inclusive aquele fundo que você mencionou '
                'e depois falamos sobre o sistema de pagamentos e que sobre a fintech, que por sinal tá '
                'indo super bem e sem dúvida é algo que pode ficar grande demais')
m['date'] = '2024-09-17'
m['time'] = '09:13'
m['timestamp_precision'] = 'minute'
m['editorial_note'] = (m.get('editorial_note') or '').rstrip() + (
    ' [Corrigido 2026-10-30 (merge): ano, hora e remetente confirmados/corrigidos pela captura publicada '
    'junto à passagem — carimbo 2024-09-17 09:13:16 -03:00 em bolha enviada por DV; remetente '
    'reatribuído a Vorcaro (o texto completa “aquele fundo que você mencionou”, pedido antes feito por '
    'Valadão) e transcrição ampliada do fragmento citado no texto corrido ao conteúdo completo da '
    'captura. A indeterminação de ano registrada em 2026-10-27 fica resolvida pelo carimbo.]')

save(path, t)
print(f'[valadao] {len(msgs)} mensagens; correções de captura aplicadas')

# ------------------------------------------- walfrido-mares-guia m-00009 (nosso)
import subprocess as sp
ours_raw = sp.run(['git', 'show', 'HEAD:data/threads/walfrido-mares-guia-daniel-vorcaro.json'],
                  capture_output=True, text=True, encoding='utf-8', check=True).stdout
ours_rec = next(x for x in json.loads(ours_raw)['messages'] if x['id'] == 'm-00009')
path = 'data/threads/walfrido-mares-guia-daniel-vorcaro.json'
t = load(path)
i = next(i for i, x in enumerate(t['messages']) if x['id'] == 'm-00009')
t['messages'][i] = ours_rec
save(path, t)
print('[walfrido-mares-guia] m-00009 := registro do lado local (palavra "Anvisa" é original)')

# ------------------------------------------------------------------ threads.json
path = 'data/threads.json'
idx = load(path)
e = next(x for x in idx if x['id'] == 'andre-valadao-daniel-vorcaro')
e['message_count'] = 36
save(path, idx)
print('[threads.json] andre-valadao: message_count=36')

# sanidade: ordem cronológica (espelha checkOrder — adjacência + minute/date)
for f in ('andre-valadao-daniel-vorcaro', 'walfrido-mares-guia-daniel-vorcaro'):
    t = load(f'data/threads/{f}.json')
    for key in ('messages', 'timeline_events'):
        lst = t.get(key) or []
        ids = [r['id'] for r in lst]
        assert len(ids) == len(set(ids)), f'{f}/{key}: IDs duplicados'
        for r1, r2 in zip(lst, lst[1:]):
            ordered = lambda r: r.get('timestamp_precision') in ('minute', 'date')
            if not (ordered(r1) and ordered(r2)):
                continue
            if r1['date'] != r2['date']:
                assert r1['date'] < r2['date'], f'{f}/{key}: {r1["id"]}>{r2["id"]} ({r1["date"]}>{r2["date"]})'
            elif r1.get('time') and r2.get('time'):
                assert r1['time'] <= r2['time'], f'{f}/{key}: {r1["id"]}/{r1["time"]}>{r2["id"]}/{r2["time"]}'
print('[sanidade] IDs únicos e ordem cronológica OK')
