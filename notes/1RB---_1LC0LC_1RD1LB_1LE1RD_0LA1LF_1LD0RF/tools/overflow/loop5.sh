#!/bin/bash
# loop5.sh START TAG ROUNDS NCYC: cycles of ROUNDS round starts with reset4 between; stop at a long trip (> 1e9 steps and 30x the previous)
cur=$1; tag=$2; R=$3; N=$4
for c in $(seq 1 $N); do
  MAXR=$R TRIPMIN=1e9 NR=300 STOPTRIP=1 DUMP=${tag}_c${c}_ ./ovr $cur > ${tag}_c${c}.log
  grep -q "HALT" ${tag}_c${c}.log && { echo "HALT ${tag}_c${c}.log"; exit 2; }
  if grep -q "^TRIP" ${tag}_c${c}.log; then echo "cycle $c: $(grep -m1 '^TRIP' ${tag}_c${c}.log | cut -c1-300)"; echo "LONGTRIP ${tag}_c${c}_00.txt prev $cur"; exit 0; fi
  echo "cycle $c: $(grep '^END' ${tag}_c${c}.log | cut -c1-260)"
  python3 reset4.py ${tag}_c${c}_end.txt ${tag}_c${c}_r.txt 3 > ${tag}_c${c}.reset || { echo "reset failed"; exit 1; }
  echo "   $(cat ${tag}_c${c}.reset)"
  rm -f ${tag}_c${c}_end.txt; [ $c -gt 2 ] && rm -f ${tag}_c$((c-2))_r.txt
  cur=${tag}_c${c}_r.txt
done
