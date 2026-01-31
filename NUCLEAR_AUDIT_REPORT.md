# Nuclear Audit Results: agentic_core/ Agent Technical Status

Generated comprehensive analysis of all agents in agentic_core/ directory.

## Summary Statistics

- **Total Agents**: 213
- **Ready**: 135
- **Broken Import**: 15
- **Signature Mismatch**: 10
- **Stub**: 53

## Detailed Technical Status Table

| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |
|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|
| **DiscoveredAgent** |  | [MISSING] | Not found |  | agentic_core [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core\L0_maintenance\logs [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BootstrapAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core\L0_maintenance\scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core\L0_maintenance\scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BaseAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core\L2_execution\tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **SubAtomicAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core\L2_execution\tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **IOrchestratorAgent** | Protocol | [MISSING] | Not found |  | agentic_core\L3_orchestration\interfaces [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BaseAgent** |  | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **FilesystemSSOTReconcilerAgent** | AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **GospelSyncAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **ITieredAgent** | Protocol | [MISSING] | Not found |  | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **MetricsWitnessAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L6_observability.metrics.MetricsAgent | agentic_core\L5_safety\validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **MockSovereignAgent** |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **SovereignBaseAgent** | infrastructure_mixin, SubatomicTestingMixin, ConfigMixin, LLMProviderMixin, EmbeddingMixin, HealingStrategyMixin, ValidatorMixin, AuditTrailMixin | [OK] SubatomicTesting, [OK] HealingStrategy | heal(self, violation) |  | agentic_core\base_agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **BiasAuditorAgent** |  | [MISSING] | heal(self, violation) | agentic_core.L5_safety.policy_engine.SafetyDetectorAgent | agentic_core\runtime\shared_runtime [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance |
| **SubAtomicAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\fission_logic [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **StructuralEngineerAgent** | SovereignBaseAgent, SubatomicTestingMixin, HealerMixin | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **SubatomicHopAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TerritoryChangeHandlerAgent** | SubatomicTestingMixin, SovereignBaseAgent, FileSystemEventHandler | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TestGeneratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TokenBudgetInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TypeHintFixerAgent** | SubatomicTestingMixin, SovereignBaseAgent, ast.NodeTransformer | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **TypeMechanicAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core\L5_safety\validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **AutonomyMixin** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| **AutonomyMixin** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [WARNING] Signature Mismatch | Missing heal() method |
| EmbeddingMixin |  | [MISSING] | Not found | agentic_core.L2_execution.mcp.EmbeddingSovereignAgent | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| EmbeddingSovereignAgent | SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) |  | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedisCacheMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| HistorianAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GitAgent | agentic_core\L2_execution\tool_registry [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| IntegrityGateExecutorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ToolsmithAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CoverageAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DAGMutatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DomainPlannerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| FeasibilityAnalystAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RiskAssessorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StrategyCoordinatorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StrategyScenarioSimulatorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| TestCoverageGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L4_state\validation_context [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| GravityLeakRepairAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.StructuralValidatorAgent | agentic_core\L5_safety\gravity [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ConstitutionalReviewerAgent | SovereignBaseAgent, L5SafetyBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| GitHygieneAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PIISanitizerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedSentinelAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains pass-only methods |
| SafetyInspectorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\guardrails [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StructuralValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\policy_engine [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ArchitectureGovernorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.L5_safety.validators.PascalSovereigntyAgent, agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent (+6) | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CanonDependencySentinelAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CodeDeduplicationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.NamingAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| FileClassificationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| InterfaceBoundaryAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| L5SafetyExerciserAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.NamingAgent (+3) | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LicS2SupervisorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationHealerAgent, agentic_core.L5_safety.validators.NamingAgent (+19) | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationValidatorAgent | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| NamingAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ReportingAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L6_observability.metrics.MetricsAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SovereignPineconeStoreAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.mcp.SovereignPineconeMcpClientAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core\L5_safety\validators [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DocstringComplianceAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PerformanceAnalystAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | AgentPerformanceMetrics | agentic_core\L6_observability\agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| TracingAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, opentelemetry.sdk.resources, opentelemetry.sdk.trace (+1) | agentic_core\L6_observability\agents [INVALID] | [INFO] Stub | Contains pass-only methods |
| HealerMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| InstructionalInjectionMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| L0DelegationTestingMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| L0MaintenanceBaseAgent | L0DelegationTestingMixin, SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| L2SelfTestingMixin | SubatomicTestingMixin, MCPHardenedMixin | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PineconeVectorMixin | RedisCacheMixin | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RedisCacheMixin |  | [MISSING] | Not found | agentic_core.L5_safety.validators.RedisSovereignAgent | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubatomicTestingMixin | InstructionalInjectionMixin | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| MCPHardenedMixin |  | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\patterns\agent_roles [INVALID] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ASTValidatorAgent | SovereignBaseAgent, CanonASTValidator | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| AutonomousPromptEvolutionAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L1_cognition.learning.MetaLearningAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| BudgetAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| LLMPromptGovernorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| MetaLearningAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| SovereignCognitivePlaneAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| StrategicRecommendationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L1_cognition\thought_engine [INVALID] | [OK] Ready |  |
| LLMProviderMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| MCPOperationMixin |  | [MISSING] | Not found |  | agentic_core\L2_execution\mcp [INVALID] | [OK] Ready |  |
| PeerIntelligenceAuditorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.IntegrityGateExecutorAgent | agentic_core\L2_execution\tool_registry [INVALID] | [OK] Ready |  |
| RgStrategicPlannerAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L2_execution\tool_registry [INVALID] | [OK] Ready |  |
| SubAtomicRegistryAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L4_state.validation_context.PineconeSovereignAgent, agentic_core.L4_state.validation_context.RedisSovereignAgent (+18) | agentic_core\L2_execution\tool_registry [INVALID] | [OK] Ready |  |
| ValidationOrchestratorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, archives.void_violations.BudgetAgent, archives.void_violations.DocumentationAgent (+2) | agentic_core\L2_execution\tool_registry [INVALID] | [OK] Ready |  |
| OrchestratorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.CanonDependencySentinelAgent, agentic_core.L5_safety.validators.CredentialScannerAgent | agentic_core\L3_orchestration [INVALID] | [OK] Ready |  |
| DagEngineAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| DagRuntimeInspectorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| DecompositionOrchestratorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) |  | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| FissionManagerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| NervousSystemAgent | SovereignBaseAgent, MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GovernanceAgent, agentic_core.L5_safety.validators.LocationAgent (+3) | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| OrchestrationHandshakeAgent | SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.unified.CoreOrchestrationAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| SovereignRedisOrchestratorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L3_orchestration\workflow_engines [INVALID] | [OK] Ready |  |
| SemanticCacheMixin |  | [MISSING] | Not found |  | agentic_core\L4_state\memory [INVALID] | [OK] Ready |  |
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
| CompositeGuardrailAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| ContextCuratorAgent | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| CredentialScannerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DDDAlignmentAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DependencyDiplomatAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DocumentationAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| DynamicSealAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| GitAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| GlobalComplianceAggregatorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| GovernanceAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealerMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HealingStrategyMixin |  | [OK] HealingStrategy | Not found |  | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HierarchyAgent | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| HygieneGuardianAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MCPHardenedMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| MemoryArchitectAgent | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| NeuralAutoImmuneAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| OmniContextAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PineconeSovereignAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PolicyNeuralAutoImmuneAgent | SubatomicTestingMixin, SovereignBaseAgent, NeuralAutoImmuneAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.NeuralAutoImmuneAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PreCommitSovereignAgent | SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PredictiveCostAuditorAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| PromptRegistryAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RagHealthCheckAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RedisSovereignAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RegressionOracleAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RgReflectionAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| RootHygieneAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SelfDiagnosisMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SemanticDebuggerAgent | SubatomicTestingMixin, SovereignBaseAgent, CognitiveRecoveryMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SemanticGatekeeperAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SemanticMapperAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SemanticTerritoryMapperAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SherlockAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.ToolsmithAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SignatureVerifierAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SovereignActionPlaneAgent | SovereignBaseAgent, IActionPlane | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SovereignCanonAuditorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| StrategistAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SubatomicTestingMixin |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| SystemArchitectAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| TestSovereigntyAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| ValidatorMixin |  | [MISSING] | Not found |  | agentic_core\L5_safety\validators [INVALID] | [OK] Ready |  |
| BenchmarkingAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [OK] Ready |  |
| DebateSynthesisAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability [INVALID] | [OK] Ready |  |
| AutonomicMonitorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| CoordinateObservabilityOperationsAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| DeadlockDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| MetricsAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| RuntimeTelemetryAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| StrategicObservationAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| TelemetryAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| TrackObservabilityCostAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core\L6_observability\agents [INVALID] | [OK] Ready |  |
| AuditTrailMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| BatchOperationMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| CapabilityDiscoveryMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| CognitiveRecoveryMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HardeningMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HealerAgentMixin |  | [MISSING] | heal(self, violation) |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| HygieneMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| InfrastructureMixin | PineconeVectorMixin, HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, TracingMixin | [OK] SubatomicTesting | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
| InstructionalInjectionMixin |  | [MISSING] | Not found |  | agentic_core\base_agents [INVALID] | [OK] Ready |  |
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
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core\L0_maintenance\scripts

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: 
- **Namespace**: agentic_core\L0_maintenance\scripts

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

### **BaseAgent** (Broken Import)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: 
- **Namespace**: agentic_core\L3_orchestration\workflow_engines

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

### **ITieredAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\IOrchestratorAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: Protocol
- **Namespace**: agentic_core\L5_safety\validators

### **MetricsWitnessAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\MetricsWitnessAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin
- **Namespace**: agentic_core\L5_safety\validators

### **StructuralEngineerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\StructuralEngineerAgent.py`
- **Issues**: Missing heal() method
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin, HealerMixin
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
