// C port of lowsim.py (with msim.py's macro step M.mstep for T37): same arithmetic, same output files.
// usage: lowsim_c STATE.txt.gz N K MAXPH OUT [LOWN]     env: FILL, JUMP=1 as for lowsim.py; STATS=1 prints counts;
// SLOW=1 uses the plain cell-by-cell sweep (as msim.py), SLOW=2 the 8-cell block sweep, default the 16-cell window sweep.
// The output files are byte-identical to lowsim.py's (checked on 29,520 phases from data/state20000.txt.gz, N = 3000).
// Build: gcc -O3 -march=native -o lowsim_c lowsim_c.c -lgmp -lz
#include <gmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <zlib.h>

static void die(const char *m) { fprintf(stderr, "%s\n", m); exit(2); }

// ---- tape ----
static uint8_t *B; static long long cap, off, hi;    // r = B[off, hi); cells >= hi are 0
static mpz_t A, Bv;                                   // timer a, b
static int modeR; static long long nov;
static int tab[14];
enum { SA, SB, SC, SD, SE, SF, SG };

static void set_tr(int s, int y, int w, int right, int n) { tab[s * 2 + y] = w | (right << 1) | (n << 2); }
static void init_table(void) {      // T37 = this machine, mirrored and renamed (m9.py)
    for (int i = 0; i < 14; i++) tab[i] = 7 << 2;
    set_tr(SA, 0, 1, 0, SC); set_tr(SA, 1, 0, 1, SF);
    set_tr(SC, 0, 1, 0, SD); set_tr(SC, 1, 1, 0, SC);
    set_tr(SD, 0, 0, 0, SE); set_tr(SD, 1, 0, 0, SD);
    set_tr(SE, 0, 1, 1, SG); set_tr(SE, 1, 1, 1, SF);
    set_tr(SG, 0, 1, 1, SE);                          // G1 halts
    set_tr(SF, 0, 0, 1, SC); set_tr(SF, 1, 1, 1, SA);
}

static void ensure(long long need_right) {           // room: off >= 64 and cap - hi >= need_right
    if (off < 64 || off > cap / 4) {                  // recentre
        long long len = hi - off, no = 64 + (1 << 16);
        if (no + len + need_right > cap) goto grow;
        memmove(B + no, B + off, len);
        if (no < off) memset(B + no + len, 0, hi - (no + len));
        else memset(B, 0, no);
        off = no; hi = no + len;
    }
    if (cap - hi >= need_right) return;
grow:;
    long long len = hi - off, ncap = 2 * (len + need_right) + (1 << 20), no = 64 + (1 << 16);
    uint8_t *nb = calloc(ncap, 1); if (!nb) die("oom");
    memcpy(nb + no, B + off, len); free(B); B = nb; cap = ncap; off = no; hi = no + len;
}

// ---- tokens (run-length) ----
typedef struct { long long *len; char *z; long long n, capn; } Toks;
static void tk_push(Toks *t, char z, long long l) {
    if (t->n == t->capn) { t->capn = t->capn ? 2 * t->capn : 1024; t->len = realloc(t->len, t->capn * 8); t->z = realloc(t->z, t->capn); }
    t->z[t->n] = z; t->len[t->n] = l; t->n++;
}
static void toks_of(const uint8_t *c, long long n, Toks *t) {   // like lowsim.toks
    t->n = 0; long long i = 0;
    while (i < n) {
        uint8_t v = c[i]; long long j = i + 1;
        uint64_t pat = v ? ~0ULL : 0ULL;
        while (j + 8 <= n) { uint64_t w; memcpy(&w, c + j, 8); if (w != (pat & 0x0101010101010101ULL)) break; j += 8; }
        while (j < n && c[j] == v) j++;
        tk_push(t, v ? 'o' : 'z', j - i); i = j;
    }
}

// ---- state load / truncation ----
static mpz_t KMASK_TARGET; static long long Kbits, FILLb = -1;   // FILLb < 0: no refill after overflow
static void fill(mpz_t b) {
    mpz_tdiv_r_2exp(b, b, Kbits);
    long long f = FILLb >= 0 ? FILLb : Kbits / 2;
    for (long long i = 0; i < f; i++) mpz_setbit(b, Kbits + i);
}
static void load_tape_from_toks(const Toks *t, long long N) {   // trunc_state: first N tokens, drop a trailing z
    long long n = t->n < N ? t->n : N;
    if (n && t->z[n - 1] == 'z') n--;
    long long len = 0; for (long long i = 0; i < n; i++) len += t->len[i];
    free(B); cap = 2 * len + (1 << 22); B = calloc(cap, 1); if (!B) die("oom");
    off = cap / 4; hi = off;
    for (long long i = 0; i < n; i++) { if (t->z[i] == 'o') memset(B + hi, 1, t->len[i]); hi += t->len[i]; }
}

// ---- macro step (msim.M.mstep) ----
enum { K_SWEEP, K_R101, K_R11, K_OV, K_INC1, K_INCS, K_HALT, K_STUCK };
static char stopmsg[256];
static long long CNT[8], SWST, PARSE;
static long long sweep_c(uint8_t *t, long long n, long long pos, int st, long long stop_pos, long long *out_pos, int *out_st, long long *h_io) {
    long long steps = 0, h = *h_io;
    while (pos != stop_pos) {
        if (pos < 0 || pos >= n) return -2;
        int e = tab[st * 2 + t[pos]], nx = e >> 2;
        if (nx == 7) { *out_pos = pos; *out_st = st; *h_io = h; return -1; }
        t[pos] = e & 1; pos += (e & 2) ? 1 : -1; if (pos > h) h = pos; st = nx; steps++;
    }
    *out_pos = pos; *out_st = st; *h_io = h; SWST += steps; return steps;
}
// ---- block-table sweep: exact, 8-cell blocks aligned at multiples of 8 ----
typedef struct { uint8_t nb, exit, st; int8_t maxp; uint32_t steps; } BT;   // exit 0 left, 1 right, 2 halt/loop
static BT tbl[7][2][256]; static uint64_t unpack8[256];
#define ONES8 0x0101010101010101ULL
static inline unsigned pack8(uint64_t w) { return (unsigned)(((w & ONES8) * 0x0102040810204080ULL) >> 56); }
static void init_blocks(void) {
    for (int x = 0; x < 256; x++) { uint64_t w = 0; for (int i = 0; i < 8; i++) if (x >> i & 1) w |= 1ULL << (8 * i); unpack8[x] = w; }
    for (int s0 = 0; s0 < 7; s0++) for (int e = 0; e < 2; e++) for (int x = 0; x < 256; x++) {
        uint8_t c[8]; for (int i = 0; i < 8; i++) c[i] = x >> i & 1;
        int pos = e ? 7 : 0, s = s0, maxp = -100; uint32_t steps = 0; BT *b = &tbl[s0][e][x]; b->exit = 2;
        for (;;) {
            int t = tab[s * 2 + c[pos]], nx = t >> 2;
            if (nx == 7) break;
            c[pos] = t & 1; pos += (t & 2) ? 1 : -1; s = nx; steps++; if (pos > maxp) maxp = pos;
            if (pos < 0 || pos > 7) {
                int y = 0; for (int i = 0; i < 8; i++) y |= c[i] << i;
                b->nb = (uint8_t)y; b->exit = pos > 7; b->st = (uint8_t)s; b->maxp = (int8_t)maxp; b->steps = steps; break;
            }
            if (steps > 100000) break;
        }
    }
}
static long long sweep_fast(uint8_t *t, long long n, long long pos, int st, long long stop_pos, long long *out_pos, int *out_st, long long *h_io) {
    long long steps = 0, h = *h_io;
    while (pos != stop_pos) {
        if (pos < 0 || pos >= n) return -2;
        long long base = pos & ~7LL; int cell = (int)(pos & 7);
        if ((cell == 0 || cell == 7) && base + 8 <= n && !(stop_pos >= base && stop_pos < base + 8)) {
            uint64_t win; memcpy(&win, t + base, 8);
            BT *b = &tbl[st][cell == 7][pack8(win)];
            if (b->exit < 2) {
                uint64_t wout = unpack8[b->nb]; memcpy(t + base, &wout, 8);
                steps += b->steps; if (base + b->maxp > h) h = base + b->maxp;
                int pass = b->st == st && b->exit == (cell == 0);
                st = b->st;
                if (b->exit) {
                    pos = base + 8;
                    if (pass) {
                        while (pos + 8 <= n && !(stop_pos >= pos && stop_pos < pos + 8)) {
                            uint64_t w; memcpy(&w, t + pos, 8); if (w != win) break;
                            memcpy(t + pos, &wout, 8); steps += b->steps; pos += 8;
                        }
                        if (pos > h) h = pos;
                    }
                } else {
                    long long nb_ = base - 8;
                    if (pass) {
                        while (nb_ >= 0 && !(stop_pos >= nb_ && stop_pos < nb_ + 8)) {
                            uint64_t w; memcpy(&w, t + nb_, 8); if (w != win) break;
                            memcpy(t + nb_, &wout, 8); steps += b->steps; nb_ -= 8;
                        }
                    }
                    pos = nb_ + 7;
                }
                continue;
            }
        }
        int e = tab[st * 2 + t[pos]], nx = e >> 2;
        if (nx == 7) { *out_pos = pos; *out_st = st; *h_io = h; return -1; }
        t[pos] = e & 1; pos += (e & 2) ? 1 : -1; if (pos > h) h = pos; st = nx; steps++;
    }
    *out_pos = pos; *out_st = st; *h_io = h; SWST += steps; return steps;
}
// ---- 16-cell window sweep: windows [w, w+16) at w = 0 mod 8, head entering at index 7 or 8; lazily cached ----
typedef struct { uint32_t steps; uint16_t out; uint8_t st, exit; int8_t maxp; } WT;   // exit 0 L, 1 R, 2 halt/loop, 255 new
static WT *wtab;                                                                         // [(st*2+ent)*65536 + key]
static WT *wlook(int st, int ent, unsigned key) {
    WT *w = &wtab[((size_t)(st * 2 + ent) << 16) + key];
    if (w->exit != 255) return w;
    uint8_t c[16]; for (int i = 0; i < 16; i++) c[i] = key >> i & 1;
    int pos = ent ? 8 : 7, s = st, maxp = -100; uint32_t steps = 0; w->exit = 2;
    for (;;) {
        int t = tab[s * 2 + c[pos]], nx = t >> 2;
        if (nx == 7) break;
        c[pos] = t & 1; pos += (t & 2) ? 1 : -1; s = nx; steps++; if (pos > maxp) maxp = pos;
        if (pos < 0 || pos > 15) {
            unsigned y = 0; for (int i = 0; i < 16; i++) y |= (unsigned)c[i] << i;
            w->out = (uint16_t)y; w->exit = pos > 15; w->st = (uint8_t)s; w->maxp = (int8_t)maxp; w->steps = steps; break;
        }
        if (steps > 100000) break;
    }
    return w;
}
#define INWIN(x, w) ((x) >= (w) && (x) < (w) + 16)
static long long sweep_win(uint8_t *t, long long n, long long pos, int st, long long stop_pos, long long *out_pos, int *out_st, long long *h_io) {
    long long steps = 0, h = *h_io;
    while (pos != stop_pos) {
        if (pos < 0 || pos >= n) return -2;
        int c = (int)(pos & 7);
        if (c == 7 || c == 0) {
            int ent = c == 0; long long wb = ent ? pos - 8 : pos - 7;
            if (wb >= 0 && wb + 16 <= n && !INWIN(stop_pos, wb)) {
                uint64_t Lw, Rw; memcpy(&Lw, t + wb, 8); memcpy(&Rw, t + wb + 8, 8);
                WT *w = wlook(st, ent, pack8(Lw) | pack8(Rw) << 8);
                if (w->exit < 2) {
                    uint64_t oL = unpack8[w->out & 255], oR = unpack8[w->out >> 8];
                    memcpy(t + wb, &oL, 8); memcpy(t + wb + 8, &oR, 8);
                    steps += w->steps; if (wb + w->maxp > h) h = wb + w->maxp;
                    int same = w->st == st; st = w->st;
                    if (w->exit == 0) {
                        long long w2 = wb - 8;
                        if (same && !ent && oL == Rw) {
                            while (w2 >= 0 && !INWIN(stop_pos, w2)) {
                                uint64_t x; memcpy(&x, t + w2, 8); if (x != Lw) break;
                                memcpy(t + w2, &oL, 8); memcpy(t + w2 + 8, &oR, 8); steps += w->steps; w2 -= 8;
                            }
                        }
                        pos = w2 + 7;
                    } else {
                        long long w2 = wb + 8;
                        if (same && ent && oR == Lw) {
                            while (w2 + 16 <= n && !INWIN(stop_pos, w2)) {
                                uint64_t x; memcpy(&x, t + w2 + 8, 8); if (x != Rw) break;
                                memcpy(t + w2, &oL, 8); memcpy(t + w2 + 8, &oR, 8); steps += w->steps;
                                if (w2 + w->maxp > h) h = w2 + w->maxp;
                                w2 += 8;
                            }
                        }
                        pos = w2 + 8;
                    }
                    continue;
                }
            }
        }
        int e = tab[st * 2 + t[pos]], nx = e >> 2;
        if (nx == 7) { *out_pos = pos; *out_st = st; *h_io = h; return -1; }
        t[pos] = e & 1; pos += (e & 2) ? 1 : -1; if (pos > h) h = pos; st = nx; steps++;
    }
    *out_pos = pos; *out_st = st; *h_io = h; SWST += steps; return steps;
}
static int SLOW;
static int do_sweep(void) {
    ensure(1 << 20);
    long long o = off; B[o - 1] = 1; B[o - 2] = 0; B[o - 3] = 1;
    long long op, h = hi; int os = 0;
    long long n = SLOW == 1 ? sweep_c(B, cap - 2, o, SA, o - 4, &op, &os, &h) : SLOW == 2 ? sweep_fast(B, cap - 2, o, SA, o - 4, &op, &os, &h) : sweep_win(B, cap - 2, o, SA, o - 4, &op, &os, &h);
    if (n == -1) { snprintf(stopmsg, sizeof stopmsg, "('halt in sweep', %lld, '%c')", op - o, "ABCDEFG"[os]); return K_HALT; }
    if (n < 0) { snprintf(stopmsg, sizeof stopmsg, "sweep limit"); return K_STUCK; }
    if (h + 1 > hi) hi = h + 1;
    if (os != SD || B[o - 3] != 0 || B[o - 2] != 1 || B[o - 1] != 1) { snprintf(stopmsg, sizeof stopmsg, "sweep returned %c", "ABCDEFG"[os]); return K_STUCK; }
    B[o - 3] = B[o - 2] = B[o - 1] = 0;
    return K_SWEEP;
}
static uint8_t *dig; static long long digcap = 1 << 20;
static uint64_t *words; static uint8_t *kbits;
static mpz_t kk;
static long long parse_digits(long long i, int tp, int *tail) {   // capacity bits into dig[]; as sweep.c
    long long nb = 0; *tail = 0;
    for (;;) {
        if (i >= hi) { *tail = 1; return nb; }
        if (nb >= digcap) return -1;
        if (tp == 0) {
            int w = B[i] << 3 | B[i + 1] << 2 | B[i + 2] << 1 | B[i + 3];
            if (w == 0x0) { dig[nb++] = 1; i += 4; }
            else if (w == 0x6) { dig[nb++] = 0; i += 4; }
            else if (w == 0x3) { dig[nb++] = 1; i += 4; tp = 1; }
            else if (w == 0x7) { dig[nb++] = 0; i += 4; tp = 1; }
            else return nb;
        } else {
            if (B[i] && B[i + 1]) { const uint8_t *z = memchr(B + i, 0, hi - i); long long j = z ? z - B : hi; i += (j - i) & ~1LL; continue; }
            int w = B[i] << 1 | B[i + 1];
            if (w == 3) i += 2;
            else if (w == 0) { dig[nb++] = 1; i += 2; tp = 0; }
            else if (w == 2) { dig[nb++] = 0; i += 2; tp = 0; }
            else return nb;
        }
    }
}
static long long add_digits(long long i, int tp, const uint8_t *kb, long long nk) {
    long long j = 0; int c = 0;
    for (;;) {
        if (j >= nk && !c) return i;
        int kbit = j < nk ? kb[j] : 0;
        if (tp == 0) {
            int w = B[i] << 3 | B[i + 1] << 2 | B[i + 2] << 1 | B[i + 3], v, sw;
            if (w == 0x0) { v = 0; sw = 0; } else if (w == 0x6) { v = 1; sw = 0; }
            else if (w == 0x3) { v = 0; sw = 1; } else if (w == 0x7) { v = 1; sw = 1; }
            else return -1;
            int s = v + kbit + c, nv = s & 1; c = s >> 1;
            if (nv != v) { if (!sw) { B[i + 1] = B[i + 2] = (uint8_t)nv; } else B[i + 1] = (uint8_t)nv; }
            i += 4; j++; if (sw) tp = 1;
        } else {
            if (B[i] && B[i + 1]) { const uint8_t *z = memchr(B + i, 0, cap - i); long long j = z ? z - B : cap; i += (j - i) & ~1LL; continue; }
            int w = B[i] << 1 | B[i + 1];
            if (w == 3) { i += 2; continue; }
            int v; if (w == 0) v = 0; else if (w == 2) v = 1; else return -1;
            int s = v + kbit + c, nv = s & 1; c = s >> 1;
            B[i] = (uint8_t)nv; i += 2; j++; tp = 0;
        }
    }
}
static int mstep(void) {
    if (modeR) { int r = do_sweep(); if (r == K_SWEEP) modeR = 0; return r; }
    if (mpz_even_p(A)) { snprintf(stopmsg, sizeof stopmsg, "a even: the left lemmas fail (halts)"); return K_HALT; }
    ensure(1 << 12);
    uint8_t p0 = B[off], p1 = B[off + 1], p2 = B[off + 2];
    if (p0 == 1 && p1 == 0 && p2 == 1) { mpz_add_ui(A, A, 4); off += 2; B[off] = 1; return K_R101; }
    if (p0 == 1 && p1 == 1) { mpz_add_ui(A, A, 4); off += 2; modeR = 1; return K_R11; }
    if (mpz_sgn(Bv) == 0) {
        if (p0 == 0 && p1 == 0) {          // a is odd here
            mpz_fdiv_q_2exp(Bv, A, 1); mpz_add_ui(Bv, Bv, 2); mpz_set_ui(A, 3);
            off += 1; B[off] = 0; modeR = 1; nov++; return K_OV;
        }
        snprintf(stopmsg, sizeof stopmsg, "b=0 without LOv pattern"); return K_STUCK;
    }
    int tail; long long nb = parse_digits(off, 1, &tail); PARSE += nb;
    if (nb < 0) { snprintf(stopmsg, sizeof stopmsg, "too many digits"); return K_STUCK; }
    if (!tail) {
        long long nw = (nb + 63) / 64; memset(words, 0, nw * 8 + 8);
        for (long long j = 0; j < nb; j++) if (dig[j]) words[j >> 6] |= 1ULL << (j & 63);
        mpz_import(kk, nw ? nw : 1, -1, 8, 0, 0, words);
        if (mpz_sgn(kk) == 0) { mpz_add_ui(A, A, 4); mpz_sub_ui(Bv, Bv, 1); modeR = 1; return K_INC1; }
        if (mpz_cmp(kk, Bv) > 0) mpz_set(kk, Bv);
    } else mpz_set(kk, Bv);
    long long nk = (long long)mpz_sizeinbase(kk, 2);
    ensure(4 * (nk + 8) + (1 << 12));
    for (long long j = 0; j < nk; j++) kbits[j] = (uint8_t)mpz_tstbit(kk, j);
    long long e = add_digits(off, 1, kbits, nk);
    if (e < 0) { snprintf(stopmsg, sizeof stopmsg, "rincs ran off digits"); return K_STUCK; }
    if (e > hi) hi = e;
    mpz_addmul_ui(A, kk, 4); mpz_sub(Bv, Bv, kk);
    return K_INCS;
}

// ---- main loop (lowsim.py) ----
static void write_toks(FILE *f, const Toks *t, long long from, long long to) {
    for (long long i = from; i < to && i < t->n; i++) fprintf(f, "%s%c%lld", i > from ? " " : "", t->z[i], t->len[i]);
}
int main(int argc, char **argv) {
    if (argc < 6) die("usage: lowsim_c STATE.txt.gz N K MAXPH OUT [LOWN]");
    const char *src = argv[1]; long long N = atoll(argv[2]); Kbits = atoll(argv[3]); long long MAXPH = atoll(argv[4]);
    const char *OUT = argv[5]; long long LOWN = argc > 6 ? atoll(argv[6]) : 24;
    const char *fe = getenv("FILL"); FILLb = (fe && *fe) ? atoll(fe) : -2;   // -2: unset in python = no refill
    int JUMP = getenv("JUMP") && !strcmp(getenv("JUMP"), "1");
    init_table(); init_blocks(); SLOW = getenv("SLOW") ? atoi(getenv("SLOW")) : 0; wtab = malloc(sizeof(WT) * 14 * 65536); for (long i = 0; i < 14 * 65536; i++) wtab[i].exit = 255; mpz_inits(A, Bv, kk, KMASK_TARGET, NULL);
    dig = malloc(digcap); words = malloc((digcap / 64 + 2) * 8); kbits = malloc(1 << 24);
    // load
    gzFile g = gzopen(src, "rb"); if (!g) die("cannot open state");
    size_t lcap = 1 << 26; char *line = malloc(lcap); Toks st = {0};
    char mode = 'L';
    while (gzgets(g, line, (int)lcap)) {
        size_t L = strlen(line); if (L && line[L - 1] == '\n') line[--L] = 0;
        if (L == lcap - 1) die("line too long");
        char *sp = strchr(line, ' '); if (!sp) continue; *sp = 0; char *v = sp + 1;
        if (!strcmp(line, "a")) mpz_set_str(A, v, 16);
        else if (!strcmp(line, "b")) mpz_set_str(Bv, v, 16);
        else if (!strcmp(line, "nov")) nov = atoll(v);
        else if (!strcmp(line, "mode")) mode = v[0];
        else if (!strcmp(line, "r")) {
            char *s = v; while (*s) { while (*s == ' ') s++; if (!*s) break; char z = *s++; long long l = strtoll(s, &s, 10); tk_push(&st, z, l); }
        }
    }
    gzclose(g);
    if (FILLb == -2) FILLb = -1;  // FILL unset: fill() uses K / 2 bits, and b is not refilled after overflows
    // trunc_state
    load_tape_from_toks(&st, N); fill(Bv); modeR = mode == 'R';
    // target for the jump test: b % 2^K == 2^K - 3
    mpz_set_ui(KMASK_TARGET, 0); mpz_setbit(KMASK_TARGET, Kbits); mpz_sub_ui(KMASK_TARGET, KMASK_TARGET, 3);
    mpz_t rem; mpz_init(rem);
    char fn[4096]; snprintf(fn, sizeof fn, "%s.exc", OUT);
    FILE *exc = fopen(fn, "w"), *out = fopen(OUT, "w"); if (!exc || !out) die("cannot open output");
    long long Q = Kbits + 100, quiet = 0; Toks T = {0}, prev = {0}; int have_prev = 0;
    struct timespec t0, tn; clock_gettime(CLOCK_MONOTONIC, &t0);
    int refill = fe && *fe;      // python: refill after each overflow only when FILL is set
    while (nov < MAXPH) {
        int k = mstep(); CNT[k]++;
        if (k == K_HALT || k == K_STUCK) {
            fprintf(out, "STOP %s %s nov=%lld\n", k == K_HALT ? "Halted" : "Stuck", stopmsg, nov);
            printf("STOP %s %lld\n", stopmsg, nov); break;
        }
        if (k != K_OV) continue;
        if (refill) fill(Bv);
        long long n = hi - off; if (n > 4000000) n = 4000000;
        toks_of(B + off, n, &T);
        fprintf(out, "%lld ", nov); write_toks(out, &T, 0, LOWN); fputc('\n', out);
        // quiet: compare tokens [2, N-100)
        long long lo = 2, up = N - 100; if (up > T.n) up = T.n; if (lo > up) up = lo;
        long long pup = N - 100; if (pup > prev.n) pup = prev.n; if (lo > pup) pup = lo;
        int same = have_prev && (up - lo) == (pup - lo) &&
                   !memcmp(T.len + lo, prev.len + lo, (up - lo) * 8) && !memcmp(T.z + lo, prev.z + lo, up - lo);
        quiet = same ? quiet + 1 : 0;
        // prev := T
        if (prev.capn < T.n) { prev.capn = T.capn; prev.len = realloc(prev.len, prev.capn * 8); prev.z = realloc(prev.z, prev.capn); }
        memcpy(prev.len, T.len, T.n * 8); memcpy(prev.z, T.z, T.n); prev.n = T.n; have_prev = 1;
        int z3 = T.n > 0 && T.z[0] == 'z' && T.len[0] == 3;
        if (!z3) { fprintf(exc, "%lld ", nov); write_toks(exc, &T, 0, 8); fputc('\n', exc); fflush(exc); }
        long long L = z3 && T.n > 1 ? T.len[1] : 0;
        if (JUMP && quiet >= Q && L > 200) {
            mpz_tdiv_r_2exp(rem, Bv, Kbits);
            if (!mpz_cmp(rem, KMASK_TARGET)) {
                long long j = L - 100; T.len[1] = L - j;
                long long old = nov; load_tape_from_toks(&T, N); fill(Bv); nov += j;
                fprintf(exc, "JUMP %lld -> %lld\n", old, nov); fflush(exc); quiet = 0; have_prev = 0;
                continue;
            }
        }
        if (nov % 500 == 0) {
            fflush(out); clock_gettime(CLOCK_MONOTONIC, &tn);
            printf("%lld %.0fs rlen %lld\n", nov, (tn.tv_sec - t0.tv_sec) + 1e-9 * (tn.tv_nsec - t0.tv_nsec), hi - off); if (getenv("STATS")) { fprintf(stderr, "%lld sw %lld r101 %lld r11 %lld inc1 %lld incs %lld swsteps %lld parsed %lld\n", nov, CNT[0], CNT[1], CNT[2], CNT[4], CNT[5], SWST, PARSE); memset(CNT,0,sizeof CNT); SWST=PARSE=0; } fflush(stdout);
        }
    }
    fclose(out); fclose(exc); return 0;
}
