#!/bin/bash
# loop3.sh START TAG ROUNDS NCYC NBMOD NBMIN MINB FW1: like loop2.sh, but an overflow is detected by the first frozen
# wall (FW1 +-20 words) disappearing (ovr MARKER); then stop with the dump ${tag}_cK_00.txt
cur=$1; tag=$2; R=$3; N=$4; NBMOD=$5; NBMIN=$6; MINB=$7; FW1=$8
python3 reset2.py $cur ${tag}_c0_r.txt $NBMOD $NBMIN $MINB $FW1 > ${tag}_c0.reset && cur=${tag}_c0_r.txt
for c in $(seq 1 $N); do
  MARKER=$FW1 MAXR=$R TRIPMIN=1e18 NR=300 DUMP=${tag}_c${c}_ ./ovr $cur > ${tag}_c${c}.log
  grep -q "HALT" ${tag}_c${c}.log && { echo "HALT in ${tag}_c${c}.log"; exit 2; }
  if grep -q "^MARKERGONE" ${tag}_c${c}.log; then echo "cycle $c: $(grep -m1 MARKERGONE ${tag}_c${c}.log)"; echo "OVERFLOW ${tag}_c${c}_00.txt"; exit 0; fi
  python3 reset2.py ${tag}_c${c}_end.txt ${tag}_c${c}_r.txt $NBMOD $NBMIN $MINB $FW1 > ${tag}_c${c}.reset; rc=$?
  if [ $rc -eq 3 ]; then mv ${tag}_c${c}_end.txt ${tag}_c${c}_r.txt; elif [ $rc -ne 0 ]; then echo "reset failed"; exit 1; else rm -f ${tag}_c${c}_end.txt; fi
  [ $c -gt 1 ] && rm -f $cur
  cur=${tag}_c${c}_r.txt
done
