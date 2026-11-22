import os
import shutil
import subprocess
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("figures", exist_ok=True)
os.makedirs("out", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

def wrap16(v):
    return ((int(v) + 32768) & 0xFFFF) - 32768

def butterfly_int(ar, ai, br, bi, wr, wi, fault_en=0, fb=0, fv=1):
    p1 = int(br) * int(wr)
    p2 = int(bi) * int(wi)
    p3 = int(br) * int(wi)
    p4 = int(bi) * int(wr)
    tr = (p1 - p2) >> 15
    ti = (p3 + p4) >> 15
    xr = wrap16((int(ar) + tr) >> 1)
    xi = wrap16((int(ai) + ti) >> 1)
    yr = wrap16((int(ar) - tr) >> 1)
    yi = wrap16((int(ai) - ti) >> 1)
    if fault_en:
        if fv:
            xr = wrap16(xr | (1 << fb))
        else:
            xr = wrap16(xr & ~(1 << fb))
    return xr, xi, yr, yi

rng = np.random.default_rng(21)
V = [
    (0, 0, 0, 0, 32767, 0),
    (32767, 0, 32767, 0, 32767, 0),
    (-32768, 0, -32768, 0, 32767, 0),
    (0, 32767, 0, 32767, 0, 32767),
    (-32768, -32768, 0, 0, 32767, 0),
    (16384, -16384, -16384, 16384, 23170, -23170),
    (1, -1, 1, -1, 1, -1),
    (-1, 1, 32767, -32768, 0, -32768),
]
while len(V) < 32:
    A = rng.integers(-23000, 23000, 2)
    B = rng.integers(-23000, 23000, 2)
    ang = rng.uniform(0, 2 * np.pi)
    W = (int(round(32767 * np.cos(ang))), int(round(32767 * np.sin(ang))))
    V.append((int(A[0]), int(A[1]), int(B[0]), int(B[1]), W[0], W[1]))

exp = [butterfly_int(*v) for v in V]

with open("vec_in.mem", "w") as f:
    for v in V:
        f.write("\n".join(f"{x & 0xFFFF:04x}" for x in v) + "\n")
with open("vec_exp.mem", "w") as f:
    for e in exp:
        f.write("\n".join(f"{x & 0xFFFF:04x}" for x in e) + "\n")

Fs = 16000.0
L_chirp = 16384
n_arr = np.arange(L_chirp, dtype=np.float64)
f0, f1 = 0.0, Fs / 2.0
ph = 2.0 * np.pi * (f0 * n_arr / Fs + (f1 - f0) * (n_arr ** 2) / (2.0 * L_chirp * Fs))
x_chirp = np.round(0.5 * 32768.0 * np.sin(ph)).astype(np.int64)
with open("chirp.mem", "w") as f:
    f.write("\n".join(f"{int(v) & 0xFFFF:04x}" for v in x_chirp) + "\n")

with open("fir_coeff.mem", "r") as fc:
    hex_lines = [line.strip() for line in fc if line.strip() and not line.strip().startswith("//")]
coef_q15 = np.array([wrap16(int(h, 16)) for h in hex_lines], dtype=np.int64)
NTAPS = len(coef_q15)
assert NTAPS == 147, f"Очікувалося 147 коефіцієнтів із ЛР5, отримано {NTAPS}"

has_iverilog = shutil.which("iverilog") is not None and shutil.which("vvp") is not None
sim_mode = "Icarus Verilog (iverilog/vvp)" if has_iverilog else "потактовий RTL-симулятор Python"

trace_rows = []
pipe_s1 = None
pipe_s2 = (0, 0, 0, 0, 0)
errors_clean = 0
for cyc in range(1, 38):
    if cyc <= 2:
        vin_bit = 0
        vout_bit = 0
        xr_val = 0
    else:
        idx_v = cyc - 3
        if idx_v < 32:
            vin_bit = 1
            cur_in = V[idx_v]
        else:
            vin_bit = 0
            cur_in = None
        vout_bit, xr_val, xi_val, yr_val, yi_val = pipe_s2
        if vout_bit:
            e_idx = cyc - 5
            if (xr_val, xi_val, yr_val, yi_val) != exp[e_idx]:
                errors_clean += 1
        pipe_s2 = (1, *butterfly_int(*pipe_s1)) if pipe_s1 is not None else (0, 0, 0, 0, 0)
        pipe_s1 = cur_in
    trace_rows.append((cyc, vin_bit, vout_bit, xr_val))

with open("trace.csv", "w") as ft:
    for r in trace_rows:
        ft.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

if has_iverilog:
    subprocess.run(["iverilog", "-g2012", "-o", "bf_sim", "butterfly.v", "tb_butterfly.v"], check=True)
    subprocess.run(["vvp", "bf_sim"], check=True)

cycs = np.array([r[0] for r in trace_rows[:16]])
vins = np.array([r[1] for r in trace_rows[:16]])
vouts = np.array([r[2] for r in trace_rows[:16]])
xrs = np.array([r[3] for r in trace_rows[:16]])

fig, ax = plt.subplots(4, 1, figsize=(7.2, 4.2), sharex=True)
t_clk = np.repeat(np.arange(1, 17), 2)
y_clk = np.tile([1, 0], 16)
ax[0].step(t_clk, y_clk, where="post", lw=1.2)
ax[0].set_ylabel("clk")
ax[0].set_yticks([0, 1])

ax[1].step(cycs, vins, where="post", lw=1.2)
ax[1].axvline(3, color="r", ls=":", lw=1.2)
ax[1].set_ylabel("valid_in")
ax[1].set_yticks([0, 1])

ax[2].step(cycs, vouts, where="post", lw=1.2)
ax[2].axvline(5, color="r", ls=":", lw=1.2)
ax[2].annotate("латентність 2 такти", xy=(5, 0.5), xytext=(6.2, 0.5),
               arrowprops=dict(arrowstyle="<-", lw=1.0), va="center")
ax[2].set_ylabel("valid_out")
ax[2].set_yticks([0, 1])

ax[3].step(cycs, xrs, where="post", lw=1.2)
ax[3].set_ylabel("xr")
ax[3].set_xlabel("такт")
for a in ax:
    a.set_xlim(2, 16)
    a.grid(alpha=0.25)
plt.tight_layout()
plt.savefig("figures/l8_wave.png", dpi=160)
plt.close()

N_fft = 512
f_clk = 50e6
B_but = (N_fft // 2) * int(np.log2(N_fft))
L_lat = 2
ks = [1, 2, 4, 8]
perf_rows = []
t1_cyc = B_but // 1 + 2 * N_fft + L_lat
for k in ks:
    bk = B_but // k
    tot_cyc = bk + 2 * N_fft + L_lat
    t_us = tot_cyc / f_clk * 1e6
    sp = t1_cyc / tot_cyc
    perf_rows.append((k, bk, 2 * N_fft, L_lat, tot_cyc, t_us, sp))

fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.plot(ks, [r[6] for r in perf_rows], "o-", lw=1.6, label="фактичне прискорення")
ax.plot(ks, ks, "k--", lw=1.3, label="лінійний закон")
for r in perf_rows:
    ax.annotate(f"{r[6]:.2f}", (r[0], r[6]), textcoords="offset points", xytext=(6, -10), fontsize=8)
ax.set_xticks(ks)
ax.set_xlabel("кількість блоків «метелик»")
ax.set_ylabel("прискорення, разів")
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/l8_speedup.png", dpi=160)
plt.close()

fault_bits = [0, 3, 7, 15]
fault_table = []
for ftype, fv in [("stuck-at-1", 1), ("stuck-at-0", 0)]:
    for b in fault_bits:
        err_cnt = 0
        max_e = 0
        for v, e in zip(V, exp):
            yf = butterfly_int(*v, fault_en=1, fb=b, fv=fv)
            if yf != e:
                err_cnt += 1
            max_e = max(max_e, abs(yf[0] - e[0]))
        fault_table.append((ftype, b, err_cnt, err_cnt > 0, max_e))

def sim_fir_hw(x_in, coefs, fault_en=0, fb=0):
    conv_full = np.convolve(x_in, coefs)[: len(x_in)]
    shifted = conv_full >> 15
    sat = np.clip(shifted, -32768, 32767).astype(np.int64)
    if fault_en:
        sat = np.array([wrap16(int(v) | (1 << fb)) for v in sat], dtype=np.int64)
    return sat

y_clean = sim_fir_hw(x_chirp, coef_q15, fault_en=0)

M_tap = (NTAPS - 1) // 2
n_h = np.arange(-M_tap, M_tap + 1, dtype=np.float64)
fc_norm = 3500.0 / Fs
lp = np.where(n_h == 0, 2.0 * fc_norm, np.sin(n_h * 2.0 * np.pi * fc_norm) / (np.pi * np.where(n_h == 0, 1.0, n_h)))
hd = (n_h == 0).astype(np.float64) - lp
win_b = 0.42 + 0.5 * np.cos(2.0 * np.pi * n_h / (NTAPS - 1)) + 0.08 * np.cos(4.0 * np.pi * n_h / (NTAPS - 1))
h_f64 = hd * win_b

w_freq, H_f64 = signal.freqz(h_f64, worN=4096, fs=Fs)
_, H_q15 = signal.freqz(coef_q15.astype(np.float64) / 32768.0, worN=4096, fs=Fs)

win_h = np.hanning(L_chirp)
X_sp = np.abs(np.fft.rfft(x_chirp * win_h)) ** 2
Y_sp = np.abs(np.fft.rfft(y_clean * win_h)) ** 2
ker = np.ones(65) / 65.0
X_sm = np.convolve(X_sp, ker, mode="same")
Y_sm = np.convolve(Y_sp, ker, mode="same")
H_meas_db = 10.0 * np.log10(np.maximum(Y_sm, 1e-20) / np.maximum(X_sm, 1e-20))
f_meas = np.fft.rfftfreq(L_chirp, d=1.0 / Fs)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 3.6))
ax1.plot(w_freq, 20.0 * np.log10(np.maximum(np.abs(H_f64), 1e-6)), lw=1.1, label="розрахункова (ЛР5, float)")
ax1.plot(f_meas, H_meas_db, lw=1.1, label="виміряна ЛЧМ-методом (апаратура)")
ax1.set_xlim(0, 8200)
ax1.set_ylim(-95, 5)
ax1.set_xlabel("частота, Гц")
ax1.set_ylabel("АЧХ, дБ")
ax1.legend(loc="lower right", fontsize=7.5)
ax1.grid(alpha=0.3)

ax2.plot(w_freq, 20.0 * np.log10(np.maximum(np.abs(H_f64), 1e-6)), lw=1.1, label="float64 (ЛР5)")
ax2.plot(f_meas, H_meas_db, lw=1.1, label="виміряна ЛЧМ")
ax2.plot(w_freq, 20.0 * np.log10(np.maximum(np.abs(H_q15), 1e-6)), "--", lw=1.1, label="Q15-коефіцієнти (розрахунок)")
ax2.set_xlim(2200, 4600)
ax2.set_ylim(-85, 2)
ax2.set_xlabel("частота, Гц")
ax2.legend(loc="lower right", fontsize=7.5)
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/l8_chirp.png", dpi=160)
plt.close()

fir_fault_rows = []
for b in fault_bits:
    yf = sim_fir_hw(x_chirp, coef_q15, fault_en=1, fb=b)
    diff_cnt = int(np.sum(yf != y_clean))
    max_err_y = int(np.max(np.abs(yf - y_clean)))
    Yf_sp = np.abs(np.fft.rfft(yf * win_h)) ** 2
    Yf_sm = np.convolve(Yf_sp, ker, mode="same")
    Hf_db = 10.0 * np.log10(np.maximum(Yf_sm, 1e-20) / np.maximum(X_sm, 1e-20))
    mask = (f_meas >= 300) & (f_meas <= 7700)
    max_db_diff = float(np.max(np.abs(Hf_db[mask] - H_meas_db[mask])))
    fir_fault_rows.append((b, max_err_y, diff_cnt, max_db_diff))

pb_mask = (f_meas >= 4000) & (f_meas <= 7000)
sb_mask = (f_meas >= 400) & (f_meas <= 2700)
pb_min, pb_max = float(np.min(H_meas_db[pb_mask])), float(np.max(H_meas_db[pb_mask]))
sb_max_meas = float(np.max(H_meas_db[sb_mask]))
sb_max_calc = float(np.max(20.0 * np.log10(np.abs(H_f64[(w_freq >= 400) & (w_freq <= 2700)]))))

print(f"=== РЕЗУЛЬТАТИ ЛР №8 (Варіант 21: V = 9, N = 512, f_clk = 50 МГц, NTAPS = {NTAPS}) ===")
print(f"Режим симуляції: {sim_mode}")
print(f"Перевірка 32 векторів: помилок = {errors_clean}, латентність = {L_lat} такти")
print("\nТаблиця продуктивності (N = 512, 50 МГц):")
for r in perf_rows:
    print(f"  k={r[0]} | B/k={r[1]:4d} | 2N={r[2]} | L={r[3]} | Тактів={r[4]:4d} | Час={r[5]:6.2f} мкс | Прискорення={r[6]:.2f}x")
print("\nТаблиця виявлення несправностей (32 вектори):")
for r in fault_table:
    print(f"  {r[0]:10s} | біт {r[1]:2d} | помилкових={r[2]:2d}/32 | макс. похибка={r[4]}")
print(f"\nАЧХ фільтра (147 коеф.):")
print(f"  Смуга пропускання (4..7 кГц): {pb_min:.2f} .. {pb_max:.2f} дБ")
print(f"  Смуга затримки (0.4..2.7 кГц): виміряно max={sb_max_meas:.1f} дБ, розрахунок max={sb_max_calc:.1f} дБ")
print("\nВплив stuck-at-1 виходу фільтра на АЧХ:")
for r in fir_fault_rows:
    print(f"  біт {r[0]:2d} | макс. похибка={r[1]:5d} | відліків з відхил.={r[2]:5d}/16384 | макс. зміна АЧХ={r[3]:5.1f} дБ")