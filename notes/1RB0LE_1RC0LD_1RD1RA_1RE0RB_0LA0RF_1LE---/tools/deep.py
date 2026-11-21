"""Search P(r; ds) starts for deep nesting (depth >= 3) with the C viewer; print starts reaching depth >= 3 and any halt.
Simulated.  Usage: deep.py N STEPS SEED"""
import random,subprocess,sys
N,steps,seed=int(sys.argv[1]),sys.argv[2],int(sys.argv[3]); random.seed(seed)
best=0
for i in range(N):
    j=random.choice([0,1,2,3,4]); r=6*j+6
    m=random.randint(20,600)
    mode=random.random()
    if mode<0.4: ds=[1]*m
    else: ds=[2*random.choice([0,0,0,0,0,1,1,2])+1 for _ in range(m)]
    out=subprocess.run(['./sweeps','P',str(r),','.join(map(str,ds)),steps,'0'],capture_output=True,text=True).stdout
    if 'HALT' in out: print('HALT', r, ds); sys.stdout.flush()
    d=0
    for line in out.splitlines():
        if 'depth=' in line: d=max(d,int(line.split('depth=')[1].split()[0]))
    if d>=3: print(f'depth {d}: r={r} m={m} mode={mode:.2f} first={ds[:5]}'); sys.stdout.flush()
    best=max(best,d)
print('max depth',best)
