from .test_read import WAVE_FILES, READABLE
from numpy.testing import assert_array_equal
from pathlib import Path
import tdir
import unittest
import wavemap


class TestWaveWrite(unittest.TestCase):
    @tdir
    def test_write(self):
        filename = next(w for w in WAVE_FILES if 'int16' in w.stem)
        wm = wavemap.WaveMap(filename)
        assert wm.shape == (23493, 2)

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

        sb = b[: len(b2)]

        assert sb[:4] == b1[:4]
        assert sb[4:8] != b1[4:8]
        assert sb[8:] == b1[8:]

        import struct

        (s1,) = struct.unpack('<I', sb[4:8])
        (s2,) = struct.unpack('<I', b1[4:8])
        assert s1 == 94174
        assert s2 == 94008

    @tdir
    def test_int(self):
        for filename in WAVE_FILES:
            if not ('int' in filename.name and filename.name in READABLE):
                continue
            wm = wavemap.WaveMap(filename)

            tf1 = Path(filename.name)
            wm1 = wavemap.new_like(tf1, wm)
            assert_array_equal(wm, wm1)
            wm1.flush()

            tf2 = Path('2-' + filename.name)
            wm2 = wavemap.new_like(tf2, wm)
            assert_array_equal(wm, wm2)
            wm2.flush()

            b, b1, b2 = (
                filename.read_bytes(),
                tf1.read_bytes(),
                tf2.read_bytes(),
            )
            assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
            assert b1 == b2
            assert b

            sb = b[: len(b2)]

            assert sb[:4] == b1[:4]
            assert sb[4:8] != b1[4:8]
            assert sb[8:] == b1[8:]

            import struct

            (s1,) = struct.unpack('<I', sb[4:8])
            (s2,) = struct.unpack('<I', b1[4:8])
            assert s1 - s2 == 166 == 0xA6

    @tdir
    def test_float(self):
        for filename in WAVE_FILES:
            if not ('float' in filename.name and filename.name in READABLE):
                continue
            wm = wavemap.WaveMap(filename)

            tf1 = Path(filename.name)
            wm1 = wavemap.new_like(tf1, wm)
            assert_array_equal(wm, wm1)
            wm1.flush()

            tf2 = Path('2-' + filename.name)
            wm2 = wavemap.new_like(tf2, wm)
            assert_array_equal(wm, wm2)
            wm2.flush()

            b, b1, b2 = (
                filename.read_bytes(),
                tf1.read_bytes(),
                tf2.read_bytes(),
            )
            assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
            assert b1 == b2
            assert b

            # sb = b[: len(b2)]
            # differs = [i for i, (x, y) in enumerate(zip(sb, b2)) if x != y]
            # # Should be zero!
            # assert len(differs) == 1355, f'{len(sb)}'
