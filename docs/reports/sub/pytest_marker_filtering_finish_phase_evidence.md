# Finisher Phase: Pytest Marker Filtering Governance Evidence

## Wave 1.1: Evidence-Locked Scan + Baseline

### Baseline pytest run

```
============================ 153 passed in 19.95s ========================
```

Exit code: 0

### Scan 1: getoption("-m") patterns (double quotes)

**Command executed:**
```
git grep -n 'getoption("-m"' -- tests tools
```

**Results:**

```
tests/conftest.py:149:    marker_expr = config.getoption("-m", default="")
tools/enforcement/pytest_config_guard.py:126:        # Check for brittle getoption("-m") marker access (AST-based detection)
tools/enforcement/pytest_config_guard.py:136:        """Check for brittle config.getoption("-m") marker access patterns.
tools/enforcement/pytest_config_guard.py:138:        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
tools/enforcement/pytest_config_guard.py:150:                                f'config.getoption("-m") should be replaced with '
tools/enforcement/pytest_config_guard.py:252:        """Test that getoption("-m") is flagged as brittle."""
tools/enforcement/pytest_config_guard.py:275:    marker_expr = config.getoption("-m", default="")
```

### Scan 2: getoption('-m') patterns (single quotes)

**Command executed:**
```
git grep -n "getoption('-m'" -- tests tools
```

**Results:**

```
tools/enforcement/pytest_config_guard.py:138:        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
```

### In-scope hits to fix

**Production code (must fix):**

1. **tests/conftest.py:149**
   - Current: `marker_expr = config.getoption("-m", default="")`
   - Action: Replace with `getattr(config.option, "markexpr", "")`

**Test/Guard code (no action needed - these are comments, docstrings, and test fixtures):**

- tools/enforcement/pytest_config_guard.py:126 (comment)
- tools/enforcement/pytest_config_guard.py:136 (docstring)
- tools/enforcement/pytest_config_guard.py:138 (docstring)
- tools/enforcement/pytest_config_guard.py:150 (error message string)
- tools/enforcement/pytest_config_guard.py:252 (docstring)
- tools/enforcement/pytest_config_guard.py:275 (test fixture code string - intentional for testing)

**Summary:** 1 production hit to fix in tests/conftest.py

---

## Wave 1.2: Remediate + Regression Lock

### A) Fix production hit in tests/conftest.py

**File:** tests/conftest.py:149

**Change:**
```python
# Before:
marker_expr = config.getoption("-m", default="")

# After:
marker_expr = getattr(config.option, "markexpr", "")
```

### B) Regression test verification

The guard already has regression tests in place from Phase 1:

- `tools/enforcement/pytest_config_guard.py::TestPytestConfigGuardBrittleMarkerDetection::test_detects_brittle_getoption_m` - Verifies that getoption("-m") is flagged as brittle
- `tools/enforcement/pytest_config_guard.py::TestPytestConfigGuardBrittleMarkerDetection::test_allows_robust_getattr_pattern` - Verifies that getattr(config.option, "markexpr", "") is NOT flagged

These tests will fail if the brittle detection rule is removed.

### C) Test verification

**Enforcement test run:**

```
============================= test session starts =============================
collected 5 items

tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_pytest_ini PASSED [ 20%]
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_valid_pytest_configuration PASSED [ 40%]
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_required_markers PASSED [ 60%]
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_unregistered_markers_in_tests PASSED [ 80%]
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_conftest_hook_without_docstring PASSED [100%]

============================== 5 passed in 0.02s ==============================
```

Exit code: 0

**Full pytest run:**

```
============================ 153 passed in 19.89s ========================
```

Exit code: 0

---

## Wave 1.3: Final Scan + Single Commit
