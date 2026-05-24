# Quarantine SSOT reconcile (2026-05-24)

**Plan:** [apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md](../../.cursor/plans/apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md)  
**Supersedes (partial):** [apps_rg_quarantine_u0_packet_coverage_audit.md](../../artifacts/apps_rg/apps_rg_quarantine_u0_packet_coverage_audit.md) (W4 stub-in-place model)

## Executive summary

| Area | W4 audit claim | Disk 2026-05-24 | W1 action |
|------|----------------|-----------------|-----------|
| `apps_rg/_quarantine/` | 3 inert stubs | **Absent** | Tests/CI → assert removed |
| `apps_rg/reasoning/` | 18 quarantined agents | **Absent** | Tests/CI → assert removed |
| `integrations/gates/online_judges` | QUARANTINE stub | **Absent** | Import tests → `ModuleNotFoundError` |
| `integrations/hops/` | 13 QUARANTINE stubs | **Live** (`_llm_client.py`) | AG-RGGOV-8 → spine must not import hops |
| `apps_rg/engines/` | 42 quarantined | **4 live modules** + unit tests | **KEEP** — not delete-ready |
| `runtime/dry_run/` | Demo quarantine | **Live** `executive_summary_demo.py` | **KEEP** until harness tests migrate |
| `runtime/internal/` | offline orchestrator | **5 helper modules** | **KEEP** — product recipe imports |

## SSOT hierarchy (use in order)

1. **Runtime path registry (W7):** [test_apps_rg_deprecated_path_quarantine.py](../../tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py)
2. **Delete authorization (W11):** [w11_gated_archive_delete_plan.md](../agent_inventory/w11_gated_archive_delete_plan.md) DELETE_GATE
3. **Fan-in matrix:** [quarantine_fanin_matrix_20260524.json](../../artifacts/governance/quarantine_fanin_matrix_20260524.json)
4. **Narrow CI gate:** [check_quarantine_ssot.py](../../ops_scripts/ci/check_quarantine_ssot.py)

## Contract test changes (W1.3)

- [test_quarantined_paths_raise_runtime_error.py](../../tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py) — retired modules assert `ModuleNotFoundError`, not `RuntimeError(QUARANTINE)`
- [test_w4_quarantine_bypass.py](../../tests/_apps_contract/test_w4_quarantine_bypass.py) — hops: spine isolation, not import block
- [test_import_graph_no_quarantine.py](../../tests/_apps_contract/test_import_graph_no_quarantine.py) — retired paths must be absent on disk

## CI inventory note

[check_apps_rg_runtime_path_inventory.py](../../ops_scripts/ci/check_apps_rg_runtime_path_inventory.py) still enforces broad `__main__.py` import allowlist (pre-existing FAIL unrelated to quarantine). Use `check_quarantine_ssot.py` for this plan's proof.
