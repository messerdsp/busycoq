import pickle, collections, sys
rec = pickle.load(open(sys.argv[1], 'rb'))
def ab(t):
    if t[0] == 'z': return t
    n = int(t[1:]); return t if n <= 4 else ('E' if n % 2 == 0 else 'O')
low = [r for r in rec if abs(r[1]) <= 50]
def state(r, back, fwd):
    ti = min(8, r[2]); W = r[5]
    return (r[0] % 2, r[1], r[3], ' '.join(ab(t) for t in W[ti - back:ti + fwd]))
for back in (1, 3, 5):
    for fwd in (1, 3, 5, 7, 9):
        for nxt_fwd in (1, 3):
            tab = collections.defaultdict(collections.Counter)
            for a, b in zip(low, low[1:]):
                if b[0] - a[0] > 3: continue
                key = state(a, back, fwd)
                val = (b[0] - a[0],) + state(b, back, nxt_fwd)
                tab[key][val] += 1
            bad = sum(1 for c in tab.values() if len(c) > 1); n = sum(sum(c.values()) for c in tab.values())
            print(f'back {back} fwd {fwd} next_fwd {nxt_fwd}: keys {len(tab):4d} nondet {bad:4d} samples {n}')
