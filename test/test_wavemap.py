from numpy.testing import assert_array_equal
from pathlib import Path
import stroll
import tdir
import unittest
import wavemap

WAVE_FILES = list(stroll(Path(__file__).parent, suffix='.wav'))
READABLE = [
    'M1F1-float32-AFsp.wav',
    'M1F1-float64-AFsp.wav',
    'M1F1-int16-AFsp.wav',
    'M1F1-int32-AFsp.wav',
    'M1F1-uint8-AFsp.wav',
    'stereofl.wav',
    'stereol.wav',
]


class TestWaveMap(unittest.TestCase):
    def test_existing(self):
        success, failure = [], []
        for w in WAVE_FILES:
            try:
                success.append(wavemap.WaveMap(w))
            except Exception as e:
                failure.append((w.stem, e.args[0]))

        filenames = [s.filename.name for s in success]
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

    def test_warnings(self):
        warnings = []
        for w in WAVE_FILES:
            if w.name in READABLE:
                warnings.append([])
                wavemap.WaveMap(w, warn=warnings[-1].append)

        expected = [
            [],
            ['8 bytes after end-of-frame discarded'],
            [],
            [],
            [],
            ['7 bytes after end-of-frame discarded'],
            ['3 bytes after end-of-frame discarded'],
        ]

        assert warnings == expected

    def test_error(self):
        with self.assertRaises(ValueError) as m:
            wavemap.WaveMap(__file__)
        assert m.exception.args[0] == 'Not a RIFF file'


@tdir
class TestWaveWrite(unittest.TestCase):
    def test_write(self):
        filename = next(w for w in WAVE_FILES if 'int16' in w.stem)
        wm = wavemap.WaveMap(filename)
        assert wm.shape == (23495, 2)

        tf1 = Path(filename.name)
        wm1 = wavemap.new_like(tf1, wm)
        assert_array_equal(wm, wm1)
        wm1.flush()

        tf2 = Path('2-' + filename.name)
        wm2 = wavemap.new_like(tf2, wm)
        assert_array_equal(wm, wm2)
        wm2.flush()

        b, b1, b2 = filename.read_bytes(), tf1.read_bytes(), tf2.read_bytes()
        assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
        assert b1 == b2
        assert b
