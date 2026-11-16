import re, sys, collections
D=['01010101010101','0101010101111111','011111110101010101','01111111010101111111']
NXT={0:2,2:1,1:3,3:0}
U1={}
rows=[]
for line in open(sys.argv[1]):
    k,pos,s=line.split(); s=s[15:]
    parts=re.split(r'((?:011101){4,})', s)
    units=[]
    for u in range(1,len(parts)-2,2):
        seg=parts[u+1]; kk=len(parts[u])//6
        if u==1: units.append((kk,seg)); continue
        ph=max((j for j in range(4) if seg.startswith(D[j])), key=lambda j:len(D[j]), default=None)
        units.append((kk,ph,seg[len(D[ph]):] if ph is not None else seg))
    rows.append((int(k),int(pos),units))
# unit 1 cycle
seq=[r[2][0][1] for r in rows[:12]]
print([len(x) for x in seq])
order=[]; 
for x in seq:
    if x not in order: order.append(x)
nx={order[i]:order[(i+1)%len(order)] for i in range(len(order))}
print('unit1 heads', len(order))
bad=0; checked=0; ex=collections.Counter()
for (t0,p0_,a),(t1,p1_,b) in zip(rows,rows[1:]):
    n=min(len(a),len(b),10)
    # unit 1
    k0,s0=a[0]; k1,s1=b[0]
    ex[('u1',len(s0),len(s1),k1-k0)]+=1
    carry = len(s0)==38
    for j in range(1,n):
        k0,q0,tl0=a[j]; k1,q1,tl1=b[j]
        if q0 is None or q1 is None: break
        if carry: exp=(k0+(1 if q0 in (2,3) else 0), NXT[q0], tl0); carry= q0==3
        else: exp=(k0,q0,tl0)
        checked+=1
        if (k1,q1,tl1)!=exp:
            bad+=1
            if bad<8: print('mismatch',t0,j,(k0,q0,len(tl0)),(k1,q1,len(tl1)))
print('checked',checked,'bad',bad,'rounds',len(rows)); print(ex)
