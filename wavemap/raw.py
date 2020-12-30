from .memmap import memmap
import numpy as np
import sys


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
        warn=warn,
    ):
        assert offset >= 0 and not roffset or roffset >= 0
        dtype = np.dtype(dtype)

        if 'w' in mode:
            if shape is None:
                raise ValueError('`shape` must be set')
            mode = 'w+'

        elif not shape:
            if not channel_count:
                raise ValueError('One of channel_count and shape must be set')

            sample_bytes = dtype.itemsize
            frame_bytes = sample_bytes * channel_count

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
            cls, filename, dtype, mode, offset, shape, order, roffset
        )
        self.order = order
        self.channnel_count = channel_count
        self.roffset = roffset

        return self


def file_byte_size(filename):
    with open(filename, 'rb') as fp:
        return fp.seek(0, 2)


def dump_locals():
    from numbers import Number

    for k, v in locals().items():
        if isinstance(v, (Number, tuple, str)):
            print(f'{k} = {v!r}')
