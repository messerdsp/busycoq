"""For each sweep, the turning point at the head's maximum excursion: state, local window, and what lies right of
it (tokens collapsed).  Simulated.  Usage: frontier.py LEFTCELLS STATE RIGHTCELLS STEPS"""
import sys,re
from ctl import parse_tm
tm=parse_tm('1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---')
def tokshape(s):
    s=s.rstrip('0'); out=[]; i=0
    while i<len(s):
        m=re.match(r'00((?:10)+)',s[i:])
        if m and (len(m.group(1))//2-2)%3==0 and (i+m.end()==len(s) or s[i+m.end()]=='0'):
            out.append('T'); i+=m.end(); continue
        out.append(s[i]); i+=1
    return re.sub(r'(T)+','T*',''.join(out))
def run(L,st,R,steps,out=print):
    n=len(L); tape=bytearray(4*n+4*len(R)+200000); pos=len(tape)//4
    for i,c in enumerate(L): tape[pos-n+i]=c
    for i,c in enumerate(R): tape[pos+i]=c
    mx=pos; mxinfo=None; t=0; res=[]
    while t<steps:
        b=tape[pos]; tr=tm[(st,b)]
        if tr is None: out(f'HALT at {t}'); return
        if pos>=mx:
            mx=pos; e=pos+40
            while e>pos and tape[e]==0: e-=1
            mxinfo=(t,st,''.join(map(str,tape[pos-9:pos])),''.join(map(str,tape[pos:pos+9])),tokshape(''.join(map(str,tape[pos:e+1]))))
        w,d,ns=tr; tape[pos]=w; pos+=1 if d=='R' else -1; st=ns; t+=1
        if pos<mx-14 and mxinfo:
            out(f'{mxinfo[0]:7d} {mxinfo[1]} ...{mxinfo[2]} [{mxinfo[1]}>]{mxinfo[3]}...   right: {mxinfo[4][:60]}')
            mxinfo=None; mx=pos
if __name__=='__main__':
    L=[int(c) for c in sys.argv[1]]; R=[int(c) for c in sys.argv[3]]
    run(L,sys.argv[2],R,int(float(sys.argv[4])))
