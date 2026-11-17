"""Run one phase from a real phase-start word with the runs at the lowest wave front replaced, and report the
local result. Usage: waveexp.py PHASE IDX  (IDX = index in the RLE list of the first run to vary)."""
import os, sys, pickle, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
P = int(sys.argv[1]); I = int(sys.argv[2])
base = M(T37, 11, 5, [1, 0])
while base.nov < P: base.mstep()
a0, b0, mode0 = base.a, base.b, base.mode
r0 = base.r_list()
def rle(r):
    out = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        out.append([r[i], j - i]); i = j
    return out
R = rle(r0)
fmt = lambda s: ' '.join(('o' if v else 'z') + str(n) for v, n in s)
print('window', fmt(R[I - 2:I + 7]))
def run(lengths):
    RR = [list(x) for x in R]
    for k, L in enumerate(lengths): RR[I + 2 * k][1] = L
    r = []
    for v, n in RR: r += [v] * n
    m = M(T37, a0, b0, r); m.mode = mode0; m.nov = P
    try:
        while m.nov == P: m.mstep()
    except (Halted, Stuck) as e:
        return 'STOP ' + str(e)[:40]
    S = rle(m.r_list())
    # locate: the run before the window is R[I-2] (unchanged, minus the bottom shift); find it by content
    return fmt(S[I - 2:I + 7])
vals = [[int(v) for v in g.split(",")] for g in sys.argv[3].split("/")]
for combo in itertools.product(*vals):
    print(combo, '->', run(list(combo)))
