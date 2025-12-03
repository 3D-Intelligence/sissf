"""Unit tests for ArchWall class."""

import unittest

from sissf.architecture import ArchOpening, ArchWall
from sissf.geometry import Point3D


class TestArchWall(unittest.TestCase):
    """Test ArchWall class."""

    def test_init(self):
        """Test ArchWall initialization."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        self.assertEqual(wall.id, "wall_0")
        self.assertEqual(len(wall.points), 2)
        self.assertEqual(wall.height, 2.5)
        self.assertEqual(wall.depth, 0.1)
        self.assertEqual(wall.room_id, "room_0")
        self.assertEqual(wall.type, "Wall")
        self.assertEqual(len(wall.openings), 0)

    def test_init_with_material(self):
        """Test ArchWall initialization with material."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
            material="concrete",
            material_file_location="/path/to/material.mtl",
        )
        self.assertEqual(wall.material, "concrete")
        self.assertEqual(wall.material_file_location, "/path/to/material.mtl")

    def test_post_init_validates_points_count(self):
        """Test that __post_init__ validates exactly 2 points."""
        with self.assertRaises(ValueError) as cm:
            ArchWall(
                id="wall_0",
                points=[Point3D(0.0, 0.0, 0.0)],
                height=2.5,
                depth=0.1,
                room_id="room_0",
            )
        self.assertIn("ArchWall requires exactly 2 points", str(cm.exception))

    def test_post_init_validates_height_positive(self):
        """Test that __post_init__ validates height is positive."""
        with self.assertRaises(ValueError) as cm:
            ArchWall(
                id="wall_0",
                points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
                height=0.0,
                depth=0.1,
                room_id="room_0",
            )
        self.assertIn("ArchWall height must be positive", str(cm.exception))

    def test_post_init_validates_depth_positive(self):
        """Test that __post_init__ validates depth is positive."""
        with self.assertRaises(ValueError) as cm:
            ArchWall(
                id="wall_0",
                points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
                height=2.5,
                depth=-0.1,
                room_id="room_0",
            )
        self.assertIn("ArchWall depth must be positive", str(cm.exception))

    def test_width_property(self):
        """Test width property calculation."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        self.assertAlmostEqual(wall.width, 3.0)

    def test_width_property_diagonal(self):
        """Test width property with diagonal wall."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 4.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        self.assertAlmostEqual(wall.width, 5.0)

    def test_area_property_no_openings(self):
        """Test area property with no openings."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(4.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        expected_area = 4.0 * 2.5
        self.assertAlmostEqual(wall.area, expected_area)

    def test_area_property_with_openings(self):
        """Test area property with openings."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(4.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        wall.add_opening(opening)
        expected_area = (4.0 * 2.5) - (0.9 * 2.0)
        self.assertAlmostEqual(wall.area, expected_area)

    def test_add_opening(self):
        """Test adding opening to wall."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        wall.add_opening(opening)
        self.assertEqual(len(wall.openings), 1)
        self.assertEqual(wall.openings[0], opening)

    def test_add_multiple_openings(self):
        """Test adding multiple openings to wall."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(5.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        door = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.3,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        window = ArchOpening(
            id="opening_1",
            type="Window",
            parent_wall_id="wall_0",
            mid=0.7,
            width=1.2,
            height=1.5,
            elevation=1.0,
        )
        wall.add_opening(door)
        wall.add_opening(window)
        self.assertEqual(len(wall.openings), 2)

    def test_to_dict(self):
        """Test to_dict serialization."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
            material="brick",
        )
        result = wall.to_dict()
        self.assertEqual(result["id"], "wall_0")
        self.assertEqual(result["type"], "Wall")
        self.assertEqual(len(result["points"]), 2)
        self.assertEqual(result["height"], 2.5)
        self.assertEqual(result["depth"], 0.1)
        self.assertEqual(result["room_id"], "room_0")
        self.assertEqual(result["material"], "brick")
        self.assertEqual(len(result["openings"]), 0)

    def test_to_dict_with_openings(self):
        """Test to_dict serialization with openings."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        wall.add_opening(opening)
        result = wall.to_dict()
        self.assertEqual(len(result["openings"]), 1)
        self.assertEqual(result["openings"][0]["id"], "opening_0")

    def test_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "wall_0",
            "points": [{"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 3.0, "y": 0.0, "z": 0.0}],
            "height": 2.5,
            "depth": 0.1,
            "room_id": "room_0",
            "material": "concrete",
            "openings": [],
        }
        wall = ArchWall.from_dict(data)
        self.assertEqual(wall.id, "wall_0")
        self.assertEqual(len(wall.points), 2)
        self.assertEqual(wall.height, 2.5)
        self.assertEqual(wall.depth, 0.1)
        self.assertEqual(wall.room_id, "room_0")
        self.assertEqual(wall.material, "concrete")

    def test_from_dict_with_openings(self):
        """Test from_dict deserialization with openings."""
        data = {
            "id": "wall_0",
            "points": [{"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 3.0, "y": 0.0, "z": 0.0}],
            "height": 2.5,
            "depth": 0.1,
            "room_id": "room_0",
            "openings": [
                {
                    "id": "opening_0",
                    "type": "Door",
                    "parent_wall_id": "wall_0",
                    "mid": 0.5,
                    "width": 0.9,
                    "height": 2.0,
                    "elevation": 0.0,
                }
            ],
        }
        wall = ArchWall.from_dict(data)
        self.assertEqual(len(wall.openings), 1)
        self.assertEqual(wall.openings[0].id, "opening_0")

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        data = wall.to_dict()
        restored = ArchWall.from_dict(data)
        self.assertEqual(restored.id, wall.id)
        self.assertEqual(len(restored.points), len(wall.points))
        self.assertEqual(restored.height, wall.height)
        self.assertEqual(restored.depth, wall.depth)
        self.assertEqual(restored.room_id, wall.room_id)


if __name__ == "__main__":
    unittest.main()
