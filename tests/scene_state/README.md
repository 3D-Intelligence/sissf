# Scene State Tests

This directory contains tests for the `sissf.scene_state` module.
# Tests - `sissf.scene_state`

## Instructions:

```bash
# Run all scene_state tests
python -m pytest tests/scene_state/ -v

# Run specific test file
python -m pytest tests/scene_state/test_scene_state.py -v

# Run with coverage (requires pytest-cov: pip install pytest-cov)
python -m pytest tests/scene_state/ --cov=sissf.scene_state --cov-report=term-missing

# Alternative: Run tests with built-in Python coverage
python -m coverage run -m pytest tests/scene_state/
python -m coverage report -m --include="sissf/scene_state/*"