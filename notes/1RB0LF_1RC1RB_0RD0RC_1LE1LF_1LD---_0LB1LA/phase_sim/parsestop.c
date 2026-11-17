#include <stdint.h>
// Like parse_digits, but returns the digit count and stores the stop cell and mode.
long long parse_stop(const uint8_t *B, long long i, long long hi, int tp, long long *stop, int *mode) {
    long long nb = 0;
    for (;;) {
        if (i >= hi) { *stop = i; *mode = tp; return nb; }
        if (tp == 0) {
            int w = B[i] << 3 | B[i+1] << 2 | B[i+2] << 1 | B[i+3];
            if (w == 0x0 || w == 0x6) { nb++; i += 4; }
            else if (w == 0x3 || w == 0x7) { nb++; i += 4; tp = 1; }
            else { *stop = i; *mode = tp; return nb; }
        } else {
            int w = B[i] << 1 | B[i+1];
            if (w == 3) i += 2;
            else if (w == 0 || w == 2) { nb++; i += 2; tp = 0; }
            else { *stop = i; *mode = tp; return nb; }
        }
    }
}
// Reset every digit (value 1 -> 0) from i up to stop, starting in mode tp. Returns 0, or -1 on a non-digit.
int zero_digits(uint8_t *B, long long i, long long stop, int tp) {
    while (i < stop) {
        if (tp == 0) {
            int w = B[i] << 3 | B[i+1] << 2 | B[i+2] << 1 | B[i+3];
            if (w == 0x6) { B[i+1] = 0; B[i+2] = 0; }
            else if (w == 0x7) { B[i+1] = 0; tp = 1; }
            else if (w == 0x3) { tp = 1; }
            else if (w != 0x0) return -1;
            i += 4;
        } else {
            int w = B[i] << 1 | B[i+1];
            if (w == 2) { B[i] = 0; tp = 0; }
            else if (w == 0) { tp = 0; }
            else if (w != 3) return -1;
            i += 2;
        }
    }
    return 0;
}
