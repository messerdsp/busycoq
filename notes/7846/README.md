# BB(6) machine 7846: `1RB0LA_1RC---_0LD1RD_0RA0RE_0RF1RC_1LF0LA`

**Status: blocked.** There is no Rocq proof here. The plan was to reuse an existing argument
(same structure as the proof of 1RB0LA_1RC---_0LD1RD_1RA0RE_0RF1RC_1LF0LA in busycoq). That
argument does not carry over to 7846: the bounded rules carry over, but the induction over
levels does not. The details are below. Every claim on this page is labelled
*simulated* or *heuristic*. Nothing here is *proved (Rocq)*.

The two machines differ in one transition only: D reading 0 is `0RA` here and `1RA` in the
other machine.

## Method

`tools/` contains the scripts. `tools/gate.sh <proof .v>` reproduces every number on this
page (about 1.5 minutes).

- `rules.py`: checks a bounded rule `l <* X {{q}}> Y *> r -->* l <* X' {{q'}}> Y' *> r`
  (busycoq notation) by running the machine on the finite segment `X q Y`. The run must
  stay inside the segment until it reaches the right-hand side.
- `scan.c` and `parse.py`: list the configurations of the form
  `RecT l0 tp W d r = lstack (d :: rev W) (base tp l0) <* [1;0] {{C}}> r`
  (a base-4 counter: `base` is `TDig d` or the lone base `TLone`, the digits are the words
  `Rl d`, and `r` is blank), together with the left part `l0`.
- `sim.c`: prints the tape as a run-length encoding.
- `erase.py`: runs the erase sweep (A moving left over 1s) into the left part that 7846
  actually has.

## Findings

1. **Bounded rules (simulated).** The other proof's `Section Gen` takes its machine as 32
   tape-rule hypotheses. All of them hold verbatim for 7846, with `SA = A`, except `exhaust`.
   `seed` holds in 0 steps because `SA = A`. For 7846, `exhaust` needs 9 zeros instead of 7
   and leaves `EXT1 = [0;0;1;1;1;1]` instead of `[0;1;1;1]`. The rule is in
   `tools/exhaust9.txt` (165 steps).
2. **Levels from the blank tape (simulated).**
   - A 7-digit counter (`TDig`) runs from step 3,491. It overflows and is erased at about
     step 3.77e6.
   - At step 20,657,323 there is a 22-digit counter, which is level m = 23:
     `RecT (0inf <* P23 <* [1]^^82433) (TDig D2) W d`, with
     `W d = 0211m1000m1000m0m0m010` (most significant digit first, `m` = `Dm`).
   - In the other machine, the corresponding configuration is level 17 (16 digits) at step
     20,274,513, and its left part is `1^R`.
   - In 7846, the left part `P23` is `1110110111110 1^1322 0110` (tape order), not `1^R`.
     It is still there at step 4e7.
3. **The erase leaves junk (simulated).** Start from `0inf <* P <* [1]^^R <{{A}} 0inf`.
   The machine clears `P` and reaches `0inf {{A}}> J *> 0inf`, where:
   - for `P0 = 1110110111110` (the left part of the 7-digit level),
     `J = 0^5 1^6 0^3 1^3`;
   - for `P23`, `J23 = 0^5 1^6 0^3 1^3 0^1320 1^6`.
4. **The run from the junk is not a replay (simulated).**
   - From `J`, with a blank right side, the machine builds a few lone counters. By step
     597,367 it has a 13-digit lone counter (`TLone`), whose left part is
     `P0 1^1322 0110 1^2663`.
   - This is exactly what the real history does after the first overflow: the tape at step
     3,775,068 + 597,367 is the same.
   - Level 23 then arises when this 13-digit lone counter reaches the remains of the 7-digit
     counter.
   - From `J23` the machine again builds a 13-digit lone counter (by step 1,864,959). It
     adds one more mark `1^8630 0110` to the left part.
   - It does not rebuild the level-23 counter.

## Why the argument does not transfer

In the other proof, the level invariant `LevD` stores a run from the blank tape to the
level-m configuration with left part `0inf <* [1]^^R`. The step from level m to level 2m+1
uses that run twice:

- At the overflow, `era1` erases the whole left part, down to `0inf`.
- The replay lemma reruns the blank-tape history. This rebuilds the level-m counter as the
  crossing counter X (m−2 digits), which counts to `WX` and stops at the old remains
  `REM` (S1, `HC`/`HS1`).

In 7846 neither step holds:

- **Left part (simulated).** The left part is not `1^R`, and the erase stops at its 0s. The
  machine clears it but leaves the junk `J23`, so the tape is not blank.
- **No replay (simulated).** From `J23`, the machine builds a fixed-size lone counter with
  13 digits, not a copy of the level-m counter. So no X of length m−2 reaches `REM_m`.
- **Lone counter overflows first (heuristic).** The 13-digit counter has at most 4^13
  values, so it travels on the order of 10^8 cells before it overflows. The old level-23
  remains are on the order of 10^13 cells away. So it overflows again first, and each
  erase leaves a new mark.
- **First transition (simulated).** The first transition (7 digits to 22 digits) already
  came from a lone 13-digit counter reaching the remains of a shorter counter. It did not
  come from a replay.

So the obstacle is not a matter of other words or constants. A proof for 7846 needs a new
invariant: a cascade of fixed-size lone counters started from junk, crossing old remains,
while marks pile up in the left part. `Section Gen` does not provide one.

## Rocq

No `.v` file was produced, so there is no compile time and no `Print Assumptions` output.
