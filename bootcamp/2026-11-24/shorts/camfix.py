# Камера Zoom (avo) показала не лектора (тёмная плитка/другой участник) — этот отрезок куска показываем экраном (scr=1).
# Кусок делится в провале огибающей рядом с границей; время ролика не меняется. Запуск после buildf.py.
import json, sys, numpy as np
sys.path.insert(0, '/home/claude/work/b1124'); from env import snap
A = np.memmap('/home/claude/work/b1124/avo.raw', np.uint8, 'r', shape=(6513, 180, 320))
bad = lambda t: A[t].mean() < 35 or A[t].mean() > 100
q = lambda x: round(round(x / 0.04) * 0.04, 2)
for f in sys.argv[1:]:
    D = json.load(open(f)); out = []
    for e in D['edl']:
        if e.get('scr'): out.append(e); continue
        a, b = e['src_in'], e['src_out']; secs = [t for t in range(int(a), int(b) + 1) if bad(t)]
        if not secs: out.append(e); continue
        runs = []
        for t in secs:
            if runs and t == runs[-1][1] + 1: runs[-1][1] = t
            else: runs.append([t, t])
        cuts = []
        for r0, r1 in runs:
            s0, s1 = r0 - 0.5, r1 + 1.0
            s0 = a if s0 - a < 0.6 else q(snap(s0, -0.3, 0.0)[0]); s1 = b if b - s1 < 0.6 else q(snap(s1, 0.0, 0.3)[0])
            cuts.append((s0, s1))
        t = a
        for s0, s1 in cuts:
            if s0 > t + 0.01: out.append(dict(e, src_in=t, src_out=s0))
            out.append(dict(e, src_in=s0, src_out=s1, scr=1)); t = s1
        if t < b - 0.01: out.append(dict(e, src_in=t, src_out=b))
        print(f, a, b, '→ экран', cuts)
    r = 0
    for e in out: e['rec'] = round(r, 2); r += e['src_out'] - e['src_in']
    assert abs(r - D['total']) < 0.01, (f, r, D['total'])
    D['edl'] = out; json.dump(D, open(f, 'w'), indent=1)
