#!/usr/bin/env python3
"""Графика выпуска 03.11.2026: edl.json + words → specs.json (плашки поверх видео)."""
import json, sys
D = sys.argv[1] if len(sys.argv) > 1 else '.'
E = json.load(open(f'{D}/edl.json')); W = json.load(open(f'{D}/words2.json'))['words']; FPS = 25
fr = lambda t: round(t * FPS) / FPS
def s2r(t):
    for e in E['edl']:
        if e['src_in'] - 0.02 <= t <= e['src_out'] + 0.02: return fr(e['rec'] + max(0, t - e['src_in']))
    raise ValueError(t)
def wat(prefix, near):
    c = [w for w in W if w['word'].lower().strip('.,?!«»').startswith(prefix.lower()) and abs(w['start'] - near) < 6]
    assert c, (prefix, near); return min(c, key=lambda w: abs(w['start'] - near))['start']
S = []
def G(id, type, rec, dur, **kw): S.append(dict(id=id, type=type, rec=fr(rec), dur=dur, **kw))
def quote(id, a, b, hl, mark, tail=1.2):
    ws = [w for w in W if a - 0.05 <= w['start'] <= b]; r0 = s2r(ws[0]['start']) - 0.25
    words = [dict(t=w['word'], at=round(s2r(w['start']) - r0, 2), hl=any(w['word'].lower().startswith(h) for h in hl)) for w in ws]
    G(id, 'quote', r0, round(s2r(ws[-1]['start']) - r0 + tail, 2), words=words, mark=mark)
SH = '../shots/1103_'
# перебивки: номер и тема новости — в паузе перед новостью
news = [(42.04, 'Карпати починил YouTube'), (157.6, 'Claude уходит от грубиянов'), (252.38, 'Лимиты: ChatGPT, Grok, Anthropic'),
        (492.45, 'Claude Code и чужие игры'), (595.3, 'Вирусный пост: 590 × 69'), (701.04, 'MIT: модель правит веса'),
        (773.55, 'Goldman Sachs: ИИ не всем'), (870.44, 'Anthropic Residency'), (936.98, 'ИИ-агент и мозг мыши'),
        (1153.4, 'Эллисон и папа Лев'), (1228.78, 'Коротко из X'), (1396.84, 'Итог дня')]
for i, (t, ttl) in enumerate(news, 1):
    G(f'k{i:02d}', 'kicker', max(s2r(t) - 0.85, E['gap_at'] + E['gap'] if i == 1 else 0), 3.4, num=f'{i:02d}', title=ttl)
G('lower', 'lower', s2r(wat('ну', 49.7)), 5.0, name='Антон Искуснов', role='Пока ты спал · день 2 из 90')
G('sh_karp', 'shot', s2r(wat('фактически', 80.7)), 7.0, src=SH + '1-08_c.png', lb='X · @karpathy')
G('ch_try', 'chip', s2r(wat('попробовать', 143.4)), 4.6, ic='→', a='hackertube.org', b='или фраза Карпати в вашу нейросеть', y=760)
quote('q_mama', 230.5, 232.2, ['хамил', 'ушел'], 'ПАНЧ', tail=1.0)
G('ch_limit', 'chip', s2r(wat('декабря', 252.5)) + 0.4, 5.0, ic='$', a='ChatGPT + Codex: общий лимит', b='с декабря · быстрые чаты не считаются', y=760)
G('st_17', 'stat', s2r(wat('17', 369.2)) - 0.3, 5.2, big='$17B', label='выручка Anthropic за III квартал', sub='по данным Bloomberg / unusual_whales')
quote('q_gb', 420.7, 423.0, ['гигабайт'], 'КАК В 2000-Х', tail=1.0)
G('sk_mario', 'strike', s2r(wat('получается', 515.4)), 4.6, head='Claude Code', items=['Марио', 'чужая игра'], at=[1.1, 1.5])
G('sh_post', 'shot', s2r(wat('пост', 597.5)), 9.0, src=SH + '2-01_c.png', lb='X · 13,5 млн просмотров', h=700)
G('st_407', 'stat', s2r(wat('40', 669.57)) - 0.1, 4.0, big='40 710', label='= 590 × 69', sub='ответ ChatGPT')
G('sh_mit', 'shot', s2r(wat('В', 701.04)) + 0.8, 7.0, src=SH + '2-03_c.png', lb='MIT · Weight-Space Programming', h=760)
G('st_x6', 'stat', s2r(wat('раз', 723.0)) - 0.6, 4.4, big='×6', label='рост на математике', sub='без обучения и градиентов', side='l')
G('sh_gs', 'shot', s2r(wat('Goldman', 773.65)) + 0.4, 5.6, src=SH + '2-02_c.png', lb='X · Bloomberg', top=300)
G('st_12k', 'stat', s2r(wat('12', 777.58)) - 0.2 + 5.6, 4.4, big='12K', label='инженеров с Claude и GitHub', sub='Goldman Sachs · остальным нельзя')
G('sh_res', 'shot', s2r(wat('Антропик', 870.44)) + 0.5, 6.0, src=SH + '1-01_c.png', lb='X · @AnthropicAI', top=300)
G('st_22', 'stat', s2r(wat('22', 886.9)) - 0.3, 4.0, big='22.11', label='последний день заявок', sub='опыт в ML не обязателен')
G('ch_plan', 'chip', s2r(wat('может', 901.3)), 3.6, ic='90', a='План Б', b='если 90 дней не взлетят', y=760)
G('ch_ell', 'chip', s2r(wat('основатель', 1153.4)), 5.6, ic='LE', a='Ларри Эллисон, Oracle', b='Роботы заменят таксистов, но не человека', y=760)
G('ch_pope', 'chip', s2r(wat('папа', 1173.3)), 5.0, ic='PL', a='Папа Лев XIV', b='Не доверять ИИ решения о жизни человека', y=760)
G('sh_musk', 'shot', s2r(wat('маск', 1259.5)), 6.4, src=SH + '1-02_c.png', lb='X · @elonmusk', top=260)
G('sh_lifeval', 'shot', s2r(wat('open', 1286.48)), 5.0, src=SH + '1-03_c.png', lb='OpenAI · LifeVal', h=760)
G('sh_lecun', 'shot', s2r(wat('лекун', 1304.1)) if any(w['word'].lower().startswith('лекун') for w in W) else s2r(1304.2), 5.2, src=SH + '1-09_c.png', lb='X · @ylecun', h=760)
G('ch_rumor', 'chip', s2r(wat('инсайдеры', 1335.3)) - 0.3, 4.6, ic='?', a='СЛУХ · не подтверждено', b='Скоро новая модель ChatGPT', y=760)
q0 = s2r(wat('вопрос', 1410.08)) - 0.4
G('poll', 'poll', q0, round(s2r(wat('страсти', 1418.54)) + 0.9 - q0, 2), head='Вопрос дня', q='Нормально, что ИИ может обидеться на грубость?',
  opts=['Да, так и надо', 'Нет, это просто инструмент'], pick=-1, foot='Ответьте в комментариях')
e0 = s2r(wat('завтра', 1421.66)) - 0.3
G('end', 'end', e0, round(E['total'] - e0, 2), sub='Ежедневно · 06:00 по Мадриду', head='Подписывайтесь', head2='Завтра в <b>06:00</b>',
  swapAt=1.4, btn='Подписаться', day=2, total=90)
S.sort(key=lambda s: s['rec'])
json.dump(S, open(f'{D}/specs.json', 'w'), ensure_ascii=False, indent=1)
for s in S: print(f"{s['id']:10} {int(s['rec']//60)}:{s['rec']%60:05.2f} +{s['dur']}")
