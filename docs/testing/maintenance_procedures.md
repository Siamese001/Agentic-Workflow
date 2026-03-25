# Test Suite Maintenance Procedures

## Overview

This document outlines procedures for maintaining and updating the test suite after Waves 1-5 hardening.

## Daily Maintenance

### Pre-Commit Checklist
1. Run syntax validation:
   ```bash
   python tools/wave6a_test_suite_validator.py
   ```

2. Run affected tests:
   ```bash
   pytest tests/path/to/affected/tests/ -v
   ```

3. Check for new issues:
   ```bash
   pytest --collect-only --quiet
   ```

4. Verify no regressions:
   ```bash
   pytest tests/smoke/ -v
   ```

### Post-Merge Validation
1. Full test suite validation:
   ```bash
   python tools/wave6a_test_suite_validator.py
   ```

2. Coverage check:
   ```bash
   pytest --cov=agentic_core --cov-report=term-missing
   ```

3. Performance check:
   ```bash
   pytest --durations=10
   ```

## Weekly Maintenance

### Test Suite Health Check
```bash
# Run comprehensive validation
python tools/wave6a_test_suite_validator.py

# Check for new quality issues
python tools/wave5a_test_quality_analyzer.py

# Generate coverage report
pytest --cov=agentic_core --cov-report=html
```

### Performance Monitoring
```bash
# Identify slow tests
pytest --durations=20

# Check test collection time
pytest --collect-only --quiet --tb=no
```

## Adding New Tests

### Test Creation Process
1. Determine appropriate test category and layer
2. Create test file following naming conventions
3. Use appropriate fixtures from `conftest_factories.py`
4. Write comprehensive test with Arrange-Act-Assert pattern
5. Add meaningful assertions and documentation
6. Run local validation
7. Submit for review

### Test Template
```python
"""Tests for [component_name]."""

import pytest
from tests.conftest_factories import *

class Test[ComponentName]:
    """Test suite for [ComponentName]."""

    def test_functionality_basic(self):
        """Test basic functionality."""
        # Arrange
        test_data = TestDataFactory.create_test_scenario("basic")

        # Act
        result = component.process(test_data)

        # Assert
        assert result.status == "success"
        assert result.data is not None

    def test_error_handling(self):
        """Test error handling scenarios."""
        # Arrange
        invalid_data = TestDataFactory.create_test_scenario("invalid")

        # Act & Assert
        with pytest.raises(ValueError):
            component.process(invalid_data)
```

## Quality Gates

### Pre-Merge Requirements
- All syntax errors: 0
- All import errors: 0
- Test collection: 100% success
- Smoke tests: 100% pass
- Coverage: No regression

### Release Requirements
- Full test suite: 100% pass
- Coverage: >80% target
- Performance: No regression
- Documentation: Updated

## Tools and Utilities

### Validation Tools
- `wave6a_test_suite_validator.py`: Comprehensive validation
- `wave5a_test_quality_analyzer.py`: Quality analysis
- `pytest`: Test execution

### Monitoring Tools
- Coverage reports: HTML and XML
- Performance metrics: pytest durations
- Quality metrics: Custom analyzers

---

Last updated: 2026-03-25
Version: 1.0 (Post-Waves 1-5)
