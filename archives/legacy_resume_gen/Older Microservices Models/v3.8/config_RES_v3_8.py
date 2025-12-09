# File: config_RES_v3.8.py
# Version: 19.0.1 (User Patches)
# Centralized configuration for Resume Generation Engine V2
# ALL CONSTANTS CONSOLIDATED - NO MAGIC NUMBERS IN CODE

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from models_RES import ReasoningConfig, ResumeSection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Get absolute paths
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "workflow_outputs"
BACKUP_DIR = PROJECT_ROOT / "backups"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, BACKUP_DIR, LOGS_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SYSTEM CONSTANTS - SINGLE SOURCE OF TRUTH
# ============================================================================

# --- v3.8 ADVERSARIAL SWARM CONFIG ---
#
# Defines high-stakes nodes that will trigger the v3.8 adversarial loop
ADVERSARIAL_NODES = {
    "K1_EXECUTIVE_SUMMARY",
    "K11_COVER_LETTER"
}

# (These would be loaded securely from env variables or a secret manager)
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "YOUR_CLAUDE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
# --- END v3.8 CONFIG ---

# API Configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2.0
DEFAULT_API_TIMEOUT = 30  # seconds
DEFAULT_RATE_LIMIT_DELAY = 5.0  # seconds

# Generation Parameters
DEFAULT_GENERATION_TEMPERATURE = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE = 0.3
DEFAULT_MAX_OUTPUT_TOKENS = 8192
DEFAULT_MIN_OUTPUT_TOKENS = 100

# Safety Configuration (from gemini_service.py)
SAFETY_THRESHOLD = "BLOCK_NONE"

# Model Configuration (from governor.py)
DEFAULT_MODEL = "gemini-2.5-pro"
MAX_RETRIES_PER_NODE = DEFAULT_MAX_RETRIES  # Alias for governor

# --- v3.8 EXTERNAL MODEL NAMES ---
GEMINI_PREMIUM_MODEL = "gemini-2.5-pro"
CLAUDE_PREMIUM_MODEL = "claude-sonnet-4-5-20250929"
OPENAI_SYNTHESIS_MODEL = "gpt-5-2025-08-07"
# --- END v3.8 ---

# Validation Thresholds
MIN_CONFIDENCE_SCORE = 0.7
MIN_RELEVANCE_SCORE = 0.65

# Bullet Word Count Constraints (from artist_RES_v3_8.py)
ACCEPTABLE_MIN_WC = 21  # From constraints.json bullets.word_count_acceptable_min
ACCEPTABLE_MAX_WC = 44  # From constraints.json bullets.word_count_acceptable_max

# Self-Consistency Parameters
DEFAULT_SELF_CONSISTENCY_RUNS = 3
MAX_SELF_CONSISTENCY_RUNS = 5
MIN_SELF_CONSISTENCY_AGREEMENT = 0.8

# Workflow Constants
MAX_WORKFLOW_HOPS = 10
DEFAULT_HOP_TIMEOUT = 300  # seconds (5 minutes)
MAX_CONCURRENT_TASKS = 4
CHECKPOINT_SAVE_INTERVAL = 2  # Save checkpoint every N hops

# Quality Thresholds
MIN_QUALITY_SCORE = 0.75
MIN_COHERENCE_SCORE = 0.8
MIN_FACTUAL_ACCURACY_SCORE = 0.9
MAX_HALLUCINATION_SCORE = 0.1

# File Size Limits
MAX_JOB_DESCRIPTION_LENGTH = 50000  # characters
MAX_RESUME_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_CACHE_ENTRIES = 100

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS = 3

# --- FIX: ADDED COVER_LETTER_SIGNATURE_TEMPLATE ---
# This was imported by context.py but was missing
COVER_LETTER_SIGNATURE_TEMPLATE = "Sincerely,\n\n{name}\n{email} | {phone}\n{linkedin}"
# --- END FIX ---


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _load_json_config(file_path: str, config_name: str, required: bool = True) -> Dict:
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
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"✓ Loaded {config_name} from {file_path}")
            return data
    except FileNotFoundError:
        if required:
            logger.error(f"✗ Required config file not found: {file_path}")
            raise
        else:
            logger.warning(f"⚠ Optional config file not found: {file_path}")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"✗ Invalid JSON in {file_path}: {e}")
        raise

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

class ModelProvider(Enum):
    """Supported model providers"""
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    provider: ModelProvider = ModelProvider.GEMINI
    default_model: str = "gemini-2.0-flash-exp"
    fallback_model: str = "gemini-1.5-pro"
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    top_p: float = 1.0
    top_k: int = 40
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

# ============================================================================
# FILE PATHS CONFIGURATION
# ============================================================================

@dataclass
class FilePaths:
    """Centralized file paths"""
    master_resume: Path = DATA_DIR / "master_resume.json"
    job_input: Path = DATA_DIR / "job_input.json"
    constraints: Path = DATA_DIR / "constraints.json"
    hyphenation_rules: Path = DATA_DIR / "hyphenation_rules.json"
    app_tracker_schema: Path = DATA_DIR / "app_tracker_schema.json"
    artist_specs: Path = DATA_DIR / "artist_specs.json"
    validator_rules: Path = DATA_DIR / "validator_rules.json"
    prompts: Path = DATA_DIR / "prompts.json"

# ============================================================================
# ARTIST CONFIGURATION
# ============================================================================

# --- FIX: (Zombie Import / Confusing Aliases) ---
# Removed the deprecated V1 'ArtistConfig' class.
# The 'artist' alias for 'constraints' is also removed from the main Config class below.
# All code should use CONFIG.constraints.
# --- END FIX ---


# ============================================================================
# ENRICHER CONFIGURATION (Bug 2 Fix)
# ============================================================================

@dataclass
class EnricherConfig:
    """Configuration for the Data Enricher"""
    canonical_verbs: Dict[str, List[str]] = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, json_path: Path = None) -> 'EnricherConfig':
        if json_path is None:
            # This file is not in the provided list, but 'enricher_RES_v3_8.py'
            # depends on it. This patch assumes it exists at this path.
            json_path = DATA_DIR / "enricher_rules.json"
        
        data = _load_json_config(str(json_path), "Enricher Rules (canonical_verbs)", required=False)
        return cls(canonical_verbs=data.get("canonical_verbs", {}))

# ============================================================================
# VALIDATOR CONFIGURATION
# ============================================================================

@dataclass
class ValidatorConfig:
    """Configuration for validation rules and constraints"""
    forbidden_verbs: List[str] = field(default_factory=list)
    required_sections: Set[str] = field(default_factory=set)
    bullet_word_count_sections_to_check: Set[str] = field(default_factory=set)
    provenance_split_targets: Dict = field(default_factory=dict)
    pipeline_status_enum: List[str] = field(default_factory=list)
    app_tracker_schema: Dict = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, 
                  rules_path: Path = None,
                  schema_path: Path = None) -> 'ValidatorConfig':
        """Load ValidatorConfig from JSON files."""
        if rules_path is None:
            rules_path = DATA_DIR / "validator_rules.json"
        if schema_path is None:
            schema_path = DATA_DIR / "app_tracker_schema.json"
            
        rules_data = _load_json_config(str(rules_path), "Validator Rules", required=False)
        schema_data = _load_json_config(str(schema_path), "App Tracker Schema", required=True)
        
        # --- FIX: Load provenance_split_targets from constraints.json ---
        # The validator_rules.json file does NOT contain this key, but constraints.json does.
        # This was a bug in the original file.
        constraints_data = _load_json_config(str(DATA_DIR / "constraints.json"), "Constraints", required=False)
        # --- END FIX ---
        
        return cls(
            forbidden_verbs=rules_data.get("forbidden_verbs", []),
            required_sections=set(rules_data.get("required_sections", [])),
            bullet_word_count_sections_to_check=set(rules_data.get("bullet_word_count_sections_to_check", [])),
            # --- FIX: Load from constraints_data ---
            provenance_split_targets=constraints_data.get("provenance_split_targets", {}),
            # --- END FIX ---
            pipeline_status_enum=rules_data.get("pipeline_status_enum", []),
            app_tracker_schema=schema_data
        )

# ============================================================================
# PROMPT CONFIGURATION
# ============================================================================

@dataclass
class PromptConfig:
    """Configuration for prompt templates"""
    prompts: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, json_path: Path = None) -> 'PromptConfig':
        """Load prompts from JSON file."""
        if json_path is None:
            json_path = DATA_DIR / "prompts.json"
            
        data = _load_json_config(str(json_path), "Prompts", required=True)
        return cls(prompts=data)

# ============================================================================
# RAG CONFIGURATION
# ============================================================================

@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    model: str = "gemini-2.5-pro"
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
    
    # --- ADDED: Circuit breaker config ---
    # These were missing but referenced by the circuit breaker
    circuit_breaker_threshold: int = 3
    circuit_breaker_timeout: int = 60
    # --- END ---

    # --- BUG 3 FIX: Add missing backoff attributes ---
    api_initial_backoff_seconds: float = 2.0
    api_backoff_multiplier: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_jitter: float = 0.1

# ============================================================================
# PROMPT ADDENDUM CONFIGURATION
# ============================================================================

@dataclass
class PromptAddendumConfig:
    """Configuration for reasoning prompt addendums"""
    HEADER: str = "\n\n--- REASONING DIRECTIVES ---\n"
    FOOTER: str = "\n--- END REASONING DIRECTIVES ---\n"
    
    # Chain-of-Thought directives (threshold, template)
    COT_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (5, "Generate at least {cot} distinct chains of reasoning. Show each step explicitly.\n"),
        (3, "Use multi-step reasoning with at least {cot} distinct chains of thought.\n"),
        (1, "Apply step-by-step reasoning through {cot} chain(s) of thought.\n")
    ])
    
    # Tree-of-Thought Breadth directives
    TOT_B_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (5, "Explore {tot_b} diverse solution branches. Evaluate each independently.\n"),
        (3, "Consider {tot_b} different approaches before selecting the best.\n"),
        (2, "Generate {tot_b} alternative solutions and compare them.\n")
    ])
    
    # Tree-of-Thought Depth directives
    TOT_D_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (3, "Explore each branch to depth {tot_d} with recursive reasoning.\n"),
        (2, "Reason through {tot_d} levels of depth for each approach.\n"),
        (1, "Apply {tot_d}-level deep reasoning.\n")
    ])
    
    # Reflexion directives
    REFLEXION_DIRECTIVES: List[tuple] = field(default_factory=lambda: [
        (3, "Apply self-critique with up to {max_loops} refinement iterations.\n"),
        (2, "Review and refine your response through {max_loops} reflection loops.\n"),
        (1, "Reflect on and improve your answer in {max_loops} iteration(s).\n")
    ])

PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()

# ============================================================================
# GOVERNOR CONFIGURATION
# ============================================================================

@dataclass
class GovernorConfig:
    """Configuration for the Governor (async orchestrator)"""
    max_concurrent_hops: int = MAX_CONCURRENT_TASKS
    hop_timeout_seconds: int = DEFAULT_HOP_TIMEOUT
    checkpoint_interval: int = CHECKPOINT_SAVE_INTERVAL
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_backoff_seconds: float = 5.0

# ============================================================================
# WORKFLOW CONFIGURATION
# ============================================================================

@dataclass
class WorkflowConfig:
    """Configuration for workflow orchestration"""
    max_hops: int = MAX_WORKFLOW_HOPS
    enable_checkpoints: bool = True
    enable_async_execution: bool = True
    gate_1_min_score: float = 0.8
    gate_2_min_score: float = 0.85
    gate_3_min_score: float = 0.9
    final_gate_min_score: float = 0.95
    total_workflow_timeout: int = 1800  # 30 minutes
    individual_hop_timeout: int = DEFAULT_HOP_TIMEOUT

# ============================================================================
# SIGNAL CONSTRAINTS CONFIGURATION
# ============================================================================

@dataclass
class SignalConstraintsConfig:
    """Upper bound constraints for signal quality metrics"""
    K1_MAX_DIFFERENTIATORS: int = 10
    CL_MAX_JD_SIMILARITY: float = 0.95
    RESUME_MAX_JD_KEYWORDS: int = 50

# ============================================================================
# CONTENT CONSTRAINTS CONFIGURATION (LOADED FROM JSON ONLY)
# ============================================================================

@dataclass
class ContentConstraintsConfig:
    """
    Constraints for generated content - defined directly in this module
    as the single source of truth (previously loaded from constraints.json).
    Version: 18.00 (Refactored - constraints now defined statically)
    """
    
    # --- Content from constraints.json is now defined here ---
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
    provenance_split_targets: Dict = field(default_factory=lambda: {
        "K2_UNIFY_BULLETS": {
            "Verbatim": 2,
            "Customized": 3,
            "Synthetic": 2
        },
        "K3_IBM_BULLETS": {
            "Verbatim": 2,
            "Customized": 2,
            "Synthetic": 2
        },
        "K9_COMPETENCIES": {
            "Verbatim": 2,
            "Customized": 2,
            "Synthetic": 2
        }
    })

# ============================================================================
# HYPHENATION CONFIGURATION
# ============================================================================

@dataclass
class HyphenationConfig:
    """Configuration for hyphenation rules"""
    rules: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, json_path: Path = None) -> 'HyphenationConfig':
        """Load hyphenation rules from JSON."""
        if json_path is None:
            json_path = DATA_DIR / "hyphenation_rules.json"
            
        data = _load_json_config(str(json_path), "Hyphenation Rules", required=False)
        return cls(rules=data)

# ============================================================================
# MAIN CONFIGURATION CLASS
# ============================================================================

@dataclass
class Config:
    """Main configuration class aggregating all configurations"""
    
    # Sub-configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    files: FilePaths = field(default_factory=FilePaths)
    # --- FIX (Inefficiency 1): Removed redundant ArtistConfig alias. ---
    # artist: ContentConstraintsConfig = field(init=False) (REMOVED)
    # --- END FIX ---
    validator: ValidatorConfig = field(default_factory=lambda: ValidatorConfig.from_json())
    prompts: PromptConfig = field(default_factory=lambda: PromptConfig.from_json())
    rag: RAGConfig = field(default_factory=RAGConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    constraints: ContentConstraintsConfig = field(default_factory=ContentConstraintsConfig)
    signal_constraints: SignalConstraintsConfig = field(default_factory=SignalConstraintsConfig)
    hyphenation: HyphenationConfig = field(default_factory=lambda: HyphenationConfig.from_json())

    # --- BUG 2 FIX: Add missing EnricherConfig ---
    enricher: EnricherConfig = field(default_factory=lambda: EnricherConfig.from_json())
    # --- END FIX ---
    
    # Load artist_specs data
    artist_specs: Dict = field(default_factory=lambda: _load_json_config(DATA_DIR / "artist_specs.json", "Artist Specs"))
    
    # System parameters (replacing magic numbers)
    # --- FIX: Use constants from top of file ---
    max_retries: int = field(default=DEFAULT_MAX_RETRIES)
    retry_delay: float = field(default=DEFAULT_RETRY_DELAY)
    # --- END FIX ---
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
    
    # --- FIX: ADDED SECTION_SIGNAL_TARGETS_CONFIG ---
    # This was missing and caused a bug in validation/rules.py
    SECTION_SIGNAL_TARGETS_CONFIG: Dict = field(default_factory=lambda: {
        "K1_Exec_Summary": (ResumeSection.K1_EXECUTIVE_SUMMARY, 0.85, 1.20, None, None),
        "K2_Unify": (ResumeSection.K2_UNIFY_OVERVIEW, 0.70, 1.00, None, None),
        "K3_IBM": (ResumeSection.K3_IBM_OVERVIEW, 0.70, 1.00, None, None),
        "K4_TraderSense": (ResumeSection.K4_TRADERSENSE_NARRATIVE, 0.60, 0.90, None, None),
        "K6_Narrative": (ResumeSection.K6_EARLY_CAREER_NARRATIVE, 0.70, 1.00, None, None),
    })
    # --- END FIX ---
    
    def __post_init__(self):
        # --- FIX (Inefficiency 1): Link artist to constraints ---
        # self.artist = self.constraints (REMOVED)
        
        # --- FIX: (Triplicated Constants) Remove hardcoded values ---
        # Values are now set directly from the top-level constants.
        pass
        # --- END FIX ---

    def validate(self) -> bool:
        """
        Validate the configuration for consistency.
        
        Returns:
            True if valid, raises ValueError if not
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
        
        logger.info("✓ Configuration validation passed")
        return True

# ============================================================================
# CREATE GLOBAL CONFIG INSTANCE
# ============================================================================

# Create and validate the global config
CONFIG = Config()

try:
    CONFIG.validate()
    logger.info("✓ Configuration loaded and validated successfully")
except ValueError as e:
    logger.error(f"✗ Configuration validation failed: {e}")
    raise

# Export commonly used items for backward compatibility
OUTPUT_DIR = OUTPUT_DIR
DATA_DIR = DATA_DIR
LOGS_DIR = LOGS_DIR
CACHE_DIR = CACHE_DIR
DEFAULT_GENERATION_TEMPERATURE = DEFAULT_GENERATION_TEMPERATURE
# --- FIX: Export single source of truth constants ---
DEFAULT_MAX_RETRIES = DEFAULT_MAX_RETRIES
DEFAULT_RETRY_DELAY = DEFAULT_RETRY_DELAY
# --- END FIX ---
# --- FIX: Export COVER_LETTER_SIGNATURE_TEMPLATE ---
COVER_LETTER_SIGNATURE_TEMPLATE = COVER_LETTER_SIGNATURE_TEMPLATE
# --- END FIX ---

# Type aliases for backward compatibility
AppConfig = Config
# --- FIX: Removed redundant alias ---
# EnricherConfig = EnricherConfig (REMOVED)
# --- END FIX ---

# Library availability flags
try:
    import google.generativeai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import sklearn
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Log configuration summary
logger.info(f"Configuration Summary:")
logger.info(f"  Project Root: {PROJECT_ROOT}")
logger.info(f"  Data Directory: {DATA_DIR}")
logger.info(f"  Output Directory: {OUTPUT_DIR}")
logger.info(f"  Model: {CONFIG.model.default_model}")
logger.info(f"  Max Retries: {CONFIG.max_retries}")
logger.info(f"  Quality Threshold: {CONFIG.min_quality_score}")