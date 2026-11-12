import json, re, sys, subprocess
sys.path.insert(0, '/home/claude/work/b1112'); from wtools import W
PL = {p['id']: p for p in json.load(open('planf.json'))}
TITLES = {'s01_utopiya': 'Модель всё сделает <b>за меня</b>?',
 's02_plan_drugie_agenty': 'Кто должен <b>менять план</b> агента?',
 's03_prava_ne_promptom': 'Как запретить агенту <b>лишнее</b>?',
 's04_reestr_navykov': 'Что делать, если в компании <b>куча MCP</b>?',
 's05_svoy_setevoy_stek': 'Что агент делает, когда <b>забыл задачу</b>?',
 's06_skill_cherez_mcp': 'Как доставить <b>новую версию скилла</b>?',
 's07_escape_vmesto_kompakta': 'Что лучше, чем <b>компакт</b>?',
 's08_bez_testov_rukami': 'Как проверять работу агента <b>без тестов</b>?',
 's09_tri_popytki': 'Что делать агенту <b>после ошибки</b>?',
 's10_kakoy_inzhener_nuzhen': 'Какой разработчик <b>будет нужен</b>?'}
C = [dict(c, edl=c['id'] + '.edl.json', title=TITLES[c['id']]) for c in json.load(open('../reels_config.json')) if c['id'] in PL]
for c in C: c['replace'] = c['replace'] + [['селя,', 'shell,'], ['P', 'Pi'], ['code', 'code'], ['МСП', 'MCP']]
json.dump(C, open('cfg.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['python3', '/home/claude/news_generator/pipeline/reels.py', 'cfg.json', '../words.json'], check=True, capture_output=True)
for sid, p in PL.items():
    E = json.load(open(sid + '.edl.json'))['edl']; s = json.load(open(sid + '.spec.json')); h = p['hook']; ws = []
    for n_, e in enumerate(E):
        sp_ = p['idx'][:1] if n_ < h else p['idx'][h:]
        ks = max(([k for k in range(i, j + 1) if e['src_in'] - 0.1 <= W[k]['start'] < e['src_out'] - 0.05] for i, j in sp_), key=len)
        for k in ks: ws.append({'t': W[k]['word'], 's': round(e['rec'] + max(0, W[k]['start'] - e['src_in']), 2), 'e': round(e['rec'] + min(W[k]['end'], e['src_out']) - e['src_in'], 2)})
    rep = dict(map(tuple, next(c for c in C if c['id'] == sid)['replace']))
    for w in ws: w['t'] = rep.get(w['t'], w['t'])
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
    s.update(dir='Разработка', tag='Harness', lector='Николай Барышников', org='ex-Yandex Cloud')
    s['hookEnd'] = round(E[h - 1]['rec'] + E[h - 1]['src_out'] - E[h - 1]['src_in'], 2) if h else 0
    json.dump(s, open(sid + '.spec.json', 'w'), ensure_ascii=False, indent=1)
    print('##', sid, dur, 'hook', s['hookEnd']); print(' '.join(f"[{c['s']:.1f}]" + ' '.join(w['t'] for w in c['words']) for c in s['chunks']))
