"""
🌊 Memory map WAVE files into numpy arrays 🌊

The actual samples from a WAVE file appear as entries in a numpy array.

See documentation for numpy.memmap

If you open the file in 'r+' mode, you can even rewrite the samples on
disk that way.

"""

from .raw import RawMap
from .read import ReadMap as WaveReadMap
from .write import WriteMap as WaveWriteMap

__all__ = 'RawMap', 'WaveReadMap', 'WaveWriteMap', 'WaveMap'
__version__ = '0.9.1'

new_like = WaveWriteMap.new_like


def WaveMap(filename, mode='r', *args, **kwargs):
    """Return an instance of `WaveReadMap` or `WaveWriteMap`, depending on
    `mode`.

    See the documentation of these classes for full signatures.
    """
    if mode.startswith('w'):
        return WaveWriteMap(filename, *args, **kwargs)
    return WaveReadMap(filename, mode, *args, **kwargs)
