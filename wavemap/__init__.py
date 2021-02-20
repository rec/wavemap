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

Typical usage:

.. code-block:: python

    import wavemap

    wm = wavemap('test.wav', 'r+')  # r+ means read/write
    # Now you have a numpy matrix that you can use like any other

    wm /= 2
    # Each sample in the file is scaled by half.
"""
from . import docs
from .convert import convert
from .raw import RawMap, warn
from .read import ReadMap as ReadMap
from .write import WriteMap as WriteMap
from typing import Callable, Optional, Union
import numpy as np
import xmod

__all__ = (
    'wavemap',
    'RawMap',
    'ReadMap',
    'WriteMap',
    'copy_to',
    'new_like',
    'convert',
)
__version__ = '1.1.1'

copy_to = WriteMap.copy_to
new_like = WriteMap.new_like
_DOKS = {warn: '<function warn: print to stderr>'}
_WRITE_PARAMETERS = 'dtype', 'shape', 'sample_rate'
_READ_PARAMETERS = 'order', 'always_2d'


@xmod
@docs.update
def wavemap(
    filename: str,
    #
    # Read parameters
    #
    mode: str = 'r',
    order: Optional[str] = None,
    always_2d: bool = False,
    allow_conversion: bool = True,
    #
    # Write parameters
    #
    shape: Union[None, int, tuple] = None,
    sample_rate: int = 0,
    roffset: int = 0,
    #
    # Read and write parameters
    #
    dtype: Optional[np.dtype] = None,
    warn: Optional[Callable] = warn,
):
    """
    Memory map a WAVE file to a `numpy` array

    Return an instance of `ReadMap` or `WriteMap`, depending on
    `mode`.
    """
    if mode.startswith('w'):
        if not dtype:
            raise ValueError('dtype must be set for write')
        if not shape:
            raise ValueError('shape must be set for write')
        if not sample_rate:
            raise ValueError('sample_rate must be set for write')

        if order:
            raise ValueError('order cannot be set for write')
        if always_2d:
            raise ValueError('always_2d cannot be set for write')

        return WriteMap(
            filename=filename,
            dtype=dtype,
            shape=shape,
            sample_rate=sample_rate,
            roffset=roffset,
            warn=warn,
        )
    else:
        if shape:
            raise ValueError('shape cannot be set for write')
        if sample_rate:
            raise ValueError('sample_rate cannot be set for write')

        result = ReadMap(
            filename=filename,
            mode=mode,
            order=order,
            always_2d=always_2d,
            allow_conversion=allow_conversion,
            warn=warn,
        )
        if dtype is not None:
            result = convert(result, dtype)
        return result
