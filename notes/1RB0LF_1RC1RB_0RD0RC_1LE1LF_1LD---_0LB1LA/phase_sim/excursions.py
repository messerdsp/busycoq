"""List excursions from a run37 .low file: phase where the low end reads z2 o2, the run above the bottom just
before it, and the new bottom run once it erodes steadily again."""
import sys
L = {}
for line in open(sys.argv[1]):
    f = line.split(); L[int(f[0])] = f[1:]
def bottom(p): return int(L[p][1][1:]) if p in L and len(L[p]) > 1 and L[p][1][0] == 'o' else None
print('| phase | run above the bottom | new bottom |')
print('|---|---|---|')
for p in sorted(L):
    if p < 80 or L[p][:2] != ['z2', 'o2']: continue
    prev = L.get(p - 2, [])
    a1 = prev[3] if len(prev) > 3 and prev[:2] == ['z3', 'o2'] else '?'
    nb = '(not yet)'
    for q in range(p + 1, p + 60):
        b0, b1, b2 = bottom(q), bottom(q + 1), bottom(q + 2)
        if None not in (b0, b1, b2) and b1 == b0 - 1 and b2 == b0 - 2:
            nb = f'{b0} (phase {q})'; break
    print(f'| {p:,} | {a1[1:]} | {nb} |')
