from . import constants
from .raw import warn, RawMap
import numpy as np
import struct

FLOAT_BITS_PER_SAMPLE = {32, 64}
PCM_BITS_PER_SAMPLE = {8, 16, 32, 64}

BITS_PER_SAMPLE = PCM_BITS_PER_SAMPLE, FLOAT_BITS_PER_SAMPLE
FMT_BLOCK_LENGTHS = {16, 18, 20, 40}

# Deal with a quirk in certain .WAV test files
BAD_TAG_ADJUSTMENT = True


class ReadMap(RawMap):
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
        ) = constants.FMT_FORMAT.unpack(fmt[: constants.FMT_FORMAT.size])

        if wFormatTag not in constants.WAVE_FORMATS:
            raise ValueError(f'Do not understand wFormatTag={wFormatTag}')

        is_float = wFormatTag == constants.WAVE_FORMAT_IEEE_FLOAT
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


def _metadata(filename, warn):
    begin = end = fmt = None

    with open(filename, 'rb') as fp:
        file_size = fp.seek(-1, 2)

    with open(filename, 'rb') as fp:
        (tag, b, e), *chunks = _chunks(fp, warn)
        if tag != b'WAVE':
            raise ValueError(f'Not a WAVE file: {tag}')
        assert b == 0
        print('chsize =', e)
        print('file_size =', file_size)

        for tag, b, e in chunks:
            if tag == b'fmt ':
                if not fmt:
                    b += constants.CHUNK_FORMAT.size
                    fp.seek(b)
                    fmt = fp.read(e - b)
                else:
                    warn('fmt chunk after first ignored')
            elif tag == b'data':
                if not (begin or end):
                    b += constants.CHUNK_FORMAT.size
                    begin, end = b, e
                else:
                    warn('data chunk after first ignored')

    if begin is None:
        raise ValueError('No data chunk found')

    if fmt is None:
        raise ValueError('No fmt chunk found')

    if len(fmt) not in FMT_BLOCK_LENGTHS:
        error = f'Weird fmt block length {len(fmt)}'
        warn(error)
        if False:
            raise ValueError(error)

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
