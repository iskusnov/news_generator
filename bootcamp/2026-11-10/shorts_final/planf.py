# Финал урока 08 (12.11): холодный старт — сочная фраза лектора из этого же ролика
import json, sys
sys.path.insert(0, '/home/claude/work/b1110'); from wtools import *
src = open('../plan.py').read().split('plan=[]')[0]; exec(src.split('from wtools import *')[1])
P = {sid: segs for sid, title, segs in P}
HK = {'s01_zachem_multiagenty': ('Вот что меня лично', 547, 'в этих мультиагентских системах.', 550),
      's04_ne_pishi_testy': ('сейчас прошу не писать', 2610, 'работает с первого раза.', 2613),
      's05_agent_nochyu': ('утром просыпаюсь, а он', 2822, 'сетевой свой пишет.', 2825),
      's09_eskalaciya_v_telegram': ('Она берет и в', 7970, 'мне пишет эскалацию.', 7973),
      's10_na_chto_tratit_dengi': ('а для исполнения можно', 10433, 'или 30B использовать,', 10437)}
OUT = []
for sid in ['s01_zachem_multiagenty', 's03_agenty_boltayut_tekstom', 's04_ne_pishi_testy', 's05_agent_nochyu', 's06_chto_takoe_guardrail', 's09_eskalaciya_v_telegram', 's10_na_chto_tratit_dengi']:
    segs = ([HK[sid]] if sid in HK else []) + P[sid]; S = []; IDX = []
    for n, (a, an, b, bn) in enumerate(segs):
        s, e, i, j = seg(a, an, b, bn)
        if sid == 's06_chto_takoe_guardrail' and n == 0: i += 2; s = W[i]['start']   # без «Так вот,»
        S.append([round(s - 0.04, 2), round(e, 2)]); IDX.append([i, j])
    nh = 1 if sid in HK else 0
    json.dump({'fps': 25, 'opener_after': None, 'segments': [{'in': s, 'out': e, 'tag': 'hook' if k < nh else 'main'} for k, (s, e) in enumerate(S)]}, open(sid + '.takes.json', 'w'))
    OUT.append({'id': sid, 'segs': S, 'idx': IDX, 'hook': nh}); print(sid, nh, S[:2], W[IDX[0][0]]['word'])
json.dump(OUT, open('planf.json', 'w'), ensure_ascii=False, indent=1)
