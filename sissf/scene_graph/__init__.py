"""
Scene graph module for sissf.

This module provides a flexible scene graph representation for semantic and spatial
scene understanding, supporting various text-to-3D scene generation pipelines.
"""

from .relationship import Relationship, RelationshipAdapter, _RELATIONSHIP_ADAPTERS
from .scene_graph import SceneGraph, SceneGraphAdapter, SceneGraphValidationError, _SCENE_GRAPH_ADAPTERS
from .scene_object import SceneObject, SceneObjectAdapter, _SCENE_OBJECT_ADAPTERS

# Import adapters to register them
from . import adapters

__all__ = [
    # Scene Object
    "_SCENE_OBJECT_ADAPTERS",
    "SceneObject",
    "SceneObjectAdapter",
    # Relationship
    "_RELATIONSHIP_ADAPTERS",
    "Relationship",
    "RelationshipAdapter",
    # Scene Graph
    "_SCENE_GRAPH_ADAPTERS",
    "SceneGraph",
    "SceneGraphAdapter",
    "SceneGraphValidationError",
]
