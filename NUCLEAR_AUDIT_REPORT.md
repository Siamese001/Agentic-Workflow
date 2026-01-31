# Nuclear Audit Results: agentic_core/ Agent Technical Status

Generated comprehensive analysis of all agents in agentic_core/ directory.

## Summary Statistics

- **Total Agents**: 65
- **Ready**: 43
- **Broken Import**: 0
- **Signature Mismatch**: 0
- **Stub**: 22

## Detailed Technical Status Table

| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |
|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|
| HistorianAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GitAgent | agentic_core/L2_execution/tool_registry [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ToolsmithAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| SubAtomicAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/fission_logic [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DAGMutatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DomainPlannerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| FeasibilityAnalystAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| RiskAssessorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StrategyCoordinatorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StrategyScenarioSimulatorAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| GravityLeakRepairAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.StructuralValidatorAgent | agentic_core/L5_safety/gravity [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| ConstitutionalReviewerAgent | SovereignBaseAgent, L5SafetyBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| PIISanitizerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| StructuralValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| AutonomyGuardianAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CanonDependencySentinelAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| CodeDeduplicationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.NamingAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| FilesystemSSOTReconcilerAgent | AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LicS2SupervisorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| LocationAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationHealerAgent, agentic_core.L5_safety.validators.NamingAgent (+19) | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| NamingAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| DocstringComplianceAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [OK] | [INFO] Stub | Contains TODO/FIXME/STUB markers |
| TracingAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, opentelemetry.sdk.resources, opentelemetry.sdk.trace (+1) | agentic_core/L6_observability/agents [OK] | [INFO] Stub | Contains pass-only methods |
| RootCustomsAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | SovereignBaseAgent | agentic_core/L0_maintenance/scripts [OK] | [OK] Ready |  |
| MetaLearningAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [OK] | [OK] Ready |  |
| RgStrategicPlannerAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [OK] | [OK] Ready |  |
| ValidationOrchestratorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, archives.void_violations.BudgetAgent, archives.void_violations.DocumentationAgent (+2) | agentic_core/L2_execution/tool_registry [OK] | [OK] Ready |  |
| OrchestratorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.CanonDependencySentinelAgent, agentic_core.L5_safety.validators.CredentialScannerAgent | agentic_core/L3_orchestration [OK] | [OK] Ready |  |
| DagEngineAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [OK] Ready |  |
| DagRuntimeInspectorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [OK] Ready |  |
| FissionManagerAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [OK] Ready |  |
| OrchestrationHandshakeAgent | SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.unified.CoreOrchestrationAgent | agentic_core/L3_orchestration/workflow_engines [OK] | [OK] Ready |  |
| GravityStateAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [OK] | [OK] Ready |  |
| AdversarialRedTeamerAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [OK] | [OK] Ready |  |
| SelfUpdatingSafetyEngineAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [OK] | [OK] Ready |  |
| CodeDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| CodeEnforcerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| CodeHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| CodeValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| ComplexityAnalyzerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| ResourceManagerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| SSOTFolderCleanupAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.cognition.CognitiveDispositionAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| SafetyDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| SafetyExecutorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| SecurityManagerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| StructureEnforcerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| StructureHealerAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/policy_engine [OK] | [OK] Ready |  |
| RedTeamAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [OK] | [OK] Ready |  |
| CognitiveDispositionAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| ContextCuratorAgent | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| DynamicSealAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| GovernanceAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| HealValidatorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| HygieneGuardianAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| MemoryArchitectAgent | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| PreCommitSovereignAgent | SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| PredictiveCostAuditorAgent | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| RgReflectionAgent | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| SignatureVerifierAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| TokenBudgetInspectorAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [OK] | [OK] Ready |  |
| BenchmarkingAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [OK] | [OK] Ready |  |
| DebateSynthesisAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [OK] | [OK] Ready |  |
| CoordinateObservabilityOperationsAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [OK] | [OK] Ready |  |
| DeadlockDetectorAgent | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [OK] | [OK] Ready |  |
| SovereignObservabilityAgent | SovereignBaseAgent, SubatomicTestingMixin, MCPHardenedMixin, RedisCacheMixin, event_emission_mixin, ContextPropagationMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [OK] | [OK] Ready |  |
| TrackObservabilityCostAgent | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [OK] | [OK] Ready |  |