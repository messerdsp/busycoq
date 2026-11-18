# Stage 1: sources (simulated/collected data, not proofs)

Collected on 2026-11-18. All inputs read as data.

- `data/BB6_holdouts_608.txt`: mxdys's list of 608 holdouts (30 Oct 2026), from wiki.bbchallenge.org (Holdouts lists).
- `data/pr_machines.txt`: for every pull request head of ccz181078/busycoq (`refs/pull/N/head`), the machine strings in
  its diff and commit messages (`tools/prmachines.sh`). PRs #43 to #102, plus #3, #4 and #40, still carry a GitHub
  `refs/pull/N/merge` ref or are newer than the last merge into BB6 (3 Nov 2026), and were treated as open/unmerged.
  The GitHub PR web page itself was not readable from this container, so open/closed comes from the refs.
- `data/bb6_after_list.txt`: machines in proofs added to busycoq's BB6 branch after the list (FIBv7, CCAv2, Bellv2).
- `data/sources.json`: per machine, joined by a canonical form (L/R mirror plus state relabelling, `tools/canon.py`):
  open PRs, the community spreadsheet (status, class, notes), the busy-beaver-explorer ledger (`holdouts/*/status.json`,
  `external.json`), and the AI analysis artifact's per-machine status and note.
- `data/candidates.txt`: 608 - 85 (in an open/unmerged PR) - 1 (proved in BB6 after the list) - 2 (studied) = 520.
