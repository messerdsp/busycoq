#!/usr/bin/env python3
"""144438 (1RB1LE_1LC1RE_1LE1LD_1LC0LA_1RF0LA_---0RA): how often do scaled-down copies of the real tape halt?
Scale every long run of the logged tape at step 7.04e17 by 1/F (residue mod 12 kept, jitter -12..+12) for many F
and seeds, run tri.c (INIT) for SECONDS, and list halts. Halts with few enough steps and cells are re-checked with
the plain one-cell simulator runcfg. Simulation only.
usage: scan144438.py TRI RUNCFG LOG.gz SECONDS F1 F2 ... [--seeds N]"""
import argparse, gzip, os, random, re, subprocess
ap = argparse.ArgumentParser()
ap.add_argument('tri'); ap.add_argument('runcfg'); ap.add_argument('log'); ap.add_argument('secs')
ap.add_argument('scales', nargs='+', type=float); ap.add_argument('--seeds', type=int, default=4)
a = ap.parse_args()
M = '1RB1LE_1LC1RE_1LE1LD_1LC0LA_1RF0LA_---0RA'; K = 6
RUN = re.compile(r'(\(?)([01]+)(\)?)(?:\^(\d+))?')
line = None
for l in gzip.open(a.log, 'rt'):
    if l[0] in 'EC' and '[' not in l and '(' in l: line = l
h, t = line.split('|', 1); h = h.split(); side, state = h[1], h[-1]
runs = [(m.group(2), int(m.group(4) or 1), m.group(1) == '(') for m in RUN.finditer(t)]
tmp = '/tmp/claude-0/scan_%d.txt' % os.getpid()
nh = nt = 0
for F in a.scales:
    for sd in range(a.seeds):
        rnd = random.Random(sd * 7919 + int(F * 10))
        out = []
        for b, c, isb in runs:
            if c < 3 or isb: out.append((b, c, isb)); continue
            tt = max(3, int(c / F)); r = c % 12; n = tt - (tt - r) % 12 + 12 * rnd.randint(-1, 1)
            while n < 3: n += 12
            out.append((b, n, isb))
        open(tmp, 'w').write('%s %s %s\n' % (side, state, ' '.join('(%s)' % b if isb else ('%s^%d' % (b, c) if c > 1 else b) for b, c, isb in out)))
        o = subprocess.run([a.tri, M, str(K), '1e30', a.secs], capture_output=True, text=True, env={'INIT': tmp}).stdout
        res = re.search(r'result=(\w+) steps=(\d+)', o); nt += 1
        tag = ''
        if res.group(1) == 'HALT':
            nh += 1
            cells = sum(len(b) * c for b, c, isb in out)
            if int(res.group(2)) < 2e10 and cells < 3e7:
                cs = ('0' * K if side == 'L' else '') + ''.join(b * c for b, c, isb in out) + ('0' * K if side == 'R' else '')
                head = K - 1 if side == 'L' else len(cs) - K
                p = subprocess.run([a.runcfg, M, state, str(head), cs, '%d' % (int(res.group(2)) + 10)], capture_output=True, text=True).stdout.split()
                tag = ' plain simulator: %s %s' % (p[0], p[1])
        print('1/%-6g seed %d: %s at step %.4g%s' % (F, sd, res.group(1), int(res.group(2)), tag), flush=True)
print('halted %d of %d scaled copies' % (nh, nt))
os.remove(tmp)
