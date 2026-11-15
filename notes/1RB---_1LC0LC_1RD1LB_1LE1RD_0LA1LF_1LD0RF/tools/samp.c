// samp MACHINE FROM TO EVERY OUT: at each step in [FROM,TO) where the head is at the left end of the visited
// region, write "step state" and the tape lo..hi (0/1) on one line (every EVERY-th such event).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int c, char **v) {
    const char *m = v[1]; long long A = atoll(v[2]), Z = atoll(v[3]), E = atoll(v[4]);
    int tw[6][2], tm[6][2], tn[6][2];
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tm[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    long long W = 1 << 26; unsigned char *T = calloc(W, 1); long long h = W / 2, lo = h, hi = h; int s = 0; long long ev = 0;
    FILE *f = strcmp(v[5], "-") ? fopen(v[5], "w") : stdout;
    for (long long k = 0; k < Z; k++) {
        int y = T[h]; if (tn[s][y] < 0) { printf("halt at %lld\n", k); return 1; }
        T[h] = tw[s][y]; h += tm[s][y]; s = tn[s][y];
        if (h < lo) lo = h; if (h > hi) hi = h;
        if (k + 1 >= A && h == lo && (ev++ % E) == 0) {
            fprintf(f, "%lld %c ", k + 1, 'A' + s);
            for (long long p = lo; p <= hi; p++) fputc('0' + T[p], f);
            fputc('\n', f);
        }
    }
    fclose(f); return 0;
}
