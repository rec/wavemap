"""
🌊 Memory map WAVE files into numpy arrays 🌊



Reads and writes 8-bit, 16-bit, 32-bit and 64-bit integer WAVE files
as well as 32-bit and

The actual samples from a WAVE file appear as entries in a numpy array.

See documentation for numpy.memmap

If you open the file in 'r+' mode, you can even rewrite the samples on
disk that way.

"""

from .raw import RawMap
from .read import ReadMap as ReadMap
from .write import WriteMap as WriteMap

__all__ = (
    'WaveMap',
    'RawMap',
    'ReadMap',
    'WriteMap',
    'copy_to',
    'new_like',
)
__version__ = '0.9.1'

copy_to = WriteMap.copy_to
new_like = WriteMap.new_like


def WaveMap(filename, mode='r', *args, **kwargs):
    """
    Memory a map WAVE file to a `numpy` array

    Return an instance of `ReadMap` or `WriteMap`, depending on
    `mode`.

    See the documentation of `ReadMap` or `WriteMap` for full signatures.
    """
    if mode.startswith('w'):
        return WriteMap(filename, *args, **kwargs)
    return ReadMap(filename, mode, *args, **kwargs)
