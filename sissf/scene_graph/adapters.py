"""
adapters.py
---
Format adapters for converting between sissf scene graphs and other formats.

These adapters demonstrate how to convert between sissf's scene graph format
and other common formats. Users can implement their own adapters following
the same pattern.
"""

from typing import Any, Dict

from .relationship import Relationship
from .scene_graph import SceneGraph
from .scene_object import SceneObject


class VisualGenomeAdapter:
    """
    Adapter for Visual Genome scene graph format.

    Visual Genome typically uses more descriptive formats with nested structures.
    This adapter provides basic compatibility with VG-style scene graphs.
    """

    @staticmethod
    def from_format(data: Dict[str, Any], **kwargs) -> SceneGraph:
        """Convert from Visual Genome format to sissf SceneGraph."""
        sg = SceneGraph(metadata={"source_format": "visual_genome"})

        # VG objects may have different field names
        obj_id_map = {}
        for obj_data in data.get("objects", []):
            obj_id = str(obj_data.get("id", obj_data.get("object_id")))
            obj = SceneObject(
                id=obj_id,
                name=obj_data.get("name", obj_data.get("names", [""])[0]),
                attributes=obj_data.get("attributes", []),
            )
            sg.add_object(obj)
            obj_id_map[int(obj_id)] = obj.id

        # VG relationships
        for rel_data in data.get("relationships", []):
            subject_id = rel_data.get("subject_id", rel_data.get("subject", {}).get("object_id"))
            target_id = rel_data.get("target_id", rel_data.get("object", {}).get("object_id"))

            if subject_id in obj_id_map and target_id in obj_id_map:
                rel = Relationship(
                    id=str(rel_data.get("relationship_id", len(sg.relationships))),
                    type=rel_data.get("predicate", rel_data.get("type", "")),
                    subject_id=obj_id_map[subject_id],
                    target_id=obj_id_map[target_id],
                )
                sg.add_relationship(rel)

        return sg

    @staticmethod
    def to_format(sg: SceneGraph, **kwargs) -> Dict[str, Any]:
        """Convert sissf SceneGraph to Visual Genome format."""
        obj_id_to_int = {obj_id: i for i, obj_id in enumerate(sg.objects.keys())}

        return {
            "objects": [
                {
                    "object_id": obj_id_to_int[obj.id],
                    "names": [obj.name],
                    "attributes": obj.attributes,
                }
                for obj in sg.objects.values()
            ],
            "relationships": [
                {
                    "relationship_id": i,
                    "predicate": rel.type,
                    "subject": {"object_id": obj_id_to_int[rel.subject_id]},
                    "object": {"object_id": obj_id_to_int[rel.target_id]},
                }
                for i, rel in enumerate(sg.relationships)
            ],
        }


# Register adapters
SceneGraph.register_adapter("visual_genome", VisualGenomeAdapter)