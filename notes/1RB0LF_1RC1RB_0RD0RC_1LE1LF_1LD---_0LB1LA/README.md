# Notes: `1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA`

BB(6) holdout (on the 608 list of 30 Oct 2026; spreadsheet class *Sync bouncer counter*).
**Status: open.** No Rocq proof here, only analysis notes and tools to reproduce it.
Everything below marked *(sim)* was checked by direct simulation; nothing here is proved.

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

**The real run, followed to phase 7,719 with no halt.** Excursions (phase, run above the bottom, new bottom
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

**What a proof still needs.** The exact wave rule (how a wave turns old runs into digits, and when it merges),
what the top writes, and an invariant showing that no run of length <= 4 is ever next to the bottom when the bottom
reaches 2. The timer side is done: the `SBCv9.v` lemmas carry over under `a` odd, and `a` is odd by a trivial
induction.

## 7. Reproduce

```bash
cd notes/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/tools
python3 sbc9.py check                                   # self-test against the direct run
python3 sbc9.py count 110000000000 30 70                # counter from a small start (section 3)
gcc -O2 -o samp samp.c && ./samp 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 3000000 C 0 R | head -60
gcc -O2 -o bstat bstat.c && ./bstat 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 1000000000
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
```

Analysis by messerdsp, with Claude Opus 5.5.
