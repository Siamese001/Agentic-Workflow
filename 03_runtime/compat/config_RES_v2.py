"""
03_runtime/compat/config_RES_v2.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 7444e0800cdc8b1b33efe573d01c020010243008bff88e4df32e9d5a1c4716d7
"""


from __future__ import annotations

import warnings

# Emit deprecation warning on import
warnings.warn(
    "config_RES_v2 is deprecated. Use 'from agentic_workflow.runtime.shared import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all config from the canonical location
from ..shared.config import (
    # Paths
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_DIR,
    BACKUP_DIR,
    LOGS_DIR,
    CACHE_DIR,
    # Constants
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_API_TIMEOUT,
    DEFAULT_RATE_LIMIT_DELAY,
    DEFAULT_GENERATION_TEMPERATURE,
    DEFAULT_SYNTHESIS_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MIN_OUTPUT_TOKENS,
    SAFETY_THRESHOLD,
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    MAX_RETRIES_PER_NODE,
    MIN_WORD_COUNT_THRESHOLD,
    MAX_WORD_COUNT_BUFFER,
    MIN_BULLET_COUNT,
    MAX_BULLET_COUNT,
    MIN_CONFIDENCE_SCORE,
    MIN_RELEVANCE_SCORE,
    ACCEPTABLE_MIN_WC,
    ACCEPTABLE_MAX_WC,
    DEFAULT_SELF_CONSISTENCY_RUNS,
    MAX_SELF_CONSISTENCY_RUNS,
    MIN_SELF_CONSISTENCY_AGREEMENT,
    MAX_WORKFLOW_HOPS,
    DEFAULT_HOP_TIMEOUT,
    MAX_CONCURRENT_TASKS,
    CHECKPOINT_SAVE_INTERVAL,
    MIN_QUALITY_SCORE,
    MIN_COHERENCE_SCORE,
    MIN_FACTUAL_ACCURACY_SCORE,
    MAX_HALLUCINATION_SCORE,
    MAX_JOB_DESCRIPTION_LENGTH,
    MAX_RESUME_FILE_SIZE,
    MAX_LOG_FILE_SIZE,
    CACHE_TTL_SECONDS,
    MAX_CACHE_ENTRIES,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_TIMEOUT,
    CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS,
    # Enums
    ModelProvider,
    # Config classes
    ModelConfig,
    RAGConfig,
    PromptAddendumConfig,
    PROMPT_ADDENDUM_CONFIG,
    GovernorConfig,
    WorkflowConfig,
    ContentConstraintsConfig,
    SignalConstraintsConfig,
    Config,
    CONFIG,
    # Availability flags
    GEMINI_AVAILABLE,
    SKLEARN_AVAILABLE,
    CHROMADB_AVAILABLE,
    REDIS_AVAILABLE,
)

# Re-export ReasoningConfig from models (historically in config)
from ..shared.models import ReasoningConfig

__all__ = [
    # Paths
    "PROJECT_ROOT",
    "DATA_DIR",
    "OUTPUT_DIR",
    "BACKUP_DIR",
    "LOGS_DIR",
    "CACHE_DIR",
    # Constants
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_API_TIMEOUT",
    "DEFAULT_RATE_LIMIT_DELAY",
    "DEFAULT_GENERATION_TEMPERATURE",
    "DEFAULT_SYNTHESIS_TEMPERATURE",
    "DEFAULT_MAX_OUTPUT_TOKENS",
    "DEFAULT_MIN_OUTPUT_TOKENS",
    "SAFETY_THRESHOLD",
    "DEFAULT_MODEL",
    "FALLBACK_MODEL",
    "MAX_RETRIES_PER_NODE",
    "MIN_WORD_COUNT_THRESHOLD",
    "MAX_WORD_COUNT_BUFFER",
    "MIN_BULLET_COUNT",
    "MAX_BULLET_COUNT",
    "MIN_CONFIDENCE_SCORE",
    "MIN_RELEVANCE_SCORE",
    "ACCEPTABLE_MIN_WC",
    "ACCEPTABLE_MAX_WC",
    "DEFAULT_SELF_CONSISTENCY_RUNS",
    "MAX_SELF_CONSISTENCY_RUNS",
    "MIN_SELF_CONSISTENCY_AGREEMENT",
    "MAX_WORKFLOW_HOPS",
    "DEFAULT_HOP_TIMEOUT",
    "MAX_CONCURRENT_TASKS",
    "CHECKPOINT_SAVE_INTERVAL",
    "MIN_QUALITY_SCORE",
    "MIN_COHERENCE_SCORE",
    "MIN_FACTUAL_ACCURACY_SCORE",
    "MAX_HALLUCINATION_SCORE",
    "MAX_JOB_DESCRIPTION_LENGTH",
    "MAX_RESUME_FILE_SIZE",
    "MAX_LOG_FILE_SIZE",
    "CACHE_TTL_SECONDS",
    "MAX_CACHE_ENTRIES",
    "CIRCUIT_BREAKER_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_TIMEOUT",
    "CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS",
    # Enums
    "ModelProvider",
    # Config classes
    "ModelConfig",
    "RAGConfig",
    "PromptAddendumConfig",
    "PROMPT_ADDENDUM_CONFIG",
    "GovernorConfig",
    "WorkflowConfig",
    "ContentConstraintsConfig",
    "SignalConstraintsConfig",
    "Config",
    "CONFIG",
    "ReasoningConfig",
    # Availability flags
    "GEMINI_AVAILABLE",
    "SKLEARN_AVAILABLE",
    "CHROMADB_AVAILABLE",
    "REDIS_AVAILABLE",
]
