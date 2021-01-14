from pathlib import Path
import stroll
import wavemap

FILE_ROOT = Path(__file__).parent
DATA_ROOT = FILE_ROOT / 'data'
EXPECTED_ROOT = FILE_ROOT / 'expected'
WAVE_FILES = list(stroll(DATA_ROOT, suffix='.wav'))
READABLE = [
    'Kick.wav',
    'Snare.wav',
    'Tom.wav',
    'bell01.wav',
    'test-44100Hz-2ch-32bit-float-le.wav',
    # 'M1F1-AlawWE-AFsp.wav',
    'M1F1-float32-AFsp.wav',
    'M1F1-float32WE-AFsp.wav',
    'M1F1-float64-AFsp.wav',
    'M1F1-float64WE-AFsp.wav',
    'M1F1-int12WE-AFsp.wav',
    'M1F1-int16-AFsp.wav',
    'M1F1-int16WE-AFsp.wav',
    'M1F1-int32-AFsp.wav',
    'M1F1-int32WE-AFsp.wav',
    # 'M1F1-mulawWE-AFsp.wav',
    'M1F1-uint8-AFsp.wav',
    'M1F1-uint8WE-AFsp.wav',
    '6_Channel_ID.wav',
    '4ch.wav',
    'drmapan.wav',
    'stereofl.wav',
    'stereol.wav',
]


def find(s=''):
    return (w for w in WAVE_FILES if w.name in READABLE and s in w.name)


def canonical(filename):
    target_file = EXPECTED_ROOT / filename.relative_to(DATA_ROOT)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    return target_file


def copy_canonical():
    for f in find():
        wavemap.copy_to(wavemap(f), canonical(f))


if __name__ == '__main__':
    copy_canonical()
