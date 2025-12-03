from sissf import (
    ArchCeiling,
    ArchFloor,
    Architecture,
    ArchRoom,
    ArchWall,
    ModelInstance,
    SceneState,
)
from sissf.geometry import Point3D, Transform


def generate_example_architecture() -> Architecture:
    arch: Architecture = Architecture(id="demo-arch")

    ################################################################
    # Add room
    ################################################################
    room: ArchRoom = generate_example_room(arch)
    arch.add_room(room)

    print(f"Created room: {room.id}")

    ################################################################
    # Add walls
    ################################################################
    walls: list[ArchWall] = generate_example_wall(arch)
    for wall in walls:
        arch.add_wall(wall)

    print(f"Added {len(walls)} walls")

    ################################################################
    # Add floor and ceiling
    ################################################################
    # Add floor
    floor: ArchFloor = generate_example_floor(arch)
    arch.add_floor(floor)

    add_ceiling = False

    if add_ceiling:
        # Add ceiling
        ceiling: ArchCeiling = generate_example_ceiling(arch)
        arch.add_ceiling(ceiling)

    print(f"✓ Floor{' and ceiling' if add_ceiling else ''} added")

    print(f"Created architecture: {arch.id}")

    return arch


def generate_example_room(arch: Architecture) -> ArchRoom:
    return ArchRoom(id="living_room")


def generate_example_wall(
    arch: Architecture, wall_height: float = 2.5, wall_depth: float = 0.1
) -> list[ArchWall]:
    return [
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


def generate_example_floor(arch: Architecture) -> ArchFloor:
    return ArchFloor(
        id="floor_living_room",
        points=[Point3D(0, 0, 0), Point3D(5, 0, 0), Point3D(5, 0, 4), Point3D(0, 0, 4)],
        depth=0.1,
        room_id="living_room",
    )


def generate_example_ceiling(
    arch: Architecture, wall_height: float = 2.5
) -> ArchCeiling:
    return ArchCeiling(
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


def add_example_objects(scene: SceneState) -> SceneState:
    ################################################################
    # Add furniture
    ################################################################
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

    print(f"✓ Added {len(scene.objects)} objects")
    for obj in scene.objects:
        print(f"  - {obj.id} ({obj.asset_source})")

    return scene


def generate_example_scene() -> SceneState:
    # Initialize scene
    scene = SceneState(id="demo-scene")
    print(f"Created scene: {scene.id}")

    # Create architecture
    arch: Architecture = generate_example_architecture()

    # Link architecture to scene
    scene.architecture = arch

    # Add objects
    scene = add_example_objects(scene)

    return scene
