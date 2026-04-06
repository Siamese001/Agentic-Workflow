# apps_* Directories - Recursive Deep Analysis

## Grand Totals (apps_* only)

| Directory | Files | Issues | Root Violations | Dead Code | Misplaced |
|-----------|-------|--------|-----------------|-----------|-----------|
| apps_underwriting_ai | 82 | 2 | 2 | 2 | 2 |
| apps_eval | 68 | 10 | 8 | 10 | 8 |
| apps_exec | 67 | 12 | 8 | 12 | 8 |
| apps_lic | 140 | 15 | 1 | 15 | 1 |
| apps_research | 63 | 10 | 8 | 10 | 8 |
| apps_rfp | 65 | 10 | 8 | 10 | 8 |
| apps_rg | 170 | 16 | 1 | 16 | 1 |
| apps_shared | 272 | 41 | 1 | 41 | 1 |

**Total files: 927 | Files with issues: 116 | Root violations: 37**

---

## apps_underwriting_ai/

Files: 82 | Issues: 2 | Root violations: 2

- tests\test_parsers.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_validators.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest

---

## apps_eval/

Files: 68 | Issues: 10 | Root violations: 8

- config\__init__.py -- DEAD_IMPORTS(2)
  - dead import L5: apps_eval.config.agent_spec_config.EvalAgentSpecs
  - dead import L5: apps_eval.config.agent_spec_config.load_eval_specs
- engines\scenario_runner.py -- UNUSED_IMPORTS(1)
  - unused import L410: PolicyHashViolation
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_eval.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_eval.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_eval.outputs.run_summary_renderer.RunSummaryRenderer
  - dead import L4: apps_eval.outputs.scorecard_renderer.ScorecardRenderer
- services\__init__.py -- DEAD_IMPORTS(9)
  - dead import L8: apps_eval.services.benchmark_runner_service.BenchmarkRunnerService
  - dead import L9: apps_eval.services.coverage_analyzer_service.CoverageAnalyzerService
  - dead import L10: apps_eval.services.metric_collector_service.MetricCollectorService
  - dead import L11: apps_eval.services.quality_assessor_service.QualityAssessorService
  - dead import L12: apps_eval.services.regression_detector_service.RegressionDetectorService
  - dead import L13: apps_eval.services.repo_signal_service.RepoSignalService
- tests\test_eval_orchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_evaluation_engines.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_quality_services.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(11)
  - dead import L3: apps_eval.types.eval_types.EvalConfig
  - dead import L3: apps_eval.types.eval_types.EvalRequest
  - dead import L3: apps_eval.types.eval_types.EvalResult
  - dead import L3: apps_eval.types.eval_types.EvalRunSummary
  - dead import L3: apps_eval.types.eval_types.EvalStatus
  - dead import L3: apps_eval.types.eval_types.RegressionRecord
- validators\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_eval.validators.compliance_validator.ComplianceValidator
  - dead import L4: apps_eval.validators.quality_gate_validator.QualityGateValidator

---

## apps_exec/

Files: 67 | Issues: 12 | Root violations: 8

- config\__init__.py -- DEAD_IMPORTS(2)
  - dead import L5: apps_exec.config.agent_spec_config.ExecAgentSpecs
  - dead import L5: apps_exec.config.agent_spec_config.load_exec_specs
- config\knowledge_base.py -- UNUSED_IMPORTS(12)
  - unused import L7: ExecBriefGlobalRule
  - unused import L7: ExecBriefNodeEntry
  - unused import L7: ExecBriefPromptEntry
  - unused import L7: ExecSovereignKnowledge
  - unused import L7: FROZEN_SNAPSHOT
  - unused import L7: get_global_rule
- engines\__init__.py -- DEAD_IMPORTS(1)
  - dead import L3: apps_exec.engines.base_exec_engine.BaseExecEngine
- engines\base_exec_engine.py -- DEAD_IMPORTS(1)
  - dead import L31: pydantic.BaseModel
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_exec.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_exec.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(3)
  - dead import L3: apps_exec.outputs.brief_renderer.BriefRenderer
  - dead import L3: apps_exec.outputs.brief_renderer.BriefSummaryRenderer
  - dead import L4: apps_exec.outputs.section_renderer.SectionRenderer
- outputs\brief_renderer.py -- DEAD_IMPORTS(1)
  - dead import L16: apps_exec.types.BriefSection
- reasoning\ExecOrchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L32: AppsQwenPromptConfig
- tests\test_exec_engines.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_exec_orchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_exec_services.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(11)
  - dead import L3: apps_exec.types.exec_types.AudiencePersona
  - dead import L3: apps_exec.types.exec_types.BriefSection
  - dead import L3: apps_exec.types.exec_types.BriefStatus
  - dead import L3: apps_exec.types.exec_types.BriefTone
  - dead import L3: apps_exec.types.exec_types.CapabilityEvidence
  - dead import L3: apps_exec.types.exec_types.EmphasisArea

---

## apps_lic/

Files: 140 | Issues: 15 | Root violations: 1

- config\archetype_indicator_config.py -- DEAD_IMPORTS(1)
  - dead import L10: apps_shared.config.pipeline_constants_config.MAX_RETRIES
- config\knowledge_base.py -- UNUSED_IMPORTS(12)
  - unused import L7: FROZEN_SNAPSHOT
  - unused import L7: LicGlobalRule
  - unused import L7: LicNodeEntry
  - unused import L7: LicPromptEntry
  - unused import L7: LicSovereignKnowledge
  - unused import L7: get_global_rule
- config\loader_config.py -- DEAD_IMPORTS(1)
  - dead import L11: apps_shared.config.pipeline_constants_config.MAX_RETRIES
- config\reasoning_toggles_config.py -- UNUSED_IMPORTS(1)
  - unused import L178: MAX_RETRIES
- config\retry_policy_config.py -- UNUSED_IMPORTS(1)
  - unused import L174: MAX_RETRIES
- engines\__init__.py -- DEAD_IMPORTS(9)
  - dead import L10: apps_lic.reasoning.ExecutiveStrategyAgent.ExecutiveStrategyAgent
  - dead import L10: apps_lic.reasoning.ExecutiveStrategyAgent.get_exec_interviewer_profile
  - dead import L10: apps_lic.reasoning.ExecutiveStrategyAgent.get_exec_shadow_audit
  - dead import L10: apps_lic.reasoning.ExecutiveStrategyAgent.get_exec_strategy_roadmap
  - dead import L24: apps_lic.reasoning.HOPPipelineExecutor.HOPPipelineExecutor
  - dead import L29: apps_lic.reasoning.LICValidationExecutor.LICValidationExecutor
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_lic.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_lic.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(4)
  - dead import L3: apps_lic.outputs.campaign_renderer.CampaignRenderer
  - dead import L3: apps_lic.outputs.campaign_renderer.CampaignSummaryRenderer
  - dead import L4: apps_lic.outputs.draft_renderer.DraftRenderer
  - dead import L4: apps_lic.outputs.draft_renderer.ValidationReportRenderer
- outputs\campaign_renderer.py -- DEAD_IMPORTS(1)
  - dead import L16: apps_lic.types.DraftPackage
- reasoning\GovernanceShieldAgent.py -- UNUSED_IMPORTS(1)
  - unused import L26: AppsQwenPromptConfig
- tests\test_lic_reasoning.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_lic_validators.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(13)
  - dead import L3: apps_lic.types.lic_types.CampaignConfig
  - dead import L3: apps_lic.types.lic_types.CampaignRequest
  - dead import L3: apps_lic.types.lic_types.CampaignResult
  - dead import L3: apps_lic.types.lic_types.CampaignRunSummary
  - dead import L3: apps_lic.types.lic_types.CampaignStatus
  - dead import L3: apps_lic.types.lic_types.ComplianceLevel
- utils\lic_agent_base_util.py -- UNUSED_IMPORTS(3)
  - unused import L112: MetaLearningMixin
  - unused import L120: SemanticCacheMixin
  - unused import L128: EmbeddingMixin
- utils\mixins_util.py -- DEAD_IMPORTS(3)
  - dead import L9: agentic_core.mixins.healer_mixin.HealerMixin
  - dead import L10: agentic_core.mixins.mcp_hardened_mixin.MCPHardenedMixin
  - dead import L11: agentic_core.mixins.subatomic_testing_mixin.SubatomicTestingMixin

---

## apps_research/

Files: 63 | Issues: 10 | Root violations: 8

- config\__init__.py -- DEAD_IMPORTS(2)
  - dead import L5: apps_research.config.agent_spec_config.ResearchAgentSpecs
  - dead import L5: apps_research.config.agent_spec_config.load_research_specs
- config\knowledge_base.py -- UNUSED_IMPORTS(12)
  - unused import L7: FROZEN_SNAPSHOT
  - unused import L7: ResearchGlobalRule
  - unused import L7: ResearchNodeEntry
  - unused import L7: ResearchPromptEntry
  - unused import L7: ResearchSovereignKnowledge
  - unused import L7: get_global_rule
- engines\__init__.py -- DEAD_IMPORTS(1)
  - dead import L3: apps_research.engines.base_research_engine.BaseResearchEngine
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_research.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_research.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(3)
  - dead import L3: apps_research.outputs.research_renderer.ResearchRenderer
  - dead import L3: apps_research.outputs.research_renderer.ResearchSummaryRenderer
  - dead import L4: apps_research.outputs.section_renderer.SectionRenderer
- outputs\research_renderer.py -- DEAD_IMPORTS(1)
  - dead import L16: apps_research.types.ResearchSection
- reasoning\ResearchOrchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L31: AppsQwenPromptConfig
- services\__init__.py -- DEAD_IMPORTS(9)
  - dead import L8: apps_research.services.citation_manager_service.CitationManagerService
  - dead import L9: apps_research.services.content_harvester_service.ContentHarvesterService
  - dead import L10: apps_research.services.credibility_scorer_service.CredibilityScorerService
  - dead import L11: apps_research.services.insight_extractor_service.InsightExtractorService
  - dead import L12: apps_research.services.knowledge_integrator_service.KnowledgeIntegratorService
  - dead import L13: apps_research.services.repo_signal_service.RepoSignalService
- tests\test_research_reasoning.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(11)
  - dead import L3: apps_research.types.research_types.ArtifactMode
  - dead import L3: apps_research.types.research_types.AudienceStyle
  - dead import L3: apps_research.types.research_types.ClaimType
  - dead import L3: apps_research.types.research_types.ComparisonRow
  - dead import L3: apps_research.types.research_types.ResearchConfig
  - dead import L3: apps_research.types.research_types.ResearchRequest

---

## apps_rfp/

Files: 65 | Issues: 10 | Root violations: 8

- config\__init__.py -- DEAD_IMPORTS(2)
  - dead import L5: apps_rfp.config.agent_spec_config.RfpAgentSpecs
  - dead import L5: apps_rfp.config.agent_spec_config.load_rfp_specs
- config\knowledge_base.py -- UNUSED_IMPORTS(12)
  - unused import L7: FROZEN_SNAPSHOT
  - unused import L7: RfpGlobalRule
  - unused import L7: RfpNodeEntry
  - unused import L7: RfpPromptEntry
  - unused import L7: RfpSovereignKnowledge
  - unused import L7: get_global_rule
- engines\__init__.py -- DEAD_IMPORTS(1)
  - dead import L3: apps_rfp.engines.base_rfp_engine.BaseRfpEngine
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_rfp.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_rfp.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(3)
  - dead import L3: apps_rfp.outputs.proposal_renderer.ProposalRenderer
  - dead import L3: apps_rfp.outputs.proposal_renderer.ProposalSummaryRenderer
  - dead import L4: apps_rfp.outputs.section_renderer.SectionRenderer
- outputs\proposal_renderer.py -- DEAD_IMPORTS(1)
  - dead import L16: apps_rfp.types.RiskItem
- reasoning\RfpOrchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L31: AppsQwenPromptConfig
- services\__init__.py -- DEAD_IMPORTS(9)
  - dead import L8: apps_rfp.services.capability_mapper_service.CapabilityMapperService
  - dead import L9: apps_rfp.services.compliance_checker_service.ComplianceCheckerService
  - dead import L10: apps_rfp.services.differentiation_analyzer_service.DifferentiationAnalyzerService
  - dead import L11: apps_rfp.services.proposal_architect_service.ProposalArchitectService
  - dead import L12: apps_rfp.services.repo_signal_service.RepoSignalService
  - dead import L13: apps_rfp.services.requirement_parser_service.RequirementParserService
- tests\test_rfp_reasoning.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(11)
  - dead import L3: apps_rfp.types.rfp_types.ArchitecturePosture
  - dead import L3: apps_rfp.types.rfp_types.AssumptionItem
  - dead import L3: apps_rfp.types.rfp_types.ProposalSection
  - dead import L3: apps_rfp.types.rfp_types.ProposalStatus
  - dead import L3: apps_rfp.types.rfp_types.RfpConfig
  - dead import L3: apps_rfp.types.rfp_types.RfpRequest

---

## apps_rg/

Files: 170 | Issues: 16 | Root violations: 1

- config\agent_spec_config.py -- UNUSED_IMPORTS(1)
  - unused import L238: MAX_RETRIES
- config\reasoning_toggles_config.py -- UNUSED_IMPORTS(1)
  - unused import L178: MAX_RETRIES
- engines\__init__.py -- DEAD_IMPORTS(1)
  - dead import L9: apps_rg.engines.base_rg_engine.BaseRGEngine
- engines\base_rg_engine.py -- UNUSED_IMPORTS(1)
  - unused import L79: AgentOutputContract
- engines\sovereign_context.py -- DEAD_IMPORTS(1)
  - dead import L1: apps_rg.types.SovereignContext.SovereignContext
- integrations\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: apps_rg.integrations.execution_adapter.ExecutionAdapter
  - dead import L4: apps_rg.integrations.observability_adapter.ObservabilityAdapter
- outputs\__init__.py -- DEAD_IMPORTS(3)
  - dead import L3: apps_rg.outputs.resume_renderer.ResumeRenderer
  - dead import L3: apps_rg.outputs.resume_renderer.ResumeSummaryRenderer
  - dead import L4: apps_rg.outputs.section_renderer.SectionRenderer
- outputs\resume_renderer.py -- DEAD_IMPORTS(1)
  - dead import L16: apps_rg.types.ResumeSection
- reasoning\DispatchResumeToolsAgent.py -- DEAD_IMPORTS(2)
  - dead import L16: titanium_rag_pipeline.get_titanium_search_tool
  - dead import L16: titanium_rag_pipeline.get_titanium_search_with_sources
- reasoning\RgResumeOrchestrator.py -- UNUSED_IMPORTS(2)
  - unused import L28: AppsQwenConfig
  - unused import L28: AppsQwenPromptConfig
- tests\test_rg_engines.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_rg_reasoning.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(11)
  - dead import L3: apps_rg.types.rg_types.ExperienceEntry
  - dead import L3: apps_rg.types.rg_types.ExperienceLevel
  - dead import L3: apps_rg.types.rg_types.ResumeConfig
  - dead import L3: apps_rg.types.rg_types.ResumeFormat
  - dead import L3: apps_rg.types.rg_types.ResumeRequest
  - dead import L3: apps_rg.types.rg_types.ResumeResult
- types\resume_analysis_plan_types.py -- UNUSED_IMPORTS(1)
  - unused import L16: MAX_RETRIES
- utils\rg_core_mixins.py -- DEAD_IMPORTS(1)
  - dead import L1: agentic_core.mixins.mcp_hardened_mixin.MCPHardenedMixin
- utils\rg_core_mixins_util.py -- DEAD_IMPORTS(3)
  - dead import L9: agentic_core.mixins.healer_mixin.HealerMixin
  - dead import L10: agentic_core.mixins.mcp_hardened_mixin.MCPHardenedMixin
  - dead import L11: agentic_core.mixins.subatomic_testing_mixin.SubatomicTestingMixin

---

## apps_shared/

Files: 272 | Issues: 41 | Root violations: 1

- config\__init__.py -- DEAD_IMPORTS(10)
  - dead import L5: apps_shared.config.operational_config.OPERATIONAL_ALLOWED_DUPLICATES
  - dead import L5: apps_shared.config.operational_config.OPERATIONAL_EXCLUDED_DIRS
  - dead import L5: apps_shared.config.operational_config.OPERATIONAL_SCAN_TARGETS
  - dead import L5: apps_shared.config.operational_config.is_allowed_duplicate
  - dead import L5: apps_shared.config.operational_config.is_excluded_path
  - dead import L5: apps_shared.config.operational_config.should_scan_directory
- config\environment_config.py -- UNUSED_IMPORTS(1)
  - unused import L40: MAX_RETRIES
- config\integration_config.py -- DEAD_IMPORTS(1)
  - dead import L14: apps_shared.config.pipeline_constants_config.MAX_RETRIES
- config\operational_config.py -- UNUSED_IMPORTS(1)
  - unused import L36: MAX_RETRIES
- config\routing_tier_config.py -- UNUSED_IMPORTS(1)
  - unused import L174: MAX_RETRIES
- config\titanium_search_tool_config.py -- DEAD_IMPORTS(1)
  - dead import L11: apps_shared.config.pipeline_constants_config.MAX_RETRIES
- data_adapters\__init__.py -- DEAD_IMPORTS(2)
  - dead import L3: repo_signal_adapter.RepoSignalAdapter
  - dead import L3: repo_signal_adapter.RepoSignalSnapshot
- enforcement\FewshotregistryStrategy.py -- UNUSED_IMPORTS(1)
  - unused import L179: MAX_RETRIES
- mixins\apps_tracing_mixin.py -- UNUSED_IMPORTS(1)
  - unused import L40: TracingMixin
- reasoning\InfrastructureUpgradesOrchestrator.py -- UNUSED_IMPORTS(1)
  - unused import L175: MAX_RETRIES
- reasoning\bulkhead_manager.py -- DEAD_IMPORTS(3)
  - dead import L2: apps_shared.enforcement.bulkhead_manager.BulkheadManager
  - dead import L2: apps_shared.enforcement.bulkhead_manager.TaskPriority
  - dead import L2: apps_shared.enforcement.bulkhead_manager.get_bulkhead_manager
- reasoning\circuit_breaker.py -- DEAD_IMPORTS(3)
  - dead import L2: apps_shared.enforcement.circuit_breaker.CircuitBreakerConfig
  - dead import L2: apps_shared.enforcement.circuit_breaker.CircuitBreakerRegistry
  - dead import L2: apps_shared.enforcement.circuit_breaker.get_circuit_breaker_registry
- reasoning\dead_letter_queue.py -- DEAD_IMPORTS(3)
  - dead import L2: apps_shared.enforcement.dead_letter_queue.DeadLetterQueue
  - dead import L2: apps_shared.enforcement.dead_letter_queue.FailureReason
  - dead import L2: apps_shared.enforcement.dead_letter_queue.get_dead_letter_queue
- reasoning\event_bus_integration.py -- UNUSED_IMPORTS(7)
  - unused import L2: EventType
  - unused import L2: SystemEvent
  - unused import L3: HardenedEventBus
  - unused import L3: get_hardened_event_bus
  - unused import L3: hardened_event_publisher
  - unused import L3: publish_hardened_event
- reasoning\core\event_bus.py -- DEAD_IMPORTS(4)
  - dead import L2: apps_shared.enforcement.core.event_bus.EventBus
  - dead import L2: apps_shared.enforcement.core.event_bus.EventType
  - dead import L2: apps_shared.enforcement.core.event_bus.SystemEvent
  - dead import L2: apps_shared.enforcement.core.event_bus.get_event_bus
- reasoning\core\provenance_tracker.py -- DEAD_IMPORTS(7)
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.ArtifactLineage
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.ProvenanceContext
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.ProvenanceTracker
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.SourceCitation
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.get_provenance_tracker
  - dead import L2: apps_shared.enforcement.ProvenancetrackerStrategy.provenance_tracked
- scripts\__init__.py -- DEAD_IMPORTS(6)
  - dead import L8: apps_shared.scripts.io_operations_validator.DataCollectionOperations
  - dead import L8: apps_shared.scripts.io_operations_validator.FileOperations
  - dead import L8: apps_shared.scripts.io_operations_validator.MonitoringOperations
  - dead import L13: apps_shared.scripts.script_bridge.ScriptBridge
  - dead import L13: apps_shared.scripts.script_bridge.ScriptResult
  - dead import L13: apps_shared.scripts.script_bridge.get_script_bridge
- scripts\fix_all_indentation_errors.py -- UNUSED_IMPORTS(3)
  - unused import L2: fix_all_indentation
  - unused import L5: fix_all_files
  - unused import L8: main
- scripts\meta_learning_bridge.py -- DEAD_IMPORTS(3)
  - dead import L1: system_learning.scripts.meta_learning_bridge.emit_app_signal_aggregate
  - dead import L1: system_learning.scripts.meta_learning_bridge.emit_app_signal_event
  - dead import L1: system_learning.scripts.meta_learning_bridge.propose_from_signal_aggregate
- scripts\meta_learning_operator.py -- DEAD_IMPORTS(2)
  - dead import L1: system_learning.scripts.meta_learning_operator.render_meta_learning_audit_pack
  - dead import L1: system_learning.scripts.meta_learning_operator.run_meta_learning_operator
- services\__init__.py -- DEAD_IMPORTS(3)
  - dead import L8: apps_shared.services.config_loader_service.ConfigLoaderService
  - dead import L9: apps_shared.services.environment_validator_service.EnvironmentValidatorService
  - dead import L10: apps_shared.services.operational_scanner_service.OperationalScannerService
- tests\test_shared_services.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- tests\test_spine_adapters.py -- UNUSED_IMPORTS(1)
  - unused import L3: pytest
- types\__init__.py -- DEAD_IMPORTS(1)
  - dead import L4: apps_shared.types.risk_level_types.RiskLevel
- types\config_format_types.py -- UNUSED_IMPORTS(1)
  - unused import L295: MAX_RETRIES
- types\config_type_types.py -- UNUSED_IMPORTS(1)
  - unused import L294: MAX_RETRIES
- types\hardened_gemini_executor_types.py -- UNUSED_IMPORTS(1)
  - unused import L513: SourceDocument
- utils\async_coordinator_util.py -- UNUSED_IMPORTS(1)
  - unused import L181: MAX_RETRIES
- utils\config_environment_util.py -- UNUSED_IMPORTS(1)
  - unused import L250: MAX_RETRIES
- utils\config_loader_util.py -- UNUSED_IMPORTS(1)
  - unused import L89: MAX_RETRIES
- utils\feedback_category_util.py -- UNUSED_IMPORTS(1)
  - unused import L273: MAX_RETRIES
- utils\golden_state_datasets_util.py -- DEAD_IMPORTS(1)
  - dead import L7: apps_shared.config.pipeline_constants_config.MAX_RETRIES
- utils\graph_rag_fusion_util.py -- UNUSED_IMPORTS(1)
  - unused import L241: MAX_RETRIES
- utils\input_validator_util.py -- UNUSED_IMPORTS(1)
  - unused import L181: MAX_RETRIES
- utils\late_interaction_reranker_util.py -- UNUSED_IMPORTS(1)
  - unused import L223: torch
- utils\rank_observability_components_util.py -- UNUSED_IMPORTS(1)
  - unused import L76: MAX_RETRIES
- utils\request_type_util.py -- UNUSED_IMPORTS(1)
  - unused import L337: MAX_RETRIES
- utils\vllm_advanced_features.py -- UNUSED_IMPORTS(3)
  - unused import L18: AppsQwenInferenceWorker
  - unused import L24: AppsQwenModelConfig
  - unused import L24: AppsQwenPromptConfig
- utils\vllm_shared_utils.py -- UNUSED_IMPORTS(1)
  - unused import L20: AppsQwenPromptConfig
- validators\__init__.py -- DEAD_IMPORTS(7)
  - dead import L3: apps_shared.validators.cache_validator.CACHE_KEY_VERSION
  - dead import L3: apps_shared.validators.cache_validator.generate_llm_cache_key
  - dead import L3: apps_shared.validators.cache_validator.generate_llm_cache_key_with_fingerprint
  - dead import L3: apps_shared.validators.cache_validator.should_invalidate_cache
  - dead import L9: apps_shared.validators.validation_validator.ExecutionResult
  - dead import L9: apps_shared.validators.validation_validator.Validation
- validators\resume_prompts_validator.py -- UNUSED_IMPORTS(4)
  - unused import L99: CompetitiveAnalysisConfig
  - unused import L101: MasterResumeIndex
  - unused import L101: RAGMission
  - unused import L101: ThematicAnalysis
