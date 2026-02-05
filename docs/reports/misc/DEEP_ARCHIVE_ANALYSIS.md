================================================================================
DEEP ARCHIVE ANALYSIS - FINDINGS & RECOMMENDATIONS
================================================================================

Total files scanned: 5900
  RESTORE (unique agents/high value): 2023
  EXTRACT (unique content): 674
  REVIEW (partial overlap): 126
  SKIP (exists in codebase): 2942
  SYNTAX ERRORS: 135

================================================================================
ARCHIVE FOLDER BREAKDOWN
================================================================================

  identity_duplicates:
    Files: 3228, Restore: 728
    Unique Agents: ['HealerAgent', 'GravityEnforcerAgent', 'GravityEnforcerAgent', 'HygieneValidatorAgent', 'CognitiveContractValidatorAgent', 'DynamicModelRouterAgent', 'OrchestratorAgentAndScopeManagerAgent', 'ActorCriticOrchestratorAgent', 'AgentPermissionManagerAgent', 'HierarchyEnforcerAgent']

  hierarchy_violations:
    Files: 719, Restore: 579
    Unique Agents: ['TestLeadQualityAgent', 'TestContactValidatorAgent', 'TestMessageComplianceAgent', 'TestOutreachProactiveAgent', 'TestContentQualityAgent', 'TestFactCheckAgent', 'TestBrandComplianceAgent', 'TestSectionBalanceAgent', 'TestATSCompatibilityAgent', 'TestReflectionAgent']

  void_violations:
    Files: 466, Restore: 152
    Unique Agents: ['AgentPermissionManagerAgent', 'AgentRegistryValidatorAgent', 'AsyncBlockingValidatorAgent', '_BlueprintHierarchyHealerAgent', '_BlueprintHierarchyHealerAgent', '_BlueprintHierarchyHealerAgent', '_BlueprintHierarchyHealerAgent', 'CachedOrchestratorAgent', 'CanonAstValidatorAgent', 'CognitiveContractValidatorAgent']

  runtime:
    Files: 136, Restore: 81
    Unique Agents: ['ReconAgent', 'Agent', 'Executive_Title_Composer', 'Gap_Closure_Architect', 'HopExecutionError', 'ValidationError', 'APIError', 'CircuitBreakerOpenError', 'QueryDecomposer', 'Strategist_BioWriter']

  Reachout Engine Archive:
    Files: 103, Restore: 74
    Unique Agents: ['HOP2_ResearchAgent', 'HOP5_GenerationAgent', 'QAConductorAgent', 'MetaLearningLoop', 'BaseTool', 'LogReaderAgent', 'AsyncLogSummarizerAgent', 'AsyncPatternFinderAgent', 'AsyncHypothesisGeneratorAgent', 'AsyncProposalDrafterAgent']

  location_violations:
    Files: 185, Restore: 53
    Unique Agents: ['ConsolidatedOrchestratorAgent', '_LegacyNamingAgent', 'OrchestratorAgentAndScopeManagerAgent', 'ExecutiveTitleComposer', 'SafetyExecutorAgent']

  legacy_agents:
    Files: 54, Restore: 47
    Unique Agents: ['BiasDetectorAgent', 'DeadCodeDetectorAgent', 'DriftDetectorAgent', 'HallucinationDetectorAgent', 'MethodChangeDetectorAgent', 'PromptInjectionDetectorAgent', 'CodeSSOTEnforcerAgent', 'CodeStandardsEnforcerAgent', 'DocEnforcerAgent', 'GravityEnforcerAgent']

  apps_shared:
    Files: 41, Restore: 37

  observability:
    Files: 63, Restore: 33

  bloat_elimination_2026_01:
    Files: 311, Restore: 28
    Unique Agents: ['MalformedAgent']

  apps_rg:
    Files: 94, Restore: 24
    Unique Agents: ['TitaniumAwareAgent']

  consolidated_agents:
    Files: 24, Restore: 24
    Unique Agents: ['ScriptToAgentClassifierAgent', 'GeneralExerciserAgent', 'L1CognitionExerciserAgent', 'L4StateExerciserAgent', 'MetaCoverageOptimizerAgent', 'ValidationContextManagerAgent', 'PatternEnforcerAgent', 'BareExceptValidatorAgent', 'DangerousBuiltinsValidatorAgent', 'DebuggerValidatorAgent']

  apps_lic:
    Files: 91, Restore: 20

  legacy_orchestrators:
    Files: 20, Restore: 18
    Unique Agents: ['CachedOrchestratorAgent', 'ConsolidatedOrchestratorAgent', 'HardenedWorkflowOrchestratorAgent', 'IntelligentOrchestratorAgent', 'LicHealingOrchestratorAgent', 'LicWorkflowOrchestratorAgent', 'OrchestratorAgentAndScopeManagerAgent', 'OutreachPhase5OrchestratorAgent', 'Phase4OrchestratorAgent', 'Phase6OrchestratorAgent']

  legacy_validators:
    Files: 18, Restore: 15
    Unique Agents: ['AgentRegistryValidatorAgent', 'AsyncBlockingValidatorAgent', 'CanonAstValidatorAgent', 'CognitiveContractValidatorAgent', 'ContactValidatorAgent', 'ContextAwareValidatorAgent', 'ExternalHttpValidatorAgent', 'GravityValidatorAgent', 'HygieneValidatorAgent', 'InputValidatorAgent']

  schemas:
    Files: 29, Restore: 14

  deprecated_agents:
    Files: 21, Restore: 10
    Unique Agents: ['GenerativeGuardDeprecatedAgent', 'GravityComplianceValidatorAgent', 'GravityEnforcerAgent', 'McpConnectionManagerAgent', 'OutreachTestPilotDeprecatedAgent', 'StrategicPlannerAgent', 'SystemArchitectDeprecatedAgent', '_LegacyConcurrencyGuardianAgent', '_LegacyDependencySentinelAgent']

  app_leaks_L1_20260110_071932:
    Files: 39, Restore: 9

  config:
    Files: 25, Restore: 8

  misplaced_tests_2026_01_20:
    Files: 14, Restore: 8

  deprecated_2026_01_20:
    Files: 14, Restore: 7
    Unique Agents: ['SSOTOrchestratorAgent', 'HealingOrchestratorAgent', 'ConsolidatedOrchestratorAgent', 'AppWorkflowOrchestratorAgent', 'CoreOrchestrationAgent', 'FilesystemAgent', 'NamingNormalizationAgent']

  tests:
    Files: 8, Restore: 7

  completed_migrations:
    Files: 22, Restore: 6

  naming_violations:
    Files: 19, Restore: 5

  unmapped_drift:
    Files: 17, Restore: 5

  deprecated_tests:
    Files: 4, Restore: 4

  legacy_code:
    Files: 18, Restore: 4

  shared:
    Files: 23, Restore: 4
    Unique Agents: ['HopExecutionError', 'StagingBufferError', 'CircuitBreakerOpenError', 'PhaseTimeoutError', 'ValidationError', 'APIError']

  dedup_archived:
    Files: 22, Restore: 3

  deprecated_modules:
    Files: 4, Restore: 3

  L4_state:
    Files: 4, Restore: 3
    Unique Agents: ['AutonomousCheckpointManagerAgent', 'AutonomousStateGuardianAgent']

  legacy_cleanup_20251219:
    Files: 5, Restore: 3

  prompt_governance:
    Files: 6, Restore: 3

  core_contracts_monolithic_20260101:
    Files: 1, Restore: 1

  deprecated_key_validators:
    Files: 1, Restore: 1

  duplicate_tests_20260110_090742:
    Files: 17, Restore: 1

  examples_deprecated:
    Files: 1, Restore: 1
    Unique Agents: ['TalentIntelligenceAgent']

================================================================================
HIGH PRIORITY - RESTORE (Unique Agents)
================================================================================

  [100%] lic_vector_memory.py
    Path: apps_lic\L1_cognition\P1_retrieve\lic_vector_memory.py
    Domain: SHARED
    Unique Classes: ['VectorDocument', 'QueryResult', 'MemoryStats', 'LICVectorMemory', 'MockVectorMemory']
    Target: apps_shared/

  [100%] enforce_outreach_boundaries.py
    Path: apps_lic\L1_cognition\P1_retrieve\check_outreach\enforce_outreach_boundaries.py
    Domain: OUTREACH
    Unique Classes: ['enforce_outreach_boundaries', 'get_enforce_outreach_boundaries_config']
    Target: apps_lic/engines/

  [100%] validate_outreach_constraints.py
    Path: apps_lic\L1_cognition\P1_retrieve\check_outreach\validate_outreach_constraints.py
    Domain: OUTREACH
    Unique Classes: ['validate_outreach_constraints', 'get_validate_outreach_constraints_config']
    Target: apps_lic/engines/

  [100%] check_message_quality.py
    Path: apps_lic\L1_cognition\P2_inspect\check_message_quality.py
    Domain: OUTREACH
    Unique Classes: ['check_message_quality', 'get_check_message_quality_config']
    Target: apps_lic/engines/

  [100%] validate_generated_message.py
    Path: apps_lic\L1_cognition\P2_inspect\validate_generated_message.py
    Domain: OUTREACH
    Unique Classes: ['validate_generated_message', 'get_validate_generated_message_config']
    Target: apps_lic/engines/

  [100%] check_message_compliance.py
    Path: apps_lic\L1_cognition\P3_aggregate\check_message_compliance.py
    Domain: OUTREACH
    Unique Classes: ['check_message_compliance', 'get_check_message_compliance_config']
    Target: apps_lic/engines/

  [100%] enforce_message_contracts.py
    Path: apps_lic\L1_cognition\P3_aggregate\enforce_message_contracts.py
    Domain: OUTREACH
    Unique Classes: ['enforce_message_contracts', 'get_enforce_message_contracts_config']
    Target: apps_lic/engines/

  [100%] lic_archetypes.py
    Path: apps_lic\L1_cognition\P3_aggregate\lic_archetypes.py
    Domain: OUTREACH
    Unique Classes: ['RecipientArchetype', 'SubjectLineBrief', 'MessageBodyBrief', 'CTABrief', 'CreativeBrief']
    Target: apps_lic/engines/

  [100%] lic_cta_patterns.py
    Path: apps_lic\L1_cognition\P3_aggregate\lic_cta_patterns.py
    Domain: OUTREACH
    Unique Classes: ['RecipientArchetype', 'CTAStyle', 'CTAPattern', 'CTATemplate', 'DateWindowConfig']
    Target: apps_lic/engines/

  [100%] merge_outreach_history.py
    Path: apps_lic\L1_cognition\P3_aggregate\merge_outreach_history.py
    Domain: OUTREACH
    Unique Classes: ['MergeOutreachHistory']
    Target: apps_lic/engines/

  [100%] serialize_outreach_context.py
    Path: apps_lic\L1_cognition\P3_aggregate\serialize_outreach_context.py
    Domain: OUTREACH
    Unique Classes: ['SerializeOutreachContext']
    Target: apps_lic/engines/

  [100%] validate_message_schema.py
    Path: apps_lic\L1_cognition\P3_aggregate\validate_message_schema.py
    Domain: OUTREACH
    Unique Classes: ['validate_message_schema', 'get_validate_message_schema_config']
    Target: apps_lic/engines/

  [100%] apply_outreach_safety_policy.py
    Path: apps_lic\L1_cognition\P4_safety\check_outreach\apply_outreach_safety_policy.py
    Domain: OUTREACH
    Unique Classes: ['apply_outreach_safety_policy', 'get_apply_outreach_safety_policy_config']
    Target: apps_lic/engines/

  [100%] track_outreach_generation_cost.py
    Path: apps_lic\L1_cognition\P4_safety\manage_outreach_costs\track_outreach_generation_cost.py
    Domain: OUTREACH
    Unique Classes: ['TrackOutreachGenerationCost']
    Target: apps_lic/engines/

  [100%] apply_lic_execution_safety.py
    Path: apps_lic\L2_execution\apply_lic_execution_safety.py
    Domain: OUTREACH
    Unique Classes: ['apply_lic_execution_safety', 'get_apply_lic_execution_safety_config']
    Target: apps_lic/engines/

  [100%] lic_code_interpreter.py
    Path: apps_lic\L2_execution\lic_code_interpreter.py
    Domain: OUTREACH
    Unique Classes: ['ScoredCandidate', 'ScoringCriteria', 'SimilarityResult', 'KeywordExtractionResult', 'LICCodeInterpreter']
    Target: apps_lic/engines/

  [100%] lic_company_research_executor.py
    Path: apps_lic\L2_execution\lic_company_research_executor.py
    Domain: OUTREACH
    Unique Classes: ['lic_company_research_executor', 'get_lic_company_research_executor_config']
    Target: apps_lic/engines/

  [100%] lic_contact_research_executor.py
    Path: apps_lic\L2_execution\lic_contact_research_executor.py
    Domain: OUTREACH
    Unique Classes: ['lic_contact_research_executor', 'get_lic_contact_research_executor_config']
    Target: apps_lic/engines/

  [100%] enforce_resume_boundaries.py
    Path: apps_rg\L1_cognition\P1_retrieve\check_resume\enforce_resume_boundaries.py
    Domain: RESUME
    Unique Classes: ['enforce_resume_boundaries', 'get_enforce_resume_boundaries_config']
    Target: apps_rg/engines/

  [100%] safety_validate_resume_constraints.py
    Path: apps_rg\L1_cognition\P1_retrieve\check_resume\safety_validate_resume_constraints.py
    Domain: RESUME
    Unique Classes: ['validate_resume_constraints', 'get_validate_resume_constraints_config']
    Target: apps_rg/engines/

  [100%] meaning_search_similar_resumes.py
    Path: apps_rg\L1_cognition\P1_retrieve\get_info\meaning_search_similar_resumes.py
    Domain: RESUME
    Unique Classes: ['SearchSimilarResumes']
    Target: apps_rg/engines/

  [100%] embed_resume_sections.py
    Path: apps_rg\L1_cognition\P2_inspect\embed_resume_sections.py
    Domain: RESUME
    Unique Classes: ['EmbedResumeSections']
    Target: apps_rg/engines/

  [100%] aggregate_resume_state.py
    Path: apps_rg\L1_cognition\P3_aggregate\aggregate_resume_state.py
    Domain: RESUME
    Unique Classes: ['AggregateResumeState']
    Target: apps_rg/engines/

  [100%] check_resume_compliance.py
    Path: apps_rg\L1_cognition\P3_aggregate\check_resume_compliance.py
    Domain: RESUME
    Unique Classes: ['check_resume_compliance', 'get_check_resume_compliance_config']
    Target: apps_rg/engines/

  [100%] enforce_resume_contracts.py
    Path: apps_rg\L1_cognition\P3_aggregate\enforce_resume_contracts.py
    Domain: RESUME
    Unique Classes: ['enforce_resume_contracts', 'get_enforce_resume_contracts_config']
    Target: apps_rg/engines/

  [100%] rg_creative_brief.py
    Path: apps_rg\L1_cognition\P3_aggregate\rg_creative_brief.py
    Domain: RESUME
    Unique Classes: ['VoiceType', 'ProvenanceStrategy', 'WordCountConstraint', 'CharCountConstraint', 'StructureConstraint']
    Target: apps_rg/engines/

  [100%] snapshot_resume_state.py
    Path: apps_rg\L1_cognition\P3_aggregate\snapshot_resume_state.py
    Domain: RESUME
    Unique Classes: ['SnapshotResumeState']
    Target: apps_rg/engines/

  [100%] validate_resume_schema.py
    Path: apps_rg\L1_cognition\P3_aggregate\validate_resume_schema.py
    Domain: RESUME
    Unique Classes: ['validate_resume_schema', 'get_validate_resume_schema_config']
    Target: apps_rg/engines/

  [100%] apply_resume_safety_policy.py
    Path: apps_rg\L1_cognition\P4_safety\check_resume\apply_resume_safety_policy.py
    Domain: SHARED
    Unique Classes: ['apply_resume_safety_policy', 'get_apply_resume_safety_policy_config']
    Target: apps_shared/

  [100%] track_resume_generation_cost.py
    Path: apps_rg\L1_cognition\P4_safety\manage_resume_costs\track_resume_generation_cost.py
    Domain: RESUME
    Unique Classes: ['TrackResumeGenerationCost']
    Target: apps_rg/engines/

  [100%] resume_planner.py
    Path: apps_rg\L1_cognition\planning\resume_planner.py
    Domain: RESUME
    Unique Classes: ['ResumeAnalysisPlan', 'ResumeSectionConfig', 'ResumeProcessingPlan', 'RGPlanner']
    Target: apps_rg/engines/

  [100%] resume_generator.py
    Path: apps_rg\L2_execution\resume_generator.py
    Domain: RESUME
    Unique Classes: ['ResumeGenerator']
    Target: apps_rg/engines/

  [100%] rg_company_research_executor.py
    Path: apps_rg\L2_execution\rg_company_research_executor.py
    Domain: SHARED
    Unique Classes: ['rg_company_research_executor', 'get_rg_company_research_executor_config']
    Target: apps_shared/

  [100%] rg_contact_research_executor.py
    Path: apps_rg\L2_execution\rg_contact_research_executor.py
    Domain: RESUME
    Unique Classes: ['SafetyExecutor']
    Target: apps_rg/engines/

  [100%] rg_message_generation_executor.py
    Path: apps_rg\L2_execution\rg_message_generation_executor.py
    Domain: OUTREACH
    Unique Classes: ['rg_message_generation_executor', 'get_rg_message_generation_executor_config']
    Target: apps_lic/engines/

  [100%] state_manager.py
    Path: apps_rg\L2_execution\resume_generation\state_manager.py
    Domain: INFRASTRUCTURE
    Unique Classes: ['StateSerializer', 'ManifestManager']
    Target: agentic_core/utils/

  [100%] hardened_orchestrator.py
    Path: apps_rg\L3_orchestration\hardened_orchestrator.py
    Domain: INFRASTRUCTURE
    Unique Classes: ['HardenedWorkflowOrchestrator', 'create_hardened_orchestrator']
    Target: agentic_core/utils/

  [100%] orchestrate_resume.py
    Path: apps_rg\L3_orchestration\orchestrate_resume.py
    Domain: RESUME
    Unique Classes: ['ResumeOrchestrator', 'orchestrate_resume']
    Target: apps_rg/engines/

  [100%] titanium_integration.py
    Path: apps_rg\L3_orchestration\titanium_integration.py
    Domain: SHARED
    Unique Agents: ['TitaniumAwareAgent']
    Unique Classes: ['TitaniumSearchWrapper', 'get_titanium_wrapper', 'inject_titanium_tools', 'with_titanium_search', 'enhance_system_prompt']
    Target: apps_shared/

  [100%] check_hallucination.py
    Path: apps_rg\L3_orchestration\safety\check_hallucination.py
    Domain: SHARED
    Unique Classes: ['HallucinationDetector']
    Target: apps_shared/

  [100%] control_plane_judge_engine.py
    Path: apps_shared\core\control_plane_judge_engine.py
    Domain: SHARED
    Unique Classes: ['test_judge_engine_unsafe_on_high_severity']
    Target: apps_shared/

  [100%] control_plane_rules_engine.py
    Path: apps_shared\core\control_plane_rules_engine.py
    Domain: OUTREACH
    Unique Classes: ['test_rules_engine_detects_pii_email']
    Target: apps_lic/engines/

  [100%] dag_executor_basic.py
    Path: apps_shared\core\dag_executor_basic.py
    Domain: OUTREACH
    Unique Classes: ['test_dag_executor_cycle_detection']
    Target: apps_lic/engines/

  [100%] dag_models.py
    Path: apps_shared\core\dag_models.py
    Domain: SHARED
    Unique Classes: ['test_graph_successors_and_predecessors', 'test_dag_executor_linear_graph']
    Target: apps_shared/

  [100%] golden_state_gating.py
    Path: apps_shared\core\golden_state_gating.py
    Domain: SHARED
    Unique Classes: ['test_gate_experiment_allows_without_baseline', 'test_gate_experiment_enforces_avg_and_pass_count']
    Target: apps_shared/

  [100%] golden_state_judge.py
    Path: apps_shared\core\golden_state_judge.py
    Domain: SHARED
    Unique Classes: ['test_judge_empty_output_fails', 'test_judge_detects_key_behavior']
    Target: apps_shared/

  [100%] golden_state_scorer.py
    Path: apps_shared\core\golden_state_scorer.py
    Domain: SHARED
    Unique Classes: ['test_aggregate_scores_basic']
    Target: apps_shared/

  [100%] metacognition_hypothesis_evaluation.py
    Path: apps_shared\core\metacognition_hypothesis_evaluation.py
    Domain: SHARED
    Unique Classes: ['test_evaluate_penalizes_no_evidence', 'test_evaluate_clamps_confidence_range']
    Target: apps_shared/

  [100%] metacognition_refinement.py
    Path: apps_shared\core\metacognition_refinement.py
    Domain: SHARED
    Unique Classes: ['test_refine_marks_very_low_confidence_as_discarded']
    Target: apps_shared/

  [100%] metacognition_uncertainty_model.py
    Path: apps_shared\core\metacognition_uncertainty_model.py
    Domain: SHARED
    Unique Classes: ['test_uncertainty_increases_with_signals']
    Target: apps_shared/

================================================================================
MEDIUM PRIORITY - EXTRACT (Unique Utilities)
================================================================================

Total: 674 files

  [79%] test_dashboard_end_to_end.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054936\import_fixes\.sovereign_healing_backup\location\20260118_053301\import_fixes\scripts\test_dashboard_end_to_end.py
    Unique: ['load_agent_discovery_json', 'load_all_js_content', 'load_html_content', 'test_agent_discovery_integrity', 'test_dashboard_html_exists']

  [79%] test_dashboard_end_to_end.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_060335\import_fixes\.sovereign_healing_backup\location\20260118_054943\import_fixes\scripts\test_dashboard_end_to_end.py
    Unique: ['load_agent_discovery_json', 'load_all_js_content', 'load_html_content', 'test_agent_discovery_integrity', 'test_dashboard_html_exists']

  [78%] use_observability_execution.py
    Path: observability\runtime\synthesis\use_tools\use_observability_execution.py
    Unique: ['ExecutionPriority', 'ExecutionRequest', 'ExecutionEnvironment', 'ExecutionConfig', 'ObservabilityExecutionEngine']

  [78%] signal_infrastructure.py
    Path: runtime\shared\signal_infrastructure.py
    Unique: ['EngineType', 'DomainValidator', 'ResumeValidator', 'OutreachValidator', 'SharedSignalInfrastructure']

  [78%] event_bus.py
    Path: runtime\shared\core\event_bus.py
    Unique: ['SystemEvent', 'EventBus', 'MemoryEventBus', 'RedisEventBus', 'create_event_bus']

  [75%] runtime_registry_agent_capabilities.py
    Path: bloat_elimination_2026_01\deprecated_l0_scripts\agentic_core\L0_maintenance\scripts\runtime_registry_agent_capabilities.py
    Unique: ['AgentRole', 'AgentSpec', 'AgentRegistry']

  [75%] archive_consolidated_agents.py
    Path: bloat_elimination_2026_01\migration_scripts\archive_consolidated_agents.py
    Unique: ['create_archive_directory', 'archive_agent', 'create_consolidation_manifest']

  [75%] phase4_batch1_decorator_sweep.py
    Path: bloat_elimination_2026_01\migration_scripts\phase4_batch1_decorator_sweep.py
    Unique: ['find_python_files', 'has_heal_repository_method', 'already_has_decorator', 'already_has_import', 'find_import_insertion_point']

  [75%] restore_all_archived_agents.py
    Path: bloat_elimination_2026_01\migration_scripts\restore_all_archived_agents.py
    Unique: ['get_current_agents', 'infer_target_directory', 'restore_agent']

  [75%] restore_app_agents.py
    Path: bloat_elimination_2026_01\migration_scripts\restore_app_agents.py
    Unique: ['extract_original_path', 'get_agents_to_restore', 'remove_violation_header']

  [75%] compare_agent_lists.py
    Path: bloat_elimination_2026_01\one_time_utilities\compare_agent_lists.py
    Unique: ['get_agents_at_commit', 'get_current_agents', 'find_agent_in_archives']

  [75%] waterfall_reconciliation.py
    Path: bloat_elimination_2026_01\one_time_utilities\waterfall_reconciliation.py
    Unique: ['get_agents_at_commit', 'get_current_agents', 'find_agent_in_archives']

  [75%] fix_testing_observability.py
    Path: bloat_elimination_2026_01\one_time_utilities\agentic_core\L0_maintenance\scripts\fix_testing_observability.py
    Unique: ['load_agents', 'add_logging_to_file', 'add_testing_mixin_to_class']

  [75%] sprint4_phase3_final_cleanup.py
    Path: completed_migrations\sprints\sprint4_phase3_final_cleanup.py
    Unique: ['fix_hierarchy_violations', 'fix_drift_violation', 'annotate_dynamic_imports']

  [75%] test_temporal_outreach.py
    Path: hierarchy_violations\apps_depth\apps_lic\engines\outreach_engine\test_temporal_outreach.py
    Unique: ['test_temporal_vetting', 'test_governed_outreach', 'test_time_bound_benchmarking']

  [75%] resume_orchestration_config_impl.py
    Path: hierarchy_violations\apps_depth\apps_rg\engines\resume_engine\resume_orchestration_config_impl.py
    Unique: ['get_word_count_constraint', 'get_char_count_constraint', 'get_validation_gates']

  [75%] TestBudgetManagerAgent.py
    Path: hierarchy_violations\apps_depth\apps_rg\engines\resume_engine\TestBudgetManagerAgent.py
    Unique: ['TestBudgetManager', 'TestSectionDependencyGraph', 'TestResumeEngineContext']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_053336\semantic_keyword_insertion\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

  [75%] fix_testing_observability.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_053840\import_fixes\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\fix_testing_observability.py
    Unique: ['load_agents', 'add_logging_to_file', 'add_testing_mixin_to_class']

  [75%] runtime_core_swarm_example.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054816\agentic_core\L0_maintenance\scripts\runtime_core_swarm_example.py
    Unique: ['example_basic_swarm', 'example_error_handling', 'example_batch_execution', 'example_resume_generation_swarm', 'example_progressive_scaling']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054936\import_fixes\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

  [75%] fix_testing_observability.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054936\import_fixes\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\fix_testing_observability.py
    Unique: ['load_agents', 'add_logging_to_file', 'add_testing_mixin_to_class']

  [75%] sprint4_phase3_final_cleanup.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054936\import_fixes\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\sprint4_phase3_final_cleanup.py
    Unique: ['fix_hierarchy_violations', 'fix_drift_violation', 'annotate_dynamic_imports']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054937\import_fixes\.sovereign_healing_backup\location\20260118_053336\semantic_keyword_insertion\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

  [75%] fix_testing_observability.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_054937\import_fixes\.sovereign_healing_backup\location\20260118_053840\import_fixes\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\fix_testing_observability.py
    Unique: ['load_agents', 'add_logging_to_file', 'add_testing_mixin_to_class']

  [75%] runtime_shared_resume_swarm.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_055046\agentic_core\L0_maintenance\scripts\runtime_shared_resume_swarm.py
    Unique: ['ResumeResult', 'ResumeSwarm', 'create_resume_swarm']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_060115\semantic_keyword_insertion\.sovereign_healing_backup\location\20260118_053300\import_fixes\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_060332\import_fixes\.sovereign_healing_backup\location\20260118_054937\import_fixes\.sovereign_healing_backup\location\20260118_053336\semantic_keyword_insertion\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

  [75%] fix_testing_observability.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_060332\import_fixes\.sovereign_healing_backup\location\20260118_054937\import_fixes\.sovereign_healing_backup\location\20260118_053842\import_fixes\scripts\fix_testing_observability.py
    Unique: ['load_agents', 'add_logging_to_file', 'add_testing_mixin_to_class']

  [75%] coverage_validator.py
    Path: identity_duplicates\.sovereign_healing_backup\location\20260118_060335\import_fixes\.sovereign_healing_backup\location\20260118_054943\import_fixes\scripts\coverage_validator.py
    Unique: ['CoverageValidator', 'CoverageHealer', 'run_autonomous_remediation']

================================================================================
EXECUTIVE SUMMARY
================================================================================

    Files to RESTORE:           2023
    Files to EXTRACT:           674
    Files to REVIEW:            126
    Files to SKIP:              2942
    Files with syntax errors:   135

    TOTAL UNIQUE AGENTS:        1260
    TOTAL RESTORATION FILES:    2697


================================================================================
TOP 20 RESTORATION COMMANDS
================================================================================

cp "archives\apps_lic\L1_cognition\P1_retrieve\lic_vector_memory.py" "apps_shared/lic_vector_memory.py"

cp "archives\apps_lic\L1_cognition\P1_retrieve\check_outreach\enforce_outreach_boundaries.py" "apps_lic/engines/enforce_outreach_boundaries.py"

cp "archives\apps_lic\L1_cognition\P1_retrieve\check_outreach\validate_outreach_constraints.py" "apps_lic/engines/validate_outreach_constraints.py"

cp "archives\apps_lic\L1_cognition\P2_inspect\check_message_quality.py" "apps_lic/engines/check_message_quality.py"

cp "archives\apps_lic\L1_cognition\P2_inspect\validate_generated_message.py" "apps_lic/engines/validate_generated_message.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\check_message_compliance.py" "apps_lic/engines/check_message_compliance.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\enforce_message_contracts.py" "apps_lic/engines/enforce_message_contracts.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\lic_archetypes.py" "apps_lic/engines/lic_archetypes.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\lic_cta_patterns.py" "apps_lic/engines/lic_cta_patterns.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\merge_outreach_history.py" "apps_lic/engines/merge_outreach_history.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\serialize_outreach_context.py" "apps_lic/engines/serialize_outreach_context.py"

cp "archives\apps_lic\L1_cognition\P3_aggregate\validate_message_schema.py" "apps_lic/engines/validate_message_schema.py"

cp "archives\apps_lic\L1_cognition\P4_safety\check_outreach\apply_outreach_safety_policy.py" "apps_lic/engines/apply_outreach_safety_policy.py"

cp "archives\apps_lic\L1_cognition\P4_safety\manage_outreach_costs\track_outreach_generation_cost.py" "apps_lic/engines/track_outreach_generation_cost.py"

cp "archives\apps_lic\L2_execution\apply_lic_execution_safety.py" "apps_lic/engines/apply_lic_execution_safety.py"

cp "archives\apps_lic\L2_execution\lic_code_interpreter.py" "apps_lic/engines/lic_code_interpreter.py"

cp "archives\apps_lic\L2_execution\lic_company_research_executor.py" "apps_lic/engines/lic_company_research_executor.py"

cp "archives\apps_lic\L2_execution\lic_contact_research_executor.py" "apps_lic/engines/lic_contact_research_executor.py"

cp "archives\apps_rg\L1_cognition\P1_retrieve\check_resume\enforce_resume_boundaries.py" "apps_rg/engines/enforce_resume_boundaries.py"

cp "archives\apps_rg\L1_cognition\P1_retrieve\check_resume\safety_validate_resume_constraints.py" "apps_rg/engines/safety_validate_resume_constraints.py"
