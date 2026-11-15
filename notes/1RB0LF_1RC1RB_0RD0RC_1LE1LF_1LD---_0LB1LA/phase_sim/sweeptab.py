"""Tabulate every carry sweep (the sweep after each INC1) by the cell window around the parse stop.
Long runs of 1s are compressed to 1^k with k = 6 + (n mod 2) when n > 7.  usage: sweeptab.py STATE P0 P1 OUT"""
import os, sys, pickle, re
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, trunc_state
from wavestate import _lib, LL
import ctypes
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3]); OUT = sys.argv[4]
N, K = 700, 900
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
def stop_cell(m):
    B = m.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B); s = LL(); md = ctypes.c_int()
    _lib.parse_stop(ctypes.addressof(cb), m.off, m.hi, 1, ctypes.byref(s), ctypes.byref(md)); del cb
    return s.value, md.value
def comp(bits):
    s = ''.join(map(str, bits))
    return re.sub(r'1{8,}', lambda mm: '1' * (6 + len(mm.group()) % 2) + '+', s)
rows = []; W = 40
while m.nov < P1:
    k = m.mstep()
    if k != 'INC1' or m.nov < P0: continue
    sc, md = stop_cell(m)
    lo, hi = sc - W, sc + W
    if lo < m.off + 8: continue
    before = list(m.buf[lo:hi]); full_before = bytes(m.buf[m.off:m.hi + 4])
    k2 = m.mstep(); assert k2 == 'sweep'
    after = list(m.buf[lo:hi]); full_after = bytes(m.buf[m.off:m.off + len(full_before)])
    ch = [i for i in range(8, len(full_before)) if full_before[i] != full_after[i]]
    near = [i + m.off - sc for i in ch if abs(i + m.off - sc) < 2000]
    far = [i for i in ch if abs(i + m.off - sc) >= 2000]
    rel = (min(near), max(near)) if near else None
    farr = (min(far), max(far)) if far else None
    rows.append(dict(ph=m.nov, pos=(sc - m.off) % 4, md=md, before=before, after=after, rel=rel, far=farr, stopidx=sc - m.off))
pickle.dump(rows, open(OUT, 'wb')); print('sweeps', len(rows))
