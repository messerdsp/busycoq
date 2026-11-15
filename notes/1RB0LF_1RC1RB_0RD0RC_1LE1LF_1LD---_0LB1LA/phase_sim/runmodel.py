import os, sys, time
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
import lowsim
from lowsim import load_state, toks, cells, fill
from model9 import Model
from m9 import T37
st = load_state(sys.argv[1]); P1 = int(sys.argv[2]); N = int(sys.argv[3]); K = N + 200; OUT = sys.argv[4]
T = toks(st['r'])[:N]
if T[-1][0] == 'z': T = T[:-1]
m = Model(T37, st['a'], fill(st['b'], K), cells(T)); m.mode = st['mode']; m.nov = st['nov']
out = open(OUT, 'w'); t0 = time.time()
while m.nov < P1:
    k = m.mstep()
    if k == 'OV':
        m.b = fill(m.b, K)
        out.write(f"{m.nov} {' '.join(toks(m.r_list())[:24])}\n")
        if m.nov % 500 == 0: print(m.nov, f'{time.time() - t0:.0f}s', dict(m.stats), flush=True)
print('end', m.nov, dict(m.stats))
