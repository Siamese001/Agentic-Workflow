# helpers.py
"""
Shared utility functions, dataclasses, and constants for the decoupled pipeline (v16.0-100%).
This is the canonical source of truth for ALL shared data models.

CRITICAL: This file now includes ALL configuration classes from v15.55:
- ReasoningConfig with all section-specific configs
- ContentConstraintsConfig with all word count boundaries
- SignalControlConfig for signal scoring
- PromptAddendumConfig for reasoning directives
- CircuitState enum for circuit breaker
- All reasoning enhancement functions
- Signal score calculation function
"""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import re
import sys
import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (Any, Callable, ClassVar, Dict, List, Optional, Tuple, Union, Set)

# Default temperature for generation
DEFAULT_GENERATION_TEMPERATURE = 0.9

# === Enums ===

class GateDecision(Enum):
    PROCEED = "PROCEED"
    HALT = "HALT"

class ValidationSeverity(Enum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
    ERROR = auto()

class HopStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    PENDING = "PENDING"
    RUNNING = "RUNNING"

class BulletProvenance(Enum):
    Verbatim = "Verbatim"
    Customized = "Customized"
    Synthetic = "Synthetic"

class CircuitState(Enum):
    """Circuit breaker states for resilient RAG operations"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing - reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class ResumeSection(Enum):
    # K.0 - Header Components
    K0_NAME = "K.0_Name"
    K0_HEADLINE = "K.0_Headline"
    K0_CONTACT = "K.0_Contact"
    K0_EXECUTIVE_SUMMARY_HEADER = "K.0_Executive_Summary_Header"
    K0_EXPERIENCE_HEADER = "K.0_Experience_Header"
    K0_EDUCATION_HEADER = "K.0_Education_Header"
    K0_CERTIFICATIONS_HEADER = "K.0_Certifications_Header"
    K0_COMPETENCIES_HEADER = "K.0_Competencies_Header"

    # K.1 - K.11 - Generated Content Sections
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

# === Configuration Classes (PRESERVED FROM v15.55) ===

@dataclass
class ReasoningConfig:
    """
    Configuration for Chain-of-Thought, Tree-of-Thought, and Self-Consistency reasoning.
    PRESERVED FROM v15.55 - All parameters and section configs intact.
    """
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 4
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

# Initialize all ReasoningConfig class variables (EXACT VALUES FROM v15.55)
ReasoningConfig.DEFAULT = ReasoningConfig()

ReasoningConfig.K0_HEADLINE_CONFIG = ReasoningConfig(
    cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=5, reflexion=True
)
ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=4
)
ReasoningConfig.K2_UNIFY_BULLETS_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True
)
ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True
)
ReasoningConfig.K3_IBM_BULLETS_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True
)
ReasoningConfig.K3_IBM_OVERVIEW_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True
)
ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False
)
ReasoningConfig.K5_EY_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=2, min_tot_depth=3, self_consistency=4, reflexion=True
)
ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False
)
ReasoningConfig.K9_COMPETENCIES_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=6, reflexion=True
)
ReasoningConfig.K10_SKILLS_CONFIG = ReasoningConfig(
    cot_min_paths=1, tot_branches=2, min_tot_depth=1, self_consistency=1, reflexion=False
)
ReasoningConfig.K11_COVER_LETTER_CONFIG = ReasoningConfig(
    cot_min_paths=4, tot_branches=3, min_tot_depth=3, self_consistency=6, reflexion=True, max_reflexion_loops=2
)

@dataclass
class ContentConstraintsConfig:
    """
    All word count boundaries and content constraints.
    PRESERVED FROM v15.55 - All 32+ constraints intact.
    """
    # Global constraints
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7

    # K0 Headline constraints
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K1 Executive Summary constraints
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 7
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4

    # K2/K3 Overview constraints
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35

    # K4/K5/K6 Narrative constraints
    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 60
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70

    # Combined constraints for K2/K3
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    # K11 Cover Letter constraints
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35

@dataclass
class SignalControlConfig:
    """
    Signal scoring parameters for content generation.
    PRESERVED FROM v15.55.
    """
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65
    SECTION_SIGNAL_SCORE_MAX: float = 0.90

@dataclass
class PromptAddendumConfig:
    """
    Reasoning directives for system prompts.
    PRESERVED FROM v15.55 - All directive templates intact.
    """
    HEADER: str = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n\n"
    FOOTER: str = "\nAll directives MUST be followed in the output.\n"

    COT_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: Explore at least {cot} distinct reasoning paths before reaching a conclusion.\n"),
        (4, "• Explore {cot} different reasoning paths; compare and synthesize insights.\n"),
        (0, "• Consider multiple reasoning approaches before concluding.\n")
    ])

    TOT_B_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: At each decision point, systematically evaluate {tot_b} different branches/alternatives.\n"),
        (4, "• Explore {tot_b} decision branches at critical junctures; document tradeoffs.\n"),
        (0, "• Consider multiple decision branches at key steps.\n")
    ])

    TOT_D_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: Reasoning depth must be {tot_d}+ levels deep with explicit layer separation.\n"),
        (4, "• Provide {tot_d}-level deep reasoning: foundation → intermediate → advanced → synthesis.\n"),
        (3, "• Provide {tot_d}-level reasoning with clear progression of thinking.\n"),
        (0, "• Structure reasoning with clear logical progression.\n")
    ])

    REFLEXION_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (3, "• MANDATORY: Review your answer {max_loops} times, refining on each pass. Document improvements.\n"),
        (2, "• Review your answer {max_loops} times; improve if refinements are identified.\n"),
        (1, "• Review and refine your answer at least once.\n")
    ])

# Initialize prompt addendum config
PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()

# === Core Dataclasses ===

@dataclass
class ValidationResult:
    """Standardized validation result object."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> ValidationResult:
        try:
            severity_enum = ValidationSeverity[data.get('severity', 'INFO')]
        except KeyError:
            severity_enum = ValidationSeverity.INFO
        return cls(
            rule_id=data.get('rule_id', 'UNKNOWN_RULE'),
            passed=data.get('passed', False),
            severity=severity_enum,
            message=data.get('message', ''),
            details=data.get('details', {})
        )

@dataclass
class HopCheckpoint:
    """
    A cryptographically verifiable record of a hop's execution.
    This is the core of the Chain of Custody.
    """
    hop_id: str
    hop_name: str
    status: HopStatus
    timestamp_start: str
    timestamp_end: str
    
    # Cryptographic proof of data provenance
    input_artifact_hashes: Dict[str, str] = field(default_factory=dict)
    output_artifact_hashes: Dict[str, str] = field(default_factory=dict)
    
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class RAGCritique:
    """Output of the LLM-powered critique step."""
    is_sufficient: bool = False
    confidence_score: float = 0.0
    critique_text: str = ""
    refinement_tasks: List[str] = field(default_factory=list)

@dataclass
class RAGMission:
    """Mission parameters for the RAG agent."""
    target_company_name: str = "Default Co"
    precise_role_title: str = "Default Role"
    key_technologies: List = field(default_factory=list)
    core_responsibilities: List = field(default_factory=list)
    signal_gap_keywords: List = field(default_factory=list)
    signal_overlap_keywords: List = field(default_factory=list)

@dataclass
class ThematicAnalysis:
    """
    The canonical output of the RAG analysis.
    PRESERVED FROM v15.55 with enhancements from v1.2.
    """
    primary_theme: Dict = field(default_factory=dict)
    secondary_themes: List[Dict] = field(default_factory=list)
    role_classification: Dict = field(default_factory=dict)
    positioning_directives: Dict = field(default_factory=dict)
    authenticity_patterns: Dict = field(default_factory=dict)
    competitive_intelligence: Any = None
    problem_solution_narratives: Optional[Dict] = None
    signal_quality_score: float = 0.0
    retrieval_method: str = "UNKNOWN"
    retrieval_sources: List[Any] = field(default_factory=list)
    weighting_formula: Optional[Dict] = None
    evidence_log: List[Dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> ThematicAnalysis:
        """Reconstructs ThematicAnalysis from a dictionary."""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

# === Workflow Spec Dataclasses ===

@dataclass
class Artifact:
    """Represents the state of a data artifact (a file) in the run directory."""
    id: str
    path: Path
    hash: Optional[str] = None
    is_ready: bool = False
    is_static: bool = False

@dataclass
class HopInput:
    """Defines a single input dependency for a hop."""
    arg_name: str 
    artifact_id: str

@dataclass
class HopOutput:
    """Defines a single output artifact for a hop."""
    arg_name: str
    artifact_id: str

@dataclass
class RetryPolicy:
    """Defines the retry strategy for a hop."""
    attempts: int = 1
    delay_seconds: int = 5
    backoff_multiplier: float = 2.0

@dataclass
class HopSpec:
    """Defines a single, executable hop in the workflow DAG."""
    id: str
    script: str
    description: str
    inputs: List[HopInput] = field(default_factory=list)
    outputs: List[HopOutput] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    extra_args: List[str] = field(default_factory=list)

@dataclass
class WorkflowSpec:
    """Defines the entire workflow."""
    name: str
    version: str
    hops: List[HopSpec] = field(default_factory=list)
    
    def get_hop_by_id(self, hop_id: str) -> Optional[HopSpec]:
        for hop in self.hops:
            if hop.id == hop_id:
                return hop
        return None

# === Exceptions ===

class HopExecutionError(Exception):
    """Raised when a hop script fails (non-zero exit code)."""
    pass

class StagingBufferError(Exception):
    """Raised on issues with the ImmutableStagingBuffer."""
    pass

class WorkflowSpecError(Exception):
    """Raised on issues with loading or parsing the workflow spec."""
    pass

# === Reasoning Enhancement Functions (PRESERVED FROM v15.55) ===

def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """
    Normalizes and clamps reasoning parameters to safe ranges.
    PRESERVED FROM v15.55 lines 372-390.
    """
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12
    reflexion = config.reflexion if config.reflexion is not None else True
    max_loops = config.max_reflexion_loops if config.max_reflexion_loops is not None else 2

    sc_clamped = max(1, min(sc, 8))

    return {
        "cot": max(2, min(config.cot_min_paths if config.cot_min_paths is not None else 3, 8)),
        "tot_b": max(2, min(tot_b, 6)),
        "tot_d": max(2, min(tot_d, 5)),
        "sc": sc_clamped,
        "reflexion": reflexion,
        "max_loops": max(1, min(max_loops, 5))
    }

def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """
    Allocates max_tokens based on reasoning depth and complexity.
    PRESERVED FROM v15.55 lines 392-415.
    """
    base_limit = 16384
    high_sc_limit = 24000
    mid_complex_limit = 26000
    high_complex_limit = 28000
    max_complex_limit = 30000

    if tot_d >= 4:
        max_tokens = max_complex_limit
    elif tot_d >= 3 and cot >= 5:
        max_tokens = high_complex_limit
    elif tot_d >= 3 or cot >= 5:
        max_tokens = mid_complex_limit
    elif sc >= 15:
        max_tokens = high_sc_limit
    else:
        max_tokens = base_limit

    rag_config_max = 30000
    return max(base_limit, min(max_tokens, rag_config_max))

def _build_reasoning_prompt_addendum(params: Dict) -> str:
    """
    Builds reasoning directives to append to system prompts.
    PRESERVED FROM v15.55 lines 417-436.
    """
    addendum = PROMPT_ADDENDUM_CONFIG.HEADER

    def find_directive(directives: List[Tuple[int, str]], value: int) -> str:
        for threshold, text in directives:
            if value >= threshold:
                return text
        return ""

    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES, params.get('cot', 0)).format(cot=params.get('cot'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES, params.get('tot_b', 0)).format(tot_b=params.get('tot_b'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES, params.get('tot_d', 0)).format(tot_d=params.get('tot_d'))

    if params.get('reflexion'):
        addendum += find_directive(PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES, params.get('max_loops', 0)).format(max_loops=params.get('max_loops'))

    addendum += PROMPT_ADDENDUM_CONFIG.FOOTER
    return addendum

def reasoning_config_to_api_params(reasoning_config: ReasoningConfig, rag_config_max_tokens: int = 30000) -> dict:
    """
    Converts reasoning config to API parameters with generation config.
    PRESERVED FROM v15.55 lines 334-370.
    
    Args:
        reasoning_config: ReasoningConfig instance
        rag_config_max_tokens: Maximum tokens from RAG config (default 30000)
    
    Returns:
        Dictionary with generation_config and system_prompt_addendum
    """
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)
    temperature = DEFAULT_GENERATION_TEMPERATURE

    allocated_max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    final_max_tokens = min(allocated_max_tokens, rag_config_max_tokens)

    prompt_addendum = _build_reasoning_prompt_addendum(params)

    logger.debug(
        f"Reasoning Params: cot={params['cot']}, tot_b={params['tot_b']}, tot_d={params['tot_d']}, "
        f"sc={params['sc']}, reflexion={params['reflexion']}, max_loops={params['max_loops']}, "
        f"temp={temperature}, allocated_tokens={allocated_max_tokens}, final_tokens={final_max_tokens}"
    )

    # Return dict without trying to create GenerationConfig (since genai may not be imported)
    return {
        "temperature": temperature,
        "max_output_tokens": final_max_tokens,
        "system_prompt_addendum": prompt_addendum,
        **params
    }

def enhance_system_prompt_with_reasoning(
    base_system_prompt: str,
    reasoning_config: ReasoningConfig,
    section_id: str = "UNKNOWN"
) -> str:
    """
    Enhance a system prompt with reasoning configuration directives.
    PRESERVED FROM v15.55 lines 438-456.

    Args:
        base_system_prompt: Original system prompt
        reasoning_config: ReasoningConfig instance
        section_id: For logging

    Returns:
        Enhanced system prompt with reasoning directives appended
    """
    api_params = reasoning_config_to_api_params(reasoning_config)
    enhanced = base_system_prompt + api_params["system_prompt_addendum"]
    return enhanced

# === Signal Scoring Function (PRESERVED FROM v15.55) ===

def calculate_signal_score(text_content, thematic_analysis: ThematicAnalysis) -> float:
    """
    Calculate signal score based on keyword matches between content and thematic analysis.
    PRESERVED FROM v15.55 lines 4593-4631.
    
    Args:
        text_content: Text to score (str, list, or dict)
        thematic_analysis: ThematicAnalysis with competitive intelligence
    
    Returns:
        Float score between 0.0 and 1.0
    """
    if not text_content:
        return 0.0

    if isinstance(text_content, (list, dict)):
        text = str(text_content).lower()
    else:
        text = str(text_content).lower()

    if not text:
        return 0.0

    try:
        differentiators = set()
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Use differentiator_keywords which is the top N ranked keywords
            differentiators = set(getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', []) or [])

        primary_theme_data = thematic_analysis.primary_theme or {}
        primary_words = set(primary_theme_data.get('keywords', []))

        all_jd_words = differentiators.union(primary_words)

    except (AttributeError, KeyError, TypeError) as e:
        logging.warning(f"Error accessing keywords in thematic_analysis for signal score calculation: {e}")
        return 0.0

    if not all_jd_words:
        return 0.0  # No keywords to score against

    words_in_text = set(re.findall(r'\b\w+\b', text))
    matches = words_in_text.intersection(all_jd_words)
    score = len(matches) / 10.0  # Base score: 0.1 per unique keyword match

    # Bonus for matching primary theme keywords
    primary_matches = words_in_text.intersection(primary_words)
    score += len(primary_matches) * 0.1

    return min(1.0, score)  # Cap score at 1.0 (100%)

# === Logging Setup ===

class WorkflowLogFilter(logging.Filter):
    """
    Custom logging filter that injects workflow_id into every log record.
    Enables tracking of logs across distributed systems and concurrent workflows.
    """
    def __init__(self, workflow_id: str):
        super().__init__()
        self.workflow_id = workflow_id
    
    def filter(self, record):
        record.workflow_id = self.workflow_id
        return True

def setup_workflow_logging(workflow_id: Optional[str] = None, test_mode: bool = False) -> Tuple[logging.Logger, str]:
    """
    Sets up enhanced logging with timestamped log files and workflow_id tracking.
    PRESERVED FROM v15.55 lines 85-128.
    
    Args:
        workflow_id: Optional workflow ID. If None, generates a new UUID.
        test_mode: If True, skips file handler creation (for testing)
    
    Returns:
        Tuple of (configured logger instance, log file path)
    """
    if workflow_id is None:
        workflow_id = str(uuid.uuid4())[:8]  # Short UUID for readability
    
    # Create timestamped log filename
    log_filename = f"resume_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - [%(workflow_id)s] - %(message)s'
    log_formatter = logging.Formatter(log_format)
    
    # Get root logger and clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Console Handler (INFO level for standard output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_formatter)
    console_handler.addFilter(WorkflowLogFilter(workflow_id))
    root_logger.addHandler(console_handler)
    
    # File Handler (DEBUG level for detailed logs) - skip in test mode
    if not test_mode:
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_formatter)
        file_handler.addFilter(WorkflowLogFilter(workflow_id))
        root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"H0_INFO - Workflow logging initialized. ID: {workflow_id}, Log file: {log_filename if not test_mode else 'DISABLED (test mode)'}")
    
    return logger, log_filename

# === Utility Functions ===

def serialize_dataclass(obj):
    """Serialize a dataclass to dict, handling nested dataclasses."""
    if is_dataclass(obj):
        return asdict(obj)
    return obj

def hash_dict(data: Dict) -> str:
    """Generate SHA-256 hash of a dictionary."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def load_json_file(filepath: str) -> Dict:
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {filepath}: {e}")
        raise

def save_json_file(filepath: str, data: Dict):
    """Save dictionary to JSON file with pretty printing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
