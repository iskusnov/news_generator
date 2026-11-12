import json
def fix(sid, f):
    E=json.load(open(sid+'.edl.json')); L=E['edl']; L=f(L); r=0.0
    for e in L: e['rec']=round(r,2); r+=e['src_out']-e['src_in']
    E['edl']=L; E['total']=round(r,2); json.dump(E,open(sid+'.edl.json','w'),indent=1); print(sid,E['total'],[(e['src_in'],e['src_out'],e.get('cam_ss')) for e in L])
def s02(L):
    for e in L:
        if abs(e['src_out']-1600.32)<.02: e['src_out']=1600.22
        if abs(e['src_in']-1600.32)<.02: e['src_in']=1600.22
    return L
def s07(L):
    for e in L:
        if abs(e['src_out']-5527.6)<.02: e['src_out']=5527.30
    return L
def s08(L):
    o=[]
    for e in L:
        if abs(e['src_in']-7174.28)<.02:   # 7172.5–7175.4: Zoom показал карточку участника — камеру берём на 1.35 с позже
            a=dict(e,src_out=7175.59,cam_ss=1.35); b=dict(e,src_in=7175.59); o+= [a,b]
        else: o.append(e)
    return o
fix('s02_plan_bomba',s02); fix('s07_proverki_v_promptah',s07); fix('s08_500_agentov',s08)
