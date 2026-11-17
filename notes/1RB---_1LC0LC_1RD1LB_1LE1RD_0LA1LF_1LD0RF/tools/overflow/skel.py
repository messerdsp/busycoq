import sys
B=['010101','110101','011101','010111']
def skel(fn, maxitems=200, minrun=3):
    toks=open(fn).read().split(); hdr=toks[:2]; t=toks[2:]
    out=[]; sh=0; i=0; n=len(t)
    while i<n:
        j=i; w=0
        while t[j:j+4]==B: j+=4; w+=1
        if w>=3:
            if sh: out.append('[%d]'%sh); sh=0
            out.append('B%d'%w); i=j; continue
        b,_,e=t[i].partition('^'); e=int(e) if e else 1
        if e>=minrun:
            if sh: out.append('[%d]'%sh); sh=0
            out.append(str(e))
        else: sh+=e
        i+=1
    if sh: out.append('[%d]'%sh)
    return hdr, out
if __name__=='__main__':
    hdr,out=skel(sys.argv[1]); k=int(sys.argv[2]) if len(sys.argv)>2 else 120
    print(' '.join(hdr), len(out),'items'); print(' '.join(out[:k]))
