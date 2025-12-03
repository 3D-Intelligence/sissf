# Tests - `sissf.scene_graph`

## Instructions:

```bash
# Run all scene_graph tests
python -m pytest tests/scene_graph/ -v

# Run specific test file
python -m pytest tests/scene_graph/test_scene_graph.py -v

# Run with coverage (requires pytest-cov: pip install pytest-cov)
python -m pytest tests/scene_graph/ --cov=sissf.scene_graph --cov-report=term-missing

# Alternative: Run tests with built-in Python coverage
python -m coverage run -m pytest tests/scene_graph/
python -m coverage report -m --include="sissf/scene_graph/*"
```
