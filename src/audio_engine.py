#!/usr/bin/env python3
import time, os, json, subprocess, math, signal
from collections import deque

import numpy as np

from protocol import (create_client_socket, MODE_MUSIC, MODE_AMBIENT, MODE_OFF,
                      MODE_TREE, MODE_CHASE, MODE_SPARKLE, MODE_NAMES)
import buttons
try:
    from oled_i2c import oled_show
except ImportError:
    def oled_show(*args, **kwargs):
        pass

SAMPLE_RATE = 44100
FPS = 40
FRAME_SIZE = int(SAMPLE_RATE / FPS)
ANALYSIS_WINDOW = 3
AUDIO_DEVICE = "plughw:CARD=Headphones,DEV=0"


class AudioEngine:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        self.songs_dir = os.path.join(base, "..", "songs")
        self.bpm_file = os.path.join(base, "..", "bpm_table.json")
        buttons.setup()
        self.songs = sorted(f for f in os.listdir(self.songs_dir)
                            if f.lower().endswith(".mp3"))
        self.idx = 0
        self.sock = None
        self.running = True
        self.note_smoother = None
        self.bass_hist = deque(maxlen=FPS)
        self.mid_hist = deque(maxlen=FPS)
        self.kick_env = 0.0
        self.snare_env = 0.0
        self.pitch_min_amp = 0.2
        self.kick_rel = 1.6
        self.kick_abs = 0.01
        self.snare_rel = 1.4
        self.snare_abs = 0.01
        self.mode = MODE_MUSIC
        self.paused = False
        try:
            with open(self.bpm_file, "r") as f:
                self.bpm_table = json.load(f)
        except Exception:
            self.bpm_table = {}

    def connect(self):
        if not self.sock:
            self.sock = create_client_socket()

    def send(self, msg):
        if not self.sock:
            self.connect()
        if not self.sock:
            return
        try:
            self.sock.sendall((msg + "\n").encode())
        except BrokenPipeError:
            self.sock = None

    def analyze(self, samples):
        if samples.size == 0:
            return 0.0, 0.0, 0.0, 0.0
        samples = samples - np.mean(samples)
        win = np.hanning(samples.size).astype(np.float32)
        spec = np.fft.rfft(samples * win)
        mag = np.abs(spec)
        freqs = np.fft.rfftfreq(samples.size, 1.0 / SAMPLE_RATE)

        def band(lo, hi):
            mask = (freqs >= lo) & (freqs <= hi)
            if not np.any(mask):
                return 0.0
            return float(np.mean(mag[mask]))

        bass = band(40, 150)
        mid = band(200, 2000)
        high = band(4000, 8000)
        overall = float(np.mean(mag))

        lead = 0.0
        mask = (freqs >= 200) & (freqs <= 2000)
        if np.any(mask):
            mm = mag[mask]
            peak = float(np.max(mm))
            if peak > self.pitch_min_amp:
                idx = int(np.argmax(mm))
                lead = float(freqs[mask][idx])

        self.bass_hist.append(bass)
        self.mid_hist.append(mid)
        bmean = float(np.mean(self.bass_hist)) if self.bass_hist else 0.0
        mmean = float(np.mean(self.mid_hist)) if self.mid_hist else 0.0

        if bmean > 0 and bass > max(self.kick_abs, self.kick_rel * bmean):
            self.kick_env = 1.0
        else:
            self.kick_env *= 0.85
        if mmean > 0 and mid > max(self.snare_abs, self.snare_rel * mmean):
            self.snare_env = 1.0
        else:
            self.snare_env *= 0.85

        self.kick_env = float(max(0.0, min(1.0, self.kick_env)))
        self.snare_env = float(max(0.0, min(1.0, self.snare_env)))
        level = min(1.0, overall * 4.0)
        return lead, bass, high, level

    @staticmethod
    def freq_to_note(freq):
        if freq <= 0:
            return -1, 0.0, None
        midi = 69.0 + 12.0 * math.log2(freq / 440.0)
        near = round(midi)
        idx = int(near) % 12
        gliss = float(midi - near)
        return idx, gliss, midi

    def loop(self):
        window_samples = FRAME_SIZE * ANALYSIS_WINDOW
        buf = np.zeros(window_samples, dtype=np.int16)
        while self.running:
            if not self.songs:
                oled_show("No songs", "", "")
                time.sleep(1.0)
                continue
            name = self.songs[self.idx]
            path = os.path.join(self.songs_dir, name)
            bpm = self.bpm_table.get(name, {}).get("bpm")
            line3 = f"BPM: {bpm:.0f}" if bpm else MODE_NAMES.get(self.mode, "Music")
            oled_show("Playing:", name[:15], line3)
            cmd = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", path,
                "-filter_complex",
                "[0:a]asplit=2[out1][out2];"
                "[out2]aresample=44100,pan=mono|c0=c0[pcm]",
                "-map", "[out1]", "-f", "alsa", AUDIO_DEVICE,
                "-map", "[pcm]", "-f", "s16le", "-"
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=FRAME_SIZE * 4)
            self.note_smoother = None
            self.bass_hist.clear()
            self.mid_hist.clear()
            self.kick_env = 0.0
            self.snare_env = 0.0
            self.paused = False
            while proc.poll() is None and self.running:
                # Buttons
                if buttons.button_pressed(buttons.BUTTON_MODE):
                    # cycle through 6 modes
                    self.mode = (self.mode + 1) % 6
                    oled_show("Mode:", MODE_NAMES.get(self.mode, "?"), name[:15])
                    if self.mode == MODE_OFF:
                        self.send(f"STATE {MODE_OFF} -1 0 0 0 0")
                    time.sleep(0.1)
                if buttons.button_pressed(buttons.BUTTON_NEXT):
                    self.idx = (self.idx + 1) % len(self.songs)
                    proc.terminate(); break
                if buttons.button_pressed(buttons.BUTTON_PREV):
                    self.idx = (self.idx - 1) % len(self.songs)
                    proc.terminate(); break
                if buttons.button_pressed(buttons.BUTTON_PLAY):
                    if not self.paused:
                        proc.send_signal(signal.SIGSTOP)
                        self.paused = True
                        oled_show("Paused", name[:15], "")
                    else:
                        proc.send_signal(signal.SIGCONT)
                        self.paused = False
                        oled_show("Playing", name[:15], MODE_NAMES.get(self.mode, ""))
                    time.sleep(0.2)
                if self.paused:
                    time.sleep(0.05)
                    continue

                raw = proc.stdout.read(FRAME_SIZE * 2)
                if not raw:
                    break
                new = np.frombuffer(raw, dtype=np.int16)
                n = new.size
                if n > window_samples:
                    new = new[-window_samples:]; n = new.size
                buf = np.roll(buf, -n)
                buf[-n:] = new
                f32 = buf.astype(np.float32) / 32768.0
                lead, bass, high, level = self.analyze(f32)
                note_idx, gliss, midi = self.freq_to_note(lead)
                if midi is not None:
                    if self.note_smoother is None:
                        self.note_smoother = midi
                    else:
                        self.note_smoother = 0.75 * self.note_smoother + 0.25 * midi
                    final_midi = self.note_smoother
                    final_note = int(round(final_midi)) % 12
                else:
                    if self.note_smoother is not None:
                        self.note_smoother = 0.9 * self.note_smoother
                        final_note = int(round(self.note_smoother)) % 12
                    else:
                        final_note = -1

                if self.mode == MODE_MUSIC:
                    msg = f"STATE {MODE_MUSIC} {final_note} {level:.2f} {gliss:.3f} {self.kick_env:.2f} {self.snare_env:.2f}"
                elif self.mode == MODE_AMBIENT:
                    msg = f"STATE {MODE_AMBIENT} -1 {level:.2f} 0.000 0.00 0.00"
                elif self.mode == MODE_OFF:
                    msg = f"STATE {MODE_OFF} -1 0 0 0 0"
                elif self.mode == MODE_TREE:
                    msg = f"STATE {MODE_TREE} -1 {level:.2f} 0 0 0"
                elif self.mode == MODE_CHASE:
                    msg = f"STATE {MODE_CHASE} -1 {level:.2f} 0 0 0"
                elif self.mode == MODE_SPARKLE:
                    msg = f"STATE {MODE_SPARKLE} -1 {level:.2f} 0 0 0"
                else:
                    msg = f"STATE {MODE_MUSIC} {final_note} {level:.2f} {gliss:.3f} {self.kick_env:.2f} {self.snare_env:.2f}"
                self.send(msg)
                time.sleep(1.0 / FPS * 0.5)
            if proc.poll() is None:
                proc.terminate()
            try:
                proc.wait(timeout=1.0)
            except Exception:
                pass
            self.idx = (self.idx + 1) % len(self.songs)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    AudioEngine().loop()
