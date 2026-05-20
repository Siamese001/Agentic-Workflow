# apps_lic spine product convergence — closeout receipt (P2 wave)

## STATUS: PARTIAL

P2 canonical dispatch and CLI switch are implemented and smoke-tested. P3–P5 deletions and GovernedLic retirement remain.

## SCOPE_MATCH: YES (P2 slice)

- Canonical path: `U0 → L1 → L0 → (R3R4 research) → C0 → PA → L3 → L2 → Exit`
- Promoted S5/S9 via `canonical_dispatch` (not new lane pipeline)
- No `apps_lic` registration in `apps_rg` L2 resolver
- Legacy `integrated_r4_lic` env-gated only

## SCOPE_DRIFT: NONE for P2

- Did not delete S11–S13 (grep-proof pending P5)
- Did not retire GovernedLic (P3)
- Added minimal `agentic_core` U0 re-export shim (≤2 lines) to unblock existing bindings

## FILES_CHANGED:

- [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py)
- [spine_run_result.py](apps_lic/runtime/dispatch/spine_run_result.py)
- [__init__.py](apps_lic/runtime/dispatch/__init__.py)
- [__main__.py](apps_lic/__main__.py)
- [r4_single_action.py](apps_lic/runtime/legacy/r4_single_action.py)
- [run_workflow_lic.py](apps_lic/tools/run_workflow_lic.py) (DELETE_PENDING header)
- [apps_lic_u0_adapter.py](agentic_core/runtime/u0/apps_lic_u0_adapter.py) (shim)
- [test_canonical_dispatch_smoke.py](tests/apps_lic/test_canonical_dispatch_smoke.py)
- [test_apps_lic_spine.py](tests/governance/test_apps_lic_spine.py)
- [test_apps_lic_w1_l0_enforcement.py](tests/governance/test_apps_lic_w1_l0_enforcement.py)
- [test_apps_lic_entrypoint_purity.py](tests/governance/test_apps_lic_entrypoint_purity.py)
- [test_ag8_apps_lic_golden_path.py](tests/_apps_contract/test_ag8_apps_lic_golden_path.py)
- [spine_shadow_deletion_roadmap_p0_p5.md](docs/reports/apps_lic/spine_shadow_deletion_roadmap_p0_p5.md)
- [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json)
- [w0_baseline_gap.json](artifacts/apps_lic/spine_convergence/w0_baseline_gap.json)

## FILES_DELETED: NONE (P5 gated)

## COMMANDS_RUN (exit codes):

| Command | Exit |
|---------|------|
| `pytest tests/apps_lic/test_canonical_dispatch_smoke.py` | 0 |
| `pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py tests/governance/test_apps_lic_spine.py -q` | 0 (after AG8 context_signals fix) |
| `pytest tests/governance/test_apps_lic_w1_l0_enforcement.py::test_main_uses_canonical_dispatch_not_run_workflow_lic` | 0 |

## CANONICAL_RUNTIME_PROOF:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py tests/governance/test_apps_lic_spine.py -q
→ 118 collected, 118 passed (post context_signals fixture fix)
```

Product seam exercised: `run_canonical_apps_lic_spine` → `l0_route_apps_lic` → `l3_orchestrate_apps_lic` → `l2_execute_apps_lic` → `exit_finalize_apps_lic`.

## ARTIFACTS_WRITTEN:

- [spine_shadow_deletion_roadmap_p0_p5.md](docs/reports/apps_lic/spine_shadow_deletion_roadmap_p0_p5.md)
- [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json)
- [w0_baseline_gap.json](artifacts/apps_lic/spine_convergence/w0_baseline_gap.json)
- Per-run: `artifacts/apps_lic/spine_convergence/runs/<run_id>/route_contract.json`, `spine_run_manifest.json` (pytest tmp)

## NONCANONICAL_RUNNERS_REMAINING:

See [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json).

## PROOF_CLASSIFICATION:

| Runner | Class |
|--------|-------|
| `canonical_dispatch.run_canonical_apps_lic_spine` | PRODUCT_CANONICAL |
| `profile_builder_adapter` | PRODUCT_CANONICAL |
| `l2_execute_apps_lic` / HOP | PRODUCT_CANONICAL |
| `integrated_r4_lic` (env gate) | LEGACY_ONLY |
| `--apps-e2e-live` governed_run | LEGACY_ONLY |
| GovernedLic / spine_handoff | LEGACY_ONLY |
| `run_workflow_lic.py` | DELETE_PENDING |
| YAML L2 recipes | DELETE_PENDING |
| eval harness | EVAL_ONLY |

## EXPLICIT_NON_CLAIMS:

- No full CLI live provider run in this wave
- No S11–S13 file deletes
- No GovernedLic removal from repo
- No `agentic_core` binding migration complete (shim only)
- `--apps-e2e-live` still symbolic cert theater (warned in CLI)

## NEXT_BLOCKER:

- P3: Remove GovernedLic from any remaining product import graph
- P4: Delete/fold `lic_l2_recipe_registry` + YAML DAGs; normalize `execution_form` at L0 binding (not only dispatch)
- P5: Grep-zero delete `run_workflow_lic.py`, deprecated HOP executor, charles outreach script
