"""
3D Bounding Box with rich face operations.

Inspired by libsg (https://github.com/smartscenes/libsg).
"""

import random
from typing import TYPE_CHECKING, Any, Optional, Sequence

from .point import Point3D

if TYPE_CHECKING:
    from pydantic_core import core_schema


class BBox3D:
    """
    Axis-aligned bounding box in 3D space.

    Provides utilities for face access, containment checks, intersection,
    and spatial sampling.
    """

    # Face indices
    LEFT = 0
    RIGHT = 1
    BOTTOM = 2
    TOP = 3
    FRONT = 4
    BACK = 5

    def __init__(self, min: Point3D, max: Point3D):
        """
        Initialize bounding box.

        Args:
            min: Minimum coordinates (corner)
            max: Maximum coordinates (opposite corner)

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
        """
        if min.x > max.x or min.y > max.y or min.z > max.z:
            raise ValueError(f"Invalid bbox: min {min} is not less than max {max}")

        self.min: Point3D = min
        self.max: Point3D = max

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> "core_schema.CoreSchema":
        """
        Provide Pydantic schema for BBox3D serialization/validation.

        This allows BBox3D to be used directly in Pydantic models:
        - Accepts BBox3D objects or dicts with min/max
        - Serializes to dict {"min": {...}, "max": {...}}
        """
        from pydantic_core import core_schema

        python_schema = core_schema.is_instance_schema(cls)

        def validate_bbox3d(value: Any) -> "BBox3D":
            if isinstance(value, BBox3D):
                return value
            elif isinstance(value, dict):
                if "min" in value and "max" in value:
                    min_pt = value["min"]
                    max_pt = value["max"]
                    # Convert dicts to Point3D if needed
                    if isinstance(min_pt, dict):
                        min_pt = Point3D.from_dict(min_pt)
                    if isinstance(max_pt, dict):
                        max_pt = Point3D.from_dict(max_pt)
                    return cls(min_pt, max_pt)
            raise ValueError(
                f"Cannot convert {type(value)} to BBox3D. "
                "Expected BBox3D or dict with 'min' and 'max'"
            )

        def serialize_bbox3d(value: "BBox3D") -> dict[str, Any]:
            return {"min": value.min.to_dict(), "max": value.max.to_dict()}

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.union_schema(
                        [
                            core_schema.dict_schema(),
                            python_schema,
                        ]
                    ),
                    core_schema.no_info_plain_validator_function(validate_bbox3d),
                ]
            ),
            python_schema=core_schema.union_schema(
                [
                    python_schema,
                    core_schema.no_info_plain_validator_function(validate_bbox3d),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_bbox3d
            ),
        )

    @property
    def center(self) -> Point3D:
        """
        Compute center/centroid of bounding box.

        Returns:
            Center point

        Example:
            >>> BBox3D(Point3D(0,0,0), Point3D(2,2,2)).center
            Point3D(1.0, 1.0, 1.0)
        """
        return Point3D.mean([self.min, self.max])

    @property
    def centroid(self) -> Point3D:
        """Alias for center"""
        return self.center

    @property
    def dims(self) -> Point3D:
        """
        Compute dimensions (width, height, depth) of bounding box.

        Returns:
            Dimensions as Point3D

        Example:
            >>> BBox3D(Point3D(0,0,0), Point3D(2,3,4)).dims
            Point3D(2.0, 3.0, 4.0)
        """
        return Point3D.sub(self.max, self.min)

    @property
    def size(self) -> Point3D:
        """Alias for dims"""
        return self.dims

    @property
    def width(self) -> float:
        """Width (X dimension)"""
        return self.max.x - self.min.x

    @property
    def height(self) -> float:
        """Height (Y dimension)"""
        return self.max.y - self.min.y

    @property
    def depth(self) -> float:
        """Depth (Z dimension)"""
        return self.max.z - self.min.z

    @property
    def volume(self) -> float:
        """
        Compute volume of bounding box.

        Returns:
            Volume

        Example:
            >>> BBox3D(Point3D(0,0,0), Point3D(2,3,4)).volume
            24.0
        """
        dims = self.dims
        return dims.x * dims.y * dims.z

    def contains(self, p: Point3D) -> bool:
        """
        Check if point is within box bounds (inclusive).

        Args:
            p: Point to check

        Returns:
            True if point is inside or on boundary

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> bbox.contains(Point3D(0.5, 0.5, 0.5))
            True
            >>> bbox.contains(Point3D(2, 0, 0))
            False
        """
        return (
            (self.max.x >= p.x >= self.min.x)
            and (self.max.y >= p.y >= self.min.y)
            and (self.max.z >= p.z >= self.min.z)
        )

    def intersects(self, other: "BBox3D") -> bool:
        """
        Check if this bounding box intersects with another.

        Args:
            other: Other bounding box

        Returns:
            True if boxes overlap

        Example:
            >>> b1 = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> b2 = BBox3D(Point3D(0.5,0.5,0.5), Point3D(1.5,1.5,1.5))
            >>> b1.intersects(b2)
            True
        """
        return (
            (self.min.x <= other.max.x and self.max.x >= other.min.x)
            and (self.min.y <= other.max.y and self.max.y >= other.min.y)
            and (self.min.z <= other.max.z and self.max.z >= other.min.z)
        )

    def expand(self, amount: float) -> "BBox3D":
        """
        Return expanded bounding box.

        Args:
            amount: Amount to expand in all directions

        Returns:
            New expanded bounding box

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> expanded = bbox.expand(0.5)
            >>> expanded.min
            Point3D(-0.5, -0.5, -0.5)
        """
        return BBox3D(
            Point3D(self.min.x - amount, self.min.y - amount, self.min.z - amount),
            Point3D(self.max.x + amount, self.max.y + amount, self.max.z + amount),
        )

    def get_face_center(self, index: int) -> Point3D:
        """
        Get center point of specified face.

        Args:
            index: Face index (LEFT, RIGHT, BOTTOM, TOP, FRONT, BACK)

        Returns:
            Center point of face

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> bbox.get_face_center(BBox3D.TOP)
            Point3D(0.5, 0.5, 1.0)
        """
        point = self.center

        if index == BBox3D.LEFT:
            point.x = self.min.x
        elif index == BBox3D.RIGHT:
            point.x = self.max.x
        elif index == BBox3D.BOTTOM:
            point.z = self.min.z
        elif index == BBox3D.TOP:
            point.z = self.max.z
        elif index == BBox3D.FRONT:
            point.y = self.max.y
        elif index == BBox3D.BACK:
            point.y = self.min.y

        return point

    def get_face_outnormal(self, index: int) -> Point3D:
        """
        Get outward-facing unit normal vector for specified face.

        Args:
            index: Face index (LEFT, RIGHT, BOTTOM, TOP, FRONT, BACK)

        Returns:
            Unit normal vector

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> bbox.get_face_outnormal(BBox3D.TOP)
            Point3D(0, 0, 1)
        """
        if index == BBox3D.LEFT:
            return Point3D(-1, 0, 0)
        elif index == BBox3D.RIGHT:
            return Point3D(+1, 0, 0)
        elif index == BBox3D.BOTTOM:
            return Point3D(0, 0, -1)
        elif index == BBox3D.TOP:
            return Point3D(0, 0, +1)
        elif index == BBox3D.FRONT:
            return Point3D(0, -1, 0)
        elif index == BBox3D.BACK:
            return Point3D(0, +1, 0)
        else:
            raise ValueError(f"Invalid face index: {index}")

    def get_face_normal(self, index: int) -> Point3D:
        """Alias for get_face_outnormal"""
        return self.get_face_outnormal(index)

    def get_face_dims(self, index: int) -> Point3D:
        """
        Get dimensions of specified face.

        Args:
            index: Face index

        Returns:
            Face dimensions as Point3D

        Note:
            Returns dimensions reordered based on face orientation
        """
        dims = self.dims
        if index == BBox3D.LEFT or index == BBox3D.RIGHT:
            return Point3D(dims.y, dims.z, dims.x)
        elif index == BBox3D.BOTTOM or index == BBox3D.TOP:
            return Point3D(dims.x, dims.y, dims.z)
        else:  # FRONT or BACK
            return Point3D(dims.x, dims.z, dims.y)

    def get_point_on_face(
        self, index: int, r: list[float], margin: Optional[tuple[float, float]] = None
    ) -> Point3D:
        """
        Get point on face using normalized coordinates.

        Args:
            index: Face index
            r: Normalized coordinates [0, 1] for position on face
            margin: Optional (min_margin, max_margin) to inset from edges

        Returns:
            Point on face

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> bbox.get_point_on_face(BBox3D.TOP, [0.5, 0.5])
            Point3D(0.5, 0.5, 1.0)
        """
        face_dims = self.get_face_dims(index)
        p0 = self.min
        p1 = self.max
        m0 = margin[0] if margin else 0
        m1 = margin[1] if margin else 0
        d0 = r[0] * (face_dims[0] - m0) + m0
        d1 = r[1] * (face_dims[1] - m1) + m1

        if index == BBox3D.LEFT:
            point = Point3D(p0[0], p0[1] + d0, p0[2] + d1)
        elif index == BBox3D.RIGHT:
            point = Point3D(p1[0], p0[1] + d0, p0[2] + d1)
        elif index == BBox3D.BOTTOM:
            point = Point3D(p0[0] + d0, p0[1] + d1, p0[2])
        elif index == BBox3D.TOP:
            point = Point3D(p0[0] + d0, p0[1] + d1, p1[2])
        elif index == BBox3D.FRONT:
            point = Point3D(p0[0] + d0, p0[1], p0[2] + d1)
        elif index == BBox3D.BACK:
            point = Point3D(p0[0] + d0, p1[1], p0[2] + d1)
        else:
            raise ValueError(f"Invalid face index: {index}")

        return point

    def sample_face(
        self, index: int, margin: Optional[tuple[float, float]] = None
    ) -> Point3D:
        """
        Sample a random point on the specified face.

        Args:
            index: Face index
            margin: Optional margins to avoid edges

        Returns:
            Random point on face

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> point = bbox.sample_face(BBox3D.TOP)
            >>> 0 <= point.x <= 1 and 0 <= point.y <= 1 and point.z == 1.0
            True
        """
        return self.get_point_on_face(
            index, [random.uniform(0, 1), random.uniform(0, 1)], margin
        )

    @classmethod
    def from_point_list(cls, points: Sequence[Point3D]) -> "BBox3D":
        """
        Construct axis-aligned bounding box containing all points.

        Args:
            points: Collection of points to bound

        Returns:
            Bounding box

        Example:
            >>> points = [Point3D(0,0,0), Point3D(1,2,3), Point3D(-1,-1,-1)]
            >>> bbox = BBox3D.from_point_list(points)
            >>> bbox.min
            Point3D(-1.0, -1.0, -1.0)
        """
        min_point = Point3D.min(points)
        max_point = Point3D.max(points)
        return cls(min_point, max_point)

    @classmethod
    def from_min_max(cls, min: Sequence[float], max: Sequence[float]) -> "BBox3D":
        """
        Construct bounding box from min and max coordinate sequences.

        Args:
            min: Minimum coordinates [x, y, z]
            max: Maximum coordinates [x, y, z]

        Returns:
            Bounding box

        Example:
            >>> bbox = BBox3D.from_min_max([0, 0, 0], [1, 1, 1])
        """
        min_point = Point3D.fromlist(min)
        max_point = Point3D.fromlist(max)
        return cls(min_point, max_point)

    @classmethod
    def from_center_size(cls, center: Point3D, size: Point3D) -> "BBox3D":
        """
        Construct bounding box from center point and size.

        Args:
            center: Center point
            size: Dimensions (width, height, depth)

        Returns:
            Bounding box

        Example:
            >>> bbox = BBox3D.from_center_size(Point3D(0,0,0), Point3D(2,2,2))
            >>> bbox.min
            Point3D(-1.0, -1.0, -1.0)
        """
        half_size = size * 0.5
        return cls(center - half_size, center + half_size)

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with 'min' and 'max' keys

        Example:
            >>> bbox = BBox3D(Point3D(0,0,0), Point3D(1,1,1))
            >>> bbox.to_dict()
            {'min': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'max': {'x': 1.0, 'y': 1.0, 'z': 1.0}}
        """
        return {"min": self.min.to_dict(), "max": self.max.to_dict()}

    @classmethod
    def from_dict(cls, d: dict) -> "BBox3D":
        """
        Construct from dictionary.

        Args:
            d: Dictionary with 'min' and 'max' keys

        Returns:
            Bounding box
        """
        return cls(Point3D.from_dict(d["min"]), Point3D.from_dict(d["max"]))

    def __str__(self) -> str:
        """String representation"""
        return f"BBox3D({self.min}, {self.max})"

    def __repr__(self) -> str:
        """String representation"""
        return self.__str__()
