/* scan <machine> <maxsteps> <every>: at every <every>-th "RecT-like" event
   (state C, head on blank frontier, tape ends "...0 1" left of head), print the
   step and the tape from lo to the head as a raw 0/1 string. */
#include <stdio.h>
#include <stdlib.h>
#define N (1<<26)
static unsigned char tape[N];
int main(int argc, char **argv) {
  const char *m = argv[1]; long steps = atol(argv[2]); long every = atol(argv[3]);
  long from = argc > 4 ? atol(argv[4]) : 0;
  int W[6][2], Dr[6][2], Nx[6][2];
  for (int s = 0; s < 6; s++) for (int b = 0; b < 2; b++) {
    const char *t = m + 7 * s + 3 * b;
    if (t[2] == '-') { Nx[s][b] = -1; W[s][b] = 1; Dr[s][b] = 1; }
    else { W[s][b] = t[0] - '0'; Dr[s][b] = t[1] == 'R' ? 1 : -1; Nx[s][b] = t[2] - 'A'; }
  }
  long pos = N / 2, lo = pos, hi = pos; int q = 0; long ev = 0;
  /* optional initial tape (argv[5]): written from the head rightwards, state A */
  if (argc > 5) { const char *t = argv[5]; long j = pos; for (; *t; t++) { if (*t == '0' || *t == '1') tape[j++] = *t - '0'; } hi = j - 1; }
  for (long i = 1; i <= steps; i++) {
    int b = tape[pos];
    if (Nx[q][b] < 0) { printf("halt at %ld\n", i); return 0; }
    tape[pos] = W[q][b]; pos += Dr[q][b]; q = Nx[q][b];
    if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    if (q == 2 && pos == hi && tape[pos] == 0 && tape[pos-1] == 1 && tape[pos-2] == 0 && i >= from) {
      if (ev++ % every == 0) {
        printf("%ld %ld ", i, lo - N/2);
        for (long j = lo; j < pos; j++) putchar('0' + tape[j]);
        putchar('\n');
      }
    }
  }
  return 0;
}
