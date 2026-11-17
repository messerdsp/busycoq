import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state, fill
from msim import Stuck, Halted
from rlesim import run, Halt, push
from m9 import T37
st = load_state(sys.argv[1]); PRE = int(sys.argv[2]); trials = [[int(x) for x in v.split(',')] for v in sys.argv[3:]]
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 1200, 1400)
while m0.nov < PRE or toks(m0.r_list()[:100000])[1] != "o4":
    k = m0.mstep()
    if k == "OV": m0.b = fill(m0.b, 1400)
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list())
for vals in trials:
    T = list(T0)
    for j, v in enumerate(vals): T[3 + 2 * j] = 'o%d' % v
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 1200, 1400); last = None
    try:
        while m.nov < m0.nov + sum(vals[:3]) + 60:
            if m.mstep() == 'OV': m.b = fill(m.b, 1400); last = toks(m.r_list()[:100000])[:8]
        res = 'no halt'
    except (Stuck, Halted):
        left = [[1, m.a]]; right = []
        for s in reversed([0, 1, 1] + m.r_list()): push(right, s, 1)
        try: run(T37, left, 0, right, 'D', max_steps=400000); res = 'stuck, machine does not halt'
        except Halt: res = 'HALT'
    print(vals, res, 'at phase', m.nov, 'last tokens', ' '.join(last or []), flush=True)
