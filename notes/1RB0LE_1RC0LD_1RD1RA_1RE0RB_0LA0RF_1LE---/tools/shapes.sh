#!/bin/bash
# Run sweeps.py from many P(r; ds) starts and print the distinct passed-region shapes (tokens p* collapsed to T).
# Simulated.  Usage: shapes.sh STEPS N SEED
python3 - "$@" <<'PY'
import random,subprocess,sys,re,collections
steps,N,seed=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]); random.seed(seed)
M='1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
shapes=collections.Counter(); ex={}; ends=collections.Counter()
for i in range(N):
    j=random.choice([0,0,1,1,2,3]); r=6*j+6
    m=random.randint(2,40)
    ds=[2*random.choice([0,0,0,0,1,1,2,3])+1 for _ in range(m)]
    out=subprocess.run(['python3','sweeps.py',M,steps,'1000000','P',str(r),','.join(map(str,ds))],capture_output=True,text=True).stdout
    for line in out.splitlines():
        if line.startswith('HALT'): print('HALT!',r,ds); 
        if '|' not in line: continue
        ev=line.split()[1]; W=line.split('|',1)[1].strip()
        w=re.sub(r'p\d+(\^\d+)?','T',W); w=re.sub(r'(T ?)+','T* ',w).strip()
        shapes[(ev,w)]+=1; ex.setdefault((ev,w),(r,ds[:6],line[:160]))
for k,v in sorted(shapes.items(),key=lambda x:-x[1]): print(v,k,ex[k][2][:150])
PY
