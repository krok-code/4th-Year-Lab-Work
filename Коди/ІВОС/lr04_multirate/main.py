import os
import math
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)

# Вихідні дані для варіанта 21 (V = 9)
Fs = 48000.0
M = 8
L = 4
f1 = 1500.0
f2 = 3500.0
A1, A2 = 1.0, 0.5
Nn = 4096
NT = 129

n = np.arange(Nn)
x = A1 * np.cos(2 * np.pi * f1 * n / Fs) + A2 * np.cos(2 * np.pi * f2 * n / Fs)

def design_fir(numtaps, cutoff_hz, fs_hz, window_type="hamming", beta=5.65):
    """Проєктування лінійно-фазового КІХ-ФНЧ (аналог scipy.signal.firwin)."""
    fc_norm = cutoff_hz / (fs_hz / 2.0)
    m_idx = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = fc_norm * np.sinc(fc_norm * m_idx)
    if window_type == "hamming":
        w = np.hamming(numtaps)
    elif window_type == "kaiser":
        w = np.kaiser(numtaps, beta)
    else:
        w = np.ones(numtaps)
    h = h * w
    return h / np.sum(h)

def freq_resp_db(h, freq_hz, fs_hz):
    k = np.arange(len(h))
    H = np.sum(h * np.exp(-1j * 2 * np.pi * freq_hz * k / fs_hz))
    return 20.0 * np.log10(np.abs(H) + 1e-20)

def spec(y, fs_hz, pad=1 << 16, skip=0):
    y_seg = y[skip:]
    w = np.hanning(len(y_seg))
    X = np.abs(np.fft.rfft(y_seg * w, pad)) / (np.sum(w) / 2.0)
    return np.fft.rfftfreq(pad, 1.0 / fs_hz), X

def find_peak(f, X, f0, bw=60.0):
    mask = np.abs(f - f0) < bw
    idx = np.argmax(X[mask])
    return f[mask][idx], X[mask][idx]

# ==============================================================================
# 1. ДЕЦИМАЦІЯ БЕЗ ФІЛЬТРА ТА З ФІЛЬТРОМ (M = 8)
# ==============================================================================
Fo = Fs / M  # 6000 Гц
f_alias_pred = abs(f2 - Fo)  # |3500 - 6000| = 2500 Гц
y0 = x[::M]

# Фільтр А: зріз Fs / (2M) = 3000 Гц (за методичкою), вікно Хеммінга
hA = design_fir(NT, Fs / (2 * M), Fs, window_type="hamming")
# Фільтр Б: зріз у середині смуги переходу (2200..3500 -> 2850 Гц), вікно Кайзера (beta = 5.65)
hB = design_fir(NT, 2850.0, Fs, window_type="kaiser", beta=5.65)

yA = np.convolve(x, hA)[:Nn][::M]
yB = np.convolve(x, hB)[:Nn][::M]

sk = NT // M + 1
fr, X0 = spec(y0, Fo, skip=sk)
_, XA = spec(yA, Fo, skip=sk)
_, XB = spec(yB, Fo, skip=sk)

fp0, a0 = find_peak(fr, X0, f_alias_pred)
fpA, aA = find_peak(fr, XA, f_alias_pred)
fpB, aB = find_peak(fr, XB, f_alias_pred)
_, a1B = find_peak(fr, XB, f1)

attA = 20.0 * np.log10(aA / a0)
attB = 20.0 * np.log10(aB / a0)
respA_3500 = freq_resp_db(hA, f2, Fs)
respB_3500 = freq_resp_db(hB, f2, Fs)
lossB_1500 = -freq_resp_db(hB, f1, Fs)

print("=== 1. ДЕЦИМАЦІЯ (Варіант 21: V = 9, M = 8, L = 4) ===")
print(f"Очікувана паразитна частота: {f_alias_pred:.1f} Гц | Виміряно без фільтра: {fp0:.1f} Гц (рівень {20*np.log10(a0):.2f} дБ)")
print(f"Фільтр А (зріз 3000 Гц, Хеммінг): АЧХ(3500 Гц) = {respA_3500:.1f} дБ | Придушення у спектрі = {attA:.1f} дБ")
print(f"Фільтр Б (зріз 2850 Гц, Кайзер) : АЧХ(3500 Гц) = {respB_3500:.1f} дБ | Придушення у спектрі = {attB:.1f} дБ (втрати на f1 = {lossB_1500:.4f} дБ)")

ff, Xin = spec(x, Fs)
fig1, ax1 = plt.subplots(4, 1, figsize=(7.5, 9.2))
ax1[0].plot(ff / 1e3, 20 * np.log10(Xin + 1e-12), lw=1.0)
ax1[0].set_title("Вхідний сигнал (F_s = 48 кГц: f₁ = 1,5 кГц, f₂ = 3,5 кГц)", fontsize=9.5)
ax1[0].set_xlim(0, 24)

ax1[1].plot(fr / 1e3, 20 * np.log10(X0 + 1e-12), lw=1.0)
ax1[1].axvline(f_alias_pred / 1e3, color="r", ls=":", lw=1.2)
ax1[1].set_title("Децимація M = 8 без фільтра (F = 6,0 кГц): паразитна складова 2,5 кГц", fontsize=9.5)

ax1[2].plot(fr / 1e3, 20 * np.log10(XA + 1e-12), lw=1.0)
ax1[2].set_title("З ФНЧ, зріз 3000 Гц (Хеммінг, 129 коеф.)", fontsize=9.5)

ax1[3].plot(fr / 1e3, 20 * np.log10(XB + 1e-12), lw=1.0)
ax1[3].set_title("З ФНЧ Кайзера, зріз 2850 Гц (129 коеф.)", fontsize=9.5)

for a in ax1:
    a.set_ylim(-120, 5)
    a.set_ylabel("рівень, дБ")
    a.set_xlabel("частота, кГц")
    a.grid(True, alpha=0.35)
for a in ax1[1:]:
    a.set_xlim(0, Fo / 2e3)

plt.tight_layout()
plt.savefig("figures/lr4_dec.png", dpi=180)
plt.close()

# ==============================================================================
# 2. ІНТЕРПОЛЯЦІЯ ТА СПЕКТРАЛЬНІ ОБРАЗИ (L = 4)
# ==============================================================================
u = np.zeros(len(yB) * L)
u[::L] = yB
Fi = Fo * L  # 24 000 Гц
hI = L * design_fir(NT, 3750.0, Fi, window_type="kaiser", beta=5.65)
v = np.convolve(u, hI)[:len(u)]

fy, Xy = spec(yB, Fo, skip=60)
fo, Xu = spec(u, Fi, skip=100)
_, Xv = spec(v, Fi, skip=100)

lev_y = find_peak(fy, Xy, f1)[1]
lev_u = find_peak(fo, Xu, f1)[1]
lev_v = find_peak(fo, Xv, f1)[1]
# Найближчий спектральний образ: Fo - f1 = 6000 - 1500 = 4500 Гц
f_img = Fo - f1
img_u_db = 20.0 * np.log10(find_peak(fo, Xu, f_img)[1])
img_v_db = 20.0 * np.log10(find_peak(fo, Xv, f_img)[1])

print("\n=== 2. ІНТЕРПОЛЯЦІЯ (L = 4, Fi = 24 кГц) ===")
print(f"Амплітуда f1=1500 Гц: до вставки = {lev_y:.3f}, після вставки нулів = {lev_u:.3f}, після ФНЧ (×L) = {lev_v:.3f}")
print(f"Найближчий образ на {f_img:.0f} Гц: після вставки = {img_u_db:.1f} дБ, після ФНЧ = {img_v_db:.1f} дБ")

fig2, ax2 = plt.subplots(3, 1, figsize=(7.5, 7.2))
ax2[0].plot(fy / 1e3, 20 * np.log10(Xy + 1e-12), lw=1.0)
ax2[0].set_title("До вставки нулів (F = 6,0 кГц)", fontsize=9.5)
ax2[0].set_xlim(0, Fi / 2e3)

ax2[1].plot(fo / 1e3, 20 * np.log10(Xu + 1e-12), lw=1.0)
ax2[1].set_title("Після вставки L − 1 = 3 нулів (F = 24,0 кГц): спектральні образи", fontsize=9.5)
ax2[1].set_xlim(0, Fi / 2e3)

ax2[2].plot(fo / 1e3, 20 * np.log10(Xv + 1e-12), lw=1.0)
ax2[2].set_title("Після згладжувального ФНЧ з підсиленням L = 4", fontsize=9.5)
ax2[2].set_xlim(0, Fi / 2e3)

for a in ax2:
    a.set_ylim(-120, 10)
    a.set_ylabel("рівень, дБ")
    a.set_xlabel("частота, кГц")
    a.grid(True, alpha=0.35)

plt.tight_layout()
plt.savefig("figures/lr4_int.png", dpi=180)
plt.close()

# ==============================================================================
# 3. ПЕРЕТВОРЕННЯ З НЕЦІЛИМ КРОКОМ 44,1 -> 48 кГц
# ==============================================================================
g = math.gcd(44100, 48000)
Lr, Mr = 48000 // g, 44100 // g
f_int = 44100 * Lr
mults_per_sec = NT * f_int
print("\n=== 3. ПЕРЕТВОРЕННЯ 44,1 -> 48 кГц ===")
print(f"НСД = {g} -> L = {Lr}, M = {Mr}, проміжна частота = {f_int/1e6:.3f} МГц, множень/с = {mults_per_sec/1e6:.1f} млн")

# ==============================================================================
# 4. ПОЛІФАЗНА ДЕЦИМАЦІЯ (M = 8, NT = 129)
# ==============================================================================
def direct_decimate(x_in, h, M_val):
    return np.convolve(x_in, h)[:len(x_in)][::M_val]

def polyphase_decimate(x_in, h, M_val):
    nout = int(np.ceil(len(x_in) / M_val))
    y_out = np.zeros(nout)
    mults = 0
    for p in range(M_val):
        e_p = h[p::M_val]  # e_p(k) = h(k*M + p)
        x_p = np.zeros(nout)
        idx = np.arange(nout) * M_val - p
        valid = idx >= 0
        x_p[valid] = x_in[idx[valid]]  # гілка p обробляє x(m*M - p)
        y_out += np.convolve(x_p, e_p)[:nout]
        mults += len(e_p) * nout
    return y_out, mults

yd = direct_decimate(x, hB, M)
yp, mults_poly = polyphase_decimate(x, hB, M)
mults_direct = Nn * NT
poly_err = np.max(np.abs(yd - yp))
branches_len = [len(hB[p::M]) for p in range(M)]

print("\n=== 4. ПОЛІФАЗНА ДЕЦИМАЦІЯ (M = 8) ===")
print(f"Довжини гілок: {branches_len} (сума = {sum(branches_len)})")
print(f"Пряма реалізація: {mults_direct} множень | Поліфазна ({len(yp)} вих. відліків): {mults_poly} множень")
print(f"Виграш: {mults_direct / mults_poly:.2f}x | Макс. розбіжність: {poly_err:.2e}")

# ==============================================================================
# 5. БАГАТОКАСКАДНА ДЕЦИМАЦІЯ (M_Σ = 96)
# ==============================================================================
def kaiser_order(Mi, A=60.0, rel_bw=0.2):
    return (A - 7.95) / (14.36 * rel_bw / (2.0 * Mi))

def cascade_cost(stages):
    total_c = 0.0
    factor = 1.0
    lengths = []
    for Mi in stages:
        N_i = int(np.ceil(kaiser_order(Mi))) | 1
        total_c += N_i / factor
        lengths.append(N_i)
        factor *= Mi
    return total_c, lengths

schemes_96 = [[96], [8, 12], [4, 4, 6], [2, 6, 8], [2, 2, 2, 2, 2, 3]]
base_c, _ = cascade_cost([96])

print("\n=== 5. БАГАТОКАСКАДНА ДЕЦИМАЦІЯ (M_Σ = 96) ===")
print(f"{'Схема':<22s} | {'Довжини фільтрів N_i':<26s} | {'Множень/відлік':>15s} | {'Виграш':>8s}")
print("-" * 80)
labels, costs, gains = [], [], []
for sc in schemes_96:
    c_val, lens = cascade_cost(sc)
    g_val = base_c / c_val
    lbl = " × ".join(map(str, sc)) if len(sc) > 1 else str(sc[0])
    labels.append(lbl)
    costs.append(c_val)
    gains.append(g_val)
    print(f"{lbl:<22s} | {str(lens):<26s} | {c_val:15.1f} | {g_val:7.1f}x")

fig3, ax3 = plt.subplots(figsize=(6.8, 3.8))
ax3.bar(range(len(schemes_96)), costs, color="steelblue")
ax3.set_xticks(range(len(schemes_96)))
ax3.set_xticklabels(labels, fontsize=8.5)
ax3.set_yscale("log")
ax3.set_ylabel("множень на вхідний відлік")
ax3.set_xlabel("схема каскадів (M = 96)")
for i, (c_v, g_v) in enumerate(zip(costs, gains)):
    ax3.text(i, c_v * 1.12, f"{c_v:.0f}\n({g_v:.1f}×)".replace(".", ","), ha="center", fontsize=8)
ax3.set_ylim(50, 6500)
ax3.grid(True, which="both", axis="y", alpha=0.35)
plt.tight_layout()
plt.savefig("figures/lr4_casc.png", dpi=180)
plt.close()

print("\nУсі 3 графіки збережено у figures/: lr4_dec.png, lr4_int.png, lr4_casc.png")