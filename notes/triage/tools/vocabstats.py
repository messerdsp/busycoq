#!/usr/bin/env python3
"""Local-vocabulary growth from a tri.c log run with VOCAB=1 (simulation only).
Per decade of steps: the largest number of runs on the tape (S lines) and the number of 3-run windows (block and
count capped at 3) seen for the first time (V lines). A vocabulary that stops growing means the tape is built
from a finite set of local pieces over the whole range simulated; new windows in late decades mean new kinds of
structure keep appearing (as after 13's overflows). Windows are only tracked while the tape has fewer runs than
VOCABMAX (5000 by default), so a tape that outgrows it shows 'untracked'.
usage: vocabstats.py LOG.gz [VOCABMAX]"""
import gzip, math, sys
from collections import defaultdict
VM = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
runs = defaultdict(int); neww = defaultdict(int); last = []; total = 0
for l in gzip.open(sys.argv[1], 'rt'):
    if l[0] == 'S':
        a = l.split(); d = int(math.log10(max(1, int(a[1])))); runs[d] = max(runs[d], int(a[4]) + int(a[5]) + 1)
    elif l[0] == 'V':
        a = l.split('|', 1)[0].split(); d = int(math.log10(max(1, int(a[2]))))
        neww[d] += int(a[4]); total = int(a[3]); last.append((int(a[2]), int(a[4])))
print('decade  max_runs  new_windows')
for d in sorted(set(runs) | set(neww)):
    print('1e%-5d %9d %12s' % (d, runs.get(d, 0), neww.get(d, 0) if runs.get(d, 0) < VM else 'untracked'))
print('total windows %d; last new windows at steps: %s' % (total, ', '.join('%.3g (+%d)' % x for x in last[-5:])))
