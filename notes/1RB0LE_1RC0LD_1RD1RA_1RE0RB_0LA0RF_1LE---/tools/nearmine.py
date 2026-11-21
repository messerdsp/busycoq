"""Exact near-head forms of right halves (DH view): shortest prefix NEAR with the rest in MAT* END.  Simulated."""
import re,collections
from ctl import parse_tm
from outside import P, STARTS, tm
MAT=r'(?:101010|00 1010(?:101010)*|0010|0010110)'.replace(' ','')
REST=re.compile(r'(?:'+MAT+r')*(?:001|00101|001011)')
def abst(s):
    s=re.sub(r'((?:10){3,})',lambda m:f'(10)[{len(m.group(1))//2%3}+]',s)
    return s
near=collections.Counter(); ex={}
def run(L,s,R,steps=60000):
    L=list(L);R=list(R);face='R'
    for t in range(steps):
        if not R: R.append(0)
        RR=R[1:] if face=='L' else R
        rs=''.join(map(str,RR)).rstrip('0')
        k=None
        for i in range(len(rs)+1):
            if REST.fullmatch(rs[i:]) or (i==len(rs)): k=i;break
        nr=rs[:k]
        key=(s+face,abst(nr) if len(nr)<len(rs) or not rs else 'ALL:'+abst(nr))
        near[key]+=1; ex.setdefault(key,rs[:60])
        tr=tm[(s,R[0])]
        w,mv,ns=tr; R[0]=w
        if mv=='R': L.append(R.pop(0))
        else: R.insert(0,L.pop() if L else 0)
        s=ns; face=mv
for st in STARTS: run(*st)
keys=sorted(near,key=lambda k:(k[1].startswith('ALL'),len(k[1])))
print(len(keys))
for k in keys: print(near[k],k,ex[k])
