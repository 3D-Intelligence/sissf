import unittest
import uuid

from sissf.architecture.architecture import Architecture
from sissf.geometry import Point3D, Transform
from sissf.scene_graph import SceneGraph
from sissf.scene_state.model_instance import ModelInstance
from sissf.scene_state.scene_state import (
    SceneState,
    SceneStateAdapter,
    SceneStateCamera,
)


class TestSceneState(unittest.TestCase):
    def test_camera_initialization(self):
        """Test SceneStateCamera initialization."""
        camera = SceneStateCamera()
        self.assertEqual(camera.up, Point3D(0, 1, 0))
        self.assertEqual(camera.position, Point3D(0, 0, 0))
        self.assertEqual(camera.target, Point3D(0, 0, 0))
        self.assertFalse(camera.is_ortho)
        self.assertEqual(camera.name, "current")

    def test_camera_from_dict(self):
        """Test SceneStateCamera from_dict conversion."""
        data = {
            "up": {"x": 0, "y": 0, "z": 1},
            "position": {"x": 1, "y": 2, "z": 3},
            "target": {"x": 4, "y": 5, "z": 6},
            "is_ortho": True,
            "name": "test_cam",
        }
        camera = SceneStateCamera.from_dict(data)
        self.assertEqual(camera.up, Point3D(0, 0, 1))
        self.assertEqual(camera.position, Point3D(1, 2, 3))
        self.assertEqual(camera.target, Point3D(4, 5, 6))
        self.assertTrue(camera.is_ortho)
        self.assertEqual(camera.name, "test_cam")

    def test_initialization(self):
        """Test SceneState initialization."""
        scene = SceneState()
        self.assertIsInstance(scene.id, str)
        self.assertEqual(scene.version, "scene@0.0.1")
        self.assertEqual(scene.up, Point3D(0, 1, 0))
        self.assertEqual(scene.front, Point3D(0, 0, -1))
        self.assertEqual(scene.unit, 1.0)
        self.assertEqual(scene.asset_source, [])
        self.assertEqual(len(scene.cameras), 1)
        self.assertEqual(scene.selected, [])
        self.assertIsNone(scene.architecture)
        self.assertEqual(scene.scene_graph, {})
        self.assertEqual(scene.model_instances, {})
        self.assertEqual(scene.max_id, 0)
        self.assertEqual(scene.metadata, {})

    def test_instance_management(self):
        """Test instance management in SceneState."""
        scene = SceneState()
        instance1 = ModelInstance(id="1", model_id="source.model1")
        instance2 = ModelInstance(id="2", model_id="source.model2")

        # Add instances
        scene.add_instance(instance1)
        scene.add_instance(instance2)
        self.assertEqual(len(scene.model_instances), 2)
        self.assertEqual(scene.get_instance("1"), instance1)
        self.assertEqual(scene.get_instance("2"), instance2)

        # Test cloning
        cloned_instance = scene.add_instance(instance1, clone=True, parent_id="2")
        self.assertNotEqual(cloned_instance.id, instance1.id)
        self.assertEqual(cloned_instance.parent_id, "2")

        # Test adding instance with existing ID
        scene.add_instance(instance1)
        self.assertEqual(len(scene.model_instances), 3)

        # Remove instance
        scene.remove_instance("1")
        self.assertIsNone(scene.get_instance("1"))
        self.assertEqual(len(scene.model_instances), 2)

        # Test adding instance with self as parent
        with self.assertRaises(ValueError):
            scene.add_instance(instance1, parent_id="1")

        # Test adding instance with non-existent parent
        with self.assertRaises(ValueError):
            scene.add_instance(instance1, parent_id="100")

    def test_properties(self):
        """Test SceneState properties."""
        scene = SceneState()
        instance1 = ModelInstance(id="1", model_id="source.model1")
        instance2 = ModelInstance(id="2", model_id="source.model2")
        scene.add_instance(instance1)
        scene.add_instance(instance2)
        self.assertEqual(len(scene.objects), 2)

    def test_to_dict(self):
        """Test SceneState to_dict conversion."""
        scene = SceneState()
        instance = ModelInstance(id="1", model_id="source.model")
        scene.add_instance(instance)
        data = scene.to_dict()
        self.assertEqual(data["format"], "sceneState")
        self.assertEqual(data["scene"]["id"], scene.id)
        self.assertEqual(len(data["scene"]["objects"]), 1)
        self.assertEqual(data["scene"]["objects"][0]["id"], "1")

    def test_from_dict(self):
        """Test SceneState from_dict conversion."""
        scene_id = str(uuid.uuid4())
        data = {
            "scene": {
                "id": scene_id,
                "objects": [
                    {
                        "id": "1",
                        "model_id": "source.model",
                        "transform": {
                            "rotation": [0, 0, 0, 1],
                            "translation": [0, 0, 0],
                            "scale": [1, 1, 1],
                        },
                    }
                ],
            },
            "arch": {"id": "arch_id"},
        }
        scene = SceneState.from_dict(data)
        self.assertEqual(scene.id, scene_id)
        self.assertIsInstance(scene.architecture, Architecture)
        self.assertEqual(len(scene.model_instances), 1)
        self.assertIsNotNone(scene.get_instance("1"))

    def test_adapter(self):
        """Test SceneState adapter functionality."""

        class TestAdapter(SceneStateAdapter):
            @staticmethod
            def from_format(obj, **kwargs):
                return SceneState(id=obj["test_id"])

            @staticmethod
            def to_format(instance, **kwargs):
                return {"test_id": instance.id}

        SceneState.register_adapter("test_format", TestAdapter)

        # Test from_format
        data = {"test_id": "adapter_id"}
        scene = SceneState.from_format("test_format", data)
        self.assertEqual(scene.id, "adapter_id")

        # Test to_format
        scene = SceneState()
        formatted_data = scene.to_format("test_format")
        self.assertEqual(formatted_data["test_id"], scene.id)

        # Test unregistered adapter
        with self.assertRaises(ValueError):
            SceneState.from_format("unregistered", {})
        with self.assertRaises(ValueError):
            scene.to_format("unregistered")

    def test_add_instance_without_id(self):
        """Test adding instance without ID triggers auto-generation."""
        scene = SceneState()
        instance = ModelInstance(id="", model_id="source.model")
        added = scene.add_instance(instance)
        self.assertEqual(added.id, "1")
        self.assertEqual(scene.max_id, 1)

        # Add another without ID
        instance2 = ModelInstance(id="", model_id="source.model2")
        added2 = scene.add_instance(instance2)
        self.assertEqual(added2.id, "2")
        self.assertEqual(scene.max_id, 2)

    def test_duplicate_id_behavior(self):
        """Test that adding instance with duplicate ID returns the duplicate (bug)."""
        scene = SceneState()
        instance1 = ModelInstance(id="1", model_id="source.model1")
        instance2 = ModelInstance(id="1", model_id="source.model2")

        scene.add_instance(instance1)
        result = scene.add_instance(instance2)

        # Current behavior: returns the second instance but doesn't add it
        # This is documented as a TODO bug in scene_state.py:102-103
        self.assertEqual(result.model_id, "source.model2")
        self.assertEqual(len(scene.model_instances), 1)
        # The original instance is still in the scene
        stored_instance = scene.get_instance("1")
        self.assertIsNotNone(stored_instance)
        self.assertEqual(stored_instance.model_id, "source.model1")

    def test_max_id_tracking_numeric(self):
        """Test that max_id is tracked correctly for numeric IDs."""
        scene = SceneState()
        scene.add_instance(ModelInstance(id="5", model_id="source.model1"))
        self.assertEqual(scene.max_id, 5)

        scene.add_instance(ModelInstance(id="10", model_id="source.model2"))
        self.assertEqual(scene.max_id, 10)

        scene.add_instance(ModelInstance(id="3", model_id="source.model3"))
        self.assertEqual(scene.max_id, 10)  # Should not decrease

    def test_max_id_tracking_string(self):
        """Test that max_id is not affected by string IDs."""
        scene = SceneState()
        scene.add_instance(ModelInstance(id="abc", model_id="source.model1"))
        self.assertEqual(scene.max_id, 0)  # String ID doesn't affect max_id

        scene.add_instance(ModelInstance(id="xyz", model_id="source.model2"))
        self.assertEqual(scene.max_id, 0)

    def test_get_next_id(self):
        """Test ID generation."""
        scene = SceneState()
        self.assertEqual(scene._get_next_id(), "1")
        self.assertEqual(scene._get_next_id(), "2")
        self.assertEqual(scene._get_next_id(), "3")
        self.assertEqual(scene.max_id, 3)

    def test_remove_instance_nonexistent(self):
        """Test removing nonexistent instance returns None."""
        scene = SceneState()
        result = scene.remove_instance("nonexistent")
        self.assertIsNone(result)

    def test_get_instance_nonexistent(self):
        """Test getting nonexistent instance returns None."""
        scene = SceneState()
        result = scene.get_instance("nonexistent")
        self.assertIsNone(result)

    def test_from_dict_with_custom_fields(self):
        """Test from_dict with all optional fields."""
        scene_id = str(uuid.uuid4())
        data = {
            "scene": {
                "id": scene_id,
                "version": "1.2.3",
                "up": {"x": 0, "y": 0, "z": 1},  # Z-up
                "front": {"x": 1, "y": 0, "z": 0},  # X-forward
                "unit": 0.01,  # Centimeters
                "asset_source": ["models/", "textures/"],
                "cameras": [
                    {
                        "name": "cam1",
                        "position": {"x": 1, "y": 2, "z": 3},
                        "target": {"x": 0, "y": 0, "z": 0},
                        "up": {"x": 0, "y": 1, "z": 0},
                        "is_ortho": False,
                    },
                    {
                        "name": "cam2",
                        "position": {"x": 5, "y": 5, "z": 5},
                        "target": {"x": 0, "y": 0, "z": 0},
                        "up": {"x": 0, "y": 1, "z": 0},
                        "is_ortho": True,
                    },
                ],
                "selected": ["obj1", "obj2"],
                "objects": [],
                "metadata": {"key": "value"},
            }
        }
        scene = SceneState.from_dict(data)
        self.assertEqual(scene.id, scene_id)
        self.assertEqual(scene.version, "1.2.3")
        self.assertEqual(scene.up, Point3D(0, 0, 1))
        self.assertEqual(scene.front, Point3D(1, 0, 0))
        self.assertEqual(scene.unit, 0.01)
        self.assertEqual(scene.asset_source, ["models/", "textures/"])
        self.assertEqual(len(scene.cameras), 2)
        self.assertEqual(scene.cameras[0].name, "cam1")
        self.assertEqual(scene.cameras[1].name, "cam2")
        self.assertTrue(scene.cameras[1].is_ortho)
        self.assertEqual(scene.selected, ["obj1", "obj2"])
        self.assertEqual(scene.metadata, {"key": "value"})

    def test_from_dict_with_scene_graph(self):
        """Test from_dict with scene_graph data."""
        data = {
            "scene": {
                "id": "test_scene",
                "objects": [],
            },
            "scene_graph": {
                "sg1": {
                    "id": "sg1",
                    "objects": {},
                    "relationships": [],
                }
            },
        }
        scene = SceneState.from_dict(data)
        self.assertIn("sg1", scene.scene_graph)
        self.assertIsInstance(scene.scene_graph["sg1"], SceneGraph)

    def test_from_dict_with_scale_to_meters(self):
        """Test from_dict with legacy scale_to_meters field."""
        data = {
            "scene": {
                "id": "test_scene",
                "scale_to_meters": 0.5,
                "objects": [],
            }
        }
        scene = SceneState.from_dict(data)
        self.assertEqual(scene.unit, 0.5)

    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves all fields."""
        # Create a scene with all fields populated
        original = SceneState(
            id="test_scene",
            version="1.0.0",
            metadata={"key": "value"},
        )
        original.up = Point3D(0, 0, 1)
        original.front = Point3D(1, 0, 0)
        original.unit = 0.01
        original.asset_source = ["models/"]
        original.selected = ["obj1"]

        # Add an instance
        instance = ModelInstance(
            id="1",
            model_id="source.model",
            transform=Transform.from_rts(
                rotation=[0, 0, 0, 1], translation=[1, 2, 3], scale=[1, 1, 1]
            ),
        )
        original.add_instance(instance)

        # Convert to dict and back
        data = original.to_dict()
        restored = SceneState.from_dict(data)

        # Verify all fields preserved
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.version, original.version)
        self.assertEqual(restored.up, original.up)
        self.assertEqual(restored.front, original.front)
        self.assertEqual(restored.unit, original.unit)
        self.assertEqual(restored.asset_source, original.asset_source)
        self.assertEqual(restored.selected, original.selected)
        self.assertEqual(restored.metadata, original.metadata)
        self.assertEqual(len(restored.model_instances), 1)
        self.assertIsNotNone(restored.get_instance("1"))

    def test_empty_objects_list(self):
        """Test scene with no objects."""
        scene = SceneState()
        self.assertEqual(len(scene.objects), 0)
        self.assertEqual(len(scene.model_instances), 0)

        data = scene.to_dict()
        self.assertEqual(len(data["scene"]["objects"]), 0)

    def test_clone_with_metadata(self):
        """Test that cloning preserves metadata and generates new ID."""
        scene = SceneState()
        instance = ModelInstance(
            id="1", model_id="source.model", metadata={"key": "value"}
        )
        # Add the original first
        scene.add_instance(instance)

        # Clone should get a new ID
        cloned = scene.add_instance(instance, clone=True)

        self.assertNotEqual(cloned.id, instance.id)
        self.assertEqual(cloned.id, "2")  # Should be auto-generated
        self.assertEqual(cloned.metadata, instance.metadata)
        self.assertIsNot(cloned.metadata, instance.metadata)  # Should be deep copy

    def test_camera_list_operations(self):
        """Test camera list can be modified."""
        scene = SceneState()
        self.assertEqual(len(scene.cameras), 1)

        # Add a camera
        new_camera = SceneStateCamera(
            name="cam2",
            position=Point3D(5, 5, 5),
            target=Point3D(0, 0, 0),
        )
        scene.cameras.append(new_camera)
        self.assertEqual(len(scene.cameras), 2)

        # Remove a camera
        scene.cameras.pop()
        self.assertEqual(len(scene.cameras), 1)

    def test_selected_list_operations(self):
        """Test selected list can be modified."""
        scene = SceneState()
        self.assertEqual(len(scene.selected), 0)

        scene.selected.append("obj1")
        scene.selected.append("obj2")
        self.assertEqual(len(scene.selected), 2)

        scene.selected.remove("obj1")
        self.assertEqual(len(scene.selected), 1)
        self.assertEqual(scene.selected[0], "obj2")


class TestSceneStateCamera(unittest.TestCase):
    """Additional comprehensive tests for SceneStateCamera."""

    def test_camera_to_dict(self):
        """Test SceneStateCamera to_dict conversion."""
        camera = SceneStateCamera(
            name="test_cam",
            position=Point3D(1, 2, 3),
            target=Point3D(4, 5, 6),
            up=Point3D(0, 1, 0),
            is_ortho=True,
        )
        data = camera.to_dict()
        self.assertEqual(data["name"], "test_cam")
        self.assertEqual(data["position"], {"x": 1, "y": 2, "z": 3})
        self.assertEqual(data["target"], {"x": 4, "y": 5, "z": 6})
        self.assertEqual(data["up"], {"x": 0, "y": 1, "z": 0})
        self.assertTrue(data["is_ortho"])

    def test_camera_roundtrip(self):
        """Test SceneStateCamera to_dict -> from_dict roundtrip."""
        original = SceneStateCamera(
            name="cam",
            position=Point3D(10, 20, 30),
            target=Point3D(0, 0, 0),
            up=Point3D(0, 0, 1),
            is_ortho=True,
        )
        data = original.to_dict()
        restored = SceneStateCamera.from_dict(data)

        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.position, original.position)
        self.assertEqual(restored.target, original.target)
        self.assertEqual(restored.up, original.up)
        self.assertEqual(restored.is_ortho, original.is_ortho)

    def test_camera_from_dict_with_defaults(self):
        """Test SceneStateCamera from_dict with missing optional fields."""
        data = {}
        camera = SceneStateCamera.from_dict(data)
        self.assertEqual(camera.name, "current")
        self.assertEqual(camera.position, Point3D(0, 0, 0))
        self.assertEqual(camera.target, Point3D(0, 0, 0))
        self.assertEqual(camera.up, Point3D(0, 1, 0))
        self.assertFalse(camera.is_ortho)

    def test_camera_from_dict_partial(self):
        """Test SceneStateCamera from_dict with some fields."""
        data = {
            "name": "partial_cam",
            "position": {"x": 5, "y": 5, "z": 5},
        }
        camera = SceneStateCamera.from_dict(data)
        self.assertEqual(camera.name, "partial_cam")
        self.assertEqual(camera.position, Point3D(5, 5, 5))
        self.assertEqual(camera.target, Point3D(0, 0, 0))  # Default
        self.assertEqual(camera.up, Point3D(0, 1, 0))  # Default
        self.assertFalse(camera.is_ortho)  # Default

    def test_camera_equality(self):
        """Test SceneStateCamera equality."""
        cam1 = SceneStateCamera(name="cam", position=Point3D(1, 2, 3))
        cam2 = SceneStateCamera(name="cam", position=Point3D(1, 2, 3))
        cam3 = SceneStateCamera(name="cam2", position=Point3D(1, 2, 3))

        # Dataclasses with same values should be equal
        self.assertEqual(cam1, cam2)
        self.assertNotEqual(cam1, cam3)


if __name__ == "__main__":
    unittest.main()
