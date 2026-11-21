(** One sweep of the counter of 23154, for every digit list.

    A port of the busy-beaver-explorer file lean/Sweep.lean (for the twin 115779), re-proved in Rocq for 23154's
    state names (115779's B, D, E, A are 23154's C, E, A, B).  A digit [d] is the block [0 1^(3d+2)].  A sweep
    configuration [P l ds] is [l 0 1^(3d1+2) ... 0 1^(3dm+2) 0 1 C>0], blank to the right.  From the right end the
    head walks left over the odd digits, turns at the first even digit, and walks back rebuilding every block three
    cells further right (sweep_zero, sweep_even).  Step counts are not tracked. *)
From BusyCoq Require Import Individual62.
From M23154 Require Import M23154Rules.
Require Import Lia List.
Import ListNotations.
Open Scope list.

(** * Words *)

Definition ones (n : nat) : list Sym := [1]^^n.

Lemma ones_add a b : ones (a + b) = ones a ++ ones b.
Proof. unfold ones. apply lpow_add. Qed.

Lemma ones_S n : ones (S n) = 1 :: ones n.
Proof. reflexivity. Qed.

Lemma ones_odd n : ones (2 * n + 1) = [1;1]^^n ++ [1].
Proof.
  induction n as [|n IH]; [reflexivity|].
  replace (2 * S n + 1) with (S (S (2 * n + 1))) by lia.
  rewrite ones_S, ones_S, IH. reflexivity.
Qed.

Lemma ones_even n : ones (2 * n + 2) = [1;1] ++ [1;1]^^n.
Proof.
  induction n as [|n IH]; [reflexivity|].
  replace (2 * S n + 2) with (S (S (2 * n + 2))) by lia.
  rewrite ones_S, ones_S, IH. reflexivity.
Qed.

Lemma pow_mul3 {A} (w : list A) k : w^^(3 * k) = (w ++ w ++ w)^^k.
Proof.
  induction k as [|k IH]; [reflexivity|].
  replace (3 * S k) with (3 + 3 * k) by lia.
  rewrite lpow_add, IH. cbn. rewrite ?app_nil_r, <- ?app_assoc. reflexivity.
Qed.

Lemma pow_mul2 {A} (w : list A) k : w^^(2 * k) = (w ++ w)^^k.
Proof.
  induction k as [|k IH]; [reflexivity|].
  replace (2 * S k) with (2 + 2 * k) by lia.
  rewrite lpow_add, IH. cbn. rewrite ?app_nil_r, <- ?app_assoc. reflexivity.
Qed.

(** * Digits *)

(** [enc ds l]: the digits [ds] (left to right) written after the side [l]; the last digit is next to the head. *)
Fixpoint enc (ds : list nat) (l : side) : side :=
  match ds with
  | [] => l
  | d :: ds' => enc ds' (ones (3 * d + 2) *> [0] *> l)
  end.

Lemma enc_app xs ys l : enc (xs ++ ys) l = enc ys (enc xs l).
Proof. revert l. induction xs; intros; cbn; auto. Qed.

Lemma enc_snoc xs d l : enc (xs ++ [d]) l = ones (3 * d + 2) *> [0] *> enc xs l.
Proof. rewrite enc_app. reflexivity. Qed.

Lemma enc_zeros xs m l : enc (xs ++ repeat O m) l = [1;1;0]^^m *> enc xs l.
Proof.
  revert xs. induction m as [|m IH]; intros xs.
  - cbn. rewrite app_nil_r. reflexivity.
  - replace (xs ++ repeat O (S m)) with ((xs ++ [O]) ++ repeat O m)
      by (cbn; rewrite <- app_assoc; reflexivity).
    rewrite IH, enc_snoc.
    replace (ones (3 * O + 2) *> [0] *> enc xs l) with ([1;1;0] *> enc xs l) by reflexivity.
    rewrite lpow_shift'. cbn [lpow]. rewrite Str_app_assoc. reflexivity.
Qed.

(** The sweep configuration at the right end (phase P). *)
Definition P (l : side) (ds : list nat) : Q * tape := enc ds l <* [1;0] {{C}}> const 0.

Definition odds (ks : list nat) : list nat := map (fun k => 2 * k + 1) ks.

(** * The left pass *)

(** What the left pass leaves right of the head after passing the odd digits [2k+1], [k] in [ks]. *)
Fixpoint modR (ks : list nat) (r : side) : side :=
  match ks with
  | [] => r
  | k :: ks' => [0;0] *> [1;0]^^(3 * k + 2) *> modR ks' r
  end.

Lemma odd_block k l : ones (3 * (2 * k + 1) + 2) *> [0] *> l = l <* [1;0] <* [1;1]^^(3 * k + 2).
Proof.
  replace (3 * (2 * k + 1) + 2) with (2 * (3 * k + 2) + 1) by lia.
  rewrite ones_odd, Str_app_assoc. reflexivity.
Qed.

Theorem left_pass l ks : forall X r,
  enc (X ++ odds ks) l {{E}}> [0] *> r -->* enc X l {{E}}> [0] *> modR ks r.
Proof.
  induction ks as [|k ks IH]; intros X r.
  - cbn. rewrite app_nil_r. apply evstep_refl.
  - replace (X ++ odds (k :: ks)) with ((X ++ [2 * k + 1]) ++ odds ks)
      by (cbn; rewrite <- app_assoc; reflexivity).
    eapply evstep_trans. { apply IH. }
    rewrite enc_snoc, odd_block.
    apply left_odd.
Qed.

(** * The right pass *)

Lemma pow10_3k2 k r : [1;0]^^(3 * k + 2) *> r = [1;0;1;0] *> [1;0;1;0;1;0]^^k *> r.
Proof.
  replace (3 * k + 2) with (2 + 3 * k) by lia.
  rewrite lpow_add, pow_mul3, Str_app_assoc. reflexivity.
Qed.

(** [1] then [k] copies of [1;1;0;1;1;0] is [1;1;1] then [k] copies of [0;1;1;0;1;1], up to the last [1;1]. *)
Lemma rot3 k l :
  l <* [1;1] <* [1;1;0;1;1;0]^^k <* [1] = l <* [0;1;1;0;1;1]^^k <* [1;1;1].
Proof.
  induction k as [|k IH]; [reflexivity|].
  assert (H : [1;1;0;1;1;0]^^k *> [1;1] *> l = [1;1] *> [0;1;1;0;1;1]^^k *> l).
  { cbn in IH. injection IH. auto. }
  cbn [lpow]. rewrite !Str_app_assoc. rewrite H. reflexivity.
Qed.

(** What the right pass writes for the odd digits [2k+1], [k] in [ks], behind the [1 1 1] it carries. *)
Fixpoint rpass (ks : list nat) (z : side) : side :=
  match ks with
  | [] => z
  | k :: ks' => rpass ks' ([0;1;1;0;1;1]^^k *> [0;1;1;1;1;1] *> z)
  end.

Lemma right_odd' k z r :
  z <* [1;1;1] {{B}}> [0;0] *> [1;0]^^(3 * k + 2) *> r -->*
  z <* [0;1;1;1;1;1] <* [0;1;1;0;1;1]^^k <* [1;1;1] {{B}}> r.
Proof.
  rewrite pow10_3k2.
  eapply evstep_trans. { apply (right_odd k z r). }
  apply evstep_refl'.
  change ([1;1;0;1;1;1;1;1] *> z) with ([1;1] *> [0;1;1;1;1;1] *> z).
  rewrite rot3. reflexivity.
Qed.

Theorem right_pass ks : forall z r,
  z <* [1;1;1] {{B}}> modR ks r -->* rpass ks z <* [1;1;1] {{B}}> r.
Proof.
  induction ks as [|k ks IH]; intros z r.
  - apply evstep_refl.
  - cbn [modR rpass].
    eapply evstep_trans. { apply right_odd'. }
    apply IH.
Qed.

(** * A whole sweep, for any side left of the stop digit *)

(** What the left pass leaves at the right end. *)
Definition T0 : side := [0;0;1] *> const 0.

(** The final form of a sweep: [1 1 1] in hand at the right end becomes [1^5 0 1 C>0]. *)
Definition F (z : side) : Q * tape := z <* [1;0;1;1;1;1;1] {{C}}> const 0.

Theorem sweep_zero_gen lc ks :
  enc ([O] ++ odds ks) lc <* [1;0] {{C}}> const 0 -->* F (rpass ks ([1] *> lc)).
Proof.
  eapply evstep_trans. { apply tail_left. }
  eapply evstep_trans. { apply (left_pass lc ks [O] T0). }
  change (enc [O] lc) with (lc <* [0] <* [1;1]^^0 <* [1;1]).
  eapply evstep_trans. { apply left_even. }
  eapply evstep_trans. { apply turn_zero. }
  change (lc <* [1;1;1;1]) with (([1] *> lc) <* [1;1;1]).
  eapply evstep_trans. { apply right_pass. }
  apply tail_right.
Qed.

Lemma pow01_3i3 i r : [0;1]^^(3 * i + 3) *> [0] *> r = [0;1;0;1;0;1] *> [0;1;0;1;0;1]^^i *> [0] *> r.
Proof.
  replace (3 * i + 3) with (3 * (S i)) by lia.
  rewrite pow_mul3. reflexivity.
Qed.

Theorem sweep_even_gen lc i ks :
  enc ([2 * i + 2] ++ odds ks) lc <* [1;0] {{C}}> const 0 -->*
  F (rpass ks ([0;1;1;0;1;1]^^i *> [0;1;1;0;1;1;1] *> lc)).
Proof.
  eapply evstep_trans. { apply tail_left. }
  eapply evstep_trans. { apply (left_pass lc ks [2 * i + 2] T0). }
  replace (enc [2 * i + 2] lc) with (lc <* [0] <* [1;1]^^(3 * i + 3) <* [1;1]).
  2:{ cbn [enc]. replace (3 * (2 * i + 2) + 2) with (2 * (3 * i + 3) + 2) by lia.
      rewrite ones_even, Str_app_assoc. reflexivity. }
  eapply evstep_trans. { apply left_even. }
  rewrite pow01_3i3.
  eapply evstep_trans. { apply turn_even. }
  change ([1;1;0;1;1;0;1;1;1] *> lc) with ([1;1] *> [0;1;1;0;1;1;1] *> lc).
  rewrite rot3.
  eapply evstep_trans. { apply right_pass. }
  apply tail_right.
Qed.

(** * Back to digits *)

(** The digits a sweep writes: [E] finished, an open block that will become the digit [c+1], then for each odd
    digit [2k+1] passed: the open block is closed, [2k] zeros follow and a new block is opened. *)
Fixpoint stepD (E : list nat) (c : nat) (ks : list nat) : list nat :=
  match ks with
  | [] => E ++ [c + 1]
  | k :: ks' => stepD (E ++ [c + 1] ++ repeat O (2 * k)) O ks'
  end.

Lemma rot0 k x : [0;1;1;0;1;1]^^k *> [0] *> x = [0] *> [1;1;0;1;1;0]^^k *> x.
Proof.
  induction k as [|k IH]; [reflexivity|].
  cbn [lpow]. rewrite !Str_app_assoc, IH. reflexivity.
Qed.

Lemma ones_app a b x : ones (a + b) *> x = ones a *> ones b *> x.
Proof. rewrite ones_add, Str_app_assoc. reflexivity. Qed.

Lemma pow110_2k k x : [1;1;0]^^(2 * k) *> x = [1;1;0;1;1;0]^^k *> x.
Proof. rewrite pow_mul2. reflexivity. Qed.

(** Closing an open block of [m] ones behind the carried [1 1 1]: it gets [5] more ones. *)
Lemma close_block k m w :
  [0;1;1;0;1;1]^^k *> [0;1;1;1;1;1] *> ones m *> w = [0] *> [1;1;0]^^(2 * k) *> ones (m + 5) *> w.
Proof.
  rewrite pow110_2k, <- rot0.
  replace (m + 5) with (5 + m) by lia. rewrite ones_app. reflexivity.
Qed.

Theorem F_rpass l ks : forall E c,
  F (rpass ks (ones (3 * c) *> [0] *> enc E l)) = P l (stepD E c ks).
Proof.
  induction ks as [|k ks IH]; intros E c.
  - cbn [rpass stepD]. unfold F, P. rewrite enc_snoc.
    replace (3 * (c + 1) + 2) with (5 + 3 * c) by lia. rewrite ones_app. reflexivity.
  - cbn [rpass stepD]. rewrite close_block, <- IH. f_equal.
    rewrite app_assoc, enc_zeros, enc_snoc.
    replace (3 * c + 5) with (3 * (c + 1) + 2) by lia. reflexivity.
Qed.

(** The sweep, stopping at a digit 0: [a 0 (2k1+1) ... (2kn+1)] becomes [(a+2) 0^(2k1) 1 ... 0^(2kn) 1]. *)
Theorem sweep_zero l Y a ks :
  P l (Y ++ [a; O] ++ odds ks) -->* P l (stepD Y (a + 1) ks).
Proof.
  rewrite <- F_rpass.
  unfold P. replace (Y ++ [a; O] ++ odds ks) with ((Y ++ [a]) ++ [O] ++ odds ks)
    by (rewrite <- app_assoc; reflexivity).
  rewrite enc_app.
  replace (ones (3 * (a + 1)) *> [0] *> enc Y l) with ([1] *> enc (Y ++ [a]) l).
  - apply sweep_zero_gen.
  - rewrite enc_snoc. replace (3 * (a + 1)) with (S (3 * a + 2)) by lia. reflexivity.
Qed.

Lemma pow110_2k1 k x : [1;1;0]^^(2 * k + 1) *> x = [1;1;0;1;1;0]^^k *> [1;1;0] *> x.
Proof. rewrite lpow_add, Str_app_assoc, pow110_2k. reflexivity. Qed.

(** The sweep, stopping at a digit [2i+2]: [a (2i+2) (2k1+1) ...] becomes
    [(a+1) 0^(2i+1) 1 0^(2k1) 1 ...]. *)
Theorem sweep_even l Y a i ks :
  P l (Y ++ [a; 2 * i + 2] ++ odds ks) -->* P l (stepD (Y ++ [a + 1] ++ repeat O (2 * i + 1)) O ks).
Proof.
  rewrite <- F_rpass.
  unfold P. replace (Y ++ [a; 2 * i + 2] ++ odds ks) with ((Y ++ [a]) ++ [2 * i + 2] ++ odds ks)
    by (rewrite <- app_assoc; reflexivity).
  rewrite enc_app.
  replace (ones (3 * O) *> [0] *> enc (Y ++ [a + 1] ++ repeat O (2 * i + 1)) l)
    with ([0;1;1;0;1;1]^^i *> [0;1;1;0;1;1;1] *> enc (Y ++ [a]) l).
  - apply sweep_even_gen.
  - rewrite app_assoc, enc_zeros, enc_snoc, enc_snoc, pow110_2k1.
    change ([0;1;1;0;1;1;1] *> ones (3 * a + 2) *> [0] *> enc Y l)
      with ([0] *> [1;1;0] *> ones 3 *> ones (3 * a + 2) *> [0] *> enc Y l).
    rewrite rot0, <- ones_app. replace (3 + (3 * a + 2)) with (3 * (a + 1) + 2) by lia. reflexivity.
Qed.

(** * At the left end: a block [1^r] that is not a digit *)

Definition raw (r : nat) : side := ones r *> const 0.

Definition rawD (ks : list nat) : list nat :=
  match ks with
  | [] => []
  | k :: ks' => stepD (repeat O (2 * k)) O ks'
  end.

(** The first digit is 0 and every digit after it is odd: the left block grows by 6. *)
Theorem raw_zero r ks : P (raw r) ([O] ++ odds ks) -->* P (raw (r + 6)) (rawD ks).
Proof.
  eapply evstep_trans. { apply sweep_zero_gen. }
  destruct ks as [|k ks].
  - apply evstep_refl'. unfold F, P, raw. cbn [rpass enc rawD].
    replace (r + 6) with (5 + S r) by lia. rewrite ones_app. reflexivity.
  - cbn [rpass rawD]. apply evstep_refl'.
    change ([1] *> raw r) with (ones (S r) *> const 0). rewrite close_block.
    rewrite <- (F_rpass (raw (r + 6)) ks (repeat O (2 * k)) O).
    f_equal. change (repeat O (2 * k)) with ([] ++ repeat O (2 * k)). rewrite enc_zeros.
    unfold raw. replace (S r + 5) with (r + 6) by lia. reflexivity.
Qed.

(** The first digit is [2i+2] and every digit after it is odd: the left block grows by 3. *)
Theorem raw_even r i ks :
  P (raw r) ([2 * i + 2] ++ odds ks) -->* P (raw (r + 3)) (stepD (repeat O (2 * i + 1)) O ks).
Proof.
  eapply evstep_trans. { apply sweep_even_gen. }
  rewrite <- F_rpass. apply evstep_refl'. f_equal.
  change (repeat O (2 * i + 1)) with ([] ++ repeat O (2 * i + 1)). rewrite enc_zeros, pow110_2k1.
  change ([0;1;1;0;1;1;1] *> raw r) with ([0] *> [1;1;0] *> ones 3 *> ones r *> const 0).
  rewrite rot0, <- ones_app. unfold raw. replace (3 + r) with (r + 3) by lia. reflexivity.
Qed.
