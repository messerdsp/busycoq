(** Block rules of 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF (the Lean rules of the busy-beaver-explorer notes,
    restated in busycoq). *)
From BusyCoq Require Import Individual62.
Require Import Lia.
Require Import String.
Open Scope list.

Definition tm := Eval compute in (TM_from_str "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF").
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

(** D moves right over 1s; F moves right over 1s erasing them. *)
Lemma D_R l r n: l {{D}}> [1]^^n *> r -->* l <* [1]^^n {{D}}> r.
Proof. shift_rule. execute. Qed.

Lemma F_R l r n: l {{F}}> [1]^^n *> r -->* l <* [0]^^n {{F}}> r.
Proof. shift_rule. execute. Qed.

(** The block rules (names as in the Lean file); halt4 ends with A on a 1, which halts. *)
Lemma r_step a b l r:
  l <* [1] {{D}}> [1] *> [1]^^(a+2) *> [0] *> [1]^^(b+5) *> [0] *> r -->*
  l <* [1]^^(a+2) <* [0]^^(b+3) <* [1] {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_step_3 a l r:
  l <* [1] {{D}}> [1] *> [1]^^(a+2) *> [0] *> [1]^^3 *> [0] *> r -->*
  l <* [1]^^(a+2) <* [0] <* [1] {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_step_4 a l r:
  l <* [1] {{D}}> [1] *> [1]^^(a+2) *> [0] *> [1]^^4 *> [0] *> r -->*
  l <* [1]^^(a+2) <* [0] <* [0] <* [1] {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_step1 b l r:
  l <* [1] {{D}}> [1] *> [1] *> [0] *> [1]^^(b+5) *> [0] *> r -->*
  l <* [1] <* [0]^^(b+3) <* [1] {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_step1_3  l r:
  l <* [1] {{D}}> [1] *> [1] *> [0] *> [1]^^3 *> [0] *> r -->*
  l <* [1] <* [0] <* [1] {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_merge a l r:
  l <* [1] {{D}}> [1] *> [1]^^(a+2) *> [0] *> [1] *> [1] *> [0] *> r -->*
  l <* [1]^^(a+3) {{D}}> [1] *> [1]^^4 *> r.
Proof. es. Qed.

Lemma r_bounce a l r:
  l <* [1] {{D}}> [1] *> [1]^^(a+3) *> [0] *> [1] *> [0] *> r -->*
  l <* [1]^^(a+2) {{C}}> [1] *> [1]^^5 *> r.
Proof. es. Qed.

Lemma r_bounce2  l r:
  l <* [1] {{D}}> [1] *> [1] *> [1] *> [0] *> [1] *> [0] *> r -->*
  l <* [1] {{C}}> [1] *> [1]^^5 *> r.
Proof. es. Qed.

Lemma r_bounce1  l r:
  l <* [1] {{D}}> [1] *> [1] *> [0] *> [1] *> [0] *> r -->*
  l {{C}}> [1] *> [1]^^5 *> r.
Proof. es. Qed.

Lemma l_sweep n l r:
  l <* [1;1]^^n {{C}}> [1] *> r -->*
  l <{{B}} [1;0]^^n *> [1] *> r.
Proof. es. Qed.

Lemma l_gap1  l r:
  l <* [1] <* [0] {{C}}> [1] *> r -->*
  l {{C}}> [1] *> [1] *> [1] *> r.
Proof. es. Qed.

Lemma l_turn  l r:
  l <* [0] <* [0] {{C}}> [1] *> r -->*
  l <* [1] {{D}}> [1] *> [1] *> r.
Proof. es. Qed.

(** In [l <* w] the first element of [w] is next to the head: [[1;1;1;1;0;1]] is the wall word 101111 read
    left to right. *)
Lemma wall_l n l r:
  l <* [1;1;1;1;0;1]^^n {{C}}> [1] *> r -->*
  l <{{B}} [1;1;1;0;1;0]^^n *> [1] *> r.
Proof. es. Qed.

Lemma halt4  l r:
  l <* [1] <* [0] <* [0] <* [0] <* [0] {{B}}> [1] *> r -->*
  l {{A}}> [1] *> [0] *> [1] *> [1] *> [1] *> [1] *> r.
Proof. es. Qed.

Lemma b_turn7  l r:
  l <* [0]^^7 {{B}}> [1] *> r -->*
  l <* [1] {{D}}> [1] *> [1]^^6 *> r.
Proof. es. Qed.

(** The pass to the right over a wall. Seen at a round start the wall is (110101)^n; during the pass the head D
    sits on the 0 after five 0s, and each 22 steps one wall word is rewritten as 011111 (as the lists are
    written next to the head: [1;1;1;1;1;0]) and the head moves 6 cells. *)
Lemma wall_pass_1 l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;1;1] *> r -->*
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> r.
Proof. es. Qed.

Lemma wall_pass n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^n *> r -->*
  l <* [1;1;1;1;1;0]^^n <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> r.
Proof.
  gen l r. induction n as [|n IHn]; intros l r.
  - finish.
  - cbn[lpow]. simpl_tape.
    follow wall_pass_1.
    follow IHn.
    rewrite lpow_shift'. simpl_tape. finish.
Qed.

(** A deep digit that does not carry. The pass has crossed the wall (head D on the 0 after 00000, the last wall word
    011111 to its left); the digit and the start of the next wall follow. Three of the four phases turn the head
    back: it ends in C on the last cell of that wall word, ready for the sweep to the left ([wall_l]); the digit is
    rewritten to the next phase. Digit words as found at step 10^11 in the deepest units. *)
Lemma digit_bounce_a l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. es. Qed.

Lemma digit_bounce_b l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. es. Qed.

Lemma digit_bounce_c l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1] *> r.
Proof. es. Qed.

(** The fourth phase carries: the head runs on to the next wall, in the form [wall_pass] starts from. *)
Lemma digit_carry l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. es. Qed.

Lemma wall_regroup k (l:side):
  l <* [1;1;1;1;1;0]^^k <* [1;1;1;1;0] = l <* [1;1;1;1;0] <* [1;1;1;1;0;1]^^k.
Proof. symmetry. apply (lpow_rotate' [1] [1;1;1;1;0]). Qed.

(** One round through a deep unit in phase a: pass over the wall (n+1 words), turn back at the digit, sweep back. *)
Lemma unit_round_a n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow digit_bounce_a. rewrite wall_regroup. follow wall_l. finish. Qed.

(** One round through a deep unit in phase b: pass over the wall (n+1 words), turn back at the digit, sweep back. *)
Lemma unit_round_b n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow digit_bounce_b. rewrite wall_regroup. follow wall_l. finish. Qed.

(** One round through a deep unit in phase c: pass over the wall (n+1 words), turn back at the digit, sweep back. *)
Lemma unit_round_c n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [1;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow digit_bounce_c. rewrite wall_regroup. follow wall_l. finish. Qed.

(** A deep unit in the carrying phase: pass over its wall, carry through the digit, arrive at the next wall. *)
Lemma unit_carry n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [1;1;1;1;1;0]^^n <* [1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow digit_carry. finish. Qed.
