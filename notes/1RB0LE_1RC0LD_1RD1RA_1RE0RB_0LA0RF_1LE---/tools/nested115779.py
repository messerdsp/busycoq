#!/usr/bin/env python3
"""Random-start test of the counter of 115779 = 1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD--- (the table of 23154 with
its states renamed; a halt from a configuration is a property of the table). Simulation only.
busy-beaver-explorer's notes: at every sweep the tape is
    0^inf 1^r [0 1^(3d1+2)] ... [0 1^(3dm+2)] 0 1 C>0 0^inf
with digits d >= 0; a sweep is an odometer step; when every digit is odd and r is even a *nested run* starts
(the counter runs again inside its own passed region), which is the part not proved.
Each trial builds such a tape with random r and digits and runs the plain simulator.
  --nested: every digit odd and r = 6j+6 with a first digit 1, so a nested run starts on the first sweep.
usage: nested115779.py RUNCFG [--trials T] [--steps S] [--nested] [--maxd D] [--len L] [--seed X]"""
import argparse, random, subprocess
ap = argparse.ArgumentParser()
ap.add_argument('runcfg'); ap.add_argument('--trials', type=int, default=100); ap.add_argument('--steps', type=float, default=1e9)
ap.add_argument('--nested', action='store_true'); ap.add_argument('--maxd', type=int, default=5)
ap.add_argument('--len', type=int, default=20); ap.add_argument('--seed', type=int, default=1)
a = ap.parse_args()
M = '1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---'
rnd = random.Random(a.seed)
halts = []; ends = {}
for t in range(a.trials):
    m = rnd.randint(3, a.len)
    if a.nested:
        digs = [1] + [rnd.choice([d for d in range(1, a.maxd + 1) if d % 2]) for _ in range(m - 1)]
        r = 6 * rnd.randint(0, 4) + 6
    else:
        digs = [rnd.randint(0, a.maxd) for _ in range(m)]
        r = rnd.choice([3, 6 * rnd.randint(0, 4) + 6, 6 * rnd.randint(0, 4) + 9, rnd.randint(1, 30)])
    cells = '1' * r + ''.join('0' + '1' * (3 * d + 2) for d in digs) + '01'
    head = len(cells); cells += '0'
    o = subprocess.run([a.runcfg, M, 'C', str(head), cells, '%.0f' % a.steps], capture_output=True, text=True).stdout.split()
    if o and o[0] == 'HALT': halts.append((int(o[1]), r, digs))
print('115779 random counter starts (%s), %d trials, %.3g steps each, digits <= %d, up to %d digits'
      % ('nested run at once' if a.nested else 'any digits and r', a.trials, a.steps, a.maxd, a.len))
print('halted %d of %d' % (len(halts), a.trials))
for h in halts[:8]: print('  halt at step %d from r=%d digits %s' % h)
