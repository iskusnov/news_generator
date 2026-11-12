# Субтитры: только слова из запланированных кусков (Whisper иногда даёт соседним словам перекрывающиеся тайминги) + правки распознавания.
import json, sys
sys.path.insert(0, '/home/claude/work/b2710'); from wtools import W
FIX = json.load(open('/home/claude/work/b2710/shorts/subfix.json'))
P = {p['id']: p for p in json.load(open('/home/claude/work/b2710/shorts/plan.json'))}
for sid, p in P.items():
    f = f'/home/claude/work/b2710/shorts/{sid}.spec.json'; s = json.load(open(f))
    E = json.load(open(f'/home/claude/work/b2710/shorts/{sid}.edl.json'))['edl']
    ok = set()
    for i, j in p['idx']:
        for k in range(i, j + 1):
            w = W[k]
            for e in E:
                if e['src_in'] - 0.08 <= w['start'] < e['src_out']:
                    ok.add(round(e['rec'] + max(0, w['start'] - e['src_in']), 2))
    # слова, которые reels.py потерял на границе куска (начало раньше src_in на миллисекунды) — добавляем
    for c in s['chunks']:
        c['words'] = [w for w in c['words'] if any(abs(w['s'] - t) < 0.03 for t in ok)]
        for w in c['words']: w['t'] = FIX.get(w['t'], w['t'])
    s['chunks'] = [c for c in s['chunks'] if c['words']]
    json.dump(s, open(f, 'w'), ensure_ascii=False)
