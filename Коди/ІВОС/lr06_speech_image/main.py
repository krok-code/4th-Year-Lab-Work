import os
import json
import wave
import numpy as np
from scipy import signal, fft as sfft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("figures", exist_ok=True)
os.makedirs("out", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

R = {}
Fs = 16000
words = ["північ", "південь", "захід", "схід", "центр"]

def read_wav_mono(path):
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if sw == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(float) / 32768.0
    elif sw == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(float) - 128.0) / 128.0
    else:
        x = np.frombuffer(raw, dtype=np.int32).astype(float) / 2147483648.0
    if nch > 1:
        x = x.reshape(-1, nch).mean(axis=1)
    return sr, x

def load(w, tag):
    sr, x = read_wav_mono(f"wav/{w}_{tag}.wav")
    if sr != Fs:
        x = signal.resample_poly(x, Fs, sr)
    # Обрізання тиші: поріг 2% від пікового RMS по кадрах 10 мс
    fr = 160
    e = np.array([np.sqrt(np.mean(x[i : i + fr] ** 2)) for i in range(0, len(x) - fr, fr)])
    idx = np.where(e > e.max() * 0.02)[0]
    a = max(idx[0] * fr - fr, 0)
    b = min((idx[-1] + 2) * fr, len(x))
    x = x[a:b]
    return x / np.max(np.abs(x)) * 0.9

data = {(w, t): load(w, t) for w in words for t in ["ref1", "ref2", "test"]}
for (w, t), x in data.items():
    with wave.open(f"wav/{w}_{t}_16k.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(Fs)
        wf.writeframes((x * 32767).astype(np.int16).tobytes())

def hz2mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)

def mel2hz(m):
    return 700.0 * (10.0 ** (m / 2595.0) - 1.0)

nfft = 512
nm = 26
mp = np.linspace(hz2mel(0), hz2mel(Fs / 2), nm + 2)
hp = mel2hz(mp)
bins = np.floor((nfft + 1) * hp / Fs).astype(int)
FB = np.zeros((nm, nfft // 2 + 1))
for m in range(1, nm + 1):
    l, c, r = bins[m - 1], bins[m], bins[m + 1]
    for k in range(l, c):
        FB[m - 1, k] = (k - l) / max(c - l, 1)
    for k in range(c, r):
        FB[m - 1, k] = (r - k) / max(r - c, 1)

def mfcc(x, cmn=True):
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    fl, hop = 400, 160
    nf = 1 + (len(x) - fl) // hop
    fr = np.stack([x[i * hop : i * hop + fl] for i in range(nf)]) * np.hamming(fl)
    P = np.abs(np.fft.rfft(fr, nfft)) ** 2 / fl
    E = np.log(P @ FB.T + 1e-10)
    C = sfft.dct(E, type=2, norm="ortho", axis=1)[:, :13]
    if cmn:
        C = C - C.mean(0)
    return C

def dtw(A, B, path=False):
    n, m = len(A), len(B)
    d = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(
                D[i - 1, j] + d[i - 1, j - 1],
                D[i, j - 1] + d[i - 1, j - 1],
                D[i - 1, j - 1] + 2.0 * d[i - 1, j - 1],
            )
    L = n + m
    cost = D[n, m] / L
    if not path:
        return cost
    i, j = n, m
    p = [(i - 1, j - 1)]
    while i > 1 or j > 1:
        c = [(D[i - 1, j - 1], i - 1, j - 1), (D[i - 1, j], i - 1, j), (D[i, j - 1], i, j - 1)]
        _, i, j = min(c)
        p.append((i - 1, j - 1))
    return cost, D[1:, 1:], p[::-1]

feat = {k: mfcc(x) for k, x in data.items()}
R["frames"] = {w: [len(feat[(w, t)]) for t in ["ref1", "ref2", "test"]] for w in words}
allT = [len(v) for v in feat.values()]
R["T_mean"] = float(np.mean(allT))
R["T_min"] = int(min(allT))
R["T_max"] = int(max(allT))

def classify(Ft, refs):
    dist = [min(dtw(Ft, refs[w][0]), dtw(Ft, refs[w][1])) for w in words]
    return np.array(dist)

refs = {w: [feat[(w, "ref1")], feat[(w, "ref2")]] for w in words}
Dm = np.array([classify(feat[(w, "test")], refs) for w in words])
pred = Dm.argmin(1)
R["dist"] = Dm.tolist()
R["pred"] = [words[i] for i in pred]
R["acc"] = float((pred == np.arange(5)).mean())
R["diag_min"] = [bool(Dm[i].argmin() == i) for i in range(5)]

# Без нормування на довжину шляху (для порівняння)
def dtw_raw(A, B):
    n, m = len(A), len(B)
    d = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = d[i - 1, j - 1] + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return D[n, m]

Draw = np.array([[min(dtw_raw(feat[(w, "test")], refs[v][0]), dtw_raw(feat[(w, "test")], refs[v][1])) for v in words] for w in words])
R["acc_raw"] = float((Draw.argmin(1) == np.arange(5)).mean())

# Дослідження стійкості до шуму
rng = np.random.default_rng(9)
snrs = [20, 10, 5, 0]
nt = 20
accs = []
for snr in snrs:
    ok = 0
    for _ in range(nt):
        for i, w in enumerate(words):
            x = data[(w, "test")]
            ps = np.mean(x ** 2)
            n_sig = rng.standard_normal(len(x)) * np.sqrt(ps / (10.0 ** (snr / 10.0)))
            Dn = classify(mfcc(x + n_sig), refs)
            ok += int(Dn.argmin() == i)
    accs.append(ok / (nt * 5))
R["snr"] = dict(snr=snrs, acc=accs, trials=nt)

# Обчислювальні витрати DTW (MAC)
T = R["T_mean"]
mac = T * T * 13
R["cost"] = {
    "T": T,
    "cell_macs": 13,
    "per_cmp": mac,
    "refs": 2,
    "dict": {str(V): float(V * 2 * mac) for V in [5, 100, 10000]},
}

# --- Графіки для звіту ---
fig, ax = plt.subplots(5, 1, figsize=(7, 7), sharex=False)
for a, w in zip(ax, words):
    x = data[(w, "ref1")]
    a.plot(np.arange(len(x)) / Fs * 1e3, x, lw=0.6)
    a.set_ylabel(w)
    a.grid(alpha=0.3)
ax[-1].set_xlabel("час, мс")
plt.tight_layout()
plt.savefig("figures/l6_wave.png", dpi=160)
plt.close()

target_word = words[1]  # "південь"
C = feat[(target_word, "ref1")]
fig, ax = plt.subplots(figsize=(6, 3))
im = ax.imshow(C.T, aspect="auto", origin="lower", cmap="viridis", extent=[0, len(C) * 10, 0, 13])
ax.set_xlabel("час, мс")
ax.set_ylabel("індекс кепстрального коефіцієнта")
plt.colorbar(im, label="значення")
plt.tight_layout()
plt.savefig("figures/l6_mfcc.png", dpi=160)
plt.close()

cst, Dacc, p = dtw(feat[(target_word, "test")], feat[(target_word, "ref1")], path=True)
fig, ax = plt.subplots(figsize=(5, 4.5))
im = ax.imshow(Dacc.T, origin="lower", aspect="auto", cmap="magma")
ax.plot([a for a, b in p], [b for a, b in p], "c-", lw=1.2)
ax.set_xlabel(f"кадри тестового слова «{target_word}»")
ax.set_ylabel(f"кадри еталона «{target_word}»")
plt.colorbar(im, label="накопичена відстань")
plt.tight_layout()
plt.savefig("figures/l6_dtw.png", dpi=160)
plt.close()
R["path_cost"] = float(cst)

fig, ax = plt.subplots(figsize=(4.6, 3.2))
ax.plot(snrs, [a * 100 for a in accs], "o-")
ax.invert_xaxis()
ax.set_xlabel("SNR, дБ")
ax.set_ylabel("точність, %")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/l6_snr.png", dpi=160)
plt.close()

with open("out/lab6.json", "w", encoding="utf-8") as fj:
    json.dump(R, fj, ensure_ascii=False, indent=1)

print("=== РЕЗУЛЬТАТИ ЛР №6 (Варіант 21: V = 9, Варіант А) ===")
print(f"Кадрів на слово: min={R['T_min']}, max={R['T_max']}, середнє={R['T_mean']:.1f}")
print("\nМатриця нормованих відстаней DTW (5x5):")
header = f"{'тест \\ еталон':<14s} | " + " | ".join(f"{w:>8s}" for w in words) + " | рішення"
print(header)
print("-" * len(header))
for i, w in enumerate(words):
    row_vals = []
    for j in range(5):
        v = Dm[i, j]
        row_vals.append(f"[{v:6.2f}]" if i == j else f" {v:6.2f} ")
    print(f"{w:<14s} | " + " | ".join(row_vals) + f" | {R['pred'][i]}")
print(f"\nТочність (з нормуванням): {int(round(R['acc']*5))}/5 = {R['acc']*100:.0f}%")
print(f"Точність (без нормування): {int(round(R['acc_raw']*5))}/5 = {R['acc_raw']*100:.0f}%")
print("\nСтійкість до шуму (SNR):")
for s, a in zip(snrs, accs):
    print(f"  SNR = {s:2d} дБ -> точність = {a*100:.0f}%")
print(f"\nВитрати DTW (T_mean = {T:.1f} кадрів, 2 еталони на слово):")
for V_sz, ops in R["cost"]["dict"].items():
    print(f"  Словник {V_sz:>5s} слів -> {ops:.2e} MAC")