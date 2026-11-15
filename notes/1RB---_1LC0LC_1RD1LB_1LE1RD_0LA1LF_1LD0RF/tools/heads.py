import os
exec(open('units.py').read().split("rows=[]")[0])
rows=[]
for line in open('ev.txt'):
    k,st,s=line.split()
    if st=='B': rows.append((int(k),split(s)))
R=[p for k,p in rows[::2]]
for u in (2,4):
    ws=[]
    for p in R:
        if p[u] not in ws: ws.append(p[u])
    # common suffix
    suf=os.path.commonprefix([w[::-1] for w in ws])[::-1]
    print('== unit',u//2,'common suffix len',len(suf))
    for w in ws: print('  head:', short(w[:len(w)-len(suf)]))
    print('  body:', short(suf)[:300])
