import math
import unittest

from path_search import find_path


def path_length(path: list[tuple[float, float]], *, closed: bool) -> float:
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        total += math.hypot(x2 - x1, y2 - y1)

    if closed:
        x1, y1 = path[-1]
        x2, y2 = path[0]
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
        self.assertAlmostEqual(path_length(out, closed=True), 6.0, places=7)

    def test_rectangle_open_path_length(self) -> None:
        pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
        out = find_path(pts, closed=False)
        self.assertEqual(len(out), len(pts))
        self.assertEqual(set(out), set(pts))
        self.assertAlmostEqual(path_length(out, closed=False), 4.0, places=7)

    def test_strategy_nearest_runs(self) -> None:
        pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
        out = find_path(pts, strategy="nearest")
        self.assertEqual(set(out), set(pts))

    def test_strategy_two_opt_runs(self) -> None:
        pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
        out = find_path(pts, strategy="two_opt")
        self.assertEqual(set(out), set(pts))

    def test_invalid_point_shape_raises(self) -> None:
        with self.assertRaises(ValueError):
            _ = find_path([(0.0, 0.0, 0.0)])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
