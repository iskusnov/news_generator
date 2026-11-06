#!/usr/bin/env python3
"""Графика спецвыпуска 06.11 «ИИ за неделю»: edl (speed.py + inserts.py) + words → specs.json. Всё поверх кадра с ведущим.
Врезки-ролики (clip) идут на весь кадр со своим звуком; на них только подпись источника."""
import json, sys
D = sys.argv[1]
E = json.load(open(f'{D}/ep/edl.json')); W = json.load(open(f'{D}/words.json'))['words']; FPS = 25
fr = lambda t: round(t * FPS) / FPS
def s2r(t):
    for e in E['edl']:
        if not e.get('clip') and e['src_in'] - 0.05 <= t <= e['src_out'] + 0.05: return fr(e['rec'] + max(0, t - e['src_in']) / e.get('speed', 1.0))
    nx = [e for e in E['edl'] if not e.get('clip') and e['src_in'] > t]
    if nx and nx[0]['src_in'] - t < 3: return fr(nx[0]['rec'])
    raise ValueError(t)
def wat(p, near):
    c = [w for w in W if w['word'].lower().strip('.,?!«»"$').startswith(p.lower()) and abs(w['start'] - near) < 8]
    assert c, (p, near); return min(c, key=lambda w: abs(w['start'] - near))['start']
S = []
def G(id, type, rec, dur, **kw): S.append(dict(id=id, type=type, rec=fr(rec), dur=dur, **kw))
FIX = {'И': 'ИИ', 'И...': '', 'Эппл': 'Apple', 'квот': 'Claude'}
def quote(id, a, b, hl, mark, tail=1.0):
    ws = [w for w in W if a - 0.05 <= w['start'] <= b]; r0 = s2r(ws[0]['start']) - 0.25
    words = [dict(t=FIX.get(w['word'], w['word']), at=round(s2r(w['start']) - r0, 2), hl=any(w['word'].lower().startswith(h) for h in hl)) for w in ws]
    G(id, 'quote', r0, round(s2r(ws[-1]['start']) - r0 + tail, 2), words=[w for w in words if w['t']], mark=mark)
SH = '../shots/1106_'
# подписи источников на врезках-роликах
for e in E['edl']:
    if e.get('clip') and e.get('label'):
        G('src_' + e['clip'].split('.')[0], 'chip', e['rec'] + 0.3, min(4.5, e['dur'] - 0.5), ic='▶', a=e['label'], b='ролик целиком — по ссылке в описании', y=880)
# блоки
for i, (t, ttl) in enumerate([(20.04, 'Агентам выдали лицо, почту и кошелёк'), (685.71, 'ИИ-слоп пошёл во власть'),
                              (1654.34, 'Великая распродажа ИИ'), (2543.97, 'Хуанг, Маск, Хаксли и инопланетяне'), (4075.3, 'Напоследок: Nothing')], 1):
    G(f'k{i:02d}', 'kicker', s2r(t) - 0.6, 3.4, num=f'{i:02d}', title=ttl)
G('lower', 'lower', s2r(wat('при', 24.4)) + 1.0, 4.6, name='Антон Искуснов', role='Пока ты спал · спецвыпуск «ИИ за неделю»')
# 1 Агенты
G('sh_uber', 'shot', s2r(wat('uber', 25.84)) + 2.2, 5.0, src=SH + 'og_uber.jpg', lb='TechCrunch · 4 ноября', top=200)
G('st_4', 'stat', s2r(wat('4', 30.48)) - 0.2, 3.6, big='4', label='поездки на такси через ИИ-агентов', sub='Uber · самая загруженная неделя октября', side='l')
G('st_320', 'stat', s2r(wat('320', 39.66)) - 0.2, 4.0, big='320 млн', label='заказов за неделю — и только 4 поездки через агентов', sub='+ около 500 заказов еды')
G('ch_50', 'chip', s2r(wat('50', 73.79)) - 0.3, 5.0, ic='⏱', a='Такси — 50 секунд, еда — 90', b='агентам тут нечего ускорять', y=760)
G('ch_cap', 'chip', s2r(wat('копчу', 90.27)) - 0.6, 4.4, ic='✕', a='Капча и ручной ввод карты', b='на этом агенты пока спотыкаются', y=760)
G('st_muse', 'stat', s2r(wat('10', 250.33)) - 0.3, 3.8, big='10 млн+', label='скачиваний Meta Muse', sub='№1 в App Store США месяц назад', side='l')
G('sh_mm', 'shot', s2r(wat('machine', 269.98)) - 0.3, 6.0, src=SH + 'og_machinemail.jpg', lb='machinemail.dev', top=200)
G('ch_trust', 'chip', s2r(wat('отчет', 299.0)) - 0.8, 4.6, ic='✓', a='Под каждым письмом — отчёт о доверии', b='агента не «разведут как бабушку»', y=760)
G('sh_cl', 'shot', s2r(wat('сегодня', 405.1)) - 0.2, 7.0, src=SH + 'post_claude.png', lb='X · @claudeai', top=180)  # до ролика
G('ch_ro', 'chip', s2r(wat('только', 447.22)) - 0.3, 4.6, ic='🔒', a='Только чтение', b='Claude не может переводить и инвестировать', y=760)
quote('q_intern', 559.15, 569.3, ['стажера', 'побаиваются'], 'ВЫВОД', 1.2)
# 2 Слоп
G('st_289', 'stat', s2r(wat('289', 848.61)) - 0.3, 3.4, big='289', label='ИИ-роликов в рекламе на выборах', sub='Wesleyan Media Project', side='l')
G('st_187', 'stat', s2r(wat('187', 853.07)) - 0.3, 3.6, big='$187 млн', label='потрачено на ИИ-рекламу', sub='в 2024 году — около $50 тыс')
G('st_x', 'stat', s2r(wat('тысячу', 873.79)) - 0.4, 3.6, big='×3700', label='рост за два года', sub='$50 тыс → $187 млн', side='l')
G('ch_lbl', 'chip', s2r(wat('пометки', 1027.42)) - 0.6, 4.4, ic='!', a='Многие ролики выходят без пометки «ИИ»', b='реальных роликов может быть больше', y=760)
G('st_15', 'stat', s2r(wat('15', 1115.93)) - 0.2, 3.6, big='15 сек', label='ролик за один запрос', sub='на 30% дешевле прошлой версии', side='l')
G('st_1usd', 'stat', s2r(wat('15', 1141.34)) - 0.3, 3.8, big='≈ $1', label='ролик в 15 секунд', sub='~7 центов за секунду в API', side='l')
G('sh_ar', 'shot', s2r(wat('слепых', 1169.32)) - 0.2, 6.0, src=SH + 'post_arena.png', lb='X · @arena', top=220)
G('sh_az', 'shot', s2r(wat('arsace', 1205.45)) - 0.2, 6.6, src=SH + 'arsaze.jpg', lb='arsaze.com', top=200)
G('st_az', 'stat', s2r(wat('3', 1264.10)) - 0.3, 4.2, big='23 мин', label='вместо 3 ч 12 мин ручного монтажа', sub='Claude + Arsaze · тест автора', side='l')
G('ch_az', 'chip', s2r(wat('при', 1324.76)) - 0.2, 4.6, ic='↓', a='Подключается к Claude как коннектор', b='ссылка и инструкция — в Telegram', y=760)
G('sh_pg', 'shot', s2r(wat('pangram', 1407.05)) - 0.4, 6.0, src=SH + 'og_pangram.jpg', lb='pangram.com · блог', top=200)
G('st_pg', 'stat', s2r(wat('99', 1452.40)) - 0.3, 4.0, big='99,96%', label='точность — по словам компании', sub='независимой проверки пока нет', side='l')
quote('q_who', 1559.85, 1564.6, ['кто', 'зачем'], 'ВЫВОД', 1.2)
quote('q_yoga', 1605.66, 1609.9, ['йога', 'работает'], 'ПАНЧ', 1.2)
# 3 Распродажа
G('ch_occ', 'chip', s2r(wat('occupy', 1745.53)) - 0.2, 5.0, ic='✊', a='OccupySaaS', b='открытые клоны платных сервисов · github.com/occupysaas', y=760)
G('ch_za', 'chip', s2r(wat('zero', 1793.83)) - 0.3, 4.2, ic='→', a='ZeroAuthy ← Auth0 · SalesCompel ← Salesforce', b='первые два клона', y=760)
G('ch_nc', 'chip', s2r(wat('крадет', 1828.44)) - 0.6, 4.6, ic='✓', a='Не копирует чужой код', b='пишет сервис заново по описанию', y=760)
G('sh_kimi', 'shot', s2r(wat('moonshot', 1995.4)) + 0.3, 5.6, src=SH + 'og_kimi.jpg', lb='Hugging Face · открытые веса', top=200)
G('st_28', 'stat', s2r(wat('2,8', 2008.0)) - 0.3, 3.6, big='2,8 трлн', label='параметров', sub='окно — около миллиона токенов', side='l')
G('ch_moe', 'chip', s2r(wat('представьте', 2054.95)), 5.6, ic='⚕', a='Смесь экспертов', b='на каждый запрос работает лишь малая часть модели', y=760)
G('sh_rv', 'shot', s2r(wat('по', 2228.76)) + 0.2, 6.0, src=SH + 'og_revolut.jpg', lb='The Register · Revolut', top=200)
G('st_rv', 'stat', s2r(wat('результат', 2248.1)) - 0.2, 4.0, big='−90%', label='расходы Revolut на ИИ для кода', sub='открытая GLM на своих серверах', side='l')
G('st_ap', 'stat', s2r(wat('раньше', 2281.4)) - 0.2, 5.0, big='$25', label='новый лимит Apple на ИИ в день', sub='было $300 → $200 → $100 · Bloomberg')
G('st_6k', 'stat', s2r(wat('6000', 2307.0)) - 0.3, 3.6, big='$6000', label='в месяц на одного инженера', sub='при лимите $300 в день', side='l')
quote('q_calc', 2467.34, 2487.0, ['калькулятором'], 'ВЫВОД', 1.2)
quote('q_cap', 2510.1, 2523.0, ['капучино', 'круассана'], 'ПАНЧ', 1.2)
# 4 Космос
G('sh_ata', 'shot', s2r(wat('в', 2630.8)) + 0.4, 6.4, src=SH + 'og_nvidia.jpg', lb='Allen Telescope Array · NVIDIA', top=180)
G('st_tb', 'stat', s2r(wat('2,4', 2803.0)) - 0.3, 4.2, big='2,4 Тб/с', label='скорость обработки', sub='≈ 300 фильмов в секунду', side='l')
quote('q_alien', 3075.11, 3099.2, ['инопланетянами', 'создали'], 'ЭНДРЮ СИМИОН · BREAKTHROUGH LISTEN', 1.2)
G('sh_musk', 'shot', s2r(wat('ясамин', 3154.92)) - 0.2, 9.0, src=SH + 'post_musk.png', lb='X · @elonmusk', top=180)
quote('q_free', 3293.5, 3297.4, ['счастливыми', 'свободными'], 'ХАКСЛИ', 1.2)
quote('q_sub', 4049.8, 4056.0, ['подписку'], 'ПАНЧ', 1.2)
G('sh_nth', 'shot', s2r(wat('компания', 4075.3)) + 1.0, 6.0, src=SH + 'og_nothing.jpg', lb='TechCrunch · Nothing', top=200)
G('ch_tg', 'chip', s2r(wat('телеграм', 5002.9)) - 0.3, 6.5, ic='✈', a='t.me/scaling_ai', b='гиты, ссылки, плейбуки — ссылка в описании', y=760)
G('outro', 'outro', E['total'] + 0.2, 5.0, day=5, total=90)
clips = [(e['rec'], e['rec'] + e['dur']) for e in E['edl'] if e.get('clip')]
for x in S:  # плашки не заходят на ролики: старт после ролика, конец до ролика
    if x['id'].startswith('src_') or x['type'] == 'outro': continue
    for a, b in clips:
        if a - 0.05 <= x['rec'] < b: x['rec'] = fr(b + 0.15)
        elif x['rec'] < a < x['rec'] + x['dur']: x['dur'] = round(a - x['rec'] - 0.1, 2)
S.sort(key=lambda s: s['rec'])
for a, b in zip(S, S[1:]):
    if a['type'] == b['type'] and a['type'] in ('quote', 'chip', 'shot') and b['rec'] < a['rec'] + a['dur']: a['dur'] = round(b['rec'] - a['rec'] - 0.1, 2)
json.dump(S, open(f'{D}/ep/specs.json', 'w'), ensure_ascii=False, indent=1)
# пересечения и наезды на врезки-ролики
clips = [(e['rec'], e['rec'] + e['dur']) for e in E['edl'] if e.get('clip')]
for s in S:
    if s['id'].startswith('src_') or s['type'] == 'outro': continue
    for a, b in clips:
        if s['rec'] < b and s['rec'] + s['dur'] > a: print('НА РОЛИК', s['id'], s['rec'], (a, b))
for a, b in zip(S, S[1:]):
    if b['rec'] < a['rec'] + a['dur'] and a['type'] not in ('kicker', 'lower') and b['type'] not in ('kicker', 'lower') and not a['id'].startswith('src_'):
        print('НАЛОЖЕНИЕ', a['id'], b['id'], a['rec'], b['rec'])
print(len(S), 'плашек')
