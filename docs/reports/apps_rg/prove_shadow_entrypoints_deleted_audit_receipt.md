# Prove shadow entrypoints deleted — audit receipt

**PLAN_ID:** prove-shadow-entrypoints-deleted  
**STATUS:** PARTIAL  
**Mode:** Audit only (no code changes)

## SCOPE_MATCH

Verified file absence, `python -m` behavior, grep/caller gates, canonical CLI, SP-001..SP-005, and product-proof guard tests against the prior outside-main inventory.

## SCOPE_DRIFT

None (read-only audit).

## FILES_CHANGED

None

## FILES_DELETED

None (audit only)

---

## FILE_ABSENCE_ENTRYPOINT_TABLE

| Target | Path exists | `__main__` | CLI parser (`argparse`/etc.) | `python -m` runnable | `python path.py` direct | Provider/judge on `-m` | Writes proof/X3 on `-m` | Status |
|--------|-------------|------------|------------------------------|----------------------|-------------------------|-------------------------|-------------------------|--------|
| orchestrate_full_resume | **no** (→ `_offline/lane_batch.py`) | no | no (no `main` in lane_batch) | **no** (N/A — module missing) | N/A | no | no | **DELETED** |
| executive_summary_demo | **no** | — | — | **no** (N/A) | — | — | — | **DELETED** |
| resume_package_x3 | **no** (→ `_offline/resume_package_disposition.py`) | no | yes (`main()` exists, not wired) | import-only exit 0 | blocked without `__main__` | no on `-m` | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| generated_lane_rollup | **no** (→ `_offline/`) | no | yes (`main()`+argparse, not wired) | import-only exit 0 | same | no on `-m` | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| final_resume_assembler | **no** (→ `_offline/`) | no | yes (`main()` exists) | import-only exit 0 | same | no on `-m` | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| docx_renderer | **no** (→ `_offline/`) | no | yes (`main()` exists) | not re-run (same pattern) | same | no on `-m` | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| locked_copy_builder | **no** (→ `_offline/`) | no | yes (`main()` exists) | not re-run | same | no on `-m` | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| dispatch `*_dispatch.py` (7 files) | **yes** (6; headline **no**) | **no** | yes (`build_parser` on exec/comp; no `main`/`run_dispatch`) | **import-only exit 0** (exec, comp tested) | N/A | import side-effects only | no on `-m` | **INTERNALIZED_NOT_RUNNABLE** |
| headline_dispatch | **no** | — | — | **no** (No module named) | — | — | — | **DELETED** |
| prove_apps_rg_e2e_runtime.py | **yes** | yes (blocked) | yes (`main()`+argparse) | **BLOCKED** exit 1 | **BLOCKED** exit 1 | yes if `main()` invoked | yes if `main()` invoked | **BLOCKED** |
| narrative_pass.py | **yes** | yes (blocked at top) | yes (`main()` below guard) | **BLOCKED** exit 1 | **BLOCKED** exit 1 | yes if `main()` invoked | yes if `main()` invoked | **BLOCKED** |
| generate_resume.py | **no** | — | — | — | — | — | — | **DELETED** |

**Notes**

- Internalized code lives under [apps_rg/runtime/internal/](apps_rg/runtime/internal/).
- `lane_batch` has no `main()`; lanes run via subprocess `python -m apps_rg --section` only.
- Legacy dispatch modules retain **argparse `build_parser`** for tests/imports but **`main` / `run_dispatch` removed**; `python -m` does not invoke them (exit 0 = import-only).
- `_offline` modules still define **`main()`** callable programmatically (not auto-run without `if __name__ == "__main__"`).

---

## DIRECT_COMMAND_PROOF

| Command | Exit | Stderr/stdout summary |
|---------|------|------------------------|
| `python -m apps_rg.runtime.orchestrate_full_resume` | **1** | `No module named apps_rg.runtime.orchestrate_full_resume` |
| `python -m apps_rg.runtime.dry_run.executive_summary_demo` | **1** | `No module named …executive_summary_demo` |
| `python -m apps_rg.runtime.package.resume_package_x3` | **1** | `No module named …resume_package_x3` |
| `python -m apps_rg.runtime.reports.generated_lane_rollup` | **1** | `No module named …generated_lane_rollup` |
| `python -m apps_rg.runtime.assembly.final_resume_assembler` | **1** | `No module named …final_resume_assembler` |
| `python -m apps_rg.runtime.render.docx_renderer` | **1** | `No module named …docx_renderer` |
| `python -m apps_rg.runtime.locked_copy.locked_copy_builder` | **1** | `No module named …locked_copy_builder` |
| `python -m apps_rg.runtime.sections.executive_summary_lane_api` | **0** | Import-only; tqdm/embedding init; **no** `main` invoked |
| `python -m apps_rg.runtime.sections.competencies_lane_api` | **0** | Import-only; tqdm/embedding init |
| `python -m apps_rg.runtime.dispatch.headline_dispatch` | **1** | `No module named …headline_dispatch` |
| `python ops_scripts/ci/prove_apps_rg_e2e_runtime.py` | **1** | `ERROR: … not a product proof entrypoint` |
| `python ops_scripts/apps_rg/narrative_pass.py` | **1** | `ERROR: … retired; use: python -m apps_rg` |

**Gap vs strict expectation:** dispatch `-m` exits **0** (module load + import side-effects), not ImportError. No fail-closed deprecation message on `-m` (stubs removed). Does **not** write proof artifacts via `-m` alone.

---

## GREP_PROOF

### `python -m apps_rg.runtime.` (docs + apps_rg + ops_scripts + tests + .github + pyproject + Makefile)

**~45 hits** repo-wide. Classification:

| Class | Examples | Count (approx.) |
|-------|----------|-----------------|
| **Allowed** — integrated proof gate | `python -m apps_rg.runtime.integrated_product_proof_gate` | few |
| **Allowed** — prepare_orchestrator_inputs / validators | RUNBOOK, policy | few |
| **Allowed** — denylist in policy | [outside_main_entry_policy.py](apps_rg/runtime/outside_main_entry_policy.py) | 16 |
| **Allowed** — dispatch doc warnings | `executive_summary_dispatch.py` docstrings | few |
| **Allowed** — tests proving absence | [test_no_disallowed_…](tests/_apps_contract/test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py) | 1 |
| **Allowed historical report** | [docs/reports/apps_rg/final_resume_aggregation_*.md](docs/reports/apps_rg/) teaching `_offline` `-m` | ~10 |
| **Violation (historical only)** | `docs/reports/**` `_offline` execution examples | not in active runbook scan roots |

**Automated gate** ([test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py](tests/_apps_contract/test_no_disallowed_apps_rg_runtime_module_commands_in_docs.py)): scans `apps_rg/`, `ops_scripts/`, `.cursor/rules/` only — **PASS** (87 tests in bundle).

**ops_scripts / .github workflows:** no `python -m apps_rg.runtime.orchestrate_*` or deleted module commands found.

### Symbol grep (`orchestrate_full_resume|…|generate_resume`)

- **apps_rg/** — docstrings, policy denylist, l2_recipe comments (internal import names), `generate_resume_step` receipt filenames (not CLI) — **allowed internal**
- **ops_scripts/** — no runnable deleted-module commands
- **tests/** — absence/deletion tests — **allowed test**
- **docs/reports/** — historical evidence — **allowed historical report**

### `apps_rg.runtime.dispatch.*_dispatch` / `python -m apps_rg.runtime.dispatch`

- Active **RUNBOOK** does not teach dispatch `-m`
- Dispatch `.py` files contain **deprecated wording in docstrings only**
- [deprecated_runtime_cli.py](apps_rg/runtime/deprecated_runtime_cli.py) — library `exit_deprecated_dispatch_cli()` (exit 2), used by [modular_lane_adapter.run_dispatch_main](apps_rg/l2_recipe/modular_lane_adapter.py), **not** a `python -m` stub

---

## CALLER_PROOF

| Symbol | Production callers | Verdict |
|--------|------------------|---------|
| `dispatch_apps_rg_run` | [apps_rg/__main__.py](apps_rg/__main__.py), [agentic_core/runtime/entry/apps_rg_dispatch.py](agentic_core/runtime/entry/apps_rg_dispatch.py), [apps_rg_dispatch.py](apps_rg/runtime/dispatch/apps_rg_dispatch.py) (parse helper) | **Canonical only** (test: PASS) |
| `run_canonical_apps_rg_from_cli_primitives` | Not in `apps_rg/runtime/dispatch/*` or deleted shadow paths; **not** in [lane_batch.py](apps_rg/runtime/internal/lane_batch.py) | **PASS** |
| `apps_rg.runtime.dispatch.*` | Section lanes, tests, PA compile helpers — **library imports** | **Allowed internal** |
| Deleted module paths | **No imports** of `orchestrate_full_resume`, `resume_package_x3`, etc. | **PASS** |

---

## CANONICAL_PATH_CHECKS

| Command | Exit |
|---------|------|
| `python -m apps_rg --help` | **0** |
| `python -m apps_rg --section executive_summary --dry-run` (Brown & Brown JD/brief fixtures) | **0** |
| `python -m apps_rg.runtime.integrated_product_proof_gate --help` | **0** |

**SP-001..SP-005:** 11 passed ([test_orchestrate_full_resume_non_product_classification.py](tests/unit/apps_rg/test_orchestrate_full_resume_non_product_classification.py), demo/CI/package/L7 tests).

**Deletion contract bundle:** 87 passed, 7 skipped ([test_no_outside_main_runtime_entrypoints.py](tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py), etc.).

---

## PRODUCT_PROOF_GUARD_REGRESSION

[test_integrated_product_proof_gate.py](tests/unit/apps_rg/test_integrated_product_proof_gate.py) — **PASS** (section-only, offline rollup, package-x3 family, demo, CI lane-dev historical artifacts rejected).

---

## DOCS_CI_STATUS

| Surface | Status |
|---------|--------|
| [RUNBOOK_E2E.md](apps_rg/runtime/RUNBOOK_E2E.md) | Canonical `python -m apps_rg` only; prove script marked test-import-only |
| **ops_scripts** | No deleted `-m` commands; prove/narrative **blocked** on direct run |
| **.github/workflows** | No matches for deleted entrypoints |
| **docs/reports/** | Historical `_offline -m` examples remain (evidence, not operator SSOT) |

---

## ALLOWED_OUTSIDE_MAIN_EXECUTABLES

- `apps_rg.runtime.integrated_product_proof_gate`
- `apps_rg.runtime.validators.validate_exec_summary_graph_only_generation`
- `apps_rg.runtime.prepare_orchestrator_inputs`
- `apps_rg.audit.srfs_receipt_aggregator`
- `apps_rg.fact_inventory.*`

## DISALLOWED_OUTSIDE_MAIN_EXECUTABLES_REMAINING

**Historical paths:** NONE runnable (`ImportError` on `-m`).

**Residual (non-product CLI, import-only):**

- `python -m apps_rg.runtime.dispatch.{executive_summary,competencies}_dispatch` → exit **0**, import side-effects only
- `python -m apps_rg.runtime.internal.*` → exit **0**, import side-effects; `main()` exists but not auto-invoked

These are **not** allowlisted product entrypoints but **remain importable module paths**.

## DEPRECATED_RUNNABLE_STUBS_REMAINING

- **`refuse_runtime_module_cli` / `refuse_runtime_module_cli_from_main`:** removed from [outside_main_entry_policy.py](apps_rg/runtime/outside_main_entry_policy.py); **not** used on dispatch modules
- **[deprecated_runtime_cli.py](apps_rg/runtime/deprecated_runtime_cli.py):** library `exit_deprecated_dispatch_cli()` (exit **2**) for [run_dispatch_main](apps_rg/l2_recipe/modular_lane_adapter.py) — **not** a `python -m` runnable stub
- **headline_dispatch refuse stub:** file **deleted**

## BLOCKERS

1. **PARTIAL:** `python -m apps_rg.runtime.dispatch.*_dispatch` (exec, comp) returns **0** with import-time side effects — does not meet strict “module not found / non-runnable” wording, though no `main`/`__main__` and no proof writes on `-m`.
2. **PARTIAL:** `_offline` modules still expose programmatic `main()`+argparse (not wired to `-m`).
3. **LOW:** `docs/reports/**` historical lines teach `_offline` `-m` (outside automated scan roots).

## PROTECTED_PATHS_TOUCHED

None

## FORBIDDEN_FILES_TOUCHED

None (`agentic_core` untouched)

## EXPLICIT_NON_CLAIMS

- No product / Fort Knox / L7 proof
- No integrated R4 refactor
- No `agentic_core` edits
- No section-only proof upgrade

## NEXT_BLOCKER

To reach strict **PASS** on direct-command proof: make `python -m apps_rg.runtime.dispatch.*` and `python -m apps_rg.runtime.internal.*` fail with **ImportError** (rename/shim-delete module paths) or document explicit approval of import-only exit 0. Optional: remove programmatic `main()` from `_offline` modules.
