import re
from endlib import Wd
from gunit2 import ok
from utypes import cells
import hashlib
res=[]
for fn in open('files2.lst').read().split():
    if not fn.endswith('_00.txt') or fn.startswith(('r1','r2','m15_01')): continue
    s=cells(fn).split('BANDBAND')[0]
    parts=re.split(r'((?:011101){3,})', s[9:])
    segs=[(len(parts[u])//6, parts[u+1]) for u in range(1,len(parts),2)]
    # end region: everything after the last validated unit (cut form, walls >= 20 words written as X)
    k=len(segs)
    while k>1 and not ok(8,segs[k-1][1]): k-=1
    E=''.join(Wd*w+b for w,b in segs[k:])
    En=re.sub(r'(?:011101){20,}','X',E)
    res.append((fn,len(E),hashlib.md5(En.encode()).hexdigest()[:8], En.replace(Wd,' W')[:90]))
from collections import Counter
c=Counter(h for _,_,h,_ in res)
for fn,L,h,e in res: print(fn, L, h, c[h], e)
print(len(res),'post-overflow end regions,',len(c),'distinct')
