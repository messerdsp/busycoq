From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia.
Require Import ZArith.
Require Import List.
Require Import String.
From BusyCoq Require Import Longitudinal.

Open Scope list.
Import Eqb.

Ltac stepn' n0 :=
  eapply without_counter with (n:=N.to_nat n0);
  eapply multistep_c_spec; vm_compute; try reflexivity.

Definition Nsubge(a b:N) :=
(if b <=? a then Some (a-b) else None)%N.

Lemma Nsubge_spec a b c:
  Nsubge a b = Some c ->
  (a=c+b)%N.
Proof.
  unfold Nsubge.
  intros.
  destruct (N.leb_spec b a);
  inverts H; lia.
Qed.

Definition if_None {A} (a:option A) b :=
match a with
| None => b tt
| _ => a
end.

Notation "a ||| b" := (if_None a b) (at level 30, right associativity).

Ltac ec := econstructor.
Ltac eex := repeat eexists.

Ltac des_if H :=
  cbn[if_None] in H;
  cbn[if_Some] in H;
  let E:=fresh "E" in
  match type of H with
  | ?a ||| _ = _ =>
    destruct a eqn:E
  | ?a &&& _ = _ =>
    destruct a eqn:E
  end.

Ltac des_if' H := des_if H; [|inverts H].


Lemma segRLs_addmul_v3 a a' x b b' tm h h' w1 w2:
  segRLs tm (h^^b) (h'^^b') w1 w2 ->
  segRLs tm (h^^a) (h'^^a') w2 w2 ->
  segRLs tm (h^^(x*a+b)) (h'^^(x*a'+b')) w1 w2.
Proof.
  intros.
  rewrite (Nat.add_comm _ b).
  rewrite (Nat.add_comm _ b').
  do 2 rewrite lpow_add.
  eapply segRLs_trans.
  1: apply H.
  induction x; cbn[Nat.mul].
  - cbn.
    constructor.
  - cbn[lpow].
    do 2 rewrite lpow_add.
    eapply segRLs_trans.
    2: apply IHx.
    apply H0.
Qed.

Ltac esc :=
  (apply BoundedConfig.segRLs_c_spec with (T:=10^3); reflexivity) ||
  (apply BoundedConfig.sideRLs_c_spec with (T:=10^3); reflexivity) ||
  (eapply sideRLs_c_spec with (T:=10^6); [vm_compute; reflexivity | st; reflexivity]).


(* 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA, mirrored, states renamed A,B,C,D,E,F -> A,C,D,E,B,F
   so that it lines up with SBCv9.v TM2 (1RB0RF_0LC---_1LD1LC_0LE0LD_1RE1RF_0RC1RA). *)
Definition tm := Eval compute in (TM_from_str "1LC0RF_1RE---_1LD1LC_0LE0LD_1RB1RF_0RC1RA").

Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

Notation hR := (C,<[0;0]).
Notation hL := (D,[0;0]).
Notation hR' := (A,<[1;0;1]).
Notation hL' := (D,[0;1;1]).
Notation hRL := [(hR,hL)].
Notation hRL' := [(hR',hL')].
Notation hLR' := [(hL',hR')].

Definition LC a b := 0inf <* [1]^^a <* <[1;0]^^b.
Definition tm' := flip tm.

Definition LCo k b := 0inf <* [1] <* [1;1]^^k <* <[1;0]^^b.

Lemma LInco k b r:
  LCo k (1+b) {{{ (hL',L) }}} r -->*
  LCo (2+k) b {{{ (hR',R) }}} r.
Proof.
  ut.
  esx.
Qed.

Lemma LIncso n k b:
  sideRLs tm' (hLR'^^n) (LCo k (n+b)) (LCo (n*2+k) b).
Proof.
  gen k b.
  induction n; intros.
  1: esx.
  cbn[lpow].
  eapply sideRLs_trans.
  2: applys_eq (IHn (2+k) b); flia.
  ut.
  esx.
Qed.

Lemma LOvo k r:
  LCo k 0 {{{ (hL',L) }}} [0;0] *> r -->*
  LCo 1 (2+k) {{{ (hR',R) }}} [0] *> r.
Proof.
  ut.
  es.
Qed.

Lemma LRst_101o k b r:
  LCo k b {{{ (hL',L) }}} [1;0;1] *> r -->*
  LCo (2+k) b {{{ (hL',L) }}} [1] *> r.
Proof.
  ut.
  es.
Qed.

Lemma LRst_11o k b r:
  LCo k b {{{ (hL',L) }}} [1;1] *> r -->*
  LCo (2+k) b {{{ (hR',R) }}} r.
Proof.
  ut.
  es.
Qed.

Lemma LRst_10o k b r r':
  sideRLs tm hRL r r' ->
  LCo k (1+b) {{{ (hL',L) }}} [1;0] *> r -->*
  LCo (2+k) b {{{ (hL',L) }}} [0;0] *> r'.
Proof.
  intros.
  eapply sideRLs_1 in H.
  ut.
  es; er.
  follow100 H.
  er.
Qed.

Lemma init:
  c0 -->*
  LCo 5 5 {{{ (hL',L) }}} [1;0] *> 0inf.
Proof.
  esx.
Qed.

Inductive Tp :=
| t0 | t1.

Notation "x ~ 1" := (N.succ_double x) : N_scope.
Notation "x ~ 0" := (N.double x) : N_scope.

Fixpoint rest T r tp: option N :=
match T with
| O => None
| S T =>
match tp with
| t0 =>
  (skip_prefix [0;0;0;0] r &&& (fun r =>
  (rest T r t0 &&& (fun s =>
  Some (s~1)%N)))) ||| (fun _ =>

  (skip_prefix [0;1;1;0] r &&& (fun r =>
  (rest T r t0 &&& (fun s =>
  Some (s~0)%N)))) ||| (fun _ =>

  (skip_prefix [0;0;1;1] r &&& (fun r =>
  (rest T r t1 &&& (fun s =>
  Some (s~1)%N)))) ||| (fun _ =>

  (skip_prefix [0;1;1;1] r &&& (fun r =>
  (rest T r t1 &&& (fun s =>
  Some (s~0)%N)))) ||| (fun _ =>
  
  Some 0%N))))
| t1 =>
  (skip_prefix [1;1] r &&& (fun r =>
  (rest T r t1 &&& (fun s =>
  Some s)))) ||| (fun _ =>

  (skip_prefix [0;0] r &&& (fun r =>
  (rest T r t0 &&& (fun s =>
  Some (s~1)%N)))) ||| (fun _ =>

  (skip_prefix [1;0] r &&& (fun r =>
  (rest T r t0 &&& (fun s =>
  Some (s~0)%N)))) ||| (fun _ =>
  
  Some 0%N)))
end
end.


Fixpoint RIncs T k r tp: option side :=
match T with
| O => None
| S T =>
if (k=?0)%N then Some r else
let k2:=N.div2 k in
match tp with
| t0 =>
  if (k mod 2 =? 0)%N then
    (skip_prefix [0;0;0;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([0;0;0;0]*>r))))) ||| (fun _ =>

    (skip_prefix [0;1;1;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([0;1;1;0]*>r))))) ||| (fun _ =>

    (skip_prefix [0;0;1;1] r &&& (fun r =>
    (RIncs T (k2)%N r t1 &&& (fun r =>
    Some ([0;0;1;1]*>r))))) ||| (fun _ =>

    (skip_prefix [0;1;1;1] r &&& (fun r =>
    (RIncs T (k2)%N r t1 &&& (fun r =>
    Some ([0;1;1;1]*>r))))) ||| (fun _ =>

    None))))
  else
    (skip_prefix [0;0;0;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([0;1;1;0]*>r))))) ||| (fun _ =>

    (skip_prefix [0;1;1;0] r &&& (fun r =>
    (RIncs T (k2+1)%N r t0 &&& (fun r =>
    Some ([0;0;0;0]*>r))))) ||| (fun _ =>

    (skip_prefix [0;0;1;1] r &&& (fun r =>
    (RIncs T (k2)%N r t1 &&& (fun r =>
    Some ([0;1;1;1]*>r))))) ||| (fun _ =>

    (skip_prefix [0;1;1;1] r &&& (fun r =>
    (RIncs T (k2+1)%N r t1 &&& (fun r =>
    Some ([0;0;1;1]*>r))))) ||| (fun _ =>

    None))))
| t1 =>
  (skip_prefix [1;1] r &&& (fun r =>
  RIncs T k r t1 &&& (fun r =>
  Some ([1;1]*>r)))) ||| (fun _ =>
  if (k mod 2 =? 0)%N then
    (skip_prefix [0;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([0;0]*>r))))) ||| (fun _ =>

    (skip_prefix [1;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([1;0]*>r))))) ||| (fun _ =>

    None))
  else
    (skip_prefix [0;0] r &&& (fun r =>
    (RIncs T (k2)%N r t0 &&& (fun r =>
    Some ([1;0]*>r))))) ||| (fun _ =>

    (skip_prefix [1;0] r &&& (fun r =>
    (RIncs T (k2+1)%N r t0 &&& (fun r =>
    Some ([0;0]*>r))))) ||| (fun _ =>

    None))
  )
end
end.

Definition Tp_eval tp :=
match tp with
| t0 => hRL
| t1 => hRL'
end.

Local Opaque Str_app.

Lemma RIncs_spec T k r tp r':
  RIncs T k r tp = Some r' ->
  sideRLs tm ((Tp_eval tp)^^(N.to_nat k)) r r'.
Proof.
  gen k r tp r'.
  induction T; intros.
  1: inverts H.
  cbn[RIncs] in H.
  destruct (N.eqb_spec k 0).
  1: inverts H; subst; apply sideRLseq_O.
  destruct tp.
  {
    destruct (N.eqb_spec (k mod 2) 0).
    {
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      inverts H.
    }
    {
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 1).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 0).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      clear E.
      des_if H.
      {
        inverts H.
        do 2 des_if' E.
        inverts E.
        apply skip_prefix_spec in E0; subst.
        eapply segRLs_sideRLs_concat.
        2: apply IHT,E1.
        applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 1).
        1,2: apply feq; [reflexivity|lia].
        1,2: esc.
      }
      inverts H.
    }
  }
  des_if H.
  {
    inverts H.
    do 2 des_if' E.
    inverts E.
    apply skip_prefix_spec in E0; subst.
    eapply segRLs_sideRLs_concat.
    2: apply IHT,E1.
    apply segRLs_wall''; esc.
  }
  clear E.
  destruct (N.eqb_spec (k mod 2) 0).
  {
    des_if H.
    {
      inverts H.
      do 2 des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      eapply segRLs_sideRLs_concat.
      2: apply IHT,E1.
      applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
      1,2: apply feq; [reflexivity|lia].
      1,2: esc.
    }
    clear E.
    des_if H.
    {
      inverts H.
      do 2 des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      eapply segRLs_sideRLs_concat.
      2: apply IHT,E1.
      applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 0 0).
      1,2: apply feq; [reflexivity|lia].
      1,2: esc.
    }
    inverts H.
  }
  {
    des_if H.
    {
      inverts H.
      do 2 des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      eapply segRLs_sideRLs_concat.
      2: apply IHT,E1.
      applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 0).
      1,2: apply feq; [reflexivity|lia].
      1,2: esc.
    }
    clear E.
    des_if H.
    {
      inverts H.
      do 2 des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      eapply segRLs_sideRLs_concat.
      2: apply IHT,E1.
      applys_eq (segRLs_addmul_v3 2 1 (N.to_nat (k/2)) 1 1).
      1,2: apply feq; [reflexivity|lia].
      1,2: esc.
    }
    inverts H.
  }
Qed.

Local Transparent Str_app.



(* Macro steps, with the timer written as a = 2k+1 (the timer lemmas need a odd). *)
Inductive Config :=
| cfgL'(k b:N)(r:side)
| cfgR'(k b:N)(r:side).

Definition Config_eval x :=
match x with
| cfgL' k b r => LCo (N.to_nat k) (N.to_nat b) {{{ (hL',L) }}} r
| cfgR' k b r => LCo (N.to_nat k) (N.to_nat b) {{{ (hR',R) }}} r
end.

Definition maxT: nat := Eval vm_compute in 10000.
Definition maxT': nat := 100000.

Fixpoint mstep x :=
match x with
| cfgR' k b r =>
  sideRLs_c tm hRL' r maxT' &&& (fun r =>
  Some (cfgL' k b r))
| cfgL' k b r =>
  (skip_prefix [1;0;1] r &&& (fun r =>
  Some (cfgL' (2+k) b ([1]*>r)))) ||| (fun _ =>

  (skip_prefix [1;1] r &&& (fun r =>
  Some (cfgR' (2+k) b r))) ||| (fun _ =>

  if (b=?0)%N then
    skip_prefix [0;0] r &&& (fun r =>
    Some (cfgR' 1 (2+k) ([0]*>r)))
  else
    rest maxT r t1 &&& (fun n =>
    if (n=?0)%N then
      Some (cfgR' (2+k) (b-1) r)
    else
      Some (N.min n b) &&& (fun n =>
      RIncs maxT n r t1 &&& (fun r =>
      Some (cfgL' (k+n*2) (b-n) r))))
  ))
end.

Local Opaque N.add maxT maxT'.

Lemma mstep_spec x x':
  mstep x = Some x' ->
  Config_eval x -->*
  Config_eval x'.
Proof.
  intros.
  destruct x; cbn[mstep] in H.
  - des_if H.
    { inverts H.
      des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      cbn[Config_eval].
      rewrite Nnat.N2Nat.inj_add.
      apply LRst_101o. }
    clear E.
    des_if H.
    { inverts H.
      des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      cbn[Config_eval].
      rewrite Nnat.N2Nat.inj_add.
      apply LRst_11o. }
    clear E.
    destruct (N.eqb_spec b 0).
    { subst.
      des_if' H.
      inverts H.
      apply skip_prefix_spec in E; subst.
      cbn[Config_eval].
      applys_eq (LOvo (N.to_nat k) s); flia. }
    { des_if' H.
      cbn[if_Some] in H.
      destruct (N.eqb_spec n0 0).
      { subst.
        inverts H.
        cbn[Config_eval].
        applys_eq (LInco (N.to_nat k) (N.to_nat (b-1))); flia. }
      { des_if' H.
        inverts H.
        apply RIncs_spec in E0.
        cbn[Config_eval].
        eapply sideRLs_concat_1L.
        1: apply E0.
        remember (N.min n0 b) as n'.
        applys_eq (LIncso (N.to_nat n') (N.to_nat k) (N.to_nat (b-n'))); flia. }
    }
  - des_if' H.
    inverts H.
    eapply sideRLs_c_spec in E.
    2: reflexivity.
    eapply sideRLs_1 in E.
    cbn[Config_eval].
    follow100 E; finish.
Qed.

Fixpoint msteps T x :=
match T with
| O => Some x
| S T =>
  (mstep x &&& (fun x =>
  msteps T x)) ||| (fun _ => Some x)
end.

Lemma msteps_spec T x x':
  msteps T x = Some x' ->
  Config_eval x -->*
  Config_eval x'.
Proof.
  gen x.
  induction T; intros.
  - inverts H.
    finish.
  - cbn[msteps] in H.
    des_if' H.
    + inverts H.
      des_if' E.
      apply mstep_spec in E0.
      follow E0.
      auto.
    + finish.
Qed.

Print Assumptions msteps_spec.
