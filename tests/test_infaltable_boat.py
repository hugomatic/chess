from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from chess.cad_model import load_model
from chess.cad_planning import CadSelection, build_render_plan
from chess.cad_system import load_system
from tests.stl_bounds import read_stl_bounds


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "things" / "infaltable_boat" / "infaltable_boat.scad"
SIDECAR = SOURCE.with_suffix(".cad.json")


class InfaltableBoatContractTests(unittest.TestCase):
    def test_model_defaults_and_set_contract(self):
        model = load_model("infaltable_boat", SIDECAR, ROOT)
        self.assertEqual(
            tuple(model.sets),
            ("scale_hull", "scale_floor", "scale_transom", "assembly", "full_size_assembly"),
        )
        self.assertEqual(model.default_set, "scale_hull")
        self.assertEqual(
            tuple(model.sets[name].printable for name in model.sets),
            (True, True, True, False, False),
        )
        expected = {
            "boat_length": 4267.2,
            "overall_width": 1828.8,
            "tube_diameter": 457.2,
            "floor_thickness": 152.4,
            "bow_height": 609.6,
            "bow_rise_length": 914.4,
            "bow_flat": 304.8,
            "transom_inset": 609.6,
            "model_scale": 0.0416666667,
            "transom_width": 1371.6,
            "transom_height": 457.2,
            "transom_thickness": 38.1,
            "transom_motor_drop": 152.4,
            "transom_motor_angle": 30,
            "transom_motor_flat": 304.8,
            "print_flat": 0.6,
        }
        self.assertEqual({key: model.source_defaults[key] for key in expected}, expected)

    def test_product_expands_to_three_separate_print_jobs(self):
        system = load_system(ROOT / "cad" / "chess.system.cad.json", ROOT)
        plan = build_render_plan(
            system,
            CadSelection(product="infaltable_boat"),
            {model_id: f"test-{model_id}" for model_id in system.models},
        )
        self.assertEqual(
            tuple((job.model_id, job.set_name) for job in plan.jobs),
            (
                ("infaltable_boat", "scale_hull"),
                ("infaltable_boat", "scale_floor"),
                ("infaltable_boat", "scale_transom"),
            ),
        )
        self.assertEqual(len({job.artifact_id for job in plan.jobs}), 3)


@unittest.skipUnless(shutil.which("openscad"), "OpenSCAD is not installed")
class InfaltableBoatGeometryTests(unittest.TestCase):
    def render(self, set_name):
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

    def test_scale_hull_is_seven_inches_long_with_exact_plan_width(self):
        self.assert_size(self.render("scale_hull"), (76.2, 177.8, 24.8))

    def test_scale_floor_is_a_separate_six_inch_thick_part(self):
        self.assert_size(self.render("scale_floor"), (38.1, 123.825, 6.35))

    def test_scale_transom_is_separate_and_print_oriented(self):
        self.assert_size(self.render("scale_transom"), (57.15, 19.05, 1.5875))

    def test_assembly_is_a_fitted_one_twenty_fourth_reference(self):
        self.assert_size(self.render("assembly"), (79.9, 177.8, 25.4), delta=0.3)

    def test_full_size_assembly_retains_nominal_envelope(self):
        self.assert_size(self.render("full_size_assembly"), (1917.7, 4267.2, 609.6), delta=1.0)


if __name__ == "__main__":
    unittest.main()
