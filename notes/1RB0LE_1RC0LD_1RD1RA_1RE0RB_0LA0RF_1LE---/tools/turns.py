"""Print the tape at every right turn of the head (a step moving left right after a step moving right).
Simulated, cell by cell.  Usage: turns.py MACHINE STEPS [TAPEFILE]
Tape shown with the head cell marked as <S>; runs of the 6-cell-free digit view are not applied here."""
import sys
def parse(s):
    t={}
    for i,r in enumerate(s.split('_')):
        for b in range(2):
            c=r[3*b:3*b+3]
            t[(chr(65+i),b)]=None if c[2] not in 'ABCDEF' else (int(c[0]),1 if c[1]=='R' else -1,c[2])
    return t
def rle(cells):
    out=[];i=0
    while i<len(cells):
        j=i
        while j<len(cells) and cells[j]==cells[i]: j+=1
        n=j-i; out.append(f'{cells[i]}^{n}' if n>3 else str(cells[i])*n); i=j
    return ' '.join(out)
def main():
    tm=parse(sys.argv[1]); N=int(float(sys.argv[2]))
    tape={}; pos=0; st='A'; last=0; step=0
    while step<N:
        b=tape.get(pos,0); tr=tm[(st,b)]
        if tr is None: print('HALT',step); return
        w,d,ns=tr; tape[pos]=w
        if last==1 and d==-1:
            lo=min(k for k,v in tape.items() if v) if any(tape.values()) else 0
            hi=max(k for k,v in tape.items() if v) if any(tape.values()) else 0
            lo=min(lo,pos);hi=max(hi,pos)
            L=[tape.get(k,0) for k in range(lo,pos)]; R=[tape.get(k,0) for k in range(pos,hi+1)]
            print(step, rle(L), f'<{st}>', rle(R))
        last=d; pos+=d; st=ns; step+=1
main()
