import sys; sys.setrecursionlimit(100000)
from ctl import check, report, words, to_dfa, track2
M115='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
DIG='(0 11 (111)*)'
T='(00 1010 (101010)*)'; U='(101010)'; b='(0010)'
LEFT=f'0* ( 111 (111)* {DIG}* (0 1*)? .{{0,3}} | 10 | 110 )?'
# right half, natural order (head first): near part, then region material, then the end 0 0 1
NEAR='(.{0,4} (10)* (110)?)'
END='(001|00101|001011)'
ENDS='(1|01|101|0101|11|011|1011|01011)'
RIGHT=f'( {NEAR} ( {U} | {T} | {b} | {b}110 )* {END} | .{{0,4}} {ENDS} )? 0*'
def P(r,ds):
    L=[1]*r
    for d in ds: L+= [0]+[1]*(3*d+2)
    return (L+[0,1],'B',[0])
init=P(3,[0,2,2,1,1,1,1,1,2,0])
for win in (4,6,8):
    r=check(M115,LEFT,RIGHT,K='w',win=win,init=init,maxconf=3_000_000); report(r)
    if r.get('status') in ('DEAD','HALT'):
        dL=track2(to_dfa(LEFT),win,6,3); dR=track2(to_dfa(RIGHT,True),win,6,3)
        for c in r['path'][-8:]: print('   ',c, words(dL,dR,c))
