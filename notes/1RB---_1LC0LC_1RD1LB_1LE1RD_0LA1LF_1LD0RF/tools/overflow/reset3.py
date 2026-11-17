"""reset2.py IN OUT NBMOD NBMIN MINB FW1 [U1WALL]   (FW1: length of the first frozen wall, +-20; nothing from it on is touched)
Round-start tape line -> shorter equivalent for the end region: cut the part left of the first band at every wall of
>= 3 words; drop every segment that is a validated regular unit (gunit2.ok), except unit 1 (wall set to
U1WALL, phase changed if needed for 6-cell alignment) and the last segment before the band; keep all other segments.
The first band is shortened to the least length >= NBMIN congruent to its length mod NBMOD.
Exit 3 (nothing written) if the first band has fewer than MINB words."""
import sys,re
from endlib import Wd, seg
from gunit2 import ok as unit_ok
fn,out,NBMOD,NBMIN,MINB=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
FW1=int(sys.argv[6]); U1W=int(sys.argv[7]) if len(sys.argv)>7 else 40
toks=open(fn).read().split(); head=toks[:2]; toks=toks[2:]
B=['010101','110101','011101','010111']
def cnt(t):
    b,_,e=t.partition('^'); return int(e) if e else 1
if FW1>0: fz=next(i for i in range(len(toks)) if abs(cnt(toks[i])-FW1)<=20)
else:   # no frozen wall: the boundary is the first band of >= 5 words (any rotation), which is kept as it is
    ROT0=[B[r:]+B[:r] for r in range(4)]
    fz=next(i for i in range(len(toks)) if any(toks[i:i+20]==R*5 for R in ROT0))
    NBMOD=10**9
ti=None
ROT=[B[r:]+B[:r] for r in range(4)]
k=fz-1
def isband(k): return k>=7 and any(toks[k-7:k+1]==R*2 for R in ROT)
while k>=0 and not isband(k) and fz-k<200: k-=1
if FW1>0 and isband(k):
    ti=k-7
    while ti>=4 and toks[ti-4:ti]==toks[ti:ti+4]: ti-=4
    BB=toks[ti:ti+4]
noband = ti is None
if noband:
    ti=max(fz-15,1)   # stop 15 runs before the first frozen wall; the last 3 segments before it are kept
tj=ti
if not noband:
    while toks[tj:tj+4]==BB: tj+=4
nb=(tj-ti)//4
if not noband and nb<MINB: print('band',nb,'words: no reset'); sys.exit(3)
s='0'
for t in toks[:ti]:
    b,_,e=t.partition('^'); e=int(e) if e else 1
    if e>200: e=200+e%12
    s+=b*e
assert s.startswith('011111111'+Wd), s[:30]
body=s[9:]
parts=re.split(r'((?:011101){3,})', body)
assert parts[0]=='', parts[0][:40]
segs=[(len(parts[u])//6, parts[u+1]) for u in range(1,len(parts),2)]
def isunit(b): return unit_ok(8,b)
k1,b1=segs[0]
ph=[p for p in range(4) if b1.startswith(seg('U1',p))]
assert ph, 'no U1'
keep=[]; dropped=0
for idx,(k,b) in enumerate(segs[1:],1):
    if idx<len(segs)-(3 if noband else 1) and isunit(b): dropped+=1; continue
    keep.append((k,b))
rest=''.join(Wd*k+b for k,b in keep)
for p in [ph[0]]+[q for q in range(4) if q!=ph[0]]:
    left='011111111'+Wd*U1W+seg('U1',p)+b1[len(seg('U1',ph[0])):]+rest
    if (len(left)-len(s))%6==0: break
else: raise SystemExit('cannot align')
cells_=left[1:]
rle=[]
for x in (cells_[j:j+6] for j in range(0,len(cells_),6)):
    if rle and rle[-1][0]==x: rle[-1][1]+=1
    else: rle.append([x,1])
nbn=nb
if nb>NBMIN+NBMOD:
    nbn=nb%NBMOD
    while nbn<NBMIN: nbn+=NBMOD
open(out,'w').write(' '.join(head+[x+('^%d'%n if n>1 else '') for x,n in rle]+(BB*nbn if not noband else [])+toks[tj:])+'\n')
print('NOBAND' if noband else '', 'segments',len(segs),'dropped',dropped,'kept',len(keep),'| kept walls',[k for k,_ in keep],'| U1 phase',p,'| band',nb,'->',nbn)
