# apps_lic spine hard-delete closeout receipt

## STATUS: PASS

All product-reachable shadow pipelines are physically deleted. Product runtime is a single path: `python -m apps_lic` → `canonical_dispatch` only. No env gates, shims, tombstones, or symbolic cert branches remain in product code.

## SCOPE_MATCH: YES

- Hard-delete (not LEGACY_ONLY / DELETE_PENDING / env-gated) per user directive
- Waves 1–4 executed: product shadows → YAML L2 → quarantined runners → agentic_core runner identity
- P2 canonical_dispatch preserved (not re-opened)

## SCOPE_DRIFT: NONE

- No apps_rg L2 resolver registration
- No lane pipeline
- No new symbolic proof path

## FILES_CHANGED:

- [__main__.py](apps_lic/__main__.py)
- [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) (comments only)
- [u0_apps_lic_binding.py](agentic_core/runtime/entry/u0_apps_lic_binding.py)
- [app_registry.py](apps_shared/integrations/app_registry.py)
- [integration_engine.py](apps_lic/engines/integration_engine.py)
- [apps_lic_ingress_payload.py](agentic_core/runtime/contracts/apps_lic_ingress_payload.py)
- [apps_lic_ingress_contract_v1.py](apps_lic/contracts/apps_lic_ingress_contract_v1.py)
- [eval/README.md](apps_lic/eval/README.md)
- [retrieval_benchmark.py](tools/eval/retrieval_benchmark.py)
- [test_spine_convergence_negative_proof.py](tests/apps_lic/test_spine_convergence_negative_proof.py)
- [test_apps_lic_spine.py](tests/governance/test_apps_lic_spine.py)
- [test_apps_lic_entrypoint_purity.py](tests/governance/test_apps_lic_entrypoint_purity.py)
- [test_apps_lic_w2_r4_manifest.py](tests/governance/test_apps_lic_w2_r4_manifest.py)
- [test_w5_apps_lic_ingress_runner_wiring.py](tests/_apps_contract/test_w5_apps_lic_ingress_runner_wiring.py)
- [test_w3_apps_lic_u0.py](tests/apps_lic/test_w3_apps_lic_u0.py)
- [test_w4_apps_lic_l1_l0.py](tests/apps_lic/test_w4_apps_lic_l1_l0.py)
- [test_w5_apps_lic_c0_pa.py](tests/apps_lic/test_w5_apps_lic_c0_pa.py)
- [test_w6_apps_lic_boundary_governance.py](tests/_apps_contract/test_w6_apps_lic_boundary_governance.py)
- [test_w4_apps_lic_schema_field_map_coverage.py](tests/_apps_contract/test_w4_apps_lic_schema_field_map_coverage.py)
- [test_apps_spine_coverage.py](tests/unit/tools/analysis/test_apps_spine_coverage.py)
- [test_w3_entrypoint_c0_bypass_audit.py](tests/agentic_core/runtime/entrypoints/test_w3_entrypoint_c0_bypass_audit.py)
- [test_governed_app_runner_hitl.py](tests/unit/apps_shared/integrations/test_governed_app_runner_hitl.py)
- [test_w5_build_app_record.py](tests/unit/apps_shared/integrations/test_w5_build_app_record.py)
- [test_governed_app_runner_w1_phase_errors.py](tests/unit/apps_shared/integrations/test_governed_app_runner_w1_phase_errors.py)

## FILES_DELETED:

- [integrated_r4_lic_pipeline_run.py](agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py)
- [apps_lic_u0_adapter.py](agentic_core/runtime/u0/apps_lic_u0_adapter.py)
- [governed_lic_run.py](apps_lic/integrations/governed_lic_run.py)
- [spine_handoff.py](apps_lic/integrations/spine_handoff.py)
- [lic_l2_recipe_registry.py](apps_lic/integrations/lic_l2_recipe_registry.py)
- [lic_l2_step_adapters.py](apps_lic/integrations/lic_l2_step_adapters.py)
- [campaign_batch_orchestrator.py](apps_lic/integrations/campaign_batch_orchestrator.py)
- [enterprise_campaign_orchestrator.py](apps_lic/reasoning/enterprise_campaign_orchestrator.py)
- [governed_outreach.py](apps_lic/outreach_engine/governed_outreach.py)
- [governed_outreach.py](apps_lic/engines/outreach/governed_outreach.py)
- [r4_single_action.py](apps_lic/runtime/legacy/r4_single_action.py)
- [__init__.py](apps_lic/runtime/legacy/__init__.py)
- [test_apps_lic_r3r4_managed_workflow.py](tests/governance/test_apps_lic_r3r4_managed_workflow.py)
- [test_apps_lic_prompt_assembly.py](tests/governance/test_apps_lic_prompt_assembly.py)
- [test_apps_lic_campaign_batch.py](tests/governance/test_apps_lic_campaign_batch.py)
- [test_apps_lic_static_recipe.py](tests/governance/test_apps_lic_static_recipe.py)
- [test_integrated_r4_lic_l7_emit.py](tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_lic_l7_emit.py)
- [test_enterprise_lic.py](tests/unit/apps_lic/scripts/test_enterprise_lic.py)

(Previously deleted in P3–P5: run_workflow_lic.py, HOPPipelineExecutor.py, run_charles_truist_outreach.py, YAML DAGs)

## FORBIDDEN_FILES_TOUCHED:

- [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py) — unchanged (execution_form SSOT from P4)
- [u0_apps_lic_binding.py](agentic_core/runtime/entry/u0_apps_lic_binding.py) — import repointed to `apps_lic.runtime.u0.adapter` (no shim left)
- Spine bindings in agentic_core remain — generic engine consumption, not app runners (see AGENTIC_CORE_APPS_LIC_OWNERSHIP_PROOF)

## COMMANDS_RUN (exact exit codes):

| Command | Exit |
|---------|------|
| `python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --manual-brief "Hard delete proof..." --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof` | 0 |
| `python -m apps_lic --apps-e2e-live` | 2 |
| `pytest tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_spine_convergence_negative_proof.py tests/governance/test_apps_lic_spine.py tests/governance/test_apps_lic_entrypoint_purity.py tests/governance/test_apps_lic_w2_r4_manifest.py tests/_apps_contract/test_w5_apps_lic_ingress_runner_wiring.py tests/_apps_contract/test_w2_apps_lic_l0_final_routing.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q` | 0 (222 passed) |

## CANONICAL_CLI_RUNTIME_PROOF:

```text
python -m apps_lic ... --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof
→ exit 0
→ route_family=R4_MANAGED_DRAFT
→ x3=UNKNOWN (stub/local LLM — not claimed as production ALLOW)
```

Artifacts:

- [route_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof/route_contract.json)
- [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof/spine_run_manifest.json)
- [ingress_raw.json](artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof/ingress_raw.json)
- [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_hard_delete_proof/fec_summary.json)

## PRODUCT_SEAM_PROOF:

`run_canonical_apps_lic_spine` → `u0_validate_apps_lic` / `apps_lic_u0_adapt` → L1 → `l0_route_apps_lic` → C0/PA (when required) → `l3_orchestrate_apps_lic` (R3R4) → `l2_execute_apps_lic` / `HopPipelineExecutor` + `hop_pipeline.REGISTRY` → `exit_finalize_apps_lic`

Verified by: `tests/apps_lic/test_canonical_dispatch_smoke.py`, `tests/_apps_contract/test_ag8_apps_lic_golden_path.py` (91 tests in golden path module)

## DELETION_PROOF:

| Shadow | Product reachable? | Proof |
|--------|-------------------|-------|
| integrated_r4_lic | No | File deleted; `test_integrated_r4_lic_entrypoint_deleted` |
| APPS_LIC_ALLOW_LEGACY_R4 | No | Removed from `__main__.py` |
| --apps-e2e-live / governed_run cert | No | Exit 2, branch removed |
| GovernedLicRun / spine_handoff | No | Modules deleted; import fails in negative tests |
| YAML L2 registry / DAGs | No | Files deleted; `lic_l2_recipe_registry` import fails |
| lic_l2_step_adapters | No | File deleted |
| campaign_batch / EnterpriseLic | No | Files deleted |
| governed_outreach (send_email) | No | Both duplicate files deleted |
| apps_lic_u0_adapter shim | No | File deleted; U0 imports `apps_lic.runtime.u0.adapter` |

## NEGATIVE_TEST_PROOF:

`tests/apps_lic/test_spine_convergence_negative_proof.py` — 21 tests:

- Parametrized `test_deleted_module_not_importable` (9 modules)
- Parametrized `test_deleted_file_absent` (8 paths)
- `test_apps_e2e_live_flag_removed`
- `test_main_canonical_dispatch_only` (AST import graph)
- `test_apps_rg_resolver_has_no_apps_lic`
- `test_main_has_no_send_email_import`

## GREP_ZERO_PROOF:

Product/runtime Python (excluding tests, docs, tools/eval skip strings):

| Pattern | Product `.py` hits (non-comment import) |
|---------|----------------------------------------|
| integrated_r4_lic_pipeline_run | 0 importable |
| apps_lic_u0_adapter | 0 (repointed to apps_lic.runtime.u0.adapter) |
| governed_lic_run / GovernedLicRun | 0 importable |
| spine_handoff / run_lic_via_spine | 0 importable |
| lic_l2_recipe_registry | 0 importable |
| lic_l2_step_adapters | 0 importable |
| run_workflow_lic | 0 file |
| EnterpriseLicOrchestrator | 0 file |
| apps_lic_static_dag / apps_lic_managed_dag | 0 file |

Allowed remaining references: tests asserting deletion, docs/receipts, `tools/eval/retrieval_benchmark.py` skip message, `canonical_dispatch.py` docstring negatives.

## REMAINING_REFERENCES_WITH_REASON:

| Reference | Reason |
|-----------|--------|
| `tests/**` shadow names | CONTRACT_TEST_ONLY — assert paths deleted / imports fail |
| `docs/reports/**`, `.cursor/plans/**` | Deletion history documentation |
| `tools/eval/retrieval_benchmark.py` | EVAL_ONLY — `run_lic_pilot_proof()` prints SKIP, returns True; not reachable from `apps_lic.__main__` |
| `apps_shared/integrations/app_registry.py` | Registry documents apps_lic as FormalExceptionEntry (canonical spine, not GovernedAppRunner) |
| `agentic_core/**/apps_lic_*_binding.py` | Generic spine bindings — not product runners (S22 deferred migration to app-owned package) |
| `agentic_core/__init__.py` `run_workflow_lic_adg` | Unrelated ADG flag name — not `run_workflow_lic.py` |

## AGENTIC_CORE_APPS_LIC_OWNERSHIP_PROOF:

**No app runner in agentic_core:** `integrated_r4_lic_pipeline_run.py` deleted.

**No U0 shim:** `apps_lic_u0_adapter.py` deleted; `u0_apps_lic_binding` imports `apps_lic.runtime.u0.adapter`.

**L2 resolver:** `apps_lic` not in `_register_builtin_recipes()` (apps_rg only).

**Remaining agentic_core apps_lic surfaces (bindings only):**

| File | Lines | Role |
|------|-------|------|
| [apps_lic_l0_binding.py](agentic_core/L0_routing/apps_lic_l0_binding.py) | 369 | L0 route contract |
| [apps_lic_l1_binding.py](agentic_core/L1_cognition/apps_lic_l1_binding.py) | 381 | L1 plan |
| [apps_lic_l2_binding.py](agentic_core/L2_execution/apps_lic_l2_binding.py) | 412 | HOP L2 execution |
| [apps_lic_l3_binding.py](agentic_core/L3_orchestration/apps_lic_l3_binding.py) | 443 | L3 orchestration |
| [apps_lic_c0_binding.py](agentic_core/runtime/c0/apps_lic_c0_binding.py) | 525 | C0 shaping |
| [u0_apps_lic_binding.py](agentic_core/runtime/entry/u0_apps_lic_binding.py) | 188 | U0 envelope bridge |
| [apps_lic_pa_binding.py](agentic_core/prompt_governance/apps_lic_pa_binding.py) | 349 | Prompt assembly |
| [apps_lic_exit_binding.py](agentic_core/runtime/exit/apps_lic_exit_binding.py) | 634 | Exit finalize |
| [apps_lic_promo_binding.py](agentic_core/L6_observability/promotion/apps_lic_promo_binding.py) | 266 | L6 promotion |

These are generic spine stage bindings invoked by `canonical_dispatch`, not alternate product runners.

## PROOF_CLASSIFICATION:

| Surface | Classification |
|---------|----------------|
| `canonical_dispatch` / `__main__.py` | PRODUCT_CANONICAL |
| `hop_pipeline.REGISTRY` / `l2_execute_apps_lic` | PRODUCT_CANONICAL |
| `managed_workflow_dispatcher` / `apps_research_bridge` | PRODUCT_CANONICAL (L3 R3R4) |
| agentic_core `apps_lic_*_binding` | CORE_SPINE_BINDING (not runner) |
| `tools/eval/retrieval_benchmark` LIC pilot | EVAL_ONLY (retired) |

## EXPLICIT_NON_CLAIMS:

- No full `tests/apps_lic/` suite green (pre-existing w6_e2e / w4_research failures)
- No live provider X3 ALLOW proof (`x3=UNKNOWN` on local path)
- No migration of spine bindings to `apps_lic/runtime/bindings/` (S22 — NEXT_BLOCKER)
- `tests/apps_lic/` full tree not run in this slice

## NEXT_BLOCKER:

- Move `apps_lic_*_binding` from `agentic_core` to `apps_lic/runtime/bindings/` (S22)
- Update `apps_spine_coverage` scanner to classify canonical spine without `spine_handoff.py`
- Optional: prune historical plan/doc references to deleted modules
