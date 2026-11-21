"""Mine the local shapes next to the head: strip from each half-tape the longest far part that matches the
structural language, and collect the remaining near-head part (runs >= 6 shown as len mod 6).  Simulated.
Usage: mine.py   (runs a fixed set of starts)"""
import re,sys,collections
from ctl import parse_tm
M='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
tm=parse_tm(M)
FARL=re.compile(r'^(?:1+(?:0 ?11(?:111)*(?=0))*)'.replace(' ',''))
TOK='0010(?:101010)*10'
# right half natural order: near part, then far part = ((101010)* T* 001 0)* (101010)* T* 001  (then 0s)
FARR=re.compile(r'(?:(?:101010)*(?:'+TOK+r')*0010)*(?:101010)*(?:'+TOK+r')*001$')
def shapeof(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        n=j-i; out.append(s[i]*n if n<6 else f'{s[i]}[{n%6}]'); i=j
    return ' '.join(out)
def run(L,s,R,steps,cl,cr):
    L=list(L);R=list(R)
    for t in range(steps):
        if not R: R.append(0)
        ls=''.join(map(str,L)).lstrip('0'); rs=''.join(map(str,R)).rstrip('0')
        m=FARL.match(ls); near=ls[m.end():] if m else ls
        cl[(s,shapeof(near[-14:]) if len(near)>14 else shapeof(near), len(near)>14)]+=1
        best=len(rs)
        for k in range(0,len(rs)+1):
            if FARR.fullmatch(rs[k:]): best=k;break
        cr[(s,shapeof(rs[:best]))]+=1
        tr=tm[(s,R[0])]
        if tr is None: print('HALT'); return
        w,mv,ns=tr; R[0]=w
        if mv=='R': L.append(R.pop(0))
        else: R.insert(0,L.pop() if L else 0)
        s=ns
cl=collections.Counter(); cr=collections.Counter()
def P(r,ds,ph='P'):
    c=[1]*r
    for d in ds: c+=[0]+[1]*(3*d+2)
    return c+([0,1] if ph=='P' else [0,1,1,1,1])
T=lambda k: '00'+'10'*(3*k+2)
def X(r,ds,levels):
    w='0'.join(''.join(T(k) for k in reg)+'001' for reg in levels)
    return P(r,ds)[:-2]+[0,1,1], 'E', [1,0]+[int(c) for c in w]
run(P(3,[0,2,2,1,1,1,1,1,2,0]),'B',[0],60000,cl,cr)
run(P(6,[1]*30),'B',[0],60000,cl,cr)
run(P(12,[3,1,5,1,1,3]),'B',[0],60000,cl,cr)
for lv in ([[0,0],[0]*5],[[0,0],[0]*5,[0]*7],[[0],[0,1,0],[2,0],[0]*4],[[],[0,0],[0]*3],[[0],[],[0,0]]):
    a,b,c=X(3,[0,1,1],lv); run(a,b,c,20000,cl,cr)
print('LEFT near shapes:',len(cl))
for k,v in sorted(cl.items(),key=lambda x:-x[1]): print(' ',v,k)
print('RIGHT near shapes:',len(cr))
for k,v in sorted(cr.items(),key=lambda x:-x[1]): print(' ',v,k)
