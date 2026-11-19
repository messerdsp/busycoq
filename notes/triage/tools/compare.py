#!/usr/bin/env python3
"""Compare every candidate with the two studied machines (heuristic, from simulation logs and past notes).
usage: compare.py FASTPASS_DIR SOURCES_JSON ANALYSIS_JSON OUT_JSON
like13: a counter with walls and digit words, as in 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF:
        at returns to the dominant end, 3+ large runs whose successive size ratios are roughly constant (>= 1.8),
        with short material between them, and tape growth logarithmic; or notes naming a wall/odometer counter.
        Hard part of 13: the band slowly used up (drift) and overflows at growing scales.
like9:  a phase/timer structure with a counter word, as in 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA:
        at returns to the dominant end, the largest run mostly decreases step by step and is reset to a larger
        value at phase starts, the reset values growing; or notes naming a timer/phase/countdown.
        Hard part of #9: the lottery (pseudo-random runs decide a bad overflow).
Bonus written to OUT_JSON: +10 when the structure resembles one of them and the hard part is absent (by simulation
and notes), else 0 (the resemblance is still reported)."""
import gzip, json, math, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FP, SRC, AN, OUT = sys.argv[1:5]
RUN = re.compile(r'([01]+)\^(\d+)|\[(\d+)\]|\(([01]+)\)|([01]+)')
def runs_of(t):
    out = []
    for m in RUN.finditer(t):
        if m.group(1): out.append((m.group(1), int(m.group(2))))
        elif m.group(3): out.append((None, int(m.group(3))))
        else: out.append((m.group(4) or m.group(5), 1))
    return out
src = {r['machine']: r for r in json.load(open(SRC))}
an = {r['machine']: r for r in json.load(open(AN))}
res = {}
for m, a in an.items():
    r = src[m]
    p = os.path.join(FP, 'logs', m + '.log.gz')
    E = []
    if os.path.exists(p):
        for l in gzip.open(p, 'rt'):
            if l[0] == 'E':
                h, t = l.split('|', 1); h = h.split()
                E.append((h[1], int(h[2]), h[6], t))
    info = {}
    if len(E) >= 30:
        dom = Counter((e[0], e[2]) for e in E[len(E) // 2:]).most_common(1)[0][0]
        es = [e for e in E if (e[0], e[2]) == dom]
        # walls: geometric ratios among the large runs at the last returns
        geo = 0
        for e in es[-5:]:
            rr = runs_of(e[3]); cs = [c for b, c in rr if b]
            mx = max(cs) if cs else 0
            big = [c for c in cs if c >= 8 and c >= mx / 2000]
            if len(big) >= 3:
                bs = sorted(big, reverse=True)
                rat = [bs[i] / bs[i + 1] for i in range(len(bs) - 1)]
                mr = sum(rat) / len(rat); cv = (sum((x - mr) ** 2 for x in rat) / len(rat)) ** .5 / mr
                if mr >= 1.8 and cv < 0.35: geo += 1
        info['walls_geometric'] = geo >= 3
        # timer: largest run at successive returns
        mx = []
        for e in es[-400:]:
            cs = [c for b, c in runs_of(e[3]) if b]
            mx.append(max(cs) if cs else 0)
        dec = sum(1 for x, y in zip(mx, mx[1:]) if y < x); inc = sum(1 for x, y in zip(mx, mx[1:]) if y > x)
        jumps = [(x, y) for x, y in zip(mx, mx[1:]) if y > 1.3 * x and y - x > 5]
        info['timer'] = len(mx) > 20 and dec > 3 * max(1, inc - len(jumps)) and len(jumps) >= 2 and jumps[-1][1] > jumps[0][1]
        info['dominant_return'] = dom
    t = ' '.join([(r.get('ai') or {}).get('note', ''), (r.get('explorer') or {}).get('summary', ''),
                  (r.get('explorer') or {}).get('verdict', ''), (r.get('sheet') or {}).get('class', ''),
                  (r.get('ai') or {}).get('class', '')]).lower()
    n13 = bool(re.search(r'odometer|base-\d (counter|odometer)|nested [a-z -]*counter|digit words?|walls? form', t)) and 'counter' in t + 'odometer'
    n9 = bool(re.search(r'\btimer|countdown|counts? down|sync bouncer counter', t))
    shape = a.get('metrics', {}).get('shape')
    like13 = (info.get('walls_geometric') and shape in ('log', 'fixed')) or n13
    like9 = info.get('timer') or n9
    ss = a.get('signs', {})
    nt = t
    drift = 'drift' in ss or bool(re.search(r'drift|used up|slowly|eats ', nt))
    over = 'overflow' in ss or bool(re.search(r'(?<!shift-)overflow|collapse|rebuil|right-end events|events do not stop', ' '.join([(r.get('ai') or {}).get('note', ''),
             (r.get('explorer') or {}).get('summary', ''), (r.get('explorer') or {}).get('verdict', '')]).lower()))
    lot = 'lottery' in ss or (r.get('ai') or {}).get('status') == 'lottery' or bool(re.search(r'pseudo-?random|random walk|lottery|irregular|never repeats', nt))
    out = {'like13': bool(like13), 'like9': bool(like9), 'evidence': {**info, 'notes13': n13, 'notes9': n9}}
    bonus = 0; why = []
    if like13:
        absent = not drift and not over
        out['hard13_absent'] = absent
        why.append('13-like (%s); band drift %s, overflows at growing scales %s' % (
            'sim walls' if info.get('walls_geometric') else 'notes', 'seen' if drift else 'not seen', 'seen' if over else 'not seen'))
        if absent: bonus = 10
    if like9:
        absent = not lot
        out['hard9_absent'] = absent
        why.append('#9-like (%s); lottery %s' % ('sim timer' if info.get('timer') else 'notes', 'seen' if lot else 'not seen'))
        if absent: bonus = 10
    out['bonus'] = bonus; out['why'] = '; '.join(why) + ('; hard part absent' if bonus else '')
    res[m] = out
json.dump(res, open(OUT, 'w'), indent=1)
print('like13', sum(v['like13'] for v in res.values()), 'like9', sum(v['like9'] for v in res.values()),
      'with hard part absent', sum(1 for v in res.values() if v['bonus']))
