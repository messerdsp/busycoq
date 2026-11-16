import pickle
by=pickle.load(open('by3.pkl','rb')); sw=pickle.load(open('sweep.pkl','rb'))
def L(s): return '['+';'.join(s)+']'
hdr='From BusyCoq Require Import Individual62.\nRequire Import Lia String.\nOpen Scope list.\nDefinition tm := Eval compute in (TM_from_str "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF").\nNotation "c -->* c\'" := (c -[ tm ]->* c\') (at level 40).\n'
out=[hdr]; seen={}
for u in sorted(by):
    bi=0
    for lem,kind in by[u].items():
        if lem is None: print('none',u); continue
        body=lem.split('\n',1)[1]
        if body in seen: out.append('(* unit %d %s: same as %s *)'%(u,kind,seen[body])); continue
        name='u%d_%s%s'%(u,kind,'' if kind=='carry' else bi); bi+= kind=='bounce'
        seen[body]=name; out.append('(* unit %d: %s *)\n'%(u,kind)+lem.replace('Lemma X','Lemma '+name,1))
for (u,Z),ok in sw.items():
    _,k,after=ok
    body=(Z,after)
    if body in seen: out.append('(* sweep %d: same as %s *)'%(u,seen[body])); continue
    name='u%d_sweep'%u; seen[body]=name
    # cells: 011111 Z 01111 [B on last] ; right starts 111010 (known wall word). After: 011111 01111 C> after
    out.append('(* the sweep back over unit %d after its carry, arriving at its wall *)\nLemma %s l r:\n  l <* [1;1;1;1;1;0] <* %s <{{B}} [1;1;1;0;1;0] *> r -->*\n  l <* [1;1;1;1;1;0] <* [1;1;1;1;0] {{C}}> %s *> r.\nProof. es. Qed.\n'%(u,name,L((Z+'01111')[::-1]),L(after)))
open('Units.v','w').write('\n'.join(out)+'\n')
