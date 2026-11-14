/* samp TM STEPS STATE SYM [L|R|A]
 * Direct simulation from blank tape; prints the run-length encoded visited tape each time the
 * machine is in STATE reading SYM with the head at the right end (R, default), left end (L)
 * or anywhere (A).  For 1RB0LF_1RC1RB_0RD0RC_1LE1LF_1LD---_0LB1LA use "C 0 R" (sample point).
 * Build: gcc -O2 -o samp samp.c */
#include <stdio.h>
#include <stdlib.h>
#define T (1 << 23)
static unsigned char tape[T];
int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: samp TM STEPS STATE SYM [L|R|A]\n"); return 1; }
  char *m = argv[1]; long long N = atoll(argv[2]);
  int S = argv[3][0] - 'A', Y = atoi(argv[4]); int where = argc > 5 ? argv[5][0] : 'R';
  int nw[6][2], mv[6][2], ns[6][2];
  for (int s = 0; s < 6; s++) for (int b = 0; b < 2; b++) {
    char *p = m + s * 7 + b * 3;
    if (p[2] == '-') ns[s][b] = -1;
    else { nw[s][b] = p[0] - '0'; mv[s][b] = p[1] == 'R' ? 1 : -1; ns[s][b] = p[2] - 'A'; }
  }
  long long pos = T / 2, lo = pos, hi = pos; int st = 0;
  for (long long i = 0; i < N; i++) {
    int b = tape[pos];
    if (st == S && b == Y && ((where == 'R' && pos == hi) || (where == 'L' && pos == lo) || where == 'A')) {
      printf("%lld |", i);
      long long p = lo;
      while (p <= hi) {
        int v = tape[p]; long long q = p;
        while (q <= hi && tape[q] == v) q++;
        if (p <= pos && pos < q) {
          if (pos > p) printf(" %d^%lld", v, pos - p);
          printf(" [%c]", 'A' + st);
          printf(" %d^%lld", v, q - pos);
        } else printf(" %d^%lld", v, q - p);
        p = q;
      }
      printf("\n");
    }
    if (ns[st][b] < 0) { printf("HALT %lld\n", i); return 0; }
    tape[pos] = nw[st][b]; pos += mv[st][b]; st = ns[st][b];
    if (pos < lo) lo = pos;
    if (pos > hi) hi = pos;
    if (pos <= 1 || pos >= T - 2) { printf("OOB\n"); return 0; }
  }
  return 0;
}
