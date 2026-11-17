"""Fast exact simulation of the low part of r: keep the first N tokens of r and b mod 2^K (plus a large filler
above bit K so every phase still delivers its carries). Influence only goes up (tokens and bits of b), so the
low tokens are exact as long as N, K are well above what is logged.
usage: lowsim.py (CKPT | start:PHASE) N K MAXPH OUT [LOWN]"""
import sys, pickle, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msim import *
def toks(r):
    out = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        out.append(('o' if r[i] else 'z') + str(j - i)); i = j
    return out
def cells(tk):
    r = []
    for t in tk: r += [1 if t[0] == 'o' else 0] * int(t[1:])
    return r
FILL = int(os.environ['FILL']) if os.environ.get('FILL') else None   # filler bits above bit K (default K // 2)
def fill(b, K): return b % 2**K + 2**K * (2**(FILL if FILL is not None else K // 2) - 1)
def trunc_state(a, b, r, mode, nov, N, K):
    T = toks(r)[:N]
    if T[-1][0] == 'z': T = T[:-1]
    m = M(T37, a, fill(b, K), cells(T)); m.mode = mode; m.nov = nov
    return m
def load_state(src):
    """start:PHASE (simulate from the blank-tape start), stateNNNN.txt.gz (a, b in hex, r as run tokens) or a pickle."""
    if src.startswith('start:'):
        P0 = int(src[6:]); m0 = M(T37, 11, 5, [1, 0])
        while m0.nov < P0: m0.mstep()
        return dict(a=m0.a, b=m0.b, r=m0.r_list(), mode=m0.mode, nov=m0.nov)
    if src.endswith('.txt.gz'):
        import gzip
        st = dict(l.rstrip('\n').split(' ', 1) for l in gzip.open(src, 'rt'))
        return dict(a=int(st['a'], 16), b=int(st['b'], 16), mode=st['mode'], nov=int(st['nov']), r=cells(st['r'].split()))
    return pickle.load(open(src, 'rb'))
if __name__ == '__main__':
    src, N, K, MAXPH, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    LOWN = int(sys.argv[6]) if len(sys.argv) > 6 else 24
    st = load_state(src)
    m = trunc_state(st['a'], st['b'], st['r'], st['mode'], st['nov'], N, K)
    JUMP = os.environ.get('JUMP') == '1'; Q = K + 100; quiet = 0; prevT = None; exc = open(OUT + '.exc', 'w')
    out = open(OUT, 'w'); t0 = time.time(); tp = t0; KC = {}; DBG = os.environ.get('DBG') == '1'
    try:
        while m.nov < MAXPH:
            k = m.mstep(); KC[k] = KC.get(k, 0) + 1
            if k == 'OV':
                if FILL is not None: m.b = fill(m.b, K)   # bits of b above K only reach tokens above N
                if DBG and time.time() - tp > 0.3: print('slow', m.nov, f"{time.time() - tp:.2f}", KC, 'rlen', m.hi - m.off, 'bbits', m.b.bit_length(), flush=True)
                tp = time.time(); KC.clear()
                T = toks(m.r_list()[:4_000_000])
                out.write(f"{m.nov} {' '.join(T[:LOWN])}\n")
                cur = T[2:N - 100]
                quiet = quiet + 1 if cur == prevT else 0
                prevT = cur
                if T[0] != 'z3': exc.write(f"{m.nov} {' '.join(T[:8])}\n"); exc.flush()
                L = int(T[1][1:]) if T[0] == 'z3' else 0
                if JUMP and quiet >= Q and L > 200 and m.b % 2**K == 2**K - 3:
                    j = L - 100; T[1] = 'o' + str(L - j)
                    m = trunc_state(m.a, m.b, cells(T), m.mode, m.nov + j, N, K)
                    exc.write(f"JUMP {m.nov - j} -> {m.nov}\n"); quiet = 0; prevT = None
                    continue
                if m.nov % 500 == 0:
                    out.flush(); print(m.nov, f"{time.time() - t0:.0f}s", 'rlen', m.hi - m.off, flush=True)
    except (Halted, Stuck) as e:
        out.write(f"STOP {type(e).__name__} {e} nov={m.nov}\n"); print('STOP', e, m.nov)
    out.close()
