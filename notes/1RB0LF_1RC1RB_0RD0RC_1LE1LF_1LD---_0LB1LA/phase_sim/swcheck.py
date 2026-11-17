import pickle, collections, re, sys
R = sum((pickle.load(open(f, 'rb')) for f in sys.argv[1:]), [])
W = 40
def comp(bits):
    s = ''.join(map(str, bits))
    return re.sub(r'1{8,}', lambda m: '1' * (6 + len(m.group()) % 2) + '+', s)
print('sweeps', len(R))
for lb, rb in [(2, 2), (4, 4), (6, 6), (8, 8), (10, 10), (12, 12), (16, 16), (8, 16), (16, 8)]:
    for pos in (False, True):
        tab = collections.defaultdict(collections.Counter)
        for r in R:
            key = (r['pos'] if pos else 0, comp(r['before'][W - lb:W + rb]))
            val = ''.join(map(str, r['after'][W - 2:W + 4]))
            tab[key][val] += 1
        bad = sum(1 for c in tab.values() if len(c) > 1)
        print(f'left {lb:2d} right {rb:2d} pos {pos!s:5}: keys {len(tab):4d} nondet {bad}')
