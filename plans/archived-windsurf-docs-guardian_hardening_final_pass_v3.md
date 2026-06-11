---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\guardian_hardening_final_pass_v3.md'
original_relative_path: 'guardian_hardening_final_pass_v3.md'
source_sha256: 4eb071987edcdde64262c05eed5bb492b90d07451fe163d5a13047f0b364b184
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Guardian Hardening Final Pass v3 — Governance Loophole Lockdown

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

All 4 phases completed. Closes the governance smells identified in v2 critique.

**179/179 guardian hardening tests pass.**

---

## Phase 1: Aggregate-Only `index` Enforcement

**Problem**: `index` field on `GuardianResult` was available to any guardian, weakening type clarity.

**Fix**: Added `AGGREGATE_GUARDIAN_ID = "combined"` constant to SSOT. Post-validation rule in `validate_against_json_schema` rejects `index` when `guardian_id != AGGREGATE_GUARDIAN_ID`. Aggregator now imports and uses the constant instead of a hardcoded string.

**Files changed**:

- `guardian_contract.py`: Added `AGGREGATE_GUARDIAN_ID` constant + aggregate-only index guard in validator
- `run_all_guardians.py`: Imports `AGGREGATE_GUARDIAN_ID`, uses it for `combined.guardian_id`
- `test_contract_compatibility.py`: Added `TestAggregateOnlyIndexEnforcement` (4 tests) + metrics-depth isolation test

**Evidence**: `test_individual_result_with_index_fails` PASS, `test_aggregate_result_with_index_passes` PASS

---

## Phase 2: Ignore List Governance Ratchet

**Problem**: `collect_ignore_glob` in `conftest.py` is a single-file "god switch" that could silently expand.

**Fix**: Created `test_conftest_ignore_policy.py` with:

- Locked `LOCKED_IGNORE_ALLOWLIST` snapshot (test fails if list changes)
- `MAX_IGNORES = 4` ceiling
- Ticket reference requirement: each ignore must have `TODO(#<id>)` comment
- AST extraction of `collect_ignore_glob` (no regex on source)

Updated `conftest.py` TODO comments to use `TODO(#GUARD-01)` / `TODO(#GUARD-02)` format.

**Files changed**:

- `tests/guardian/test_conftest_ignore_policy.py`: New file (4 tests)
- `tests/guardian/conftest.py`: Updated TODO comments to include ticket refs

**Evidence**: `test_ignore_list_matches_locked_allowlist` PASS, `test_each_ignore_has_ticket_reference` PASS

---

## Phase 3: Integrity Checker Bans Cap RuntimeErrors

**Problem**: Future scanning guardians could regress by raising `RuntimeError` for scan caps instead of returning FAIL via `guard_scan_budget()`.

**Fix**: Added 3 AST-based detection functions to `run_guardian_contract_integrity.py`:

- `_check_imports_scan_caps`: Detects guardians importing `MAX_FILES_PER_SCAN` / `MAX_FOLDER_DEPTH`
- `_check_uses_guard_scan_budget`: Verifies `guard_scan_budget` import
- `_check_no_raise_runtime_error_for_caps`: Flags `raise RuntimeError(...)` mentioning cap names

Wired as Check 4 in the integrity guardian loop. Created `test_scan_budget_integrity.py` with synthetic AST fixtures proving detection (good guardian, bad-raises-error, bad-missing-helper, non-scanning).

**Files changed**:

- `run_guardian_contract_integrity.py`: Added 3 AST check functions + Check 4 in main loop
- `tests/guardian/test_scan_budget_integrity.py`: New file (10 tests)

**Evidence**: `test_detects_raise_runtime_error_with_cap_name` PASS, `test_no_false_positive_on_correct_guardian` PASS

---

## Phase 4: Disabled Guardian Invariants

**Problem**: No explicit assertion that disabled guardians are excluded from the aggregate index and checks.

**Fix**: Added `TestDisabledGuardianExclusion` to `test_aggregator_invariants.py`:

- `test_index_excludes_disabled_guardians`: disabled IDs NOT in `combined.index`
- `test_index_keys_are_strict_subset_of_enabled`: no extras beyond enabled set
- `test_aggregate_uses_ssot_guardian_id`: verifies `AGGREGATE_GUARDIAN_ID` constant
- `test_disabled_guardians_not_in_checks`: disabled IDs NOT in aggregate checks

**Files changed**:

- `tests/guardian/test_aggregator_invariants.py`: Added `TestDisabledGuardianExclusion` (4 tests)

**Evidence**: All 4 disabled guardian invariant tests PASS

---

## Test Results

```text
179 passed in 10.19s
GUARDIAN STATUS: PASS
```

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

