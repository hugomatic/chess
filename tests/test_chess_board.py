from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from chess.cad_model import load_model
from tests.stl_bounds import read_stl_bounds


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "things" / "chess_board" / "chess_board.scad"
SIDECAR = SOURCE.with_suffix(".cad.json")


class ChessBoardContractTests(unittest.TestCase):
    def test_revised_print_dimensions_are_exposed_as_model_defaults(self):
        model = load_model("chess_board", SIDECAR, ROOT)
        self.assertEqual(
            tuple(model.sets),
            ("chess_board", "drawer", "assembly", "interference"),
        )
        self.assertFalse(model.sets["interference"].printable)
        self.assertEqual(model.source_defaults["square_size"], 27)
        self.assertEqual(model.source_defaults["groove_width"], 1)
        self.assertEqual(model.source_defaults["groove_depth"], 1)
        self.assertEqual(model.source_defaults["drawer_height"], 27.5)
        self.assertEqual(model.source_defaults["top_ramp_width"], 3)
        self.assertEqual(model.source_defaults["detent_depth"], 1.2)
        self.assertEqual(model.source_defaults["detent_base_radius"], 3.5)


@unittest.skipUnless(shutil.which("openscad"), "OpenSCAD is not installed")
class ChessBoardGeometryTests(unittest.TestCase):
    def render_bounds(self, set_name):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name) / f"{set_name}.stl"
        result = subprocess.run(
            ["openscad", "-o", str(output), "-D", f'set="{set_name}"', str(SOURCE)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file() and output.stat().st_size > 0)
        self.assertNotIn("WARNING:", result.stderr)
        self.assertNotIn("ERROR:", result.stderr)
        return read_stl_bounds(output)

    def assert_size(self, bounds, expected, delta=0.16):
        minimum, maximum = bounds
        actual = tuple(maximum[index] - minimum[index] for index in range(3))
        for observed, wanted in zip(actual, expected):
            self.assertAlmostEqual(observed, wanted, delta=delta)

    def test_enlarged_board_and_taller_drawer_render_as_printable_parts(self):
        self.assert_size(self.render_bounds("chess_board"), (226, 226, 32.5))
        self.assert_size(self.render_bounds("drawer"), (219.2, 222.6, 27.5))


if __name__ == "__main__":
    unittest.main()
