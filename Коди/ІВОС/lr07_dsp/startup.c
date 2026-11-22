#include <stdint.h>
extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss, _estack;
extern int main(void);
void Reset_Handler(void);
void Default_Handler(void) { for (;;); }
__attribute__((section(".isr_vector"), used)) const void *vectors[16 + 82] = {
    &_estack, Reset_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler
};
void Reset_Handler(void) {
    uint32_t *s = &_sidata, *d = &_sdata;
    while (d < &_edata) *d++ = *s++;
    for (d = &_sbss; d < &_ebss;) *d++ = 0;
    *(volatile uint32_t *)0xE000ED88 |= (0xFu << 20); /* увімкнути FPU (CPACR) */
    __asm volatile("dsb; isb");
    main();
    for (;;);
}