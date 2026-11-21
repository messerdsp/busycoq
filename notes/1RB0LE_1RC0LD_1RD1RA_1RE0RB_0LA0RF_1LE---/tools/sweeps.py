"""Snapshot at every sweep start of 115779's table (states named as in 115779), decoded into digits.
Simulated, cell by cell.  Events: P/Q: state B on 0 with blank right; X: E on 1 with left ...0 1 1;
Y: F on 0 with left ...0 1 1 1 0 and right 0 1 0 ...
Usage: sweeps.py MACHINE STEPS [maxprint]   (MACHINE in 115779 naming or 23154: renamed automatically)"""
import sys,re
REN23154={'A':'E','B':'A','C':'B','D':'C','E':'D','F':'F'}   # 23154 state -> 115779 state
def parse(s):
    t={}
    for i,r in enumerate(s.split('_')):
        for b in range(2):
            c=r[3*b:3*b+3]
            t[(chr(65+i),b)]=None if c[2] not in 'ABCDEF' else (int(c[0]),1 if c[1]=='R' else -1,c[2])
    return t
def dec_left(L):
    # L: list of cells from leftmost nonzero to head-1. Expect 1^r then (0 1^n)*
    s=''.join(map(str,L)).lstrip('0')
    parts=s.split('0')
    r=len(parts[0]); ds=[]
    for p in parts[1:]:
        n=len(p)
        ds.append(str((n-2)//3) if n>=2 and (n-2)%3==0 else f'[{n}]')
    return r,ds
def tok_right(R):
    s=''.join(map(str,R)).rstrip('0')
    out=[];i=0
    m=re.compile(r'00((?:10)+)')
    while i<len(s):
        mm=m.match(s,i)
        if mm and (len(mm.group(1))//2-2)%3==0 and (i+len(mm.group(0))==len(s) or s[i+len(mm.group(0))]=='0'):
            k=(len(mm.group(1))//2-2)//3; out.append(f'p{2*k+1}'); i+=len(mm.group(0)); continue
        out.append(s[i]); i+=1
    # compress plain chars
    res=[];buf=''
    for o in out:
        if len(o)==1: buf+=o
        else:
            if buf: res.append(buf); buf=''
            res.append(o)
    if buf: res.append(buf)
    # rle tokens
    r2=[]
    for o in res:
        if r2 and r2[-1][0]==o: r2[-1][1]+=1
        else: r2.append([o,1])
    return ' '.join(o if c==1 else f'{o}^{c}' for o,c in r2)
def rled(ds):
    r2=[]
    for o in ds:
        if r2 and r2[-1][0]==o: r2[-1][1]+=1
        else: r2.append([o,1])
    return ' '.join(o if c<3 else f'{o}^{c}' for o,c in r2 for _ in ([0] if c>=3 else range(c)))
def main():
    m=sys.argv[1]
    if m.startswith('1RB0LE'):
        # rename 23154 into 115779 naming
        rows=m.split('_'); t={}
        new=['']*6
        for i,r in enumerate(rows):
            s=chr(65+i); ns=REN23154[s]
            rr=''
            for b in range(2):
                c=r[3*b:3*b+3]; rr+=c if c=='---' else c[:2]+REN23154[c[2]]
            new[ord(ns)-65]=rr
        tm=parse('_'.join(new)); st='E'
    else:
        tm=parse(m); st='A'
    N=int(float(sys.argv[2])); maxp=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
    tape=bytearray(1<<22); pos=1<<21; lo=hi=pos; step=0; cnt=0; prev=None
    if len(sys.argv)>4:   # start from P(r; ds) or Q(r; ds): argv[4] = 'P' or 'Q', argv[5] = r, argv[6] = d1,d2,...
        ph=sys.argv[4]; r=int(sys.argv[5]); ds=[int(x) for x in sys.argv[6].split(',') if x]
        cells=[1]*r
        for d in ds: cells+=[0]+[1]*(3*d+2)
        cells+= [0,1] if ph=='P' else [0,1,1,1,1]
        start=pos-len(cells)
        for i,c in enumerate(cells): tape[start+i]=c
        lo=start; st='B'
    while step<N:
        b=tape[pos]; tr=tm[(st,b)]
        if tr is None: print('HALT',step); return
        ev=None
        if st=='B' and b==0 and pos>=hi: ev='PQ'
        elif st=='E' and prev==('B',1) and b==1 and tape[pos-1]==1 and tape[pos-2]==1 and tape[pos-3]==0 and tape[pos+1]==0: ev='X'
        elif st=='F' and prev==('D',1) and b==0 and tape[pos-1]==0 and tape[pos-2]==1 and tape[pos-3]==1 and tape[pos-4]==1 and tape[pos-5]==0 and tape[pos+1]==1 and tape[pos+2]==0: ev='Y'
        if ev:
            cnt+=1
            if cnt<=maxp:
                L=list(tape[lo:pos]); R=list(tape[pos:hi+1])
                if ev=='PQ':
                    s=''.join(map(str,L)).rstrip('0')
                    ph='P' if s.endswith('01') and not s.endswith('11') else ('Q' if s.endswith('01111') else '?')
                    core=L[:len(s)-(2 if ph=='P' else 5)] if ph!='?' else L
                    r,ds=dec_left(core); print(step,ph,f'r={r}',rled(ds))
                else:
                    core=L[:len(L)-(3 if ev=='X' else 5)]
                    r,ds=dec_left(core); print(step,ev,f'r={r}',rled(ds),'|',tok_right(R[(2 if ev=='X' else 3):]))
        w,d,ns=tr; tape[pos]=w; pos+=d; prev=(st,b); st=ns; step+=1
        if pos<lo: lo=pos
        if pos>hi: hi=pos
main()
