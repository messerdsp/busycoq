/* Exhaustive small-case test for 115779's table (states as in 115779).  Simulated, cell by cell.
   Reads start configurations from stdin, one per line:
       P r d1,..,dm            P(raw r) ds          (outer end, phase P: ... 0 1 B>0)
       Q r d1,..,dm            Q(raw r) ds          (outer end, phase Q: ... 0 1^4 B>0)
       X r d1,..,dm W          [1^r ds] 0 1 1 E> 1 0 W        (W a 0/1 string, blank after it)
       Y r d1,..,dm W          [1^r ds] 0 1 1 1 0 F> 0 1 0 W
   ("-" for an empty digit list.)  Each start is run until the next outer sweep start (P/Q event at the right end
   of the tape) after step 0, or MAXT steps.  At every sweep start on the way (P, Q, X, Y as in sweeps.c) the tape
   is checked against the documented forms:
       left part  1^r (r = 0 mod 3, r >= 3), then digits 0 1^(3d+2);
       X/Y: W in (101010)* (B1 | B1 110 | B_(3k+2))* 0 0 1, then blank, with B_n = 0 0 (1 0)^n.
   Output per start: OK|HALT|BADLEFT|BADW|TIMEOUT, steps, number of events, max nesting depth (number of B1 + 1 in
   W, i.e. regions), end phase and end r/digits.  Usage: exh MAXT < starts */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N (1 << 24)
static unsigned char tape[N];
static const char *TM = "1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---";
static int W_[6][2], D_[6][2], S_[6][2];

/* check left part tape[a..b] (inclusive): 1^r then (0 1^(3d+2))*; returns r or -1; fills digits */
static long long checkleft(long long a, long long b, int *nd, char *buf, int bufsz) {
  while (a <= b && tape[a] == 0) a++;
  long long r = 0; while (a + r <= b && tape[a + r] == 1) r++;
  if (r < 3 || r % 3) return -1;
  long long i = a + r; int o = 0; *nd = 0; o += snprintf(buf + o, bufsz - o, "r=%lld", r);
  while (i <= b) {
    if (tape[i] != 0) return -1;
    long long j = i + 1; while (j <= b && tape[j] == 1) j++;
    long long n = j - i - 1;
    if (n < 2 || (n - 2) % 3) return -1;
    if (o < bufsz - 20) o += snprintf(buf + o, bufsz - o, " %lld", (n - 2) / 3);
    (*nd)++; i = j;
  }
  return r;
}
/* check W = tape[a..] up to blank: (101010)* (B1 | B1 110 | B_(3k+2))* 001 then zeros.  returns regions or -1 */
static int checkW(long long a, long long lim) {
  long long i = a; int regions = 1;
  { int z = 1; for (int q = 0; q < 64; q++) if (tape[a + q]) { z = 0; break; } if (z) return 0; }   /* W empty: frontier at blank */
  while (tape[i] == 1 && tape[i + 1] == 0 && tape[i + 2] == 1 && tape[i + 3] == 0 && tape[i + 4] == 1 && tape[i + 5] == 0) i += 6;
  for (;;) {
    if (i > lim) return -1;
    if (tape[i] != 0 || tape[i + 1] != 0) return -1;
    long long j = i + 2, n = 0;
    while (tape[j] == 1 && tape[j + 1] == 0) { j += 2; n++; }
    if (n == 0) {           /* 0 0 1 then blank? */
      if (tape[i + 2] == 1) { long long k = i + 3; int z = 1; for (int q = 0; q < 64; q++) if (tape[k + q]) { z = 0; break; } if (z) return regions; }
      return -1;
    }
    if (n == 1) {          /* B1, maybe followed by 110; or the final 0 0 1 followed by blank */
      { int z = 1; for (int q = 0; q < 64; q++) if (tape[i + 3 + q]) { z = 0; break; } if (z) return regions; }
      regions++;
      if (tape[j] == 1 && tape[j + 1] == 1 && tape[j + 2] == 0) j += 3;
      while (tape[j] == 1 && tape[j + 1] == 0 && tape[j + 2] == 1 && tape[j + 3] == 0 && tape[j + 4] == 1 && tape[j + 5] == 0) j += 6;
      i = j; continue;
    }
    if ((n - 2) % 3 == 0) { i = j; continue; }
    /* B_n with n = 0 mod 3 or n = 1 mod 3 (n >= 3): could be B_m followed by 0 0 1 end where the last (10) is the end: allow end 0 0 1 0 0.. */
    return -1;
  }
}
int main(int argc, char **argv) {
  for (int i = 0; i < 6; i++) for (int b = 0; b < 2; b++) {
    const char *c = TM + 7 * i + 3 * b;
    if (c[2] < 'A' || c[2] > 'F') { S_[i][b] = -1; continue; }
    W_[i][b] = c[0] - '0'; D_[i][b] = c[1] == 'R' ? 1 : -1; S_[i][b] = c[2] - 'A';
  }
  long long MAXT = (long long)atof(argv[1]);
  char line[1 << 16], ph[4], ds[1 << 15], wstr[1 << 15];
  static char buf[4096];
  long long tot = 0, nok = 0, nhalt = 0, nbad = 0, nto = 0, nnest = 0;
  while (fgets(line, sizeof line, stdin)) {
    int r; wstr[0] = 0;
    if (sscanf(line, "%3s %d %s %s", ph, &r, ds, wstr) < 3) continue;
    tot++;
    long long lo = N / 2 - (1 << 22), hi = N / 2 + (1 << 22);
    static long long clo = N / 2, chi = N / 2; memset(tape + clo - 64, 0, chi - clo + 128);
    long long pos = N / 2; int n = 0; static unsigned char cells[1 << 16];
    for (int k = 0; k < r; k++) cells[n++] = 1;
    if (strcmp(ds, "-")) { char *t = strtok(ds, ","); while (t) { int d = atoi(t); cells[n++] = 0; for (int k = 0; k < 3 * d + 2; k++) cells[n++] = 1; t = strtok(NULL, ","); } }
    int st; const char *lw = "", *rw = "";
    if (ph[0] == 'P') { lw = "01"; st = 1; } else if (ph[0] == 'Q') { lw = "01111"; st = 1; }
    else if (ph[0] == 'X') { lw = "011"; rw = "10"; st = 4; } else { lw = "01110"; rw = "010"; st = 5; }
    for (const char *q = lw; *q; q++) cells[n++] = *q - '0';
    for (int k = 0; k < n; k++) tape[pos - n + k] = cells[k];
    long long q = pos; for (const char *c = rw; *c; c++) tape[q++] = *c - '0';
    for (const char *c = wstr; *c; c++) tape[q++] = *c - '0';
    long long lmin = pos - n, rmax = q; int pst = -1, pb = -1;
    long long nev = 0; int maxdep = (ph[0] == 'X' || ph[0] == 'Y') ? 1 : 0, depth0 = maxdep; const char *status = "TIMEOUT";
    char endinfo[256] = "";
    long long t;
    for (t = 0; t < MAXT; t++) {
      int b = tape[pos];
      if (S_[st][b] < 0) { status = "HALT"; break; }
      char ev = 0;
      if (st == 1 && b == 0 && pos >= rmax) ev = 'P';
      else if (st == 4 && pst == 1 && pb == 1 && b == 1 && tape[pos - 1] == 1 && tape[pos - 2] == 1 && tape[pos - 3] == 0 && tape[pos + 1] == 0) ev = 'X';
      else if (st == 5 && pst == 3 && pb == 1 && b == 0 && tape[pos - 1] == 0 && tape[pos - 2] == 1 && tape[pos - 3] == 1 && tape[pos - 4] == 1 && tape[pos - 5] == 0 && tape[pos + 1] == 1 && tape[pos + 2] == 0) ev = 'Y';
      if (ev && t > 0) {
        nev++; int nd;
        long long endl = pos - 1 - (ev == 'P' ? (tape[pos - 2] == 1 ? 5 : 2) : (ev == 'X' ? 3 : 5));
        if (ev == 'P' && tape[pos - 2] == 1) ev = 'Q';
        if (checkleft(lmin, endl, &nd, buf, sizeof buf) < 0) { status = "BADLEFT"; snprintf(endinfo, sizeof endinfo, "%c at t=%lld", ev, t); break; }
        if (ev == 'X' || ev == 'Y') {
          int reg = checkW(pos + (ev == 'X' ? 2 : 3), rmax + 8);
          if (reg < 0) { status = "BADW"; int o = snprintf(endinfo, sizeof endinfo, "%c at t=%lld W=", ev, t);
            for (long long k = pos + (ev == 'X' ? 2 : 3); k <= rmax && o < 250; k++) endinfo[o++] = '0' + tape[k]; endinfo[o] = 0; break; }
          if (reg > maxdep) maxdep = reg;
        } else { status = "OK"; snprintf(endinfo, sizeof endinfo, "%c %.200s", ev, buf); break; }
      }
      pst = st; pb = b;
      tape[pos] = W_[st][b]; pos += D_[st][b]; st = S_[st][b];
      if (pos < lmin) lmin = pos; if (pos > rmax) rmax = pos;
      if (pos < lo || pos > hi) { status = "OUT"; break; }
    }
    clo = lmin - 64; chi = rmax + 4096;
    if (!strcmp(status, "OK")) nok++; else if (!strcmp(status, "HALT")) nhalt++; else if (!strcmp(status, "TIMEOUT")) nto++; else nbad++;
    if (maxdep > depth0) nnest++;
    printf("%s | %s %lld events=%lld maxregions=%d | %s\n", strtok(line, "\n"), status, t, nev, maxdep, endinfo);
  }
  fprintf(stderr, "total %lld ok %lld halt %lld bad %lld timeout %lld nested %lld\n", tot, nok, nhalt, nbad, nto, nnest);
  return 0;
}
