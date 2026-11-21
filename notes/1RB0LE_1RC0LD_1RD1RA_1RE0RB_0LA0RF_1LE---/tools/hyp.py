"""Test a hypothesis for the half-tape languages on all configurations of several runs.  Simulated.
Right half (head->far): NEAR then FAR, FAR = blocks B_n = 00(10)^n with n = 1 or n = 2 mod 3, or `110`, then `001`.
Left half (far->head): 1^(3a) then digits 0 1^(3d+2), then NEAR.  Reports the longest NEAR parts seen."""
import re,collections,sys
from ctl import parse_tm
tm=parse_tm('1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---')
FARR=re.compile(r'(?:00(?:10|1010(?:101010)*)|110)*001$')    # B_1 = 0010 or B_(3k+2) = 00 1010 (101010)^k ; or 110
FARL=re.compile(r'^(?:111)+(?:011(?:111)*)*')
def near_right(rs):
    for k in range(len(rs)+1):
        if FARR.fullmatch(rs[k:]): return rs[:k]
    return None
statsL=collections.Counter(); statsR=collections.Counter(); worst=[0,0,'','']
def run(L,s,R,steps,name):
    L=list(L);R=list(R)
    for t in range(steps):
        if not R: R.append(0)
        ls=''.join(map(str,L)).lstrip('0'); rs=''.join(map(str,R)).rstrip('0')
        m=FARL.match(ls); nl=ls[m.end():] if m else ls
        nr=near_right(rs) if rs else ''
        if nr is None: nr='!'+rs
        if len(nl)>worst[0]: worst[0]=len(nl); worst[2]=f'{name} t={t} {s} L-near={nl[:80]}'
        if len(nr)>worst[1]: worst[1]=len(nr); worst[3]=f'{name} t={t} {s} R-near={nr[:80]}'
        statsL[min(len(nl),40)]+=1; statsR[min(len(nr),40)]+=1
        tr=tm[(s,R[0])]
        if tr is None: print('HALT',name,t); return
        w,mv,ns=tr; R[0]=w
        if mv=='R': L.append(R.pop(0))
        else: R.insert(0,L.pop() if L else 0)
        s=ns
def P(r,ds,ph='P'):
    c=[1]*r
    for d in ds: c+=[0]+[1]*(3*d+2)
    return c+([0,1] if ph=='P' else [0,1,1,1,1])
T=lambda k: '00'+'10'*(3*k+2)
def X(r,ds,levels):
    w='0'.join(''.join(T(k) for k in reg)+'001' for reg in levels)
    return P(r,ds)[:-2]+[0,1,1], 'E', [1,0]+[int(c) for c in w]
run(P(3,[0,2,2,1,1,1,1,1,2,0]),'B',[0],80000,'run115779')
run(P(6,[1]*30),'B',[0],60000,'P6_1^30')
run(P(12,[3,1,5,1,1,3]),'B',[0],60000,'P12')
for lv in ([[0,0],[0]*5],[[0,0],[0]*5,[0]*7],[[0],[0,1,0],[2,0],[0]*4],[[],[0,0],[0]*3],[[0],[],[0,0]]):
    a,b,c=X(3,[0,1,1],lv); run(a,b,c,20000,f'X{lv}')
print('left near lengths',sorted(statsL.items())); print('right near lengths',sorted(statsR.items()))
print(worst[2]); print(worst[3])
# debug: show the right half at the worst point, split into blocks
def blocks(s):
    out=[];i=0
    while i<len(s):
        m=re.match(r'00((?:10)*)',s[i:])
        if m and m.end()>2:
            out.append(f'B{len(m.group(1))//2}'); i+=m.end(); continue
        out.append(s[i]); i+=1
    return ' '.join(out)
