"""Run the exact 13-rule model from a full state; give every run an id and track it through the local edits between
phase starts. A run inside an edited block gets as parents the old runs whose cells overlap it (offsets measured
from the block start). Writes OUT.runs: one line per run when it dies (or at the end):
  id birth death length parent_ids
usage: STRICT=1 lineage.py STATE P1 OUT"""
import os, sys, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import load_state
from model9 import Model
from m9 import T37
st = load_state(sys.argv[1]); P1 = int(sys.argv[2]); OUT = sys.argv[3]
m = Model(T37, st['a'], st['b'], st['r']); m.mode = st['mode']; m.nov = st['nov']
_RX = re.compile(rb'\x00+|\x01+')
def tl():
    return [(1 if g[0] else 0, len(g)) for g in _RX.findall(bytes(m.buf[m.off:m.hi]))]
K = 6
def resync(a, b, i, j):
    for s in range(0, 60, 2):
        for di in range(0, s + 1):
            dj = s - di
            if i + di + K <= len(a) and j + dj + K <= len(b) and a[i + di:i + di + K] == b[j + dj:j + dj + K]:
                return di, dj
    return None
runs_out = open(OUT + '.runs', 'w'); nid = [0]
def new_id(): nid[0] += 1; return nid[0]
prev = tl(); ids = [new_id() if t[0] else 0 for t in prev]
info = {x: [m.nov, None, t[1], [], i, len(prev)] for i, (x, t) in enumerate(zip(ids, prev)) if x}
def kill(x, ph):
    b, _, L, par, pos, tot = info.pop(x); runs_out.write(f"{x} {b} {ph} {L} {','.join(map(str, par)) or '-'} {pos} {tot}\n")
t0 = time.time()
while m.nov < P1:
    if m.mstep() != 'OV': continue
    ph = m.nov
    cur = tl(); nids = [0] * len(cur)
    i = j = 0
    while i < len(prev) and j < len(cur):
        if prev[i] == cur[j]:
            nids[j] = ids[i]; i += 1; j += 1; continue
        r = resync(prev, cur, i, j)
        if r is None: di, dj = len(prev) - i, len(cur) - j
        else: di, dj = r
        # cell spans relative to block start
        old = []; p = 0
        for t, x in zip(prev[i:i + di], ids[i:i + di]):
            if t[0]: old.append((p, p + t[1], x))
            p += t[1]
        q = 0
        for jj in range(j, j + dj):
            t = cur[jj]
            if t[0]:
                par = [x for (a0, a1, x) in old if a0 < q + t[1] and q < a1]
                y = new_id(); nids[jj] = y; info[y] = [ph, None, t[1], par, jj, len(cur)]
            q += t[1]
        for (_, _, x) in old: kill(x, ph)
        i += di; j += dj
    for jj in range(j, len(cur)):
        if cur[jj][0]: y = new_id(); nids[jj] = y; info[y] = [ph, None, cur[jj][1], [], jj, len(cur)]
    for ii in range(i, len(prev)):
        if ids[ii]: kill(ids[ii], ph)
    prev, ids = cur, nids
    if ph % 250 == 0:
        with open(OUT + '.alive.tmp', 'w') as fa:
            for x, (b0, _, L0, par0, pos0, tot0) in info.items():
                fa.write(f"{x} {b0} alive {L0} {','.join(map(str, par0)) or '-'} {pos0} {tot0}\n")
        os.replace(OUT + '.alive.tmp', OUT + '.alive')
    if ph % 100 == 0: runs_out.flush(); print(ph, f'{time.time() - t0:.0f}s', len(cur), dict(m.stats), flush=True)
    if ph % 5000 == 0:
        import gzip
        with gzip.open(f'{OUT}_state{ph}.txt.gz', 'wt') as f:   # taken right after the overflow, before its sweep
            f.write(f"nov {m.nov}\nmode {m.mode}\na {m.a:x}\nb {m.b:x}\nr {' '.join(('o' if t[0] else 'z') + str(t[1]) for t in cur)}\n")
for x in list(info): kill(x, 'end')
