"""Where does a right pass stop?  Start: LEFT 0 1 1 1 A> R; simulate until the head is 10 cells left of its
maximum; print the configuration at the maximum (the turn), as  ...left [S>] right.  Simulated.
Usage: rpass.py R [R ...]"""
import sys
from ctl import parse_tm
tm=parse_tm('1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---')
LEFT='11111101111101111101111101111'+'0111'
def go(Rs):
    tape=bytearray(4000); pos=1000
    for i,c in enumerate(LEFT): tape[pos-len(LEFT)+i]=int(c)
    for i,c in enumerate(Rs): tape[pos+i]=int(c)
    st='A'; mx=pos; best=None
    for t in range(20000):
        b=tape[pos]; tr=tm[(st,b)]
        if tr is None: return f'HALT at t={t}'
        if pos>mx or best is None:
            mx=pos; e=pos+60
            while e>pos and tape[e]==0: e-=1
            best=(t,st,''.join(map(str,tape[pos-12:pos])),''.join(map(str,tape[pos:e+1])))
        w,d,ns=tr; tape[pos]=w; pos+=1 if d=='R' else -1; st=ns
        if pos<mx-10: return f't={best[0]:4d}  ...{best[2]} [{best[1]}>] {best[3]}'
    return 'no turn'
for R in sys.argv[1:]:
    print(f'{R:>40} : {go(R)}')
