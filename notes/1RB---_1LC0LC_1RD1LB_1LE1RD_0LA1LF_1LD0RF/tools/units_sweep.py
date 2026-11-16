import sys, pickle, collections
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from genlemmas import run, T
ctx=collections.defaultdict(set)
for l in open(sys.argv[1]):
    u,_,c=l.split(); ctx[int(u)].add(c)
res={}
for u in sorted(ctx):
    for c in sorted(ctx[u]):
        kind,tape,start,pos,hi,s=run(c)
        if kind!='carry': continue
        fin=''.join(map(str,tape)); Z=fin[start-11:pos-5]
        if (u,Z) in res: continue
        cells=[int(x) for x in '0'*30+'011111'+Z+'01111']+[1,1,1,0,1,0]+[2]*50
        p=len(cells)-57; st='B'; ok=None; base=30
        for k in range(100000):
            y=cells[p]
            if y==2: ok='read-right'; break
            w,d,ns=T[(st,y)]; cells[p]=w; p+=d; st=ns
            if st=='C' and p==base+11 and cells[base:base+11]==[0,1,1,1,1,1,0,1,1,1,1]: ok=('ok',k+1,''.join(map(str,cells[p:p+len(Z)+6]))); break
            if p<base: ok='left-wall'; break
        res[(u,Z)]=ok
        print(u,len(Z),ok if not isinstance(ok,tuple) else ok[:2])
pickle.dump(res,open('sweep.pkl','wb'))
