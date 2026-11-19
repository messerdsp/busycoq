#!/usr/bin/env python3
"""112769 (1RB0RA_1LC0LE_1RA1LD_0LB1LF_1LD0RC_1LB---), K = 6: at left-end returns in state B the tape is
(A) A^x 010010 A^3 010010 A^(x+11) 011100 (100100)^t TAIL with A = 011011: x counts up and the timer t counts down
by one per return, x + t constant within a phase. Print one line per phase: x + t and the tail word.
usage: phases112769.py LOG.gz [LOG.gz ...]"""
import gzip, re, sys
RUN = re.compile(r'([01]+)\^(\d+)|\(([01]+)\)|([01]+)')
seen = {}
for f in sys.argv[1:]:
    for l in gzip.open(f, 'rt'):
        if not (l.startswith('E L') and l.split()[6] == 'B'): continue
        h, t = l.split('|', 1)
        rr = [(m.group(1) or m.group(3) or m.group(4), int(m.group(2) or 1)) for m in RUN.finditer(t)]
        try: i = [b for b, c in rr].index('100100')
        except ValueError: continue
        if len(rr) < 3: continue
        x = rr[1][1]; tim = rr[i][1]
        tail = ' '.join('%s^%d' % (b, c) if c > 1 else b for b, c in rr[i + 1:])
        seen.setdefault(x + tim, (int(h.split()[2]), tail))
prev = None
for tot in sorted(seen):
    s, tail = seen[tot]
    print('%.4g' % s, tot, '' if prev is None else 'ratio %.5f  3*tot-8*prev=%d' % (tot / prev, 3 * tot - 8 * prev), '|', tail[:110])
    prev = tot
