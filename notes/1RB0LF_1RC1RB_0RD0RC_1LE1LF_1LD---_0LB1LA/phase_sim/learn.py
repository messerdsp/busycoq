"""From synthetic alignments (#B lines: block size, delta, old runs), find how much history determines each gap
decision. Event per old run i: parity p_i, filled f_i (gap after run i joined), and the block delta at block ends."""
import sys, collections
seqs = []
for f in sys.argv[1:]:
    ev = []
    for l in open(f):
        if not l.startswith('#B'): continue
        _, n, d, *g = l.split(); n = int(n); d = int(d); g = list(map(int, g))
        for q, v in enumerate(g): ev.append([v % 2, 1 if q < n - 1 else 0, d if q == n - 1 else None, v])
    # absolute old position mod 4 of each run start, and the shift so far (sum of earlier block deltas) mod 4
    pos = 0; sh = 0
    for e in ev:
        e.append(pos % 4); e.append(sh % 4)
        pos += e[3] + 3
        if e[2] is not None: sh += e[2]
    seqs.append([tuple(e) for e in ev[3:]])            # skip the runs below the front and the first block
def test(kp, kf, ahead, target):
    tab = collections.defaultdict(collections.Counter)
    for ev in seqs:
        for i in range(max(kp, kf), len(ev) - ahead - 1):
            key = (tuple(e[0] for e in ev[i - kp + 1:i + 1 + ahead]), tuple(e[1] for e in ev[i - kf:i]), ev[i][4] if POS else 0, ev[i][5] if SH else 0,
                   tuple(e[2] for e in ev[i - kf:i]) if target == 'delta' else ())
            val = ev[i][1] if target == 'fill' else (ev[i][1], ev[i][2])
            tab[key][val] += 1
    bad = sum(1 for c in tab.values() if len(c) > 1)
    return len(tab), bad, sum(sum(c.values()) for c in tab.values())
import os
POS = 'POS' in os.environ; SH = 'SH' in os.environ
for target in ('fill', 'delta'):
    print(target)
    for ahead in (0, 1, 2):
        for kp in (1, 2, 3, 4):
            for kf in (0, 1, 2, 3, 4):
                keys, bad, n = test(kp, kf, ahead, target)
                if bad == 0: print(f'  ahead {ahead} parities back {kp} decisions back {kf}: keys {keys} samples {n} DETERMINISTIC')
                elif kf == 4 and kp == 4: print(f'  ahead {ahead} kp4 kf4: keys {keys} nondet {bad}')
