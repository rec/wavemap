"""Better struct"""
from argparse import Namespace
import struct


class Structure:
    def __init__(self, **formats):
        self.formats = formats
        self.struct = struct.Struct('<' + ''.join(formats.values()))
        self.size = self.struct.size

    def pack(self, **kwargs):
        return self.struct.pack(*self._to_arg(kwargs))

    def pack_into(self, buffer, offset=0, **kwargs):
        return self.struct.pack_into(buffer, offset, *self._to_arg(kwargs))

    def unpack_from(self, buffer, offset=0):
        parts = self.struct.unpack_from(buffer, offset)
        return Namespace(**dict(zip(self.formats, parts)))

    def __add__(self, fmt):
        return __class__(**dict(self.formats, **fmt.formats))

    def _to_arg(self, kw):
        errors, args = [], []
        for name, fmt in self.formats.items():
            try:
                v = kw[name]
            except KeyError:
                errors.append(f'Unknown param {name}')
            else:
                if fmt in INT and not isinstance(v, int):
                    errors.append(f'Integer {name} had value {v!r}')
                elif fmt in BYTES and not isinstance(v, (bytes, bytearray)):
                    errors.append(f'Bytes {name} had value {v!r}')
                else:
                    args.append(v)

        # We accept the unknown
        unknown = False and set(kw).difference(self.names)
        if unknown:
            s = '' if len(unknown) == 1 else 's'
            unknown = ', '.join(sorted(unknown))
            errors.append(f'Unknown argument{s}: {unknown}')
            raise ValueError(errors[-1])

        msg = '. '.join(errors)
        if msg:
            raise ValueError(msg)

        assert len(args) == len(
            self.formats
        ), f'{len(args)} == {len(self.formats)}'
        return args


# See http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
INT16 = 'H'
INT32 = 'I'
SUBFORMAT = '16s'
TAG = '4s'

INT = INT16, INT32
BYTES = SUBFORMAT, TAG

CHUNK = Structure(ckID=TAG, cksize=INT32)
RIFF = Structure(ckIDRiff=TAG, cksizeRiff=INT32, WAVEID=TAG)
FACT = Structure(ckIDFact=TAG, cksizeFact=INT32, dwSampleLength=INT32)
DATA = Structure(ckIDData=TAG, cksizeData=INT32)

assert CHUNK.size == 8
assert RIFF.size == 12
assert FACT.size == 12
assert DATA.size == 8

FMT_PCM = Structure(
    ckIDFmt=TAG,
    cksizeFmt=INT32,
    wFormatTag=INT16,
    nChannels=INT16,
    nSamplesPerSec=INT32,
    nAvgBytesPerSec=INT32,
    nBlockAlign=INT16,
    wBitsPerSample=INT16,
)

FMT_NON_PCM = FMT_PCM + Structure(cbSize=INT16)

FMT_EXTENSIBLE = FMT_NON_PCM + Structure(
    wValidBitsPerSample=INT16, dwChannelMask=TAG, SubFormat=SUBFORMAT
)

assert FMT_PCM.size == 24
assert FMT_NON_PCM.size == 26
assert FMT_EXTENSIBLE.size == 48

PCM = RIFF + FMT_PCM + DATA
NON_PCM = RIFF + FMT_NON_PCM + FACT + DATA
EXTENSIBLE = RIFF + FMT_EXTENSIBLE + DATA

assert PCM.size == 44
assert NON_PCM.size == 58
assert EXTENSIBLE.size == 68

if __name__ == '__main__':
    d = list(locals().items())
    for k, v in d:
        if isinstance(v, Structure):
            print(f'assert {k}.size == {v.size}')