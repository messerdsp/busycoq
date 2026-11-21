import re,sys
def parse(s):
    rows=s.strip().split('_'); return [[r[i:i+3] for i in range(0,len(r),3)] for r in rows]
def fmt(t): return '_'.join(''.join(c for c in r) for r in t)
def norm_halt(c): return '---' if (c[2] in 'Z-H' or c=='---' or c[2] not in 'ABCDEF') else c
def mirror(t): return [[c if c=='---' else c[0]+{'L':'R','R':'L'}[c[1]]+c[2] for c in r] for r in t]
def relabel(t):
    # BFS-ish order of first appearance reading table row by row in new order
    n=len(t); order=['A']; i=0
    while i<len(order):
        r=t[ord(order[i])-65]
        for c in r:
            if c!='---' and c[2] not in order: order.append(c[2])
        i+=1
    for k in range(n):
        ch=chr(65+k)
        if ch not in order: order.append(ch)
    mp={o:chr(65+i) for i,o in enumerate(order)}
    nt=[None]*n
    for o in order:
        nt[ord(mp[o])-65]=[c if c=='---' else c[:2]+mp[c[2]] for c in t[ord(o)-65]]
    return nt
def canon(s):
    t=[[norm_halt(c) for c in r] for r in parse(s)]
    a=fmt(relabel(t)); b=fmt(relabel(mirror(t)))
    # TNF: first move right
    cands=[x for x in (a,b) if x[1]=='R'] or [a,b]
    return min(cands)
if __name__=='__main__':
    for l in sys.stdin: 
        l=l.strip()
        if l: print(canon(l))
