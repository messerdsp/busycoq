#!/bin/bash
# usage: run1.sh NAME TM "CERT"   -> prints NAME result time
V=/home/user/busycoq/verify
f=$(mktemp -p . t_XXXX.v)
cat > $f <<EOV
From BusyCoq Require Import CTL62.
Eval vm_compute in (decide_nonhalt (TM_from_str "$2") ($3)).
EOV
st=$(date +%s.%N)
out=$(timeout ${TMO:-150} coqc -Q $V BusyCoq $f 2>&1 | grep -o -E 'true|false|Error.*' | head -1)
en=$(date +%s.%N)
echo "$1 | $2 | $3 | ${out:-TIMEOUT} | $(echo "$en - $st" | bc)"
rm -f $f ${f%.v}.vo ${f%.v}.glob ${f%.v}.vok ${f%.v}.vos .${f#./}.aux 2>/dev/null
