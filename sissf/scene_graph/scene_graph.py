"""
scene_graph.py
---
Scene graph representation for semantic scene understanding.
Adapted from libsg (https://github.com/smartscenes/libsg) and Visual Genome formats.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..utils import Dictionable, dict_to_uuid
from .relationship import Relationship
from .scene_object import SceneObject

# Registry for adapters
_SCENE_GRAPH_ADAPTERS: Dict[str, Type["SceneGraphAdapter"]] = {}


class SceneGraphAdapter(Protocol):
    """Protocol for SceneGraph format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "SceneGraph":
        """Convert from format to SceneGraph."""
        ...

    @staticmethod
    def to_format(instance: "SceneGraph", **kwargs) -> Dict[str, Any]:
        """Convert SceneGraph to format."""
        ...


class SceneGraphValidationError(Exception):
    """Exception raised when scene graph validation fails."""

    pass


@dataclass
class SceneGraph(Dictionable):
    """
    Scene graph representation for semantic and spatial scene understanding.

    A scene graph consists of objects (nodes) and relationships (edges) that
    define the semantic and spatial structure of a scene. This is commonly used
    as an intermediate representation in text-to-3D scene generation pipelines.

    The scene graph can optionally include:
    - Room type information
    - Object attributes and embeddings
    - Relationship confidence scores
    - Additional metadata

    This format is designed to be flexible and support conversion to/from
    various scene graph formats used in different methods (e.g., libsg,
    holodeck, instructscene, visual genome).
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Scene graph ID
    room_type: Optional[str] = None  # Room type (e.g., "bedroom", "kitchen")
    objects: Dict[str, SceneObject] = field(default_factory=dict)  # Object lookup
    relationships: List[Relationship] = field(default_factory=list)  # Relationships
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def add_object(self, obj: SceneObject) -> SceneObject:
        """Add an object to the scene graph."""
        if obj.id in self.objects:
            # TODO: Handle duplicate IDs more gracefully
            raise ValueError(f"Object with id {obj.id} already exists")

        self.objects[obj.id] = obj
        return obj

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        """Get object by ID."""
        return self.objects.get(obj_id)

    def remove_object(self, obj_id: str) -> Optional[SceneObject]:
        """
        Remove object and all relationships involving it.

        Returns the removed object, or None if not found.
        """
        obj = self.objects.pop(obj_id, None)
        if obj is not None:
            # Remove all relationships involving this object
            self.relationships = [
                rel
                for rel in self.relationships
                if rel.subject_id != obj_id and rel.target_id != obj_id
            ]
        return obj

    def add_relationship(self, relationship: Relationship) -> Relationship:
        """Add a relationship to the scene graph."""
        # Validate that subject and target objects exist
        if relationship.subject_id not in self.objects:
            raise ValueError(f"Subject object {relationship.subject_id} does not exist")
        if (
            relationship.target_id is not None
            and relationship.target_id not in self.objects
        ):
            raise ValueError(f"Target object {relationship.target_id} does not exist")

        self.relationships.append(relationship)
        return relationship

    def get_relationships_for_object(
        self, obj_id: str, as_subject: bool = True, as_target: bool = True
    ) -> List[Relationship]:
        """
        Get all relationships involving a specific object.

        Args:
            obj_id: Object ID to search for
            as_subject: Include relationships where object is subject
            as_target: Include relationships where object is target

        Returns:
            List of relationships involving the object
        """
        result = []
        for rel in self.relationships:
            if as_subject and rel.subject_id == obj_id:
                result.append(rel)
            elif as_target and rel.target_id == obj_id:
                result.append(rel)
        return result

    def get_related_objects(
        self, obj_id: str, relationship_type: Optional[str] = None
    ) -> List[SceneObject]:
        """
        Get all objects related to a specific object.

        Args:
            obj_id: Object ID to find relations for
            relationship_type: Optional filter by relationship type

        Returns:
            List of related objects
        """
        related_ids = set()

        for rel in self.relationships:
            if relationship_type and rel.type != relationship_type:
                continue

            if rel.subject_id == obj_id:
                related_ids.add(rel.target_id)
            elif rel.target_id == obj_id:
                related_ids.add(rel.subject_id)

        return [self.objects[oid] for oid in related_ids if oid in self.objects]

    def validate(
        self,
        allowed_objects: Optional[List[str]] = None,
        allowed_relationships: Optional[List[str]] = None,
    ) -> bool:
        """
        Validate the scene graph structure and constraints.

        Args:
            allowed_objects: Optional whitelist of allowed object names
            allowed_relationships: Optional whitelist of allowed relationship types

        Returns:
            True if valid

        Raises:
            SceneGraphValidationError: If validation fails
        """
        # Check objects
        for obj_id, obj in self.objects.items():
            if not obj.name:
                raise SceneGraphValidationError(f"Object {obj_id} has empty name")
            if allowed_objects is not None and obj.name not in allowed_objects:
                raise SceneGraphValidationError(
                    f"Invalid object name: {obj.name}. Allowed: {allowed_objects}"
                )

        # Check relationships
        for rel in self.relationships:
            if not rel.type:
                raise SceneGraphValidationError(f"Relationship {rel.id} has empty type")
            if (
                allowed_relationships is not None
                and rel.type not in allowed_relationships
            ):
                raise SceneGraphValidationError(
                    f"Invalid relationship type: {rel.type}. Allowed: {allowed_relationships}"
                )
            # Check for orphaned relationships (subject must exist)
            if rel.subject_id not in self.objects:
                raise SceneGraphValidationError(
                    f"Orphaned relationship {rel.id}: subject {rel.subject_id} not found in scene graph"
                )
            # Check target if it's specified (target_id is optional)
            if rel.target_id is not None and rel.target_id not in self.objects:
                raise SceneGraphValidationError(
                    f"Orphaned relationship {rel.id}: target {rel.target_id} not found in scene graph"
                )

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "id": self.id,
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "relationships": [rel.to_dict() for rel in self.relationships],
        }

        if self.room_type is not None:
            result["room_type"] = self.room_type

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneGraph":
        """Create SceneGraph from dictionary."""
        sg = cls(
            id=data.get("id", str(dict_to_uuid(data))),
            room_type=data.get("room_type"),
            metadata=data.get("metadata", {}),
        )

        # Load objects
        for obj_data in data.get("objects", []):
            obj = SceneObject.from_dict(obj_data)
            sg.add_object(obj)

        # Load relationships
        for rel_data in data.get("relationships", []):
            rel = Relationship.from_dict(rel_data)
            sg.add_relationship(rel)

        return sg

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[SceneGraphAdapter]
    ) -> None:
        """Register a format adapter for SceneGraph."""
        _SCENE_GRAPH_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, data: Dict[str, Any], **kwargs
    ) -> "SceneGraph":
        """Convert from specified format to SceneGraph."""
        if format_name not in _SCENE_GRAPH_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_GRAPH_ADAPTERS[format_name].from_format(data, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert SceneGraph to specified format."""
        if format_name not in _SCENE_GRAPH_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _SCENE_GRAPH_ADAPTERS[format_name].to_format(self, **kwargs)

    @property
    def num_objects(self) -> int:
        """Get number of objects in scene graph."""
        return len(self.objects)

    @property
    def num_relationships(self) -> int:
        """Get number of relationships in scene graph."""
        return len(self.relationships)

    def __repr__(self) -> str:
        room_str = f", room={self.room_type}" if self.room_type else ""
        return f"SceneGraph(id={self.id}{room_str}, {self.num_objects} objects, {self.num_relationships} relationships)"
