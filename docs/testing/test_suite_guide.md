# Test Suite Documentation

## Overview

This document provides comprehensive information about the test suite after Waves 1-5 hardening.

## Test Structure

### Test Categories
- **Unit Tests**: `tests/unit/` - Fast, isolated tests for individual components
- **Integration Tests**: `tests/integration/` - Tests for component interactions
- **Smoke Tests**: `tests/smoke/` - Quick validation of critical paths
- **Architecture Tests**: `tests/architecture/` - System-level validation
- **Enforcement Tests**: `tests/enforcement/` - Policy and rule validation

### Layer Organization
Tests are organized by the same layer structure as the main codebase:
- `L0_routing/` - Routing and navigation tests
- `L1_cognition/` - Cognitive engine tests
- `L2_execution/` - Execution engine tests
- `L3_orchestration/` - Orchestration tests
- `L4_state/` - State management tests
- `L5_safety/` - Safety and validation tests
- `L6_observability/` - Observability tests

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/agentic_core/L0_routing/test_component_util.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=agentic_core --cov-report=html
```

### Test Categories
```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run smoke tests
pytest tests/smoke/

# Run architecture tests
pytest tests/architecture/
```

### Performance Options
```bash
# Run with parallel execution
pytest -n auto

# Run with timeout (default 300s)
pytest --timeout=600

# Stop after first failure
pytest -x

# Run failed tests only
pytest --lf
```

## Test Fixtures and Utilities

### Common Fixtures
- `temp_dir`: Temporary directory for file operations
- `sample_config`: Sample configuration data
- `mock_agent`: Mock agent for testing
- `sample_test_data`: Common test data patterns

### Test Utilities
- `TestDataFactory`: Factory for creating test data
- `assert_file_exists()`: File existence assertions
- `assert_mock_called()`: Mock call validation
- `create_test_scenario()`: Test scenario creation

## Test Quality Standards

### Constitutional Rules
1. **No Test Skipping**: All tests must run, no skip markers
2. **No Silent Failures**: Proper exception handling with pytest.raises
3. **Behavioral Assertions**: All tests must have meaningful assertions
4. **Quality Standards**: No debug prints, proper logging only

### Test Naming
- Use descriptive test names: `test_function_behavior_expected_result`
- Group related tests in classes
- Use docstrings for complex test scenarios

### Test Structure
```python
def test_component_functionality():
    """Test that component performs expected functionality."""
    # Arrange
    setup_data = create_test_data()

    # Act
    result = component.process(setup_data)

    # Assert
    assert result.status == "success"
    assert result.data is not None
```

## History

### Waves 1-5 Hardening
- **Wave 1**: Inventory and classification
- **Wave 2**: Constitutional violation fixes
- **Wave 3**: Hollowed test restoration
- **Wave 4**: Guardian swallow conversion
- **Wave 5**: Quality improvements

### Key Improvements
- Eliminated 32 ImportErrors
- Restored 354 hollowed tests
- Converted 70+ guardian swallows
- Replaced 158 print statements
- Created comprehensive test infrastructure

---

For more information, see the wave reports in `docs/reports/plans/`.
