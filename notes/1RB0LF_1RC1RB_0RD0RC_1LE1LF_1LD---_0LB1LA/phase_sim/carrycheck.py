import sys, collections; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import M
from m9 import T37

def carry_py(r):
    """mirror of the Rocq carry: returns new r or None"""
    r = list(r) + [0] * 16; i = 0; tp = 1
    W0 = {(0,1,1,0,1,1,0,0):(0,0,1,1,1,1,0,0),(0,1,1,0,1,1,1,1):(0,0,1,1,1,1,1,1),(0,1,1,0,1,1,1,0):(0,0,1,1,1,1,1,0),
          (0,1,1,0,1,1,0,1):(0,0,1,1,1,1,0,1),(0,1,1,0,0,0,0,1):(0,0,0,0,0,1,1,1),(0,1,1,1,0,1,1,0):(0,0,1,1,1,1,1,0)}
    W1 = {(1,0,1,1,0,0):(1,1,1,1,0,0),(1,0,1,1,1,1):(1,1,1,1,1,1),(1,0,1,1,1,0):(1,1,1,1,1,0),(1,0,1,1,0,1):(1,1,1,1,0,1),
          (1,0,0,0,0,1):(0,0,0,1,1,1),(0,1,1,0):(1,1,1,0),(0,1,1,1):(1,1,1,1)}
    while True:
        if tp == 0:
            w = tuple(r[i:i+8])
            if w in W0: r[i:i+8] = W0[w]; return r, i
            if tuple(r[i:i+4]) == (0,1,1,0): r[i:i+4] = [0,0,0,0]; i += 4; continue
            if tuple(r[i:i+4]) == (0,1,1,1): r[i:i+4] = [0,0,1,1]; i += 4; tp = 1; continue
            if tuple(r[i:i+4]) == (0,0,0,0): r[i:i+4] = [0,1,1,0]; return r, i
            if tuple(r[i:i+4]) == (0,0,1,1): r[i:i+4] = [0,1,1,1]; return r, i
            return None, i
        else:
            for n in (6, 4):
                w = tuple(r[i:i+n])
                if w in W1: r[i:i+n] = W1[w]; return r, i
            if tuple(r[i:i+2]) == (1,1): i += 2; continue
            if tuple(r[i:i+2]) == (1,0): r[i:i+2] = [0,0]; i += 2; tp = 0; continue
            if tuple(r[i:i+2]) == (0,0): r[i:i+2] = [1,0]; return r, i
            return None, i
m = M(T37, 11, 5, [1, 0]); misses = collections.Counter(); first = None
while m.nov < int(sys.argv[1]):
    if m.mode == 'R':
        r0 = list(m.buf[m.off:m.hi])
        if r0 and r0[0] == 0: m.mstep(); continue
        pr, i = carry_py(r0)
        m.mstep(); r1 = list(m.buf[m.off:m.hi])
        if pr is None or pr[:len(r1)] != r1:
            # window around i
            key = ''.join(map(str, r0[max(0, i-4):i])) + '|' + ''.join(map(str, r0[i:i+8]))
            misses[(pr is None, key, m.nov)] += 1
            if first is None: first = (m.nmstep, m.nov, key)
    else: m.mstep()
print('first miss', first)
for k, v in sorted(misses.items(), key=lambda x: x[0][2])[:40]: print(v, k)
print(len(misses))
