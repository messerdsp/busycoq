(** Piece rules of 23154 = 1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---.

    These are the rules of the busy-beaver-explorer Lean files for the twin 115779 (lean/Rules.lean,
    lean/InnerRules.lean), restated for 23154's own state names and re-proved here; nothing is imported from Lean.
    115779's table with its states renamed A->B, B->C, C->D, D->E, E->A (F stays) is 23154's table.

    Notation: in [l <* w] the first element of [w] is next to the head; in [w *> r] likewise. A digit d is the
    block [0 1^(3d+2)]; a passed (converted) odd digit 2k+1 is [0 0 (1 0)^(3k+2)]. *)
From BusyCoq Require Import Individual62.
Require Import Lia.
Require Import String.
Open Scope list.

Definition tm := Eval compute in (TM_from_str "1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---").
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

(** * Outer sweep pieces *)

(** The sweep starts at the right end: [0 1 C>0] (blank beyond) becomes [E>0 0 0 1 0]. *)
Lemma tail_left l:
  l <* [1;0] {{C}}> const 0 -->* l {{E}}> [0;0;0;1] *> const 0.
Proof. es. Qed.

(** Moving left over a block of [2n+1] ones: E on its right separator goes to its left separator; the block and
    the right separator become [0 0 (1 0)^n]. *)
Lemma left_odd n l r:
  l <* [1;0] <* [1;1]^^n {{E}}> [0] *> r -->* l {{E}}> [0;0;0] *> [1;0]^^n *> r.
Proof. es. Qed.

(** Moving left over a block of [2n+2] ones: A stops on the left separator; the block becomes [0 1 (0 1)^n 0]. *)
Lemma left_even n l r:
  l <* [0] <* [1;1]^^n <* [1;1] {{E}}> [0] *> r -->* l {{A}}> [0;0;1] *> [0;1]^^n *> [0] *> r.
Proof. es. Qed.

(** The turn at a digit 0. *)
Lemma turn_zero l r:
  l {{A}}> [0;0;1;0] *> r -->* l <* [1;1;1;1] {{B}}> r.
Proof. es. Qed.

(** The turn at a digit [2i+2] ([1^(6i+8)]). *)
Lemma turn_even i l r:
  l {{A}}> [0;0;1;0;1;0;1;0;1] *> [0;1;0;1;0;1]^^i *> [0] *> r -->*
  l <* [1;1;0;1;1;0;1;1;1] <* [1;1;0;1;1;0]^^i <* [1] {{B}}> r.
Proof. es. Qed.

(** Moving right over a passed odd digit [2k+1] ([0 0 (1 0)^(3k+2)]) with [1 1 1] in hand. *)
Lemma right_odd k l r:
  l <* [1;1;1] {{B}}> [0;0;1;0;1;0] *> [1;0;1;0;1;0]^^k *> r -->*
  l <* [1;1;0;1;1;1;1;1] <* [1;1;0;1;1;0]^^k <* [1] {{B}}> r.
Proof. es. Qed.

(** The right end again. *)
Lemma tail_right l:
  l <* [1;1;1] {{B}}> [0;0;1] *> const 0 -->* l <* [1;0;1;1;1;1;1] {{C}}> const 0.
Proof. es. Qed.

(** * Left-end pieces *)

(** Leftmost block [1^3], first digit [2k+1]: the tape grows three cells to the left. *)
Lemma carry3 k r:
  const 0 <* [1;1;1] {{E}}> [0;0;0;1;0;1;0] *> [1;0;1;0;1;0]^^k *> r -->*
  const 0 <* [1;1;0;1;1;0;1;1;0;1;1;1] <* [1;1;0;1;1;0]^^k <* [1] {{B}}> r.
Proof. es. Qed.

(** Leftmost block [1^(6j+9)]: it becomes [1^3] and [2j+3] zeros. *)
Lemma carry9 j r:
  const 0 <* [1;1;1;1;1;1;1;1;1] <* [1;1;1;1;1;1]^^j {{E}}> [0] *> r -->*
  const 0 <* [1;1;0;1;1;0;1;1;0;1;1;0;1;1;1] <* [1;1;0;1;1;0]^^j <* [1] {{B}}> r.
Proof. es. Qed.

(** The other phase of the right end ([0 1^4 C>0]): the last digit 1 becomes [2 0]. *)
Lemma phase2 l:
  l <* [1;1;1;1;0;1;1;1;1;1;0] {{C}}> const 0 -->*
  l <* [1;0;1;1;0;1;1;1;1;1;1;1;1;0] {{C}}> const 0.
Proof. es. Qed.

(** * Pieces of a nested run (inner sweeps) *)

(** Phase X of an inner right end ([0 1 1 A>1 0]): the left pass starts. *)
Lemma x_left l r:
  l <* [1;1;0] {{A}}> [1] *> r -->* l {{E}}> [0;0;0;1] *> r.
Proof. es. Qed.

(** Phase Y ([0 1 1 1 0 F>0 1 0]): the left pass starts. *)
Lemma y_left l r:
  l <* [0;1;1;1;0] {{F}}> [0;1;0] *> r -->* l {{E}}> [0;0;0;1;0;1;1;0] *> r.
Proof. es. Qed.

(** The right pass comes back to an X end and eats one passed digit 1 ([0 0 1 0 1 0]); the end goes to phase Y. *)
Lemma x_right l r:
  l <* [1;1;1] {{B}}> [0;0;1;0;0;0;1;0;1;0] *> r -->* l <* [0;1;1;1;0;1;1;1;1;1] {{F}}> [0;1;0] *> r.
Proof. es. Qed.

(** The right pass comes back to a Y end; the end goes to phase X. *)
Lemma y_right l r:
  l <* [1;1;1] {{B}}> [0;0;1;0;1;1;0] *> r -->* l <* [1;1;0;1;1;1;1;1] {{A}}> [1;0] *> r.
Proof. es. Qed.

(** The start of a nested run: leftmost block [1^(6j+6)], first digit 1. *)
Lemma nest_start j r:
  const 0 <* [1;1;1;1;1;1] <* [1;1;1;1;1;1]^^j {{E}}> [0;0;0;1;0;1;0] *> r -->*
  const 0 <* [1;0;1;1;0;1;1;1] <* [1;0;1;1;0;1]^^j <* [0;1;1] {{F}}> [0;1;0] *> r.
Proof. es. Qed.
