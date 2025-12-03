"""
relationship.py
---
Relationship representation for scene graphs.
Represents spatial, functional, or semantic relationships between scene objects.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..utils import Dictionable, dict_to_uuid

# Registry for adapters
_RELATIONSHIP_ADAPTERS: Dict[str, Type["RelationshipAdapter"]] = {}


class RelationshipAdapter(Protocol):
    """Protocol for Relationship format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "Relationship":
        """Convert from format to Relationship."""
        ...

    @staticmethod
    def to_format(instance: "Relationship", **kwargs) -> Dict[str, Any]:
        """Convert Relationship to format."""
        ...


@dataclass
class Relationship(Dictionable):
    """
    Represents a relationship between two objects in a scene graph.

    Relationships can be spatial (e.g., "left of", "above"), functional
    (e.g., "supports", "inside"), or semantic (e.g., "matches", "part of").

    Note: To avoid circular dependencies during serialization, we store
    subject_id and target_id as strings rather than object references.
    The SceneGraph class maintains the mapping between IDs and objects.
    """

    type: str  # Relationship type (e.g., "left of", "on", "supports")
    subject_id: str  # ID of the subject object
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Relationship ID
    target_id: Optional[str] = None  # ID of the target object
    confidence: Optional[float] = None  # Optional confidence score
    embedding: Optional[List[float]] = None  # Optional feature embedding
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __post_init__(self):
        if not self.type:
            raise ValueError("Relationship type cannot be empty")
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0 and 1, got {self.confidence}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "id": self.id,
            "type": self.type,
            "subject_id": self.subject_id,
            "target_id": self.target_id,
        }

        if self.confidence is not None:
            result["confidence"] = self.confidence

        if self.embedding is not None:
            result["embedding"] = self.embedding

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create Relationship from dictionary."""
        return cls(
            id=data.get("id", str(dict_to_uuid(data))),
            type=data.get("type", ""),
            subject_id=data.get("subject_id", ""),
            target_id=data.get("target_id", ""),
            confidence=data.get("confidence"),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[RelationshipAdapter]
    ) -> None:
        """Register a format adapter for Relationship."""
        _RELATIONSHIP_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, data: Dict[str, Any], **kwargs
    ) -> "Relationship":
        """Convert from specified format to Relationship."""
        if format_name not in _RELATIONSHIP_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _RELATIONSHIP_ADAPTERS[format_name].from_format(data, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert Relationship to specified format."""
        if format_name not in _RELATIONSHIP_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _RELATIONSHIP_ADAPTERS[format_name].to_format(self, **kwargs)

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Relationship):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Relationship(id={self.id}, type={self.type}, {self.subject_id} -> {self.target_id})"
