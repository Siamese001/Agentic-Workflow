# Agent Consolidation Plan

**Generated from**: 190 active agents
**Clusters identified**: 7

## Cluster 1

- **Members** (13): CoordinateObservabilityOperationsAgent, DagRuntimeInspectorAgent, IntelligenceLibrarianAgent, OmniContextAgent, RgStrategicPlannerAgent__RgStrategicPlannerAgent, RgTemplateOptimizerAgent, SemanticMapperAgent, SemanticTerritoryMapperAgent, SignatureVerifierAgent, StrategistAgent, TokenBudgetInspectorAgent, TrackObservabilityCostAgent, UiValidationAgent
- **Code similarity**: min=0.107, median=0.384, max=0.795
- **Prompt similarity**: min=0.006, median=0.113, max=0.838
- **Responsibility overlap**: min=0.0, median=0.0, max=1.0
- **Risk**: high
- **Recommendation**: RE-SCOPE agents (responsibilities ambiguous)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CoordinateObservabilityOperationsAgent | L6_observability | 177 | AtomicExecutionMixin, SubatomicTestingMixin, SovereignBaseAgent | __init__, add_step, execute, heal, heal_repository | orchestrator |
| DagRuntimeInspectorAgent | L3_orchestration | 93 | AtomicExecutionMixin, SubatomicTestingMixin, SovereignBaseAgent | __init__, heal_repository, diagnose, heal | inspection |
| IntelligenceLibrarianAgent | apps_lic | 34 | SubatomicTestingMixin, LICAgentBase | __post_init__, query_intelligence | retrieval |
| OmniContextAgent | L5_safety | 78 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal_repository, heal | retrieval |
| RgStrategicPlannerAgent__RgStrategicPlannerAgent | apps_rg | 98 | RGAgentBase | __post_init__, execute, heal_repository, heal | analyzes, state |
| RgTemplateOptimizerAgent | apps_rg | 115 | RGAgentBase | __post_init__, execute, _detect_job_type, heal_repository, heal | analyzes |
| SemanticMapperAgent | L5_safety | 73 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal_repository, heal | analyzes |
| SemanticTerritoryMapperAgent | L5_safety | 51 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal | - |
| SignatureVerifierAgent | L5_safety | 138 | SubatomicTestingMixin, SovereignBaseAgent | __init__, execute, _process, heal_repository, heal | inspection |
| StrategistAgent | L1_cognition | 87 | SubatomicTestingMixin, SovereignBaseAgent | can_run, execute, heal_repository, heal | code |
| TokenBudgetInspectorAgent | L5_safety | 89 | SubatomicTestingMixin, SovereignBaseAgent | __init__, heal_repository, heal, diagnose | inspection |
| TrackObservabilityCostAgent | L6_observability | 120 | AtomicExecutionMixin, SubatomicTestingMixin, SovereignBaseAgent | __init__, execute, _process, heal, heal_repository | - |
| UiValidationAgent | L2_execution | 168 | SubatomicTestingMixin, SovereignBaseAgent | can_run, execute, heal, heal_repository | validate, validator |

### Proposed Canonical Agent

- **Target**: `CoordinateObservabilityOperationsAgent`
- **File**: `agentic_core\L6_observability\reasoning\CoordinateObservabilityOperationsAgent.py`
- **Layer**: L6_observability

### Backward Compatibility

- `DagRuntimeInspectorAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `IntelligenceLibrarianAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `OmniContextAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `RgStrategicPlannerAgent__RgStrategicPlannerAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `RgTemplateOptimizerAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `SemanticMapperAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `SemanticTerritoryMapperAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `SignatureVerifierAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `StrategistAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `TokenBudgetInspectorAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `TrackObservabilityCostAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`
- `UiValidationAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`

### Migration Steps

1. Extract shared logic into canonical agent `CoordinateObservabilityOperationsAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 2

- **Members** (4): ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
- **Code similarity**: min=0.49, median=0.636, max=0.802
- **Prompt similarity**: min=0.152, median=0.245, max=0.455
- **Responsibility overlap**: min=0.25, median=1.0, max=1.0
- **Risk**: medium
- **Recommendation**: RE-SCOPE agents (responsibilities ambiguous)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| ATSCompatibilityAgent | apps_rg | 277 | RGAgentBase | __post_init__, execute, _calculate_keyword_score, heal_repository, heal | checks, formatting, tracking, validates |
| BrandComplianceAgent | apps_rg | 221 | RGAgentBase | __post_init__, execute, _to_string, heal_repository, heal | checks |
| FactCheckAgent | apps_rg | 147 | RGAgentBase | __post_init__, execute, _extract_skills, _normalize, heal_repository | checks |
| SectionBalanceAgent | apps_rg | 129 | RGAgentBase | __post_init__, execute, _to_string, heal_repository, heal | checks |

### Proposed Canonical Agent

- **Target**: `ATSCompatibilityAgent`
- **File**: `apps_rg\reasoning\ATSCompatibilityAgent.py`
- **Layer**: apps_rg

### Backward Compatibility

- `BrandComplianceAgent` → redirect/shim to `ATSCompatibilityAgent`
- `FactCheckAgent` → redirect/shim to `ATSCompatibilityAgent`
- `SectionBalanceAgent` → redirect/shim to `ATSCompatibilityAgent`

### Migration Steps

1. Extract shared logic into canonical agent `ATSCompatibilityAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 3

- **Members** (4): DynamicSealAgent, HOP6ValidationAgent, HistorianAgent, LicS2SupervisorAgent
- **Code similarity**: min=0.044, median=0.197, max=0.254
- **Prompt similarity**: min=0.038, median=0.094, max=0.202
- **Responsibility overlap**: min=1.0, median=1.0, max=1.0
- **Risk**: medium
- **Recommendation**: RE-SCOPE agents (responsibilities ambiguous)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| DynamicSealAgent | L5_safety | 359 | SubatomicTestingMixin, SovereignBaseAgent | heal_repository, __init__, heal, execute_sprint, _apply_seal | validation |
| HOP6ValidationAgent | apps_lic | 155 | SubatomicTestingMixin, LICAgentBase | __post_init__, _process, _check_placeholders, _check_strategic_alignment, _check_forbidden_verbs | validation |
| HistorianAgent | L2_execution | 229 | AtomicExecutionMixin, SovereignBaseAgent | __init__, execute, record_event, heal_repository, heal | validation |
| LicS2SupervisorAgent | apps_lic | 410 | SovereignBaseAgent | heal_repository, __init__, orchestrate_research, _run_adversarial_check, _extract_sender_grounding | validation |

### Proposed Canonical Agent

- **Target**: `LicS2SupervisorAgent`
- **File**: `apps_lic\engines\LicS2SupervisorAgent.py`
- **Layer**: apps_lic

### Backward Compatibility

- `DynamicSealAgent` → redirect/shim to `LicS2SupervisorAgent`
- `HOP6ValidationAgent` → redirect/shim to `LicS2SupervisorAgent`
- `HistorianAgent` → redirect/shim to `LicS2SupervisorAgent`

### Migration Steps

1. Extract shared logic into canonical agent `LicS2SupervisorAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 4

- **Members** (3): HOP4RoutingAgent, HOP7GateDecisionAgent, HOP9IntegrationAgent
- **Code similarity**: min=0.717, median=0.75, max=0.779
- **Prompt similarity**: min=0.083, median=0.109, max=0.166
- **Responsibility overlap**: min=0.0, median=0.0, max=0.0
- **Risk**: low
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| HOP4RoutingAgent | apps_lic | 136 | SubatomicTestingMixin, LICAgentBase | __post_init__, _process, _check_conditions | - |
| HOP7GateDecisionAgent | apps_lic | 91 | SubatomicTestingMixin, LICAgentBase | __post_init__, _process | classifies, classify |
| HOP9IntegrationAgent | apps_lic | 117 | SubatomicTestingMixin, LICAgentBase | __post_init__, _process | checksum, formatting, healing, tracing |

### Proposed Canonical Agent

- **Target**: `HOP4RoutingAgent`
- **File**: `apps_lic\engines\Hop4RoutingAgent.py`
- **Layer**: apps_lic

### Backward Compatibility

- `HOP7GateDecisionAgent` → redirect/shim to `HOP4RoutingAgent`
- `HOP9IntegrationAgent` → redirect/shim to `HOP4RoutingAgent`

### Migration Steps

1. Extract shared logic into canonical agent `HOP4RoutingAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 5

- **Members** (2): CampaignBalanceAgent, DeliverabilityAgent
- **Code similarity**: min=0.828, median=0.828, max=0.828
- **Prompt similarity**: min=0.251, median=0.251, max=0.251
- **Responsibility overlap**: min=0.0, median=0.0, max=0.0
- **Risk**: low
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CampaignBalanceAgent | apps_lic | 111 | SubatomicTestingMixin, LICAgentBase | __post_init__, execute, heal_repository, heal | structure, validates, validator |
| DeliverabilityAgent | apps_lic | 88 | SubatomicTestingMixin, LICAgentBase | __post_init__, execute, heal_repository, heal | - |

### Proposed Canonical Agent

- **Target**: `CampaignBalanceAgent`
- **File**: `apps_lic\engines\CampaignBalanceAgent.py`
- **Layer**: apps_lic

### Backward Compatibility

- `DeliverabilityAgent` → redirect/shim to `CampaignBalanceAgent`

### Migration Steps

1. Extract shared logic into canonical agent `CampaignBalanceAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 6

- **Members** (2): CodeFormatterAgent, UnusedCleanupAgent
- **Code similarity**: min=0.925, median=0.925, max=0.925
- **Prompt similarity**: min=0.468, median=0.468, max=0.468
- **Responsibility overlap**: min=0.556, median=0.556, max=0.556
- **Risk**: low
- **Recommendation**: MERGE

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CodeFormatterAgent | L5_safety | 96 | CodeToolRunnerCapability, SovereignBaseAgent | execute | code, codetoolrunnercapability, enforces, fixes, formatting |
| UnusedCleanupAgent | L5_safety | 85 | CodeToolRunnerCapability, SovereignBaseAgent | execute | codetoolrunnercapability, heal_repository, healing, safety, telemetry |

### Proposed Canonical Agent

- **Target**: `CodeFormatterAgent`
- **File**: `agentic_core\L5_safety\reasoning\CodeFormatterAgent.py`
- **Layer**: L5_safety

### Backward Compatibility

- `UnusedCleanupAgent` → redirect/shim to `CodeFormatterAgent`

### Migration Steps

1. Extract shared logic into canonical agent `CodeFormatterAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 7

- **Members** (2): ContentStrategyAgent, RgStrategicPlannerAgent
- **Code similarity**: min=0.028, median=0.028, max=0.028
- **Prompt similarity**: min=0.066, median=0.066, max=0.066
- **Responsibility overlap**: min=1.0, median=1.0, max=1.0
- **Risk**: low
- **Recommendation**: RETIRE redundant agent (if superseded)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| ContentStrategyAgent | apps_rg | 50 | RGAgentBase | __post_init__, analyze_topic | analyzes, generates |
| RgStrategicPlannerAgent | L2_execution | 192 | AtomicExecutionMixin, SovereignBaseAgent | __init__, execute, heal, heal_repository | analyzes, generates |

### Proposed Canonical Agent

- **Target**: `RgStrategicPlannerAgent`
- **File**: `agentic_core\L2_execution\reasoning\RgStrategicPlannerAgent.py`
- **Layer**: L2_execution

### Backward Compatibility

- `ContentStrategyAgent` → redirect/shim to `RgStrategicPlannerAgent`

### Migration Steps

1. Extract shared logic into canonical agent `RgStrategicPlannerAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

