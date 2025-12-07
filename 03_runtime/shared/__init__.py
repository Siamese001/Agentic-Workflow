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
]
