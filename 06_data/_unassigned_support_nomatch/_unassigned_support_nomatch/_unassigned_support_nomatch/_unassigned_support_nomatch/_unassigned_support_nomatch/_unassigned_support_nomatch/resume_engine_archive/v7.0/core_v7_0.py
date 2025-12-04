# File: core_v7_0.py
# Overwrites: core_v6_5.py
# Version: 7.0 (LangGraph + Redis)
# Zero-Loss Consolidation - The Foundation
# Merges: models_RES.py → config_RES.py → utils_RES.py → prompts_RES.py
# v7.0: Pointing CONFIG_PATH to master_config_v7_0.json
#
# v6.4 (Corrected V3) CHANGES:
# - Renamed ImmutableStagingBuffer 'metadata' field to 'sections' to match
#   the semantic expectations of the ValidationContext.
# v6.4 (Corrected V2) CHANGES:
# - Added master_resume and job_input to WorkflowBlackboard dataclass
#   to fix TypeError during Governor initialization.
#
# GEMINI REVIEW (v6.4 FINAL):
# - Removed unused import 'TYPE_CHECKING'.
# - Removed unused/uncalled function 'build_atomic_agent_prompt'.
# - Removed unused/uncalled class 'WorkflowLogFilter'.

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
    Any, Callable, ClassVar, Dict, List, Optional, Set, Tuple, Union, TypedDict
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
CONFIG_PATH = PROJECT_ROOT / "master_config_v7_0.json"

class Configuration:
    """
    Central configuration class.
    Reads all settings from master_config_v6_5.json.
    v6.1: Enhanced with cost_config and meta_loop_config
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
        
        # --- v6.1: New config sections ---
        self.cost_config = getattr(self, 'cost_config', self._get_default_cost_config())
        self.meta_loop_config = getattr(self, 'meta_loop_config', self._get_default_meta_loop_config())
        self.circuit_breaker_config = getattr(self, 'circuit_breaker_config', self._get_default_circuit_breaker_config())
        self.reflection_config = getattr(self, 'reflection_config', self._get_default_reflection_config())

        # Set derived defaults
        self.min_confidence_score = getattr(self.signal_constraints, 'MIN_SIGNAL_SCORE', 0.75)
        self.min_relevance_score = getattr(self.signal_constraints, 'MIN_JD_ALIGNMENT', 0.70)
    
    def _get_default_cost_config(self):
        """Default cost config if missing from JSON"""
        ns = type('Namespace', (), {})()
        ns.cost_ceiling_per_workflow = 5.0
        ns.enable_cost_tracking = True
        return ns
    
    def _get_default_meta_loop_config(self):
        """Default meta loop config if missing from JSON"""
        ns = type('Namespace', (), {})()
        ns.feedback_log_path = "feedback_log.jsonl"
        ns.rules_registry_path = "rules_registry.json"
        ns.enable_meta_learning = False
        return ns
    
    def _get_default_circuit_breaker_config(self):
        """Default circuit breaker config if missing from JSON"""
        ns = type('Namespace', (), {})()
        ns.failure_threshold = 3
        ns.reset_timeout_sec = 60
        ns.enable_circuit_breaker = True
        return ns
    
    def _get_default_reflection_config(self):
        """Default reflection config if missing from JSON"""
        ns = type('Namespace', (), {})()
        ns.max_iterations = 3
        ns.enable_reflection = True
        return ns
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if not self.config_path.exists():
                core_logger.critical(f"FATAL: master_config_v7_0.json not found at {self.config_path}.")
                raise FileNotFoundError(f"master_config_v7_0.json not found at {self.config_path}.")
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
    """--- v6.1: Raised when circuit breaker is open and rejects requests ---"""
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
    Dynamically provides resume sections from the master_config_v6_5.json.
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
    Dynamically provides JD enforcement rules from master_config_v6_5.json.
    Access rules like: JDEnforcementRule.KEYWORD_MATCH_REQUIRED
    """
    _rules = CONFIG.rules
    
    def __getattr__(self, name: str) -> Any:
        """Allow dot notation access to rules."""
        if hasattr(self, '_rules') and hasattr(self._rules, name):
            return getattr(self._rules, name)
        raise AttributeError(f"'JDEnforcementRule' has no attribute '{name}'")
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Return all rules as a dictionary."""
        return {key: value for key, value in vars(cls._rules).items() if not key.startswith('_')}

# Instantiate to allow class-level access
JDEnforcementRule = JDEnforcementRule()

class ReasoningStrategy(Enum):
    """Reasoning strategies for LLM generation."""
    STANDARD = "standard"
    CHAIN_OF_THOUGHT = "cot"
    TREE_OF_THOUGHTS = "tot"
    SELF_CONSISTENCY = "self_consistency"

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class RAGPhase(Enum):
    """RAG pipeline phases."""
    EXTRACTION = "extraction"
    ENRICHMENT = "enrichment"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"

class VetoLevel(Enum):
    """Veto signal levels for validation."""
    SOFT = "soft"
    HARD = "hard"
    CRITICAL = "critical"

class QAClassification(Enum):
    """QA validation classifications."""
    LINGUISTIC = "linguistic"
    FACTUAL = "factual"
    STRATEGIC = "strategic"
    GLOBAL = "global"

# REFACTORED: ReflectionStatus for v6.1+ agentic features
class ReflectionStatus(Enum):
    """Status of reflection iterations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CONVERGED = "converged"
    MAX_ITERATIONS_REACHED = "max_iterations"
    FAILED = "failed"

class ToolType(Enum):
    """Types of tools available to ReAct agents."""
    WEB_SEARCH = "web_search"
    COMPANY_RESEARCH = "company_research"
    DOCUMENT_RETRIEVE = "document_retrieve"
    DATA_ANALYSIS = "data_analysis"

# Dataclasses
@dataclass
class ValidationResult:
    """Result from a validation check."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "severity": self.severity.name,
            "message": self.message,
            "details": self.details,
            "metadata": self.metadata
        }

@dataclass
class HopResult:
    """Result from a single hop execution."""
    hop_id: str
    content: str
    metadata: Dict[str, Any]
    passed_validation: bool
    validation_results: List[ValidationResult]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hop_id": self.hop_id,
            "content": self.content,
            "metadata": self.metadata,
            "passed_validation": self.passed_validation,
            "validation_results": [vr.to_dict() for vr in self.validation_results],
            "timestamp": self.timestamp
        }

@dataclass
class GenerationAttempt:
    """Record of a single LLM generation attempt."""
    attempt_number: int
    prompt: str
    response: str
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ReasoningConfig:
    """Configuration for reasoning-enhanced generation."""
    strategy: ReasoningStrategy = ReasoningStrategy.STANDARD
    cot_depth: int = 3
    tot_branches: int = 3
    self_consistency_samples: int = 5
    temperature: float = 0.7
    enable_reflection: bool = False
    max_reflection_iterations: int = 3

@dataclass
class RAGConfig:
    """Configuration for RAG pipeline."""
    max_documents: int = 10
    chunk_size: int = 512
    chunk_overlap: int = 50
    relevance_threshold: float = 0.7
    enable_reranking: bool = True
    timeout_sec: int = 30

@dataclass
class ThematicAnalysis:
    """Results of thematic analysis on job description."""
    themes: List[str]
    skills_required: List[str]
    experience_level: str
    industry: str
    culture_signals: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperienceBullet:
    """Structured representation of an experience bullet."""
    company: str
    role: str
    bullet_text: str
    keywords: List[str]
    impact_score: float
    relevance_score: float
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PortfolioCompany:
    """Information about a portfolio company."""
    name: str
    industry: str
    description: str
    ai_use_cases: List[str]
    revenue_impact: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGMission:
    """RAG mission specification."""
    objective: str
    constraints: List[str]
    success_criteria: List[str]
    timeout_sec: int = 30

@dataclass
class MasterResumeIndex:
    """Index of master resume content."""
    companies: List[str]
    roles: List[str]
    skills: List[str]
    certifications: List[str]
    education: List[Dict[str, str]]
    bullet_pool: Dict[str, List[str]]

@dataclass
class CircuitBreakerConfig:
    """--- v6.1: Configuration for circuit breaker pattern ---"""
    failure_threshold: int = 3
    success_threshold: int = 2
    timeout_sec: int = 60
    half_open_max_requests: int = 1

@dataclass
class ImmutableStagingBuffer:
    """Immutable staging buffer for content validation."""
    content_hash: str
    source_hop: str
    timestamp: str
    # v6.4 (Corrected V3): Renamed 'metadata' to 'sections'
    # This aligns the dataclass with the semantic expectation
    # of the ValidationContext, fixing a critical bug.
    sections: Dict[str, str] = field(default_factory=dict)

@dataclass
class RAG_Blackboard:
    """Blackboard for RAG pipeline state."""
    mission: RAGMission
    documents: List[Dict[str, Any]] = field(default_factory=list)
    chunks: List[str] = field(default_factory=list)
    synthesis: str = ""
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyBrief:
    """Strategic positioning brief from analysis."""
    positioning_statement: str
    key_themes: List[str]
    differentiators: List[str]
    alignment_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VetoSignal:
    """Veto signal from validation."""
    rule_id: str
    level: VetoLevel
    reason: str
    recoverable: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AtomicAgentConfig:
    """Configuration for atomic validation agent."""
    agent_id: str
    agent_type: str
    classification: QAClassification
    priority: int
    enabled: bool
    rules: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

# ===== v6.1+ AGENTIC DATACLASSES =====

@dataclass
class ReflectionIteration:
    """Single iteration of reflection loop."""
    iteration_number: int
    critique: str
    improvements: List[str]
    status: ReflectionStatus
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ReflectionResult:
    """Result of reflection process."""
    iterations: List[ReflectionIteration]
    final_output: str
    converged: bool
    status: ReflectionStatus
    total_iterations: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolCall:
    """Represents a tool call in ReAct loop."""
    tool_type: ToolType
    parameters: Dict[str, Any]
    result: Any
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ReActTrace:
    """Trace of ReAct (Reasoning + Acting) loop."""
    thought: str
    action: ToolCall
    observation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class MoEExpertResult:
    """Result from a single MoE expert."""
    expert_id: str
    output: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MoEDecision:
    """Decision from Mixture of Experts routing."""
    selected_experts: List[str]
    expert_results: List[MoEExpertResult]
    final_output: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConductorBranch:
    """Single branch in Conductor's Tree of Thought."""
    branch_id: str
    strategy_type: str
    plan: 'WorkflowPlan'
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConductorDecision:
    """Final decision from Conductor."""
    winning_branch: ConductorBranch
    explored_branches: List[ConductorBranch]
    reasoning: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class MoERouterConfig:
    """Configuration for MoE router."""
    enabled_experts: List[str]
    voting_strategy: str  # "weighted", "majority", "unanimous"
    confidence_threshold: float
    enable_parallel: bool = True

@dataclass
class WorkflowBlackboard:
    """Central blackboard for workflow state."""
    workflow_id: str
    plan: Optional['WorkflowPlan'] # v6.4: Can be None for dynamic
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # v6.4 (Corrected): Add core context fields
    master_resume: Dict[str, Any] = field(default_factory=dict)
    job_input: Dict[str, Any] = field(default_factory=dict)
    
    # v6.4: Add agent-specific boards
    strategy_board: Optional[StrategyBlackboard] = None
    rag_board: Optional[RAG_Blackboard] = None


@dataclass
class WorkflowPlan:
    """Plan generated by WorkflowPlannerAgent."""
    plan_id: str
    steps: List['WorkflowStep']
    strategy_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowStep:
    """Single step in workflow plan."""
    step_id: str
    agent: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "PENDING"
    result: Any = None
    error: Optional[str] = None

@dataclass
class StrategyBlackboard:
    """Blackboard for strategy stack."""
    job_context: Dict[str, Any]
    strategy_brief: Optional[StrategyBrief] = None
    reflection_result: Optional[ReflectionResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# PART 3: UTILS (from utils_RES.py)
# ============================================================================

class TextUtils:
    """Unified text manipulation utilities."""
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(re.findall(r'\b\w+\b', text))
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove special characters and normalize whitespace."""
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text."""
        if not SKLEARN_AVAILABLE:
            # Fallback to simple word frequency
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = defaultdict(int)
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_freq[word] += 1
            return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:top_n]
        
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
        try:
            vectorizer.fit([text])
            return vectorizer.get_feature_names_out().tolist()
        except:
            return []
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        if not SKLEARN_AVAILABLE:
            # Fallback to simple Jaccard similarity
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            words2 = set(re.findall(r'\b\w+\b', text2.lower()))
            if not words1 or not words2:
                return 0.0
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0
        
        vectorizer = TfidfVectorizer()
        try:
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0

text_utils = TextUtils()

def fence_data(data: Any, tag: str = "context") -> str:
    """Fence data in XML tags for structured prompts."""
    if isinstance(data, dict):
        data_str = json.dumps(data, indent=2)
    elif isinstance(data, (list, tuple)):
        data_str = json.dumps(data, indent=2)
    else:
        data_str = str(data)
    
    return f"<{tag}>\n{data_str}\n</{tag}>"

def reasoning_config_to_api_params(config: ReasoningConfig) -> Dict[str, Any]:
    """Convert ReasoningConfig to API parameters."""
    params = {
        "temperature": config.temperature
    }
    
    if config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
        params["n"] = config.self_consistency_samples
    
    return params

def enhance_system_prompt_with_reasoning(
    base_prompt: str,
    reasoning_config: ReasoningConfig
) -> str:
    """Enhance system prompt with reasoning instructions."""
    if reasoning_config.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
        reasoning_instruction = (
            "\n\nBefore providing your final answer, think step-by-step through the problem. "
            "Show your reasoning process clearly."
        )
    elif reasoning_config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
        reasoning_instruction = (
            "\n\nExplore multiple possible approaches to this problem. "
            "For each approach, evaluate its strengths and weaknesses before selecting the best path."
        )
    elif reasoning_config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
        reasoning_instruction = (
            "\n\nGenerate multiple possible solutions and select the most consistent answer "
            "across different reasoning paths."
        )
    else:
        reasoning_instruction = ""
    
    return base_prompt + reasoning_instruction

class DuplicateDetector:
    """Detect duplicate content using hashing."""
    
    def __init__(self):
        self.seen_hashes: Set[str] = set()
    
    def is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
    
    def clear(self):
        """Clear seen hashes."""
        self.seen_hashes.clear()

class TextSanitizer:
    """Sanitize text for resume generation."""
    
    FORBIDDEN_PATTERNS = [
        r'\[.*?\]',  # Bracketed placeholders
        r'\{.*?\}',  # Curly brace placeholders
        r'<.*?>',    # XML/HTML tags
        r'TODO',     # TODO markers
        r'FIXME',    # FIXME markers
    ]
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        """Remove forbidden patterns."""
        for pattern in cls.FORBIDDEN_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()
    
    @classmethod
    def has_forbidden_content(cls, text: str) -> bool:
        """Check if text contains forbidden patterns."""
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


# ============================================================================
# PART 5: V7.0 LANGGRAPH STATE
# ============================================================================

class GraphState(TypedDict):
    """
    The state object for the v7.0 LangGraph.
    This replaces the in-memory Governor/Blackboard object.
    """
    
    # --- Core Context (from WorkflowBlackboard) ---
    master_resume: Dict[str, Any]
    job_input: Dict[str, Any]
    
    # --- Artifacts (from WorkflowBlackboard) ---
    artifacts: Dict[str, Any]
    
    # --- Graph-Specific State ---
    replan_count: int
    workflow_id: str

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
        raise KeyError(f"Prompt template key '{key}' not found in master_config_v7_0.json!")
    
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
    # v7.0 Models
    'GraphState',
    
    # Config
    'CONFIG', 'PROJECT_ROOT', 'DATA_DIR', 'OUTPUT_DIR', 'CACHE_DIR',
    'DEFAULT_GENERATION_TEMPERATURE', 'DEFAULT_SYNTHESIS_TEMPERATURE',
    'DEFAULT_MAX_RETRIES', 'DEFAULT_RETRY_DELAY', 'ACCEPTABLE_MIN_WC', 'ACCEPTABLE_MAX_WC',
    
    # Utils
    'text_utils', 'fence_data', 'reasoning_config_to_api_params',
    'enhance_system_prompt_with_reasoning', 'DuplicateDetector',
    'TextSanitizer',
    
    # Prompts
    'build_crl_context_for_section', 'format_prompt_with_context',
    'get_validation_prompt', 'get_rag_phase_prompt', 'get_specialist_prompt'
]