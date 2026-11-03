#!/usr/bin/env python3
"""Шортсы 03.11: takes по каждому → cut.py (CUT_GAP=0.22) → edl; спеки вертикальной графики (shorts.html) → shorts.json"""
import json, re, os, subprocess, sys
D = sys.argv[1]; P = '/home/claude/news_generator/pipeline'
W = json.load(open(f'{D}/words2.json'))['words']
SH = [dict(id='short1_claude_ushel', title='Claude теперь может <b>уйти от вас</b>', segs=[(156.75, 219.5), (230.4, 232.6)]),
      dict(id='short2_590x69', title='Призналась ChatGPT в измене. <b>Он посчитал</b>', segs=[(594.45, 626.4), (634.7, 638.4), (663.9, 672.6)]),
      dict(id='short3_karpathy', title='Карпати за вечер <b>починил YouTube</b>', segs=[(41.19, 62.2), (80.6, 91.3), (106.0, 112.6), (143.1, 153.5)]),
      dict(id='short4_mysh', title='ИИ уже делает <b>операции на мозге</b>', segs=[(936.13, 943.1), (963.1, 968.3), (981.1, 1000.9), (1005.7, 1006.9)])]
FIX = {'квот': 'Claude', 'Ина': 'ИИ', 'Чаджи-петти': 'ChatGPT', 'Карпаты': 'Карпати', 'Карпатый': 'Карпати',
       'hackersube.org': 'hackertube.org', 'кодом.': 'Claude Code.', 'коду,': 'Claude Code,', 'клейбейтных': 'кликбейтных', 'youtube': 'YouTube'}
out = json.load(open(f'{D}/shorts/shorts.json')) if os.environ.get('ONLY') else []
ONLY = os.environ.get('ONLY', '').split(',') if os.environ.get('ONLY') else None
out = [o for o in out if not ONLY or o['id'] not in ONLY]
for s in [x for x in SH if not ONLY or x['id'] in ONLY]:
    tp = f'{D}/shorts/{s["id"]}.takes.json'; ep = f'{D}/shorts/{s["id"]}.edl.json'
    json.dump(dict(fps=25, opener_after=None, segments=[dict(zip(('in', 'out'), x), tag='main') for x in s['segs']]), open(tp, 'w'))
    subprocess.run(['python3', f'{P}/cut.py', tp, f'{D}/words2.json', f'{D}/silence.json', '-', ep], env=dict(os.environ, CUT_GAP='0.22', CUT_PAD='0.07'), check=True, capture_output=True)
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
