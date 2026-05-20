# W10 — Exit / UWG / L4 / L6 No-Bypass Boundary Report

**Generated:** 2026-05-19  
**JSON:** [w10_exit_uwg_l4_l6_no_bypass.json](w10_exit_uwg_l4_l6_no_bypass.json)

## Plan sync

| Marker | Value |
|--------|-------|
| LAST_COMPLETED_WAVE | W10 |
| CURRENT_WAVE | W11 |
| W2–W5 receipt | [w2_w5_boundary_and_healing.md](w2_w5_boundary_and_healing.md) |
| W6–W9 receipt | [w6_w9_quarantine_and_e2_boundary.md](w6_w9_quarantine_and_e2_boundary.md) |

---

## W10 results (confidence)

| Boundary | Result | Confidence |
|----------|--------|------------|
| L2 → no direct L4 | PASS | HIGH |
| Exit X3 required | PASS | HIGH |
| UWG / L4 admission | PASS | HIGH |
| L6 current-run firewall | PASS | HIGH |
| Deprecated path no-bypass | PASS | HIGH |

**Behavior / runtime change:** none

---

## 1. L2 boundary

- [l2_phase_pipeline.py](../../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py): pipeline never writes L4/UWG.
- [DispatchReceipt](../../../agentic_core/L2_execution/types/l2_v3_receipts.py): `has_commit_payload=True` raises; default targets `exit_eval`, `uwg_decision`, `l6_audit`.
- [AttemptReceipt](../../../agentic_core/L2_execution/types/l2_v3_receipts.py): `proposed_state_diff` is an inert proposal at E3.

**Tests:** [test_l2_exit_uwg_l4_no_bypass_boundary.py](../../../tests/unit/agentic_core/test_l2_exit_uwg_l4_no_bypass_boundary.py)

---

## 2. Exit / X3 boundary

- Canonical lane bundle includes `x3_disposition.json` ([run_bundle_index.py](../../../apps_rg/runtime/run_bundle_index.py)).
- [review_lane_policy.py](../../../apps_rg/runtime/aggregation/review_lane_policy.py): product ALLOW requires `X3_ALLOW` + `REAL_LLM`; mock/stub statuses excluded.
- [exit_binding.py](../../../apps_rg/runtime/bindings/exit_binding.py): `exit_finalize_apps_rg` → `X3Disposition`; inert commit candidate pattern.
- Regression: [test_gap001_exit_l4_boundary_hardening.py](../../../tests/_apps_contract/test_gap001_exit_l4_boundary_hardening.py).

**Tests:** [test_apps_rg_exit_uwg_l4_no_bypass_boundary.py](../../../tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py)

---

## 3. UWG / L4 boundary

- [universal_write_gate.py](../../../agentic_core/runtime/uwg/universal_write_gate.py): sole durable admission façade; blocks direct writes from L2/Exit/L6.
- [future_run_promotion.py](../../../agentic_core/runtime/contracts/future_run_promotion.py): `current_run_mutation_allowed=False`, `requires_uwg=True` structurally enforced.

**Confidence note:** W10 proves documented contracts + gate classes; full runtime fan-in to `UniversalWriteGate.admit()` is **MEDIUM** until ADG/runtime trace (W11 planning).

---

## 4. L6 firewall

- [g29_learning_firewall.py](../../../agentic_core/L5_safety/runtime_gates/g29_learning_firewall.py): DENY on current-run mutation; BLOCK_COMMIT on L6→L4 direct write.
- [runtime_artifact_validators.py](../../../tests/fixtures/proof_evidence/runtime_artifact_validators.py): `assert_l6_eval_no_current_run_mutation`.

**Tests:** [test_l6_current_run_learning_firewall_boundary.py](../../../tests/unit/agentic_core/test_l6_current_run_learning_firewall_boundary.py)

---

## 5. Deprecated path no-bypass

Non-product / quarantine paths cannot satisfy product ALLOW or bypass UWG:

- `dry_run/`, `RgResumeOrchestrator.py`, `apps_rg_l2_binding` shim
- `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB`, `stub_only`, `legacy_full_resume`
- Legacy `runtime/dispatch/*_dispatch.py` → `exit_deprecated_dispatch_cli`

Cross-ref: [w6_w9_quarantine_and_e2_boundary.md](w6_w9_quarantine_and_e2_boundary.md)

---

## Test evidence

| Command | Result |
|---------|--------|
| W10 new tests + orchestration | 32 passed |
| Broad filtered contract/unit suites | NOT_RUN_SLOW |

---

## W11 readiness

W10 guardrails are in place for gated archive planning. W11 still requires:

1. ADG fan-in zero on RETIRE_CANDIDATE paths (shim, Rg*, deprecated dispatch)
2. Migration receipt under `artifacts/governance/migration_receipts/`
3. Author-Gate for any test/CI import path changes

---

## Explicit non-claims

- No deletes, archives, or deprecation markers
- No live apps_rg proof
- Static/grep evidence ≠ runtime reachability proof
