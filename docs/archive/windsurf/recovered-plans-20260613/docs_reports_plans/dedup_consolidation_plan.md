# Agent Consolidation Plan

**Generated from**: 190 active agents
**Clusters identified**: 10

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Cluster 1

- **Members** (8): IntelligenceLibrarianAgent, OmniContextAgent, RgStrategicPlannerAgent__RgStrategicPlannerAgent, RgTemplateOptimizerAgent, SemanticMapperAgent, SemanticTerritoryMapperAgent, StrategistAgent, UiValidationAgent
- **Code similarity**: min=0.229, median=0.385, max=0.795
- **Prompt similarity**: min=0.006, median=0.191, max=0.702
- **Responsibility overlap**: min=0.0, median=0.0, max=1.0
- **Risk**: high
- **Recommendation**: RE-SCOPE agents (responsibilities ambiguous)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| IntelligenceLibrarianAgent | apps_lic | 34 | SubatomicTestingMixin, LICAgentBase | __post_init__, query_intelligence | retrieval |
| OmniContextAgent | L5_safety | 78 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal_repository, heal | retrieval |
| RgStrategicPlannerAgent__RgStrategicPlannerAgent | apps_rg | 98 | RGAgentBase | __post_init__, execute, heal_repository, heal | analyzes, state |
| RgTemplateOptimizerAgent | apps_rg | 115 | RGAgentBase | __post_init__, execute, _detect_job_type, heal_repository, heal | analyzes |
| SemanticMapperAgent | L5_safety | 73 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal_repository, heal | analyzes |
| SemanticTerritoryMapperAgent | L5_safety | 51 | SubatomicTestingMixin, SovereignBaseAgent | execute, heal | - |
| StrategistAgent | L1_cognition | 87 | SubatomicTestingMixin, SovereignBaseAgent | can_run, execute, heal_repository, heal | code |
| UiValidationAgent | L2_execution | 168 | SubatomicTestingMixin, SovereignBaseAgent | can_run, execute, heal, heal_repository | validate, validator |

### Proposed Canonical Agent

- **Target**: `UiValidationAgent`
- **File**: `agentic_core\L2_execution\reasoning\UiValidationAgent.py`
- **Layer**: L2_execution

### Backward Compatibility

- `IntelligenceLibrarianAgent` → redirect/shim to `UiValidationAgent`
- `OmniContextAgent` → redirect/shim to `UiValidationAgent`
- `RgStrategicPlannerAgent__RgStrategicPlannerAgent` → redirect/shim to `UiValidationAgent`
- `RgTemplateOptimizerAgent` → redirect/shim to `UiValidationAgent`
- `SemanticMapperAgent` → redirect/shim to `UiValidationAgent`
- `SemanticTerritoryMapperAgent` → redirect/shim to `UiValidationAgent`
- `StrategistAgent` → redirect/shim to `UiValidationAgent`

### Migration Steps

1. Extract shared logic into canonical agent `UiValidationAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 2

- **Members** (4): ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
- **Code similarity**: min=0.679, median=0.742, max=0.821
- **Prompt similarity**: min=0.265, median=0.303, max=0.416
- **Responsibility overlap**: min=0.25, median=1.0, max=1.0
- **Risk**: medium
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| ATSCompatibilityAgent | apps_rg | 139 | RGValidationCapability, RGAgentBase | __post_init__, execute, collect_issues, _calculate_keyword_score, heal_repository | checks, formatting, tracking, validates |
| BrandComplianceAgent | apps_rg | 110 | RGValidationCapability, RGAgentBase | __post_init__, execute, collect_issues, heal_repository, heal | checks |
| FactCheckAgent | apps_rg | 139 | RGValidationCapability, RGAgentBase | __post_init__, execute, collect_issues, _extract_skills, _normalize | checks |
| SectionBalanceAgent | apps_rg | 98 | RGValidationCapability, RGAgentBase | __post_init__, execute, collect_issues, heal_repository, heal | checks |

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
- **Code similarity**: min=0.037, median=0.197, max=0.268
- **Prompt similarity**: min=0.038, median=0.094, max=0.202
- **Responsibility overlap**: min=1.0, median=1.0, max=1.0
- **Risk**: medium
- **Recommendation**: RE-SCOPE agents (responsibilities ambiguous)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| DynamicSealAgent | L5_safety | 359 | SubatomicTestingMixin, SovereignBaseAgent | heal_repository, __init__, heal, execute_sprint, _apply_seal | validation |
| HOP6ValidationAgent | apps_lic | 162 | HOPStageCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, _process, _check_placeholders, _check_strategic_alignment, _check_forbidden_verbs | validation |
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

- **Members** (3): DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
- **Code similarity**: min=0.698, median=0.749, max=0.837
- **Prompt similarity**: min=0.206, median=0.208, max=0.605
- **Responsibility overlap**: min=0.25, median=0.333, max=0.5
- **Risk**: low
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| DagRuntimeInspectorAgent | L3_orchestration | 56 | InspectionCapability, AtomicExecutionMixin, SubatomicTestingMixin | __init__, diagnose, heal_repository, heal | dag, inspector |
| SignatureVerifierAgent | L5_safety | 100 | InspectionCapability, SubatomicTestingMixin, SovereignBaseAgent | __init__, diagnose, heal_repository, heal | inspector |
| TokenBudgetInspectorAgent | L5_safety | 59 | InspectionCapability, SubatomicTestingMixin, SovereignBaseAgent | __init__, diagnose, heal_repository, heal | budget, inspector, token |

### Proposed Canonical Agent

- **Target**: `SignatureVerifierAgent`
- **File**: `agentic_core\L5_safety\reasoning\SignatureVerifierAgent.py`
- **Layer**: L5_safety

### Backward Compatibility

- `DagRuntimeInspectorAgent` → redirect/shim to `SignatureVerifierAgent`
- `TokenBudgetInspectorAgent` → redirect/shim to `SignatureVerifierAgent`

### Migration Steps

1. Extract shared logic into canonical agent `SignatureVerifierAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 5

- **Members** (3): HOP4RoutingAgent, HOP7GateDecisionAgent, HOP9IntegrationAgent
- **Code similarity**: min=0.782, median=0.783, max=0.827
- **Prompt similarity**: min=0.083, median=0.109, max=0.166
- **Responsibility overlap**: min=0.0, median=0.0, max=0.0
- **Risk**: low
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| HOP4RoutingAgent | apps_lic | 146 | HOPStageCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, _process, _check_conditions | - |
| HOP7GateDecisionAgent | apps_lic | 97 | HOPStageCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, _process | classifies, classify |
| HOP9IntegrationAgent | apps_lic | 119 | HOPStageCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, _process | checksum, formatting, healing, tracing |

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

## Cluster 6

- **Members** (2): CampaignBalanceAgent, DeliverabilityAgent
- **Code similarity**: min=0.867, median=0.867, max=0.867
- **Prompt similarity**: min=0.246, median=0.246, max=0.246
- **Responsibility overlap**: min=0.0, median=0.0, max=0.0
- **Risk**: low
- **Recommendation**: MERGE

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CampaignBalanceAgent | apps_lic | 112 | LICEngineValidationCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, execute, _validate, heal_repository, heal | structure, validates, validator |
| DeliverabilityAgent | apps_lic | 93 | LICEngineValidationCapability, SubatomicTestingMixin, LICAgentBase | __post_init__, execute, _validate, heal_repository, heal | - |

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

## Cluster 7

- **Members** (2): CodeFormatterAgent, UnusedCleanupAgent
- **Code similarity**: min=0.925, median=0.925, max=0.925
- **Prompt similarity**: min=0.468, median=0.468, max=0.468
- **Responsibility overlap**: min=0.556, median=0.556, max=0.556
- **Risk**: low
- **Recommendation**: MERGE

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CodeFormatterAgent | L5_safety | 97 | CodeToolRunnerCapability, SovereignBaseAgent | execute | code, codetoolrunnercapability, enforces, fixes, formatting |
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

## Cluster 8

- **Members** (2): ConfigurationSecurityGuardrailAgent, input_validation_guardrail
- **Code similarity**: min=0.741, median=0.741, max=0.741
- **Prompt similarity**: min=0.152, median=0.152, max=0.152
- **Responsibility overlap**: min=0.286, median=0.286, max=0.286
- **Risk**: low
- **Recommendation**: SPLIT shared core into library + thin wrappers

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| ConfigurationSecurityGuardrailAgent | L5_safety | 180 | SovereignBaseAgent | __post_init__, validate_config, _apply_rule, _detect_secrets, _validate_config_structure | detection, enforcement, secret, security, validation |
| input_validation_guardrail | L5_safety | 232 | SovereignBaseAgent | __post_init__, validate, _apply_rule, _detect_pii, _detect_prompt_injection | detection, pii, prompt, validation |

### Proposed Canonical Agent

- **Target**: `input_validation_guardrail`
- **File**: `agentic_core\L5_safety\enforcement\input_validation_guardrail.py`
- **Layer**: L5_safety

### Backward Compatibility

- `ConfigurationSecurityGuardrailAgent` → redirect/shim to `input_validation_guardrail`

### Migration Steps

1. Extract shared logic into canonical agent `input_validation_guardrail`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

## Cluster 9

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

## Cluster 10

- **Members** (2): CoordinateObservabilityOperationsAgent, TrackObservabilityCostAgent
- **Code similarity**: min=0.625, median=0.625, max=0.625
- **Prompt similarity**: min=0.838, median=0.838, max=0.838
- **Responsibility overlap**: min=0.0, median=0.0, max=0.0
- **Risk**: low
- **Recommendation**: RETIRE redundant agent (if superseded)

### Member Details

| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |
|-------|-------|-------|-------------|-------------|------------------------|
| CoordinateObservabilityOperationsAgent | L6_observability | 177 | AtomicExecutionMixin, SubatomicTestingMixin, SovereignBaseAgent | __init__, add_step, execute, heal, heal_repository | orchestrator |
| TrackObservabilityCostAgent | L6_observability | 120 | AtomicExecutionMixin, SubatomicTestingMixin, SovereignBaseAgent | __init__, execute, _process, heal, heal_repository | - |

### Proposed Canonical Agent

- **Target**: `CoordinateObservabilityOperationsAgent`
- **File**: `agentic_core\L6_observability\reasoning\CoordinateObservabilityOperationsAgent.py`
- **Layer**: L6_observability

### Backward Compatibility

- `TrackObservabilityCostAgent` → redirect/shim to `CoordinateObservabilityOperationsAgent`

### Migration Steps

1. Extract shared logic into canonical agent `CoordinateObservabilityOperationsAgent`
2. Convert other members to thin shims importing from canonical
3. Update all imports/registry references
4. Add regression tests for merged behavior
5. Run `full_agent_discovery.py` to verify count reduction

---

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

