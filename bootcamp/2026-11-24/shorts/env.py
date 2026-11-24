import numpy as np
A=np.memmap('/home/claude/work/b1124/aud8k.raw',np.int16,'r'); SR=8000
def db(t,w=0.03):
    a=A[int((t-w/2)*SR):int((t+w/2)*SR)].astype(np.float32)/32768
    return 20*np.log10(np.sqrt((a*a).mean())+1e-6)
def prof(t,lo,hi,st=0.02): return [(round(x,2),round(db(x),1)) for x in np.arange(t+lo,t+hi,st)]
def snap(t,lo,hi):
    p=prof(t,lo,hi,0.01); return min(p,key=lambda x:x[1])
