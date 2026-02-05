# Nuclear Audit Results: agentic_core/ Agent Technical Status

Generated comprehensive analysis of all agents in agentic_core/ directory.

## Summary Statistics

- **Total Agents**: 214
- **Ready**: 93
- **Broken Import**: 15
- **Signature Mismatch**: 72
- **Stub**: 34

## Detailed Technical Status Table

| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |
|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|
| **DiscoveredAgent** |  | [MISSING] | Not found |  | agentic_core [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **RootCustomsAgent** |  | [MISSING] | Not found |  | agentic_core\L0_maintenance\logs [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BootstrapAgent** | L0MaintenanceBaseAgent | [MISSING] | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core\L0_maintenance\scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **RootCustomsAgent** |  | [MISSING] | Not found |  | agentic_core\L0_maintenance\scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BaseAgent** |  | [MISSING] | Not found |  | agentic_core\L2_execution\tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **SubAtomicAgent** |  | [MISSING] | Not found |  | agentic_core\L2_execution\tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **IOrchestratorAgent** | Protocol | [MISSING] | Not found |  | agentic_core\L3_orchestration\interfaces [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BaseAgent** |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **FilesystemSSOTReconcilerAgent** | AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **GospelSyncAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **ITieredAgent** | Protocol | [MISSING] | Not found |  | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **MetricsWitnessAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L6_observability.metrics.MetricsAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **MockSovereignAgent** |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **SovereignBaseAgent** | infrastructure_mixin, SubatomicTestingMixin, ConfigMixin, LLMProviderMixin, EmbeddingMixin, HealingStrategyMixin, ValidatorMixin, AuditTrailMixin | [OK] SubatomicTesting, [OK] HealingStrategy | heal(self, violation) |  | agentic_core\base_agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BiasAuditorAgent** |  | [MISSING] | Not found | agentic_core.L5_safety.policy_engine.SafetyDetectorAgent | agentic_core\runtime\shared_runtime [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **L0MaintenanceBaseAgent** | L0DelegationTestingMixin, SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L0_maintenance\scripts [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **ASTValidatorAgent** | SovereignBaseAgent, CanonASTValidator | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **AutonomousPromptEvolutionAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L1_cognition.learning.MetaLearningAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **BudgetAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **LLMPromptGovernorAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **MetaLearningAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignCognitivePlaneAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StrategicRecommendationAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **EmbeddingSovereignAgent** | SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **CanonBaseAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent, archives.void_violations.BudgetAgent, archives.void_violations.DocumentationAgent (+2) | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **HistorianAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GitAgent | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **IntegrityGateExecutorAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **PeerIntelligenceAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.IntegrityGateExecutorAgent | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RgStrategicPlannerAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SubAtomicRegistryAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L4_state.validation_context.PineconeSovereignAgent, agentic_core.L4_state.validation_context.RedisSovereignAgent (+18) | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **ToolsmithAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **OrchestratorAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.CanonDependencySentinelAgent, agentic_core.L5_safety.validators.CredentialScannerAgent | agentic_core\L3_orchestration [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SubAtomicAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\fission_logic [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **CoverageAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **DAGMutatorAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **DagEngineAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **DagRuntimeInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **DecompositionOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found |  | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **DomainPlannerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **FeasibilityAnalystAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **FissionManagerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **NervousSystemAgent** | SovereignBaseAgent, MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GovernanceAgent, agentic_core.L5_safety.validators.LocationAgent (+3) | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **OrchestrationHandshakeAgent** | SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.unified.CoreOrchestrationAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RiskAssessorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignRagOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent, IRagProvider | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignRedisOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StrategyCoordinatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StrategyScenarioSimulatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **CanonBaseAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **CanonDependencySentinelAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **CompositeGuardrailAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **ContextCuratorAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **GovernanceAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **InterfaceBoundaryAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **L5SafetyExerciserAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.NamingAgent (+3) | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **LicS2SupervisorAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **MemoryArchitectAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **NeuralAutoImmuneAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **OmniContextAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **PolicyNeuralAutoImmuneAgent** | SubatomicTestingMixin, SovereignBaseAgent, NeuralAutoImmuneAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.NeuralAutoImmuneAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **PreCommitSovereignAgent** | SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **PredictiveCostAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RagHealthCheckAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RedisSovereignAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RegressionOracleAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **ReportingAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.L6_observability.metrics.MetricsAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **RgReflectionAgent** | SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SemanticDebuggerAgent** | SubatomicTestingMixin, SovereignBaseAgent, CognitiveRecoveryMixin | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SemanticGatekeeperAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SemanticMapperAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SemanticTerritoryMapperAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SherlockAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.ToolsmithAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SignatureVerifierAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignActionPlaneAgent** | SovereignBaseAgent, IActionPlane | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignCanonAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SovereignPineconeStoreAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SprawlInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StrategistAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StructuralEngineerAgent** | SubatomicTestingMixin, SovereignBaseAgent, CanonBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.CanonBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SubatomicHopAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TerritoryChangeHandlerAgent** | SubatomicTestingMixin, SovereignBaseAgent, FileSystemEventHandler | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TestGeneratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TokenBudgetInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TypeHintFixerAgent** | SubatomicTestingMixin, SovereignBaseAgent, ast.NodeTransformer | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TypeMechanicAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **AutonomyMixin** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **AutonomyMixin** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| L0DelegationTestingMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L0_maintenance\scripts [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| EmbeddingMixin |  | [MISSING] | Not found | agentic_core.L2_execution.mcp.EmbeddingSovereignAgent | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedisCacheMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| TestCoverageGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| GravityLeakRepairAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.StructuralValidatorAgent | agentic_core\L5_safety\gravity [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ConstitutionalReviewerAgent | SovereignBaseAgent, L5SafetyBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| GitHygieneAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PIISanitizerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedSentinelAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains pass-only methods |
| SafetyInspectorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StructuralValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ArchitectureGovernorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent, agentic_core.L5_safety.validators.PascalSovereigntyAgent (+6) | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| AutonomyGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CodeDeduplicationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.NamingAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationHealerAgent, agentic_core.L5_safety.validators.NamingAgent (+19) | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationValidatorAgent | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| NamingAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DocstringComplianceAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PerformanceAnalystAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | AgentPerformanceMetrics | agentic_core\L6_observability\agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| TracingAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, opentelemetry.sdk.resources, opentelemetry.sdk.trace (+1) | agentic_core\L6_observability\agents [INVALID] | [INFO] Stub | Contains pass-only methods |
| HealerMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| L2SelfTestingMixin | SubatomicTestingMixin, MCPHardenedMixin | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PineconeVectorMixin | RedisCacheMixin | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedisCacheMixin |  | [MISSING] | Not found | agentic_core.L5_safety.validators.RedisSovereignAgent | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin | instructional_injection_mixin | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LLMProviderMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| MCPOperationMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| CheckpointManagerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| ContextPropagationMixin |  | [MISSING] | Not found |  | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| GravityStateAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| StateManagementAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| StateValidationMixin |  | [MISSING] | Not found |  | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| StateValidatorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| UiValidationAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [OK] Ready |  |
| ASTEnforcementMixin |  | [MISSING] | Not found |  | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| AdversarialRedTeamerAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| AutonomousThreatEvolutionAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| CodeFormatterAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| CostGovernorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| DependencyPruningAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| GenerativeGuardAgent | SovereignBaseAgent, SubatomicTestingMixin, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| GitSafetyHandlerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| SelfUpdatingSafetyEngineAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| UnusedCleanupAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [OK] Ready |  |
| CodeDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| CodeEnforcerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| CodeHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| CodeValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| ComplexityAnalyzerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| ResourceManagerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| SSOTFolderCleanupAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.cognition.CognitiveDispositionAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| SafetyDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| SafetyExecutorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| SecurityManagerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| StructureEnforcerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| StructureHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [OK] Ready |  |
| AdversarialProbeAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\red_teaming [INVALID] | [OK] Ready |  |
| BoundaryTestingAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\red_teaming [INVALID] | [OK] Ready |  |
| ChaosEngineeringAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\red_teaming [INVALID] | [OK] Ready |  |
| RedTeamAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\red_teaming [INVALID] | [OK] Ready |  |
| AdaptiveExecutionMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| AutonomyMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| CartographerAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| CognitiveDispositionAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| CredentialScannerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DDDAlignmentAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DependencyDiplomatAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DocumentationAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DynamicSealAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| GitAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| GlobalComplianceAggregatorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealerMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealingStrategyMixin |  | [OK] HealingStrategy | Not found |  | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HierarchyAgent | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HygieneGuardianAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PascalSovereigntyAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PineconeSovereignAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PromptRegistryAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RootHygieneAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SelfDiagnosisMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SystemArchitectAgent | SovereignBaseAgent, CanonBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.CanonBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| TestSovereigntyAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.ExecutionCanonBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| ValidatorMixin |  | [MISSING] | Not found |  | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| BenchmarkingAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [OK] Ready |  |
| ConversationalRepairAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [OK] Ready |  |
| AutonomicMonitorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| CoordinateObservabilityOperationsAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| DeadlockDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| MetricsAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| RuntimeTelemetryAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| SovereignObservabilityAgent | SovereignBaseAgent, SubatomicTestingMixin, MCPHardenedMixin, RedisCacheMixin, event_emission_mixin, ContextPropagationMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| StrategicObservationAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| TelemetryAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| TrackObservabilityCostAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| AuditTrailMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| CapabilityDiscoveryMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| CognitiveRecoveryMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HardeningMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HealerAgentMixin |  | [MISSING] | heal(self, violation) |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HygieneMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| LifecycleMixin | ABC | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| MetaLearningMixin | BaseMetaLearner | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| MigrationMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| RateLimitMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| SecretsManagementMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| StructuralHealingMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| TracingMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| ConfigMixin |  | [MISSING] | Not found |  | agentic_core\config [INVALID] | [OK] Ready |  |
| AdaptiveExecutionMixin |  | [MISSING] | Not found |  | agentic_core\patterns\agent_roles [INVALID] | [OK] Ready |  |
| SelfDiagnosisMixin |  | [MISSING] | Not found |  | agentic_core\patterns\agent_roles [INVALID] | [OK] Ready |  |
| HealerMixin |  | [MISSING] | Not found |  | agentic_core\utils\core_extensions [INVALID] | [OK] Ready |  |

## High-Priority Remediation Targets

The following agents require immediate attention:

### **SovereignBaseAgent** (Broken Import)
- **File**: `agentic_core\base_agents\SovereignBaseAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: infrastructure_mixin, SubatomicTestingMixin, ConfigMixin, LLMProviderMixin, EmbeddingMixin, HealingStrategyMixin, ValidatorMixin, AuditTrailMixin
- **Namespace**: agentic_core\base_agents

### **DiscoveredAgent** (Broken Import)
- **File**: `agentic_core\DiscoveredAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\logs\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L0_maintenance\logs

### **BootstrapAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\BootstrapAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: L0MaintenanceBaseAgent
- **Namespace**: agentic_core\L0_maintenance\scripts

### **L0MaintenanceBaseAgent** (Signature Mismatch)
- **File**: `agentic_core\L0_maintenance\scripts\L0MaintenanceBaseAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: L0DelegationTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L0_maintenance\scripts

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L0_maintenance\scripts

### **ASTValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\ASTValidatorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, CanonASTValidator
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **AutonomousPromptEvolutionAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\AutonomousPromptEvolutionAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **BudgetAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\BudgetAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **LLMPromptGovernorAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\LLMPromptGovernorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **MetaLearningAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **SovereignCognitivePlaneAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\SovereignCognitivePlaneAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **StrategicRecommendationAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\StrategicRecommendationAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L1_cognition\thought_engine

### **EmbeddingSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\mcp\EmbeddingSovereignAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\mcp

### **SubAtomicAgent** (Broken Import)
- **File**: `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L2_execution\tool_registry

### **BaseAgent** (Broken Import)
- **File**: `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L2_execution\tool_registry

### **CanonBaseAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\CanonBaseAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **HistorianAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\HistorianAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **IntegrityGateExecutorAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\IntegrityGateExecutorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **PeerIntelligenceAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\PeerIntelligenceAuditorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **RgStrategicPlannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\RgStrategicPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **SubAtomicRegistryAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\SubAtomicRegistryAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **ToolsmithAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\ToolsmithAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L2_execution\tool_registry

### **SubAtomicAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\fission_logic\SubAtomicAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\fission_logic

### **IOrchestratorAgent** (Broken Import)
- **File**: `agentic_core\L3_orchestration\interfaces\IOrchestratorAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: Protocol
- **Namespace**: agentic_core\L3_orchestration\interfaces

### **OrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\OrchestratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration

### **CoverageAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\CoverageAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **DagEngineAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DagEngineAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **DAGMutatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DAGMutatorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **DagRuntimeInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DagRuntimeInspectorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **DecompositionOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DecompositionOrchestratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **BaseAgent** (Broken Import)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **DomainPlannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **RiskAssessorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **FeasibilityAnalystAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **StrategyScenarioSimulatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **StrategyCoordinatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **FissionManagerAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\FissionManagerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **NervousSystemAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **OrchestrationHandshakeAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\OrchestrationHandshakeAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **SovereignRagOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\SovereignRagOrchestratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, IRagProvider
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **SovereignRedisOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\SovereignRedisOrchestratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

### **CanonBaseAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CanonBaseAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **CanonDependencySentinelAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CanonDependencySentinelAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **CompositeGuardrailAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CompositeGuardrailAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **ContextCuratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ContextCuratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **FilesystemSSOTReconcilerAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **GospelSyncAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\GospelSyncAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **GovernanceAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\GovernanceAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **InterfaceBoundaryAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\InterfaceBoundaryAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **ITieredAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\IOrchestratorAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: Protocol
- **Namespace**: agentic_core\L5_safety\validators

### **L5SafetyExerciserAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\L5SafetyExerciserAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **LicS2SupervisorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\LicS2SupervisorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **MemoryArchitectAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\MemoryArchitectAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **MetricsWitnessAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\MetricsWitnessAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin
- **Namespace**: agentic_core\L5_safety\validators

### **NeuralAutoImmuneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\NeuralAutoImmuneAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **OmniContextAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\OmniContextAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **PolicyNeuralAutoImmuneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PolicyNeuralAutoImmuneAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, NeuralAutoImmuneAgent
- **Namespace**: agentic_core\L5_safety\validators

### **PreCommitSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PreCommitSovereignAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **PredictiveCostAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PredictiveCostAuditorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **RagHealthCheckAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RagHealthCheckAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **RedisSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RedisSovereignAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **RegressionOracleAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RegressionOracleAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **ReportingAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ReportingAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **RgReflectionAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RgReflectionAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SemanticDebuggerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticDebuggerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, CognitiveRecoveryMixin
- **Namespace**: agentic_core\L5_safety\validators

### **SemanticGatekeeperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticGatekeeperAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SemanticMapperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticMapperAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SemanticTerritoryMapperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticTerritoryMapperAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SherlockAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SherlockAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SignatureVerifierAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SignatureVerifierAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SovereignActionPlaneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignActionPlaneAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, IActionPlane
- **Namespace**: agentic_core\L5_safety\validators

### **SovereignCanonAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignCanonAuditorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SovereignPineconeStoreAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignPineconeStoreAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SprawlInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SprawlInspectorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **StrategistAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\StrategistAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **StructuralEngineerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\StructuralEngineerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, CanonBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **SubatomicHopAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SubatomicHopAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **TerritoryChangeHandlerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TerritoryChangeHandlerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, FileSystemEventHandler
- **Namespace**: agentic_core\L5_safety\validators

### **TestGeneratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TestGeneratorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **TokenBudgetInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TokenBudgetInspectorAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core\L5_safety\validators

### **TypeHintFixerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TypeHintFixerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, ast.NodeTransformer
- **Namespace**: agentic_core\L5_safety\validators

### **TypeMechanicAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TypeMechanicAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core\L5_safety\validators

### **MockSovereignAgent** (Broken Import)
- **File**: `agentic_core\L6_observability\agents\RuntimeTelemetryAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\L6_observability\agents

### **AutonomyMixin** (Signature Mismatch)
- **File**: `agentic_core\patterns\agent_roles\autonomy_mixin.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\patterns\agent_roles

### **AutonomyMixin** (Signature Mismatch)
- **File**: `agentic_core\patterns\agent_roles\AutonomyMixinAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core\patterns\agent_roles

### **BiasAuditorAgent** (Broken Import)
- **File**: `agentic_core\runtime\shared_runtime\BiasTypeAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**:
- **Namespace**: agentic_core\runtime\shared_runtime
