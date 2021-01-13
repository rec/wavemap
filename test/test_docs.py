from wavemap import docs, ReadMap
import inspect
import unittest


class TestDocs(unittest.TestCase):
    def test_docs(self):
        expected = inspect.getdoc(ReadMap.__new__).splitlines()
        while expected[0] != 'ARGUMENTS':
            expected.pop(0)
        actual = list(
            docs.arguments(
                'filename',
                'mode',
                'order',
                'always_2d',
                'allow_conversion',
                'warn',
            )
        )
        assert actual.pop() == ''
        if expected != actual:
            print('expected', '------', '', *expected, sep='\n')
            print
            print('actual', '------', '', *actual, sep='\n')
            if True:
                assert expected == actual
            assert False
