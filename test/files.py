from pathlib import Path
import stroll

WAVE_FILES = list(stroll(Path(__file__).parent / 'data', suffix='.wav'))
READABLE = [
    'Kick.wav',
    'Snare.wav',
    'Tom.wav',
    'bell01.wav',
    'test-44100Hz-2ch-32bit-float-le.wav',
    'M1F1-float32-AFsp.wav',
    'M1F1-float64-AFsp.wav',
    'M1F1-int16-AFsp.wav',
    'M1F1-int32-AFsp.wav',
    'M1F1-uint8-AFsp.wav',
    'stereofl.wav',
    'stereol.wav',
]


def find(s):
    return (w for w in WAVE_FILES if w.name in READABLE and s in w.name)
