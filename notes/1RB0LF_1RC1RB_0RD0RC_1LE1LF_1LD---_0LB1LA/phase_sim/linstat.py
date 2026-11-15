"""From lineage .runs: for each run that stayed unchanged >= F phases ('frozen'), find its frozen ancestors
(walking up through short-lived ids). One frozen ancestor = the run came through a wave single: record (old, new).
usage: linstat.py OUT.runs [F]"""
import sys, collections
F = int(sys.argv[2]) if len(sys.argv) > 2 else 8
info = {}
for line in open(sys.argv[1]):
    x, b, d, L, par = line.split()
    info[int(x)] = (int(b), None if d == 'end' else int(d), int(L), [] if par == '-' else [int(p) for p in par.split(',')])
END = max(v[1] or 0 for v in info.values())
def life(x):
    b, d, L, par = info[x]; return (d if d is not None else END) - b
def frozen(x): return x in info and life(x) >= F
memo = {}
def fanc(x):
    """frozen ancestors of x (x itself excluded), and whether a run with no ancestor (born) was met"""
    if x in memo: return memo[x]
    res = set(); born = False
    for p in info[x][3]:
        if p not in info: continue          # parent from before the log start: treat as frozen
        if frozen(p): res.add(p)
        else:
            r, bb = fanc(p); res |= r; born |= bb
    if not info[x][3]: born = True
    memo[x] = (res, born); return memo[x]
sys.setrecursionlimit(100000)
single = collections.Counter(); merged = 0; bornc = 0; shortsingle = []
for x in info:
    if not frozen(x) or not info[x][3]: continue
    anc, born = fanc(x)
    if len(anc) == 1 and not born:
        a = next(iter(anc)); oldL, newL = info[a][2], info[x][2]
        if a == 1 or info[a][0] == min(v[0] for v in [info[a]]) and False: pass
        single[newL - oldL] += 1
        if newL <= 7: shortsingle.append((oldL, newL, info[x][0]))
    elif len(anc) >= 2: merged += 1
    else: bornc += 1
print('frozen runs with one frozen ancestor (single), by change:', sorted(single.items()))
print('merged:', merged, 'born/other:', bornc)
print('single survivors ending at length <= 7 (old, new, phase):', sorted(shortsingle)[:80], len(shortsingle))
