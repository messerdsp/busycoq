// Chain simulator with a back block: tape = L stack | back | R stack (runs of K-cell blocks); the head sits at the
// boundary between `back` and the facing block. A macro step simulates the machine on the 2K-cell window
// [back, facing] (in tape order) until the head leaves it. A run of identical facing blocks is crossed at once when
// one copy returns the same state, direction and back block. Exact: checked cell for cell against direct simulation.
// usage: chainb MACHINE MAXSTEPS EVERY OUT
//   EVERY > 0: print every EVERY-th left-end event (head moving left with nothing nonblank to its left)
//   EVERY = 0: print when the pattern of the rightmost NB (25) runs changes
//   EVERY < 0: print every |EVERY|-th round start (first left-end event after the head was away)
//   env SKEL=1: print a skeleton instead of the tape: runs of >= 3 equal blocks as counts, [n] = n blocks between
//   env ENDT=T: at round starts, print the end region (runs right of the last run of >= T blocks) when it changes
//   env ENDB=T [ENDBEVERY=k]: at round starts (every k-th), print the end of the first chain (runs between its
//     last run of >= T blocks and the band) when it changes
//   env INIT=file: start from a printed full line (as written with EVERY < 0); MAXSTEPS then counts from it
// build: gcc -O2 -o chainb chainb.c
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#ifndef K
#define K 6
#endif
#define M ((1 << K) - 1)
#ifndef NB
#define NB 25
#endif
static int tw[6][2], tmv[6][2], tn[6][2];
typedef struct { uint32_t steps; uint16_t w0, w1; uint8_t ns, exitR, valid; } MT;
static MT *mt;   // index: ((s*2+dr) << 2K) | back << K | facing
static MT *macro(int s, int dr, int back, int fac) {
    MT *m = &mt[(((size_t)(s * 2 + dr)) << (2 * K)) | (size_t)back << K | fac];
    if (m->valid) return m;
    int c[2 * K];
    int lo = dr ? back : fac, hi = dr ? fac : back;      // window in tape order: [lo][hi]
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
    memset(&s->r[s->len], 0, sizeof(Run)); s->r[s->len].b = b; s->r[s->len].n = n; s->len++;
}
static int pop1(Stack *s) {                  // take one block from the top (blank if empty)
    if (!s->len) return 0;
    int b = s->r[s->len - 1].b; if (--s->r[s->len - 1].n == 0) s->len--; return b;
}
static void pr128(FILE *f, u128 x) { char buf[48]; int i = 47; buf[i] = 0; if (!x) buf[--i] = '0'; while (x) { buf[--i] = '0' + x % 10; x /= 10; } fputs(buf + i, f); }
static void prb(FILE *f, int b) { for (int k = 0; k < K; k++) fputc('0' + (b >> k & 1), f); }
int main(int argc, char **argv) {
    const char *m = argv[1]; double MAXS = atof(argv[2]); long EVERY = atol(argv[3]);
    FILE *out = strcmp(argv[4], "-") ? fopen(argv[4], "w") : stdout;
    mt = calloc((size_t)12 << (2 * K), sizeof(MT));
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tmv[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    Stack L = {0}, R = {0}; int back = 0, s = 0, dr = 1;
    u128 steps = 0;
    if (getenv("INIT")) {      // start from a printed full line: "steps state back run run ..." (head at the left end, moving left)
        FILE *f = fopen(getenv("INIT"), "r"); if (!f) { fprintf(stderr, "no INIT file\n"); return 2; }
        static char line[1 << 24]; if (!fgets(line, sizeof line, f)) return 2; fclose(f);
        char *tok = strtok(line, " \n"); steps = 0; for (char *c = tok; *c; c++) steps = steps * 10 + (*c - '0');
        tok = strtok(NULL, " \n"); s = tok[0] - 'A'; dr = 0;
        Run *tmp = NULL; long nt = 0, ct = 0; int first = 1;
        while ((tok = strtok(NULL, " \n"))) {
            int b = 0; for (int k = 0; k < K; k++) b |= (tok[k] - '0') << k;
            uint64_t n = 1; char *c = strchr(tok, '^'); if (c) n = strtoull(c + 1, NULL, 10);
            if (first) { back = b; first = 0; if (n > 1) { if (nt == ct) { ct = ct ? 2 * ct : 1024; tmp = realloc(tmp, ct * sizeof(Run)); } tmp[nt].b = b; tmp[nt].n = n - 1; nt++; } continue; }
            if (nt == ct) { ct = ct ? 2 * ct : 1024; tmp = realloc(tmp, ct * sizeof(Run)); }
            tmp[nt].b = b; tmp[nt].n = n; nt++;
        }
        for (long i = nt - 1; i >= 0; i--) push(&R, tmp[i].b, tmp[i].n);
        free(tmp);
        MAXS += (double)steps;      // with INIT, MAXSTEPS counts from the initial step
    } long ev = 0, nchain = 0, nsingle = 0;
    while ((double)steps < MAXS) {
        Stack *F = dr ? &R : &L, *Bk = dr ? &L : &R;
        int fac = F->len ? (int)F->r[F->len - 1].b : 0;
        MT *x = macro(s, dr, back, fac);
        if (x->valid != 1) { fprintf(out, "STOP %s at ", x->valid == 2 ? "halt" : "loop"); pr128(out, steps); fputc('\n', out); break; }
        int far = dr ? x->w0 : x->w1, near = dr ? x->w1 : x->w0;   // far = block left behind, near = new back
        if (x->exitR == dr && x->ns == s && near == back && F->len) {   // chain the whole run
            uint64_t cnt = F->r[F->len - 1].n; F->len--;
            push(Bk, far, cnt); steps += (u128)x->steps * cnt; nchain++;
        } else {
            pop1(F); nsingle++; steps += x->steps;
            if (x->exitR == dr) { push(Bk, far, 1); back = near; }
            else { push(F, near, 1); back = far; }          // turned: the old facing block (now `near`) is ahead again
            s = x->ns; dr = x->exitR;
        }
        static int away = 1;
        static long endbcount = 0;
        if (getenv("ENDB") && !dr && L.len == 0 && away && (endbcount++ & (getenv("ENDBEVERY") ? atol(getenv("ENDBEVERY")) - 1 : 0)) == 0) {     // end of the first chain: runs between its last run >= T and the band
            static long T = 0; if (!T) T = atol(getenv("ENDB"));
            long lastbig = -1, single = 0, bandstart = -1;
            for (long i = R.len - 1; i >= 0; i--) {             // left to right
                if (R.r[i].n == 1) { if (++single >= 200) { bandstart = i + 199; break; } }
                else { single = 0; if (R.r[i].n >= (uint64_t)T) lastbig = i; }
            }
            if (bandstart >= 0 && lastbig > bandstart) {
                static uint32_t pv[4096]; static uint64_t pc[4096]; static long pn = -1;
                long n = lastbig - bandstart - 1; int d = n != pn;
                for (long j = 0; j < n && j < 4096 && !d; j++) d = pv[j] != R.r[lastbig - 1 - j].b || pc[j] != R.r[lastbig - 1 - j].n;
                if (d && n < 4096) {
                    for (long j = 0; j < n; j++) { pv[j] = R.r[lastbig - 1 - j].b; pc[j] = R.r[lastbig - 1 - j].n; } pn = n;
                    pr128(out, steps); fprintf(out, " W%llu", (unsigned long long)R.r[lastbig].n);
                    for (long j = lastbig - 1; j > bandstart; j--) { fputc(' ', out); prb(out, R.r[j].b); if (R.r[j].n > 1) fprintf(out, "^%llu", (unsigned long long)R.r[j].n); }
                    fputc('\n', out); fflush(out);
                }
            }
        }
        if (getenv("ENDT") && !dr && L.len == 0 && away) {     // at round starts: print the end region when it changes
            static long T = 0; if (!T) T = atol(getenv("ENDT"));
            static uint32_t pv[4096]; static uint64_t pc[4096]; static long pn = -1;
            long k = 0; while (k < R.len && R.r[k].n < (uint64_t)T) k++;          // R.r[0] = far right; stop at first big run
            int d = k != pn; for (long i = 0; i < k && !d; i++) d = pv[i] != R.r[i].b || pc[i] != R.r[i].n;
            if (d && k < 4096) {
                for (long i = 0; i < k; i++) { pv[i] = R.r[i].b; pc[i] = R.r[i].n; } pn = k;
                pr128(out, steps); fprintf(out, " %c", 'A' + s);
                if (k < R.len) fprintf(out, " W%llu", (unsigned long long)R.r[k].n);
                for (long i = k - 1; i >= 0; i--) { fputc(' ', out); prb(out, R.r[i].b); if (R.r[i].n > 1) fprintf(out, "^%llu", (unsigned long long)R.r[i].n); }
                fputc('\n', out); fflush(out);
            }
        }
        if (!(!dr && L.len == 0)) away = 1;
        if (EVERY < 0 && !dr && L.len == 0) {          // round starts only: first left-end macro step after being away
            if (away && ev++ % (-EVERY) == 0) {
                pr128(out, steps); fprintf(out, " %c ", 'A' + s);
                if (getenv("SKEL")) {               // skeleton: runs with count >= 3, and the number of blocks between
                    long sh = 1;
                    for (long i = R.len - 1; i >= 0; i--) {
                        if (R.r[i].n >= 3) { if (sh) fprintf(out, "[%ld] ", sh); fprintf(out, "%llu ", (unsigned long long)R.r[i].n); sh = 0; }
                        else sh += R.r[i].n;
                    }
                    fprintf(out, "[%ld] runs=%ld", sh, R.len);
                } else {
                    prb(out, back);
                    for (long i = R.len - 1; i >= 0; i--) { fputc(' ', out); prb(out, R.r[i].b); if (R.r[i].n > 1) fprintf(out, "^%llu", (unsigned long long)R.r[i].n); }
                }
                fputc('\n', out); fflush(out);
            }
            away = 0;
        } else if (!dr && L.len == 0) {
            int show = 0;
            if (EVERY == 0) {
                static uint32_t prev[61]; static long pn = -1; long n = R.len < NB ? R.len : NB; int d = n != pn || prev[60] != (uint32_t)back;
                for (long i = 0; i < n && !d; i++) d = prev[i] != R.r[i].b;
                if (d) { for (long i = 0; i < n; i++) prev[i] = R.r[i].b; prev[60] = back; pn = n; show = 1; }
            } else show = ev++ % EVERY == 0;
            if (show) {
                pr128(out, steps); fprintf(out, " %c ", 'A' + s); prb(out, back);
                for (long i = R.len - 1; i >= 0; i--) { fputc(' ', out); prb(out, R.r[i].b); if (R.r[i].n > 1) fprintf(out, "^%llu", (unsigned long long)R.r[i].n); }
                fputc('\n', out); fflush(out);
            }
        }
    }
    fprintf(stderr, "chain %ld single %ld steps ", nchain, nsingle); pr128(stderr, steps); fputc('\n', stderr);
    return 0;
}
