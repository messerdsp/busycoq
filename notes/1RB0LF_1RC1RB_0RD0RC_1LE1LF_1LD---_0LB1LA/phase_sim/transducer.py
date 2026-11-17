"""The digit parse of SBCv9 (rest) as a transducer on units 0^g 1^n. Entry state = (mode, k): mode t1/t0 at a
digit boundary located k cells into the unit (k cells already consumed by a digit that began in the previous
unit). Output: exit state for the next unit, the digits read, or FAIL."""
import collections
D4 = {(0,0,0,0): (0, 0), (0,1,1,0): (1, 0), (0,0,1,1): (0, 1), (0,1,1,1): (1, 1)}   # value, switch-to-t1
D2 = {(1,1): None, (0,0): 0, (1,0): 1}
def step_unit(g, n, mode, k, nxt_g=3):
    cells = [0] * g + [1] * n + [0] * nxt_g + [1] * 6      # lookahead into the next unit
    U = g + n; i = k; tp = mode; digits = []
    while i < U:
        if tp == 0:
            w = tuple(cells[i:i+4])
            if w not in D4: return 'FAIL', digits
            v, sw = D4[w]; digits.append(v); i += 4; tp = 1 if sw else 0
        else:
            w = tuple(cells[i:i+2])
            if w not in D2: return 'FAIL', digits
            if D2[w] is None: i += 2
            else: digits.append(D2[w]); i += 2; tp = 0
    return (tp, i - U), digits
if __name__ == "__main__":
  for g in (2, 3, 4, 7):
    print(f'gap {g}:')
    for mode in (0, 1):
        for k in range(0, 4):
            res = collections.defaultdict(list)
            for n in range(2, 14):
                out, dg = step_unit(g, n, mode, k)
                res[(out, tuple(dg))].append(n)
            line = '; '.join(f"n={','.join(map(str, ns)) if len(ns) < 5 else ('even' if ns[0] % 2 == 0 and all(x % 2 == 0 for x in ns) else 'odd' if all(x % 2 for x in ns) else ns)} -> {o} digits {list(d)}" for (o, d), ns in res.items())
            print(f'  in (t{mode}, k={k}): {line}')
