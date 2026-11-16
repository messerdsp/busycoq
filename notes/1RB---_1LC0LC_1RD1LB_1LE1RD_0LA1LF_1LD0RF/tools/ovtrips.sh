#!/bin/bash
# ovtrips.sh INIT MAXSTEPS OUT : log only long trips (overflows) and a sample every 2^20 rounds
INIT=$1 SKEL=1 ./chainb 1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF $2 -1 - 2>/dev/null | awk '{n++; if (NR>2 && $1-p > 30*(p-pp+1) && $1-p > 1e6) {print "TRIP", $1-p; print pl; print; fflush()} else if (n % 1048576 == 0) {print "S", $0; fflush()} pp=p; p=$1; pl=$0} END{print "END", $0}' | cut -c1-600 > $3
