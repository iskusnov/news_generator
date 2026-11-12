# v3: субтитры по запланированным словам + перенос моушн-сцен со старого монтажа + новые хуки
import json, re, sys, subprocess
sys.path.insert(0, '/home/claude/work/b2710'); from wtools import W
PL = {p['id']: p for p in json.load(open('plan3.json'))}
FIX = json.load(open('../subfix.json'))
C = [dict(c, edl=c['id'] + '.edl.json') for c in json.load(open('../reels_config.json')) if c['id'] in PL]
json.dump(C, open('cfg.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['python3', '/home/claude/news_generator/pipeline/reels.py', 'cfg.json', '../../words.json'], check=True, capture_output=True)
OLD = {s['id']: s for s in json.load(open('../specs_motion.json'))}
HOOKK = {
 's01_prototip_eto_tz': [{"t": "Понятная форма ТЗ —", "at": 0.1, "size": 2}, {"t": "прототип", "at": 2.4, "hl": ["прототип"]}],
 's02_ot_prototipa_k_api': [{"t": "Схема бэкенда —", "at": 0.1, "size": 2}, {"t": "структура БД", "at": 0.9, "size": 2, "hl": ["БД"]}, {"t": "схема фронтенда — прототип", "at": 2.6, "size": 3, "hl": ["прототип"]}],
 's04_vykinte_i_sdelayte_zanovo': [{"t": "Выкинуть и сделать", "at": 0.1, "size": 2}, {"t": "ещё раз", "at": 0.9, "size": 2}, {"t": "совсем не больно", "at": 2.1, "size": 2, "hl": ["не больно"]}],
 's06_monolit_v_agenta': [{"t": "Весь монолит в агента?", "at": 0.1, "size": 2}, {"t": "Захлебнётся", "at": 3.4, "hl": ["Захлебнётся"]}],
 's10_freymvork_za_12_chasov': [{"t": "Полных 12 часов,", "at": 0.1, "size": 2, "hl": ["12"]}, {"t": "чтобы хоть как-то", "at": 2.4, "size": 3}, {"t": "взлетела", "at": 3.6, "hl": ["взлетела"]}],
}
L = lambda e: e['src_out'] - e['src_in']
OUT = []
for sid, p in PL.items():
    E = json.load(open(sid + '.edl.json'))['edl']; s = json.load(open(sid + '.spec.json')); h = p['hook']
    # субтитры: только слова запланированных кусков (допуск на границах), правки распознавания
    ws = []
    for e in E:
        ks = max(([k for k in range(i, j + 1) if e['src_in'] - 0.1 <= W[k]['start'] < e['src_out'] - 0.05] for i, j in p['idx']), key=len)
        for k in ks: ws.append({'t': FIX.get(W[k]['word'], W[k]['word']), 's': round(e['rec'] + max(0, W[k]['start'] - e['src_in']), 2), 'e': round(e['rec'] + min(W[k]['end'], e['src_out']) - e['src_in'], 2)})
    rep = dict(map(tuple, next(c for c in C if c['id'] == sid)['replace']))
    for w in ws: w['t'] = rep.get(w['t'], w['t'])
    ch, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.4 or re.search(r'[.?!,]$', cur[-1]['t']) or sum(len(x['t']) for x in cur) + len(w['t']) > 16): ch.append(cur); cur = []
        cur.append(w)
    if cur: ch.append(cur)
    if ws: ws[0]['t'] = ws[0]['t'][:1].upper() + ws[0]['t'][1:]
    dur, endDur = s['dur'], s['endDur']; s['chunks'] = []
    for n, c in enumerate(ch):
        en = min(ch[n + 1][0]['s'] if n + 1 < len(ch) else dur, c[-1]['e'] + 0.5)
        if c[0]['s'] < dur - endDur: s['chunks'].append({'s': c[0]['s'], 'e': round(min(en, dur - endDur), 2), 'words': [{'t': x['t'], 's': x['s']} for x in c]})
    # сцены: старое время ролика → исходник → новое время (берём куски после хука)
    O = json.load(open(sid + '.old.edl.json'))['edl']; OT = O[-1]['rec'] + L(O[-1]); NT = E[-1]['rec'] + L(E[-1])
    def f(t):
        if t >= OT - 0.05: return round(NT, 2)
        e = next((e for e in O if e['rec'] <= t < e['rec'] + L(e)), None)
        src = e['src_in'] + t - e['rec'] if e else min(O, key=lambda e: abs(e['rec'] - t))['src_in']
        best = None
        for n in E[h:]:
            if n['src_in'] - 0.02 <= src <= n['src_out'] + 0.02: return round(n['rec'] + max(0, src - n['src_in']), 2)
            d0, d1 = abs(src - n['src_in']), abs(src - n['src_out'])
            c = (min(d0, d1), n['rec'] + (0 if d0 < d1 else L(n)))
            if best is None or c[0] < best[0]: best = c
        return round(best[1], 2)
    def remap(x):
        if isinstance(x, dict): return {k: (f(v) if k in ('at', 'out', 'onAt') and isinstance(v, (int, float)) else remap(v)) for k, v in x.items()}
        if isinstance(x, list): return [remap(v) for v in x]
        return x
    old = OLD[sid]; first = old['scenes'][0]
    if h:
        hend = E[h - 1]['rec'] + L(E[h - 1])
        sc = [dict(first, at=0, out=round(hend, 2), lines=HOOKK[sid])] + [remap(x) for x in old['scenes'][1:]]
    else:
        sc = [dict(first, at=0, out=3.0)] + [remap(x) for x in old['scenes'][1:]]
    sc = [x for i, x in enumerate(sc) if i == 0 or x['out'] - x['at'] > 0.3]
    if sid == 's06_monolit_v_agenta': sc = sc[:-1]; sc[-1]['out'] = round(NT, 2)   # «захлебнётся» теперь в хуке
    sc[1]['at'] = sc[0]['out']
    for a, b in zip(sc, sc[1:]):
        if b['at'] < a['out']: b['at'] = a['out']
        if 0 < b['at'] - a['out'] < 0.6: b['at'] = a['out']
    for k in ('tag', 'lector', 'org', 'title', 'num'):
        if k in old: s[k] = old[k]
    s['scenes'] = sc; s['pv'] = [1.5] + [round((x['at'] + x['out']) / 2, 2) for x in sc[1:]] + [round(dur - 0.8, 2)]
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1); OUT.append(s)
    print(sid, dur, [(x['kind'], x['at'], x['out']) for x in sc])
    print('   ', ' '.join(w['t'] for c in s['chunks'][:12] for w in c['words']))
json.dump(OUT, open('specs_motion.json', 'w'), ensure_ascii=False)
