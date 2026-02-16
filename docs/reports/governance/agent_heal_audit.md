# Agent Healing Audit Report

## Summary

- **Total Agents**: 136
- **Missing heal()**: 22
- **Missing heal_repository()**: 34
- **Missing Both**: 20

## Phase 2: Heal Escalation Policy Contracts

### Overview
Phase 2 introduces a pure policy contract module for agent healing escalation decisions. This module provides deterministic reasoning tier classification based on task complexity, confidence, safety risk, and retry count.

### Module Location
- `agentic_core/L5_safety/types/heal_policy_types.py`

### Key Components
1. **Enums**:
   - `ReasoningTier`: LOW, HIGH
   - `ConfidenceLevel`: LOW, MEDIUM, HIGH, VERY_HIGH

2. **Dataclasses**:
   - `HealEscalationInputs`: Input parameters for escalation decision
   - `HealEscalationDecision`: Output decision with tier and rationale

3. **Pure Functions**:
   - `classify_confidence(confidence: float) -> ConfidenceLevel`
   - `decide_reasoning_tier(inputs: HealEscalationInputs) -> HealEscalationDecision`

### Decision Logic
The `decide_reasoning_tier` function follows deterministic rules:
1. Validate input ranges
2. Apply trivial rule (low complexity, low risk, few retries) → LOW
3. Escalate to HIGH if ANY condition met:
   - confidence < 0.70
   - task_complexity >= 8
   - safety_risk >= 7
   - retry_count > 2
4. Otherwise default to LOW

### Integration Note
**No runtime integration in Phase 2.** This module provides the pure policy contract that will be consumed by future phases for actual escalation routing and execution.

### Tests
Comprehensive unit tests in `tests/governance/test_heal_policy_types.py` cover:
- Boundary conditions for confidence classification
- Ordered rule behavior and escalation triggers
- Determinism (same inputs produce identical decisions)
- Input validation with proper error handling

---

## Detailed Results

| Path | Class | heal | heal_repository |
|------|-------|------|-----------------|
| agentic_core/L0_routing/reasoning/RootCustomsAgent.py | RootCustomsAgent | ✓ | ✗ |
| agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py | SSOTFolderCleanupAgent | ✓ | ✓ |
| agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py | ASTValidatorAgent | ✓ | ✓ |
| agentic_core/L1_cognition/reasoning/MetaLearningAgent.py | MetaLearningAgent | ✓ | ✓ |
| agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py | StrategicRecommendationAgent | ✓ | ✓ |
| agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py | EmbeddingSovereignAgent | ✓ | ✓ |
| agentic_core/L2_execution/reasoning/StructuredEngineAgent.py | StructuredEngineAgent | ✓ | ✗ |
| agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py | SubAtomicRegistryAgent | ✓ | ✓ |
| agentic_core/L2_execution/reasoning/ToolsmithAgent.py | ToolsmithAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/CoverageAgent.py | CoverageAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py | DAGMutatorAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DagEngineAgent.py | DagEngineAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | DomainPlannerAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | FeasibilityAnalystAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | RiskAssessorAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | StrategyCoordinatorAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | StrategyScenarioSimulatorAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py | FissionManagerAgent | ✓ | ✗ |
| agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py | NervousSystemAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py | OrchestrationHandshakeAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py | SemanticGatekeeperAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/StateManagementAgent.py | StateManagementAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py | SubAtomicAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py | SubatomicHopAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/reasoning/UnifiedAgent.py | UnifiedAgent | ✓ | ✓ |
| agentic_core/L3_orchestration/types/orchestrator_types.py | IOrchestratorAgent | ✗ | ✗ |
| agentic_core/L4_state/reasoning/CachedStateLedgerAgent.py | CachedStateLedgerAgent | ✗ | ✓ |
| agentic_core/L4_state/reasoning/CheckpointManagerAgent.py | CheckpointManagerAgent | ✓ | ✓ |
| agentic_core/L4_state/reasoning/GravityStateAgent.py | GravityStateAgent | ✓ | ✓ |
| agentic_core/L4_state/reasoning/PineconeSovereignAgent.py | PineconeSovereignAgent | ✓ | ✓ |
| agentic_core/L4_state/reasoning/RedisSovereignAgent.py | RedisSovereignAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py | AdversarialProbeAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py | AdversarialRedTeamerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | ArchitectureGovernorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py | AutonomousThreatEvolutionAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py | AutonomyGuardianAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/BenchmarkingAgent.py | BenchmarkingAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/BootstrapAgent.py | BootstrapAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py | BoundaryTestingAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py | ChaosEngineeringAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py | CodeDeduplicationAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CodeDetectorAgent.py | CodeDetectorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py | CodeEnforcerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CodeFormatterAgent.py | CodeFormatterAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/CodeHealerAgent.py | CodeHealerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CodeValidatorAgent.py | CodeValidatorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py | CognitiveDispositionAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py | ComplexityAnalyzerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py | ConstitutionalReviewerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CostGovernorAgent.py | CostGovernorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/CredentialScannerAgent.py | CredentialScannerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py | DDDAlignmentAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DependencyPruningAgent.py | DependencyPruningAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py | DocstringComplianceAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DocumentationAgent.py | DocumentationAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py | DuplicateCodeDetectorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/DynamicSealAgent.py | DynamicSealAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | FileClassificationAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py | FilesystemSSOTReconcilerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py | GenerativeGuardAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/GitHygieneAgent.py | GitHygieneAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/GospelSyncAgent.py | GospelSyncAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/GovernanceAgent.py | GovernanceAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py | GravityLeakRepairAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/HierarchyAgent.py | HierarchyAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py | HygieneGuardianAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py | IntegrityGateExecutorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py | InterfaceBoundaryAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py | L5SafetyExerciserAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/LocationAgent.py | LocationAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/LocationHealerAgent.py | LocationHealerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/LocationValidatorAgent.py | LocationValidatorAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/NamingAgent.py | NamingAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py | NeuralAutoImmuneAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py | PolicyNeuralAutoImmuneAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py | PreCommitSovereignAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py | PredictiveCostAuditorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/RedSentinelAgent.py | RedSentinelAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/RedTeamAgent.py | RedTeamAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/RegressionOracleAgent.py | RegressionOracleAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/ReportLocationAgent.py | ReportLocationAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/ResourceManagerAgent.py | ResourceManagerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/RootHygieneAgent.py | RootHygieneAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py | SafetyDetectorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py | SafetyExecutorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py | SafetyInspectorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SecurityManagerAgent.py | SecurityManagerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py | SelfUpdatingSafetyEngineAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py | SovereignActionPlaneAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py | SprawlInspectorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py | StructuralEngineerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py | StructuralValidatorAgent | ✓ | ✗ |
| agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py | StructureEnforcerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/StructureHealerAgent.py | StructureHealerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/SystemArchitectAgent.py | SystemArchitectAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py | TerritoryChangeHandlerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/TestGeneratorAgent.py | TestGeneratorAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py | TypeHintFixerAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/TypeMechanicAgent.py | TypeMechanicAgent | ✓ | ✓ |
| agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py | UnusedCleanupAgent | ✓ | ✗ |
| agentic_core/base_agents/SovereignBaseAgent.py | SovereignBaseAgent | ✓ | ✗ |
| agentic_core/interfaces/IOrchestratorProtocol.py | ITieredAgent | ✗ | ✗ |
| apps_lic/config/placeholder_detector_agent_config.py | PlaceholderDetectorAgent | ✗ | ✓ |
| apps_lic/engines/DispatchOutreachToolsAgent.py | DispatchOutreachToolsAgent | ✓ | ✓ |
| apps_lic/engines/ExecutiveStrategyAgent.py | ExecutiveStrategyAgent | ✗ | ✗ |
| apps_lic/engines/GovernanceShieldAgent.py | GovernanceShieldAgent | ✓ | ✗ |
| apps_lic/engines/LicReflectionAgent.py | LicReflectionAgent | ✓ | ✓ |
| apps_lic/engines/LicTemplateOptimizerAgent.py | LicTemplateOptimizerAgent | ✓ | ✓ |
| apps_lic/engines/MessageComplianceAgent.py | MessageComplianceAgent | ✓ | ✓ |
| apps_lic/engines/OutreachLearningAgent.py | OutreachLearningAgent | ✓ | ✓ |
| apps_lic/engines/OutreachMessageAgent.py | OutreachMessageAgent | ✗ | ✗ |
| apps_lic/engines/OutreachProactiveAgent.py | OutreachProactiveAgent | ✓ | ✓ |
| apps_lic/engines/OutreachSignalRouterAgent.py | OutreachSignalRouterAgent | ✓ | ✓ |
| apps_lic/engines/OutreachValidationExecutorAgent.py | OutreachValidationExecutorAgent | ✓ | ✓ |
| apps_lic/engines/PIISanitizerSpecialistAgent.py | ConstitutionalReviewerAgent | ✗ | ✗ |
| apps_lic/engines/PIISanitizerSpecialistAgent.py | PII_SanitizerSpecialistAgent | ✓ | ✗ |
| apps_lic/engines/ValidatorAgent.py | ValidatorAgent | ✓ | ✗ |
| apps_lic/engines/competitor_recon_agent_types.py | CompetitorReconAgent | ✗ | ✗ |
| apps_lic/engines/stack_modernization_agent_types.py | StackModernizationAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | GateDecisionAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | GenerationAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ProfileAnalysisAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | QAReportAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ResearchAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | RoutingAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | SenderGroundingAgent | ✗ | ✗ |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ValidationAgent | ✗ | ✗ |
| apps_lic/types/app_content_validator_agent_types.py | AppContentValidatorAgent | ✗ | ✗ |
| apps_rg/engines/ResumeAssemblyAgent.py | ResumeAssemblyAgent | ✗ | ✗ |
| apps_rg/reasoning/ContentQualityAgent.py | ContentQualityAgent | ✓ | ✓ |
| apps_rg/reasoning/DispatchResumeToolsAgent.py | DispatchResumeToolsAgent | ✓ | ✓ |
| apps_rg/reasoning/ProactiveAgent.py | ProactiveAgent | ✓ | ✓ |
| apps_rg/reasoning/RgReflectionAgent.py | RgReflectionAgent | ✓ | ✓ |
| apps_rg/types/gap_closure_architect_agent_types.py | GapClosureArchitectAgent | ✗ | ✗ |
| apps_shared/utils/agent_interface.py | BaseAgent | ✗ | ✗ |
| apps_shared/utils/agent_interface.py | IAgent | ✗ | ✗ |
