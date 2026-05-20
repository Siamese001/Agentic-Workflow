# Hard-delete residual shadow module paths — closeout

**PLAN_ID:** `hard-delete-residual-shadow-module-paths`  
**STATUS:** PASS  
**Date:** 2026-05-20

## SCOPE_MATCH

- Physical removal of `apps_rg.runtime.dispatch.*_dispatch` shadow modules (not stubs).
- `_offline/` tree eliminated; helpers live under `apps_rg.runtime.internal.*` with non-CLI guards.
- Old shadow dotted paths (`orchestrate_full_resume`, `package.resume_package_x3`, `reports.generated_lane_rollup`, `assembly.final_resume_assembler`, `render.docx_renderer`, `locked_copy.locked_copy_builder`, `dry_run.executive_summary_demo`) no longer importable.
- Lane helpers moved to `apps_rg.runtime.sections.*_lane_api` (no `python -m` exit 0).
- Fail-closed `deprecated_runtime_cli.py` removed; `run_dispatch_main` raises `ImportError`.
- Protected paths untouched (`apps_rg/__main__.py`, `canonical_dispatch`, product proof gate, section lanes).

## SCOPE_DRIFT

- Large repo-wide import migration via `tools/cursor/migrate_shadow_import_paths.py` (mechanical `_offline` → `internal`, `dispatch.*_dispatch` → `sections.*_lane_api`).
- `agentic_core` and unrelated workspace files remain modified from prior workstreams — **not claimed** as part of this plan.

## FILES_DELETED

- [headline_dispatch.py](apps_rg/runtime/dispatch/headline_dispatch.py)
- [deprecated_runtime_cli.py](apps_rg/runtime/deprecated_runtime_cli.py)
- [executive_summary_demo.py](apps_rg/runtime/dry_run/executive_summary_demo.py)
- [generate_resume.py](ops_scripts/apps_rg/generate_resume.py) (prior wave; confirmed absent)
- All `apps_rg/runtime/dispatch/*_dispatch.py` lane shadow files (moved, not retained at old paths)
- Entire `apps_rg/runtime/_offline/` tree (renamed to `internal/`)

## FILES_CHANGED

- [outside_main_entry_policy.py](apps_rg/runtime/outside_main_entry_policy.py) — deleted-module registry + doc/CI disallow list
- [modular_lane_adapter.py](apps_rg/l2_recipe/modular_lane_adapter.py) — `run_dispatch_main` retired (`ImportError`)
- [modular_resume_generation.py](apps_rg/l2_recipe/modular_resume_generation.py) — lane module paths → `sections.*_lane_api`
- [RUNBOOK_E2E.md](apps_rg/runtime/RUNBOOK_E2E.md) — canonical operator commands only
- [internal/](apps_rg/runtime/internal/) — post-lane helpers (no `main()`, top-of-file `__main__` guard)
- [sections/*_lane_api.py](apps_rg/runtime/sections/) — lane API surface (import-only; `-m` raises `ImportError`)
- Contract tests under [tests/_apps_contract/](tests/_apps_contract/) and [tests/unit/apps_rg/](tests/unit/apps_rg/)

## HELPERS_MOVED

| Old path | New path |
|----------|----------|
| `apps_rg.runtime.dispatch.executive_summary_dispatch` | [executive_summary_lane_api.py](apps_rg/runtime/sections/executive_summary_lane_api.py) |
| `apps_rg.runtime.dispatch.competencies_dispatch` | [competencies_lane_api.py](apps_rg/runtime/sections/competencies_lane_api.py) |
| `apps_rg.runtime.dispatch.unify_bullets_dispatch` | [unify_bullets_lane_api.py](apps_rg/runtime/sections/unify_bullets_lane_api.py) |
| `apps_rg.runtime.dispatch.unify_narrative_dispatch` | [unify_narrative_lane_api.py](apps_rg/runtime/sections/unify_narrative_lane_api.py) |
| `apps_rg.runtime.dispatch.ibm_bullets_dispatch` | [ibm_bullets_lane_api.py](apps_rg/runtime/sections/ibm_bullets_lane_api.py) |
| `apps_rg.runtime.dispatch.ibm_narrative_dispatch` | [ibm_narrative_lane_api.py](apps_rg/runtime/sections/ibm_narrative_lane_api.py) |
| `apps_rg.runtime.orchestrate_full_resume` | [lane_batch.py](apps_rg/runtime/internal/lane_batch.py) |
| `apps_rg.runtime.reports.generated_lane_rollup` | [generated_lane_rollup.py](apps_rg/runtime/internal/generated_lane_rollup.py) |
| `apps_rg.runtime.assembly.final_resume_assembler` | [final_resume_assembler.py](apps_rg/runtime/internal/final_resume_assembler.py) |
| `apps_rg.runtime.package.resume_package_x3` | [resume_package_disposition.py](apps_rg/runtime/internal/resume_package_disposition.py) |
| `apps_rg.runtime.render.docx_renderer` | [docx_renderer.py](apps_rg/runtime/internal/docx_renderer.py) |
| `apps_rg.runtime.render.docx_manifest_builder` | [docx_manifest_builder.py](apps_rg/runtime/internal/docx_manifest_builder.py) |
| `apps_rg.runtime.locked_copy.locked_copy_builder` | [locked_copy_builder.py](apps_rg/runtime/internal/locked_copy_builder.py) |

## IMPORTS_REPOINTED

- Mechanical migration across apps_rg, tests, ops_scripts, and docs (excluding historical `docs/reports/**` evidence).

## OLD_DISPATCH_MODULES_REMOVED

Retired files absent from [dispatch/](apps_rg/runtime/dispatch/); only [apps_rg_dispatch.py](apps_rg/runtime/dispatch/apps_rg_dispatch.py) remains as `*_dispatch.py`.

## OFFLINE_MODULES_REMOVED_OR_CLASSIFIED

- `_offline/` **removed** (0 files).
- [internal/](apps_rg/runtime/internal/) — **pure helpers**, classified `TEST_SUPPORT_ONLY` / in-process post-lane only:
  - No `def main()` in any internal module.
  - Top-of-file guard: `python -m apps_rg.runtime.internal.<module>` → **exit 1** + `ImportError` (not exit 0).

## LEGACY_OPS_DELETION_STATUS

| Script | Status |
|--------|--------|
| [generate_resume.py](ops_scripts/apps_rg/generate_resume.py) | **Deleted** |
| [prove_apps_rg_e2e_runtime.py](ops_scripts/ci/prove_apps_rg_e2e_runtime.py) | **BLOCKED on direct run** (exit **1**); `main()` importable for unit tests |
| [narrative_pass.py](ops_scripts/apps_rg/narrative_pass.py) | **BLOCKED on direct run** (exit **1**); recipe imports only |

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `git status --short` | 0 |
| `Get-ChildItem apps_rg/runtime/dispatch -Filter *_dispatch.py` | only `apps_rg_dispatch.py` |
| `Get-ChildItem apps_rg/runtime/internal -Filter *.py` | 7 modules (+ `__init__.py`) |
| `python -m apps_rg --help` | **0** |
| `python -m apps_rg --section executive_summary --dry-run` | **2** (missing targeting — canonical path reached) |
| `python -m apps_rg.runtime.orchestrate_full_resume` | **1** (No module named) |
| `python -m apps_rg.runtime.dispatch.executive_summary_dispatch` | **1** (No module named) |
| `python -m apps_rg.runtime.dispatch.competencies_dispatch` | **1** (No module named) |
| `python -m apps_rg.runtime._offline.lane_batch` | **1** (No module named `_offline`) |
| `python -m apps_rg.runtime.internal.lane_batch` | **1** (ImportError guard) |
| `python -m apps_rg.runtime.internal.docx_renderer` | **1** (ImportError guard) |
| `python -m apps_rg.runtime.sections.executive_summary_lane_api` | **1** (ImportError guard) |
| `python ops_scripts/ci/prove_apps_rg_e2e_runtime.py` | **1** |
| `python ops_scripts/apps_rg/narrative_pass.py` | **1** |
| `pytest` shadow + SP + product-proof bundle (see below) | **0** |

## DIRECT_MODULE_PROOF

All retired shadow `python -m` paths return **non-zero**; none return import-only **exit 0**.

## GREP_PROOF

- Active scan roots (`apps_rg/`, `ops_scripts/`, `.cursor/rules/`): **zero** disallowed operator substrings (`test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py` — **34 passed**).
- Historical strings remain only in `docs/reports/**` audit receipts (excluded by policy).

## IMPORT_ABSENCE_PROOF

- `test_shadow_dispatch_modules_deleted.py` — retired `*_dispatch.py` files absent; import `ModuleNotFoundError`.
- `test_retired_dispatch_module_paths_removed` in deprecated-path quarantine.

## CANONICAL_PATH_CHECKS

- `python -m apps_rg --help` → exit **0**
- `python -m apps_rg --section executive_summary --dry-run` → exit **2** (expected preflight/targeting block, not shadow path)

## PRODUCT_PROOF_GUARD_REGRESSION

`pytest` bundle (**108 passed**):

- [test_no_outside_main_runtime_entrypoints.py](tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py)
- [test_shadow_dispatch_modules_deleted.py](tests/unit/apps_rg/test_shadow_dispatch_modules_deleted.py)
- [test_integrated_product_proof_gate.py](tests/unit/apps_rg/test_integrated_product_proof_gate.py)
- SP-001 … SP-005 + [test_apps_rg_exit_uwg_l4_no_bypass_boundary.py](tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py)

## DISALLOWED_EXIT_0_IMPORT_ONLY_MODULES_REMAINING

**NONE**

## DEPRECATED_RUNNABLE_STUBS_REMAINING

**NONE** (`deprecated_runtime_cli.py` deleted; no fail-closed dispatch `-m` stubs)

## BLOCKERS

None for this plan scope.

## PROTECTED_PATHS_TOUCHED

- [apps_rg/__main__.py](apps_rg/__main__.py) — prior convergence only (canonical CLI preserved)
- [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py) — import path updates only
- Section lane implementations — import repoints to `*_lane_api` / `internal`

## FORBIDDEN_FILES_TOUCHED

None intentionally (no `agentic_core` edits claimed for this plan).

## EXPLICIT_NON_CLAIMS

- No `agentic_core` spine refactor or certification
- No integrated R4 product/Fort Knox/L7 proof
- No section-only proof upgraded to product proof
- No package X3 rollup treated as Exit X3
- `prove_apps_rg_e2e_runtime.py` / `narrative_pass.py` not deleted (test imports); direct execution blocked

## NEXT_BLOCKER

None — optional follow-up: delete `prove_apps_rg_e2e_runtime.py` / `narrative_pass.py` entirely once test imports are refactored to library modules.
