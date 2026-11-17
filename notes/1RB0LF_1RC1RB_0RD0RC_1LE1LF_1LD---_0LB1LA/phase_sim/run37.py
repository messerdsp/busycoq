import os, sys, time, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
OUT = sys.argv[1]; MAXPH = int(sys.argv[2])
if len(sys.argv) > 3:
    st = pickle.load(open(sys.argv[3], 'rb'))
    m = M(T37, st['a'], st['b'], st['r']); m.mode = st['mode']; m.nov = st['nov']; m.nmstep = st['nmstep']
else:
    m = M(T37, 11, 5, [1, 0])
log = open(OUT + '.log', 'a'); lowlog = open(OUT + '.low', 'a'); t0 = time.time(); ms0 = m.nmstep; kinds = {}
def ckpt():
    pickle.dump({'a': m.a, 'b': m.b, 'r': m.r_list(), 'mode': m.mode, 'nov': m.nov, 'nmstep': m.nmstep},
                open(OUT + '.ckpt.tmp', 'wb')); os.replace(OUT + '.ckpt.tmp', OUT + '.ckpt')
try:
    while m.nov < MAXPH:
        aprev = m.a
        k = m.mstep(); kinds[k] = kinds.get(k, 0) + 1
        if k == 'OV':
            B = m.buf; i = m.off; low = []
            while len(low) < 24 and i < m.hi:
                j = i
                while j < m.hi and B[j] == B[i]: j += 1
                low.append(('o' if B[i] else 'z') + str(j - i)); i = j
            lowlog.write(f"{m.nov} {' '.join(low)}\n"); lowlog.flush()
            # phase m.nov starts; b = 2 + a/2 of the old a
            log.write(f"{m.nov} b_bits={m.b.bit_length()} b_mod16={m.b % 16} rlen={m.hi - m.off} msteps={m.nmstep - ms0} "
                      f"kinds={kinds} sweep_steps={m.sweep_steps} t={time.time() - t0:.1f}\n"); log.flush()
            ms0 = m.nmstep; kinds = {}; m.sweep_steps = 0
            if m.nov % 100 == 0: ckpt()
except (Halted, Stuck) as e:
    log.write(f"STOP {type(e).__name__} {e} nov={m.nov} mode={m.mode} a_mod4={m.a % 4} b_bits={m.b.bit_length()}\n")
    ckpt()
log.close()
