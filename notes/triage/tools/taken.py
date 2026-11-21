#!/usr/bin/env python3
"""Is a machine already in a busycoq PR or in an equivalence file? (canonical form: mirror + state renaming)
usage: taken.py CCZ_CLONE MACHINE [MACHINE ...]
CCZ_CLONE is a clone of https://github.com/ccz181078/busycoq with the PR heads fetched:
    git fetch origin '+refs/pull/*/head:refs/remotes/pr/*' '+BB6:refs/remotes/origin/BB6'
For each machine it prints every PR whose diff or commit message names it (or a renaming or mirror of it), and every
verify/Eqv*.v on BB6 that names it. An Eqv entry means the machine is tied to another one: proving either settles both.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon

TOK = r'(?:[01][LR][A-FH]|---|HHH|[01][LR]Z)'
PAT = re.compile(TOK * 2 + '(?:_' + TOK * 2 + '){5}')

def git(d, *a):
    return subprocess.run(['git', '-C', d] + list(a), capture_output=True, text=True, errors='ignore').stdout

def canon_of(m):
    try: return canon.canon(m.replace('HHH', '---'))
    except Exception: return None

def main():
    d, want = sys.argv[1], sys.argv[2:]
    targets = {canon_of(m): m for m in want}
    hits = {m: [] for m in want}
    refs = git(d, 'for-each-ref', '--format=%(refname:short)', 'refs/remotes/pr').split()
    for r in refs:
        b = git(d, 'merge-base', r, 'origin/BB6').strip()
        txt = git(d, 'diff', b, r) + git(d, 'log', '--format=%B', b + '..' + r)
        found = {canon_of(x) for x in set(PAT.findall(txt))}
        for c in found & set(targets):
            hits[targets[c]].append(r + ' "' + git(d, 'log', '-1', '--format=%s', r).strip()[:90] + '"')
    for f in git(d, 'ls-tree', '--name-only', 'origin/BB6', 'verify/').split():
        if 'Eqv' in f:
            found = {canon_of(x) for x in set(PAT.findall(git(d, 'show', 'origin/BB6:' + f)))}
            for c in found & set(targets):
                hits[targets[c]].append(f + ' (equivalence: proving either machine settles both)')
    for m in want:
        print(m, 'FREE' if not hits[m] else '')
        for h in hits[m]: print('   ', h)

if __name__ == '__main__':
    main()
