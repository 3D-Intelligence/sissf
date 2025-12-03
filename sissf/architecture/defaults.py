"""
defaults.py
---
Default values for architectural elements (walls, floors, ceilings, ground).
"""

from dataclasses import dataclass, field

from ..utils import Dictionable


@dataclass
class DepthDefault(Dictionable):
    """Architecture depth default."""

    depth: float = 0.05


@dataclass
class WallDefault(DepthDefault):
    depth: float = 0.1
    extra_height: float = 0.0


@dataclass
class CeilingDefault(DepthDefault):
    pass


@dataclass
class FloorDefault(DepthDefault):
    pass


@dataclass
class GroundDefault(DepthDefault):
    pass


@dataclass
class ArchitectureDefaults(Dictionable):
    """Architecture defaults."""

    Wall: WallDefault = field(default_factory=WallDefault)
    Ceiling: CeilingDefault = field(default_factory=CeilingDefault)
    Floor: FloorDefault = field(default_factory=FloorDefault)
    Ground: GroundDefault = field(default_factory=GroundDefault)
