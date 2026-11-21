import re,collections
exec(open('hyp.py').read().split("statsL=collections.Counter()")[0])
def norm(s):
    # leading partial (10)^i or (01)^i, then blocks
    out=[];i=0
    while i<len(s):
        m=re.match(r'00((?:10)*)',s[i:])
        if m and m.end()>2:
            n=len(m.group(1))//2; out.append(f'B{n}' if n<3 else f'B[{n%3}]'); i+=m.end(); continue
        m=re.match(r'((?:10){2,})',s[i:])
        if m:
            n=len(m.group(1))//2; out.append(f'(10)[{n%3}]'); i+=m.end(); continue
        out.append(s[i]); i+=1
    return ' '.join(out)
forms=collections.Counter(); ex={}
def run(L,s,R,steps,name):
    L=list(L);R=list(R)
    for t in range(steps):
        if not R: R.append(0)
        rs=''.join(map(str,R)).rstrip('0')
        nr=near_right(rs) if rs else ''
        if nr is None: nr='!!'+rs[:30]
        k=(s,norm(nr)); forms[k]+=1; ex.setdefault(k,(name,t))
        tr=tm[(s,R[0])]
        if tr is None: print('HALT',name,t); return
        w,mv,ns=tr; R[0]=w
        if mv=='R': L.append(R.pop(0))
        else: R.insert(0,L.pop() if L else 0)
        s=ns
exec(open('hyp.py').read().split("T=lambda k")[0].split("def run(")[0].split("statsL=")[0][-1:])  # no-op
src=open('hyp.py').read()
exec(src[src.index('def P(r,ds'):src.index("print('left near")])
print(len(forms))
for k,v in sorted(forms.items(),key=lambda x:(x[0][0],-x[1])): print(v,k,ex[k])
