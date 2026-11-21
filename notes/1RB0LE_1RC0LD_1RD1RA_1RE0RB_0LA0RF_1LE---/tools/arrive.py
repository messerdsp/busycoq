"""The frontier as a transducer (simulated).

An arrival is the end of a right pass: left `[digits] 0 1^(3c+3)` (the open block with the carried 1 1 1), head in
115779's A (23154's B) on the first cell of the right context t.  The core of every sweep leaves t unchanged
(Rocq: core_zero, core_even), so what matters is the map

    arrival(c, t)  -->  next left-pass start: head in 115779's D (23154's E) on a separator 0, with right context t'
                         (left side again digits)

This tool runs it for given t (block notation: B<n> = 0 0 (1 0)^n, U = 1 0 1 0 1 0, `110`, `1`, `0`, E = 0 0 1
then blank) and prints how the digits next to the frontier change and t'.  Usage: arrive.py "B1 B2 E" ...
"""
import sys, re
from ctl import parse_tm
tm = parse_tm('1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---')

def cells(spec):
    out = ''
    for tkn in spec.split():
        m = re.fullmatch(r'B(\d+)', tkn)
        if m: out += '00' + '10' * int(m.group(1)); continue
        if tkn == 'U': out += '101010'; continue
        if tkn == 'E': out += '001'; continue
        if re.fullmatch(r'[01]+', tkn): out += tkn; continue
        raise ValueError(tkn)
    return out

def blocks(s):
    s = s.rstrip('0'); out = []; i = 0
    while i < len(s):
        if s[i:] == '001': out.append('E'); break
        m = re.match(r'00((?:10)*)', s[i:])
        if m and m.end() > 2:
            n = len(m.group(1)) // 2
            # a block B_n immediately followed by `1` then `0 0 ...` or the end: keep as B_n then `1`
            out.append(f'B{n}'); i += m.end(); continue
        m = re.match(r'(?:101010)+', s[i:])
        if m: out.append('U' * (len(m.group(0)) // 6)); i += m.end(); continue
        out.append(s[i]); i += 1
    return ' '.join(out)

def digits(s):
    """decode a left half `1^r (0 1^n)*` into r and the list of block lengths"""
    s = s.lstrip('0'); parts = s.split('0')
    return len(parts[0]), [len(p) for p in parts[1:]]

def fmt_digits(ns):
    return ' '.join(str((n - 2) // 3) if n >= 2 and (n - 2) % 3 == 0 else f'[{n}]' for n in ns)

def arrival(c, tspec, pre=(1, 1, 1, 1), r=3, maxsteps=200000):
    left = '1' * r + ''.join('0' + '1' * (3 * d + 2) for d in pre) + '0' + '1' * (3 * c + 3)
    right = cells(tspec)
    tape = {}
    n0 = len(left)
    for i, ch in enumerate(left): tape[i - n0] = int(ch)
    for i, ch in enumerate(right): tape[i] = int(ch)
    pos, st = 0, 'A'
    mx = 0
    for t in range(maxsteps):
        b = tape.get(pos, 0)
        # left-pass start: D on a 0 with a 1 left of it, after the head has been right of the arrival point
        if st == 'D' and b == 0 and tape.get(pos - 1, 0) == 1 and t > 0:
            lo = min(k for k, v in tape.items() if v)
            L = ''.join(str(tape.get(k, 0)) for k in range(lo, pos))
            hi = max([k for k, v in tape.items() if v] + [pos])
            R = ''.join(str(tape.get(k, 0)) for k in range(pos + 1, hi + 1))
            rr, ns = digits(L)
            if ns and all(n >= 2 and (n - 2) % 3 == 0 for n in ns):
                return t, rr, ns, R
        tr = tm[(st, b)]
        if tr is None: return ('HALT', t)
        w, mv, ns_ = tr
        tape[pos] = w; pos += 1 if mv == 'R' else -1; st = ns_
    return ('NOLPS',)

if __name__ == '__main__':
    pre = (1, 1, 1, 1)
    for spec in sys.argv[1:]:
        for c in (0, 1, 2):
            res = arrival(c, spec, pre)
            if len(res) < 4: print(f'{spec:>24} c={c}: {res}'); continue
            t, rr, ns, R = res
            # digits after the fixed prefix
            print(f'{spec:>24} c={c}: t={t:5d} r={rr} digits: {fmt_digits(ns)}   t\' = {blocks(R)}')
