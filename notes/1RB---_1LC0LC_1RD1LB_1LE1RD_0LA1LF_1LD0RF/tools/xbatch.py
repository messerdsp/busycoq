# xbatch.py XFILE OUTDIR NPERFILE : unique end-entry configurations -> Rocq lemma files (proved by es)
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlemma import make, parse
lines=[l for l in open(sys.argv[1]) if ' X ' in l]
seen={}; res=[]
for ln in lines:
    step, st, Lr, back, Rr = parse(ln)
    key=(st, Lr[-1].split('^')[0], back, ' '.join(Rr))
    if key in seen: continue
    seen[key]=step
    lem, info = make(ln)
    res.append((step, lem, info))
os.makedirs(sys.argv[2], exist_ok=True)
hdr='From BusyCoq Require Import Individual62.\nRequire Import Lia String.\nOpen Scope list.\nDefinition tm := Eval compute in (TM_from_str "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF").\nNotation "c -->* c\'" := (c -[ tm ]->* c\') (at level 40).\n\n'
N=int(sys.argv[3]); bad=[r for r in res if r[1] is None]
good=[r for r in res if r[1] is not None]
for i in range(0, len(good), N):
    with open(os.path.join(sys.argv[2], 'E%03d.v' % (i//N)), 'w') as f:
        f.write(hdr)
        for step, lem, info in good[i:i+N]: f.write('(* step %d: %s *)\n%s\n' % (step, info, lem))
print('entries', len(lines), 'unique', len(res), 'lemmas', len(good), 'not closed', len(bad), [b[2] for b in bad][:5])
