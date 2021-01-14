"""🌊 Memory map WAVE files into numpy arrays 🌊
----------------------------------------------

.. image:: https://raw.githubusercontent.com/rec/wavemap/master/wavemap.png
   :alt: WaveMap logo

Manipulate huge WAVE or RAW files as numpy matrices - even if they are too
large to fit into memory.

Memory mapping is a technique where files on disk are directly mapped to
locations in memory and use the same logic as swap space does.

Samples from a WAVE or RAW audio file are directly memory mapped to entries in
a ``numpy`` array, letting you manipulate very large audio files as if they
all fit into memory at one time, and even directly change samples on disk.

"""
from . import docs
from .convert import convert
from .raw import RawMap, warn
from .read import ReadMap as ReadMap
from .write import WriteMap as WriteMap
import inspect
import xmod

__all__ = (
    'WaveMap',
    'RawMap',
    'ReadMap',
    'WriteMap',
    'copy_to',
    'new_like',
    'convert',
)
__version__ = '0.9.1'

copy_to = WriteMap.copy_to
new_like = WriteMap.new_like
_DOKS = {warn: '<function warn: print to stderr>'}


@xmod
def WaveMap(filename, mode='r', *args, **kwargs):
    """
    Memory map a WAVE file to a `numpy` array

    Return an instance of `ReadMap` or `WriteMap`, depending on
    `mode`.
    """
    if mode.startswith('w'):
        return WriteMap(filename, *args, **kwargs)
    return ReadMap(filename, mode, *args, **kwargs)


def _add_doc():
    names = list(inspect.signature(ReadMap).parameters)
    for name in inspect.signature(WriteMap).parameters:
        if name not in names:
            names.append(name)
    docs.add_arguments(WaveMap, names)
