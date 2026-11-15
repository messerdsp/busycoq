"""End-to-end check of the halt route: at a real pre-excursion state (bottom = 4), set A..D (A even, B odd) with D
small, run through this excursion and the next one; report halt / no halt and the runs at the next excursion.
usage: excroute.py STATE PRE SEED NT"""
import os, sys, random
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells, trunc_state, fill
from msim import Stuck, Halted
from rlesim import run, Halt, push
from m9 import T37
st = load_state(sys.argv[1]); PRE = int(sys.argv[2]); rnd = random.Random(int(sys.argv[3])); NT = int(sys.argv[4])
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 1200, 1400)
while m0.nov < PRE or toks(m0.r_list()[:100000])[1] != "o4":
    k = m0.mstep()
    if k == "OV": m0.b = fill(m0.b, 1400)
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list()); print('base', m0.nov, ' '.join(T0[:12]), flush=True)
for t in range(NT):
    A = rnd.randrange(10, 40, 2); B = rnd.randrange(11, 41, 2); C = rnd.randint(10, 40); D = rnd.randint(1, 8)
    E = rnd.randint(10, 40)
    T = list(T0)
    for j, v in enumerate((A, B, C, D, E)): T[3 + 2 * j] = 'o%d' % v
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 1200, 1400)
    res = 'ok'; hist = []
    try:
        while m.nov < m0.nov + A + B + C + 60:
            k = m.mstep()
            if k == 'OV':
                m.b = fill(m.b, 1400); hist.append(toks(m.r_list()[:100000])[:8])
    except (Stuck, Halted):
        if m.mode != 'L' or m.b != 0: res = 'odd'
        else:
            left = [[1, m.a]]; right = []
            for s in reversed([0, 1, 1] + m.r_list()): push(right, s, 1)
            try: run(T37, left, 0, right, 'D', max_steps=400000); res = 'stuck-nohalt'
            except Halt: res = 'HALT'
    # runs at the excursion after this one: last phase where bottom was 2 (after the first 10 phases)
    nxt = [h for h in hist[10:] if h[1] in ('o2', 'o3')]
    print(f'A={A} B={B} C={C} D={D} E={E} -> {res} at +{m.nov - m0.nov}; next-exc runs:', ' '.join(nxt[-1][:8]) if nxt else '-', flush=True)
