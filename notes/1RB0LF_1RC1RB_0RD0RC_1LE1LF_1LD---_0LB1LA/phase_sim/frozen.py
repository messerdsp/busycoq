"""From a checkpoint, run K phases and report which run indices ever change (the frozen low region)."""
import sys, pickle
sys.path.insert(0, '/home/user/m9')
from msim import *
st = pickle.load(open(sys.argv[1], 'rb')); K = int(sys.argv[2])
m = M(T37, st['a'], st['b'], st['r']); m.mode = st['mode']; m.nov = st['nov']
def rle(r):
    out = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        out.append((r[i], j - i)); i = j
    return out
R0 = rle(m.r_list())
print('phase', m.nov, 'runs', len(R0), 'cells', sum(n for _, n in R0))
prev = R0
for k in range(K):
    P = m.nov
    while m.nov == P: m.mstep()
    R = rle(m.r_list())
    # align: bottom run loses one cell; compare runs index-wise
    ch = [i for i in range(1, min(len(R), len(prev))) if R[i] != prev[i]]
    first = ch[:12]
    print(m.nov, 'bottom', R[0], R[1], 'changed idx', first, '... n', len(ch))
    prev = R
pickle.dump(R0, open(sys.argv[1] + '.rle', 'wb'))
