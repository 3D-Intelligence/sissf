"""
floor.py
---
Floor representation with polygon geometry.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..geometry import Point3D

# Registry for adapters
_ARCH_FLOOR_ADAPTERS: Dict[str, Type["ArchFloorAdapter"]] = {}


class ArchFloorAdapter(Protocol):
    """Protocol for ArchFloor format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "ArchFloor":
        """Convert from format to ArchFloor."""
        ...

    @staticmethod
    def to_format(instance: "ArchFloor", **kwargs) -> Dict[str, Any]:
        """Convert ArchFloor to format."""
        ...


@dataclass
class ArchFloor:
    """Floor definition with polygon geometry."""

    id: str
    points: List[Point3D]  # Polygon vertices
    depth: float  # thickness
    room_id: str
    material: Optional[str] = None
    type: str = "Floor"
    material_file_location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def area(self) -> float:
        """Calculate floor/ceiling area using polygon vertices.

        Uses the Shoelace formula for 2D polygon area.
        Assumes points lie in a plane (typically XZ plane for floors).

        Returns:
            Area of the polygon in square units
        """
        if len(self.points) < 3:
            return 0.0

        # Shoelace formula: A = 0.5 * |sum(x_i * y_{i+1} - x_{i+1} * y_i)|
        # For floors, we use X and Z coordinates (assuming Y is up)
        area = 0.0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i].x * self.points[j].z
            area -= self.points[j].x * self.points[i].z

        return abs(area) / 2.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "points": [p.to_dict() for p in self.points],
            "depth": self.depth,
            "room_id": self.room_id,
            "material": self.material,
            "material_file_location": self.material_file_location,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchFloor":
        """Create ArchFloor from dictionary."""
        return ArchFloor(
            id=data["id"],
            points=[Point3D(**p) for p in data["points"]],
            depth=data["depth"],
            room_id=data["room_id"],
            material=data.get("material"),
            material_file_location=data.get("material_file_location"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[ArchFloorAdapter]
    ) -> None:
        """Register a format adapter for ArchFloor."""
        _ARCH_FLOOR_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, obj: Dict[str, Any], **kwargs
    ) -> "ArchFloor":
        """Convert from specified format to ArchFloor."""
        if format_name not in _ARCH_FLOOR_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_FLOOR_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert ArchFloor to specified format."""
        if format_name not in _ARCH_FLOOR_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_FLOOR_ADAPTERS[format_name].to_format(self)
