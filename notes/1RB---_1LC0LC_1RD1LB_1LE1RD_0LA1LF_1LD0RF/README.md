# Notes: `1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF`

The Busy Beaver problem asks which n-state Turing machines halt when started on a blank tape; the
[bbchallenge](https://bbchallenge.org) community is settling the six-state case with machine-checked proofs, and
about 600 machines are still open. This is a study of one of them (bbchallenge id 130302): it describes the run as a
nested base-4 counter with overflows, and follows it exactly to 10^18 steps with an accelerated simulator.

**Status: open.** Not proved non-halting yet. Proved in Rocq: the block rules, the round of the post-overflow chain
for any unit list (section 4, `rocq/round/`), and that the machine reaches the tape after the second overflow
(`PART3.md`). The rest is checked by simulation (*sim*). Exact simulation shows that the end of the new chain uses up
the band slowly (section 3), so the planned closure argument does not give non-halting (section 6); the overflows
that follow are simulated in section 3b.

| state | read 0 | read 1 |
|---|---|---|
| A | 1RB | --- |
| B | 1LC | 0LC |
| C | 1RD | 1LB |
| D | 1LE | 1RD |
| E | 0LA | 1LF |
| F | 1LD | 0RF |

**Where things stand (short version).**

* *Known before* (busy-beaver-explorer notes on this machine, Nov 2026): the block rules in Lean for all lengths,
  the only way to halt (`1 0 0 0 0 B> 1`: a gap of exactly four 0s), a description of the counter from the run, and
  no halt in 2·10^10 steps. A tracker lists it as a "shift-overflow structural counter" with an accelerated run to
  1.1·10^17 steps.
* *New here*: an exact accelerated simulator (`tools/chainb.c`, checked cell for cell against direct simulation)
  that runs to 10^18 steps in minutes with no halt; the exact digit words of the counter; and the second overflow,
  which takes the head away from the left end from step 1.3689·10^15 to 2.4869·10^15 and leaves a frozen cascade of
  bands and near copies of the old chain.
* *Also new*: a numerical rule for what the overflow does to the top walls, checked on scaled-down restarts, and
  the block rules proved in Rocq (`rocq/M130Rules.v`).
* *Open*: a rule for what an overflow does to the tape in general, and an invariant that survives it. The end of the
  new chain cycles but eats 4 band words per cycle (section 3), so the next overflow does come, after about 282,000
  cycles. Simulated (section 3b): that overflow and about 40 later ones rewrite the first frozen unit by one rule
  (band + 8V/9, wall V/3), until the cascade is used up. The overflow that would build the next cascade (type 2) is
  not simulated yet. No halt seen.

## 1. The counter (*sim*, steps 2·10^8 to 3·10^9)

Sample the tape when the head is at the left end of the visited region in state B (a round start). Write
`W = 111010` (one wall word). Then the tape is

    P  W^a1 D1  W^a2 D2  W^a3 D3 ...  W^ak Dk  T

* `P` is a fixed prefix (103 cells), `T` a tail of about 200 cells at the right end that does not change.
* Each `Di` is a digit word with 4 phases. Unit 1 steps every round, unit `i+1` steps when unit `i` wraps, and each
  wall gains one word every other step of its unit: a base-4 counter. At 3·10^9 the walls hold 9992, 2486, 614,
  113, ... words.
* In deep units the four digit words are exactly `(10)^7`, `(10)^4 1^7 0`, `1^7 0 (10)^5` and `1^7 0 1010 1^7 0`
  (14, 16, 18 and 20 cells).
* Units 1 and 2 carry fixed bodies left over from the start (134 and 150 cells after a short phase head); they
  are unchanged from 2·10^8 to 3·10^9.
* New units are born at the end of the chain, just left of `T`, whenever a carry reaches it; `T` itself is not
  consumed.

## 2. Accelerated simulation (*sim*)

`tools/chainb.c` keeps the tape as runs of 6-cell blocks and carries the block behind the head, so the zigzag of a
pass over a wall stays inside one 12-cell window and a whole wall is crossed in one step. Checked against direct
simulation: identical tape at sampled events (for example step 1,357,659,723). Speed on one core: 3·10^9 steps in
2 s, 10^13 in 4 s, 10^18 in a few minutes. No halt up to 10^18 steps.

## 3. The second overflow (*sim*)

The busy-beaver-explorer notes report a first overflow at about step 1.94·10^8 (a carry out of the last unit that
rebuilt the end of the chain). The second one takes two long trips of the head away from the left end
(skeletons: numbers are runs of one repeated 6-cell block, `[n]` is n other blocks):

    1,368,863,728,438,429  [17] 6769940 [25] 1692473 [28] 423111 [9] 105737 [4] 26433 [12] 6606 [3] 1651 [6] 411 [19] 95 [29] 11 [22] 3 [5]
    -- first trip, 8.4·10^14 steps --
    2,208,844,122,802,475  [24] 5077453 [6] 1269364 [13] 317338 [25] 79325 [3] 19830 [22] 4950 [3] 1237 [11] 3 [8] 302 [3] 74 3 [19] 11
                           [1128287] 423113 [2] 105780 [3] 26444 [38] 3 [8] 6595 ... [282048] 105774 [22] 26435 ... [88070] 3 [40] 33026 ...
    -- a new counter starts at the left end; second trip, 2.8·10^14 steps --
    2,486,893,016,200,431  [1] 83 [5] 22 3 [4513318] 1692485 [14] 423118 [25] 105770 [2] 26442 [22] 6603 3 1650 [22] 405 3 101 [21] 18 [3] 4
                           [1128282] 423113 [2] 105780 ... [282048] 105774 ... [88070] 3 [40] 33026 ... [270] 94 ...

In the first trip the chain shrinks to about 3/4 of its walls (6769940 -> 5077453, 1692473 -> 1269364, ...) and a
cascade is written to its right: a band (the `[1128287]`: about 282,000 copies of the 24-cell word
`110101 011101 010111 010101`), a near copy of the chain from the third wall on (423113, 105780, ...), a band a
quarter as long, a near copy from the fourth wall on, and so on down. In the second trip the shrunken top wall
becomes a band of about 1.13 million copies of the same word, followed by a near copy of the chain from the second
wall on (1692485, 423118, ...). From then on (to 10^18) the cascade stays frozen and the new chain grows; at
10^18 its walls hold 182230022, 45557506, 11389372, ... words (`data/skel_to_1e18.txt.gz`; the round starts every
20,000 rounds to 4·10^15 are in `data/skel_to_4e15.txt.gz`).

**What triggers it** (`data/end_events_to_1.37e15.txt.gz`: the end of the tape, right of the last wall of 40 or
more words, at every round start where it changes; `ENDT=40`). From 2·10^8 to 2.6·10^14 the tape ends in the same
34-block word `T`; units are born just left of it and their walls grow until they leave the region. At step
263,252,731,346,449 `T` itself is rewritten and the tape ends in a wall of 3 words followed by 5 blocks (`3 [5]`).
That ending is still there when the overflow starts at 1.37·10^15: the next carry to pass it reaches the blank tape
at the right end. The event at 1.94·10^8 reported by the busy-beaver-explorer notes is of the same kind (the end
`34 [10] 5 [10]` becomes `3 [17] 15 [33]` within one round), on a much smaller scale.

**The end of the tape before an overflow** (*sim*, `data/end_events_to_1.37e15.txt.gz`,
`data/end_events_scaled_div256.txt.gz`). Read as cells, the end of the old chain is a leftover word whose last ~50
cells never change. From 2·10^8 to 10^13 the part after the last wall stays at 132 to 148 cells while units are
born in front of it; at 5.47·10^14 the end is rewritten once, and from then until the overflow it is a young unit
(its wall growing from 3 to 12 words) followed by the unchanging end. The overflow starts when a carry passes them.
The new chain of the walls-divided-by-256 restart ends the same way before its overflow at top wall 22,418 (a young
unit and the unchanging end `...1011111111101010101111111111111`), and the band next to it is not used up. What
decides when the end reaches this state is not known; in the real run the new chain has not reached it by 10^18
steps.

**The end of the new chain cycles** (*sim*, `data/end_events_new_chain_to_1e18.txt.gz`: the end of the real new chain,
between its last wall of 40 or more words and the band, every 4,096th round start from 2.5·10^15 to 10^18;
`ENDB=40 ENDBEVERY=4096`). With every wall replaced by one symbol, the 1,081 recorded end states take 480 distinct
values, the first repeat comes by 2.8·10^15, and over the last 300 states the sequence is periodic with period 536.
At full resolution (every round start, from the tape at step 2,592,545,302,250,949 to 2.0·10^17;
`data/end_events_new_chain_full_2.59e15_2e17.txt.gz`, which also records the band's length and first blocks) the
end takes 536 distinct shapes with each wall written as its length mod 4 (and the wall before the end region mod 4),
the same number as the period of the sampled run; all 900 shapes sampled later up to 10^18 are among them. 180 of the
shapes occur more than once in the window, and each of them is always followed by the same next shape: the end
behaves as a deterministic system running through a cycle of 536 shapes. The band's edge does not enter it: the
band keeps its length between 4,513,207 and 4,513,230 blocks and its first blocks vary without affecting the shapes.
The end does not reach the young
unit + unchanging end seen before the two overflows. If the cycle is exact, the new chain never overflows; this is
the kind of statement an invariant can carry. Observed on sampled states, not proved. *But see the next paragraph:
the cycle uses up the band.*

**The end region eats the band** (*sim, exact*; `tools/end_period.py`). Cut the tape at a round start into the
regular units of section 6 (U1..U4, then K, D, K, D, ..., any wall of at least 3 words; the words are in
`tools/trips_gen.py`), the end word `E` (from the last regular unit to the band), the band and the frozen cascade.
`E` changes only when every regular unit carries, and then by one trip in the unit interface, so its visits can be
simulated one after another, exactly, without the regular units (the band is kept at a few dozen words: the pass
over it is uniform). Checked against the accelerated run: from the real tape at step 5,269,000,298,949,519, one
visit (the band crossing) gives exactly the end word of the real tape at 5,271,000,331,149,223. From the tape at
step 2,592,545,302,250,949:

* every 72 visits `E` returns exactly to its value at that step;
* in each period a K unit (wall 33 words, visit 13) and a D unit (wall 5 words, visit 21) leave `E` and join the
  regular chain, and one visit (34th) crosses the band and the whole first frozen wall (1,692,491 blocks) and turns
  just after it;
* per period the band's left edge moves 84 cells to the right (the start of `E` moves 72·4 = 288 cells to the left,
  the two new units take 372 cells off its front) and its right edge 12 cells to the left: **the band loses 96
  cells (4 words) per period**. The real run agrees: 1,128,303 band words at 2.59·10^15, 1,128,298 at 10^17, which
  is two periods later (the tape at 10^17 has the end word of visit 94).

So the cycle of end shapes above is real, but the band is not part of an invariant: after about 282,000 periods
(each takes 16 times as many rounds as the one before, since it adds two base-4 units) the end reaches the first
frozen wall, and what happens then is an overflow into the frozen cascade of the kind seen in the scaled-down runs.
With a band of 12 words the same simulation shows the end leaving the cycle once the band is gone.

**A rule for the top walls** (*sim*). In the cascade each of the two top walls of the old chain is replaced by a band
and a fresh chain: a wall of `W` words becomes about `2W/3` blocks of band (`W/6` copies of the 24-cell word)
followed by a chain with walls `W/4, W/16, W/64, ...`:

| wall `W` | band, blocks (`2W/3`) | following chain (`W/4, W/16, W/64`) |
|---|---|---|
| 6,769,940 | 4,513,318 (4,513,293) | 1,692,485, 423,118, 105,770 (1,692,485, 423,121, 105,780) |
| 1,692,473 | 1,128,287 (1,128,315) | 423,113, 105,780, 26,444 (423,118, 105,780, 26,445) |

The same holds when the real tape just before the overflow (`data/pre_overflow_1368863728438429.txt.gz`) is
restarted with every wall divided by 16, 64 or 256 (`tools/mkinit.py`, `INIT=`): with walls divided by 256 the top
wall 26,445 gives a band of 17,614 blocks and the chain 6,611, 1,650, 402, 100, and the next wall 6,611 a band of
4,403 and the chain 1,647, 412, 102. The lower, small walls do not follow it this simply.

**Later rewrites of the cascade** (*sim*, `data/scaled_div*.txt`, `tools/scalefrozen.py`). In the scaled-down runs
the new chain later overflows into the frozen cascade: with walls divided by 16, 256 or 1024, when its top wall
reaches 22,418 words (with walls divided by 16 the new band part sits just after the old band), the first frozen unit (a band of `B` blocks and a chain with top wall `W`) becomes a band of
about `B + 8W/9` blocks and a chain `W/3, W/12, W/48, ...` (for example `B, W` = 17,615, 6,611 -> 23,502 and the
chain 2,201, 540, 134). The rule is the same when the first frozen unit is changed by hand before this happens: the
band and the walls multiplied by 1 or 4 independently (`B, W` = 70,403, 6,611 -> 76,290 and 2,201; 17,615, 26,444
-> 41,131 and 8,804, 2,159, 538), and the wall moved by -3 to +3. So the frozen cascade behaves like the next digits of a nested
counter: each overflow of the level below carries into it by a fixed rule. In the real run the new chain started
differently (its own leftover words differ) and has not overflowed by 10^18 steps.

## 3b. The overflows after the second (*sim*)

Everything in this section is simulation, with `tools/ovr.c` (chainb's core: logs round starts, long trips, and
stops when the first frozen wall changes) and the scripts in `tools/overflow/`. Nothing here is proved.

**Method: drop the regular units.** The end region is visited only when every regular unit carries, and it only
sees the trip interface (section 4, `Trip`; proved for the six known unit types, checked by simulation for the others).
So removing regular units changes only *when* the end is visited, not *what* happens there. That turns 4^n rounds
per end visit into a few rounds:
* `mkmin.py`, `reset2.py`: keep the prefix and unit 1 (wall set to 40 words, phase changed only for 6-cell
  alignment), drop every other segment that is a regular unit, and keep everything else. A segment is a wall of ≥ 3
  words plus the rest up to the next such wall. It counts as a regular unit when `gunit2.py` finds that 4 trips in
  the unit interface bring it back to itself with exactly one carry and the wall 2 words longer. This test also
  accepts unit types not in section 4, and new ones appear after every overflow. Static segments that every trip
  passes unchanged are kept. Walls of kept segments over 200 words are shortened, keeping the residue mod 12.
* The band in front of the first frozen unit is shortened to a few dozen words, keeping its length mod 48 (the pass
  over the band does not depend on its length). The frozen cascade is kept exactly.
* `loop3.sh`/`auto.sh` alternate runs of 2 million rounds with resets and stop when the first frozen wall changes.

Cross-check: README's scaled run (walls ÷256, plain chainb, no dropping) and this method give the same rule below.

**Type 3: the end rewrites the first frozen unit.** At step 2,592,545,302,250,949 the tape is: the active chain
and its end, then frozen units `F1, F2, ...`; each is a band of `b` blocks and a chain of walls `V, ~V/4, ~V/16, ...`
(`F1`: 1,128,303 band words, `V` = 1,692,491; `F2`: 282,063, 423,113; `F3`: 70,506, 105,774; `F4`: 22,011, 33,026;
then smaller pieces and the old end). The end eats the band in front of `F1` (section 3: 4 words per 72 visits;
after the next overflow the end cycles again, with period 1,032 visits and 36 band words per period, and different
unit types). Soon after the band is gone (sometimes with a few band words still left), one long trip
(3·10^13 steps for `V` = 1.7·10^6) rewrites `F1` and nothing else:

    F1 = (band b, chain V, V/4, V/16, ...)   ->   (band b + 8V/9 blocks, chain V/3, V/12, V/48, ...)

The frozen walls (`V` just before each overflow, then `V` after it; `+k`: band words left over from before):

| frozen unit | walls, one overflow after another |
|---|---|
| F1 | 1,692,490 → 564,162 → 188,045 → 62,681 → 20,888 → 6,959 (+23) → 2,313 → 772 (+30) → 250 → 81 (+17) → 21 |
| F2 | 423,114 → 141,040 (+32) → 47,014 → 15,661 → 5,223 → 1,735 → 579 (+25) → 186 → 60 → 13 |
| F3 | 105,774 → 35,250 → 11,749 → 3,912 → 1,299 → 427 → 139 → 41 → 8 |
| F4 | 33,026 → 10,996 → 3,660 (+42), then the rest of the cascade goes at once |

New band (blocks) against `8V/9`: 1,504,432 / 1,504,436; 501,468 / 501,473; 167,144 / 167,151; 55,712 / 55,716;
376,108 / 376,101 (`F2`); 94,016 / 94,021 (`F3`); 29,348 / 29,356 (`F4`). The new wall against `V/3`: 564,162 /
564,163; 188,045 / 188,052; 141,040 / 141,038; 35,250 / 35,258; 10,996 / 11,009. So the rule holds within about
10 blocks for `V` from 1.7·10^6 down to about 1,000, on four different frozen units. Below about 150 words it
drifts (60 → 13 instead of 20). When `F_k`'s wall is down to about 20 words, the next overflow takes the rest of
`F_k` and the end goes on to `F_{k+1}`. The mass is conserved: a chain `V, V/4, ...` is 4V/3 blocks, and
`8V/9 + 4(V/3)/3 = 4V/3`. In about 40 simulated overflows of this kind no halt occurred (`ovr` stops on the
halting transition). Data: `data/overflows_sim.txt`.

**After the cascade.** When all frozen units are used up, the end lies against the blank tape behind the leftover
end word of the old chain (`... 70 [28] 3 [53]` at step 2.59·10^15). There it starts a new counter: units with
walls in ratio 4 are born in front of a fixed right end. That is the situation of the first chain between the
first and the second overflow (section 3: units born just left of the fixed end word `T`). There, the next event
was the second overflow (type 2), which turned the whole active chain into the cascade: top wall `W1` into a band
of about `2W1/3` blocks, then each wall `W_k` into a band of `2W_k/3` blocks followed by a near copy of the chain
from `W_{k+1}` on (section 3). **Not simulated yet**: dropping regular units destroys the active chain that a type-2
overflow turns into the next cascade. A faithful test needs the active chain rebuilt (the dropped units in birth
order with realistic walls) before the type-2 overflow.

**The first overflow** (step 193,820,039) is a small event of a third kind: the walls 2,517, 617, 147 are untouched
and only the end `34 [10] 5 [10]` becomes `3 [17] 15 [33]`. It is like the end rewrite at step 2.63·10^14
(section 3), not a cascade.

**Candidate rule (not verified).** At the start of an epoch the tape is a fresh chain, its end, a cascade
`F1, ..., Fn` with `F_k = (band ~2W_k/3, chain W_{k+1}, W_{k+2}, ...)` made from the previous chain's walls
`W_1, W_2, ...`, and a leftover end word. During the epoch type-3 overflows use up the cascade one frozen unit at a
time, wall `V -> V/3` per overflow, about log_3 V overflows per unit. Then the end reaches the blank tape and, as
after the first overflow, the chain grows in front of a fixed end until a type-2 overflow turns it into the next
cascade, with much larger walls. If the type-2 step repeats, every overflow maps the tape to the same shapes with
larger numbers. The type-3 step is checked across scales (table). The type-2 step is seen once (the second
overflow, and its scaled restarts in section 3) and has not been seen to repeat. The small-wall end of each frozen
unit (below ~150 words) does not follow the formula exactly.

## 4. Rocq

`rocq/M130Rules.v` restates the block rules of the busy-beaver-explorer notes in busycoq and proves them for all
lengths (the 15 rules, among them the only way to the halting transition, and the moves of D and F over a run of
1s), all by busycoq's symbolic execution, and builds the round through a deep unit on them:

* `wall_pass`: the pass to the right over a wall of any length (each wall word is rewritten in 22 steps as the head
  moves 6 cells);
* `digit_bounce_a/b/c`: the three phases of a deep digit that turn the head back, and `digit_carry`, the phase that
  carries on to the next wall (digit words as found at step 10^11 in the deepest units);
* `unit_round_a/b/c`: a whole round through a deep unit with a wall of any length: pass, turn back, sweep back
  (`wall_l`); `unit_carry`: pass and carry into the next unit.

* `u1_case*`, `u2_case*` and their `_round` versions: the same for the first two units of the chain that starts
  after the second overflow, whose digits are followed by fixed leftover words (generated by `tools/genlemmas.py` from
  the configurations `tools/ctx300.c` finds at the end of each wall, then proved by `es`).

* `prefix_turn` and `round_close`: the left end of the post-overflow chain. A round starts with the head in state C
  on the blank cell left of a 14-cell prefix; `prefix_turn` (18 steps) takes it into the first wall in the form
  `wall_pass` starts from, and `round_close` (31 steps, touching only the prefix) takes the sweep that `wall_l`
  brings back over the first wall to the next round start; the wall words are read with a shift of one cell.
* `round_u1_0`: a whole round, round start to round start, when unit 1 is in phase 0 of its leftover body and turns
  back: the first wall goes from n+1 to n+2 words and the digit word `0101010` becomes `11110`. It is composed from
  `prefix_turn`, `u1_case0_round` and `round_close`, so the pieces fit together.

`rocq/units/Units.v`: the walls and the segments between them in the post-overflow chain, one lemma per kind of
event, 39 lemmas proved by `es`. Every wall the rightward pass finishes is followed by a fixed segment, and what the
pass does there is one of: turn back (*bounce*, ready for `wall_l`), carry on to the next wall (*carry*, in the
form `wall_pass` starts from), and, on the way back after a carry, cross the carried segment to the wall's left end
(*sweep*, ready for `wall_l`; the head never reads past the first word of the next wall). Counting walls from the
left, the "real" units (walls 1, 3, 6, 8, 18, 23, 24, 29, 30, ...) have two bounce statements and one carry
statement; the short walls inside the leftover segments only ever carry. Found from 1,000 round starts sampled from
the exact run between steps 2.59·10^15 and 3·10^16 (walls shortened to 30 or 31 words, which changes nothing at the
ends of the walls): 458,000 wall ends giving 53 bounce or carry statements and 34 sweeps, 39 distinct
(`tools/units_ctx3.py`, `units_gen3.py`, `units_sweep.py`, `units_emit.py`).

* `enter_D`, `enter_D2`, `trip_D0`, `trip_D1`, `trip_D2`: the cut-form interface for units: a unit is entered in
  state D on its first cell with `11` to the left; `trip_Dp` is a whole trip through a deep unit in phase `Dp` that
  turns back (any wall of at least 3 words), from entry to the last exit (state C on the cell left of the unit),
  composed from the entry lemma and `unit_round_a/b/c`. `trip_D3` is the carrying phase: it takes the next unit's
  trip (any unit with the same entry and exit interface) as a hypothesis, so trips nest; pieces `carry_A` (pass to
  the next unit's first cell) and `carry_B` (sweep back to the wall). With these four, a whole round through a run
  of deep units follows by induction over the units.
* `tripU_D0` ... `tripU_D3`: the same four trips in one uniform form. A deep unit is `Wd *> Wd^^m *> Dg p`
  (wall of m+1 words `Wd = 011101`, digit head `Dg p`). Entered in state D with `11` to the left, it is left for the
  last time in state C with `[1;0;1] *> Wd^^m' *> Dg p'` to the right of the head, which is the cut form of the next
  phase once the left neighbour supplies its `0111`: `D0 -> D2`, `D1 -> D3` (same m), `D2 -> D1`, `D3 -> D0`
  (m + 1), and `tripU_D3` takes the next unit's trip in the same form as hypothesis. This is the counter rule of
  section 6 for deep units, now proved (`recut_D0` ... `recut_D3` are the tape identities).

69 lemmas, closed under the global context (no axioms), among them `band_pass`: the pass to the right over the
band of any length (one 24-cell word every 228 steps).

`rocq/round/Trips.v` (generated by `tools/trips_gen.py`, about 6 minutes) and `rocq/round/Round.v`: **[proved]**
the round as a whole, by induction over the units.

* `Trip u v` (`forall l, l <* [1;1] {{D}}> u -->* l <* [0] {{C}}> [1;0;1] *> v`) is the unit interface; `seg t p`
  is the digit head of phase `p` followed by the fixed tail of type `t` (`TU1`..`TU4`, `TK`, `TD`; words in
  `tools/trips_gen.py`). `tripU_<t>_<p>` (24 lemmas): for every type and phase, a unit `Wd *> Wd^^(S (S m)) *> seg t p`
  (any wall of at least 3 words) followed by anything; phases 0, 1, 2 turn back and need nothing of the next unit
  (the trip never reads past the unit), phase 3 carries and takes the next trip as hypothesis. Each is composed from
  `enter_D`, `wall_pass`, one or two pieces proved by `es` (found by simulation in `trips_gen.py`, which also checks
  the re-cut), `wall_regroup`, `wall_l` and three steps. The D-type lemmas no longer need the next unit's wall.
* `vt us E` writes a list of units `(t, p, m)` in cut form before the rest of the tape `E`; `step us` is the
  counter (first unit steps; phase 3 carries into the next unit, wall +1 on `2 -> 1` and `3 -> 0`). `chain_trip`:
  `Trip (Wd *> vt us E) (vt (step us) E*)`, by induction over `us`, where `E* = E` unless every unit carries, and
  then the trip into the end (`Trip (Wd *> E) E'`) is a hypothesis.
* `round`: `RS (vt us E) -->+ RS (vt (step us) E*)` with `RS v = const 0 {{C}}> [0;1;1;1;1;1;1;1;1] *> Wd *> v`
  (`prefix_in`, 9 steps; `prefix_out`, 28 steps). Closed under the global context.

So the chain left of the end is proved to be an exact counter for any wall lengths and any unit types in this
list; what remains is the end (section 6).

`rocq/end/E000.v` ... `E053.v`: the end of the post-overflow chain, one lemma per transition. Inside the end region all
walls are shorter than 40 words, so it has finitely many exact states (536, wall lengths included); every time a
pass carries past the chain's last big wall, the end region goes from one of them to the next. `chainb` with `XEND=1`
records the configuration at that moment (713 times from the tape at step 2,592,545,302,250,949 to 2·10^17, 535
distinct, `data/end_entries_2.59e15_2e17.txt.gz`); `tools/xlemma.py` simulates each one until the head leaves the end
region to the left and states it as a lemma over the cells the head visits (the rest of the tape, including the big
walls on the left, is arbitrary), and `es` proves it. 534 lemmas, all proved (`tools/xbatch.py`, `tools/xcompile.sh`,
about 25 minutes on 4 cores). The remaining transition (at step 5,269,793,291,944,956, the only one of its kind
to 2·10^17) is different: the carry runs through the whole band (about 4.5 million blocks) to the first frozen
wall and back. Comparing the tape at the round starts just before and after it, the band ends up shifted (its
blocks are rotated by 2 cells), the first frozen wall's leading cells change, and the 1.5 million runs of the
frozen cascade beyond it are unchanged. A proof needs one more lemma for it: the pass over the band, which is a
periodic 24-cell word, so a shift rule like `wall_pass` (proved: `band_pass`).

Not formalized yet: the rounds for the other phases and carries composed the same way, the link between these pieces (the invariant), and reaching the second overflow.

## 5. Automatic deciders (negative)

From the configuration at step 2·10^8 (busycoq's `CPS_LRU` and `RWL_mod` take a simulation prefix), with
mxdys's FAR (`ccz181078/TM`): `RWL_mod`, 360 parameter sets, and `CPS_LRU`, 880 parameter sets at
`maxT = 10^6` and 165 at `10^7` (block sizes 1 to 24): no certificate. The leftover words in the first units and
the cascade are the likely reason: no small set of local patterns describes them.

## 6. What a proof would need

The observations suggested a two-part proof: the machine reaches the tape after the second overflow, and from there
it never overflows again, because the end of the new chain cycles. **This plan cannot be completed as stated**: the
end cycle consumes the band (section 3, *The end region eats the band*), so a family "regular chain + end in its
cycle + band of any length + fixed cascade" is not closed. Following it gives at most a proof that the machine does
not halt for the next ~282,000 end periods. A non-halting proof also has to describe what happens when the band runs
out (an overflow into the frozen cascade) and every later overflow, i.e. an invariant for the nested counter as a
whole. The plan below is kept for the parts that remain useful (the regular chain is now proved, `rocq/round/`).

1. *From the second overflow on (an invariant), at round starts.* A tape of the form

       prefix, units 1 and 2 (phase + fixed leftover word, wall n1, n2), deep units (wall n_i, phase p_i),
       the last wall of >= 40 words, the end region in one of its 536 states, the band (any length), the cascade

   with the walls n_i symbolic. One round is: the pass from the left end into unit 1; for each unit either
   `unit_round_*` (turn back) or `unit_carry` (carry on); when the carry passes the last big wall, one of the
   534 lemmas in `rocq/end/` (or the band pass, `band_pass`, for the one transition that crosses the band); the sweep
   back to the left end (`wall_l` over each wall). Done: the block rules, `wall_pass`, `wall_l`, `band_pass`, the
   rounds and carries of deep units and of units 1 and 2, and the 534 end transitions. Also done: the turn at the left end (`prefix_turn`, `round_close`)
   and one whole round composed from the pieces (`round_u1_0`); the bounce, carry and sweep lemmas for every wall of
   the chain left of the end region (`rocq/units/`). To do: compose them into rounds by induction over the walls; the band-crossing transition's two ends (entering the band, turning at the
   first frozen wall); the bookkeeping that turns the tape after a round back into the round-start form (each unit's
   wall grows by one word every other step of its phase, section 1); a wall leaving the end region when it reaches
   40 words; and the closure argument (`progress_nonhalt` over this family). The halting pattern
   `1 0 0 0 0 B> 1` does not occur in any of the lemmas' configurations.
   *The units of the post-overflow chain (sim).* At a round start, cut the tape at every run of at least four words
   `011101`. Each piece is a wall `(011101)^k` followed by a segment, and every segment is one of four digit heads
   followed by a fixed tail of its unit's type. The heads are the deep digit words `D0 = (01)^7`,
   `D1 = (01)^5 1^6`, `D2 = 01^7 (01)^5`, `D3 = 01^7 (01)^3 1^6` (14, 16, 18, 20 cells). A unit steps
   `D0 -> D2 -> D1 -> D3 -> D0`, its wall gains one word on `D2 -> D1` and on `D3 -> D0`, and on `D3 -> D0` it
   carries into the next unit. Types from the left: four units with their own tails (`U1` to `U4`; tails of 94, 62
   and 302 cells for `U2` to `U4`, `U1`'s cycle has the same shape with its own heads), then `K D K D ...`, where
   `K` has a 116-cell tail and `D` has none; then the end region. Checked on 1,000 sampled round starts and on 70
   consecutive rounds. Each unit is entered and left the same way: the pass steps onto the unit's first cell in
   state D with eight 1s to its left, and the last time it leaves to the left it is in state C with `1111101` to the
   left of the unit and the unit's first cell 0. This gives a uniform interface for a per-unit round-trip lemma and
   an induction over the units (a carrying unit's lemma takes the next unit's round trip as a hypothesis). The cut
   points move by a few cells per step, so the induction also needs the rewriting of each unit's new content into
   the cut form above.
   *The round map in this form (sim, exact).* Write the tape at a round start as the prefix followed by units
   `W^k D T` (wall, digit head, the unit's fixed tail). Then one round is exactly: unit 1 steps; unit `j+1` steps
   when unit `j` goes `D3 -> D0`; a unit that steps goes to the next phase, and its wall gains one word on
   `D2 -> D1` and `D3 -> D0`; nothing else changes. Unit 1 has its own four heads (32, 36, 34, 38 cells, same
   cycle and wall rule). Checked on 10,000 consecutive rounds (2,000 each from five sampled round starts between
   2.59·10^15 and 3·10^16, walls shortened to 30 or 31 words), about 84,000 unit steps, no exception
   (`tools/units_rsc.c`: direct simulation printing round starts; `tools/units_model.py`: the check). So the tape
   at round starts is a plain counter: no tails move, and the cut points move only because walls grow.
2. *Reaching that tape.* **Done** (`PART3.md`, `rocq/p3/`): a verified block simulator run by `vm_compute` proves that the blank tape reaches the round start at step 2,592,545,302,250,949 (1.81·10^9 macro steps, about 15 minutes to check). The text below is the earlier plan. The second overflow is at step 1.4·10^15, far beyond step-by-step computation in Rocq. It
   needs the first chain as an accelerated counter (rounds skipped arithmetically), its end process up to the
   overflow, and the overflow itself (the cascade rule for the top walls, section 3). This is the larger part.

The end cycle is observed for the transitions that occur to 2·10^17, and the exact simulation of section 3 shows it
repeating with period 72 end visits while the band shrinks; a closure argument over a family with a fixed band
fails for that reason.

## 7. Reproduce

```bash
cd notes/1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF/tools
gcc -O2 -o chainb chainb.c && gcc -O2 -o dump dump.c && gcc -O2 -o samp samp.c
SKEL=1 ./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 4e15 -20000 skel.txt        # the overflow (seconds)
ENDT=40 ./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 1.3689e15 -100000000000 - > end.txt   # end of the tape
SKEL=1 ./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 2.487e15 -1 - | awk '$1>1.3e15 {if ($1-p>1e10) {print pl; print} p=$1; pl=$0}'   # the two trips
./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 1e18 3000000 e18.txt                # to 10^18 (large output)
./samp 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 200000000 260000000 1 ev.txt && python3 units.py ev.txt   # section 1
./dump 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 1357659723 d.txt                       # direct tape, for checks
zcat ../data/pre_overflow_1368863728438429.txt.gz > pre.txt && python3 mkinit.py pre.txt v256.txt 'max(n//256, 3)'
./ovtrips.sh v256.txt 1e15 t256.txt                                                       # scaled-down overflow
gcc -O2 -o p3_count p3_count.c && DUMP=init26.txt ./p3_count 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 2592545302250949
python3 end_period.py init26.txt 30 150 150                                             # the end period (minutes)
cd overflow && gcc -O2 -o ovr ../ovr.c                                                    # section 3b
python3 mkmin.py ../init26.txt min15.txt 15 1 40                                          # unit 1 only, band 15 words
TRIPMIN=1e18 MARKER=1692491 MAXR=1e10 DUMP=ov3_ ./ovr min15.txt > ov3.log                             # to overflow 3 (minutes)
./auto.sh ov3_00.txt A 40 > auto.log                                                      # the overflows after it (hours)
```

Rocq (Coq 8.20.1; after `make` in `verify/`):

```bash
cd notes/1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF/rocq && coqc $(cat _CoqProject) M130Rules.v
```

Analysis by messerdsp, with Claude Opus 5.5.
