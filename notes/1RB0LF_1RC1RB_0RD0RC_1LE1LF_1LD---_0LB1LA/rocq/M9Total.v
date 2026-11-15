From BusyCoq Require Import Individual62.
Require Import ZifyNat ZifyN Lia ZArith List String.
From M9 Require Import M9Timer M9Carry M9Windows2 M9Reduce M9List.
Open Scope list.
Import Eqb.

Lemma pfx_none_iff p w:
  pfx p w = None <-> exists i, (i < List.length p)%nat /\ nth i p S0 <> nth i w S0.
Proof.
  gen w. induction p as [|x p IH]; intros w; cbn.
  - split; [discriminate|]. intros [i [Hi _]]. lia.
  - destruct w as [|y w].
    + destruct x.
      * rewrite IH. split.
        -- intros [i [Hi Hn]]. exists (S i). cbn. split; [lia|]. destruct i; auto.
        -- intros [i [Hi Hn]]. destruct i as [|i]; [cbn in Hn; congruence|].
           exists i. split; [lia|]. cbn in Hn. destruct i; auto.
      * split; auto. intros _. exists O. split; [lia|]. cbn. discriminate.
    + destruct (sym_eqb x y) eqn:E.
      * apply sym_eqb_eq in E; subst. rewrite IH. split.
        -- intros [i [Hi Hn]]. exists (S i). cbn. split; [lia|auto].
        -- intros [i [Hi Hn]]. destruct i as [|i]; [cbn in Hn; congruence|].
           exists i. split; [lia|auto].
      * split; auto. intros _. exists O. split; [lia|]. cbn.
        destruct x, y; cbn in E; congruence.
Qed.

Lemma pfx_some_nth p w w1:
  pfx p w = Some w1 -> forall i, nth i w1 S0 = nth (List.length p + i) w S0.
Proof.
  gen w. induction p as [|x p IH]; intros w H i; cbn in *.
  - inverts H. reflexivity.
  - destruct w as [|y w].
    + destruct x; [|discriminate]. rewrite (IH _ H). destruct (List.length p + i)%nat; reflexivity.
    + destruct (sym_eqb x y); [|discriminate]. apply IH, H.
Qed.

Lemma pfx_len p w w1: pfx p w = Some w1 -> (List.length w1 <= List.length w)%nat.
Proof.
  gen w. induction p as [|x p IH]; intros w H; cbn in *.
  - inverts H. lia.
  - destruct w as [|y w].
    + destruct x; [|discriminate]. apply IH in H. cbn in *. lia.
    + destruct (sym_eqb x y); [|discriminate]. apply IH in H. cbn. lia.
Qed.

(* everything below looks at the first 8 cells only *)
Definition v8 (w: list Sym) := map (fun i => nth i w S0) [0;1;2;3;4;5;6;7]%nat.

Lemma v8_nth w i: (i < 8)%nat -> nth i (v8 w) S0 = nth i w S0.
Proof. intros H. do 8 (destruct i as [|i]; [reflexivity|]). lia. Qed.

Lemma pfx_none_v8 p w: (List.length p <= 8)%nat -> (pfx p w = None <-> pfx p (v8 w) = None).
Proof.
  intros Hl. rewrite !pfx_none_iff. split; intros [i [Hi Hn]]; exists i; split; auto;
  rewrite v8_nth in *; auto; lia.
Qed.

Lemma find_win1_none ws w:
  find_win1 ws w = None <-> (forall pre post, In (pre,post) ws -> pfx pre w = None).
Proof.
  induction ws as [|[pre post] ws IH]; cbn.
  - split; auto. intros _ ? ? [].
  - destruct (pfx pre w) eqn:E.
    + split; [discriminate|]. intros H. rewrite (H pre post (or_introl eq_refl)) in E. discriminate.
    + rewrite IH. split.
      * intros H p q Hpq. destruct Hpq as [Hpq|Hpq]; [inverts Hpq; exact E|exact (H p q Hpq)].
      * intros H p q Hpq. exact (H p q (or_intror Hpq)).
Qed.

Lemma find_win0_none ws w:
  find_win0 ws w = None <-> (forall pre post ab, In (pre,post,ab) ws -> pfx pre w = None).
Proof.
  induction ws as [|[[pre post] ab] ws IH]; cbn.
  - split; auto. intros _ ? ? ? [].
  - destruct (pfx pre w) eqn:E.
    + split; [discriminate|]. intros H. rewrite (H pre post ab (or_introl eq_refl)) in E. discriminate.
    + rewrite IH. split.
      * intros H p q a Hpq. destruct Hpq as [Hpq|Hpq]; [inverts Hpq; exact E|exact (H p q a Hpq)].
      * intros H p q a Hpq. exact (H p q a (or_intror Hpq)).
Qed.

Lemma win1_len pre post: In (pre,post) win1 -> (List.length pre <= 8)%nat.
Proof. cbn. intros H. repeat destruct H as [H|H]; try contradiction; inverts H; cbn; lia. Qed.
Lemma win0_len pre post ab: In (pre,post,ab) win0 -> (List.length pre <= 8)%nat.
Proof. cbn. intros H. repeat destruct H as [H|H]; try contradiction; inverts H; cbn; lia. Qed.

Lemma find_win1_v8 w: find_win1 win1 w = None <-> find_win1 win1 (v8 w) = None.
Proof.
  rewrite !find_win1_none. split; intros H p q Hin; specialize (H p q Hin);
  [rewrite <-pfx_none_v8|rewrite pfx_none_v8]; eauto using win1_len.
Qed.
Lemma find_win0_v8 w: find_win0 win0 w = None <-> find_win0 win0 (v8 w) = None.
Proof.
  rewrite !find_win0_none. split; intros H p q a Hin; specialize (H p q a Hin);
  [rewrite <-pfx_none_v8|rewrite pfx_none_v8]; eauto using win0_len.
Qed.

Definition isS (o: option (list Sym)) := match o with Some _ => true | None => false end.
Definition t0startb w := isS (pfx [0;0;0;0] w) || isS (pfx [0;1;1;0] w) || isS (pfx [0;0;1;1] w) || isS (pfx [0;1;1;1] w).

Lemma isS_v8 p w: (List.length p <= 8)%nat -> isS (pfx p w) = isS (pfx p (v8 w)).
Proof.
  intros Hl. pose proof (pfx_none_v8 p w Hl) as H.
  destruct (pfx p w), (pfx p (v8 w)); cbn; auto.
  - destruct H as [_ H]. specialize (H eq_refl). discriminate.
  - destruct H as [H _]. specialize (H eq_refl). discriminate.
Qed.

Lemma same4_pfx p a b: (List.length p <= 4)%nat ->
  (forall i, (i < 4)%nat -> nth i a S0 = nth i b S0) -> isS (pfx p a) = isS (pfx p b).
Proof.
  intros Hl Hs.
  assert (Hiff: pfx p a = None <-> pfx p b = None).
  { rewrite !pfx_none_iff. split; intros [i [Hi Hn]]; exists i; split; auto;
    [rewrite <-Hs|rewrite Hs]; auto; lia. }
  destruct (pfx p a), (pfx p b); cbn; auto.
  - destruct Hiff as [_ H]. specialize (H eq_refl). discriminate.
  - destruct Hiff as [H _]. specialize (H eq_refl). discriminate.
Qed.

Lemma t0startb_same4 a b: (forall i, (i < 4)%nat -> nth i a S0 = nth i b S0) -> t0startb a = t0startb b.
Proof.
  intros Hs. unfold t0startb.
  rewrite (same4_pfx [0;0;0;0] a b), (same4_pfx [0;1;1;0] a b), (same4_pfx [0;0;1;1] a b),
    (same4_pfx [0;1;1;1] a b); auto.
Qed.

Fixpoint allL (n:nat) : list (list Sym) :=
match n with O => [[]] | S n => flat_map (fun l => [S0::l; S1::l]) (allL n) end.

Lemma allL_in l: In l (allL (List.length l)).
Proof.
  induction l as [|x l IH]; cbn; auto.
  apply in_flat_map. exists l. split; auto. destruct x; cbn; auto.
Qed.

Lemma v8_len w: List.length (v8 w) = 8%nat. Proof. reflexivity. Qed.

(* the finite checks *)
Definition chk1 v :=
  match find_win1 win1 v with
  | Some _ => true
  | None =>
    (match pfx [1;0] v with Some v1 => t0startb v1 | None => true end) &&
    (isS (pfx [1;1] v) || isS (pfx [1;0] v) || isS (pfx [0;0] v))
  end.
Definition chk0 v :=
  match find_win0 win0 v with
  | Some _ => true
  | None => match pfx [0;1;1;0] v with Some v1 => t0startb v1 | None => true end
  end.

Lemma chk_all: forallb chk1 (allL 8) = true /\ forallb chk0 (allL 8) = true.
Proof. vm_compute. split; reflexivity. Qed.

Lemma chk1_w w: chk1 (v8 w) = true.
Proof.
  destruct chk_all as [H _]. rewrite forallb_forall in H. apply H.
  rewrite <-(v8_len w). apply allL_in.
Qed.
Lemma chk0_w w: chk0 (v8 w) = true.
Proof.
  destruct chk_all as [_ H]. rewrite forallb_forall in H. apply H.
  rewrite <-(v8_len w). apply allL_in.
Qed.

Lemma isS_some o: isS o = true -> o <> None. Proof. destruct o; cbn; congruence. Qed.
Lemma isS_none o: isS o = false -> o = None. Proof. destruct o; cbn; congruence. Qed.

Lemma pfx_v8_some p w w1: (List.length p <= 8)%nat -> pfx p w = Some w1 -> exists v1, pfx p (v8 w) = Some v1.
Proof.
  intros Hl E. destruct (pfx p (v8 w)) eqn:E'; eauto.
  apply (pfx_none_v8 p w Hl) in E'. congruence.
Qed.

Lemma key_t0start p w w1 v1: (List.length p + 4 <= 8)%nat ->
  pfx p w = Some w1 -> pfx p (v8 w) = Some v1 -> t0startb w1 = t0startb v1.
Proof.
  intros Hl E1 E2. apply t0startb_same4. intros i Hi.
  rewrite (pfx_some_nth _ _ _ E1), (pfx_some_nth _ _ _ E2), v8_nth; auto. lia.
Qed.

Lemma key1 w w1: find_win1 win1 w = None -> pfx [1;0] w = Some w1 -> t0startb w1 = true.
Proof.
  intros Hw E. pose proof (chk1_w w) as C. unfold chk1 in C.
  rewrite find_win1_v8 in Hw. rewrite Hw in C.
  destruct (pfx_v8_some [1;0] w w1 ltac:(cbn; lia) E) as [v1 Ev].
  rewrite Ev in C. apply andb_prop in C as [C _].
  rewrite (key_t0start [1;0] w w1 v1 ltac:(cbn; lia) E Ev); exact C.
Qed.

Lemma key0 w w1: find_win0 win0 w = None -> pfx [0;1;1;0] w = Some w1 -> t0startb w1 = true.
Proof.
  intros Hw E. pose proof (chk0_w w) as C. unfold chk0 in C.
  rewrite find_win0_v8 in Hw. rewrite Hw in C.
  destruct (pfx_v8_some [0;1;1;0] w w1 ltac:(cbn; lia) E) as [v1 Ev].
  rewrite Ev in C.
  rewrite (key_t0start [0;1;1;0] w w1 v1 ltac:(cbn; lia) E Ev); exact C.
Qed.

Lemma cover1 w: find_win1 win1 w = None ->
  isS (pfx [1;1] w) || isS (pfx [1;0] w) || isS (pfx [0;0] w) = true.
Proof.
  intros Hw. pose proof (chk1_w w) as C. unfold chk1 in C.
  rewrite find_win1_v8 in Hw. rewrite Hw in C.
  apply andb_prop in C as [_ C].
  rewrite (isS_v8 [1;1] w ltac:(cbn; lia)), (isS_v8 [1;0] w ltac:(cbn; lia)), (isS_v8 [0;0] w ltac:(cbn; lia)); exact C.
Qed.

Lemma pfx_cons_len x p y w w1: pfx (x::p) (y::w) = Some w1 -> (List.length w1 <= List.length w)%nat.
Proof. cbn. destruct (sym_eqb x y); [apply pfx_len|discriminate]. Qed.

Lemma carryL_total n: forall w, (List.length w <= n)%nat ->
  (forall T, (n < T)%nat -> carryL T w t1 <> None) /\
  (t0startb w = true -> forall T, (n < T)%nat -> carryL T w t0 <> None).
Proof.
  induction n as [|n IH]; intros w Hl.
  - destruct w; [|cbn in Hl; lia].
    split; [intros T HT|intros _ T HT]; (destruct T as [|T]; [lia|]); cbn; discriminate.
  - destruct w as [|y w'].
    { split; [intros T HT|intros _ T HT]; (destruct T as [|T]; [lia|]); cbn; discriminate. }
    cbn in Hl. assert (Hl': (List.length w' <= n)%nat) by lia.
    split.
    + intros T HT. destruct T as [|T]; [lia|]. cbn[carryL].
      destruct (find_win1 win1 (y::w')) eqn:Ew; [discriminate|].
      destruct (pfx [1;1] (y::w')) as [w1|] eqn:E1.
      { pose proof (pfx_cons_len _ _ _ _ _ E1) as Hw1.
        destruct (IH w1 ltac:(lia)) as [IH1 _].
        specialize (IH1 T ltac:(lia)).
        destruct (carryL T w1 t1) as [[w2 ab]|] eqn:Ec; [|congruence].
        rewrite (carryL_t1 _ _ _ _ Ec). discriminate. }
      destruct (pfx [1;0] (y::w')) as [w1|] eqn:E2.
      { pose proof (pfx_cons_len _ _ _ _ _ E2) as Hw1.
        destruct (IH w1 ltac:(lia)) as [_ IH0].
        specialize (IH0 (key1 _ _ Ew E2) T ltac:(lia)).
        destruct (carryL T w1 t0) as [[w2 [|]]|] eqn:Ec; [discriminate|discriminate|congruence]. }
      destruct (pfx [0;0] (y::w')) eqn:E3; [discriminate|].
      pose proof (cover1 _ Ew) as C. rewrite E1, E2, E3 in C. discriminate.
    + intros Hs T HT. destruct T as [|T]; [lia|]. cbn[carryL].
      destruct (find_win0 win0 (y::w')) as [[? ?]|] eqn:Ew; [discriminate|].
      destruct (pfx [0;1;1;0] (y::w')) as [w1|] eqn:E1.
      { pose proof (pfx_cons_len _ _ _ _ _ E1) as Hw1.
        destruct (IH w1 ltac:(lia)) as [_ IH0].
        specialize (IH0 (key0 _ _ Ew E1) T ltac:(lia)).
        destruct (carryL T w1 t0) as [[w2 [|]]|] eqn:Ec; [discriminate|discriminate|congruence]. }
      destruct (pfx [0;1;1;1] (y::w')) as [w1|] eqn:E2.
      { pose proof (pfx_cons_len _ _ _ _ _ E2) as Hw1.
        destruct (IH w1 ltac:(lia)) as [IH1 _].
        specialize (IH1 T ltac:(lia)).
        destruct (carryL T w1 t1) as [[w2 ab]|] eqn:Ec; [|congruence].
        rewrite (carryL_t1 _ _ _ _ Ec). discriminate. }
      destruct (pfx [0;0;0;0] (y::w')) eqn:E3; [discriminate|].
      destruct (pfx [0;0;1;1] (y::w')) eqn:E4; [discriminate|].
      unfold t0startb in Hs. rewrite E1, E2, E3, E4 in Hs. discriminate.
Qed.

(* So the list machine gets stuck only at a bad overflow. *)
Definition bad x :=
match x with
| LL k b w => b = 0%N /\ pfx [1;0;1] w = None /\ pfx [1;1] w = None /\ pfx [0;0] w = None
| LR _ _ _ => False
end.

Lemma stepL_stuck x: stepL x = None -> bad x.
Proof.
  destruct x as [k b w|k b w]; cbn[stepL bad].
  - destruct (N.eqb_spec b 0); [|discriminate]. subst.
    destruct (pfx [1;0;1] w); [discriminate|].
    destruct (pfx [1;1] w); [discriminate|].
    destruct (pfx [0;0] w); [discriminate|]. auto.
  - destruct (pfx [0] w); [discriminate|].
    destruct (carryL_total (List.length w) w ltac:(lia)) as [H _].
    specialize (H (S (List.length w)) ltac:(lia)).
    destruct (carryL (S (List.length w)) w t1) as [[? ?]|]; [discriminate|congruence].
Qed.

(* The reduction: if the list machine never reaches a bad overflow, the holdout never halts. *)
Lemma iterL_S m x: iterL (S m) x = match iterL m x with Some y => stepL y | None => None end.
Proof.
  revert x. induction m; intros x; cbn; [destruct (stepL x); auto|].
  destruct (stepL x) as [y|]; auto. rewrite <-IHm. reflexivity.
Qed.

Theorem holdout_nonhalt_of_no_bad:
  (forall n x, iterL n startL = Some x -> ~ bad x) -> ~ halts holdout c0.
Proof.
  intros H. apply holdout_nonhalt_of_iterL.
  intros n. induction n as [|n IHn]; [cbn; discriminate|].
  rewrite iterL_S. destruct (iterL n startL) as [x|] eqn:E; [|congruence].
  destruct (stepL x) eqn:E2; [discriminate|].
  apply stepL_stuck in E2. exfalso. exact (H n x E E2).
Qed.

Print Assumptions holdout_nonhalt_of_no_bad.
