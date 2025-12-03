"""
Scene Graph Example
---
Demonstrates how to use the sissf scene graph format for semantic scene understanding.

The scene graph format provides an intermediate representation for text-to-3D scene
generation pipelines, enabling LLMs to define semantic and spatial constraints that
can be solved downstream.
"""

import json

from sissf import Relationship, SceneGraph, SceneObject


def example_1_basic_scene_graph():
    """Example 1: Creating a basic scene graph from scratch."""
    print("=" * 80)
    print("Example 1: Creating a Basic Scene Graph")
    print("=" * 80)

    # Create a scene graph for a bedroom
    sg = SceneGraph(room_type="bedroom")

    # Add objects
    bed = SceneObject(id="0", name="bed", attributes=["double", "wooden"])
    nightstand_left = SceneObject(id="1", name="nightstand", attributes=["small"])
    nightstand_right = SceneObject(id="2", name="nightstand", attributes=["small"])
    lamp = SceneObject(id="3", name="lamp", attributes=["table"])

    sg.add_object(bed)
    sg.add_object(nightstand_left)
    sg.add_object(nightstand_right)
    sg.add_object(lamp)

    # Add spatial relationships
    rel1 = Relationship(
        id="0", type="left of", subject_id="1", target_id="0"  # nightstand left of bed
    )
    rel2 = Relationship(
        id="1",
        type="right of",
        subject_id="2",  # nightstand right of bed
        target_id="0",
    )
    rel3 = Relationship(
        id="2", type="on", subject_id="3", target_id="1"  # lamp on nightstand
    )

    sg.add_relationship(rel1)
    sg.add_relationship(rel2)
    sg.add_relationship(rel3)

    # Validate the scene graph
    try:
        sg.validate()
        print(f"✓ Scene graph is valid")
    except Exception as e:
        print(f"✗ Validation failed: {e}")

    print(f"\n{sg}")
    print(f"\nObjects:")
    for obj in sg.objects.values():
        print(f"  - {obj}")
    print(f"\nRelationships:")
    for rel in sg.relationships:
        print(f"  - {rel}")

    return sg


def example_2_scene_graph_queries():
    """Example 2: Querying a scene graph."""
    print("\n" + "=" * 80)
    print("Example 2: Querying Scene Graph")
    print("=" * 80)

    # Create a scene graph
    sg = SceneGraph(room_type="living room")

    sofa = SceneObject(id="0", name="sofa", attributes=["large", "leather"])
    coffee_table = SceneObject(id="1", name="coffee_table", attributes=["glass"])
    tv_stand = SceneObject(id="2", name="tv_stand", attributes=["wooden"])
    tv = SceneObject(id="3", name="tv", attributes=["flat_screen"])

    sg.add_object(sofa)
    sg.add_object(coffee_table)
    sg.add_object(tv_stand)
    sg.add_object(tv)

    sg.add_relationship(
        Relationship(id="0", type="in front of", subject_id="1", target_id="0")
    )
    sg.add_relationship(
        Relationship(id="1", type="facing", subject_id="2", target_id="0")
    )
    sg.add_relationship(Relationship(id="2", type="on", subject_id="3", target_id="2"))

    # Query relationships for an object
    print(f"\nRelationships involving coffee_table (id=1):")
    rels = sg.get_relationships_for_object("1")
    for rel in rels:
        print(f"  - {rel}")

    # Get objects related to the sofa
    print(f"\nObjects related to sofa (id=0):")
    related = sg.get_related_objects("0")
    for obj in related:
        print(f"  - {obj}")

    # Get objects with specific relationship
    print(f"\nObjects 'on' tv_stand (id=2):")
    on_tv_stand = sg.get_related_objects("2", relationship_type="on")
    for obj in on_tv_stand:
        print(f"  - {obj}")


def example_3_serialization():
    """Example 3: Serializing and deserializing scene graphs."""
    print("\n" + "=" * 80)
    print("Example 3: Serialization and Deserialization")
    print("=" * 80)

    # Create a simple scene graph
    sg = SceneGraph(room_type="kitchen")

    table = SceneObject(id="0", name="dining_table", attributes=["wooden", "rectangular"])
    chair1 = SceneObject(id="1", name="chair", attributes=["wooden"])
    chair2 = SceneObject(id="2", name="chair", attributes=["wooden"])

    sg.add_object(table)
    sg.add_object(chair1)
    sg.add_object(chair2)

    sg.add_relationship(Relationship(id="0", type="around", subject_id="1", target_id="0"))
    sg.add_relationship(Relationship(id="1", type="around", subject_id="2", target_id="0"))

    # Convert to dictionary
    sg_dict = sg.to_dict()
    print("\nScene graph as dictionary:")
    print(json.dumps(sg_dict, indent=2))

    # Recreate from dictionary
    sg_reconstructed = SceneGraph.from_dict(sg_dict)
    print(f"\nReconstructed: {sg_reconstructed}")

    # Verify they're equivalent
    assert sg.room_type == sg_reconstructed.room_type
    assert sg.num_objects == sg_reconstructed.num_objects
    assert sg.num_relationships == sg_reconstructed.num_relationships
    print("✓ Serialization round-trip successful")


def example_4_adapters():
    """Example 4: Using format adapters."""
    print("\n" + "=" * 80)
    print("Example 4: Format Adapters")
    print("=" * 80)

    # Create a scene graph in sissf format
    sg = SceneGraph(room_type="bedroom")
    sg.add_object(SceneObject(id="0", name="bed", attributes=["large"]))
    sg.add_object(SceneObject(id="1", name="desk", attributes=["wooden"]))
    sg.add_relationship(
        Relationship(id="0", type="next to", subject_id="1", target_id="0")
    )

    print("\nOriginal sissf format:")
    print(json.dumps(sg.to_dict(), indent=2))

    # Convert to Visual Genome format
    vg_format = sg.to_format("visual_genome")
    print("\nConverted to Visual Genome format:")
    print(json.dumps(vg_format, indent=2))

    # Convert back from Visual Genome format
    sg_from_vg = SceneGraph.from_format("visual_genome", vg_format)
    print(f"\nRecreated from VG format: {sg_from_vg}")
    print("✓ Format conversion successful")


def example_5_building_from_llm_output():
    """Example 5: Building a scene graph from LLM output (typical use case)."""
    print("\n" + "=" * 80)
    print("Example 5: Building Scene Graph from LLM Output")
    print("=" * 80)

    # Simulated LLM output (this is what you'd get from an LLM scene parser)
    llm_output = {
        "room_type": "home_office",
        "objects": [
            {"id": "0", "name": "desk", "attributes": ["large", "L-shaped"]},
            {"id": "1", "name": "office_chair", "attributes": ["ergonomic", "black"]},
            {"id": "2", "name": "bookshelf", "attributes": ["tall", "wooden"]},
            {"id": "3", "name": "monitor", "attributes": ["curved", "ultrawide"]},
            {"id": "4", "name": "keyboard", "attributes": ["mechanical"]},
        ],
        "relationships": [
            {"id": "0", "type": "on", "subject_id": "3", "target_id": "0"},
            {"id": "1", "type": "on", "subject_id": "4", "target_id": "0"},
            {"id": "2", "type": "in front of", "subject_id": "1", "target_id": "0"},
            {"id": "3", "type": "behind", "subject_id": "2", "target_id": "0"},
        ],
    }

    # Parse into sissf scene graph
    sg = SceneGraph.from_dict(llm_output)

    print(f"\nParsed scene graph: {sg}")
    print(f"\nValidating...")

    # Validate with constraints (e.g., for a specific downstream method)
    allowed_objects = [
        "desk",
        "office_chair",
        "bookshelf",
        "monitor",
        "keyboard",
        "filing_cabinet",
    ]
    allowed_relationships = [
        "on",
        "in front of",
        "behind",
        "left of",
        "right of",
        "above",
        "below",
    ]

    try:
        sg.validate(allowed_objects=allowed_objects, allowed_relationships=allowed_relationships)
        print("✓ Scene graph is valid for downstream processing")
    except Exception as e:
        print(f"✗ Validation failed: {e}")

    # Access scene graph data for downstream processing
    print(f"\nScene graph contains:")
    print(f"  - {sg.num_objects} objects")
    print(f"  - {sg.num_relationships} relationships")

    # Example: Convert to format expected by a layout generator
    print(f"\nReady for layout generation...")


def example_6_modifying_scene_graphs():
    """Example 6: Modifying scene graphs (adding/removing objects and relationships)."""
    print("\n" + "=" * 80)
    print("Example 6: Modifying Scene Graphs")
    print("=" * 80)

    # Start with a basic scene
    sg = SceneGraph(room_type="bedroom")
    bed = SceneObject(id="0", name="bed", attributes=["queen"])
    nightstand = SceneObject(id="1", name="nightstand", attributes=[])

    sg.add_object(bed)
    sg.add_object(nightstand)
    sg.add_relationship(Relationship(id="0", type="left of", subject_id="1", target_id="0"))

    print(f"Initial: {sg}")

    # Add more furniture
    dresser = SceneObject(id="2", name="dresser", attributes=["large"])
    sg.add_object(dresser)
    sg.add_relationship(
        Relationship(id="1", type="facing", subject_id="2", target_id="0")
    )
    print(f"\nAfter adding dresser: {sg}")

    # Modify object attributes
    bed.add_attribute("wooden")
    bed.add_attribute("upholstered")
    print(f"\nBed attributes: {bed.attributes}")

    # Remove an object (also removes related relationships)
    removed = sg.remove_object("1")
    print(f"\nRemoved {removed}")
    print(f"Scene graph now: {sg}")
    print(f"Remaining relationships: {len(sg.relationships)}")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_scene_graph()
    example_2_scene_graph_queries()
    example_3_serialization()
    example_4_adapters()
    example_5_building_from_llm_output()
    example_6_modifying_scene_graphs()

    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
