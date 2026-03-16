# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "model_provider_config", "p0_governance")
_emit_reads_policy_state("p0", "model_provider_config", "policy_binding")
_emit_snapshots_state("p0", "model_provider_config", "state_snapshot")
emit_replay_key("p0", "model_provider_config")
emit_determinism_digest("p0", "model_provider_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Shared configuration constants and constraint classes.

This module contains configuration dataclasses for content constraints,
signal control, and other shared settings.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

# =============================================================================
# CORE CONSTANTS
# =============================================================================

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_API_TIMEOUT = 60.0
DEFAULT_GENERATION_TEMPERATURE = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE = 0.3
DEFAULT_MAX_OUTPUT_TOKENS = 4000
SAFETY_THRESHOLD = "MEDIUM_AND_ABOVE"

# =============================================================================
# PATH CONSTANTS
# =============================================================================

# Resolve absolute paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
LOGS_DIR = PROJECT_ROOT / AGENTIC_CORE_DIR / "L0_routing" / "logs"

# Ensure directories exist
for d in [DATA_DIR, OUTPUT_DIR, CACHE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# =============================================================================
# ENUMS & CONFIG CLASSES
# =============================================================================


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class ModelConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    Provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="Model provider")
    model_name: str = Field(default="gpt-4-turbo", description="Model name")
    api_key: str | None = Field(default=None, description="API key if required")
    temperature: float = Field(
        default=DEFAULT_GENERATION_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(default=DEFAULT_MAX_OUTPUT_TOKENS, ge=1, description="Maximum tokens")

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        """[HARDENED] Ensure model name is not empty."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ModelConfig.validate_model_name")

        if not value.strip():
            raise ValueError("model_name cannot be empty")
        return value.strip()


class RAGConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True, description="Whether RAG is enabled")
    chunk_size: int = Field(default=1000, ge=1, description="Chunk size for retrieval")
    chunk_overlap: int = Field(default=200, ge=0, description="Chunk overlap")
    retrieval_count: int = Field(default=5, ge=1, description="Number of chunks to retrieve")


class GovernorConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    strict_mode: bool = Field(default=True, description="Enable strict governance")
    constraints: ContentConstraintsConfig = Field(
        default_factory=lambda: ContentConstraintsConfig(),
        description="Content constraints configuration",
    )


class WorkflowConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_steps: int = Field(default=10, ge=1, description="Maximum workflow steps")
    stop_on_error: bool = Field(default=True, description="Stop on error")
    parallel_execution: bool = Field(default=False, description="Allow parallel execution")


class Config(BaseModel):
    """Legacy Config class for backward compatibility"""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: ModelConfig = Field(default_factory=ModelConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    governor: GovernorConfig = Field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)


# =============================================================================
# ORIGINAL CONTENT CONSTRAINTS (PRESERVED)
# =============================================================================


class ContentConstraintsConfig(BaseModel):
    """Centralized configuration for content constraints like word counts."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    # Overall Resume
    TOTAL_WORD_COUNT_MIN: int = 950
    TOTAL_WORD_COUNT_MAX: int = 1100
    MIN_JD_KEYWORDS: int = 5

    # K.0 Headline
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_MIN_CHARS: int = 60
    HEADLINE_MAX_CHARS: int = 90
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 5
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 6
    K1_MIN_DIFFERENTIATORS: int = 3

    # Experience Overviews
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 28
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 44
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 28
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 38
    EY_OVERVIEW_WORD_COUNT_MIN: int = 28
    EY_OVERVIEW_WORD_COUNT_MAX: int = 38
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 21
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 33
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 33

    # Word Distribution (Experience)
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    # K.13 Cover Letter
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 110
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 100
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 130
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 110
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


class SignalControlConfig(BaseModel):
    """configuration for signal quality control thresholds."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    # K.1 Executive Summary
    K1_MAX_DIFFERENTIATORS: int = 4

    # Overall Resume
    RESUME_MAX_JD_KEYWORDS: int = 15

    # K.13 Cover Letter
    CL_MAX_JD_SIMILARITY: float = 0.75

    # QA Report (Section 1)
    SECTION_SIGNAL_SCORE_MAX: float = 0.95


# =============================================================================
# GLOBAL CONFIG OBJECTS
# =============================================================================


class GlobalConfig(BaseModel):
    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: ModelConfig = Field(default_factory=ModelConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    governor: GovernorConfig = Field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)


# Singleton Instance
CONFIG = GlobalConfig()

# Default instances (preserved for backward compatibility)
CONTENT_CONSTRAINTS = ContentConstraintsConfig()
SIGNAL_CONTROL = SignalControlConfig()
