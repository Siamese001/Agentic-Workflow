# Guardian Hardening v4 — Type/Contract Drift Elimination

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

All 4 phases completed. Eliminates remaining type/contract drift risks by enforcing enum round-trip for `artifact_class`, requiring `index` for aggregates, preventing ignore-date time-bombing, and removing ambiguity from integrity checker aliasing.

**204/204 core guardian tests pass.**

---

## Phase 1 — Canonicalize `artifact_class` representation end-to-end

**Problem**: `artifact_class` was stored as string, losing enum identity and allowing invalid values.

**Fix**:
- Changed `GuardianResult.artifact_class` type from `str` to `ArtifactClass` enum (default `INDIVIDUAL`)
- `to_dict()` serializes as `artifact_class.value` (string)
- `load_guardian_result()` parses string back to `ArtifactClass` enum with validation
- `validate_against_json_schema()` validates serialized value is in enum set

**Files changed**:

- `guardian_contract.py`:
  - Line 633: Changed field type to `ArtifactClass = ArtifactClass.INDIVIDUAL`
  - Line 694: Serialize as `.value` in `to_dict()`
  - Line 755-769: Added `_parse_artifact_class()` helper with validation
  - Line 782: Use `_parse_artifact_class()` in `load_guardian_result()`
  - Lines 489-496: Added enum value validation in schema validator
- `run_all_guardians.py`:
  - Line 93: Pass `ArtifactClass.AGGREGATE` (enum, not `.value`)
- `test_contract_compatibility.py`:
  - Line 580: Updated test to expect enum, not string
  - Lines 583-676: Added `TestArtifactClassRoundTrip` (4 tests)
  - Line 543: Fixed test to use enum, not `.value`

**Evidence**: `test_unknown_artifact_class_fails_load` PASS — rejects "unknown_type" with clear error message

---

## Phase 2 — Aggregate must include `index`

**Problem**: Aggregates could omit `index` field, violating contract expectations.

**Fix**: Added post-validation rules in `validate_against_json_schema()`:
- If `artifact_class != AGGREGATE`: `index` must be absent/None
- If `artifact_class == AGGREGATE`: `index` must be present (non-None)

**Files changed**:

- `guardian_contract.py`:
  - Lines 498-514: Added aggregate field requirements validation
- `test_contract_compatibility.py`:
  - Lines 678-755: Added `TestAggregateIndexRequirement` (4 tests)

**Evidence**: `test_aggregate_missing_index_fails` PASS — aggregate without index rejected

---

## Phase 3 — Replace fixed ignore dates with rolling review window

**Problem**: Fixed calendar dates create time-bomb failures that require constant updates.

**Fix**: Enforce `review_by` is not in the past AND not more than `TODAY + `. Keep injected `_TODAY` for deterministic tests.

**Files changed**:

- `test_conftest_ignore_policy.py`:
  - Lines 197-215: Added `test_review_dates_not_too_far_in_future`
- `conftest.py`: Comments already use 2026-06-01 (within 180-day window from 2026-02-09)

**Evidence**: `test_review_dates_not_too_far_in_future` PASS — enforces 180-day maximum future window

---

## Phase 4 — Deprecate/remove integrity checker alias ambiguity

**Problem**: Main loop could call either the new broad function or the deprecated alias, creating ambiguity.

**Fix**:
- Marked `_check_no_raise_runtime_error_for_caps` as DEPRECATED in comment
- Verified main loop only calls `_check_no_raise_exception_for_caps`
- Added test to assert main loop doesn't reference deprecated alias

**Files changed**:

- `run_guardian_contract_integrity.py`:
  - Lines 146-150: Added DEPRECATED comment to legacy wrapper
- `test_scan_budget_integrity.py`:
  - Lines 183-199: Added `test_main_loop_uses_non_deprecated_function`

**Evidence**: `test_main_loop_uses_non_deprecated_function` PASS — confirms main loop uses non-deprecated function

---

## Test Results

```text
204 passed in 10.17s
GUARDIAN STATUS: PASS
```

## Test Count Progression

| Version | Core Tests | Total Tests | Delta |
|---------|------------|-------------|-------|
| v4      | 194        | 194         | +15   |
| v4+     | 204        | 204+        | +10   |

*Note: Total tests exceed 204 when including pre-existing failing tests outside core guardian suite.*

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

