// dump MACHINE STEPS OUT: run from blank tape, write "step state head lo" line then the cells lo..hi as 0/1 chars
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int c, char **v) {
    const char *m = v[1]; long long N = atoll(v[2]);
    int tw[6][2], tm[6][2], tn[6][2];
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tm[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    long long W = 1 << 26; unsigned char *T = calloc(W, 1); long long h = W / 2, lo = h, hi = h; int s = 0;
    for (long long k = 0; k < N; k++) {
        int y = T[h]; if (tn[s][y] < 0) { printf("halt at %lld\n", k); return 1; }
        T[h] = tw[s][y]; h += tm[s][y]; s = tn[s][y];
        if (h < lo) lo = h; if (h > hi) hi = h;
        if (h <= 0 || h >= W - 1) { printf("tape\n"); return 1; }
    }
    FILE *f = fopen(v[3], "w");
    fprintf(f, "%lld %c %lld %lld\n", N, 'A' + s, h - lo, hi - lo + 1);
    for (long long p = lo; p <= hi; p++) fputc('0' + T[p], f);
    fputc('\n', f); fclose(f); return 0;
}
