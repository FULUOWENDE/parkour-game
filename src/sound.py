"""Procedural sound effects & BGM system for Campus Rush.

All sounds are synthesised at runtime — no external audio files needed.
Generates 16-bit 22050Hz mono WAV samples via waveform synthesis.

Sound effects:
  jump        — sneaker-on-track thud
  slide       — fabric rustle
  death       — bag crash + wailing voice
  item_shield — magical shimmer (book pickup)
  item_bun    — crunch/chew (bun pickup)
  item_key    — rising whoosh (bike key)
  item_ticket — alarm buzz (late ticket)
  item_roster — freeze stinger (roll call)
  rain_start  — soft umbrella pop
  click       — UI button click

BGM layers (generated as looping ambient textures):
  menu        — gentle major-key arpeggio pad
  early       — light rhythm + bird-like chirps
  tension     — faster minor-key pulse + driving bass
"""

import io
import math
import random
import struct

import pygame

# ── Constants ────────────────────────────────────────────────────
SAMPLE_RATE = 22050
BITS = 16
CHANNELS = 1
MAX_AMP = 32767


# ═══════════════════════════════════════════════════════════════════
#  WAV BUILDER
# ═══════════════════════════════════════════════════════════════════

def _build_wav(samples):
    """Pack a list of float samples (-1.0..1.0) into WAV bytes, return a pygame Sound."""
    if not samples:
        return None

    # Convert float samples to 16-bit ints
    int_samples = [
        max(-32768, min(32767, int(s * 32767)))
        for s in samples
    ]
    n = len(int_samples)

    buf = io.BytesIO()
    byte_rate = SAMPLE_RATE * CHANNELS * BITS // 8
    block_align = CHANNELS * BITS // 8
    data_size = n * BITS // 8

    # RIFF header
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')

    # fmt sub-chunk
    buf.write(b'fmt ')
    buf.write(struct.pack('<I', 16))          # sub-chunk size (PCM)
    buf.write(struct.pack('<H', 1))            # audio format (PCM)
    buf.write(struct.pack('<H', CHANNELS))
    buf.write(struct.pack('<I', SAMPLE_RATE))
    buf.write(struct.pack('<I', byte_rate))
    buf.write(struct.pack('<H', block_align))
    buf.write(struct.pack('<H', BITS))

    # data sub-chunk
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    for s in int_samples:
        buf.write(struct.pack('<h', s))

    wav_bytes = buf.getvalue()
    try:
        return pygame.mixer.Sound(buffer=wav_bytes)
    except Exception:
        return None


def _make_sound(samples):
    """Shorthand: build WAV from float samples, return Sound or None."""
    return _build_wav(samples)


# ═══════════════════════════════════════════════════════════════════
#  WAVEFORM HELPERS
# ═══════════════════════════════════════════════════════════════════

def _sine(freq, duration, volume=0.3):
    """Generate a sine-wave tone."""
    n = int(SAMPLE_RATE * duration)
    return [
        math.sin(2 * math.pi * freq * i / SAMPLE_RATE) * volume
        for i in range(n)
    ]


def _saw(freq, duration, volume=0.3):
    """Generate a sawtooth wave."""
    n = int(SAMPLE_RATE * duration)
    return [
        (2 * ((freq * i / SAMPLE_RATE) % 1.0) - 1) * volume
        for i in range(n)
    ]


def _square(freq, duration, volume=0.3):
    """Generate a square wave."""
    n = int(SAMPLE_RATE * duration)
    return [
        (1 if (freq * i / SAMPLE_RATE) % 1.0 < 0.5 else -1) * volume
        for i in range(n)
    ]


def _noise(duration, volume=0.3):
    """Generate white noise."""
    n = int(SAMPLE_RATE * duration)
    return [
        random.uniform(-1, 1) * volume
        for _ in range(n)
    ]


def _silence(duration):
    """Generate silence."""
    return [0.0] * int(SAMPLE_RATE * duration)


def _envelope(samples, attack=0.01, decay=0.1, sustain=0.7, release=0.05):
    """Apply ADSR envelope to samples (times in seconds)."""
    n = len(samples)
    sr = SAMPLE_RATE
    a_samp = int(attack * sr)
    d_samp = int(decay * sr)
    r_samp = int(release * sr)

    result = []
    for i, s in enumerate(samples):
        if i < a_samp:
            env = i / max(1, a_samp)
        elif i < a_samp + d_samp:
            env = 1.0 - (1.0 - sustain) * (i - a_samp) / max(1, d_samp)
        elif i >= n - r_samp:
            env = sustain * (n - i) / max(1, r_samp)
        else:
            env = sustain
        result.append(s * env)
    return result


def _mix(*tracks):
    """Mix multiple sample lists together (additive, clamped)."""
    if not tracks:
        return []
    length = max(len(t) for t in tracks)
    result = []
    for i in range(length):
        val = 0.0
        for t in tracks:
            if i < len(t):
                val += t[i]
        result.append(max(-1.0, min(1.0, val)))
    return result


def _fade_in(samples, duration=0.02):
    """Linear fade-in."""
    n = len(samples)
    fade_samp = int(duration * SAMPLE_RATE)
    result = []
    for i, s in enumerate(samples):
        if i < fade_samp:
            s *= i / max(1, fade_samp)
        result.append(s)
    return result


def _fade_out(samples, duration=0.05):
    """Linear fade-out."""
    n = len(samples)
    fade_samp = int(duration * SAMPLE_RATE)
    result = []
    for i, s in enumerate(samples):
        if i >= n - fade_samp:
            s *= (n - i) / max(1, fade_samp)
        result.append(s)
    return result


def _freq_sweep(start_freq, end_freq, duration, volume=0.3, wave_fn=_sine):
    """Frequency sweep from start_freq to end_freq over duration."""
    n = int(SAMPLE_RATE * duration)
    result = []
    for i in range(n):
        t = i / n
        freq = start_freq + (end_freq - start_freq) * t
        phase = (i / SAMPLE_RATE) * freq * 2 * math.pi
        # Accumulate phase correctly
        if i == 0:
            cum_phase = 0
        else:
            cum_phase += 2 * math.pi * freq / SAMPLE_RATE
        result.append(math.sin(cum_phase) * volume)
    return result


# ═══════════════════════════════════════════════════════════════════
#  SFX GENERATORS
# ═══════════════════════════════════════════════════════════════════

def _gen_jump():
    """Sneaker-on-track thud — low-frequency pulse with quick decay."""
    body = _sine(80, 0.08, 0.5)
    click = _sine(600, 0.02, 0.2)
    noise = [n * 0.15 for n in _noise(0.04)]
    # Pad click to align with body
    body_mix = _mix(body, noise)
    return _envelope(body_mix, attack=0.002, decay=0.06, sustain=0.0, release=0.02)


def _gen_slide():
    """Fabric rustle — bandpass-ish filtered noise with short duration."""
    n = int(SAMPLE_RATE * 0.18)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Simulate bandpass by modulating noise with a mid-frequency sine
        carrier = math.sin(2 * math.pi * 1800 * t)
        noise_val = random.uniform(-1, 1)
        raw.append(noise_val * carrier * 0.35)
    return _envelope(raw, attack=0.005, decay=0.1, sustain=0.3, release=0.07)


def _gen_death():
    """Bag crash + wailing '要迟到了!' voice — impact + descending tone."""
    # Impact noise
    impact = [n * 0.6 for n in _noise(0.15)]
    impact = _envelope(impact, attack=0.002, decay=0.12, sustain=0.0, release=0.03)

    # Descending wail (simulated voice)
    wail = _freq_sweep(450, 120, 0.55, volume=0.35)
    # Add vibrato
    n = len(wail)
    for i in range(n):
        t = i / SAMPLE_RATE
        vib = math.sin(2 * math.pi * 7 * t) * 0.06
        wail[i] = wail[i] * (1 + vib) if abs(wail[i]) > 0.001 else 0

    # Thud on ground
    thud = _sine(55, 0.2, 0.4)
    thud = _envelope(thud, attack=0.005, decay=0.15, sustain=0.0, release=0.05)

    # Silence gap then combine
    gap = _silence(0.08)
    return _mix(impact, thud, gap + wail)


def _gen_item_shield():
    """Magical shimmer for book pickup — ascending arpeggio with sparkle."""
    notes = [523, 659, 784, 1047]  # C5 E5 G5 C6
    total_dur = 0.45
    note_dur = total_dur / len(notes)
    segments = []
    for i, freq in enumerate(notes):
        seg = _sine(freq, note_dur, 0.22)
        # Add slight detune sparkle
        sparkle = _sine(freq * 1.008, note_dur, 0.1)
        seg = _mix(seg, sparkle)
        seg = _envelope(seg, attack=0.01, decay=note_dur * 0.5, sustain=0.6, release=note_dur * 0.3)
        segments.append(seg)
    # Concatenate with tiny overlaps
    result = []
    for seg in segments:
        result.extend(seg)
    # Add high shimmer
    shimmer = [s * 0.12 for s in _sine(8000, total_dur + 0.1, 0.15)]
    shimmer = _envelope(shimmer, attack=0.02, decay=0.1, sustain=0.3, release=0.15)
    result = _mix(result, shimmer + _silence(0.05))
    return _fade_out(result, 0.08)


def _gen_item_bun():
    """Crunch/chew sound — two quick noise bursts."""
    crunch1 = [n * 0.4 for n in _noise(0.06)]
    crunch1 = _envelope(crunch1, attack=0.002, decay=0.04, sustain=0.0, release=0.02)
    crunch2 = [n * 0.35 for n in _noise(0.07)]
    crunch2 = _envelope(crunch2, attack=0.002, decay=0.05, sustain=0.0, release=0.02)

    # High-frequency click for each crunch
    click1 = _sine(3000, 0.015, 0.2)
    click2 = _sine(3500, 0.015, 0.18)

    result = _mix(crunch1, click1)
    gap = _silence(0.05)
    result += gap
    result += _mix(crunch2, click2)
    return result


def _gen_item_key():
    """Rising whoosh for bike key — upward sweep with brightness."""
    whoosh = _freq_sweep(300, 1400, 0.35, volume=0.3)
    # Add harmonic for brightness
    harmonic = _freq_sweep(600, 2800, 0.35, volume=0.12)
    result = _mix(whoosh, harmonic)
    return _envelope(result, attack=0.02, decay=0.15, sustain=0.6, release=0.12)


def _gen_item_ticket():
    """Alarm buzz for late ticket — harsh dual-tone buzz."""
    buzz1 = _square(120, 0.3, 0.3)
    buzz2 = _square(180, 0.3, 0.25)
    noise = [n * 0.1 for n in _noise(0.3)]
    result = _mix(buzz1, buzz2, noise)
    return _envelope(result, attack=0.005, decay=0.08, sustain=0.5, release=0.1)


def _gen_item_roster():
    """Freeze stinger for roll call — descending 'failure' tone."""
    tone = _freq_sweep(500, 80, 0.35, volume=0.35)
    # Add dissonant harmonic
    dissonant = _freq_sweep(480, 90, 0.35, volume=0.15)
    result = _mix(tone, dissonant)
    return _envelope(result, attack=0.01, decay=0.2, sustain=0.3, release=0.12)


def _gen_rain_start():
    """Soft umbrella pop / rain beginning — gentle filtered noise whoosh."""
    n = int(SAMPLE_RATE * 0.5)
    whoosh = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Increasing volume over time
        env = min(1.0, i / (SAMPLE_RATE * 0.25))
        # Low-pass-ish by averaging adjacent random values
        noise_val = random.uniform(-1, 1) * 0.6
        whoosh.append(noise_val * env)
    return _envelope(whoosh, attack=0.1, decay=0.2, sustain=0.5, release=0.15)


def _gen_click():
    """UI button click — very short tick."""
    tick = _sine(1200, 0.015, 0.2)
    return _envelope(tick, attack=0.001, decay=0.01, sustain=0.0, release=0.004)


# ═══════════════════════════════════════════════════════════════════
#  BGM GENERATORS (looping ambient textures, ~6-10 sec each)
# ═══════════════════════════════════════════════════════════════════

def _gen_bgm_menu():
    """Gentle major-key arpeggio pad for main menu.

    C major: C4 E4 G4 C5, slow arpeggio with soft attack.
    """
    duration = 8.0
    n = int(SAMPLE_RATE * duration)
    notes_c_major = [262, 330, 392, 523, 659, 784]  # C4 D4 E4 G4 E5 G5-ish
    pattern = [262, 330, 392, 523, 392, 330, 262, 330, 392, 523, 659, 523, 392, 262]
    note_len = duration / len(pattern)

    samples = []
    for ni, freq in enumerate(pattern):
        seg_n = int(SAMPLE_RATE * note_len)
        for i in range(seg_n):
            t = i / SAMPLE_RATE
            # Soft sine with slow tremolo
            tremolo = 0.7 + 0.3 * math.sin(2 * math.pi * 0.4 * (ni * note_len + t))
            val = math.sin(2 * math.pi * freq * t) * 0.08 * tremolo
            # Add sub-bass pad
            val += math.sin(2 * math.pi * freq * 0.5 * t) * 0.04
            samples.append(val)
        # Crossfade between notes
        fade_n = int(SAMPLE_RATE * 0.06)
        for i in range(fade_n):
            if len(samples) - fade_n + i >= 0:
                idx = len(samples) - fade_n + i
                if idx < len(samples):
                    samples[idx] *= 1.0 - i / fade_n
    return samples


def _gen_bgm_early():
    """Light rhythm + bird-like chirps for early game (sunny).

    Gentle pulse with occasional high-frequency chirps.
    """
    duration = 7.0
    n = int(SAMPLE_RATE * duration)
    samples = [0.0] * n

    # Soft bass pulse every beat (~100 BPM = 0.6s per beat)
    beat_interval = 0.6
    for beat_t in [i * beat_interval for i in range(int(duration / beat_interval))]:
        start_i = int(beat_t * SAMPLE_RATE)
        for i in range(int(0.2 * SAMPLE_RATE)):
            idx = start_i + i
            if idx < n:
                t_in = i / SAMPLE_RATE
                env = math.exp(-t_in * 8)
                samples[idx] += math.sin(2 * math.pi * 180 * t_in) * 0.06 * env

    # Offbeat hi-hat tick
    for beat_t in [i * beat_interval + 0.3 for i in range(int(duration / beat_interval))]:
        start_i = int(beat_t * SAMPLE_RATE)
        for i in range(int(0.04 * SAMPLE_RATE)):
            idx = start_i + i
            if idx < n:
                samples[idx] += random.uniform(-1, 1) * 0.04

    # Bird chirps (random high-frequency sine bursts)
    for _ in range(6):
        chirp_t = random.uniform(1.0, duration - 0.5)
        chirp_freq = random.choice([2200, 2600, 3100, 3500, 2800, 2400])
        start_i = int(chirp_t * SAMPLE_RATE)
        chirp_dur = int(0.08 * SAMPLE_RATE)
        for i in range(chirp_dur):
            idx = start_i + i
            if idx < n:
                t_in = i / SAMPLE_RATE
                env = math.exp(-t_in * 30)
                # Frequency modulation for bird-like warble
                warble = math.sin(2 * math.pi * 25 * t_in) * 0.3
                freq = chirp_freq * (1 + warble)
                samples[idx] += math.sin(2 * math.pi * freq * t_in) * 0.07 * env

    return [max(-0.3, min(0.3, s)) for s in samples]


def _gen_bgm_tension():
    """Faster minor-key pulse + driving bass for high-score / rainy segments.

    A minor: faster tempo, more urgency.
    """
    duration = 6.0
    n = int(SAMPLE_RATE * duration)
    samples = [0.0] * n

    # Driving bass pulse (~140 BPM = 0.43s per beat)
    beat_interval = 0.43
    bass_notes = [110, 110, 130, 146, 130, 110, 98, 110]  # A minorish
    for bi, (beat_t, freq) in enumerate(
        zip([i * beat_interval for i in range(min(len(bass_notes), int(duration / beat_interval)))],
            bass_notes)
    ):
        start_i = int(beat_t * SAMPLE_RATE)
        note_dur = int(beat_interval * 0.7 * SAMPLE_RATE)
        for i in range(note_dur):
            idx = start_i + i
            if idx < n:
                t_in = i / SAMPLE_RATE
                env = math.exp(-t_in * 4)
                # Sawtooth for edgier bass
                phase = (freq * t_in) % 1.0
                samples[idx] += (2 * phase - 1) * 0.08 * env

    # Tense high pad
    for i in range(n):
        t = i / SAMPLE_RATE
        # Minor chord pad (A C E)
        pad = math.sin(2 * math.pi * 220 * t) * 0.03
        pad += math.sin(2 * math.pi * 262 * t) * 0.025
        pad += math.sin(2 * math.pi * 330 * t) * 0.02
        # Slow tremolo
        tremolo = 0.5 + 0.5 * math.sin(2 * math.pi * 0.6 * t)
        samples[i] += pad * tremolo

    return [max(-0.3, min(0.3, s)) for s in samples]


# ═══════════════════════════════════════════════════════════════════
#  SOUND MANAGER
# ═══════════════════════════════════════════════════════════════════

class SoundManager:
    """Manages all sound effects and background music."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        if not enabled:
            return

        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        except pygame.error:
            self.enabled = False
            return

        # ── Pre-generate all SFX ──
        self.sfx = {}
        self._sfx_funcs = {
            "jump":        _gen_jump,
            "slide":       _gen_slide,
            "death":       _gen_death,
            "item_shield": _gen_item_shield,
            "item_bun":    _gen_item_bun,
            "item_ebike":  _gen_item_key,    # rising whoosh for shared e-bike
            "item_key":    _gen_item_key,
            "item_ticket": _gen_item_ticket,
            "item_roster": _gen_item_roster,
            "rain_start":  _gen_rain_start,
            "click":       _gen_click,
        }
        for name, func in self._sfx_funcs.items():
            sound = _make_sound(func())
            if sound:
                sound.set_volume(0.7)
            self.sfx[name] = sound

        # ── Pre-generate BGM loops ──
        self._bgm_data = {
            "menu":    _gen_bgm_menu(),
            "early":   _gen_bgm_early(),
            "tension": _gen_bgm_tension(),
        }
        self._bgm_sounds = {}
        for name, samples in self._bgm_data.items():
            snd = _make_sound(samples)
            if snd:
                snd.set_volume(0.35)
            self._bgm_sounds[name] = snd

        # ── Channels ──
        self._sfx_channel = pygame.mixer.Channel(0)
        self._bgm_channel = pygame.mixer.Channel(1)

        self._current_bgm = None
        self._bgm_fade_ms = 400

    # ── SFX playback ──────────────────────────────────────────

    def _play(self, name):
        if not self.enabled:
            return
        sound = self.sfx.get(name)
        if sound:
            self._sfx_channel.play(sound)

    def play_jump(self):
        self._play("jump")

    def play_slide(self):
        self._play("slide")

    def play_death(self):
        self._play("death")

    def play_item(self, item_type):
        """Play item pickup sound based on item class name."""
        mapping = {
            "BookShield":  "item_shield",
            "SpeedBun":    "item_bun",
            "SharedEBike": "item_ebike",
        }
        name = mapping.get(item_type, "item_shield")
        self._play(name)

    def play_rain_start(self):
        self._play("rain_start")

    def play_click(self):
        self._play("click")

    # ── BGM control ───────────────────────────────────────────

    def switch_bgm(self, name):
        """Switch background music to a named BGM loop ('menu'/'early'/'tension')."""
        if not self.enabled:
            return
        if name == self._current_bgm:
            return
        sound = self._bgm_sounds.get(name)
        if sound is None:
            return
        self._bgm_channel.stop()
        self._bgm_channel.play(sound, loops=-1, fade_ms=self._bgm_fade_ms)
        self._current_bgm = name

    def stop_bgm(self):
        """Fade out and stop background music."""
        if not self.enabled:
            return
        self._bgm_channel.fadeout(self._bgm_fade_ms)
        self._current_bgm = None

    def set_muted(self, muted):
        """Mute/unmute all audio."""
        if not self.enabled:
            return
        vol = 0.0 if muted else 1.0
        self._sfx_channel.set_volume(vol * 0.7)
        self._bgm_channel.set_volume(vol * 0.35)

    def cleanup(self):
        """Stop all audio and release resources."""
        if not self.enabled:
            return
        self._bgm_channel.stop()
        self._sfx_channel.stop()
