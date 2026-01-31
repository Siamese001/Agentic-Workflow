# Nuclear Audit Results: agentic_core/ Agent Technical Status

Generated comprehensive analysis of all agents in agentic_core/ directory.

## Summary Statistics

- **Total Agents**: 160
- **Ready**: 1
- **Broken Import**: 12
- **Signature Mismatch**: 146
- **Stub**: 1

## Detailed Technical Status Table

| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |
|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|
| **DiscoveredAgent** |  | [MISSING] | Not found |  | agentic_core [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core |
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L0_maintenance/logs [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/logs |
| **BootstrapAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core/L0_maintenance/scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts |
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L0_maintenance/scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts |
| **BaseAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L2_execution/tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry |
| **SubAtomicAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L2_execution/tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry |
| **BaseAgent** |  | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FilesystemSSOTReconcilerAgent** | AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core/L5_safety/validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators |
| **GospelSyncAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent | agentic_core/L5_safety/validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators |
| **MetricsWitnessAgent** | SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L6_observability.metrics.MetricsAgent | agentic_core/L5_safety/validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators |
| **MockSovereignAgent** |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L6_observability/agents |
| **BiasAuditorAgent** |  | [MISSING] | heal(self, violation) | agentic_core.L5_safety.policy_engine.SafetyDetectorAgent | agentic_core/runtime/shared_runtime [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/runtime/shared_runtime |
| **ASTValidatorAgent** | SovereignBaseAgent, CanonASTValidator | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **AutonomousPromptEvolutionAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L1_cognition.learning.MetaLearningAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **BudgetAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **LLMPromptGovernorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **MetaLearningAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **SovereignCognitivePlaneAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **StrategicRecommendationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **EmbeddingSovereignAgent** | SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) |  | agentic_core/L2_execution/mcp [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/mcp |
| **HistorianAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GitAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **IntegrityGateExecutorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **PeerIntelligenceAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.IntegrityGateExecutorAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **RgStrategicPlannerAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **SubAtomicRegistryAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L4_state.validation_context.PineconeSovereignAgent, agentic_core.L4_state.validation_context.RedisSovereignAgent (+18) | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **ToolsmithAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **ValidationOrchestratorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, archives.void_violations.BudgetAgent, archives.void_violations.DocumentationAgent (+2) | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **OrchestratorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.CanonDependencySentinelAgent, agentic_core.L5_safety.validators.CredentialScannerAgent | agentic_core/L3_orchestration [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration |
| **SubAtomicAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/fission_logic [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L3_orchestration/fission_logic |
| **CoverageAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DAGMutatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DagEngineAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DagRuntimeInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DecompositionOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) |  | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DomainPlannerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FeasibilityAnalystAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FissionManagerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **NervousSystemAgent** | SovereignBaseAgent, MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GovernanceAgent, agentic_core.L5_safety.validators.LocationAgent (+3) | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **OrchestrationHandshakeAgent** | SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.unified.CoreOrchestrationAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **RiskAssessorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **SovereignRagOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent, IRagProvider | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **SovereignRedisOrchestratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **StrategyCoordinatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **StrategyScenarioSimulatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **CheckpointManagerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **GravityStateAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **StateManagementAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **StateValidatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **TestCoverageGuardianAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **UiValidationAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **GravityLeakRepairAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.StructuralValidatorAgent | agentic_core/L5_safety/gravity [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/gravity |
| **AdversarialRedTeamerAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **AutonomousThreatEvolutionAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **CodeFormatterAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **ConstitutionalReviewerAgent** | SovereignBaseAgent, L5SafetyBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **CostGovernorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **DependencyPruningAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **GenerativeGuardAgent** | SovereignBaseAgent, SubatomicTestingMixin, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **GitHygieneAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **GitSafetyHandlerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **PIISanitizerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **RedSentinelAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **SafetyInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **SelfUpdatingSafetyEngineAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **UnusedCleanupAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **CodeDetectorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **CodeEnforcerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **CodeHealerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **CodeValidatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **ComplexityAnalyzerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **ResourceManagerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **SSOTFolderCleanupAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.cognition.CognitiveDispositionAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **SafetyDetectorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **SafetyExecutorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **SecurityManagerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **StructuralValidatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **StructureEnforcerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **StructureHealerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/policy_engine |
| **AdversarialProbeAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/red_teaming |
| **BoundaryTestingAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/red_teaming |
| **ChaosEngineeringAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/red_teaming |
| **RedTeamAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/red_teaming |
| **ArchitectureGovernorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.L5_safety.validators.PascalSovereigntyAgent, agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent (+6) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **AutonomyGuardianAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CanonDependencySentinelAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CartographerAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CodeDeduplicationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.NamingAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CognitiveDispositionAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CompositeGuardrailAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **ContextCuratorAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CredentialScannerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **DDDAlignmentAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **DependencyDiplomatAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **DocumentationAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **DynamicSealAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **FileClassificationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **GitAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **GlobalComplianceAggregatorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **GovernanceAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **HealValidatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **HierarchyAgent** | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **HygieneGuardianAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **InterfaceBoundaryAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **L5SafetyExerciserAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.NamingAgent (+3) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LicS2SupervisorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LocationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationHealerAgent, agentic_core.L5_safety.validators.NamingAgent (+19) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LocationHealerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LocationValidatorAgent** | SovereignBaseAgent, SubatomicTestingMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **MCPGuardianAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **MemoryArchitectAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **NamingAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **NeuralAutoImmuneAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **OmniContextAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PineconeSovereignAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PolicyNeuralAutoImmuneAgent** | SubatomicTestingMixin, SovereignBaseAgent, NeuralAutoImmuneAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.NeuralAutoImmuneAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PreCommitSovereignAgent** | SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PredictiveCostAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PromptRegistryAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RagHealthCheckAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RedisSovereignAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RegressionOracleAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **ReportingAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L6_observability.metrics.MetricsAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RgReflectionAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RootHygieneAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SemanticDebuggerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SemanticGatekeeperAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SemanticMapperAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SemanticTerritoryMapperAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SherlockAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.tool_registry.ToolsmithAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SignatureVerifierAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SovereignActionPlaneAgent** | SovereignBaseAgent, IActionPlane | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SovereignCanonAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SovereignPineconeStoreAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L2_execution.mcp.SovereignPineconeMcpClientAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SprawlInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **StrategistAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **StructuralEngineerAgent** | SovereignBaseAgent, SubatomicTestingMixin, HealerMixin | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **SubatomicHopAgent** | SovereignBaseAgent | [MISSING] | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **SystemArchitectAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **TerritoryChangeHandlerAgent** | SubatomicTestingMixin, SovereignBaseAgent, FileSystemEventHandler | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **TestGeneratorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **TestSovereigntyAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **TokenBudgetInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **TypeHintFixerAgent** | SubatomicTestingMixin, SovereignBaseAgent, ast.NodeTransformer | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **TypeMechanicAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.fission_logic.SubAtomicAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **BenchmarkingAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **DebateSynthesisAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **DocstringComplianceAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **AutonomicMonitorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **CoordinateObservabilityOperationsAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **DeadlockDetectorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **MetricsAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **PerformanceAnalystAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | AgentPerformanceMetrics | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **RuntimeTelemetryAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **SovereignObservabilityAgent** | SovereignBaseAgent, SubatomicTestingMixin, MCPHardenedMixin, RedisCacheMixin, event_emission_mixin, ContextPropagationMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **StrategicObservationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **TelemetryAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **TracingAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, opentelemetry.sdk.resources, opentelemetry.sdk.trace (+1) | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **TrackObservabilityCostAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| L0MaintenanceBaseAgent | L0DelegationTestingMixin, SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/base_agents [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SovereignBaseAgent |  | [OK] SubatomicTesting, [OK] HealingStrategy | heal(self, violation) |  | agentic_core/base_agents [OK] | [OK] Ready |  |

## High-Priority Remediation Targets

The following agents require immediate attention:

### **DiscoveredAgent** (Broken Import)
- **File**: `agentic_core\DiscoveredAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core
- **Inheritance**: 
- **Namespace**: agentic_core

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\logs\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/logs
- **Inheritance**: 
- **Namespace**: agentic_core/L0_maintenance/logs

### **BootstrapAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\BootstrapAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core/L0_maintenance/scripts

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts
- **Inheritance**: 
- **Namespace**: agentic_core/L0_maintenance/scripts

### **ASTValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\ASTValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent, CanonASTValidator
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **AutonomousPromptEvolutionAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\AutonomousPromptEvolutionAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **BudgetAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\BudgetAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **LLMPromptGovernorAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\LLMPromptGovernorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **MetaLearningAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **SovereignCognitivePlaneAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\SovereignCognitivePlaneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **StrategicRecommendationAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\StrategicRecommendationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

### **EmbeddingSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\mcp\EmbeddingSovereignAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/mcp
- **Inheritance**: SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/mcp

### **SubAtomicAgent** (Broken Import)
- **File**: `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: 
- **Namespace**: agentic_core/L2_execution/tool_registry

### **BaseAgent** (Broken Import)
- **File**: `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: 
- **Namespace**: agentic_core/L2_execution/tool_registry

### **HistorianAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\HistorianAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **IntegrityGateExecutorAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\IntegrityGateExecutorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **PeerIntelligenceAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\PeerIntelligenceAuditorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **RgStrategicPlannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\RgStrategicPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **SubAtomicRegistryAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\SubAtomicRegistryAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **ToolsmithAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\ToolsmithAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **ValidationOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\ValidationOrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L2_execution/tool_registry
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L2_execution/tool_registry

### **SubAtomicAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\fission_logic\SubAtomicAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L3_orchestration/fission_logic
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/fission_logic

### **OrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\OrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration

### **CoverageAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\CoverageAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **DagEngineAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DagEngineAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **DAGMutatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DAGMutatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **DagRuntimeInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DagRuntimeInspectorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **DecompositionOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DecompositionOrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **BaseAgent** (Broken Import)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: 
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **DomainPlannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **RiskAssessorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **FeasibilityAnalystAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **StrategyScenarioSimulatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **StrategyCoordinatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **FissionManagerAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\FissionManagerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **NervousSystemAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SovereignBaseAgent, MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **OrchestrationHandshakeAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\OrchestrationHandshakeAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **SovereignRagOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\SovereignRagOrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, IRagProvider
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **SovereignRedisOrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\SovereignRedisOrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **CheckpointManagerAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\CheckpointManagerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **GravityStateAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\GravityStateAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **StateManagementAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\StateManagementAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **StateValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\StateValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **TestCoverageGuardianAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\TestCoverageGuardianAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **UiValidationAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\UiValidationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L4_state/validation_context
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L4_state/validation_context

### **GravityLeakRepairAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\gravity\GravityLeakRepairAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/gravity
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/gravity

### **AdversarialRedTeamerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\AdversarialRedTeamerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **AutonomousThreatEvolutionAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\AutonomousThreatEvolutionAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **CodeFormatterAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\CodeFormatterAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **ConstitutionalReviewerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\ConstitutionalReviewerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent, L5SafetyBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **CostGovernorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\CostGovernorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **DependencyPruningAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\DependencyPruningAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **GenerativeGuardAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\GenerativeGuardAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin
- **Namespace**: agentic_core/L5_safety/guardrails

### **GitHygieneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\GitHygieneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **GitSafetyHandlerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\GitSafetyHandlerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **PIISanitizerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\PIISanitizerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **RedSentinelAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\RedSentinelAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **SafetyInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\SafetyInspectorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **SelfUpdatingSafetyEngineAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\SelfUpdatingSafetyEngineAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **UnusedCleanupAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\UnusedCleanupAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **CodeDetectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\CodeDetectorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **CodeEnforcerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\CodeEnforcerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **CodeHealerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\CodeHealerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **CodeValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\CodeValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **ComplexityAnalyzerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\ComplexityAnalyzerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **ResourceManagerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\ResourceManagerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **SafetyDetectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\SafetyDetectorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **SafetyExecutorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\SafetyExecutorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **SecurityManagerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\SecurityManagerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **SSOTFolderCleanupAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\SSOTFolderCleanupAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **StructuralValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\StructuralValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **StructureEnforcerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\StructureEnforcerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **StructureHealerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\policy_engine\StructureHealerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/policy_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/policy_engine

### **AdversarialProbeAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\red_teaming\AdversarialProbeAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/red_teaming
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/red_teaming

### **BoundaryTestingAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\red_teaming\BoundaryTestingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/red_teaming
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/red_teaming

### **ChaosEngineeringAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\red_teaming\ChaosEngineeringAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/red_teaming
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/red_teaming

### **RedTeamAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\red_teaming\RedTeamAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/red_teaming
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/red_teaming

### **ArchitectureGovernorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ArchitectureGovernorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **AutonomyGuardianAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\AutonomyGuardianAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CanonDependencySentinelAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CanonDependencySentinelAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CartographerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CartographerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CodeDeduplicationAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CodeDeduplicationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CognitiveDispositionAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CognitiveDispositionAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CompositeGuardrailAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CompositeGuardrailAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **ContextCuratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ContextCuratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CredentialScannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\CredentialScannerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **DDDAlignmentAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\DDDAlignmentAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **DependencyDiplomatAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\DependencyDiplomatAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **DocumentationAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\DocumentationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **DynamicSealAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\DynamicSealAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **FileClassificationAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\FileClassificationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **FilesystemSSOTReconcilerAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **GitAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\GitAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **GlobalComplianceAggregatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\GlobalComplianceAggregatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **GospelSyncAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\GospelSyncAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **GovernanceAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\GovernanceAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **HealValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\HealValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **HierarchyAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\HierarchyAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin
- **Namespace**: agentic_core/L5_safety/validators

### **HygieneGuardianAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\HygieneGuardianAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **InterfaceBoundaryAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\InterfaceBoundaryAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **L5SafetyExerciserAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\L5SafetyExerciserAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **LicS2SupervisorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\LicS2SupervisorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **LocationAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\LocationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **LocationHealerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\LocationHealerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **LocationValidatorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\LocationValidatorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin
- **Namespace**: agentic_core/L5_safety/validators

### **MCPGuardianAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\MCPGuardianAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **MemoryArchitectAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\MemoryArchitectAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **MetricsWitnessAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\MetricsWitnessAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, L0MaintenanceBaseAgent, AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin
- **Namespace**: agentic_core/L5_safety/validators

### **NamingAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\NamingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **NeuralAutoImmuneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\NeuralAutoImmuneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **OmniContextAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\OmniContextAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **PineconeSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PineconeSovereignAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **PolicyNeuralAutoImmuneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PolicyNeuralAutoImmuneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, NeuralAutoImmuneAgent
- **Namespace**: agentic_core/L5_safety/validators

### **PreCommitSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PreCommitSovereignAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **PredictiveCostAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PredictiveCostAuditorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **PromptRegistryAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\PromptRegistryAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **RagHealthCheckAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RagHealthCheckAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **RedisSovereignAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RedisSovereignAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **RegressionOracleAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RegressionOracleAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **ReportingAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ReportingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **RgReflectionAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RgReflectionAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **RootHygieneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RootHygieneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SemanticDebuggerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticDebuggerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SemanticGatekeeperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticGatekeeperAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SemanticMapperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticMapperAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SemanticTerritoryMapperAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SemanticTerritoryMapperAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SherlockAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SherlockAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SignatureVerifierAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SignatureVerifierAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SovereignActionPlaneAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignActionPlaneAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, IActionPlane
- **Namespace**: agentic_core/L5_safety/validators

### **SovereignCanonAuditorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignCanonAuditorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SovereignPineconeStoreAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SovereignPineconeStoreAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SprawlInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SprawlInspectorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **StrategistAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\StrategistAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **StructuralEngineerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\StructuralEngineerAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin, HealerMixin
- **Namespace**: agentic_core/L5_safety/validators

### **SubatomicHopAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SubatomicHopAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SystemArchitectAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SystemArchitectAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **TerritoryChangeHandlerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TerritoryChangeHandlerAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, FileSystemEventHandler
- **Namespace**: agentic_core/L5_safety/validators

### **TestGeneratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TestGeneratorAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **TestSovereigntyAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TestSovereigntyAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **TokenBudgetInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TokenBudgetInspectorAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **TypeHintFixerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TypeHintFixerAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, ast.NodeTransformer
- **Namespace**: agentic_core/L5_safety/validators

### **TypeMechanicAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TypeMechanicAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **AutonomicMonitorAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\AutonomicMonitorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **CoordinateObservabilityOperationsAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\CoordinateObservabilityOperationsAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **MetricsAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\MetricsAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **PerformanceAnalystAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\PerformanceAnalystAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **RuntimeTelemetryAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\RuntimeTelemetryAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **MockSovereignAgent** (Broken Import)
- **File**: `agentic_core\L6_observability\agents\RuntimeTelemetryAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: 
- **Namespace**: agentic_core/L6_observability/agents

### **SovereignObservabilityAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\SovereignObservabilityAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SovereignBaseAgent, SubatomicTestingMixin, MCPHardenedMixin, RedisCacheMixin, event_emission_mixin, ContextPropagationMixin
- **Namespace**: agentic_core/L6_observability/agents

### **StrategicObservationAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\StrategicObservationAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **DeadlockDetectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\TaskMonitorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **TelemetryAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\TelemetryAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **TracingAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\TracingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **TrackObservabilityCostAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\TrackObservabilityCostAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability/agents

### **BenchmarkingAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\BenchmarkingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability

### **DebateSynthesisAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\DebateSynthesisAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability

### **DocstringComplianceAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\DocstringComplianceAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L6_observability

### **BiasAuditorAgent** (Broken Import)
- **File**: `agentic_core\runtime\shared_runtime\BiasTypeAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/runtime/shared_runtime
- **Inheritance**: 
- **Namespace**: agentic_core/runtime/shared_runtime
