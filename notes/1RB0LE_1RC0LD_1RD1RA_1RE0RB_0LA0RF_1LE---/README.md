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

## Stage 1: more testing (all *simulated*)

Tools (in `tools/`; all use 115779's state names, 23154 is mapped by A→E, B→A, C→B, D→C, E→D):
`sweeps.c` (sweep-start events P/Q/X/Y with the passed region's shape), `exh.c` + `gen_exh.py` (exhaustive test),
`cells.py` (cell-level trace), `rpass.py` (where a right pass stops), `hyp.py`, `outside.py`, `nearmine.py`
(language mining). Checked against the explorer's numbers: `sweeps blank23154` reproduces the nested runs at
sweeps 5 and 28 and the tape `Q r=3 [0,0,1,1,1,0,2,1^10]` at step 5,512; `sweeps P 3 0,2,2,1,1,1,1,1,2,0` reproduces
`P r=3 0 2 2 1 1 1 1 1 4` after 21 steps (`reach_D1`).

### 1. Exhaustive small cases (`tools/exh.c`, results in `data/exh/`)

Each start is run to the next sweep start at the outer right end (or 10^8 steps); every sweep start on the way
(outer P/Q and inner X/Y) is checked against the documented forms: left part `1^r` (r ≡ 0 mod 3) then digits
`0 1^(3d+2)`; passed region W (see 3 below).

| starts | number | halts | left the forms | nested runs | timeouts |
|---|---|---|---|---|---|
| P and Q, r = 3..30 (step 3), up to 6 digits, each 0..6 | 2,745,140 | **0** | 2 (see below) | 5,460 (1 of depth 2) | 0 |
| X and Y, r = 3..18, up to 3 digits 0..3, W = `(101010)^{0,1}` + up to 3 blocks of {B1, B1 110, B2, B5, B8} + `001` | 318,240 | **0** | 22,302 | 182,760 | 0 |

(B_n = `0 0 (1 0)^n`; a passed digit 2k+1 is B_(3k+2), the "token" T; U = `1 0 1 0 1 0`.)

* The 2 outer starts that left the forms (`P 12 1,1,1,1,1,3` and `...,5`) start a nested run inside a nested run while
  the passed region begins with a partial token, so a region boundary B1 can be followed by U's. With the region
  language widened to that, they pass.
* Every inner start that leaves the forms has a synthetic W that the machine does not seem to build (for example an
  empty region `B1 001`); they still never halt. The shortest: `X 6 [0] W=0010001` gives a Y sweep start with right
  part `0 1 0`.
* So: **no halting configuration was found in 3.06 million starts**, and the documented sweep forms are closed on all
  outer starts up to these sizes, once the passed-region language below is used.

### 2. The nested run, as seen (simulated)

* The inner counter is the same counter: left of the frontier the digits follow the outer rule, and the left-end
  events (carry3, carry9, merges, and new nested runs) are the outer ones, because the counter's left end *is* the
  tape's left end. Only the right end differs: a frontier inside the passed region W.
* The frontier eats W six cells per X→Y→X pair of sweeps: from X it eats `0 0 1 0 1 0` (Lean, proved) or `1 0 1 0 1 0`
  (the rest of a longer token; other end shapes, not yet formalized), from Y nothing.
* A nested run started from a sweep in phase φ makes `W' = U^a T* E_φ W`, where T* are the passed digits (all odd,
  because a nested run starts only when every digit is odd), `U^a` is left when the first digit is 2a+1 > 1, and
  `E_φ` is the end piece of φ: `0 0 1` (outer end, P), `B1` (X), `B1 1 1 0` (Y). So at every sweep start,
  `W ∈ R (B1 (110)? R)* 0 0 1` with `R = U* T*` (simulated on all runs above; never violated by real runs).
* End of a region: depth 1 (frontier reaches the final `0 0 1`): the run continues at the outer end in phase Q (or
  P, or X/Y with nothing to the right). Depth ≥ 2 (frontier reaches a boundary B1): the next region is
  "closed up": the head runs right turning it into one large odd digit; with more regions behind, constructed
  cases end in P, Q, or back at a depth-1 frontier (`data/` runs in this README's history; e.g. W with regions
  [2],[5] → Q with a new digit 45 in `P(6; 1^30)`). None halts.
* Depth ≥ 3 was not reached from any of 60 random starts in 3·10^7 steps (`tools/deep.py`): the counter reaches its
  left end at super-exponentially growing intervals, so deep nesting needs huge passed regions. A proof still has to
  cover every depth; the region language above is depth-free.

### 3. Halting forms

The machine halts only when a right-moving head (B, C, D, then F in 115779's names) meets `0 0 1 1`. In every test
above no halt occurred, and no reachable halting form was found. In the region language above, `1 1` occurs only in
the Y end piece `B1 1 1 0` (heuristic: whether the frontier can meet it in a bad phase is part of the open frontier
case analysis below).

Random right contexts are **not** safe: X/Y starts with a random W over {`0`, `1 0`, `1 1 0`} halt in about 10% of
cases (1,911 of 20,000), fully random W in about 10% too. Random *orders of the material blocks* {U, T, B1, B1 110}
with any of the three outer-end pieces never halted (0 of 60,000), but produce block types outside the grammar
(B_n with n ≡ 0 or 1 mod 3, partial `(1 0)` runs). So the invariant has to keep the passed-region grammar, not just
"material".

Q phase: Q occurs with last digits other than 1 (for example `P(6;[3])` ends in `Q r=3 [0,0,0,1,2]`; from P starts,
3,642 of 5,461 Q endings have last digit 2). Every Q sweep takes 25 steps and is local: `Q(ds ++ [d]) → P(ds ++ [d+1, 0])`
for every d (now proved in Rocq, `q_sweep`).

### 4. Revised estimate after stage 1

The nested run has a finite description (a regular language for W plus a finite set of frontier events), and it
recurses only through the left-end rule, which is the same at every depth. Nothing found points to a halt or to
unbounded case lists. But the frontier has more cases than the Lean files cover (partial tokens U, the Y end piece,
region boundaries, closing up, several outer-end phases), so a hand proof is at the upper end of the estimate
(4–6 weeks) unless a closed language can be built (stage 2).

## Stage 2: closed tape language

### Generic deciders: none closes

* busycoq `RWL_mod` in Rocq (`decide_nonhalt`, 236 settings of block size 1/2/3/6, mod 3/6, cap 2/4, windows 2–8,
  tail 0–2, on 23154, 115779 and TM567, 60 s each): all `false` or timeout (`data/rwl_coq_grid_results.txt`).
* mxdys's C++ deciders (ccz181078/TM `main.cpp` built for 6 states, same algorithms as busycoq's): `RWL_mod`
  1,296 settings (`data/tmtools_grid_rwl.txt`), `CPS_LRU` and `NG` 1,680 settings (`data/tmtools_grid_cps_ng.txt`,
  about half completed in the time limit): none decides any of the three machines.

This agrees with the explorer's note: the generic window languages forget the far structure (block lengths mod 3
of the passed region and the left end).

### Hand-built language (in progress)

`tools/ctl.py` is a CTL checker with explicit DFAs and the semantics of busycoq's CTL / `MITMDFA` certificate (a
head between cells facing a side, DFAs read each half from the far end, predecessor enumeration on moves). A
closed result can be exported as `MITMDFA` arrays (`mitm_cert`) and checked in Rocq. The DFAs are built from
regular expressions (`lang2.py`): left `0* 1^(3a) (0 1^(3d+2))* (0 1*)? .{0,3}`; right
`NEAR (U | T | B1 | B1 110)* END`, times a tracker of the last few cells and of 1-run and `10`-run lengths mod 6.
Status: **not closed**. Every remaining failure is a spurious abstract path through transient near-head forms
(carry at the left end, nest start, closing up, outer-end phases); the real runs stay inside the language
(`outside.py`). A generic alternative (left half as its last K runs, right half as its last K alternating segments,
lengths mod 6, `lang3.py`) blows up (over 200,000 DFA states for K ≥ 4, no closure for K ≤ 3).

Conclusion of stage 2 for now: a closed language is not cheap here. A hand-built one needs the exact frontier case
list, which is the same knowledge the hand proof needs; so I went on to stage 3, which also gives the case list.

## Stage 3: the hand proof in Rocq (in progress)

`rocq/` (build: `coqc -Q ../../../verify BusyCoq -Q . M23154 FILE` in `rocq/`, in the order of `_CoqProject`;
requires `verify/Individual62.vo`, built by `make Individual62.vo` in `verify/`). All files use 23154's own state
names; everything is *proved (Rocq)*, no admits, and `Print Assumptions` of every theorem below prints
"Closed under the global context".

| file | content |
|---|---|
| `M23154Rules.v` | 17 piece rules for all parameters (`es`): `tail_left`, `left_odd`, `left_even`, `turn_zero`, `turn_even`, `right_odd`, `tail_right`, `carry3`, `carry9`, `phase2`, `x_left`, `y_left`, `x_right`, `y_right`, `nest_start` |
| `M23154Sweep.v` | digits (`enc`), `left_pass`, `right_pass` (induction over the odd digits), **`sweep_zero`, `sweep_even`** (one sweep for every digit list), **`raw_zero`, `raw_even`** (merge into the leftmost block) |
| `M23154Carry.v` | **`carry3_sweep`, `carry9_sweep`** (left end, r = 3 and r = 6j+9), `phase2_sweep`, and **`q_sweep`** (the Q phase for any last digit; new, not in the Lean files) |
| `M23154Reach.v` | **`reach_D0`**: `c0 -->* Q (raw 3) [0,0,1,1,1,0,2,1^10]` (by computation, `solve_init`) |
| `M23154Inner.v` | `core_zero`, `core_even` (a sweep's core for any right context), `close_rpass`, **`inner_X_zero`, `inner_X_even`, `inner_Y_zero`, `inner_Y_even`** (inner sweeps eating passed digits 1), **`nest_sweep`** (start of a nested run, first digit 1) |

This re-proves in Rocq every theorem of the explorer's Lean files except the computed runs (`MacroRun`, `Rle`,
`Nested`, `RunLong`, `Reduce`), which only matter for finite prefixes.

### What remains (the frontier program)

The part no one has formalized, and the bulk of the remaining work:

1. **Arrivals.** Every right pass ends as `z <* [1;1;1] {{B}}> T`, after rebuilding the blocks `B_(3k+2)` at the
   front of T (`right_pass`). Then T starts with an end piece (`0 0 1` + blank; `B1`; `B1 1 1 0`) followed by W. A
   frontier lemma is needed for each way the next blocks can start: `B1` followed by `B2` (done: `x_right`),
   `B1 1 1 0` (done: `y_right`), `B1` followed by `U` (it is read as `B_(3a+1)`; simulated: it eats U and the next
   token in one sweep and stays in X), `B1` followed by `B1` (a region boundary: closing up), `B1` followed by the
   final end, `0 0 1` + blank (done: `tail_right`), and the outer-end variants after a region end (X/Y with blank
   right, `0 0 1 0 1`).
2. **Nest starts in every phase and with any first digit.** `nest_sweep` covers the outer P phase with first digit
   1. Needed: first digit 2a+1 > 1 (leaves `U^a`), and nests that start from an inner sweep (end pieces `B1`,
   `B1 1 1 0`), i.e. `W' = U^a T* E_φ W`.
3. **Closing up** a region when the frontier meets a boundary, for each phase, and its end at the next boundary or
   the final end.
4. **The invariant**: macro configurations (r, digits, phase, W) with W in the grammar
   `R (B1 (110)? R)* 0 0 1`, R = `U* T*` (or the closure of this under the frontier events, if larger), plus the
   proof that every macro step (an outer sweep, an inner sweep, a left-end event, a nest start, a frontier event)
   maps the set into itself in at least one machine step; then `progress_nonhalt` from `reach_D0`.
5. **115779 and TM567**: 115779 needs its own reach lemma (blank → `P (raw 3) [0,2,2,1,1,1,1,1,2,0]` at step
   2,340, a renamed copy of the rules); TM567 follows from 23154 through `Eqv_v2` (`TM567.eqv`).

Items 1–3 are a finite case list (every case seen in simulation so far is one of a few block patterns), and each
case is an `es`-provable rule plus bookkeeping like `inner_X_zero`. The case list has to be completed first by
simulation (`tools/rpass.py`, `tools/exh.c`), then each case proved.

### Revised estimate

Done in this session: stage 0, stage 1, the stage 2 attempts, and the Rocq foundation (all known rules). Left:
items 1–5, about 3–4 weeks of focused work by the stage-1 picture; the main risk is that the closure of the region
grammar under the frontier events is larger than the grammar seen in real runs (the random-order test produced
new block types), which would make the invariant longer but, from everything seen, still finite. Nothing so far
meets a switching criterion (no halt, no unbounded case list, not twice over the estimate).
