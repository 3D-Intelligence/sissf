# Scene-Graph Format

The scene-graph format represents semantic and spatial relationships between objects in a scene, serving as an intermediate representation in text-to-3D scene generation pipelines.

## Overview

The scene-graph format is designed to:
- Represent semantic structure of scenes independent of 3D geometry
- Enable LLMs to define spatial and functional constraints
- Support downstream layout generation and constraint solving
- Maintain compatibility with multiple scene graph vocabularies
- Provide a flexible intermediate step between text and 3D scenes

## Format Structure

Scene graphs can be embedded in other formats or stored separately. The structure is:

```json
{
  "id": "unique-scene-graph-id",
  "room_type": "bedroom",
  "objects": [...],
  "relationships": [...],
  "metadata": {}
}
```

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for this scene graph |
| `room_type` | string | Optional room type (e.g., "bedroom", "kitchen") |
| `objects` | SceneObject[] | Array of object nodes in the scene graph |
| `relationships` | Relationship[] | Array of relationship edges between objects |
| `metadata` | object | Optional metadata for the entire scene graph |

## Scene Objects

Each object in the scene graph is a semantic node representing an entity (furniture, fixture, etc.):

```json
{
  "id": "0",
  "name": "bed",
  "attributes": ["double", "wooden"],
  "description": "A large wooden bed",
  "embedding": null,
  "metadata": {}
}
```

### SceneObject Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this object |
| `name` | string | Yes | Object category/class name (e.g., "chair", "table") |
| `attributes` | string[] | Yes | Semantic attributes describing the object |
| `description` | string | No | Optional natural language description |
| `embedding` | number[] | No | Optional feature embedding for ML pipelines |
| `metadata` | object | No | Additional metadata for the object |

### Attributes

Attributes provide additional semantic information:

```json
{
  "id": "0",
  "name": "chair",
  "attributes": ["wooden", "armchair", "brown"]
}
```

## Relationships

Relationships are directed edges connecting two objects:

```json
{
  "id": "0",
  "type": "left of",
  "subject_id": "1",
  "target_id": "0",
  "confidence": 0.95,
  "embedding": null,
  "metadata": {}
}
```

### Relationship Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this relationship |
| `type` | string | Yes | Relationship type (see below) |
| `subject_id` | string | Yes | ID of the subject object |
| `target_id` | string | Yes | ID of the target object |
| `confidence` | number | No | Optional confidence score (0.0-1.0) |
| `embedding` | number[] | No | Optional feature embedding for ML pipelines |
| `metadata` | object | No | Additional metadata for the relationship |

### Relationship Direction

Relationships are **directed** from subject to target:

```json
{
  "type": "left of",
  "subject_id": "nightstand",  // The nightstand...
  "target_id": "bed"            // ...is left of the bed
}
```

Reading direction: `{subject} {type} {target}`
- Example: `nightstand left of bed`

### Common Relationship Types

#### Spatial - Horizontal

| Type | Description | Example |
|------|-------------|---------|
| `left of` | Subject is to the left of target | `nightstand left of bed` |
| `right of` | Subject is to the right of target | `lamp right of chair` |
| `closely left of` | Subject is immediately adjacent on the left | `chair closely left of table` |
| `closely right of` | Subject is immediately adjacent on the right | `monitor closely right of keyboard` |

#### Spatial - Depth

| Type | Description | Example |
|------|-------------|---------|
| `in front of` | Subject is in front of target (viewer perspective) | `coffee_table in front of sofa` |
| `behind` | Subject is behind target | `bookshelf behind desk` |
| `closely in front of` | Subject is immediately in front | `ottoman closely in front of armchair` |
| `closely behind` | Subject is immediately behind | `console_table closely behind sofa` |

#### Spatial - Vertical

| Type | Description | Example |
|------|-------------|---------|
| `above` | Subject is above target | `painting above fireplace` |
| `below` | Subject is below target | `rug below table` |
| `on` | Subject is resting on target surface | `lamp on nightstand` |
| `under` | Subject is underneath target | `storage_box under bed` |

#### Spatial - Containment

| Type | Description | Example |
|------|-------------|---------|
| `in` | Subject is inside target | `clothes in wardrobe` |
| `inside` | Subject is contained within target | `books inside bookshelf` |
| `contains` | Subject contains target (inverse of `in`) | `wardrobe contains clothes` |

#### Spatial - Proximity

| Type | Description | Example |
|------|-------------|---------|
| `next to` | Subject is adjacent to target | `nightstand next to bed` |
| `near` | Subject is close to target | `floor_lamp near reading_chair` |
| `around` | Subject is positioned around target | `chairs around dining_table` |
| `facing` | Subject is oriented toward target | `tv_stand facing sofa` |

#### Functional

| Type | Description | Example |
|------|-------------|---------|
| `supports` | Subject physically supports target | `desk supports monitor` |
| `attached to` | Subject is attached to target | `wall_lamp attached to wall` |
| `part of` | Subject is a component of target | `drawer part of dresser` |
| `aligned with` | Subject is aligned with target | `nightstands aligned with bed` |

### Reflexive Relationships

For bidirectional constraints, include both directions:

```json
[
  {
    "type": "left of",
    "subject_id": "chair_1",
    "target_id": "table"
  },
  {
    "type": "right of",
    "subject_id": "table",
    "target_id": "chair_1"
  }
]
```

Common reflexive pairs:
- `left of` ↔ `right of`
- `in front of` ↔ `behind`
- `above` ↔ `below`
- `in` ↔ `contains`

## Complete Example

```json
{
  "id": "sg-bedroom-001",
  "room_type": "bedroom",
  "objects": [
    {
      "id": "0",
      "name": "bed",
      "attributes": ["double", "wooden"],
      "description": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "1",
      "name": "nightstand",
      "attributes": ["small", "wooden"],
      "description": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "2",
      "name": "nightstand",
      "attributes": ["small", "wooden"],
      "description": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "3",
      "name": "lamp",
      "attributes": ["table"],
      "description": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "4",
      "name": "dresser",
      "attributes": ["large", "wooden"],
      "description": null,
      "embedding": null,
      "metadata": {}
    }
  ],
  "relationships": [
    {
      "id": "0",
      "type": "left of",
      "subject_id": "1",
      "target_id": "0",
      "confidence": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "1",
      "type": "right of",
      "subject_id": "2",
      "target_id": "0",
      "confidence": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "2",
      "type": "on",
      "subject_id": "3",
      "target_id": "1",
      "confidence": null,
      "embedding": null,
      "metadata": {}
    },
    {
      "id": "3",
      "type": "facing",
      "subject_id": "4",
      "target_id": "0",
      "confidence": null,
      "embedding": null,
      "metadata": {}
    }
  ],
  "metadata": {
    "source": "llm_parser",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```
