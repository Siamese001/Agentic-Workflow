# apps_lic spine product convergence — closeout receipt (P3–P5)

## STATUS: PASS

P3–P5 shadow retirement complete on top of P2 canonical dispatch. Product CLI is `canonical_dispatch` only; YAML L2 recipes and GovernedLic runners are hard-deleted; L0 binding emits canonical `execution_form`.

**Release eligibility:** **RELEASE_ELIGIBLE** as of 2026-05-20 — see [release_eligibility_verification_receipt.md](release_eligibility_verification_receipt.md). R4 live PASS; R3R4 live `BriefingReady` PASS (Tavily-sourced evidence, no mock env). Mock R3R4 does not count.

## SCOPE_MATCH: YES

- P3: GovernedLic / spine_handoff / campaign_batch removed from product import graph; eval harness labeled in [eval/README.md](apps_lic/eval/README.md)
- P4: `lic_l2_recipe_registry` + static/managed YAML DAGs deleted; L2 SSOT is `hop_pipeline.REGISTRY` + `l2_execute_apps_lic`; `execution_form` normalized in [l0_binding.py](apps_lic/runtime/bindings/l0_binding.py)
- P5: `run_workflow_lic.py`, `apps_lic/reasoning/HOPPipelineExecutor.py`, `run_charles_truist_outreach.py` deleted; governance tests updated
- P2 preserved: [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) unchanged except dispatch-only execution_form shim removal (now L0-owned)

## SCOPE_DRIFT: NONE

- No apps_rg-style lane pipeline
- No `apps_lic` registration in `apps_rg` L2 resolver
- No new symbolic proof path (`--apps-e2e-live` blocked exit 2)
- No re-open of P2 routing model

## FILES_CHANGED:

- [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py)
- [spine_run_result.py](apps_lic/runtime/dispatch/spine_run_result.py)
- [__main__.py](apps_lic/__main__.py)
- [l0_binding.py](apps_lic/runtime/bindings/l0_binding.py) (migrated from agentic_core; execution_form canonicalization)
- [l1_binding.py](apps_lic/runtime/bindings/l1_binding.py)
- [l2_binding.py](apps_lic/runtime/bindings/l2_binding.py)
- [l3_binding.py](apps_lic/runtime/bindings/l3_binding.py)
- [c0_binding.py](apps_lic/runtime/bindings/c0_binding.py)
- [pa_binding.py](apps_lic/runtime/bindings/pa_binding.py)
- [exit_binding.py](apps_lic/runtime/bindings/exit_binding.py)
- [adapter.py](apps_lic/runtime/u0/adapter.py)
- [hop_pipeline.py](apps_lic/config/hop_pipeline.py)
- [eval/README.md](apps_lic/eval/README.md)
- [test_spine_convergence_negative_proof.py](tests/apps_lic/test_spine_convergence_negative_proof.py)
- [test_canonical_dispatch_smoke.py](tests/apps_lic/test_canonical_dispatch_smoke.py)
- [test_apps_lic_spine.py](tests/governance/test_apps_lic_spine.py)
- [test_apps_lic_w1_l0_enforcement.py](tests/governance/test_apps_lic_w1_l0_enforcement.py)
- [test_apps_lic_w2_r4_manifest.py](tests/governance/test_apps_lic_w2_r4_manifest.py)
- [test_apps_lic_entrypoint_purity.py](tests/governance/test_apps_lic_entrypoint_purity.py)
- [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json)

## FILES_DELETED:

- [run_workflow_lic.py](apps_lic/tools/run_workflow_lic.py)
- [HOPPipelineExecutor.py](apps_lic/reasoning/HOPPipelineExecutor.py)
- [run_charles_truist_outreach.py](apps_lic/scripts/run_charles_truist_outreach.py)
- [apps_lic_static_dag.yaml](apps_lic/config/apps_lic_static_dag.yaml)
- [apps_lic_managed_dag.yaml](apps_lic/config/apps_lic_managed_dag.yaml)
- [lic_l2_recipe_registry.py](apps_lic/integrations/lic_l2_recipe_registry.py)
- [lic_l2_step_adapters.py](apps_lic/integrations/lic_l2_step_adapters.py)
- [governed_lic_run.py](apps_lic/integrations/governed_lic_run.py)
- [spine_handoff.py](apps_lic/integrations/spine_handoff.py)
- [campaign_batch_orchestrator.py](apps_lic/integrations/campaign_batch_orchestrator.py)
- [integrated_r4_lic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py)
- [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py) (migrated to app bindings)
- [apps_lic_u0_adapter.py](agentic_core/runtime/u0/apps_lic_u0_adapter.py) (migrated to app adapter)

## FORBIDDEN_FILES_TOUCHED:

- NONE for new product ownership in `agentic_core` (bindings migrated out; `integrated_r4_lic` entrypoint deleted)
- Retained generic-only: [apps_lic_ingress_payload.py](agentic_core/runtime/contracts/apps_lic_ingress_payload.py) (106 lines — contract type, not runner)

## COMMANDS_RUN (exit codes):

| Command | Exit |
|---------|------|
| `python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --manual-brief "Enterprise renewal briefing..." --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2` | 0 |
| `python -m apps_lic --apps-e2e-live` | 2 |
| `pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_spine_convergence_negative_proof.py tests/_apps_contract/test_w2_apps_lic_l0_final_routing.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py tests/governance/test_apps_lic_spine.py tests/governance/test_apps_lic_w1_l0_enforcement.py tests/governance/test_apps_lic_w2_r4_manifest.py tests/governance/test_apps_lic_entrypoint_purity.py -q -o addopts=` | 0 (211 passed, 1 skipped) |

## CANONICAL_CLI_RUNTIME_PROOF:

```text
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold \
  --manual-brief "Enterprise renewal briefing for Truist technology leadership." \
  --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2
→ exit 0
→ producer_component=apps_lic.runtime.dispatch.canonical_dispatch
→ route_family=R4_MANAGED_DRAFT, execution_form=managed_workflow
```

Artifacts:

- [route_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2/route_contract.json)
- [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2/spine_run_manifest.json)
- [ingress_raw.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2/ingress_raw.json)
- [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_proof_p345_v2/fec_summary.json)

## PRODUCT_SEAM_PROOF:

| Stage | Binding / component | Proof |
|-------|---------------------|-------|
| Dispatch | `run_canonical_apps_lic_spine` | CLI + smoke tests |
| U0 | `apps_lic_u0_adapt` | AG-8 golden path |
| L1 | `l1_plan_apps_lic` | canonical_dispatch |
| L0 | `l0_route_apps_lic` → `execution_form=managed_workflow` | [test_w2_apps_lic_l0_final_routing.py](tests/_apps_contract/test_w2_apps_lic_l0_final_routing.py) |
| R3R4 (when selected) | `ManagedWorkflowDispatcher` → re-plan → L0 | L0 routing tests + dispatch `_run_r3r4_research` |
| C0 / PA | `c0_retrieve_apps_lic` / `pa_compose_apps_lic` | CLI fec_summary + manifest flags |
| L3 | `l3_orchestrate_apps_lic` | smoke + AG-8 |
| L2 | `l2_execute_apps_lic` → `HopPipelineExecutor` + `hop_pipeline.REGISTRY` | smoke `l2_execution_status=completed` |
| Exit | `exit_finalize_apps_lic` | manifest `x3_disposition` present |

R4 path exercised live (CLI above). R3R4 routing logic proven by contract tests (L0 emits `R3R4_MANAGED_RESEARCH_THEN_DRAFT` when context missing + research authorized).

## NEGATIVE_PROOF:

| Check | Result |
|-------|--------|
| `integrated_r4_lic_pipeline_run` deleted from agentic_core | PASS |
| `APPS_LIC_ALLOW_LEGACY_R4` not in `__main__` | PASS |
| `--apps-e2e-live` → exit 2, not product proof | PASS |
| GovernedLic / spine_handoff / governed_run not importable | PASS |
| `lic_l2_recipe_registry` not importable | PASS |
| YAML static/managed DAG files absent | PASS |
| `run_workflow_lic.py` absent; not in `__main__` AST | PASS |
| `apps_lic` ∉ `l2_recipe_resolver` builtin registry | PASS |
| `apps_lic.reasoning.HOPPipelineExecutor` absent (use apps_shared) | PASS |

## NONCANONICAL_RUNNERS_REMAINING:

See [noncanonical_runner_classification.json](artifacts/apps_lic/spine_convergence/noncanonical_runner_classification.json).

| Surface | Classification |
|---------|----------------|
| `canonical_dispatch` + app bindings | PRODUCT_CANONICAL |
| `hop_pipeline.REGISTRY` / `l2_execute_apps_lic` | PRODUCT_CANONICAL |
| `apps_lic.eval` | EVAL_ONLY |
| Contract/governance tests | CONTRACT_TEST_ONLY |
| Shadow runners (GovernedLic, YAML L2, run_workflow_lic, etc.) | **hard_deleted_p5** |

## PROOF_CLASSIFICATION:

- **PRODUCT_CANONICAL**: `python -m apps_lic` → `run_canonical_apps_lic_spine` only
- **EVAL_ONLY**: `apps_lic/eval/`, retired `run_lic_pilot_proof` stub in `tools/eval/retrieval_benchmark.py`
- **CONTRACT_TEST_ONLY**: `_apps_contract` + governance spine tests
- **HARD_DELETED**: all S3–S13 shadow inventory surfaces (grep-zero on disk)

## EXPLICIT_NON_CLAIMS:

- No full-repo pytest green (pre-existing `test_w6_e2e` / UWG-redis failures outside scope)
- No X3 `ALLOW` / `COMMIT_REQUEST` on CLI run (`x3_disposition=UNKNOWN` on local vLLM path)
- No live cloud-provider proof (localhost:8000 only)
- No R3R4 end-to-end live `apps_research` bridge run in this wave (routing + dispatch code path only)
- `agentic_core` retains generic L5/L4 contract files (listed below) — not product runners

## NEXT_BLOCKER:

- Optional: live R3R4 CLI proof with `APPS_LIC_MOCK_RESEARCH=1` or real `apps_research` bridge
- Pre-existing: `tests/apps_lic/test_w6_e2e.py`, `test_w4_research_bridge.py` (UWG/redis)
- Docs hygiene: [RUNBOOK.md](apps_lic/RUNBOOK.md) still mentions deleted runners (comment-only drift)

## Protected-path proof (agentic_core)

| File | Lines | Reason |
|------|-------|--------|
| [apps_lic_ingress_payload.py](agentic_core/runtime/contracts/apps_lic_ingress_payload.py) | 106 | Generic ingress contract type |
| [apps_lic_reengagement.py (policy)](agentic_core/L5_safety/policy/apps_lic_reengagement.py) | 347 | L5 policy schema |
| [apps_lic_reengagement.py (evaluator)](agentic_core/L5_safety/evaluators/apps_lic_reengagement.py) | 445 | L5 evaluator |
| [apps_lic_touch_state.sql](agentic_core/L4_state/schemas/apps_lic_touch_state.sql) | 124 | L4 schema |

No `apps_lic_*_binding.py` shims remain in `agentic_core`. No `apps_lic` in L2 recipe resolver.
