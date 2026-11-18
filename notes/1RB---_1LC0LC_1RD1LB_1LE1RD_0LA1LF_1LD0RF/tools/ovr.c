#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define K 6
static int tw[6][2], tmv[6][2], tn[6][2];
typedef struct { uint32_t steps; uint16_t w0, w1; uint8_t ns, exitR, valid; } MT;
static MT *mt;
static MT *macro(int s, int dr, int back, int fac) {
    MT *m = &mt[(((size_t)(s * 2 + dr)) << (2 * K)) | (size_t)back << K | fac];
    if (m->valid) return m;
    int c[2 * K];
    int lo = dr ? back : fac, hi = dr ? fac : back;
    for (int i = 0; i < K; i++) { c[i] = lo >> i & 1; c[K + i] = hi >> i & 1; }
    int p = dr ? K : K - 1, st = s; uint32_t n = 0;
    for (;;) {
        int y = c[p];
        if (tn[st][y] < 0) { m->valid = 2; return m; }
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
    s->r[s->len].b = b; s->r[s->len].n = n; s->len++;
}
static int pop1(Stack *s) { if (!s->len) return 0; int b = s->r[s->len - 1].b; if (--s->r[s->len - 1].n == 0) s->len--; return b; }
static void pr128(FILE *f, u128 x) { char buf[48]; int i = 47; buf[i] = 0; if (!x) buf[--i] = '0'; while (x) { buf[--i] = '0' + x % 10; x /= 10; } fputs(buf + i, f); }
static void prb(FILE *f, int b) { for (int k = 0; k < K; k++) fputc('0' + (b >> k & 1), f); }
// ovr: (env PROG=n: print the head position every n macro steps; DUMPANY=1: dump at any round start, not only
// when the standard prefix is block-aligned)
// ovr: run from a tape line (INIT format of chainb: "steps state back runs...", head left of it in state C moving left)
// and log round starts: env TRIPMIN (log rounds whose trip took more than this many steps and 30 times the
// previous trip, default 1e7),
// EVERY (also log every EVERY-th round start, default 0 = never), NR (runs shown, default 400),
// MAXR (stop after this many round starts), MARKER (stop when no run of MARKER +-20 is among the first 600 runs outside band words, looking at most 20000 runs deep), STOPTRIP (stop after that many long trips), DUMP (prefix: write the full tape after each logged long trip).
// A logged line: round number, step, trip length, then a skeleton of the first NR runs: counts >= 3 as numbers,
// stretches of other runs as [k] (k blocks), a stretch of the band word 010101 110101 011101 010111 as B<words>.
static int tok2b(const char *t) { int b = 0; for (int k = 0; k < K; k++) b |= (t[k] - '0') << k; return b; }
static int BW[4];
static void skel(FILE *o, Stack *R, int back, long NR) {
    long sh = 1; long i = R->len - 1, lim = R->len - NR; if (lim < 0) lim = 0;
    // treat back as the first block (count 1)
    while (i >= lim) {
        // band?
        long j = i, w = 0;
        while (j - 3 >= 0 && R->r[j].n == 1 && (int)R->r[j].b == BW[0] && R->r[j-1].n == 1 && (int)R->r[j-1].b == BW[1]
               && R->r[j-2].n == 1 && (int)R->r[j-2].b == BW[2] && R->r[j-3].n == 1 && (int)R->r[j-3].b == BW[3]) { j -= 4; w++; }
        if (w >= 3) { if (sh) fprintf(o, "[%ld] ", sh); sh = 0; fprintf(o, "B%ld ", w); i = j; continue; }
        if (R->r[i].n >= 3) { if (sh) fprintf(o, "[%ld] ", sh); fprintf(o, "%llu ", (unsigned long long)R->r[i].n); sh = 0; }
        else sh += R->r[i].n;
        i--;
    }
    if (sh) fprintf(o, "[%ld] ", sh);
    fprintf(o, "| runs=%ld", R->len);
}
static void dump(const char *fn, u128 steps, int s, int back, Stack *R) {
    FILE *o = fopen(fn, "w"); pr128(o, steps); fprintf(o, " %c ", 'A' + s); prb(o, back);
    for (long i = R->len - 1; i >= 0; i--) { fputc(' ', o); prb(o, R->r[i].b); if (R->r[i].n > 1) fprintf(o, "^%llu", (unsigned long long)R->r[i].n); }
    fputc('\n', o); fclose(o);
}
int main(int argc, char **argv) {
    const char *m = "1RB---_1LC0LC_1RD1LB_1LE1RD_0LA1LF_1LD0RF";
    BW[0] = tok2b("010101"); BW[1] = tok2b("110101"); BW[2] = tok2b("011101"); BW[3] = tok2b("010111");
    double TRIPMIN = getenv("TRIPMIN") ? atof(getenv("TRIPMIN")) : 1e7; long EVERY = getenv("EVERY") ? atol(getenv("EVERY")) : 0;
    long NR = getenv("NR") ? atol(getenv("NR")) : 400; double MAXR = getenv("MAXR") ? atof(getenv("MAXR")) : 1e18;
    const char *DP = getenv("DUMP"); int ndump = 0; long nstop = 0; long MARK = getenv("MARKER") ? atol(getenv("MARKER")) : 0;
    mt = calloc((size_t)12 << (2 * K), sizeof(MT));
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tmv[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    Stack L = {0}, R = {0}; int back = 0, s = 0, dr = 1; u128 steps = 0;
    {
        FILE *f = fopen(argv[1], "r"); char *line = NULL; size_t lcap = 0; if (!f || getline(&line, &lcap, f) <= 0) return 2; fclose(f);
        char *tok = strtok(line, " \n"); for (char *c = tok; *c; c++) steps = steps * 10 + (*c - '0');
        tok = strtok(NULL, " \n"); s = tok[0] - 'A'; dr = 0;
        Run *tmp = NULL; long nt = 0, ct = 0; int first = 1;
        while ((tok = strtok(NULL, " \n"))) {
            int b = tok2b(tok);
            uint64_t n = 1; char *c = strchr(tok, '^'); if (c) n = strtoull(c + 1, NULL, 10);
            if (first) { back = b; first = 0; if (n == 1) continue; n--; }
            if (nt == ct) { ct = ct ? 2 * ct : 1024; tmp = realloc(tmp, ct * sizeof(Run)); }
            tmp[nt].b = b; tmp[nt].n = n; nt++;
        }
        for (long i = nt - 1; i >= 0; i--) push(&R, tmp[i].b, tmp[i].n);
    }
    u128 last = steps; double rounds = 0, prevtrip = 1e18; int away = 1, pend = 0;
    long long it = 0; long long PROG = getenv("PROG") ? atoll(getenv("PROG")) : 0;
    for (;;) {
        if (PROG && ++it % PROG == 0) {
            printf("PROG "); pr128(stdout, steps); printf(" state %c dir %d Lruns %ld Rruns %ld | L(near head): ", 'A'+s, dr, L.len, R.len);
            for (long q = L.len - 1; q >= 0 && q >= L.len - 12; q--) printf("%llu ", (unsigned long long)L.r[q].n);
            printf("| R(near head): ");
            for (long q = R.len - 1; q >= 0 && q >= R.len - 12; q--) printf("%llu ", (unsigned long long)R.r[q].n);
            printf("\n"); fflush(stdout);
        }
        Stack *F = dr ? &R : &L, *Bk = dr ? &L : &R;
        int fac = F->len ? (int)F->r[F->len - 1].b : 0;
        MT *x = macro(s, dr, back, fac);
        if (x->valid != 1) { printf("STOP %s at ", x->valid == 2 ? "HALT" : "loop"); pr128(stdout, steps); printf("\n"); if (DP) dump("halt_tape.txt", steps, s, back, &R); return 1; }
        int far = dr ? x->w0 : x->w1, near = dr ? x->w1 : x->w0;
        if (x->exitR == dr && x->ns == s && near == back && F->len) {
            uint64_t cnt = F->r[F->len - 1].n; F->len--; push(Bk, far, cnt); steps += (u128)x->steps * cnt;
        } else {
            pop1(F); steps += x->steps;
            if (x->exitR == dr) { push(Bk, far, 1); back = near; } else { push(F, near, 1); back = far; }
            s = x->ns; dr = x->exitR;
        }
        if (!dr && L.len == 0) {
            if (away) {
                rounds++;
                double trip = (double)(steps - last); last = steps;
                int big = trip > TRIPMIN && trip > 30 * prevtrip; prevtrip = trip;
                int lg = big || (EVERY && (long)rounds % EVERY == 0);
                if (lg) {
                    printf("%s %.0f ", big ? "TRIP" : "S", rounds); pr128(stdout, steps); printf(" %.0f ", trip); skel(stdout, &R, back, NR); printf("\n"); fflush(stdout);
                    if (DP && big && ndump < 50) pend = 1;
                    if (big && getenv("STOPTRIP") && ++nstop >= atol(getenv("STOPTRIP"))) pend = 2;
                }
                if (rounds >= MAXR && !pend) pend = 3;
                if (MARK > 0 && !pend && ((long)rounds & 63) == 0) {   // the first frozen wall (MARKER +-20 words) still there?
                    int found = 0; long cntd = 0;
                    for (long q = R.len - 1; q >= 0 && cntd < 600 && q >= R.len - 20000 && !found; q--) {
                        int bandrun = R.r[q].n == 1 && ((int)R.r[q].b == BW[0] || (int)R.r[q].b == BW[1] || (int)R.r[q].b == BW[2] || (int)R.r[q].b == BW[3]);
                        if (!bandrun) cntd++;
                        found = R.r[q].n + 20 >= (uint64_t)MARK && R.r[q].n <= (uint64_t)MARK + 20;
                    }
                    if (!found) { printf("MARKERGONE %.0f ", rounds); pr128(stdout, steps); printf("\n"); pend = 2; }
                }
                // dumps are written at the next round start where the prefix 0 11111111 0111 01 starts at a block
                // boundary (head in C on the blank cell left of the back block 111111, next block 110111)
                if (pend && (getenv("DUMPANY") || (s == 2 && back == 63 && R.len && R.r[R.len - 1].b == (uint32_t)tok2b("110111")))) {
                    char fn[512];
                    if (pend == 3) { printf("END %.0f ", rounds); pr128(stdout, steps); printf(" "); skel(stdout, &R, back, NR); printf("\n"); if (DP) { snprintf(fn, sizeof fn, "%send.txt", DP); dump(fn, steps, s, back, &R); } return 0; }
                    if (DP) { snprintf(fn, sizeof fn, "%s%02d.txt", DP, ndump++); dump(fn, steps, s, back, &R); printf("DUMP %s at round %.0f\n", fn, rounds); }
                    if (pend == 2) return 0;
                    pend = 0;
                }
            }
            away = 0;
        } else away = 1;
    }
}
