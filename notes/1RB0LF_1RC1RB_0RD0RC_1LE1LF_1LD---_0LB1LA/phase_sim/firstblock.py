"""At each excursion (bottom token != z3 -> merges), compare the runs above the bottom just before with those 12
phases after: report how the wave grouped the first few old runs.  usage: firstblock.py LOWLOG (plain or .gz)"""
import sys, gzip
from align import align
f = gzip.open(sys.argv[1], 'rt') if sys.argv[1].endswith('.gz') else open(sys.argv[1])
rows = {}
for l in f:
    T = l.split()
    if len(T) > 1 and T[0].isdigit(): rows[int(T[0])] = T[1:]
ph = sorted(rows); exc = [p for p in ph if rows[p][0] != 'z3' and rows.get(p - 1, ['z3'])[0] == 'z3' and p - 1 in rows]
for p in exc:
    old = rows[p - 1]; new = rows.get(p + 12)
    if new is None or p - 1 < 30: continue
    seps_old = old[0::2]; X = [int(t[1:]) for t in old[7::2] if t[0] == 'o']; Y = [int(t[1:]) for t in new[3::2] if t[0] == 'o']
    # only runs below the wave front in NEW
    fr = next((i for i in range(2, len(new)) if new[i][0] == 'z' and new[i] != 'z3'), len(new))
    Y = [int(t[1:]) for t in new[3:fr:2]]
    Xall = [int(t[1:]) for t in old[3::2] if t[0] == 'o']
    best = None
    for absorb in range(2, 8):          # the new bottom absorbs `absorb` old runs (A, B, ...)
        o, err = align(Xall[absorb:], Y, D=3, J=12)
        if best is None or len(o) > len(best[1]): best = (absorb, o, err)
    p_abs, o, err = best
    print(p, 'absorb', p_abs, 'old', ' '.join(old[:9]), '| groups', [(len(a[0]), a[1]) for a in o], 'new', ' '.join(new[:4]), '' if err is None else err)
