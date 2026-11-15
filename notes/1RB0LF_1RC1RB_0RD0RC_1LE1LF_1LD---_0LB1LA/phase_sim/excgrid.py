"""At a real pre-excursion state, set the 4 runs above the bottom (A, B, C, D) to lengths with given parities and
record: how many runs the new bottom absorbs and whether the next run (future A) is a merged block or one old run."""
import os, sys, itertools, random
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
from align import align
st = load_state(sys.argv[1]); PRE = int(sys.argv[2]); rnd = random.Random(5)
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 1200, 1400)
while m0.nov < PRE: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list()); print('state', m0.nov, ' '.join(T0[:12]))
res = {}
for par in itertools.product((0, 1), repeat=4):
    outs = set()
    for rep in range(3):
        vals = [rnd.randrange(21, 61, 2) + (1 - p) * 0 + (0 if p else 1) for p in par]   # odd if p=1
        vals = [v if (v % 2 == p) else v + 1 for v, p in zip(vals, par)]
        T = list(T0)
        for j, v in enumerate(vals): T[3 + 2 * j] = 'o%d' % v
        m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 1200, 1400)
        while m.nov < m0.nov + 40: m.mstep()
        A = toks(m.r_list())
        X = [int(T[1][1:])] + vals + [int(t[1:]) for t in T[11:40:2]]
        Y = [int(t[1:]) for t in A[1:30:2]]
        # bottom absorbed: find k with Y[0] close to sum of X[1:k] (+ gaps), allowing the bottom's decrement
        bot = Y[0]; best = None
        for k in range(2, 6):
            s = sum(X[1:1 + k]) + 3 * (k - 1)
            if best is None or abs(bot - s) < abs(bot - best[1]): best = (k, s)
        k = best[0]
        o, err = align(X[1 + k:], Y[1:], D=4, J=8)
        first = len(o[0][0]) if o else None
        outs.add((k, first))
    res[par] = outs
    print('parities A,B,C,D =', par, '-> (runs absorbed, size of next block):', sorted(outs), flush=True)
