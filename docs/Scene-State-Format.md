# Scene-State Format

The scene-state format specifies the set of 3D model assets used in the scene together with their transforms.

## Overview

The scene-state format is designed to be a lightweight, standardized representation of scenes that:
- Uses quaternion rotations for accurate, gimbal-lock-free transformations
- Supports parent-child hierarchies for object relationships
- Can embed or reference architecture data
- Maintains compatibility with multiple asset sources (Objaverse, AI2-THOR, etc.)

## Format Structure

The scene-state file has four top-level sections:

```json
{
  "format": "sceneState",
  "scene": { ... },       // Object instances and metadata
  "arch": { ... },        // Architecture (optional, can be ref or embedded)
  "scene_graph": { ... }  // Scene graph (optional, semantic relationships)
}
```

## Scene Section

The `scene` section contains metadata and object instances:

```json
{
  "scene": {
    "id": "unique-scene-id",
    "version": "scene@0.0.1",
    "up": { "x": 0.0, "y": 1.0, "z": 0.0 },
    "front": { "x": 0.0, "y": 0.0, "z": -1.0 },
    "unit": 1.0,
    "asset_source": ["Holodeck", "Objaverse", "AI2-THOR"],
    "objects": [...],
    "cameras": [...],
    "selected": [],
    "metadata": {}
  }
}
```

### Scene Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the scene |
| `version` | string | Scene format version (e.g., "scene@0.0.1") |
| `up` | Point3D | Up vector (typically {x:0, y:1, z:0} for Y-up) |
| `front` | Point3D | Front vector (typically {x:0, y:0, z:-1}) |
| `unit` | number | Scale to meters (1.0 = meters, 0.0254 = inches) |
| `asset_source` | string[] | List of asset sources used in scene |
| `objects` | ModelInstance[] | Array of object instances |
| `cameras` | Camera[] | Optional list of camera definitions |
| `selected` | string[] | Optional list of selected object IDs |
| `metadata` | object | Optional metadata for the entire scene |

## Object Instances (ModelInstance)

Each object in the scene is represented as a `ModelInstance`:

```json
{
  "id": "sofa-0 (living room)",
  "type": "ModelInstance",
  "model_id": "holodeck.b0e8d0249d6f43c7981ec15bc859fc2e",
  "transform": {
    "rotation": [0.0, 1.0, 0.0, 6.123233995736766e-17],
    "translation": [3.6, 0.3694220084309739, 5.519237989975812],
    "scale": [1.0, 1.0, 1.0],
    "matrix": [...]
  },
  "parent_id": "floor_living room",
  "asset_file_location": null,
  "metadata": {"kinematic": true}
}
```

### ModelInstance Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this object instance |
| `type` | string | Yes | Always "ModelInstance" |
| `model_id` | string | Yes | Asset reference in format `source.asset_id` |
| `transform` | Transform | Yes | Spatial transformation (see below) |
| `parent_id` | string | No | ID of parent object or architectural element |
| `asset_file_location` | string | No | Optional path to asset file (local/remote storage location) |
| `metadata` | object | No | Additional metadata (kinematic, etc.) |

### Model ID Format

The `model_id` field uses a standardized format: `source.asset_id`

Examples:
- `holodeck.b0e8d0249d6f43c7981ec15bc859fc2e` - Holodeck asset
- `objaverse.abc123def456` - Objaverse asset
- `ai2thor.Sofa_1` - AI2-THOR asset

This is automatically converted from holodeck's format:
- `Objaverse_abc123` → `objaverse.abc123`
- `ThorObject_Sofa_1` → `ai2thor.Sofa_1`
- `other_asset` → `holodeck.other_asset`

### Transform

The transform contains both explicit rotation/translation/scale vectors and a 4x4 transformation matrix:

```json
{
  "rotation": [x, y, z, w],        // Quaternion (x, y, z, w)
  "translation": [x, y, z],        // Position in meters
  "scale": [x, y, z],              // Scale factors
  "matrix": [...]                  // 4x4 matrix in column-major order
}
```

**Important:**
- **Rotation** is a quaternion in **[x, y, z, w]** order (not w, x, y, z)
- **Matrix** is in **column-major** order (16 elements)
- The matrix is computed from rotation, translation, and scale

### Parent ID Hierarchy

The `parent_id` field establishes hierarchical relationships:

| Object Type | Parent ID Pattern | Example |
|-------------|------------------|---------|
| Floor objects | `floor_{room_id}` | `floor_living room` |
| Ceiling objects | `ceiling_{room_id}` | `ceiling_bedroom` |
| Wall objects | Wall ID from architecture | `wall\|living room\|north\|0` |
| Small objects | Receptacle object ID | `coffee_table-0 (living room)` |

This enables:
- Scene graph traversal
- Spatial queries (e.g., "all objects on floor_living room")
- Grouping and selection
- Physics simulation hierarchies

## Architecture Section

The architecture can be embedded or referenced. See [Architecture-Format.md](Architecture-Format.md) for details.

### Embedded Architecture

```json
{
  "arch": {
    "id": "unique-arch-id",
    "version": "arch@0.0.1",
    "up": [0.0, 1.0, 0.0],
    "front": [0.0, 0.0, -1.0],
    "scale_to_meters": 1.0,
    "defaults": {...},
    "rooms": [...],
    "walls": [...],
    "floors": [...],
    "ceilings": [...]
  }
}
```

### Referenced Architecture

```json
{
  "arch": {
    "ref": "architecture-id-or-path"
  }
}
```

## Scene Graph Section

The scene graph can optionally be embedded to capture semantic and spatial relationships between objects. See [Scene-Graph-Format.md](Scene-Graph-Format.md) for details.

### Embedded Scene Graph

```json
{
  "scene_graph": {
    "unique-graph-id": {
      "id": "unique-graph-id",
      "room_type": "living room",
      "objects": [
        {
          "id": "0",
          "name": "sofa",
          "attributes": ["floor", "furniture"],
          "description": "A comfortable three-seat sofa",
          "metadata": {}
        },
        {
          "id": "1",
          "name": "pillow",
          "attributes": ["small", "soft"],
          "description": "A decorative throw pillow",
          "metadata": {}
        }
      ],
      "relationships": [
        {
          "id": "0",
          "type": "on",
          "subject_id": "1",
          "target_id": "0",
          "metadata": {}
        }
      ],
      "metadata": {}
    }
  }
}
```

**Key Points:**
- The scene graph is **optional** and complements the scene state
- Scene graph objects can reference model instances through matching names/IDs
- Relationships capture semantic connections (e.g., "on", "near", "inside")
- Can be used for spatial reasoning, object queries, and scene understanding
- The scene graph provides a higher-level semantic layer over the geometric scene state

## Complete Example

```json
{
  "format": "sceneState",
  "scene": {
    "id": "51e2f26f-5853-0eb4-d02a-d922433aaf42",
    "version": "scene@0.0.1",
    "up": { "x": 0.0, "y": 1.0, "z": 0.0 },
    "front": { "x": 0.0, "y": 0.0, "z": -1.0 },
    "unit": 1.0,
    "asset_source": ["Holodeck"],
    "objects": [
      {
        "id": "sofa-0 (living room)",
        "type": "ModelInstance",
        "model_id": "holodeck.b0e8d0249d6f43c7981ec15bc859fc2e",
        "transform": {
          "rotation": [0.0, 1.0, 0.0, 6.123233995736766e-17],
          "translation": [3.6, 0.3694220084309739, 5.519237989975812],
          "scale": [1.0, 1.0, 1.0],
          "matrix": [
            -1.0, 0.0, -1.2246467991473532e-16, 0.0,
            0.0, 1.0, 0.0, 0.0,
            1.2246467991473532e-16, 0.0, -1.0, 0.0,
            3.6, 0.3694220084309739, 5.519237989975812, 1.0
          ]
        },
        "parent_id": "floor_living room",
        "asset_file_location": null,
        "metadata": {
          "roomId": "living room",
          "kinematic": true
        }
      },
      {
        "id": "coffee_table-0 (living room)",
        "type": "ModelInstance",
        "model_id": "holodeck.TV_Stand_201_1",
        "transform": {
          "rotation": [0.0, 1.0, 0.0, 6.123233995736766e-17],
          "translation": [1.8, 0.3578382730484009, 5.665925468206406],
          "scale": [1.0, 1.0, 1.0],
          "matrix": [...]
        },
        "parent_id": "floor_living room",
        "asset_file_location": null,
        "metadata": {"kinematic": true}
      }
    ],
    "cameras": [],
    "selected": [],
    "metadata": {}
  },
  "arch": {
    "ref": "architecture.json"
  },
  "scene_graph": {
    "51e2f26f-5853-0eb4-d02a-d922433aaf42-graph": {
      "id": "51e2f26f-5853-0eb4-d02a-d922433aaf42-graph",
      "room_type": "living room",
      "objects": [
        {
          "id": "0",
          "name": "sofa",
          "attributes": ["floor", "furniture", "seating"],
          "description": "A comfortable three-seat sofa",
          "metadata": {
            "model_instance_id": "sofa-0 (living room)"
          }
        },
        {
          "id": "1",
          "name": "coffee table",
          "attributes": ["floor", "furniture", "table"],
          "description": "A coffee table in front of the sofa",
          "metadata": {
            "model_instance_id": "coffee_table-0 (living room)"
          }
        }
      ],
      "relationships": [
        {
          "id": "0",
          "type": "near",
          "subject_id": "1",
          "target_id": "0",
          "metadata": {}
        }
      ],
      "metadata": {}
    }
  }
}
```

## Coordinate System

- **Y-up**: Vertical axis points upward
- **Z-forward**: Forward/front direction (scene uses Z=-1 as front)
- **Right-handed**: Cross(X, Y) = Z
- **Units**: Meters (configurable via `unit` field)
