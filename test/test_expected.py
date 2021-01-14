from . import files
from pathlib import Path
import tdir
import unittest
import wavemap


class TestExpected(unittest.TestCase):
    @tdir
    def test_expected(self):
        failures = []
        for filename in files.find():
            canonical = files.canonical(filename)
            local = Path(filename.name)
            wm = wavemap(filename)
            wavemap.copy_to(wm, local)

            b1, b2 = canonical.read_bytes(), local.read_bytes()
            if b1 != b2:
                failures.append(filename.name)
        assert failures == []
