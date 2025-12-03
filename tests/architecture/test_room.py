"""Unit tests for ArchRoom class."""

import unittest

from sissf.architecture import ArchCeiling, ArchFloor, ArchRoom
from sissf.geometry import Point3D


class TestArchRoom(unittest.TestCase):
    """Test ArchRoom class."""

    def test_init(self):
        """Test ArchRoom initialization."""
        room = ArchRoom(id="room_0")
        self.assertEqual(room.id, "room_0")
        self.assertEqual(room.type, "Room")
        self.assertEqual(len(room.wall_ids), 0)
        self.assertIsNone(room.floor)
        self.assertIsNone(room.ceiling)

    def test_init_with_wall_ids(self):
        """Test ArchRoom initialization with wall IDs."""
        room = ArchRoom(id="room_0", wall_ids=["wall_0", "wall_1", "wall_2", "wall_3"])
        self.assertEqual(len(room.wall_ids), 4)
        self.assertEqual(room.wall_ids[0], "wall_0")

    def test_init_with_floor(self):
        """Test ArchRoom initialization with floor."""
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
        room = ArchRoom(id="room_0", floor=floor)
        self.assertIsNotNone(room.floor)
        self.assertEqual(room.floor.id, "floor_0")

    def test_init_with_ceiling(self):
        """Test ArchRoom initialization with ceiling."""
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
        room = ArchRoom(id="room_0", ceiling=ceiling)
        self.assertIsNotNone(room.ceiling)
        self.assertEqual(room.ceiling.id, "ceiling_0")

    def test_init_with_metadata(self):
        """Test ArchRoom initialization with metadata."""
        metadata = {"name": "Living Room", "area": 12.0}
        room = ArchRoom(id="room_0", metadata=metadata)
        self.assertEqual(room.metadata, metadata)

    def test_to_dict_minimal(self):
        """Test to_dict serialization with minimal data."""
        room = ArchRoom(id="room_0")
        result = room.to_dict()
        self.assertEqual(result["id"], "room_0")
        self.assertEqual(result["type"], "Room")
        self.assertEqual(len(result["wall_ids"]), 0)
        self.assertIsNone(result["floor"])
        self.assertIsNone(result["ceiling"])

    def test_to_dict_with_walls(self):
        """Test to_dict serialization with wall IDs."""
        room = ArchRoom(id="room_0", wall_ids=["wall_0", "wall_1"])
        result = room.to_dict()
        self.assertEqual(len(result["wall_ids"]), 2)
        self.assertEqual(result["wall_ids"][0], "wall_0")

    def test_to_dict_with_floor(self):
        """Test to_dict serialization with floor."""
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
        room = ArchRoom(id="room_0", floor=floor)
        result = room.to_dict()
        self.assertIsNotNone(result["floor"])
        self.assertEqual(result["floor"]["id"], "floor_0")

    def test_to_dict_with_ceiling(self):
        """Test to_dict serialization with ceiling."""
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
        room = ArchRoom(id="room_0", ceiling=ceiling)
        result = room.to_dict()
        self.assertIsNotNone(result["ceiling"])
        self.assertEqual(result["ceiling"]["id"], "ceiling_0")

    def test_from_dict_minimal(self):
        """Test from_dict deserialization with minimal data."""
        data = {"id": "room_0"}
        room = ArchRoom.from_dict(data)
        self.assertEqual(room.id, "room_0")
        self.assertEqual(len(room.wall_ids), 0)
        self.assertIsNone(room.floor)
        self.assertIsNone(room.ceiling)

    def test_from_dict_with_walls(self):
        """Test from_dict deserialization with wall IDs."""
        data = {"id": "room_0", "wall_ids": ["wall_0", "wall_1", "wall_2"]}
        room = ArchRoom.from_dict(data)
        self.assertEqual(len(room.wall_ids), 3)
        self.assertEqual(room.wall_ids[1], "wall_1")

    def test_from_dict_with_floor(self):
        """Test from_dict deserialization with floor."""
        data = {
            "id": "room_0",
            "floor": {
                "id": "floor_0",
                "points": [
                    {"x": 0.0, "y": 0.0, "z": 0.0},
                    {"x": 3.0, "y": 0.0, "z": 0.0},
                    {"x": 3.0, "y": 0.0, "z": 4.0},
                    {"x": 0.0, "y": 0.0, "z": 4.0},
                ],
                "depth": 0.2,
                "room_id": "room_0",
            },
        }
        room = ArchRoom.from_dict(data)
        self.assertIsNotNone(room.floor)
        self.assertEqual(room.floor.id, "floor_0")

    def test_from_dict_with_ceiling(self):
        """Test from_dict deserialization with ceiling."""
        data = {
            "id": "room_0",
            "ceiling": {
                "id": "ceiling_0",
                "points": [
                    {"x": 0.0, "y": 2.5, "z": 0.0},
                    {"x": 3.0, "y": 2.5, "z": 0.0},
                    {"x": 3.0, "y": 2.5, "z": 4.0},
                    {"x": 0.0, "y": 2.5, "z": 4.0},
                ],
                "depth": 0.1,
                "room_id": "room_0",
            },
        }
        room = ArchRoom.from_dict(data)
        self.assertIsNotNone(room.ceiling)
        self.assertEqual(room.ceiling.id, "ceiling_0")

    def test_from_dict_none_floor(self):
        """Test from_dict with explicit None floor."""
        data = {"id": "room_0", "floor": None}
        room = ArchRoom.from_dict(data)
        self.assertIsNone(room.floor)

    def test_from_dict_none_ceiling(self):
        """Test from_dict with explicit None ceiling."""
        data = {"id": "room_0", "ceiling": None}
        room = ArchRoom.from_dict(data)
        self.assertIsNone(room.ceiling)

    def test_roundtrip_dict_minimal(self):
        """Test roundtrip conversion to/from dict with minimal data."""
        room = ArchRoom(id="room_0")
        data = room.to_dict()
        restored = ArchRoom.from_dict(data)
        self.assertEqual(restored.id, room.id)
        self.assertEqual(len(restored.wall_ids), len(room.wall_ids))

    def test_roundtrip_dict_complete(self):
        """Test roundtrip conversion to/from dict with complete data."""
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
        room = ArchRoom(
            id="room_0",
            wall_ids=["wall_0", "wall_1", "wall_2", "wall_3"],
            floor=floor,
            ceiling=ceiling,
        )
        data = room.to_dict()
        restored = ArchRoom.from_dict(data)
        self.assertEqual(restored.id, room.id)
        self.assertEqual(len(restored.wall_ids), len(room.wall_ids))
        self.assertIsNotNone(restored.floor)
        self.assertIsNotNone(restored.ceiling)


if __name__ == "__main__":
    unittest.main()
