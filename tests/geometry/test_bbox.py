"""Unit tests for BBox3D class."""

import random
import unittest

from sissf.geometry import BBox3D, Point3D


class TestBBox3D(unittest.TestCase):
    """Test BBox3D class."""

    def test_init(self):
        """Test BBox3D initialization."""
        min_pt = Point3D(0.0, 0.0, 0.0)
        max_pt = Point3D(1.0, 1.0, 1.0)
        bbox = BBox3D(min_pt, max_pt)
        self.assertEqual(bbox.min, min_pt)
        self.assertEqual(bbox.max, max_pt)

    def test_init_invalid(self):
        """Test BBox3D initialization with invalid bounds."""
        with self.assertRaises(ValueError) as cm:
            BBox3D(Point3D(1.0, 0.0, 0.0), Point3D(0.0, 1.0, 1.0))
        self.assertIn("Invalid bbox", str(cm.exception))

    def test_center(self):
        """Test center calculation."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.center
        self.assertEqual(center.x, 1.0)
        self.assertEqual(center.y, 1.0)
        self.assertEqual(center.z, 1.0)

    def test_centroid(self):
        """Test centroid (alias for center)."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        centroid = bbox.centroid
        self.assertEqual(centroid.x, 1.0)
        self.assertEqual(centroid.y, 1.0)
        self.assertEqual(centroid.z, 1.0)

    def test_dims(self):
        """Test dimensions calculation."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        dims = bbox.dims
        self.assertEqual(dims.x, 2.0)
        self.assertEqual(dims.y, 3.0)
        self.assertEqual(dims.z, 4.0)

    def test_size(self):
        """Test size (alias for dims)."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        size = bbox.size
        self.assertEqual(size.x, 2.0)
        self.assertEqual(size.y, 3.0)
        self.assertEqual(size.z, 4.0)

    def test_width(self):
        """Test width property."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        self.assertEqual(bbox.width, 2.0)

    def test_height(self):
        """Test height property."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        self.assertEqual(bbox.height, 3.0)

    def test_depth(self):
        """Test depth property."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        self.assertEqual(bbox.depth, 4.0)

    def test_volume(self):
        """Test volume calculation."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        self.assertEqual(bbox.volume, 24.0)

    def test_contains_inside(self):
        """Test contains for point inside box."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        self.assertTrue(bbox.contains(Point3D(0.5, 0.5, 0.5)))

    def test_contains_on_boundary(self):
        """Test contains for point on boundary."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        self.assertTrue(bbox.contains(Point3D(0.0, 0.0, 0.0)))
        self.assertTrue(bbox.contains(Point3D(1.0, 1.0, 1.0)))

    def test_contains_outside(self):
        """Test contains for point outside box."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        self.assertFalse(bbox.contains(Point3D(2.0, 0.0, 0.0)))
        self.assertFalse(bbox.contains(Point3D(-1.0, 0.0, 0.0)))

    def test_intersects_overlapping(self):
        """Test intersects with overlapping boxes."""
        b1 = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        b2 = BBox3D(Point3D(0.5, 0.5, 0.5), Point3D(1.5, 1.5, 1.5))
        self.assertTrue(b1.intersects(b2))
        self.assertTrue(b2.intersects(b1))

    def test_intersects_touching(self):
        """Test intersects with touching boxes."""
        b1 = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        b2 = BBox3D(Point3D(1.0, 0.0, 0.0), Point3D(2.0, 1.0, 1.0))
        self.assertTrue(b1.intersects(b2))

    def test_intersects_separate(self):
        """Test intersects with separate boxes."""
        b1 = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        b2 = BBox3D(Point3D(2.0, 2.0, 2.0), Point3D(3.0, 3.0, 3.0))
        self.assertFalse(b1.intersects(b2))

    def test_expand(self):
        """Test expand method."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        expanded = bbox.expand(0.5)
        self.assertEqual(expanded.min.x, -0.5)
        self.assertEqual(expanded.min.y, -0.5)
        self.assertEqual(expanded.min.z, -0.5)
        self.assertEqual(expanded.max.x, 1.5)
        self.assertEqual(expanded.max.y, 1.5)
        self.assertEqual(expanded.max.z, 1.5)

    def test_get_face_center_left(self):
        """Test get_face_center for LEFT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.LEFT)
        self.assertEqual(center.x, 0.0)
        self.assertEqual(center.y, 1.0)
        self.assertEqual(center.z, 1.0)

    def test_get_face_center_right(self):
        """Test get_face_center for RIGHT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.RIGHT)
        self.assertEqual(center.x, 2.0)
        self.assertEqual(center.y, 1.0)
        self.assertEqual(center.z, 1.0)

    def test_get_face_center_bottom(self):
        """Test get_face_center for BOTTOM face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.BOTTOM)
        self.assertEqual(center.x, 1.0)
        self.assertEqual(center.y, 1.0)
        self.assertEqual(center.z, 0.0)

    def test_get_face_center_top(self):
        """Test get_face_center for TOP face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.TOP)
        self.assertEqual(center.x, 1.0)
        self.assertEqual(center.y, 1.0)
        self.assertEqual(center.z, 2.0)

    def test_get_face_center_front(self):
        """Test get_face_center for FRONT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.FRONT)
        self.assertEqual(center.x, 1.0)
        self.assertEqual(center.y, 2.0)
        self.assertEqual(center.z, 1.0)

    def test_get_face_center_back(self):
        """Test get_face_center for BACK face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        center = bbox.get_face_center(BBox3D.BACK)
        self.assertEqual(center.x, 1.0)
        self.assertEqual(center.y, 0.0)
        self.assertEqual(center.z, 1.0)

    def test_get_face_outnormal_left(self):
        """Test get_face_outnormal for LEFT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.LEFT)
        self.assertEqual(normal, Point3D(-1, 0, 0))

    def test_get_face_outnormal_right(self):
        """Test get_face_outnormal for RIGHT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.RIGHT)
        self.assertEqual(normal, Point3D(1, 0, 0))

    def test_get_face_outnormal_bottom(self):
        """Test get_face_outnormal for BOTTOM face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.BOTTOM)
        self.assertEqual(normal, Point3D(0, 0, -1))

    def test_get_face_outnormal_top(self):
        """Test get_face_outnormal for TOP face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.TOP)
        self.assertEqual(normal, Point3D(0, 0, 1))

    def test_get_face_outnormal_front(self):
        """Test get_face_outnormal for FRONT face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.FRONT)
        self.assertEqual(normal, Point3D(0, -1, 0))

    def test_get_face_outnormal_back(self):
        """Test get_face_outnormal for BACK face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_outnormal(BBox3D.BACK)
        self.assertEqual(normal, Point3D(0, 1, 0))

    def test_get_face_outnormal_invalid(self):
        """Test get_face_outnormal with invalid face index."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        with self.assertRaises(ValueError):
            bbox.get_face_outnormal(999)

    def test_get_face_normal(self):
        """Test get_face_normal (alias for get_face_outnormal)."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        normal = bbox.get_face_normal(BBox3D.TOP)
        self.assertEqual(normal, Point3D(0, 0, 1))

    def test_get_face_dims_left_right(self):
        """Test get_face_dims for LEFT/RIGHT faces."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        dims = bbox.get_face_dims(BBox3D.LEFT)
        self.assertEqual(dims.x, 3.0)  # y dimension
        self.assertEqual(dims.y, 4.0)  # z dimension
        self.assertEqual(dims.z, 2.0)  # x dimension

    def test_get_face_dims_bottom_top(self):
        """Test get_face_dims for BOTTOM/TOP faces."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        dims = bbox.get_face_dims(BBox3D.TOP)
        self.assertEqual(dims.x, 2.0)  # x dimension
        self.assertEqual(dims.y, 3.0)  # y dimension
        self.assertEqual(dims.z, 4.0)  # z dimension

    def test_get_face_dims_front_back(self):
        """Test get_face_dims for FRONT/BACK faces."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 3.0, 4.0))
        dims = bbox.get_face_dims(BBox3D.FRONT)
        self.assertEqual(dims.x, 2.0)  # x dimension
        self.assertEqual(dims.y, 4.0)  # z dimension
        self.assertEqual(dims.z, 3.0)  # y dimension

    def test_get_point_on_face_top_center(self):
        """Test get_point_on_face for center of TOP face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        point = bbox.get_point_on_face(BBox3D.TOP, [0.5, 0.5])
        self.assertEqual(point.x, 1.0)
        self.assertEqual(point.y, 1.0)
        self.assertEqual(point.z, 2.0)

    def test_get_point_on_face_top_corner(self):
        """Test get_point_on_face for corner of TOP face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        point = bbox.get_point_on_face(BBox3D.TOP, [0.0, 0.0])
        self.assertEqual(point.x, 0.0)
        self.assertEqual(point.y, 0.0)
        self.assertEqual(point.z, 2.0)

    def test_get_point_on_face_with_margin(self):
        """Test get_point_on_face with margin."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        point = bbox.get_point_on_face(BBox3D.TOP, [0.0, 0.0], margin=(0.5, 0.5))
        self.assertEqual(point.x, 0.5)
        self.assertEqual(point.y, 0.5)
        self.assertEqual(point.z, 2.0)

    def test_get_point_on_face_invalid(self):
        """Test get_point_on_face with invalid face index."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        with self.assertRaises(ValueError):
            bbox.get_point_on_face(999, [0.5, 0.5])

    def test_sample_face(self):
        """Test sample_face returns point on face."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        random.seed(42)
        point = bbox.sample_face(BBox3D.TOP)
        # Point should be on top face (z=1.0) and within bounds
        self.assertEqual(point.z, 1.0)
        self.assertTrue(0.0 <= point.x <= 1.0)
        self.assertTrue(0.0 <= point.y <= 1.0)

    def test_sample_face_with_margin(self):
        """Test sample_face with margin."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        random.seed(42)
        point = bbox.sample_face(BBox3D.TOP, margin=(0.1, 0.1))
        # Point should respect margins
        self.assertEqual(point.z, 1.0)
        self.assertTrue(0.1 <= point.x)
        self.assertTrue(0.1 <= point.y)

    def test_from_point_list(self):
        """Test from_point_list construction."""
        points = [Point3D(0.0, 0.0, 0.0), Point3D(1.0, 2.0, 3.0), Point3D(-1.0, -1.0, -1.0)]
        bbox = BBox3D.from_point_list(points)
        self.assertEqual(bbox.min, Point3D(-1.0, -1.0, -1.0))
        self.assertEqual(bbox.max, Point3D(1.0, 2.0, 3.0))

    def test_from_min_max(self):
        """Test from_min_max construction."""
        bbox = BBox3D.from_min_max([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        self.assertEqual(bbox.min, Point3D(0.0, 0.0, 0.0))
        self.assertEqual(bbox.max, Point3D(1.0, 1.0, 1.0))

    def test_from_center_size(self):
        """Test from_center_size construction."""
        bbox = BBox3D.from_center_size(Point3D(0.0, 0.0, 0.0), Point3D(2.0, 2.0, 2.0))
        self.assertEqual(bbox.min, Point3D(-1.0, -1.0, -1.0))
        self.assertEqual(bbox.max, Point3D(1.0, 1.0, 1.0))

    def test_to_dict(self):
        """Test to_dict serialization."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        result = bbox.to_dict()
        expected = {
            "min": {"x": 0.0, "y": 0.0, "z": 0.0},
            "max": {"x": 1.0, "y": 1.0, "z": 1.0},
        }
        self.assertEqual(result, expected)

    def test_from_dict(self):
        """Test from_dict deserialization."""
        d = {
            "min": {"x": 0.0, "y": 0.0, "z": 0.0},
            "max": {"x": 1.0, "y": 1.0, "z": 1.0},
        }
        bbox = BBox3D.from_dict(d)
        self.assertEqual(bbox.min, Point3D(0.0, 0.0, 0.0))
        self.assertEqual(bbox.max, Point3D(1.0, 1.0, 1.0))

    def test_str(self):
        """Test string representation."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        result = str(bbox)
        self.assertIn("BBox3D", result)
        self.assertIn("0.0", result)
        self.assertIn("1.0", result)

    def test_repr(self):
        """Test repr."""
        bbox = BBox3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 1.0, 1.0))
        result = repr(bbox)
        self.assertIn("BBox3D", result)

    def test_face_constants(self):
        """Test face index constants."""
        self.assertEqual(BBox3D.LEFT, 0)
        self.assertEqual(BBox3D.RIGHT, 1)
        self.assertEqual(BBox3D.BOTTOM, 2)
        self.assertEqual(BBox3D.TOP, 3)
        self.assertEqual(BBox3D.FRONT, 4)
        self.assertEqual(BBox3D.BACK, 5)


if __name__ == "__main__":
    unittest.main()
