"""Exact halting criterion at an excursion: from the real state just before an excursion, set the run next to the
bottom (A) and the one after (B) to given lengths and run the machine for a while."""
import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
from msim import Halted, Stuck
st = load_state(sys.argv[1]); PRE = int(sys.argv[2])
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 2000, 2200)
while m0.nov < PRE: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list()); print('state at', m0.nov, ' '.join(T0[:10]))
def trial(A, B):
    T = list(T0); T[3] = 'o%d' % A; T[5] = 'o%d' % B
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 2000, 2200)
    try:
        while m.nov < m0.nov + 40: m.mstep()
        return 'ok   ' + ' '.join(toks(m.r_list())[:6])
    except Halted as e: return 'HALT ' + str(e)[:60]
    except Stuck as e: return 'stuck ' + str(e)[:60]
for A in list(range(1, 15)) + [99, 100]:
    print('A', A, ':', trial(A, 2235), ' | with B=2236:', trial(A, 2236)[:5])
