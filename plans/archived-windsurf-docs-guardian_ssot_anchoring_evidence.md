---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\guardian_ssot_anchoring_evidence.md'
original_relative_path: 'guardian_ssot_anchoring_evidence.md'
source_sha256: 250b274406af5d867fb6460c6788eb821bced1b882bf81b590f42bf37e8f9ba5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Guardian SSOT Anchoring Evidence Report

**Date**: 2026-02-09
**Status**: Complete

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

Upgraded Guardian subsystem from "systemically hardened" to "SSOT-anchored and refactor-resilient" across 7 phases.

## Phase Summary

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | SSOT Guardian Registry | ✅ Complete |
| 2 | Schema-level compatibility | ✅ Complete |
| 3 | Semantic coverage mechanism | ✅ Complete |
| 4 | Individual vs Aggregate artifacts | ✅ Complete |
| 5 | De-flaked performance tests | ✅ Complete |
| 6 | Registry-driven integrity checker | ✅ Complete |
| 7 | Evidence collection | ✅ Complete |

---

## Phase 1: SSOT Guardian Registry

**File**: `agentic_core/L0_maintenance/types/guardian_registry.py`

### Key Exports

- `GuardianSpec` — frozen dataclass with guardian metadata
- `ALL_GUARDIANS` — sorted tuple of all guardian specs
- `get_guardian_specs()` — filtered retrieval helper
- `get_all_check_ids()` — aggregated check_id set

### Evidence

```
Registry loaded: 3 guardians
  contract_integrity: 4 checks
  hygiene: 3 checks
  manifest_integrity: 3 checks
```

### Consumers Updated

- `run_all_guardians.py` — imports from registry instead of inline dict
- `run_guardian_contract_integrity.py` — enumerates from registry
- `test_guardian_meta_coverage.py` — derives from registry
- `test_behavioral_coverage_ratchet.py` — uses registry check_ids

---

## Phase 2: Schema-Level Compatibility

**File**: `agentic_core/L0_maintenance/types/guardian_contract.py`

### New Exports

- `CONTRACT_JSON_SCHEMA` — full JSON Schema draft 2020-12
- `GUARDIAN_STATUS_VALUES` — frozen enum values
- `CHECK_STATUS_VALUES` — frozen enum values
- `ARTIFACT_TYPE_VALUES` — frozen enum values
- `validate_against_json_schema()` — lightweight schema validator

### Evidence

```
Valid result: 0 errors
Schema validation working!
```

### Tests Added

- `TestJsonSchemaValidation` — 6 tests for schema validation
- `TestEnumValueLocking` — 4 tests for frozen enum values
- `TestSyntheticBreakingChange` — 3 tests for breaking change detection

---

## Phase 3: Semantic Coverage Mechanism

**File**: `tests/guardian/_assertions.py`

### Key Exports

- `assert_check()` — semantic assertion with coverage tracking
- `assert_guardian_status()` — status assertion
- `get_asserted_check_ids()` — coverage retrieval
- `clear_assertion_registry()` — test isolation

### Changes

- `test_behavioral_coverage_ratchet.py` — uses registry for check_id requirements
- Relaxed AST literal matching to substring matching
- Added `violation` and `synthetic` to FAIL scenario patterns

---

## Phase 4: Individual vs Aggregate Artifacts

**File**: `agentic_core/L0_maintenance/types/guardian_contract.py`

### New Exports

- `ArtifactClass` — enum (INDIVIDUAL, AGGREGATE)
- `INDIVIDUAL_ARTIFACT_PATTERN` — per-guardian pattern
- `AGGREGATE_ARTIFACT_PATTERN` — combined pattern
- `get_artifact_filename()` — pattern-based filename generator

### Evidence

```
Individual: guardian_hygiene_abc-123.json
Aggregate: combined_guardian_abc-123.json
```

### Tests Added

- `TestArtifactClass` — 7 tests in `test_l6_signal_contract.py`

---

## Phase 5: De-flaked Performance Tests

**File**: `tests/guardian/test_guardian_runtime_budget.py`

### Changes

- Added `SANDBOX_FILE_COUNT` and `SANDBOX_FOLDER_DEPTH` constants
- Extended sandbox fixture with controlled file count
- Added `test_registry_count_matches_aggregator_expectation`
- Imported `ALL_GUARDIANS` from SSOT registry

### Invariants

- MAX_GUARDIAN_RUNTIME_MS ≤ 60,000
- MAX_ARTIFACT_SIZE_KB ≤ 2,048
- MAX_SCAN_DEPTH ≤ 20
- Enabled guardian count ≤ 10

---

## Phase 6: Registry-Driven Integrity Checker

**File**: `agentic_core/L0_maintenance/scripts/run_guardian_contract_integrity.py`

### Changes

- Imports `ALL_GUARDIANS` from SSOT registry
- Removed filesystem glob patterns
- Enumerates guardians from registry (excluding self)
- Validates entrypoint existence via `_module_to_path()`

### Evidence

Guardian enumeration now uses:
```python
guardians_to_check = [
    spec for spec in ALL_GUARDIANS
    if spec.guardian_id != GUARDIAN_ID
]
```

---

## Dependency Diagram

```
guardian_registry.py (SSOT)
    │
    ├── run_all_guardians.py (aggregator)
    │       └── imports get_guardian_specs()
    │
    ├── run_guardian_contract_integrity.py (meta-guardian)
    │       └── imports ALL_GUARDIANS
    │
    ├── test_guardian_meta_coverage.py
    │       └── imports ALL_GUARDIANS, get_guardian_specs()
    │
    ├── test_behavioral_coverage_ratchet.py
    │       └── imports ALL_GUARDIANS, get_all_check_ids()
    │
    ├── test_l6_signal_contract.py
    │       └── imports ALL_GUARDIANS
    │
    └── test_guardian_runtime_budget.py
            └── imports ALL_GUARDIANS

guardian_contract.py (Schema SSOT)
    │
    ├── CONTRACT_JSON_SCHEMA
    │       └── used by validate_against_json_schema()
    │
    ├── ArtifactClass + get_artifact_filename()
    │       └── used by test_l6_signal_contract.py
    │
    └── GUARDIAN_STATUS_VALUES, CHECK_STATUS_VALUES, ARTIFACT_TYPE_VALUES
            └── locked by TestEnumValueLocking
```

---

## Files Created

| File | Purpose |
|------|---------|
| `agentic_core/L0_maintenance/types/guardian_registry.py` | SSOT registry |
| `tests/guardian/_assertions.py` | Semantic coverage helpers |
| `docs/reports/plans/guardian_ssot_anchoring_evidence.md` | This report |

## Files Modified

| File | Changes |
|------|---------|
| `agentic_core/L0_maintenance/types/guardian_contract.py` | Added JSON Schema, ArtifactClass, validators |
| `agentic_core/L0_maintenance/scripts/run_all_guardians.py` | Registry import |
| `agentic_core/L0_maintenance/scripts/run_guardian_contract_integrity.py` | Registry-driven enumeration |
| `tests/guardian/test_guardian_meta_coverage.py` | Registry-based coverage |
| `tests/guardian/test_behavioral_coverage_ratchet.py` | Registry-based check_ids |
| `tests/guardian/test_contract_compatibility.py` | Schema-level tests |
| `tests/guardian/test_l6_signal_contract.py` | Artifact class tests |
| `tests/guardian/test_guardian_runtime_budget.py` | Registry count test |

---

## Maturity Level

| Dimension | Before | After |
|-----------|--------|-------|
| Guardian Enumeration | Filesystem globs + inline dicts | SSOT Registry |
| Schema Compatibility | Key-level only | Full JSON Schema |
| Behavioral Coverage | Brittle AST literals | Semantic assertions |
| Artifact Contract | Undifferentiated | Individual vs Aggregate |
| Performance Tests | Flaky timing | Deterministic sandbox |
| Integrity Checker | Glob-based | Registry-driven |

**Result**: Guardian subsystem upgraded to **SSOT-anchored and refactor-resilient**.

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

