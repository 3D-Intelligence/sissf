"""
opening.py
---
Opening representation for doors and windows in walls.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol, Type

# Registry for adapters
_ARCH_OPENING_ADAPTERS: Dict[str, Type["ArchOpeningAdapter"]] = {}


class ArchOpeningAdapter(Protocol):
    """Protocol for ArchOpening format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "ArchOpening":
        """Convert from format to ArchOpening."""
        ...

    @staticmethod
    def to_format(instance: "ArchOpening", **kwargs) -> Dict[str, Any]:
        """Convert ArchOpening to format."""
        ...


@dataclass
class ArchOpening:
    """Base class for openings (doors, windows) in walls."""

    id: str
    type: str  # "Door" or "Window"
    parent_wall_id: str
    mid: float  # fractional position along wall (0-1)
    width: float
    height: float
    elevation: float  # height of midpoint from floor
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0 <= self.mid <= 1:
            raise ValueError(f"Opening mid must be between 0 and 1, got {self.mid}")
        if self.type not in ("Door", "Window"):
            raise ValueError(
                f"Opening type must be 'Door' or 'Window', got {self.type}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "parent_wall_id": self.parent_wall_id,
            "mid": self.mid,
            "width": self.width,
            "height": self.height,
            "elevation": self.elevation,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchOpening":
        """Create ArchOpening from dictionary."""
        return ArchOpening(
            id=data["id"],
            type=data["type"],
            parent_wall_id=data["parent_wall_id"],
            mid=data["mid"],
            width=data["width"],
            height=data["height"],
            elevation=data["elevation"],
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[ArchOpeningAdapter]
    ) -> None:
        """Register a format adapter for ArchOpening."""
        _ARCH_OPENING_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, obj: Dict[str, Any], **kwargs
    ) -> "ArchOpening":
        """Convert from specified format to ArchOpening."""
        if format_name not in _ARCH_OPENING_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_OPENING_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert ArchOpening to specified format."""
        if format_name not in _ARCH_OPENING_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_OPENING_ADAPTERS[format_name].to_format(self)
