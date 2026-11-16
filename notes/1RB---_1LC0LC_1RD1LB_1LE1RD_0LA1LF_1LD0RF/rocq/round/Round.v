(** A whole round of the post-overflow chain, by induction over its units.

    A round start is [RS v = const 0 {{C}}> [0;1;1;1;1;1;1;1;1] *> Wd *> v].  The tape after the prefix is a list
    of units in cut form followed by the rest of the tape (the end region, the band, the frozen cascade):
    [Wd *> vt us E], where [vt] writes each unit [(t, p, m)] as [Wd^^(S (S m)) *> seg t p] and puts the first
    word [Wd] of the next unit (or of [E]) after it.  One round steps the counter [step us]: the first unit steps;
    a unit in phase 3 carries into the next one.  When every unit carries, the trip goes on into the end, which
    enters as a hypothesis ([Trip (Wd *> E) E']). *)
From BusyCoq Require Import Individual62.
From M130 Require Import M130Rules.
From M130.round Require Import Trips.
Require Import Lia List.
Import ListNotations.
Open Scope list.

Definition unit : Type := utype * nat * nat.

Fixpoint vt (us : list unit) (E : side) : side :=
  match us with
  | [] => E
  | (t, p, m) :: us' => Wd^^(S (S m)) *> seg t p *> Wd *> vt us' E
  end.

(** Does a trip through [us] carry out of the last unit? *)
Fixpoint carries (us : list unit) : bool :=
  match us with
  | [] => true
  | (_, p, _) :: us' => match p with S (S (S _)) => carries us' | _ => false end
  end.

Fixpoint step (us : list unit) : list unit :=
  match us with
  | [] => []
  | (t, p, m) :: us' =>
      match p with
      | S (S (S _)) => (t, O, S m) :: step us'
      | _ => (t, nxt p, grow p m) :: us'
      end
  end.

Lemma trip_b0 t m r:
  Trip (Wd *> Wd^^(S (S m)) *> seg t O *> r) (Wd^^(S (S m)) *> seg t (S (S O)) *> r).
Proof.
  destruct t; [exact (tripU_U1_0 m r) | exact (tripU_U2_0 m r) | exact (tripU_U3_0 m r)
             | exact (tripU_U4_0 m r) | exact (tripU_K_0 m r) | exact (tripU_D_0 m r)].
Qed.

Lemma trip_b1 t m r:
  Trip (Wd *> Wd^^(S (S m)) *> seg t (S O) *> r) (Wd^^(S (S m)) *> seg t (S (S (S O))) *> r).
Proof.
  destruct t; [exact (tripU_U1_1 m r) | exact (tripU_U2_1 m r) | exact (tripU_U3_1 m r)
             | exact (tripU_U4_1 m r) | exact (tripU_K_1 m r) | exact (tripU_D_1 m r)].
Qed.

Lemma trip_b2 t m r:
  Trip (Wd *> Wd^^(S (S m)) *> seg t (S (S O)) *> r) (Wd^^(S (S (S m))) *> seg t (S O) *> r).
Proof.
  destruct t; [exact (tripU_U1_2 m r) | exact (tripU_U2_2 m r) | exact (tripU_U3_2 m r)
             | exact (tripU_U4_2 m r) | exact (tripU_K_2 m r) | exact (tripU_D_2 m r)].
Qed.

Lemma trip_c t m u v:
  Trip u v ->
  Trip (Wd *> Wd^^(S (S m)) *> seg t (S (S (S O))) *> u) (Wd^^(S (S (S m))) *> seg t O *> Wd *> v).
Proof.
  destruct t; [exact (tripU_U1_3 m u v) | exact (tripU_U2_3 m u v) | exact (tripU_U3_3 m u v)
             | exact (tripU_U4_3 m u v) | exact (tripU_K_3 m u v) | exact (tripU_D_3 m u v)].
Qed.

(** The trip through the whole chain, by induction over the units. *)
Theorem chain_trip us E E':
  (carries us = true -> Trip (Wd *> E) E') ->
  Trip (Wd *> vt us E) (vt (step us) (if carries us then E' else E)).
Proof.
  induction us as [|[[t p] m] us IH]; intros H.
  - exact (H eq_refl).
  - destruct p as [|[|[|p]]]; cbn [vt step carries nxt grow].
    + exact (trip_b0 t m (Wd *> vt us E)).
    + exact (trip_b1 t m (Wd *> vt us E)).
    + exact (trip_b2 t m (Wd *> vt us E)).
    + apply (trip_c t m). exact (IH H).
Qed.

(** The left end: the prefix [0;1;1;1;1;1;1;1;1] in front of the first unit. *)
Definition RS (v : side) : Q * tape := const 0 {{C}}> [0;1;1;1;1;1;1;1;1] *> Wd *> v.

Lemma prefix_in u:
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1] *> u -->+ const 0 <* [1;1;1;1;1;1;1] <* [1;1] {{D}}> u.
Proof. start_progress. Qed.

Lemma prefix_out_r r:
  const 0 <* [1;1;1;1;1;1;1] <* [0] {{C}}> [1] *> r -->*
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1] *> [1] *> r.
Proof. es. Qed.

Lemma prefix_out v:
  const 0 <* [1;1;1;1;1;1;1] <* [0] {{C}}> [1;0;1] *> v -->* RS v.
Proof. unfold RS, Wd. follow prefix_out_r. finish. Qed.

(** One round, round start to round start. *)
Theorem round us E E':
  (carries us = true -> Trip (Wd *> E) E') ->
  RS (vt us E) -->+ RS (vt (step us) (if carries us then E' else E)).
Proof.
  intros H. unfold RS at 1.
  eapply progress_evstep_trans. { apply prefix_in. }
  eapply evstep_trans. { apply (chain_trip us E E' H). }
  apply prefix_out.
Qed.
