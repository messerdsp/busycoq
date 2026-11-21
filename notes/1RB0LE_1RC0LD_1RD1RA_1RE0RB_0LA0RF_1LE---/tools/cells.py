"""Print every configuration (cell by cell) of 115779's table from a given tape.  Simulated.
Usage: cells.py "LEFT" STATE "RIGHT" STEPS    (LEFT ends next to the head; RIGHT starts with the head cell)"""
import sys
T='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
tm={}
for i,r in enumerate(T.split('_')):
    for b in range(2):
        c=r[3*b:3*b+3]; tm[(chr(65+i),b)]=None if c=='---' else (int(c[0]),1 if c[1]=='R' else -1,c[2])
L=[int(c) for c in sys.argv[1].replace(' ','')]; st=sys.argv[2]; R=[int(c) for c in sys.argv[3].replace(' ','')]
N=int(sys.argv[4])
for t in range(N):
    if not R: R=[0]
    b=R[0]; tr=tm[(st,b)]
    print(f'{t:4d} {"".join(map(str,L)):>60} {st}> {"".join(map(str,R))}')
    if tr is None: print('HALT'); break
    w,d,ns=tr; R[0]=w
    if d==1: L.append(R.pop(0))
    else:
        R.insert(0, L.pop() if L else 0)
    st=ns
