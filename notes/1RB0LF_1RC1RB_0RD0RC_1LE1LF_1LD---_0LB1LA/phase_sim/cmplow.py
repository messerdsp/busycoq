import sys
R={}
for l in open(sys.argv[1]):
    p,*t=l.split()
    if p.isdigit(): R[int(p)]=t
ok=0; n24=int(sys.argv[3]) if len(sys.argv)>3 else 24
for l in open(sys.argv[2]):
    p,*t=l.split()
    if not p.isdigit(): print(l.strip()); continue
    p=int(p)
    if p in R:
        n=min(len(t),len(R[p]),n24)
        if R[p][:n]!=t[:n]: print('DIFF',p,t[:8],R[p][:8]); break
        ok+=1
print('phases compared, all equal:',ok)
