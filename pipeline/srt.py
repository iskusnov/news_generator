import json
E=json.load(open('edl.json')); W=json.load(open('/home/claude/pod/words.json'))['words']
items=[]
for e in E['edl']:
    for w in W:
        if e['src_in']<=w['start']<e['src_out']:
            items.append((e['rec']+w['start']-e['src_in'], e['rec']+min(w['end'],e['src_out'])-e['src_in'], w['word']))
items.sort()
def ts(t): t=max(t,0); ms=int(round(t*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
cues=[];cur=[]
for it in items:
    if cur and (len(cur)>=7 or it[0]-cur[-1][1]>0.6 or it[1]-cur[0][0]>3.2 or cur[-1][2][-1] in '.?!'): cues.append(cur); cur=[]
    cur.append(it)
cues.append(cur)
out=[]
for i,c in enumerate(cues,1):
    end=min(c[-1][1]+0.3, cues[i][0][0] if i<len(cues) else c[-1][1]+0.3)
    txt=' '.join(x[2] for x in c)
    if i==1 and txt.startswith('этом'): txt='При '+txt
    out.append(f"{i}\n{ts(c[0][0])} --> {ts(end)}\n{txt}\n")
open('podcast_2026-11-02.srt','w').write('\n'.join(out)); print(len(cues))
