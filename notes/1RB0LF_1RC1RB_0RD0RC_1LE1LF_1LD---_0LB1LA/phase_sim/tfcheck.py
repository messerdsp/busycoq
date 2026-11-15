"""Is the controlled wave step a function of a small key?"""
import sys, pickle, glob, collections
rows = sum((pickle.load(open(f, 'rb')) for f in sys.argv[1:]), [])
rows = [r for r in rows if all(int(g[1:]) <= 7 for g in r[3].split()[:5])]
print('rows', len(rows), 'phases', len(set(r[0] for r in rows)))
def check(name, keyf):
    tab = collections.defaultdict(collections.Counter)
    for r in rows: tab[keyf(r)][r[5]] += 1
    bad = [k for k in tab if len(tab[k]) > 1]
    print(f'{name:45s} keys {len(tab):4d} nondet {len(bad):4d}')
    return tab, bad
check('parities only', lambda r: r[4])
check('gaps + parities', lambda r: (r[3], r[4]))
check('phase par + gaps + parities', lambda r: (r[1], r[3], r[4]))
check('pos mod 4 + gaps + parities', lambda r: (r[2], r[3], r[4]))
check('pos mod 2 + gaps + parities', lambda r: (r[2] % 2, r[3], r[4]))
tab, bad = check('phase + pos4 + gaps + parities', lambda r: (r[1], r[2], r[3], r[4]))
for k in bad[:6]:
    print(k); [print('    ', c, v) for v, c in tab[k].items()]
print('--- trimmed: outcome over the first 4 old runs, gaps near the front only')
def trim(o, n=4):
    bl, gp = o.split(' | '); bl = bl.split(); gp = gp.split()
    out = []; c = 0
    for b in bl:
        if c >= n: break
        out.append(b); c += int(b.split('+')[0].split('-')[0])
    return ' '.join(out) + ' | ' + ' '.join(gp[:len(out) + 1])
rows = [(r[0], r[1], r[2], ' '.join(r[3].split()[:4]), r[4], trim(r[5])) for r in rows]
check('parities only', lambda r: r[4])
check('gaps4 + parities', lambda r: (r[3], r[4]))
check('phase par + gaps4 + parities', lambda r: (r[1], r[3], r[4]))
check('pos mod 2 + gaps4 + parities', lambda r: (r[2] % 2, r[3], r[4]))
tab, bad = check('phase + pos4 + gaps4 + parities', lambda r: (r[1], r[2], r[3], r[4]))
tab, bad = check('phase + pos2 + gaps4 + parities', lambda r: (r[1], r[2] % 2, r[3], r[4]))
for k in bad[:8]:
    print(k); [print('    ', c, v) for v, c in tab[k].items()]
print('--- with real context parities (2 runs below, 3 above the varied ones) and bottom parity')
rows = [r for r in rows]
raw = sum((pickle.load(open(f, 'rb')) for f in sys.argv[1:]), [])
raw = [r for r in raw if all(int(g[1:]) <= 7 for g in r[3].split()[:5])]
rows = [(r[0], r[1], r[2], ' '.join(r[3].split()[:4]), r[4], trim(r[5]), r[6], int(r[7][1:]) % 2) for r in raw]
check('gaps4 + par + ctx', lambda r: (r[3], r[4], r[6]))
check('gaps4 + par + X4', lambda r: (r[3], r[4], r[6][2]))
check('phase + gaps4 + par + X4', lambda r: (r[1], r[3], r[4], r[6][2]))
check('phase + pos2 + gaps4 + par + X4', lambda r: (r[1], r[2] % 2, r[3], r[4], r[6][2]))
check('phase + pos2 + gaps4 + par + ctx', lambda r: (r[1], r[2] % 2, r[3], r[4], r[6]))
tab, bad = check('phase + pos4 + gaps4 + par + ctx', lambda r: (r[1], r[2], r[3], r[4], r[6]))
for k in bad[:5]:
    print(k); [print('    ', c, v) for v, c in tab[k].items()]
