"""
Trimesh Visualization Demo - CORRECTED VERSION
-----------------------------------------------
This example demonstrates how to visualize SISSF scenes using trimesh.

Features:
- Visualize architecture (walls, floors, ceilings)
- Visualize model instances as bounding boxes
- Interactive 3D viewer
- Export to various formats (glb, obj, etc.)
"""

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

# Add the project root to sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sissf import Architecture, ModelInstance, SceneState
from sissf.geometry import Point3D


def create_wall_mesh(wall, color=[0.8, 0.8, 0.8, 0.9]):
    """Create a trimesh box for a wall."""
    if len(wall.points) < 2:
        return None

    p1, p2 = wall.points[0], wall.points[1]

    # Calculate wall dimensions
    width = np.sqrt((p2.x - p1.x) ** 2 + (p2.z - p1.z) ** 2)

    # Calculate wall angle (rotation around Y axis)
    angle = np.arctan2(p2.z - p1.z, p2.x - p1.x)

    # Calculate wall center position AFTER considering rotation
    # The wall center should be at the midpoint between p1 and p2
    center_x = (p1.x + p2.x) / 2
    center_y = p1.y + wall.height / 2
    center_z = (p1.z + p2.z) / 2

    # Create box at origin first
    box = trimesh.creation.box(extents=[width, wall.height, wall.depth])

    # Apply transformations in correct order:
    # 1. Rotate around Y axis at origin
    rotation = trimesh.transformations.rotation_matrix(angle, [0, 1, 0])
    box.apply_transform(rotation)

    # 2. Then translate to final position
    translation = trimesh.transformations.translation_matrix(
        [center_x, center_y, center_z]
    )
    box.apply_transform(translation)

    box.visual.vertex_colors = color  # type: ignore
    return box


def create_floor_mesh(floor, color=[0.6, 0.5, 0.4, 1.0]):
    """Create a trimesh mesh for a floor from polygon points."""
    if len(floor.points) < 3:
        return None

    # Extract 2D points (X, Z plane)
    points_2d = np.array([[p.x, p.z] for p in floor.points])
    base_y = floor.points[0].y

    # Create top surface (at base_y)
    vertices_top = np.column_stack(
        [points_2d[:, 0], np.full(len(points_2d), base_y), points_2d[:, 1]]
    )

    # Create bottom surface (depth goes DOWN, so subtract depth from y)
    vertices_bottom = np.column_stack(
        [
            points_2d[:, 0],
            np.full(len(points_2d), base_y - floor.depth),
            points_2d[:, 1],
        ]
    )

    # Create simple triangulation (fan triangulation from first vertex)
    n = len(points_2d)
    faces = []

    # Top face (counter-clockwise when viewed from above)
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])

    # Bottom face (clockwise when viewed from above, i.e., counter-clockwise from below)
    for i in range(1, n - 1):
        faces.append([0 + n, i + 1 + n, i + n])

    # Side faces (connect top and bottom)
    for i in range(n):
        next_i = (i + 1) % n
        # Two triangles per side
        faces.append([i, next_i, next_i + n])
        faces.append([i, next_i + n, i + n])

    vertices = np.vstack([vertices_top, vertices_bottom])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.visual.vertex_colors = color  # type: ignore

    return mesh


def create_ceiling_mesh(ceiling, color=[0.9, 0.9, 0.9, 0.8]):
    """Create a trimesh mesh for a ceiling (similar to floor but depth goes UP)."""
    if len(ceiling.points) < 3:
        return None

    # Extract 2D points (X, Z plane)
    points_2d = np.array([[p.x, p.z] for p in ceiling.points])
    base_y = ceiling.points[0].y

    # Create bottom surface (at base_y)
    vertices_bottom = np.column_stack(
        [points_2d[:, 0], np.full(len(points_2d), base_y), points_2d[:, 1]]
    )

    # Create top surface (depth goes UP, so add depth to y)
    vertices_top = np.column_stack(
        [
            points_2d[:, 0],
            np.full(len(points_2d), base_y + ceiling.depth),
            points_2d[:, 1],
        ]
    )

    # Create simple triangulation
    n = len(points_2d)
    faces = []

    # Bottom face (clockwise when viewed from below, i.e., counter-clockwise from above)
    for i in range(1, n - 1):
        faces.append([0, i + 1, i])

    # Top face (counter-clockwise when viewed from below)
    for i in range(1, n - 1):
        faces.append([0 + n, i + n, i + 1 + n])

    # Side faces
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, next_i + n])
        faces.append([i, next_i + n, i + n])

    vertices = np.vstack([vertices_bottom, vertices_top])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.visual.vertex_colors = color  # type: ignore

    return mesh


def create_model_instance_mesh(
    instance, bbox_size=[0.5, 0.5, 0.5], color=[0.2, 0.6, 0.8, 0.7]
):
    """Create a bounding box representation for a model instance."""
    # Create a box at origin
    box = trimesh.creation.box(extents=bbox_size)

    # Apply the instance's transform
    transform_matrix = instance.transform.mat4.T  # Transpose back to standard form
    box.apply_transform(transform_matrix)

    box.visual.vertex_colors = color  # type: ignore
    return box


def visualize_scene(scene_state: SceneState, show_architecture=True, show_objects=True):
    """
    Visualize a SceneState using trimesh.

    Args:
        scene_state: The SceneState to visualize
        show_architecture: Whether to show walls, floors, ceilings
        show_objects: Whether to show model instances
    """
    meshes = []

    # Visualize architecture
    if show_architecture and scene_state.architecture:
        arch = scene_state.architecture

        # Add walls
        for wall in arch.walls.values():
            wall_mesh = create_wall_mesh(wall, color=[0.85, 0.85, 0.85, 0.9])
            if wall_mesh:
                meshes.append(wall_mesh)

        # Add floors
        for floor in arch.floors.values():
            floor_mesh = create_floor_mesh(floor, color=[0.6, 0.5, 0.4, 1.0])
            if floor_mesh:
                meshes.append(floor_mesh)

        # Add ceilings
        for ceiling in arch.ceilings.values():
            ceiling_mesh = create_ceiling_mesh(ceiling, color=[0.95, 0.95, 0.95, 0.8])
            if ceiling_mesh:
                meshes.append(ceiling_mesh)

    # Visualize model instances as bounding boxes
    if show_objects:
        for instance in scene_state.objects:
            # Color-code by asset source
            color_map = {
                "holodeck": [0.2, 0.6, 0.8, 0.7],
                "objaverse": [0.8, 0.4, 0.2, 0.7],
                "ai2thor": [0.2, 0.8, 0.4, 0.7],
            }
            color = color_map.get(instance.asset_source, [0.5, 0.5, 0.5, 0.7])

            bbox_mesh = create_model_instance_mesh(instance, color=color)
            if bbox_mesh:
                meshes.append(bbox_mesh)

    # Combine all meshes
    if not meshes:
        print("No geometry to visualize!")
        return None

    scene = trimesh.Scene(meshes)

    # Add coordinate frame for reference
    axis = trimesh.creation.axis(origin_size=0.05, axis_radius=0.01, axis_length=1.0)
    scene.add_geometry(axis)

    return scene


def main(add_ceiling: bool = True):
    """Main demo function."""

    # Example 1: Create a simple scene programmatically
    print("Creating example scene...")

    scene = SceneState(id="demo-scene")

    # Create simple architecture
    arch = Architecture(id="demo-arch")

    # Create a simple room (5m x 4m, 2.5m high)
    from sissf.architecture.architecture import (
        ArchCeiling,
        ArchFloor,
        ArchRoom,
        ArchWall,
    )

    room = ArchRoom(id="living_room")
    arch.add_room(room)

    # Add walls
    wall_height = 2.5
    wall_depth = 0.1

    walls = [
        ArchWall(
            id="wall_north",
            points=[Point3D(0, 0, 0), Point3D(5, 0, 0)],
            height=wall_height,
            depth=wall_depth,
            room_id="living_room",
        ),
        # ArchWall(
        #     id="wall_east",
        #     points=[Point3D(5, 0, 0), Point3D(5, 0, 4)],
        #     height=wall_height,
        #     depth=wall_depth,
        #     room_id="living_room",
        # ),
        # ArchWall(
        #     id="wall_south",
        #     points=[Point3D(5, 0, 4), Point3D(0, 0, 4)],
        #     height=wall_height,
        #     depth=wall_depth,
        #     room_id="living_room",
        # ),
        ArchWall(
            id="wall_west",
            points=[Point3D(0, 0, 4), Point3D(0, 0, 0)],
            height=wall_height,
            depth=wall_depth,
            room_id="living_room",
        ),
    ]

    for wall in walls:
        arch.add_wall(wall)

    # Add floor
    floor = ArchFloor(
        id="floor_living_room",
        points=[Point3D(0, 0, 0), Point3D(5, 0, 0), Point3D(5, 0, 4), Point3D(0, 0, 4)],
        depth=0.1,
        room_id="living_room",
    )
    arch.add_floor(floor)

    # Add ceiling
    if add_ceiling:
        ceiling = ArchCeiling(
            id="ceiling_living_room",
            points=[
                Point3D(0, wall_height, 0),
                Point3D(5, wall_height, 0),
                Point3D(5, wall_height, 4),
                Point3D(0, wall_height, 4),
            ],
            depth=0.1,
            room_id="living_room",
        )
        arch.add_ceiling(ceiling)

    scene.architecture = arch

    # Add some model instances
    from sissf.geometry import Transform

    # Sofa (back wall)
    sofa = ModelInstance(
        id="sofa-0",
        model_id="holodeck.sofa_example",
        transform=Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],  # No rotation
            translation=[2.5, 0.3, 3.5],  # Center-back of room
            scale=[4, 0.6, 1.6],
        ),
        parent_id="floor_living_room",
    )
    scene.add_instance(sofa)

    # Backrest
    backrest = ModelInstance(
        id="backrest",
        model_id="holodeck.backrest_cushion_example",
        transform=Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],
            translation=[2.5, 0.55, 3.75],
            scale=[3.6, 0.3, 0.4],  # Cushion proportions
        ),
        parent_id="sofa-0",
    )
    scene.add_instance(backrest)

    # Coffee table (center)
    table = ModelInstance(
        id="table-0",
        model_id="holodeck.table_example",
        transform=Transform.from_rts(
            rotation=[0.0, 0.0, 0.0, 1.0],
            translation=[2.5, 0.3, 2.0],
            scale=[1.0, 0.6, 0.6],
        ),
        parent_id="floor_living_room",
    )
    scene.add_instance(table)

    # TV Stand (front wall)
    tv = ModelInstance(
        id="tv-0",
        model_id="objaverse.tv_example",
        transform=Transform.from_rts(
            rotation=[0.0, 1.0, 0.0, 0.0],  # 180 degree rotation around Y
            translation=[2.5, 0.7, 0.2],
            scale=[2.0, 1.2, 0.15],
        ),
        parent_id="floor_living_room",
    )
    scene.add_instance(tv)

    # Save the scene
    output_dir = Path(__file__).parent
    scene_file = output_dir / "demo_scene.json"

    with open(scene_file, "w") as f:
        json.dump(scene.to_dict(), f, indent=2)

    print(f"Scene saved to: {scene_file}")

    # Visualize the scene
    print("\nVisualizing scene with trimesh...")
    trimesh_scene = visualize_scene(scene)

    if trimesh_scene:
        # Show interactive viewer
        print("Opening interactive viewer...")
        print("  - Left click + drag: Rotate")
        print("  - Right click + drag: Pan")
        print("  - Scroll: Zoom")
        print("  - Press 'q' to quit")
        trimesh_scene.show()

        # Optionally export to file
        export_file = output_dir / "demo_scene.glb"
        trimesh_scene.export(export_file)
        print(f"\nScene exported to: {export_file}")


if __name__ == "__main__":
    ADD_CEILING = False

    main(add_ceiling=ADD_CEILING)
