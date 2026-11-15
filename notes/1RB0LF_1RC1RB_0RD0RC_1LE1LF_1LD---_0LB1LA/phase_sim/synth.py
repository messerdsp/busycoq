"""Put random runs (lengths in [LO, HI], all gaps z3) above the lowest wave of a real state, let the wave cross
them, and record per old gap whether it was filled (joined) and how far it moved.
usage: synth.py STATE SEED NRUNS PHASES LO HI > out"""
import os, sys, random
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state
st = load_state(sys.argv[1]); seed, NR, PH, LO, HI = map(int, sys.argv[2:7]); rnd = random.Random(seed)
N0 = 120 + 2 * NR + 200; K = N0 + 200
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N0, K)
while True:                                   # advance to a phase start with a visible front marker
    while m.mode != 'R': m.mstep()
    T = toks(m.r_list())
    fr = next((i for i in range(2, len(T)) if T[i][0] == 'z' and T[i] != 'z3'), None)
    if fr is not None: break
    m.mstep()
start = fr + 4                               # keep the front and two runs above it as they are
old = [rnd.randint(LO, HI) for _ in range(NR)]
T2 = T[:start] + sum((['z3', 'o%d' % v] for v in old), [])[0:] + T[start + 2 * NR:]
T2 = T2[:start] + ['z3' if t[0] == 'z' else t for t in T2[start:start + 2 * NR]] + T2[start + 2 * NR:]
for k, v in enumerate(old): T2[start + 1 + 2 * k] = 'o%d' % v
m = trunc_state(m.a, m.b, cells(T2), 'R', m.nov, N0, K)
nov0 = m.nov
PL = open(os.environ['PHASELOG'], 'w') if os.environ.get('PHASELOG') else None
while m.nov < nov0 + PH:
    k = m.mstep()
    if PL and k == 'OV': PL.write(f"{m.nov} {' '.join(toks(m.r_list())[:start + 2 * NR])}\n")
while m.mode != 'R': m.mstep()
A = toks(m.r_list())
# cell position (from the start of the run list at index `start`) of each old gap, and of each new gap
base_old = sum(int(t[1:]) for t in T2[:start]); base_new = sum(int(t[1:]) for t in A[:start])
# find where the synthetic region starts in A: the runs below start may have been joined, so locate by cells.
pos = 0; old_gaps = []
for k, v in enumerate(old):
    pos += 3 + v; old_gaps.append(pos)               # gap after old run k starts at this offset
cum = 0; new_gaps = {}; i = 0
while i < len(A):
    cum += int(A[i][1:])
    if A[i][0] == 'o' and i + 1 < len(A) and A[i + 1][0] == 'z': new_gaps[cum - base_old] = A[i + 1]
    i += 1
# the bottom run shrinks by PH cells? positions are measured from the tape start, which moves; estimate the offset
print('#', ' '.join(T2[start - 8:start + 8]), '->', ' '.join(A[start - 8:start + 8]))
print('#OLD', ' '.join(map(str, old)))
print('#NEW', ' '.join(A[start - 8:start + 2 * NR]))
from align import align
X = [int(t[1:]) for t in T2[start - 7:start + 2 * NR:2]]     # from the unchanged run 2 below the front
Y = [int(t[1:]) for t in A[start - 7:start + 2 * NR:2]]
o, err = align(X, Y, D=4, J=40)
print('#ALIGN blocks', len(o), 'of old', sum(len(g) for g, d, y in o), 'err', err)
for g, d, y in o:
    print('#B', len(g), d, ' '.join(map(str, g)))
