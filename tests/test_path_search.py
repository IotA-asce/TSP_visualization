import math
import unittest


try:
    from path_search import find_path
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f"path_search dependencies missing: {exc}") from exc


def tour_length(path: list[tuple[float, float]]) -> float:
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path)):
        x1, y1 = path[i]
        x2, y2 = path[(i + 1) % len(path)]
        total += math.hypot(x2 - x1, y2 - y1)
    return total


class TestFindPath(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(find_path([]), [])

    def test_single_point_returns_copy(self) -> None:
        pts = [(1.0, 2.0)]
        out = find_path(pts)
        self.assertEqual(out, pts)
        self.assertIsNot(out, pts)

    def test_rectangle_tour_length(self) -> None:
        pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
        out = find_path(pts)

        self.assertEqual(len(out), len(pts))
        self.assertEqual(set(out), set(pts))
        self.assertAlmostEqual(tour_length(out), 6.0, places=7)

    def test_invalid_point_shape_raises(self) -> None:
        with self.assertRaises(ValueError):
            _ = find_path([(0.0, 0.0, 0.0)])


if __name__ == "__main__":
    unittest.main()
