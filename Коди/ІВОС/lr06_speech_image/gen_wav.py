import os
import subprocess
import wave
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("wav", exist_ok=True)

words = ["північ", "південь", "захід", "схід", "центр"]
# Три варіанти вимови: ref1 (нормальна), ref2 (повільніша, нижчий тон), test (швидша, вищий тон)
variants = [
    ("ref1", 0, 1.00),
    ("ref2", -2, 0.94),
    ("test", 2, 1.06),
]

def try_windows_sapi(text, rate, out_path):
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $ukVoice = $synth.GetInstalledVoices() | Where-Object {{ $_.VoiceInfo.Culture.Name -like 'uk*' }} | Select-Object -First 1
    if ($ukVoice) {{
        $synth.SelectVoice($ukVoice.VoiceInfo.Name)
        $synth.Rate = {rate}
        $synth.SetOutputToWaveFile('{out_path.replace("'", "''")}')
        $synth.Speak('{text}')
        $synth.Dispose()
        exit 0
    }} else {{
        exit 1
    }}
    """
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True)
    return res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000

def synth_ukrainian_word_fallback(word, pitch_scale, dur_scale, out_path):
    # Детермінований формантний синтезатор українських слів словника (16 кГц, 16-біт WAV)
    # Кожна фонема має власні формантні частоти (F1, F2, F3) або шумовий спектр приголосних
    phonemes_map = {
        "північ":  [("p", 0.05), ("i", 0.11), ("v", 0.06), ("n_soft", 0.07), ("i", 0.10), ("ch", 0.09)],
        "південь": [("p", 0.05), ("i", 0.11), ("v", 0.06), ("d", 0.06), ("e", 0.11), ("n_soft", 0.08)],
        "захід":   [("z", 0.08), ("a", 0.13), ("kh", 0.08), ("i", 0.10), ("d", 0.06)],
        "схід":    [("s", 0.09), ("kh", 0.08), ("i", 0.12), ("d", 0.07)],
        "центр":   [("ts", 0.08), ("e", 0.12), ("n", 0.07), ("t", 0.05), ("r", 0.08)],
    }
    formants = {
        "a":      (750, 1250, 2500, True),
        "e":      (520, 1850, 2550, True),
        "i":      (300, 2250, 3050, True),
        "n":      (280, 1100, 2200, True),
        "n_soft": (280, 1950, 2750, True),
        "v":      (320, 950,  2100, True),
        "r":      (420, 1350, 1750, True),
        "d":      (250, 1600, 2400, True),
        "z":      (350, 1700, 4200, False),
        "s":      (1200, 4800, 6200, False),
        "kh":     (900, 2400, 3800, False),
        "ch":     (1400, 3200, 5200, False),
        "ts":     (1300, 4200, 5800, False),
        "p":      (500, 1400, 2600, False),
        "t":      (800, 2800, 4600, False),
    }
    sr = 16000
    rng = np.random.default_rng(abs(hash((word, pitch_scale, dur_scale))) % (2**32))
    chunks = [np.zeros(int(0.04 * sr))]
    f0_base = 128.0 * pitch_scale
    total_ph = len(phonemes_map[word])
    for idx_p, (ph, dur) in enumerate(phonemes_map[word]):
        n_samp = max(int(dur * dur_scale * sr), 160)
        t = np.arange(n_samp) / sr
        f1, f2, f3, voiced = formants[ph]
        f1 *= (0.97 + 0.06 * (pitch_scale - 1.0))
        f2 *= (0.98 + 0.04 * (pitch_scale - 1.0))
        if voiced:
            f0 = f0_base * (1.06 - 0.14 * (idx_p / max(total_ph - 1, 1)))
            phase = 2.0 * np.pi * np.cumsum(np.full(n_samp, f0)) / sr
            exc = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase) + 0.04 * rng.standard_normal(n_samp)
        else:
            exc = rng.standard_normal(n_samp)
            if ph in ("p", "t", "ts"):
                env_burst = np.exp(-((t - 0.35 * t[-1]) ** 2) / (2 * (0.14 * t[-1]) ** 2))
                exc *= env_burst
        sig = np.zeros(n_samp)
        for fk, bw, amp in [(f1, 90.0, 1.0), (f2, 130.0, 0.65), (f3, 180.0, 0.35)]:
            r = np.exp(-np.pi * bw / sr)
            theta = 2.0 * np.pi * fk / sr
            y = np.zeros(n_samp)
            for n in range(2, n_samp):
                y[n] = exc[n] + 2 * r * np.cos(theta) * y[n - 1] - (r ** 2) * y[n - 2]
            sig += amp * y / (np.max(np.abs(y)) + 1e-9)
        win = np.hanning(min(160, n_samp // 2 * 2))
        half = len(win) // 2
        env = np.ones(n_samp)
        env[:half] = win[:half]
        env[-half:] = win[half:]
        chunks.append(sig * env * (1.0 if voiced else 0.45))
    chunks.append(np.zeros(int(0.04 * sr)))
    full = np.concatenate(chunks)
    full = full / (np.max(np.abs(full)) + 1e-9) * 0.88
    pcm = (full * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

used_sapi = False
for w in words:
    for tag, rate, scale in variants:
        raw_path = os.path.abspath(f"wav/{w}_{tag}.wav")
        if try_windows_sapi(w, rate, raw_path):
            used_sapi = True
        else:
            synth_ukrainian_word_fallback(w, scale, 1.0 / scale, raw_path)

mode = "Windows SAPI (uk-UA)" if used_sapi else "формантний синтезатор українських фонем"
print(f"Згенеровано 15 WAV-файлів у wav/ (метод: {mode})")