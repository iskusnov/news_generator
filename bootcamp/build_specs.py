#!/usr/bin/env python3
"""specs графики урока: graphics_plan.json (время исходной записи) → specs.json (время итогового видео).
build_specs.py <graphics_plan.json> <edl.json> <out specs.json>
Итоговое видео = пре-ролл (plan.pre с) + смонтированный урок + финальная карта ДЗ (12 с). Плашки в одном месте кадра
(низ слева: глава/термин/цитата/вопрос; справа: цифра) не пересекаются — более поздняя сдвигается."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline'))
plan, E = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
from importlib import util
spec = util.spec_from_file_location('le', os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'lesson_edl.py'))
src = open(spec.origin, encoding='utf-8').read().split("if sys.argv[1] == 'tc':")[0]
ns = {}; exec(src.split('sil_p, words_p')[0], ns); s2r = ns['s2r']
PRE = plan['pre']; T = lambda t: round(s2r(E['edl'], t, PRE), 2)
DUR = dict(chapter=4.5, term=7, quote=6, question=6, stat=8, sting=1.2)
S = [dict(id='preroll', type='preroll', rec=0, dur=PRE, **plan['preroll'])]
names = {p[0]: (p[1], p[2]) for p in plan['parts']}
for n, title, icon, t in plan['parts'][1:]:
    S.append(dict(id=f'sting{n}', type='sting', rec=T(t) - 0.5, dur=1.2))
for part, num, title, t in plan['chapters']:
    S.append(dict(id='ch' + num.replace('.', '_'), type='chapter', rec=T(t) + 0.3, dur=4.5, num=num, title=title,
                  part=f'Часть {part} · {names[part][0]}', icon=names[part][1], total=len(plan['parts']), index=part, top=890))
for i, it in enumerate(plan['items']):
    it = dict(it); t = it.pop('t'); d = it.pop('dur', DUR[it['type']])
    S.append(dict(id=f"{it['type']}{i:02d}", rec=T(t), dur=d, **it))
slot = lambda s: 'r' if s['type'] == 'stat' else 'full' if s['type'] in ('preroll', 'sting', 'hw') else 'bl'
S.sort(key=lambda s: s['rec']); last = {}
for s in S:
    k = slot(s)
    if k in last and s['rec'] < last[k] + 0.5: s['rec'] = round(last[k] + 0.5, 2)
    last[k] = s['rec'] + s['dur']
end = PRE + E['total']
S.append(dict(id='hw', type='hw', rec=round(end, 2), dur=12, **plan['hw']))
json.dump(S, open(sys.argv[3], 'w'), ensure_ascii=False, indent=0)
print(len(S), 'плашек; итог', round(end + 12, 1), 'с;', ', '.join(f"{t}:{sum(1 for s in S if s['type']==t)}" for t in sorted({s['type'] for s in S})))
