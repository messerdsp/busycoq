#!/usr/bin/env python3
"""Drift test on a deep log (from deep.py): at the dominant return point, align consecutive tapes by their run
structure and report, for each position counted from the FAR end of the tape (the end away from the head), how
often its block/count changes between consecutive returns. Positions that never change are frozen; positions that
change rarely are rare events (overflows, refills); positions that change every return are the active counter.
usage: deep2.py DEEPLOG.gz SIDE STATE [NFAR] [SHOW]"""
import gzip, re, sys
from collections import Counter
log, side, st = sys.argv[1:4]
NFAR = int(sys.argv[4]) if len(sys.argv) > 4 else 12
SHOW = int(sys.argv[5]) if len(sys.argv) > 5 else 8
RUN = re.compile(r'([01]+)\^(\d+)|\[(\d+)\]|\(([01]+)\)|([01]+)')
def runs_of(t):
    out = []
    for m in RUN.finditer(t):
        if m.group(1): out.append((m.group(1), int(m.group(2))))
        elif m.group(3): out.append(('gap', int(m.group(3))))
        else: out.append((m.group(4) or m.group(5), 1))
    return out
recs = []
for l in gzip.open(log, 'rt'):
    if l[0] != 'E': continue
    h, t = l.split('|', 1); h = h.split()
    if h[1] == side and h[6] == st: recs.append((int(h[2]), runs_of(t)))
print('records', len(recs))
far = (lambda rr: rr[::-1]) if side == 'L' else (lambda rr: rr)
chg = Counter(); n = 0; events = []
for (s0, a), (s1, b) in zip(recs, recs[1:]):
    fa, fb = far(a), far(b); n += 1
    first = None
    for i in range(NFAR):
        x = fa[i] if i < len(fa) else None; y = fb[i] if i < len(fb) else None
        if x != y:
            chg[i] += 1
            if first is None: first = i
    if first is not None and first <= NFAR - 1: events.append((s1, first))
print('pairs', n, ' change counts by position from the far end:', [chg[i] for i in range(NFAR)])
deep = [e for e in events if e[1] <= 3]
print('returns where one of the 4 farthest runs changed: %d; first few steps:' % len(deep), [('%.3g' % s, i) for s, i in deep[:SHOW]])
for s, i in deep[-SHOW:]:
    r = [x for x in recs if x[0] == s][0]
    print('  %.4g' % s, ' '.join('%s^%s' % (b, c) if c != 1 else b for b, c in far(r[1])[:NFAR]))
