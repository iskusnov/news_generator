# Субтитры v2: слова только из запланированных фраз, с допуском на границе куска (Whisper сдвигает тайминги на мс)
import json, re, sys
sys.path.insert(0,'/home/claude/work/b1110'); from wtools import W, seg
exec(open('../plan2.py').read().split('HOOK=')[0].split('from wtools import *')[1])  # P
C={c['id']:c for c in json.load(open('cfg.json'))}
for sid, segs in P.items():
    spans=[seg(a,an,b,bn)[2:] for a,an,b,bn in segs]
    E=json.load(open(sid+'.edl.json'))['edl']; s=json.load(open(sid+'.spec.json'))
    ws=[]
    for e in E:
        ks=max(([k for k in range(i,j+1) if e['src_in']-0.1 <= W[k]['start'] < e['src_out']-0.05] for i,j in spans),key=len)
        for k in ks:
            w=W[k]; ws.append({'t':w['word'],'s':round(e['rec']+max(0,w['start']-e['src_in']),2),'e':round(e['rec']+min(w['end'],e['src_out'])-e['src_in'],2)})
    rep=dict(map(tuple,C[sid]['replace'])); rep['Чтобы']='чтобы'
    for w in ws: w['t']=rep.get(w['t'],w['t'])
    ch,cur=[],[]
    for w in ws:
        if cur and (len(cur)>=3 or w['s']-cur[-1]['e']>0.4 or re.search(r'[.?!,]$',cur[-1]['t']) or sum(len(x['t']) for x in cur)+len(w['t'])>16):
            ch.append(cur); cur=[]
        cur.append(w)
    if cur: ch.append(cur)
    dur=s['dur']; endDur=s['endDur']; out=[]
    for n,c in enumerate(ch):
        e=min(ch[n+1][0]['s'] if n+1<len(ch) else dur, c[-1]['e']+0.5)
        if c[0]['s']<dur-endDur: out.append({'s':c[0]['s'],'e':round(min(e,dur-endDur),2),'words':[{'t':x['t'],'s':x['s']} for x in c]})
    s['chunks']=out; json.dump(s,open(sid+'.spec.json','w'),ensure_ascii=False,indent=1)
    print(sid,': ',' '.join(w['t'] for c in out for w in c['words']))
