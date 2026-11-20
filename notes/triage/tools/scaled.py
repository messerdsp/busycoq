#!/usr/bin/env python3
"""Scaled-down restarts (simulation, heuristic), as in 13's notes: take the last logged full tape of the real run,
divide every run of count >= 3 by F (keeping its residue mod MOD, with a jitter of -1, 0 or +1 times MOD), and run
the accelerated simulator tri.c from there (INIT). Worn-down blocks then run out within reach, many times over.
If scaled copies halt, the real run may halt when its own blocks run out; if none does across scales, the
structure survives its run-out events, at least at these scales.
usage: scaled.py TRI MACHINE K LOG.gz SECONDS SCALE [SCALE ...] [--seeds N] [--mod M]"""
import argparse, gzip, os, random, re, subprocess
ap = argparse.ArgumentParser()
ap.add_argument('tri'); ap.add_argument('machine'); ap.add_argument('K', type=int); ap.add_argument('log')
ap.add_argument('secs'); ap.add_argument('scales', nargs='+', type=float)
ap.add_argument('--seeds', type=int, default=2); ap.add_argument('--mod', type=int, default=12)
a = ap.parse_args()
RUN = re.compile(r'(\(?)([01]+)(\)?)(?:\^(\d+))?')
line = None
for l in gzip.open(a.log, 'rt'):
    if l[0] in 'EC' and '[' not in l and '(' in l: line = l
h, t = line.split('|', 1); h = h.split(); side, step0, state = h[1], h[2], h[-1]
runs = [(m.group(2), int(m.group(4) or 1), m.group(1) == '(') for m in RUN.finditer(t)]
print('%s K=%d: scaled restarts from the %s-end return at step %s (state %s, %d runs), %s s each'
      % (a.machine, a.K, side, step0, state, len(runs), a.secs))
tmp = '/tmp/claude-0/scaled_%d.txt' % os.getpid()
os.makedirs('/tmp/claude-0', exist_ok=True)
for F in a.scales:
    for sd in range(a.seeds):
        rnd = random.Random(sd * 1000 + int(F))
        out = []
        for b, c, isb in runs:
            if c < 3 or isb: out.append('(%s)' % b if isb else ('%s^%d' % (b, c) if c > 1 else b)); continue
            tt = max(3, int(c / F)); r = c % a.mod
            n = tt - (tt - r) % a.mod + a.mod * rnd.randint(-1, 1)
            while n < 3: n += a.mod
            out.append('%s^%d' % (b, n))
        open(tmp, 'w').write('%s %s %s\n' % (side, state, ' '.join(out)))
        lg = tmp + '.log'
        o = subprocess.run([a.tri, a.machine, str(a.K), '1e30', a.secs, lg], capture_output=True, text=True, env={'INIT': tmp}).stdout.strip()
        res = re.search(r'result=(\w+) steps=(\d+).*runs=(\d+)', o)
        fin = [l for l in open(lg) if l.startswith('F ')]
        far = lambda toks: ' '.join(toks[-4:] if side == 'L' else toks[:4])
        endt = fin[0].split(None, 3)[3].split() if fin else []
        print('  1/%-6g seed %d: %s at step %.3g, %s runs; far end %s -> %s' % (F, sd, res.group(1), int(res.group(2)), res.group(3),
              far(out), far(endt)))
        os.remove(lg)
os.remove(tmp)
