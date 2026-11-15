import sys
exec(open('units.py').read().split("rows=[]")[0])
prev=None
for line in sys.stdin:
    k,st,s=line.split()
    if st!='B': continue
    p=split(s)
    desc=' | '.join(str(x) if isinstance(x,int) else '[%d]'%len(x) for x in p)
    print(k, len(s), desc, flush=True)
