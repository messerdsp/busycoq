"""Stronger over-approximation: before every macro step from cfgL', set b to a random value (often small, so
overflows happen at arbitrary times). Checks only the sweeps (carry windows); getting stuck at b = 0 just ends
the run."""
import os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import M, Stuck, Halted
from m9 import T37
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'carrycheck.py')).read().split('m = M(T37')[0])
seed, STEPS, NT = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rnd = random.Random(seed); misses = collections.Counter(); stats = collections.Counter()
for trial in range(NT):
    m = M(T37, 11, 5, [1, 0]); n = 0
    try:
        while n < STEPS:
            n += 1
            if m.mode == 'R':
                r0 = list(m.buf[m.off:m.hi])
                if r0 and r0[0] == 0: pr = r0[:]; pr[0] = 1; i = 0
                else: pr, i = carry_py(r0)
                m.mstep(); r1 = list(m.buf[m.off:m.hi])
                L = max(len(r1), len(pr) if pr else 0) + 8
                if pr is None or (list(pr) + [0] * L)[:L] != (r1 + [0] * L)[:L]:
                    key = ''.join(map(str, r0[max(0, i-4):i])) + '|' + ''.join(map(str, r0[i:i+8]))
                    misses[key] += 1; stats['miss'] += 1
                else: stats['ok'] += 1
            else:
                u = rnd.random()
                m.b = 0 if u < 0.15 else rnd.randint(1, 3) if u < 0.5 else rnd.getrandbits(rnd.randint(2, 40))
                pre = list(m.buf[m.off:m.off + 3])
                if m.b == 0 and pre[:2] != [0, 0] and pre != [1, 0, 1] and pre[:2] != [1, 1]: m.b = rnd.randint(1, 5)
                m.mstep()
    except Halted: stats['halt'] += 1
    except Stuck as e: stats['stuck ' + str(e)[:25]] += 1
print(dict(stats)); print(misses.most_common(20))
