import unittest

from vector import Vector


class TestVector(unittest.TestCase):
    def test_add_and_sub(self) -> None:
        self.assertEqual(Vector(1, 2) + Vector(3, 4), Vector(4, 6))
        self.assertEqual(Vector(1, 2) - Vector(3, 4), Vector(-2, -2))

    def test_mul_scalar_left_and_right(self) -> None:
        self.assertEqual(Vector(2, 3) * 2, Vector(4, 6))
        self.assertEqual(2 * Vector(2, 3), Vector(4, 6))

    def test_mul_vector_elementwise(self) -> None:
        self.assertEqual(Vector(2, 3) * Vector(4, 5), Vector(8, 15))

    def test_unsupported_ops_return_notimplemented(self) -> None:
        v = Vector(1, 2)
        self.assertIs(v.__mul__("x"), NotImplemented)
        self.assertIs(v.__add__(1), NotImplemented)
        self.assertIs(v.__sub__(None), NotImplemented)
        self.assertIs(v.__truediv__("x"), NotImplemented)

    def test_divide_by_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            _ = Vector(1, 2) / 0

    def test_normalize_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            _ = Vector(0, 0).normalize()

    def test_angle_with_zero_vector_raises(self) -> None:
        with self.assertRaises(ValueError):
            _ = Vector(0, 0).angle(Vector(1, 0))

        with self.assertRaises(ValueError):
            _ = Vector(1, 0).angle(Vector(0, 0))

    def test_get_tuple(self) -> None:
        self.assertEqual(Vector(1.5, -2.0).get_tuple(), (1.5, -2.0))


if __name__ == "__main__":
    unittest.main()
