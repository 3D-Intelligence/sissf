"""Unit tests for ArchFloor class."""

import unittest

from sissf.architecture import ArchFloor
from sissf.geometry import Point3D


class TestArchFloor(unittest.TestCase):
    """Test ArchFloor class."""

    def test_init(self):
        """Test ArchFloor initialization."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 4.0),
                Point3D(0.0, 0.0, 4.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        self.assertEqual(floor.id, "floor_0")
        self.assertEqual(len(floor.points), 4)
        self.assertEqual(floor.depth, 0.2)
        self.assertEqual(floor.room_id, "room_0")
        self.assertEqual(floor.type, "Floor")

    def test_init_with_material(self):
        """Test ArchFloor initialization with material."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 4.0),
                Point3D(0.0, 0.0, 4.0),
            ],
            depth=0.2,
            room_id="room_0",
            material="wood",
            material_file_location="/path/to/material.mtl",
        )
        self.assertEqual(floor.material, "wood")
        self.assertEqual(floor.material_file_location, "/path/to/material.mtl")

    def test_area_rectangle(self):
        """Test area calculation for rectangular floor."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 4.0),
                Point3D(0.0, 0.0, 4.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        expected_area = 3.0 * 4.0
        self.assertAlmostEqual(floor.area, expected_area)

    def test_area_square(self):
        """Test area calculation for square floor."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(2.0, 0.0, 0.0),
                Point3D(2.0, 0.0, 2.0),
                Point3D(0.0, 0.0, 2.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        expected_area = 2.0 * 2.0
        self.assertAlmostEqual(floor.area, expected_area)

    def test_area_triangle(self):
        """Test area calculation for triangular floor."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(4.0, 0.0, 0.0),
                Point3D(0.0, 0.0, 3.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        expected_area = 0.5 * 4.0 * 3.0
        self.assertAlmostEqual(floor.area, expected_area)

    def test_area_l_shape(self):
        """Test area calculation for L-shaped floor."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(2.0, 0.0, 0.0),
                Point3D(2.0, 0.0, 1.0),
                Point3D(3.0, 0.0, 1.0),
                Point3D(3.0, 0.0, 3.0),
                Point3D(0.0, 0.0, 3.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        # L-shape area: Using shoelace formula, the actual result is 8
        expected_area = 8.0
        self.assertAlmostEqual(floor.area, expected_area)

    def test_area_too_few_points(self):
        """Test area returns 0 for too few points."""
        floor = ArchFloor(
            id="floor_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            depth=0.2,
            room_id="room_0",
        )
        self.assertEqual(floor.area, 0.0)

    def test_to_dict(self):
        """Test to_dict serialization."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 4.0),
                Point3D(0.0, 0.0, 4.0),
            ],
            depth=0.2,
            room_id="room_0",
            material="tile",
        )
        result = floor.to_dict()
        self.assertEqual(result["id"], "floor_0")
        self.assertEqual(result["type"], "Floor")
        self.assertEqual(len(result["points"]), 4)
        self.assertEqual(result["depth"], 0.2)
        self.assertEqual(result["room_id"], "room_0")
        self.assertEqual(result["material"], "tile")

    def test_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "floor_0",
            "points": [
                {"x": 0.0, "y": 0.0, "z": 0.0},
                {"x": 3.0, "y": 0.0, "z": 0.0},
                {"x": 3.0, "y": 0.0, "z": 4.0},
                {"x": 0.0, "y": 0.0, "z": 4.0},
            ],
            "depth": 0.2,
            "room_id": "room_0",
            "material": "carpet",
        }
        floor = ArchFloor.from_dict(data)
        self.assertEqual(floor.id, "floor_0")
        self.assertEqual(len(floor.points), 4)
        self.assertEqual(floor.depth, 0.2)
        self.assertEqual(floor.room_id, "room_0")
        self.assertEqual(floor.material, "carpet")

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        floor = ArchFloor(
            id="floor_0",
            points=[
                Point3D(0.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 0.0),
                Point3D(3.0, 0.0, 4.0),
                Point3D(0.0, 0.0, 4.0),
            ],
            depth=0.2,
            room_id="room_0",
        )
        data = floor.to_dict()
        restored = ArchFloor.from_dict(data)
        self.assertEqual(restored.id, floor.id)
        self.assertEqual(len(restored.points), len(floor.points))
        self.assertEqual(restored.depth, floor.depth)
        self.assertEqual(restored.room_id, floor.room_id)
        self.assertAlmostEqual(restored.area, floor.area)


if __name__ == "__main__":
    unittest.main()
