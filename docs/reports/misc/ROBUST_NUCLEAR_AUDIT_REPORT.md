# ROBUST NUCLEAR AUDIT REPORT: Agent Technical Status
Generated: 2026-01-29T16:04:11.073925
Total Agents Analyzed: 159

## Summary Statistics
- Total Agents: 159
- Broken Inheritance: 5 (3.1%)
- Missing heal() Method: 159 (100.0%)
- Invalid Namespace: 159 (100.0%)
- Stub/Incomplete Agents: 17 (10.7%)
- Fully Compliant: 0 (0.0%)

## Agent Distribution by Layer

- Base: 1 agents
- L0: 5 agents
- L1: 7 agents
- L2: 8 agents
- L3: 18 agents
- L4: 6 agents
- L5: 97 agents
- L6: 13 agents
- Unknown: 4 agents

## Detailed Technical Status

| Agent | Layer | File | Inheritance | heal() | Namespace | Type | Complexity | Issues |
|-------|-------|------|-------------|--------|-----------|------|------------|--------|
| BootstrapAgent | L0 | maintenance\scripts\BootstrapAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 4.0 | ISSUES 2 |
| L0MaintenanceBaseAgent | L0 | nce\scripts\L0MaintenanceBaseAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 5.0 | ISSUES 2 |
| CompliantAgent | L0 | aintenance\scripts\lifecycle_audit.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| ZombieAgent | L0 | aintenance\scripts\lifecycle_audit.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| NoKwargsAgent | L0 | aintenance\scripts\lifecycle_audit.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| ASTValidatorAgent | L1 | n\thought_engine\ASTValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 55.0 | ISSUES 2 |
| AutonomousPromptEvolutionAgent | L1 | ine\AutonomousPromptEvolutionAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 38.0 | ISSUES 2 |
| BudgetAgent | L1 | gnition\thought_engine\BudgetAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 6.5 | ISSUES 2 |
| LLMPromptGovernorAgent | L1 | ught_engine\LLMPromptGovernorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 24.0 | ISSUES 2 |
| MetaLearningAgent | L1 | n\thought_engine\MetaLearningAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 21.5 | ISSUES 2 |
| SovereignCognitivePlaneAgent | L1 | ngine\SovereignCognitivePlaneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 14.5 | ISSUES 2 |
| StrategicRecommendationAgent | L1 | ngine\StrategicRecommendationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 46.0 | ISSUES 2 |
| EmbeddingSovereignAgent | L2 | cution\mcp\EmbeddingSovereignAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 25.5 | ISSUES 2 |
| HistorianAgent | L2 | ution\tool_registry\HistorianAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 16.0 | ISSUES 2 |
| IntegrityGateExecutorAgent | L2 | egistry\IntegrityGateExecutorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 28.5 | ISSUES 3 |
| PeerIntelligenceAuditorAgent | L2 | istry\PeerIntelligenceAuditorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 31.0 | ISSUES 2 |
| RgStrategicPlannerAgent | L2 | l_registry\RgStrategicPlannerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 13.0 | ISSUES 2 |
| SubAtomicRegistryAgent | L2 | ol_registry\SubAtomicRegistryAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 28.0 | ISSUES 2 |
| ToolsmithAgent | L2 | ution\tool_registry\ToolsmithAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 58.0 | ISSUES 3 |
| DomainPlannerAgent | L3 | orkflow_engines\DomainPlannerAgent.py | [PARTIAL] | [MISSING] - No heal() method | [INVALID] | Concrete | 5.0 | ISSUES 2 |
| RiskAssessorAgent | L3 | orkflow_engines\DomainPlannerAgent.py | [PARTIAL] | [MISSING] - No heal() method | [INVALID] | Concrete | 5.5 | ISSUES 2 |
| FeasibilityAnalystAgent | L3 | orkflow_engines\DomainPlannerAgent.py | [PARTIAL] | [MISSING] - No heal() method | [INVALID] | Concrete | 6.0 | ISSUES 2 |
| StrategyScenarioSimulatorAgent | L3 | orkflow_engines\DomainPlannerAgent.py | [PARTIAL] | [MISSING] - No heal() method | [INVALID] | Concrete | 11.0 | ISSUES 2 |
| StrategyCoordinatorAgent | L3 | orkflow_engines\DomainPlannerAgent.py | [PARTIAL] | [MISSING] - No heal() method | [INVALID] | Concrete | 12.5 | ISSUES 2 |
| OrchestratorAgent | L3 | L3_orchestration\OrchestratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 54.5 | ISSUES 2 |
| SubAtomicAgent | L3 | ation\fission_logic\SubAtomicAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 4.0 | ISSUES 2 |
| CoverageAgent | L3 | ion\workflow_engines\CoverageAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 24.5 | ISSUES 2 |
| DagEngineAgent | L3 | on\workflow_engines\DagEngineAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 54.0 | ISSUES 2 |
| DAGMutatorAgent | L3 | n\workflow_engines\DAGMutatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 39.0 | ISSUES 2 |
| DagRuntimeInspectorAgent | L3 | w_engines\DagRuntimeInspectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 7.5 | ISSUES 2 |
| DecompositionOrchestratorAgent | L3 | nes\DecompositionOrchestratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 35.5 | ISSUES 3 |
| FissionManagerAgent | L3 | rkflow_engines\FissionManagerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 2 |
| NervousSystemAgent | L3 | orkflow_engines\NervousSystemAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 88.5 | ISSUES 2 |
| OrchestrationHandshakeAgent | L3 | ngines\OrchestrationHandshakeAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 14.0 | ISSUES 2 |
| SovereignRagOrchestratorAgent | L3 | ines\SovereignRagOrchestratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 39.0 | ISSUES 2 |
| SovereignRedisOrchestratorAgent | L3 | es\SovereignRedisOrchestratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 25.0 | ISSUES 2 |
| CheckpointManagerAgent | L4 | ion_context\CheckpointManagerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 74.5 | ISSUES 2 |
| GravityStateAgent | L4 | lidation_context\GravityStateAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 31.5 | ISSUES 2 |
| StateManagementAgent | L4 | ation_context\StateManagementAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 96.0 | ISSUES 2 |
| StateValidatorAgent | L4 | dation_context\StateValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 12.0 | ISSUES 2 |
| TestCoverageGuardianAgent | L4 | _context\TestCoverageGuardianAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 60.5 | ISSUES 3 |
| UiValidationAgent | L4 | lidation_context\UiValidationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 4.0 | ISSUES 2 |
| GravityLeakRepairAgent | L5 | ety\gravity\GravityLeakRepairAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 25.0 | ISSUES 3 |
| AdversarialRedTeamerAgent | L5 | ardrails\AdversarialRedTeamerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 59.0 | ISSUES 2 |
| AutonomousThreatEvolutionAgent | L5 | ils\AutonomousThreatEvolutionAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 28.0 | ISSUES 2 |
| CodeFormatterAgent | L5 | fety\guardrails\CodeFormatterAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 14.0 | ISSUES 2 |
| ConstitutionalReviewerAgent | L5 | drails\ConstitutionalReviewerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 7.5 | ISSUES 2 |
| CostGovernorAgent | L5 | afety\guardrails\CostGovernorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 2 |
| DependencyPruningAgent | L5 | \guardrails\DependencyPruningAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 19.5 | ISSUES 2 |
| GenerativeGuardAgent | L5 | ty\guardrails\GenerativeGuardAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 19.5 | ISSUES 2 |
| GitHygieneAgent | L5 | _safety\guardrails\GitHygieneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 26.5 | ISSUES 3 |
| GitSafetyHandlerAgent | L5 | y\guardrails\GitSafetyHandlerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 26.5 | ISSUES 2 |
| PIISanitizerAgent | L5 | afety\guardrails\PIISanitizerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 13.0 | ISSUES 2 |
| RedSentinelAgent | L5 | safety\guardrails\RedSentinelAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 37.0 | ISSUES 2 |
| SafetyInspectorAgent | L5 | ty\guardrails\SafetyInspectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 31.0 | ISSUES 3 |
| SelfUpdatingSafetyEngineAgent | L5 | ails\SelfUpdatingSafetyEngineAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 47.5 | ISSUES 2 |
| UnusedCleanupAgent | L5 | fety\guardrails\UnusedCleanupAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 10.5 | ISSUES 2 |
| CodeDetectorAgent | L5 | ty\policy_engine\CodeDetectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 27.5 | ISSUES 2 |
| CodeEnforcerAgent | L5 | ty\policy_engine\CodeEnforcerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 53.5 | ISSUES 2 |
| CodeHealerAgent | L5 | fety\policy_engine\CodeHealerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 50.5 | ISSUES 2 |
| CodeValidatorAgent | L5 | y\policy_engine\CodeValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 52.5 | ISSUES 2 |
| ComplexityAnalyzerAgent | L5 | icy_engine\ComplexityAnalyzerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 15.5 | ISSUES 2 |
| ResourceManagerAgent | L5 | policy_engine\ResourceManagerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 31.0 | ISSUES 2 |
| SafetyDetectorAgent | L5 | \policy_engine\SafetyDetectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 26.0 | ISSUES 2 |
| SafetyExecutorAgent | L5 | \policy_engine\SafetyExecutorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 36.0 | ISSUES 2 |
| SecurityManagerAgent | L5 | policy_engine\SecurityManagerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 35.0 | ISSUES 2 |
| SSOTFolderCleanupAgent | L5 | licy_engine\SSOTFolderCleanupAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 59.0 | ISSUES 2 |
| StructuralValidatorAgent | L5 | cy_engine\StructuralValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 32.0 | ISSUES 2 |
| StructureEnforcerAgent | L5 | licy_engine\StructureEnforcerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 45.5 | ISSUES 2 |
| StructureHealerAgent | L5 | policy_engine\StructureHealerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 32.5 | ISSUES 2 |
| AdversarialProbeAgent | L5 | \red_teaming\AdversarialProbeAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 26.0 | ISSUES 2 |
| BoundaryTestingAgent | L5 | y\red_teaming\BoundaryTestingAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 28.5 | ISSUES 2 |
| ChaosEngineeringAgent | L5 | \red_teaming\ChaosEngineeringAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 22.0 | ISSUES 2 |
| RedTeamAgent | L5 | L5_safety\red_teaming\RedTeamAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 18.5 | ISSUES 3 |
| ArchitectureGovernorAgent | L5 | lidators\ArchitectureGovernorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 170.0 | ISSUES 2 |
| AutonomyGuardianAgent | L5 | y\validators\AutonomyGuardianAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 67.5 | ISSUES 2 |
| CanonBaseAgent | L5 | 5_safety\validators\CanonBaseAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 1.0 | ISSUES 3 |
| CanonDependencySentinelAgent | L5 | ators\CanonDependencySentinelAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 18.5 | ISSUES 2 |
| CartographerAgent | L5 | afety\validators\CartographerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 11.5 | ISSUES 2 |
| CodeDeduplicationAgent | L5 | \validators\CodeDeduplicationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 121.5 | ISSUES 3 |
| CognitiveDispositionAgent | L5 | lidators\CognitiveDispositionAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 18.0 | ISSUES 2 |
| CompositeGuardrailAgent | L5 | validators\CompositeGuardrailAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 16.0 | ISSUES 2 |
| ContextCuratorAgent | L5 | ety\validators\ContextCuratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 49.5 | ISSUES 2 |
| CredentialScannerAgent | L5 | \validators\CredentialScannerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 28.0 | ISSUES 3 |
| DDDAlignmentAgent | L5 | afety\validators\DDDAlignmentAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 35.0 | ISSUES 2 |
| DependencyDiplomatAgent | L5 | validators\DependencyDiplomatAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 1.0 | ISSUES 2 |
| DocumentationAgent | L5 | fety\validators\DocumentationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 11.5 | ISSUES 2 |
| DynamicSealAgent | L5 | safety\validators\DynamicSealAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 31.0 | ISSUES 2 |
| FilesystemSSOTReconcilerAgent | L5 | tors\FilesystemSSOTReconcilerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 141.5 | ISSUES 2 |
| GitAgent | L5 | a_c\L5_safety\validators\GitAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 61.5 | ISSUES 2 |
| GlobalComplianceAggregatorAgent | L5 | rs\GlobalComplianceAggregatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 5.5 | ISSUES 2 |
| GospelSyncAgent | L5 | _safety\validators\GospelSyncAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 15.0 | ISSUES 2 |
| GovernanceAgent | L5 | _safety\validators\GovernanceAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 101.5 | ISSUES 3 |
| HealValidatorAgent | L5 | fety\validators\HealValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 30.5 | ISSUES 2 |
| HierarchyAgent | L5 | 5_safety\validators\HierarchyAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 181.0 | ISSUES 2 |
| HygieneGuardianAgent | L5 | ty\validators\HygieneGuardianAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 57.5 | ISSUES 2 |
| InterfaceBoundaryAgent | L5 | \validators\InterfaceBoundaryAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Abstract | 16.0 | ISSUES 2 |
| L5SafetyExerciserAgent | L5 | \validators\L5SafetyExerciserAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 22.0 | ISSUES 2 |
| LicS2SupervisorAgent | L5 | ty\validators\LicS2SupervisorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 33.5 | ISSUES 3 |
| LocationAgent | L5 | L5_safety\validators\LocationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 214.5 | ISSUES 3 |
| LocationHealerAgent | L5 | ety\validators\LocationHealerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 136.0 | ISSUES 3 |
| LocationValidatorAgent | L5 | \validators\LocationValidatorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Stub | 112.5 | ISSUES 3 |
| MCPGuardianAgent | L5 | safety\validators\MCPGuardianAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 29.0 | ISSUES 2 |
| MemoryArchitectAgent | L5 | ty\validators\MemoryArchitectAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 64.5 | ISSUES 2 |
| MetricsWitnessAgent | L5 | ety\validators\MetricsWitnessAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 21.5 | ISSUES 2 |
| NamingAgent | L5 | a_c\L5_safety\validators\NamingAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 19.5 | ISSUES 2 |
| NeuralAutoImmuneAgent | L5 | y\validators\NeuralAutoImmuneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| OmniContextAgent | L5 | safety\validators\OmniContextAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| PascalSovereigntyAgent | L5 | \validators\PascalSovereigntyAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 76.0 | ISSUES 2 |
| PineconeSovereignAgent | L5 | \validators\PineconeSovereignAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 58.0 | ISSUES 2 |
| PolicyNeuralAutoImmuneAgent | L5 | dators\PolicyNeuralAutoImmuneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 6.0 | ISSUES 2 |
| PreCommitSovereignAgent | L5 | validators\PreCommitSovereignAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 46.0 | ISSUES 2 |
| PredictiveCostAuditorAgent | L5 | idators\PredictiveCostAuditorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 53.0 | ISSUES 2 |
| RagHealthCheckAgent | L5 | ety\validators\RagHealthCheckAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 16.0 | ISSUES 2 |
| RedisSovereignAgent | L5 | ety\validators\RedisSovereignAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 24.0 | ISSUES 2 |
| RegressionOracleAgent | L5 | y\validators\RegressionOracleAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 46.5 | ISSUES 2 |
| ReportingAgent | L5 | 5_safety\validators\ReportingAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 23.0 | ISSUES 2 |
| RgReflectionAgent | L5 | afety\validators\RgReflectionAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 46.0 | ISSUES 2 |
| RootHygieneAgent | L5 | safety\validators\RootHygieneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 37.5 | ISSUES 2 |
| SemanticDebuggerAgent | L5 | y\validators\SemanticDebuggerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 11.0 | ISSUES 2 |
| SemanticGatekeeperAgent | L5 | validators\SemanticGatekeeperAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 21.0 | ISSUES 2 |
| SemanticMapperAgent | L5 | ety\validators\SemanticMapperAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 2.0 | ISSUES 2 |
| SemanticTerritoryMapperAgent | L5 | ators\SemanticTerritoryMapperAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 1.0 | ISSUES 2 |
| SherlockAgent | L5 | L5_safety\validators\SherlockAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 15.5 | ISSUES 2 |
| SignatureVerifierAgent | L5 | \validators\SignatureVerifierAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 2 |
| SovereignActionPlaneAgent | L5 | lidators\SovereignActionPlaneAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 43.5 | ISSUES 2 |
| SovereignCanonAuditorAgent | L5 | idators\SovereignCanonAuditorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 20.5 | ISSUES 2 |
| SovereignPineconeStoreAgent | L5 | dators\SovereignPineconeStoreAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 31.0 | ISSUES 2 |
| SprawlInspectorAgent | L5 | ty\validators\SprawlInspectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 12.0 | ISSUES 2 |
| StrategistAgent | L5 | _safety\validators\StrategistAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 5.0 | ISSUES 2 |
| StructuralEngineerAgent | L5 | validators\StructuralEngineerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 36.0 | ISSUES 2 |
| SubatomicHopAgent | L5 | afety\validators\SubatomicHopAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 35.5 | ISSUES 2 |
| SystemArchitectAgent | L5 | ty\validators\SystemArchitectAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 61.0 | ISSUES 2 |
| TerritoryChangeHandlerAgent | L5 | dators\TerritoryChangeHandlerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 7.0 | ISSUES 2 |
| TestGeneratorAgent | L5 | fety\validators\TestGeneratorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 46.5 | ISSUES 2 |
| TokenBudgetInspectorAgent | L5 | lidators\TokenBudgetInspectorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 7.5 | ISSUES 2 |
| TypeHintFixerAgent | L5 | fety\validators\TypeHintFixerAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.0 | ISSUES 2 |
| TypeMechanicAgent | L5 | afety\validators\TypeMechanicAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 33.0 | ISSUES 2 |
| BenchmarkingAgent | L6 | L6_observability\BenchmarkingAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 33.0 | ISSUES 2 |
| DocstringComplianceAgent | L6 | rvability\DocstringComplianceAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 19.0 | ISSUES 2 |
| AutonomicMonitorAgent | L6 | ility\agents\AutonomicMonitorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 28.5 | ISSUES 2 |
| CoordinateObservabilityOperationsAgent | L6 | dinateObservabilityOperationsAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 11.0 | ISSUES 2 |
| MetricsAgent | L6 | _observability\agents\MetricsAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 38.0 | ISSUES 2 |
| PerformanceAnalystAgent | L6 | ity\agents\PerformanceAnalystAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 23.0 | ISSUES 2 |
| RuntimeTelemetryAgent | L6 | ility\agents\RuntimeTelemetryAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 13.0 | ISSUES 2 |
| SovereignObservabilityAgent | L6 | agents\SovereignObservabilityAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 28.5 | ISSUES 2 |
| StrategicObservationAgent | L6 | y\agents\StrategicObservationAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 2 |
| DeadlockDetectorAgent | L6 | ervability\agents\TaskMonitorAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 20.0 | ISSUES 2 |
| TelemetryAgent | L6 | bservability\agents\TelemetryAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 30.5 | ISSUES 2 |
| TracingAgent | L6 | _observability\agents\TracingAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 63.0 | ISSUES 2 |
| TrackObservabilityCostAgent | L6 | agents\TrackObservabilityCostAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 2 |
| TestSovereigntyAgent | Unknown | int_sovereign\TestSovereigntyAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 29.0 | ISSUES 2 |
| ConversationalRepairAgent | Unknown | e\agents\ConversationalRepairAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 19.0 | ISSUES 2 |
| PromptRegistryAgent | Unknown | ernance\agents\PromptRegistryAgent.py | [VALID] | [MISSING] - No heal() method | [INVALID] | Concrete | 48.5 | ISSUES 2 |
| SovereignBaseAgent | Base | a_c\base_agents\SovereignBaseAgent.py | [BROKEN] - Missing proper base agent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 25.0 | ISSUES 3 |
| CanonBaseAgent | L2 | ution\tool_registry\CanonBaseAgent.py | [BROKEN] - Missing proper base agent inheritance | [MISSING] - No heal() method | [INVALID] | Stub | 47.0 | ISSUES 4 |
| IOrchestratorAgent | L3 | tion\interfaces\IOrchestratorAgent.py | [BROKEN] - Missing proper base agent inheritance | [MISSING] - No heal() method | [INVALID] | Stub | 1.0 | ISSUES 5 |
| ITieredAgent | L5 | fety\validators\IOrchestratorAgent.py | [BROKEN] - Missing proper base agent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 4.5 | ISSUES 3 |
| DuplicatePromptErrorAgent | Unknown | ernance\agents\PromptRegistryAgent.py | [BROKEN] - Missing proper base agent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 8.5 | ISSUES 3 |

## Critical Issues Requiring Immediate Attention

### CRITICAL: BootstrapAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\BootstrapAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: L0MaintenanceBaseAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\L0MaintenanceBaseAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: CompliantAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\lifecycle_audit.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: ZombieAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\lifecycle_audit.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: NoKwargsAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\lifecycle_audit.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: ASTValidatorAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\ASTValidatorAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: AutonomousPromptEvolutionAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\AutonomousPromptEvolutionAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: BudgetAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\BudgetAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: LLMPromptGovernorAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\LLMPromptGovernorAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: MetaLearningAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: SovereignCognitivePlaneAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\SovereignCognitivePlaneAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: StrategicRecommendationAgent (L1)
**File:** `agentic_core\L1_cognition\thought_engine\StrategicRecommendationAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: EmbeddingSovereignAgent (L2)
**File:** `agentic_core\L2_execution\mcp\EmbeddingSovereignAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: HistorianAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\HistorianAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: IntegrityGateExecutorAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\IntegrityGateExecutorAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location, Agent is incomplete stub
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Complete agent implementation or mark as abstract

### CRITICAL: PeerIntelligenceAuditorAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\PeerIntelligenceAuditorAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: RgStrategicPlannerAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\RgStrategicPlannerAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: SubAtomicRegistryAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\SubAtomicRegistryAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: ToolsmithAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\ToolsmithAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location, Agent is incomplete stub
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Complete agent implementation or mark as abstract

### CRITICAL: DomainPlannerAgent (L3)
**File:** `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
**Issues:** Missing heal() method, Invalid namespace/location
**Recommendations:** Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

*... and 139 more critical agents*
