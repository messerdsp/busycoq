// runcfg.c: run a 6-state 2-symbol machine from a given configuration (plain one-cell simulation).
// usage: runcfg MACHINE STATE HEAD CELLS MAXSTEPS
//   STATE: A..F; HEAD: index of the head's cell in CELLS (string of 0/1, blank elsewhere).
// prints "HALT steps", "RUN steps maxcells" or "EDGE steps" (left the 2^25-cell window).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: runcfg MACHINE STATE HEAD CELLS MAXSTEPS\n"); return 2; }
    const char *m = argv[1]; int s = argv[2][0] - 'A'; long head = atol(argv[3]); const char *cells = argv[4];
    double N = atof(argv[5]);
    int tw[6][2], tm[6][2], tn[6][2];
    for (int q = 0; q < 6; q++) for (int y = 0; y < 2; y++) {
        const char *t = m + q * 7 + y * 3;
        if (t[0] == '-') { tn[q][y] = -1; continue; }
        tw[q][y] = t[0] - '0'; tm[q][y] = t[1] == 'R' ? 1 : -1; tn[q][y] = t[2] - 'A';
    }
    long W = 1L << 25; char *tp = calloc(W, 1); long n = strlen(cells), off = W / 2 - n / 2;
    for (long i = 0; i < n; i++) tp[off + i] = cells[i] - '0';
    long p = off + head, lo = p, hi = p;
    for (double i = 0; i < N; i++) {
        int y = tp[p];
        if (tn[s][y] < 0) { printf("HALT %.0f\n", i + 1); return 0; }
        tp[p] = tw[s][y]; p += tm[s][y]; s = tn[s][y];
        if (p < lo) lo = p; if (p > hi) hi = p;
        if (p <= 0 || p >= W - 1) { printf("EDGE %.0f\n", i + 1); return 0; }
    }
    if (getenv("DUMP")) {   // same format as plaind: "DUMP state headpos cells" trimmed
        long a = 0, b = W - 1; while (a < p && !tp[a]) a++; while (b > p && !tp[b]) b--;
        printf("DUMP %c %ld ", 'A' + s, p - a); for (long i = a; i <= b; i++) putchar('0' + tp[i]); putchar('\n'); return 0;
    }
    printf("RUN %.0f %ld\n", N, hi - lo + 1);
    return 0;
}
