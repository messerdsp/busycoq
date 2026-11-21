import sys
from ctl import check_abs, runs_abs, alt_abs, report, words
M115='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
def P(r,ds):
    L=[1]*r
    for d in ds: L+= [0]+[1]*(3*d+2)
    return (L+[0,1],'B',[0])
init=P(3,[0,2,2,1,1,1,1,1,2,0])
for KL,KR in [(2,2),(3,3),(4,4),(3,6),(4,8),(6,6),(6,10)]:
    try:
        r=check_abs(M115,runs_abs(KL),alt_abs(KR),init=init,maxconf=1_500_000)
    except RuntimeError as e: print(KL,KR,e); continue
    print(KL,KR,end=' '); report(r)
