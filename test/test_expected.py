from . import files
from pathlib import Path
import tdir
import unittest
import wavemap


class TestExpected(unittest.TestCase):
    @tdir
    def test_expected(self):
        for filename in files.find():
            canonical = files.canonical(filename)
            local = Path(filename.name)
            wm = wavemap.WaveMap(filename)
            wavemap.copy_to(wm, local)

            b1, b2 = canonical.read_bytes(), local.read_bytes()
            assert b1 == b2, str(filename.name)
