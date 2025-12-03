"""Unit tests for Architecture class."""

import unittest

from sissf.architecture import (
    ArchCeiling,
    Architecture,
    ArchFloor,
    ArchOpening,
    ArchRoom,
    ArchWall,
)
from sissf.geometry import Point3D


class TestArchitecture(unittest.TestCase):
    """Test Architecture class."""

    def test_init_default(self):
        """Test Architecture initialization with defaults."""
        arch = Architecture()
        self.assertIsNotNone(arch.id)
        self.assertEqual(arch.version, "arch@0.0.1")
        self.assertEqual(arch.up.y, 1)
        self.assertEqual(arch.front.z, -1)
        self.assertEqual(arch.scale_to_meters, 1.0)
        self.assertEqual(len(arch.rooms), 0)
        self.assertEqual(len(arch.walls), 0)
        self.assertEqual(len(arch.floors), 0)
        self.assertEqual(len(arch.ceilings), 0)

    def test_init_with_id(self):
        """Test Architecture initialization with custom ID."""
        arch = Architecture(id="arch_custom")
        self.assertEqual(arch.id, "arch_custom")

    def test_doors_property_empty(self):
        """Test doors property with no doors."""
        arch = Architecture()
        self.assertEqual(len(arch.doors), 0)

    def test_doors_property_with_doors(self):
        """Test doors property with doors."""
        arch = Architecture()
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        door = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        wall.add_opening(door)
        arch.add_wall(wall)
        self.assertEqual(len(arch.doors), 1)
        self.assertEqual(arch.doors[0].id, "opening_0")

    def test_windows_property_empty(self):
        """Test windows property with no windows."""
        arch = Architecture()
        self.assertEqual(len(arch.windows), 0)

    def test_windows_property_with_windows(self):
        """Test windows property with windows."""
        arch = Architecture()
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        window = ArchOpening(
            id="opening_0",
            type="Window",
            parent_wall_id="wall_0",
            mid=0.5,
            width=1.2,
            height=1.5,
            elevation=1.0,
        )
        wall.add_opening(window)
        arch.add_wall(wall)
        self.assertEqual(len(arch.windows), 1)
        self.assertEqual(arch.windows[0].id, "opening_0")

    def test_doors_and_windows_mixed(self):
        """Test doors and windows properties with mixed openings."""
        arch = Architecture()
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(5.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        door = ArchOpening(
            id="door_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.3,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        window = ArchOpening(
            id="window_0",
            type="Window",
            parent_wall_id="wall_0",
            mid=0.7,
            width=1.2,
            height=1.5,
            elevation=1.0,
        )
        wall.add_opening(door)
        wall.add_opening(window)
        arch.add_wall(wall)
        self.assertEqual(len(arch.doors), 1)
        self.assertEqual(len(arch.windows), 1)
        self.assertEqual(arch.doors[0].id, "door_0")
        self.assertEqual(arch.windows[0].id, "window_0")

    def test_add_room(self):
        """Test adding room to architecture."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
        self.assertEqual(len(arch.rooms), 1)
        self.assertIn("room_0", arch.rooms)

    def test_add_wall(self):
        """Test adding wall to architecture."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        arch.add_wall(wall)
        self.assertEqual(len(arch.walls), 1)
        self.assertIn("wall_0", arch.walls)
        # Wall should be added to room's wall_ids
        self.assertIn("wall_0", arch.rooms["room_0"].wall_ids)

    def test_add_wall_without_room(self):
        """Test adding wall without corresponding room."""
        arch = Architecture()
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_nonexistent",
        )
        arch.add_wall(wall)
        self.assertEqual(len(arch.walls), 1)
        # Should not crash even if room doesn't exist

    def test_add_floor(self):
        """Test adding floor to architecture."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
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
        arch.add_floor(floor)
        self.assertEqual(len(arch.floors), 1)
        self.assertIn("floor_0", arch.floors)
        # Floor should be linked to room
        self.assertIsNotNone(arch.rooms["room_0"].floor)
        self.assertEqual(arch.rooms["room_0"].floor.id, "floor_0")

    def test_add_ceiling(self):
        """Test adding ceiling to architecture."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
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
        arch.add_ceiling(ceiling)
        self.assertEqual(len(arch.ceilings), 1)
        self.assertIn("ceiling_0", arch.ceilings)
        # Ceiling should be linked to room
        self.assertIsNotNone(arch.rooms["room_0"].ceiling)
        self.assertEqual(arch.rooms["room_0"].ceiling.id, "ceiling_0")

    def test_get_room(self):
        """Test get_room method."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
        retrieved = arch.get_room("room_0")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "room_0")

    def test_get_room_nonexistent(self):
        """Test get_room with nonexistent ID."""
        arch = Architecture()
        retrieved = arch.get_room("nonexistent")
        self.assertIsNone(retrieved)

    def test_get_wall(self):
        """Test get_wall method."""
        arch = Architecture()
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        arch.add_wall(wall)
        retrieved = arch.get_wall("wall_0")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "wall_0")

    def test_get_wall_nonexistent(self):
        """Test get_wall with nonexistent ID."""
        arch = Architecture()
        retrieved = arch.get_wall("nonexistent")
        self.assertIsNone(retrieved)

    def test_to_dict(self):
        """Test to_dict serialization."""
        arch = Architecture(id="arch_0")
        room = ArchRoom(id="room_0")
        arch.add_room(room)
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        arch.add_wall(wall)

        result = arch.to_dict()
        self.assertEqual(result["id"], "arch_0")
        self.assertEqual(result["version"], "arch@0.0.1")
        self.assertIn("up", result)
        self.assertIn("front", result)
        self.assertEqual(len(result["rooms"]), 1)
        self.assertEqual(len(result["walls"]), 1)

    def test_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "arch_0",
            "version": "arch@0.0.1",
            "up": {"x": 0, "y": 1, "z": 0},
            "front": {"x": 0, "y": 0, "z": -1},
            "scale_to_meters": 1.0,
            "rooms": [{"id": "room_0"}],
            "walls": [
                {
                    "id": "wall_0",
                    "points": [
                        {"x": 0.0, "y": 0.0, "z": 0.0},
                        {"x": 3.0, "y": 0.0, "z": 0.0},
                    ],
                    "height": 2.5,
                    "depth": 0.1,
                    "room_id": "room_0",
                    "openings": [],
                }
            ],
            "floors": [],
            "ceilings": [],
        }
        arch = Architecture.from_dict(data)
        self.assertEqual(arch.id, "arch_0")
        self.assertEqual(len(arch.rooms), 1)
        self.assertEqual(len(arch.walls), 1)
        self.assertIn("room_0", arch.rooms)
        self.assertIn("wall_0", arch.walls)
        # Wall should be linked to room
        self.assertIn("wall_0", arch.rooms["room_0"].wall_ids)

    def test_from_dict_with_defaults(self):
        """Test from_dict with defaults specified."""
        data = {
            "id": "arch_0",
            "defaults": {
                "Wall": {"depth": 0.15, "extra_height": 0.1},
                "Floor": {"depth": 0.25},
            },
            "rooms": [],
            "walls": [],
            "floors": [],
            "ceilings": [],
        }
        arch = Architecture.from_dict(data)
        self.assertEqual(arch.defaults.Wall.depth, 0.15)
        self.assertEqual(arch.defaults.Wall.extra_height, 0.1)
        self.assertEqual(arch.defaults.Floor.depth, 0.25)

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        arch = Architecture()
        room = ArchRoom(id="room_0")
        arch.add_room(room)
        wall = ArchWall(
            id="wall_0",
            points=[Point3D(0.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0)],
            height=2.5,
            depth=0.1,
            room_id="room_0",
        )
        arch.add_wall(wall)
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
        arch.add_floor(floor)

        data = arch.to_dict()
        restored = Architecture.from_dict(data)

        self.assertEqual(restored.id, arch.id)
        self.assertEqual(len(restored.rooms), len(arch.rooms))
        self.assertEqual(len(restored.walls), len(arch.walls))
        self.assertEqual(len(restored.floors), len(arch.floors))


if __name__ == "__main__":
    unittest.main()
