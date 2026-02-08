# Structural Similarity Waivers — 2026-02-08

## Context

Deduplication analysis identified 10 clusters of agents with elevated similarity scores.
After manual review, the following clusters were determined to have **structural similarity**
from shared capability patterns, NOT actual code duplication. Each agent retains distinct
domain logic.

## Waivers Granted

### Cluster 2: RGValidationCapability (apps_rg)

- **Agents**: ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
- **Similarity source**: All inherit `RGValidationCapability` + `RGAgentBase`
- **Distinct logic**: Each has unique `collect_issues()` implementation
- **Decision**: WAIVER — structural similarity by design

### Cluster 4: InspectionCapability (agentic_core)

- **Agents**: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
- **Similarity source**: All inherit `InspectionCapability`
- **Action taken**: Deduplicated identical `perform_checks()` placeholder into
  `InspectionCapability` base class. Agents now inherit default implementation.
- **Decision**: WAIVER + CODE DEDUP — shared core extracted

### Cluster 5: HOPStageCapability (apps_lic)

- **Agents**: HOP4RoutingAgent, HOP7GateDecisionAgent, HOP9IntegrationAgent
- **Similarity source**: All inherit `HOPStageCapability` + `LICAgentBase`
- **Distinct logic**: Each has unique `_process()` implementation (different pipeline stages)
- **Decision**: WAIVER — pipeline stages share harness by design

### Cluster 6: LICEngineValidationCapability (apps_lic)

- **Agents**: CampaignBalanceAgent, DeliverabilityAgent
- **Similarity source**: Both inherit `LICEngineValidationCapability` + `LICAgentBase`
- **Distinct logic**: Each has unique `_validate()` with different business rules
- **Decision**: WAIVER — structural similarity by design

### Cluster 7: CodeToolRunnerCapability (agentic_core)

- **Agents**: CodeFormatterAgent, UnusedCleanupAgent
- **Similarity source**: Both inherit `CodeToolRunnerCapability`
- **Decision**: WAIVER — previously consolidated (2026-02-08)

### Cluster 10: L6 Observability (agentic_core)

- **Agents**: CoordinateObservabilityOperationsAgent, TrackObservabilityCostAgent
- **Similarity source**: Shared base classes + auto-inserted semantic signals
- **Distinct logic**: Orchestrator (multi-step workflow) vs pass-through tracker
- **Decision**: WAIVER — different purposes, prompt similarity is artifact of auto-signals

## Approval

Reviewed and approved as part of deduplication pipeline Phase 3 (2026-02-08).
