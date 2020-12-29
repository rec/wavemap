import numpy as np
import sys


def warn(msg):
    print(msg, file=sys.stderr)


class RawMap(np.memmap):
    """"Memory map raw audio data from a disk file into a numpy matrix"""

    def __new__(
        cls,
        filename,
        dtype,
        channels,
        offset=0,
        length=None,
        mode='r',
        shape=None,
        order=None,
        always_2d=False,
        warn=warn,
    ):
        dt = np.dtype(dtype)
        bytes_per_frame = dt.itemsize * channels

        if 'w' in mode:
            mode = 'w+'
            if shape:
                if length and warn:
                    warn('Setting shape overrides length')
                order = order or 'FC'[max(shape) == shape[0]]

            elif length is None:
                raise ValueError('One of `length` or `shape` must be set')

        elif length is None and shape is None:
            length = _file_size(filename) - offset

        order = order or 'C'

        if not shape:
            frames = length // bytes_per_frame
            extra = length % bytes_per_frame
            if extra and warn:
                s = '' if extra == 1 else 's'
                warn(f'{extra} byte{s} after end-of-frame discarded')

            if channels == 1 and not always_2d:
                shape = (frames,)
            elif order == 'C':
                shape = frames, channels
            elif order == 'F':
                shape = channels, frames
            else:
                raise ValueError(f'Bad order "{order}"')

        self = np.memmap.__new__(cls, filename, dt, mode, offset, shape, order)

        self.order = order
        self.channnels = channels
        self.length = length

        return self

    @property
    def duration(self):
        return max(self.shape) / self.sample_rate


def _file_size(filename):
    with open(filename, 'rb') as fp:
        fp.seek(0, 2)
        return fp.tell()
