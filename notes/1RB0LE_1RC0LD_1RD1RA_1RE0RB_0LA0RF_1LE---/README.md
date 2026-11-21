# Notes: `1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---` (23154), with its twin 115779

Goal: a Rocq proof, in this repository's style, that bbchallenge machine 23154 does not halt from blank tape
(and, through `verify/Eqv_v2.v` module TM567, that `1RB0RD_0LC0RF_1RD0LB_1RE0LA_1RA1RC_1LB---` does not), and the
same for its twin 115779 = `1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---`; or a clear finding that it is much harder
than expected, or halts.

Labels used for every claim: *proved (Rocq)*, *proved elsewhere (Lean, not ported)*, *simulated*, *heuristic*.

Branch: created from `master` and fast-forwarded to this fork's `BB6` (= ccz181078/busycoq `BB6` at `33209bc`,
3 Nov 2026), like the two studied machines' branches, so that `verify/` has the busycoq library (`Individual62`,
`Eqv_v2`, `CTLv*`, ...).

## Stage 0: what is known, by whom, at what level (checked 21 Nov 2026)

### Is anyone else on it? No.

* **ccz181078/busycoq, `BB6` branch** (last commit `33209bc`, 3 Nov 2026, "add FIBv7, 23 2x5 proofs"): the three
  tables of this family occur only in `verify/Eqv_v2.v`:
  * TM567: `halts 1RB0RD_0LC0RF_1RD0LB_1RE0LA_1RA1RC_1LB--- <-> halts 23154` (`solve_eqv`, proved (Rocq) there);
  * line 16130: `1RB---_0RC0LA_1LD0RB_1LE0RF_1LF1LC_1LB0LD` (third holdout with this table, see below) is the `tm'`
    of an equivalence module.
  No file proves any of them non-halting.
* **Open PRs** (all 109 `refs/pull/N/head`, diffs against their merge base with `BB6` and their commit messages,
  every machine string mapped to the canonical form of `notes/triage/tools/canon.py`): no PR mentions 23154, 115779,
  TM567's machine or `1RB---_0RC0LA_...`, literally or in mirrored/renamed form. Script: scratch `scanpr.py`
  (the logic is in `tools/canon.py` plus a `git diff` loop).
* **bbchallenge wiki**: no page for either machine (the page `1RB0LE_1RC0LD_..._1LE---` does not exist). *BB(6)*,
  *Holdouts lists*, *TMBR: November 2026* do not mention them. The newest BB(6) list is still mxdys's 608 of
  30 Oct 2026 (TMBR November: "BB(6) 608 608 0").
* **Community spreadsheet**: both listed, class "Shift-overflow bouncer counter", no status, no notes, no name.
* **AI analysis artifact** (8B8E5ms18otN4XHbEnxaP2, read as data): both `pattern`, "Same table as another holdout,
  mirrored. It joins that machine's main layout", simulated to 1.0e17 (23154) and 4.0e17 (115779), no PR, no proof.
* **busy-beaver-explorer** (fractal-geometry-explorer, clone of 20 Nov 2026, folder status "as of 9 November 2026"):
  folders for both, verdict "open". This is the main prior work; see below. It is a broad project with folders for
  about 600 holdouts, not a dedicated effort on this machine.

So nobody has proved it or has a PR for it. Proceeding.

### The family

Three holdouts of the 608 share one table up to renaming and mirroring (exact table comparison by the explorer's
`related.py`, which I rechecked with `canon.py` on the tables, not the runs):

| id | machine | start |
|---|---|---|
| 115779 | `1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---` | the reference table, state A |
| 23154 | `1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---` | 115779's table (A→B, B→C, C→D, D→E, E→A) started in 115779's E |
| ? | `1RB---_0RC0LA_1LD0RB_1LE0RF_1LF1LC_1LB0LD` | 115779's table mirrored, started in 115779's F; the explorer calls it a different-looking bouncer with a "chaotic wall" (not studied here) |

Plus TM567's machine, equivalent to 23154 by busycoq's `Eqv_v2`.

Below, states are 115779's unless said otherwise (23154's are one letter later: 115779's B is 23154's C, etc.).

### What the explorer notes say (proved elsewhere (Lean, not ported) unless marked)

Table of 115779:

| state | 0 | 1 |
|---|---|---|
| A | 1RB | 0LC |
| B | 1RC | 1RE |
| C | 1RD | 0RA |
| D | 0LE | 0RF |
| E | 1RA | 0LD |
| F | 1LD | --- |

* **Digits.** A digit `d` is the block `0 1^(3d+2)`. At each sweep the tape is
  `0^∞ 1^r [0 1^(3d1+2)] ... [0 1^(3dm+2)] 0 1 B>0 0^∞` (`P (raw r) ds`) or the same ending `0 1^4 B>0` (`Q`).
* **Sweep rule** (`Sweep.lean`: `sweep_zero`, `sweep_even`; *Lean kernel*): with `b` the rightmost even digit, `a`
  the digit left of it and odd digits `2k+1` right of it,
  `a 0 (2k1+1)...(2kn+1) -> (a+2) 0^(2k1) 1 ... 0^(2kn) 1` and
  `a (2i+2) (2k+1)... -> (a+1) 0^(2i+1) 1 0^(2k1) 1 ...`, in `21 + 10b + Σ(20kj+16)` steps.
* **Left end** (`raw_zero`, `raw_even`, `carry3_sweep`, `carry9_sweep`, `phase2_sweep`; *Lean kernel*): no even digit
  left: first digit even merges into `1^r` (r+6 or r+3); all odd and r = 3: two new leading zeros; all odd and
  r = 6j+9: `1^r` becomes `1^3` and `2j+3` zeros; `Q` with last digit 1: one sweep to `P` with last digits `2 0`.
* **Nested run start** (`nest_sweep`, *Lean kernel*): all digits odd, first digit 1, r = 6j+6: `1^r` becomes `1^3`
  and `2j+1` zeros and the head turns back before the right end, in phase Y. The passed region holds each passed
  digit `2k+1` as `0 0 (1 0)^(3k+2)` (digit 1: `0 0 1 0 1 0`), then the old right end `0 0 1 0`.
* **Inner sweeps** (`Inner.lean`: `inner_X_zero/even`, `inner_Y_zero/even`, *Lean kernel*): phases
  `X: [ds] 0 1 1 E>1 0 W` and `Y: [ds] 0 1 1 1 0 F>0 1 0 W`; an inner sweep changes the digits by the same rule,
  alternates X and Y, and each sweep from X eats one passed token `0 0 1 0 1 0` from `W`. These need the stop digit
  (an even digit) to exist, i.e. not an inner left-end event.
* **Halting condition** (README, argued by hand; *not formalized*): halts iff a right-moving head in B reads `0`
  followed by `0 1 1` (B, C, D, F moving right over `0 0 1 1`).
* **Reduction** (`Reduce.lean`, `halts_imp_uncovered`, *Lean kernel on a native-decided reach*): if 115779 halts then
  the run-length sweep function `nextR`, started at step 231,327,122, eventually fails (an uncovered sweep).
* **Runs** (*Lean native_decide*): 115779 no halt in 4.0·10^14 steps (its first nested run, 115,676,475 steps, is
  checked cell by cell); 23154 no halt in 266,357,150,814 steps (up to the start of its third nested run).
  *Simulated* (C, trusted): 115779 runs 2.1·10^9 sweeps (1.8·10^19 steps) of proved rules without an uncovered
  sweep.
* **Not formalized, only seen in simulation:** passed digits other than 1 (eaten in another phase pattern, ending
  `1^4` instead of `1^5`), inner left-end events (including a nested run inside a nested run, seen at depth 2), and
  the end of a nested run (right end in phase `Q`; when a deeper level ends first, the rest of the passed region
  above "is closed up into one large digit").

### What the triage (`bb6-triage`) adds (all simulated or heuristic)

No halt of 23154 to 1.25·10^20 steps (`tri.c`); at most 34 runs of 6-cell blocks; no new local 3-run window after
5.3·10^11; 0 halts in 200 random/forced-nested 115779 starts (10^9 steps each) and in every perturbation, run-out and
scaled-restart test.

### What is missing for a proof

1. The nested run as a theorem: inner left-end events (recursively: nested runs inside nested runs), passed digits
   other than 1, and the end of the run (what the tape is after it).
2. An invariant on whole configurations that covers the stack of nested runs, plus the halting check
   (no `0 0 1 1` in front of a right-moving B).
3. Everything in Rocq: none of the Lean work is in Rocq; it all has to be re-proved here.

## Stage 1: more testing

(in progress)
