import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol, Tuple, Type

import numpy as np
from scipy.spatial.transform import Rotation

_TRANSFORM_ADAPTERS: Dict[str, Type["TransformAdapter"]] = {}


class TransformAdapter(Protocol):
    """Protocol for Transform format adapters."""

    @staticmethod
    def from_format(obj: Dict[str, Any], **kwargs) -> "Transform":
        """Convert from format to Transform."""
        ...

    @staticmethod
    def to_format(instance: "Transform", **kwargs) -> Dict[str, Any]:
        """Convert Transform to format."""
        ...


@dataclass
class Transform:
    """
    General class to handle arbitrary transforms of objects.

    Stores rotation (quaternion), translation, and scale with automatic
    matrix synchronization. Matrix is stored in transposed form.

    Examples:
        >>> # Create identity transform
        >>> xform = Transform()

        >>> # Create from components
        >>> xform = Transform.from_rts(
        ...     rotation=[0, 0, 0, 1],
        ...     translation=[1, 2, 3],
        ...     scale=[1, 1, 1]
        ... )

        >>> # Modify translation
        >>> xform.set_translation([5, 6, 7])
        >>> print(xform.translation)
        [5.0, 6.0, 7.0]
    """

    _r: List[float] = field(
        default_factory=lambda: [0.0, 0.0, 0.0, 1.0]
    )  # quaternion [x,y,z,w]
    _t: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # [x,y,z]
    _s: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])  # [sx,sy,sz]
    _mat4: List[List[float]] | List[float] = field(
        default_factory=lambda: np.identity(4).tolist()
    )

    @property
    def translation(self) -> List[float]:
        """Translation vector [x, y, z]."""
        return self._t

    def set_translation(self, t: List[float]) -> None:
        self._t = copy.deepcopy(t) if isinstance(t, list) else copy.deepcopy(t.tolist())
        self.__update_matrix()

    @property
    def rotation(self) -> List[float]:
        return self._r

    def set_rotation(self, r: List[float]) -> None:
        self._r = copy.deepcopy(r)
        self.__update_matrix()

    @property
    def scale(self) -> List[float]:
        return self._s

    def set_scale(self, s: float | List[float]) -> None:
        if isinstance(s, (int, float)):
            self._s = [float(s)] * 3
        else:
            self._s = (
                copy.deepcopy(s) if isinstance(s, list) else copy.deepcopy(s.tolist())
            )
        self.__update_matrix()

    @property
    def mat4(self) -> np.ndarray:
        return np.array(self._mat4)

    def __update_matrix(self) -> None:
        self._mat4 = Transform.rts_to_mat4(self._r, self._t, self._s).tolist()

    @classmethod
    def rts_to_mat4(
        cls, rotation: List[float], translation: List[float], scale: List[float]
    ) -> np.ndarray:
        """Convert rotation (quaternion), translation, scale to 4x4 matrix."""
        T = np.identity(4)
        T[:3, 3] = translation
        R = np.identity(4)
        R[:3, :3] = Rotation.from_quat(rotation).as_matrix()
        S = np.identity(4)
        S[:3, :3] = np.diag(scale)
        X = (T @ R @ S).transpose()

        return X

    @classmethod
    def mat4_to_rts(
        cls, mat4: np.ndarray
    ) -> Tuple[List[float], List[float], List[float]]:
        """Convert 4x4 matrix to rotation (quaternion), translation, scale."""
        mat4 = np.asarray(mat4).reshape((4, 4)).transpose()

        translation: np.ndarray = mat4[:3, 3]

        scale: np.ndarray = np.linalg.norm(mat4, axis=0)[:3]
        scale_zeros: np.ndarray = np.isclose(scale, [0, 0, 0])
        if np.any(scale_zeros):
            scale[scale_zeros] = 1e-7

        R = mat4[:3, :3] / scale
        if np.linalg.det(R) < 0:  # if reflection, flip one axis and negate scale
            R[:3, 0] *= -1
            scale[0] *= -1
        rotation: np.ndarray = Rotation.from_matrix(R).as_quat()

        return rotation.tolist(), translation.tolist(), scale.tolist()

    @classmethod
    def from_mat4(cls, mat4: np.ndarray) -> "Transform":
        """
        Create Transform from a 4x4 transformation matrix.

        Args:
            mat4: 4x4 transformation matrix (can be row or column major)

        Returns:
            Transform instance
        """
        xform = Transform()
        xform._mat4 = np.asarray(mat4).reshape((4, 4)).tolist()
        xform._r, xform._t, xform._s = Transform.mat4_to_rts(mat4)

        return xform

    @classmethod
    def from_rts(
        cls, rotation: List[float], translation: List[float], scale: List[float]
    ) -> "Transform":
        xform = Transform()
        xform._r = copy.deepcopy(rotation)
        xform._t = copy.deepcopy(translation)
        xform._s = copy.deepcopy(scale)
        xform._mat4 = Transform.rts_to_mat4(rotation, translation, scale).tolist()
        return xform

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "rotation": list(self._r),
            "translation": list(self._t),
            "scale": list(self._s),
            "matrix": self._mat4,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transform":
        """Create Transform from dictionary."""
        if "matrix" in data:
            return cls.from_mat4(data["matrix"])
        else:
            return cls.from_rts(
                rotation=data["rotation"],
                translation=data["translation"],
                scale=data["scale"],
            )

    @classmethod
    def register_adapter(
        cls, format_name: str, adapter: Type[TransformAdapter]
    ) -> None:
        """Register a format adapter for Transform."""
        _TRANSFORM_ADAPTERS[format_name] = adapter

    @classmethod
    def from_format(
        cls, format_name: str, obj: Dict[str, Any], **kwargs
    ) -> "Transform":
        """Convert from specified format to Transform."""
        if format_name not in _TRANSFORM_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _TRANSFORM_ADAPTERS[format_name].from_format(obj, **kwargs)

    def to_format(self, format_name: str, **kwargs) -> Dict[str, Any]:
        """Convert Transform to specified format."""
        if format_name not in _TRANSFORM_ADAPTERS:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return _TRANSFORM_ADAPTERS[format_name].to_format(self)
