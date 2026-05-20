# Hard-delete outside-main runtime entrypoints — closeout receipt

**PLAN_ID:** hard-delete-outside-main-runtime-entrypoints  
**STATUS:** PASS

## SCOPE_MATCH

Physical removal or internalization of shadow `apps_rg.runtime.*` CLIs; canonical entry remains `python -m apps_rg` / `python -m apps_rg --section <lane>`; no `refuse_runtime_module_cli` stubs; no deprecated exit-2 dispatch CLIs.

## SCOPE_DRIFT

- `ops_scripts/ci/prove_apps_rg_e2e_runtime.py` retained as **import-only** lane-dev harness (direct `__main__` exits 1); not deleted because unit/contract tests import `main()`.
- `ops_scripts/apps_rg/narrative_pass.py` retained for `apps_rg.l2_recipe` / narrative adapter imports; direct script execution exits 1 (not deleted).

## FILES_DELETED

- [headline_dispatch.py](apps_rg/runtime/dispatch/headline_dispatch.py)
- [executive_summary_demo.py](apps_rg/runtime/dry_run/executive_summary_demo.py) (prior wave)
- [generate_resume.py](ops_scripts/apps_rg/generate_resume.py)

## FILES_CHANGED

- [outside_main_entry_policy.py](apps_rg/runtime/outside_main_entry_policy.py) — deleted-module registry; removed refuse stubs
- [lane_batch.py](apps_rg/runtime/internal/lane_batch.py) — moved from `orchestrate_full_resume.py`; lanes via `python -m apps_rg --section` subprocess only
- [resume_package_disposition.py](apps_rg/runtime/internal/resume_package_disposition.py) — moved from `package/resume_package_x3.py`
- [generated_lane_rollup.py](apps_rg/runtime/internal/generated_lane_rollup.py)
- [final_resume_assembler.py](apps_rg/runtime/internal/final_resume_assembler.py)
- [locked_copy_builder.py](apps_rg/runtime/internal/locked_copy_builder.py)
- [docx_renderer.py](apps_rg/runtime/internal/docx_renderer.py)
- [docx_manifest_builder.py](apps_rg/runtime/internal/docx_manifest_builder.py)
- Legacy [dispatch](apps_rg/runtime/dispatch/) lane modules — removed `main` / `run_dispatch` / `__main__`
- [prove_apps_rg_e2e_runtime.py](ops_scripts/ci/prove_apps_rg_e2e_runtime.py) — blocked direct execution; rollup import fixed
- [narrative_pass.py](ops_scripts/apps_rg/narrative_pass.py) — blocked direct execution
- [RUNBOOK_E2E.md](apps_rg/runtime/RUNBOOK_E2E.md) — canonical CLI only
- Contract tests under [tests/_apps_contract](tests/_apps_contract/) and [tests/unit/apps_rg](tests/unit/apps_rg/)

## HELPERS_MOVED

| Former path | Internal path |
|-------------|---------------|
| `apps_rg/runtime/orchestrate_full_resume.py` | `apps_rg/runtime/internal/lane_batch.py` |
| `apps_rg/runtime/package/resume_package_x3.py` | `apps_rg/runtime/internal/resume_package_disposition.py` |
| `apps_rg/runtime/reports/generated_lane_rollup.py` | `apps_rg/runtime/internal/generated_lane_rollup.py` |
| `apps_rg/runtime/assembly/final_resume_assembler.py` | `apps_rg/runtime/internal/final_resume_assembler.py` |
| `apps_rg/runtime/locked_copy/locked_copy_builder.py` | `apps_rg/runtime/internal/locked_copy_builder.py` |
| `apps_rg/runtime/render/docx_renderer.py` | `apps_rg/runtime/internal/docx_renderer.py` |
| `apps_rg/runtime/render/docx_manifest_builder.py` | `apps_rg/runtime/internal/docx_manifest_builder.py` |

## MODULE_ENTRYPOINTS_REMOVED

All `if __name__ == "__main__"` blocks removed from `_offline` post-lane modules and legacy `*_dispatch.py` modules (except canonical [apps_rg_dispatch.py](apps_rg/runtime/dispatch/apps_rg_dispatch.py) bridge). `main()` / `run_dispatch()` removed from lane dispatch modules.

## DOCS_REPOINTED

- [RUNBOOK_E2E.md](apps_rg/runtime/RUNBOOK_E2E.md)
- Bulk import/doc path updates (349 files) from module moves

## CI_REPOINTED_OR_DELETED

- [prove_apps_rg_e2e_runtime.py](ops_scripts/ci/prove_apps_rg_e2e_runtime.py): lanes already `python -m apps_rg --section`; direct script run blocked (exit 1)

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `python -m apps_rg.runtime.orchestrate_full_resume` | 1 (No module named …) |
| `python -m apps_rg.runtime.dry_run.executive_summary_demo` | 1 (No module named …) |
| `python -m apps_rg.runtime.package.resume_package_x3` | 1 (No module named …) |
| `python -m apps_rg.runtime.reports.generated_lane_rollup` | 1 (No module named …) |
| `python -m apps_rg.runtime.sections.executive_summary_lane_api` | 0 (import-only; no `main`) |
| `python ops_scripts/apps_rg/narrative_pass.py` | 1 (retired message) |
| `python ops_scripts/ci/prove_apps_rg_e2e_runtime.py` | 1 (retired message) |
| `python -m apps_rg --help` | 0 |
| `python -m apps_rg --section executive_summary --dry-run` (Brown & Brown fixtures) | 0 |
| `python -m apps_rg.runtime.integrated_product_proof_gate --help` | 0 |
| `pytest` hard-delete bundle (116 tests) | 0 |

## DIRECT_MODULE_DELETION_PROOF

Deleted historical module names raise `ModuleNotFoundError` on `python -m` (see table above).

## GREP_PROOF

`test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py` — PASS over `apps_rg/`, `ops_scripts/`, `.cursor/rules/`.

## CALLER_GATE_PROOF

`test_dispatch_callers_are_canonical_only.py` — PASS (`dispatch_apps_rg_run` and `run_canonical_apps_rg_from_cli_primitives` callers constrained).

## PRODUCT_PROOF_GUARD_REGRESSION

`tests/unit/apps_rg/test_integrated_product_proof_gate.py` — PASS (section-only / offline rollup / package-x3 / demo / CI lane-dev historical artifacts rejected).

## CANONICAL_COMMAND_CHECKS

`python -m apps_rg --help` and section dry-run with JD/brief fixtures — PASS (exit 0).

## ALLOWED_OUTSIDE_MAIN_EXECUTABLES

- `apps_rg.runtime.integrated_product_proof_gate`
- `apps_rg.runtime.validators.validate_exec_summary_graph_only_generation`
- `apps_rg.runtime.prepare_orchestrator_inputs`
- `apps_rg.audit.srfs_receipt_aggregator`
- `apps_rg.fact_inventory.*` (prefix)

## DISALLOWED_OUTSIDE_MAIN_EXECUTABLES_REMAINING

**NONE** for `apps_rg.runtime.*` product/section CLI surfaces. Legacy ops scripts are blocked on direct execution, not allowlisted as product proof.

## DEPRECATED_STUBS_REMAINING

**NONE** (`refuse_runtime_module_cli` / exit-2 deprecated dispatch stubs removed).

## LEGACY_OPS_STATUS

| Script | Status |
|--------|--------|
| [generate_resume.py](ops_scripts/apps_rg/generate_resume.py) | **DELETED** |
| [narrative_pass.py](ops_scripts/apps_rg/narrative_pass.py) | **BLOCKED** on direct run (still imported by recipe adapter) |
| [prove_apps_rg_e2e_runtime.py](ops_scripts/ci/prove_apps_rg_e2e_runtime.py) | **BLOCKED** on direct run (importable for tests) |

## PROTECTED_PATHS_TOUCHED

- [apps_rg/__main__.py](apps_rg/__main__.py) — docstring only (prior wave)
- [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) — unchanged logic
- [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) — unchanged allowlisted CLI

## FORBIDDEN_FILES_TOUCHED

None under `agentic_core/`.

## EXPLICIT_NON_CLAIMS

- No `agentic_core` edits
- No integrated R4 refactor
- No product / Fort Knox / L7 proof claimed
- No section-only proof upgraded
- Package disposition JSON family `resume_package_x3` is **not** Exit X3

## NEXT_BLOCKER

None for this plan. Follow-up (optional): migrate `narrative_pass` recipe binding off [narrative_pass.py](ops_scripts/apps_rg/narrative_pass.py) so the file can be deleted entirely.
