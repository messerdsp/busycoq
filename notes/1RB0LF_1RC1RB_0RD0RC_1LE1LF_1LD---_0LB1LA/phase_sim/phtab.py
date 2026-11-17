"""Per-phase local rewrite of the wave on synthetic logs: key = gaps and run parities in a window that starts
BACK runs below the first changed token; value = the block structure and gaps after one phase."""
import sys, collections
from align import align
BACK, C = int(sys.argv[1]), int(sys.argv[2])
tab = collections.defaultdict(collections.Counter); ex = {}
for f in sys.argv[3:]:
    L = [l.split() for l in open(f)][:int(__import__('os').environ.get('MAXL', '220'))]
    for (p0, *B), (p1, *A) in zip(L, L[1:]):
        if int(p1) != int(p0) + 1: continue
        i = 2
        while i < min(len(A), len(B)) and A[i] == B[i]: i += 1
        if i >= len(B) - 40: continue
        i -= i % 2; i0 = max(2, i - 2 * BACK)
        key = ('ph%d ' % (int(p0) % 2)) + ('p%d ' % (sum(int(t[1:]) for t in B[:i0]) % int(__import__('os').environ.get('PM', '4')))) + ' '.join(t if t[0] == 'z' else ('E' if int(t[1:]) % 2 == 0 else 'O') for t in B[i0:i0 + C])
        X = [int(t[1:]) for t in B[i0 + 1:i0 + 1 + C + 8:2]]; Y = [int(t[1:]) for t in A[i0 + 1:i0 + 1 + C + 8:2]]
        o, err = align(X, Y, D=4, J=6)
        # outcome up to the end of the key window (in old runs)
        n = 0; out = []
        for g, d, y in o:
            if n >= C // 2: break
            out.append(f"{len(g)}{'%+d' % d if d else ''}"); n += len(g)
        gaps = ' '.join(A[i0:i0 + 2 * len(out) + 2:2])
        val = ' '.join(out) + ' | ' + gaps
        tab[key][val] += 1; ex.setdefault((key, val), (f, p0, ' '.join(B[i0:i0 + C]), ' '.join(A[i0:i0 + C])))
bad = [k for k in tab if len(tab[k]) > 1]
print('keys', len(tab), 'nondet', len(bad), 'samples', sum(sum(c.values()) for c in tab.values()))
if '-v' in sys.argv[0:1] or len(bad) < 15:
    for k in bad:
        print(k)
        for v, c in tab[k].items(): print('   ', c, v, '  e.g.', ex[(k, v)][1:])
