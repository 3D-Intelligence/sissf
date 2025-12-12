from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, Type

from ..geometry import BBox3D, Transform
from ..utils import dict_to_uuid

# Registry for adapters
_MODEL_INSTANCE_ADAPTERS: Dict[str, Type["ModelInstanceAdapter"]] = {}


class ModelInstanceAdapter(Protocol):
    """Protocol for ModelInstance format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "ModelInstance":
        """Convert from format to ModelInstance."""
        ...

    @staticmethod
    def to_format(instance: "ModelInstance", **kwargs) -> Dict[str, Any]:
        """Convert ModelInstance to format."""
        ...


@dataclass
class ModelInstance:
    """A class representing a 3D model instance in a scene."""

    id: str
    model_id: str
    transform: Transform = field(default_factory=Transform)
    bounding_box: Optional[BBox3D] = None
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: str = "ModelInstance"
    asset_file_location: Optional[str] = None

    @property
    def asset_source(self) -> str:
        """Extract asset source from model_id (format: source.id)."""
        return self.model_id.partition(".")[0]

    @property
    def object_id(self) -> str:
        """Extract object_id from model_id (format: source.id)."""
        return self.model_id.partition(".")[-1]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "model_id": self.model_id,
            "transform": self.transform.to_dict(),
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "asset_file_location": self.asset_file_location,
        }

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> "ModelInstance":
        """Create ModelInstance from dictionary."""
        mi = ModelInstance(
            id=obj.get("id", str(dict_to_uuid(obj))),
            model_id=obj.get("model_id", ""),
            parent_id=obj.get("parent_id"),
            transform=Transform.from_dict(obj["transform"]),
            bounding_box=(
                BBox3D.from_dict(bbox) if (bbox := obj.get("bounding_box")) else None
            ),
            metadata=obj.get("metadata", {}),
            asset_file_location=obj.get("asset_file_location"),
        )

        return mi

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[ModelInstanceAdapter]
    ) -> None:
        """Register a format adapter for ModelInstance."""
        _MODEL_INSTANCE_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, obj: Dict[str, Any], **kwargs
    ) -> "ModelInstance":
        """Convert from specified format to ModelInstance."""
        if format_name not in _MODEL_INSTANCE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _MODEL_INSTANCE_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert ModelInstance to specified format."""
        if format_name not in _MODEL_INSTANCE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _MODEL_INSTANCE_ADAPTERS[format_name].to_format(self)
