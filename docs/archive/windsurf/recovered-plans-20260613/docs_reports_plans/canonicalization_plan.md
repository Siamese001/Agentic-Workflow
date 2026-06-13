# Agent Canonicalization Plan

**Date**: 2026-02-08
**Baseline**: 190 ACTIVE agents
**Target**: ≤150 ACTIVE agents

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Strategy

Old agent files are converted to **thin re-export shims** (import alias only, no ClassDef).
Discovery uses AST ClassDef scanning → shim files do NOT count as agents.
Backward compatibility preserved: existing imports continue to work.

---

## Retirements (19 agents → 0)

Files fully deleted (no replacement needed — zero domain logic).

| # | Agent | File | Domain LOC | Reason |
|---|-------|------|-----------|--------|
| 1 | OutreachAgent | apps_lic/engines/EngagementTrackerAgent.py | 0 | Duplicate stub |
| 2 | OutreachAgent | apps_lic/engines/MessageComplianceAgent.py | 0 | Duplicate stub |
| 3 | OutreachAgent | apps_lic/engines/OutreachLearningAgent.py | 0 | Duplicate stub |
| 4 | OutreachAgent | apps_lic/engines/OutreachProactiveAgent.py | 0 | Duplicate stub |
| 5 | OutreachAgent | apps_lic/engines/OutreachEngineCoordinator.py | 0 | Duplicate stub |
| 6 | MCPHardenedMixin | apps_lic/config/mcp_hardened_mixin.py | 0 | Not an agent |
| 7 | DiscoveredAgent | agentic_core/runtime/utils/discovery_util.py | 0 | Utility class |
| 8 | DependencyDiplomatAgent | agentic_core/L5_safety/reasoning/DependencyDiplomatAgent.py | 0 | Empty stub |
| 9 | SemanticTerritoryMapperAgent | agentic_core/L5_safety/reasoning/SemanticTerritoryMapperAgent.py | 2 | Near-empty stub |
| 10 | OmniContextAgent | agentic_core/L5_safety/reasoning/OmniContextAgent.py | 4 | Boilerplate wrapper |
| 11 | SemanticMapperAgent | agentic_core/L5_safety/reasoning/SemanticMapperAgent.py | 6 | Boilerplate wrapper |
| 12 | IntelligenceLibrarianAgent | apps_lic/engines/IntelligenceLibrarianAgent.py | 6 | Trivial stub |
| 13 | StrategistAgent | agentic_core/L1_cognition/reasoning/StrategistAgent.py | 7 | Boilerplate wrapper |
| 14 | GlobalComplianceAggregatorAgent | agentic_core/L5_safety/reasoning/GlobalComplianceAggregatorAgent.py | 8 | Boilerplate wrapper |
| 15 | MessageArchitectAgent | apps_lic/engines/MessageArchitectAgent.py | 8 | Trivial stub |
| 16 | UiValidationAgent | agentic_core/L2_execution/reasoning/UiValidationAgent.py | 10 | 97% boilerplate |
| 17 | CampaignPlannerAgent | apps_rg/reasoning/CampaignPlannerAgent.py | 11 | Trivial stub |
| 18 | CartographerAgent | agentic_core/runtime/cartographer/CartographerAgent.py | 29 | Legacy extracted stub |
| 19 | LeadQualityAgent | apps_lic/engines/LeadQualityAgent.py | 40 | Thin wrapper |

## Canonical Executors (6 created, 27 agents merged)

### 1. HOPPipelineExecutor (9 agents → 1)

**Canonical**: `apps_lic/engines/HOPPipelineExecutor.py`

| Old Agent | Stage ID | Domain LOC |
|-----------|----------|-----------|
| HOP1ProfileAnalysisAgent | 1 | 217 |
| HOP2ResearchAgent | 2 | 300 |
| HOP3SenderGroundingAgent | 3 | 121 |
| HOP4RoutingAgent | 4 | 98 |
| HOP5GenerationAgent | 5 | 353 |
| HOP6ValidationAgent | 6 | 111 |
| HOP7GateDecisionAgent | 7 | 51 |
| HOP8QAReportAgent | 8 | 109 |
| HOP9IntegrationAgent | 9 | 70 |

**Pattern**: Stage registry maps stage_id → _process function.
Old files become shims: `from .HOPPipelineExecutor import HOPPipelineExecutor as HOP<N>Agent`

### 2. RGValidationExecutor (4 agents → 1)

**Canonical**: `apps_rg/engines/RGValidationExecutor.py`

| Old Agent | Rule Set | Domain LOC |
|-----------|----------|-----------|
| ATSCompatibilityAgent | ats_compatibility | 72 |
| BrandComplianceAgent | brand_compliance | 43 |
| FactCheckAgent | fact_check | 90 |
| SectionBalanceAgent | section_balance | 41 |

**Pattern**: Rule registry maps rule_set → collect_issues function.

### 3. LICValidationExecutor (2 agents → 1)

**Canonical**: `apps_lic/engines/LICValidationExecutor.py`

| Old Agent | Rule Set | Domain LOC |
|-----------|----------|-----------|
| CampaignBalanceAgent | campaign_balance | 37 |
| DeliverabilityAgent | deliverability | 34 |

### 4. InspectorExecutor (3 agents → 1)

**Canonical**: `agentic_core/L5_safety/reasoning/InspectorExecutor.py`

| Old Agent | Inspector Type | Domain LOC |
|-----------|---------------|-----------|
| DagRuntimeInspectorAgent | dag_runtime | 0 (inherited) |
| SignatureVerifierAgent | signature | 0 (inherited) |
| TokenBudgetInspectorAgent | token_budget | 0 (inherited) |

### 5. ObservabilityProbeExecutor (6 agents → 1)

**Canonical**: `agentic_core/L6_observability/reasoning/ObservabilityProbeExecutor.py`

| Old Agent | Probe Type | Domain LOC |
|-----------|-----------|-----------|
| TrackObservabilityCostAgent | cost_tracker | 11 |
| CoordinateObservabilityOperationsAgent | coordinator | 45 |
| StrategicObservationAgent | strategic | 44 |
| DeadlockDetectorAgent | deadlock | 31 |
| DebateSynthesisAgent | debate | 75 |
| RuntimeTelemetryAgent | runtime_telemetry | 54 |

### 6. RGStrategyExecutor (3 agents → 1)

**Canonical**: `apps_rg/engines/RGStrategyExecutor.py`

| Old Agent | Strategy Type | Domain LOC |
|-----------|-------------|-----------|
| ContentStrategyAgent | content | 10 |
| RgStrategicPlannerAgent | strategic_planner | 44 |
| RgTemplateOptimizerAgent | template_optimizer | 54 |

## Projected Metrics

| Metric | Before | After |
|--------|--------|-------|
| Agent count | 190 | 150 |
| Retired | 0 | 19 |
| Merged | 0 | 27 |
| Canonical executors | 0 | 6 |
| Net reduction | 0 | 40 |

## Risk Rating

| Executor | Risk | Reason |
|----------|------|--------|
| HOPPipelineExecutor | HIGH | 9 agents, complex domain logic, many refs |
| RGValidationExecutor | MEDIUM | 4 agents, uniform structure |
| LICValidationExecutor | LOW | 2 agents, very similar |
| InspectorExecutor | LOW | 3 agents, already deduplicated |
| ObservabilityProbeExecutor | MEDIUM | 6 agents, varying complexity |
| RGStrategyExecutor | LOW | 3 agents, low domain logic |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

