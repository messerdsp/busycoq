#!/usr/bin/env python3
"""Fast pass: for every machine in candidates.txt, probe block sizes K=1..8 (PROBE seconds each), keep the K that
compresses best (most tape cells per run at the end of the probe; within 10% of the best, the K that simulated
more steps), then run that K for MAIN seconds with a log (gzipped).
usage: fastpass.py TRI candidates.txt OUTDIR [PROBE MAIN JOBS]
writes OUTDIR/logs/<machine>.log and appends one JSON line per machine to OUTDIR/fastpass.jsonl (resumable)."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
TRI, CAND, OUT = sys.argv[1:4]
PROBE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
MAIN = float(sys.argv[5]) if len(sys.argv) > 5 else 20
JOBS = int(sys.argv[6]) if len(sys.argv) > 6 else 4
os.makedirs(os.path.join(OUT, 'logs'), exist_ok=True)
res_path = os.path.join(OUT, 'fastpass.jsonl')
done = set()
if os.path.exists(res_path):
    for l in open(res_path): done.add(json.loads(l)['machine'])
def parse(o):
    d = dict(re.findall(r'(\w+)=(\S+)', o))
    return {'K': int(d['K']), 'result': d['result'], 'steps': int(d['steps']), 'cells': int(d['cells']),
            'runs': int(d['runs']), 'macro': int(d['macro']), 'chain': int(d['chain']), 'secs': float(d['secs']),
            'recL': int(d['recL']), 'recR': int(d['recR'])}
def one(line):
    i, m = line.split()
    probes = []
    for k in range(1, 9):
        o = subprocess.run([TRI, m, str(k), '1e30', str(PROBE)], capture_output=True, text=True).stdout
        p = parse(o); probes.append(p)
        if p['result'] != 'RUN': break
    stop = [p for p in probes if p['result'] != 'RUN']
    if stop: best = stop[0]
    else:
        cmax = max(p['cells'] / p['runs'] for p in probes)
        best = max((p for p in probes if p['cells'] / p['runs'] >= 0.9 * cmax), key=lambda p: p['steps'])
    log = os.path.join(OUT, 'logs', m + '.log')
    if best['result'] == 'RUN':
        o = subprocess.run([TRI, m, str(best['K']), '1e30', str(MAIN), log], capture_output=True, text=True).stdout
        main = parse(o)
        subprocess.run(['gzip', '-f', log])
    else:
        main = best
    return {'id608': int(i), 'machine': m, 'probes': [{k: p[k] for k in ('K', 'result', 'steps', 'runs', 'cells')} for p in probes],
            'cells_per_run': [round(p['cells'] / p['runs'], 2) for p in probes],
            'main': main}
todo = [l for l in open(CAND) if l.strip() and l.split()[1] not in done]
with ThreadPoolExecutor(JOBS) as ex, open(res_path, 'a') as f:
    for r in ex.map(one, todo):
        f.write(json.dumps(r) + '\n'); f.flush()
        print(r['id608'], r['machine'], r['main']['K'], r['main']['result'], '%.3g' % r['main']['steps'], flush=True)
