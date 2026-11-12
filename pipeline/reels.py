#!/usr/bin/env python3
"""Спеки вертикальной графики для Reels/Shorts по монтажному листу.

reels.py <config.json> <words.json> → <id>.spec.json для каждого ролика из config.
config: [{"id","edl":"<id>.edl.json","title":"... <b>акцент</b>","endline","endDur",
          "list":{"items":[..],"src_at":[..],"src_out":X}, "stamps":[{"text","small","src_at","dur"}],
          "vs":{"a","al","b","bl","src_a","src_b","src_out"}}]
Время элементов задаётся в секундах ИСХОДНИКА (src_*), скрипт переводит его во время ролика по edl.
tail — секунд стоп-кадра после речи под финальную карточку.
Ускорение (поле speed в edl от speed.py) учитывается: время = rec + (t − src_in) / speed.
Субтитры: 1–3 слова, подсветка текущего слова; ошибки распознавания правятся словарём FIX ниже.
"""
import sys, json, re
FIX = {'AI-вдохновение': 'AI-вдохновение', 'код?': 'кот?', 'главой.': 'головой.', 'банду': 'бонусу', 'отобранное': '«избранное»', 'сохраненных': 'сохранёнок', 'бессонницы,': 'бессонница,'}
cfg, words_p = sys.argv[1], sys.argv[2]
W = json.load(open(words_p))['words']
for R in json.load(open(cfg)):
    E = json.load(open(R['edl']))
    def s2r(t):
        for e in E['edl']:
            if e['src_in'] - 0.05 <= t <= e['src_out'] + 0.05: return round(e['rec'] + max(0, t - e['src_in']) / e.get('speed', 1.0), 2)
        prev = [e for e in E['edl'] if e['src_out'] <= t]   # время в вырезанном месте → конец предыдущего куска
        if prev: e = max(prev, key=lambda e: e['src_out']); return round(e['rec'] + (e['src_out'] - e['src_in']) / e.get('speed', 1.0), 2)
        raise ValueError(f"{R['id']}: время {t} раньше начала монтажа")
    ws = []
    for e in E['edl']:
        for w in W:
            if e['src_in'] <= w['start'] < e['src_out']:
                sp = e.get('speed', 1.0)  # ускорение speed.py: время в ролике = rec + (t − src_in) / speed
                ws.append({'t': FIX.get(w['word'], w['word']), 's': round(e['rec'] + (w['start'] - e['src_in']) / sp, 2),
                           'e': round(e['rec'] + (min(w['end'], e['src_out']) - e['src_in']) / sp, 2)})
    for a, b in R.get('replace', []):          # точечные правки текста субтитров
        for w in ws:
            if w['t'] == a: w['t'] = b
    ch, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.4 or re.search(r'[.?!,]$', cur[-1]['t'])
                    or sum(len(x['t']) for x in cur) + len(w['t']) > 16):
            ch.append(cur); cur = []
        cur.append(w)
    if cur: ch.append(cur)
    tail = R.get('tail', 0)  # секунд стоп-кадра в конце под финальную карточку (речь не перекрывается)
    dur = round(E['total'] + tail, 2); endDur = R.get('endDur', 1.6)
    chunks = []
    for i, c in enumerate(ch):
        e = min(ch[i + 1][0]['s'] if i + 1 < len(ch) else dur, c[-1]['e'] + 0.5)
        if c[0]['s'] < dur - endDur:
            chunks.append({'s': c[0]['s'], 'e': round(min(e, dur - endDur), 2), 'words': [{'t': x['t'], 's': x['s']} for x in c]})
    spec = {'id': R['id'], 'title': R['title'], 'dur': dur, 'endDur': endDur, 'endline': R.get('endline', 'Подписывайся'), 'tail': tail, 'chunks': chunks}
    if 'list' in R:
        L = R['list']; spec['list'] = {'items': L['items'], 'at': [s2r(t) for t in L['src_at']], 'out': s2r(L['src_out'])}
    if 'stamps' in R:
        spec['stamps'] = [{'text': s['text'], 'small': s.get('small', ''), 'at': s2r(s['src_at']), 'dur': s.get('dur', 1.8)} for s in R['stamps']]
    if 'vs' in R:
        v = R['vs']; spec['vs'] = {k: v[k] for k in ('a', 'al', 'b', 'bl')}; spec['vs'].update(at_a=s2r(v['src_a']), at_b=s2r(v['src_b']), out=s2r(v['src_out']))
    if 'extras' in R:   # box / tag / phone / fine (мелкий текст, на это время субтитры скрыты)
        spec['extras'] = [dict({k: v for k, v in x.items() if k not in ('src_at', 'src_out')}, at=s2r(x['src_at']), out=s2r(x['src_out']) if x['src_out'] < 9000 else round(dur - endDur, 2)) for x in R['extras']]
    for k in ('capTop', 'stampTop', 'endline2', 'endHead', 'pv', 'scenes', 'tag', 'lector', 'org'):  # scenes — моушн-сцены шортсов из уроков (время ролика)
        if k in R: spec[k] = R[k]
    spec['covers'] = E.get('covers', [])
    json.dump(spec, open(R['id'] + '.spec.json', 'w'), ensure_ascii=False, indent=1)
    print(R['id'], f"{dur:.1f} с", len(chunks), 'титров', len(spec['covers']), 'перекрыть B-roll')
