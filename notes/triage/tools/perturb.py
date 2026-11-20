#!/usr/bin/env python3
"""Perturbation test (simulation, heuristic): how much does non-halting depend on the exact sizes?
Take one logged tape of the real run (an 'E' or 'C' line with the whole tape, <= 120 runs), keep every block and
every run of count < 3, and replace each count c >= 3 by a random value with the same residue mod MOD (default 12),
between 3 and MAXC. Start the machine there (same state, head at the same end) and run MAXSTEPS steps with the plain
simulator runcfg. Report how many of the TRIALS starts halt, and how soon.
  residue mode (default): sizes change, residues mod MOD are kept;
  free mode (--free):     sizes and residues both random;
  scaled mode (--scale F): every long run divided by F (residue mod MOD kept, +-MOD jitter): a scaled-down copy of
                           the real tape, so that slowly worn blocks run out within the simulated steps;
  permute mode (--permute): residue mode, and in addition the stretches of short runs (count < 3) between long runs
                           are shuffled among themselves: a random arrangement of the tape's own digit words.
If nearly no perturbed start halts, the observed structure is robust: an invariant on shapes and residues is
plausible. If many halt, non-halting of the real run rests on exact relations between the numbers.
usage: perturb.py RUNCFG MACHINE K LOG.gz [--line N] [--trials T] [--maxc C] [--steps S] [--mod M] [--free] [--seed X]
"""
import argparse, gzip, random, re, subprocess
ap = argparse.ArgumentParser()
ap.add_argument('runcfg'); ap.add_argument('machine'); ap.add_argument('K', type=int); ap.add_argument('log')
ap.add_argument('--line', type=int, default=-1, help='which full-tape line (index among usable lines; -1 = last)')
ap.add_argument('--trials', type=int, default=100); ap.add_argument('--maxc', type=int, default=300)
ap.add_argument('--steps', type=float, default=3e8); ap.add_argument('--mod', type=int, default=12)
ap.add_argument('--free', action='store_true'); ap.add_argument('--permute', action='store_true'); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--show', action='store_true'); ap.add_argument('--scale', type=float, default=0)
a = ap.parse_args()
RUN = re.compile(r'(\(?)([01]+)(\)?)(?:\^(\d+))?')
lines = []
for l in gzip.open(a.log, 'rt'):
    if l[0] not in 'EC' or '[' in l: continue
    h, t = l.split('|', 1); h = h.split()
    if '(' not in t: continue
    lines.append((h[1], h[2], h[-1], t.strip()))
side, steps, state, tape = lines[a.line]
runs = []   # (block, count, is_back)
for m in RUN.finditer(tape):
    runs.append((m.group(2), int(m.group(4) or 1), m.group(1) == '('))
K = a.K
blank = '0' * K
def build(rs):
    cells = []; head = None
    if side == 'L': cells.append(blank); head = K - 1          # facing = blank block left of everything
    for b, c, isb in rs: cells.append(b * c)
    if side == 'R': head = sum(len(x) for x in cells); cells.append(blank)
    return ''.join(cells), head
rnd = random.Random(a.seed)
def perturb():
    out = []
    if a.scale:      # scaled-down copy: every long run divided by SCALE, residue mod MOD kept, plus a small random jitter
        for b, c, isb in runs:
            if c < 3 or isb: out.append((b, c, isb)); continue
            t = max(3, int(c / a.scale)); r = c % a.mod
            n = t - (t - r) % a.mod + a.mod * rnd.randint(-1, 1)
            while n < 3: n += a.mod
            out.append((b, n, isb))
        return out
    if a.permute:
        segs, cur, longs = [], [], []
        for b, c, isb in runs:
            if c >= 3 and not isb: segs.append(cur); cur = []; longs.append((b, c, isb))
            else: cur.append((b, c, isb))
        segs.append(cur)
        inner = [g for g in segs[1:-1] if not any(x[2] for x in g)]
        rnd.shuffle(inner); it = iter(inner)
        segs = [segs[0]] + [g if any(x[2] for x in g) else next(it) for g in segs[1:-1]] + ([segs[-1]] if len(segs) > 1 else [])
        rs = list(segs[0])
        for (b, c, isb), g in zip(longs, segs[1:]):
            r = c % a.mod; n = r + a.mod * rnd.randint(0, max(0, (a.maxc - r) // a.mod))
            while n < 3: n += a.mod
            rs.append((b, n, isb)); rs.extend(g)
        return rs
    for b, c, isb in runs:
        if c < 3 or isb: out.append((b, c, isb)); continue
        if a.free: n = rnd.randint(3, a.maxc)
        else:
            r = c % a.mod; n = r + a.mod * rnd.randint(0, max(0, (a.maxc - r) // a.mod))
            while n < 3: n += a.mod
        out.append((b, n, isb))
    return out
# sanity: the unperturbed tape (scaled down is not possible); report the original sizes
print('machine', a.machine, 'K', K, 'from %s-end return at step %s, state %s, %d runs' % (side, steps, state, len(runs)))
print('mode', ('scaled 1/%g, ' % a.scale if a.scale else '') + 'free' if a.free else ('scaled 1/%g, ' % a.scale if a.scale else '') + ('permute + ' if a.permute else '') + 'residues mod %d kept' % a.mod, 'max count', a.maxc, 'steps per trial %.3g' % a.steps)
halts = []
for t in range(a.trials):
    rs = perturb(); cells, head = build(rs)
    o = subprocess.run([a.runcfg, a.machine, state, str(head), cells, '%.0f' % a.steps], capture_output=True, text=True).stdout.split()
    if o and o[0] == 'HALT':
        halts.append(int(o[1]))
        if a.show: print('  halt at %s:' % o[1], ' '.join('%s^%d' % (b, c) if c > 1 else b for b, c, isb in rs))
    elif a.show and t < 5: print('  no halt:', ' '.join('%s^%d' % (b, c) if c > 1 else b for b, c, isb in rs))
print('halted %d of %d' % (len(halts), a.trials), ('; median halt step %.3g' % sorted(halts)[len(halts) // 2]) if halts else '')
