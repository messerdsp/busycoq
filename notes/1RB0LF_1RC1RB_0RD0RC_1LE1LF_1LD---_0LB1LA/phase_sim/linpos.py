"""Lineage stats by position: for frozen runs (unchanged >= F phases) whose frozen ancestry is exactly one run,
tabulate (bucket of the run's index) x (old length class -> new length class); also merged counts per bucket."""
import sys, collections
F = int(sys.argv[2]) if len(sys.argv) > 2 else 20
info = {}
import os
files = [sys.argv[1]] + ([sys.argv[1].replace('.runs', '.alive')] if os.path.exists(sys.argv[1].replace('.runs', '.alive')) else [])
for line in (l for f in files for l in open(f)):
    x, b, d, L, par, pos, tot = line.split()
    info[int(x)] = (int(b), None if d in ('end', 'alive') else int(d), int(L), [] if par == '-' else [int(p) for p in par.split(',')], int(pos) // 2, int(tot) // 2)
END = max(v[1] or 0 for v in info.values())
def life(x): b, d = info[x][0], info[x][1]; return (d if d is not None else END) - b
def frozen(x): return x in info and life(x) >= F
memo = {}
sys.setrecursionlimit(1000000)
def fanc(x):
    if x in memo: return memo[x]
    res = set(); born = not info[x][3]
    for p in info[x][3]:
        if p not in info: continue
        if frozen(p): res.add(p)
        else:
            r, bb = fanc(p); res |= r; born |= bb
    memo[x] = (res, born); return memo[x]
def bucket(i, tot):
    return '<300' if i < 300 else '<1000' if i < 1000 else '<3000' if i < 3000 else 'top(>=tot-2000)' if i >= tot - 2000 else '>=3000'
single = collections.defaultdict(collections.Counter); merged = collections.Counter(); short = collections.defaultdict(collections.Counter)
for x in info:
    if not frozen(x) or not info[x][3]: continue
    anc, born = fanc(x)
    bk = bucket(info[x][4], info[x][5])
    if len(anc) == 1 and not born:
        a = next(iter(anc)); o, n = info[a][2], info[x][2]
        single[bk][max(-3, min(3, n - o))] += 1
        if n <= 7 or o <= 7: short[bk][(o, n)] += 1
    elif len(anc) >= 2: merged[bk] += 1
for bk in sorted(single):
    print(bk, 'single', sum(single[bk].values()), 'merged', merged[bk], dict(sorted(single[bk].items())))
    print('   short (old,new):', sorted(short[bk].items())[:20])
