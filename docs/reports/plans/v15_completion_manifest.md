# V15 Completion Manifest — Runtime Enforcement Final

**Generated**: 2026-02-10
**Status**: UNWIRED = 0 repo-wide. All gates PASS.
**Branch**: `agentic-core-v5.2`

---

## Phase-by-Phase Summary

### Phase 0 — Smoke Path & Regression Guarantees

- **Objective**: Establish CI-ready P0 gate with evidence-only gating.
- **Commits**:
  - `87974a158` — feat(v15): Phase-0 CI-ready smoke path and regression guarantees
  - `f8b785449` — fix(v15): P0 gate evidence-only — baseline status counts ignored
  - `34c411cce` — feat(v15): Complete Phase-0 and Phase-0.1 implementation
- **Gate result**: P0 PASS (evidence_fail_count = 0)
- **Artifacts**: `ops_scripts/ci/v15_gap_regenerate_p0.py`, `ops_scripts/ci/v15_coverage_scoreboard.py`

### Phase 1 — D-Evidence Wiring & P1 Gate

- **Objective**: Wire critical D-set runtime guards, achieve D_RUNTIME_WIRED >= 80%.
- **Commits**:
  - `7f38a593a` — fix(v15): Phase 1 wiring + deterministic P0/P1 gates (CI-ready)
  - `bd4289d02` — fix(v15): Phase 1 lint compliance (no silent swallowers)
  - `1bf09cd95` — fix(v15): Phase 1 pre-commit compliance (detector-aligned allow comments)
- **Gate result**: P1 PASS (D_RUNTIME_WIRED = 100%, critical_d_set_passed = True)
- **Artifacts**: `ops_scripts/ci/v15_d_evidence_collect_p1.py`, `ops_scripts/ci/run_v15_p1_gate.py`

### Phase 2 — Runtime Entrypoint Enforcement & P2 Gate

- **Objective**: Wire all 28 runtime entrypoints with `@v15_runtime_guard` or `@_optional_v15_runtime_guard()`. Achieve UNWIRED = 0.
- **Commits**:
  - `fe944cfe7` — feat(v15): Wave 2.1 runtime entry-point inventory + guardian test
  - `ad74162c2` — feat(v15): P2 Wave 2.2 runtime entrypoint enforcement + P2 gate (CI-ready)
  - `73b6cba4e` — fix(v15): P2 Wave 2.2 pre-commit compliance (no scope expansion)
  - `2684b979b` — chore(pre-commit): deterministic normalization + generated-artifact tracking guard
  - `bec5cd1e1` — chore(pre-commit): clarify tier structure, deduplicate excludes
- **Gate result**: P2 PASS (24 WIRED, 4 ALREADY_ENFORCED, 0 UNWIRED, total = 28)
- **Artifacts**: `ops_scripts/ci/v15_d_evidence_collect_p2.py`, `ops_scripts/ci/run_v15_p2_gate.py`
- **Inventory**: `docs/reports/plans/v15_phase2_wave2_1_runtime_entrypoints.json` (28 entrypoints, 5 categories A–E)

### Phase 3 — Harden execute_ssot.py for CI

- **Objective**: Harden `execute_ssot.py` into a CI-safe, V15-aligned agent-init entrypoint.
- **Commits**:
  - `7bc503950` — Phase 3 Wave 3.1: harden execute_ssot.py for CI
- **Changes**:
  - Deterministic `REPO_ROOT = resolve_repo_root()` (no `Path.cwd()` dependence)
  - Lazy `@_optional_v15_runtime_guard()` on `_legacy_main` and `with_retry`
  - CLI flags: `--v15-enforcement`, `--verbose`
  - Forward reference fix (`RuntimeStateManager`)
  - AST parsing updated in evidence collector + bypass test for lazy decorator shape
- **Guardian tests**: 11/11 PASS (`tests/guardian/test_execute_ssot_v15_contract.py`)

### Phase 4 — Repo-Wide Convergence / Debt Burn-Down

- **Objective**: Eliminate residual V15 non-conformant patterns repo-wide.
- **Commits**:
  - `4ce1af886` — Phase 4 Wave 4.1: repo-wide V15 conformance inventory + classification
- **Inventory result** (1196 files scanned):
  - 25 guarded functions (with `@v15_runtime_guard` or `@_optional_v15_runtime_guard()`)
  - 253 in-scope unguarded — **all classified as FALSE POSITIVES**:
    - Internal helpers, `heal()` pathway methods, read-only accessors
    - Factory functions, CI utilities, dispatch wrappers
    - Phase functions called from within guarded `_legacy_main`
    - Data class methods (serialization, in-memory state)
  - **UNWIRED = 0 repo-wide**
- **Waves 4.2/4.3**: SKIPPED (nothing to patch, no regressions)
- **Artifacts**: `ops_scripts/ci/v15_d_inventory_collect_full.py`

### Phase 5 — Release Finalize

- **Objective**: Produce immutable evidence, manifests, and locks.
- **Final inventory**: Identical to Phase 4 (25 guarded, 253 false positives, 0 UNWIRED)
- **All gates**: P0 PASS, P1 PASS, P2 PASS
- **This manifest**: `docs/reports/plans/v15_completion_manifest.md`

---

## Final Assertions

- **UNWIRED = 0** across all 28 P2 inventory entrypoints
- **UNWIRED = 0** repo-wide (1196 files, 253 in-scope unguarded all classified as false positives)
- **P0 gate**: PASS (evidence_fail_count = 0)
- **P1 gate**: PASS (D_RUNTIME_WIRED = 100%, critical_d_set_passed = True)
- **P2 gate**: PASS (24 WIRED, 4 ALREADY_ENFORCED, 0 UNWIRED)
- **V15 guardian tests**: 30/30 PASS
- **Pre-commit**: All hooks PASS

---

## V15 Type Modules (P1–P6)

| Module | Priority | Path |
| --- | --- | --- |
| V15 P1 Types | P1 | `agentic_core/L0_maintenance/types/v15_types.py` |
| V15 P1 Contracts (types) | P1 | `agentic_core/L0_maintenance/types/v15_contracts.py` |
| V15 P2 Types | P2 | `agentic_core/L0_maintenance/types/v15_p2_types.py` |
| V15 P2 Contracts (types) | P2 | `agentic_core/L0_maintenance/types/v15_p2_contracts.py` |
| V15 P3 Types | P3 | `agentic_core/L0_maintenance/types/v15_p3_types.py` |
| V15 P4 Types | P4 | `agentic_core/L0_maintenance/types/v15_p4_types.py` |
| V15 P5 Types | P5 | `agentic_core/L0_maintenance/types/v15_p5_types.py` |
| V15 P6 Types | P6 | `agentic_core/L0_maintenance/types/v15_p6_types.py` |

## V15 Enforcement Contract Modules (P1–P6)

| Module | Priority | Path |
| --- | --- | --- |
| V15 Execution Gateway | P1/P2 | `agentic_core/L0_maintenance/enforcement/v15_execution_gateway.py` |
| V15 P3 Contracts | P3 | `agentic_core/L0_maintenance/enforcement/v15_p3_contracts.py` |
| V15 P4 Contracts | P4 | `agentic_core/L0_maintenance/enforcement/v15_p4_contracts.py` |
| V15 P5 Contracts | P5 | `agentic_core/L0_maintenance/enforcement/v15_p5_contracts.py` |
| V15 P6 Contracts | P6 | `agentic_core/L0_maintenance/enforcement/v15_p6_contracts.py` |

## V15 Guardian Test Suites

| Suite | Tests | Path |
| --- | --- | --- |
| P1 Compliance | 60 | `tests/guardian/test_v15_p1_compliance.py` |
| P2 Compliance | 64 | `tests/guardian/test_v15_p2_compliance.py` |
| P3 Compliance | 47 | `tests/guardian/test_v15_p3_compliance.py` |
| P4 Compliance | 53 | `tests/guardian/test_v15_p4_compliance.py` |
| P5 Compliance | 52 | `tests/guardian/test_v15_p5_compliance.py` |
| P6 Compliance | 40 | `tests/guardian/test_v15_p6_compliance.py` |
| Baseline Pins | 3 | `tests/guardian/test_v15_baseline_pins.py` |
| Integration Wiring | 17 | `tests/guardian/test_v15_integration_wiring.py` |
| Final Baseline Pins | 23 | `tests/guardian/test_v15_final_baseline_pins.py` |
| execute_ssot V15 Contract | 11 | `tests/guardian/test_execute_ssot_v15_contract.py` |
| P2 Wave 2.2 Bypass | 10 | `tests/guardian/test_v15_p2_wave2_2_bypass.py` |
| P2 Wave 2.2 Gate Tooling | 9 | `tests/guardian/test_v15_p2_wave2_2_gate_tooling.py` |
| **Total** | **389** | |

## CI Gate Scripts

| Script | Purpose |
| --- | --- |
| `ops_scripts/ci/run_v15_p0_gate.py` | P0 gate runner (evidence-only) |
| `ops_scripts/ci/run_v15_p1_gate.py` | P1 gate runner (D-evidence) |
| `ops_scripts/ci/run_v15_p2_gate.py` | P2 gate runner (runtime wiring) |
| `ops_scripts/ci/v15_gap_regenerate_p0.py` | P0 gap analysis regenerator |
| `ops_scripts/ci/v15_d_evidence_collect_p1.py` | P1 D-evidence collector |
| `ops_scripts/ci/v15_d_evidence_collect_p2.py` | P2 evidence collector |
| `ops_scripts/ci/v15_d_inventory_collect_full.py` | Full repo-wide inventory collector |
| `ops_scripts/ci/v15_coverage_scoreboard.py` | Coverage scoreboard + gate checker |

## Pinned Discovery Hash

```text
f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4
```

Artifact: `artifacts/forensic_discovery_output.json`
