#!/usr/bin/env python3
"""Факт-чек текстов графики против речи (решение Антона 06.11): то, что на экране, должно совпадать со сказанным.

gfx_factcheck.py extract <words.json> <outdir> [--lesson graphics_plan.json edl.json] [--shorts dir_with_specs_and_edls]
  → outdir/items.json — каждая «сцена» (живой слайд, сцена шортса, плашка) с текстами на экране, знаками ✓/✕, цветом
    (r — красный = негатив/ошибка, g — зелёный = хорошо/работает, a — акцент) и окном транскрипта вокруг (время исходника);
  → outdir/mech.json — механические проверки: цитаты дословно, цифры есть в речи рядом, текст не раньше слов;
  → outdir/batch_NN.md — пачки для независимых проверяющих (тот, кто делал графику, не проверяет).
gfx_factcheck.py report <outdir> → outdir/report.md из verdict_NN.json + mech.json. Код возврата 3, если есть
  «противоречит» или «не говорилось» — финальный рендер не запускать.
Вердикты: ok | contradicts (инверсия смысла: работает↔не работает, хорошо↔плохо) | not_said (домыслено) |
  distorted (другая цифра, усилено/ослаблено, мнение участника подано как слова лектора) | unclear.
"""
import sys, json, re, os, glob, bisect

def load_words(p):
    W = json.load(open(p)); return W['words'] if isinstance(W, dict) else W

def norm(s): return re.sub(r'[^\wё]+', ' ', s.lower().replace('ё', 'е')).strip()

def window(W, a, b):
    return ' '.join(f"[{int(w['start']) // 60}:{int(w['start']) % 60:02d}]{w['word']}" if k % 14 == 0 else w['word']
                    for k, w in enumerate(x for x in W if a <= x['start'] <= b))

def actor_lines(sc, to_src):
    """Тексты сцены stage/других видов в человекочитаемом виде с временем исходника."""
    L = []
    def add(at, kind, text, c=None, extra=''):
        if not text: return
        col = {'r': 'красный (плохо/ошибка)', 'g': 'зелёный (хорошо/работает)', 'a': 'акцент', 'ink': 'тёмный', 'w': 'нейтральный', 'm': 'серый'}.get(c or '', 'нейтральный')
        L.append(dict(src=round(to_src(at), 1), kind=kind, text=text, color=col, extra=extra))
    k = sc.get('kind')
    if k == 'stage':
        for a in sc['actors']:
            at = a.get('at', sc['at']); kk = a.get('k', 'ic')
            if kk == 'mk': add(at, 'знак', '✓' if a.get('c') == 'ok' else '✕', 'g' if a.get('c') == 'ok' else 'r', 'значок рядом с ближайшей карточкой')
            elif kk in ('ln', 'dt', 'ring'): continue
            else:
                add(at, {'ic': 'иконка с подписью', 'tx': 'крупный текст', 'pill': 'плашка', 'card': 'карточка', 'fr': 'рамка'}.get(kk, kk),
                    ' — '.join(x for x in [a.get('t'), a.get('s')] if x), a.get('c'))
                for f in a.get('kf', []):
                    if f.get('c'): add(f['at'], 'смена цвета', a.get('t'), f['c'], 'элемент перекрашивается')
    elif k == 'kinetic':
        for l in sc['lines']: add(l.get('at', sc['at']), 'крупный текст', l['t'], 'a' if l.get('hl') else None, ('зачёркнуто: ' + ','.join(l['stk'])) if l.get('stk') else '')
        if sc.get('sub'): add(sc['sub']['at'], 'подпись', sc['sub']['t'])
    elif k == 'steps':
        if sc.get('hd'): add(sc['at'], 'заголовок списка', sc['hd'])
        for it in sc['items']: add(it['at'], 'пункт списка', it['t'] + {'x': '  ✕', 'ok': '  ✓'}.get(it.get('mark'), ''), {'x': 'r', 'ok': 'g'}.get(it.get('mark')))
    elif k == 'chat':
        for m in sc['msgs']: add(m['at'], 'реплика ' + m['who'], m['t'], None, 'зачёркнуто' if m.get('stkAt') else '')
    elif k in ('nodes', 'vector', 'rank'):
        for n in sc.get('nodes', []) + sc.get('pts', []): add(n.get('at', sc['at']), 'узел', n.get('t'), n.get('cls'))
        for g in sc.get('tags', []): add(g['at'], 'метка', g['t'], g.get('cls'))
        for l in sc.get('labels', []): add(l['at'], 'подпись', l['t'])
        if sc.get('wrap'): add(sc['wrap']['at'], 'рамка', sc['wrap']['t'])
        if sc.get('items'): add(sc['at'], 'список', ', '.join(sc['items']))
        if sc.get('cut'): add(sc['cut']['at'], 'черта', sc['cut']['t'], 'r')
    return L

def extract(words_p, out, lesson=None, shorts=None):
    W = load_words(words_p); os.makedirs(out, exist_ok=True); items = []
    if lesson:
        plan = json.load(open(lesson[0]))
        for bd in plan.get('boards', []):
            sc = sorted(bd['scenes'], key=lambda s: s['at'])
            for i, s in enumerate(sc):
                end = sc[i + 1]['at'] if i + 1 < len(sc) else bd['b']
                lines = actor_lines(s, lambda t: t)
                if lines: items.append(dict(id=f"{bd['id']}#{i + 1}", where=f"урок · живой слайд «{bd['label']}», сцена {i + 1}",
                                            a=s['at'], b=end, lines=lines))
        for i, it in enumerate(plan['items']):
            txt = {'term': lambda x: f"{x['word']} — {x['def']}", 'quote': lambda x: f"«{x['text'].replace('*', '')}» — {x['author']}",
                   'question': lambda x: f"Вопрос {x['src']}: {x['q']}", 'stat': lambda x: f"{x['label']}: {x['big']}"}[it['type']](it)
            items.append(dict(id=f"{it['type']}{i:02d}", where=f"урок · плашка {it['type']}", a=it['t'], b=it['t'] + 8,
                              lines=[dict(src=it['t'], kind=it['type'], text=txt, color='нейтральный', extra='цитата — должна быть дословной' if it['type'] == 'quote' else '')]))
    if shorts:
        for sp in sorted(glob.glob(os.path.join(shorts, '*.spec.json'))):
            S = json.load(open(sp)); E = json.load(open(sp.replace('.spec.json', '.edl.json')))['edl']
            recs = [e['rec'] for e in E]
            def to_src(t, E=E, recs=recs):
                i = max(0, bisect.bisect_right(recs, t) - 1); e = E[i]
                return e['src_in'] + (t - e['rec']) * e.get('speed', 1.0)
            sid = os.path.basename(sp)[:-10]
            items.append(dict(id=f'{sid}#title', where=f'шортс {sid} · заголовок', a=to_src(0), b=to_src(S['dur'] - S.get('tail', 0) - .1),
                              lines=[dict(src=round(to_src(0), 1), kind='заголовок шортса', text=re.sub('<[^>]+>', '', S['title']), color='нейтральный', extra='проверить по всему ролику')]))
            sc = sorted(S.get('scenes', []), key=lambda s: s['at'])
            for i, s in enumerate(sc):
                end = sc[i + 1]['at'] if i + 1 < len(sc) else S['dur'] - S.get('tail', 0) - .1
                lines = actor_lines(s, to_src)
                if lines: items.append(dict(id=f'{sid}#{i + 1}', where=f'шортс {sid}, сцена {i + 1}', a=to_src(s['at']), b=to_src(end), lines=lines))
    for it in items:
        if it['where'].startswith('шортс') and it['id'].endswith('#title'):
            it['speech'] = window(W, it['a'] - 1, it['b'] + 1)
        else:
            it['speech'] = window(W, it['a'] - 20, it['b'] + 10)
    json.dump(items, open(os.path.join(out, 'items.json'), 'w'), ensure_ascii=False, indent=1)
    # --- механика ---
    mech = []
    for it in items:
        sp = norm(' '.join(w['word'] for w in W if it['a'] - 25 <= w['start'] <= it['b'] + 12))
        for l in it['lines']:
            t = l['text']
            for q in re.findall(r'«([^»]{6,})»', t) + ([re.sub(r'^«|» — .*$', '', t)] if l['kind'] == 'quote' else []):
                qn = norm(q); toks = qn.split()
                hit = sum(1 for x in toks if x[:5] in sp) / max(1, len(toks))
                if hit < .75: mech.append(dict(id=it['id'], type='цитата не дословно', text=q, score=round(hit, 2)))
            for n in re.findall(r'\d+(?:[.,]\d+)?', t.replace(' ', '')):
                digits = n.replace(',', '.')
                spoken = {'1': 'один', '2': 'два', '3': 'три', '4': 'четыр', '5': 'пят', '8': 'восем', '10': 'десят', '15': 'пятнадц', '100': 'сто', '80': 'восемьдесят', '20': 'двадцат'}.get(digits, '§')
                if digits not in sp.replace(' ', '') and spoken not in sp and not re.match(r'^(1|2|3|4)$', digits):
                    mech.append(dict(id=it['id'], type='цифры нет в речи рядом', text=t, num=n))
            # не раньше слов: ключевое слово текста впервые прозвучало после появления
            keys = [x for x in norm(t).split() if len(x) >= 6]
            firsts = [min(ts) for k in keys if (ts := [w['start'] for w in W if it['a'] - 25 <= w['start'] <= it['b'] + 12 and norm(w['word']).startswith(k[:6])])]
            if len(firsts) >= 2 and min(firsts) > l['src'] + 6 and l['kind'] not in ('заголовок шортса', 'рамка'):
                mech.append(dict(id=it['id'], type='появляется раньше, чем сказано', text=t, shown=l['src'], said=round(min(firsts), 1)))
    json.dump(mech, open(os.path.join(out, 'mech.json'), 'w'), ensure_ascii=False, indent=1)
    # --- пачки для проверяющих ---
    n = 0; B = []
    def flush():
        nonlocal n, B
        if not B: return
        md = ['# Пачка на проверку', '']
        for it in B:
            md += [f"## {it['id']} — {it['where']}", '', 'На экране:']
            md += [f"- [{int(l['src']) // 60}:{int(l['src']) % 60:02d}] {l['kind']}, {l['color']}: «{l['text']}»" + (f" ({l['extra']})" if l['extra'] else '') for l in it['lines']]
            md += ['', 'Речь (транскрипт Whisper, время исходника):', '', '> ' + it['speech'], '']
        open(os.path.join(out, f'batch_{n:02d}.md'), 'w').write('\n'.join(md)); n += 1; B = []
    size = 0
    for it in items:
        B.append(it); size += len(it['speech'])
        if size > 26000: flush(); size = 0
    flush()
    print(f'{len(items)} сцен/плашек, {sum(len(i["lines"]) for i in items)} текстов, механика: {len(mech)} замечаний, пачек: {n}')

def report(out):
    items = {i['id']: i for i in json.load(open(os.path.join(out, 'items.json')))}
    V = []
    for f in sorted(glob.glob(os.path.join(out, 'verdict_*.json'))): V += json.load(open(f))
    mech = json.load(open(os.path.join(out, 'mech.json')))
    bad = [v for v in V if v['verdict'] in ('contradicts', 'not_said')]
    mid = [v for v in V if v['verdict'] in ('distorted', 'unclear')]
    name = {'contradicts': 'ПРОТИВОРЕЧИТ', 'not_said': 'НЕ ГОВОРИЛОСЬ', 'distorted': 'искажено', 'unclear': 'неясно'}
    L = ['# Факт-чек графики', '', f"Проверено текстов: {len(V)} · ок: {sum(v['verdict'] == 'ok' for v in V)} · "
         f"противоречит: {sum(v['verdict'] == 'contradicts' for v in V)} · не говорилось: {sum(v['verdict'] == 'not_said' for v in V)} · "
         f"искажено: {sum(v['verdict'] == 'distorted' for v in V)} · неясно: {sum(v['verdict'] == 'unclear' for v in V)} · механика: {len(mech)}", '']
    for title, arr in [('## Исправить обязательно', bad), ('## Посмотреть', mid)]:
        L += [title, '']
        for v in arr:
            it = items.get(v['id'], {})
            L += [f"- **{name[v['verdict']]}** · {it.get('where', v['id'])} · «{v['text']}»", f"  - лектор: «{v.get('evidence', '')}»", f"  - {v.get('note', '')}" + (f" → предлагаю: «{v['fix']}»" if v.get('fix') else '')]
        L.append('')
    L += ['## Механика', ''] + [f"- {m['type']} · {items.get(m['id'], {}).get('where', m['id'])} · «{m['text']}»" for m in mech]
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(L) + '\n')
    print(L[2]); sys.exit(3 if bad else 0)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'extract':
        lesson = a[a.index('--lesson') + 1:a.index('--lesson') + 3] if '--lesson' in a else None
        shorts = a[a.index('--shorts') + 1] if '--shorts' in a else None
        extract(a[1], a[2], lesson, shorts)
    elif a[0] == 'report': report(a[1])
    else: sys.exit(__doc__)
