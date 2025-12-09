"""
03_runtime/shared/config.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 37431f4a44f427d6dc6b242b1bd0cc7faa82bae43b8a7d9659fd4136a8094e8b
"""


from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Get absolute paths - use environment variable or default
_env_root = os.environ.get("AGENTIC_WORKFLOW_ROOT")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    # Default to the Agentic-Workflow directory
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "06_data"
OUTPUT_DIR = PROJECT_ROOT / "workflow_outputs"
BACKUP_DIR = PROJECT_ROOT / "backups"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist (only if we have write access)
for dir_path in [OUTPUT_DIR, BACKUP_DIR, LOGS_DIR, CACHE_DIR]:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        pass  # Skip if we can't create directories


# =============================================================================
# SYSTEM CONSTANTS - SINGLE SOURCE OF TRUTH
# =============================================================================

# API Configuration
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_DELAY: float = 2.0
DEFAULT_API_TIMEOUT: int = 30  # seconds
DEFAULT_RATE_LIMIT_DELAY: float = 5.0  # seconds

# Generation Parameters
DEFAULT_GENERATION_TEMPERATURE: float = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE: float = 0.3
DEFAULT_MAX_OUTPUT_TOKENS: int = 8192
DEFAULT_MIN_OUTPUT_TOKENS: int = 100

# Safety Configuration
SAFETY_THRESHOLD: str = "BLOCK_NONE"

# Model Configuration
DEFAULT_MODEL: str = "gemini-2.0-flash-exp"
FALLBACK_MODEL: str = "gemini-1.5-pro"
MAX_RETRIES_PER_NODE: int = DEFAULT_MAX_RETRIES

# Validation Thresholds
MIN_WORD_COUNT_THRESHOLD: int = 5
MAX_WORD_COUNT_BUFFER: int = 10
MIN_BULLET_COUNT: int = 5
MAX_BULLET_COUNT: int = 8
MIN_CONFIDENCE_SCORE: float = 0.7
MIN_RELEVANCE_SCORE: float = 0.65

# Bullet Word Count Constraints
ACCEPTABLE_MIN_WC: int = 21
ACCEPTABLE_MAX_WC: int = 44

# Self-Consistency Parameters
DEFAULT_SELF_CONSISTENCY_RUNS: int = 3
MAX_SELF_CONSISTENCY_RUNS: int = 5
MIN_SELF_CONSISTENCY_AGREEMENT: float = 0.8

# Workflow Constants
MAX_WORKFLOW_HOPS: int = 10
DEFAULT_HOP_TIMEOUT: int = 300  # seconds (5 minutes)
MAX_CONCURRENT_TASKS: int = 4
CHECKPOINT_SAVE_INTERVAL: int = 2

# Quality Thresholds
MIN_QUALITY_SCORE: float = 0.75
MIN_COHERENCE_SCORE: float = 0.8
MIN_FACTUAL_ACCURACY_SCORE: float = 0.9
MAX_HALLUCINATION_SCORE: float = 0.1

# File Size Limits
MAX_JOB_DESCRIPTION_LENGTH: int = 50000  # characters
MAX_RESUME_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
MAX_LOG_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

# Cache Configuration
CACHE_TTL_SECONDS: int = 3600  # 1 hour
MAX_CACHE_ENTRIES: int = 100

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
CIRCUIT_BREAKER_TIMEOUT: int = 60  # seconds
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS: int = 3


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _load_json_config(
    file_path: Path | str,
    config_name: str,
    required: bool = True,
) -> Dict[str, Any]:
    """
    Load JSON configuration file with error handling.

    Args:
        file_path: Path to JSON file
        config_name: Name for logging
        required: Whether file is required

    Returns:
        Loaded JSON data or empty dict
    """
    try:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"✓ Loaded {config_name} from {path}")
            return data
    except FileNotFoundError:
        if required:
            logger.warning(f"⚠ Required config file not found: {file_path}")
            return {}
        else:
            logger.debug(f"Optional config file not found: {file_path}")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"✗ Invalid JSON in {file_path}: {e}")
        return {}


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

class ModelProvider(Enum):
    """Supported model providers."""
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    provider: ModelProvider = ModelProvider.GEMINI
    default_model: str = DEFAULT_MODEL
    fallback_model: str = FALLBACK_MODEL
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    top_p: float = 1.0
    top_k: int = 40
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


# =============================================================================
# RAG CONFIGURATION
# =============================================================================

@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    model: str = DEFAULT_MODEL
    top_k: int = 5
    max_top_k: int = 20
    enable_reranking: bool = True
    rerank_top_k: int = 3
    min_similarity_score: float = 0.5
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    enable_cache: bool = True
    cache_ttl: int = CACHE_TTL_SECONDS
    min_retrieval_confidence: float = MIN_CONFIDENCE_SCORE
    enable_cross_validation: bool = True
    # Backoff configuration
    api_initial_backoff_seconds: float = 2.0
    api_backoff_multiplier: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_jitter: float = 0.1


# =============================================================================
# PROMPT ADDENDUM CONFIGURATION
# =============================================================================

@dataclass
class PromptAddendumConfig:
    """Configuration for reasoning prompt addendums."""
    HEADER: str = "\n\n--- REASONING DIRECTIVES ---\n"
    FOOTER: str = "\n--- END REASONING DIRECTIVES ---\n"

    COT_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (5, "Generate at least {cot} distinct chains of reasoning. Show each step explicitly.\n"),
        (3, "Use multi-step reasoning with at least {cot} distinct chains of thought.\n"),
        (1, "Apply step-by-step reasoning through {cot} chain(s) of thought.\n"),
    ])

    TOT_B_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (5, "Explore {tot_b} diverse solution branches. Evaluate each independently.\n"),
        (3, "Consider {tot_b} different approaches before selecting the best.\n"),
        (2, "Generate {tot_b} alternative solutions and compare them.\n"),
    ])

    TOT_D_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (3, "Explore each branch to depth {tot_d} with recursive reasoning.\n"),
        (2, "Reason through {tot_d} levels of depth for each approach.\n"),
        (1, "Apply {tot_d}-level deep reasoning.\n"),
    ])

    REFLEXION_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (3, "Apply self-critique with up to {max_loops} refinement iterations.\n"),
        (2, "Review and refine your response through {max_loops} reflection loops.\n"),
        (1, "Reflect on and improve your answer in {max_loops} iteration(s).\n"),
    ])


PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()


# =============================================================================
# GOVERNOR CONFIGURATION
# =============================================================================

@dataclass
class GovernorConfig:
    """Configuration for the Governor (async orchestrator)."""
    max_concurrent_hops: int = MAX_CONCURRENT_TASKS
    hop_timeout_seconds: int = DEFAULT_HOP_TIMEOUT
    checkpoint_interval: int = CHECKPOINT_SAVE_INTERVAL
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_backoff_seconds: float = 5.0


# =============================================================================
# WORKFLOW CONFIGURATION
# =============================================================================

@dataclass
class WorkflowConfig:
    """Configuration for workflow orchestration."""
    max_hops: int = MAX_WORKFLOW_HOPS
    enable_checkpoints: bool = True
    enable_async_execution: bool = True
    gate_1_min_score: float = 0.8
    gate_2_min_score: float = 0.85
    gate_3_min_score: float = 0.9
    final_gate_min_score: float = 0.95
    total_workflow_timeout: int = 1800  # 30 minutes
    individual_hop_timeout: int = DEFAULT_HOP_TIMEOUT


# =============================================================================
# CONTENT CONSTRAINTS CONFIGURATION
# =============================================================================

@dataclass
class ContentConstraintsConfig:
    """
    Constraints for generated content.
    Single source of truth for all content constraints.
    """
    # Headline constraints
    HEADLINE_WORD_COUNT_MIN: int = 7
    HEADLINE_WORD_COUNT_MAX: int = 12
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # Executive Summary constraints
    EXECUTIVE_SUMMARY_WORD_COUNT_MIN: int = 120
    EXECUTIVE_SUMMARY_WORD_COUNT_MAX: int = 150
    EXECUTIVE_SUMMARY_SENTENCE_COUNT_MIN: int = 7
    EXECUTIVE_SUMMARY_SENTENCE_COUNT_MAX: int = 9

    # Bullets constraints
    BULLETS_WORD_COUNT_MIN: int = 25
    BULLETS_WORD_COUNT_MAX: int = 40
    BULLETS_WORD_COUNT_ACCEPTABLE_MIN: int = 21
    BULLETS_WORD_COUNT_ACCEPTABLE_MAX: int = 44

    # Competencies constraints
    COMPETENCIES_BULLET_COUNT_MIN: int = 5
    COMPETENCIES_BULLET_COUNT_MAX: int = 7

    # Skills constraints
    SKILLS_COUNT_MIN: int = 8
    SKILLS_COUNT_MAX: int = 12
    SKILLS_WORD_COUNT_MIN: int = 1
    SKILLS_WORD_COUNT_MAX: int = 3

    # Cover Letter constraints
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 130
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 120
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.7

    # Total Resume constraints
    TOTAL_RESUME_WORD_COUNT_MIN: int = 900
    TOTAL_RESUME_WORD_COUNT_MAX: int = 1200

    # Section-specific constraints
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 50
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 70
    EY_NARRATIVE_WORD_COUNT_MIN: int = 60
    EY_NARRATIVE_WORD_COUNT_MAX: int = 80
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70

    # Generation requirements
    K1_MIN_DIFFERENTIATORS: int = 4
    MIN_JD_KEYWORDS: int = 6

    # Provenance split targets
    provenance_split_targets: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "K2_UNIFY_BULLETS": {"Verbatim": 2, "Customized": 3, "Synthetic": 2},
        "K3_IBM_BULLETS": {"Verbatim": 2, "Customized": 2, "Synthetic": 2},
        "K9_COMPETENCIES": {"Verbatim": 2, "Customized": 2, "Synthetic": 2},
    })


# =============================================================================
# SIGNAL CONSTRAINTS CONFIGURATION
# =============================================================================

@dataclass
class SignalConstraintsConfig:
    """Upper bound constraints for signal quality metrics."""
    K1_MAX_DIFFERENTIATORS: int = 10
    CL_MAX_JD_SIMILARITY: float = 0.95
    RESUME_MAX_JD_KEYWORDS: int = 50


# =============================================================================
# MAIN CONFIGURATION CLASS
# =============================================================================

@dataclass
class Config:
    """Main configuration class aggregating all configurations."""

    # Sub-configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    constraints: ContentConstraintsConfig = field(default_factory=ContentConstraintsConfig)
    signal_constraints: SignalConstraintsConfig = field(default_factory=SignalConstraintsConfig)

    # System parameters
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    api_timeout: int = DEFAULT_API_TIMEOUT
    rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY

    # Quality thresholds
    min_quality_score: float = MIN_QUALITY_SCORE
    min_confidence_score: float = MIN_CONFIDENCE_SCORE
    min_relevance_score: float = MIN_RELEVANCE_SCORE

    # File limits
    max_job_description_length: int = MAX_JOB_DESCRIPTION_LENGTH
    max_resume_file_size: int = MAX_RESUME_FILE_SIZE
    max_log_file_size: int = MAX_LOG_FILE_SIZE

    def validate(self) -> bool:
        """
        Validate the configuration for consistency.

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate word count constraints
        if self.constraints.HEADLINE_WORD_COUNT_MIN > self.constraints.HEADLINE_WORD_COUNT_MAX:
            raise ValueError("Headline min word count > max word count")

        if self.constraints.EXECUTIVE_SUMMARY_WORD_COUNT_MIN > self.constraints.EXECUTIVE_SUMMARY_WORD_COUNT_MAX:
            raise ValueError("Executive summary min word count > max word count")

        if self.constraints.BULLETS_WORD_COUNT_MIN > self.constraints.BULLETS_WORD_COUNT_MAX:
            raise ValueError("Bullet min word count > max word count")

        # Validate thresholds
        if not 0 <= self.min_quality_score <= 1:
            raise ValueError("min_quality_score must be between 0 and 1")

        if not 0 <= self.min_confidence_score <= 1:
            raise ValueError("min_confidence_score must be between 0 and 1")

        if not 0 <= self.min_relevance_score <= 1:
            raise ValueError("min_relevance_score must be between 0 and 1")

        # Validate retries and timeouts
        if self.max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if self.api_timeout < 1:
            raise ValueError("api_timeout must be at least 1 second")

        logger.debug("✓ Configuration validation passed")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model": {
                "provider": self.model.provider.value,
                "default_model": self.model.default_model,
                "temperature": self.model.temperature,
                "max_tokens": self.model.max_tokens,
            },
            "workflow": {
                "max_hops": self.workflow.max_hops,
                "enable_checkpoints": self.workflow.enable_checkpoints,
                "total_timeout": self.workflow.total_workflow_timeout,
            },
            "quality": {
                "min_quality_score": self.min_quality_score,
                "min_confidence_score": self.min_confidence_score,
                "min_relevance_score": self.min_relevance_score,
            },
            "api": {
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "timeout": self.api_timeout,
            },
        }


# =============================================================================
# CREATE GLOBAL CONFIG INSTANCE
# =============================================================================

CONFIG = Config()

try:
    CONFIG.validate()
    logger.debug("✓ Configuration loaded and validated successfully")
except ValueError as e:
    logger.error(f"✗ Configuration validation failed: {e}")
    raise


# =============================================================================
# LIBRARY AVAILABILITY FLAGS
# =============================================================================

try:
    import google.generativeai  # noqa: F401
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import sklearn  # noqa: F401
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import chromadb  # noqa: F401
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import redis  # noqa: F401
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
