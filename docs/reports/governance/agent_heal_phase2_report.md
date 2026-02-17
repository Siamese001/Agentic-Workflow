# Agent Healing Audit Report

## Runtime Agents Summary

- **Runtime Agents**: 114
- **Missing heal()**: 0
- **Missing heal_repository()**: 0
- **Missing Both**: 0

## Runtime Agents Detailed Results

| Path | Class | heal | heal_repository | Reason |
|------|-------|------|-----------------|--------|
| agentic_core/L0_routing/reasoning/RootCustomsAgent.py | RootCustomsAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py | SSOTFolderCleanupAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py | ASTValidatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L1_cognition/reasoning/MetaLearningAgent.py | MetaLearningAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py | StrategicRecommendationAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py | EmbeddingSovereignAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L2_execution/reasoning/StructuredEngineAgent.py | StructuredEngineAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py | SubAtomicRegistryAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L2_execution/reasoning/ToolsmithAgent.py | ToolsmithAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/CoverageAgent.py | CoverageAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py | DAGMutatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DagEngineAgent.py | DagEngineAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | DomainPlannerAgent | ✓ | ✓ | inherits from L3OrchestrationBase |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | FeasibilityAnalystAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | RiskAssessorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | StrategyCoordinatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py | StrategyScenarioSimulatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py | NervousSystemAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py | OrchestrationHandshakeAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py | SemanticGatekeeperAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/StateManagementAgent.py | StateManagementAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py | SubAtomicAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py | SubatomicHopAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L3_orchestration/reasoning/UnifiedAgent.py | UnifiedAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L4_state/reasoning/CachedStateLedgerAgent.py | CachedStateLedgerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L4_state/reasoning/CheckpointManagerAgent.py | CheckpointManagerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L4_state/reasoning/GravityStateAgent.py | GravityStateAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L4_state/reasoning/PineconeSovereignAgent.py | PineconeSovereignAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L4_state/reasoning/RedisSovereignAgent.py | RedisSovereignAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py | AdversarialProbeAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py | AdversarialRedTeamerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | ArchitectureGovernorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py | AutonomousThreatEvolutionAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py | AutonomyGuardianAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/BenchmarkingAgent.py | BenchmarkingAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/BootstrapAgent.py | BootstrapAgent | ✓ | ✓ | inherits from L0RoutingBase |
| agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py | BoundaryTestingAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py | ChaosEngineeringAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py | CodeDeduplicationAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeDetectorAgent.py | CodeDetectorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py | CodeEnforcerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeFormatterAgent.py | CodeFormatterAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeHealerAgent.py | CodeHealerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CodeValidatorAgent.py | CodeValidatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py | CognitiveDispositionAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py | ComplexityAnalyzerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py | ConstitutionalReviewerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CostGovernorAgent.py | CostGovernorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/CredentialScannerAgent.py | CredentialScannerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py | DDDAlignmentAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/DependencyPruningAgent.py | DependencyPruningAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py | DocstringComplianceAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/DocumentationAgent.py | DocumentationAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py | DuplicateCodeDetectorAgent | ✓ | ✓ | in runtime folder reasoning |
| agentic_core/L5_safety/reasoning/DynamicSealAgent.py | DynamicSealAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | FileClassificationAgent | ✓ | ✓ | in runtime folder reasoning |
| agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py | FilesystemSSOTReconcilerAgent | ✓ | ✓ | in runtime folder reasoning |
| agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py | GenerativeGuardAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/GitHygieneAgent.py | GitHygieneAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/GospelSyncAgent.py | GospelSyncAgent | ✓ | ✓ | inherits from L0RoutingBase |
| agentic_core/L5_safety/reasoning/GovernanceAgent.py | GovernanceAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py | GravityLeakRepairAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/HierarchyAgent.py | HierarchyAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py | HygieneGuardianAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py | IntegrityGateExecutorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py | InterfaceBoundaryAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py | L5SafetyExerciserAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/LocationAgent.py | LocationAgent | ✓ | ✓ | in runtime folder reasoning |
| agentic_core/L5_safety/reasoning/LocationHealerAgent.py | LocationHealerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/NamingAgent.py | NamingAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py | NeuralAutoImmuneAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py | PolicyNeuralAutoImmuneAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py | PreCommitSovereignAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py | PredictiveCostAuditorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/RedSentinelAgent.py | RedSentinelAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/RedTeamAgent.py | RedTeamAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/RegressionOracleAgent.py | RegressionOracleAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/ReportLocationAgent.py | ReportLocationAgent | ✓ | ✓ | in runtime folder reasoning |
| agentic_core/L5_safety/reasoning/ResourceManagerAgent.py | ResourceManagerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/RootHygieneAgent.py | RootHygieneAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py | SafetyDetectorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py | SafetyExecutorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py | SafetyInspectorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SecurityManagerAgent.py | SecurityManagerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py | SelfUpdatingSafetyEngineAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py | SovereignActionPlaneAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py | SprawlInspectorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py | StructuralEngineerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py | StructuralValidatorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py | StructureEnforcerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/StructureHealerAgent.py | StructureHealerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/SystemArchitectAgent.py | SystemArchitectAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py | TerritoryChangeHandlerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/TestGeneratorAgent.py | TestGeneratorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py | TypeHintFixerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/TypeMechanicAgent.py | TypeMechanicAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py | UnusedCleanupAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/enforcement/ExecutiveStrategyAgent.py | ExecutiveStrategyAgent | ✓ | ✓ | in runtime folder enforcement |
| apps_lic/reasoning/DispatchOutreachToolsAgent.py | DispatchOutreachToolsAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/GovernanceShieldAgent.py | GovernanceShieldAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_lic/reasoning/LicReflectionAgent.py | LicReflectionAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/LicTemplateOptimizerAgent.py | LicTemplateOptimizerAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/MessageComplianceAgent.py | MessageComplianceAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/OutreachLearningAgent.py | OutreachLearningAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/OutreachMessageAgent.py | OutreachMessageAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_lic/reasoning/OutreachProactiveAgent.py | OutreachProactiveAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/OutreachSignalRouterAgent.py | OutreachSignalRouterAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/OutreachValidationExecutorAgent.py | OutreachValidationExecutorAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_lic/reasoning/ValidatorAgent.py | ValidatorAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_rg/reasoning/ContentQualityAgent.py | ContentQualityAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_rg/reasoning/DispatchResumeToolsAgent.py | DispatchResumeToolsAgent | ✓ | ✓ | inherits from SovereignBaseAgent |
| apps_rg/reasoning/ProactiveAgent.py | ProactiveAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_rg/reasoning/ResumeAssemblyAgent.py | ResumeAssemblyAgent | ✓ | ✓ | in runtime folder reasoning |
| apps_rg/reasoning/RgReflectionAgent.py | RgReflectionAgent | ✓ | ✓ | in runtime folder reasoning |

## Non-Agents Appendix

*Total non-agent classes with 'Agent' suffix: 20*

| Path | Class | Reason |
|------|-------|--------|
| agentic_core/L3_orchestration/types/orchestrator_types.py | IOrchestratorAgent | protocol/interface/model/type |
| agentic_core/base_agents/SovereignBaseAgent.py | SovereignBaseAgent | protocol/interface/model/type |
| agentic_core/interfaces/IOrchestratorProtocol.py | ITieredAgent | protocol/interface/model/type |
| apps_lic/config/placeholder_detector_agent_config.py | PlaceholderDetectorAgent | protocol/interface/model/type |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | GateDecisionAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | GenerationAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ProfileAnalysisAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | QAReportAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ResearchAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | RoutingAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | SenderGroundingAgent | Pydantic model |
| apps_lic/reasoning/ArchetypeIndicatorsAgent.py | ValidationAgent | Pydantic model |
| apps_lic/types/app_content_validator_agent_types.py | AppContentValidatorAgent | protocol/interface/model/type |
| apps_lic/types/competitor_recon_agent_types.py | CompetitorReconAgent | protocol/interface/model/type |
| apps_lic/types/stack_modernization_agent_types.py | StackModernizationAgent | protocol/interface/model/type |
| apps_lic/utils/PIISanitizerSpecialistAgent_util.py | ConstitutionalReviewerAgent | protocol/interface/model/type |
| apps_lic/utils/PIISanitizerSpecialistAgent_util.py | PII_SanitizerSpecialistAgent | protocol/interface/model/type |
| apps_rg/types/gap_closure_architect_agent_types.py | GapClosureArchitectAgent | protocol/interface/model/type |
| apps_shared/utils/agent_interface_util.py | BaseAgent | protocol/interface/model/type |
| apps_shared/utils/agent_interface_util.py | IAgent | protocol/interface/model/type |

## Policy Routing Coverage

All runtime agents route through `standard_heal` decorator which invokes `decide_heal_escalation()`.

| Category | Count | Routed Through Policy |
|----------|-------|----------------------|
| Runtime Agents | 114 | ✓ (via standard_heal) |
| Non-Agent Classes | 20 | N/A |

## LLM Escalation Simulation

Fixed input scenarios with deterministic tier decisions (no network calls):

| Scenario | Confidence | LLM Enabled | Complexity | Failures | Proceed | Tier | Threshold |
|----------|------------|-------------|------------|----------|---------|------|-----------|
| high_conf_llm_off | 0.85 | False | 5 | 0 | True | NONE | HIGH_CONF_AUTO |
| high_conf_llm_on | 0.85 | True | 5 | 0 | True | NONE | HIGH_CONF_AUTO |
| med_conf_llm_off | 0.6 | False | 5 | 0 | False | NONE | MEDIUM_CONF_LLM_DISABLED |
| med_conf_llm_on | 0.6 | True | 5 | 0 | True | LOW | MEDIUM_CONF_LLM_LOW |
| med_conf_low_complex | 0.6 | True | 3 | 0 | False | NONE | MEDIUM_CONF_JUDICIOUS_BLOCK |
| low_conf_llm_off | 0.3 | False | 8 | 0 | False | NONE | LOW_CONF_LLM_DISABLED |
| low_conf_high_complex | 0.3 | True | 8 | 0 | True | HIGH | LOW_CONF_LLM_HIGH |
| low_conf_with_failures | 0.3 | True | 3 | 2 | True | HIGH | LOW_CONF_LLM_HIGH |
