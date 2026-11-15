"""Locality test: truncate r after N tokens, run K phases, compare low tokens with the full run's dump."""
import os
import sys, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
def toks(r):
    out = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        out.append(('o' if r[i] else 'z') + str(j - i)); i = j
    return out
def cells(tk):
    r = []
    for t in tk: r += [1 if t[0] == 'o' else 0] * int(t[1:])
    return r
st = pickle.load(open(sys.argv[1], 'rb')); N = int(sys.argv[2]); K = int(sys.argv[3]); bmode = sys.argv[4] if len(sys.argv) > 4 else 'keep'
T = toks(st['r'])[:N]
if T[-1][0] == 'z': T = T[:-1]
b = st['b'] if bmode == 'keep' else (2**int(bmode[1:]) - 3 if bmode[0] == 'p' else (st['b'] % 2**int(bmode[1:]) + 2**int(bmode[1:]) * (2**1000 - 1) if bmode[0] == 'm' else int(bmode)))
m = M(T37, st['a'], b, cells(T)); m.mode = st['mode']; m.nov = st['nov']
t0 = time.time()
for k in range(K):
    P = m.nov
    while m.nov == P: m.mstep()
print('time', time.time() - t0, 'phase', m.nov, 'b_bits', m.b.bit_length())
pickle.dump(toks(m.r_list()), open(sys.argv[5] if len(sys.argv) > 5 else 'trunc.out', 'wb'))
ref = None
import gzip
REF = os.environ.get('REFLOW', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'model_pure_10000_29438.txt.gz'))
for line in (gzip.open(REF, 'rt') if REF.endswith('.gz') else open(REF)):
    p, *rest = line.split()
    if int(p) == m.nov: ref = rest
R = toks(m.r_list())
if ref:
    n = min(len(R), len(ref)); d = [i for i in range(n) if R[i] != ref[i]]
    print('compared', n, 'first diff', d[:5], R[d[0]-2:d[0]+4] if d else '', ref[d[0]-2:d[0]+4] if d else '')
