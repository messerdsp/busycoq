import os, sys, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
def capture(P, which=0):
    """state just before the (which)-th sweep in phase P that follows an INC1"""
    m = M(T37, 11, 5, [1, 0])
    while m.nov < P: m.mstep()
    n = 0; last = None
    while True:
        k = m.mstep()
        if k == 'INC1':
            if n == which: return m
            n += 1
        if k == 'OV': return None
if __name__ == '__main__':
    P = int(sys.argv[1]); w = int(sys.argv[2])
    m = capture(P, w)
    o = m.off; before = bytes(m.buf[o:m.hi + 8])
    m.sweep()
    after = bytes(m.buf[o:o + len(before)])
    d = [i for i in range(len(before)) if before[i] != after[i]]
    lo = max(0, min(d) - 6); hi = max(d) + 30
    big = [i for i in d if i > 8]
    lo = max(0, big[0] - 12); hi = big[-1] + 24
    print('changed cells (excluding the low end):', big[0], '..', big[-1], 'count', len(big))
    s = lambda b: ''.join(map(str, b[lo:hi]))
    print('before', s(before)); print('after ', s(after))
    low = [i for i in d if i <= 8]
    print('low-end changes', low, ' low digits region before', ''.join(map(str, before[:40])), ' after', ''.join(map(str, after[:40])))
