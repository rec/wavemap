from numpy.testing import assert_array_equal
import numpy as np
import unittest
import wavemap


class TestConvert(unittest.TestCase):
    def test_convert(self):
        u8 = np.array(range(256), 'uint8')

        def conv(x, dtype):
            ar = wavemap.convert(x, dtype)
            co = wavemap.convert(ar, 'uint8')
            try:
                assert_array_equal(co, u8)
            except Exception:
                print('BEFORE', ar)
                print('AFTER', co)
                raise
            return ar

        u16 = conv(u8, 'uint16')

        conv(u8, 'int8')
        u16 = conv(u8, 'uint16')
        assert 0x80 == np.amin(u16)
        assert 0xFF80 == np.amax(u16)

        conv(u8, 'int8')

        f32 = conv(u8, 'float32')
        assert np.amin(f32) == -1
        assert np.amax(f32) == 1

        f64 = conv(u8, 'float64')
        assert np.amin(f64) == -1
        assert np.amax(f64) == 1
