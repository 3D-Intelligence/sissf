"""Unit tests for architecture defaults."""

import unittest

from sissf.architecture import (
    ArchitectureDefaults,
    CeilingDefault,
    DepthDefault,
    FloorDefault,
    GroundDefault,
    WallDefault,
)


class TestDepthDefault(unittest.TestCase):
    """Test DepthDefault class."""

    def test_init_default(self):
        """Test DepthDefault initialization with defaults."""
        default = DepthDefault()
        self.assertEqual(default.depth, 0.05)

    def test_init_custom(self):
        """Test DepthDefault initialization with custom value."""
        default = DepthDefault(depth=0.1)
        self.assertEqual(default.depth, 0.1)

    def test_to_dict(self):
        """Test to_dict serialization."""
        default = DepthDefault(depth=0.08)
        result = default.to_dict()
        self.assertEqual(result["depth"], 0.08)


class TestWallDefault(unittest.TestCase):
    """Test WallDefault class."""

    def test_init_default(self):
        """Test WallDefault initialization with defaults."""
        default = WallDefault()
        self.assertEqual(default.depth, 0.1)
        self.assertEqual(default.extra_height, 0.0)

    def test_init_custom(self):
        """Test WallDefault initialization with custom values."""
        default = WallDefault(depth=0.15, extra_height=0.2)
        self.assertEqual(default.depth, 0.15)
        self.assertEqual(default.extra_height, 0.2)

    def test_to_dict(self):
        """Test to_dict serialization."""
        default = WallDefault(depth=0.15, extra_height=0.2)
        result = default.to_dict()
        self.assertEqual(result["depth"], 0.15)
        self.assertEqual(result["extra_height"], 0.2)


class TestCeilingDefault(unittest.TestCase):
    """Test CeilingDefault class."""

    def test_init_default(self):
        """Test CeilingDefault initialization with defaults."""
        default = CeilingDefault()
        self.assertEqual(default.depth, 0.05)

    def test_init_custom(self):
        """Test CeilingDefault initialization with custom value."""
        default = CeilingDefault(depth=0.08)
        self.assertEqual(default.depth, 0.08)


class TestFloorDefault(unittest.TestCase):
    """Test FloorDefault class."""

    def test_init_default(self):
        """Test FloorDefault initialization with defaults."""
        default = FloorDefault()
        self.assertEqual(default.depth, 0.05)

    def test_init_custom(self):
        """Test FloorDefault initialization with custom value."""
        default = FloorDefault(depth=0.2)
        self.assertEqual(default.depth, 0.2)


class TestGroundDefault(unittest.TestCase):
    """Test GroundDefault class."""

    def test_init_default(self):
        """Test GroundDefault initialization with defaults."""
        default = GroundDefault()
        self.assertEqual(default.depth, 0.05)

    def test_init_custom(self):
        """Test GroundDefault initialization with custom value."""
        default = GroundDefault(depth=0.3)
        self.assertEqual(default.depth, 0.3)


class TestArchitectureDefaults(unittest.TestCase):
    """Test ArchitectureDefaults class."""

    def test_init_default(self):
        """Test ArchitectureDefaults initialization with defaults."""
        defaults = ArchitectureDefaults()
        self.assertIsNotNone(defaults.Wall)
        self.assertIsNotNone(defaults.Ceiling)
        self.assertIsNotNone(defaults.Floor)
        self.assertIsNotNone(defaults.Ground)
        self.assertEqual(defaults.Wall.depth, 0.1)
        self.assertEqual(defaults.Ceiling.depth, 0.05)
        self.assertEqual(defaults.Floor.depth, 0.05)
        self.assertEqual(defaults.Ground.depth, 0.05)

    def test_init_custom(self):
        """Test ArchitectureDefaults initialization with custom values."""
        defaults = ArchitectureDefaults(
            Wall=WallDefault(depth=0.15, extra_height=0.2),
            Ceiling=CeilingDefault(depth=0.1),
            Floor=FloorDefault(depth=0.25),
            Ground=GroundDefault(depth=0.3),
        )
        self.assertEqual(defaults.Wall.depth, 0.15)
        self.assertEqual(defaults.Wall.extra_height, 0.2)
        self.assertEqual(defaults.Ceiling.depth, 0.1)
        self.assertEqual(defaults.Floor.depth, 0.25)
        self.assertEqual(defaults.Ground.depth, 0.3)

    def test_to_dict(self):
        """Test to_dict serialization."""
        defaults = ArchitectureDefaults()
        result = defaults.to_dict()
        self.assertIn("Wall", result)
        self.assertIn("Ceiling", result)
        self.assertIn("Floor", result)
        self.assertIn("Ground", result)
        self.assertEqual(result["Wall"]["depth"], 0.1)
        self.assertEqual(result["Ceiling"]["depth"], 0.05)


if __name__ == "__main__":
    unittest.main()
