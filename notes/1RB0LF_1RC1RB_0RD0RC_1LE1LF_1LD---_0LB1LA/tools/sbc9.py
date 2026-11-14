#!/usr/bin/env python3
"""Exact (cell-level) experiments for the BB(6) holdout
    1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA

Sample point: state C reading 0 at the right end of the visited tape.  At every sample
the tape is  W 1^K 0^Z  (W = counter region, see ../README.md).

  python3 sbc9.py sweep  "<bits>"        one sweep from tape <bits> + head C>0 at its right end
  python3 sbc9.py count  "<bits>" [m] [n] iterate the 8-sweep counter step F n times from X=<bits>
  python3 sbc9.py check                  self-test against values observed in the direct run
"""
import sys

TM = '1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA'

def parse(m):
    t = {}
    for s, grp in enumerate(m.split('_')):
        for b in range(2):
            x = grp[3 * b:3 * b + 3]
            t[(s, b)] = None if x[2] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return t

T = parse(TM)

def rle(s):
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f'{s[i]}^{j - i}')
        i = j
    return ' '.join(out)

def unrle(s):
    return ''.join(b * int(n) for b, n in (t.split('^') for t in s.split()))

def sweep(left, maxsteps=10 ** 8):
    """Run from  0^inf <left> C> 0^inf  to the next sample point.
    Returns (new_left, steps), ('HALT', steps) or (None, steps) on timeout.
    new_left is the tape from the leftmost visited cell up to (excluding) the head."""
    tape = dict(enumerate(map(int, left)))
    pos, st, hi, lo = len(left), 2, len(left), 0
    for i in range(maxsteps):
        b = tape.get(pos, 0)
        if i > 0 and st == 2 and b == 0 and pos == hi:
            return ''.join(str(tape.get(p, 0)) for p in range(min(lo, 0), pos)), i
        tr = T[(st, b)]
        if tr is None:
            return 'HALT', i
        w, d, ns = tr
        tape[pos] = w
        pos += d
        st = ns
        hi, lo = max(hi, pos), min(lo, pos)
    return None, maxsteps

def counter_step(X, m=30, K=81, Z=8):
    """F: 8 sweeps from  X 1^m 0^3 1^K 0^Z  (a (c, K mod 8) = (3, 1) sample).
    Returns (X', m') or 'HALT'."""
    L = X + '1' * m + '000' + '1' * K + '0' * Z
    for _ in range(8):
        L, _n = sweep(L)
        if L in ('HALT', None):
            return 'HALT'
    s = L.rstrip('0')
    j = s.rfind('0001')          # the 0^3 tail separating the block 1^m' from 1^K'
    blk = s[:j]
    k = len(blk) - len(blk.rstrip('1'))
    return blk[:len(blk) - k], k

def check():
    # one observed S_h sweep (sample at step 38,860,428; K = 6661 ~ 61 mod 8)
    L = unrle('1^2 0^2 1^2 0^5 1^2 0^2 1^32 0^2') + '1' * 61 + '0' * 124
    r, n = sweep(L)
    assert rle(r) == '1^2 0^2 1^2 0^1 1^2 0^7 1^30 0^4 1^58 0^128', rle(r)
    # counter in phase K0 = 6718: 16-cell window counts in binary
    X, seq = '1100110000000000', []
    for _ in range(4):
        X, m = counter_step(X)
        seq.append(X)
        assert m == 30
    assert seq == ['1100110000011000', '1100110110000000', '1100110110011000', '1100111100000000'], seq
    print('ok')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'sweep':
        r, n = sweep(sys.argv[2])
        print(r if r in ('HALT', None) else rle(r), n)
    elif cmd == 'count':
        X = sys.argv[2]
        m = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
        for i in range(n):
            print(i, rle(X), ' m =', m)
            r = counter_step(X, m)
            if r == 'HALT':
                print('HALT')
                break
            X, m = r
    else:
        check()
