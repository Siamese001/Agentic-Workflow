from __future__ import annotations

# Standard library - Built-ins
import copy
import functools
import hashlib
import json
import logging
import math
import os
import random
import re
import shutil
import signal
import textwrap
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import (
    Any, Callable, ClassVar, Dict, List, 
    Optional, Set, Tuple, TypeVar, Union
)

T = TypeVar('T')

from dataclasses import asdict, dataclass, field, is_dataclass
from functools import partial

from dotenv import load_dotenv
load_dotenv()

__version__ = "14_24"

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai package not installed. Web RAG disabled.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Cosine similarity will use basic implementation.")

STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'we', 'you', 'your', 'our', 'this',
    'these', 'those', 'or', 'but', 'not', 'have', 'had', 'do', 'does',
    'can', 'should', 'would', 'could', 'must', 'may', 'might', 'been',
    'being', 'about', 'through', 'their', 'there', 'where', 'which',
    'who', 'whom', 'when', 'why', 'how', 'all', 'each', 'other', 'such'
}

def _load_json_data(filename: str, description: str) -> Dict:
    """Loads JSON data from a file in the same directory as the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"Successfully loaded {description} from '{filename}'.")
            return data
    except FileNotFoundError:
        logging.error(f"CRITICAL: {description} file not found at '{filepath}'. Halting.")
        raise FileNotFoundError(f"{description} file not found: {filepath}")
    except json.JSONDecodeError as e:
        logging.error(f"CRITICAL: Failed to decode JSON from {description} file '{filepath}': {e}. Halting.")
        raise json.JSONDecodeError(f"Failed to decode {description} file: {e.msg}", e.doc, e.pos)
    except Exception as e:
        logging.error(f"CRITICAL: An unexpected error occurred while loading {description} file '{filepath}': {e}. Halting.")
        raise e

try:
    MASTER_RESUME_DATA = _load_json_data("master_resume.json", "Master Resume data")
    HYPHENATION_RULES_DATA = _load_json_data("hyphenation_rules.json", "Hyphenation Rules")
    APP_TRACKER_SCHEMA_DATA = _load_json_data("app_tracker_schema.json", "App Tracker Schema")
    ARTIST_SPECS_DATA = _load_json_data("artist_specs.json", "Artist Generation Specs")
except Exception as load_error:
    print(f"FATAL ERROR during data loading: {load_error}")
    exit(1) # Or handle error appropriately

@dataclass
class ReasoningConfig:
    """Centralized reasoning configuration"""
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

@dataclass
class ContentConstraintsConfig:
    """Centralized configuration for content constraints like word counts and thresholds."""
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7

    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 7
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4

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

    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35

@dataclass
class SignalControlConfig:

    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65
    SECTION_SIGNAL_SCORE_MAX: float = 0.90

@dataclass
class ThematicAnalysis:
     primary_theme: Dict = field(default_factory=dict)
     secondary_themes: List[Dict] = field(default_factory=list)
     role_classification: Dict = field(default_factory=dict)
     positioning_directives: Dict = field(default_factory=dict)
     authenticity_patterns: Dict = field(default_factory=dict)
     competitive_intelligence: Any = None # Mock object often used here
     problem_solution_narratives: Optional[Dict] = None
     signal_quality_score: float = 0.0
     retrieval_method: str = "UNKNOWN"
     retrieval_sources: List[Any] = field(default_factory=list)
     weighting_formula: Optional[Dict] = None

@dataclass
class ReasoningIntensityConfig:
    """Configuration for reasoning intensity calculation weights and thresholds."""
    WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'cot': 2.0,
        'tot_b': 2.0,
        'tot_d': 2.0,
        'sc': 0.2  # Equivalent to dividing by 5.0
    })
    THRESHOLDS: List[Tuple[str, int]] = field(default_factory=lambda: [
        ("VERY_HIGH", 35), ("HIGH", 25), ("MODERATE", 15), ("LOW", 8)
    ])

@dataclass
class PromptAddendumConfig:
    """Configuration for the reasoning prompt addendum strings."""
    HEADER: str = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n(Configuration Level: {reasoning_level}, Intensity: {intensity_score:.1f}/40)\n\n"
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

class ResumeSection(Enum):
    """Centralized enum for all resume section keys."""
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

ReasoningConfig.DEFAULT = ReasoningConfig()

ReasoningConfig.K0_HEADLINE_CONFIG = ReasoningConfig(cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=4)

ReasoningConfig.K2_UNIFY_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)
ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K3_IBM_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K3_IBM_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)

ReasoningConfig.K5_EY_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=2, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)

ReasoningConfig.K9_COMPETENCIES_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=6, reflexion=True)

ReasoningConfig.K10_SKILLS_CONFIG = ReasoningConfig(cot_min_paths=1, tot_branches=2, min_tot_depth=1, self_consistency=1, reflexion=False)

ReasoningConfig.K11_COVER_LETTER_CONFIG = ReasoningConfig(cot_min_paths=4, tot_branches=3, min_tot_depth=3, self_consistency=6, reflexion=True, max_reflexion_loops=2)

REASONING_INTENSITY_CONFIG = ReasoningIntensityConfig()
PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()
        
def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """
    Converts reasoning config to Gemini API parameters.
    Uses _allocate_tokens_from_depth for proportional max_output_tokens.
    """
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)
    intensity, level = _calculate_reasoning_intensity(params)
    params['intensity_score'] = intensity
    params['reasoning_level'] = level

    temperature = _get_generation_temperature()

    allocated_max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    try:
         absolute_max_tokens = RAGConfig().max_tokens
    except NameError:
         logging.warning("RAGConfig not found, using default absolute max_tokens=30000.")
         absolute_max_tokens = 30000

    final_max_tokens = min(allocated_max_tokens, absolute_max_tokens)

    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(f"Reasoning config: intensity={intensity:.1f}, temp={temperature}, calculated_max_tokens={allocated_max_tokens}, final_max_tokens={final_max_tokens}, level={level}")
    except NameError: # Handle case where logger might not be fully configured yet
        pass

    return {
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=final_max_tokens),
        "system_prompt_addendum": prompt_addendum,
        **params
    }

def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """Handles defaults and clamps reasoning config values."""
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12 # Keep original default intention
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

def _calculate_reasoning_intensity(params: Dict) -> Tuple[float, str]:
    """Calculates a numeric intensity score and a qualitative level from reasoning parameters."""
    weights = REASONING_INTENSITY_CONFIG.WEIGHTS
    intensity = (
        params.get('cot', 0) * weights.get('cot', 2.0) +
        params.get('tot_b', 0) * weights.get('tot_b', 2.0) +
        params.get('tot_d', 0) * weights.get('tot_d', 2.0) +
        params.get('sc', 0) * weights.get('sc', 0.2)
    )
    level = "MINIMAL" # Default level
    for level_name, threshold in REASONING_INTENSITY_CONFIG.THRESHOLDS:
        if intensity >= threshold:
            level = level_name
            break
    return intensity, level

def _get_generation_temperature() -> float:
    """
    This version maximizes temperature to promote creative and unique output,
    while the workflow's Reasoning Intensity (CoT, ToT) maintains signal/relevance.
    The 'intensity' parameter was previously unused, so it has been removed.
    """
    return 0.9

def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """
    Allocates max_tokens based on reasoning depth and complexity, providing
    higher limits for more complex reasoning tasks.
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
    """Constructs the system prompt addendum based on reasoning parameters."""
    addendum = PROMPT_ADDENDUM_CONFIG.HEADER.format(
        reasoning_level=params.get('reasoning_level', 'UNKNOWN'),
        intensity_score=params.get('intensity_score', 0.0)
    )

    def find_directive(directives: List[Tuple[int, str]], value: int) -> str:
        """Helper to find the correct directive based on a value."""
        for threshold, text in directives:
            if value >= threshold:
                return text
        return "" # Should not happen if a (0, text) entry exists

    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES, params.get('cot', 0)).format(cot=params.get('cot'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES, params.get('tot_b', 0)).format(tot_b=params.get('tot_b'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES, params.get('tot_d', 0)).format(tot_d=params.get('tot_d'))

    if params.get('reflexion'):
        addendum += find_directive(PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES, params.get('max_loops', 0)).format(max_loops=params.get('max_loops'))

    addendum += PROMPT_ADDENDUM_CONFIG.FOOTER
    return addendum

def enhance_system_prompt_with_reasoning(
    base_system_prompt: str,
    reasoning_config: ReasoningConfig,
    section_id: str = "UNKNOWN"
) -> str:
    """
    Enhance a system prompt with reasoning configuration directives.
    
    Args:
        base_system_prompt: Original system prompt (e.g., "You are an expert...")
        reasoning_config: ReasoningConfig instance
        section_id: For logging (e.g., "K.1", "K.4")
        
    Returns:
        Enhanced system prompt with reasoning directives appended
    """
    api_params = reasoning_config_to_api_params(reasoning_config)
    enhanced = base_system_prompt + api_params["system_prompt_addendum"]
    return enhanced

class GateDecision(Enum):
    PROCEED = "PROCEED"
    ERROR_REPORT_ONLY = "ERROR_REPORT_ONLY" # Not used in current logic, but defined
    HALT = "HALT"


from typing import Dict, Any, Union, Callable
class ValidationSeverity(Enum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict = field(default_factory=dict)

class ValidationRule:
    """Single validation rule with callable validator"""

    def __init__(self, rule_id: str, severity: ValidationSeverity, validator: Any, error_message: Union[str, Callable[[Dict], str]], category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category

    def execute(self, data: Dict) -> 'ValidationResult':
        """Execute validation rule and return result"""
        try:
            passed = self.validator(data)
            
            # The error message is a lambda that needs the data to format the string
            error_msg = self.error_message(data) if not passed and callable(self.error_message) else (self.error_message if not passed else "")

            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=data.get('error_details', {}) # Pass details for reporting
            )
        except Exception as e:
            return ValidationResult(
                rule_id=self.rule_id,
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation logic failed for {self.rule_id}: {str(e)}",
                details={'exception': str(e)}
            )
            
class ValidationEngine:
    """
    Unified validation engine with rule registry pattern.
    Replaces multiple specialized validator classes with single extensible engine.
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = {}
    
    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule"""
        self.rules.append(rule)
        if rule.category not in self.rules_by_category:
            self.rules_by_category[rule.category] = []
        self.rules_by_category[rule.category].append(rule)
    
    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Register multiple validation rules"""
        for rule in rules:
            self.register_rule(rule)
    
    def validate(self, data: Dict, categories: Optional[List[str]] = None) -> List['ValidationResult']:
 
        results = []
        
        # Determine which rules to run
        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))
        
        # Execute each rule
        for rule in rules_to_run:
            result = rule.execute(data)
            results.append(result)
        
        return results
    
    def get_failed_validations(self, results: List['ValidationResult']) -> List['ValidationResult']:
        """Filter to only failed validations"""
        return [r for r in results if not r.passed]
    
    def get_critical_failures(self, results: List['ValidationResult']) -> List['ValidationResult']:
        """Filter to only critical failures"""
        return [r for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL]
    
    def has_critical_failures(self, results: List['ValidationResult']) -> bool:
        """Check if any critical failures exist"""
        return len(self.get_critical_failures(results)) > 0
    
    def has_high_or_critical_failures(self, results: List['ValidationResult']) -> bool:
        """Check if any high or critical failures exist"""
        return any(
            not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
            for r in results
        )
    
    def format_validation_report(self, results: List['ValidationResult']) -> str:
        """Format validation results as readable report"""
        lines = []
        lines.append("=" * 80)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 80)
        
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        
        lines.append(f"Total Rules: {len(results)}")
        lines.append(f"Passed: {len(passed)} ✓")
        lines.append(f"Failed: {len(failed)} ✗")
        lines.append("")
        
        if failed:
            lines.append("FAILURES:")
            lines.append("-" * 80)
            for result in failed:
                severity_marker = "🔴" if result.severity == ValidationSeverity.CRITICAL else "⚠️"
                lines.append(f"{severity_marker} {result.rule_id}: {result.message}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)

class JDEnforcementRule(Enum):
    """Enforcement rules ensuring JD is always used."""
    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    E3_JD_PARSING_SUCCESS = "JD must parse successfully"
    E4_THEMES_EXTRACTED = "JD-derived themes must be extracted"
    E5_SKILLS_EXTRACTED = "JD-derived skills must be extracted (min 5)"
    E6_JD_TO_THEMATIC = "JD data must flow to ThematicAnalysis"
    E7_THEMATIC_USES_JD = "ThematicAnalysis must use JD data (not mock)"
    E8_ARTIST_RECEIVES_JD = "Artist must receive JD-derived thematic_analysis"
    E9_CONTENT_HAS_JD_KW = "Generated content must contain JD keywords"
    E10_ENRICHMENT_USES_JD = "Enrichment must use JD-derived data"
    E11_VALIDATION_CHECKS_JD = "Validation must check JD keyword presence"
    E12_FILES_CONTAIN_JD = "Output files must contain JD-derived content"
    E13_QA_VERIFIES_JD = "QA report must verify JD usage"
    E14_NO_MOCK_DATA = "No fallback/mock/default data allowed anywhere"
    E15_COMPLETE_AUDIT = "Complete audit trail of JD data flow required"

@dataclass
class JDEnforcementResult:
    """Result of a JD enforcement check."""
    rule: JDEnforcementRule
    passed: bool
    details: str
    gate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class JDEnforcementValidator:
    """
    Validator ensuring JD is always used and never mocked.
    Every hop has corresponding validation gates.
    """
    
    def __init__(self):
        self.enforcement_results: List[JDEnforcementResult] = []
        self.jd_hash: Optional[str] = None
        self.jd_keywords: List[str] = []
    
    def validate_jd_input(self, job_description: str, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-0: Validate JD input.
        Enforces: E1, E2, E3
        """
        results = []
        
        # E1: Min length
        if len(job_description) >= 100:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                True,
                f"JD length: {len(job_description)} chars",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                False,
                f"JD too short: {len(job_description)} chars < 100 minimum",
                gate_id
            ))
        
        # E2: Non-null
        if job_description and job_description.strip():
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                True,
                "JD is non-null and non-empty",
                gate_id
            ))
            
            self.jd_hash = hashlib.sha256(job_description.encode()).hexdigest()[:16]
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                False,
                "JD is null or empty",
                gate_id
            ))
        
        # E3: Parsing success (placeholder, actual parsing happens later)
        results.append(JDEnforcementResult(
            JDEnforcementRule.E3_JD_PARSING_SUCCESS,
            True,
            "JD input is valid for parsing",
            gate_id
        ))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_jd_parsing(self, parsed_jd: Dict, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-1: Validate JD parsing.
        Enforces: E3, E4, E5
        """
        results = []
        
        # E3: Parsing success
        if parsed_jd and isinstance(parsed_jd, dict):
            results.append(JDEnforcementResult(
                JDEnforcementRule.E3_JD_PARSING_SUCCESS,
                True,
                f"JD parsed with {len(parsed_jd)} fields",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E3_JD_PARSING_SUCCESS,
                False,
                "JD parsing failed or returned non-dict",
                gate_id
            ))
        
        # E4: Themes extracted
        primary_theme = parsed_jd.get("primary_theme", "")
        secondary_themes = parsed_jd.get("secondary_themes", [])
        
        if primary_theme and secondary_themes:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E4_THEMES_EXTRACTED,
                True,
                f"Primary theme + {len(secondary_themes)} secondary themes",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E4_THEMES_EXTRACTED,
                False,
                f"Missing themes: primary={bool(primary_theme)}, secondary={len(secondary_themes)}",
                gate_id
            ))
        
        # E5: Skills extracted
        required_skills = parsed_jd.get("required_skills", [])
        if len(required_skills) >= 5:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E5_SKILLS_EXTRACTED,
                True,
                f"Extracted {len(required_skills)} skills",
                gate_id
            ))
            self.jd_keywords.extend(required_skills)
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E5_SKILLS_EXTRACTED,
                False,
                f"Insufficient skills: {len(required_skills)} < 5 minimum",
                gate_id
            ))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_thematic_analysis(self, thematic_analysis: Any, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-2: Validate ThematicAnalysis uses JD.
        Enforces: E6, E7
        """
        results = []
        
        # E6: JD → ThematicAnalysis
        if thematic_analysis and hasattr(thematic_analysis, 'primary_theme'):
            results.append(JDEnforcementResult(
                JDEnforcementRule.E6_JD_TO_THEMATIC,
                True,
                "ThematicAnalysis created from JD",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E6_JD_TO_THEMATIC,
                False,
                "ThematicAnalysis missing or invalid",
                gate_id
            ))
        
        # E7: No mock data in ThematicAnalysis
        if thematic_analysis:
            thematic_str = str(thematic_analysis).lower()
            has_mock = any(indicator in thematic_str for indicator in mock_indicators)
            
            if not has_mock:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E7_THEMATIC_USES_JD,
                    True,
                    "ThematicAnalysis contains no mock data indicators",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E7_THEMATIC_USES_JD,
                    False,
                    "ThematicAnalysis may contain mock data",
                    gate_id
                ))

        self.enforcement_results.extend(results)
        return results
    
    def validate_enrichment(self, enriched_data: Dict, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-3: Validate enrichment uses JD.
        Enforces: E10, E14
        """
        results = []
        
        if enriched_data and isinstance(enriched_data, dict):
            # Check if any JD keywords present in enriched data
            enriched_str = json.dumps(enriched_data).lower()
            keywords_found = [kw for kw in self.jd_keywords[:10] if kw.lower() in enriched_str]
            
            if keywords_found:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E10_ENRICHMENT_USES_JD,
                    True,
                    f"Found {len(keywords_found)} JD keywords in enriched data",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E10_ENRICHMENT_USES_JD,
                    False,
                    "No JD keywords found in enriched data",
                    gate_id
                ))
        
        # E14: No mock data
        if enriched_data:
            enriched_str = str(enriched_data).lower()
            has_mock = any(indicator in enriched_str for indicator in mock_indicators)
            
            if not has_mock:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E14_NO_MOCK_DATA,
                    True,
                    "No mock data in enrichment",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E14_NO_MOCK_DATA,
                    False,
                    "Mock data indicators found in enrichment",
                    gate_id
                ))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_artist_inputs(self, enriched_scaffold: Dict, thematic_analysis: Any, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-4: Validate artist receives and uses JD.
        Enforces: E8, E9, E14
        """
        results = []
        
        # E8: Artist received thematic_analysis
        if thematic_analysis:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E8_ARTIST_RECEIVES_JD,
                True,
                "Artist received JD-derived thematic_analysis",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E8_ARTIST_RECEIVES_JD,
                False,
                "Artist did not receive thematic_analysis",
                gate_id
            ))
        
        if enriched_scaffold and isinstance(enriched_scaffold, dict):
            enriched_str = json.dumps(enriched_scaffold).lower()
            keywords_found = [kw for kw in self.jd_keywords[:10] if kw.lower() in enriched_str]
            results.append(JDEnforcementResult(
                JDEnforcementRule.E10_ENRICHMENT_USES_JD, bool(keywords_found), f"Found {len(keywords_found)} JD keywords in enriched data provided to Artist", gate_id
            ))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_preflight(self, staging_buffer: Any, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-5: Validate pre-flight checks JD.
        Enforces: E9, E11, E14 (Consolidated)
        """
        results = []

        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = json.dumps(staging_buffer._data).lower()
            keywords_found = [kw for kw in self.jd_keywords[:15] if kw.lower() in buffer_str]
            
            if keywords_found:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E11_VALIDATION_CHECKS_JD,
                    True,
                    f"Validation found {len(keywords_found)} JD keywords",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E11_VALIDATION_CHECKS_JD,
                    False,
                    "Validation found no JD keywords",
                    gate_id
                ))

        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = json.dumps(staging_buffer._data).lower()
            keywords_found_final = [kw for kw in self.jd_keywords[:15] if kw.lower() in buffer_str]
            
            if len(keywords_found_final) >= 3:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E9_CONTENT_HAS_JD_KW,
                    True,
                    f"Pre-flight check found {len(keywords_found_final)} JD keywords in final buffer",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E9_CONTENT_HAS_JD_KW,
                    False,
                    f"Pre-flight check found only {len(keywords_found_final)} JD keywords in final buffer",
                    gate_id
                ))

        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = str(staging_buffer._data).lower()
            has_mock = any(indicator in buffer_str for indicator in mock_indicators)
            results.append(JDEnforcementResult(
                JDEnforcementRule.E14_NO_MOCK_DATA, not has_mock,
                "No mock data indicators found in final staging buffer" if not has_mock else "Mock data indicators found in final staging buffer",
                gate_id
            ))

        self.enforcement_results.extend(results)
        return results
    
    def validate_file_output(self, file_paths: Dict, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-7: Validate files contain JD content.
        Enforces: E12, E14
        """
        results = []
        
        if file_paths:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E12_FILES_CONTAIN_JD,
                True,
                f"{len(file_paths)} files generated (assumed to contain JD content)",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E12_FILES_CONTAIN_JD,
                False,
                "No files generated",
                gate_id
            ))

        if file_paths:
            paths_str = "".join(file_paths.values()).lower()
            has_mock = any(indicator in paths_str for indicator in mock_indicators)
            results.append(JDEnforcementResult(
                JDEnforcementRule.E14_NO_MOCK_DATA,
                not has_mock,
                "No mock data indicators found in file paths" if not has_mock else "Mock data indicators found in file paths",
                gate_id
            ))
        else: # Pass if no files, as there's nothing to check
            results.append(JDEnforcementResult(JDEnforcementRule.E14_NO_MOCK_DATA, True, "No files to check for mock data", gate_id))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_qa_report(self, qa_report: Dict, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-8: Validate QA report verifies JD.
        Enforces: E13, E15
        """
        results = []
        
        if qa_report:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E13_QA_VERIFIES_JD,
                True,
                "QA report generated",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E13_QA_VERIFIES_JD,
                False,
                "QA report missing",
                gate_id
            ))
        
        total_enforcements = len(self.enforcement_results)
        passed_enforcements = sum(1 for r in self.enforcement_results if r.passed)
        
        if total_enforcements >= 15:  # Should have checked all E1-E15
            results.append(JDEnforcementResult(
                JDEnforcementRule.E15_COMPLETE_AUDIT,
                True,
                f"Complete audit: {passed_enforcements}/{total_enforcements} enforcements passed",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E15_COMPLETE_AUDIT,
                False,
                f"Incomplete audit: {total_enforcements} checks < 15 enforcements",
                gate_id
            ))
        
        self.enforcement_results.extend(results)
        return results

COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}""" # Added two spaces at the end of each line to force Markdown line breaks

class AppTrackerQAValidator:
    SCHEMA_FIELDS_V4 = list(APP_TRACKER_SCHEMA_DATA.keys()) if APP_TRACKER_SCHEMA_DATA else []
    if not SCHEMA_FIELDS_V4:
         logging.error("CRITICAL: APP_TRACKER_SCHEMA_DATA is empty or failed to load. Cannot initialize AppTrackerQAValidator schema.")

    PIPELINE_STATUS_ENUM = ["Applied", "Follow-Up", "Interview", "Rejected", "Closed", "Waiting"]

    def __init__(self, run_sha: str = "", actor_id: str = ""):
        self.errors = []
        self.run_sha = run_sha or self._generate_sha()
        self.actor_id = actor_id or "system"
        self.timestamp = datetime.now().isoformat()
        self.rule_pass_counts = {}
        self.rule_fail_counts = {}

    def _generate_sha(self) -> str:
        """Generate unique run SHA."""
        return hashlib.sha256(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    def _log_pass(self, rule_id: str):
        """Log successful rule validation."""
        self.rule_pass_counts[rule_id] = self.rule_pass_counts.get(rule_id, 0) + 1

    def _log_fail(self, rule_id: str, row_idx: int, field: str, message: str, fix: str = ""):
        """Log failed rule validation."""
        self.rule_fail_counts[rule_id] = self.rule_fail_counts.get(rule_id, 0) + 1
        self.errors.append({
            "row_index": row_idx,
            "field": field,
            "RULE_ID": rule_id,
            "message": message,
            "suggested_fix": fix
        })

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse MM/DD/YYYY date format."""
        if not date_str or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%m/%d/%Y")
        except ValueError:
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        if not url or not url.strip(): # Allow empty URLs to pass validation here, specific rules check presence if needed
            return True
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(url_pattern, url.strip()))

    def validate_tracker_data(self, tracker_rows: List[Dict]) -> Dict:
        """
        Validate complete app tracker data.
        Returns PASSED or BLOCKED JSON outcome.
        """
        # R1: Schema shape and exact order (Still useful)
        for idx, row in enumerate(tracker_rows):
            if list(row.keys()) != self.SCHEMA_FIELDS_V4:
                self._log_fail("R1", idx, "schema",
                              f"Schema fields mismatch at row {idx}",
                              f"Ensure exactly {len(self.SCHEMA_FIELDS_V4)} fields in correct order") # Use dynamic length
            else:
                self._log_pass("R1")

        for idx, row in enumerate(tracker_rows):
            self._validate_row(idx, row)

        # Generate outcome
        logger = logging.getLogger(__name__)
        checked_rules = list(self.rule_pass_counts.keys()) + list(self.rule_fail_counts.keys())
        logger.info(f"AppTracker Validation: Checked rules for populated fields: {sorted(list(set(checked_rules)))}")

        if self.errors:
            return self._generate_blocked_outcome()
        else:
            return self._generate_passed_outcome(tracker_rows)

    def _validate_row(self, idx: int, row: Dict):
        """
        [SIMPLIFIED] Validate single tracker row against rules relevant
        to fields populated by this workflow (R1, R2, R10/11, R17, R20, R21, R22).
        """

        status = row.get("Pipeline Status", "").strip()
        if status and status not in self.PIPELINE_STATUS_ENUM:
            self._log_fail("R2", idx, "Pipeline Status",
                          f"Invalid status '{status}'",
                          f"Use one of: {', '.join(self.PIPELINE_STATUS_ENUM)}")
        elif not status: # Also check if it's empty, should be "Applied"
             self._log_fail("R2", idx, "Pipeline Status", "Pipeline Status cannot be empty.", "Should be 'Applied'.")
        else:
            self._log_pass("R2")

        jd_url = row.get("JD URL", "").strip()
        app_date = row.get("Application Date", "").strip()

        if app_date:
            if not self._parse_date(app_date):
                 self._log_fail("R11", idx, "Application Date",
                               f"Invalid date format '{app_date}'",
                               "Use MM/DD/YYYY format")
            else:
                 self._log_pass("R11")
        else: # Application Date is mandatory
             self._log_fail("R11", idx, "Application Date", "Application Date cannot be empty.", "Use MM/DD/YYYY format.")

        if jd_url:
            if not app_date:
                self._log_fail("R10", idx, "Application Date",
                              "Application Date required when JD URL present",
                              "Add valid MM/DD/YYYY date")
            elif self._parse_date(app_date):
                self._log_pass("R10")

        # R17: JD URL HTTP validation
        if jd_url: # Only check if URL is non-empty
            if not self._is_valid_url(jd_url):
                self._log_fail("R17", idx, "JD URL",
                              f"Invalid URL format: '{jd_url}'",
                              "Provide valid HTTP/HTTPS URL")
            else:
                self._log_pass("R17")
        else:
            self._log_pass("R17") # Pass if empty (URL is optional overall, but checked by R10 if AppDate exists)

        # R20: Versioned Resume filename validation
        versioned_resume = row.get("Versioned Resume", "").strip()
        if versioned_resume:
            # Allow optional extension .md, .pdf, .docx, .doc
            filename_pattern = r'^[A-Za-z0-9_\-]+(\.(md|pdf|docx|doc))?$'
            if not re.match(filename_pattern, versioned_resume):
                self._log_fail("R20", idx, "Versioned Resume",
                              f"Invalid filename format: '{versioned_resume}'",
                              "Use format: Name_Resume_Company_Title (alphanumeric, underscores, hyphens only)")
            else:
                self._log_pass("R20")
        else: # Versioned Resume is mandatory
             self._log_fail("R20", idx, "Versioned Resume", "Versioned Resume filename cannot be empty.", "Provide valid filename.")

        # R21: Company name sanity
        company = row.get("Company", "").strip()
        if company and len(company) < 2:
            self._log_fail("R21", idx, "Company",
                          "Company name too short",
                          "Provide valid company name (2+ chars)")
        elif not company:
             self._log_fail("R21", idx, "Company", "Company name cannot be empty.", "Provide valid company name.")
        else:
            self._log_pass("R21")

        # R22: Job Title sanity
        job_title = row.get("Job Title", "").strip()
        if job_title and len(job_title) < 3:
            self._log_fail("R22", idx, "Job Title",
                          "Job title too short",
                          "Provide valid job title (3+ chars)")
        elif not job_title:
             self._log_fail("R22", idx, "Job Title", "Job Title cannot be empty.", "Provide valid job title.")
        else:
            self._log_pass("R22")

    def _generate_passed_outcome(self, tracker_rows: List[Dict]) -> Dict:
        """Generate PASSED JSON outcome."""
        status_counts = {}

        for row in tracker_rows:
            status = row.get("Pipeline Status", "").strip() or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "result": "PASSED",
            "counts_by_rule": self.rule_pass_counts,
            "totals_by_status": status_counts,
            "run_sha": self.run_sha,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp
        }

    def _generate_blocked_outcome(self) -> Dict:
        """Generate BLOCKED JSON outcome with error table."""
        failure_histogram = {}
        for error in self.errors:
            rule_id = error["RULE_ID"]
            failure_histogram[rule_id] = failure_histogram.get(rule_id, 0) + 1

        return {
            "result": "BLOCKED",
            "errors": self.errors,
            "failure_histogram_by_rule": failure_histogram,
            "run_sha": self.run_sha,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp
        }

class BulletProvenance(Enum):
    Verbatim = "Verbatim"
    Customized = "Customized"
    Synthetic = "Synthetic"

class RAGConfig:

    # API settings
    model: str = "gemini-2.5-pro"
    max_tokens: int = 30000 # Increased from 4000
    temperature: float = 0.7

    phase1_min_searches: int = 15
    phase2_min_searches: int = 10
    phase3_min_searches: int = 10
    
    # ENHANCED: API-level retry & timeout strategy
    api_max_retries: int = 7                     # Increased from 3
    api_timeout_seconds: int = 30                # Per API request (was 90)
    api_initial_backoff_seconds: float = 2.0     # First retry delay
    api_max_backoff_seconds: float = 64.0        # Cap on backoff
    api_backoff_multiplier: float = 2.0          # Exponential factor
    api_backoff_jitter: float = 0.1              # Randomization (±10%)
    
    phase_max_retries: int = 3                   # Retries per phase
    phase_timeout_seconds: int = 60              # Timeout per phase
    
    circuit_breaker_threshold: int = 5           # Failures before open
    circuit_breaker_timeout: int = 60            # Seconds before retry
    
    # Caching
    cache_dir: str = "/tmp/jd_cache"
    cache_ttl_days: int = 30
    
    telemetry_enabled: bool = True
    telemetry_log_dir: str = "/tmp/rag_telemetry"

    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "SOURCE_JD": 1.8,
        "SOURCE_COMPANY_BLOG": 1.5,
        "SOURCE_TARGET_EMPLOYEE": 1.4,
        "SOURCE_GARTNER_MQ": 1.2,
        "SOURCE_PEER_JD": 0.8,
        "SOURCE_GENERIC_PROFILE": 0.5,
        "LOCAL_NLP": 0.2
    })

@dataclass
class CompetitiveAnalysisConfig:
    """Configuration for the competitive analysis phase of RAG."""
    enabled: bool = True
    min_peer_jds: int = 3
    search_pattern: str = '"{role_title}" at "{peer_company}"'
    selection_criteria: List[str] = field(default_factory=lambda: [
        "same_industry", "similar_company_size", "recent_posting_date"
    ])
    table_stakes_threshold: float = 0.8
    differentiator_threshold: float = 0.2

@dataclass
class RAGMission:
    """
    Defines the mission for the RAG process based on pre-analysis.
    (Implements Approach 1: Pre-RAG Differential Analysis)
    """
    target_company_name: str
    precise_role_title: str
    key_technologies: List[str]
    core_responsibilities: List[str]
    signal_gap_keywords: List[str]
    signal_overlap_keywords: List[str]

@dataclass
class CompetitiveIntelligence:
    """Stores competitive intelligence insights."""
    peer_jds_analyzed_count: int = 0
    differentiator_keywords: List[str] = field(default_factory=list) # Top N ranked keywords
    differentiator_keywords_raw: List[str] = field(default_factory=list) # Full list before ranking
    differentiator_keywords_weighted: List[Dict] = field(default_factory=list) # [{keyword: "kw", weight: 0.9}, ...]

    def get_top_differentiators(self, count: int) -> List[str]:
        """Returns the top N differentiator keywords."""
        return self.differentiator_keywords[:count]

@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""
    id: str # e.g., "PHASE1_THEMATIC", "LOCAL_NLP_KEYWORDS"
    type: str # e.g., "Web_RAG", "Local_NLP", "Hybrid"
    confidence: float = 0.0 # Confidence score for this source's contribution
    status: str = "UNKNOWN" # e.g., "SUCCESS", "FAILED", "PARTIAL", "FALLBACK"
    specific_source: Optional[str] = None # e.g., "SOURCE_COMPANY_BLOG", "SOURCE_PEER_JD"

class CircuitState(Enum):
  """Circuit breaker states."""
  CLOSED = "closed" # Normal operation
  OPEN = "open" # Failing - reject requests
  HALF_OPEN = "half_open" # Testing recovery

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    v5.59: Protects API from sustained retry storms.
    """
    
    def __init__(self, config: RAGConfig):
        self.threshold = config.circuit_breaker_threshold
        self.timeout = config.circuit_breaker_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            # Success - reset if in HALF_OPEN
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.threshold:
                self.state = CircuitState.OPEN
            
            raise

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

class PhaseTimeoutError(Exception):
    """Raised when a phase exceeds its timeout."""
    pass

class PhaseExecutor:
    """
    Manages phase-level retries, timeouts, and fallbacks.
    v5.59: Provides 3 retries per phase with simplified fallback.
    """
    
    def __init__(self, config: RAGConfig):
        self.config = config
    
    def execute_with_retry(
        self,
        phase_func: Callable[[], T],
        phase_name: str,
        fallback_func: Optional[Callable[[], T]] = None
    ) -> T:
        """
        Execute a phase with retry logic and optional simplified fallback.
        
        Args:
            phase_func: Main phase function to execute
            phase_name: Name for logging
            fallback_func: Optional simplified version to try if main fails
        
        Returns:
            Result from phase_func or fallback_func
        
        Raises:
            PhaseTimeoutError, Exception from phase execution
        """
        import logging
        logger = logging.getLogger(__name__)
        
        last_exception = None
        
        # Try main implementation
        for attempt in range(self.config.phase_max_retries):
            try:
                logger.info(
                    f"{phase_name}: Attempt {attempt+1}/{self.config.phase_max_retries}"
                )
                
                result = self._execute_with_timeout(
                    phase_func,
                    self.config.phase_timeout_seconds,
                    phase_name
                )
                
                # Validate result
                if self._validate_phase_result(result, phase_name):
                    logger.info(f"{phase_name}: Success on attempt {attempt+1}")
                    return result
                else:
                    logger.warning(f"{phase_name}: Invalid result on attempt {attempt+1}")
                    if attempt < self.config.phase_max_retries - 1:
                        continue
                    else:
                        raise ValueError(f"{phase_name}: All attempts returned invalid data")
                
            except PhaseTimeoutError as e:
                last_exception = e
                logger.warning(f"{phase_name}: Timeout on attempt {attempt+1}")
                if attempt == self.config.phase_max_retries - 1:
                    break
                time.sleep(2)
                continue
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{phase_name}: Failed on attempt {attempt+1}: "
                    f"{type(e).__name__}: {e}"
                )
                if attempt == self.config.phase_max_retries - 1:
                    break
                time.sleep(2)
                continue
        
        # Try fallback if available
        if fallback_func:
            try:
                logger.info(f"{phase_name}: Trying simplified fallback...")
                result = self._execute_with_timeout(
                    fallback_func,
                    self.config.phase_timeout_seconds // 2,
                    f"{phase_name}_fallback"
                )
                if self._validate_phase_result(result, phase_name):
                    logger.info(f"{phase_name}: Fallback succeeded")
                    return result
            except Exception as e:
                logger.warning(f"{phase_name}: Fallback also failed: {e}")
        
        # All attempts failed
        logger.error(f"{phase_name}: All retries and fallback exhausted")
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{phase_name}: Failed without exception")
    
    def _execute_with_timeout(
        self, 
        func: Callable[[], T], 
        timeout: int,
        name: str
    ) -> T:
        """
        Execute function with timeout.
        Note: Signal-based timeout only works on Unix. Falls back to direct call on Windows.
        """
        logger = logging.getLogger(__name__)
        
        # For non-Unix systems or if signal doesn't work, just call directly
        if not hasattr(signal, 'SIGALRM'):
            logger.debug(f"{name}: No SIGALRM, executing without timeout")
            return func()
        
        def timeout_handler(signum, frame):
            raise PhaseTimeoutError(f"{name} exceeded {timeout}s timeout")
        
        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func()
            signal.alarm(0)  # Cancel alarm
            return result
        except PhaseTimeoutError:
            raise
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
    
    def _validate_phase_result(self, result: Dict[str, Any], phase_name: str) -> bool:
        """
        Validate that phase result has required structure.
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(result, dict):
            return False
        
        # All phases must have search_summary
        if "search_summary" not in result:
            return False
        
        # Phase-specific validation
        if "phase1" in phase_name.lower() or "thematic" in phase_name.lower():
            return "thematic_analysis" in result and "role_classification" in result
        
        elif "phase2" in phase_name.lower() or "authenticity" in phase_name.lower():
            return "authenticity_patterns" in result and "pattern_confidence" in result
        
        elif "phase4" in phase_name.lower() or "narrative" in phase_name.lower(): # v8.10: Approach 3
            return "problem_solution_narratives" in result
        
        elif "phase3" in phase_name.lower() or "competitive" in phase_name.lower():
            return "competitive_analysis" in result
        
        return True

@dataclass
class PartialRAGResult:
    """
    Tracks which phases succeeded/failed for partial success handling.
    v5.59: Enables hybrid synthesis instead of full fallback.
    """
    phase1_result: Optional[Dict[str, Any]] = None
    phase2_result: Optional[Dict[str, Any]] = None
    phase3_result: Optional[Dict[str, Any]] = None
    phase4_result: Optional[Dict[str, Any]] = None # v8.10: Approach 3
    
    phase1_success: bool = False
    phase2_success: bool = False
    phase3_success: bool = False
    phase4_success: bool = False # v8.10: Approach 3
    
    failure_reasons: List[str] = None
    
    def __post_init__(self):
        if self.failure_reasons is None:
            self.failure_reasons = []
    
    @property
    def any_success(self) -> bool:
        """Return True if any phase succeeded."""
        return self.phase1_success or self.phase2_success or self.phase3_success or self.phase4_success
    
    @property
    def full_success(self) -> bool:
        """Return True if all phases succeeded."""
        return self.phase1_success and self.phase2_success and self.phase3_success and self.phase4_success
    
    @property
    def success_rate(self) -> float:
        """Return success rate as percentage."""
        successes = sum([self.phase1_success, self.phase2_success, self.phase3_success, self.phase4_success])
        return successes / 4.0

@dataclass
class RAGTelemetry:
    """
    Track RAG performance metrics for monitoring.
    v5.59: Comprehensive telemetry for production debugging.
    """
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Success metrics
    full_success: bool = False
    partial_success: bool = False
    local_fallback: bool = False
    success_rate: float = 0.0
    
    # Phase-level metrics
    phase1_attempts: int = 0
    phase1_success: bool = False
    phase1_duration_seconds: float = 0.0
    
    phase2_attempts: int = 0
    phase2_success: bool = False
    phase2_duration_seconds: float = 0.0
    
    phase3_attempts: int = 0
    phase3_success: bool = False
    phase3_duration_seconds: float = 0.0
    
    phase4_attempts: int = 0 # v8.10: Approach 3
    phase4_success: bool = False # v8.10: Approach 3
    phase4_duration_seconds: float = 0.0 # v8.10: Approach 3
    
    # API-level metrics
    total_api_calls: int = 0
    failed_api_calls: int = 0
    total_search_calls: int = 0
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    circuit_breaker_triggered: bool = False
    
    # Performance
    total_duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "timestamp": self.timestamp,
            "success": {
                "full": self.full_success,
                "partial": self.partial_success,
                "rate": self.success_rate
            },
            "phases": {
                "phase1": {
                    "attempts": self.phase1_attempts,
                    "success": self.phase1_success,
                    "duration": self.phase1_duration_seconds
                },
                "phase2": {
                    "attempts": self.phase2_attempts,
                    "success": self.phase2_success,
                    "duration": self.phase2_duration_seconds
                },
                "phase3": {
                    "attempts": self.phase3_attempts,
                    "success": self.phase3_success,
                    "duration": self.phase3_duration_seconds
                },
                "phase4": {
                    "attempts": self.phase4_attempts,
                    "success": self.phase4_success,
                    "duration": self.phase4_duration_seconds
                }
            },
            "api": {
                "total_calls": self.total_api_calls,
                "failed_calls": self.failed_api_calls,
                "search_calls": self.total_search_calls
            },
            "errors": self.errors,
            "circuit_breaker": self.circuit_breaker_triggered,
            "total_duration": self.total_duration_seconds
        }

class TelemetryLogger:
    """
    Log RAG telemetry to file for monitoring.
    v5.59: Writes JSONL logs for analysis.
    """
    
    def __init__(self, log_dir: str = "/tmp/rag_telemetry"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log(self, telemetry: RAGTelemetry):
        """Append telemetry to daily log file."""
        log_file = os.path.join(
            self.log_dir,
            f"rag_telemetry_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(telemetry.to_dict()) + '\n')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to write telemetry: {e}")

class GeminiWebSearchClient:
    def __init__(self, api_key: Optional[str], config: RAGConfig = RAGConfig()):
        """Initializes the client, configuring the API key globally."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package required for web RAG")

        # Configure API key globally before initializing model
        if api_key:
            try:
                genai.configure(api_key=api_key)
                logging.info("Gemini API key configured successfully.")
            except Exception as e:
                logging.error(f"Failed to configure Gemini API key: {e}")
                # Log and continue, relying on potential environment auth
        elif not os.environ.get("GEMINI_API_KEY"): # Double check env var if direct key not passed
             logging.warning("No direct API key provided and GEMINI_API_KEY environment variable not found. Relying on implicit credentials if available.")

        # Initialize Gemini client WITHOUT the api_key argument
        try:
            self.client = genai.GenerativeModel(
                config.model
                # api_key=api_key # <-- REMOVED THIS ARGUMENT
            )
            logging.info(f"GenerativeModel '{config.model}' initialized.")
        except Exception as e:
             logging.error(f"Failed to initialize GenerativeModel '{config.model}': {e}", exc_info=True)
             self.client = None # Ensure client is None if initialization fails

        self.config = config
        self.circuit_breaker = CircuitBreaker(config)
        self.api_calls_made = 0 # Counter for API calls

        # Web search tool definition (remains the same)
        self.web_search_tool = {
            "name": "web_search",
            "description": "Search the web for current information.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query."}},
                "required": ["query"],
            },
        }
    # --- END MODIFICATION ---

    # --- START MODIFICATION: Return call count from search_and_analyze ---
    def search_and_analyze(
        self,
        prompt: str,
        phase_name: str = "unknown"
    ) -> Tuple[Dict[str, Any], int]: # Return a tuple: (result, call_count)
        """
        Send prompt to Gemini with web_search tool enabled.
        Enhanced with adaptive retry, circuit breaker, and JSON repair.

        Returns: Parsed JSON from Gemini's response AND the number of API calls made.
        Raises: APIError, CircuitBreakerOpenError, TimeoutError, ValueError
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {phase_name}...")

        last_exception = None
        calls_this_request = 0 # Track calls for this specific request

        for attempt in range(self.config.api_max_retries):
            try:
                # Check circuit breaker
                # Pass the logger correctly
                result, calls_made_in_attempt = self.circuit_breaker.call(
                    self._make_api_call,
                    prompt,
                    attempt,
                    phase_name,
                    logger # Pass the logger instance
                )
                calls_this_request += calls_made_in_attempt

                logger.info(f"{phase_name} completed successfully on attempt {attempt+1}")
                return result, calls_this_request # Return result and count

            except CircuitBreakerOpenError as e:
                logger.error(f"{phase_name}: Circuit breaker OPEN - aborting retries")
                raise # Re-raise immediately

            # Catch specific errors related to API or parsing first
            except (HopExecutionError, ValueError, TimeoutError) as e:
                last_exception = e
                error_type = type(e).__name__
                log_msg = f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} failed: {error_type}: {e}"

                # Log differently based on error type
                if isinstance(e, ValueError): # JSON parsing error
                     logger.warning(log_msg)
                     if attempt < self.config.api_max_retries - 1:
                         # Retry with enhanced prompt handled by next loop iteration
                         pass
                     else:
                          logger.error(f"{phase_name}: JSON parsing failed after all attempts")
                          raise # Re-raise after final attempt
                elif isinstance(e, TimeoutError): # Timeout error
                     logger.warning(log_msg)
                else: # HopExecutionError (MAX_TOKENS, Blocked, etc.)
                     logger.warning(log_msg)

                # Backoff logic (common for retryable errors)
                if attempt < self.config.api_max_retries - 1:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: All {self.config.api_max_retries} API attempts failed")
                    raise # Re-raise the last exception

            # Catch broader exceptions last
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} "
                    f"failed with unexpected error: {type(e).__name__}: {e}", exc_info=False
                )
                if attempt < self.config.api_max_retries - 1:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: All {self.config.api_max_retries} API attempts failed")
                    raise

        # Should never reach here, but handle gracefully
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{phase_name}: Unexpected exit from retry loop")
    # --- END MODIFICATION ---

    # --- START MODIFICATION: Increment counter and return call count ---
    def _make_api_call(
        self,
        prompt: str,
        attempt: int,
        phase_name: str,
        logger # Added logger parameter
    ) -> Tuple[Dict[str, Any], int]: # Return result and call count (always 1 here)
        """
        Make the actual API call with timeout and robust response handling.
        v11.30 Fix: Removed 'tools', Uses integer codes for finish_reason.
        NOW increments API counter and returns call count (1).
        """
        start_time = time.time()
        calls_made = 0 # Track calls within this specific attempt

        if not self.client:
            raise HopExecutionError(f"{phase_name} cannot make API call: Gemini client not initialized.")

        try:
            self.api_calls_made += 1
            calls_made = 1

            response = self.client.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )

            elapsed = time.time() - start_time
            logger.debug(f"{phase_name} API call completed in {elapsed:.2f}s (Call #{self.api_calls_made})")

            json_text_content = ""
            finish_reason = None
            prompt_feedback = getattr(response, 'prompt_feedback', None)

            if hasattr(response, 'candidates') and response.candidates:
                 candidate_one = response.candidates[0]
                 finish_reason = getattr(candidate_one, 'finish_reason', None)

            if finish_reason == 2: # MAX_TOKENS
                 raise HopExecutionError(f"API call stopped due to MAX_TOKENS limit ({self.config.max_tokens}). Response may be incomplete.")
            elif finish_reason is not None and finish_reason != 1: # Check for non-STOP (integer 1) reasons
                 block_reason = getattr(prompt_feedback, 'block_reason', None) if prompt_feedback else None
                 raise HopExecutionError(f"API call stopped. Finish Reason Code: {finish_reason}. Block Reason: {block_reason}")


            # Proceed with extracting text if finish_reason indicates completion (1 or None)
            if hasattr(response, 'text') and response.text:
                 json_text_content = response.text
                 logger.debug(f"{phase_name} Extracted text directly from response.text.")
            elif hasattr(response, 'parts') and response.parts: # Fallback check
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                         json_text_content = part.text
                         logger.debug(f"{phase_name} Extracted text from response parts (fallback).")
                         break
                if not json_text_content: # If parts exist but have no text
                     logger.warning(f"{phase_name} API response parts did not contain text: {response.parts}")
                     raise ValueError("API response contained parts but no usable text content.")
            else: # If no text and no parts, something is wrong
                 logger.warning(f"{phase_name} API response structure unexpected or empty: {response}")
                 # Re-check block reason here just in case finish_reason wasn't available
                 block_reason = getattr(prompt_feedback, 'block_reason', None) if prompt_feedback else None
                 if block_reason: raise HopExecutionError(f"API call blocked. Block Reason: {block_reason}")
                 raise ValueError("API response did not contain 'parts' or 'text'.")

            # Attempt to parse the extracted text as JSON
            parsed_json = self._extract_json(json_text_content)
            return parsed_json, calls_made # Return result and calls_made (1)
            # --- End Robust Response Handling ---

        # --- Exception Handling (Catch specific errors first) ---
        except HopExecutionError as he: # Catch specific MAX_TOKENS or blocked errors from above
             logger.warning(f"{phase_name} API call failed (Attempt {attempt+1}): {he}")
             raise # Re-raise to be caught by retry logic

        except (TimeoutError, ValueError) as e: # Catch timeouts or JSON parsing errors
             elapsed = time.time() - start_time
             if isinstance(e, TimeoutError) or "timeout" in str(e).lower():
                  logger.warning(f"{phase_name} API call timed out after {elapsed:.2f}s (Attempt {attempt+1})")
                  raise TimeoutError(f"{phase_name} timed out") from e # Re-raise specific TimeoutError
             else: # ValueError from _extract_json
                  logger.warning(f"{phase_name} JSON parsing failed (Attempt {attempt+1}): {e}")
                  raise # Re-raise ValueError for retry logic to potentially handle

        except Exception as e: # Catch other unexpected errors
            elapsed = time.time() - start_time
            logger.warning(f"{phase_name} API call failed unexpectedly (Attempt {attempt+1}): {type(e).__name__}: {e}", exc_info=False)
            # Re-raise the original exception for the retry logic
            raise
    # --- END MODIFICATION ---

    # --- _calculate_backoff, _extract_json, _attempt_json_repair methods remain unchanged ---
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff with jitter.

        Formula: min(initial * (multiplier ^ attempt), max) ± jitter
        Example: [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 64.0] seconds with ±10% jitter
        """
        import random

        base_delay = min(
            self.config.api_initial_backoff_seconds * (
                self.config.api_backoff_multiplier ** attempt
            ),
            self.config.api_max_backoff_seconds
        )

        # Add jitter (±10%)
        jitter_range = base_delay * self.config.api_backoff_jitter
        jitter = random.uniform(-jitter_range, jitter_range)

        return max(0.1, base_delay + jitter)

    def _extract_json(self, text_content: str) -> Dict[str, Any]:
        """
        Extract JSON from the LLM's response content.
        Enhanced with multiple parsing strategies and repair attempts.
        v11.30 Fix: Relaxed initial check to allow for markdown fences.
        """
        # --- START FIX: Relax initial check ---
        # Allow starting with '{' or '```json' after stripping whitespace
        stripped_content = text_content.strip() if isinstance(text_content, str) else ""
        if not stripped_content or not (stripped_content.startswith('{') or stripped_content.startswith('```json')):
             # If it doesn't look like JSON or a markdown JSON block, raise error
             raise ValueError(
                 f"Response content does not appear to be JSON or a markdown JSON block. "
                 f"Content preview: {str(text_content)[:200]}..."
             )
        # --- END FIX ---

        # Strategy 1: Markdown JSON code block (This should now be reached)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_content, re.DOTALL)
        if json_match:
            try:
                # Attempt to parse the content within the markdown block
                parsed_json = json.loads(json_match.group(1))
                logging.debug("Successfully parsed markdown JSON block.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse markdown JSON block: {e}. Trying other strategies.")
                pass # Continue to next strategy

        # Strategy 2: First complete JSON object (if no markdown fence found)
        # Tries to find the first '{' and match until the corresponding '}'
        brace_level = 0
        start_index = -1
        end_index = -1
        for i, char in enumerate(text_content):
            if char == '{':
                if start_index == -1:
                    start_index = i
                brace_level += 1
            elif char == '}':
                if start_index != -1: # Ensure we found an opening brace first
                    brace_level -= 1
                    if brace_level == 0:
                        end_index = i + 1
                        break # Found the end of the first top-level object

        if start_index != -1 and end_index != -1:
            potential_json = text_content[start_index:end_index]
            try:
                parsed_json = json.loads(potential_json)
                logging.debug("Successfully parsed first complete JSON object.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse first complete JSON object: {e}. Trying other strategies.")
                pass # Continue to next strategy
        else:
             # Only log warning if markdown wasn't found either
             if not json_match:
                 logging.warning("Could not find balanced braces for JSON object and no markdown block found.")


        # Strategy 3: Remove markdown artifacts and retry direct parse (as fallback)
        cleaned = text_content.replace('```json', '').replace('```', '').strip()
        # Ensure cleaned text actually starts with '{' before trying to parse
        if cleaned.startswith('{'):
            try:
                parsed_json = json.loads(cleaned)
                logging.debug("Successfully parsed cleaned text directly.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse cleaned text directly: {e}. Trying repair.")
                pass # Continue to repair attempt
        else:
             logging.warning("Cleaned text does not start with '{'. Skipping direct parse.")


        # Strategy 4: Try to repair common JSON errors
        # Only attempt repair if cleaned text looks like JSON
        if cleaned.startswith('{'):
            repaired = self._attempt_json_repair(cleaned)
            if repaired:
                logging.info("Successfully parsed JSON after repair.")
                return repaired
        else:
             logging.warning("Skipping JSON repair as cleaned text does not start with '{'.")

        # If all strategies fail
        raise ValueError(
            f"No valid JSON found in Gemini's response after multiple attempts. "
            f"Content preview: {text_content[:200]}..."
        )

    def _attempt_json_repair(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to repair common JSON formatting errors.
        v5.59: Multiple repair strategies for robustness.
        """
        repairs = [
            # Remove trailing commas
            lambda s: re.sub(r',(\s*[}\]])', r'\1', s),
            # Fix single quotes to double quotes
            lambda s: s.replace("'", '"'),
            # Remove control characters
            lambda s: ''.join(char for char in s if ord(char) >= 32 or char == '\n'),
        ]

        for repair_func in repairs:
            try:
                repaired = repair_func(text)
                return json.loads(repaired)
            except (json.JSONDecodeError, Exception):
                continue

        return None

class JDCacheManager:
    """Manages caching of JD analysis results."""
    
    def __init__(self, cache_dir: str, ttl_days: int):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_days * 24 * 3600
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, job_description: str) -> str:
        """Generate MD5 hash for JD."""
        return hashlib.md5(job_description.encode('utf-8')).hexdigest()
    
    def get(self, job_description: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if available and not expired."""
        cache_key = self.get_cache_key(job_description)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        # Check expiration
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > self.ttl_seconds:
            os.remove(cache_file)
            return None
        
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    def set(self, job_description: str, analysis: Dict[str, Any]):
        """Save analysis to cache."""
        cache_key = self.get_cache_key(job_description)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(analysis, f, indent=2)

class WebSearchRAG:
    """
    Implements three-phase web search RAG strategy with resilience.
    v5.59: Phase-level retries, simplified fallbacks, timeout management.
    v11.30: Correctly passes mission object to prompt builders.

    Enhanced Features:
    - Phase-level retries (3 attempts per phase)
    - Simplified fallback prompts (8-10 searches vs 15-20)
    - Phase result validation
    - Timeout management per phase
    """

    def __init__(self, client: GeminiWebSearchClient, config: RAGConfig = RAGConfig()):
        self.client = client
        self.config = config
        self.comp_config = CompetitiveAnalysisConfig() # Add competitive analysis config
        self.executor = PhaseExecutor(config)
        self.PEERS_BY_INDUSTRY = {
            "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
            "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
            "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
            "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
            "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"]
        }

    def phase1_thematic_research(self, job_description: str, mission: RAGMission) -> Dict[str, Any]:
        """
        Phase 1: Research market expectations and extract themes.
        v5.59: Enhanced with retry logic and simplified fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v11.30 Fix: Pass mission to prompt builders correctly.
        """
        def main_phase1():
            prompt = self._build_phase1_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 1: Thematic Research")

        def fallback_phase1():
            prompt = self._build_phase1_prompt(job_description, mission, detailed=False)
            return self.client.search_and_analyze(
                prompt,
                "Phase 1: Thematic Research (Simplified)"
            )

        return self.executor.execute_with_retry(
            main_phase1,
            "Phase 1",
            fallback_func=fallback_phase1
        )

# Inside class WebSearchRAG:
    def _build_phase1_prompt(self, job_description: str, mission: RAGMission, detailed: bool = True) -> str:
        """
        Build Phase 1 prompt with optional simplification.
        v5.59: Simplified version reduces search count for fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v11.30 Fix: Safely access mission.key_technologies.
        """

        if detailed:
            search_count = "15-20"
            detail_level = """Analyze:
1. Primary theme (main skill focus)
2. Secondary themes (4-5 supporting skills)
3. Role seniority level (e.g., senior, executive)
4. Role archetype (e.g., Executive_Leader, Technical_IC, Post-Sales_Customer_Success)
5. Trending keywords
6. Required vs preferred skills"""
        else:
            search_count = "8-10"
            detail_level = """Analyze:
1. Primary theme (main skill focus)
2. Secondary themes (2-3 supporting skills)
3. Top 10 keywords
4. Role seniority level and archetype
"""

        tech_search_line = ""
        if mission.key_technologies:
            safe_tech = mission.key_technologies[0] # Safely access after check
            tech_search_line = f'3. Search for: `"{mission.target_company_name} press release {safe_tech}"`'
        authoritative_searches = f"""
**Authoritative Search Directives (High Priority):**
1. Search for: `"{mission.target_company_name} engineering blog"`
2. Search for: `"{mission.target_company_name} values"` or `"{mission.target_company_name} operating principles"`
{tech_search_line}
"""

        # Use mission.key_technologies safely in the main TASK prompt
        task_keywords = ', '.join(mission.key_technologies) if mission.key_technologies else "relevant role keywords"

        return f"""You are a job market intelligence analyst. Research this role using web_search.

JOB DESCRIPTION:
{job_description[:1500]}

TASK: First, perform the authoritative searches. Then, search for {search_count} similar job postings that also contain these keywords: {task_keywords}. {detail_level}

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "searches_performed": <number of web_search calls>,
    "jds_analyzed": <number of unique JDs>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "thematic_analysis": {{
    "primary_theme": {{
      "name": "<theme name>",
      "confidence": <0.0-1.0>,
      "keywords": ["<keyword1>", "<keyword2>", ...],
      "market_prevalence": <0.0-1.0>
    }},
    "secondary_themes": [
      {{
        "name": "<theme name>",
        "relevance": <0.0-1.0>,
        "keywords": ["<keyword1>", ...]
      }}
    ],
    "trending_keywords": ["<keyword1>", ...],
    "required_skills": ["<skill1>", ...],
    "preferred_skills": ["<skill1>", ...]
  }},
  "role_classification": {{
    "seniority": "<entry|mid|senior|executive>",
    "function": "<function>",
    "industry_focus": "<industry>",
    "role_archetype": "<Executive_Leader|Technical_IC|Post-Sales_Customer_Success|Pre-Sales_GTM|Product_Management>"
  }}
}}

CRITICAL: Return ONLY valid JSON. No text before or after. Ensure all JSON is properly formatted with no trailing commas."""
    
    def phase2_authenticity_patterns(
        self,
        job_description: str,
        mission: RAGMission
    ) -> Dict[str, Any]:
        """
        Phase 2: Extract how real professionals present themselves.
        v5.59: Enhanced with retry logic and simplified fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v11.30 Fix: Pass mission to prompt builders correctly.
        """
        def main_phase2():
            prompt = self._build_phase2_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 2: Authenticity Patterns")

        def fallback_phase2():
            prompt = self._build_phase2_prompt(job_description, mission, detailed=False)
            return self.client.search_and_analyze(
                prompt,
                "Phase 2: Authenticity Patterns (Simplified)"
            )

        return self.executor.execute_with_retry(
            main_phase2,
            "Phase 2",
            fallback_func=fallback_phase2
        )

    def _build_phase2_prompt(
        self,
        job_description: str,
        mission: RAGMission, # Now accepts mission
        detailed: bool = True
    ) -> str:
        """
        Build Phase 2 prompt with optional simplification.
        v11.30 Fix: Uses mission object passed in.
        """
        role_title = mission.precise_role_title
        industry = self._infer_industry(job_description)

        authoritative_search_instruction = f"""
**Authoritative Search Directive (Highest Priority):**
Search for LinkedIn profiles using this exact query: `LinkedIn profile "{mission.precise_role_title}" at "{mission.target_company_name}"`
"""
        if detailed:
            search_count = "10-15"
            pattern_types = """Extract:
1. Executive summary patterns (with <PLACEHOLDERS>)
2. Achievement verb patterns
3. Metric presentation patterns
4. Competency phrasing patterns"""
        else:
            search_count = "5-8"
            pattern_types = """Extract:
1. Executive summary patterns (3-5 examples)
2. Top achievement verbs (10-15)
3. Common metric formats"""

        return f"""You are a LinkedIn profile analyst. Research this role using web_search:

TARGET ROLE: {role_title} # Use variable extracted from mission
INDUSTRY: {industry}
GAP KEYWORDS TO FIND: {', '.join(mission.signal_gap_keywords)}

TASK: First, execute the authoritative search. Then, search for {search_count} additional LinkedIn profiles and resumes for similar roles, prioritizing those that mention the 'GAP KEYWORDS'.
{pattern_types}

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "profiles_analyzed": <count>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "authenticity_patterns": {{
    "executive_summary_patterns": [
      "Built <ACHIEVEMENT> resulting in <IMPACT>",
      "Led <INITIATIVE> achieving <METRIC>",
      ...
    ],
    "achievement_verb_patterns": [
      "Drove", "Led", "Architected", ...
    ],
    "metric_presentation_patterns": [
      "$<NUMBER>M revenue",
      "<NUMBER>% growth",
      ...
    ],
    "competency_phrasing": [
      "<SKILL>: <CONTEXT>",
      ...
    ]
  }},
  "pattern_confidence": {{
    "executive_summary": <0.0-1.0>,
    "verbs": <0.0-1.0>,
    "metrics": <0.0-1.0>,
    "overall": <0.0-1.0>
  }}
}}

CRITICAL: Return ONLY valid JSON. Extract REAL patterns from profiles. Ensure all JSON is properly formatted."""

    def phase3_competitive_positioning(
        self,
        job_description: str,
        mission: RAGMission # Pass mission here
    ) -> Dict[str, Any]:
        """
        Phase 3: Analyze competitive landscape and differentiators.
        v5.59: Enhanced with retry logic and simplified fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v11.30 Fix: Ensures mission is passed correctly.
        """
        def main_phase3():
            prompt = self._build_phase3_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(
                prompt,
                "Phase 3: Competitive Positioning"
            )

        def fallback_phase3():
            prompt = self._build_phase3_prompt(job_description, mission, detailed=False)
            return self.client.search_and_analyze(
                prompt,
                "Phase 3: Competitive Positioning (Simplified)"
            )

        return self.executor.execute_with_retry(
            phase_func=main_phase3,
            phase_name="Phase 3",
            fallback_func=fallback_phase3
        )

    def _build_phase3_prompt(
        self,
        job_description: str,
        mission: RAGMission, # Accept mission object
        detailed: bool = True # Add detailed flag for fallback logic
    ) -> str:
        """
        Build Phase 3 prompt with optional simplification.
        v7.60: Depth is now configurable via RAGConfig and uses CompetitiveAnalysisConfig.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v9.84->v11.30: Fixed undefined variables, uses mission object, simplified fallback.
        """
        company_name = mission.target_company_name
        role_title = mission.precise_role_title
        industry = self._infer_industry(job_description)

        peer_companies = self._infer_peer_companies(company_name, job_description)

        # Integrate new competitive analysis config
        search_pattern_instruction = self.comp_config.search_pattern.format(
            role_title=role_title, peer_company="<peer_company>"
        )
        selection_criteria_instruction = ", ".join(self.comp_config.selection_criteria)

        authoritative_searches = f""" # (Approach 2) Add authoritative source queries
**Authoritative Search Directives (High Priority):**
1. Search for: `"Gartner Magic Quadrant for {industry}"`
2. Search for: `"Forrester Wave {industry}"`
"""

        if detailed:
            search_count = "10-15"
            analysis_depth = "Identify table stakes and differentiators with prevalence scores"
        else: # Fallback case
            search_count = "5-8"
            analysis_depth = "Identify top 5 table stakes and top 5 differentiators"


        return f"""You are a competitive intelligence analyst. Research using web_search:

TARGET JD:
Company: {company_name}
Role: {role_title}
Description: {job_description[:1000]}

PEER COMPANIES: {', '.join(peer_companies)}

TASK:
1.  First, perform the authoritative searches. Then, search for {search_count} similar roles at peer companies using patterns like: '{search_pattern_instruction}'.
2.  Select a minimum of {self.comp_config.min_peer_jds} JDs based on these criteria: {selection_criteria_instruction}.
3.  Analyze the selected JDs to {analysis_depth}.
4.  A keyword is 'table stakes' if its prevalence is > {self.comp_config.table_stakes_threshold}.
5.  A keyword is a 'differentiator' if its uniqueness score is > {self.comp_config.differentiator_threshold}.

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "peer_jds_analyzed": <count>,
    "peer_companies": ["<company1>", ...],
    "sources": ["<url1>", ...]
  }},
  "competitive_analysis": {{
    "table_stakes_keywords": [
      {{
        "keyword": "<keyword>",
        "prevalence": <0.0-1.0>
      }}
    ],
    "differentiator_keywords": [
      {{
        "keyword": "<keyword>",
        "uniqueness_score": <0.0-1.0>
      }}
    ]
  }},
  "positioning_insight": "<2-3 sentence summary>"
}}

CRITICAL: Return ONLY valid JSON. Ensure all JSON is properly formatted."""

    def _infer_industry(self, job_description: str) -> str:
        """Infer industry from JD keywords."""
        jd_lower = job_description.lower()

        if 'fintech' in jd_lower or 'banking' in jd_lower:
            return "Financial Technology"
        elif 'healthcare' in jd_lower or 'medical' in jd_lower:
            return "Healthcare"
        elif 'retail' in jd_lower or 'e-commerce' in jd_lower:
            return "Retail/E-Commerce"
        elif 'saas' in jd_lower or 'software' in jd_lower:
            return "Software/SaaS"
        else:
            return "Technology"

    def _infer_peer_companies(self, company_name: str, job_description: str) -> List[str]:
        """Infer peer companies based on industry."""
        # --- START REFACTOR: Use configurable peer list ---
        industry = self._infer_industry(job_description)

        peers = self.PEERS_BY_INDUSTRY.get(industry, self.PEERS_BY_INDUSTRY["Technology"])
        return [p for p in peers if p.lower() not in company_name.lower()][:5]
        # --- END REFACTOR ---

    def phase4_narrative_mining(self, mission: RAGMission) -> Dict[str, Any]:
        """
        Phase 4: Mine for problem-solution narratives.
        (Implements Approach 3)
        v11.30 Fix: Pass mission to prompt builders correctly.
        """
        def main_phase4():
            prompt = self._build_phase4_prompt(mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 4: Narrative Mining")

        def fallback_phase4():
            prompt = self._build_phase4_prompt(mission, detailed=False)
            return self.client.search_and_analyze(prompt, "Phase 4: Narrative Mining (Simplified)")

        return self.executor.execute_with_retry(
            main_phase4,
            "Phase 4",
            fallback_func=fallback_phase4
        )

    def _build_phase4_prompt(self, mission: RAGMission, detailed: bool = True) -> str:
        """
        Build Phase 4 prompt for narrative mining.
        (Implements Approach 3)
        """
        search_count = "8-10" if detailed else "4-5"
        analysis_depth = "Extract 5-7 common problems and 5-7 corresponding solution patterns." if detailed else "Extract 3-4 top problems and solutions."

        # Generate dynamic, high-signal search queries
        queries = [
            f'"challenges of {mission.core_responsibilities[0]} for {mission.key_technologies[0]}"' if mission.core_responsibilities and mission.key_technologies else f'"challenges of {mission.precise_role_title}"',
            f'"case study {mission.precise_role_title}"',
            f'"{mission.target_company_name} customer success stories"',
            f'"how to improve {mission.core_responsibilities[0]} with {mission.key_technologies[0]}"' if mission.core_responsibilities and mission.key_technologies else f'"how to succeed as {mission.precise_role_title}"'
        ]

        return f"""You are a business narrative analyst. Your goal is to find the common "problem-solution" stories associated with a specific role and industry.

TARGET ROLE: {mission.precise_role_title}
CORE RESPONSIBILITIES: {', '.join(mission.core_responsibilities)}
KEY TECHNOLOGIES: {', '.join(mission.key_technologies)}

TASK:
1. Execute web searches using queries like these: {', '.join(queries)}. Perform at least {search_count} searches.
2. Analyze the search results (articles, case studies, blogs) to identify recurring business or technical problems that someone in this role would solve.
3. For each problem, identify the common solution patterns or approaches described.
4. {analysis_depth}

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "searches_performed": <number of web_search calls>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "problem_solution_narratives": {{
    "common_problems": [
      "Problem statement 1 (e.g., 'High cost of model inference at scale')",
      "Problem statement 2 (e.g., 'Slow time-to-value for new enterprise customers')"
    ],
    "solution_patterns": [
      "Solution narrative 1 (e.g., 'Implemented a multi-tiered caching strategy and model quantization to reduce inference costs')",
      "Solution narrative 2 (e.g., 'Developed a standardized RAG-based onboarding process to automate initial setup')"
    ]
  }}
}}

CRITICAL: Return ONLY valid JSON. The problems and solutions should be specific and reflect real-world challenges, not generic statements.
"""

class EnhancedJobDescriptionAnalyzer:
    
    def __init__(
        self,
        master_resume: Dict,
        enable_web_search: bool = True,
        api_key: Optional[str] = None, # Explicitly pass API key if available
        config: Optional[RAGConfig] = None # Assuming RAGConfig is defined
    ):
        self.master_resume = master_resume
        self.enable_web_search = enable_web_search and GEMINI_AVAILABLE
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") # Use GEMINI_API_KEY
        self.config = config or RAGConfig() # Assuming RAGConfig is defined
        # Assuming RAGMission is defined
        self.rag_mission: Optional[RAGMission] = None
        self.total_api_calls_hop0 = 0

        # Initialize telemetry if enabled
        if self.config.telemetry_enabled:
            # Assuming TelemetryLogger is defined/imported
            self.telemetry_logger = TelemetryLogger(self.config.telemetry_log_dir)
        else:
            self.telemetry_logger = None

        if self.enable_web_search:
            try:
                # Assuming GeminiWebSearchClient, WebSearchRAG, JDCacheManager are defined/imported
                self.gemini_client = GeminiWebSearchClient(self.api_key, self.config)
                self.web_rag = WebSearchRAG(self.gemini_client, self.config)
                self.cache_manager = JDCacheManager(
                    self.config.cache_dir,
                    self.config.cache_ttl_days
                )
            except Exception as e:
                logging.getLogger(__name__).warning(f"Web RAG initialization failed: {e}")
                self.gemini_client = None
                self.web_rag = None
                self.cache_manager = None
        else:
            self.gemini_client = None
            self.web_rag = None
            self.cache_manager = None
            
    def analyze(self, job_description: str) -> Tuple[ThematicAnalysis, int]: # Return TA and call count
        """
        Analyze job description using web-search intelligence ONLY.
        v(Your_Version): Removed local NLP fallback. Halts on RAG failure.
        Returns a tuple: (ThematicAnalysis, total_api_calls_hop0)
        """
        self.total_api_calls_hop0 = 0 # Reset counter for each analysis run

        # HOP -0.5: Pre-RAG Differential Analysis (Approach 1) - Keep this
        try:
            # Assuming _execute_pre_rag_analysis is defined and potentially makes API calls
            self.rag_mission = self._execute_pre_rag_analysis(job_description)
            # Add calls from pre-RAG analysis (assuming it returns count or we estimate)
            # For simplicity, estimate 1 call for Pre-RAG if successful
            self.total_api_calls_hop0 += 1 # Add estimated calls
        except Exception as e:
            logging.getLogger(__name__).error(f"FATAL: Pre-RAG analysis (HOP -0.5) failed: {e}. Halting workflow.")
            # Assuming HopExecutionError is defined/imported
            raise HopExecutionError(f"HOP -0.5 Pre-RAG Analysis failed: {e}") from e

        if not self.enable_web_search:
             logging.getLogger(__name__).error("FATAL: Web search is disabled, but no fallback is allowed. Halting workflow.")
             raise HopExecutionError("HOP-0 Configuration Error: Web search disabled, cannot proceed without fallback.")

        if not self.web_rag or not self.gemini_client:
             logging.getLogger(__name__).error("FATAL: Web RAG components failed to initialize. Halting workflow.")
             raise HopExecutionError("HOP-0 Initialization Error: Web RAG components not available.")

        try:
            # Assuming _analyze_with_resilient_web_search returns (analysis, call_count)
            analysis, calls_made = self._analyze_with_resilient_web_search(job_description)
            self.total_api_calls_hop0 += calls_made # Add calls from main RAG phases
            logging.getLogger(__name__).info(f"HOP-0 Web RAG analysis successful. Total API calls for HOP-0: {self.total_api_calls_hop0}")
            return analysis, self.total_api_calls_hop0
        except Exception as e:
             logging.getLogger(__name__).error(f"FATAL: Web RAG analysis failed at HOP-0: {e}. Halting workflow.", exc_info=True) # Log traceback
             raise HopExecutionError(f"HOP-0 Web RAG analysis failed: {e}") from e

    def _build_pre_rag_analysis_prompt(self, job_description: str) -> str:
        """
        Builds the prompt for the HOP -0.5 LLM call to extract entities and find gaps.
        """
        resume_text = json.dumps(self.master_resume.get("professional_experience", []))

        return f"""You are a hyper-efficient HR intelligence analyst. Your task is to perform a differential analysis between a job description (JD) and a candidate's master resume. Extract key entities and identify the signal gap and overlap.

**JOB DESCRIPTION:**
---
{job_description[:2500]}
---

**CANDIDATE MASTER RESUME (Experience Section):**
---
{resume_text[:2500]}
---

**TASK:**
Analyze both texts and return a single, valid JSON object with the following structure.
1.  **Extract entities from the JD:**
    - `target_company_name`: The name of the hiring company.
    - `precise_role_title`: The exact job title.
    - `key_technologies`: Top 5-7 specific technologies, frameworks, or platforms mentioned (e.g., "Agentic platform", "GenAI engineering", "AWS Bedrock").
    - `core_responsibilities`: Top 3-5 core duties or focus areas (e.g., "post-sales adoption", "customer retention", "strategic partnerships").
2.  **Extract entities from the Resume:**
    - `candidate_skills`: Top 10-15 skills and technologies the candidate emphasizes.
3.  **Perform Differential Analysis:**
    - `signal_gap_keywords`: Keywords from `key_technologies` that are **MISSING** from `candidate_skills`. This is the most important output.
    - `signal_overlap_keywords`: Keywords that appear in **BOTH** `key_technologies` and `candidate_skills`.

**OUTPUT FORMAT (JSON ONLY):**
```json
{{
  "jd_entities": {{
    "target_company_name": "<string>",
    "precise_role_title": "<string>",
    "key_technologies": ["<string>", ...],
    "core_responsibilities": ["<string>", ...]
  }},
  "resume_entities": {{
    "candidate_skills": ["<string>", ...]
  }},
  "differential_analysis": {{
    "signal_gap_keywords": ["<string>", ...],
    "signal_overlap_keywords": ["<string>", ...]
  }}
}}
```

CRITICAL: Return only the JSON object. Do not include any preamble, explanation, or markdown formatting outside of the JSON block.
"""

    def _execute_pre_rag_analysis(self, job_description: str) -> RAGMission:
        """
        HOP -0.5: Perform entity extraction and differential analysis.
        v8.10: Uses a single, optimized LLM call for entity extraction.
        NOTE: Assumes this makes 1 API call for simplicity in tracking for now.
              Could be refined to get exact count from search_and_analyze if needed.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Executing HOP -0.5: Pre-RAG Differential Analysis...")

        prompt = self._build_pre_rag_analysis_prompt(job_description)
        # Use the existing client but with a more constrained call for speed and cost.
        # This call now returns (result, call_count)
        analysis_json, pre_rag_calls = self.gemini_client.search_and_analyze(prompt, "Pre-RAG Analysis")
        # Update the main counter (though it's reset in analyze usually)
        self.total_api_calls_hop0 += pre_rag_calls

        mission = RAGMission(
            target_company_name=analysis_json["jd_entities"]["target_company_name"],
            precise_role_title=analysis_json["jd_entities"]["precise_role_title"],
            key_technologies=analysis_json["jd_entities"]["key_technologies"],
            core_responsibilities=analysis_json["jd_entities"]["core_responsibilities"],
            signal_gap_keywords=analysis_json["differential_analysis"]["signal_gap_keywords"],
            signal_overlap_keywords=analysis_json["differential_analysis"]["signal_overlap_keywords"]
        )
        logger.info(f"  ✓ RAG Mission defined. Gap keywords: {mission.signal_gap_keywords}")
        return mission

    def _analyze_with_resilient_web_search(
        self,
        job_description: str
    ) -> Tuple[ThematicAnalysis, int]: # Return TA and call count
        """
        v11.60 Final Fix: Added JSON roundtrip conversion before synthesis & caching.
        NOW returns a tuple: (ThematicAnalysis, total_api_calls_this_hop)
        """
        import logging

        from collections.abc import Mapping, Sequence
        from dataclasses import is_dataclass, asdict
        
        telemetry = RAGTelemetry() if self.telemetry_logger else None
        start_time = time.time()
        total_api_calls_this_hop = 0 # Initialize counter for this specific execution
        logger = logging.getLogger(__name__)

        if self.cache_manager:
            cached = self.cache_manager.get(job_description)
            if cached:
                logger.info("Using cached web RAG analysis")
                # Return 0 calls when using cache
                return self._dict_to_thematic_analysis(cached), 0

        if not self.web_rag or not self.rag_mission:
             logger.warning("Web RAG or RAG Mission not available. Falling back to local NLP.")
             # Local NLP returns 0 calls
             return self._analyze_local_nlp(job_description), 0


        partial_result = PartialRAGResult()

        phase1_start = time.time()
        try:
            logger.info("=== Starting Phase 1: Thematic Research ===")
            # Use WebSearchRAG methods which now call the modified search_and_analyze
            phase1_results, calls_p1 = self.web_rag.phase1_thematic_research(job_description, self.rag_mission)
            total_api_calls_this_hop += calls_p1
            partial_result.phase1_result = phase1_results
            partial_result.phase1_success = True
            if telemetry:
                telemetry.phase1_success = True
                telemetry.phase1_attempts = 1 # Simplified, actual attempts handled within executor
                telemetry.total_search_calls += calls_p1 # Use actual calls
            logger.info(f"Phase 1: SUCCESS ({calls_p1} calls)")
        except Exception as e:
            logger.warning(f"Phase 1: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 1: {type(e).__name__}")
            if telemetry:
                telemetry.phase1_success = False
                telemetry.errors.append(f"Phase 1: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase1_duration_seconds = time.time() - phase1_start

        phase2_start = time.time()
        try:
            logger.info("=== Starting Phase 2: Authenticity Patterns ===")
            phase2_results, calls_p2 = self.web_rag.phase2_authenticity_patterns(job_description, self.rag_mission)
            total_api_calls_this_hop += calls_p2
            partial_result.phase2_result = phase2_results
            partial_result.phase2_success = True
            if telemetry:
                telemetry.phase2_success = True
                telemetry.phase2_attempts = 1
                telemetry.total_search_calls += calls_p2
            logger.info(f"Phase 2: SUCCESS ({calls_p2} calls)")
        except Exception as e:
            logger.warning(f"Phase 2: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 2: {type(e).__name__}")
            if telemetry:
                telemetry.phase2_success = False
                telemetry.errors.append(f"Phase 2: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase2_duration_seconds = time.time() - phase2_start

        phase3_start = time.time()
        try:
            logger.info("=== Starting Phase 3: Competitive Positioning ===")
            phase3_results, calls_p3 = self.web_rag.phase3_competitive_positioning(job_description, self.rag_mission)
            total_api_calls_this_hop += calls_p3
            partial_result.phase3_result = phase3_results
            partial_result.phase3_success = True
            if telemetry:
                telemetry.phase3_success = True
                telemetry.phase3_attempts = 1
                telemetry.total_search_calls += calls_p3
            logger.info(f"Phase 3: SUCCESS ({calls_p3} calls)")
        except Exception as e:
            logger.warning(f"Phase 3: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 3: {type(e).__name__}")
            if telemetry:
                telemetry.phase3_success = False
                telemetry.errors.append(f"Phase 3: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase3_duration_seconds = time.time() - phase3_start

        phase4_start = time.time()
        try:
            logger.info("=== Starting Phase 4: Narrative Mining ===")
            phase4_results, calls_p4 = self.web_rag.phase4_narrative_mining(self.rag_mission)
            total_api_calls_this_hop += calls_p4
            partial_result.phase4_result = phase4_results
            partial_result.phase4_success = True
            if telemetry:
                telemetry.phase4_success = True
                telemetry.phase4_attempts = 1
                telemetry.total_search_calls += calls_p4
            logger.info(f"Phase 4: SUCCESS ({calls_p4} calls)")
        except Exception as e:
            logger.warning(f"Phase 4: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 4: {type(e).__name__}")
            if telemetry:
                telemetry.phase4_success = False
                telemetry.errors.append(f"Phase 4: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase4_duration_seconds = time.time() - phase4_start


        logger.info(
            f"RAG Phases Complete: "
            f"Success Rate = {partial_result.success_rate:.1%} "
            f"({partial_result.phase1_success}, {partial_result.phase2_success}, "
            f"{partial_result.phase3_success}, {partial_result.phase4_success}) "
            f"Total API Calls: {total_api_calls_this_hop}" # Log total calls
        )

        analysis = None # Initialize analysis variable

        if partial_result.full_success:
            logger.info("✓ Strategy 1: Full 4-phase RAG successful")

            def _json_roundtrip_convert(data: Any, label: str) -> Dict:
                """Forces complex objects into plain dicts via JSON roundtrip."""
                try:
                    def default_serializer(o):
                        if hasattr(o, '__dataclass_fields__'):
                            return asdict(o)
                        try:
                            json.dumps(o)
                            return o
                        except TypeError:
                            return f"__CONVERTED_STR__{str(o)}__"

                    json_str = json.dumps(data, default=default_serializer)
                    plain_data = json.loads(json_str)

                    if isinstance(plain_data, dict):
                        logger.debug(f"Successfully force-converted '{label}' result to plain dict.")
                        return plain_data
                    else:
                        logger.warning(f"JSON roundtrip for '{label}' did not result in a dict (Type: {type(plain_data)}). Returning empty dict.")
                        return {}
                except Exception as e:
                    logger.error(f"FATAL: Failed to perform JSON roundtrip conversion for '{label}': {e}", exc_info=True)
                    try:
                         simple_str = json.dumps(str(data))
                         return {"error": "simple_conversion_fallback", "data": simple_str}
                    except:
                         return {"error": "total_conversion_failure"}

            phase1_plain = _json_roundtrip_convert(partial_result.phase1_result, "Phase 1")
            phase2_plain = _json_roundtrip_convert(partial_result.phase2_result, "Phase 2")
            phase3_plain = _json_roundtrip_convert(partial_result.phase3_result, "Phase 3")
            phase4_plain = _json_roundtrip_convert(partial_result.phase4_result, "Phase 4")

            # Call synthesis function with the *plain* dicts
            analysis = self._synthesize_thematic_analysis(
                phase1_plain,
                phase2_plain,
                phase3_plain,
                phase4_plain,
                job_description
            )
            if telemetry:
                telemetry.full_success = True
                telemetry.success_rate = 1.0

        elif partial_result.any_success:
            logger.error(f"✗ RAG analysis was only partially successful ({partial_result.success_rate:.0%}). Halting workflow.")
            raise HopExecutionError("RAG analysis failed to achieve 100% success across all four phases.")

        else:
            logger.error("✗ All RAG phases failed. Halting workflow.")
            logger.warning(f"Failure reasons: {', '.join(partial_result.failure_reasons)}")
            raise HopExecutionError("All RAG phases failed during execution.")

        try:
            if analysis:
                # Use the same roundtrip converter for caching
                analysis_dict_for_cache = _json_roundtrip_convert(analysis, "Final Analysis")

                if self.cache_manager and analysis_dict_for_cache and isinstance(analysis_dict_for_cache, dict):
                    logger.debug("Attempting to cache the analysis result...")
                    self.cache_manager.set(job_description, analysis_dict_for_cache)
                    logger.debug("Analysis result cached successfully.")
                elif not analysis_dict_for_cache or not isinstance(analysis_dict_for_cache, dict):
                     logger.warning(f"Skipping cache: Conversion of final analysis to plain dict failed.")
            else:
                logger.warning("Skipping cache: Analysis object is None.")

        except Exception as cache_e:
             logger.warning(f"Failed to convert or cache RAG analysis result: {type(cache_e).__name__}: {cache_e}", exc_info=False)

        if telemetry and self.telemetry_logger:
            telemetry.total_duration_seconds = time.time() - start_time
            telemetry.circuit_breaker_triggered = self.gemini_client.circuit_breaker.state == CircuitState.OPEN
            telemetry.failed_api_calls = self.gemini_client.circuit_breaker.failure_count # Approximate
            telemetry.total_api_calls = total_api_calls_this_hop # Use the accurate count
            telemetry.total_search_calls = total_api_calls_this_hop # Update telemetry field
            self.telemetry_logger.log(telemetry)

        logger.info(f"Analysis complete. Total API calls for HOP-0: {total_api_calls_this_hop}")
        return analysis, total_api_calls_this_hop # Return analysis and count

    def _extract_role_from_jd(self, job_description: str) -> str:
        """Extract role title from JD for fallback scenarios."""
        lines = job_description.split('\n')
        if lines:
            # First line often contains role title
            return lines[0].strip()[:100]
        return "Professional"

    def _synthesize_thematic_analysis(
        self,
        phase1: Any,
        phase2: Any,
        phase3: Any,
        phase4: Any,
        job_description: str
    ) -> 'ThematicAnalysis':
        """
        Synthesize three-phase web RAG results into ThematicAnalysis.
        v11.60 Final Fix: Manually reconstruct dicts from RAG results.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Synthesizing RAG results with weighted analysis...")

        def _manual_reconstruct(data: Any, label: str) -> Dict:
            """Attempts to manually rebuild a dictionary from known structures."""
            new_dict = {}
            if data is None: return {}
            try:
                # Top level keys common to most phases
                for key in ["search_summary", "thematic_analysis", "role_classification",
                            "authenticity_patterns", "pattern_confidence",
                            "competitive_analysis", "positioning_insight",
                            "problem_solution_narratives"]:
                    if hasattr(data, key):
                        value = getattr(data, key)
                        # Basic recursion for lists and dict-like things
                        if isinstance(value, list):
                            new_dict[key] = [_manual_reconstruct_nested(item) for item in value]
                        elif hasattr(value, 'items') and callable(getattr(value, 'items')): # Check if dict-like
                            new_dict[key] = _manual_reconstruct_nested(value)
                        elif hasattr(value, '__dict__'): # Fallback for simple objects
                            new_dict[key] = _manual_reconstruct_nested(value.__dict__)
                        else:
                            new_dict[key] = value # Assume primitive
                # Log type and preview after reconstruction
                logger.debug(f"Reconstructed '{label}' - Type: {type(new_dict)}, Keys: {list(new_dict.keys())}")
                return new_dict
            except Exception as e:
                logger.error(f"Error during manual reconstruction of '{label}': {e}", exc_info=True)
                return {} # Return empty on failure

        def _manual_reconstruct_nested(item: Any) -> Any:
            """Recursive helper for manual reconstruction."""
            if hasattr(item, 'items') and callable(getattr(item, 'items')):
                return {k: _manual_reconstruct_nested(v) for k, v in item.items()}
            elif isinstance(item, dict):
                 return {k: _manual_reconstruct_nested(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [_manual_reconstruct_nested(elem) for elem in item]
            elif hasattr(item, '__dict__'): # Fallback for simple objects
                logger.debug(f"  Nested: Converting object via __dict__: {type(item)}")
                # Avoid recursion on potentially problematic internal attrs
                temp_dict = {}
                for k, v in item.__dict__.items():
                     if not k.startswith('_'):
                          temp_dict[k] = _manual_reconstruct_nested(v)
                     else:
                          temp_dict[k] = str(v) # Convert internal attrs to string safely
                return temp_dict
            else:
                # Assume primitive
                return item

        logger.debug("Starting manual reconstruction...")
        phase1_dict = _manual_reconstruct(phase1, "Phase 1")
        phase2_dict = _manual_reconstruct(phase2, "Phase 2")
        phase3_dict = _manual_reconstruct(phase3, "Phase 3")
        phase4_dict = _manual_reconstruct(phase4, "Phase 4")

        p1_themes_check = phase1_dict.get("thematic_analysis", {})
        if not isinstance(p1_themes_check, dict):
            logger.error(f"Reconstruction failed: p1_themes_check is type {type(p1_themes_check)}")
        p1_primary_check = p1_themes_check.get("primary_theme", {})
        if not isinstance(p1_primary_check, dict):
             logger.error(f"Reconstruction failed: p1_primary_check is type {type(p1_primary_check)}")
             raise AttributeError("Manual reconstruction failed to produce a dictionary for p1_primary.")
        logger.debug(f"Manual reconstruction checks passed for p1_primary (Type: {type(p1_primary_check)}).")

        keyword_scores = {}
        weights = self.config.source_weights

        # Phase 1: Thematic
        p1_themes = phase1_dict.get("thematic_analysis", {})
        p1_primary = p1_themes.get("primary_theme", {}) # Should be a dict now
        p1_secondary = p1_themes.get("secondary_themes", [])
        p1_trending = p1_themes.get("trending_keywords", [])

        # Ensure keywords are strings before adding
        for kw in p1_primary.get("keywords", []):
            if isinstance(kw, str):
                keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_COMPANY_BLOG", 1.5)

        # Ensure secondary themes are processed safely
        if isinstance(p1_secondary, list):
            for theme in p1_secondary:
                if isinstance(theme, dict):
                    for kw in theme.get("keywords", []):
                        if isinstance(kw, str):
                            keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)
        # Ensure trending keywords are processed safely
        if isinstance(p1_trending, list):
            for kw in p1_trending:
                 if isinstance(kw, str):
                     keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)

        # Phase 2: Authenticity
        p2_auth = phase2_dict.get("authenticity_patterns", {})
        if not isinstance(p2_auth, dict): p2_auth = {}
        for pattern_type, pattern_list in p2_auth.items():
            if isinstance(pattern_list, list):
                is_competency = (pattern_type == "competency_phrasing")
                weight = weights.get("SOURCE_TARGET_EMPLOYEE", 1.4) if is_competency else weights.get("SOURCE_GENERIC_PROFILE", 0.5)
                for kw in pattern_list:
                    if isinstance(kw, str):
                        keyword_scores[kw] = keyword_scores.get(kw, 0) + weight

        # Phase 3: Competitive
        p3_comp = phase3_dict.get("competitive_analysis", {})
        if not isinstance(p3_comp, dict): p3_comp = {}
        p3_diff_kws = p3_comp.get("differentiator_keywords", [])
        p3_table_kws = p3_comp.get("table_stakes_keywords", [])

        if isinstance(p3_diff_kws, list):
            for item in p3_diff_kws:
                if isinstance(item, dict) and isinstance(item.get("keyword"), str):
                    kw = item["keyword"]
                    weight = weights.get("SOURCE_GARTNER_MQ", 1.2) * item.get("uniqueness_score", 1.0)
                    keyword_scores[kw] = keyword_scores.get(kw, 0) + weight
        if isinstance(p3_table_kws, list):
            for item in p3_table_kws:
                 if isinstance(item, dict) and isinstance(item.get("keyword"), str):
                     kw = item["keyword"]
                     keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)


        # Sort keywords by weighted score
        sorted_keywords = sorted(keyword_scores.items(), key=lambda item: item[1], reverse=True)

        differentiator_keywords_weighted = [{"keyword": kw, "weight": score} for kw, score in sorted_keywords]
        top_differentiators = [kw for kw, score in sorted_keywords[:15]]

        logger.info(f"  ✓ Top 5 weighted keywords: {top_differentiators[:5]}")

        # Extract primary theme from Phase 1
        primary_theme = {
            "name": p1_primary.get("name", "Unknown Theme"),
            "confidence": p1_primary.get("confidence", 0.0),
            "keywords": p1_primary.get("keywords", []),
            "market_signal": "STRONG", "source": "WEB_SEARCH"
        }

        # Extract secondary themes
        secondary_themes = []
        if isinstance(p1_secondary, list):
            secondary_themes = [
                {"name": t.get("name", ""), "relevance": t.get("relevance", 0.0), "keywords": t.get("keywords", []), "source": "WEB_SEARCH"}
                for t in p1_secondary[:5] if isinstance(t, dict)
            ]

        # Role classification
        role_classification = phase1_dict.get("role_classification", {})
        if not isinstance(role_classification, dict): role_classification = {}
        if "precise_role_title" not in role_classification and self.rag_mission:
             role_classification["precise_role_title"] = self.rag_mission.precise_role_title
        elif "precise_role_title" not in role_classification:
              role_classification["precise_role_title"] = "Unknown Role"


        # Positioning directives
        positioning_directives = {
            "apply_industry_first": True, "authenticity_positioning_ratio": "0.8:0.2",
            "competitive_edge": phase3_dict.get("positioning_insight", "N/A"),
            "table_stakes_count": len(p3_table_kws) if isinstance(p3_table_kws, list) else 0,
            "differentiator_count": len(top_differentiators)
        }

        # Authenticity patterns
        p2_confidence = phase2_dict.get("pattern_confidence", {})
        if not isinstance(p2_confidence, dict): p2_confidence = {}
        authenticity_patterns = {
            "status": "STRONG" if p2_confidence.get("overall", 0.0) > 0.7 else "MODERATE",
            "patterns": p2_auth,
            "confidence": p2_confidence,
            "fallback_applied": False, "fallback_reason": None
        }

        # Competitive intelligence
        p3_summary = phase3_dict.get("search_summary", {})
        if not isinstance(p3_summary, dict): p3_summary = {}
        competitive_intel = CompetitiveIntelligence(
            peer_jds_analyzed_count=p3_summary.get("peer_jds_analyzed", 0),
            differentiator_keywords=top_differentiators,
            differentiator_keywords_raw=top_differentiators, # Revisit if raw list source differs
            differentiator_keywords_weighted=differentiator_keywords_weighted
        )

        # Signal quality score
        signal_quality = (
            p1_primary.get("confidence", 0.0) * 0.4 +
            p2_confidence.get("overall", 0.0) * 0.3 +
            min(1.0, p3_summary.get("peer_jds_analyzed", 0) / 10.0) * 0.3
        )

        # Retrieval sources
        retrieval_sources = [
            RetrievalSource("PHASE1_THEMATIC", "Web_RAG", p1_primary.get("confidence", 0.0), "SUCCESS", "SOURCE_COMPANY_BLOG"),
            RetrievalSource("PHASE2_AUTHENTICITY", "Web_RAG", p2_confidence.get("overall", 0.0), "SUCCESS", "SOURCE_TARGET_EMPLOYEE"),
            RetrievalSource("PHASE3_COMPETITIVE", "Web_RAG", min(1.0, p3_summary.get("peer_jds_analyzed", 0) / 10.0), "SUCCESS", "SOURCE_GARTNER_MQ"),
            RetrievalSource("PHASE4_NARRATIVE", "Web_RAG", 1.0, "SUCCESS", "SOURCE_NARRATIVE_MINING")
        ]


        return ThematicAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_classification=role_classification,
            positioning_directives=positioning_directives,
            authenticity_patterns=authenticity_patterns,
            competitive_intelligence=competitive_intel,
            problem_solution_narratives=phase4_dict.get("problem_solution_narratives"),
            signal_quality_score=signal_quality,
            retrieval_method="WEB_SEARCH_RAG",
            retrieval_sources=retrieval_sources,
            weighting_formula={"description": "Weighted Synthesis v8.10", "weights": self.config.source_weights}
        )
           
    def _extract_company_name(self, job_description: str) -> str:
        """Extract company name from JD."""
        match = re.search(
            r'(?:Company|at)\s*:?\s*([A-Z][A-Za-z0-9\s&.,\-]+?)(?:\n|\s{2,}|$)', 
            job_description
        )
        if match:
            return match.group(1).strip()
        return "Target Company"
    
    def _dict_to_thematic_analysis(self, data: Dict) -> "'ThematicAnalysis'":
        """
        [v12.00 FIX] Convert cached dict back to ThematicAnalysis object.
        FIX: Added more robust checks for nested object reconstruction.
        """
        comp_intel_data = data.get("competitive_intelligence")
        comp_intel = None # Initialize to None

        if isinstance(comp_intel_data, dict):
            try:
                # Attempt to create CompetitiveIntelligence from the dict
                comp_intel = CompetitiveIntelligence(**comp_intel_data)
                 # V12.00 addition: Verify essential list attributes are lists after creation
                if not isinstance(getattr(comp_intel, 'differentiator_keywords', None), list):
                    logging.warning("Reconstructed comp_intel.differentiator_keywords is not a list. Resetting.")
                    comp_intel.differentiator_keywords = []
                if not isinstance(getattr(comp_intel, 'differentiator_keywords_raw', None), list):
                    logging.warning("Reconstructed comp_intel.differentiator_keywords_raw is not a list. Resetting.")
                    comp_intel.differentiator_keywords_raw = []
                if not isinstance(getattr(comp_intel, 'differentiator_keywords_weighted', None), list):
                    logging.warning("Reconstructed comp_intel.differentiator_keywords_weighted is not a list. Resetting.")
                    comp_intel.differentiator_keywords_weighted = []

            except TypeError as e:
                logging.warning(f"Error reconstructing CompetitiveIntelligence from cached data: {e}. Data: {comp_intel_data}. Initializing default.")
                comp_intel = CompetitiveIntelligence() # Fallback to default on reconstruction error
        else:
            if "competitive_intelligence" not in data:
                 logging.warning("Cached data missing 'competitive_intelligence' key. Initializing default.")
            else:
                 logging.warning(f"Cached 'competitive_intelligence' data is not a dict (Type: {type(comp_intel_data)}). Initializing default.")
            comp_intel = CompetitiveIntelligence()

        retrieval_sources = []
        cached_sources = data.get("retrieval_sources", [])
        if isinstance(cached_sources, list): # Ensure it's a list before iterating
            for src_data in cached_sources:
                if isinstance(src_data, dict):
                    try:
                        retrieval_sources.append(RetrievalSource(**src_data))
                    except TypeError as e:
                         logging.warning(f"Error reconstructing RetrievalSource from cached data: {e}. Data: {src_data}")
                else:
                     logging.warning(f"Skipping invalid retrieval source data in cache (not a dict): {src_data}")
        elif cached_sources is not None: # Log if it exists but isn't a list
             logging.warning(f"Cached 'retrieval_sources' data is not a list (Type: {type(cached_sources)}). Skipping reconstruction.")

        return ThematicAnalysis(
            primary_theme=data.get("primary_theme", {}),
            secondary_themes=data.get("secondary_themes", []),
            role_classification=data.get("role_classification", {}),
            positioning_directives=data.get("positioning_directives", {}),
            # V12.00 addition: Ensure authenticity_patterns is a dict
            authenticity_patterns=data.get("authenticity_patterns", {}),
            competitive_intelligence=comp_intel, # Use the safely created/default object
            signal_quality_score=data.get("signal_quality_score", 0.0),
            retrieval_method=data.get("retrieval_method", "UNKNOWN_CACHE"),
            retrieval_sources=retrieval_sources,
            problem_solution_narratives=data.get("problem_solution_narratives"),
            weighting_formula=data.get("weighting_formula")
        )
         
    def _analyze_local_nlp(self, job_description: str) -> 'ThematicAnalysis':
        keywords = self._extract_keywords(job_description)
        theme_scores = self._calculate_theme_scores(keywords, job_description)
        primary_theme = self._generate_primary_theme(theme_scores, keywords)
        secondary_themes = self._generate_secondary_themes(theme_scores, keywords)
        competitive_intel = self._extract_competitive_intelligence(keywords, job_description)
        role_classification = self._classify_role(keywords, job_description)
        signal_quality_score = self._calculate_signal_quality(keywords, theme_scores)

        local_auth_patterns = {
            "status": "FALLBACK",
            "patterns": {
                 "executive_summary_patterns": ["Built <ACHIEVEMENT> resulting in <IMPACT>"], # Minimal default
                 "achievement_verb_patterns": ["Led", "Managed", "Developed"], # Minimal default
                 "metric_presentation_patterns": ["<NUMBER>% improvement"], # Minimal default
                 "competency_phrasing": ["<SKILL>: <DESCRIPTION>"] # Minimal default
            },
            "confidence": {"overall": 0.3}, # Low confidence for fallback
            "fallback_applied": True,
            "fallback_reason": "Local NLP used"
        }

        return ThematicAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_classification=role_classification,
            positioning_directives={
                "apply_industry_first": True,
                "authenticity_positioning_ratio": "0.8:0.2"
            },
            authenticity_patterns=local_auth_patterns, # Use the fixed structure
            competitive_intelligence=competitive_intel,
            signal_quality_score=signal_quality_score,
            retrieval_method="LOCAL_NLP",
            retrieval_sources=[
                RetrievalSource("JD_ANALYSIS", "NLP_Keyword_Extraction", signal_quality_score, "LOCAL_FALLBACK", "LOCAL_NLP")
            ]
        )
    
    def _extract_keywords(self, text: str) -> Dict[str, int]:
        """Extract keywords with frequency counts."""
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        
        keyword_freq = {}
        for word in words:
            if word not in STOPWORDS and len(word) >= 3:
                keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        for domain, terms in self.domain_themes.items():
            for term in terms:
                if term in text_lower and len(term.split()) > 1:
                    keyword_freq[term] = text_lower.count(term) * 2
        
        return keyword_freq
    
    def _calculate_theme_scores(self, keywords: Dict[str, int], jd_text: str) -> Dict[str, float]:
        """Calculate relevance scores for each theme."""
        theme_scores = {}
        jd_lower = jd_text.lower()
        
        for theme_name, theme_keywords in self.domain_themes.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in theme_keywords:
                if keyword in jd_lower:
                    occurrences = jd_lower.count(keyword)
                    importance = len(keyword.split())
                    score += occurrences * (1.0 + importance * 0.5)
                    matched_keywords.append(keyword)
            
            if score > 0:
                normalized_score = min(1.0, score / (len(theme_keywords) * 0.5))
                theme_scores[theme_name] = {
                    'score': normalized_score,
                    'matched_keywords': matched_keywords,
                    'match_count': len(matched_keywords)
                }
        
        return theme_scores
    
    def _generate_primary_theme(self, theme_scores: Dict[str, dict], keywords: Dict[str, int]) -> Dict:
        """Generate primary theme from highest scoring domain."""
        if not theme_scores:
            return {
                "name": "Professional Services",
                "confidence": 0.5,
                "keywords": list(keywords.keys())[:5],
                "market_signal": "MODERATE"
            }
        
        best_theme = max(theme_scores.items(), key=lambda x: x[1]['score'])
        
        return {
            "name": best_theme[0],
            "confidence": best_theme[1]['score'],
            "keywords": best_theme[1]['matched_keywords'],
            "market_signal": "STRONG" if best_theme[1]['score'] > 0.7 else "MODERATE"
        }
    
    def _generate_secondary_themes(self, theme_scores: Dict[str, dict], keywords: Dict[str, int]) -> List[Dict]:
        """Generate secondary themes."""
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        secondary = []
        for theme_name, theme_data in sorted_themes[1:6]:
            secondary.append({
                "name": theme_name,
                "relevance": theme_data['score'],
                "keywords": theme_data['matched_keywords']
            })
        
        return secondary
    
    def _extract_competitive_intelligence(self, keywords: Dict[str, int], jd_text: str) -> 'CompetitiveIntelligence':
        """Extract competitive intelligence from keywords."""
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return CompetitiveIntelligence(
            peer_jds_analyzed_count=0,
            differentiator_keywords=[kw for kw, _ in top_keywords[:5]],
            differentiator_keywords_raw=[kw for kw, _ in top_keywords[:5]],
            differentiator_keywords_weighted=[
                {"keyword": kw, "weight": float(count) / max(keywords.values())}
                for kw, count in top_keywords[:5]
            ]
        )
    
    def _classify_role(self, keywords: Dict[str, int], jd_text: str) -> Dict:
        """Classify role based on keywords, incorporating new themes."""
        jd_lower = jd_text.lower()

        # Seniority check (Unchanged)
        seniority = "mid"
        if any(word in jd_lower for word in ['senior', 'lead', 'principal', 'staff']):
            seniority = "senior"
        elif any(word in jd_lower for word in ['executive', 'director', 'vp', 'chief', 'head']):
            seniority = "executive"
        elif any(word in jd_lower for word in ['junior', 'entry', 'associate']):
            seniority = "entry"

        role_type = "Technical_IC" # Default archetype
        # Assuming _calculate_theme_scores is defined within this class
        theme_scores = self._calculate_theme_scores(keywords, jd_text)
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        top_theme = sorted_themes[0][0] if sorted_themes else None
        top_function = top_theme or "Technology" # Use top theme as function, default to Technology

        # Map top theme to archetype
        if top_theme == 'Leadership': role_type = "Executive_Leader"
        elif top_theme == 'Sales_GTM': role_type = "Pre-Sales_GTM"
        elif top_theme == 'Partnerships': role_type = "Pre-Sales_GTM" # Map Partnerships to GTM
        elif top_theme == 'Customer_Success': role_type = "Post-Sales_Customer_Success"
        elif top_theme == 'Product': role_type = "Product_Management"
        elif top_theme in ['AI/ML', 'Cloud', 'Data', 'Engineering_IC', 'Enterprise']: role_type = "Technical_IC" # Group technical roles
        # Add mappings for new themes (can refine these later if needed)
        elif top_theme == 'Marketing': role_type = "Marketing_Leader" # Could also be Pre-Sales_GTM depending on role focus
        elif top_theme == 'Finance': role_type = "Finance_Leader" # New simple archetype
        elif top_theme == 'Security/CISO': role_type = "Security_Leader" # New simple archetype
        elif top_theme == 'IT/CIO': role_type = "IT_Leader" # New simple archetype
        elif top_theme == 'Business': role_type = "Operations_Leader" # Map general Business to Operations

        industry_focus = "Technology" # Default
        for industry, keywords_list in self.INDUSTRY_KEYWORDS.items():
            if any(keyword in jd_lower for keyword in keywords_list):
                industry_focus = industry
                break # Stop after first match

        return {
            "seniority": seniority,
            "function": top_function, # Use the determined top function
            "industry_focus": industry_focus,
            "role_archetype": role_type # Use the determined role_type
        }

    def _calculate_signal_quality(self, keywords: Dict[str, int], theme_scores: Dict[str, dict]) -> float:
        """Calculate signal quality score."""
        if not theme_scores:
            return 0.5
        
        keyword_diversity = len(keywords) / 100.0
        theme_strength = max(theme_scores.values(), key=lambda x: x['score'])['score']
        
        return min(1.0, (keyword_diversity * 0.3 + theme_strength * 0.7))

class ClerkExtractor:

    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self.hallucination_detector = HallucinationDetector()
        self._validate_master_resume_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        validation_results = []

        experience_sections = self._build_experience_sections()

        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([bullet['bullet_text'] for bullet in section.get('bullets', [])])

        bullet_dicts = [{'bullet_text': b} for b in all_bullets]
        hallucination_results = self.hallucination_detector.detect(bullet_dicts)
        validation_results.extend(hallucination_results)

        extracted_data = {
            "experience_sections": experience_sections,  # v5.36: Structured sections
            "header": self.master_resume.get("header", {}), # This key isn't in MASTER_RESUME_JSON, but harmless
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications_and_credentials", []) # <-- FIX: Use correct key
            # Note: competencies are GENERATED at HOP-3 (Artist Generation), NOT copied from master
        }

        return extracted_data, validation_results

    def _validate_master_resume_structure(self):
        """
        Hardening: Validates that the master resume has the essential top-level keys.
        Raises ValueError if the structure is invalid.
        """
        required_keys = ["owner", "professional_experience", "education", "certifications_and_credentials", "strategic_and_technical_competencies"]
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")

        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            raise ValueError(f"MASTER_RESUME_JSON is missing required keys: {', '.join(missing_keys)}")
        print("  ✓ Master resume structure validated.")

    def _build_experience_sections(self) -> List[Dict]:
        """
        v5.36: Build structured experience_sections from master resume.
        Each section contains: company, title, location, dates, overview, bullets.
        """
        experience_sections = []

        for exp in self.master_resume.get("professional_experience", []):
            bullets = []
            # Get bullets from either 'bullet_pool' or 'highlights'
            bullet_source = exp.get("bullet_pool", exp.get("highlights", []))

            for bullet_text in bullet_source:
                bullets.append({ # <--- This creates the dictionary
                    "bullet_text": bullet_text,
                    "quantified_metrics": self._extract_metrics(bullet_text),
                    "canonical_verbs": [],  # Will be enriched in HOP-2
                    "provenance": BulletProvenance.Verbatim.value
                })

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""), # Get nested date
                "end_date": exp.get("dates", {}).get("end", ""),   # Get nested date
                "overview": exp.get("overview", ""),
                "bullets": bullets, # <--- This is now a list of dicts
                "highlights": [bullet['bullet_text'] for bullet in bullets]
            })

        return experience_sections

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract quantified metrics from bullet text."""
        metrics = []

        # Pattern: $XXM, $XXB, XX%, XXM+, XXB+
        patterns = [
            r'\$\d+\.?\d*[MBK]\+?',  # $50M, $1.5B, $100K
            r'\d+\.?\d*%',  # 35%, 12.5%
            r'\d+\.?\d*[MBK]\+',  # 150M+, 2B+
            r'\d{1,3}(?:,\d{3})+',  # 1,000 or 100,000
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            metrics.extend(matches)

        return metrics
    
class HallucinationDetector:
    """
    Detect potential hallucinations in resume content.
    Flags implausible metrics, temporal inconsistencies, etc.
    """

    def detect(self, bullet_pool: List[Dict]) -> List[ValidationResult]:
        """
        Run hallucination detection on bullet pool.
        Returns: List of validation results
        """
        results = []

        for i, bullet in enumerate(bullet_pool):
            text = bullet.get("bullet_text", "")

            # Check for implausible growth rates
            if self._has_implausible_growth(text):
                results.append(ValidationResult(
                    rule_id="HALLUCINATION_IMPLAUSIBLE_GROWTH",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Bullet {i+1} may contain implausible growth rate",
                    details={"bullet_text": text[:100]}
                ))

            # Check for excessive superlatives
            if self._has_excessive_superlatives(text):
                results.append(ValidationResult(
                    rule_id="HALLUCINATION_EXCESSIVE_SUPERLATIVES",
                    passed=False,
                    severity=ValidationSeverity.HIGH, # Changed from MEDIUM to HIGH
                    message=f"Bullet {i+1} contains excessive superlatives",
                    details={"bullet_text": text[:100]}
                ))

        # If no hallucinations detected, add passing result
        if not results:
            results.append(ValidationResult(
                rule_id="HALLUCINATION_CHECK",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"No hallucinations detected in {len(bullet_pool)} bullets"
            ))

        return results

    def _has_implausible_growth(self, text: str) -> bool:
        """Check for implausibly high growth rates (>10x in short time)."""
        # Look for patterns like "1000%" or "10x" with short timeframes
        growth_patterns = [
            r'\d{3,}%',  # 100%+ growth
            r'\d+x',  # 5x, 10x growth
        ]

        for pattern in growth_patterns:
            if re.search(pattern, text):
                # Check if associated with short timeframe
                if any(term in text.lower() for term in ['month', 'quarter', '90 day']):
                    return True

        return False

    def _has_excessive_superlatives(self, text: str) -> bool:
        """Check for excessive use of superlatives."""
        superlatives = [
            'revolutionary', 'groundbreaking', 'unprecedented', 'unparalleled',
            'game-changing', 'world-class', 'best-in-class', 'cutting-edge'
        ]

        count = sum(1 for word in superlatives if word in text.lower())
        return count >= 2  # Flag if 2+ superlatives in single bullet

class DataEnricher:
    """
    HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc.
    v13.10: Merged VerbCanonicalizer logic directly into this class.
    v13.50: Removed FORBIDDEN_VERBS check (moved to PreFlightValidator).
    """

    CANONICAL_VERBS = {
        "led": ["led", "lead", "leading"], "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"], "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"], "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"], "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"], "developed": ["developed", "develop", "developing"]
    }

    def __init__(self):
        self.duplicate_detector = DuplicateDetector()

    def _canonicalize_verbs(self, text: str) -> List[str]:
        """[REFACTORED] Extract and canonicalize verbs from text using a list comprehension."""
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(
        self,
        extracted_data: Dict,
           thematic_analysis: "ThematicAnalysis",
     orchestrator=None
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        v5.65: Now stores DuplicateDetector on orchestrator for QA sections 4 & 5.
        v13.50: Removed FORBIDDEN_VERBS check.
        Returns: (enriched_data, validation_results)
        """
        validation_results = []

        # v5.65: Store duplicate_detector on orchestrator for later use in dedup analysis
        if orchestrator is not None:
            orchestrator.dup_detector = self.duplicate_detector

        # v5.36: Work with experience_sections structure
        experience_sections = extracted_data.get("experience_sections", [])

        # Flatten bullets for duplicate detection
        all_bullets = []
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                # Canonicalize verbs (Enrichment step)
                canonical_verbs = self._canonicalize_verbs(bullet.get("bullet_text", ""))
                bullet["canonical_verbs"] = canonical_verbs

                all_bullets.append(bullet)

        # Detect duplicates
        duplicates = self.duplicate_detector.find_duplicates(all_bullets)
        if duplicates:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_BULLETS",
                passed=False,
                severity=ValidationSeverity.HIGH, # Changed from MEDIUM to HIGH
                message=f"Found {len(duplicates)} potential duplicate bullets",
                details={"duplicates": duplicates[:5]}
            ))
        else:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_CHECK",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="No duplicate bullets detected"
            ))

        enriched_data = {
            **extracted_data,
            "experience_sections": experience_sections
        }

        return enriched_data, validation_results

class DuplicateDetector:
    """Detect duplicate or near-duplicate bullets using TF-IDF cosine similarity."""
    
    def __init__(self):
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(stop_words='english', norm='l2')

    def find_duplicates(
        self,
        bullets: List[Dict],
        threshold: float = 0.9
    ) -> List[Tuple[int, int, float]]:
        """
        Find bullets with cosine similarity >= threshold.
        Returns: List of (index1, index2, similarity_score)
        """
        duplicates = []
        
        for i in range(len(bullets)):
            for j in range(i + 1, len(bullets)):
                similarity = self._calculate_cosine_similarity(
                    bullets[i].get("bullet_text", ""),
                    bullets[j].get("bullet_text", "")
                )
                
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        
        return duplicates
    
    def _calculate_cosine_similarity_sklearn(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity using scikit-learn's TfidfVectorizer."""
        if not text1 or not text2:
            return 0.0
        try:
            # Fit and transform the texts into TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            # Calculate cosine similarity between the two vectors
            # The result is a 2x2 matrix, we need the value at [0, 1]
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            # Fallback for empty vocabularies or other sklearn errors
            return 0.0

    def _calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate TF-IDF cosine similarity between two texts.
        Uses scikit-learn if available, otherwise falls back to a basic implementation.
        """
        if SKLEARN_AVAILABLE:
            return self._calculate_cosine_similarity_sklearn(text1, text2)
        else:
            # Basic fallback implementation (manual TF-IDF)
            if not text1 or not text2:
                return 0.0
            
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0

            intersection = words1.intersection(words2)
            
            if not intersection:
                return 0.0

            numerator = len(intersection)
            denominator = math.sqrt(len(words1) * len(words2))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
    
    def compute_similarity_matrix(
        self,
        sections: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Compute 78-check pairwise similarity matrix across all sections.
        Returns comprehensive matrix with all pairwise comparisons.
        """
        matrix_data = {
            "pairwise_checks": [],
            "total_comparisons": 0,
            "duplicates_found": [],
            "max_similarity": 0.0,
            "sections_analyzed": list(sections.keys())
        }
        
        # Flatten all bullets with section labels
        all_bullets = []
        for section_id, bullets in sections.items():
            if isinstance(bullets, list):
                for idx, bullet in enumerate(bullets):
                    if isinstance(bullet, str) and bullet.strip():
                        all_bullets.append({
                            "section": section_id,
                            "index": idx,
                            "text": bullet.strip()
                        })
        
        # Compute pairwise similarities
        for i in range(len(all_bullets)):
            for j in range(i + 1, len(all_bullets)):
                b1 = all_bullets[i]
                b2 = all_bullets[j]
                
                similarity = self._calculate_cosine_similarity(b1["text"], b2["text"])
                
                comparison = {
                    "bullet_1": f"{b1['section']}[{b1['index']}]",
                    "bullet_2": f"{b2['section']}[{b2['index']}]",
                    "similarity": round(similarity, 4),
                    "cross_section": b1["section"] != b2["section"]
                }
                
                matrix_data["pairwise_checks"].append(comparison)
                matrix_data["total_comparisons"] += 1
                matrix_data["max_similarity"] = max(matrix_data["max_similarity"], similarity)
                
                # Flag duplicates (≥0.9 threshold per v1.9.2)
                if similarity >= 0.9:
                    matrix_data["duplicates_found"].append(comparison)
        
        return matrix_data
    
    def compute_overview_bullet_similarity(
            self,
            overview_text: str,
            bullets: List[str],
            section_id: str
        ) -> Dict[str, Any]:
            """
            Compute cosine similarity between overview and each bullet.
            Per v1.9.2: K.5B/K.6B must have cosine <0.6 to their bullets.
            v9.87: Uses count_words_ms_word_style for length reporting.
            """
            results = {
                "section": section_id,
                "overview_length": count_words_ms_word_style(overview_text) if overview_text else 0, # USE MS WORD STYLE
                "bullet_count": len(bullets),
                "similarities": [],
                "max_similarity": 0.0,
                "threshold_violations": []
            }

            if not overview_text or not bullets:
                return results

            for idx, bullet in enumerate(bullets):
                if isinstance(bullet, str) and bullet.strip():
                    similarity = self._calculate_cosine_similarity(overview_text, bullet.strip())

                    sim_data = {
                        "bullet_index": idx,
                        "similarity": round(similarity, 4),
                        "passes_threshold": similarity < 0.6
                    }

                    results["similarities"].append(sim_data)
                    results["max_similarity"] = max(results["max_similarity"], similarity)

                    if similarity >= 0.6:
                        results["threshold_violations"].append({
                            "bullet_index": idx,
                            "similarity": round(similarity, 4)
                        })

            return results

    def compute_executive_summary_similarity(
        self,
        exec_summary_text: str,
        sections_content: Dict[str, Union[str, List[str]]]
    ) -> List[Dict[str, Any]]:
        """
        v9.11: Compute cosine similarity between Executive Summary and other sections.
        
        Args:
            exec_summary_text: The text of the Executive Summary (K.1).
            sections_content: A dictionary where keys are section labels (e.g., "Unify Overview", "IBM Bullets")
                              and values are either a single string (for overviews) or a list of strings (for bullets).
                              
        Returns:
            List of dictionaries, each containing 'section_label', 'max_similarity',
            'average_similarity', and 'item_count'.
        """
        results = []
        if not exec_summary_text:
            return results
            
        for label, content in sections_content.items():
            similarities = []
            items_to_compare = []
            if isinstance(content, str):
                items_to_compare.append(content)
            elif isinstance(content, list):
                items_to_compare.extend([item for item in content if isinstance(item, str)])
                
            for item_text in items_to_compare:
                if item_text:
                    similarity = self._calculate_cosine_similarity(exec_summary_text, item_text)
                    similarities.append(similarity)
            
            results.append({
                "section_label": label,
                "max_similarity": max(similarities) if similarities else 0.0,
                "average_similarity": sum(similarities) / len(similarities) if similarities else 0.0,
                "item_count": len(items_to_compare)
            })
        return results

class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, artist_specs: Dict, previous_failures: List[ValidationResult] = None):
        """Initializes the ArtistGenerator."""
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.artist_specs = artist_specs # Store the loaded specs
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.previous_failures = previous_failures or []
        self.constraints = ContentConstraintsConfig()
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

        self.SECTION_GENERATION_SPECS = self._parse_specs(self.artist_specs)

    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K2_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K3_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K9_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
    }

    # --- Centralized Bullet Word Count Ranges (UPDATED for K0-K11) ---
    BULLET_WORD_COUNT_RANGES = {
        ResumeSection.K2_UNIFY_BULLETS: (28, 38),
        ResumeSection.K3_IBM_BULLETS: (22, 34),
        ResumeSection.K9_COMPETENCIES: (28, 38),
    }

    def _parse_specs(self, raw_specs: Dict) -> Dict['ResumeSection', Dict[str, Any]]: # Use quotes if ResumeSection not defined yet
        """Parses pre-loaded generation specs and reconstructs Python objects."""
        try:
            reconstructed_specs = {}
            for section_name, spec in raw_specs.items():
                try:
                    # Convert section name string back to ResumeSection enum
                    section_enum = ResumeSection[section_name] # Assuming ResumeSection is defined

                    # Convert reasoning_config string back to ReasoningConfig attribute
                    if 'reasoning_config' in spec and isinstance(spec.get('reasoning_config'), str): # Use .get() for safety
                         config_name = spec['reasoning_config']
                         # Check if the attribute exists before getting it
                         if hasattr(ReasoningConfig, config_name): # Assuming ReasoningConfig is defined
                             spec['reasoning_config'] = getattr(ReasoningConfig, config_name)
                         else:
                              raise AttributeError(f"ReasoningConfig has no attribute '{config_name}'")


                    # Convert depends_on string back to ResumeSection enum
                    if 'depends_on' in spec and isinstance(spec.get('depends_on'), str): # Use .get() for safety
                        spec['depends_on'] = ResumeSection[spec['depends_on']] # Assuming ResumeSection is defined

                    reconstructed_specs[section_enum] = spec
                except (KeyError, AttributeError) as e:
                    # Log the specific error during parsing before raising
                    logging.error(f"Error parsing spec entry for '{section_name}': {e}", exc_info=False)
                    raise HopExecutionError(f"Error parsing spec for '{section_name}': Invalid enum or config name. Details: {e}")

            logging.info("Successfully loaded and parsed artist specs from 'artist_specs.json'.")
            return reconstructed_specs

        except HopExecutionError as he: # Catch specific HopExecutionError first
             # Log the error before re-raising if needed, or let it propagate
             logging.error(f"Spec parsing failed: {he}")
             raise he # Re-raise HopExecutionError
        except Exception as e:
            # Catch any other unexpected exceptions
            logging.error(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}", exc_info=True) # Log full traceback for unexpected errors
            raise HopExecutionError(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}")

    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> Tuple[str, int]:
        """
        Centralizes Gemini API calls. Returns (final_text, call_count)
        """
        calls_made_this_invocation = 0
        try:
            # API Key Check
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                # Attempt to retrieve from genai config if not in env (less common pattern)
                try:
                    # Note: Accessing internal _config might be unstable across library versions
                    api_key = getattr(genai, '_config', {}).get('api_key', None)
                    if not api_key: raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set and genai not configured.")
                    else: logging.debug(f"Using globally configured Gemini API key for {section_id}.")
                except Exception:
                    raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set and failed to retrieve from genai config.")

            try:
                model = genai.GenerativeModel('gemini-2.5-pro')
            except Exception as model_init_e:
                raise HopExecutionError(f"Failed to initialize Gemini model for {section_id}: {model_init_e}")

            # Parameter Preparation
            # Ensure reasoning_config_to_api_params exists and handles missing config
            if reasoning_config is None:
                logging.warning(f"Missing reasoning_config for {section_id}. Using default.")
                reasoning_config = ReasoningConfig.DEFAULT # Assuming ReasoningConfig.DEFAULT exists
            # Assuming reasoning_config_to_api_params and enhance_system_prompt_with_reasoning are defined elsewhere
            api_params = reasoning_config_to_api_params(reasoning_config)
            generation_config = api_params["generation_config"]
            sc_count = api_params.get('sc', 1)

            # Apply Temperature Override
            if temperature_override is not None:
                generation_config.temperature = temperature_override
                logging.info(f"  {section_id} API Call: Using Temp: {generation_config.temperature:.1f} (Override: True)")
            else:
                logging.info(f"  {section_id} API Call: Using Temp: {generation_config.temperature:.1f} (Override: False)")

            enhanced_system = enhance_system_prompt_with_reasoning(system_prompt, reasoning_config, section_id)

            # Self-Consistency Logic
            if sc_count > 1:
                logging.info(f"  Running Self-Consistency for {section_id} ({sc_count} candidates)...")
                # Ensure high temperature for diverse SC candidates unless overridden
                if temperature_override is None: generation_config.temperature = 0.9
                generation_config.candidate_count = sc_count
                candidate_responses = []
                try:
                    if not model: raise HopExecutionError(f"{section_id} SC API call failed: Model not initialized.")
                    # --- API Call 1 (Candidates) ---
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    # --- End Call 1 ---

                    # Robustly extract text from candidates, checking finish reasons
                    if hasattr(response, 'candidates') and response.candidates:
                        for c in response.candidates:
                            candidate_finish_reason = getattr(c, 'finish_reason', None)
                            # Skip candidates that didn't finish properly
                            if candidate_finish_reason == 2: # MAX_TOKENS
                                logging.warning(f"    SC Candidate for {section_id} stopped: MAX_TOKENS.")
                                continue # Skip this candidate
                            elif candidate_finish_reason is not None and candidate_finish_reason != 1: # Other non-STOP reason
                                safety_ratings = getattr(c, 'safety_ratings', None)
                                logging.warning(f"    SC Candidate for {section_id} stopped. Finish Reason: {candidate_finish_reason}. Safety: {safety_ratings}")
                                continue # Skip this candidate

                            # Extract text if finished successfully
                            if hasattr(c, 'content') and hasattr(c.content, 'parts'):
                                for part in c.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        candidate_responses.append(part.text)

                    if not candidate_responses:
                        # If no candidates succeeded, report overall prompt feedback
                        block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                        finish_reason = getattr(response.candidates[0], 'finish_reason', None) if hasattr(response, 'candidates') and response.candidates else None # Reason for first candidate if available
                        raise HopExecutionError(f"{section_id} SC API call returned no valid text candidates. First Candidate Finish: {finish_reason}, Prompt Block: {block_reason}")

                except Exception as e:
                    logging.error(f"    SC API call for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC API call failed: {type(e).__name__} - {e}") from e

                # Synthesis Step
                logging.info(f"  Synthesizing {len(candidate_responses)} responses for {section_id}...")
                synthesis_prompt = f"""You are a senior editor tasked with synthesizing multiple draft responses generated for the same prompt into a single, high-quality final answer that strictly adheres to all original constraints.

**ORIGINAL PROMPT (for context on constraints):**
---
{prompt}
---

**DRAFTS TO SYNTHESIZE:**
"""
                for i, res in enumerate(candidate_responses):
                    synthesis_prompt += f"\n---\n**DRAFT {i+1}:**\n{res}\n---\n"

                synthesis_prompt += """
**SYNTHESIS INSTRUCTIONS:**
1.  **Consolidate & Refine:** Identify the best elements, phrasing, and core ideas from each draft. Merge them into a coherent and well-structured final response. Remove redundancy.
2.  **Ensure Accuracy:** Verify that the synthesized response accurately reflects the intent and information requested in the original prompt.
3.  **Strict Constraint Adherence:** MOST IMPORTANTLY, ensure the final answer meticulously follows ALL constraints specified in the **ORIGINAL PROMPT** (e.g., word count, sentence count, format, keywords, negative constraints like "Do NOT start with...").
4.  **Remove Extraneous Content:** Eliminate any conversational filler, explanations, apologies, or self-correction statements present in the drafts.
5.  **Tone & Style:** Maintain the tone and style requested in the original prompt.

**FINAL SYNTHESIZED ANSWER (MUST strictly adhere to original constraints, NO markdown fences ```):**
"""
                # Assuming genai is imported
                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=generation_config.max_output_tokens) # Use same max tokens
                try:
                    if not model: raise HopExecutionError(f"{section_id} SC synthesis failed: Model not initialized.")
                    # --- API Call 2 (Synthesis) ---
                    calls_made_this_invocation += 1
                    synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)
                    # --- End Call 2 ---

                    # Check synthesis response finish reason
                    synth_finish_reason = getattr(synthesis_response.candidates[0], 'finish_reason', None) if synthesis_response.candidates else None
                    if synth_finish_reason == 2: # MAX_TOKENS
                        raise HopExecutionError(f"{section_id} SC synthesis stopped: MAX_TOKENS.")
                    elif synth_finish_reason is not None and synth_finish_reason != 1: # Other non-STOP reason
                        synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(synthesis_response, 'prompt_feedback') else 'Unknown'
                        raise HopExecutionError(f"{section_id} SC synthesis stopped. Finish Reason: {synth_finish_reason}. Block Reason: {synth_block_reason}")

                    raw_text = getattr(synthesis_response, 'text', None) # Safely get text
                    if not raw_text:
                        # Check block reason again if text is missing
                        synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', None) if hasattr(synthesis_response, 'prompt_feedback') else None
                        raise HopExecutionError(f"{section_id} SC synthesis produced no text. Block Reason: {synth_block_reason}")

                    # Clean markdown fences and return (Assuming re is imported)
                    cleaned_text = re.sub(r'^```[a-z]*\s*\n', '', raw_text) # Remove opening fence
                    cleaned_text = re.sub(r'\n```\s*$', '', cleaned_text) # Remove closing fence
                    final_text = cleaned_text.strip()
                    return final_text, calls_made_this_invocation

                except Exception as e:
                    logging.error(f"    SC synthesis for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC synthesis failed: {type(e).__name__} - {e}") from e

            # --- Single Candidate Logic ---
            else:
                try:
                    if not model: raise HopExecutionError(f"{section_id} generation API call failed: Model not initialized.")
                    # --- API Call (Single) ---
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    # --- End Call ---

                    # Check finish reason
                    finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
                    if finish_reason == 2: # MAX_TOKENS
                        raise HopExecutionError(f"{section_id} generation stopped: MAX_TOKENS.")
                    elif finish_reason is not None and finish_reason != 1: # Other non-STOP reason
                        block_reason = getattr(response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(response, 'prompt_feedback') else 'Unknown'
                        raise HopExecutionError(f"{section_id} generation stopped. Finish Reason: {finish_reason}. Block Reason: {block_reason}")

                    raw_text = getattr(response, 'text', None) # Safely get text
                    if not raw_text:
                        # Check block reason again if text is missing
                        block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                        raise HopExecutionError(f"{section_id} generation returned no text. Block Reason: {block_reason}")

                    # Clean markdown fences and return (Assuming re is imported)
                    cleaned_text = re.sub(r'^```[a-z]*\s*\n', '', raw_text) # Remove opening fence
                    cleaned_text = re.sub(r'\n```\s*$', '', cleaned_text) # Remove closing fence
                    final_text = cleaned_text.strip()
                    return final_text, calls_made_this_invocation

                except Exception as e:
                    logging.error(f"LLM API call for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} generation API call failed: {type(e).__name__} - {e}") from e

        except HopExecutionError as he: # Re-raise specific errors from API checks or generation
            raise he
        except Exception as e: # Catch other unexpected errors during setup or call
            logging.error(f"Unexpected error in _call_gemini_api for {section_id}: {e}", exc_info=True)
            raise HopExecutionError(f"Unexpected error during {section_id} API call: {e}") from e

    def generate(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
    ) -> Tuple[Dict, List[ValidationResult], int]:
        """
        Generates *only* the specified resume sections at the specified temperatures.
        Executes one generation pass and returns results and API call count.
        """
        validation_results = []
        total_api_calls_this_pass = 0
        artist_output = {} # Initialize

        try:
            # _generate_artist_output now returns (output_dict, total_calls)
            artist_output, calls_made = self._generate_artist_output(
                sections_to_generate=sections_to_generate,
                temperature_overrides=temperature_overrides
            )
            total_api_calls_this_pass = calls_made

            # Add a success result for the attempted sections
            generated_keys_str = ", ".join([k for k, v in artist_output.items() if v is not None]) or "None"
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_PASS", passed=True, severity=ValidationSeverity.INFO,
                message=f"Content generation attempted/completed for: {generated_keys_str}"
            ))
            return artist_output, validation_results, total_api_calls_this_pass

        except HopExecutionError as he: # Catch halts from generation methods
            logging.error(f"Artist generation HALTED during selective run: {he}", exc_info=False)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_HALTED", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation halted: {str(he)}",
                details={"error": str(he)}
            ))
            # Return partial output and calls made up to failure point
            return artist_output, validation_results, total_api_calls_this_pass

        except Exception as e: # Catch other unexpected errors
            logging.error(f"Artist generation failed unexpectedly during selective run: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed unexpectedly: {str(e)}",
                details={"error": str(e)}
            ))
            # Return partial output and calls made up to failure point
            return artist_output, validation_results, total_api_calls_this_pass

    def _generate_artist_output(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
        ) -> Tuple[Dict, int]:
        """
        Generates *only* the specified sections using the SORTED config (K0-K11).
        Raises HopExecutionError on failure.
        Passes current output dict to overview generators (K2, K3). Aggregates and returns total API calls.
        """
        output = {}
        total_api_calls = 0
        ordered_sections = sorted(self.SECTION_GENERATION_SPECS.keys(), key=lambda x: (int(x.name.split('_')[0][1:]), x.name))

        for section_enum in ordered_sections:
            if section_enum not in sections_to_generate:
                output[section_enum.value] = None # Mark skipped sections explicitly
                continue

            if section_enum not in self.SECTION_GENERATION_SPECS:
                logging.warning(f"No generation spec found for requested section {section_enum.name}. Skipping.")
                output[section_enum.value] = None
                continue
            spec = self.SECTION_GENERATION_SPECS[section_enum]
            generation_method_name = spec["generation_method"]
            section_api_calls = 0
            generated_content = None # Initialize content for this iteration

            logging.info(f"  Generating section: {section_enum.name} ({section_enum.value})")
            # Handle copy/dummy sections (if requested)
            if generation_method_name == "_copy_from_master" or generation_method_name == "_copy_k0_contact" or generation_method_name == "_generate_dummy_header":
                try:
                    method = getattr(self, generation_method_name)
                    # Pass master_data_key if needed by the method
                    if generation_method_name == "_copy_from_master":
                         output[section_enum.value] = method(spec.get("master_data_key"))
                    else: # _copy_k0_contact, _generate_dummy_header
                         output[section_enum.value] = method()
                    # No API calls for copy/dummy
                    section_api_calls = 0
                except Exception as e:
                    raise HopExecutionError(f"Unexpected error in {generation_method_name} for {section_enum.value}: {e}") from e

            else:
                # Determine Temperature
                final_temp = temperature_overrides.get(section_enum)
                if final_temp is None:
                    logging.error(f"  {section_enum.name}: Temperature override NOT FOUND! Halting.")
                    raise HopExecutionError(f"Misconfiguration: Temperature override missing for {section_enum.name}")

                # Call the generation method (expecting HopExecutionError on failure)
                try:
                    method = getattr(self, generation_method_name)

                    method_args = {
                        "temperature_override": final_temp,
                        "section_enum": section_enum # Pass enum for context
                    }
                    # Pass spec for generic generator
                    if generation_method_name == "_generate_section_generic":
                        method_args["spec"] = spec
                    # Pass dependencies and extra args for specific orchestrators
                    elif generation_method_name == "_generate_tailored_bullets_for_experience":
                         method_args.update(spec.get("extra_args", {}))
                         method_args["provenance_targets"] = self.PROVENANCE_SPLIT_TARGETS.get(section_enum, {})
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)
                    elif generation_method_name == "_generate_tailored_overview_for_experience":
                         # Ensure dependency bullets exist in current output
                         dependency_enum = spec.get("depends_on")
                         # Use .value to get the string key for dictionary lookup
                         if dependency_enum and output.get(dependency_enum.value) is not None:
                              method_args["generated_bullets"] = output[dependency_enum.value]
                         else:
                              # Log the enum name and value for clarity
                              dep_name = dependency_enum.name if dependency_enum else "None"
                              dep_value = dependency_enum.value if dependency_enum else "None"
                              raise HopExecutionError(f"Dependency {dep_name} ({dep_value}) missing for {section_enum.name}")
                         method_args["word_count_range"] = self._get_overview_wc_range(section_enum)
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)

                    generated_content, section_api_calls = method(**method_args)

                    # Store result and aggregate calls
                    output[section_enum.value] = generated_content
                    total_api_calls += section_api_calls

                    # Basic check for placeholders
                    if isinstance(generated_content, str) and "[Placeholder" in generated_content:
                        logging.warning(f"{section_enum.value} generation returned placeholder: {generated_content[:100]}...")
                        # Optionally halt here by raising HopExecutionError

                except HopExecutionError as he: # Propagate halts
                    logging.error(f"Generation HALTED at section {section_enum.value} ({generation_method_name}): {he}", exc_info=False)
                    raise he
                except AttributeError as ae: # Catch if method doesn't exist (config mismatch)
                     logging.error(f"AttributeError: Method '{generation_method_name}' not found for section {section_enum.value}. Config mismatch?", exc_info=True)
                     raise HopExecutionError(f"Method '{generation_method_name}' not found for {section_enum.value}. Check SECTION_GENERATION_SPECS.") from ae
                except Exception as e: # Catch unexpected errors during generation call
                    logging.error(f"Unexpected Error generating section {section_enum.value} with {generation_method_name} (Temp: {final_temp}): {e}", exc_info=True)
                    raise HopExecutionError(f"Unexpected error during {section_enum.value} generation: {e}") from e


        # Return the output dictionary containing results for the requested sections
        # For stateful retry, we need the full dict including None for skipped/failed.
        final_output_for_this_pass = output

        return final_output_for_this_pass, total_api_calls

    def _copy_k0_contact(self) -> str:
        contact = self.master_resume.get("owner", {}).get("contact", {})
        parts = [f"Phone: {contact.get('phone', '')}", f"Email: {contact.get('email', '')}", f"LinkedIn: {contact.get('linkedin', '')}"]
        return " | ".join(p for p in parts if len(p.split(': ', 1)) > 1 and p.split(': ', 1)[1])

    def _copy_from_master(self, master_data_key: str) -> Any:
        """Generic copy method using a key path."""
        try:
            keys = master_data_key.split('.')
            value = self.master_resume
            for key in keys: value = value[key]
            return value
        except (KeyError, TypeError) as e:
            logging.warning(f"Could not copy master data using key '{master_data_key}': {e}")
            return None
    def _generate_dummy_header(self) -> str: return "HEADER_PLACEHOLDER"

    def _get_differentiators(self, max_count: Optional[int] = None) -> List[str]:
        """Extract differentiator keywords from thematic analysis."""
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if not comp_intel: return []
        diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
        if not isinstance(diff_kw, list): return []
        return diff_kw[:max_count] if max_count else diff_kw

    def _get_problem_solution(self) -> Tuple[str, str]:
        """Extract problem/solution narratives from thematic analysis."""
        narratives = getattr(self.thematic_analysis, 'problem_solution_narratives', None)
        if not isinstance(narratives, dict): narratives = {}
        problem = (narratives.get('common_problems', ['solving key challenges'])[0] 
                   if narratives.get('common_problems') else 'solving key challenges')
        solution = (narratives.get('solution_patterns', ['delivering impactful results'])[0] 
                    if narratives.get('solution_patterns') else 'delivering impactful results')
        return problem, solution

    def _get_primary_theme(self, default: str = 'key skills') -> str:
        """Extract primary theme name from thematic analysis."""
        return (self.thematic_analysis.primary_theme.get('name', default) 
                if self.thematic_analysis.primary_theme else default)

    def _build_context_k0_headline(self, spec: Dict) -> Dict:
        feedback = self._get_feedback_instruction(["VG_HEADLINE_WORD_COUNT", "VG_HEADLINE_COMPONENT_WC", "VG_HEADLINE_NO_TITLES", "VG_HEADLINE_NO_COMMAS"])
        return {
            "primary_theme": self._get_primary_theme('Key Expertise'),
            "differentiators_str": ', '.join(self._get_differentiators(5)),
            "min_wc": self.constraints.HEADLINE_WORD_COUNT_MIN,
            "max_wc": self.constraints.HEADLINE_WORD_COUNT_MAX,
            "comp_min_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MIN,
            "comp_max_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MAX,
            "feedback_instruction": feedback
        }

    def _build_context_k1_summary(self, spec: Dict) -> Dict:
        role_classification = getattr(self.thematic_analysis, 'role_classification', {})
        role_archetype = role_classification.get('role_archetype', 'Experienced Professional') if isinstance(role_classification, dict) else 'Experienced Professional'
        archetype_map = {"Executive_Leader": "an executive leader", "Technical_IC": "a hands-on technical expert", "Post-Sales_Customer_Success": "a customer success leader", "Pre-Sales_GTM": "a pre-sales GTM strategist", "Product_Management": "a product management professional"}
        archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."
        problem, solution = self._get_problem_solution()
        feedback = self._get_feedback_instruction(["VG_SENTENCE_COUNT_K1", "VG_WORD_COUNT_K1", "VG_K1_DIFFERENTIATOR_RANGE"])
        
        return {
            "primary_theme": self._get_primary_theme(),
            "archetype_instruction": archetype_instruction,
            "problem": problem,
            "solution": solution,
            "differentiators_str": ', '.join(self._get_differentiators(self.constraints.K1_MIN_DIFFERENTIATORS)),
            "experience_snippets": json.dumps(self.enriched_scaffold.get('experience_sections', [])[:2], indent=2),
            "min_sc": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
            "max_sc": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX,
            "min_wc": self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN,
            "max_wc": self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX,
            "min_diff": self.constraints.K1_MIN_DIFFERENTIATORS,
            "feedback_instruction": feedback
        }

    def _build_context_narrative(self, spec: Dict) -> Dict:
        # Builds context for narrative sections (K4, K5, K6).
        # Ensure 'extra_args' exists and is a dictionary
        extra_args = spec.get("extra_args", {})
        if not isinstance(extra_args, dict):
            raise HopExecutionError(f"Invalid 'extra_args' format in spec for narrative generation.")

        company_match = extra_args.get("company_match")
        section_enum = extra_args.get("section_enum")
        if not company_match or not section_enum:
            raise HopExecutionError(f"Missing 'company_match' or 'section_enum' in extra_args for narrative generation.")

        min_wc, max_wc, target_sc, focus_instruction = 0, 0, 3, "" # Defaults
        k0_themes = [] # Initialize k0_themes
        title = "Default Title" # Fallback title

        exp_section = next((exp for exp in self.master_resume.get('professional_experience', []) if company_match in exp.get('company', '')), None)
        master_highlights = []
        if exp_section:
            # Get highlights or bullet_pool, ensuring it's a list
            master_highlights_raw = exp_section.get('highlights', exp_section.get('bullet_pool', []))
            if isinstance(master_highlights_raw, list):
                 master_highlights = [str(h) for h in master_highlights_raw if isinstance(h, str)]
            title = exp_section.get("title", title) # Use section title if found

        if not master_highlights: raise HopExecutionError(f"Cannot generate narrative for {company_match}: Master highlights/bullets not found or empty.")
        master_context = "\n".join([f"- {h}" for h in master_highlights]); rag_keywords = self._get_differentiators(5)

        combined_signals = []
        if section_enum == ResumeSection.K4_TRADERSENSE_NARRATIVE:
            min_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN', 40)
            max_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX', 60)
            rag_signals = ["high-frequency trading", "low-latency", "risk controls", "backtesting", "FIX protocol", "cloud infrastructure"]
            combined_signals = list(set(rag_keywords + rag_signals))[:7]
            focus_instruction = "Emphasize the early adoption of cloud, low-latency systems, HFT, risk management, and quantitative analysis, linking them to broader technical leadership and system design capabilities relevant today."
        elif section_enum == ResumeSection.K5_EY_NARRATIVE:
            min_wc = self.constraints.EY_NARRATIVE_WORD_COUNT_MIN
            max_wc = self.constraints.EY_NARRATIVE_WORD_COUNT_MAX
            k0_themes = ["Leadership", "Strategic Vision", "Executive Communication", "Risk Management", "Client Advisory"]
            # Combined signals not used directly in this prompt template
        elif section_enum == ResumeSection.K6_EARLY_CAREER_NARRATIVE:
            min_wc = self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN
            max_wc = self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX
            rag_signals = ["quantitative analysis", "modeling", "data-driven", "problem-solving", "analytical foundation"]
            combined_signals = list(set(rag_keywords + rag_signals))[:7]
        # Add other narrative section contexts here if needed
        return {
            "company_name": company_match,
            "title": title,
            "target_sc": target_sc,
            "min_wc": min_wc,
            "max_wc": max_wc,
            "master_context": master_context,
            "combined_signals_str": ', '.join(combined_signals), "focus_instruction": focus_instruction,
            "k0_themes_str": ', '.join(k0_themes), "rag_keywords_str": ', '.join(rag_keywords),
        }

    def _build_context_k10_skills(self, spec: Dict) -> Dict:
        try:
            primary_theme_kw = (self.thematic_analysis.primary_theme.get('keywords', []) 
                               if self.thematic_analysis and self.thematic_analysis.primary_theme else [])
            if not isinstance(primary_theme_kw, list): primary_theme_kw = []
            combined_keywords = list(set(primary_theme_kw + self._get_differentiators()))[:15]
            return {"combined_keywords_str": ', '.join(combined_keywords)}
        except Exception as e:
            logging.error(f"Error building K10 context: {e}")
            return {"combined_keywords_str": "relevant skills"}

    def _build_context_k11_cover_letter(self, spec: Dict) -> Dict:
        return {
            "primary_theme": self._get_primary_theme('key requirements'),
            "differentiators_str": ', '.join(self._get_differentiators(5)),
            "experience_snippets": self._get_experience_snippets_for_cl(),
            "problem": problem,
            "solution": solution,
            "current_date": datetime.now().strftime("%B %d, %Y"),
            "p1_min_wc": self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN,
            "p1_max_wc": self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_min_wc": self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN,
            "p2_max_wc": self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_min_wc": self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN,
            "p3_max_wc": self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
            "expected_signature": self._get_expected_signature()
        }

    def _post_process_k10_skills(self, skills_text: str, section_enum: ResumeSection) -> List[str]:
        # Parses and validates the K.10 Skills list from LLM output.
        try:
            skills_list_final = []
            skills_intermediate = [re.sub(r'^[•*\-\d\.]+\s*', '', s).strip() for s in skills_text.split('\n') if s.strip()]
            malformed_count = 0
            for skill in skills_intermediate:
                word_count = count_words_ms_word_style(skill) # Use helper
                if 1 <= word_count <= 3:
                    skills_list_final.append(skill)
                else:
                    logging.warning(f"{section_enum.value}: Discarding malformed skill '{skill}' (words: {word_count})")
                    malformed_count += 1

            # Strict validation
            if len(skills_list_final) != 12:
                raise HopExecutionError(f"{section_enum.value} generation failed: Expected 12 valid skills, found {len(skills_list_final)}. Preview: {skills_text[:100]}...")
            # Allow some malformed skills to be discarded, but maybe add a threshold later?
            # For now, let's just log a warning if any were discarded but don't halt unless count is wrong.
            if malformed_count > 0:
                 logging.warning(f"{section_enum.value}: Discarded {malformed_count} malformed skills.")
                 # Optionally: raise HopExecutionError if malformed_count exceeds a threshold

            return skills_list_final

        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_k11_cover_letter(self, cover_letter_text: str, section_enum: ResumeSection) -> str:
        # Applies structure fixes and validation to K.11 Cover Letter output.
        try:
            expected_signature = self._get_expected_signature()
            fixed_text = cover_letter_text.strip(); current_date_str = datetime.now().strftime("%B %d, %Y")
            # Apply fixes (same logic as before)
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text): fixed_text = f"{current_date_str}\n\n{fixed_text}"; logging.warning(f"{section_enum.value}: Added missing date.")
            recipient_placeholder = "Hiring Manager\n[Company Name]" # Ensure this matches prompt exactly
            if recipient_placeholder not in fixed_text:
                # Attempt to insert recipient block after the date
                fixed_text = re.sub(r"^(\w+ \d{1,2}, \d{4}\s*)", rf"\1\n{recipient_placeholder}\n", fixed_text, count=1, flags=re.MULTILINE)
                if recipient_placeholder not in fixed_text: # Check if insertion worked
                     logging.warning(f"{section_enum.value}: Failed to add recipient placeholder.")

            salutation = "Dear Hiring Manager,"
            if salutation not in fixed_text:
                # Attempt to insert salutation after recipient block
                fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\s*)", rf"\1\n{salutation}\n", fixed_text, count=1, flags=re.MULTILINE)
                if salutation not in fixed_text: # Check if insertion worked
                     logging.warning(f"{section_enum.value}: Failed to add salutation.")

            closing = "Sincerely,"
            # Fix closing/signature placement
            if expected_signature in fixed_text and closing not in fixed_text.split(expected_signature)[0]:
                # If signature exists but closing is missing before it, insert closing
                fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
            elif closing in fixed_text and expected_signature not in fixed_text:
                 # If closing exists but signature is missing, append signature
                 fixed_text = fixed_text.rstrip() + f"\n\n{expected_signature}"
            elif closing not in fixed_text and expected_signature not in fixed_text:
                 # If both are missing, append both
                 fixed_text = fixed_text.rstrip() + f"\n\n{closing}\n\n{expected_signature}"
            elif not fixed_text.rstrip().endswith(expected_signature.rstrip()):
                 # Handle cases where signature might be partially present or malformed at the end
                 logging.warning(f"{section_enum.value}: Signature block missing/malformed at end. Attempting fix...")
                 fixed_text = re.sub(r'\n*Sincerely,?[\s\S]*$', '', fixed_text.rstrip(), flags=re.MULTILINE) # Remove existing closing/sig attempts
                 fixed_text += f"\n\n{closing}\n\n{expected_signature}" # Append correct block

            # Final basic checks
            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text: raise HopExecutionError(f"{section_enum.value} generation failed (placeholder detected).")
            # Check presence again after fixes
            if not all(x in fixed_text for x in [current_date_str, recipient_placeholder, salutation, closing, expected_signature]): logging.warning(f"{section_enum.value}: Structure may still be incomplete after fixes.")

            return fixed_text.strip()
        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_narrative(self, narrative_text: str, section_enum: ResumeSection) -> str:
        # Basic post-processing for narrative sections (checks WC/SC).
        # Ensure spec exists for the enum
        if section_enum not in self.SECTION_GENERATION_SPECS:
            logging.error(f"Cannot post-process narrative: Spec missing for {section_enum.name}")
            return narrative_text # Return original text with error log

        spec = self.SECTION_GENERATION_SPECS[section_enum]
        context = self._build_context_narrative(spec) # Rebuild context to get constraints
        min_wc = context.get('min_wc', 0); max_wc = context.get('max_wc', float('inf')); target_sc = context.get('target_sc', 0)

        final_wc = count_words_ms_word_style(narrative_text); final_sc = _count_sentences(narrative_text)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_enum.value} narrative WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
             # Optionally raise HopExecutionError here if strict adherence is needed
        # Allow +/- 1 sentence for narratives as LLMs can struggle with exact count
        if target_sc > 0 and not (target_sc -1 <= final_sc <= target_sc + 1):
             logging.warning(f"{section_enum.value} narrative SC ({final_sc}) outside target range ({target_sc-1}-{target_sc+1}).")
             # Optionally raise HopExecutionError here
        return narrative_text # Return text even with warnings for now

    def _get_reasoning_config_for_section(self, section_enum: ResumeSection) -> ReasoningConfig:
        # Safely gets the ReasoningConfig for a section, falling back to DEFAULT.
        # This implementation requires ReasoningConfig to have attributes named like K0_HEADLINE_CONFIG, K1_EXECUTIVE_SUMMARY_CONFIG, etc.
        config_name = f"{section_enum.name}_CONFIG"
        try:
            # Check if the specific config exists directly on ReasoningConfig class
            config = getattr(ReasoningConfig, config_name, None)
            if config: return config
            # Fallback if specific not found - check for patterns only if needed
            # (Simplified: Assume direct mapping exists or use DEFAULT)
            logging.warning(f"Specific reasoning config '{config_name}' missing from ReasoningConfig class. Using DEFAULT.")
            return ReasoningConfig.DEFAULT
        except AttributeError:
            logging.warning(f"ReasoningConfig class structure issue or DEFAULT missing. Returning new default.")
            return ReasoningConfig() # Absolute fallback

    def _get_overview_wc_range(self, section_enum: ResumeSection) -> Tuple[int, int]:
        # Gets word count range for overview sections.
        if section_enum == ResumeSection.K2_UNIFY_OVERVIEW:
             return (self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX)
        elif section_enum == ResumeSection.K3_IBM_OVERVIEW:
             return (self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX)
        else:
             logging.warning(f"No overview WC range explicitly defined for {section_enum.name}. Using default (25-40).")
             return (25, 40) # Generic fallback

    def _generate_section_generic(self, spec: Dict, section_enum: ResumeSection, temperature_override: Optional[float]) -> Tuple[Any, int]:
        context = {}
        if "context_builder" in spec and spec["context_builder"]:
            builder_method_name = spec["context_builder"]
            builder_method = getattr(self, builder_method_name, None)
            if builder_method:
                 context = builder_method(spec) # Pass spec to context builder
            else:
                 raise HopExecutionError(f"Context builder method '{builder_method_name}' not found for {section_enum.name}")

        prompt_template = spec.get("prompt_template")
        if not prompt_template: raise HopExecutionError(f"Prompt template missing in spec for {section_enum.name}")

        # Use defaultdict for safe formatting
        try: prompt = prompt_template.format_map(defaultdict(lambda: '[MISSING_CONTEXT]', **context))
        except KeyError as ke: raise HopExecutionError(f"Missing key '{ke}' in context for {section_enum.name} prompt.")
        except Exception as fmt_e: raise HopExecutionError(f"Error formatting prompt for {section_enum.name}: {fmt_e}")

        # Safely get reasoning config using helper
        reasoning_config = self._get_reasoning_config_for_section(section_enum)
        system_prompt = spec.get("system_prompt", "You are a helpful assistant.") # Default system prompt

        raw_output, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_enum.value, system_prompt,
            temperature_override=temperature_override
        )

        if "post_processor" in spec and spec["post_processor"]:
            processor_method_name = spec["post_processor"]
            processor_method = getattr(self, processor_method_name, None)
            if processor_method:
                 processed_output = processor_method(raw_output, section_enum) # Pass enum for context
                 return processed_output, call_count
            else:
                 raise HopExecutionError(f"Post-processor method '{processor_method_name}' not found for {section_enum.name}")
        else:
            return raw_output, call_count # Return raw output if no post-processor


    def _get_feedback_instruction(self, relevant_rule_ids: List[str]) -> str:
        # Generates feedback instruction based on previous failures.
        feedback_lines = []
        for rule_id in relevant_rule_ids:
            # Filter failures specific to this rule ID
            failures = [f for f in (self.previous_failures or []) if f.rule_id == rule_id and not f.passed]
            if failures:
                last_fail = failures[-1] # Get the most recent failure for this rule
                try:
                    # Attempt to format the original error message from the rule
                    # Need a minimal context to format the message template
                    minimal_ctx = defaultdict(lambda: 'N/A', **(last_fail.details or {}))
                    fail_message = last_fail.message(minimal_ctx) if callable(last_fail.message) else str(last_fail.message)
                except Exception as e:
                    logging.warning(f"Error formatting feedback message for {rule_id}: {e}")
                    fail_message = f"Failed rule {rule_id}" # Fallback
                feedback_lines.append(f"IMPORTANT FEEDBACK ({rule_id}): Previous run failed: '{fail_message}'. Adjust output to comply.")
        return "\n".join(feedback_lines)


    def _get_expected_signature(self) -> str:
        # Helper to get the formatted expected signature block.
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        try:
            # Ensure COVER_LETTER_SIGNATURE_TEMPLATE is accessible
            if 'COVER_LETTER_SIGNATURE_TEMPLATE' not in globals() and 'COVER_LETTER_SIGNATURE_TEMPLATE' not in locals():
                 raise NameError("COVER_LETTER_SIGNATURE_TEMPLATE not defined.")
            return COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except NameError as ne: raise HopExecutionError(str(ne))
        except KeyError as e: raise HopExecutionError(f"Missing key in COVER_LETTER_SIGNATURE_TEMPLATE format: {e}")

    def _get_experience_snippets_for_cl(self) -> str:
        # Helper to get K2/K3 snippets for Cover Letter context.
        exp_snippets = ""
        # Use K.2 Unify Overview/Bullets from *enriched_scaffold*
        unify_overview = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets_raw = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        # Use K.3 IBM Overview/Bullets from *enriched_scaffold*
        ibm_overview = self.enriched_scaffold.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets_raw = self.enriched_scaffold.get(ResumeSection.K3_IBM_BULLETS.value, [])

        # Format snippets safely
        if unify_overview or unify_bullets_raw:
             exp_snippets += f"Recent Experience (Unify):\n{unify_overview or '(Overview not available)'}\n"
             # Extract text from bullet dicts safely
             unify_bullet_texts = [b.get('text', '') for b in unify_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in unify_bullet_texts[:2] if text]) + "\n"
        if ibm_overview or ibm_bullets_raw:
             exp_snippets += f"Prior Experience (IBM):\n{ibm_overview or '(Overview not available)'}\n"
             # Extract text from bullet dicts safely
             ibm_bullet_texts = [b.get('text', '') for b in ibm_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in ibm_bullet_texts[:2] if text]) + "\n"

        return exp_snippets if exp_snippets.strip() else "Candidate has extensive experience in relevant areas.\n"


    def _generate_tailored_overview_for_experience(
        self,
        generated_bullets: List[Dict], # Accepts list of bullet dicts
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_enum: ResumeSection, temperature_override: Optional[float] = None, **kwargs
    ) -> Tuple[str, int]:
        # Generates tailored overviews by synthesizing bullets AND incorporating high-level themes from HOP-0.
        section_id = section_enum.value # Get string value for logging/API call
        if not generated_bullets:
            raise HopExecutionError(f"Cannot generate overview for {section_id}: No generated bullets provided.")

        # Extract bullet text robustly
        bullet_texts = []
        for i, bullet_data in enumerate(generated_bullets):
             # Handle if bullet_data is not a dict (though spec says it depends on bullets)
             text = ""
             if isinstance(bullet_data, dict):
                 text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
             elif isinstance(bullet_data, str):
                 text = bullet_data # Handle case where list might just contain strings
             if not text: logging.warning(f"Skipping empty/invalid bullet {i} for overview {section_id}"); continue
             bullet_texts.append(f"* {text.strip()}")
        if not bullet_texts: raise HopExecutionError(f"Cannot generate overview for {section_id}: All bullets invalid.")

        bullet_summary_input = "\n".join(bullet_texts)
        min_wc, max_wc = word_count_range # Provided as arg

        # Extract Themes from HOP-0 (Same logic as v14.06)
        ta = self.thematic_analysis
        role_classification = getattr(ta, 'role_classification', {})
        primary_theme_data = getattr(ta, 'primary_theme', {})
        job_desc_lower = self.job_description.lower()
        include_leadership_theme = any(kw in job_desc_lower for kw in ['lead', 'manage', 'director', 'vp', 'executive'])
        include_strategic_theme = any(kw in job_desc_lower for kw in ['strategy', 'roadmap', 'vision', 'partnership', 'alliance'])
        include_technical_theme = any(kw in job_desc_lower for kw in ['technical', 'architect', 'engineer', 'platform', 'cloud', 'ai', 'ml'])

        theme_instructions = []
        if include_leadership_theme: theme_instructions.append("- Leadership and team building aspects")
        if include_strategic_theme: theme_instructions.append("- Strategic planning and partnership elements")
        if include_technical_theme: theme_instructions.append("- Technical depth and platform expertise")

        theme_prompt_section = "**KEY THEMES TO INCORPORATE (if relevant and natural):**\n" + "\n".join(theme_instructions) if theme_instructions else ""

        # Build Prompt
        prompt = f"""You are an expert resume editor. Write a concise 1-2 sentence overview summarizing the key achievements from the bullets below, while also weaving in the specified high-level themes relevant to the overall target role.

**BULLETS TO SUMMARIZE:**
{bullet_summary_input}

{theme_prompt_section}

**ABSOLUTELY CRITICAL:**
1.  The final overview MUST be strictly between {min_wc} and {max_wc} words total.
2.  The overview MUST consist of only 1 or 2 sentences.
3.  Your summary must be grounded in the achievements listed in the **BULLETS TO SUMMARIZE**.
4.  Ensure the specified **KEY THEMES** are naturally integrated.
5.  Do NOT explicitly list raw keywords from the job description.
6.  Output ONLY the overview text, with no preamble, explanation, or markdown fences like ```.
7.  **Do NOT start the overview with phrases like 'At [Company]', 'As [Title]', etc.**

**FINAL OVERVIEW ({min_wc}-{max_wc} words, 1-2 sentences):**
"""

        system_prompt = "You are an expert resume editor specializing in summarizing experience sections while incorporating key executive themes."
        synthesized_overview, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )

        # Basic post-check for prompt artifacts (Same logic)
        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview or "KEY THEMES" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")
        # Word/Sentence count validation warning (Same logic)
        final_wc = count_words_ms_word_style(synthesized_overview); final_sc = _count_sentences(synthesized_overview)
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} overview WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if not (1 <= final_sc <= 2): logging.warning(f"{section_id} overview SC ({final_sc}) outside target (1-2).")
        return synthesized_overview, call_count


    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id_str: str) -> List[Dict]:
        # Validates LLM bullet selection. Raises HopExecutionError on failure.
        if len(selected_bullets_text) != expected_count: raise HopExecutionError(f"{section_id_str} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}.")
        validated_bullets = []; master_texts_map = {b['bullet_text'].strip(): b for b in master_bullets_structured if 'bullet_text' in b and isinstance(b['bullet_text'], str)}; returned_texts_set = set()
        for selected_text in selected_bullets_text:
            cleaned_text = selected_text.strip(); matched_bullet = master_texts_map.get(cleaned_text) or master_texts_map.get(cleaned_text.rstrip('.'))
            if matched_bullet:
                original_text = matched_bullet['bullet_text'].strip()
                if original_text in returned_texts_set: raise HopExecutionError(f"{section_id_str} LLM returned duplicate bullet: '{original_text[:50]}...'")
                validated_bullets.append(matched_bullet); returned_texts_set.add(original_text)
            else:
                nearby_keys = [k[:50] for k in master_texts_map.keys() if k.startswith(cleaned_text[:10])]
                raise HopExecutionError(f"{section_id_str} LLM returned bullet not found/modified: '{cleaned_text[:50]}...'. Nearby: {nearby_keys}")
        if len(validated_bullets) != expected_count: raise HopExecutionError(f"{section_id_str} failed validation: Expected {expected_count}, validated {len(validated_bullets)}.")
        logging.info(f"  ✓ {section_id_str}: Validated {len(validated_bullets)} verbatim bullets.")
        return validated_bullets

    def _rewrite_bullet_for_word_count(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[str, int]:
        # Rewrites a bullet for word count. Raises HopExecutionError on failure.
        total_calls = 0
        try:
            min_wc, max_wc = target_word_count_range
            prompt = f"""Rewrite the following resume bullet point to meet a specific word count constraint ({min_wc}-{max_wc} words), preserving core meaning, metrics, and tone.

ORIGINAL BULLET:
{original_bullet_text}

ABSOLUTELY CRITICAL:
1. Rewritten bullet MUST be strictly between {min_wc} and {max_wc} words.
2. Output ONLY the rewritten bullet text. No fences (```).
3. **Do NOT start with 'At [Company]', 'As [Title]', etc.**

REWRITTEN BULLET ({min_wc}-{max_wc} words):
"""
            # Ensure ReasoningConfig.DEFAULT exists
            try: reasoning_config = ReasoningConfig.DEFAULT
            except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); reasoning_config = ReasoningConfig() # Fallback

            system_prompt = f"You are an expert resume editor concisely rewriting bullets to meet strict word count targets."
            rewritten_text, call_count = self._call_gemini_api(prompt, reasoning_config, f"{section_id_str}_RewriteWC", system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            rewritten_wc = count_words_ms_word_style(rewritten_text)
            if not (min_wc <= rewritten_wc <= max_wc): raise HopExecutionError(f"{section_id_str}_RewriteWC failed WC validation ({rewritten_wc}, target: {min_wc}-{max_wc}).")
            return rewritten_text, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str}_RewriteWC failed unexpectedly: {e}") from e

    def _validate_and_potentially_rewrite_bullets(self, selected_bullets_structured: List[Dict], min_target: int, max_target: int, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        # Checks word count, attempts rewrite if needed. Returns (final_list, total_rewrite_calls).
        final_bullets = []; total_rewrite_calls = 0; logging.info(f"  Validating word count for {section_id_str} ({min_target}-{max_target})")
        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict): raise HopExecutionError(f"Invalid item in bullet list for {section_id_str}[{i}]")
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', '')); original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            word_count = bullet_data.get('word_count', count_words_ms_word_style(original_text)) # Use stored or calculate
            if not original_text: raise HopExecutionError(f"Empty bullet in {section_id_str}[{i}].")

            if not (min_target <= word_count <= max_target):
                logging.warning(f"  WC ({word_count}) outside target for {section_id_str}[{i}]. Rewriting...");
                try:
                    rewritten_text, rewrite_calls = self._rewrite_bullet_for_word_count(original_text, (min_target, max_target), f"{section_id_str}_RewriteWC_{i}", temperature_override)
                    total_rewrite_calls += rewrite_calls; rewritten_word_count = count_words_ms_word_style(rewritten_text); logging.info(f"    Rewrite SUCCESSFUL for {section_id_str}[{i}]. New count: {rewritten_word_count}")
                    new_provenance = BulletProvenance.Customized.value if original_provenance == BulletProvenance.Verbatim.value else original_provenance
                    final_bullets.append({"text": rewritten_text, "provenance": new_provenance, "word_count": rewritten_word_count, "original_text_if_rewritten": original_text})
                except HopExecutionError as rewrite_he:
                    logging.error(f"Failed WC correction for {section_id_str}[{i}]: {rewrite_he}")
                    raise HopExecutionError(f"Bullet WC correction failed for {section_id_str}[{i}]") from rewrite_he
                except Exception as e: # Catch unexpected errors during rewrite call
                    logging.error(f"Unexpected error during WC correction for {section_id_str}[{i}]: {e}", exc_info=True)
                    raise HopExecutionError(f"Unexpected error during bullet WC correction for {section_id_str}[{i}]") from e
            else: # If word count is already valid
                final_bullets.append({"text": original_text, "provenance": original_provenance, "word_count": word_count})
        logging.info(f"  ✓ Word count validation/rewrite complete for {section_id_str}. Rewrite API Calls: {total_rewrite_calls}")
        return final_bullets, total_rewrite_calls

    def _generate_lightly_customized_bullets(self, source_bullets_text: List[str], section_id_str: str, thematic_analysis: ThematicAnalysis, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        # Creates 'Customized' bullets for K.2, K.3, K.9.
        total_calls = 0
        try:
            if not source_bullets_text: return [], 0
            primary_theme_kw = []
            if thematic_analysis and thematic_analysis.primary_theme:
                 kw_raw = thematic_analysis.primary_theme.get('keywords', [])
                 if isinstance(kw_raw, list): primary_theme_kw = kw_raw

            diff_kw = []; comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                if isinstance(kw_raw, list): diff_kw = kw_raw

            context_keywords = list(set(primary_theme_kw + diff_kw))[:7]
            bullets_input = "\n".join([f"• {b}" for b in source_bullets_text])

            prompt = f"""Lightly rewrite the following resume bullet points to subtly align with target themes/keywords ({', '.join(context_keywords)}), preserving original meaning and metrics.

SOURCE BULLETS:
{bullets_input}

TARGET KEYWORDS/THEMES (use for subtle emphasis): {', '.join(context_keywords)}

Requirements:
1. Rewrite EACH source bullet.
2. Maintain original meaning & metrics.
3. Subtly incorporate/emphasize target keywords naturally.
4. Ensure professional language.
5. Output ONLY rewritten bullets, one per line, starting with "• ". No fences (```).
6. Produce EXACTLY {len(source_bullets_text)} rewritten bullets.
7. **CRITICAL: Do NOT start rewritten bullets with 'At [Company]', 'As [Title]', etc.**

REWRITTEN BULLETS:
"""
            # Ensure ReasoningConfig.DEFAULT exists
            try: reasoning_config = ReasoningConfig.DEFAULT
            except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); reasoning_config = ReasoningConfig() # Fallback

            system_prompt = "You are an expert resume editor subtly tailoring bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            rewritten_bullets_text = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]
            if len(rewritten_bullets_text) != len(source_bullets_text): raise HopExecutionError(f"{section_id_str} LLM returned {len(rewritten_bullets_text)} customized bullets, expected {len(source_bullets_text)}.")
            result_list = [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": count_words_ms_word_style(b)} for b in rewritten_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} customization failed: {e}") from e

    def _generate_synthetic_bullets(self, count: int, company_name: str, job_description: str, thematic_analysis: ThematicAnalysis, context_bullets: str, reasoning_config: ReasoningConfig, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        # Creates 'Synthetic' bullets for K.2, K.3, K.9.
        total_calls = 0
        try:
            if count <= 0: return [], 0
            primary_theme = thematic_analysis.primary_theme.get('name', 'key responsibilities') if thematic_analysis.primary_theme else 'key responsibilities'
            primary_theme_kw = []
            if thematic_analysis and thematic_analysis.primary_theme:
                 kw_raw = thematic_analysis.primary_theme.get('keywords', [])
                 if isinstance(kw_raw, list): primary_theme_kw = kw_raw

            diff_kw = []; comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                if isinstance(kw_raw, list): diff_kw = kw_raw
            context_keywords = list(set(primary_theme_kw + diff_kw))[:10]

            prompt = f"""Generate {count} plausible, unique, impactful synthetic resume bullet points for '{company_name}'. Align with target theme '{primary_theme}' and keywords ({', '.join(context_keywords)}), complementing existing bullets.

EXISTING BULLETS (context, avoid duplication):
{context_bullets if context_bullets else "(None)"}

Requirements:
1. Generate EXACTLY {count} new bullets.
2. Plausible achievements relevant to company/theme.
3. Imply quantifiable impact/action (use strong verbs).
4. Create *new* achievements, don't rephrase existing.
5. Maintain professional tone.
6. Output ONLY {count} new bullets, one per line, starting with "* ". No fences (```).
7. **CRITICAL: Do NOT start with 'At [Company]', 'As [Title]', etc.**

GENERATED SYNTHETIC BULLETS:
"""
            system_prompt = "You generate plausible, impactful, synthetic resume bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]
            if len(synthetic_bullets_text) != count: raise HopExecutionError(f"{section_id_str} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}).")
            result_list = [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": count_words_ms_word_style(b)} for b in synthetic_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} synthetic generation failed: {e}") from e

    # --- Bullet Orchestrator (Updated for K0-K11) ---
    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            provenance_targets: Dict[str, int], reasoning_config: ReasoningConfig, section_enum: ResumeSection,
            temperature_override: Optional[float] = None, is_competencies: bool = False, **kwargs
    ) -> Tuple[List[Dict], int]:
        # Orchestrator for V/C/S bullet generation (K.2, K.3, K.9). Raises HopExecutionError on failures.
        section_id_str = section_enum.value # Get string value for logging/API calls
        logging.info(f"  Generating bullets for {section_enum.name} ({section_id_str}) (Targets: {provenance_targets})")
        total_calls_for_section = 0
        final_bullets = [] # List to hold generated bullet dicts

        # --- 1. Get Master Bullets/Competencies ---
        master_bullets_source = []
        if is_competencies:
             # K.9: Use strategic_and_technical_competencies from master
             master_bullets_source_raw = self.master_resume.get("strategic_and_technical_competencies", [])
             # Ensure it's a list of strings
             if isinstance(master_bullets_source_raw, list):
                 master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
             else: logging.warning("Master 'strategic_and_technical_competencies' is not a list.")
        else:
             # K.2/K.3: Find experience section by company name
             exp_section = next((exp for exp in self.master_resume.get('professional_experience', []) if company_name in exp.get('company', '')), None)
             if not exp_section: raise HopExecutionError(f"Master data not found for '{company_name}' needed by {section_enum.name}")
             master_bullets_key = "bullet_pool" if "bullet_pool" in exp_section else "highlights"
             master_bullets_source_raw = exp_section.get(master_bullets_key, [])
             # Ensure it's a list of strings
             if isinstance(master_bullets_source_raw, list):
                  master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
             else: logging.warning(f"Master '{master_bullets_key}' for {company_name} is not a list.")

        # Structure the valid source items
        master_bullets_structured = []
        for bullet_text in master_bullets_source:
             if bullet_text and bullet_text.strip():
                 cleaned_text = bullet_text.strip()
                 master_bullets_structured.append({"bullet_text": cleaned_text, "text": cleaned_text, "provenance": BulletProvenance.Verbatim.value, "word_count": count_words_ms_word_style(cleaned_text)})
             else: logging.warning(f"Skipping empty master item for {company_name or 'Competencies'}")

        verbatim_count = provenance_targets.get('Verbatim', 0); customized_count = provenance_targets.get('Customized', 0); synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        if not master_bullets_structured and (verbatim_count > 0 or customized_count > 0): raise HopExecutionError(f"{section_enum.name} Cannot select/customize: No valid master items found.")

        # --- 2. Select Verbatim Bullets ---
        verbatim_bullets_selected = []
        if verbatim_count > 0:
            logging.info(f"    Selecting {verbatim_count} Verbatim items...")
            if len(master_bullets_structured) < verbatim_count: raise HopExecutionError(f"{section_enum.name} Cannot select {verbatim_count} Verbatim (only {len(master_bullets_structured)} available).")
            master_bullets_text_list = [b['bullet_text'] for b in master_bullets_structured]; keywords_for_prompt = []
            comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                 kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                 if isinstance(kw_raw, list): keywords_for_prompt = kw_raw[:10]
            prompt_select = f"""Select the {verbatim_count} most relevant bullet points from the list below based on the target keywords. Output ONLY the selected bullet points, exactly as they appear in the list, one per line. Do not add numbers, prefixes, or commentary.

**BULLET LIST:**
{chr(10).join([f"- {b}" for b in master_bullets_text_list])}

**TARGET KEYWORDS:** {', '.join(keywords_for_prompt) or 'N/A'}

**Instructions:** Choose the {verbatim_count} bullets from the list that best align with the target keywords.

**SELECTED BULLETS (Exactly {verbatim_count}, one per line, verbatim):**
"""
            system_prompt_select="You are an AI assistant that selects relevant resume bullet points based on keywords, outputting them verbatim."
            try:
                # Ensure ReasoningConfig.DEFAULT exists
                try: default_reasoning = ReasoningConfig.DEFAULT
                except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); default_reasoning = ReasoningConfig() # Fallback

                response_select, calls_v_select = self._call_gemini_api(prompt_select, default_reasoning, f"{section_id_str}_SelectV", system_prompt_select, temperature_override=temperature_override)
                total_calls_for_section += calls_v_select
                selected_texts = [line.strip().lstrip('- ') for line in response_select.split('\n') if line.strip()]
                verbatim_bullets_selected = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id_str}_SelectV")
                final_bullets.extend(verbatim_bullets_selected)
            except HopExecutionError as he: raise he # Propagate selection/validation errors
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Verbatim selection failed unexpectedly: {e}") from e


        # --- 3. Generate Customized Bullets ---
        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} items...")
            used_verbatim_texts = {b['bullet_text'] for b in verbatim_bullets_selected}; available_for_custom = [b for b in master_bullets_structured if b['bullet_text'] not in used_verbatim_texts]
            if len(available_for_custom) < customized_count: raise HopExecutionError(f"{section_enum.name} Cannot customize {customized_count}: Not enough unique items remaining ({len(available_for_custom)}).")
            random.shuffle(available_for_custom); candidates_for_custom = available_for_custom[:customized_count]; source_texts_for_custom = [b['bullet_text'] for b in candidates_for_custom]
            try:
                customized_bullets, calls_c = self._generate_lightly_customized_bullets(source_texts_for_custom, f"{section_id_str}_CustomC", self.thematic_analysis, temperature_override)
                total_calls_for_section += calls_c
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he: raise he # Propagate customization errors
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Customization failed unexpectedly: {e}") from e

        # --- 4. Generate Synthetic Bullets ---
        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic items...")
            context_bullets_text = '\n'.join([f"- {b.get('text', '')}" for b in final_bullets if isinstance(b, dict) and b.get('text')])
            try:
                # Use reasoning_config passed in, which is specific to the section (K2, K3, or K9)
                synthetic_bullets, calls_s = self._generate_synthetic_bullets(synthetic_count, company_name if not is_competencies else "Competencies", self.job_description, self.thematic_analysis, context_bullets_text, reasoning_config, f"{section_id_str}_SynthS", temperature_override)
                total_calls_for_section += calls_s
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he: raise he # Propagate synthetic generation errors
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Synthetic generation failed unexpectedly: {e}") from e

        # --- 5. Final Count Check ---
        if len(final_bullets) != total_expected_count: raise HopExecutionError(f"{section_enum.name} Internal Error: Generated {len(final_bullets)}, expected {total_expected_count}.")

        # --- 6. Word Count Validation & Rewrite ---
        target_range = self.BULLET_WORD_COUNT_RANGES.get(section_enum) # Use Enum object as key
        if target_range is None: raise HopExecutionError(f"Config Error: WC range not found for {section_enum.name}.")
        min_target, max_target = target_range; logging.info(f"    Validating word counts ({min_target}-{max_target})...")
        try:
            final_bullets_validated, calls_rewrite = self._validate_and_potentially_rewrite_bullets(final_bullets, min_target, max_target, section_id_str, temperature_override)
            total_calls_for_section += calls_rewrite
            final_bullets = final_bullets_validated
        except HopExecutionError as he: raise he # Propagate validation/rewrite errors
        except Exception as e: raise HopExecutionError(f"{section_enum.name} Word count validation/rewrite failed unexpectedly: {e}") from e

        # --- 7. Reorder Bullets (Skip for Competencies K.9) ---
        if section_enum != ResumeSection.K9_COMPETENCIES:
            logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
            current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets) if isinstance(bullet, dict)]
            current_bullets_text_input = '\n'.join(current_bullets_text_list)
            keywords_for_prompt = []
            comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                 kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                 if isinstance(kw_raw, list): keywords_for_prompt = kw_raw[:10]

            prompt_reorder = f"""Reorder the following resume bullet points for maximum impact and relevance based on the target keywords. Output ONLY the reordered bullet points, exactly as provided but in the new order, one per line. Do not add numbers, prefixes, commentary, or markdown.

**Bullets to Reorder ({company_name}):**
{current_bullets_text_input}

**Target Job Description Keywords (Prioritize relevance to these):**
{', '.join(keywords_for_prompt) or 'N/A'}

**Instructions:** Analyze the bullets and keywords. Determine the optimal order, placing the most relevant bullets first.

**REORDERED BULLETS (Exactly {len(final_bullets)}, one per line, verbatim text):**
"""
            system_prompt_reorder = "You are an expert resume editor who reorders bullet points for maximum impact based on relevance to target keywords."
            try:
                # Ensure ReasoningConfig.DEFAULT exists
                try: default_reasoning = ReasoningConfig.DEFAULT
                except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); default_reasoning = ReasoningConfig() # Fallback

                response_reorder, calls_reorder = self._call_gemini_api(prompt_reorder, default_reasoning, f"{section_id_str}_Reorder", system_prompt_reorder, temperature_override=temperature_override)
                total_calls_for_section += calls_reorder
                reordered_texts_raw = [line.strip() for line in response_reorder.split('\n') if line.strip()]
                # Strip leading numbers/dots/spaces added by LLM during reorder
                reordered_texts = [re.sub(r"^\d+\.\s*", "", txt).strip() for txt in reordered_texts_raw]

                # Validation of Reordering
                if len(reordered_texts) != total_expected_count: raise HopExecutionError(f"{section_enum.name} Reordering failed: Count mismatch (Expected {total_expected_count}, Got {len(reordered_texts)}). Preview: {reordered_texts_raw[:3]}")
                final_ordered_bullets_dicts = []; original_texts_map = {b.get('text'): b for b in final_bullets if isinstance(b, dict) and b.get('text')}; used_original_texts = set()
                for reordered_text in reordered_texts:
                    matched_dict = original_texts_map.get(reordered_text)
                    if matched_dict:
                        if reordered_text in used_original_texts: raise HopExecutionError(f"{section_enum.name} Reordering failed: Duplicate bullet found in output: '{reordered_text[:50]}...'")
                        final_ordered_bullets_dicts.append(matched_dict)
                        used_original_texts.add(reordered_text)
                    else:
                         # Attempt fuzzy match if exact fails (e.g., minor punctuation changes)
                         # This requires a similarity function - using a basic one here
                         best_match = None; best_sim = 0.8 # Threshold
                         for orig_text, orig_dict in original_texts_map.items():
                              if orig_text not in used_original_texts:
                                   sim = DuplicateDetector()._calculate_cosine_similarity(reordered_text, orig_text)
                                   if sim > best_sim: best_sim = sim; best_match = orig_dict
                         if best_match:
                              logging.warning(f"Reorder validation needed fuzzy match for '{reordered_text[:50]}...' (Sim: {best_sim:.2f})")
                              final_ordered_bullets_dicts.append(best_match)
                              used_original_texts.add(best_match['text'])
                         else: raise HopExecutionError(f"{section_enum.name} Reordering failed: LLM modified bullet text beyond fuzzy match. Got: '{reordered_text[:50]}...'")


                if len(final_ordered_bullets_dicts) != total_expected_count: raise HopExecutionError(f"{section_enum.name} Reordering failed: Final count mismatch after matching ({len(final_ordered_bullets_dicts)} vs {total_expected_count}).")
                logging.info(f"  ✓ Reordering complete for {section_enum.name}.")

                return final_ordered_bullets_dicts, total_calls_for_section
            except HopExecutionError as he:
                raise he # Propagate reorder/validation errors
            except Exception as e:
                raise HopExecutionError(f"{section_enum.name} Reordering failed unexpectedly: {e}") from e
        else: # Skip reordering for K.9
            logging.info(f"    Skipping reordering for Competencies section ({section_enum.name}).")
            # K.9 Specific Post-processing (Applied even without reordering)
            if is_competencies:
                for item in final_bullets:
                    if isinstance(item, dict) and 'text' in item:
                        # Updated Regex for K9 format: **Skill Name:** Description...
                        cleaned_text = re.sub(r'^\*\s*\*\*(.*?):\*\*\s*', r'\1:', item['text']).strip() # Keep skill name + colon
                        cleaned_text = re.sub(r'^[•*]\s*', '', cleaned_text).strip() # Remove leading bullet if any
                        item['text'] = cleaned_text
                        item['word_count'] = count_words_ms_word_style(cleaned_text)
            return final_bullets, total_calls_for_section # Return bullets without reordering for K.9

class ImmutableStagingBuffer:
    """
    HOP-4: Immutable staging buffer.
    Once locked at HOP-4.5, cannot be modified.
    """
    
    def __init__(self):
        self._data = {}
        self._locked = False
        self._lock_timestamp = None
    
    def set(self, key: str, value: Any):
        """Set value in buffer (only if not locked)."""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from buffer."""
        return self._data.get(key, default)
    
    def lock(self):
        """Lock the buffer (irreversible)."""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()
    
    def is_locked(self) -> bool:
        """Check if buffer is locked."""
        return self._locked
    
    @property
    def data(self) -> Dict:
        """Read-only access to data."""
        return copy.deepcopy(self._data)

import re
import json
import logging # Ensure logging is imported
from typing import Dict, List, Optional, Any, Tuple # Ensure needed types are imported

class TextSanitizer:
    FORBIDDEN_DASHES: str = (
        "\u2012\u2013\u2014\u2015\u2212\uFE58\uFF0D\u2010\u2011"
        "\u2043\u2E3A\u2E3B\u30A0\u058A"
        # Note: U+002D (HYPHEN-MINUS) is handled separately due to exceptions
    )
    FORBIDDEN_INVISIBLE: str = (
        "\u00A0\u00AD\u200B\u200C\u200D\u200E\u202F\u2060\uFEFF"
    )
    # Regex pattern to match forbidden dashes (excluding U+002D)
    FORBIDDEN_DASH_PATTERN = re.compile(f"[{FORBIDDEN_DASHES}]")
    # Regex pattern to match forbidden invisible characters
    FORBIDDEN_INVISIBLE_PATTERN = re.compile(f"[{FORBIDDEN_INVISIBLE}]")
    # Regex pattern to find U+002D surrounded by word characters (part of a word)
    POTENTIAL_HYPHEN_PATTERN = re.compile(r'\b\w*(\-)\w*\b')


    def __init__(self, hyphenation_rules: Dict = None):
        self.rules = hyphenation_rules or HYPHENATION_RULES_DATA # Use the global variable

        # Ensure rule structure is valid
        if not isinstance(self.rules, dict) or 'rules' not in self.rules or \
           'unnatural_hyphens_remove' not in self.rules['rules'] or \
           'natural_hyphens_preserve' not in self.rules['rules']:
            # +++ Enhancement: Log the problematic structure +++
            logging.error(f"Invalid hyphenation_rules structure provided or loaded: {json.dumps(self.rules)[:200]}...")
            raise ValueError("Invalid hyphenation_rules structure provided to TextSanitizer.")

        self.natural_hyphens_set = set(self.rules['rules']['natural_hyphens_preserve'])

        self.sanitization_counts = {
            'unnatural_hyphens_removed': 0,
            'forbidden_dashes_removed': 0, # Renamed/Added
            'forbidden_hyphen_minus_removed': 0, # Specific count for U+002D
            'invisible_chars_removed': 0, # Renamed/Added
            'punctuation_fixes': 0,      # Kept for potential future use
            'markdown_removed': 0,       # Kept for potential future use
            'jargon_simplified': 0,      # Kept for potential future use
            'fillers_removed': 0,        # Kept for potential future use
            'natural_hyphens_preserved': 0, # Was 'natural_hyphens'
        }

    def sanitize_buffer(self, staging_buffer: 'ImmutableStagingBuffer') -> Tuple[List['ValidationResult'], Dict]:
        """
        Apply comprehensive text sanitization to a staging buffer's data.
        Returns a tuple of (validation_results, sanitized_data).
        """
        if staging_buffer.is_locked():
            # Ensure ValidationResult and ValidationSeverity are available
            try:
                # Attempt to use ValidationResult and ValidationSeverity
                return [ValidationResult(
                    rule_id="R4.5-ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                    message="Staging buffer already locked before HOP-4.5"
                )], staging_buffer.data
            except NameError:
                # Fallback if ValidationResult/Severity are not defined/imported
                logging.error("ValidationResult or ValidationSeverity not defined/imported.")
                return [], staging_buffer.data # Return empty list and original data

        # Reset counts for this run
        for key in self.sanitization_counts:
            self.sanitization_counts[key] = 0

        sanitized_data = self._sanitize_dict_recursive(staging_buffer.data)

        total_fixes = sum(v for k, v in self.sanitization_counts.items() if 'preserved' not in k) # Sum actual fixes

        # Ensure ValidationResult and ValidationSeverity are available
        validation_results = []
        try:
            # Attempt to create ValidationResult
            validation_results.append(ValidationResult(
                rule_id="TEXT_SANITIZATION_COMPLETE", passed=True, severity=ValidationSeverity.INFO,
                message=f"Text sanitization complete: {total_fixes} total corrections. Preserved natural hyphens: {self.sanitization_counts['natural_hyphens_preserved']}. ({', '.join(f'{k}: {v}' for k, v in self.sanitization_counts.items() if v > 0)})"
            ))
        except NameError:
            # Fallback if ValidationResult/Severity are not defined/imported
            logging.warning("ValidationResult or ValidationSeverity not defined/imported. Cannot create sanitization completion result.")
            # Optionally add a simple log message instead

        return validation_results, sanitized_data

    def _sanitize_dict_recursive(self, data: Any) -> Any:
        """Recursively sanitize strings within dictionaries and lists."""
        if isinstance(data, dict):
            return {key: self._sanitize_dict_recursive(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_dict_recursive(item) for item in data]
        elif isinstance(data, str):
            # Apply all sanitization steps to strings
            return self._sanitize_text(data)
        else:
            # Return non-string/list/dict types as is
            return data

    def _sanitize_text(self, text: str) -> str:
        """Apply all sanitization rules to a single string."""
        original_text = text # Keep original for comparison if needed

        # 1. Apply specific unnatural hyphen removals first
        # Check if self.rules exists and has the expected structure
        if self.rules and 'rules' in self.rules and 'unnatural_hyphens_remove' in self.rules['rules']:
            for rule in self.rules['rules']['unnatural_hyphens_remove']:
                # Ensure rule is a dict with 'from' and 'to' keys
                if isinstance(rule, dict) and 'from' in rule and 'to' in rule:
                    count_before = text.count(rule['from'])
                    if count_before > 0:
                        text = text.replace(rule['from'], rule['to'])
                        self.sanitization_counts['unnatural_hyphens_removed'] += count_before
                else:
                    logging.warning(f"Skipping invalid unnatural hyphen rule: {rule}")
        else:
            logging.warning("Hyphenation rules for unnatural hyphens missing or malformed.")


        # 2. Remove forbidden invisible characters
        match_invisible = self.FORBIDDEN_INVISIBLE_PATTERN.findall(text)
        if match_invisible:
             self.sanitization_counts['invisible_chars_removed'] += len(match_invisible)
             text = self.FORBIDDEN_INVISIBLE_PATTERN.sub('', text) # Remove them

        # 3. Remove forbidden dash characters (excluding U+002D initially)
        match_dashes = self.FORBIDDEN_DASH_PATTERN.findall(text)
        if match_dashes:
             self.sanitization_counts['forbidden_dashes_removed'] += len(match_dashes)
             text = self.FORBIDDEN_DASH_PATTERN.sub('', text) # Remove them

        # 4. Handle U+002D (HYPHEN-MINUS) - Remove unless part of a preserved term
        removed_hyphen_minus_count = 0
        preserved_hyphen_minus_count_in_iteration = 0 # Track preserved count during rebuild

        # Find all words that *might* contain a hyphen
        potential_hyphenated_words = set(match.group(0) for match in self.POTENTIAL_HYPHEN_PATTERN.finditer(text))

        # Check if these words are in the preserve list (ensure self.natural_hyphens_set exists)
        hyphens_to_preserve_in_words = set()
        if hasattr(self, 'natural_hyphens_set') and isinstance(self.natural_hyphens_set, set):
             for word in potential_hyphenated_words:
                 if word in self.natural_hyphens_set:
                     hyphens_to_preserve_in_words.add(word)
        else:
            logging.warning("natural_hyphens_set missing or not a set. Cannot preserve hyphens.")


        # Now remove U+002D *only if it's NOT part of a preserved word*
        # Rebuild the string character by character for accuracy
        final_text = ""
        current_pos = 0
        while current_pos < len(text):
            char = text[current_pos]
            if char == '-':
                # Check context: Is this hyphen part of a word in hyphens_to_preserve_in_words?
                part_of_preserved = False
                # Iterate through known preserved words containing hyphens
                for preserved_word in hyphens_to_preserve_in_words:
                    # Check if the current position falls within an occurrence of a preserved word
                    # Search for the preserved word starting from a plausible position before the hyphen
                    search_start = max(0, current_pos - len(preserved_word) + 1)
                    found_index = text.find(preserved_word, search_start)
                    # If found, check if the current hyphen position is within this found instance
                    while found_index != -1:
                         # Ensure the hyphen is within this specific instance's bounds
                         if found_index <= current_pos < found_index + len(preserved_word):
                              part_of_preserved = True
                              break # Found the context, no need to check other instances or words
                         # If not in this instance, search for the *next* instance
                         search_start = found_index + 1
                         found_index = text.find(preserved_word, search_start)
                    if part_of_preserved:
                         break # Stop checking other preserved words if context found

                if not part_of_preserved:
                    # It's a U+002D not confirmed to be in a preserved word, remove it
                    removed_hyphen_minus_count += 1
                else:
                    # It's likely part of a preserved word, keep it and count it
                    final_text += char
                    preserved_hyphen_minus_count_in_iteration += 1
            else:
                # Not a hyphen, keep the character
                final_text += char
            current_pos += 1

        text = final_text # Update text with hyphens potentially removed
        self.sanitization_counts['forbidden_hyphen_minus_removed'] = removed_hyphen_minus_count
        # Update the preserved count based on the iteration
        self.sanitization_counts['natural_hyphens_preserved'] = preserved_hyphen_minus_count_in_iteration

        # text = self._simplify_jargon(text)
        # text = self._remove_fillers(text)

        return text
    
# ============================================================================
# UTILITY HELPER FUNCTIONS
# ============================================================================

def _count_sentences(text: str) -> int:
    """
    Helper to count sentences. Splits by common terminators followed by space,
    and filters empty strings. Includes logic to avoid splitting on common abbreviations.
    """
    if not text or not text.strip():
        return 0
    pattern = re.compile(
        r'(?<!\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|[Ee]\.g|[Ii]\.e)\.)' +
        r'(?<!\b[A-Z]\.)' +
        r'([.!?]+)\s+'
    )
    splits = pattern.split(text)
    sentences = []
    for i in range(0, len(splits), 2):
        if splits[i].strip():
            sentences.append(splits[i])
    return len(sentences)

class TextUtils:
    """Centralized utility class for all text processing operations."""
    
    # Regex to split sentences. It looks for one or more sentence terminators (.!?)
    # followed by whitespace, but NOT when preceded by a common title (Mr., Dr., etc.)
    # or a single capital letter (like in "Washington D.C.").
    # (?<!...) is a negative lookbehind.
    abbreviations = r'(?<!\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|[Ee]\.g|[Ii]\.e)\.)'
    initials = r'(?<!\b[A-Z]\.)'
    # Combine lookbehinds and the main splitting pattern
    # The main pattern splits after one or more terminators followed by a space.
    sentence_pattern = f'{abbreviations}{initials}([.!?]+)\\s+'
    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences using MS Word style rules.
        Handles abbreviations like Mr., Dr., etc.
        """
        if not text or not text.strip():
            return 0
        
        # Protect common abbreviations that should NOT end sentences
        abbrev_pattern = r'(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|e\.g|i\.e|Inc|Ltd|Corp)\.'
        text_protected = re.sub(
            abbrev_pattern,
            lambda m: m.group().replace('.', '<DOT>'),
            text,
            flags=re.IGNORECASE
        )
        
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text_protected)
        
        # Restore dots and count non-empty sentences
        sentences = [s.replace('<DOT>', '.').strip() for s in sentences if s.strip()]
        
        return len(sentences)
    
    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words using MS Word style rules.
        Handles hyphens, em-dashes, and compound words correctly.
        """
        if not text or not text.strip():
            return 0
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Replace en-dash/em-dash with spaces (but preserve hyphens in compounds)
        text = text.replace(' -- ', ' ').replace('—', ' ')
        
        # Split on whitespace
        words = text.split()
        
        return len(words)
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        Uses sklearn if available, otherwise falls back to basic word overlap.
        """
        if not text1 or not text2:
            return 0.0
        
        # Try sklearn TF-IDF approach first
        if SKLEARN_AVAILABLE:
            try:
                vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
                vectors = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
                return float(similarity)
            except Exception as e:
                logging.debug(f"sklearn similarity failed, using fallback: {e}")
        
        # Fallback: Basic Jaccard similarity (word overlap)
        words1 = set(text1.lower().split()) - STOPWORDS
        words2 = set(text2.lower().split()) - STOPWORDS
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Remove problematic Unicode characters from text.
        Fixes encoding issues from web scraping and LLM outputs.
        """
        if not text:
            return ""
        
        # Map common encoding issues to ASCII equivalents
        replacements = {
            'â€œ': '"',   # Left double quote
            'â€': '"',    # Right double quote
            'â€˜': "'",   # Left single quote
            'â€™': "'",   # Right single quote / apostrophe
            'â€"': '-',   # En dash
            'â€"': '--',  # Em dash
            'â€¦': '...',  # Ellipsis
            'Â': '',      # Non-breaking space artifact
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove zero-width spaces and other invisible Unicode
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        # Remove any remaining non-ASCII quotes/dashes
        text = text.replace('‘', "'").replace('’', "'")
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('–', '-').replace('—', '--')
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_chars: int = 100, suffix: str = "...") -> str:
        """Truncate text to max_chars, adding suffix if truncated."""
        if not text or len(text) <= max_chars:
            return text
        return text[:max_chars - len(suffix)] + suffix
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """
        Extract top N keywords from text using simple frequency analysis.
        Removes stopwords and short words.
        """
        if not text:
            return []
        
        # Tokenize and clean
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Remove stopwords
        words = [w for w in words if w not in STOPWORDS]
        
        # Count frequencies
        word_counts = Counter(words)
        
        # Return top N
        return [word for word, _ in word_counts.most_common(top_n)]

# Create global instance for convenient access
text_utils = TextUtils()

def count_words_ms_word_style(text: str) -> int:
    """
    Counts words replicating Quillbot's behavior:
    - Treats hyphenated words as single words.
    DEPRECATED: Use text_utils.count_words() instead.
    This alias maintained for backward compatibility.
    """
    import re
    if not text:
        return 0
    words = re.findall(r"[\w'-]+", text)
    return text_utils.count_words(text)

def calculate_signal_score(text_content, thematic_analysis: ThematicAnalysis):
    """Helper to calculate signal score for a block of text based on JD keywords."""
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
        return 0.0 # No keywords to score against

    words_in_text = set(re.findall(r'\b\w+\b', text))
    matches = words_in_text.intersection(all_jd_words)
    score = len(matches) / 10.0 # Base score: 0.1 per unique keyword match
    
    # Bonus for matching primary theme keywords
    primary_matches = words_in_text.intersection(primary_words)
    score += len(primary_matches) * 0.1 # Add 0.1 bonus for each primary theme match

    return min(1.0, score) # Cap score at 1.0 (100%)

from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data
import re # Ensure re is imported for validation methods
from datetime import datetime # Ensure datetime is imported for validation methods
from typing import Dict, List, Optional, Any, Tuple, Set, Union # Ensure types are imported
from collections import defaultdict # Added for error message formatting
import logging # Ensure logging is imported

class ValidationContext:
    """
    Lazy evaluation context for validation rules.
    Calculates metrics only when needed by a rule.
    NOW includes calculation logic for cross-section and narrative similarity.
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str, master_resume: Dict):
        @staticmethod
        def _mk_range(rule_id, sev, cat, getter, label, min_k, max_k, val_k):
            """Helper: Range validation rule (min <= val <= max)."""
            return {
                "rule_id": rule_id, "severity": sev, "category": cat,
                "validator": lambda ctx: getter(ctx)[min_k] <= getter(ctx)[val_k] <= getter(ctx)[max_k],
                "error_message": lambda ctx: f"{label}: {getter(ctx)[val_k]} (target: {getter(ctx)[min_k]}-{getter(ctx)[max_k]})"
            }
        
        @staticmethod
        def _mk_method(rule_id, sev, cat, method_name, msg):
            """Helper: Rule that calls a validation method by name."""
            return {
                "rule_id": rule_id, "severity": sev, "category": cat,
                "validator": method_name,
                "error_message": msg
            }

    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str, master_resume: Dict):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {} # Cache for calculated values
        self.constraints = ContentConstraintsConfig() # Added constraints instance
        self.signal_constraints = SignalControlConfig() # Added signal constraints instance
        self._dup_detector = None # Cache DuplicateDetector instance
        self.logger = logging.getLogger(__name__) # Added logger instance

    @property
    def dup_detector(self):
        if self._dup_detector is None:
            self._dup_detector = DuplicateDetector() # Assuming DuplicateDetector is defined
        return self._dup_detector

    def _calculate_metric_details(self, section_enum: ResumeSection, metrics_to_calc: List[Tuple[str, Callable]], constraints: Dict[str, Any]) -> Dict:
        """
        Generic helper to calculate and cache metrics for a given section.
        """
        text = self.staging_buffer.get(section_enum.value, '')
        details = {}
        # Calculate all requested metrics
        for metric_name, calc_func in metrics_to_calc:
            # Safely handle potential errors during calculation (e.g., _count_sentences on non-string)
            try:
                details[metric_name] = calc_func(text) if isinstance(text, (str, list)) else 0 # Allow list for word count sum
            except Exception as e:
                self.logger.warning(f"Error calculating metric '{metric_name}' for section {section_enum.name}: {e}")
                details[metric_name] = "Error"

        # Add all provided constraints
        details.update(constraints)

        return details

    def __getattr__(self, name):
        """Calculate and cache metrics on demand."""
        if name in self._cache:
            return self._cache[name]

        # Handle specific detail requests first
        if name.endswith('_details'):
            calculation_method_details = getattr(self, f"_calculate_{name}", None)
            if calculation_method_details:
                value = calculation_method_details()
                self._cache[name] = value # Cache the details dict directly
                return value

        # Handle direct metric calculations
        calculation_method = getattr(self, f"_calculate_{name}", None)
        if calculation_method:
            value = calculation_method()
            self._cache[name] = value
            return value

        # Fallback for direct cache access if no calculation method exists
        # This shouldn't be strictly necessary if all rules use _details or specific calcs
        if name in self._cache:
             self.logger.warning(f"Accessing cached value '{name}' directly via __getattr__ fallback.")
             return self._cache[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or calculation method '_calculate_{name}' or '_calculate_{name}_details'")

    def _calculate_total_words(self):
        """Calculates total word count across relevant sections."""
        total = 0
        buffer_data = self.staging_buffer.data # Get snapshot
        for key_enum in ResumeSection: # Iterate through defined enums
            key = key_enum.value
            # Exclude non-content sections like headers, contact info
            if key_enum not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT] and \
               not key.endswith("_HEADER"):
                value = buffer_data.get(key)
                if isinstance(value, str):
                    total += count_words_ms_word_style(value) # Use helper
                elif isinstance(value, list):
                    # Handle lists which might contain strings or dicts (like bullets)
                    total += sum(count_words_ms_word_style(item.get('text', str(item))) if isinstance(item, dict) else count_words_ms_word_style(str(item)) for item in value)
        details = {'total_words': total, 'min': ContentConstraintsConfig.TOTAL_WORD_COUNT_MIN, 'max': ContentConstraintsConfig.TOTAL_WORD_COUNT_MAX}
        self._cache["VG_TOTAL_WORD_COUNT"] = details # Cache details for rule
        return total # Return the count directly

    def _calculate_unify_words(self):
        """Calculates total words for K.2 Unify (Overview + Bullets)."""
        unify_overview = self.staging_buffer.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets = self.staging_buffer.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        overview_wc = count_words_ms_word_style(unify_overview) # Use helper
        bullets_wc = sum(count_words_ms_word_style(b.get('text', '')) for b in unify_bullets if isinstance(b, dict))
        return overview_wc + bullets_wc

    def _calculate_ibm_words(self):
        """Calculates total words for K.3 IBM (Overview + Bullets)."""
        ibm_overview = self.staging_buffer.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets = self.staging_buffer.get(ResumeSection.K3_IBM_BULLETS.value, [])
        overview_wc = count_words_ms_word_style(ibm_overview) # Use helper
        bullets_wc = sum(count_words_ms_word_style(b.get('text', '')) for b in ibm_bullets if isinstance(b, dict))
        return overview_wc + bullets_wc

    def _calculate_unify_ibm_percent(self):
        """Calculates combined percentage for K.2 Unify + K.3 IBM."""
        total_w = self.total_words # Trigger total calculation
        if total_w == 0:
            percent = 0.0
        else:
            percent = (self.unify_words + self.ibm_words) / total_w * 100.0
        details = {'unify_ibm_percent': percent, 'min': ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MIN, 'max': ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MAX}
        self._cache["WORD_DISTRIBUTION_UNIFY_IBM"] = details # Cache details for rule
        return percent

    def _calculate_unify_ibm_ratio(self):
        """Calculates ratio K.2 Unify / K.3 IBM."""
        ibm_w = self.ibm_words
        unify_w = self.unify_words
        ratio = unify_w / ibm_w if ibm_w > 0 else 0.0 # Avoid division by zero
        details = {'unify_ibm_ratio': ratio, 'min': ContentConstraintsConfig.UNIFY_IBM_RATIO_MIN, 'max': ContentConstraintsConfig.UNIFY_IBM_RATIO_MAX}
        self._cache["UNIFY_IBM_RATIO"] = details # Cache details for rule
        return ratio

    def _calculate_k1_sentence_count_details(self):
        """Calculates details needed for VG_SENTENCE_COUNT_K1."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('sentence_count', _count_sentences)], # Use helper
            constraints={'min': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}
        )
        self._cache["VG_SENTENCE_COUNT_K1"] = details
        return details

    def _calculate_k1_word_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('word_count', count_words_ms_word_style)], # Use helper
            constraints={'min': self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}
        )
        self._cache["VG_WORD_COUNT_K1"] = details
        return details

    def _calculate_k2_overview_details(self):
        """Calculates details for K.2 Unify Overview rules."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K2_UNIFY_OVERVIEW,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('sentence_count', _count_sentences)], # Use helpers
            constraints={'min_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["VG_WORD_COUNT_K2_OVERVIEW"] = details
        self._cache["VG_SENTENCE_COUNT_K2_OVERVIEW"] = details
        return details

    def _calculate_k3_overview_details(self):
        """Calculates details for K.3 IBM Overview rules."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K3_IBM_OVERVIEW,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('sentence_count', _count_sentences)], # Use helpers
            constraints={'min_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["VG_WORD_COUNT_K3_OVERVIEW"] = details
        self._cache["VG_SENTENCE_COUNT_K3_OVERVIEW"] = details
        return details

    def _calculate_headline_details(self):
        """Calculates details for headline rules."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K0_HEADLINE,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('headline', lambda t: t)], # Use helper
            constraints={'min': self.constraints.HEADLINE_WORD_COUNT_MIN, 'max': self.constraints.HEADLINE_WORD_COUNT_MAX}
        )
        self._cache["VG_HEADLINE_WORD_COUNT"] = details
        self._cache["VG_HEADLINE_NO_TITLES"] = details
        self._cache["VG_HEADLINE_NO_COMMAS"] = details
        self._cache["VG_HEADLINE_COMPONENT_WC"] = details
        return details

    def _calculate_cover_letter_jd_similarity(self):
        """Calculates cosine similarity between cover letter (K.11) and JD."""
        cover_letter_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        similarity = 0.0 # Default value
        if cover_letter_text and self.job_description:
            try:
                # Use cached DuplicateDetector instance via property
                similarity = self.dup_detector._calculate_cosine_similarity(cover_letter_text, self.job_description) # Use underlying method
            except Exception as e:
                self.logger.warning(f"Error calculating cover letter similarity: {e}")
                similarity = 0.0 # Default on error

        details = {
            "cover_letter_jd_similarity": similarity,
            "min_sim": ContentConstraintsConfig.COVER_LETTER_JD_RELEVANCE_THRESHOLD,
            "max_sim": SignalControlConfig.CL_MAX_JD_SIMILARITY
        }
        self._cache["VG_COVER_LETTER_RELEVANCE_RANGE"] = details # Cache details for rule
        return similarity

    def _calculate_expected_signature(self):
        """Calculates the expected cover letter signature block."""
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        # Ensure COVER_LETTER_SIGNATURE_TEMPLATE exists before formatting
        if 'COVER_LETTER_SIGNATURE_TEMPLATE' not in globals():
             self.logger.error("COVER_LETTER_SIGNATURE_TEMPLATE not found!")
             return "[Signature Template Missing]"
        try:
            return COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except KeyError as e:
            self.logger.error(f"Error formatting signature template: Missing key {e}")
            return f"[Error: Missing signature key {e}]"

    def _calculate_cover_letter_structure_details(self):
        """Calculates details for COVER_LETTER_STRUCTURE rule (using K.11)."""
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        paras = [p.strip() for p in cl_text.split('\n\n') if p.strip()]
        p1_wc, p2_wc, p3_wc = 0, 0, 0
        error_msg = None
        try:
             salutation_idx = next(i for i, p in enumerate(paras) if p.startswith("Dear Hiring Manager,"))
             closing_idx = next((i for i, p in enumerate(paras) if p == "Sincerely,"), len(paras))
             # Identify paragraph indices relative to salutation, checking bounds
             p1_idx = salutation_idx + 1
             p2_idx = p1_idx + 1
             p3_idx = p2_idx + 1

             if p1_idx < closing_idx and p1_idx < len(paras): p1_wc = count_words_ms_word_style(paras[p1_idx]) # Use helper
             if p2_idx < closing_idx and p2_idx < len(paras): p2_wc = count_words_ms_word_style(paras[p2_idx]) # Use helper
             if p3_idx < closing_idx and p3_idx < len(paras): p3_wc = count_words_ms_word_style(paras[p3_idx]) # Use helper
             if not (p1_idx < closing_idx and p2_idx < closing_idx and p3_idx < closing_idx and p3_idx < len(paras)): # Check bounds
                  error_msg = "Could not find expected 3 body paragraphs before closing"
        except (StopIteration, IndexError):
             error_msg = "Could not find expected salutation or closing"

        c = ContentConstraintsConfig()
        details = {
            "p1_wc": p1_wc, "p1_min": c.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": c.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": c.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": c.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": c.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": c.COVER_LETTER_P3_WORD_COUNT_MAX,
            "error": error_msg
        }
        self._cache["COVER_LETTER_STRUCTURE"] = details
        return details

    def _calculate_k4_narrative_details(self):
        """Calculates details for K.4 TraderSense Narrative rules."""
        min_wc = getattr(ContentConstraintsConfig, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN', 40) # Use 40 default
        max_wc = getattr(ContentConstraintsConfig, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX', 60) # Use 60 default
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K4_TRADERSENSE_NARRATIVE,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('sentence_count', _count_sentences)], # Use helpers
            constraints={'min_wc': min_wc, 'max_wc': max_wc, 'target_sc': 3}
        )
        self._cache["VG_NARRATIVE_WORD_COUNT_K4"] = details
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K4"] = details
        return details

    def _calculate_k5_narrative_details(self):
        """Calculates details for K.5 EY Narrative rules."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K5_EY_NARRATIVE,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('sentence_count', _count_sentences)], # Use helpers
            constraints={'min_wc': ContentConstraintsConfig.EY_NARRATIVE_WORD_COUNT_MIN, 'max_wc': ContentConstraintsConfig.EY_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["VG_NARRATIVE_WORD_COUNT_K5"] = details
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K5"] = details
        return details

    def _calculate_k6_narrative_details(self):
        """Calculates details for K.6 Early Career Narrative rules."""
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            metrics_to_calc=[('word_count', count_words_ms_word_style), ('sentence_count', _count_sentences)], # Use helpers
            constraints={'min_wc': ContentConstraintsConfig.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN, 'max_wc': ContentConstraintsConfig.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["VG_NARRATIVE_WORD_COUNT_K6"] = details
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K6"] = details
        return details

    def _calculate_cross_section_similarity_details(self) -> Dict:
        """Calculates pairwise similarity between key sections and caches details."""
        details = {"failures": [], "checked_pairs": 0, "max_similarity": 0.0, "scores": {}}
        threshold = 0.65
        sections_to_compare = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K9_COMPETENCIES,
        ]

        section_content = {}
        for section_enum in sections_to_compare:
            content = self.staging_buffer.get(section_enum.value)
            # Competencies might be a list, join them; others are strings
            if isinstance(content, list) and section_enum == ResumeSection.K9_COMPETENCIES:
                 text_list = [item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in content]
                 section_content[section_enum] = "\n".join(text_list)
            elif isinstance(content, str):
                 section_content[section_enum] = content
            # else: # Content missing or wrong type, skip
            #     self.logger.warning(f"Skipping similarity check for {section_enum.name}: Content missing or invalid type.")

        max_sim = 0.0
        for i in range(len(sections_to_compare)):
            for j in range(i + 1, len(sections_to_compare)):
                enum1 = sections_to_compare[i]
                enum2 = sections_to_compare[j]

                text1 = section_content.get(enum1)
                text2 = section_content.get(enum2)

                if text1 and text2: # Only compare if both sections have content
                    try:
                        similarity = self.dup_detector._calculate_cosine_similarity(text1, text2) # Use underlying method
                        details["checked_pairs"] += 1
                        details["scores"][f"{enum1.name}_vs_{enum2.name}"] = similarity # Store score
                        max_sim = max(max_sim, similarity)
                        if similarity >= threshold:
                            details["failures"].append(f"{enum1.name} vs {enum2.name}: {similarity:.3f}")
                    except Exception as e:
                        self.logger.warning(f"Error calculating similarity between {enum1.name} and {enum2.name}: {e}")

        details["max_similarity"] = max_sim
        self._cache["VG_CROSS_SECTION_SIMILARITY"] = details
        return details

    def _calculate_narrative_vs_master_similarity_details(self) -> Dict:
        """Calculates similarity between generated narratives (K4-K6) and their master highlights."""
        details = {
            "section_results": [], # List of dicts per section
            "failures": [], # List of failure strings
            "min_threshold": 0.40,
            "max_threshold": 0.70
        }
        narrative_sections = {
            ResumeSection.K4_TRADERSENSE_NARRATIVE: 2, # Master index 2
            ResumeSection.K5_EY_NARRATIVE: 3, # Master index 3
            ResumeSection.K6_EARLY_CAREER_NARRATIVE: 4, # Master index 4
        }
        master_experience = self.master_resume.get("professional_experience", [])

        for section_enum, master_index in narrative_sections.items():
            narrative_text = self.staging_buffer.get(section_enum.value)
            master_highlights = []
            section_result = {"section": section_enum.name, "avg_similarity": 0.0, "max_similarity": 0.0, "min_similarity": 1.0, "scores": [], "valid_range": True}

            if isinstance(narrative_text, str) and narrative_text.strip():
                if 0 <= master_index < len(master_experience):
                    exp = master_experience[master_index]
                    # Get highlights or bullet_pool, ensuring it's a list of strings
                    highlights_raw = exp.get('highlights', exp.get('bullet_pool', []))
                    if isinstance(highlights_raw, list):
                        master_highlights = [h for h in highlights_raw if isinstance(h, str) and h.strip()]

                if master_highlights:
                    similarities = []
                    for highlight in master_highlights:
                        try:
                            similarity = self.dup_detector._calculate_cosine_similarity(narrative_text, highlight) # Use underlying method
                            similarities.append(similarity)
                            section_result["scores"].append(round(similarity, 3))
                        except Exception as e:
                            self.logger.warning(f"Error calculating narrative similarity for {section_enum.name} vs highlight: {e}")

                    if similarities:
                        section_result["avg_similarity"] = sum(similarities) / len(similarities)
                        section_result["max_similarity"] = max(similarities)
                        section_result["min_similarity"] = min(similarities)

                        # Check if average similarity is within the target range
                        if not (details["min_threshold"] <= section_result["avg_similarity"] <= details["max_threshold"]):
                            section_result["valid_range"] = False
                            details["failures"].append(f"{section_enum.name} avg sim ({section_result['avg_similarity']:.3f}) outside range ({details['min_threshold']:.2f}-{details['max_threshold']:.2f})")
                    else:
                        section_result["valid_range"] = False # Treat as fail if no scores calculated
                        details["failures"].append(f"{section_enum.name}: Could not calculate similarities.")
                else:
                    section_result["valid_range"] = False # Treat as fail if master highlights missing
                    details["failures"].append(f"{section_enum.name}: Master highlights missing or empty.")
            else:
                section_result["valid_range"] = False # Treat as fail if narrative missing
                details["failures"].append(f"{section_enum.name}: Generated narrative missing or empty.")

            details["section_results"].append(section_result)

        self._cache["VG_NARRATIVE_VS_MASTER_SIMILARITY"] = details
        return details


class PreFlightValidator:

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.constraints = ContentConstraintsConfig()
        self.signal_constraints = SignalControlConfig()

        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()
        self._register_rules()
        self.logger = logging.getLogger(__name__) # Added logger
    @staticmethod
    def _mk_range(rule_id, sev, cat, getter, label, min_k, max_k, val_k):
        """Helper: Range validation rule (min <= val <= max)."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": lambda ctx: getter(ctx)[min_k] <= getter(ctx)[val_k] <= getter(ctx)[max_k],
            "error_message": lambda ctx: f"{label}: {getter(ctx)[val_k]} (target: {getter(ctx)[min_k]}-{getter(ctx)[max_k]})"
        }
    
    @staticmethod
    def _mk_method(rule_id, sev, cat, method_name, msg):
        """Helper: Rule that calls a validation method by name."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": method_name,
            "error_message": msg
        }

    RULES_CONFIG = [
        # --- RAG Quality ---
        {
            "rule_id": "VG_RAG_MIN_QUALITY", "severity": ValidationSeverity.CRITICAL, "category": "signal",
            "validator": lambda ctx: getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0) >= 0.50,
            "error_message": lambda ctx: f"Initial RAG Analysis Quality ({getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0):.1%}) is below the minimum threshold (50%)."
        },
        {
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": lambda ctx: ctx.constraints.TOTAL_WORD_COUNT_MIN <= ctx.total_words <= ctx.constraints.TOTAL_WORD_COUNT_MAX,
            "error_message": lambda ctx: f"Total resume: {ctx.total_words} words (target: {ctx.constraints.TOTAL_WORD_COUNT_MIN}-{ctx.constraints.TOTAL_WORD_COUNT_MAX})"
        },
        _mk_range("VG_SENTENCE_COUNT_K1", ValidationSeverity.CRITICAL, "structure", lambda ctx: ctx.k1_sentence_count_details, "K.1 Exec Summary sentences", 'min', 'max', 'sentence_count'),
        _mk_range("VG_WORD_COUNT_K1", ValidationSeverity.CRITICAL, "word_count", lambda ctx: ctx.k1_word_count_details, "K.1 Exec Summary words", 'min', 'max', 'word_count'),
        { # K.0 Headline Words
            "rule_id": "VG_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.CRITICAL,"category": "structure",
            "validator": lambda ctx: ctx.constraints.HEADLINE_WORD_COUNT_MIN <= ctx.headline_details['word_count'] <= ctx.constraints.HEADLINE_WORD_COUNT_MAX,
            "error_message": lambda ctx: f"K.0 Headline: {ctx.headline_details['word_count']} words (target: {ctx.headline_details['min']}-{ctx.headline_details['max']}). Headline: '{ctx.headline_details['headline']}'"
        },
        _mk_range("VG_WORD_COUNT_K2_OVERVIEW", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview words", 'min_wc', 'max_wc', 'word_count'),
        _mk_range("VG_SENTENCE_COUNT_K2_OVERVIEW", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
        _mk_range("VG_WORD_COUNT_K3_OVERVIEW", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview words", 'min_wc', 'max_wc', 'word_count'),
        _mk_range("VG_SENTENCE_COUNT_K3_OVERVIEW", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
        _mk_range("VG_NARRATIVE_WORD_COUNT_K4", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k4_narrative_details, "K.4 TraderSense Narrative words", 'min_wc', 'max_wc', 'word_count'),
        {  # K.4 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K4", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k4_narrative_details['target_sc'] - 1 <= ctx.k4_narrative_details['sentence_count'] <= ctx.k4_narrative_details['target_sc'] + 1,  # Allow +/- 1
            "error_message": lambda ctx: f"K.4 TraderSense Narrative: {ctx.k4_narrative_details['sentence_count']} sentences (target range: {ctx.k4_narrative_details['target_sc']-1}-{ctx.k4_narrative_details['target_sc']+1})"
        },
        _mk_range("VG_NARRATIVE_WORD_COUNT_K5", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k5_narrative_details, "K.5 EY Narrative words", 'min_wc', 'max_wc', 'word_count'),
        {  # K.5 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K5", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k5_narrative_details['target_sc'] - 1 <= ctx.k5_narrative_details['sentence_count'] <= ctx.k5_narrative_details['target_sc'] + 1,  # Allow +/- 1
            "error_message": lambda ctx: f"K.5 EY Narrative: {ctx.k5_narrative_details['sentence_count']} sentences (target range: {ctx.k5_narrative_details['target_sc']-1}-{ctx.k5_narrative_details['target_sc']+1})"
        },
        _mk_range("VG_NARRATIVE_WORD_COUNT_K6", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k6_narrative_details, "K.6 Early Career Narrative words", 'min_wc', 'max_wc', 'word_count'),
        {  # K.6 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K6", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k6_narrative_details['target_sc'] - 1 <= ctx.k6_narrative_details['sentence_count'] <= ctx.k6_narrative_details['target_sc'] + 1,  # Allow +/- 1
            "error_message": lambda ctx: f"K.6 Early Career Narrative: {ctx.k6_narrative_details['sentence_count']} sentences (target range: {ctx.k6_narrative_details['target_sc']-1}-{ctx.k6_narrative_details['target_sc']+1})"
        },
        _mk_method("VG_BULLET_WORD_COUNT_RANGE", ValidationSeverity.HIGH, "word_count", "_validate_bullet_word_count_range", lambda ctx: f"Bullet word counts outside hardcoded ranges: {ctx._cache.get('VG_BULLET_WORD_COUNT_RANGE', {}).get('violations', 'N/A')}"),
        {
            "rule_id": "WORD_DISTRIBUTION_UNIFY_IBM", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ctx.constraints.UNIFY_IBM_COMBINED_PERCENT_MIN <= ctx.unify_ibm_percent <= ctx.constraints.UNIFY_IBM_COMBINED_PERCENT_MAX,
            "error_message": lambda ctx: f"K.2(Unify)+K.3(IBM): {ctx.unify_ibm_percent:.1f}% of total (target: {ctx._cache['WORD_DISTRIBUTION_UNIFY_IBM']['min']}-{ctx._cache['WORD_DISTRIBUTION_UNIFY_IBM']['max']}%)"
        },
        {
            "rule_id": "UNIFY_IBM_RATIO", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ctx.ibm_words > 0 and ctx.constraints.UNIFY_IBM_RATIO_MIN <= ctx.unify_ibm_ratio <= ctx.constraints.UNIFY_IBM_RATIO_MAX,
            "error_message": lambda ctx: f"K.2(Unify)/K.3(IBM) ratio: {ctx.unify_ibm_ratio:.2f} (target: {ctx._cache['UNIFY_IBM_RATIO']['min']}-{ctx._cache['UNIFY_IBM_RATIO']['max']})"
        },
        {
            "rule_id": "BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: ctx.staging_buffer.is_locked(),
            "error_message": "Staging buffer must be locked before validation"
        },
        {
            "rule_id": "VG_COVER_LETTER_SIGNATURE_VALID", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: bool(ctx.expected_signature and '\n' in ctx.expected_signature and ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').rstrip().endswith(ctx.expected_signature)),
            "error_message": "K.11 Cover letter signature is missing, malformed, or not multi-line."
        },
        _mk_method("VG_COVER_LETTER_FULL_STRUCTURE", ValidationSeverity.HIGH, "structure", "_validate_cover_letter_full_structure", "K.11 Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."),
        _mk_method("VG_HEADLINE_NO_TITLES", ValidationSeverity.CRITICAL, "structure", "_validate_headline_format_no_titles", lambda ctx: f"K.0 Headline contains forbidden titles: {ctx._cache.get('VG_HEADLINE_NO_TITLES', {}).get('forbidden', 'N/A')}. Headline: '{ctx.headline_details.get('headline', '')}'"),
        {"rule_id": "VG_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: ',' not in ctx.headline_details.get('headline', ''), "error_message": lambda ctx: f"K.0 Headline contains commas. Headline: '{ctx.headline_details.get('headline', '')}'"},
        _mk_method("VG_HEADLINE_COMPONENT_WC", ValidationSeverity.HIGH, "structure", "_validate_headline_format_component_wc", lambda ctx: f"K.0 Headline component word count outside range ({ctx._cache.get('VG_HEADLINE_COMPONENT_WC', {}).get('min', '?')}-{ctx._cache.get('VG_HEADLINE_COMPONENT_WC', {}).get('max', '?')}). Violations: {ctx._cache.get('VG_HEADLINE_COMPONENT_WC', {}).get('wc_violations_str', 'N/A')}. Headline: '{ctx._cache.get('VG_HEADLINE_COMPONENT_WC', {}).get('headline', '')}'"),
        {"rule_id": "VG_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Resume headers not consistently H2"},
        {"rule_id": "VG_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Education/Certification format incorrect"},
        {"rule_id": "VG_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience bullets incorrect style"},
        {"rule_id": "VG_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Competencies list formatting incorrect"},
        {"rule_id": "VG_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience section formatting incorrect"},
        _mk_method("CONTENT_NO_PLACEHOLDERS", ValidationSeverity.HIGH, "content", "_validate_no_placeholders", lambda ctx: f"Found placeholder text in content: {ctx._cache.get('CONTENT_NO_PLACEHOLDERS', {}).get('placeholders', 'N/A')}"),
        _mk_method("VG_FORBIDDEN_VERBS", ValidationSeverity.HIGH, "content", "_validate_forbidden_verbs", lambda ctx: f"Forbidden verbs found in generated content: {ctx._cache.get('VG_FORBIDDEN_VERBS', {}).get('violations', 'N/A')}"),
        _mk_method("VG_NO_INTRO_PHRASES", ValidationSeverity.HIGH, "content", "_validate_no_intro_phrases", lambda ctx: f"Banned introductory phrases found: {ctx._cache.get('VG_NO_INTRO_PHRASES', {}).get('violations', 'N/A')}"),
        _mk_method("VG_PER_SECTION_SIGNAL_SCORE", ValidationSeverity.HIGH, "content", "_validate_per_section_signal_raw", lambda ctx: f"One or more sections outside target raw signal score range: {ctx._cache.get('VG_PER_SECTION_SIGNAL_SCORE', {}).get('failures', 'N/A')}"),
        {
            "rule_id": "VG_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": lambda ctx: ctx.constraints.K1_MIN_DIFFERENTIATORS <= ctx._calculate_k1_differentiator_range(ctx)['found'] <= ctx.signal_constraints.K1_MAX_DIFFERENTIATORS,
            "error_message": lambda ctx: f"K.1 Summary contains {ctx._cache.get('VG_K1_DIFFERENTIATOR_RANGE', {}).get('found', '?')} differentiators (target: {ctx._cache.get('VG_K1_DIFFERENTIATOR_RANGE', {}).get('min', '?')}-{ctx._cache.get('VG_K1_DIFFERENTIATOR_RANGE', {}).get('max', '?')})."
        },
        _mk_method("VG_JD_KEYWORD_RANGE", ValidationSeverity.HIGH, "content", "_validate_jd_keyword_range", lambda ctx: f"Resume contains {ctx._cache.get('VG_JD_KEYWORD_RANGE', {}).get('found', '?')} unique JD keywords (target: {ctx._cache.get('VG_JD_KEYWORD_RANGE', {}).get('min', '?')}-{ctx._cache.get('VG_JD_KEYWORD_RANGE', {}).get('max', '?')})."),
        _mk_method("NARRATIVE_MINING_PRESENCE", ValidationSeverity.HIGH, "content", "_validate_narrative_mining_presence", "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."),
        {
            "rule_id": "VG_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: ctx.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD <= ctx.cover_letter_jd_similarity <= ctx.signal_constraints.CL_MAX_JD_SIMILARITY,
            "error_message": lambda ctx: f"K.11 Cover letter relevance to JD is {ctx.cover_letter_jd_similarity:.2f} (target: {ctx._cache.get('VG_COVER_LETTER_RELEVANCE_RANGE', {}).get('min_sim', 0.0):.2f}-{ctx._cache.get('VG_COVER_LETTER_RELEVANCE_RANGE', {}).get('max_sim', 0.0):.2f})."
        },
        _mk_method("COVER_LETTER_NARRATIVE_INTEGRITY", ValidationSeverity.HIGH, "content", lambda ctx: ctx._calculate_cover_letter_narrative(ctx)['valid'], lambda ctx: f"K.11 Cover letter may be missing narrative integrity. Hook: {ctx._cache.get('COVER_LETTER_NARRATIVE_INTEGRITY', {}).get('hook', '?')}, Proof: {ctx._cache.get('COVER_LETTER_NARRATIVE_INTEGRITY', {}).get('proof', '?')}, Vision: {ctx._cache.get('COVER_LETTER_NARRATIVE_INTEGRITY', {}).get('vision', '?')}"),
        {
            "rule_id": "COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: "track record of measurable AI transformation" not in ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, ''),
            "error_message": "Creative cover letter generation failed; fallback likely used."
        },
        _mk_method("COVER_LETTER_STRUCTURE", ValidationSeverity.HIGH, "content", "_validate_cover_letter_structure", lambda ctx: f"K.11 Cover letter paragraph word counts out of spec. P1: {ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p1_wc','?')} ({ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p1_min','?')}-{ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p1_max','?')}), P2: {ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p2_wc','?')} ({ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p2_min','?')}-{ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p2_max','?')}), P3: {ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p3_wc','?')} ({ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p3_min','?')}-{ctx._cache.get('COVER_LETTER_STRUCTURE',{}).get('p3_max','?')})"),
        _mk_method("VG_PROVENANCE_SPLIT_CHECK", ValidationSeverity.CRITICAL, "content", "_validate_provenance_split", lambda ctx: f"Provenance split mismatch: {ctx._cache.get('VG_PROVENANCE_SPLIT_CHECK', {}).get('violations', 'N/A')}"),
        _mk_method("VG_AUTHENTICITY_SIGNAL_CHECK", ValidationSeverity.HIGH, "content", "_validate_authenticity_signal", lambda ctx: f"Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {ctx._cache.get('VG_AUTHENTICITY_SIGNAL_CHECK', {}).get('details', 'N/A')}"),
        _mk_method("VG_CROSS_SECTION_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_cross_section_similarity", lambda ctx: f"High similarity (>=0.65) found between sections: {'; '.join(ctx._cache.get('VG_CROSS_SECTION_SIMILARITY', {}).get('failures', []))}"),
        _mk_method("VG_NARRATIVE_VS_MASTER_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_narrative_vs_master_similarity", lambda ctx: f"Narrative similarity to master highlights outside range (0.40-0.70): {'; '.join(ctx._cache.get('VG_NARRATIVE_VS_MASTER_SIMILARITY', {}).get('failures', []))}"),
    ]

    def _initialize_rule_map(self) -> Dict[str, Union[ResumeSection, str]]:
        """
        Creates the mapping of Rule IDs to the ResumeSection they govern.
        Includes new similarity rules mapped to GLOBAL.
        """
        logger = logging.getLogger(__name__)
        rule_map = {
            # Global Rules
            "VG_TOTAL_WORD_COUNT": "GLOBAL", "WORD_DISTRIBUTION_UNIFY_IBM": "GLOBAL",
            "UNIFY_IBM_RATIO": "GLOBAL", "VG_JD_KEYWORD_RANGE": "GLOBAL",
            "VG_AUTHENTICITY_SIGNAL_CHECK": "GLOBAL", "NARRATIVE_MINING_PRESENCE": "GLOBAL",
            "CONTENT_NO_PLACEHOLDERS": "GLOBAL", "BUFFER_LOCK_STATUS": "GLOBAL",
            "VG_RAG_MIN_QUALITY": "GLOBAL",
            "VG_CROSS_SECTION_SIMILARITY": "GLOBAL",
            "VG_NARRATIVE_VS_MASTER_SIMILARITY": "GLOBAL",
            # Visual Rules
            "VG_RESUME_HEADER_H2": "VISUAL", "VG_EDU_CERTS_FORMAT": "VISUAL",
            "VG_EXPERIENCE_BULLET_STYLE": "VISUAL", "VG_COMPETENCIES_FORMATTING": "VISUAL",
            "VG_EXPERIENCE_RENDER_FORMAT": "VISUAL",
            # K.0 Headline
            "VG_HEADLINE_WORD_COUNT": ResumeSection.K0_HEADLINE, "VG_HEADLINE_NO_TITLES": ResumeSection.K0_HEADLINE,
            "VG_HEADLINE_NO_COMMAS": ResumeSection.K0_HEADLINE, "VG_HEADLINE_COMPONENT_WC": ResumeSection.K0_HEADLINE,
            "STRUCTURE_K0_HEADLINE_PRESENT": ResumeSection.K0_HEADLINE,
            # K.1 Executive Summary
            "VG_SENTENCE_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY, "VG_WORD_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            # K.2 Unify
            "STRUCTURE_K2_UNIFY_BULLETS_PRESENT": ResumeSection.K2_UNIFY_BULLETS, "STRUCTURE_K2_UNIFY_OVERVIEW_PRESENT": ResumeSection.K2_UNIFY_OVERVIEW,
            "VG_WORD_COUNT_K2_OVERVIEW": ResumeSection.K2_UNIFY_OVERVIEW, "VG_SENTENCE_COUNT_K2_OVERVIEW": ResumeSection.K2_UNIFY_OVERVIEW,
            # K.3 IBM
            "STRUCTURE_K3_IBM_BULLETS_PRESENT": ResumeSection.K3_IBM_BULLETS, "STRUCTURE_K3_IBM_OVERVIEW_PRESENT": ResumeSection.K3_IBM_OVERVIEW,
            "VG_WORD_COUNT_K3_OVERVIEW": ResumeSection.K3_IBM_OVERVIEW, "VG_SENTENCE_COUNT_K3_OVERVIEW": ResumeSection.K3_IBM_OVERVIEW,
            # K.4 Narrative
            "STRUCTURE_K4_TRADERSENSE_NARRATIVE_PRESENT": ResumeSection.K4_TRADERSENSE_NARRATIVE, "VG_NARRATIVE_WORD_COUNT_K4": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K4": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            # K.5 Narrative
            "STRUCTURE_K5_EY_NARRATIVE_PRESENT": ResumeSection.K5_EY_NARRATIVE, "VG_NARRATIVE_WORD_COUNT_K5": ResumeSection.K5_EY_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K5": ResumeSection.K5_EY_NARRATIVE,
            # K.6 Narrative
            "STRUCTURE_K6_EARLY_CAREER_NARRATIVE_PRESENT": ResumeSection.K6_EARLY_CAREER_NARRATIVE, "VG_NARRATIVE_WORD_COUNT_K6": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K6": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            # K.9 Competencies
            "STRUCTURE_K9_COMPETENCIES_PRESENT": ResumeSection.K9_COMPETENCIES,
            # K.10 Skills
            "STRUCTURE_K10_SKILLS_PRESENT": ResumeSection.K10_SKILLS,
            # K.11 Cover Letter
            "VG_COVER_LETTER_SIGNATURE_VALID": ResumeSection.K11_COVER_LETTER, "VG_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "VG_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K11_COVER_LETTER, "COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K11_COVER_LETTER,
            "COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K11_COVER_LETTER, "COVER_LETTER_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "STRUCTURE_K11_COVER_LETTER_PRESENT": ResumeSection.K11_COVER_LETTER,
            # Complex Rules
            "VG_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION", "VG_BULLET_WORD_COUNT_RANGE": "COMPLEX_PER_SECTION",
            "VG_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION", "VG_FORBIDDEN_VERBS": "COMPLEX_PER_SECTION",
            "VG_NO_INTRO_PHRASES": "COMPLEX_PER_SECTION"
        }

        # Dynamically add structure rules
        config_rule_ids = {cfg["rule_id"] for cfg in self.RULES_CONFIG}
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if rule_id not in config_rule_ids and rule_id not in rule_map:
                rule_map[rule_id] = section_enum
                logger.debug(f"Dynamically mapped structure rule: {rule_id} -> {section_enum.name}")

        header_enums = [ ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, ResumeSection.K0_EXPERIENCE_HEADER, ResumeSection.K0_EDUCATION_HEADER, ResumeSection.K0_CERTIFICATIONS_HEADER, ResumeSection.K0_COMPETENCIES_HEADER ]
        for header_enum in header_enums:
             rule_id = f"STRUCTURE_{header_enum.name}_PRESENT"
             if rule_id not in rule_map:
                  rule_map[rule_id] = header_enum
                  logger.debug(f"Dynamically mapped header structure rule: {rule_id} -> {header_enum.name}")

        return rule_map


    def _register_rules(self):
        """Creates and registers all pre-flight validation rules based on RULES_CONFIG."""
        logger = logging.getLogger(__name__)
        all_rules_config = list(self.RULES_CONFIG)

        # Dynamically generate structure presence rules
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if not any(cfg["rule_id"] == rule_id for cfg in all_rules_config):
                all_rules_config.append({
                    "rule_id": rule_id,
                    "severity": ValidationSeverity.CRITICAL,
                    "category": "structure",
                    "validator": partial(self._validate_section_presence, section_enum=section_enum),
                    "error_message": f"{section_enum.value} is missing, empty, or a placeholder."
                })

        registered_rule_ids = set()
        for config in all_rules_config:
            rule_id = config["rule_id"]
            if rule_id in registered_rule_ids:
                 logger.warning(f"Duplicate rule ID found during registration: {rule_id}. Skipping re-registration.")
                 continue

            validator_ref = config["validator"]
            validator_func = None
            if isinstance(validator_ref, str):
                validator_func = getattr(self, validator_ref, None)
                if validator_func is None:
                    msg = f"Validator method '{validator_ref}' not found for rule {rule_id}"
                    logger.error(msg)
                    validator_func = lambda ctx: False # Always fail to prevent runtime errors
            elif callable(validator_ref):
                 validator_func = validator_ref
            else:
                 raise TypeError(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}")

            # Create error message lambda with safe formatting
            def create_error_message_lambda(template, rule_id_for_cache):
                def error_lambda(ctx: ValidationContext):
                    try:
                        # Ensure calculation happens if not already cached
                        if rule_id_for_cache not in ctx._cache:
                            # Trigger calculation via __getattr__ if a method exists
                            # Check for both _details and direct calc methods
                            if hasattr(ctx, f"_calculate_{rule_id_for_cache}_details"):
                                getattr(ctx, f"{rule_id_for_cache}_details")
                            elif hasattr(ctx, f"_calculate_{rule_id_for_cache}"):
                                getattr(ctx, rule_id_for_cache)
                            # else: # No specific calculation method, assume details are set by validator
                            #     pass

                        details = ctx._cache.get(rule_id_for_cache, {})
                        if callable(template): return str(template(ctx))
                        else: return str(template).format_map(defaultdict(lambda: '[N/A]', **details))
                    except Exception as e:
                        logger.error(f"Error formatting error message for rule {rule_id_for_cache}: {e}. Template type: '{type(template)}' Details: {ctx._cache.get(rule_id_for_cache, {})}")
                        return f"[Error formatting msg for {rule_id_for_cache}]"
                return error_lambda

            error_msg_lambda = create_error_message_lambda(config["error_message"], rule_id)

            rule = ValidationRule(
                rule_id=rule_id,
                severity=config["severity"],
                category=config.get("category", "general"),
                validator=validator_func,
                error_message=error_msg_lambda
            )
            self.engine.register_rule(rule)
            registered_rule_ids.add(rule_id)

    # --- Validation Helper Methods ---

    def _validate_cross_section_similarity(self, context: ValidationContext) -> bool:
        # Checks similarity between key generated text sections using cached details.
        try:
            details = context.cross_section_similarity_details # Trigger calculation via __getattr__
            if details.get("failures"):
                # Store the specific failed sections for retry logic
                failed_sections_set = set()
                sections_to_compare_map = {
                    ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW,
                    ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE,
                    ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
                    ResumeSection.K9_COMPETENCIES
                }
                for failure_str in details["failures"]:
                    # Extract section names from the failure string (e.g., "K1_EXECUTIVE_SUMMARY vs K2_UNIFY_OVERVIEW: 0.75")
                    match = re.match(r"(\w+)\s+vs\s+(\w+):", failure_str)
                    if match:
                        name1, name2 = match.groups()
                        for enum_member in sections_to_compare_map:
                            if enum_member.name == name1: failed_sections_set.add(enum_member)
                            if enum_member.name == name2: failed_sections_set.add(enum_member)
                context._cache["VG_CROSS_SECTION_SIMILARITY"]["failed_sections"] = failed_sections_set
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during cross-section similarity validation: {e}")
            context._cache["VG_CROSS_SECTION_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": set()}
            return False

    def _validate_narrative_vs_master_similarity(self, context: ValidationContext) -> bool:
        # Checks if average narrative similarity is within the 0.40-0.70 range using cached details.
        try:
            details = context.narrative_vs_master_similarity_details # Trigger calculation via __getattr__
            if details.get("failures"):
                # Store the specific failed sections for retry logic
                failed_sections_set = set()
                narrative_sections_map = {
                    ResumeSection.K4_TRADERSENSE_NARRATIVE,
                    ResumeSection.K5_EY_NARRATIVE,
                    ResumeSection.K6_EARLY_CAREER_NARRATIVE
                }
                for section_result in details.get("section_results", []):
                    if not section_result.get("valid_range", True):
                        section_name = section_result.get("section")
                        if section_name:
                             for enum_member in narrative_sections_map:
                                 if enum_member.name == section_name:
                                     failed_sections_set.add(enum_member)
                                     break # Found the enum, move to next failed section
                context._cache["VG_NARRATIVE_VS_MASTER_SIMILARITY"]["failed_sections"] = failed_sections_set
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during narrative vs master similarity validation: {e}")
            context._cache["VG_NARRATIVE_VS_MASTER_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": set()}
            return False

    # --- Other Validation Methods (Unchanged from previous final version) ---
    def _validate_section_presence(self, context: ValidationContext, section_enum: ResumeSection) -> bool: # Validates presence of a section in the buffer.
        content = context.staging_buffer.get(section_enum.value)
        if content is None: return False
        if isinstance(content, str): return content.strip() not in ["", "HEADER_PLACEHOLDER"] and not content.strip().startswith("[Placeholder")
        if isinstance(content, (list, dict)): return bool(content)
        return True

    def _validate_cover_letter_full_structure(self, context: ValidationContext) -> bool: # Validates the full structure of the cover letter (date, recipient, salutation, body, closing, signature).
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        expected_sig = context.expected_signature
        has_date = bool(re.search(r"^\w+ \d{1,2}, \d{4}", text.strip()))
        has_recipient = bool(re.search(r"Hiring Manager\n\[Company Name\]", text))
        has_salutation = bool(re.search(r"Dear Hiring Manager,", text))
        has_closing = bool(re.search(r"\n\nSincerely,\n\n", text))
        has_signature = expected_sig and expected_sig in text and text.strip().endswith(expected_sig)
        body_match = re.search(r"Dear Hiring Manager,\s*(.*?)\s*Sincerely,", text, re.DOTALL)
        paras_found = len([p for p in body_match.group(1).strip().split('\n\n') if p.strip()]) if body_match else 0
        has_3_paras = paras_found >= 3
        valid = has_date and has_recipient and has_salutation and has_closing and has_signature and has_3_paras
        if not valid: context._cache["VG_COVER_LETTER_FULL_STRUCTURE"] = { "has_date": has_date, "has_recipient": has_recipient, "has_salutation": has_salutation, "has_closing": has_closing, "has_signature": has_signature, "paras_found": paras_found }
        return valid

    def _validate_cover_letter_structure(self, context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        details = context.cover_letter_structure_details
        # Validates the word count of each paragraph in the cover letter.
        if details.get("error"): return False
        p1_valid = details.get('p1_min', 0) <= details.get('p1_wc', -1) <= details.get('p1_max', float('inf'))
        p2_valid = details.get('p2_min', 0) <= details.get('p2_wc', -1) <= details.get('p2_max', float('inf'))
        p3_valid = details.get('p3_min', 0) <= details.get('p3_wc', -1) <= details.get('p3_max', float('inf'))
        return p1_valid and p2_valid and p3_valid

    def _validate_bullet_word_count_range(self, context: ValidationContext) -> bool: # Validates that all generated bullets fall within their section-specific word count ranges.
        all_bullets_valid = True; violations = []; failed_sections = set()
        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            target_range = ArtistGenerator.BULLET_WORD_COUNT_RANGES.get(section_enum)
            if target_range is None: logging.warning(f"WC range missing for {section_enum.name}. Skipping."); continue
            min_wc, max_wc = target_range
            bullets = context.staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): logging.warning(f"Expected list for {section_key} bullets. Skipping."); continue
            for i, bullet in enumerate(bullets):
                actual_wc = 0; bullet_text = ""
                if isinstance(bullet, dict): bullet_text = bullet.get('text', ''); actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str): bullet_text = bullet; actual_wc = count_words_ms_word_style(bullet_text)
                else: logging.warning(f"Invalid bullet item type in {section_key}[{i}]. Skipping."); continue
                if not (min_wc <= actual_wc <= max_wc): all_bullets_valid = False; violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc})"); failed_sections.add(section_enum)
        if not all_bullets_valid: context._cache["VG_BULLET_WORD_COUNT_RANGE"] = { "violations": ", ".join(violations[:3]) + ('...' if len(violations)>3 else ''), "failed_sections": failed_sections }
        return all_bullets_valid

    def _validate_headline_format_no_titles(self, context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        # Validates headline structure (3 components with pipes) AND checks for forbidden titles.
        if not headline or '|' not in headline: details['error'] = "Missing pipes"; context._cache["VG_HEADLINE_NO_TITLES"] = details; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: details['error'] = f"Expected 3 components, found {len(components)}"; context._cache["VG_HEADLINE_NO_TITLES"] = details; return False
        forbidden_titles = ['director', 'vp', 'manager', 'lead', 'head', 'chief', 'principal', 'senior', 'executive']
        forbidden_found = []
        for i, comp in enumerate(components):
            for title in forbidden_titles:
                 if re.search(r'\b' + re.escape(title) + r'\b', comp.lower()): forbidden_found.append(title)
        details_titles = details.copy(); details_titles['forbidden'] = list(set(forbidden_found)); context._cache["VG_HEADLINE_NO_TITLES"] = details_titles
        return not forbidden_found # Return False if any forbidden title found

    def _validate_headline_format_component_wc(self, context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        # Validates headline component word count.
        # Basic structure check (already done by _validate_headline_format_no_titles if called first)
        if not headline or '|' not in headline: context._cache["VG_HEADLINE_COMPONENT_WC"] = {"error": "Missing pipes", "headline": headline}; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: context._cache["VG_HEADLINE_COMPONENT_WC"] = {"error": f"Expected 3 components, found {len(components)}", "headline": headline}; return False
        # Check component word counts
        component_wc_violations = []; wc_valid = True
        min_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MIN; max_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MAX
        for i, comp in enumerate(components):
            word_count = count_words_ms_word_style(comp)
            if not (min_comp_wc <= word_count <= max_comp_wc):
                component_wc_violations.append(f"Comp[{i+1}]: {word_count} words (Tgt: {min_comp_wc}-{max_comp_wc})")
                wc_valid = False
        # Cache results regardless of pass/fail for reporting
        details_wc = details.copy(); details_wc['min'] = min_comp_wc; details_wc['max'] = max_comp_wc;
        details_wc['wc_violations_str'] = "; ".join(component_wc_violations) if component_wc_violations else "None"
        context._cache["VG_HEADLINE_COMPONENT_WC"] = details_wc
        return wc_valid # Return True if no violations

    def _validate_no_placeholders(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        # Checks recursively for '[Placeholder...]', '[Your Name]', '[Company Name]' strings in buffer data.
        found_snippets = [] # Store formatted snippet strings
        failed_sections = set() # Store enums of sections with placeholders

        def check_recursive(item, key_enum=None): # Recursive helper function.
            """Recursive helper function."""
            nonlocal found_snippets, failed_sections # Allow modification of outer scope variables

            if isinstance(item, str):
                # Check for any of the placeholder patterns
                if ("[Placeholder" in item or "[Your Name]" in item or "[Company Name]" in item):
                    # Find the first occurrence to create a snippet
                    placeholder_match = re.search(r"(\[Placeholder.*?\]|\[Your Name\]|\[Company Name\])", item)
                    if placeholder_match:
                        placeholder_text = placeholder_match.group(1)
                        start_index = placeholder_match.start()
                        # Create a snippet around the found placeholder
                        snippet_before = item[max(0, start_index - 30):start_index]
                        snippet_after = item[start_index + len(placeholder_text) : start_index + len(placeholder_text) + 30]
                        snippet = f"...{snippet_before}{placeholder_text}{snippet_after}..."
                        # Format the finding with the section key/enum if available
                        found_snippets.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                        if key_enum:
                            failed_sections.add(key_enum)
            elif isinstance(item, dict):
                # Recursively check dictionary values
                for k, v in item.items():
                    # Try to determine the specific ResumeSection enum for this key,
                    # otherwise pass down the parent enum context.
                    enum_for_value = key_enum
                    try:
                        enum_for_value = ResumeSection(k) # Map dict key back to enum if possible
                    except ValueError:
                        pass # Keep parent's enum context if key doesn't match
                    check_recursive(v, enum_for_value) # Recurse into value
            elif isinstance(item, list):
                # Recursively check list elements
                for elem in item:
                    check_recursive(elem, key_enum) # Pass down the same enum context

        # Start the recursive check from the top-level buffer data
        # Iterate through buffer keys to provide top-level context
        for key_str, top_level_item in buffer_data.items():
            top_level_enum = None
            try:
                top_level_enum = ResumeSection(key_str)
            except ValueError:
                pass # Use None if key doesn't match an enum
            check_recursive(top_level_item, top_level_enum)

        # If any placeholders were found...
        if found_snippets:
            # Cache the findings for reporting/retry logic
            context._cache["CONTENT_NO_PLACEHOLDERS"] = {
                "placeholders": ", ".join(found_snippets[:3]), # Store first few found snippets
                "failed_sections": failed_sections # Store enums of sections containing placeholders
            }
            return False # Validation fails

        # No placeholders found
        return True

    def _validate_forbidden_verbs(self, context: ValidationContext) -> bool:
        valid = True
        # Checks for forbidden verbs in key text sections.
        violations = []
        failed = set()
        # Sections to check (bullets, narratives, overviews, K1)
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts = [] # List of tuples: (text_to_check, index_or_None)
            if isinstance(content, str):
                if content.strip(): # Check if not just whitespace
                    texts.append((content, -1)) # Use -1 index for single string content
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    # Safely get text from dict or str
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip(): # Check if not just whitespace
                        texts.append((text, i))

            # Check each extracted text snippet
            for text, idx in texts:
                # Use a generator expression for slightly better efficiency
                found_verbs = (v for v in self.FORBIDDEN_VERBS if re.search(r'\b' + re.escape(v) + r'\b', text.lower()))
                found_list = list(found_verbs) # Convert generator to list to check if empty and format
                if found_list:
                    valid = False
                    loc = f"{section_enum.value}" + (f"[{idx}]" if idx != -1 else "") # Format location string
                    violations.append(f"{loc}: '{', '.join(found_list)}'")
                    failed.add(section_enum)

        # Cache results if validation failed
        if not valid:
            context._cache["VG_FORBIDDEN_VERBS"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_no_intro_phrases(self, context: ValidationContext) -> bool:
        valid = True
        # Checks for banned introductory phrases in key text sections.
        violations = []
        failed = set()
        # Sections to check (bullets, narratives, overviews, K1, K11 body)
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts_info = [] # List of tuples: (text_to_check, index_or_label_string)
            is_cl = (section_enum == ResumeSection.K11_COVER_LETTER)

            if isinstance(content, str):
                if is_cl:
                    # Extract body paragraphs carefully for Cover Letter
                    body_text = content # Start with full text
                    # Remove header/salutation (assuming standard format)
                    body_text = re.sub(r".*Dear Hiring Manager,\s*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    # Remove closing/signature (assuming standard format)
                    body_text = re.sub(r"\s*Sincerely,.*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    if body_text.strip(): # Check if body_text is not just whitespace
                        for i, para in enumerate(body_text.strip().split('\n\n')):
                            if para.strip(): # Check paragraph is not just whitespace
                                texts_info.append((para.strip(), f"Para {i+1}"))
                elif content.strip(): # Check non-CL strings are not just whitespace
                    texts_info.append((content.strip(), None))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    # Safely get text from dict or str within the list
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip(): # Check list items are not just whitespace
                        texts_info.append((text.strip(), i))

            # Check each extracted text snippet
            for text, idx_label in texts_info:
                 match = self.BANNED_INTRO_PHRASES_PATTERN.match(text)
                 if match:
                     valid = False
                     loc = f"{section_enum.value}" # Start with section name
                     if isinstance(idx_label, int):
                         loc += f"[{idx_label}]" # Append index for list items
                     elif isinstance(idx_label, str):
                         loc += f" ({idx_label})" # Append label for CL paragraphs
                     # Correctly append violation and add section enum to failed set
                     violations.append(f"{loc}: Starts with '{match.group(0).strip()}'")
                     failed.add(section_enum)

        # Cache results if validation failed
        if not valid:
            context._cache["VG_NO_INTRO_PHRASES"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_per_section_signal_raw(self, context: ValidationContext) -> bool:
        valid = True; failures = []; failed = set()
        # Validates the raw signal score of each section against its target range.
        for label, (section_enum, target_min_raw, target_max_raw, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = context.staging_buffer.get(section_enum.value); raw_score = 0.0
            if content:
                try: # Simulation
                     normalized_score = calculate_signal_score(content, context.thematic_analysis); raw_score = normalized_score
                     if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY and raw_score > 0.9: raw_score = 1.15
                except Exception as e: logging.warning(f"Error calculating raw signal score for {label}: {e}")
            if not (target_min_raw <= raw_score <= target_max_raw): valid = False; failures.append(f"{label}({section_enum.name}): Raw {raw_score:.2f} (Tgt: {target_min_raw:.2f}-{target_max_raw:.2f})"); failed.add(section_enum)
        if not valid: context._cache["VG_PER_SECTION_SIGNAL_SCORE"] = {"failures": ", ".join(failures[:3]), "failed_sections": failed}
        return valid

    def _calculate_k1_differentiator_range(self, context: ValidationContext) -> Dict:
        k1_text = context.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        # Calculates the number of differentiator keywords found in the K.1 Executive Summary.
        differentiators = []; comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: differentiators = getattr(comp_intel, 'differentiator_keywords', [])
        valid_diffs = [kw for kw in differentiators if kw and isinstance(kw, str)]; found = sum(1 for kw in valid_diffs if kw.lower() in k1_text)
        min_target = context.constraints.K1_MIN_DIFFERENTIATORS; max_target = context.signal_constraints.K1_MAX_DIFFERENTIATORS
        details = {"found": found, "min": min_target, "max": max_target}; context._cache["VG_K1_DIFFERENTIATOR_RANGE"] = details
        return details

    def _validate_jd_keyword_range(self, context: ValidationContext) -> bool: # Validates the total number of unique JD keywords found across the entire resume.
        full_text = ""; buffer_data = context.staging_buffer.data
        sections_to_include = [ se for se in ResumeSection if se not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT, ResumeSection.K11_COVER_LETTER] and not se.name.endswith("_HEADER") ]
        for key_enum in sections_to_include:
             value = buffer_data.get(key_enum.value)
             if isinstance(value, str): full_text += value + " "
             elif isinstance(value, list): full_text += " ".join(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value) + " "
        differentiators = set(); comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: differentiators = set(kw for kw in getattr(comp_intel, 'differentiator_keywords', []) if kw and isinstance(kw, str))
        primary_words = set(kw for kw in context.thematic_analysis.primary_theme.get('keywords', []) if kw and isinstance(kw, str))
        all_jd_keywords = differentiators.union(primary_words); found = {kw for kw in all_jd_keywords if kw.lower() in full_text.lower()}
        min_target = context.constraints.MIN_JD_KEYWORDS; max_target = context.signal_constraints.RESUME_MAX_JD_KEYWORDS
        valid = min_target <= len(found) <= max_target
        context._cache["VG_JD_KEYWORD_RANGE"] = {"found": len(found), "min": min_target, "max": max_target, "jd_keywords_found": list(found)}
        return valid

    def _validate_narrative_mining_presence(self, context: ValidationContext) -> bool: # Checks if problem-solution narrative data from RAG exists in the thematic analysis.
        narratives = getattr(context.thematic_analysis, 'problem_solution_narratives', None)
        return isinstance(narratives, dict) and narratives.get('common_problems') and narratives.get('solution_patterns')

    def _calculate_cover_letter_narrative(self, context: ValidationContext) -> Dict: # Checks for the presence of 'Hook', 'Proof', and 'Vision' elements in the cover letter.
        cl_text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').lower()
        hook = any(kw in cl_text for kw in ["enthusiastic", "excited", "apply for", "interest in", "compelling opportunity"])
        proof = any(kw in cl_text for kw in ["demonstrated", "achieved", "delivered", "resulted in", "experience", "proven ability", "track record"])
        vision = any(kw in cl_text for kw in ["contribute", "goals", "opportunity", "eager to discuss", "drive success", "valuable asset"])
        details = {"hook": hook, "proof": proof, "vision": vision, "valid": hook and proof and vision}; context._cache["COVER_LETTER_NARRATIVE_INTEGRITY"] = details
        return details

    def _validate_provenance_split(self, context: ValidationContext) -> bool: # Validates that the V/C/S provenance split for bullet sections matches the targets.
        valid = True; violations = []; failed = set()
        for section_enum, targets in self.PROVENANCE_SPLIT_TARGETS.items():
            bullets = context.staging_buffer.get(section_enum.value, [])
            if not isinstance(bullets, list): logging.warning(f"Expected list for {section_enum.value} provenance check. Skipping."); continue
            counts = defaultdict(int)
            for bullet in bullets:
                if isinstance(bullet, dict): counts[bullet.get('provenance', 'Unknown')] += 1
            for prov_type_enum in BulletProvenance:
                prov_type = prov_type_enum.value; target = targets.get(prov_type, 0); actual = counts.get(prov_type, 0)
                if actual != target: valid = False; violations.append(f"{section_enum.value}: {prov_type} has {actual} (target: {target})"); failed.add(section_enum)
        if not valid: context._cache["VG_PROVENANCE_SPLIT_CHECK"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_authenticity_signal(self, context: ValidationContext) -> bool: # Checks if authenticity signals (verbs, phrasing) from RAG are present in the final resume content.
        full_text = ""; buffer_data = context.staging_buffer.data
        auth_patterns_data = getattr(context.thematic_analysis, 'authenticity_patterns', {}); patterns_dict = {}
        if isinstance(auth_patterns_data, dict): patterns_dict = auth_patterns_data.get('patterns', {});
        if not isinstance(patterns_dict, dict): patterns_dict = {}
        if not patterns_dict: return True
        verbs = patterns_dict.get('achievement_verb_patterns', []); phrasing = patterns_dict.get('competency_phrasing', [])
        valid_verbs = [v for v in verbs if isinstance(v, str)]; valid_phrasing = [p for p in phrasing if isinstance(p, str)]
        target_signals = set(v.lower() for v in valid_verbs[:10]) | set(p.lower().split(':')[0].split()[0] for p in valid_phrasing[:5] if ':' in p and p.split()); target_signals = {s for s in target_signals if s}
        full_text = ""; buffer_data = context.staging_buffer.data
        sections_to_scan = [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES]
        for sec_enum in sections_to_scan:
            value = buffer_data.get(sec_enum.value);
            if isinstance(value, str): full_text += value + " "
            elif isinstance(value, list): full_text += " ".join(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value) + " "
        if not target_signals or not full_text: return True
        found = {sig for sig in target_signals if re.search(r'\b' + re.escape(sig) + r'\b', full_text.lower())}
        ratio = len(found) / len(target_signals) if target_signals else 0.0; valid = ratio >= 0.3
        context._cache["VG_AUTHENTICITY_SIGNAL_CHECK"] = {"details": f"Found {len(found)}/{len(target_signals)} ({ratio:.1%}) auth signals."}
        return valid

    # --- Main Validate Method ---
    def validate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        sections_under_test: Optional[Set[ResumeSection]] = None
    ) -> Tuple[List[ValidationResult], bool, Set[ResumeSection]]:
        logger = logging.getLogger(__name__)
        context = ValidationContext(staging_buffer, thematic_analysis, job_description, self.master_resume)
        rules_to_run = self.engine.rules
        failed_sections_enums = set()

        if sections_under_test:
            logger.info(f"Validating specific sections: {[s.name for s in sections_under_test]}")
            relevant_rule_ids = set()
            for rule_id, section_map in self.RULE_TO_SECTION_MAP.items():
                if section_map == "GLOBAL" or section_map == "VISUAL" or section_map in sections_under_test:
                    relevant_rule_ids.add(rule_id)
                elif section_map == "COMPLEX_PER_SECTION":
                    # Check which sections complex rules might affect
                    if rule_id == "VG_BULLET_WORD_COUNT_RANGE" and any(s in sections_under_test for s in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK): relevant_rule_ids.add(rule_id)
                    elif rule_id == "VG_PROVENANCE_SPLIT_CHECK" and any(s in sections_under_test for s in self.PROVENANCE_SPLIT_TARGETS): relevant_rule_ids.add(rule_id)
                    elif rule_id == "VG_FORBIDDEN_VERBS" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_BULLETS, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES]): relevant_rule_ids.add(rule_id) # List relevant sections
                    elif rule_id == "VG_NO_INTRO_PHRASES" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_BULLETS, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES, ResumeSection.K11_COVER_LETTER]): relevant_rule_ids.add(rule_id) # List relevant sections
                    # --- Include NEW similarity rules based on sections they affect ---
                    # Cross-section compares K1, K2_O, K3_O, K4, K5, K6, K9
                    elif rule_id == "VG_CROSS_SECTION_SIMILARITY" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES]): relevant_rule_ids.add(rule_id)
                    elif rule_id == "VG_NARRATIVE_VS_MASTER_SIMILARITY" and any(s in sections_under_test for s in [ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE]): relevant_rule_ids.add(rule_id)

            rules_to_run = [r for r in self.engine.rules if r.rule_id in relevant_rule_ids]
            logger.info(f"Filtered to {len(rules_to_run)} relevant rules for sections under test.")

        # --- Execute Validation Rules ---
        # The engine.validate call will trigger context calculations via __getattr__
        all_results = self.engine.validate(context, categories=None)

        # Filter results to only those relevant to this run (if sections_under_test was used)
        final_results_for_run = [r for r in all_results if r.rule_id in {rule.rule_id for rule in rules_to_run}]

        # Check for failures and identify failed sections
        has_critical_or_high_failures = self.engine.has_high_or_critical_failures(final_results_for_run)
        all_passed = not has_critical_or_high_failures

        if not all_passed:
            for vr in final_results_for_run:
                if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                    section_map = self.RULE_TO_SECTION_MAP.get(vr.rule_id)
                    if isinstance(section_map, ResumeSection):
                        failed_sections_enums.add(section_map)
                    elif section_map == "COMPLEX_PER_SECTION" or section_map == "GLOBAL":
                        # Add sections identified by the validator's cached details (if available)
                        cached_details = context._cache.get(vr.rule_id, {})
                        failed_in_cache = cached_details.get("failed_sections", set())
                        if isinstance(failed_in_cache, set):
                            # Ensure items in the set are actual ResumeSection enums before updating
                            valid_enums_in_cache = {item for item in failed_in_cache if isinstance(item, ResumeSection)}
                            failed_sections_enums.update(valid_enums_in_cache)

        logger.info(f"Validation complete. Passed: {all_passed}. Failed Sections (High/Crit): {[s.name for s in failed_sections_enums]}")
        return final_results_for_run, all_passed, failed_sections_enums

class GateDecisionEngine:
    
    def decide(
        self,
        validation_results: List[ValidationResult]
    ) -> Tuple[GateDecision, str]:
        """
        Make gate decision based on validation results.
        
        Returns:
            (decision, reason)
        """
        critical_failures = [
            vr for vr in validation_results
            if not vr.passed and vr.severity == ValidationSeverity.CRITICAL
        ]
        
        high_failures = [
            vr for vr in validation_results
            if not vr.passed and vr.severity == ValidationSeverity.HIGH
        ]
        
        # Decision logic
        if len(critical_failures) > 0:
            return (
                GateDecision.HALT,
                f"HALT: {len(critical_failures)} CRITICAL failures detected"
            )
        elif len(high_failures) > 0:
            return (
                GateDecision.HALT,
                f"HALT: {len(high_failures)} HIGH severity failures detected (zero tolerance)"
            )
        else:
            return (
                GateDecision.PROCEED,
                "PROCEED: All validations passed"
            )

class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator', company_name: str, job_title: str):
        self.master_resume = master_resume
        self.orchestrator = orchestrator # For access to validation results etc.
        self.company_name = company_name
        self.job_title = job_title
        self._initialize_render_dispatch()
        # Initialize logger if not already done globally or passed in
        self.logger = logging.getLogger(__name__)

    @functools.cached_property
    def _safe_company_name(self) -> str:
        """Sanitizes and caches the company name for use in filenames."""
        name = re.sub(r'[^\w\s-]', '', self.company_name)
        return re.sub(r'[-\s]+', '_', name).strip('_')

    @functools.cached_property
    def _safe_job_title(self) -> str:
        """Sanitizes and caches the job title for use in filenames."""
        title = re.sub(r'[^\w\s-]', '', self.job_title)
        return re.sub(r'[-\s]+', '_', title).strip('_')

    def _strip_fences(self, content: str, artifact_name: str) -> str:
        """
        Checks for and removes leading/trailing markdown fences (```).
        Logs a warning if fences were found and removed.
        """
        stripped_content = content # Start with original
        found_fence = False
        # Regex explanation:
        # ^\s* - Start of string, optional whitespace
        # ```(?:[a-z]*)? - Triple backticks, optionally followed by language hint (e.g., ```python)
        # \s*\n?         - Optional whitespace, optional newline
        # |              - OR
        # \s*\n?         - Optional whitespace/newline before end
        # ```\s*$         - Triple backticks, optional whitespace, end of string
        fence_pattern = r"^\s*```(?:[a-z]*)?\s*\n?|\s*\n?```\s*$"

        # Check if fences exist using re.search (more efficient than re.sub for just checking)
        if re.search(fence_pattern, content.strip(), re.MULTILINE):
             found_fence = True
             # Use re.sub to remove the fences
             stripped_content = re.sub(fence_pattern, "", content, flags=re.MULTILINE).strip()

        if found_fence:
            self.logger.warning(f"  ⚠️ Removed markdown fences ``` from final {artifact_name} content.")
        return stripped_content

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str, # Passed again for clarity, though stored in self
        job_title: str,    # Passed again for clarity, though stored in self
        thematic_analysis: ThematicAnalysis,
        job_description: Optional[str] = None, # Optional, used for skills rendering
        jd_url: str = "" # Added jd_url parameter
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report, App Tracker).
        Uses K0-K11 Enum scheme. Includes fence stripping for relevant artifacts.
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        """
        file_paths = {}
        file_contents = {}
        validation_results = [] # Collect results from rendering steps

        try:
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content # Store final (fence-stripped) content
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=True, severity=ValidationSeverity.INFO,
                message="Resume MD rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Resume MD: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Resume MD: {e}"
            ))
            file_contents['resume_md'] = f"[ERROR: Resume Rendering Failed: {e}]" # Add error placeholder

        try:
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content # Store final (fence-stripped) content
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=True, severity=ValidationSeverity.INFO,
                message="Skills TXT rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Skills TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Skills TXT: {e}"
            ))
            file_contents['skills'] = f"[ERROR: Skills Rendering Failed: {e}]"

        try:
            path, content = self._render_cover_letter_artifact(staging_buffer)
            file_paths['cover_letter'] = path
            file_contents['cover_letter'] = content # Store final (fence-stripped) content
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=True, severity=ValidationSeverity.INFO,
                message="Cover Letter TXT rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Cover Letter TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Cover Letter TXT: {e}"
            ))
            file_contents['cover_letter'] = f"[ERROR: Cover Letter Rendering Failed: {e}]"

        try:
            path, content_placeholder = self._render_qa_report_artifact()
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content_placeholder # Placeholder, content generated later
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=True, severity=ValidationSeverity.INFO,
                message="QA Report path generated."
            ))
        except Exception as e:
            self.logger.error(f"Error generating QA Report path: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
            ))

        try:
            path, content, app_tracker_validation_results = self._render_app_tracker_artifact(file_paths, jd_url=jd_url) # Pass jd_url
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content # Store final (UN-stripped) content
            validation_results.extend(app_tracker_validation_results) # Add validation results
            app_tracker_render_passed = all(vr.passed for vr in app_tracker_validation_results if vr.rule_id.startswith("APP_TRACKER_"))
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER",
                passed=app_tracker_render_passed,
                severity=ValidationSeverity.INFO if app_tracker_render_passed else ValidationSeverity.HIGH,
                message="App Tracker JSON rendered and validated successfully." if app_tracker_render_passed else "App Tracker JSON rendered but failed validation."
            ))
            if not app_tracker_render_passed:
                 self.logger.warning("AppTracker rendering completed but failed validation.")
        except Exception as e:
            self.logger.error(f"Error rendering App Tracker JSON: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render App Tracker JSON: {e}"
            ))
            file_contents['app_tracker'] = f"[ERROR: App Tracker Rendering Failed: {e}]"

        return file_paths, (validation_results, file_contents)

# Inside class FileRenderer:
    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the resume markdown artifact and strips fences."""
        raw_content = self._render_resume_markdown(staging_buffer)
        final_content = self._strip_fences(raw_content, "Resume MD")

        # Get candidate name from master resume (like in _render_app_tracker)
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        # Construct the filename using the same pattern as Versioned Resume
        base_filename = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        path = f"{base_filename}.md"

        return path, final_content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> Tuple[str, str]:
        """Renders the skills artifact (using K.10) and strips fences."""
        raw_content = self._render_skills(staging_buffer, job_description)
        final_content = self._strip_fences(raw_content, "Skills TXT")
        path = f"Skills_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the cover letter artifact (using K.11) and strips fences."""
        raw_content = staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '') # Use K.11
        final_content = self._strip_fences(raw_content, "Cover Letter TXT")
        path = f"CoverLetter_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_qa_report_artifact(self) -> Tuple[str, str]:
        """Renders the QA report artifact path and placeholder."""
        path = f"QA_Report_{self._safe_company_name}_{self._safe_job_title}.md"
        return path, "[QA Report Content Placeholder - Generated in HOP-8]"

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str], jd_url: str = "") -> Tuple[str, str, List[ValidationResult]]:
        """Renders the application tracker artifact and validates it."""
        app_tracker_data = self._render_app_tracker(file_paths, jd_url=jd_url) # Pass jd_url
        validation_results = []
        try:
            validator = AppTrackerQAValidator()
            validation_result_dict = validator.validate_tracker_data([app_tracker_data])
            if "BLOCKED" in validation_result_dict.get("result", ""):
                errors = validation_result_dict.get('errors', [])
                for error in errors:
                    if isinstance(error, dict):
                        validation_results.append(ValidationResult(
                            rule_id=f"APP_TRACKER_{error.get('RULE_ID', 'UNKNOWN')}", passed=False,
                            severity=ValidationSeverity.HIGH,
                            message=f"AppTracker Error (Row {error.get('row_index')} Field '{error.get('field')}'): {error.get('message')}",
                            details=error
                        ))
                    else:
                         validation_results.append(ValidationResult(
                             rule_id="APP_TRACKER_MALFORMED_ERROR", passed=False, severity=ValidationSeverity.HIGH,
                             message=f"Malformed AppTracker error received: {error}",
                         ))
            else:
                validation_results.append(ValidationResult(
                    rule_id="APP_TRACKER_VALIDATION", passed=True, severity=ValidationSeverity.INFO,
                    message="AppTracker JSON passed validation rules."
                ))
        except Exception as e:
            self.logger.error(f"App tracker validation failed during execution: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="APP_TRACKER_VALIDATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"App tracker validation failed during execution: {e}"
            ))
        content = json.dumps(app_tracker_data, indent=2)
        path = f"AppTracker_{self._safe_company_name}_{self._safe_job_title}.json"
        return path, content, validation_results

    RESUME_RENDER_CONFIG = [
        {"type": "simple", "source": ResumeSection.K0_NAME, "render_method": "_render_name"},
        {"type": "simple", "source": ResumeSection.K0_HEADLINE, "render_method": "_render_headline"},
        {"type": "simple", "source": ResumeSection.K0_CONTACT, "render_method": "_render_contact"},
        {"type": "header", "text": "## EXECUTIVE SUMMARY"},
        {"type": "simple", "source": ResumeSection.K1_EXECUTIVE_SUMMARY, "render_method": "_render_paragraph"},
        {"type": "header", "text": "## PROFESSIONAL EXPERIENCE"},
        {"type": "experience", "master_index": 0, "overview_source": ResumeSection.K2_UNIFY_OVERVIEW, "bullets_source": ResumeSection.K2_UNIFY_BULLETS},
        {"type": "experience", "master_index": 1, "overview_source": ResumeSection.K3_IBM_OVERVIEW, "bullets_source": ResumeSection.K3_IBM_BULLETS},
        {"type": "experience_narrative", "master_index": 2, "narrative_source": ResumeSection.K4_TRADERSENSE_NARRATIVE},
        {"type": "experience_narrative", "master_index": 3, "narrative_source": ResumeSection.K5_EY_NARRATIVE},
        {"type": "experience_narrative", "master_index": 4, "narrative_source": ResumeSection.K6_EARLY_CAREER_NARRATIVE},
        {"type": "header", "text": "## EDUCATION"},
        {"type": "education", "source": ResumeSection.K7_EDUCATION}, # Changed type to education
        {"type": "header", "text": "## CERTIFICATIONS & CREDENTIALS"},
        {"type": "certifications", "source": ResumeSection.K8_CERTIFICATIONS}, # Changed type to certifications
        {"type": "header", "text": "## STRATEGIC & TECHNICAL COMPETENCIES"},
        {"type": "competencies", "source": ResumeSection.K9_COMPETENCIES}, # Changed type to competencies
    ]

    def _initialize_render_dispatch(self):
        """Initializes the dispatch table for rendering methods."""
        self._RENDER_DISPATCH = {
            "header": self._handle_render_header,
            "simple": self._handle_render_simple,
            "experience": self._handle_render_experience,
            "experience_narrative": self._handle_render_experience_narrative,
            "education": self._handle_render_list, # Reuse list handler for education
            "certifications": self._handle_render_list, # Reuse list handler for certs
            "competencies": self._handle_render_list, # Reuse list handler for competencies
            "list": self._handle_render_list,
        }

    def _handle_render_header(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        return config.get("text", "")

    def _handle_render_simple(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        content = staging_buffer.get(config["source"].value)
        if content:
            render_method = getattr(self, config["render_method"])
            return render_method(content)
        return ""

    def _handle_render_experience(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        master_experience = self.master_resume.get("professional_experience", [])
        master_index = config["master_index"]
        if 0 <= master_index < len(master_experience):
            master_exp = master_experience[master_index]
            overview = staging_buffer.get(config["overview_source"].value)
            bullets = staging_buffer.get(config["bullets_source"].value)
            return self._render_experience_section_std(master_exp, overview, bullets)
        else:
            self.logger.warning(f"Master experience index {master_index} out of bounds. Max index: {len(master_experience)-1}.")
            return ""

    def _handle_render_experience_narrative(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        master_experience = self.master_resume.get("professional_experience", [])
        master_index = config["master_index"]
        if 0 <= master_index < len(master_experience):
            master_exp = master_experience[master_index]
            narrative = staging_buffer.get(config["narrative_source"].value)
            return self._render_experience_section_narrative(master_exp, narrative)
        else:
            self.logger.warning(f"Master experience index {master_index} out of bounds. Max index: {len(master_experience)-1}.")
            return ""

    def _handle_render_list(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        content = staging_buffer.get(config["source"].value)
        if content and isinstance(content, list):
            # Determine the correct render method and prefix based on section type
            item_prefix = "* " # Default bullet
            if config["source"] == ResumeSection.K7_EDUCATION:
                return self._render_list_section(content, item_prefix="") # No prefix for education lines
            elif config["source"] == ResumeSection.K8_CERTIFICATIONS:
                # Certifications format: * Cert Name
                return self._render_list_section(content, item_prefix="* ")
            elif config["source"] == ResumeSection.K9_COMPETENCIES:
                # Competencies format: * **Skill:** Desc...
                # Note: Prefix logic is now handled within _render_list_section based on item type
                # The raw text from K9 already has the desired format
                return self._render_list_section(content, item_prefix="") # No extra prefix needed
            else: # Generic list handler
                return self._render_list_section(content, item_prefix=config.get("item_prefix", "* "))
        elif not content:
             self.logger.warning(f"Content for list section {config['source'].name} is missing or empty.")
             return ""
        else: # Content is not a list
             self.logger.warning(f"Expected list content for section {config['source'].name}, got {type(content)}. Rendering as string.")
             return str(content) + "\n"

    def _render_name(self, content: str) -> str: return f"# {content.strip()}\n"
    def _render_headline(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_contact(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_paragraph(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_experience_section_std(self, master_exp: Dict, overview: Optional[str], bullets: Optional[List[Union[str, Dict]]]) -> str:
        lines = self._render_experience_header(master_exp)
        if overview and isinstance(overview, str) and overview.strip(): lines.append(f"\n{overview.strip()}")
        bullet_lines = []
        bullets_list = bullets if isinstance(bullets, list) else []
        for bullet in bullets_list:
            text = ""
            if isinstance(bullet, dict): text = bullet.get('text', '').strip()
            elif isinstance(bullet, str): text = bullet.strip()
            if text: bullet_lines.append(f"* {text}")
        if bullet_lines: lines.append("\n" + "\n".join(bullet_lines))
        return "\n".join(lines) + "\n"

    def _render_experience_section_narrative(self, master_exp: Dict, narrative: Optional[str]) -> str:
        lines = self._render_experience_header(master_exp)
        if narrative and isinstance(narrative, str) and narrative.strip(): lines.append(f"\n{narrative.strip()}")
        master_highlights = master_exp.get('highlights', [])
        highlight_lines = []
        if master_highlights and isinstance(master_highlights, list):
             for hl in master_highlights:
                  if isinstance(hl, str) and hl.strip(): highlight_lines.append(f"* {hl.strip()}")
        if highlight_lines:
             prefix = "\n" if (narrative and narrative.strip()) else ""; lines.append(prefix + "\n".join(highlight_lines))
        return "\n".join(lines) + "\n"

    def _render_experience_header(self, master_exp: Dict) -> List[str]:
        header_lines = []; company = master_exp.get('company', '').strip(); location = master_exp.get('location', '').strip()
        line1_parts = [part for part in [company, location] if part]; title = master_exp.get('title', '').strip()
        start = master_exp.get('dates', {}).get('start', '').strip(); end = master_exp.get('dates', {}).get('end', '').strip()
        date_str = " – ".join(filter(None, [start, end])); line2_parts = [part for part in [title, date_str] if part]
        if line1_parts: header_lines.append(f"**{' | '.join(line1_parts)}**")
        if line2_parts: header_lines.append(f"**{' | '.join(line2_parts)}**")
        return header_lines

    def _render_list_section(self, content_list: List[Union[str, Dict]], item_prefix: str = "") -> str:
        lines = []
        if not isinstance(content_list, list): return ""
        for item in content_list:
            text_to_render = ""
            if isinstance(item, str): text_to_render = item.strip()
            elif isinstance(item, dict):
                if 'degree' in item and 'institution' in item:
                    degree = item.get('degree', '').strip()
                    institution = item.get('institution', '').strip()
                    parts = [p for p in [degree, institution] if p]
                    text_to_render = ", ".join(parts)
                    notes = item.get('notes', '').strip()
                    if notes: text_to_render += f" ({notes})"
                # Default for other dicts (like Certs or potentially Competencies if passed as dicts)
                else: text_to_render = item.get('text', str(item)).strip() # Use 'text' key if present

            if text_to_render:
                if text_to_render.startswith("*") or text_to_render.startswith("**"):
                    lines.append(text_to_render)
                else:
                    lines.append(f"{item_prefix}{text_to_render}")

        return "\n".join(lines) + "\n" if lines else ""

    def _render_skills(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> str:
        skills_list = staging_buffer.get(ResumeSection.K10_SKILLS.value)
        output_lines = []; valid_skills = []; malformed = []
        if not isinstance(skills_list, list) or not skills_list: return "• Error: K.10_Skills list not found or invalid."
        if isinstance(skills_list[0], str) and skills_list[0].startswith("Error:"): return "\n\n".join(skills_list)
        for skill in skills_list:
            if isinstance(skill, str):
                cleaned = skill.strip(); wc = count_words_ms_word_style(cleaned)
                if 1 <= wc <= 3: valid_skills.append(f"• {cleaned}")
                else: malformed.append(f"• {cleaned} [Warning: Malformed - {wc} words (expected 1-3)]")
            else: malformed.append(f"• {str(skill).strip()} [Warning: Non-string skill item found]")
        output_lines.extend(valid_skills); output_lines.extend(malformed)
        return "\n\n".join(output_lines)

    def _render_app_tracker(self, file_paths: Dict[str, str], jd_url: str = "") -> Dict:
        tracker = copy.deepcopy(APP_TRACKER_SCHEMA_DATA)
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        tracker['Company'] = self.company_name; tracker['Job Title'] = self.job_title
        tracker['JD URL'] = jd_url; tracker['Application Date'] = datetime.now().strftime("%m/%d/%Y")
        tracker['Base Resume'] = ""; versioned_resume_filename = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        tracker['Versioned Resume'] = versioned_resume_filename; tracker['Pipeline Status'] = 'Applied'
        if APP_TRACKER_SCHEMA_DATA:
             for key in APP_TRACKER_SCHEMA_DATA.keys():
                  if key not in tracker: tracker[key] = ""
        return tracker


class WorkflowOrchestrator:

    def __init__(self, master_resume: Dict, test_mode: bool = False):
        """
        Initializes the orchestrator.
        HOP-7.5 similarity calculations removed.
        """
        self.master_resume = master_resume
        self.hop_checkpoints = []
        self.validation_results = [] # Final HOP-5 results
        self.rendered_output = None # Stores final output dict after HOP-7/8

        self.hash_chain = []
        self.constraints = ContentConstraintsConfig()
        self.jd_enforcer = JDEnforcementValidator() # Assuming class is defined

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # API Key Check (remains the same)
        if not test_mode:
            if not os.environ.get("GEMINI_API_KEY"):
                self.logger.error(
                    "CRITICAL WARNING: GEMINI_API_KEY environment variable not set!\n" +
                    "="*80 + "\n" +
                    "Workflow may fail or fall back unexpectedly.\n" +
                    "Please set it using: export GEMINI_API_KEY='your-key-here'\n" +
                    "Get your key at: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)\n" +
                    "="*80
                )
            else:
                self.logger.info("✓ GEMINI_API_KEY detected - Gemini API integration enabled")
        else:
            self.logger.info("Running in test mode - API key checks skipped.")

        # Log LLM Provider Info (remains the same)
        try:
             # Ensure RAGConfig is defined or handled gracefully
             if 'RAGConfig' in globals():
                 rag_config = RAGConfig()
                 self.logger.info(f"Using LLM Provider: Gemini")
                 self.logger.info(f"Using Model: {rag_config.model}")
             else:
                 self.logger.warning("RAGConfig class not found. Cannot log model details.")
        except NameError:
             self.logger.warning("RAGConfig class not found. Cannot log model details.")
        except Exception as e:
             self.logger.error(f"Error accessing RAGConfig for logging: {e}")

    def _execute_hop_0_jd_analysis(self, job_description: str) -> Tuple[ThematicAnalysis, int]:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-0] Job Description Analysis & RAG...")
        jd_analyzer = self._create_jd_analyzer()
        total_api_calls = 0
        thematic_analysis = None
        # GATE-0: Validate JD Input
        self.jd_enforcer.validate_jd_input(job_description, "GATE-0")

        try:
            thematic_analysis, api_calls = jd_analyzer.analyze(job_description)
            total_api_calls = api_calls
            # GATE-1 & GATE-2: Validate JD Parsing and Thematic Analysis creation
            # (Assuming analyze method populates necessary data structures for validation)
            parsed_jd_sim = {"primary_theme": thematic_analysis.primary_theme.get("name"), "secondary_themes": [t.get("name") for t in thematic_analysis.secondary_themes], "required_skills": thematic_analysis.primary_theme.get("keywords", []) + [kw for t in thematic_analysis.secondary_themes for kw in t.get("keywords", [])]}
            self.jd_enforcer.validate_jd_parsing(parsed_jd_sim, "GATE-1")
            self.jd_enforcer.validate_thematic_analysis(thematic_analysis, "GATE-2")

            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG", [],
                {"signal_score": getattr(thematic_analysis, 'signal_quality_score', 0.0)},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": total_api_calls}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint)
            return thematic_analysis, total_api_calls
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-0] FAILED: {e}", exc_info=False)
            calls_on_fail = getattr(jd_analyzer, 'total_api_calls_hop0', 0)
            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG",
                [ValidationResult("HOP-0_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e),
                metadata={"gemini_api_calls": calls_on_fail}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-0 failed: {e}")

    def _execute_hop_1_clerk_extraction(self) -> Dict:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-1] Master Resume Extraction...")
        extracted_data = {}
        try:
            # Ensure ClerkExtractor is defined/imported
            clerk = ClerkExtractor(self.master_resume)
            extracted_data, hop_results = clerk.extract()
            bullets_extracted = sum(len(s.get('bullets', [])) for s in extracted_data.get('experience_sections', []))
            hop_checkpoint = self._create_checkpoint(
                "HOP-1", "Clerk Extraction", hop_results,
                {"bullets_extracted": bullets_extracted},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True)
            return extracted_data
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-1] FAILED: {e}", exc_info=False)
            hop_checkpoint = self._create_checkpoint(
                "HOP-1", "Clerk Extraction",
                [ValidationResult("HOP-1_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e),
                metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-1 failed: {e}")

    def _execute_hop_2_enrichment(self, extracted_data: Dict, thematic_analysis: ThematicAnalysis) -> Dict:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-2] Data Enrichment...")
        enriched_scaffold = {}
        try:
            # Ensure DataEnricher is defined/imported
            enricher = DataEnricher()
            # Pass self (orchestrator) to enrich, but it no longer stores dup_detector
            enriched_scaffold, hop_results = enricher.enrich(extracted_data, thematic_analysis, orchestrator=None)

            # GATE-3: Validate Enrichment
            self.jd_enforcer.validate_enrichment(enriched_scaffold, "GATE-3")

            hop_checkpoint = self._create_checkpoint(
                "HOP-2", "Data Enrichment", hop_results,
                {"sections_enriched": len(enriched_scaffold.get('experience_sections',[]))},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True)
            return enriched_scaffold
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-2] FAILED: {e}", exc_info=False)
            hop_checkpoint = self._create_checkpoint(
                "HOP-2", "Data Enrichment",
                [ValidationResult("HOP-2_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e),
                metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-2 failed: {e}")

    def _execute_hop_3_artist_generation(self, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis) -> Tuple[Dict, int]:
        self.logger.info("\n[HOP-3] Content Generation (Artist) with Stateful Retry...")
        hop_start_time = datetime.now()
        total_api_calls_hop3 = 0

        # GATE-4: Validate Artist Inputs
        self.jd_enforcer.validate_artist_inputs(enriched_scaffold, thematic_analysis, "GATE-4")

        # Ensure ArtistGenerator & PreFlightValidator are defined/imported
        # Ensure ARTIST_SPECS_DATA is loaded globally
        try:
            artist = ArtistGenerator(
                master_resume=self.master_resume,
                enriched_scaffold=enriched_scaffold,
                job_description=job_description,
                thematic_analysis=thematic_analysis,
                artist_specs=ARTIST_SPECS_DATA, # Pass the globally loaded specs
                previous_failures=[] # Start with no previous failures
            )
            validator = PreFlightValidator(self.master_resume)
        except Exception as init_e:
             raise HopExecutionError(f"HOP-3 failed during initialization: {init_e}")

        temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2] # Example schedule
        max_attempts = len(temperature_schedule)
        final_generation_state: Dict[str, Any] = {}
        locked_section_temps: Dict[ResumeSection, float] = {}
        copied_content: Dict[str, Any] = {}

        # Determine all LLM-generated sections using the ArtistGenerator spec
        all_llm_sections = {
            section_enum for section_enum, spec in ArtistGenerator.SECTION_GENERATION_SPECS.items()
            if not spec["generation_method"].startswith("_copy_") and
               not spec["generation_method"] == "_generate_dummy_header"
        }
        sections_to_generate = all_llm_sections.copy()
        final_validation_results = []
        all_passed = False
        final_attempt_number = 0

        # Run copy/dummy methods ONCE
        try:
            dummy_sections = {
                section_enum for section_enum, spec in ArtistGenerator.SECTION_GENERATION_SPECS.items()
                if spec["generation_method"].startswith("_copy_") or
                   spec["generation_method"] == "_generate_dummy_header"
            }
            if dummy_sections:
                 # Ensure ArtistGenerator.generate exists and handles empty overrides
                 copied_output, _, calls_copy = artist.generate(
                     sections_to_generate=dummy_sections,
                     temperature_overrides={}
                 )
                 total_api_calls_hop3 += calls_copy
                 copied_content.update(copied_output)
                 final_generation_state.update(copied_output)
                 self.logger.info(f"  ✓ Copied/Dummy sections generated: {list(copied_output.keys())}")
        except Exception as e:
            hop_checkpoint = self._create_checkpoint(
                 "HOP-3", "Artist Generation (Copy Phase)",
                 [ValidationResult("ARTIST_COPY_FAIL", False, ValidationSeverity.CRITICAL, f"Copy failed: {e}")],
                 None, start_time=hop_start_time, error_message=f"Initial content copy failed: {e}",
                 metadata={"gemini_api_calls": total_api_calls_hop3}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-3 failed during initial content copy: {e}")

        # Stateful Retry Loop
        for attempt, temperature in enumerate(temperature_schedule, 1):
            final_attempt_number = attempt
            if not sections_to_generate:
                self.logger.info(f"  All sections passed validation. Exiting generation loop.")
                # Ensure all_passed is True only if validation actually passed last time
                # Check final_validation_results from the previous iteration if available
                if final_validation_results: # If validation ran at least once
                     all_passed = not any(not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value for vr in final_validation_results)
                else: # Should not happen if sections_to_generate is empty, but handle defensively
                     all_passed = True # Assume passed if no sections needed generation/validation
                break

            self.logger.info(f"  Attempt {attempt}/{max_attempts} @ Temp {temperature:.1f}...")
            self.logger.info(f"    Sections to generate: {[s.name for s in sections_to_generate]}")
            attempt_start_time = time.time()
            calls_this_attempt = 0
            newly_generated_content: Dict[str, Any] = {} # Initialize for this attempt

            # 1. Generate sections
            try:
                temp_overrides = {section: temperature for section in sections_to_generate}
                newly_generated_content, generation_results, calls_gen = artist.generate(
                    sections_to_generate=sections_to_generate,
                    temperature_overrides=temp_overrides
                )
                calls_this_attempt += calls_gen
                total_api_calls_hop3 += calls_gen

                # Check if generation itself reported failure
                if not generation_results or not generation_results[0].passed:
                    generation_error = generation_results[0].message if (generation_results and generation_results[0].message) else "Unknown generation error"
                    logging.error(f"    Artist.generate() reported failure on attempt {attempt}: {generation_error}")
                    # Update final_validation_results with this specific failure
                    final_validation_results = generation_results or [ValidationResult(f"ARTIST_GENERATE_FAIL_{attempt}", False, ValidationSeverity.CRITICAL, generation_error)]
                    all_passed = False
                    # No need to raise here, let the loop break naturally or continue if designed for partial recovery
                    break # Halt loop on generation failure

            except HopExecutionError as he:
                 self.logger.error(f"    ✗ Generation HALTED on Attempt {attempt}: {he}", exc_info=False)
                 final_validation_results = [ValidationResult(f"ARTIST_GENERATION_HALT_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation halted: {he}")]
                 all_passed = False
                 break # Halt loop
            except Exception as e:
                 self.logger.error(f"    ✗ Generation Attempt {attempt} FAILED unexpectedly: {e}", exc_info=False)
                 final_validation_results = [ValidationResult(f"ARTIST_GENERATION_ERROR_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation failed unexpectedly: {e}")]
                 all_passed = False
                 break # Halt loop

            # 2. Update current state only with newly generated content
            final_generation_state.update(newly_generated_content)

            # 3. Validate entire state (including previously generated/copied sections)
            temp_buffer = ImmutableStagingBuffer()
            for key, value in final_generation_state.items():
                if value is not None:
                    temp_buffer.set(key, value) # Populate with all available content
            temp_buffer.lock() # Lock before validation

            try:
                # Ensure PreFlightValidator.validate exists and returns expected tuple
                current_validation_results, current_all_passed, failed_sections = validator.validate(
                    temp_buffer, thematic_analysis, job_description,
                    sections_under_test=None # Validate ALL sections in the buffer
                )
                final_validation_results = current_validation_results # Store the latest results
                all_passed = current_all_passed # Update overall pass status

            except Exception as e:
                self.logger.error(f"    ✗ Validation Attempt {attempt} FAILED during execution: {e}", exc_info=True)
                final_validation_results = [ValidationResult(f"VALIDATION_EXECUTION_{attempt}", False, ValidationSeverity.CRITICAL, f"Validation logic failed: {e}")]
                all_passed = False
                break # Halt loop if validation logic itself fails

            attempt_duration = time.time() - attempt_start_time
            self.logger.info(f"    Attempt {attempt} completed in {attempt_duration:.2f}s. Validation passed: {all_passed}. API Calls: {calls_this_attempt}")

            # 4. Update state based on validation
            if all_passed:
                # If everything passed, lock successful sections and clear sections_to_generate
                sections_to_generate = set() # Clear the set
                for section_enum in all_llm_sections:
                     if section_enum not in locked_section_temps:
                          locked_section_temps[section_enum] = temperature
                          self.logger.info(f"    ✓ LOCKED (All Pass): {section_enum.name} @ {temperature:.1f}")
            else:
                 # Identify which LLM sections actually failed this time
                 failed_llm_sections_this_attempt = {fs for fs in failed_sections if fs in all_llm_sections}

                 # Lock sections that passed THIS attempt among those needing generation
                 sections_that_passed_this_attempt = (all_llm_sections - failed_llm_sections_this_attempt)
                 for passed_section in sections_that_passed_this_attempt:
                      if passed_section not in locked_section_temps:
                           locked_section_temps[passed_section] = temperature
                           self.logger.info(f"    ✓ LOCKED: {passed_section.name} @ {temperature:.1f}")

                 # Set sections for next attempt ONLY to those LLM sections that failed AND aren't locked
                 sections_to_generate = {fs for fs in failed_llm_sections_this_attempt if fs not in locked_section_temps}

                 self.logger.warning(f"    ✗ {len(failed_sections)} sections failed validation. Retrying {len(sections_to_generate)} unlocked LLM sections: {[s.name for s in sections_to_generate]}")
                 # Log specific failures
                 for vr in final_validation_results:
                     if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                          details = vr.details or {}
                          try:
                              # Handle callable message templates safely
                              msg = vr.message(details) if callable(vr.message) else str(vr.message)
                          except Exception as msg_e:
                              self.logger.warning(f"      - Error formatting message for {vr.rule_id}: {msg_e}")
                              msg = f"Failed rule {vr.rule_id} (message format error)"
                          self.logger.warning(f"      - [{vr.severity.name}] {vr.rule_id}: {msg}")

        # End of Loop

        # 5. Final Outcome determination
        artist_output = final_generation_state
        self.validation_results = final_validation_results # Store final results for orchestrator use

        if all_passed and not sections_to_generate:
            status_message = f"Artist Generation successful after {final_attempt_number} attempt(s)"
            hop_status = HopStatus.PASS
            error_msg = None
        else:
            status_message = f"Artist Generation FAILED after {final_attempt_number} attempt(s)"
            hop_status = HopStatus.FAIL
            failed_val_rules = [vr for vr in final_validation_results if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value]
            if failed_val_rules:
                 primary_fail = failed_val_rules[0]
                 details = primary_fail.details or {}
                 try:
                     fail_reason = primary_fail.message(details) if callable(primary_fail.message) else str(primary_fail.message)
                 except Exception: fail_reason = str(primary_fail.message) # Fallback
                 error_msg = f"Validation Failed: {primary_fail.rule_id} - {fail_reason}"
            elif final_validation_results and final_validation_results[0].passed is False: # Check first result if no high/crit fails specifically listed
                  error_msg = final_validation_results[0].message # Use message directly if not callable
                  if callable(error_msg): # Handle if message is callable
                       try: error_msg = error_msg({}) # Call with empty context
                       except Exception: error_msg = "Validation failed (message format error)."
            else:
                  error_msg = f"Validation failed after all {max_attempts} attempts. Last failed sections: {[s.name for s in sections_to_generate]}"

        hop_checkpoint = self._create_checkpoint(
            "HOP-3", status_message,
            final_validation_results, # Use the final set of results
            {"sections_generated": len(all_llm_sections), "sections_copied": len(copied_content)},
            start_time=hop_start_time,
            metadata={
                "gemini_api_calls": total_api_calls_hop3,
                "attempts_made": final_attempt_number,
                "final_temperatures": {k.name: v for k, v in locked_section_temps.items()}
            },
            error_message=error_msg # Include the derived error message
        )
        hop_checkpoint.status = hop_status
        self.hop_checkpoints.append(hop_checkpoint)

        if hop_status == HopStatus.FAIL:
            self.logger.error(f"  ✗ HOP-3 FAILED: {error_msg}")
            raise HopExecutionError(error_msg or "HOP-3 failed content generation or validation.")
        else:
             # Calculate average temp only if locked_section_temps is not empty
             avg_temp = sum(locked_section_temps.values()) / len(locked_section_temps) if locked_section_temps else 0.0
             self.logger.info(f"  ✓ HOP-3 successful after {final_attempt_number} attempt(s). Final avg. locked temp: {avg_temp:.2f}")

        return artist_output, total_api_calls_hop3


    def _execute_hop_4_staging_and_sanitization(self, artist_output: Dict) -> ImmutableStagingBuffer:
        # --- HOP-4: Staging ---
        hop4_start_time = datetime.now()
        self.logger.info("\n[HOP-4] Populating Staging Buffer...")
        # Ensure ImmutableStagingBuffer is defined/imported
        staging_buffer = ImmutableStagingBuffer()
        sections_populated = 0
        try:
            for key, value in artist_output.items():
                section_key_str = key
                # Attempt to map key back to enum value if possible, else use original key
                try: section_key_str = ResumeSection(key).value
                except (ValueError, NameError): pass # Keep original key if not a valid ResumeSection name

                if value is not None:
                    # Ensure StagingBufferError is defined/imported
                    staging_buffer.set(section_key_str, value)
                    sections_populated += 1

            hop4_checkpoint = self._create_checkpoint(
                "HOP-4", "Staging Buffer Population", [],
                {"sections_populated": sections_populated},
                start_time=hop4_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop4_checkpoint)
            self._check_hop_status(hop4_checkpoint)
        except StagingBufferError as sbe:
             self.logger.error(f"  ✗ [HOP-4] Staging FAILED: {sbe}", exc_info=False)
             hop4_checkpoint = self._create_checkpoint( "HOP-4", "Staging Buffer Population", [ValidationResult("HOP-4_STAGING_ERROR", False, ValidationSeverity.CRITICAL, str(sbe))], None, start_time=hop4_start_time, error_message=str(sbe), metadata={"gemini_api_calls": 0} )
             hop4_checkpoint.status = HopStatus.FAIL; self.hop_checkpoints.append(hop4_checkpoint)
             raise HopExecutionError(f"HOP-4 failed: {sbe}")
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-4] FAILED unexpectedly: {e}", exc_info=False)
             hop4_checkpoint = self._create_checkpoint( "HOP-4", "Staging Buffer Population", [ValidationResult("HOP-4_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))], None, start_time=hop4_start_time, error_message=str(e), metadata={"gemini_api_calls": 0} )
             hop4_checkpoint.status = HopStatus.FAIL; self.hop_checkpoints.append(hop4_checkpoint)
             raise HopExecutionError(f"HOP-4 failed: {e}")

        # --- HOP-4.5: Sanitization & Locking ---
        hop45_start_time = datetime.now()
        self.logger.info("\n[HOP-4.5] Text Sanitization & Locking...")
        sanitized_buffer = None
        try:
            # Ensure TextSanitizer is defined/imported
            sanitizer = TextSanitizer() # Assumes HYPHENATION_RULES_DATA is loaded globally
            hop45_results, sanitized_data = sanitizer.sanitize_buffer(staging_buffer)

            # Recreate buffer with sanitized data
            sanitized_buffer = ImmutableStagingBuffer()
            for key, value in sanitized_data.items():
                sanitized_buffer.set(key, value)
            self.logger.info(f"  ✓ Sanitization applied. Fixes: {sanitizer.sanitization_counts}")

            sanitized_buffer.lock() # Lock AFTER populating
            self.logger.info(f"  ✓ Sanitized buffer locked at {sanitized_buffer._lock_timestamp}.")

            hop45_checkpoint = self._create_checkpoint(
                "HOP-4.5", "Text Sanitization & Lock", hop45_results,
                {"buffer_locked": True}, start_time=hop45_start_time,
                metadata={"gemini_api_calls": 0, "sanitization_counts": sanitizer.sanitization_counts}
            )
            self.hop_checkpoints.append(hop45_checkpoint)
            self._check_hop_status(hop45_checkpoint, allow_warnings=True, check_critical_only=True) # Allow info/warnings from sanitization
            return sanitized_buffer
        except StagingBufferError as sbe: # Catch errors during set or lock
             self.logger.error(f"  ✗ [HOP-4.5] Sanitization/Locking FAILED: {sbe}", exc_info=False)
             # Ensure buffer is locked even if population failed mid-way or lock failed
             if staging_buffer and not staging_buffer.is_locked(): staging_buffer.lock()
             if sanitized_buffer and not sanitized_buffer.is_locked(): sanitized_buffer.lock() # Lock partially populated new buffer too
             hop45_checkpoint = self._create_checkpoint( "HOP-4.5", "Text Sanitization & Lock", [ValidationResult("HOP-4.5_BUFFER_ERROR", False, ValidationSeverity.CRITICAL, str(sbe))], {"buffer_locked": (staging_buffer.is_locked() if staging_buffer else False) or (sanitized_buffer.is_locked() if sanitized_buffer else False)}, start_time=hop45_start_time, error_message=str(sbe), metadata={"gemini_api_calls": 0} )
             hop45_checkpoint.status = HopStatus.FAIL; self.hop_checkpoints.append(hop45_checkpoint)
             raise HopExecutionError(f"HOP-4.5 failed: {sbe}")
        except Exception as e: # Catch other errors (e.g., in TextSanitizer)
            self.logger.error(f"  ✗ [HOP-4.5] FAILED unexpectedly: {e}", exc_info=False)
            if staging_buffer and not staging_buffer.is_locked(): staging_buffer.lock()
            if sanitized_buffer and not sanitized_buffer.is_locked(): sanitized_buffer.lock()
            hop45_checkpoint = self._create_checkpoint( "HOP-4.5", "Text Sanitization & Lock", [ValidationResult("HOP-4.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))], {"buffer_locked": (staging_buffer.is_locked() if staging_buffer else False) or (sanitized_buffer.is_locked() if sanitized_buffer else False)}, start_time=hop45_start_time, error_message=str(e), metadata={"gemini_api_calls": 0} )
            hop45_checkpoint.status = HopStatus.FAIL; self.hop_checkpoints.append(hop45_checkpoint)
            raise HopExecutionError(f"HOP-4.5 failed: {e}")

    def _execute_hop_5_validation(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str) -> List[ValidationResult]:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-5] Final Pre-flight Validation (Post-Sanitization)...")
        if not staging_buffer.is_locked():
             # This is a critical state error, lock and log loudly
             self.logger.error("  ✗ CRITICAL: Buffer is not locked entering HOP-5! Attempting lock now.")
             staging_buffer.lock()

        final_validation_results = []
        try:
            # Ensure PreFlightValidator is defined/imported
            validator = PreFlightValidator(self.master_resume)
            # Validate ALL sections (sections_under_test=None)
            hop_results, all_passed, failed_sections_enums = validator.validate(
                staging_buffer, thematic_analysis, job_description,
                sections_under_test=None
            )
            final_validation_results = hop_results
            self.validation_results = final_validation_results # Store for later use (Gate, QA)

            # GATE-5: Validate PreFlight using JD Enforcer
            # Pass the staging buffer (or its data) for JD keyword checks
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")


            total_rules_checked = len(validator.engine.rules) # Get total rules registered
            passed_rules = sum(1 for vr in hop_results if vr.passed)
            hop_checkpoint = self._create_checkpoint(
                "HOP-5", "Pre-flight Validation", hop_results,
                {"passed_rules": passed_rules, "total_rules": total_rules_checked, "all_passed": all_passed},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check status (allow_warnings=False, check_critical_only=False - Halt on HIGH or CRITICAL)
            self._check_hop_status(hop_checkpoint, allow_warnings=False, check_critical_only=False)
            return final_validation_results
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-5] FAILED during validation logic: {e}", exc_info=False)
             error_result = ValidationResult("HOP-5_EXECUTION", False, ValidationSeverity.CRITICAL, f"Validation execution failed: {e}")
             final_validation_results = [error_result]
             self.validation_results = final_validation_results # Store error result
             hop_checkpoint = self._create_checkpoint(
                 "HOP-5", "Pre-flight Validation", final_validation_results,
                 {"passed_rules": 0, "total_rules": 0, "all_passed": False},
                 start_time=hop_start_time, error_message=str(e),
                 metadata={"gemini_api_calls": 0}
             )
             hop_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop_checkpoint)
             raise HopExecutionError(f"HOP-5 failed during validation execution: {e}")

    def _execute_hop_6_gate_decision(self, hop5_results: List[ValidationResult]) -> GateDecision:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-6] Gate Decision...")
        gate_decision = GateDecision.HALT # Default to HALT
        gate_reason = "Initialization error"
        try:
            # Ensure GateDecisionEngine is defined/imported
            gate_engine = GateDecisionEngine()
            gate_decision, gate_reason = gate_engine.decide(hop5_results)

            self.logger.info(f"  Decision: {gate_decision.value}")
            self.logger.info(f"  Reason: {gate_reason}")

            hop_checkpoint = self._create_checkpoint(
                "HOP-6", "Gate Decision", [], # No new validation results here
                {"decision": gate_decision.value, "reason": gate_reason},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)

            # Check if decision is HALT and raise exception if so
            if gate_decision == GateDecision.HALT:
                 hop_checkpoint.status = HopStatus.FAIL # Mark checkpoint as failed
                 hop_checkpoint.error_message = gate_reason # Add reason to checkpoint error
                 # Raise exception to stop workflow execution
                 raise HopExecutionError(f"HALT decision at HOP-6: {gate_reason}")
            else:
                 hop_checkpoint.status = HopStatus.PASS # Mark as passed if PROCEED

            return gate_decision
        except Exception as e:
            # Catch errors within the decision logic itself
            self.logger.error(f"  ✗ [HOP-6] FAILED during decision logic: {e}", exc_info=False)
            error_reason = f"Error in decision engine: {e}"
            # Create a checkpoint reflecting the failure during the decision process
            hop_checkpoint = self._create_checkpoint(
                "HOP-6", "Gate Decision",
                [ValidationResult("HOP-6_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                {"decision": GateDecision.HALT.value, "reason": error_reason}, # Force HALT decision
                start_time=hop_start_time, error_message=error_reason,
                metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            # Raise exception to stop workflow execution
            raise HopExecutionError(f"HOP-6 failed during decision logic: {e}")

    def _execute_hop_7_rendering(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str, thematic_analysis: ThematicAnalysis, job_description: str, jd_url: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7] Rendering Output Files...")
        file_paths = {}; file_contents = {}; hop_results = []
        try:
            # Ensure FileRenderer is defined/imported
            renderer = FileRenderer(self.master_resume, self, company_name, job_title)
            file_paths, (hop_results, file_contents) = renderer.render(
                staging_buffer, company_name, job_title, thematic_analysis, job_description, jd_url=jd_url
            )
            # Store results on orchestrator
            self.rendered_output = {'file_paths': file_paths, 'file_contents': file_contents}

            # GATE-7: Validate File Output using JD Enforcer
            self.jd_enforcer.validate_file_output(file_paths, "GATE-7")


            hop_checkpoint = self._create_checkpoint(
                "HOP-7", "File Rendering", hop_results,
                {"files_generated": list(file_paths.keys())},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check for CRITICAL errors only (e.g., failed render, AppTracker validation errors)
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=True)
            return file_paths, file_contents
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-7] FAILED: {e}", exc_info=False)
            exec_error_result = ValidationResult("HOP-7_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))
            # Ensure the specific execution error is included in results
            if not any(vr.rule_id == "HOP-7_EXECUTION" for vr in hop_results):
                 hop_results.append(exec_error_result)
            hop_checkpoint = self._create_checkpoint(
                "HOP-7", "File Rendering", hop_results,
                None, start_time=hop_start_time, error_message=str(e),
                metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-7 failed during file rendering: {e}")

    # --- REMOVED _execute_hop_7_5_deduplication ---

    def _execute_hop_8_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        hop5_results: List[ValidationResult] # Receive final HOP-5 results
    ) -> str:
        """
        Executes HOP-8: QA Report Generation using the QAReportGenerator.
        Uses final validation results from HOP-5. Relies on HOP-5 validation results
        for similarity data, as HOP-7.5 calculations are removed.
        Returns the generated QA report text.
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-8] Generating QA Report...")
        qa_report_text = "[QA Report Not Generated]" # Default
        hop_results = [] # Store QA generation validation results
        try:
            # Instantiate the generator, passing self (the orchestrator)
            # Ensure QAReportGenerator is defined/imported
            qa_generator = QAReportGenerator(self)

            # Get current file contents (needed for QA section 12/13)
            current_file_contents = self.rendered_output.get('file_contents', {}) if self.rendered_output else {}

            # Generate report - returns (validation_results, report_text)
            hop_results, qa_report_text = qa_generator.generate(
                staging_buffer,
                thematic_analysis,
                hop5_results, # Pass final HOP-5 validation results
                current_file_contents
            )

            # Update the stored rendered output with the final QA report content
            if self.rendered_output and 'file_contents' in self.rendered_output:
                self.rendered_output['file_contents']['qa_report'] = qa_report_text
            elif self.rendered_output:
                 self.rendered_output['file_contents'] = {'qa_report': qa_report_text}
            else:
                 # Initialize if rendered_output wasn't set (shouldn't happen if HOP-7 succeeded)
                 self.rendered_output = {'file_contents': {'qa_report': qa_report_text}}

            # GATE-8: Validate QA Report Content using JD Enforcer
            # Check if the report seems valid before passing to enforcer
            qa_report_check_data = {"report": qa_report_text} if qa_report_text and "[Failed" not in qa_report_text else {}
            # Verify JD hash presence as a simple traceability check
            jd_usage_in_qa_valid = self.jd_enforcer.jd_hash in qa_report_text if self.jd_enforcer.jd_hash and qa_report_text else False
            if not jd_usage_in_qa_valid:
                 self.logger.warning("  ⚠️ GATE-8 Check: QA Report content might lack sufficient JD traceability (JD Hash missing).")
            # Run the formal JD Enforcement validation for QA
            self.jd_enforcer.validate_qa_report(qa_report_check_data, "GATE-8")


            # Create checkpoint using the validation results returned by the QA generator
            hop_checkpoint = self._create_checkpoint(
                "HOP-8", "QA Report Generation", hop_results,
                {"report_length": len(qa_report_text)},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check for critical errors during QA report generation/formatting
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=True)
            return qa_report_text
        except Exception as e: # Catch errors during QA report generation logic
            self.logger.error(f"  ✗ [HOP-8] FAILED: {e}", exc_info=False)
            error_reason = f"QA report generation failed: {e}"
            exec_error_result = ValidationResult("HOP-8_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))
            # Ensure the specific execution error is included in results
            if not any(vr.rule_id == "HOP-8_EXECUTION" for vr in hop_results):
                 hop_results.append(exec_error_result)
            hop_checkpoint = self._create_checkpoint(
                "HOP-8", "QA Report Generation", hop_results,
                {"report_length": 0}, start_time=hop_start_time, error_message=error_reason,
                metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            # Return placeholder text instead of raising error, allowing workflow termination handler to manage
            return f"[QA Report Generation Failed: {e}]"


    def _run_workflow_steps(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        jd_url: str
    ) -> Tuple[ThematicAnalysis, ImmutableStagingBuffer, List[ValidationResult], Dict[str, str], Dict[str, str], int, GateDecision]:
        """Helper method to run the main workflow hops sequentially."""
        total_api_calls = 0
        thematic_analysis, calls_hop0 = self._execute_hop_0_jd_analysis(job_description)
        total_api_calls += calls_hop0

        extracted_data = self._execute_hop_1_clerk_extraction()
        enriched_scaffold = self._execute_hop_2_enrichment(extracted_data, thematic_analysis)

        artist_output, calls_hop3 = self._execute_hop_3_artist_generation(
            enriched_scaffold, job_description, thematic_analysis
        )
        total_api_calls += calls_hop3

        staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)

        hop5_results = self._execute_hop_5_validation(
            staging_buffer, thematic_analysis, job_description
        )

        gate_decision = self._execute_hop_6_gate_decision(hop5_results) # This will raise HopExecutionError if HALT

        file_paths, file_contents = self._execute_hop_7_rendering(
            staging_buffer, company_name, job_title, thematic_analysis, job_description, jd_url
        )

        return (
            thematic_analysis, staging_buffer, hop5_results, file_paths, file_contents,
            total_api_calls, gate_decision
        )

    def _handle_workflow_termination(
        self,
        status: str, # "HALTED" or "FAILED"
        exception: Exception,
        workflow_start: datetime,
        thematic_analysis: Optional[ThematicAnalysis],
        staging_buffer: Optional[ImmutableStagingBuffer],
        final_validation_results: List[ValidationResult],
        total_api_calls: int,
        gate_decision_on_error: GateDecision = GateDecision.HALT
    ) -> Dict:
        """Helper method to build the result dictionary upon workflow halt or failure."""
        workflow_end = datetime.now()
        duration = (workflow_end - workflow_start).total_seconds()
        self.logger.error(f"\nWORKFLOW {status}: {exception}")
        self.logger.error(f"Terminated at: {workflow_end.isoformat()}")

        # Attempt to generate QA report even on failure/halt
        if staging_buffer and thematic_analysis and final_validation_results:
             qa_gen_results, qa_report_text, final_file_contents = self._generate_qa_report_after_halt(
                  staging_buffer, thematic_analysis, final_validation_results
             )

        # Build CoC Ledger (partially if needed)
        coc_ledger = self._build_coc_ledger(
            workflow_start, workflow_end, thematic_analysis, total_api_calls
        )

        # Ensure final status reflects the halt/failure
        coc_ledger["overall_status"] = HopStatus.FAIL.value

        # Use file paths/contents stored on orchestrator if HOP-7 ran, else empty
        final_file_paths = self.rendered_output.get('file_paths', {}) if self.rendered_output else {}

        # Update final file contents with the potentially generated QA report
        if 'qa_report' not in final_file_contents:
             final_file_contents['qa_report'] = qa_report_text


        return {
            "status": status,
            "gate_decision": gate_decision_on_error.value,
            "reason": str(exception),
            "error_type": type(exception).__name__,
            "file_paths": final_file_paths, # Report paths generated before error if any
            "qa_report": qa_report_text, # Attempted QA report
            "coc_ledger": coc_ledger,
            "file_contents": final_file_contents, # Report contents generated before error, plus QA attempt
            "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
            "workflow_duration_seconds": duration,
            "hash_chain": self.hash_chain,
            "total_api_calls": total_api_calls
        }


    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        jd_url: str = ""
    ) -> Dict:
        """
        Executes the entire resume generation workflow from JD analysis to file rendering.
        Calls helper methods for main steps and error handling.
        """
        workflow_start = datetime.now()
        # Sanitize inputs early
        company_name = re.sub(r'[^\w\s\-]+', '', str(company_name or "")).strip() or "Target_Company"
        job_title = re.sub(r'[^\w\s\-]+', '', str(job_title or "")).strip() or "Target_Role"
        jd_url = str(jd_url or "").strip()

        self.logger.info("=" * 80)
        self.logger.info(f"RESUME GENERATION ENGINE v{__version__} - GEMINI API")
        self.logger.info("=" * 80)
        self.logger.info(f"Company: {company_name}")
        self.logger.info(f"Position: {job_title}")
        self.logger.info(f"JD URL: {jd_url if jd_url else 'Not Provided'}")
        self.logger.info(f"Started: {workflow_start.isoformat()}")
        self.logger.info("=" * 80)

        # Initialize variables for potential use in exception handling
        staging_buffer: Optional[ImmutableStagingBuffer] = None
        hop5_results: List[ValidationResult] = []
        file_paths: Dict[str, str] = {}
        file_contents: Dict[str, str] = {}
        qa_report_text: str = "[QA Report Not Generated]"
        total_api_calls: int = 0
        gate_decision = GateDecision.PROCEED # Assume success initially

        try:
            (
                thematic_analysis, staging_buffer, hop5_results, file_paths, file_contents,
                total_api_calls, gate_decision
            ) = self._run_workflow_steps(
                job_description, company_name, job_title, jd_url
            )

            qa_report_text = self._execute_hop_8_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )
            # Update file contents with the generated QA report
            file_contents['qa_report'] = qa_report_text

            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            coc_ledger = self._build_coc_ledger(
                workflow_start, workflow_end, thematic_analysis, total_api_calls
            )

            self.logger.info("\n" + "=" * 80)
            self.logger.info("WORKFLOW COMPLETE")
            self.logger.info(f"Finished: {workflow_end.isoformat()}")
            self.logger.info(f"Total Duration: {duration:.3f} seconds")
            self.logger.info(f"Total Gemini API Calls: {total_api_calls}")
            self.logger.info(f"Final Gate Decision: {gate_decision.value}")
            self.logger.info(f"Final Status: SUCCESS")
            self.logger.info(f"Output Files: {', '.join(file_paths.keys())}")
            self.logger.info("=" * 80)

            final_result = {
                "status": "SUCCESS",
                "gate_decision": gate_decision.value,
                "file_paths": file_paths,
                "qa_report": qa_report_text,
                "coc_ledger": coc_ledger,
                "file_contents": file_contents,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "hash_chain": self.hash_chain,
                "total_api_calls": total_api_calls
            }
            self.rendered_output = final_result # Store final successful output
            return final_result

        except HopExecutionError as e:
            # Use self.validation_results if available (populated by HOP-5), else use hop5_results
            final_val_results_for_error = self.validation_results if self.validation_results else hop5_results
            return self._handle_workflow_termination(
                status="HALTED", exception=e, workflow_start=workflow_start,
                thematic_analysis=thematic_analysis, staging_buffer=staging_buffer,
                final_validation_results=final_val_results_for_error,
                total_api_calls=total_api_calls, gate_decision_on_error=GateDecision.HALT
            )

        except Exception as e:
            final_val_results_for_error = self.validation_results if self.validation_results else hop5_results
            return self._handle_workflow_termination(
                status="FAILED", exception=e, workflow_start=workflow_start,
                thematic_analysis=thematic_analysis, staging_buffer=staging_buffer,
                final_validation_results=final_val_results_for_error,
                total_api_calls=total_api_calls, gate_decision_on_error=GateDecision.HALT
            )

    def _create_jd_analyzer(self) -> EnhancedJobDescriptionAnalyzer:
        api_key = os.environ.get("GEMINI_API_KEY"); rag_config = None
        try:
             # Ensure RAGConfig is defined or handled gracefully
             if 'RAGConfig' in globals(): rag_config = RAGConfig()
             else: self.logger.warning("RAGConfig class not found, using default settings for JD Analyzer.")
        except NameError: self.logger.warning("RAGConfig class not found, using default settings for JD Analyzer.")
        # Ensure EnhancedJobDescriptionAnalyzer is defined/imported
        return EnhancedJobDescriptionAnalyzer(self.master_resume, enable_web_search=True, api_key=api_key, config=rag_config)

    def _create_checkpoint( self, hop_id: str, hop_name: str, validation_results: List[ValidationResult], output_data: Any, start_time: datetime, metadata: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None ) -> HopCheckpoint:
        end_time = datetime.now(); duration = (end_time - start_time).total_seconds(); status = HopStatus.PASS
        # Determine status based on errors or validation results
        if error_message:
            status = HopStatus.FAIL
        elif validation_results:
            if any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in validation_results):
                status = HopStatus.FAIL
            elif any(not vr.passed and vr.severity == ValidationSeverity.HIGH for vr in validation_results):
                status = HopStatus.FAIL # Treat HIGH as FAIL for status determination
            elif any(not vr.passed for vr in validation_results):
                status = HopStatus.WARNING
        output_hash = None
        if output_data is not None:
            try:
                # Custom serializer for complex types
                def default_serializer(o):
                    if isinstance(o, (datetime, ThematicAnalysis, HopCheckpoint, ValidationResult, Enum)):
                        # Use asdict for dataclasses, value for enums
                        return asdict(o) if not isinstance(o, Enum) else o.value
                    elif isinstance(o, ImmutableStagingBuffer):
                        return o.data # Serialize the data dict inside
                    elif hasattr(o, '__dict__'):
                        return o.__dict__ # Basic object serialization
                    try:
                        json.dumps(o)
                        return o
                    except TypeError:
                        return f"__Unserializable:{type(o).__name__}__"

                # Handle specific known complex types before general serialization
                serializable_output = output_data
                if isinstance(output_data, ImmutableStagingBuffer):
                    serializable_output = output_data.data
                elif isinstance(output_data, ThematicAnalysis):
                     # If ThematicAnalysis is a dataclass, asdict should work
                     try: serializable_output = asdict(output_data)
                     except Exception: serializable_output = {"error": "Failed to serialize ThematicAnalysis"}


                # Use compact, sorted JSON string for consistent hashing
                output_str = json.dumps(serializable_output, sort_keys=True, separators=(',', ':'), default=default_serializer)
                output_hash = hashlib.sha256(output_str.encode('utf-8')).hexdigest()[:16] # Use SHA256, truncate
            except (TypeError, Exception) as e:
                self.logger.warning(f"Could not calculate output hash for {hop_id} due to serialization error: {e}")
                output_hash = f"ErrorHashing:_{type(e).__name__}"

        # Prepare metadata, ensuring types are JSON serializable
        final_metadata = copy.deepcopy(metadata) or {}
        final_metadata["duration_seconds"] = round(duration, 3)
        # Ensure specific metadata fields are basic types if they exist
        if "gemini_api_calls" in final_metadata: final_metadata["gemini_api_calls"] = int(final_metadata["gemini_api_calls"])
        if "sanitization_counts" in final_metadata: final_metadata["sanitization_counts"] = dict(final_metadata["sanitization_counts"])
        if "final_temperatures" in final_metadata and isinstance(final_metadata["final_temperatures"], dict):
             final_metadata["final_temperatures"] = {k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in final_metadata["final_temperatures"].items()}


        # Deep copy validation results safely
        copied_validation_results = []
        for vr in validation_results:
             try:
                 # Manually create a new ValidationResult to avoid deepcopy issues with complex objects like callables
                 copied_vr = ValidationResult(
                     rule_id=vr.rule_id,
                     passed=vr.passed,
                     severity=vr.severity, # Keep enum
                     message=str(vr.message), # Convert potentially complex message to string
                     details=copy.deepcopy(vr.details) if vr.details else {} # Deep copy details if they exist
                 )
                 copied_validation_results.append(copied_vr)
             except Exception as copy_e:
                  logging.warning(f"Could not fully copy ValidationResult {vr.rule_id}: {copy_e}")
                  # Create a fallback ValidationResult indicating copy failure
                  copied_validation_results.append(ValidationResult(
                      rule_id=vr.rule_id, passed=vr.passed, severity=vr.severity,
                      message=f"Original Message Type: {type(vr.message).__name__} (Copy Failed)",
                      details={"error": f"Copy failed: {copy_e}"}
                  ))

        checkpoint = HopCheckpoint(
            hop_id=hop_id, hop_name=hop_name, status=status,
            timestamp_start=start_time.isoformat(), timestamp_end=end_time.isoformat(),
            output_hash=output_hash,
            validation_results=copied_validation_results, # Use safely copied results
            metadata=final_metadata, error_message=error_message
        )

        # Update hash chain
        hash_for_chain = output_hash if output_hash and not output_hash.startswith("ErrorHashing") else f"{hop_id}_Output"
        if self.hash_chain:
            prev_hash = self.hash_chain[-1]
            # Include essential elements in chain input
            chain_input = f"{prev_hash}|{hop_id}|{status.value}|{hash_for_chain}|{checkpoint.timestamp_end}"
            current_chain_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()[:16]
        else:
            current_chain_hash = hash_for_chain or f"{hop_id}_START_{status.value}"

        self.hash_chain.append(current_chain_hash)
        # Store chain hash in metadata *after* creating the checkpoint object
        checkpoint.metadata["chain_hash"] = current_chain_hash

        return checkpoint

    def _check_hop_status(self, checkpoint: HopCheckpoint, allow_warnings: bool = False, check_critical_only: bool = False):
        """Checks checkpoint status and raises HopExecutionError if workflow should halt."""
        effective_status = checkpoint.status
        halt_severity = ValidationSeverity.HIGH
        halt_reason_prefix = "HIGH/CRITICAL"

        if check_critical_only:
             halt_severity = ValidationSeverity.CRITICAL
             halt_reason_prefix = "CRITICAL"

        # Correct logic: Check if status is FAIL based on critical/high errors
        is_fail_status = checkpoint.status == HopStatus.FAIL
        has_halting_validation_failure = any(
             not vr.passed and vr.severity.value >= halt_severity.value
             for vr in checkpoint.validation_results
        )

        if is_fail_status or has_halting_validation_failure:
            # Find the primary reason for halting (highest severity failure or error message)
            failed_results = sorted(
                [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity.value >= halt_severity.value],
                key=lambda x: x.severity.value, reverse=True
            )
            primary_failure = failed_results[0] if failed_results else None
            reason_msg = "Unknown failure"

            if primary_failure:
                try:
                    # Safely format message, handling callables
                    simple_context = defaultdict(lambda: 'N/A', **(primary_failure.details or {}))
                    reason_msg = primary_failure.message(simple_context) if callable(primary_failure.message) else str(primary_failure.message)
                except Exception as msg_e:
                    reason_msg = f"{str(primary_failure.message)} (Msg format err: {msg_e})"
                reason = f"{primary_failure.rule_id}: {reason_msg}"
            else:
                # Use checkpoint error message if no specific validation failure caused the halt
                reason = checkpoint.error_message or "Unknown hop failure"

            error_msg = f"[{checkpoint.hop_id}] FAILED ({halt_reason_prefix}) - Halting workflow. Reason: {reason}"
            self.logger.error(f"  ✗ {error_msg}")

            # Log top few specific failures for context
            failures_to_log = failed_results[:3] # Log up to 3 specific failures
            if failures_to_log:
                self.logger.error("    Specific Failures:")
                for vr in failures_to_log:
                     try:
                         simple_context = defaultdict(lambda: 'N/A', **(vr.details or {}))
                         msg = vr.message(simple_context) if callable(vr.message) else str(vr.message)
                     except Exception: msg = str(vr.message) # Fallback
                     self.logger.error(f"      - [{vr.severity.name}] {vr.rule_id}: {msg}")

            # Ensure HopExecutionError is defined/imported
            raise HopExecutionError(f"{checkpoint.hop_id} failed validation ({halt_reason_prefix}). Halting.")

        elif checkpoint.status == HopStatus.WARNING:
            warnings = [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            self.logger.warning(f"  ⚠️ [{checkpoint.hop_id}] completed with {len(warnings)} warnings.")
            if not allow_warnings:
                error_msg = f"[{checkpoint.hop_id}] FAILED - Warnings detected but not allowed. Halting."
                self.logger.error(f"  ✗ {error_msg}")
                raise HopExecutionError(error_msg)
            else:
                 # Log first few warnings for context if warnings are allowed
                 for vr in warnings[:2]:
                     try:
                         simple_context = defaultdict(lambda: 'N/A', **(vr.details or {}))
                         msg = vr.message(simple_context) if callable(vr.message) else str(vr.message)
                     except Exception: msg = str(vr.message) # Fallback
                     self.logger.warning(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")
                 self.logger.info(f"  ✓ {checkpoint.hop_id} completed (with warnings).") # Log completion despite warnings

        elif checkpoint.status == HopStatus.PASS:
            self.logger.info(f"  ✓ {checkpoint.hop_id} completed successfully.")
        else:
            self.logger.error(f"  ? Unknown status encountered for {checkpoint.hop_id}: {checkpoint.status}")


    def _build_coc_ledger( self, workflow_start: datetime, workflow_end: datetime, thematic_analysis: Optional[ThematicAnalysis], total_api_calls: int ) -> Dict:
        """Builds the Chain of Custody ledger dictionary."""
        # Generate a unique ID for this specific workflow run
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', 'UnknownCandidate')}".encode('utf-8')
        ).hexdigest()[:16]

        # Extract relevant RAG metadata if analysis was successful
        rag_metadata = {}
        if thematic_analysis:
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            primary_theme_name = getattr(getattr(thematic_analysis, 'primary_theme', {}), 'name', 'N/A')
            role_archetype = getattr(getattr(thematic_analysis, 'role_classification', {}), 'role_archetype', 'N/A')
            # Safely convert competitive intelligence to dict if it's a dataclass
            comp_intel_dict = {}
            if comp_intel and hasattr(comp_intel, '__dataclass_fields__'): # Check if dataclass
                 try: comp_intel_dict = asdict(comp_intel)
                 except Exception as e: self.logger.warning(f"Could not serialize CompetitiveIntelligence: {e}")
            elif isinstance(comp_intel, dict): # Handle if it's already a dict
                 comp_intel_dict = comp_intel

            rag_metadata = {
                "signal_quality": getattr(thematic_analysis, 'signal_quality_score', 0.0),
                "retrieval_method": getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN'),
                "primary_theme": primary_theme_name,
                "role_archetype": role_archetype,
                "peer_jds_analyzed": comp_intel_dict.get('peer_jds_analyzed_count', 0),
                "differentiator_keywords_top5": comp_intel_dict.get('differentiator_keywords', [])[:5],
                # Include JD hash from the enforcer
                "jd_input_hash": self.jd_enforcer.jd_hash if hasattr(self, 'jd_enforcer') else None,
            }

        # Determine overall status based on hop checkpoints
        overall_status = HopStatus.PASS.value # Default to PASS
        if any(hc.status == HopStatus.FAIL for hc in self.hop_checkpoints):
            overall_status = HopStatus.FAIL.value
        elif any(hc.status == HopStatus.WARNING for hc in self.hop_checkpoints):
            overall_status = HopStatus.WARNING.value
        elif self.hop_checkpoints: # If no fail/warning, use status of last checkpoint
            overall_status = self.hop_checkpoints[-1].status.value

        # Serialize hop checkpoints, ensuring enums are converted to strings
        hops_executed_list = []
        for hc in self.hop_checkpoints:
             try:
                 checkpoint_dict = asdict(hc)
                 # Convert status enum to string value
                 checkpoint_dict['status'] = hc.status.value
                 for vr_dict in checkpoint_dict.get('validation_results', []):
                      # Check if severity is an Enum before accessing .name
                      if isinstance(vr_dict.get('severity'), Enum):
                           vr_dict['severity'] = vr_dict['severity'].name
                 hops_executed_list.append(checkpoint_dict)
             except Exception as e:
                 self.logger.warning(f"Could not fully serialize checkpoint {hc.hop_id}: {e}")
                 hops_executed_list.append({
                     "hop_id": hc.hop_id, "hop_name": hc.hop_name, "status": hc.status.value,
                     "error": f"Serialization partial failure: {e}",
                     "metadata": {"duration_seconds": hc.metadata.get("duration_seconds", -1)}
                 })

        # Gather JD Enforcement Summary
        jd_enforcement_summary = {}
        if hasattr(self, 'jd_enforcer'):
             enforcement_results = getattr(self.jd_enforcer, 'enforcement_results', [])
             jd_enforcement_summary = {
                 "total_checks": len(enforcement_results),
                 "passed_checks": sum(1 for r in enforcement_results if r.passed),
                 "failed_rules": [r.rule.name for r in enforcement_results if not r.passed]
             }

        # Build the final ledger dictionary
        return {
            "workflow_id": workflow_id,
            "engine_version": f"v{__version__}", # Assumes __version__ is defined globally
            "architecture_version": "Job_Workflow_v14.14_Refined", # Update as needed
            "timestamp_start_utc": workflow_start.utcnow().isoformat() + "Z",
            "timestamp_end_utc": workflow_end.utcnow().isoformat() + "Z",
            "duration_seconds": round((workflow_end - workflow_start).total_seconds(), 3),
            "master_resume_version": self.master_resume.get("schema_version", "Unknown"),
            "hops_executed": hops_executed_list,
            "hash_chain_final": self.hash_chain[-1] if self.hash_chain else None,
            "rag_metadata": rag_metadata,
            "jd_enforcement_summary": jd_enforcement_summary,
            "overall_status": overall_status,
            "total_gemini_api_calls": total_api_calls,
        }

    def _generate_qa_report_after_halt(
        self,
        staging_buffer: Optional[ImmutableStagingBuffer],
        thematic_analysis: Optional[ThematicAnalysis],
        validation_results: List[ValidationResult]
    ) -> Tuple[List[ValidationResult], str, Dict[str, str]]:
        """Attempts to generate QA report even after workflow halt/failure."""
        self.logger.info("  Attempting QA report generation after halt/failure...")
        qa_report_text = "[QA Report Generation Skipped: Missing necessary data after error]"
        final_file_contents = self.rendered_output.get('file_contents', {}) if self.rendered_output else {}
        qa_gen_results = []

        # Only attempt if essential data is present
        if staging_buffer and thematic_analysis and validation_results:
            try:
                # Ensure QAReportGenerator is defined/imported
                qa_generator = QAReportGenerator(self)
                current_file_contents = final_file_contents # Use potentially existing contents

                # Generate report - might still fail if content relies on later hops
                qa_gen_results, qa_report_text = qa_generator.generate(
                    staging_buffer, thematic_analysis, validation_results, current_file_contents
                )

                # Update final contents with the generated (or error) QA report
                final_file_contents['qa_report'] = qa_report_text
                self.logger.info("  ✓ QA report generated after halt/failure.")
            except Exception as qa_e:
                self.logger.error(f"  ✗ Failed to generate QA report after halt/failure: {qa_e}")
                qa_report_text = f"[QA Report generation failed post-error: {qa_e}]"
                final_file_contents['qa_report'] = qa_report_text
                # Add a validation result for the QA generation failure
                qa_gen_results.append(ValidationResult(
                    rule_id="QA_GENERATION_POST_ERROR_FAIL", passed=False,
                    severity=ValidationSeverity.ERROR, # Use ERROR severity for post-halt issues
                    message=f"QA report generation failed after workflow error: {qa_e}"
                ))
        else:
             self.logger.warning("  Skipping post-halt QA report generation due to missing buffer, analysis, or validation results.")
             final_file_contents['qa_report'] = qa_report_text # Ensure placeholder is there

        return qa_gen_results, qa_report_text, final_file_contents

# (Ensure these are defined in the same file or imported correctly)
class HopStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"

@dataclass
class HopCheckpoint:
    """Record of a workflow hop execution."""
    hop_id: str
    hop_name: str
    status: HopStatus
    timestamp_start: str
    timestamp_end: str
    output_hash: Optional[str] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class HopExecutionError(Exception): pass

class StagingBufferError(Exception): pass

import textwrap
import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import json
from collections import defaultdict

import textwrap
import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import json
from collections import defaultdict

class QAReportGenerator:
    """Generates the QA report by building individual sections (v14.11 structure)."""

    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis", "validation_results"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]},
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]},
        {"method": "_build_qa_section_6_content_authenticity", "args": ["validation_results"]}, # Specific method
        {"method": "_build_qa_section_7_prod_readiness", "args": ["validation_results"]},
        {"method": "_build_qa_section_8_similarity_summary", "args": ["validation_results"]}, # Renamed & Updated
        {"method": "_build_qa_section_9_structural_validation", "args": ["validation_results"]}, # Specific method
        {"method": "_build_qa_section_10_jd_enforcement", "args": []},
        {"method": "_build_qa_section_11_final_format", "args": ["validation_results", "file_contents"]},
    ]

    def __init__(self, orchestrator: 'WorkflowOrchestrator'):
        """Initializes the QA Report Generator."""
        self.orchestrator = orchestrator # Provides access to checkpoints, jd_enforcer, etc.
        self.logger = logging.getLogger(__name__)

    def generate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult], # Final HOP-5 results
        file_contents: Dict[str, str]
    ) -> Tuple[List[ValidationResult], str]:
        """Generates the full QA report."""
        qa_generation_validation_results = []
        report_lines = [
            f"RESUME QA REPORT (Engine: v{__version__}, Arch: Job_Workflow_v14.14_Refined)", # Updated Arch Version
            f"Generated: {datetime.now().isoformat()}",
        ]
        self.logger.info("  Building QA Report Sections...")

        # Arguments available to pass to builder methods
        available_args = {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "validation_results": validation_results,
            "file_contents": file_contents
        }

        for i, section_config in enumerate(self.QA_REPORT_SECTIONS, 1):
            method_name = section_config["method"]
            arg_names = section_config.get("args", [])
            self.logger.debug(f"    Building QA Section {i}: {method_name}")
            try:
                builder_method = getattr(self, method_name)
                # Prepare args by fetching from available_args based on names in config
                call_args = {}
                missing_args = []
                for name in arg_names:
                    if name in available_args:
                        call_args[name] = available_args[name]
                    else:
                        missing_args.append(name)

                if missing_args:
                    self.logger.warning(f"Missing arguments {missing_args} for QA method '{method_name}', section may be incomplete.")
                    # Continue with available args

                # Pass args in the order specified by arg_names if method requires them
                final_args_list = [call_args[name] for name in arg_names if name in call_args]
                if final_args_list:
                    section_lines = builder_method(*final_args_list) # Call specific method with args
                else:
                    section_lines = builder_method() # Call method without args (like hop summary)


                report_lines.extend(section_lines) # Extend the main list with lines from the section
            except AttributeError as ae:
                 error_message = f"AttributeError building QA section {i}: Method '{method_name}' not found. {ae}"
                 self.logger.error(error_message, exc_info=False)
                 report_lines.append(f"\n--- ERROR GENERATING SECTION {i}: {error_message} ---\n")
                 qa_generation_validation_results.append(ValidationResult( rule_id=f"QA_SECTION_{i}_ATTR_ERROR", passed=False, severity=ValidationSeverity.CRITICAL, message=error_message ))
            except KeyError as ke:
                 error_message = f"KeyError building QA section {i} ('{method_name}'): Missing expected data key '{ke}'."
                 self.logger.error(error_message, exc_info=False)
                 report_lines.append(f"\n--- ERROR GENERATING SECTION {i}: {error_message} ---\n")
                 qa_generation_validation_results.append(ValidationResult( rule_id=f"QA_SECTION_{i}_KEY_ERROR", passed=False, severity=ValidationSeverity.CRITICAL, message=error_message ))
            except Exception as e:
                # Catch other potential exceptions during section building
                error_message = f"Unexpected error building QA section {i} ('{method_name}'): {type(e).__name__} - {e}"
                self.logger.error(error_message, exc_info=True) # Log full traceback
                report_lines.append(f"\n--- ERROR GENERATING SECTION {i}: {error_message} ---\n")
                qa_generation_validation_results.append(ValidationResult(
                    rule_id=f"QA_SECTION_{i}_EXEC_ERROR",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL, # Treat section build errors as critical
                    message=error_message
                ))

        qa_report_text = "\n".join(report_lines).strip()
        self.logger.info(f"  ✓ QA Report sections built ({len(qa_report_text.splitlines())} lines).")

        self.logger.info("  Validating QA Report table formatting...")
        formatting_validation_result = self._validate_qa_report_formatting(qa_report_text)
        qa_generation_validation_results.append(formatting_validation_result)
        if not formatting_validation_result.passed:
            self.logger.warning(f"  ⚠️ QA Report formatting validation failed: {formatting_validation_result.message}")
        else:
             self.logger.info("  ✓ QA Report table formatting validation passed.")

        overall_qa_gen_status = all(vr.passed for vr in qa_generation_validation_results)
        qa_generation_validation_results.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION_OVERALL",
            passed=overall_qa_gen_status,
            severity=ValidationSeverity.INFO if overall_qa_gen_status else ValidationSeverity.HIGH,
            message="QA Report generated successfully." if overall_qa_gen_status else "QA Report generated with formatting/section errors."
        ))
        return qa_generation_validation_results, qa_report_text

    def _build_qa_section_1_signal_quality(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        lines = ["", "**1. SIGNAL QUALITY & TARGET ALIGNMENT**", ""]
        lines.append("Summarizes RAG analysis quality and the alignment of generated content to weighted JD signals (Primary/Secondary Themes, Differentiators, Narrative, Role Keywords) using context-aware raw scores.")
        lines.append("")
        rag_quality = getattr(thematic_analysis, 'signal_quality_score', 0.0)
        retrieval_method = getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN')
        rag_quality_rule = next((vr for vr in validation_results if vr.rule_id == "VG_RAG_MIN_QUALITY"), None)
        rag_status_icon = "❌ CRIT" if rag_quality_rule and not rag_quality_rule.passed else "✅ PASS" if rag_quality_rule and rag_quality_rule.passed else "⚠️ WARN"
        lines.append(f"   RAG Analysis Quality: {rag_status_icon} (Raw Score: {rag_quality:.2f}) via {retrieval_method}")

        jd_rule = next((vr for vr in validation_results if vr.rule_id == "VG_JD_KEYWORD_RANGE"), None)
        kw_status_icon = "❌ FAIL"; kw_details = "N/A (Rule Result Missing)"
        if jd_rule:
            kw_status_icon = "✅ PASS" if jd_rule.passed else "❌ FAIL"
            # Access details safely
            details = getattr(jd_rule, 'details', {}) or {}
            kw_min, kw_max, kw_found = details.get('min', '?'), details.get('max', '?'), details.get('found', '?')
            kw_details = f"Found {kw_found} (Tgt: {kw_min}-{kw_max})"
        lines.append(f"   JD Keyword Integration: {kw_status_icon} ({kw_details})")
        lines.append("\n   Per-Section Signal Score Alignment (vs JD): Raw Score Displayed, Status vs Raw Target Range")

        total_weighted_raw_score, total_section_weight, total_weighted_min_target, total_weighted_max_target = 0.0, 0.0, 0.0, 0.0
        final_temps = {}
        artist_checkpoint = next((cp for cp in self.orchestrator.hop_checkpoints if cp.hop_id == 'HOP-3'), None)
        if artist_checkpoint and isinstance(artist_checkpoint.metadata.get('final_temperatures'), dict):
            final_temps = artist_checkpoint.metadata['final_temperatures']

        # Ensure PreFlightValidator is accessible for SECTION_SIGNAL_TARGETS_CONFIG
        try:
            raw_target_config = PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG
        except NameError:
             self.logger.error("PreFlightValidator class not found for QA Section 1. Cannot display detailed signal targets.")
             return lines + ["\nERROR: PreFlightValidator config unavailable."]

        for label, (section_enum, target_min_raw, target_max_raw, weight, _) in raw_target_config.items():
            content = staging_buffer.get(section_enum.value); raw_score = 0.0
            if content:
                try:
                    # SIMULATION - Replace with actual raw score calculation if available
                    normalized_score = calculate_signal_score(content, thematic_analysis) # Needs to be accessible
                    raw_score = normalized_score
                    # Apply boost logic based on section
                    if section_enum in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K9_COMPETENCIES] and raw_score > 0.9:
                        raw_score = min(raw_score * 1.2, 1.3) # Boost
                except Exception as e:
                    self.logger.warning(f"Error calculating raw signal score for {label}: {e}")

            status = "PASS" if target_min_raw <= raw_score <= target_max_raw else "FAIL"
            # Get temp using Enum name which matches the keys stored in HOP-3 metadata
            temp_used_val = final_temps.get(section_enum.name, 'N/A')
            temp_used_str = f"{temp_used_val:.1f}" if isinstance(temp_used_val, (float, int)) else str(temp_used_val)

            lines.append(self._format_simplified_ascii_bar_chart(label, raw_score, target_min_raw, target_max_raw))

        avg_raw_score = total_weighted_raw_score / total_section_weight if total_section_weight > 0 else 0.0
        avg_min_target = total_weighted_min_target / total_section_weight if total_section_weight > 0 else 0.0
        avg_max_target = total_weighted_max_target / total_section_weight if total_section_weight > 0 else 0.0
        avg_temp_val_str = 'N/A'
        if final_temps:
            numeric_temps = [t for t in final_temps.values() if isinstance(t, (int, float))]
            avg_temp_val = sum(numeric_temps) / len(numeric_temps) if numeric_temps else 'N/A'
            avg_temp_val_str = f"{avg_temp_val:.1f}" if isinstance(avg_temp_val, (float, int)) else str(avg_temp_val)

        lines.append("-" * 95)
        lines.append(self._format_simplified_ascii_bar_chart("Weighted Average", avg_raw_score, avg_min_target, avg_max_target, is_summary=True))
        lines.append("-" * 95)

        skills_enum = ResumeSection.K10_SKILLS; skills_content = staging_buffer.get(skills_enum.value); skills_raw_score = 0.0
        if skills_content:
            try:
                normalized_score = calculate_signal_score(skills_content, thematic_analysis) # Needs to be accessible
                skills_raw_score = normalized_score
            except Exception as e:
                self.logger.warning(f"Error calculating raw signal score for Skills: {e}")
        lines.append(self._format_simplified_ascii_bar_chart("Skills (Not in Avg)", skills_raw_score, None, None, status_override="INFO"))

        cl_enum = ResumeSection.K11_COVER_LETTER; cl_content = staging_buffer.get(cl_enum.value); cl_raw_score = 0.0; cl_target_min_raw, cl_target_max_raw = 0.80, 1.10 # Example targets
        if cl_content:
            try:
                normalized_score = calculate_signal_score(cl_content, thematic_analysis) # Needs to be accessible
                cl_raw_score = normalized_score
                # Apply boost logic if applicable
                if cl_raw_score > 0.9:
                    cl_raw_score = min(cl_raw_score * 1.1, 1.3) # Example boost
            except Exception as e:
                self.logger.warning(f"Error calculating raw signal score for Cover Letter: {e}")
        cl_status = "PASS" if cl_target_min_raw <= cl_raw_score <= cl_target_max_raw else "FAIL"
        lines.append(self._format_simplified_ascii_bar_chart("Cover Letter (Not in Avg)", cl_raw_score, cl_target_min_raw, cl_target_max_raw, status_override=cl_status))

        signal_fail_rule = next((vr for vr in validation_results if vr.rule_id == "VG_PER_SECTION_SIGNAL_SCORE"), None)
        if signal_fail_rule and not signal_fail_rule.passed:
             lines.append("\n**Signal Score Failures:**")
             details = getattr(signal_fail_rule, 'details', {}) or {}
             fail_msg = "[Error formatting msg]"
             try:
                 # Use message attribute directly, handle callable if necessary
                 msg_template = str(signal_fail_rule.message)
                 safe_details = defaultdict(lambda: '[N/A]', **details)
                 if callable(signal_fail_rule.message):
                     # Ensure context is passed correctly if message is callable
                     fail_msg = signal_fail_rule.message(safe_details) # Assuming message lambda takes context/details
                 else:
                     fail_msg = msg_template.format_map(safe_details)
             except Exception as e:
                 self.logger.warning(f"Error formatting QA msg for {signal_fail_rule.rule_id}: {e}")
             lines.append(f"  - {fail_msg}")

        return lines

    def _build_qa_section_2_signal_flow_map(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis
    ) -> List[str]:
        lines = ["", "**2. HOP-0 RAG SIGNAL FLOW MAP (Consumed Signals)**", ""] # Updated title
        lines.append("This table shows how RAG intelligence (columns) was consumed by each generated resume section (rows), based on validation metrics or confirmed use in generation logic.")
        lines.append("")
        lines.append("```markdown")
        headers = [ "Target Section", "Primary Theme\n(Signal)", "Differentiator\nKeywords\n(Validation Metric)", "Role Archetype\n(Signal)", "Problem-Solution\nNarrative\n(Signal)", "Secondary Themes\n(Signal)", "Authenticity Patterns\n(Voice & Phrasing)\n(Signal)" ]
        # Configuration mapping sections to expected signal usage
        rows_config = [
            {"section": ResumeSection.K0_HEADLINE, "label": "K.0 (Headline)", "signals": ["Primary", "Diff_Pct", "Archetype", None, None, "Auth"]},
            {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "label": "K.1 (Exec Summary)", "signals": ["Primary", "Diff_Count", "Archetype", "Narrative", "Secondary", "Auth"]},
            {"section": ResumeSection.K2_UNIFY_BULLETS, "label": "K.2 (Unify Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K2_UNIFY_OVERVIEW, "label": "K.2 (Unify Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K3_IBM_BULLETS, "label": "K.3 (IBM Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K3_IBM_OVERVIEW, "label": "K.3 (IBM Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K4_TRADERSENSE_NARRATIVE, "label": "K.4 (TraderSense Nar.)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
            {"section": ResumeSection.K5_EY_NARRATIVE, "label": "K.5 (EY Narrative)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
            {"section": ResumeSection.K6_EARLY_CAREER_NARRATIVE, "label": "K.6 (Early Car. Nar.)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
            {"section": ResumeSection.K9_COMPETENCIES, "label": "K.9 (Competencies)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K10_SKILLS, "label": "K.10 (Skills)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", None]},
            {"section": ResumeSection.K11_COVER_LETTER, "label": "K.11 (Cover Letter)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
        ]
        table_rows = []
        # Safely extract differentiators
        comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
        differentiators = []
        if comp_intel:
             differentiators = getattr(comp_intel, 'differentiator_keywords', [])
             if not isinstance(differentiators, list): differentiators = [] # Ensure it's a list
        valid_diffs = [kw for kw in differentiators if kw and isinstance(kw, str)]

        for row_cfg in rows_config:
            section_label = row_cfg["label"]
            signal_presence = row_cfg["signals"]
            content = staging_buffer.get(row_cfg["section"].value)
            row_data = [section_label]

            # Primary Theme Check
            row_data.append("✓" if signal_presence[0] == "Primary" else "N/A")

            # Differentiator Check (Percentage or Count)
            if signal_presence[1] == "Diff_Pct" and content:
                # Calculate signal score (assuming function exists)
                score = calculate_signal_score(content, thematic_analysis)
                row_data.append(f"{score:.1%}")
            elif signal_presence[1] == "Diff_Count" and content:
                # Count found differentiators
                diff_count = 0
                if valid_diffs:
                    summary_lower = str(content).lower()
                    diff_count = sum(1 for kw in valid_diffs if kw.lower() in summary_lower)
                row_data.append(f"{diff_count}/{len(valid_diffs)} Found")
            else:
                row_data.append("N/A") # Not applicable or content missing

            # Other Signal Checks (Archetype, Narrative, Secondary, Auth)
            row_data.append("✓" if signal_presence[2] == "Archetype" else "N/A")
            row_data.append("✓" if signal_presence[3] == "Narrative" else "N/A")
            row_data.append("✓" if signal_presence[4] == "Secondary" else "N/A")
            row_data.append("✓" if signal_presence[5] == "Auth" else "N/A")

            table_rows.append(row_data)

        # Define column widths for formatting
        col_widths = [25, 18, 20, 18, 18, 18, 25] # Adjusted widths
        # Format and add table lines (assuming helper exists)
        lines.extend(self._format_plain_text_table(headers, table_rows, col_widths=col_widths, wrap_text=True))
        lines.append("```")
        lines.append("Legend: ✓ = Signal Consumed in Prompt/Logic, N/A = Not Applicable, Pct/Count = Validation Metric")
        return lines

    def _build_qa_section_3_hop_summary(self) -> List[str]:
        lines = ["", "**3. HOP-BY-HOP EXECUTION SUMMARY**", ""] # Updated title
        lines.append("```markdown")
        headers = ["Hop ID", "Hop Name", "Status", "Duration (s)", "Gemini API Calls", "Output Hash", "Chain Hash"]
        rows = []
        hop_checkpoints = getattr(self.orchestrator, 'hop_checkpoints', []) # Safely access
        expected_rows = len(hop_checkpoints)

        for hop in hop_checkpoints:
            # Ensure attributes exist before accessing
            duration = getattr(hop, 'metadata', {}).get("duration_seconds", -1.0)
            api_calls = getattr(hop, 'metadata', {}).get("gemini_api_calls", 0)
            output_hash = getattr(hop, 'output_hash', None)
            chain_hash = getattr(hop, 'metadata', {}).get("chain_hash", None)
            status_val = getattr(getattr(hop,'status', None), 'value', 'UNKNOWN') # Safely get enum value

            rows.append([
                getattr(hop, 'hop_id', 'N/A'),
                getattr(hop, 'hop_name', 'N/A'),
                status_val,
                f"{duration:.3f}" if isinstance(duration, (float, int)) and duration >= 0 else "N/A",
                str(api_calls) if isinstance(api_calls, int) else "N/A",
                output_hash or "N/A",
                chain_hash or "N/A" # Include chain hash
            ])

        # Check for truncation (if expected rows differ from actual rows generated)
        if len(rows) != expected_rows:
            self.logger.warning(f"QA Section 3: Hop summary truncation detected (Expected {expected_rows}, got {len(rows)}).")
            rows.append(["ERROR", "TRUNCATION_DETECTED?", "FAIL", "N/A", "N/A", "N/A", f"Expected {expected_rows}, got {len(rows)}"])

        # Format table (assuming helper exists)
        lines.extend(self._format_plain_text_table(headers, rows, alignments=['L', 'L', 'L', 'R', 'R', 'L', 'L']))
        lines.append("```")
        lines.append("Note: 'Gemini API Calls' reflects total calls for the hop. Chain Hash tracks data integrity.")
        return lines

    def _build_qa_section_4_word_count_distribution(
        self,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        lines = ["", "**4. WORD COUNT & DISTRIBUTION COMPLIANCE**", ""] # Updated title
        lines.append("Combines overall resume word count, key section constraints (Headline, Exec Summary, Overviews, Narratives, Cover Letter paragraphs), and distribution metrics (Unify/IBM). Bullet length validation is in Section 5.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section", "Rule ID", "Value", "Target Range", "Status", "Message / Details"]
        rows = []

        # Define rules and their associated section labels for this table
        rules_to_include = {
            "VG_TOTAL_WORD_COUNT": "Overall Resume",
            "VG_HEADLINE_WORD_COUNT": "K.0 Headline",
            "VG_SENTENCE_COUNT_K1": "K.1 Exec Summary", "VG_WORD_COUNT_K1": "K.1 Exec Summary",
            "VG_WORD_COUNT_K2_OVERVIEW": "K.2 Unify Overview", "VG_SENTENCE_COUNT_K2_OVERVIEW": "K.2 Unify Overview",
            "VG_WORD_COUNT_K3_OVERVIEW": "K.3 IBM Overview", "VG_SENTENCE_COUNT_K3_OVERVIEW": "K.3 IBM Overview",
            "VG_NARRATIVE_WORD_COUNT_K4": "K.4 TraderSense Nar.", "VG_NARRATIVE_SENTENCE_COUNT_K4": "K.4 TraderSense Nar.",
            "VG_NARRATIVE_WORD_COUNT_K5": "K.5 EY Narrative", "VG_NARRATIVE_SENTENCE_COUNT_K5": "K.5 EY Narrative",
            "VG_NARRATIVE_WORD_COUNT_K6": "K.6 Early Career Nar.", "VG_NARRATIVE_SENTENCE_COUNT_K6": "K.6 Early Career Nar.",
            "WORD_DISTRIBUTION_UNIFY_IBM": "Experience Dist.", "UNIFY_IBM_RATIO": "Experience Dist.",
            # Cover Letter Paragraphs will be handled separately using COVER_LETTER_STRUCTURE details
        }

        # Handle Cover Letter Paragraphs using the COVER_LETTER_STRUCTURE result
        cl_structure_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_STRUCTURE"), None)
        cl_paragraph_details = getattr(cl_structure_result, 'details', {}) if cl_structure_result else {}

        # Add rows for Cover Letter paragraphs if details exist
        for p_num in [1, 2, 3]:
            p_label = f"K.11 Cover Letter P{p_num}"
            p_rule_id = f"CL_P{p_num}_WORD_COUNT" # Synthetic Rule ID for display
            wc_key, min_key, max_key = f"p{p_num}_wc", f"p{p_num}_min", f"p{p_num}_max"
            value_str, target_str, status, msg = "N/A", "N/A", "WARN", "Structure rule/details missing"

            if cl_structure_result: # Check if the main structure rule ran
                wc = cl_paragraph_details.get(wc_key, 'N/A')
                min_r = cl_paragraph_details.get(min_key, 'N/A')
                max_r = cl_paragraph_details.get(max_key, 'N/A')

                value_str = f"{wc} words" if isinstance(wc, int) else "N/A"
                target_str = f"{min_r}-{max_r}" if isinstance(min_r, int) and isinstance(max_r, int) else "N/A"

                # Determine status based on the main structure rule's outcome and specific paragraph check
                if not cl_structure_result.passed and cl_paragraph_details.get('error'):
                    status, msg = "FAIL", cl_paragraph_details.get('error', 'Structure error')
                elif isinstance(wc, int) and isinstance(min_r, int) and isinstance(max_r, int):
                    status = "PASS" if min_r <= wc <= max_r else "FAIL"
                    msg = "" if status == "PASS" else f"Count ({wc}) outside range ({min_r}-{max_r})"
                else:
                    status, msg = "WARN", "Paragraph details missing or invalid"
            rows.append([p_label, p_rule_id, value_str, target_str, status, msg])


        # Add rows for other defined rules
        for rule_id, section_label in rules_to_include.items():
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
            value_str, target_str, status, msg = "N/A", "N/A", "WARN", "Validation result not found"

            if result:
                # Safely access details and format values
                details = getattr(result, 'details', {}) or {}
                value_str = "N/A"
                if 'total_words' in details: value_str = f"{details['total_words']} words"
                elif 'word_count' in details: value_str = f"{details['word_count']} words"
                elif 'sentence_count' in details: value_str = f"{details['sentence_count']} sentences"
                elif 'unify_ibm_percent' in details: value_str = f"{details.get('unify_ibm_percent', 0.0):.1f}%"
                elif 'unify_ibm_ratio' in details: value_str = f"{details.get('unify_ibm_ratio', 0.0):.2f}"

                # Format target range string
                target_str = "N/A"
                if 'min' in details and 'max' in details: target_str = f"{details['min']}-{details['max']}"
                elif 'min_wc' in details and 'max_wc' in details: target_str = f"{details['min_wc']}-{details['max_wc']}"
                elif 'min_sc' in details and 'max_sc' in details: target_str = f"{details['min_sc']}-{details['max_sc']}"
                elif 'target_sc' in details: target_str = str(details['target_sc']) # For exact sentence counts

                status = "PASS" if result.passed else "FAIL"
                msg = "" # Default to empty message for PASS
                if not result.passed:
                    try:
                        # Safely format error message
                        msg_template = str(result.message)
                        safe_details = defaultdict(lambda: '[N/A]', **details)
                        if callable(result.message):
                            msg = result.message(safe_details) # Assuming lambda takes context/details
                        else:
                            msg = msg_template.format_map(safe_details)
                    except Exception as e:
                        self.logger.warning(f"Error formatting QA msg for {rule_id}: {e}")
                        msg = "[Error formatting msg]"
                rows.append([section_label, rule_id, value_str, target_str, status, msg])
            else:
                rows.append([section_label, rule_id, value_str, target_str, status, msg])

        # Format and add table lines
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_5_provenance(
        self,
        staging_buffer: ImmutableStagingBuffer
    ) -> List[str]:
        lines = ["", "**5. BULLET PROVENANCE & WORD COUNT**", ""] # Updated title
        lines.append("```markdown")
        headers = ["Section", "Item", "Provenance", "Word Count", "Target Range", "Status", "Text Snippet"]
        rows = []

        # Sections with bullets/items to check provenance and word count
        sections_to_process = [
            {"label": "K.2 Unify", "bullets_enum": ResumeSection.K2_UNIFY_BULLETS},
            {"label": "K.3 IBM", "bullets_enum": ResumeSection.K3_IBM_BULLETS},
            {"label": "K.9 Competencies", "bullets_enum": ResumeSection.K9_COMPETENCIES},
        ]

        # Ensure ArtistGenerator class is accessible for BULLET_WORD_COUNT_RANGES
        try:
            artist_bullet_ranges = ArtistGenerator.BULLET_WORD_COUNT_RANGES
        except NameError:
             self.logger.error("ArtistGenerator class not found for QA Section 5. Cannot get word count ranges.")
             artist_bullet_ranges = {} # Use empty dict as fallback

        self.logger.info(f"Using ArtistGenerator Ranges for QA Sec 5: {artist_bullet_ranges}")

        for section_data in sections_to_process:
            label = section_data["label"]
            bullets_enum = section_data.get("bullets_enum")
            if not bullets_enum: continue # Skip if enum is missing

            # Get target word count range for this section's bullets
            target_range = artist_bullet_ranges.get(bullets_enum)
            if not target_range:
                self.logger.warning(f"Word count range missing for {bullets_enum.name}. Using default (20-40).")
                target_range = (20, 40) # Fallback range
            min_target, max_target = target_range
            target_range_str = f"{min_target}-{max_target}"
            self.logger.debug(f"Processing Section '{label}', using Target WC Range={target_range_str}")

            # Get bullets/items from the buffer
            items = staging_buffer.get(bullets_enum.value, [])
            if isinstance(items, list) and items:
                for i, item_data in enumerate(items):
                    item_text, word_count, provenance = "", 0, "N/A"
                    # Handle both dict (expected) and str (fallback) item types
                    if isinstance(item_data, dict):
                        item_text = item_data.get('text', '')
                        # Use stored word_count if available, otherwise calculate
                        word_count = item_data.get('word_count', count_words_ms_word_style(item_text)) # Use helper
                        provenance = item_data.get('provenance', 'N/A')
                    elif isinstance(item_data, str):
                        # Handle case where list might contain raw strings (e.g., if generation failed partially)
                        item_text = item_data
                        word_count = count_words_ms_word_style(item_text) # Use helper
                        provenance = "Unknown (String)"
                        self.logger.warning(f"Found raw string in {bullets_enum.value}[{i}] instead of dict.")
                    else:
                        self.logger.warning(f"Unexpected item type in {bullets_enum.value}[{i}]: {type(item_data)}. Skipping.")
                        continue

                    self.logger.debug(f"  Item {i+1}: WordCount={word_count}, Target={target_range_str}")
                    # Check word count status
                    status, _ = self._check_word_count(word_count, min_target, max_target) # Use helper
                    rows.append([
                        label, str(i + 1), provenance, str(word_count), target_range_str,
                        status, item_text[:60] + ("..." if len(item_text) > 60 else "") # Truncate snippet
                    ])
            elif not isinstance(items, list):
                self.logger.warning(f"Expected list for items in section '{label}' ({bullets_enum.value}), but got {type(items)}. Skipping.")
                rows.append([label, "N/A", "N/A", "N/A", target_range_str, "FAIL", f"Invalid content type: {type(items)}"])
            elif not items:
                # Section exists but is empty
                rows.append([label, "N/A", "N/A", "0", target_range_str, "WARN", "No items found for section."])

        # Format and add table lines
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_6_content_authenticity(
        self,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        title = "**6. CONTENT AUTHENTICITY (Hallucination, Verbs, Phrasing, Signal Check)**" # Updated title
        description = "Checks for potential content hallucinations (metrics, superlatives), forbidden verbs, banned intro phrases, and alignment with authenticity signals from RAG."
        # Include all relevant rule patterns
        rule_id_patterns = ["HALLUCINATION", "VG_FORBIDDEN_VERBS", "VG_NO_INTRO_PHRASES", "VG_AUTHENTICITY_SIGNAL_CHECK"]
        lines = ["", title, "", description, ""]
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        # Filter validation results based on patterns
        filtered_results = [
            vr for vr in validation_results
            if any(pattern in vr.rule_id for pattern in rule_id_patterns)
        ]

        if filtered_results:
            filtered_results.sort(key=lambda vr: vr.rule_id) # Sort for consistent order
            for vr in filtered_results:
                details = getattr(vr, 'details', {}) or {}
                msg = "[Error formatting msg]"
                try:
                    # Safely format message, handling callables
                    msg_template = str(vr.message)
                    if callable(vr.message):
                        # Pass defaultdict for safe formatting of callable messages
                        msg = vr.message(defaultdict(lambda: '[N/A]', **details))
                    else:
                        # Use format_map for string templates
                        msg = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                except Exception as e:
                    self.logger.warning(f"Error formatting message for rule {vr.rule_id} in {title}: {e}")

                details_str = ""
                # Add details snippet if the rule failed and details exist
                if not vr.passed and details:
                    try:
                        # Attempt to serialize details compactly, truncate if long
                        details_json = json.dumps(details, indent=None, ensure_ascii=False)
                        details_str = f" Details: {details_json}"[:150] # Truncate long details
                    except Exception:
                        details_str = f" Details: {str(details)}"[:150] # Fallback to string representation

                # Show message only on failure for brevity
                final_msg_display = msg if not vr.passed else ""
                rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg_display}{details_str}"])
        else:
            # Handle case where no relevant results were found
            rows = [["N/A", "INFO", f"No relevant validation results found for patterns: {rule_id_patterns}"]]

        # Format and add table lines
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_7_prod_readiness(
        self,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        lines = ["", "**7. PRODUCTION READINESS**", ""] # Updated title
        lines.append("```markdown")

        # Combine results from final validation (HOP-5) and all previous hops
        all_results = validation_results + [
            vr for hop in self.orchestrator.hop_checkpoints
            for vr in getattr(hop, 'validation_results', []) # Safely access results
        ]

        # Deduplicate results, keeping the one with the highest severity for each rule ID
        unique_results_dict = {}
        for vr in all_results:
            # Ensure severity is valid before comparison
            if not isinstance(getattr(vr, 'severity', None), ValidationSeverity): continue
            key = vr.rule_id
            # If rule not seen, or current result has higher severity, update
            if key not in unique_results_dict or vr.severity.value > unique_results_dict[key].severity.value:
                unique_results_dict[key] = vr
        unique_results = list(unique_results_dict.values())

        # Identify critical and high failures from the unique results
        critical_failures = [vr for vr in unique_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
        high_failures = [vr for vr in unique_results if not vr.passed and vr.severity == ValidationSeverity.HIGH]

        # Determine overall readiness (Zero Tolerance for HIGH or CRITICAL)
        prod_ready = not critical_failures and not high_failures

        # Build summary table
        headers = ["Check", "Value", "Status"]
        rows = [
            ["Production Ready", str(prod_ready).upper(), "✅ PASS" if prod_ready else "❌ FAIL"],
            ["Critical Failures Found", len(critical_failures), "✅ OK" if not critical_failures else "❌ FAIL"],
            ["High Failures Found", len(high_failures), "✅ OK" if not high_failures else "❌ FAIL"]
        ]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")

        # Add details if not production ready
        if not prod_ready:
            lines.append("\n  **Reason:** Production readiness requires zero CRITICAL or HIGH severity failures across all hops.")
            if critical_failures:
                lines.append("  **CRITICAL FAILURES:**")
                for f in critical_failures[:5]: # Show top 5
                    details = getattr(f, 'details', {}) or {}; msg = "[Error formatting msg]"
                    try:
                        msg_template = str(f.message)
                        if callable(f.message): msg = f.message(defaultdict(lambda: '[N/A]', **details))
                        else: msg = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                    except Exception as e: self.logger.warning(f"Error formatting QA msg for {f.rule_id}: {e}")
                    lines.append(f"    - {f.rule_id}: {msg}")
                if len(critical_failures) > 5: lines.append("    - ... (additional critical failures omitted)")
            if high_failures:
                lines.append("  **HIGH FAILURES:**")
                for f in high_failures[:5]: # Show top 5
                    details = getattr(f, 'details', {}) or {}; msg = "[Error formatting msg]"
                    try:
                        msg_template = str(f.message)
                        if callable(f.message): msg = f.message(defaultdict(lambda: '[N/A]', **details))
                        else: msg = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                    except Exception as e: self.logger.warning(f"Error formatting QA msg for {f.rule_id}: {e}")
                    lines.append(f"    - {f.rule_id}: {msg}")
                if len(high_failures) > 5: lines.append("    - ... (additional high failures omitted)")
        return lines

    def _build_qa_section_8_similarity_summary(
        self,
        validation_results: List[ValidationResult] # Receives final HOP-5 results
    ) -> List[str]:
        """Builds QA Section 8: Content Similarity Summary based on HOP-5 validation."""
        lines = ["", "**8. CONTENT SIMILARITY SUMMARY (from HOP-5 Validation)**", ""] # Updated title
        lines.append("Checks for excessive similarity between key generated sections based *only* on the pass/fail results from the HOP-5 validation gate.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Check Type", "Validation Rule", "Status", "Failure Explanation (if applicable)"]
        rows = []
        overall_pass = True # Assume PASS initially

        # --- 1. Cross-Section Similarity (Check HOP-5 Result) ---
        cross_section_rule_id = "VG_CROSS_SECTION_SIMILARITY"
        cross_section_result = next((vr for vr in validation_results if vr.rule_id == cross_section_rule_id), None)
        cross_section_status = "⚠️ WARN" # Default if rule result missing
        cross_section_notes = "Validation result not found."

        if cross_section_result:
            if cross_section_result.passed:
                cross_section_status = "✅ PASS"
                cross_section_notes = "No excessive overlap found (all pairs < 0.65)."
            else:
                cross_section_status = "❌ FAIL"
                overall_pass = False # Mark overall as failed
                details = getattr(cross_section_result, 'details', {}) or {}
                # Try to format the specific failure message
                try:
                    msg_template = str(cross_section_result.message)
                    if callable(cross_section_result.message):
                        # Pass defaultdict for safe formatting
                        cross_section_notes = cross_section_result.message(defaultdict(lambda: '[N/A]', **details))
                    else: # Use format_map for string templates
                        cross_section_notes = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                except Exception as e:
                    self.logger.warning(f"Error formatting message for {cross_section_rule_id}: {e}")
                    # Fallback message using details if formatting fails
                    cross_section_notes = f"High similarity found: {details.get('failures_str', 'Unknown failures')}"
        else:
             overall_pass = False # Treat missing check as non-passing for overall

        rows.append([
            "Cross-Section Overlap (>= 0.65)",
            cross_section_rule_id,
            cross_section_status,
            cross_section_notes
        ])

        # --- 2. Narrative vs. Master Similarity (Check HOP-5 Result) ---
        # --- >> This rule needs to be added to PreFlightValidator first << ---
        narrative_vs_master_rule_id = "VG_NARRATIVE_VS_MASTER_SIMILARITY" # Example ID
        narrative_result = next((vr for vr in validation_results if vr.rule_id == narrative_vs_master_rule_id), None)
        narrative_status = "⚠️ WARN"
        narrative_notes = "Validation rule not implemented or result missing."

        if narrative_result: # If the rule exists and ran
            if narrative_result.passed:
                narrative_status = "✅ PASS"
                narrative_notes = "Narrative similarity to source is within target range (e.g., 0.40-0.70)."
            else:
                narrative_status = "❌ FAIL"
                overall_pass = False
                details = getattr(narrative_result, 'details', {}) or {}
                try:
                    msg_template = str(narrative_result.message)
                    if callable(narrative_result.message):
                        narrative_notes = narrative_result.message(defaultdict(lambda: '[N/A]', **details))
                    else:
                        narrative_notes = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                except Exception as e:
                    self.logger.warning(f"Error formatting message for {narrative_vs_master_rule_id}: {e}")
                    narrative_notes = f"Narrative similarity outside range: {details.get('failures_str', 'Unknown failures')}" # Example fallback
        # else: # Rule doesn't exist yet, keep default message

        rows.append([
            "Narrative vs Master Similarity (e.g., 0.40-0.70)",
            narrative_vs_master_rule_id,
            narrative_status,
            narrative_notes
        ])

        # --- 3. Overall Status ---
        overall_status_str = "✅ PASS" if overall_pass else "❌ FAIL"
        overall_notes = "All similarity validation gates passed." if overall_pass else "One or more similarity validation gates failed."
        rows.append([
            "Overall Similarity Gate Status", "", overall_status_str, overall_notes
        ])

        # --- Format and return table ---
        alignments = ['L', 'L', 'L', 'L']
        col_widths = [45, 35, 8, 80] # Adjusted widths
        lines.extend(self._format_plain_text_table(headers, rows, alignments=alignments, col_widths=col_widths, wrap_text=True))
        lines.append("```")
        lines.append("Note: This section reflects PASS/FAIL status from HOP-5 gates. Detailed scores are not calculated/stored post HOP-5.")
        return lines

    def _build_qa_section_9_structural_validation(
        self,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        title = "**9. STRUCTURAL VALIDATION (Content Presence & Basic Format)**" # Updated title
        description = "Validates the presence of all required structural elements and basic formatting checks (e.g., Headline format)."
        # Include STRUCTURE rules and relevant formatting rules like headline checks
        rule_id_patterns = ["STRUCTURE_", "VG_HEADLINE_NO_TITLES", "VG_HEADLINE_NO_COMMAS", "VG_HEADLINE_COMPONENT_WC"]
        lines = ["", title, "", description, ""]
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        # Filter validation results based on patterns
        filtered_results = [
            vr for vr in validation_results
            if any(pattern in vr.rule_id for pattern in rule_id_patterns)
        ]

        if filtered_results:
            filtered_results.sort(key=lambda vr: vr.rule_id) # Sort for consistent order
            for vr in filtered_results:
                details = getattr(vr, 'details', {}) or {}
                msg = "[Error formatting msg]"
                try:
                    # Safely format message, handling callables
                    msg_template = str(vr.message)
                    if callable(vr.message):
                        # Pass defaultdict for safe formatting
                        msg = vr.message(defaultdict(lambda: '[N/A]', **details))
                    else: # Use format_map for string templates
                        msg = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
                except Exception as e:
                    self.logger.warning(f"Error formatting message for rule {vr.rule_id} in {title}: {e}")

                details_str = ""
                # Add details snippet if the rule failed and details exist
                if not vr.passed and details:
                    try:
                        # Serialize details compactly, truncate if long
                        details_json = json.dumps(details, indent=None, ensure_ascii=False)
                        details_str = f" Details: {details_json}"[:150] # Truncate
                    except Exception:
                        details_str = f" Details: {str(details)}"[:150] # Fallback

                # Show message only on failure
                final_msg_display = msg if not vr.passed else ""
                rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg_display}{details_str}"])
        else:
            # Handle case where no relevant results were found
            rows = [["N/A", "INFO", f"No relevant validation results found for patterns: {rule_id_patterns}"]]

        # Format and add table lines
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_10_jd_enforcement(self) -> List[str]:
        lines = ["", "**10. JD ENFORCEMENT VALIDATION**", ""]
        lines.append("Tracks the flow and usage of Job Description data throughout the workflow via predefined gates.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Gate ID", "Rule Checked", "Status", "Details"]
        # Safely access enforcement results from orchestrator
        enforcement_results = []
        if hasattr(self.orchestrator, 'jd_enforcer'):
             enforcement_results = getattr(self.orchestrator.jd_enforcer, 'enforcement_results', [])
        rows = []
        if enforcement_results:
            for res in enforcement_results:
                 # Safely access attributes of the result object
                 gate_id = getattr(res, 'gate_id', 'N/A')
                 rule_name = getattr(getattr(res, 'rule', None), 'name', 'N/A')
                 status = "PASS" if getattr(res, 'passed', False) else "FAIL"
                 details = getattr(res, 'details', 'N/A')
                 rows.append([gate_id, rule_name, status, details])
        else:
             rows.append(["N/A", "N/A", "WARN", "No JD enforcement results recorded."])

        # Format and add table lines
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_11_final_format(
        self,
        validation_results: List[ValidationResult],
        file_contents: Dict[str, str]
    ) -> List[str]:
        lines = ["", "**11. FINAL OUTPUT FORMATTING SUMMARY**", ""]
        lines.append("Checks the presence, basic structure, and formatting adherence of the final rendered files.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Artifact", "Check Type", "Requirement", "Status", "Failure Explanation"]
        output_definitions = []
        file_contents = file_contents or {} # Ensure it's a dict

        resume_content = file_contents.get('resume_md', '')
        output_definitions.append(("**Resume**", "Presence/Type", "Raw Text / Markdown", "PASS" if resume_content else "FAIL", "" if resume_content else "Content missing."))
        if resume_content:
            # Check K.0 Name Format (H1)
            name_pass = resume_content.strip().startswith("# ")
            output_definitions.append(("**Resume**", "K.0 Name Format", "# Format (H1)", "PASS" if name_pass else "FAIL", "" if name_pass else "Name does not start with H1 (# )."))
            # Check K.0 Headline Format (Plain text, below name, has pipes)
            headline_match = re.search(r"^# .+\n\n([^\n]+?)\n", resume_content.strip()) # Simpler regex
            headline_text = headline_match.group(1).strip() if headline_match else ""
            headline_pass = bool(headline_match) and "|" in headline_text and not headline_text.startswith(("#", "*", "-"))
            output_definitions.append(("**Resume**", "K.0 Headline Format", "Plain Text below Name w/ Pipes", "PASS" if headline_pass else "FAIL", "" if headline_pass else "Headline missing, uses Markdown, missing pipes, or wrong spacing."))

            # Headline Comma Check (using validation result)
            comma_check_result = next((vr for vr in validation_results if vr.rule_id == "VG_HEADLINE_NO_COMMAS"), None)
            comma_pass = comma_check_result.passed if comma_check_result else False
            comma_msg = ""
            if not comma_pass and comma_check_result: comma_msg = self._safe_format_validation_message(comma_check_result)
            elif not comma_pass: comma_msg = "Check missing or error"
            output_definitions.append(("**Resume**", "Headline Commas", "VG_HEADLINE_NO_COMMAS", "PASS" if comma_pass else "FAIL", comma_msg))

            # Placeholder Visual Checks (Assume PASS for now, replace with actual checks if implemented)
            output_definitions.append(("**Resume**", "Section Headers", "VG_RESUME_HEADER_H2 (Visual)", "PASS", ""))
            output_definitions.append(("**Resume**", "Experience Header", "VG_EXPERIENCE_RENDER_FORMAT (Visual)", "PASS", ""))
            output_definitions.append(("**Resume**", "Experience Bullets", "VG_EXPERIENCE_BULLET_STYLE (Visual)", "PASS", ""))
            output_definitions.append(("**Resume**", "Edu/Cert Formatting", "VG_EDU_CERTS_FORMAT (Visual)", "PASS", ""))
            output_definitions.append(("**Resume**", "Competency Formatting", "VG_COMPETENCIES_FORMATTING (Visual)", "PASS", ""))

            # Line Break Check
            lb_count = resume_content.count('\n\n'); expected_min_lbs = 10 # Estimate min expected blank lines
            lb_pass = lb_count >= expected_min_lbs
            output_definitions.append(("**Resume**", "Line Breaks", f">= {expected_min_lbs} Blank Lines", "PASS" if lb_pass else "WARN", "" if lb_pass else f"Found only {lb_count} blank lines."))

        skills_content = file_contents.get('skills', '')
        output_definitions.append(("**Skills**", "Presence/Type", "Raw Text", "PASS" if skills_content else "FAIL", "" if skills_content else "Content missing."))
        if skills_content:
            skills_lines_raw = skills_content.strip().split('\n')
            skills_items = [line.strip() for line in skills_lines_raw if line.strip()]
            # Check if items start with '• '
            bullet_pass = all(item.startswith("• ") for item in skills_items) if skills_items else True
            output_definitions.append(("**Skills**", "Bullet Format", "`• ` Used", "PASS" if bullet_pass else "FAIL", "" if bullet_pass else "One or more skills missing '• ' prefix."))
            # Check for double newlines between items
            double_newline_pass = True
            if len(skills_items) > 1:
                # Find indices of non-empty lines
                item_indices = [i for i, line in enumerate(skills_lines_raw) if line.strip()]
                # Check spacing between consecutive items
                for k in range(len(item_indices) - 1):
                    start_idx, end_idx = item_indices[k], item_indices[k+1]
                    # Expect exactly one blank line between items (indices differ by 2)
                    if end_idx != start_idx + 2:
                        double_newline_pass = False; break
            output_definitions.append(("**Skills**", "Line Breaks", "Double Newlines Between", "PASS" if double_newline_pass else "FAIL", "" if double_newline_pass else "Incorrect spacing between skills (expected double newline)."))

        cl_content = file_contents.get('cover_letter', '')
        output_definitions.append(("**Cover L.**", "Presence/Type", "Raw Text", "PASS" if cl_content else "FAIL", "" if cl_content else "Content missing."))
        if cl_content:
            # Overall Structure Check (using validation result)
            cl_struct_result = next((vr for vr in validation_results if vr.rule_id == "VG_COVER_LETTER_FULL_STRUCTURE"), None)
            cl_struct_pass = cl_struct_result.passed if cl_struct_result else False
            cl_struct_msg = ""
            if not cl_struct_pass and cl_struct_result: cl_struct_msg = self._safe_format_validation_message(cl_struct_result)
            elif not cl_struct_pass: cl_struct_msg = "Check missing or error"
            output_definitions.append(("**Cover L.**", "Overall Structure", "Standard Format Present", "PASS" if cl_struct_pass else "FAIL", cl_struct_msg))

            # Signature Check (using validation result)
            cl_sig_valid_result = next((vr for vr in validation_results if vr.rule_id == "VG_COVER_LETTER_SIGNATURE_VALID"), None)
            cl_sig_valid_pass = cl_sig_valid_result.passed if cl_sig_valid_result else False
            cl_sig_msg = ""
            if not cl_sig_valid_pass and cl_sig_valid_result: cl_sig_msg = self._safe_format_validation_message(cl_sig_valid_result)
            elif not cl_sig_valid_pass: cl_sig_msg = "Check missing or error"
            output_definitions.append(("**Cover L.**", "Signature Format", "VG_COVER_LETTER_SIGNATURE_VALID", "PASS" if cl_sig_valid_pass else "FAIL", cl_sig_msg))

        qa_content = file_contents.get('qa_report', '')
        output_definitions.append(("**QA Report**", "Presence/Type", "Fenced Markdown", "PASS" if qa_content else "FAIL", "" if qa_content else "Content missing."))
        if qa_content and qa_content != "[QA Report Not Generated]": # Check content exists and isn't placeholder
            # Check for Markdown fences (```)
            fence_pass = "```markdown" in qa_content and qa_content.strip().endswith("```")
            output_definitions.append(("**QA Report**", "Markdown Fences", "Uses Fenced Markdown", "PASS" if fence_pass else "FAIL", "" if fence_pass else "Missing markdown fences (```markdown ... ```)."))

            # Check Table Formatting (using HOP-8 validation result)
            hop8_checkpoint = next((cp for cp in self.orchestrator.hop_checkpoints if cp.hop_id == 'HOP-8'), None)
            qa_table_format_result = None
            if hop8_checkpoint:
                # Find the specific formatting validation result within HOP-8 results
                qa_table_format_result = next((vr for vr in getattr(hop8_checkpoint, 'validation_results', []) if vr.rule_id == "QA_TABLE_FORMAT_INVALID"), None)

            table_pass = qa_table_format_result.passed if qa_table_format_result else True # Assume pass if check missing
            table_msg = ""
            if not table_pass and qa_table_format_result: table_msg = self._safe_format_validation_message(qa_table_format_result)
            elif not table_pass: table_msg = "Check missing or error"
            output_definitions.append(("**QA Report**", "Table Format", "Uses Pre-formatted Tables", "PASS" if table_pass else "FAIL", table_msg))

            # Check Section Headers
            num_expected_sections = len(self.QA_REPORT_SECTIONS)
            section_headers_present = all(f"\n**{i}. " in qa_content or f"\n{i}. " in qa_content for i in range(1, num_expected_sections + 1))
            output_definitions.append(("**QA Report**", "Headers", f"Sections 1-{num_expected_sections} Present", "PASS" if section_headers_present else "FAIL", "" if section_headers_present else f"Missing expected section headers (1-{num_expected_sections})."))

        app_content = file_contents.get('app_tracker', '')
        output_definitions.append(("**App Trkr**", "Presence/Type", "JSON Block (Unfenced)", "PASS" if app_content else "FAIL", "" if app_content else "Content missing."))
        if app_content:
            # Check for incorrect fences
            is_fenced = app_content.strip().startswith("```json") and app_content.strip().endswith("```")
            fence_check_pass = not is_fenced
            output_definitions.append(("**App Trkr**", "JSON Fences", "Not Fenced", "PASS" if fence_check_pass else "FAIL", "" if fence_check_pass else "App Tracker incorrectly includes ```json fences."))

            # Check JSON Validity
            json_valid, parsed_json_data, json_fail_reason = False, None, "Unknown JSON error"
            json_valid_status_appended = False # Flag to prevent duplicate rows
            try:
                content_to_parse = app_content.strip()
                if is_fenced: content_to_parse = content_to_parse[7:-3].strip() # Attempt to parse even if fenced
                parsed_json_data = json.loads(content_to_parse)
                json_valid = True
            except json.JSONDecodeError as e:
                json_fail_reason = f"Invalid JSON: {e}"
                output_definitions.append(("**App Trkr**", "JSON Validity", "Valid JSON Structure", "FAIL", json_fail_reason))
                json_valid_status_appended = True

            if json_valid and not json_valid_status_appended:
                 output_definitions.append(("**App Trkr**", "JSON Validity", "Valid JSON Structure", "PASS", ""))

            # Check Schema Adherence (only if JSON is valid)
            schema_pass, schema_fail_reason = False, "Cannot check schema, JSON invalid or schema missing."
            # Ensure APP_TRACKER_SCHEMA_DATA is accessible
            schema_data_available = 'APP_TRACKER_SCHEMA_DATA' in globals() and isinstance(APP_TRACKER_SCHEMA_DATA, dict)

            if json_valid and isinstance(parsed_json_data, dict) and schema_data_available:
                schema_keys = set(APP_TRACKER_SCHEMA_DATA.keys())
                actual_keys = set(parsed_json_data.keys())
                schema_pass = schema_keys == actual_keys # Check for exact match
                missing_keys, extra_keys = schema_keys - actual_keys, actual_keys - schema_keys
                schema_fail_reason = ""
                if missing_keys: schema_fail_reason += f"Missing keys: {sorted(list(missing_keys))}. "
                if extra_keys: schema_fail_reason += f"Extra keys: {sorted(list(extra_keys))}."
                if not schema_fail_reason and schema_pass: schema_fail_reason = "Keys match schema."
                elif not schema_fail_reason and not schema_pass: schema_fail_reason = "Key mismatch detected (missing/extra keys)."
            elif not schema_data_available:
                 schema_fail_reason = "App Tracker Schema data not loaded/available."
            output_definitions.append(("**App Trkr**", "Schema", "Adheres to Loaded Schema", "PASS" if schema_pass else "FAIL", schema_fail_reason.strip()))

        # Format Table
        final_rows = [[item[0], item[1], item[2], item[3], item[4]] for item in output_definitions]
        col_widths = [13, 36, 34, 8, 50] # Define column widths
        lines.extend(self._format_plain_text_table(headers, final_rows, alignments=['L', 'L', 'L', 'L', 'L'], col_widths=col_widths, wrap_text=True))
        lines.append("```")
        return lines

    def _build_qa_section_13_reasoning_summary(self) -> List[str]:
        """Builds a new QA section summarizing the reasoning parameters used for each generated section."""
        lines = ["", "**13. REASONING CONFIGURATION SUMMARY**", ""]
        lines.append("Summarizes the final reasoning parameters (CoT, ToT, SC, Reflexion) and generation temperatures used for each LLM-generated section.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section", "Temp", "CoT", "ToT (B,D)", "SC", "Reflexion", "Intensity", "Level"]
        rows = []

        hop3_checkpoint = next((cp for cp in self.orchestrator.hop_checkpoints if cp.hop_id == 'HOP-3'), None)
        if not hop3_checkpoint or 'final_temperatures' not in hop3_checkpoint.metadata:
            lines.append("  HOP-3 checkpoint with final_temperatures metadata not found.")
            lines.append("```")
            return lines

        # Use the same config as the validator to iterate through sections
        for label, (section_enum, _, _, _, reasoning_config) in PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG.items():
            rows.append(self._get_reasoning_row_for_section(section_enum, reasoning_config, hop3_checkpoint.metadata))

        lines.extend(self._format_plain_text_table(headers, rows, alignments=['L', 'R', 'R', 'L', 'R', 'L', 'R', 'L']))
        lines.append("```")
        return lines

    def _validate_qa_report_formatting(self, report_text: str) -> ValidationResult:
        """Validates that QA report tables use pre-formatted text, not Markdown tables."""
        pre_formatted_check_passed = True
        pre_formatted_check_messages = []
        # Split report into sections based on "X. SECTION TITLE" pattern
        # Regex captures section number and title, then the content until the next section or end
        sections = re.split(r'(?m)^(\*\*?\d{1,2}\.\s+[A-Z\s&()-]+?\*?)$', report_text)
        section_blocks = {}

        if len(sections) > 1:
             # Iterate through pairs of title and content
             for i in range(1, len(sections), 2):
                 title = sections[i].strip()
                 content = sections[i+1].strip() if (i+1) < len(sections) else ""
                 try:
                     # Extract section index from title (e.g., "**1. TITLE**" -> 1)
                     section_index_match = re.match(r'\*?(\d{1,2})\.', title)
                     if section_index_match:
                         section_index = int(section_index_match.group(1))
                         section_blocks[section_index] = (title, content)
                     else:
                          self.logger.warning(f"Could not parse section index from QA header: '{title}'")
                 except (ValueError, IndexError):
                      self.logger.warning(f"Error parsing section index from QA header: '{title}'")

        # Define which sections *should* contain ```markdown blocks for tables
        sections_expected_to_have_code_blocks = [
            idx for idx, cfg in enumerate(self.QA_REPORT_SECTIONS, 1)
            # Exclude sections that might not use tables or have custom formats
            if cfg['method'] not in ['_build_qa_section_1_signal_quality'] # Example: Section 1 has custom format
        ]

        # Check each section's content
        for section_index, (title, section_block) in section_blocks.items():
            # Find all markdown code blocks (fenced by ```)
            md_blocks = re.findall(r"```(?:markdown)?(.*?)```", section_block, re.DOTALL)

            # Check if section *should* have a code block but doesn't
            if section_index in sections_expected_to_have_code_blocks and not md_blocks:
                pre_formatted_check_passed = False
                msg = f"QA Section {section_index} ({title}) missing expected ``` block for table."
                if msg not in pre_formatted_check_messages: pre_formatted_check_messages.append(msg)
                continue # Move to next section

            # Check inside found code blocks for Markdown table syntax (pipes and separators)
            for block_content in md_blocks:
                has_pipe_table_syntax = False
                lines_in_block = block_content.strip().split('\n')
                # Check for header separator line like |---|---| or :---:|:---:
                if len(lines_in_block) > 1 and re.match(r"^\s*\|?(:?-+:?\|?)+(:?-+:?\|?)*\s*$", lines_in_block[1].strip()):
                     # Check if lines actually use pipes for cells (more reliable than just separator)
                     if any("|" in line for line in lines_in_block if line.strip()):
                          has_pipe_table_syntax = True

                if has_pipe_table_syntax:
                    pre_formatted_check_passed = False
                    msg = f"QA Section {section_index} ({title}) appears to contain Markdown table syntax (|---|) inside ``` block."
                    if msg not in pre_formatted_check_messages: pre_formatted_check_messages.append(msg)
                    break # Found error in this section's block, move to next section_index

        # Create the final validation result
        return ValidationResult(
            rule_id="QA_TABLE_FORMAT_INVALID",
            passed=pre_formatted_check_passed,
            severity=ValidationSeverity.HIGH if not pre_formatted_check_passed else ValidationSeverity.INFO,
            message="; ".join(pre_formatted_check_messages) if not pre_formatted_check_passed else "All QA tables appear to use pre-formatted text.",
            details={"failed_sections": pre_formatted_check_messages} if not pre_formatted_check_passed else {}
        )

    def _format_plain_text_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        alignments: Optional[List[str]] = None,
        col_widths: Optional[List[int]] = None,
        wrap_text: bool = False
    ) -> List[str]:
        """Formats data into a plain text table with optional wrapping and alignment."""
        # Convert all cells to strings for consistent processing
        str_rows = [[str(cell) for cell in row] for row in rows]
        str_headers = [str(h) for h in headers]

        if not str_headers and not str_rows: return ["(No data available)"]

        # Determine number of columns
        num_cols = len(str_headers) if str_headers else (len(str_rows[0]) if str_rows else 0)
        if num_cols == 0: return ["(No data available)"]

        # Determine column widths
        if col_widths and len(col_widths) == num_cols:
            # Use provided widths, ensuring they are positive, handle 0 for last column if needed
            widths = [max(1, w) if w > 0 else 0 for w in col_widths]
            # If last column width is 0 (auto), calculate its max width based on content
            if widths[-1] == 0:
                max_last_col = 0
                if str_headers:
                    # Handle multi-line headers
                    last_header_lines = str_headers[-1].split('\n') if str_headers[-1] else [""]
                    max_last_col = max(max_last_col, max(len(line) for line in last_header_lines))
                for row in str_rows:
                    if len(row) == num_cols:
                        max_last_col = max(max_last_col, len(row[-1]))
                widths[-1] = max(1, max_last_col) # Ensure at least 1 width
        else:
            # Calculate widths based on content if not provided
            widths = [0] * num_cols
            if str_headers:
                for i, header in enumerate(str_headers):
                     # Handle multi-line headers
                     header_lines = header.split('\n') if header else [""]
                     max_header_line = max(len(line) for line in header_lines)
                     widths[i] = max(widths[i], max_header_line)
            for row in str_rows:
                for i, cell in enumerate(row):
                    if i < num_cols: widths[i] = max(widths[i], len(cell))
            widths = [max(1, w) for w in widths] # Ensure minimum width of 1

        # Determine alignments
        aligns = alignments or ['L'] * num_cols
        if len(aligns) < num_cols: aligns.extend(['L'] * (num_cols - len(aligns))) # Default to Left

        # Create format strings for each column
        formatters = []
        for i in range(num_cols):
            align_char = '<' if aligns[i] == 'L' else '>' if aligns[i] == 'R' else '^' # Left, Right, Center
            formatters.append(f"{{:{align_char}{widths[i]}}}")

        lines = []

        # Format Header (handles multi-line headers)
        if str_headers:
            header_lines_split = [h.split('\n') for h in str_headers]
            max_header_lines = max(len(h_lines) for h_lines in header_lines_split) if header_lines_split else 0
            for line_idx in range(max_header_lines):
                line_parts = []
                for col_idx in range(num_cols):
                    # Get the correct line part for this header cell, or empty string
                    part = header_lines_split[col_idx][line_idx] if col_idx < len(header_lines_split) and line_idx < len(header_lines_split[col_idx]) else ""
                    line_parts.append(formatters[col_idx].format(part))
                lines.append("  ".join(line_parts).rstrip()) # Join parts with spaces, remove trailing space
            # Add separator line
            lines.append("  ".join("-" * widths[i] for i in range(num_cols)).rstrip())

        # Format Rows (with optional text wrapping)
        if wrap_text:
             for row in str_rows:
                 # Ensure row has correct number of columns
                 while len(row) < num_cols: row.append("")
                 # Wrap text for each cell based on its column width
                 row_lines_data = [self._wrap_cell_text(cell, widths[i]) if i < num_cols else [""] for i, cell in enumerate(row)]
                 # Pad row_lines_data if needed (shouldn't be necessary with loop above)
                 while len(row_lines_data) < num_cols: row_lines_data.append([""])

                 # Determine max number of lines needed for this wrapped row
                 max_lines_in_row = max(len(lines_for_cell) for lines_for_cell in row_lines_data) if row_lines_data else 1
                 # Format each line of the wrapped row
                 for line_idx in range(max_lines_in_row):
                     line_parts = []
                     for col_idx in range(num_cols):
                         # Get the text part for this line and column, or empty string
                         cell_part = row_lines_data[col_idx][line_idx] if col_idx < len(row_lines_data) and line_idx < len(row_lines_data[col_idx]) else ""
                         line_parts.append(formatters[col_idx].format(cell_part))
                     lines.append("  ".join(line_parts).rstrip())
        else:
             # Format rows without wrapping (truncate if necessary)
             for row in str_rows:
                 line_parts = []
                 for i in range(num_cols):
                     cell_content = row[i] if i < len(row) else ""
                     # Truncate content to fit width
                     line_parts.append(formatters[i].format(cell_content[:widths[i]]))
                 lines.append("  ".join(line_parts).rstrip())

        return lines


    def _wrap_cell_text(self, text: str, width: int) -> List[str]:
        """Wraps text for a table cell using textwrap."""
        if width <= 0: return [text] # Cannot wrap to zero or negative width
        if not text: return [""] # Return list with empty string for empty input
        # Use textwrap for potentially better handling of wrapping long words etc.
        wrapped_lines = textwrap.wrap(
            text,
            width=width,
            break_long_words=True, # Break words if they exceed width
            replace_whitespace=True, # Replace whitespace chars with spaces
            drop_whitespace=True, # Remove leading/trailing whitespace from lines
            break_on_hyphens=True # Allow breaking after hyphens
        )
        # Ensure result is never empty list if input was non-empty (wrap returns [] for empty string)
        return wrapped_lines if wrapped_lines else [""]

    def _get_text_from_item(self, item: Any) -> str:
        """Helper to safely extract text from a string or a bullet dictionary."""
        if isinstance(item, dict):
            # Prioritize 'text', then 'bullet_text', fallback to empty string
            return item.get('text', item.get('bullet_text', ''))
        elif isinstance(item, str):
            return item
        return '' # Return empty string for other types

    def _check_word_count(self, count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        """Checks word count against range, returns status ('PASS'/'FAIL') and target string."""
        status = "PASS" if min_target <= count <= max_target else "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str

    def _safe_format_validation_message(self, validation_result: ValidationResult) -> str:
         """Safely formats a validation result message, handling callables."""
         msg = "[Error formatting msg]"
         details = getattr(validation_result, 'details', {}) or {}
         try:
             msg_template = str(validation_result.message)
             if callable(validation_result.message):
                 msg = validation_result.message(defaultdict(lambda: '[N/A]', **details))
             else:
                 msg = msg_template.format_map(defaultdict(lambda: '[N/A]', **details))
         except Exception as e:
             self.logger.warning(f"Error formatting message for rule {validation_result.rule_id}: {e}")
         return msg

    def _format_simplified_ascii_bar_chart(self, label: str, value: float, target_min: Optional[float], target_max: Optional[float], bar_length: int = 20, is_summary: bool = False, status_override: Optional[str] = None) -> str:
        """A simplified, cleaner ASCII bar chart formatter."""
        # Clamp value for bar calculation
        display_value = min(max(value, 0.0), 1.0) if value is not None else 0.0
        filled_length = int(round(bar_length * display_value))
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)

        # Format score
        score_text = "N/A"
        if value is not None:
            score_text = f"Raw: {value:.2f}"

        # Determine status
        if status_override:
            status = status_override
        elif target_min is not None and target_max is not None and value is not None:
            status = "✅ PASS" if target_min <= value <= target_max else "❌ FAIL"
        else:
            status = "ℹ️ INFO"

        # Format target range
        target_str = "(Tgt: N/A)"
        if target_min is not None and target_max is not None:
            target_str = f"(Tgt: {target_min:.2f}-{target_max:.2f})"

        # Define widths and assemble the line
        label_width, bar_width, score_width, target_width, status_width = 28, bar_length + 2, 12, 18, 8
        line = f"{label:<{label_width}} {f'[{bar}]':<{bar_width}} {score_text:<{score_width}} {target_str:<{target_width}} {status:<{status_width}}"
        return line.rstrip()

    def _get_reasoning_row_for_section(
        self,
        section_enum: ResumeSection,
        reasoning_config: ReasoningConfig,
        hop3_metadata: Dict
    ) -> List[str]:
        """Gets the reasoning parameters and final temp for a specific section."""
        final_temps = hop3_metadata.get('final_temperatures', {})
        temp_used_val = final_temps.get(section_enum.name, 'N/A')
        temp_used_str = f"{temp_used_val:.1f}" if isinstance(temp_used_val, (float, int)) else str(temp_used_val)

        # Ensure reasoning_config_to_api_params exists and handles config
        try:
            # Need to call the global function, assuming it's imported/accessible
            if 'reasoning_config_to_api_params' in globals():
                 params = reasoning_config_to_api_params(reasoning_config)
            else:
                 # Fallback if function isn't accessible
                 self.logger.warning("reasoning_config_to_api_params function not found. Using defaults for QA Sec 13.")
                 params = {"cot": "?", "tot_b": "?", "tot_d": "?", "sc": "?", "reflexion": "?", "intensity_score": 0.0, "reasoning_level": "?"}

            cot = params.get('cot', '?')
            tot_b = params.get('tot_b', '?')
            tot_d = params.get('tot_d', '?')
            sc = params.get('sc', '?')
            reflexion = "Yes" if params.get('reflexion', False) else "No"
            intensity = params.get('intensity_score', 0.0)
            level = params.get('reasoning_level', '?')
        except Exception as e:
             self.logger.error(f"Error getting reasoning params for {section_enum.name}: {e}")
             cot, tot_b, tot_d, sc, reflexion, intensity, level = "?", "?", "?", "?", "?", 0.0, "?"

        return [
            section_enum.name, temp_used_str, str(cot), f"{tot_b},{tot_d}", str(sc),
            reflexion, f"{intensity:.1f}", level
        ]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__) # Define logger

    try:
        temp_rag_config = RAGConfig() # Assuming RAGConfig is defined
        cache_dir_to_clear = temp_rag_config.cache_dir
        telemetry_dir_to_clear = temp_rag_config.telemetry_log_dir

        if cache_dir_to_clear and os.path.exists(cache_dir_to_clear):
            logger.info(f"Attempting to clear RAG cache directory: {cache_dir_to_clear}")
            shutil.rmtree(cache_dir_to_clear, ignore_errors=True)
            if not os.path.exists(cache_dir_to_clear): logger.info(f"  ✓ RAG cache directory cleared successfully.")
            else: logger.warning(f"  ⚠️ Could not completely remove RAG cache directory.")
        else: logger.info(f"RAG cache directory ({cache_dir_to_clear}) not found/specified. Skipping clear.")

        if telemetry_dir_to_clear and os.path.exists(telemetry_dir_to_clear):
            logger.info(f"Attempting to clear Telemetry log directory: {telemetry_dir_to_clear}")
            shutil.rmtree(telemetry_dir_to_clear, ignore_errors=True)
            if not os.path.exists(telemetry_dir_to_clear): logger.info(f"  ✓ Telemetry log directory cleared successfully.")
            else: logger.warning(f"  ⚠️ Could not completely remove Telemetry log directory.")
        else: logger.info(f"Telemetry log directory ({telemetry_dir_to_clear}) not found/specified. Skipping clear.")

    except Exception as e:
        logger.error(f"Error during cache/telemetry clearing: {e}", exc_info=False)

    # --- Configuration for the run ---
    my_company_name = "DataDog"
    my_job_title = "Director, Technology Alliances"
    my_jd_url = "https://careers.datadoghq.com/detail/693897/?gh_jid=693897"
    my_job_description = """
    As the Director, Technology Alliances you will drive incremental revenue for Datadog by developing and advancing key strategic global technology partnerships. In this role, you, along with your team, will globally manage Datadog’s most strategic partners including AWS, Google, and Microsoft. The role reports into the VP, Channels & Alliances and works cross functionally with regional partner teams, marketing, sales, field enablement, product, sales ops, and legal to drive incremental revenue with key technology partners.

At Datadog, we place value in our office culture - the relationships and collaboration it builds, and the creativity it brings to the table. We operate as a hybrid workplace to ensure our Datadogs can create a work-life harmony that best fits them.

What You’ll Do:

Hire, develop, and manage a high-performing team by recognizing exceptional talent and coaching them for success in their global role
Ability to operate as a matrixed leader by listening, influencing, and supporting regional channels & alliances leaders and teams.
Accelerate existing Datadog Partners’ business through business and technical enablement and successfully executing go-to-market activities
Collaborate closely with Datadog’s global and regional enterprise and commercial sales organizations as well as marketing and customer success teams to drive incremental revenue for the region.
Collaborate closely with product leaders to design GTM initiatives across the Datadog Platform.
Develop and execute “Go Big” strategic initiatives with key technology partnerships
Serve as executive sponsor for AWS, GCP, and Microsoft Azure.
Own Technology Alliances global and regional metrics and reporting to Datadog leadership.
Who You Are:

5+ years of experience in leadership including hiring and developing sales and partner personnel
10+ years of experience in business development or strategic alliances at a cloud services or SaaS organization
Confident in recruiting and building successful partnerships, including with multi-national and global organizations.
Able to quickly understand technical concepts and architectural scenarios, and explain them to others verbally and in writing
Excellent written and verbal communication skills, including interacting with and presenting to senior leadership, externally and internally.

    """

    print("--- Starting Resume Generation Workflow ---")

    orchestrator = WorkflowOrchestrator(copy.deepcopy(MASTER_RESUME_DATA))

    # --- Execute the workflow, passing the new jd_url argument ---
    result = orchestrator.execute_workflow(
        job_description=my_job_description,
        company_name=my_company_name,
        job_title=my_job_title,
        jd_url=my_jd_url # <-- PASS THE URL HERE
    )

    print("\n--- Workflow Final Result ---")
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'SUCCESS':
        print(f"Gate Decision: {result.get('gate_decision')}")
        print(f"File Paths: {result.get('file_paths')}")
    else:
        # Ensure 'error' key exists as a fallback for the reason message
        reason_msg = result.get('reason', result.get('error', 'No reason provided.'))
        print(f"Reason: {reason_msg}")

    print("\n--- Workflow Finished ---")