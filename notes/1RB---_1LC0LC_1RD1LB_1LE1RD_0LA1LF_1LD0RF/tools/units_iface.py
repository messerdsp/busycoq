# at each unit boundary (start cell of a wall run, round-start alignment), record how the head enters and leaves it
import re, sys, collections
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from xlemma import T
def cells(toks):
    s=''
    for t in toks:
        b,_,e=t.partition('^'); e=int(e) if e else 1
        if e>8: e=30+e%2
        s+=b*e
    return s
ent=collections.Counter(); ext=collections.Counter()
for li,line in enumerate(open('samp.txt')):
    if li%50: continue
    s=cells(line.split()[2:])
    starts=[m.start() for m in re.finditer(r'(?:011101){4,}', s)]
    base=1000; tape=bytearray(base)+bytearray(int(c) for c in s)+bytearray(3000)
    bset={base+x:i+1 for i,x in enumerate(starts[:10])}
    pos=base-1; st='C'; seen=set(); lastleave={}
    for k in range(2_000_000):
        y=tape[pos]; w,d,ns=T[(st,y)]; tape[pos]=w; npos=pos+d
        if npos in bset and d==1 and npos not in seen:
            seen.add(npos); ent[(bset[npos], ns, bytes(tape[npos-8:npos]).hex())]+=1
        if pos in bset and d==-1:
            lastleave[pos]=(ns, bytes(tape[pos-7:pos+1]).hex())
        pos=npos; st=ns
        if pos<base-6 and len(seen)>0 and st=='C': break
    for p,v in lastleave.items(): ext[(bset[p],)+v]+=1
for k,v in sorted(ent.items()): print('enter',k,v)
for k,v in sorted(ext.items()): print('leave',k,v)
