"""Vary the runs at the lowest wave front of a real state and run one phase; report how the outcome depends on
the run lengths. usage: frontexp.py STATE PHASES_AHEAD NRUNS VALUES (e.g. 5,6,7,8,105,106)"""
import os
import sys, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state
from align import align
st = load_state(sys.argv[1]); AH = int(sys.argv[2]); NR = int(sys.argv[3]); VALS = [int(v) for v in sys.argv[4].split(',')]; OFF = int(sys.argv[5]) if len(sys.argv) > 5 else 0
N, K = 700, 900
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
while m0.nov < st['nov'] + AH: m0.mstep()
while m0.mode != 'R': m0.mstep()          # phase start (after OV the mode is R)
T0 = toks(m0.r_list()); a0, b0, nov0 = m0.a, m0.b, m0.nov
fr = next(i for i in range(2, len(T0)) if T0[i][0] == 'z' and T0[i] != 'z3')
print('phase', nov0, 'front at token', fr, ':', ' '.join(T0[fr - 4:fr + 2 * NR + 4]))
def one(vals):
    T = list(T0)
    for k, v in enumerate(vals): T[fr + 1 + 2 * (k + OFF)] = 'o%d' % v
    m = trunc_state(a0, b0, cells(T), 'R', nov0, N, K)
    while m.nov == nov0: m.mstep()
    A = toks(m.r_list())
    return T, A
def describe(T, A):
    # tokens from fr-2 on: compare run lists; bottom shrinks by one so start after the bottom
    lo = fr - 2 + 2 * min(OFF, 0)
    X = [int(t[1:]) for t in T[lo + 1:lo + 1 + 2 * (NR + 6):2]]; G = T[lo:lo + 2 * (NR + 6):2]
    Y = [int(t[1:]) for t in A[lo + 1:lo + 1 + 2 * (NR + 6):2]]; H = A[lo:lo + 2 * (NR + 6):2]
    o, err = align(X, Y[:-1], D=4, J=6)
    return ' '.join(f"{len(g)}{'%+d' % d if d else ''}" for g, d, y in o[:NR + 2]) + ' | gaps ' + ' '.join(H[:NR + 3])
res = collections.defaultdict(list)
for vals in itertools.product(VALS, repeat=NR):
    T, A = one(vals)
    res[describe(T, A)].append(vals)
for d, vs in sorted(res.items(), key=lambda a: -len(a[1])):
    par = sorted(set(tuple(v % 2 for v in x) for x in vs))
    print(f'{len(vs):4d}  {d:60s} parities {par if len(par) < 9 else "many"}  e.g. {vs[:3]}')
