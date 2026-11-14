import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
m = M(TM2, 11, 5, [1, 0])
try:
    while True: m.mstep()
except (Halted, Stuck) as e:
    print('stopped:', type(e).__name__, e)
print('msteps', m.nmstep, 'overflows', m.nov, 'a bits', m.a.bit_length(), 'b bits', m.b.bit_length(), 'r len', m.hi - m.off, 'mode', m.mode)
