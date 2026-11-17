"""Randomize the first R runs above the bottom (lengths LO..HI) at a real pre-excursion state, run the macro model
PH phases, log the first 20 tokens per phase; on a stuck macro step, run the machine (rlesim) and record halt/no halt.
usage: e2e.py STATE PRE SEED NTRIALS R LO HI PH OUT"""
import os, sys, random, json
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state, fill
from msim import Stuck, Halted
from rlesim import run, Halt, push
from m9 import T37
src, PRE, SEED, NT, R, LO, HI, PH, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), sys.argv[9]
N, K = 1200, 1400
st = load_state(src)
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
while m0.nov < PRE: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list())
rnd = random.Random(SEED); out = open(OUT, 'w')
for trial in range(NT):
    T = list(T0)
    vals = [rnd.randint(LO, HI) for _ in range(R)]
    for j, v in enumerate(vals): T[3 + 2 * j] = 'o%d' % v
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, N, K)
    log = []; res = 'ok'
    try:
        while m.nov < m0.nov + PH:
            nv = m.nov; k = m.mstep()
            if k == 'OV':
                m.b = fill(m.b, K)
                log.append(toks(m.r_list()[:200000])[:20])
    except (Stuck, Halted):
        if m.mode != 'L' or m.b != 0: res = 'odd'
        else:
            left = [[1, m.a]]; right = []
            for s in reversed([0, 1, 1] + m.r_list()): push(right, s, 1)
            try: run(T37, left, 0, right, 'D', max_steps=400000); res = 'stuck-nohalt'
            except Halt: res = 'HALT'
            log.append(toks(m.r_list()[:200000])[:20])
    out.write(json.dumps(dict(trial=trial, vals=vals, base=m0.nov, res=res, log=log)) + '\n'); out.flush()
