"""
🌊 Memory map WAVE files into numpy arrays 🌊

.. image:: https://raw.githubusercontent.com/rec/wavemap/master/wavemap.png
   :alt: WaveMap logo

Samples from a WAVE or RAW audio file are directly memory mapped to entries in
a ``numpy`` array, letting you manipulate very large audio files as if they
all fit into memory at one time, and even directly change samples on disk.
"""

from .raw import RawMap, warn
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
_DOKS = {warn: '<function warn: print to stderr>'}


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
