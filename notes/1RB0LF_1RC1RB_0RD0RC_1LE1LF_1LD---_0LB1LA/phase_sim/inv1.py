import os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import M, Stuck, Halted
from m9 import T37
def parse_end(r):
    i = 0; tp = 1; n = len(r)
    while i < n:
        if tp == 0:
            w = tuple(r[i:i+4]) + (0,) * max(0, i + 4 - n)
            if w in ((0,0,0,0),(0,1,1,0)): i += 4
            elif w in ((0,0,1,1),(0,1,1,1)): i += 4; tp = 1
            else: return i, tp
        else:
            w = tuple(r[i:i+2]) + (0,) * max(0, i + 2 - n)
            if w == (1,1): i += 2
            elif w in ((0,0),(1,0)): i += 2; tp = 0
            else: return i, tp
    return n, tp
def ones_after(r, p):
    """positions of runs of length 1 that start at or after p (a run straddling p counts if it starts >= p-?)"""
    out = []; i = 0; n = len(r)
    while i < n:
        if r[i] == 1:
            j = i
            while j < n and r[j] == 1: j += 1
            if j - i == 1 and j > p: out.append(i)
            i = j
        else: i += 1
    return out
rnd = random.Random(int(sys.argv[1])); stats = collections.Counter(); ex = []
for trial in range(int(sys.argv[3])):
    m = M(T37, 11, 5, [1, 0]); n = 0
    try:
        while n < int(sys.argv[2]):
            n += 1
            r = list(m.buf[m.off:m.hi]); p, tp = parse_end(r)
            bad = ones_after(r, p)
            stats[(m.mode, 'bad' if bad else 'ok')] += 1
            if bad and len(ex) < 8: ex.append((m.mode, p, bad[:3], ''.join(map(str, r[max(0, p-6):p+12]))))
            if m.mode == 'R': m.mstep()
            else:
                u = rnd.random()
                m.b = 0 if u < 0.15 else rnd.randint(1, 3) if u < 0.5 else rnd.getrandbits(rnd.randint(2, 40))
                pre = list(m.buf[m.off:m.off + 3])
                if m.b == 0 and pre[:2] != [0, 0] and pre != [1, 0, 1] and pre[:2] != [1, 1]: m.b = rnd.randint(1, 5)
                m.mstep()
    except (Halted, Stuck) as e: stats['end ' + str(e)[:20]] += 1
print(dict(stats))
for e in ex: print(e)
