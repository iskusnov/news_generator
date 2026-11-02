#!/usr/bin/env python3
"""Шортсы: куски исходника + спеки вертикальной графики. Выход: shorts.json"""
import json, re
W = json.load(open('/home/claude/pod/words.json'))['words']
FPS = 25
fr = lambda t: round(t * FPS) / FPS
FIX = {'телеведущий': 'телеведущим', 'Альдмана,': 'Альтмана,', 'Амадея.': 'Амодеи.', 'twitter': 'Twitter', 'ютубе.': 'YouTube.',
       'промтов': 'промптов', 'AI.': 'AI.', 'ну': '', 'как': None}

def split_pauses(a, b, maxgap=0.6, pad_out=0.2, pad_in=0.1):
    ws = [w for w in W if w['start'] >= a - 0.05 and w['start'] < b]
    out, cur = [], a
    for x, y in zip(ws, ws[1:]):
        if y['start'] - x['end'] > maxgap and x['end'] + pad_out < y['start'] - pad_in:
            out.append((cur, x['end'] + pad_out)); cur = y['start'] - pad_in
    out.append((cur, b))
    return [(fr(p), fr(q)) for p, q in out if q - p > 0.2]

SHORTS = [
 dict(id='short1_televeduschiy', title='Переехал в другую страну и стал <b>телеведущим</b>',
      segs=[(224.40, 227.89), (228.43, 270.25)]),
 dict(id='short2_ranshe_sosedey', title='Переехал, чтобы вставать <b>раньше соседей</b>',
      segs=[(595.0, 605.45), (564.7, 575.0)]),
 dict(id='short3_studiya', title='Студия не делает тебя <b>ведущим</b>',
      segs=[(309.2, 315.5), (321.25, 357.1), (663.85, 673.6)]),
 dict(id='short4_bez_top5', title='Никаких «топ-5 <b>нейросетей</b>»',
      segs=[(431.0, 477.3)]),
 dict(id='short5_dictor', title='Как подавать новости: <b>диктор или по-дружески?</b>',
      segs=[(779.0, 798.2), (822.5, 832.45)]),
]
out = []
for s in SHORTS:
    pieces, rec, words = [], 0.0, []
    for a, b in s['segs']:
        for p, q in split_pauses(a, b):
            for w in W:
                if p <= w['start'] < q:
                    t = w['word']
                    if t in ('Нет,',) : continue
                    words.append(dict(t=t, s=round(rec + w['start'] - p, 2), e=round(rec + min(w['end'], q) - p, 2)))
            pieces.append(dict(src_in=p, src_out=q)); rec += q - p
    dur = fr(rec)
    # фиксы распознавания
    if s['id'].startswith('short1'):
        words = [w for w in words if not (w['t'] in ('ну', 'как', 'не') and w['s'] < 6)]
    for w in words:
        w['t'] = {'телеведущий': 'телеведущим', 'Альдмана,': 'Альтмана,', 'Амадея.': 'Амодеи.', 'twitter': 'Twitter',
                  'ютубе.': 'YouTube.', 'промтов': 'промптов', 'Не': 'не'}.get(w['t'], w['t'])
    if s['id'].startswith('short2'): words.insert(0, dict(t='При', s=0.05, e=0.3))
    for w in words:
        if w['t']=='приехал' and s['id'].startswith('short1'): w['t']='приехал в'
    if words: words[0]['t'] = words[0]['t'][:1].upper() + words[0]['t'][1:]
    # чанки по 1–3 слова
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.5 or re.search(r'[.?!,]$', cur[-1]['t']) or sum(len(x['t']) for x in cur) + len(w['t']) > 18):
            chunks.append(cur); cur = []
        cur.append(w)
    chunks.append(cur)
    ch = []
    for i, c in enumerate(chunks):
        e = chunks[i + 1][0]['s'] if i + 1 < len(chunks) else dur
        e = min(e, c[-1]['e'] + 0.6)
        ch.append(dict(s=c[0]['s'], e=round(e, 2), words=[dict(t=x['t'], s=x['s']) for x in c]))
    spec = dict(id=s['id'], title=s['title'], dur=dur, chunks=ch, cta='Подпишись · завтра в 06:00', ctaDur=2.6, pieces=pieces)
    if s['id'].startswith('short5'):
        def at(prefix, after=0):
            return next(w['s'] for w in words if w['t'].lower().startswith(prefix) and w['s'] >= after)
        a1 = at('стил'); a2 = at('дружес')
        spec['poll'] = dict(opts=['Как диктор новостей', 'По-дружески и понятно'], at=[a1 - 0.3, a2 - 0.6], pick=1, pickAt=at('ближе'))
    out.append(spec)
    print(s['id'], f'{dur:.1f}s', len(pieces), 'кусков', len(ch), 'титров')
json.dump(out, open('shorts.json', 'w'), ensure_ascii=False, indent=1)
