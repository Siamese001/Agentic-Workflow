# File: core.py
# Zero-Loss Consolidation - The Foundation
# Merges: models_RES.py → config_RES.py → utils_RES.py → prompts_RES.py
# Version: 5.9 (Batch Harness)
# REFACTORED: Removed all hard-coded defaults, enums, and shadow-configs.
# All configuration is now read from the central CONFIG object.

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import copy
import hashlib
import json
import logging
import os
import re
import subprocess
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, ClassVar, Dict, List, Optional, Set, Tuple, Union, TYPE_CHECKING
)

# Optional imports with fallback handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# Configure logging
logging.basicConfig(level=logging.INFO)
core_logger = logging.getLogger(__name__)  # Renamed to avoid conflict

# ============================================================================
# PART 1: CONFIGURATION (from config_RES.py)
# ============================================================================

# Project Paths
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Load Configuration
CONFIG_PATH = PROJECT_ROOT / "master_config_v5_9.json"

class Configuration:
    """
    Central configuration class.
    Reads all settings from master_config_v5_9.json.
    """
    
    def __init__(self, config_path: Optional[Path] = None, logger=None):
        self.config_path = config_path or CONFIG_PATH
        self._config_data = self._load_config()
        
        # Dynamically load all top-level keys as attributes
        for key, value in self._config_data.items():
            setattr(self, key, self._to_namespace(value))
        
        # Ensure critical configs exist
        self.llm_config = getattr(self, 'llm_config', {})
        self.constraints = getattr(self, 'constraints', {})
        self.signal_constraints = getattr(self, 'signal_constraints', {})
        self.prompts = getattr(self, 'prompts', {})
        self.rules = getattr(self, 'rules', {})
        self.resume_structure = getattr(self, 'resume_structure', {})
        self.tool_configs = getattr(self, 'tool_configs', {})
        self.file_paths = getattr(self, 'file_paths', {})
        self.agent_definitions = getattr(self, 'agent_definitions', {})

        # Set derived defaults
        self.min_confidence_score = getattr(self.signal_constraints, 'MIN_SIGNAL_SCORE', 0.75)
        self.min_relevance_score = getattr(self.signal_constraints, 'MIN_JD_ALIGNMENT', 0.70)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            core_logger.critical(f"FATAL: master_config_v5_9.json not found at {self.config_path}.")
            raise FileNotFoundError(f"master_config_v5_9.json not found at {self.config_path}.")
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            core_logger.critical(f"FATAL: Failed to load or parse config: {e}")
            raise
            
    def _to_namespace(self, data: Any) -> Any:
        """Recursively convert dicts to simple namespace-like objects for dot notation."""
        if isinstance(data, dict):
            # Create a simple class instance for dot notation
            namespace = type('Namespace', (), {})()
            for key, value in data.items():
                setattr(namespace, key, self._to_namespace(value))
            return namespace
        elif isinstance(data, list):
            return [self._to_namespace(item) for item in data]
        else:
            return data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config_data.get(key, default)

# Initialize global configuration
CONFIG = Configuration(logger=core_logger)

# Constants derived from CONFIG
# These replace the old hard-coded module-level constants
LLM_DEFAULTS = CONFIG.llm_config.defaults
DEFAULT_MAX_RETRIES = LLM_DEFAULTS.max_retries
DEFAULT_RETRY_DELAY = LLM_DEFAULTS.retry_delay_sec
DEFAULT_GENERATION_TEMPERATURE = LLM_DEFAULTS.default_generation_temperature
DEFAULT_SYNTHESIS_TEMPERATURE = LLM_DEFAULTS.default_synthesis_temperature
DEFAULT_MAX_OUTPUT_TOKENS = LLM_DEFAULTS.default_max_output_tokens
SAFETY_THRESHOLD = LLM_DEFAULTS.safety_threshold

# Word count constraints from CONFIG
BULLET_CONSTRAINTS = CONFIG.constraints.bullets
ACCEPTABLE_MIN_WC = BULLET_CONSTRAINTS.word_count_acceptable_min
ACCEPTABLE_MAX_WC = BULLET_CONSTRAINTS.word_count_acceptable_max


# ============================================================================
# PART 2: MODELS (from models_RES.py)
# ============================================================================

# Custom Exceptions
class HopExecutionError(Exception):
    """Raised when a hop fails to execute successfully."""
    pass

class StagingBufferError(Exception):
    """Raised when staging buffer encounters data integrity issues."""
    pass

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects requests."""
    pass

class PhaseTimeoutError(Exception):
    """Raised when a RAG phase execution exceeds timeout."""
    pass

class FactualFailureException(Exception):
    """Raised by Validator when a high-signal factual or strategic check fails, triggering a Slow Loop."""
    pass

class MechanicalFailureError(Exception):
    """Raised for mechanical, format, or constraint violations (e.g., word count, forbidden jargon)."""
    pass

class SemanticFailureError(Exception):
    """Raised for factual, logical, or thematic inconsistencies (e.g., hallucination, contradiction)."""
    pass

# Enumerations
class GateDecision(Enum):
    """Decision outcomes for gate validation."""
    PROCEED = "PROCEED"
    HALT = "HALT"

class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

# REFACTORED: ResumeSection is now dynamically loaded from CONFIG
class ResumeSection:
    """
    Dynamically provides resume sections from the master_config_v5_9.json.
    Access sections like: ResumeSection.K1_EXECUTIVE_SUMMARY
    """
    _sections = CONFIG.resume_structure
    
    def __getattr__(self, name: str) -> str:
        """Allow dot notation access to section names."""
        if hasattr(self, '_sections') and hasattr(self._sections, name):
            return getattr(self._sections, name)
        raise AttributeError(f"'ResumeSection' has no attribute '{name}'")
    
    @classmethod
    def get_all(cls) -> Dict[str, str]:
        """Return all sections as a dictionary."""
        return {key: value for key, value in vars(cls._sections).items() if not key.startswith('_')}

# Instantiate to allow class-level access
ResumeSection = ResumeSection()


# REFACTORED: JDEnforcementRule is now dynamically loaded from CONFIG
class JDEnforcementRule:
    """
    Dynamically provides JD enforcement rules from the master_config_v5_9.json.
    Access rule messages like: JDEnforcementRule.E1_JD_MIN_LENGTH.message
    Access rule values like: JDEnforcementRule.E1_JD_MIN_LENGTH.value
    """
    _rules = CONFIG.rules.jd_enforcement
    
    def __getattr__(self, name: str) -> Any:
        """Allow dot notation access to rule objects."""
        if hasattr(self, '_rules') and hasattr(self._rules, name):
            return getattr(self._rules, name)
        raise AttributeError(f"'JDEnforcementRule' has no attribute '{name}'")

# Instantiate to allow class-level access
JDEnforcementRule = JDEnforcementRule()


class ReasoningStrategy(Enum):
    """Available reasoning strategies for enhanced prompt processing."""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    SELF_CONSISTENCY = "self_consistency"
    LEAST_TO_MOST = "least_to_most"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    META_REASONING = "meta_reasoning"
    BASELINE = "baseline"

class CircuitBreakerState(Enum):
    """States for the circuit breaker pattern."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class RAGPhase(Enum):
    """RAG processing phases with distinct objectives."""
    EXTRACTION = "EXTRACTION"
    ENRICHMENT = "ENRICHMENT"
    SYNTHESIS = "SYNTHESIS"
    VALIDATION = "VALIDATION"

class VetoLevel(Enum):
    """Veto priority levels for QA failures."""
    NONE = 0
    QA3_SEMANTIC = 1
    QA2_FACTUAL = 2
    QA1_LINGUISTIC = 3
    STRATEGY = 4        # Highest blocking priority
    HOLISTIC = 5        # For NarrativeThread failures
    ADVERSARIAL = 6     # For Red Team failures

class QAClassification(Enum):
    """QA Agent classifications."""
    CLASS_1_LINGUISTIC_CHEAP = auto()
    CLASS_2_FACTUAL_MEDIUM = auto()
    CLASS_3_SEMANTIC_EXPENSIVE = auto()
    CLASS_4_HOLISTIC_DEEP = auto()
    CLASS_5_ADVERSARIAL = auto()

# v5.8: New Enums for MoE and Reflection
class ReflectionStatus(Enum):
    """Status of reflection loop iterations."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    CONVERGED = "CONVERGED"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    FAILED = "FAILED"

class ToolType(Enum):
    """Types of tools available for ReAct agents."""
    WEB_SEARCH = "web_search"
    CHROMADB_SEARCH = "chromadb_search"
    WIKI_SEARCH = "wiki_search"
    BROWSE_PAGE = "browse_page"
    COMPANY_RESEARCH = "company_research"

# Data Classes
@dataclass
class ValidationResult:
    """Result of a single validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "severity": self.severity.name if isinstance(self.severity, Enum) else str(self.severity),
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class HopResult:
    """Result of a single hop execution."""
    hop_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hop_id": self.hop_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class GenerationAttempt:
    """Single generation attempt with metadata."""
    temperature: float
    attempt_number: int
    content: str
    passed: bool
    validation_results: List[ValidationResult]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReasoningConfig:
    """Configuration for reasoning strategies."""
    strategy: ReasoningStrategy = ReasoningStrategy.BASELINE
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    num_branches: int = 3
    max_depth: int = 3
    voting_threshold: float = 0.7
    enable_self_critique: bool = True
    enable_confidence_scoring: bool = True

@dataclass
class ThematicAnalysis:
    """Result of thematic analysis on job description."""
    themes: List[str]
    skills_required: List[str]
    impact_phrases: List[str]
    expertise_areas: List[str]
    differentiators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperienceBullet:
    """A single experience bullet with metadata."""
    text: str
    company: str
    keywords: List[str]
    metrics: List[str]
    achievements: List[str]
    source_section: str
    relevance_score: float = 0.0

@dataclass
class PortfolioCompany:
    """Portfolio company reference."""
    name: str
    description: str
    url: Optional[str] = None
    relevance_to_jd: float = 0.0

# v5.8: New Data Classes for MoE and Reflection
@dataclass
class ReflectionIteration:
    """Single iteration in a reflection loop."""
    iteration_number: int
    draft: str
    critique: str
    issues_found: List[str]
    improvements_made: List[str]
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReflectionResult:
    """Result of a complete reflection loop."""
    final_output: str
    iterations: List[ReflectionIteration]
    status: ReflectionStatus
    total_iterations: int
    quality_improvement: float  # Delta from first to last
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolCall:
    """Record of a tool invocation by ReAct agent."""
    tool_type: ToolType
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    success: bool
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReActTrace:
    """Complete trace of ReAct agent reasoning."""
    thought: str
    action: str
    tool_calls: List[ToolCall]
    observation: str
    reflection: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MoEExpertResult:
    """Result from a single expert in MoE ensemble."""
    expert_id: str
    expert_type: str
    result: Any
    confidence: float
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MoEDecision:
    """Final decision from MoE router after aggregating expert results."""
    selected_expert: Optional[str]
    aggregated_result: Any
    expert_results: List[MoEExpertResult]
    aggregation_method: str  # "voting", "averaging", "weighted", "best_confidence"
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConductorBranch:
    """A single branch in Tree of Thought conductor."""
    branch_id: str
    strategy_description: str
    planner_id: str
    execution_plan: List[str]  # List of steps
    result: Optional[Any] = None
    score: float = 0.0
    execution_time: float = 0.0
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED

@dataclass
class ConductorDecision:
    """Final decision from conductor after evaluating all branches."""
    winning_branch: ConductorBranch
    all_branches: List[ConductorBranch]
    vote_results: Dict[str, float]
    selection_method: str  # "vote", "score", "hybrid"
    metadata: Dict[str, Any] = field(default_factory=dict)

# RAG System Data Classes
@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    enabled: bool = True
    max_docs_per_query: int = 10
    similarity_threshold: float = 0.7
    rerank_enabled: bool = True
    max_tokens_per_doc: int = 1000

@dataclass
class RAGMission:
    """Mission specification for RAG pipeline."""
    objective: str
    constraints: List[str]
    success_criteria: List[str]
    target_section: Optional[str] = None

@dataclass
class MasterResumeIndex:
    """Indexed representation of master resume."""
    sections: Dict[str, List[ExperienceBullet]]
    skills: List[str]
    certifications: List[str]
    companies: List[str]
    keywords_index: Dict[str, List[Tuple[str, str]]]  # keyword -> [(section, text)]
    metrics_index: Dict[str, List[Tuple[str, str]]]  # metric -> [(section, text)]

# Circuit Breaker
@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker pattern.
    REFACTORED: Defaults are read from CONFIG.
    """
    failure_threshold: int = CONFIG.tool_configs.circuit_breaker.failure_threshold
    success_threshold: int = CONFIG.tool_configs.circuit_breaker.success_threshold
    timeout_duration: int = CONFIG.tool_configs.circuit_breaker.timeout_duration
    half_open_timeout: int = CONFIG.tool_configs.circuit_breaker.half_open_timeout

# Immutable Staging Buffer
@dataclass
class ImmutableStagingBuffer:
    """Immutable staging buffer for resume sections."""
    sections: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.checksum is None:
            self.checksum = self._compute_checksum()
    
    def _compute_checksum(self) -> str:
        content = json.dumps(self.sections, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_section(self, section_name: str) -> Optional[str]:
        return self.sections.get(section_name)
    
    def verify_integrity(self) -> bool:
        return self.checksum == self._compute_checksum()

# RAG Blackboard
@dataclass
class RAG_Blackboard:
    """Shared state for RAG pipeline with v5.8 ReAct traces."""
    mission: RAGMission
    queries: List[str] = field(default_factory=list)
    raw_results: List[Dict[str, Any]] = field(default_factory=list)
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    ranked_chunks: List[Dict[str, Any]] = field(default_factory=list)
    filtered_chunks: List[Dict[str, Any]] = field(default_factory=list)
    cross_refs: Dict[str, List[str]] = field(default_factory=dict)
    draft: Optional[str] = None
    critique: Optional[str] = None
    final_output: Optional[str] = None
    # v5.8: ReAct traces
    react_traces: List[ReActTrace] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    # v5.8: Reflection loop
    reflection_result: Optional[ReflectionResult] = None

# Strategy Blackboard
@dataclass
class StrategyBrief:
    """Strategic brief for resume generation."""
    themes: List[str]
    differentiators: List[str]
    gaps: List[str]
    recommendations: List[str]
    tone: str = "professional"
    emphasis_areas: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # v5.8: Reflection loop result
    reflection_result: Optional[ReflectionResult] = None

@dataclass
class StrategyBlackboard:
    """Shared state for strategy stack with v5.8 reflection."""
    raw_jd: str
    parsed_jd: Optional[Dict[str, Any]] = None
    themes: List[str] = field(default_factory=list)
    ranked_themes: List[Tuple[str, float]] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    differentiators: List[str] = field(default_factory=list)
    draft_brief: Optional[StrategyBrief] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    final_brief: Optional[StrategyBrief] = None
    # v5.8: Reflection loop
    reflection_iterations: List[ReflectionIteration] = field(default_factory=list)
    reflection_status: ReflectionStatus = ReflectionStatus.PENDING

# Veto System
@dataclass
class VetoSignal:
    """Signal for quality veto."""
    level: VetoLevel
    reason: str
    agent_id: str
    details: Dict[str, Any] = field(default_factory=dict)

# v5.8: Atomic Agent Config
@dataclass
class AtomicAgentConfig:
    """
    Configuration for atomic QA agents in MoE bundles.
    REFACTORED: This class now simply defines the structure.
    The actual definitions are loaded from CONFIG.agent_definitions.
    """
    agent_id: str
    agent_type: str
    complexity: int
    classification: QAClassification
    veto_level: VetoLevel
    enabled: bool = True
    timeout_seconds: int = 30
    retry_count: int = 2

# v5.8: MoE Router Config
@dataclass
class MoERouterConfig:
    """Configuration for MoE validation routers."""
    router_id: str
    router_name: str
    expert_agents: List[AtomicAgentConfig] # These will be populated from CONFIG
    aggregation_method: str = "voting"  # voting, weighted, all_pass
    parallel_execution: bool = True
    timeout_seconds: int = 60

# v5.8: Workflow Blackboard (Enhanced)
@dataclass
class WorkflowBlackboard:
    """Central blackboard for v5.8 agentic orchestration with MoE and Conductor."""
    workflow_id: str
    master_resume: Dict[str, Any]
    job_input: Dict[str, Any]
    
    # Blackboards for each stack
    strategy_board: Optional[StrategyBlackboard] = None
    rag_board: Optional[RAG_Blackboard] = None
    
    # Artifacts
    artifacts: Dict[str, Any] = field(default_factory=dict)
    
    # Execution plan
    plan: Optional['WorkflowPlan'] = None
    
    # State tracking
    state: Dict[str, Any] = field(default_factory=dict)
    
    # v5.8: MoE Results
    moe_decisions: Dict[str, MoEDecision] = field(default_factory=dict)
    
    # v5.8: Conductor branches (for Tree of Thought)
    conductor_branches: List[ConductorBranch] = field(default_factory=list)
    conductor_decision: Optional[ConductorDecision] = None

# v5.8: Workflow Plan
@dataclass
class WorkflowPlan:
    """Execution plan with v5.8 enhancements."""
    plan_id: str
    steps: List['WorkflowStep']
    strategy_type: str = "balanced"  # For conductor branches: gtm-focused, tech-focused, balanced
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowStep:
    """Single step in workflow plan."""
    step_id: str
    agent: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0


# ============================================================================
# PART 3: UTILITIES (from utils_RES.py)
# ============================================================================

class TextUtils:
    """Utility functions for text processing."""
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> List[str]:
        """Extract top keywords from text."""
        if not SKLEARN_AVAILABLE:
            # Fallback: simple word frequency
            min_len = CONFIG.tool_configs.text_utils.min_keyword_len
            words = re.findall(r'\b[a-zA-Z]{' + str(min_len) + r',}\b', text.lower())
            word_freq = defaultdict(int)
            for word in words:
                word_freq[word] += 1
            return [word for word, _ in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]
        
        try:
            vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
            vectorizer.fit([text])
            return vectorizer.get_feature_names_out().tolist()
        except:
            return []
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(re.findall(r'\b\w+\b', text))
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text."""
        return len(re.findall(r'[.!?]+', text))
    
    @staticmethod
    def compute_similarity(text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        if not SKLEARN_AVAILABLE or not text1 or not text2:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text by removing problematic characters."""
        # Remove zero-width spaces and other invisible characters
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

text_utils = TextUtils()

class DuplicateDetector:
    """
    Detect duplicate or near-duplicate content.
    REFACTORED: Threshold is read from CONFIG.
    """
    
    def __init__(self, threshold: Optional[float] = None):
        self.threshold = threshold or CONFIG.tool_configs.duplicate_detector.threshold
        self.seen_content = []
    
    def is_duplicate(self, text: str) -> bool:
        """Check if text is duplicate or near-duplicate."""
        for seen in self.seen_content:
            similarity = text_utils.compute_similarity(text, seen)
            if similarity >= self.threshold:
                return True
        self.seen_content.append(text)
        return False
    
    def reset(self):
        """Reset seen content."""
        self.seen_content = []

class TextSanitizer:
    """Sanitize and clean text content."""
    
    @staticmethod
    def remove_forbidden_terms(text: str, forbidden_terms: List[str]) -> str:
        """Remove forbidden terms from text."""
        for term in forbidden_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def remove_redundant_punctuation(text: str) -> str:
        """Remove redundant punctuation."""
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\,{2,}', ',', text)
        return text

def fence_data(data: Any, tag: str = "data") -> str:
    """Wrap data in XML-style fencing for structured prompts."""
    if isinstance(data, dict) or isinstance(data, list):
        content = json.dumps(data, indent=2)
    else:
        content = str(data)
    return f"<{tag}>\n{content}\n</{tag}>"

def reasoning_config_to_api_params(config: ReasoningConfig) -> Dict[str, Any]:
    """Convert reasoning config to API parameters."""
    params = {
        "temperature": config.temperature,
    }
    
    if config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
        params["n"] = config.num_branches
    elif config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
        params["n"] = config.num_branches
        params["best_of"] = config.num_branches
    
    return params

def enhance_system_prompt_with_reasoning(
    base_prompt: str,
    reasoning_config: ReasoningConfig
) -> str:
    """Enhance system prompt with reasoning instructions."""
    if reasoning_config.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
        return base_prompt + "\n\nPlease think step-by-step and show your reasoning process."
    elif reasoning_config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
        return base_prompt + "\n\nGenerate multiple reasoning paths and select the most consistent answer."
    elif reasoning_config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
        return base_prompt + "\n\nExplore multiple solution branches and evaluate each path."
    return base_prompt

# Logging Filter
class WorkflowLogFilter(logging.Filter):
    """Filter logs by workflow_id."""
    
    def __init__(self, workflow_id: str):
        super().__init__()
        self.workflow_id = workflow_id
    
    def filter(self, record):
        return getattr(record, 'workflow_id', None) == self.workflow_id

# REFACTORED: Removed vulnerable CodeInterpreterTool class


# v5.8: Build atomic agent prompt helper
def build_atomic_agent_prompt(agent_config: AtomicAgentConfig, context: Dict[str, Any]) -> str:
    """Build prompt for atomic QA agent."""
    prompt_parts = [
        f"You are {agent_config.agent_id}, a specialized validation agent.",
        f"Your role: {agent_config.agent_type}",
        f"Classification: {agent_config.classification.name}",
        "",
        "Context:",
        fence_data(context),
        "",
        "Execute your validation and return results in JSON format."
    ]
    return "\n".join(prompt_parts)

# ============================================================================
# PART 4: PROMPTS (from prompts_RES.py)
# ============================================================================

# REFACTORED: Prompts are now loaded directly from the CONFIG object.
try:
    PROMPT_TEMPLATES = CONFIG.prompts
    if not PROMPT_TEMPLATES or not vars(PROMPT_TEMPLATES):
        core_logger.critical("FATAL: PROMPT_TEMPLATES dictionary from CONFIG is empty.")
        raise ValueError("Prompts are missing from configuration.")
    else:
        core_logger.info(f"✓ Successfully loaded prompts from CONFIG")
except Exception as e:
    core_logger.critical(f"FATAL: Could not load prompts from CONFIG: {e}")
    PROMPT_TEMPLATES = {} # Should fail fast later

def _get_prompt_template(key: str) -> str:
    """
    Helper to safely get a prompt template from CONFIG.
    REFACTORED: Fails fast if prompt is missing.
    """
    if not hasattr(PROMPT_TEMPLATES, key):
        core_logger.error(f"Prompt template key '{key}' not found in config!")
        raise KeyError(f"Prompt template key '{key}' not found in master_config_v5_9.json!")
    
    template = getattr(PROMPT_TEMPLATES, key)
    
    if not template or not isinstance(template, str):
        core_logger.error(f"Prompt template key '{key}' is empty or invalid in config!")
        raise ValueError(f"Prompt template '{key}' is empty or invalid in config!")
    
    return template

def build_crl_context_for_section(
    section_name: str,
    job_context: Dict[str, Any],
    master_resume: Dict[str, Any],
    thematic_analysis: Optional[ThematicAnalysis] = None
) -> str:
    """
    Build CRL (Contextual Resume Language) context for a specific section.
    This provides the LLM with structured context about what to generate.
    """
    context_parts = []
    
    # Section-specific guidance
    section_guidance = {
        "K.1_Executive_Summary": "Focus on strategic leadership and measurable impact",
        "K.2_Unify_Bullets": "Emphasize AI/ML expertise and transformation results",
        "K.3_IBM_Bullets": "Highlight enterprise scale and regulatory compliance",
        "K.11_Cover_Letter": "Connect experience directly to job requirements"
    }
    
    guidance = section_guidance.get(section_name, "Generate relevant content for this section")
    context_parts.append(f"Section Guidance: {guidance}")
    
    # Add job context
    context_parts.append(f"Company: {job_context.get('company_name', 'N/A')}")
    context_parts.append(f"Role: {job_context.get('job_title', 'N/A')}")
    
    # Add thematic elements if available
    if thematic_analysis:
        if thematic_analysis.themes:
            context_parts.append(f"Key Themes: {', '.join(thematic_analysis.themes[:5])}")
        if thematic_analysis.skills_required:
            context_parts.append(f"Required Skills: {', '.join(thematic_analysis.skills_required[:5])}")
    
    return "\n".join(context_parts)

def format_prompt_with_context(
    template_key: str,
    **kwargs
) -> str:
    """
    Format a prompt template with provided context.
    Handles both simple string formatting and complex context injection.
    """
    template = _get_prompt_template(template_key)
    
    # Handle XML fencing for structured data
    if "structured_data" in kwargs:
        kwargs["structured_context"] = fence_data(kwargs["structured_data"])
    
    # Format template with kwargs
    try:
        return template.format(**kwargs)
    except KeyError as e:
        core_logger.error(f"Missing required parameter for template '{template_key}': {e}")
        # Return template with placeholders for missing values
        for key in re.findall(r'\{(\w+)\}', template):
            if key not in kwargs:
                kwargs[key] = f"[MISSING: {key}]"
        return template.format(**kwargs)

def get_validation_prompt(
    content: str,
    validation_type: str,
    criteria: List[str]
) -> str:
    """Generate a validation prompt for content review."""
    base_template = _get_prompt_template("validation_base")
    
    criteria_text = "\n".join(f"- {criterion}" for criterion in criteria)
    
    return base_template.format(
        content=content,
        validation_type=validation_type,
        criteria=criteria_text
    )

def get_rag_phase_prompt(
    phase: RAGPhase,
    mission: RAGMission,
    context: Dict[str, Any]
) -> str:
    """Generate a prompt for a specific RAG phase."""
    phase_templates = {
        RAGPhase.EXTRACTION: "rag_extraction",
        RAGPhase.ENRICHMENT: "rag_enrichment", 
        RAGPhase.SYNTHESIS: "rag_synthesis",
        RAGPhase.VALIDATION: "rag_validation"
    }
    
    template_key = phase_templates.get(phase, "rag_generic")
    template = _get_prompt_template(template_key)
    
    return template.format(
        objective=mission.objective,
        context=fence_data(context),
        constraints="\n".join(mission.constraints),
        success_criteria="\n".join(mission.success_criteria)
    )

def get_specialist_prompt(
    specialist_type: str,
    task: str,
    context: Dict[str, Any]
) -> str:
    """Generate a prompt for a specific specialist agent."""
    specialist_templates = {
        "Library_Specialist": "specialist_library",
        "Web_Specialist": "specialist_web",
        "Governor": "specialist_governor",
        "RAG_Synthesizer": "specialist_rag",
        "QA_Auditor": "specialist_qa"
    }
    
    template_key = specialist_templates.get(specialist_type, "specialist_generic")
    
    # Add specialist-specific context
    if specialist_type == "Library_Specialist":
        context["memory_instructions"] = "Use ChromaDB to persist and retrieve memories"
    elif specialist_type == "Web_Specialist":
        context["circuit_breaker"] = "Implement circuit breaker pattern for fault tolerance"
    
    template = _get_prompt_template(template_key)
    return template.format(
        task=task,
        context=fence_data(context)
    )

# REFACTORED: Removed all default fallback prompt dictionaries.


# Export key functions
__all__ = [
    # Models
    'HopExecutionError', 'StagingBufferError', 'CircuitBreakerOpenError', 
    'PhaseTimeoutError', 'FactualFailureException',
    'MechanicalFailureError', 'SemanticFailureError',
    'GateDecision', 'ValidationSeverity', 'ResumeSection', 'JDEnforcementRule',
    'ReasoningStrategy', 'CircuitBreakerState', 'RAGPhase', 'VetoLevel', 'QAClassification',
    'ValidationResult', 'HopResult', 'GenerationAttempt', 'ReasoningConfig',
    'RAGConfig', 'ThematicAnalysis', 'ExperienceBullet', 'PortfolioCompany',
    'RAGMission', 'MasterResumeIndex', 'CircuitBreakerConfig', 'ImmutableStagingBuffer', 'RAG_Blackboard',
    'StrategyBrief', 'VetoSignal', 'AtomicAgentConfig',
    # v5.8 Models
    'ReflectionStatus', 'ToolType', 'ReflectionIteration', 'ReflectionResult',
    'ToolCall', 'ReActTrace', 'MoEExpertResult', 'MoEDecision',
    'ConductorBranch', 'ConductorDecision', 'MoERouterConfig',
    'WorkflowBlackboard', 'WorkflowPlan', 'WorkflowStep', 'StrategyBlackboard',
    
    # Config
    'CONFIG', 'PROJECT_ROOT', 'DATA_DIR', 'OUTPUT_DIR', 'CACHE_DIR',
    'DEFAULT_GENERATION_TEMPERATURE', 'DEFAULT_SYNTHESIS_TEMPERATURE',
    'DEFAULT_MAX_RETRIES', 'DEFAULT_RETRY_DELAY', 'ACCEPTABLE_MIN_WC', 'ACCEPTABLE_MAX_WC',
    
    # Utils
    'text_utils', 'fence_data', 'reasoning_config_to_api_params',
    'enhance_system_prompt_with_reasoning', 'DuplicateDetector',
    'TextSanitizer', 'WorkflowLogFilter',
    'build_atomic_agent_prompt',
    
    # Prompts
    'build_crl_context_for_section', 'format_prompt_with_context',
    'get_validation_prompt', 'get_rag_phase_prompt', 'get_specialist_prompt'
]