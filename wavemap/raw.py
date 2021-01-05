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
        if offset < 0 or roffset < 0:
            raise ValueError('offset and roffset must be non-negative')

        is_write = 'w' in mode
        if is_write:
            mode = 'w+'

        if not shape:
            if is_write:
                raise ValueError('Must set a shape in write mode')
            shape = (1,)

        if isinstance(shape, int):
            shape = (shape,)

        if not (1 <= len(shape) <= 2):
            raise ValueError('Wave files must have 1 or 2 dimensions')

        is_int24 = str(dtype) == int24
        dt = np.dtype('uint8' if is_int24 else dtype)

        if is_write:
            mode = 'w+'
            order = order or 'FC'[max(shape) == shape[0]]
            channels = min(shape)

        else:
            channels, *rest = sorted(shape)
            frames_requested = rest and rest[0] or 0

            if is_int24:
                channels *= 3

            file_size = file_byte_size(filename)
            audio_size = file_size - offset - roffset
            frame_size = dt.itemsize * channels
            frame_count = audio_size // frame_size

            if frames_requested and frames_requested < frame_count:
                warn(f'Requested {frames_requested} frames, got {frame_count}')
                frame_count = frames_requested
            elif warn:
                extra = audio_size % frame_size
                if extra:
                    s = '' if extra == 1 else 's'
                    warn(f'{extra} byte{s} after end-of-frame discarded')

            order = order or 'C'

            if channels == 1 and not always_2d:
                shape = (frame_count,)
            elif order == 'C':
                shape = frame_count, channels
            elif order == 'F':
                shape = channels, frame_count
            else:
                raise ValueError(f'Bad order "{order}"')

        self = memmap.__new__(
            cls, filename, dt, mode, offset, shape, order, roffset
        )

        self.order = order
        self.channels = channels
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
