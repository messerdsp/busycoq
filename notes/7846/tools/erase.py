"""Erase experiment for 1RB0LA_1RC---_0LD1RD_0RA0RE_0RF1RC_1LF0LA.
Start: state A on the last 1 of  P 1^R  (blank to the left of P and to the right), i.e. the
configuration  0inf <* P <* [1]^^R <{{A}} 0inf  that the overflow of a level leaves behind.
Stop at the first time the head is in state A on a 0 with only blanks to its left, left of the
old position of P, and print the tape from the head on (the junk the next run starts from)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import parse_tm
from parse import rle
tm = parse_tm('1RB0LA_1RC---_0LD1RD_0RA0RE_0RF1RC_1LF0LA')

def run_erase(prefix, R=100, pad=200):
    tape = [0] * pad + [int(c) for c in prefix] + [1] * R + [0] * 400
    pos = pad + len(prefix) + R - 1; q = 'A'
    for st in range(1, 100000):
        w, d, nq = tm[(q, tape[pos])]
        tape[pos] = w; pos += 1 if d == 'R' else -1; q = nq
        if q == 'A' and tape[pos] == 0 and pos < pad + len(prefix) and not any(tape[:pos]):
            return st, pos - pad, ''.join(map(str, tape[pos:])).rstrip('0')
    return None

P0 = '1110110111110'                       # left part of the first (7-digit) level
P23 = P0 + '1' * 1322 + '0110'             # left part of the 22-digit level (m = 23)
for name, P in [('P0', P0), ('P23', P23)]:
    st, off, junk = run_erase(P)
    print(f"{name} = {rle(P)}: after {st} steps head at offset {off}, tape from head: {rle(junk)}")
    print(f"  raw junk: {junk}")
