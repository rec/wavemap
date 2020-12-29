"""
🌊 Memory map WAVE files into numpy arrays 🌊

The actual samples from a WAVE file appear as entries in a numpy array.

See documentation for numpy.memmap

If you open the file in 'r+' mode, you can even rewrite the samples on
disk that way.

"""


from . import constants
from .raw import warn, RawMap
from .read import ReadMap as WaveReadMap
import io
import numpy as np
import struct

__all__ = 'RawMap', 'WaveReadMap', 'WaveWriteMap', 'WaveMap'
__version__ = '0.9.1'


class WaveWriteMap(RawMap):
    """"Memory-map a new wave file"""

    @classmethod
    def new_like(cls, filename, arr, sample_rate=None, length=None, warn=warn):
        sample_rate = sample_rate or getattr(arr, 'sample_rate', None)
        if not sample_rate:
            raise ValueError('sample_rate must be set')

        wm = cls(filename, arr.dtype, arr.shape, sample_rate, length, warn)
        np.copyto(dst=wm, src=arr, casting='no')
        return wm

    def __new__(
        cls, filename, dtype, shape, sample_rate, length=None, warn=warn
    ):
        dt = np.dtype(dtype)
        nChannels = 1 if len(shape) == 1 else min(shape)
        nSamples = max(shape)
        size = nChannels * nSamples * dt.itemsize
        cksize = size + size % 2

        if issubclass(dt.type, np.integer):
            wFormatTag = constants.WAVE_FORMAT_PCM
            fmt_cksize = 16
            fact_cksize = 0
            cksize += 36
        else:
            wFormatTag = constants.WAVE_FORMAT_IEEE_FLOAT
            fmt_cksize = 18
            fact_cksize = 12
            cksize += 48

        wBitsPerSample = dt.itemsize * 8
        nAvgBytesPerSec = sample_rate * dt.itemsize * nChannels
        nBlockAlign = dt.itemsize * nChannels

        fp = io.BytesIO()

        def chunk(name, size):
            fp.write(constants.CHUNK_FORMAT.pack(name, size))

        chunk(b'RIFF', cksize)
        fp.write(b'WAVE')

        chunk(b'fmt ', fmt_cksize)
        fp.write(
            constants.FMT_FORMAT.pack(
                wFormatTag,
                nChannels,
                sample_rate,
                nAvgBytesPerSec,
                nBlockAlign,
                wBitsPerSample,
            )
        )

        if fact_cksize:
            print('YES')
            fp.write(struct.pack('<H', 0))
            chunk(b'fact', 4)
        else:
            print('NO')

        chunk(b'data', size)
        offset = fp.tell()
        print('XXX', offset, size, cksize, fmt_cksize, fact_cksize)

        s1, *s2 = shape
        s2 = s2 and s2[0] or 1
        length = s1 * s2

        self = RawMap.__new__(
            cls,
            filename,
            dtype,
            nChannels,
            offset,
            length,
            'w+',
            shape,
            None,
            False,
            warn,
        )

        assert offset == len(fp.getvalue())
        self._mmap[:offset] = fp.getvalue()
        self.sample_rate = sample_rate

        return self
        # TODO: handle that extra pad byte again!


new_like = WaveWriteMap.new_like


def WaveMap(filename, mode='r', *args, **kwargs):
    """Return an instance of `WaveReadMap` or `WaveWriteMap`, depending on
    `mode`.

    See the documentation of these classes for full signatures.
    """
    if mode.startswith('w'):
        return WaveWriteMap(filename, *args, **kwargs)
    return WaveReadMap(filename, mode, *args, **kwargs)
