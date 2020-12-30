import struct

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMATS = WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT

# Making 24 bits work transparently is probably impossible:
# https://stackoverflow.com/a/34128171/43839

CHUNK_FORMAT = struct.Struct('<4s I')
FMT_FORMAT = struct.Struct('<HHIIHH')
HEADER_FORMAT = struct.Struct('<4s I 4s 4s I H H I I H H')
FMT_FORMAT = struct.Struct('<H H I I H H')

assert CHUNK_FORMAT.size == 8
assert FMT_FORMAT.size == 16
assert HEADER_FORMAT.size == 36, f'{HEADER_FORMAT.size}'
