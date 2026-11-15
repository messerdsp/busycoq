import sys, re, collections
ROT=['110101'[i:]+'110101'[:i] for i in range(6)]
RX=re.compile('|'.join('(?:%s){3,}'%r for r in ROT))
def cells_of(toks, big=200):
    """expand; runs with count>=big become placeholders \x00index"""
    s=[]; bigs=[]
    for t in toks:
        b,_,n=t.partition('^'); n=int(n) if n else 1
        if n>=big: s.append('|%d|'%len(bigs)); bigs.append((b,n))
        else: s.append(b*n)
    return ''.join(s).rstrip('0'), bigs
def parse(toks):
    s,bigs=cells_of(toks)
    # replace big placeholders by a wall marker: we need its cell length; walls are 110101 rotations
    parts=re.split(r'\|(\d+)\|', s)
    seq=[]   # list of ('w', word) and ('W', ncopies)
    for i,pc in enumerate(parts):
        if i%2==1:
            b,n=bigs[int(pc)]; seq.append(('B', b, n)); continue
        last=0
        for m in RX.finditer(pc):
            seq.append(('w', pc[last:m.start()])); seq.append(('W', m.group()[:6], (m.end()-m.start())//6)); 
            if (m.end()-m.start())%6: seq.append(('w', m.group()[(m.end()-m.start())//6*6:]))
            last=m.end()
        seq.append(('w', pc[last:]))
    # merge: a big run adjacent to a W of the same period joins it; drop empty words
    out=[]
    for x in seq:
        if x[0]=='w' and x[1]=='': continue
        out.append(x)
    return out
def fmt(seq):
    return ' '.join(('%d'%len(x[1])) if x[0]=='w' else ('W%d'%x[2] if x[0]=='W' else 'B%s^%d'%(x[1],x[2])) for x in seq)
if __name__=='__main__':
    rows=[l.split() for l in open(sys.argv[1])]
    for r in rows[int(sys.argv[2]):int(sys.argv[3])]:
        print(r[0], fmt(parse(r[2:])))
