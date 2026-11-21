# Notes: `1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD` (19219), with 44531 and 157488

First fallback after 23154 (see branch `bb6-1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---`, README section
"Decision: switch to the first fallback": 23154's documented sweep forms contain halting configurations, and
excluding them needs control of every future nested run).

Labels: *proved (Rocq)*, *proved elsewhere (Lean, not ported)*, *simulated*, *heuristic*.

Branch created from `master` and fast-forwarded to this fork's `BB6` (= ccz181078/busycoq `BB6` at `33209bc`).

## Stage 0 (checked 21 Nov 2026)

### Is anyone else on it? No.

* **ccz181078/busycoq `BB6`** (last commit 3 Nov 2026): the family occurs only in `verify/Eqv_v2.v` module TM421
  (`halts 1RB0LD_1LC0RC_1RD1LA_1RB1RE_0LC1RF_---1RA <-> halts 44531`). No non-halting proof.
* **Open PRs** (all `refs/pull/N/head`, up to #109; diffs and commit messages, canonical forms by
  `notes/triage/tools/canon.py`): none mentions 19219, 44531, 157488 or TM421's partner.
* **Wiki**: no page for any of the three; the newest BB(6) list is still the 608 of 30 Oct 2026.
* **Spreadsheet**: all three "Skelet 1-like Class 1", no status, no notes.
* **AI artifact** (read as data): all three status `little`, simulated to 3.3·10^19 (19219, 157488) and 10^17 (44531).
* **busy-beaver-explorer** (clone of 20 Nov 2026, status "as of 8 November 2026"): folders for all three; verdict
  "open". Main prior work, summarized below.

### What is known

| id | machine | relation |
|---|---|---|
| 19219 | `1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD` | reference |
| 44531 | `1RB1RE_1LC0RC_1RA1LD_1RB0LA_0LC1RF_---1RD` | same table started in another state (exact table comparison); halts iff TM421's partner halts (`Eqv_v2`, proved (Rocq) in busycoq) |
| 157488 | `1RB1LD_1RC1RF_1LA1RD_1RE0LB_---0RA_0LA1RC` | same tape as 19219 at every step of the first 10^9 (observed, not proved) |

From the explorer (19219's README; *proved elsewhere (Lean, not ported)* where marked):

* Tick start: `0^∞ 1110 (111110)^n 1 A> [word] 0^∞`, n even; right of the head the tape is a bit string in cell pairs
  `1b`. Blocks v = `101110` (bits `010`); separators r `0`, q `10`, p `001`, s `1`. A tick is a base-4 borrow.
* Lean (kernel): `tick_r`, `tick_q`, `tick_q2`, `tick_p`, `tick_p1`, `tick_s`, `tick_w` (wall), `overflow_2`,
  `overflow_3` (overflow F1 with 2 and 3 blocks); halting configurations; no halt in 10^7 steps.
* Simulated: the macro map reproduces all 22,198 tick boundaries of the first 6·10^9 steps; run alone it reaches
  10^19 steps (205 events, 89 overflows), no halting event. Far end: 102 far ends seen, closed under borrow arrivals
  to 128, none halts; all fall into the cycle `11 → (overflow) → 0011 → 11`, in which the last block loses one per
  overflow. So no halt *while the last block lasts* (heuristic).
* Open (explorer): borrow chains and F1 for every k (induction on the list); the far-end closure as rules; **what
  the list looks like when the last block wears away**.
* Triage (`bb6-triage`, simulated): no halt to 4.8·10^20 steps; at the overflow near 3.3·10^19 two far blocks
  (644 and 494 words) were used up without a halt; at most 31 runs; robust in every perturbation and in scaled
  copies down to 1/4096 (where far blocks run out repeatedly). Estimate there: 1–2 months.

### First impression, after 23154

The lesson from 23154 applies here: the risk is a halting configuration inside the macro forms that is avoided only
by a numeric coincidence. 19219's notes already point at the place to look: the far end when the last blocks wear
out. The triage's scaled restarts (blocks run out repeatedly, no halt) are encouraging. Stage 1 should start by
searching the macro forms for halting configurations directly (as done for 23154 with `tools/exh.c` and
`tools/arrive.py` on that branch), before any proof work.

## Stage 1

(not started)
