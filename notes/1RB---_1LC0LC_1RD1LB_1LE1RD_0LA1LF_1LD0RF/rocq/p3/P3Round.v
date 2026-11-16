(** The result of P3Reach in the round-start form of ../M130Rules.v ([prefix_turn], [round_u1_0]): the head in
    state C on the blank cell left of the 14-cell prefix, then the first wall. *)
From BusyCoq Require Import Individual62.
From Coq Require Import ZArith List.
From P3 Require Import P3Sim P3Reach.
Import PrimInt63.

Lemma round_form (r : side) :
  const S0 <{{C}} (wr 63%uint63 *> (wr 59%uint63)^^(cnt 0%uint63) *> (wr 58%uint63)^^(cnt 1880774%uint63) *> r) =
  const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^(Z.to_nat 1880774) *> [0;1;1;1] *> r.
Proof.
  change (wr 63%uint63) with [1;1;1;1;1;1]. change (wr 59%uint63) with [1;1;0;1;1;1].
  change (wr 58%uint63) with [0;1;0;1;1;1]. change (cnt 0%uint63) with 1%nat.
  change (cnt 1880774%uint63) with (S (Z.to_nat 1880774)).
  generalize (Z.to_nat 1880774) as m. intro m.
  rewrite (lpow_rotate' [0;1] [0;1;1;1]).
  cbn [lpow app Str_app]. reflexivity.
Qed.

Theorem reach_round_start : exists r,
  c0 -[ tm ]->* const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^(Z.to_nat 1880774) *> [0;1;1;1] *> r.
Proof.
  destruct reach_overflow2 as (n & rest & H).
  exists (runs wr (tl (tl H1)) (BAND^^n *> runs wr H2 rest)).
  rewrite <- round_form. exact H.
Qed.
