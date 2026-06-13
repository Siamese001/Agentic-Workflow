# Guardian Junior-Pattern Brittleness Elimination

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary

Eliminated 4 junior-pattern brittleness issues: (1) removed line-number coupling from AST fixtures, (2) ratcheted against `.value` drift for `artifact_class`, (3) SSOT-locked the contract-gate test scope, and (4) enforced alias non-usage beyond definition.

**213/213 core guardian tests pass.**

---

## Phase 1 — Remove line-number brittleness in scan-budget integrity tests

**Problem**: Tests asserted exact `node.lineno` values, creating brittle fixtures that break when code changes.

**Fix**:
- Replaced line number assertions with:
  - Violation count checks
  - Exception type validation
  - Message content validation (contains cap names)
- Kept negative fixtures per exception type without line numbers

**Files changed**:

- `test_scan_budget_integrity.py`:
  - Line 180: Changed from `assert violations == [(11, "ValueError")]` to count and type checks
  - Line 209: Added explicit count check for RuntimeError

**Evidence**: `test_detects_value_error_with_cap_name` PASS — validates exception type without line coupling

---

## Phase 2 — Ratchet: forbid `.value` when constructing `GuardianResult`

**Problem**: Junior pattern of using `artifact_class=ArtifactClass.AGGREGATE.value` instead of the enum directly.

**Fix**: Created AST-scanning ratchet that:
- Scans `agentic_core/L0_maintenance/scripts/` and `tests/guardian/`
- Fails on `GuardianResult(... artifact_class=ArtifactClass.<X>.value ...)`
- Whitelists `.value` usage only in `guardian_contract.py` serialization logic
- Reports exact file/line violations

**Files created**:

- `test_artifact_class_enum_ratchet.py`:
  - `_find_guardian_result_with_value_usage()` — AST scanner with whitelist
  - `test_no_artifact_class_value_usage_in_construction()` — Ratchet test
  - `test_synthetic_value_usage_detected()` — Synthetic violation detection

**Evidence**: Ratchet PASS on repo, FAIL on synthetic `.value` usage

---

## Phase 3 — SSOT-lock the contract gate scope

**Problem**: Contract gate scope could be silently widened via ignores or new test modules.

**Fix**:
- Defined SSOT `CONTRACT_GATE_TEST_MODULES` tuple (13 modules)
- Asserted all SSOT modules exist and are not ignored
- Prevented silent addition of contract modules without SSOT update
- Enforced ignore ceiling to prevent gate widening

**Files created**:

- `test_guardian_contract_gate_scope.py`:
  - `CONTRACT_GATE_TEST_MODULES` — SSOT list of 13 core modules
  - `test_contract_gate_modules_are_present()` — Existence validation
  - `test_collect_ignore_glob_excludes_no_contract_modules()` — Ignore validation
  - `test_no_additional_contract_gate_modules_without_update()` — Silent addition prevention
  - `test_contract_gate_scope_cannot_be_widened_by_ignores()` — Ignore ceiling

**Evidence**: All 13 contract gate modules present, none ignored, ignore count ≤5

---

## Phase 4 — Enforce alias non-usage beyond definition

**Problem**: Deprecated alias `_check_no_raise_runtime_error_for_caps` could be called beyond its definition.

**Fix**:
- AST-scanned `run_guardian_contract_integrity.py`
- Asserted alias appears only in its `def` statement and docstring
- Verified no Call nodes reference the alias
- Confirmed main loop uses non-deprecated function

**Files created**:

- `test_integrity_checker_alias_policy.py`:
  - `_find_alias_references()` — AST scanner with context detection
  - `test_deprecated_alias_only_used_in_definition()` — No calls beyond definition
  - `test_main_loop_uses_correct_function()` — Uses non-deprecated function
  - `test_alias_definition_exists_and_is_deprecated()` — Definition exists with DEPRECATED marker

**Evidence**: Alias referenced only in definition, main loop uses correct function

---

## Test Results

```text
213 passed in 10.99s
GUARDIAN STATUS: PASS
```

## Test Count Progression

| Version | Core Tests | Total Tests | Delta |
|---------|------------|-------------|-------|
| v4+     | 204        | 204+        | +0    |
| v5      | 213        | 213+        | +9    |

*Note: Total tests exceed 213 when including pre-existing failing tests outside core guardian suite.*

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

