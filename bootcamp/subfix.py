#!/usr/bin/env python3
"""Правка субтитров шортсов после reels.py: subfix.py <subfix.json> <папка со *.spec.json>
subfix.json: {id: {"seq": [[[старые слова…], [новые слова…]], …], "tail": N}} — замена последовательностей слов
(тайминги берутся у старых слов) и удаление N последних слов (у Whisper они перекрывают конец куска, звука в ролике нет)."""
import sys, json, os
F = json.load(open(sys.argv[1]))
for id, fx in F.items():
    p = os.path.join(sys.argv[2], id + '.spec.json'); S = json.load(open(p))
    flat = [(ci, wi) for ci, c in enumerate(S['chunks']) for wi in range(len(c['words']))]
    txt = lambda: [S['chunks'][ci]['words'][wi]['t'] for ci, wi in flat]
    for old, new in fx.get('seq', []):
        t = txt(); n = len(old)
        for i in range(len(t) - n + 1):
            if t[i:i + n] == old:
                slots = flat[i:i + n]
                for k, (ci, wi) in enumerate(slots):
                    w = S['chunks'][ci]['words'][wi]
                    w['t'] = new[k] if k < len(new) else None
                    if k == n - 1 and len(new) > n: w['t'] = ' '.join(new[n - 1:])
                break
        else: print(id, 'не найдено:', old)
    for ci, wi in flat[len(flat) - fx.get('tail', 0):] if fx.get('tail') else []:
        S['chunks'][ci]['words'][wi]['t'] = None
    for c in S['chunks']: c['words'] = [w for w in c['words'] if w['t']]
    S['chunks'] = [c for c in S['chunks'] if c['words']]
    json.dump(S, open(p, 'w'), ensure_ascii=False, indent=1)
    print(id, 'ок')
