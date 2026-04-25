# Test Hotspot Gap Report

ADG Provenance: backend=sqlite, snapshot=adg_indexed_04252026_0843.sqlite

## Summary

- **Total agentic_core modules (excl. __init__):** 966
- **Modules with matching test_<name>.py:** 719 (74%)
- **Remaining gaps:** 247

## Gaps by Priority Band (fan-in)

| Band | Fan-in range | Gap count | Action |
|---|---|---|---|
| P1_critical_fanin_ge_10 | >= 10 | 0 | Test next — central dependency |
| P2_high_fanin_5_to_9 | 5–9 | 0 | Test soon — significant blast radius |
| P3_medium_fanin_2_to_4 | 2–4 | 17 | Backlog — moderate impact |
| P4_low_fanin_1 | 1 | 230 | Optional — single consumer |
| P5_isolated_fanin_0 | 0 | 0 | Likely dead code — verify before testing |

## Gaps by Layer

| Layer | Gap count | Top gap (fanin) | Top gap module |
|---|---|---|---|
| (root) | 1 | 1 | `agentic_core_shim` |
| L0_routing | 5 | 2 | `agentic_core.L0_routing.types.boundary_types` |
| L1_cognition | 23 | 2 | `agentic_core.L1_cognition.types.reasoning_pattern` |
| L2_execution | 60 | 2 | `agentic_core.L2_execution.types.tool_enforcement_types` |
| L3_orchestration | 9 | 1 | `agentic_core.L3_orchestration.utils.subatomic_hop_util` |
| L4_state | 7 | 1 | `agentic_core.L4_state.utils.memory.graph_knowledge_store` |
| L5_safety | 9 | 1 | `agentic_core.L5_safety.validators.test_skip_detector_validator` |
| L6_observability | 16 | 1 | `agentic_core.L6_observability.utils.visualization.workflow_visualization` |
| adg | 38 | 1 | `agentic_core.adg.runtime.safety_observer` |
| agents | 1 | 1 | `agentic_core.agents.types.adg_backed_registry` |
| base_agents | 3 | 1 | `agentic_core.base_agents.L6ObservabilityBase` |
| cache | 1 | 1 | `agentic_core.cache.redis_coordination_fabric` |
| case_memory | 2 | 1 | `agentic_core.case_memory.core.graph_neighborhood_memory` |
| config | 3 | 1 | `agentic_core.config.redis_config` |
| embeddings | 1 | 1 | `agentic_core.embeddings.tokenization_adapter` |
| evaluation | 9 | 1 | `agentic_core.evaluation.metrics.f1_score` |
| interfaces | 6 | 1 | `agentic_core.interfaces.state_agents` |
| knowledge | 10 | 1 | `agentic_core.knowledge.static_index.skill_taxonomy_types` |
| mixins | 24 | 1 | `agentic_core.mixins.tool_reliability_mixin` |
| prompt_governance | 4 | 1 | `agentic_core.prompt_governance.validation.apply_patch_validator` |
| runtime | 7 | 1 | `agentic_core.runtime.types.state_types` |
| seams | 3 | 1 | `agentic_core.seams.workflow_learning_bridge` |
| utils | 5 | 1 | `agentic_core.utils.workflow_engines.shadow_eval_runner` |

## P1 Critical Gaps (full list, fan-in >= 10)

| Fan-in | Layer | Module |
|---|---|---|

**P1 total: 0**

## P2 High Gaps (full list, fan-in 5-9)

| Fan-in | Layer | Module |
|---|---|---|

**P2 total: 0**

## P3 Medium Gaps (top 100 of band, fan-in 2-4)

| Fan-in | Layer | Module |
|---|---|---|
| 2 | L2_execution | `agentic_core.L2_execution.types.tool_enforcement_types` |
| 2 | L2_execution | `agentic_core.L2_execution.types.ml_write_intent_types` |
| 2 | L2_execution | `agentic_core.L2_execution.reasoning.authority_validator` |
| 2 | L2_execution | `agentic_core.L2_execution.reasoning.adaptation_orchestrator` |
| 2 | L2_execution | `agentic_core.L2_execution.reasoning.action_node` |
| 2 | L2_execution | `agentic_core.L2_execution.reasoning.StructuredEngineAgent` |
| 2 | L2_execution | `agentic_core.L2_execution.reasoning.RedisSovereignAgent` |
| 2 | L2_execution | `agentic_core.L2_execution.healers.artifact_loader` |
| 2 | L2_execution | `agentic_core.L2_execution.enforcement.write_governor_mixin` |
| 2 | L2_execution | `agentic_core.L2_execution.enforcement._token_counter` |
| 2 | L2_execution | `agentic_core.L2_execution.enforcement._provider_local_vllm` |
| 2 | L1_cognition | `agentic_core.L1_cognition.types.reasoning_pattern` |
| 2 | L1_cognition | `agentic_core.L1_cognition.reasoning.reasoning_context` |
| 2 | L1_cognition | `agentic_core.L1_cognition.reasoning.query_planner` |
| 2 | L1_cognition | `agentic_core.L1_cognition.reasoning.plan_creator` |
| 2 | L1_cognition | `agentic_core.L1_cognition.reasoning.SemanticMemory` |
| 2 | L0_routing | `agentic_core.L0_routing.types.boundary_types` |

**P3 total: 17 (showing top 100)**

## Notes

- Coverage measured by basename match: `tests/**/test_<leaf>.py`.
- Some matches may be name-collisions across layers (e.g. two modules named `types.py`).
- P5 (fanin=0) modules likely indicate dead code or test-only modules — verify before adding tests.
- 340 hotspot tests added in this session prior to regeneration cover P1/P2 hotspots.
