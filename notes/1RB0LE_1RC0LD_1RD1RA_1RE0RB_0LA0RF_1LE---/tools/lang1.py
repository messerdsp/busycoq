import sys; sys.setrecursionlimit(100000)
from ctl import check, report, concrete
M115='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
DIG='(0 11 (111)*)'            # a digit block 0 1^(3d+2)
TOK='(0 0 1 0 1 0 (101010)*)'  # converted odd digit / passed token 0 0 (1 0)^(3k+2)
LEFT=f'0* ( 1 ( 11 (111)* {DIG}* (0 1*)? .{{0,4}} | .{{0,6}} ) )?'
RIGHT=f'( .{{0,4}} ( (10)* {TOK}* 001 0 )* (10)* {TOK}* 001 | .{{0,6}} 1 )? 0*'
def P(r,ds):
    L=[1]*r
    for d in ds: L+= [0]+[1]*(3*d+2)
    return (L+[0,1],'B',[0])
init=P(3,[0,2,2,1,1,1,1,1,2,0])
print(concrete(M115,LEFT,RIGHT,init,200000))
from ctl import words
for K in (1,):
    r=check(M115,LEFT,RIGHT,K=K,init=init); report(r)
    import ctl
    dL=ctl.track(ctl.to_dfa(LEFT),K,6,3); dR=ctl.track(ctl.to_dfa(RIGHT,True),K,6,3)
    for c in r['path']: print(c, words(dL,dR,c))
