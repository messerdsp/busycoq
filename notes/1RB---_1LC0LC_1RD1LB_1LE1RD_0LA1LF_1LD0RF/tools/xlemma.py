import sys
M='1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF'
T={}
for s in range(6):
    for y in range(2):
        t=M[s*7+y*3:s*7+y*3+3]
        if t[0]!='-': T[('ABCDEF'[s],y)]=(int(t[0]),1 if t[1]=='R' else -1,t[2])
def expand(toks, cap=None):
    out=''
    for t in toks:
        b,_,n=t.partition('^'); n=int(n) if n else 1
        if cap: n=min(n,cap)
        out+=b*n
    return out
def parse(line):
    t=line.split(); st=t[2]; i=t.index('L:'); j=t.index('back'); k=t.index('R:')
    return int(t[0]), st, t[i+1:j], t[j+1], t[k+1:]
def L(s): return '['+';'.join(s)+']'
def make(line, wallcopies=3):
    step, st, Lr, back, Rr = parse(line)
    left=expand(Lr[-1:], cap=wallcopies)   # last L run (the big wall), a few copies
    left=expand(Lr[-1:], cap=wallcopies)+back
    right=expand(Rr)
    tape=[int(c) for c in left+right]+[0]*50
    pos=len(left); s=st; start=pos; lo=pos; hi=pos
    for n in range(10**7):
        y=tape[pos]
        if (s,y) not in T: return None, 'halt'
        w,d,ns=T[(s,y)]; tape[pos]=w; pos+=d; s=ns; lo=min(lo,pos); hi=max(hi,pos)
        if pos < 6: break                    # into the big wall, moving left
        if pos >= len(left)+len(right)-2: return None, 'ran off the right'
    fin=''.join(map(str,tape))
    keep=min(len(right), hi-start+14)              # cells right of the start the head can touch, plus a margin
    right=right[:keep]
    # lemma: l <* rev(left) {{st}}> right *> r -->* l <{{s}} fin[0..] ... head at pos (inside left region)
    lhs='l <* %s {{%s}}> %s *> r' % (L(left[::-1]), st, L(right))
    rhs='l <* %s {{%s}}> %s *> r' % (L(fin[:pos][::-1]), s, L(fin[pos:len(left)+len(right)]))
    return 'Lemma end_step_%d l r:\n  %s -->*\n  %s.\nProof. es. Qed.\n' % (step % 100000, lhs, rhs), 'ok steps=%d hi=%d'%(n, hi-start)
if __name__=='__main__':
    lines=[l for l in open(sys.argv[1]) if ' X ' in l]
    print('From BusyCoq Require Import Individual62.\nRequire Import Lia String.\nOpen Scope list.\nDefinition tm := Eval compute in (TM_from_str "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF").\nNotation "c -->* c\'" := (c -[ tm ]->* c\') (at level 40).\n')
    for ln in lines[int(sys.argv[2]):int(sys.argv[3])]:
        lem, info = make(ln)
        print('(* %s *)' % info)
        if lem: print(lem)
