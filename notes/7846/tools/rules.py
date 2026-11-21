"""Check bounded tape rules  l <* X {{q}}> Y *> r -->* l <* X' {{q'}}> Y' *> r  (Coq/busycoq notation)
by running the machine on the finite segment X q Y; the run must stay inside the segment
until it reaches the right-hand side.  Usage: rules.py <machine> <MZ> <file of Hypothesis lines> <SA>"""
import re, sys, itertools

def parse_tm(s):
    t = {}
    for i, part in enumerate(s.split('_')):
        for b in range(2):
            x = part[3*b:3*b+3]
            if x[2] in '-ZH':
                t[('ABCDEF'[i], b)] = None
            else:
                t[('ABCDEF'[i], b)] = (int(x[0]), x[1], x[2])
    return t

D = {}
D['bt'] = {'Dm':[1,1,1,1,1,0],'D0':[1,1,1,1,1],'D1':[1,1,0,1,1,1,0],'D2':[1,1,0,1,1,1],'D3':[1,1,0,0,1,1,1,0]}
D['dec'] = {'Dm':[1,1,0,1,1,0,1],'D0':[1,0,1,1,0,1],'D1':[1,1,0,1,1,1,0,1],'D2':[1,0,1,1,1,0,1],'D3':[1,1,0,1,1,1,1,0,1]}
D['Rl'] = {'Dm':[1,1,1,0,1,1,0],'D0':[1,1,0,1,1,0],'D1':[1,1,1,0,1,1,1,0],'D2':[1,1,0,1,1,1,0],'D3':[1,1,1,0,1,1,1,1,0]}
D['Er'] = {'Dm':[0,0,0,1,1,1,0,1,1,1],'D0':[0,0,0,1,1,1,1,1,1],'D1':[0,0,0,0,1,1,1,0,1,1,1],'D2':[0,0,0,0,1,1,1,1,1,1],'D3':[0,0,0,0,0,1,1,1,0,1,1,1]}
D["Erp"] = {'Dm':[1,1,1,0,1,1,1],'D0':[1,1,1,1,1,1],'D1':[0,1,1,1,0,1,1,1],'D2':[0,1,1,1,1,1,1],'D3':[0,0,1,1,1,0,1,1,1]}
CONST = {'EXT':[1,1,0,1,1,0,1,1,1], 'OVT':[0,0,0,0,1,1,1,1,1,1,1,0,1,1,1],
         'MLONE':[1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,1,0,1,1,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,1,1,0,1,1,1,0,1,1,0,1,1,1,0]}

def ev(tok, env):
    tok = tok.strip()
    if tok.startswith('['):
        m = re.match(r'^\[([01;]*)\](\^\^(\w+))?$', tok)
        xs = [int(c) for c in m.group(1).split(';') if c]
        if m.group(3):
            n = int(env[m.group(3)]) if not m.group(3).isdigit() else int(m.group(3))
            xs = xs * n
        return xs
    m = re.match(r"^(bt|dec|Rl|Er'|Er) (\w+)$", tok)
    if m:
        f = m.group(1).replace("'", 'p'); d = m.group(2)
        d = env.get(d, d)
        return D[f][d]
    if tok in CONST: return CONST[tok]
    if tok in env: return env[tok]
    raise ValueError(tok)

def parse_cfg(s, env):
    s = s.strip()
    m = re.match(r'^(.*?)\s*(<\{\{|\{\{)(\w+)(\}\}>|\}\})\s*(.*)$', s)
    left, op, q, op2, right = m.groups()
    q = env.get(q, q)
    lp = [p.strip() for p in left.split('<*')]
    assert lp[0] in ('l', 'W', '0inf', 'Y'), lp[0]
    L = []  # nearest-first
    for p in lp[1:]:
        L = ev(p, env) + L
    rp = [p.strip() for p in right.split('*>')]
    assert rp[-1] == 'r', rp
    R = []
    for p in rp[:-1]:
        R = R + ev(p, env)
    zinf = lp[0] == '0inf'
    seg = L[::-1] + R
    hp = len(L) if op == '{{' else len(L) - 1
    return (q, seg, len(L), hp, zinf)

def run_check(tm, c1, c2, maxsteps=10**6):
    q, seg, nl, pos, zinf = c1
    q2, seg2, nl2, hp2, zinf2 = c2
    # coordinates: segment index; l boundary at index 0 (cells < 0 are l)
    if len(seg) != len(seg2):
        return 'lenmismatch'
    tape = list(seg)
    lo, hi = 0, len(seg) - 1
    zeros = 0
    for step in range(maxsteps + 1):
        if step > 0 and q == q2 and pos == hp2 + zeros and tape[zeros:] == seg2 and (not zinf or all(x == 0 for x in tape[:zeros])):
            return ('ok', step)
        if pos < 0:
            if zinf:
                tape.insert(0, 0); pos = 0; zeros += 1; hi += 1
            else:
                return ('left', step)
        if pos > len(tape) - 1:
            return ('right', step)
        tr = tm[(q, tape[pos])]
        if tr is None: return ('halt', step)
        w, d, nq = tr
        tape[pos] = w
        pos += 1 if d == 'R' else -1
        q = nq
    return ('timeout', maxsteps)

def check_line(tm, line, env):
    line = re.sub(r'^\s*Hypothesis\s+\w+\s*:\s*', '', line)
    m = re.match(r'^forall ([\w ]+),\s*(.*)$', line)
    vars_ = m.group(1).split() if m else []
    body = m.group(2) if m else line
    pre = None
    mm = re.match(r'^(.*?)->\s*(.*-\[tm\]->\*.*)$', body)
    if mm and '-[tm]->*' not in mm.group(1):
        pre = mm.group(1).strip(); body = mm.group(2)
    a, b = body.split('-[tm]->*')
    b = b.strip().rstrip('.')
    results = []
    ds = ['Dm', 'D0', 'D1', 'D2', 'D3'] if 'd' in vars_ else [None]
    for d in ds:
        if pre and d == 'D3': continue
        e = dict(env)
        if d: e['d'] = d
        c1 = parse_cfg(a, e); c2 = parse_cfg(b, e)
        results.append((d, run_check(tm, c1, c2)))
    return results

if __name__ == '__main__':
    tm = parse_tm(sys.argv[1])
    env = {'MZ': sys.argv[2] if len(sys.argv) > 2 else '6', 'SA': sys.argv[4] if len(sys.argv)>4 else 'A'}
    env['EXR'] = [1]*12 + [0,1,1,1]
    txt = open(sys.argv[3] if len(sys.argv) > 3 else 'hyps.txt').read()
    # join continuation lines
    hyps = re.findall(r'Hypothesis (\w+) :(.*?)(?=\nHypothesis|\Z)', txt, re.S)
    for name, h in hyps:
        h = ' '.join(h.split())
        if 'mfacts' in h or 'MREC' in h or 'MY0' in h or 'lstack' in h: continue
        try:
            print(name, check_line(tm, h.rstrip('.'), env))
        except Exception as ex:
            import traceback; print(name, 'ERR', repr(ex), traceback.format_exc().splitlines()[-3])
