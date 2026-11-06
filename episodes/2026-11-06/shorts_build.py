#!/usr/bin/env python3
"""Шортсы 05.11: takes по каждому → cut.py (CUT_GAP=0.22) → edl; спеки вертикальной графики (shorts.html) → shorts.json"""
import json, re, os, subprocess, sys
D = sys.argv[1]; P = '/home/claude/news_generator/pipeline'
W = json.load(open(f'{D}/words.json'))['words']
CTA = 'Полное видео — завтра на канале\nПодписывайся'
SH = [dict(id='s1_slop', title='Сатанисты <b>в предвыборной</b> рекламе',
           logos=['sora-color.svg', 'gemini-color.svg', 'kling-color.svg', 'midjourney.svg|mono', 'runway.svg|mono'],
           segs=[(728.86, 734.45), (744.29, 746.2), (747.01, 751.9), (759.33, 765.55), (780.41, 782.3), (824.86, 831.1),
                 (845.07, 861.1), (873.01, 875.95), (936.99, 942.72), (955.57, 960.65), (982.12, 989.7), (990.47, 994.75), (693.17, 699.35)], cta=CTA),
      dict(id='s2_uber', title='Агенты заказали <b>4 такси</b> из 320 млн',
           logos=['txt:Uber', 'openai.svg|mono', 'claude-color.svg', 'gemini-color.svg'],
           segs=[(20.04, 41.4), (56.13, 60.6), (67.41, 92.74), (548.17, 557.5), (559.15, 571.95)], cta=CTA)]
FIX = {'Убер': 'Uber', 'ИСЛОПа.': 'ИИ-слопа.', 'тором,': 'торт,', 'копчу,': 'капчу,', 'кандидатов': 'кандидата', 'кампания.': 'кампания.'}
out = json.load(open(f'{D}/shorts/shorts.json')) if os.environ.get('ONLY') else []
ONLY = os.environ.get('ONLY', '').split(',') if os.environ.get('ONLY') else None
out = [o for o in out if not ONLY or o['id'] not in ONLY]
for s in [x for x in SH if not ONLY or x['id'] in ONLY]:
    tp = f'{D}/shorts/{s["id"]}.takes.json'; ep = f'{D}/shorts/{s["id"]}.edl.json'
    json.dump(dict(fps=25, opener_after=None, segments=[dict(zip(('in', 'out'), x), tag='main') for x in s['segs']]), open(tp, 'w'))
    subprocess.run(['python3', f'{P}/cut.py', tp, f'{D}/words.json', f'{D}/silence.json', '-', ep], env=dict(os.environ, CUT_GAP='0.22', CUT_PAD='0.07'), check=True, capture_output=True)
    E = json.load(open(ep))
    words = []
    for e in E['edl']:
        for w in W:
            if e['src_in'] - 0.06 <= w['start'] < e['src_out']:
                t = FIX.get(w['word'], w['word'])
                words.append(dict(t=t, s=round(e['rec'] + max(0, w['start'] - e['src_in']), 2), e=round(e['rec'] + min(w['end'], e['src_out']) - e['src_in'], 2)))
    SEQ = {('губернатором', 'жующим'): ['губернатором,', 'жующим'], ('поезда', 'к', 'такси.'): ['поездки', 'на', 'такси.'], ('где-то', 'требуются'): ['где-то', 'требуется'], ('как', 'и', 'решая'): ['как', 'ИИ', 'решает'], ('Gemini', 'Най,'): ['Gemini,'], ('Сегодня', 'выпуске.'): ['Сегодня', 'в выпуске:'], ('И', 'поселили'): ['ИИ', 'поселили']}
    for k, v in SEQ.items():  # точечные правки распознавания (несколько слов подряд)
        for i in range(len(words) - len(k) + 1):
            if tuple(w['t'] for w in words[i:i + len(k)]) == k:
                for j, w in enumerate(words[i:i + len(k)]): w['t'] = v[j] if j < len(v) else ''
    words = [w for w in words if w['t'] not in ('', '...')]
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
    out.append(dict(id=s['id'], title=s['title'], logos=s.get('logos'), dur=round(dur + tail, 2), tail=tail, chunks=ch, cta=s.get('cta', 'Подпишись · завтра в 06:00'), ctaDur=2.6))
    print(s['id'], f'{dur:.1f}s', len(E['edl']), 'кусков', ' '.join(w['t'] for w in words)[:160])
json.dump(out, open(f'{D}/shorts/shorts.json', 'w'), ensure_ascii=False, indent=1)
