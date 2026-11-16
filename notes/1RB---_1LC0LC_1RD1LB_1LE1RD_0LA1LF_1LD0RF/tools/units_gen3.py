import sys, collections, pickle
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from genlemmas import lemma
ctx=collections.defaultdict(set)
for l in open(sys.argv[1]):
    u,_,c=l.split(); ctx[int(u)].add(c)
by={}
for u in sorted(ctx):
    st=collections.OrderedDict()
    for c in sorted(ctx[u]):
        kind,lem=lemma('X',c)
        st.setdefault(lem,kind)
    by[u]=st
    print(u, len(ctx[u]), len(st), collections.Counter(st.values()), flush=True)
pickle.dump(by,open('by3.pkl','wb'))
