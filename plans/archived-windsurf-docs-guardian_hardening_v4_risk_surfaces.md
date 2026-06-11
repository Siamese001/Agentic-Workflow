---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\guardian_hardening_v4_risk_surfaces.md'
original_relative_path: 'guardian_hardening_v4_risk_surfaces.md'
source_sha256: 316d5ef4c1bbe309f090ddfd9a05bf6bb3a7838e9a3a88da221f58f549d4aa41
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Guardian Hardening v4 — Risk Surface Elimination

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

All 4 phases completed. Removes magic-identifier coupling, time-bounds ignore exceptions, hardens scan budget enforcement against exception-type bypasses, and explicitly locks aggregator include/exclude semantics.

**194/194 guardian hardening tests pass.**

---

## Phase 1: Index enforcement via ArtifactClass, not guardian_id

**Problem**: `index` presence/absence was gated on `guardian_id == "combined"` — a magic identifier coupling. If aggregate ID changes or tiered aggregators emerge, the gate breaks.

**Fix**: Added `artifact_class` field to `GuardianResult` (default `ArtifactClass.INDIVIDUAL`). Aggregate sets `artifact_class=AGGREGATE`. Validator now checks `artifact_class`, not `guardian_id`.

**Files changed**:

- `guardian_contract.py`: Added `artifact_class` to `CONTRACT_SCHEMA_SNAPSHOT`, `CONTRACT_JSON_SCHEMA`, `GuardianResult` dataclass, `to_dict()`, `load_guardian_result()`, and updated validator gate
- `run_all_guardians.py`: Imports `ArtifactClass`, sets `artifact_class=ArtifactClass.AGGREGATE.value` on combined result
- `test_contract_compatibility.py`: Updated `EXPECTED_OPTIONAL_KEYS` (+artifact_class), snapshot key count (11→12), rewrote `TestAggregateOnlyIndexEnforcement` (7 tests including `test_non_aggregate_artifact_class_with_index_fails`, `test_default_artifact_class_is_individual`)

**Evidence**: `test_non_aggregate_artifact_class_with_index_fails` PASS — even with `guardian_id=="combined"`, setting `artifact_class="individual"` correctly rejects `index`

---

## Phase 2: Ignore list expiration + ownership policy

**Problem**: Locked allowlist + ticket refs prevent silent expansion but don't force resolution — ignored tests can live indefinitely.

**Fix**: Extended comment format to include `owner=@<handle>` and `review_by=YYYY-MM-DD`. Added `TestIgnoreListExpiration` with 3 tests enforcing owner presence, review_by presence, and expiration date check.

**Files changed**:

- `conftest.py`: Updated TODO comments to `TODO(#GUARD-01 owner=@guardian-team review_by=2026-06-01): ...`
- `test_conftest_ignore_policy.py`: Added `_OWNER_PATTERN`, `_REVIEW_BY_PATTERN`, `_TODAY` injection, `_get_comment_line_for_entry()` helper, and `TestIgnoreListExpiration` class (3 tests)

**Evidence**: `test_no_expired_ignores` PASS (review_by=2026-06-01 is in the future); will auto-fail on 2026-06-02

---

## Phase 3: Budget cap exception-type bypass prevention

**Problem**: Only `RuntimeError` was flagged. A future regression could raise `ValueError` or custom exceptions and bypass the "FAIL-not-ERROR" policy.

**Fix**: Added `_check_no_raise_exception_for_caps()` — catches any `raise <Exception>(...)` where message references cap symbols. Returns `(line, exception_name)` tuples. Legacy `_check_no_raise_runtime_error_for_caps` kept as backward-compatible alias. Main loop updated to use broadened check with exception type info in violation messages.

**Files changed**:

- `run_guardian_contract_integrity.py`: Added `_check_no_raise_exception_for_caps()`, backward-compat alias, updated Check 4 in main loop
- `test_scan_budget_integrity.py`: Added `BAD_GUARDIAN_RAISES_VALUE_ERROR`, `BAD_GUARDIAN_RAISES_CUSTOM_EXCEPTION` fixtures, and `TestAnyExceptionForCapsDetection` class (5 tests)

**Evidence**: `test_detects_value_error_with_cap_name` PASS, `test_detects_custom_exception_with_cap_name` PASS

---

## Phase 4: Aggregator mode invariants

**Problem**: No explicit `--include-disabled` flag; someone could change default behavior without tests catching it.

**Fix**: Added `include_disabled: bool = False` parameter to `run_all_guardians()` and `--include-disabled` CLI flag. Added `TestAggregatorModeInvariants` with 5 tests covering both modes.

**Files changed**:

- `run_all_guardians.py`: Added `include_disabled` parameter, `--include-disabled` CLI arg, passes to `get_guardian_specs(enabled_only=not include_disabled)`
- `test_aggregator_invariants.py`: Added `TestAggregatorModeInvariants` (5 tests: default excludes disabled, include_disabled includes all, validates contract, has aggregate artifact_class, default has fewer checks)

**Evidence**: `test_include_disabled_mode_includes_all` PASS, `test_default_mode_excludes_disabled` PASS

---

## Test Results

```text
194 passed in 9.88s
GUARDIAN STATUS: PASS
```

## Test Count Progression

| Version | Tests |
|---------|-------|
| v3      | 179   |
| v4      | 194   |
| Delta   | +15   |

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

