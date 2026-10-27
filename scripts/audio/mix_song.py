import sys
import subprocess
import numpy as np
import soundfile as sf

FF = "/usr/bin/ffmpeg"
SR = 44100


def dec(path, sr=SR):
    y, fs = sf.read(path, dtype="float32", always_2d=True)
    if y.shape[1] == 1:
        y = np.repeat(y, 2, axis=1)
    if fs != sr:
        import librosa
        y = np.stack([librosa.resample(y[:, c], orig_sr=fs, target_sr=sr) for c in range(y.shape[1])], axis=1)
    return y


def rms(x):
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


vocal, inst, out = sys.argv[1], sys.argv[2], sys.argv[3]
v = dec(vocal)
i = dec(inst)
n = min(len(v), len(i))
v, i = v[:n], i[:n]
vv = v.copy()
d1, d2 = int(0.008 * SR), int(0.016 * SR)
if n > d2:
    vv[d1:, 0] += v[:-d1, 1] * 0.06
    vv[d2:, 1] += v[:-d2, 0] * 0.045
vv *= 0.92
vg = 10 ** (-15 / 20) / rms(vv)
ig = 10 ** (-17 / 20) / rms(i)
mix = vv * vg + i * ig
peak = float(np.max(np.abs(mix)) + 1e-9)
if peak > 10 ** (-1 / 20):
    mix *= 10 ** (-1 / 20) / peak
sf.write(out, mix.astype(np.float32), SR, subtype="PCM_24")
mp3 = out.replace(".wav", ".mp3")
subprocess.run([FF, "-y", "-loglevel", "error", "-i", out, "-af",
                "loudnorm=I=-14:TP=-1.5:LRA=11", "-b:a", "320k", mp3], check=True)
print("mixed", mp3, "dur", round(n / SR, 2))
