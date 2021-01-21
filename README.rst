🌊 Memory map WAVE files into numpy arrays 🌊

.. image:: https://raw.githubusercontent.com/rec/wavemap/master/wavemap.png
   :alt: WaveMap logo

Samples from a WAVE or RAW audio file are directly memory mapped to entries in
a ``numpy`` array, letting you manipulate very large audio files as if they
all fit into memory at one time, and even directly change samples on disk.

API
===

``wavemap.WaveMap(filename, mode='r', *args, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`wavemap/__init__.py, 32-42 <https://github.com/rec/wavemap/blob/master/wavemap/__init__.py#L32-L42>`_)

Memory map a WAVE file to a ``numpy`` array

Return an instance of ``ReadMap`` or ``WriteMap``, depending on
``mode``.

Class ``wavemap.RawMap``
~~~~~~~~~~~~~~~~~~~~~~~~

(`wavemap/raw.py, 14-82 <https://github.com/rec/wavemap/blob/master/wavemap/raw.py#L14-L82>`_)

"Memory map raw audio data from a disk file into a numpy matrix

``wavemap.RawMap.__new__()``
____________________________

.. code-block:: python

  wavemap.RawMap.__new__(
       cls,
       filename,
       dtype,
       shape=None,
       mode='r',
       offset=0,
       roffset=0,
       order=None,
       always_2d=False,
       allow_conversion=True,
       warn='<function warn: print to stderr>',
  )

(`wavemap/raw.py, 17-82 <https://github.com/rec/wavemap/blob/master/wavemap/raw.py#L17-L82>`_)

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
    integer, or None.

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

(`wavemap/read.py, 17-85 <https://github.com/rec/wavemap/blob/master/wavemap/read.py#L17-L85>`_)

Memory-map an existing WAVE file into a numpy vector or matrix

``wavemap.ReadMap.__new__()``
_____________________________

.. code-block:: python

  wavemap.ReadMap.__new__(
       cls,
       filename,
       mode='r',
       order=None,
       always_2d=False,
       allow_conversion=True,
       warn='<function warn: print to stderr>',
  )

(`wavemap/read.py, 20-85 <https://github.com/rec/wavemap/blob/master/wavemap/read.py#L20-L85>`_)

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

(`wavemap/write.py, 11-98 <https://github.com/rec/wavemap/blob/master/wavemap/write.py#L11-L98>`_)

"Memory-map a new wave file into a new numpy vector or matrix

``wavemap.WriteMap.__new__()``
______________________________

.. code-block:: python

  wavemap.WriteMap.__new__(
       cls,
       filename,
       dtype,
       shape,
       sample_rate,
       roffset=0,
       warn='<function warn: print to stderr>',
  )

(`wavemap/write.py, 14-78 <https://github.com/rec/wavemap/blob/master/wavemap/write.py#L14-L78>`_)

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
    integer, or None.

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

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2021-01-21T14:02:50.817846)
