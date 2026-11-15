From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia ZArith List String.
From BusyCoq Require Import Longitudinal.
From M9 Require Import M9Timer.
Open Scope list.
Import Eqb.

(* The 13 carry rules. A carry sweep turns every digit below the parse stop from 1 to 0 (the RIncs cases)
   and ends at the stop with one of these: the head enters the last digit (or the stop itself) with the
   pass of that parse state (t0: hRL, t1: hRL') and turns back inside the 8-cell window, so the tape beyond
   is never read. *)
Ltac esw := apply BoundedConfig.segRLs_c_spec with (T:=10^3); reflexivity.

Lemma W0_1100: segRLs tm hRL [] [0;1;1;0;1;1;0;0] [0;0;1;1;1;1;0;0]. Proof. esw. Qed.
Lemma W0_1111: segRLs tm hRL [] [0;1;1;0;1;1;1;1] [0;0;1;1;1;1;1;1]. Proof. esw. Qed.
Lemma W0_1110: segRLs tm hRL [] [0;1;1;0;1;1;1;0] [0;0;1;1;1;1;1;0]. Proof. esw. Qed.
Lemma W0_1101: segRLs tm hRL [] [0;1;1;0;1;1;0;1] [0;0;1;1;1;1;0;1]. Proof. esw. Qed.
Lemma W0_0001: segRLs tm hRL [] [0;1;1;0;0;0;0;1] [0;0;0;0;0;1;1;1]. Proof. esw. Qed.
Lemma W1_1100: segRLs tm hRL' [] [1;0;1;1;0;0] [1;1;1;1;0;0]. Proof. esw. Qed.
Lemma W1_1111: segRLs tm hRL' [] [1;0;1;1;1;1] [1;1;1;1;1;1]. Proof. esw. Qed.
Lemma W1_1110: segRLs tm hRL' [] [1;0;1;1;1;0] [1;1;1;1;1;0]. Proof. esw. Qed.
Lemma W1_1101: segRLs tm hRL' [] [1;0;1;1;0;1] [1;1;1;1;0;1]. Proof. esw. Qed.
Lemma W1_0001: segRLs tm hRL' [] [1;0;0;0;0;1] [0;0;0;1;1;1]. Proof. esw. Qed.
Lemma W1_0110: segRLs tm hRL' [] [0;1;1;0] [1;1;1;0]. Proof. esw. Qed.
Lemma W1_0111: segRLs tm hRL' [] [0;1;1;1] [1;1;1;1]. Proof. esw. Qed.
Lemma W0_0111_0110: segRLs tm hRL [] [0;1;1;1;0;1;1;0] [0;0;1;1;1;1;1;0]. Proof. esw. Qed.

(* the 1-digits a carry zeroes on its way to the stop *)
Lemma D0_0110: segRLs tm hRL hRL [0;1;1;0] [0;0;0;0]. Proof. esw. Qed.
Lemma D0_0111: segRLs tm hRL hRL' [0;1;1;1] [0;0;1;1]. Proof. esw. Qed.
Lemma D1_11: segRLs tm hRL' hRL' [1;1] [1;1]. Proof. esw. Qed.
Lemma D1_10: segRLs tm hRL' hRL [1;0] [0;0]. Proof. esw. Qed.
(* the sweep after an overflow (and after LRst_11) when r starts with 0 *)
Lemma S_0: segRLs tm hRL' [] [0] [1]. Proof. esw. Qed.
(* a carry absorbed by a 0-digit (only near the top) *)
Lemma A0_0000: segRLs tm hRL [] [0;0;0;0] [0;1;1;0]. Proof. esw. Qed.
Lemma A0_0011: segRLs tm hRL [] [0;0;1;1] [0;1;1;1]. Proof. esw. Qed.
Lemma A1_00: segRLs tm hRL' [] [0;0] [1;0]. Proof. esw. Qed.

Definition win (pre post: list Sym) (r: side) : option side :=
  skip_prefix pre r &&& (fun r => Some (post *> r)).

Fixpoint carry T r tp : option side :=
match T with
| O => None
| S T =>
match tp with
| t0 =>
  win [0;1;1;0;1;1;0;0] [0;0;1;1;1;1;0;0] r ||| (fun _ =>
  win [0;1;1;0;1;1;1;1] [0;0;1;1;1;1;1;1] r ||| (fun _ =>
  win [0;1;1;0;1;1;1;0] [0;0;1;1;1;1;1;0] r ||| (fun _ =>
  win [0;1;1;0;1;1;0;1] [0;0;1;1;1;1;0;1] r ||| (fun _ =>
  win [0;1;1;0;0;0;0;1] [0;0;0;0;0;1;1;1] r ||| (fun _ =>
  win [0;1;1;1;0;1;1;0] [0;0;1;1;1;1;1;0] r ||| (fun _ =>
  (skip_prefix [0;1;1;0] r &&& (fun r => carry T r t0 &&& (fun r => Some ([0;0;0;0] *> r)))) ||| (fun _ =>
  (skip_prefix [0;1;1;1] r &&& (fun r => carry T r t1 &&& (fun r => Some ([0;0;1;1] *> r)))) ||| (fun _ =>
  win [0;0;0;0] [0;1;1;0] r ||| (fun _ =>
  win [0;0;1;1] [0;1;1;1] r ||| (fun _ =>
  None))))))))))
| t1 =>
  win [1;0;1;1;0;0] [1;1;1;1;0;0] r ||| (fun _ =>
  win [1;0;1;1;1;1] [1;1;1;1;1;1] r ||| (fun _ =>
  win [1;0;1;1;1;0] [1;1;1;1;1;0] r ||| (fun _ =>
  win [1;0;1;1;0;1] [1;1;1;1;0;1] r ||| (fun _ =>
  win [1;0;0;0;0;1] [0;0;0;1;1;1] r ||| (fun _ =>
  win [0;1;1;0] [1;1;1;0] r ||| (fun _ =>
  win [0;1;1;1] [1;1;1;1] r ||| (fun _ =>
  (skip_prefix [1;1] r &&& (fun r => carry T r t1 &&& (fun r => Some ([1;1] *> r)))) ||| (fun _ =>
  (skip_prefix [1;0] r &&& (fun r => carry T r t0 &&& (fun r => Some ([0;0] *> r)))) ||| (fun _ =>
  win [0;0] [1;0] r ||| (fun _ =>
  None))))))))))
end
end.

Lemma win_spec pre post r r' hs:
  segRLs tm hs [] pre post ->
  win pre post r = Some r' ->
  sideRLs tm hs r r'.
Proof.
  unfold win. intros H E.
  des_if' E. inverts E.
  apply skip_prefix_spec in E0; subst.
  exact (segRLs_sideRLs_concat H (sideRLseq_O tm _)).
Qed.

Local Opaque Str_app.

Lemma carry_spec T r tp r':
  carry T r tp = Some r' ->
  sideRLs tm (Tp_eval tp) r r'.
Proof.
  gen r tp r'.
  induction T; intros.
  1: inverts H.
  destruct tp; cbn[carry Tp_eval] in *.
  - des_if H. { inverts H. eapply win_spec; [apply W0_1100|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W0_1111|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W0_1110|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W0_1101|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W0_0001|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W0_0111_0110|eauto]. } clear E.
    des_if H.
    { inverts H. do 2 des_if' E. inverts E.
      apply skip_prefix_spec in E0; subst.
      exact (segRLs_sideRLs_concat D0_0110 (IHT _ t0 _ E1)). }
    clear E.
    des_if H.
    { inverts H. do 2 des_if' E. inverts E.
      apply skip_prefix_spec in E0; subst.
      exact (segRLs_sideRLs_concat D0_0111 (IHT _ t1 _ E1)). }
    clear E.
    des_if H. { inverts H. eapply win_spec; [apply A0_0000|eauto]. } clear E.
    des_if' H. inverts H. eapply win_spec; [apply A0_0011|eauto].
  - des_if H. { inverts H. eapply win_spec; [apply W1_1100|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_1111|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_1110|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_1101|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_0001|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_0110|eauto]. } clear E.
    des_if H. { inverts H. eapply win_spec; [apply W1_0111|eauto]. } clear E.
    des_if H.
    { inverts H. do 2 des_if' E. inverts E.
      apply skip_prefix_spec in E0; subst.
      exact (segRLs_sideRLs_concat D1_11 (IHT _ t1 _ E1)). }
    clear E.
    des_if H.
    { inverts H. do 2 des_if' E. inverts E.
      apply skip_prefix_spec in E0; subst.
      exact (segRLs_sideRLs_concat D1_10 (IHT _ t0 _ E1)). }
    clear E.
    des_if' H. inverts H. eapply win_spec; [apply A1_00|eauto].
Qed.


(* Macro step with no simulation: every sweep is S_0 or a carry (13 windows). *)
Definition sweep T r := win [0] [1] r ||| (fun _ => carry T r t1).

Lemma sweep_spec T r r': sweep T r = Some r' -> sideRLs tm hRL' r r'.
Proof.
  unfold sweep. intros H.
  des_if H.
  - inverts H. eapply win_spec; [apply S_0|eauto].
  - apply (carry_spec T _ t1 _ H).
Qed.

Definition mstep2 x :=
match x with
| cfgR' k b r => sweep maxT r &&& (fun r => Some (cfgL' k b r))
| cfgL' _ _ _ => mstep x
end.

Local Opaque maxT maxT' N.add.

Lemma mstep2_spec x x':
  mstep2 x = Some x' ->
  Config_eval x -->* Config_eval x'.
Proof.
  intros.
  destruct x; cbn[mstep2] in H.
  - apply mstep_spec, H.
  - des_if' H. inverts H.
    apply sweep_spec in E.
    eapply sideRLs_1 in E.
    cbn[Config_eval].
    follow100 E; finish.
Qed.

Fixpoint mcount2 T x n :=
match T with
| O => (n, x)
| S T => match mstep2 x with Some x' => mcount2 T x' (N.succ n) | None => (n, x) end
end.

Lemma mcount2_spec T x n:
  Config_eval x -->* Config_eval (snd (mcount2 T x n)).
Proof.
  revert x n; induction T; intros; cbn.
  - finish.
  - destruct (mstep2 x) eqn:E.
    + apply mstep2_spec in E. follow E. apply IHT.
    + finish.
Qed.

Definition b_of x := match x with cfgL' _ b _ | cfgR' _ b _ => b end.

Definition run2 := mcount2 13000 (cfgL' 5 5 ([1;0]*>0inf)) 0.

(* From the blank tape, 13,000 macro steps in which every sweep is S_0 or a carry made of the lemmas above
   (no simulation of sweeps); the counter b then has 400 bits. *)
Theorem reach13000_rules: c0 -->* Config_eval (snd run2).
Proof.
  eapply evstep_trans. 1: apply init.
  apply (mcount2_spec 13000 (cfgL' 5 5 ([1;0]*>0inf)) 0).
Qed.

Lemma run2_facts: fst run2 = 13000%N /\ N.size (b_of (snd run2)) = 400%N.
Proof. vm_compute. split; reflexivity. Qed.

Print Assumptions reach13000_rules.
Print Assumptions run2_facts.
