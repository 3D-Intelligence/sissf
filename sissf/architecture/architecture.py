"""
architecture.py
---
Architecture representation for building geometry (walls, floors, ceilings, openings).
Adapted from libsg (https://github.com/smartscenes/libsg) and smartscenes architecture format
(https://github.com/smartscenes/sstk/wiki/Architecture-Format).
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type

from ..geometry import Point3D
from ..utils import dict_to_uuid
from .ceiling import ArchCeiling
from .defaults import (
    ArchitectureDefaults,
    CeilingDefault,
    FloorDefault,
    GroundDefault,
    WallDefault,
)
from .floor import ArchFloor
from .room import ArchRoom
from .wall import ArchOpening, ArchWall

# Registry for adapters
_ARCHITECTURE_ADAPTERS: Dict[str, Type["ArchitectureAdapter"]] = {}


class ArchitectureAdapter(Protocol):
    """Protocol for Architecture format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "Architecture":
        """Convert from format to Architecture."""
        ...

    @staticmethod
    def to_format(instance: "Architecture", **kwargs) -> Dict[str, Any]:
        """Convert Architecture to format."""
        ...


@dataclass
class Architecture:
    """
    Complete architecture definition containing rooms, walls, floors, ceilings.

    Represents the architectural structure of a building with hierarchical
    relationships between rooms and their components (walls, floors, ceilings).

    Examples:
        >>> # Create empty architecture
        >>> arch = Architecture()

        >>> # Add a room
        >>> room = ArchRoom(id="room_0")
        >>> arch.add_room(room)

        >>> # Add a wall to the room
        >>> wall = ArchWall(
        ...     id="wall_0",
        ...     points=[Point3D(0, 0, 0), Point3D(3, 0, 0)],
        ...     height=2.5,
        ...     depth=0.1,
        ...     room_id="room_0"
        ... )
        >>> arch.add_wall(wall)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Architecture ID
    version: str = "arch@0.0.1"
    up: Point3D = field(default_factory=lambda: Point3D(0, 1, 0))  # Y-up
    front: Point3D = field(default_factory=lambda: Point3D(0, 0, -1))  # Z-forward
    scale_to_meters: float = 1.0
    defaults: ArchitectureDefaults = field(default_factory=ArchitectureDefaults)

    rooms: Dict[str, ArchRoom] = field(default_factory=dict)
    walls: Dict[str, ArchWall] = field(default_factory=dict)
    floors: Dict[str, ArchFloor] = field(
        default_factory=dict
    )  # TODO: make this a property instead that gets floors from rooms
    ceilings: Dict[str, ArchCeiling] = field(
        default_factory=dict
    )  # TODO: make this a property instead that gets ceilings from rooms
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def doors(self) -> List[ArchOpening]:
        """Get all door openings across all walls.

        Returns:
            List of ArchOpening objects with type="Door"
        """
        return [
            o
            for w in self.walls.values()
            if w.openings
            for o in w.openings
            if o.type == "Door"
        ]

    @property
    def windows(self) -> List[ArchOpening]:
        """Get all window openings across all walls.

        Returns:
            List of ArchOpening objects with type="Window"
        """
        return [
            o
            for w in self.walls.values()
            if w.openings
            for o in w.openings
            if o.type == "Window"
        ]

    def add_room(self, room: ArchRoom) -> None:
        """Add a room to the architecture."""
        self.rooms[room.id] = room

    def add_wall(self, wall: ArchWall) -> None:
        """Add a wall to the architecture."""
        self.walls[wall.id] = wall

        # Add wall to room's wall list
        if wall.room_id in self.rooms:
            self.rooms[wall.room_id].wall_ids.append(wall.id)

    def add_floor(self, floor: ArchFloor) -> None:
        """Add a floor to the architecture."""
        self.floors[floor.id] = floor

        # Link floor to room
        if floor.room_id in self.rooms:
            self.rooms[floor.room_id].floor = floor

    def add_ceiling(self, ceiling: ArchCeiling) -> None:
        """Add a ceiling to the architecture."""
        self.ceilings[ceiling.id] = ceiling

        # Link ceiling to room
        if ceiling.room_id in self.rooms:
            self.rooms[ceiling.room_id].ceiling = ceiling

    def get_room(self, room_id: str) -> Optional[ArchRoom]:
        """Get room by ID."""
        return self.rooms.get(room_id)

    def get_wall(self, wall_id: str) -> Optional[ArchWall]:
        """Get wall by ID."""
        return self.walls.get(wall_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "version": self.version,
            "up": self.up.to_dict(),
            "front": self.front.to_dict(),
            "scale_to_meters": self.scale_to_meters,
            "defaults": self.defaults.to_dict(),
            "rooms": [room.to_dict() for room in self.rooms.values()],
            "walls": [wall.to_dict() for wall in self.walls.values()],
            "floors": [floor.to_dict() for floor in self.floors.values()],
            "ceilings": [ceiling.to_dict() for ceiling in self.ceilings.values()],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Architecture":
        """Create Architecture from dictionary."""
        arch = Architecture(
            id=data.get("id", str(dict_to_uuid(data))),
            version=data.get("version", "0.0.1"),
            metadata=data.get("metadata", {}),
        )
        if (up := data.get("up")) is not None:
            arch.up = Point3D(**up)
        if (front := data.get("front")) is not None:
            arch.front = Point3D(**front)
        if (
            scale_to_meters := data.get("scale_to_meters", data.get("unit"))
        ) is not None:
            arch.scale_to_meters = scale_to_meters
        if (defaults := data.get("defaults")) is not None:
            arch.defaults = ArchitectureDefaults()
            if (wall_default := defaults.get("Wall")) is not None:
                arch.defaults.Wall = WallDefault(**wall_default)
            if (ceiling_default := defaults.get("Ceiling")) is not None:
                arch.defaults.Ceiling = CeilingDefault(**ceiling_default)
            if (floor_default := defaults.get("Floor")) is not None:
                arch.defaults.Floor = FloorDefault(**floor_default)
            if (ground_default := defaults.get("Ground")) is not None:
                arch.defaults.Ground = GroundDefault(**ground_default)

        # Load rooms
        for room_data in data.get("rooms", []):
            room = ArchRoom.from_dict(room_data)
            arch.add_room(room)

        # Load walls
        for wall_data in data.get("walls", []):
            wall = ArchWall.from_dict(wall_data)
            arch.add_wall(wall)

        # Load floors
        for floor_data in data.get("floors", []):
            floor = ArchFloor.from_dict(floor_data)
            arch.add_floor(floor)

        # Load ceilings
        for ceiling_data in data.get("ceilings", []):
            ceiling = ArchCeiling.from_dict(ceiling_data)
            arch.add_ceiling(ceiling)

        return arch

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[ArchitectureAdapter]
    ) -> None:
        """Register a format adapter for Architecture."""
        _ARCHITECTURE_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, data: Dict[str, Any], **kwargs
    ) -> "Architecture":
        """Convert from specified format to Architecture."""
        if format_name not in _ARCHITECTURE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCHITECTURE_ADAPTERS[format_name].from_format(data, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert Architecture to specified format."""
        if format_name not in _ARCHITECTURE_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _ARCHITECTURE_ADAPTERS[format_name].to_format(self)
