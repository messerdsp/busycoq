/* Sweep-start events of 115779's table (states as in 115779), cell by cell (simulated).
   Events: P/Q (B on 0, blank right), X (E on 1 entered from B on 1, left ...0 1 1, right 1 0), Y (F on 0 entered
   from D on 1, left ...0 1 1 1 0, right 0 1 0).  For every event prints: step, event, depth (number of `0 0 1 0`
   boundaries + 1 in the passed region, 0 for P/Q), r, number of digits, and the passed region's shape with tokens
   0 0 (1 0)^(3k+2) collapsed to T and runs of T collapsed to T*.
   Usage: sweeps MODE ... where MODE is
     blank23154 STEPS EVERY          (23154 from blank: 115779's table started in E)
     blank115779 STEPS EVERY
     P|Q r d1,d2,... STEPS EVERY     (start from P(raw r) ds or Q(raw r) ds)
   EVERY: print every EVERY-th event (events with depth >= 2 and shape changes are always printed if SHAPES=1).
   Halting prints HALT. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N (1<<27)
static unsigned char tape[N];
static const char *TM = "1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---";
static int W[6][2], D[6][2], S[6][2];
static char shp[1 << 16];
static char seen[4096][128]; static int nseen = 0;
/* shape of tape[a..b] (inclusive), tokens collapsed */
static void shape(long long a, long long b, char *out, int max) {
  int o = 0; long long i = a; int lastT = 0;
  while (i <= b && o < max - 8) {
    if (tape[i] == 0 && i + 1 <= b && tape[i + 1] == 0) {
      long long j = i + 2; long long n = 0;
      while (j + 1 <= b + 1 && tape[j] == 1 && tape[j + 1] == 0) { j += 2; n++; }
      /* token must be followed by a 0 (next token or boundary) or be at the end */
      if (n >= 2 && (n - 2) % 3 == 0 && (j > b || tape[j] == 0)) {
        if (!lastT) { out[o++] = 'T'; out[o++] = '*'; out[o++] = ' '; lastT = 1; }
        i = j; continue;
      }
    }
    lastT = 0; out[o++] = '0' + tape[i]; i++;
    if (i <= b && tape[i] == 0 && i + 1 <= b && tape[i + 1] == 0) out[o++] = ' ';
  }
  out[o] = 0;
}
int main(int argc, char **argv) {
  for (int i = 0; i < 6; i++) for (int b = 0; b < 2; b++) {
    const char *c = TM + 7 * i + 3 * b;
    if (c[2] < 'A' || c[2] > 'F') { S[i][b] = -1; continue; }
    W[i][b] = c[0] - '0'; D[i][b] = c[1] == 'R' ? 1 : -1; S[i][b] = c[2] - 'A';
  }
  long long pos = N / 2, lo, hi, lstart = N / 2; int st; long long steps, every; int ai;
  const char *only = getenv("SHAPES");
  if (!strcmp(argv[1], "blank23154")) { st = 'E' - 'A'; ai = 2; }
  else if (!strcmp(argv[1], "blank115779")) { st = 0; ai = 2; }
  else {
    int r = atoi(argv[2]); char *ds = argv[3]; long long p = pos;
    char *cells = malloc(1 << 26); int n = 0;
    for (int k = 0; k < r; k++) cells[n++] = 1;
    char *tok = strtok(ds, ",");
    while (tok) { int d = atoi(tok); cells[n++] = 0; for (int k = 0; k < 3 * d + 2; k++) cells[n++] = 1; tok = strtok(NULL, ","); }
    char ph = argv[1][0];
    if (ph == 'X' || ph == 'Y') {
      /* X: [ds] 0 1 1 E> 1 0 W ;  Y: [ds] 0 1 1 1 0 F> 0 1 0 W ;  W = argv[4] as a 0/1 string */
      const char *lw = ph == 'X' ? "011" : "01110"; for (const char *q = lw; *q; q++) cells[n++] = *q - '0';
      const char *rw = ph == 'X' ? "10" : "010";
      for (int k = 0; k < n; k++) tape[p - n + k] = cells[k];
      long long q = p; for (const char *c = rw; *c; c++) tape[q++] = *c - '0';
      for (const char *c = argv[4]; *c; c++) tape[q++] = *c - '0';
      st = ph == 'X' ? 4 : 5; ai = 5; pos = p; lstart = p - n;
      /* the first event must still count: pretend the entering transition */
    } else {
    cells[n++] = 0; cells[n++] = 1;
    if (ph == 'Q') { cells[n++] = 1; cells[n++] = 1; cells[n++] = 1; }
    for (int k = 0; k < n; k++) tape[p - n + k] = cells[k];
    st = 1; ai = 4; pos = p; lstart = p - n;
    }
  }
  steps = (long long)atof(argv[ai]); every = atoll(argv[ai + 1]);
  lo = pos - (1 << 20); hi = pos;
  long long lmin = lstart, rmax = pos; { long long q = pos; while (q < pos + (1 << 22) && !(tape[q] == 0 && tape[q+1] == 0 && tape[q+2] == 0 && tape[q+3] == 0)) q++; if (q > rmax) rmax = q - 1; }
  int pst = -1, pb = -1; long long nev = 0;
  for (long long t = 0; t < steps; t++) {
    int b = tape[pos];
    if (S[st][b] < 0) { printf("HALT %lld\n", t); return 0; }
    char ev = 0;
    if (st == 1 && b == 0 && pos >= rmax) ev = 'P';
    else if (st == 4 && pst == 1 && pb == 1 && b == 1 && tape[pos - 1] == 1 && tape[pos - 2] == 1 && tape[pos - 3] == 0 && tape[pos + 1] == 0) ev = 'X';
    else if (st == 5 && pst == 3 && pb == 1 && b == 0 && tape[pos - 1] == 0 && tape[pos - 2] == 1 && tape[pos - 3] == 1 && tape[pos - 4] == 1 && tape[pos - 5] == 0 && tape[pos + 1] == 1 && tape[pos + 2] == 0) ev = 'Y';
    if (ev) {
      nev++;
      long long a = lmin; while (tape[a] == 0) a++;
      long long r = 0; while (tape[a + r] == 1) r++;
      long long nd = 0; for (long long k = a + r; k < pos; k++) if (tape[k] == 0 && tape[k + 1] == 1) nd++;
      long long e = rmax; while (e > pos && tape[e] == 0) e--;
      int depth = 0;
      if (ev == 'P') {
        if (tape[pos - 2] == 1) ev = 'Q';
        shp[0] = 0;
      } else {
        long long s0 = pos + (ev == 'X' ? 2 : 3);
        shape(s0, e, shp, sizeof shp);
        depth = 0; for (char *q = shp; (q = strstr(q, "001")); q++) depth++;
      }
      int pr = (every > 0 && nev % every == 0);
      if (only) {
        int found = 0;
        for (int k = 0; k < nseen; k++) if (!strncmp(seen[k], shp, 127)) { found = 1; break; }
        if (!found && nseen < 4096) { strncpy(seen[nseen++], shp, 127); pr = 1; }
      }
      if (depth >= 3) pr = 1;
      if (pr) printf("%lld %c depth=%d r=%lld nd=%lld | %.300s\n", t, ev, depth, r, nd, shp);
    }
    pst = st; pb = b;
    tape[pos] = W[st][b]; pos += D[st][b]; st = S[st][b];
    if (pos < lmin) lmin = pos; if (pos > rmax) rmax = pos;
    if (pos < 8 || pos > N - 8) { printf("OUT\n"); return 1; }
  }
  printf("END %lld events\n", nev);
  return 0;
}
