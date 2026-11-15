import sys, os, pickle
sys.path.insert(0, '/home/user/m9')
from lowsim import toks
from align import align
from lowsim import load_state
st = load_state(os.environ.get('OLDSTATE', '/home/user/m9/real10k.ckpt')); OLD = toks(st['r'])[:2300]
line = open(sys.argv[1]).readlines()[int(sys.argv[2]) if len(sys.argv) > 2 else -2].split()
ph, NEW = line[0], line[1:]
front = next(i for i in range(2, len(NEW)) if NEW[i][0] == 'z' and NEW[i] != 'z3')   # wave front
assert all(t == 'z3' for t in OLD[2:200:2]), 'separators'
X = [int(t[1:]) for t in OLD[7::2]]          # old runs above bottom and the run right above it
Y = [int(t[1:]) for t in NEW[3:front:2]]     # new runs above the bottom, below the wave
o, err = align(X, Y, D=3, J=60)
print('phase', ph, 'front token', front, 'new runs', len(Y), 'aligned', len(o), err)
for a in o: print(len(a[0]), a[1], a[0] if len(a[0]) < 6 else a[0][:5] + ['...'], a[2])
