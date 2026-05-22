# apps_rg legacy SRFS JSON purge — D4 receipt

**Plan:** [apps-rg-legacy-srfs-json-purge-a8f3c1.md](../../.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)  
**Generated:** 2026-05-22

## D4 — Fact inventory: graph projection SSOT + offline JSON gate

### Folded / deleted

- **Deleted** [exec_summary_srfs_arsenal.py](../../apps_rg/fact_inventory/exec_summary_srfs_arsenal.py) — arsenal ranking merged into [exec_summary_graph_projection_w4b.py](../../apps_rg/fact_inventory/exec_summary_graph_projection_w4b.py) (graph projection SSOT for exec-summary fact reservation + W4B offline inspection)

### Runtime / inventory

- [selected_role_fact_set.py](../../apps_rg/fact_inventory/selected_role_fact_set.py) (fact_inventory):
  - `select_candidate_facts_for_role` imports arsenal helpers from `exec_summary_graph_projection_w4b` (in-memory only)
  - `write_selected_role_fact_set_artifacts` fail-closed unless `APPS_RG_OFFLINE_SRFS_JSON_WRITE=1` (offline CLI only)
- [select_role_facts.py](../../apps_rg/fact_inventory/select_role_facts.py) — sets `APPS_RG_OFFLINE_SRFS_JSON_WRITE=1` before JSON write
- [exec_summary_graph_projection_w4b.py](../../apps_rg/fact_inventory/exec_summary_graph_projection_w4b.py):
  - W4B inspection uses graph `proof_pool_metadata` only (no `srfs_integration` envelope, no JSON artifact path authority)
  - `product_visible=False` for offline prompt compile
  - Appends forbidden-phrase contract block for W4B audit parity on graph path

### Import updates

- [validate_commercial_srfs_projection.py](../../apps_rg/fact_inventory/validate_commercial_srfs_projection.py)
- [test_exec_summary_srfs_arsenal_wiring.py](../../tests/unit/apps_rg/fact_inventory/test_exec_summary_srfs_arsenal_wiring.py)
- [test_selected_role_fact_set_contract.py](../../tests/_apps_contract/test_selected_role_fact_set_contract.py)

### Proof

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout \
  tests/unit/apps_rg/fact_inventory/test_exec_summary_graph_projection_w4b.py \
  tests/unit/apps_rg/fact_inventory/test_exec_summary_srfs_arsenal_wiring.py \
  tests/_apps_contract/test_selected_role_fact_set_contract.py::test_write_selected_role_fact_set_roundtrip_schema \
  tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py \
  -> 31 passed
```

Product path: `resolve_section_proof_pool` → `select_candidate_facts_for_role` (in-memory); no `write_selected_role_fact_set_artifacts` on lane hot path.

### Deferred (D5)

- PA/capsule `srfs_integration` reads and prompt vocabulary purge
- `selected_role_fact_set_active.json` as required runtime path
