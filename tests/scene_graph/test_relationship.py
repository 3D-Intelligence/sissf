"""Unit tests for Relationship class."""

import unittest

from sissf.scene_graph import Relationship


class TestRelationship(unittest.TestCase):
    """Test Relationship class."""

    def test_init_minimal(self):
        """Test Relationship initialization with minimal data."""
        rel = Relationship(type="on", subject_id="obj1")
        self.assertEqual(rel.type, "on")
        self.assertEqual(rel.subject_id, "obj1")
        self.assertIsNotNone(rel.id)
        self.assertIsNone(rel.target_id)
        self.assertIsNone(rel.confidence)
        self.assertIsNone(rel.embedding)
        self.assertEqual(len(rel.metadata), 0)

    def test_init_with_id(self):
        """Test Relationship initialization with custom ID."""
        rel = Relationship(type="left of", subject_id="obj1", id="rel_001")
        self.assertEqual(rel.id, "rel_001")
        self.assertEqual(rel.type, "left of")

    def test_init_with_target(self):
        """Test Relationship initialization with target."""
        rel = Relationship(type="on", subject_id="obj1", target_id="obj2")
        self.assertEqual(rel.subject_id, "obj1")
        self.assertEqual(rel.target_id, "obj2")

    def test_init_with_confidence(self):
        """Test Relationship initialization with confidence."""
        rel = Relationship(type="supports", subject_id="obj1", confidence=0.95)
        self.assertEqual(rel.confidence, 0.95)

    def test_init_with_embedding(self):
        """Test Relationship initialization with embedding."""
        embedding = [0.1, 0.2, 0.3]
        rel = Relationship(type="near", subject_id="obj1", embedding=embedding)
        self.assertEqual(rel.embedding, embedding)

    def test_init_with_metadata(self):
        """Test Relationship initialization with metadata."""
        metadata = {"distance": 1.5, "unit": "meters"}
        rel = Relationship(type="near", subject_id="obj1", metadata=metadata)
        self.assertEqual(rel.metadata, metadata)

    def test_post_init_validates_empty_type(self):
        """Test that __post_init__ validates empty type."""
        with self.assertRaises(ValueError) as cm:
            Relationship(type="", subject_id="obj1")
        self.assertIn("Relationship type cannot be empty", str(cm.exception))

    def test_post_init_validates_confidence_lower_bound(self):
        """Test that __post_init__ validates confidence lower bound."""
        with self.assertRaises(ValueError) as cm:
            Relationship(type="on", subject_id="obj1", confidence=-0.1)
        self.assertIn("Confidence must be between 0 and 1", str(cm.exception))

    def test_post_init_validates_confidence_upper_bound(self):
        """Test that __post_init__ validates confidence upper bound."""
        with self.assertRaises(ValueError) as cm:
            Relationship(type="on", subject_id="obj1", confidence=1.5)
        self.assertIn("Confidence must be between 0 and 1", str(cm.exception))

    def test_confidence_boundary_values(self):
        """Test confidence boundary values are accepted."""
        rel1 = Relationship(type="on", subject_id="obj1", confidence=0.0)
        self.assertEqual(rel1.confidence, 0.0)
        rel2 = Relationship(type="on", subject_id="obj1", confidence=1.0)
        self.assertEqual(rel2.confidence, 1.0)

    def test_to_dict_minimal(self):
        """Test to_dict serialization with minimal data."""
        rel = Relationship(type="on", subject_id="obj1", id="rel_001")
        result = rel.to_dict()
        self.assertEqual(result["id"], "rel_001")
        self.assertEqual(result["type"], "on")
        self.assertEqual(result["subject_id"], "obj1")
        self.assertIsNone(result["target_id"])
        self.assertNotIn("confidence", result)
        self.assertNotIn("embedding", result)
        self.assertNotIn("metadata", result)

    def test_to_dict_with_target(self):
        """Test to_dict serialization with target."""
        rel = Relationship(
            type="left of", subject_id="obj1", target_id="obj2", id="rel_001"
        )
        result = rel.to_dict()
        self.assertEqual(result["subject_id"], "obj1")
        self.assertEqual(result["target_id"], "obj2")

    def test_to_dict_complete(self):
        """Test to_dict serialization with complete data."""
        rel = Relationship(
            type="near",
            subject_id="obj1",
            target_id="obj2",
            id="rel_001",
            confidence=0.85,
            embedding=[0.1, 0.2],
            metadata={"distance": 1.5},
        )
        result = rel.to_dict()
        self.assertEqual(result["id"], "rel_001")
        self.assertEqual(result["type"], "near")
        self.assertEqual(result["confidence"], 0.85)
        self.assertEqual(result["embedding"], [0.1, 0.2])
        self.assertEqual(result["metadata"]["distance"], 1.5)

    def test_from_dict_minimal(self):
        """Test from_dict deserialization with minimal data."""
        data = {"type": "on", "subject_id": "obj1"}
        rel = Relationship.from_dict(data)
        self.assertEqual(rel.type, "on")
        self.assertEqual(rel.subject_id, "obj1")
        self.assertIsNotNone(rel.id)

    def test_from_dict_with_id(self):
        """Test from_dict deserialization with ID."""
        data = {"id": "rel_001", "type": "left of", "subject_id": "obj1"}
        rel = Relationship.from_dict(data)
        self.assertEqual(rel.id, "rel_001")
        self.assertEqual(rel.type, "left of")

    def test_from_dict_complete(self):
        """Test from_dict deserialization with complete data."""
        data = {
            "id": "rel_001",
            "type": "supports",
            "subject_id": "obj1",
            "target_id": "obj2",
            "confidence": 0.92,
            "embedding": [0.3, 0.4],
            "metadata": {"strength": "high"},
        }
        rel = Relationship.from_dict(data)
        self.assertEqual(rel.id, "rel_001")
        self.assertEqual(rel.type, "supports")
        self.assertEqual(rel.subject_id, "obj1")
        self.assertEqual(rel.target_id, "obj2")
        self.assertEqual(rel.confidence, 0.92)
        self.assertEqual(rel.embedding, [0.3, 0.4])
        self.assertEqual(rel.metadata["strength"], "high")

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        rel = Relationship(
            type="above",
            subject_id="obj1",
            target_id="obj2",
            id="rel_001",
            confidence=0.88,
        )
        data = rel.to_dict()
        restored = Relationship.from_dict(data)
        self.assertEqual(restored.id, rel.id)
        self.assertEqual(restored.type, rel.type)
        self.assertEqual(restored.subject_id, rel.subject_id)
        self.assertEqual(restored.target_id, rel.target_id)
        self.assertEqual(restored.confidence, rel.confidence)

    def test_equality(self):
        """Test equality based on ID."""
        rel1 = Relationship(type="on", subject_id="obj1", id="rel_001")
        rel2 = Relationship(
            type="under", subject_id="obj2", id="rel_001"
        )  # Same ID, different type
        rel3 = Relationship(type="on", subject_id="obj1", id="rel_002")
        self.assertEqual(rel1, rel2)  # Same ID
        self.assertNotEqual(rel1, rel3)  # Different ID

    def test_equality_with_non_relationship(self):
        """Test equality with non-Relationship returns False."""
        rel = Relationship(type="on", subject_id="obj1")
        self.assertNotEqual(rel, "on")
        self.assertNotEqual(rel, 123)

    def test_hash(self):
        """Test hashing based on ID."""
        rel1 = Relationship(type="on", subject_id="obj1", id="rel_001")
        rel2 = Relationship(type="under", subject_id="obj2", id="rel_001")
        self.assertEqual(hash(rel1), hash(rel2))

    def test_hash_allows_use_in_set(self):
        """Test that relationships can be used in sets."""
        rel1 = Relationship(type="on", subject_id="obj1", id="rel_001")
        rel2 = Relationship(type="under", subject_id="obj2", id="rel_001")
        rel3 = Relationship(type="near", subject_id="obj3", id="rel_002")
        rel_set = {rel1, rel2, rel3}
        self.assertEqual(len(rel_set), 2)  # rel1 and rel2 have same ID

    def test_repr(self):
        """Test string representation."""
        rel = Relationship(
            type="left of", subject_id="obj1", target_id="obj2", id="rel_001"
        )
        repr_str = repr(rel)
        self.assertIn("rel_001", repr_str)
        self.assertIn("left of", repr_str)
        self.assertIn("obj1", repr_str)
        self.assertIn("obj2", repr_str)

    def test_repr_without_target(self):
        """Test string representation without target."""
        rel = Relationship(type="on floor", subject_id="obj1", id="rel_001")
        repr_str = repr(rel)
        self.assertIn("rel_001", repr_str)
        self.assertIn("on floor", repr_str)
        self.assertIn("obj1", repr_str)

    def test_adapter_registration_unregistered_format(self):
        """Test from_format with unregistered format raises error."""
        with self.assertRaises(ValueError) as cm:
            Relationship.from_format("unknown_format", {})
        self.assertIn("No adapter registered", str(cm.exception))

    def test_to_format_unregistered_format(self):
        """Test to_format with unregistered format raises error."""
        rel = Relationship(type="on", subject_id="obj1")
        with self.assertRaises(ValueError) as cm:
            rel.to_format("unknown_format")
        self.assertIn("No adapter registered", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
