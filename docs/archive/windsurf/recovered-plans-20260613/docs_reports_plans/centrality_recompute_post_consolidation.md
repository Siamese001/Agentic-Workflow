# Centrality Recompute — Post-Consolidation

**Date**: 2026-02-09
**Scope**: All Python files under `agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`
**Metric**: In-degree centrality (count of modules importing a given module)

## Top 20 Gravity Nodes

| Rank | Module | Importers | Category |
| ---- | ------ | --------- | -------- |
| 1 | `agentic_core.base_agents.SovereignBaseAgent` | 164 | Infrastructure (pre-existing) |
| 2 | `agentic_core.L5_safety.config.structure_blueprint_config` | 140 | Infrastructure (pre-existing) |
| 3 | `agentic_core.base_agents.decorators` | 94 | Infrastructure (pre-existing) |
| 4 | `agentic_core.base_agents.timeout_decorator` | 65 | Infrastructure (pre-existing) |
| 5 | `agentic_core.mixins.subatomic_testing_mixin` | 41 | Infrastructure (pre-existing) |
| 6 | `agentic_core.mixins.atomic_execution_mixin` | 28 | Infrastructure (pre-existing) |
| 7 | `agentic_core.L5_safety.enforcement.archival_gatekeeper` | 10 | Infrastructure (pre-existing) |
| 8 | `agentic_core.L5_safety.reasoning.HierarchyAgent` | 10 | Infrastructure (pre-existing) |
| 9 | `apps_rg.utils.RGAgentBase` | 9 | App base class (pre-existing) |
| 10 | `agentic_core.mixins.mcp_hardened_mixin` | 9 | Infrastructure (pre-existing) |
| 11 | `apps_lic.engines.HOPPipelineExecutor` | 9 | **Consolidation executor** |
| 12 | `agentic_core.L0_maintenance.scripts.full_agent_discovery` | 8 | Infrastructure (pre-existing) |
| 13 | `agentic_core.L3_orchestration.reasoning.UnifiedAgent` | 7 | Infrastructure (pre-existing) |
| 14 | `agentic_core.L5_safety.reasoning.FileClassificationAgent` | 7 | Infrastructure (pre-existing) |
| 15 | `agentic_core.L5_safety.reasoning.CodeHealerAgent` | 7 | Infrastructure (pre-existing) |
| 16 | `agentic_core.L5_safety.types.healing_orchestration_types` | 6 | Infrastructure (pre-existing) |
| 17 | `agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor` | 6 | **Consolidation executor** |
| 18 | `agentic_core.L5_safety.config.structure_blueprint.enforcement.types` | 6 | Infrastructure (pre-existing) |
| 19 | `agentic_core.L5_safety.reasoning.CodeValidatorAgent` | 6 | Infrastructure (pre-existing) |
| 20 | `apps_shared.utils.ConfigurationService` | 6 | Infrastructure (pre-existing) |

## Consolidation Executor Centrality

| Executor | Importers | Source |
| -------- | --------- | ------ |
| `HOPPipelineExecutor` | 9 | HOP1-HOP9 backward-compat alias shims |
| `ObservabilityProbeExecutor` | 6 | Observability alias shims |
| `LICValidationExecutor` | 2 | DeliverabilityAgent + CampaignBalanceAgent shims |
| `RGValidationExecutor` | 0 | No shim importers (agents in `reasoning/`) |
| `RGStrategyExecutor` | 0 | No shim importers |
| `InspectorExecutor` | 3 | Inspector alias shims |

## Assessment

- **No unexpected gravity nodes** emerged from the consolidation.
- The two highest-centrality executors (`HOPPipelineExecutor` at 9, `ObservabilityProbeExecutor` at 6) are expected — their importers are purely backward-compatibility alias shims.
- The top infrastructure nodes (`SovereignBaseAgent` 164, `structure_blueprint_config` 140) are unchanged and pre-existing.
- **Verdict**: Consolidation did not introduce new architectural risk. The import graph is healthier after removing broken `__init__.py` chains.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

