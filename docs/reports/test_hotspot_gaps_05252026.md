# Test Hotspot Gap Report

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite
Generated: 2026-05-25T04:07:57+00:00
Commit SHA: `ee3001638c8894973b45414ba0071c02485a5f3b`

## Summary

- **Total agentic_core modules (excl. __init__):** 2372
- **Modules with matching test_<name>.py:** 1370 (57%)
- **Remaining gaps:** 1002

> **W2 note:** P3 modules may have behavioral coverage in
> `tests/agentic_core/test_p3_w2_hotspot_behavior.py` without a basename match.
> See `artifacts/test_inventory/w2_basename_collision_audit.md`.

## Gaps by Priority Band (fan-in)

| Band | Fan-in range | Gap count | Action |
|---|---|---|---|
| P1_critical_fanin_ge_10 | >= 10 | 52 | Test next — central dependency |
| P2_high_fanin_5_to_9 | 5–9 | 100 | Test soon — significant blast radius |
| P3_medium_fanin_2_to_4 | 2–4 | 243 | Backlog — moderate impact |
| P4_low_fanin_1 | 1 | 541 | Optional — single consumer |
| P5_isolated_fanin_0 | 0 | 66 | Likely dead code — verify before testing |

## Gaps by Layer

| Layer | Gap count | Top gap (fanin) | Top gap module |
|---|---|---|---|
| runtime | 221 | 79 | `agentic_core.runtime.contracts.apps_rg_ingress_payload` |
| L2_execution | 115 | 14 | `agentic_core.L2_execution.healers.vllm_health_probe` |
| L3_orchestration | 112 | 40 | `agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry` |
| L1_cognition | 110 | 16 | `agentic_core.L1_cognition.types.intent_frame_types` |
| L5_safety | 99 | 16 | `agentic_core.L5_safety.enforcement.ingress` |
| L4_state | 72 | 32 | `agentic_core.L4_state.contracts.records` |
| adg | 62 | 2 | `agentic_core.adg.artifact.consumer_mode` |
| L0_routing | 34 | 22 | `agentic_core.L0_routing.intake.envelope` |
| L6_observability | 34 | 13 | `agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle` |
| knowledge | 31 | 3 | `agentic_core.knowledge.ingestion.intake_clerk` |
| utils | 25 | 2 | `agentic_core.utils.workflow_engines.apps_engines_aliases` |
| prompt_governance | 22 | 5 | `agentic_core.prompt_governance.pa_package_driven_binding` |
| evaluation | 11 | 4 | `agentic_core.evaluation.judges.deterministic_graders` |
| config | 10 | 2 | `agentic_core.config.token_budget_loader` |
| mixins | 7 | 1 | `agentic_core.mixins.adg_tracing_hooks` |
| runtime_gates | 5 | 6 | `agentic_core.runtime_gates.definitions` |
| L6_learning | 4 | 4 | `agentic_core.L6_learning.completed_run_evaluator` |
| L7_auditability | 4 | 4 | `agentic_core.L7_auditability.contracts.how_trace` |
| cache | 4 | 1 | `agentic_core.cache.core.graph_aware_cache` |
| embeddings | 4 | 4 | `agentic_core.embeddings.exceptions` |
| UWG | 3 | 2 | `agentic_core.UWG.package_driven_write_admission` |
| base_agents | 3 | 1 | `agentic_core.base_agents.L1CognitionBase` |
| C0_context | 2 | 2 | `agentic_core.C0_context.cross_app_research_substrate_ingest` |
| core | 2 | 1 | `agentic_core.core.frameworks.dependency_manager` |
| _compat | 1 | 0 | `agentic_core._compat.core.l5_safety_aliases` |
| cloud_native | 1 | 1 | `agentic_core.cloud_native.core.cloud_native_manager` |
| gateway | 1 | 1 | `agentic_core.gateway.api_gateway_integration` |
| interfaces | 1 | 1 | `agentic_core.interfaces.gateways` |
| tracing | 1 | 1 | `agentic_core.tracing.engines.distributed_tracing_coordinator` |
| visualization | 1 | 1 | `agentic_core.visualization.engines.trace_3d_visualizer` |

## P1 Critical Gaps (full list, fan-in >= 10)

| Fan-in | Layer | Module |
|---|---|---|
| 79 | runtime | `agentic_core.runtime.contracts.apps_rg_ingress_payload` |
| 74 | runtime | `agentic_core.runtime.contracts.final_evidence_contract` |
| 40 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry` |
| 40 | runtime | `agentic_core.runtime.contracts.l1_plan_contract` |
| 32 | L4_state | `agentic_core.L4_state.contracts.records` |
| 30 | runtime | `agentic_core.runtime.contracts.compiled_prompt_artifact` |
| 27 | L4_state | `agentic_core.L4_state.uwg.durable_write_gateway` |
| 23 | runtime | `agentic_core.runtime.contracts.x3_disposition` |
| 22 | L0_routing | `agentic_core.L0_routing.intake.envelope` |
| 21 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.dimension` |
| 20 | L0_routing | `agentic_core.L0_routing.intake.validated_request` |
| 20 | runtime | `agentic_core.runtime.contracts.posture` |
| 19 | L0_routing | `agentic_core.L0_routing.intake.reason_codes` |
| 19 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.x2_matrix` |
| 17 | runtime | `agentic_core.runtime.entry.app_ingress_runner` |
| 16 | L1_cognition | `agentic_core.L1_cognition.types.intent_frame_types` |
| 16 | L5_safety | `agentic_core.L5_safety.enforcement.ingress` |
| 16 | runtime | `agentic_core.runtime.contracts.origin` |
| 16 | runtime | `agentic_core.runtime.contracts.sealed_workflow_types` |
| 15 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.consistency` |
| 15 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions` |
| 15 | L4_state | `agentic_core.L4_state.contracts.app_domain` |
| 15 | L5_safety | `agentic_core.L5_safety.contracts.verify` |
| 15 | runtime | `agentic_core.runtime.artifacts.integrated_runtime_emitter` |
| 15 | runtime | `agentic_core.runtime.contracts.x1_checkout_result` |
| 15 | runtime | `agentic_core.runtime.entrypoints.integrated_single_action_spine_run` |
| 15 | runtime | `agentic_core.runtime.exit.exit_disposition` |
| 15 | runtime | `agentic_core.runtime.gates.gate_types` |
| 14 | L0_routing | `agentic_core.L0_routing.c0_retrieval.final_contract` |
| 14 | L2_execution | `agentic_core.L2_execution.healers.vllm_health_probe` |
| 14 | L5_safety | `agentic_core.L5_safety.identity.guardrail_bank` |
| 14 | runtime | `agentic_core.runtime.prove_requirements.otel_emitter` |
| 13 | L0_routing | `agentic_core.L0_routing.c0_retrieval.candidate_pool` |
| 13 | L0_routing | `agentic_core.L0_routing.intake.stages` |
| 13 | L4_state | `agentic_core.L4_state.otel.spans` |
| 13 | L6_observability | `agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle` |
| 13 | runtime | `agentic_core.runtime.bindings.app_binding_loader` |
| 13 | runtime | `agentic_core.runtime.contracts.apps_rg_runtime_authority_policy` |
| 13 | runtime | `agentic_core.runtime.entrypoints.integrated_safe_reuse_run` |
| 13 | runtime | `agentic_core.runtime.prove_requirements.otel_contract` |
| 12 | L0_routing | `agentic_core.L0_routing.config.pipeline_constants` |
| 12 | L2_execution | `agentic_core.L2_execution.orchestration.l2_phase_pipeline` |
| 12 | L5_safety | `agentic_core.L5_safety.identity.principal_verifier` |
| 12 | runtime | `agentic_core.runtime.bindings.app_binding_validation` |
| 11 | L0_routing | `agentic_core.L0_routing.types.route_contract_v15` |
| 11 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator` |
| 11 | L4_state | `agentic_core.L4_state.contracts.digests` |
| 11 | runtime | `agentic_core.runtime.prove_requirements.matrix_loader` |
| 10 | L0_routing | `agentic_core.L0_routing.c0_retrieval.hydration` |
| 10 | L1_cognition | `agentic_core.L1_cognition.reasoning.intent_parser` |
| 10 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.rubric` |
| 10 | L4_state | `agentic_core.L4_state.uwg.touch_state_writer` |

**P1 total: 52**

## P2 High Gaps (full list, fan-in 5-9)

| Fan-in | Layer | Module |
|---|---|---|
| 9 | L0_routing | `agentic_core.L0_routing.u0_intake_validator` |
| 9 | L1_cognition | `agentic_core.L1_cognition.package_driven_l1_binding` |
| 9 | L1_cognition | `agentic_core.L1_cognition.planning.digests` |
| 9 | L2_execution | `agentic_core.L2_execution.observability.l2_spans` |
| 9 | L6_observability | `agentic_core.L6_observability.shadow_eval._digest` |
| 9 | runtime | `agentic_core.runtime.contracts.judge_types` |
| 9 | runtime | `agentic_core.runtime.contracts.l3_to_l2_step_contract` |
| 9 | runtime | `agentic_core.runtime.gates.gate_profile_resolver` |
| 9 | runtime | `agentic_core.runtime.prove_requirements.replay_engine` |
| 9 | runtime | `agentic_core.runtime.providers.provider_types` |
| 8 | L0_routing | `agentic_core.L0_routing.intake.receipts` |
| 8 | L1_cognition | `agentic_core.L1_cognition.reasoning.plan_bundle_loader` |
| 8 | L1_cognition | `agentic_core.L1_cognition.types.plan_bundle_types` |
| 8 | L2_execution | `agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent` |
| 8 | L2_execution | `agentic_core.L2_execution.types.heal_contract_types` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_control.exit_controller` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.bus` |
| 8 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.disposition` |
| 8 | L5_safety | `agentic_core.L5_safety.identity.registries` |
| 8 | runtime | `agentic_core.runtime.bindings.native_contract_chain` |
| 8 | runtime | `agentic_core.runtime.entry.apps_rg_dispatch` |
| 8 | runtime | `agentic_core.runtime.judges.panel.panel_types` |
| 8 | runtime | `agentic_core.runtime.reasoning.reasoning_control_resolver` |
| 7 | L0_routing | `agentic_core.L0_routing.intake.origin_labels` |
| 7 | L0_routing | `agentic_core.L0_routing.package_driven_l0_binding` |
| 7 | L2_execution | `agentic_core.L2_execution.types.capability_token_types` |
| 7 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.contracts_l3_7` |
| 7 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.composition` |
| 7 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter` |
| 7 | L4_state | `agentic_core.L4_state.contracts.app_domain_lookup` |
| 7 | L4_state | `agentic_core.L4_state.refresh.refresh_coordinator` |
| 7 | L5_safety | `agentic_core.L5_safety.contracts.l5_certification_contracts` |
| 7 | runtime | `agentic_core.runtime.c0.c0_package_driven_grounding` |
| 7 | runtime | `agentic_core.runtime.contracts.c0_bypass_receipt` |
| 7 | runtime | `agentic_core.runtime.contracts.l3_runtime_orchestration_receipt` |
| 7 | runtime | `agentic_core.runtime.judges.panel.adapter_protocol` |
| 7 | runtime | `agentic_core.runtime.l2_recipe_resolver` |
| 7 | runtime | `agentic_core.runtime.prove_requirements.tier_fixture_bootstrap` |
| 7 | runtime | `agentic_core.runtime.reasoning.reasoning_control_requirement` |
| 6 | L0_routing | `agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter` |
| 6 | L0_routing | `agentic_core.L0_routing.doctrine.terminal_routes` |
| 6 | L1_cognition | `agentic_core.L1_cognition.enforcement.reasoning_chokepoint` |
| 6 | L2_execution | `agentic_core.L2_execution.healers.healing_cascade_registry` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.contracts_l3_6` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.graders.adversarial` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.graders.code_based` |
| 6 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges._base_http_judge` |
| 6 | L4_state | `agentic_core.L4_state.adapters.sqlite3_adapter` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.guardrail_adapter` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.pre_l5_sweep` |
| 6 | L5_safety | `agentic_core.L5_safety.identity.runtime_rails` |
| 6 | L5_safety | `agentic_core.L5_safety.policy.apps_lic_reengagement` |
| 6 | L6_observability | `agentic_core.L6_observability.shadow_eval.gauntlet` |
| 6 | L6_observability | `agentic_core.L6_observability.shadow_eval.observer` |
| 6 | runtime | `agentic_core.runtime.c0.evidence_metrics_extractor` |
| 6 | runtime | `agentic_core.runtime.contracts.apps_lic_ingress_payload` |
| 6 | runtime | `agentic_core.runtime.contracts.ensemble_types` |
| 6 | runtime | `agentic_core.runtime.contracts.otel_lifecycle_bridge` |
| 6 | runtime | `agentic_core.runtime.contracts.runtime_customization_package` |
| 6 | runtime | `agentic_core.runtime.entrypoints.integrated_single_action_run` |
| 6 | runtime | `agentic_core.runtime.exit.exit_package_driven_binding` |
| 6 | runtime | `agentic_core.runtime.exit.exit_review_normalizer` |
| 6 | runtime | `agentic_core.runtime.exit.x1_checkout_runner` |
| 6 | runtime | `agentic_core.runtime.prove_requirements.tier2_step1_metadata` |
| 6 | runtime | `agentic_core.runtime.reasoning.transport_capabilities` |
| 6 | runtime_gates | `agentic_core.runtime_gates.definitions` |
| 5 | L0_routing | `agentic_core.L0_routing.app_domain_resolver` |
| 5 | L0_routing | `agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry` |
| 5 | L0_routing | `agentic_core.L0_routing.intake.handoff` |
| 5 | L1_cognition | `agentic_core.L1_cognition.enforcement.first_safety_reading` |
| 5 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_plan` |
| 5 | L2_execution | `agentic_core.L2_execution.entry.packet_normalizer` |
| 5 | L2_execution | `agentic_core.L2_execution.types.l2_execution_request` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_control.ledger_integrity` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.break_glass` |
| 5 | L3_orchestration | `agentic_core.L3_orchestration.managed_workflow_runner` |
| 5 | L5_safety | `agentic_core.L5_safety.exceptions` |
| 5 | L5_safety | `agentic_core.L5_safety.identity.audit_binding_lane` |
| 5 | L5_safety | `agentic_core.L5_safety.identity.egress_adapter_gated` |
| 5 | L5_safety | `agentic_core.L5_safety.runtime_gates.digest` |
| 5 | L5_safety | `agentic_core.L5_safety.runtime_gates.mesh_result` |
| 5 | L6_observability | `agentic_core.L6_observability.shadow_eval.proposal` |
| 5 | prompt_governance | `agentic_core.prompt_governance.pa_package_driven_binding` |
| 5 | runtime | `agentic_core.runtime.bindings.binding_validation_types` |
| 5 | runtime | `agentic_core.runtime.contracts.future_run_promotion` |
| 5 | runtime | `agentic_core.runtime.contracts.identity` |
| 5 | runtime | `agentic_core.runtime.contracts.prompt_assembly_bypass_receipt` |
| 5 | runtime | `agentic_core.runtime.contracts.runtime_gate_verdict_bundle` |
| 5 | runtime | `agentic_core.runtime.entry.u0_apps_research_binding` |
| 5 | runtime | `agentic_core.runtime.entry.u0_runtime_package_binding` |
| 5 | runtime | `agentic_core.runtime.exhaust.runtime_exhaust_bundle` |
| 5 | runtime | `agentic_core.runtime.exit.x2_aggregator` |
| 5 | runtime | `agentic_core.runtime.exit.x3_emitter` |
| 5 | runtime | `agentic_core.runtime.gates.gate_evaluators` |
| 5 | runtime | `agentic_core.runtime.judges.panel.canonical_contract` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.acceptance_validator` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.otel_harness` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.r1b_subclaim_schema` |
| 5 | runtime | `agentic_core.runtime.prove_requirements.tier3_step1_metadata` |
| 5 | runtime | `agentic_core.runtime.reasoning.reasoning_execution_receipt` |

**P2 total: 100**

## P3 Medium Gaps (top 100 of band, fan-in 2-4)

| Fan-in | Layer | Module |
|---|---|---|
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.contracts_l0_1` |
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.replay` |
| 4 | L0_routing | `agentic_core.L0_routing.doctrine.selector` |
| 4 | L0_routing | `agentic_core.L0_routing.intake.correlation` |
| 4 | L1_cognition | `agentic_core.L1_cognition.bridges.u0_to_l1_plan` |
| 4 | L1_cognition | `agentic_core.L1_cognition.enforcement.consensus_validator` |
| 4 | L1_cognition | `agentic_core.L1_cognition.planning.planning_priors` |
| 4 | L1_cognition | `agentic_core.L1_cognition.planning.reasoning_loop` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.knowledge_orchestrator` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.l1_v5_contract_builder` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.meta_client` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_knowledge` |
| 4 | L1_cognition | `agentic_core.L1_cognition.reasoning.search_fusion_engine` |
| 4 | L2_execution | `agentic_core.L2_execution.bounded_executor` |
| 4 | L2_execution | `agentic_core.L2_execution.enforcement.anti_bypass_guards` |
| 4 | L2_execution | `agentic_core.L2_execution.l2_package_driven_executor` |
| 4 | L2_execution | `agentic_core.L2_execution.observability.l2_resolution_spans` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.state` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.consistency_redis` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.factory` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.anthropic_judge` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.openai_judge` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.prompt_templates` |
| 4 | L3_orchestration | `agentic_core.L3_orchestration.registry.static_dag_proof` |
| 4 | L4_state | `agentic_core.L4_state.uwg.app_domain_registration` |
| 4 | L5_safety | `agentic_core.L5_safety.eval_spine.kill_switch` |
| 4 | L5_safety | `agentic_core.L5_safety.evaluators.apps_lic_reengagement` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.data_authority_loader` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.front_door_resolver` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.registry_loader` |
| 4 | L5_safety | `agentic_core.L5_safety.identity.write_adapter` |
| 4 | L6_learning | `agentic_core.L6_learning.completed_run_evaluator` |
| 4 | L6_learning | `agentic_core.L6_learning.package_driven_l6_binding` |
| 4 | L6_observability | `agentic_core.L6_observability.runtime_trace.synthetic_trace_detector` |
| 4 | L6_observability | `agentic_core.L6_observability.shadow_eval.evaluation` |
| 4 | L6_observability | `agentic_core.L6_observability.shadow_eval.ingest` |
| 4 | L6_observability | `agentic_core.L6_observability.shadow_eval.rca` |
| 4 | L7_auditability | `agentic_core.L7_auditability.contracts.how_trace` |
| 4 | embeddings | `agentic_core.embeddings.exceptions` |
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
| 4 | runtime | `agentic_core.runtime.exit.x2_aggregation_result` |
| 4 | runtime | `agentic_core.runtime.judges.panel.transport_parity` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.artifact_payload_hasher` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.implementation_mapper` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.proof_depth_ladder` |
| 4 | runtime | `agentic_core.runtime.prove_requirements.tier0_step1_metadata` |
| 4 | runtime | `agentic_core.runtime.providers.provider_gateway` |
| 4 | runtime_gates | `agentic_core.runtime_gates.gate_bundle` |
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
| 3 | L2_execution | `agentic_core.L2_execution.orchestration.resolution_consistency_gate` |
| 3 | L2_execution | `agentic_core.L2_execution.types.ptc_execution_profile` |
| 3 | L2_execution | `agentic_core.L2_execution.utils.safe_subprocess` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.eligibility` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.doctrine.governance` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.consistency_sqlite` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.judges.http_judge` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.otel_sdk_sink` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.hitl` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.exit_eval.v6.x1d_deterministic_evaluator` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.inference.qwen_vllm.config.qwen_telemetry` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.managed_workflow_router` |
| 3 | L3_orchestration | `agentic_core.L3_orchestration.section_merge_engine` |
| 3 | L4_state | `agentic_core.L4_state.enforcement.blast_radius` |
| 3 | L4_state | `agentic_core.L4_state.enforcement.uwg_committer` |
| 3 | L4_state | `agentic_core.L4_state.types.no_durable_mutation_receipt` |
| 3 | L4_state | `agentic_core.L4_state.uwg.app_domain_loader` |
| 3 | L5_safety | `agentic_core.L5_safety.adapters.email_magic_link_adapter` |
| 3 | L5_safety | `agentic_core.L5_safety.certification.l5_parent_vocab` |
| 3 | L5_safety | `agentic_core.L5_safety.contracts._vocab` |
| 3 | L5_safety | `agentic_core.L5_safety.identity.action_pipeline` |
| 3 | L5_safety | `agentic_core.L5_safety.identity.write_adapter_gated` |
| 3 | L5_safety | `agentic_core.L5_safety.runtime_gates.g29_learning_firewall` |
| 3 | L5_safety | `agentic_core.L5_safety.v5.replay_audit` |
| 3 | L5_safety | `agentic_core.L5_safety.validators.anti_overfit_detector_validator` |
| 3 | L6_learning | `agentic_core.L6_learning.future_run_proposal_builder` |

**P3 total: 243 (showing top 100)**

## Notes

- Coverage measured by basename match: `tests/**/test_<leaf>.py`.
- Some matches may be name-collisions across layers (e.g. two modules named `types.py`).
- P5 (fanin=0) modules likely indicate dead code or test-only modules — verify before adding tests.
- For risk × pytest coverage bands use `artifacts/test_inventory/hotspot_coverage_priority.md`.
- Renderer: `tools/analysis/test_hotspot_gaps_report.py`.
