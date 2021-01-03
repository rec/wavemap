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
        mode='r',
        shape=None,  # For writing
        channel_count=None,  # For reading
        offset=0,
        roffset=None,
        order=None,
        always_2d=False,
        allow_conversion=True,
        warn=warn,
    ):
        if (channel_count is None) == (shape is None):
            raise ValueError('One of channel_count or shape must be set')

        if offset < 0 or roffset and roffset < 0:
            raise ValueError('offset and roffset must be non-negative')

        is_int24 = isinstance(dtype, str) and dtype == int24
        dt = np.dtype('uint8' if is_int24 else dtype)

        if 'w' in mode:
            if shape is None:
                raise ValueError('`shape` must be set in write mode')
            mode = 'w+'

        elif not shape:
            if is_int24:
                channel_count *= 3

            frame_bytes = dt.itemsize * channel_count

            audio_bytes = file_byte_size(filename) - offset - roffset
            frame_count = audio_bytes // frame_bytes

            extra = audio_bytes % frame_bytes
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

        else:
            cc = channel_count
            if len(shape) == 1:
                frame_count = shape[0]
                channel_count = 1

            elif len(shape) == 2:
                frame_count, channel_count = max(shape), min(shape)

            else:
                raise ValueError('Wave files can only have 1 or 2 dimensions')
            if cc is not None and cc != channel_count:
                warn('Setting shape overrides channel_count')

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
