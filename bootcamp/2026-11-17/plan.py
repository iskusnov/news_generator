# План графики урока 10 (17.11.2026, практика на Mastodon) — время исходника → list.json (render_list.js) + gfx.json (nation_base.py)
# Раскладка frame3: экран 1504×846 по центру по вертикали (NB_SY=117), колонка справа; камера лектора выключена весь урок → монограмма.
# Окна Zoom на демонстрации нет; нижней строки «Нэйшн · …» нет (просьба Антона 17.11: без дублей названий).
import json
W = '/home/claude/work/b1117/'
CH = json.load(open(W + 'chapters_src.json'))
LECT = 'Михаил Овчинников'; ORG = 'Staff-инженер, Google'
PHOTO = 'data:image/jpeg;base64,' + __import__('base64').b64encode(open(W + 'photo/m.jpg', 'rb').read()).decode(); NUM = '10'; ROLE = 'dev'; TOP = 117
DUR = 9333.5; T0 = 146.6
PARTS = {'Вступление': 'Вступление', 'Часть 1. Разведка незнакомого репозитория': 'Часть 1 · Разведка репозитория',
         'Часть 2. Как устроены нотификации': 'Часть 2 · Нотификации', 'Часть 3. Спецификации с OpenSpec': 'Часть 3 · Спеки в OpenSpec',
         'Часть 4. Поиск решения': 'Часть 4 · Поиск решения', 'Часть 5. Ревью, ADR и скиллы': 'Часть 5 · Ревью, ADR, скиллы', 'Итог и вопросы': 'Итог и вопросы'}
L = []; G = {'frames': [], 'cards': [], 'qside': json.load(open(W + 'participants.json')), 'noshare': [], 'nocam': True}
for i, c in enumerate(CH):
    a = 0 if i == 0 else c['t']; b = CH[i + 1]['t'] if i + 1 < len(CH) else DUR
    f = f'gfx/fr_{c["n"].replace(".", "_")}.png'
    L.append({'out': W + f, 'spec': {'type': 'frame3', 'top': TOP, 'photo': PHOTO, 'lector': LECT, 'org': ORG, 'role': ROLE,
              'part': PARTS[c['part']], 'ch': c['n'], 'chTitle': c['title'], 'progress': round(max(0, c['t'] - T0) / (DUR - T0), 3)}})
    G['frames'].append([a, b, f])
L.append({'out': W + 'gfx/qside.png', 'alpha': 1, 'spec': {'type': 'qside3', 'top': TOP}})
G['qside_png'] = 'gfx/qside.png'
def card(cid, t, dur, spec, alpha=1, kind='overlay'):
    f = f'gfx/{cid}.png'; L.append({'out': W + f, 'alpha': alpha, 'spec': spec}); G['cards'].append({'id': cid, 'from': t, 'to': t + dur, 'png': f, 'kind': kind})
for cid, t, n, title, sub in [('part1', 309, 1, 'Разведка незнакомого репозитория', 'Mastodon, DeepWiki, первый промпт «что есть и чего нет», OpenSpec'),
                              ('part2', 1850, 2, 'Как устроены нотификации', 'Архитектура и сценарии, профиль нагрузки, три уровня спецификации'),
                              ('part3', 2969, 3, 'Спецификации с OpenSpec', 'Спеки пользователя, компонентов и базы данных; explore, propose, apply'),
                              ('part4', 4868, 4, 'Поиск решения', 'Топ-3 тяжеловесных и сложных точек, три направления оптимизации, Postgres или Redis'),
                              ('part5', 6606, 5, 'Ревью, ADR и скиллы', 'Ревью субагентами, файл принятых решений, папка reviewers и скилл review')]:
    card(cid, t, 4.6, {'type': 'chapter', 'n': n, 'total': 5, 'title': title, 'sub': sub}, alpha=0, kind='chapter')
SIDE = [
 ('t_deepwiki', 432, 'Термин', 'DeepWiki', 'Позволяет посмотреть у любого GitHub-репозитория сгенерированную документацию на основе всего, что в репозитории есть.'),
 ('t_openspec', 1281, 'Термин', 'OpenSpec', 'Чтобы с ним работать, нужно набрать команду openspec init и выбрать свою среду — появятся OpenSpec-скиллы, и можно создавать спеки.'),
 ('t_levels', 2672, 'Термин', 'Три уровня спецификации', 'Пользовательский — что пользователь ожидает от системы; системный — какие компоненты как должны себя вести; уровень базы данных — что происходит в базе.'),
 ('t_adr', 7109, 'Термин', 'ADR', 'Файл, в который записываем все решения, принятые по проекту.'),
 ('t_final', 8090, 'Термин', 'Финальный ревьюер', 'Ревьюеры что-то находят, а финальный ревьюер каждую находку классифицирует.'),
]
QUO = [
 ('q_answers', 5346, 'Мне очень нравятся его ответы, потому что я их не понимаю'),
 ('q_context', 5518, 'Если в контекст агента это влезает, то в мой контекст это уже не влезает'),
 ('q_trust', 7024, 'Я хочу наладить такие механизмы контроля, которые мне позволят убедиться, что я могу доверять агенту'),
]
for cid, t, kind, term, text in SIDE: card(cid, t, 9, {'type': 'side', 'kind': kind, 'term': term, 'text': text})
for cid, t, text in QUO: card(cid, t, 8, {'type': 'side', 'kind': 'Цитата', 'text': text, 'who': LECT})
L.append({'out': W + 'gfx/hw.png', 'spec': {'type': 'hw', 'num': NUM, 'title': 'Повторите действия, которые мы сделали на уроке',
          'text': 'Домашнего задания прямо сейчас не будет: урок продолжится в четверг. Если хотите за нами поспеть — повторите действия, которые мы сделали на уроке.',
          'items': ['Разведка репозитория и отчёт «что есть и чего нет»', 'Спеки трёх уровней в OpenSpec', 'Ревью субагентами и файл принятых решений (ADR)'],
          'foot': 'Текстовая версия урока и файл для нейросети — на странице урока'}})
L.append({'out': W + 'gfx/end.png', 'spec': {'type': 'end', 'num': NUM, 'topic': 'Практика на Mastodon', 'title': 'До встречи на следующем уроке',
          'text': 'Текстовая версия урока и файл для нейросети — на странице урока.'}})
G.update({'intro_mp4': 'gfx/intro.mp4', 'intro': 'gfx/end.png', 'hw': 'gfx/hw.png', 'end': 'gfx/end.png'})
json.dump(L, open(W + 'list.json', 'w'), ensure_ascii=False)
json.dump(G, open(W + 'gfx.json', 'w'), ensure_ascii=False, indent=1)
print(len(L), 'кадров;', len(G['cards']), 'плашек')
