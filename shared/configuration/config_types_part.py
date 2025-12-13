"""Split module 1 for config_types."""

from dataclasses import dataclass, field
from enum import Enum

class ModelProvider(Enum):
    """TODO: Add docstring."""

    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    AZURE = 'azure'
    LOCAL = 'local'

@dataclass
    """TODO: Add docstring."""

class ModelConfig:
    provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = 'gpt-4-turbo'
    api_key: Optional[str] = None
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS

    """TODO: Add docstring."""

@dataclass
class RAGConfig:
    enabled: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_count: int = 5
    """TODO: Add docstring."""


@dataclass
class GovernorConfig:
    strict_mode: bool = True
    """TODO: Add docstring."""

    constraints: 'ContentConstraintsConfig' = field(default_factory=lambda: ContentConstraintsConfig())

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

@dataclass
class ContentConstraintsConfig:
    """Centralized configuration for content constraints like word counts."""
    TOTAL_WORD_COUNT_MIN: int = 950
    TOTAL_WORD_COUNT_MAX: int = 1100
    MIN_JD_KEYWORDS: int = 5
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_MIN_CHARS: int = 60
    HEADLINE_MAX_CHARS: int = 90
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 5
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 6
    K1_MIN_DIFFERENTIATORS: int = 3
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
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3
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
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 15
    """TODO: Add docstring."""

    CL_MAX_JD_SIMILARITY: float = 0.75
    SECTION_SIGNAL_SCORE_MAX: float = 0.95

@dataclass
class GlobalConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
