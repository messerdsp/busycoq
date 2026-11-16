import sys, collections
M='1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF'
T={}
for s in range(6):
    for y in range(2):
        t=M[s*7+y*3:s*7+y*3+3]
        if t[0]!='-': T[('ABCDEF'[s],y)]=(int(t[0]),1 if t[1]=='R' else -1,t[2])
def L(s): return '['+';'.join(s)+']'
def run(ctx):
    left='011111'+'00000'; right='0110111'+ctx
    tape=[int(x) for x in '0'*40+left+right]; pos=40+len(left); s='D'; start=pos; hi=pos
    for k in range(200000):
        y=tape[pos]; w,d,ns=T[(s,y)]; tape[pos]=w; pos+=d; s=ns; hi=max(hi,pos)
        if pos==start-6 and s=='C': return ('bounce', tape, start, pos, hi, s)
        if s=='D' and pos>start+10 and tape[pos]==0 and tape[pos-5:pos]==[0]*5 and tape[pos+1:pos+7]==[1,1,0,1,1,1]:
            return ('carry', tape, start, pos, hi, s)
        if pos>=len(tape)-2 or pos<start-12: return ('unknown', tape, start, pos, hi, s)
    return ('timeout',)+(None,)*5
def lemma(name, ctx):
    kind, tape, start, pos, hi, s = run(ctx)
    if kind=='bounce':
        n=hi-start+3; region=('0110111'+ctx)[:n]; fin=''.join(map(str,tape))
        after=fin[start-5:start+n]
        return kind, 'Lemma %s l r:\n  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> %s *> r -->*\n  l <* [1;1;1;1;0] {{C}}> %s *> r.\nProof. es. Qed.\n' % (name, L(region), L(fin[start-6]+after))
    if kind=='carry':
        n=pos+7-start+12; region=('0110111'+ctx)[:n]; fin=''.join(map(str,tape))
        newleft=fin[start-11:pos-5]; rest=fin[pos+7:start+n]
        return kind, 'Lemma %s l r:\n  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> %s *> r -->*\n  l <* %s <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> %s *> r.\nProof. es. Qed.\n' % (name, L(region), L(newleft[::-1]), L(rest))
    return kind, None
if __name__=='__main__':
    rows=[l.split() for l in open(sys.argv[1])]
    groups=collections.defaultdict(set)
    for p,c in rows: groups[int(p)//1000].add(c)
    print('From BusyCoq Require Import Individual62.\nRequire Import Lia String.\nOpen Scope list.\nDefinition tm := Eval compute in (TM_from_str "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF").\nNotation "c -->* c\'" := (c -[ tm ]->* c\') (at level 40).\n')
    for gi,g in enumerate(sorted(groups)[:int(sys.argv[2])]):
        for ci,c in enumerate(sorted(groups[g])):
            kind, lem = lemma('u%d_case%d'%(gi+1,ci), c)
            print('(* unit %d, case %d: %s *)' % (gi+1, ci, kind))
            if lem: print(lem)
