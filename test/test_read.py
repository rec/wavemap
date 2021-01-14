from . import files
import unittest
import wavemap


class TestWaveMap(unittest.TestCase):
    def test_snare(self):
        wavemap(next(files.find('Kick')))

    def test_existing(self):
        success, failure = [], []
        for f in files.WAVE_FILES:
            try:
                success.append(wavemap(f))
            except Exception as e:
                if not True:
                    raise
                failure.append((f.stem, e.args[0]))

        filenames = [s.filename.name for s in success]
        assert filenames == files.READABLE
        dtypes = [str(s.dtype) for s in success]
        lengths = [s.shape[0] for s in success]

        print(f'assert dtypes == {dtypes}')
        print(f'assert lengths == {lengths}')

        assert dtypes == [
            'int16',
            'float32',
            'int16',
            'int16',
            'float32',
            'float32',
            'float32',
            'float64',
            'float64',
            'int16',
            'int16',
            'int16',
            'int32',
            'int32',
            'uint8',
            'uint8',
            'int16',
            'int16',
            'int16',
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
            23493,
            23493,
            23493,
            23493,
            23493,
            23493,
            257411,
            169031,
            105507,
            29016,
            29016,
        ]

    def test_warnings(self):
        warnings = []
        for w in files.find():
            warnings.append([])
            wavemap(w, warn=warnings[-1].append)

        first, *rest = warnings

        assert first == ['WAVE cksize is wrong: 42074 != 42082']
        assert all(i == [] for i in rest)

    def test_error(self):
        with self.assertRaises(ValueError) as m:
            wavemap(__file__)
        assert m.exception.args[0] == 'Not a RIFF file'
