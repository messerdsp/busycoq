import re,sys
from endlib import Wd
from gunit2 import ok, trip
B=['010101','110101','011101','010111']; ROT=[B[r:]+B[:r] for r in range(4)]
def cells(fn, stop_band=False):
    t=open(fn).read().split()[2:]; s='0'; i=0
    while i<len(t):
        if any(t[i:i+40]==R*10 for R in ROT):   # skip long bands (keep 2 words as a marker)
            R=next(R for R in ROT if t[i:i+40]==R*10); s+='BANDBAND'
            while t[i:i+4]==R: i+=4
            continue
        b,_,e=t[i].partition('^'); e=int(e) if e else 1
        if e>60: e=60+e%12
        s+=b*e; i+=1
    return s.rstrip('0')
def orbit(b):
    bs=[b]; k=8
    for _ in range(3):
        r=trip(k,bs[-1]); k=r[1]; bs.append(r[2])
    return frozenset(bs)
seen={}; order=[]
for fn in open('files2.lst').read().split():
    s=cells(fn)
    for piece in s.split('BANDBAND'):
        parts=re.split(r'((?:011101){3,})', piece)
        for u in range(1,len(parts),2):
            b=parts[u+1]
            if 'BAND' in b or len(b)>3000: continue
            if ok(8,b):
                key=orbit(b)
                if key not in seen:
                    seen[key]=fn; order.append((fn,min(len(x) for x in key)))
    print(fn, 'types so far', len(seen)); sys.stdout.flush()
print('\nnew types by file:')
from collections import Counter
for fn,c in Counter(f for f,_ in order).items(): print(fn,c)
print('\n=== bodies (phase with the shortest body), compressed: W=011101, runs of repeated 8-cell band piece as b<n>')
def comp(x):
    x=x.replace(Wd,' W ')
    x=re.sub(r'(?: W 01){3,}', lambda m:' w01^%d'%(len(m.group(0))//6), x)
    return re.sub(r'\s+',' ',x)
for key,fn in seen.items():
    b=min(key,key=len)
    print(fn, len(b), comp(b)[:170])
