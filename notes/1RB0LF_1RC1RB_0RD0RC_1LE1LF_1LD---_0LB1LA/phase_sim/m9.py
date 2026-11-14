"""#9 (1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA) in the orientation of verify/SBCv9.v TM2:
mirrored, states renamed A,B,C,D,E,F -> A,C,D,E,G,F.  Differs from TM2 only at A0 and the E/G walk."""
import random

# (state, sym) -> (write, move, next); move +1 = R
T37 = {('A',0):(1,-1,'C'), ('A',1):(0,1,'F'),
       ('C',0):(1,-1,'D'), ('C',1):(1,-1,'C'),
       ('D',0):(0,-1,'E'), ('D',1):(0,-1,'D'),
       ('E',0):(1,1,'G'),  ('E',1):(1,1,'F'),
       ('G',0):(1,1,'E'),  ('G',1):None,
       ('F',0):(0,1,'C'),  ('F',1):(1,1,'A')}
TM2 = {('A',0):(1,1,'B'), ('A',1):(0,1,'F'), ('B',0):(0,-1,'C'), ('B',1):None,
       ('C',0):(1,-1,'D'), ('C',1):(1,-1,'C'), ('D',0):(0,-1,'E'), ('D',1):(0,-1,'D'),
       ('E',0):(1,1,'E'),  ('E',1):(1,1,'F'), ('F',0):(0,1,'C'), ('F',1):(1,1,'A')}

class Halt(Exception): pass

def LC(a, b):
    """left side cells from the head outward (position -1, -2, ...)"""
    return [0, 1] * b + [1] * a

def tape_of(left, right):
    t = {}
    for i, s in enumerate(left): t[-1 - i] = s
    for i, s in enumerate(right): t[i] = s
    return t

def run_until(tm, t, pos, st, stop, limit=10**7):
    """run until stop(pos, st) is true *before* executing the step"""
    n = 0
    while not stop(pos, st):
        tr = tm[(st, t.get(pos, 0))]
        if tr is None: raise Halt((pos, st, n))
        w, d, st = tr
        t[pos] = w; pos += d; n += 1
        if n > limit: raise RuntimeError('limit')
    return pos, st, n

def norm(t):
    return {k: v for k, v in t.items() if v}

def bounce(tm, hR, hL, r, limit=10**9):
    """sideRL: head in state hR[0] at r[0] with hR[1] (stream, nearest first) to its left, run until the head
    steps left of that word; it must then be in state hL[0] with hL[1] (nearest-first from the head) to its
    right. Returns r' (list) or raises."""
    q, ql = hR; q2, ql2 = hL
    n = len(ql); assert len(ql2) == n
    t = tape_of(ql, r)
    pos, st, steps = run_until(tm, t, 0, q, lambda p, s: p == -n - 1, limit)
    got = [t.get(-n + i, 0) for i in range(n)]
    if st != q2 or got != ql2:
        return None, steps
    hi = max([k for k, v in t.items() if v] + [0])
    return [t.get(i, 0) for i in range(0, hi + 1)], steps

hR, hL = ('C', [0, 0]), ('D', [0, 0])
hR_, hL_ = ('A', [1, 0, 1]), ('D', [0, 1, 1])

# counter word: r[0] is nearest the head.  Digits as in SBCv9.v (rest / RIncs).
def rest(r, i=0, tp=0):
    """number of increments before the parsed digits are all 1 (complement of their value). iterative."""
    bits = []
    while True:
        w4 = r[i:i + 4]; w2 = r[i:i + 2]
        if tp == 0:
            if w4 == [0, 0, 0, 0]: bits.append(1); i += 4
            elif w4 == [0, 1, 1, 0]: bits.append(0); i += 4
            elif w4 == [0, 0, 1, 1]: bits.append(1); i += 4; tp = 1
            elif w4 == [0, 1, 1, 1]: bits.append(0); i += 4; tp = 1
            else: break
        else:
            if w2 == [1, 1]: i += 2
            elif w2 == [0, 0]: bits.append(1); i += 2; tp = 0
            elif w2 == [1, 0]: bits.append(0); i += 2; tp = 0
            else: break
    return sum(b << j for j, b in enumerate(bits))

def rincs(r, k, tp=0):
    """add k to the counter in place (r: list). Returns False if it runs off the parsed digits."""
    i = 0
    while k:
        if tp == 0:
            w4 = r[i:i + 4]
            odd = k & 1; k >>= 1
            if w4 == [0, 0, 0, 0]:
                if odd: r[i:i + 4] = [0, 1, 1, 0]
            elif w4 == [0, 1, 1, 0]:
                if odd: r[i:i + 4] = [0, 0, 0, 0]; k += 1
            elif w4 == [0, 0, 1, 1]:
                if odd: r[i:i + 4] = [0, 1, 1, 1]
                tp = 1
            elif w4 == [0, 1, 1, 1]:
                if odd: r[i:i + 4] = [0, 0, 1, 1]; k += 1
                tp = 1
            else: return False
            i += 4
        else:
            w2 = r[i:i + 2]
            if w2 == [1, 1]: i += 2; continue
            odd = k & 1; k >>= 1
            if w2 == [0, 0]:
                if odd: r[i:i + 2] = [1, 0]
            elif w2 == [1, 0]:
                if odd: r[i:i + 2] = [0, 0]; k += 1
            else: return False
            i += 2; tp = 0
    return True
