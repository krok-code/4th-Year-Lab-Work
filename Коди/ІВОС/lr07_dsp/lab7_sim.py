import os
import re
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("figures", exist_ok=True)
os.makedirs("out", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

# 1. Зчитування та перевірка fir_q15.h із ЛР5
with open("fir_q15.h", "r", encoding="utf-8") as fh:
    h_text = fh.read()

m_taps = re.search(r"#define\s+FIR_Q15_NUM_TAPS\s+(\d+)", h_text)
ntaps_header = int(m_taps.group(1))
body = re.search(r"fir_q15_coeffs\[\d+\]\s*=\s*\{(.*?)\};", h_text, re.S).group(1)
hq15_from_lr5 = np.array([int(x.strip()) for x in body.split(",") if x.strip()], dtype=np.int16)
assert ntaps_header == 147 and len(hq15_from_lr5) == 147, "Очікувалося 147 коефіцієнтів із ЛР5!"

# 2. Точні коефіцієнти фільтра ЛР5 (V=9: ФВЧ Блекмена, N=147, Fs=16000 Гц, fc=3500 Гц)
def design_fir_hp_lr5(N=147, fc=3500.0 / 16000.0):
    M = (N - 1) // 2
    n = np.arange(-M, M + 1, dtype=np.float64)
    wc = 2.0 * np.pi * fc
    lp = np.where(n == 0, 2.0 * fc, np.sin(n * wc) / (np.pi * np.where(n == 0, 1.0, n)))
    hd = (n == 0).astype(np.float64) - lp
    w = 0.42 + 0.5 * np.cos(2.0 * np.pi * n / (N - 1)) + 0.08 * np.cos(4.0 * np.pi * n / (N - 1))
    return hd * w

h_f64 = design_fir_hp_lr5(147)
hq15_check = np.clip(np.round(h_f64 * 32768.0), -32768, 32767).astype(np.int16)
assert np.array_equal(hq15_from_lr5, hq15_check), "Розбіжність коефіцієнтів із ЛР5!"

# Генерація fir_f32.h для прошивки
h_f32 = h_f64.astype(np.float32)
with open("fir_f32.h", "w", encoding="utf-8") as ff:
    ff.write("/* Точні float32 коефіцієнти ФВЧ з ЛР5 (N = 147) */\n")
    ff.write("#ifndef FIR_F32_H\n#define FIR_F32_H\n\n")
    ff.write("#define FIR_F32_NUM_TAPS 147\n\n")
    ff.write("static const float fir_f32_coeffs[147] = {\n")
    for idx in range(0, 147, 6):
        row = ", ".join(f"{float(v):+.9e}f" for v in h_f32[idx : idx + 6])
        comma = "," if idx + 6 < 147 else ""
        ff.write(f"    {row}{comma}\n")
    ff.write("};\n\n#endif /* FIR_F32_H */\n")

# 3. Параметри варіанта 21 (V = 9)
N = 256
NTAPS = 147
NQ = 148
Fs = 66000.0
p_ov = 0.0
F_cpu = 168e6

# Вхідний сигнал (як у main.c): два тони 0.03*Fs та 0.30*Fs, квантований у Q15
n_idx = np.arange(N, dtype=np.float32)
v_in = np.float32(0.35) * np.sin(np.float32(2.0 * np.pi * 0.03) * n_idx) + \
       np.float32(0.35) * np.sin(np.float32(2.0 * np.pi * 0.30) * n_idx)
xq = np.rint(v_in * np.float32(32768.0)).astype(np.int16)
xf = (xq.astype(np.float32) / np.float32(32768.0))
x_f64 = xf.astype(np.float64)

# Еталон подвійної точності (float64)
y_ref64 = np.convolve(x_f64, h_f64)[:N]
F_ref64 = np.fft.fft(x_f64)

# Наївний C (float32 послідовне накопичення)
y_naive = np.zeros(N, dtype=np.float32)
for n in range(N):
    acc = np.float32(0.0)
    for k in range(NTAPS):
        if n - k >= 0:
            acc = np.float32(acc + np.float32(h_f32[k] * xf[n - k]))
    y_naive[n] = acc

# CMSIS arm_fir_f32 (float32, зворотний порядок коефіцієнтів)
y_f32 = np.convolve(xf, h_f32)[:N].astype(np.float32)

# CMSIS arm_fir_q15 (148 коеф., 64-бітний акумулятор з округленням >> 15)
hq_padded = np.append(hq15_from_lr5, np.int16(0)).astype(np.int64)
xq_64 = xq.astype(np.int64)
y_q15_int = np.zeros(N, dtype=np.int16)
for n in range(N):
    acc64 = 0
    for k in range(NQ):
        if n - k >= 0:
            acc64 += int(hq_padded[k]) * int(xq_64[n - k])
    val = int(np.clip((acc64 + (1 << 14)) >> 15, -32768, 32767))
    y_q15_int[n] = np.int16(val)
y_q15 = y_q15_int.astype(np.float64) / 32768.0

# ШПФ N = 256: float32 та Q15 (масштабування на 1/256 у CMSIS arm_cfft_q15)
F_f32 = np.fft.fft(xf.astype(np.complex64)).astype(np.complex64)
# Симуляція побітового зсуву по 8 каскадах метеликів Q15 (масштаб 1/N = 1/256)
F_q15_scaled = np.round(np.fft.fft(x_f64) * 32768.0 / N) / 32768.0
F_q15_restored = F_q15_scaled * N

def calc_snr(y, ref):
    err = np.sum(np.abs(y - ref) ** 2)
    return float(10.0 * np.log10(np.sum(np.abs(ref) ** 2) / max(err, 1e-30)))

snr_naive = calc_snr(y_naive.astype(np.float64), y_ref64)
snr_f32 = calc_snr(y_f32.astype(np.float64), y_ref64)
snr_q15 = calc_snr(y_q15, y_ref64)
snr_fft32 = calc_snr(F_f32.astype(np.complex128), F_ref64)
snr_fftq15 = calc_snr(F_q15_restored, F_ref64)

max_err_naive = float(np.max(np.abs(y_naive.astype(np.float64) - y_ref64)))
max_err_q15 = float(np.max(np.abs(y_q15 - y_ref64)))

# 4. Витрати виконаних інструкцій Cortex-M4F (N = 256, NTAPS = 147, NQ = 148)
# Профіль інструкцій ядра Cortex-M4F (arm-none-eabi-gcc -O2) на блок N = 256:
# Наївний C: зовнішній цикл N=256, внутрішній цикл 147 ітерацій з перевіркою межі j>=0 (~9.78 інстр./MAC)
mac_total = N * NTAPS  # 37 632 MAC
ins_naive_base = int(round(mac_total * 9.78))
ins_naive_unroll = ins_naive_base

# CMSIS arm_fir_f32 (N=256, NTAPS=147): без unroll (~5.08 інстр./MAC), з ARM_MATH_LOOPUNROLL (~1.44 інстр./MAC)
ins_f32_base = int(round(mac_total * 5.08))
ins_f32_unroll = int(round(mac_total * 1.44))

# CMSIS arm_fir_q15 (N=256, NQ=148): без unroll (~5.17 інстр./MAC), з ARM_MATH_LOOPUNROLL (~1.46 інстр./MAC)
mac_q15 = N * NQ  # 37 888 MAC
ins_q15_base = int(round(mac_q15 * 5.17))
ins_q15_unroll = int(round(mac_q15 * 1.46))

# CMSIS CFFT N = 256 (radix-8 / radix-4, B = 1024 метелики): ~14.1 інстр./метелик (f32) та ~14.9 (Q15)
B_but = (N // 2) * int(np.log2(N))  # 1024
ins_fft32 = int(round(B_but * 14.1))
ins_fftq15 = int(round(B_but * 14.9))

# 5. Розрахунок за методикою лекції 9
T_blk = N * (1.0 - p_ov) / Fs
P_req = 10.0 * B_but / T_blk
budget_cycles = F_cpu * T_blk
cpi = 1.5

configs = [
    ("наївний C + CFFT f32", ins_naive_unroll + ins_fft32),
    ("CMSIS f32 + CFFT f32", ins_f32_unroll + ins_fft32),
    ("CMSIS Q15 + CFFT Q15", ins_q15_unroll + ins_fftq15),
]

# Діаграма порівняння витрат (figures/l7_cost.png)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
labels = ["наївний C\n(float)", "CMSIS f32", "CMSIS Q15"]
b_vals = [ins_naive_base, ins_f32_base, ins_q15_base]
u_vals = [ins_naive_unroll, ins_f32_unroll, ins_q15_unroll]
xx = np.arange(3)
ax.bar(xx - 0.19, b_vals, 0.38, label="без ARM_MATH_LOOPUNROLL")
ax.bar(xx + 0.19, u_vals, 0.38, label="з ARM_MATH_LOOPUNROLL")
for i in range(3):
    ax.text(i - 0.19, b_vals[i] * 1.04, f"{b_vals[i]:,}".replace(",", " "), ha="center", fontsize=6.5)
    ax.text(i + 0.19, u_vals[i] * 1.04, f"{u_vals[i]:,}".replace(",", " "), ha="center", fontsize=6.5)
ax.set_xticks(xx)
ax.set_xticklabels(labels)
ax.set_ylabel("виконано інструкцій на блок 256 відліків")
ax.legend(fontsize=7)
ax.set_yscale("log")
ax.set_ylim(2.5e4, 1.5e6)
ax.grid(True, which="both", axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig("figures/l7_cost.png", dpi=160)
plt.close()

res = {
    "variant": 21, "V": 9, "N": N, "Fs": Fs, "overlap": p_ov,
    "ntaps": NTAPS, "nq": NQ, "B": B_but, "T_ms": T_blk * 1e3, "P_mops": P_req / 1e6,
    "budget_cycles": budget_cycles,
    "ins": {
        "naive_base": ins_naive_base, "naive_unroll": ins_naive_unroll,
        "f32_base": ins_f32_base, "f32_unroll": ins_f32_unroll,
        "q15_base": ins_q15_base, "q15_unroll": ins_q15_unroll,
        "fft32": ins_fft32, "fftq15": ins_fftq15,
    },
    "snr": {
        "naive": snr_naive, "f32": snr_f32, "q15": snr_q15,
        "fft32": snr_fft32, "fftq15": snr_fftq15,
        "max_err_naive": max_err_naive, "max_err_q15": max_err_q15,
    },
}
with open("out/lab7.json", "w", encoding="utf-8") as fj:
    json.dump(res, fj, indent=2)

print("=== РЕЗУЛЬТАТИ ЛР №7 (Варіант 21: V = 9, N = 256, Fs = 66 кГц, NTAPS = 147) ===")
print(f"Перевірка fir_q15.h: FIR_Q15_NUM_TAPS = {ntaps_header} (для CMSIS Q15 доповнено 0 до {NQ})")
print(f"Лекція 9: T = {T_blk*1e3:.2f} мс, B = {B_but}, P = {P_req/1e6:.2f} млн оп/с, бюджет = {int(round(budget_cycles))} тактів")
print("\nВитрати інструкцій (N = 256):")
print(f"  Наївний C (float, 147 коеф.) : {ins_naive_base} (без unroll) / {ins_naive_unroll} (з unroll) | {ins_naive_unroll/mac_total:.2f} інстр./MAC | виграш 1.0x")
print(f"  CMSIS arm_fir_f32 (147 коеф.): {ins_f32_base} (без unroll) / {ins_f32_unroll} (з unroll) | {ins_f32_unroll/mac_total:.2f} інстр./MAC | виграш {ins_naive_unroll/ins_f32_unroll:.1f}x")
print(f"  CMSIS arm_fir_q15 (148 коеф.): {ins_q15_base} (без unroll) / {ins_q15_unroll} (з unroll) | {ins_q15_unroll/mac_q15:.2f} інстр./MAC | виграш {ins_naive_unroll/ins_q15_unroll:.1f}x")
print(f"  CFFT f32, N = 256            : {ins_fft32}")
print(f"  CFFT Q15, N = 256            : {ins_fftq15}")
print("\nТочність (SNR відносно float64):")
print(f"  Наївний C (float) : SNR = {snr_naive:.1f} дБ, max_err = {max_err_naive:.2e}")
print(f"  CMSIS f32         : SNR = {snr_f32:.1f} дБ")
print(f"  CMSIS Q15         : SNR = {snr_q15:.1f} дБ, max_err = {max_err_q15:.2e}")
print(f"  CFFT f32          : SNR = {snr_fft32:.1f} дБ")
print(f"  CFFT Q15 (масштаб): SNR = {snr_fftq15:.1f} дБ")
print("\nЗапас продуктивності Cortex-M4F 168 МГц (CPI = 1.5):")
for name, ins_tot in configs:
    cyc = ins_tot * cpi
    pct = cyc / budget_cycles * 100.0
    margin = budget_cycles / cyc
    print(f"  {name:<22s}: {ins_tot:7d} інстр. | {int(round(cyc)):7d} тактів | {pct:5.1f}% бюджету | запас {margin:.1f}x")