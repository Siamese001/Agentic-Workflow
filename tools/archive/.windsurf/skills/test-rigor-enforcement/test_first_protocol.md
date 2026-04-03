# Test-First Protocol

**Enforces §1.2: Tests MUST exist before logic changes are committed.**

## Protocol

### Step 1: Write Tests BEFORE Logic

For each changed surface identified in `pre_code_generation_gate.md`:

1. Create test file if it doesn't exist
2. Write ALL required tests (edge cases, determinism, fail-closed)
3. Tests should FAIL initially (no implementation yet)
4. Verify tests are deterministic (§1.3)

**Order:**
```
1. Write test_edge_cases_*
2. Write test_determinism_*
3. Write test_fail_closed_*
4. Write test_state_transitions_* (if applicable)
5. Run tests → ALL SHOULD FAIL (no implementation)
6. ONLY THEN write implementation
```

### Step 2: Verify Test Determinism (§1.3)

Each test MUST be deterministic:

**Checklist:**
- [ ] No `random.random()` without fixed seed
- [ ] No `datetime.now()` without injected timestamp
- [ ] No external API calls without mocks
- [ ] No filesystem reads without fixtures
- [ ] No database queries without test database
- [ ] No environment variables without explicit injection

**If system under test uses randomness:**
```python
import random

def test_deterministic_with_seed():
    random.seed(42)  # Fix seed
    result = function_using_random()
    assert result == expected_value
```

**If system under test uses time:**
```python
from unittest.mock import patch
from datetime import datetime

def test_deterministic_with_time():
    fixed_time = datetime(2026, 3, 9, 12, 0, 0)
    with patch('module.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        result = function_using_time()
        assert result == expected_value
```

### Step 3: Verify Edge Case Coverage (§1.5)

Each changed surface MUST test:

**Mandatory edge cases:**
```python
def test_null_input():
    """§1.5: null/None input"""
    assert function(None) raises ValueError

def test_empty_input():
    """§1.5: empty input"""
    assert function({}) raises ValueError

def test_malformed_structure():
    """§1.5: malformed structure"""
    assert function({"wrong_key": "value"}) raises ValueError

def test_boundary_values():
    """§1.5: boundary values"""
    assert function({"score": 0}) == min_value
    assert function({"score": 100}) == max_value

def test_unauthorized_input():
    """§1.5: unauthorized input"""
    assert function({"role": "guest"}) raises PermissionError

def test_stale_state():
    """§1.5: stale state"""
    # Test with expired timestamp, outdated version, etc.

def test_dependency_failure():
    """§1.5: dependency failure"""
    with patch('module.dependency', side_effect=Exception):
        assert function(valid_input) raises DependencyError

def test_negative_control_path():
    """§1.5: negative control path"""
    assert function(invalid_input) == False

def test_recovery_path():
    """§1.5: recovery path"""
    # Test retry logic, fallback behavior, etc.
```

### Step 4: Verify Fail-Closed (§1.8)

For side-effect surfaces (writes, mutations, external calls):

```python
def test_invalid_preconditions_block_operation():
    """§1.8: invalid preconditions block operation"""
    with pytest.raises(ValidationError):
        mutate_state(invalid_input)

    # Verify no side-effects occurred
    assert state_unchanged()

def test_no_side_effects_before_block():
    """§1.8: no side-effects occur before block"""
    initial_state = capture_state()

    with pytest.raises(ValidationError):
        function_with_side_effects(invalid_input)

    final_state = capture_state()
    assert initial_state == final_state  # No partial writes
```

### Step 5: Run Tests (Should Fail)

```bash
pytest tests/test_new_module.py -v
```

**Expected output:**
```
test_null_input FAILED
test_empty_input FAILED
test_malformed_structure FAILED
...
18 failed in 0.5s
```

**If tests PASS before implementation:**
- Tests are not testing the right thing
- Tests are too permissive
- STOP and fix tests

### Step 6: Implement Logic

ONLY after all tests are written and failing:

1. Write minimal implementation to pass first test
2. Run tests → verify one test passes
3. Iterate until all tests pass
4. Refactor if needed (tests should still pass)

### Step 7: Verify All Tests Pass

```bash
pytest tests/test_new_module.py -v
```

**Expected output:**
```
test_null_input PASSED
test_empty_input PASSED
test_malformed_structure PASSED
...
18 passed in 0.5s
```

## Enforcement

```
IF tests_written_first AND tests_are_deterministic AND edge_cases_covered:
    ALLOW implementation
ELSE:
    BLOCK implementation
    REQUIRE test-first discipline
```

## Constitutional References

- **§1.2:** Tests MUST exist before logic changes are committed
- **§1.3:** Tests MUST be deterministic
- **§1.4:** No mocks for integration seams (use real integration)
- **§1.5:** Every changed surface MUST include edge case tests
- **§1.8:** Tests MUST prove invalid preconditions block operation
- **§1.10:** Tests MUST target the real entrypoint or enforcement choke point
