#!/usr/bin/env python3
"""Графика выпуска 04.11.2026 (день 3): edl + words → specs.json. Всё — поверх кадра с ведущим (прозрачный фон)."""
import json, sys
D = sys.argv[1]; TAIL = 3.6
E = json.load(open(f'{D}/edl.json')); W = json.load(open(f'{D}/words3.json'))['words']; FPS = 25
fr = lambda t: round(t * FPS) / FPS
def s2r(t):
    for e in E['edl']:
        if e['src_in'] - 0.05 <= t <= e['src_out'] + 0.05: return fr(e['rec'] + max(0, t - e['src_in']))
    nx = [e for e in E['edl'] if e['src_in'] > t]
    if nx and nx[0]['src_in'] - t < 3: return fr(nx[0]['rec'])
    raise ValueError(t)
def wat(p, near):
    c = [w for w in W if w['word'].lower().strip('.,?!«»"$').startswith(p.lower()) and abs(w['start'] - near) < 8]
    assert c, (p, near); return min(c, key=lambda w: abs(w['start'] - near))['start']
S = []
def G(id, type, rec, dur, **kw): S.append(dict(id=id, type=type, rec=fr(rec), dur=dur, **kw))
def quote(id, a, b, hl, mark, tail=1.2):
    ws = [w for w in W if a - 0.05 <= w['start'] <= b]; r0 = s2r(ws[0]['start']) - 0.25
    words = [dict(t=w['word'], at=round(s2r(w['start']) - r0, 2), hl=any(w['word'].lower().startswith(h) for h in hl)) for w in ws]
    G(id, 'quote', r0, round(s2r(ws[-1]['start']) - r0 + tail, 2), words=words, mark=mark)
SH = '../shots/1104_'
# до заставки — ключевые фразы крупно
quote('q_t1', 13.7, 18.2, ['поиска'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.9)
quote('q_t2', 22.9, 26.0, ['психан'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.6)
quote('q_t3', 33.2, 39.7, ['34', 'тысяч', 'долларов'], 'СЕГОДНЯ В ВЫПУСКЕ', 0.8)
G('lower', 'lower', s2r(wat('привет', 49.7)), 5.0, name='Антон Искуснов', role='Пока ты спал · день 3 из 90')
news = [(136.8, 'Google: без ИИ — без поиска'), (444.1, 'ИИ-учитель психанул'), (608.7, 'Claude нашёл $34 000'), (856.3, 'Canva уволила 22%'),
        (1043.2, 'ИИ починил ИИ за $10'), (1314.8, 'Слух: GPT-6.2 Astra'), (1414.85, 'Найм: ушёл без ИИ'), (1556.6, 'Вопрос дня')]
for i, (t, ttl) in enumerate(news, 1):
    w = min((x for x in W if x['start'] >= t - 0.3), key=lambda x: x['start'])['start']
    G(f'k{i:02d}', 'kicker', s2r(w) - 0.85, 3.4, num=f'{i:02d}', title=ttl)
# 1 Google
G('sh_g', 'shot', s2r(wat('по', 175.6)) + 0.3, 6.5, src=SH + '1_c.png', lb='X · The New York Times', top=220)
G('ch_one', 'chip', s2r(wat('детям', 287.6)), 4.6, ic='G', a='Решает одна компания', b='не родители и не школа', y=760)
G('st_50k', 'stat', s2r(wat('50', 250.1)) - 0.3, 4.4, big='50K', label='лайков у поста мэра Нью-Йорка', sub='«Google давит монополией»')
quote('q_net', 303.0, 311.0, ['интернета'], 'КАК РАНЬШЕ', 1.0)
# 2 Учитель
G('sh_t', 'shot', s2r(wat('сети', 455.3)), 6.5, src=SH + '2_c.png', lb='X · 588K просмотров', top=200)
G('st_23', 'stat', s2r(wat('23', 486.0)) - 0.3, 4.0, big='23M', label='просмотров оригинала', sub='«seventeen» по буквам')
quote('q_rude', 530.0, 532.0, ['хамит', 'сам'], 'ПАНЧ', 1.6)
# 3 Claude $34 000
G('st_34', 'stat', s2r(wat('34', 609.5)) - 0.2, 4.2, big='$34K', label='экономии в месяц', sub='нашёл Claude Code', side='l')
G('sh_lv', 'shot', s2r(wat('один', 631.4)), 7.0, src=SH + '4_c.png', lb='X · @levelsio', h=760, top=170)
G('st_300', 'stat', s2r(wat('300', 710.9)) - 0.3, 4.0, big='$300', label='в месяц — все его сайты', sub='было ≈ $34 000', side='l')
G('ch_do', 'chip', s2r(wat('попросите', 790.1)), 6.0, ic='→', a='Что делать: выписка + ИИ', b='«Где я переплачиваю?»', y=760)
dim0 = s2r(wat('ну', 842.0)) - 0.2
G('dim', 'dim', dim0, round(s2r(wat('применение', 844.02)) + 0.8 - dim0, 2), text='мысль вслух')
# 4 Canva
G('st_22', 'stat', s2r(wat('сразу', 884.4)), 4.6, big='22%', label='сотрудников Canva — ≈1200 человек', sub='впервые за 13 лет')
G('sh_cv', 'shot', s2r(wat('оставляет', 931.8)) - 0.4, 6.4, src=SH + '3_c.png', lb='X · @MarkDiStef', h=760, top=170)
G('st_10k', 'stat', s2r(wat('10', 942.3)) - 0.2, 4.0, big='$10K', label='на свой бизнес', sub='+ MacBook и 6 зарплат', side='l')
quote('q_cv', 959.8, 964.0, ['хотя', 'так'], 'ПАНЧ', 1.2)
# 5 ИИ починил ИИ
G('sh_hf', 'shot', s2r(wat('инженер', 1068.8)), 7.0, src=SH + '10_c.png', lb='X · Hugging Face', h=760, top=170)
G('st_001', 'stat', s2r(wat('клод', 1093.4)), 4.4, big='<0,01%', label='весов изменил Claude', sub='без обучения', side='l')
G('st_10', 'stat', s2r(wat('на', 1112.6)), 4.2, big='$10', label='и меньше 3 часов', sub='раньше — команда и месяц', side='l')
G('ch_hf', 'chip', s2r(wat('разработчикам', 1210.1)), 5.0, ic='→', a='Что делать: повторить опыт', b='ссылка в описании', y=760)
# 6 Слух
G('ch_rum', 'chip', s2r(wat('разработчики', 1317.8)), 5.2, ic='?', a='СЛУХ · не подтверждено', b='GPT-6.2 Astra в Codex', y=760)
G('sh_rum', 'shot', s2r(wat('она', 1334.0)), 5.6, src=SH + '20_c.png', lb='X · @embw_l0x', top=240)
G('st_60', 'stat', s2r(wat('60', 1338.1)) - 0.2, 3.6, big='−60%', label='цена — по слухам', side='l')
# 7 Найм
G('sh_hr', 'shot', s2r(wat('сооснователь', 1433.7)), 7.0, src=SH + '17_c.png', lb='X · Дэвид Крамер, Sentry', top=280)
quote('q_hr', 1530.2, 1536.3, ['свободен', 'кофе'], 'ПАНЧ', 1.2)
# Вопрос дня + отбивка
q0 = s2r(wat('google', 1557.6)) - 0.3
G('poll', 'poll', q0, round(s2r(wat('поиск', 1573.5)) + 1.2 - q0, 2), head='Вопрос дня', q='Google прав или это шантаж?',
  opts=['Прав: ИИ и поиск уже не разделить', 'Шантаж: у школы должен быть выбор'], pick=-1, foot='Ответьте в комментариях')
e0 = s2r(wat('завтра', 1581.5)) - 0.2
G('end', 'end', e0, round(E['total'] + TAIL - e0, 2), sub='Ежедневно · 06:00 по Мадриду', head='Подписывайтесь', head2='Завтра в <b>06:00</b>',
  swapAt=1.6, btn='Подписаться', day=3, total=90)
S.sort(key=lambda s: s['rec'])
for a, b in zip(S, S[1:]):  # одинаковые зоны не наслаиваются
    if a['type'] == b['type'] == 'quote' or (a['type'], b['type']) == ('poll', 'end'):
        a['dur'] = round(min(a['dur'], b['rec'] - a['rec'] - 0.1), 2)
json.dump(S, open(f'{D}/specs.json', 'w'), ensure_ascii=False, indent=1)
# пересечения справа/слева
for a, b in zip(S, S[1:]):
    if b['rec'] < a['rec'] + a['dur'] and a['type'] not in ('kicker', 'dim') and b['type'] not in ('kicker', 'dim'):
        print('overlap', a['id'], b['id'])
for s in S: print(f"{s['id']:8} {int(s['rec']//60)}:{s['rec']%60:05.2f} +{s['dur']}")
