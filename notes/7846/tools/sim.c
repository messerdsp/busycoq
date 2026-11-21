/* Simple TM simulator: sim <machine> <steps> [print_every]
   Prints the tape (run-length encoded) and state at the given step counts. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N (1<<26)
static unsigned char tape[N];
int main(int argc, char **argv) {
  const char *m = argv[1]; long steps = atol(argv[2]); long every = argc > 3 ? atol(argv[3]) : 0; long from = argc > 4 ? atol(argv[4]) : 0; int onlo = every < 0; if (onlo) every = 0;
  int W[6][2], Dr[6][2], Nx[6][2];
  for (int s = 0; s < 6; s++) for (int b = 0; b < 2; b++) {
    const char *t = m + 7 * s + 3 * b;
    if (t[2] == '-' || t[2] == 'Z' || t[2] == 'H') { Nx[s][b] = -1; W[s][b] = 1; Dr[s][b] = 1; }
    else { W[s][b] = t[0] - '0'; Dr[s][b] = t[1] == 'R' ? 1 : -1; Nx[s][b] = t[2] - 'A'; }
  }
  long pos = N / 2, lo = pos, hi = pos; int q = 0;
  for (long i = 1; i <= steps; i++) {
    int b = tape[pos];
    if (Nx[q][b] < 0) { printf("halt at %ld\n", i); return 0; }
    tape[pos] = W[q][b]; pos += Dr[q][b]; q = Nx[q][b];
    int newlo = pos < lo; if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    if (pos <= 0 || pos >= N - 1) { printf("out of tape\n"); return 1; }
    if ((every && i >= from && i % every == 0) || i == steps || (onlo && newlo)) {
      printf("step %ld state %c headoff %ld lo %ld hi %ld\n", i, 'A' + q, pos - lo, lo - N/2, hi - N/2);
      /* RLE from lo to hi with head marked */
      long j = lo; 
      while (j <= hi) {
        if (j == pos) { printf("[%c%d]", 'A' + q, tape[j]); j++; continue; }
        long k = j; while (k <= hi && k != pos && tape[k] == tape[j]) k++;
        if (k - j > 3) printf(" %d^%ld ", tape[j], k - j); else for (long t = j; t < k; t++) printf("%d", tape[t]);
        j = k;
      }
      printf("\n");
    }
  }
  return 0;
}
