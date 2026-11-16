import sys
# scalefrozen.py IN OUT KB KW : multiply the first band (period-4 stretch of single blocks) by KB and the
# walls of the chain right after it (runs >= 3 until the next band) by KW
t=open(sys.argv[1]).read().split(); KB=int(sys.argv[3]); KW=int(sys.argv[4])
head=t[:2]; toks=t[2:]
# band: find the first stretch of >= 400 consecutive count-1 tokens with period 4
i=0
while True:
    j=i
    while j<len(toks) and '^' not in toks[j]: j+=1
    if j-i>=400: break
    i=j+1
s,e=i,j
band=toks[s:e]
# find the periodic core: skip a few tokens until period 4 holds
k=s
while not (toks[k:k+4]==toks[k+4:k+8]==toks[k+8:k+12]): k+=1
core=toks[k:k+4]; m=k
while toks[m:m+4]==core: m+=4
reps=(m-k)//4
newband=toks[s:k]+core*(reps*KB)+toks[m:e]
# chain after band: scale runs >= 3 until the next long stretch of singles
rest=toks[e:]; out=[]; singles=0; done=False
for x in rest:
    if done: out.append(x); continue
    if '^' in x:
        b,n=x.split('^'); n=int(n)
        if n>=3: x='%s^%d'%(b,n*KW)
        singles=0
    else:
        singles+=1
        if singles>=400: done=True
    out.append(x)
open(sys.argv[2],'w').write(' '.join(head+toks[:s]+newband+out)+'\n')
print('band reps', reps, '->', reps*KB)
