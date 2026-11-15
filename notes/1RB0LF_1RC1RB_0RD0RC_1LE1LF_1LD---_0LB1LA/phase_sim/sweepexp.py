"""The wave step as a pure machine sweep. In each phase, capture the word just before the first carry sweep (the
sweep after the first INC1, which carries into the lowest wave), vary the runs just above the parse stop, run that
one sweep, and record the local result. A sweep is the machine itself (no counter), so this is exact.
usage: sweepexp.py STATE P0 P1 OUT"""
import os, sys, itertools, pickle, random
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state
from wavestate import wave_state, locate
from msim import Halted, Stuck
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3]); OUT = sys.argv[4]
N, K = 700, 900; rnd = random.Random(7)
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
rows = []
def sweep_tokens(a, b, T):
    m = trunc_state(a, b, cells(T), 'R', 0, 10**6, K)
    m.b = b; m.a = a
    m.sweep()
    return toks(m.r_list())
while m0.nov < P1:
    k = m0.mstep()
    if k != 'OV' or m0.nov < P0: continue
    while True:                                   # advance to the first INC1 of this phase
        k = m0.mstep()
        if k in ('INC1', 'OV'): break
    if k == 'OV': continue
    T0 = toks(m0.r_list()); cell, md, nb, d = wave_state(m0); ti, off = locate(T0, cell)
    if not (6 < ti < N - 150): continue
    pos = sum(int(t[1:]) for t in T0[:ti]) % 4
    for par in itertools.product((0, 1), repeat=4):
        T = list(T0)
        first = ti + 1 if T0[ti][0] == 'z' else ti + 2      # first run above the stop token
        for j, q in enumerate(par): T[first + 2 * j] = 'o%d' % (9 + 2 * rnd.randint(0, 3) + (1 - q))
        try: A = sweep_tokens(m0.a, m0.b, T)
        except (Halted, Stuck) as e: A = ['ERR', str(e)[:30]]
        rows.append(dict(ph=m0.nov, d=d, ti=ti, off=off, md=md, pos=pos, par=par, first=first,
                         before=T[ti - 6:first + 12], after=A[ti - 6:first + 14], below=T0[ti - 6:ti]))
    print(m0.nov, ti, off, T0[ti], flush=True)
pickle.dump(rows, open(OUT, 'wb'))
