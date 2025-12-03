"""Unit tests for SceneGraph class."""

import unittest

from sissf.scene_graph import Relationship, SceneGraph, SceneGraphValidationError, SceneObject


class TestSceneGraph(unittest.TestCase):
    """Test SceneGraph class."""

    def test_init_default(self):
        """Test SceneGraph initialization with defaults."""
        sg = SceneGraph()
        self.assertIsNotNone(sg.id)
        self.assertIsNone(sg.room_type)
        self.assertEqual(len(sg.objects), 0)
        self.assertEqual(len(sg.relationships), 0)
        self.assertEqual(len(sg.metadata), 0)

    def test_init_with_id(self):
        """Test SceneGraph initialization with custom ID."""
        sg = SceneGraph(id="scene_001")
        self.assertEqual(sg.id, "scene_001")

    def test_init_with_room_type(self):
        """Test SceneGraph initialization with room type."""
        sg = SceneGraph(room_type="bedroom")
        self.assertEqual(sg.room_type, "bedroom")

    def test_init_with_metadata(self):
        """Test SceneGraph initialization with metadata."""
        metadata = {"source": "llm", "confidence": 0.9}
        sg = SceneGraph(metadata=metadata)
        self.assertEqual(sg.metadata, metadata)

    def test_add_object(self):
        """Test adding object to scene graph."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="chair_001")
        result = sg.add_object(obj)
        self.assertEqual(len(sg.objects), 1)
        self.assertIn("chair_001", sg.objects)
        self.assertEqual(result, obj)

    def test_add_object_duplicate_id(self):
        """Test adding object with duplicate ID raises error."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj_001")
        obj2 = SceneObject(name="table", id="obj_001")
        sg.add_object(obj1)
        with self.assertRaises(ValueError) as cm:
            sg.add_object(obj2)
        self.assertIn("already exists", str(cm.exception))

    def test_get_object(self):
        """Test getting object by ID."""
        sg = SceneGraph()
        obj = SceneObject(name="table", id="table_001")
        sg.add_object(obj)
        retrieved = sg.get_object("table_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "table_001")

    def test_get_object_nonexistent(self):
        """Test getting nonexistent object returns None."""
        sg = SceneGraph()
        retrieved = sg.get_object("nonexistent")
        self.assertIsNone(retrieved)

    def test_remove_object(self):
        """Test removing object from scene graph."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="chair_001")
        sg.add_object(obj)
        removed = sg.remove_object("chair_001")
        self.assertEqual(removed, obj)
        self.assertEqual(len(sg.objects), 0)

    def test_remove_object_nonexistent(self):
        """Test removing nonexistent object returns None."""
        sg = SceneGraph()
        removed = sg.remove_object("nonexistent")
        self.assertIsNone(removed)

    def test_remove_object_cascades_to_relationships(self):
        """Test removing object also removes related relationships."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)
        self.assertEqual(len(sg.relationships), 1)

        sg.remove_object("obj1")
        self.assertEqual(len(sg.relationships), 0)

    def test_add_relationship(self):
        """Test adding relationship to scene graph."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2", id="rel_001")
        result = sg.add_relationship(rel)
        self.assertEqual(len(sg.relationships), 1)
        self.assertEqual(result, rel)

    def test_add_relationship_invalid_subject(self):
        """Test adding relationship with invalid subject raises error."""
        sg = SceneGraph()
        obj = SceneObject(name="table", id="obj2")
        sg.add_object(obj)
        rel = Relationship(type="on", subject_id="obj_nonexistent", target_id="obj2")
        with self.assertRaises(ValueError) as cm:
            sg.add_relationship(rel)
        self.assertIn("Subject object", str(cm.exception))
        self.assertIn("does not exist", str(cm.exception))

    def test_add_relationship_invalid_target(self):
        """Test adding relationship with invalid target raises error."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj_nonexistent")
        with self.assertRaises(ValueError) as cm:
            sg.add_relationship(rel)
        self.assertIn("Target object", str(cm.exception))
        self.assertIn("does not exist", str(cm.exception))

    def test_add_relationship_with_none_target(self):
        """Test adding relationship with None target is allowed."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)
        rel = Relationship(type="on floor", subject_id="obj1", target_id=None)
        sg.add_relationship(rel)
        self.assertEqual(len(sg.relationships), 1)

    def test_get_relationships_for_object_as_subject(self):
        """Test getting relationships where object is subject."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)

        rels = sg.get_relationships_for_object("obj1", as_subject=True, as_target=False)
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0].subject_id, "obj1")

    def test_get_relationships_for_object_as_target(self):
        """Test getting relationships where object is target."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)

        rels = sg.get_relationships_for_object("obj2", as_subject=False, as_target=True)
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0].target_id, "obj2")

    def test_get_relationships_for_object_both(self):
        """Test getting all relationships involving object."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        obj3 = SceneObject(name="lamp", id="obj3")
        sg.add_object(obj1)
        sg.add_object(obj2)
        sg.add_object(obj3)
        rel1 = Relationship(type="on", subject_id="obj1", target_id="obj2")
        rel2 = Relationship(type="left of", subject_id="obj3", target_id="obj1")
        sg.add_relationship(rel1)
        sg.add_relationship(rel2)

        rels = sg.get_relationships_for_object("obj1")
        self.assertEqual(len(rels), 2)

    def test_get_related_objects(self):
        """Test getting related objects."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        obj3 = SceneObject(name="lamp", id="obj3")
        sg.add_object(obj1)
        sg.add_object(obj2)
        sg.add_object(obj3)
        rel1 = Relationship(type="on", subject_id="obj1", target_id="obj2")
        rel2 = Relationship(type="near", subject_id="obj3", target_id="obj1")
        sg.add_relationship(rel1)
        sg.add_relationship(rel2)

        related = sg.get_related_objects("obj1")
        self.assertEqual(len(related), 2)
        related_ids = {obj.id for obj in related}
        self.assertIn("obj2", related_ids)
        self.assertIn("obj3", related_ids)

    def test_get_related_objects_with_type_filter(self):
        """Test getting related objects filtered by relationship type."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        obj3 = SceneObject(name="lamp", id="obj3")
        sg.add_object(obj1)
        sg.add_object(obj2)
        sg.add_object(obj3)
        rel1 = Relationship(type="on", subject_id="obj1", target_id="obj2")
        rel2 = Relationship(type="near", subject_id="obj3", target_id="obj1")
        sg.add_relationship(rel1)
        sg.add_relationship(rel2)

        related = sg.get_related_objects("obj1", relationship_type="on")
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0].id, "obj2")

    def test_validate_success(self):
        """Test validation passes for valid scene graph."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)

        self.assertTrue(sg.validate())

    def test_validate_empty_object_name(self):
        """Test validation fails for empty object name."""
        sg = SceneGraph()
        # Bypass __post_init__ by creating object with valid name then modifying
        obj = SceneObject(name="chair", id="obj1")
        obj.name = ""  # Manually set to empty
        sg.objects["obj1"] = obj

        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate()
        self.assertIn("empty name", str(cm.exception))

    def test_validate_empty_relationship_type(self):
        """Test validation fails for empty relationship type."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        # Bypass __post_init__ by creating relationship with valid type then modifying
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        rel.type = ""  # Manually set to empty
        sg.relationships.append(rel)

        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate()
        self.assertIn("empty type", str(cm.exception))

    def test_validate_orphaned_relationship_subject(self):
        """Test validation fails for orphaned relationship subject."""
        sg = SceneGraph()
        obj = SceneObject(name="table", id="obj2")
        sg.add_object(obj)
        # Manually add relationship with invalid subject (bypass add_relationship validation)
        rel = Relationship(type="on", subject_id="obj_nonexistent", target_id="obj2")
        sg.relationships.append(rel)

        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate()
        self.assertIn("Orphaned relationship", str(cm.exception))
        self.assertIn("subject", str(cm.exception))

    def test_validate_orphaned_relationship_target(self):
        """Test validation fails for orphaned relationship target."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)
        # Manually add relationship with invalid target (bypass add_relationship validation)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj_nonexistent")
        sg.relationships.append(rel)

        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate()
        self.assertIn("Orphaned relationship", str(cm.exception))
        self.assertIn("target", str(cm.exception))

    def test_validate_with_none_target(self):
        """Test validation passes for relationship with None target."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)
        rel = Relationship(type="on floor", subject_id="obj1", target_id=None)
        sg.add_relationship(rel)

        self.assertTrue(sg.validate())

    def test_validate_with_allowed_objects(self):
        """Test validation with allowed objects whitelist."""
        sg = SceneGraph()
        obj = SceneObject(name="chair", id="obj1")
        sg.add_object(obj)

        # Valid object name
        self.assertTrue(sg.validate(allowed_objects=["chair", "table"]))

        # Invalid object name
        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate(allowed_objects=["table", "desk"])
        self.assertIn("Invalid object name", str(cm.exception))

    def test_validate_with_allowed_relationships(self):
        """Test validation with allowed relationships whitelist."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        sg.add_relationship(rel)

        # Valid relationship type
        self.assertTrue(sg.validate(allowed_relationships=["on", "left of"]))

        # Invalid relationship type
        with self.assertRaises(SceneGraphValidationError) as cm:
            sg.validate(allowed_relationships=["near", "above"])
        self.assertIn("Invalid relationship type", str(cm.exception))

    def test_num_objects_property(self):
        """Test num_objects property."""
        sg = SceneGraph()
        self.assertEqual(sg.num_objects, 0)
        sg.add_object(SceneObject(name="chair", id="obj1"))
        self.assertEqual(sg.num_objects, 1)
        sg.add_object(SceneObject(name="table", id="obj2"))
        self.assertEqual(sg.num_objects, 2)

    def test_num_relationships_property(self):
        """Test num_relationships property."""
        sg = SceneGraph()
        obj1 = SceneObject(name="chair", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        self.assertEqual(sg.num_relationships, 0)
        sg.add_relationship(Relationship(type="on", subject_id="obj1", target_id="obj2"))
        self.assertEqual(sg.num_relationships, 1)

    def test_to_dict_minimal(self):
        """Test to_dict serialization with minimal data."""
        sg = SceneGraph(id="scene_001")
        result = sg.to_dict()
        self.assertEqual(result["id"], "scene_001")
        self.assertEqual(len(result["objects"]), 0)
        self.assertEqual(len(result["relationships"]), 0)
        self.assertNotIn("room_type", result)
        self.assertNotIn("metadata", result)

    def test_to_dict_with_room_type(self):
        """Test to_dict serialization with room type."""
        sg = SceneGraph(id="scene_001", room_type="bedroom")
        result = sg.to_dict()
        self.assertEqual(result["room_type"], "bedroom")

    def test_to_dict_with_metadata(self):
        """Test to_dict serialization with metadata."""
        sg = SceneGraph(id="scene_001", metadata={"source": "llm"})
        result = sg.to_dict()
        self.assertEqual(result["metadata"]["source"], "llm")

    def test_to_dict_complete(self):
        """Test to_dict serialization with complete data."""
        sg = SceneGraph(id="scene_001", room_type="living room")
        obj1 = SceneObject(name="sofa", id="obj1")
        obj2 = SceneObject(name="table", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="in front of", subject_id="obj2", target_id="obj1")
        sg.add_relationship(rel)

        result = sg.to_dict()
        self.assertEqual(result["id"], "scene_001")
        self.assertEqual(result["room_type"], "living room")
        self.assertEqual(len(result["objects"]), 2)
        self.assertEqual(len(result["relationships"]), 1)

    def test_from_dict_minimal(self):
        """Test from_dict deserialization with minimal data."""
        data = {"id": "scene_001"}
        sg = SceneGraph.from_dict(data)
        self.assertEqual(sg.id, "scene_001")
        self.assertEqual(len(sg.objects), 0)
        self.assertEqual(len(sg.relationships), 0)

    def test_from_dict_with_room_type(self):
        """Test from_dict deserialization with room type."""
        data = {"id": "scene_001", "room_type": "kitchen"}
        sg = SceneGraph.from_dict(data)
        self.assertEqual(sg.room_type, "kitchen")

    def test_from_dict_with_objects(self):
        """Test from_dict deserialization with objects."""
        data = {
            "id": "scene_001",
            "objects": [
                {"id": "obj1", "name": "chair"},
                {"id": "obj2", "name": "table"},
            ],
            "relationships": [],
        }
        sg = SceneGraph.from_dict(data)
        self.assertEqual(len(sg.objects), 2)
        self.assertIn("obj1", sg.objects)
        self.assertIn("obj2", sg.objects)

    def test_from_dict_with_relationships(self):
        """Test from_dict deserialization with relationships."""
        data = {
            "id": "scene_001",
            "objects": [
                {"id": "obj1", "name": "chair"},
                {"id": "obj2", "name": "table"},
            ],
            "relationships": [
                {"id": "rel1", "type": "on", "subject_id": "obj1", "target_id": "obj2"}
            ],
        }
        sg = SceneGraph.from_dict(data)
        self.assertEqual(len(sg.relationships), 1)
        self.assertEqual(sg.relationships[0].type, "on")

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        sg = SceneGraph(id="scene_001", room_type="office")
        obj1 = SceneObject(name="desk", id="obj1")
        obj2 = SceneObject(name="chair", id="obj2")
        sg.add_object(obj1)
        sg.add_object(obj2)
        rel = Relationship(type="in front of", subject_id="obj2", target_id="obj1")
        sg.add_relationship(rel)

        data = sg.to_dict()
        restored = SceneGraph.from_dict(data)

        self.assertEqual(restored.id, sg.id)
        self.assertEqual(restored.room_type, sg.room_type)
        self.assertEqual(len(restored.objects), len(sg.objects))
        self.assertEqual(len(restored.relationships), len(sg.relationships))

    def test_repr(self):
        """Test string representation."""
        sg = SceneGraph(id="scene_001", room_type="bedroom")
        sg.add_object(SceneObject(name="bed", id="obj1"))
        sg.add_object(SceneObject(name="nightstand", id="obj2"))
        obj1 = sg.get_object("obj1")
        obj2 = sg.get_object("obj2")
        sg.add_relationship(Relationship(type="next to", subject_id=obj2.id, target_id=obj1.id))

        repr_str = repr(sg)
        self.assertIn("scene_001", repr_str)
        self.assertIn("bedroom", repr_str)
        self.assertIn("2 objects", repr_str)
        self.assertIn("1 relationships", repr_str)

    def test_repr_without_room_type(self):
        """Test string representation without room type."""
        sg = SceneGraph(id="scene_001")
        repr_str = repr(sg)
        self.assertIn("scene_001", repr_str)
        self.assertIn("0 objects", repr_str)

    def test_adapter_registration_unregistered_format(self):
        """Test from_format with unregistered format raises error."""
        with self.assertRaises(ValueError) as cm:
            SceneGraph.from_format("unknown_format", {})
        self.assertIn("No adapter registered", str(cm.exception))

    def test_to_format_unregistered_format(self):
        """Test to_format with unregistered format raises error."""
        sg = SceneGraph()
        with self.assertRaises(ValueError) as cm:
            sg.to_format("unknown_format")
        self.assertIn("No adapter registered", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
