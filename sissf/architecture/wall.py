"""
wall.py
---
Wall representation with geometry and openings (doors, windows).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..geometry import Point3D
from .opening import ArchOpening

# Registry for adapters
_ARCH_WALL_ADAPTERS: Dict[str, Type["ArchWallAdapter"]] = {}


class ArchWallAdapter(Protocol):
    """Protocol for ArchWall format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "ArchWall":
        """Convert from format to ArchWall."""
        ...

    @staticmethod
    def to_format(instance: "ArchWall", **kwargs) -> Dict[str, Any]:
        """Convert ArchWall to format."""
        ...


@dataclass
class ArchWall:
    """Wall definition with geometry and openings."""

    id: str
    points: List[Point3D]  # Start and end points (2 points)
    height: float
    depth: float  # thickness
    room_id: str
    material: Optional[str] = None
    type: str = "Wall"
    openings: List[ArchOpening] = field(default_factory=list)
    material_file_location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.points) != 2:
            raise ValueError(
                f"ArchWall requires exactly 2 points, got {len(self.points)}"
            )
        if self.height <= 0:
            raise ValueError(f"ArchWall height must be positive, got {self.height}")
        if self.depth <= 0:
            raise ValueError(f"ArchWall depth must be positive, got {self.depth}")

    @property
    def width(self) -> float:
        """Calculate wall width from points.

        Returns:
            Euclidean distance between the two wall points
        """
        return self.points[0].distance_to(self.points[1])

    @property
    def area(self) -> float:
        """Calculate wall surface area (excluding openings).

        Returns:
            Total wall area minus opening areas
        """
        wall_area = self.width * self.height
        opening_area = sum(o.width * o.height for o in self.openings)

        return wall_area - opening_area

    def add_opening(self, opening: ArchOpening) -> None:
        """Add an opening (door/window) to this wall."""
        self.openings.append(opening)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "points": [p.to_dict() for p in self.points],
            "height": self.height,
            "depth": self.depth,
            "room_id": self.room_id,
            "material": self.material,
            "openings": [opening.to_dict() for opening in self.openings],
            "material_file_location": self.material_file_location,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchWall":
        """Create ArchWall from dictionary."""
        wall = ArchWall(
            id=data["id"],
            points=[Point3D(**p) for p in data["points"]],
            height=data["height"],
            depth=data["depth"],
            room_id=data["room_id"],
            material=data.get("material"),
            material_file_location=data.get("material_file_location"),
            metadata=data.get("metadata", {}),
        )

        for opening_data in data.get("openings", []):
            opening = ArchOpening.from_dict(opening_data)
            wall.add_opening(opening)

        return wall

    @classmethod
    def register_adapter(cls, format_name: str, adapter: Type[ArchWallAdapter]) -> None:
        """Register a format adapter for ArchWall."""
        _ARCH_WALL_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(cls, format_name: str, obj: Dict[str, Any], **kwargs) -> "ArchWall":
        """Convert from specified format to ArchWall."""
        if format_name not in _ARCH_WALL_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_WALL_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert ArchWall to specified format."""
        if format_name not in _ARCH_WALL_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_WALL_ADAPTERS[format_name].to_format(self)
