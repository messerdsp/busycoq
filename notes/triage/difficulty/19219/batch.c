// batch plain simulation: argv[1] = machine; stdin lines "STATE HEAD CELLS MAXSTEPS"; prints one result per line
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static char *tp; static long W = 1L << 22;
int main(int argc, char **argv) {
    const char *m = argv[1]; int tw[6][2], tm[6][2], tn[6][2];
    for (int q = 0; q < 6; q++) for (int y = 0; y < 2; y++) { const char *t = m + q * 7 + y * 3;
        if (t[0] == '-') { tn[q][y] = -1; continue; } tw[q][y] = t[0] - '0'; tm[q][y] = t[1] == 'R' ? 1 : -1; tn[q][y] = t[2] - 'A'; }
    tp = calloc(W, 1); char st[8]; long head; static char cells[1 << 20]; double N;
    while (scanf("%7s %ld %1048575s %lf", st, &head, cells, &N) == 4) {
        long n = strlen(cells), off = W / 2 - n / 2, lo = off, hi = off + n;
        for (long i = 0; i < n; i++) tp[off + i] = cells[i] - '0';
        long p = off + head; int s = st[0] - 'A'; const char *res = "RUN"; double i;
        for (i = 0; i < N; i++) { int y = tp[p]; if (tn[s][y] < 0) { res = "HALT"; break; }
            tp[p] = tw[s][y]; p += tm[s][y]; s = tn[s][y]; if (p < lo) lo = p; if (p > hi) hi = p;
            if (p <= 0 || p >= W - 1) { res = "EDGE"; break; } }
        printf("%s %.0f\n", res, i + 1); fflush(stdout);
        memset(tp + lo, 0, hi - lo + 1);
    }
    return 0;
}
