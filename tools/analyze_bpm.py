#!/usr/bin/env python3
import os, json, sys
try:
    import librosa, numpy as np  # noqa
except ImportError:
    print("Install librosa, numpy, soundfile first.")
    sys.exit(1)


def analyze_song(path):
    y, sr = librosa.load(path, sr=None, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo)


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    songs_dir = os.path.join(base, "..", "songs")
    out = os.path.join(base, "..", "bpm_table.json")
    data = {}
    if os.path.exists(out):
        try:
            with open(out, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
    for name in sorted(os.listdir(songs_dir)):
        if not name.lower().endswith(".mp3"):
            continue
        if name in data:
            continue
        path = os.path.join(songs_dir, name)
        print("Analyzing", name)
        bpm = analyze_song(path)
        data[name] = {"bpm": bpm}
        print(" -> %.1f BPM" % bpm)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print("Saved to", out)


if __name__ == "__main__":
    main()
