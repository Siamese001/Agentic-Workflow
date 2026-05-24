# dry_run importer inventory (2026-05-24)

**Plan:** `apps-rg-dry-run-migrate-delete-b9e4f2`  
**Pre-delete module:** `apps_rg/runtime/dry_run/executive_summary_demo.py`  
**Replacement:** `tests/fixtures/apps_rg/demo_harness_fixture.py`

## Product importers

_none_

## Test / fixture consumers (migrated)

| File | Usage |
|------|--------|
| `tests/unit/apps_rg/test_demo_harness_fail_closed.py` | `python -m` subprocess |
| `tests/unit/apps_rg/test_section_evidence_w7a_shadow_proof_boundary.py` | subprocess + `run_demo_harness` import |
| `tests/unit/apps_rg/test_integrated_lane_evidence_packaging.py` | asserts demo not in evidence tree |
| `tests/unit/apps_rg/test_integrated_product_proof_gate.py` | `demo_harness_non_product_stamp` |

## Contract / boundary lists (updated post-delete)

| File | Change |
|------|--------|
| `tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py` | `dry_run/` removed from KEEP registry; absent-path test |
| `tests/_apps_contract/test_apps_rg_canonical_runtime_hygiene.py` | marker → `tests/fixtures/apps_rg/` |
| `tests/_apps_contract/test_apps_rg_generation_model_env_boundary.py` | prefix removed |
| `tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py` | path removed |
| `tests/unit/apps_rg/test_dispatch_callers_are_canonical_only.py` | forbidden suffix removed |

## Policy / CI (updated)

| File | Change |
|------|--------|
| `apps_rg/runtime/outside_main_entry_policy.py` | removed `python -m apps_rg.runtime.dry_run.` |
| `apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py` | keeps `executive_summary_demo` as deprecated artifact marker |
| `ops_scripts/ci/check_quarantine_ssot.py` | `dry_run` → REMOVED_PATHS |
| `ops_scripts/ci/check_apps_rg_runtime_path_inventory.py` | `dry_run/` removed from NON_PRODUCT_DIRS |

## Verdict

`C1_dry_run` → **DELETE_READY** after migration (test-only importers cleared from product tree).
