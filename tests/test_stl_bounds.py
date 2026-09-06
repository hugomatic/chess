import struct
from pathlib import Path
import tempfile
import unittest

from tests.stl_bounds import read_stl_bounds


class StlBoundsTests(unittest.TestCase):
    def test_reads_ascii_triangle_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "triangle.stl"
            path.write_text(
                "solid t\nfacet normal 0 0 1\nouter loop\n"
                "vertex -1 2 3\nvertex 4 -5 6\nvertex 0 1 -2\n"
                "endloop\nendfacet\nendsolid t\n",
                encoding="ascii",
            )
            self.assertEqual(read_stl_bounds(path), ((-1, -5, -2), (4, 2, 6)))

    def test_reads_binary_triangle_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "triangle.stl"
            header = b"binary fixture".ljust(80, b"\0")
            triangle = struct.pack(
                "<12fH", 0, 0, 1, -3, 2, 7, 4, -6, 1, 2, 5, -8, 0
            )
            path.write_bytes(header + struct.pack("<I", 1) + triangle)
            self.assertEqual(read_stl_bounds(path), ((-3, -6, -8), (4, 5, 7)))


if __name__ == "__main__":
    unittest.main()
