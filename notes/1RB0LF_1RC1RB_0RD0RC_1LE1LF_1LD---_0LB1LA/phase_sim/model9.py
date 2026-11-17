"""Model of #9 without machine sweeps: a carry sweep (after INC1) = digits below the parse stop reset to 0 plus a
local rule at the stop; the sweep after an overflow sets r[0] = 1. Any other sweep falls back to the machine and
is counted. With CHECK=1 every modelled sweep is also run on the machine and compared cell by cell."""
import os, sys, ctypes, collections
os.environ.setdefault('FILL', '10')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import M
from wavestate import _lib, LL
RULE = {'1110|1100': '1111|1100', '1110|1111': '1111|1111', '1110|1110': '1111|1110', '1110|1101': '1111|1101',
        '1110|0001': '1100|0111',
        '0110|1100': '0011|1100', '0110|1111': '0011|1111', '0110|1110': '0011|1110', '0110|1101': '0011|1101',
        '0110|0001': '0000|0111',
        '0111|0110': '0011|1110', '1111|0110': '1111|1110', '1111|0111': '1111|1111'}
RULEB = {k: bytes(int(c) for c in v.replace('|', '')) for k, v in RULE.items()}
_lib.zero_digits.restype = ctypes.c_int
_lib.zero_digits.argtypes = [ctypes.c_void_p, LL, LL, ctypes.c_int]
def zero_digits(B, i, stop):
    cb = (ctypes.c_uint8 * len(B)).from_buffer(B); r = _lib.zero_digits(ctypes.addressof(cb), i, stop, 1); del cb
    if r: raise ValueError('bad digit')
def zero_digits_py(B, i, stop):
    tp = 1
    while i < stop:
        if tp == 0:
            w = bytes(B[i:i + 4])
            if w == b'\0\1\1\0': B[i:i + 4] = b'\0\0\0\0'
            elif w == b'\0\1\1\1': B[i:i + 4] = b'\0\0\1\1'; tp = 1
            elif w == b'\0\0\1\1': tp = 1
            elif w != b'\0\0\0\0': raise ValueError('bad digit')
            i += 4
        else:
            w = bytes(B[i:i + 2])
            if w == b'\1\0': B[i:i + 2] = b'\0\0'; tp = 0
            elif w == b'\0\0': tp = 0
            elif w != b'\1\1': raise ValueError('bad digit')
            i += 2
class Model(M):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.last = None; self.stats = collections.Counter()
        self.check = os.environ.get('CHECK') == '1'
    def mstep(self):
        k = super().mstep(); self.last = k; return k
    def stop_cell(self):
        B = self.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B); s = LL(); md = ctypes.c_int()
        _lib.parse_stop(ctypes.addressof(cb), self.off, self.hi, 1, ctypes.byref(s), ctypes.byref(md)); del cb
        return s.value
    def sweep(self):
        o = self.off; pred = None
        if self.last == 'INC1':
            sc = self.stop_cell(); key = ''.join(map(str, self.buf[sc - 4:sc])) + '|' + ''.join(map(str, self.buf[sc:sc + 4]))
            if key in RULE:
                if not self.check:      # fast path: rewrite in place
                    zero_digits(self.buf, o, sc)
                    self.buf[sc - 4:sc + 4] = RULEB[key]; self.stats['carry'] += 1
                    if self.buf[self.hi:self.hi + 8].count(1): self.hi += 8
                    return
                pred = bytearray(self.buf); zero_digits(pred, o, sc)
                pred[sc - 4:sc + 4] = bytes(int(c) for c in RULE[key].replace('|', ''))
                kind = 'carry'
            else: self.stats['unknown ' + key] += 1
        elif self.last == 'OV' and self.buf[o] == 0:
            pred = bytearray(self.buf); pred[o] = 1; kind = 'ov'
        elif self.last == 'R11' and self.buf[o] == 0:
            pred = bytearray(self.buf); pred[o - 2] = 0; pred[o - 1] = 0; pred[o] = 1; kind = 'r11'
        if pred is None:
            self.stats['machine sweep after ' + str(self.last)] += 1
            if os.environ.get('STRICT') == '1' and self.last is not None: raise SystemExit('no rule for sweep after %s at phase %d' % (self.last, self.nov))
            return super().sweep()
        if self.check:
            super().sweep()
            same = pred[o - 4:self.hi + 8] == self.buf[o - 4:self.hi + 8]
            self.stats[kind + (' ok' if same else ' MISMATCH')] += 1
            if not same: raise SystemExit('mismatch at phase %d' % self.nov)
        else:
            self.buf[:] = pred; self.stats[kind] += 1
            if self.buf[self.hi:self.hi + 8].count(1): self.hi += 8
