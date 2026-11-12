# Моушн-сцены финала урока 08: тексты — только из сказанного; время — по словам субтитров.
import json, re
def A(k, **kw): kw['k'] = k; return kw
def st(at, out, *a): return {"kind": "stage", "at": at, "out": out, "actors": list(a)}
def kin(at, out, lines): return {"kind": "kinetic", "at": at, "out": out, "lines": lines}
def steps(at, out, hd, items): return {"kind": "steps", "at": at, "out": out, "hd": hd, "items": items}
nz = lambda x: re.sub(r'[^\wё-]', '', x.lower())
SP = {}
def T(sid, ph, after=0):
    s = SP.setdefault(sid, json.load(open(sid + '.spec.json'))); Wd = [w for c in s['chunks'] for w in c['words']]; p = [nz(x) for x in ph.split()]
    for i in range(len(Wd)):
        if Wd[i]['s'] >= after and all(i + k < len(Wd) and nz(Wd[i + k]['t']) == p[k] for k in range(len(p))): return Wd[i]['s']
    raise ValueError(f'{sid}: нет «{ph}» после {after}')
CX = 540; S = {}
sid = 's01_zachem_multiagenty'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('Наверное,'), [{"t": "Вот что меня лично", "at": 0.05, "size": 2}, {"t": "бесит", "at": t('лично бесит'), "hl": ["бесит"]}, {"t": "в мультиагентных системах", "at": t('мультиагентских'), "size": 3}]),
 st(t('Наверное,'), t('То есть должна'),
    A('ic', i='bot', c='a', t='мультиагентная система', z=190, x=CX, y=250, at=t('мультиагентские', 5), bob=6),
    A('tx', t='«должны быть автономные»', sz=58, x=CX, y=540, at=t('такие автономные,'), enter='up')),
 st(t('То есть должна'), t('Вот что меня', 30),
    A('ic', i='building-2', t='dark factory', z=160, x=250, y=230, at=t('darkfactory'), bob=5),
    A('ln', c='ar', x=370, y=230, x2=650, y2=230, at=t('а в итоге'), dur=0.6),
    A('ic', i='user', c='a', t='моё внимание', z=160, x=800, y=230, at=t('моего внимания,'), enter='right', bob=5),
    A('pill', t='важное — подтверждать мне', x=CX, y=520, at=t('подтверждать мне.'), enter='up')),
 kin(t('Вот что меня', 30), t('А когда задача'), [{"t": "Вот что меня", "at": t('Вот что меня', 30), "size": 2}, {"t": "лично бесит", "at": t('лично бесит', 30), "hl": ["бесит"]}]),
 st(t('А когда задача'), 99,
    A('card', i='list-checks', t='задача описана и структурирована', x=CX, y=110, at=t('хорошо описана'), enter='drop'),
    A('ic', i='bot', t='один агент', z=170, x=330, y=380, at=t('одного и того'), bob=6),
    A('tx', t='×50', sz=200, x=760, y=380, c='a', at=t('запустить 50'), enter='slam')),
]
sid = 's03_agenty_boltayut_tekstom'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('это когда мы'), [{"t": "Одно из", "at": 0.1, "size": 2}, {"t": "антипаттернов", "at": t('антипаттернов,'), "hl": ["антипаттернов"]}]),
 st(t('это когда мы'), t('Если мы начинаем'),
    *[A('ic', i='bot', z=130, x=200 + k * 340, y=200, at=t('создаем кучу') + k * 0.15, bob=5) for k in range(3)],
    A('ln', x=280, y=200, x2=460, y2=200, at=t('общаются текстом.')), A('ln', x=620, y=200, x2=800, y2=200, at=t('общаются текстом.') + 0.15),
    A('pill', t='общаются текстом', c='r', x=CX, y=390, at=t('общаются текстом.'), enter='pop'),
    A('tx', t='«а мы это никак не контролируем»', sz=46, x=CX, y=540, at=t('это никак не'), enter='up')),
 st(t('Если мы начинаем'), t('Задача codemode'),
    A('ic', i='code', c='a', t='через код', z=200, x=CX, y=250, at=t('делать это через'), enter='pop', bob=6),
    A('tx', t='гораздо более контролируемо', sz=60, x=CX, y=540, at=t('гораздо более'), enter='up')),
 steps(t('Задача codemode'), t('Это сильно'), 'Code mode', [
    {"t": "не читать контекст целиком", "i": "file-text", "at": t('чтобы читать'), "mark": "x"},
    {"t": "выполнить конкретную функцию", "i": "terminal", "at": t('выполняешь')},
    {"t": "получить конкретное поле", "i": "list-checks", "at": t('конкретное поле,')}]),
 kin(t('Это сильно'), 99, [{"t": "Сильно экономит", "at": t('Это сильно'), "size": 2}, {"t": "контекст", "at": t('контекст.', 33), "hl": ["контекст"]}]),
]
sid = 's04_ne_pishi_testy'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('я кстати'), [{"t": "Прошу не писать тесты", "at": 0.1, "size": 2, "stk": ["тесты"]}, {"t": "— работает с первого раза", "at": t('и оно работает'), "size": 3, "hl": ["первого"]}]),
 st(t('я кстати'), t('Раньше я прям'),
    A('ic', i='file-code', c='a', t='код модели', z=180, x=300, y=250, at=t('модельки довольно'), bob=6),
    A('pill', t='довольно неплохой', c='g', x=300, y=470, at=t('неплохой пишут'), enter='up'),
    A('ic', i='test-tube', t='тесты', z=150, x=800, y=250, at=t('тесты уже не'), enter='right'),
    A('tx', t='уже не так нужны', sz=48, x=800, y=470, at=t('так сильно нужны'), enter='up')),
 st(t('Раньше я прям'), t('Очень любит'),
    A('pill', t='раньше', x=270, y=90, at=t('Раньше я прям'), enter='drop'),
    A('card', i='test-tube', t='постоянно писать тесты', x=270, y=300, at=t('приходилось'), enter='left'),
    A('pill', t='сейчас', c='a', x=810, y=90, at=t('Сейчас вот инсайт'), enter='drop'),
    A('card', i='circle-check', t='не писать — с первого раза', x=810, y=300, at=t('прошу не писать', 25), enter='right')),
 steps(t('Очень любит'), t('Если ты ему'), 'Любит писать тесты', [
    {"t": "что запятая есть", "i": "hash", "at": t('что запятая')},
    {"t": "что строка правильного размера", "i": "list-checks", "at": t('что строка')}]),
 kin(t('Если ты ему'), 99, [{"t": "Запрещаешь тесты —", "at": t('Если ты ему'), "size": 2}, {"t": "справляется с первого раза", "at": t('он с первого'), "size": 3, "hl": ["первого"]}]),
]
sid = 's05_agent_nochyu'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('Oracle тоже'), [{"t": "Утром просыпаюсь —", "at": 0.05, "size": 2}, {"t": "а он пишет", "at": t('а он протокол'), "size": 2}, {"t": "свой сетевой протокол", "at": t('сетевой свой'), "size": 3, "hl": ["протокол"]}]),
 st(t('Oracle тоже'), t('У нас есть,'),
    A('ic', i='eye', c='a', t='Oracle', z=190, x=CX, y=220, at=t('Oracle тоже'), enter='pop', bob=6),
    A('pill', t='скептик', x=CX, y=420, at=t('как скептик,'), enter='up'),
    A('tx', t='разумно ли то, что мы делаем?', sz=50, x=CX, y=540, at=t('разумно ли'), enter='up')),
 st(t('У нас есть,'), t('Чтобы такого не'),
    A('ic', i='bot', t='агент на ночь', z=170, x=260, y=250, at=t('ставлю агента'), bob=6),
    A('ln', c='ar', x=380, y=250, x2=650, y2=250, at=t('утром просыпаюсь,', 20), dur=0.6),
    A('ic', i='network', c='r', t='свой сетевой протокол', z=170, x=810, y=250, at=t('а он протокол', 20), enter='slam')),
 st(t('Чтобы такого не'), t('Ну, там'),
    A('ic', i='eye', c='a', t='скептик', z=170, x=260, y=220, at=t('скептика,'), bob=6),
    A('card', i='siren', t='вовремя эскалирует', x=720, y=150, at=t('эскалирует и'), enter='right'),
    A('card', i='ban', t='остановит работу', x=720, y=300, at=t('остановит работу.'), enter='right'),
    A('tx', t='лучше остановить, чем делать непонятное', sz=42, x=CX, y=540, at=t('остановить,', 31), enter='up')),
 steps(t('Ну, там'), 99, 'Или исправить агента', [
    {"t": "обратная связь", "i": "message-square", "at": t('обратную')},
    {"t": "другое направление", "i": "route", "at": t('другом')},
    {"t": "тоже работает нормально", "i": "circle-check", "at": t('тоже работает'), "mark": "ok"}]),
]
sid = 's06_chto_takoe_guardrail'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('список правил,'), [{"t": "Guardrail —", "at": 0.1}, {"t": "просто правило", "at": t('просто такое'), "size": 2, "hl": ["правило"]}]),
 st(t('список правил,'), t('То есть, у'),
    A('card', i='list-checks', t='список правил', x=CX, y=90, at=t('список правил,'), enter='drop'),
    A('ln', c='ar', x=CX, y=170, x2=CX, y2=290, at=t('вставляются в'), dur=0.5),
    A('card', i='file-text', t='системный промпт', x=CX, y=360, at=t('системный промпт.'), enter='up'),
    A('pill', t='при каждом запросе', c='a', x=CX, y=540, at=t('каждом запросе'), enter='up')),
 st(t('То есть, у'), t('Вот как я'),
    A('ic', i='file-text', c='a', t='системный промпт', z=160, x=280, y=230, at=t('системный промпт,', 10), bob=5),
    A('tx', t='+', sz=120, x=CX, y=230, at=t('передаешь вместе'), enter='pop'),
    A('ic', i='user', t='запрос пользователя', z=160, x=800, y=230, at=t('пользовательским.'), enter='right', bob=5),
    A('tx', t='не забывается со временем', sz=56, x=CX, y=530, at=t('он не забывается'), enter='up')),
 steps(t('Вот как я'), 99, 'Свои guardrails', [
    {"t": "инструкции агентам — в MCP", "i": "server", "at": t('MCP вообще')},
    {"t": "агент стартует — подгружает", "i": "rocket", "at": t('когда агент')},
    {"t": "вставляет в системный промпт", "i": "file-text", "at": t('вставить в')},
    {"t": "бюджет и всё остальное", "i": "coins", "at": t('пишется про')}]),
]
sid = 's09_eskalaciya_v_telegram'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('у меня там'), [{"t": "В Telegram-бот —", "at": t('в Telegram-бот'), "size": 2}, {"t": "эскалация", "at": t('пишет эскалацию.'), "hl": ["эскалация"]}]),
 st(t('у меня там'), t('Я прописываю,'),
    A('pill', t='«Эскалировать»', c='a', x=290, y=120, at=t('есть ручка'), enter='drop'),
    A('pill', t='«Отправить статус»', x=790, y=120, at=t('и ручка'), enter='drop'),
    A('ln', c='ar', x=CX, y=200, x2=CX, y2=300, at=t('Она берет', 10), dur=0.5),
    A('ic', i='send', c='a', t='Telegram-бот', z=170, x=CX, y=400, at=t('в Telegram-бот', 10), enter='pop')),
 st(t('Я прописываю,'), t('Это можно было'),
    A('tx', t='когда эскалировать — прописано', sz=48, x=CX, y=70, at=t('Я прописываю,'), enter='drop'),
    A('ic', i='bot', t='агент', z=150, x=200, y=300, at=t('эта эскалация'), bob=5),
    A('ln', c='ar', x=300, y=300, x2=440, y2=300, at=t('он через MCP'), dur=0.4),
    A('ic', i='server', c='a', t='MCP', z=150, x=CX, y=300, at=t('он через MCP'), enter='pop'),
    A('ln', c='ar', x=640, y=300, x2=780, y2=300, at=t('сообщения боту.'), dur=0.4),
    A('ic', i='send', t='бот', z=150, x=880, y=300, at=t('сообщения боту.'), enter='right')),
 st(t('Это можно было'), t('и в ответ'),
    A('card', i='shield-check', t='в guardrails', x=CX, y=110, at=t('в guardrails'), enter='left'),
    A('card', i='bot', t='в отдельном субагенте', x=CX, y=260, at=t('просто в субагенте'), enter='right'),
    A('pill', t='засорял бы контекст', c='r', x=CX, y=430, at=t('засорял контекст,'), enter='pop'),
    A('pill', t='просто ручка «Эскалировать»', c='a', x=CX, y=540, at=t('есть просто ручка'), enter='up')),
 steps(t('и в ответ'), 99, 'Дальше агент', [
    {"t": "ждёт, пока обновлю статус", "i": "hourglass", "at": t('он ждет,')},
    {"t": "постоянно опрашивает MCP", "i": "refresh-cw", "at": t('постоянно его')},
    {"t": "есть результат — продолжает", "i": "circle-check", "at": t('то продолжает'), "mark": "ok"}]),
]
sid = 's10_na_chto_tratit_dengi'; t = lambda p, a=0: T(sid, p, a)
S[sid] = [
 kin(0, t('Но, по'), [{"t": "Для исполнения —", "at": 0.05, "size": 2}, {"t": "локальная 70B или 30B", "at": t('локальную на'), "size": 3, "hl": ["70B", "30B"]}]),
 st(t('Но, по'), t('Если у тебя'),
    A('card', i='brain', t='планирование', x=290, y=130, at=t('планирование.'), enter='left'),
    A('pill', t='высокий effort', c='a', x=290, y=300, at=t('высокий уровень'), enter='up'),
    A('card', i='cpu', t='всё остальное', x=800, y=130, at=t('А все остальное'), enter='right'),
    A('pill', t='на маленьком', x=800, y=300, at=t('на маленьком.'), enter='up')),
 st(t('Если у тебя'), t('И единственное,'),
    A('ic', i='list-checks', c='a', t='точный атомарный план', z=190, x=CX, y=230, at=t('атомарный'), enter='pop', bob=6),
    A('tx', t='чтобы контекст не переполнился', sz=52, x=CX, y=530, at=t('это чтобы контекст'), enter='up')),
 steps(t('И единственное,'), t('Типа какую-то'), 'Реально стоит тратить деньги', [
    {"t": "планирование", "i": "brain", "at": t('это планирование.')},
    {"t": "research", "i": "search", "at": t('И задача research.')}]),
 st(t('Типа какую-то'), 99,
    A('card', i='sparkles', t='крутая модель → планирование', x=CX, y=140, at=t('крутую модельку'), enter='left'),
    A('card', i='cpu', t='локальная 70B / 30B → исполнение', x=CX, y=330, at=t('локальную на', 35), enter='right'),
    A('pill', t='тоже пойдёт нормально', c='g', x=CX, y=520, at=t('тоже пойдет'), enter='up')),
]
OUT = []
for sid, sc in S.items():
    s = SP[sid]; end = round(s['dur'] - s['endDur'], 2)
    for x in sc:
        if x['out'] == 99: x['out'] = end
    for a, b in zip(sc, sc[1:]):
        assert a['at'] < a['out'] <= b['at'] + 0.01, (sid, a['kind'], a['at'], a['out'], b['at'])
    f = sc[0]; s['scenes'] = sc
    s['sfx'] = [{'file': 'sfx_whoosh.wav', 'at': 0.0, 'vol': 0.35}] + [{'file': 'sfx_pop.wav', 'at': l['at'], 'vol': 0.35} for l in f['lines']]
    s['pv'] = [1.0] + [round((x['at'] + x['out']) / 2, 2) for x in sc[1:]] + [round(s['dur'] - 0.8, 2)]
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1); OUT.append(s)
    print(sid, [(x['kind'], x['at'], x['out']) for x in sc])
json.dump(OUT, open('specs7.json', 'w'), ensure_ascii=False)
