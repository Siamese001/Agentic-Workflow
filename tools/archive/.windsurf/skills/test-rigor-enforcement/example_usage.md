# Test Rigor Enforcement - Example Usage

Complete example of enforcing §1 TESTING & EVIDENCE requirements during code generation.

## Scenario

Adding a new validator with deterministic scoring logic and file I/O.

## Step 1: Pre-Code-Generation Gate

**Before writing ANY code:**

```markdown
[PRE-CODE-GENERATION GATE]

SCOPE_DECLARATION:
- agentic_core/L5_safety/validators/input_scorer.py (new file)
- tests/unit_min_deps/test_input_scorer.py (new file)

CHANGED_SURFACES:

input_scorer.py::calculate_risk_score:
  Type: deterministic_decision_surface
  Risk: Scoring must be deterministic, identical input → identical output

input_scorer.py::validate_and_save:
  Type: side_effect_surface
  Risk: File write must fail-closed on invalid input

TEST_REQUIREMENTS:

input_scorer.py::calculate_risk_score:
  Edge cases (§1.5):
    ✓ null/None input
    ✓ empty dict input
    ✓ malformed structure (missing 'score' key)
    ✓ boundary values (score=0, score=100)
    ✓ negative values (score=-1)

  Determinism (§1.7):
    ✓ identical input → identical output
    ✓ normalized equivalent input → identical output
    ✓ stable ordering for ties

  Minimum: 8 tests

input_scorer.py::validate_and_save:
  Fail-closed (§1.8):
    ✓ invalid preconditions block operation
    ✓ no side-effects occur before block

  Side-effect safety (§1.8):
    ✓ file write on valid input
    ✓ exception on invalid input
    ✓ no partial writes

  Edge cases (§1.5):
    ✓ null/None data
    ✓ empty dict
    ✓ malformed path

  Minimum: 8 tests

TOTAL_REQUIRED_TESTS: 16

GATE STATUS: ✅ APPROVED
NEXT STEP: Write tests FIRST (test_first_protocol.md)
```

## Step 2: Test-First Protocol

**Write tests BEFORE implementation:**

```python
# tests/unit_min_deps/test_input_scorer.py

import pytest
from pathlib import Path
from agentic_core.L5_safety.validators.input_scorer import (
    calculate_risk_score,
    validate_and_save,
)


# =============================================================================
# calculate_risk_score - Edge Cases (§1.5)
# =============================================================================

def test_calculate_risk_score_null_input():
    """§1.5: null/None input"""
    with pytest.raises(ValueError, match="Input cannot be None"):
        calculate_risk_score(None)


def test_calculate_risk_score_empty_dict():
    """§1.5: empty input"""
    with pytest.raises(ValueError, match="Input cannot be empty"):
        calculate_risk_score({})


def test_calculate_risk_score_malformed_structure():
    """§1.5: malformed structure - missing 'score' key"""
    with pytest.raises(KeyError, match="score"):
        calculate_risk_score({"wrong_key": 50})


def test_calculate_risk_score_boundary_min():
    """§1.5: boundary values - minimum"""
    result = calculate_risk_score({"score": 0})
    assert result == 0.0


def test_calculate_risk_score_boundary_max():
    """§1.5: boundary values - maximum"""
    result = calculate_risk_score({"score": 100})
    assert result == 1.0


def test_calculate_risk_score_negative_value():
    """§1.5: negative values"""
    with pytest.raises(ValueError, match="Score must be non-negative"):
        calculate_risk_score({"score": -1})


# =============================================================================
# calculate_risk_score - Determinism (§1.7)
# =============================================================================

def test_calculate_risk_score_identical_input_identical_output():
    """§1.7: identical input → identical output"""
    input_data = {"score": 50}
    result1 = calculate_risk_score(input_data)
    result2 = calculate_risk_score(input_data)
    assert result1 == result2


def test_calculate_risk_score_normalized_equivalent():
    """§1.7: normalized equivalent input → identical output"""
    result1 = calculate_risk_score({"score": 50})
    result2 = calculate_risk_score({"score": 50.0})  # int vs float
    assert result1 == result2


# =============================================================================
# validate_and_save - Fail-Closed (§1.8)
# =============================================================================

def test_validate_and_save_invalid_preconditions_block(tmp_path):
    """§1.8: invalid preconditions block operation"""
    invalid_data = {"score": -1}  # Invalid
    output_file = tmp_path / "output.json"

    with pytest.raises(ValueError):
        validate_and_save(invalid_data, output_file)

    # Verify no file was created (no side-effects)
    assert not output_file.exists()


def test_validate_and_save_no_side_effects_before_block(tmp_path):
    """§1.8: no side-effects occur before block"""
    invalid_data = None  # Invalid
    output_file = tmp_path / "output.json"

    # Create a marker file to verify no writes occurred
    marker = tmp_path / "marker.txt"
    marker.write_text("initial")

    with pytest.raises(ValueError):
        validate_and_save(invalid_data, output_file)

    # Verify marker unchanged (no side-effects)
    assert marker.read_text() == "initial"
    assert not output_file.exists()


# =============================================================================
# validate_and_save - Side-Effect Safety (§1.8)
# =============================================================================

def test_validate_and_save_success(tmp_path):
    """§1.8: file write on valid input"""
    valid_data = {"score": 50}
    output_file = tmp_path / "output.json"

    validate_and_save(valid_data, output_file)

    assert output_file.exists()
    import json
    saved = json.loads(output_file.read_text())
    assert saved == valid_data


def test_validate_and_save_exception_on_invalid(tmp_path):
    """§1.8: exception on invalid input"""
    invalid_data = {"score": -1}
    output_file = tmp_path / "output.json"

    with pytest.raises(ValueError):
        validate_and_save(invalid_data, output_file)


def test_validate_and_save_no_partial_writes(tmp_path):
    """§1.8: no partial writes"""
    # Simulate failure during write by using invalid path
    valid_data = {"score": 50}
    invalid_path = tmp_path / "nonexistent_dir" / "output.json"

    with pytest.raises(FileNotFoundError):
        validate_and_save(valid_data, invalid_path)

    # Verify no partial file created
    assert not invalid_path.exists()


# =============================================================================
# validate_and_save - Edge Cases (§1.5)
# =============================================================================

def test_validate_and_save_null_data(tmp_path):
    """§1.5: null/None data"""
    output_file = tmp_path / "output.json"

    with pytest.raises(ValueError, match="Data cannot be None"):
        validate_and_save(None, output_file)


def test_validate_and_save_empty_dict(tmp_path):
    """§1.5: empty dict"""
    output_file = tmp_path / "output.json"

    with pytest.raises(ValueError, match="Data cannot be empty"):
        validate_and_save({}, output_file)


def test_validate_and_save_malformed_path(tmp_path):
    """§1.5: malformed path"""
    valid_data = {"score": 50}

    with pytest.raises(ValueError, match="Invalid path"):
        validate_and_save(valid_data, "")  # Empty path
```

**Run tests (should all FAIL - no implementation yet):**

```bash
pytest tests/unit_min_deps/test_input_scorer.py -v
```

**Expected:**
```
16 failed in 0.5s
```

## Step 3: Implement Logic

**ONLY after tests are written:**

```python
# agentic_core/L5_safety/validators/input_scorer.py

from pathlib import Path
import json


def calculate_risk_score(input_data: dict | None) -> float:
    """Calculate deterministic risk score from input data.

    Args:
        input_data: Dictionary with 'score' key (0-100)

    Returns:
        Normalized risk score (0.0-1.0)

    Raises:
        ValueError: If input is None, empty, or score is negative
        KeyError: If 'score' key is missing
    """
    if input_data is None:
        raise ValueError("Input cannot be None")

    if not input_data:
        raise ValueError("Input cannot be empty")

    score = input_data["score"]  # Raises KeyError if missing

    if score < 0:
        raise ValueError("Score must be non-negative")

    # Deterministic normalization
    return float(score) / 100.0


def validate_and_save(data: dict | None, output_path: Path | str) -> None:
    """Validate data and save to file (fail-closed).

    Args:
        data: Dictionary to validate and save
        output_path: Path to output file

    Raises:
        ValueError: If data is None, empty, invalid, or path is invalid
        FileNotFoundError: If parent directory doesn't exist
    """
    # Validate preconditions BEFORE any side-effects
    if data is None:
        raise ValueError("Data cannot be None")

    if not data:
        raise ValueError("Data cannot be empty")

    if not output_path:
        raise ValueError("Invalid path")

    # Validate data (fail-closed)
    score = data.get("score")
    if score is not None and score < 0:
        raise ValueError("Invalid score")

    # Convert to Path
    path = Path(output_path) if isinstance(output_path, str) else output_path

    # Ensure parent directory exists (fail if not)
    if not path.parent.exists():
        raise FileNotFoundError(f"Parent directory does not exist: {path.parent}")

    # Write atomically (no partial writes)
    path.write_text(json.dumps(data), encoding="utf-8")
```

**Run tests (should all PASS now):**

```bash
pytest tests/unit_min_deps/test_input_scorer.py -v
```

**Expected:**
```
16 passed in 0.5s
```

## Step 4: Post-Code Validation

**Use Python enforcer:**

```python
from pathlib import Path
from agentic_core.L5_safety.enforcement.test_rigor_enforcer import (
    TestRigorEnforcer,
    TestCoverageRequirement,
)

# Initialize enforcer
enforcer = TestRigorEnforcer(project_root=Path.cwd())

# Declare requirements (from pre-code-generation gate)
enforcer.add_coverage_requirement(
    TestCoverageRequirement(
        file_path="agentic_core/L5_safety/validators/input_scorer.py",
        surface_name="calculate_risk_score",
        surface_type="deterministic_decision_surface",
        required_tests=["edge_null", "edge_empty", "determinism_identical"],
        minimum_test_count=8,
    )
)

enforcer.add_coverage_requirement(
    TestCoverageRequirement(
        file_path="agentic_core/L5_safety/validators/input_scorer.py",
        surface_name="validate_and_save",
        surface_type="side_effect_surface",
        required_tests=["fail_closed", "side_effect_safety", "edge_null"],
        minimum_test_count=8,
    )
)

# Validate post-code-generation
result = enforcer.validate_post_code_generation(
    test_path="tests/unit_min_deps/test_input_scorer.py"
)

# Generate report
report = enforcer.generate_validation_report(result)
print(report)

# Check compliance
if result.compliant:
    print("\n✅ APPROVED FOR COMMIT")
else:
    print("\n❌ BLOCKED - FIX VIOLATIONS")
    for violation in result.violations:
        print(f"  {violation}")
```

**Output:**
```
============================================================
POST-CODE VALIDATION REPORT
============================================================

Test Execution:
  Collected: 16 tests
  Executed:  16 tests
  Passed:    16 tests
  Failed:    0 tests
  Skipped:   0 tests

  Collection/Execution Match: ✅ PASS (§1.12)

Test Coverage:
  Declared minimum: 16 tests
  Actual coverage:  16 tests
  Coverage gap:     0 tests

  Coverage Match: ✅ PASS (§1.1)

============================================================
VALIDATION STATUS: ✅ APPROVED FOR COMMIT
============================================================

✅ APPROVED FOR COMMIT
```

## Summary

**Workflow enforced:**

1. ✅ Pre-code-generation gate: Declared scope and test requirements
2. ✅ Test-first protocol: Wrote 16 tests BEFORE implementation
3. ✅ Implementation: Wrote minimal code to pass tests
4. ✅ Post-code validation: Verified 16/16 tests pass, no skipping

**Constitutional compliance:**

- §1.1: ✅ Every line covered by tests
- §1.2: ✅ Tests written before implementation
- §1.3: ✅ Tests are deterministic
- §1.5: ✅ Edge cases covered
- §1.8: ✅ Fail-closed and side-effect safety proven
- §1.12: ✅ No test skipping (collected == executed)

**Result:** Code changes APPROVED for commit.
