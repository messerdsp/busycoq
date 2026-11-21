# Difficulty follow-up: are the 13-like machines easier than 13, and which top-10 machines look doable?

November 2026, after the triage in `README.md`. **Everything here is simulation. Nothing is proved.** The tests
are heuristics that try to say *how much a proof would have to know*. Outputs are in `difficulty/` and
`deep/`, and the tools are in `tools/`.

## Update (20 Nov 2026)

New ccz181078/busycoq PRs since the triage (Alex Havrilla, 19 Nov):
* **#105 proves 144438 halts**, which agrees with the "halting candidate" finding below;
* **#104 proves 65980 never halts.**

busycoq's `verify/Eqv_v2.v` already proves that 23154 halts iff `1RB0RD_0LC0RF_1RD0LB_1RE0LA_1RA1RC_1LB---`
halts (TM567), and that 44531 halts iff `1RB0LD_1LC0RC_1RD1LA_1RB1RE_0LC1RF_---1RA` halts (TM421).

## Short answers

* **Easier than 13:** 23154 (with its twin 115779) clearly; 19219 (+44531, 157488) and 97939 (+ twin 99198)
  probably. All three keep the tape to a list of at most about 35 runs, against 13's 6 million. All three
  survive every perturbation and every scaled run-out test, and their notes already contain most of the local
  rules in Lean.
* **Not easier: 144438.** Scaled-down copies of its real tape **halt in 25 of 44 cases** when the far block runs
  out, and changing block sizes by ±12 flips the outcome. It is better seen as a **halting candidate**, a coin flip
  at each far-block run-out. It is **not** a quick halt by simulation: the real far block (about 2,840 words at
  10^18) wears about 100 words per decade of steps, so it lasts to roughly 10^45 to 10^50 steps.
* **13:** probably non-halting, and possible in principle. Nothing in these tests is random, and its overflow
  rule conserves mass. But its tape has 6 million runs after the second overflow, new unit types appear at every
  overflow, and its notes show two different overflow types plus a rule that drifts for small walls. Of all the
  machines here it needs the largest proof: research-level, months rather than weeks.
* **The rest of the top 10:**
  * **112769 moves up.** Its Collatz-like front map (y ↦ 4y/3, by y mod 3) chooses between branches, but no
    random size or residue made it halt (0 of 260). So a proof may be able to treat the residue as arbitrary.
  * **65980 moves down.** It is robust, but its structure keeps changing at the largest scale: whole-tape
    conversion passes and new local windows in every decade.
  * **40361** stays hard: it depends on a residue relation between neighbours.
  * **149064** stays undecoded (up to about 176 runs, with a structural jump near 10^15).
  * **5380 and 78071** could not be tested this way (tens of thousands of runs).

## The tests

1. **Tape size** (`tri.c` S lines): the largest number of runs on the tape late in a 10-minute run. A small
   bounded number means the configuration is a short list of integers, so a proof is about a finite-dimensional
   map.
2. **Local vocabulary** (`tri.c` with `VOCAB=1`, `tools/vocabstats.py`): every window of 3 consecutive runs (block,
   count capped at 3) at every return to an end; how many new ones appear per decade of steps. Saturation means a
   finite set of local pieces. New windows late mean new kinds of structure. With the 6-cell grid, rotations of a
   period-3 background inflate the count (97939 at K = 6), so 97939 was rerun at K = 3.
3. **Perturbation** (`tools/perturb.py`, plain simulator `tools/runcfg.c`, 60 starts × 3·10^8 steps each): start
   from the real late tape with
   * every long run resized at random with its residue mod 12 kept (*residue*),
   * resized with its residue random (*free*),
   * resized with residues kept and the short-run segments between long runs shuffled, i.e. a random arrangement
     of the tape's own digit words (*permute*).

   Halts mean non-halting depends on exact relations between the numbers.
   * Controls: #9, whose notes say random counters hit a bad overflow quickly, halts in 18 of 30 permuted
     starts and 31 of 60 free starts.
   * Two machines proved non-halting in merged busycoq PRs halt 0/60 and 1/60 in permute mode, so 1/60 is noise.
   * **Antihydra halts in none: this test cannot see Collatz-type hardness**, only fragile arrangements.
4. **Run-out** (`perturb.py --maxc 60`, 12 starts × 10^10 steps): every long run small, so worn blocks run out
   many times within the run.
5. **Scaled restarts** (`tools/scaled.py`, `tools/scan144438.py`, accelerated `tri.c` with `INIT`): the real late
   tape with every long run divided by 16 … 4096 (residues kept, ±12 jitter), as 13's notes did with walls
   divided by 256. Worn blocks then run out within reach. A scaled copy is not a configuration of the real run.
   A halt there shows the structure is not robust at that event; it does not show that the real run halts.
6. **Machine-specific**:
   * 115779 (23154's table, other start): random digit-list tapes of the form in its notes, and tapes that start a
     nested run at once (`tools/nested115779.py`, 100 each × 10^9 steps);
   * 112769: 200 more free-mode starts;
   * 144438: 52 scaled copies at 13 scales.

The new simulator modes were checked before use. `INIT` reproduces the plain simulator's configuration
exactly: 16 of 16 tapes, plus one 27.6-million-cell scaled 144438 tape after 2·10^9 steps. The 400-configuration
exactness check of `tri.c` still passes with the new code.

## Results

| machine | runs late (13 = 6 million) | new windows late | perturbation: residue / free / permute (halts of 60) | run-out (of 12) | scaled restarts | other |
|---|---|---|---|---|---|---|
| 13 (studied) | 6,012,654 from 1.37·10^15 (cascade) | not trackable after the cascade | 0 / 0 / 0 | 0 | 0 of 8 (1/2 … 1/16) | notes: new unit types after every overflow, two overflow types |
| **23154** (+115779) | ≤ 34 | **none after 5.3·10^11** (8 decades to 1.25·10^20) | 0 / 0 / 0 | 0 | 0 of 10 | 115779: random digit lists 0/100, forced nested runs 0/100 |
| **19219** (+44531, 157488) | ≤ 27 (14 to 17 late) | only at big overflows (1e13, 1e16, +24 at 3.3·10^19) | 0 / 0 / 0 | 0 | 0 of 10 | real run to 4.8·10^20 with no halt; two far blocks used up near 3.3·10^19 without a halt |
| **97939** (+99198) | ≤ 35 | at K = 3 only at timer refills (1e14, 1e16, 1e18) | 0 / 0 / 0 | 0 | 0 of 10 | notes: CTL fails; the invariant must be numeric |
| 144438 | ≤ 38 | nearly saturated | **24 of 200 / 0 / 1 of 60** | – | **25 of 44 halt** (1/40 … 1/192); 0 of 18 at other scales within time | halting outcome flips with ±12 jitter |
| 112769 (+152969) | ≤ 24 | only at level resets | 0 / **0 of 260** / 10 of 60 | 0 | 0 of 9 | Collatz-like front map; level order matters (permute) |
| 65980 | ≤ 19 | **17 to 35 in every decade** | 0 / 0 / 0 | 0 | 0 of 10 | whole-tape conversion passes (e.g. near 8.9·10^18) |
| 40361 | 33 | (not run) | 0 / **60 / 60** | – | – | depends on a residue relation between neighbours (known charge argument) |
| 149064 | up to 176 | jump near 10^15, then a few | 0 / 0 / 0 | – | – | not decoded |
| #9 (control, studied) | – | – | 0 / 31 / 18 of 30 | – | – | known lottery |
| Antihydra (control) | – | – | 0 / 0 / 0 | – | – | cryptid: this test cannot see it |

## Per machine

**23154 (+115779): the best candidate, and easier than 13.**
* *What it is* (busy-beaver-explorer notes): an odometer on digits written as blocks `0 1^(3d+2)`, swept once per
  increment. Every ordinary sweep is proved in Lean. The one open piece is the *nested run*: the counter counting
  inside its own passed region. The inner sweeps of a nested run are already proved to follow the same digit rule.
  The only slow quantity is a run of digit 1 that a middle cluster eats about 3 digits per factor 10 of sweeps.
  At that rate the next nested run is about 10^800 sweeps away (their estimate).
* *What the tests add:* the local vocabulary stops growing after 5.3·10^11 steps. Random digit lists and forced
  nested runs never halted (200 starts × 10^9 steps). No perturbation, run-out or scaled restart halted.
* *What a proof would need:*
  * the nested run as a theorem (a recursion: the same rule one level down);
  * an invariant "the tape is a stack of digit lists and passed regions".

  Because every form in the notes is regular once block lengths are taken mod 3, a hand-built closed tape
  language that keeps lengths mod 3 is worth trying. The notes say generic CTL searches failed precisely because
  they lose lengths mod 3.
* *Difficulty:* medium. Weeks, not months, if the nested-run induction goes through. The twin 115779 comes along
  for free (same table).

**19219 (+44531, 157488): probably easier than 13.**
* *What it is:* a base-4 countdown on a bit word, with a timer and frozen far blocks that lose a little at each
  overflow. The notes have a map that reproduces the run exactly to 10^19, and 9 rules in Lean. The far end is
  closed under borrows (128 suffixes, none halts) as long as the last far block lasts.
* *What the tests add:*
  * the real run reaches 4.8·10^20 steps with no halt, and two inner far blocks were used up there without a halt;
  * the tape never exceeds 31 runs;
  * no perturbation, run-out or scaled restart (down to 1/4096, where far blocks run out repeatedly) halted.
* *What a proof would need:* the overflow map in closed form for any k, and the far-end closure extended to the
  cases where far blocks are used up. The tests suggest that closure holds generally.
* *Difficulty:* medium-hard. It is the same kind of obstacle as 13's (wear at growing scales), but on a list of
  fewer than 30 numbers with a finite far-end closure already found. One proof covers three holdouts.

**97939 (+99198): probably easier than 13, but its invariant is numeric.**
* *What it is:* a base-4 counter feeding timers that lose 9, 24, 96, 384 per right-end visit and are refilled when
  used up. Halting needs an E-chain on a run of length 2 mod 3. In the notes, CTL with counter classes failed
  because small timers in the abstraction reach the bad residue.
* *What the tests add:* at most 35 runs; new windows only at refills; no halt in any perturbation (including free
  and permuted), run-out, or scaled restart down to 1/4096.
* *What a proof would need:* a numeric invariant such as "every timer is at least its decrement, or one of a few
  small shapes", together with residues mod 3 and 12. The tests suggest the real dynamics keep it.
* *Difficulty:* medium-hard; the twin's run from state B comes with it.

**144438: not easier; a halting candidate.**
* *What the tests show:*
  * residue-kept perturbations halt 24 of 200 times, mostly when the far-end run is small;
  * scaled copies halt 25 of 44 times at scales 1/40 to 1/192, at the event where the far block (2,957 words in the
    real tape at 7·10^17, wearing slowly) runs out;
  * ±12 changes in block sizes decide whether a copy halts.

  So the next far-block run-out of the real run looks like a coin flip that depends on exact sizes: a lottery at
  each run-out, not a structure a proof can rely on.
* *Timing:* the far block wears about 90 to 100 words per decade of steps in the real run (3,672 at 10^10, 2,840 at
  10^18; `difficulty/144438/far_block_wear.txt`). The 1/16 copy reached the same rate before its 173-word block ran
  out near 10^18. So the run-out comes after about B/100 decades for a far block of B words: roughly 10^45 to 10^50
  steps for the real tape. (A first extrapolation by scale factor, about 10^21 to 10^22, was wrong: the time is set
  by the far block's size, not by the scale of the other blocks.)
* *Next steps:* a halting argument would have to predict the exact block sizes at that run-out, far beyond
  simulation: an accelerator at the level of the counter (one step per refill event), like the explorer's for
  40361. A non-halting proof looks hard, maybe cryptid-like.
* *Difficulty:* hard either way; the most interesting open question here is whether it halts.

**112769 (+152969): upgraded from "Collatz-like risk" to "medium".**
* *What it is:* the front level follows y ↦ 4y/3 (y ≡ 0), 4(y−2)/3+2 (y ≡ 2), and a separate reset regime for
  y ≡ 1, so the residues look irregular.
* *What the tests show:* none of 260 starts with random sizes *and* random residues halted. So the Collatz-like
  map seems only to choose between safe branches, and a proof can treat y mod 3 as arbitrary if every branch is
  proved safe. Permuting the level order does cause halts (10 of 60), so the invariant needs an order or size
  relation between levels.
* *What a proof would need:* the y ≡ 1 regime (a secondary bouncer) and the level resets as closed rules. Both are
  listed as open in its notes; the sweep and clean phases are proved in Lean.
* *Difficulty:* medium-hard.

**65980: downgraded.** It is robust in every test, but new local windows appear in every decade (1,398 in all).
The whole tape is rewritten from time to time (a conversion pass near 8.9·10^18, `001001`/`100100` words). Its
structure is still changing at the largest scale simulated. A proof needs the nested register levels and the
conversion pass as rules. Medium-hard to hard.

**40361:** residue-kept perturbations never halt, but free and permuted ones always do. That matches its notes:
non-halting rests on a mod-3 relation between neighbouring groups, and on a race decided about 10^12 rounds out.
It is hard and is being worked on elsewhere.

**149064:** robust in every perturbation, but up to 176 runs, with a jump in structure near 10^15; its counter
has not been decoded. Medium-hard, with little known.

**5380, 78071:** tens of thousands of irregular runs, so these tests do not apply. They stay hard.

## Is 13 possible?

Evidence for:
* no randomness anywhere in these tests (0 halts in every perturbation mode, run-out and scaled restart);
* its notes find a numerical overflow rule that conserves mass (`8V/9 + 4(V/3)/3 = 4V/3`) and holds within
  about 10 blocks for walls from 1.7·10^6 down to about 1,000;
* the regular chain is proved in Rocq, and 534 end-region transitions are proved.

Evidence that it is large:
* after the second overflow the tape is a frozen cascade of about 6 million runs;
* new unit types appear after every overflow;
* there are two different overflow types (type 2 rebuilds the whole chain, type 3 rewrites one frozen unit);
* the overflow rule drifts for walls below about 150 words.

A proof needs a uniform description of the whole nested structure (a grammar of unit types and a cascade
invariant), not a fixed list of rules.

Assessment: probably non-halting and provable in principle, but by far the largest effort of the machines here.
23154 and 19219 have the same kind of hard part (wear at growing scales) on a tape of fewer than 35 runs.

## Long runs (144438)

* **The 1/16 copy halts too**, at step 1.67·10^18 after its start (`difficulty/144438/scale16_run.txt`). Its far
  block went 173 → 6 words between 10^14 and 10^18 and the machine halted at the far end right after it ran out.
* The 1/8 copy (far block 369 at the start) was at 2.0·10^19 steps with 271 words left and no halt when it was
  stopped. The 1/4 copy and the real tape were stopped early, once the wear rate showed that the real event is out
  of reach. Checkpoint and resume (`tools/longrun.py`, `tri.c` with `CKPT`) are exact against the plain simulator,
  and the checkpoints are in `difficulty/144438/`, so the runs can be resumed:

      python3 tools/longrun.py ./tri 1RB1LE_1LC1RE_1LE1LD_1LC0LA_1RF0LA_---0RA 6 DIR 1200 200 difficulty/144438/real_ckpt.txt OFFSET

  with OFFSET from `difficulty/144438/real_offset.txt`.
