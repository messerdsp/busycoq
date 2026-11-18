"""reset4.py IN OUT KEEPLAST: after the cascade is used up. Cut the whole tape at walls of >= 3 words; keep unit 1
(wall 40, phase changed only for alignment), drop every regular unit (gunit2.ok) except in the last KEEPLAST
segments, keep everything else (walls over 200 words shortened mod 12). Prints the kept segments' walls."""
import sys,re
from endlib import Wd, seg
from gunit2 import ok as unit_ok
fn,out,KL=sys.argv[1],sys.argv[2],int(sys.argv[3])
toks=open(fn).read().split(); head=toks[:2]; toks=toks[2:]
s='0'
for t in toks:
    b,_,e=t.partition('^'); e=int(e) if e else 1
    if e>200: e=200+e%12
    s+=b*e
s=s.rstrip('0')
assert s.startswith('011111111'+Wd), s[:30]
parts=re.split(r'((?:011101){3,})', s[9:])
segs=[(len(parts[u])//6, parts[u+1]) for u in range(1,len(parts),2)]
k1,b1=segs[0]
ph=[p for p in range(4) if b1.startswith(seg('U1',p))]; assert ph
keep=[]; dropped=0
for idx,(k,b) in enumerate(segs[1:],1):
    if idx<len(segs)-KL and unit_ok(8,b): dropped+=1; continue
    keep.append((k,b))
rest=''.join(Wd*k+b for k,b in keep)
for p in [ph[0]]+[q for q in range(4) if q!=ph[0]]:
    left='011111111'+Wd*40+seg('U1',p)+b1[len(seg('U1',ph[0])):]+rest
    if (len(left)-len(s))%6==0: break
else:
    left+='0'*((-(len(left)-1))%6)
cells_=left[1:]; cells_+='0'*((-len(cells_))%6)
rle=[]
for x in (cells_[j:j+6] for j in range(0,len(cells_),6)):
    if rle and rle[-1][0]==x: rle[-1][1]+=1
    else: rle.append([x,1])
open(out,'w').write(' '.join(head+[x+('^%d'%n if n>1 else '') for x,n in rle])+'\n')
print('segments',len(segs),'dropped',dropped,'kept walls',[k for k,_ in keep])
