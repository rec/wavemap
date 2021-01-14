from . import files
from numpy.testing import assert_array_equal
from pathlib import Path
import struct
import tdir
import unittest
import wavemap


class TestWaveWrite(unittest.TestCase):
    def test_write1(self):
        wm = wavemap(next(files.find('int16')))
        assert wm.shape == (23493, 2)

    @tdir
    def test_write2(self):
        wm, (b, b1, b2) = _find('int16', not True)
        assert wm[0].shape == (23493, 2)
        assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
        assert b1 == b2
        assert b

        sb = b[: len(b2)]

        assert sb[:4] == b1[:4]
        assert sb[4:8] != b1[4:8]
        if True:
            return
        assert sb[8:-1] == b1[8:-1]

        import struct

        (s1,) = struct.unpack('<I', sb[4:8])
        (s2,) = struct.unpack('<I', b1[4:8])
        assert s1 != s2
        assert s1 == 94174
        assert s2 == 94008
        # assert s1 - s2 == 0x9E == 158

    @tdir
    def test_int(self):
        for filename in files.find('int'):
            (wm, wm1, wm2), (b, b1, b2) = _test(filename)
            assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
            assert b1 == b2
            assert b

            sb = b[: len(b2)]

            assert sb[:4] == b1[:4]
            assert sb[4:8] != b1[4:8]
            if True:
                return

            if not sb[8:-1] == b1[8:-1]:
                assert False, 'binaries differ'

            (s1,) = struct.unpack('<I', sb[4:8])
            (s2,) = struct.unpack('<I', b1[4:8])
            assert s1 != s2

    @tdir
    def test_float(self):
        for filename in files.find('float'):
            # print(filename)
            (wm, wm1, wm2), (b, b1, b2) = _test(filename)
            assert len(b1) == len(b2), f'{len(b1)} == {len(b2)}'
            assert b1 == b2
            assert b

            # sb = b[: len(b2)]
            # differs = [i for i, (x, y) in enumerate(zip(sb, b2)) if x != y]
            # # Should be zero!
            # assert len(differs) == 1355, f'{len(sb)}'


def _find(s, hard=False):
    return _test(next(files.find(s)), hard)


def _test(filename, hard=False, assert_array_equal=assert_array_equal):
    wm1 = wavemap(filename)

    localfile = Path(filename.name)
    wm2 = wavemap.copy_to(wm1, localfile)
    assert_array_equal(wm1, wm2)
    wm2.flush()

    localfile2 = Path(f'{filename.stem}-2{filename.suffix}')
    wm3 = wavemap.copy_to(wm2, localfile2)
    assert_array_equal(wm1, wm3)
    wm3.flush()

    wm = wm1, wm2, wm3
    b = tuple(i.filename.read_bytes() for i in wm)
    file_sizes = tuple(w.filename.stat().st_size for w in wm)
    byte_sizes = tuple(8 + struct.unpack('<I', i[4:8])[0] for i in b)

    if hard:
        assert file_sizes == byte_sizes
        assert wm1.shape == wm2.shape == wm3.shape
    else:
        # This is a bit silly - we're measuring how much stuff we find in files
        assert max(abs(f - b) for f, b in zip(file_sizes, byte_sizes)) <= 188

    return wm, b
