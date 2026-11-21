"""Collect half-tapes of real runs that lie outside the given LEFT/RIGHT languages (simulated)."""
import re,collections,sys
from ctl import parse_tm, to_dfa
tm=parse_tm('1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---')
def runs(LEFT,RIGHT,starts,steps=60000):
    dL=to_dfa(LEFT); dR=to_dfa(RIGHT,True)
    outL=collections.Counter(); outR=collections.Counter()
    for (L,s,R) in starts:
        L=list(L);R=list(R); face='R'
        for t in range(steps):
            if not R: R.append(0)
            LL = L+[R[0]] if face=='L' else L          # DH view: facing left, the head cell belongs to the left half
            RR = R[1:] if face=='L' else R
            q=0
            for a in LL: q=dL[0][q][a]
            if q==dL[3]: outL[(s+face,''.join(map(str,LL)).lstrip('0'))]+=1
            r=0
            for a in reversed(RR): r=dR[0][r][a]
            if r==dR[3]: outR[(s+face,''.join(map(str,RR)).rstrip('0'))]+=1
            tr=tm[(s,R[0])]
            if tr is None: print('HALT'); break
            w,mv,ns=tr; R[0]=w
            if mv=='R': L.append(R.pop(0))
            else: R.insert(0,L.pop() if L else 0)
            s=ns; face=mv
    return outL,outR
def P(r,ds,ph='P'):
    c=[1]*r
    for d in ds: c+=[0]+[1]*(3*d+2)
    return (c+([0,1] if ph=='P' else [0,1,1,1,1]),'B',[0])
STARTS=[P(3,[0,2,2,1,1,1,1,1,2,0]),P(6,[1]*30),P(12,[3,1,5,1,1,3]),P(12,[1,1,1,1,1,1]),P(9,[1,1,3]),P(3,[1,1,1,1]),P(15,[1,3,1])]
if __name__=='__main__':
    exec(open('lang2.py').read().split('def P(')[0])
    oL,oR=runs(LEFT,RIGHT,STARTS)
    print('LEFT outside:',len(oL))
    for k,v in sorted(oL.items(),key=lambda x:len(x[0][1]))[:60]: print(' ',v,k)
    print('RIGHT outside:',len(oR))
    for k,v in sorted(oR.items(),key=lambda x:len(x[0][1]))[:60]: print(' ',v,k)
