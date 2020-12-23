from struct import unpack_from, calcsize
import numpy as np
import sys

__all__ = 'RawMap', 'WaveMap', 'QUIET'
__version__ = '0.8.0'

QUIET = False
BAD_TAG_ADJUSTMENT = True


def warn(*args, **kwargs):
    if not QUIET:
        print(*args, **kwargs, file=sys.stderr)


class RawMap(np.memmap):
    """"Memory map raw audio data from a disk file into a numpy matrix"""

    def __new__(
        cls,
        filename,
        dtype,
        channels,
        begin=0,
        end=None,
        mode='r',
        order='C',
        always_2d=False,
        warn=warn,
    ):
        if end is None:
            with open(filename, 'rb') as fp:
                fp.seek(-1, 2)
                end = fp.tell()

        dt = np.dtype(dtype)
        bytes_per_frame = dt.itemsize * channels

        frames = (end - begin) // bytes_per_frame
        extra = (end - begin) % bytes_per_frame
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

        self = np.memmap.__new__(cls, filename, dt, mode, begin, shape, order)

        self.order = order
        self.channnels = channels

        return self

    @property
    def duration(self):
        return max(self.shape) / self.sample_rate


class WaveMap(RawMap):
    """"Memory-map a wave file into a numpy matrix"""

    def __new__(
        cls, filename, mode='r', order='C', always_2d=False, warn=warn
    ):
        begin, end, fmt = _metadata(filename, warn)

        (
            wFormatTag,
            nChannels,
            nSamplesPerSec,
            nAvgBytesPerSec,
            nBlockAlign,
            wBitsPerSample,
        ) = unpack_from(FMT_FORMAT, fmt[:FMT_LENGTH])

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
            begin,
            end,
            mode,
            order,
            always_2d,
            warn,
        )
        self.begin = begin
        self.end = end
        self.sample_rate = nSamplesPerSec

        return self


# See http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMATS = {WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT}

HEADER_LENGTH = 8
FMT_FORMAT = '<HHIIHH'
FMT_LENGTH = calcsize(FMT_FORMAT)
assert FMT_LENGTH == 16

FMT_BLOCK_LENGTHS = {16, 18, 40}

FLOAT_BITS_PER_SAMPLE = {32, 64}
PCM_BITS_PER_SAMPLE = {8, 16, 32, 64}

BITS_PER_SAMPLE = PCM_BITS_PER_SAMPLE, FLOAT_BITS_PER_SAMPLE

# Making 24 bits work transparently is probably impossible:
# https://stackoverflow.com/a/34128171/43839


def _metadata(filename, warn):
    begin = end = fmt = None

    with open(filename, 'rb') as fp:
        (tag, _, _), *chunks = _chunks(fp, warn)
        if tag != b'WAVE':
            raise ValueError(f'Not a WAVE file: {tag}')

        for tag, b, e in chunks:
            if tag == b'fmt ':
                if not fmt:
                    b += HEADER_LENGTH
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

    return begin, end, fmt


def _chunks(fp, warn):
    file_size = fp.seek(-1, 2)
    fp.seek(0)

    def read_one(format):
        return unpack_from('<' + format, fp.read(calcsize(format)))[0]

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
        raise ValueError(f'Not a RIFF file: {tag}')

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
