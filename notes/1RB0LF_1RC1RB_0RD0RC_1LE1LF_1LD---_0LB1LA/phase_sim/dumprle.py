import os, sys, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
lo, hi = int(sys.argv[1]), int(sys.argv[2]); out = sys.argv[3]
def rle(B, i, e):
    res = []
    while i < e:
        j = i
        while j < e and B[j] == B[i]: j += 1
        res.append((B[i], j - i)); i = j
    return res
m = M(T37, 11, 5, [1, 0]); words = {}
while m.nov < hi:
    if m.mstep() == 'OV' and m.nov >= lo:
        words[m.nov] = (m.b, rle(m.buf, m.off, m.hi))
pickle.dump(words, open(out, 'wb'))
