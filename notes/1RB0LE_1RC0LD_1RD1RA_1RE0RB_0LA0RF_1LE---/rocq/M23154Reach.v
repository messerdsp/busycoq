(** 23154 from blank tape reaches the sweep configuration [Q (raw 3) [0,0,1,1,1,0,2,1^10]] (step 5,512, as in the
    explorer's lean/Reach.lean for 23154).  Checked by computation ([solve_init]). *)
From BusyCoq Require Import Individual62.
From M23154 Require Import M23154Rules M23154Sweep M23154Carry.
Require Import Lia List.
Import ListNotations.
Open Scope list.

Definition D0 : list nat := [O; O; S O; S O; S O; O; S (S O)] ++ repeat (S O) 10.

Theorem reach_D0 : c0 -->* Q (raw 3) D0.
Proof. unfold Q, raw, D0. cbn. solve_init. Qed.
