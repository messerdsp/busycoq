"""mkmin.py IN OUT NB [KEEP] [U1WALL]: from a round-start line (init26), keep the prefix and the first KEEP regular units
(default 1), drop the other regular units, keep the end word, NB band words, and the rest of the tape unchanged.
U1's phase is changed if needed so that the band stays 6-cell aligned."""
import sys
from endlib import *
fn,out,NB=sys.argv[1],sys.argv[2],int(sys.argv[3]); KEEP=int(sys.argv[4]) if len(sys.argv)>4 else 1
U1W=int(sys.argv[5]) if len(sys.argv)>5 else None
toks=open(fn).read().split(); head=toks[:2]; toks=toks[2:]
B=['010101','110101','011101','010111']
for ti in range(len(toks)):
    if toks[ti:ti+8]==B*2: break
tj=ti
while toks[tj:tj+4]==B: tj+=4
s='0'+cells_cap(toks[:ti],1000)   # head cell + left part (walls over 1000 words shortened, mod 12 kept)
assert s.startswith('011111111'+Wd)
us,i=parse_from(s,9,0)
print('units',[(t,p,k) for t,p,k in us])
E=s[i:]
# rebuild: prefix + kept units + E
def unitw(t,p,k): return Wd*k+seg(t,p)
kept=us[:KEEP]
if U1W: kept[0]=(kept[0][0],kept[0][1],U1W)
for ph in [kept[0][1]]+[p for p in range(4) if p!=kept[0][1]]:
    kept[0]=(kept[0][0],ph,kept[0][2])
    left='011111111'+''.join(unitw(*u) for u in kept)+E
    if (len(left)-len(s))%6==0: break
else: raise SystemExit('cannot align')
print('kept',kept,'E len',len(E))
cells=left[1:]   # drop head cell (blank, left of the line)
assert len(cells)%6==0
blk=[cells[j:j+6] for j in range(0,len(cells),6)]
rle=[]
for b in blk:
    if rle and rle[-1][0]==b: rle[-1][1]+=1
    else: rle.append([b,1])
line=head+[b+('^%d'%n if n>1 else '') for b,n in rle]+B*NB+toks[tj:]
open(out,'w').write(' '.join(line)+'\n')
