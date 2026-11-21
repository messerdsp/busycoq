#!/usr/bin/env python3
"""Run a machine for a long time in checkpointed segments (tri.c with INIT and CKPT), resumable after a restart.
DIR holds: ckpt.txt (the current tape, INIT format), offset.txt (exact step count of that tape), progress.txt (one
line per segment). Each segment runs SECONDS of CPU, then on to the next return to an end, and writes the next
checkpoint. Stops on HALT, on LOOP, or after MAXSEG segments.
usage: longrun.py TRI MACHINE K DIR SECONDS MAXSEG [INIT_FILE OFFSET]   (INIT_FILE and OFFSET only for a fresh DIR)"""
import os, re, shutil, subprocess, sys, time
tri, M, K, D, secs, maxseg = sys.argv[1:7]
os.makedirs(D, exist_ok=True)
ck, off_f, prog = os.path.join(D, 'ckpt.txt'), os.path.join(D, 'offset.txt'), os.path.join(D, 'progress.txt')
if not os.path.exists(ck):
    shutil.copy(sys.argv[7], ck); open(off_f, 'w').write(sys.argv[8] + '\n')
for seg in range(int(maxseg)):
    off = int(open(off_f).read())
    t0 = time.time()
    o = subprocess.run([tri, M, K, '1e30', secs], capture_output=True, text=True,
                       env={'INIT': ck, 'CKPT': ck + '.new'}).stdout
    m = re.search(r'result=(\w+) steps=(\d+) cells=(\d+) runs=(\d+)', o)
    res, st, cells, runs = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    total = off + st
    if res == 'CKPT':
        toks = open(ck + '.new').read().split()
        far = ' '.join(toks[-4:] if toks[0] == 'L' else toks[2:6])
        os.replace(ck + '.new', ck); open(off_f, 'w').write('%d\n' % total)
    else:
        far = ''
    line = '%s total_steps=%d (%.4g) cells=%s runs=%s wall=%.0fs far_end: %s' % (res, total, total, cells, runs, time.time() - t0, far)
    open(prog, 'a').write(line + '\n'); print(line, flush=True)
    if res != 'CKPT': break
