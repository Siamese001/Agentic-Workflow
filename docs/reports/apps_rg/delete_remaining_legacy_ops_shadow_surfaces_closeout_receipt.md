# Delete remaining legacy ops shadow surfaces — closeout

**PLAN_ID:** `delete-remaining-legacy-ops-shadow-surfaces`  
**STATUS:** PASS  
**Date:** 2026-05-20

## FILES_DELETED

- [prove_apps_rg_e2e_runtime.py](ops_scripts/ci/prove_apps_rg_e2e_runtime.py)
- [narrative_pass.py](ops_scripts/apps_rg/narrative_pass.py)

## HELPERS_MOVED

| Former location | New location |
|-----------------|--------------|
| `prove_apps_rg_e2e_runtime.py` boundary/persist helpers | [ci_lane_dev_boundary.py](tests/helpers/ci_lane_dev_boundary.py) |
| CI harness classification strings | [non_product_proof_stamp.py](apps_rg/runtime/non_product_proof_stamp.py) (`CI_LANE_DEV_HARNESS_CLASSIFICATION`, unchanged) |

`narrative_pass.py` had **no** remaining production imports (`NarrativePassStep` already skips when `narrative_adapter` is absent). No helper migration required.

## IMPORTS_REPOINTED

- [test_ci_rollup_not_product_certification.py](tests/unit/apps_rg/test_ci_rollup_not_product_certification.py) → `tests.helpers.ci_lane_dev_boundary`
- [test_apps_rg_e2e_boundary_hygiene.py](tests/_apps_contract/test_apps_rg_e2e_boundary_hygiene.py) → `tests.helpers.ci_lane_dev_boundary`
- [test_apps_rg_x1d_judge_execution_quality.py](tests/_apps_contract/test_apps_rg_x1d_judge_execution_quality.py) → `tests.helpers.ci_lane_dev_boundary`
- [test_dispatch_callers_are_canonical_only.py](tests/unit/apps_rg/test_dispatch_callers_are_canonical_only.py) — removed `prove_apps_rg_e2e_runtime.py` from allowed canonical caller list

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `python ops_scripts/ci/prove_apps_rg_e2e_runtime.py` | **2** — `can't open file` / No such file |
| `python ops_scripts/apps_rg/narrative_pass.py` | **2** — `can't open file` / No such file |
| `python -m apps_rg --help` | **0** |
| `pytest` regression bundle (112 tests) | **0** |

## GREP_PROOF

- `ops_scripts/`: **zero** references to deleted scripts (post-delete).
- `apps_rg/`: only [outside_main_entry_policy.py](apps_rg/runtime/outside_main_entry_policy.py) disallow-list entries and [RUNBOOK_E2E.md](apps_rg/runtime/RUNBOOK_E2E.md) deletion note (no `python ops_scripts/...` operator commands).
- [test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py](tests/_apps_contract/test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py) — **34 passed**.

## DIRECT_RUN_PROOF

- [test_legacy_ops_scripts_deleted.py](tests/unit/apps_rg/test_legacy_ops_scripts_deleted.py) — files absent; direct `python <path>` fails with file-not-found (not blocked-stub stderr).

## CANONICAL_PATH_CHECKS

- `python -m apps_rg --help` → exit **0**

## PRODUCT_PROOF_GUARD_REGRESSION

- [test_integrated_product_proof_gate.py](tests/unit/apps_rg/test_integrated_product_proof_gate.py) — passed in bundle
- SP-005 via [test_ci_rollup_not_product_certification.py](tests/unit/apps_rg/test_ci_rollup_not_product_certification.py) — passed
- [test_no_outside_main_runtime_entrypoints.py](tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py) — passed in bundle

## DISALLOWED_OUTSIDE_MAIN_EXECUTABLES_REMAINING

**NONE** (deleted scripts; no blocked `__main__` stubs)

## DEPRECATED_OR_BLOCKED_STUBS_REMAINING

**NONE**

## EXPLICIT_NON_CLAIMS

- No `agentic_core` edits for this plan
- No integrated R4 refactor
- No product/Fort Knox/L7 proof
- `NarrativePassStep` still skips when adapter missing (unchanged recipe behavior)

## NEXT_BLOCKER

None.
