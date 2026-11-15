# Notes: `1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA`

The Busy Beaver problem asks which n-state Turing machines halt when started on a blank tape; the [bbchallenge](https://bbchallenge.org) community is settling the six-state case with machine-checked proofs, and about 600 machines are still open. This is a study of one of them: it reduces the machine to a timer-and-counter system, proves that reduction in the Rocq proof assistant, and uses fast exact simulation (C, with a Python reference) to test the one statement left open.

BB(6) holdout (on the 608 list of 30 Oct 2026; spreadsheet class *Sync bouncer counter*).
**Status: open.** No proof here: analysis notes, tools to reproduce them, and a Rocq reduction (`rocq/`,
section 6): the holdout does not halt if an explicit list machine never reaches a "bad overflow".
Everything below marked *(sim)* was checked by direct simulation; apart from the Rocq files, nothing here is proved.

**Where things stand (short version).**

* *Proved in Rocq* (`rocq/`, only the framework's `functional_extensionality_dep`): the timer and counter lemmas of
  `SBCv9.v` ported to this machine (`a` odd), every carry sweep as a lemma (30 stop windows, an abnormal return mode,
  digit and absorb lemmas), the carry total on every word, and `holdout_nonhalt_of_no_bad`: if the list machine
  `stepL` started from `LL 5 5 [1;0]` never reaches `b = 0` with a word that starts with none of `101`, `11`, `00`,
  then `~ halts holdout c0`.
* *Checked by simulation*: the real run (and the exact models of it) to phase 29,438 with no bad overflow, and the
  low end predicted to phase 1,011,350 (and the phase of the next excursion, 1,402,241); at every excursion the run next to the bottom is long (hundreds or more
  after the first few hundred phases).
* *Open*: the global statement. A bad overflow needs a short run (in the one tested pattern, `A` even, `B` odd, `C`
  odd and `D = 3`) next to the bottom at an excursion. Run lengths come out of a deterministic but pseudo-random
  wave process, and with a random counter the model hits a bad overflow within 80 phases every time. No invariant
  is known; heuristically a halt is very unlikely.

**Picking this up.**

* *The open statement*, exactly: `holdout_nonhalt_of_iterL` (`rocq/M9List.v`) reduces non-halting to
  `forall n, iterL n startL <> None` for the list machine `stepL` with `startL := LL 5 5 [1;0]`, and
  `holdout_nonhalt_of_no_bad` (`rocq/M9Total.v`) to "no reachable `x` is `bad`". A proof of that, or
  an `m` where it fails (then the machine halts and the proof is a computation, as for TM2 in `verify/SBCv9.v`),
  settles the holdout.
* *Read first*: "Where things stand" above, then section 6 (phases, waves, excursions, the halt route) and
  section 4 (what failed).
* *Tools*: `phase_sim/lowsim_c.c` (C, about 70x the Python; `NOFILL=1` with a huge `N` runs the exact full tape),
  `fullmodel.py` / `lineage.py` (the 13-rule model with run ids), `haltgrid2.py` / `routeone.py` (what a short run at
  an excursion does). Exact tapes: `phase_sim/data/state{10000,14700,15000,20000}.txt.gz`.
* *Ideas not yet tried*: an exact transducer for one wave pass (section 6 lists the cases found so far) and a search
  for a property of the runs next to the bottom that every wave and excursion preserves; a run-length version of
  the exact simulator (each sweep replaced by the proved carry rule) to get exact tapes at phase 10^5 to 10^6 and
  so a longer predicted horizon.

| state | read 0 | read 1 |
|---|---|---|
| A | 1RB | 0LF |
| B | 1RC | 1RB |
| C | 0RD | 0RC |
| D | 1LE | 1LF |
| E | 1LD | --- |
| F | 0LB | 1LA |

## 1. How it can halt

`E` on a 1 is the only halt, and `E` is entered only by `D0 -> 1LE`. Working backwards:

* Leftward over 0s, `D` and `E` alternate and fill the zeros with 1s (`D0 -> 1LE`, `E0 -> 1LD`).
  The fill halts iff `E` (not `D`) reaches the 1 that ends the zero run.
* A fill starts only after `C0 -> 0RD` with `D` reading 0. `C` comes from `B0 -> 1RC` and
  erases the 1s it crosses (`C1 -> 0RC`).

So the machine halts iff it reaches **`B> 0 1^r 0 0` with `r` odd**.
`B` writes a 1, `C` erases `1^r`, and the fill over the `r+1` zeros puts `E` on `B`'s 1.

*(sim, 10^9 steps; `tools/bstat.c`)* At every "B reads 0" event, `r` is 0 or 1 mod 4, never 2 or 3.
When `r` is odd (so `r = 1 mod 4`) the following cells are always `0 1`, never `0 0`.

## 2. Sweeps and phases

**Sample point:** state `C` reading 0 at the right end of the visited tape. At every sample the tape is
`0^inf W 1^K 0^Z C> 0^inf` *(sim)*.

* One sweep (sample to next sample): `Z += 4`, and `K` decreases by 1 and 3 alternately.
  The only exceptions *(sim)* are right after a phase start, when the last run of `W` is
  absorbed into `K`.
* Sweep mechanics, leftward then rightward:
  * leftward: the `D/E` fill turns `0^Z` back into 1s; the `F/A` pass turns `11` into `01`
    pairs (`F1 -> 1LA`, `A1 -> 0LF`);
  * rightward: a zigzag restores the pairs (10 steps per pair); `C` erases the end (`C1 -> 0RC`).
* **Phases.** When `K` reaches 2, the next sample has `K' = Z + 6`, `Z' = 0`.
  * Phase-start values of `K`: 838, 1678, 3358, 6718, 13446, 26894, 53790.
  * The rule is `K' = 2K + 2`, except once: 6718 -> 13446 is `+10` (that phase had 3361 sweeps
    instead of 3358). Right after some phase starts the last runs of `W` are absorbed into `K`
    (K goes up instead of down); that is the likely cause, but it was not worked out exactly.

Let `W = X 1^m 0^c` (`X` = counter, `1^m` = a block). Every 8 sweeps the right end runs through
this cycle, with `(c, K mod 8)` in `{(4,2), (3,1), (3,6), (2,5)}`:

```
P 0^a     1^m     0^4    (K = 2 mod 8)
P 0^a     1^m     0^3    (1)
P 0^a     1^(m+1) 0^3    (6)
P 0^a     1^(m+1) 0^2    (5)   deep sweep: F/A pass crosses the block, A writes a 1 left of it
P 0^(a-1) 1^(m+1) 0^4    (2)
P 0^(a-1) 1^(m+1) 0^3    (1)
P 0^(a-1) 1^(m+2) 0^3    (6)
P 0^(a-1) 1^(m+2) 0^2    (5)   deep sweep: F reaches the 0 left of the block -> carry into P
P'        1^m     0^4    (2)
```

## 3. The counter

`tools/sbc9.py count` applies the 8-sweep step `F` to any word `X`. It reproduces the direct run
exactly *(sim, `sbc9.py check`)*. The block stays at `m = 30` within a phase.

**Carry mechanics** (leftward pass in `F`/`A`):

| the pass meets | result |
|---|---|
| `11` | becomes `01`, pass continues |
| `00` (with `F`) | becomes `11` (via `F0 -> 0LB`, `B0 -> 1RC`, `C0 -> 0RD`, `D0`, `E0`); pass continues |
| `A` on a 0 | writes 1, carry stops |
| `F` on `10` | carry stops |

The return zigzag then repairs the pairs.

**Early encoding.** From a small start (`X = 1^2 0^10`), at every 8th step
`X = 1^2 D 0^3 1^4 0^8`. Here `D` is a word over the digits
`0 = 0000` and `1 = 0011`, and it advances by the shortlex successor
(`[]`, `[0]`, `[1]`, `[00]`, `[01]`, `[10]`, `[11]`, `[000]`, ...): bijective base 2.
The low 3 bits sit in the tail `0^3 1^{4,5,6} 0^{7,8}` / `... 1^2 0^3`.

**Late encoding** (phase 26894, `X = 1^2 0^7 1^13 0^3 1^11 0^3 1^9 0^3 1^3 0^3`, `m = 26`):
the digits are groups `0^z 1^y` with `z` in {2,3,4}, and each step moves one group
boundary by one cell. Long 1-runs like `1^13` are ordinary digits here.

## 4. Why this is hard (negative results)

**Automatic tools** (all failed):

* busycoq `Inductive` decider (`make decider`): default and `--arithseq` gave no answer within
  300 s each (an `--exploop` run was stopped early).
* mxdys's FAR (`ccz181078/TM`, branch `FAR`):
  * CPS_LRU and RWL_mod: block sizes up to 30, `maxT` up to 1e8, 3060 tasks;
  * RNGS_mod: 2880 tasks.
* Blanchard's FAR (`bbchallenge-deciders`, patched to 6 states): a run with direct up to depth 6
  and mitm_dfa up to depth 14 found nothing before it was stopped (it did not finish).

**Stress tests** (`sbc9.sweep` on hand-made tapes `X 1^m 0^c 1^K 0^Z` in the good classes above,
160–200 sweeps, several phase changes):

* random `X`: 27 of 180 runs halt (about 15%);
* well-formed `X = 1^2 (0^{2..4} 1^{>=2})* 0^{2..4}`: 15 of 150 halt (about 10%);
* the same with `Z = 0` (a clean phase start): 21 of 150 halt (about 14%).

So safety seems to depend on the exact relation between the counter's value, `K` and `m` at each
phase change: the "sync" of a sync bouncer counter. No regular-language (CTL) invariant was found;
my guess (not a result) is that none exists.

**A proof would need:**

1. sweep lemmas (`es`) for the 8-sweep cycle with general `P`;
2. the counter step for both digit encodings, including carries through long 1-runs;
3. the exact phase arithmetic, including the absorption events that cause the `+10`;
4. an invariant tying them together.

`verify/SBCv13.v` (lemma `round`, `n+2 = 2^k*4`) is the closest template.

## 5. Related work

Dennis Koshta's notes (Oct 2026) on the same machine go further than these:
`DennisKoshta/denniskoshta-portfolio`, folder
`public/busy-beaver/machines/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/`
(`status.json`, `decision.json`). From his summary:

* The machine is a mirror twin of `verify/SBCv9.v` Module TM2 (`1RB0RF_0LC---_1LD1LC_0LE0LD_1RE1RF_0RC1RA`),
  which is proved to **halt**. Both follow the same macro run; TM2 halts at its 374th overflow,
  and this machine survives that point.
* TM2's left lemmas hold here exactly when `a` is odd, and `a = 3 mod 4` along the orbit.
* An exact jump simulator followed the real orbit to phase 1,857 with no halt.
* What is missing is a rule for the "merge wave" (his status: stuck, parked 2026-10-11).

The most promising route to a proof is therefore to port `SBCv9.v` and add an invariant for the
merge wave, not to start from scratch.

## 6. Phase-level simulation (Nov 2026)

`phase_sim/` follows the real run phase by phase, using the macro steps of the upstream halting proof for the
twin (`verify/SBCv9.v`, Module TM2) instead of new ones.

**The representation.** Mirror this machine and rename its states A..F to A, C, D, E, G, F. The result is TM2
except at two places: `A0` (TM2 needs 3 steps, and halts if the cell beyond is 1; here 1 step, no halt) and the
`E` walk over 0s (TM2 stays in E; here E and G alternate, and G on a 1 halts). A configuration is
`LC a b {{{(hL',L)}}} r` or `LC a b {{{(hR',R)}}} r`: a timer `0^inf 1^a (10)^b` left of the head and a counter
word `r` right of it. `phase_sim/msim.py` is a line-by-line port of TM2's `mstep`: the timer lemmas `LInc`,
`LIncs`, `LOv`, `LRst_101`, `LRst_11`, the counter arithmetic `rest` / `RIncs` (the word read as a binary number:
4-cell digits `0000` = 0, `0110` = 1, `0011` / `0111` switch to 2-cell digits `00` = 0, `10` = 1, with `11` pairs
skipped), and a direct simulation for each `sweep` (`sideRLs_c` with `hR' -> hL'`). The sweeps run this machine's
own table.

**Checks.**

* On TM2 the port reproduces the upstream run exactly: 12,417 macro steps, 374 overflows, `a` of 373 bits,
  `b` of 378 bits, then TM2 halts inside a sweep (`B` reading 1), as in `SBCv9.v`.
* The timer lemmas, brute-forced on this machine for `a <= 15`, `b <= 5`: they hold exactly when `a` is odd,
  and the machine halts when `a` is even (Koshta found the same). `RIncs` against `k` single sweeps on random
  digit words: 2,669 / 2,669 equal.
* From the blank tape this machine reaches the same start `LC 11 5 {{{(hL',L)}}} [1;0]` (step 301).
* The phase lengths `b + 1` after each overflow are 418, 838, 1678, 3358, 6722, 13446, ..., the block lengths
  seen in direct simulation (6,722 = 6,718 + 4 at the absorption phase).

**What it shows.**

* `a = 3 (mod 4)` always: every overflow sets `a := 3` and every other step adds 4. So the timer side cannot
  halt, and **a halt can only happen inside a sweep over the counter word `r`**.
* At a phase start `r` is a list of runs of 1s separated by `000`. Each phase changes it in three places only:
  the bottom run loses one cell; a few waves change a few runs each; the top, where the counter writes new runs.
  Everything else is frozen.
* The lowest wave sits exactly where the digit parse (`rest`) stops: below it every `000 1^n` reads as two
  counter digits; above it are old runs. The wave moves up about one run per two phases. In one cycle
  `z3 X z3 Y -> z4 (X-2) z3 (Y+1) -> z3 (X-1) z3 (Y-1) ...`; at some runs it makes a gap of 2 and the two runs
  merge next phase (for example `155 z2 216 -> 373`). The exact rule is not worked out.
* **Excursions:** when the bottom run reaches 2, the next run becomes the bottom after a merge cascade. That is
  safe when the next run is long; a short one (about 4 or less) would put the run off sync, and then it halts.

**The real run, followed to phase 10,000 with no halt.** Excursions (phase, run above the bottom, new bottom
after the cascade):

| phase | run above the bottom | new bottom |
|---|---|---|
| 91 | 14 | 24 (phase 95) |
| 119 | 77 | 93 (phase 122) |
| 215 | 93 | 269 (phase 218) |
| 487 | 700 | 2824 (phase 497) |
| 3,321 | 555 | 1542 (phase 3324) |
| 4,866 | 102 | 302 (phase 4870) |
| 5,172 | 1052 | 2498 (phase 5177) |
| 7,675 | 3596 | 6930 (phase 7680) |

("new bottom" is the bottom run when it starts losing one cell per phase again.)

Phases 91 to 487 agree with Koshta's direct follow. 3,321, 4,866 and 5,172 are the excursions he predicted from
the frozen low region, with their next runs and new bottoms; all three happened as predicted (his new bottoms
1,542, 300 and 2,497 against 1,542, 302 and 2,498 here, measured one or two phases later). He gave about 7,675 for
the one after with next run 3,596: it happened at 7,675 with next run 3,596. The next
excursion is due near phase 14,600 (the bottom run after 7,675 is about 6,930). The per-phase logs of this run are
in `phase_sim/data/` (`real_low.txt.gz`: the lowest 24 runs at every phase start; `real_log.txt.gz`: per phase
the size of `b`, the length of `r` and the macro steps used).

**The digit parse is a two-state machine (exact).** Split `r` into units `0^g 1^n`. Between units the parse
(`rest`) is always in one of two states, and which one is the parity of the unit's start cell. A unit starting at
cell `p` parses iff `g = 3 (mod 4)` or `g + 2p = 0 (mod 4)` (so gaps of 3 or 7 always parse, a gap of 2 or 4 only at
one parity, a gap of 1 or 5 never). Each unit then gives 2 or 3 digits whose values depend on the parity of `n`:
the counter value is written in run-length parities. Checked: the predicted stop is the real stop at all 401
phase starts from 600 to 1,000 (`phase_sim/transducer.py`).

Because the frozen region moves one cell relative to `r[0]` every phase, the parity of every `p` flips each phase.
A gap of 2 or 4 therefore blocks the parse every other phase: this is the two-phase rhythm of the waves.

**One carry per wave per phase.** Within a phase the counter is filled up to the lowest blocking gap, then one
single-increment sweep carries into it and rewrites a few cells there, the parse continues to the next blocking
gap, and so on up the word (`phase_sim/frontier.py`, and the per-step cell ranges in a phase). So each wave moves
by exactly one local rewrite per phase.

**Wave rules found so far** (`phase_sim/waveexp.py`: one phase from a real word with only the runs at the wave
changed; `X, Y, Z` are consecutive runs above the wave, gaps written `zK`):

* `z4 X z3 Y z3 Z`: `X -> X+1` and the `z4` becomes `z3`; then if `X + Y` is even, `Y -> Y+1` and the gap after `Y`
  becomes `z2` (a merge next phase); if odd, `Y -> Y-1` and `Z -> Z+1`. Exception: `Y = 2` with `X + Y` odd keeps
  `Y = 2`, makes the gap after it `z2` and `Z -> Z+1`. (Lengths 2 to 41 tested.)
* `z3 X z3 Y` at the wave (the other phase): `X` even: `z4 (X-2) z3 (Y+1)`; `X` odd: `z4 X z2 Y`; `X = 2`: the 2-run is
  erased, `z7 (Y+1)` (this is where the `z7` gaps in the frozen region come from).
* `z4 X z2 Y z3 Z z3 W`: `X` even: `X -> X+1`, the pair `X z2 Y` is left alone, and the first rule acts one pair
  higher with `Y, Z` in place of `X, Y` (if `Y + Z` is even, `Z -> Z+1` and a `z2` after it; else `Z -> Z-1`,
  `W -> W+1`). `X` odd: `X+1` and `Y` merge (`X + Y + 3`) and the rest depends on the parities of `Y` and `Z`.
* `z3 X z2 Y` at the wave: `X` even: merge `X + Y + 2`; `X` odd: the pair is skipped and the first rule acts on
  `Y, Z`.
* Not complete: the merge cases chain, so the full rule is a small transducer over (parse state, gap, run parity,
  runs of length 2 to 4) that has not been tabulated. Every case tested so far depends only on these features.

**Every excursion starts a wave, and waves never die.** Write `r` as tokens (`zK` and `oN` alternate). Full
token dumps 10 phases apart near phase 10,000 change only in a few clusters: the bottom run, the top, and clusters
near token 2,333, 4,805, 5,099 and 6,574 at phase 10,010. Each cluster moves up by one token per phase (one run per
two phases), and the age it implies matches an excursion: 7,675 (age 2,335), 5,172 (4,838), 4,866 (5,144),
3,321 (6,689). Between two waves the runs are frozen. So an excursion is not only a local event: it starts a
wave that rewrites every run above it, one by one, forever. The run that will be next to the bottom at the next
excursion is written by the wave from the excursion before, a few phases after it starts.

**The low runs do not depend on the far tape.** From the phase 10,000 state with `r` cut after token 2,600
(everything above replaced by blank tape), 10 phases give the same tokens as the full run up to the cut
(`phase_sim/trunc.py`). They do depend on the counter `b` (with `b` replaced by a small value the run is different
from the first phase).

**How `b` enters, and a fast exact predictor.** In one phase the counter adds `b` to a binary number written
across all of `r`, with about one bit per token. One phase at 10,000 is 143 increment blocks: fill to the lowest
wave (`2^2329`), one carry, fill to the next wave (`2^4823`), and so on up to the top (`2^10004`). Since
`b_new + 3 = 2(b + 3 + s)` (`s` = right-moves in the phase), `b + 3` gains a factor 2 every quiet phase: at phase 10,000,
`b + 3` is divisible by exactly `2^2326`, about the age of the lowest wave. Influence only goes upward (lower
tokens and lower bits of `b` never depend on higher ones). So the first `N` tokens and `b mod 2^K` (with a large
filler above bit `K`, so every carry is still delivered) give the low tokens exactly (`phase_sim/lowsim.py`).
Between excursions the low tokens are frozen except the bottom run, which loses one cell per phase, so once the
last wave has left the first `N` tokens and `b = -3 (mod 2^K)`, the predictor jumps straight to the next
excursion. Checks:

* From phase 10,000 with `N = 2,600` and `b mod 2^2800`: identical to the full run up to the cut.
* From phase 600 with jumps: the lowest 8 tokens are identical to the full run at every phase it visits, through
  the excursions at 3,321, 4,866, 5,172 and 7,675 (the tokens above were not on the tape at phase 600, so they are
  not exact there).
* The full simulation, continued from phase 10,000 to 14,620 (about 7 hours), matches the predictor's first 12
  tokens exactly at phases 14,608, 14,609 and 14,619, so the first predicted excursion below is confirmed by the
  real run.

**Predicted excursions after phase 10,000** (from the phase 10,000 state; `N` = tokens kept):

| phase | run above the bottom | bottom 10 phases later | agreed by |
|---|---|---|---|
| 14,609 | 3,749 | 5,977 | N = 1000, 1300, 2000, and the full run |
| 20,595 | 42,177 | 54,376 | N = 1000, 1300, 2000 |
| 74,980 | 11,715 | 77,168 | N = 1000, 1300, 2000 |
| 152,157 | 114,247 | 174,179 | N = 1000, 1300, 2000 |
| 326,345 | 82,349 | 118,753 | N = 1000, 1300, 2000 |
| 445,107 | 201,658 | 410,262 | N = 1000, 1300, 2000 |
| 855,378 | 65,463 | 155,963 | N = 1300, 2000 (N = 1000 differs here) |
| 1,011,350 | 219,297 | | N = 2000; from phase 15,000 N = 2500, 3000 (runs after it differ, see below) |
| 1,402,241 | 364,948 or 522,086 | | from phase 15,000: N = 2500 and 3000 agree on the phase only |

Correction (from the exact full tape at phase 15,000, `data/state15000.txt.gz` from `fullmodel.py`, with `N = 2,500` and
`3,000`): both runs reproduce every excursion above through 855,378 with the same four runs, and at 1,011,350 they
agree on `A, B, C = 219,297, 171,592, 78,245` (`D` = 244,131 or 443,838). The `N = 2,000` run from phase 10,000
had `B, C, D = 80,185, 485, 589` there, and its next three excursions (1,310,834, 1,313,118, 1,316,154, with runs
of a few hundred) were artifacts of too little information: from phase 15,000 the next excursion is at 1,402,241.

No short run (length <= 4) next to the bottom in this range. The horizon is limited by information, not by
speed: an excursion merges many runs into the new bottom (`201,658 -> 410,262`), so a few hundred tokens are
used per excursion, and the runs that will be next to the bottom after about phase `10^6` were not yet on the
tape at phase 10,000. They are written later by the top, which depends on all of `b`. From a full state at phase
`P` this method reaches roughly phase `100 P`.

**Excursion arithmetic.** At an excursion the bottom run (now 2) and the 2 or 3 runs above it become one new
bottom run, of length about their sum, and the bottom then loses one cell per phase. So the next excursion comes
about (new bottom) phases later: 14,609 + 5,977 + 10 = 20,596 against 20,595 predicted; 20,595 + 54,376 + 10 =
74,981 against 74,980. Three runs are absorbed at 486, 5,171, 7,674 and 445,107; two at the others.

**What one wave does to the runs** (`phase_sim/align.py`, `wavecmp.py`). Follow the wave started at 14,609 from the
full state at phase 14,700 (`data/state14700.txt.gz`) to 15,970, and match the runs it left behind with the runs
there at phase 10,000 (nothing else touched that region in between). Every new run is a block of consecutive old
runs joined across their `z3` gaps (length = sum + 3 per gap), changed by at most 3 cells. Over 1,147 old runs: 508
blocks, of which 239 pairs, 62 triples, 62 blocks of 4 to 14 runs, and 145 single runs (changed by -3 to +3, mostly
0 or -1). A `-1` on one run with `+1` on the next is a gap moved by one cell. So each wave cuts the number of runs by
about 2.3, and the run left next to the bottom after an excursion is usually a joined block, but not always: at
445,107 the bottom takes three runs and the next run, 65,463, is a single old run left as it was. Short runs are
joined more often than not: of the 45 old runs of length <= 10, 41 were joined into a longer run and 4 were left
single (6 -> 5, 9 -> 10, 3 -> 2, 9 -> 12); a run of length 2 is erased when a wave reaches it (rule above).

**Short runs are everywhere.** Runs of length <= 4 at phase 10,000, by token position: 0 in tokens 2-500, 2 in
500-1,000, 7 in 1,000-2,000, 15 in 2,000-3,000, up to about 100 per 1,000 tokens near the top; at 14,700 there are
again some in every range. A halt needs one of them to reach the bottom unjoined. A run at index `i` needs about
`log_2.3 i` waves to get there, and is left single by a wave about 9 to 13% of the time (4 of 45 short runs, 145
of 1,147 runs above), so a naive estimate is `i^-2.5` per short run. The sum over all short runs ever written converges, so if waves acted at random
the chance of a halt would be small, and smaller the longer it runs. That is a heuristic, not a proof: the waves
are a deterministic carry and could favour some patterns.

**Run lineage on the exact tape** (`phase_sim/lineage.py`, `linpos.py`). The exact 13-rule model is run from the
full tape at phase 15,000; every run gets an id, and each local edit between phase starts gives the new runs as
parents the old runs whose cells they overlap. A run unchanged for 20 phases is "frozen"; following parents back to
frozen runs tells, for each wave passage, which old runs became which new run. The run also saves the exact full state at phase 20,000
(`data/state20000.txt.gz`; its lowest 24 tokens equal the independent model log at that phase). From 15,000 to 16,500, below run
index 1,000 (where the 14,609 wave passed): 1,335 old runs became 639 new ones (a factor 2.1); 16% of the old runs
were left single (14% of the 238 below index 300). The single ones mostly shrink: changes -3, -2, -1, 0, +1..+3 in
25, 16, 95, 68, 16 cases. Short runs do pass single: `2 -> 3`, `3 -> 3`, `3 -> 2`, `5 -> 2`, `6 -> 4`. Higher up
(index above 3,000, older waves) about half the old runs are left single. So the per-wave survival and shrinkage
used in the heuristic above are measured, not assumed, near the bottom; nothing here bounds them.

**Toward the exact wave rule.** Controlled test (`phase_sim/frontexp.py`): take the real state one phase after
14,731 (front `o1385 z2 o1273 z3 o909 z3 o8225`), replace the run below the front and the three above it by every
combination of lengths 9 to 12 (all four classes mod 4; also 5 to 8 and 105, 106 in a second test), and run one phase.
The result is a function of the four parities only: 8 outcomes, for example both odd below and at the front gives
the merge `W + X + 2`, then `z2 (X2 + 2) z2` if `X2` is even and `z2 X2 z3 (X3 + 1)` if `X2` is odd; an even run below
the front stops the `z2` merge altogether. So for runs of length >= 5 the wave is a finite-state machine on
run parities. What else enters is not settled: in synthetic runs (`phase_sim/synth.py`: random runs of length 9 to
16 put above the wave, then 220 phases) the same 4-run parity window gives different steps at different phases,
and two such cases differ only in the phase parity (bottom 5,871 against 5,754), so the phase parity, and
probably the position parity, are part of the state. Mining the logs (`phtab.py`, `learn.py`) with these
features still leaves about one sample per key, so the full table has to come from controlled tests like the
one above, run over all front configurations and both phase parities. That is the next step.

**The counter `b` is one marker bit per wave.** At phase 14,700, `b + 3 = 2^91 E` with `E` having 14 one-bits in
14,613 bits, and the gaps between them (6,934, 2,833, 2,502, 1,544, 305, ...) are the gaps between past excursions
(7,675 -> 14,609, 487 -> 3,321, 5,172 -> 7,675, 3,321 -> 4,866, 4,866 -> 5,172). The counter only changes at
excursions (`s = 0` in quiet phases, so `b + 3` just doubles), and each excursion leaves one bit that then moves up one
place per phase: the bit sits exactly at its wave (`v2(b + 3)` = age of the lowest wave). So `b` holds no hidden
history beyond the wave positions, and the whole state is the run list plus the waves. Flipping single bits of `b`
(`phase_sim/bflip.py`) confirms that bit `j` acts on the tape near token `j`.

**The wave's hidden state is an offset.** The marker bit moves one digit per phase, while the front moves by
whole runs (each run is 2 or 3 digits depending on its parity). Their difference `d` (digits below the front minus
`v2(b + 3)`) is a real part of the wave's state; it explains the ambiguity in the controlled tests (it also means
varying the run below the front, as in the test above, produces states that cannot occur). Varying only the runs
above the front, over 208 real front positions between phases 14,701 and 15,300 (`phase_sim/tabfront2.py`):
keyed on gaps and parities alone, 48 of 128 keys have two outcomes for the next three runs; adding `d`, 8 of 464;
adding one more gap and the run below the front, 0 of 800. For outcomes reaching further up a few conflicts remain,
and `d` takes values from -8 to 3, more than expected, so the front detection or the definition of `d` still needs
work. Next: define the wave state exactly (front position, `d`, pending `z2`/`z4`) and tabulate the transducer on it.

**Exact wave position, and why a data table has not closed** (`phase_sim/wavestate.py`, `wavefsm.py`,
`fsmcheck.py`, `parsestop.c`). The lowest wave is where the digit parse of `r` stops; recording that cell at every
phase start of the real run from 14,700 to 16,000 gives a clean picture for about 70% of phases: the stop sits on one
token for a few phases while `d` falls by one per phase, then moves up a couple of tokens and `d` resets. In the other
30% the parse runs past the wave (the two-phase rhythm above). But tabulating (phase parity, `d`, stop offset, run
parities around the stop) -> next state over these 943 transitions still leaves 17 to 25 conflicting keys at best,
with only one or two samples per key. Part of the reason is that `d` is not local: it is a digit count over the whole
word below the wave, and the units below give different digit counts on alternate phases (near phase 15,900, `d` is
about -4 on even phases and -1 to 5 on odd ones). The next attempt should derive the wave step from the machine's
transitions at the cell level (one carry sweep through a gap of 2, 3 or 4 with given parse state and neighbouring run
parities) instead of from run statistics.

**The wave step at machine level: 13 local rules** (`phase_sim/sweeptab.py`, `swmodel.py`, `model9.py`). Inside a
phase the counter fills its digits up to the lowest block (`INCS`, exact arithmetic), then one single increment
(`INC1`) is done by a real machine sweep, which carries into the block; the parse then reads on to the next block,
and so on. That sweep is the only part not already given as arithmetic, and it turns out to be simple: every digit
below the block goes from 1 to 0 (`0110 -> 0000`, `0111 -> 0011`, `10 -> 00`), and the 8 cells around the parse stop
change by one of these rules (`|` = the stop):

| before | after | | before | after |
|---|---|---|---|---|
| `1110|1100` | `1111|1100` | | `0110|1100` | `0011|1100` |
| `1110|1111` | `1111|1111` | | `0110|1111` | `0011|1111` |
| `1110|1110` | `1111|1110` | | `0110|1110` | `0011|1110` |
| `1110|1101` | `1111|1101` | | `0110|1101` | `0011|1101` |
| `1110|0001` | `1100|0111` | | `0110|0001` | `0000|0111` |
| `0111|0110` | `0011|1110` | | `1111|0110` | `1111|1110` |
| `1111|0111` | `1111|1111` | | | |

Checked cell by cell (whole word, including the low end) against the machine on all 9,160 carry sweeps from phase
14,700 to 16,000: all equal. Every rule except `1110|0001` removes exactly one run: two runs merge across a gap of 1 (or a run
of 2 is erased, `0110|0001`). `1110|0001` instead turns a gap of 4 into a gap of 3 (one cell off the run below, two
onto the run above). So the rules never create a run. The filling between carries can, though: near a wave, a
gap of 7 holds a run of 2 on some phase starts and not on others (`z7` becomes `z2 o2 z3`, and the 2 is erased
again later), so at phase starts runs do appear below the top, but only as these 2s inside a wave. The only other sweep in a quiet phase is the one after an overflow, and it only sets
`r[0] = 1`. So between excursions the machine is exactly: binary addition on a digit word that stops at blocks, plus
the 13 rules. At an excursion there is one more sweep (after the `R11` step), and it only clears the two cells left
of `r` and sets `r[0] = 1`. `model9.py` simulates the machine this way, without running any machine sweep; with
`CHECK=1` it also runs the machine and compares the whole word after every sweep. From phase 10,000 to 14,700,
across the excursion at 14,609, all 8,691 modelled sweeps (4,699 after an overflow, 3,991 carries, 1 excursion) are
equal to the machine's, and the tokens equal the full run's. With `STRICT=1` (stop on any sweep the rules do
not cover) and no machine sweeps after the first, the model ran from phase 10,000 to 29,438 (19,000 overflow sweeps,
36,800 carries, 2 excursion sweeps): its first 10 tokens equal the full run's at every phase from 10,001 to 14,857
and the predictor's at every logged phase to 24,803, across the excursions at 14,609 and 20,595. So the machine is exactly: the timer lemmas of
`SBCv9.v`, binary addition on the digit word, 13 local carry rules and 2 bookkeeping rules. Each of these is a
small statement that can be proved once in Rocq (like `RIncs` upstream), which is the per-phase half of a proof.

**Exact halting criterion at an excursion** (`phase_sim/haltgrid.py`, `rlesim.py`). Take the real state at phase
14,606 (bottom run 4, then `A = 3,749`, `B = 2,235`), set `A` and `B` to small values, and run 30 phases. Where the
macro model stops (`b = 0` without the overflow pattern), the real machine is run from that configuration with a
run-length simulator that crosses whole runs at once (the timer part `1^a` has `a` of about 2,200 bits). That
simulator agrees with plain step-by-step simulation on 400 random small configurations. Result (`H` = halts,
`.` = no halt in 30 phases):

```
A\B    1    2    3    4    5    6    7    8    9   10 2235 2236
  1    .    .    .    .    .    .    .    .    .    .    .    .
  2    .    H    H    .    .    .    .    .    .    .    .    .
  3    .    .    H    H    H    H    H    H    .    .    H    H
  4    .    H    H    H    H    .    H    H    H    H    H    H
5..12  .    .    .    .    .    .    .    .    .    .    .    .
```

So a run of length 5 or more next to the bottom is always safe, and lengths 2 to 4 can halt (3 and 4 almost
always). The halt is real: the machine ends in `G` reading a 1. The parity of `A` also decides how many runs the
bottom absorbs (odd `A`: 2, even `A`: 3, from the same grid run).

The same grid just before the excursions at 3,321, 4,866 and 20,595 (`haltgrid2.py`: the predictor is run to the
phase where the bottom run is 4; the early ones start from phase 600): `A >= 5` never halts in any of the four
contexts, and `A = 2..4` can halt in all of them. The exact cells inside `2..4` vary (at 20,595, `A = 2, B = 5`
halts; at 4,866, `A = 4, B = 1` halts), and `A = 1` is not always safe: at 4,866 it halts with `B = 4` or `5`. So the
fact a proof needs is: at every excursion the run next to the bottom is at least 5 (or 1 with the run after it not
4 or 5).

**The one route to a halt** (`phase_sim/excgrid.py`). Same state (phase 14,606), now with the four runs above the
bottom set to lengths 21 to 61 of every parity combination. In 12 of 16 parity patterns the bottom absorbs 2 runs
and the run left next to it is a joined block (so at least 5: safe). When `A` is even and `B` odd, the bottom can
absorb 3 runs and leave the 4th run on its own next to it, unchanged: with `A..D = 30, 41, 51, 61` the new bottom is
`30 + 41 + 51 - 3 = 119` and `61` sits next to it. Had `D` been 2 to 4, the following excursion would halt. So the
machine halts only if, at some excursion, the bottom takes 3 runs and the run after them is short and is still
short when the bottom has counted down to it. In the real run that single-run case has happened once in the 16
excursions (445,107, with `D = 65,463`).

End to end (`phase_sim/routeone.py`: set the runs, run through this excursion and the next one, and on a stuck
macro step run the machine). At the states just before 14,609 and 20,595, with `A = 30, 31`, `B = 40, 41`,
`C = 50, 51`, `D = 1..8` and `E = 61` (64 cases each), exactly one case halts, the same in both: `A` even, `B` odd,
`C` odd, `D = 3` (halt about 120 phases later, at the next excursion). There the 3 goes `3 -> 2 -> 3` while the wave
passes and stays single. With the same parities `D = 2` and `D = 4` do not halt (the 4 becomes 3 and merges with
`E`), and `D >= 5` is swallowed by the new bottom. The `D = 3` case halts for every `E` tried (2, 3, 60, 61, 64, 100)
and for other sizes of `A, B, C` (`32, 43, 53` and `28, 13, 9`). A short `C` (1 to 7) does not halt with `A` odd, or
with `A` and `B` even (28 + 14 cases at 20,592). Two short runs together (`C, D` in 1..6 with `A = 30, B = 41`;
`C, D` in 1..5 with `A = 31`, `B = 40, 41`; 86 cases): with `A` even only `C = 3, D = 3` and `C = 5, D = 3` halt (the
same route, `C` odd); with `A` odd only `B = 40, C = 2, D = 1` and `B = 41, C = 3, D = 1`. No run of length 1 occurs
at any phase start in the data (the lowest 24 runs at every phase to 29,438, and the full tapes at 10,000, 14,700
and 15,000), so those two need a configuration that does not seem to occur. So the remaining proof task is about
one pattern: show that no excursion has `A` even, `B` odd, `C` odd and `D = 3` (and that runs of 1 never appear,
and no other short pattern halts; only the cases above were tried).

**How close the real run comes.** The four runs above the bottom at each excursion (real run to 10,000, then the
predictor), the number absorbed by the new bottom, and the shortest of the first 11 runs:

| phase | A | B | C | D | absorbed | shortest of first 11 |
|---|---|---|---|---|---|---|
| 89 | 14 | 12 | 3 | 71 | 2 | 3 |
| 117 | 77 | 17 | 57 | 33 | 2 | 17 |
| 213 | 93 | 177 | 112 | 69 | 2 | 17 |
| 485 | 700 | 277 | 40 | 109 | 3+ | 40 |
| 3,319 | 555 | 988 | 23 | 76 | 2 | 23 |
| 4,864 | 102 | 202 | 192 | 809 | 2 | 45 |
| 5,170 | 1,052 | 853 | 593 | 2,322 | 3 | 250 |
| 7,673 | 3,596 | 2,829 | 505 | 1,016 | 3 | 505 |
| 14,609 | 3,749 | 2,235 | 37,239 | 4,935 | 2 | 1,061 |
| 20,595 | 42,177 | 12,206 | 3,604 | 8,108 | 2 | 3,604 |
| 74,980 | 11,715 | 65,460 | 46,780 | 67,464 | 2 | 11,715 |
| 152,157 | 114,247 | 59,939 | 34,139 | 48,207 | 2 | 19,041 |
| 326,345 | 82,349 | 36,411 | 89,522 | 44,351 | 2 | 36,411 |
| 445,107 | 201,658 | 49,627 | 158,981 | 65,463 | 3 | 35,305 |
| 855,378 | 65,463 | 90,507 | 134,142 | 85,152 | 2 | 60,536 |
| 1,011,350 | 219,297 | 171,592 | 78,245 | 244,131 or 443,838 | 2 | |

The closest call is phase 89, with a 3 as the third run (absorbed safely). After the first few hundred phases the runs
near the bottom are hundreds to hundreds of thousands long. Three runs were absorbed at 445,107 (A even, B odd, as
the grid above predicts) and in the early cases where the first runs were short.

**Speed.** The predictor keeps `b mod 2^K` plus a filler above bit `K`. The filler was `K/2` one-bits; each of them
costs an extra increment block per phase once a wave is inside the kept tokens, which made `N = 3,000` run at
90 s per phase. With `FILL=10` (10 filler bits, re-trimmed every phase) it is about 10 phases per second again,
and from phase 10,000 with `N = 2,500` its first 300 tokens equal the full run's at every phase
from 10,001 to 14,620; with `N = 2,000` it gives the same first four excursions as the
slow version (14,609, 20,595, 74,980, 152,157, with the same runs).

**What a proof still needs.** Two parts, of very different difficulty.

1. *The per-phase part* (done in Rocq, see below). The timer lemmas of `SBCv9.v` under `a` odd (and `a = 3 mod 4` by a
   trivial induction), the digit arithmetic (`rest`, `RIncs`, as upstream), the 13 carry rules and the 2 bookkeeping
   sweeps as Rocq lemmas, and a local invariant on `r` (gap and run shapes) showing that every carry sweep meets one
   of the 13 windows. All of this is checked by simulation. In Rocq so far (`rocq/`): the timer lemmas, the
   counter arithmetic, all carry windows as lemmas, a carry proved total on every word, and the reduction
   `holdout_nonhalt_of_no_bad` (below), so no local invariant is needed.
2. *The global part* (open, and possibly as hard as a cryptid). At every excursion, the run next to the bottom is at
   least 5. The pieces known: below the top, runs are created only as transient 2s inside a wave; each wave passes every run once, and leaves it either
   merged (length at least the sum plus 2) or single, changed by -3 to +3 in the data, depending on parities and the wave's
   offset; an excursion's cascade swallows short runs near the bottom except in narrow cases (the `D = 3` route
   above). So a halt needs a run born at the top to stay unmerged through every wave down to the bottom and end at
   length 3 (or 2 to 4) in the one slot that is not swallowed. Nothing found so far rules this out deterministically:
   whether a run is left single depends on run parities and the wave offset, which look pseudo-random. The
   heuristic above (survival about 10% per wave, about `log_2.3 i` waves from index `i`) makes a halt after phase
   10,000 very unlikely, but it is not a proof.

**Rocq** (`rocq/M9Timer.v`, `rocq/M9Run.v`, against this repository's `verify/`). The machine is written mirrored
with states renamed so that it lines up with TM2 of `SBCv9.v` (`1LC0RF_1RE---_1LD1LC_0LE0LD_1RB1RF_0RC1RA`).
TM2's timer lemmas fail here for even `a` (in Rocq, `LInc` goes through at `a = 3` and gets stuck at `a = 4`), so
the timer is written `0inf <* [1] <* [1;1]^^k <* <[1;0]^^b` (`a = 2k + 1`). With that, `LInc`, `LIncs`, `LOv`,
`LRst_101`, `LRst_11`, `LRst_10` and `init` are proved with TM2's proof scripts unchanged, and the counter
arithmetic (`rest`, `RIncs`, `RIncs_spec`) is TM2's, unchanged. The macro step `mstep` (sweeps still by bounded
simulation, as upstream) and `msteps_spec` follow. `M9Run.v` runs it from the blank tape: all 13,000 macro steps
succeed, and `reach13000 : c0 -->* (that configuration)` is proved, with a counter of 400 bits (past TM2's halt at
its 374th overflow). Assumptions: only `functional_extensionality_dep`, which the framework's `flip` uses.

`rocq/M9Carry.v` replaces the simulated sweep by lemmas. A carry sweep never reads past the 8-cell window at the
parse stop (the head turns inside it), so each of the 13 rules is a `segRLs` fact about a fixed word with an
arbitrary tail, proved by computation: entering the last digit (t0 `0110`, t0 `0111`, or t1 `10`) or the stop
itself (t1 `0110`, `0111`) with that parse state's pass. With the four digit lemmas (t0 `0110 -> 0000` and
`0111 -> 0011`, t1 `10 -> 00`, `11` unchanged), three absorb lemmas (a carry ending in a 0-digit near the top:
`0000 -> 0110`, `0011 -> 0111`, `00 -> 10`) and `0 -> 1` for the sweep after an overflow, `carry_spec` says: if
the function `carry` succeeds on `r`, the machine does that sweep. `mstep2` uses only these (no simulation), and
`reach13000_rules` runs it from the blank tape: all 13,000 macro steps succeed, so on that stretch every sweep is
one of these 21 lemmas. In Python (`phase_sim/carrycheck.py`, the same `carry` against the machine's sweeps) every
sweep from the blank tape to phase 1,500 is covered, and the pure model above covers 10,000 to 29,438.

`rocq/M9Reduce.v` turns this into a reduction. It restates the macro steps with `-->+` (each takes at least one
machine step), gives the macro step `mstepG T` the fuel `T` as a parameter (a fixed fuel runs out once the tape is
long), and defines `runs` coinductively: `runs x` if some fuel gives a step `mstepG T x = Some y` and `runs y`. Then

```
Theorem holdout_nonhalt_of_runs: runs start -> ~ halts holdout c0.
```

for `holdout := TM_from_str "1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA"` (through `Perm` for the renaming and
`flip_halts_c0` for the mirror), with `start := cfgL' 5 5 ([1;0]*>0inf)`. Assumptions: `functional_extensionality_dep`
only. So a non-halting proof now needs exactly `runs start`: that this explicit function on `(k, b, word)` (timer
arithmetic, digit addition, `0 -> 1`, and the 21 carry lemmas) never gets stuck. It gets stuck exactly when a
carry meets a window outside the 21 (the local invariant) or when `b = 0` and the word does not start with `00`,
`101` or `11` (the halt route of the excursions).

**The local part is now proved** (`rocq/M9Windows2.v`, `M9List.v`, `M9Total.v`). The carry does not need an
invariant after all. Every stop pattern has a lemma: after a t0 `0110` all 12 non-digit 4-cell patterns, after a
t1 `10` all 12, and at a t1 stop all 4 (`01xx`), 30 windows proved by computation. Two of them (`0110|0100`,
`0110|0101`) return in a different state `X = (C,[1;1])`. In that state every t0 `0110` below becomes `1111` and
passes `X` on, and the first t1 `10` below becomes `11` and returns to the normal t1 state (4 more lemmas). The
word is kept as a list (tape `w *> 0inf`). `carryL` follows the parse with both return modes, and `carryL_spec`
says it is sound. `carryL_total` proves that with fuel `|w| + 1` it always succeeds. The proof is induction on
`|w|`, plus a computation over all 256 possible first 8 cells: after the windows fail, the next cells are a valid
digit, and every start is covered. The macro step `stepL` does one increment when `b > 0` and the reset/overflow
rules when `b = 0`. It can only get stuck at `b = 0` with a word starting with none of `101`, `11`, `00`
(`stepL_stuck`). So:

```
Theorem holdout_nonhalt_of_no_bad:
  (forall n x, iterL n startL = Some x -> ~ bad x) -> ~ halts holdout c0.
```

Assumptions: `functional_extensionality_dep` only. A bad configuration is not always a halt (simulated from a few
bad ones, some halt within a few thousand steps and some do not, depending on `k`), so this is one direction
only, which is the one a non-halting proof needs. Run from the start in Rocq, `stepL` takes 200,000 steps (to
`b = 7,532`) without reaching a bad overflow. `stepL` applies the timer resets (`101`, `11`) only at `b = 0`, while
TM2's order (the Python model) applies them whenever the word starts that way, which happens at excursions with
`b > 0`. Both are proved lemmas from the same configuration (in a direct check the machine passes through the
`LInc` end point first and the `LRst_11` end point later in the same sweep), so both orders are sound, but their
checkpoints differ. `phase_sim/steplorder.py` runs the Python model in `stepL`'s order: from the blank tape to
phase 400 (excursions 91, 119, 215) and from phase 10,000 to 21,000 (excursions 14,609 and 20,595) it never
reaches a bad overflow, and its phase-start words equal the real run's (phases 398 to 400) and the predictor's
(phase 21,000). What remains is exactly the global statement: the list machine never
reaches `b = 0` with a word that starts with none of `101`, `11`, `00`.

The two parts behave very differently (`phase_sim/randb.py`): run the same macro model from the blank tape but
replace `b` by a random number at every overflow (same bit length, or a random length). Over 20 runs of up to 80
phases no carry ever meets a window outside the 21, so the local invariant looks independent of `b`, and a proof of
it on words alone is plausible. A stronger test (`phase_sim/randk.py`): set `b` to a random value before every
macro step (often 0 to 3, so increments and overflows happen at arbitrary times; an overflow that would get stuck
is replaced by a small `b`). Over 20 runs of 4,000 macro steps, all 22,308 sweeps are covered by the 21 lemmas.
But in the first test every one of the 20 runs gets stuck within 80 phases at an overflow (`b = 0` and the word
starts with none of `00`, `101`, `11`). So staying alive depends on the exact value of `b`, the "sync" of the class
name, and any proof of the global part has to track `b` exactly (as the marker bits above).

Why, and a candidate invariant. Parse `r` from its start (state t1) until the parse fails. At a failure in state
t0 the next 4 cells are not a t0 digit; of the 12 such patterns, the 5 that contain no run of length 1 (`1100`,
`1111`, `1110`, `1101`, `0001`) are exactly the right halves of the t0 windows. At a failure in state t1 the next
2 cells are `01`; the patterns without a run of 1 are `0110` and `0111`, the t1 windows. At a carry all digits
below the stop are 1-digits, which fixes the left halves. So `carry` succeeds whenever no run of length 1 starts
at or after the failure point. Candidate invariant: *every run of length 1 in `r` ends inside the parse-valid
prefix*. It holds at all 30,000 configurations of 10 runs of the random-counter model above
(`phase_sim/inv1.py`), and no run of 1 occurs at any phase start of the real run. Digit addition keeps the digit
structure (it only swaps `0000/0110`, `0011/0111`, `00/10`), so it keeps the parse prefix and the rest of the word;
a carry zeroes digits (same structure) and rewrites one window into a longer parse prefix. Proving that it is
preserved, in Rocq, would leave exactly the overflow condition.

## 7. Reproduce

```bash
cd notes/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/tools
python3 sbc9.py check                                   # self-test against the direct run
python3 sbc9.py count 110000000000 30 70                # counter from a small start (section 3)
gcc -O2 -o samp samp.c && ./samp 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 3000000 C 0 R | head -60
gcc -O2 -o bstat bstat.c && ./bstat 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 1000000000
```

Rocq (after `make` in `verify/`):

```bash
cd notes/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/rocq
coqc $(cat _CoqProject) M9Timer.v && coqc $(cat _CoqProject) M9Run.v   # M9Run takes about a minute
coqc $(cat _CoqProject) M9Carry.v                                       # about two minutes
coqc $(cat _CoqProject) M9Reduce.v                                      # the reduction theorem
coqc $(cat _CoqProject) M9Windows2.v && coqc $(cat _CoqProject) M9List.v && coqc $(cat _CoqProject) M9Total.v
```

Phase-level simulation (needs Python 3 and a C compiler):

```bash
cd notes/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/phase_sim
gcc -O3 -shared -fPIC -o libsweep.so sweep.c
python3 test_tm2.py              # the port on TM2: 12417 macro steps, 374 overflows, then TM2 halts
python3 check_lemmas.py          # timer lemmas on this machine (ok for odd a); add "tm2" for TM2
python3 check_rincs.py           # RIncs vs single sweeps
python3 run37.py out 10000       # the real run: out.log (per phase), out.low (lowest runs per phase), out.ckpt
python3 excursions.py out.low     # the excursion table above
gcc -O3 -shared -fPIC -o libparsestop.so parsestop.c
JUMP=1 FILL=10 python3 lowsim.py data/state10000.txt.gz 2000 2200 1400000 pred   # predicted excursions
gcc -O3 -march=native -o lowsim_c lowsim_c.c -lgmp -lz   # C port of lowsim.py: same output files, about 70x faster
JUMP=1 FILL=10 ./lowsim_c data/state20000.txt.gz 3000 3200 4000000 pred20k
STRICT=1 python3 fullmodel.py data/state14700.txt.gz 20000 full 5000   # exact full tape, 13-rule model, no machine sweeps
python3 haltgrid2.py data/state14700.txt.gz 20580                     # halting grid just before the 20,595 excursion
python3 routeone.py data/state14700.txt.gz 20580 30,41,51,3,61        # the D = 3 route: halts at the next excursion
```

Analysis by messerdsp, with Claude Opus 5.5.
