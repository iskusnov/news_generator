#!/usr/bin/env python3
"""Шортсы 03.11: takes по каждому → cut.py (CUT_GAP=0.22) → edl; спеки вертикальной графики (shorts.html) → shorts.json"""
import json, re, os, subprocess, sys
D = sys.argv[1]; P = '/home/claude/news_generator/pipeline'
W = json.load(open(f'{D}/words3.json'))['words']
SH = [dict(id='s1_google', title='Без ИИ? Тогда <b>без поиска</b>', segs=[(161.3, 163.15), (175.4, 181.4), (184.6, 190.4), (195.9, 200.3), (236.0, 252.3), (286.5, 295.9), (303.0, 311.1)]),
      dict(id='s2_uchitel', title='ИИ-учитель <b>психанул</b>', segs=[(444.1, 448.2), (455.2, 466.0), (474.2, 480.9), (484.4, 488.0), (491.6, 504.2), (525.8, 534.2)]),
      dict(id='s3_34k', title='Claude нашёл <b>$34 000</b> в месяц', segs=[(608.7, 612.1), (631.4, 636.9), (642.9, 650.2), (667.3, 670.7), (675.9, 678.0), (683.3, 686.5), (708.8, 714.0), (790.0, 803.0)]),
      dict(id='s4_canva', title='Уволили, но дали <b>$10 000</b> и MacBook', segs=[(856.3, 860.1), (878.5, 899.4), (928.1, 936.7), (942.1, 945.2), (959.4, 964.4), (967.1, 970.0)])]
FIX = {'Клод':'Claude','Клод-код':'Claude Code','квот,':'Claude,','Канва':'Canva','канва':'Canva','ИИ-аватар-учитель':'ИИ-аватар учителя','мультиматум.':'ультиматум.','квот': 'Claude', 'Ина': 'ИИ', 'Чаджи-петти': 'ChatGPT', 'Карпаты': 'Карпати', 'Карпатый': 'Карпати',
       'hackersube.org': 'hackertube.org', 'кодом.': 'Claude Code.', 'коду,': 'Claude Code,', 'клейбейтных': 'кликбейтных', 'youtube': 'YouTube'}
out = json.load(open(f'{D}/shorts/shorts.json')) if os.environ.get('ONLY') else []
ONLY = os.environ.get('ONLY', '').split(',') if os.environ.get('ONLY') else None
out = [o for o in out if not ONLY or o['id'] not in ONLY]
for s in [x for x in SH if not ONLY or x['id'] in ONLY]:
    tp = f'{D}/shorts/{s["id"]}.takes.json'; ep = f'{D}/shorts/{s["id"]}.edl.json'
    json.dump(dict(fps=25, opener_after=None, segments=[dict(zip(('in', 'out'), x), tag='main') for x in s['segs']]), open(tp, 'w'))
    subprocess.run(['python3', f'{P}/cut.py', tp, f'{D}/words3.json', f'{D}/silence.json', '-', ep], env=dict(os.environ, CUT_GAP='0.22', CUT_PAD='0.07'), check=True, capture_output=True)
    E = json.load(open(ep))
    words = []
    for e in E['edl']:
        for w in W:
            if e['src_in'] - 0.02 <= w['start'] < e['src_out']:
                t = FIX.get(w['word'], w['word'])
                words.append(dict(t=t, s=round(e['rec'] + max(0, w['start'] - e['src_in']), 2), e=round(e['rec'] + min(w['end'], e['src_out']) - e['src_in'], 2)))
    words[0]['t'] = words[0]['t'][:1].upper() + words[0]['t'][1:]
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.5 or re.search(r'[.?!,]$', cur[-1]['t']) or sum(len(x['t']) for x in cur) + len(w['t']) > 18):
            chunks.append(cur); cur = []
        cur.append(w)
    chunks.append(cur)
    dur = E['total']; tail = 2.0
    ch = []
    for i, c in enumerate(chunks):
        e2 = chunks[i + 1][0]['s'] if i + 1 < len(chunks) else dur
        ch.append(dict(s=c[0]['s'], e=round(min(e2, c[-1]['e'] + 0.6), 2), words=[dict(t=x['t'], s=x['s']) for x in c]))
    out.append(dict(id=s['id'], title=s['title'], dur=round(dur + tail, 2), tail=tail, chunks=ch, cta='Подпишись · завтра в 06:00', ctaDur=2.6))
    print(s['id'], f'{dur:.1f}s', len(E['edl']), 'кусков', ' '.join(w['t'] for w in words)[:160])
json.dump(out, open(f'{D}/shorts/shorts.json', 'w'), ensure_ascii=False, indent=1)
