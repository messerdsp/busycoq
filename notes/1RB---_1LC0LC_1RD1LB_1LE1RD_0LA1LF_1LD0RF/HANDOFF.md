# Handoff: finishing the Rocq proof

What a new session needs that is not obvious from README.md / PART3.md.

## Exact unit words (post-overflow chain, round-start cut form, *sim*)

Round start: head in state C on the blank cell left of `011111111011101` (15 cells, the head's cell first). Then
units `W^k H T` with `W = 011101` (k >= 4 at the cut, regex `(011101){4,}`), digit head H, fixed tail T.
Deep digit heads (`Dg p` in M130Rules.v): D0 `01010101010101`, D1 `0101010101111111`, D2 `011111110101010101`,
D3 `01111111010101111111`. Phase order `D0 -> D2 -> D1 -> D3 -> D0`, wall +1 on `D2 -> D1` and `D3 -> D0`, carry
on `D3 -> D0`.

* Unit 1: own heads (no separate tail), same cycle and wall rule, carry on 38 -> 32:
  32 `01010101011101010101111111010101`, 36 `011111110101011101010101111111010101`,
  34 `0101010101011111110101111111010101`, 38 `01111111010101011111110101111111010101`; order 32 -> 36 -> 34 -> 38.
* Units 2..4: deep heads plus tails
  - U2 (94) `0111111111010101011111111101111111011101011111111101010101111111110101010111010111111111010101`
  - U3 (62) `01111111110101010111010111010111111111011111110111111111010101`
  - U4 (302) `01110101111111110101111111010101011101011101011111111101111111011111111101010101111111110111111101111111110101010111010111111111011101010111010101011111110111111101111111110111111101111111110101010111010111111111010101011101011101011111111101111111011101011101011111111101010101111111110101111111010101`
* Then alternating K (tail 116) and plain deep units (tail empty):
  K `01110101111111110101010111111111011101010111010101010101110101110101111111110111111101110101111111110101111111010101`
* Then the end region (walls < 40), the band, the frozen cascade.

Checked exactly on 10,000 consecutive rounds (`tools/units_rsc.c` + `tools/units_model.py`; shrink walls to 30/31
on load). Regenerate the post-overflow tape line (`init26.txt`, 42 MB, not in git) with `tools/p3_count.c`
(`DUMP=`), or `tools/chainb.c` from the blank tape to step 2592545302250949.

## Interface facts

* A trip into a unit: entered in state D on the unit's first (cut) cell with `11` to the left; left for the last
  time in state C on cell -1 with cell -2 = 0. It leaves `[1;0;1] *> Wd^^m' *> Dg p'` right of the head; the left
  neighbour's sweep later turns cells -4..-1 into `0111`, which completes the first word `Wd`. So unit cut points
  move 4 cells left per visit, and the round-start cell moves 4 cells left per round. Describe tapes relative to
  the head, never by absolute position.
* Bounce trips read the next unit's first 2 (D0, D1) or 3 (D2) wall words, unchanged; state them with the next
  unit's wall as `Wd *> Wd^^(S m2)` (or `S (S m2)`). Walls next to the end region can be short; the end region is
  handled by the `rocq/end/` lemmas instead.
* The `rocq/end/E*.v` lemmas start when a pass carries past the last big wall (>= 40 words) and end when the head
  leaves the end region to the left; their configurations come from `data/end_entries_2.59e15_2e17.txt.gz`. They
  are stated over the visited cells only; restating them in the trip interface is part of the work.
* Only one band-crossing transition occurs to 2e17 (step 5,269,793,291,944,956); `band_pass` covers the band
  itself.

## Rocq gotchas met so far

* `l <* xs`: xs's first element is next to the head. `{{S}}> r`: head on r's first cell. `l <{{S}}`: head on l's
  last cell.
* In `match` on nat inside these files write `O`, `S O`, ... (`0`, `1` parse as tape symbols).
* `es` sometimes stalls before a short final stretch: finish with `step. step. step. finish.`
* `lpow_shift'` from Individual did not rewrite in these goals; use `lshift`/`wd_S` (in M130Rules.v). `rot_w`
  rotates `[0] *> [1;1;1;0;1;0]^^n` into `Wd^^n *> [0]`.
* Re-cut identities (`recut_D*`): `rewrite <- !wd_S`, split `[1;0;1;0]` as `[1;0;1] ++ [0]`, `rewrite
  Str_app_assoc, rot_w`, then `reflexivity`.
* `follow` sometimes needs the lemma's arguments given explicitly (`follow (unit_round_c (S n))`).
* `simpl_tape` rewrites `lpow_shift'` forward; avoid it right after turning a power around.

## Build times

P3Reach.v about 16 minutes (one core); the 534 end lemmas about 25 minutes on 4 cores (`tools/xcompile.sh`);
M130Rules.v under a minute.
