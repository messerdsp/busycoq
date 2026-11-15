"""Run the macro model in the order of the Rocq list machine stepL: timer resets (prefix 101 / 11) and overflow
only when b = 0; otherwise increments (INCS up to the stop, then INC1 and a carry). Report any bad overflow."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('FILL', '10')
from msim import M, Stuck, INF
from m9 import T37
from lowsim import load_state, trunc_state, fill, toks
class ML(M):
    def mstep(self):
        if self.mode == 'R':
            self.sweep(); self.mode = 'L'; self.nmstep += 1; return 'sweep'
        if self.b == 0:
            p = self.pre(3)
            if p == [1, 0, 1]:
                self.a += 4; self.off += 2; self.buf[self.off] = 1; self.nmstep += 1; return 'R101'
            if p[:2] == [1, 1]:
                self.a += 4; self.off += 2; self.mode = 'R'; self.nmstep += 1; return 'R11'
            if p[:2] == [0, 0]:
                a = self.a; self.a, self.b = 3, 2 + a // 2
                self.off += 1; self.buf[self.off] = 0; self.mode = 'R'; self.nmstep += 1; self.nov += 1; return 'OV'
            raise Stuck('BAD overflow: b=0 and prefix %s' % p)
        k = self.rest(1)
        if k == 0:
            self.a += 4; self.b -= 1; self.mode = 'R'; self.nmstep += 1; return 'INC1'
        k = self.b if k == INF else min(k, self.b)
        while self.hi + 4 * (k.bit_length() + 8) + (1 << 12) > len(self.buf): self.grow()
        self.rincs(k, 1); self.a += 4 * k; self.b -= k; self.nmstep += 1; return 'INCS'
src, P1 = sys.argv[1], int(sys.argv[2])
if src == 'start':
    m = ML(T37, 11, 5, [1, 0]); K = None
else:
    st = load_state(src); K = 1400; T = toks(st['r'])[:1200]
    if T[-1][0] == 'z': T = T[:-1]
    from lowsim import cells
    m = ML(T37, st['a'], fill(st['b'], K), cells(T)); m.mode = st['mode']; m.nov = st['nov']
c = collections.Counter(); low = {}
try:
    while m.nov < P1:
        b0 = m.b; k = m.mstep(); c[k] += 1
        if k == 'OV':
            if K: m.b = fill(m.b, K)
            low[m.nov] = ' '.join(toks(m.r_list()[:200000])[:8])
except Stuck as e:
    print('STUCK', e, 'at phase', m.nov)
print(dict(c)); print('last', m.nov, low.get(m.nov))
for p in sorted(low)[-3:]: print(p, low[p])
