# Deferred Cluster Re-Assessment

**Date**: 2026-02-09
**Thresholds**: code_similarity ≥ 0.75, responsibility_overlap ≥ 0.70

## Summary

| Cluster | Members | Code Sim (max) | Resp Overlap (max) | Verdict | Next Action |
| ------- | ------- | -------------- | ------------------- | ------- | ----------- |
| 1 | 13 | 0.795 | 1.0 | RE-SCOPE | Split into sub-clusters |
| 2 | 4 | 0.802 | 1.0 | ACTIONABLE | Extract RGValidationCapability |
| 3 | 4 | 0.254 | 1.0 | CLOSE | False positive (keyword collision) |
| 4 | 3 | 0.779 | 0.0 | RESOLVED | HOPStageCapability migration done |
| 5 | 2 | 0.828 | 0.0 | ACTIONABLE | Extract LICValidationCapability |
| 6 | 2 | 0.925 | 0.556 | DONE | CodeToolRunnerCapability extracted |
| 7 | 2 | 0.028 | 1.0 | DONE | ContentStrategyAgent deprecated |

## Detailed Verdicts

### Cluster 1 — RE-SCOPE (13 agents across 6 layers)

**Problem**: The cluster is too large and heterogeneous. 13 agents span L1, L2, L3, L5, L6, apps_lic, and apps_rg. Median code similarity is only 0.384 — the high max (0.795) is driven by isolated pairs:

- OmniContextAgent + SemanticMapperAgent (0.795) — both L5 retrieval/analysis
- UiValidationAgent + SemanticMapperAgent (0.780) — both L5 with shared testing mixin
- StrategistAgent + OmniContextAgent (0.771) — L1 + L5

**Recommendation**: Split into 3 sub-clusters based on actual pair similarity:

1. **L5 Semantic Group** (OmniContext, SemanticMapper, SemanticTerritoryMapper, UiValidation, Strategist) — code_sim 0.57-0.80. Extract `SemanticAnalysisCapability`.
2. **Inspector Group** (DagRuntimeInspector, TokenBudgetInspector, SignatureVerifier) — resp_overlap=1.0 ("inspection"). Extract `InspectionCapability`.
3. **Remaining** (CoordinateObservabilityOps, TrackObservabilityCost, IntelligenceLibrarian, RgStrategicPlanner, RgTemplateOptimizer) — no actionable pair similarity. Close.

### Cluster 2 — ACTIONABLE (4 RG validation agents)

**Agents**: ATSCompatibilityAgent (0.802), BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent

**Evidence**:
- ATSCompatibility + BrandCompliance: code_sim=0.802, shared base RGAgentBase, 4 shared methods
- All 4 share responsibility keyword "checks" (resp_overlap=1.0)
- All inherit from RGAgentBase with identical method signatures (execute, heal_repository, heal)

**Action**: Extract `RGValidationCapability` pure mixin with shared validation patterns (execute scaffold, result formatting, scoring). Each agent keeps domain-specific logic.

### Cluster 3 — CLOSE (false positive)

**Agents**: DynamicSealAgent (L5), HOP6ValidationAgent (apps_lic), HistorianAgent (L2), LicS2SupervisorAgent (apps_lic)

**Evidence**:
- Code similarity max=0.254 (far below 0.75 threshold)
- Responsibility overlap=1.0 is a false positive: all share keyword "validation" but perform completely different functions (seal management, draft QA, event history, research supervision)
- Different layers, different base classes, different method signatures

**Action**: Close. No consolidation warranted.

### Cluster 4 — RESOLVED by HOPStageCapability

**Agents**: HOP4RoutingAgent, HOP7GateDecisionAgent, HOP9IntegrationAgent

**Evidence**:
- Code similarity (0.717-0.779) was driven by shared IO plumbing pattern: manual buffer.read() + buffer.write_once() + registry.add_trace()
- Phase 3 migration extracted this shared plumbing into `HOPStageCapability`
- All 3 agents (plus 6 more) now use read_required_inputs() and write_output()

**Action**: Resolved. 39/39 structural tests pass. No further action needed.

### Cluster 5 — ACTIONABLE (2 LIC validation agents)

**Agents**: CampaignBalanceAgent (111 lines), DeliverabilityAgent (88 lines)

**Evidence**:
- Code similarity: 0.828 (above 0.75 threshold)
- Shared bases: SubatomicTestingMixin, LICAgentBase
- 4 shared methods: __post_init__, execute, heal_repository, heal
- Both are LIC domain validation agents in apps_lic/engines

**Action**: Extract `LICEngineValidationCapability` pure mixin with shared execute/heal scaffold. Each agent keeps domain-specific validation logic.

## Prioritized Backlog

1. **Cluster 5**: Extract LICEngineValidationCapability (small scope, 2 agents, high confidence)
2. **Cluster 2**: Extract RGValidationCapability (medium scope, 4 agents, high confidence)
3. **Cluster 1 sub-cluster A**: Extract SemanticAnalysisCapability (medium scope, 5 agents)
4. **Cluster 1 sub-cluster B**: Extract InspectionCapability (small scope, 3 agents)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

