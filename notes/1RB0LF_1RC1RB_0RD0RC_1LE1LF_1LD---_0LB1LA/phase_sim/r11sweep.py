import os, sys, collections
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, trunc_state, toks
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3])
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 2000, 2200)
prev = None
while m.nov < P1:
    if m.nov >= P0 and m.mode == 'R' and prev not in ('INC1', 'OV'):
        o = m.off; before = bytes(m.buf[o - 4:m.hi + 4]); a, b = m.a, m.b
        k = m.mstep()
        after = bytes(m.buf[o - 4:o - 4 + len(before)])
        ch = [i - 4 for i in range(len(before)) if before[i] != after[i]]
        print(m.nov, 'sweep after', prev, 'changed rel r0:', ch[:20], 'n', len(ch))
        print('   before', ''.join(map(str, before[:60])))
        print('   after ', ''.join(map(str, after[:60])))
        print('   toks before', ' '.join(toks(list(before[4:]))[:8]))
        prev = k; continue
    k = m.mstep()
    if m.nov >= P0 and k not in ('sweep',): pass
    if m.nov >= P0 and k in ('R101', 'R11', 'INC1', 'INCS', 'OV') and m.nov <= P1: print('   step', m.nov, k, 'b', m.b if m.b < 10**6 else 'big', 'pre', list(m.buf[m.off:m.off + 6]))
    prev = k
