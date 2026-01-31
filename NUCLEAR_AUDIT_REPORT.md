# Nuclear Audit Results: agentic_core/ Agent Technical Status

Generated comprehensive analysis of all agents in agentic_core/ directory.

## Summary Statistics

- **Total Agents**: 71
- **Ready**: 0
- **Broken Import**: 8
- **Signature Mismatch**: 63
- **Stub**: 0

## Detailed Technical Status Table

| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |
|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L0_maintenance/logs [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/logs |
| **RootCustomsAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L0_maintenance/scripts [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts |
| **BaseAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L2_execution/tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry |
| **SubAtomicAgent** |  | [MISSING] | heal(self, violation) |  | agentic_core/L2_execution/tool_registry [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L2_execution/tool_registry |
| **BaseAgent** |  | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FilesystemSSOTReconcilerAgent** | AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.L5_safety.validators.HierarchyAgent, agentic_core.L5_safety.validators.LocationValidatorAgent | agentic_core/L5_safety/validators [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators |
| **MockSovereignAgent** |  | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L6_observability/agents |
| **BiasAuditorAgent** |  | [MISSING] | heal(self, violation) | agentic_core.L5_safety.policy_engine.SafetyDetectorAgent | agentic_core/runtime/shared_runtime [INVALID] | [CRITICAL] Broken Import | Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/runtime/shared_runtime |
| **MetaLearningAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L1_cognition/thought_engine [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L1_cognition/thought_engine |
| **HistorianAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.GitAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **RgStrategicPlannerAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **ToolsmithAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **ValidationOrchestratorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, archives.void_violations.BudgetAgent, archives.void_violations.DocumentationAgent (+2) | agentic_core/L2_execution/tool_registry [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L2_execution/tool_registry |
| **OrchestratorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.CanonDependencySentinelAgent, agentic_core.L5_safety.validators.CredentialScannerAgent | agentic_core/L3_orchestration [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration |
| **SubAtomicAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/fission_logic [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/fission_logic |
| **DAGMutatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DagEngineAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DagRuntimeInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **DomainPlannerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FeasibilityAnalystAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **FissionManagerAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **OrchestrationHandshakeAgent** | SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L3_orchestration.unified.CoreOrchestrationAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **RiskAssessorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **StrategyCoordinatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **StrategyScenarioSimulatorAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.BaseAgent | agentic_core/L3_orchestration/workflow_engines [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L3_orchestration/workflow_engines |
| **GravityStateAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L4_state/validation_context [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L4_state/validation_context |
| **GravityLeakRepairAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.policy_engine.StructuralValidatorAgent | agentic_core/L5_safety/gravity [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/gravity |
| **AdversarialRedTeamerAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **ConstitutionalReviewerAgent** | SovereignBaseAgent, L5SafetyBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **PIISanitizerAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
| **SelfUpdatingSafetyEngineAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/guardrails [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/guardrails |
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
| **RedTeamAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/red_teaming [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/red_teaming |
| **AutonomyGuardianAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CanonDependencySentinelAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CodeDeduplicationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.base_agents.NamingAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **CognitiveDispositionAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **ContextCuratorAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **DynamicSealAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **GovernanceAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.guardrails.StructuralHealerAgent, agentic_core.L5_safety.guardrails.HierarchyAgent (+1) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **HealValidatorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **HygieneGuardianAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LicS2SupervisorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **LocationAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, agentic_core.L5_safety.validators.LocationHealerAgent, agentic_core.L5_safety.validators.NamingAgent (+19) | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **MemoryArchitectAgent** | SovereignBaseAgent, SubAtomicAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **NamingAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PreCommitSovereignAgent** | SubatomicTestingMixin, SovereignBaseAgent, L0MaintenanceBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent, agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **PredictiveCostAuditorAgent** | SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **RgReflectionAgent** | SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **SignatureVerifierAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L5_safety/validators |
| **TokenBudgetInspectorAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | Not found | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L5_safety/validators [INVALID] | [WARNING] Signature Mismatch | Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators |
| **BenchmarkingAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **DebateSynthesisAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **DocstringComplianceAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability |
| **CoordinateObservabilityOperationsAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **DeadlockDetectorAgent** | SovereignBaseAgent | [MISSING] | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **SovereignObservabilityAgent** | SovereignBaseAgent, SubatomicTestingMixin, MCPHardenedMixin, RedisCacheMixin, event_emission_mixin, ContextPropagationMixin | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **TracingAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent, opentelemetry.sdk.resources, opentelemetry.sdk.trace (+1) | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |
| **TrackObservabilityCostAgent** | SubatomicTestingMixin, SovereignBaseAgent | [OK] SubatomicTesting | heal(self, violation) | agentic_core.base_agents.SovereignBaseAgent | agentic_core/L6_observability/agents [INVALID] | [WARNING] Signature Mismatch | Invalid namespace: agentic_core/L6_observability/agents |

## High-Priority Remediation Targets

The following agents require immediate attention:

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\logs\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/logs
- **Inheritance**: 
- **Namespace**: agentic_core/L0_maintenance/logs

### **RootCustomsAgent** (Broken Import)
- **File**: `agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L0_maintenance/scripts
- **Inheritance**: 
- **Namespace**: agentic_core/L0_maintenance/scripts

### **MetaLearningAgent** (Signature Mismatch)
- **File**: `agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py`
- **Issues**: Invalid namespace: agentic_core/L1_cognition/thought_engine
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L1_cognition/thought_engine

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

### **RgStrategicPlannerAgent** (Signature Mismatch)
- **File**: `agentic_core\L2_execution\tool_registry\RgStrategicPlannerAgent.py`
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
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/fission_logic
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration/fission_logic

### **OrchestratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\OrchestratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L3_orchestration

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

### **OrchestrationHandshakeAgent** (Signature Mismatch)
- **File**: `agentic_core\L3_orchestration\workflow_engines\OrchestrationHandshakeAgent.py`
- **Issues**: Invalid namespace: agentic_core/L3_orchestration/workflow_engines
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent, CoreOrchestrationAgent
- **Namespace**: agentic_core/L3_orchestration/workflow_engines

### **GravityStateAgent** (Signature Mismatch)
- **File**: `agentic_core\L4_state\validation_context\GravityStateAgent.py`
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

### **ConstitutionalReviewerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\ConstitutionalReviewerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent, L5SafetyBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **PIISanitizerAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\PIISanitizerAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/guardrails

### **SelfUpdatingSafetyEngineAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\guardrails\SelfUpdatingSafetyEngineAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/guardrails
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
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

### **RedTeamAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\red_teaming\RedTeamAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/red_teaming
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/red_teaming

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

### **ContextCuratorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\ContextCuratorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **DynamicSealAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\DynamicSealAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **FilesystemSSOTReconcilerAgent** (Broken Import)
- **File**: `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Issues**: Missing SovereignBaseAgent inheritance; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: AutonomyMixin, SelfDiagnosisMixin, L0MaintenanceBaseAgent
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

### **HygieneGuardianAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\HygieneGuardianAgent.py`
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

### **MemoryArchitectAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\MemoryArchitectAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent, SubAtomicAgent
- **Namespace**: agentic_core/L5_safety/validators

### **NamingAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\NamingAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
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

### **RgReflectionAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\RgReflectionAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **SignatureVerifierAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\SignatureVerifierAgent.py`
- **Issues**: Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **TokenBudgetInspectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L5_safety\validators\TokenBudgetInspectorAgent.py`
- **Issues**: Missing heal() method; Invalid namespace: agentic_core/L5_safety/validators
- **Inheritance**: SubatomicTestingMixin, SovereignBaseAgent
- **Namespace**: agentic_core/L5_safety/validators

### **CoordinateObservabilityOperationsAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\CoordinateObservabilityOperationsAgent.py`
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

### **DeadlockDetectorAgent** (Signature Mismatch)
- **File**: `agentic_core\L6_observability\agents\TaskMonitorAgent.py`
- **Issues**: Invalid namespace: agentic_core/L6_observability/agents
- **Inheritance**: SovereignBaseAgent
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
