from wavemap import ReadMap
import inspect
import unittest


class TestDocs(unittest.TestCase):
    def test_docs(self):
        actual = inspect.getdoc(ReadMap.__new__)
        expected = READMAP_DOC
        if expected != actual:
            print('expected', '------', '', *expected, sep='\n')
            print
            print('actual', '------', '', *actual, sep='\n')
            if True:
                assert expected == actual
            assert False


READMAP_DOC = """\
Memory-map an existing WAVE file into a numpy matrix.

ARGUMENTS
  cls
    Think of this as `self`.  (This is because you need to implement `__new__`
    and not `__init__` when deriving from `np.darray`.)

  filename
    The name of the file being mapped

  mode
    The file is opened in this mode.
    Must be one of `'r'`, `'r+'` and `'c'`.

    In mode `'r'`, the default, the file is opened read-only and
    the `numpy.darray` is immutable.

    In mode `'r+'`, the file is opened read-write and changes to the
    `numpy.darray` are automatically applied to the file.

    In mode `'c'`, "copy-on-write", the file is opened read-only, but
    the `numpy.darray` is *not* immutable: changes to the array are
    instead stored in memory.

  order
    Samples usually get laid out in into a `numpy.darray` with`
    shape=(N, C)` where `N` is the number of audio frames, and `C` is
    the number of channels.

    This is called column major order, but this can be toggled by
    setting the `order` parameter to `F` for Fortan or row-major row.

    See https://stackoverflow.com/questions/27266338/

  always_2d
    If `False`, the default, mono WAVE files with only one channel
    get special treatment and are mapped to a one-dimensional vector
    with `size=(N,)`.

    If `True`, mono WAVE files are treated the same as any other file
    and are mapped to a two-dimensional matrix with `size=(N, 1)`.

  warn
    Programmers are sloppy so quite a lot of real-world WAVE files have
    recoverable errors in their format.  `warn` is the function used to
    report those recoverable errors.  By default, it's set to print to
    `sys.stderr` but setting it to `None` disables errors entirely, or
    you can pass your own callback in\
"""
