# Per-agent spine trace (skeptical pass)

**Generated:** 2026-05-25T13:47:52Z

Transitive import closure from canonical spine seeds (not grep string hits).

| Metric | Value |
|--------|------:|
| Modules in spine closure | 100 |
| Agents scanned | 118 |
| Agent **modules** inside spine closure | 0 |

## Verdict rollup

| Verdict | Count | Meaning |
|---------|------:|---------|
| SPINE_CLOSURE | 0 | Agent module imported (transitively) from spine seeds |
| APPS_RG_ONLY | 1 | Referenced from apps_rg, not in spine closure |
| CORE_OFF_SPINE | 100 | agentic_core importers, not spine/apps_rg |
| OPS_ONLY | 5 | Only ops_scripts/tools importers |
| TEST_ONLY | 0 | Only tests reference |
| ORPHAN_NO_REF | 12 | No importer found in scan (agentic_core+apps+ops) |

## SPINE_CLOSURE agents (only these are in spine import graph)

_None_

## Full table

| Agent | Verdict | Spine closure | apps_rg | prod importers | sample |
|-------|---------|:-------------:|:-------:|:--------------:|--------|
| IntegrityGateExecutorAgent | APPS_RG_ONLY | no | 1 | 8 | agentic_core/L2_execution/config/strategist_bio_writer_config.py; agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py |
| ASTValidatorAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| AdversarialRedTeamerAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/L5_safety/redteam/__init__.py |
| ArchitectureGovernorAgent | CORE_OFF_SPINE | no | 0 | 30 | agentic_core/L0_routing/config/structure_blueprint_data.py; agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py |
| ArchitectureGovernorValidatorAgent | CORE_OFF_SPINE | no | 0 | 1 | agentic_core/L5_safety/utils/architecture_governor_validator_util.py |
| AutonomousThreatEvolutionAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; ops_scripts/general/generate_qwen_healing_report.py |
| AutonomyGuardianAgent | CORE_OFF_SPINE | no | 0 | 11 | agentic_core/L0_routing/config/structure_blueprint_data.py; agentic_core/L0_routing/enforcement/safety_validators_seam.py |
| BenchmarkingAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/L5_safety/utils/benchmarking_util.py |
| BootstrapAgent | CORE_OFF_SPINE | no | 0 | 8 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/L5_safety/utils/bootstrap_util.py |
| BoundaryTestingAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/runtime/prove_requirements/tier1_step1_metadata.py; ops_scripts/general/generate_qwen_healing_report.py |
| ChaosEngineeringAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L5_safety/validators/chaos_healing_integration_types.py; ops_scripts/general/generate_qwen_healing_report.py |
| CodeDeduplicationAgent | CORE_OFF_SPINE | no | 0 | 11 | agentic_core/L0_routing/enforcement/safety_enforcement_seam.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| CodeDetectorAgent | CORE_OFF_SPINE | no | 0 | 16 | agentic_core/L0_routing/config/structure_blueprint_data.py; agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py |
| CodeEnforcerAgent | CORE_OFF_SPINE | no | 0 | 11 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L3_orchestration/reasoning/engines/AgentFactory.py |
| CodeFormatterAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py; agentic_core/L5_safety/utils/code_formatter_util.py |
| CodeHealerAgent | CORE_OFF_SPINE | no | 0 | 14 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py |
| CodeJanitorAgent | CORE_OFF_SPINE | no | 0 | 8 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| CodeValidatorAgent | CORE_OFF_SPINE | no | 0 | 19 | agentic_core/L0_routing/utils/subprocess_runner_util.py; agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py |
| CognitiveDispositionAgent | CORE_OFF_SPINE | no | 0 | 12 | agentic_core/L0_routing/enforcement/safety_reasoning_seam.py; agentic_core/L0_routing/enforcement/safety_validators_seam.py |
| ComplexityAnalyzerAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L5_safety/utils/complexity_analyzer_util.py; agentic_core/prompt_governance/core/template_catalog.py |
| ConstitutionalReviewerAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/_compat/core/l5_safety_aliases.py |
| CostGovernorAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L5_safety/utils/cost_governor_util.py; ops_scripts/general/generate_qwen_healing_report.py |
| CoverageAgent | CORE_OFF_SPINE | no | 0 | 8 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py |
| CredentialScannerAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py; agentic_core/L5_safety/utils/credential_scanner_util.py |
| DAGMutatorAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/reasoning/engines/dag_manager.py |
| DDDAlignmentAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/_compat/core/l5_safety_aliases.py; agentic_core/config/hygiene_registry_config.py |
| DagEngineAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| DagRuntimeInspector | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/reasoning/InspectorExecutor.py |
| DependencyPruningAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/utils/dependency_pruning_util.py; agentic_core/L5_safety/validators/dependency_healing_integration_types.py |
| DocstringComplianceAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/prompt_governance/core/template_catalog.py |
| DocumentationAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py; agentic_core/L3_orchestration/utils/subatomic_agent_util.py |
| DomainPlannerAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/enforcement/DomainPlannerAdapter.py |
| DynamicSealAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py; agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py |
| EmbeddingSovereignAgent | CORE_OFF_SPINE | no | 0 | 21 | agentic_core/L1_cognition/reasoning/memory_embedder.py; agentic_core/L1_cognition/reasoning/meta_client.py |
| FileClassificationHealerAgent | CORE_OFF_SPINE | no | 0 | 13 | agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py; agentic_core/L5_safety/reasoning/file_classification/classification_core.py |
| FilesystemSSOTReconcilerAgent | CORE_OFF_SPINE | no | 0 | 16 | agentic_core/L3_orchestration/reasoning/territory_healing/territory_healer_adapters.py; agentic_core/L5_safety/config/structure_blueprint/ssot.py |
| FissionManagerAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| GitHygieneAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/enforcement/HealingStrategy.py; agentic_core/config/hygiene_registry_config.py |
| GospelSyncAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/_compat/core/l5_safety_aliases.py; ops_scripts/general/generate_qwen_healing_report.py |
| GovernanceAgent | CORE_OFF_SPINE | no | 0 | 13 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/enforcement/mission_runner.py |
| GravityLeakRepairAgent | CORE_OFF_SPINE | no | 0 | 12 | agentic_core/L4_state/utils/layer_gravity_util.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| GravityStateAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/utils/gravity_state_util.py |
| GravityValidatorAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py |
| HierarchyHealerAgent | CORE_OFF_SPINE | no | 0 | 16 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L3_orchestration/reasoning/territory_healing/territory_healer_adapters.py |
| HygieneGuardianAgent | CORE_OFF_SPINE | no | 0 | 21 | agentic_core/L0_routing/enforcement/safety_validators_seam.py; agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py |
| IOrchestratorAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py; agentic_core/L5_safety/utils/fca_safety_gates_util.py |
| ITieredAgent | CORE_OFF_SPINE | no | 0 | 1 | agentic_core/interfaces/__init__.py |
| InterfaceBoundaryAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/_compat/core/l5_safety_aliases.py; agentic_core/prompt_governance/core/template_catalog.py |
| L2EmbeddingSovereignAgent | CORE_OFF_SPINE | no | 0 | 1 | agentic_core/L2_execution/utils/l2_agent_wrappers.py |
| L2ExecutionAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L2_execution/reasoning/tool_intent_executor.py; agentic_core/L2_execution/types/__init__.py |
| L5SafetyExerciserAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| LocationHealerAgent | CORE_OFF_SPINE | no | 0 | 20 | agentic_core/L3_orchestration/reasoning/UnifiedAgent.py; agentic_core/L3_orchestration/reasoning/territory_healing/territory_healer_adapters.py |
| LocationValidatorAgent | CORE_OFF_SPINE | no | 0 | 10 | agentic_core/L0_routing/enforcement/safety_reasoning_seam.py; agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py |
| MetaLearningAgent | CORE_OFF_SPINE | no | 0 | 11 | agentic_core/L1_cognition/reasoning/CognitiveNode.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| NamingAgent | CORE_OFF_SPINE | no | 0 | 28 | agentic_core/L0_routing/enforcement/safety_reasoning_seam.py; agentic_core/L2_execution/config/unified_workflow_config.py |
| NervousSystemAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| NeuralAutoImmuneAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py |
| ObservabilityProbeExecutorAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L5_safety/utils/runners/agent_roster_runner.py; ops_scripts/dev_tools/L0_routing_scripts/_ssot_reporting.py |
| OrchestrationHandshakeAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/reasoning/engines/rl_coordinator_orchestrator.py |
| PascalSovereigntyAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/validators/PascalSovereigntyAgent.py |
| PerformanceAnalystAgentSimple | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; ops_scripts/dev_tools/L0_routing_scripts/colors.py |
| PolicyNeuralAutoImmuneAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/_compat/core/l5_safety_aliases.py; agentic_core/prompt_governance/core/template_catalog.py |
| PreCommitSovereignAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L0_routing/config/structure_blueprint_data.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| PredictiveCostAuditorAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/_compat/core/l5_safety_aliases.py |
| RedTeamAgent | CORE_OFF_SPINE | no | 0 | 8 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| RedisSovereignAgent | CORE_OFF_SPINE | no | 0 | 12 | agentic_core/L1_cognition/reasoning/meta_client.py; agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py |
| RegressionOracleAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/_compat/core/l5_safety_aliases.py |
| ReportLocationAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/_compat/core/l5_safety_aliases.py; agentic_core/prompt_governance/core/template_catalog.py |
| ResourceManagerAgent | CORE_OFF_SPINE | no | 0 | 9 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L3_orchestration/reasoning/engines/autonomous_execution_engine.py |
| RootCustomsAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L0_routing/utils/root_customs_util.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| RootHygieneHealerAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L5_safety/reasoning/root_hygiene_validator.py; agentic_core/L5_safety/utils/runners/agent_roster_runner.py |
| SSOTFolderCleanupAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py |
| SafetyDetectorAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; ops_scripts/dev_tools/L0_routing_scripts/archive_duplicates_util.py |
| SafetyExecutorAgent | CORE_OFF_SPINE | no | 0 | 7 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; ops_scripts/dev_tools/L0_routing_scripts/archive_duplicates_util.py |
| SafetyInspectorAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L3_orchestration/enforcement/mission_runner.py; agentic_core/L3_orchestration/reasoning/engines/AgentFactory.py |
| SecurityManagerAgent | CORE_OFF_SPINE | no | 0 | 7 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py |
| SelfUpdatingSafetyEngineAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; ops_scripts/general/generate_qwen_healing_report.py |
| SemanticGatekeeperAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| SovereignActionPlaneAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L0_routing/config/structure_blueprint_data.py; agentic_core/L5_safety/config/structure_blueprint/semantics.py |
| SovereignBaseAgent | CORE_OFF_SPINE | no | 0 | 40 | agentic_core/L0_routing/reasoning/RootCustomsAgent.py; agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py |
| SovereignMCPGateway | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L2_execution/utils/l2_agent_wrappers.py |
| SovereignRAGManager | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/adg/applications/rag_sovereignty.py; agentic_core/adg/applications/rag_sovereignty_validator.py |
| SprawlInspectorAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/_compat/core/l5_safety_aliases.py; ops_scripts/dev_tools/l0_scripts/rename_to_agent_suffix_util.py |
| StateManagementAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| StrategicRecommendationAgent | CORE_OFF_SPINE | no | 0 | 3 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; ops_scripts/dev_tools/L0_routing_scripts/investigate_overlaps_util.py |
| StructuralEngineerAgent | CORE_OFF_SPINE | no | 0 | 9 | agentic_core/L2_execution/reasoning/validation_orchestrator.py; agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py |
| StructuralValidatorAgent | CORE_OFF_SPINE | no | 0 | 12 | agentic_core/L3_orchestration/reasoning/UnifiedAgent.py; agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py |
| StructureEnforcerAgent | CORE_OFF_SPINE | no | 0 | 17 | agentic_core/L0_routing/enforcement/safety_reasoning_seam.py; agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py |
| StructureHealerAgent | CORE_OFF_SPINE | no | 0 | 9 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L2_execution/types/capability_token_types.py |
| StructuredEngineAgent | CORE_OFF_SPINE | no | 0 | 5 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L2_execution/utils/l2_agent_wrappers.py |
| SubAtomicAgent | CORE_OFF_SPINE | no | 0 | 13 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/reasoning/engines/omni_context_engine.py |
| SubAtomicRegistryAgent | CORE_OFF_SPINE | no | 0 | 6 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L2_execution/utils/l2_agent_wrappers.py |
| SubatomicHopAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L3_orchestration/utils/subatomic_hop_util.py |
| SystemArchitectAgent | CORE_OFF_SPINE | no | 0 | 8 | agentic_core/L5_safety/config/structure_blueprint/semantics.py; agentic_core/L5_safety/config/structure_blueprint/ssot.py |
| TerritoryChangeHandlerAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L3_orchestration/reasoning/engines/rl_coordinator_orchestrator.py; agentic_core/_compat/core/l5_safety_aliases.py |
| TestGeneratorAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py; agentic_core/L5_safety/config/structure_blueprint/ssot.py |
| ToolsmithAgent | CORE_OFF_SPINE | no | 0 | 7 | agentic_core/L2_execution/types/agent_taxonomy_registry.py; agentic_core/L2_execution/utils/toolsmith_util.py |
| TypeHintFixerAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/_compat/core/l5_safety_aliases.py; ops_scripts/dev_tools/L0_routing/add_test_coverage_util.py |
| TypeMechanicAgent | CORE_OFF_SPINE | no | 0 | 4 | agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py; agentic_core/L3_orchestration/utils/subatomic_agent_util.py |
| UnifiedAgent | CORE_OFF_SPINE | no | 0 | 14 | agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py; agentic_core/L2_execution/types/agent_taxonomy_registry.py |
| UnusedCleanupAgent | CORE_OFF_SPINE | no | 0 | 2 | agentic_core/L5_safety/utils/code_tool_runner_core_util.py; ops_scripts/general/generate_qwen_healing_report.py |
| AdversarialProbeAgent | OPS_ONLY | no | 0 | 1 | ops_scripts/general/generate_qwen_healing_report.py |
| DuplicateCodeDetectorAgent | OPS_ONLY | no | 0 | 6 | ops_scripts/dev_tools/L0_routing_scripts/delete_duplicates_util.py; ops_scripts/dev_tools/L0_routing_scripts/execute_safe_deletion_util.py |
| GenerativeGuardAgent | OPS_ONLY | no | 0 | 2 | ops_scripts/general/generate_qwen_healing_report.py; ops_scripts/general/restore_void_agents.py |
| HierarchyValidatorAgent | OPS_ONLY | no | 0 | 1 | ops_scripts/dev_tools/L0_routing_scripts/investigate_overlaps_util.py |
| RedSentinelAgent | OPS_ONLY | no | 0 | 2 | ops_scripts/dev_tools/l0_scripts/rename_to_agent_suffix_util.py; ops_scripts/general/generate_qwen_healing_report.py |
| FeasibilityAnalystAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| FileClassificationValidatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| FilesystemSSOTValidatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| GravityLeakValidatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| L2RedisSovereignAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| L2SovereignMCPGatewayAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| L2StructuredEngineAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| L2SubAtomicRegistryAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| RiskAssessorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| RootHygieneValidatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| StrategyCoordinatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
| StrategyScenarioSimulatorAgent | ORPHAN_NO_REF | no | 0 | 0 | — |
