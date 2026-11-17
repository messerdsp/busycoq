"""Check: the carry sweep = (every digit below the parse stop goes 1 -> 0) + (local rule at the stop) + (the fixed
bottom bookkeeping). Compares the predicted word with the real sweep, cell by cell above the low end."""
import os, sys, ctypes, collections
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, trunc_state
from wavestate import _lib, LL
RULE = {'1110|1100': '1111|1100', '1110|1111': '1111|1111', '0110|1100': '0011|1100', '1110|0001': '1100|0111',
        '0110|0001': '0000|0111', '0110|1111': '0011|1111', '1110|1110': '1111|1110'}
st = load_state(sys.argv[1]); P0, P1 = int(sys.argv[2]), int(sys.argv[3])
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], 700, 900)
def stop_cell(m):
    B = m.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B); s = LL(); md = ctypes.c_int()
    _lib.parse_stop(ctypes.addressof(cb), m.off, m.hi, 1, ctypes.byref(s), ctypes.byref(md)); del cb
    return s.value
def zero_digits(B, i, stop):
    tp = 1
    while i < stop:
        if tp == 0:
            w = bytes(B[i:i + 4])
            if w == b'\0\1\1\0': B[i:i + 4] = b'\0\0\0\0'
            elif w == b'\0\1\1\1': B[i:i + 4] = b'\0\0\1\1'; tp = 1
            elif w == b'\0\0\1\1': tp = 1
            elif w != b'\0\0\0\0': raise ValueError('bad digit %r at %d' % (w, i))
            i += 4
        else:
            w = bytes(B[i:i + 2])
            if w == b'\1\0': B[i:i + 2] = b'\0\0'; tp = 0
            elif w == b'\0\0': tp = 0
            elif w != b'\1\1': raise ValueError('bad digit %r' % w)
            i += 2
stats = collections.Counter(); ex = []; LEARN = {}
while m.nov < P1:
    k = m.mstep()
    if k != 'INC1' or m.nov < P0: continue
    sc = stop_cell(m); o = m.off
    pred = bytearray(m.buf); zero_digits(pred, o, sc)
    key = ''.join(map(str, pred[sc - 4:sc])) + '|' + ''.join(map(str, m.buf[sc:sc + 4]))
    # the zeroing changes the 4 cells below the stop too, so key the rule on the ORIGINAL cells
    key0 = ''.join(map(str, m.buf[sc - 4:sc])) + '|' + ''.join(map(str, m.buf[sc:sc + 4]))
    learned = key0 not in RULE
    if not learned:
        new = RULE[key0].replace('|', '')
        pred[sc - 4:sc + 4] = bytes(int(c) for c in new)
    m.mstep()                     # the real sweep
    real = m.buf
    if learned:
        obs = ''.join(map(str, real[sc - 4:sc])) + '|' + ''.join(map(str, real[sc:sc + 4]))
        LEARN.setdefault(key0, collections.Counter())[obs] += 1
        pred[sc - 4:sc + 4] = real[sc - 4:sc + 4]
    diff = [i - o for i in range(o, m.hi + 4) if pred[i] != real[i]]
    stats['exact' if not diff else 'differs'] += 1
    if diff and len(ex) < 5: ex.append((m.nov, sc - o, diff[:10], len(diff)))
print(dict(stats)); [print(e) for e in ex]
for k, v in LEARN.items(): print('LEARNED', k, dict(v))
