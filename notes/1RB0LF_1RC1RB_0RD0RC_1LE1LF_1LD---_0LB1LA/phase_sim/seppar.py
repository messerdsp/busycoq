"""For one wave: which old separators did the wave fill (merge) and which did it keep, against the parity of the
separator's cell position and of the runs around it."""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowsim import toks
from align import align
from lowsim import load_state
st = load_state(os.environ.get('OLDSTATE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'state10000.txt.gz'))); OLD = toks(st['r'])[:2300]
line = open(sys.argv[1]).readlines()[int(sys.argv[2])].split(); NEW = line[1:]
front = next(i for i in range(2, len(NEW)) if NEW[i][0] == 'z' and NEW[i] != 'z3')
X = [int(t[1:]) for t in OLD[7::2]]; Y = [int(t[1:]) for t in NEW[3:front:2]]
o, err = align(X, Y)
# absolute cell position of each old separator after X[k] (offset from start of tape)
pos = 0; cellpos = []
for t in OLD:
    pos += int(t[1:]); cellpos.append(pos)
# OLD index of X[k] is 7+2k; separator after it is 8+2k, starting at cellpos[7+2k]
k = 0; stats = {}
rows = []
for grp, d, y in o:
    for m in range(len(grp)):
        idx = 7 + 2 * (k + m); filled = m < len(grp) - 1
        key = (cellpos[idx] % 2, X[k + m] % 2)
        stats.setdefault(key, [0, 0])[filled] += 1
        rows.append((filled, cellpos[idx] % 4, X[k + m] % 4, d if m == len(grp) - 1 else None))
    k += len(grp)
print('aligned groups', len(o), err)
print('(sep cell parity, run parity): [kept, filled]')
for kk in sorted(stats): print(kk, stats[kk])
print(''.join('F' if r[0] else 'k' for r in rows))
print(''.join(str(r[1]) for r in rows))
