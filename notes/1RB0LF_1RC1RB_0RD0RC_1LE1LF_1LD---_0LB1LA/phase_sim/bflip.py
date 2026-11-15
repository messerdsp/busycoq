"""Fixed tape, one phase: which single-bit flips of b change the low tokens after the phase?"""
import os, sys
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, cells, trunc_state
st = load_state(sys.argv[1]); AH = int(sys.argv[2]); J0, J1 = int(sys.argv[3]), int(sys.argv[4])
N, K = 700, 900
m0 = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
while m0.nov < st['nov'] + AH: m0.mstep()
while m0.mode != 'R': m0.mstep()
T0 = toks(m0.r_list()); fr = next(i for i in range(2, len(T0)) if T0[i][0] == 'z' and T0[i] != 'z3')
def run(b):
    m = trunc_state(m0.a, b, cells(T0), 'R', m0.nov, N, K)
    nv = m.nov
    while m.nov == nv: m.mstep()
    return toks(m.r_list())[:fr + 30]
base = run(m0.b)
print('phase', m0.nov, 'front token', fr, 'b mod 2^40 =', bin(m0.b % 2**40), 'v2(b+3) =', ((m0.b + 3) & -(m0.b + 3)).bit_length() - 1)
print('base ', ' '.join(base[fr - 4:fr + 10]))
for j in range(J0, J1):
    try: t = run(m0.b ^ (1 << j))
    except Exception as e:
        print("bit", j, "breaks:", str(e)[:40]); continue
    if t != base:
        d = next(i for i in range(len(t)) if i >= len(base) or t[i] != base[i])
        print('bit', j, 'changes token', d, ':', ' '.join(t[fr - 4:fr + 10]))
