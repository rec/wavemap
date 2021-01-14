from . import files
from numpy.testing import assert_array_equal
from pathlib import Path
import numpy as np
import os
import subprocess
import tdir
import unittest
import wavemap

IS_TRAVIS = os.getenv('TRAVIS', '').lower().startswith('t')
skip_if_travis = unittest.skipIf(IS_TRAVIS, 'Test does not work in travis')


@skip_if_travis
class TestCanonical(unittest.TestCase):
    @tdir
    def FAILED_test_canonical(self):
        # ffmpeg writes files in extended format when I try to write
        # floating point!
        for infile in files.find():
            # print('-->', infile)
            w_in = wavemap(infile)

            outfile = Path(infile.name)
            assert outfile.suffix == '.wav'
            fmt = _to_format(w_in.dtype)
            canonical(infile, outfile, fmt)

            w_out = wavemap(outfile)
            assert w_in.sample_rate == w_out.sample_rate
            assert w_in.dtype == w_out.dtype

            if w_in.shape != w_out.shape:
                li, ci, lo, co = w_in.shape + w_out.shape
                assert ci == co, 'Channels'
                assert li > lo
                assert li - lo < 2

                w_in = w_in[:-1, :]

            assert_array_equal(w_in, w_out)


def canonical(i, o, fmt):
    o.parent.mkdir(parents=True, exist_ok=True)
    cmd = (
        'ffmpeg',
        '-y',
        '-i',
        str(i.absolute()),
        '-c:a',
        'pcm_' + fmt,
        str(o.absolute()),
    )
    print('$', *cmd)
    subprocess.run(cmd)


# https://trac.ffmpeg.org/wiki/audio%20types


def _to_format(dt, big_endian=False):
    if issubclass(dt.type, np.signedinteger):
        ntype = 's'
    elif issubclass(dt.type, np.unsignedinteger):
        ntype = 'u'
    else:
        ntype = 'f'

    bits = dt.itemsize * 8
    endian = '' if bits == 8 else 'be' if big_endian else 'le'
    return f'{ntype}{bits}{endian}'


if __name__ == '__main__':
    pass
