"""end_period.py: exact simulation of the end region of the post-overflow chain, isolated from the regular units.

The end region (everything right of the last regular unit, up to the band) is only visited when every regular unit
carries; a visit is a trip in the unit interface (enter in D with 11 to the left, leave in C at cell -1). This
simulates the visits one after another, peels off regular units that form at the front (types and words of
trips_gen.py), and reports when the end word returns to its starting value, the band crossings and where the band
edges are (distances from the right end of the simulated tape, which is fixed in absolute position)."""
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from trips_gen import Wd,seg,TR
BAND='010101110101011101010111'
TYPES=['U1','U2','U3','U4']
def ty(i): return TYPES[i] if i<4 else ('K' if i%2==0 else 'D')
def cells_cap(toks,cap):
    s=''
    for t in toks:
        b,_,e=t.partition('^'); e=int(e) if e else 1
        if cap and e>cap: e=cap+e%12
        s+=b*e
    return s
def parse_from(s,i,n0,kmin=3):
    us=[]
    while True:
        j=i; k=0
        while s.startswith(Wd,j): j+=6; k+=1
        t=ty(n0+len(us)); ph=[p for p in range(4) if s.startswith(seg(t,p),j)]
        if k<kmin or not ph: return us,i
        p=max(ph,key=lambda p:len(seg(t,p)))
        rest=s[j+len(seg(t,p)):]
        if not rest.startswith(Wd): return us,i
        us.append((t,p,k)); i=j+len(seg(t,p))
def load(fn,NB,FW,NAFT=40):
    """returns (units from U2, T) with T = E + BAND^NB + after-band cells (frozen wall capped at FW blocks)"""
    toks=open(fn).read().split(); toks=toks[2:]
    B=['010101','110101','011101','010111']
    for ti in range(len(toks)):
        if toks[ti:ti+8]==B*2: break
    tj=ti
    while toks[tj:tj+4]==B: tj+=4
    s=cells_cap(toks[:ti],60)
    best=min(m for m in (s.find(Wd*3+seg('U2',p)) for p in range(4)) if m>=0)
    i=best
    while s[i-6:i]==Wd: i-=6
    us,i=parse_from(s,i,1)
    return us, s[i:]+BAND*NB+cells_cap(toks[tj:tj+NAFT],FW)
def bandsplit(T):
    b=T.find(BAND*3); j=b
    while T.startswith(BAND,j): j+=24
    return T[:b],(j-b)//24,T[j:]
def trip(T):
    left='0'*60+'11'; s=left+T
    tape=bytearray(int(c) for c in s)+bytearray(300); base=len(left); pos=base; st='D'; ex=None; hi=pos; n=0
    snap=None
    while True:
        y=tape[pos]
        if (st,y) not in TR: return ('HALT',n)
        w,d,ns=TR[(st,y)]; tape[pos]=w; pos+=d; st=ns; n+=1
        if pos>hi: hi=pos
        if pos==base-1 and st=='C': snap=bytes(tape[base-2:base+len(T)+2])
        if pos<=base-3: break
        if pos>=len(s)+250: return ('RAN',)
    t=''.join(map(str,snap))
    assert t[:4]=='0101', t[:10]
    return ('ok','011'+t[1:len(T)+2], hi-base, n)
def peel(T,nu):
    E,nb,rest=bandsplit(T)
    us,i=parse_from(E,0,nu)
    return us, T[i:]

if __name__=='__main__':
    # usage: end_period.py TAPELINE NB FW VISITS
    #   TAPELINE: a round-start line of p3_count/chainb (e.g. init26.txt, the tape at step 2,592,545,302,250,949)
    #   NB: band words kept (the band pass does not depend on it), FW: cap on the frozen wall (blocks)
    fn=sys.argv[1]; NB=int(sys.argv[2]); FW=int(sys.argv[3]); N=int(sys.argv[4])
    us0,T=load(fn,NB,FW); nu=len(us0)+1
    print('regular units from U2:',len(us0))
    ref=None
    for it in range(N):
        E,nb,rest=bandsplit(T); D=len(T)-len(E)
        if ref is None: ref=E
        if E==ref: print('visit',it,'end word equal to the start','| band words',nb,'| band left edge to right end of tape',D,'| band right edge to right end',len(rest))
        r=trip(T)
        if r[0]!='ok': print(it,r); break
        T=r[1]
        if r[2]>len(E)+24*nb: print('   visit',it,'crosses the band and the first frozen wall, reaching',r[2]-len(E)-24*nb,'cells past the band,',r[3],'steps')
        born,T=peel(T,nu); nu+=len(born)
        if born: print('   visit',it,'a regular unit leaves the end region:',born)
