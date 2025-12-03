"""
Point classes for 2D and 3D geometry.

Lightweight plain Python classes inspired by libsg (https://github.com/smartscenes/libsg).
"""

import math
from typing import TYPE_CHECKING, Any, Sequence, TypeVar

import numpy as np
from scipy.spatial.transform import Rotation as ScipyRotation

if TYPE_CHECKING:
    from pydantic_core import core_schema

Self = TypeVar("Self", bound="Point")


class Point:
    """
    Base class for points in N-dimensional space.

    Provides vector operations, distance calculations, and axis manipulations.
    Subclasses define SIZE and implement __init__, __getitem__, and tolist().
    """

    SIZE: int  # Subclasses must define

    def __getitem__(self, key: int) -> float:
        """
        Get coordinate by index.

        Must be implemented by subclasses.

        Args:
            key: Index (0 for x, 1 for y, etc.)

        Returns:
            Coordinate value
        """
        raise NotImplementedError

    def tolist(self) -> list[float]:
        """
        Convert point to list of coordinates.

        Must be implemented by subclasses.

        Returns:
            List of coordinate values
        """
        raise NotImplementedError

    @classmethod
    def fromlist(cls: type[Self], coords: Sequence[float]) -> Self:
        """
        Construct point from sequence of coordinates.

        Args:
            coords: Sequence of coordinate values

        Returns:
            New point instance

        Example:
            >>> Point3D.fromlist([1.0, 2.0, 3.0])
            Point3D(1.0, 2.0, 3.0)
        """
        return cls(*coords)

    @classmethod
    def min(cls: type[Self], points: Sequence[Self]) -> Self:
        """
        Compute element-wise minimum across collection of points.

        Args:
            points: Collection of points

        Returns:
            Point with minimum value per dimension

        Example:
            >>> Point3D.min([Point3D(1,2,3), Point3D(0,5,2)])
            Point3D(0.0, 2.0, 2.0)
        """
        return cls(*[min(p[i] for p in points) for i in range(cls.SIZE)])

    @classmethod
    def max(cls: type[Self], points: Sequence[Self]) -> Self:
        """
        Compute element-wise maximum across collection of points.

        Args:
            points: Collection of points

        Returns:
            Point with maximum value per dimension

        Example:
            >>> Point3D.max([Point3D(1,2,3), Point3D(0,5,2)])
            Point3D(1.0, 5.0, 3.0)
        """
        return cls(*[max(p[i] for p in points) for i in range(cls.SIZE)])

    @classmethod
    def sum(cls: type[Self], points: Sequence[Self]) -> Self:
        """
        Compute element-wise sum across collection of points.

        Args:
            points: Collection of points

        Returns:
            Point with summed values per dimension
        """
        return cls(*[sum(p[i] for p in points) for i in range(cls.SIZE)])

    @classmethod
    def mean(cls: type[Self], points: Sequence[Self]) -> Self:
        """
        Compute centroid (mean) of collection of points.

        Args:
            points: Collection of points

        Returns:
            Centroid point

        Example:
            >>> Point3D.mean([Point3D(0,0,0), Point3D(2,2,2)])
            Point3D(1.0, 1.0, 1.0)
        """
        k = len(points)
        return cls(*[sum(p[i] for p in points) / k for i in range(cls.SIZE)])

    @classmethod
    def sub(cls: type[Self], a: Self, b: Self) -> Self:
        """
        Subtract one point from another element-wise.

        Args:
            a: First point
            b: Second point to subtract

        Returns:
            Difference vector
        """
        return cls(*[a[i] - b[i] for i in range(cls.SIZE)])

    def __sub__(self: Self, other: Self) -> Self:
        """Subtract operator: a - b"""
        return self.__class__.sub(self, other)

    @classmethod
    def add(cls: type[Self], a: Self, b: Self) -> Self:
        """
        Add two points element-wise.

        Args:
            a: First point
            b: Second point

        Returns:
            Sum vector
        """
        return cls(*[a[i] + b[i] for i in range(cls.SIZE)])

    def __add__(self: Self, other: Self) -> Self:
        """Addition operator: a + b"""
        return self.__class__.add(self, other)

    @classmethod
    def mult(cls: type[Self], a: Self, scalar: float) -> Self:
        """
        Multiply point by scalar.

        Args:
            a: Point
            scalar: Scalar multiplier

        Returns:
            Scaled point
        """
        return cls(*[a[i] * scalar for i in range(cls.SIZE)])

    def __mul__(self: Self, scalar: float) -> Self:
        """Multiplication operator: point * scalar"""
        return self.__class__.mult(self, scalar)

    def __rmul__(self: Self, scalar: float) -> Self:
        """Reverse multiplication operator: scalar * point"""
        return self.__mul__(scalar)

    @classmethod
    def div(cls: type[Self], a: Self, scalar: float) -> Self:
        """
        Divide point by scalar.

        Args:
            a: Point
            scalar: Scalar divisor

        Returns:
            Scaled point
        """
        return cls(*[a[i] / scalar for i in range(cls.SIZE)])

    def __truediv__(self: Self, scalar: float) -> Self:
        """Division operator: point / scalar"""
        return self.__class__.div(self, scalar)

    @classmethod
    def distance_sq(cls: type[Self], a: Self, b: Self) -> float:
        """
        Compute squared Euclidean distance between two points.

        Faster than distance() when you only need relative distances.

        Args:
            a: First point
            b: Second point

        Returns:
            Squared distance
        """
        return sum((a[i] - b[i]) ** 2 for i in range(cls.SIZE))

    @classmethod
    def distance(cls: type[Self], a: Self, b: Self) -> float:
        """
        Compute Euclidean distance between two points.

        Args:
            a: First point
            b: Second point

        Returns:
            Distance

        Example:
            >>> Point3D.distance(Point3D(0,0,0), Point3D(3,4,0))
            5.0
        """
        return math.sqrt(cls.distance_sq(a, b))

    def distance_to(self: Self, other: Self) -> float:
        """
        Compute distance from this point to another.

        Args:
            other: Target point

        Returns:
            Distance

        Example:
            >>> Point3D(0,0,0).distance_to(Point3D(3,4,0))
            5.0
        """
        return self.__class__.distance(self, other)

    def swap_axes(self: Self, axis_1: int, axis_2: int) -> Self:
        """
        Return new point with two axes swapped.

        Args:
            axis_1: Index of first axis to swap
            axis_2: Index of second axis to swap

        Returns:
            New point with axes swapped

        Example:
            >>> Point3D(1, 2, 3).swap_axes(0, 1)
            Point3D(2.0, 1.0, 3.0)
        """
        if axis_1 == axis_2:
            return self

        point = self.tolist()
        transform_matrix = np.eye(len(point))
        row_1 = np.copy(transform_matrix[axis_1])
        row_2 = np.copy(transform_matrix[axis_2])
        transform_matrix[axis_1, :] = row_2
        transform_matrix[axis_2, :] = row_1

        new_point = transform_matrix @ np.array(point)
        return self.__class__.fromlist(new_point)  # type: ignore

    def invert(self: Self, axis: int) -> Self:
        """
        Return new point with specified axis inverted (negated).

        Args:
            axis: Index of axis to invert

        Returns:
            New point with axis inverted

        Example:
            >>> Point3D(1, 2, 3).invert(0)
            Point3D(-1.0, 2.0, 3.0)
        """
        point = self.tolist()
        point[axis] = -point[axis]
        return self.__class__.fromlist(point)

    def magnitude(self) -> float:
        """
        Compute magnitude (length) of vector from origin to this point.

        Returns:
            Magnitude

        Example:
            >>> Point3D(3, 4, 0).magnitude()
            5.0
        """
        return math.sqrt(sum(self[i] ** 2 for i in range(self.SIZE)))

    def length(self) -> float:
        """Alias for magnitude()"""
        return self.magnitude()

    def to_dict(self) -> dict[str, float]:
        """
        Convert point to dictionary for JSON serialization.

        Must be implemented by subclasses.

        Returns:
            Dictionary with coordinate keys
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls: type[Self], d: dict[str, float]) -> Self:
        """
        Construct point from dictionary.

        Must be implemented by subclasses.

        Args:
            d: Dictionary with coordinate keys

        Returns:
            New point instance
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """String representation"""
        coords = ", ".join(str(self[i]) for i in range(self.SIZE))
        return f"{self.__class__.__name__}({coords})"

    def __str__(self) -> str:
        """String representation (same as repr)"""
        return str(self.tolist())

    def __eq__(self, other: object) -> bool:
        """
        Check equality with floating point tolerance.

        Uses relative and absolute tolerance for robust comparison.

        Args:
            other: Object to compare with

        Returns:
            True if points are equal within tolerance

        Example:
            >>> Point(1.0) == Point(1.0000001)
            True
        """
        if not isinstance(other, Point):
            return NotImplemented

        return math.isclose(self.SIZE, other.SIZE, rel_tol=1e-7, abs_tol=1e-7)


class Point2D(Point):
    """
    2D point with x, y coordinates.

    Lightweight plain Python class for performance.
    """

    SIZE = 2

    def __init__(self, x: float, y: float):
        """
        Initialize 2D point.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x: float = float(x)
        self.y: float = float(y)

    def __getitem__(self, key: int) -> float:
        """Get coordinate by index (0=x, 1=y)"""
        return (self.x, self.y)[key]

    def tolist(self) -> list[float]:
        """Convert to list [x, y]"""
        return [self.x, self.y]

    def to_tuple(self) -> tuple[float, float]:
        """Convert to tuple (x, y)"""
        return (self.x, self.y)

    def to_dict(self) -> dict[str, float]:
        """Convert to dict {"x": x, "y": y}"""
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> "Point2D":
        """Construct from dict with 'x', 'y' keys"""
        return cls(d["x"], d["y"])

    def __eq__(self, other: object) -> bool:
        """
        Check equality with floating point tolerance.

        Uses relative and absolute tolerance for robust comparison.

        Args:
            other: Object to compare with

        Returns:
            True if points are equal within tolerance

        Example:
            >>> Point2D(1.0, 2.0) == Point2D(1.0000001, 2.0)
            True
        """
        if not isinstance(other, Point2D):
            return NotImplemented

        return math.isclose(
            self.x, other.x, rel_tol=1e-7, abs_tol=1e-7
        ) and math.isclose(self.y, other.y, rel_tol=1e-7, abs_tol=1e-7)


class Point3D(Point):
    """
    3D point with x, y, z coordinates.

    Lightweight plain Python class with rich 3D operations.
    """

    SIZE = 3

    def __init__(self, x: float, y: float, z: float):
        """
        Initialize 3D point.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.z: float = float(z)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> "core_schema.CoreSchema":
        """
        Provide Pydantic schema for Point3D serialization/validation.

        This allows Point3D to be used directly in Pydantic models:
        - Accepts Point3D objects, dicts with x/y/z, or lists [x, y, z]
        - Serializes to dict {"x": x, "y": y, "z": z}
        """
        from pydantic_core import core_schema

        def validate_point3d(value: Any) -> "Point3D":
            if isinstance(value, Point3D):
                return value
            elif isinstance(value, dict):
                return cls.from_dict(value)
            elif isinstance(value, (list, tuple)) and len(value) == 3:
                return cls(value[0], value[1], value[2])
            else:
                raise ValueError(
                    f"Cannot convert {type(value)} to Point3D. "
                    "Expected Point3D, dict with x/y/z, or list [x,y,z]"
                )

        def serialize_point3d(value: "Point3D") -> dict[str, float]:
            return value.to_dict()

        # python_schema = core_schema.is_instance_schema(cls)

        # return core_schema.json_or_python_schema(
        #     json_schema=core_schema.chain_schema(
        #         [
        #             core_schema.union_schema(
        #                 [
        #                     core_schema.dict_schema(),
        #                     core_schema.list_schema(),
        #                     python_schema,
        #                 ]
        #             ),
        #             core_schema.no_info_plain_validator_function(validate_point3d),
        #         ]
        #     ),
        #     python_schema=core_schema.union_schema(
        #         [
        #             python_schema,
        #             core_schema.no_info_plain_validator_function(validate_point3d),
        #         ]
        #     ),
        #     serialization=core_schema.plain_serializer_function_ser_schema(
        #         serialize_point3d
        #     ),
        # )

        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.no_info_plain_validator_function(validate_point3d),
            ]
        )

        return core_schema.json_or_python_schema(
            # JSON schema: describe what the JSON representation looks like
            json_schema=core_schema.union_schema(
                [
                    # Either a dict with x, y, z
                    core_schema.typed_dict_schema(
                        {
                            "x": core_schema.typed_dict_field(
                                core_schema.float_schema()
                            ),
                            "y": core_schema.typed_dict_field(
                                core_schema.float_schema()
                            ),
                            "z": core_schema.typed_dict_field(
                                core_schema.float_schema()
                            ),
                        }
                    ),
                    # Or a list of 3 floats
                    core_schema.list_schema(
                        items_schema=core_schema.float_schema(),
                        min_length=3,
                        max_length=3,
                    ),
                ]
            ),
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_point3d
            ),
        )

    def __getitem__(self, key: int) -> float:
        """Get coordinate by index (0=x, 1=y, 2=z)"""
        return (self.x, self.y, self.z)[key]

    def tolist(self) -> list[float]:
        """Convert to list [x, y, z]"""
        return [self.x, self.y, self.z]

    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to tuple (x, y, z)"""
        return (self.x, self.y, self.z)

    def to_dict(self) -> dict[str, float]:
        """Convert to dict {"x": x, "y": y, "z": z}"""
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> "Point3D":
        """Construct from dict with 'x', 'y', 'z' keys"""
        return cls(d["x"], d["y"], d["z"])

    def scale(self, s: float) -> "Point3D":
        """
        Scale point along vector from origin by factor s.

        Modifies this point in-place.

        Args:
            s: Scale factor

        Returns:
            Self for chaining
        """
        self.x *= s
        self.y *= s
        self.z *= s
        return self

    def normalize(self) -> "Point3D":
        """
        Normalize vector from origin to point (make unit length).

        Modifies this point in-place.

        Returns:
            Self for chaining

        Example:
            >>> Point3D(3, 4, 0).normalize()
            Point3D(0.6, 0.8, 0.0)
        """
        length = self.length()
        if length > 0:
            self.scale(1.0 / length)
        return self

    def normalized(self) -> "Point3D":
        """
        Return normalized copy without modifying original.

        Returns:
            Normalized point

        Example:
            >>> p = Point3D(3, 4, 0)
            >>> p.normalized()  # p is unchanged
            Point3D(0.6, 0.8, 0.0)
        """
        return Point3D(self.x, self.y, self.z).normalize()

    def rotate(self, axis: int, angle: float) -> "Point3D":
        """
        Rotate point about an axis by given angle (in radians).

        Modifies this point in-place.

        Args:
            axis: Axis index (0=X, 1=Y, 2=Z)
            angle: Rotation angle in radians

        Returns:
            Self for chaining

        Example:
            >>> import math
            >>> Point3D(1, 0, 0).rotate(2, math.pi/2)  # Rotate around Z
            Point3D(0.0, 1.0, 0.0)
        """
        point = self.tolist()
        rotvec = np.zeros(3, dtype=float)
        rotvec[axis] = angle
        new_point = ScipyRotation.from_rotvec(rotvec).as_matrix() @ np.array(point)
        self.x, self.y, self.z = new_point[0], new_point[1], new_point[2]
        return self

    def rotated(self, axis: int, angle: float) -> "Point3D":
        """
        Return rotated copy without modifying original.

        Args:
            axis: Axis index (0=X, 1=Y, 2=Z)
            angle: Rotation angle in radians

        Returns:
            Rotated point
        """
        return Point3D(self.x, self.y, self.z).rotate(axis, angle)

    def translate(self, vec: np.ndarray) -> "Point3D":
        """
        Translate point by vector.

        Modifies this point in-place.

        Args:
            vec: Translation vector (numpy array or array-like)

        Returns:
            Self for chaining

        Example:
            >>> Point3D(1, 2, 3).translate(np.array([1, 1, 1]))
            Point3D(2.0, 3.0, 4.0)
        """
        point = np.array(self.tolist())
        transformed = point + vec
        self.x, self.y, self.z = transformed[0], transformed[1], transformed[2]
        return self

    def translated(self, vec: np.ndarray) -> "Point3D":
        """
        Return translated copy without modifying original.

        Args:
            vec: Translation vector

        Returns:
            Translated point
        """
        return Point3D(self.x, self.y, self.z).translate(vec)

    def cross(self, other: "Point3D") -> "Point3D":
        """
        Compute cross product with another vector.

        Args:
            other: Other vector

        Returns:
            Cross product vector

        Example:
            >>> Point3D(1,0,0).cross(Point3D(0,1,0))
            Point3D(0.0, 0.0, 1.0)
        """
        return Point3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other: "Point3D") -> float:
        """
        Compute dot product with another vector.

        Args:
            other: Other vector

        Returns:
            Dot product

        Example:
            >>> Point3D(1,2,3).dot(Point3D(4,5,6))
            32.0
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __eq__(self, other: object) -> bool:
        """
        Check equality with floating point tolerance.

        Uses relative and absolute tolerance for robust comparison.

        Args:
            other: Object to compare with

        Returns:
            True if points are equal within tolerance

        Example:
            >>> Point3D(1.0, 2.0, 3.0) == Point3D(1.0000001, 2.0, 3.0)
            True
        """
        if not isinstance(other, Point3D):
            return NotImplemented

        return (
            math.isclose(self.x, other.x, rel_tol=1e-7, abs_tol=1e-7)
            and math.isclose(self.y, other.y, rel_tol=1e-7, abs_tol=1e-7)
            and math.isclose(self.z, other.z, rel_tol=1e-7, abs_tol=1e-7)
        )
