# Моушн-сцены v2: старые сцены переносятся по исходнику (старый edl → исходник → новый edl), хуки — новые.
import json, copy
src = open('../motion_scenes.py').read().split('SPECS =')[0]; exec(src)   # S, kin, st, A, steps, CX
HOOK = {'s02_plan_bomba': 2, 's07_proverki_v_promptah': 2, 's08_500_agentov': 0}
def ln(e): return e['src_out'] - e['src_in']
def mapper(sid):
    O = json.load(open(sid + '.old.edl.json'))['edl']; N = json.load(open(sid + '.edl.json'))['edl']; h = HOOK[sid]
    OT = O[-1]['rec'] + ln(O[-1]); NT = N[-1]['rec'] + ln(N[-1])
    def f(t):
        if t >= OT - 0.05: return round(NT, 2)
        e = next((e for e in O if e['rec'] <= t < e['rec'] + ln(e)), None)
        if e is None: e = min(O, key=lambda e: abs(e['rec'] - t)); src = e['src_in']
        else: src = e['src_in'] + t - e['rec']
        best = None
        for n in N[h:]:
            if n['src_in'] - 0.02 <= src <= n['src_out'] + 0.02: return round(n['rec'] + max(0, src - n['src_in']), 2)
            d = min(abs(src - n['src_in']), abs(src - n['src_out']))
            if best is None or d < best[0]: best = (d, n['rec'] + (0 if abs(src - n['src_in']) < abs(src - n['src_out']) else ln(n)))
        return round(best[1], 2)
    return f
def remap(x, f):
    if isinstance(x, dict): return {k: (f(v) if k in ('at', 'out') and isinstance(v, (int, float)) else remap(v, f)) for k, v in x.items()}
    if isinstance(x, list): return [remap(v, f) for v in x]
    return x
NEW = {}
f = mapper('s02_plan_bomba'); sc = [remap(s, f) for s in S['s02_plan_bomba'][1:]]
sc = [s for s in sc if s['out'] - s['at'] > 0.3 and not any(a.get('t') == '6–10' for a in s.get('actors', []))]
NEW['s02_plan_bomba'] = [kin(0.0, 5.04, [{"t": "6–10 итераций", "at": 0.9, "hl": ["6–10"]}, {"t": "чтобы план", "at": 3.2, "size": 2}, {"t": "стал хорошим", "at": 3.8, "size": 2, "hl": ["хорошим"]}])] + sc
f = mapper('s07_proverki_v_promptah'); sc = [remap(s, f) for s in S['s07_proverki_v_promptah'][1:]]
NEW['s07_proverki_v_promptah'] = [kin(0.0, 2.84, [{"t": "Модели доверять нельзя", "at": 0.05, "size": 2, "hl": ["нельзя"]}, {"t": "Тем не менее —", "at": 1.0, "size": 3}, {"t": "проскакивает", "at": 1.5, "size": 2, "hl": ["проскакивает"]}])] + sc
f = mapper('s08_500_agentov'); sc = [remap(s, f) for s in S['s08_500_agentov'][1:]]
NEW['s08_500_agentov'] = [kin(0.0, 3.6, [{"t": "500 агентов.", "at": 0.1}, {"t": "В какой ресурс", "at": 0.7, "size": 2}, {"t": "мы упрёмся?", "at": 1.2, "size": 2, "hl": ["упрёмся?"]}])] + sc
for sid, sc in NEW.items():   # первая сцена после хука — встык к хуку
    if HOOK[sid]: sc[1]['at'] = sc[0]['out']
    for a, b in zip(sc, sc[1:]):
        if 0 < b['at'] - a['out'] < 0.5: b['at'] = a['out']
OUT = []
for sid, scenes in NEW.items():
    s = json.load(open(sid + '.spec.json')); s['scenes'] = scenes
    s['pv'] = [1.5, 6.0, 14.0, 24.0, 33.0, round(s['dur'] - 1.0, 2)]
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1); OUT.append(s)
    print(sid, [(x['kind'], x['at'], x['out']) for x in scenes])
json.dump(OUT, open('specs_motion.json', 'w'), ensure_ascii=False)
