import sys
# usage: mkinit.py IN OUT expr   ; expr maps (index i among big runs, count n) -> new count, e.g. "n % 1000 + 1000"
toks=open(sys.argv[1]).read().split()
expr=sys.argv[3]; out=toks[:2]; i=0
for t in toks[2:]:
    b,_,n=t.partition('^'); n=int(n) if n else 1
    if n>=100: n=eval(expr, {'n':n,'i':i}); i+=1
    out.append(b+('^%d'%n if n>1 else ''))
open(sys.argv[2],'w').write(' '.join(out)+'\n')
