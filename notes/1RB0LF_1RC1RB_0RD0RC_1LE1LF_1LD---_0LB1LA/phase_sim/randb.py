"""Over-approximation test of the local invariant: run the macro model (21-lemma sweeps, STRICT) from the blank-tape
start, but replace b by a random number of the same bit length (or random length) at every overflow.
Report any sweep that is not S_0 or a carry covered by the 21 lemmas."""
import os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import M, Stuck, Halted
from m9 import T37
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'carrycheck.py')).read().split('m = M(T37')[0]
exec(src)              # defines carry_py
seed = int(sys.argv[1]); PH = int(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else 'same'
rnd = random.Random(seed); misses = collections.Counter(); stats = collections.Counter()
for trial in range(int(sys.argv[4]) if len(sys.argv) > 4 else 20):
    m = M(T37, 11, 5, [1, 0])
    try:
        while m.nov < PH:
            if m.mode == 'R':
                r0 = list(m.buf[m.off:m.hi])
                if r0 and r0[0] == 0:
                    pr = r0[:]; pr[0] = 1; i = 0
                else:
                    pr, i = carry_py(r0)
                m.mstep(); r1 = list(m.buf[m.off:m.hi])
                L = max(len(r1), len(pr) if pr else 0) + 8
                if pr is None or (list(pr) + [0] * L)[:L] != (r1 + [0] * L)[:L]:
                    key = ''.join(map(str, r0[max(0, i-4):i])) + '|' + ''.join(map(str, r0[i:i+8]))
                    misses[key] += 1; stats['miss'] += 1
                else: stats['ok'] += 1
            else:
                k = m.mstep()
                if k == 'OV':
                    L = m.b.bit_length()
                    m.b = rnd.getrandbits(L) | (1 << (L - 1)) if mode == 'same' else rnd.getrandbits(rnd.randint(2, L + 2)) + 1
    except Halted as e: stats['halt'] += 1
    except Stuck as e: stats['stuck ' + str(e)[:30]] += 1
print(dict(stats)); print(misses.most_common(30))
