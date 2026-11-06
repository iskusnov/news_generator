#!/usr/bin/env python3
"""Шортсы 05.11: takes по каждому → cut.py (CUT_GAP=0.22) → edl; спеки вертикальной графики (shorts.html) → shorts.json"""
import json, re, os, subprocess, sys
D = sys.argv[1]; P = '/home/claude/news_generator/pipeline'
W = json.load(open(f'{D}/words.json'))['words']
CTA = 'Полное видео — завтра на канале\nПодписывайся'
END = dict(title='Спецвыпуск<br>«ИИ за неделю»<br><b>уже на канале</b>', sub='Материалы, чтобы повторить —\nв TG @scaling_ai', dur=3.2)
F = lambda n, l, k='': f'<div class="n s">{n}</div><div class="l">{l}</div>' + (f'<div class="k">{k}</div>' if k else '')
CH = lambda *xs: '<div class="chips">' + ''.join(f'<div class="chip {c}">{t}</div>' for t, c in xs) + '</div>'
CARDS = {
 's2_uber': [('4', 1, 2.2, 'full', '<div class="n">4</div><div class="l">поездки на такси<br><b>через ИИ-агентов</b></div><div class="k">UBER · САМАЯ ЗАГРУЖЕННАЯ НЕДЕЛЯ ОКТЯБРЯ</div>'),
             ('500', 1, 1.6, 'full', F('~500', 'заказов еды')),
             ('320', 1, 3.0, 'full', '<div class="n s" style="font-size:86px;white-space:nowrap">4 из 320 000 000</div><div class="l">заказов — <b>через агентов</b></div><div class="k">ВСЕ ЗАКАЗЫ UBER ЗА НЕДЕЛЮ</div>' or F('','заказов — <b>через агентов</b>', 'ВСЕ ЗАКАЗЫ UBER ЗА НЕДЕЛЮ')),
             ('50', 1, 4.2, 'low', CH(('🚕 такси · 50 сек', 'g'), ('🍔 еда · 90 сек', 'g'))),
             ('капчу,', 1, 3.0, 'low', CH(('капча ✗', 'r'), ('ручной ввод карты ✗', 'r'))),
             ('лицо,', 1, 3.0, 'low', CH(('лицо', ''), ('паспорт', ''), ('кошелёк', '')))],
 's1_slop': [('289', 1, 1.9, 'full', F('289', 'ИИ-роликов<br><b>в предвыборной рекламе</b>')),
             ('187', 1, 2.1, 'full', F('$187 млн', 'потрачено на ИИ-рекламу')),
             ('2024', 1, 4.6, 'full', '<div class="bars"><div class="bar a"><u>$50 тыс</u><i style="height:6px"></i><s>2024</s></div><div class="bar"><u>$187 млн</u><i style="height:460px"></i><s>2026</s></div></div><div class="l">рост <b>в тысячи раз</b></div>'),
             ('5', 1, 1.7, 'full', F('5 млн', 'просмотров')),
             ('53', 1, 1.9, 'full', F('53 : 47', 'кандидатка-«крендель»<br><b>победила</b>')),
             ('отличить', 1, 3.3, 'full', '<div class="tag">ЭТОТ ПЛАКАТ — ИИ ЗА 30 СЕКУНД</div><div class="ph" style="width:640px"><img src="file:///home/claude/ep1106/media/poster_s.jpg"><div class="src">Gemini · из одного моего фото</div></div>'),
             ('15', 1, 2.9, 'low', CH(('⏱ 15 минут', 'g'), ('💵 $1', 'g'))),
             ('Сатанисты', 1, 5.0, 'low', CH(('ИИ-реклама · Орегон, 2026', 'r'))),
             ('Фанатский', 1, 4.8, 'low', CH(('ИИ-ролик · Лос-Анджелес', 'r'))),
             ('Северной', 1, 6.4, 'low', CH(('ИИ-реклама · «Bonkers Bichler»', 'r')))],
}
# b-roll: (слово начала, n, слово конца, n, ролик, с какой секунды ролика, fit)
BR = {'s1_slop': [('Сатанисты', 1, 'Представьте', 1, 'slop_fb_satanists', 0.0, False),
                  ('Ваши', 1, 'И', 2, 'slop_fb_satanists', 4.5, False),
                  ('Фанатский', 1, 'И', 3, 'slop_x_batman', 28.0, True),
                  ('И', 3, '5', 1, 'slop_x_batman', 45.5, True),
                  ('Северной', 1, 'Кстати,', 1, 'slop_yt_lee', 3.0, True)],
}
SH = [dict(id='s1_slop', title='Сатанисты <b>в предвыборной</b> рекламе',
           logos=['sora-color.svg', 'gemini-color.svg', 'kling-color.svg', 'midjourney.svg|mono', 'runway.svg|mono'],
           segs=[(728.86, 734.45), (744.29, 746.2), (747.01, 751.9), (759.33, 765.55), (780.41, 782.3), (824.86, 831.1),
                 (845.07, 861.1), (873.01, 875.95), (936.99, 942.72), (955.57, 960.65), (982.12, 989.7), (990.47, 994.75), (693.17, 699.35)], cta=CTA),
      dict(id='s2_uber', title='Агенты <b>никому не нужны?</b>',
           logos=['txt:Uber', 'openai.svg|mono', 'claude-color.svg', 'gemini-color.svg'],
           segs=[(2.70, 4.05), (20.04, 41.4), (56.13, 60.6), (67.41, 92.74), (548.17, 557.5), (559.15, 571.95)], cta=CTA)]
FIX = {'Убер': 'Uber', 'нужны': 'нужны?', 'ИСЛОПа.': 'ИИ-слопа.', 'тором,': 'торт,', 'копчу,': 'капчу,', 'кандидатов': 'кандидата', 'кампания.': 'кампания.'}
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
    dur = E['total']; tail = END['dur']
    ch = []
    for i, c in enumerate(chunks):
        e2 = chunks[i + 1][0]['s'] if i + 1 < len(chunks) else dur
        ch.append(dict(s=c[0]['s'], e=round(min(e2, c[-1]['e'] + 0.6), 2), words=[dict(t=x['t'], s=x['s']) for x in c]))
    cards = []
    for wd, nth, cd, pos, html in CARDS.get(s['id'], []):
        hits = [w for w in words if w['t'] == wd]
        if len(hits) >= nth: cards.append(dict(at=max(0.05, round(hits[nth - 1]['s'] - 0.05, 2)), dur=cd, pos=pos, html=html, stag=1.0 if wd == '50' else 0.35))
        else: print('!! нет слова', wd, s['id'])
    broll = []
    for w1, n1, w2, n2, clip, ss, fit in BR.get(s['id'], []):
        h1 = [w for w in words if w['t'] == w1]; h2 = [w for w in words if w['t'] == w2]
        a = round(h1[n1 - 1]['s'] - (0.05 if h1[n1 - 1]['s'] > 0.1 else 0), 2); b = round(h2[n2 - 1]['s'] - 0.05, 2)
        broll.append(dict(clip=clip, rec_in=a, rec_out=b, ss=ss, fit=fit)); print('  broll', clip, a, b)
    out.append(dict(id=s['id'], title=s['title'], logos=s.get('logos'), cards=cards, broll=broll, end=END, sfx=[dict(at=round(dur + 0.05, 2), file='sfx.wav', vol=0.6)], dur=round(dur + tail, 2), tail=tail, chunks=ch, cta=s.get('cta', 'Подпишись · завтра в 06:00'), ctaDur=2.6))
    print(s['id'], f'{dur:.1f}s', len(E['edl']), 'кусков', ' '.join(w['t'] for w in words)[:160])
json.dump(out, open(f'{D}/shorts/shorts.json', 'w'), ensure_ascii=False, indent=1)
