#!/bin/bash
# loop4.sh START TAG ROUNDS NCYC : reset3 with no frozen wall (boundary = first band), log every cycle's skeleton, stop at a long trip
cur=$1; tag=$2; R=$3; N=$4
for c in $(seq 1 $N); do
  MAXR=$R TRIPMIN=1e9 NR=300 STOPTRIP=1 DUMP=${tag}_c${c}_ ./ovr $cur > ${tag}_c${c}.log
  grep -q "HALT" ${tag}_c${c}.log && { echo "HALT ${tag}_c${c}.log"; exit 2; }
  if grep -q "^TRIP" ${tag}_c${c}.log; then echo "cycle $c: $(grep -m1 '^TRIP' ${tag}_c${c}.log | cut -c1-300)"; echo "LONGTRIP ${tag}_c${c}_00.txt"; exit 0; fi
  echo "cycle $c: $(grep '^END' ${tag}_c${c}.log | cut -c1-300)"
  python3 reset3.py ${tag}_c${c}_end.txt ${tag}_c${c}_r.txt 48 12 4 0 > ${tag}_c${c}.reset || { echo "reset failed"; mv ${tag}_c${c}_end.txt ${tag}_c${c}_r.txt; }
  rm -f ${tag}_c${c}_end.txt; [ $c -gt 1 ] && rm -f $cur
  cur=${tag}_c${c}_r.txt
done
