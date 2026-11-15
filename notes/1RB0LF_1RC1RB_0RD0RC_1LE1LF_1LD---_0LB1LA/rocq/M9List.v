From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia ZArith List String.
From BusyCoq Require Import Longitudinal.
From M9 Require Import M9Timer M9Carry M9Windows2 M9Reduce.
Open Scope list.
Import Eqb.

(* Words as finite lists: the tape right of the timer is w *> 0inf. *)
Fixpoint pfx (p w: list Sym) : option (list Sym) :=
match p with
| [] => Some w
| x::p' =>
  match w with
  | [] => match x with S0 => pfx p' [] | S1 => None end
  | y::w' => if sym_eqb x y then pfx p' w' else None
  end
end.

Lemma sym_eqb_eq x y: sym_eqb x y = true -> x = y.
Proof. destruct x, y; cbn; congruence. Qed.

Lemma pfx_spec p w w':
  pfx p w = Some w' -> w *> 0inf = p *> w' *> 0inf.
Proof.
  gen w. induction p as [|x p IH]; intros w H; cbn in H.
  - inverts H. reflexivity.
  - destruct w as [|y w].
    + destruct x; [|discriminate].
      apply IH in H. cbn. rewrite <-H. cbn. apply const_unfold.
    + destruct (sym_eqb x y) eqn:E; [|discriminate].
      apply sym_eqb_eq in E; subst.
      apply IH in H. cbn. rewrite H. reflexivity.
Qed.

(* windows: (prefix, replacement, abnormal return) *)
Definition win0 : list (list Sym * list Sym * bool) := [
  ([0;1;1;0;1;1;0;0], [0;0;1;1;1;1;0;0], false);
  ([0;1;1;0;1;1;1;1], [0;0;1;1;1;1;1;1], false);
  ([0;1;1;0;1;1;1;0], [0;0;1;1;1;1;1;0], false);
  ([0;1;1;0;1;1;0;1], [0;0;1;1;1;1;0;1], false);
  ([0;1;1;0;0;0;0;1], [0;0;0;0;0;1;1;1], false);
  ([0;1;1;0;1;0;0;0], [0;0;1;1;1;0;0;0], false);
  ([0;1;1;0;1;0;0;1], [0;0;1;1;1;0;0;1], false);
  ([0;1;1;0;1;0;1;0], [0;0;1;1;1;0;1;0], false);
  ([0;1;1;0;1;0;1;1], [0;0;1;1;1;0;1;1], false);
  ([0;1;1;0;0;0;1;0], [0;0;0;0;0;1;1;0], false);
  ([0;1;1;0;0;1;0;0], [1;1;1;1;1;1;1;0], true);
  ([0;1;1;0;0;1;0;1], [1;1;1;1;1;1;1;1], true)].
Definition win1 : list (list Sym * list Sym) := [
  ([1;0;1;1;0;0], [1;1;1;1;0;0]);
  ([1;0;1;1;1;1], [1;1;1;1;1;1]);
  ([1;0;1;1;1;0], [1;1;1;1;1;0]);
  ([1;0;1;1;0;1], [1;1;1;1;0;1]);
  ([1;0;0;0;0;1], [0;0;0;1;1;1]);
  ([1;0;1;0;0;0], [1;1;1;0;0;0]);
  ([1;0;1;0;0;1], [1;1;1;0;0;1]);
  ([1;0;1;0;1;0], [1;1;1;0;1;0]);
  ([1;0;1;0;1;1], [1;1;1;0;1;1]);
  ([1;0;0;0;1;0], [0;0;0;1;1;0]);
  ([1;0;0;1;0;0], [1;1;1;1;1;0]);
  ([1;0;0;1;0;1], [1;1;1;1;1;1]);
  ([0;1;0;0], [1;1;0;0]);
  ([0;1;0;1], [1;1;0;1]);
  ([0;1;1;0], [1;1;1;0]);
  ([0;1;1;1], [1;1;1;1])].

Definition ret (ab: bool) (tp: Tp) := if ab then [(hR,X)] else Tp_eval tp.

Lemma win0_ok pre post ab: In (pre,post,ab) win0 -> segRLs tm (ret ab t0) [] pre post.
Proof.
  intros H. cbn in H.
  repeat destruct H as [H|H]; try contradiction; inverts H; cbn;
    first [apply W0_1100|apply W0_1111|apply W0_1110|apply W0_1101|apply W0_0001
          |apply X0_01101000|apply X0_01101001|apply X0_01101010|apply X0_01101011|apply X0_01100010
          |apply AB0_0100|apply AB0_0101].
Qed.

Lemma win1_ok pre post: In (pre,post) win1 -> segRLs tm (Tp_eval t1) [] pre post.
Proof.
  intros H. cbn in H.
  repeat destruct H as [H|H]; try contradiction; inverts H; cbn;
    first [apply W1_1100|apply W1_1111|apply W1_1110|apply W1_1101|apply W1_0001
          |apply X1_101000|apply X1_101001|apply X1_101010|apply X1_101011|apply X1_100010
          |apply X1_100100|apply X1_100101|apply X1_0100|apply X1_0101|apply W1_0110|apply W1_0111].
Qed.

Fixpoint find_win0 (ws: list (list Sym * list Sym * bool)) w :=
match ws with
| [] => None
| (pre,post,ab)::ws => match pfx pre w with Some w' => Some (post ++ w', ab) | None => find_win0 ws w end
end.
Fixpoint find_win1 (ws: list (list Sym * list Sym)) w :=
match ws with
| [] => None
| (pre,post)::ws => match pfx pre w with Some w' => Some (post ++ w') | None => find_win1 ws w end
end.

Lemma find_win0_spec ws w w' ab:
  (forall pre post ab, In (pre,post,ab) ws -> segRLs tm (ret ab t0) [] pre post) ->
  find_win0 ws w = Some (w', ab) ->
  sideRLs tm (ret ab t0) (w *> 0inf) (w' *> 0inf).
Proof.
  induction ws as [|[[pre post] ab'] ws IH]; cbn; intros Hw H.
  1: discriminate.
  destruct (pfx pre w) eqn:E.
  - inverts H. apply pfx_spec in E. rewrite E, Str_app_assoc.
    exact (segRLs_sideRLs_concat (Hw _ _ _ (or_introl eq_refl)) (sideRLseq_O tm _)).
  - refine (IH _ H). intros p0 q0 a0 Hin. apply Hw. right. exact Hin.
Qed.

Lemma find_win1_spec ws w w':
  (forall pre post, In (pre,post) ws -> segRLs tm (Tp_eval t1) [] pre post) ->
  find_win1 ws w = Some w' ->
  sideRLs tm (Tp_eval t1) (w *> 0inf) (w' *> 0inf).
Proof.
  induction ws as [|[pre post] ws IH]; cbn; intros Hw H.
  1: discriminate.
  destruct (pfx pre w) eqn:E.
  - inverts H. apply pfx_spec in E. rewrite E, Str_app_assoc.
    exact (segRLs_sideRLs_concat (Hw _ _ (or_introl eq_refl)) (sideRLseq_O tm _)).
  - refine (IH _ H). intros p0 q0 Hin. apply Hw. right. exact Hin.
Qed.

Fixpoint carryL (T:nat) (w: list Sym) (tp: Tp) : option (list Sym * bool) :=
match T with
| O => None
| S T =>
match tp with
| t0 =>
  match find_win0 win0 w with Some p => Some p | None =>
  match pfx [0;1;1;0] w with
  | Some w1 =>
    match carryL T w1 t0 with
    | Some (w2, true) => Some ([1;1;1;1] ++ w2, true)
    | Some (w2, false) => Some ([0;0;0;0] ++ w2, false)
    | None => None end
  | None =>
  match pfx [0;1;1;1] w with
  | Some w1 =>
    match carryL T w1 t1 with
    | Some (w2, false) => Some ([0;0;1;1] ++ w2, false)
    | _ => None end
  | None =>
  match pfx [0;0;0;0] w with Some w1 => Some ([0;1;1;0] ++ w1, false) | None =>
  match pfx [0;0;1;1] w with Some w1 => Some ([0;1;1;1] ++ w1, false) | None => None end end end end end
| t1 =>
  match find_win1 win1 w with Some w' => Some (w', false) | None =>
  match pfx [1;1] w with
  | Some w1 =>
    match carryL T w1 t1 with
    | Some (w2, false) => Some ([1;1] ++ w2, false)
    | _ => None end
  | None =>
  match pfx [1;0] w with
  | Some w1 =>
    match carryL T w1 t0 with
    | Some (w2, true) => Some ([1;1] ++ w2, false)
    | Some (w2, false) => Some ([0;0] ++ w2, false)
    | None => None end
  | None =>
  match pfx [0;0] w with Some w1 => Some ([1;0] ++ w1, false) | None => None end end end end
end
end.

Lemma seg_step {hs1 hs2 d d' w w1 w2}:
  segRLs tm hs1 hs2 d d' ->
  pfx d w = Some w1 ->
  sideRLs tm hs2 (w1 *> 0inf) (w2 *> 0inf) ->
  sideRLs tm hs1 (w *> 0inf) ((d' ++ w2) *> 0inf).
Proof.
  intros Hs E H.
  apply pfx_spec in E. rewrite E, Str_app_assoc.
  exact (segRLs_sideRLs_concat Hs H).
Qed.

Lemma seg_end {hs1 d d' w w1}:
  segRLs tm hs1 [] d d' ->
  pfx d w = Some w1 ->
  sideRLs tm hs1 (w *> 0inf) ((d' ++ w1) *> 0inf).
Proof.
  intros Hs E. eapply seg_step; eauto. apply sideRLseq_O.
Qed.

Lemma carryL_spec T w tp w' ab:
  carryL T w tp = Some (w', ab) ->
  sideRLs tm (ret ab tp) (w *> 0inf) (w' *> 0inf).
Proof.
  gen w tp w' ab.
  induction T; intros.
  1: discriminate.
  destruct tp; cbn[carryL] in H.
  - destruct (find_win0 win0 w) as [[w0 ab0]|] eqn:Ew.
    { inverts H. apply (find_win0_spec win0); auto. apply win0_ok. }
    destruct (pfx [0;1;1;0] w) as [w1|] eqn:E1.
    { destruct (carryL T w1 t0) as [[w2 [|]]|] eqn:Ec; inverts H.
      - apply IHT in Ec. exact (seg_step ABD0_0110 E1 Ec).
      - apply IHT in Ec. exact (seg_step D0_0110 E1 Ec). }
    destruct (pfx [0;1;1;1] w) as [w1|] eqn:E2.
    { destruct (carryL T w1 t1) as [[w2 [|]]|] eqn:Ec; inverts H.
      apply IHT in Ec. exact (seg_step D0_0111 E2 Ec). }
    destruct (pfx [0;0;0;0] w) as [w1|] eqn:E3.
    { inverts H. exact (seg_end A0_0000 E3). }
    destruct (pfx [0;0;1;1] w) as [w1|] eqn:E4.
    { inverts H. exact (seg_end A0_0011 E4). }
    discriminate.
  - destruct (find_win1 win1 w) as [w0|] eqn:Ew.
    { inverts H. cbn[ret]. apply (find_win1_spec win1); auto. apply win1_ok. }
    destruct (pfx [1;1] w) as [w1|] eqn:E1.
    { destruct (carryL T w1 t1) as [[w2 [|]]|] eqn:Ec; inverts H.
      apply IHT in Ec. exact (seg_step D1_11 E1 Ec). }
    destruct (pfx [1;0] w) as [w1|] eqn:E2.
    { destruct (carryL T w1 t0) as [[w2 [|]]|] eqn:Ec; inverts H.
      - apply IHT in Ec. exact (seg_step ABD1_10 E2 Ec).
      - apply IHT in Ec. exact (seg_step D1_10 E2 Ec). }
    destruct (pfx [0;0] w) as [w1|] eqn:E3.
    { inverts H. exact (seg_end A1_00 E3). }
    discriminate.
Qed.

Lemma carryL_t1 T w w' ab: carryL T w t1 = Some (w', ab) -> ab = false.
Proof.
  destruct T; cbn; intros H. 1: discriminate.
  repeat (match type of H with context [match ?e with _ => _ end] => destruct e end);
  try discriminate; inverts H; auto.
Qed.

Inductive CfgL :=
| LL (k b:N) (w: list Sym)
| LR (k b:N) (w: list Sym).

Definition evalL x :=
match x with
| LL k b w => Config_eval (cfgL' k b (w *> 0inf))
| LR k b w => Config_eval (cfgR' k b (w *> 0inf))
end.

(* One macro step: at b = 0 the timer resets (prefix 101 or 11) or overflows (prefix 00); otherwise one increment.
   A sweep is 0 -> 1 or a carry. None = stuck. *)
Definition stepL x :=
match x with
| LL k b w =>
  if (b =? 0)%N then
    match pfx [1;0;1] w with Some w' => Some (LL (2+k) 0 (1::w')) | None =>
    match pfx [1;1] w with Some w' => Some (LR (2+k) 0 w') | None =>
    match pfx [0;0] w with Some w' => Some (LR 1 (2+k) (0::w')) | None => None end end end
  else Some (LR (2+k) (b-1) w)
| LR k b w =>
  match pfx [0] w with Some w' => Some (LL k b (1::w')) | None =>
  match carryL (S (List.length w)) w t1 with Some (w', _) => Some (LL k b w') | None => None end end
end.

Local Opaque N.add.

Lemma stepL_plus x y: stepL x = Some y -> evalL x -->+ evalL y.
Proof.
  destruct x as [k b w|k b w]; cbn[stepL]; intros H.
  - destruct (N.eqb_spec b 0).
    + subst.
      destruct (pfx [1;0;1] w) as [w'|] eqn:E1.
      { inverts H. apply pfx_spec in E1. cbn[evalL Config_eval]. rewrite E1.
        rewrite Nnat.N2Nat.inj_add. apply LRst_101o_p. }
      destruct (pfx [1;1] w) as [w'|] eqn:E2.
      { inverts H. apply pfx_spec in E2. cbn[evalL Config_eval]. rewrite E2.
        rewrite Nnat.N2Nat.inj_add. apply LRst_11o_p. }
      destruct (pfx [0;0] w) as [w'|] eqn:E3.
      { inverts H. apply pfx_spec in E3. cbn[evalL Config_eval]. rewrite E3.
        applys_eq (LOvo_p (N.to_nat k) (w' *> 0inf)); flia. }
      discriminate.
    + inverts H. cbn[evalL Config_eval].
      applys_eq (LInco_p (N.to_nat k) (N.to_nat (b-1)) (w *> 0inf)); flia.
  - destruct (pfx [0] w) as [w'|] eqn:E1.
    { inverts H. cbn[evalL Config_eval].
      pose proof (seg_end S_0 E1) as Hs.
      eapply sideRLs_1 in Hs. apply Hs. }
    destruct (carryL (S (List.length w)) w t1) as [[w' ab]|] eqn:Ec.
    2: discriminate.
    inverts H. cbn[evalL Config_eval].
    pose proof (carryL_t1 _ _ _ _ Ec); subst.
    apply carryL_spec in Ec. cbn[ret Tp_eval] in Ec.
    eapply sideRLs_1 in Ec. apply Ec.
Qed.

Fixpoint iterL n x :=
match n with
| O => Some x
| S n => match stepL x with Some y => iterL n y | None => None end
end.

Definition startL := LL 5 5 [1;0].

Theorem holdout_nonhalt_of_iterL:
  (forall n, iterL n startL <> None) -> ~ halts holdout c0.
Proof.
  intros H.
  apply (perm_nonhalt holdout tmR rename A _ correspondence).
  apply flip_halts_c0.
  rewrite flip_tmR.
  rewrite (halts_evstep_iff _ _ _ init).
  change (LCo 5 5 {{{ (hL',L) }}} [1;0] *> 0inf) with (evalL startL).
  apply progress_nonhalt_cond with (P := fun x => forall n, iterL n x <> None).
  2: exact H.
  intros x Hx.
  pose proof (Hx (S O)) as H1. cbn[iterL] in H1.
  destruct (stepL x) as [y|] eqn:E.
  2: congruence.
  exists y. split.
  - apply stepL_plus, E.
  - intros n. specialize (Hx (S n)). cbn[iterL] in Hx. rewrite E in Hx. exact Hx.
Qed.

Print Assumptions holdout_nonhalt_of_iterL.
