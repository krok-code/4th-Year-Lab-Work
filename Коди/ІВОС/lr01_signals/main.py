import os
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

# 1. Вихідні дані для варіанта 9[cite: 18]
Fs = 8500.0
f1, f2, f3 = 750.0, 2775.0, 5250.0
A1, A2, A3 = 1.0, 0.5, 0.3

print(f"Варіант 9: Fs = {Fs:.0f} Гц, f1 = {f1:.0f} Гц, f2 = {f2:.0f} Гц, f3 = {f3:.0f} Гц")
print(f"Частота Найквіста: {Fs/2:.0f} Гц")

# 2. Ручний розрахунок дзеркальної частоти (перебір k = 0..3)[cite: 17]
k_vals = range(4)
candidates = [abs(f3 - k * Fs) for k in k_vals]
f_alias_calc = min(candidates)
for k, val in zip(k_vals, candidates):
    print(f"  k={k}: |{f3:.0f} - {k}*{Fs:.0f}| = {val:.0f} Гц")
print(f"Розрахована f_alias = {f_alias_calc:.0f} Гц\n")

# 3. Моделювання "аналогового" тракту на частоті 8 * Fs[cite: 16]
M = 8
Fs_high = Fs * M
duration = 0.5
t_high = np.arange(0, duration, 1.0 / Fs_high)
x_analog = (A1 * np.sin(2 * np.pi * f1 * t_high) +
            A2 * np.sin(2 * np.pi * f2 * t_high) +
            A3 * np.sin(2 * np.pi * f3 * t_high))

# Дискретизація БЕЗ антиаліасингового фільтра[cite: 17]
x_no_filter = x_analog[::M]

# Антиаліасинговий ФНЧ (КІХ-фільтр з вікном Блекмена, зріз 3600 Гц < Fs/2) на чистому NumPy[cite: 16, 17]
numtaps = 257
fc_norm = 3600.0 / Fs_high
n_tap = np.arange(numtaps) - (numtaps - 1) / 2.0
h_ideal = 2 * fc_norm * np.sinc(2 * fc_norm * n_tap)
h_flt = h_ideal * np.blackman(numtaps)
h_flt /= np.sum(h_flt)

x_filtered_high = np.convolve(x_analog, h_flt, mode='same')
x_with_filter = x_filtered_high[::M]

# Спектральний аналіз (вікно Хеннінга)[cite: 16, 19]
def get_spectrum_db(x, fs):
    N = len(x)
    win = np.hanning(N)
    spec = np.fft.rfft(x * win) / (N * 0.5 / 2.0)
    freqs = np.fft.rfftfreq(N, 1.0 / fs)
    mag_db = 20 * np.log10(np.maximum(np.abs(spec), 1e-12))
    return freqs, mag_db

freqs, spec_no_flt = get_spectrum_db(x_no_filter, Fs)
_, spec_with_flt = get_spectrum_db(x_with_filter, Fs)

search_mask = (freqs >= f_alias_calc - 20) & (freqs <= f_alias_calc + 20)
f_alias_meas = freqs[search_mask][np.argmax(spec_no_flt[search_mask])]
lvl_no_flt = np.max(spec_no_flt[search_mask])
lvl_with_flt = np.max(spec_with_flt[search_mask])
attenuation = lvl_with_flt - lvl_no_flt

print(f"Виміряно у спектрі без фільтра: {f_alias_meas:.1f} Гц (рівень {lvl_no_flt:.2f} дБ)")
print(f"Рівень з фільтром: {lvl_with_flt:.2f} дБ -> Придушення f3: {attenuation:.2f} дБ\n")

# Графік 1: Спектри без фільтра та з фільтром[cite: 19]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
ax1.plot(freqs, spec_no_flt, color='#1f77b4', lw=1.2)
ax1.plot(f_alias_meas, lvl_no_flt, 'ro')
ax1.annotate(f'f_alias = {f_alias_meas:.0f} Гц ({lvl_no_flt:.1f} дБ)',
             xy=(f_alias_meas, lvl_no_flt), xytext=(f_alias_meas - 1100, lvl_no_flt + 6),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', fontweight='bold')
ax1.set_title('Спектр сигналу після дискретизації БЕЗ антиаліасингового фільтра')
ax1.set_ylabel('Амплітуда, дБ')
ax1.set_ylim(-110, 10)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2.plot(freqs, spec_with_flt, color='#2ca02c', lw=1.2)
ax2.plot(f_alias_meas, lvl_with_flt, 'ko')
ax2.annotate(f'Придушено до {lvl_with_flt:.1f} дБ (Δ = {attenuation:.1f} дБ)',
             xy=(f_alias_meas, lvl_with_flt), xytext=(f_alias_meas - 1400, lvl_with_flt + 20),
             arrowprops=dict(arrowstyle='->', color='black'))
ax2.set_title('Спектр сигналу після дискретизації З антиаліасинговим ФНЧ')
ax2.set_xlabel('Частота, Гц')
ax2.set_ylabel('Амплітуда, дБ')
ax2.set_ylim(-110, 10)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("figures/lr1_alias.png", dpi=200)
plt.close()

# 4. Дослідження шуму квантування[cite: 17, 18]
f_ref = 1013.7
t_q = np.arange(0, 1.0, 1.0 / Fs)
x_ref = np.sin(2 * np.pi * f_ref * t_q)
P_signal = np.mean(x_ref ** 2)

bits_list = [4, 6, 8, 10, 12, 14, 16]
snr_exp_list, snr_th_list = [], []

print(f"{'b':>3s} | {'SNR експ., дБ':>13s} | {'SNR теор., дБ':>13s} | {'Відхилення, дБ':>14s}")
print("-" * 52)
for b in bits_list:
    q = 2.0 / (2 ** b)
    x_quant = np.clip(np.round(x_ref / q) * q, -1.0, 1.0 - q)
    P_noise = np.mean((x_ref - x_quant) ** 2)
    snr_exp = 10 * np.log10(P_signal / P_noise)
    snr_th = 6.02 * b + 1.76
    snr_exp_list.append(snr_exp)
    snr_th_list.append(snr_th)
    print(f"{b:3d} | {snr_exp:13.2f} | {snr_th:13.2f} | {snr_exp - snr_th:14.2f}")

# Графік 2: SNR від розрядності[cite: 19]
plt.figure(figsize=(8, 5))
plt.plot(bits_list, snr_th_list, 'k--', lw=1.5, label='Теоретична: 6,02·b + 1,76')
plt.plot(bits_list, snr_exp_list, 'bo-', lw=1.8, markersize=6, label='Експериментальна (модель АЦП)')
plt.title('Залежність відношення сигнал/шум (SNR) від розрядності АЦП')
plt.xlabel('Розрядність АЦП b, біт')
plt.ylabel('SNR, дБ')
plt.xticks(bits_list)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("figures/lr1_snr.png", dpi=200)
plt.close()

# 5. Чотири специфічні сигнали[cite: 17, 19]
N_sig = 512
n = np.arange(N_sig)
t_s = n / Fs

s_imp = np.zeros(N_sig)
s_imp[10] = 1.0

s_step = np.where(n >= 10, 1.0, 0.0)

# ЛЧМ-сигнал (100..4000 Гц) через аналітичну фазу: phi(t) = 2*pi*(f0*t + (f1-f0)/(2*T)*t^2)
f0_c, f1_c = 100.0, 4000.0
T_c = t_s[-1]
s_chirp = np.cos(2 * np.pi * (f0_c * t_s + ((f1_c - f0_c) / (2 * T_c)) * (t_s ** 2)))

rng = np.random.default_rng(42)
s_noise = rng.normal(0.0, 0.3, N_sig)

signals_data = [
    ("Одиничний імпульс δ(n - 10)", s_imp),
    ("Одиничний стрибок u(n - 10)", s_step),
    ("ЛЧМ-сигнал (100–4000 Гц)", s_chirp),
    ("Білий гаусівський шум", s_noise)
]

fig, axes = plt.subplots(4, 2, figsize=(12, 11))
for idx, (title, sig) in enumerate(signals_data):
    ax_t = axes[idx, 0]
    if idx < 2:
        ax_t.stem(n[:60], sig[:60], basefmt=" ")
        ax_t.set_xlabel('Відліки n')
    else:
        ax_t.plot(t_s * 1000, sig, lw=1.0)
        ax_t.set_xlabel('Час, мс')
    ax_t.set_title(f"{title} — часова область")
    ax_t.set_ylabel('Амплітуда')
    ax_t.grid(True, linestyle='--', alpha=0.6)

    ax_f = axes[idx, 1]
    f_sp = np.fft.rfftfreq(N_sig, 1.0 / Fs)
    mag_sp = np.abs(np.fft.rfft(sig)) / N_sig
    ax_f.plot(f_sp, mag_sp, color='#d62728', lw=1.2)
    ax_f.set_title(f"{title} — модуль спектра")
    ax_f.set_xlabel('Частота, Гц')
    ax_f.set_ylabel('|X(f)|')
    ax_f.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("figures/lr1_signals.png", dpi=200)
plt.close()

print("\nГрафіки успішно збережено у папку figures/: lr1_alias.png, lr1_snr.png, lr1_signals.png")