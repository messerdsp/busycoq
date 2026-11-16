# for sampled round-start lines (first runs only): shrink walls, simulate, record wall-end contexts with unit index
import sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from xlemma import T
TT={(s,y):v for (s,y),v in T.items()}
out=open(sys.argv[2],'w'); every=int(sys.argv[3]); NS=int(sys.argv[4])
for li,line in enumerate(open(sys.argv[1])):
    if li%every: continue
    f=line.split()
    if f[1]!='C': continue
    cells=[]
    for t in f[2:]:
        b,_,e=t.partition('^'); e=int(e) if e else 1
        if e>8: e=30+(e%2)
        cells+=[int(c) for c in b]*e
    s0=''.join(map(str,cells))
    if not (s0.startswith('111111110111') or s0.startswith('110101011101')): continue
    tape=bytearray(1000)+bytearray(cells)+bytearray(2000); end=1000+len(cells)-400
    pos=999; s='C'; unit=0
    for k in range(NS):
        y=tape[pos]; w,d,ns=TT[(s,y)]; tape[pos]=w; pos+=d; s=ns
        if pos<1010: unit=0
        if pos>end: break
        if s=='D' and tape[pos]==0 and tape[pos-5:pos]==b'\0\0\0\0\0' and tape[pos+1:pos+7]==b'\1\1\0\1\1\1' and tape[pos+7:pos+13]!=b'\0\1\0\1\1\1':
            unit+=1
            out.write('%d %d %s\n'%(unit,li,''.join(map(str,tape[pos+7:pos+307]))))
