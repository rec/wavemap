# from numpy.lib.stride_tricks import as_strided
from .memmap import memmap
from numpy.lib.stride_tricks import as_strided
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

        if order not in ('C', 'F', None):
            raise ValueError(f'Bad order "{order}"')

        if isinstance(shape, int):
            shape = (shape,)

        if not (shape is None or 1 <= len(shape) <= 2):
            raise ValueError('Wave files must have 1 or 2 dimensions')

        if 'w' in mode:
            if not shape:
                raise ValueError('Must set a shape in write mode')
            order = order or 'FC'[max(shape) == shape[0]]

            return memmap.__new__(
                cls, filename, dtype, 'w+', offset, shape, order, roffset
            )

        is_int24 = str(dtype) == int24
        if is_int24:
            dt = np.dtype('uint8')
            itemsize = 3
            frame_scale = 3
        else:
            dt = np.dtype(dtype)
            itemsize = dt.itemsize
            frame_scale = 1

        channels, *rest = sorted(shape or (1,))
        frames_requested = rest and rest[0] or 0

        file_size = file_byte_size(filename)
        audio_size = file_size - offset - roffset
        if is_int24:
            extra = audio_size % 12
            if extra and warn:
                s = 's' if len(extra) != 1 else ''
                warn(f'24-bit conversion lost last {extra} byte{s}, sorry')
            audio_size -= extra

        frame_size = itemsize * channels
        frames = audio_size // frame_size

        if frames_requested and frames_requested < frames:
            warn(f'Requested {frames_requested} frames, got {frames}')
            frames = frames_requested

        if warn:
            extra = audio_size % frame_size
            if extra:
                s = '' if extra == 1 else 's'
                warn(f'{extra} byte{s} after end-of-frame discarded')

        order = order or 'C'

        if channels == 1 and not always_2d:
            shape = (frames * frame_scale,)
        elif order == 'C':
            shape = frames, channels * frame_scale
        else:
            shape = channels * frame_scale, frames

        self = memmap.__new__(
            cls, filename, dt, mode, offset, shape, order, roffset
        )

        if is_int24 and allow_conversion:
            # https://stackoverflow.com/a/34128171/4383

            # length -= length % 12
            # rawbytes = rawdatamap[:length]

            # realdata = as_strided(
            #     rawbytes.view(np.int32), strides=(12, 3,), shape=(frames, 4)
            # )

            # someusefulpart = (
            #   realdata[hugeoffset : hugeoffset + smallerthanram] & 0x00FFFFFF
            # )
            assert as_strided

        return self


def file_byte_size(filename):
    with open(filename, 'rb') as fp:
        return fp.seek(0, 2)


def dump_locals():
    from numbers import Number

    for k, v in locals().items():
        if isinstance(v, (Number, tuple, str)):
            print(f'{k} = {v!r}')
