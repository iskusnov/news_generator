# План графики урока 12 (24.11.2026, End-to-end SDLC, Даниил Пилипенко) — время исходника → list.json + gfx.json (nation_base.py)
# Раскладка frame3 (NB_SY=117): экран 1504×846 + колонка справа с живой камерой лектора. Слайды — страницы PDF в окне экрана (video_iv.json slides).
# Окно Zoom в углу демонстрации закрывается белой плашкой «Нэйшн» только там, где оно есть и слайд не заменён (zoom_iv).
import json, base64
W = '/home/claude/work/b1124/'
CH = json.load(open(W + 'chapters_src.json')); VI = json.load(open(W + 'video_iv.json')); META = json.load(open(W + 'out/meta.json'))
LECT = 'Даниил Пилипенко'; ORG = 'SymbioWay'; NUM = '12'; ROLE = 'dev'; TOP = 117
PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(open(W + 'photo.jpg', 'rb').read()).decode()
DUR = 6513.0; T0 = 478.7
PARTS = {'Часть 1. От системной декомпозиции к ИИ-сотрудникам': 'Часть 1 · К ИИ-сотрудникам', 'Часть 2. Задание: проектируем ИИ-разработчика': 'Часть 2 · Задание',
         'Часть 3. Выступления команд и разбор': 'Часть 3 · Выступления команд', 'Часть 4. Домашнее задание и диаграмма лектора': 'Часть 4 · ДЗ и диаграмма лектора',
         'Часть 5. Вопросы и ответы': 'Часть 5 · Вопросы и ответы'}
L = []; G = {'frames': [], 'cards': [], 'qside': [], 'noshare': VI['V'], 'slides': VI['slides'], 'zoom_plate': 'gfx/zoom_plate.png', 'zoom_iv': VI['Z']}
for i, c in enumerate(CH):
    a = 0 if i == 0 else c['t']; b = CH[i + 1]['t'] if i + 1 < len(CH) else DUR
    f = f'gfx/fr_{c["n"].replace(".", "_")}.png'
    L.append({'out': W + f, 'spec': {'type': 'frame3', 'top': TOP, 'photo': PHOTO, 'lector': LECT, 'org': ORG, 'role': ROLE,
              'part': PARTS[c['part']], 'ch': c['n'], 'chTitle': c['title'], 'progress': round(max(0, c['t'] - T0) / (DUR - T0), 3)}})
    G['frames'].append([a, b, f])
L.append({'out': W + 'gfx/qside.png', 'alpha': 1, 'spec': {'type': 'qside3', 'top': TOP}})
G['qside_png'] = 'gfx/qside.png'
def card(cid, t, dur, spec, alpha=1, kind='overlay', png=None):
    f = png or f'gfx/{cid}.png'
    if not png: L.append({'out': W + f, 'alpha': alpha, 'spec': spec})
    G['cards'].append({'id': cid, 'from': t, 'to': t + dur, 'png': f, 'kind': kind})
# реплики участников: в блоках команд — «Команда N · выступление», иначе — «Вопрос из зала»; плюс тёмные плитки Zoom (D)
P = json.load(open(W + 'participants.json')) + VI['D']
TEAMS = [(g['n'], g['t_from'], g['t_to']) for g in META['groups']]
for n, a, b in TEAMS:
    L.append({'out': W + f'gfx/qteam{n}.png', 'alpha': 1, 'spec': {'type': 'qside3', 'top': TOP, 'label': f'Команда {n}', 'sub': 'Выступление'}})
for a, b in P:
    tm = [n for n, ta, tb in TEAMS if ta <= a < tb]
    if tm: card(f'qt{a}', a, b - a, None, png=f'gfx/qteam{tm[0]}.png')
    else: G['qside'].append([a, b])
for cid, t, n, title, sub in [('part1', 478.7, 1, 'От системной декомпозиции к ИИ-сотрудникам', 'Паттерн декомпозиции, ИИ-модель и живой разработчик, Human-off-the-loop, свой фреймворк'),
                              ('part2', 1404.0, 2, 'Задание: проектируем ИИ-разработчика', 'Диаграмма активностей системы, подключённой к GitLab: от задачи до продакшна'),
                              ('part3', 2281.3, 3, 'Выступления команд и разбор', 'Четыре команды, четыре схемы ИИ-разработчика и разбор лектора'),
                              ('part4', 4718.0, 4, 'Домашнее задание и диаграмма лектора', 'Реализовать фреймворк по своей диаграмме; с чего начинали у себя'),
                              ('part5', 5112.2, 5, 'Вопросы и ответы', 'Точки контроля человека, модель, тестовые версии, стоимость задачи')]:
    card(cid, t, 4.6, {'type': 'chapter', 'n': n, 'total': 5, 'title': title, 'sub': sub}, alpha=0, kind='chapter')
SIDE = [
 ('t_blackbox', 916, 'Термин', 'Black box', 'Если мы сделаем систему закрытого цикла — вы что-то просите, она что-то выдаёт, — для нас она в значительной мере будет black box, если мы не знаем, как она работает внутри.'),
 ('t_hotl', 989, 'Термин', 'Human-off-the-loop', 'Инструменты полного цикла: если задача ставится понятно, чётко, то реализовать её по спецификации, протестировать, задеплоить — вполне автоматизируемые шаги.'),
 ('t_apifirst', 2915, 'Термин', 'API-first', 'Мы сначала пишем спецификацию, потом всё остальное разрабатываем — фронт, бэк и тесты.'),
]
QUO = [
 ('q_elementary', 1203, 'Это элементарный запрос, никакой человек для выполнения такого запроса вообще не требуется'),
 ('q_elephant', 2948.5, 'Крупных агентов с большим расходом контекста вообще не делать никогда'),
]
for cid, t, kind, term, text in SIDE: card(cid, t, 9, {'type': 'side', 'kind': kind, 'term': term, 'text': text})
for cid, t, text in QUO: card(cid, t, 8, {'type': 'side', 'kind': 'Цитата', 'text': text, 'who': LECT})
L.append({'out': W + 'gfx/hw.png', 'spec': {'type': 'hw', 'num': NUM, 'title': 'Реализуйте фреймворк по своей диаграмме',
          'text': 'Создать новый проект, загрузить туда диаграмму и попросить агента создать фреймворк, который будет реализовывать работу в рамках этой диаграммы, — утилиту, которую можно подключить к GitLab. Задание по желанию.',
          'items': ['Модераторы публикуют диаграммы в общем чате', 'Новый проект: диаграмма → агент создаёт фреймворк', 'Пишите в чат, что у вас получилось'],
          'foot': 'Текстовая версия урока, ДЗ и файл для нейросети — на странице урока'}})
L.append({'out': W + 'gfx/end.png', 'spec': {'type': 'end', 'num': NUM, 'topic': 'End-to-end SDLC', 'title': 'До встречи на следующем уроке',
          'text': 'Текстовая версия урока, ДЗ и файл для нейросети — на странице урока.'}})
G.update({'intro_mp4': 'gfx/intro.mp4', 'intro': 'gfx/end.png', 'hw': 'gfx/hw.png', 'end': 'gfx/end.png'})
json.dump(L, open(W + 'list.json', 'w'), ensure_ascii=False)
json.dump(G, open(W + 'gfx.json', 'w'), ensure_ascii=False, indent=1)
print(len(L), 'кадров;', len(G['cards']), 'плашек;', len(G['qside']), 'вопросов')
