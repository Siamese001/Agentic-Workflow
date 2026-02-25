# Pytest Structural Authority Analysis

## Executive Summary

**DETERMINATION**: `tests/unit_min_deps` were introduced as **MARKER-BASED STRUCTURAL TESTS**, not as part of the authoritative default suite.

## Historical Evidence

### Commit 05b1c9732 (2026-02-08) - "Commit B: True unit_min_deps isolation"

**Key Evidence from commit message:**
```
Commit B: True unit_min_deps isolation (marker run, zero collection errors)

- Created root conftest.py with pytest_make_collect_report wrapper hook
  - Suppresses pre-existing collection errors (ImportError, NameError, TypeError,
    import file mismatch) so marker-based test selection works cleanly
  - Transparent pass-through when no collection errors occur

Evidence: pytest -m unit_min_deps -q -> 29 passed, 0 errors, exit 0
```

**Critical Findings:**
1. **Purpose**: Enable marker-based execution (`-m unit_min_deps`)
2. **Design**: Collection error suppression for clean marker runs
3. **Evidence**: Explicitly tested with marker, not default testpaths
4. **Intent**: Isolation for specific test category, not default suite

### Testpaths Evolution

**Before 05b1c9732:**
```ini
testpaths = tests
```

**After 05b1c9732:**
```ini
testpaths = tests
# No change to testpaths - unit_min_deps remained marker-based
```

**When unit_min_deps was added to testpaths (later):**
- Occurred in a subsequent commit, not the original design
- Changed from `testpaths = tests` to include specific directories
- This was a later deviation from the original marker-based design

### Original Design Intent

**From commit 05b1c9732 analysis:**
1. `unit_min_deps` marker defined for "tests that run without optional deps"
2. Root conftest.py created to handle collection errors for marker-based runs
3. Explicit evidence: `pytest -m unit_min_deps -q -> 29 passed, 0 errors, exit 0`
4. No mention of adding to default testpaths in original design

### Marker vs Testpaths Conflict

**Original Design (Marker-based):**
- Tests marked with `@pytest.mark.unit_min_deps`
- Executed via: `pytest -m unit_min_deps`
- Default suite: `testpaths = tests`

**Later Deviation (Testpaths inclusion):**
- `tests/unit_min_deps` added to testpaths
- Broke the original marker-based isolation design
- Created the current governance issue

## Conclusion

**ANSWER: NO** - `tests/unit_min_deps` were NOT explicitly defined as part of the authoritative suite in their original design.

**Evidence:**
1. Original commit (05b1c9732) designed them as marker-based structural tests
2. Explicit evidence shows marker-based execution (`pytest -m unit_min_deps`)
3. Testpaths inclusion was a later deviation from original intent
4. Collection error suppression designed for marker isolation, not default runs

**Implication:**
- Current testpaths configuration violates original design intent
- Proper resolution is to restore marker-based execution model
- Remove from default testpaths, maintain marker accessibility
