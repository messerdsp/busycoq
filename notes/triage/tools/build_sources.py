#!/usr/bin/env python3
"""Join the 608-holdout list with past research. Writes ../data/sources.json and ../data/candidates.txt.
Inputs (paths given on the command line, read as data only):
  --h608 BB6_holdouts_608.txt  --sheet sheet.csv  --prs pr_machines.txt  --bb6after bb6_after_list.txt
  --explorer busy-beaver-explorer/holdouts  --ai ai_artifact.json
"""
import argparse, csv, glob, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canon import canon
RE = re.compile(r'([01-][LR-][A-Z-]){2}(_([01-][LR-][A-Z-]){2}){5}')
STUDIED = {canon('1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA'): '#9 (branch bb6-1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA)',
           canon('1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF'): '13 (branch bb6-1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF)'}
def strip(s): return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()
ap = argparse.ArgumentParser()
for a in ['h608', 'sheet', 'prs', 'bb6after', 'explorer', 'ai', 'out']: ap.add_argument('--' + a)
a = ap.parse_args()
rows = []
for l in open(a.h608):
    p = l.split()
    if len(p) >= 2: rows.append({'id608': int(p[0]), 'machine': p[1], 'canon': canon(p[1])})
by = {r['canon']: r for r in rows}
# open / unmerged PRs (#43 and later, plus #3 #4 #40 which still have merge refs)
for l in open(a.prs):
    n, date, who, ms = l.rstrip('\n').split('|')
    n = int(n)
    if not (n >= 43 or n in (3, 4, 40)): continue
    for m in ms.split():
        c = canon(m)
        if c in by: by[c].setdefault('pr', []).append(f'#{n} {who} {date}')
for m in open(a.bb6after).read().split():
    c = canon(m)
    if c in by: by[c]['bb6_after_list'] = True
for c, why in STUDIED.items():
    if c in by: by[c]['studied'] = why
# spreadsheet
for r in csv.reader(open(a.sheet)):
    mm = RE.search(r[0]) if r else None
    if not mm: continue
    c = canon(mm.group(0))
    if c in by:
        by[c]['sheet'] = {'status': r[1].replace('Status ', ''), 'class': r[2].replace('Classification ', ''),
                          'notes': r[3].replace('Notes ', '')[:400], 'by': r[5].replace('Done By ', '')}
# explorer
for f in glob.glob(os.path.join(a.explorer, '*', 'status.json')) + glob.glob(os.path.join(a.explorer, '..', 'bb6-*', 'status.json')):
    try: d = json.load(open(f))
    except Exception: continue
    m = d.get('machine') or os.path.basename(os.path.dirname(f))
    mm = RE.search(m)
    if not mm: continue
    c = canon(mm.group(0))
    if c in by:
        by[c]['explorer'] = {'decision': d.get('decision'), 'generated': d.get('generated'), 'group': d.get('group'),
                             'summary': strip(d.get('summary'))[:400],
                             'verdict': strip(' '.join(d.get('verdict') or []))[:1200],
                             'nclaims': len(d.get('claims') or []),
                             'kernel_claims': sum(1 for x in d.get('claims') or [] if x.get('level') == 'kernel')}
ext = json.load(open(os.path.join(a.explorer, 'external.json')))
for m, d in ext.get('machines', {}).items():
    c = canon(m)
    if c in by: by[c]['explorer_external'] = d
known = json.load(open(os.path.join(a.explorer, 'known.json')))
for m, d in known.items():
    if m.startswith('_'): continue
    c = canon(m)
    if c in by: by[c]['wiki_label'] = {'name': d[0], 'desc': d[1], 'page': (d[2] or {}).get('page') if len(d) > 2 else None}
for g in json.load(open(os.path.join(a.explorer, 'groups.json'))):
    for m in g.get('machines', []):
        c = canon(m)
        if c in by: by[c]['explorer_family'] = g['group'] + ': ' + g.get('family', '')
rel = json.load(open(os.path.join(a.explorer, 'related.json')))
for kind in ('same_table', 'same_run', 'same_tapes'):
    for g in rel.get(kind, []):
        ms = [canon(m) for m in g['machines']]
        for c in ms:
            if c in by:
                for o in ms:
                    if o != c: by[c].setdefault('related', []).append([kind, by[o]['machine'] if o in by else o])
for g in rel.get('slowed', []):
    ms = [canon(g['slow']), canon(g['fast'])]
    for c in ms:
        if c in by:
            for o in ms:
                if o != c: by[c].setdefault('related', []).append(['slowed', by[o]['machine'] if o in by else o])
for r in rows:
    sib = [m for k, m in r.get('related', []) if canon(m) in by and by[canon(m)].get('pr')]
    if sib: r['related_in_pr'] = sorted(set(sib))
for d in json.load(open(a.ai)):
    c = canon(d['m'])
    if c in by: by[c]['ai'] = {'status': d['s'], 'note': d['t'], 'class': d['c'], 'simulated': d['r'], 'pr': d['p']}
os.makedirs(a.out, exist_ok=True)
json.dump(rows, open(os.path.join(a.out, 'sources.json'), 'w'), indent=1)
cand = [r for r in rows if not r.get('pr') and not r.get('bb6_after_list') and not r.get('studied')]
with open(os.path.join(a.out, 'candidates.txt'), 'w') as f:
    for r in cand: f.write(f"{r['id608']} {r['machine']}\n")
print('with wiki label:', sum(1 for r in rows if r.get('wiki_label')), ' related machine in a PR:', sum(1 for r in cand if r.get('related_in_pr')))
print('608 list:', len(rows), ' in open/unmerged PR:', sum(1 for r in rows if r.get('pr')),
      ' proved in BB6 after list:', sum(1 for r in rows if r.get('bb6_after_list')),
      ' studied:', sum(1 for r in rows if r.get('studied')), ' candidates:', len(cand))
