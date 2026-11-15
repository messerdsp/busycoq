From BusyCoq Require Import Individual62.
Require Import ZArith List Lia.
From M9 Require Import M9Timer.
Open Scope list.

Fixpoint mcount T x n :=
match T with
| O => (n, x)
| S T => match mstep x with Some x' => mcount T x' (N.succ n) | None => (n, x) end
end.

Lemma mcount_spec T x n:
  Config_eval x -->* Config_eval (snd (mcount T x n)).
Proof.
  revert x n; induction T; intros; cbn.
  - finish.
  - destruct (mstep x) eqn:E.
    + apply mstep_spec in E. follow E. apply IHT.
    + finish.
Qed.

Definition run13000 := mcount 13000 (cfgL' 5 5 ([1;0]*>0inf)) 0.

Definition b_of x := match x with cfgL' _ b _ | cfgR' _ b _ => b end.

(* From the blank tape the machine reaches the macro configuration after 13,000 macro steps (all of them
   succeed), where the counter b has 400 bits; the twin TM2 of SBCv9.v halts at its 374th overflow. *)
Theorem reach13000: c0 -->* Config_eval (snd run13000).
Proof.
  eapply evstep_trans. 1: apply init.
  apply (mcount_spec 13000 (cfgL' 5 5 ([1;0]*>0inf)) 0).
Qed.

Lemma run13000_facts: fst run13000 = 13000%N /\ N.size (b_of (snd run13000)) = 400%N.
Proof. vm_compute. split; reflexivity. Qed.

Print Assumptions reach13000.
Print Assumptions run13000_facts.
