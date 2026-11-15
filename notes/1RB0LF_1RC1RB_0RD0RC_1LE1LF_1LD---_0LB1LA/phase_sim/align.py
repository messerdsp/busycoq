"""Align the runs before a wave passes (OLD) with the runs after (NEW): each new run is a block of j consecutive
old runs merged across their z3 separators (sum + 3(j-1)) plus a small change d.
usage: align.py OLDTOKS NEWTOKS (files with one token line each; only o/z3 tokens after the given start)"""
import sys
def runs(line):
    T = line.split(); assert all(t[0] in 'oz' for t in T)
    return T
def align(X, Y, D=3, J=60):
    i = 0; out = []
    for y in Y:
        best = None
        for j in range(1, J + 1):
            if i + j > len(X): break
            s = sum(X[i:i + j]) + 3 * (j - 1)
            if abs(y - s) <= D: best = (j, y - s); break
            if s > y + D: break
        if best is None: return out, ('stuck at', i, y, X[i:i + 6])
        out.append((X[i:i + best[0]], best[1], y)); i += best[0]
    return out, None
if __name__ == '__main__':
    X = [int(t) for t in sys.argv[1].split(',')]; Y = [int(t) for t in sys.argv[2].split(',')]
    o, err = align(X, Y)
    for a in o: print(a)
    print(err)
