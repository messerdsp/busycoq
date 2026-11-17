import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m9 import *

TM = TM2 if sys.argv[1:] == ['tm2'] else T37   # "tm2": run the same checks on SBCv9.v TM2

def mk(left, right, off):
    """left stream ends at off-1 going left, right starts at off"""
    t = {}
    for i, s in enumerate(left): t[off - 1 - i] = s
    for i, s in enumerate(right): t[off + i] = s
    return t

def lemma(tm, start, pos0, st0, end, pos1, st1):
    t = dict(start)
    try:
        p, s, n = run_until(tm, t, pos0, st0, lambda p, s: p == pos1 and s == st1, 10**6)
    except Halt as h:
        return 'HALT'
    except RuntimeError:
        return 'LIMIT'
    return 'ok' if norm(t) == norm(end) else 'DIFF'

random.seed(1)
res = {}
for a in range(0, 16):
    for b in range(0, 6):
        r = [random.randint(0, 1) for _ in range(8)]
        out = {}
        # LInc: LC a (1+b) hL' r -> LC (4+a) b hR' r      (r at pos 3)
        out['LInc'] = lemma(TM, mk(LC(a, b + 1), [0, 1, 1] + r, 0), -1, 'D', mk([1, 0, 1] + LC(a + 4, b), r, 3), 3, 'A')
        # LOv (a=1+2c, b=0): LC (1+2c) 0 hL' [0;0] r -> LC 3 (2+c) hR' [0] r   (r at pos 5)
        if a % 2 == 1 and b == 0:
            c = (a - 1) // 2
            out['LOv'] = lemma(TM, mk(LC(a, 0), [0, 1, 1, 0, 0] + r, 0), -1, 'D', mk([1, 0, 1] + LC(3, 2 + c), [0] + r, 4), 4, 'A')
        # LRst_101: LC a b hL' [1;0;1] r -> LC (4+a) b hL' [1] r   (r at pos 6)
        out['LRst_101'] = lemma(TM, mk(LC(a, b), [0, 1, 1, 1, 0, 1] + r, 0), -1, 'D', mk(LC(a + 4, b), [0, 1, 1, 1] + r, 2), 1, 'D')
        # LRst_11: LC a b hL' [1;1] r -> LC (4+a) b hR' r   (r at pos 5)
        out['LRst_11'] = lemma(TM, mk(LC(a, b), [0, 1, 1, 1, 1] + r, 0), -1, 'D', mk([1, 0, 1] + LC(a + 4, b), r, 5), 5, 'A')
        for k, v in out.items(): res.setdefault((k, a % 2, v), 0); res[(k, a % 2, v)] += 1
for k in sorted(res): print(k, res[k])
