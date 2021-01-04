# from numpy.lib.stride_tricks import as_strided
from .memmap import memmap
import numpy as np
import sys

int24 = 'int24'


def warn(msg):
    print(msg, file=sys.stderr)


class RawMap(memmap):
    """"Memory map raw audio data from a disk file into a numpy matrix"""

    def __new__(
        cls,
        filename,
        dtype,
        shape=None,
        mode='r',
        offset=0,
        roffset=0,
        order=None,
        always_2d=False,
        allow_conversion=True,
        warn=warn,
    ):
        if not shape:
            if 'w' in mode:
                raise ValueError('Must set a shape in write mode')
            shape = (1,)
        elif isinstance(shape, int):
            shape = (shape,)
        if not (1 <= len(shape) <= 2):
            raise ValueError('Wave files must have 1 or 2 dimensions')


        channel_count, frame_count = sorted((shape + (1,))[:2])

        if offset < 0 or roffset < 0:
            raise ValueError('offset and roffset must be non-negative')

        is_int24 = isinstance(dtype, str) and dtype == int24
        dt = np.dtype('uint8' if is_int24 else dtype)

        if 'w' in mode:
            mode = 'w+'

        else:
            if is_int24:
                channel_count *= 3

            frame_size = dt.itemsize * channel_count
            file_size = file_byte_size(filename)

            audio_size = file_size - offset - roffset
            frame_count = audio_size // frame_size

            extra = audio_size % frame_size
            if extra and warn:
                s = '' if extra == 1 else 's'
                warn(f'{extra} byte{s} after end-of-frame discarded')

            order = order or 'C'

            if channel_count == 1 and not always_2d:
                shape = (frame_count,)
            elif order == 'C':
                shape = frame_count, channel_count
            elif order == 'F':
                shape = channel_count, frame_count
            else:
                raise ValueError(f'Bad order "{order}"')

        order = order or 'FC'[max(shape) == shape[0]]

        self = memmap.__new__(
            cls, filename, dt, mode, offset, shape, order, roffset
        )

        self.order = order
        self.channnel_count = channel_count
        self.roffset = roffset

        if is_int24 and allow_conversion:
            length = max(self.shape)
            length -= length % 12

        return self


def file_byte_size(filename):
    with open(filename, 'rb') as fp:
        return fp.seek(0, 2)


def dump_locals():
    from numbers import Number

    for k, v in locals().items():
        if isinstance(v, (Number, tuple, str)):
            print(f'{k} = {v!r}')
