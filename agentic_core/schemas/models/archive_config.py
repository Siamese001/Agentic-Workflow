# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Shared configuration constants and constraint classes.

This module contains configuration dataclasses for content constraints,
signal control, and other shared settings.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

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
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / "cache"
LOGS_DIR = PROJECT_ROOT / "logs"

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


@dataclass
class ModelConfig:
    Provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-4-turbo"
    api_key: str | None = None
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS


@dataclass
class RAGConfig:
    enabled: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_count: int = 5


@dataclass
class GovernorConfig:
    strict_mode: bool = True
    constraints: ContentConstraintsConfig = field(
        default_factory=lambda: ContentConstraintsConfig()
    )


@dataclass
class WorkflowConfig:
    max_steps: int = 10
    stop_on_error: bool = True
    parallel_execution: bool = False


@dataclass
class Config:
    """Legacy Config class for backward compatibility"""

    model: ModelConfig = field(default_factory=ModelConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)


# =============================================================================
# ORIGINAL CONTENT CONSTRAINTS (PRESERVED)
# =============================================================================


@dataclass
class ContentConstraintsConfig:
    """Centralized configuration for content constraints like word counts."""

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


@dataclass
class SignalControlConfig:
    """Configuration for signal quality control thresholds."""

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


@dataclass
class GlobalConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)


# Singleton Instance
CONFIG = GlobalConfig()

# Default instances (preserved for backward compatibility)
CONTENT_CONSTRAINTS = ContentConstraintsConfig()
SIGNAL_CONTROL = SignalControlConfig()
