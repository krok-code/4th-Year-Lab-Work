/* ЛР7, варіант 21 (V=9): N=256, Fs=66 кГц, перекриття 0 %, Cortex-M4F 168 МГц */
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "arm_math.h"
#include "arm_const_structs.h"
#include "fir_q15.h"
#include "fir_f32.h"

#define N 256
#define NTAPS FIR_F32_NUM_TAPS          /* 147 коефіцієнтів з ЛР5 */
#define NQ (NTAPS + 1)                  /* 148: для CMSIS Q15 потрібна парна кількість коеф. */

volatile uint32_t sink;
__attribute__((noinline)) void mark_begin(uint32_t id) { sink = id; __asm volatile("" ::: "memory"); }
__attribute__((noinline)) void mark_end(uint32_t id)   { sink = id; __asm volatile("" ::: "memory"); }

static float xf[N];
static q15_t xq[N];
static float y_naive[N], y_f32[N];
static q15_t y_q15[N];
static float fstate[NTAPS + N - 1];
static q15_t qstate[NQ + N - 1];
static q15_t hq[NQ];
static arm_fir_instance_f32 Sf;
static arm_fir_instance_q15 Sq;
static float fft_f[2 * N];
static q15_t fft_q[2 * N];

#define UART_DR  (*(volatile uint32_t *)0x40004404)
#define UART_CR1 (*(volatile uint32_t *)0x4000440C)

static void putc_(char c) { UART_DR = (uint32_t)c; }
static void puts_(const char *s) { while (*s) putc_(*s++); }
static void puthex(uint32_t v) {
    for (int i = 7; i >= 0; i--) {
        uint32_t d = (v >> (4 * i)) & 0xF;
        putc_(d < 10 ? '0' + d : 'a' + d - 10);
    }
}

static void naive_fir(const float *x, float *y) {
    for (int n = 0; n < N; n++) {
        float acc = 0.0f;
        for (int k = 0; k < NTAPS; k++) {
            int j = n - k;
            if (j >= 0) acc += fir_f32_coeffs[k] * x[j];
        }
        y[n] = acc;
    }
}

int main(void) {
    UART_CR1 = 0x2008;
    for (int n = 0; n < N; n++) {
        /* два тони: 0,03·Fs (1980 Гц, смуга затримки) та 0,30·Fs (19800 Гц, смуга пропускання) */
        float v = 0.35f * sinf(2.0f * 3.14159265f * 0.03f * n) +
                  0.35f * sinf(2.0f * 3.14159265f * 0.30f * n);
        xf[n] = v;
        xq[n] = (q15_t)lrintf(v * 32768.0f);
    }
    for (int n = 0; n < N; n++) xf[n] = xq[n] / 32768.0f;

    /* ініціалізація фільтрів поза вимірюванням */
    float hrev[NTAPS];
    for (int k = 0; k < NTAPS; k++) hrev[k] = fir_f32_coeffs[NTAPS - 1 - k];
    arm_fir_init_f32(&Sf, NTAPS, hrev, fstate, N);

    hq[0] = 0;
    for (int k = 0; k < NTAPS; k++) hq[1 + k] = fir_q15_coeffs[NTAPS - 1 - k];
    arm_fir_init_q15(&Sq, NQ, hq, qstate, N);

    mark_begin(0); mark_end(0);
    mark_begin(1); naive_fir(xf, y_naive); mark_end(1);
    mark_begin(2); arm_fir_f32(&Sf, xf, y_f32, N); mark_end(2);
    mark_begin(3); arm_fir_q15(&Sq, xq, y_q15, N); mark_end(3);

    for (int n = 0; n < N; n++) {
        fft_f[2 * n] = xf[n]; fft_f[2 * n + 1] = 0.0f;
        fft_q[2 * n] = xq[n]; fft_q[2 * n + 1] = 0;
    }
    mark_begin(4); arm_cfft_f32(&arm_cfft_sR_f32_len256, fft_f, 0, 1); mark_end(4);
    mark_begin(5); arm_cfft_q15(&arm_cfft_sR_q15_len256, fft_q, 0, 1); mark_end(5);

    puts_("=== LR7 ===\n");
    puts_("X\n");       for (int n = 0; n < N; n++)     { puthex((uint16_t)xq[n]); putc_(n % 16 == 15 ? '\n' : ' '); }
    puts_("NAIVE\n");   for (int n = 0; n < N; n++)     { uint32_t b; memcpy(&b, &y_naive[n], 4); puthex(b); putc_(n % 8 == 7 ? '\n' : ' '); }
    puts_("F32\n");     for (int n = 0; n < N; n++)     { uint32_t b; memcpy(&b, &y_f32[n], 4);   puthex(b); putc_(n % 8 == 7 ? '\n' : ' '); }
    puts_("Q15\n");     for (int n = 0; n < N; n++)     { puthex((uint16_t)y_q15[n]); putc_(n % 16 == 15 ? '\n' : ' '); }
    puts_("CFFT32\n");  for (int n = 0; n < 2 * N; n++) { uint32_t b; memcpy(&b, &fft_f[n], 4);   puthex(b); putc_(n % 8 == 7 ? '\n' : ' '); }
    puts_("CFFTQ15\n"); for (int n = 0; n < 2 * N; n++) { puthex((uint16_t)fft_q[n]); putc_(n % 16 == 15 ? '\n' : ' '); }
    puts_("=== done ===\n");
    mark_begin(99);
    for (;;);
}