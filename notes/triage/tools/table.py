#!/usr/bin/env python3
"""Write the table of all scored machines as Markdown (TABLE.md) and TSV (data/table.tsv).
usage: table.py SOURCES_JSON SCORES_JSON COMPARE_JSON OUTDIR"""
import json, os, sys
SRC, SC, CMP, OUT = sys.argv[1:5]
src = {r['machine']: r for r in json.load(open(SRC))}
cmp_ = json.load(open(CMP))
sc = json.load(open(SC))
ABBR = {'lottery': 'LOT', 'collatz': 'COL', 'nostruct': 'NOS', 'cryptid': 'CRY', 'drift': 'dr', 'overflow': 'ov',
        'late': 'la', 'parts': 'pa', 'rare': 're', 'halt': 'HALT', 'loop': 'LOOP'}
def fmt_signs(d): return ' '.join(ABBR.get(k, k) for k in d)
def past(r):
    bits = []
    a = r.get('ai') or {}
    if a: bits.append('AI:%s' % a.get('status'))
    s = r.get('sheet') or {}
    if s.get('class'): bits.append('sheet:%s' % s['class'])
    if s.get('status'): bits.append(s['status'])
    e = r.get('explorer') or {}
    if e.get('kernel_claims'): bits.append('explorer:%d Lean claims' % e['kernel_claims'])
    w = r.get('wiki_label') or {}
    if w.get('name'): bits.append('wiki:%s' % w['name'])
    if r.get('related_in_pr'): bits.append('related table in PR')
    return '; '.join(bits)
rows = []
for i, x in enumerate(sc, 1):
    r = src[x['machine']]; c = cmp_.get(x['machine'], {})
    like = ','.join(k for k in ('like13', 'like9') if c.get(k)).replace('like13', '13').replace('like9', '#9')
    sim = x.get('metrics', {})
    rows.append([i, x['score'], x['id608'], x['machine'], x.get('K') or '', '%.2g' % x['steps'] if x.get('steps') else '',
                 sim.get('shape', ''), sim.get('rho', ''), fmt_signs(x['sim_signs']), fmt_signs(x['note_signs']), like,
                 past(r), (r.get('ai') or {}).get('note', '')[:140].replace('|', '/')])
hdr = ['rank', 'score', 'id', 'machine', 'K', 'sim steps', 'growth', 'runs/block', 'sim signs', 'note signs',
       'resembles', 'past research', 'AI note (first 140 chars)']
os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
with open(os.path.join(OUT, 'data', 'table.tsv'), 'w') as f:
    f.write('\t'.join(hdr) + '\n')
    for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
with open(os.path.join(OUT, 'TABLE.md'), 'w') as f:
    f.write('# All 520 candidates (simulated and read from notes; nothing here is proved)\n\n')
    f.write('Signs: fatal in capitals (LOT lottery, COL Collatz-like, NOS no structure, CRY cryptid label), manageable in '
            'lower case (dr drift, ov overflows, la late changes, pa several parts, re rare exceptions). "sim signs" come '
            'from the fast-pass simulation (`tools/analyze.py`), "note signs" from past notes (`tools/score.py`). '
            'Growth = shape of tape length against steps in the last three decades of the run; runs/block = runs × K / '
            'cells at the end (low = compressible). Resembles: 13 = counter with walls and digit words, #9 = '
            'phase/timer with a counter word (`tools/compare.py`). Same data as TSV: `data/table.tsv`.\n\n')
    f.write('| ' + ' | '.join(hdr) + ' |\n|' + '---|' * len(hdr) + '\n')
    for r in rows: f.write('| ' + ' | '.join(str(x) for x in r[:3]) + ' | `' + r[3] + '` | ' + ' | '.join(str(x) for x in r[4:]) + ' |\n')
print('wrote', len(rows), 'rows')
