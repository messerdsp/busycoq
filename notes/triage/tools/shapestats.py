#!/usr/bin/env python3
"""Structure statistics of a shape log (tri.c with SHAPE=1). Simulation only.
Per decade of steps:
  runs     largest number of runs on the tape (S lines): does the tape stay a short list of numbers?
  changes  shape changes at end returns (C lines)
  newwin   local windows (3 consecutive runs, each as block and count capped at 3; skeleton gaps as one token)
           seen for the first time in that decade: a finite, saturating vocabulary means a finite set of local
           rules; new windows late in the run mean new kinds of structure keep appearing.
usage: shapestats.py LOG.gz"""
import gzip, math, re, sys
from collections import defaultdict
TOK = re.compile(r'\[(\d+)\]|\(?([01]+)\)?(?:\^(\d+))?')
runs = defaultdict(int); chg = defaultdict(int); neww = defaultdict(int); seen = set(); last = None
for l in gzip.open(sys.argv[1], 'rt'):
    if l[0] == 'S':
        a = l.split(); d = int(math.log10(max(1, int(a[1]))))
        runs[d] = max(runs[d], int(a[4]) + int(a[5]) + 1)
    elif l[0] == 'C':
        h, t = l.split('|', 1); a = h.split(); d = int(math.log10(max(1, int(a[2]))))
        chg[d] += 1
        toks = []
        for m in TOK.finditer(t):
            if m.group(1): toks.append('G')
            else:
                c = int(m.group(3) or 1); toks.append('%s%d' % (m.group(2), min(c, 3)))
        for i in range(len(toks) - 2):
            w = tuple(toks[i:i + 3])
            if w not in seen: seen.add(w); neww[d] += 1
        last = a[2]
print('decade  max_runs  shape_changes  new_windows')
for d in sorted(set(runs) | set(chg)):
    print('1e%-5d %9d %14d %12d' % (d, runs.get(d, 0), chg.get(d, 0), neww.get(d, 0)))
print('total windows', len(seen), ' last shape change at step', last)
