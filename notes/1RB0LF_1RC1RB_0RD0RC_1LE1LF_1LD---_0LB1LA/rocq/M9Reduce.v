From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia ZArith List String.
From BusyCoq Require Import Longitudinal.
From M9 Require Import M9Timer M9Carry.
Open Scope list.
Import Eqb.

(* -->+ versions of the macro steps, so that "the macro simulator never gets stuck" gives non-halting. *)

Lemma LInco_p k b (r:side):
  LCo k (1+b) {{{ (hL',L) }}} r -->+
  LCo (2+k) b {{{ (hR',R) }}} r.
Proof. ut. esx. Qed.

Lemma LOvo_p k (r:side):
  LCo k 0 {{{ (hL',L) }}} [0;0] *> r -->+
  LCo 1 (2+k) {{{ (hR',R) }}} [0] *> r.
Proof. ut. es. Qed.

Lemma LRst_101o_p k b (r:side):
  LCo k b {{{ (hL',L) }}} [1;0;1] *> r -->+
  LCo (2+k) b {{{ (hL',L) }}} [1] *> r.
Proof. ut. es. Qed.

Lemma LRst_11o_p k b (r:side):
  LCo k b {{{ (hL',L) }}} [1;1] *> r -->+
  LCo (2+k) b {{{ (hR',R) }}} r.
Proof. ut. es. Qed.

Lemma sideRLs_concat_1_plus [tm0 hR hL n l1 l2 r1 r2]:
  sideRLs tm0 ([(hR,hL)]^^(S n)) r1 r2 ->
  sideRLs (flip tm0) ([(hL,hR)]^^(S n)) l1 l2 ->
  l1 {{{ (hR,R) }}} r1 -[tm0]->+
  l2 {{{ (hR,R) }}} r2.
Proof.
  intros HR HL.
  rewrite <-lrcons_lpow1 in HR by lia.
  replace (S n-1) with n in HR by lia.
  replace (S n) with (n+1) in HL by lia.
  rewrite lpow_add in HL.
  epose proof (sideRLs_split HL) as [l3 [HL1 HL2]].
  pose proof (sideRLs_concat HL1 HR) as H1.
  inverts HL2.
  inverts H6.
  unfold sideRL in H5.
  specialize (H5 r2).
  destruct hR,hL.
  eapply progress_trans. 1: apply H1.
  apply (unflip_progress _ _ _ H5).
Qed.

Lemma sideRLs_concat_1L_plus [tm0 hR hL n l1 l2 r1 r2]:
  sideRLs tm0 ([(hR,hL)]^^(S n)) r1 r2 ->
  sideRLs (flip tm0) ([(hL,hR)]^^(S n)) l1 l2 ->
  l1 {{{ (hL,L) }}} r1 -[tm0]->+
  l2 {{{ (hL,L) }}} r2.
Proof.
  intros HR HL.
  rewrite <-(flip_involutive tm0) in HR.
  epose proof (sideRLs_concat_1_plus HL HR) as H.
  destruct hR,hL.
  apply (unflip_progress _ _ _ H).
Qed.

Local Opaque N.add maxT maxT'.
Local Opaque Str_app.

Lemma mstep_plus x x':
  mstep x = Some x' ->
  Config_eval x -->+ Config_eval x'.
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
      apply LRst_101o_p. }
    clear E.
    des_if H.
    { inverts H.
      des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      cbn[Config_eval].
      rewrite Nnat.N2Nat.inj_add.
      apply LRst_11o_p. }
    clear E.
    destruct (N.eqb_spec b 0).
    { subst.
      des_if' H.
      inverts H.
      apply skip_prefix_spec in E; subst.
      cbn[Config_eval].
      applys_eq (LOvo_p (N.to_nat k) s); flia. }
    { des_if' H.
      cbn[if_Some] in H.
      destruct (N.eqb_spec n0 0).
      { subst.
        inverts H.
        cbn[Config_eval].
        applys_eq (LInco_p (N.to_nat k) (N.to_nat (b-1))); flia. }
      { des_if' H.
        inverts H.
        apply RIncs_spec in E0.
        cbn[Config_eval].
        remember (N.min n0 b) as n'.
        assert (Hn: N.to_nat n' = S (N.to_nat n' - 1)) by lia.
        pose proof (LIncso (N.to_nat n') (N.to_nat k) (N.to_nat (b-n'))) as HL.
        rewrite Hn in E0, HL.
        eapply sideRLs_concat_1L_plus.
        1: apply E0.
        applys_eq HL; flia. }
    }
  - des_if' H.
    inverts H.
    eapply sideRLs_c_spec in E.
    2: reflexivity.
    eapply sideRLs_1 in E.
    apply E.
Qed.

Lemma mstep2_plus x x':
  mstep2 x = Some x' ->
  Config_eval x -->+ Config_eval x'.
Proof.
  intros.
  destruct x; cbn[mstep2] in H.
  - apply mstep_plus, H.
  - des_if' H. inverts H.
    apply sweep_spec in E.
    eapply sideRLs_1 in E.
    apply E.
Qed.

(* The same macro step with the fuel T as a parameter (the fixed maxT runs out once the tape is long). *)
Definition mstepG T x :=
match x with
| cfgR' k b r => sweep T r &&& (fun r => Some (cfgL' k b r))
| cfgL' k b r =>
  (skip_prefix [1;0;1] r &&& (fun r =>
  Some (cfgL' (2+k) b ([1]*>r)))) ||| (fun _ =>
  (skip_prefix [1;1] r &&& (fun r =>
  Some (cfgR' (2+k) b r))) ||| (fun _ =>
  if (b=?0)%N then
    skip_prefix [0;0] r &&& (fun r =>
    Some (cfgR' 1 (2+k) ([0]*>r)))
  else
    rest T r t1 &&& (fun n =>
    if (n=?0)%N then
      Some (cfgR' (2+k) (b-1) r)
    else
      Some (N.min n b) &&& (fun n =>
      RIncs T n r t1 &&& (fun r =>
      Some (cfgL' (k+n*2) (b-n) r))))
  ))
end.

Lemma mstepG_plus T x x':
  mstepG T x = Some x' ->
  Config_eval x -->+ Config_eval x'.
Proof.
  intros.
  destruct x; cbn[mstepG] in H.
  - des_if H.
    { inverts H.
      des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      cbn[Config_eval].
      rewrite Nnat.N2Nat.inj_add.
      apply LRst_101o_p. }
    clear E.
    des_if H.
    { inverts H.
      des_if' E.
      inverts E.
      apply skip_prefix_spec in E0; subst.
      cbn[Config_eval].
      rewrite Nnat.N2Nat.inj_add.
      apply LRst_11o_p. }
    clear E.
    destruct (N.eqb_spec b 0).
    { subst.
      des_if' H.
      inverts H.
      apply skip_prefix_spec in E; subst.
      cbn[Config_eval].
      applys_eq (LOvo_p (N.to_nat k) s); flia. }
    { des_if' H.
      cbn[if_Some] in H.
      destruct (N.eqb_spec n0 0).
      { subst.
        inverts H.
        cbn[Config_eval].
        applys_eq (LInco_p (N.to_nat k) (N.to_nat (b-1))); flia. }
      { des_if' H.
        inverts H.
        apply RIncs_spec in E0.
        cbn[Config_eval].
        remember (N.min n0 b) as n'.
        assert (Hn: N.to_nat n' = S (N.to_nat n' - 1)) by lia.
        pose proof (LIncso (N.to_nat n') (N.to_nat k) (N.to_nat (b-n'))) as HL.
        rewrite Hn in E0, HL.
        eapply sideRLs_concat_1L_plus.
        1: apply E0.
        applys_eq HL; flia. }
    }
  - des_if' H. inverts H.
    apply sweep_spec in E.
    eapply sideRLs_1 in E.
    apply E.
Qed.

(* "the macro simulator runs forever": at every step some fuel suffices *)
CoInductive runs : Config -> Prop :=
| runs_step T x y : mstepG T x = Some y -> runs y -> runs x.

Definition start := cfgL' 5 5 ([1;0]*>0inf).

(* The reduction: if the macro simulator (timer lemmas, counter arithmetic, and sweeps made only of the
   21 carry lemmas) runs forever from the start, the machine never halts. *)
Theorem nonhalt_of_runs:
  runs start -> ~ halts tm c0.
Proof.
  intros H.
  rewrite (halts_evstep_iff _ _ _ init).
  change (LCo 5 5 {{{ (hL',L) }}} [1;0] *> 0inf) with (Config_eval start).
  apply progress_nonhalt_cond with (P := runs).
  2: exact H.
  intros x Hx.
  inversion Hx as [T x0 y E Hy]; subst.
  exists y. split.
  - apply (mstepG_plus T), E.
  - exact Hy.
Qed.


(* Back to the holdout as listed. tmR is the holdout with states renamed (A,B,C,D,E,F -> A,C,D,E,B,F);
   tm (the one used above) is tmR mirrored. *)
Definition holdout := Eval compute in (TM_from_str "1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA").
Definition tmR := Eval compute in (TM_from_str "1RC0LF_1LE---_1RD1RC_0RE0RD_1LB1LF_0LC1LA").
Definition rename q := match q with A=>A | B=>C | C=>D | D=>E | E=>B | F=>F end.

Lemma correspondence : Perm holdout tmR rename.
Proof. split; intros [] [] * H; cbn in H; inversion H; reflexivity. Qed.

Lemma flip_tmR : flip tmR = tm.
Proof.
  apply FunctionalExtensionality.functional_extensionality.
  intros [[] []]; reflexivity.
Qed.

Theorem holdout_nonhalt_of_runs:
  runs start -> ~ halts holdout c0.
Proof.
  intros H.
  apply (perm_nonhalt holdout tmR rename A _ correspondence).
  apply flip_halts_c0.
  rewrite flip_tmR.
  apply nonhalt_of_runs, H.
Qed.

Print Assumptions holdout_nonhalt_of_runs.
