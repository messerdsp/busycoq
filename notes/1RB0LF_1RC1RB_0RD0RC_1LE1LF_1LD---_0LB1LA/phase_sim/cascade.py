import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state, fill
st = load_state(sys.argv[1]); PRE = int(sys.argv[2]); vals = [int(x) for x in sys.argv[3].split(',')]; PH = int(sys.argv[4])
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 1200, 1400)
while m0.nov < PRE or toks(m0.r_list()[:100000])[1] != "o4":
    k = m0.mstep()
    if k == "OV": m0.b = fill(m0.b, 1400)
while m0.mode != 'R': m0.mstep()
T = toks(m0.r_list())
for j, v in enumerate(vals): T[3 + 2 * j] = 'o%d' % v
m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 1200, 1400)
print(m.nov, ' '.join(T[:16]))
while m.nov < m0.nov + PH:
    if m.mstep() == 'OV':
        m.b = fill(m.b, 1400); print(m.nov, ' '.join(toks(m.r_list()[:100000])[:16]), flush=True)
