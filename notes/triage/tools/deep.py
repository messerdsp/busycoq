#!/usr/bin/env python3
"""Deep simulation of one machine: a long tri run, then a drift test at the dominant cycle point.
usage: deep.py TRI MACHINE K SECONDS OUTDIR [EFROM]
At the dominant return point (end of the tape, side and state most frequent in the late records) every logged tape
is reduced to a shape: the sequence of blocks with counts < 3 kept and counts >= 3 replaced by a variable.
Drift test (all sim): for records with the same shape, is every kept quantity identical (it is, by definition of
the shape) and does each variable change by the same amount over one period of the shape sequence? Reports the
number of shapes, the period, the per-period increments, and the gap lengths [n] of skeleton tapes, which are
quantities that should return to the same value if the structure repeats.
"""
import gzip, json, math, os, re, subprocess, sys
from collections import Counter, defaultdict
TRI, M, K, SECS, OUT = sys.argv[1:6]
EFROM = sys.argv[6] if len(sys.argv) > 6 else None
os.makedirs(OUT, exist_ok=True)
log = os.path.join(OUT, M + '.deep.log')
env = dict(os.environ)
if EFROM: env['EFROM'] = EFROM; env['ECAP'] = '30000'
o = subprocess.run([TRI, M, K, '1e30', SECS, log], capture_output=True, text=True, env=env).stdout
print(o.strip())
RUN = re.compile(r'([01]+)\^(\d+)|\[(\d+)\]|\(([01]+)\)|([01]+)')
def runs_of(t):
    out = []
    for m in RUN.finditer(t):
        if m.group(1): out.append((m.group(1), int(m.group(2))))
        elif m.group(3): out.append(('gap', int(m.group(3))))
        else: out.append((m.group(4) or m.group(5), 1))
    return out
E = []
for l in open(log):
    if l[0] == 'E':
        h, t = l.split('|', 1); h = h.split()
        E.append((h[1], int(h[2]), h[6], runs_of(t)))
if not E: print('no end returns'); sys.exit()
late = E[len(E) // 2:]
dom = Counter((e[0], e[2]) for e in late).most_common(3)
print('dominant return points (late half):', dom)
side, st = dom[0][0]
es = [e for e in E if (e[0], e[2]) == (side, st)]
if EFROM: es = [e for e in es if e[1] >= float(EFROM)] or es
def shape(rr): return tuple((b, c if (b != 'gap' and c < 3) else ('g' if b == 'gap' else 'X')) for b, c in rr)
def vars_(rr): return [c for b, c in rr if b == 'gap' or c >= 3]
shs = [shape(e[3]) for e in es]
cnt = Counter(shs)
print('records at %s-end state %s: %d, distinct shapes %d, most common shape covers %d' % (side, st, len(es), len(cnt), cnt.most_common(1)[0][1]))
# period of the shape sequence over the last 2000 records
seq = shs[-2000:]
period = None
for p in range(1, min(400, len(seq) // 3)):
    if all(seq[i] == seq[i + p] for i in range(len(seq) - p)): period = p; break
print('shape sequence period (last %d records):' % len(seq), period)
res = {'machine': M, 'K': int(K), 'run': o.strip(), 'dominant': [side, st], 'records': len(es), 'shapes': len(cnt),
       'period': period}
if period:
    v = [vars_(e[3]) for e in es[-2000:]]
    incs = defaultdict(list)
    for i in range(len(v) - period):
        if len(v[i]) == len(v[i + period]):
            incs[i % period].append(tuple(b - a for a, b in zip(v[i], v[i + period])))
    const = all(len(set(x)) == 1 for x in incs.values())
    res['increments_constant'] = const
    ex = {k: Counter(x).most_common(3) for k, x in list(incs.items())[:3]}
    print('per-period increments constant at every phase:', const)
    print('examples (phase: most common increment vectors):', ex)
    res['increments_examples'] = {str(k): [[list(a), b] for a, b in x] for k, x in ex.items()}
    gaps = [[c for b, c in e[3] if b == 'gap'] for e in es[-2000:]]
    if any(gaps):
        gp = defaultdict(set)
        for i, g in enumerate(gaps): gp[i % period].add(tuple(g))
        res['gaps_repeat_exactly'] = all(len(x) == 1 for x in gp.values())
        print('skeleton gaps return to the same values at the same phase:', res['gaps_repeat_exactly'])
else:
    # no period: report how the variables at the most common shape evolve
    best = cnt.most_common(1)[0][0]
    v = [(e[1], vars_(e[3])) for e, s in zip(es, shs) if s == best]
    res['common_shape_samples'] = [[str(t), x[:12]] for t, x in v[-5:]]
    print('most common shape, last samples (steps, variables):')
    for t, x in v[-5:]: print('  ', t, x[:12])
    print('last record:', es[-1][1], ' '.join('%s^%s' % (b, c) if c != 1 else b for b, c in es[-1][3])[:600])
json.dump(res, open(os.path.join(OUT, M + '.deep.json'), 'w'), indent=1)
subprocess.run(['gzip', '-f', log])
