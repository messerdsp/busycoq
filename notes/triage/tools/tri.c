// tri.c: triage block-chain simulator for any 6-state 2-symbol machine, generalized from
// notes/1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF/tools/chainb.c (branch bb6-1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF).
//
// Tape = L stack | back | R stack, each stack a list of runs of identical K-cell blocks. A macro step simulates the
// machine on the 2K-cell window [back, facing] until the head leaves it; a run of identical facing blocks is crossed
// at once when one copy returns the same state, direction and back block. Exact (same configurations as the plain
// machine at macro boundaries). Block size K is a run-time argument (1..8).
//
// usage: tri MACHINE K MAXSTEPS SECONDS [LOG]
//   prints one summary line to stdout:
//     K=.. result=HALT|LOOP|RUN steps=.. cells=.. runs=.. macro=.. chain=.. secs=.. recL=.. recR=..
//   with LOG: writes samples
//     S steps cellsL cellsR runsL runsR bigruns maxrun          at steps crossing 2^(i/4)
//     E side steps cellsL cellsR runs | runlist                  at returns to an end of the visited tape
//         (side L: head at the left end moving left; R: at the right end moving right), the first 2000 such
//         returns and then those whose index crosses 1.02^j; runlist = whole tape as block^count, or a skeleton
//         (runs with count >= 3, gaps as [n]) when the tape has more than 120 runs.
//   env EFROM=x [ECAP=n]: also log every return after step x (at most n of them; default 20000) for drift tests.
//   env INIT=file: start from a logged tape ("SIDE STATE runs..." with the back block in parentheses).
//   env CKPT=file: when SECONDS are up, run on to the next return to an end and write the tape there in INIT format
//     (result=CKPT); a long run can then be continued in segments.
//   env DUMP=1: print the final configuration cell by cell (for exact_check.sh).
//   env SHAPE=1 [SHAPEMAX=n SHAPECAP=m]: at end returns (while the tape has < n runs, default 3000) reduce the tape
//     to its shape (every run as block and min(count, 3)) and log a line
//       C side steps distinct_shapes_so_far shape_changes is_new runs state | tape
//     whenever the shape differs from the last one seen at the same side and state (at most m lines).
//   env VOCAB=1 [VOCABMAX=n]: at end returns (tape < n runs, default 5000) collect every window of 3 consecutive runs
//     (block, count capped at 3) and log  V side steps windows_so_far new_windows runs state | tape  when new ones appear.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
typedef unsigned __int128 u128;
static int K, MK;
static int tw[6][2], tmv[6][2], tn[6][2];
typedef struct { uint32_t steps; uint16_t w0, w1; uint8_t ns, exitR, valid; } MT;
static MT *mt;
static MT *macro(int s, int dr, int back, int fac) {
    MT *m = &mt[(((size_t)(s * 2 + dr)) << (2 * K)) | (size_t)back << K | fac];
    if (m->valid) return m;
    int c[16];
    int lo = dr ? back : fac, hi = dr ? fac : back;
    for (int i = 0; i < K; i++) { c[i] = lo >> i & 1; c[K + i] = hi >> i & 1; }
    int p = dr ? K : K - 1, st = s; uint32_t n = 0;
    for (;;) {
        int y = c[p];
        if (tn[st][y] < 0) { m->valid = 2; m->steps = n + 1; return m; }   // halting transition counts as a step
        c[p] = tw[st][y]; p += tmv[st][y]; st = tn[st][y]; n++;
        if (p < 0 || p >= 2 * K) break;
        if (n > 1000000) { m->valid = 3; return m; }
    }
    int a = 0, b = 0; for (int i = 0; i < K; i++) { a |= c[i] << i; b |= c[K + i] << i; }
    m->w0 = a; m->w1 = b; m->ns = st; m->exitR = p >= 2 * K; m->steps = n; m->valid = 1; return m;
}
typedef struct { uint64_t n; uint32_t b; uint32_t pad; } Run;
typedef struct { Run *r; long len, cap; } Stack;
static void push(Stack *s, int b, uint64_t n) {
    if (s->len && s->r[s->len - 1].b == (uint32_t)b) { s->r[s->len - 1].n += n; return; }
    if (s->len == s->cap) { s->cap = s->cap ? 2 * s->cap : 1024; s->r = realloc(s->r, s->cap * sizeof(Run)); }
    s->r[s->len].b = b; s->r[s->len].n = n; s->r[s->len].pad = 0; s->len++;
}
static int pop1(Stack *s) {
    if (!s->len) return 0;
    int b = s->r[s->len - 1].b; if (--s->r[s->len - 1].n == 0) s->len--; return b;
}
static void pr128(FILE *f, u128 x) { char buf[48]; int i = 47; buf[i] = 0; if (!x) buf[--i] = '0'; while (x) { buf[--i] = '0' + x % 10; x /= 10; } fputs(buf + i, f); }
static void prb(FILE *f, int b) { for (int k = 0; k < K; k++) fputc('0' + (b >> k & 1), f); }
static u128 cells(Stack *s) { u128 c = 0; for (long i = 0; i < s->len; i++) c += s->r[i].n; return c * K; }
// whole tape left to right: L bottom..top, back, R top..bottom
static void prtape(FILE *f, Stack *L, int back, Stack *R) {
    long nr = L->len + R->len + 1;
    if (nr <= 120) {
        for (long i = 0; i < L->len; i++) { fputc(' ', f); prb(f, L->r[i].b); if (L->r[i].n > 1) fprintf(f, "^%llu", (unsigned long long)L->r[i].n); }
        fputs(" (", f); prb(f, back); fputc(')', f);
        for (long i = R->len - 1; i >= 0; i--) { fputc(' ', f); prb(f, R->r[i].b); if (R->r[i].n > 1) fprintf(f, "^%llu", (unsigned long long)R->r[i].n); }
    } else {
        long gap = 0;
        for (long i = 0; i < L->len; i++) {
            if (L->r[i].n >= 3) { if (gap) fprintf(f, " [%ld]", gap); gap = 0; fputc(' ', f); prb(f, L->r[i].b); fprintf(f, "^%llu", (unsigned long long)L->r[i].n); }
            else gap += L->r[i].n;
        }
        gap++;  // back
        for (long i = R->len - 1; i >= 0; i--) {
            if (R->r[i].n >= 3) { if (gap) fprintf(f, " [%ld]", gap); gap = 0; fputc(' ', f); prb(f, R->r[i].b); fprintf(f, "^%llu", (unsigned long long)R->r[i].n); }
            else gap += R->r[i].n;
        }
        if (gap) fprintf(f, " [%ld]", gap);
    }
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: tri MACHINE K MAXSTEPS SECONDS [LOG]\n"); return 2; }
    const char *m = argv[1]; K = atoi(argv[2]); double MAXS = atof(argv[3]); double SECS = atof(argv[4]);
    if (K < 1 || K > 8) return 2;
    MK = (1 << K) - 1;
    FILE *lg = argc > 5 ? fopen(argv[5], "w") : NULL;
    mt = calloc((size_t)12 << (2 * K), sizeof(MT));
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-' || t[2] == 'Z' || t[2] == 'H') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tmv[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    Stack L = {0}, R = {0}; int back = 0, s = 0, dr = 1;
    if (getenv("INIT")) {
        // start from a logged tape: one line "SIDE STATE run run ... (back) run ...", runs as BLOCK or BLOCK^N, K cells
        // each; SIDE L: head at the left end moving left (nothing left of the tape); R: at the right end moving right.
        FILE *f = fopen(getenv("INIT"), "r"); if (!f) { fprintf(stderr, "no INIT file\n"); return 2; }
        char *line = NULL; size_t cap = 0; if (getline(&line, &cap, f) <= 0) return 2; fclose(f);
        char *tok = strtok(line, " \n"); char side = tok[0]; tok = strtok(NULL, " \n"); s = tok[0] - 'A';
        Run *tmp = NULL; long nt = 0, ct = 0, bi = -1;
        while ((tok = strtok(NULL, " \n"))) {
            int isb = tok[0] == '('; char *q = tok + isb; int b = 0;
            for (int k = 0; k < K; k++) b |= (q[k] - '0') << k;
            uint64_t n = 1; char *c = strchr(tok, '^'); if (c) n = strtoull(c + 1, NULL, 10);
            if (nt == ct) { ct = ct ? 2 * ct : 1024; tmp = realloc(tmp, ct * sizeof(Run)); }
            tmp[nt].b = b; tmp[nt].n = n; tmp[nt].pad = 0; if (isb) bi = nt; nt++;
        }
        if (bi < 0) { fprintf(stderr, "INIT: no (back) block\n"); return 2; }
        back = tmp[bi].b;
        for (long i = 0; i < bi; i++) push(&L, tmp[i].b, tmp[i].n);
        for (long i = nt - 1; i > bi; i--) push(&R, tmp[i].b, tmp[i].n);
        dr = side == 'R';
        free(tmp);
    }
    u128 steps = 0; long nchain = 0, nsingle = 0, recL = 0, recR = 0; double ethr = 2000;
    int awayL = 1, awayR = 1; double nexts = 1; int qs = 0;
    const char *res = "RUN";
    clock_t t0 = clock(); long iter = 0;
    while ((double)steps < MAXS) {
        static int stopping = 0; static const char *ckpt = (const char *)1;
        if (ckpt == (const char *)1) ckpt = getenv("CKPT");
        if ((++iter & 4095) == 0 && !stopping && (double)(clock() - t0) / CLOCKS_PER_SEC > SECS) { if (!ckpt) break; stopping = 1; }
        Stack *F = dr ? &R : &L, *Bk = dr ? &L : &R;
        int fac = F->len ? (int)F->r[F->len - 1].b : 0;
        MT *x = macro(s, dr, back, fac);
        if (x->valid != 1) { if (x->valid == 2) { steps += x->steps; res = "HALT"; } else res = "LOOP"; break; }
        int far = dr ? x->w0 : x->w1, near = dr ? x->w1 : x->w0;
        if (x->exitR == dr && x->ns == s && near == back && F->len) {
            uint64_t cnt = F->r[F->len - 1].n; F->len--;
            push(Bk, far, cnt); steps += (u128)x->steps * cnt; nchain++;
        } else {
            pop1(F); nsingle++; steps += x->steps;
            if (x->exitR == dr) { push(Bk, far, 1); back = near; }
            else { push(F, near, 1); back = far; }
            s = x->ns; dr = x->exitR;
        }
        // returns to an end of the visited tape
        int atL = !dr && L.len == 0, atR = dr && R.len == 0;
        if (atL && awayL) { recL++; awayL = 0; }
        if (!atL) awayL = 1;
        if (atR && awayR) { recR++; awayR = 0; }
        if (!atR) awayR = 1;
        if (stopping && (atL || atR)) {    // checkpoint: the tape at this return, in INIT format
            FILE *cf = fopen(ckpt, "w");
            fprintf(cf, "%c %c", atL ? 'L' : 'R', 'A' + s);
            for (long i = 0; i < L.len; i++) { fputc(' ', cf); prb(cf, L.r[i].b); if (L.r[i].n > 1) fprintf(cf, "^%llu", (unsigned long long)L.r[i].n); }
            fputs(" (", cf); prb(cf, back); fputc(')', cf);
            for (long i = R.len - 1; i >= 0; i--) { fputc(' ', cf); prb(cf, R.r[i].b); if (R.r[i].n > 1) fprintf(cf, "^%llu", (unsigned long long)R.r[i].n); }
            fputc('\n', cf); fclose(cf); res = "CKPT"; break;
        }
        if (lg && ((atL && recL && awayL == 0 && iter) || (atR && awayR == 0))) {
            static long lastL = -1, lastR = -1;
            int fresh = atL ? (recL != lastL) : (recR != lastR);
            static int shapemode = -1; static long shapemax = 3000, shapecap = 200000, shapeout = 0, ndist = 0, nchg = 0;
            static uint64_t *seen = NULL, lasth[2][8];
            if (shapemode < 0) {
                shapemode = getenv("SHAPE") != NULL;
                if (getenv("SHAPEMAX")) shapemax = atol(getenv("SHAPEMAX"));
                if (getenv("SHAPECAP")) shapecap = atol(getenv("SHAPECAP"));
                if (shapemode) seen = calloc((size_t)1 << 22, sizeof(uint64_t));
            }
            if (fresh && shapemode && L.len + R.len < shapemax) {
                // shape = side, state, back block and every run as (block, min(count, 3)); log when it changes
                uint64_t h = 1469598103934665603ULL ^ (uint64_t)(atL * 7 + s) * 1099511628211ULL ^ (uint64_t)back * 0x9E3779B97F4A7C15ULL;
                for (long i = 0; i < L.len; i++) h = (h ^ ((uint64_t)L.r[i].b << 2 | (L.r[i].n < 3 ? L.r[i].n : 3))) * 1099511628211ULL;
                h = (h ^ 0xABCDEF) * 1099511628211ULL;
                for (long i = R.len - 1; i >= 0; i--) h = (h ^ ((uint64_t)R.r[i].b << 2 | (R.r[i].n < 3 ? R.r[i].n : 3))) * 1099511628211ULL;
                if (!h) h = 1;
                size_t mask = ((size_t)1 << 22) - 1, j = h & mask; int isnew = 0;
                while (seen[j] && seen[j] != h) j = (j + 1) & mask;
                if (!seen[j] && ndist < (long)(mask / 2)) { seen[j] = h; ndist++; isnew = 1; }
                if (h != lasth[atL][s]) {
                    nchg++; lasth[atL][s] = h;
                    if (shapeout++ < shapecap) {
                        fprintf(lg, "C %c ", atL ? 'L' : 'R'); pr128(lg, steps);
                        fprintf(lg, " %ld %ld %d %ld %c |", ndist, nchg, isnew, L.len + R.len + 1, 'A' + s);
                        prtape(lg, &L, back, &R); fputc('\n', lg);
                    }
                }
            }
            static int vocab = -1; static long vmax = 5000, vcap = 50000, vout = 0, nwin = 0;
            static uint64_t *wset = NULL; static uint64_t *tok = NULL; static long tokcap = 0;
            if (vocab < 0) {
                vocab = getenv("VOCAB") != NULL;
                if (getenv("VOCABMAX")) vmax = atol(getenv("VOCABMAX"));
                if (vocab) wset = calloc((size_t)1 << 22, sizeof(uint64_t));
            }
            if (fresh && vocab && L.len + R.len + 1 < vmax) {
                // local vocabulary: windows of 3 consecutive runs (block, count capped at 3; the back block marked)
                long nt = L.len + R.len + 1;
                if (nt > tokcap) { tokcap = 2 * nt; tok = realloc(tok, tokcap * sizeof(uint64_t)); }
                long q = 0;
                for (long i = 0; i < L.len; i++) tok[q++] = (uint64_t)L.r[i].b << 2 | (L.r[i].n < 3 ? L.r[i].n : 3);
                tok[q++] = (uint64_t)back << 2 | 1ULL << 40;
                for (long i = R.len - 1; i >= 0; i--) tok[q++] = (uint64_t)R.r[i].b << 2 | (R.r[i].n < 3 ? R.r[i].n : 3);
                long newc = 0;
                for (long i = 0; i + 2 < q; i++) {
                    uint64_t h = ((tok[i] * 0x9E3779B97F4A7C15ULL) ^ (tok[i + 1] * 0xC2B2AE3D27D4EB4FULL) ^ (tok[i + 2] * 0x165667B19E3779F9ULL)) | 1;
                    size_t mask = ((size_t)1 << 22) - 1, j = (h ^ (h >> 29)) & mask;
                    while (wset[j] && wset[j] != h) j = (j + 1) & mask;
                    if (!wset[j] && nwin < (long)(mask / 2)) { wset[j] = h; nwin++; newc++; }
                }
                if (newc && vout++ < vcap) {
                    fprintf(lg, "V %c ", atL ? 'L' : 'R'); pr128(lg, steps);
                    fprintf(lg, " %ld %ld %ld %c |", nwin, newc, nt, 'A' + s);
                    prtape(lg, &L, back, &R); fputc('\n', lg);
                }
            }
            if (fresh) {
                if (atL) lastL = recL; else lastR = recR;
                long idx = recL + recR;
                static double efrom = -1; static long ecap = 0, eout = 0;
                if (efrom < 0) { efrom = getenv("EFROM") ? atof(getenv("EFROM")) : 1e300; ecap = getenv("ECAP") ? atol(getenv("ECAP")) : 20000; }
                int late = (double)steps >= efrom && eout < ecap;
                if (late) eout++;
                if (idx <= 2000 || idx >= ethr || late) {
                    if (idx > 2000) while (ethr <= idx) ethr *= 1.02;
                    fprintf(lg, "E %c ", atL ? 'L' : 'R'); pr128(lg, steps);
                    fputc(' ', lg); pr128(lg, cells(&L)); fputc(' ', lg); pr128(lg, cells(&R));
                    fprintf(lg, " %ld %c |", L.len + R.len + 1, 'A' + s);
                    prtape(lg, &L, back, &R); fputc('\n', lg);
                }
            }
        }
        if (lg && (double)steps >= nexts) {
            uint64_t mx = 0; long big = 0;
            for (long i = 0; i < L.len; i++) { if (L.r[i].n > mx) mx = L.r[i].n; if (L.r[i].n >= 3) big++; }
            for (long i = 0; i < R.len; i++) { if (R.r[i].n > mx) mx = R.r[i].n; if (R.r[i].n >= 3) big++; }
            fprintf(lg, "S "); pr128(lg, steps); fputc(' ', lg); pr128(lg, cells(&L)); fputc(' ', lg); pr128(lg, cells(&R));
            fprintf(lg, " %ld %ld %ld %llu\n", L.len, R.len, big, (unsigned long long)mx);
            while (nexts <= (double)steps) nexts = pow(2, ++qs / 4.0);
        }
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("K=%d result=%s steps=", K, res); pr128(stdout, steps);
    printf(" cells="); pr128(stdout, cells(&L) + cells(&R) + K);
    printf(" runs=%ld macro=%ld chain=%ld secs=%.2f recL=%ld recR=%ld\n", L.len + R.len + 1, nsingle + nchain, nchain, secs, recL, recR);
    if (lg) { fprintf(lg, "F %s ", res); pr128(lg, steps); fputc(' ', lg); prtape(lg, &L, back, &R); fputc('\n', lg); fclose(lg); }
    if (getenv("DUMP") && !strcmp(res, "RUN")) {   // exact check: "DUMP state headpos cells" (cells left to right)
        long nb = 2; for (long i = 0; i < L.len; i++) nb += L.r[i].n; for (long i = 0; i < R.len; i++) nb += R.r[i].n;
        if (nb * K > 50000000) return 0;
        char *t = malloc(nb * K + 1); long q = 0, head = -1;
        for (long i = 0; i < L.len; i++) for (uint64_t j = 0; j < L.r[i].n; j++) for (int k = 0; k < K; k++) t[q++] = '0' + (L.r[i].b >> k & 1);
        if (!dr) { if (!L.len) for (int k = 0; k < K; k++) t[q++] = '0'; head = q - 1; }   // facing = L top (or a blank block)
        for (int k = 0; k < K; k++) t[q++] = '0' + (back >> k & 1);
        if (dr) { head = q; if (!R.len) for (int k = 0; k < K; k++) t[q++] = '0'; }      // facing = R top (or a blank block)
        for (long i = R.len - 1; i >= 0; i--) for (uint64_t j = 0; j < R.r[i].n; j++) for (int k = 0; k < K; k++) t[q++] = '0' + (R.r[i].b >> k & 1);
        t[q] = 0;
        long a = 0, b = q - 1; while (a < head && t[a] == '0') a++; while (b > head && t[b] == '0') b--;
        t[b + 1] = 0; printf("DUMP %c %ld %s\n", 'A' + s, head - a, t + a);
    }
    return 0;
}
