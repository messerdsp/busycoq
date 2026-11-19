#!/usr/bin/env python3
"""Score every candidate from simulation signs (analyze.py) and signs read from past notes (sources.json).
usage: score.py SOURCES_JSON ANALYSIS_JSON [EXTRA_JSON] OUT_JSON
EXTRA_JSON (optional): {machine: {"bonus": n, "why": "..."}} from the comparison with the studied machines.
Heuristic weights (see README "Method"):
  start 50; each fatal kind (lottery, collatz, nostruct, cryptid) -22, or -28 when simulation and notes agree;
  each manageable kind (drift, overflow, late, parts, rare) -5; compressible tape in simulation +8;
  rules proved in Rocq/Lean +10; an exact model/law +6; a reduction of halting to a precise statement +6;
  being worked on elsewhere (dedicated busy-beaver-explorer folder) -10, or recent heavy work there (notes of 190+
  lines with a status of 13 Nov 2026 or later) -8; a related table in an open PR -3.
"""
import json, re, sys
SRC, AN = sys.argv[1], sys.argv[2]
EXTRA = json.load(open(sys.argv[3])) if len(sys.argv) > 4 else {}
OUT = sys.argv[-1]
FATAL = ['lottery', 'collatz', 'nostruct', 'cryptid']
MANAGE = ['drift', 'overflow', 'late', 'parts', 'rare']
ACTIVE = {'1RB0RE_1LC0RA_1LA1LD_1LA---_0RF0LB_0LD1RE', '1RB1RA_1RC1LB_1LD0RA_---0LE_1LC0LF_1RE0LB',
          '1RB1RA_1LC1LD_1LD0LB_1RE0RF_---1RD_1RA1RB', '1RB1RA_1RC1LB_1LD0RA_1LB0LE_1LF1LD_---0LD',
          '1RB0LF_1RC0LB_1RD1RB_1RE1RF_1LA---_0RC1LA', '1RB1RF_1LC0LB_1RE0LD_1LB0RF_0RA0RC_1RE---'}
def notes_text(r):
    a = r.get('ai', {}); e = r.get('explorer', {}); s = r.get('sheet', {}); w = r.get('wiki_label', {})
    return ' '.join([a.get('note', ''), a.get('class', ''), e.get('summary', ''), e.get('verdict', ''),
                     s.get('class', ''), s.get('notes', ''), w.get('name', ''), w.get('desc', '')])
def note_signs(r):
    t = notes_text(r); tl = t.lower(); a = r.get('ai', {}); s = r.get('sheet', {}); w = r.get('wiki_label', {})
    cls = (a.get('class', '') + ' ' + s.get('class', '')).lower()
    sg = {}
    if a.get('status') == 'cryptid' or s.get('status') == 'CRYPTID' or 'cryptid' in (w.get('desc', '') + w.get('name', '')).lower():
        sg['cryptid'] = 'labelled a (potential) cryptid'
    if a.get('status') == 'lottery' or re.search(r'pseudo-?random|random walk|lottery|look(s)? random|random-looking|like random|look(s)? irregular|irregular lengths|irregular hierarchy|never repeats|chaotic wall|lengths look irregular', tl):
        sg['lottery'] = 'notes: random-looking statistics decide halting'
    if re.search(r'collatz|\b\d/\d map|\b3x ?/ ?2|3n/2|x ?→ ?3x|factors? near 1\.\d|by about 3/2|grows? \d/\d per', tl):
        sg['collatz'] = 'notes: Collatz-like map'
    if 'spaghetti' in cls or re.search(r'chaotic (bell|fractal|1dca|ack)', cls) or 'no structure' in tl:
        sg['nostruct'] = 'notes/class: chaotic, no usable structure'
    prose = ' '.join([a.get('note', ''), (r.get('explorer') or {}).get('summary', ''), (r.get('explorer') or {}).get('verdict', ''),
                      s.get('notes', '')]).lower()
    if re.search(r'(?<!shift-)overflow|collapse|rebuil|right-end events|events do not stop', prose): sg['overflow'] = 'notes: overflows/collapses'
    if re.search(r'drift|used up|slowly|eats ', tl): sg['drift'] = 'notes: slow drift'
    if re.search(r'\brare\b|exception|can in principle leave a halting|halting words? exist', tl): sg['rare'] = 'notes: rare events/exceptions'
    if re.search(r'two counters|bi-counter|registers|independent|several (counters|parts)|two-stack|nested', tl): sg['parts'] = 'notes: several interacting parts'
    pos = {}
    if a.get('status') == 'rules' or re.search(r'proved in (rocq|lean)|in lean \(kernel\)|rules? (are )?proved', tl) or e_kernel(r) >= 3:
        pos['rules_proved'] = 10
    if re.search(r'exact (law|model|macro|odometer|block macro|recursive|column|binary counter|token)', tl): pos['exact_model'] = 6
    if re.search(r'closed set gives|terminal regime|halts iff|reduces exactly|if and only if|never halt if|does not halt if', tl): pos['reduction'] = 6
    likely_halt = bool(re.search(r'probviously halting|likely (to )?halt|expected to halt|chance of halting', tl))
    return sg, pos, likely_halt
def e_kernel(r): return (r.get('explorer') or {}).get('kernel_claims', 0) or 0
src = {r['machine']: r for r in json.load(open(SRC))}
out = []
for a in json.load(open(AN)):
    m = a['machine']; r = src[m]
    ns, pos, lh = note_signs(r)
    ss = a.get('signs', {})
    score = 50; parts = []
    for k in FATAL:
        if k in ss and k in ns: score -= 28; parts.append('-28 %s (sim+notes)' % k)
        elif k in ss: score -= 22; parts.append('-22 %s (sim)' % k)
        elif k in ns: score -= 22; parts.append('-22 %s (notes)' % k)
    for k in MANAGE:
        if k in ss or k in ns: score -= 5; parts.append('-5 %s' % k)
    met = a.get('metrics', {})
    if met.get('rho', 1) < 0.2 and 'nostruct' not in ss: score += 8; parts.append('+8 compressible')
    for k, v in pos.items(): score += v; parts.append('+%d %s' % (v, k))
    if m in ACTIVE: score -= 10; parts.append('-10 active (explorer folder)')
    if r.get('related_in_pr'): score -= 3; parts.append('-3 related table in open PR')
    ex = r.get('explorer') or {}
    day = int(re.match(r'(\d+)', ex.get('asof') or '0').group(1)) if re.match(r'(\d+)', ex.get('asof') or '') else 0
    busy = m not in ACTIVE and ex.get('readme_lines', 0) >= 190 and day >= 13
    if busy: score -= 8; parts.append('-8 recent heavy work in busy-beaver-explorer (%d-line notes, %s)' % (ex['readme_lines'], ex.get('asof')))
    if m in EXTRA: score += EXTRA[m]['bonus']; parts.append('%+d %s' % (EXTRA[m]['bonus'], EXTRA[m]['why']))
    out.append({'id608': r['id608'], 'machine': m, 'score': score, 'why': parts, 'sim_signs': ss, 'note_signs': ns,
                'positive': pos, 'likely_halt_notes': lh, 'halted_sim': 'halt' in ss, 'metrics': met, 'K': a.get('K'),
                'steps': a.get('steps'), 'active': m in ACTIVE or busy, 'related_in_pr': r.get('related_in_pr', [])})
out.sort(key=lambda x: -x['score'])
json.dump(out, open(OUT, 'w'), indent=1)
for x in out[:25]: print(x['score'], x['id608'], x['machine'], '|', ', '.join(x['why']))
