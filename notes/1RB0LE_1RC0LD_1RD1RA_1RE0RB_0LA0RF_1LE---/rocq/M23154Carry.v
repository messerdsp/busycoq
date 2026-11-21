(** Sweeps that reach the left end, and the other phase of the right end (port of the explorer's
    lean/Carry.lean for the twin 115779, re-proved here for 23154's state names).

    * [carry3_sweep]: leftmost block [1^3], every digit odd: [1^3] then [2k+2] zeros, the rest as in a sweep;
    * [carry9_sweep]: leftmost block [1^(6j+9)], every digit odd: [1^3] then [2j+3] zeros;
    * [phase2_sweep]: the other phase [Q] of the right end ([0 1^4 C>0]) with last digit 1 becomes [P] with the
      last digits [2 0].
    The case of an even leftmost block (a nested run) is elsewhere. *)
From BusyCoq Require Import Individual62.
From M23154 Require Import M23154Rules M23154Sweep.
Require Import Lia List.
Import ListNotations.
Open Scope list.

Lemma ones_six j m x : ones (6 * j + m) *> x = [1;1;1;1;1;1]^^j *> ones m *> x.
Proof.
  induction j as [|j IH]; [reflexivity|].
  replace (6 * S j + m) with (6 + (6 * j + m)) by lia.
  rewrite ones_app, IH. reflexivity.
Qed.

(** The tail of the rebuilt left end, as [F_rpass] wants it. *)
Lemma left_zeros j x : [0;1;1;0;1;1]^^j *> [0] *> [1;1;0] *> x = [0] *> [1;1;0]^^(2 * j + 1) *> x.
Proof. rewrite rot0, pow110_2k1. reflexivity. Qed.

Theorem carry3_sweep k ks :
  P (raw 3) (odds (k :: ks)) -->* P (raw 3) (stepD (repeat O (2 * k + 2)) O ks).
Proof.
  rewrite <- F_rpass.
  replace (ones (3 * O) *> [0] *> enc (repeat O (2 * k + 2)) (raw 3))
    with ([0;1;1;0;1;1]^^k *> [0;1;1;0;1;1;0;1;1;1] *> const 0).
  2:{ change (repeat O (2 * k + 2)) with ([] ++ repeat O (2 * k + 2)). rewrite enc_zeros.
      change ([0;1;1;0;1;1;0;1;1;1] *> const 0) with ([0] *> [1;1;0] *> [1;1;0;1;1;1] *> const 0).
      rewrite left_zeros.
      replace (2 * k + 2) with (S (2 * k + 1)) by lia. cbn [lpow]. rewrite Str_app_assoc, <- lpow_shift'.
      reflexivity. }
  unfold P.
  eapply evstep_trans. { apply tail_left. }
  eapply evstep_trans. { apply (left_pass (raw 3) (k :: ks) [] T0). }
  cbn [enc modR]. rewrite pow10_3k2.
  eapply evstep_trans. { apply carry3. }
  change ([1;1;0;1;1;0;1;1;0;1;1;1] *> const 0) with ([1;1] *> [0;1;1;0;1;1;0;1;1;1] *> const 0).
  rewrite rot3.
  eapply evstep_trans. { apply right_pass. }
  apply tail_right.
Qed.

Theorem carry9_sweep j ks :
  P (raw (6 * j + 9)) (odds ks) -->* P (raw 3) (stepD (repeat O (2 * j + 3)) O ks).
Proof.
  rewrite <- F_rpass.
  replace (ones (3 * O) *> [0] *> enc (repeat O (2 * j + 3)) (raw 3))
    with ([0;1;1;0;1;1]^^j *> [0;1;1;0;1;1;0;1;1;0;1;1;1] *> const 0).
  2:{ change (repeat O (2 * j + 3)) with ([] ++ repeat O (2 * j + 3)). rewrite enc_zeros.
      change ([0;1;1;0;1;1;0;1;1;0;1;1;1] *> const 0)
        with ([0] *> [1;1;0] *> [1;1;0;1;1;0;1;1;1] *> const 0).
      rewrite left_zeros.
      replace (2 * j + 3) with (S (S (2 * j + 1))) by lia. cbn [lpow]. rewrite !Str_app_assoc, <- !lpow_shift'.
      reflexivity. }
  unfold P.
  eapply evstep_trans. { apply tail_left. }
  eapply evstep_trans. { apply (left_pass (raw (6 * j + 9)) ks [] T0). }
  cbn [enc]. unfold raw. rewrite ones_six.
  eapply evstep_trans. { apply carry9. }
  change ([1;1;0;1;1;0;1;1;0;1;1;0;1;1;1] *> const 0)
    with ([1;1] *> [0;1;1;0;1;1;0;1;1;0;1;1;1] *> const 0).
  rewrite rot3.
  eapply evstep_trans. { apply right_pass. }
  apply tail_right.
Qed.

(** The other phase of the right end: [l 0 1^(3d1+2) ... 0 1^(3dm+2) 0 1^4 C>0]. *)
Definition Q (l : side) (ds : list nat) : Q * tape := enc ds l <* [1;1;1;1;0] {{C}}> const 0.

Theorem phase2_sweep l (ds : list nat) : Q l (ds ++ [1%nat]) -->* P l (ds ++ [2%nat; O]).
Proof.
  unfold Q, P.
  replace (ds ++ [2%nat; O]) with ((ds ++ [2%nat]) ++ [O]) by (rewrite <- app_assoc; reflexivity).
  rewrite !enc_snoc.
  apply phase2.
Qed.
