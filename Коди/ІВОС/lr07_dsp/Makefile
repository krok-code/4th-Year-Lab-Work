CC = arm-none-eabi-gcc
DSP = CMSIS-DSP
CORE = CMSIS_5/CMSIS/Core/Include
CFLAGS = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard
CFLAGS += $(CFLAGS_EXTRA) -O2 -g -Wall -ffunction-sections -fdata-sections
CFLAGS += -DARM_MATH_CM4 -D__FPU_PRESENT=1 -DSTM32F407xx -I$(CORE) -I$(DSP)/Include -I$(DSP)/PrivateInclude -I.
LDFLAGS = -T stm32f407.ld -nostartfiles -Wl,--gc-sections -Wl,-Map=lr7.map -lm
DSPSRC = $(DSP)/Source/FilteringFunctions/arm_fir_f32.c $(DSP)/Source/FilteringFunctions/arm_fir_init_f32.c \
 $(DSP)/Source/FilteringFunctions/arm_fir_q15.c $(DSP)/Source/FilteringFunctions/arm_fir_init_q15.c \
 $(filter-out %f16.c %f64.c %_mve.c,$(wildcard $(DSP)/Source/TransformFunctions/arm_cfft_*.c $(DSP)/Source/TransformFunctions/arm_bitreversal*.c)) \
 $(DSP)/Source/CommonTables/arm_common_tables.c $(DSP)/Source/CommonTables/arm_const_structs.c
SRC = main.c startup.c $(sort $(DSPSRC))

lr7.elf: $(SRC) fir_q15.h fir_f32.h
	$(CC) $(CFLAGS) $(SRC) $(LDFLAGS) -o $@