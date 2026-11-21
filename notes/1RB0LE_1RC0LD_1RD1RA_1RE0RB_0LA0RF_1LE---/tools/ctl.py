"""Closed tape language (CTL) check with explicit DFAs, same semantics as busycoq's CTL / MITMDFA certificate.

A configuration is (left half, state, right half, facing direction).  The head sits between cells and reads the
nearest cell of the side it faces.  Each half is read by its own DFA from the far end (infinitely many 0s, so the
start state must loop on 0) towards the head.  An abstract configuration is (qL, s, qR, d).  To read the cell next to
the head, every predecessor pair (q', a) with delta(q', a) = q is tried.

The DFAs are built from regular expressions over {0,1}:
  * LEFT  regex: the left half-tape written left to right (far end first, the cell next to the head last);
  * RIGHT regex: the right half-tape written left to right (the cell next to the head first, far end last);
    it is reversed internally.
Both must describe languages closed under adding 0s at the far end (write 0* at the far end).
A half-tape that leaves the language reaches the dead state; the checker reports it (that half-tape word is a
witness that the regex is too narrow, not that the machine halts).

Usage as a library: check(tm, left_regex, right_regex) -> dict.  Simulation-free; nothing here is a proof.
"""
import sys
from collections import deque

# ---------------- regex -> NFA -> DFA ----------------
class P:
    def __init__(s, txt): s.t = ''.join(txt.split()); s.i = 0
    def peek(s): return s.t[s.i] if s.i < len(s.t) else None
    def eat(s, c=None):
        ch = s.peek()
        if c is not None and ch != c: raise SyntaxError(f'expected {c} at {s.i} in {s.t[:s.i]}^{s.t[s.i:]}')
        s.i += 1; return ch
    def alt(s):
        n = s.cat()
        while s.peek() == '|': s.eat(); n = ('|', n, s.cat())
        return n
    def cat(s):
        items = []
        while s.peek() not in (None, '|', ')'): items.append(s.post())
        n = ('e',)
        for it in items: n = it if n == ('e',) else ('.', n, it)
        return n
    def post(s):
        n = s.atom()
        while s.peek() in ('*', '+', '?', '{'):
            c = s.eat()
            if c == '*': n = ('*', n)
            elif c == '+': n = ('.', n, ('*', n))
            elif c == '?': n = ('|', n, ('e',))
            else:
                j = s.t.index('}', s.i); spec = s.t[s.i:j]; s.i = j + 1
                if ',' in spec:
                    a, b = spec.split(','); a = int(a or 0)
                else: a = b = int(spec)
                m = ('e',)
                for _ in range(a): m = ('.', m, n)
                if b == '': m = ('.', m, ('*', n))
                else:
                    for _ in range(int(b) - a): m = ('.', m, ('|', n, ('e',)))
                n = m
        return n
    def atom(s):
        c = s.eat()
        if c == '(':
            n = s.alt(); s.eat(')'); return n
        if c in '01': return ('c', int(c))
        if c == '.': return ('|', ('c', 0), ('c', 1))
        if c == '~': return ('e',)
        raise SyntaxError(f'bad char {c!r} at {s.i-1}: {s.t[:s.i]}^')

def rev(n):
    k = n[0]
    if k in ('c', 'e'): return n
    if k == '.': return ('.', rev(n[2]), rev(n[1]))
    if k == '|': return ('|', rev(n[1]), rev(n[2]))
    if k == '*': return ('*', rev(n[1]))

def to_nfa(n):
    trans = []  # list of dict sym->set, eps list
    def new():
        trans.append(({0: set(), 1: set()}, set())); return len(trans) - 1
    def build(n):
        k = n[0]
        if k == 'e':
            a = new(); return a, a
        if k == 'c':
            a, b = new(), new(); trans[a][0][n[1]].add(b); return a, b
        if k == '.':
            a1, b1 = build(n[1]); a2, b2 = build(n[2]); trans[b1][1].add(a2); return a1, b2
        if k == '|':
            a, b = new(), new(); a1, b1 = build(n[1]); a2, b2 = build(n[2])
            trans[a][1].update([a1, a2]); trans[b1][1].add(b); trans[b2][1].add(b); return a, b
        if k == '*':
            a, b = new(), new(); a1, b1 = build(n[1])
            trans[a][1].update([a1, b]); trans[b1][1].update([a1, b]); return a, b
    s, f = build(n)
    return trans, s, f

def to_dfa(regex, reverse=False):
    """Minimal complete DFA; returns (delta list of [q0,q1], start, accepting set, dead state or None)."""
    ast = P(regex).alt()
    if reverse: ast = rev(ast)
    trans, s0, fin = to_nfa(ast)
    def clos(S):
        st = list(S); S = set(S)
        while st:
            x = st.pop()
            for y in trans[x][1]:
                if y not in S: S.add(y); st.append(y)
        return frozenset(S)
    start = clos({s0}); ids = {start: 0}; Q = [start]; delta = []
    i = 0
    while i < len(Q):
        S = Q[i]; row = []
        for a in (0, 1):
            T = clos({y for x in S for y in trans[x][0][a]})
            if T not in ids: ids[T] = len(Q); Q.append(T)
            row.append(ids[T])
        delta.append(row); i += 1
    acc = {ids[S] for S in Q if fin in S}
    # minimize (Moore)
    part = [1 if q in acc else 0 for q in range(len(Q))]
    while True:
        sig = {}
        newp = []
        for q in range(len(Q)):
            k = (part[q], part[delta[q][0]], part[delta[q][1]])
            if k not in sig: sig[k] = len(sig)
            newp.append(sig[k])
        if len(set(newp)) == len(set(part)): part = newp; break
        part = newp
    # renumber so that start is 0, BFS order
    order = {part[0]: 0}; qq = [part[0]]; rep = {}
    for q in range(len(Q)): rep.setdefault(part[q], q)
    j = 0
    while j < len(qq):
        p = qq[j]; j += 1
        for a in (0, 1):
            t = part[delta[rep[p]][a]]
            if t not in order: order[t] = len(qq); qq.append(t)
    md = [[order[part[delta[rep[p]][a]]] for a in (0, 1)] for p in qq]
    macc = {order[part[q]] for q in acc}
    dead = None
    for q in range(len(md)):
        if q not in macc and md[q] == [q, q]:
            # dead only if no accepting state reachable
            seen = {q}; st = [q]; ok = False
            while st:
                x = st.pop()
                if x in macc: ok = True; break
                for y in md[x]:
                    if y not in seen: seen.add(y); st.append(y)
            if not ok: dead = q
    return md, 0, macc, dead

def track(dfa, K=1, mod=6, cap=3):
    """Product of a language DFA with a run tracker: the last K runs read (symbol, length capped at cap, length mod
    mod).  The far 0s are not a run (the start state still loops on 0).  The dead state stays absorbing."""
    delta, s0, acc, dead = dfa
    def upd(tr, a):
        if tr == 'far':
            return 'far' if a == 0 else ((1, 1, 1),)
        runs = list(tr)
        sym, c, m = runs[-1]
        if sym == a: runs[-1] = (a, min(c + 1, cap), (m + 1) % mod)
        else: runs.append((a, 1, 1 % mod))
        return tuple(runs[-K:])
    start = (s0, 'far'); ids = {start: 0}; Q = [start]; nd = []; i = 0
    DEAD = None
    while i < len(Q):
        q, tr = Q[i]; row = []
        for a in (0, 1):
            nq = delta[q][a]
            n = (nq, 'dead') if nq == dead else (nq, upd(tr, a))
            if n not in ids: ids[n] = len(Q); Q.append(n)
            row.append(ids[n])
        nd.append(row); i += 1
    if dead is not None:
        for k, v in ids.items():
            if k[1] == 'dead': DEAD = v
    nacc = {ids[k] for k in ids if k[0] in acc}
    return nd, 0, nacc, DEAD

def track2(dfa, win=6, mod=6, cap=3):
    """Product of a language DFA with: the last `win` cells exactly, the length of the current run of 1s (capped,
    mod `mod`) and the length of the current alternating run ...1010 / ...0101 (mod `mod`).  Start loops on 0."""
    delta, s0, acc, dead = dfa
    def upd(tr, a):
        if tr == 'far':
            if a == 0: return 'far'
            return ((1,), (1, 1), 1)
        w, (c1, m1), alt = tr
        w2 = (w + (a,))[-win:]
        if a == 1: c1n, m1n = min(c1 + 1, cap), (m1 + 1) % mod
        else: c1n, m1n = 0, 0
        alt2 = (alt + 1) % (2 * mod) if (len(w) and w[-1] != a) else 1
        return (w2, (c1n, m1n), alt2)
    start = (s0, 'far'); ids = {start: 0}; Q = [start]; nd = []; i = 0; DEAD = None
    while i < len(Q):
        q, tr = Q[i]; row = []
        for a in (0, 1):
            nq = delta[q][a]
            n = (nq, 'dead') if nq == dead else (nq, upd(tr, a))
            if n not in ids: ids[n] = len(Q); Q.append(n)
            row.append(ids[n])
        nd.append(row); i += 1
    for k, v in ids.items():
        if k[1] == 'dead': DEAD = v
    nacc = {ids[k] for k in ids if k[0] in acc}
    return nd, 0, nacc, DEAD

def sample_word(delta, target, maxlen=60):
    """A shortest word from 0 to target (as read from the far end)."""
    prev = {0: None}; dq = deque([0])
    while dq:
        q = dq.popleft()
        if q == target: break
        for a in (0, 1):
            t = delta[q][a]
            if t not in prev: prev[t] = (q, a); dq.append(t)
    if target not in prev: return None
    w = []; q = target
    while prev[q] is not None: q, a = prev[q]; w.append(a)
    return ''.join(map(str, reversed(w)))

def parse_tm(s):
    t = {}
    for i, r in enumerate(s.split('_')):
        for b in range(2):
            c = r[3 * b:3 * b + 3]
            t[(chr(65 + i), b)] = None if c[2] not in 'ABCDEF' else (int(c[0]), c[1], c[2])
    return t

def check(tm_str, left_re, right_re, start='A', maxconf=2_000_000, verbose=True, K=1, mod=6, cap=3, init=None, win=6):
    """init: optional (left cells far->head, state, right cells head->far) to start from instead of blank."""
    tm = parse_tm(tm_str)
    dL = to_dfa(left_re); dR = to_dfa(right_re, reverse=True)
    if K == 'w':
        dL = track2(dL, win, mod, cap); dR = track2(dR, win, mod, cap)
    elif K:
        dL = track(dL, K, mod, cap); dR = track(dR, K, mod, cap)
    res = {'nL': len(dL[0]), 'nR': len(dR[0])}
    for nm, d in (('left', dL), ('right', dR)):
        if d[0][0][0] != 0:
            res['error'] = f'{nm} start state does not loop on 0'; return res
    preds = []
    for d in (dL, dR):
        pr = [[] for _ in d[0]]
        for q, row in enumerate(d[0]):
            for a in (0, 1): pr[row[a]].append((q, a))
        preds.append(pr)
    D = {'L': dL, 'R': dR}; PR = {'L': preds[0], 'R': preds[1]}
    if init is None:
        init = (0, start, 0, 'R')
    else:
        lw, st0, rw = init
        q = 0
        for a in lw: q = dL[0][q][a]
        r = 0
        for a in reversed(rw): r = dR[0][r][a]
        init = (q, st0, r, 'R')
        if q == dL[3] or r == dR[3]:
            res.update(status='INIT_DEAD', conf=init); return res
    par = {init: None}; dq = deque([init])
    while dq:
        c = dq.popleft()
        qL, s, qR, d = c
        side_q = qR if d == 'R' else qL
        for (qp, a) in PR[d][side_q]:
            tr = tm[(s, a)]
            if tr is None:
                res.update(status='HALT', conf=c, read=a, path=trace(par, c)); res['words'] = words(dL, dR, c); return res
            w, mv, ns = tr
            if d == 'R':
                if mv == 'R': n = (dL[0][qL][w], ns, qp, 'R')
                else: n = (qL, ns, dR[0][qp][w], 'L')
            else:
                if mv == 'L': n = (qp, ns, dR[0][qR][w], 'L')
                else: n = (dL[0][qp][w], ns, qR, 'R')
            if n not in par:
                if n[0] == dL[3] or n[2] == dR[3]:
                    res.update(status='DEAD', conf=n, frm=c, read=a, path=trace(par, c) + [n])
                    res['words'] = words(dL, dR, c); res['words_new'] = words(dL, dR, n)
                    return res
                par[n] = c; dq.append(n)
                if len(par) > maxconf:
                    res.update(status='LIMIT'); return res
    res.update(status='CLOSED', nconf=len(par), dL=dL, dR=dR, confs=list(par))
    return res

def trace(par, c, k=12):
    out = []
    while c is not None and len(out) < k: out.append(c); c = par[c]
    return list(reversed(out))

def words(dL, dR, c):
    qL, s, qR, d = c
    wl = sample_word(dL[0], qL) if qL != dL[3] else 'DEAD'
    wr = sample_word(dR[0], qR) if qR != dR[3] else 'DEAD'
    if wr not in (None, 'DEAD'): wr = wr[::-1]
    return f'{wl} {"<" if d=="L" else ""}{s}{">" if d=="R" else ""} {wr}'

def report(res):
    print({k: v for k, v in res.items() if k in ('nL', 'nR', 'status', 'nconf', 'error')})
    if res.get('status') in ('HALT', 'DEAD'):
        print('  at', res['conf'], 'read', res.get('read'))
        print('  sample:', res['words'])
        if 'words_new' in res: print('  new   :', res['words_new'])

def mitm_cert(res):
    """busycoq MITMDFA arrays (ldfa, rdfa) for a CLOSED result: ldfa[q*2+a] = delta(q, a)."""
    out = []
    for d in (res['dL'], res['dR']):
        out.append([d[0][q][a] for q in range(len(d[0])) for a in (0, 1)])
    return out

def rle(cells):
    out = []; i = 0
    while i < len(cells):
        j = i
        while j < len(cells) and cells[j] == cells[i]: j += 1
        n = j - i; out.append(f'{cells[i]}^{n}' if n > 3 else str(cells[i]) * n); i = j
    return ' '.join(out)

def concrete(tm_str, left_re, right_re, init, steps, K=1, mod=6, cap=3, every=1):
    """Simulate from init (left cells, state, right cells) and check each configuration against the two DFAs.
    Returns the first configuration with a dead half (as text), or None.  Simulated."""
    tm = parse_tm(tm_str)
    dL = to_dfa(left_re); dR = to_dfa(right_re, reverse=True)
    if K: dL = track(dL, K, mod, cap); dR = track(dR, K, mod, cap)
    L, s, R = list(init[0]), init[1], list(init[2])
    seen = set()
    for t in range(steps):
        if not R: R.append(0)
        if t % every == 0:
            q = 0
            for a in L: q = dL[0][q][a]
            r = 0
            for a in reversed(R): r = dR[0][r][a]
            if q == dL[3] or r == dR[3]:
                ll = L[:]
                while ll and ll[0] == 0: ll.pop(0)
                rr = R[:]
                while rr and rr[-1] == 0: rr.pop()
                return f't={t} {"LEFT" if q==dL[3] else ""}{"RIGHT" if r==dR[3] else ""} dead: {rle(ll)} [{s}>] {rle(rr)}'
            seen.add((q, s, r))
        tr = tm[(s, R[0])]
        if tr is None: return f'HALT at {t}'
        w, mv, ns = tr; R[0] = w
        if mv == 'R': L.append(R.pop(0))
        else: R.insert(0, L.pop() if L else 0)
        s = ns
    return None
