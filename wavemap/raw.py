from . import docs
from .memmap import memmap
from numpy.lib.stride_tricks import as_strided
from typing import Callable, Optional, Union
import numpy as np
import sys

int24 = 'int24'


def warn(msg):
    print(msg, file=sys.stderr)


class RawMap(memmap):
    """"Memory map raw audio data from a disk file into a numpy matrix"""

    @docs.update
    def __new__(
        cls,
        filename: str,
        dtype: np.dtype,
        shape: Union[tuple, int, None] = None,
        mode: str = 'r',
        offset: int = 0,
        roffset: int = 0,
        order: Optional[str] = None,
        always_2d: bool = False,
        allow_conversion: bool = True,
        warn: Optional[Callable] = warn,
    ):
        """Memory map raw audio data from a disk file into a numpy matrix"""
        # Documentation for parameters is in docs.py

        def new(shape=shape, dtype=dtype, order=order, mode=mode):
            return memmap.__new__(
                cls, filename, dtype, mode, offset, shape, order, roffset
            )

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
            return new(mode='w+', order=order)

        if str(dtype) == int24:
            itemsize = 3
        else:
            itemsize = np.dtype(dtype).itemsize

        file_size = file_byte_size(filename)
        audio_size = file_size - offset - roffset
        shape = _get_shape(shape, audio_size, itemsize, order, always_2d, warn)
        if itemsize != 3:
            return new(shape=shape)

        frames = shape[0] * (shape[1] if len(shape) else 1)
        assert not (frames % 4)

        # https://stackoverflow.com/a/34128171/4383
        raw = new(shape=(itemsize * frames // 4,), dtype='int32')
        strided = as_strided(raw, strides=(12, 3,), shape=(frames, 4))
        reshaped = np.reshape(strided, shape=shape)

        if not allow_conversion:
            return reshaped

        result = reshaped & 0x00FFFFFF
        result *= 0x100
        return result


def file_byte_size(filename: str):
    with open(filename, 'rb') as fp:
        return fp.seek(0, 2)


def _get_shape(shape, audio_size, itemsize, order, always_2d, warn):
    channels, *rest = sorted(shape or (1,))
    frames_requested = rest and rest[0] or 0

    if itemsize == 3:
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

    if channels == 1 and not always_2d:
        return (frames,)

    if not order or order == 'C':
        return frames, channels

    return channels, frames
