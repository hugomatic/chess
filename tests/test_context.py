import unittest
from pathlib import Path

from chess.context import resolve_context


class ContextTests(unittest.TestCase):
    def test_defaults_to_repository_and_data_child(self):
        context = resolve_context({})

        self.assertEqual(context.root, Path(__file__).resolve().parents[1])
        self.assertEqual(context.data_dir, context.root / "data")

    def test_environment_overrides_are_resolved(self):
        context = resolve_context(
            {"CHESS_ROOT": "./project", "CHESS_DATA_DIR": "./runs"}
        )

        self.assertEqual(context.root, Path("project").resolve())
        self.assertEqual(context.data_dir, Path("runs").resolve())


if __name__ == "__main__":
    unittest.main()
