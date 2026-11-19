#!/usr/bin/env python3
"""Phase map of a timer machine: at returns to the given end in the given state, take the tape's runs; within a
phase two given runs (indexes I, J, counted from the far end) have a constant sum (I counts up, J counts down).
Print one line per phase: the sum, every other run count, and 3*S' - 8*S style residues are left to the reader.
usage: phases_generic.py SIDE STATE I J LOG.gz [LOG.gz ...]"""
import gzip, re, sys
side, st, I, J = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
RUN = re.compile(r'([01]+)\^(\d+)|\(([01]+)\)|([01]+)')
ph = {}
for f in sys.argv[5:]:
    for l in gzip.open(f, 'rt'):
        if not l.startswith('E ' + side) or l.split()[6] != st: continue
        h, t = l.split('|', 1)
        rr = [(m.group(1) or m.group(3) or m.group(4), int(m.group(2) or 1)) for m in RUN.finditer(t)]
        if side == 'L': rr = rr[::-1]
        if len(rr) <= max(I, J): continue
        S = rr[I][1] + rr[J][1]
        rest = tuple((b, c) for k, (b, c) in enumerate(rr) if k not in (I, J))
        key = (S, rest)
        ph.setdefault(S, (int(h.split()[2]), rr[I][0], rr[J][0], rest))
prev = None
for S in sorted(ph):
    s, bi, bj, rest = ph[S]
    print('%.4g S=%d' % (s, S), '' if not prev else 'S/prev=%.5f' % (S / prev), '|', ' '.join('%s^%d' % (b, c) if c > 1 else b for b, c in rest)[:150])
    prev = S
