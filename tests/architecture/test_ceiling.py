"""Unit tests for ArchCeiling class."""

import unittest

from sissf.architecture import ArchCeiling
from sissf.geometry import Point3D


class TestArchCeiling(unittest.TestCase):
    """Test ArchCeiling class."""

    def test_init(self):
        """Test ArchCeiling initialization."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 4.0),
                Point3D(0.0, 2.5, 4.0),
            ],
            depth=0.1,
            room_id="room_0",
        )
        self.assertEqual(ceiling.id, "ceiling_0")
        self.assertEqual(len(ceiling.points), 4)
        self.assertEqual(ceiling.depth, 0.1)
        self.assertEqual(ceiling.room_id, "room_0")
        self.assertEqual(ceiling.type, "Ceiling")

    def test_init_with_material(self):
        """Test ArchCeiling initialization with material."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 4.0),
                Point3D(0.0, 2.5, 4.0),
            ],
            depth=0.1,
            room_id="room_0",
            material="drywall",
            material_file_location="/path/to/material.mtl",
        )
        self.assertEqual(ceiling.material, "drywall")
        self.assertEqual(ceiling.material_file_location, "/path/to/material.mtl")

    def test_area_rectangle(self):
        """Test area calculation for rectangular ceiling."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 4.0),
                Point3D(0.0, 2.5, 4.0),
            ],
            depth=0.1,
            room_id="room_0",
        )
        expected_area = 3.0 * 4.0
        self.assertAlmostEqual(ceiling.area, expected_area)

    def test_area_square(self):
        """Test area calculation for square ceiling."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(2.0, 2.5, 0.0),
                Point3D(2.0, 2.5, 2.0),
                Point3D(0.0, 2.5, 2.0),
            ],
            depth=0.1,
            room_id="room_0",
        )
        expected_area = 2.0 * 2.0
        self.assertAlmostEqual(ceiling.area, expected_area)

    def test_area_triangle(self):
        """Test area calculation for triangular ceiling."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(4.0, 2.5, 0.0),
                Point3D(0.0, 2.5, 3.0),
            ],
            depth=0.1,
            room_id="room_0",
        )
        expected_area = 0.5 * 4.0 * 3.0
        self.assertAlmostEqual(ceiling.area, expected_area)

    def test_area_pentagon(self):
        """Test area calculation for pentagonal ceiling."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(2.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 1.5),
                Point3D(1.5, 2.5, 3.0),
                Point3D(-0.5, 2.5, 1.5),
            ],
            depth=0.1,
            room_id="room_0",
        )
        # Pentagon area should be positive
        self.assertGreater(ceiling.area, 0)

    def test_area_too_few_points(self):
        """Test area returns 0 for too few points."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[Point3D(0.0, 2.5, 0.0), Point3D(3.0, 2.5, 0.0)],
            depth=0.1,
            room_id="room_0",
        )
        self.assertEqual(ceiling.area, 0.0)

    def test_to_dict(self):
        """Test to_dict serialization."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 4.0),
                Point3D(0.0, 2.5, 4.0),
            ],
            depth=0.1,
            room_id="room_0",
            material="plaster",
        )
        result = ceiling.to_dict()
        self.assertEqual(result["id"], "ceiling_0")
        self.assertEqual(result["type"], "Ceiling")
        self.assertEqual(len(result["points"]), 4)
        self.assertEqual(result["depth"], 0.1)
        self.assertEqual(result["room_id"], "room_0")
        self.assertEqual(result["material"], "plaster")

    def test_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "ceiling_0",
            "points": [
                {"x": 0.0, "y": 2.5, "z": 0.0},
                {"x": 3.0, "y": 2.5, "z": 0.0},
                {"x": 3.0, "y": 2.5, "z": 4.0},
                {"x": 0.0, "y": 2.5, "z": 4.0},
            ],
            "depth": 0.1,
            "room_id": "room_0",
            "material": "acoustic_tile",
        }
        ceiling = ArchCeiling.from_dict(data)
        self.assertEqual(ceiling.id, "ceiling_0")
        self.assertEqual(len(ceiling.points), 4)
        self.assertEqual(ceiling.depth, 0.1)
        self.assertEqual(ceiling.room_id, "room_0")
        self.assertEqual(ceiling.material, "acoustic_tile")

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        ceiling = ArchCeiling(
            id="ceiling_0",
            points=[
                Point3D(0.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 0.0),
                Point3D(3.0, 2.5, 4.0),
                Point3D(0.0, 2.5, 4.0),
            ],
            depth=0.1,
            room_id="room_0",
        )
        data = ceiling.to_dict()
        restored = ArchCeiling.from_dict(data)
        self.assertEqual(restored.id, ceiling.id)
        self.assertEqual(len(restored.points), len(ceiling.points))
        self.assertEqual(restored.depth, ceiling.depth)
        self.assertEqual(restored.room_id, ceiling.room_id)
        self.assertAlmostEqual(restored.area, ceiling.area)


if __name__ == "__main__":
    unittest.main()
