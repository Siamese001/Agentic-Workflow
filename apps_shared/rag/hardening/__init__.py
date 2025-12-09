"""
03_runtime/shared/__init__.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 7d5b6ed86f6afb9d2ba4e4ca60be5e450370b4d2e95a94d3e9603409c08e4e1b
"""


from __future__ import annotations

from .exceptions import (
    AgenticWorkflowError,
    HopExecutionError,
    StagingBufferError,
    CircuitBreakerOpenError,
    PhaseTimeoutError,
    FactualFailureException,
    ValidationError,
    ConfigurationError,
    APIError,
    MCPClientInitializationError,
    SemanticCacheError,
    PipelineError,
)

from .models import (
    # Enums
    GateDecision,
    ValidationSeverity,
    ResumeSection,
    JDEnforcementRule,
    BulletProvenance,
    CircuitState,
    HopStatus,
    APICallStatus,
    # Dataclasses
    ReasoningConfig,
    ValidationResult,
    ThematicAnalysis,
    JDEnforcementResult,
    CompetitiveAnalysisConfig,
    RAGMission,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    RAGEvidence,
    RAGCritique,
    RAGState,
    CompetitiveIntelligence,
    RetrievalSource,
    PartialRAGResult,
    RAGTelemetry,
    HopCheckpoint,
    APICallMetrics,
    # Classes
    ImmutableStagingBuffer,
)

from .config import (
    # Constants
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_API_TIMEOUT,
    DEFAULT_GENERATION_TEMPERATURE,
    DEFAULT_SYNTHESIS_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
    SAFETY_THRESHOLD,
    # Config classes
    ModelProvider,
    ModelConfig,
    RAGConfig,
    GovernorConfig,
    WorkflowConfig,
    ContentConstraintsConfig,
    Config,
    CONFIG,
    # Paths
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_DIR,
    CACHE_DIR,
    LOGS_DIR,
)

from .utils import (
    TextUtils,
    text_utils,
    DuplicateDetector,
    TelemetryLogger,
    WorkflowLogFilter,
    setup_workflow_logging,
    create_directory_if_missing,
    sanitize_filename,
    calculate_signal_score,
    reasoning_config_to_api_params,
    enhance_system_prompt_with_reasoning,
    build_generation_prompt_with_reinforced_constraints,
)

from .clients import (
    get_openai_client,
    get_openai_sync_client,
    reset_clients,
    get_default_seed,
    OPENAI_MAX_RETRIES,
    OPENAI_TIMEOUT,
    OPENAI_DEFAULT_SEED,
)

from .cache import (
    generate_llm_cache_key,
    generate_llm_cache_key_with_fingerprint,
    extract_cache_metadata,
    should_invalidate_cache,
    CACHE_KEY_PREFIX,
    CACHE_KEY_VERSION,
)

from .multi_provider_clients import (
    Provider,
    ProviderConfig,
    get_client,
    get_api_key,
    reset_all_clients,
    get_available_providers,
    get_litellm_completion,
    get_litellm_completion_sync,
    get_structured_output,
)

from .sdk_registry import (
    # Enums
    SDKCategory,
    # Registry
    SDKEntry,
    SDK_REGISTRY,
    # Validation
    validate_sdk,
    validate_all_sdks,
    get_available_sdks,
    # Vector Stores
    ChromaConfig,
    QdrantConfig,
    PineconeConfig,
    get_vector_store,
    # Redis
    RedisConfig,
    get_redis_client,
    # Tracing
    TracingConfig,
    setup_tracing,
    get_tracer,
    # MCP
    MCPServerConfig,
    create_mcp_server,
    create_mcp_tool_from_function,
    # Document Processing
    parse_document,
    extract_pdf_text,
)

# =============================================================================
# LEGACY ENGINE PORTS — Constitutional AI, Retrieval, Quality, etc.
# =============================================================================

from .pii_scrubber import (
    PIIType,
    PIIMatch,
    PIIResult,
    PIIScrubber,
    create_pii_scrubber,
    scrub_pii,
)

from .bias_auditor import (
    BiasType,
    BiasSeverity,
    BiasMatch,
    BiasResult,
    BiasAuditor,
    create_bias_auditor,
    audit_bias,
)

from .constitutional_ai import (
    RuleType,
    RuleSeverity,
    ViolationType,
    RuleAction,
    ConstitutionalRule,
    ViolationReport,
    ConstitutionalReviewResult,
    RuleEngine,
    ContentValidator,
    ConstitutionalAISystem,
    create_constitutional_ai_system,
    create_rule_engine,
    create_content_validator,
    review_content,
)

from .goal_injection import (
    GoalType,
    GoalPriority,
    StrategicGoal,
    GoalState,
    InjectionResult,
    GoalStateInjector,
    create_goal_injector,
    inject_goals,
    create_business_goal,
    create_quality_goal,
)

from .hyde_processor import (
    ExpansionStrategy,
    HyDEDocument,
    HyDEResult,
    HyDEProcessor,
    create_hyde_processor,
    expand_query_with_hyde,
    generate_hypothetical_profile,
)

from .signal_weighter import (
    SignalType,
    SignalWeights,
    WeightedResult,
    WeightingResult,
    SignalWeighter,
    create_signal_weighter,
    weight_results,
    create_weights,
)

from .hybrid_scorer import (
    ScoringConfig,
    ScoringResult,
    HybridScoringResult,
    BM25Scorer,
    SemanticScorer,
    HybridScorer,
    create_hybrid_scorer,
    create_bm25_scorer,
    score_documents,
)

from .evidence_ranker import (
    EvidenceType,
    EvidenceQuality,
    EvidenceItem,
    RankingResult,
    EvidenceRanker,
    create_evidence_ranker,
    rank_evidence,
)

from .tone_model import (
    ToneType,
    FormalityLevel,
    ToneProfile,
    ToneAdaptation,
    AdvancedToneModel,
    create_tone_model,
    adapt_tone,
)

from .claim_confidence import (
    ClaimType,
    ConfidenceLevel,
    Claim,
    ClaimAnalysisResult,
    ClaimConfidenceScorer,
    create_claim_scorer,
    analyze_claims,
)

from .goal_alignment import (
    GoalCategory,
    AlignmentStrategy,
    AlignmentResult,
    GoalAlignmentEngine,
    create_goal_alignment_engine,
    align_prompt_with_goals,
    create_strategic_goal,
)

from .prompt_optimizer import (
    OptimizationStrategy,
    OptimizationLevel,
    OptimizationConfig,
    OptimizationResult,
    PromptOptimizer,
    create_prompt_optimizer,
    optimize_prompt,
    create_optimization_config,
)

from .meta_learning import (
    FeedbackType,
    PatternType,
    LearningMode,
    FeedbackSignal,
    LearningPattern,
    AdaptationResult,
    FeedbackCollector,
    PatternRecognizer,
    AdaptiveParameterTuner,
    MetaLearningSystem,
    create_meta_learning_system,
    create_feedback_collector,
    create_pattern_recognizer,
    record_feedback,
)

from .business_intelligence import (
    BusinessStage,
    MarketPosition,
    ProductCategory,
    CompanyInsights,
    ProductInsights,
    IntelligenceResult,
    CompanyIntelligenceBundle,
    ProductIntelligenceBundle,
    IntelligenceBundleSystem,
    create_intelligence_system,
    create_company_bundle,
    create_product_bundle,
    analyze_company,
    analyze_product,
)

from .rag_components import (
    # Semantic Cache
    CacheEntry,
    CacheSufficiencyResult,
    SemanticCache,
    create_semantic_cache,
    # Self-RAG
    GapType,
    KnowledgeGap,
    SelfRAGResult,
    SelfRAGProcessor,
    create_self_rag_processor,
    # Episodic Memory
    Episode,
    EpisodicMemoryResult,
    EpisodicMemory,
    create_episodic_memory,
    # Knowledge Graph
    KGRelationship,
    KGContext,
    KnowledgeGraphInjector,
    create_kg_injector,
    # Few-Shot
    FewShotExample,
    FewShotInjectionResult,
    FewShotInjector,
    create_few_shot_injector,
)

from .orchestration import (
    # Error Recovery
    RecoveryStrategy,
    CircuitBreakerConfig,
    RetryConfig,
    RecoveryResult,
    CircuitBreaker,
    ErrorRecoveryManager,
    create_error_recovery_manager,
    create_circuit_breaker,
    # Execution Trace
    TraceLevel,
    TraceStep,
    ExecutionTrace,
    ExecutionTracer,
    create_execution_tracer,
    # Fusion Planner
    ValueProposition,
    MessageSectionPlan,
    FusionPlan,
    FusionPlanner,
    create_fusion_planner,
)

from .state_management import (
    # Text Sanitizer
    SanitizationLevel,
    SanitizationResult,
    TextSanitizer,
    create_text_sanitizer,
    sanitize_text,
    # Validation Context
    ValidationIssue,
    ValidationContextResult,
    ValidationContext,
    create_validation_context,
    # Workflow State
    WorkflowPhase,
    WorkflowCheckpoint,
    WorkflowState,
    WorkflowStateManager,
    create_workflow_state_manager,
    create_staging_buffer,
)

# =============================================================================
# LEGACY RESUME GEN PORT — NOW IN apps_shared/rag/hardening/
# Import from there directly:
#   from apps_shared.rag.hardening import SignalQualityPipeline, ...
# =============================================================================

__all__ = [
    # Exceptions
    "AgenticWorkflowError",
    "HopExecutionError",
    "StagingBufferError",
    "CircuitBreakerOpenError",
    "PhaseTimeoutError",
    "FactualFailureException",
    "ValidationError",
    "ConfigurationError",
    "APIError",
    "MCPClientInitializationError",
    "SemanticCacheError",
    "PipelineError",
    # Enums
    "GateDecision",
    "ValidationSeverity",
    "ResumeSection",
    "JDEnforcementRule",
    "BulletProvenance",
    "CircuitState",
    "HopStatus",
    "APICallStatus",
    # Dataclasses
    "ReasoningConfig",
    "ValidationResult",
    "ThematicAnalysis",
    "JDEnforcementResult",
    "CompetitiveAnalysisConfig",
    "RAGMission",
    "SkillRequirement",
    "SkillCluster",
    "MasterResumeIndex",
    "RAGEvidence",
    "RAGCritique",
    "RAGState",
    "CompetitiveIntelligence",
    "RetrievalSource",
    "PartialRAGResult",
    "RAGTelemetry",
    "HopCheckpoint",
    "APICallMetrics",
    # Classes
    "ImmutableStagingBuffer",
    # Config
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_API_TIMEOUT",
    "DEFAULT_GENERATION_TEMPERATURE",
    "DEFAULT_SYNTHESIS_TEMPERATURE",
    "DEFAULT_MAX_OUTPUT_TOKENS",
    "SAFETY_THRESHOLD",
    "ModelProvider",
    "ModelConfig",
    "RAGConfig",
    "GovernorConfig",
    "WorkflowConfig",
    "ContentConstraintsConfig",
    "Config",
    "CONFIG",
    "PROJECT_ROOT",
    "DATA_DIR",
    "OUTPUT_DIR",
    "CACHE_DIR",
    "LOGS_DIR",
    # Utils
    "TextUtils",
    "text_utils",
    "DuplicateDetector",
    "TelemetryLogger",
    "WorkflowLogFilter",
    "setup_workflow_logging",
    "create_directory_if_missing",
    "sanitize_filename",
    "calculate_signal_score",
    "reasoning_config_to_api_params",
    "enhance_system_prompt_with_reasoning",
    "build_generation_prompt_with_reinforced_constraints",
    # Clients
    "get_openai_client",
    "get_openai_sync_client",
    "reset_clients",
    "get_default_seed",
    "OPENAI_MAX_RETRIES",
    "OPENAI_TIMEOUT",
    "OPENAI_DEFAULT_SEED",
    # Cache
    "generate_llm_cache_key",
    "generate_llm_cache_key_with_fingerprint",
    "extract_cache_metadata",
    "should_invalidate_cache",
    "CACHE_KEY_PREFIX",
    "CACHE_KEY_VERSION",
    # Multi-Provider Clients
    "Provider",
    "ProviderConfig",
    "get_client",
    "get_api_key",
    "reset_all_clients",
    "get_available_providers",
    "get_litellm_completion",
    "get_litellm_completion_sync",
    "get_structured_output",
    # SDK Registry
    "SDKCategory",
    "SDKEntry",
    "SDK_REGISTRY",
    "validate_sdk",
    "validate_all_sdks",
    "get_available_sdks",
    # Vector Stores
    "ChromaConfig",
    "QdrantConfig",
    "PineconeConfig",
    "get_vector_store",
    # Redis
    "RedisConfig",
    "get_redis_client",
    # Tracing
    "TracingConfig",
    "setup_tracing",
    "get_tracer",
    # MCP
    "MCPServerConfig",
    "create_mcp_server",
    "create_mcp_tool_from_function",
    # Document Processing
    "parse_document",
    "extract_pdf_text",
    # ==========================================================================
    # LEGACY ENGINE PORTS
    # ==========================================================================
    # PII Scrubber
    "PIIType",
    "PIIMatch",
    "PIIResult",
    "PIIScrubber",
    "create_pii_scrubber",
    "scrub_pii",
    # Bias Auditor
    "BiasType",
    "BiasSeverity",
    "BiasMatch",
    "BiasResult",
    "BiasAuditor",
    "create_bias_auditor",
    "audit_bias",
    # Constitutional AI
    "RuleType",
    "RuleSeverity",
    "ViolationType",
    "RuleAction",
    "ConstitutionalRule",
    "ViolationReport",
    "ConstitutionalReviewResult",
    "RuleEngine",
    "ContentValidator",
    "ConstitutionalAISystem",
    "create_constitutional_ai_system",
    "create_rule_engine",
    "create_content_validator",
    "review_content",
    # Goal Injection
    "GoalType",
    "GoalPriority",
    "StrategicGoal",
    "GoalState",
    "InjectionResult",
    "GoalStateInjector",
    "create_goal_injector",
    "inject_goals",
    "create_business_goal",
    "create_quality_goal",
    # HyDE Processor
    "ExpansionStrategy",
    "HyDEDocument",
    "HyDEResult",
    "HyDEProcessor",
    "create_hyde_processor",
    "expand_query_with_hyde",
    "generate_hypothetical_profile",
    # Signal Weighter
    "SignalType",
    "SignalWeights",
    "WeightedResult",
    "WeightingResult",
    "SignalWeighter",
    "create_signal_weighter",
    "weight_results",
    "create_weights",
    # Hybrid Scorer
    "ScoringConfig",
    "ScoringResult",
    "HybridScoringResult",
    "BM25Scorer",
    "SemanticScorer",
    "HybridScorer",
    "create_hybrid_scorer",
    "create_bm25_scorer",
    "score_documents",
    # Evidence Ranker
    "EvidenceType",
    "EvidenceQuality",
    "EvidenceItem",
    "RankingResult",
    "EvidenceRanker",
    "create_evidence_ranker",
    "rank_evidence",
    # Tone Model
    "ToneType",
    "FormalityLevel",
    "ToneProfile",
    "ToneAdaptation",
    "AdvancedToneModel",
    "create_tone_model",
    "adapt_tone",
    # Claim Confidence
    "ClaimType",
    "ConfidenceLevel",
    "Claim",
    "ClaimAnalysisResult",
    "ClaimConfidenceScorer",
    "create_claim_scorer",
    "analyze_claims",
    # Goal Alignment
    "GoalCategory",
    "AlignmentStrategy",
    "AlignmentResult",
    "GoalAlignmentEngine",
    "create_goal_alignment_engine",
    "align_prompt_with_goals",
    "create_strategic_goal",
    # Prompt Optimizer
    "OptimizationStrategy",
    "OptimizationLevel",
    "OptimizationConfig",
    "OptimizationResult",
    "PromptOptimizer",
    "create_prompt_optimizer",
    "optimize_prompt",
    "create_optimization_config",
    # Meta-Learning
    "FeedbackType",
    "PatternType",
    "LearningMode",
    "FeedbackSignal",
    "LearningPattern",
    "AdaptationResult",
    "FeedbackCollector",
    "PatternRecognizer",
    "AdaptiveParameterTuner",
    "MetaLearningSystem",
    "create_meta_learning_system",
    "create_feedback_collector",
    "create_pattern_recognizer",
    "record_feedback",
    # Business Intelligence
    "BusinessStage",
    "MarketPosition",
    "ProductCategory",
    "CompanyInsights",
    "ProductInsights",
    "IntelligenceResult",
    "CompanyIntelligenceBundle",
    "ProductIntelligenceBundle",
    "IntelligenceBundleSystem",
    "create_intelligence_system",
    "create_company_bundle",
    "create_product_bundle",
    "analyze_company",
    "analyze_product",
    # RAG Components - Semantic Cache
    "CacheEntry",
    "CacheSufficiencyResult",
    "SemanticCache",
    "create_semantic_cache",
    # RAG Components - Self-RAG
    "GapType",
    "KnowledgeGap",
    "SelfRAGResult",
    "SelfRAGProcessor",
    "create_self_rag_processor",
    # RAG Components - Episodic Memory
    "Episode",
    "EpisodicMemoryResult",
    "EpisodicMemory",
    "create_episodic_memory",
    # RAG Components - Knowledge Graph
    "KGRelationship",
    "KGContext",
    "KnowledgeGraphInjector",
    "create_kg_injector",
    # RAG Components - Few-Shot
    "FewShotExample",
    "FewShotInjectionResult",
    "FewShotInjector",
    "create_few_shot_injector",
    # Orchestration - Error Recovery
    "RecoveryStrategy",
    "CircuitBreakerConfig",
    "RetryConfig",
    "RecoveryResult",
    "CircuitBreaker",
    "ErrorRecoveryManager",
    "create_error_recovery_manager",
    "create_circuit_breaker",
    # Orchestration - Execution Trace
    "TraceLevel",
    "TraceStep",
    "ExecutionTrace",
    "ExecutionTracer",
    "create_execution_tracer",
    # Orchestration - Fusion Planner
    "ValueProposition",
    "MessageSectionPlan",
    "FusionPlan",
    "FusionPlanner",
    "create_fusion_planner",
    # State Management - Text Sanitizer
    "SanitizationLevel",
    "SanitizationResult",
    "TextSanitizer",
    "create_text_sanitizer",
    "sanitize_text",
    # State Management - Validation Context
    "ValidationIssue",
    "ValidationContextResult",
    "ValidationContext",
    "create_validation_context",
    # State Management - Workflow State
    "WorkflowPhase",
    "WorkflowCheckpoint",
    "WorkflowState",
    "WorkflowStateManager",
    "create_workflow_state_manager",
    "create_staging_buffer",
]
