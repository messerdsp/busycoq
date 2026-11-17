"""generic regular unit: a segment Wd^k + body (k >= 3) whose trips in the unit interface (enter in D on the cut
cell with 11 to the left; leave in C at cell -1 with 0101 at -2..1; a carry reaches the end of the segment in D with
11 to its left, and the next unit is then replaced by its standard exit) bring the body back to itself after 4 trips
with exactly one carry. Bounces must not read past the segment."""
import re
from endlib import Wd, TR
_c={}
def trip(k, body):
    U=Wd*k+body; left='0'*30+'11'
    tape=[int(c) for c in left+U]+[9]*40; base=len(left); vb=base+len(U)
    pos=base; st='D'; snap=None; carried=False
    for _ in range(5*10**6):
        y=tape[pos]
        if y not in (0,1): return None
        w,d,ns=TR[(st,y)]; tape[pos]=w; pos+=d; st=ns
        if pos==vb and not carried:
            if st!='D' or tape[vb-2:vb]!=[1,1]: return None
            carried=True; tape[vb-2]=0; pos=vb-1; st='C'
        if carried and pos>=vb: return None
        if pos==base-1 and st=='C': snap=''.join(map(str,tape[base-2:vb]))
        if pos<=base-3: break
    else: return None
    if snap is None or snap[:4]!='0101': return None
    new='011'+snap[1:]
    if carried:
        if new[-4:]!='0111': return None
        new=new[:-4]
    m=re.match(r'((?:011101)*)',new); k2=len(m.group(1))//6
    return carried, k2, new[6*k2:]
def ok(k, body):
    key=body
    if key in _c: return _c[key]
    res=False; b=body; kk=max(k,6); nc=0
    for i in range(4):
        r=trip(kk,b)
        if r is None: break
        c,k2,b=r; nc+=c; kk=k2
        if kk<3: break
        if b==body and i==3: res = (nc==1 and kk==max(k,6)+2)
    _c[key]=res; return res
