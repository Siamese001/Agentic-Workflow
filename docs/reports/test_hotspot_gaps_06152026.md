# Test Hotspot Gap Report

ADG Provenance: backend=sqlite, snapshot=adg_indexed_06152026_1043.sqlite
Generated: 2026-06-15T18:05:38+00:00
Commit SHA: `093cd5b804ce269042dfeca2293d6b899520780e`

## Summary

- **Total agentic_core modules (excl. __init__):** 2668
- **Modules with matching test_<name>.py:** 1537 (57%)
- **Remaining gaps:** 1131

- **apps_* packages with ADG hotspot paths:** 10
- **apps_* ADG hotspot paths:** 1503
- **apps_* paths reached by test `covers` edges:** 657
- **apps_* distinct covering tests (`covers` source_file):** 857

> **W2 note:** P3 modules may have behavioral coverage in
> `tests/agentic_core/test_p3_w2_hotspot_behavior.py` without a basename match.
> See `artifacts/test_inventory/w2_basename_collision_audit.md`.

## apps_* ADG Test-Reachability Indicator

This table is ADG-backed. `coverage_by_path` is coverage.py line/branch ingestion; `covers` edges are the ADG test-reachability indicator from `tests/%` to app paths. A zero `coverage_by_path` row count does not mean the app is absent from ADG.

| App | ADG source paths | Hotspot paths | Paths reached by `covers` | Distinct covering tests | `covers` edges | `coverage_by_path` rows | Hotspot paths without `covers` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `apps_architect` | 28 | 28 | 0 | 0 | 0 | 0 | 28 |
| `apps_eval` | 29 | 29 | 0 | 0 | 0 | 0 | 29 |
| `apps_eval_legacy` | 76 | 76 | 0 | 0 | 0 | 0 | 76 |
| `apps_exec` | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| `apps_lic` | 250 | 250 | 159 | 147 | 960 | 0 | 91 |
| `apps_qna` | 110 | 110 | 0 | 0 | 0 | 0 | 110 |
| `apps_research` | 100 | 100 | 0 | 0 | 0 | 0 | 100 |
| `apps_rg` | 562 | 562 | 439 | 638 | 2638 | 0 | 123 |
| `apps_shared` | 269 | 269 | 59 | 72 | 205 | 0 | 210 |
| `apps_underwriting_ai` | 78 | 78 | 0 | 0 | 0 | 0 | 78 |

## Top Uncovered apps_* Hotspots by ADG Centrality

| App | Fan-in | Fan-out | Degree | Centrality | Path |
|---|---:|---:|---:|---:|---|
| `apps_shared` | 127 | 8 | 135 | 0.010700 | `apps_shared/config/pipeline_constants_config.py` |
| `apps_shared` | 24 | 12 | 36 | 0.002000 | `apps_shared/validators/proof/proof_contracts.py` |
| `apps_rg` | 23 | 5 | 28 | 0.001900 | `apps_rg/runtime/sections/role_episode_bundle_registry.py` |
| `apps_lic` | 20 | 6 | 26 | 0.001700 | `apps_lic/types/PromptTemplate.py` |
| `apps_rg` | 18 | 13 | 31 | 0.001500 | `apps_rg/runtime/section_repair_lane_integration.py` |
| `apps_rg` | 17 | 11 | 28 | 0.001400 | `apps_rg/runtime/providers/provider_gateway.py` |
| `apps_rg` | 17 | 4 | 21 | 0.001400 | `apps_rg/runtime/sections/ibm_narrative_lane_defaults.py` |
| `apps_rg` | 15 | 11 | 26 | 0.001300 | `apps_rg/runtime/section_proof/section_input_usage_ledger.py` |
| `apps_shared` | 14 | 5 | 19 | 0.001200 | `apps_shared/proof/runtime_drivers/_driver_base.py` |
| `apps_shared` | 14 | 5 | 19 | 0.001200 | `apps_shared/validators/proof/runtime_drivers/_driver_base.py` |
| `apps_rg` | 13 | 8 | 21 | 0.001100 | `apps_rg/runtime/judges/x1d_panel_harness.py` |
| `apps_rg` | 13 | 5 | 18 | 0.001100 | `apps_rg/runtime/spine/governed_pa_c0_contracts.py` |
| `apps_shared` | 12 | 82 | 94 | 0.001000 | `apps_shared/validators/enforcement/ProvenancetrackerStrategy.py` |
| `apps_rg` | 11 | 6 | 17 | 0.000900 | `apps_rg/runtime/sections/executive_summary_regen_support.py` |
| `apps_rg` | 11 | 1 | 12 | 0.000900 | `apps_rg/runtime/offline_contract_status.py` |
| `apps_rg` | 10 | 24 | 34 | 0.000800 | `apps_rg/cache/r1b_ingest.py` |
| `apps_shared` | 10 | 13 | 23 | 0.000800 | `apps_shared/contracts/cross_app/base.py` |
| `apps_rg` | 9 | 10 | 19 | 0.000800 | `apps_rg/runtime/spine_contracts.py` |
| `apps_rg` | 10 | 8 | 18 | 0.000800 | `apps_rg/runtime/sections/companion_lane_context.py` |
| `apps_rg` | 9 | 5 | 14 | 0.000800 | `apps_rg/runtime/sections/lane_artifact_io.py` |
| `apps_shared` | 10 | 3 | 13 | 0.000800 | `apps_shared/adapters/rg_integrations_facade.py` |
| `apps_shared` | 10 | 3 | 13 | 0.000800 | `apps_shared/adapters/system_learning_facade.py` |
| `apps_shared` | 8 | 15 | 23 | 0.000700 | `apps_shared/orchestration/hop_pipeline.py` |
| `apps_rg` | 8 | 9 | 17 | 0.000700 | `apps_rg/runtime/providers/section_provider_call.py` |
| `apps_rg` | 8 | 4 | 12 | 0.000700 | `apps_rg/runtime/sections/role_episode_metric_registry.py` |
| `apps_rg` | 8 | 2 | 10 | 0.000700 | `apps_rg/fact_inventory/arsenal_graph_w4a_spec.py` |
| `apps_shared` | 7 | 56 | 63 | 0.000600 | `apps_shared/validators/proof/scenario_base.py` |
| `apps_lic` | 7 | 22 | 29 | 0.000600 | `apps_lic/runtime/bindings/c03_binding.py` |
| `apps_shared` | 7 | 15 | 22 | 0.000600 | `apps_shared/reasoning/orchestration/hop_pipeline.py` |
| `apps_rg` | 7 | 9 | 16 | 0.000600 | `apps_rg/runtime/sections/ey_graph_role_episode_registry.py` |
| `apps_rg` | 7 | 9 | 16 | 0.000600 | `apps_rg/runtime/sections/insurtech_graph_role_episode_registry.py` |
| `apps_lic` | 7 | 8 | 15 | 0.000600 | `apps_lic/runtime/dispatch/stage_receipts.py` |
| `apps_rg` | 7 | 4 | 11 | 0.000600 | `apps_rg/runtime/section_one_spine_certification_lane_integration.py` |
| `apps_rg` | 7 | 2 | 9 | 0.000600 | `apps_rg/runtime/sections/prompt_trace_reasoning.py` |
| `apps_shared` | 6 | 14 | 20 | 0.000500 | `apps_shared/validators/proof/validators.py` |
| `apps_lic` | 6 | 9 | 15 | 0.000500 | `apps_lic/policy/__init__.py` |
| `apps_lic` | 6 | 9 | 15 | 0.000500 | `apps_lic/validators/policy/judge_base.py` |
| `apps_rg` | 6 | 9 | 15 | 0.000500 | `apps_rg/runtime/judges/policy_backed_section_judges.py` |
| `apps_shared` | 6 | 7 | 13 | 0.000500 | `apps_shared/enforcement/core/event_bus.py` |
| `apps_rg` | 6 | 3 | 9 | 0.000500 | `apps_rg/runtime/ibm_narrative_proof_accounting.py` |
| `apps_shared` | 6 | 3 | 9 | 0.000500 | `apps_shared/data_adapters/__init__.py` |
| `apps_shared` | 5 | 88 | 93 | 0.000400 | `apps_shared/validators/enforcement/HardenedeventbusStrategy.py` |
| `apps_lic` | 5 | 9 | 14 | 0.000400 | `apps_lic/validators/policy/decision_router.py` |
| `apps_shared` | 5 | 8 | 13 | 0.000400 | `apps_shared/proof/scenarios.py` |
| `apps_shared` | 5 | 7 | 12 | 0.000400 | `apps_shared/cert/grounded_fec_producers.py` |
| `apps_rg` | 5 | 6 | 11 | 0.000400 | `apps_rg/fact_inventory/build_cro_projection_gap_analysis.py` |
| `apps_rg` | 5 | 5 | 10 | 0.000400 | `apps_rg/fact_inventory/materialize_arsenal_from_design.py` |
| `apps_rg` | 5 | 5 | 10 | 0.000400 | `apps_rg/runtime/sections/competency_capability_registry.py` |
| `apps_rg` | 5 | 4 | 9 | 0.000400 | `apps_rg/runtime/exit/competencies_x3.py` |
| `apps_shared` | 5 | 1 | 6 | 0.000400 | `apps_shared/utils/ConfigurationService.py` |

## Gaps by Priority Band (fan-in)

| Band | Fan-in range | Gap count | Action |
|---|---|---|---|
| P1_critical_fanin_ge_10 | >= 10 | 21 | Test next — central dependency |
| P2_high_fanin_5_to_9 | 5–9 | 62 | Test soon — significant blast radius |
| P3_medium_fanin_2_to_4 | 2–4 | 300 | Backlog — moderate impact |
| P4_low_fanin_1 | 1 | 672 | Optional — single consumer |
| P5_isolated_fanin_0 | 0 | 76 | Likely dead code — verify before testing |

## Gaps by Layer

| Layer | Gap count | Top gap (fanin) | Top gap module |
|---|---|---|---|
| L6_system_learning | 217 | 11 | `agentic_core.L6_system_learning.config.semantic_memory_config` |
| runtime | 186 | 15 | `agentic_core.runtime.artifacts.integrated_runtime_emitter` |
| L2_execution | 120 | 12 | `agentic_core.L2_execution.orchestration.l2_phase_pipeline` |
| L1_cognition | 106 | 17 | `agentic_core.L1_cognition.types.intent_frame_types` |
| L3_orchestration | 103 | 12 | `agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator` |
| L5_safety | 86 | 16 | `agentic_core.L5_safety.enforcement.ingress` |
| L4_state | 64 | 4 | `agentic_core.L4_state.uwg.app_domain_registration` |
| adg | 61 | 2 | `agentic_core.adg.artifact.consumer_mode` |
| knowledge | 31 | 3 | `agentic_core.knowledge.ingestion.intake_clerk` |
| L6_observability | 30 | 13 | `agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle` |
| utils | 25 | 2 | `agentic_core.utils.workflow_engines.apps_engines_aliases` |
| L0_routing | 21 | 12 | `agentic_core.L0_routing.config.pipeline_constants` |
| prompt_governance | 21 | 4 | `agentic_core.prompt_governance.apps_research_pa_binding` |
| evaluation | 11 | 4 | `agentic_core.evaluation.judges.deterministic_graders` |
| config | 10 | 2 | `agentic_core.config.token_budget_loader` |
| mixins | 7 | 1 | `agentic_core.mixins.adg_tracing_hooks` |
| L7_auditability | 4 | 4 | `agentic_core.L7_auditability.contracts.how_trace` |
| cache | 4 | 1 | `agentic_core.cache.core.graph_aware_cache` |
| runtime_gates | 4 | 4 | `agentic_core.runtime_gates.gate_bundle` |
| UWG | 3 | 2 | `agentic_core.UWG.package_driven_write_admission` |
| base_agents | 3 | 1 | `agentic_core.base_agents.L1CognitionBase` |
| embeddings | 3 | 1 | `agentic_core.embeddings.forward_pass` |
| C0_context | 2 | 2 | `agentic_core.C0_context.cross_app_research_substrate_ingest` |
| core | 2 | 1 | `agentic_core.core.frameworks.dependency_manager` |
| tracing | 2 | 4 | `agentic_core.tracing.runtime_tracing` |
| _compat | 1 | 0 | `agentic_core._compat.core.l5_safety_aliases` |
| cloud_native | 1 | 1 | `agentic_core.cloud_native.core.cloud_native_manager` |
| gateway | 1 | 1 | `agentic_core.gateway.api_gateway_integration` |
| interfaces | 1 | 1 | `agentic_core.interfaces.gateways` |
| visualization | 1 | 1 | `agentic_core.visualization.engines.trace_3d_visualizer` |

## P1 Critical Gaps (full list, fan-in >= 10)

| Fan-in | Layer | Module |
|---|---|---|
| 17 | L1_cognition | `agentic_core.L1_cognition.types.intent_frame_types` |
| 16 | L5_safety | `agentic_core.L5_safety.enforcement.ingress` |
| 15 | runtime | `agentic_core.runtime.artifacts.integrated_runtime_emitter` |
| 15 | runtime | `agentic_core.runtime.entry.app_ingress_runner` |
| 15 | runtime | `agentic_core.runtime.gates.gate_types` |
| 14 | runtime | `agentic_core.runtime.contracts.apps_rg_runtime_authority_policy` |
| 14 | runtime | `agentic_core.runtime.prove_requirements.otel_emitter` |
| 13 | L6_observability | `agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle` |
| 13 | runtime | `agentic_core.runtime.bindings.app_binding_loader` |
| 13 | runtime | `agentic_core.runtime.entrypoints.integrated_safe_reuse_run` |
| 13 | runtime | `agentic_core.runtime.prove_requirements.otel_contract` |
| 12 | L0_routing | `agentic_core.L0_routing.config.pipeline_constants` |
| 12 | L2_execution | `agentic_core.L2_execution.orchestration.l2_phase_pipeline` |
| 12 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator` |
| 12 | runtime | `agentic_core.runtime.bindings.app_binding_validation` |
| 11 | L6_system_learning | `agentic_core.L6_system_learning.config.semantic_memory_config` |
| 11 | L6_system_learning | `agentic_core.L6_system_learning.types.semantic_memory_types` |
| 11 | runtime | `agentic_core.runtime.prove_requirements.matrix_loader` |
| 10 | L1_cognition | `agentic_core.L1_cognition.reasoning.intent_parser` |
| 10 | L2_execution | `agentic_core.L2_execution.healers.vllm_health_probe` |
| 10 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.rubric` |

**P1 total: 21**

## P2 High Gaps (full list, fan-in 5-9)

| Fan-in | Layer | Module |
|---|---|---|
| 9 | L0_routing | `agentic_core.L0_routing.c0_retrieval.hydration` |
| 9 | runtime | `agentic_core.runtime.bindings.native_contract_chain` |
| 8 | L2_execution | `agentic_core.L2_execution.regen.prefix_digest` |
| 8 | L2_execution | `agentic_core.L2_execution.regen.prompt_lock` |
| 8 | L2_execution | `agentic_core.L2_execution.regen.regen_types` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_control.exit_controller` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.bus` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.disposition` |
| 8 | L5_safety | `agentic_core.L5_safety.identity.registries` |
| 8 | runtime | `agentic_core.runtime.c0.evidence_metrics_extractor` |
| 8 | runtime | `agentic_core.runtime.entry.apps_rg_dispatch` |
| 7 | L0_routing | `agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry` |
| 7 | L0_routing | `agentic_core.L0_routing.package_driven_l0_binding` |
| 7 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.composition` |
| 7 | L6_system_learning | `agentic_core.L6_system_learning.stores.version_store` |
| 6 | L1_cognition | `agentic_core.L1_cognition.enforcement.reasoning_chokepoint` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.graders.adversarial` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.graders.code_based` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges._base_http_judge` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.guardrail_adapter` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.pre_l5_sweep` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.runtime_rails` |
| 6 | L6_observability | `agentic_core.L6_observability.shadow_eval.gauntlet` |
| 6 | L6_observability | `agentic_core.L6_observability.shadow_eval.ingest` |
| 6 | L6_system_learning | `agentic_core.L6_system_learning.types.prompt_artifact_types` |
| 6 | L6_system_learning | `agentic_core.L6_system_learning.types.trace_feature_types` |
| 6 | runtime | `agentic_core.runtime.contracts.apps_lic_ingress_payload` |
| 6 | runtime | `agentic_core.runtime.contracts.ensemble_types` |
| 6 | runtime | `agentic_core.runtime.entrypoints.integrated_single_action_run` |
| 6 | runtime | `agentic_core.runtime.exhaust.runtime_exhaust_bundle` |
| 6 | runtime | `agentic_core.runtime.exit.exit_package_driven_binding` |
| 6 | runtime | `agentic_core.runtime.exit.exit_review_normalizer` |
| 6 | runtime | `agentic_core.runtime.prove_requirements.tier2_step1_metadata` |
| 6 | runtime | `agentic_core.runtime.reasoning.reasoning_control_requirement` |
| 5 | L0_routing | `agentic_core.L0_routing.intake.handoff` |
| 5 | L1_cognition | `agentic_core.L1_cognition.bridges.u0_to_l1_plan` |
| 5 | L1_cognition | `agentic_core.L1_cognition.enforcement.first_safety_reading` |
| 5 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_plan` |
| 5 | L2_execution | `agentic_core.L2_execution.regen.same_authority_bundle` |
| 5 | L2_execution | `agentic_core.L2_execution.regen.same_authority_thread` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_control.ledger_integrity` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.break_glass` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.factory` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.otel_sdk_sink` |
| 5 | L5_safety | `agentic_core.L5_safety.identity.audit_binding_lane` |
| 5 | L5_safety | `agentic_core.L5_safety.identity.egress_adapter_gated` |
| 5 | L6_observability | `agentic_core.L6_observability.shadow_eval.evaluation` |
| 5 | L6_observability | `agentic_core.L6_observability.shadow_eval.proposal` |
| 5 | L6_observability | `agentic_core.L6_observability.shadow_eval.span_export` |
| 5 | L6_system_learning | `agentic_core.L6_system_learning.constraints.dampening` |
| 5 | L6_system_learning | `agentic_core.L6_system_learning.future_run_promotion.completed_run_evaluator` |
| 5 | L6_system_learning | `agentic_core.L6_system_learning.types.optimization_types` |
| 5 | runtime | `agentic_core.runtime.entry.u0_apps_research_binding` |
| 5 | runtime | `agentic_core.runtime.exit.x2_aggregation_result` |
| 5 | runtime | `agentic_core.runtime.exit.x2_aggregator` |
| 5 | runtime | `agentic_core.runtime.exit.x3_emitter` |
| 5 | runtime | `agentic_core.runtime.gates.gate_evaluators` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.acceptance_validator` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.otel_harness` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.r1b_subclaim_schema` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.tier3_step1_metadata` |
| 5 | runtime | `agentic_core.runtime.reasoning.reasoning_execution_receipt` |

**P2 total: 62**

## P3 Medium Gaps (top 100 of band, fan-in 2-4)

| Fan-in | Layer | Module |
|---|---|---|
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.contracts_l0_1` |
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.replay` |
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.selector` |
| 4 | L0_routing | `agentic_core.L0_routing.intake.correlation` |
| 4 | L1_cognition | `agentic_core.L1_cognition.enforcement.consensus_validator` |
| 4 | L1_cognition | `agentic_core.L1_cognition.planning.plan_validation` |
| 4 | L1_cognition | `agentic_core.L1_cognition.planning.planning_priors` |
| 4 | L1_cognition | `agentic_core.L1_cognition.planning.reasoning_loop` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.knowledge_orchestrator` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.l1_v5_contract_builder` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.meta_client` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_knowledge` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.search_fusion_engine` |
| 4 | L2_execution | `agentic_core.L2_execution.bounded_executor` |
| 4 | L2_execution | `agentic_core.L2_execution.enforcement.anti_bypass_guards` |
| 4 | L2_execution | `agentic_core.L2_execution.observability.l2_resolution_spans` |
| 4 | L2_execution | `agentic_core.L2_execution.regen.incremental_repair_contract` |
| 4 | L2_execution | `agentic_core.L2_execution.types.agent_taxonomy_spine_axes` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.state` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.consistency_redis` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.anthropic_judge` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.openai_judge` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.prompt_templates` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.registry.static_dag_proof` |
| 4 | L4_state | `agentic_core.L4_state.uwg.app_domain_registration` |
| 4 | L5_safety | `agentic_core.L5_safety.contracts._vocab` |
| 4 | L5_safety | `agentic_core.L5_safety.eval_spine.kill_switch` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.data_authority_loader` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.front_door_resolver` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.registry_loader` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.write_adapter` |
| 4 | L6_observability | `agentic_core.L6_observability.runtime_trace.synthetic_trace_detector` |
| 4 | L6_observability | `agentic_core.L6_observability.shadow_eval.rca` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.engines.change_package_impl` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.engines.l4_state_writer` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.future_run_promotion.future_run_proposal_builder` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.future_run_promotion.package_driven_l6_binding` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.future_run_promotion.rca_synthesizer` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.types.evaluation_spine_types` |
| 4 | L6_system_learning | `agentic_core.L6_system_learning.types.prompt_adg_relations` |
| 4 | L7_auditability | `agentic_core.L7_auditability.contracts.how_trace` |
| 4 | evaluation | `agentic_core.evaluation.judges.deterministic_graders` |
| 4 | evaluation | `agentic_core.evaluation.judges.gate_evidence_mapper` |
| 4 | prompt_governance | `agentic_core.prompt_governance.apps_research_pa_binding` |
| 4 | runtime | `agentic_core.runtime.artifacts.spine_proof_bundle` |
| 4 | runtime | `agentic_core.runtime.bindings.exit_binding_validator` |
| 4 | runtime | `agentic_core.runtime.bindings.profile_validators` |
| 4 | runtime | `agentic_core.runtime.contracts.apps_research_runtime_package` |
| 4 | runtime | `agentic_core.runtime.contracts.l3_bypass_receipt` |
| 4 | runtime | `agentic_core.runtime.entrypoints.integrated_grounded_read_run` |
| 4 | runtime | `agentic_core.runtime.exit.apps_research_exit_binding` |
| 4 | runtime | `agentic_core.runtime.judges.panel.canonical_contract` |
| 4 | runtime | `agentic_core.runtime.judges.panel.transport_parity` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.artifact_payload_hasher` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.constants` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.implementation_mapper` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.proof_depth_ladder` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.tier0_step1_metadata` |
| 4 | runtime_gates | `agentic_core.runtime_gates.gate_bundle` |
| 4 | tracing | `agentic_core.tracing.runtime_tracing` |
| 3 | L0_routing | `agentic_core.L0_routing.apps_research_l0_binding` |
| 3 | L0_routing | `agentic_core.L0_routing.doctrine.contracts_l0_2` |
| 3 | L0_routing | `agentic_core.L0_routing.reasoning.v15_to_c0_adapter` |
| 3 | L1_cognition | `agentic_core.L1_cognition.apps_research_l1_binding` |
| 3 | L1_cognition | `agentic_core.L1_cognition.planning.draft_plan` |
| 3 | L1_cognition | `agentic_core.L1_cognition.planning.plan_contract_handoff` |
| 3 | L1_cognition | `agentic_core.L1_cognition.reasoning.constitutional_rules_engine` |
| 3 | L1_cognition | `agentic_core.L1_cognition.reasoning.plan_self_repair` |
| 3 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_evaluation` |
| 3 | L1_cognition | `agentic_core.L1_cognition.types.action_request_types` |
| 3 | L1_cognition | `agentic_core.L1_cognition.types.client_types` |
| 3 | L2_execution | `agentic_core.L2_execution.candidate_gate_runner` |
| 3 | L2_execution | `agentic_core.L2_execution.enforcement.egress_proxy` |
| 3 | L2_execution | `agentic_core.L2_execution.enforcement.kill_switch` |
| 3 | L2_execution | `agentic_core.L2_execution.ensemble_lane` |
| 3 | L2_execution | `agentic_core.L2_execution.healers.qwen_strict_diagnostic` |
| 3 | L2_execution | `agentic_core.L2_execution.judge_jury_runner` |
| 3 | L2_execution | `agentic_core.L2_execution.l2_package_driven_executor` |
| 3 | L2_execution | `agentic_core.L2_execution.orchestration.resolution_consistency_gate` |
| 3 | L2_execution | `agentic_core.L2_execution.regen.same_authority_errors` |
| 3 | L2_execution | `agentic_core.L2_execution.regen.same_authority_regen_receipt` |
| 3 | L2_execution | `agentic_core.L2_execution.types.agent_taxonomy_w1_merge` |
| 3 | L2_execution | `agentic_core.L2_execution.types.ptc_execution_profile` |
| 3 | L2_execution | `agentic_core.L2_execution.utils.safe_subprocess` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.eligibility` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.governance` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.consistency_sqlite` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.http_judge` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.hitl` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.x1d_deterministic_evaluator` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.inference.qwen_vllm.config.qwen_telemetry` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.managed_workflow_router` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.section_merge_engine` |
| 3 | L4_state | `agentic_core.L4_state.enforcement.blast_radius` |
| 3 | L4_state | `agentic_core.L4_state.enforcement.uwg_committer` |
| 3 | L4_state | `agentic_core.L4_state.fact_writeback.engine` |
| 3 | L4_state | `agentic_core.L4_state.types.no_durable_mutation_receipt` |
| 3 | L4_state | `agentic_core.L4_state.uwg.app_domain_loader` |
| 3 | L5_safety | `agentic_core.L5_safety.adapters.email_magic_link_adapter` |
| 3 | L5_safety | `agentic_core.L5_safety.certification.l5_parent_vocab` |

**P3 total: 300 (showing top 100)**

## Notes

- Coverage measured by basename match: `tests/**/test_<leaf>.py`.
- Some matches may be name-collisions across layers (e.g. two modules named `types.py`).
- P5 (fanin=0) modules likely indicate dead code or test-only modules — verify before adding tests.
- For risk × pytest coverage bands use `artifacts/test_inventory/hotspot_coverage_priority.md`.
- Renderer: `tools/analysis/test_hotspot_gaps_report.py`.
