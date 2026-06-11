---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2.md'
source_sha256: c83409b35d1a8632d0c4dc7670f222d9d3671af06cef889ab41fc05e156c4b90
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-zip-based-full-spine-runtime-restoration-v1
plan_slug: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2
plan_type: implementation
status: IN_PROGRESS
active_authority: true
supersedes: apps-rg-w3-plus-managed-workflow-sequence
supersedes_plan_file: .cursor/plans/apps-rg-ensemble-judge-restoration-a7c4e2.md
created: "2026-05-11"
created_for: apps_rg
rebaseline_id: apps_rg_runtime_restoration_rebaseline_after_w11
rebaseline_status: ACTIVE
final_status: COMPLETE
closure_wave: RB16_JUDGE_BOUNDARY_CLEANUP
closure_reason: "All waves RB0-RB16 complete. 21 receipts inventoried. RB13 boundary drift (executive_positioning string pattern) FIXED in RB16 via config-driven approach. Judge classification now fully profile-driven from grader_roster.yaml. Route remains registered_not_active. Provider mode remains stub_only. 158 tests passing."
certification_status: PASS
route_activation_status: NOT_ACTIVATED
next_active_wave: null
---

# apps_rg Zip-Based Full-Spine Runtime Restoration

Fully implement `apps_rg` on the common agentic spine using the attached/current `apps_rg.zip` as source evidence, while reconciling against the live repo.

This is the **new active sequencing authority** for `apps_rg` runtime implementation.

The prior W3+ sequence (`apps-rg-ensemble-judge-restoration-a7c4e2`) is **archived and superseded**. W3+ may be referenced only as historical implementation detail.

---

## Design Target

`apps_rg` is **declarative app configuration and domain logic only**.  
`agentic_core` **owns runtime execution**.

### apps_rg may own
- U0 app package refs
- Domain contract YAML/JSON
- Prompt templates
- Workflow manifests
- Gate config
- Pure domain gate functions if registered as config and invoked by core
- Judge rubric config, thresholds, negative controls
- Learning/meta-feedback profiles

### agentic_core owns
- U0 validation adapter
- L1/L0 core contract flow
- Workflow registry resolution
- L3 managed workflow orchestration
- L2 execution lanes
- Provider/model calls
- Runtime gate evaluation
- LLM judge invocation
- Exit X1-X3
- RuntimeExhaustBundle
- L6 meta-learning
- UWG durable write admission
- L4 durable storage

---

## Hard Invariants

- No apps_rg-specific runtime authority inside apps_rg.
- No separate apps_rg Exit.
- apps_rg must not emit X3.
- apps_rg must not write L4.
- apps_rg must not call providers directly.
- apps_rg must not execute quarantined HOPs directly.
- apps_rg must not bypass core L3/L2.
- U0 must validate and preserve the apps_rg package, not execute it.
- L0 must emit exactly one RouteContract.
- L3 sequences workflow nodes.
- L2 executes exactly one bounded node at a time.
- Exit emits exactly one X3.
- L6 learns only after current-run boundary.
- Durable writes go only through UWG.
- UNKNOWN is never PASS.
- NOT_APPLICABLE requires reason.
- Missing applicable GateVerdict is UNKNOWN, not PASS.

---

## Source Facts from apps_rg.zip

- `apps_rg/contracts/apps_rg_ingress_contract_v1.py` in the zip does not include `runtime_customization_package`.
- `apps_rg/config/l0_policy.yaml` declares `l3_bypass.always=true` and `c0_bypass.always=true` (stale — reconcile).
- `apps_rg/config/route_registry.yaml` declares `execution_form=DETERMINISTIC_PIPELINE` and `l3_required=false` (stale).
- `apps_rg/config/l3_dag.yaml` is a static auditable DAG, not runtime L3 orchestration.
- `apps_rg/integrations/hops/*` are quarantined and raise `RuntimeError`.
- `apps_rg/integrations/gates/*` are quarantined and raise `RuntimeError`.
- `apps_rg/prompt_assembly/rg_pa_compiler.py` and `prompt_assembly/contracts.py` are quarantined.
- `apps_rg/engines/judges/executive_positioning_judge.py` is quarantined.
- `apps_rg/config/domain_contract/` contains useful declarative refs (see Phase 5).
- `apps_rg/config/hop_pipeline.py` defines a 7-stage HOP topology: HOP1 clerk_extraction, HOP2 data_enrichment, HOP3 resume_generation, HOP4 fact_check, HOP5 bullet_diversity_gate, HOP6 content_optimizer, HOP7 generation_diagnostics.

---

## Wave Structure — Rebaselined After W10 (2026-05-11)

> **REBASELINE NOTE**: Original W10-W14 tail superseded. See `## ORIGINAL TAIL — SUPERSEDED` below for archived original content.

| Wave | Focus | Status |
|------|-------|--------|
| RB0 | Archive old W3+ | ✅ DONE |
| RB1 | Source reconciliation audit | ✅ DONE |
| RB2 | U0 runtime customization package | ✅ DONE |
| RB3 | L1/L0 managed workflow routing | ✅ DONE |
| RB4 | apps_rg declarative domain package | ✅ DONE |
| RB5 | Generic L3 managed workflow runner | ✅ DONE |
| RB6 | Generic L2 ensemble lane | ✅ DONE |
| RB7 | Prompt Assembly profile consumption | ✅ DONE |
| RB8 | GateMesh + Exit harness (G21–G28) | ✅ DONE |
| BR1 | agentic_core leakage repair | ✅ DONE |
| RB9 | Stubbed full-spine E2E | ✅ DONE |
| RB10 | L6 → UWG → L4 writeback | ✅ DONE |
| RB11 | Final no-bypass certification and W10 leakage scan | ✅ DONE |
| RB12 | Guarded route activation readiness | ✅ DONE |
| RB13 | Live provider and real LLM judge integration | ✅ DONE |
| RB14 | apps_rg quality parity and regression proof | ✅ DONE |
| RB15 | Final restoration receipt and plan closure | ✅ DONE |
| RB16 | Judge boundary cleanup — config-driven informational-only | ✅ DONE |

---

## Phase-Level Summary — Rebaselined After W10

| Phase ID | Title | Scope (files) | Pain Points | Status |
|----------|-------|---------------|-------------|--------|
| RB0 | Archive W3+ | receipt + archival marker | Already done — verified | ✅ DONE |
| RB1 | Source Reconciliation Audit | 20-row audit matrix, receipts | Zip vs live repo conflict resolution | ✅ DONE |
| RB2 | U0 Package | ingress contract, schema, field map, u0 adapter | 24-field package completeness | ✅ DONE |
| RB3 | L1/L0 Routing | l1_binding, l0_binding, route_contract, workflow_registry | No route authority leakage; stale bypass flags | ✅ DONE |
| RB4 | Domain Config | workflow_manifest, runtime_gate_profile, exit_profile, section_prompts, candidate_gates | Quarantine boundary, declarative only | ✅ DONE |
| RB5 | L3 Runner | managed_workflow_runner, workflow_registry, sealed_workflow_types | Generic, no resume hardcoding | ✅ DONE |
| RB6 | L2 Ensemble | ensemble_lane, candidate_gate_runner, judge_jury_runner, ensemble_types | No quarantine imports, no hardcoding | ✅ DONE |
| RB7 | PA Profile Consumption | apps_rg_pa_binding, prompt profiles | PA uses domain contract refs only | ✅ DONE |
| RB8 | GateMesh + Exit Harness | exit_gate_harness, gate_evaluators G21–G28, gate_mesh, exit_profile.json | G24/G26 completeness; G28 required for Exit | ✅ DONE |
| BR1 | Leakage Repair | agentic_core boundary scan + repair | apps_rg-specific code removed from core | ✅ DONE |
| RB9 | Stubbed Full-Spine E2E | test_apps_rg_full_spine_stubbed_e2e.py (26 tests) | G24 provenance fields; G28 required (not conditional) | ✅ DONE |
| RB10 | L6/UWG Writeback | runtime_exhaust_bundle, writeback_proposer, universal_write_gate, write_adapters (57 tests) | No current-run mutation; semantic cache off by default | ✅ DONE |
| RB11 | Final No-Bypass Certification | leakage scan; no-bypass proof; certification receipt | No direct L4 from Exit/L6/L2/L3; UWG enforced | ✅ DONE |
| RB12 | Activation Readiness | activation_policy.py; test_apps_rg_guarded_activation_readiness.py (29 tests) | Guarded activation policy; stub_only enforcement; rollback proof | ✅ DONE |
| RB13 | Live Provider + Real Judge | provider_gateway.py, llm_judge_gateway.py, judge_registry.py (20+ tests) | Provider gateway generic; stub_only enforced; judge abstain/fail-closed; G22/G25 integration | ✅ DONE |
| RB14 | Quality Parity + Regression | test_apps_rg_quality_parity.py (31 tests) + full spine suite | parity suite vs prior pipeline; 122 tests green | ✅ DONE |
| RB15 | Final Restoration Receipt | full-spine receipt; plan closure | All DoD rows verified | ✅ DONE |
| RB16 | Judge Boundary Cleanup | grader_roster.yaml; judge_registry.py | Config-driven informational-only; removes core hardcoding | ✅ DONE |

---

## PHASE 0 — Archive Old W3+ Active Authority ✅ DONE

> **Status**: Prior archival receipt exists at `artifacts/apps_rg/apps_rg_w3_plus_archival_receipt.json`.  
> Plan file already marked `ARCHIVED_SUPERSEDED` at `apps-rg-ensemble-judge-restoration-a7c4e2.md`.  
> Notion page `35d27693-f55c-81ed-b5b1-db110843992f` updated to Archived.

**Action**: Verify prior archival is complete and update `superseded_by` field if needed to reference this plan slug (`apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2`).

**Archival receipt path**: `artifacts/apps_rg/apps_rg_w3_plus_archival_receipt.json`

---

## PHASE 1 — Source Reconciliation Audit ✅ DONE

Compare:
1. extracted apps_rg.zip
2. live repo `apps_rg/`
3. live repo `agentic_core/`
4. existing tests
5. existing receipts

**Audit questions (20)**:
1. Does live AppsRgIngressContractV1 already have `runtime_customization_package`?
2. Does live schema include `runtime_customization_package`?
3. Does live field map cover `runtime_customization_package`?
4. Does U0 preserve `runtime_customization_package` into `ValidatedRequest.app_payload`?
5. Does live L0 still follow zip policy with `l3_bypass=true`?
6. Does live L0 already support managed_workflow for apps_rg?
7. Does live RouteContract support `workflow_ref`?
8. Does live workflow registry resolve apps_rg workflow refs?
9. Are quarantined HOPs still quarantined?
10. Are any quarantined runtime files accidentally imported?
11. Does agentic_core have generic L3 ManagedWorkflowRunner?
12. Does agentic_core have generic L2 ENSEMBLE_MODEL lane?
13. Does agentic_core have candidate gate runner?
14. Does agentic_core have judge jury runner?
15. Does Exit consume SealedWorkflowPackage?
16. Does Exit require GateMeshResult before X3?
17. Does L6 `writeback_proposer` exist?
18. Does UWG-only writeback exist?
19. Are runtime gates executable or docs-only?
20. Are LLM judges executable through core or quarantined in apps_rg?

**Audit receipt**: `artifacts/apps_rg/apps_rg_full_runtime_implementation_audit_receipt.json`

**Do not implement until audit matrix is written.**

---

## PHASE 2 — U0 apps_rg Runtime Customization Package ✅ DONE

If live repo already has `runtime_customization_package` from Wave 2.5 and tests pass → mark IMPLEMENTED, do not duplicate.

**Known baseline**: Wave 2.5 reported complete, 56/56 tests passed, receipt at `artifacts/apps_rg/apps_rg_wave_2_5_u0_reconciliation_receipt.json`.

### Required U0 package fields (24)
`package_id`, `package_version`, `app_id`, `task_class`, `spine_profile_ref`, `workflow_manifest_ref`, `runtime_gate_profile_ref`, `exit_profile_ref`, `judge_profile_ref`, `eval_rubric_ref`, `threshold_profile_ref`, `grader_roster_ref`, `rubric_output_map_ref`, `negative_controls_ref`, `learning_profile_ref`, `meta_feedback_profile_ref`, `prompt_profile_ref`, `route_profile_ref`, `retrieval_profile_ref`, `repair_profile_ref`, `cache_profile_ref`, `capability_profile_ref`, `orchestration_profile_ref`, `provider_profile_ref`, `write_policy`, `required_runtime_gates`, `required_exit_gates`, `conditional_exit_gates`, `judge_execution_policy`, `eval_execution_policy`, `meta_feedback_policy`, `l6_learning_policy`, `package_digest`

### Files to inspect/update
- `apps_rg/contracts/apps_rg_ingress_contract_v1.py`
- `apps_rg/contracts/apps_rg_ingress_contract.v1.schema.json`
- `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml`
- `agentic_core/runtime/u0/apps_rg_u0_adapter.py`
- `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` if active

### Tests
- `test_apps_rg_ingress_accepts_runtime_customization_package`
- `test_apps_rg_ingress_rejects_unknown_runtime_package_field`
- `test_apps_rg_field_map_covers_every_runtime_customization_pointer`
- `test_apps_rg_u0_reflection_preserves_runtime_package`
- `test_apps_rg_runtime_package_digest_required`
- `test_apps_rg_runtime_package_digest_mismatch_fails`
- `test_apps_rg_effective_output_contract_resolves_from_u0_package`
- `test_apps_rg_missing_output_contract_fails_closed`
- `test_apps_rg_no_runtime_package_pointer_silently_dropped`

---

## PHASE 3 — L1 apps_rg Planning ✅ DONE

### Expected L1 behavior
- Consume `ValidatedRequest`
- Identify `task_class=resume_generation`
- Classify `generation_mode`
- Emit `L1PlanContract`
- Add hints: `multiple_work_units_hint`, `merge_required_hint`, `per_unit_quality_selection_hint`, `candidate_generation_expected_hint`, `managed_workflow_candidate_hint`, `grounding_required_hint`, `prompt_assembly_required_hint`, `exit_eval_required_hint`

### L1 must NOT
- Route, execute, retrieve final evidence, assemble prompts

### Files
- `agentic_core/L1_cognition/apps_rg_l1_binding.py`
- `agentic_core/runtime/contracts/l1_plan_contract.py`
- `apps_rg/L1_cognition/jd_planner.py` (domain planning source only, if still active)

### Tests
- `test_apps_rg_l1_emits_work_shape_hints`
- `test_apps_rg_l1_does_not_select_route`
- `test_apps_rg_l1_does_not_execute`
- `test_apps_rg_l1_managed_workflow_hint_for_resume_generation`
- `test_apps_rg_l1_generation_mode_affects_hints_without_route_authority`

---

## PHASE 4 — L0 apps_rg Routing Reconciliation ✅ DONE

The zip L0 policy is **stale** — it declares `c0_bypass.always=true`, `l3_bypass.always=true`, `execution_form=DETERMINISTIC_PIPELINE`, `l3_required=false`. Reconcile into final route model.

### Final apps_rg L0 route model

1. **R1A** exact cache lookup — hit returns RET to Exit; L0 never writes cache
2. **R1B** semantic cache — disabled by default (`semantic_cache_enabled=false`); L0 never writes cache
3. **R5** fallback — missing/stale prerequisites; emits terminal packet to Exit
4. **R4_MANAGED_RESUME_WORKFLOW** — default after cache miss; `execution_form=MANAGED_WORKFLOW`; next stage L3

No silent fallback to `SINGLE_STEP` after `MANAGED_WORKFLOW` is selected.

### RouteContract must include
`route_id`, `execution_form`, `workflow_ref` (when managed), `r1a_lookup_receipt_ref`, `r1b_lookup_receipt_ref`, `r5_fallback_receipt_ref`, `cache_miss_receipts`, `policy_hash`, `blueprint_hash`, `registry_digest_set`, `runtime_gate_refs`

### Files
- `apps_rg/config/l0_policy.yaml`
- `apps_rg/config/route_registry.yaml`
- `apps_rg/config/domain_contract/route_profiles.yaml`
- `apps_rg/config/domain_contract/cache_profiles.yaml`
- `agentic_core/L0_routing/apps_rg_l0_binding.py`
- `agentic_core/runtime/contracts/route_contract.py`
- `agentic_core/L3_orchestration/workflow_registry.py`

### Tests (10)
- `test_apps_rg_l0_checks_r1a_before_managed_workflow`
- `test_apps_rg_l0_checks_r1b_before_managed_workflow`
- `test_apps_rg_semantic_cache_disabled_by_default_for_final_resume`
- `test_apps_rg_l0_selects_managed_workflow_after_cache_miss`
- `test_apps_rg_l0_fails_closed_on_missing_workflow_ref`
- `test_apps_rg_l0_fails_closed_on_zero_workflow_matches`
- `test_apps_rg_l0_fails_closed_on_multiple_workflow_matches`
- `test_apps_rg_l0_fails_closed_on_registry_digest_mismatch`
- `test_apps_rg_l0_emits_exactly_one_route_contract`
- `test_apps_rg_l0_never_writes_cache`

---

## PHASE 5 — apps_rg Domain Config for Managed Workflow ✅ DONE

Convert useful zip configs and quarantined HOP source material into **declarative** runtime profiles.  
**Do not unquarantine runtime authority. Do not import `apps_rg.integrations.hops` at runtime.**

### Files to create/update
- `apps_rg/config/domain_contract/runtime_customization_package.resume_generation.v1.json`
- `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json`
- `apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json`
- `apps_rg/config/domain_contract/meta_feedback_profile.resume_generation.v1.json`
- `apps_rg/config/workflow_manifest.resume_generation.v1.yaml`
- `apps_rg/config/provider_profiles.yaml`
- `apps_rg/config/candidate_gates.yaml`
- `apps_rg/config/judge_rubrics/*.yaml`
- `apps_rg/config/section_prompts/*.yaml`

### Minimum workflow manifest section nodes
`header_block`, `professional_summary`, `skills_block`, `experience_block`, `education_block`, `certifications_block` (optional), `selected_projects_block` (optional), `publications_block` (optional), `final_render`, `ats_validate`, `factual_grounding_check`, `no_fabrication_guardrail`

### Legacy per-section HOP nodes (declarative restoration)
`headline`, `exec_summary`, `competencies`, `unify_bullets`, `ibm_bullets`, `tradersense_bullets`, `ey_bullets`, `marquee`, `final_merge`

Each node must declare: `node_id`, `node_type`, `tier`, `depends_on`, `candidate_count`, `generator_profile`, `temperature_profile`, `prompt_variant_refs`, `candidate_gate_profile`, `judge_profile`, `selection_policy`, `archive_policy`, `output_schema_ref`, `required_runtime_gates`

---

## PHASE 6 — Core L3 ManagedWorkflowRunner ✅ DONE

Generic, not apps_rg-specific.

### Files
- `agentic_core/L3_orchestration/managed_workflow_runner.py`
- `agentic_core/L3_orchestration/workflow_registry.py`
- `agentic_core/L3_orchestration/section_merge_engine.py`
- `agentic_core/runtime/contracts/workflow_manifest_types.py`
- `agentic_core/runtime/contracts/sealed_workflow_types.py`
- `agentic_core/runtime/contracts/l3_to_l2_step_contract.py`

### L3 responsibilities
- Consume `RouteContract` with `execution_form=MANAGED_WORKFLOW`
- Resolve `workflow_ref` via registry, validate manifest digest
- Topologically sort nodes, detect cycles
- Emit one `L3ToL2StepContract` per ready node
- Call injected L2 executor once per node
- Collect `SealedSectionArtifact` per node
- Merge into `SealedWorkflowPackage`
- Write stage-output receipts, emit workflow ledger/checkpoint refs
- Consume/emit G18/G19/G20/G25 gate refs as applicable

### L3 must NOT
- Execute model/tool/provider calls, retrieve evidence, assemble prompts, write L4, emit X3, hardcode resume section names, hardcode provider names, silently fallback to single-step

### Tests (15)
- `test_l3_runner_rejects_non_managed_workflow_route`
- `test_l3_runner_fails_when_workflow_ref_missing`
- `test_l3_runner_fails_on_manifest_digest_mismatch`
- `test_l3_runner_topologically_orders_nodes`
- `test_l3_runner_fails_on_cycle`
- `test_l3_runner_emits_one_step_contract_per_node`
- `test_l3_runner_calls_l2_executor_once_per_ready_node`
- `test_l3_runner_fails_closed_on_critical_node_failure`
- `test_l3_runner_policy_allows_noncritical_skip_only_when_configured`
- `test_l3_runner_produces_sealed_workflow_package`
- `test_l3_runner_writes_stage_output_receipts`
- `test_l3_runner_no_resume_section_names_in_core`
- `test_l3_runner_no_provider_hardcoding_in_core`
- `test_l3_runner_never_writes_l4`
- `test_l3_runner_never_emits_x3`

---

## PHASE 7 — Core L2 apps_rg Execution via Generic ENSEMBLE_MODEL Lane ✅ DONE

### Files
- `agentic_core/L2_execution/ensemble_lane.py`
- `agentic_core/L2_execution/candidate_gate_runner.py`
- `agentic_core/L2_execution/judge_jury_runner.py`
- `agentic_core/runtime/contracts/ensemble_types.py`
- `agentic_core/runtime/contracts/judge_types.py`
- `agentic_core/runtime/contracts/sealed_workflow_types.py`

### L2 behavior
- Receive one bounded node
- Generate N candidates using `provider_profile` through core gateway
- Run candidate gates; fail closed if all fail and no repair policy exists
- Run judge jury when required
- Select winner, seal `SealedSectionArtifact`
- No direct L4 write, no route change, no workflow expansion, no provider hardcoding, no quarantine imports

### Tests (11)
- `test_l2_ensemble_generates_expected_candidate_count`
- `test_l2_ensemble_uses_provider_profile_registry_key`
- `test_l2_ensemble_no_provider_hardcoding`
- `test_l2_candidate_gate_runner_blocks_all_failed_candidates`
- `test_l2_candidate_gate_runner_runs_apps_rg_gate_config_without_importing_quarantined_modules`
- `test_l2_judge_jury_selects_winner`
- `test_l2_judge_jury_fails_closed_when_required_judge_missing`
- `test_l2_seals_section_artifact`
- `test_l2_never_writes_l4`
- `test_l2_never_emits_x3`
- `test_l2_executes_one_bounded_node_only`

---

## PHASE 8 — PA Profile + Gate Mesh + Exit Harness ✅ DONE

> **Delivered**: `apps_rg_exit_binding.py`, `exit_gate_harness.py`, `gate_evaluators.py` (G21–G28), `gate_mesh.py`, `gate_types.py`, `gate_profile_resolver.py`, `exit_profile.resume_generation.v1.json`, `runtime_gate_profile.resume_generation.v1.json`.
>
> **G28 STATUS (rebaselined 2026-05-11)**: G28 is **required** for Exit. G28 PASS requires material audit refs. G28 WARN is allowed only for optional observability gaps that are not material to the audit trail. Missing material G28 evidence blocks `ALLOW_FINISH`. This supersedes any earlier statement that G28 was moved to conditional, advisory-only, or removed from `required_exit_gates`.

Core PA must:
- Resolve apps_rg `prompt_profile_ref`, `prompt_bom.yaml`, `prompt_registry.yaml`
- Preserve canonical slot order: S0, D0, I0, E0, C0, M0/Y0, U0, H0, R0
- Treat JD/resume/company brief/prior artifacts/C0 evidence as data only
- Bind output schema as R0
- Emit `CompiledPromptArtifact`, sign prompt artifact, emit prompt hash / component hash map / replay manifest

**apps_rg must NOT**: compile prompt in app runtime code, call providers, emit core prompt contracts from quarantined files.

### Tests (8)
- `test_apps_rg_pa_resolves_prompt_bom`
- `test_apps_rg_pa_resolves_prompt_registry`
- `test_apps_rg_pa_preserves_authority_order`
- `test_apps_rg_retrieved_or_preloaded_text_remains_data`
- `test_apps_rg_pa_blocks_prompt_injection_from_user_resume`
- `test_apps_rg_pa_emits_compiled_prompt_artifact`
- `test_apps_rg_pa_missing_template_fails_closed`
- `test_apps_rg_pa_does_not_import_quarantined_app_compiler`

---

## PHASE 9 — Managed Workflow E2E Test Suite ✅ DONE

> **Delivered**: `agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py` (dispatch function + `build_w9_success_evidence` + `_fake_generator_gateway`), `tests/_apps_contract/test_apps_rg_full_spine_stubbed_e2e.py` (**26/26 passing**).
>
> Root causes fixed: G24 required 16 provenance fields (all now supplied), G26 threshold 0.99 (was 0.96). G24 repair receipt: `artifacts/apps_rg/apps_rg_w9_g24_provenance_and_x3d_success_repair_receipt.json`. G28 repair receipt: `artifacts/apps_rg/apps_rg_w9_g28_required_gate_repair_receipt.json`.
>
> **G28 CORRECTION (rebaselined 2026-05-11)**: G28 is **required** for Exit. G28 PASS requires material audit refs. G28 WARN is allowed only for optional observability gaps. Missing material G28 evidence blocks `ALLOW_FINISH`. Any prior statement that G28 was "moved to conditional" or is "advisory only" is incorrect and superseded.
>
> Test activates managed workflow via `APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1` + `APPS_RG_EXECUTION_FORM=managed_workflow`. Verifies: `X3D_ALLOW_FINISH` on success path, no cache/vector/L4 writes, no quarantined imports, full stage-receipt completeness, gate-mesh required before Exit, exactly one X3.
>
> **DISTINCTION**: This is stubbed E2E — no real LLM/provider calls. Real provider and judge integration is deferred to RB13.
>
> W9 receipt: `artifacts/apps_rg/apps_rg_w9_full_spine_stubbed_e2e_receipt.json`

### Required stage gates by layer

| Layer | Gates |
|-------|-------|
| U0 | G01, G02, G03-lite, G04-lite, G17-lite |
| L1 | G03, G04, G05, G18 |
| L0 | G07, G08, G10, G20 |
| C0/evidence | G08, G09, G13, G17, G23, G24 |
| PA | G10, G13, G17, G21, G23 |
| L3 | G18, G19, G20, G25 |
| L2 | G11, G12, G13, G14, G15, G17, G19, G20, G21, G23, G24, G28 |
| Exit | G21, G22, G23, G24, G25, G26, G27, G28 |
| L6 | G28, G29 |

### apps_rg-specific gate rules

**G21**: Use `output_schema.yaml`. Hard fail on: missing required section, malformed record, experience/skill/education not in candidate_profile, invalid date range, fabricated employer/title/degree/publication.

**G22**: Use `eval_rubrics.yaml` + `threshold_profiles.yaml`. Thresholds: `overall_pass≥0.75`, `factual_grounding≥0.95`, `role_alignment≥0.65`, `ats_readability≥0.80`, `specificity≥0.55`, `concision≥0.60`, `format_compliance≥0.95`, `no_fabrication≥0.99`. `executive_positioning`: informational only by default.

**G23**: Hard fail: prompt leakage, system instruction leakage, credential/secret leakage, cross-tenant leakage, unauthorized PII, fabrication instructions.

**G24**: Require: `request_id`, `run_id`, `trace_root`, `replay_key`, candidate_profile/resume/JD/role spec hashes, all config ref hashes, sealed artifact refs, output artifact digest.

**G27**: Default `NOT_APPLICABLE` for read-only resume return. Required when: `proposed_state_diff` exists, cache/memory/promotion writes requested.

### Tests (11)
- `test_apps_rg_runtime_gate_profile_declares_required_stage_gates`
- `test_apps_rg_missing_gate_is_unknown_not_pass`
- `test_apps_rg_not_applicable_requires_reason`
- `test_apps_rg_exit_blocks_missing_gate_mesh`
- `test_apps_rg_exit_blocks_material_unknown`
- `test_apps_rg_exit_blocks_g21_schema_failure`
- `test_apps_rg_exit_blocks_g22_no_fabrication_below_threshold`
- `test_apps_rg_exit_blocks_g23_prompt_leakage`
- `test_apps_rg_g27_not_applicable_with_reason_for_read_only_resume_return`
- `test_apps_rg_g27_required_for_cache_writeback`
- `test_apps_rg_executive_positioning_informational_only_by_default`

---

## CURRENT STATUS SNAPSHOT (rebaselined after W11 2026-05-11)

| Receipt | Path |
|---------|------|
| BR1 leakage repair | `artifacts/apps_rg/apps_rg_br1_agentic_core_leakage_repair_receipt.json` |
| W9 stubbed E2E | `artifacts/apps_rg/apps_rg_w9_full_spine_stubbed_e2e_receipt.json` |
| G24 repair | `artifacts/apps_rg/apps_rg_w9_g24_provenance_and_x3d_success_repair_receipt.json` |
| G28 required-gate repair | `artifacts/apps_rg/apps_rg_w9_g28_required_gate_repair_receipt.json` |
| W10 L6/UWG writeback | `artifacts/apps_rg/apps_rg_w10_l6_uwg_writeback_receipt.json` |
| **W11 final no-bypass certification** | `artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json` |

**Certification verdict**: PASS — apps_rg full-spine is certified-ready for route activation. Zero blockers. Two non-blocking gaps documented and deferred.

**Tests passing**: 217 (W11 certification suite) + 294 (W9-W10 suites) = 511 total tests passing.

**Route status**: `route_registry.yaml` → `registered_not_active`. Route activation explicitly gated to RB12.

**Next active prompt**: RB12 guarded route activation readiness. Do not proceed to RB13 (live provider integration) until RB12 completes.

### G28 Language Confirmation

G28 is **required** for Exit. G28 PASS requires material audit refs. G28 WARN is allowed only for optional observability gaps that are not material to the audit trail. Missing material G28 evidence blocks `ALLOW_FINISH`. This is enforced, not conditional/advisory-only.

---

## RB11 COMPLETED — Final No-Bypass Certification ✅

W11 final no-bypass certification completed successfully. Receipt: `artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json`

**Certification verdict**: PASS  
**Activation blockers**: 0  
**Non-blocking gaps**: 2 (documented in receipt, deferred to future waves)

### RB11 Scope Completed
- ✅ Full leakage scan: confirmed no direct L4 writes from Exit/L0/L2/L3/PA/L6/C0.
- ✅ Confirmed no bypass of UWG on any write path.
- ✅ Confirmed no quarantined imports anywhere in the runtime path.
- ✅ Confirmed G28 is required (not conditional/advisory) in `exit_profile.resume_generation.v1.json`.
- ✅ Emitted W11 certification receipt.

### RB12 NEXT — Guarded Route Activation Readiness

> **Route remains `registered_not_active`. Do NOT activate before RB12 passes.**  
> **Do NOT proceed to RB13 (live provider integration) until RB12 completes.**

RB12 scope:
- Activation checklist verification
- Route registry status transition planning (`registered_not_active` → `active`)
- Guarded activation criteria definition
- No broad production activation without explicit approval

---

## ORIGINAL TAIL — SUPERSEDED BY REBASELINE

> **ORIGINAL_TAIL_STATUS: SUPERSEDED_BY_REBASELINE**  
> Reason:
> - Exit X1-X3 was already implemented in RB7/RB8 (was W8).
> - Full-spine stubbed E2E was already implemented in RB9 (was W9).
> - L6/UWG writeback was already implemented in RB10 (was W10).
> - Final no-bypass certification completed in RB11 (was W11) with certification_verdict: PASS.
> - Real LLM judge/provider integration remains deferred to RB13.
> - Route activation must wait for RB12 guarded activation readiness wave.
>
> Original Phase 10-14 content preserved below for historical reference only.

---

## [ARCHIVED] PHASE 10 — LLM Judges Customized to Runtime Gates

**Do not unquarantine** `apps_rg/engines/judges/executive_positioning_judge.py`.

### Judge ownership split
- **apps_rg owns**: `grader_roster.yaml`, `judge_rubrics/*.yaml`, `threshold_profiles.yaml`, `eval_rubrics.yaml`, calibration refs, test fixtures
- **core owns**: judge invocation, provider calls, timeout handling, result normalization, GateVerdict conversion, calibration record attachment

### Required judge mappings
| Judge | Type | Gate |
|-------|------|------|
| `factual_grounding` | deterministic | hard |
| `ats_readability` | deterministic | hard |
| `format_compliance` | deterministic | hard |
| `no_fabrication` | deterministic | hard |
| `concision` | deterministic | hard/soft per threshold profile |
| `role_alignment` | hybrid | required |
| `specificity` | hybrid | required |
| `executive_positioning` | llm_as_judge | informational only by default |

### Tests (10)
- `test_apps_rg_grader_roster_loads`
- `test_apps_rg_required_deterministic_graders_fail_closed_when_missing`
- `test_apps_rg_hybrid_role_alignment_required`
- `test_apps_rg_hybrid_specificity_required`
- `test_apps_rg_executive_positioning_judge_informational_only_by_default`
- `test_apps_rg_llm_judge_result_converts_to_g22_evidence`
- `test_apps_rg_judge_disagreement_can_trigger_g25`
- `test_apps_rg_missing_required_judge_output_fails_closed`
- `test_apps_rg_judge_timeout_fails_closed_for_required_dimension`
- `test_apps_rg_judge_timeout_warns_only_for_informational_dimension`

---

## [ARCHIVED] PHASE 11 — Exit X1-X3 for apps_rg

> **SUPERSEDED**: Exit X1-X3 was delivered in W8 (RB7/RB8). This phase is archived.

Core Exit must consume: `RET` terminal packet, `SealedL2Artifact`, `SealedWorkflowPackage`, `ReClearedHITLPacket` (if applicable).

### X1 checks
X1A Today's Rules, X1B Answered It, X1C Safe to Leave, X1D Answer Good, X1E Trajectory OK, X1F Story Adds Up, X1G Replay Eligible, X1H Observable, X1I Consistency (if activated), X1J Write Eligibility

### Allowed X3 dispositions
`X3A_DENY_REROUTE`, `X3B_ESCALATE_HITL`, `X3C_COMMIT_REQUEST_TO_UWG`, `X3D_ALLOW_FINISH`, `X3E_SAFE_ABSTAIN`

**Important**: If output is returned AND writeback proposed → current-run disposition is `X3D_ALLOW_FINISH`. Post-runtime writeback belongs to `RuntimeExhaustBundle → L6 writeback_proposer → UWG → L4`. **Do not use Exit to write cache/evidence.**

### Exit must NOT
Write Redis, Chroma, cache, vector store, L4, durable state; call providers; execute tools; return output without X3.

### Tests (10)
- `test_apps_rg_exit_requires_gate_mesh_result`
- `test_apps_rg_exit_emits_exactly_one_x3`
- `test_apps_rg_exit_accepts_sealed_workflow_package`
- `test_apps_rg_exit_blocks_missing_sealed_artifact`
- `test_apps_rg_exit_blocks_material_unknown_for_allow_finish`
- `test_apps_rg_exit_blocks_commit_without_g27_g28`
- `test_apps_rg_exit_never_writes_redis`
- `test_apps_rg_exit_never_writes_chroma`
- `test_apps_rg_exit_never_writes_l4`
- `test_apps_rg_success_with_writeback_candidate_still_returns_x3d_and_defers_writeback_to_l6`

---

## [ARCHIVED] PHASE 12 — L6 Meta-Learning Customized for apps_rg

> **SUPERSEDED**: L6 meta-learning and RuntimeExhaustBundle were delivered in W10 (RB10). This phase is archived.

### Learning profile (`lp::apps_rg::resume_generation::v1`)
- `promotion_threshold: 0.65`
- `min_n_each_arm: 30`
- `holdout_required: true`
- `judge_calibration_cadence_days: 14`
- `regret_budget: 0.10`
- `z_score: 1.96`
- `uplift_required: true`

### L6 responsibilities
Evaluate: output quality, trajectory, judge disagreement, repeated fabrication/schema failures, candidate gate failure patterns, prompt variant performance, section-level performance, cache/evidence reuse eligibility. Emit inert `FutureRunPromotionRequest` only. UWG admits or blocks.

### L6 must NOT
Rescue current run, mutate current run, write L4 directly, update prompt/rubric/policy/registry directly, bypass UWG.

### Tests (9)
- `test_apps_rg_runtime_exhaust_contains_learning_refs`
- `test_apps_rg_l6_runs_only_after_current_run_boundary`
- `test_apps_rg_l6_cannot_rescue_current_run`
- `test_apps_rg_l6_future_run_promotion_requires_holdout`
- `test_apps_rg_l6_future_run_promotion_requires_min_n`
- `test_apps_rg_l6_future_run_promotion_requires_uwg`
- `test_apps_rg_l6_judge_calibration_uses_learning_profile`
- `test_apps_rg_l6_prompt_variant_learning_is_inert_before_uwg`
- `test_apps_rg_l6_no_direct_l4_write`

---

## [ARCHIVED] PHASE 13 — UWG and Writeback

> **SUPERSEDED**: UWG writeback (FutureRunPromotionRequest, StateCommitReceipt, BlockedWriteReceipt) was delivered in W10 (RB10). This phase is archived.

### Cache policy
- `semantic_cache_enabled=false` by default
- Exact cache: allowed only if user-scoped and policy permits
- No cache write before Exit clears
- No writeback during current-run output path
- L6 proposes only after `RuntimeExhaustBundle`

### Contract types
`FutureRunPromotionRequest`, R1A/R1B promotion payloads, C0/local evidence promotion payload, index refresh payload, `UWGAdmissionResult`, `StateCommitReceipt`, `BlockedWriteReceipt`

### Tests (9)
- `test_apps_rg_l0_reads_cache_only`
- `test_apps_rg_l2_never_writes_cache`
- `test_apps_rg_l3_never_writes_cache`
- `test_apps_rg_exit_never_writes_cache`
- `test_apps_rg_l6_writeback_proposer_creates_inert_future_run_promotion`
- `test_apps_rg_uwg_admits_or_blocks_cache_promotion`
- `test_apps_rg_l4_accepts_cache_write_only_from_uwg`
- `test_apps_rg_semantic_cache_writeback_disabled_by_default`
- `test_apps_rg_c0_evidence_writeback_uwg_only`

---

## [ARCHIVED] PHASE 14 — End-to-End Parity and Proof

> **SUPERSEDED**: Stubbed full-spine E2E was delivered in W9 (RB9). Full parity with real providers is now RB13+RB14.

### E2E test scenarios
- Stubbed no-provider managed workflow run
- Full spine: U0 → L1 → L0 → L3 → L2 stub → Exit → RuntimeExhaustBundle
- Candidate generation stub with 3 candidates
- Deterministic gate failure case
- Judge jury selection case
- Schema failure case
- `no_fabrication` failure case
- Degraded success case
- Safe abstain case
- Post-runtime L6 writeback proposal case
- No-bypass proof

### Required artifacts per run (15+)
`00_parse_envelope.json`, `01_U0_validated_request.json`, `02_L1_plan_contract.json`, `03_L0_route_contract.json`, `03a_R1A_cache_lookup_receipt.json`, `03b_R1B_cache_lookup_receipt.json`, `03c_R5_fallback_receipt.json` (if fallback), `04_C0_or_local_evidence_contract.json`, `05_PA_compiled_prompt.json`, `06_L3_workflow_manifest_resolved.json`, `07_L3_to_L2_step_contract_<node>.json`, `08_L2_candidate_artifacts_<node>.json`, `09_L2_gate_results_<node>.json`, `10_L2_judge_results_<node>.json`, `11_L2_selection_receipt_<node>.json`, `12_L2_sealed_section_<node>.json`, `13_L3_sealed_workflow_package.json`, `14_Exit_disposition_receipt.json`, `99_runtime_exhaust_bundle.json`, `15_l6_future_run_promotion_request_*.json` (optional, after runtime boundary)

### Tests (10)
- `test_apps_rg_full_spine_stubbed_managed_workflow_e2e`
- `test_apps_rg_stage_output_receipts_complete`
- `test_apps_rg_no_quarantined_runtime_imports`
- `test_apps_rg_no_core_provider_hardcoding`
- `test_apps_rg_no_core_resume_section_hardcoding_except_registry_fixtures`
- `test_apps_rg_no_direct_l4_writes`
- `test_apps_rg_unknown_never_pass`
- `test_apps_rg_not_applicable_requires_reason`
- `test_apps_rg_exactly_one_x3`
- `test_apps_rg_runtime_exhaust_after_exit_only`

**Final receipt**: `artifacts/apps_rg/apps_rg_zip_based_full_spine_runtime_restoration_receipt.json`

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| DoD-1 | Old W3+ active authority archived and preserved | Receipt exists at `artifacts/apps_rg/apps_rg_w3_plus_archival_receipt.json`; plan file marked `ARCHIVED_SUPERSEDED` |
| DoD-2 | Source reconciliation audit matrix written | `artifacts/apps_rg/apps_rg_full_runtime_implementation_audit_receipt.json` exists and covers all 20 audit questions |
| DoD-3 | U0 `runtime_customization_package` complete | 56/56 Wave 2.5 tests pass OR new tests added and pass; no silent field drop |
| DoD-4 | L0 routes cache miss to `MANAGED_WORKFLOW` | `test_apps_rg_l0_selects_managed_workflow_after_cache_miss` passes |
| DoD-5 | L3 orchestrates managed workflow nodes generically | `test_l3_runner_no_resume_section_names_in_core` passes |
| DoD-6 | L2 executes one bounded node at a time | `test_l2_executes_one_bounded_node_only` passes |
| DoD-7 | Exit emits exactly one X3 | `test_apps_rg_exit_emits_exactly_one_x3` passes |
| DoD-8 | Quarantined runtime code not imported | `test_apps_rg_no_quarantined_runtime_imports` passes |
| DoD-9 | All targeted tests pass; gaps listed in receipt | Final receipt exists at `artifacts/apps_rg/apps_rg_zip_based_full_spine_runtime_restoration_receipt.json` |
| DoD-10 | Smoke run exits 0 | `python -m apps_rg --dry-run` exits 0 with no quarantine import errors |

### Verification-vs-Deferral

| Item | Verify in this plan | Defer |
|------|--------------------|----|
| Real LLM inference (Qwen 32B) | No — stubbed | Defer to live run |
| Per-section HOP logic | No — declarative config only | Defer to future phase |
| UWG promotion to L4 | Stub/contract only | Defer to L4 integration plan |
| holdout corpus calibration | No | Defer to L6 calibration plan |

---

## Acceptance Criteria

- Old W3+ active authority is archived and preserved.
- apps_rg enters U0 with complete `runtime_customization_package`.
- L1 emits apps_rg work-shape hints without route authority.
- L0 emits exactly one deterministic `RouteContract`.
- L0 routes cache miss + valid prerequisites to `MANAGED_WORKFLOW`.
- `workflow_ref` resolves deterministically.
- L3 orchestrates managed workflow nodes generically.
- L2 executes one bounded node at a time.
- Old quarantined runtime HOP/gate/judge code is not imported.
- Prompt Assembly uses core PA with apps_rg prompt profile/template refs.
- Runtime Gates emit `GateVerdict`s customized by apps_rg profile.
- LLM judges feed G22 and G25 evidence through core judge infrastructure.
- Exit requires `GateMeshResult` and emits exactly one X3.
- L6 meta-learning is apps_rg-customized and future-run only.
- Durable writes go only through UWG.
- All targeted tests pass.
- Remaining gaps are explicit, non-blocking, and listed in the receipt.

---

## Work Sequence

1. Phase 0 — verify W3+ archive (receipt exists)
2. Phase 1 — audit zip vs live repo
3. Phase 2 — implement U0 only if missing or drifted
4. Phase 3 — implement L1 if missing
5. Phase 4 — reconcile L0 routing
6. Phase 5 — implement apps_rg domain config profiles
7. Phase 6 — implement L3 runner if missing
8. Phase 7 — implement L2 ensemble/gate/judge lane if missing
9. Phase 8 — implement core PA profile consumption if missing
10. Phase 9 — implement runtime gates customization
11. Phase 10 — implement judge/eval integration
12. Phase 11 — implement Exit X1-X3 enforcement
13. Phase 12 — implement L6 meta-learning
14. Phase 13 — implement UWG writeback
15. Phase 14 — implement E2E proof
16. Write final receipt

---

## Scope Boundaries

- **Do not** broaden beyond apps_rg.
- **Do not** touch apps_lic or other apps unless anti-regression tests require it.
- **Do not** implement docs-only compliance.
- **Do not** fake gate receipts.
- **Do not** mark quarantined source as active.
- **Do not** bypass core ownership.
