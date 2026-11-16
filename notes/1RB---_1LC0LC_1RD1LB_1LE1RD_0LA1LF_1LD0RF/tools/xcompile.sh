#!/bin/bash
# xcompile.sh DIR : compile every E*.v without a .vo, 4 at a time; resumable after restarts
cd "$1"
ls E*.v | while read f; do [ -f "${f%.v}.vo" ] || [ -f "$f.failed" ] || echo "$f"; done | \
  xargs -P 4 -I{} sh -c 'VERIFY=$VERIFY timeout 3000 coqc -Q ${VERIFY:-../../../../verify} BusyCoq {} > {}.log 2>&1 || touch {}.failed'
echo "compiled: $(ls E*.vo 2>/dev/null | wc -l) of $(ls E*.v | wc -l); failed: $(ls *.failed 2>/dev/null | wc -l)"
