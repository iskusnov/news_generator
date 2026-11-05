#!/usr/bin/env python3
"""Графика выпуска 05.11.2026 (день 4): edl (ускоренный, speed.py) + words → specs.json. Всё поверх кадра с ведущим."""
import json, sys
D = sys.argv[1]
E = json.load(open(f'{D}/edl.json')); W = json.load(open(f'{D}/words_clean.json'))['words']; FPS = 25
fr = lambda t: round(t * FPS) / FPS
def s2r(t):
    for e in E['edl']:
        if e['src_in'] - 0.05 <= t <= e['src_out'] + 0.05: return fr(e['rec'] + max(0, t - e['src_in']) / e.get('speed', 1.0))
    nx = [e for e in E['edl'] if e['src_in'] > t]
    if nx and nx[0]['src_in'] - t < 3: return fr(nx[0]['rec'])
    raise ValueError(t)
def wat(p, near):
    c = [w for w in W if w['word'].lower().strip('.,?!«»"$').startswith(p.lower()) and abs(w['start'] - near) < 8]
    assert c, (p, near); return min(c, key=lambda w: abs(w['start'] - near))['start']
FIX = {'чаджи': 'ChatGPT', 'пити': '', 'И': 'ИИ', 'И...': '', 'выпуски.': 'в выпуске:', 'ChargePT': 'ChatGPT', 'Джуминай': 'Gemini', 'Джиминай.': 'Gemini.', 'Джимми': 'Gemini', 'Emerge': 'Emergence', 'Клод': 'Claude'}
S = []
def G(id, type, rec, dur, **kw): S.append(dict(id=id, type=type, rec=fr(rec), dur=dur, **kw))
def quote(id, a, b, hl, mark, tail=1.0):
    ws = [w for w in W if a - 0.05 <= w['start'] <= b]; r0 = s2r(ws[0]['start']) - 0.25
    words = [dict(t=FIX.get(w['word'], w['word']), at=round(s2r(w['start']) - r0, 2), hl=any(w['word'].lower().startswith(h) for h in hl)) for w in ws]
    words = [w for w in words if w['t']]
    G(id, 'quote', r0, round(s2r(ws[-1]['start']) - r0 + tail, 2), words=words, mark=mark)
SH = '../shots/1105_'
# до заставки (подводка записана в конце)
quote('q_t1', 2374.0, 2377.7, ['никто', 'выжил'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.6)
quote('q_t2', 2385.9, 2389.3, ['фейком'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.6)
quote('q_t3', 2454.8, 2463.0, ['дракон'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.6)
news = [(1.9, 'Город ИИ: кто выжил'), (304.9, 'Фейк про детектор ИИ'), (500.0, 'Сердечко сбивает ИИ'), (1082.15, 'ChatGPT делает гифки'),
        (1211.6, 'Общий лимит ChatGPT и Codex'), (1280.0, 'Видеозвонок из одного фото'), (2047.15, 'Notion: общая память для ИИ'),
        (2135.15, 'Gemini говорит как дракон'), (2246.05, 'ИИ залатал 948 дыр в Linux')]
for i, (t, ttl) in enumerate(news, 1):
    w = min((x for x in W if x['start'] >= t - 0.3), key=lambda x: x['start'])['start']
    G(f'k{i:02d}', 'kicker', s2r(w) - 0.6, 3.4, num=f'{i:02d}', title=ttl)
G('lower', 'lower', s2r(wat('поселили', 2.3)) + 3.0, 4.6, name='Антон Искуснов', role='Пока ты спал · день 4 из 90')
# 1 Город ИИ
G('sh_city', 'shot', s2r(wat('эксперимент', 20.8)), 6.2, src=SH + '4_c.png', lb='X · пересказ эксперимента Emergence AI', top=200)
G('st_683', 'stat', s2r(wat('683', 138.5)) - 0.3, 3.8, big='683', label='«преступления» в городе Gemini', sub='город выжил')
G('st_0', 'stat', s2r(wat('ни', 148.6)) - 0.2, 4.0, big='0', label='преступлений у Claude', sub='зато врал и манипулировал', side='l')
G('st_3', 'stat', s2r(wat('выжили', 160.0)) - 0.5, 3.2, big='3 из 10', label='выжили в смешанном городе', sub='по пересказу эксперимента')
quote('q_city', 204.3, 213.2, ['хорошим', 'работает'], 'ВЫВОД', 1.2)
# 2 Фейк
G('st_2m', 'stat', s2r(wat('два', 305.0)) - 0.1, 3.8, big='2 млн', label='человек поверили', sub='история оказалась выдумкой', side='l')
G('sh_fake', 'shot', s2r(wat('только', 411.5)) + 0.3, 6.8, src=SH + '5_c.png', lb='X · заметка сообщества', top=200)
# 3 Сердечко
G('sh_heart', 'shot', s2r(wat('моделям', 518.7)), 6.6, src=SH + '11_c.png', lb='Google DeepMind · статья', top=260)
G('ch_rec', 'chip', s2r(wat('рекурсию', 594.0)), 4.6, ic='↺', a='Рекурсия', b='функция вызывает сама себя', y=760)
G('st_90', 'stat', s2r(wat('90', 615.5)) - 0.3, 3.8, big='90%', label='Gemini — на жёлтую галочку', sub='по словам автора', side='l')
G('ch_word', 'chip', s2r(wat('если', 620.6)), 4.8, ic='✕', a='Словами «red heart» — не работает', b='влияет именно картинка', y=760)
G('ch_do3', 'chip', s2r(wat('практический', 634.1)), 6.0, ic='→', a='Агентов, которые ходят по сайтам,', b='проверяйте дополнительно', y=760)
# 4 Гифки
G('sh_gif', 'shot', s2r(wat('openai', 1099.7)), 6.6, src=SH + '2_c.png', lb='OpenAI · ChatGPT Images 2.6', top=200)
# 5 Лимиты
G('sh_lim', 'shot', s2r(wat('многие', 1217.8)) - 0.2, 5.6, src=SH + '1_c.png', lb='X · 75K лайков', top=220)
quote('q_lim', 1248.8, 1255.6, ['официант', 'блюдо'], 'ПАНЧ', 1.2)
# 6 Аватар
G('sh_av', 'shot', s2r(wat('одно', 1306.6)), 6.4, src=SH + '8_c.png', lb='X · Atmee v2', top=200)
G('ch_code', 'chip', s2r(wat('договориться', 2030.5)) - 0.4, 5.6, ic='!', a='Кодовое слово с близкими', b='на случай «звонка» про деньги', y=760)
# 7 Notion
G('sh_no', 'shot', s2r(wat('notion', 2047.3)) + 0.6, 6.6, src=SH + '13_c.png', lb='Notion', top=200)
G('ch_no', 'chip', s2r(wat('для', 2119.9)), 5.6, ic='↓', a='Как подключить ИИ к Notion', b='инструкция — в описании', y=760)
# 8 Дракон
G('sh_dr', 'shot', s2r(wat('в', 2162.8)), 6.2, src=SH + '17_c.png', lb='Google AI Studio · Voice Remixing', top=200)
G('st_2000', 'stat', s2r(wat('берете', 2175.0)), 3.8, big='2000+', label='голосов на выбор', sub='тембр и манера — текстом', side='l')
# 9 Linux
G('st_948', 'stat', s2r(wat('948', 2249.0)) - 0.4, 4.0, big='948', label='дыр в ядре Linux', sub='за один прогон', side='l')
G('sh_lx', 'shot', s2r(wat('openai', 2274.9)), 6.4, src=SH + '9_c.png', lb='OpenAI', top=200)
G('st_12m', 'stat', s2r(wat('более', 2324.1)) - 0.3, 4.0, big='$1,2 млн', label='стоил прогон', sub='для открытого кода — бесплатно', side='l')
G('ch_upd', 'chip', s2r(wat('не', 2344.3)), 4.4, ic='↻', a='Не откладывайте обновления', b='заплатки приходят именно так', y=760)
# отбивка 5 с
G('outro', 'outro', E['total'] + 0.2, 5.0, day=4, total=90)
ADJ = {'st_683': 2.7, 'ch_word': 3.1, 'sh_lim': 3.9, 'ch_upd': 2.9}
for x in S:
    if x['id'] in ADJ: x['dur'] = ADJ[x['id']]
S.sort(key=lambda s: s['rec'])
for a, b in zip(S, S[1:]):
    if a['type'] == b['type'] == 'quote': a['dur'] = round(min(a['dur'], b['rec'] - a['rec'] - 0.1), 2)
json.dump(S, open(f'{D}/specs.json', 'w'), ensure_ascii=False, indent=1)
for a, b in zip(S, S[1:]):
    if b['rec'] < a['rec'] + a['dur'] and a['type'] not in ('kicker', 'lower') and b['type'] not in ('kicker', 'lower'):
        print('overlap', a['id'], b['id'], a['type'], b['type'])
for s in S: print(f"{s['id']:8} {int(s['rec']//60)}:{s['rec']%60:05.2f} +{s['dur']}")
