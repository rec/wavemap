🌊 Memory map WAVE files into numpy arrays 🌊
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

API
===

``wavemap()``
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  wavemap(
       filename: str,
       mode: str='r',
       order: Union[str, NoneType]=None,
       always_2d: bool=False,
       allow_conversion: bool=True,
       dtype: Union[numpy.dtype, NoneType]=None,
       shape: Union[NoneType, int, tuple]=None,
       sample_rate: int=0,
       roffset: int=0,
       warn: Union[Callable, NoneType]='<function warn:  print to stderr>',
  )

(`wavemap/__init__.py, 56-122 <https://github.com/rec/wavemap/blob/master/wavemap/__init__.py#L56-L122>`_)

    Memory map a WAVE file to a ``numpy`` array

    Return an instance of ``ReadMap`` or ``WriteMap``, depending on
    ``mode``.

ARGUMENTS
  filename
    The name of the file being mapped

  mode
    The file is opened in this mode.
    Must be one of ``'r'``, ``'r+'``, ``'c'``, ``'w+'``

    In mode ``'r'``, the default, the file is opened read-only and
    the ``numpy.darray`` is immutable.

    In mode ``'r+'``, the file is opened read-write and changes to the
    ``numpy.darray`` are automatically applied to the file.

    In mode ``'c'``, "copy-on-write", the file is opened read-only, but
    the ``numpy.darray`` is *not* immutable: changes to the array are
    instead stored in memory.

    In mode ``'w+'``, "write", the file is opened for write, and overwrites
    whatever else is there.

  order
    Samples usually get laid out in into a ``numpy.darray`` with``
    shape=(N, C)`` where ``N`` is the number of audio frames, and ``C`` is
    the number of channels.

    This is called column major order, but this can be toggled by
    setting the ``order`` parameter to ``F`` for Fortan or row-major row.

    See https://stackoverflow.com/questions/27266338/

  always_2d
    If ``False``, the default, mono WAVE files with only one channel
    get special treatment and are mapped to a one-dimensional vector
    with ``size=(N,)``.

    If ``True``, mono WAVE files are treated the same as any other file
    and are mapped to a two-dimensional matrix with ``size=(N, 1)``.

  allow_conversion
    Some types of WAVE files cannot be directedly memory-mapped because
    their datatype is not supported by numpy - the list includes
    24-bit PCM, 8-bit µ-Law, and 8-bit A-law.

    If ``allow_conversion`` is ``True``, the default, the result is
    converted to a numpy type.  If it is ``False``, then the result is
    not converted and returned as numpy array of raw bytes

  dtype
    The numpy datatype of the samples in the file.

  shape
    The shape of the resulting numpy.darray. Can be a tuple, or a positive
    integer, or ``None``.

  sample_rate
    The sample rate in Hz (cycles per second)

  roffset
    How many bytes in the file after the WAV data

  warn
    Programmers are sloppy so quite a lot of real-world WAVE files have
    recoverable errors in their format.  ``warn`` is the function used to
    report those recoverable errors.  By default, it's set to print to
    ``sys.stderr`` but setting it to ``None`` disables errors entirely, or
    you can pass your own callback in

Class ``wavemap.RawMap``
~~~~~~~~~~~~~~~~~~~~~~~~

(`wavemap/raw.py, 15-83 <https://github.com/rec/wavemap/blob/master/wavemap/raw.py#L15-L83>`_)

"Memory map raw audio data from a disk file into a numpy matrix

``wavemap.RawMap.__new__()``
____________________________

.. code-block:: python

  wavemap.RawMap.__new__(
       cls,
       filename: str,
       dtype: numpy.dtype,
       shape: Union[tuple, int, NoneType]=None,
       mode: str='r',
       offset: int=0,
       roffset: int=0,
       order: Union[str, NoneType]=None,
       always_2d: bool=False,
       allow_conversion: bool=True,
       warn: Union[Callable, NoneType]='<function warn:  print to stderr>',
  )

(`wavemap/raw.py, 18-83 <https://github.com/rec/wavemap/blob/master/wavemap/raw.py#L18-L83>`_)

Memory map raw audio data from a disk file into a numpy matrix

ARGUMENTS
  cls
    Think of this as ``self``.  (This is because you need to implement ``__new__``
    and not ``__init__`` when deriving from ``np.darray``.)

  filename
    The name of the file being mapped

  dtype
    The numpy datatype of the samples in the file.

  shape
    The shape of the resulting numpy.darray. Can be a tuple, or a positive
    integer, or ``None``.

  mode
    The file is opened in this mode.
    Must be one of ``'r'``, ``'r+'``, ``'c'``, ``'w+'``

    In mode ``'r'``, the default, the file is opened read-only and
    the ``numpy.darray`` is immutable.

    In mode ``'r+'``, the file is opened read-write and changes to the
    ``numpy.darray`` are automatically applied to the file.

    In mode ``'c'``, "copy-on-write", the file is opened read-only, but
    the ``numpy.darray`` is *not* immutable: changes to the array are
    instead stored in memory.

    In mode ``'w+'``, "write", the file is opened for write, and overwrites
    whatever else is there.

  offset
    How many bytes in the file before the WAV data

  roffset
    How many bytes in the file after the WAV data

  order
    Samples usually get laid out in into a ``numpy.darray`` with``
    shape=(N, C)`` where ``N`` is the number of audio frames, and ``C`` is
    the number of channels.

    This is called column major order, but this can be toggled by
    setting the ``order`` parameter to ``F`` for Fortan or row-major row.

    See https://stackoverflow.com/questions/27266338/

  always_2d
    If ``False``, the default, mono WAVE files with only one channel
    get special treatment and are mapped to a one-dimensional vector
    with ``size=(N,)``.

    If ``True``, mono WAVE files are treated the same as any other file
    and are mapped to a two-dimensional matrix with ``size=(N, 1)``.

  allow_conversion
    Some types of WAVE files cannot be directedly memory-mapped because
    their datatype is not supported by numpy - the list includes
    24-bit PCM, 8-bit µ-Law, and 8-bit A-law.

    If ``allow_conversion`` is ``True``, the default, the result is
    converted to a numpy type.  If it is ``False``, then the result is
    not converted and returned as numpy array of raw bytes

  warn
    Programmers are sloppy so quite a lot of real-world WAVE files have
    recoverable errors in their format.  ``warn`` is the function used to
    report those recoverable errors.  By default, it's set to print to
    ``sys.stderr`` but setting it to ``None`` disables errors entirely, or
    you can pass your own callback in

Class ``wavemap.ReadMap``
~~~~~~~~~~~~~~~~~~~~~~~~~

(`wavemap/read.py, 18-86 <https://github.com/rec/wavemap/blob/master/wavemap/read.py#L18-L86>`_)

Memory-map an existing WAVE file into a numpy vector or matrix

``wavemap.ReadMap.__new__()``
_____________________________

.. code-block:: python

  wavemap.ReadMap.__new__(
       cls: Type,
       filename: str,
       mode: str='r',
       order: Union[str, NoneType]=None,
       always_2d: bool=False,
       allow_conversion: bool=True,
       warn: Union[Callable, NoneType]='<function warn:  print to stderr>',
  )

(`wavemap/read.py, 21-86 <https://github.com/rec/wavemap/blob/master/wavemap/read.py#L21-L86>`_)

Memory-map an existing WAVE file into a numpy matrix.

ARGUMENTS
  cls
    Think of this as ``self``.  (This is because you need to implement ``__new__``
    and not ``__init__`` when deriving from ``np.darray``.)

  filename
    The name of the file being mapped

  mode
    The file is opened in this mode.
    Must be one of ``'r'``, ``'r+'`` and ``'c'``.

    In mode ``'r'``, the default, the file is opened read-only and
    the ``numpy.darray`` is immutable.

    In mode ``'r+'``, the file is opened read-write and changes to the
    ``numpy.darray`` are automatically applied to the file.

    In mode ``'c'``, "copy-on-write", the file is opened read-only, but
    the ``numpy.darray`` is *not* immutable: changes to the array are
    instead stored in memory.

  order
    Samples usually get laid out in into a ``numpy.darray`` with``
    shape=(N, C)`` where ``N`` is the number of audio frames, and ``C`` is
    the number of channels.

    This is called column major order, but this can be toggled by
    setting the ``order`` parameter to ``F`` for Fortan or row-major row.

    See https://stackoverflow.com/questions/27266338/

  always_2d
    If ``False``, the default, mono WAVE files with only one channel
    get special treatment and are mapped to a one-dimensional vector
    with ``size=(N,)``.

    If ``True``, mono WAVE files are treated the same as any other file
    and are mapped to a two-dimensional matrix with ``size=(N, 1)``.

  allow_conversion
    Some types of WAVE files cannot be directedly memory-mapped because
    their datatype is not supported by numpy - the list includes
    24-bit PCM, 8-bit µ-Law, and 8-bit A-law.

    If ``allow_conversion`` is ``True``, the default, the result is
    converted to a numpy type.  If it is ``False``, then the result is
    not converted and returned as numpy array of raw bytes

  warn
    Programmers are sloppy so quite a lot of real-world WAVE files have
    recoverable errors in their format.  ``warn`` is the function used to
    report those recoverable errors.  By default, it's set to print to
    ``sys.stderr`` but setting it to ``None`` disables errors entirely, or
    you can pass your own callback in

Class ``wavemap.WriteMap``
~~~~~~~~~~~~~~~~~~~~~~~~~~

(`wavemap/write.py, 12-115 <https://github.com/rec/wavemap/blob/master/wavemap/write.py#L12-L115>`_)

"Memory-map a new wave file into a new numpy vector or matrix

``wavemap.WriteMap.__new__()``
______________________________

.. code-block:: python

  wavemap.WriteMap.__new__(
       cls: Type,
       filename: str,
       dtype: numpy.dtype,
       shape: Union[NoneType, int, tuple],
       sample_rate: int,
       roffset: int=0,
       warn: Union[Callable, NoneType]='<function warn:  print to stderr>',
  )

(`wavemap/write.py, 15-85 <https://github.com/rec/wavemap/blob/master/wavemap/write.py#L15-L85>`_)

        Open a memory-mapped WAVE file in write mode and overwrite any existing
        file.

ARGUMENTS
  cls
    Think of this as ``self``.  (This is because you need to implement ``__new__``
    and not ``__init__`` when deriving from ``np.darray``.)

  filename
    The name of the file being mapped

  dtype
    The numpy datatype of the samples in the file.

  shape
    The shape of the resulting numpy.darray. Can be a tuple, or a positive
    integer, or ``None``.

  sample_rate
    The sample rate in Hz (cycles per second)

  roffset
    How many bytes in the file after the WAV data

  warn
    Programmers are sloppy so quite a lot of real-world WAVE files have
    recoverable errors in their format.  ``warn`` is the function used to
    report those recoverable errors.  By default, it's set to print to
    ``sys.stderr`` but setting it to ``None`` disables errors entirely, or
    you can pass your own callback in

``wavemap.convert()``
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  wavemap.convert(
       arr: numpy.ndarray,
       dtype: numpy.dtype,
  )

(`wavemap/convert.py, 5-70 <https://github.com/rec/wavemap/blob/master/wavemap/convert.py#L5-L70>`_)

Returns a copy of a numpy array or matrix that represents audio data in
another type, scaling and shifting as necessary.

ARGUMENTS
  arr
    A numpy darry representing an audio signal

  dtype
    The numpy dtype to convert to

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2021-01-24T11:34:57.710869)
