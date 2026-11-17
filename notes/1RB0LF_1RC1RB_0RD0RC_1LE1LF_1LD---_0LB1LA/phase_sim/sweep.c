// Fast bounce over a counter word. States 0..6 = A B C D E F G. tab[(st*2+sym)] = write | move<<1 | next<<2,
// move bit 1 = R; next 7 = halt. Tape buffer: cells [0, n); r starts at index off; head starts at off.
// Runs until head == stop_pos (to the left of the start word). Returns steps, or -1 on halt, -2 on bound/limit.
#include <stdint.h>
long long sweep(uint8_t *t, long long n, long long pos, int st, long long stop_pos, const int *tab,
                long long limit, long long *out_pos, int *out_st, long long *hi) {
    long long steps = 0, h = *hi;
    while (pos != stop_pos) {
        if (pos < 0 || pos >= n) return -2;
        int e = tab[st * 2 + t[pos]];
        int nx = e >> 2;
        if (nx == 7) { *out_pos = pos; *out_st = st; *hi = h; return -1; }
        t[pos] = e & 1;
        pos += (e & 2) ? 1 : -1;
        if (pos > h) h = pos;
        st = nx;
        if (++steps > limit) return -2;
    }
    *out_pos = pos; *out_st = st; *hi = h;
    return steps;
}

// Parse counter digits from index i in mode tp (as SBCv9 rest). Writes capacity bits (1 - digit value) to out.
// Returns number of digits; *tail = 1 if the parse reached index hi (zero tail => unbounded capacity).
long long parse_digits(const uint8_t *B, long long i, long long hi, int tp, uint8_t *out, long long maxd, int *tail) {
    long long nb = 0; *tail = 0;
    for (;;) {
        if (i >= hi) { *tail = 1; return nb; }
        if (nb >= maxd) return -1;
        if (tp == 0) {
            int w = B[i] << 3 | B[i+1] << 2 | B[i+2] << 1 | B[i+3];
            if (w == 0x0) { out[nb++] = 1; i += 4; }
            else if (w == 0x6) { out[nb++] = 0; i += 4; }
            else if (w == 0x3) { out[nb++] = 1; i += 4; tp = 1; }
            else if (w == 0x7) { out[nb++] = 0; i += 4; tp = 1; }
            else return nb;
        } else {
            int w = B[i] << 1 | B[i+1];
            if (w == 3) i += 2;
            else if (w == 0) { out[nb++] = 1; i += 2; tp = 0; }
            else if (w == 2) { out[nb++] = 0; i += 2; tp = 0; }
            else return nb;
        }
    }
}

// Add K (little-endian bits kb[0..nk)) to the counter starting at i in mode tp. Returns the index after the
// last digit touched, or -1 if it runs off the digits.
long long add_digits(uint8_t *B, long long i, int tp, const uint8_t *kb, long long nk) {
    long long j = 0; int c = 0;
    for (;;) {
        if (j >= nk && !c) return i;
        int kbit = j < nk ? kb[j] : 0;
        if (tp == 0) {
            int w = B[i] << 3 | B[i+1] << 2 | B[i+2] << 1 | B[i+3];
            int v, sw;
            if (w == 0x0) { v = 0; sw = 0; } else if (w == 0x6) { v = 1; sw = 0; }
            else if (w == 0x3) { v = 0; sw = 1; } else if (w == 0x7) { v = 1; sw = 1; }
            else return -1;
            int s = v + kbit + c; int nv = s & 1; c = s >> 1;
            if (nv != v) {
                if (!sw) { if (nv) { B[i+1] = 1; B[i+2] = 1; } else { B[i+1] = 0; B[i+2] = 0; } }
                else { B[i+1] = nv; }
            }
            i += 4; j++; if (sw) tp = 1;
        } else {
            int w = B[i] << 1 | B[i+1];
            if (w == 3) { i += 2; continue; }
            int v;
            if (w == 0) v = 0; else if (w == 2) v = 1; else return -1;
            int s = v + kbit + c; int nv = s & 1; c = s >> 1;
            B[i] = nv;
            i += 2; j++; tp = 0;
        }
    }
}
