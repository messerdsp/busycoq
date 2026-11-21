"""Closure of the right contexts t under the frontier map f (simulated arrival -> next left-pass start, see
arrive.py) and the nest prefixes N_a,m(t) = B1 110 U^a T^m t.  Simulated; a search over concrete contexts up to a
length bound.  Prints the distinct front shapes (first few tokens of t) and any context where the arrival does not
reach a left-pass start (halts, or never returns within the step bound).
Usage: closure.py MAXLEN MAXITER"""
import sys, re, collections
from arrive import arrival, cells, blocks

def norm_front(s, k=4):
    """front shape: tokenize and keep the first k tokens"""
    return ' '.join(blocks(s).split()[:k])

def f(tcells):
    # arrival with c=1 and a long prefix of digits 1 so no left-end event happens
    spec = ' '.join(['0' if ch == '0' else '1' for ch in tcells]) or '0'
    res = arrival(1, tcells_to_spec(tcells), pre=(1, 1, 1, 1, 1, 1))
    return res

def tcells_to_spec(s):
    return ' '.join(s) if s else '0'

def main():
    MAXLEN = int(sys.argv[1]); MAXIT = int(sys.argv[2])
    T = lambda k: '00' + '10' * (3 * k + 2)
    GAP = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    start = ('001', GAP)
    seen = {start}; frontier = [start]; fronts = collections.Counter(); bad = []; par = {start: None}
    for it in range(MAXIT):
        new = []
        for (t, age) in frontier:
            fronts[norm_front(t)] += 1
            # frontier map
            res = arrival(1, ' '.join(t), pre=(1, 1, 1, 1, 1, 1))
            if len(res) < 4:
                bad.append(((t, age), res))
                if len(bad) <= 6:
                    print('BAD', blocks(t), age, res)
                    c = (t, age)
                    while par.get(c):
                        p_, how = par[c]; print('   <-', how, ':', blocks(p_[0]), p_[1]); c = p_
                continue
            _, rr, ns, R = res
            t2 = R.rstrip('0')
            if not t2: t2 = ''
            cand = [((t2, min(age + 1, GAP)), 'f')]
            # nest prefixes
            for a in ((0, 1) if age >= GAP else ()):
                for m in (0, 1, 2, 7, 9, 12):
                    for ks in ([0] * m, ([1] + [0] * (m - 1)) if m else []):
                        cand.append((('0010' + '110' + '101010' * a + ''.join(T(k) for k in ks) + t, 0), f'N{a},{ks}'))
            for c, how in cand:
                if len(c[0]) <= MAXLEN and c not in seen:
                    seen.add(c); new.append(c); par[c] = ((t, age), how)
        frontier = new
        print(f'iter {it}: {len(seen)} contexts, {len(fronts)} front shapes, {len(bad)} bad', flush=True)
        if not new: break
    for k, v in sorted(fronts.items(), key=lambda x: -x[1]): print(v, k)
    for b in bad[:3]:
        print('BAD', blocks(b[0][0]), b[0][1], b[1])
        c = b[0]
        while par.get(c):
            p_, how = par[c]; print('   <-', how, ':', blocks(p_[0]), p_[1]); c = p_

if __name__ == '__main__':
    main()
