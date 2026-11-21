"""Generate start configurations for exh.c.  Usage: gen_exh.py outer RMAX MMAX DMAX | gen_exh.py inner ..."""
import sys,itertools
mode=sys.argv[1]
if mode=='outer':
    RMAX,MMAX,DMAX=map(int,sys.argv[2:5])
    for ph in 'PQ':
        for r in range(3,RMAX+1,3):
            for m in range(0,MMAX+1):
                for ds in itertools.product(range(DMAX+1),repeat=m):
                    print(ph,r,','.join(map(str,ds)) or '-')
else:
    RMAX,MMAX,DMAX,BMAX=map(int,sys.argv[2:6])
    B=lambda n:'00'+'10'*n
    blocks=[B(1),B(1)+'110',B(2),B(5),B(8)]
    Ws=[]
    for i in (0,1):
        for b in range(BMAX+1):
            for bs in itertools.product(blocks,repeat=b):
                Ws.append('101010'*i+''.join(bs)+'001')
    for ph in 'XY':
        for r in range(3,RMAX+1,3):
            for m in range(0,MMAX+1):
                for ds in itertools.product(range(DMAX+1),repeat=m):
                    for w in Ws: print(ph,r,','.join(map(str,ds)) or '-',w)
