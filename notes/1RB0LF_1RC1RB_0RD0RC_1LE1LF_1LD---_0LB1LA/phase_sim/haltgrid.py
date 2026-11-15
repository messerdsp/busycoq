import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
from msim import Stuck, Halted
from rlesim import run, Halt, push
from m9 import T37
st = load_state(sys.argv[1]); PRE = int(sys.argv[2])
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 1200, 1400)
while m0.nov < PRE: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list())
def outcome(A, B):
    T = list(T0); T[3] = 'o%d' % A; T[5] = 'o%d' % B
    m = trunc_state(m0.a, m0.b, cells(T), 'R', m0.nov, 1200, 1400)
    try:
        while m.nov < m0.nov + 30: m.mstep()
        return '.'
    except (Stuck, Halted):
        if m.mode != 'L' or m.b != 0: return '?'
        left = [[1, m.a]]; right = []
        for s in reversed([0, 1, 1] + m.r_list()): push(right, s, 1)
        try: run(T37, left, 0, right, 'D', max_steps=200000); return 'n'
        except Halt: return 'H'
Bs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2235, 2236]
print('A\\B ' + ' '.join(f'{b:>4}' for b in Bs))
for A in range(1, 13):
    print(f'{A:>3} ' + ' '.join(f'{outcome(A, B):>4}' for B in Bs), flush=True)
