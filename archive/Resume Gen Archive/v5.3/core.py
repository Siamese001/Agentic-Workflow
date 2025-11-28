# File: core.py
# Zero-Loss Consolidation - The Foundation
# Merges: models_RES.py → config_RES.py → utils_RES.py → prompts_RES.py
# Version: Consolidated 5.3 + Patch Applied

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
logger = logging.getLogger(__name__)

# ============================================================================
# PART 1: MODELS (from models_RES.py)
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

class ResumeSection(Enum):
    """Enumeration of all resume sections."""
    K0_NAME = "K.0_Name"
    K0_HEADLINE = "K.0_Headline"
    K0_CONTACT = "K.0_Contact"
    K0_EXECUTIVE_SUMMARY_HEADER = "K.0_Executive_Summary_Header"
    K0_EXPERIENCE_HEADER = "K.0_Experience_Header"
    K0_EDUCATION_HEADER = "K.0_Education_Header"
    K0_CERTIFICATIONS_HEADER = "K.0_Certifications_Header"
    K0_COMPETENCIES_HEADER = "K.0_Competencies_Header"
    
    K1_EXECUTIVE_SUMMARY = "K.1_Executive_Summary"
    K2_UNIFY_OVERVIEW = "K.2_Unify_Overview"
    K2_UNIFY_BULLETS = "K.2_Unify_Bullets"
    K3_IBM_OVERVIEW = "K.3_IBM_Overview"
    K3_IBM_BULLETS = "K.3_IBM_Bullets"
    K4_TRADERSENSE_NARRATIVE = "K.4_TraderSense_Narrative"
    K5_EY_NARRATIVE = "K.5_EY_Narrative"
    K6_EARLY_CAREER_NARRATIVE = "K.6_Early_Career_Narrative"
    K7_EDUCATION = "K.7_Education"
    K8_CERTIFICATIONS = "K.8_Certifications"
    K9_COMPETENCIES = "K.9_Competencies"
    K10_SKILLS = "K.10_Skills"
    K11_COVER_LETTER = "K.11_Cover_Letter"

class JDEnforcementRule(Enum):
    """Rules for JD enforcement validation."""
    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    E3_JD_PARSING_SUCCESS = "JD must parse successfully"
    E4_THEMES_EXTRACTED = "JD-derived themes must be extracted"
    E5_SKILLS_EXTRACTED = "JD-derived skills must be extracted (min 5)"
    E6_IMPACT_PHRASES = "JD-derived impact phrases must be captured (min 8)"
    E7_EXPERTISE_MAPPING = "JD expertise areas must map to resume (min 3 overlaps)"
    E8_NO_DEFAULT_PLACEHOLDERS = "No '[JOB TITLE]' or '[COMPANY]' placeholders in JD"

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
    temperature: float = 0.7
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
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyBrief:
    """Strategic brief for generation."""
    primary_focus: str
    differentiators: List[str]
    target_keywords: List[str]
    confidence_score: float = 1.0
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AtomicAgentConfig:
    """Configuration for hyper-atomic agent behaviors."""
    global_negative_constraints: List[str] = field(default_factory=list)
    cognitive_tokens: Dict[str, str] = field(default_factory=dict)
    common_failure_modes: Dict[str, str] = field(default_factory=dict)

@dataclass
class VetoSignal:
    """Signal from a validator indicating pass/fail with priority level."""
    level: VetoLevel
    agent_name: str
    message: str
    suggested_fix: Optional[str] = None

@dataclass
class RAGConfig:
    """Configuration for RAG processing phases."""
    max_phase_retries: int = 3
    phase_timeout_seconds: int = 120
    enable_parallel_phases: bool = False
    min_signal_quality: float = 0.7
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_semantic_search: bool = True
    enable_circuit_breaker: bool = True

@dataclass
class ExperienceBullet:
    """Single experience bullet point."""
    text: str
    metrics: List[str]
    technologies: List[str]
    impact_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PortfolioCompany:
    """Portfolio company investment details."""
    name: str
    role: str
    sector: str
    stage: str
    investment_date: str
    outcome: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGMission:
    """Mission specification for RAG processing."""
    objective: str
    constraints: List[str]
    success_criteria: List[str]
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MasterResumeIndex:
    """Index of master resume content for quick retrieval."""
    executive_summary: str
    skills: List[str]
    experiences: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_requests: int = 3

@dataclass
class ImmutableStagingBuffer:
    """Immutable staging buffer for generated content."""
    sections: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    
    def __post_init__(self):
        """Calculate checksum after initialization."""
        if not self.checksum:
            content = json.dumps(self.sections, sort_keys=True)
            self.checksum = hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify buffer integrity via checksum."""
        current = json.dumps(self.sections, sort_keys=True)
        current_checksum = hashlib.sha256(current.encode()).hexdigest()
        return current_checksum == self.checksum

# ============================================================================
# PART 2: CONFIGURATION (from config_RES.py)
# ============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Create directories if they don't exist
for directory in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# Generation parameters
DEFAULT_GENERATION_TEMPERATURE = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE = 0.3
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2.0
DEFAULT_MAX_OUTPUT_TOKENS = 8000
SAFETY_THRESHOLD = "BLOCK_MEDIUM_AND_ABOVE"

# Load configuration from master_config.json
CONFIG_FILE = DATA_DIR / "master_config.json"

class Configuration:
    """Global configuration manager."""
    
    def __init__(self):
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config_data = json.load(f)
                logger.info(f"✓ Loaded configuration from {CONFIG_FILE}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.config_data = {}
        else:
            logger.warning(f"Config file not found: {CONFIG_FILE}")
            self.config_data = {}
    
    @property
    def constraints(self) -> Dict[str, Any]:
        return self.config_data.get('constraints', {})
    
    @property
    def validation_rules(self) -> Dict[str, Any]:
        return self.config_data.get('validation_rules', {})
    
    @property
    def prompts(self) -> Dict[str, Any]:
        return self.config_data.get('prompts', {})
    
    @property
    def atomic_config(self) -> AtomicAgentConfig:
        data = self.config_data.get('atomic_agent_config', {})
        return AtomicAgentConfig(**data)
    
    @property
    def rag_config(self) -> RAGConfig:
        rag_data = self.config_data.get('rag_config', {})
        return RAGConfig(**rag_data) if rag_data else RAGConfig()
    
    @property
    def default_model(self) -> str:
        return self.config_data.get('default_model', 'gemini-2.5-pro')

    @property
    def enricher_rules(self) -> Dict[str, Any]:
        return self.config_data.get('enricher_rules', {})

    @property
    def hyphenation_rules(self) -> Dict[str, Any]:
        return self.config_data.get('hyphenation_rules', {})

    @property
    def governor_config(self) -> Dict[str, Any]:
        return self.config_data.get('governor_config', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config_data.get(key, default)

# Global configuration instance
CONFIG = Configuration()

# ============================================================================
# PART 3: UTILITIES (from utils_RES.py)
# ============================================================================

class TextUtils:
    """Text processing utilities."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        return text.strip()
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

text_utils = TextUtils()

def fence_data(data: Any, tag: str = "data") -> str:
    """Fence data in XML-style tags for LLM context."""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, indent=2)
    else:
        data_str = str(data)
    return f"<{tag}>\n{data_str}\n</{tag}>"

def reasoning_config_to_api_params(config: ReasoningConfig) -> Dict[str, Any]:
    """Convert reasoning config to API parameters."""
    return {
        'temperature': config.temperature,
        'num_samples': config.num_branches if config.strategy == ReasoningStrategy.SELF_CONSISTENCY else 1
    }

def enhance_system_prompt_with_reasoning(prompt: str, config: ReasoningConfig) -> str:
    """Enhance system prompt with reasoning strategy instructions."""
    if config.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
        enhancement = "\n\nPlease think step-by-step and show your reasoning process."
    elif config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
        enhancement = "\n\nGenerate multiple reasoning paths and identify the most consistent answer."
    elif config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
        enhancement = "\n\nExplore multiple solution paths and evaluate each branch critically."
    else:
        enhancement = ""
    
    return prompt + enhancement

class DuplicateDetector:
    """Detect duplicate or near-duplicate content."""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.seen_content: Set[str] = set()
    
    def is_duplicate(self, text: str) -> bool:
        """Check if text is duplicate."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.seen_content:
            return True
        self.seen_content.add(text_hash)
        return False
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not SKLEARN_AVAILABLE:
            return 0.0
        
        vectorizer = TfidfVectorizer()
        try:
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0

class TextSanitizer:
    """Sanitize text for ATS compliance."""
    
    FORBIDDEN_PATTERNS = [
        r'<table',
        r'style=',
        r'onclick=',
        r'javascript:',
    ]
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Remove ATS-unfriendly patterns."""
        for pattern in TextSanitizer.FORBIDDEN_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def is_clean(text: str) -> bool:
        """Check if text is ATS-compliant."""
        for pattern in TextSanitizer.FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return False
        return True

class WorkflowLogFilter(logging.Filter):
    """Filter for workflow-specific logging."""
    
    def filter(self, record):
        return 'workflow' in record.name.lower()

class CodeInterpreterTool:
    """Execute code safely in sandboxed environment."""
    
    @staticmethod
    def execute_python(code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code with timeout."""
        try:
            # Create temporary file
            temp_file = f"/tmp/exec_{uuid.uuid4().hex}.py"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Execute with timeout
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Clean up
            os.remove(temp_file)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# ============================================================================
# PART 4: PROMPTS (from prompts_RES.py)
# ============================================================================

# Load Recipe Book (prompts.json) from global CONFIG
try:
    PROMPT_TEMPLATES = CONFIG.prompts.get('prompts', {})
    if not PROMPT_TEMPLATES:
        logger.warning("PROMPT_TEMPLATES dictionary from CONFIG is empty.")
    else:
        logger.info(f"✓ Successfully loaded {len(PROMPT_TEMPLATES)} prompts from CONFIG")
except Exception as e:
    logger.critical(f"FATAL: Could not load prompts from CONFIG: {e}")
    PROMPT_TEMPLATES = {}

def _get_prompt_template(key: str) -> str:
    """Helper to safely get a prompt template."""
    template = PROMPT_TEMPLATES.get(key)
    if not template:
        logger.error(f"Prompt template key '{key}' not found in prompts.json!")
        raise KeyError(f"Prompt template key '{key}' not found in prompts.json!")
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
        logger.error(f"Missing required parameter for template '{template_key}': {e}")
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
    """
    Generate a validation prompt for content review.
    """
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
    """
    Generate a prompt for a specific RAG phase.
    """
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
    """
    Generate a prompt for a specific specialist agent.
    """
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

# Fallback prompt templates if prompts.json is not available
DEFAULT_PROMPTS = {
    "validation_base": """
Validate the following content according to {validation_type} criteria:

Content:
{content}

Criteria:
{criteria}

Provide a detailed validation report.
""",
    "rag_generic": """
Objective: {objective}

Context:
{context}

Constraints:
{constraints}

Success Criteria:
{success_criteria}

Execute the task and provide results.
""",
    "specialist_generic": """
Task: {task}

Context:
{context}

Execute the specialist task and provide structured output.
"""
}

# Update PROMPT_TEMPLATES with defaults if empty
if not PROMPT_TEMPLATES:
    PROMPT_TEMPLATES = DEFAULT_PROMPTS
    logger.warning("Using default prompt templates")

# Export key functions
__all__ = [
    # Models
    'HopExecutionError', 'StagingBufferError', 'CircuitBreakerOpenError', 
    'PhaseTimeoutError', 'FactualFailureException',
    'GateDecision', 'ValidationSeverity', 'ResumeSection', 'JDEnforcementRule',
    'ReasoningStrategy', 'CircuitBreakerState', 'RAGPhase', 'VetoLevel', 'QAClassification',
    'ValidationResult', 'HopResult', 'GenerationAttempt', 'ReasoningConfig',
    'RAGConfig', 'ThematicAnalysis', 'ExperienceBullet', 'PortfolioCompany',
    'RAGMission', 'MasterResumeIndex', 'CircuitBreakerConfig', 'ImmutableStagingBuffer',
    'StrategyBrief', 'VetoSignal', 'AtomicAgentConfig',
    
    # Config
    'CONFIG', 'PROJECT_ROOT', 'DATA_DIR', 'OUTPUT_DIR', 'CACHE_DIR',
    'DEFAULT_GENERATION_TEMPERATURE', 'DEFAULT_SYNTHESIS_TEMPERATURE',
    'DEFAULT_MAX_RETRIES', 'DEFAULT_RETRY_DELAY',
    
    # Utils
    'text_utils', 'fence_data', 'reasoning_config_to_api_params',
    'enhance_system_prompt_with_reasoning', 'DuplicateDetector',
    'TextSanitizer', 'WorkflowLogFilter', 'CodeInterpreterTool',
    
    # Prompts
    'build_crl_context_for_section', 'format_prompt_with_context',
    'get_validation_prompt', 'get_rag_phase_prompt', 'get_specialist_prompt'
]
