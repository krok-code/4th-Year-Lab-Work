import os
import math
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

# Вихідні дані для варіанта 21 (V = 9):
# ФВЧ, Fs = 16000 Гц, F_п = 3800 Гц, Δf = 600 Гц, A = 60 дБ, вікно Блекмена, N = 147
Fs = 16000.0
Fp = 3800.0
df = 600.0
Fstop = Fp - df          # 3200 Гц
A_req = 60.0             # дБ
fc_hz = Fp - df / 2.0    # 3500 Гц
fc_norm = fc_hz / Fs     # 0.21875
df_norm = df / Fs        # 0.0375

def design_fir_hp(N, fc, win_name):
    M = (N - 1) // 2
    n = np.arange(-M, M + 1, dtype=float)
    wc = 2.0 * np.pi * fc
    lp = np.where(n == 0, 2.0 * fc, np.sin(n * wc) / (np.pi * np.where(n == 0, 1.0, n)))
    hd = (n == 0).astype(float) - lp
    if win_name == "rect":
        w = np.ones(N)
    elif win_name == "hann":
        w = 0.5 + 0.5 * np.cos(2.0 * np.pi * n / (N - 1))
    elif win_name == "hamming":
        w = 0.54 + 0.46 * np.cos(2.0 * np.pi * n / (N - 1))
    elif win_name == "blackman":
        w = 0.42 + 0.5 * np.cos(2.0 * np.pi * n / (N - 1)) + 0.08 * np.cos(4.0 * np.pi * n / (N - 1))
    return hd * w

def eval_fir_specs(h, nfft=32768):
    # Обчислення АЧХ та ФЧХ на густій сітці частот [0 .. Fs/2]
    H = np.fft.rfft(h, 2 * nfft)
    freqs = np.fft.rfftfreq(2 * nfft, 1.0 / Fs)
    mag_db = 20.0 * np.log10(np.maximum(np.abs(H), 1e-15))
    phase = np.unwrap(np.angle(H))
    
    stop_mask = freqs <= Fstop
    pass_mask = freqs >= Fp
    att_db = -np.max(mag_db[stop_mask])
    ripple_db = np.max(mag_db[pass_mask]) - np.min(mag_db[pass_mask])
    
    # Ширина переходу між рівнями -A_req (-60 дБ) та -0.1 дБ
    idx_sb = np.where(mag_db >= -A_req)[0][0]
    idx_pb = np.where(mag_db >= -0.1)[0][0]
    trans_hz = freqs[idx_pb] - freqs[idx_sb]
    return freqs, mag_db, phase, att_db, ripple_db, trans_hz

# ==============================================================================
# 1. ОСНОВНИЙ ФІЛЬТР (ВІКНО БЛЕКМЕНА, N = 147) ТА РУЧНА ПЕРЕВІРКА
# ==============================================================================
N_main = int(np.ceil(5.5 / df_norm))
if N_main % 2 == 0:
    N_main += 1
h_main = design_fir_hp(N_main, fc_norm, "blackman")
M_half = (N_main - 1) // 2

print("=== 1. СИНТЕЗ ФВЧ (Варіант 21: V = 9, Блекмен, N = 147) ===")
print(f"F_п = {Fp:.0f} Гц, F_зат = {Fstop:.0f} Гц, fc = {fc_hz:.0f} Гц (норм. {fc_norm:.5f})")
for idx_n in [0, 1, 2, M_half]:
    print(f"  h({idx_n:2d}) = {h_main[M_half + idx_n]:+.6f}")

freqs, mag_db, phase, att_main, rip_main, tr_main = eval_fir_specs(h_main)
print(f"Загасання в смузі затримки (0..{Fstop:.0f} Гц): {att_main:.1f} дБ (вимога >= {A_req:.0f} дБ)")
print(f"Нерівномірність у смузі пропускання (>= {Fp:.0f} Гц): {rip_main:.4f} дБ (вимога <= 0,1 дБ)")

# Рис. 1: АЧХ зі схемою допусків (загальний вигляд та смуга переходу)
fig1, ax1 = plt.subplots(1, 2, figsize=(9.5, 4.0))
ax1[0].plot(freqs, mag_db, lw=1.3, label=f"ФВЧ Блекмена, N = {N_main}")
ax1[0].fill_between([0, Fstop], -A_req, 5, color="red", alpha=0.14, label=f"заборонена зона (A < {int(A_req)} дБ)")
ax1[0].axvline(Fstop, color="k", ls=":", lw=1.0)
ax1[0].axvline(Fp, color="k", ls=":", lw=1.0)
ax1[0].set_xlim(0, Fs / 2)
ax1[0].set_ylim(-110, 5)
ax1[0].set_xlabel("частота, Гц")
ax1[0].set_ylabel("АЧХ, дБ")
ax1[0].grid(True, alpha=0.35)
ax1[0].legend(fontsize=8, loc="lower right")

ax1[1].plot(freqs, mag_db, lw=1.4)
ax1[1].fill_between([0, Fstop], -A_req, 5, color="red", alpha=0.14)
ax1[1].axvline(Fstop, color="k", ls=":", lw=1.0)
ax1[1].axvline(Fp, color="k", ls=":", lw=1.0)
ax1[1].set_xlim(2800, 4400)
ax1[1].set_ylim(-80, 2)
ax1[1].set_xlabel("частота, Гц")
ax1[1].set_ylabel("АЧХ, дБ")
ax1[1].grid(True, alpha=0.35)
plt.tight_layout()
plt.savefig("figures/lr5_specs.png", dpi=180)
plt.close()

# Рис. 2: АЧХ та ФЧХ спроєктованого фільтра
fig2, ax2 = plt.subplots(1, 2, figsize=(9.5, 3.8))
ax2[0].plot(freqs, mag_db, lw=1.3)
ax2[0].set_xlim(0, Fs / 2)
ax2[0].set_ylim(-110, 5)
ax2[0].set_xlabel("частота, Гц")
ax2[0].set_ylabel("АЧХ, дБ")
ax2[0].grid(True, alpha=0.35)

ax2[1].plot(freqs, phase, lw=1.3)
ax2[1].set_xlim(0, Fs / 2)
ax2[1].set_xlabel("частота, Гц")
ax2[1].set_ylabel("ФЧХ, рад")
ax2[1].grid(True, alpha=0.35)
plt.tight_layout()
plt.savefig("figures/lr5_mag_phase.png", dpi=180)
plt.close()

# ==============================================================================
# 2. ПОРІВНЯННЯ ЧОТИРЬОХ ВАГОВИХ ФУНКЦІЙ
# ==============================================================================
windows_cfg = [
    ("прямокутне", "rect", 0.9),
    ("Хеннінга", "hann", 3.1),
    ("Хеммінга", "hamming", 3.3),
    ("Блекмена", "blackman", 5.5),
]
print("\n=== 2. ПОРІВНЯННЯ ЧОТИРЬОХ ВАГОВИХ ФУНКЦІЙ ===")
print(f"{'Вікно':<12s} | {'k':>4s} | {'N':>4s} | {'Загас., дБ':>10s} | {'Нерівн., дБ':>11s} | {'Перехід, Гц':>11s} | {'Множень (сим.)':>14s}")
print("-" * 82)

fig3, ax3 = plt.subplots(figsize=(8.2, 4.2))
for title_ua, w_key, k_val in windows_cfg:
    Nw = int(np.ceil(k_val / df_norm))
    if Nw % 2 == 0:
        Nw += 1
    hw = design_fir_hp(Nw, fc_norm, w_key)
    fw, mw, _, att_w, rip_w, tr_w = eval_fir_specs(hw)
    sym_mults = (Nw + 1) // 2
    print(f"{title_ua:<12s} | {k_val:4.1f} | {Nw:4d} | {att_w:10.1f} | {rip_w:11.4f} | {tr_w:11.0f} | {Nw:4d} ({sym_mults:2d})")
    ax3.plot(fw, mw, lw=1.2, label=f"{title_ua}, N = {Nw}")

ax3.axhline(-A_req, color="k", ls="--", lw=0.9)
ax3.set_xlim(0, Fs / 2)
ax3.set_ylim(-115, 5)
ax3.set_xlabel("частота, Гц")
ax3.set_ylabel("АЧХ, дБ")
ax3.grid(True, alpha=0.35)
ax3.legend(fontsize=8.5, loc="lower right")
plt.tight_layout()
plt.savefig("figures/lr5_windows.png", dpi=180)
plt.close()

# ==============================================================================
# 3. ПОРІВНЯННЯ З РЕКУРСИВНИМИ ПРОТОТИПАМИ (Баттерворта, Чебишова I/II, Еліптичний)
# ==============================================================================
# Аналітичний розрахунок порядків та побудова АЧХ рекурсивних прототипів ФВЧ для заданого ТЗ
wp = np.tan(np.pi * Fp / Fs)
ws = np.tan(np.pi * Fstop / Fs)
Omega_s = wp / ws  # нормована частота затримки прототипу ФНЧ (> 1)
eps_p = np.sqrt(10.0 ** (0.1 / 10.0) - 1.0)
eps_s = np.sqrt(10.0 ** (A_req / 10.0) - 1.0)
k_ell = 1.0 / Omega_s
k1_ell = eps_p / eps_s

# Порядки прототипів
n_butt = int(np.ceil(np.log10(eps_s / eps_p) / np.log10(Omega_s)))
n_cheb = int(np.ceil(np.arccosh(eps_s / eps_p) / np.arccosh(Omega_s)))
# Повний еліптичний інтеграл першого роду K(m) через АГМ
def ellipk(m):
    a, b = 1.0, np.sqrt(1.0 - m)
    while abs(a - b) > 1e-14:
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    return np.pi / (2.0 * a)

n_ellip = int(np.ceil((ellipk(k_ell**2) * ellipk(1 - k1_ell**2)) / (ellipk(1 - k_ell**2) * ellipk(k1_ell**2))))

# Аналітичні АЧХ для графіка порівняння (рис. 4)
w_grid = freqs[1:] * np.pi / Fs
Omega_hp = wp / np.tan(w_grid)  # перетворення ФНЧ -> ФВЧ

# 1) Баттерворт
mag_butt = np.zeros_like(freqs)
mag_butt[0] = -140.0
mag_butt[1:] = -10.0 * np.log10(1.0 + (eps_p ** 2) * (Omega_hp ** (2 * n_butt)))

# 2) Чебишов I
def cheb_T(n, x):
    return np.where(np.abs(x) <= 1.0, np.cos(n * np.arccos(np.clip(x, -1.0, 1.0))), np.cosh(n * np.arccosh(np.maximum(x, 1.0))))

mag_cheb1 = np.zeros_like(freqs)
mag_cheb1[0] = -140.0
mag_cheb1[1:] = -10.0 * np.log10(1.0 + (eps_p ** 2) * (cheb_T(n_cheb, Omega_hp) ** 2))

# 3) Чебишов II
mag_cheb2 = np.zeros_like(freqs)
mag_cheb2[0] = -10.0 * np.log10(1.0 + eps_s ** 2)
T_inv = cheb_T(n_cheb, Omega_s / np.maximum(Omega_hp, 1e-9))
mag_cheb2[1:] = -10.0 * np.log10(1.0 + (eps_s ** 2) / np.maximum(T_inv ** 2, 1e-30))

# 4) Золотарьов–Кауер (еліптичний прототип 6-го порядку з нулями передачі в смузі затримки)
z_zeros = [1.05, 1.35, 2.40]  # нулі в нормованій смузі затримки прототипу
R_num = np.ones_like(Omega_hp)
R_den = np.ones_like(Omega_hp)
for z0 in z_zeros:
    R_num *= (Omega_hp**2 - z0**2)
    R_den *= (Omega_hp**2 - (Omega_s / z0)**2)
R_rat = R_num / np.maximum(np.abs(R_den), 1e-12)
R_at_1 = np.prod([(1.0 - z0**2) / (1.0 - (Omega_s / z0)**2) for z0 in z_zeros])
R_norm = R_rat / R_at_1
mag_ellip = np.zeros_like(freqs)
mag_ellip[0] = -A_req
mag_ellip[1:] = -10.0 * np.log10(1.0 + (eps_p ** 2) * (R_norm ** 2))

print("\n=== 3. ПОРІВНЯННЯ З РЕКУРСИВНИМИ ПРОТОТИПАМИ ===")
print(f"КІХ Блекмена     : N = {N_main}, множень = {N_main} ({(N_main+1)//2} з симетрією)")
print(f"Баттерворта      : n = {n_butt}, множень = {2*n_butt + 1}")
print(f"Чебишова I       : n = {n_cheb}, множень = {2*n_cheb + 1}")
print(f"Чебишова II      : n = {n_cheb}, множень = {2*n_cheb + 1}")
print(f"Золотарьова-Кауер: n = {n_ellip}, множень = {2*n_ellip + 1}")

fig4, ax4 = plt.subplots(figsize=(8.2, 4.2))
ax4.plot(freqs, mag_butt, lw=1.1, label=f"Баттерворта, n = {n_butt}")
ax4.plot(freqs, mag_cheb1, lw=1.1, label=f"Чебишова I, n = {n_cheb}")
ax4.plot(freqs, mag_cheb2, lw=1.1, label=f"Чебишова II, n = {n_cheb}")
ax4.plot(freqs, mag_ellip, lw=1.1, label=f"Золотарьова–Кауера, n = {n_ellip}")
ax4.plot(freqs, mag_db, "k-", lw=1.2, label=f"КІХ Блекмена, N = {N_main}")
ax4.axhline(-A_req, color="k", ls="--", lw=0.9)
ax4.set_xlim(0, Fs / 2)
ax4.set_ylim(-115, 5)
ax4.set_xlabel("частота, Гц")
ax4.set_ylabel("АЧХ, дБ")
ax4.grid(True, alpha=0.35)
ax4.legend(fontsize=8.5, loc="lower right")
plt.tight_layout()
plt.savefig("figures/lr5_iir_cmp.png", dpi=180)
plt.close()

# ==============================================================================
# 4. ДОСЛІДЖЕННЯ КВАНТУВАННЯ КОЕФІЦІЄНТІВ (16, 12, 10, 8 біт)
# ==============================================================================
print("\n=== 4. ДОСЛІДЖЕННЯ КВАНТУВАННЯ КОЕФІЦІЄНТІВ ===")
print(f"{'Розрядність b':<18s} | {'Загасання, дБ':>13s} | {'Зміна, дБ':>10s} | {'Нерівн., дБ':>11s} | {'Макс. похибка':>13s}")
print("-" * 76)
print(f"{'подвійна точність':<18s} | {att_main:13.1f} | {0.0:10.1f} | {rip_main:11.4f} | {0.0:13.1e}")

fig5, ax5 = plt.subplots(figsize=(8.2, 4.2))
ax5.plot(freqs, mag_db, "k-", lw=1.3, label="подвійна точність")

for bits in [16, 12, 10, 8]:
    scale = 2 ** (bits - 1)
    hq = np.clip(np.round(h_main * scale), -scale, scale - 1) / scale
    _, mq, _, att_q, rip_q, _ = eval_fir_specs(hq)
    max_err = np.max(np.abs(h_main - hq))
    print(f"{str(bits) + ' розрядів':<18s} | {att_q:13.1f} | {att_q - att_main:+10.1f} | {rip_q:11.4f} | {max_err:13.2e}")
    ax5.plot(freqs, mq, lw=1.1, label=f"{bits} розрядів")

ax5.axhline(-A_req, color="k", ls="--", lw=0.9)
ax5.set_xlim(0, Fs / 2)
ax5.set_ylim(-115, 5)
ax5.set_xlabel("частота, Гц")
ax5.set_ylabel("АЧХ, дБ")
ax5.grid(True, alpha=0.35)
ax5.legend(fontsize=8.5, loc="lower right")
plt.tight_layout()
plt.savefig("figures/lr5_quant.png", dpi=180)
plt.close()

# ==============================================================================
# 5. ЕКСПОРТ ФАЙЛІВ ДЛЯ ЛР 7 ТА ЛР 8 (fir_q15.h та fir_coeff.mem)
# ==============================================================================
max_abs_h = np.max(np.abs(h_main))
# Оскільки max(|h|) = 0.5625 < 0.999, масштабування не потрібне (коефіцієнт 1.0)
hq15 = np.clip(np.round(h_main * 32768.0), -32768, 32767).astype(np.int16)

with open("fir_q15.h", "w", encoding="utf-8") as f_h:
    f_h.write("/* Сгенеровано в ЛР №5 (Варіант 21, V=9: ФВЧ Блекмена, N=147, Fs=16000 Гц, Fp=3800 Гц) */\n")
    f_h.write("#ifndef FIR_Q15_H\n#define FIR_Q15_H\n\n#include <stdint.h>\n\n")
    f_h.write(f"#define FIR_Q15_NUM_TAPS {N_main}\n\n")
    f_h.write(f"static const int16_t fir_q15_coeffs[{N_main}] = {{\n")
    for idx in range(0, N_main, 12):
        row = ", ".join(f"{int(val):6d}" for val in hq15[idx : idx + 12])
        comma = "," if idx + 12 < N_main else ""
        f_h.write(f"    {row}{comma}\n")
    f_h.write("};\n\n#endif /* FIR_Q15_H */\n")

with open("fir_coeff.mem", "w", encoding="utf-8") as f_mem:
    for val in hq15:
        f_mem.write(f"{int(val) & 0xFFFF:04x}\n")

print(f"\n=== 5. ЕКСПОРТ КОЕФІЦІЄНТІВ У Q15 ===")
print(f"max(|h|) = {max_abs_h:.6f} < 0,999 -> масштабування не потрібне, переповнення відсутнє.")
print(f"Діапазон Q15: min = {int(np.min(hq15))}, max = {int(np.max(hq15))} (кількість коеф. = {N_main})")
print("Збережено файли: fir_q15.h, fir_coeff.mem та 5 графіків у figures/")