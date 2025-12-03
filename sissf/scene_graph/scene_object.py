"""
scene_object.py
---
Scene object representation for scene graphs.
Represents entities (furniture, fixtures, etc.) with attributes and optional embeddings.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..utils import Dictionable, dict_to_uuid

# Registry for adapters
_SCENE_OBJECT_ADAPTERS: Dict[str, Type["SceneObjectAdapter"]] = {}


class SceneObjectAdapter(Protocol):
    """Protocol for SceneObject format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "SceneObject":
        """Convert from format to SceneObject."""
        ...

    @staticmethod
    def to_format(instance: "SceneObject", **kwargs) -> Dict[str, Any]:
        """Convert SceneObject to format."""
        ...


@dataclass
class SceneObject(Dictionable):
    """
    Represents an object in a scene graph.

    A scene object can represent furniture, fixtures, architectural elements,
    or any other entity in a 3D scene. Objects can have semantic attributes
    and optional feature embeddings for ML pipelines.

    Example:
        >>> chair = SceneObject(
        ...     name="chair",
        ...     attributes=["wooden", "dining"],
        ...     description="A wooden dining chair"
        ... )
        >>> chair.add_attribute("antique")
        >>> chair.has_attribute("wooden")
        True
    """

    name: str  # Object category/class name (e.g., "chair", "table")
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Object ID
    attributes: List[str] = field(default_factory=list)  # Semantic attributes
    description: Optional[str] = None  # Optional natural language description
    embedding: Optional[List[float]] = None  # Optional feature embedding
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __post_init__(self):
        if not self.name:
            raise ValueError("name cannot be empty")

    def add_attribute(self, attribute: str) -> None:
        """Add an attribute to the object."""
        if attribute not in self.attributes:
            self.attributes.append(attribute)

    def remove_attribute(self, attribute: str) -> None:
        """Remove an attribute from the object."""
        if attribute in self.attributes:
            self.attributes.remove(attribute)

    def has_attribute(self, attribute: str) -> bool:
        """Check if object has a specific attribute."""
        return attribute in self.attributes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes,
        }

        if self.description is not None:
            result["description"] = self.description

        if self.embedding is not None:
            result["embedding"] = self.embedding

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        """Create SceneObject from dictionary."""
        return cls(
            id=data.get("id", str(dict_to_uuid(data))),
            name=data.get("name", ""),
            attributes=data.get("attributes", []),
            description=data.get("description"),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[SceneObjectAdapter]
    ) -> None:
        """Register a format adapter for SceneObject."""
        _SCENE_OBJECT_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, data: Dict[str, Any], **kwargs
    ) -> "SceneObject":
        """Convert from specified format to SceneObject."""
        if format_name not in _SCENE_OBJECT_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_OBJECT_ADAPTERS[format_name].from_format(data, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert SceneObject to specified format."""
        if format_name not in _SCENE_OBJECT_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_OBJECT_ADAPTERS[format_name].to_format(self, **kwargs)

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, SceneObject):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        attrs_str = f", {len(self.attributes)} attrs" if self.attributes else ""
        return f"SceneObject(id={self.id}, name={self.name}{attrs_str})"
