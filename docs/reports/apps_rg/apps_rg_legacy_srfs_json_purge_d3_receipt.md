# apps_rg legacy SRFS JSON purge — D3 receipt

**Plan:** [apps-rg-legacy-srfs-json-purge-a8f3c1.md](../../.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)  
**Generated:** 2026-05-22

## D3 — Delete SRFS receipt aggregator + metadata purge

### Deleted

- [srfs_receipt_aggregator.py](../../apps_rg/audit/srfs_receipt_aggregator.py) — cross-section SRFS structural audit CLI (~26K LOC)
- [srfs_audit_advisory_judge.py](../../apps_rg/audit/srfs_audit_advisory_judge.py) — advisory judge layer for aggregator
- [test_apps_rg_srfs_aggregator.py](../../tests/_apps_contract/test_apps_rg_srfs_aggregator.py) — W5 aggregator contract tests (18 cases)

### Policy / inventory

- [__init__.py](../../apps_rg/audit/__init__.py) — empty exports; documents D3 removal
- [outside_main_entry_policy.py](../../apps_rg/runtime/outside_main_entry_policy.py) — removed from `ALLOWED_OUTSIDE_MAIN_MODULE_CLI`; added to `DELETED_RUNTIME_MODULE_CLI`
- [audit_post_section_aggregation_readiness.py](../../tools/apps_rg/audit_post_section_aggregation_readiness.py) — aggregator marked `REMOVED_D3_legacy_srfs_structural_audit`

### Metadata / reporting (product path)

- [selected_role_fact_set.py](../../apps_rg/runtime/sections/selected_role_fact_set.py):
  - Deleted `broad_skills_ledger_proof_pool_metadata`
  - `graph_only_proof_pool_metadata` no longer emits `broad_skills_ledger_*` authority switches
  - `normalized_srfs_section_reporting_fields` always uses `product_authority_reporting_fields`; legacy SRFS-active branch removed; `out_of_slice_fact_ids` copied from active proof-pool X2 gate only

### Tests

- [test_apps_rg_srfs_w6_reporting.py](../../tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py):
  - SRFS JSON CLI integration tests skipped (D2/D3)
  - Normalizer unit tests rewritten for graph `evidence_authority` + `x2_active_proof_pool_gate_status`

### Proof

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout \
  tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py::test_deleted_runtime_module_cli_missing \
  tests/unit/apps_rg/test_product_evidence_authority_contract.py::test_normalized_reporting_never_marks_srfs_authority \
  tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py::test_w6_normalizer_pass_path_matches_gate_envelope \
  tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py::test_w6_normalizer_unify_bullets_fail_out_of_slice \
  tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py::test_w6_normalizer_unify_narrative_fail_out_of_slice \
  tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py::test_w6_normalizer_competencies_fail_out_of_slice \
  tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py \
  tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py \
  -> 48 passed
```

`python -m apps_rg.audit.srfs_receipt_aggregator` → `No module named` (deleted CLI).

### Deferred (D4–D5)

- `srfs_proof_pool_metadata`, `srfs_present` on `SectionProofPool` dataclass (receipt labels only)
- ~~exec_summary_graph_projection_w4b~~ arsenal folded D4; PA `srfs_integration` reads remain D5
- PA/capsule `srfs_integration` reads
