# Stage 2: fast pass, warning signs, scores (simulated; nothing proved)

- `data/fastpass.jsonl`: per machine, the K probes (K = 1..8, 0.5 s each) and the main run (15 s, best K).
  All 520 ran; **none halted** in the fast pass (it reaches 10^10 to 10^17 steps, usually less than the
  community's own runs).
- `data/analysis.json`: simulation signs and metrics (`tools/analyze.py`).
- `data/compare.json`, `data/compare_bonus.json`: resemblance to the studied machines 13 and #9 (`tools/compare.py`).
- `data/scores.json`: score, reasons, simulation and note signs (`tools/score.py`); `TABLE.md` and `data/table.tsv`:
  all 520 ranked (`tools/table.py`).
- Logs of the fast pass are not committed (about 60 MB); rerun with
  `python3 tools/fastpass.py ./tri data/candidates.txt OUT 0.5 15 4`.
