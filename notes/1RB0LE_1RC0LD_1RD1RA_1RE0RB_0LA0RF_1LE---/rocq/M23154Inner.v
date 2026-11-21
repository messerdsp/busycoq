(** Inside a nested run: the same counter with a moving right end (port of the explorer's lean/Inner.lean for the
    twin 115779, re-proved here for 23154's state names).

    Phases of the inner right end, with [W] the passed region to its right:
    * [X l ds W]: [l [ds] 0 1 1 A>1 0 W];
    * [Yc l ds W]: [l [ds] 0 1 1 1 0 F>0 1 0 W].
    An inner sweep changes the digits by the outer rule, the phase alternates, and a sweep from X eats one passed
    digit 1 ([tok], [0 0 1 0 1 0]).  [nest_sweep] is the start of a nested run.  Not covered here: inner sweeps
    that reach the left end with an empty or other right context, passed digits other than 1, region ends. *)
From BusyCoq Require Import Individual62.
From M23154 Require Import M23154Rules M23154Sweep M23154Carry.
Require Import Lia List.
Import ListNotations.
Open Scope list.

Definition tok (w : side) : side := [0;0;1;0;1;0] *> w.

Definition X (l : side) (ds : list nat) (w : side) : BB62.Q * tape := enc ds l <* [1;1;0] {{A}}> [1;0] *> w.
Definition Yc (l : side) (ds : list nat) (w : side) : BB62.Q * tape := enc ds l <* [0;1;1;1;0] {{F}}> [0;1;0] *> w.

(** The core of a sweep, for any tape [t] right of the left pass. *)
Theorem core_zero lc ks t :
  enc ([O] ++ odds ks) lc {{E}}> [0] *> t -->* rpass ks ([1] *> lc) <* [1;1;1] {{B}}> t.
Proof.
  eapply evstep_trans. { apply (left_pass lc ks [O] t). }
  change (enc [O] lc) with (lc <* [0] <* [1;1]^^0 <* [1;1]).
  eapply evstep_trans. { apply left_even. }
  eapply evstep_trans. { apply turn_zero. }
  change (lc <* [1;1;1;1]) with (([1] *> lc) <* [1;1;1]).
  apply right_pass.
Qed.

Theorem core_even lc i ks t :
  enc ([2 * i + 2] ++ odds ks) lc {{E}}> [0] *> t -->*
  rpass ks ([0;1;1;0;1;1]^^i *> [0;1;1;0;1;1;1] *> lc) <* [1;1;1] {{B}}> t.
Proof.
  eapply evstep_trans. { apply (left_pass lc ks [2 * i + 2] t). }
  replace (enc [2 * i + 2] lc) with (lc <* [0] <* [1;1]^^(3 * i + 3) <* [1;1]).
  2:{ cbn [enc]. replace (3 * (2 * i + 2) + 2) with (2 * (3 * i + 3) + 2) by lia.
      rewrite ones_even, Str_app_assoc. reflexivity. }
  eapply evstep_trans. { apply left_even. }
  rewrite pow01_3i3.
  eapply evstep_trans. { apply turn_even. }
  change ([1;1;0;1;1;0;1;1;1] *> lc) with ([1;1] *> [0;1;1;0;1;1;1] *> lc).
  rewrite rot3.
  apply right_pass.
Qed.

(** Closing the right pass: the carried [1 1 1] and two more ones finish the open block. *)
Theorem close_rpass l ks : forall E c,
  [1;1;1;1;1] *> rpass ks (ones (3 * c) *> [0] *> enc E l) = enc (stepD E c ks) l.
Proof.
  induction ks as [|k ks IH]; intros E c.
  - cbn [rpass stepD]. rewrite enc_snoc.
    replace (3 * (c + 1) + 2) with (5 + 3 * c) by lia. rewrite ones_app. reflexivity.
  - cbn [rpass stepD]. rewrite close_block, <- IH. f_equal. f_equal.
    rewrite app_assoc, enc_zeros, enc_snoc.
    replace (3 * c + 5) with (3 * (c + 1) + 2) by lia. reflexivity.
Qed.

Lemma open_zero l Y a : [1] *> enc (Y ++ [a]) l = ones (3 * (a + 1)) *> [0] *> enc Y l.
Proof. rewrite enc_snoc. replace (3 * (a + 1)) with (S (3 * a + 2)) by lia. reflexivity. Qed.

Lemma open_even l Y a i :
  [0;1;1;0;1;1]^^i *> [0;1;1;0;1;1;1] *> enc (Y ++ [a]) l =
  ones (3 * O) *> [0] *> enc (Y ++ [a + 1] ++ repeat O (2 * i + 1)) l.
Proof.
  rewrite app_assoc, enc_zeros, enc_snoc, enc_snoc, pow110_2k1.
  change ([0;1;1;0;1;1;1] *> ones (3 * a + 2) *> [0] *> enc Y l)
    with ([0] *> [1;1;0] *> ones 3 *> ones (3 * a + 2) *> [0] *> enc Y l).
  rewrite rot0, <- ones_app. replace (3 + (3 * a + 2)) with (3 * (a + 1) + 2) by lia. reflexivity.
Qed.

Lemma split_last l Y a b ks : enc (Y ++ [a; b] ++ odds ks) l = enc ([b] ++ odds ks) (enc (Y ++ [a]) l).
Proof. rewrite <- enc_app. f_equal. rewrite <- app_assoc. reflexivity. Qed.

(** An inner sweep from phase X stopping at a digit 0: digits as in [sweep_zero], one passed digit 1 eaten,
    the end goes to phase Y. *)
Theorem inner_X_zero l Y a ks w :
  X l (Y ++ [a; O] ++ odds ks) (tok w) -->* Yc l (stepD Y (a + 1) ks) w.
Proof.
  unfold X, Yc. rewrite split_last.
  eapply evstep_trans. { apply x_left. }
  eapply evstep_trans. { apply (core_zero _ ks ([0;0;1;0] *> tok w)). }
  eapply evstep_trans. { apply x_right. }
  rewrite open_zero.
  change ([0;1;1;1;0;1;1;1;1;1] *> ?z) with ([0;1;1;1;0] *> [1;1;1;1;1] *> z).
  rewrite close_rpass. apply evstep_refl.
Qed.

Theorem inner_X_even l Y a i ks w :
  X l (Y ++ [a; 2 * i + 2] ++ odds ks) (tok w) -->*
  Yc l (stepD (Y ++ [a + 1] ++ repeat O (2 * i + 1)) O ks) w.
Proof.
  unfold X, Yc. rewrite split_last.
  eapply evstep_trans. { apply x_left. }
  eapply evstep_trans. { apply (core_even _ i ks ([0;0;1;0] *> tok w)). }
  eapply evstep_trans. { apply x_right. }
  rewrite open_even.
  change ([0;1;1;1;0;1;1;1;1;1] *> ?z) with ([0;1;1;1;0] *> [1;1;1;1;1] *> z).
  rewrite close_rpass. apply evstep_refl.
Qed.

(** An inner sweep from phase Y: back to phase X, nothing eaten. *)
Theorem inner_Y_zero l Y a ks w :
  Yc l (Y ++ [a; O] ++ odds ks) w -->* X l (stepD Y (a + 1) ks) w.
Proof.
  unfold X, Yc. rewrite split_last.
  eapply evstep_trans. { apply y_left. }
  eapply evstep_trans. { apply (core_zero _ ks ([0;0;1;0;1;1;0] *> w)). }
  eapply evstep_trans. { apply y_right. }
  rewrite open_zero.
  change ([1;1;0;1;1;1;1;1] *> ?z) with ([1;1;0] *> [1;1;1;1;1] *> z).
  rewrite close_rpass. apply evstep_refl.
Qed.

Theorem inner_Y_even l Y a i ks w :
  Yc l (Y ++ [a; 2 * i + 2] ++ odds ks) w -->*
  X l (stepD (Y ++ [a + 1] ++ repeat O (2 * i + 1)) O ks) w.
Proof.
  unfold X, Yc. rewrite split_last.
  eapply evstep_trans. { apply y_left. }
  eapply evstep_trans. { apply (core_even _ i ks ([0;0;1;0;1;1;0] *> w)). }
  eapply evstep_trans. { apply y_right. }
  rewrite open_even.
  change ([1;1;0;1;1;1;1;1] *> ?z) with ([1;1;0] *> [1;1;1;1;1] *> z).
  rewrite close_rpass. apply evstep_refl.
Qed.

(** The start of a nested run: every digit odd, the first one 1, the leftmost block [1^(6j+6)].  The sweep does
    not come back to the right end: the leftmost block becomes [1^3] and [2j+1] digits 0, the inner end is in
    phase Y, and right of it lies the region the left pass went over. *)
Theorem nest_sweep j ks :
  P (raw (6 * j + 6)) (odds (O :: ks)) -->* Yc (raw 3) (repeat O (2 * j + 1)) (modR ks T0).
Proof.
  unfold P, Yc.
  eapply evstep_trans. { apply tail_left. }
  eapply evstep_trans. { apply (left_pass (raw (6 * j + 6)) (O :: ks) [] T0). }
  cbn [enc modR]. unfold raw. rewrite ones_six.
  eapply evstep_trans. { apply nest_start. }
  apply evstep_refl'.
  change (repeat O (2 * j + 1)) with ([] ++ repeat O (2 * j + 1)). rewrite enc_zeros, pow110_2k1.
  cbn [enc].
  assert (H : forall x, [1;0;1;1;0;1]^^j *> [1;0] *> x = [1;0] *> [1;1;0;1;1;0]^^j *> x).
  { clear. induction j as [|j IH]; intros x; [reflexivity|].
    cbn [lpow]. rewrite !Str_app_assoc, IH. reflexivity. }
  change ([1;0;1;1;0;1;1;1] *> const 0) with ([1;0] *> [1;1;0;1;1;1] *> const 0).
  rewrite H. reflexivity.
Qed.
