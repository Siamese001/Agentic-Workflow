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
# NEW MODULES FROM LEGACY RESUME GEN PORT
# =============================================================================

from .signal_quality_pipeline import (
    # Enums
    SourceTier,
    SignalQualityStage,
    PipelineDecision,
    ClaimVerificationMode,
    # Dataclasses
    RetrievedDocument,
    StageResult,
    PipelineResult,
    HyDEConfig,
    SignalQualityConfig,
    SelfCritiqueResult,
    HopRefinementConfig,
    # Classes
    SignalQualityPipeline,
    HopRefinementStrategy,
    # Factory functions
    create_default_pipeline,
    create_strict_pipeline,
    create_permissive_pipeline,
)

from .validation_gates import (
    # Enums
    GatePolicy,
    GateDecision as VGateDecision,
    GateSeverity,
    # Dataclasses
    GateViolation,
    GateResult,
    GateContext,
    ValidationGateConfig,
    ValidationReport,
    # Base class
    ValidationGate,
    # Concrete gates
    SummaryGroundingCheckGate,
    BulletHallucinationCheckGate,
    ThematicUniquenessGate,
    CreativeBriefAdherenceGate,
    HeaderIntegrityCheckGate,
    BulletProvenanceCheckGate,
    RedundancyCheckGate,
    HyphenPreservationGate,
    WordCountBalanceGate,
    BulletPunctuationGate,
    SummaryVoiceTenseGate,
    AgenticOutputValidationGate,
    # Registry
    ValidationGateRegistry,
    generate_validation_report,
    # Factory functions
    create_default_registry,
    create_strict_registry,
    create_minimal_registry,
)

from .preflight import (
    # Enums
    PreflightTestType,
    PreflightResult,
    PreflightAction,
    # Dataclasses
    PreflightTestResult,
    PreflightReport,
    IterationTest,
    StructuralParseTest,
    FileManifestTest,
    DependencyTest,
    SchemaVersionTest,
    PreflightConfig,
    # Classes
    PreflightValidator,
    CapabilityTest,
    # Factory functions
    create_default_validator,
    create_strict_validator,
    create_minimal_validator,
    run_preflight_checks,
)

from .creative_brief import (
    # Enums
    VoiceType,
    TenseType,
    ProvenanceType,
    SourcingStrategy,
    # Constraint classes
    WordCountConstraint,
    CharCountConstraint,
    StructureConstraint,
    ForbiddenPatternConstraint,
    VoiceConstraint,
    # Section briefs
    HeadlineBrief,
    ExecutiveSummaryBrief,
    ExperienceBulletsBrief,
    CompetenciesBrief,
    CoverLetterBrief,
    SkillsListBrief,
    # Master brief
    CreativeBrief,
    # Factory functions
    create_default_brief,
    create_strict_brief,
    create_flexible_brief,
)

from .transaction_manager import (
    # Enums
    TransactionState,
    StepState,
    ExecutionTraceLevel,
    # Dataclasses
    Checkpoint,
    StepResult,
    ExecutionTrace,
    DependencyNode,
    TransactionConfig,
    # Classes
    DependencyGraph,
    TransactionManager,
    WorkflowExecutor,
    # Factory functions
    create_default_transaction_manager,
    create_strict_transaction_manager,
    create_workflow_executor,
)

from .schema_transform import (
    # Enums
    TransformAction,
    ValidationPolicy,
    TransformResult,
    # Dataclasses
    KeyMapping,
    EnumSpec,
    TransformViolation,
    TransformReport,
    SchemaTransformConfig,
    QASpec,
    # Classes
    SchemaTransformer,
    DataLossPreventionGate,
    ControlledVocabularyValidator,
    SchemaTransformationGate,
    # Factory functions
    create_default_transformer,
    create_strict_transformer,
    create_transformation_gate,
    # Constants
    RESUME_TRACKER_KEY_MAP,
)

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
    # NEW MODULES FROM LEGACY RESUME GEN PORT
    # ==========================================================================
    # Signal Quality Pipeline
    "SourceTier",
    "SignalQualityStage",
    "PipelineDecision",
    "ClaimVerificationMode",
    "RetrievedDocument",
    "StageResult",
    "PipelineResult",
    "HyDEConfig",
    "SignalQualityConfig",
    "SelfCritiqueResult",
    "HopRefinementConfig",
    "SignalQualityPipeline",
    "HopRefinementStrategy",
    "create_default_pipeline",
    "create_strict_pipeline",
    "create_permissive_pipeline",
    # Validation Gates
    "GatePolicy",
    "VGateDecision",
    "GateSeverity",
    "GateViolation",
    "GateResult",
    "GateContext",
    "ValidationGateConfig",
    "ValidationReport",
    "ValidationGate",
    "SummaryGroundingCheckGate",
    "BulletHallucinationCheckGate",
    "ThematicUniquenessGate",
    "CreativeBriefAdherenceGate",
    "HeaderIntegrityCheckGate",
    "BulletProvenanceCheckGate",
    "RedundancyCheckGate",
    "HyphenPreservationGate",
    "WordCountBalanceGate",
    "BulletPunctuationGate",
    "SummaryVoiceTenseGate",
    "AgenticOutputValidationGate",
    "ValidationGateRegistry",
    "generate_validation_report",
    "create_default_registry",
    "create_strict_registry",
    "create_minimal_registry",
    # Pre-Flight Validation
    "PreflightTestType",
    "PreflightResult",
    "PreflightAction",
    "PreflightTestResult",
    "PreflightReport",
    "IterationTest",
    "StructuralParseTest",
    "FileManifestTest",
    "DependencyTest",
    "SchemaVersionTest",
    "PreflightConfig",
    "PreflightValidator",
    "CapabilityTest",
    "create_default_validator",
    "create_strict_validator",
    "create_minimal_validator",
    "run_preflight_checks",
    # Creative Brief
    "VoiceType",
    "TenseType",
    "ProvenanceType",
    "SourcingStrategy",
    "WordCountConstraint",
    "CharCountConstraint",
    "StructureConstraint",
    "ForbiddenPatternConstraint",
    "VoiceConstraint",
    "HeadlineBrief",
    "ExecutiveSummaryBrief",
    "ExperienceBulletsBrief",
    "CompetenciesBrief",
    "CoverLetterBrief",
    "SkillsListBrief",
    "CreativeBrief",
    "create_default_brief",
    "create_strict_brief",
    "create_flexible_brief",
    # Transaction Manager
    "TransactionState",
    "StepState",
    "ExecutionTraceLevel",
    "Checkpoint",
    "StepResult",
    "ExecutionTrace",
    "DependencyNode",
    "TransactionConfig",
    "DependencyGraph",
    "TransactionManager",
    "WorkflowExecutor",
    "create_default_transaction_manager",
    "create_strict_transaction_manager",
    "create_workflow_executor",
    # Schema Transform
    "TransformAction",
    "ValidationPolicy",
    "TransformResult",
    "KeyMapping",
    "EnumSpec",
    "TransformViolation",
    "TransformReport",
    "SchemaTransformConfig",
    "QASpec",
    "SchemaTransformer",
    "DataLossPreventionGate",
    "ControlledVocabularyValidator",
    "SchemaTransformationGate",
    "create_default_transformer",
    "create_strict_transformer",
    "create_transformation_gate",
    "RESUME_TRACKER_KEY_MAP",
]
