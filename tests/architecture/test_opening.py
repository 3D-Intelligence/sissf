"""Unit tests for ArchOpening class."""

import unittest

from sissf.architecture import ArchOpening


class TestArchOpening(unittest.TestCase):
    """Test ArchOpening class."""

    def test_init(self):
        """Test ArchOpening initialization."""
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        self.assertEqual(opening.id, "opening_0")
        self.assertEqual(opening.type, "Door")
        self.assertEqual(opening.parent_wall_id, "wall_0")
        self.assertEqual(opening.mid, 0.5)
        self.assertEqual(opening.width, 0.9)
        self.assertEqual(opening.height, 2.0)
        self.assertEqual(opening.elevation, 0.0)

    def test_init_with_metadata(self):
        """Test ArchOpening initialization with metadata."""
        metadata = {"color": "brown"}
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
            metadata=metadata,
        )
        self.assertEqual(opening.metadata, metadata)

    def test_init_window(self):
        """Test ArchOpening initialization for window."""
        opening = ArchOpening(
            id="opening_1",
            type="Window",
            parent_wall_id="wall_0",
            mid=0.3,
            width=1.2,
            height=1.5,
            elevation=1.0,
        )
        self.assertEqual(opening.type, "Window")
        self.assertEqual(opening.elevation, 1.0)

    def test_post_init_validates_mid_range(self):
        """Test that __post_init__ validates mid is between 0 and 1."""
        with self.assertRaises(ValueError) as cm:
            ArchOpening(
                id="opening_0",
                type="Door",
                parent_wall_id="wall_0",
                mid=1.5,
                width=0.9,
                height=2.0,
                elevation=0.0,
            )
        self.assertIn("Opening mid must be between 0 and 1", str(cm.exception))

    def test_post_init_validates_mid_negative(self):
        """Test that __post_init__ validates mid is not negative."""
        with self.assertRaises(ValueError) as cm:
            ArchOpening(
                id="opening_0",
                type="Door",
                parent_wall_id="wall_0",
                mid=-0.1,
                width=0.9,
                height=2.0,
                elevation=0.0,
            )
        self.assertIn("Opening mid must be between 0 and 1", str(cm.exception))

    def test_post_init_validates_type(self):
        """Test that __post_init__ validates type is Door or Window."""
        with self.assertRaises(ValueError) as cm:
            ArchOpening(
                id="opening_0",
                type="InvalidType",
                parent_wall_id="wall_0",
                mid=0.5,
                width=0.9,
                height=2.0,
                elevation=0.0,
            )
        self.assertIn("Opening type must be 'Door' or 'Window'", str(cm.exception))

    def test_to_dict(self):
        """Test to_dict serialization."""
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
            metadata={"color": "brown"},
        )
        result = opening.to_dict()
        self.assertEqual(result["id"], "opening_0")
        self.assertEqual(result["type"], "Door")
        self.assertEqual(result["parent_wall_id"], "wall_0")
        self.assertEqual(result["mid"], 0.5)
        self.assertEqual(result["width"], 0.9)
        self.assertEqual(result["height"], 2.0)
        self.assertEqual(result["elevation"], 0.0)
        self.assertEqual(result["metadata"], {"color": "brown"})

    def test_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "opening_0",
            "type": "Window",
            "parent_wall_id": "wall_0",
            "mid": 0.3,
            "width": 1.2,
            "height": 1.5,
            "elevation": 1.0,
            "metadata": {"frame": "aluminum"},
        }
        opening = ArchOpening.from_dict(data)
        self.assertEqual(opening.id, "opening_0")
        self.assertEqual(opening.type, "Window")
        self.assertEqual(opening.parent_wall_id, "wall_0")
        self.assertEqual(opening.mid, 0.3)
        self.assertEqual(opening.width, 1.2)
        self.assertEqual(opening.height, 1.5)
        self.assertEqual(opening.elevation, 1.0)
        self.assertEqual(opening.metadata, {"frame": "aluminum"})

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        data = opening.to_dict()
        restored = ArchOpening.from_dict(data)
        self.assertEqual(restored.id, opening.id)
        self.assertEqual(restored.type, opening.type)
        self.assertEqual(restored.parent_wall_id, opening.parent_wall_id)
        self.assertEqual(restored.mid, opening.mid)
        self.assertEqual(restored.width, opening.width)
        self.assertEqual(restored.height, opening.height)
        self.assertEqual(restored.elevation, opening.elevation)


class MockOpeningAdapter:
    """Mock adapter for testing format registration."""

    @staticmethod
    def from_format(obj, **kwargs):
        """Mock from_format."""
        return ArchOpening(
            id=obj.get("opening_id", "opening_0"),
            type=obj.get("opening_type", "Door"),
            parent_wall_id=obj.get("wall", "wall_0"),
            mid=obj.get("position", 0.5),
            width=obj.get("w", 0.9),
            height=obj.get("h", 2.0),
            elevation=obj.get("elev", 0.0),
        )

    @staticmethod
    def to_format(instance, **kwargs):
        """Mock to_format."""
        return {
            "opening_id": instance.id,
            "opening_type": instance.type,
            "wall": instance.parent_wall_id,
            "position": instance.mid,
            "w": instance.width,
            "h": instance.height,
            "elev": instance.elevation,
        }


class TestArchOpeningAdapters(unittest.TestCase):
    """Test ArchOpening adapter registration and usage."""

    def test_register_adapter(self):
        """Test registering a format adapter."""
        ArchOpening.register_adapter("mock_format", MockOpeningAdapter)
        # Should not raise an error

    def test_from_format(self):
        """Test from_format with registered adapter."""
        ArchOpening.register_adapter("mock_format", MockOpeningAdapter)
        obj = {
            "opening_id": "opening_1",
            "opening_type": "Window",
            "wall": "wall_1",
            "position": 0.3,
            "w": 1.2,
            "h": 1.5,
            "elev": 1.0,
        }
        opening = ArchOpening.from_format("mock_format", obj)
        self.assertEqual(opening.id, "opening_1")
        self.assertEqual(opening.type, "Window")
        self.assertEqual(opening.parent_wall_id, "wall_1")
        self.assertEqual(opening.mid, 0.3)

    def test_from_format_unregistered(self):
        """Test from_format with unregistered format."""
        with self.assertRaises(ValueError) as cm:
            ArchOpening.from_format("nonexistent_format", {})
        self.assertIn("No adapter registered", str(cm.exception))

    def test_to_format(self):
        """Test to_format with registered adapter."""
        ArchOpening.register_adapter("mock_format", MockOpeningAdapter)
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        result = opening.to_format("mock_format")
        self.assertEqual(result["opening_id"], "opening_0")
        self.assertEqual(result["opening_type"], "Door")
        self.assertEqual(result["wall"], "wall_0")
        self.assertEqual(result["position"], 0.5)

    def test_to_format_unregistered(self):
        """Test to_format with unregistered format."""
        opening = ArchOpening(
            id="opening_0",
            type="Door",
            parent_wall_id="wall_0",
            mid=0.5,
            width=0.9,
            height=2.0,
            elevation=0.0,
        )
        with self.assertRaises(ValueError) as cm:
            opening.to_format("nonexistent_format")
        self.assertIn("No adapter registered", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
