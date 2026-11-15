import pickle, difflib, collections, sys
W = pickle.load(open(sys.argv[1], 'rb'))
fmt = lambda s: ' '.join(('o' if v else 'z') + str(n) for v, n in s)
ph = sorted(W)
rows = []
for p in ph[:-1]:
    x = W[p][1]; y = W[p + 1][1]
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    blocks = [op for op in sm.get_opcodes() if op[0] != 'equal']
    for tag, i1, i2, j1, j2 in blocks:
        cell = sum(n for _, n in x[:i1])
        rows.append((p, i1, len(x), cell, fmt(x[max(0, i1 - 2):i2 + 2]), fmt(y[max(0, j1 - 2):j2 + 2])))
for r in rows[:60]:
    print(f"{r[0]} run {r[1]}/{r[2]} cell {r[3]}:  {r[4]}  ->  {r[5]}")
