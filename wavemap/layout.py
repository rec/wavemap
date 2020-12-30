"""Layouts of data in memory"""
import struct


class Layout:
    def __init__(self, **formats):
        self.formats = formats
        self.struct = struct.Struct('<' + ''.join(formats.values()))
        self.size = self.struct.size

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

    def pack(self, **kwargs):
        return self.struct.pack(*self._to_arg(kwargs))

    def pack_into(self, buffer, offset=0, **kwargs):
        return self.struct.pack_into(buffer, offset, *self._to_arg(kwargs))

    def unpack(self, src):
        parts = self.struct.unpack(src)
        return dict(zip(self.names, parts))

    def __add__(self, fmt):
        return __class__(**dict(self.formats, **fmt.formats))


# See http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
INT16 = 'H'
INT32 = 'I'
SUBFORMAT = '16s'
TAG = '4s'

INT = INT16, INT32
BYTES = SUBFORMAT, TAG

RIFF = Layout(ckIDRiff=TAG, cksizeRiff=INT32, WAVEID=TAG)
FACT = Layout(ckIDFact=TAG, cksizeFact=INT32, dwSampleLength=INT32)
DATA = Layout(ckIDData=TAG, cksizeData=INT32)

FMT_PCM = Layout(
    ckIDFmt=TAG,
    cksizeFmt=INT32,
    wFormatTag=INT16,
    nChannels=INT16,
    nSamplesPerSec=INT32,
    nAvgBytesPerSec=INT32,
    nBlockAlign=INT16,
    wBitsPerSample=INT16,
)

FMT_NON_PCM = FMT_PCM + Layout(cbSize=INT16)

FMT_EXTENSIBLE = FMT_NON_PCM + Layout(
    wValidBitsPerSample=INT16, dwChannelMask=TAG, SubFormat=SUBFORMAT
)


PCM = RIFF + FMT_PCM + DATA
NON_PCM = RIFF + FMT_NON_PCM + FACT + DATA
EXTENSIBLE = RIFF + FMT_EXTENSIBLE + DATA

assert RIFF.size == 12
assert FMT_PCM.size == 24
assert FMT_NON_PCM.size == 26
assert FMT_EXTENSIBLE.size == 48
assert DATA.size == 8
assert FACT.size == 12
assert PCM.size == 44
assert NON_PCM.size == 58
assert EXTENSIBLE.size == 68

if __name__ == '__main__':
    d = list(locals().items())
    for k, v in d:
        if isinstance(v, Layout):
            print(f'assert {k}.size == {v.size}')
