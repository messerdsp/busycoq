"""Exact position of the lowest wave: the cell where the digit parse of r stops, its token, the cell offset in that
token, the parse mode there, and d = digits parsed - v2(b + 3)."""
import os
import ctypes
LL = ctypes.c_longlong
_lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libparsestop.so'))
_lib.parse_stop.restype = LL
_lib.parse_stop.argtypes = [ctypes.c_void_p, LL, LL, ctypes.c_int, ctypes.POINTER(LL), ctypes.POINTER(ctypes.c_int)]
def wave_state(m):
    B = m.buf; cb = (ctypes.c_uint8 * len(B)).from_buffer(B); st = LL(); md = ctypes.c_int()
    nb = _lib.parse_stop(ctypes.addressof(cb), m.off, m.hi, 1, ctypes.byref(st), ctypes.byref(md))
    del cb
    cell = st.value - m.off
    x = m.b + 3; v = (x & -x).bit_length() - 1
    return cell, md.value, nb, nb - v
def locate(T, cell):
    """token index containing `cell` and offset inside it"""
    pos = 0
    for i, t in enumerate(T):
        n = int(t[1:])
        if pos + n > cell: return i, cell - pos
        pos += n
    return len(T), cell - pos
