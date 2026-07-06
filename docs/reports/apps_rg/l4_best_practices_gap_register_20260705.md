# apps_rg L4 Best-Practices Gap Register

Plan ID: `apps-rg-l4-best-practices-hardening`
Owner: Codex
Baseline date: 2026-07-06
ADG Provenance: backend=sqlite+redis, snapshot=adg_indexed_07052026_2301.sqlite

## Scope

This register tracks R1B semantic-cache durable-write hardening across
`apps_rg/cache/*` and `agentic_core/L4_state/*`. The priority rule is
fail-closed over cache reuse.

## Gaps

| Gap | Severity | Runtime Risk | Files | Test Target |
|---|---:|---|---|---|
| L4-RG-001 | P0 | Missing derived index can consult fixture mirror and produce a runtime hit. | `apps_rg/cache/r1b_derived_index.py`, `apps_rg/cache/r1b_whole_run_preflight.py`, `apps_rg/cache/whole_run_entrypoint_preflight.py` | `tests/unit/apps_rg/test_r1b_no_fixture_read_fallback.py` |
| L4-RG-002 | P0 | Blocked/non-admitted candidates can still be mirrored into fixture state. | `apps_rg/cache/r1b_post_exit_ingest.py`, `apps_rg/cache/r1b_uwg_promotion.py`, `apps_rg/cache/r1b_store.py` | `tests/unit/apps_rg/test_r1b_fixture_quarantine.py` |
| L4-RG-003 | P0 | apps_rg monkeypatches core `UWGCommitReceipt` construction to carry L5 evidence. | `apps_rg/cache/r1b_uwg_promotion.py`, `apps_rg/cache/r1b_uwg_receipt_contract.py`, `agentic_core/L4_state/contracts/records.py`, `agentic_core/L4_state/uwg/durable_write_gateway.py` | `tests/unit/agentic_core/L4_state/uwg_acceptance/test_uwg_commit_receipt_parity.py` |
| L4-RG-004 | P1 | UWG validation does not fail closed on all clearance, registry, signature, staged-diff, and certification gaps. | `agentic_core/L4_state/uwg/durable_write_gateway.py`, `agentic_core/L4_state/contracts/records.py`, `apps_rg/cache/r1b_uwg_promotion.py` | `tests/unit/agentic_core/L4_state/uwg_acceptance/test_uwg_validation_fail_closed.py` |
| L4-RG-005 | P1 | Audit append evidence is monotonic but not hash-chained. | `agentic_core/L4_state/audit/audit_ledger.py`, `agentic_core/L4_state/contracts/records.py` | `tests/unit/agentic_core/L4_state/uwg_acceptance/test_audit_hash_chain.py` |
| L4-RG-006 | P1 | R1B projection/index refresh is local apps_rg state after commit, not a canonical refresh receipt chain. | `apps_rg/cache/r1b_uwg_promotion.py`, `apps_rg/cache/r1b_derived_index.py`, `agentic_core/L4_state/refresh/refresh_coordinator.py` | `tests/unit/apps_rg/test_r1b_read_surface_refresh_receipts.py` |
| L4-RG-007 | P1 | CI does not block fixture fallback, receipt monkeypatch, audit-chain absence, or sidecar-only provenance regressions. | `ops_scripts/ci/run_contract_gates.py`, `ops_scripts/ci/check_apps_rg_l4_best_practices.py` | `tests/unit/apps_rg/test_apps_rg_l4_best_practices_gate.py` |
| L4-RG-008 | P2 | Durable R1B bundles do not carry full lifecycle/retention/migration evidence. | `apps_rg/cache/r1b_uwg_promotion.py`, `apps_rg/cache/r1b_derived_index.py`, `agentic_core/L4_state/enforcement/state_lifecycle_policy.py` | `tools/apps_rg/migrate_r1b_durable_projection_receipts.py` |

## Baseline Evidence

Baseline command outputs and exit codes are recorded under
`artifacts/apps_rg/l4_best_practices/`. W0 intentionally changes only
documentation and evidence artifacts.
