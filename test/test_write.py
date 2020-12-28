from .test_read import WAVE_FILES, READABLE
from numpy.testing import assert_array_equal
from pathlib import Path
import tdir
import unittest
import wavemap


class TestWaveWrite(unittest.TestCase):
    @tdir
    def test_write(self):
        wm, (b, b1, b2) = _find('int16')
        assert wm[0].shape == (23493, 2)
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
        assert s2 == 94016

    @tdir
    def test_int(self):
        for filename in WAVE_FILES:
            if not ('int' in filename.name and filename.name in READABLE):
                continue
            (wm, wm1, wm2), (b, b1, b2) = _test(filename)
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
            assert s1 - s2 == 158 == 0x9E  # ???

    @tdir
    def test_float(self):
        for filename in WAVE_FILES:
            if not ('float' in filename.name and filename.name in READABLE):
                continue
            (wm, wm1, wm2), (b, b1, b2) = _test(filename)
            assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
            assert b1 == b2
            assert b

            # sb = b[: len(b2)]
            # differs = [i for i, (x, y) in enumerate(zip(sb, b2)) if x != y]
            # # Should be zero!
            # assert len(differs) == 1355, f'{len(sb)}'


def _find(s):
    fname = next(w for w in WAVE_FILES if w.name in READABLE and s in w.name)
    return _test(fname)


def _test(filename):
    wm1 = wavemap.WaveMap(filename)

    localfile = Path(filename.name)
    wm2 = wavemap.new_like(localfile, wm1)
    assert_array_equal(wm1, wm2)
    wm2.flush()

    localfile2 = Path(f'{filename.stem}-2{filename.suffix}')
    wm3 = wavemap.new_like(localfile2, wm2)
    assert_array_equal(wm1, wm3)
    wm3.flush()

    wm = wm1, wm2, wm3
    b = tuple(i.filename.read_bytes() for i in wm)
    return wm, b
