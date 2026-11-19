#!/usr/bin/env python3
"""Turn fast-pass logs into warning signs (heuristic, from simulation only).
usage: analyze.py FASTPASS_DIR SOURCES_JSON OUT_JSON
Signs from the simulation log (each a heuristic proxy, see README "Method"):
  halt        the run halted (exact step count)
  nostruct    tape incompressible at every block size: rho = runs*K/cells > 0.5 at the end and runs grow with the tape
  lottery     walls exist but the material between them is irregular (many distinct small blocks, rho 0.15..0.5)
  collatz     the largest run is rebuilt again and again, and successive peak sizes have a near-constant non-integer ratio
  drift       at the same point of the cycle (end returns, same side and state) the non-wall part of the tape changes
              slowly and steadily while the tape as a whole grows
  overflow    big rearrangements (largest run or run count drops by half) keep happening in the last half of the run
  late        block types not seen in big runs before 30% of the run appear in big runs at the end
  parts       three or more large runs whose size ratios are still changing (not locked like a counter's walls)
  rare        returns to an end almost always happen in one state, with rare exceptions (< 3%)
"""
import gzip, json, math, os, re, sys
from collections import Counter
FP, SRC, OUT = sys.argv[1:4]

def slope(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    if vx == 0: return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx

def spearman(a):
    n = len(a)
    if n < 5: return 0
    r = sorted(range(n), key=lambda i: a[i]); rk = [0] * n
    for j, i in enumerate(r): rk[i] = j
    d = sum((rk[i] - i) ** 2 for i in range(n))
    return 1 - 6 * d / (n * (n * n - 1))

RUN = re.compile(r'([01]+)\^(\d+)|\[(\d+)\]|\(([01]+)\)|([01]+)')
def tape_runs(s):
    """list of (block, count) and gaps (None, n) from a printed tape"""
    out = []
    for m in RUN.finditer(s):
        if m.group(1): out.append((m.group(1), int(m.group(2))))
        elif m.group(3): out.append((None, int(m.group(3))))
        elif m.group(4): out.append((m.group(4), 1))
        else: out.append((m.group(5), 1))
    return out

def analyze(rec):
    m, main = rec['machine'], rec['main']
    K = main['K']
    r = {'machine': m, 'id608': rec['id608'], 'K': K, 'result': main['result'], 'steps': main['steps'],
         'cells': main['cells'], 'runs': main['runs'], 'signs': {}, 'metrics': {}}
    if main['result'] == 'HALT':
        r['signs']['halt'] = 'halted at step %d (sim)' % main['steps']; return r
    if main['result'] == 'LOOP':
        r['signs']['loop'] = 'window loop'; return r
    p = os.path.join(FP, 'logs', m + '.log.gz')
    if not os.path.exists(p): return r
    S, E, F = [], [], None
    for l in gzip.open(p, 'rt'):
        if l[0] == 'S':
            a = l.split(); S.append(tuple(int(x) for x in a[1:]))
        elif l[0] == 'E':
            head, tp = l.split('|', 1)
            a = head.split()
            E.append({'side': a[1], 'steps': int(a[2]), 'cells': int(a[3]) + int(a[4]), 'runs': int(a[5]), 'state': a[6],
                      'tape': tp.strip()})
        elif l[0] == 'F':
            F = l
    M = r['metrics']
    if len(S) < 8: return r
    end = S[-1][0]
    win = [s for s in S if s[0] >= end / 1e3 and s[0] > 1e4]
    if len(win) < 5: win = S[len(S) // 2:]
    cells = [s[1] + s[2] + K for s in win]; runs = [s[3] + s[4] + 1 for s in win]
    lx = [math.log(s[0]) for s in win]
    alpha = slope(lx, [math.log(c) for c in cells]) or 0
    beta = slope([math.log(c) for c in cells], [math.log(x) for x in runs]) if cells[-1] > 1.5 * cells[0] else 0
    beta = beta or 0
    rho = runs[-1] * K / cells[-1]
    mxr = [max(1, s[6]) for s in win]
    gm = slope(lx, [math.log(x) for x in mxr]) or 0
    M.update(alpha=round(alpha, 3), beta=round(beta, 3), rho=round(rho, 3), maxrun=S[-1][6], maxrun_slope=round(gm, 3),
             bigruns=S[-1][5])
    sg = r['signs']
    # shape (not a sign, a description)
    M['shape'] = ('fixed' if cells[-1] <= cells[0] * 1.05 else 'log' if alpha < 0.2 else
                  'sqrt' if alpha < 0.62 else 'linear' if alpha > 0.85 else 'power')
    if rho > 0.5 and beta > 0.6:
        sg['nostruct'] = 'rho=%.2f, runs ~ cells^%.2f' % (rho, beta)
    # overflow / rearrangement events in the whole S series
    ev = []
    for a, b in zip(S, S[1:]):
        if a[6] >= 20 and b[6] < 0.5 * a[6]: ev.append((b[0], 'max', a[6]))
        elif a[3] + a[4] >= 50 and b[3] + b[4] < 0.6 * (a[3] + a[4]): ev.append((b[0], 'runs', a[3] + a[4]))
    late_ev = [e for e in ev if e[0] >= math.sqrt(end * S[0][0] + 1)]
    M['rearrangements'] = len(ev)
    if len(late_ev) >= 2:
        decades = {int(math.log10(e[0])) for e in late_ev}
        sg['overflow'] = '%d big rearrangements, %d in the last half (log scale), in %d decades' % (len(ev), len(late_ev), len(decades))
    # Collatz-like: peak sizes of the largest run before each drop
    peaks = [e[2] for e in ev if e[1] == 'max']
    if len(peaks) >= 4:
        rat = [b / a for a, b in zip(peaks, peaks[1:]) if a > 0]
        rat = rat[-6:]
        mr = sum(rat) / len(rat)
        cv = (sum((x - mr) ** 2 for x in rat) / len(rat)) ** 0.5 / mr if mr else 9
        M['peak_ratio'] = round(mr, 3); M['peak_cv'] = round(cv, 3)
        if mr > 1.05 and abs(mr - round(mr)) > 0.15 and cv < 0.35:
            sg['collatz'] = 'largest run rebuilt %d times, peaks grow by about x%.2f each time (cv %.2f)' % (len(peaks), mr, cv)
    # end returns
    if E:
        tend = E[-1]['steps']
        for side in 'LR':
            es = [e for e in E if e['side'] == side]
            if len(es) < 30: continue
            st = Counter(e['state'] for e in es[len(es) // 2:])
            top, n = st.most_common(1)[0]; tot = sum(st.values())
            if 0 < tot - n <= 0.03 * tot:
                sg['rare'] = 'returns to the %s end: state %s in %d of %d, others %s' % (side, top, n, tot, dict(st))
            # drift: non-wall cells at the same cycle point
            same = [e for e in es if e['state'] == top]
            same = same[len(same) // 2:]
            if len(same) >= 10:
                small = []
                for e in same:
                    tr = tape_runs(e['tape'])
                    small.append(sum(c for b, c in tr if b is None or c < 3) if any(b is None for b, c in tr) else
                                 sum(1 for b, c in tr if c < 3))
                c0, c1 = same[0]['cells'], same[-1]['cells']
                if small[0] > 0 and min(small) > 0:
                    ch = (small[-1] - small[0]) / small[0]
                    rs = spearman(small)
                    M['drift_%s' % side] = {'state': top, 'small_first': small[0], 'small_last': small[-1], 'spearman': round(rs, 2),
                                            'cells_ratio': round(c1 / max(1, c0), 2)}
                    if abs(rs) > 0.8 and 0.02 < abs(ch) < 0.5 and c1 > 2 * c0:
                        sg['drift'] = ('at %s-end returns in state %s, the non-wall part goes %d -> %d (rank corr %.2f) while the tape grows x%.1f'
                                       % (side, top, small[0], small[-1], rs, c1 / c0))
        # late block types
        cut = 0.3 * tend
        early = set();
        for e in E:
            if e['steps'] <= cut:
                for b, c in tape_runs(e['tape']):
                    if b and c >= 3: early.add(b)
        if F and early:
            fin = {b for b, c in tape_runs(F.split(None, 3)[3]) if b and c >= 3}
            new = fin - early
            M['late_new_types'] = len(new); M['big_types_end'] = len(fin)
            if len(new) >= 2 and len(new) >= 0.25 * len(fin):
                sg['late'] = '%d of %d block types in big runs at the end were not in big runs before 30%% of the run' % (len(new), len(fin))
    # parts: large runs whose size ratios still change
    if F:
        fr = [c for b, c in tape_runs(F.split(None, 3)[3]) if b]
        mx = max(fr) if fr else 0
        big = sorted([c for c in fr if c >= 10 and c >= 0.05 * mx], reverse=True)
        M['large_runs_end'] = len(big)
        if len(big) >= 3 and E:
            # compare the largest runs at two returns to the same end in the same state, a decade apart in steps
            last = E[-1]
            same = [e for e in E if e['side'] == last['side'] and e['state'] == last['state'] and e['steps'] <= last['steps'] / 10]
            def top3(e):
                fr2 = [c for b, c in tape_runs(e['tape']) if b]
                mx2 = max(fr2) if fr2 else 0
                return sorted([c for c in fr2 if c >= 10 and c >= 0.05 * mx2], reverse=True)[:3]
            b1 = top3(last)
            if same and len(b1) >= 3:
                b2 = top3(same[-1])
                if len(b2) >= 3:
                    r1 = [b1[i] / b1[i + 1] for i in range(2)]; r2 = [b2[i] / b2[i + 1] for i in range(2)]
                    chg = max(abs(math.log(a / b)) for a, b in zip(r1, r2))
                    M['part_ratio_change'] = round(chg, 3)
                    if chg > 0.5:
                        sg['parts'] = ('largest runs at %s-end returns in state %s, a decade apart: size ratios (%.2f, %.2f) -> (%.2f, %.2f)'
                                       % (last['side'], last['state'], r2[0], r2[1], r1[0], r1[1]))
        # lottery: irregular material between walls
        if fr and mx >= 20:
            smalltypes = len({b for b, c in tape_runs(F.split(None, 3)[3]) if b and c < 3})
            M['small_types_end'] = smalltypes
            if 0.15 <= rho <= 0.5 and smalltypes >= 12 and beta > 0.3:
                sg['lottery'] = 'walls (max run %d) with irregular material between them: %d distinct small blocks, rho %.2f' % (mx, smalltypes, rho)
    return r

out = []
for l in open(os.path.join(FP, 'fastpass.jsonl')):
    rec = json.loads(l)
    try: out.append(analyze(rec))
    except Exception as ex: out.append({'machine': rec['machine'], 'id608': rec['id608'], 'error': repr(ex), 'signs': {}, 'metrics': {}})
json.dump(out, open(OUT, 'w'), indent=1)
c = Counter(s for r in out for s in r['signs'])
print(len(out), 'machines;', dict(c))
