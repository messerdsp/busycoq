"""Record the lowest wave's state at each phase start: d and the tokens around the parse stop.
usage: wavefsm.py STATE N PHASES OUT"""
import os, sys, pickle
os.environ.setdefault('FILL', '10')
sys.path.insert(0, '/home/user/m9')
from lowsim import load_state, toks, trunc_state
from wavestate import wave_state, locate
st = load_state(sys.argv[1]); N = int(sys.argv[2]); PH = int(sys.argv[3])
m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, N + 200)
rec = []
end = st['nov'] + PH
while m.nov < end:
    k = m.mstep()
    if k == 'OV':
        T = toks(m.r_list()); cell, md, nb, d = wave_state(m); ti, off = locate(T, cell)
        rec.append((m.nov, d, ti, off, md, T[max(0, ti - 8):ti + 24], T[1]))
pickle.dump(rec, open(sys.argv[4], 'wb'))
print('done', len(rec))
