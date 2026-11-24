# Субтитры и база спек шортсов урока 12 (24.11): reels.py → слова только из запланированных фраз (SHORTS.md шаг 4).
import json, re, sys, subprocess
sys.path.insert(0, '/home/claude/work/b1124'); from wtools import W
PL = {p['id']: p for p in json.load(open('planf.json'))}
TITLES = {
 's01_chetyre_dollara': 'Сколько стоит задача, которую <b>сделал ИИ</b>?',
 's02_odna_iz_sta': 'Зачем человек, если <b>все тесты прошли</b>?',
 's03_gitlab_bot': 'Как ИИ-разработчик берёт <b>задачу из GitLab</b>?',
 's04_eto_ne_zadacha': 'Что делать, если задача — <b>это вопрос</b>?',
 's05_spec_pri_ustanovke': 'Как сэкономить токены <b>в десятки раз</b>?',
 's06_logika_chelovecheskim': 'Чего не хватило агенту, чтобы <b>понять логику</b>?',
 's07_pervyi_prompt': 'Что написать агенту <b>в первом промпте</b>?',
 's08_otvetstvennost': 'Кто отвечает, если <b>ИИ сломает прод</b>?',
 's09_openhands': 'Почему не зашёл <b>OpenHands</b>?',
 's10_bezopasnost': 'Что ревьюер обязан <b>проверять всегда</b>?',
 's11_vosem_chasov': 'Сколько часов ушло на <b>код фреймворка</b>?',
 's12_chelovek_ili_ii': 'Чем живой разработчик <b>лучше модели</b>?',
 's13_testy_v_otryve': 'Тесты агенту — <b>до кода или после</b>?'}
REP = [['прот', 'прод'], ['прот.', 'прод.'], ['прот,', 'прод,'], ['IE,', 'ИИ,'], ['IE', 'ИИ'], ['n2n', 'end-to-end'], ['Клоду', 'Claude'],
       ['иишкой', 'ИИшкой'], ['иишки', 'ИИшки'], ['E-моделью', 'ИИ-моделью'], ['ЭДЕшке', 'IDE'], ['api', 'API'], ['review', 'ревью'],
       ['reviewer', 'ревьюер'], ['СВГ', 'SVG'], ['СВГшку,', 'SVG-шку,'], ['элефан-то', 'элефанта'], ['ЕТИ,', 'e2e,'], ['Ентуэнт', 'end-to-end'],
       ['промте', 'промпте'], ['Black', 'black'], ['Box', 'box'], ['Box,', 'box,'], ['Box.', 'box.'], ['endpoint', 'endpoint\'а'], ['ИМ-моделью', 'ИИ-моделью'],
       ['гите', 'Git'], ['OpenHands', 'OpenHands'], ['pull-request', 'pull request'], ['виш-листу,', 'вишлисту,'], ['пыхать.', '…']]
WHO = {'s12_chelovek_ili_ii': [(805.0, 812.0, 'Марат Хасанов', 'участник'), (884.0, 914.0, 'Владимир Савостин', 'участник')],
       's13_testy_v_otryve': [(2882.0, 2902.0, 'Виталий Кузнецов', 'участник')]}
SEQ = {'s12_chelovek_ili_ii': [('это было по понятию,', 'это было понятно,'), ('модель И этого нет,', 'у модели этого нет,'), ('То есть...', '')],
       's10_bezopasnost': [('ревьюер и надо', 'В ревьюере надо'), ('все здесь для хорошего замечания массово ломают на поэтому', 'все массово ломают. Поэтому'),
                           ('удавались.', 'удавались.')],
       's13_testy_v_otryve': [('выполнен,', 'выполнит,'), ('агенты e2e, end-to-end или', 'агенты, end-to-end или')],
       's07_pervyi_prompt': [('но я здесь', 'Но я здесь'), ('не продумывает диаграммы ты', 'не продумывай диаграммы, ты'), ('подключать', 'подключать.')],
       's03_gitlab_bot': [('исполнителем ставится', 'Исполнителем ставится'), ('выполнить ее выложить', 'Выполнить её, выложить')],
       's02_odna_iz_sta': [('вторая точка', 'Вторая точка')],
       's09_openhands': [('точнее, в прошлом', 'В прошлом'), ('но удивительным', 'Но удивительным')],
       's11_vosem_chasov': [('вместе с прогонами.', 'вместе с прогонами.')],
       's05_spec_pri_ustanovke': [('они парсили весь', 'а не парсили весь')],
       's06_logika_chelovecheskim': [('документация копии', 'документация API')],
       's08_otvetstvennost': [('ревьювер', 'ревьюер')]}
C = [{'id': i, 'edl': i + '.edl.json', 'title': t, 'endline': '', 'endDur': 1.8, 'tail': 1.8, 'replace': REP} for i, t in TITLES.items() if i in PL]
json.dump(C, open('cfg.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['python3', '/home/claude/news_generator/pipeline/reels.py', 'cfg.json', '../words.json'], check=True, capture_output=True)
for sid, p in PL.items():
    D = json.load(open(sid + '.edl.json')); E = D['edl']; s = json.load(open(sid + '.spec.json')); h = p['hook']; ws = []
    h = sum(1 for e in E if e.get('tag') == 'hook')  # хук по факту edl (cut.py мог разбить фразу)
    # студент без камеры — в окне камеры экран (флаг scr в edl для vertical_render.py)
    for e in E:
        e.pop('scr', None)
        for (a, b), fl in zip(p['segs'], p['flags']):
            if 'scr' in fl and a - 0.2 <= e['src_in'] < b: e['scr'] = 1
    json.dump(D, open(sid + '.edl.json', 'w'), indent=1)
    for n_, e in enumerate(E):
        sp_ = p['idx'][:1] if n_ < h else p['idx'][1:]
        ks = max(([k for k in range(i, j + 1) if e['src_in'] - 0.1 <= W[k]['start'] < e['src_out'] - 0.05] for i, j in sp_), key=len)
        for k in ks: ws.append({'t': W[k]['word'], 's': round(e['rec'] + max(0, W[k]['start'] - e['src_in']), 2), 'e': round(e['rec'] + min(W[k]['end'], e['src_out']) - e['src_in'], 2)})
    rep = dict(map(tuple, REP))
    for w in ws: w['t'] = rep.get(w['t'], w['t'])
    for a, b in SEQ.get(sid, []):  # правки фраз распознавания (несколько слов → текст из чистовика); время — первого слова
        a = a.split(); i = 0
        while i <= len(ws) - len(a):
            if [w['t'] for w in ws[i:i + len(a)]] == a:
                bb = b.split() if b else []
                new = [dict(ws[i + min(k, len(a) - 1)], t=t) for k, t in enumerate(bb)]
                ws[i:i + len(a)] = new; i += max(1, len(new))
            else: i += 1
    ws[0]['t'] = ws[0]['t'][:1].upper() + ws[0]['t'][1:]
    ch, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or w['s'] - cur[-1]['e'] > 0.4 or re.search(r'[.?!,]$', cur[-1]['t']) or sum(len(x['t']) for x in cur) + len(w['t']) > 16): ch.append(cur); cur = []
        cur.append(w)
    if cur: ch.append(cur)
    dur, endDur = s['dur'], s['endDur']; s['chunks'] = []
    for n, c in enumerate(ch):
        en = min(ch[n + 1][0]['s'] if n + 1 < len(ch) else dur, c[-1]['e'] + 0.5)
        if c[0]['s'] < dur - endDur: s['chunks'].append({'s': c[0]['s'], 'e': round(min(en, dur - endDur), 2), 'words': [{'t': x['t'], 's': x['s']} for x in c]})
    s.update(dir='Разработка', tag='SDLC', lector='Даниил Пилипенко', org='SymbioWay')
    # подпись в окне камеры: на кусках студента — его имя (время ролика)
    nm = []
    for a, b, who, org in WHO.get(sid, []):
        for e in E:
            if a <= e['src_in'] < b: nm.append({'s': e['rec'], 'e': round(e['rec'] + e['src_out'] - e['src_in'], 2), 't': who, 'org': org})
    if nm: s['names'] = nm
    s['hookEnd'] = round(E[h - 1]['rec'] + E[h - 1]['src_out'] - E[h - 1]['src_in'], 2) if h else 0
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1)
    print('##', sid, dur, 'hook', s['hookEnd'], 'scr', sum(1 for e in E if e.get('scr'))); print(' '.join(f"[{c['s']:.1f}]" + ' '.join(w['t'] for w in c['words']) for c in s['chunks']))
