from pathlib import Path
import stroll
import unittest
import wavemap

WAVE_FILES = list(stroll(Path(__file__).parent, suffix='.wav'))
READABLE = [
    'M1F1-float32-AFsp',
    'M1F1-float64-AFsp',
    'M1F1-int16-AFsp',
    'M1F1-int32-AFsp',
    'M1F1-uint8-AFsp',
    'stereofl',
    'stereol',
]


class TestWaveMap(unittest.TestCase):
    def test_existing(self):
        success, failure = [], []
        for w in WAVE_FILES:
            import sys

            print(w, file=sys.stderr)
            try:
                success.append(wavemap.WaveMap(w))
            except Exception as e:
                failure.append((w.stem, e.args[0]))

        filenames = [s.filename.stem for s in success]
        assert filenames == READABLE
        dtypes = [str(s.dtype) for s in success]
        lengths = [s.shape[0] for s in success]

        assert dtypes == [
            'float32',
            'float64',
            'int16',
            'int32',
            'uint8',
            'float32',
            'int16',
        ]
        assert lengths == [23494, 23493, 23495, 23494, 23497, 29016, 29017]

    def test_error(self):
        errors = []
        for w in WAVE_FILES:
            if w.stem in READABLE:
                errors.append([])
                wavemap.WaveMap(w, error=errors[-1].append)

        expected = [
            [],
            ['8 bytes after end-of-frame discarded'],
            [],
            [],
            [],
            ['7 bytes after end-of-frame discarded'],
            ['3 bytes after end-of-frame discarded'],
        ]

        assert errors == expected
