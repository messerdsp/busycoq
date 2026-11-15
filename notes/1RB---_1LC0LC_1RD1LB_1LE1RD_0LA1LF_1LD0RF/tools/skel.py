import sys
def skel(toks):
    out=[]; nshort=0; words=[]; cur=[]
    for t in toks:
        b,_,n=t.partition('^'); n=int(n) if n else 1
        if n>=3:
            out.append('[%d]'%nshort if nshort else ''); out.append(str(n)); nshort=0
        else: nshort+=n
    out.append('[%d]'%nshort)
    return ' '.join(x for x in out if x)
for l in open(sys.argv[1]):
    r=l.split()
    if r[0]=='STOP': print(l); continue
    print(r[0], skel(r[2:]))
