# План графики урока 11 (19.11.2026, Практика работы с легаси проектами) — время исходника → list.json (render_list.js) + gfx.json (nation_base.py)
# Раскладка frame3: экран 1504×846 по центру по вертикали (NB_SY=117), колонка справа; камера лектора выключена весь урок → монограмма.
# Окна Zoom на демонстрации нет; нижней строки «Нэйшн · …» нет (просьба Антона 17.11: без дублей названий).
import json
W = '/home/claude/work/b1119/'
CH = json.load(open(W + 'chapters_src.json'))
LECT = 'Михаил Овчинников'; ORG = 'Staff-инженер, Google'
PHOTO = 'data:image/jpeg;base64,' + __import__('base64').b64encode(open(W + 'm.jpg', 'rb').read()).decode(); NUM = '11'; ROLE = 'dev'; TOP = 117
DUR = 8965.0; T0 = 963
PARTS = {'Вступление': 'Вступление', 'Часть 1. Ревьюеры спек и изолированные агенты': 'Часть 1 · Ревьюеры и worktree',
         'Часть 2. Дашборды и нагрузочный тест': 'Часть 2 · Дашборды и load-тест', 'Часть 3. Спека оптимизации и таски': 'Часть 3 · Спека и таски',
         'Часть 4. Код: воркеры, коммиты, ревью': 'Часть 4 · Код и воркеры', 'Часть 5. Ревью кода и ревьюеры кода': 'Часть 5 · Ревью кода', 'Итог и вопросы': 'Итог и вопросы'}
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
for cid, t, n, title, sub in [('part1', 1267, 1, 'Ревьюеры спек и изолированные агенты', 'Ревьюеры деталей, цели и факт-чекер; скилл new-worker и git worktree'),
                              ('part2', 1938, 2, 'Дашборды и нагрузочный тест', 'Дашборды на трёх уровнях, скилл Goal, load-тест и baseline старой архитектуры'),
                              ('part3', 3469, 3, 'Спека оптимизации и таски', 'Ревьюер тасков, поэтапная выкатка, полуручной конвейер из агентов'),
                              ('part4', 4557, 4, 'Код: воркеры, коммиты, ревью', 'Таски в одной ветке, ASD-STE100, Flash и тяжёлая модель'),
                              ('part5', 6292, 5, 'Ревью кода и ревьюеры кода', 'Final Reviewer, ревьюер тестов, readability, simplicity, overengineering protection')]:
    card(cid, t, 4.6, {'type': 'chapter', 'n': n, 'total': 5, 'title': title, 'sub': sub}, alpha=0, kind='chapter')
SIDE = [
 ('t_worktree', 1650, 'Термин', 'git worktree', 'Отдельное рабочее дерево: над этой папкой может работать отдельный агент. Для каждого агента формируется свой файл правил.'),
 ('t_goal', 2183, 'Термин', 'Скилл Goal', 'Когда агент пытается завершить работу, хук проверяет, достигнута ли цель. Если нет — агент продолжает.'),
 ('t_shadow', 4311, 'Термин', 'Shadow reconciliation', 'Проверка того, что в старом и в новом месте лежат правильные данные и что они на 99,99% сходятся.'),
 ('t_final', 6482, 'Термин', 'Final Reviewer', 'Делает триаж — классификацию найденных проблем: что из этого реальный дефект.'),
 ('t_overeng', 8031, 'Термин', 'Overengineering protection', 'Ревьюер, который ищет альтернативные способы решения задачи — с меньшим числом изменений.'),
]
QUO = [
 ('q_conveyor', 3945, 'Одни агенты пишут, другие ревьюят, третьи делают таски, четвёртые сейчас будут эти таски исполнять'),
 ('q_flash', 6071, 'Лучше запустить много раз, много параллельно моделей Flash, чтобы они перепроверяли'),
 ('q_reviewer', 8594, 'С каждой неудачной итерацией, когда агент выдаёт фигню, из такой неудачной итерации рождается следующий ревьюер'),
]
for cid, t, kind, term, text in SIDE: card(cid, t, 9, {'type': 'side', 'kind': kind, 'term': term, 'text': text})
for cid, t, text in QUO: card(cid, t, 8, {'type': 'side', 'kind': 'Цитата', 'text': text, 'who': LECT})
L.append({'out': W + 'gfx/hw.png', 'spec': {'type': 'hw', 'num': NUM, 'title': 'Домашнего задания к этому уроку нет',
          'text': 'Третий, завершающий урок по Mastodon — тоже с Михаилом: запустим созданный нагрузочный тест на новой архитектуре. Всё, что сделано на уроке, лектор выложит на GitHub в тот же репозиторий.',
          'items': ['Ревьюеры спек и скилл review', 'Изолированные агенты в git worktree', 'Ревьюеры кода и Final Reviewer'],
          'foot': 'Текстовая версия урока и файл для нейросети — на странице урока'}})
L.append({'out': W + 'gfx/end.png', 'spec': {'type': 'end', 'num': NUM, 'topic': 'Практика работы с легаси проектами', 'title': 'До встречи на следующем уроке',
          'text': 'Текстовая версия урока и файл для нейросети — на странице урока.'}})
L.append({'out': W + 'gfx/nsbox.png', 'alpha': 1, 'spec': {'type': 'speakerbox', 'top': TOP, 'photo': PHOTO, 'lector': LECT, 'org': ORG, 'role': ROLE, 'num': NUM, 'title': 'Практика работы с легаси проектами'}})
G['cards'].append({'id': 'nsbox', 'from': 0, 'to': 1281, 'png': 'gfx/nsbox.png', 'kind': 'overlay'})
G.update({'intro_mp4': 'gfx/intro.mp4', 'intro': 'gfx/end.png', 'hw': 'gfx/hw.png', 'end': 'gfx/end.png'})
json.dump(L, open(W + 'list.json', 'w'), ensure_ascii=False)
json.dump(G, open(W + 'gfx.json', 'w'), ensure_ascii=False, indent=1)
print(len(L), 'кадров;', len(G['cards']), 'плашек')
