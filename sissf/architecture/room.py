"""
room.py
---
Room representation containing references to architectural elements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from .ceiling import ArchCeiling
from .floor import ArchFloor

# Registry for adapters
_ARCH_ROOM_ADAPTERS: Dict[str, Type["ArchRoomAdapter"]] = {}


class ArchRoomAdapter(Protocol):
    """Protocol for ArchRoom format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "ArchRoom":
        """Convert from format to ArchRoom."""
        ...

    @staticmethod
    def to_format(instance: "ArchRoom", **kwargs) -> Dict[str, Any]:
        """Convert ArchRoom to format."""
        ...


@dataclass
class ArchRoom:
    """Room definition containing references to walls, floor, and ceiling."""

    id: str
    type: str = "Room"
    wall_ids: List[str] = field(default_factory=list)
    floor: Optional["ArchFloor"] = None
    ceiling: Optional["ArchCeiling"] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "wall_ids": self.wall_ids,
            "floor": self.floor.to_dict() if self.floor is not None else None,
            "ceiling": self.ceiling.to_dict() if self.ceiling is not None else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchRoom":
        """Create ArchRoom from dictionary."""
        room = ArchRoom(
            id=data["id"],
            wall_ids=data.get("wall_ids", []),
            floor=(
                ArchFloor.from_dict(data.get("floor", {}))
                if data.get("floor")
                else None
            ),
            ceiling=(
                ArchCeiling.from_dict(data.get("ceiling", {}))
                if data.get("ceiling")
                else None
            ),
            metadata=data.get("metadata", {}),
        )

        return room

    @classmethod
    def register_adapter(cls, format_name: str, adapter: Type[ArchRoomAdapter]) -> None:
        """Register a format adapter for ArchRoom."""
        _ARCH_ROOM_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(cls, format_name: str, obj: Dict[str, Any], **kwargs) -> "ArchRoom":
        """Convert from specified format to ArchRoom."""
        if format_name not in _ARCH_ROOM_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_ROOM_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert ArchRoom to specified format."""
        if format_name not in _ARCH_ROOM_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCH_ROOM_ADAPTERS[format_name].to_format(self)
