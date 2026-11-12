# v3 (12.11): холодный старт — сильная фраза лектора из этого же ролика в первые секунды (у 6 роликов начало было вялым)
import json, sys
sys.path.insert(0, '/home/claude/work/b2710'); from wtools import *
src = open('/home/claude/work/b2710/shorts/plan.py').read().split('plan = []')[0]; exec(src.split('from wtools import *')[1])
P = {sid: segs for sid, title, segs in P}
HK = {
 's01_prototip_eto_tz': [('на мой взгляд, и понятная', 790, 'задания, прототип.', 792)],
 's02_ot_prototipa_k_api': [('есть схема бэкэнда', 876, 'схема фронтэнда в виде прототипа', 880)],
 's04_vykinte_i_sdelayte_zanovo': [('просто его выкинуть', 1337, 'совсем не больно.', 1340)],
 's06_monolit_v_agenta': [('если вы возьмете большой', 2415, 'Много глюков.', 2421)],
 's10_freymvork_za_12_chasov': [('потратил прям полных', 6423, 'хоть как-то взлетела', 6428)],
}
BODY = {
 's03_chto_nuzhno_bylo_zakazchiku': [('вот объяснил заказчик,', 1245, 'что на самом деле нужно было заказчику.', 1252)] + P['s03_chto_nuzhno_bylo_zakazchiku'][1:],
 's06_monolit_v_agenta': [P['s06_monolit_v_agenta'][0], ('Мы сначала ходим по', 2390, 'спецификацию делается очень хорошо,', 2413)],
}
out = []
for sid in list(HK) + ['s03_chto_nuzhno_bylo_zakazchiku']:
    segs = HK.get(sid, []) + BODY.get(sid, P[sid]); S = []; IDX = []
    for a, an, b, bn in segs:
        s, e, i, j = seg(a, an, b, bn); S.append([round(s - 0.06, 2), round(e, 2)]); IDX.append([i, j])
    nh = len(HK.get(sid, []))
    print(sid, nh, round(sum(e - s for s, e in S), 1), S)
    json.dump({'fps': 25, 'opener_after': None, 'segments': [{'in': s, 'out': e, 'tag': 'hook' if k < nh else 'main'} for k, (s, e) in enumerate(S)]}, open(f'v3/{sid}.takes.json', 'w'))
    out.append({'id': sid, 'segs': S, 'idx': IDX, 'hook': nh})
json.dump(out, open('v3/plan3.json', 'w'), ensure_ascii=False, indent=1)
