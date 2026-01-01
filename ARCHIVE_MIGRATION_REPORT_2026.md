# Zero-Loss Archive Migration Analysis Report

**Generated:** 2026-01-01 12:09:22
**Project:** Agentic-Workflow
**Archives Analyzed:** runtime/, schemas/, shared/

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Files | 258 |
| Total LOC | 78,807 |
| Python Files | 247 |
| Total Classes | 880 |

### Recommended Actions

| Action | Count |
|--------|-------|
| REVIEW | 150 |
| MIGRATE | 99 |
| DELETE | 6 |
| MERGE | 3 |

### Risk Distribution

| Risk Level | Count |
|------------|-------|
| MEDIUM | 159 |
| LOW | 99 |

### Compliance Issues

| Issue | Count | Files |
|-------|-------|-------|
| Snake_case Classes | 10 | executive_title_composer.py, gap_closure_architect.py, k1_routing_agent.py... |
| Hardcoded Credentials | 0 | None |
| Raw Prompt Strings | 6 | reflection_engine.py, persona_router.py, architecture_visualizer_agent.py... |

## archives/runtime/ Analysis

**Files:** 141 | **LOC:** 62,797

| Path | Size | LOC | Classes | Action | Target | Risk |
|------|------|-----|---------|--------|--------|------|
| `runtime\03_runtime_freeze_report.json` | 21,203B | 426 | - | **MIGRATE** | `agentic_core/runtime/` | LOW |
| `runtime\__init__.py` | 172B | 8 | - | **DELETE** | `agentic_core/runtime/` | LOW |
| `runtime\core\cognitive_contracts.py` | 16,810B | 511 | PlanQualityError, ConsistencyError, ContractStage... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `runtime\core\dynamic_dag_manager.py` | 26,856B | 714 | GraphTransaction, MutationAction, HopSpec... | **MIGRATE** | `agentic_core/L3_orchestration/` | LOW |
| `runtime\core\few_shot_registry.py` | 14,155B | 376 | ContextType, FewShotExample, FewShotRegistry... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\injection_patterns_extended.py` | 13,592B | 284 | - | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\instructional_injections.py` | 33,558B | 837 | InstructionalLayer, InstructionalInjectionType, StageMapping | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\node_negotiator.py` | 17,634B | 513 | NegotiationMessage, NegotiationRound, NegotiationConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\prompt_assembler.py` | 19,321B | 540 | PromptComponents, PromptTemplate, PromptAssembler | **MIGRATE** | `agentic_core/prompt_governance/` | LOW |
| `runtime\core\prompt_enhancer.py` | 14,606B | 411 | EnhancementConfig, PromptEnhancer | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\prompt_injection_loader.py` | 23,245B | 583 | PromptInjectionLoader | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\quality\feedback_loop.py` | 19,081B | 525 | FeedbackType, QualityFeedback, QualityTrend... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\quality\signal_enhancer.py` | 25,008B | 723 | SignalQuality, QualityThresholds, ClaimAnalysis... | **MIGRATE** | `agentic_core/runtime/shared_runtime/` | LOW |
| `runtime\core\reflection_engine.py` | 17,901B | 512 | CritiqueResult, ValidationCriterion, ReflectionConfig... | **MIGRATE** | `agentic_core/runtime/shared_runtime/` | LOW |
| `runtime\core\resilience\async_coordinator.py` | 15,784B | 483 | TaskState, TaskInfo, AsyncCoordinator | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `runtime\core\resilience\circuit_breaker.py` | 12,537B | 357 | CircuitState, CircuitOpenError, CriticalServiceFailure... | **MERGE** | `agentic_core/L4_resilience/circuit_breaker.py` | MEDIUM |
| `runtime\core\resilience\dag_safety.py` | 13,210B | 395 | MutationPhase, StateSnapshot, DAGSafetyManager... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `runtime\core\resilience\memory_manager.py` | 16,941B | 485 | PruningStrategy, MemoryLimits, ContextItem... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `runtime\core\resilience\rate_limiter.py` | 14,090B | 427 | RateLimitStrategy, RateLimitConfig, RateLimitExceeded... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `runtime\core\resilience\resource_manager.py` | 14,765B | 443 | ResourceType, ResourceInfo, ResourceManager... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `runtime\core\security\input_sanitizer.py` | 9,843B | 268 | SecurityIntegrityError, InputSanitizer | **REVIEW** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\input_validator.py` | 18,091B | 510 | ValidationType, ValidationRule, InputValidationError... | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\secure_checkpoint.py` | 11,938B | 318 | CheckpointIntegrityError, SecureCheckpointManager, CheckpointManagerFactory | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\secure_config.py` | 15,505B | 467 | SecureConfigManager | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\secure_error.py` | 12,739B | 372 | SecureError, SecurityError, ConfigurationError... | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\secure_logger.py` | 9,637B | 266 | SecureLogger, SecureLoggerAdapter, SecureLogContext | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\security\test_input_sanitizer.py` | 9,486B | 226 | TestInputSanitizer | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `runtime\core\service_container.py` | 7,211B | 210 | ServiceNotFoundError, ServiceContainer, Service | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\shared_models.py` | 7,029B | 194 | MicroStage, HopState, RetryPolicy... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `runtime\core\subatomic_hop.py` | 38,069B | 940 | InputValidationError, StageExecutionError, QualityGateFailure... | **DELETE** | `agentic_core/runtime/shared_runtime/subatomic_hop.py` | LOW |
| `runtime\core\test_dynamic_dag.py` | 21,864B | 595 | TestDAGMutator, TestDAGManager, TestMutationIntegration... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\test_instructional_injections.py` | 15,781B | 382 | TestInstructionalInjections, TestPromptInjectionLoaderIntegration, TestSubatomicHopIntegration... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\test_node_negotiation.py` | 16,480B | 452 | TestNodeNegotiator, TestSubatomicHopNegotiation, TestNegotiationIntegration... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\test_prompt_injection_loader.py` | 14,139B | 411 | TestPromptInjectionLoader, TestInjectionPatterns, TestIntegration... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\test_reflection_engine.py` | 11,874B | 342 | TestReflectionEngine, TestSubatomicHopReflection, TestReflectionIntegration... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\core\test_subatomic_hop.py` | 13,068B | 382 | TestSubatomicHop, TestSubatomicHopIntegration | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\engine\resume\enhancement_integration.py` | 15,374B | 397 | ResumeEnhancementOrchestrator | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\engine\resume\evidence_injector.py` | 14,413B | 402 | EvidenceType, EvidenceItem, EvidenceInjector | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\engine\resume\persona_router.py` | 18,543B | 477 | ArchetypeBase, PsychometricProfile, ReaderPersona... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\engine\strategy\competitor_recon.py` | 16,098B | 433 | CompetitivePosition, Company, ReconSignal... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\prompts\functional_personas.py` | 14,706B | 354 | PersonaTemplate, PromptSanitizer | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\registry\agent_capabilities.py` | 18,033B | 491 | AgentRole, AgentCapability, AgentSpec... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\registry\migration_tools.py` | 14,640B | 425 | KNodeScanner, KNodeMigrator, MigrationValidator | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\__init__.py` | 8,593B | 377 | - | **REVIEW** | `agentic_core/runtime/` | LOW |
| `runtime\shared\adaptive_recovery_loop.py` | 9,577B | 266 | FailureType, RecoveryAction, FailureEvent... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\adaptive_retrieval_gate.py` | 10,768B | 289 | RetrievalDecision, AdaptiveRetrievalGate | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\agent_base.py` | 7,996B | 237 | ReasoningStrategy, ReasoningConfig, Agent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\agent_executor.py` | 21,573B | 583 | AgentConfig, AgentMessage, AgentResponse... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\architecture_visualizer_agent.py` | 12,527B | 338 | DiagramType, DiagramNode, DiagramArtifact... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\brand_voice_enforcer.py` | 22,936B | 617 | ToneVoice, ToneSettings, ToneViolation... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\bulkhead_manager.py` | 20,167B | 611 | TaskPriority, BulkheadConfig, BulkheadMetrics... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\cache.py` | 2,676B | 91 | - | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `runtime\shared\cache_clients.py` | 7,809B | 307 | RedisConfig | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `runtime\shared\circuit_breaker.py` | 14,712B | 450 | CircuitState, CircuitBreakerConfig, RequestResult... | **MERGE** | `agentic_core/L4_resilience/circuit_breaker.py` | MEDIUM |
| `runtime\shared\competitor_recon_agent.py` | 16,893B | 469 | CompetitorMove, StrategicHook, IntelProvider... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\contextual_compressor.py` | 11,464B | 306 | CompressionResult, ContextualCompressor | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\contrastive_cache.py` | 16,545B | 482 | CacheEntry, ContrastiveSemanticCache, NullCache | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `runtime\shared\core\checkpoint_manager.py` | 23,256B | 752 | CheckpointStorage, CheckpointConfig, CheckpointStorageBackend... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\core\envelope.py` | 18,442B | 532 | PipelineStageStatus, PayloadType, PayloadBase... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\core\event_bus.py` | 24,921B | 769 | EventType, SystemEvent, EventBus... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\core\model_router.py` | 23,473B | 741 | ModelTier, TaskType, ModelConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\core\provenance_tracker.py` | 19,408B | 602 | SourceCitation, ArtifactLineage, ProvenanceTracker... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\cultural_decoder_agent.py` | 20,046B | 470 | WritingStyle, CompanyDNA, CulturallyAlignedContent... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\dead_letter_queue.py` | 21,921B | 678 | FailureReason, DeadLetterStatus, DeadLetterItem... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\event_bus_integration.py` | 13,899B | 436 | HardenedEventBus | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\evidence_ranker.py` | 19,681B | 487 | RankedEvidence, EvidenceRanker | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\execution_orchestrator.py` | 9,668B | 281 | ExecutionArtifact, ExecutionTrace, ExecutionOrchestrator | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\executive_brief_agent.py` | 28,180B | 686 | BriefSection, ExecutiveBrief, ExecutiveBriefAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\executive_title_composer.py` | 10,322B | 295 | HeadlineOutput, Executive_Title_Composer | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\fact_ledger.py` | 22,065B | 636 | FactStatus, Fact, VerificationResult... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\feedback_loop_orchestrator.py` | 19,278B | 491 | ConstraintFailureType, RegenerationCheckpoint, RegenerationResult... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\gap_closure_architect.py` | 14,342B | 397 | CompetencyItem, CompetenciesOutput, Gap_Closure_Architect | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\global_cache.py` | 19,685B | 663 | CacheEntry, L1MemoryCache, L2VectorStore... | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `runtime\shared\governance_shield_agent.py` | 15,513B | 385 | IndustrySensitivity, RiskProfile, SafetyProtocol... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\graphrag_fusion.py` | 21,998B | 596 | QueryType, FusionResult, CypherQueryGenerator... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\hardened_anthropic_executor.py` | 12,696B | 354 | HardenedAnthropicConfig, HardenedAnthropicExecutor | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\hardened_gemini_executor.py` | 22,708B | 646 | ContextOverflowError, CircuitBreakerOpenError, HardenedGeminiConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\hardened_openai_executor.py` | 12,537B | 361 | HardenedOpenAIConfig, HardenedOpenAIExecutor | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\health_check.py` | 21,141B | 588 | HealthStatus, ComponentType, HealthCheckResult... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\hybrid_scorer.py` | 23,198B | 556 | HybridScoreResult, HybridScorer | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\hyde_processor.py` | 20,092B | 516 | ExpansionStrategy, HyDEDocument, HyDEResult... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\infrastructure_integration.py` | 20,444B | 562 | InfrastructureOrchestrator, EventBusHealthChecker, ProvenanceHealthChecker... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\infrastructure_upgrades_integration.py` | 17,048B | 473 | InfrastructureUpgradesOrchestrator | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\input_guardrail.py` | 21,721B | 541 | GuardAction, GuardResult, InputGuardrail | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\integrity_gate_executor.py` | 12,967B | 362 | ValidationSeverity, GateType, ValidationRule... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\k1_routing_agent.py` | 12,866B | 339 | ArchetypeClassificationResult, RouteSelectionResult, K1Output... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\k3_message_body_agent.py` | 10,871B | 342 | K3Output, K3_MessageBodyAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\k5_cta_agent.py` | 8,015B | 263 | K5Output, K5_CTAAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\k5a_agent.py` | 11,419B | 324 | ProvenanceRule, K5AOutput, K5A_GenerationAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\k7_assembly_agent.py` | 9,778B | 313 | K7Output, K7_AssemblyAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\knowledge_graph_agent.py` | 27,711B | 741 | GraphContext, KnowledgeGraphAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\kx_executor.py` | 14,892B | 423 | KXExecutionContext, KXExecutionResult, KXNodeExecutor | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\kx_nodes.py` | 21,163B | 577 | KNodeType, ReasoningStrategy, RAGConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\late_interaction_reranker.py` | 10,889B | 298 | LateInteractionReranker, PassThroughReranker | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\mcp_tools.py` | 9,711B | 347 | MCPTool, MCPToolResult, MCPToolServer | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `runtime\shared\metric_augmenter.py` | 20,142B | 521 | ImpactCategory, BusinessImpact, AugmentedBullet... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\models.py` | 3,465B | 151 | LLMResponse, MessageType, AgentMessage... | **REVIEW** | `agentic_core/schemas/models/` | MEDIUM |
| `runtime\shared\multi_provider_clients.py` | 8,867B | 321 | Provider, ProviderConfig | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\observability_clients.py` | 7,726B | 272 | TracingConfig | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\onboarding_planner_agent.py` | 20,948B | 534 | PlanPhase, OnboardingPlan, OnboardingPlannerAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\outreach_validation_executor.py` | 16,773B | 473 | OutreachValidationExecutor | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\pre_mortem_agent.py` | 19,992B | 536 | RiskCategory, ImpactLevel, FailureMode... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\quality_standards.py` | 20,212B | 565 | StandardType, QualityDimension, QualityStandard... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\query_decomposer.py` | 11,708B | 306 | DecomposedQuery, SimpleAgentBase, QueryDecomposer... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\rate_limiter.py` | 18,907B | 591 | RateLimitStrategy, RateLimitExceeded, RateLimitConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\retrieval_grader.py` | 12,309B | 356 | GradeStatus, RetrievalGrade, RetrievalGrader... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\retry_policy.py` | 15,676B | 502 | RetryStrategy, RetryableError, NonRetryableError... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\routing\__init__.py` | 543B | 20 | - | **REVIEW** | `agentic_core/runtime/` | LOW |
| `runtime\shared\routing\factory.py` | 2,378B | 72 | - | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\routing\router.py` | 13,741B | 357 | AllProvidersDownError, HardenedRouter | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\routing\schema.py` | 4,353B | 118 | RoutingTier, RouteConfig | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\sdk_registry.py` | 12,366B | 405 | SDKCategory, SDKEntry, MockCollection... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\self_healing_formatter.py` | 22,497B | 678 | RepairStrategy, RepairResult, FormatRepair... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\signal_infrastructure.py` | 25,971B | 682 | EngineType, DomainConfig, DomainValidator... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\signal_quality_pipeline.py` | 18,988B | 471 | QualityAssessment, SignalQualityPipeline | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\signal_weighter.py` | 19,018B | 488 | SignalWeights, WeightingResult, SignalWeighter... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\stack_modernization_agent.py` | 14,514B | 345 | LegacyDiagnostic, MigrationThesis, StackModernizationAgent | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\state\__init__.py` | 613B | 21 | - | **REVIEW** | `agentic_core/runtime/` | LOW |
| `runtime\shared\state\atomic_manager.py` | 14,459B | 364 | StatePersistenceError, AtomicStateManager | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\state\factory.py` | 2,489B | 78 | - | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\state\schema.py` | 5,665B | 162 | BackendType, CheckpointMetadata, KNodeExecution... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\strategist_biowriter.py` | 10,237B | 286 | ExecutiveSummaryOutput, Strategist_BioWriter | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\talent_signal_enhancer.py` | 15,976B | 431 | TalentMetrics, TalentSignalEnhancer | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\temperature_components.py` | 24,697B | 616 | RiskLevel, SentimentMood, DepthScore... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_agentic_canon.py` | 20,246B | 540 | TestInputGuardrail, TestRetrievalGrader, TestWebSearchFallback... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_precision_layer.py` | 12,283B | 291 | PrecisionLayerTestSuite | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_reasoning_layer.py` | 13,308B | 322 | ReasoningLayerTestSuite | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_sota_layer.py` | 17,407B | 437 | SOTALayerTestSuite | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_titanium_integration.py` | 8,249B | 233 | - | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_titanium_pipeline.py` | 18,625B | 440 | TitaniumPipelineIntegrationTest | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\test_uber_signal_agents.py` | 12,823B | 299 | UberSignalTestSuite | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\titanium_rag_pipeline.py` | 27,069B | 664 | TitaniumRAGPipeline | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\titanium_search_tool.py` | 14,173B | 396 | - | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\tone_model.py` | 26,607B | 629 | ToneType, StyleProfile, GenerationConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\unified_executor.py` | 21,794B | 703 | ExecutionStatus, ExecutionContext, ExecutionResult... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\unified_feedback.py` | 21,675B | 583 | FeedbackCategory, CrossEngineFeedback, FeedbackAggregator... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\unified_formatter.py` | 21,147B | 686 | FormatType, FormatResult, FormatterStrategy... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\unified_signal_pipeline.py` | 47,176B | 1348 | PipelineStageType, PipelineContext, PipelineStage... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\validation_executor.py` | 26,807B | 707 | ValidationStatus, ValidationAction, RuleFailure... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\vector_store_clients.py` | 9,437B | 336 | VectorStoreProvider, ChromaConfig, QdrantConfig... | **REVIEW** | `agentic_core/runtime/` | MEDIUM |
| `runtime\shared\workflow_integration.py` | 10,640B | 348 | WorkflowContext, HopExecutionContext, WorkflowOrchestrator | **REVIEW** | `agentic_core/runtime/` | MEDIUM |

## archives/schemas/ Analysis

**Files:** 74 | **LOC:** 10,244

| Path | Size | LOC | Classes | Action | Target | Risk |
|------|------|-----|---------|--------|--------|------|
| `schemas\__init__.py` | 1,991B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\cache\__init__.py` | 1,981B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\cache\data_access\__init__.py` | 2,011B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\cache\data_access\get_schema_info.py` | 6,775B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_interfaces\__init__.py` | 908B | 41 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_interfaces\action_plane.py` | 4,472B | 156 | ActionCapability, ActionRequest, ActionResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_interfaces\cognitive_plane.py` | 4,679B | 153 | CognitiveCapability, PlanningRequest, PlanningResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_interfaces\orchestrator.py` | 6,788B | 234 | ExecutionPhase, OrchestratorConfig, ExecutionContext... | **MIGRATE** | `agentic_core/L3_orchestration/` | LOW |
| `schemas\core_models\__init__.py` | 63B | 1 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\budget_profile.py` | 431B | 17 | BudgetProfile | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\context_profile.py` | 422B | 14 | ContextProfile | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\golden_state_datasets.py` | 2,565B | 82 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\golden_state_models.py` | 1,422B | 64 | GoldenStateTestCase, JudgeVerdict, EvalResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\l4_types.py` | 3,482B | 109 | StateOperation, StateEventType, StatePath... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\llm_profile.py` | 811B | 24 | LLMProfile | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\meta_metacognition_models.py` | 677B | 28 | Hypothesis, MetacognitionReport | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\models.py` | 3,513B | 131 | ValidationSeverity, Provider, APICallStatus... | **REVIEW** | `agentic_core/schemas/models/` | MEDIUM |
| `schemas\core_models\safety_profile.py` | 519B | 18 | SafetyProfile | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\core_models\security_controls.py` | 2,041B | 74 | - | **MIGRATE** | `agentic_core/L5_safety/guardrails/` | MEDIUM |
| `schemas\core_models\simulation_models.py` | 400B | 23 | SimScenario, SimOutcome | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\__init__.py` | 63B | 1 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\app_tracker_schema.json` | 1,580B | 20 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\artist_constraints.json` | 2,081B | 66 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\artist_specs.json` | 8,710B | 220 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\hyphenation_rules.json` | 1,320B | 23 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\job_input.json` | 6,193B | 6 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\master_resume.json` | 14,603B | 141 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\prompts.json` | 27,703B | 29 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\data_assets\validator_rules.json` | 1,282B | 68 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\evaluation\__init__.py` | 63B | 1 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\evaluation\baseline_scores.json` | 75B | 6 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\evaluation\exemplar_prompts.json` | 330B | 10 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\__init__.py` | 63B | 1 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\l1_cms_schemas.py` | 1,600B | 62 | PromptType, PromptSchema, ValidationResult | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\l1_result_parser.py` | 1,713B | 62 | StrategyResult, DraftResult, QAResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\model_routing_policy_selection.py` | 723B | 26 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\model_routing_selector_integration.py` | 487B | 18 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\providers_anthropic_client.py` | 1,314B | 49 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\integration\providers_google_genai_client.py` | 3,194B | 94 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\__init__.py` | 1,981B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\__init__.py` | 2,011B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\check_schema_rules.py` | 6,796B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\check_schema_safety\__init__.py` | 2,051B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\check_schema_safety\check_schema_policy.py` | 6,954B | 208 | CheckDataPolicyPlanType, CheckDataPolicyPlanConstraints, CheckDataPolicyPlanResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\convert\__init__.py` | 49B | 1 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\convert\convert_to_internal_schema.py` | 20,925B | 521 | SchemaType, ConversionStrategy, FieldMapping... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_embedding\__init__.py` | 2,056B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_embedding\match_schema_context.py` | 19,879B | 518 | ContextMatchType, SchemaContext, ContextMatchRequest... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_embedding\retrieve_schema_similarity.py` | 21,457B | 539 | SimilarityMethod, CompatibilityLevel, SchemaSimilarityRequest... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_embedding\search_schema_vectors.py` | 22,095B | 584 | SchemaSearchMode, SchemaSimilarityType, SchemaVectorEntry... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_info.py` | 6,775B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_request\__init__.py` | 2,046B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_request\fetch_schema_history.py` | 19,998B | 549 | HistoryAction, SchemaChangeRecord, SchemaHistoryQuery... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_request\load_schema_planning.py` | 19,772B | 542 | SchemaType, ValidationMode, SchemaScope... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\data_access\get_schema_request\query_schema_store.py` | 23,157B | 654 | SchemaType, SchemaStatus, SchemaMetadata... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\synthesis\__init__.py` | 2,001B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\synthesis\pick_best_request\__init__.py` | 2,041B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\synthesis\pick_best_request\rank_schema_components.py` | 7,024B | 208 | RankDataComponentsPlanType, RankDataComponentsPlanConstraints, RankDataComponentsPlanResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\synthesis\pick_best_result.py` | 6,782B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\synthesis\state_update.py` | 6,758B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\validation\__init__.py` | 2,006B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\validation\check_schema_structure.py` | 6,824B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\validation\convert_schema_content.py` | 6,824B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\validation\find_schema_diagnostics.py` | 6,831B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\logic\validation\find_schema_problems.py` | 6,810B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\pipeline\__init__.py` | 1,996B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\pipeline\data_access\__init__.py` | 2,011B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\pipeline\data_access\get_schema_info.py` | 6,775B | 194 | ExecutionStatus, ExecutionContext, ProcessingResult... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\pipeline\data_access\get_schema_request\__init__.py` | 2,046B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\pipeline\data_access\get_schema_request\orchestrate_schema_planning.py` | 17,928B | 468 | SchemaType, ValidationLevel, TransformationType... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\runtime\__init__.py` | 1,991B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\runtime\validation.py` | 7,876B | 192 | ExecutionResult, Validation | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\templates\__init__.py` | 2,001B | 74 | - | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `schemas\templates\injection_patterns.py` | 2,627B | 64 | ExecutionResult, InjectionPatterns | **MIGRATE** | `agentic_core/schemas/models/` | LOW |

## archives/shared/ Analysis

**Files:** 43 | **LOC:** 5,766

| Path | Size | LOC | Classes | Action | Target | Risk |
|------|------|-----|---------|--------|--------|------|
| `shared\__init__.py` | 3,748B | 179 | - | **REVIEW** | `agentic_core/utils/` | LOW |
| `shared\caching\__init__.py` | 600B | 30 | - | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `shared\caching\semantic_cache.py` | 8,180B | 292 | CacheEntry, CacheHit, CacheMiss... | **DELETE** | `agentic_core/runtime/shared_runtime/semantic_cache.py` | LOW |
| `shared\caching\token_budget.py` | 8,502B | 240 | BudgetExceededError, TokenBudgetConfig, TokenBudget | **REVIEW** | `agentic_core/runtime/shared_runtime/` | MEDIUM |
| `shared\configuration\__init__.py` | 63B | 1 | - | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\configuration\config.py` | 5,826B | 183 | ModelProvider, ModelConfig, RAGConfig... | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\configuration\reasoning_config.py` | 5,456B | 144 | ModelProvider, ModelConfig, RAGConfig... | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\configuration\reasoning_prompt.py` | 2,244B | 54 | - | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\core\__init__.py` | 0B | 0 | - | **DELETE** | `agentic_core/utils/` | LOW |
| `shared\core\config.py` | 6,009B | 183 | ModelProvider, ModelConfig, RAGConfig... | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\core\exceptions.py` | 1,333B | 61 | AgenticWorkflowError, HopExecutionError, StagingBufferError... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\core\models.py` | 4,219B | 150 | ValidationSeverity, ValidationResult, ThematicAnalysis... | **REVIEW** | `agentic_core/schemas/models/` | MEDIUM |
| `shared\errors\__init__.py` | 63B | 1 | - | **DELETE** | `agentic_core/utils/` | LOW |
| `shared\errors\exceptions.py` | 1,272B | 61 | AgenticWorkflowError, HopExecutionError, StagingBufferError... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\internal\__init__.py` | 63B | 1 | - | **DELETE** | `agentic_core/utils/` | LOW |
| `shared\internal\placeholder_stub.py` | 1,072B | 25 | ARCHIVE_FILE_ACCESS_DEPRECATED | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\mcp\__init__.py` | 955B | 44 | - | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `shared\mcp\client.py` | 7,262B | 241 | MCPClient, MCPClientSpec, MCPClientStub... | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `shared\mcp\exceptions.py` | 981B | 34 | MCPError, MCPClientInitializationError, MCPClientNotFoundError... | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `shared\mcp\factory.py` | 6,297B | 196 | - | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `shared\mcp\providers.py` | 2,062B | 87 | ProviderType | **MIGRATE** | `agentic_core/L2_execution/mcp/` | MEDIUM |
| `shared\reasoning\__init__.py` | 646B | 33 | - | **REVIEW** | `agentic_core/utils/` | LOW |
| `shared\reasoning\react_engine.py` | 10,930B | 301 | ReasoningMode, ReActStep, ReActTrace... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\reasoning\reasoning_config.py` | 5,600B | 144 | ModelProvider, ModelConfig, RAGConfig... | **MIGRATE** | `agentic_core/config/` | LOW |
| `shared\reasoning\reasoning_prompt.py` | 2,298B | 54 | - | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\reasoning\reasoning_router.py` | 5,933B | 201 | TaskType, ReasoningRouter | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\reasoning\trace_models.py` | 5,490B | 121 | ThinkStep, ActionStep, ObservationStep... | **MIGRATE** | `agentic_core/schemas/models/` | LOW |
| `shared\resilience\__init__.py` | 1,432B | 67 | - | **REVIEW** | `agentic_core/L4_resilience/` | LOW |
| `shared\resilience\backoff.py` | 3,219B | 118 | BackoffStrategy, ExponentialBackoff, LinearBackoff | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `shared\resilience\circuit_breaker.py` | 4,265B | 131 | CircuitBreakerState, CircuitBreakerOpenError, CircuitBreaker | **MERGE** | `agentic_core/L4_resilience/circuit_breaker.py` | MEDIUM |
| `shared\resilience\error_recovery.py` | 7,481B | 211 | RecoveryStrategy, ResilienceError, TransientError... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `shared\resilience\mixin.py` | 7,515B | 218 | TokenLimitError, HardeningMixin | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `shared\resilience\rate_limiter.py` | 6,821B | 239 | RateLimitExceeded, TokenBucket, FixedWindow... | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `shared\resilience\telemetry.py` | 6,954B | 223 | OperationStatus, TelemetryEvent, SystemTelemetry | **REVIEW** | `agentic_core/L4_resilience/` | MEDIUM |
| `shared\result_types.py` | 2,879B | 99 | ResultStatus, Result, ValidationResult... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\safety\__init__.py` | 1,179B | 60 | - | **REVIEW** | `agentic_core/utils/` | LOW |
| `shared\safety\bias_auditor.py` | 8,306B | 243 | BiasType, BiasMatch, BiasResult... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\safety\constitutional_ai.py` | 11,293B | 363 | RuleType, RuleSeverity, ViolationType... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\safety\control_plane.py` | 11,662B | 298 | PolicyAction, SafetyPolicy, PolicyDecision... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\safety\pii_scrubber.py` | 5,969B | 186 | PIIType, PIIMatch, PIIResult... | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\stubs\placeholder_stub.py` | 1,097B | 25 | ARCHIVE_FILE_ACCESS_DEPRECATED | **REVIEW** | `agentic_core/utils/` | MEDIUM |
| `shared\types\models.py` | 4,219B | 150 | ValidationSeverity, ValidationResult, ThematicAnalysis... | **REVIEW** | `agentic_core/schemas/models/` | MEDIUM |
| `shared\types\workflow_types.py` | 1,471B | 74 | CircuitState, HopStatus, GateDecision... | **REVIEW** | `agentic_core/utils/` | MEDIUM |

## High-Value Migration Candidates (>100 LOC)

| File | LOC | Classes | Justification |
|------|-----|---------|---------------|
| `signal_enhancer.py` | 723 | 5 | Unique implementation (723 LOC). Migrate to modern structure. |
| `dynamic_dag_manager.py` | 714 | 9 | Unique implementation (714 LOC). Migrate to modern structure. |
| `query_schema_store.py` | 654 | 8 | Schema/model definition. Move to agentic_core/schemas/ |
| `search_schema_vectors.py` | 584 | 7 | Schema/model definition. Move to agentic_core/schemas/ |
| `fetch_schema_history.py` | 549 | 7 | Schema/model definition. Move to agentic_core/schemas/ |
| `load_schema_planning.py` | 542 | 10 | Schema/model definition. Move to agentic_core/schemas/ |
| `prompt_assembler.py` | 540 | 3 | Unique implementation (540 LOC). Migrate to modern structure. |
| `retrieve_schema_similarity.py` | 539 | 7 | Schema/model definition. Move to agentic_core/schemas/ |
| `convert_to_internal_schema.py` | 521 | 7 | Schema/model definition. Move to agentic_core/schemas/ |
| `match_schema_context.py` | 518 | 7 | Schema/model definition. Move to agentic_core/schemas/ |
| `reflection_engine.py` | 512 | 5 | Unique implementation (512 LOC). Migrate to modern structure. |
| `cognitive_contracts.py` | 511 | 8 | Unique implementation (511 LOC). Migrate to modern structure. |
| `input_validator.py` | 510 | 6 | Security/safety component. Move to L5_safety/ |
| `orchestrate_schema_planning.py` | 468 | 13 | Schema/model definition. Move to agentic_core/schemas/ |
| `secure_config.py` | 467 | 1 | Security/safety component. Move to L5_safety/ |
| `03_runtime_freeze_report.json` | 426 | 0 | JSON data asset. Move to agentic_core/schemas/models/data_assets/ |
| `secure_error.py` | 372 | 7 | Security/safety component. Move to L5_safety/ |
| `mcp_tools.py` | 347 | 3 | MCP integration. Move to L2_execution/mcp/ |
| `secure_checkpoint.py` | 318 | 3 | Security/safety component. Move to L5_safety/ |
| `secure_logger.py` | 266 | 3 | Security/safety component. Move to L5_safety/ |
| `client.py` | 241 | 4 | MCP integration. Move to L2_execution/mcp/ |
| `orchestrator.py` | 234 | 5 | Abstract interface/contract. Migrate to schemas. |
| `test_input_sanitizer.py` | 226 | 1 | Security/safety component. Move to L5_safety/ |
| `artist_specs.json` | 220 | 0 | Schema/model definition. Move to agentic_core/schemas/ |
| `check_schema_policy.py` | 208 | 8 | Schema/model definition. Move to agentic_core/schemas/ |
| `rank_schema_components.py` | 208 | 8 | Schema/model definition. Move to agentic_core/schemas/ |
| `factory.py` | 196 | 0 | MCP integration. Move to L2_execution/mcp/ |
| `shared_models.py` | 194 | 13 | Schema/model definition. Move to agentic_core/schemas/ |
| `get_schema_info.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `check_schema_rules.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `get_schema_info.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `pick_best_result.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `state_update.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `check_schema_structure.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `convert_schema_content.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `find_schema_diagnostics.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `find_schema_problems.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `get_schema_info.py` | 194 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `validation.py` | 192 | 2 | Schema/model definition. Move to agentic_core/schemas/ |
| `config.py` | 183 | 9 | Configuration. Move to agentic_core/config/ |
| `config.py` | 183 | 9 | Configuration. Move to agentic_core/config/ |
| `action_plane.py` | 156 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `cognitive_plane.py` | 153 | 4 | Schema/model definition. Move to agentic_core/schemas/ |
| `reasoning_config.py` | 144 | 5 | Configuration. Move to agentic_core/config/ |
| `reasoning_config.py` | 144 | 5 | Configuration. Move to agentic_core/config/ |
| `master_resume.json` | 141 | 0 | Schema/model definition. Move to agentic_core/schemas/ |
| `trace_models.py` | 121 | 8 | Schema/model definition. Move to agentic_core/schemas/ |
| `l4_types.py` | 109 | 8 | Schema/model definition. Move to agentic_core/schemas/ |

## Merge Candidates (Archive Richer Than Modern)

| Archive File | LOC | Modern Equivalent | Action |
|--------------|-----|-------------------|--------|
| `runtime\core\resilience\circuit_breaker.py` | 357 | `agentic_core/L4_resilience/circuit_breaker.py` | Merge unique features |
| `runtime\shared\circuit_breaker.py` | 450 | `agentic_core/L4_resilience/circuit_breaker.py` | Merge unique features |
| `shared\resilience\circuit_breaker.py` | 131 | `agentic_core/L4_resilience/circuit_breaker.py` | Merge unique features |

## Delete Candidates

| File | Reason |
|------|--------|
| `runtime\__init__.py` | Empty or stub init file. |
| `runtime\core\subatomic_hop.py` | Modern version exists with dependency injection pattern. Archive obsolete. |
| `shared\caching\semantic_cache.py` | Modern version has semantic matching. Archive is basic version. |
| `shared\core\__init__.py` | Empty or stub init file. |
| `shared\errors\__init__.py` | Empty or stub init file. |
| `shared\internal\__init__.py` | Empty or stub init file. |

## Python Class Inventory

| Class | File | Bases | Methods | Migrate To |
|-------|------|-------|---------|------------|
| `PlanQualityError` | `cognitive_contracts.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `ConsistencyError` | `cognitive_contracts.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `ContractStage` | `cognitive_contracts.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `Constraint` | `cognitive_contracts.py` | None | 0 | `agentic_core/schemas/models/` |
| `Plan` | `cognitive_contracts.py` | None | 0 | `agentic_core/schemas/models/` |
| `CognitiveContract` | `cognitive_contracts.py` | None | 0 | `agentic_core/schemas/models/` |
| `CognitiveContractValidator` | `cognitive_contracts.py` | None | 5 | `agentic_core/schemas/models/` |
| `CognitiveContractManager` | `cognitive_contracts.py` | None | 5 | `agentic_core/schemas/models/` |
| `GraphTransaction` | `dynamic_dag_manager.py` | None | 5 | `agentic_core/L3_orchestration/` |
| `MutationAction` | `dynamic_dag_manager.py` | Enum | 0 | `agentic_core/L3_orchestration/` |
| `HopSpec` | `dynamic_dag_manager.py` | BaseModel | 0 | `agentic_core/L3_orchestration/` |
| `DAGMutation` | `dynamic_dag_manager.py` | BaseModel | 1 | `agentic_core/L3_orchestration/` |
| `MutationResult` | `dynamic_dag_manager.py` | BaseModel | 0 | `agentic_core/L3_orchestration/` |
| `DAGConfig` | `dynamic_dag_manager.py` | BaseModel | 0 | `agentic_core/L3_orchestration/` |
| `DAGMutator` | `dynamic_dag_manager.py` | None | 10 | `agentic_core/L3_orchestration/` |
| `DAGManager` | `dynamic_dag_manager.py` | None | 10 | `agentic_core/L3_orchestration/` |
| `Config` | `dynamic_dag_manager.py` | None | 0 | `agentic_core/L3_orchestration/` |
| `ContextType` | `few_shot_registry.py` | Enum | 0 | `agentic_core/runtime/` |
| `FewShotExample` | `few_shot_registry.py` | None | 0 | `agentic_core/runtime/` |
| `FewShotRegistry` | `few_shot_registry.py` | BaseModel | 5 | `agentic_core/runtime/` |
| `Config` | `few_shot_registry.py` | None | 0 | `agentic_core/runtime/` |
| `InstructionalLayer` | `instructional_injections.py` | Enum | 0 | `agentic_core/runtime/` |
| `InstructionalInjectionType` | `instructional_injections.py` | Enum | 0 | `agentic_core/runtime/` |
| `StageMapping` | `instructional_injections.py` | None | 0 | `agentic_core/runtime/` |
| `NegotiationMessage` | `node_negotiator.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `NegotiationRound` | `node_negotiator.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `NegotiationConfig` | `node_negotiator.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `NegotiationResult` | `node_negotiator.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `NodeNegotiator` | `node_negotiator.py` | None | 7 | `agentic_core/runtime/` |
| `NegotiatingHop` | `node_negotiator.py` | SubatomicHop | 1 | `agentic_core/runtime/` |
| `PromptComponents` | `prompt_assembler.py` | None | 0 | `agentic_core/prompt_governance/` |
| `PromptTemplate` | `prompt_assembler.py` | BaseModel | 0 | `agentic_core/prompt_governance/` |
| `PromptAssembler` | `prompt_assembler.py` | None | 10 | `agentic_core/prompt_governance/` |
| `EnhancementConfig` | `prompt_enhancer.py` | None | 0 | `agentic_core/runtime/` |
| `PromptEnhancer` | `prompt_enhancer.py` | None | 6 | `agentic_core/runtime/` |
| `PromptInjectionLoader` | `prompt_injection_loader.py` | None | 11 | `agentic_core/runtime/` |
| `CritiqueResult` | `reflection_engine.py` | BaseModel | 1 | `agentic_core/runtime/shared_runtime/` |
| `ValidationCriterion` | `reflection_engine.py` | BaseModel | 0 | `agentic_core/runtime/shared_runtime/` |
| `ReflectionConfig` | `reflection_engine.py` | BaseModel | 0 | `agentic_core/runtime/shared_runtime/` |
| `MutationRequest` | `reflection_engine.py` | BaseModel | 0 | `agentic_core/runtime/shared_runtime/` |
| `ReflectionEngine` | `reflection_engine.py` | None | 8 | `agentic_core/runtime/shared_runtime/` |
| `ServiceNotFoundError` | `service_container.py` | Exception | 0 | `agentic_core/runtime/` |
| `ServiceContainer` | `service_container.py` | None | 6 | `agentic_core/runtime/` |
| `Service` | `service_container.py` | ABC | 0 | `agentic_core/runtime/` |
| `MicroStage` | `shared_models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `HopState` | `shared_models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `RetryPolicy` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `MicroCheckpoint` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `StageTransition` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `InjectionType` | `shared_models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `InjectionScope` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `InjectionPattern` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `InjectionMatch` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `InjectionConfig` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ExecutionResult` | `shared_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `Config` | `shared_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `InputValidationError` | `subatomic_hop.py` | Exception | 0 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `StageExecutionError` | `subatomic_hop.py` | Exception | 0 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `QualityGateFailure` | `subatomic_hop.py` | Exception | 0 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `MutationRequired` | `subatomic_hop.py` | Exception | 1 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `SubatomicHopConfig` | `subatomic_hop.py` | None | 0 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `SubatomicHop` | `subatomic_hop.py` | None | 5 | `agentic_core/runtime/shared_runtime/subatomic_hop.py` |
| `TestDAGMutator` | `test_dynamic_dag.py` | None | 10 | `agentic_core/runtime/` |
| `TestDAGManager` | `test_dynamic_dag.py` | None | 11 | `agentic_core/runtime/` |
| `TestMutationIntegration` | `test_dynamic_dag.py` | None | 2 | `agentic_core/runtime/` |
| `TestMutationScenarios` | `test_dynamic_dag.py` | None | 1 | `agentic_core/runtime/` |
| `TestInstructionalInjections` | `test_instructional_injections.py` | None | 4 | `agentic_core/runtime/` |
| `TestPromptInjectionLoaderIntegration` | `test_instructional_injections.py` | None | 5 | `agentic_core/runtime/` |
| `TestSubatomicHopIntegration` | `test_instructional_injections.py` | None | 2 | `agentic_core/runtime/` |
| `TestInjectionQuality` | `test_instructional_injections.py` | None | 3 | `agentic_core/runtime/` |
| `TestNodeNegotiator` | `test_node_negotiation.py` | None | 6 | `agentic_core/runtime/` |
| `TestSubatomicHopNegotiation` | `test_node_negotiation.py` | None | 3 | `agentic_core/runtime/` |
| `TestNegotiationIntegration` | `test_node_negotiation.py` | None | 1 | `agentic_core/runtime/` |
| `TestNegotiationScenarios` | `test_node_negotiation.py` | None | 0 | `agentic_core/runtime/` |
| `TestPromptInjectionLoader` | `test_prompt_injection_loader.py` | None | 11 | `agentic_core/runtime/` |
| `TestInjectionPatterns` | `test_prompt_injection_loader.py` | None | 5 | `agentic_core/runtime/` |
| `TestIntegration` | `test_prompt_injection_loader.py` | None | 4 | `agentic_core/runtime/` |
| `TestRealWorldScenarios` | `test_prompt_injection_loader.py` | None | 5 | `agentic_core/runtime/` |
| `TestReflectionEngine` | `test_reflection_engine.py` | None | 3 | `agentic_core/runtime/` |
| `TestSubatomicHopReflection` | `test_reflection_engine.py` | None | 1 | `agentic_core/runtime/` |
| `TestReflectionIntegration` | `test_reflection_engine.py` | None | 1 | `agentic_core/runtime/` |
| `TestReflectionPerformance` | `test_reflection_engine.py` | None | 0 | `agentic_core/runtime/` |
| `TestSubatomicHop` | `test_subatomic_hop.py` | None | 7 | `agentic_core/runtime/` |
| `TestSubatomicHopIntegration` | `test_subatomic_hop.py` | None | 2 | `agentic_core/runtime/` |
| `FeedbackType` | `feedback_loop.py` | Enum | 0 | `agentic_core/runtime/` |
| `QualityFeedback` | `feedback_loop.py` | None | 0 | `agentic_core/runtime/` |
| `QualityTrend` | `feedback_loop.py` | None | 0 | `agentic_core/runtime/` |
| `AdaptiveThresholds` | `feedback_loop.py` | None | 2 | `agentic_core/runtime/` |
| `FeedbackLoop` | `feedback_loop.py` | None | 9 | `agentic_core/runtime/` |
| `SignalQuality` | `signal_enhancer.py` | Enum | 0 | `agentic_core/runtime/shared_runtime/` |
| `QualityThresholds` | `signal_enhancer.py` | None | 0 | `agentic_core/runtime/shared_runtime/` |
| `ClaimAnalysis` | `signal_enhancer.py` | None | 0 | `agentic_core/runtime/shared_runtime/` |
| `SignalAssessment` | `signal_enhancer.py` | None | 1 | `agentic_core/runtime/shared_runtime/` |
| `SignalEnhancer` | `signal_enhancer.py` | None | 16 | `agentic_core/runtime/shared_runtime/` |
| `TaskState` | `async_coordinator.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `TaskInfo` | `async_coordinator.py` | None | 0 | `agentic_core/L4_resilience/` |
| `AsyncCoordinator` | `async_coordinator.py` | None | 2 | `agentic_core/L4_resilience/` |
| `CircuitState` | `circuit_breaker.py` | Enum | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitOpenError` | `circuit_breaker.py` | Exception | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CriticalServiceFailure` | `circuit_breaker.py` | Exception | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerConfig` | `circuit_breaker.py` | None | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreaker` | `circuit_breaker.py` | None | 9 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerFactory` | `circuit_breaker.py` | None | 8 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `MutationPhase` | `dag_safety.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `StateSnapshot` | `dag_safety.py` | None | 1 | `agentic_core/L4_resilience/` |
| `DAGSafetyManager` | `dag_safety.py` | None | 9 | `agentic_core/L4_resilience/` |
| `SafeMutationContext` | `dag_safety.py` | None | 4 | `agentic_core/L4_resilience/` |
| `PruningStrategy` | `memory_manager.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `MemoryLimits` | `memory_manager.py` | None | 0 | `agentic_core/L4_resilience/` |
| `ContextItem` | `memory_manager.py` | None | 0 | `agentic_core/L4_resilience/` |
| `MemoryManager` | `memory_manager.py` | None | 15 | `agentic_core/L4_resilience/` |
| `RateLimitStrategy` | `rate_limiter.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `RateLimitConfig` | `rate_limiter.py` | None | 0 | `agentic_core/L4_resilience/` |
| `RateLimitExceeded` | `rate_limiter.py` | Exception | 1 | `agentic_core/L4_resilience/` |
| `SlidingWindowLimiter` | `rate_limiter.py` | None | 2 | `agentic_core/L4_resilience/` |
| `TokenBucketLimiter` | `rate_limiter.py` | None | 2 | `agentic_core/L4_resilience/` |
| `FixedWindowLimiter` | `rate_limiter.py` | None | 2 | `agentic_core/L4_resilience/` |
| `RateLimiter` | `rate_limiter.py` | None | 7 | `agentic_core/L4_resilience/` |
| `ResourceType` | `resource_manager.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `ResourceInfo` | `resource_manager.py` | None | 0 | `agentic_core/L4_resilience/` |
| `ResourceManager` | `resource_manager.py` | None | 8 | `agentic_core/L4_resilience/` |
| `ConnectionPool` | `resource_manager.py` | None | 1 | `agentic_core/L4_resilience/` |
| `SecurityIntegrityError` | `input_sanitizer.py` | Exception | 0 | `agentic_core/L5_safety/guardrails/` |
| `InputSanitizer` | `input_sanitizer.py` | None | 7 | `agentic_core/L5_safety/guardrails/` |
| `ValidationType` | `input_validator.py` | Enum | 0 | `agentic_core/L5_safety/guardrails/` |
| `ValidationRule` | `input_validator.py` | None | 0 | `agentic_core/L5_safety/guardrails/` |
| `InputValidationError` | `input_validator.py` | Exception | 1 | `agentic_core/L5_safety/guardrails/` |
| `InputValidator` | `input_validator.py` | None | 10 | `agentic_core/L5_safety/guardrails/` |
| `ValidatedInput` | `input_validator.py` | BaseModel | 2 | `agentic_core/L5_safety/guardrails/` |
| `Config` | `input_validator.py` | None | 0 | `agentic_core/L5_safety/guardrails/` |
| `CheckpointIntegrityError` | `secure_checkpoint.py` | Exception | 0 | `agentic_core/L5_safety/guardrails/` |
| `SecureCheckpointManager` | `secure_checkpoint.py` | None | 8 | `agentic_core/L5_safety/guardrails/` |
| `CheckpointManagerFactory` | `secure_checkpoint.py` | None | 2 | `agentic_core/L5_safety/guardrails/` |
| `SecureConfigManager` | `secure_config.py` | None | 19 | `agentic_core/L5_safety/guardrails/` |
| `SecureError` | `secure_error.py` | Exception | 2 | `agentic_core/L5_safety/guardrails/` |
| `SecurityError` | `secure_error.py` | SecureError | 0 | `agentic_core/L5_safety/guardrails/` |
| `ConfigurationError` | `secure_error.py` | SecureError | 0 | `agentic_core/L5_safety/guardrails/` |
| `ValidationError` | `secure_error.py` | SecureError | 0 | `agentic_core/L5_safety/guardrails/` |
| `ExecutionError` | `secure_error.py` | SecureError | 0 | `agentic_core/L5_safety/guardrails/` |
| `ErrorSanitizer` | `secure_error.py` | None | 3 | `agentic_core/L5_safety/guardrails/` |
| `SecureErrorHandler` | `secure_error.py` | None | 3 | `agentic_core/L5_safety/guardrails/` |
| `SecureLogger` | `secure_logger.py` | None | 9 | `agentic_core/L5_safety/guardrails/` |
| `SecureLoggerAdapter` | `secure_logger.py` | None | 7 | `agentic_core/L5_safety/guardrails/` |
| `SecureLogContext` | `secure_logger.py` | None | 3 | `agentic_core/L5_safety/guardrails/` |
| `TestInputSanitizer` | `test_input_sanitizer.py` | None | 13 | `agentic_core/L5_safety/guardrails/` |
| `ResumeEnhancementOrchestrator` | `enhancement_integration.py` | None | 3 | `agentic_core/runtime/` |
| `EvidenceType` | `evidence_injector.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `EvidenceItem` | `evidence_injector.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `EvidenceInjector` | `evidence_injector.py` | None | 10 | `agentic_core/runtime/` |
| `ArchetypeBase` | `persona_router.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `PsychometricProfile` | `persona_router.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ReaderPersona` | `persona_router.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `PersonaRouter` | `persona_router.py` | None | 13 | `agentic_core/runtime/` |
| `CompetitivePosition` | `competitor_recon.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `Company` | `competitor_recon.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ReconSignal` | `competitor_recon.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ReconAgent` | `competitor_recon.py` | None | 11 | `agentic_core/runtime/` |
| `PersonaTemplate` | `functional_personas.py` | None | 2 | `agentic_core/runtime/` |
| `PromptSanitizer` | `functional_personas.py` | None | 2 | `agentic_core/runtime/` |
| `AgentRole` | `agent_capabilities.py` | Enum | 0 | `agentic_core/runtime/` |
| `AgentCapability` | `agent_capabilities.py` | None | 0 | `agentic_core/runtime/` |
| `AgentSpec` | `agent_capabilities.py` | None | 3 | `agentic_core/runtime/` |
| `AgentRegistry` | `agent_capabilities.py` | None | 9 | `agentic_core/runtime/` |
| `LegacyCodeError` | `agent_capabilities.py` | Exception | 0 | `agentic_core/runtime/` |
| `KNodeScanner` | `migration_tools.py` | None | 4 | `agentic_core/runtime/` |
| `KNodeMigrator` | `migration_tools.py` | None | 4 | `agentic_core/runtime/` |
| `MigrationValidator` | `migration_tools.py` | None | 3 | `agentic_core/runtime/` |
| `FailureType` | `adaptive_recovery_loop.py` | Enum | 0 | `agentic_core/runtime/` |
| `RecoveryAction` | `adaptive_recovery_loop.py` | Enum | 0 | `agentic_core/runtime/` |
| `FailureEvent` | `adaptive_recovery_loop.py` | None | 0 | `agentic_core/runtime/` |
| `TemperatureAdjustment` | `adaptive_recovery_loop.py` | None | 0 | `agentic_core/runtime/` |
| `RecoveryResult` | `adaptive_recovery_loop.py` | None | 0 | `agentic_core/runtime/` |
| `AdaptiveRecoveryLoop` | `adaptive_recovery_loop.py` | None | 8 | `agentic_core/runtime/` |
| `RetrievalDecision` | `adaptive_retrieval_gate.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `AdaptiveRetrievalGate` | `adaptive_retrieval_gate.py` | None | 5 | `agentic_core/runtime/` |
| `ReasoningStrategy` | `agent_base.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ReasoningConfig` | `agent_base.py` | None | 0 | `agentic_core/runtime/` |
| `Agent` | `agent_base.py` | ABC | 2 | `agentic_core/runtime/` |
| `AgentConfig` | `agent_executor.py` | None | 0 | `agentic_core/runtime/` |
| `AgentMessage` | `agent_executor.py` | None | 0 | `agentic_core/runtime/` |
| `AgentResponse` | `agent_executor.py` | None | 0 | `agentic_core/runtime/` |
| `AgentExecutor` | `agent_executor.py` | None | 14 | `agentic_core/runtime/` |
| `DiagramType` | `architecture_visualizer_agent.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `DiagramNode` | `architecture_visualizer_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `DiagramArtifact` | `architecture_visualizer_agent.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `SimpleAgentBase` | `architecture_visualizer_agent.py` | None | 1 | `agentic_core/runtime/` |
| `ArchitectureVisualizerAgent` | `architecture_visualizer_agent.py` | SimpleAgentBase | 3 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `architecture_visualizer_agent.py` | None | 1 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `architecture_visualizer_agent.py` | None | 1 | `agentic_core/runtime/` |
| `ToneVoice` | `brand_voice_enforcer.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ToneSettings` | `brand_voice_enforcer.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ToneViolation` | `brand_voice_enforcer.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ToneAnalysisResult` | `brand_voice_enforcer.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ToneEnforcer` | `brand_voice_enforcer.py` | None | 15 | `agentic_core/runtime/` |
| `TaskPriority` | `bulkhead_manager.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `BulkheadConfig` | `bulkhead_manager.py` | None | 0 | `agentic_core/runtime/` |
| `BulkheadMetrics` | `bulkhead_manager.py` | None | 0 | `agentic_core/runtime/` |
| `ResourceExhaustedError` | `bulkhead_manager.py` | Exception | 1 | `agentic_core/runtime/` |
| `Bulkhead` | `bulkhead_manager.py` | None | 4 | `agentic_core/runtime/` |
| `BulkheadManager` | `bulkhead_manager.py` | None | 7 | `agentic_core/runtime/` |
| `RedisConfig` | `cache_clients.py` | None | 0 | `agentic_core/runtime/shared_runtime/` |
| `CircuitState` | `circuit_breaker.py` | str, Enum | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerConfig` | `circuit_breaker.py` | None | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `RequestResult` | `circuit_breaker.py` | None | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerError` | `circuit_breaker.py` | Exception | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreaker` | `circuit_breaker.py` | None | 14 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerRegistry` | `circuit_breaker.py` | None | 3 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CompetitorMove` | `competitor_recon_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `StrategicHook` | `competitor_recon_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `IntelProvider` | `competitor_recon_agent.py` | ABC | 2 | `agentic_core/runtime/` |
| `MockIntelProvider` | `competitor_recon_agent.py` | IntelProvider | 3 | `agentic_core/runtime/` |
| `CompetitorReconAgent` | `competitor_recon_agent.py` | None | 8 | `agentic_core/runtime/` |
| `CompressionResult` | `contextual_compressor.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ContextualCompressor` | `contextual_compressor.py` | None | 6 | `agentic_core/runtime/` |
| `CacheEntry` | `contrastive_cache.py` | BaseModel | 1 | `agentic_core/runtime/shared_runtime/` |
| `ContrastiveSemanticCache` | `contrastive_cache.py` | None | 14 | `agentic_core/runtime/shared_runtime/` |
| `NullCache` | `contrastive_cache.py` | None | 5 | `agentic_core/runtime/shared_runtime/` |
| `WritingStyle` | `cultural_decoder_agent.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `CompanyDNA` | `cultural_decoder_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `CulturallyAlignedContent` | `cultural_decoder_agent.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `SimpleAgentBase` | `cultural_decoder_agent.py` | None | 1 | `agentic_core/runtime/` |
| `CulturalDecoderAgent` | `cultural_decoder_agent.py` | SimpleAgentBase | 5 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `cultural_decoder_agent.py` | None | 1 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `cultural_decoder_agent.py` | None | 1 | `agentic_core/runtime/` |
| `FailureReason` | `dead_letter_queue.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `DeadLetterStatus` | `dead_letter_queue.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `DeadLetterItem` | `dead_letter_queue.py` | None | 2 | `agentic_core/runtime/` |
| `DeadLetterStorage` | `dead_letter_queue.py` | ABC | 0 | `agentic_core/runtime/` |
| `FileDeadLetterStorage` | `dead_letter_queue.py` | DeadLetterStorage | 2 | `agentic_core/runtime/` |
| `DeadLetterQueue` | `dead_letter_queue.py` | None | 2 | `agentic_core/runtime/` |
| `HardenedEventBus` | `event_bus_integration.py` | None | 2 | `agentic_core/runtime/` |
| `RankedEvidence` | `evidence_ranker.py` | BaseModel | 3 | `agentic_core/runtime/` |
| `EvidenceRanker` | `evidence_ranker.py` | None | 8 | `agentic_core/runtime/` |
| `ExecutionArtifact` | `execution_orchestrator.py` | None | 0 | `agentic_core/runtime/` |
| `ExecutionTrace` | `execution_orchestrator.py` | None | 0 | `agentic_core/runtime/` |
| `ExecutionOrchestrator` | `execution_orchestrator.py` | None | 11 | `agentic_core/runtime/` |
| `BriefSection` | `executive_brief_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `ExecutiveBrief` | `executive_brief_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `ExecutiveBriefAgent` | `executive_brief_agent.py` | None | 9 | `agentic_core/runtime/` |
| `HeadlineOutput` | `executive_title_composer.py` | None | 0 | `agentic_core/runtime/` |
| `Executive_Title_Composer` | `executive_title_composer.py` | Agent | 5 | `agentic_core/runtime/` |
| `FactStatus` | `fact_ledger.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `Fact` | `fact_ledger.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `VerificationResult` | `fact_ledger.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ClaimExtractor` | `fact_ledger.py` | None | 3 | `agentic_core/runtime/` |
| `FactLedger` | `fact_ledger.py` | None | 15 | `agentic_core/runtime/` |
| `ConstraintFailureType` | `feedback_loop_orchestrator.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RegenerationCheckpoint` | `feedback_loop_orchestrator.py` | None | 1 | `agentic_core/runtime/` |
| `RegenerationResult` | `feedback_loop_orchestrator.py` | None | 1 | `agentic_core/runtime/` |
| `FeedbackLoopOrchestrator` | `feedback_loop_orchestrator.py` | None | 7 | `agentic_core/runtime/` |
| `CompetencyItem` | `gap_closure_architect.py` | None | 0 | `agentic_core/runtime/` |
| `CompetenciesOutput` | `gap_closure_architect.py` | None | 0 | `agentic_core/runtime/` |
| `Gap_Closure_Architect` | `gap_closure_architect.py` | Agent | 7 | `agentic_core/runtime/` |
| `CacheEntry` | `global_cache.py` | BaseModel | 2 | `agentic_core/runtime/shared_runtime/` |
| `L1MemoryCache` | `global_cache.py` | None | 5 | `agentic_core/runtime/shared_runtime/` |
| `L2VectorStore` | `global_cache.py` | None | 5 | `agentic_core/runtime/shared_runtime/` |
| `SimpleEmbedder` | `global_cache.py` | None | 3 | `agentic_core/runtime/shared_runtime/` |
| `GlobalCache` | `global_cache.py` | None | 8 | `agentic_core/runtime/shared_runtime/` |
| `IndustrySensitivity` | `governance_shield_agent.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RiskProfile` | `governance_shield_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `SafetyProtocol` | `governance_shield_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `GovernanceShieldAgent` | `governance_shield_agent.py` | None | 9 | `agentic_core/runtime/` |
| `QueryType` | `graphrag_fusion.py` | Enum | 0 | `agentic_core/runtime/` |
| `FusionResult` | `graphrag_fusion.py` | None | 1 | `agentic_core/runtime/` |
| `CypherQueryGenerator` | `graphrag_fusion.py` | None | 2 | `agentic_core/runtime/` |
| `GraphRAGFusion` | `graphrag_fusion.py` | None | 4 | `agentic_core/runtime/` |
| `HardenedAnthropicConfig` | `hardened_anthropic_executor.py` | None | 2 | `agentic_core/runtime/` |
| `HardenedAnthropicExecutor` | `hardened_anthropic_executor.py` | HardeningMixin | 5 | `agentic_core/runtime/` |
| `ContextOverflowError` | `hardened_gemini_executor.py` | Exception | 0 | `agentic_core/runtime/` |
| `CircuitBreakerOpenError` | `hardened_gemini_executor.py` | Exception | 0 | `agentic_core/runtime/` |
| `HardenedGeminiConfig` | `hardened_gemini_executor.py` | None | 3 | `agentic_core/runtime/` |
| `InteractionTelemetry` | `hardened_gemini_executor.py` | None | 0 | `agentic_core/runtime/` |
| `CircuitBreakerState` | `hardened_gemini_executor.py` | None | 1 | `agentic_core/runtime/` |
| `CircuitBreaker` | `hardened_gemini_executor.py` | None | 5 | `agentic_core/runtime/` |
| `InteractionTelemetry` | `hardened_gemini_executor.py` | None | 0 | `agentic_core/runtime/` |
| `HardenedGeminiExecutor` | `hardened_gemini_executor.py` | None | 6 | `agentic_core/runtime/` |
| `HardenedOpenAIConfig` | `hardened_openai_executor.py` | None | 2 | `agentic_core/runtime/` |
| `HardenedOpenAIExecutor` | `hardened_openai_executor.py` | HardeningMixin | 5 | `agentic_core/runtime/` |
| `HealthStatus` | `health_check.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ComponentType` | `health_check.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `HealthCheckResult` | `health_check.py` | None | 1 | `agentic_core/runtime/` |
| `HealthChecker` | `health_check.py` | ABC | 2 | `agentic_core/runtime/` |
| `BulkheadHealthChecker` | `health_check.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `CircuitBreakerHealthChecker` | `health_check.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `DeadLetterQueueHealthChecker` | `health_check.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `CheckpointManagerHealthChecker` | `health_check.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `HealthCheckRegistry` | `health_check.py` | None | 3 | `agentic_core/runtime/` |
| `HybridScoreResult` | `hybrid_scorer.py` | BaseModel | 3 | `agentic_core/runtime/` |
| `HybridScorer` | `hybrid_scorer.py` | None | 9 | `agentic_core/runtime/` |
| `ExpansionStrategy` | `hyde_processor.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `HyDEDocument` | `hyde_processor.py` | None | 1 | `agentic_core/runtime/` |
| `HyDEResult` | `hyde_processor.py` | None | 0 | `agentic_core/runtime/` |
| `HyDEProcessor` | `hyde_processor.py` | None | 8 | `agentic_core/runtime/` |
| `InfrastructureOrchestrator` | `infrastructure_integration.py` | None | 1 | `agentic_core/runtime/` |
| `EventBusHealthChecker` | `infrastructure_integration.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `ProvenanceHealthChecker` | `infrastructure_integration.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `ModelRouterHealthChecker` | `infrastructure_integration.py` | HealthChecker | 3 | `agentic_core/runtime/` |
| `InfrastructureUpgradesOrchestrator` | `infrastructure_upgrades_integration.py` | None | 2 | `agentic_core/runtime/` |
| `GuardAction` | `input_guardrail.py` | Enum | 0 | `agentic_core/runtime/` |
| `GuardResult` | `input_guardrail.py` | None | 1 | `agentic_core/runtime/` |
| `InputGuardrail` | `input_guardrail.py` | None | 12 | `agentic_core/runtime/` |
| `ValidationSeverity` | `integrity_gate_executor.py` | Enum | 0 | `agentic_core/runtime/` |
| `GateType` | `integrity_gate_executor.py` | Enum | 0 | `agentic_core/runtime/` |
| `ValidationRule` | `integrity_gate_executor.py` | None | 0 | `agentic_core/runtime/` |
| `ValidationResult` | `integrity_gate_executor.py` | None | 0 | `agentic_core/runtime/` |
| `CryptographicSignature` | `integrity_gate_executor.py` | None | 1 | `agentic_core/runtime/` |
| `IntegrityGateExecutor` | `integrity_gate_executor.py` | None | 13 | `agentic_core/runtime/` |
| `ArchetypeClassificationResult` | `k1_routing_agent.py` | None | 0 | `agentic_core/runtime/` |
| `RouteSelectionResult` | `k1_routing_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K1Output` | `k1_routing_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K1_RoutingAgent` | `k1_routing_agent.py` | Agent | 3 | `agentic_core/runtime/` |
| `K3Output` | `k3_message_body_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K3_MessageBodyAgent` | `k3_message_body_agent.py` | Agent | 6 | `agentic_core/runtime/` |
| `ProvenanceRule` | `k5a_agent.py` | None | 2 | `agentic_core/runtime/` |
| `K5AOutput` | `k5a_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K5A_GenerationAgent` | `k5a_agent.py` | Agent | 5 | `agentic_core/runtime/` |
| `K5Output` | `k5_cta_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K5_CTAAgent` | `k5_cta_agent.py` | Agent | 3 | `agentic_core/runtime/` |
| `K7Output` | `k7_assembly_agent.py` | None | 0 | `agentic_core/runtime/` |
| `K7_AssemblyAgent` | `k7_assembly_agent.py` | Agent | 7 | `agentic_core/runtime/` |
| `GraphContext` | `knowledge_graph_agent.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `KnowledgeGraphAgent` | `knowledge_graph_agent.py` | None | 16 | `agentic_core/runtime/` |
| `KXExecutionContext` | `kx_executor.py` | None | 0 | `agentic_core/runtime/` |
| `KXExecutionResult` | `kx_executor.py` | None | 0 | `agentic_core/runtime/` |
| `KXNodeExecutor` | `kx_executor.py` | None | 9 | `agentic_core/runtime/` |
| `KNodeType` | `kx_nodes.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ReasoningStrategy` | `kx_nodes.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RAGConfig` | `kx_nodes.py` | None | 1 | `agentic_core/runtime/` |
| `DecodingParams` | `kx_nodes.py` | None | 0 | `agentic_core/runtime/` |
| `KNodeConfig` | `kx_nodes.py` | None | 1 | `agentic_core/runtime/` |
| `KXNodeRegistry` | `kx_nodes.py` | None | 7 | `agentic_core/runtime/` |
| `LateInteractionReranker` | `late_interaction_reranker.py` | None | 6 | `agentic_core/runtime/` |
| `PassThroughReranker` | `late_interaction_reranker.py` | None | 3 | `agentic_core/runtime/` |
| `MCPTool` | `mcp_tools.py` | None | 2 | `agentic_core/L2_execution/mcp/` |
| `MCPToolResult` | `mcp_tools.py` | None | 0 | `agentic_core/L2_execution/mcp/` |
| `MCPToolServer` | `mcp_tools.py` | None | 7 | `agentic_core/L2_execution/mcp/` |
| `ImpactCategory` | `metric_augmenter.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `BusinessImpact` | `metric_augmenter.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `AugmentedBullet` | `metric_augmenter.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `MetricAugmenter` | `metric_augmenter.py` | None | 8 | `agentic_core/runtime/` |
| `LLMResponse` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `MessageType` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `AgentMessage` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `AgentResponse` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ReasoningConfig` | `models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `HopStatus` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `GateDecision` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationSeverity` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `WorkflowCheckpoint` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ThematicAnalysis` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `RAGState` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `CircuitState` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `AgenticWorkflowError` | `models.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `HopExecutionError` | `models.py` | AgenticWorkflowError | 0 | `agentic_core/schemas/models/` |
| `ValidationError` | `models.py` | AgenticWorkflowError | 0 | `agentic_core/schemas/models/` |
| `APIError` | `models.py` | AgenticWorkflowError | 0 | `agentic_core/schemas/models/` |
| `CircuitBreakerOpenError` | `models.py` | AgenticWorkflowError | 0 | `agentic_core/schemas/models/` |
| `Provider` | `multi_provider_clients.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ProviderConfig` | `multi_provider_clients.py` | None | 0 | `agentic_core/runtime/` |
| `TracingConfig` | `observability_clients.py` | None | 0 | `agentic_core/runtime/` |
| `PlanPhase` | `onboarding_planner_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `OnboardingPlan` | `onboarding_planner_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `OnboardingPlannerAgent` | `onboarding_planner_agent.py` | None | 11 | `agentic_core/runtime/` |
| `OutreachValidationExecutor` | `outreach_validation_executor.py` | ValidationGateExecutor | 12 | `agentic_core/runtime/` |
| `RiskCategory` | `pre_mortem_agent.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ImpactLevel` | `pre_mortem_agent.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `FailureMode` | `pre_mortem_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `PreMortemReport` | `pre_mortem_agent.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `SimpleAgentBase` | `pre_mortem_agent.py` | None | 1 | `agentic_core/runtime/` |
| `PreMortemAgent` | `pre_mortem_agent.py` | SimpleAgentBase | 8 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `pre_mortem_agent.py` | None | 1 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `pre_mortem_agent.py` | None | 1 | `agentic_core/runtime/` |
| `StandardType` | `quality_standards.py` | Enum | 0 | `agentic_core/runtime/` |
| `QualityDimension` | `quality_standards.py` | Enum | 0 | `agentic_core/runtime/` |
| `QualityStandard` | `quality_standards.py` | None | 1 | `agentic_core/runtime/` |
| `EngineQualityProfile` | `quality_standards.py` | None | 1 | `agentic_core/runtime/` |
| `CrossEngineQualityStandards` | `quality_standards.py` | None | 9 | `agentic_core/runtime/` |
| `DecomposedQuery` | `query_decomposer.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `SimpleAgentBase` | `query_decomposer.py` | None | 1 | `agentic_core/runtime/` |
| `QueryDecomposer` | `query_decomposer.py` | SimpleAgentBase | 2 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `query_decomposer.py` | None | 1 | `agentic_core/runtime/` |
| `LLMResponseImpl` | `query_decomposer.py` | None | 1 | `agentic_core/runtime/` |
| `RateLimitStrategy` | `rate_limiter.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RateLimitExceeded` | `rate_limiter.py` | Exception | 1 | `agentic_core/runtime/` |
| `RateLimitConfig` | `rate_limiter.py` | None | 1 | `agentic_core/runtime/` |
| `ClientState` | `rate_limiter.py` | None | 1 | `agentic_core/runtime/` |
| `RateLimiter` | `rate_limiter.py` | ABC | 1 | `agentic_core/runtime/` |
| `TokenBucketRateLimiter` | `rate_limiter.py` | RateLimiter | 3 | `agentic_core/runtime/` |
| `SlidingWindowRateLimiter` | `rate_limiter.py` | RateLimiter | 2 | `agentic_core/runtime/` |
| `RateLimitManager` | `rate_limiter.py` | None | 3 | `agentic_core/runtime/` |
| `GradeStatus` | `retrieval_grader.py` | Enum | 0 | `agentic_core/runtime/` |
| `RetrievalGrade` | `retrieval_grader.py` | None | 1 | `agentic_core/runtime/` |
| `RetrievalGrader` | `retrieval_grader.py` | None | 2 | `agentic_core/runtime/` |
| `WebSearchFallback` | `retrieval_grader.py` | None | 1 | `agentic_core/runtime/` |
| `RetryStrategy` | `retry_policy.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RetryableError` | `retry_policy.py` | Exception | 0 | `agentic_core/runtime/` |
| `NonRetryableError` | `retry_policy.py` | Exception | 0 | `agentic_core/runtime/` |
| `RetryConfig` | `retry_policy.py` | None | 1 | `agentic_core/runtime/` |
| `RetryAttempt` | `retry_policy.py` | None | 0 | `agentic_core/runtime/` |
| `RetryResult` | `retry_policy.py` | None | 0 | `agentic_core/runtime/` |
| `DelayCalculator` | `retry_policy.py` | None | 1 | `agentic_core/runtime/` |
| `RetryPolicy` | `retry_policy.py` | None | 3 | `agentic_core/runtime/` |
| `RetryableExecutor` | `retry_policy.py` | None | 2 | `agentic_core/runtime/` |
| `SDKCategory` | `sdk_registry.py` | Enum | 0 | `agentic_core/runtime/` |
| `SDKEntry` | `sdk_registry.py` | None | 2 | `agentic_core/runtime/` |
| `MockCollection` | `sdk_registry.py` | None | 3 | `agentic_core/runtime/` |
| `MockVectorStore` | `sdk_registry.py` | None | 7 | `agentic_core/runtime/` |
| `RepairStrategy` | `self_healing_formatter.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RepairResult` | `self_healing_formatter.py` | None | 0 | `agentic_core/runtime/` |
| `FormatRepair` | `self_healing_formatter.py` | ABC | 1 | `agentic_core/runtime/` |
| `JSONRepairStrategy` | `self_healing_formatter.py` | FormatRepair | 3 | `agentic_core/runtime/` |
| `MarkdownStripStrategy` | `self_healing_formatter.py` | FormatRepair | 2 | `agentic_core/runtime/` |
| `RegexExtractStrategy` | `self_healing_formatter.py` | FormatRepair | 2 | `agentic_core/runtime/` |
| `SchemaFillStrategy` | `self_healing_formatter.py` | FormatRepair | 2 | `agentic_core/runtime/` |
| `FallbackTextStrategy` | `self_healing_formatter.py` | FormatRepair | 1 | `agentic_core/runtime/` |
| `SelfHealingFormatter` | `self_healing_formatter.py` | None | 3 | `agentic_core/runtime/` |
| `EngineType` | `signal_infrastructure.py` | Enum | 0 | `agentic_core/runtime/` |
| `DomainConfig` | `signal_infrastructure.py` | None | 0 | `agentic_core/runtime/` |
| `DomainValidator` | `signal_infrastructure.py` | ABC | 2 | `agentic_core/runtime/` |
| `ResumeValidator` | `signal_infrastructure.py` | DomainValidator | 11 | `agentic_core/runtime/` |
| `OutreachValidator` | `signal_infrastructure.py` | DomainValidator | 11 | `agentic_core/runtime/` |
| `SharedSignalInfrastructure` | `signal_infrastructure.py` | None | 9 | `agentic_core/runtime/` |
| `QualityAssessment` | `signal_quality_pipeline.py` | BaseModel | 4 | `agentic_core/runtime/` |
| `SignalQualityPipeline` | `signal_quality_pipeline.py` | None | 8 | `agentic_core/runtime/` |
| `SignalWeights` | `signal_weighter.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `WeightingResult` | `signal_weighter.py` | BaseModel | 2 | `agentic_core/runtime/` |
| `SignalWeighter` | `signal_weighter.py` | None | 6 | `agentic_core/runtime/` |
| `Config` | `signal_weighter.py` | None | 0 | `agentic_core/runtime/` |
| `LegacyDiagnostic` | `stack_modernization_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `MigrationThesis` | `stack_modernization_agent.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `StackModernizationAgent` | `stack_modernization_agent.py` | None | 6 | `agentic_core/runtime/` |
| `ExecutiveSummaryOutput` | `strategist_biowriter.py` | None | 0 | `agentic_core/runtime/` |
| `Strategist_BioWriter` | `strategist_biowriter.py` | Agent | 5 | `agentic_core/runtime/` |
| `TalentMetrics` | `talent_signal_enhancer.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `TalentSignalEnhancer` | `talent_signal_enhancer.py` | None | 9 | `agentic_core/runtime/` |
| `RiskLevel` | `temperature_components.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `SentimentMood` | `temperature_components.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `DepthScore` | `temperature_components.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `MicroHook` | `temperature_components.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `SentimentProfile` | `temperature_components.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `WarmthSetting` | `temperature_components.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `DepthScorer` | `temperature_components.py` | None | 2 | `agentic_core/runtime/` |
| `MicroHookGenerator` | `temperature_components.py` | None | 2 | `agentic_core/runtime/` |
| `SentimentAnalyzer` | `temperature_components.py` | None | 2 | `agentic_core/runtime/` |
| `WarmthManager` | `temperature_components.py` | None | 2 | `agentic_core/runtime/` |
| `TemperatureEngine` | `temperature_components.py` | None | 3 | `agentic_core/runtime/` |
| `TestInputGuardrail` | `test_agentic_canon.py` | None | 8 | `agentic_core/runtime/` |
| `TestRetrievalGrader` | `test_agentic_canon.py` | None | 2 | `agentic_core/runtime/` |
| `TestWebSearchFallback` | `test_agentic_canon.py` | None | 1 | `agentic_core/runtime/` |
| `TestCypherQueryGenerator` | `test_agentic_canon.py` | None | 5 | `agentic_core/runtime/` |
| `TestGraphRAGFusion` | `test_agentic_canon.py` | None | 2 | `agentic_core/runtime/` |
| `TestTitaniumRAGPipelineIntegration` | `test_agentic_canon.py` | None | 2 | `agentic_core/runtime/` |
| `PrecisionLayerTestSuite` | `test_precision_layer.py` | None | 6 | `agentic_core/runtime/` |
| `ReasoningLayerTestSuite` | `test_reasoning_layer.py` | None | 4 | `agentic_core/runtime/` |
| `SOTALayerTestSuite` | `test_sota_layer.py` | None | 8 | `agentic_core/runtime/` |
| `TitaniumPipelineIntegrationTest` | `test_titanium_pipeline.py` | None | 2 | `agentic_core/runtime/` |
| `UberSignalTestSuite` | `test_uber_signal_agents.py` | None | 1 | `agentic_core/runtime/` |
| `TitaniumRAGPipeline` | `titanium_rag_pipeline.py` | None | 4 | `agentic_core/runtime/` |
| `ToneType` | `tone_model.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `StyleProfile` | `tone_model.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `GenerationConfig` | `tone_model.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `ToneAnalyzer` | `tone_model.py` | None | 8 | `agentic_core/runtime/` |
| `ToneAdapter` | `tone_model.py` | None | 4 | `agentic_core/runtime/` |
| `ToneModel` | `tone_model.py` | None | 3 | `agentic_core/runtime/` |
| `Config` | `tone_model.py` | None | 0 | `agentic_core/runtime/` |
| `ExecutionStatus` | `unified_executor.py` | Enum | 0 | `agentic_core/runtime/` |
| `ExecutionContext` | `unified_executor.py` | None | 1 | `agentic_core/runtime/` |
| `ExecutionResult` | `unified_executor.py` | None | 1 | `agentic_core/runtime/` |
| `ExecutionStrategy` | `unified_executor.py` | ABC | 1 | `agentic_core/runtime/` |
| `LLMExecutionStrategy` | `unified_executor.py` | ExecutionStrategy | 5 | `agentic_core/runtime/` |
| `APIExecutionStrategy` | `unified_executor.py` | ExecutionStrategy | 2 | `agentic_core/runtime/` |
| `BatchExecutionStrategy` | `unified_executor.py` | ExecutionStrategy | 2 | `agentic_core/runtime/` |
| `UnifiedExecutor` | `unified_executor.py` | None | 3 | `agentic_core/runtime/` |
| `EngineExecutor` | `unified_executor.py` | None | 3 | `agentic_core/runtime/` |
| `FeedbackCategory` | `unified_feedback.py` | Enum | 0 | `agentic_core/runtime/` |
| `CrossEngineFeedback` | `unified_feedback.py` | None | 1 | `agentic_core/runtime/` |
| `FeedbackAggregator` | `unified_feedback.py` | None | 8 | `agentic_core/runtime/` |
| `UnifiedFeedbackSystem` | `unified_feedback.py` | None | 8 | `agentic_core/runtime/` |
| `FormatType` | `unified_formatter.py` | Enum | 0 | `agentic_core/runtime/` |
| `FormatResult` | `unified_formatter.py` | None | 1 | `agentic_core/runtime/` |
| `FormatterStrategy` | `unified_formatter.py` | ABC | 2 | `agentic_core/runtime/` |
| `DefaultFormatter` | `unified_formatter.py` | FormatterStrategy | 2 | `agentic_core/runtime/` |
| `ResumeBulletFormatter` | `unified_formatter.py` | FormatterStrategy | 6 | `agentic_core/runtime/` |
| `ResumeSectionFormatter` | `unified_formatter.py` | FormatterStrategy | 7 | `agentic_core/runtime/` |
| `OutreachMessageFormatter` | `unified_formatter.py` | FormatterStrategy | 4 | `agentic_core/runtime/` |
| `OutreachSubjectFormatter` | `unified_formatter.py` | FormatterStrategy | 3 | `agentic_core/runtime/` |
| `JSONFormatter` | `unified_formatter.py` | FormatterStrategy | 2 | `agentic_core/runtime/` |
| `UnifiedFormatter` | `unified_formatter.py` | None | 4 | `agentic_core/runtime/` |
| `PipelineStageType` | `unified_signal_pipeline.py` | Enum | 0 | `agentic_core/runtime/` |
| `PipelineContext` | `unified_signal_pipeline.py` | None | 1 | `agentic_core/runtime/` |
| `PipelineStage` | `unified_signal_pipeline.py` | ABC | 1 | `agentic_core/runtime/` |
| `InputProcessingStage` | `unified_signal_pipeline.py` | PipelineStage | 4 | `agentic_core/runtime/` |
| `ContextEnrichmentStage` | `unified_signal_pipeline.py` | PipelineStage | 5 | `agentic_core/runtime/` |
| `SignalAugmentationStage` | `unified_signal_pipeline.py` | PipelineStage | 5 | `agentic_core/runtime/` |
| `QualityValidationStage` | `unified_signal_pipeline.py` | PipelineStage | 6 | `agentic_core/runtime/` |
| `OutputFormattingStage` | `unified_signal_pipeline.py` | PipelineStage | 17 | `agentic_core/runtime/` |
| `UnifiedSignalPipeline` | `unified_signal_pipeline.py` | None | 2 | `agentic_core/runtime/` |
| `PipelineExecutionError` | `unified_signal_pipeline.py` | Exception | 1 | `agentic_core/runtime/` |
| `ValidationStatus` | `validation_executor.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ValidationAction` | `validation_executor.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RuleFailure` | `validation_executor.py` | None | 0 | `agentic_core/runtime/` |
| `ValidationResult` | `validation_executor.py` | None | 1 | `agentic_core/runtime/` |
| `ValidationGateExecutor` | `validation_executor.py` | None | 19 | `agentic_core/runtime/` |
| `VectorStoreProvider` | `vector_store_clients.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ChromaConfig` | `vector_store_clients.py` | None | 0 | `agentic_core/runtime/` |
| `QdrantConfig` | `vector_store_clients.py` | None | 0 | `agentic_core/runtime/` |
| `PineconeConfig` | `vector_store_clients.py` | None | 0 | `agentic_core/runtime/` |
| `WorkflowContext` | `workflow_integration.py` | None | 3 | `agentic_core/runtime/` |
| `HopExecutionContext` | `workflow_integration.py` | None | 3 | `agentic_core/runtime/` |
| `WorkflowOrchestrator` | `workflow_integration.py` | None | 3 | `agentic_core/runtime/` |
| `CheckpointStorage` | `checkpoint_manager.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `CheckpointConfig` | `checkpoint_manager.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `CheckpointStorageBackend` | `checkpoint_manager.py` | ABC | 0 | `agentic_core/runtime/` |
| `FileCheckpointStorage` | `checkpoint_manager.py` | CheckpointStorageBackend | 3 | `agentic_core/runtime/` |
| `RedisCheckpointStorage` | `checkpoint_manager.py` | CheckpointStorageBackend | 2 | `agentic_core/runtime/` |
| `MemoryCheckpointStorage` | `checkpoint_manager.py` | CheckpointStorageBackend | 1 | `agentic_core/runtime/` |
| `CheckpointManager` | `checkpoint_manager.py` | None | 3 | `agentic_core/runtime/` |
| `PipelineStageStatus` | `envelope.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `PayloadType` | `envelope.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `PayloadBase` | `envelope.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ResumeData` | `envelope.py` | PayloadBase | 1 | `agentic_core/runtime/` |
| `OutreachData` | `envelope.py` | PayloadBase | 1 | `agentic_core/runtime/` |
| `RawText` | `envelope.py` | PayloadBase | 1 | `agentic_core/runtime/` |
| `DictData` | `envelope.py` | PayloadBase | 1 | `agentic_core/runtime/` |
| `ErrorPayload` | `envelope.py` | PayloadBase | 0 | `agentic_core/runtime/` |
| `StageResult` | `envelope.py` | BaseModel | 1 | `agentic_core/runtime/` |
| `SignalEnvelope` | `envelope.py` | GenericModel | 13 | `agentic_core/runtime/` |
| `EnvelopeFactory` | `envelope.py` | None | 2 | `agentic_core/runtime/` |
| `Config` | `envelope.py` | None | 0 | `agentic_core/runtime/` |
| `Config` | `envelope.py` | None | 0 | `agentic_core/runtime/` |
| `EventType` | `event_bus.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `SystemEvent` | `event_bus.py` | BaseModel | 2 | `agentic_core/runtime/` |
| `EventBus` | `event_bus.py` | ABC | 0 | `agentic_core/runtime/` |
| `MemoryEventBus` | `event_bus.py` | EventBus | 1 | `agentic_core/runtime/` |
| `RedisEventBus` | `event_bus.py` | EventBus | 1 | `agentic_core/runtime/` |
| `Config` | `event_bus.py` | None | 0 | `agentic_core/runtime/` |
| `ModelTier` | `model_router.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `TaskType` | `model_router.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `ModelConfig` | `model_router.py` | None | 0 | `agentic_core/runtime/` |
| `TaskProfile` | `model_router.py` | None | 0 | `agentic_core/runtime/` |
| `ModelRouter` | `model_router.py` | None | 12 | `agentic_core/runtime/` |
| `FallbackClient` | `model_router.py` | None | 3 | `agentic_core/runtime/` |
| `LLMClient` | `model_router.py` | ABC | 1 | `agentic_core/runtime/` |
| `OpenAIClient` | `model_router.py` | LLMClient | 0 | `agentic_core/runtime/` |
| `AnthropicClient` | `model_router.py` | LLMClient | 0 | `agentic_core/runtime/` |
| `SourceCitation` | `provenance_tracker.py` | None | 1 | `agentic_core/runtime/` |
| `ArtifactLineage` | `provenance_tracker.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `ProvenanceTracker` | `provenance_tracker.py` | None | 7 | `agentic_core/runtime/` |
| `ProvenanceContext` | `provenance_tracker.py` | None | 1 | `agentic_core/runtime/` |
| `Config` | `provenance_tracker.py` | None | 0 | `agentic_core/runtime/` |
| `AllProvidersDownError` | `router.py` | Exception | 1 | `agentic_core/runtime/` |
| `HardenedRouter` | `router.py` | None | 7 | `agentic_core/runtime/` |
| `RoutingTier` | `schema.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `RouteConfig` | `schema.py` | None | 3 | `agentic_core/runtime/` |
| `StatePersistenceError` | `atomic_manager.py` | Exception | 0 | `agentic_core/runtime/` |
| `AtomicStateManager` | `atomic_manager.py` | None | 12 | `agentic_core/runtime/` |
| `BackendType` | `schema.py` | str, Enum | 0 | `agentic_core/runtime/` |
| `CheckpointMetadata` | `schema.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `KNodeExecution` | `schema.py` | BaseModel | 0 | `agentic_core/runtime/` |
| `WorkflowState` | `schema.py` | BaseModel | 9 | `agentic_core/runtime/` |
| `Config` | `schema.py` | None | 0 | `agentic_core/runtime/` |
| `ExecutionStatus` | `get_schema_info.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `get_schema_info.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `get_schema_info.py` | None | 0 | `agentic_core/schemas/models/` |
| `GetSchemaInfo` | `get_schema_info.py` | None | 5 | `agentic_core/schemas/models/` |
| `ActionCapability` | `action_plane.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ActionRequest` | `action_plane.py` | None | 1 | `agentic_core/schemas/models/` |
| `ActionResult` | `action_plane.py` | None | 1 | `agentic_core/schemas/models/` |
| `IActionPlane` | `action_plane.py` | ABC | 3 | `agentic_core/schemas/models/` |
| `CognitiveCapability` | `cognitive_plane.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `PlanningRequest` | `cognitive_plane.py` | None | 1 | `agentic_core/schemas/models/` |
| `PlanningResult` | `cognitive_plane.py` | None | 1 | `agentic_core/schemas/models/` |
| `ICognitivePlane` | `cognitive_plane.py` | ABC | 1 | `agentic_core/schemas/models/` |
| `ExecutionPhase` | `orchestrator.py` | Enum | 0 | `agentic_core/L3_orchestration/` |
| `OrchestratorConfig` | `orchestrator.py` | None | 1 | `agentic_core/L3_orchestration/` |
| `ExecutionContext` | `orchestrator.py` | None | 1 | `agentic_core/L3_orchestration/` |
| `ExecutionResult` | `orchestrator.py` | None | 1 | `agentic_core/L3_orchestration/` |
| `IOrchestrator` | `orchestrator.py` | ABC | 2 | `agentic_core/L3_orchestration/` |
| `BudgetProfile` | `budget_profile.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ContextProfile` | `context_profile.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `GoldenStateTestCase` | `golden_state_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `JudgeVerdict` | `golden_state_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `EvalResult` | `golden_state_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `GoldenCase` | `golden_state_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `GoldenOutput` | `golden_state_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `StateOperation` | `l4_types.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `StateEventType` | `l4_types.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `StatePath` | `l4_types.py` | None | 3 | `agentic_core/schemas/models/` |
| `StateTransition` | `l4_types.py` | None | 1 | `agentic_core/schemas/models/` |
| `StateSnapshot` | `l4_types.py` | None | 1 | `agentic_core/schemas/models/` |
| `StateError` | `l4_types.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `StateValidationError` | `l4_types.py` | StateError | 0 | `agentic_core/schemas/models/` |
| `StateRollbackError` | `l4_types.py` | StateError | 0 | `agentic_core/schemas/models/` |
| `LLMProfile` | `llm_profile.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `Hypothesis` | `meta_metacognition_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `MetacognitionReport` | `meta_metacognition_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ValidationSeverity` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `Provider` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `APICallStatus` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ThematicAnalysis` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `RAGState` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ImmutableStagingBuffer` | `models.py` | None | 2 | `agentic_core/schemas/models/` |
| `SafetyProfile` | `safety_profile.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `SimScenario` | `simulation_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `SimOutcome` | `simulation_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `PromptType` | `l1_cms_schemas.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `PromptSchema` | `l1_cms_schemas.py` | None | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `l1_cms_schemas.py` | None | 1 | `agentic_core/schemas/models/` |
| `StrategyResult` | `l1_result_parser.py` | None | 0 | `agentic_core/schemas/models/` |
| `DraftResult` | `l1_result_parser.py` | None | 0 | `agentic_core/schemas/models/` |
| `QAResult` | `l1_result_parser.py` | None | 0 | `agentic_core/schemas/models/` |
| `SafetyResult` | `l1_result_parser.py` | None | 0 | `agentic_core/schemas/models/` |
| `ResultParser` | `l1_result_parser.py` | None | 4 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `check_schema_rules.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `check_schema_rules.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `check_schema_rules.py` | None | 0 | `agentic_core/schemas/models/` |
| `CheckSchemaRules` | `check_schema_rules.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `get_schema_info.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `get_schema_info.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `get_schema_info.py` | None | 0 | `agentic_core/schemas/models/` |
| `GetSchemaInfo` | `get_schema_info.py` | None | 5 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanType` | `check_schema_policy.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanConstraints` | `check_schema_policy.py` | None | 0 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanResult` | `check_schema_policy.py` | None | 0 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanProcessor` | `check_schema_policy.py` | ABC | 2 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanImpl` | `check_schema_policy.py` | CheckDataPolicyPlanProcessor | 5 | `agentic_core/schemas/models/` |
| `SecurityError` | `check_schema_policy.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanInterface` | `check_schema_policy.py` | None | 2 | `agentic_core/schemas/models/` |
| `CheckDataPolicyPlanFactory` | `check_schema_policy.py` | None | 1 | `agentic_core/schemas/models/` |
| `SchemaType` | `convert_to_internal_schema.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ConversionStrategy` | `convert_to_internal_schema.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `FieldMapping` | `convert_to_internal_schema.py` | None | 0 | `agentic_core/schemas/models/` |
| `InternalSchema` | `convert_to_internal_schema.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConversionConfig` | `convert_to_internal_schema.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConversionResult` | `convert_to_internal_schema.py` | None | 0 | `agentic_core/schemas/models/` |
| `InternalSchemaConverter` | `convert_to_internal_schema.py` | None | 22 | `agentic_core/schemas/models/` |
| `ContextMatchType` | `match_schema_context.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaContext` | `match_schema_context.py` | None | 0 | `agentic_core/schemas/models/` |
| `ContextMatchRequest` | `match_schema_context.py` | None | 0 | `agentic_core/schemas/models/` |
| `ContextMatchResult` | `match_schema_context.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaContextMatchResult` | `match_schema_context.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaContextConfig` | `match_schema_context.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaContextMatcher` | `match_schema_context.py` | None | 15 | `agentic_core/schemas/models/` |
| `SimilarityMethod` | `retrieve_schema_similarity.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `CompatibilityLevel` | `retrieve_schema_similarity.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaSimilarityRequest` | `retrieve_schema_similarity.py` | None | 0 | `agentic_core/schemas/models/` |
| `FieldMatch` | `retrieve_schema_similarity.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaSimilarityResult` | `retrieve_schema_similarity.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaSimilarityConfig` | `retrieve_schema_similarity.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaSimilarityRetriever` | `retrieve_schema_similarity.py` | None | 18 | `agentic_core/schemas/models/` |
| `SchemaSearchMode` | `search_schema_vectors.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaSimilarityType` | `search_schema_vectors.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaVectorEntry` | `search_schema_vectors.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaSearchQuery` | `search_schema_vectors.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaSearchResult` | `search_schema_vectors.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaVectorConfig` | `search_schema_vectors.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaVectorSearcher` | `search_schema_vectors.py` | None | 16 | `agentic_core/schemas/models/` |
| `HistoryAction` | `fetch_schema_history.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaChangeRecord` | `fetch_schema_history.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaHistoryQuery` | `fetch_schema_history.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaHistoryResult` | `fetch_schema_history.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaEvolutionSummary` | `fetch_schema_history.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaHistoryConfig` | `fetch_schema_history.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaHistoryFetcher` | `fetch_schema_history.py` | None | 11 | `agentic_core/schemas/models/` |
| `SchemaType` | `load_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationMode` | `load_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaScope` | `load_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaDefinition` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `ValidationRule` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaTransform` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaLoadPlan` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaLoadConfig` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaLoadResult` | `load_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaLoadPlanner` | `load_schema_planning.py` | None | 10 | `agentic_core/schemas/models/` |
| `SchemaType` | `query_schema_store.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaStatus` | `query_schema_store.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaMetadata` | `query_schema_store.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaEntry` | `query_schema_store.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaQuery` | `query_schema_store.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaQueryResult` | `query_schema_store.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaStoreConfig` | `query_schema_store.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaStoreQuerier` | `query_schema_store.py` | None | 16 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `pick_best_result.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `pick_best_result.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `pick_best_result.py` | None | 0 | `agentic_core/schemas/models/` |
| `PickBestResult` | `pick_best_result.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `state_update.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `state_update.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `state_update.py` | None | 0 | `agentic_core/schemas/models/` |
| `StateUpdate` | `state_update.py` | None | 5 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanType` | `rank_schema_components.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanConstraints` | `rank_schema_components.py` | None | 0 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanResult` | `rank_schema_components.py` | None | 0 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanProcessor` | `rank_schema_components.py` | ABC | 2 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanImpl` | `rank_schema_components.py` | RankDataComponentsPlanProcessor | 5 | `agentic_core/schemas/models/` |
| `SecurityError` | `rank_schema_components.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanInterface` | `rank_schema_components.py` | None | 2 | `agentic_core/schemas/models/` |
| `RankDataComponentsPlanFactory` | `rank_schema_components.py` | None | 1 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `check_schema_structure.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `check_schema_structure.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `check_schema_structure.py` | None | 0 | `agentic_core/schemas/models/` |
| `CheckSchemaStructure` | `check_schema_structure.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `convert_schema_content.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `convert_schema_content.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `convert_schema_content.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConvertSchemaContent` | `convert_schema_content.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `find_schema_diagnostics.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `find_schema_diagnostics.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `find_schema_diagnostics.py` | None | 0 | `agentic_core/schemas/models/` |
| `FindSchemaDiagnostics` | `find_schema_diagnostics.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `find_schema_problems.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `find_schema_problems.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `find_schema_problems.py` | None | 0 | `agentic_core/schemas/models/` |
| `FindSchemaProblems` | `find_schema_problems.py` | None | 5 | `agentic_core/schemas/models/` |
| `ExecutionStatus` | `get_schema_info.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ExecutionContext` | `get_schema_info.py` | None | 2 | `agentic_core/schemas/models/` |
| `ProcessingResult` | `get_schema_info.py` | None | 0 | `agentic_core/schemas/models/` |
| `GetSchemaInfo` | `get_schema_info.py` | None | 5 | `agentic_core/schemas/models/` |
| `SchemaType` | `orchestrate_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationLevel` | `orchestrate_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `TransformationType` | `orchestrate_schema_planning.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `SchemaDefinition` | `orchestrate_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `ValidationRule` | `orchestrate_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `TransformationPlan` | `orchestrate_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaPlanningConfig` | `orchestrate_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaPlanningResult` | `orchestrate_schema_planning.py` | None | 0 | `agentic_core/schemas/models/` |
| `SchemaPlanningOrchestrator` | `orchestrate_schema_planning.py` | None | 7 | `agentic_core/schemas/models/` |
| `OrchestrateDataPlanningOrchestratorImpl` | `orchestrate_schema_planning.py` | OrchestrateDataPlanningOrchestratorProcessor | 5 | `agentic_core/schemas/models/` |
| `SecurityError` | `orchestrate_schema_planning.py` | Exception | 0 | `agentic_core/schemas/models/` |
| `OrchestrateDataPlanningOrchestratorInterface` | `orchestrate_schema_planning.py` | None | 2 | `agentic_core/schemas/models/` |
| `OrchestrateDataPlanningOrchestratorFactory` | `orchestrate_schema_planning.py` | None | 1 | `agentic_core/schemas/models/` |
| `ExecutionResult` | `validation.py` | None | 0 | `agentic_core/schemas/models/` |
| `Validation` | `validation.py` | None | 9 | `agentic_core/schemas/models/` |
| `ExecutionResult` | `injection_patterns.py` | None | 0 | `agentic_core/schemas/models/` |
| `InjectionPatterns` | `injection_patterns.py` | None | 3 | `agentic_core/schemas/models/` |
| `ResultStatus` | `result_types.py` | Enum | 0 | `agentic_core/utils/` |
| `Result` | `result_types.py` | None | 2 | `agentic_core/utils/` |
| `ValidationResult` | `result_types.py` | Result | 1 | `agentic_core/utils/` |
| `ProcessingResult` | `result_types.py` | Result | 2 | `agentic_core/utils/` |
| `ActionResult` | `result_types.py` | Result | 1 | `agentic_core/utils/` |
| `ExecutionResult` | `result_types.py` | Result | 1 | `agentic_core/utils/` |
| `CacheEntry` | `semantic_cache.py` | None | 1 | `agentic_core/runtime/shared_runtime/semantic_cache.py` |
| `CacheHit` | `semantic_cache.py` | None | 0 | `agentic_core/runtime/shared_runtime/semantic_cache.py` |
| `CacheMiss` | `semantic_cache.py` | None | 0 | `agentic_core/runtime/shared_runtime/semantic_cache.py` |
| `SemanticCache` | `semantic_cache.py` | None | 8 | `agentic_core/runtime/shared_runtime/semantic_cache.py` |
| `BudgetExceededError` | `token_budget.py` | Exception | 1 | `agentic_core/runtime/shared_runtime/` |
| `TokenBudgetConfig` | `token_budget.py` | None | 0 | `agentic_core/runtime/shared_runtime/` |
| `TokenBudget` | `token_budget.py` | None | 7 | `agentic_core/runtime/shared_runtime/` |
| `ModelProvider` | `config.py` | Enum | 0 | `agentic_core/config/` |
| `ModelConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `RAGConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `GovernorConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `WorkflowConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `Config` | `config.py` | None | 0 | `agentic_core/config/` |
| `ContentConstraintsConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `SignalControlConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `GlobalConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `ModelProvider` | `reasoning_config.py` | str, Enum | 0 | `agentic_core/config/` |
| `ModelConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `RAGConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `GovernorConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `ReasoningConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `ModelProvider` | `config.py` | Enum | 0 | `agentic_core/config/` |
| `ModelConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `RAGConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `GovernorConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `WorkflowConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `Config` | `config.py` | None | 0 | `agentic_core/config/` |
| `ContentConstraintsConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `SignalControlConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `GlobalConfig` | `config.py` | None | 0 | `agentic_core/config/` |
| `AgenticWorkflowError` | `exceptions.py` | Exception | 0 | `agentic_core/utils/` |
| `HopExecutionError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `StagingBufferError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `CircuitBreakerOpenError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `PhaseTimeoutError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `ValidationError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `APIError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `ValidationSeverity` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ThematicAnalysis` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `Provider` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `APICallStatus` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `APICallMetrics` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `RAGState` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ImmutableStagingBuffer` | `models.py` | None | 2 | `agentic_core/schemas/models/` |
| `AgenticWorkflowError` | `exceptions.py` | Exception | 0 | `agentic_core/utils/` |
| `HopExecutionError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `StagingBufferError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `CircuitBreakerOpenError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `PhaseTimeoutError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `ValidationError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `APIError` | `exceptions.py` | AgenticWorkflowError | 0 | `agentic_core/utils/` |
| `ARCHIVE_FILE_ACCESS_DEPRECATED` | `placeholder_stub.py` | None | 0 | `agentic_core/utils/` |
| `MCPClient` | `client.py` | Protocol | 1 | `agentic_core/L2_execution/mcp/` |
| `MCPClientSpec` | `client.py` | None | 3 | `agentic_core/L2_execution/mcp/` |
| `MCPClientStub` | `client.py` | None | 3 | `agentic_core/L2_execution/mcp/` |
| `MCPClientRegistry` | `client.py` | None | 8 | `agentic_core/L2_execution/mcp/` |
| `MCPError` | `exceptions.py` | Exception | 0 | `agentic_core/L2_execution/mcp/` |
| `MCPClientInitializationError` | `exceptions.py` | MCPError | 1 | `agentic_core/L2_execution/mcp/` |
| `MCPClientNotFoundError` | `exceptions.py` | MCPError | 1 | `agentic_core/L2_execution/mcp/` |
| `MCPProviderError` | `exceptions.py` | MCPError | 1 | `agentic_core/L2_execution/mcp/` |
| `ProviderType` | `providers.py` | Enum | 0 | `agentic_core/L2_execution/mcp/` |
| `ReasoningMode` | `react_engine.py` | Enum | 0 | `agentic_core/utils/` |
| `ReActStep` | `react_engine.py` | None | 0 | `agentic_core/utils/` |
| `ReActTrace` | `react_engine.py` | None | 1 | `agentic_core/utils/` |
| `ReActEngine` | `react_engine.py` | None | 3 | `agentic_core/utils/` |
| `ModelProvider` | `reasoning_config.py` | str, Enum | 0 | `agentic_core/config/` |
| `ModelConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `RAGConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `GovernorConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `ReasoningConfig` | `reasoning_config.py` | None | 0 | `agentic_core/config/` |
| `TaskType` | `reasoning_router.py` | Enum | 0 | `agentic_core/utils/` |
| `ReasoningRouter` | `reasoning_router.py` | None | 4 | `agentic_core/utils/` |
| `ThinkStep` | `trace_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ActionStep` | `trace_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ObservationStep` | `trace_models.py` | BaseModel | 0 | `agentic_core/schemas/models/` |
| `ReasoningTraceModel` | `trace_models.py` | BaseModel | 7 | `agentic_core/schemas/models/` |
| `ConfigThinkStep` | `trace_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConfigActionStep` | `trace_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConfigObservationStep` | `trace_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ConfigReasoningTrace` | `trace_models.py` | None | 0 | `agentic_core/schemas/models/` |
| `BackoffStrategy` | `backoff.py` | ABC | 1 | `agentic_core/L4_resilience/` |
| `ExponentialBackoff` | `backoff.py` | BackoffStrategy | 1 | `agentic_core/L4_resilience/` |
| `LinearBackoff` | `backoff.py` | BackoffStrategy | 1 | `agentic_core/L4_resilience/` |
| `CircuitBreakerState` | `circuit_breaker.py` | Enum | 0 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreakerOpenError` | `circuit_breaker.py` | Exception | 1 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `CircuitBreaker` | `circuit_breaker.py` | None | 3 | `agentic_core/L4_resilience/circuit_breaker.py` |
| `RecoveryStrategy` | `error_recovery.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `ResilienceError` | `error_recovery.py` | None | 0 | `agentic_core/L4_resilience/` |
| `TransientError` | `error_recovery.py` | ResilienceError | 0 | `agentic_core/L4_resilience/` |
| `PermanentError` | `error_recovery.py` | ResilienceError | 0 | `agentic_core/L4_resilience/` |
| `RetryExhaustedError` | `error_recovery.py` | ResilienceError | 0 | `agentic_core/L4_resilience/` |
| `ErrorRecoveryManager` | `error_recovery.py` | None | 6 | `agentic_core/L4_resilience/` |
| `TokenLimitError` | `mixin.py` | Exception | 0 | `agentic_core/L4_resilience/` |
| `HardeningMixin` | `mixin.py` | None | 4 | `agentic_core/L4_resilience/` |
| `RateLimitExceeded` | `rate_limiter.py` | Exception | 1 | `agentic_core/L4_resilience/` |
| `TokenBucket` | `rate_limiter.py` | None | 4 | `agentic_core/L4_resilience/` |
| `FixedWindow` | `rate_limiter.py` | None | 3 | `agentic_core/L4_resilience/` |
| `RateLimiter` | `rate_limiter.py` | None | 5 | `agentic_core/L4_resilience/` |
| `OperationStatus` | `telemetry.py` | Enum | 0 | `agentic_core/L4_resilience/` |
| `TelemetryEvent` | `telemetry.py` | None | 0 | `agentic_core/L4_resilience/` |
| `SystemTelemetry` | `telemetry.py` | None | 6 | `agentic_core/L4_resilience/` |
| `BiasType` | `bias_auditor.py` | Enum | 0 | `agentic_core/utils/` |
| `BiasMatch` | `bias_auditor.py` | None | 0 | `agentic_core/utils/` |
| `BiasResult` | `bias_auditor.py` | None | 1 | `agentic_core/utils/` |
| `BiasAuditor` | `bias_auditor.py` | None | 5 | `agentic_core/utils/` |
| `RuleType` | `constitutional_ai.py` | Enum | 0 | `agentic_core/utils/` |
| `RuleSeverity` | `constitutional_ai.py` | Enum | 0 | `agentic_core/utils/` |
| `ViolationType` | `constitutional_ai.py` | Enum | 0 | `agentic_core/utils/` |
| `ConstitutionalRule` | `constitutional_ai.py` | None | 0 | `agentic_core/utils/` |
| `ViolationReport` | `constitutional_ai.py` | None | 0 | `agentic_core/utils/` |
| `ConstitutionalReviewResult` | `constitutional_ai.py` | None | 0 | `agentic_core/utils/` |
| `ConstitutionalAISystem` | `constitutional_ai.py` | None | 9 | `agentic_core/utils/` |
| `PolicyAction` | `control_plane.py` | Enum | 0 | `agentic_core/utils/` |
| `SafetyPolicy` | `control_plane.py` | None | 0 | `agentic_core/utils/` |
| `PolicyDecision` | `control_plane.py` | None | 1 | `agentic_core/utils/` |
| `ControlPlane` | `control_plane.py` | None | 10 | `agentic_core/utils/` |
| `PIIType` | `pii_scrubber.py` | Enum | 0 | `agentic_core/utils/` |
| `PIIMatch` | `pii_scrubber.py` | None | 0 | `agentic_core/utils/` |
| `PIIResult` | `pii_scrubber.py` | None | 2 | `agentic_core/utils/` |
| `PIIScrubber` | `pii_scrubber.py` | None | 5 | `agentic_core/utils/` |
| `ARCHIVE_FILE_ACCESS_DEPRECATED` | `placeholder_stub.py` | None | 0 | `agentic_core/utils/` |
| `ValidationSeverity` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `ValidationResult` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ThematicAnalysis` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `Provider` | `models.py` | str, Enum | 0 | `agentic_core/schemas/models/` |
| `APICallStatus` | `models.py` | Enum | 0 | `agentic_core/schemas/models/` |
| `APICallMetrics` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `RAGState` | `models.py` | None | 0 | `agentic_core/schemas/models/` |
| `ImmutableStagingBuffer` | `models.py` | None | 2 | `agentic_core/schemas/models/` |
| `CircuitState` | `workflow_types.py` | Enum | 0 | `agentic_core/utils/` |
| `HopStatus` | `workflow_types.py` | Enum | 0 | `agentic_core/utils/` |
| `GateDecision` | `workflow_types.py` | Enum | 0 | `agentic_core/utils/` |
| `BulletProvenance` | `workflow_types.py` | Enum | 0 | `agentic_core/utils/` |
| `HopCheckpoint` | `workflow_types.py` | None | 0 | `agentic_core/utils/` |
| `RetrievalSource` | `workflow_types.py` | None | 0 | `agentic_core/utils/` |

## Implementation Plan

```bash
# 1. Create migration branch
git checkout -b refactor/migrate-runtime-schemas-shared-2026

# 2. High-priority migrations (unique valuable code)
git mv archives/runtime\03_runtime_freeze_report.json agentic_core/runtime/03_runtime_freeze_report.json
git mv archives/runtime\core\cognitive_contracts.py agentic_core/schemas/models/cognitive_contracts.py
git mv archives/runtime\core\dynamic_dag_manager.py agentic_core/L3_orchestration/dynamic_dag_manager.py
git mv archives/runtime\core\prompt_assembler.py agentic_core/prompt_governance/prompt_assembler.py
git mv archives/runtime\core\reflection_engine.py agentic_core/runtime/shared_runtime/reflection_engine.py

# 3. Update imports (global replace)
# sed -i 's/from archives.runtime/from agentic_core.runtime/g' **/*.py
# sed -i 's/from archives.schemas/from agentic_core.schemas/g' **/*.py
# sed -i 's/from archives.shared/from agentic_core.utils/g' **/*.py

# 4. Run validation
python -m pytest tests/ -v
python -m mypy agentic_core/
```