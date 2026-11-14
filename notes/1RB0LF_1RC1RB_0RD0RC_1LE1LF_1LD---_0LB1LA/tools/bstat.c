/* bstat TM STEPS
 * For 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA the only way to halt is  B> 0 1^r 0 0  with r odd.
 * At every event "B reads 0" this counts r (length of the 1-run after B's cell, capped at 63) and
 * whether the cell after the following 0 is 1 (safe) or 0 (dangerous when r is odd).
 * Build: gcc -O2 -o bstat bstat.c */
#include <stdio.h>
#include <stdlib.h>
#define T (1 << 23)
static unsigned char tape[T];
static long long cnt[64][2];
int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: bstat TM STEPS\n"); return 1; }
  char *m = argv[1]; long long N = atoll(argv[2]);
  int nw[6][2], mv[6][2], ns[6][2];
  for (int s = 0; s < 6; s++) for (int b = 0; b < 2; b++) {
    char *p = m + s * 7 + b * 3;
    if (p[2] == '-') ns[s][b] = -1;
    else { nw[s][b] = p[0] - '0'; mv[s][b] = p[1] == 'R' ? 1 : -1; ns[s][b] = p[2] - 'A'; }
  }
  long long pos = T / 2; int st = 0;
  for (long long i = 0; i < N; i++) {
    int b = tape[pos];
    if (st == 1 && b == 0) {
      long long p = pos + 1, r = 0;
      while (tape[p]) { r++; p++; }
      cnt[r > 63 ? 63 : r][tape[p + 1]]++;
    }
    if (ns[st][b] < 0) { printf("HALT %lld\n", i); return 0; }
    tape[pos] = nw[st][b]; pos += mv[st][b]; st = ns[st][b];
  }
  for (int k = 0; k < 64; k++)
    if (cnt[k][0] + cnt[k][1])
      printf("r=%d%s  then 0 1: %lld   then 0 0: %lld\n", k, k == 63 ? "+" : "", cnt[k][1], cnt[k][0]);
  return 0;
}
