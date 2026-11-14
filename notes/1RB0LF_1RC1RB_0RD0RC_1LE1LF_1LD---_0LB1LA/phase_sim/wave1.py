import pickle, difflib, sys  # usage: wave1.py <rle.pkl> <from_index> <to_index>
W = pickle.load(open(sys.argv[1], 'rb'))
fmt = lambda s: ' '.join(('o' if v else 'z') + str(n) for v, n in s)
ph = sorted(W)
for p in ph[int(sys.argv[2]):int(sys.argv[3])]:
    x = W[p][1]; y = W[p + 1][1]
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != 'equal' and op[1] > 2]
    if not ops: print(p, 'no wave'); continue
    i1 = ops[0][1]; j1 = ops[0][3]
    # merge ops that are within 8 runs of the first
    last = [op for op in ops if op[1] - i1 < 10]
    i2 = max(op[2] for op in last); j2 = max(op[4] for op in last)
    print(f"{p} @{i1}: {fmt(x[i1-3:i2+1])}  ->  {fmt(y[j1-3:j2+1])}")
