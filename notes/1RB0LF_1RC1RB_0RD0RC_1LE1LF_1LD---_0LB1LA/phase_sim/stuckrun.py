"""Run the real machine from the configuration where the macro model gets stuck (b = 0, prefix not 00)."""
import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
from msim import Stuck
from rlesim import run, Halt, push
from m9 import T37
st = load_state(sys.argv[1]); PRE = int(sys.argv[2])
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 2000, 2200)
while m0.nov < PRE: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list())
for A in [1, 2, 3, 4, 5, 6]:
    T = list(T0); T[3] = 'o%d' % A
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 2000, 2200)
    try:
        while m.nov < m0.nov + 40: m.mstep()
        print('A', A, 'macro model fine'); continue
    except Stuck as e:
        pass
    # config: head D at H; left (outward) = (10)^b 1^a; right = 0 1 1 r
    assert m.mode == 'L' and m.b == 0
    r = m.r_list()
    left = [[1, m.a]]                       # nearest last: 1^a (b = 0 so no (10) pairs)
    right = []
    for s in reversed([0, 1, 1] + r): push(right, s, 1)
    print('A', A, 'stuck at phase', m.nov, 'a bits', m.a.bit_length(), 'r prefix', r[:12])
    try:
        stt, L, cur, R = run(T37, left, 0, right, 'D', max_steps=200000)
        print('   no halt within 200000 macro steps; state', stt, 'near', L[-3:], cur, R[-3:])
    except Halt as h:
        print('   HALTS:', str(h.args[0])[:200])
