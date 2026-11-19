import os
import time
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

# 1. Власна реалізація ДПФ за означенням через матрицю повертаючих множників
def my_dft(x):
    x = np.asarray(x, dtype=np.complex128)
    N = x.shape[0]
    n = np.arange(N)
    # Взяття показника за модулем N усуває накопичення похибки аргументу
    W = np.exp(-2j * np.pi * (np.outer(n, n) % N) / N)
    return W @ x

# 2. Бітреверсна перестановка та власний ШПФ (основа 2, проріджування за часом)
def bit_reverse_indices(N):
    bits = int(np.log2(N))
    idx = np.arange(N)
    rev = np.zeros(N, dtype=int)
    for i in range(bits):
        rev = (rev << 1) | ((idx >> i) & 1)
    return rev

def my_fft_dit(x):
    x = np.asarray(x, dtype=np.complex128)
    N = x.shape[0]
    X = x[bit_reverse_indices(N)].copy()
    m = 2
    while m <= N:
        half_m = m // 2
        w_m = np.exp(-2j * np.pi * np.arange(half_m) / m)
        for k in range(0, N, m):
            u = X[k : k + half_m].copy()
            t = w_m * X[k + half_m : k + m]
            X[k : k + half_m] = u + t
            X[k + half_m : k + m] = u - t
        m *= 2
    return X

# 3. Перевірка точності обох реалізацій
rng = np.random.default_rng(42)
x_test = rng.standard_normal(512) + 1j * rng.standard_normal(512)
X_ref = np.fft.fft(x_test)

err_dft = np.max(np.abs(my_dft(x_test) - X_ref))
err_fft = np.max(np.abs(my_fft_dit(x_test) - X_ref))

print(f"Похибка ДПФ : {err_dft:.2e}  [{'OK' if err_dft < 1e-12 else 'FAIL'}]")
print(f"Похибка ШПФ : {err_fft:.2e}  [{'OK' if err_fft < 1e-12 else 'FAIL'}]\n")

# 4. Вимірювання часу виконання та складності для N = 128 .. 8192
N_list = [128, 256, 512, 1024, 2048, 4096, 8192]
t_dft_list, t_fft_list, t_np_list = [], [], []
ops_dft_list, ops_fft_list = [], []

print(f"{'N':>5s} | {'Множ. ДПФ':>10s} | {'Множ. ШПФ':>10s} | {'Теор. виграш':>12s} | {'Час ДПФ, мс':>11s} | {'Час ШПФ, мс':>11s} | {'Вимір. виграш':>13s} | {'NumPy, мс':>9s}")
print("-" * 102)

for N in N_list:
    sig = rng.standard_normal(N) + 1j * rng.standard_normal(N)
    repeats = 12 if N <= 2048 else 10
    
    _ = my_dft(sig)
    _ = my_fft_dit(sig)
    _ = np.fft.fft(sig)
    
    t0 = time.perf_counter()
    for _ in range(repeats):
        _ = my_dft(sig)
    t_dft = (time.perf_counter() - t0) / repeats * 1000.0
    
    t0 = time.perf_counter()
    for _ in range(repeats):
        _ = my_fft_dit(sig)
    t_fft = (time.perf_counter() - t0) / repeats * 1000.0
    
    t0 = time.perf_counter()
    for _ in range(repeats * 10):
        _ = np.fft.fft(sig)
    t_np = (time.perf_counter() - t0) / (repeats * 10) * 1000.0
    
    ops_dft = N ** 2
    ops_fft = int((N / 2) * np.log2(N))
    th_gain = ops_dft / ops_fft
    meas_gain = t_dft / t_fft
    
    t_dft_list.append(t_dft)
    t_fft_list.append(t_fft)
    t_np_list.append(t_np)
    ops_dft_list.append(ops_dft)
    ops_fft_list.append(ops_fft)
    
    print(f"{N:5d} | {ops_dft:10d} | {ops_fft:10d} | {th_gain:11.1f}x | {t_dft:11.3f} | {t_fft:11.3f} | {meas_gain:12.1f}x | {t_np:9.4f}")

# Графік 1: Кількість множень та виміряний час у логарифмічних координатах
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
ax1.loglog(N_list, ops_dft_list, 'o-', lw=1.8, label='ДПФ, N² множень')
ax1.loglog(N_list, ops_fft_list, 's-', lw=1.8, label='ШПФ, (N/2)·log₂N множень')
ax1.set_xlabel('Розмір перетворення N')
ax1.set_ylabel('Кількість комплексних множень')
ax1.set_title('Теоретична обчислювальна складність')
ax1.grid(True, which='both', ls='--', alpha=0.5)
ax1.legend()

ax2.loglog(N_list, t_dft_list, 'o-', lw=1.8, label='Власне ДПФ')
ax2.loglog(N_list, t_fft_list, 's-', lw=1.8, label='Власне ШПФ (ПЗЧ)')
ax2.loglog(N_list, t_np_list, '^-', lw=1.8, label='Бібліотечне ШПФ (NumPy)')
ax2.set_xlabel('Розмір перетворення N')
ax2.set_ylabel('Час виконання, мс')
ax2.set_title('Виміряний час виконання')
ax2.grid(True, which='both', ls='--', alpha=0.5)
ax2.legend()

plt.tight_layout()
plt.savefig("figures/lr2_complexity.png", dpi=200)
plt.close()

# 5. Дослідження роздільної здатності та доповнення нулями (Варіант 9: f1=1225, f2=1260, Δ=35 Гц)
Fs = 10000.0
f1, delta_f = 1225.0, 35.0
f2 = f1 + delta_f  # 1260 Гц

print(f"\n=== Дослідження роздільної здатності (Варіант 9: f1={f1:.0f} Гц, f2={f2:.0f} Гц, Δ={delta_f:.0f} Гц) ===")

def get_dip_db(mag_db, freqs, f_low, f_high):
    mask = (freqs >= f_low - 15) & (freqs <= f_high + 15)
    f_sub, m_sub = freqs[mask], mag_db[mask]
    idx_mid = np.argmin(np.abs(f_sub - 0.5 * (f_low + f_high)))
    left_peak = np.max(m_sub[:idx_mid]) if idx_mid > 0 else m_sub[0]
    right_peak = np.max(m_sub[idx_mid+1:]) if idx_mid + 1 < len(m_sub) else m_sub[-1]
    valley = m_sub[idx_mid]
    dip = max(0.0, min(left_peak, right_peak) - valley)
    return dip >= 6.0, dip

fig, axes = plt.subplots(2, 2, figsize=(10.5, 7))
plot_Ns = [256, 512, 1024]

for idx, N_res in enumerate([256, 512, 1024, 2048, 4096, 8192]):
    t_r = np.arange(N_res) / Fs
    sig_r = np.cos(2 * np.pi * f1 * t_r) + np.cos(2 * np.pi * f2 * t_r)
    spec = np.abs(my_fft_dit(sig_r))
    spec = spec / np.max(spec)
    freqs = np.fft.fftfreq(N_res, 1.0 / Fs)
    pos = freqs >= 0
    freqs_p = freqs[pos]
    mag_db = 20 * np.log10(np.maximum(spec[pos], 1e-12))
    
    resolved, dip = get_dip_db(mag_db, freqs_p, f1, f2)
    status = "РОЗДІЛЯЮТЬСЯ" if resolved else "ні"
    print(f"N = {N_res:4d} | Δf = {Fs/N_res:6.2f} Гц | глибина провалу = {dip:5.2f} дБ | розділення (>=6 дБ): {status}")
    
    if N_res in plot_Ns:
        ax = axes.flat[idx]
        zoom = (freqs_p >= 1100) & (freqs_p <= 1380)
        ax.plot(freqs_p[zoom], mag_db[zoom], lw=1.6)
        ax.set_title(f"N={N_res}, Δf={Fs/N_res:.2f} Гц")
        ax.set_xlabel("Частота, Гц")
        ax.set_ylabel("Амплітуда, дБ")
        ax.set_ylim(-40, 2)
        ax.grid(True, alpha=0.35)

# Доповнення нулями найкоротшої вибірки N = 256 до 8192
N_short = 256
t_short = np.arange(N_short) / Fs
sig_short = np.cos(2 * np.pi * f1 * t_short) + np.cos(2 * np.pi * f2 * t_short)
sig_zp = np.zeros(8192)
sig_zp[:N_short] = sig_short

spec_zp = np.abs(my_fft_dit(sig_zp))
spec_zp = spec_zp / np.max(spec_zp)
freqs_zp = np.fft.fftfreq(8192, 1.0 / Fs)
pos_zp = freqs_zp >= 0
mag_zp_db = 20 * np.log10(np.maximum(spec_zp[pos_zp], 1e-12))
res_zp, dip_zp = get_dip_db(mag_zp_db, freqs_zp[pos_zp], f1, f2)
print(f"N = {N_short} + нулі до 8192 | Δf_еф = {Fs/N_short:.2f} Гц | провал = {dip_zp:.2f} дБ -> {'РОЗДІЛЯЮТЬСЯ' if res_zp else 'зливаються (не допомогло)'}")

ax_zp = axes.flat[3]
zoom_zp = (freqs_zp[pos_zp] >= 1100) & (freqs_zp[pos_zp] <= 1380)
ax_zp.plot(freqs_zp[pos_zp][zoom_zp], mag_zp_db[zoom_zp], lw=1.6)
ax_zp.set_title(f"N=256 + нулі до 8192, Δf={Fs/N_short:.2f} Гц")
ax_zp.set_xlabel("Частота, Гц")
ax_zp.set_ylabel("Амплітуда, дБ")
ax_zp.set_ylim(-40, 2)
ax_zp.grid(True, alpha=0.35)

plt.tight_layout()
plt.savefig("figures/lr2_resolution.png", dpi=200)
plt.close()