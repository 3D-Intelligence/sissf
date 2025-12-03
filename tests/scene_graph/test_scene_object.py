"""Unit tests for SceneObject class."""

import unittest

from sissf.scene_graph import SceneObject


class TestSceneObject(unittest.TestCase):
    """Test SceneObject class."""

    def test_init_minimal(self):
        """Test SceneObject initialization with minimal data."""
        obj = SceneObject(name="chair")
        self.assertEqual(obj.name, "chair")
        self.assertIsNotNone(obj.id)
        self.assertEqual(len(obj.attributes), 0)
        self.assertIsNone(obj.description)
        self.assertIsNone(obj.embedding)
        self.assertEqual(len(obj.metadata), 0)

    def test_init_with_id(self):
        """Test SceneObject initialization with custom ID."""
        obj = SceneObject(name="table", id="table_001")
        self.assertEqual(obj.id, "table_001")
        self.assertEqual(obj.name, "table")

    def test_init_with_attributes(self):
        """Test SceneObject initialization with attributes."""
        obj = SceneObject(name="chair", attributes=["wooden", "dining"])
        self.assertEqual(len(obj.attributes), 2)
        self.assertIn("wooden", obj.attributes)
        self.assertIn("dining", obj.attributes)

    def test_init_with_description(self):
        """Test SceneObject initialization with description."""
        obj = SceneObject(name="sofa", description="A comfortable 3-seater sofa")
        self.assertEqual(obj.description, "A comfortable 3-seater sofa")

    def test_init_with_embedding(self):
        """Test SceneObject initialization with embedding."""
        embedding = [0.1, 0.2, 0.3, 0.4]
        obj = SceneObject(name="lamp", embedding=embedding)
        self.assertEqual(obj.embedding, embedding)

    def test_init_with_metadata(self):
        """Test SceneObject initialization with metadata."""
        metadata = {"color": "blue", "material": "fabric"}
        obj = SceneObject(name="chair", metadata=metadata)
        self.assertEqual(obj.metadata, metadata)

    def test_post_init_validates_empty_name(self):
        """Test that __post_init__ validates empty name."""
        with self.assertRaises(ValueError) as cm:
            SceneObject(name="")
        self.assertIn("name cannot be empty", str(cm.exception))

    def test_add_attribute(self):
        """Test adding attribute to object."""
        obj = SceneObject(name="desk")
        obj.add_attribute("wooden")
        self.assertIn("wooden", obj.attributes)
        self.assertEqual(len(obj.attributes), 1)

    def test_add_attribute_duplicate(self):
        """Test adding duplicate attribute doesn't create duplicates."""
        obj = SceneObject(name="chair", attributes=["wooden"])
        obj.add_attribute("wooden")
        self.assertEqual(len(obj.attributes), 1)
        self.assertIn("wooden", obj.attributes)

    def test_remove_attribute(self):
        """Test removing attribute from object."""
        obj = SceneObject(name="table", attributes=["wooden", "dining"])
        obj.remove_attribute("wooden")
        self.assertNotIn("wooden", obj.attributes)
        self.assertEqual(len(obj.attributes), 1)

    def test_remove_attribute_nonexistent(self):
        """Test removing nonexistent attribute doesn't raise error."""
        obj = SceneObject(name="chair", attributes=["wooden"])
        obj.remove_attribute("metal")  # Should not raise
        self.assertEqual(len(obj.attributes), 1)

    def test_has_attribute(self):
        """Test checking if object has attribute."""
        obj = SceneObject(name="chair", attributes=["wooden", "dining"])
        self.assertTrue(obj.has_attribute("wooden"))
        self.assertTrue(obj.has_attribute("dining"))
        self.assertFalse(obj.has_attribute("metal"))

    def test_to_dict_minimal(self):
        """Test to_dict serialization with minimal data."""
        obj = SceneObject(name="chair", id="chair_001")
        result = obj.to_dict()
        self.assertEqual(result["id"], "chair_001")
        self.assertEqual(result["name"], "chair")
        self.assertEqual(result["attributes"], [])
        self.assertNotIn("description", result)
        self.assertNotIn("embedding", result)
        self.assertNotIn("metadata", result)

    def test_to_dict_complete(self):
        """Test to_dict serialization with complete data."""
        obj = SceneObject(
            name="sofa",
            id="sofa_001",
            attributes=["comfortable", "leather"],
            description="A leather sofa",
            embedding=[0.1, 0.2],
            metadata={"color": "brown"},
        )
        result = obj.to_dict()
        self.assertEqual(result["id"], "sofa_001")
        self.assertEqual(result["name"], "sofa")
        self.assertEqual(len(result["attributes"]), 2)
        self.assertEqual(result["description"], "A leather sofa")
        self.assertEqual(result["embedding"], [0.1, 0.2])
        self.assertEqual(result["metadata"]["color"], "brown")

    def test_from_dict_minimal(self):
        """Test from_dict deserialization with minimal data."""
        data = {"name": "chair"}
        obj = SceneObject.from_dict(data)
        self.assertEqual(obj.name, "chair")
        self.assertIsNotNone(obj.id)
        self.assertEqual(len(obj.attributes), 0)

    def test_from_dict_with_id(self):
        """Test from_dict deserialization with ID."""
        data = {"id": "table_001", "name": "table"}
        obj = SceneObject.from_dict(data)
        self.assertEqual(obj.id, "table_001")
        self.assertEqual(obj.name, "table")

    def test_from_dict_complete(self):
        """Test from_dict deserialization with complete data."""
        data = {
            "id": "lamp_001",
            "name": "lamp",
            "attributes": ["modern", "LED"],
            "description": "A modern LED lamp",
            "embedding": [0.5, 0.6],
            "metadata": {"wattage": 15},
        }
        obj = SceneObject.from_dict(data)
        self.assertEqual(obj.id, "lamp_001")
        self.assertEqual(obj.name, "lamp")
        self.assertEqual(len(obj.attributes), 2)
        self.assertEqual(obj.description, "A modern LED lamp")
        self.assertEqual(obj.embedding, [0.5, 0.6])
        self.assertEqual(obj.metadata["wattage"], 15)

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        obj = SceneObject(
            name="desk",
            id="desk_001",
            attributes=["office", "ergonomic"],
            description="An ergonomic office desk",
        )
        data = obj.to_dict()
        restored = SceneObject.from_dict(data)
        self.assertEqual(restored.id, obj.id)
        self.assertEqual(restored.name, obj.name)
        self.assertEqual(restored.attributes, obj.attributes)
        self.assertEqual(restored.description, obj.description)

    def test_equality(self):
        """Test equality based on ID."""
        obj1 = SceneObject(name="chair", id="chair_001")
        obj2 = SceneObject(name="table", id="chair_001")  # Same ID, different name
        obj3 = SceneObject(name="chair", id="chair_002")
        self.assertEqual(obj1, obj2)  # Same ID
        self.assertNotEqual(obj1, obj3)  # Different ID

    def test_equality_with_non_scene_object(self):
        """Test equality with non-SceneObject returns False."""
        obj = SceneObject(name="chair")
        self.assertNotEqual(obj, "chair")
        self.assertNotEqual(obj, 123)

    def test_hash(self):
        """Test hashing based on ID."""
        obj1 = SceneObject(name="chair", id="chair_001")
        obj2 = SceneObject(name="table", id="chair_001")
        self.assertEqual(hash(obj1), hash(obj2))

    def test_hash_allows_use_in_set(self):
        """Test that objects can be used in sets."""
        obj1 = SceneObject(name="chair", id="chair_001")
        obj2 = SceneObject(name="table", id="chair_001")
        obj3 = SceneObject(name="desk", id="desk_001")
        obj_set = {obj1, obj2, obj3}
        self.assertEqual(len(obj_set), 2)  # obj1 and obj2 have same ID

    def test_repr(self):
        """Test string representation."""
        obj = SceneObject(name="chair", id="chair_001", attributes=["wooden"])
        repr_str = repr(obj)
        self.assertIn("chair_001", repr_str)
        self.assertIn("chair", repr_str)
        self.assertIn("1 attrs", repr_str)

    def test_repr_without_attributes(self):
        """Test string representation without attributes."""
        obj = SceneObject(name="table", id="table_001")
        repr_str = repr(obj)
        self.assertIn("table_001", repr_str)
        self.assertIn("table", repr_str)
        self.assertNotIn("attrs", repr_str)

    def test_adapter_registration_unregistered_format(self):
        """Test from_format with unregistered format raises error."""
        with self.assertRaises(ValueError) as cm:
            SceneObject.from_format("unknown_format", {})
        self.assertIn("No adapter registered", str(cm.exception))

    def test_to_format_unregistered_format(self):
        """Test to_format with unregistered format raises error."""
        obj = SceneObject(name="chair")
        with self.assertRaises(ValueError) as cm:
            obj.to_format("unknown_format")
        self.assertIn("No adapter registered", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
