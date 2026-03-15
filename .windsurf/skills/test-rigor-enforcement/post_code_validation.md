# Post-Code Validation

**MANDATORY after code changes.**

Enforces §1.12 (zero-tolerance for test skipping) and verifies test coverage matches declared scope.

## Protocol

### Step 1: Run Pytest Collection

```bash
pytest --collect-only -q
```

**Capture output:**
```
COLLECTED: 18 tests
```

### Step 2: Run Pytest Execution

```bash
pytest -v
```

**Capture output:**
```
EXECUTED: 18 tests
PASSED: 18
FAILED: 0
ERROR: 0
SKIPPED: 0
```

### Step 3: Verify Collection = Execution (§1.12)

**Formula:**
```
collected_count == (passed + failed + error)
```

**If counts mismatch:**
```
COLLECTED: 18
EXECUTED: 15  ← MISMATCH!
DESELECTED: 3  ← CONSTITUTIONAL VIOLATION (§1.12)
```

**Action:**
- STOP immediately
- Invoke `pytest-integrity/conftest_hook_audit.md`
- Identify why tests were deselected
- Fix conftest hooks or marker registration
- Re-run until collected == executed

### Step 4: Verify Test Coverage Matches Scope

Cross-reference with `pre_code_generation_gate.md`:

**Declared scope:**
```
TEST_REQUIREMENTS: 18 tests minimum
```

**Actual execution:**
```
EXECUTED: 18 tests ✅
```

**If actual < declared:**
```
DECLARED: 18 tests
EXECUTED: 12 tests ← COVERAGE GAP!
MISSING: 6 tests
```

**Action:**
- Identify missing test categories (edge cases, determinism, fail-closed)
- Write missing tests
- Re-run validation

### Step 5: Verify No Test Skipping

**Check for skip markers:**
```bash
grep -r "@pytest.mark.skip\|@pytest.mark.skipif" tests/
```

**Expected output:**
```
(no results)
```

**If skips found:**
```
tests/test_module.py:42: @pytest.mark.skip(reason="TODO")
```

**Action:**
- Remove skip markers
- Fix or delete incomplete tests
- Re-run validation

### Step 6: Verify Determinism

Run tests multiple times to verify deterministic behavior:

```bash
pytest tests/test_new_module.py -v --tb=short
pytest tests/test_new_module.py -v --tb=short
pytest tests/test_new_module.py -v --tb=short
```

**Expected:**
- Same tests pass/fail each run
- Same order of execution
- Same assertion values

**If non-deterministic:**
```
Run 1: test_function PASSED
Run 2: test_function FAILED  ← NON-DETERMINISTIC!
```

**Action:**
- Identify source of randomness (time, random, external state)
- Fix seed or inject deterministic values per §1.3
- Re-run validation

### Step 7: Verify No Mock Bypass (§1.4)

**Check for integration seam mocks:**
```bash
grep -r "mock.*validate\|mock.*signature\|mock.*routing" tests/
```

**If mocks found bypassing enforcement:**
```
tests/test_module.py:15: mock_validate.return_value = True  ← VIOLATION!
```

**Action per §1.4:**
- Remove mocks for validation, signature checks, routing gates
- Use real integration for enforcement seams
- Re-run validation

### Step 8: Generate Validation Report

**Template:**
```
POST-CODE VALIDATION REPORT

Scope: 2 files changed
  - agentic_core/L5_safety/validators/new_validator.py
  - agentic_core/L5_safety/enforcement/existing_enforcer.py

Test Execution:
  Collected: 18 tests
  Executed:  18 tests
  Passed:    18 tests
  Failed:    0 tests
  Skipped:   0 tests

  Collection/Execution Match: ✅ PASS (§1.12)

Test Coverage:
  Declared minimum: 18 tests
  Actual coverage:  18 tests
  Coverage gap:     0 tests

  Coverage Match: ✅ PASS (§1.1)

Determinism:
  Runs: 3
  Consistent results: ✅ YES

  Determinism: ✅ PASS (§1.3)

Edge Cases:
  null/None: ✅ 2 tests
  empty input: ✅ 2 tests
  malformed: ✅ 2 tests
  boundary: ✅ 2 tests
  unauthorized: ✅ 1 test
  dependency failure: ✅ 1 test
  negative control: ✅ 2 tests
  recovery: ✅ 1 test

  Edge Coverage: ✅ PASS (§1.5)

Fail-Closed:
  Invalid preconditions block: ✅ 3 tests
  No side-effects before block: ✅ 3 tests

  Fail-Closed: ✅ PASS (§1.8)

Mock Bypass Check:
  Integration seam mocks: ✅ NONE

  Mock Discipline: ✅ PASS (§1.4)

VALIDATION STATUS: ✅ APPROVED FOR COMMIT

Constitutional Compliance:
  §1.1 Zero-tolerance: ✅ PASS
  §1.2 Test-first: ✅ PASS
  §1.3 Deterministic: ✅ PASS
  §1.4 No mock bypass: ✅ PASS
  §1.5 Edge cases: ✅ PASS
  §1.8 Fail-closed: ✅ PASS
  §1.12 No test skipping: ✅ PASS
```

### Step 9: Gate Decision

**BLOCK commit if ANY of:**
- Collection ≠ Execution (§1.12 violation)
- Actual tests < Declared minimum (§1.1 violation)
- Tests are non-deterministic (§1.3 violation)
- Skip markers present (§1.12 violation)
- Mocks bypass enforcement (§1.4 violation)
- Edge cases missing (§1.5 violation)

**ALLOW commit only if:**
- All validation checks pass
- All constitutional requirements met
- Validation report generated

## Enforcement

```
IF all_checks_pass:
    APPROVE commit
    SAVE validation report to docs/reports/plans/
ELSE:
    BLOCK commit
    REQUIRE fixes per failed checks
    RE-RUN post_code_validation.md
```

## Constitutional References

- **§1.1:** Every line of changed logic MUST be covered by deterministic tests
- **§1.3:** Tests MUST be deterministic
- **§1.4:** No mocks for integration seams
- **§1.5:** Every changed surface MUST include edge case tests
- **§1.8:** Tests MUST prove invalid preconditions block operation
- **§1.12:** Zero-tolerance for test skipping
