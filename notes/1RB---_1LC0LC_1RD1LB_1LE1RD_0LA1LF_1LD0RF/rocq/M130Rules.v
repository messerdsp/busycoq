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

(** The first two units of the chain that starts after the second overflow (tape at step 2,592,545,302,250,949):
    their digits are followed by fixed leftover words. Each case, as found at the end of the wall, either turns the
    head back (ready for [wall_l]) or carries on to the next wall (in the form [wall_pass] starts from). *)
(* unit 1, case 0: bounce *)
Lemma u1_case0 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 1, case 1: bounce *)
Lemma u1_case1 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 1, case 2: carry *)
Lemma u1_case2 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1] *> r -->*
  l <* [1;1;1;1;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1;0;1;0;1;1;1] *> r.
Proof. es. Qed.

(* unit 1, case 3: carry *)
Lemma u1_case3 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1] *> r -->*
  l <* [0;0;0;0;1;1;1;1;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [1;1;1;1;0;1;0;1;0;1;0;1] *> r.
Proof. es. Qed.

(* unit 1, case 4: bounce *)
Lemma u1_case4 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 2, case 0: bounce *)
Lemma u2_case0 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 2, case 1: bounce *)
Lemma u2_case1 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 2, case 2: bounce *)
Lemma u2_case2 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] {{C}}> [1;1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. es. Qed.

(* unit 2, case 3: carry *)
Lemma u2_case3 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1] *> r -->*
  l <* [1;1;1;1;1;1;1;1;1;1;1;0;0;0;0;0;0;0;1;1;1;1;1;1;1;1;1;1;1;1;1;0;0;0;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [1;1;1;1;1;1;0;1;0;1;0;1] *> r.
Proof. es. Qed.

(* unit 2, case 4: carry *)
Lemma u2_case4 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1] *> r -->*
  l <* [1;1;1;1;1;1;1;1;1;1;1;1;1;0;0;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1;0;1;0;1;1;1] *> r.
Proof. es. Qed.

(* unit 2, case 5: carry *)
Lemma u2_case5 l r:
  l <* [1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;1;1;0;1;0;1;0;1] *> r -->*
  l <* [1;1;1;1;1;1;1;1;1;1;1;1;1;0;0;0;1;1;1;1;1;1;1;1;1;1;1;1;1;0;0;0;1;1;1;1;1;0;1;1;1;1;1;0] <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [1;1;1;1;1;1;0;1;0;1;0;1] *> r.
Proof. es. Qed.


Lemma u1_case0_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u1_case0. rewrite wall_regroup. follow wall_l. finish. Qed.

Lemma u1_case1_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u1_case1. rewrite wall_regroup. follow wall_l. finish. Qed.

Lemma u1_case4_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [1;1;1;1;0;1;0;1;0;1;1;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u1_case4. rewrite wall_regroup. follow wall_l. finish. Qed.

Lemma u2_case0_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u2_case0. rewrite wall_regroup. follow wall_l. finish. Qed.

Lemma u2_case1_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u2_case1. rewrite wall_regroup. follow wall_l. finish. Qed.

Lemma u2_case2_round n l r:
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S n) *> [1;1;1;1;0;1;0;1;0;1;0;1;0;1;0] *> r -->*
  l <* [1;1;1;1;0] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0] *> r.
Proof. follow wall_pass. cbn[lpow]. simpl_tape. follow u2_case2. rewrite wall_regroup. follow wall_l. finish. Qed.

(** The pass to the right over the band left by the second overflow: the band is a periodic 24-cell word; every 228
    steps the head moves one word (found in the end transition at step 5,269,793,291,944,956, the only one to 2·10^17
    that crosses the whole band). *)
Lemma band_pass_1 l r:
  l <* [1;1;1;1;1;1;1;1;1;0;0;0;0;0;1;1;1;1;1;1;1;0;1;1] {{D}}> [0;1;0;1;0;1;1;1;0;1;0;1;0;1;1;1;0;1;0;1;0;1;1;1] *> r -->* l <* [1;1;1;1;1;0;1;1;1;1;1;1;1;0;1;1;1;1;1;1;1;0;1;1] <* [1;1;1;1;1;1;1;1;1;0;0;0;0;0;1;1;1;1;1;1;1;0;1;1] {{D}}> r.
Proof. es. Qed.

Lemma band_pass n l r:
  l <* [1;1;1;1;1;1;1;1;1;0;0;0;0;0;1;1;1;1;1;1;1;0;1;1] {{D}}> [0;1;0;1;0;1;1;1;0;1;0;1;0;1;1;1;0;1;0;1;0;1;1;1]^^n *> r -->* l <* [1;1;1;1;1;0;1;1;1;1;1;1;1;0;1;1;1;1;1;1;1;0;1;1]^^n <* [1;1;1;1;1;1;1;1;1;0;0;0;0;0;1;1;1;1;1;1;1;0;1;1] {{D}}> r.
Proof.
  gen l r. induction n as [|n IHn]; intros l r.
  - finish.
  - cbn[lpow]. simpl_tape. follow band_pass_1. follow IHn. rewrite lpow_shift'. simpl_tape. finish.
Qed.


(** The left end of the post-overflow chain. Each round starts with the head in state C on the blank cell left of
    the 14-cell prefix, crosses the prefix into the first wall (prefix_turn), and ends when the sweep back over the
    first wall (wall_l) reaches the prefix and turns (round_close). *)
Lemma prefix_turn k r:
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^k *> [0;1;1;1] *> r -->*
  const 0 <* [0;0;0;0;0;1;1;1;1;1;1;1] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^k *> r.
Proof.
  intros. rewrite (lpow_rotate' [0;1] [0;1;1;1]).
  es.
Qed.

Lemma round_close n r:
  const 0 <* [1;1;1;1;0;1;1;1;1;1;1;1] <{{B}} [1;1;1;0;1;0]^^n *> [1] *> r -->*
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^n *> [0] *> [1] *> r.
Proof.
  intros. rewrite (lpow_rotate' [1;1;1;0;1] [0]).
  es.
Qed.

(** A whole round in which unit 1 (phase 0 of its leftover body) turns back: round start to round start. The first
    wall grows from n+1 to n+2 words and the digit word changes. *)
Lemma round_u1_0 n r:
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^(S n) *> [0;1;1;1] *> [0;1;0;1;0;1;0] *> r -->*
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^(n + 2) *> [0;1;1;1] *> [1;1;1;1;0] *> r.
Proof.
  intros. follow prefix_turn. follow u1_case0_round.
  change (const 0 <* [1;1;1;1;1;1;1] <* [1;1;1;1;0]) with (const 0 <* [1;1;1;1;0;1;1;1;1;1;1;1]).
  follow round_close.
  rewrite lpow_add. cbn [lpow]. simpl_tape. finish.
Qed.

(** Units of the post-overflow chain in cut form (README section 6): a unit is entered with the head in state D on
    its first cell and [1;1] to the left, and left for the last time in state C on the cell left of it. *)
Lemma enter_D m l r:
  l <* [1;1] {{D}}> [0;1;1;1;0;1]^^(S (S m)) *> r -->*
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^m *> [0;1] *> r.
Proof.
  intros. rewrite (lpow_rotate' [0;1;1;1] [0;1]). cbn [lpow]. simpl_tape. es.
Qed.

(** A deep unit in phase D0 (digit (01)^7, wall n+3 words, followed by a wall of at least two words): one trip. *)
Lemma trip_D0 n l r:
  l <* [1;1] {{D}}> [0;1;1;1;0;1]^^(S (S (S n))) *> [0;1;0;1;0;1;0;1;0;1;0;1;0;1] *> [0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [0] {{C}}> [1;0;1;0] *> [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof.
  intros. follow (enter_D (S n)). simpl_tape. follow unit_round_a. es.
Qed.

Lemma trip_D1 n l r:
  l <* [1;1] {{D}}> [0;1;1;1;0;1]^^(S (S (S n))) *> [0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1] *> [0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [0] {{C}}> [1;0;1;0] *> [1;1;1;0;1;0]^^n *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;1;1;1;1;1;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r.
Proof.
  intros. follow (enter_D (S n)). simpl_tape. follow unit_round_b. es.
Qed.

Lemma lshift (xs : list Sym) n (r : side): xs^^n *> xs *> r = xs *> xs^^n *> r.
Proof.
  induction n as [|n IH]; cbn [lpow].
  - reflexivity.
  - rewrite !Str_app_assoc, IH. reflexivity.
Qed.

Lemma enter_D2 m l r:
  l <* [1;1] {{D}}> [0;1;1;1;0;1]^^(S (S m)) *> [0;1;1;1;1;1;1;1] *> r -->*
  l <* [0;0;0;0;0] {{D}}> [0;1;1;0;1;1;1] *> [0;1;0;1;1;1]^^(S m) *> [1;1;1;1] *> r.
Proof.
  intros. follow enter_D. cbn [lpow]. rewrite Str_app_assoc. rewrite <- lshift. cbn [Str_app]. apply evstep_refl.
Qed.

Lemma trip_D2 n l r:
  l <* [1;1] {{D}}> [0;1;1;1;0;1]^^(S (S (S n))) *> [0;1;1;1;1;1;1;1;0;1;0;1;0;1;0;1;0;1] *> [0;1;1;1;0;1;0;1;1;1;0;1;0;1;1;1;0;1] *> r -->*
  l <* [0] {{C}}> [1;0;1;0] *> [1;1;1;0;1;0]^^(S n) *> [1] *> [1;1;0;1;0;1;1;1;0;1;0;1;0;1;0;1;0;1;0;1;1;1;1;1;1;1;0;1;1;1;0;1;0;1;1;1;0;1;0;1] *> [1;1;0;1] *> r.
Proof.
  intros. follow (enter_D2 (S n)). simpl_tape. follow (unit_round_c (S n)). step. step. step. finish.
Qed.
