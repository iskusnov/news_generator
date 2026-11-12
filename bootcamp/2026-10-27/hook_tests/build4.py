import json, re, sys, subprocess
sys.path.insert(0, '/home/claude/work/b2710'); from wtools import W
PL = {p['id']: p for p in json.load(open('plan4.json'))}
FIX = json.load(open('../subfix.json'))
L = lambda e: e['src_out'] - e['src_in']
CARD0 = {  # A: вопрос на весь кадр, слова по одному; звук речи выключен
 's01_prototip_eto_tz': dict(dur=2.5, lines=[['Как', 'сделать', 'ТЗ,'], ['чтобы', 'заказчик'], ['не', 'переделывал'], ['всё', 'в', 'конце?']], hl={'конце?', 'переделывал'}),
 's05_60_agentov': dict(dur=1.8, lines=[['Нанять'], ['60'], ['бэкендеров?']], hl={'60'}),
}
CARD = {}   # 12.11: Антону больше нравится вариант Б (сочная фраза), карточки убраны
for sid in PL:
    E = json.load(open(sid + '.edl.json'))
    if E['edl'][0].get('mute'):
        E['edl'] = E['edl'][1:]; r = 0.0
        for e in E['edl']: e['rec'] = round(r, 2); r += L(e)
        E['total'] = round(r, 2); json.dump(E, open(sid + '.edl.json', 'w'), indent=1)
for sid, c in CARD.items():   # карточка = кусок без звука перед хуком
    E = json.load(open(sid + '.edl.json'))
    if not E['edl'][0].get('mute'):
        e0 = E['edl'][0]; E['edl'].insert(0, dict(e0, src_out=round(e0['src_in'] + c['dur'], 2), mute=True, scale=1.0))
        r = 0.0
        for e in E['edl']: e['rec'] = round(r, 2); r += L(e)
        E['total'] = round(r, 2); json.dump(E, open(sid + '.edl.json', 'w'), indent=1)
C = [dict(c, edl=c['id'] + '.edl.json') for c in json.load(open('../reels_config.json')) if c['id'] in PL]
json.dump(C, open('cfg.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['python3', '/home/claude/news_generator/pipeline/reels.py', 'cfg.json', '../../words.json'], check=True, capture_output=True)
OLD = {s['id']: s for s in json.load(open('../specs_motion.json'))}
if 'v3' not in OLD.get('_', ''):
    for s in json.load(open('../v3/specs_motion.json')): pass
OUT = []
for sid, p in PL.items():
    E = json.load(open(sid + '.edl.json'))['edl']; s = json.load(open(sid + '.spec.json')); h = p['hook'] + (1 if E[0].get('mute') else 0)
    ws = []
    for n_, e in enumerate(E):
        if e.get('mute'): continue
        sp_ = p['idx'][:1] if n_ < h else p['idx'][1:]
        ks = max(([k for k in range(i, j + 1) if e['src_in'] - 0.1 <= W[k]['start'] < e['src_out'] - 0.05] for i, j in sp_), key=len)
        for k in ks: ws.append({'t': FIX.get(W[k]['word'], W[k]['word']), 's': round(e['rec'] + max(0, W[k]['start'] - e['src_in']), 2), 'e': round(e['rec'] + min(W[k]['end'], e['src_out']) - e['src_in'], 2)})
    rep = dict(map(tuple, next(c for c in C if c['id'] == sid)['replace']))
    for w in ws: w['t'] = rep.get(w['t'], w['t'])
    ws[0]['t'] = ws[0]['t'][:1].upper() + ws[0]['t'][1:]
    ch, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.4 or re.search(r'[.?!,]$', cur[-1]['t']) or sum(len(x['t']) for x in cur) + len(w['t']) > 16): ch.append(cur); cur = []
        cur.append(w)
    if cur: ch.append(cur)
    dur, endDur = s['dur'], s['endDur']; s['chunks'] = []
    for n, c in enumerate(ch):
        en = min(ch[n + 1][0]['s'] if n + 1 < len(ch) else dur, c[-1]['e'] + 0.5)
        if c[0]['s'] < dur - endDur: s['chunks'].append({'s': c[0]['s'], 'e': round(min(en, dur - endDur), 2), 'words': [{'t': x['t'], 's': x['s']} for x in c]})
    def wt(word, after=0):  # время слова в ролике
        for c in s['chunks']:
            for w in c['words']:
                if w['s'] >= after and re.sub(r'[^\wё]', '', w['t'].lower()) == word: return w['s']
        raise ValueError(word)
    O = json.load(open(sid + '.old.edl.json'))['edl']; OT = O[-1]['rec'] + L(O[-1]); NT = E[-1]['rec'] + L(E[-1])
    def f(t):
        if t >= OT - 0.05: return round(NT, 2)
        e = next((e for e in O if e['rec'] <= t < e['rec'] + L(e)), None)
        src = e['src_in'] + t - e['rec'] if e else min(O, key=lambda e: abs(e['rec'] - t))['src_in']
        best = None
        for n in E[h:]:
            if n['src_in'] - 0.02 <= src <= n['src_out'] + 0.02: return round(n['rec'] + max(0, src - n['src_in']), 2)
            d0, d1 = abs(src - n['src_in']), abs(src - n['src_out']); c = (min(d0, d1), n['rec'] + (0 if d0 < d1 else L(n)))
            if best is None or c[0] < best[0]: best = c
        return round(best[1], 2)
    def remap(x):
        if isinstance(x, dict): return {k: (f(v) if k in ('at', 'out', 'onAt') and isinstance(v, (int, float)) else remap(v)) for k, v in x.items()}
        if isinstance(x, list): return [remap(v) for v in x]
        return x
    old = OLD[sid]; first = old['scenes'][0]; hend = round(E[h - 1]['rec'] + L(E[h - 1]), 2)
    c0 = CARD.get(sid, {}).get('dur', 0.0); sfx = []
    # хук-кинетика по словам речи (каждая строка — с «попом»)
    K = {
     's01_prototip_eto_tz': [("Понятная форма ТЗ —", 'понятная', 2, []), ("прототип", 'прототип', 0, ['прототип'])],
     's05_60_agentov': [("А 60 агентов", 'агентов', 0, ['60']), ("запустить можем", 'запустить', 2, ['можем'])],
     's06_monolit_v_agenta': [("Весь монолит в агента —", 'весь', 3, []), ("захлебнётся", 'захлебнется', 0, ['захлебнётся']), ("много глюков", 'много', 2, ['глюков'])],
     's09_zoom_s_zakazchikom': [("Правок с каждой итерацией —", 'количество', 3, []), ("меньше", 'уменьшалось', 0, ['меньше'])],
    }[sid]
    lines = []
    for t, w, size, hl in K:
        at = wt(w); d = {"t": t, "at": at}
        if size: d['size'] = size
        if hl: d['hl'] = hl
        lines.append(d); sfx.append({'file': 'sfx_pop.wav', 'at': at, 'vol': 0.35})
    sc = [dict(first, at=c0, out=hend, lines=lines)] + [remap(x) for x in old['scenes'][1:]]
    sc = [x for i, x in enumerate(sc) if i == 0 or x['out'] - x['at'] > 0.3]
    if sid == 's06_monolit_v_agenta': sc = sc[:-1]; sc[-1]['out'] = round(NT, 2)
    sc[1]['at'] = sc[0]['out']
    for a, b in zip(sc, sc[1:]):
        if b['at'] < a['out'] or 0 < b['at'] - a['out'] < 0.6: b['at'] = a['out']
    if sid in CARD:
        cd = CARD[sid]; n = sum(len(l) for l in cd['lines']); step = (cd['dur'] - 0.55) / n; k = 0; HL = []
        for l in cd['lines']:
            ww = []
            for w in l: ww.append({'t': w, 'at': round(0.08 + k * step, 2), 'hl': w in cd['hl']}); sfx.append({'file': 'sfx_pop.wav', 'at': round(0.08 + k * step, 2), 'vol': 0.4}); k += 1
            HL.append({'words': ww})
        s['hookcard'] = {'lines': HL, 'out': cd['dur']}
        sfx.append({'file': 'sfx_whoosh.wav', 'at': round(cd['dur'] - 0.3, 2), 'vol': 0.5})
    else:
        sfx.insert(0, {'file': 'sfx_whoosh.wav', 'at': 0.0, 'vol': 0.35})
    for k in ('tag', 'lector', 'org', 'title'): s[k] = old[k]
    s['scenes'] = sc; s['sfx'] = sfx; s['pv'] = [0.6, 1.4, round(c0 + 1.0, 2), round(hend + 2, 2), round(dur - 0.8, 2)]
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1); OUT.append(s)
    print(sid, dur, 'hook до', hend, [(x['kind'], x['at'], x['out']) for x in sc][:3])
    print('   ', ' '.join(w['t'] for c in s['chunks'][:10] for w in c['words']))
json.dump(OUT, open('specs_motion.json', 'w'), ensure_ascii=False)
