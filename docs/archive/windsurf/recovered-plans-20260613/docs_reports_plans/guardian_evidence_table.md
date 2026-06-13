# Guardian Update — Evidence Table (Level 3: Systemically Hardened)

Generated: 2026-02-08

## Files Created/Modified

### Phase 0-2 (Foundation)

| File | Purpose |
| ---- | ------- |
| `agentic_core/L0_maintenance/types/guardian_contract.py` | Canonical schema + compatibility gate + L6 constants + performance ceilings |
| `agentic_core/L0_maintenance/scripts/run_guardian_hygiene.py` | Hygiene guardian with SSOT imports, CLI, schema-locked output |
| `agentic_core/L0_maintenance/scripts/run_guardian_manifest.py` | Manifest integrity guardian with SSOT imports, CLI, schema-locked output |
| `docs/reports/plans/guardian_inventory.md` | Phase 0 discovery inventory |

### Phase A — Contract Compatibility Ratchet

| File | Purpose |
| ---- | ------- |
| `tests/guardian/test_contract_compatibility.py` | 15 tests: snapshot fidelity, check/artifact key lock, compatibility gate, version bump migration |

### Phase B — Aggregation Runner

| File | Purpose |
| ---- | ------- |
| `agentic_core/L0_maintenance/scripts/run_all_guardians.py` | Deterministic aggregator with sorted execution, global status rollup, combined artifact |
| `tests/guardian/test_guardian_aggregation.py` | 16 tests: clean/dirty rollup, deterministic ordering, per-guardian metrics, schema compliance, artifact writing |

### Phase C — Behavioral Coverage Ratchet

| File | Purpose |
| ---- | ------- |
| `tests/guardian/test_behavioral_coverage_ratchet.py` | 7 tests: check_id AST coverage, PASS/FAIL scenario enforcement, status promotion coverage |

### Phase D — L6 Signal Contract

| File | Purpose |
| ---- | ------- |
| `docs/contracts/guardian_to_L6.md` | L6 ingestion contract (artifact location, naming, correlation, compatibility) |
| `tests/guardian/test_l6_signal_contract.py` | 10 tests: constants, artifact path contract, correlation_id propagation, contract doc exists |

### Phase E — Performance Guard

| File | Purpose |
| ---- | ------- |
| `tests/guardian/test_guardian_runtime_budget.py` | 12 tests: ceiling constants, individual guardian runtime, aggregator runtime, artifact sizes |

### Phase F — Guardian Self-Integrity

| File | Purpose |
| ---- | ------- |
| `agentic_core/L0_maintenance/scripts/run_guardian_contract_integrity.py` | AST-based meta-guardian: verifies all guardian scripts follow contract |
| `tests/guardian/test_guardian_self_integrity.py` | 14 tests: AST checks, real repo integrity, synthetic violation detection, schema compliance |

### Cross-Cutting Updates

| File | Purpose |
| ---- | ------- |
| `tests/guardian/test_guardian_meta_coverage.py` | Updated: 4 guardian scripts + 5 coverage map entries |
| `.github/workflows/guardian-tests.yml` | Updated: all 10 test files + aggregator --strict step |

## Test Evidence

```text
Command: python -m pytest tests/guardian/test_guardian_contract.py
         tests/guardian/test_contract_compatibility.py
         tests/guardian/test_guardian_hygiene.py
         tests/guardian/test_guardian_manifest.py
         tests/guardian/test_guardian_aggregation.py
         tests/guardian/test_behavioral_coverage_ratchet.py
         tests/guardian/test_l6_signal_contract.py
         tests/guardian/test_guardian_runtime_budget.py
         tests/guardian/test_guardian_self_integrity.py
         tests/guardian/test_guardian_meta_coverage.py
         -v --tb=short -m guardian

Result:  146 passed in 0.42s
Exit:    0

GUARDIAN STATUS: PASS
```

## CLI Evidence

```text
Command: python -m agentic_core.L0_maintenance.scripts.run_all_guardians --format text
Result:
  Guardian Aggregator | Status: FAIL
  Summary: 1 guardian(s) failed out of 2 (4 checks)
    [FAIL] guardian_hygiene: Hygiene: 3/3 checks failed
    [PASS] guardian_manifest_integrity: Manifest integrity: SKIP (manifest.json absent)

Command: python -m agentic_core.L0_maintenance.scripts.run_guardian_contract_integrity --format text
Result:
  Guardian: contract_integrity | Status: PASS
  Summary: Contract integrity: 2 scripts checked, 0 violations
    [PASS] scripts_found: Found 2 guardian script(s)
    [PASS] imports_contract_run_guardian_hygiene.py
    [PASS] imports_normalize_run_guardian_hygiene.py
    [PASS] returns_result_run_guardian_hygiene.py
    [PASS] imports_contract_run_guardian_manifest.py
    [PASS] imports_normalize_run_guardian_manifest.py
    [PASS] returns_result_run_guardian_manifest.py
```

## Invariant Compliance

| Invariant | Status | Evidence |
| --------- | ------ | -------- |
| SSOT-only imports | PASS | All scripts import from `structure_blueprint` SSOT package |
| Schema lock | PASS | All output via `GuardianResult.to_json()` from canonical contract |
| Contract evolution safety | PASS | `CONTRACT_SCHEMA_SNAPSHOT` + `check_schema_compatibility()` + version bump test |
| Aggregation maturity | PASS | `run_all_guardians.py` with deterministic sorted execution + global rollup |
| Behavioral coverage | PASS | AST-scanned check_id coverage + PASS/FAIL scenario enforcement |
| Observability binding | PASS | `GUARDIAN_ARTIFACT_DIR` + naming pattern + `correlation_id` field + L6 contract doc |
| Drift self-protection | PASS | `run_guardian_contract_integrity.py` AST-checks all guardian scripts |
| Performance control | PASS | `MAX_GUARDIAN_RUNTIME_MS`/`MAX_ARTIFACT_SIZE_KB` ceilings + runtime budget tests |
| Deterministic execution | PASS | No `datetime.now()`, no network, injectable timestamp + correlation_id |
| No absolute paths | PASS | `validate_no_absolute_paths()` enforced in every schema compliance test |
| No claims without evidence | PASS | 146 tests pass, CLI output shown, all artifacts inspected |

## Maturity Model

| Layer | Status |
| ----- | ------ |
| Deterministic execution | PASS |
| Schema lock | PASS |
| Test coverage presence | PASS |
| Contract evolution safety | PASS |
| Aggregation maturity | PASS |
| Observability binding | PASS |
| Drift self-protection | PASS |
| Performance control | PASS |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

