"""Run-length Turing machine simulator with chain steps (a whole run crossed at once when the machine walks
through it without changing state). Tape: left and right stacks of [sym, count] runs, nearest run last."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m9 import T37
class Halt(Exception): pass
def push(stack, sym, n):
    if n <= 0: return
    if stack and stack[-1][0] == sym: stack[-1][1] += n
    else: stack.append([sym, n])
def pop1(stack):
    if not stack: return 0
    s = stack[-1][0]; stack[-1][1] -= 1
    if stack[-1][1] == 0: stack.pop()
    return s
def run(tm, left, cur, right, st, max_steps=10**6):
    """left/right: lists of [sym, n], nearest last. cur: symbol under head. Returns final state or raises Halt."""
    macro = 0
    while macro < max_steps:
        macro += 1
        tr = tm[(st, cur)]
        if tr is None: raise Halt((st, macro, left[-3:], cur, right[-3:]))
        w, d, nst = tr
        src, dst = (right, left) if d > 0 else (left, right)
        if nst == st and src and src[-1][0] == cur and w != cur or (nst == st and src and src[-1][0] == cur):
            # chain: write w on cur and on the whole run of `cur` ahead, ending on the cell after it
            n = src[-1][1]; src.pop()
            push(dst, w, 1 + n)
            cur = pop1(src)
            continue
        tr2 = tm.get((nst, cur))
        if tr2 is not None and tr2[1] == d and tr2[0] == w and tr2[2] == st and src and src[-1][0] == cur:
            # two-state walk over a run of `cur`: X,Y,X,Y,... each writing w; total cells = 1 + n
            n = src[-1][1]; src.pop()
            push(dst, w, 1 + n)
            st = st if (1 + n) % 2 == 0 else nst
            cur = pop1(src)
            continue
        push(dst, w, 1); cur = pop1(src); st = nst
    return st, left, cur, right
