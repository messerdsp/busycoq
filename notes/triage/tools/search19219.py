#!/usr/bin/env python3
"""Search 19219's documented tick-start forms for halting configurations (simulation only).
19219 = 1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD. Tick start (busy-beaver-explorer notes):
    0^inf 1110 (111110)^n 1 A> [word] 0^inf,   n even,   word = bits written in cell pairs '1b'.
Words built here: [prefix] v^x1 S1 v^x2 S2 ... v^xk TAIL with v = 010 (a block), separators S in
{r = 0, q = 10, p = 001, s = 1}, block sizes x >= 0 (0 = a block worn away, so separators touch), prefix '' or the
other phase '01', and TAIL from a file of far ends seen in the real run. Each start runs MAXSTEPS steps with the
batch plain simulator; halts are listed.
usage: search19219.py BATCH TAILS_FILE [--k K] [--sizes 0,1,2,3,4,6,9] [--n 2,6,12,30] [--steps 2e6] [--jobs 4]"""
import argparse, itertools, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ap = argparse.ArgumentParser()
ap.add_argument('batch'); ap.add_argument('tails')
ap.add_argument('--k', type=int, default=3); ap.add_argument('--sizes', default='0,1,2,3,4,6,9')
ap.add_argument('--n', default='2,6,12,30'); ap.add_argument('--steps', type=float, default=2e6)
ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--prefixes', default=',01'); ap.add_argument('--dump', default='')
a = ap.parse_args()
M = '1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD'
SEP = {'r': '0', 'q': '10', 'p': '001', 's': '1'}
tails = [l.split()[0] if l.strip() else '' for l in open(a.tails) if not l.startswith('#')]
tails = [t if t != '-' else '' for t in tails]
sizes = [int(x) for x in a.sizes.split(',')]; ns = [int(x) for x in a.n.split(',')]
prefixes = a.prefixes.split(',')
def configs():
    for n in ns:
        for pre in prefixes:
            for T in tails:
                for k in range(1, a.k + 1):
                    for xs in itertools.product(sizes, repeat=k):
                        for ss in itertools.product('rqps', repeat=k - 1):
                            w = pre + '010' * xs[0] + ''.join(SEP[s] + '010' * x for s, x in zip(ss, xs[1:])) + T
                            yield (n, pre, T, xs, ss, w)
allc = list(configs())
print('%d starts (n in %s, prefixes %s, %d tails, up to %d blocks of sizes %s), %.3g steps each'
      % (len(allc), ns, prefixes, len(tails), a.k, sizes, a.steps), flush=True)
def run(chunk):
    lines = []
    for n, pre, T, xs, ss, w in chunk:
        left = '1110' + '111110' * n + '1'
        lines.append('A %d %s %.0f' % (len(left), left + ''.join('1' + b for b in w), a.steps))
    o = subprocess.run([a.batch, M], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout.split('\n')
    return [(c, r) for c, r in zip(chunk, o) if r.startswith('HALT')]
chunks = [allc[i:i + 500] for i in range(0, len(allc), 500)]
halts = []
with ThreadPoolExecutor(a.jobs) as ex:
    for h in ex.map(run, chunks): halts.extend(h)
print('halted: %d of %d' % (len(halts), len(allc)))
import collections, json
by = collections.defaultdict(lambda: [0, 0])
for c in allc:
    n, pre, T, xs, ss, w = c
    key = (n, 'min>=3' if min(xs) >= 3 else 'some<3', T in ('11', '0011'))
    by[key][1] += 1
for (n, pre, T, xs, ss, w), r in halts:
    by[(n, 'min>=3' if min(xs) >= 3 else 'some<3', T in ('11', '0011'))][0] += 1
print('halts by (n, smallest block, tail is 11 or 0011):')
for k in sorted(by): print('  ', k, '%d of %d' % tuple(by[k]))
if a.dump: json.dump([[list(c[:4]) + [list(c[4])], r] for c, r in halts], open(a.dump, 'w'))
for (n, pre, T, xs, ss, w), r in halts[:40]:
    print('  n=%d prefix=%r blocks=%s seps=%s tail=%r -> %s' % (n, pre, xs, ''.join(ss), T, r))
