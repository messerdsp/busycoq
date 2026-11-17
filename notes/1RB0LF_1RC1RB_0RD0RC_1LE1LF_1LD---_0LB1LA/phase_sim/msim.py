"""Macro simulator for #9 (and TM2 as a check), a port of SBCv9.v TM2.mstep with exact big-integer a, b and a
concrete counter word r. Configs: ('L', a, b) = LC a b {{{(hL',L)}}} r ; ('R', a, b) = LC a b {{{(hR',R)}}} r."""
import ctypes, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m9 import T37, TM2

lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libsweep.so'))
lib.sweep.restype = ctypes.c_longlong
LL = ctypes.c_longlong
lib.sweep.argtypes = [ctypes.c_void_p, LL, LL, ctypes.c_int, LL, ctypes.c_void_p, LL,
                      ctypes.POINTER(LL), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(LL)]
SI = {s: i for i, s in enumerate('ABCDEFG')}

def table(tm):
    tab = (ctypes.c_int * 14)()
    for i in range(14): tab[i] = 7 << 2
    for (s, y), tr in tm.items():
        if tr is None: tab[SI[s] * 2 + y] = 7 << 2
        else:
            w, d, n = tr; tab[SI[s] * 2 + y] = w | ((1 if d > 0 else 0) << 1) | (SI[n] << 2)
    return tab

INF = float('inf')
lib.parse_digits.restype = LL
lib.parse_digits.argtypes = [ctypes.c_void_p, LL, LL, ctypes.c_int, ctypes.c_void_p, LL, ctypes.POINTER(ctypes.c_int)]
lib.add_digits.restype = LL
lib.add_digits.argtypes = [ctypes.c_void_p, LL, ctypes.c_int, ctypes.c_void_p, LL]
_T01 = bytes.maketrans(b'\x00\x01', b'01'); _T10 = bytes.maketrans(b'01', b'\x00\x01')
class Halted(Exception): pass
class Stuck(Exception): pass

class M:
    def __init__(self, tm, a, b, r, cap=1 << 22):
        self.tab = table(tm); self.tm = tm
        self.buf = bytearray(cap); self.off = cap // 4
        self.buf[self.off:self.off + len(r)] = bytes(r)
        self.hi = self.off + len(r)          # exclusive bound of possibly-nonzero cells
        self.a, self.b, self.mode = a, b, 'L'
        self.nmstep = 0; self.nov = 0; self.sweep_steps = 0
    def grow(self):
        n = len(self.buf); nb = bytearray(2 * n); sh = n // 2
        nb[self.off + sh:self.hi + sh] = self.buf[self.off:self.hi]
        self.buf = nb; self.off += sh; self.hi += sh
    def pre(self, k):
        return list(self.buf[self.off:self.off + k])
    # --- counter word arithmetic on buf, starting in mode t1 (as mstep calls it) ---
    def rest_py(self, tp=1):
        i = self.off; bits = 0; nb = 0; B = self.buf; hi = self.hi
        while True:
            if i >= hi: return INF   # 0inf parses as endless 0000 digits (Coq: until fuel), capacity unbounded
            if tp == 0:
                w = B[i:i + 4]
                if w == b'\0\0\0\0': bits |= 1 << nb; nb += 1; i += 4
                elif w == b'\0\1\1\0': nb += 1; i += 4
                elif w == b'\0\0\1\1': bits |= 1 << nb; nb += 1; i += 4; tp = 1
                elif w == b'\0\1\1\1': nb += 1; i += 4; tp = 1
                else: return bits
            else:
                w = B[i:i + 2]
                if w == b'\1\1': i += 2
                elif w == b'\0\0': bits |= 1 << nb; nb += 1; i += 2; tp = 0
                elif w == b'\1\0': nb += 1; i += 2; tp = 0
                else: return bits
    def rincs_py(self, k, tp=1):
        i = self.off; B = self.buf
        while k:
            if tp == 0:
                w = B[i:i + 4]; odd = k & 1; k >>= 1
                if w == b'\0\0\0\0':
                    if odd: B[i:i + 4] = b'\0\1\1\0'
                elif w == b'\0\1\1\0':
                    if odd: B[i:i + 4] = b'\0\0\0\0'; k += 1
                elif w == b'\0\0\1\1':
                    if odd: B[i:i + 4] = b'\0\1\1\1'
                    tp = 1
                elif w == b'\0\1\1\1':
                    if odd: B[i:i + 4] = b'\0\0\1\1'; k += 1
                    tp = 1
                else: raise Stuck('rincs ran off digits')
                i += 4
            else:
                w = B[i:i + 2]
                if w == b'\1\1': i += 2; continue
                odd = k & 1; k >>= 1
                if w == b'\0\0':
                    if odd: B[i:i + 2] = b'\1\0'
                elif w == b'\1\0':
                    if odd: B[i:i + 2] = b'\0\0'; k += 1
                else: raise Stuck('rincs ran off digits')
                i += 2; tp = 0
        if i > self.hi: self.hi = i
    def rest(self, tp=1):
        B = self.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B); out = bytearray(1 << 20)
        co = (ctypes.c_uint8 * len(out)).from_buffer(out); tail = ctypes.c_int()
        nb = lib.parse_digits(ctypes.addressof(cb), self.off, self.hi, tp, ctypes.addressof(co), len(out), ctypes.byref(tail))
        del cb, co
        if nb < 0: raise Stuck('too many digits')
        if tail.value: return INF
        return int(bytes(out[nb - 1::-1]).translate(_T01) or b'0', 2) if nb else 0
    def rincs(self, k, tp=1):
        kb = bin(k)[:1:-1].encode().translate(_T10) if k else b''
        B = self.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B)
        kbb = bytearray(kb) or bytearray(1); ck = (ctypes.c_uint8 * len(kbb)).from_buffer(kbb)
        e = lib.add_digits(ctypes.addressof(cb), self.off, tp, ctypes.addressof(ck), len(kb))
        del cb, ck
        if e < 0: raise Stuck('rincs ran off digits')
        if e > self.hi: self.hi = e
    def sweep(self):
        """cfgR' -> cfgL': bounce (A,<[1;0;1]) -> (D,[0;1;1]) over r."""
        while self.off < 8 or len(self.buf) - self.hi < (1 << 16): self.grow()
        o = self.off; B = self.buf
        B[o - 1] = 1; B[o - 2] = 0; B[o - 3] = 1
        cbuf = (ctypes.c_uint8 * len(B)).from_buffer(B); cptr = ctypes.addressof(cbuf)
        op = ctypes.c_longlong(); os_ = ctypes.c_int(); hi = ctypes.c_longlong(self.hi)
        while True:
            n = lib.sweep(cptr, len(B) - 2, o, SI['A'], o - 4, self.tab, 1 << 40, ctypes.byref(op), ctypes.byref(os_), ctypes.byref(hi))
            if n == -2 and hi.value >= len(B) - 4:
                del cbuf; self.grow(); raise Stuck('grow during sweep: restart not supported')
            break
        del cbuf
        if n == -1: raise Halted(('halt in sweep', op.value - o, 'ABCDEFG'[os_.value]))
        if n < 0: raise Stuck('sweep limit')
        self.hi = max(self.hi, hi.value + 1); self.sweep_steps += n
        if 'ABCDEFG'[os_.value] != 'D' or bytes(B[o - 3:o]) != b'\0\1\1':
            raise Stuck(('sweep returned', 'ABCDEFG'[os_.value], list(B[o - 3:o])))
        B[o - 3:o] = b'\0\0\0'
    def mstep(self):
        if self.mode == 'R':
            self.sweep(); self.mode = 'L'; self.nmstep += 1; return 'sweep'
        a, b = self.a, self.b
        if a % 2 == 0 and self.tm is T37: raise Halted('a even: the left lemmas fail (halts)')
        p = self.pre(3)
        if p == [1, 0, 1]:
            self.a += 4; self.off += 2; self.buf[self.off] = 1; self.nmstep += 1; return 'R101'
        if p[:2] == [1, 1]:
            self.a += 4; self.off += 2; self.mode = 'R'; self.nmstep += 1; return 'R11'
        if b == 0:
            if a % 2 == 1 and p[:2] == [0, 0]:
                self.a, self.b = 3, 2 + a // 2
                self.off += 1; self.buf[self.off] = 0; self.mode = 'R'; self.nmstep += 1; self.nov += 1; return 'OV'
            raise Stuck('b=0 without LOv pattern')
        k = self.rest(1)
        if k == 0:
            self.a += 4; self.b -= 1; self.mode = 'R'; self.nmstep += 1; return 'INC1'
        k = b if k == INF else min(k, b)
        while self.hi + 4 * (k.bit_length() + 8) + (1 << 12) > len(self.buf): self.grow()
        self.rincs(k, 1)
        self.a += 4 * k; self.b -= k; self.nmstep += 1; return 'INCS'
    def r_list(self):
        return list(self.buf[self.off:self.hi])
