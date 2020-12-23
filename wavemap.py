import numbers
import numpy as np
import struct
import sys

__all__ = 'RawMap', 'WaveReadMap', 'WaveWriteMap', 'WaveMap'
__version__ = '0.8.0'

# See http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMATS = WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT

CHUNK_FORMAT = struct.Struct('<4s I')
assert CHUNK_FORMAT.size == 8

FMT_FORMAT = struct.Struct('<HHIIHH')
assert FMT_FORMAT.size == 16

FMT_BLOCK_LENGTHS = {16, 18, 40}

FLOAT_BITS_PER_SAMPLE = {32, 64}
PCM_BITS_PER_SAMPLE = {8, 16, 32, 64}

BITS_PER_SAMPLE = PCM_BITS_PER_SAMPLE, FLOAT_BITS_PER_SAMPLE

# Making 24 bits work transparently is probably impossible:
# https://stackoverflow.com/a/34128171/43839

# Deal with a quirk in certain .WAV test files
BAD_TAG_ADJUSTMENT = True

HEADER_FORMAT = struct.Struct('<4s I 4s 4s I H H I I H H')
assert HEADER_FORMAT.size == 36, f'{HEADER_FORMAT.size}'

FMT_FORMAT = struct.Struct('<H H I I H H')


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
                warn(f'{extra} bytes after end-of-frame discarded')

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


class WaveReadMap(RawMap):
    """"Memory-map an existing wave file into a numpy matrix"""

    def __new__(
        cls, filename, mode='r', order=None, always_2d=False, warn=warn
    ):
        offset, length, fmt = _metadata(filename, warn)

        (
            wFormatTag,
            nChannels,
            nSamplesPerSec,
            nAvgBytesPerSec,
            nBlockAlign,
            wBitsPerSample,
        ) = FMT_FORMAT.unpack(fmt[: FMT_FORMAT.size])

        if wFormatTag not in WAVE_FORMATS:
            raise ValueError(f'Do not understand wFormatTag={wFormatTag}')

        is_float = wFormatTag == WAVE_FORMAT_IEEE_FLOAT
        if wBitsPerSample not in BITS_PER_SAMPLE[is_float]:
            raise ValueError(f'Cannot mmap wBitsPerSample={wBitsPerSample}')

        if wBitsPerSample == 8:
            dtype = 'uint8'
        else:
            type_name = ('int', 'float')[is_float]
            dtype = f'{type_name}{wBitsPerSample}'

        assert np.dtype(dtype).itemsize == wBitsPerSample // 8

        self = RawMap.__new__(
            cls,
            filename,
            dtype,
            nChannels,
            offset,
            length,
            mode,
            None,
            order,
            always_2d,
            warn,
        )

        self.sample_rate = nSamplesPerSec
        return self


class WaveWriteMap(RawMap):
    """"Memory-map a new wave file"""

    def __new__(cls, filename, dtype, shape, sample_rate, warn=warn):
        dt = np.dtype(dtype)
        nChannels = 1 if len(shape) == 1 else min(shape)
        nSamples = max(shape)
        size = nChannels * nSamples * dt.itemsize

        if issubclass(dt.type, numbers.Integral):
            wFormatTag = WAVE_FORMAT_PCM
            fmt_cksize = 16
            fact_cksize = 0
        else:
            wFormatTag = WAVE_FORMAT_IEEE_FLOAT
            fmt_cksize = 18
            fact_cksize = 12

        cksize = size + size % 2 + fmt_cksize + fact_cksize
        wBitsPerSample = dt.itemsize * 8
        nAvgBytesPerSec = sample_rate * dt.itemsize * nChannels
        nBlockAlign = dt.itemsize * nChannels

        with open(filename, 'wb') as fp:

            def chunk(name, size):
                fp.write(CHUNK_FORMAT.pack(name, size))

            chunk(b'RIFF', cksize)
            fp.write(b'WAVE')

            chunk(b'fmt ', fmt_cksize)
            fp.write(
                FMT_FORMAT.pack(
                    wFormatTag,
                    nChannels,
                    sample_rate,
                    nAvgBytesPerSec,
                    nBlockAlign,
                    wBitsPerSample,
                )
            )

            if fact_cksize:
                fp.write(struct.pack('<H', 0))
                chunk(b'fact', 4)

            chunk(b'data', size)
            offset = fp.tell()

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
        self.sample_rate = sample_rate

        return self
        # TODO: handle that extra pad byte again!


def WaveMap(filename, mode='r', *args, **kwargs):
    """Return an instance of `WaveReadMap` or `WaveWriteMap`, depending on
    `mode`.

    See the documentation of these classes for full signatures.
    """
    if mode.startswith('w'):
        return WaveWriteMap(filename, *args, **kwargs)
    return WaveReadMap(filename, mode, *args, **kwargs)


def _file_size(filename):
    with open(filename, 'rb') as fp:
        fp.seek(0, 2)
        return fp.tell()


def _metadata(filename, warn):
    begin = end = fmt = None

    with open(filename, 'rb') as fp:
        (tag, _, _), *chunks = _chunks(fp, warn)
        if tag != b'WAVE':
            raise ValueError(f'Not a WAVE file: {tag}')

        for tag, b, e in chunks:
            if tag == b'fmt ':
                if not fmt:
                    b += CHUNK_FORMAT.size
                    fp.seek(b)
                    fmt = fp.read(e - b)
                else:
                    warn('fmt chunk after first ignored')
            elif tag == b'data':
                if not (begin or end):
                    begin, end = b, e
                else:
                    warn('data chunk after first ignored')

    if begin is None:
        raise ValueError('No data chunk found')

    if fmt is None:
        raise ValueError('No fmt chunk found')

    if len(fmt) not in FMT_BLOCK_LENGTHS:
        raise ValueError('Weird fmt block')

    if len(fmt) == 40:
        raise ValueError('Cannot read extensible format WAV files')

    return begin, end - begin, fmt


def _chunks(fp, warn):
    file_size = fp.seek(-1, 2)
    fp.seek(0)

    def read_one(format):
        s = fp.read(struct.calcsize(format))
        return struct.unpack('<' + format, s)[0]

    def read_tag():
        tag = read_one('4s')
        if tag and not tag.rstrip().isalnum():
            if BAD_TAG_ADJUSTMENT and tag[0] == 0:
                tag = tag[1:] + fp.read(1)
                if tag.rstrip().isalnum():
                    return tag

            warn(f'Dubious tag {tag}')

        return tag

    def read_int():
        return read_one('I')

    tag = read_tag()
    if tag != b'RIFF':
        raise ValueError('Not a RIFF file')

    size = read_int()
    yield read_tag(), 0, size

    while fp.tell() < file_size:
        begin = fp.tell()
        tag, chunk_size = read_tag(), read_int()
        fp.seek(chunk_size, 1)
        end = fp.tell()
        if end > file_size:
            if end > file_size + 1:
                warn(f'Incomplete chunk: {end} > {file_size + 1}')
            end = file_size
        yield tag, begin, end


if __name__ == '__main__':
    for i in sys.argv[1:]:
        mw = WaveMap(i)
        print(mw.shape)
        print(mw.length)
        print(mw.duration)
        print(mw)

    print('done')
