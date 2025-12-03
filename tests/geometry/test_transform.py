"""Unit tests for Transform class."""

import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from sissf.geometry import Transform


class TestTransform(unittest.TestCase):
    """Test Transform class."""

    def test_init_default(self):
        """Test default Transform initialization."""
        xform = Transform()
        self.assertEqual(xform.rotation, [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(xform.translation, [0.0, 0.0, 0.0])
        self.assertEqual(xform.scale, [1.0, 1.0, 1.0])
        np.testing.assert_array_almost_equal(xform.mat4, np.identity(4))

    def test_translation_property(self):
        """Test translation property getter."""
        xform = Transform()
        self.assertEqual(xform.translation, [0.0, 0.0, 0.0])

    def test_set_translation(self):
        """Test set_translation method."""
        xform = Transform()
        xform.set_translation([1.0, 2.0, 3.0])
        self.assertEqual(xform.translation, [1.0, 2.0, 3.0])

    def test_set_translation_updates_matrix(self):
        """Test that set_translation updates the transformation matrix."""
        xform = Transform()
        xform.set_translation([1.0, 2.0, 3.0])
        mat4 = xform.mat4
        # Matrix is stored in transposed form, so translation is in last row
        self.assertAlmostEqual(mat4[3, 0], 1.0)
        self.assertAlmostEqual(mat4[3, 1], 2.0)
        self.assertAlmostEqual(mat4[3, 2], 3.0)

    def test_set_translation_from_array(self):
        """Test set_translation with numpy array."""
        xform = Transform()
        xform.set_translation(np.array([1.0, 2.0, 3.0]))
        self.assertEqual(xform.translation, [1.0, 2.0, 3.0])

    def test_rotation_property(self):
        """Test rotation property getter."""
        xform = Transform()
        self.assertEqual(xform.rotation, [0.0, 0.0, 0.0, 1.0])

    def test_set_rotation(self):
        """Test set_rotation method."""
        xform = Transform()
        # 90 degree rotation around z-axis
        rot_quat = Rotation.from_euler("z", 90, degrees=True).as_quat().tolist()
        xform.set_rotation(rot_quat)
        np.testing.assert_array_almost_equal(xform.rotation, rot_quat)

    def test_set_rotation_updates_matrix(self):
        """Test that set_rotation updates the transformation matrix."""
        xform = Transform()
        # 90 degree rotation around z-axis
        rot_quat = Rotation.from_euler("z", 90, degrees=True).as_quat().tolist()
        xform.set_rotation(rot_quat)
        mat4 = xform.mat4
        # Verify that rotation was applied (top-left 3x3 should not be identity)
        self.assertFalse(np.allclose(mat4[:3, :3], np.identity(3)))

    def test_scale_property(self):
        """Test scale property getter."""
        xform = Transform()
        self.assertEqual(xform.scale, [1.0, 1.0, 1.0])

    def test_set_scale_uniform(self):
        """Test set_scale with uniform scalar."""
        xform = Transform()
        xform.set_scale(2.0)
        self.assertEqual(xform.scale, [2.0, 2.0, 2.0])

    def test_set_scale_non_uniform(self):
        """Test set_scale with non-uniform scale."""
        xform = Transform()
        xform.set_scale([1.0, 2.0, 3.0])
        self.assertEqual(xform.scale, [1.0, 2.0, 3.0])

    def test_set_scale_from_array(self):
        """Test set_scale with numpy array."""
        xform = Transform()
        xform.set_scale(np.array([1.0, 2.0, 3.0]))
        self.assertEqual(xform.scale, [1.0, 2.0, 3.0])

    def test_set_scale_updates_matrix(self):
        """Test that set_scale updates the transformation matrix."""
        xform = Transform()
        xform.set_scale([2.0, 3.0, 4.0])
        mat4 = xform.mat4
        # Scale should be reflected in the matrix
        self.assertFalse(np.allclose(mat4, np.identity(4)))

    def test_mat4_property(self):
        """Test mat4 property returns numpy array."""
        xform = Transform()
        mat4 = xform.mat4
        self.assertIsInstance(mat4, np.ndarray)
        self.assertEqual(mat4.shape, (4, 4))

    def test_rts_to_mat4_identity(self):
        """Test rts_to_mat4 with identity transformation."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation = [0.0, 0.0, 0.0]
        scale = [1.0, 1.0, 1.0]
        mat4 = Transform.rts_to_mat4(rotation, translation, scale)
        np.testing.assert_array_almost_equal(mat4, np.identity(4))

    def test_rts_to_mat4_translation(self):
        """Test rts_to_mat4 with translation only."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation = [1.0, 2.0, 3.0]
        scale = [1.0, 1.0, 1.0]
        mat4 = Transform.rts_to_mat4(rotation, translation, scale)
        # Matrix is stored in transposed form, so translation is in last row
        self.assertAlmostEqual(mat4[3, 0], 1.0)
        self.assertAlmostEqual(mat4[3, 1], 2.0)
        self.assertAlmostEqual(mat4[3, 2], 3.0)

    def test_rts_to_mat4_scale(self):
        """Test rts_to_mat4 with scale only."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation = [0.0, 0.0, 0.0]
        scale = [2.0, 3.0, 4.0]
        mat4 = Transform.rts_to_mat4(rotation, translation, scale)
        # Diagonal should reflect scale
        self.assertAlmostEqual(mat4[0, 0], 2.0)
        self.assertAlmostEqual(mat4[1, 1], 3.0)
        self.assertAlmostEqual(mat4[2, 2], 4.0)

    def test_mat4_to_rts_identity(self):
        """Test mat4_to_rts with identity matrix."""
        mat4 = np.identity(4)
        rotation, translation, scale = Transform.mat4_to_rts(mat4)
        np.testing.assert_array_almost_equal(rotation, [0.0, 0.0, 0.0, 1.0])
        np.testing.assert_array_almost_equal(translation, [0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(scale, [1.0, 1.0, 1.0])

    def test_mat4_to_rts_translation(self):
        """Test mat4_to_rts with translation."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation_in = [1.0, 2.0, 3.0]
        scale = [1.0, 1.0, 1.0]
        mat4 = Transform.rts_to_mat4(rotation, translation_in, scale)
        _, translation_out, _ = Transform.mat4_to_rts(mat4)
        np.testing.assert_array_almost_equal(translation_out, translation_in)

    def test_mat4_to_rts_scale(self):
        """Test mat4_to_rts with scale."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation = [0.0, 0.0, 0.0]
        scale_in = [2.0, 3.0, 4.0]
        mat4 = Transform.rts_to_mat4(rotation, translation, scale_in)
        _, _, scale_out = Transform.mat4_to_rts(mat4)
        np.testing.assert_array_almost_equal(scale_out, scale_in)

    def test_mat4_to_rts_with_reflection(self):
        """Test mat4_to_rts handles reflection (negative determinant)."""
        mat4 = np.identity(4)
        mat4[0, 0] = -1.0  # Reflection in x
        rotation, translation, scale = Transform.mat4_to_rts(mat4)
        # Should handle reflection by negating scale
        self.assertAlmostEqual(scale[0], -1.0)

    def test_from_mat4(self):
        """Test from_mat4 constructor."""
        mat4 = np.identity(4)
        mat4[3, 0] = 1.0  # Matrix is in transposed form
        mat4[3, 1] = 2.0
        mat4[3, 2] = 3.0
        xform = Transform.from_mat4(mat4)
        # Should extract translation
        np.testing.assert_array_almost_equal(xform.translation, [1.0, 2.0, 3.0])

    def test_from_rts(self):
        """Test from_rts constructor."""
        rotation = [0.0, 0.0, 0.0, 1.0]
        translation = [1.0, 2.0, 3.0]
        scale = [2.0, 2.0, 2.0]
        xform = Transform.from_rts(rotation, translation, scale)
        self.assertEqual(xform.rotation, rotation)
        self.assertEqual(xform.translation, translation)
        self.assertEqual(xform.scale, scale)

    def test_to_dict(self):
        """Test to_dict serialization."""
        xform = Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],
            translation=[1.0, 2.0, 3.0],
            scale=[2.0, 2.0, 2.0],
        )
        result = xform.to_dict()
        self.assertIn("rotation", result)
        self.assertIn("translation", result)
        self.assertIn("scale", result)
        self.assertIn("matrix", result)
        self.assertEqual(result["rotation"], [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(result["translation"], [1.0, 2.0, 3.0])
        self.assertEqual(result["scale"], [2.0, 2.0, 2.0])

    def test_from_dict_with_matrix(self):
        """Test from_dict with matrix key."""
        data = {"matrix": np.identity(4).tolist()}
        xform = Transform.from_dict(data)
        np.testing.assert_array_almost_equal(xform.mat4, np.identity(4))

    def test_from_dict_with_rts(self):
        """Test from_dict with rotation, translation, scale keys."""
        data = {
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "translation": [1.0, 2.0, 3.0],
            "scale": [2.0, 2.0, 2.0],
        }
        xform = Transform.from_dict(data)
        self.assertEqual(xform.rotation, [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(xform.translation, [1.0, 2.0, 3.0])
        self.assertEqual(xform.scale, [2.0, 2.0, 2.0])

    def test_roundtrip_rts_to_mat4(self):
        """Test roundtrip conversion between RTS and matrix."""
        rotation = Rotation.from_euler("xyz", [30, 45, 60], degrees=True).as_quat().tolist()
        translation = [1.0, 2.0, 3.0]
        scale = [2.0, 3.0, 4.0]

        # Convert to matrix and back
        mat4 = Transform.rts_to_mat4(rotation, translation, scale)
        r_out, t_out, s_out = Transform.mat4_to_rts(mat4)

        # Should be approximately equal
        np.testing.assert_array_almost_equal(r_out, rotation, decimal=5)
        np.testing.assert_array_almost_equal(t_out, translation, decimal=5)
        np.testing.assert_array_almost_equal(s_out, scale, decimal=5)

    def test_roundtrip_dict(self):
        """Test roundtrip conversion to/from dict."""
        xform = Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],
            translation=[1.0, 2.0, 3.0],
            scale=[2.0, 3.0, 4.0],
        )

        # Convert to dict and back
        data = xform.to_dict()
        xform_restored = Transform.from_dict(data)

        np.testing.assert_array_almost_equal(xform_restored.rotation, xform.rotation)
        np.testing.assert_array_almost_equal(xform_restored.translation, xform.translation)
        np.testing.assert_array_almost_equal(xform_restored.scale, xform.scale)
        np.testing.assert_array_almost_equal(xform_restored.mat4, xform.mat4)


class MockTransformAdapter:
    """Mock adapter for testing format registration."""

    @staticmethod
    def from_format(obj, **kwargs):
        """Mock from_format."""
        return Transform.from_rts(
            rotation=obj.get("rot", [0.0, 0.0, 0.0, 1.0]),
            translation=obj.get("pos", [0.0, 0.0, 0.0]),
            scale=obj.get("scl", [1.0, 1.0, 1.0]),
        )

    @staticmethod
    def to_format(instance, **kwargs):
        """Mock to_format."""
        return {
            "rot": instance.rotation,
            "pos": instance.translation,
            "scl": instance.scale,
        }


class TestTransformAdapters(unittest.TestCase):
    """Test Transform adapter registration and usage."""

    def test_register_adapter(self):
        """Test registering a format adapter."""
        Transform.register_adapter("mock_format", MockTransformAdapter)
        # Should not raise an error

    def test_from_format(self):
        """Test from_format with registered adapter."""
        Transform.register_adapter("mock_format", MockTransformAdapter)
        obj = {"pos": [1.0, 2.0, 3.0], "rot": [0.0, 0.0, 0.0, 1.0], "scl": [2.0, 2.0, 2.0]}
        xform = Transform.from_format("mock_format", obj)
        self.assertEqual(xform.translation, [1.0, 2.0, 3.0])
        self.assertEqual(xform.scale, [2.0, 2.0, 2.0])

    def test_from_format_unregistered(self):
        """Test from_format with unregistered format."""
        with self.assertRaises(ValueError) as cm:
            Transform.from_format("nonexistent_format", {})
        self.assertIn("No adapter registered", str(cm.exception))

    def test_to_format(self):
        """Test to_format with registered adapter."""
        Transform.register_adapter("mock_format", MockTransformAdapter)
        xform = Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],
            translation=[1.0, 2.0, 3.0],
            scale=[2.0, 2.0, 2.0],
        )
        result = xform.to_format("mock_format")
        self.assertEqual(result["pos"], [1.0, 2.0, 3.0])
        self.assertEqual(result["scl"], [2.0, 2.0, 2.0])

    def test_to_format_unregistered(self):
        """Test to_format with unregistered format."""
        xform = Transform()
        with self.assertRaises(ValueError) as cm:
            xform.to_format("nonexistent_format")
        self.assertIn("No adapter registered", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
