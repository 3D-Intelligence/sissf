# SISSF

Spatial Intelligence Scene State Format:
- A platform-agnostic, human and machine readable 3D scene representation standard ([wiki](https://github.com/3D-Intelligence/sissf/wiki)).
- A Python library for working with the Spatial Intelligence Scene State Format ([`pip install sissf`](https://pypi.org/project/sissf/)).

## Features

- Parse and generate scene-state files with 3D model instances and transforms
- Support for architecture definitions (rooms, walls, floors, ceilings)
- Scene graph representation for semantic and spatial relationships
- Quaternion-based rotations for accurate transformations
- Compatible with Holodeck, Objaverse, and AI2-THOR asset sources
- Geometry utilities for 3D bounding boxes, points, and transforms

## Installation

### From pypi Package
[sissf](https://pypi.org/project/sissf/)
```bash
# https://pypi.org/project/sissf/
pip install sissf
```

### From Local Repository
```bash
pip install -e .

# Or install with visualization support
pip install -e ".[viz]"

# Install all optional dependencies (dev tools, visualization, examples)
pip install -e ".[all]"
```

### Requirements

- Python >= 3.10
- numpy >= 1.24.0
- scipy >= 1.10.0

## Examples

- [visualize_scene.py](examples/visualize_scene.py) - Complete Python script for trimesh visualization
- [visualize_scene.ipynb](examples/visualize_scene.ipynb) - Interactive Jupyter notebook walkthrough
- [visualize_scene.ipynb](https://colab.research.google.com/drive/15xrKb_lNUeQ1HE_-Q5NgiWH6IGH3fdIL) - Interactive Google colab walkthrough
- [scene_graph_example.py](examples/scene_graph_example.py) - Scene graph creation, querying, and format conversion

## Documentation

- [Scene State Format](docs/Scene-State-Format.md) - 3D model instances and transforms
- [Architecture Format](docs/Architecture-Format.md) - Building geometry (rooms, walls, floors, ceilings)
- [Scene Graph Format](docs/Scene-Graph-Format.md) - Semantic and spatial relationships between objects

## Acknowledgements

- [smartscenes libsg](https://github.com/smartscenes/libsg)
- [smartscenes sstk](https://github.com/smartscenes/sstk/wiki/Architecture-Format)