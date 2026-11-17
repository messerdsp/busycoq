From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia ZArith List String.
From BusyCoq Require Import Longitudinal.
From M9 Require Import M9Timer M9Carry.
Open Scope list.
Import Eqb.

Ltac esw := apply BoundedConfig.segRLs_c_spec with (T:=10^3); reflexivity.

(* The 14 other stop patterns with the normal return (they contain a run of length 1, so they do not occur
   outside the parse prefix in the data, but the machine handles them the same way). *)
Lemma X0_01101000: segRLs tm hRL [] [0;1;1;0;1;0;0;0] [0;0;1;1;1;0;0;0]. Proof. esw. Qed.
Lemma X0_01101001: segRLs tm hRL [] [0;1;1;0;1;0;0;1] [0;0;1;1;1;0;0;1]. Proof. esw. Qed.
Lemma X0_01101010: segRLs tm hRL [] [0;1;1;0;1;0;1;0] [0;0;1;1;1;0;1;0]. Proof. esw. Qed.
Lemma X0_01101011: segRLs tm hRL [] [0;1;1;0;1;0;1;1] [0;0;1;1;1;0;1;1]. Proof. esw. Qed.
Lemma X0_01100010: segRLs tm hRL [] [0;1;1;0;0;0;1;0] [0;0;0;0;0;1;1;0]. Proof. esw. Qed.
Lemma X1_101000: segRLs tm hRL' [] [1;0;1;0;0;0] [1;1;1;0;0;0]. Proof. esw. Qed.
Lemma X1_101001: segRLs tm hRL' [] [1;0;1;0;0;1] [1;1;1;0;0;1]. Proof. esw. Qed.
Lemma X1_101010: segRLs tm hRL' [] [1;0;1;0;1;0] [1;1;1;0;1;0]. Proof. esw. Qed.
Lemma X1_101011: segRLs tm hRL' [] [1;0;1;0;1;1] [1;1;1;0;1;1]. Proof. esw. Qed.
Lemma X1_100010: segRLs tm hRL' [] [1;0;0;0;1;0] [0;0;0;1;1;0]. Proof. esw. Qed.
Lemma X1_100100: segRLs tm hRL' [] [1;0;0;1;0;0] [1;1;1;1;1;0]. Proof. esw. Qed.
Lemma X1_100101: segRLs tm hRL' [] [1;0;0;1;0;1] [1;1;1;1;1;1]. Proof. esw. Qed.
Lemma X1_0100: segRLs tm hRL' [] [0;1;0;0] [1;1;0;0]. Proof. esw. Qed.
Lemma X1_0101: segRLs tm hRL' [] [0;1;0;1] [1;1;0;1]. Proof. esw. Qed.

(* The abnormal return: after a t0 0110, a stop 0100 or 0101 sends the head back in X = (C,[1;1]); every t0 0110
   below becomes 1111 and passes X on, and the first t1 10 below becomes 11 and returns in the normal t1 state. *)
Notation X := (C,[1;1]).
Lemma AB0_0100: segRLs tm [(hR,X)] [] [0;1;1;0;0;1;0;0] [1;1;1;1;1;1;1;0]. Proof. esw. Qed.
Lemma AB0_0101: segRLs tm [(hR,X)] [] [0;1;1;0;0;1;0;1] [1;1;1;1;1;1;1;1]. Proof. esw. Qed.
Lemma ABD0_0110: segRLs tm [(hR,X)] [(hR,X)] [0;1;1;0] [1;1;1;1]. Proof. esw. Qed.
Lemma ABD1_10: segRLs tm hRL' [(hR,X)] [1;0] [1;1]. Proof. esw. Qed.
