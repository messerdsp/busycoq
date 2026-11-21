#!/bin/bash
# Reproduces the simulation results in ../README.md.
# Usage: gate.sh <path to the busycoq proof of 1RB0LA_1RC---_0LD1RD_1RA0RE_0RF1RC_1LF0LA (.v)>
set -e
T=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d)
M=1RB0LA_1RC---_0LD1RD_0RA0RE_0RF1RC_1LF0LA
gcc -O2 -o $W/sim $T/sim.c; gcc -O2 -o $W/scan $T/scan.c
echo "== 1. Section Gen's bounded rules (Hypothesis lines) checked on $M (SA = A)"
awk '/^Section Gen\./{g=1} g&&/^Hypothesis MF/{exit} g' "$1" | sed -n '/^Hypothesis/,$p' > $W/hyps.txt
python3 $T/rules.py $M 6 $W/hyps.txt A
echo "== 1b. exhaust with 9 zeros"
python3 $T/rules.py $M 6 $T/exhaust9.txt A
echo "== 2. RecT configurations from the blank tape (step lo base #digits leftlen), first of each kind"
$W/scan $M 40000000 1 | python3 $T/parse.py > $W/ev.txt
awk '$3=="tp"{print $1, $2, $4, $6, $(NF)}' $W/ev.txt | awk '{k=$2" "$3" "$4; if (k!=p) {print; p=k}}'
grep " n 22 " $W/ev.txt | head -1 | cut -c1-200
echo "== 3. erase of the left part"
python3 $T/erase.py
echo "== 4. runs from the junk (blank to the right), RecT configurations, first of each kind"
J=00000111111000111
J23=$(python3 -c "print('00000111111000111' + '0' * 1320 + '111111')")
for j in $J $J23; do
  echo "-- start: state A, tape ${j:0:20}... (length ${#j})"
  $W/scan $M 25000000 1 0 $j | python3 $T/parse.py > $W/evj.txt
  awk '$3=="tp"{print $1, $2, $4, $6, $(NF)}' $W/evj.txt | awk '{k=$2" "$3" "$4; if (k!=p) {print; p=k}}'
  tail -1 $W/evj.txt | cut -c1-200
done
rm -rf $W
