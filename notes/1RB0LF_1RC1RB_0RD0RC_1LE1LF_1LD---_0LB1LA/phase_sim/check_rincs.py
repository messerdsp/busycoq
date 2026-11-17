import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m9 import *
random.seed(2)
D0 = [[0,0,0,0],[0,1,1,0]]; SW = [[0,0,1,1],[0,1,1,1]]; T1 = [[0,0],[1,0]]
def rand_word():
    r = []; tp = 0
    for _ in range(random.randint(1, 7)):
        if tp == 0:
            if random.random() < 0.6: r += random.choice(D0)
            else: r += random.choice(SW); tp = 1
        else:
            r += [1, 1] * random.randint(0, 2)
            r += random.choice(T1); tp = 0
    return r + [random.randint(0, 1) for _ in range(6)]
stats = {}
for trial in range(3000):
    r = rand_word(); cap = rest(r)
    if cap == 0: continue
    k = random.randint(1, cap)
    r1 = list(r); ok = rincs(r1, k)
    r2 = list(r); res = 'ok'
    try:
        for _ in range(k):
            r2, _n = bounce(T37, hR, hL, r2)
            if r2 is None: res = 'BADBOUNCE'; break
    except Halt: res = 'HALT'
    if res == 'ok':
        L = max(len(r1), len(r2)); a = r1 + [0] * (L - len(r1)); b = r2 + [0] * (L - len(r2))
        res = 'ok' if (a == b and ok) else 'DIFF'
    stats[res] = stats.get(res, 0) + 1
print(stats)
