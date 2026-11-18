import sys
B=['010101','110101','011101','010111']
ROT=[B[r:]+B[:r] for r in range(4)]
toks=open(sys.argv[1]).read().split(); t=toks[2:]
out=[]; sh=0; i=0
while i<len(t):
    w=0
    for R in ROT:
        j=i; w=0
        while t[j:j+4]==R: j+=4; w+=1
        if w>=3: break
    if w>=3:
        if sh: out.append('[%d]'%sh); sh=0
        out.append('B%d'%w); i=j; continue
    b,_,e=t[i].partition('^'); e=int(e) if e else 1
    if e>=3:
        if sh: out.append('[%d]'%sh); sh=0
        out.append(str(e))
    else: sh+=e
    i+=1
if sh: out.append('[%d]'%sh)
print(toks[0],toks[1],len(out),'items'); print(' '.join(out[:int(sys.argv[2]) if len(sys.argv)>2 else 200]))
