"""Controlled tabulation of the wave step. At each phase start in [P0, P1) with a visible front, set the run
below the front (W) and the three above (X1..X3) to every parity combination (lengths 9/10 + JIT jitter), run one
phase, and record the outcome. Then check: is the outcome a function of (phase parity, start-cell parity, gap
tokens around the front, the 4 parities)?   usage: tabfront.py STATE P0 P1 OUT"""
import os, sys, itertools, collections, pickle, random
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
from align import align
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3]); OUT = sys.argv[4]
N, K = 700, 900; rnd = random.Random(1)
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
rows = []
def outcome(T, A, lo, n=7):
    X = [int(t[1:]) for t in T[lo + 1:lo + 1 + 2 * (n + 4):2]]; Y = [int(t[1:]) for t in A[lo + 1:lo + 1 + 2 * (n + 4):2]]
    o, err = align(X, Y[:-1], D=4, J=6)
    out = []; c = 0
    for g, d, y in o:
        if c >= n: break
        out.append(f"{len(g)}{'%+d' % d if d else ''}"); c += len(g)
    return ' '.join(out) + ' | ' + ' '.join(A[lo:lo + 2 * len(out) + 2:2])
while m0.nov < P1:
    while m0.mode != 'R': m0.mstep()
    if m0.nov >= P0:
        T0 = toks(m0.r_list())
        fr = next((i for i in range(2, len(T0)) if T0[i][0] == 'z' and T0[i] != 'z3'), None)
        if fr is not None and 8 < fr < N - 150:
            a0, b0, nov0 = m0.a, m0.b, m0.nov
            lo = fr - 4
            gaps = ' '.join(T0[fr - 4:fr + 10:2])
            for par in itertools.product((0, 1), repeat=4):
                T = list(T0)
                for k, q in enumerate(par): T[fr - 1 + 2 * k] = 'o%d' % (9 + 2 * rnd.randint(0, 3) + (1 - q))  # odd if q=1
                pos = sum(int(t[1:]) for t in T[:fr - 1]) % 4
                m = trunc_state(a0, b0, cells(T), 'R', nov0, N, K)
                while m.nov == nov0: m.mstep()
                A = toks(m.r_list())
                ctx = tuple(int(T0[j][1:]) % 2 for j in (fr - 5, fr - 3, fr + 7, fr + 9, fr + 11))
                rows.append((nov0, nov0 % 2, pos, gaps, par, outcome(T, A, lo), ctx, T0[1]))
            print(nov0, fr, gaps, flush=True)
    m0.mstep()
pickle.dump(rows, open(OUT, 'wb'))
