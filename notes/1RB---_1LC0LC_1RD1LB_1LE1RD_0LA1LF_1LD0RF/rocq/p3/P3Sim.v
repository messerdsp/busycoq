(** A verified accelerated simulator (the scheme of tools/chainb.c): the tape is two stacks of runs of 6-cell
    blocks plus the block behind the head; a macro step runs the machine on the 12-cell window
    [back block, facing block] until the head leaves it, and a whole run of equal facing blocks is crossed at once
    when one copy gives back the same state, direction and back block.
    Main result: [run_ok]: [c0 -->* decode (run tbl n init)] for every n and every table that passes [check_table].
    Generic in the machine. *)
From BusyCoq Require Import Individual62.
From Coq Require Import Lia ZArith List Bool.
From Coq Require Uint63 PArray.
Import PrimInt63.
Notation int := PrimInt63.int.
Notation "a =? b" := (PrimInt63.eqb a b) (at level 70) : uint63_scope.
Notation "a <? b" := (PrimInt63.ltb a b) (at level 70) : uint63_scope.
Notation "t .[ i ]" := (PArray.get t i) (at level 2, left associativity, format "t .[ i ]").
Notation array := PArray.array.
Notation to_Z := Uint63.to_Z.
Import ListNotations.
Set Default Goal Selector "!".

Section Sim.
Variable tm : TM.
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).

(** ** The machine on a finite window *)
(** [ls]: cells left of the head (nearest first), [c]: the cell under the head, [rs]: cells to the right.
    Result: new state, exit side ([true] = right) and the window: reversed when the exit is to the right. *)
Fixpoint wsim (fuel : nat) (q : Q) (ls : list Sym) (c : Sym) (rs : list Sym) : option (Q * bool * list Sym) :=
  match fuel with
  | O => None
  | S f =>
    match tm (q, c) with
    | None => None
    | Some (c', R, q') =>
      match rs with [] => Some (q', true, c' :: ls) | x :: rs' => wsim f q' (c' :: ls) x rs' end
    | Some (c', L, q') =>
      match ls with [] => Some (q', false, c' :: rs) | x :: ls' => wsim f q' ls' x (c' :: rs) end
    end
  end.

Lemma wsim_ok fuel : forall q ls c rs q' b w,
  wsim fuel q ls c rs = Some (q', b, w) ->
  forall l r, (q;; (l <* ls) {{c}} (rs *> r)) -->* (if b then (l <* w) {{q'}}> r else l <{{q'}} (w *> r)).
Proof.
  induction fuel as [|f IH]; simpl; intros q ls c rs q' b w H l r; try discriminate.
  destruct (tm (q, c)) as [[[c' d] q'']|] eqn:E; try discriminate.
  destruct d.
  - destruct ls as [|x ls'].
    + inversion H; subst. eapply evstep_step; [exact (step_left E)|]. apply evstep_refl.
    + eapply evstep_step; [exact (step_left E)|]. exact (IH _ _ _ _ _ _ _ H l r).
  - destruct rs as [|x rs'].
    + inversion H; subst. eapply evstep_step; [exact (step_right E)|]. apply evstep_refl.
    + eapply evstep_step; [exact (step_right E)|]. exact (IH _ _ _ _ _ _ _ H l r).
Qed.

(** ** Blocks and states as machine integers *)
Definition wr (b : int) : list Sym :=
  map (fun i => if Uint63.bit b i then S1 else S0) [0; 1; 2; 3; 4; 5]%uint63.
Definition wl (b : int) : list Sym := rev (wr b).
Fixpoint enc (l : list Sym) : int :=
  match l with
  | [] => 0
  | S0 :: t => lsl (enc t) 1
  | S1 :: t => lor (lsl (enc t) 1) 1
  end%uint63.

Definition st_of (sd : int) : option (Q * bool) :=
  (if sd =? 0 then Some (A, false) else if sd =? 1 then Some (A, true) else
   if sd =? 2 then Some (B, false) else if sd =? 3 then Some (B, true) else
   if sd =? 4 then Some (C, false) else if sd =? 5 then Some (C, true) else
   if sd =? 6 then Some (D, false) else if sd =? 7 then Some (D, true) else
   if sd =? 8 then Some (E, false) else if sd =? 9 then Some (E, true) else
   if sd =? 10 then Some (F, false) else if sd =? 11 then Some (F, true) else None)%uint63.
Definition enc_st (q : Q) (dr : bool) : int :=
  (add (match q with A => 0 | B => 2 | C => 4 | D => 6 | E => 8 | F => 10 end) (if dr then 1 else 0))%uint63.

Fixpoint list_eqb (a b : list Sym) : bool :=
  match a, b with
  | [], [] => true
  | x :: a', y :: b' => sym_eqb x y && list_eqb a' b'
  | _, _ => false
  end.
Lemma list_eqb_ok a : forall b, list_eqb a b = true -> a = b.
Proof.
  induction a as [|x a IH]; destruct b as [|y b]; simpl; intros H; try discriminate; auto.
  apply andb_true_iff in H. destruct H as [H1 H2].
  destruct (sym_eqb_spec x y); try discriminate. subst. f_equal. auto.
Qed.

(** ** Table entries *)
Record entry := Ent {
  ksd : int; kback : int; kfac : int;      (* key: state*2+direction, back block, facing block *)
  valid : bool; kdr : bool;                (* [kdr]: moving right *)
  chain : bool;                            (* same state, direction and back block afterwards *)
  cont : bool;                             (* leaves the window on the far side *)
  nsd : int; far : int; near : int }.      (* [far]: the block left behind, [near]: the new back block *)

Definition start s (dr : bool) back fac (l r : side) : Q * tape :=
  if dr then (l <* wl back) {{s}}> (wr fac *> r) else (l <* wl fac) <{{s}} (wr back *> r).
Definition fin ns (ndr : bool) w0 w1 (l r : side) : Q * tape :=
  if ndr then (l <* wl w0 <* wl w1) {{ns}}> r else l <{{ns}} (wr w0 *> wr w1 *> r).

Definition entry_spec (e : entry) : Prop :=
  valid e = true ->
  exists s ns ndr,
    st_of (ksd e) = Some (s, kdr e) /\ st_of (nsd e) = Some (ns, ndr) /\
    cont e = Bool.eqb (kdr e) ndr /\
    (chain e = true -> cont e = true /\ nsd e = ksd e /\ near e = kback e) /\
    forall l r, start s (kdr e) (kback e) (kfac e) l r -->*
                fin ns ndr (if kdr e then far e else near e) (if kdr e then near e else far e) l r.

Definition FUEL := 5000%nat.
Definition st_chk (o : option (Q * bool)) (q : Q) (d : bool) : bool :=
  match o with Some (q', d') => q_eqb q' q && Bool.eqb d' d | None => false end.

Definition mk_entry (ksd kback kfac : int) : entry :=
  let bad := Ent ksd kback kfac false false false false 0%uint63 0%uint63 0%uint63 in
  match st_of ksd with
  | None => bad
  | Some (s, dr) =>
    let res := if dr then match wr kfac with [] => None | c :: rs => wsim FUEL s (wl kback) c rs end
               else match wl kfac with [] => None | c :: ls => wsim FUEL s ls c (wr kback) end in
    match res with
    | None => bad
    | Some (ns, ndr, w) =>
      let tp := if ndr then rev w else w in
      let w0 := enc (firstn 6 tp) in
      let w1 := enc (skipn 6 tp) in
      let nsd := enc_st ns ndr in
      let far := if dr then w0 else w1 in
      let near := if dr then w1 else w0 in
      let cont := Bool.eqb dr ndr in
      if list_eqb tp (wr w0 ++ wr w1) && st_chk (st_of nsd) ns ndr
      then Ent ksd kback kfac true dr (cont && (nsd =? ksd)%uint63 && (near =? kback)%uint63) cont nsd far near
      else bad
    end
  end.

Lemma mk_entry_spec a b c : entry_spec (mk_entry a b c).
Proof.
  unfold mk_entry, entry_spec.
  destruct (st_of a) as [[s dr]|] eqn:Ea; [|simpl; discriminate].
  match goal with |- context [match ?res with Some _ => _ | None => _ end] => destruct res as [[[ns ndr] w]|] eqn:Er end;
    [|simpl; discriminate].
  match goal with |- context [if ?g then _ else _] => destruct g eqn:Eg end; [|simpl; discriminate].
  apply andb_true_iff in Eg. destruct Eg as [Et Es].
  apply list_eqb_ok in Et.
  cbn [valid ksd kdr nsd cont chain far near kback kfac]. intros _. exists s, ns, ndr.
  split; [exact Ea|]. split.
  { unfold st_chk in Es. destruct (st_of (enc_st ns ndr)) as [[q' d']|]; [|discriminate].
    apply andb_true_iff in Es. destruct Es as [E1 E2].
    destruct (q_eqb_spec q' ns); [|discriminate]. apply eqb_prop in E2. subst. reflexivity. }
  split; [reflexivity|]. split.
  { intros H. apply andb_true_iff in H. destruct H as [H H3]. apply andb_true_iff in H. destruct H as [H1 H2].
    apply Uint63.eqb_correct in H2, H3. auto. }
  intros l r.
  set (tp := if ndr then rev w else w) in *.
  set (w0 := enc (firstn 6 tp)) in *. set (w1 := enc (skipn 6 tp)) in *.
  assert (Hfin : (if ndr then (l <* w) {{ns}}> r else l <{{ns}} (w *> r)) =
                 fin ns ndr w0 w1 l r).
  { unfold fin. destruct ndr.
    - assert (Hw : w = wl w1 ++ wl w0).
      { unfold wl. rewrite <- rev_app_distr, <- Et. unfold tp. rewrite rev_involutive. reflexivity. }
      rewrite Hw, Str_app_assoc. reflexivity.
    - unfold tp in Et. rewrite Et, Str_app_assoc. reflexivity. }
  destruct dr.
  - destruct (wr c) as [|x rs] eqn:Ec; [discriminate|].
    unfold start. rewrite Ec. rewrite <- Hfin.
    exact (wsim_ok _ _ _ _ _ _ _ _ Er l r).
  - destruct (wl c) as [|x ls] eqn:Ec; [discriminate|].
    unfold start. rewrite Ec. rewrite <- Hfin.
    exact (wsim_ok _ _ _ _ _ _ _ _ Er l r).
Qed.

(** ** The table and its check *)
Definition bool_eqb := Bool.eqb.
Definition entry_eqb (x y : entry) : bool :=
  ((ksd x =? ksd y) && (kback x =? kback y) && (kfac x =? kfac y) && bool_eqb (valid x) (valid y) &&
   bool_eqb (kdr x) (kdr y) && bool_eqb (chain x) (chain y) && bool_eqb (cont x) (cont y) &&
   (nsd x =? nsd y) && (far x =? far y) && (near x =? near y))%uint63.
Lemma entry_eqb_ok x y : entry_eqb x y = true -> x = y.
Proof.
  unfold entry_eqb, bool_eqb. destruct x, y; simpl. intros H.
  repeat (apply andb_true_iff in H; destruct H as [H ?]).
  repeat match goal with
  | H : (_ =? _)%uint63 = true |- _ => apply Uint63.eqb_correct in H
  | H : Bool.eqb _ _ = true |- _ => apply eqb_prop in H
  end. subst. reflexivity.
Qed.

Definition ints_upto (n : nat) : list int := map (fun k => Uint63.of_Z (Z.of_nat k)) (seq 0 n).
Definition TSIZE := Z.to_nat 49152.
Definition chk_entry (e : entry) : bool := entry_eqb e (mk_entry (ksd e) (kback e) (kfac e)).
Definition check_table (t : array entry) : bool :=
  forallb (fun i => chk_entry t.[i]) (ints_upto TSIZE) && chk_entry (PArray.default t) && (PArray.length t =? 49152)%uint63.

Lemma check_table_ok t : check_table t = true -> forall i, entry_spec t.[i].
Proof.
  unfold check_table. intros H i.
  apply andb_true_iff in H. destruct H as [H Hl]. apply andb_true_iff in H. destruct H as [Hf Hd].
  apply Uint63.eqb_correct in Hl.
  assert (Hc : chk_entry t.[i] = true).
  { destruct (ltb i (PArray.length t)) eqn:Elt.
    - rewrite forallb_forall in Hf. apply Hf. unfold ints_upto.
      rewrite Hl in Elt. apply Uint63.ltb_spec in Elt. change (to_Z 49152) with 49152%Z in Elt.
      pose proof (Uint63.to_Z_bounded i) as Hb.
      apply in_map_iff. exists (Z.to_nat (to_Z i)). split.
      + rewrite Z2Nat.id by lia. apply Uint63.of_to_Z.
      + apply in_seq. split; [lia|]. rewrite Nat.add_0_l. unfold TSIZE. apply Z2Nat.inj_lt; lia.
    - rewrite PArray.get_out_of_bounds by exact Elt. exact Hd. }
  unfold chk_entry in Hc. apply entry_eqb_ok in Hc. rewrite Hc. apply mk_entry_spec.
Qed.

(** ** Stacks of runs.  [Run b n rest]: n+1 copies of block b, then rest. *)
Inductive stk := Nil | Run (b n : int) (rest : stk).
Definition cnt (n : int) : nat := S (Z.to_nat (to_Z n)).
Fixpoint dec (w : int -> list Sym) (s : stk) : side :=
  match s with
  | Nil => const S0
  | Run b n r => (w b)^^(cnt n) *> dec w r
  end.

Definition push (b n : int) (s : stk) : stk :=
  match s with
  | Run b' n' r => let m := add (add n n') 1%uint63 in
                   if (b =? b')%uint63 && (n <? m)%uint63 then Run b m r else Run b n s
  | Nil => Run b n s
  end.
Definition top (s : stk) : int := match s with Nil => 0%uint63 | Run b _ _ => b end.
Definition pop1 (s : stk) : stk :=
  match s with
  | Nil => Nil
  | Run b n r => if (n =? 0)%uint63 then r else Run b (sub n 1%uint63) r
  end.

Lemma push_ok w b n s : dec w (push b n s) = (w b)^^(cnt n) *> dec w s.
Proof.
  destruct s as [|b' n' r]; [reflexivity|]. unfold push.
  destruct ((b =? b')%uint63 && (n <? add (add n n') 1)%uint63) eqn:E; [|reflexivity].
  apply andb_true_iff in E. destruct E as [E1 E2]. apply Uint63.eqb_correct in E1. subst b'.
  apply Uint63.ltb_spec in E2. cbn [dec].
  assert (Hc : cnt (add (add n n') 1%uint63) = (cnt n + cnt n')%nat).
  { unfold cnt.
    pose proof (Uint63.to_Z_bounded n) as B1. pose proof (Uint63.to_Z_bounded n') as B2.
    assert (Hm : to_Z (add (add n n') 1%uint63) = (to_Z n + to_Z n' + 1)%Z).
    { rewrite Uint63.add_spec, Uint63.add_spec in *. change (to_Z 1) with 1%Z in *.
      rewrite Zplus_mod_idemp_l in *.
      destruct (Z_lt_dec (to_Z n + to_Z n' + 1) Uint63.wB) as [Hlt|Hge].
      - apply Z.mod_small. lia.
      - exfalso.
        replace (to_Z n + to_Z n' + 1)%Z with ((to_Z n + to_Z n' + 1 - Uint63.wB) + 1 * Uint63.wB)%Z in E2 by ring.
        rewrite Z_mod_plus_full in E2. rewrite Z.mod_small in E2 by lia. lia. }
    rewrite Hm. lia. }
  rewrite Hc, lpow_add, Str_app_assoc. reflexivity.
Qed.

Lemma c6 : [S0; S0; S0; S0; S0; S0] *> const S0 = const S0.
Proof. simpl. repeat rewrite <- const_unfold. reflexivity. Qed.

Lemma pop_ok w s : w 0%uint63 = [S0; S0; S0; S0; S0; S0] -> dec w s = w (top s) *> dec w (pop1 s).
Proof.
  intros H0. destruct s as [|b n r]; cbn [dec top pop1].
  - rewrite H0. symmetry. apply c6.
  - destruct (n =? 0)%uint63 eqn:E.
    + apply Uint63.eqb_correct in E. subst n. unfold cnt. change (to_Z 0) with 0%Z. simpl. rewrite app_nil_r. reflexivity.
    + assert (Hc : cnt n = S (cnt (sub n 1%uint63))).
      { unfold cnt. apply Uint63.eqb_false_spec in E.
        pose proof (Uint63.to_Z_bounded n) as B1.
        assert (to_Z n <> 0%Z) by (intros H; apply E; apply Uint63.to_Z_inj; exact H).
        rewrite Uint63.sub_spec. change (to_Z 1) with 1%Z. rewrite Z.mod_small by lia. lia. }
      rewrite Hc. cbn [dec lpow]. rewrite Str_app_assoc. reflexivity.
Qed.

Lemma wr0 : wr 0%uint63 = [S0; S0; S0; S0; S0; S0].
Proof. reflexivity. Qed.
Lemma wl0 : wl 0%uint63 = [S0; S0; S0; S0; S0; S0].
Proof. reflexivity. Qed.

(** ** Configurations and the macro step *)
Record cfg := Cfg { sd : int; back : int; cl : stk; cr : stk }.
Definition decL := dec wl.
Definition decR := dec wr.
Definition decode (c : cfg) : Q * tape :=
  match st_of (sd c) with
  | Some (s, true) => (decL (cl c) <* wl (back c)) {{s}}> decR (cr c)
  | Some (s, false) => decL (cl c) <{{s}} (wr (back c) *> decR (cr c))
  | None => c0
  end.

Definition mk (drg : bool) sd back (F Bk : stk) : cfg := if drg then Cfg sd back Bk F else Cfg sd back F Bk.

Definition step (t : array entry) (c : cfg) : cfg :=
  let 'Cfg sd back l r := c in
  let drg := (land sd 1 =? 1)%uint63 in
  let F := if drg then r else l in
  let Bk := if drg then l else r in
  let fac := top F in
  let e := t.[lor (lor (lsl sd 12) (lsl back 6)) fac] in
  if valid e && bool_eqb (kdr e) drg && (ksd e =? sd)%uint63 && (kback e =? back)%uint63 && (kfac e =? fac)%uint63
  then
    let single :=
      let F' := pop1 F in
      if cont e then mk drg (nsd e) (near e) F' (push (far e) 0 Bk)
      else mk drg (nsd e) (far e) (push (near e) 0 F') Bk in
    if chain e then
      match F with
      | Nil => single
      | Run _ n F' => mk drg sd back F' (push (far e) n Bk)
      end
    else single
  else c.

Lemma chain_r s bk b fr :
  (forall l r, (l <* wl bk) {{s}}> (wr b *> r) -->* (l <* wl fr <* wl bk) {{s}}> r) ->
  forall k l r, (l <* wl bk) {{s}}> ((wr b)^^k *> r) -->* (l <* (wl fr)^^k <* wl bk) {{s}}> r.
Proof.
  intros H k. induction k as [|k IH]; intros l r.
  - apply evstep_refl.
  - cbn [lpow]. rewrite !Str_app_assoc.
    eapply evstep_trans; [apply H|].
    eapply evstep_trans; [apply IH|].
    rewrite lpow_shift'. apply evstep_refl.
Qed.

Lemma chain_l s bk b fr :
  (forall l r, (l <* wl b) <{{s}} (wr bk *> r) -->* l <{{s}} (wr bk *> wr fr *> r)) ->
  forall k l r, (l <* (wl b)^^k) <{{s}} (wr bk *> r) -->* l <{{s}} (wr bk *> (wr fr)^^k *> r).
Proof.
  intros H k. induction k as [|k IH]; intros l r.
  - apply evstep_refl.
  - cbn [lpow]. rewrite !Str_app_assoc.
    eapply evstep_trans; [apply H|].
    eapply evstep_trans; [apply IH|].
    rewrite lpow_shift'. apply evstep_refl.
Qed.

Lemma lpow1 (w : list Sym) (x : side) : w^^(cnt 0) *> x = w *> x.
Proof. unfold cnt. change (to_Z 0) with 0%Z. simpl. rewrite app_nil_r. reflexivity. Qed.

Lemma step_ok t : (forall i, entry_spec t.[i]) -> forall c, decode c -->* decode (step t c).
Proof.
  intros Ht [sd0 bk l r]. unfold step.
  set (drg := (land sd0 1 =? 1)%uint63).
  set (F := if drg then r else l). set (Bk := if drg then l else r).
  set (e := t.[lor (lor (lsl sd0 12) (lsl bk 6)) (top F)]).
  destruct (valid e && bool_eqb (kdr e) drg && (ksd e =? sd0)%uint63 && (kback e =? bk)%uint63 &&
            (kfac e =? top F)%uint63) eqn:G; [|apply evstep_refl].
  repeat (apply andb_true_iff in G; destruct G as [G ?]).
  repeat match goal with
  | H : (_ =? _)%uint63 = true |- _ => apply Uint63.eqb_correct in H
  | H : bool_eqb _ _ = true |- _ => apply eqb_prop in H
  end.
  destruct (Ht (lor (lor (lsl sd0 12) (lsl bk 6)) (top F)) G) as (s & ns & ndr & Hs & Hn & Hc & Hch & Hrun).
  fold e in Hs, Hn, Hc, Hch, Hrun.
  rewrite H0, H1, H2 in *. clear H0 H1 H2.
  assert (Hsingle : decode (Cfg sd0 bk l r) -->*
    decode (if cont e then mk drg (nsd e) (near e) (pop1 F) (push (far e) 0 Bk)
            else mk drg (nsd e) (far e) (push (near e) 0 (pop1 F)) Bk)).
  { unfold decode at 1. cbn [sd back cl cr]. rewrite Hs.
    specialize (Hrun (if drg then decL Bk else decL (pop1 F)) (if drg then decR (pop1 F) else decR Bk)).
    rewrite Hc. unfold F, Bk in *. destruct drg.
    - replace (decR r) with (wr (top r) *> decR (pop1 r)) by (symmetry; apply (pop_ok wr r wr0)).
      rewrite H in Hrun.
      eapply evstep_trans; [exact Hrun|]. apply evstep_refl'.
      destruct ndr; cbn [Bool.eqb]; unfold mk; cbn iota; unfold decode; cbn [sd back cl cr]; rewrite Hn;
        unfold start, fin, decL, decR;
        rewrite push_ok, lpow1; reflexivity.
    - replace (decL l) with (wl (top l) *> decL (pop1 l)) by (symmetry; apply (pop_ok wl l wl0)).
      rewrite H in Hrun.
      eapply evstep_trans; [exact Hrun|]. apply evstep_refl'.
      destruct ndr; cbn [Bool.eqb]; unfold mk; cbn iota; unfold decode; cbn [sd back cl cr]; rewrite Hn;
        unfold start, fin, decL, decR;
        rewrite push_ok, lpow1; reflexivity. }
  destruct (chain e) eqn:Ech; [|exact Hsingle].
  destruct F as [|b n F'] eqn:EF; [exact Hsingle|].
  destruct (Hch eq_refl) as (Hcont & Hnsd & Hnear).
  rewrite Hcont in Hc. rewrite Hnsd in Hn. rewrite Hs in Hn. inversion Hn; subst ns ndr.
  rewrite Hnear, H in Hrun. cbn [top] in Hrun.
  unfold decode at 1. cbn [sd back cl cr]. rewrite Hs.
  unfold F, Bk in *. destruct drg; unfold mk, decode; cbn [sd back cl cr]; rewrite Hs.
  - subst r. unfold decR at 1. cbn [dec]. fold decR.
    eapply evstep_trans; [apply (chain_r s bk b (far e)); exact Hrun|].
    apply evstep_refl'. unfold decL. rewrite push_ok. reflexivity.
  - subst l. unfold decL at 1. cbn [dec]. fold decL.
    eapply evstep_trans; [apply (chain_l s bk b (far e)); exact Hrun|].
    apply evstep_refl'. unfold decR. rewrite push_ok. reflexivity.
Qed.

(** ** Running *)
Definition init : cfg := Cfg 1%uint63 0%uint63 Nil Nil.
Definition run (t : array entry) (n : N) (c : cfg) : cfg := N.iter n (step t) c.

Lemma init_ok : decode init = c0.
Proof.
  change (decode init) with ((const S0 <* wl 0%uint63) {{A}}> const S0).
  rewrite wl0. pose proof c6 as H6. cbv beta in H6.
  change ([S0; S0; S0; S0; S0; S0] *> const S0) with (@Str_app sym [S0; S0; S0; S0; S0; S0] (@const sym S0)) in *.
  unfold Sym in *. unfold BB62.Sym in *. rewrite H6. reflexivity.
Qed.

Theorem run_ok t n c : check_table t = true -> decode c -->* decode (run t n c).
Proof.
  intros H. pose proof (check_table_ok t H) as Ht. unfold run.
  apply N.iter_invariant; [|apply evstep_refl].
  intros x Hx. eapply evstep_trans; [exact Hx|]. apply step_ok. exact Ht.
Qed.

Definition build_table : array entry :=
  fold_left (fun t i => let s := lsr i 12 in let b := land (lsr i 6) 63 in let f := land i 63 in
                        PArray.set t i (mk_entry s b f))
            (ints_upto TSIZE) (PArray.make 49152 (mk_entry 12 0 0)).

(** ** Reading off the result: explicit runs, a periodic stretch of four single blocks, explicit runs, the rest *)
Definition runs (w : int -> list Sym) (h : list (int * int)) (r : side) : side :=
  fold_right (fun p x => (w (fst p))^^(cnt (snd p)) *> x) r h.
Fixpoint take (k : nat) (s : stk) : list (int * int) * stk :=
  match k, s with
  | S k', Run b n r => let (h, t) := take k' r in ((b, n) :: h, t)
  | _, _ => ([], s)
  end.
Lemma take_ok w k : forall s h t, take k s = (h, t) -> dec w s = runs w h (dec w t).
Proof.
  induction k as [|k IH]; intros s h t H.
  - simpl in H. inversion H. reflexivity.
  - destruct s as [|b n r]; [inversion H; reflexivity|].
    cbn [take] in H. destruct (take k r) as [h' t'] eqn:E. inversion H; subst.
    cbn [runs fold_right fst snd dec]. rewrite (IH _ _ _ E). reflexivity.
Qed.

Fixpoint strip4 (b1 b2 b3 b4 : int) (s : stk) (acc : nat) : nat * stk :=
  match s with
  | Run c1 n1 (Run c2 n2 (Run c3 n3 (Run c4 n4 r))) =>
    if ((c1 =? b1) && (c2 =? b2) && (c3 =? b3) && (c4 =? b4) &&
        (n1 =? 0) && (n2 =? 0) && (n3 =? 0) && (n4 =? 0))%uint63
    then strip4 b1 b2 b3 b4 r (S acc) else (acc, s)
  | _ => (acc, s)
  end.
Fixpoint ssize (s : stk) : nat := match s with Nil => O | Run _ _ r => S (ssize r) end.
Lemma strip4_ok w b1 b2 b3 b4 m : forall s acc c t, (ssize s <= m)%nat ->
  strip4 b1 b2 b3 b4 s acc = (c, t) ->
  exists k, c = (acc + k)%nat /\ dec w s = (w b1 ++ w b2 ++ w b3 ++ w b4)^^k *> dec w t.
Proof.
  induction m as [|m IH]; intros s acc c t Hm H.
  - destruct s; [|simpl in Hm; lia]. inversion H. exists O. split; [lia|reflexivity].
  - destruct s as [|c1 n1 [|c2 n2 [|c3 n3 [|c4 n4 r]]]];
      try (inversion H; exists O; split; [lia|reflexivity]).
    cbn [strip4] in H.
    match type of H with (if ?g then _ else _) = _ => destruct g eqn:G end;
      [|inversion H; exists O; split; [lia|reflexivity]].
    repeat (apply andb_true_iff in G; destruct G as [G ?]).
    repeat match goal with
    | H : (_ =? _)%uint63 = true |- _ => apply Uint63.eqb_correct in H
    end. subst.
    apply IH in H; [|simpl in Hm; lia].
    destruct H as (k & Hk & Hd). exists (S k). split; [lia|].
    cbn [dec]. rewrite Hd. rewrite !lpow1. cbn [lpow]. rewrite !Str_app_assoc. reflexivity.
Qed.

Definition is_nil (s : stk) : bool := match s with Nil => true | _ => false end.
Definition shape (k1 : nat) (b1 b2 b3 b4 : int) (k2 : nat) (c : cfg) :=
  let (h1, s1) := take k1 (cr c) in
  let (n, s2) := strip4 b1 b2 b3 b4 s1 O in
  let (h2, _) := take k2 s2 in
  (sd c, back c, is_nil (cl c), h1, h2).

Lemma shape_ok k1 b1 b2 b3 b4 k2 c sd0 bk h1 h2 s :
  shape k1 b1 b2 b3 b4 k2 c = (sd0, bk, true, h1, h2) -> st_of sd0 = Some (s, false) ->
  exists n rest, decode c =
    const S0 <{{s}} (wr bk *> runs wr h1 ((wr b1 ++ wr b2 ++ wr b3 ++ wr b4)^^n *> runs wr h2 rest)).
Proof.
  unfold shape. intros H Hs.
  destruct (take k1 (cr c)) as [h1' s1] eqn:E1.
  destruct (strip4 b1 b2 b3 b4 s1 O) as [n s2] eqn:E2.
  destruct (take k2 s2) as [h2' s3] eqn:E3.
  inversion H; subst. clear H.
  destruct (strip4_ok wr _ _ _ _ _ _ _ _ _ (le_n _) E2) as (k & _ & Hk).
  exists k, (dec wr s3).
  unfold decode. rewrite Hs. destruct (cl c); [|discriminate].
  unfold decR, decL. rewrite (take_ok wr _ _ _ _ E1), Hk, (take_ok wr _ _ _ _ E3). reflexivity.
Qed.

End Sim.
