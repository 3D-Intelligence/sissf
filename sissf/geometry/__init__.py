"""
Geometry utilities for 3D scene generation.

Provides lightweight point and bounding box classes with rich operations,
inspired by libsg (https://github.com/smartscenes/libsg).

These are plain Python classes for performance and NumPy interop.
"""

from .bbox import BBox3D
from .point import Point, Point2D, Point3D
from .transform import _TRANSFORM_ADAPTERS, Transform, TransformAdapter

__all__ = [
    # Bbox
    "BBox3D",
    # Point
    "Point",
    "Point2D",
    "Point3D",
    # Transform
    "_TRANSFORM_ADAPTERS",
    "Transform",
    "TransformAdapter",
]
