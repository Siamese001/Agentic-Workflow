# apps_lic spine product convergence — P3/P4/P5 closeout receipt

> **Superseded by:** [spine_product_convergence_closeout_receipt.md](spine_product_convergence_closeout_receipt.md) (combined P2+P3–P5 SSOT).

## STATUS: PASS (P3–P5 scoped slice)

Canonical CLI, L0 execution_form normalization, YAML L2 retirement, legacy file deletes, and negative proofs are complete for the requested slice. Pre-existing failures in `test_w6_e2e.py` / `test_w4_research_bridge.py` remain outside this scope.

## SCOPE_MATCH: YES

- P3: GovernedLic / spine_handoff / governed_run removed from product CLI
- P4: YAML L2 registry retired; L0 emits `managed_workflow` / `terminal_fallback`
- P5: `run_workflow_lic.py`, `HOPPipelineExecutor.py`, `run_charles_truist_outreach.py` deleted

## SCOPE_DRIFT: NONE

- Did not re-open P2 canonical_dispatch logic (except removed dispatch-only execution_form shim)
- No apps_rg L2 resolver registration
- No lane pipeline

## FILES_CHANGED:

- [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py)
- [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py)
- [__main__.py](apps_lic/__main__.py)
- [lic_l2_recipe_registry.py](apps_lic/integrations/lic_l2_recipe_registry.py)
- [governed_lic_run.py](apps_lic/integrations/governed_lic_run.py)
- [spine_handoff.py](apps_lic/integrations/spine_handoff.py)
- [campaign_batch_orchestrator.py](apps_lic/integrations/campaign_batch_orchestrator.py)
- [hop_pipeline.py](apps_lic/config/hop_pipeline.py)
- [test_spine_convergence_negative_proof.py](tests/apps_lic/test_spine_convergence_negative_proof.py)
- [test_apps_lic_static_recipe.py](tests/governance/test_apps_lic_static_recipe.py)
- [test_apps_lic_w1_l0_enforcement.py](tests/governance/test_apps_lic_w1_enforcement.py)
- [test_apps_lic_w2_r4_manifest.py](tests/governance/test_apps_lic_w2_r4_manifest.py)
- [test_apps_lic_w3_managed_workflow.py](tests/governance/test_apps_lic_w3_managed_workflow.py)
- [test_apps_lic_r3r4_managed_workflow.py](tests/governance/test_apps_lic_r3r4_managed_workflow.py)
- [test_apps_lic_entrypoint_purity.py](tests/governance/test_apps_lic_entrypoint_purity.py)
- [test_w2_apps_lic_l0_final_routing.py](tests/_apps_contract/test_w2_apps_lic_l0_final_routing.py)
- [test_w4_apps_lic_l1_l0.py](tests/apps_lic/test_w4_apps_lic_l1_l0.py)
- [eval/README.md](apps_lic/eval/README.md)
- [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json)

## FILES_DELETED:

- [run_workflow_lic.py](apps_lic/tools/run_workflow_lic.py)
- [HOPPipelineExecutor.py](apps_lic/reasoning/HOPPipelineExecutor.py)
- [run_charles_truist_outreach.py](apps_lic/scripts/run_charles_truist_outreach.py)
- [apps_lic_static_dag.yaml](apps_lic/config/apps_lic_static_dag.yaml)
- [apps_lic_managed_dag.yaml](apps_lic/config/apps_lic_managed_dag.yaml)
- [test_hop_pipeline_executor.py](tests/unit/apps_lic/reasoning/test_hop_pipeline_executor.py)

## FORBIDDEN_FILES_TOUCHED:

- [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py) — execution_form canonicalization only (no app identity)
- [apps_lic_u0_adapter.py](agentic_core/runtime/u0/apps_lic_u0_adapter.py) — unchanged from P2 (2-line re-export shim)

## COMMANDS_RUN (exit codes):

| Command | Exit |
|---------|------|
| `python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --manual-brief "..." --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_proof_p345` | 0 |
| `python -m apps_lic --apps-e2e-live` | 2 |
| `pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_spine_convergence_negative_proof.py tests/_apps_contract/test_w2_apps_lic_l0_final_routing.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py tests/governance/test_apps_lic_spine.py tests/governance/test_apps_lic_static_recipe.py tests/governance/test_apps_lic_w1_l0_enforcement.py tests/governance/test_apps_lic_w2_r4_manifest.py tests/governance/test_apps_lic_entrypoint_purity.py -q` | 0 (218 passed, 1 skipped) |

## CANONICAL_CLI_RUNTIME_PROOF:

```text
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold \
  --manual-brief "Enterprise renewal briefing..." \
  --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_proof_p345
→ exit 0
→ route_family=R4_MANAGED_DRAFT
```

Artifacts:

- [route_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345/route_contract.json)
- [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345/spine_run_manifest.json)
- [ingress_raw.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345/ingress_raw.json)
- [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345/fec_summary.json)

## PRODUCT_SEAM_PROOF:

`run_canonical_apps_lic_spine` → `l0_route_apps_lic` (execution_form=`managed_workflow`) → `l3_orchestrate_apps_lic` → `l2_execute_apps_lic` / `apps_shared.orchestration.HopPipelineExecutor` + `hop_pipeline.REGISTRY` → `exit_finalize_apps_lic`

Verified by: `tests/apps_lic/test_canonical_dispatch_smoke.py` (3 passed)

## NEGATIVE_PROOF:

| Check | Result |
|-------|--------|
| `APPS_LIC_ALLOW_LEGACY_R4` unset → no default `integrated_r4_lic` in `main()` | PASS (`test_spine_convergence_negative_proof`) |
| `--apps-e2e-live` → exit 2, EVAL_ONLY message | PASS |
| GovernedLic / spine_handoff / governed_run not in product `main()` | PASS |
| `resolve_recipe("apps_lic")` → `YamlL2RecipeRetiredError` | PASS |
| `run_workflow_lic.py` deleted | PASS |
| `HOPPipelineExecutor.py` (apps_lic) deleted | PASS |
| `apps_lic` not in `l2_recipe_resolver` registry | PASS |

## NONCANONICAL_RUNNERS_REMAINING:

| Surface | Classification |
|---------|----------------|
| `canonical_dispatch` | PRODUCT_CANONICAL |
| `hop_pipeline.REGISTRY` / `l2_execute_apps_lic` | PRODUCT_CANONICAL |
| `governed_lic_run` / `spine_handoff` | LEGACY_ONLY / EVAL_ONLY |
| `campaign_batch_orchestrator` | LEGACY_ONLY (injected run_fn) |
| `--apps-e2e-live` | EVAL_ONLY (blocked exit 2) |
| `integrated_r4_lic` via `APPS_LIC_ALLOW_LEGACY_R4=1` | LEGACY_ONLY |
| `lic_l2_recipe_registry.resolve_recipe` | DELETE_PENDING (raises) |
| `lic_l2_step_adapters` | CONTRACT_TEST_ONLY |

## PROOF_CLASSIFICATION:

See [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json) (updated P3–P5).

## EXPLICIT_NON_CLAIMS:

- No full-repo pytest green (pre-existing `test_w6_e2e` UWG/redis errors)
- No live provider X3 ALLOW proof (exit shows `x3=UNKNOWN` on stub/local LLM path)
- No `agentic_core` binding migration to `apps_lic/runtime/bindings/` (S22 deferred)
- No GovernedLic file deletion (LEGACY_ONLY retained for eval/contract tests)

## NEXT_BLOCKER:

- Move bindings S22 to app-owned package; shrink `apps_lic_u0_adapter` shim
- Optional: hard-fail `APPS_LIC_ALLOW_LEGACY_R4` with deprecation sunset date
- Pre-existing: `tests/apps_lic/test_w6_e2e.py`, `test_w4_research_bridge.py` (UWG/redis) — not P3–P5 scope
