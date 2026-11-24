import json,re
W=json.load(open('/home/claude/work/b1124/words.json')); W=W['words'] if isinstance(W,dict) else W
def norm(s): return re.sub(r'[^\wё-]','',s.lower())
def find(phrase, near, span=120):
    p=[norm(x) for x in phrase.split()]
    for i,w in enumerate(W):
        if abs(w['start']-near)>span: continue
        if all(i+k<len(W) and norm(W[i+k]['word'])==p[k] for k in range(len(p))): return i
    raise ValueError(f'not found: {phrase} @ {near}')
def seg(a_phrase, a_near, b_phrase, b_near):
    i=find(a_phrase,a_near); j=find(b_phrase,b_near)+len(b_phrase.split())-1
    return [W[i]['start'], W[j]['end'], i, j]
def show(a,b):
    ws=[w for w in W if a<=w['start']<=b]; out=[]; line=[]; t0=None
    for w in ws:
        if t0 is None: t0=w['start']
        line.append(w['word'])
        if w['word'][-1:] in '.?!': out.append(f'[{t0:.1f}] '+' '.join(line)); line=[]; t0=None
    if line: out.append(f'[{t0:.1f}] '+' '.join(line))
    print(f'==== {a}-{b}'); print('\n'.join(out))
