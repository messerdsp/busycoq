// p3_count: chainb's core (6-cell blocks, back block, run chaining) without printing, to count macro steps.
// usage: p3_count MACHINE STOPSTEP [INITFILE]     (stops at the first round start at or after STOPSTEP)
// prints the macro-step counts every 1e14 steps and at the end; env DUMP=file writes the final tape line.
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
int main(int argc, char **argv) {
    const char *m = argv[1]; double STOP = atof(argv[2]);
    mt = calloc((size_t)12 << (2 * K), sizeof(MT));
    for (int s = 0; s < 6; s++) for (int y = 0; y < 2; y++) {
        const char *t = m + s * 7 + y * 3;
        if (t[0] == '-') { tn[s][y] = -1; continue; }
        tw[s][y] = t[0] - '0'; tmv[s][y] = t[1] == 'R' ? 1 : -1; tn[s][y] = t[2] - 'A';
    }
    Stack L = {0}, R = {0}; int back = 0, s = 0, dr = 1; u128 steps = 0;
    if (argc > 3) {
        FILE *f = fopen(argv[3], "r"); char *line = NULL; size_t lcap = 0; if (!f || getline(&line, &lcap, f) <= 0) return 2; fclose(f);
        char *tok = strtok(line, " \n"); for (char *c = tok; *c; c++) steps = steps * 10 + (*c - '0');
        tok = strtok(NULL, " \n"); s = tok[0] - 'A'; dr = 0;
        Run *tmp = NULL; long nt = 0, ct = 0; int first = 1;
        while ((tok = strtok(NULL, " \n"))) {
            int b = 0; for (int k = 0; k < K; k++) b |= (tok[k] - '0') << k;
            uint64_t n = 1; char *c = strchr(tok, '^'); if (c) n = strtoull(c + 1, NULL, 10);
            if (first) { back = b; first = 0; if (n == 1) continue; n--; }
            if (nt == ct) { ct = ct ? 2 * ct : 1024; tmp = realloc(tmp, ct * sizeof(Run)); }
            tmp[nt].b = b; tmp[nt].n = n; nt++;
        }
        for (long i = nt - 1; i >= 0; i--) push(&R, tmp[i].b, tmp[i].n);
    }
    unsigned long nchain = 0, nsingle = 0, rounds = 0; double next = (double)steps + 1e14; int away = 1; long maxruns = 0;
    for (;;) {
        Stack *F = dr ? &R : &L, *Bk = dr ? &L : &R;
        int fac = F->len ? (int)F->r[F->len - 1].b : 0;
        MT *x = macro(s, dr, back, fac);
        if (x->valid != 1) { printf("STOP\n"); break; }
        int far = dr ? x->w0 : x->w1, near = dr ? x->w1 : x->w0;
        if (x->exitR == dr && x->ns == s && near == back && F->len) {
            uint64_t cnt = F->r[F->len - 1].n; F->len--; push(Bk, far, cnt); steps += (u128)x->steps * cnt; nchain++;
        } else {
            pop1(F); nsingle++; steps += x->steps;
            if (x->exitR == dr) { push(Bk, far, 1); back = near; } else { push(F, near, 1); back = far; }
            s = x->ns; dr = x->exitR;
        }
        if (L.len + R.len > maxruns) maxruns = L.len + R.len;
        if (!dr && L.len == 0) {
            if (away) { rounds++; if ((double)steps >= STOP) break; }
            away = 0;
        } else away = 1;
        if ((double)steps > next) { pr128(stdout, steps); printf(" chain %lu single %lu rounds %lu runs %ld\n", nchain, nsingle, rounds, L.len + R.len); fflush(stdout); next += 1e14; }
    }
    pr128(stdout, steps); printf(" END chain %lu single %lu rounds %lu runs %ld maxruns %ld\n", nchain, nsingle, rounds, L.len + R.len, maxruns);
    if (getenv("DUMP")) { FILE *o = fopen(getenv("DUMP"), "w"); pr128(o, steps); fprintf(o, " %c ", 'A' + s); prb(o, back);
        for (long i = R.len - 1; i >= 0; i--) { fputc(' ', o); prb(o, R.r[i].b); if (R.r[i].n > 1) fprintf(o, "^%llu", (unsigned long long)R.r[i].n); } fputc('\n', o); fclose(o); }
    return 0;
}
