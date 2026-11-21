#!/bin/bash
# Exactness check of tri.c: for random candidates, every K = 1..8 and two step budgets, compare tri's final
# configuration (state, head position, trimmed tape; DUMP=1) with a plain one-cell simulator run for the same
# number of steps. usage: exact_check.sh TRI PLAIND candidates.txt
TRI=$1; PL=$2; bad=0; n=0
for m in $(awk '{print $2}' "$3" | shuf -n 25 --random-source=<(yes)); do for k in 1 2 3 4 5 6 7 8; do for N in 3e6 4e7; do
  o=$(DUMP=1 $TRI $m $k $N 20); st=$(echo "$o" | head -1 | sed 's/.*steps=\([0-9]*\).*/\1/')
  d1=$(echo "$o" | grep '^DUMP'); d2=$($PL $m $st); n=$((n+1))
  if [ "$d1" != "$d2" ]; then bad=$((bad+1)); echo "MISMATCH $m K=$k steps=$st"; fi
done; done; done
echo "configurations compared: $n, mismatches: $bad"
