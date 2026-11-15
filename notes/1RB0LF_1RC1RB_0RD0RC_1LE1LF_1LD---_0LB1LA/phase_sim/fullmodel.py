"""Exact full-tape run with the 13-rule model (no truncation, no machine sweeps; STRICT stops on any uncovered sweep).
Logs the first 24 tokens per phase, saves the full state every SAVE phases.
usage: STRICT=1 fullmodel.py STATE P1 OUTPREFIX [SAVE]"""
import os, sys, time, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state, toks, cells
from model9 import Model
from m9 import T37
st = load_state(sys.argv[1]); P1 = int(sys.argv[2]); OUT = sys.argv[3]; SAVE = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
m = Model(T37, st['a'], st['b'], st['r']); m.mode = st['mode']; m.nov = st['nov']
log = open(OUT + '.txt', 'a'); t0 = time.time()
def save():
    with gzip.open(f'{OUT}_state{m.nov}.txt.gz', 'wt') as f:
        f.write(f'nov {m.nov}\nmode {m.mode}\na {m.a:x}\nb {m.b:x}\nr {" ".join(toks(m.r_list()))}\n')
while m.nov < P1:
    k = m.mstep()
    if k == 'OV':
        log.write(f"{m.nov} {' '.join(toks(list(m.buf[m.off:min(m.hi, m.off + 300000)]))[:24])}\n")
        if m.nov % 500 == 0: print(m.nov, f'{time.time() - t0:.0f}s', 'bbits', m.b.bit_length(), 'rlen', m.hi - m.off, dict(m.stats), flush=True); log.flush()
        if m.nov % SAVE == 0:
            while m.mode != 'R': m.mstep()
            save()
print('end', m.nov, dict(m.stats))
