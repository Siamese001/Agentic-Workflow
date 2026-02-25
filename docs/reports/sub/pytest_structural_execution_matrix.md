# Pytest Structural Execution Matrix

## Execution Behavior Analysis

### Current Testpaths Configuration
```ini
testpaths = tests/integration/agentic_core
```

### Execution Results

| Command | Tests Collected | Tests Run | Result | Notes |
|---------|----------------|-----------|--------|-------|
| `pytest -q` | 19 | 19 | **PASSED** | Default suite - only integration tests |
| `pytest -m unit_min_deps -q` | 19 | 0 | **SKIPPED** | No tests selected - unit_min_deps not in testpaths |
| `pytest tests/unit_min_deps -q` | 79 | 79 | **19 FAILED, 60 PASSED** | Direct path execution reveals structural failures |

### Key Findings

1. **Default Suite (pytest -q)**:
   - Runs only `tests/integration/agentic_core`
   - 19 tests pass
   - No structural enforcement

2. **Marker Execution (pytest -m unit_min_deps)**:
   - Collects 0 tests (not in testpaths)
   - Marker-based isolation broken by testpaths change

3. **Direct Path Execution**:
   - 79 tests collected from unit_min_deps
   - 19 failures reveal structural debt
   - Tests are marked with `@pytest.mark.unit_min_deps`

### Structural Failures Identified

The 19 failing tests detect:
- Import boundary violations
- Agent placement violations
- Folder structure violations
- Configuration property violations
- Quarantine manifest inconsistencies
- Root hygiene violations
- Testpaths contract violations

### Execution Intent vs Reality

**Original Intent (from commit 05b1c9732):**
- Marker-based execution: `pytest -m unit_min_deps`
- Collection error suppression for clean runs
- Structural governance enforcement

**Current Reality:**
- Marker execution broken (tests not in testpaths)
- Structural failures hidden from default suite
- Governance bypassed through testpaths manipulation

### Corrective Model Required

**CASE B - Structural Audit Model:**
1. Remove `tests/unit_min_deps` from default testpaths
2. Restore marker-based execution functionality
3. Document structural audit execution contract
4. Maintain governance enforcement visibility

**Required Changes:**
- `pytest.ini`: Remove unit_min_deps from testpaths
- `docs/testing/TEST_CONTRACT.md`: Document structural audit suite
- Governance policy: Explicit classification decision
