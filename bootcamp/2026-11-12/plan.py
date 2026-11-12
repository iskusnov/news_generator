# План графики урока 09 (12.11.2026, Harness) — время исходника → list.json (render_list.js) + gfx.json (nation_base.py)
import json
W = '/home/claude/work/b1112/'
CH = json.load(open(W + 'chapters_src.json'))
LECT = 'Николай Барышников'; ORG = 'ex-Yandex Cloud'; NUM = '09'; TOPIC = 'Harness'; ROLE = 'dev'
DUR = 12175.27
PARTS = {'Вступление': 'Вступление', 'Часть 1. Что такое harness': 'Часть 1 · Что такое harness', 'Часть 2. Компоненты harness': 'Часть 2 · Компоненты',
         'Часть 3. Готовые harness': 'Часть 3 · Готовые harness', 'Часть 4. Проблемы, которые решает harness': 'Часть 4 · Проблемы', 'Итог': 'Итог урока'}
L = []; G = {'frames': [], 'cards': [], 'qside': json.load(open(W + 'participants.json')), 'noshare': json.load(open(W + 'noshare.json'))}
for i, c in enumerate(CH):
    a = 0 if i == 0 else c['t']; b = CH[i + 1]['t'] if i + 1 < len(CH) else DUR
    f = f'gfx/fr_{c["n"].replace(".", "_").replace("—", "end")}.png'
    L.append({'out': W + f, 'spec': {'type': 'frame', 'lector': LECT, 'org': ORG, 'role': ROLE, 'num': NUM, 'topic': 'Harness: инженерия вокруг модели',
              'part': PARTS[c['part']], 'ch': c['n'] if c['n'] != '—' else '✓', 'chTitle': c['title'], 'progress': round((c['t'] - 795) / (DUR - 795), 3)}})
    G['frames'].append([a, b, f])
L.append({'out': W + 'gfx/roletop.png', 'alpha': 1, 'spec': {'type': 'roletop', 'role': ROLE}})
L.append({'out': W + 'gfx/qside.png', 'alpha': 1, 'spec': {'type': 'qside'}})
G['roletop'] = 'gfx/roletop.png'; G['qside_png'] = 'gfx/qside.png'
def card(cid, t, dur, spec, alpha=1, kind='overlay'):
    f = f'gfx/{cid}.png'; L.append({'out': W + f, 'alpha': alpha, 'spec': spec}); G['cards'].append({'id': cid, 'from': t, 'to': t + dur, 'png': f, 'kind': kind})
card('speaker', 800, 5.5, {'type': 'speaker', 'lector': LECT, 'org': ORG, 'role': ROLE, 'sub': 'ведёт урок 09'})
for cid, t, n, title, sub in [('part1', 1474, 1, 'Что такое harness', 'Модель, агент и harness: цикл с планом, рантайм, сборка контекста, observability'),
                              ('part2', 3236, 2, 'Компоненты harness', 'Model router, policy engine, state, восстановление, ошибки, репланинг, качество'),
                              ('part3', 7538, 3, 'Готовые harness', 'Мультиагентный рантайм, уровни зрелости; Pi, OpenAI Agents SDK, LangGraph, Claude Agent'),
                              ('part4', 10732, 4, 'Проблемы, которые решает harness', 'Отравление контекста, runaway agent loop, schema drift, скрытый недетерминизм')]:
    card(cid, t, 4.6, {'type': 'chapter', 'n': n, 'total': 4, 'title': title, 'sub': sub}, alpha=0, kind='chapter')
SIDE = [
 ('t_harness', 852, 'Термин', 'Harness', 'По сути, это просто инженерия вокруг модельки.'),
 ('t_runtime', 1980, 'Термин', 'Рантайм', 'Контейнер, какая-то операционная система: Docker, виртуалка, bash, PowerShell. Агент всегда запускается где-то в рантайме.'),
 ('t_compiler', 2395, 'Термин', 'Context compiler', 'Штука, которая собирает контекст и может им управлять, чтобы контекст сильно не разросся.'),
 ('t_router', 3286, 'Термин', 'Model router', 'Решение о том, что нужно пойти не в эту модельку, а в какую-то другую: поменьше, побольше, для рассуждения.'),
 ('t_policy', 3298, 'Термин', 'Policy engine', 'Место управления, отдельное от контекста, где хранятся правила: как ходим в MCP, как просим пользователя помочь.'),
 ('t_stateless', 3690, 'Термин', 'Stateless', 'В контейнере, в котором агент работает, статус не хранится — стейт приходит вместе с запросом.'),
 ('t_replan', 4603, 'Термин', 'Репланинг', 'Остановиться там, где мы находимся, пересмотреть план целиком, доуточнить и проверить другими агентами.'),
 ('t_dark', 5730, 'Термин', 'Dark factory', 'Как магазины Лавки и Самоката, только с кодом: внутри какая-то магия — и он выплёвывает код.'),
 ('t_observ', 6246, 'Термин', 'Observability', 'Наблюдаемость: с её помощью оцениваем, видим прозрачно и можем это посчитать.'),
 ('t_poison', 10860, 'Термин', 'Retrieval poisoning', 'Получаем неверные данные из RAG и даже не знаем о том, что мы эти данные получили.'),
 ('t_runaway', 10944, 'Термин', 'Runaway agent loop', 'Вечный цикл: агент делает одно и то же несколько раз. Ставим бюджеты и правило: попыток не больше трёх.'),
 ('t_drift', 11035, 'Термин', 'Schema drift', 'Переменные для LLM пишутся в разных нотациях: для модели это одна схема, а в коде начнутся проблемы.'),
]
QUO = [
 ('q_utopia', 1312, 'Ощущение о том, что сейчас моделька всё делает за меня, — это, конечно, утопия'),
 ('q_plan', 1935, 'Если мы меняем план, то планировать должны другие агенты'),
 ('q_eval', 6299, 'Без observability evaluation невозможно'),
 ('q_graph', 10265, 'Агенты круче, чем графы, стопудово'),
 ('q_escape', 11610, 'Гораздо эффективнее даже два раза Escape назад нажать и вернуться к точке'),
]
for cid, t, kind, term, text in SIDE: card(cid, t, 9, {'type': 'side', 'kind': kind, 'term': term, 'text': text})
for cid, t, text in QUO: card(cid, t, 8, {'type': 'side', 'kind': 'Цитата', 'text': text, 'who': LECT})
L.append({'out': W + 'gfx/hw.png', 'spec': {'type': 'hw', 'num': NUM, 'title': 'Доделайте практику урока: harness своего агента',
          'text': 'На уроке рисовали harness для себя: какие кубики нужны, лишние уберите, что в них внесёте и как подключите к своему агенту — Claude Code, Cursor или другому.',
          'items': ['Проблемы, с которыми сталкиваетесь со своими агентами', 'Что сделаете после урока, чтобы такого больше не было', 'Вопросы для рефлексии — в презентации урока'],
          'foot': 'Текстовая версия урока, ДЗ и файл для нейросети — на странице урока'}})
L.append({'out': W + 'gfx/end.png', 'spec': {'type': 'end', 'num': NUM, 'topic': 'Harness', 'title': 'До встречи на следующем уроке',
          'text': 'Лекция, домашнее задание и файл для нейросети — на странице урока.'}})
G['camoff'] = json.load(open(W + 'camoff.json')); G['camoff_png'] = 'gfx/camoff.png'
G.update({'intro_mp4': 'gfx/intro.mp4', 'intro': 'gfx/end.png', 'hw': 'gfx/hw.png', 'end': 'gfx/end.png'})
json.dump(L, open(W + 'list.json', 'w'), ensure_ascii=False)
json.dump(G, open(W + 'gfx.json', 'w'), ensure_ascii=False, indent=1)
print(len(L), 'кадров;', len(G['cards']), 'плашек')
