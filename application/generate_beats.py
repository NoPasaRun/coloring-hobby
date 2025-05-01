import os
import sys
from pathlib import Path

import librosa
import json


ROOT_PATH = Path(__file__).parent.resolve()


def main(*args):
    if not len(args):
        return print("Pass filepath to audio file")
    if not os.path.exists(args[0]):
        return print("File does not exist")
    if not args[0].endswith(".mp3"):
        return print("File must be in mp3 format to generate beat")
    y, sr = librosa.load(args[0])
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.times_like(onset_env, sr=sr)

    beats = [
        {"time": t, "intensity": float(i / max(onset_env))}
        for t, i in zip(times, onset_env) if i > float(args[1])
    ]
    with open(ROOT_PATH / "src/beats.json", "w") as f:
        json.dump(beats, f)


if __name__ == '__main__':
    main(*sys.argv[1:])
