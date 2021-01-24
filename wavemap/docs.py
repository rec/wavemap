import functools
import inspect

ALLOW_CONVERSION = """
Some types of WAVE files cannot be directedly memory-mapped because
their datatype is not supported by numpy - the list includes
24-bit PCM, 8-bit µ-Law, and 8-bit A-law.

If `allow_conversion` is `True`, the default, the result is
converted to a numpy type.  If it is `False`, then the result is
not converted and returned as numpy array of raw bytes
"""

ALWAYS_2D = """
If `False`, the default, mono WAVE files with only one channel
get special treatment and are mapped to a one-dimensional vector
with `size=(N,)`.

If `True`, mono WAVE files are treated the same as any other file
and are mapped to a two-dimensional matrix with `size=(N, 1)`.
"""

CLS = """
Think of this as `self`.  (This is because you need to implement `__new__`
and not `__init__` when deriving from `np.darray`.)
"""

DTYPE = 'The numpy datatype of the samples in the file.'

FILENAME = 'The name of the file being mapped'

ORDER = """
Samples usually get laid out in into a `numpy.darray` with`
shape=(N, C)` where `N` is the number of audio frames, and `C` is
the number of channels.

This is called column major order, but this can be toggled by
setting the `order` parameter to `F` for Fortan or row-major row.

See https://stackoverflow.com/questions/27266338/
"""

READ_ONLY_MODE = """
The file is opened in this mode.
Must be one of `'r'`, `'r+'` and `'c'`.

In mode `'r'`, the default, the file is opened read-only and
the `numpy.darray` is immutable.

In mode `'r+'`, the file is opened read-write and changes to the
`numpy.darray` are automatically applied to the file.

In mode `'c'`, "copy-on-write", the file is opened read-only, but
the `numpy.darray` is *not* immutable: changes to the array are
instead stored in memory.
"""

MODE = """
The file is opened in this mode.
Must be one of `'r'`, `'r+'`, `'c'`, `'w+'`

In mode `'r'`, the default, the file is opened read-only and
the `numpy.darray` is immutable.

In mode `'r+'`, the file is opened read-write and changes to the
`numpy.darray` are automatically applied to the file.

In mode `'c'`, "copy-on-write", the file is opened read-only, but
the `numpy.darray` is *not* immutable: changes to the array are
instead stored in memory.

In mode `'w+'`, "write", the file is opened for write, and overwrites
whatever else is there.
"""

OFFSET = 'How many bytes in the file before the WAV data'
ROFFSET = 'How many bytes in the file after the WAV data'
SAMPLE_RATE = 'The sample rate in Hz (cycles per second)'

SHAPE = """
The shape of the resulting numpy.darray. Can be a tuple, or a positive
integer, or `None`.
"""

WARN = """
Programmers are sloppy so quite a lot of real-world WAVE files have
recoverable errors in their format.  `warn` is the function used to
report those recoverable errors.  By default, it's set to print to
`sys.stderr` but setting it to `None` disables errors entirely, or
you can pass your own callback in
"""


def arguments(*names, subs=None):
    subs = subs or {}
    # TODO: wrong name gets put here in a substitution
    names = [(i, subs.get(i, i).upper()) for i in names]
    missing = [n for (n, a) in names if a not in globals()]
    if missing:
        raise ValueError(f'Cannot document arguments {missing}')

    yield 'ARGUMENTS'
    for name, attr in names:
        yield f'  {name}'
        for line in globals()[attr].strip().splitlines():
            yield line and f'    {line}'
        yield ''


def add_arguments(func, names, subs=None):
    params = arguments(*names, subs=subs)
    func.__doc__ = func.__doc__.rstrip() + '\n\n' + '\n'.join(params)
    return func


def update(func=None, **subs):
    assert not (func and subs)

    def updater(func, subs=None):
        names = inspect.signature(func).parameters
        return add_arguments(func, names, subs=subs)

    if func:
        return updater(func)

    return functools.partial(updater, subs=subs)
