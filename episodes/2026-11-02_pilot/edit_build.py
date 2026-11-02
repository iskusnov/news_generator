#!/usr/bin/env python3
"""Монтажный лист + спеки графики для выпуска. Выход: edl.json, specs.json"""
import json, re
W = json.load(open('/home/claude/pod/words.json'))['words']
FPS = 25
SIL = [tuple(map(float, l.split())) for l in open('/home/claude/pod/sil.txt') if len(l.split()) == 2]
def fr(t): return round(t * FPS) / FPS

def wat(prefix, near, field='start'):
    """время слова, начинающегося с prefix, ближайшего к near"""
    c = [w for w in W if w['word'].lower().strip('.,?!«»').startswith(prefix.lower())]
    w = min(c, key=lambda w: abs(w['start'] - near))
    assert abs(w['start'] - near) < 8, (prefix, near, w)
    return w[field]

# (src_in, src_out) — выбранные дубли по порядку
COLD = [(595.0, 605.45)]
MAIN = [
 (22.10, 28.70), (45.05, 50.60), (57.55, 96.60),
 (112.00, 133.15), (141.45, 201.70),
 (208.60, 217.05), (218.10, 219.05),
 (224.40, 227.89), (228.43, 270.25), (277.70, 309.05),
 (309.20, 315.50), (321.25, 357.10),
 (368.40, 389.50), (395.40, 420.10),
 (431.00, 477.30),
 (512.60, 551.20),
 (564.70, 605.45),
 (623.50, 653.20),
 (663.85, 673.60),
 (681.00, 735.30),
 (754.20, 760.50),
 (779.00, 798.20),
 (822.50, 832.45),
]
OPENER_GAP = 4.0

def split_pauses(a, b, maxgap=0.75, pad_out=0.22, pad_in=0.12):
    ws = [w for w in W if w['start'] >= a - 0.05 and w['end'] <= b + 0.6 and w['start'] < b]
    out, cur = [], a
    for x, y in zip(ws, ws[1:]):
        if y['start'] - x['end'] > maxgap and x['end'] + pad_out < y['start'] - pad_in:
            out.append((cur, x['end'] + pad_out)); cur = y['start'] - pad_in
    out.append((cur, b))
    # вторая проверка — по звуку: тишина > 0.9 с внутри куска вырезается
    res = []
    for p, q in out:
        cur = p
        for sa, sb in SIL:
            lo, hi = max(sa, cur), min(sb, q)
            if hi - lo > 0.9:
                res.append((cur, lo + 0.25)); cur = hi - 0.15
        res.append((cur, q))
    return [(fr(p), fr(q)) for p, q in res if q - p > 0.2]

edl, rec = [], 0.0
def add(segs, tag):
    global rec
    for a, b in segs:
        for p, q in split_pauses(a, b):
            edl.append({'src_in': p, 'src_out': q, 'rec': fr(rec), 'tag': tag})
            rec += q - p
add(COLD, 'cold')
gap_at = fr(rec); rec += OPENER_GAP
add(MAIN, 'main')
for i, e in enumerate(edl): e['scale'] = 1.0 if i % 2 == 0 else 1.12
total = fr(rec)

def s2r(t, after=0.0):
    for e in edl:
        if e['src_in'] - 0.01 <= t <= e['src_out'] and e['rec'] >= after:
            return fr(e['rec'] + t - e['src_in'])
    raise ValueError(t)

def words_between(a, b):
    return [w for w in W if a - 0.05 <= w['start'] <= b]

specs = []
def G(id, type, rec_at, dur, **kw):
    specs.append(dict(id=id, type=type, rec=fr(rec_at), dur=dur, **kw))

def quote(id, a, b, hl, mark, after=0.0, tail=1.2):
    ws = words_between(a, b); r0 = s2r(ws[0]['start'], after) - 0.25
    words = [dict(t=w['word'], at=round(s2r(w['start'], after) - r0, 2), hl=any(w['word'].lower().startswith(h) for h in hl)) for w in ws]
    words[0]['t'] = words[0]['t'][:1].upper() + words[0]['t'][1:]
    dur = round(s2r(ws[-1]['start'], after) - r0 + tail, 2)
    G(id, 'quote', r0, dur, words=words, mark=mark)

# холодное открытие — цитата-хук
quote('q_hook', 595.8, 600.2, ['замедл', 'раньше', 'соседей'], 'ПРОЛОГ', tail=1.4)
# заставка
G('opener', 'opener', gap_at, OPENER_GAP + 1.2, day=1, total=90, city='MADRID',
  title=[dict(t='ПОКА'), dict(t='ТЫ'), dict(t='СПАЛ'), dict(br=True), dict(t='НОВОСТИ', hl=True), dict(t='AI', hl=True)], tag='Каждое утро в 06:00 по Мадриду',
  pv=[0.6, 1.5, 3.4, 4.6])
after = gap_at + OPENER_GAP
G('lower', 'lower', s2r(22.3, after) + 0.3, 5.0, name='Антон Искуснов', role='Ведущий · эксперимент 90 дней')
chap = [(22.3, '01', 'Зачем я это делаю'), (112.1, '02', 'Идея канала'), (252.7, '03', 'Правила эксперимента'),
        (309.3, '04', 'Студия — не результат'), (431.1, '05', 'Что будет в выпусках'), (512.7, '06', 'Обратная связь'),
        (623.6, '07', 'Почему именно новости'), (681.1, '08', 'Что дальше')]
for t, n, ttl in chap:
    G(f'k{n}', 'kicker', s2r(t, after) + (6.0 if n == '01' else 0.2), 3.6, num=n, title=ttl)
G('s90', 'stat', s2r(wat('90-днев', 255)) - 0.2, 6.4, side='l', big='90', label='дней эксперимента', sub='Старт: сегодня')
G('s0600', 'stat', s2r(wat('кажд', 259.5)) - 0.1, 5.0, big='06:00', label='каждое утро по Мадриду', sub='Кроме воскресенья')
G('s1020', 'stat', s2r(wat('10-20', 297)) - 0.3, 4.4, big='10–20', label='минут — пока пьёте кофе', sub='Всё главное за день')
G('strike', 'strike', s2r(wat('без', 433.5)) - 0.2, 4.6, head='Чего здесь не будет', items=['топ-5 нейросетей', 'топ-5 промптов'], at=[1.0, 1.9])
G('toxic', 'chip', s2r(wat('toxic', 447)) - 0.3, 3.6, ic='IG', a='Toxic TV', b='Новый инстаграм', y=760)
G('s30', 'stat', s2r(wat('топ-30', 467.7)) - 0.2, 4.4, big='≈30', label='новостей за 15–25 минут', sub='Только проверенные факты')
G('day1', 'day', s2r(wat('сегодня', 474.7)), 3.4, n=1, total=90)
G('fb', 'chip', s2r(wat('писали', 520)) - 0.2, 4.0, ic='?', a='Пишите в комментариях', b='Что интересно · что не так', y=760)
G('s0601', 'stat', s2r(wat('кажд', 572.4, ), after) - 0.4, 4.4, side='r', big='06:01', label='— вот что имеет значение', sub='Не студия и не подъём')
quote('q_studio', 663.9, 673.0, ['отговорки', 'закончились'], 'ГЛАВНОЕ')
G('mogilko', 'chip', s2r(wat('марин', 717.6)) - 0.2, 3.6, ic='M', a='Марина Могилко', b='Интервью с лидерами индустрии', y=760)
G('altman', 'chip', s2r(wat('сэма', 758.2)) - 0.2, 3.2, ic='SA', a='Сэм Альтман', b='CEO OpenAI', y=600)
G('amodei', 'chip', s2r(wat('дарио', 759.5)) - 0.1, 2.8, ic='DA', a='Дарио Амодеи', b='CEO Anthropic', y=760)
G('poll', 'poll', s2r(779.3) + 1.6, round(s2r(822.6) - s2r(779.3) - 1.6, 2), head='Вопрос к первым зрителям', q='Как подавать новости?',
  opts=['Как диктор новостей', 'По-дружески и понятно'], pick=1, pickAt=round(s2r(wat('дружес', 787.5)) - s2r(779.3) - 1.6, 2),
  foot='Ответьте в комментариях')
G('end', 'end', s2r(822.6), round(total - s2r(822.6), 2), sub='Ежедневно · кроме воскресенья', head='Подписывайтесь',
  head2='Завтра в <b>06:00</b>', swapAt=round(s2r(wat('завтра', 830.3)) - s2r(822.6), 2), btn='Подписаться', day=1, total=90)

json.dump(dict(fps=FPS, total=total, gap_at=gap_at, gap=OPENER_GAP, edl=edl), open('edl.json', 'w'), ensure_ascii=False, indent=1)
json.dump(specs, open('specs.json', 'w'), ensure_ascii=False, indent=1)
print('pieces', len(edl), 'total', f'{int(total//60)}:{total%60:04.1f}')
for s in specs: print(f"{s['id']:9} {int(s['rec']//60)}:{s['rec']%60:04.1f} +{s['dur']}")
