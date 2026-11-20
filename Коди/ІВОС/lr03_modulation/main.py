import os
import math
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

# Вихідні дані для варіанта 21 (V = 9):
# f_c = 24000 Гц, F = 700 Гц, Fs = 200 кГц, девіації = 1000 / 5000 / 15000 Гц, QPSK і 16-QAM
Fs = 200000.0
fc = 24000.0
F_mod = 700.0
N = int(Fs)  # 1 с даних (200 000 відліків) -> крок по частоті 1 Гц, когерентна вибірка
t = np.arange(N) / Fs

def one_sided_spectrum(x):
    X = np.fft.rfft(x) / len(x) * 2.0
    return np.fft.rfftfreq(len(x), 1.0 / Fs), np.abs(X)

# ==============================================================================
# 0. СХЕМА З'ЄДНАНЬ БЛОКІВ АМ-МОДУЛЯТОРА
# ==============================================================================
fig_b, ax_b = plt.subplots(figsize=(8.6, 2.3))
ax_b.axis("off")

def draw_box(x, y, text, w=1.65, h=0.65):
    ax_b.add_patch(plt.Rectangle((x, y), w, h, fill=False, lw=1.2))
    ax_b.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

draw_box(0.0, 1.25, "Signal Source\nf_mod = 700 Гц")
draw_box(0.0, 0.25, "Signal Source\nf_c = 24 кГц")
draw_box(2.15, 1.25, "Multiply Const\nm")
draw_box(4.30, 1.25, "Add Const\n1,0")
draw_box(6.45, 0.75, "Multiply")
draw_box(8.55, 0.75, "Throttle\n200 кГц", w=1.35)

ax_b.annotate("", (2.15, 1.57), (1.65, 1.57), arrowprops=dict(arrowstyle="->", lw=1.1))
ax_b.annotate("", (4.30, 1.57), (3.80, 1.57), arrowprops=dict(arrowstyle="->", lw=1.1))
ax_b.annotate("", (6.45, 1.20), (5.95, 1.57), arrowprops=dict(arrowstyle="->", lw=1.1))
ax_b.annotate("", (6.45, 0.90), (1.65, 0.57), arrowprops=dict(arrowstyle="->", lw=1.1))
ax_b.annotate("", (8.55, 1.07), (8.10, 1.07), arrowprops=dict(arrowstyle="->", lw=1.1))
ax_b.text(10.05, 1.07, "→ Time Sink,\n   Freq Sink", fontsize=8, va="center")
ax_b.set_xlim(-0.2, 11.7)
ax_b.set_ylim(0.0, 2.1)
plt.savefig("figures/lr3_blocks.png", dpi=180, bbox_inches="tight")
plt.close()

# ==============================================================================
# ЧАСТИНА А: АМПЛІТУДНА МОДУЛЯЦІЯ (АМ)
# ==============================================================================
print("=== ЧАСТИНА А: Амплітудна модуляція (fc = 24 кГц, F = 700 Гц) ===")
print(f"{'m':>5s} | {'Вимір., дБ':>11s} | {'Теорія, дБ':>11s} | {'Мін. огин.':>11s} | {'Спотворення, %':>15s}")
print("-" * 65)

fig_am, ax_am = plt.subplots(4, 2, figsize=(9.5, 9.5))
ic = int(fc)
df_i = int(F_mod)

# Маска Гільберта через БПФ для обчислення аналітичного сигналу / огинаючої
h_filt = np.zeros(N)
h_filt[0] = 1.0
h_filt[1 : N // 2] = 2.0
h_filt[N // 2] = 1.0

for i, m in enumerate([0.3, 0.7, 1.0, 1.3]):
    env_ideal = 1.0 + m * np.cos(2 * np.pi * F_mod * t)
    s = env_ideal * np.cos(2 * np.pi * fc * t)
    f, A = one_sided_spectrum(s)

    carrier = A[ic]
    side = 0.5 * (A[ic - df_i] + A[ic + df_i])
    meas_db = 20 * np.log10(side / carrier)
    theo_db = 20 * np.log10(m / 2.0)

    env_det = np.abs(np.fft.ifft(np.fft.fft(s) * h_filt))
    _, E_amp = one_sided_spectrum(env_det)
    k1 = E_amp[df_i]
    harmonics = np.sqrt(sum(E_amp[k * df_i] ** 2 for k in range(2, 8)))
    thd_pct = 100.0 * harmonics / k1

    print(f"{m:5.1f} | {meas_db:11.2f} | {theo_db:11.2f} | {1.0 - m:11.1f} | {thd_pct:15.3f}")

    n_plot = int(0.0045 * Fs)
    ax_am[i, 0].plot(t[:n_plot] * 1e3, s[:n_plot], lw=0.7)
    ax_am[i, 0].plot(t[:n_plot] * 1e3, env_ideal[:n_plot], "r", lw=1.0)
    ax_am[i, 0].plot(t[:n_plot] * 1e3, -env_ideal[:n_plot], "r", lw=1.0)
    ax_am[i, 0].set_title(f'm = {str(m).replace(".", ",")}', fontsize=9.5)
    ax_am[i, 0].set_xlabel("час, мс")
    ax_am[i, 0].set_ylabel("амплітуда, В")
    ax_am[i, 0].set_ylim(-2.5, 2.5)
    ax_am[i, 0].grid(True, alpha=0.35)

    ax_am[i, 1].plot(f / 1e3, 20 * np.log10(np.maximum(A, 1e-12)), lw=1.0)
    ax_am[i, 1].set_xlim(21, 27)
    ax_am[i, 1].set_ylim(-60, 3)
    ax_am[i, 1].set_xlabel("частота, кГц")
    ax_am[i, 1].set_ylabel("рівень, дБ (відн. 1 В)")
    ax_am[i, 1].grid(True, alpha=0.35)

plt.tight_layout()
plt.savefig("figures/lr3_am.png", dpi=180)
plt.close()

# ==============================================================================
# ЧАСТИНА Б: ЧАСТОТНА МОДУЛЯЦІЯ (ЧМ) ТА ПРАВИЛО КАРСОНА
# ==============================================================================
print("\n=== ЧАСТИНА Б: Частотна модуляція (fc = 24 кГц, F = 700 Гц) ===")
print(f"{'Δf, Гц':>8s} | {'β':>6s} | {'B Карсон, Гц':>13s} | {'Вимір -30 дБ, Гц':>17s} | {'Розбіжн., %':>12s} | {'Смуга 98%, Гц':>14s}")
print("-" * 82)

fig_fm, ax_fm = plt.subplots(3, 1, figsize=(8.5, 8.2))
for i, df in enumerate([1000.0, 5000.0, 15000.0]):
    beta = df / F_mod
    ph = 2 * np.pi * fc * t + beta * np.sin(2 * np.pi * F_mod * t)
    s = np.cos(ph)
    f, A = one_sided_spectrum(s)

    thr = 10.0 ** (-30.0 / 20.0)
    idx = np.where(A > thr)[0]
    flo, fhi = f[idx[0]], f[idx[-1]]
    Bm = fhi - flo

    P = (A ** 2) / 2.0
    cum_p = np.cumsum(P)
    tot_p = cum_p[-1]
    lo_98 = np.searchsorted(cum_p, 0.01 * tot_p)
    hi_98 = np.searchsorted(cum_p, 0.99 * tot_p)
    B98 = f[hi_98] - f[lo_98]

    Bc = 2.0 * (df + F_mod)
    diff_pct = (Bm - Bc) / Bc * 100.0
    print(f"{df:8.0f} | {beta:6.2f} | {Bc:13.0f} | {Bm:17.0f} | {diff_pct:11.1f}% | {B98:14.0f}")

    ax_fm[i].plot(f / 1e3, 20 * np.log10(np.maximum(A, 1e-12)), lw=0.8)
    ax_fm[i].axhline(-30.0, color="r", ls="--", lw=0.9)
    ax_fm[i].axvline(flo / 1e3, color="g", ls=":", lw=1.2)
    ax_fm[i].axvline(fhi / 1e3, color="g", ls=":", lw=1.2)
    ax_fm[i].set_xlim(0, 48)
    ax_fm[i].set_ylim(-80, 3)
    ax_fm[i].set_title(f"Δf = {int(df)} Гц, β = {beta:.2f}".replace(".", ","), fontsize=9.5)
    ax_fm[i].set_xlabel("частота, кГц")
    ax_fm[i].set_ylabel("рівень, дБ")
    ax_fm[i].grid(True, alpha=0.35)

plt.tight_layout()
plt.savefig("figures/lr3_fm.png", dpi=180)
plt.close()

# ==============================================================================
# ЧАСТИНА В: ЦИФРОВА МАНІПУЛЯЦІЯ (QPSK і 16-QAM) — СУЗІР'Я ТА КРИВА ПОМИЛОК
# ==============================================================================
rng = np.random.default_rng(7)

def qpsk_map(b):
    # Середня потужність символу Es = 1
    return ((1 - 2 * b[:, 0]) + 1j * (1 - 2 * b[:, 1])) / np.sqrt(2.0)

def qpsk_demap(r):
    return np.stack([(r.real < 0).astype(int), (r.imag < 0).astype(int)], axis=1)

def qam16_map(b):
    # Кодування Грея: 00 -> -3, 01 -> -1, 11 -> +1, 10 -> +3; середня потужність Es = 1
    def lvl(b1, b0):
        return np.where(b1 == 0, np.where(b0 == 0, -3, -1), np.where(b0 == 0, 3, 1))
    return (lvl(b[:, 0], b[:, 1]) + 1j * lvl(b[:, 2], b[:, 3])) / np.sqrt(10.0)

def qam16_demap(r):
    s = r * np.sqrt(10.0)
    def bits(x):
        return (x > 0).astype(int), (np.abs(x) < 2.0).astype(int)
    i1, i0 = bits(s.real)
    q1, q0 = bits(s.imag)
    return np.stack([i1, i0, q1, q0], axis=1)

# Перевірка коректності відображення та демодуляції Грея
test_b16 = np.array([[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0]])
assert np.array_equal(qam16_demap(qam16_map(test_b16)), test_b16)

# Сузір'я для трьох рівнів шуму sigma = 0.1; 0.4; 0.8
fig_c, ax_c = plt.subplots(2, 3, figsize=(8.8, 5.8))
for r_idx, kind in enumerate(["QPSK", "16-QAM"]):
    k = 2 if kind == "QPSK" else 4
    b = rng.integers(0, 2, (4000, k))
    x = qpsk_map(b) if kind == "QPSK" else qam16_map(b)
    for c_idx, nv in enumerate([0.1, 0.4, 0.8]):
        # Потужність комплексного шуму дорівнює nv^2 -> на кожну квадратуру I та Q припадає nv^2 / 2 (СКВ = nv / sqrt(2))
        y = x + (nv / np.sqrt(2.0)) * (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape))
        ax_c[r_idx, c_idx].plot(y.real, y.imag, ".", ms=1.6)
        ax_c[r_idx, c_idx].set_xlim(-2, 2)
        ax_c[r_idx, c_idx].set_ylim(-2, 2)
        ax_c[r_idx, c_idx].set_aspect("equal")
        ax_c[r_idx, c_idx].grid(True, alpha=0.35)
        ebn0 = 10 * np.log10((1.0 / k) / (nv ** 2))
        ax_c[r_idx, c_idx].set_title(
            f"{kind}, σ={nv} (Eb/N₀={ebn0:.1f} дБ)".replace(".", ","), fontsize=8.5
        )
        ax_c[r_idx, c_idx].set_xlabel("I")
        ax_c[r_idx, c_idx].set_ylabel("Q")

plt.tight_layout()
plt.savefig("figures/lr3_const.png", dpi=180)
plt.close()

# Моделювання кривої BER для Eb/N0 = 0 .. 10 дБ
erfc_vec = np.vectorize(math.erfc)

def th_qpsk(e_db):
    g = 10.0 ** (np.asarray(e_db) / 10.0)
    return 0.5 * erfc_vec(np.sqrt(g))

def th_16qam(e_db):
    g = 10.0 ** (np.asarray(e_db) / 10.0)
    return (3.0 / 8.0) * erfc_vec(np.sqrt(0.4 * g))

def sim_ber(kind, ebn0_db, max_bits=20_000_000):
    k = 2 if kind == "QPSK" else 4
    g = 10.0 ** (ebn0_db / 10.0)
    # Es = 1 -> Eb = 1/k; відношення Eb/N0 = g => N0 = Eb / g = 1 / (k * g)
    # Для комплексного АБГШ: E[|n|^2] = N0, отже Re(n), Im(n) ~ N(0, N0/2) зі СКВ sigma = sqrt(N0/2)
    N0 = 1.0 / (k * g)
    sig = np.sqrt(N0 / 2.0)
    err, total_bits = 0, 0
    while err < 200 and total_bits < max_bits:
        b = rng.integers(0, 2, (500_000, k))
        x = qpsk_map(b) if kind == "QPSK" else qam16_map(b)
        y = x + sig * (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape))
        bh = qpsk_demap(y) if kind == "QPSK" else qam16_demap(y)
        err += int(np.sum(bh != b))
        total_bits += b.size
    return err / total_bits

ebs = list(range(0, 11))
ber_q = [sim_ber("QPSK", e) for e in ebs]
ber_16 = [sim_ber("16-QAM", e) for e in ebs]

print("\n=== ЧАСТИНА В: Імовірність бітової помилки BER(Eb/N0) ===")
print(f"{'Eb/N0, дБ':>9s} | {'QPSK експ.':>12s} | {'QPSK теор.':>12s} | {'16-QAM експ.':>13s} | {'16-QAM теор.':>13s}")
print("-" * 70)
for e, pq, p16 in zip(ebs, ber_q, ber_16):
    print(f"{e:9d} | {pq:12.2e} | {th_qpsk(e):12.2e} | {p16:13.2e} | {th_16qam(e):13.2e}")

fig_ber, ax_ber = plt.subplots(figsize=(7.5, 4.8))
xs = np.linspace(0, 10, 200)
ax_ber.semilogy(xs, th_qpsk(xs), "k-", lw=1.6, label="теорія QPSK/BPSK ½·erfc(√(Eb/N₀))")
ax_ber.semilogy(xs, th_16qam(xs), "b-", lw=1.6, label="теорія 16-QAM (Грей, ≈ 3/8·erfc(√(0,4·Eb/N₀)))")
ax_ber.semilogy(ebs, ber_q, "ro", mfc="none", ms=6.5, lw=1.5, label="модель QPSK")
ax_ber.semilogy(ebs, ber_16, "bs", mfc="none", ms=6.5, lw=1.5, label="модель 16-QAM")
ax_ber.set_ylim(1e-6, 1)
ax_ber.set_xlim(0, 10)
ax_ber.set_xlabel("Eb/N₀, дБ")
ax_ber.set_ylabel("імовірність помилки на біт")
ax_ber.grid(True, which="both", alpha=0.35)
ax_ber.legend(fontsize=8.5, loc="lower left")
plt.tight_layout()
plt.savefig("figures/lr3_ber.png", dpi=180)
plt.close()

print("\nУсі 5 графіків збережено у figures/: lr3_blocks.png, lr3_am.png, lr3_fm.png, lr3_const.png, lr3_ber.png")