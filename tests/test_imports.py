import importlib
import unittest


class TestImports(unittest.TestCase):
    def test_import_vector(self) -> None:
        importlib.import_module("vector")

    def test_import_path_search(self) -> None:
        try:
            importlib.import_module("path_search")
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(f"path_search dependencies missing: {exc}") from exc

    def test_import_game_screen(self) -> None:
        try:
            importlib.import_module("game_screen")
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(f"pygame missing: {exc}") from exc


if __name__ == "__main__":
    unittest.main()
