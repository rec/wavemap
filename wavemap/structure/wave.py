from .structure import Structure, INT16, INT32, SUBFORMAT, TAG

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
