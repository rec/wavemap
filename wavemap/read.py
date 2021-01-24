from . import docs, raw
from .structure import wave
from typing import Callable, Optional, Type
import numpy as np
import struct

FLOAT_BITS_PER_SAMPLE = {32, 64}
PCM_BITS_PER_SAMPLE = {8, 16, 24, 32, 64}

BITS_PER_SAMPLE = PCM_BITS_PER_SAMPLE, FLOAT_BITS_PER_SAMPLE
FMT_BLOCK_LENGTHS = {16, 18, 20, 40}
MODES = 'r', 'r+', 'c'

# Deal with a quirk in certain .WAV test files
BAD_TAG_ADJUSTMENT = True


class ReadMap(raw.RawMap):
    """Memory-map an existing WAVE file into a numpy vector or matrix"""

    @docs.update(mode='READ_ONLY_MODE')
    def __new__(
        cls: Type,
        filename: str,
        mode: str = 'r',
        order: Optional[str] = None,
        always_2d: bool = False,
        allow_conversion: bool = True,
        warn: Optional[Callable] = raw.warn,
    ):
        # Documentation for parameters is in docs.py
        """Memory-map an existing WAVE file into a numpy matrix."""

        if mode not in MODES:
            raise ValueError(f'Mode {mode} not in {MODES}')

        file_size = raw.file_byte_size(filename)

        with open(filename, 'rb') as fp:
            begin, end, fmt = _metadata(fp, warn, file_size)
            offset = begin + wave.CHUNK.size
            roffset = file_size - end

        f = wave.FMT_PCM.unpack_from(fmt)

        if f.wFormatTag == wave.WAVE_FORMAT_EXTENSIBLE:
            g = wave.FMT_EXTENSION.unpack_from(fmt, offset=wave.FMT_PCM.size)
            f.wFormatTag = g.wFormatTag

        if f.wFormatTag not in wave.WAVE_FORMATS:
            raise ValueError(f'Do not understand f.wFormatTag={f.wFormatTag}')

        is_float = f.wFormatTag == wave.WAVE_FORMAT_IEEE_FLOAT

        if f.wBitsPerSample == 24:
            raise ValueError('Reading 24-bit WAVEs is not quite supported')

        if f.wBitsPerSample not in BITS_PER_SAMPLE[is_float]:
            raise ValueError(
                f'Cannot mmap f.wBitsPerSample={f.wBitsPerSample}'
            )

        if f.wBitsPerSample == 8:
            dtype = 'uint8'
        else:
            type_name = ('int', 'float')[is_float]
            dtype = f'{type_name}{f.wBitsPerSample}'

        assert np.dtype(dtype).itemsize == f.wBitsPerSample // 8
        self = raw.RawMap.__new__(
            cls,
            filename=filename,
            dtype=dtype,
            mode=mode,
            shape=f.nChannels,
            offset=offset,
            roffset=roffset,
            order=order,
            always_2d=always_2d,
            allow_conversion=allow_conversion,
            warn=warn,
        )

        self.sample_rate = f.nSamplesPerSec
        return self


def _metadata(fp, warn, file_size):
    (tag, b, e), *chunks = _chunks(fp, warn, file_size)
    if tag != b'WAVE':
        raise ValueError(f'Not a WAVE file: {tag}')

    assert b == 0
    if e != file_size - 8:
        warn(f'WAVE cksize is wrong: {e} != {file_size - 8}')

    begin = end = fmt = None
    for tag, b, e in chunks:
        if tag == b'fmt ':
            if not fmt:
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

    if (len(fmt) - wave.CHUNK.size) not in FMT_BLOCK_LENGTHS:
        warn(f'Weird fmt block length {len(fmt)}')

    return begin, end, fmt


def _chunks(fp, warn, file_size):
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
