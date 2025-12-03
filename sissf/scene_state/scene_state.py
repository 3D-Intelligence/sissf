"""
scene_state.py
---
Scene state representation for object layout and placement.
Adapted from libsg (https://github.com/smartscenes/libsg) and smartscenes scene state format.
(https://github.com/smartscenes/sstk/wiki/Scene-State-Format).
"""

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..architecture.architecture import Architecture
from ..geometry import Point3D
from ..scene_graph.scene_graph import SceneGraph
from ..utils import Dictionable, dict_to_uuid
from .model_instance import ModelInstance

# Registry for adapters
_SCENE_STATE_ADAPTERS: Dict[str, Type["SceneStateAdapter"]] = {}


class SceneStateAdapter(Protocol):
    """Protocol for SceneState format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "SceneState":
        """Convert from format to SceneState."""
        ...

    @staticmethod
    def to_format(instance: "SceneState", **kwargs) -> Dict[str, Any]:
        """Convert SceneState to format."""
        ...


@dataclass
class SceneStateCamera(Dictionable):
    """Scene state camera representation."""

    up: Point3D = field(default_factory=lambda: Point3D(0, 1, 0))
    position: Point3D = field(default_factory=lambda: Point3D(0, 0, 0))
    target: Point3D = field(default_factory=lambda: Point3D(0, 0, 0))
    is_ortho: bool = False
    name: str = "current"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create SceneStateCamera from dictionary."""
        return cls(
            up=Point3D(**data.get("up", dict(x=0, y=1, z=0))),
            position=Point3D(**data.get("position", dict(x=0, y=0, z=0))),
            target=Point3D(**data.get("target", dict(x=0, y=0, z=0))),
            is_ortho=data.get("is_ortho", False),
            name=data.get("name", "current"),
        )


@dataclass
class SceneState:
    """Scene state representation containing objects and their placement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Scene ID
    version: str = "scene@0.0.1"
    up: Point3D = field(default_factory=lambda: Point3D(0, 1, 0))  # Y-up
    front: Point3D = field(default_factory=lambda: Point3D(0, 0, -1))  # Z-forward
    unit: float = 1.0  # (meters) Same as Architecture.scale_to_meters
    asset_source: List[str] = field(default_factory=list)
    cameras: List[SceneStateCamera] = field(
        default_factory=lambda: [SceneStateCamera()]
    )
    selected: List[str] = field(default_factory=list)
    architecture: Optional[Architecture] = None
    scene_graph: Dict[str, SceneGraph] = field(default_factory=dict)
    model_instances: Dict[str, ModelInstance] = field(default_factory=dict)
    max_id: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_instance(
        self, mi: ModelInstance, clone: bool = False, parent_id: Optional[str] = None
    ) -> ModelInstance:
        """Add a model instance to the scene."""
        if not mi.id:
            mi.id = self._get_next_id()

        if mi.id == parent_id:
            raise ValueError("Model instance cannot be parent of itself")

        if parent_id and parent_id not in self.model_instances:
            raise ValueError(f"Parent model instance with id {parent_id} not found")

        if clone:
            instance = copy.deepcopy(mi)
            instance.id = self._get_next_id()
            instance.parent_id = parent_id
        else:
            instance = mi

        if instance.id in self.model_instances:
            # raise ValueError(f"Model instance with id {instance.id} already exists")
            # TODO: Handle duplicate IDs
            return instance

        self.model_instances[instance.id] = instance

        # Update max ID if numeric
        if instance.id.isdigit():
            self.max_id = max(int(instance.id), self.max_id)

        return instance

    def get_instance(self, instance_id: str) -> Optional[ModelInstance]:
        """Get model instance by ID."""
        return self.model_instances.get(instance_id, None)

    def remove_instance(self, instance_id: str) -> Optional[ModelInstance]:
        """Remove model instance by ID."""
        return self.model_instances.pop(instance_id, None)

    def _get_next_id(self) -> str:
        """Generate next numeric ID."""
        self.max_id += 1

        return str(self.max_id)

    @property
    def objects(self) -> List[ModelInstance]:
        """Return model instances"""
        return list(self.model_instances.values())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "format": "sceneState",
            "scene": {
                "id": self.id,
                "version": self.version,
                "up": self.up.to_dict(),
                "front": self.front.to_dict(),
                "unit": self.unit,
                "asset_source": self.asset_source,
                "objects": [mi.to_dict() for mi in self.model_instances.values()],
                "cameras": [c.to_dict() for c in self.cameras],
                "selected": self.selected,
                "metadata": self.metadata,
            },
            "arch": (
                self.architecture.to_dict() if self.architecture is not None else {}
            ),
            "scene_graph": {
                sg_id: sg.to_dict() for sg_id, sg in self.scene_graph.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneState":
        """Create SceneState from dictionary."""
        arch_dict: Optional[Dict[str, Any]] = data.get("arch")
        architecture: Optional[Architecture] = (
            Architecture.from_dict(arch_dict) if (arch_dict) else None
        )

        scene_graphs_by_id: Dict[str, Dict[str, Any]] = data.get("scene_graph", {})
        scene_graph: Dict[str, SceneGraph] = (
            {
                scene_graph_id: SceneGraph.from_dict(scene_graph_dict)
                for scene_graph_id, scene_graph_dict in scene_graphs_by_id.items()
            }
            if (scene_graphs_by_id)
            else {}
        )

        scene_dict: Dict[str, Any] = data["scene"]
        scene = SceneState(
            id=scene_dict.get("id", str(dict_to_uuid(scene_dict))),
            version=scene_dict.get("version", "0.0.1"),
            architecture=architecture,
            scene_graph=scene_graph,
            metadata=scene_dict.get("metadata", {}),
        )
        if (up := scene_dict.get("up")) is not None:
            scene.up = Point3D(**up)
        if (front := scene_dict.get("front")) is not None:
            scene.front = Point3D(**front)
        if (
            scale_to_meters := scene_dict.get("scale_to_meters", scene_dict.get("unit"))
        ) is not None:
            scene.unit = scale_to_meters
        if (asset_source := scene_dict.get("asset_source")) is not None:
            scene.asset_source = asset_source
        if (cameras := scene_dict.get("cameras")) is not None:
            scene.cameras = [SceneStateCamera.from_dict(c_dict) for c_dict in cameras]
        if (selected := scene_dict.get("selected")) is not None:
            scene.selected = selected

        for obj_data in scene_dict.get("objects", []):
            mi = ModelInstance.from_dict(obj_data)
            scene.add_instance(mi)

        return scene

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[SceneStateAdapter]
    ) -> None:
        """Register a format adapter for SceneState."""
        _SCENE_STATE_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, data: Dict[str, Any], **kwargs
    ) -> "SceneState":
        """Convert from specified format to SceneState."""
        if format_name not in _SCENE_STATE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_STATE_ADAPTERS[format_name].from_format(data, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert SceneState to specified format."""
        if format_name not in _SCENE_STATE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_STATE_ADAPTERS[format_name].to_format(self)
