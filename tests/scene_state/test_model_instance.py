import unittest

from sissf.geometry import Transform
from sissf.scene_state.model_instance import ModelInstance, ModelInstanceAdapter


class TestModelInstance(unittest.TestCase):
    def test_initialization(self):
        """Test ModelInstance initialization."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        self.assertEqual(instance.id, "test_id")
        self.assertEqual(instance.model_id, "source.model")
        self.assertIsInstance(instance.transform, Transform)
        self.assertIsNone(instance.parent_id)
        self.assertEqual(instance.metadata, {})
        self.assertEqual(instance.type, "ModelInstance")
        self.assertIsNone(instance.asset_file_location)

    def test_properties(self):
        """Test ModelInstance properties."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        self.assertEqual(instance.asset_source, "source")
        self.assertEqual(instance.object_id, "model")

    def test_to_dict(self):
        """Test ModelInstance to_dict conversion."""
        instance = ModelInstance(
            id="test_id",
            model_id="source.model",
            transform=Transform.from_rts(
                rotation=[0, 0, 0, 1], translation=[1, 2, 3], scale=[1, 1, 1]
            ),
            parent_id="parent",
            metadata={"key": "value"},
            asset_file_location="/path/to/asset",
        )
        data = instance.to_dict()
        self.assertEqual(data["id"], "test_id")
        self.assertEqual(data["model_id"], "source.model")
        self.assertEqual(data["transform"]["translation"], [1, 2, 3])
        self.assertEqual(data["parent_id"], "parent")
        self.assertEqual(data["metadata"], {"key": "value"})
        self.assertEqual(data["asset_file_location"], "/path/to/asset")

    def test_from_dict(self):
        """Test ModelInstance from_dict conversion."""
        data = {
            "id": "test_id",
            "model_id": "source.model",
            "transform": {
                "rotation": [0, 0, 0, 1],
                "translation": [1, 2, 3],
                "scale": [1, 1, 1],
            },
            "parent_id": "parent",
            "metadata": {"key": "value"},
            "asset_file_location": "/path/to/asset",
        }
        instance = ModelInstance.from_dict(data)
        self.assertEqual(instance.id, "test_id")
        self.assertEqual(instance.model_id, "source.model")
        self.assertEqual(instance.transform.translation, [1, 2, 3])
        self.assertEqual(instance.parent_id, "parent")
        self.assertEqual(instance.metadata, {"key": "value"})
        self.assertEqual(instance.asset_file_location, "/path/to/asset")

    def test_adapter(self):
        """Test ModelInstance adapter functionality."""

        class TestAdapter(ModelInstanceAdapter):
            @staticmethod
            def from_format(obj, **kwargs):
                return ModelInstance(id=obj["test_id"], model_id=obj["test_model_id"])

            @staticmethod
            def to_format(instance, **kwargs):
                return {"test_id": instance.id, "test_model_id": instance.model_id}

        ModelInstance.register_adapter("test_format", TestAdapter)

        # Test from_format
        data = {"test_id": "adapter_id", "test_model_id": "adapter.model"}
        instance = ModelInstance.from_format("test_format", data)
        self.assertEqual(instance.id, "adapter_id")
        self.assertEqual(instance.model_id, "adapter.model")

        # Test to_format
        instance = ModelInstance(id="test_id", model_id="source.model")
        formatted_data = instance.to_format("test_format")
        self.assertEqual(formatted_data["test_id"], "test_id")
        self.assertEqual(formatted_data["test_model_id"], "source.model")

        # Test unregistered adapter
        with self.assertRaises(ValueError):
            ModelInstance.from_format("unregistered", {})
        with self.assertRaises(ValueError):
            instance.to_format("unregistered")

    def test_from_dict_missing_transform(self):
        """Test from_dict with missing transform key raises KeyError."""
        data = {"id": "test_id", "model_id": "source.model"}
        with self.assertRaises(KeyError) as cm:
            ModelInstance.from_dict(data)
        self.assertIn("transform", str(cm.exception))

    def test_from_dict_minimal(self):
        """Test from_dict with only required fields."""
        data = {
            "id": "test_id",
            "model_id": "source.model",
            "transform": {
                "rotation": [0, 0, 0, 1],
                "translation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
        }
        instance = ModelInstance.from_dict(data)
        self.assertEqual(instance.id, "test_id")
        self.assertEqual(instance.model_id, "source.model")
        self.assertIsNone(instance.parent_id)
        self.assertEqual(instance.metadata, {})
        self.assertIsNone(instance.asset_file_location)

    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves all fields."""
        original = ModelInstance(
            id="test_id",
            model_id="source.model",
            transform=Transform.from_rts(
                rotation=[0, 0, 0, 1], translation=[1, 2, 3], scale=[2, 2, 2]
            ),
            parent_id="parent_id",
            metadata={"key1": "value1", "key2": 42},
            asset_file_location="/path/to/asset.obj",
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = ModelInstance.from_dict(data)

        # Verify all fields preserved
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.model_id, original.model_id)
        self.assertEqual(restored.transform.translation, original.transform.translation)
        self.assertEqual(restored.transform.rotation, original.transform.rotation)
        self.assertEqual(restored.transform.scale, original.transform.scale)
        self.assertEqual(restored.parent_id, original.parent_id)
        self.assertEqual(restored.metadata, original.metadata)
        self.assertEqual(restored.asset_file_location, original.asset_file_location)

    def test_model_id_parsing_no_dot(self):
        """Test model_id parsing when there's no dot separator."""
        instance = ModelInstance(id="test_id", model_id="modelname")
        # With no dot, split returns the whole string as first element
        self.assertEqual(instance.asset_source, "modelname")
        self.assertEqual(instance.object_id, "")

    def test_model_id_parsing_multiple_dots(self):
        """Test model_id parsing with multiple dots."""
        instance = ModelInstance(id="test_id", model_id="source.category.model")
        # Split with maxsplit=1 should give us "source" and "category.model"
        self.assertEqual(instance.asset_source, "source")
        self.assertEqual(instance.object_id, "category.model")

    def test_model_id_parsing_empty(self):
        """Test model_id parsing with empty string."""
        instance = ModelInstance(id="test_id", model_id="")
        self.assertEqual(instance.asset_source, "")
        self.assertEqual(instance.object_id, "")

    def test_equality(self):
        """Test that instances use dataclass equality (all fields must match)."""
        instance1 = ModelInstance(id="test_id", model_id="source.model1")
        instance2 = ModelInstance(id="test_id", model_id="source.model1")
        instance3 = ModelInstance(id="test_id", model_id="source.model2")
        instance4 = ModelInstance(id="other_id", model_id="source.model1")

        # All fields must match for equality (dataclass default)
        self.assertEqual(instance1, instance2)

        # Different model_id means not equal (even with same ID)
        self.assertNotEqual(instance1, instance3)

        # Different ID means not equal
        self.assertNotEqual(instance1, instance4)

    def test_not_hashable(self):
        """Test that ModelInstance is not hashable (has mutable fields)."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        with self.assertRaises(TypeError):
            hash(instance)

    def test_transform_default(self):
        """Test that default transform is identity."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        self.assertEqual(instance.transform.translation, [0, 0, 0])
        self.assertEqual(instance.transform.rotation, [0, 0, 0, 1])
        self.assertEqual(instance.transform.scale, [1, 1, 1])

    def test_metadata_mutability(self):
        """Test that metadata can be modified after initialization."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        instance.metadata["new_key"] = "new_value"
        self.assertEqual(instance.metadata["new_key"], "new_value")

    def test_parent_id_update(self):
        """Test that parent_id can be updated after initialization."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        self.assertIsNone(instance.parent_id)

        instance.parent_id = "parent_id"
        self.assertEqual(instance.parent_id, "parent_id")

    def test_type_field(self):
        """Test that type field is always 'ModelInstance'."""
        instance = ModelInstance(id="test_id", model_id="source.model")
        self.assertEqual(instance.type, "ModelInstance")


if __name__ == "__main__":
    unittest.main()
