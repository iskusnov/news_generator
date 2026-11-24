# Края кусков edl — в провал огибающей (Whisper склеивает слова): out/in, попавшие на речь (> −40 дБ), сдвигаются к минимуму ±0,12 с; rec пересчитывается.
import json, sys
sys.path.insert(0, '/home/claude/work/b1124'); from env import db, snap
q = lambda x: round(round(x / 0.04) * 0.04, 2)
for f in sys.argv[1:]:
    D = json.load(open(f)); E = D['edl']; ch = []
    for k, e in enumerate(E):
        if db(e['src_out'] - 0.015) > -40:
            t = snap(e['src_out'], -0.12, 0.12)[0]
            nx = E[k + 1]['src_in'] if k + 1 < len(E) and E[k + 1]['src_in'] > e['src_out'] else 1e9
            t = min(t, nx - 0.04); ch.append(('out', e['src_out'], q(t))); e['src_out'] = q(t)
        if db(e['src_in'] + 0.015) > -40:
            t = snap(e['src_in'], -0.12, 0.05)[0]
            pv = E[k - 1]['src_out'] if k and E[k - 1]['src_out'] < e['src_in'] else -1
            t = max(t, pv + 0.04); ch.append(('in', e['src_in'], q(t))); e['src_in'] = q(t)
    r = 0
    for e in E: e['rec'] = round(r, 2); r += e['src_out'] - e['src_in']
    D['total'] = round(r, 2); json.dump(D, open(f, 'w'), indent=1)
    print(f, D['total'], [c for c in ch if abs(c[1] - c[2]) > 0.03])
