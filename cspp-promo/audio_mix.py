#!/usr/bin/env python3
"""Synthesizes an original background music bed + transition SFX (pure numpy),
places the voiceover clips on the timeline, ducks the music under the voice and
writes build/mix.wav (48 kHz stereo)."""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
TL = json.load(open(os.path.join(B, "timeline.json")))
SR = 48000
TOTAL = TL["total"]
N = int((TOTAL + 0.5) * SR)
rng = np.random.default_rng(11)

def read_wav(p):
    with wave.open(p) as w:
        assert w.getsampwidth() == 2 and w.getframerate() == SR
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels())

def write_wav(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def add(buf, sig, t, pan=0.0, gain=1.0):
    """add mono (n,) or stereo (n,2) sig at time t"""
    i = int(t * SR)
    if i >= len(buf): return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], 1) * 1.414
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain

def smooth(x, n):
    """centered moving average via cumulative sum (O(N))"""
    n = max(1, int(n))
    if n == 1: return x.astype(np.float32)
    c = np.cumsum(np.concatenate([np.zeros(1), np.pad(x, (n // 2, n - n // 2 - 1), mode="edge")]))
    return ((c[n:] - c[:-n]) / n).astype(np.float32)

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

# --------------------------------------------------------------- music
BPM = 96
beat = 60 / BPM
bar = beat * 4
# Bm  G  D  A   (vi IV I V in D major)
CHORDS = [[47, 50, 54], [43, 47, 50], [50, 54, 57], [45, 49, 52]]
ROOTS = [35, 31, 38, 33]

vo, dur = TL["vo"], TL["dur"]
GROOVE_IN = vo["s3"] + 1.6          # CSPP slam
OUTRO = vo["s9"] + dur["s9"] + 0.4    # final chord
music = np.zeros((N, 2), np.float32)

def pad_note(f, length):
    t = np.arange(int(length * SR)) / SR
    env = np.minimum(1, t / 0.7) * np.minimum(1, (length - t) / 0.9).clip(0)
    out = np.zeros((len(t), 2), np.float32)
    for ch, det in ((0, -0.004), (1, 0.004)):
        ff = f * (1 + det)
        sig = sum(np.sin(2 * np.pi * ff * h * t + h) * (1 / h) * np.exp(-h * 0.35) for h in range(1, 9))
        out[:, ch] = sig * env
    return out

def pluck(f, length=0.5):
    t = np.arange(int(length * SR)) / SR
    env = np.exp(-t * 7) * np.minimum(1, t / 0.004)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * env

def kick():
    t = np.arange(int(0.45 * SR)) / SR
    f = 46 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7.5)) + rng.normal(0, 1, len(t)) * np.exp(-t * 300) * 0.25

def hat():
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.normal(0, 1, len(t))
    return (n - smooth(n, 6)) * np.exp(-t * 90)

def clap():
    t = np.arange(int(0.25 * SR)) / SR
    n = rng.normal(0, 1, len(t))
    n = smooth(n, 3) - smooth(n, 24)
    return n * np.exp(-t * 18) * 1.6

def bass_note(f, length):
    t = np.arange(int(length * SR)) / SR
    env = np.minimum(1, t / 0.01) * np.exp(-t * 3.2)
    return np.tanh(1.4 * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))) * env

K, H, C = kick(), hat(), clap()
nbars = int(np.ceil(OUTRO / bar))
ARP = [0, 1, 2, 3, 2, 1, 2, 3]  # index into chord tones (3 == octave root)
for b in range(nbars):
    t0 = b * bar
    ch = CHORDS[b % 4]
    groove = t0 + 0.01 >= GROOVE_IN - 0.01
    # pad
    for m in ch:
        add(music, pad_note(midi(m + 12), bar + 1.0), t0, gain=0.050 if groove else 0.075)
    # arpeggio (8ths) two octaves up
    tones = [ch[0], ch[1], ch[2], ch[0] + 12]
    for i, ix in enumerate(ARP):
        tt = t0 + i * beat / 2
        if tt > OUTRO: break
        add(music, pluck(midi(tones[ix] + 24)), tt, pan=0.35 if i % 2 else -0.35, gain=0.060 if groove else 0.065)
    if groove:
        for q in range(4):
            tt = t0 + q * beat
            if tt > OUTRO - 0.05: break
            add(music, K, tt, gain=0.42)
            add(music, bass_note(midi(ROOTS[b % 4] + 12), beat * 0.95), tt, gain=0.16)
            add(music, bass_note(midi(ROOTS[b % 4] + 12), beat * 0.45), tt + beat / 2, gain=0.10)
            add(music, H, tt + beat / 2, pan=0.25, gain=0.10)
            add(music, H, tt + beat / 4 * 3, pan=-0.25, gain=0.05)
            if q in (1, 3): add(music, C, tt, gain=0.16)

# final ringing chord
for m in CHORDS[2] + [62]:
    add(music, pad_note(midi(m + 12), TOTAL - OUTRO + 0.3), OUTRO, gain=0.06)
    add(music, pluck(midi(m + 24), 3.0), OUTRO + 0.02 * (m % 5), gain=0.06)
add(music, K, OUTRO, gain=0.45)

# light stereo delay on music for space
d = int(beat * 0.75 * SR)
wet = np.zeros_like(music)
wet[d:, 0] = music[:-d, 1] * 0.22
wet[2 * d:, 1] = music[:-2 * d, 0] * 0.15
music += wet
# gentle high cut
for c in range(2):
    music[:, c] = smooth(music[:, c], 3)

# --------------------------------------------------------------- sfx
sfx = np.zeros((N, 2), np.float32)

def whoosh(length=0.7, rise=True):
    t = np.arange(int(length * SR)) / SR
    n = rng.normal(0, 1, len(t))
    bright = smooth(n, 4) - smooth(n, 40)
    dark = smooth(n, 30)
    mixp = (t / length) if rise else 1 - t / length
    env = np.sin(np.pi * (t / length)) ** 2
    return (bright * mixp + dark * 2.0 * (1 - mixp)) * env

def riser(length=2.0):
    t = np.arange(int(length * SR)) / SR
    n = rng.normal(0, 1, len(t))
    f = 200 * (12 ** (t / length))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    env = (t / length) ** 2.2
    return ((smooth(n, 5) - smooth(n, 30)) * 0.8 + tone) * env

def impact():
    t = np.arange(int(2.2 * SR)) / SR
    f = 38 + 60 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    n = rng.normal(0, 1, len(t))
    crash = (n - smooth(n, 3)) * np.exp(-t * 3.5) * 0.25
    return np.tanh(1.8 * boom) * 0.9 + crash

def ding(f=1318.5):
    t = np.arange(int(1.6 * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in ((1, 1, 3), (2.76, .4, 6), (5.4, .2, 10)))

def tick():
    t = np.arange(int(0.08 * SR)) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 60)

scene = TL["scene"]
order = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"]
for k in order[1:]:
    add(sfx, whoosh(), scene[k][0] - 0.35, pan=-0.3, gain=0.10)
add(sfx, whoosh(1.0), 0.0, gain=0.12)
add(sfx, ding(1046.5), 0.25, gain=0.07)
# CSPP reveal
add(sfx, riser(2.2), GROOVE_IN - 2.2, gain=0.10)
add(sfx, impact(), GROOVE_IN - 0.03, gain=0.30)
# price reveal (kept subtle)
add(sfx, ding(1318.5), vo["s8"] + 2.05, gain=0.035)
# ticks for list items (module highlights / benefits)
for off in (1.45, 3.7, 5.95, 9.25, 12.45):
    add(sfx, tick(), vo["s4"] + off - 0.05, gain=0.05)
for off in (4.0, 6.2, 8.6, 10.8, 12.7):
    add(sfx, tick(), vo["s6"] + off + 0.1, gain=0.05)
add(sfx, ding(1567.98), vo["s8"] + 7.75, gain=0.03)  # first-10 discount
add(sfx, ding(1046.5), vo["s9"] + 0.15, gain=0.05)  # CTA button

# --------------------------------------------------------------- voice + ducking
voice = np.zeros((N, 2), np.float32)
for k in order:
    add(voice, read_wav(os.path.join(B, "vo", f"{k}.wav")), vo[k], gain=1.0)

env = smooth(np.abs(voice).mean(1), int(0.12 * SR))
env = np.maximum(env, np.roll(env, int(0.15 * SR)))           # hold a bit after speech
env = smooth(env, int(0.25 * SR))
duck = 1 - 0.62 * np.clip(env / 0.035, 0, 1)                    # ~ -8.5 dB under speech
music *= duck[:, None]

# fade in/out
fade = np.ones(N, np.float32)
fi = int(0.4 * SR); fade[:fi] = np.linspace(0, 1, fi)
fo = int(2.5 * SR); end = int(TOTAL * SR)
fade[end - fo:end] = np.linspace(1, 0, fo); fade[end:] = 0
music *= fade[:, None]; sfx *= fade[:, None]

mix = voice * 1.0 + music * 0.85 + sfx
mix = np.tanh(mix * 1.1) / 1.1
mix = mix[:int(TOTAL * SR)]
write_wav(os.path.join(B, "mix_raw.wav"), mix)
write_wav(os.path.join(B, "music_only.wav"), (music * 0.85 + sfx)[:int(TOTAL * SR)])
print("mix written", mix.shape[0] / SR, "s; peak", float(np.abs(mix).max()))
