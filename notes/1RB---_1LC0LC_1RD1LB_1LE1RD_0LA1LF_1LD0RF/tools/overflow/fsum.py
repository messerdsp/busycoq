"""fsum.py DUMP: summary of the tape right of the active part: first band (words) and the following big runs."""
import sys
from skel import skel
hdr,out=skel(sys.argv[1])
i=next(k for k,x in enumerate(out) if x.startswith('B') and int(x[1:])>=8)
nums=[x for x in out[i+1:i+60] if not x.startswith('[')]
print('active:',' '.join(out[:i])[:200]); print('first band:',out[i],'| then:',' '.join(nums[:30]))
marker=next(int(x) for x in nums if not x.startswith('B') and int(x)>=30)
print('MARKER',marker)
