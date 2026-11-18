"""construct.py PRE OUT SCALE: realistic chain in front of the end region of PRE (a round-start line).
Keeps unit 1's segment (static piece after its head kept, head set to the carrying phase, wall from init26 / SCALE),
the next segment (the transparent 3-word one), then init26's units U2..D in the carrying phase with init26's walls
/ SCALE, then the last segment of PRE (the end region) and blank tape."""
import sys,re
from endlib import Wd, seg
pre,out,SC=sys.argv[1],sys.argv[2],int(sys.argv[3])
def cells(fn):
    toks=open(fn).read().split(); h=toks[:2]; s='0'
    for t in toks[2:]:
        b,_,e=t.partition('^'); e=int(e) if e else 1; s+=b*e
    return h,s.rstrip('0')
h,s=cells(pre)
parts=re.split(r'((?:011101){3,})', s[9:])
segs=[(len(parts[u])//6, parts[u+1]) for u in range(1,len(parts),2)]
k1,b1=segs[0]; p1=[p for p in range(4) if b1.startswith(seg('U1',p))][0]
junk=b1[len(seg('U1',p1)):]
walls=[1880776,470195,117544,29380,7326,1823,455,106]
types=['U1','U2','U3','U4','K','D','K','D']
w=[max(3,x//SC) for x in walls]
t='011111111'+Wd*w[0]+seg('U1',3)+junk
t+=Wd*segs[1][0]+segs[1][1]
for ty,ww in zip(types[1:],w[1:]): t+=Wd*ww+seg(ty,3)
t+=Wd*segs[-1][0]+segs[-1][1]
c=t[1:]; c+='0'*((-len(c))%6)
rle=[]
for x in (c[j:j+6] for j in range(0,len(c),6)):
    if rle and rle[-1][0]==x: rle[-1][1]+=1
    else: rle.append([x,1])
open(out,'w').write(' '.join([h[0],'C']+[x+('^%d'%n if n>1 else '') for x,n in rle])+'\n')
print('walls',w,'end wall',segs[-1][0])
