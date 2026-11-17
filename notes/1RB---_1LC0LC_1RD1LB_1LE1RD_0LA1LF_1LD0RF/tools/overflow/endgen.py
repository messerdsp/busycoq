"""endgen.py LINE NB FWCAP VISITS : isolated end-region visits from a round-start line (unit 1 = left neighbour).
E = everything right of unit 1's head up to the first band; after every visit, segments of E (cut at walls of >= 3
words) that validate as regular units (gunit2.ok) are removed, except the last one. Logs end-word repeats with the
band edge and the frozen part (drift test)."""
import sys,re
from endlib import Wd, seg, TR, BAND, cells_cap, trip
from gunit2 import ok as unit_ok
fn=sys.argv[1]; NB=int(sys.argv[2]); FWC=int(sys.argv[3]); N=int(sys.argv[4])
toks=open(fn).read().split()[2:]
B=['010101','110101','011101','010111']
ti=next(i for i in range(len(toks)) if toks[i:i+8]==B*2)
tj=ti
while toks[tj:tj+4]==B: tj+=4
s='0'+cells_cap(toks[:ti],200)
j=9; 
while s.startswith(Wd,j): j+=6
ph=[p for p in range(4) if s.startswith(seg('U1',p),j)]
E=s[j+len(seg('U1',ph[0])):]
F=cells_cap(toks[tj:tj+60],FWC)
T=E+BAND*NB+F; R=len(F)
def bandsplit(T):
    b=T.find(BAND*2); j=b
    while T.startswith(BAND,j): j+=24
    return b,(j-b)//24
def peel(E):
    parts=re.split(r'((?:011101){3,})', E)
    out=parts[0]; dropped=0; segs=[(parts[u],parts[u+1]) for u in range(1,len(parts),2)]
    for idx,(w,b) in enumerate(segs):
        if idx<len(segs)-1 and unit_ok(8,b): dropped+=1; continue
        out+=w+b
    return out,dropped
seen={}; ndrop=0
for v in range(N):
    b,nb=bandsplit(T)
    Ecur=T[:b]; key=Ecur
    tail=T[b+24*nb:]
    if key in seen:
        v0,nb0,d0,tail0,dist0=seen[key]
        print('visit',v,'end word = visit',v0,'| band words',nb0,'->',nb,'| band left edge to right end',dist0,'->',len(T)-b,
              '| units dropped',d0,'->',ndrop,'| right of band same:',tail0==tail); sys.stdout.flush()
    else: seen[key]=(v,nb,ndrop,tail,len(T)-b)
    r=trip(T)
    if r[0]!='ok': print('visit',v,r[:2]); break
    T=r[1]
    if r[2]>b+24*nb: print('  visit',v,'crossing'); sys.stdout.flush()
    b2,_=bandsplit(T); E2,d=peel(T[:b2]); ndrop+=d; T=E2+T[b2:]
    if v%200==0: print('  visit',v,'E',len(E2),'band',bandsplit(T)[1],'dropped',ndrop); sys.stdout.flush()
