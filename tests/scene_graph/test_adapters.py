"""Unit tests for scene graph format adapters."""

import unittest

from sissf.scene_graph import Relationship, SceneGraph, SceneObject
from sissf.scene_graph.adapters import VisualGenomeAdapter


class TestVisualGenomeAdapter(unittest.TestCase):
    """Test Visual Genome format adapter."""

    def test_from_format_minimal(self):
        """Test conversion from Visual Genome format with minimal data."""
        vg_data = {"objects": [], "relationships": []}
        sg = VisualGenomeAdapter.from_format(vg_data)
        self.assertIsInstance(sg, SceneGraph)
        self.assertEqual(len(sg.objects), 0)
        self.assertEqual(len(sg.relationships), 0)
        self.assertEqual(sg.metadata.get("source_format"), "visual_genome")

    def test_from_format_with_objects(self):
        """Test conversion from Visual Genome format with objects."""
        vg_data = {
            "objects": [
                {"id": 1, "name": "chair", "attributes": ["wooden"]},
                {"object_id": 2, "names": ["table"], "attributes": ["glass"]},
            ],
            "relationships": [],
        }
        sg = VisualGenomeAdapter.from_format(vg_data)
        self.assertEqual(len(sg.objects), 2)

        # Check first object (using 'id' and 'name' fields)
        obj1 = sg.get_object("1")
        self.assertIsNotNone(obj1)
        self.assertEqual(obj1.name, "chair")
        self.assertIn("wooden", obj1.attributes)

        # Check second object (using 'object_id' and 'names' fields)
        obj2 = sg.get_object("2")
        self.assertIsNotNone(obj2)
        self.assertEqual(obj2.name, "table")
        self.assertIn("glass", obj2.attributes)

    def test_from_format_with_relationships(self):
        """Test conversion from Visual Genome format with relationships."""
        vg_data = {
            "objects": [
                {"object_id": 1, "names": ["chair"]},
                {"object_id": 2, "names": ["table"]},
            ],
            "relationships": [
                {
                    "relationship_id": 0,
                    "predicate": "on",
                    "subject": {"object_id": 1},
                    "object": {"object_id": 2},
                }
            ],
        }
        sg = VisualGenomeAdapter.from_format(vg_data)
        self.assertEqual(len(sg.relationships), 1)
        rel = sg.relationships[0]
        self.assertEqual(rel.type, "on")
        self.assertEqual(rel.subject_id, "1")
        self.assertEqual(rel.target_id, "2")

    def test_from_format_alternative_field_names(self):
        """Test conversion handles alternative VG field names."""
        vg_data = {
            "objects": [
                {"object_id": 1, "names": ["lamp"]},
                {"object_id": 2, "names": ["desk"]},
            ],
            "relationships": [
                {
                    "relationship_id": 0,
                    "type": "on top of",
                    "subject_id": 1,
                    "target_id": 2,
                }
            ],
        }
        sg = VisualGenomeAdapter.from_format(vg_data)
        self.assertEqual(len(sg.relationships), 1)
        rel = sg.relationships[0]
        self.assertEqual(rel.type, "on top of")

    def test_from_format_skips_invalid_relationships(self):
        """Test conversion skips relationships with missing objects."""
        vg_data = {
            "objects": [{"object_id": 1, "names": ["chair"]}],
            "relationships": [
                {
                    "relationship_id": 0,
                    "predicate": "on",
                    "subject": {"object_id": 1},
                    "object": {"object_id": 999},  # Non-existent object
                }
            ],
        }
        sg = VisualGenomeAdapter.from_format(vg_data)
        # Relationship should be skipped since object 999 doesn't exist
        self.assertEqual(len(sg.relationships), 0)

    def test_to_format_minimal(self):
        """Test conversion to Visual Genome format with minimal data."""
        sg = SceneGraph()
        vg_data = VisualGenomeAdapter.to_format(sg)
        self.assertIn("objects", vg_data)
        self.assertIn("relationships", vg_data)
        self.assertEqual(len(vg_data["objects"]), 0)
        self.assertEqual(len(vg_data["relationships"]), 0)

    def test_to_format_with_objects(self):
        """Test conversion to Visual Genome format with objects."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1", attributes=["wooden", "dining"])
        obj2 = SceneObject(name="table", id="obj2", attributes=["glass"])
        sg.add_object(obj1)
        sg.add_object(obj2)

        vg_data = VisualGenomeAdapter.to_format(sg)
        self.assertEqual(len(vg_data["objects"]), 2)

        # Objects should have integer IDs
        obj_ids = {obj["object_id"] for obj in vg_data["objects"]}
        self.assertEqual(obj_ids, {0, 1})

        # Check object structure
        for vg_obj in vg_data["objects"]:
            self.assertIn("object_id", vg_obj)
            self.assertIn("names", vg_obj)
            self.assertIn("attributes", vg_obj)
            self.assertIsInstance(vg_obj["names"], list)
            self.assertEqual(len(vg_obj["names"]), 1)

    def test_to_format_with_relationships(self):
        """Test conversion to Visual Genome format with relationships."""
        sg = SceneGraph()
        obj1 = SceneObject(name="cup", id="obj1")
        obj2 = SceneObject(name="saucer", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)

        vg_data = VisualGenomeAdapter.to_format(sg)
        self.assertEqual(len(vg_data["relationships"]), 1)

        vg_rel = vg_data["relationships"][0]
        self.assertIn("relationship_id", vg_rel)
        self.assertIn("predicate", vg_rel)
        self.assertIn("subject", vg_rel)
        self.assertIn("object", vg_rel)
        self.assertEqual(vg_rel["predicate"], "on")
        self.assertIsInstance(vg_rel["subject"]["object_id"], int)
        self.assertIsInstance(vg_rel["object"]["object_id"], int)

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion to/from Visual Genome format."""
        # Create original scene graph
        sg_original = SceneGraph()
        obj1 = SceneObject(name="laptop", id="obj1", attributes=["silver", "15inch"])
        obj2 = SceneObject(name="desk", id="obj2", attributes=["wooden"])
        sg_original.add_object(obj1)
        sg_original.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg_original.add_relationship(rel)

        # Convert to VG format
        vg_data = VisualGenomeAdapter.to_format(sg_original)

        # Convert back to SceneGraph
        sg_restored = VisualGenomeAdapter.from_format(vg_data)

        # Verify structure is preserved
        self.assertEqual(len(sg_restored.objects), len(sg_original.objects))
        self.assertEqual(len(sg_restored.relationships), len(sg_original.relationships))

        # Check objects by name (IDs will be different after roundtrip since VG uses integers)
        original_names = {obj.name for obj in sg_original.objects.values()}
        restored_names = {obj.name for obj in sg_restored.objects.values()}
        self.assertEqual(original_names, restored_names)

        # Check attributes are preserved
        for original_obj in sg_original.objects.values():
            # Find matching object by name in restored
            restored_obj = next(
                (obj for obj in sg_restored.objects.values() if obj.name == original_obj.name),
                None
            )
            self.assertIsNotNone(restored_obj)
            self.assertEqual(restored_obj.attributes, original_obj.attributes)

    def test_adapter_is_registered(self):
        """Test that VisualGenomeAdapter is registered with SceneGraph."""
        # Should be able to use from_format and to_format on SceneGraph
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)

        # Test to_format
        vg_data = sg.to_format("visual_genome")
        self.assertIsInstance(vg_data, dict)
        self.assertIn("objects", vg_data)

        # Test from_format
        vg_input = {
            "objects": [{"object_id": 1, "names": ["table"]}],
            "relationships": [],
        }
        sg_from_vg = SceneGraph.from_format("visual_genome", vg_input)
        self.assertIsInstance(sg_from_vg, SceneGraph)
        self.assertEqual(len(sg_from_vg.objects), 1)


class TestAdapterRegistration(unittest.TestCase):
    """Test adapter registration mechanism."""

    def test_scene_object_adapter_registration(self):
        """Test SceneObject adapter registration."""

        # Create a mock adapter
        class MockAdapter:
            @staticmethod
            def from_format(obj, **kwargs):
                return SceneObject(name="mock", id="mock_001")

            @staticmethod
            def to_format(instance, **kwargs):
                return {"mock": True}

        # Register adapter
        SceneObject.register_adapter("mock_format", MockAdapter)

        # Test from_format
        obj = SceneObject.from_format("mock_format", {})
        self.assertEqual(obj.name, "mock")

        # Test to_format
        test_obj = SceneObject(name="test")
        result = test_obj.to_format("mock_format")
        self.assertEqual(result["mock"], True)

    def test_relationship_adapter_registration(self):
        """Test Relationship adapter registration."""

        # Create a mock adapter
        class MockAdapter:
            @staticmethod
            def from_format(obj, **kwargs):
                return Relationship(type="mock", subject_id="obj1", id="rel_mock")

            @staticmethod
            def to_format(instance, **kwargs):
                return {"mock": True}

        # Register adapter
        Relationship.register_adapter("mock_format", MockAdapter)

        # Test from_format
        rel = Relationship.from_format("mock_format", {})
        self.assertEqual(rel.type, "mock")

        # Test to_format
        test_rel = Relationship(type="test", subject_id="obj1")
        result = test_rel.to_format("mock_format")
        self.assertEqual(result["mock"], True)

    def test_scene_graph_adapter_registration(self):
        """Test SceneGraph adapter registration."""

        # Create a mock adapter
        class MockAdapter:
            @staticmethod
            def from_format(obj, **kwargs):
                return SceneGraph(id="mock_scene")

            @staticmethod
            def to_format(instance, **kwargs):
                return {"mock": True}

        # Register adapter
        SceneGraph.register_adapter("mock_format", MockAdapter)

        # Test from_format
        sg = SceneGraph.from_format("mock_format", {})
        self.assertEqual(sg.id, "mock_scene")

        # Test to_format
        test_sg = SceneGraph()
        result = test_sg.to_format("mock_format")
        self.assertEqual(result["mock"], True)


if __name__ == "__main__":
    unittest.main()
