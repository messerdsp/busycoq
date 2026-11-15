"""What do the other sweeps (after OV, after R11) do? Report changed cell ranges relative to the parse stop / start."""
import os, sys, ctypes, collections
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, trunc_state
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3])
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 700, 900)
kinds = collections.Counter(); seqs = collections.Counter(); prev = None; ex = collections.defaultdict(list)
seq = []
while m.nov < P1:
    if m.mode == 'R' and m.nov >= P0:
        o = m.off; before = bytes(m.buf[o - 4:m.hi + 4])
        k = m.mstep()
        after = bytes(m.buf[o - 4:o - 4 + len(before)])
        ch = [i - 4 for i in range(len(before)) if before[i] != after[i]]
        tag = prev
        kinds[(tag, (min(ch), max(ch)) if ch and max(ch) < 40 else ('far' if ch else 'none'))] += 1
        if len(ex[tag]) < 3: ex[tag].append((m.nov, ''.join(map(str, before[:30])), ''.join(map(str, after[:30])), ch[:12]))
    else:
        k = m.mstep()
    prev = k
for k, v in sorted(kinds.items(), key=lambda a: -a[1]): print(v, k)
for t, e in ex.items():
    print('after', t)
    for x in e: print('   ', x[0], x[1], '->', x[2], x[3])
