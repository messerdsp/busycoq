#!/bin/bash
d=$1; V=$((3914+d)); f=var/v$V
sed "s/110101^3914 /110101^$V /" ${IN:-before_overflow_V3914.txt} > $f.in   # IN: tape shortly before an overflow, first frozen wall 3914
TRIPMIN=1e18 MARKER=$V MAXR=2e7 DUMPANY=1 NR=40 DUMP=${f}_ ./ovr $f.in > $f.log 2>&1
r=$(ls ${f}_00.txt 2>/dev/null)
if [ -n "$r" ]; then echo "$V $(python3 skelr.py $r 40 | tail -1)" > $f.res; else echo "$V NONE" > $f.res; fi
