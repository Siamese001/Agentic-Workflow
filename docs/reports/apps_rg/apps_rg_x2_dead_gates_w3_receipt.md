# apps_rg X2 dead gates — W3 receipt

**Plan:** [apps-rg-x2-dead-gates-burndown-c4e8f2.md](../../.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md)  
**Generated:** 2026-05-22

## W3 — Legacy proof-pool gate ID collapse

### Runtime

- `proof_pool_x2_gate_id()` always returns `x2_{section}_active_proof_pool_source_fact_ids` (retired `*_within_srfs_slice` branch removed).
- All seven section validators route through `proof_pool_x2_gate_id` (unify_bullets, competencies, ibm_bullets inlined branches collapsed).
- `evaluate_proof_pool_source_fact_gate()` sets `x2_srfs_gate_status` to `NOT_APPLICABLE` on product `evidence_authority` path; legacy SRFS pool type still sets `selected_role_fact_set_used` when applicable.
- `normalized_srfs_section_reporting_fields()` reads only the active proof-pool gate for SRFS reporting.
- `RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS` added to [section_product_shape_ssot.py](../../apps_rg/runtime/sections/section_product_shape_ssot.py); complexity audit flags stale bundle IDs.

### Proof

```text
pytest tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py tests/unit/apps_rg/test_product_evidence_authority_contract.py -> 56 passed
python ops_scripts/apps_rg/section_complexity_reduction_audit.py -> exit 0
python ops_scripts/apps_rg/section_authority_convergence_audit.py -> exit 0
```

Mock lane receipts assert `x2_*_active_proof_pool_source_fact_ids` only (no `within_srfs_slice` in `x2_gate_outputs.json`).

### Out of scope (deferred)

- `test_offline_stub_includes_srfs_slice_gate_pass` / `test_section_metric_receipt_w6_srfs_mode_all_fields` harness tests still expect removed CLI `selected_role_fact_set` wiring — refresh when SRFS CLI path is reattached or tests are retired.
