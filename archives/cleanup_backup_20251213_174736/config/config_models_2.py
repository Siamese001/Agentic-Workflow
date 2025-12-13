"""Dataclass models for config."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class EnricherConfig:
    """Configuration for data enrichment."""
    canonical_verbs: Dict = field(default_builder=lambda: {'led': ['led', 'lead', 'leading'], 'built': ['built', 'build', 'building'], 'drove': ['drove', 'drive', 'driving'], 'launched': ['launched', 'launch', 'launching'], 'scaled': ['scaled', 'scale', 'scaling'], 'delivered': ['delivered', 'deliver', 'delivering'], 'achieved': ['achieved', 'achieve', 'achieving'], 'established': ['established', 'establish', 'establishing'], 'managed': ['managed', 'manage', 'managing'], 'developed': ['developed', 'develop', 'developing']})

@dataclass
class RAGConfig:
    """Configuration for RAG (Retrieval Augmented Generation) system."""
    model: str = 'gemini-2.5-pro'
    max_tokens: int = 8192
    temperature: float = 0.7
    api_max_retries: int = 7
    api_timeout_seconds: int = 120
    api_initial_backoff_seconds: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_multiplier: float = 2.0
    api_backoff_jitter: float = 0.1
    phase_max_retries: int = 3
    phase_timeout_seconds: int = 180
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    cache_dir: Path = CACHE_DIR / 'rag_cache'
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    telemetry_log_dir: Path = CACHE_DIR / 'rag_telemetry'
    chroma_persist_dir: Path = CACHE_DIR / 'chroma_memory'
    chroma_collection_name: str = 'rag_librarian_v1'
    source_weights: Dict[str, float] = field(default_builder=lambda: {'SOURCE_JD': 1.8, 'SOURCE_COMPANY_BLOG': 1.5, 'SOURCE_TARGET_EMPLOYEE': 1.4, 'SOURCE_GARTNER_MQ': 1.2, 'SOURCE_PEER_JD': 0.8, 'SOURCE_GENERIC_PROFILE': 0.5, 'LOCAL_NLP': 0.2})

    def __post_init__(self) -> None:
        """Ensure source_weights is a dict, not a field builder."""
        if not isinstance(self.source_weights, dict):
            logging.error('source_weights must be a dict.')
            raise TypeError('source_weights must be a dict')
        self._validate_source_weights()
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.telemetry_log_dir.mkdir(parents=True, exist_ok=True)
            self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logging.warning(f'Could not create cache directories (read-only filesystem?): {e}')
            logging.warning('Caching features will be disabled')

    def _validate_source_weights(self) -> None:
        """Ensure source_weights are positive and reasonable."""
        for source, weight in self.source_weights.items():
            if not isinstance(weight, (int, float)):
                raise TypeError(f"Weight for '{source}' must be numeric, got {type(weight)}")
            if weight < 0:
                raise ValueError(f"Weight for '{source}' cannot be negative: {weight}")
            if weight > 10.0:
                logging.warning(f"Unusually high weight for '{source}': {weight}")

@dataclass
class ReasoningConfig:
    """
    Configuration for reasoning strategies (CoT, ToT, Self-Consistency, Reflexion).
    
    PHASE 2 CHANGE: Rationalized reasoning parameters.
    - Lowered self_consistency intensity since Inspector handles evaluation
    - CoT/ToT remain strategic for planning, but SC reduced from 8 -> 3 for K1
    """
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 3
    reflexion: bool = True
    max_reflexion_loops: int = 3
    DEFAULT: ClassVar['ReasoningConfig']
    K0_HEADLINE_CONFIG: ClassVar['ReasoningConfig']
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar['ReasoningConfig']
    K2_UNIFY_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K2_UNIFY_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K3_IBM_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K3_IBM_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K4_TRADERSENSE_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K5_EY_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K6_EARLY_CAREER_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K9_COMPETENCIES_CONFIG: ClassVar['ReasoningConfig']
    K10_SKILLS_CONFIG: ClassVar['ReasoningConfig']
    K11_COVER_LETTER_CONFIG: ClassVar['ReasoningConfig']

@dataclass
class ContentConstraintsConfig:
    """Content-level constraints for word counts, sentence counts, etc."""
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 12
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4
    SKILLS_COUNT_MIN: int = 8
    SKILLS_COUNT_MAX: int = 12
    SKILLS_WORD_COUNT_MIN: int = 1
    SKILLS_WORD_COUNT_MAX: int = 3
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35
    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 60
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35

@dataclass
class SignalControlConfig:
    """Signal control thresholds for quality and relevance."""
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65

