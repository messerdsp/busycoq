import pickle, difflib, collections, sys
W = pickle.load(open(sys.argv[1], 'rb'))
ph = sorted(W)
pat = collections.Counter(); ex = {}
for p in ph[:-1]:
    x = W[p][1]; y = W[p + 1][1]
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal' or i1 <= 2: continue
        if sum(n for _, n in x[i1:]) < 1500: continue          # skip the top region
        a = x[i1 - 1:i2 + 1]; b = y[j1 - 1:j2 + 1]
        # signature: gaps and parities before; deltas after
        sig = ('B:' + ' '.join(('z%d' % n) if v == 0 else ('o' + 'eo'[n % 2]) for v, n in a) + ' | A:' +
               ' '.join(('z%d' % n) if v == 0 else 'o' for v, n in b))
        pat[sig] += 1; ex.setdefault(sig, (p, a, b))
for sig, c in pat.most_common(40):
    p, a, b = ex[sig]
    f = lambda s: ' '.join(('o' if v else 'z') + str(n) for v, n in s)
    print(f'{c:4d}  {sig:60s}  e.g. {p}: {f(a)} -> {f(b)}')
