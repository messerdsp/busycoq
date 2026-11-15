"""Tabulate the wave's local rewrite from a per-phase token log: for consecutive phases find the changed window
(ignoring the bottom run), abstract runs (n<=4 exact, else parity e/o) and check the rule is deterministic."""
import sys
from collections import defaultdict
def ab(t):
    if t[0] == 'z': return t
    n = int(t[1:]); return t if n <= 4 else ('E' if n % 2 == 0 else 'O')
def window(B, A, lo=2, maxfront=None):
    i = lo
    while i < min(len(B), len(A)) and B[i] == A[i]: i += 1
    for j in range(i, len(B) - 30):
        for sh in (0, -2, 2, -4, 4):
            if B[j:j + 24] == A[j + sh:j + sh + 24]: return i, j, j + sh
    return i, len(B), len(A)
def run(path, C=8, upto=None):
    L = open(path).readlines()[:-1]
    prev = None; tab = defaultdict(lambda: defaultdict(int)); ex = {}
    for l in L:
        T = l.split(); ph = int(T[0]); T = T[1:]
        if upto and ph > upto: break
        if prev is not None and ph == prev[0] + 1:
            B = prev[1]
            # only consider the region below the cut (last 400 tokens can be affected by truncation)
            B = B[:len(B) - 400]; A = T[:len(B) + 20]
            i, jb, ja = window(B, A)
            if i >= len(B): prev = (ph, T); continue
            i -= i % 2                      # start at a gap token
            pc = sum(int(t[1:]) for t in B[:i]) % 4
            key = f'p{pc} ' + ' '.join(ab(t) for t in B[i:i + C])
            # describe the change: before window and after window with o-runs as deltas when the shape is equal
            bw, aw = B[i:jb + (jb - i) % 2], A[i:ja + (ja - i) % 2]
            if len(bw) == len(aw):
                val = ' '.join(a if a[0] == 'z' else ('o%+d' % (int(a[1:]) - int(b[1:]))) for a, b in zip(bw, aw[:0] or bw) for a in [aw[bw.index(b)] if False else None] if False) or None
                val = ' '.join((aw[k] if aw[k][0] == 'z' else 'o%+d' % (int(aw[k][1:]) - int(bw[k][1:]))) for k in range(len(bw)))
            else:
                val = 'SHAPE ' + ' '.join(bw) + ' -> ' + ' '.join(aw)
            v = val if not val.startswith('SHAPE') else 'SHAPE%d->%d' % (len(bw), len(aw))
            tab[key][v] += 1; ex.setdefault((key, v), (ph, ' '.join(B[i:i + C]), ' '.join(A[i:i + C + 2])))
        prev = (ph, T)
    return tab, ex
if __name__ == '__main__':
    C = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    tab, ex = run(sys.argv[1], C)
    nd = 0
    for k in sorted(tab, key=lambda k: -sum(tab[k].values())):
        vs = tab[k]
        flag = '' if len(vs) == 1 else '  <-- NONDET'
        nd += len(vs) > 1
        print(f'{k:40s} n={sum(vs.values()):4d}{flag}')
        for v, c in sorted(vs.items(), key=lambda a: -a[1]):
            e = ex[(k, v)]
            print(f'      {c:4d}  {v[:60]:60s} e.g. ph{e[0]}: {e[1]}  =>  {e[2]}')
    print('keys', len(tab), 'nondet', nd)
