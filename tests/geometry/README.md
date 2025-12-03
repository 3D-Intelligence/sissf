# Tests - `sissf.geometry`

## Instructions:

```bash
# Run all geometry tests
python -m pytest tests/geometry/ -v

# Run specific test file
python -m pytest tests/geometry/test_point.py -v

# Run with coverage (requires pytest-cov: pip install pytest-cov)
python -m pytest tests/geometry/ --cov=sissf.geometry --cov-report=term-missing

# Alternative: Run tests with built-in Python coverage
python -m coverage run -m pytest tests/geometry/
python -m coverage report -m --include="sissf/geometry/*"
```