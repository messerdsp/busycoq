import sys, gzip
for fn in sys.argv[1:]:
    st = dict(l.rstrip('\n').split(' ', 1) for l in gzip.open(fn, 'rt'))
    T = st['r'].split(); runs = [int(t[1:]) for t in T if t[0] == 'o']
    out = [st['nov'], 'runs', len(runs)]
    for th in (4, 7, 10, 20):
        idx = [i for i, x in enumerate(runs) if x <= th]
        out += [f'<= {th}: first {idx[0] if idx else None} count-in-first-1000 {sum(1 for i in idx if i < 1000)}']
    print(*out)
