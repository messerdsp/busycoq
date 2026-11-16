import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from xlemma import T
D=['01010101010101','0101010101111111','011111110101010101','01111111010101111111']
def trip(U, V, LEFT='1'*12, maxk=400000):
    s=LEFT+U+V+'011101'*6+D[0]+'011101'*6
    tape=[0]*40+[int(c) for c in s]+[0]*80; base=40+len(LEFT); pos=base; st='D'; vb=base+len(U)
    lo=pos; hi=pos; ex=None
    for k in range(maxk):
        y=tape[pos]; w,d,ns=T[(st,y)]; tape[pos]=w; np_=pos+d
        if np_==vb and d==1: return ('carry',k+1,lo-base,hi-base,''.join(map(str,tape[base-12:vb])),ns)
        if pos==base and np_==base-1: ex=(k+1,ns,''.join(map(str,tape[base-12:vb+2])),lo-base,hi-base)
        pos=np_; st=ns; lo=min(lo,pos); hi=max(hi,pos)
        if pos<base-12: return ('bounce',ex[0],ex[3],ex[4],ex[2],ex[1])
    return ('timeout',)
if __name__=='__main__':
  for p in range(4):
    for kk in (3,4):
        U='011101'*kk+D[p]; V='011101'*5+D[0]
        r=trip(U,V); print(p,kk,r)
