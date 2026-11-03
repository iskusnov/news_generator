#!/usr/bin/env python3
"""Сверка монтажа ДО чистового рендера: текстовый лист склеек + поиск оговорок.

review.py <edl.json> <words.json> [silence.json] [--audio audio.m4a draft.mp3] > review.txt
--audio: звуковой черновик ролика по edl за секунды (до любого рендера видео) — послушать склейки.
Что ищет (всё, что ниже, — повод вырезать или переставить дубль, а не рендерить):
- ПОВТОР: одна и та же пара/тройка слов дважды в пределах 15 с внутри взятого материала (запнулся и сказал заново);
- РАСТЯНУТО: слово длиннее 1,1 с — Whisper «размазал» на нём оговорку, «тьфу» или паузу;
- ОБРЫВ: кусок кончается посреди слова (конец слова позже конца куска);
- ОБРЫВОК: кусок короче 1,2 с из 1–2 слов, за которым склейка, — часто неудачный заход.
Лист склеек: время в ролике, последние слова до склейки | первые слова после — читается за минуту.
"""
import sys, json, re
AUD = None
if '--audio' in sys.argv:
    k = sys.argv.index('--audio'); AUD = sys.argv[k + 1:k + 3]; del sys.argv[k:k + 3]
E = json.load(open(sys.argv[1])); W = json.load(open(sys.argv[2]))['words']
norm = lambda s: re.sub(r'[^\wё-]', '', s.lower())
mm = lambda t: f'{int(t // 60)}:{t % 60:05.2f}'
SIL = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else []
def voiced(a, b):  # сколько из [a,b] не тишина по звуку (Whisper тянет слова через паузы)
    return (b - a) - sum(max(0, min(b, y) - max(a, x)) for x, y in SIL)
issues, lines = [], []
pieces = E['edl']
def ws_in(e): return [w for w in W if e['src_in'] - 0.02 <= w['start'] < e['src_out']]
used = []  # (rec_time, word) всего, что звучит в ролике
for e in pieces:
    ws = ws_in(e)
    for w in ws:
        used.append((e['rec'] + w['start'] - e['src_in'], w))
        if voiced(w['start'], min(w['end'], e['src_out'])) > 1.1:
            issues.append((e['rec'] + w['start'] - e['src_in'], f"РАСТЯНУТО «{w['word']}» {voiced(w['start'], min(w['end'], e['src_out'])):.1f} с — проверь на оговорку"))
    if ws and voiced(e['src_out'], ws[-1]['end']) > 0.25:
        issues.append((e['rec'] + e['src_out'] - e['src_in'], f"ОБРЫВ «{ws[-1]['word']}» обрезано на ~{voiced(e['src_out'], ws[-1]['end']):.2f} с звука"))
    d = e['src_out'] - e['src_in']
    if d < 1.2 and len(ws) <= 2:
        issues.append((e['rec'], f"ОБРЫВОК {d:.1f} с «{' '.join(w['word'] for w in ws)}» — похоже на неудачный заход"))
for n in (3, 2):
    for i in range(len(used) - n):
        g = tuple(norm(used[i + k][1]['word']) for k in range(n))
        if sum(len(x) for x in g) < 7: continue
        for j in range(i + n, len(used) - n + 1):
            if used[j][0] - used[i][0] > 15: break
            if tuple(norm(used[j + k][1]['word']) for k in range(n)) == g:
                issues.append((used[i][0], f"ПОВТОР «{' '.join(used[i + k][1]['word'] for k in range(n))}» в {mm(used[i][0])} и {mm(used[j][0])} — оставить один дубль"))
                break
seen, out = set(), []
for t, m in sorted(issues):
    key = (round(t), m.split()[0])
    if key not in seen: seen.add(key); out.append(f'  {mm(t)}  {m}')
print(f"СВЕРКА {sys.argv[1]} — длина {mm(E['total'])}, кусков {len(pieces)}")
print(f"\nЗамечания ({len(out)}):" if out else '\nЗамечаний нет.'); print('\n'.join(out))
print('\nСклейки (…до | после…):')
for a, b in zip(pieces, pieces[1:]):
    wa, wb = ws_in(a)[-4:], ws_in(b)[:4]
    print(f"  {mm(b['rec'])}  …{' '.join(w['word'] for w in wa)} | {' '.join(w['word'] for w in wb)}…   (src {a['src_out']:.1f}→{b['src_in']:.1f})")
if AUD:
    import subprocess
    fc, parts, end = '', [], 0.0  # пробелы в монтаже (заставка, паузы) — тишиной, чтобы время совпадало с edl
    for i, e in enumerate(pieces):
        if e['rec'] - end > 0.02:
            fc += f"anullsrc=r=16000:cl=mono,atrim=0:{e['rec'] - end:.3f}[g{i}];"; parts.append(f'[g{i}]')
        fc += f"[0:a]atrim={e['src_in']}:{e['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,aformat=sample_rates=16000:channel_layouts=mono[a{i}];"; parts.append(f'[a{i}]')
        end = e['rec'] + e['src_out'] - e['src_in']
    fc += ''.join(parts) + f'concat=n={len(parts)}:v=0:a=1[o]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', AUD[0], '-filter_complex', fc, '-map', '[o]', '-b:a', '96k', AUD[1]], check=True)
    print(f'\nЗвуковой черновик: {AUD[1]}')
