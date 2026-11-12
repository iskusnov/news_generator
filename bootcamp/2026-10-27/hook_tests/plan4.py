# Тест 4 вариантов старта (12.11): A — вопрос-карточка 1.5–2 с (без звука речи) → ответ лектора; B — самая сочная фраза из середины в ноль.
import json, sys
sys.path.insert(0, '/home/claude/work/b2710'); from wtools import *
src = open('/home/claude/work/b2710/shorts/plan.py').read().split('plan = []')[0]; exec(src.split('from wtools import *')[1])
P = {sid: segs for sid, title, segs in P}
NEW = {'s05_60_agentov': [('А 60 агентов мы', 2262, 'запустить можем.', 2263)] + P['s05_60_agentov'],
       's09_zoom_s_zakazchikom': [('количество правок с', 6915, 'итерации уменьшалось', 6918)] + P['s09_zoom_s_zakazchikom']}
PL = {p['id']: p for p in json.load(open('../v3/plan3.json')) if p['id'] in ('s01_prototip_eto_tz', 's06_monolit_v_agenta')}
for sid, segs in NEW.items():
    S, IDX = [], []
    for a, an, b, bn in segs:
        s, e, i, j = seg(a, an, b, bn); S.append([round(s - 0.06, 2), round(e, 2)]); IDX.append([i, j])
    json.dump({'fps': 25, 'opener_after': None, 'segments': [{'in': s, 'out': e, 'tag': 'hook' if k == 0 else 'main'} for k, (s, e) in enumerate(S)]}, open(sid + '.takes.json', 'w'))
    PL[sid] = {'id': sid, 'segs': S, 'idx': IDX, 'hook': 1}
    print(sid, S)
json.dump(list(PL.values()), open('plan4.json', 'w'), ensure_ascii=False, indent=1)
