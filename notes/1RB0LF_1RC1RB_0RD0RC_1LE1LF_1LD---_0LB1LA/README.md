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

## 5. Reproduce

```bash
cd notes/1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA/tools
python3 sbc9.py check                                   # self-test against the direct run
python3 sbc9.py count 110000000000 30 70                # counter from a small start (section 3)
gcc -O2 -o samp samp.c && ./samp 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 3000000 C 0 R | head -60
gcc -O2 -o bstat bstat.c && ./bstat 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA 1000000000
```

Analysis by messerdsp, with Claude Opus 5.5.
