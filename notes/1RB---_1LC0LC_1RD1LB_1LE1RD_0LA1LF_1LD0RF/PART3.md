# Part 3: reaching the tape after the second overflow, in Rocq

Goal (README section 6, item 2): a Rocq proof that `1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF`, started on the
blank tape, reaches the round start at step 2,592,545,302,250,949 (the tape of `init26.txt`, after the second
overflow, where the post-overflow chain of section 6, item 1 runs).

Marks: **[proved]** = checked by `coqc`; **[sim]** = measured with the C tools; **[open]** = not done.

## Result

**[proved]** `rocq/p3/P3Reach.v`, theorem `reach_overflow2`:

    exists n rest,
      c0 -[ tm ]->* const S0 <{{C}} (wr 63 *> runs wr H1 (BAND^^n *> runs wr H2 rest))

* `c0` is busycoq's blank start; the right-hand side is the round start at step 2,592,545,302,250,949: head in
  state C on the blank cell left of the tape.
* `H1`: the first 158 runs of 6-cell blocks, written out with their lengths (the whole new chain up to the band:
  walls of 1,880,775, 470,195, 117,544, 29,380, ... words).
* `BAND^^n`: `n` copies of the 24-cell band word `010101 110101 011101 010111`; `n` is not stated (it is
  1,128,303 in the simulation).
* `H2`: the next 14 runs (three band blocks, the turn word and the first frozen wall, 1,692,491 blocks of `110101`).
* `rest`: the frozen cascade beyond (about 1.5 million runs), not stated.

**[proved]** `rocq/p3/P3Round.v`, theorem `reach_round_start`: the same configuration in the round-start form of
`rocq/M130Rules.v` (`prefix_turn`, `round_u1_0`):

    exists r, c0 -[ tm ]->* const 0 {{C}}> [0;1;1;1;1;1;1;1;1;0;1;1;1;0;1] *> [0;1;1;1;0;1]^^1880774 *> [0;1;1;1] *> r

Assumptions (`Print Assumptions`): only the primitive 63-bit integers and primitive arrays of Rocq's standard
library (`Uint63`, `PArray`: the operations and their specification axioms such as `add_spec`, `eqb_correct`,
`get_out_of_bounds`). No axioms of our own. The proof is by `vm_compute` (kernel conversion), no `native_compute`.

## Route

The task listed (1) a counter theory with a closed form for the overflow, (2) a verified macro simulator with
compression of multi-block periodic words. Measurement decided it: **plain `chainb` is already cheap enough**, so
neither the counter theory nor multi-block compression is needed for this part.

**[sim]** `tools/p3_count.c` (the core of `chainb.c` without the per-step `getenv` calls and per-round scans that
made the instrumented binary slow):

| round start at step | macro steps (chained + single) | rounds | runs on tape |
|---|---|---|---|
| 1,368,863,728,438,429 (before overflow 2) | 157,609,277 + 761,893,039 | 9,026,634 | 181 |
| 2,208,844,122,802,475 (after the first trip) | 258,736,431 + 1,169,753,442 | 9,026,635 | 1,499,277 |
| 2,486,893,016,200,431 (after the second trip) | 276,684,502 + 1,241,580,276 | 9,026,746 | 6,012,573 |
| 2,592,545,302,250,949 (`init26.txt`) | 294,481,453 + 1,515,810,417 = **1,810,291,870** | 11,534,337 | 6,012,626 |

The whole run from the blank tape takes 15 s in C; its final tape is byte-identical to `init26.txt`. The band is
crossed block by block (each band block is its own run), and that costs only about 9·10^8 macro steps in total
for both trips and the 2.5 million rounds after them.

So the route is: **the `chainb` scheme itself as a verified function in Rocq, run by `vm_compute`**.

## The verified simulator (`rocq/p3/P3Sim.v`) **[proved]**

Generic in the machine (a section variable `tm`), about 450 lines.

* `wsim`: the machine on a finite window, with fuel; `wsim_ok`: its result is a `-->*` between the two
  configurations, for any tape outside the window.
* Blocks and states are machine integers; `wr b` is the 6 cells of block `b` (bit i = i-th cell from the left).
  A table entry holds its own key (state and direction, back block, facing block) and the outcome (new state and
  direction, the block left behind, the new back block, two flags). `mk_entry` computes an entry with `wsim`
  and re-checks its own encoding by decoding it, so `mk_entry_spec` needs no lemma about the bit encoding.
* `check_table t`: every one of the 49,152 entries of the array `t` (and its default) equals `mk_entry` of its own
  key. `check_table_ok`: then every entry that can be read from `t` satisfies `entry_spec`. The step function
  compares the entry's key with the configuration, so no arithmetic on table indices has to be proved.
* A configuration is `Cfg sd back cl cr`: two stacks of runs `Run block (copies - 1) rest` and the back block.
  `decode` maps it to a busycoq configuration. `push` merges equal blocks (only when the 63-bit sum does not wrap),
  `pop1` takes one block (the blank block from an empty stack).
* `step`: one macro step, or a whole run of equal facing blocks at once when the entry gives back the same state,
  direction and back block (`chain_r`, `chain_l`: induction on the run length). `step_ok`:
  `decode c -->* decode (step t c)`. When no valid entry applies (a halt or fuel exhausted inside a window) `step`
  returns the configuration unchanged, which keeps it sound.
* `run t n c = N.iter n (step t) c`; **`run_ok`**: `check_table t = true -> decode c -->* decode (run t n c)`;
  `init_ok`: `decode init = c0`.
* Reading the result without printing six million runs: `shape k1 b1 b2 b3 b4 k2 c` returns the state, the back
  block, the first `k1` runs, skips copies of a 4-block word and returns the next `k2` runs; `shape_ok` turns an
  equation `shape ... = (...)` into the statement above with `exists n rest`.

`rocq/p3/P3Reach.v` is generated by `tools/p3_gen.py` from a tape line and its macro-step count: it builds the
table (`vm_compute`), proves `check_table` and the `shape` equation by `vm_cast_no_check (eq_refl ...)` (the kernel
runs the simulation once, at `Qed`) and derives the theorem.

Measured in Rocq 8.20.1 (`vm_compute`, one core):

| | time |
|---|---|
| `P3Sim.v` | TIME_SIM |
| table: build / check | about 40 s / 40 s |
| `P3Small.v`: 786,319 macro steps to step 1,000,172,375 (`reach_1e9`) | 0.4 s (2.1 million macro steps per second) |
| `P3Reach.v`: 1,810,291,870 macro steps | TIME_REACH |

## What this does and does not give

* **[proved]** The machine reaches the post-overflow round start; with the first 158 runs explicit, every wall
  length of the new chain at that moment is a literal in `H1`.
* **[open]** The statement is not yet in the form of the part-1 invariant (units with phases and symbolic walls,
  the end region as one of its 536 states, the band, the first frozen wall). That is a rewriting of `H1`/`H2`
  (finite, explicit words) once the invariant is fixed; `P3Round.v` does the first step (prefix and first wall).
  If the invariant needs more of the frozen cascade than `H2`, change `K2` in `p3_gen.py` (or extend `shape`)
  and rerun.
* **[open]** Nothing here explains the overflow. The cascade rule (W -> band 2W/3 + chain W/4, ...) stays an
  observation; it is not needed to reach this tape, but a proof of non-halting for the scaled variants or of any
  later overflow would need it or another long computation of this kind.
* The same file proves "reaches the tape at step X" for any round start X the C simulator can reach in about
  10^10 macro steps (about 80 minutes per 10^10 at the measured speed; memory grows with the number of runs).

## Reproduce

    cd tools && gcc -O2 -o p3_count p3_count.c
    DUMP=line.txt ./p3_count 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF 2592545302250949     # 15 s; prints the counts
    python3 p3_gen.py line.txt 1810291870 158 14 reach_overflow2 > ../rocq/p3/P3Reach.v
    cd ../rocq/p3 && V=../../../../verify
    coqc -Q $V BusyCoq -Q . P3 P3Sim.v && coqc -Q $V BusyCoq -Q . P3 P3Reach.v && coqc -Q $V BusyCoq -Q . P3 P3Round.v

`p3_count MACHINE STOPSTEP [INITLINE]` stops at the first round start at or after `STOPSTEP`.

## Next steps

1. Fix the part-1 invariant's round-start form and prove that the tape of `reach_overflow2` is an instance
   (unfold `H1` into the unit words of section 6; the walls become the literals above).
2. For the one band-crossing end transition: `H2` already contains the turn word and the first frozen wall.
3. Optional hardening: replace `PArray` by a pattern-matching table or `Uint63` by `N` if the primitive-integer
   axioms are unwanted (expected to be several times slower; not measured).
