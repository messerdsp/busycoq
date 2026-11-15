import sys, re, collections
W='111010'
def split(s):
    """split tape into [d0, n1, d1, n2, d2, ...]: d = non-wall strings, n = wall counts (runs of W of length >= 3)"""
    parts=[]; i=0; last=0
    for m in re.finditer('(?:%s){3,}'%W, s):
        parts.append(s[last:m.start()]); parts.append((m.end()-m.start())//6); last=m.end()
    parts.append(s[last:]); return parts
def short(d):
    out=[];i=0
    while i<len(d):
        j=i
        while j<len(d) and d[j]==d[i]: j+=1
        out.append(('1' if d[i]=='1' else '0')+('' if j-i==1 else '^%d'%(j-i))); i=j
    return ' '.join(out)
rows=[]
for line in open(sys.argv[1]):
    k,st,s=line.split()
    if st!='B': continue
    rows.append((int(k),split(s)))
print(len(rows))
for k,p in rows[:12]:
    print(k, ' | '.join(str(x) if isinstance(x,int) else short(x)[:60] for x in p[:9]))

# per unit index: distinct digit words, their lengths
R=[p for k,p in rows[::2]]
nun=collections.Counter(len(p) for p in R); print('parts per sample', nun)
L=min(len(p) for p in R)
for u in range(0, L, 2):
    words=collections.Counter(p[u] for p in R)
    walls=collections.Counter(p[u+1] for p in R if u+1<L)
    print('unit',u//2,'distinct words',len(words),'lens',sorted(set(len(w) for w in words))[:8], 'walls', (min(walls),max(walls)) if walls else '')
