#!/bin/bash
# nudge.sh BASE IDX DELTA : add DELTA to the run count of token IDX (0-based after "step state") and report the frozen unit later
python3 - "$1" "$2" "$3" <<'PY'
import sys
t=open(sys.argv[1]).read().split(); i=int(sys.argv[2])+2; d=int(sys.argv[3])
b,n=t[i].split('^'); t[i]='%s^%d'%(b,int(n)+d)
open('nudged_%s.txt'%sys.argv[3],'w').write(' '.join(t)+'\n')
PY
INIT=nudged_$3.txt SKEL=1 ./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 3e10 -16 - 2>/dev/null | python3 -c "
import sys,re
first=last=None
for line in sys.stdin:
    m=re.search(r'\[(\d{4,})\]\s+(\d+)', line)
    if not m: continue
    v=(int(m.group(1)), int(m.group(2)))
    if first is None: first=v
    if v!=last and last is not None and abs(v[1]-last[1])>50:
        t=line.split(); print('  change at W1new', t[2] if not t[2].startswith('[') else t[3], last, '->', v)
    last=v
print('  delta $3: first', first, 'last', last)
"
