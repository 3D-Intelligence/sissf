# Architecture Format

The architecture format defines the scene building geometry:
rooms, walls, floors, ceilings, and openings (doors/windows).

## Overview

The architecture format is designed to:
- Represent scene building geometry independent of furniture/objects
- Support parametric openings (doors/windows) on walls
- Enable easy reconstruction of 3D geometry
- Maintain material and room associations

## Format Structure

Architecture can be embedded in scene-state files or stored separately. The structure is:

```json
{
  "id": "unique-architecture-id",            // Ideally a UUID
  "version": "arch@0.0.1",
  "up": {"x": 0.0, "y": 1.0, "z": 0.0},
  "front": {"x": 0.0, "y": 0.0, "z": -1.0},
  "scale_to_meters": 1.0,
  "defaults": {...},
  "rooms": [...],
  "walls": [...],
  "floors": [...],
  "ceilings": [...],
  "metadata": {}
}
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for this architecture (ideally a UUID) |
| `version` | string | Format version (e.g., "arch@0.0.1") |
| `up` | Point3D | Up vector (typically Point3D(0, 1, 0) for Y-up) |
| `front` | Point3D | Front vector (typically Point3D(0, 0, -1)) |
| `scale_to_meters` | number | Conversion factor to meters (1.0 = meters) |
| `defaults` | object | Default values for walls, floors, ceilings |
| `rooms` | Room[] | Array of room definitions |
| `walls` | Wall[] | Array of wall segments |
| `floors` | Floor[] | Array of floor surfaces (legacy) |
| `ceilings` | Ceiling[] | Array of ceiling surfaces (legacy) |
| `metadata` | object | Optional metadata for the entire architecture |

**Note:** In the current implementation, floors and ceilings are embedded within rooms, and the top-level `floors` and `ceilings` arrays are provided for backward compatibility.

### Defaults

Default properties for architectural elements:

```json
{
  "defaults": {
    "Wall": {
      "depth": 0.1,
      "extra_height": 0.035
    },
    "Ceiling": {
      "depth": 0.05
    },
    "Floor": {
      "depth": 0.05
    },
    "Ground": {
      "depth": 0.08
    }
  }
}
```

## Rooms

Rooms contain floors and ceilings and reference their associated walls:

```json
{
  "id": "living room",
  "type": "Room",
  "wall_ids": [],
  "floor": {
    "id": "floor_living room",
    "type": "Floor",
    "points": [
      { "x": 0.0, "y": 0.0, "z": 0.0 },
      { "x": 0.0, "y": 0.0, "z": 6.0 },
      { "x": 6.0, "y": 0.0, "z": 6.0 },
      { "x": 6.0, "y": 0.0, "z": 0.0 }
    ],
    "depth": 0.05,
    "room_id": "living room",
    "material": "DarkWoodSmooth2",
    "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/DarkWoodSmooth2.png",
    "metadata": {}
  },
  "ceiling": {
    "id": "ceiling_living room",
    "type": "Ceiling",
    "points": [
      { "x": 0.0, "y": 2.7, "z": 0.0 },
      { "x": 0.0, "y": 2.7, "z": 6.0 },
      { "x": 6.0, "y": 2.7, "z": 6.0 },
      { "x": 6.0, "y": 2.7, "z": 0.0 }
    ],
    "depth": 0.05,
    "room_id": "living room",
    "material": "Walldrywall4",
    "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4.png",
    "metadata": {}
  },
  "metadata": {}
}
```

### Room Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique room identifier |
| `type` | string | Yes | Always "Room" |
| `wall_ids` | string[] | No | IDs of walls belonging to this room |
| `floor` | Floor | Yes | Floor surface for this room |
| `ceiling` | Ceiling | Yes | Ceiling surface for this room |
| `metadata` | object | No | Optional metadata for the room |

## Walls

Walls are vertical planar segments that can have openings (doors/windows):

```json
{
  "id": "wall|living room|north|0",                 // Holodeck format
  "type": "Wall",
  "points": [
    { "x": 0.0, "y": 0.0, "z": 0.0 },
    { "x": 6.0, "y": 0.0, "z": 0.0 }
  ],
  "height": 2.7,
  "depth": 0.1,                                     // thickness
  "room_id": "living room",
  "material": "Walldrywall4Tiled",
  "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4Tiled.png",
  "openings": [
    {
      "id": "door|wall|living room|north|0|0",      // Holodeck format
      "type": "Door",
      "parent_wall_id": "wall|living room|north|0", // Holodeck format
      "mid": 0.5,
      "width": 0.9,
      "height": 2.0,
      "elevation": 1.0,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

### Wall Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique wall identifier |
| `type` | string | Yes | Always "Wall" |
| `points` | Point3D[2] | Yes | Two endpoints defining the wall segment |
| `height` | number | Yes | Height of the wall in meters |
| `depth` | number | Yes | Thickness of the wall in meters |
| `room_id` | string | No | ID of room this wall belongs to |
| `material` | string | No | Material name for the wall surface |
| `material_file_location` | string | No | Optional path to material file (local/remote storage location) |
| `openings` | Opening[] | No | Array of doors/windows in this wall |
| `metadata` | object | No | Optional metadata for the wall |

**Note:** The wall extends vertically from y=0 to y=height. The two points define the base of the wall.

## Openings (Doors/Windows)

Openings are parametrically defined cutouts in walls:

```json
{
  "id": "window|wall|dining room|north|1|0",     // Holodeck format
  "type": "Window",
  "parent_wall_id": "wall|dining room|north|1",  // Holodeck format
  "mid": 0.5351024638833694,
  "width": 2.3935734748840334,
  "height": 1.177397680282593,
  "elevation": 1.4886988401412964,
  "metadata": {}
}
```

### Opening Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique opening identifier |
| `type` | string | Yes | "Door" or "Window" |
| `parent_wall_id` | string | Yes | ID of wall containing this opening |
| `mid` | number | Yes | Fractional position along wall (0-1) |
| `width` | number | Yes | Width of opening in meters |
| `height` | number | Yes | Height of opening in meters |
| `elevation` | number | Yes | Center elevation from floor in meters |
| `metadata` | object | No | Optional metadata for the opening |

### Opening Parameters

The parametric representation allows openings to be positioned independent of wall length:

- **mid**: Fractional distance (0.0 to 1.0) from wall's first point to second point
  - `0.0` = at first point
  - `0.5` = centered on wall
  - `1.0` = at second point

- **width**: Opening width in meters
  - Extends ±width/2 from the mid position

- **height**: Opening height in meters
  - Extends ±height/2 from the elevation

- **elevation**: Center height of opening from floor (y=0)

### Opening Placement Example

For a wall from (0, 0, 0) to (6, 0, 0) with height 2.7:
- `mid=0.5, width=0.9` → opening from x=2.55 to x=3.45
- `elevation=1.0, height=2.0` → opening from y=0.0 to y=2.0

## Floors

Floor surfaces define walkable areas:

```json
{
  "id": "floor_living room",
  "type": "Floor",
  "points": [
    { "x": 0.0, "y": 0.0, "z": 0.0 },
    { "x": 0.0, "y": 0.0, "z": 6.0 },
    { "x": 6.0, "y": 0.0, "z": 6.0 },
    { "x": 6.0, "y": 0.0, "z": 0.0 }
  ],
  "depth": 0.05,
  "room_id": "living room",
  "material": "DarkWoodSmooth2",
  "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/DarkWoodSmooth2.png",
  "metadata": {}
}
```

### Floor Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique floor identifier (typically `floor_{room_id}`) |
| `type` | string | Yes | Always "Floor" |
| `points` | Point3D[] | Yes | Polygon vertices defining floor boundary |
| `depth` | number | Yes | Thickness of floor in meters |
| `room_id` | string | Yes | ID of room this floor belongs to |
| `material` | string | No | Material name for floor surface |
| `material_file_location` | string | No | Optional path to material file (local/remote storage location) |
| `metadata` | object | No | Optional metadata for the floor |

## Ceilings

Ceiling surfaces define the top of rooms:

```json
{
  "id": "ceiling_living room",
  "type": "Ceiling",
  "points": [
    { "x": 0.0, "y": 2.7, "z": 0.0 },
    { "x": 0.0, "y": 2.7, "z": 6.0 },
    { "x": 6.0, "y": 2.7, "z": 6.0 },
    { "x": 6.0, "y": 2.7, "z": 0.0 }
  ],
  "depth": 0.05,
  "room_id": "living room",
  "material": "Walldrywall4",
  "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4.png",
  "metadata": {}
}
```

### Ceiling Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ceiling identifier (typically `ceiling_{room_id}`) |
| `type` | string | Yes | Always "Ceiling" |
| `points` | Point3D[] | Yes | Polygon vertices defining ceiling boundary |
| `depth` | number | Yes | Thickness of ceiling in meters |
| `room_id` | string | Yes | ID of room this ceiling belongs to |
| `material` | string | No | Material name for ceiling surface |
| `material_file_location` | string | No | Optional path to material file (local/remote storage location) |
| `metadata` | object | No | Optional metadata for the ceiling |

## Complete Example

```json
{
  "id": "51e2f26f-5853-0eb4-d02a-d922433aaf42",
  "version": "arch@0.0.1",
  "up": [0.0, 1.0, 0.0],
  "front": [0.0, 0.0, -1.0],
  "scale_to_meters": 1.0,
  "defaults": {
    "Wall": {
      "depth": 0.1,
      "extra_height": 0.035
    },
    "Ceiling": {
      "depth": 0.05
    },
    "Floor": {
      "depth": 0.05
    }
  },
  "rooms": [
    {
      "id": "living room",
      "type": "Room",
      "wall_ids": [],
      "floor": {
        "id": "floor_living room",
        "type": "Floor",
        "points": [
          { "x": 0.0, "y": 0.0, "z": 0.0 },
          { "x": 0.0, "y": 0.0, "z": 6.0 },
          { "x": 6.0, "y": 0.0, "z": 6.0 },
          { "x": 6.0, "y": 0.0, "z": 0.0 }
        ],
        "depth": 0.05,
        "room_id": "living room",
        "material": "DarkWoodSmooth2",
        "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/DarkWoodSmooth2.png",
        "metadata": {}
      },
      "ceiling": {
        "id": "ceiling_living room",
        "type": "Ceiling",
        "points": [
          { "x": 0.0, "y": 2.7, "z": 0.0 },
          { "x": 0.0, "y": 2.7, "z": 6.0 },
          { "x": 6.0, "y": 2.7, "z": 6.0 },
          { "x": 6.0, "y": 2.7, "z": 0.0 }
        ],
        "depth": 0.05,
        "room_id": "living room",
        "material": "Walldrywall4",
        "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4.png",
        "metadata": {}
      }
    }
  ],
  "walls": [
    {
      "id": "wall|living room|north|0",
      "type": "Wall",
      "points": [
        { "x": 0.0, "y": 0.0, "z": 0.0 },
        { "x": 6.0, "y": 0.0, "z": 0.0 }
      ],
      "height": 2.7,
      "depth": 0.1,
      "room_id": "living room",
      "material": "Walldrywall4Tiled",
      "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4Tiled.png",
      "openings": [
        {
          "id": "door|wall|living room|north|0|0",
          "type": "Door",
          "parent_wall_id": "wall|living room|north|0",
          "mid": 0.5,
          "width": 0.9,
          "height": 2.0,
          "elevation": 1.0
        }
      ],
      "metadata": {}
    },
    {
      "id": "wall|living room|west|0",
      "type": "Wall",
      "points": [
        { "x": 0.0, "y": 0.0, "z": 0.0 },
        { "x": 0.0, "y": 0.0, "z": 6.0 }
      ],
      "height": 2.7,
      "depth": 0.1,
      "room_id": "living room",
      "material": "Walldrywall4Tiled",
      "material_file_location": "https://huggingface.co/datasets/yunusskeete/holodeck-base-data/resolve/main/base_data/materials/images/Walldrywall4Tiled.png",
      "openings": [
        {
          "id": "window|wall|living room|west|0|0",
          "type": "Window",
          "parent_wall_id": "wall|living room|west|0",
          "mid": 0.5,
          "width": 1.5,
          "height": 1.2,
          "elevation": 1.5
        }
      ],
      "metadata": {}
    }
  ],
  "floors": [],
  "ceilings": []
}
```

## Coordinate System

- **Y-up**: Vertical axis points upward
- **Z-forward**: Forward/front direction
- **Right-handed**: Cross(X, Y) = Z
- **Units**: Meters (configurable via `scale_to_meters`)

## Usage in Scene-State

Architecture can be embedded or referenced in scene-state files:

### Embedded
```json
{
  "format": "sceneState",
  "scene": {...},
  "arch": {
    "id": "...",
    "version": "arch@0.0.1",
    "rooms": [...],
    "walls": [...]
  }
}
```

### Referenced
```json
{
  "format": "sceneState",
  "scene": {...},
  "arch": {
    "ref": "architecture.json"
  }
}
```
