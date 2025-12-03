"""Unit tests for Point, Point2D, and Point3D classes."""

import math
import unittest

import numpy as np

from sissf.geometry import Point2D, Point3D


class TestPoint2D(unittest.TestCase):
    """Test Point2D class."""

    def test_init(self):
        """Test Point2D initialization."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)

    def test_getitem(self):
        """Test indexing into Point2D."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(p[0], 1.0)
        self.assertEqual(p[1], 2.0)

    def test_tolist(self):
        """Test conversion to list."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(p.tolist(), [1.0, 2.0])

    def test_to_tuple(self):
        """Test conversion to tuple."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(p.to_tuple(), (1.0, 2.0))

    def test_to_dict(self):
        """Test conversion to dictionary."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(p.to_dict(), {"x": 1.0, "y": 2.0})

    def test_from_dict(self):
        """Test creation from dictionary."""
        p = Point2D.from_dict({"x": 1.0, "y": 2.0})
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)

    def test_fromlist(self):
        """Test creation from list."""
        p = Point2D.fromlist([1.0, 2.0])
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)

    def test_min(self):
        """Test element-wise minimum."""
        p1 = Point2D(1.0, 5.0)
        p2 = Point2D(3.0, 2.0)
        p3 = Point2D(0.0, 4.0)
        result = Point2D.min([p1, p2, p3])
        self.assertEqual(result.x, 0.0)
        self.assertEqual(result.y, 2.0)

    def test_max(self):
        """Test element-wise maximum."""
        p1 = Point2D(1.0, 5.0)
        p2 = Point2D(3.0, 2.0)
        p3 = Point2D(0.0, 4.0)
        result = Point2D.max([p1, p2, p3])
        self.assertEqual(result.x, 3.0)
        self.assertEqual(result.y, 5.0)

    def test_sum(self):
        """Test element-wise sum."""
        p1 = Point2D(1.0, 2.0)
        p2 = Point2D(3.0, 4.0)
        result = Point2D.sum([p1, p2])
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)

    def test_mean(self):
        """Test mean (centroid) calculation."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(2.0, 4.0)
        result = Point2D.mean([p1, p2])
        self.assertEqual(result.x, 1.0)
        self.assertEqual(result.y, 2.0)

    def test_add(self):
        """Test point addition."""
        p1 = Point2D(1.0, 2.0)
        p2 = Point2D(3.0, 4.0)
        result = p1 + p2
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)

    def test_sub(self):
        """Test point subtraction."""
        p1 = Point2D(5.0, 7.0)
        p2 = Point2D(2.0, 3.0)
        result = p1 - p2
        self.assertEqual(result.x, 3.0)
        self.assertEqual(result.y, 4.0)

    def test_mult(self):
        """Test scalar multiplication."""
        p = Point2D(2.0, 3.0)
        result = p * 2.0
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)

    def test_rmult(self):
        """Test reverse scalar multiplication."""
        p = Point2D(2.0, 3.0)
        result = 2.0 * p
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)

    def test_div(self):
        """Test scalar division."""
        p = Point2D(4.0, 6.0)
        result = p / 2.0
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.y, 3.0)

    def test_distance(self):
        """Test distance calculation."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        dist = Point2D.distance(p1, p2)
        self.assertEqual(dist, 5.0)

    def test_distance_to(self):
        """Test distance_to method."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        dist = p1.distance_to(p2)
        self.assertEqual(dist, 5.0)

    def test_distance_sq(self):
        """Test squared distance calculation."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        dist_sq = Point2D.distance_sq(p1, p2)
        self.assertEqual(dist_sq, 25.0)

    def test_magnitude(self):
        """Test magnitude calculation."""
        p = Point2D(3.0, 4.0)
        self.assertEqual(p.magnitude(), 5.0)

    def test_length(self):
        """Test length (alias for magnitude)."""
        p = Point2D(3.0, 4.0)
        self.assertEqual(p.length(), 5.0)

    def test_swap_axes(self):
        """Test axis swapping."""
        p = Point2D(1.0, 2.0)
        result = p.swap_axes(0, 1)
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.y, 1.0)

    def test_swap_axes_same(self):
        """Test swapping same axis."""
        p = Point2D(1.0, 2.0)
        result = p.swap_axes(0, 0)
        self.assertEqual(result.x, 1.0)
        self.assertEqual(result.y, 2.0)

    def test_invert(self):
        """Test axis inversion."""
        p = Point2D(1.0, 2.0)
        result = p.invert(0)
        self.assertEqual(result.x, -1.0)
        self.assertEqual(result.y, 2.0)

    def test_equality(self):
        """Test equality comparison."""
        p1 = Point2D(1.0, 2.0)
        p2 = Point2D(1.0, 2.0)
        p3 = Point2D(1.0000001, 2.0)
        p4 = Point2D(2.0, 3.0)

        self.assertEqual(p1, p2)
        self.assertEqual(p1, p3)  # Within tolerance
        self.assertNotEqual(p1, p4)

    def test_repr(self):
        """Test string representation."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(repr(p), "Point2D(1.0, 2.0)")

    def test_str(self):
        """Test string conversion."""
        p = Point2D(1.0, 2.0)
        self.assertEqual(str(p), "[1.0, 2.0]")


class TestPoint3D(unittest.TestCase):
    """Test Point3D class."""

    def test_init(self):
        """Test Point3D initialization."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)
        self.assertEqual(p.z, 3.0)

    def test_getitem(self):
        """Test indexing into Point3D."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p[0], 1.0)
        self.assertEqual(p[1], 2.0)
        self.assertEqual(p[2], 3.0)

    def test_tolist(self):
        """Test conversion to list."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p.tolist(), [1.0, 2.0, 3.0])

    def test_to_tuple(self):
        """Test conversion to tuple."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p.to_tuple(), (1.0, 2.0, 3.0))

    def test_to_dict(self):
        """Test conversion to dictionary."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p.to_dict(), {"x": 1.0, "y": 2.0, "z": 3.0})

    def test_from_dict(self):
        """Test creation from dictionary."""
        p = Point3D.from_dict({"x": 1.0, "y": 2.0, "z": 3.0})
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)
        self.assertEqual(p.z, 3.0)

    def test_fromlist(self):
        """Test creation from list."""
        p = Point3D.fromlist([1.0, 2.0, 3.0])
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)
        self.assertEqual(p.z, 3.0)

    def test_min(self):
        """Test element-wise minimum."""
        p1 = Point3D(1.0, 5.0, 2.0)
        p2 = Point3D(3.0, 2.0, 4.0)
        p3 = Point3D(0.0, 4.0, 1.0)
        result = Point3D.min([p1, p2, p3])
        self.assertEqual(result.x, 0.0)
        self.assertEqual(result.y, 2.0)
        self.assertEqual(result.z, 1.0)

    def test_max(self):
        """Test element-wise maximum."""
        p1 = Point3D(1.0, 5.0, 2.0)
        p2 = Point3D(3.0, 2.0, 4.0)
        p3 = Point3D(0.0, 4.0, 1.0)
        result = Point3D.max([p1, p2, p3])
        self.assertEqual(result.x, 3.0)
        self.assertEqual(result.y, 5.0)
        self.assertEqual(result.z, 4.0)

    def test_sum(self):
        """Test element-wise sum."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        result = Point3D.sum([p1, p2])
        self.assertEqual(result.x, 5.0)
        self.assertEqual(result.y, 7.0)
        self.assertEqual(result.z, 9.0)

    def test_mean(self):
        """Test mean (centroid) calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(2.0, 4.0, 6.0)
        result = Point3D.mean([p1, p2])
        self.assertEqual(result.x, 1.0)
        self.assertEqual(result.y, 2.0)
        self.assertEqual(result.z, 3.0)

    def test_add(self):
        """Test point addition."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        result = p1 + p2
        self.assertEqual(result.x, 5.0)
        self.assertEqual(result.y, 7.0)
        self.assertEqual(result.z, 9.0)

    def test_sub(self):
        """Test point subtraction."""
        p1 = Point3D(5.0, 7.0, 9.0)
        p2 = Point3D(2.0, 3.0, 4.0)
        result = p1 - p2
        self.assertEqual(result.x, 3.0)
        self.assertEqual(result.y, 4.0)
        self.assertEqual(result.z, 5.0)

    def test_mult(self):
        """Test scalar multiplication."""
        p = Point3D(2.0, 3.0, 4.0)
        result = p * 2.0
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)
        self.assertEqual(result.z, 8.0)

    def test_rmult(self):
        """Test reverse scalar multiplication."""
        p = Point3D(2.0, 3.0, 4.0)
        result = 2.0 * p
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)
        self.assertEqual(result.z, 8.0)

    def test_div(self):
        """Test scalar division."""
        p = Point3D(4.0, 6.0, 8.0)
        result = p / 2.0
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.y, 3.0)
        self.assertEqual(result.z, 4.0)

    def test_distance(self):
        """Test distance calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        dist = Point3D.distance(p1, p2)
        self.assertEqual(dist, 5.0)

    def test_distance_to(self):
        """Test distance_to method."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        dist = p1.distance_to(p2)
        self.assertEqual(dist, 5.0)

    def test_distance_sq(self):
        """Test squared distance calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        dist_sq = Point3D.distance_sq(p1, p2)
        self.assertEqual(dist_sq, 25.0)

    def test_magnitude(self):
        """Test magnitude calculation."""
        p = Point3D(3.0, 4.0, 0.0)
        self.assertEqual(p.magnitude(), 5.0)

    def test_length(self):
        """Test length (alias for magnitude)."""
        p = Point3D(3.0, 4.0, 0.0)
        self.assertEqual(p.length(), 5.0)

    def test_swap_axes(self):
        """Test axis swapping."""
        p = Point3D(1.0, 2.0, 3.0)
        result = p.swap_axes(0, 2)
        self.assertEqual(result.x, 3.0)
        self.assertEqual(result.y, 2.0)
        self.assertEqual(result.z, 1.0)

    def test_swap_axes_same(self):
        """Test swapping same axis."""
        p = Point3D(1.0, 2.0, 3.0)
        result = p.swap_axes(1, 1)
        self.assertEqual(result.x, 1.0)
        self.assertEqual(result.y, 2.0)
        self.assertEqual(result.z, 3.0)

    def test_invert(self):
        """Test axis inversion."""
        p = Point3D(1.0, 2.0, 3.0)
        result = p.invert(1)
        self.assertEqual(result.x, 1.0)
        self.assertEqual(result.y, -2.0)
        self.assertEqual(result.z, 3.0)

    def test_scale(self):
        """Test in-place scaling."""
        p = Point3D(2.0, 3.0, 4.0)
        result = p.scale(2.0)
        self.assertIs(result, p)  # Should return self
        self.assertEqual(p.x, 4.0)
        self.assertEqual(p.y, 6.0)
        self.assertEqual(p.z, 8.0)

    def test_normalize(self):
        """Test in-place normalization."""
        p = Point3D(3.0, 4.0, 0.0)
        result = p.normalize()
        self.assertIs(result, p)  # Should return self
        self.assertAlmostEqual(p.x, 0.6)
        self.assertAlmostEqual(p.y, 0.8)
        self.assertAlmostEqual(p.z, 0.0)
        self.assertAlmostEqual(p.magnitude(), 1.0)

    def test_normalized(self):
        """Test normalized copy."""
        p = Point3D(3.0, 4.0, 0.0)
        result = p.normalized()
        self.assertIsNot(result, p)  # Should be a copy
        self.assertEqual(p.x, 3.0)  # Original unchanged
        self.assertAlmostEqual(result.x, 0.6)
        self.assertAlmostEqual(result.y, 0.8)
        self.assertAlmostEqual(result.magnitude(), 1.0)

    def test_rotate(self):
        """Test in-place rotation."""
        p = Point3D(1.0, 0.0, 0.0)
        result = p.rotate(2, math.pi / 2)  # Rotate around Z-axis by 90 degrees
        self.assertIs(result, p)  # Should return self
        self.assertAlmostEqual(p.x, 0.0, places=5)
        self.assertAlmostEqual(p.y, 1.0, places=5)
        self.assertAlmostEqual(p.z, 0.0, places=5)

    def test_rotated(self):
        """Test rotated copy."""
        p = Point3D(1.0, 0.0, 0.0)
        result = p.rotated(2, math.pi / 2)  # Rotate around Z-axis by 90 degrees
        self.assertIsNot(result, p)  # Should be a copy
        self.assertEqual(p.x, 1.0)  # Original unchanged
        self.assertAlmostEqual(result.x, 0.0, places=5)
        self.assertAlmostEqual(result.y, 1.0, places=5)

    def test_translate(self):
        """Test in-place translation."""
        p = Point3D(1.0, 2.0, 3.0)
        result = p.translate(np.array([1.0, 1.0, 1.0]))
        self.assertIs(result, p)  # Should return self
        self.assertEqual(p.x, 2.0)
        self.assertEqual(p.y, 3.0)
        self.assertEqual(p.z, 4.0)

    def test_translated(self):
        """Test translated copy."""
        p = Point3D(1.0, 2.0, 3.0)
        result = p.translated(np.array([1.0, 1.0, 1.0]))
        self.assertIsNot(result, p)  # Should be a copy
        self.assertEqual(p.x, 1.0)  # Original unchanged
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.y, 3.0)
        self.assertEqual(result.z, 4.0)

    def test_cross(self):
        """Test cross product."""
        p1 = Point3D(1.0, 0.0, 0.0)
        p2 = Point3D(0.0, 1.0, 0.0)
        result = p1.cross(p2)
        self.assertEqual(result.x, 0.0)
        self.assertEqual(result.y, 0.0)
        self.assertEqual(result.z, 1.0)

    def test_dot(self):
        """Test dot product."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        result = p1.dot(p2)
        self.assertEqual(result, 32.0)  # 1*4 + 2*5 + 3*6 = 32

    def test_equality(self):
        """Test equality comparison."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = Point3D(1.0000001, 2.0, 3.0)
        p4 = Point3D(2.0, 3.0, 4.0)

        self.assertEqual(p1, p2)
        self.assertEqual(p1, p3)  # Within tolerance
        self.assertNotEqual(p1, p4)

    def test_repr(self):
        """Test string representation."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(repr(p), "Point3D(1.0, 2.0, 3.0)")

    def test_str(self):
        """Test string conversion."""
        p = Point3D(1.0, 2.0, 3.0)
        self.assertEqual(str(p), "[1.0, 2.0, 3.0]")


if __name__ == "__main__":
    unittest.main()
