"""Summarize excursions from a lowsim run: phase, run above the bottom, bottom 10 phases later. Flags runs <= 6."""
import sys
L = {}
for l in open(sys.argv[1]):
    p, *t = l.split()
    if p.isdigit(): L[int(p)] = t
    else: print(l.strip())
seen = set()
for l in open(sys.argv[1] + '.exc'):
    w = l.split()
    if w[0] == 'JUMP': continue
    p = int(w[0])
    if w[1].startswith('z') and w[1] != 'z2' and p not in seen and p - 1 not in seen:
        seen.add(p); nxt = int(w[2][1:]); later = L.get(p + 10, ['?', '?'])
        print(f"{p:>16} next_run {nxt:>8} bottom@+10 {later[1]:>9} {'<<< SHORT' if nxt <= 6 else ''}")
