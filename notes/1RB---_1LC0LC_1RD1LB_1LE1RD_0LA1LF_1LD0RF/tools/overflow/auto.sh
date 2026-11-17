#!/bin/bash
# auto.sh START TAG N : repeat N overflows (loop2.sh between them), logging fsum.py summaries
cur=$1; tag=$2
for k in $(seq 1 $3); do
  python3 fsum.py $cur > ${tag}_$k.sum; cat ${tag}_$k.sum; m=$(grep MARKER ${tag}_$k.sum | awk '{print $2}')
  [ -z "$m" ] && { echo "no marker"; exit 1; }
  out=$(./loop3.sh $cur ${tag}$k 2000000 400 48 12 4 $m 2>&1 | tail -3); echo "$out" | cut -c1-150
  nxt=$(echo "$out" | grep OVERFLOW | awk '{print $2}'); [ -z "$nxt" ] && { echo "stopped"; exit 1; }
  echo "$out" | grep -q HALT && { echo HALT; exit 2; }
  cur=$nxt; echo "== overflow $k done: $cur"
done
