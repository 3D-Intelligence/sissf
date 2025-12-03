# Tests - `sissf.architecture`

## Instructions:

```bash
# Run all architecture tests
python -m pytest tests/architecture/ -v

# Run specific test file
python -m pytest tests/architecture/test_architecture.py -v

# Run with coverage (requires pytest-cov: pip install pytest-cov)
python -m pytest tests/architecture/ --cov=sissf.architecture --cov-report=term-missing

# Alternative: Run tests with built-in Python coverage
python -m coverage run -m pytest tests/architecture/
python -m coverage report -m --include="sissf/architecture/*"
```
