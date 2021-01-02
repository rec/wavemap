from . import files
from pathlib import Path
import stroll
import unittest
import wavemap

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


class TestWaveMap(unittest.TestCase):
    def test_snare(self):
        wavemap.WaveMap(next(files.find('Kick')))

    def test_existing(self):
        success, failure = [], []
        for f in files.WAVE_FILES:
            try:
                success.append(wavemap.WaveMap(f))
            except Exception as e:
                if not True:
                    raise
                failure.append((f.stem, e.args[0]))

        filenames = [s.filename.name for s in success]
        assert filenames == files.READABLE
        dtypes = [str(s.dtype) for s in success]
        lengths = [s.shape[0] for s in success]

        assert dtypes == [
            'int16',
            'float32',
            'int16',
            'int16',
            'float32',
            'float32',
            'float64',
            'int16',
            'int32',
            'uint8',
            'float32',
            'int16',
        ]
        assert lengths == [
            10482,
            3131,
            10288,
            296109,
            441,
            23493,
            23493,
            23493,
            23493,
            23493,
            29016,
            29016,
        ]

    def test_warnings(self):
        warnings = []
        for w in WAVE_FILES:
            if w.name in READABLE:
                warnings.append([])
                wavemap.WaveMap(w, warn=warnings[-1].append)

        expected = [['WAVE cksize is wrong: 42074 != 42082']]
        expected += [[]] * (len(warnings) - 1)
        assert warnings == expected

    def test_error(self):
        with self.assertRaises(ValueError) as m:
            wavemap.WaveMap(__file__)
        assert m.exception.args[0] == 'Not a RIFF file'
