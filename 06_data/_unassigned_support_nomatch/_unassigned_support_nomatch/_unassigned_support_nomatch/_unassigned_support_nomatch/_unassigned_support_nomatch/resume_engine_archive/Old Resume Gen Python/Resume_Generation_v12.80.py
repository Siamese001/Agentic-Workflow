from __future__ import annotations

from dotenv import load_dotenv
load_dotenv() # This loads the variables from .env into os.environ

import json
import re # Added for truncation check logic and new validation rules
import hashlib
import math
import logging
import os
import time


__version__ = "12.80"
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

import random

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, ClassVar # Added ClassVar

@dataclass
class ReasoningConfig:
    """Centralized reasoning configuration"""
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 4
    reflexion: bool = True
    max_reflexion_loops: int = 3

    # --- START FIX: MOVED DECLARATIONS INSIDE THE CLASS ---
    # Section-specific configurations
    K0_HEADLINE_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K5_UNIFY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K5_UNIFY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K6_IBM_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K6_IBM_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K8_EY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K8_EY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K9_EARLY_CAREER_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K9_EARLY_CAREER_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K2_SKILLS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K10_COMPETENCIES_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    DEFAULT: ClassVar[Optional[ReasoningConfig]] = None
    # --- END FIX ---

@dataclass
class ContentConstraintsConfig:
    """Centralized configuration for content constraints like word counts and thresholds."""
    # Overall Resume
    TOTAL_WORD_COUNT_MIN: int = 950
    TOTAL_WORD_COUNT_MAX: int = 1100
    MIN_JD_KEYWORDS: int = 7

    # K.0 Headline
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_MIN_CHARS: int = 60
    HEADLINE_MAX_CHARS: int = 90
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K.1 Executive Summary
    # EXEC_SUMMARY_WORD_COUNT_MIN: int = 140 # Removed Constraint
    # EXEC_SUMMARY_WORD_COUNT_MAX: int = 170 # Removed Constraint
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 7
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9 # Increased max sentence count to 9
    K1_MIN_DIFFERENTIATORS: int = 4

    # --- START CHANGES: Updated Unify/IBM Overview Word Counts ---
    # Experience Overviews (Synthesized from Bullets)
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25 # NEW RANGE
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40 # NEW RANGE
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25   # NEW RANGE
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35   # NEW RANGE
    # --- END CHANGES ---
    EY_OVERVIEW_WORD_COUNT_MIN: int = 25
    EY_OVERVIEW_WORD_COUNT_MAX: int = 40
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 20
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 35
    # <<< Corrected: Added TraderSense constraints (using EY as template, adjust if needed)
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 35


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

    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65
    SECTION_SIGNAL_SCORE_MAX: float = 0.90

@dataclass
class ThematicAnalysis: # Simplified for testing compatibility
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
     weighting_formula: Optional[Dict] = None # Added field

# Define the default config first
ReasoningConfig.DEFAULT = ReasoningConfig()

# Define configurations as a list of tuples: (AttributeName, ConfigArgs_or_Default)
reasoning_configs_list = [
    ("K0_HEADLINE_CONFIG", dict(cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=5, reflexion=True)),
    ("K1_EXECUTIVE_SUMMARY_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=4)),
    ("K5_UNIFY_BULLETS_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)),
    ("K5_UNIFY_OVERVIEW_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)),
    ("K6_IBM_BULLETS_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True)),
    ("K6_IBM_OVERVIEW_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)),
    ("K8_EY_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True)),
    ("K8_EY_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True)),
    ("K9_EARLY_CAREER_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K9_EARLY_CAREER_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K2_SKILLS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=True)),
    ("K10_COMPETENCIES_CONFIG", dict(cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=6, reflexion=True)),
]

# Loop through the list and set the ClassVars
for config_name, config_value in reasoning_configs_list:
    if isinstance(config_value, dict):
        # Create a new ReasoningConfig instance using the dictionary arguments
        setattr(ReasoningConfig, config_name, ReasoningConfig(**config_value))
    elif isinstance(config_value, ReasoningConfig):
        # Assign the existing default instance
        setattr(ReasoningConfig, config_name, config_value)
    else:
        # Handle potential errors or unexpected types if necessary
        print(f"Warning: Unexpected config value type for {config_name}: {type(config_value)}")
        
# ============================================================================
# REASONING CONFIGURATION HELPERS
# ============================================================================

def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """
    [MODIFIED FOR OPTION B]
    Converts reasoning config to Gemini API parameters.
    Uses _allocate_tokens_from_depth for proportional max_output_tokens.
    """
    import logging # Ensure logging is imported if not already
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)
    intensity, level = _calculate_reasoning_intensity(params)
    params['intensity_score'] = intensity
    params['reasoning_level'] = level

    temperature = _get_generation_temperature()

    # --- START CHANGE FOR OPTION B ---
    # Calculate max_tokens using the allocation function based on reasoning params
    allocated_max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    # Use RAGConfig().max_tokens only as an absolute upper bound if needed,
    # otherwise, trust the allocated value.
    # Ensure RAGConfig is accessible
    try:
         absolute_max_tokens = RAGConfig().max_tokens # e.g., 30000
    except NameError:
         logging.warning("RAGConfig not found, using default absolute max_tokens=30000.")
         absolute_max_tokens = 30000

    # Ensure allocated tokens do not exceed the absolute max
    final_max_tokens = min(allocated_max_tokens, absolute_max_tokens)
    # --- END CHANGE FOR OPTION B ---

    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(f"Reasoning config: intensity={intensity:.1f}, temp={temperature}, calculated_max_tokens={allocated_max_tokens}, final_max_tokens={final_max_tokens}, level={level}")
    except NameError: # Handle case where logger might not be fully configured yet
        pass

    return {
        # --- Apply the calculated max_tokens here ---
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=final_max_tokens),
        # --- End change ---
        "system_prompt_addendum": prompt_addendum,
        **params # Include cot, tot_b, tot_d, sc, reflexion, max_loops, intensity_score, reasoning_level
    }

def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """Handles defaults and clamps reasoning config values."""
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12 # Keep original default intention
    reflexion = config.reflexion if config.reflexion is not None else True
    max_loops = config.max_reflexion_loops if config.max_reflexion_loops is not None else 2

    # --- START FIX: Clamp sc (self-consistency / candidate_count) to API max of 8 ---
    sc_clamped = max(1, min(sc, 8))
    # --- END FIX ---


    return {
        "cot": max(2, min(config.cot_min_paths if config.cot_min_paths is not None else 3, 8)),
        "tot_b": max(2, min(tot_b, 6)),
        "tot_d": max(2, min(tot_d, 5)),
        # --- START FIX: Use clamped value ---
        "sc": sc_clamped,
        # --- END FIX ---
        "reflexion": reflexion,
        "max_loops": max(1, min(max_loops, 5))
    }

def _calculate_reasoning_intensity(params: Dict) -> Tuple[float, str]:
    """Calculates a numeric intensity score and a qualitative level from reasoning parameters."""
    intensity = (params['cot'] * 2.0) + (params['tot_b'] * 2.0) + (params['tot_d'] * 2.0) + (params['sc'] / 5.0)
    
    if intensity >= 35: level = "VERY_HIGH"
    elif intensity >= 25: level = "HIGH"
    elif intensity >= 15: level = "MODERATE"
    elif intensity >= 8: level = "LOW"
    else: level = "MINIMAL"
    
    return intensity, level

def _get_generation_temperature() -> float:
    """
    [OPTIMIZED FOR CREATIVITY]
    This version maximizes temperature to promote creative and unique output,
    while the workflow's Reasoning Intensity (CoT, ToT) maintains signal/relevance.
    The 'intensity' parameter was previously unused, so it has been removed.
    """
    # Set a high, consistent temperature regardless of intensity.
    # 0.9 is very creative. 1.0 is the maximum.
    # This value is already within the valid [0.0, 1.0] range.
    return 0.9

def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """
    [REVISED FOR OPTION B]
    Allocates max_tokens based on reasoning depth and complexity, providing
    higher limits for more complex reasoning tasks.
    """
    # Set higher base and tier limits, aligning closer to RAGConfig.max_tokens
    base_limit = 16384      # Increased base significantly
    high_sc_limit = 24000   # Increased (Note: sc capped at 8 later)
    mid_complex_limit = 26000 # Increased
    high_complex_limit = 28000# Increased
    max_complex_limit = 30000 # Increased to match RAGConfig upper bound

    if tot_d >= 4:
        max_tokens = max_complex_limit
    elif tot_d >= 3 and cot >= 5:
        max_tokens = high_complex_limit
    elif tot_d >= 3 or cot >= 5:
        max_tokens = mid_complex_limit
    # Check against the *actual* sc value before clamping (more accurate)
    # Note: _get_normalized_reasoning_params clamps sc to 8 later,
    # so this specific elif sc >= 15 might not be hit often in practice.
    elif sc >= 15:
        max_tokens = high_sc_limit
    else:
        max_tokens = base_limit

    # Ensure bounds are within [new_base_limit, RAGConfig.max_tokens]
    # Use RAGConfig().max_tokens as the absolute ceiling.
    rag_config_max = 30000 # Assuming RAGConfig().max_tokens is 30000
    return max(base_limit, min(max_tokens, rag_config_max))

def _build_reasoning_prompt_addendum(params: Dict) -> str:
    """Constructs the system prompt addendum based on reasoning parameters."""
    p = params
    addendum = f"\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n"
    addendum += f"(Configuration Level: {p['reasoning_level']}, Intensity: {p['intensity_score']:.1f}/40)\n\n"

    if p['cot'] >= 5: addendum += f"• MANDATORY: Explore at least {p['cot']} distinct reasoning paths before reaching a conclusion.\n"
    elif p['cot'] >= 4: addendum += f"• Explore {p['cot']} different reasoning paths; compare and synthesize insights.\n"
    else: addendum += f"• Consider multiple reasoning approaches before concluding.\n"

    if p['tot_b'] >= 5: addendum += f"• MANDATORY: At each decision point, systematically evaluate {p['tot_b']} different branches/alternatives.\n"
    elif p['tot_b'] >= 4: addendum += f"• Explore {p['tot_b']} decision branches at critical junctures; document tradeoffs.\n"
    else: addendum += f"• Consider multiple decision branches at key steps.\n"

    if p['tot_d'] >= 5: addendum += f"• MANDATORY: Reasoning depth must be {p['tot_d']}+ levels deep with explicit layer separation.\n"
    elif p['tot_d'] >= 4: addendum += f"• Provide {p['tot_d']}-level deep reasoning: foundation → intermediate → advanced → synthesis.\n"
    elif p['tot_d'] >= 3: addendum += f"• Provide {p['tot_d']}-level reasoning with clear progression of thinking.\n"
    else: addendum += f"• Structure reasoning with clear logical progression.\n"

    if p['reflexion'] and p['max_loops'] >= 3: addendum += f"• MANDATORY: Review your answer {p['max_loops']} times, refining on each pass. Document improvements.\n"
    elif p['reflexion'] and p['max_loops'] >= 2: addendum += f"• Review your answer {p['max_loops']} times; improve if refinements are identified.\n"
    elif p['reflexion']: addendum += f"• Review and refine your answer at least once.\n"

    addendum += f"\nAll directives MUST be followed in the output.\n"
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

from enum import Enum, auto
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Any, Union, Callable

# 1. DEFINE THE ENUM FIRST
# This class must be defined before ValidationResult and ValidationRule
class ValidationSeverity(Enum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

# 2. USE THE ENUM IN THE DATACLASS
@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity  # <-- Correctly references the class
    message: str
    details: Dict = field(default_factory=dict)

# 3. USE THE ENUM IN THE NEXT CLASS
class ValidationRule:
    """Single validation rule with callable validator"""

    def __init__(self, rule_id: str, severity: ValidationSeverity, validator: Any, error_message: Union[str, Callable[[Dict], str]], category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category
    # --- END FIX ---

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
            
            # Calculate JD hash for tracking
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
            # Check for mock indicators
            thematic_str = str(thematic_analysis).lower()
            mock_indicators = ['mock', 'sample', 'example', 'placeholder', 'fallback']
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
        
        # E10: Enrichment uses JD
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
            mock_indicators = ['mock', 'sample', 'example@', 'placeholder']
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
        
        # E10: Enrichment uses JD (checking the input to the artist)
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

        # E11: Validation checks JD keywords
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

        # E9: Content has JD keywords (re-check on final buffer)
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

        # E14: No mock data in final buffer
        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = str(staging_buffer._data).lower()
            mock_indicators = ['mock', 'sample', 'example@', 'placeholder', 'fallback']
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
        
        # E12: Files contain JD content
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

        # E14: No mock data in file paths (checks for placeholder names)
        if file_paths:
            paths_str = "".join(file_paths.values()).lower()
            mock_indicators = ['mock', 'sample', 'example', 'placeholder']
            has_mock = any(indicator in paths_str for indicator in mock_indicators)
            results.append(JDEnforcementResult(
                JDEnforcementRule.E14_NO_MOCK_DATA,
                not has_mock,
                "No mock data indicators found in file paths" if not has_mock else "Mock data indicators found in file paths",
                gate_id
            ))
        else:
            # Pass if no files, as there's nothing to check
            results.append(JDEnforcementResult(JDEnforcementRule.E14_NO_MOCK_DATA, True, "No files to check for mock data", gate_id))
        
        self.enforcement_results.extend(results)
        return results
    
    def validate_qa_report(self, qa_report: Dict, gate_id: str) -> List[JDEnforcementResult]:
        """
        GATE-8: Validate QA report verifies JD.
        Enforces: E13, E15
        """
        results = []
        
        # E13: QA verifies JD
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
        
        # E15: Complete audit trail
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

APP_TRACKER_SCHEMA_V4 = {
# Global schema for the Application Tracker, derived from AppTrackerQAValidator.
    "Company": "", "Category": "", "Sub-Category": "", "Job Title": "", "Primary Job Role": "",
    "JD URL": "", "Application Date": "", "Pipeline Status": "",
    "Hiring Recruiter": "", "Hiring Recruiter URL": "", "Hiring Recruiter Interview Date": "",
    "Hiring Manager": "", "Hiring Manager URL": "", "Hiring Manager Interview Date": "",
    "Other Interviewer": "", "Other Interviewer URL": "", "Other Interviewer Date": "",
    "Other Interviewer 2": "", "Other Interviewer 2 URL": "", "Other Interviewer 2 Date": "",
    "Base Resume": "", "Versioned Resume": "", "Outreach Channel": "",
    "Recruiter / Contact 1 Name": "", "Recruiter / Contact 1 Title": "", "Recruiter / Contact 1 URL": "",
    "Date Communication Sent 1": "", "Follow-Up Date 1": "", "Second Follow-Up Date 1": "",
    "Recruiter / Contact 2 Name": "", "Recruiter / Contact 2 Title": "", "Recruiter / Contact 2 URL": "",
    "Date Communication Sent 2": "", "Follow-Up Date 2": "", "Second Follow-Up Date 2": "",
    "Recruiter / Contact 3 Name": "", "Recruiter / Contact 3 Title": "", "Recruiter / Contact 3 URL": "",
    "Date Communication Sent 3": "", "Follow-Up Date 3": "", "Second Follow-Up Date 3": "",
    "Recruiter / Contact 4 Name": "", "Recruiter / Contact 4 Title": "", "Recruiter / Contact 4 URL": "",
    "Date Communication Sent 4": "", "Follow-Up Date 4": "", "Second Follow-Up Date 4": "",
    "Recruiter / Contact 5 Name": "", "Recruiter / Contact 5 Title": "", "Recruiter / Contact 5 URL": "",
    "Date Communication Sent 5": "", "Follow-Up Date 5": "", "Second Follow-Up Date 5": "",
    "Closure Reason": ""
}

COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}""" # Added two spaces at the end of each line to force Markdown line breaks

class AppTrackerQAValidator:
    # Exact 54-field schema from App Schema v4
    SCHEMA_FIELDS_V4 = [
        "Company", "Category", "Sub-Category", "Job Title", "Primary Job Role",
        "JD URL", "Application Date", "Pipeline Status",
        "Hiring Recruiter", "Hiring Recruiter URL", "Hiring Recruiter Interview Date",
        "Hiring Manager", "Hiring Manager URL", "Hiring Manager Interview Date",
        "Other Interviewer", "Other Interviewer URL", "Other Interviewer Date",
        "Other Interviewer 2", "Other Interviewer 2 URL", "Other Interviewer 2 Date",
        "Base Resume", "Versioned Resume", "Outreach Channel",
        "Recruiter / Contact 1 Name", "Recruiter / Contact 1 Title", "Recruiter / Contact 1 URL",
        "Date Communication Sent 1", "Follow-Up Date 1", "Second Follow-Up Date 1",
        "Recruiter / Contact 2 Name", "Recruiter / Contact 2 Title", "Recruiter / Contact 2 URL",
        "Date Communication Sent 2", "Follow-Up Date 2", "Second Follow-Up Date 2",
        "Recruiter / Contact 3 Name", "Recruiter / Contact 3 Title", "Recruiter / Contact 3 URL",
        "Date Communication Sent 3", "Follow-Up Date 3", "Second Follow-Up Date 3",
        "Recruiter / Contact 4 Name", "Recruiter / Contact 4 Title", "Recruiter / Contact 4 URL",
        "Date Communication Sent 4", "Follow-Up Date 4", "Second Follow-Up Date 4",
        "Recruiter / Contact 5 Name", "Recruiter / Contact 5 Title", "Recruiter / Contact 5 URL",
        "Date Communication Sent 5", "Follow-Up Date 5", "Second Follow-Up Date 5",
        "Closure Reason"
    ]
    
    # Controlled enums
    PIPELINE_STATUS_ENUM = ["Applied", "Follow-Up", "Interview", "Rejected", "Closed", "Waiting"]
    OUTREACH_CHANNEL_ENUM = ["Recruiter Outreach", "Contact Outreach", "Blended Outreach", "No Outreach", ""]
    CLOSURE_REASON_ENUM = ["Rejected", "No Reply", "Role Filled", "On Hold", "Withdrawn by Candidate", 
                           "Internal Hire", "Changed Scope", "Role Too Junior", ""]
    
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
        if not url or not url.strip():
            return False
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(url_pattern, url.strip()))
    
    def _is_linkedin_profile(self, url: str) -> bool:
        """Validate LinkedIn canonical profile format."""
        if not url or not url.strip():
            return False
        linkedin_pattern = r'^https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?$'
        return bool(re.match(linkedin_pattern, url.strip()))
    
    def validate_tracker_data(self, tracker_rows: List[Dict]) -> Dict:
        """
        Validate complete app tracker data.
        Returns PASSED or BLOCKED JSON outcome.
        """
        # R1: Schema shape and exact order
        for idx, row in enumerate(tracker_rows):
            if list(row.keys()) != self.SCHEMA_FIELDS_V4:
                self._log_fail("R1", idx, "schema", 
                              f"Schema fields mismatch at row {idx}",
                              f"Ensure exactly 54 fields in correct order")
            else:
                self._log_pass("R1")
        
        # Per-row validation
        for idx, row in enumerate(tracker_rows):
            self._validate_row(idx, row)
        
        # Generate outcome
        if self.errors:
            return self._generate_blocked_outcome()
        else:
            return self._generate_passed_outcome(tracker_rows)
    
    def _validate_row(self, idx: int, row: Dict):
        """Validate single tracker row against R2-R22."""
        
        # R2: Pipeline Status enum
        status = row.get("Pipeline Status", "").strip()
        if status and status not in self.PIPELINE_STATUS_ENUM:
            self._log_fail("R2", idx, "Pipeline Status",
                          f"Invalid status '{status}'",
                          f"Use one of: {', '.join(self.PIPELINE_STATUS_ENUM)}")
        else:
            self._log_pass("R2")
        
        # R3: Outreach Channel enum
        channel = row.get("Outreach Channel", "").strip()
        if channel not in self.OUTREACH_CHANNEL_ENUM:
            self._log_fail("R3", idx, "Outreach Channel",
                          f"Invalid channel '{channel}'",
                          f"Use one of: {', '.join(self.OUTREACH_CHANNEL_ENUM)}")
        else:
            self._log_pass("R3")
        
        # R4: Closure Reason enum
        closure = row.get("Closure Reason", "").strip()
        if closure not in self.CLOSURE_REASON_ENUM:
            self._log_fail("R4", idx, "Closure Reason",
                          f"Invalid closure reason '{closure}'",
                          f"Use one of: {', '.join(self.CLOSURE_REASON_ENUM)}")
        else:
            self._log_pass("R4")
        
        # R5: Channel gating validation
        self._validate_channel_gating(idx, row, channel)
        
        # R10: JD URL and Application Date validation
        jd_url = row.get("JD URL", "").strip()
        app_date = row.get("Application Date", "").strip()
        if jd_url:
            if not app_date:
                self._log_fail("R10", idx, "Application Date",
                              "Application Date required when JD URL present",
                              "Add valid MM/DD/YYYY date")
            elif not self._parse_date(app_date):
                self._log_fail("R10", idx, "Application Date",
                              f"Invalid date format '{app_date}'",
                              "Use MM/DD/YYYY format")
            else:
                self._log_pass("R10")
        
        # R11-R12: Date validation for contacts
        for i in range(1, 6):
            date_sent = row.get(f"Date Communication Sent {i}", "").strip()
            followup1 = row.get(f"Follow-Up Date {i}", "").strip()
            followup2 = row.get(f"Second Follow-Up Date {i}", "").strip()
            
            if date_sent and not self._parse_date(date_sent):
                self._log_fail("R11", idx, f"Date Communication Sent {i}",
                              f"Invalid date format '{date_sent}'",
                              "Use MM/DD/YYYY format")
            else:
                self._log_pass("R11")
            
            if followup1 and not self._parse_date(followup1):
                self._log_fail("R12", idx, f"Follow-Up Date {i}",
                              f"Invalid date format '{followup1}'",
                              "Use MM/DD/YYYY format")
            else:
                self._log_pass("R12")
            
            if followup2 and not self._parse_date(followup2):
                self._log_fail("R12", idx, f"Second Follow-Up Date {i}",
                              f"Invalid date format '{followup2}'",
                              "Use MM/DD/YYYY format")
            else:
                self._log_pass("R12")
        
        # R13-R15: Status/closure mapping
        if status in ["Rejected", "Closed"] and not closure:
            self._log_fail("R13", idx, "Closure Reason",
                          f"Closure Reason required for status '{status}'",
                          "Provide valid closure reason")
        else:
            self._log_pass("R13")
        
        if status not in ["Rejected", "Closed"] and closure:
            self._log_fail("R14", idx, "Closure Reason",
                          f"Closure Reason should be blank for status '{status}'",
                          "Clear closure reason")
        else:
            self._log_pass("R14")
        
        # R16-R18: Contact integrity and LinkedIn validation
        for i in range(1, 6):
            name = row.get(f"Recruiter / Contact {i} Name", "").strip()
            title = row.get(f"Recruiter / Contact {i} Title", "").strip()
            url = row.get(f"Recruiter / Contact {i} URL", "").strip()
            
            # R16: All-or-none presence
            has_any = bool(name or title or url)
            has_all = bool(name and title and url)
            
            if has_any and not has_all:
                self._log_fail("R16", idx, f"Recruiter / Contact {i}",
                              "Contact must have all fields (Name, Title, URL) or none",
                              "Complete all contact fields or clear all")
            else:
                self._log_pass("R16")
            
            # R18: LinkedIn canonical format
            if url and not self._is_linkedin_profile(url):
                self._log_fail("R18", idx, f"Recruiter / Contact {i} URL",
                              f"Invalid LinkedIn profile format: '{url}'",
                              "Use format: https://linkedin.com/in/username")
            else:
                self._log_pass("R18")
        
        # R17: JD URL HTTP validation
        if jd_url and not self._is_valid_url(jd_url):
            self._log_fail("R17", idx, "JD URL",
                          f"Invalid URL format: '{jd_url}'",
                          "Provide valid HTTP/HTTPS URL")
        else:
            self._log_pass("R17")
        
        # R20: Versioned Resume filename validation
        versioned_resume = row.get("Versioned Resume", "").strip()
        if versioned_resume:
            # Makes the file extension group optional: (\.(pdf|docx|doc))?
            filename_pattern = r'^[A-Za-z0-9_\-]+(\.(pdf|docx|doc))?$'
            if not re.match(filename_pattern, versioned_resume):
                self._log_fail("R20", idx, "Versioned Resume",
                              f"Invalid filename format: '{versioned_resume}'",
                              "Use format: CompanyName_JobTitle_v1")
            else:
                self._log_pass("R20")
        
        # R21: Company name sanity
        company = row.get("Company", "").strip()
        if company and len(company) < 2:
            self._log_fail("R21", idx, "Company",
                          "Company name too short",
                          "Provide valid company name (2+ chars)")
        else:
            self._log_pass("R21")
        
        # R22: Job Title sanity
        job_title = row.get("Job Title", "").strip()
        if job_title and len(job_title) < 3:
            self._log_fail("R22", idx, "Job Title",
                          "Job title too short",
                          "Provide valid job title (3+ chars)")
        else:
            self._log_pass("R22")
    
    def _validate_channel_gating(self, idx: int, row: Dict, channel: str):
        """Validate R5a-R5d channel gating requirements."""
        
        if channel == "Recruiter Outreach":
            # R5a: Hiring Recruiter fields required
            recruiter = row.get("Hiring Recruiter", "").strip()
            recruiter_url = row.get("Hiring Recruiter URL", "").strip()
            if not recruiter or not recruiter_url:
                self._log_fail("R5a", idx, "Hiring Recruiter",
                              "Recruiter name and URL required for Recruiter Outreach",
                              "Provide recruiter details")
            else:
                self._log_pass("R5a")
        
        elif channel == "Contact Outreach":
            # R5b: At least one contact required
            has_contact = False
            for i in range(1, 6):
                name = row.get(f"Recruiter / Contact {i} Name", "").strip()
                if name:
                    has_contact = True
                    break
            if not has_contact:
                self._log_fail("R5b", idx, "Recruiter / Contact",
                              "At least one contact required for Contact Outreach",
                              "Add contact details")
            else:
                self._log_pass("R5b")
        
        elif channel == "Blended Outreach":
            # R5c: Both recruiter and contact required
            recruiter = row.get("Hiring Recruiter", "").strip()
            has_contact = any(row.get(f"Recruiter / Contact {i} Name", "").strip() 
                            for i in range(1, 6))
            if not recruiter or not has_contact:
                self._log_fail("R5c", idx, "Outreach",
                              "Both recruiter and contact required for Blended Outreach",
                              "Provide both recruiter and contact details")
            else:
                self._log_pass("R5c")
        
        elif channel == "No Outreach":
            # R5d: No recruiter or contact should be present
            recruiter = row.get("Hiring Recruiter", "").strip()
            has_contact = any(row.get(f"Recruiter / Contact {i} Name", "").strip() 
                            for i in range(1, 6))
            if recruiter or has_contact:
                self._log_fail("R5d", idx, "Outreach",
                              "No recruiter/contact allowed for No Outreach",
                              "Clear recruiter and contact fields")
            else:
                self._log_pass("R5d")
    
    def _generate_passed_outcome(self, tracker_rows: List[Dict]) -> Dict:
        """Generate PASSED JSON outcome."""
        # Count by status and channel
        status_counts = {}
        channel_counts = {}
        
        for row in tracker_rows:
            status = row.get("Pipeline Status", "").strip()
            channel = row.get("Outreach Channel", "").strip()
            status_counts[status] = status_counts.get(status, 0) + 1
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        return {
            "result": "PASSED",
            "counts_by_rule": self.rule_pass_counts,
            "totals_by_status": status_counts,
            "totals_by_channel": channel_counts,
            "run_sha": self.run_sha,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp
        }
    
    def _generate_blocked_outcome(self) -> Dict:
        """Generate BLOCKED JSON outcome with error table."""
        # Create failure histogram
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

COMPREHENSIVE_HYPHENATION_RULES = {
    "description": "A comprehensive suite of rules for style enforcement, including hyphenation and advanced AI text sanitization inspired by principles from leading language models.",
    "style_version": "v2.1-Comprehensive",
    "rules": {
        "unnatural_hyphens_remove": [
            {"from": "AI-powered", "to": "AI powered"},
            {"from": "PS-centric", "to": "professional services"},
            {"from": "high-velocity", "to": "high velocity"},
            {"from": "automation-first", "to": "automation"},
            {"from": "lifecycle-based", "to": "lifecycle based"}
        ],
        "natural_hyphens_preserve": [
            "best-in-class",
            "business-to-business",
            "business-to-consumer",
            "co-author",
            "co-deliver",
            "co-founder",
            "cost-effective",
            "cross-functional",
            "customer-centric",
            "cutting-edge",
            "data-driven",
            "day-to-day",
            "deep-learning",
            "end-to-end",
            "enterprise-wide",
            "forward-thinking",
            "go-to-market",
            "hands-on",
            "high-performance",
            "long-term",
            "machine-learning",
            "mission-critical",
            "multi-cloud",
            "multi-framework",
            "multi-jurisdictional",
            "multi-million",
            "multi-region",
            "multi-tenant",
            "on-premise",
            "post-sales",
            "pre-sales",
            "quarter-over-quarter",
            "real-time",
            "results-oriented",
            "self-service",
            "short-term",
            "state-of-the-art",
            "year-over-year",
            "zero-loss"
        ]
    }
}

MASTER_RESUME_JSON = {
  "schema_version": "master_resume_v2.15",
  "owner": {
    "name": "Amit Ayer",
    "headline": "Chief AI Officer | LLM Product Launches | Strategic AI Partnerships",
    "contact": {
      "phone": "+1-917-239-3830",
      "email": "amitayer1@gmail.com",
      "linkedin": "https://www.linkedin.com/in/amitayer1"
    }
  },
  "professional_experience": [
    {
      "company": "Unify Consulting",
      "location": "Boca Raton, FL",
      "title": "Chief AI Officer",
      "dates": {
        "start": "February 2023",
        "end": "Present"
      },
      "overview": "Led enterprise generative AI and LLM solution delivery for Fortune 500 financial services clients, scaling senior ML engineering teams and accelerating production deployment timelines by 40% across regulated client programs.",
      "bullet_pool": [
        "Designed and deployed context-engineering frameworks with retrieval-augmented pipelines on unified analytics platforms and semantic caching, improving generative AI accuracy by 33% while accelerating customer solution adoption across multiple Fortune 500 portfolio companies.",
        "Architected LLM deployment pipelines with embedding stores, vector databases on cloud infrastructure, and inference optimization techniques, cutting latency by 38% and improving model throughput to meet production SLAs for regulated financial workloads.",
        "Deployed agentic API frameworks using chain-of-thought prompting to automate complex workflows, reducing manual intervention in reporting and operations by 28% while improving audit traceability for regulatory compliance requirements across Fortune 500 clients.",
        "Built senior engineering teams focused on transformer models and attention mechanisms, delivering low-latency inference optimization on cloud infrastructure and reducing fraud detection response times by 42% across client production deployments.",
        "Recruited and scaled senior LLM and ML engineering practice from 5 to 18 members, delivering enterprise AI adoption for Fortune 500 financial clients and accelerating time-to-production by 37% across regulated programs.",
        "Built and mentored 12-person professional services AI team, equipping delivery leads with production-grade LLM tools and code accelerators that reduced development sprint cycles by 27% and improved overall project delivery velocity.",
        "Led multi-year strategic partnerships with leading AWS to co-develop platforms and go-to-market programs that scaled enterprise generative AI adoption, secured $18M in partnership revenue, and expanded professional services reach globally.",
        "Partnered with C-suite executives to align AI strategy with business outcomes, co-developing generative AI products using cloud platforms that generated $32M in measurable client value and operational transformation initiatives across portfolio companies.",
        "Drove strategic alliances with AWS and Snowflake to co-develop generative AI solutions, launching 8 client-specific pilots worth $17M in pipeline value and accelerating professional services onboarding across portfolio companies.",
        "Accelerated professional services onboarding with automated LLM-powered discovery and RAG pipelines on unified analytics platforms, reducing client intake times by 43% and launching enterprise projects faster with standardized AI delivery frameworks.",
        "Standardized professional services delivery using modular AI architectures and retrieval-augmented generation systems, cutting consultant ramp-up by 32 days and raising client consistency scores to 91% across all engagements.",
        "Automated repetitive professional services tasks with transformer-based large language models and intelligent workflow orchestration on cloud platforms, reducing overall delivery costs by 22% while maintaining enterprise-grade quality standards across all engagements.",
        "Automated compliance and risk validation using policy-as-code and transformer-based LLM validators embedded in professional services workflows, cutting regulatory remediation cycles by 37% and accelerating audit timelines for global clients.",
        "Enabled measurable business outcomes by embedding AI-powered analytics and intelligent chatbot support into client engagements, raising renewal rates by 23% and strengthening long-term partnership relationships across Fortune 500 portfolio companies."
      ]
    },
    {
      "company": "IBM",
      "location": "New York, NY",
      "title": "Lead Client Partner",
      "dates": {
        "start": "April 2017",
        "end": "October 2022"
      },
      "overview": "Directed global digital transformation programs across financial institutions, modernizing legacy risk systems and reducing regulatory reporting cycles by 50% through cloud analytics migrations.",
      "bullet_pool": [
        "Integrated AI decision engines into risk platforms enabling real-time CCAR and Basel III regulatory reporting, raising client renewal rates by 24% across Fortune 500 financial accounts.",
        "Launched machine learning risk analytics platform on cloud infrastructure serving global markets, improving predictive accuracy by 17% while ensuring compliance with international regulatory frameworks including MiFID II.",
        "Led multi-region regulatory modernization projects across EMEA and APAC, deploying NLP fraud analytics on cloud platforms that reduced false positives by 29% and improved audit transparency for global clients.",
        "Introduced AI-infused reporting and compliance automation frameworks, improving regulatory response times by 53% and supporting scalable client transformation programs across financial services portfolios globally.",
        "Delivered $34M transformation by migrating legacy risk systems to AWS analytics platforms, cutting regulatory response times by 48% for Fortune 500 banking clients.",
        "Migrated large-scale Monte Carlo risk models to cloud HPC infrastructure, accelerating execution cycles by 43% and reducing annual compute costs by $4.2M for global financial institutions.",
        "Oversaw global migrations of on-premise risk models to cloud infrastructure, enabling real-time analytics capabilities and saving $3.8M in annual infrastructure costs for Fortune 500 financial institutions.",
        "Established strategic alliances with leading cloud and data platform providers and systems integrators to co-deliver enterprise solutions, generating $16M in incremental partnership revenue across 32 global markets.",
        "Partnered with cloud providers and top systems integrators to co-deliver complex AI transformation programs, unlocking $14M in incremental revenue and expanding professional services reach globally.",
        "Enabled recurring client engagements by launching managed AI services on AWS for insurance and capital markets sectors, increasing client renewal rates by 26% and driving recurring revenue growth.",
        "Implemented NLP-based fraud analytics on cloud platforms across multi-jurisdictional operations to reduce false positives by 32%, improving detection precision and accelerating investigation timelines for global banking clients.",
        "Delivered CI/CD pipelines with embedded security scanning on cloud infrastructure, reducing production incidents by 36% and accelerating AI feature releases by 52% globally for Fortune 500 clients.",
        "Standardized professional services workflows by embedding automated risk controls and AI governance frameworks, reducing delivery timelines by 47% and securing global executive sign-off across all transformation programs.",
        "Developed data pipelines with standardized delivery playbooks on unified analytics platforms, accelerating feature launches by 49% while maintaining audit trail and compliance standards globally for Fortune 500 clients."
      ]
    },
    {
      "company": "TraderSense (Early-Stage / Stealth)",
      "location": "New York, NY",
      "title": "Chief Technology Officer",
      "dates": {
        "start": "April 2014",
        "end": "March 2017"
      },
      "overview": "As co-founder and CTO, led all technology strategy, product development, and team management from concept to initial launch.",
      "highlights": [
        "Architected the company's proprietary automated trading platform, designed to analyze market data and execute high-speed algorithmic trades.",
        "Led the 6-person engineering team, secured key data and brokerage partnerships, and launched the beta product to early adopter customers."
      ]
    },
    {
      "company": "Ernst & Young",
      "location": "New York, NY",
      "title": "Principal",
      "dates": {
        "start": "October 2009",
        "end": "March 2014"
      },
      "overview": "Managed an 18-person enterprise risk team that provided strategic guidance to financial institutions on capital adequacy and regulatory modeling.",
      "highlights": [
        "Directed $16M stress testing transformation for Tier 1 banks, advising CROs on CCAR methodology and automated reporting that reduced Federal Reserve examination findings by 38%.",
        "Advised insurance boards and audit committees on Solvency II implementation, designing economic capital models and loss reserving methodologies that reduced statutory provisions by 19%."
      ]
    },
    {
      "company": "Early Career Roles",
      "location": "Philadelphia, PA",
      "title": "Actuarial Consultant and Quantitative Roles",
      "dates": {
        "start": "October 2002",
        "end": "September 2009"
      },
      "overview": "Advanced from actuarial analyst to senior consultant, building expertise across insurance and derivatives valuation that provided the quantitative and computational foundation for a career in technology.",
      "highlights": [
        "Designed stochastic pricing models for variable annuities and path-dependent options while developing distributed computing systems on grid clusters to execute large-scale valuations for financial reporting."
      ]
    }
  ],
  "education": [
    {
      "degree": "Master of Science in Biostatistics",
      "institution": "Columbia University",
      "notes": "Graduated with Distinction"
    },
    {
      "degree": "Bachelor of Arts in Biology",
      "institution": "Brown University",
      "notes": "Graduated Cum Laude"
    }
  ],
  "certifications_and_credentials": [
    "Certified Machine Learning Engineer – Associate, AWS (2025)",
    "Databricks Lakehouse Fundamentals Accreditation (2023)",
    "Certified Solutions Architect – Professional, AWS (2022)",
    "Fellow of the Society of Actuaries (2010)"
  ],
  "strategic_and_technical_competencies": [
    "• **Enterprise AI Platform Architecture:** Designed multi-cloud AI platforms on leading cloud and analytics infrastructures for financial services driving regulatory compliance, operational efficiency, and 42% performance improvements across organizations.",
    "• **AI Governance & Risk Management:** Established enterprise governance and bias audit frameworks enabling audit-ready AI model launches while reducing compliance risk by 36% and accelerating regulatory approval cycles for clients.",
    "• **Production System Scalability & Reliability:** Built scalable AI systems on cloud infrastructure processing millions of daily transactions with 99.9% uptime, deploying containerized microservices and implementing enterprise-grade reliability standards.",
    "• **Executive Leadership & Strategic Transformation:** Unified senior technical, commercial, and risk leaders to drive enterprise-wide technology programs delivering $50M+ in value and business transformation results across regulated industries.",
    "• **Strategic Partnership & Alliance Development:** Forged alliances with cloud, data platform, and systems integration providers to expand market reach, co-develop solutions, and accelerate adoption across portfolio companies.",
    "• **AI-Driven Operational Excellence & Innovation:** Embedded automation and intelligent systems into operational models cutting delivery costs by 37% and improving transformation outcomes through technology adoption."
  ]
}

# Define BulletProvenance Enum here if not imported elsewhere
class BulletProvenance(Enum):
    Verbatim = "Verbatim"
    Customized = "Customized"
    Synthetic = "Synthetic"

class RAGConfig:

    # API settings
    model: str = "gemini-2.5-pro"
    max_tokens: int = 30000 # Increased from 4000
    temperature: float = 0.7

    # ... rest of RAGConfig remains the same ...
    
    # Search targetscd
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
    
    # NEW: Phase-level settings
    phase_max_retries: int = 3                   # Retries per phase
    phase_timeout_seconds: int = 60              # Timeout per phase
    
    # NEW: Circuit breaker
    circuit_breaker_threshold: int = 5           # Failures before open
    circuit_breaker_timeout: int = 60            # Seconds before retry
    
    # Caching
    cache_dir: str = "/tmp/jd_cache"
    cache_ttl_days: int = 30
    
    # NEW: Telemetry
    telemetry_enabled: bool = True
    telemetry_log_dir: str = "/tmp/rag_telemetry"

    # v8.10: Weighted Synthesis (Approach 4)
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
    # v8.10 (Approach 4): Add specific source identifier
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

class ResumeSection(Enum):
    K0_NAME = "K.0_Name"
    K0_HEADLINE = "K.0_Headline"
    K0_CONTACT = "K.0_Contact"
    K1_EXECUTIVE_SUMMARY = "K.1_Executive_Summary"
    K5_UNIFY_BULLETS = "K.5_Unify_Bullets"
    K5_UNIFY_OVERVIEW = "K.5_Unify_Overview"
    K6_IBM_BULLETS = "K.6_IBM_Bullets"
    K6_IBM_OVERVIEW = "K.6_IBM_Overview"
    K7_TRADERSENSE_BULLETS = "K.7_TraderSense_Bullets"
    K7_TRADERSENSE_OVERVIEW = "K.7_TraderSense_Overview"
    K8_EY_BULLETS = "K.8_EY_Bullets"
    K8_EY_OVERVIEW = "K.8_EY_Overview"
    K9_EARLY_CAREER_BULLETS = "K.9_Early_Career_Bullets"
    K9_EARLY_CAREER_OVERVIEW = "K.9_Early_Career_Overview"
    K10_COMPETENCIES = "K.10_Competencies"
    K11_EDUCATION = "K.11_Education"
    K12_CERTIFICATIONS = "K.12_Certifications"
    K2_SKILLS = "K.2_Skills"
    K13_COVER_LETTER = "K.13_Cover_Letter"
    K0_EXECUTIVE_SUMMARY_HEADER = "K.0_Executive_Summary_Header"
    K0_EXPERIENCE_HEADER = "K.0_Experience_Header"
    K0_EDUCATION_HEADER = "K.0_Education_Header"
    K0_CERTIFICATIONS_HEADER = "K.0_Certifications_Header"
    K0_COMPETENCIES_HEADER = "K.0_Competencies_Header"

from typing import Callable, TypeVar
import signal

T = TypeVar('T')

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
        import logging
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
                "phase4": { # v8.10: Approach 3
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
    
# Inside class GeminiWebSearchClient:
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
    
    def search_and_analyze(
        self, 
        prompt: str, 
        phase_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Send prompt to Gemini with web_search tool enabled.
        Enhanced with adaptive retry, circuit breaker, and JSON repair.
        
        Returns: Parsed JSON from Gemini's response.
        Raises: APIError, CircuitBreakerOpenError, TimeoutError, ValueError
        """
        import logging
        import random
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {phase_name}...")
        
        last_exception = None
        
        for attempt in range(self.config.api_max_retries):
            try:
                # Check circuit breaker
                result = self.circuit_breaker.call(
                    self._make_api_call,
                    prompt,
                    attempt,
                    phase_name,
                    logger
                )
                
                logger.info(f"{phase_name} completed successfully on attempt {attempt+1}")
                return result
                
            except CircuitBreakerOpenError as e:
                logger.error(f"{phase_name}: Circuit breaker OPEN - aborting retries")
                raise
                
            except Exception as e: # Broad exception for Gemini API
                last_exception = e
                logger.warning(
                    f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} "
                    f"failed: {type(e).__name__}: {e}"
                )
                
                if attempt < self.config.api_max_retries - 1:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: All {self.config.api_max_retries} API attempts failed")
                    raise
            
            except ValueError as e:
                # JSON parsing error - try repair
                last_exception = e
                logger.warning(f"{phase_name} JSON parsing failed (attempt {attempt+1}): {e}")
                
                if attempt < self.config.api_max_retries - 1:
                    # Retry with explicit JSON format instruction
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Retrying with enhanced JSON prompt after {backoff:.2f}s...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: JSON parsing failed after all attempts")
                    raise
        
        # Should never reach here, but handle gracefully
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{phase_name}: Unexpected exit from retry loop")
    
# Inside class GeminiWebSearchClient:
# Inside class GeminiWebSearchClient:
    def _make_api_call(
        self,
        prompt: str,
        attempt: int,
        phase_name: str,
        logger
    ) -> Dict[str, Any]:
        """
        Make the actual API call with timeout and robust response handling.
        v11.30 Fix: Removed 'tools', Uses integer codes for finish_reason.
        """
        start_time = time.time()

        if not self.client:
            raise HopExecutionError(f"{phase_name} cannot make API call: Gemini client not initialized.")

        try:
            # Call generate_content (tools parameter removed)
            response = self.client.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens, # Uses RAGConfig value (e.g., 8192)
                    temperature=self.config.temperature
                )
            )

            elapsed = time.time() - start_time
            logger.debug(f"{phase_name} API call completed in {elapsed:.2f}s")

            # --- Robust Response Handling (Check finish_reason using integers) ---
            json_text_content = ""
            finish_reason = None
            prompt_feedback = getattr(response, 'prompt_feedback', None)

            # --- START FIX: Check finish_reason using integers ONLY ---
            # Access finish_reason from the candidate if available
            # Use safe attribute access with getattr
            if hasattr(response, 'candidates') and response.candidates:
                 # Ensure candidates[0] exists and access finish_reason safely
                 candidate_one = response.candidates[0]
                 finish_reason = getattr(candidate_one, 'finish_reason', None) # Use getattr here

            # Handle MAX_TOKENS (integer 2) or other blocking reasons immediately
            if finish_reason == 2: # MAX_TOKENS
                 # Raise a specific error for MAX_TOKENS
                 raise HopExecutionError(f"API call stopped due to MAX_TOKENS limit ({self.config.max_tokens}). Response may be incomplete.")
            elif finish_reason is not None and finish_reason != 1: # Check for non-STOP (integer 1) reasons
                 # Get block reason if available
                 block_reason = getattr(prompt_feedback, 'block_reason', None) if prompt_feedback else None
                 # Raise a specific error for other non-STOP reasons
                 raise HopExecutionError(f"API call stopped. Finish Reason Code: {finish_reason}. Block Reason: {block_reason}")
            # --- END FIX ---


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
            return self._extract_json(json_text_content)
            # --- End Robust Response Handling ---

        # --- Exception Handling (Catch specific errors first) ---
        except HopExecutionError as he: # Catch specific MAX_TOKENS or blocked errors from above
             logger.warning(f"{phase_name} API call failed (Attempt {attempt+1}): {he}")
             raise # Re-raise to be caught by retry logic

        except (TimeoutError, Exception) as e: # Catch other errors like timeouts or ValueErrors from parsing
            elapsed = time.time() - start_time
            if isinstance(e, TimeoutError) or "timeout" in str(e).lower():
                 logger.warning(f"{phase_name} API call timed out after {elapsed:.2f}s (Attempt {attempt+1})")
                 # Re-raise as TimeoutError for retry logic
                 raise TimeoutError(f"{phase_name} timed out") from e
            else:
                 # Log other unexpected errors (e.g., ValueError from _extract_json)
                 logger.warning(f"{phase_name} API call failed (Attempt {attempt+1}): {type(e).__name__}: {e}", exc_info=False)
                 # Re-raise the original exception for the retry logic
                 raise
                                 
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

    def phase1_thematic_research(self, job_description: str, mission: RAGMission) -> Dict[str, Any]:
        """
        Phase 1: Research market expectations and extract themes.
        v5.59: Enhanced with retry logic and simplified fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        v11.30 Fix: Pass mission to prompt builders correctly.
        """
        def main_phase1():
            # --- Pass mission ---
            prompt = self._build_phase1_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 1: Thematic Research")

        def fallback_phase1():
            # --- Pass mission ---
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

        # --- START FIX: Safely access key_technologies[0] ---
        # Only add the tech-specific search if key_technologies is not empty
        tech_search_line = ""
        if mission.key_technologies:
            safe_tech = mission.key_technologies[0] # Safely access after check
            tech_search_line = f'3. Search for: `"{mission.target_company_name} press release {safe_tech}"`'
        # --- END FIX ---

        # (Approach 2) Add authoritative source queries
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
            # --- Pass mission ---
            prompt = self._build_phase2_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 2: Authenticity Patterns")

        def fallback_phase2():
            # --- Pass mission ---
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
        # Use role_title from mission
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
            # Pass mission to the prompt builder
            prompt = self._build_phase3_prompt(job_description, mission, detailed=True)
            return self.client.search_and_analyze(
                prompt,
                "Phase 3: Competitive Positioning"
            )

        def fallback_phase3():
            # Pass mission to the prompt builder
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
        # Extract company/role from mission
        company_name = mission.target_company_name
        role_title = mission.precise_role_title
        industry = self._infer_industry(job_description)

        peer_companies = self._infer_peer_companies(company_name, job_description)

        # Integrate new competitive analysis config
        search_pattern_instruction = self.comp_config.search_pattern.format(
            role_title=role_title, peer_company="<peer_company>"
        )
        selection_criteria_instruction = ", ".join(self.comp_config.selection_criteria)

        # (Approach 2) Add authoritative source queries
        authoritative_searches = f"""
**Authoritative Search Directives (High Priority):**
1. Search for: `"Gartner Magic Quadrant for {industry}"`
2. Search for: `"Forrester Wave {industry}"`
"""

        # Simplified fallback logic based on 'detailed' flag
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
        industry = self._infer_industry(job_description)

        peers_by_industry = {
            "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
            "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
            "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
            "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
            "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"]
        }

        peers = peers_by_industry.get(industry, peers_by_industry["Technology"])
        return [p for p in peers if p.lower() not in company_name.lower()][:5]

    def phase4_narrative_mining(self, mission: RAGMission) -> Dict[str, Any]:
        """
        Phase 4: Mine for problem-solution narratives.
        (Implements Approach 3)
        v11.30 Fix: Pass mission to prompt builders correctly.
        """
        def main_phase4():
            # --- Pass mission ---
            prompt = self._build_phase4_prompt(mission, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 4: Narrative Mining")

        def fallback_phase4():
            # --- Pass mission ---
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
    """
    HOP-0: Enhanced Job Description Parser with Resilient Web-Search Intelligence.
    
    v5.59: HARDENED RAG WITH MULTI-LAYER RESILIENCE
    - API Layer: 7 retries with adaptive backoff + jitter
    - Phase Layer: 3 retries per phase with simplified fallbacks
    - Orchestration Layer: Partial success preservation
    - Fallback Layer: 4-tier degradation hierarchy
    - Monitoring Layer: Comprehensive telemetry
    
    v5.54: WEB RAG FULLY IMPLEMENTED
    - Phase 1: Thematic Research (15-20 searches)
    - Phase 2: Authenticity Patterns (10-15 searches)
    - Phase 3: Competitive Positioning (10-15 searches)
    - Graceful fallback to v5.52 local NLP
    """
    
    def __init__(
        self, 
        master_resume: Dict, 
        enable_web_search: bool = True,
        api_key: Optional[str] = None, # Explicitly pass API key if available
        config: Optional[RAGConfig] = None 
    ):
        self.master_resume = master_resume
        self.enable_web_search = enable_web_search and GEMINI_AVAILABLE
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") # Use GEMINI_API_KEY
        self.config = config or RAGConfig()
        self.rag_mission: Optional[RAGMission] = None
        self.search_calls_made = 0
        
        # Initialize telemetry if enabled
        if self.config.telemetry_enabled:
            self.telemetry_logger = TelemetryLogger(self.config.telemetry_log_dir)
        else:
            self.telemetry_logger = None
        
        # Common stopwords
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'we', 'you', 'your', 'our', 'this',
            'these', 'those', 'or', 'but', 'not', 'have', 'had', 'do', 'does',
            'can', 'should', 'would', 'could', 'must', 'may', 'might', 'been',
            'being', 'about', 'through', 'their', 'there', 'where', 'which',
            'who', 'whom', 'when', 'why', 'how', 'all', 'each', 'other', 'such'
        }
        
        # Domain themes
        self.domain_themes = {
            'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
                     'neural network', 'llm', 'generative ai', 'nlp', 'computer vision',
                     'data science', 'predictive', 'algorithms'],
            'Cloud': ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'infrastructure',
                     'devops', 'microservices', 'scalability', 'distributed'],
            'Leadership': ['lead', 'leadership', 'manage', 'director', 'executive', 'vp',
                          'chief', 'head', 'team', 'strategy', 'vision', 'roadmap'],
            'Product': ['product', 'development', 'innovation', 'design', 'features',
                       'roadmap', 'user experience', 'ux', 'agile', 'scrum'],
            # ADDED PER RCA (Option 1.1)
            'Customer_Success': ['customer success', 'post-sales', 'adoption', 'retention', 'renewal', 'customer health', 'value realization', 'technical success'],
            'Sales_GTM': ['sales', 'go-to-market', 'gtm', 'revenue', 'quota', 'pre-sales', 'solution engineering'],
            'Engineering_IC': ['engineer', 'software engineer', 'ic', 'developer', 'hands-on'],

            'Enterprise': ['enterprise', 'b2b', 'saas', 'platform', 'solution', 'architecture',
                          'integration', 'api', 'deployment', 'implementation'],
            'Business': ['revenue', 'growth', 'sales', 'p&l', 'roi', 'kpi', 'metrics',
                        'business', 'commercial', 'financial', 'budget'],
            'Data': ['data', 'analytics', 'database', 'sql', 'warehouse', 'pipeline',
                    'etl', 'big data', 'reporting', 'visualization']
        }
        
        # Initialize web RAG components if enabled
        if self.enable_web_search: # Check only enable_web_search, API key is handled by GeminiWebSearchClient
            try:
                self.gemini_client = GeminiWebSearchClient(self.api_key, self.config)
                self.web_rag = WebSearchRAG(self.gemini_client, self.config)
                self.cache_manager = JDCacheManager(
                    self.config.cache_dir, 
                    self.config.cache_ttl_days
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Web RAG initialization failed: {e}")
                self.gemini_client = None
                self.web_rag = None
                self.cache_manager = None
        else:
            self.gemini_client = None # Corrected from self.web_client
            self.web_rag = None
            self.cache_manager = None
    
    def analyze(self, job_description: str) -> "'ThematicAnalysis'":  # Forward reference
        """
        Analyze job description with resilient web-search intelligence.
        v5.59: Enhanced with 4-tier fallback hierarchy and telemetry.
        
        Fallback Hierarchy:
        1. Full web RAG (all 3 phases)
        2. Partial web RAG (any successful phases)
        3. Hybrid (web RAG phases + local NLP fill-in)
        4. Local NLP only
        """
        # HOP -0.5: Pre-RAG Differential Analysis (Approach 1)
        try:
            self.rag_mission = self._execute_pre_rag_analysis(job_description)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Pre-RAG analysis (HOP -0.5) failed: {e}. Proceeding with standard RAG.")
            # Create a fallback mission
            self.rag_mission = RAGMission(
                target_company_name=self._extract_company_name(job_description),
                precise_role_title=self._extract_role_from_jd(job_description),
                key_technologies=[], core_responsibilities=[],
                signal_gap_keywords=[], signal_overlap_keywords=[]
            )

        if not self.enable_web_search:
            return self._analyze_local_nlp(job_description)
        
        # New Design: Re-raise any exception to halt the workflow. No fallback.
        try:
            return self._analyze_with_resilient_web_search(job_description)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"FATAL: Web RAG analysis failed at HOP-0: {e}. Halting workflow.")
            raise # Re-raise the exception to enforce fail-fast.

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
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Executing HOP -0.5: Pre-RAG Differential Analysis...")

        prompt = self._build_pre_rag_analysis_prompt(job_description)
        # Use the existing client but with a more constrained call for speed and cost.
        analysis_json = self.gemini_client.search_and_analyze(prompt, "Pre-RAG Analysis")

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
    
# Inside class EnhancedJobDescriptionAnalyzer:
    def _analyze_with_resilient_web_search(
        self,
        job_description: str
    ) -> 'ThematicAnalysis':
        """
        v11.60 Final Fix: Added JSON roundtrip conversion before synthesis & caching.
        """
        import logging
        logger = logging.getLogger(__name__)

        # --- Imports needed for conversion ---
        import json
        from collections.abc import Mapping, Sequence
        from dataclasses import is_dataclass, asdict
        # --- End imports ---

        telemetry = RAGTelemetry() if self.telemetry_logger else None
        start_time = time.time()
        
        if self.cache_manager:
            cached = self.cache_manager.get(job_description)
            if cached:
                logger.info("Using cached web RAG analysis")
                return self._dict_to_thematic_analysis(cached)
        
        if not self.web_rag or not self.rag_mission:
             logger.warning("Web RAG or RAG Mission not available. Falling back to local NLP.")
             return self._analyze_local_nlp(job_description)


        partial_result = PartialRAGResult()

        # --- Phase 1: Thematic Research ---
        phase1_start = time.time()
        try:
            logger.info("=== Starting Phase 1: Thematic Research ===")
            phase1_results = self.web_rag.phase1_thematic_research(job_description, self.rag_mission)
            partial_result.phase1_result = phase1_results
            partial_result.phase1_success = True
            search_summary_p1 = phase1_results.get("search_summary", {})
            searches_performed_p1 = search_summary_p1.get("searches_performed", 0)
            self.search_calls_made += searches_performed_p1
            if telemetry:
                telemetry.phase1_success = True
                telemetry.phase1_attempts = 1
                telemetry.total_search_calls += searches_performed_p1
            logger.info(f"Phase 1: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 1: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 1: {type(e).__name__}")
            if telemetry:
                telemetry.phase1_success = False
                telemetry.errors.append(f"Phase 1: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase1_duration_seconds = time.time() - phase1_start

        # --- Phase 2: Authenticity Patterns ---
        phase2_start = time.time()
        try:
            logger.info("=== Starting Phase 2: Authenticity Patterns ===")
            phase2_results = self.web_rag.phase2_authenticity_patterns(job_description, self.rag_mission)
            partial_result.phase2_result = phase2_results
            partial_result.phase2_success = True
            search_summary_p2 = phase2_results.get("search_summary", {})
            profiles_analyzed_p2 = search_summary_p2.get("profiles_analyzed", 0)
            self.search_calls_made += profiles_analyzed_p2
            if telemetry:
                telemetry.phase2_success = True
                telemetry.phase2_attempts = 1
                telemetry.total_search_calls += profiles_analyzed_p2
            logger.info(f"Phase 2: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 2: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 2: {type(e).__name__}")
            if telemetry:
                telemetry.phase2_success = False
                telemetry.errors.append(f"Phase 2: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase2_duration_seconds = time.time() - phase2_start

        # --- Phase 3: Competitive Positioning ---
        phase3_start = time.time()
        try:
            logger.info("=== Starting Phase 3: Competitive Positioning ===")
            phase3_results = self.web_rag.phase3_competitive_positioning(job_description, self.rag_mission)
            partial_result.phase3_result = phase3_results
            partial_result.phase3_success = True
            search_summary_p3 = phase3_results.get("search_summary", {})
            peer_jds_analyzed_p3 = search_summary_p3.get("peer_jds_analyzed", 0)
            self.search_calls_made += peer_jds_analyzed_p3
            if telemetry:
                telemetry.phase3_success = True
                telemetry.phase3_attempts = 1
                telemetry.total_search_calls += peer_jds_analyzed_p3
            logger.info(f"Phase 3: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 3: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 3: {type(e).__name__}")
            if telemetry:
                telemetry.phase3_success = False
                telemetry.errors.append(f"Phase 3: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase3_duration_seconds = time.time() - phase3_start

        # --- Phase 4: Problem-Solution Narrative Mining ---
        phase4_start = time.time()
        try:
            logger.info("=== Starting Phase 4: Narrative Mining ===")
            phase4_results = self.web_rag.phase4_narrative_mining(self.rag_mission)
            partial_result.phase4_result = phase4_results
            partial_result.phase4_success = True
            search_summary_p4 = phase4_results.get("search_summary", {})
            searches_performed_p4 = search_summary_p4.get("searches_performed", 0)
            self.search_calls_made += searches_performed_p4
            if telemetry:
                telemetry.phase4_success = True
                telemetry.phase4_attempts = 1
                telemetry.total_search_calls += searches_performed_p4
            logger.info(f"Phase 4: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 4: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 4: {type(e).__name__}")
            if telemetry:
                telemetry.phase4_success = False
                telemetry.errors.append(f"Phase 4: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase4_duration_seconds = time.time() - phase4_start


        # --- Evaluation Logic ---
        logger.info(
            f"RAG Phases Complete: "
            f"Success Rate = {partial_result.success_rate:.1%} "
            f"({partial_result.phase1_success}, {partial_result.phase2_success}, "
            f"{partial_result.phase3_success}, {partial_result.phase4_success})"
        )

        analysis = None # Initialize analysis variable

        if partial_result.full_success:
            logger.info("✓ Strategy 1: Full 4-phase RAG successful")

            # --- START JSON Roundtrip Conversion ---
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
            # --- END JSON Roundtrip Conversion ---

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

        # --- Caching Logic (with robust conversion) ---
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
        # --- End Caching Logic ---


        # --- Telemetry Logging ---
        if telemetry and self.telemetry_logger:
            telemetry.total_duration_seconds = time.time() - start_time
            telemetry.circuit_breaker_triggered = self.gemini_client.circuit_breaker.state == CircuitState.OPEN
            telemetry.failed_api_calls = self.gemini_client.circuit_breaker.failure_count
            telemetry.total_api_calls = self.search_calls_made
            self.telemetry_logger.log(telemetry)

        logger.info(f"Analysis complete. Total searches: {self.search_calls_made}")
        return analysis
    
    def _extract_role_from_jd(self, job_description: str) -> str:
        """Extract role title from JD for fallback scenarios."""
        lines = job_description.split('\n')
        if lines:
            # First line often contains role title
            return lines[0].strip()[:100]
        return "Professional"

# Inside class EnhancedJobDescriptionAnalyzer:
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

        # --- START FINAL FIX: Manual Reconstruction of Dicts ---
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
            if hasattr(item, 'items') and callable(getattr(item, 'items')): # Check if dict-like FIRST
                # logger.debug(f"  Nested: Reconstructing dict-like: {type(item)}")
                return {k: _manual_reconstruct_nested(v) for k, v in item.items()}
            elif isinstance(item, dict): # Handle actual dicts
                 # logger.debug(f"  Nested: Processing dict: {type(item)}")
                 return {k: _manual_reconstruct_nested(v) for k, v in item.items()}
            elif isinstance(item, list):
                # logger.debug(f"  Nested: Processing list: {type(item)}")
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

        # --- Add detailed check specifically for the failing structure ---
        p1_themes_check = phase1_dict.get("thematic_analysis", {})
        if not isinstance(p1_themes_check, dict):
            logger.error(f"Reconstruction failed: p1_themes_check is type {type(p1_themes_check)}")
        p1_primary_check = p1_themes_check.get("primary_theme", {})
        if not isinstance(p1_primary_check, dict):
             logger.error(f"Reconstruction failed: p1_primary_check is type {type(p1_primary_check)}")
             raise AttributeError("Manual reconstruction failed to produce a dictionary for p1_primary.")
        logger.debug(f"Manual reconstruction checks passed for p1_primary (Type: {type(p1_primary_check)}).")
        # --- END FINAL FIX ---


        # --- Keyword Aggregation and Weighted Scoring (Use *_dict variables) ---
        keyword_scores = {}
        weights = self.config.source_weights

        # Phase 1: Thematic
        p1_themes = phase1_dict.get("thematic_analysis", {})
        p1_primary = p1_themes.get("primary_theme", {}) # Should be a dict now
        p1_secondary = p1_themes.get("secondary_themes", [])
        p1_trending = p1_themes.get("trending_keywords", [])

        # Ensure keywords are strings before adding
        # This is the line that was failing before
        for kw in p1_primary.get("keywords", []):
            if isinstance(kw, str):
                keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_COMPANY_BLOG", 1.5)

        # --- Rest of the synthesis logic ---
        # (Ensure all .get() calls have defaults and type checks if needed)

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
        # --- Handle competitive_intelligence ---
        comp_intel_data = data.get("competitive_intelligence")
        comp_intel = None # Initialize to None

        # Check if comp_intel_data is a dict and try to reconstruct
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
            # If key is missing or data is not a dict, create a default empty object
            if "competitive_intelligence" not in data:
                 logging.warning("Cached data missing 'competitive_intelligence' key. Initializing default.")
            else:
                 logging.warning(f"Cached 'competitive_intelligence' data is not a dict (Type: {type(comp_intel_data)}). Initializing default.")
            comp_intel = CompetitiveIntelligence()

        # --- Handle retrieval_sources ---
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


        # --- Construct ThematicAnalysis with fallbacks ---
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
            # Ensure 'patterns' is a dictionary, even if empty
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
            if word not in self.stopwords and len(word) >= 3:
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
        """Classify role based on keywords."""
        jd_lower = jd_text.lower()
        
        seniority = "mid"
        if any(word in jd_lower for word in ['senior', 'lead', 'principal', 'staff']):
            seniority = "senior"
        elif any(word in jd_lower for word in ['executive', 'director', 'vp', 'chief', 'head']):
            seniority = "executive"
        elif any(word in jd_lower for word in ['junior', 'entry', 'associate']):
            seniority = "entry"
        
        return {
            "seniority": seniority,
            "function": "Engineering",
            "industry_focus": "Technology"
        }
    
    def _calculate_signal_quality(self, keywords: Dict[str, int], theme_scores: Dict[str, dict]) -> float:
        """Calculate signal quality score."""
        if not theme_scores:
            return 0.5
        
        keyword_diversity = len(keywords) / 100.0
        theme_strength = max(theme_scores.values(), key=lambda x: x['score'])['score']
        
        return min(1.0, (keyword_diversity * 0.3 + theme_strength * 0.7))

# ============================================================================
# HOP-1: CLERK EXTRACTOR & HALLUCINATION DETECTION
# ============================================================================

class ClerkExtractor:
    """
    HOP-1: Extract structured data from master resume.
    Includes hallucination detection.
    """
    
    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self.hallucination_detector = HallucinationDetector()
        self._validate_master_resume_structure()
    
    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        """
        Extract and validate structured data from master resume.
        v5.36: Now creates experience_sections structure instead of flat bullet_pool.
        Returns: (extracted_data, validation_results)
        """
        validation_results = []
        
        # v5.36: Create structured experience_sections from master resume
        experience_sections = self._build_experience_sections()
        
        # Detect hallucinations on all bullets
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
        
        # --- START FIX: Use correct keys from MASTER_RESUME_JSON ---
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
        # --- END FIX ---
        
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
                    severity=ValidationSeverity.MEDIUM,
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

# ============================================================================
# HOP-2: DATA ENRICHMENT
# ============================================================================

class DataEnricher:
    """
    HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc.
    """
    
    def __init__(self):
        self.verb_canonicalizer = VerbCanonicalizer()
        self.duplicate_detector = DuplicateDetector()
    
    def enrich(
        self,
        extracted_data: Dict,
           thematic_analysis: "ThematicAnalysis",
     orchestrator=None
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        v5.65: Now stores DuplicateDetector on orchestrator for QA sections 4 & 5.
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
                # Canonicalize verbs
                canonical_verbs = self.verb_canonicalizer.canonicalize(
                    bullet.get("bullet_text", "")
                )
                bullet["canonical_verbs"] = canonical_verbs
                # Enforce FORBIDDEN_VERBS rule
                forbidden_found = self.verb_canonicalizer.check_for_forbidden_verbs(
                    bullet.get("bullet_text", "")
                )
                if forbidden_found:
                    validation_results.append(ValidationResult(
                        rule_id="FORBIDDEN_VERB_USAGE",
                        passed=False,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Bullet contains forbidden verb(s): {', '.join(forbidden_found)}",
                        details={"bullet_text": bullet.get("bullet_text", "")[:100]}
                    ))

                all_bullets.append(bullet)
        
        # Detect duplicates
        duplicates = self.duplicate_detector.find_duplicates(all_bullets)
        if duplicates:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_BULLETS",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
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

class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""
    
    CANONICAL_VERBS = {
        "led": ["led", "lead", "leading"],
        "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"],
        "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"],
        "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"],
        "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"],
        "developed": ["developed", "develop", "developing"]
    }
    
    FORBIDDEN_VERBS = [
        "pioneered", "spearheaded", "orchestrated", "architected",
        "revolutionized", "transformed"  # Too strong
    ]
    
    def canonicalize(self, text: str) -> List[str]:
        """Extract and canonicalize verbs from text."""
        canonical = []
        text_lower = text.lower()
        
        for canonical_form, variants in self.CANONICAL_VERBS.items():
            if any(variant in text_lower for variant in variants):
                canonical.append(canonical_form)
        
        return canonical

    def check_for_forbidden_verbs(self, text: str) -> List[str]:
        """Check for forbidden verbs in the text."""
        found_verbs = []
        text_lower = text.lower()
        for verb in self.FORBIDDEN_VERBS:
            # Use word boundaries to avoid matching substrings (e.g., 'arch' in 'architecture')
            if re.search(r'\b' + verb + r'\b', text_lower):
                found_verbs.append(verb)
        return found_verbs

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

    # --- START FIX: MOVED METHOD INSIDE THE CLASS ---
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

# ============================================================================
# HOP-3: ARTIST GENERATOR (LLM Calls) - STATEFUL RETRY VERSION
# ============================================================================

# ============================================================================
# HOP-3: ARTIST GENERATOR (LLM Calls) - STATEFUL RETRY VERSION
# ============================================================================
import copy # Added for deepcopy in competency generation
import re   # Added for fence removal in _call_gemini_api

class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, previous_failures: List[ValidationResult] = None):
        """Initializes the ArtistGenerator with the master resume."""
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        # previous_failures is now used ONLY for the first attempt's prompt context
        self.previous_failures = previous_failures or []
        self.constraints = ContentConstraintsConfig()
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

    # Provenance targets configuration (Unchanged)
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    # Configuration defining which method generates each section
    # V12.55: Reordered K5/K6 so bullets generate before overview
    ARTIST_GENERATION_CONFIG = [
        # Sections copied directly or using placeholders
        {"section": ResumeSection.K0_NAME, "method_name": "_copy_k0_name"},
        {"section": ResumeSection.K0_CONTACT, "method_name": "_copy_k0_contact"},
        {"section": ResumeSection.K7_TRADERSENSE_BULLETS, "method_name": "_copy_k7_tradersense_bullets"},
        {"section": ResumeSection.K7_TRADERSENSE_OVERVIEW, "method_name": "_copy_k7_tradersense_overview"},
        {"section": ResumeSection.K11_EDUCATION, "method_name": "_copy_k11_education"},
        {"section": ResumeSection.K12_CERTIFICATIONS, "method_name": "_copy_k12_certifications"},
        {"section": ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EXPERIENCE_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EDUCATION_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_CERTIFICATIONS_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_COMPETENCIES_HEADER, "method_name": "_generate_dummy_header"},
        # Sections generated by LLM (will use temperature schedules and fail fast)
        {"section": ResumeSection.K0_HEADLINE, "method_name": "_generate_k0_headline"},
        {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "method_name": "_generate_k1_executive_summary"},
        # --- START REORDERING ---
        {"section": ResumeSection.K5_UNIFY_BULLETS, "method_name": "_generate_k5_unify_bullets"}, # BULLETS FIRST
        {"section": ResumeSection.K5_UNIFY_OVERVIEW, "method_name": "_generate_k5_unify_overview"}, # THEN OVERVIEW
        {"section": ResumeSection.K6_IBM_BULLETS, "method_name": "_generate_k6_ibm_bullets"},       # BULLETS FIRST
        {"section": ResumeSection.K6_IBM_OVERVIEW, "method_name": "_generate_k6_ibm_overview"},     # THEN OVERVIEW
        # --- END REORDERING ---
        {"section": ResumeSection.K8_EY_BULLETS, "method_name": "_generate_k8_ey_bullets"},
        {"section": ResumeSection.K8_EY_OVERVIEW, "method_name": "_generate_k8_ey_overview"},
        {"section": ResumeSection.K9_EARLY_CAREER_BULLETS, "method_name": "_generate_k9_early_career_bullets"},
        {"section": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "method_name": "_generate_k9_early_career_overview"},
        {"section": ResumeSection.K10_COMPETENCIES, "method_name": "_generate_k10_competencies"},
        {"section": ResumeSection.K2_SKILLS, "method_name": "_generate_k2_skills"},
        {"section": ResumeSection.K13_COVER_LETTER, "method_name": "_generate_k13_cover_letter"},
    ]

    # --- START OVERWRITE: _call_gemini_api ---
    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> str:
        """
        Refactored Helper: Centralizes Gemini API calls.
        v12.70: Raises HopExecutionError on API failure. Explicitly removes markdown fences from text output.
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set. Cannot make API call.")
            # Configure API Key (Consider moving to __init__)
            # genai.configure(api_key=api_key) # Typically done once globally
            # Initialize model (Ideally done once in __init__)
            model = genai.GenerativeModel('gemini-2.5-pro') # Or your chosen model

            api_params = reasoning_config_to_api_params(reasoning_config)
            generation_config = api_params["generation_config"]
            sc_count = api_params.get('sc', 1)

            if temperature_override is not None:
                generation_config.temperature = temperature_override
                logging.info(f"  {section_id} API Call: Using temp: {generation_config.temperature:.1f} (Override: {temperature_override is not None})")
            else:
                 # Log the temperature that was calculated by reasoning_config_to_api_params
                 logging.info(f"  {section_id} API Call: Using temp: {generation_config.temperature:.1f} (Override: {temperature_override is not None})")


            enhanced_system = enhance_system_prompt_with_reasoning(system_prompt, reasoning_config, section_id)

            # Self-Consistency Logic
            if sc_count > 1:
                logging.info(f"  Running Self-Consistency for {section_id} ({sc_count} candidates)...")
                # Ensure high temperature for diverse SC candidates unless overridden
                if temperature_override is None: generation_config.temperature = 0.9
                generation_config.candidate_count = sc_count
                candidate_responses = []
                try:
                    # Make sure the model object is properly initialized and authenticated
                    if not model:
                        raise HopExecutionError(f"{section_id} SC API call failed: Model not initialized.")
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    if response.candidates:
                        candidate_responses = [part.text for c in response.candidates if c.content and c.content.parts for part in c.content.parts if part.text] # Keep original text including potential fences
                    if not candidate_responses:
                        # Check for blocking reasons if no candidates
                        block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                        if block_reason: raise HopExecutionError(f"{section_id} SC API call blocked: {block_reason}")
                        raise HopExecutionError(f"{section_id} SC API call returned no valid text candidates.")
                except Exception as e:
                    logging.error(f"    SC API call for {section_id} failed: {e}", exc_info=True)
                    # Include more context in the exception
                    raise HopExecutionError(f"{section_id} SC API call failed: {type(e).__name__} - {e}") from e


                # Synthesis Step
                logging.info(f"  Synthesizing {len(candidate_responses)} responses for {section_id}...")
                synthesis_prompt = f"""You are a senior editor tasked with synthesizing multiple draft responses into a single, high-quality final answer. Review the original request and the provided drafts, then produce the best possible combined response, ensuring accuracy, coherence, and adherence to all original constraints.

**ORIGINAL PROMPT (for context):**
---
{prompt}
---

**DRAFTS TO SYNTHESIZE:**
"""
                for i, res in enumerate(candidate_responses):
                    synthesis_prompt += f"\n---\n**DRAFT {i+1}:**\n{res}\n---\n" # Pass raw responses

                synthesis_prompt += "\n**FINAL SYNTHESIZED ANSWER (ensure it strictly follows original prompt constraints like word count, format, etc., and DO NOT add markdown fences like ```):**\n" # Explicitly forbid fences

                # Use a moderate temperature for synthesis
                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=generation_config.max_output_tokens)
                try:
                    # Make sure the model object is properly initialized and authenticated
                    if not model:
                         raise HopExecutionError(f"{section_id} SC synthesis failed: Model not initialized.")
                    synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)

                    # Check synthesis response for issues
                    synth_finish_reason = getattr(synthesis_response.candidates[0], 'finish_reason', None) if synthesis_response.candidates else None
                    if synth_finish_reason == 2: raise HopExecutionError(f"{section_id} SC synthesis stopped: MAX_TOKENS.")
                    elif synth_finish_reason is not None and synth_finish_reason != 1:
                         synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(synthesis_response, 'prompt_feedback') else 'Unknown'
                         raise HopExecutionError(f"{section_id} SC synthesis stopped. Finish: {synth_finish_reason}. Block: {synth_block_reason}")

                    raw_text = synthesis_response.text # Get raw text
                    if not raw_text:
                        synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', None) if hasattr(synthesis_response, 'prompt_feedback') else None
                        if synth_block_reason: raise HopExecutionError(f"{section_id} SC synthesis blocked: {synth_block_reason}")
                        else: raise HopExecutionError(f"{section_id} SC synthesis produced no text.")

                    # --- Apply Fence Stripping ---
                    cleaned_text = re.sub(r'^```[a-z]*\s*\n', '', raw_text) # Remove opening fence
                    cleaned_text = re.sub(r'\n```\s*$', '', cleaned_text)       # Remove closing fence
                    final_text = cleaned_text.strip() # Strip again after removing fences
                    # --- End Fence Stripping ---

                    return final_text
                except Exception as e:
                    logging.error(f"    SC synthesis for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC synthesis failed: {type(e).__name__} - {e}") from e

            # Single Candidate Logic
            else:
                try:
                    # Make sure the model object is properly initialized and authenticated
                    if not model:
                        raise HopExecutionError(f"{section_id} generation API call failed: Model not initialized.")
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
                    if finish_reason == 2: raise HopExecutionError(f"{section_id} generation stopped: MAX_TOKENS.")
                    elif finish_reason is not None and finish_reason != 1:
                         block_reason = getattr(response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(response, 'prompt_feedback') else 'Unknown'
                         raise HopExecutionError(f"{section_id} generation stopped. Finish: {finish_reason}. Block: {block_reason}")

                    raw_text = response.text # Get raw text
                    if not raw_text:
                         block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                         if block_reason: raise HopExecutionError(f"{section_id} generation blocked: {block_reason}")
                         else: raise HopExecutionError(f"{section_id} generation returned no text.")

                    # --- Apply Fence Stripping ---
                    cleaned_text = re.sub(r'^```[a-z]*\s*\n', '', raw_text) # Remove opening fence
                    cleaned_text = re.sub(r'\n```\s*$', '', cleaned_text)       # Remove closing fence
                    final_text = cleaned_text.strip() # Strip again after removing fences
                    # --- End Fence Stripping ---

                    return final_text
                except Exception as e:
                    logging.error(f"LLM API call for {section_id} failed: {e}", exc_info=True)
                    # Include more context in the exception
                    raise HopExecutionError(f"{section_id} generation API call failed: {type(e).__name__} - {e}") from e
        except HopExecutionError as he: # Re-raise specific errors
            raise he
        except Exception as e: # Catch other unexpected errors
            logging.error(f"Unexpected error in _call_gemini_api for {section_id}: {e}", exc_info=True)
            raise HopExecutionError(f"Unexpected error during {section_id} API call: {e}") from e
    # --- END OVERWRITE: _call_gemini_api ---

    # --- Rest of ArtistGenerator methods remain unchanged ---
    # (generate, _generate_artist_output, _copy_*, _generate_k*, etc.)
    # They will now receive unfenced text from _call_gemini_api.

    def generate(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        [REFACTORED]
        Generates *only* the specified resume sections at the specified temperatures.
        v12.50: This method no longer loops or retries. It executes one generation pass
        on the requested sections.
        """
        validation_results = []

        try:
            # Call the internal generation method, passing the new parameters
            artist_output = self._generate_artist_output(
                sections_to_generate=sections_to_generate,
                temperature_overrides=temperature_overrides
            )

            # Add a success result *only* for the sections that were attempted
            generated_keys = ", ".join(k for k in artist_output.keys() if artist_output.get(k) is not None)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_PASS", passed=True, severity=ValidationSeverity.INFO,
                message=f"Content generated successfully for: {generated_keys}"
            ))
            return artist_output, validation_results

        except HopExecutionError as he: # Catch specific halt errors from generation
            logging.error(f"Artist generation HALTED during selective run: {he}", exc_info=False)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_HALTED", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation halted: {str(he)}",
                details={"error": str(he)}
            ))
            return {}, validation_results # Return empty dict, but include the critical error

        except Exception as e: # Catch other unexpected errors
            logging.error(f"Artist generation failed unexpectedly during selective run: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed unexpectedly: {str(e)}",
                details={"error": str(e)}
            ))
            return {}, validation_results

    def _generate_artist_output(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
        ) -> Dict:
        """
        [REFACTORED V12.55]
        Generates *only* the specified sections. Raises HopExecutionError on failure.
        Passes current output dict to overview generators that synthesize bullets.
        """
        output = {} # This dictionary accumulates results during the generation pass

        for config in self.ARTIST_GENERATION_CONFIG:
            section_enum = config["section"]
            method_name = config["method_name"]

            # --- Check if this section should be generated ---
            if section_enum not in sections_to_generate:
                # If it's a copy/dummy method, run it anyway (they are idempotent)
                if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                     try:
                         method = getattr(self, method_name)
                         # Store result directly in the final output dict for this pass
                         output[section_enum.value] = method()
                     except Exception as e:
                         raise HopExecutionError(f"Unexpected error in {method_name} for {section_enum.value}: {e}") from e
                # If it's an LLM method we're skipping, add None temporarily
                else:
                    output[section_enum.value] = None # Will be filtered later
                continue # Skip to next config item

            # --- If section IS in sections_to_generate, run it ---
            logging.info(f"  Generating section: {section_enum.name}")

            # --- Handle sections copied or using placeholders (should be in set?) ---
            if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                 try:
                     method = getattr(self, method_name)
                     # Store result directly
                     output[section_enum.value] = method()
                 except Exception as e:
                     raise HopExecutionError(f"Unexpected error in {method_name} for {section_enum.value}: {e}") from e
                 continue # Skip to next config item

            # --- Determine Temperature for LLM-generated sections ---
            final_temp = temperature_overrides.get(section_enum)
            if final_temp is None:
                 logging.error(f"  {section_enum.name}: Temperature override NOT FOUND! Halting.")
                 raise HopExecutionError(f"Misconfiguration: Temperature override missing for {section_enum.name}")

            # --- Call the generation method ---
            # NOTE: The called method is expected to raise HopExecutionError on failure
            try:
                method = getattr(self, method_name)
                # Check if the method needs the current output dict (for synthesis)
                if method_name in ["_generate_k5_unify_overview", "_generate_k6_ibm_overview"]:
                    # Pass the current state of the output dict
                    generated_content = method(current_output=output, temperature_override=final_temp)
                elif method_name in ["_generate_k8_ey_overview", "_generate_k9_early_career_overview"]:
                    # Pass company name for these overview methods (still using rewrite logic)
                     company_name = "Ernst & Young" if method_name == "_generate_k8_ey_overview" else "Early Career Roles"
                     # Find the master overview for these sections as they still use the rewrite logic
                     experience_section = next((exp for exp in self.master_resume['professional_experience'] if company_name in exp['company']), None)
                     source_overview = experience_section['overview'] if experience_section else ""
                     if not source_overview:
                          raise HopExecutionError(f"Source overview not found for {company_name} in {section_enum.value}.")
                     # Call the original rewrite method signature
                     generated_content = method(source_overview=source_overview, temperature_override=final_temp)
                else:
                    # Pass only the temperature for other LLM methods
                    generated_content = method(temperature_override=final_temp)

                # Store the result in the output dictionary
                output[section_enum.value] = generated_content

                # Basic check for placeholders
                if isinstance(generated_content, str) and "[Placeholder" in generated_content:
                    raise HopExecutionError(f"{section_enum.value} generation returned placeholder unexpectedly: {generated_content}")

            except HopExecutionError as he:
                 logging.error(f"Generation HALTED at section {section_enum.value} ({method_name}): {he}", exc_info=False)
                 raise he # Propagate the error to stop the process
            except Exception as e:
                 logging.error(f"Unexpected Error generating section {section_enum.value} with {method_name} (Temp: {final_temp}): {e}", exc_info=True)
                 raise HopExecutionError(f"Unexpected error during {section_enum.value} generation: {e}") from e

        # Return *only* the newly generated content (and copied content) for this pass
        # Filter out the None values for sections that were skipped
        final_output_for_this_pass = {k: v for k, v in output.items() if v is not None}
        return final_output_for_this_pass

    # --- Copy Methods ---
    def _copy_k0_name(self) -> str: return self.master_resume.get("owner", {}).get("name", "")
    def _copy_k0_contact(self) -> str:
        contact = self.master_resume.get("owner", {}).get("contact", {})
        parts = [f"Phone: {contact.get('phone', '')}", f"Email: {contact.get('email', '')}", f"LinkedIn: {contact.get('linkedin', '')}"]
        return " | ".join(p for p in parts if p.split(': ')[1])
    def _copy_k7_tradersense_bullets(self) -> List[str]:
        tradersense_exp = next((exp for exp in self.master_resume['professional_experience'] if 'TraderSense' in exp['company']), None)
        return tradersense_exp.get('highlights', [])[:2] if tradersense_exp else []
    def _copy_k7_tradersense_overview(self) -> str:
        tradersense_exp = next((exp for exp in self.master_resume['professional_experience'] if 'TraderSense' in exp['company']), None)
        return tradersense_exp.get('overview', "") if tradersense_exp else ""
    def _copy_k11_education(self) -> List[Dict]: return self.master_resume.get("education", [])
    def _copy_k12_certifications(self) -> List[str]: return self.master_resume.get('certifications_and_credentials', [])
    def _generate_dummy_header(self) -> str: return "HEADER_PLACEHOLDER"

    # --- LLM Generation Methods ---

    def _generate_k0_headline(self, temperature_override: Optional[float] = None) -> str:
        """
        Generates K.0 Headline. Relies on validator for constraint check.
        v12.05: No internal fallback on word count failure. Raises error on API failure.
        """
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'Key Expertise') if self.thematic_analysis.primary_theme else 'Key Expertise'
        differentiators = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            differentiators = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])

        feedback_instruction = "" # Add feedback logic if needed

        prompt = f"""Generate a compelling resume headline for a candidate applying for a role focused on '{primary_theme}'.
Key differentiating keywords from the job description analysis include: {', '.join(differentiators[:5])}.
The headline should be structured as 3 distinct components separated by pipes (|). Each component should be 2-4 words.

ABSOLUTELY CRITICAL:
1.  Total headline length MUST be strictly between {self.constraints.HEADLINE_WORD_COUNT_MIN} and {self.constraints.HEADLINE_WORD_COUNT_MAX} words.
2.  Each of the 3 components MUST be between {self.constraints.HEADLINE_COMPONENT_WORDS_MIN} and {self.constraints.HEADLINE_COMPONENT_WORDS_MAX} words.
3.  DO NOT include job titles like Director, VP, Manager, Lead, etc. Focus on skills and outcomes.
4.  DO NOT use commas. Use pipes (|) as the ONLY separator.
5.  Output ONLY the headline text. Do NOT use markdown fences like ```.

{feedback_instruction}
Example Format: Skill Area 1 | Skill Area 2 | Outcome Focus

Generate Headline:
"""
        reasoning_config = ReasoningConfig.K0_HEADLINE_CONFIG
        base_system = "You are an expert resume headline crafter specializing in concise, impactful, keyword-rich headlines without using job titles."

        # Call API (raises HopExecutionError on API failure)
        headline = self._call_gemini_api(
            prompt, reasoning_config, ResumeSection.K0_HEADLINE.value, base_system,
            temperature_override=temperature_override
        )
        return headline # Return generated text directly

    def _generate_k1_executive_summary(self, temperature_override: Optional[float] = None) -> str:
        """
        Generates K.1 Executive Summary. Relies on validator for sentence count.
        v12.05: Raises error on API failure.
        """
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key skills') if self.thematic_analysis.primary_theme else 'key skills'
        differentiators = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            differentiators = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        role_archetype = self.thematic_analysis.role_classification.get('role_archetype', 'Experienced Professional') if self.thematic_analysis.role_classification else 'Experienced Professional'

        # Example: Map archetype to descriptive phrase
        archetype_map = {
            "Executive_Leader": "an executive leader",
            "Technical_IC": "a hands-on technical expert",
            "Post-Sales_Customer_Success": "a customer success leader",
            "Pre-Sales_GTM": "a pre-sales GTM strategist",
            "Product_Management": "a product management professional"
        }
        archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."

        # Feedback based on previous failures
        feedback_instruction = ""
        sentence_count_failures = [f for f in self.previous_failures if f.rule_id == "VG_SENTENCE_COUNT_K1"]
        if sentence_count_failures:
            last_fail = sentence_count_failures[-1]
            if last_fail.details:
                 actual = last_fail.details.get('sentence_count')
                 target = f"{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}"
                 feedback_instruction = f"\nIMPORTANT FEEDBACK: Previous attempt failed sentence count check (had {actual} sentences, target is {target}). Adjust sentence structure to meet the target range precisely."

        prompt = f"""Write a compelling executive summary (approx. 150 words) for a resume targeting a role focused on '{primary_theme}'.
Key differentiating keywords from the JD analysis to incorporate: {', '.join(differentiators[:self.constraints.K1_MIN_DIFFERENTIATORS])}.
{archetype_instruction}

Reference Experience (Use metrics and context from here):
{json.dumps(self.enriched_scaffold['experience_sections'][:2], indent=2)}

NON-NEGOTIABLE REQUIREMENTS:
1.  SENTENCE COUNT: MUST have strictly between {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences. Count carefully.
2.  KEYWORDS: Naturally integrate at least {self.constraints.K1_MIN_DIFFERENTIATORS} of the differentiating keywords.
3.  CONTENT: Summarize key achievements, skills, and career trajectory relevant to the primary theme and keywords. Use quantifiable results where possible.
4.  TONE: Professional, confident, and achievement-oriented.
5.  Output ONLY the executive summary text. Do NOT use markdown fences like ```.
{feedback_instruction}

Output ONLY the executive summary text.
"""
        reasoning_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG
        base_system = "You are an expert resume writer specializing in crafting concise, impactful executive summaries tailored to specific job descriptions."
        # API call raises HopExecutionError on failure
        summary = self._call_gemini_api(
            prompt, reasoning_config, "K.1", base_system,
            temperature_override=temperature_override
        )
        return summary # Return generated text directly

    def _generate_k2_skills(self, temperature_override: Optional[float] = None) -> List[str]:
        """
        Generates K.2 Skills. Raises error on API failure or parsing/validation failure.
        v12.05: Fail fast instead of returning error messages in the list.
        """
        try:
            primary_theme_kw = self.thematic_analysis.primary_theme.get('keywords', []) if self.thematic_analysis.primary_theme else []
            diff_kw = []
            if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
                diff_kw = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])

            combined_keywords = list(set(primary_theme_kw + diff_kw))[:15] # Top 15 combined

            prompt = f"""Based on the following key themes and keywords derived from a target job description, generate a list of exactly 12 relevant skills.

Key Themes/Keywords: {', '.join(combined_keywords)}

Requirements:
1.  Generate EXACTLY 12 skills.
2.  Each skill MUST be 1 to 3 words long.
3.  Focus on nouns and noun phrases (e.g., "Cloud Strategy", "GTM Execution", "AWS Partnerships"). Avoid verbs.
4.  Prioritize skills directly matching or closely related to the provided keywords.
5.  Output ONLY the list of skills, separated by newlines. Do not use bullets, numbers, markdown fences like ```, or any other formatting.

Example Output:
Skill One
Skill Two Name
Third Skill

Generate Skills List:
"""
            reasoning_config = ReasoningConfig.K2_SKILLS_CONFIG
            base_system = "You are an expert HR data analyst specializing in extracting concise, relevant skills from job requirements."
            # API call raises HopExecutionError on failure
            skills_text = self._call_gemini_api(
                prompt, reasoning_config, "K.2", base_system,
                temperature_override=temperature_override
            )

            # --- Parse and Validate Output ---
            skills_list_final = []
            # Split by newline, handle potential commas as well just in case
            skills_intermediate = re.split(r'[\n,]', skills_text)
            malformed_count = 0
            for skill in skills_intermediate:
                # Remove potential list markers and strip whitespace
                cleaned_skill = re.sub(r'^[•*\-\d\.]+\s*', '', skill).strip()
                if not cleaned_skill: continue # Skip empty lines

                word_count = len(cleaned_skill.split())
                # Strict validation: 1 to 3 words
                if 1 <= word_count <= 3:
                    skills_list_final.append(cleaned_skill)
                else:
                    logging.warning(f"K.2: Discarding malformed skill '{cleaned_skill}' (words: {word_count})")
                    malformed_count += 1

            # --- Fail Fast if insufficient valid skills ---
            # Expecting exactly 12
            if len(skills_list_final) != 12:
                raise HopExecutionError(f"K.2 generation failed: Expected exactly 12 valid 1-3 word skills, found {len(skills_list_final)}. Output preview: {skills_text[:100]}...")
            # Allow zero malformed skills, fail if any were discarded
            if malformed_count > 0:
                 raise HopExecutionError(f"K.2 generation failed: Found {malformed_count} malformed skills (invalid word count) which were discarded. Output preview: {skills_text[:100]}...")


            return skills_list_final # Return exactly 12 valid skills

        except HopExecutionError as he:
             raise he # Propagate API or validation errors
        except Exception as e: # Catch potential regex/parsing errors
            logging.error(f"K.2 Skills processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"K.2 processing failed: {e}") from e

    def _generate_tailored_overview_for_experience(
        self,
        generated_bullets: List[Dict], # CHANGED: Now accepts generated bullets
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_id: str,
        # company_name is no longer needed here
        temperature_override: Optional[float] = None
    ) -> str:
        """
        [REFACTORED V12.55]
        Generates tailored overviews by synthesizing provided bullet points.
        Relies on validator for word count. Raises error on API failure.
        """
        if not generated_bullets:
            raise HopExecutionError(f"Cannot generate overview for {section_id}: No generated bullets provided.")

        bullet_texts = []
        for i, bullet_data in enumerate(generated_bullets):
             text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
             if not text:
                  logging.warning(f"Skipping empty bullet at index {i} during overview synthesis for {section_id}")
                  continue
             bullet_texts.append(f"* {text}")

        if not bullet_texts:
            raise HopExecutionError(f"Cannot generate overview for {section_id}: All provided bullets were empty.")

        bullet_summary_input = "\n".join(bullet_texts)
        min_wc, max_wc = word_count_range

        # Extract primary theme and differentiator keywords for context
        primary_theme_kw = self.thematic_analysis.primary_theme.get('keywords', []) if self.thematic_analysis.primary_theme else []
        diff_kw = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            diff_kw = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])

        context_keywords = list(set(primary_theme_kw + diff_kw))[:10] # Top 10 combined

        prompt = f"""You are an expert resume editor. Your task is to write a concise 1-2 sentence overview that accurately summarizes the key achievements and themes from the following bullet points.

**BULLETS TO SUMMARIZE:**
{bullet_summary_input}

**CONTEXT:**
* **Target Job Description Keywords:** {', '.join(context_keywords)}
* Focus on quantifying impact and aligning with strategic themes like alliances, GTM, revenue generation, and leadership if present in the bullets.

**ABSOLUTELY CRITICAL:**
1. The final overview MUST be strictly between {min_wc} and {max_wc} words total. Do NOT exceed {max_wc} words.
2. Output ONLY the overview text, with no preamble, explanation, or markdown fences like ```.

**FINAL OVERVIEW ({min_wc}-{max_wc} words):**
"""

        system_prompt = "You are an expert resume editor specializing in summarizing experience sections."
        # API call raises HopExecutionError on failure
        synthesized_overview = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )

        # Basic check to prevent obviously wrong outputs (e.g., just repeating the prompt)
        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")

        # Final word count check (redundant with validator, but good safety)
        final_wc = count_words_ms_word_style(synthesized_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{synthesized_overview}'")
             # We rely on the HOP-5 validator to fail this if it's critical.

        return synthesized_overview # Return generated text directly

    # --- Methods calling _generate_tailored_overview_for_experience ---
    def _generate_k5_unify_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> str:
        """
        [REFACTORED V12.55] Generates K.5 Unify Overview by synthesizing K.5 Bullets.
        """
        # Retrieve the bullets generated in the same pass
        generated_bullets = current_output.get(ResumeSection.K5_UNIFY_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K5_UNIFY_OVERVIEW.value}: Corresponding bullets not found or invalid in current output.")

        return self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K5_UNIFY_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K5_UNIFY_OVERVIEW.value,
            temperature_override=temperature_override
        )

    def _generate_k6_ibm_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> str:
        """
        [REFACTORED V12.55] Generates K.6 IBM Overview by synthesizing K.6 Bullets.
        """
        # Retrieve the bullets generated in the same pass
        generated_bullets = current_output.get(ResumeSection.K6_IBM_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K6_IBM_OVERVIEW.value}: Corresponding bullets not found or invalid in current output.")

        return self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K6_IBM_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K6_IBM_OVERVIEW.value,
            temperature_override=temperature_override
        )

    # Note: EY and Early Career still use the rewrite logic, adjust if needed
    def _generate_k8_ey_overview(self, source_overview: str, temperature_override: Optional[float] = None) -> str:
        """Generates K.8 EY Overview by rewriting the source overview."""
        min_wc = self.constraints.EY_OVERVIEW_WORD_COUNT_MIN
        max_wc = self.constraints.EY_OVERVIEW_WORD_COUNT_MAX
        reasoning_config = ReasoningConfig.K8_EY_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT
        section_id = ResumeSection.K8_EY_OVERVIEW.value

        primary_theme_kw = self.thematic_analysis.primary_theme.get('keywords', []) if self.thematic_analysis.primary_theme else []
        diff_kw = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            diff_kw = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        context_keywords = list(set(primary_theme_kw + diff_kw))[:5]

        prompt = f"""Rewrite the following source overview for a resume, tailoring it slightly towards these keywords: {', '.join(context_keywords)}.

SOURCE OVERVIEW (Ernst & Young):
{source_overview}

ABSOLUTELY CRITICAL:
1. The rewritten overview MUST be strictly between {min_wc} and {max_wc} words.
2. Output ONLY the rewritten overview text. Do NOT use markdown fences like ```.

REWRITTEN OVERVIEW ({min_wc}-{max_wc} words):
"""
        system_prompt = "You are an expert resume editor focusing on concise experience overviews."
        tailored_overview = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )
        # Final word count check (safety)
        final_wc = count_words_ms_word_style(tailored_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{tailored_overview}'")
        return tailored_overview

    def _generate_k9_early_career_overview(self, source_overview: str, temperature_override: Optional[float] = None) -> str:
        """Generates K.9 Early Career Overview by rewriting the source overview."""
        min_wc = self.constraints.EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN
        max_wc = self.constraints.EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX
        reasoning_config = ReasoningConfig.K9_EARLY_CAREER_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT
        section_id = ResumeSection.K9_EARLY_CAREER_OVERVIEW.value

        primary_theme_kw = self.thematic_analysis.primary_theme.get('keywords', []) if self.thematic_analysis.primary_theme else []
        diff_kw = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            diff_kw = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        context_keywords = list(set(primary_theme_kw + diff_kw))[:5]

        prompt = f"""Rewrite the following source overview for a resume, tailoring it slightly towards these keywords: {', '.join(context_keywords)}.

SOURCE OVERVIEW (Early Career):
{source_overview}

ABSOLUTELY CRITICAL:
1. The rewritten overview MUST be strictly between {min_wc} and {max_wc} words.
2. Output ONLY the rewritten overview text. Do NOT use markdown fences like ```.

REWRITTEN OVERVIEW ({min_wc}-{max_wc} words):
"""
        system_prompt = "You are an expert resume editor focusing on concise experience overviews."
        tailored_overview = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )
        # Final word count check (safety)
        final_wc = count_words_ms_word_style(tailored_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{tailored_overview}'")
        return tailored_overview

    # --- Bullet Generation Helpers ---

    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id: str) -> List[Dict]:
        """
        Validates LLM bullet selection. Raises HopExecutionError on failure.
        v12.05: Fail fast instead of returning fallback. Ensures exact match and no duplicates.
        """
        # Check 1: Did the LLM return the correct number of bullets?
        if len(selected_bullets_text) != expected_count:
            msg = f"{section_id} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}. Output preview: '{str(selected_bullets_text)[:100]}...'"
            logging.error(msg)
            raise HopExecutionError(msg)

        validated_bullets = []
        # Create a lookup map for efficient checking (master text -> original dict)
        master_texts_map = {b['bullet_text'].strip(): b for b in master_bullets_structured if 'bullet_text' in b}
        returned_texts_set = set() # To detect duplicates returned by the LLM

        # Check 2 & 3: Does each returned bullet exactly match a master bullet, and are there duplicates?
        for selected_text in selected_bullets_text:
            cleaned_text = selected_text.strip() # Ensure no leading/trailing whitespace

            if cleaned_text in master_texts_map:
                 # Check if this exact text has already been added
                 if cleaned_text in returned_texts_set:
                      msg = f"{section_id} LLM returned duplicate bullet: '{cleaned_text[:50]}...'"
                      logging.error(msg)
                      raise HopExecutionError(msg)
                 # If it's a valid match and not a duplicate, add the original structured dict
                 validated_bullets.append(master_texts_map[cleaned_text])
                 returned_texts_set.add(cleaned_text) # Mark this text as used
            else:
                # If the text doesn't exactly match any master bullet
                msg = f"{section_id} LLM returned bullet not found in master list or modified: '{cleaned_text[:50]}...'"
                # Log potential near matches for debugging
                # (You could add fuzzy matching here if needed, but strict is safer)
                logging.error(msg + f" Master keys nearby: {[k[:50] for k in master_texts_map.keys() if k.startswith(cleaned_text[:10])]}")
                raise HopExecutionError(msg)

        # Check 4: Did we successfully validate the expected number of *unique* bullets?
        # This check is somewhat redundant due to check 1 and the duplicate check, but serves as a final safeguard.
        if len(validated_bullets) != expected_count:
             msg = f"{section_id} failed final validation: Expected {expected_count} unique bullets from master list, but validated {len(validated_bullets)}."
             logging.error(msg)
             raise HopExecutionError(msg)

        logging.info(f"  ✓ {section_id}: Successfully validated {len(validated_bullets)} verbatim bullets.")
        return validated_bullets

    def _rewrite_bullet_for_word_count(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id: str, temperature_override: Optional[float] = None) -> str:
        """
        Rewrites a bullet for word count. Raises HopExecutionError if rewrite fails compliance.
        v12.05: Fail fast instead of returning original.
        """
        try:
            min_wc, max_wc = target_word_count_range
            prompt = f"""Rewrite the following resume bullet point to meet a specific word count constraint, while preserving the core meaning, key metrics, and professional tone.

ORIGINAL BULLET:
{original_bullet_text}

ABSOLUTELY CRITICAL:
1. The rewritten bullet MUST be strictly between {min_wc} and {max_wc} words (inclusive). Count words carefully using standard English rules (hyphenated words count as one).
2. Output ONLY the rewritten bullet text. Do NOT use markdown fences like ```.

REWRITTEN BULLET ({min_wc}-{max_wc} words):
"""
            # Use a default reasoning config, as this is a constrained rewrite task
            reasoning_config = ReasoningConfig.DEFAULT
            system_prompt = f"You are an expert resume editor specializing in concisely rewriting bullet points to meet strict word count targets."
            rewritten_text = self._call_gemini_api(
                prompt, reasoning_config, f"{section_id}_RewriteWC", system_prompt,
                temperature_override=temperature_override
            )

            # Validate the word count of the rewritten text
            rewritten_wc = count_words_ms_word_style(rewritten_text)
            if not (min_wc <= rewritten_wc <= max_wc):
                 msg = f"{section_id}_RewriteWC returned non-compliant word count ({rewritten_wc}, target: {min_wc}-{max_wc})."
                 logging.error(msg + f" Original: '{original_bullet_text[:50]}...' Rewritten: '{rewritten_text[:50]}...'")
                 # Raise error if the LLM failed to meet the constraint
                 raise HopExecutionError(msg)

            return rewritten_text

        except HopExecutionError as he:
            # Propagate errors from the API call or the word count validation
            raise he
        except Exception as e:
            # Catch any other unexpected errors during the process
            logging.error(f"{section_id}_RewriteWC unexpected error: {e}", exc_info=True)
            raise HopExecutionError(f"{section_id}_RewriteWC failed: {e}") from e

    def _validate_and_potentially_rewrite_bullets(
        self,
        selected_bullets_structured: List[Dict], master_avg_lengths: Dict[str, float],
        section_name_for_avg: str, section_id_for_logging: str,
        temperature_override: Optional[float] = None
    ) -> List[Dict]:
        """
        [v12.05 REWRITE] Checks word count, attempts rewrite if needed. Raises HopExecutionError on failure.
        Uses master average lengths +/- tolerance to set target range.
        """
        final_bullets = []
        # Get the average length for this section type, fallback to Default
        avg_len = master_avg_lengths.get(section_name_for_avg, master_avg_lengths.get("Default", 25.0))
        # --- START FIX ---
        # Access the constant from the PreFlightValidator class
        tolerance = PreFlightValidator.BULLET_WORD_COUNT_TOLERANCE # e.g., 0.20
        # --- END FIX ---
        min_target = round(avg_len * (1 - tolerance))
        max_target = round(avg_len * (1 + tolerance))
        logging.info(f"  Validating word count for {section_id_for_logging} against target range: {min_target}-{max_target} (Avg: {avg_len:.1f})")


        for i, bullet_data in enumerate(selected_bullets_structured):
            # Basic type check for safety
            if not isinstance(bullet_data, dict):
                 raise HopExecutionError(f"Invalid item found in bullet list for {section_id_for_logging} at index {i}: {bullet_data}")

            # Extract text, provenance, and calculate word count
            # Prefer 'text' key if present (from rewrite/customization), fallback to 'bullet_text' (from verbatim)
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
            original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            # Use pre-calculated word_count if available, otherwise calculate it
            word_count = bullet_data.get('word_count', count_words_ms_word_style(original_text))

            if not original_text:
                 raise HopExecutionError(f"Empty bullet found in {section_id_for_logging} at index {i}.")

            # Check if word count is within the calculated tolerance range
            if not (min_target <= word_count <= max_target):
                logging.warning(f"  Word count ({word_count}) outside target ({min_target}-{max_target}) for {section_id_for_logging}[{i}]. Attempting rewrite...")
                try:
                    # Call the rewrite helper function
                    rewritten_text = self._rewrite_bullet_for_word_count(
                        original_bullet_text=original_text,
                        target_word_count_range=(min_target, max_target),
                        section_id=f"{section_id_for_logging}_RewriteWC_{i}",
                        temperature_override=temperature_override
                    )
                    rewritten_word_count = count_words_ms_word_style(rewritten_text)
                    logging.info(f"    Rewrite SUCCESSFUL for {section_id_for_logging}[{i}]. New count: {rewritten_word_count}")

                    # Update provenance if a Verbatim bullet was rewritten
                    new_provenance = BulletProvenance.Customized.value if original_provenance == BulletProvenance.Verbatim.value else original_provenance

                    # Append the rewritten bullet data
                    final_bullets.append({
                        "text": rewritten_text, # Use the new text
                        "provenance": new_provenance,
                        "word_count": rewritten_word_count, # Use the new word count
                        "original_text_if_rewritten": original_text # Store original for QA
                    })
                except HopExecutionError as rewrite_he:
                    # If the rewrite fails (either API error or word count still wrong), halt the process
                    logging.error(f"Failed to correct word count for {section_id_for_logging}[{i}]. Reason: {rewrite_he}")
                    raise HopExecutionError(f"Bullet word count correction failed for {section_id_for_logging}[{i}]: {rewrite_he}") from rewrite_he
            else:
                # If word count is already compliant, append the original data
                final_bullets.append({
                    "text": original_text,
                    "provenance": original_provenance,
                    "word_count": word_count
                    # No original_text_if_rewritten needed
                })

        logging.info(f"  ✓ Word count validation/rewrite complete for {section_id_for_logging}.")
        return final_bullets

    def _generate_lightly_customized_bullets(
        self,
        source_bullets_text: List[str], section_id: str,
        thematic_analysis: ThematicAnalysis, temperature_override: Optional[float] = None
    ) -> List[Dict]:
        """
        Lightly rewrites bullets based on thematic analysis. Raises HopExecutionError on failure or incorrect count.
        v12.05: Fail fast.
        """
        try:
            if not source_bullets_text: return [] # Return empty list if no source bullets

            primary_theme_kw = thematic_analysis.primary_theme.get('keywords', []) if thematic_analysis.primary_theme else []
            diff_kw = []
            if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
                diff_kw = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
            context_keywords = list(set(primary_theme_kw + diff_kw))[:5] # Top 5 combined

            bullets_input = "\n".join([f"• {b}" for b in source_bullets_text])

            prompt = f"""Lightly rewrite the following resume bullet points to subtly align with the target job description's themes and keywords, while preserving the original meaning, metrics, and professional tone.

SOURCE BULLETS:
{bullets_input}

TARGET KEYWORDS/THEMES (use for subtle emphasis): {', '.join(context_keywords)}

Requirements:
1.  Rewrite EACH source bullet.
2.  Maintain the original core achievement and metrics.
3.  Subtly incorporate or emphasize aspects related to the target keywords where natural. Do not force keywords unnaturally.
4.  Ensure professional resume language.
5.  Output ONLY the rewritten bullets, one per line, starting with "• ". Do NOT use markdown fences like ```.
6.  Produce EXACTLY {len(source_bullets_text)} rewritten bullets.

REWRITTEN BULLETS:
"""
            # Use default reasoning for this focused rewrite task
            reasoning_config = ReasoningConfig.DEFAULT
            system_prompt = "You are an expert resume editor skilled at subtly tailoring bullet points to job descriptions."
            response_text = self._call_gemini_api(
                prompt, reasoning_config, section_id, system_prompt,
                temperature_override=temperature_override
            )

            # Parse the response, expecting bullets starting with "• "
            rewritten_bullets = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]

            # Validate the count
            if len(rewritten_bullets) != len(source_bullets_text):
                msg = f"{section_id} LLM returned {len(rewritten_bullets)} customized bullets, expected {len(source_bullets_text)}. Output preview: {response_text[:100]}..."
                logging.error(msg)
                raise HopExecutionError(msg)

            # Return structured data
            return [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": count_words_ms_word_style(b)} for b in rewritten_bullets]

        except HopExecutionError as he:
            # Propagate API errors or count validation errors
            raise he
        except Exception as e:
            # Catch other unexpected errors
            logging.error(f"{section_id} customization processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_id} customization failed: {e}") from e

    def _generate_synthetic_bullets(
        self,
        count: int, company_name: str, job_description: str,
        thematic_analysis: ThematicAnalysis, context_bullets: str, # Context of existing bullets in the section
        reasoning_config: ReasoningConfig, section_id: str,
        temperature_override: Optional[float] = None
    ) -> List[Dict]:
        """
        Generates plausible, synthetic resume bullets based on context. Raises HopExecutionError on failure or incorrect count.
        v12.05: Fail fast.
        """
        try:
            if count <= 0: return [] # Nothing to generate

            primary_theme = thematic_analysis.primary_theme.get('name', 'key responsibilities') if thematic_analysis.primary_theme else 'key responsibilities'
            primary_theme_kw = thematic_analysis.primary_theme.get('keywords', []) if thematic_analysis.primary_theme else []
            diff_kw = []
            if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
                diff_kw = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
            context_keywords = list(set(primary_theme_kw + diff_kw))[:10] # Top 10 combined

            prompt = f"""Generate {count} plausible, unique, and impactful synthetic resume bullet points for a role at '{company_name}'. These bullets should align with the themes derived from the target job description and complement the existing bullets provided for context.

TARGET JOB DESCRIPTION THEME: '{primary_theme}'
TARGET JOB DESCRIPTION KEYWORDS: {', '.join(context_keywords)}

EXISTING BULLETS IN THIS SECTION (for context and to avoid duplication):
{context_bullets if context_bullets else "(No existing bullets provided)"}

Requirements:
1.  Generate EXACTLY {count} new, distinct bullet points.
2.  Each bullet MUST be a plausible achievement relevant to the company and target themes/keywords.
3.  Each bullet should ideally imply quantifiable impact or significant action (use strong action verbs).
4.  DO NOT simply rephrase the existing bullets. Create *new* achievements.
5.  Maintain a professional and consistent tone.
6.  Output ONLY the {count} new bullet points, one per line, starting with "* ". Do NOT use markdown fences like ```.

GENERATED SYNTHETIC BULLETS:
"""
            system_prompt = "You generate plausible, impactful, synthetic resume bullets aligned with job requirements and existing content."
            response_text = self._call_gemini_api(
                prompt, reasoning_config, section_id, system_prompt,
                temperature_override=temperature_override
            )

            # Parse the response, expecting bullets starting with "* "
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]

            # Validate the count
            if len(synthetic_bullets_text) != count:
                msg = f"{section_id} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}). Output preview: {response_text[:100]}..."
                logging.error(msg)
                raise HopExecutionError(msg)

            # Return structured data
            return [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": count_words_ms_word_style(b)} for b in synthetic_bullets_text]

        except HopExecutionError as he:
            # Propagate API errors or count validation errors
            raise he
        except Exception as e:
            # Catch other unexpected errors
            logging.error(f"{section_id} synthetic generation processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_id} synthetic generation failed: {e}") from e

    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str, section_index: int, provenance_targets: Dict[str, int],
            reasoning_config: ReasoningConfig, section_id: str,
            temperature_override: Optional[float] = None
    ) -> List[Dict]:
        """
        Generic method to generate bullets (Verbatim, Customized, Synthetic) based on provenance targets.
        Raises HopExecutionError on failures during selection, generation, validation, or reordering.
        v12.05: Uses fail-fast helpers for selection, customization, synthesis, and word count validation.
        """
        logging.info(f"  Generating bullets for {section_id} (Targets: {provenance_targets})")
        # --- 1. Get Master Bullets ---
        # Find the corresponding experience section in the master resume
        experience_section = next((exp for exp in self.master_resume['professional_experience'] if company_name in exp.get('company', '')), None)
        if not experience_section:
            raise HopExecutionError(f"Master experience data not found for company '{company_name}' needed for {section_id}")

        # Extract master bullets into the required structured format
        master_bullets_structured = []
        # Use 'bullet_pool' preferentially, fallback to 'highlights'
        bullet_source = experience_section.get("bullet_pool", experience_section.get("highlights", []))
        if not isinstance(bullet_source, list):
             raise HopExecutionError(f"{section_id} master bullet source ('{experience_section.get('bullet_pool') or experience_section.get('highlights')}') is not a list for company '{company_name}'.")

        for bullet_text in bullet_source:
             # Ensure the item is a non-empty string before processing
             if isinstance(bullet_text, str) and bullet_text.strip():
                 master_bullets_structured.append({
                     "bullet_text": bullet_text.strip(), # Store the original, clean text
                     "text": bullet_text.strip(),        # 'text' key for consistency after potential rewrites
                     "provenance": BulletProvenance.Verbatim.value,
                     "word_count": count_words_ms_word_style(bullet_text.strip())
                 })
             else:
                  logging.warning(f"Skipping invalid master bullet item for {company_name}: {bullet_text}")

        if not master_bullets_structured:
             logging.warning(f"No valid master bullets found for company '{company_name}' in section {section_id}.")
             # Only raise error if verbatim bullets were actually requested
             if provenance_targets.get('Verbatim', 0) > 0:
                 raise HopExecutionError(f"{section_id} Cannot select Verbatim bullets: No valid master bullets available for '{company_name}'.")

        # --- 2. Initialize Counts and Final List ---
        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        final_bullets = [] # This list will hold the generated bullet dictionaries

        # --- 3. Select Verbatim Bullets (if needed) ---
        if verbatim_count > 0:
            logging.info(f"    Selecting {verbatim_count} Verbatim bullets...")
            if len(master_bullets_structured) < verbatim_count:
                raise HopExecutionError(f"{section_id} Cannot select {verbatim_count} Verbatim bullets: Only {len(master_bullets_structured)} master bullets available for '{company_name}'.")

            # Prepare prompt for LLM selection
            master_bullets_text_list = [b['bullet_text'] for b in master_bullets_structured]
            prompt_select = f"""Select the {verbatim_count} most relevant bullet points from the MASTER LIST below that align with the TARGET KEYWORDS.

MASTER LIST ({company_name}):
{chr(10).join([f'- {b}' for b in master_bullets_text_list])}

TARGET KEYWORDS (derived from Job Description):
{', '.join(getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])[:10]) if hasattr(self.thematic_analysis, 'competitive_intelligence') else 'N/A'}

Instructions:
1. Choose EXACTLY {verbatim_count} bullets from the MASTER LIST.
2. Output ONLY the selected bullet points, exactly as they appear in the MASTER LIST, one per line. Do not add numbers, prefixes, explanations, or markdown fences like ```.

SELECTED BULLETS:
"""
            system_prompt_select="You are an AI assistant that selects relevant resume bullet points based on keywords."
            try:
                # Call LLM to select bullets
                response_select = self._call_gemini_api(prompt_select, reasoning_config, f"{section_id}_SelectV", system_prompt_select, temperature_override=temperature_override)
                # Parse the response (one bullet per line)
                selected_texts = [line.strip() for line in response_select.split('\n') if line.strip()]
                # Validate the selection (exact match, correct count, no duplicates)
                verbatim_bullets = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id}_SelectV")
                final_bullets.extend(verbatim_bullets)
            except HopExecutionError as he:
                logging.error(f"{section_id} Verbatim selection/validation failed: {he}")
                raise he # Halt workflow

        # --- 4. Generate Customized Bullets (if needed) ---
        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} bullets...")
            # Identify master bullets *not* used for verbatim
            used_verbatim_texts = {b.get('bullet_text') for b in final_bullets if b.get('provenance') == BulletProvenance.Verbatim.value}
            available_for_custom = [b for b in master_bullets_structured if b.get('bullet_text') not in used_verbatim_texts]

            if len(available_for_custom) < customized_count:
                raise HopExecutionError(f"{section_id} Cannot customize {customized_count} bullets: Only {len(available_for_custom)} unique master bullets remaining after verbatim selection for '{company_name}'.")

            # Randomly select bullets to customize from the available pool
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count]

            try:
                # Call helper to rewrite the selected bullets
                customized_bullets = self._generate_lightly_customized_bullets(
                    source_bullets_text=[b['bullet_text'] for b in candidates_for_custom],
                    section_id=f"{section_id}_CustomC",
                    thematic_analysis=self.thematic_analysis,
                    temperature_override=temperature_override
                )
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he:
                logging.error(f"{section_id} Customization failed: {he}")
                raise he # Halt workflow

        # --- 5. Generate Synthetic Bullets (if needed) ---
        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic bullets...")
            # Provide context of bullets already selected/generated for this section
            context_bullets_text = '\n'.join([f"- {b.get('text', b.get('bullet_text', ''))}" for b in final_bullets])
            try:
                # Call helper to generate new bullets
                synthetic_bullets = self._generate_synthetic_bullets(
                    count=synthetic_count, company_name=company_name,
                    job_description=self.job_description, thematic_analysis=self.thematic_analysis,
                    context_bullets=context_bullets_text, reasoning_config=reasoning_config,
                    section_id=f"{section_id}_SynthS",
                    temperature_override=temperature_override
                )
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he:
                logging.error(f"{section_id} Synthetic generation failed: {he}")
                raise he # Halt workflow

        # --- 6. Final Count Check ---
        if len(final_bullets) != total_expected_count:
            # This should ideally be caught earlier, but serves as a final check
            raise HopExecutionError(f"{section_id} Generated incorrect total bullet count ({len(final_bullets)}), expected {total_expected_count}. Check V/C/S generation logic.")

        # --- 7. Word Count Validation & Potential Rewrite ---
        logging.info(f"    Validating word counts for {len(final_bullets)} generated bullets...")
        # Calculate master average lengths if not already done (though typically done once per workflow)
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
        # Determine the key to use for looking up the average length for this specific section
        section_name_for_avg = "Default" # Fallback
        # Map company name or section ID to the keys used in master_avg_lengths
        if "Unify" in company_name: section_name_for_avg = "Unify"
        elif "IBM" in company_name: section_name_for_avg = "IBM"
        elif "Ernst & Young" in company_name: section_name_for_avg = "EY"
        elif "Early Career" in company_name: section_name_for_avg = "EarlyCareer"
        elif section_id == ResumeSection.K10_COMPETENCIES.value: section_name_for_avg = "Competencies" # Special case for competencies

        try:
            # This helper validates each bullet's word count against the target range
            # and attempts to rewrite non-compliant ones, raising HopExecutionError if rewrite fails.
            final_bullets = self._validate_and_potentially_rewrite_bullets(
                selected_bullets_structured=final_bullets, # Pass the list generated so far
                master_avg_lengths=master_avg_lengths,
                section_name_for_avg=section_name_for_avg,
                section_id_for_logging=section_id, # For logging messages
                temperature_override=temperature_override # Pass temperature for potential rewrites
            )
        except HopExecutionError as he:
            logging.error(f"{section_id} Word count validation/rewrite failed: {he}")
            raise he # Halt workflow

        # --- 8. Reorder Bullets ---
        logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
        # Prepare current bullet texts for the reordering prompt
        # Use the 'text' key which contains the final (potentially rewritten) text
        current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets)]
        current_bullets_text_input = '\n'.join(current_bullets_text_list)

        prompt_reorder = f"""Reorder the following resume bullet points for maximum impact and relevance based on the target job description keywords. Prioritize bullets that show quantifiable results and align closely with the keywords.

**Bullets to Reorder ({company_name}):**
{current_bullets_text_input}

**Target Job Description Keywords (for relevance ranking):**
{', '.join(getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])[:10]) if hasattr(self.thematic_analysis, 'competitive_intelligence') else 'N/A'}

Instructions:
1.  Analyze the impact and keyword relevance of each bullet.
2.  Output the bullets in the optimal order, from most impactful/relevant to least.
3.  Output ONLY the reordered bullet points, exactly as provided in the input list, one per line. Do not add numbers, prefixes, explanations, or modify the text. Do NOT use markdown fences like ```.
4.  Ensure all {total_expected_count} bullets are present in the output.

**REORDERED BULLETS:**
"""
        system_prompt_reorder = "You are an expert resume editor who reorders bullet points for maximum impact based on relevance to target keywords."
        try:
            # Call LLM to get the reordered list of texts
            response_reorder = self._call_gemini_api(prompt_reorder, ReasoningConfig.DEFAULT, f"{section_id}_Reorder", system_prompt_reorder, temperature_override=temperature_override)
            # Parse the response (one bullet text per line)
            reordered_texts = [line.strip() for line in response_reorder.split('\n') if line.strip()]

            # --- Validation of Reordering ---
            # Check 1: Correct number of bullets returned?
            if len(reordered_texts) != total_expected_count:
                raise HopExecutionError(f"{section_id} Reordering returned wrong count ({len(reordered_texts)}), expected {total_expected_count}. Output preview: '{response_reorder[:100]}...'")

            # Check 2: Did the LLM modify text or return duplicates?
            final_ordered_bullets_dicts = []
            # Create a map from the *final* bullet text (post-rewrite) to its corresponding dictionary
            original_texts_map = {b.get('text'): b for b in final_bullets}
            used_original_texts = set() # Track used texts to detect duplicates in LLM output

            for reordered_text in reordered_texts:
                 cleaned_reordered = reordered_text.strip()
                 # Does the returned text exactly match one of the input texts?
                 if cleaned_reordered in original_texts_map:
                     # Has this text already been added to the final list? (Checks for LLM duplication)
                     if cleaned_reordered in used_original_texts:
                          raise HopExecutionError(f"{section_id} Reordering validation failed: LLM returned duplicate bullet text '{cleaned_reordered[:50]}...'.")
                     # If valid and unique, add the corresponding dictionary to the final list
                     final_ordered_bullets_dicts.append(original_texts_map[cleaned_reordered])
                     used_original_texts.add(cleaned_reordered) # Mark as used
                 else:
                     # If the returned text doesn't match any input text
                     raise HopExecutionError(f"{section_id} Reordering validation failed: LLM modified text or returned unknown bullet ('{cleaned_reordered[:50]}...').")

            # Check 3: Does the final list have the correct number of unique items? (Final safeguard)
            if len(final_ordered_bullets_dicts) != total_expected_count:
                raise HopExecutionError(f"{section_id} Reordering validation failed: Final count mismatch ({len(final_ordered_bullets_dicts)}) after matching, expected {total_expected_count}.")

            logging.info(f"  ✓ Reordering complete for {section_id}.")
            return final_ordered_bullets_dicts # Return the list of dictionaries in the new order

        except HopExecutionError as he:
            logging.error(f"{section_id} Reordering failed: {he}")
            raise he # Halt workflow
        except Exception as e:
            logging.error(f"{section_id} Reordering unexpected error: {e}", exc_info=True)
            raise HopExecutionError(f"{section_id} Reordering failed: {e}") from e

    # --- Methods calling _generate_tailored_bullets_for_experience ---
    def _generate_k5_unify_bullets(self, temperature_override: Optional[float] = None) -> List[Dict]:
        return self._generate_tailored_bullets_for_experience(
            company_name="Unify Consulting", section_index=0,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K5_UNIFY_BULLETS],
            reasoning_config=ReasoningConfig.K5_UNIFY_BULLETS_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K5_UNIFY_BULLETS.value,
            temperature_override=temperature_override
        )

    def _generate_k6_ibm_bullets(self, temperature_override: Optional[float] = None) -> List[Dict]:
        return self._generate_tailored_bullets_for_experience(
            company_name="IBM", section_index=1,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K6_IBM_BULLETS],
            reasoning_config=ReasoningConfig.K6_IBM_BULLETS_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K6_IBM_BULLETS.value,
            temperature_override=temperature_override
        )

    def _generate_k10_competencies(self, temperature_override: Optional[float] = None) -> List[Dict]:
        """Generates K.10 Competencies using the bullet generation framework."""
        # Define a temporary 'company name' for context
        fake_company_name = "Strategic Competencies"
        # Get the source competencies from the master resume
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])

        # Temporarily add these competencies to the master resume structure
        # under the fake company name so the generic bullet generator can find them.
        # Use deepcopy to avoid modifying the original master resume object.
        original_master_resume = self.master_resume
        self.master_resume = copy.deepcopy(self.master_resume)
        self.master_resume["professional_experience"].append({
             "company": fake_company_name,
             "bullet_pool": competencies_list # Treat competencies as bullets for V/C/S
        })

        try:
            # Call the generic bullet generator
            generated_bullets = self._generate_tailored_bullets_for_experience(
                company_name=fake_company_name,
                section_index=-1, # Use an index that won't collide
                provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K10_COMPETENCIES],
                reasoning_config=ReasoningConfig.K10_COMPETENCIES_CONFIG or ReasoningConfig.DEFAULT,
                section_id=ResumeSection.K10_COMPETENCIES.value,
                temperature_override=temperature_override
            )
        finally:
             # IMPORTANT: Restore the original master resume object
             self.master_resume = original_master_resume

        # Post-processing: Remove any leading "**...:**" patterns often added by LLMs to competencies
        for bullet in generated_bullets:
             if 'text' in bullet and isinstance(bullet['text'], str):
                 bullet['text'] = re.sub(r'^\*\*\s*.*?:?\s*\*\*\s*', '', bullet['text']).strip()
                 # Recalculate word count after cleaning
                 bullet['word_count'] = count_words_ms_word_style(bullet['text'])

        return generated_bullets

    def _generate_k8_ey_bullets(self, temperature_override: Optional[float] = None) -> List[Dict]:
        """Generates K.8 EY Bullets (Customized only)."""
        ey_exp = next((exp for exp in self.master_resume['professional_experience'] if 'Ernst & Young' in exp.get('company','')), None)
        target_count = self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K8_EY_BULLETS]['Customized']

        if not ey_exp: raise HopExecutionError("K.8 EY master data not found.")
        source_bullets = ey_exp.get('highlights', []) # EY uses 'highlights'
        if not isinstance(source_bullets, list): raise HopExecutionError("K.8 EY master highlights is not a list.")
        valid_source_bullets = [b for b in source_bullets if isinstance(b, str) and b.strip()]

        if len(valid_source_bullets) < target_count:
            raise HopExecutionError(f"K.8 EY needs {target_count} valid source bullets, found {len(valid_source_bullets)}.")

        # Select the first 'target_count' valid bullets to customize
        bullets_to_customize = valid_source_bullets[:target_count]

        # Generate customized bullets
        customized_bullets = self._generate_lightly_customized_bullets(
            source_bullets_text=bullets_to_customize,
            section_id=ResumeSection.K8_EY_BULLETS.value,
            thematic_analysis=self.thematic_analysis,
            temperature_override=temperature_override
        )

        # Validate word counts
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
        return self._validate_and_potentially_rewrite_bullets(
             customized_bullets, master_avg_lengths, "EY", ResumeSection.K8_EY_BULLETS.value, temperature_override
        )

    def _generate_k9_early_career_bullets(self, temperature_override: Optional[float] = None) -> List[Dict]:
        """Generates K.9 Early Career Bullets (Customized only)."""
        early_exp = next((exp for exp in self.master_resume['professional_experience'] if 'Early Career' in exp.get('company','')), None)
        target_count = self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K9_EARLY_CAREER_BULLETS]['Customized']

        if not early_exp: raise HopExecutionError("K.9 Early Career master data not found.")
        source_bullets = early_exp.get('highlights', []) # Early Career uses 'highlights'
        if not isinstance(source_bullets, list): raise HopExecutionError("K.9 Early Career master highlights is not a list.")
        valid_source_bullets = [b for b in source_bullets if isinstance(b, str) and b.strip()]


        if len(valid_source_bullets) < target_count:
            raise HopExecutionError(f"K.9 Early Career needs {target_count} valid source bullets, found {len(valid_source_bullets)}.")

        # Select the first 'target_count' valid bullets to customize
        bullets_to_customize = valid_source_bullets[:target_count]

        # Generate customized bullets
        customized_bullets = self._generate_lightly_customized_bullets(
            source_bullets_text=bullets_to_customize,
            section_id=ResumeSection.K9_EARLY_CAREER_BULLETS.value,
            thematic_analysis=self.thematic_analysis,
            temperature_override=temperature_override
        )

        # Validate word counts
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
        return self._validate_and_potentially_rewrite_bullets(
             customized_bullets, master_avg_lengths, "EarlyCareer", ResumeSection.K9_EARLY_CAREER_BULLETS.value, temperature_override
        )

    # --- Cover Letter Generation ---
    def _generate_k13_cover_letter(self, temperature_override: Optional[float] = None) -> str:
        """
        [v12.05 NO_FALLBACK] Generates K.13 cover letter. Raises HopExecutionError on failure.
        Includes structure fixes.
        """
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key requirements') if self.thematic_analysis.primary_theme else 'key requirements'
        differentiators = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            differentiators = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        narratives_data = getattr(self.thematic_analysis, 'problem_solution_narratives', None) # Get attribute, might be None from cache
        narratives = narratives_data if isinstance(narratives_data, dict) else {} # Ensure narratives is a dict {} before using .get()

        # Now safely use .get() on the ensured dictionary
        problem_list = narratives.get('common_problems', ['solving key challenges'])
        problem = problem_list[0] if problem_list else 'solving key challenges' # Handle empty list case

        solution_list = narratives.get('solution_patterns', ['delivering impactful results'])
        solution = solution_list[0] if solution_list else 'delivering impactful results' # Handle empty list case
        # Get contact info for signature
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        expected_signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', '[Your Name]'),
            email=contact_info.get('email', '[Your Email]'),
            phone=contact_info.get('phone', '[Your Phone]'),
            linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
        ).strip() # Use the template

        # Retrieve relevant experience snippets (e.g., Unify and IBM)
        exp_snippets = ""
        unify_exp = next((exp for exp in self.enriched_scaffold['experience_sections'] if 'Unify' in exp['company']), None)
        ibm_exp = next((exp for exp in self.enriched_scaffold['experience_sections'] if 'IBM' in exp['company']), None)
        if unify_exp: exp_snippets += f"Unify:\n{unify_exp['overview']}\n{[b.get('text', '') for b in unify_exp['bullets'][:2]]}\n"
        if ibm_exp: exp_snippets += f"IBM:\n{ibm_exp['overview']}\n{[b.get('text', '') for b in ibm_exp['bullets'][:2]]}\n"


        prompt = f"""Write a professional cover letter for the candidate applying for a role focused on '{primary_theme}'.

JOB DESCRIPTION KEYWORDS/DIFFERENTIATORS: {', '.join(differentiators[:5])}
CANDIDATE'S RELEVANT EXPERIENCE (Snippets):
{exp_snippets}
NARRATIVE CONTEXT (Problem candidate solves): "{problem}" -> (Solution candidate provides): "{solution}"

INSTRUCTIONS:
1.  **Standard Letter Format:** Include today's date (Month Day, Year), recipient address placeholder, salutation ("Dear Hiring Manager,"), 3 body paragraphs, closing ("Sincerely,"), and the EXACT signature block provided below.
2.  **Paragraph 1 (Hook):** State the role applied for and express enthusiasm. Briefly connect the candidate's core expertise (e.g., derived from '{primary_theme}') to the role's main requirements. Target word count: {self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX} words.
3.  **Paragraph 2 (Proof):** Provide specific examples (drawing from experience snippets and keywords) demonstrating the candidate's ability to solve problems like "{problem}" and deliver solutions like "{solution}". Quantify achievements where possible. Weave in 2-3 differentiators naturally. Target word count: {self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX} words.
4.  **Paragraph 3 (Vision/Fit):** Reiterate interest, connect skills to the company's specific needs or goals (if inferable), and express excitement about the opportunity. Include a call to action (e.g., "eager to discuss"). Target word count: {self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX} words.
5.  **Signature:** Append the following signature block EXACTLY as shown, including line breaks (use two spaces at the end of each line before the newline):
{expected_signature}

CRITICAL:
1. Adhere strictly to the word count targets for each paragraph.
2. Ensure the exact signature block is appended correctly with forced line breaks.
3. Output ONLY the complete cover letter text. Do NOT use markdown fences like ```.

COVER LETTER:
"""
        try:
            # Use default reasoning, focus is on adherence to structure and content
            reasoning_config = ReasoningConfig.DEFAULT
            base_system = f"You are an expert executive ghostwriter crafting tailored cover letters."
            cover_letter_text = self._call_gemini_api(
                prompt, reasoning_config, "K.13", base_system,
                temperature_override=temperature_override
            )

            # --- Post-generation Structure Fixes ---
            fixed_text = cover_letter_text.strip()
            current_date = datetime.now().strftime("%B %d, %Y")
            recipient_placeholder = "Hiring Manager\n[Company Name]" # Simplified placeholder
            salutation = "Dear Hiring Manager,"
            closing = "Sincerely,"
            structure_fix_fails_date = False
            structure_fix_fails_signature = False

            # Ensure Date is present at the beginning
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text):
                 fixed_text = f"{current_date}\n\n{fixed_text}"
                 logging.warning("K.13: Added missing date.")
            # Ensure Recipient Placeholder is present after date
            if recipient_placeholder not in fixed_text:
                 # Attempt to insert it after the date block
                 fixed_text = re.sub(r"(\w+ \d{1,2}, \d{4}\n*\s*)", rf"\1\n{recipient_placeholder}\n\n", fixed_text, count=1)
                 if recipient_placeholder not in fixed_text: # If insertion failed
                      logging.error("K.13: Failed to insert recipient placeholder.")
                      structure_fix_fails_date = True # Use this flag

            # Ensure Salutation is present after recipient
            if salutation not in fixed_text:
                # Attempt to insert after recipient block
                fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\n*\s*)", rf"\1\n{salutation}\n\n", fixed_text, count=1)
                if salutation not in fixed_text:
                     logging.error("K.13: Failed to insert salutation.")
                     structure_fix_fails_date = True

            # Ensure Closing is present before signature
            if closing not in fixed_text.split(expected_signature)[0]: # Check only before signature
                 # Attempt to insert before signature block
                 if expected_signature in fixed_text:
                     fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
                 else: # If signature is also missing, add both
                     fixed_text += f"\n\n{closing}\n\n{expected_signature}"
                 if closing not in fixed_text.split(expected_signature)[0]:
                      logging.error("K.13: Failed to insert closing.")
                      structure_fix_fails_signature = True # Use separate flag

            # Ensure Signature is present and correctly formatted at the end
            # Remove trailing whitespace before check
            fixed_text_stripped_end = '\n'.join(line.rstrip() for line in fixed_text.split('\n'))
            expected_sig_stripped_end = '\n'.join(line.rstrip() for line in expected_signature.split('\n'))

            if not fixed_text_stripped_end.endswith(expected_sig_stripped_end):
                 # Attempt to remove any trailing text and append the correct signature
                 pattern = re.escape(expected_sig_stripped_end.split('\n')[0]) # Use first line of expected sig as anchor
                 match = list(re.finditer(pattern, fixed_text_stripped_end))
                 if match: # If anchor found, replace from there
                     last_match_start = match[-1].start()
                     fixed_text = fixed_text[:last_match_start] + expected_signature
                 else: # If anchor not found, just append
                     fixed_text = fixed_text_stripped_end + "\n\n" + expected_signature
                 logging.warning("K.13: Corrected or appended signature block.")
                 # Re-check after attempting fix
                 fixed_text_stripped_end = '\n'.join(line.rstrip() for line in fixed_text.split('\n'))
                 if not fixed_text_stripped_end.endswith(expected_sig_stripped_end):
                      logging.error("K.13: Failed to fix signature block placement.")
                      structure_fix_fails_signature = True


            # Check for placeholder text (often indicates LLM failure)
            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text:
                raise HopExecutionError(f"K.13 generation failed (placeholder detected after fixes).")

            # Check flags and raise error if structure fixes failed critically
            if structure_fix_fails_date:
                raise HopExecutionError("K.13 failed critical structure fix (date/recipient/salutation).")
            if structure_fix_fails_signature:
                raise HopExecutionError("K.13 failed critical structure fix (closing/signature).")

            return fixed_text.strip() # Return the potentially fixed text

        except HopExecutionError as he:
            # Propagate API errors or structure fix errors
            logging.error(f"K.13 generation process failed: {he}")
            raise he
        except Exception as e:
            # Catch other unexpected errors
            logging.error(f"K.13 generation unexpected error: {e}", exc_info=True)
            raise HopExecutionError(f"K.13 generation failed: {e}") from e

# ============================================================================
# HOP-4: IMMUTABLE STAGING BUFFER
# ============================================================================

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

# Assuming necessary classes like ValidationResult, ValidationSeverity,
# ImmutableStagingBuffer are defined elsewhere.
# Also assuming COMPREHENSIVE_HYPHENATION_RULES is defined as provided.

class TextSanitizer:
    """
    v6.1: Comprehensive text sanitization engine.
    Applies rules for hyphenation, unicode, punctuation, and style.
    Now includes blocklists for dash-like and invisible characters.
    """

    # --- Blocklists Added ---
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
        self.rules = hyphenation_rules or COMPREHENSIVE_HYPHENATION_RULES
        # Ensure rule structure is valid
        if not isinstance(self.rules, dict) or 'rules' not in self.rules or \
           'unnatural_hyphens_remove' not in self.rules['rules'] or \
           'natural_hyphens_preserve' not in self.rules['rules']:
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
            return [ValidationResult(
                rule_id="R4.5-ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message="Staging buffer already locked before HOP-4.5"
            )], staging_buffer.data

        # Reset counts for this run
        for key in self.sanitization_counts:
            self.sanitization_counts[key] = 0
            
        sanitized_data = self._sanitize_dict_recursive(staging_buffer.data)

        total_fixes = sum(v for k, v in self.sanitization_counts.items() if 'preserved' not in k) # Sum actual fixes
        validation_results = [ValidationResult(
            rule_id="TEXT_SANITIZATION_COMPLETE", passed=True, severity=ValidationSeverity.INFO,
            message=f"Text sanitization complete: {total_fixes} total corrections. Preserved natural hyphens: {self.sanitization_counts['natural_hyphens_preserved']}. ({', '.join(f'{k}: {v}' for k, v in self.sanitization_counts.items() if v > 0)})"
        )]
        
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
        for rule in self.rules['rules']['unnatural_hyphens_remove']:
            count_before = text.count(rule['from'])
            if count_before > 0:
                text = text.replace(rule['from'], rule['to'])
                self.sanitization_counts['unnatural_hyphens_removed'] += count_before
                
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
        # Need to iterate carefully to check context
        sanitized_text_parts = []
        last_index = 0
        removed_hyphen_minus_count = 0
        preserved_hyphen_minus_count = 0

        # Find all words that *might* contain a hyphen
        potential_hyphenated_words = set()
        for match in self.POTENTIAL_HYPHEN_PATTERN.finditer(text):
             potential_hyphenated_words.add(match.group(0))

        # Check if these words are in the preserve list
        hyphens_to_preserve_in_words = set()
        for word in potential_hyphenated_words:
             if word in self.natural_hyphens_set:
                 hyphens_to_preserve_in_words.add(word)
                 # Count how many times this specific preserved word occurs
                 # Note: This might overcount if the word appears multiple times,
                 # but gives an estimate of preserved hyphens.
                 preserved_hyphen_minus_count += text.count(word)

        # Now remove U+002D *only if it's NOT part of a preserved word*
        # This is tricky with simple replace. Let's rebuild the string.
        final_text = ""
        current_pos = 0
        while current_pos < len(text):
            char = text[current_pos]
            if char == '-':
                # Check if this hyphen is part of a known preserved word starting nearby
                part_of_preserved = False
                for preserved_word in hyphens_to_preserve_in_words:
                    # Look backwards slightly to see if we're inside a preserved word
                    start_check = max(0, current_pos - len(preserved_word) + 1)
                    if text[start_check : current_pos + len(preserved_word) - (current_pos-start_check)].startswith(preserved_word):
                         part_of_preserved = True
                         break
                if not part_of_preserved:
                    # It's a U+002D not in a preserved word, remove it (skip adding it)
                    removed_hyphen_minus_count += 1
                else:
                    # It's part of a preserved word, keep it
                    final_text += char
            else:
                # Not a hyphen, keep the character
                final_text += char
            current_pos += 1
        
        text = final_text # Update text with hyphens potentially removed
        self.sanitization_counts['forbidden_hyphen_minus_removed'] = removed_hyphen_minus_count
        # This count might not be perfectly precise due to overlapping words, but it's an estimate.
        self.sanitization_counts['natural_hyphens_preserved'] = preserved_hyphen_minus_count

        # Placeholder for other potential sanitization steps (add functions as needed)
        # text = self._fix_punctuation(text)
        # text = self._remove_markdown(text)
        # text = self._simplify_jargon(text)
        # text = self._remove_fillers(text)

        return text

# ============================================================================
# UTILITY HELPER FUNCTIONS
# ============================================================================

def count_words_ms_word_style(text: str) -> int:
    """
    Counts words attempting to replicate MS Word behavior:
    - Keeps hyphenated words (e.g., "post-sales") as single words.
    - Ignores empty strings resulting from splitting.
    """
    if not text:
        return 0
    # Finds sequences of word characters (\w) possibly connected by hyphens (-)
    words = re.findall(r'\b[\w-]+\b', text)
    # Filter out potential empty strings or standalone hyphens caught by regex
    valid_words = [word for word in words if word and word != '-']
    return len(valid_words)

def count_words_in_list_ms_word_style(content_list: List[Any]) -> int:
    """Helper to count words in a list using the MS Word style counter."""
    return sum(count_words_ms_word_style(str(item)) for item in content_list)

def _count_sentences(text: str) -> int:
    """
    Helper to count sentences using a regex that handles common abbreviations.
    """
    if not text: return 0
    # Finds . ! ? that are not preceded by common titles or single capital letters.
    return len(re.findall(r'(?<!\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|vs|e\.g|i\.e))\.(?!\d)|[.!?]\s', text + " "))

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

def calculate_master_avg_bullet_length(master_resume: Dict) -> Dict[str, float]:
    """
    [GLOBAL UTILITY]
    Helper to calculate average bullet length for sections in master resume using MS Word style counting.
    """
    logging.info("Calculating Master Resume Average Bullet Lengths...")
    avg_lengths = {}
    # Corrected structure access based on MASTER_RESUME_JSON
    experience_sections = master_resume.get("professional_experience", [])
    # Defines which sections to average and which key ('bullet_pool' or 'highlights') contains the bullets
    experience_sections_to_avg = {
        "Unify": ("Unify Consulting", "bullet_pool"),
        "IBM": ("IBM", "bullet_pool"),
        "EY": ("Ernst & Young", "highlights"),
        "TraderSense": ("TraderSense", "highlights"), # Add TraderSense
        "EarlyCareer": ("Early Career Roles", "highlights"),
    }
    default_avg = 25.0 # Fallback average

    # Calculate average for each experience section defined above
    for key, (company_name_part, bullets_key) in experience_sections_to_avg.items():
        total_words = 0
        bullet_count = 0
        # Find the matching experience section in the master resume
        exp = next((e for e in experience_sections if company_name_part in e.get("company", "")), None)
        if exp:
            bullets = exp.get(bullets_key, [])
            # Ensure we only process strings
            str_bullets = [b for b in bullets if isinstance(b, str)]
            if str_bullets:
                # Sum words using the MS Word style counter
                total_words = sum(count_words_ms_word_style(b) for b in str_bullets)
                bullet_count = len(str_bullets)

        # Calculate average or use default if no bullets found
        calculated_avg = (total_words / bullet_count) if bullet_count > 0 else default_avg
        avg_lengths[key] = calculated_avg
        # Log the calculated average for this section
        logging.info(f"  - Master Avg for '{key}': {calculated_avg:.1f} words ({bullet_count} bullets)")

    # Calculate average for Competencies section
    competencies_list = master_resume.get("strategic_and_technical_competencies", [])
    competencies_strings = [c for c in competencies_list if isinstance(c, str)]
    calculated_avg_comp = (sum(count_words_ms_word_style(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0 # Specific default
    avg_lengths["Competencies"] = calculated_avg_comp
    # Log the calculated average for competencies
    logging.info(f"  - Master Avg for 'Competencies': {calculated_avg_comp:.1f} words ({len(competencies_strings)} items)")

    # Add a general default
    avg_lengths["Default"] = default_avg
    logging.info(f"  - Master Avg for 'Default': {default_avg:.1f} words")
    return avg_lengths

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================
from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data

class PreFlightValidator:

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.dup_detector = DuplicateDetector() # For cosine similarity
        self.constraints = ContentConstraintsConfig() # Centralized constraints
        self.signal_constraints = SignalControlConfig() # Signal control constraints

        # --- Rule to Section Mapping (Initialized via method) ---
        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()

        self._register_rules() # Must be called after constraints are set

    # Class constant for signal targets configuration (Unchanged)
    SECTION_SIGNAL_TARGETS_CONFIG = {
        # Label: (Enum, Min_Target, Max_Target, Weight, ReasoningConfig)
        "Headline": (ResumeSection.K0_HEADLINE, 0.70, 0.90, 0.05, ReasoningConfig.K0_HEADLINE_CONFIG),
        "Executive Summary": (ResumeSection.K1_EXECUTIVE_SUMMARY, 0.80, 0.90, 0.25, ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG),
        "Unify Overview": (ResumeSection.K5_UNIFY_OVERVIEW, 0.70, 0.90, 0.05, ReasoningConfig.K5_UNIFY_OVERVIEW_CONFIG),
        "Unify Bullets": (ResumeSection.K5_UNIFY_BULLETS, 0.70, 0.90, 0.20, ReasoningConfig.K5_UNIFY_BULLETS_CONFIG),
        "IBM Overview": (ResumeSection.K6_IBM_OVERVIEW, 0.60, 0.80, 0.05, ReasoningConfig.K6_IBM_OVERVIEW_CONFIG),
        "IBM Bullets": (ResumeSection.K6_IBM_BULLETS, 0.65, 0.85, 0.20, ReasoningConfig.K6_IBM_BULLETS_CONFIG),
        "EY Overview": (ResumeSection.K8_EY_OVERVIEW, 0.50, 0.70, 0.025, ReasoningConfig.K8_EY_OVERVIEW_CONFIG),
        "EY Bullets": (ResumeSection.K8_EY_BULLETS, 0.50, 0.70, 0.025, ReasoningConfig.K8_EY_BULLETS_CONFIG),
        "Early Career Overview": (ResumeSection.K9_EARLY_CAREER_OVERVIEW, 0.40, 0.60, 0.025, ReasoningConfig.K9_EARLY_CAREER_OVERVIEW_CONFIG),
        "Early Career Bullets": (ResumeSection.K9_EARLY_CAREER_BULLETS, 0.40, 0.60, 0.025, ReasoningConfig.K9_EARLY_CAREER_BULLETS_CONFIG),
        "Competencies": (ResumeSection.K10_COMPETENCIES, 0.85, 0.95, 0.10, ReasoningConfig.K10_COMPETENCIES_CONFIG),
    }

    # Bullet word count tolerance configuration (Unchanged)
    BULLET_WORD_COUNT_TOLERANCE = 0.20 # +/- 20%
    BULLET_WORD_COUNT_SECTIONS_TO_CHECK = [
        ResumeSection.K5_UNIFY_BULLETS,
        ResumeSection.K6_IBM_BULLETS,
        ResumeSection.K10_COMPETENCIES,
        ResumeSection.K8_EY_BULLETS,
        ResumeSection.K9_EARLY_CAREER_BULLETS,
    ]

    # Provenance split targets configuration (Unchanged)
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    # Consolidated Rules Configuration (Add new rule here)
    RULES_CONFIG = [
        # --- Word Count & Sentence Count Rules ---
        {
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_total_word_count",
            "error_message": "Total resume: {total_words} words (target: {min}-{max})"
        },
        {
            "rule_id": "VG_SENTENCE_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_k1_sentence_count",
            "error_message": "K.1: {sentence_count} sentences (target: {min}-{max})"
        },
         {
            "rule_id": "VG_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.CRITICAL,"category": "structure",
            "validator": "_validate_headline_word_count",
            "error_message": "K.0 Headline: {word_count} words (target: {min}-{max}). Headline: '{headline}'"
        },
        {
            "rule_id": "VG_BULLET_WORD_COUNT_TOLERANCE", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": "_validate_bullet_word_count_tolerance",
            "error_message": "Bullet word counts outside tolerance ({tolerance}%): {violations}"
        },
        # --- Distribution Rules ---
        {
            "rule_id": "WORD_DISTRIBUTION_UNIFY_IBM", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": "_validate_unify_ibm_distribution",
            "error_message": "Unify+IBM: {percent:.1f}% of total (target: {min}-{max}%)"
        },
        {
            "rule_id": "UNIFY_IBM_RATIO", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": "_validate_unify_ibm_ratio",
            "error_message": "Unify/IBM ratio: {ratio:.2f} (target: {min}-{max})"
        },
        # --- Structure & Formatting Rules ---
        {
            "rule_id": "BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_buffer_locked",
            "error_message": "Staging buffer must be locked before validation"
        },
        {
            "rule_id": "COVER_LETTER_SIGNATURE", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": "_validate_cover_letter_signature",
            "error_message": "Cover letter signature is missing or malformed."
        },
        {
            "rule_id": "VG_COVER_LETTER_FULL_STRUCTURE", "severity": ValidationSeverity.MEDIUM, "category": "structure",
            "validator": "_validate_cover_letter_full_structure",
            "error_message": "Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."
        },
        {
            "rule_id": "VG_COVER_LETTER_SIGNATURE_MULTILINE", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_cover_letter_signature_multiline",
            "error_message": "Cover letter signature is not rendering multi-line (check trailing spaces)."
        },
        {
            "rule_id": "VG_HEADLINE_NO_TITLES", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_headline_format_no_titles",
            "error_message": "K.0 Headline contains forbidden titles: {forbidden}. Headline: '{headline}'"
        },
        {
            "rule_id": "VG_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_headline_format_no_commas",
            "error_message": "K.0 Headline contains commas. Headline: '{headline}'"
        },
        {
            "rule_id": "VG_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_resume_header_h2",
            "error_message": "Resume headers not consistently H2: {failed_headers}"
        },
        {
            "rule_id": "VG_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_edu_certs_format",
            "error_message": "Education/Certification format error: {details}"
        },
        {
            "rule_id": "VG_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_experience_bullet_style",
            "error_message": "Experience bullets do not consistently use '* ': {details}"
        },
        {
            "rule_id": "VG_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_competencies_formatting",
            "error_message": "Competencies list not using '*' bullets: {details}"
        },
        {
            "rule_id": "VG_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_experience_render_format",
            "error_message": "Experience section formatting error: {details}"
        },
        # --- Content & Signal Rules ---
        {
            "rule_id": "CONTENT_NO_PLACEHOLDERS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_no_placeholders",
            "error_message": "Found placeholder text in content: {placeholders}"
        },
        {
            "rule_id": "VG_PER_SECTION_SIGNAL_SCORE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_per_section_signal",
            "error_message": "One or more sections are below minimum signal score: {failures}"
        },
        {
            "rule_id": "VG_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_k1_differentiator_range",
            "error_message": "K.1 Summary contains {found} differentiators (target: {min}-{max})."
        },
        {
            "rule_id": "VG_JD_KEYWORD_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_jd_keyword_range",
            "error_message": "Resume contains {found} JD keywords (target: {min}-{max})."
        },
        {
            "rule_id": "NARRATIVE_MINING_PRESENCE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_narrative_mining_presence",
            "error_message": "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."
        },
        {
            "rule_id": "VG_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_cover_letter_relevance_range",
            "error_message": "Cover letter relevance to JD is {similarity:.2f} (target: {min_sim}-{max_sim})."
        },
        {
            "rule_id": "COVER_LETTER_NARRATIVE_INTEGRITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_cover_letter_narrative",
            "error_message": "Cover letter may be missing narrative integrity. Hook: {hook}, Proof: {proof}, Vision: {vision}"
        },
        {
            "rule_id": "COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_cover_letter_fallback",
            "error_message": "Creative cover letter generation failed; fallback was used."
        },
        {
            "rule_id": "COVER_LETTER_STRUCTURE", "severity": ValidationSeverity.MEDIUM, "category": "content",
            "validator": "_validate_cover_letter_structure",
            "error_message": "Cover letter paragraph word counts are out of spec. P1: {p1_wc} ({p1_min}-{p1_max}), P2: {p2_wc} ({p2_min}-{p2_max}), P3: {p3_wc} ({p3_min}-{p3_max})"
        },
        {
            "rule_id": "VG_PROVENANCE_SPLIT_CHECK", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_provenance_split",
            "error_message": "Provenance split mismatch: {violations}"
        },
        {
            "rule_id": "VG_AUTHENTICITY_SIGNAL_CHECK", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_authenticity_signal",
            "error_message": "Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {details}"
        },
        # --- NEW RULE FOR EXEC SUMMARY SIMILARITY ---
        {
            "rule_id": "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_exec_summary_vs_sections",
            "error_message": "Executive Summary similarity to sections exceeds threshold: {failures}"
        },
    ]

    def _initialize_rule_map(self) -> Dict[str, Union[ResumeSection, str]]:
        """
        Creates the mapping of Rule IDs to the ResumeSection they govern.
        Uses a special string "GLOBAL" for rules that affect the whole document.
        """
        rule_map = {
            # Global Rules (affect everything or multiple sections)
            "VG_TOTAL_WORD_COUNT": "GLOBAL",
            "WORD_DISTRIBUTION_UNIFY_IBM": "GLOBAL", # Affects K5/K6, retry both
            "UNIFY_IBM_RATIO": "GLOBAL", # Affects K5/K6, retry both
            "VG_JD_KEYWORD_RANGE": "GLOBAL",
            "VG_AUTHENTICITY_SIGNAL_CHECK": "GLOBAL",
            "NARRATIVE_MINING_PRESENCE": "GLOBAL", # Not a content rule, but a HOP-0 check
            "CONTENT_NO_PLACEHOLDERS": "GLOBAL", # Could be anywhere
            "BUFFER_LOCK_STATUS": "GLOBAL", # Workflow rule
            # --- Placeholder / Visual Rules (Not linked to generation) ---
            "VG_RESUME_HEADER_H2": "VISUAL",
            "VG_EDU_CERTS_FORMAT": "VISUAL",
            "VG_EXPERIENCE_BULLET_STYLE": "VISUAL",
            "VG_COMPETENCIES_FORMATTING": "VISUAL",
            "VG_EXPERIENCE_RENDER_FORMAT": "VISUAL",
            # --- Headline (K.0) ---
            "VG_HEADLINE_WORD_COUNT": ResumeSection.K0_HEADLINE,
            "VG_HEADLINE_NO_TITLES": ResumeSection.K0_HEADLINE,
            "VG_HEADLINE_NO_COMMAS": ResumeSection.K0_HEADLINE,
            "STRUCTURE_K0_HEADLINE_PRESENT": ResumeSection.K0_HEADLINE,
            # --- Executive Summary (K.1) ---
            "VG_SENTENCE_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY": ResumeSection.K1_EXECUTIVE_SUMMARY, # <-- Map new rule to K.1
            # --- Skills (K.2) ---
            "STRUCTURE_K2_SKILLS_PRESENT": ResumeSection.K2_SKILLS,
            # --- Unify (K.5) ---
            "STRUCTURE_K5_UNIFY_BULLETS_PRESENT": ResumeSection.K5_UNIFY_BULLETS,
            "STRUCTURE_K5_UNIFY_OVERVIEW_PRESENT": ResumeSection.K5_UNIFY_OVERVIEW,
            # --- IBM (K.6) ---
            "STRUCTURE_K6_IBM_BULLETS_PRESENT": ResumeSection.K6_IBM_BULLETS,
            "STRUCTURE_K6_IBM_OVERVIEW_PRESENT": ResumeSection.K6_IBM_OVERVIEW,
            # --- EY (K.8) ---
            "STRUCTURE_K8_EY_BULLETS_PRESENT": ResumeSection.K8_EY_BULLETS,
            "STRUCTURE_K8_EY_OVERVIEW_PRESENT": ResumeSection.K8_EY_OVERVIEW,
            # --- Early Career (K.9) ---
            "STRUCTURE_K9_EARLY_CAREER_BULLETS_PRESENT": ResumeSection.K9_EARLY_CAREER_BULLETS,
            "STRUCTURE_K9_EARLY_CAREER_OVERVIEW_PRESENT": ResumeSection.K9_EARLY_CAREER_OVERVIEW,
            # --- Competencies (K.10) ---
            "STRUCTURE_K10_COMPETENCIES_PRESENT": ResumeSection.K10_COMPETENCIES,
            # --- Cover Letter (K.13) ---
            "COVER_LETTER_SIGNATURE": ResumeSection.K13_COVER_LETTER,
            "VG_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K13_COVER_LETTER,
            "VG_COVER_LETTER_SIGNATURE_MULTILINE": ResumeSection.K13_COVER_LETTER,
            "VG_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_STRUCTURE": ResumeSection.K13_COVER_LETTER,
            "STRUCTURE_K13_COVER_LETTER_PRESENT": ResumeSection.K13_COVER_LETTER,

            # --- Complex Rules (Handled in `validate` method) ---
            "VG_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION",
            "VG_BULLET_WORD_COUNT_TOLERANCE": "COMPLEX_PER_SECTION",
            "VG_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION",
        }

        # Add simple structure rules
        for section in ResumeSection:
             rule_id = f"STRUCTURE_{section.name}_PRESENT"
             if rule_id not in rule_map:
                 # Map all structure rules, even for copied sections
                 rule_map[rule_id] = section

        return rule_map

    def _register_rules(self):
        """Creates and registers all pre-flight validation rules."""
        for config in self.RULES_CONFIG:
            validator_ref = config["validator"]
            if isinstance(validator_ref, str):
                if hasattr(self, validator_ref):
                    validator_func = getattr(self, validator_ref)
                else:
                    logging.error(f"AttributeError during rule registration: Validator method '{validator_ref}' not found in {self.__class__.__name__} for rule {config['rule_id']}")
                    raise AttributeError(f"Validator method '{validator_ref}' not found in {self.__class__.__name__} for rule {config['rule_id']}")
            elif callable(validator_ref):
                 validator_func = validator_ref
            else:
                 raise TypeError(f"Invalid validator type for rule {config['rule_id']}: {type(validator_ref)}")

            # Use defaultdict to handle missing keys gracefully in error message formatting
            def create_error_message_lambda(template):
                expected_args = re.findall(r'\{(\w+)\}', template)
                format_args = {}
                if "tolerance" in expected_args:
                    format_args["tolerance"] = self.BULLET_WORD_COUNT_TOLERANCE * 100
                # Use a defaultdict for formatting to avoid KeyErrors if details are missing
                return lambda data: template.format_map(defaultdict(lambda: 'N/A', **data.get("error_details", {}), **format_args))

            error_message_template = str(config["error_message"])
            error_message_lambda = create_error_message_lambda(error_message_template)

            rule = ValidationRule(
                rule_id=config["rule_id"],
                severity=config["severity"],
                category=config["category"],
                validator=validator_func,
                error_message=error_message_lambda
            )
            self.engine.register_rule(rule)

        # Register rules for required sections dynamically
        required_sections = [
            ResumeSection.K0_NAME, ResumeSection.K0_HEADLINE, ResumeSection.K0_CONTACT,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K5_UNIFY_BULLETS,
            ResumeSection.K5_UNIFY_OVERVIEW, ResumeSection.K6_IBM_BULLETS,
            ResumeSection.K6_IBM_OVERVIEW,
            ResumeSection.K7_TRADERSENSE_BULLETS,
            ResumeSection.K7_TRADERSENSE_OVERVIEW,
            ResumeSection.K8_EY_BULLETS,
            ResumeSection.K8_EY_OVERVIEW,
            ResumeSection.K9_EARLY_CAREER_BULLETS,
            ResumeSection.K9_EARLY_CAREER_OVERVIEW,
            ResumeSection.K10_COMPETENCIES,
            ResumeSection.K11_EDUCATION, ResumeSection.K12_CERTIFICATIONS,
            ResumeSection.K13_COVER_LETTER,
        ]
        for section in required_sections:
            rule_id = f"STRUCTURE_{section.name}_PRESENT"
            rule = ValidationRule(
                rule_id=rule_id,
                severity=ValidationSeverity.CRITICAL,
                validator=lambda d, s=section: (
                    d['staging_buffer'].get(s.value) is not None and
                    ( (isinstance(d['staging_buffer'].get(s.value), str) and d['staging_buffer'].get(s.value).strip()) or
                      (isinstance(d['staging_buffer'].get(s.value), list) and d['staging_buffer'].get(s.value)) or
                      (isinstance(d['staging_buffer'].get(s.value), dict) and d['staging_buffer'].get(s.value))
                    )
                ),
                error_message=f"{section.value} is missing or empty.",
                category="structure"
            )
            self.engine.register_rule(rule)

    # --- VALIDATE METHOD ---
    def validate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        sections_under_test: Optional[Set[ResumeSection]] = None
    ) -> Tuple[List[ValidationResult], bool, Set[ResumeSection]]:
        """
        [REFACTORED]
        Validates the staging buffer and returns which sections failed.

        Args:
            staging_buffer: The buffer with all *current* content (including locked-in).
            thematic_analysis: The HOP-0 analysis.
            job_description: The JD text.
            sections_under_test: The set of sections that were *newly generated*
                                 in this attempt. This is used to attribute
                                 GLOBAL rule failures.

        Returns:
            Tuple of (
                all_validation_results: List[ValidationResult],
                all_passed: bool (True if no HIGH or CRITICAL failures),
                failed_sections: Set[ResumeSection] (Sections to be re-run)
            )
        """
        actual_counts = {}
        total_words = 0

        # Count words for each section in the buffer using MS WORD STYLE
        for section_id, content in staging_buffer.data.items():
            if content is None:
                actual_counts[section_id] = 0
                continue
            if isinstance(content, str):
                word_count = count_words_ms_word_style(content)
            elif isinstance(content, list):
                if content and isinstance(content[0], dict) and ('text' in content[0] or 'bullet_text' in content[0]): # List of bullet dicts
                     word_count = sum(item.get('word_count', count_words_ms_word_style(item.get('text', item.get('bullet_text','')))) for item in content)
                else:
                    word_count = count_words_in_list_ms_word_style(content)
            elif isinstance(content, dict):
                 word_count = count_words_ms_word_style(json.dumps(content))
            else:
                word_count = 0

            actual_counts[section_id] = word_count
            total_words += word_count
        actual_counts["TOTAL"] = total_words

        section_averages = calculate_master_avg_bullet_length(self.master_resume)

        data = self._prepare_validation_data(
            staging_buffer, thematic_analysis, job_description, actual_counts, section_averages
        )

        # Execute validation
        validation_results = self.engine.validate(data)
        all_passed = not self.engine.has_high_or_critical_failures(validation_results)

        # --- Map failures back to sections ---
        failed_sections = set()
        failed_global_rules = False

        failures = self.engine.get_failed_validations(validation_results)

        for vr in failures:
            if vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
                continue # Ignore LOW/MEDIUM failures for retry logic

            section_or_flag = self.RULE_TO_SECTION_MAP.get(vr.rule_id)

            if isinstance(section_or_flag, ResumeSection):
                failed_sections.add(section_or_flag)

            elif section_or_flag == "GLOBAL":
                failed_global_rules = True
                logging.warning(f"Global rule failed: {vr.rule_id}. This will trigger a retry of all non-locked sections.")

            elif section_or_flag == "COMPLEX_PER_SECTION":
                # These rules add their details about *which* sections failed
                if vr.details and "failed_sections" in vr.details and isinstance(vr.details["failed_sections"], set):
                    failed_sections.update(vr.details["failed_sections"])
                else:
                    logging.warning(f"Complex rule {vr.rule_id} failed but did not provide failed_sections set in details.")


            elif vr.rule_id.startswith("STRUCTURE_"):
                # Handle dynamic structure rules
                try:
                    section_name = vr.rule_id.replace("STRUCTURE_", "").replace("_PRESENT", "")
                    section_enum = ResumeSection[section_name]
                    failed_sections.add(section_enum)
                except KeyError:
                    logging.warning(f"Could not map structure rule {vr.rule_id} to an enum.")

        # If a global rule failed, all sections that were *just tested* must be re-run
        if failed_global_rules and sections_under_test:
            logging.info(f"Adding all {len(sections_under_test)} sections under test to retry list due to GLOBAL rule failure.")
            failed_sections.update(sections_under_test)

        return validation_results, all_passed, failed_sections

    def _prepare_validation_data(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        actual_counts: Dict,
        section_averages: Dict
    ) -> Dict:
        """Prepares a dictionary of data needed by the validation rules."""
        unify_words = actual_counts.get(ResumeSection.K5_UNIFY_OVERVIEW.value, 0) + actual_counts.get(ResumeSection.K5_UNIFY_BULLETS.value, 0)
        ibm_words = actual_counts.get(ResumeSection.K6_IBM_OVERVIEW.value, 0) + actual_counts.get(ResumeSection.K6_IBM_BULLETS.value, 0)
        total_words = actual_counts.get("TOTAL", 1) # Avoid division by zero

        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})

        jd_keywords_tracked = []
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Use differentiator_keywords_raw which is the full list before ranking/weighting
            jd_keywords_tracked = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords_raw', [])
            if not isinstance(jd_keywords_tracked, list): jd_keywords_tracked = [] # Ensure it's a list
        else:
             logging.warning("Competitive intelligence missing or empty in thematic analysis during validation data prep.")

        try:
            # Use deepcopy of buffer data to avoid issues if buffer gets modified elsewhere unexpectedly
            # Although it's supposed to be immutable, this adds safety.
            buffer_data_copy = staging_buffer.data # Assuming .data returns a deep copy
            buffer_str = json.dumps(buffer_data_copy).lower()
        except (TypeError, Exception) as e:
            logging.error(f"Error serializing staging buffer data: {e}")
            buffer_str = ""

        # Ensure keywords are strings before comparison
        jd_keywords_found_list = [
            kw for kw in jd_keywords_tracked
            if isinstance(kw, str) and kw and kw.lower() in buffer_str
        ] if buffer_str else []


        cover_letter_text = staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        # Ensure calculation happens only if both texts are non-empty
        cover_letter_jd_similarity = self.dup_detector._calculate_cosine_similarity(
            cover_letter_text,
            job_description
        ) if cover_letter_text and job_description else 0.0

        top_differentiators = []
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Use get_top_differentiators which accesses the ranked list
             try:
                 top_differentiators = thematic_analysis.competitive_intelligence.get_top_differentiators(self.signal_constraints.K1_MAX_DIFFERENTIATORS)
                 if not isinstance(top_differentiators, list): top_differentiators = [] # Ensure list
             except AttributeError:
                  top_differentiators = [] # Handle case where method might be missing


        return {
            "staging_buffer": staging_buffer, # Pass the buffer object itself
            "thematic_analysis": thematic_analysis,
            "total_words": total_words,
            "unify_words": unify_words,
            "ibm_words": ibm_words,
            "unify_ibm_percent": ((unify_words + ibm_words) / total_words * 100) if total_words > 0 else 0,
            "differentiators": top_differentiators,
            "expected_signature": COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', ''),
                email=contact_info.get('email', ''),
                phone=contact_info.get('phone', ''),
                linkedin=contact_info.get('linkedin', '')
            ).strip(),
            "jd_keywords_tracked": jd_keywords_tracked, # The full raw list
            "jd_keywords_found": jd_keywords_found_list, # List of keywords found in buffer
            "cover_letter_jd_similarity": cover_letter_jd_similarity,
            "section_averages": section_averages,
        }

    # --- Validation Helper Methods ---

    def _validate_total_word_count(self, data: Dict) -> bool:
        data["error_details"] = {
            "total_words": data['total_words'],
            "min": self.constraints.TOTAL_WORD_COUNT_MIN,
            "max": self.constraints.TOTAL_WORD_COUNT_MAX
        }
        return self.constraints.TOTAL_WORD_COUNT_MIN <= data['total_words'] <= self.constraints.TOTAL_WORD_COUNT_MAX

    def _validate_k1_sentence_count(self, data: Dict) -> bool:
        summary_text = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        sentence_count = _count_sentences(summary_text)
        data["error_details"] = {
            "sentence_count": sentence_count,
            "min": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
            "max": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        }
        is_valid = self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN <= sentence_count <= self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        if not is_valid:
            logging.warning(f"K.1 Sentence Count VALIDATION FAILED: Target={self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}, Actual={sentence_count}")
        return is_valid

    def _validate_unify_ibm_distribution(self, data: Dict) -> bool:
        min_pct = self.constraints.UNIFY_IBM_COMBINED_PERCENT_MIN
        max_pct = self.constraints.UNIFY_IBM_COMBINED_PERCENT_MAX
        data["error_details"] = {"percent": data['unify_ibm_percent'], "min": min_pct, "max": max_pct}
        return min_pct <= data['unify_ibm_percent'] <= max_pct

    def _validate_unify_ibm_ratio(self, data: Dict) -> bool:
        min_ratio = self.constraints.UNIFY_IBM_RATIO_MIN
        max_ratio = self.constraints.UNIFY_IBM_RATIO_MAX
        if data['ibm_words'] == 0:
            # If IBM has 0 words, the ratio is undefined/infinite. Fail the check.
            data["error_details"] = {"ratio": "Infinity (IBM words = 0)", "min": min_ratio, "max": max_ratio}
            return False
        ratio = data['unify_words'] / data['ibm_words']
        # Round ratio for consistent reporting in error details
        data["error_details"] = {"ratio": round(ratio, 2), "min": min_ratio, "max": max_ratio}
        return min_ratio <= ratio <= max_ratio


    def _validate_buffer_locked(self, data: Dict) -> bool:
        return data['staging_buffer'].is_locked()

    def _validate_cover_letter_signature(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        # Ensure expected_signature exists before checking endswith
        expected_sig = data.get('expected_signature')
        return bool(expected_sig and cover_letter.strip().endswith(expected_sig))


    def _validate_no_placeholders(self, data: Dict) -> bool:
        try:
            # Serialize the buffer data safely
            buffer_data = data['staging_buffer'].data # Get a copy
            buffer_str = json.dumps(buffer_data)
            # Find placeholders (case-insensitive)
            placeholders = re.findall(r'(\[placeholder.*?\])', buffer_str, re.IGNORECASE)
            if placeholders:
                unique_placeholders = list(set(placeholders))
                data["error_details"] = {"placeholders": unique_placeholders[:5]} # Report up to 5 unique placeholders found
                return False
            return True
        except (TypeError, Exception) as e:
            logging.error(f"Error checking for placeholders: {e}")
            data["error_details"] = {"placeholders": [f"Error during check: {e}"]}
            return False # Fail if serialization or regex fails

    def _validate_per_section_signal(self, data: Dict) -> bool:
        """
        [REFACTORED]
        VG_PER_SECTION_SIGNAL_SCORE: Checks if all generated sections meet min signal score.
        Adds failed sections to error_details.
        """
        staging_buffer = data['staging_buffer']
        thematic_analysis = data['thematic_analysis']
        if not thematic_analysis:
             data["error_details"] = {
                 "failures": "Thematic analysis object is missing.",
                 "failed_sections": {cfg[0] for cfg in self.SECTION_SIGNAL_TARGETS_CONFIG.values()} # Fail all targeted sections
             }
             return False

        failures = []
        failed_sections = set() # Store ResumeSection enums

        for label, (section_enum, target_min_score, _, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = staging_buffer.get(section_enum.value)

            # Check only if content exists for the section
            if content is not None:
                try:
                    score = calculate_signal_score(content, thematic_analysis)
                    # Use >= for comparison as score needs to meet or exceed the minimum
                    if score < target_min_score:
                        failures.append(f"{label}: {score:.1%} (Target: >={target_min_score:.0%})")
                        failed_sections.add(section_enum)
                except Exception as e:
                    logging.error(f"Error calculating signal score for {label}: {e}", exc_info=True)
                    failures.append(f"{label}: Error calculating score ({e})")
                    failed_sections.add(section_enum) # Fail section if score calculation errors out
            else:
                # Log sections that are expected but missing content (might indicate earlier failure)
                # Don't fail this *specific* rule for missing content, let STRUCTURE rule handle it.
                logging.debug(f"Signal score check skipped for {label}: Content not found in buffer.")


        if failures:
            data["error_details"] = {
                "failures": "; ".join(failures),
                "failed_sections": failed_sections # Store the set of failed ResumeSection enums
            }
            return False

        return True


    def _validate_k1_differentiator_range(self, data: Dict) -> bool:
        MIN_DIFF = self.constraints.K1_MIN_DIFFERENTIATORS
        MAX_DIFF = self.signal_constraints.K1_MAX_DIFFERENTIATORS
        differentiators = data.get('differentiators', []) # Should be the top N ranked list
        if not isinstance(differentiators, list): differentiators = [] # Ensure list

        summary = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        if not summary:
             data["error_details"] = {"found": 0, "min": MIN_DIFF, "max": MAX_DIFF, "message": "Exec Summary missing."}
             return False # Fail if summary is missing

        # Count how many of the top differentiators appear in the summary
        found_count = sum(1 for kw in differentiators if isinstance(kw, str) and kw.lower() in summary)

        data["error_details"] = {"found": found_count, "min": MIN_DIFF, "max": MAX_DIFF}
        return MIN_DIFF <= found_count <= MAX_DIFF


    def _validate_jd_keyword_range(self, data: Dict) -> bool:
        MIN_KW = self.constraints.MIN_JD_KEYWORDS
        MAX_KW = self.signal_constraints.RESUME_MAX_JD_KEYWORDS
        # Use the count of keywords found in the buffer
        found_count = len(data.get('jd_keywords_found', []))
        data["error_details"] = {"found": found_count, "min": MIN_KW, "max": MAX_KW}
        return MIN_KW <= found_count <= MAX_KW


    def _validate_narrative_mining_presence(self, data: Dict) -> bool:
        thematic_analysis = data.get('thematic_analysis')
        if not thematic_analysis:
             return False # Cannot validate if analysis object is missing

        # Check if the attribute exists first
        if not hasattr(thematic_analysis, 'problem_solution_narratives'):
             logging.warning("ThematicAnalysis object missing 'problem_solution_narratives' attribute.")
             return False

        narratives = thematic_analysis.problem_solution_narratives # Now safe to access

        # Check if it's a dictionary and has the required keys with non-empty lists
        return (
            isinstance(narratives, dict) and
            isinstance(narratives.get("common_problems"), list) and
            len(narratives.get("common_problems", [])) > 0 and
            isinstance(narratives.get("solution_patterns"), list) and
            len(narratives.get("solution_patterns", [])) > 0
        )

    def _validate_cover_letter_relevance_range(self, data: Dict) -> bool:
        MIN_SIM = self.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD
        MAX_SIM = self.signal_constraints.CL_MAX_JD_SIMILARITY
        similarity = data.get('cover_letter_jd_similarity', 0.0)
        data["error_details"] = {"similarity": similarity, "min_sim": MIN_SIM, "max_sim": MAX_SIM}
        # Similarity must be within the range [MIN_SIM, MAX_SIM] inclusive
        return MIN_SIM <= similarity <= MAX_SIM


    def _validate_cover_letter_narrative(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        thematic_analysis = data.get('thematic_analysis')

        # Basic checks for presence of required data
        if not cover_letter or not thematic_analysis: return False
        if not hasattr(thematic_analysis, 'primary_theme') or not thematic_analysis.primary_theme: return False

        primary_theme = thematic_analysis.primary_theme.get('name', 'default_theme')
        differentiators = data.get('differentiators', []) or []
        # Ensure differentiators are strings for comparison
        differentiators = [str(d) for d in differentiators if d]

        # Split cover letter into paragraphs (assuming double newline separator)
        paragraphs = [p.strip() for p in cover_letter.split('\n\n') if p.strip()]

        # Check indices based on standard letter format (Date, Recipient, Salutation, P1, P2, P3, Closing, Signature block might span multiple lines)
        # We expect P1 at index 3, P2 at 4, P3 at 5
        if len(paragraphs) < 6:
             data["error_details"] = {"hook": False, "proof": False, "vision": False, "message": f"Expected at least 6 paragraphs/blocks, found {len(paragraphs)}"}
             return False

        p1 = paragraphs[3].lower() # Paragraph 1 (Hook)
        p2 = paragraphs[4].lower() # Paragraph 2 (Proof)
        p3 = paragraphs[5].lower() # Paragraph 3 (Vision/Fit)

        # Check Hook: Must mention primary theme or express interest
        hook_pass = primary_theme.lower() in p1 or "interest in the" in p1 or "apply for the role" in p1

        # Check Proof: Should mention differentiators OR common achievement language
        proof_pass = any(kw.lower() in p2 for kw in differentiators) or "resulted in" in p2 or "achieved" in p2 or "experience in" in p2 or "demonstrated" in p2

        # Check Vision/Fit: Should express excitement, mention opportunity, or call to action
        vision_pass = "excited" in p3 or "opportunity" in p3 or "discuss" in p3 or "contribute" in p3 or "look forward" in p3

        data["error_details"] = {"hook": hook_pass, "proof": proof_pass, "vision": vision_pass}
        return hook_pass and proof_pass and vision_pass


    def _validate_cover_letter_fallback(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        # Check for the specific fallback phrase used in _generate_k13_cover_letter's fallback logic
        # If the generation ever fully failed and used a hardcoded fallback, this would catch it.
        # Currently, the K13 generation fails fast, so this might always pass unless fallback logic is re-introduced.
        return "track record of measurable AI transformation" not in cover_letter


    def _validate_cover_letter_structure(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        if not cover_letter: return False # Fail if CL is missing

        paragraphs = [p.strip() for p in cover_letter.split('\n\n') if p.strip()]
        # Expected indices for paragraphs P1, P2, P3 after Date, Recipient, Salutation
        p1_idx, p2_idx, p3_idx = 3, 4, 5

        # Check if enough paragraphs exist
        if len(paragraphs) <= max(p1_idx, p2_idx, p3_idx):
            data["error_details"] = {
                "p1_wc": 0, "p2_wc": 0, "p3_wc": 0,
                "p1_min": self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
                "p2_min": self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
                "p3_min": self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
                "message": f"Insufficient paragraphs found ({len(paragraphs)})."
            }
            return False

        # Calculate word counts for the expected paragraphs
        p1_wc = count_words_ms_word_style(paragraphs[p1_idx])
        p2_wc = count_words_ms_word_style(paragraphs[p2_idx])
        p3_wc = count_words_ms_word_style(paragraphs[p3_idx])

        # Store details for error message formatting
        data["error_details"] = {
            "p1_wc": p1_wc, "p1_min": self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
        }

        # Check each paragraph against its constraints
        p1_valid = self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN <= p1_wc <= self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX
        p2_valid = self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN <= p2_wc <= self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX
        p3_valid = self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN <= p3_wc <= self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX

        return p1_valid and p2_valid and p3_valid

    def _validate_cover_letter_full_structure(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_signature_block = data.get('expected_signature', '') # Get expected sig from prep data
        if not cover_letter or not expected_signature_block: return False

        # Check for components using regex for flexibility with whitespace/newlines
        has_date = bool(re.match(r"\w+ \d{1,2}, \d{4}", cover_letter.strip()))
        # Check for recipient block (allows slight variations in spacing)
        has_recipient = bool(re.search(r"Hiring Manager\s+\[Company Name\]", cover_letter))
        # Check for salutation
        has_salutation = "Dear Hiring Manager," in cover_letter
        # Check for closing
        has_closing = "Sincerely," in cover_letter
        # Check for exact signature block presence
        has_signature = expected_signature_block in cover_letter

        # Check for 3 body paragraphs between salutation and closing
        body_match = re.search(r"Dear Hiring Manager,\s*(.*?)\s*Sincerely,", cover_letter, re.DOTALL)
        # Count paragraphs separated by double newlines (or more) in the extracted body
        body_paras_count = len(re.split(r'\n\s*\n', body_match.group(1).strip())) if body_match else 0
        has_3_body_paras = (body_paras_count == 3)

        return has_date and has_recipient and has_salutation and has_3_body_paras and has_closing and has_signature


    def _validate_cover_letter_signature_multiline(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_signature_block = data.get('expected_signature', '')
        if not expected_signature_block: return False

        # Check if the exact expected block is present
        if expected_signature_block not in cover_letter:
            return False

        # Check if the signature block itself contains newlines (indicating multi-line)
        # This assumes the template correctly forces newlines (e.g., using double spaces in Markdown)
        return '\n' in expected_signature_block


    def _validate_headline_word_count(self, data: Dict) -> bool:
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        word_count = count_words_ms_word_style(headline)
        data["error_details"] = {
            "word_count": word_count,
            "min": self.constraints.HEADLINE_WORD_COUNT_MIN,
            "max": self.constraints.HEADLINE_WORD_COUNT_MAX,
            "headline": headline # Include headline text in details
        }
        return self.constraints.HEADLINE_WORD_COUNT_MIN <= word_count <= self.constraints.HEADLINE_WORD_COUNT_MAX

    def _validate_headline_format_no_titles(self, data: Dict) -> bool:
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '').lower()
        forbidden_titles = ['vp', 'vice president', 'director', 'manager', 'chief', 'head', 'lead', 'principal', 'senior', 'c-suite', 'executive']
        # Use word boundaries to avoid matching parts of words (e.g., 'chief' in 'chiefly')
        found_forbidden = [t for t in forbidden_titles if re.search(r'\b' + re.escape(t) + r'\b', headline)]
        data["error_details"] = {"headline": headline, "forbidden": found_forbidden}
        return not found_forbidden # Return True if list is empty (no forbidden titles found)

    def _validate_headline_format_no_commas(self, data: Dict) -> bool:
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        data["error_details"] = {"headline": headline}
        return ',' not in headline


    # --- Placeholder validation methods for rules checked during rendering ---
    # These return True as the actual check happens later or is implicitly covered.
    def _validate_resume_header_h2(self, data: Dict) -> bool:
        data["error_details"] = {"failed_headers": ["Checked during rendering/QA-14"]}
        return True

    def _validate_edu_certs_format(self, data: Dict) -> bool:
        data["error_details"] = {"details": "Checked during rendering/QA-14"}
        return True

    def _validate_experience_bullet_style(self, data: Dict) -> bool:
        data["error_details"] = {"details": "Checked during rendering/QA-14"}
        return True

    def _validate_competencies_formatting(self, data: Dict) -> bool:
        data["error_details"] = {"details": "Checked during rendering/QA-14"}
        return True

    def _validate_experience_render_format(self, data: Dict) -> bool:
        data["error_details"] = {"details": "Checked during rendering/QA-14"}
        return True

    def _validate_bullet_word_count_tolerance(self, data: Dict) -> bool:
        """
        [REFACTORED]
        VG_BULLET_WORD_COUNT_TOLERANCE: Checks individual bullet word counts
        against master averages +/- tolerance. Adds failed sections to error_details.
        """
        all_bullets_valid = True
        violations = []
        failed_sections = set() # Store ResumeSection enums

        # Use pre-calculated averages passed in the data dictionary
        averages = data.get('section_averages')
        if not averages:
            logging.error("Master average bullet lengths not provided to validator. Skipping tolerance check.")
            data["error_details"] = {"violations": ["Master averages missing."], "failed_sections": set()}
            return False # Fail if averages are missing

        staging_buffer = data['staging_buffer']

        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            # Determine the correct key to look up the average length
            avg_key = "Default" # Fallback key
            if section_enum == ResumeSection.K5_UNIFY_BULLETS: avg_key = "Unify"
            elif section_enum == ResumeSection.K6_IBM_BULLETS: avg_key = "IBM"
            elif section_enum == ResumeSection.K10_COMPETENCIES: avg_key = "Competencies"
            elif section_enum == ResumeSection.K8_EY_BULLETS: avg_key = "EY"
            elif section_enum == ResumeSection.K9_EARLY_CAREER_BULLETS: avg_key = "EarlyCareer"

            avg_wc = averages.get(avg_key)
            # Check if average exists and is valid
            if avg_wc is None or avg_wc <= 0:
                logging.warning(f"Skipping bullet tolerance for {section_key}: Invalid or missing average length ({avg_wc}) for key '{avg_key}'")
                continue # Skip section if average isn't usable

            # Calculate min/max targets based on average and tolerance
            min_wc = round(avg_wc * (1 - self.BULLET_WORD_COUNT_TOLERANCE))
            max_wc = round(avg_wc * (1 + self.BULLET_WORD_COUNT_TOLERANCE))

            bullets = staging_buffer.get(section_key, [])
            # Ensure bullets data is a list before iterating
            if not isinstance(bullets, list):
                 logging.warning(f"Data for {section_key} is not a list ({type(bullets)}), skipping bullet tolerance check.")
                 continue

            for i, bullet in enumerate(bullets):
                actual_wc = 0
                bullet_text = "" # For error message context
                # Handle both dict and string bullet formats
                if isinstance(bullet, dict):
                    # Prefer 'text' (final), fallback to 'bullet_text' (original)
                    bullet_text = bullet.get('text', bullet.get('bullet_text',''))
                    # Use pre-calculated 'word_count' if available, else calculate
                    actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str):
                    bullet_text = bullet
                    actual_wc = count_words_ms_word_style(bullet_text)
                else:
                    # Skip unexpected item types
                    logging.warning(f"Unexpected item type in {section_key}[{i}]: {type(bullet)}. Skipping tolerance check.")
                    continue

                # Check if the actual word count is within the target range
                if not (min_wc <= actual_wc <= max_wc):
                    all_bullets_valid = False
                    violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc} based on avg {avg_wc:.1f})")
                    failed_sections.add(section_enum) # Add the section enum to the failed set

        # Populate error details if any violations occurred
        if not all_bullets_valid:
            data["error_details"] = {
                "violations": violations[:5], # Report first 5 violations
                "failed_sections": failed_sections # Store the set of failed ResumeSection enums
            }
        return all_bullets_valid

    def _validate_provenance_split(self, data: Dict) -> bool:
        """
        [REFACTORED]
        VG_PROVENANCE_SPLIT_CHECK: Checks if bullet provenance matches target splits.
        Adds failed sections to error_details.
        """
        all_splits_valid = True
        violations = []
        failed_sections = set() # Store ResumeSection enums
        staging_buffer = data['staging_buffer']

        for section_enum, target_split in self.PROVENANCE_SPLIT_TARGETS.items():
            section_key = section_enum.value
            bullets = staging_buffer.get(section_key, [])
            # Ensure bullets data is a list
            if not isinstance(bullets, list):
                logging.warning(f"Provenance check skipped for {section_key}: Data is not a list ({type(bullets)}).")
                continue

            # Initialize actual counts for each provenance type
            actual_counts = {prov.value: 0 for prov in BulletProvenance}
            target_total = sum(target_split.values()) # Expected total bullets for this section
            actual_total = 0

            # Count actual provenance types
            for i, bullet in enumerate(bullets):
                 if isinstance(bullet, dict):
                     prov = bullet.get('provenance')
                     if prov in actual_counts:
                         actual_counts[prov] += 1
                         actual_total += 1
                     else:
                          # Log if an unknown provenance value is encountered
                          logging.warning(f"Unknown provenance '{prov}' found in {section_key}[{i}].")
                 # Special case for TraderSense which might have simple strings copied directly
                 elif isinstance(bullet, str) and section_enum == ResumeSection.K7_TRADERSENSE_BULLETS:
                     actual_counts[BulletProvenance.Verbatim.value] += 1 # Assume copied = Verbatim
                     actual_total += 1
                 else:
                      # Skip unexpected item types
                      logging.warning(f"Unexpected item type in {section_key}[{i}]: {type(bullet)}. Skipping provenance count.")

            # Check 1: Does the total number of bullets match the target?
            if actual_total != target_total:
                 all_splits_valid = False
                 violations.append(f"{section_key}: Total count mismatch (Expected {target_total}, Got {actual_total})")
                 failed_sections.add(section_enum)
                 # Continue to check individual types for more detailed errors if needed,
                 # but this section already failed.

            # Check 2: Does the count for each provenance type match the target?
            for prov_type_enum in BulletProvenance:
                prov_type = prov_type_enum.value
                target_count = target_split.get(prov_type, 0) # Target count for this type (0 if not specified)
                actual_count = actual_counts.get(prov_type, 0) # Actual count found
                if actual_count != target_count:
                    all_splits_valid = False
                    # Only add violation message if total count check didn't already fail this section
                    if section_enum not in failed_sections:
                         violations.append(f"{section_key}: {prov_type} count mismatch (Expected {target_count}, Got {actual_count})")
                         failed_sections.add(section_enum)

        # Populate error details if any violations occurred
        if not all_splits_valid:
            data["error_details"] = {
                "violations": violations,
                "failed_sections": failed_sections # Store the set of failed ResumeSection enums
            }
        return all_splits_valid

    def _validate_authenticity_signal(self, data: Dict) -> bool:
        """Checks if generated content contains authenticity verbs from HOP-0."""
        try:
            thematic_analysis = data.get('thematic_analysis')
            # Check if thematic_analysis and authenticity_patterns exist
            if not thematic_analysis or not hasattr(thematic_analysis, 'authenticity_patterns') or not thematic_analysis.authenticity_patterns:
                 data["error_details"] = {"details": "ThematicAnalysis or AuthenticityPatterns missing/empty."}
                 # Allow pass if HOP-0 failed to generate patterns, as we can't check.
                 # Consider changing severity or adding a separate check for HOP-0 success if needed.
                 logging.warning("Authenticity signal check skipped: HOP-0 patterns missing.")
                 return True

            auth_patterns = thematic_analysis.authenticity_patterns
            # Ensure 'patterns' key exists and is a dictionary
            patterns_dict = auth_patterns.get('patterns') if isinstance(auth_patterns, dict) else None
            if not isinstance(patterns_dict, dict):
                 data["error_details"] = {"details": "Authenticity patterns format invalid (expected dict under 'patterns')."}
                 logging.warning("Authenticity signal check skipped: Invalid patterns format.")
                 return True # Allow pass if format is wrong

            target_verbs = patterns_dict.get('achievement_verb_patterns')
            # Ensure target_verbs is a list
            if not isinstance(target_verbs, list):
                logging.warning(f"Authenticity Signal Check: Target verbs is not a list ({type(target_verbs)}). Skipping.")
                data["error_details"] = {"details": "Target authenticity verbs from HOP-0 analysis is not a list."}
                return True # Pass if HOP-0 output was malformed

            if not target_verbs:
                logging.info("Authenticity Signal Check: No target verbs found in HOP-0 analysis to check against.")
                data["error_details"] = {"details": "No authenticity verbs found in HOP-0 analysis to check against."}
                return True # Pass if no verbs were extracted

            # Gather text from relevant sections
            content_to_check = []
            staging_buffer = data['staging_buffer']
            # Include Exec Summary
            content_to_check.append(staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, ''))
            # Include bullets from experience and competencies
            bullet_sections = [
                ResumeSection.K5_UNIFY_BULLETS, ResumeSection.K6_IBM_BULLETS,
                ResumeSection.K8_EY_BULLETS, ResumeSection.K9_EARLY_CAREER_BULLETS,
                ResumeSection.K10_COMPETENCIES
            ]
            for section_enum in bullet_sections:
                bullets = staging_buffer.get(section_enum.value, [])
                if isinstance(bullets, list):
                    for bullet in bullets:
                        text_to_add = None
                        if isinstance(bullet, dict):
                            text_to_add = bullet.get('text', bullet.get('bullet_text')) # Prefer final text
                        elif isinstance(bullet, str):
                            text_to_add = bullet
                        if text_to_add:
                            content_to_check.append(text_to_add)

            # Combine all text and convert to lower case for matching
            full_text = " ".join(content_to_check).lower()
            if not full_text.strip():
                 data["error_details"] = {"details": "No generated text content found to check verbs against."}
                 return False # Fail if there's no text to check

            # Count how many target verbs are present (case-insensitive)
            found_verbs_count = sum(1 for verb in target_verbs if isinstance(verb, str) and verb.lower() in full_text)

            # Require at least 2 matching verbs
            if found_verbs_count < 2:
                data["error_details"] = {"details": f"Found only {found_verbs_count} matching auth-verbs. Expected 2+. (Targets: {target_verbs[:5]})"}
                return False # Fail if fewer than 2 verbs match

            return True # Pass if 2 or more verbs match

        except Exception as e:
            # Catch unexpected errors during validation logic
            logging.error(f"Error during authenticity signal validation: {e}", exc_info=True)
            data["error_details"] = {"details": f"Validation logic failed: {e}"}
            return False # Fail on exception

    # --- NEW VALIDATOR METHOD ---
    def _validate_exec_summary_vs_sections(self, data: Dict) -> bool:
        """
        [NEW in v12.65]
        Validates the cosine similarity between the Executive Summary (K.1)
        and the combined content of key sections against defined thresholds.
        Adds K.1 to failed_sections in error_details if any threshold is exceeded.
        """
        all_passed = True
        failures = []
        failed_sections_for_rule = set() # Store K.1 if any check fails

        exec_summary_text = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        if not exec_summary_text:
            # If K.1 is missing, that's a STRUCTURE failure, not a similarity failure. Pass here.
            data["error_details"] = {"failures": "Executive Summary text not found for comparison."}
            return True # Pass this specific rule, let structure rule fail it.

        # Define sections and their thresholds
        sections_to_compare = {
            ResumeSection.K10_COMPETENCIES: ("Competencies (K.10 Items)", 0.30),
            ResumeSection.K5_UNIFY_BULLETS: ("Unify (K.5 Overview + Bullets)", 0.60), # Use Bullets enum to get associated Overview
            ResumeSection.K6_IBM_BULLETS: ("IBM (K.6 Overview + Bullets)", 0.50),     # Use Bullets enum to get associated Overview
            ResumeSection.K8_EY_BULLETS: ("EY (K.8 Overview + Bullets)", 0.30),         # Use Bullets enum to get associated Overview
            ResumeSection.K9_EARLY_CAREER_BULLETS: ("Early Career (K.9 Overview + Bullets)", 0.30), # Use Bullets enum to get associated Overview
        }

        # Mapping for finding the corresponding overview section
        bullet_to_overview_map = {
            ResumeSection.K5_UNIFY_BULLETS: ResumeSection.K5_UNIFY_OVERVIEW,
            ResumeSection.K6_IBM_BULLETS: ResumeSection.K6_IBM_OVERVIEW,
            ResumeSection.K8_EY_BULLETS: ResumeSection.K8_EY_OVERVIEW,
            ResumeSection.K9_EARLY_CAREER_BULLETS: ResumeSection.K9_EARLY_CAREER_OVERVIEW,
        }


        for bullets_section_enum, (label, threshold) in sections_to_compare.items():
            section_content_parts = []

            # Add overview text (if applicable and exists)
            overview_section_enum = bullet_to_overview_map.get(bullets_section_enum)
            if overview_section_enum:
                overview_text = data['staging_buffer'].get(overview_section_enum.value, '')
                if overview_text and isinstance(overview_text, str):
                    section_content_parts.append(overview_text.strip())

            # Add bullet texts (or competency items)
            items = data['staging_buffer'].get(bullets_section_enum.value, [])
            if items and isinstance(items, list):
                for item in items:
                    item_text = ""
                    if isinstance(item, dict):
                        # Use final 'text' if available (post-rewrite), else fallback
                        item_text = item.get('text', item.get('bullet_text', ''))
                    elif isinstance(item, str):
                        item_text = item
                    if item_text:
                        section_content_parts.append(item_text.strip())

            # Combine parts and calculate similarity
            if section_content_parts:
                combined_section_text = "\n".join(section_content_parts)
                # Ensure dup_detector exists before calling its method
                if hasattr(self, 'dup_detector') and self.dup_detector:
                     similarity = self.dup_detector._calculate_cosine_similarity(exec_summary_text, combined_section_text)
                else:
                     logging.warning(f"DuplicateDetector not initialized in PreFlightValidator. Skipping similarity check for {label}.")
                     similarity = -1.0 # Indicate skipped calculation


                if similarity >= threshold:
                    all_passed = False
                    failures.append(f"{label}: {similarity:.2f} (Threshold: < {threshold:.2f})")
                    failed_sections_for_rule.add(ResumeSection.K1_EXECUTIVE_SUMMARY) # Add K.1 to trigger its rewrite
                elif similarity < 0:
                     # Log if calculation was skipped, but don't fail the rule
                     logging.warning(f"Similarity check skipped for {label} due to missing detector.")

            else:
                # Log if a section expected for comparison was missing content
                logging.debug(f"Exec Summary Similarity: No content found for section {label} to compare.")


        if not all_passed:
            data["error_details"] = {
                "failures": "; ".join(failures),
                "failed_sections": failed_sections_for_rule # Pass the set containing K.1
            }
        return all_passed
      
# ============================================================================
# HOP-6: GATE DECISION
# ============================================================================
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

# ============================================================================
# HOP-7: FILE RENDERING
# ============================================================================

class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator'):
        self.master_resume = master_resume
        self.orchestrator = orchestrator # For access to validation results etc.

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str,
        job_title: str,
        thematic_analysis: ThematicAnalysis,
        job_description: str = None
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report, App Tracker).
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        v10.0: Swapped QA Report (Output 4) and App Tracker (Output 5).
        """
        file_paths = {}
        file_contents = {}
        validation_results = []

        # --- 1. Render Resume Artifact ---
        try:
            path, content = self._render_resume_artifact(staging_buffer, company_name, job_title)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Resume MD: {e}"
            ))

        # --- 2. Render Skills Artifact ---
        try:
            path, content = self._render_skills_artifact(staging_buffer, company_name, job_title, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Skills TXT: {e}"
            ))

        # --- 3. Render Cover Letter Artifact ---
        try:
            path, content = self._render_cover_letter_artifact(staging_buffer, company_name, job_title)
            file_paths['cover_letter'] = path
            file_contents['cover_letter'] = content
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Cover Letter TXT: {e}"
            ))

        # --- 4. Render QA Report Artifact (Path only) --- [NOW OUTPUT 4]
        # The content for the QA report is generated in HOP-8 by the orchestrator
        try:
            path, content = self._render_qa_report_artifact(company_name, job_title)
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content # Will be an empty string
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
            ))

        # --- 5. Render App Tracker Artifact (and Validate) --- [NOW OUTPUT 5]
        try:
            path, content, app_tracker_validation_results = self._render_app_tracker_artifact(company_name, job_title, file_paths)
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content
            validation_results.extend(app_tracker_validation_results) # Add validation results
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render App Tracker JSON: {e}"
            ))

        return file_paths, (validation_results, file_contents)

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str) -> Tuple[str, str]:
        """Renders the resume markdown artifact."""
        content = self._render_resume_markdown(staging_buffer)
        # Clean company/title for filename
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)
        path = f"Resume_{safe_company}_{safe_title}.md"
        return path, content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str, job_description: str) -> Tuple[str, str]:
        """Renders the skills artifact."""
        content = self._render_skills(staging_buffer, job_description)
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)
        path = f"Skills_{safe_company}_{safe_title}.txt"
        return path, content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str) -> Tuple[str, str]:
        """Renders the cover letter artifact."""
        content = staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)
        path = f"CoverLetter_{safe_company}_{safe_title}.txt"
        return path, content

    def _render_qa_report_artifact(self, company_name: str, job_title: str) -> Tuple[str, str]:
        """Renders the QA report artifact placeholder. Content is generated in the orchestrator."""
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)
        path = f"QA_Report_{safe_company}_{safe_title}.md"
        # Content is generated in HOP-8 by the orchestrator, return empty string.
        return path, ""

    def _render_app_tracker_artifact(self, company_name: str, job_title: str, file_paths: Dict[str, str]) -> Tuple[str, str, List[ValidationResult]]:
        """Renders the application tracker artifact and validates it."""
        app_tracker_data = self._render_app_tracker(company_name, job_title, file_paths)
        validation_results = []
        
        # Validate the generated tracker data
        try:
            validator = AppTrackerQAValidator()
            # The validator expects a list of rows
            validation_result_dict = validator.validate_tracker_data([app_tracker_data])
            
            if "BLOCKED" in validation_result_dict.get("result", ""):
                # Convert AppTracker validation failures into standard ValidationResult objects
                errors = validation_result_dict.get('errors', [])
                for error in errors:
                    validation_results.append(ValidationResult(
                        rule_id=f"APP_TRACKER_{error.get('RULE_ID', 'UNKNOWN')}",
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"AppTracker Error (Row {error.get('row_index')}): {error.get('message')}",
                        details=error
                    ))
            else:
                validation_results.append(ValidationResult(
                    rule_id="APP_TRACKER_VALIDATION", passed=True, severity=ValidationSeverity.INFO,
                    message="AppTracker JSON passed v5 QA spec."
                ))

        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="APP_TRACKER_VALIDATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"App tracker validation failed during execution: {e}"
            ))
            
        content = json.dumps(app_tracker_data, indent=2)
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)
        path = f"AppTracker_{safe_company}_{safe_title}.json"
        return path, content, validation_results
    
    # Data-driven configuration for rendering the resume markdown.
    # Defines the order, content source, and rendering style for each part of the resume.
    RESUME_RENDER_CONFIG = [
        # --- K.0 Name, Headline, Contact ---
        {"type": "simple", "source": ResumeSection.K0_NAME, "render_method": "_render_name"},
        {"type": "simple", "source": ResumeSection.K0_HEADLINE, "render_method": "_render_headline"},
        {"type": "simple", "source": ResumeSection.K0_CONTACT, "render_method": "_render_contact"},
        # --- K.1 Executive Summary ---
        {"type": "header", "text": "## EXECUTIVE SUMMARY"},
        {"type": "simple", "source": ResumeSection.K1_EXECUTIVE_SUMMARY, "render_method": "_render_paragraph"},
        # --- K.5 - K.9 Professional Experience ---
        {"type": "header", "text": "## PROFESSIONAL EXPERIENCE"},
        {"type": "experience", "master_index": 0, "overview_source": ResumeSection.K5_UNIFY_OVERVIEW, "bullets_source": ResumeSection.K5_UNIFY_BULLETS},
        {"type": "experience", "master_index": 1, "overview_source": ResumeSection.K6_IBM_OVERVIEW, "bullets_source": ResumeSection.K6_IBM_BULLETS},
        {"type": "experience", "master_index": 2, "overview_source": ResumeSection.K7_TRADERSENSE_OVERVIEW, "bullets_source": ResumeSection.K7_TRADERSENSE_BULLETS},
        {"type": "experience", "master_index": 3, "overview_source": ResumeSection.K8_EY_OVERVIEW, "bullets_source": ResumeSection.K8_EY_BULLETS},
        {"type": "experience", "master_index": 4, "overview_source": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "bullets_source": ResumeSection.K9_EARLY_CAREER_BULLETS},
        # --- K.11 Education ---
        {"type": "header", "text": "## EDUCATION"},
        {"type": "education", "source": ResumeSection.K11_EDUCATION},
        # --- K.12 Certifications ---
        {"type": "header", "text": "## CERTIFICATIONS & CREDENTIALS"},
        {"type": "certifications", "source": ResumeSection.K12_CERTIFICATIONS},
        # --- K.10 Competencies ---
        {"type": "header", "text": "## STRATEGIC & TECHNICAL COMPETENCIES"},
        {"type": "competencies", "source": ResumeSection.K10_COMPETENCIES},
    ]

    def _render_resume_markdown(self, staging_buffer: ImmutableStagingBuffer) -> str:
        """
        Render resume as Markdown, driven by the RESUME_RENDER_CONFIG.
        v9.90: Uses specific render methods for each type to enforce format.
        """
        output_lines = []
        
        for config in self.RESUME_RENDER_CONFIG:
            render_type = config["type"]
            
            if render_type == "header":
                # Add a newline before H2 headers, except for the very first one
                prefix = "\n" if output_lines else ""
                output_lines.append(f'{prefix}{config["text"]}')
            
            elif render_type == "simple":
                content = staging_buffer.get(config["source"].value)
                render_method = getattr(self, config["render_method"])
                if content:
                    output_lines.append(render_method(content))
            
            elif render_type == "experience":
                master_experience = self.master_resume.get("professional_experience", [])
                if config["master_index"] < len(master_experience):
                    master_exp = master_experience[config["master_index"]]
                    overview = staging_buffer.get(config["overview_source"].value)
                    bullets = staging_buffer.get(config["bullets_source"].value)
                    output_lines.append(self._render_experience_section(master_exp, overview, bullets))
            
            elif render_type == "education":
                content = staging_buffer.get(config["source"].value)
                if content:
                    output_lines.append(self._render_education_section(content))

            elif render_type == "certifications":
                content = staging_buffer.get(config["source"].value)
                if content:
                    output_lines.append(self._render_certifications_section(content))

            elif render_type == "competencies":
                content = staging_buffer.get(config["source"].value)
                if content:
                    output_lines.append(self._render_competencies_section(content))

        # Join all rendered parts with a single newline, as formatting (like \n\n)
        # is now handled by the individual render methods.
        return "\n".join(output_lines)

    # --- Start of v9.90 Hardened Render Methods ---

    def _render_name(self, content: str) -> str:
        """Enforces H2 (##) for Name (K.0)."""
        return f"## {content.strip()}\n" # Add one trailing newline

    def _render_headline(self, content: str) -> str:
        """Enforces plain text for Headline (K.0)."""
        return f"{content.strip()}\n" # Add one trailing newline

    def _render_contact(self, content: str) -> str:
        """Enforces plain text for Contact (K.0)."""
        return f"{content.strip()}\n" # Add one trailing newline

    def _render_paragraph(self, content: str) -> str:
        """Enforces plain text for paragraphs (K.1)."""
        return f"{content.strip()}\n" # Add one trailing newline

    def _render_experience_section(self, master_exp: Dict, overview: str, bullets: List[Union[str, Dict]]) -> str:
        """
        Enforces hardened format for experience sections (K.5-K.9).
        - Line 1: **Company | Location**
        - (Blank Line)
        - Line 2: **Title | Start – End**
        - (Blank Line)
        - Overview text
        - (Blank Line)
        - * Bullet 1
        - * Bullet 2
        - (Blank Line)
        """
        if not master_exp:
            return ""
        
        lines = []

        # Line 1: **Company | Location**
        company = master_exp.get('company', '').strip()
        location = master_exp.get('location', '').strip()
        line1_parts = [part for part in [company, location] if part]
        if line1_parts:
            lines.append(f"**{' | '.join(line1_parts)}**")

        # Line 2: **Title | Dates**
        title = master_exp.get('title', '').strip()
        dates = master_exp.get('dates', {})
        start_date = dates.get('start', '').strip()
        end_date = dates.get('end', '').strip()
        date_parts = [part for part in [start_date, end_date] if part]
        date_str = " – ".join(date_parts)
        line2_parts = [part for part in [title, date_str] if part]
        if line2_parts:
            lines.append(f"**{' | '.join(line2_parts)}**")
        
        # Overview
        if overview:
            lines.append(f"\n{overview.strip()}") # Add blank line before

        # Bullets
        bullet_lines = []
        bullets_list = bullets if isinstance(bullets, list) else []
        for bullet in bullets_list:
            bullet_text = ""
            if isinstance(bullet, dict):
                bullet_text = bullet.get('text', str(bullet)).strip()
            elif isinstance(bullet, str):
                bullet_text = bullet.strip()

            if bullet_text:
                bullet_lines.append(f"* {bullet_text}") # Enforce '* '
        
        if bullet_lines:
            # Join bullets with single newline, add blank line before list
            lines.append("\n" + "\n".join(bullet_lines))
        
        # Join all parts with a single newline, add one trailing blank line
        return "\n".join(lines) + "\n"

    def _render_education_section(self, education_list: List[Dict]) -> str:
        """
        Enforces hardened format for Education (K.11).
        - No bullets.
        - Single line per entry.
        - Two newlines at end.
        """
        lines = []
        if not education_list:
            return ""
        for edu in education_list:
            degree = edu.get('degree', '').strip()
            institution = edu.get('institution', '').strip()
            notes = edu.get('notes', '').strip()
            
            line_parts = [part for part in [degree, institution] if part]
            line = ", ".join(line_parts)
            if notes:
                line += f" ({notes})"
            lines.append(line) # No bullet
        
        # Join with single newline, add one trailing blank line
        return "\n".join(lines) + "\n"

    def _render_certifications_section(self, certifications_list: List[str]) -> str:
        """
        Enforces hardened format for Certifications (K.12).
        - No bullets.
        - Single line per entry.
        - Two newlines at end.
        """
        if not certifications_list:
            return ""
        
        # Join with single newline, add one trailing blank line
        return "\n".join([cert for cert in certifications_list if cert]) + "\n"

    
    def _render_competencies_section(self, competencies_list: List[Union[str, Dict]]) -> str:
        """
        Enforces hardened format for Competencies (K.10).
        - Uses '* ' bullet.
        - Single line per entry.
        - Two newlines at end.
        """
        if not competencies_list:
            return ""
        
        lines = []
        for comp in competencies_list:
            comp_text = ""
            if isinstance(comp, dict):
                comp_text = comp.get('text', str(comp)).strip()
            elif isinstance(comp, str):
                comp_text = comp.strip()
            
            if comp_text:
                # Remove any existing bullet markers before adding the correct one
                comp_text = re.sub(r'^[•*]\s*', '', comp_text)
                lines.append(f"* {comp_text}") # Enforce '* '
        
        # Join with single newline, add one trailing blank line
        return "\n".join(lines) + "\n"
    
    # --- End of v9.90 Hardened Render Methods ---

    def _render_skills(self, staging_buffer: ImmutableStagingBuffer, job_description: str = None) -> str:
        """
        Render skills with double-check validation.
        This method retrieves K.2_Skills from the buffer (LLM-generated)
        and validates each skill is 1-3 words before formatting.
        """
        skills_list = staging_buffer.get(ResumeSection.K2_SKILLS.value)
        
        output_lines = []
        if not isinstance(skills_list, list) or not skills_list:
            return "• Error: K.2_Skills list not found or is not a list in staging buffer."
            
        # HARDENING: If the list contains an error message, return it directly.
        if isinstance(skills_list[0], str) and skills_list[0].strip().startswith("Error:"):
            return "\n\n".join(skills_list)
        
        valid_skills = []
        malformed_skills = []
        
        for skill in skills_list:
            if isinstance(skill, str):
                cleaned_skill = skill.strip()
                word_count = len(cleaned_skill.split())
                if 1 <= word_count <= 3:
                    valid_skills.append(f"• {cleaned_skill}") # Format with bullet
                else:
                    malformed_skills.append(f"• {cleaned_skill} [Warning: Malformed - {word_count} words]")
            else:
                malformed_skills.append(f"• {str(skill).strip()} [Warning: Non-string skill]")
        
        output_lines.extend(valid_skills)
        output_lines.extend(malformed_skills) # Append warnings at the end
        
        # Format with double newlines for spacing
        return "\n\n".join(output_lines)

    def _render_app_tracker(
        self,
        company_name: str,
        job_title: str,
        file_paths: Dict[str, str]
    ) -> Dict:
        """Render application tracker (v4 - 54 fields) - QA SPEC V5 VALIDATED."""
        tracker = copy.deepcopy(APP_TRACKER_SCHEMA_V4)
        
        # Get candidate name and format it for the versioned resume string
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        
        # Clean company/title for filename
        safe_company = re.sub(r'[^\w\-]', '_', company_name)
        safe_title = re.sub(r'[^\w\-]', '_', job_title)

        # Auto-populate fields with new schema field names
        tracker['Company'] = company_name
        tracker['Job Title'] = job_title
        tracker['Application Date'] = datetime.now().strftime("%m/%d/%Y")
        tracker['Base Resume'] = "" # Per user request
        # Per user request for format: "Amit_Ayer_Resume_DataRobot_VP_AI_Technical_Success"
        tracker['Versioned Resume'] = f"{candidate_name}_Resume_{safe_company}_{safe_title}"
        tracker['Pipeline Status'] = 'Applied'
        
        return tracker
    
# ============================================================================
# WORKFLOW ORCHESTRATOR (STATEFUL RETRY VERSION)
# ============================================================================

class WorkflowOrchestrator:

    def __init__(self, master_resume: Dict, test_mode: bool = False):
        """
        Initializes the orchestrator.

        Args:
            master_resume (Dict): The candidate's master resume data.
            test_mode (bool): If True, skips API key checks for testing purposes.
        """
        self.master_resume = master_resume
        self.hop_checkpoints = [] # Stores HopCheckpoint objects for CoC
        self.validation_results = [] # Stores final validation results from HOP-5
        self.rendered_output = None # Stores final output dict after HOP-7/8

        self.dup_detector = None 
        self.similarity_matrix_data = None 
        self.executive_summary_similarity_data = None 
        self.overview_similarity_data = None 
        self.dedup_analysis_timestamp = None 
        self.hash_chain = [] 
        self.constraints = ContentConstraintsConfig() 

        self.jd_enforcer = JDEnforcementValidator() 

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__) 

        if not test_mode:
            if not os.environ.get("GEMINI_API_KEY"):
                self.logger.error(
                    "CRITICAL WARNING: GEMINI_API_KEY environment variable not set!\n" +
                    "="*80 + "\n" +
                    "Workflow may fail or fall back unexpectedly.\n" +
                    "Please set it using: export GEMINI_API_KEY='your-key-here'\n" +
                    "Get your key at: https://makersuite.google.com/app/apikey\n" +
                    "="*80
                )
            else:
                self.logger.info("✓ GEMINI_API_KEY detected - Gemini API integration enabled")
        else:
            self.logger.info("Running in test mode - API key checks skipped.")


        self.logger.info(f"Using LLM Provider: Gemini")
        self.logger.info(f"Using Model: {RAGConfig().model}") 

    def _execute_hop_0_jd_analysis(self, job_description: str) -> ThematicAnalysis:
        """Executes HOP-0: Job Description Analysis & RAG."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-0] Job Description Analysis & RAG...")
        jd_analyzer = self._create_jd_analyzer()
        try:
            thematic_analysis = jd_analyzer.analyze(job_description)
            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG", [],
                {"signal_score": getattr(thematic_analysis, 'signal_quality_score', 0.0)},
                start_time=hop_start_time,
                metadata={"web_search_calls": getattr(jd_analyzer, 'search_calls_made', 0)}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint)
            return thematic_analysis
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-0] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG",
                [ValidationResult("HOP-0_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-0 failed: {e}")

    def _execute_hop_1_clerk_extraction(self) -> Dict:
        """Executes HOP-1: Master Resume Extraction & Hallucination Check."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-1] Master Resume Extraction...")
        try:
            clerk = ClerkExtractor(self.master_resume)
            extracted_data, hop_results = clerk.extract()
            bullets_extracted = sum(len(s.get('bullets', [])) for s in extracted_data.get('experience_sections', []))
            hop_checkpoint = self._create_checkpoint(
                "HOP-1", "Clerk Extraction", hop_results,
                {"bullets_extracted": bullets_extracted},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True)
            return extracted_data
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-1] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                "HOP-1", "Clerk Extraction",
                [ValidationResult("HOP-1_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-1 failed: {e}")

    def _execute_hop_2_enrichment(self, extracted_data: Dict, thematic_analysis: ThematicAnalysis) -> Dict:
        """Executes HOP-2: Data Enrichment (Verbs, Duplicates)."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-2] Data Enrichment...")
        try:
            enricher = DataEnricher()
            enriched_scaffold, hop_results = enricher.enrich(extracted_data, thematic_analysis, self)
            hop_checkpoint = self._create_checkpoint(
                "HOP-2", "Data Enrichment", hop_results,
                enriched_scaffold,
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True)
            return enriched_scaffold
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-2] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                "HOP-2", "Data Enrichment",
                [ValidationResult("HOP-2_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                extracted_data, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-2 failed: {e}")

    def _execute_hop_3_artist_generation(self, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis) -> Dict:
        """
        [REFACTORED]
        Executes HOP-3: Content Generation with STATEFUL RETRY logic.
        v12.50: Manages generation state and selectively retries failed sections
        at progressively lower temperatures.
        """
        self.logger.info("\n[HOP-3] Content Generation (Artist) with Stateful Retry...")
        hop_start_time = datetime.now()

        artist = ArtistGenerator(
            master_resume=self.master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis,
            previous_failures=[] # Pass empty list, feedback is now handled by retry logic
        )
        
        validator = PreFlightValidator(self.master_resume)
        
        # Define the universal temperature schedule
        temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2]
        max_attempts = len(temperature_schedule)
        
        # --- State Tracking ---
        # Stores the final, locked-in content for all sections
        final_generation_state: Dict[str, Any] = {} 
        # Stores the *best* temperature at which each section passed
        locked_section_temps: Dict[ResumeSection, float] = {}
        # Stores all copied/dummy content
        copied_content: Dict[str, Any] = {}
        
        # Get the set of all sections that need LLM generation
        all_llm_sections = {
            config["section"] for config in artist.ARTIST_GENERATION_CONFIG 
            if not config["method_name"].startswith("_copy_") and 
               not config["method_name"] == "_generate_dummy_header"
        }
        
        # Initially, we need to generate all LLM sections
        sections_to_generate = all_llm_sections.copy() 
        
        # Store validation results from the *final* successful attempt
        final_validation_results = []
        all_passed = False
        
        # Run copy/dummy methods ONCE and store them
        try:
            dummy_sections = {
                config["section"] for config in artist.ARTIST_GENERATION_CONFIG 
                if config["method_name"].startswith("_copy_") or 
                   config["method_name"] == "_generate_dummy_header"
            }
            copied_output, _ = artist.generate(
                sections_to_generate=dummy_sections,
                temperature_overrides={} # Temps don't matter for copy methods
            )
            copied_content.update(copied_output)
            final_generation_state.update(copied_output)
        except Exception as e:
            raise HopExecutionError(f"HOP-3 failed during initial content copy: {e}")

        
        # --- Stateful Retry Loop ---
        for attempt, temperature in enumerate(temperature_schedule, 1):
            if not sections_to_generate:
                self.logger.info(f"  All sections passed. Exiting generation loop.")
                all_passed = True # We finished with no sections to retry
                break # All sections are locked in

            self.logger.info(f"  Attempt {attempt}/{max_attempts} @ Temp {temperature:.1f}...")
            self.logger.info(f"    Sections to generate: {[s.name for s in sections_to_generate]}")
            attempt_start_time = time.time()

            # 1. Generate *only* the sections that need (re)generation
            try:
                # Create temp overrides only for sections being generated this round
                temp_overrides = {section: temperature for section in sections_to_generate}
                
                newly_generated_content, generation_results = artist.generate(
                    sections_to_generate=sections_to_generate,
                    temperature_overrides=temp_overrides
                )
                
                # Check for immediate generation failure
                if not generation_results or not generation_results[0].passed:
                    generation_error = generation_results[0].message if generation_results else "Unknown generation error"
                    raise HopExecutionError(f"Artist.generate() failed: {generation_error}")
                
            except Exception as e:
                 self.logger.error(f"    ✗ Generation Attempt {attempt} FAILED: {e}", exc_info=False)
                 # This is a hard failure, abort the whole hop
                 final_validation_results = [ValidationResult(f"ARTIST_GENERATION_ATTEMPT_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation failed: {e}")]
                 all_passed = False
                 break 

            # 2. Update the *current* state with the new content
            # This merges locked content (already in state) with new content
            final_generation_state.update(newly_generated_content)

            # 3. Validate the *entire* resume state
            temp_buffer = ImmutableStagingBuffer()
            for key, value in final_generation_state.items():
                if value is not None: # Only add non-empty sections to buffer
                    temp_buffer.set(key, value)
            temp_buffer.lock() # Lock for validation

            try:
                current_validation_results, current_all_passed, failed_sections = validator.validate(
                    temp_buffer, thematic_analysis, job_description,
                    sections_under_test=sections_to_generate # Pass sections that were just run
                )
                final_validation_results = current_validation_results
                all_passed = current_all_passed
                
            except Exception as e:
                self.logger.error(f"    ✗ Validation Attempt {attempt} FAILED: {e}", exc_info=True)
                final_validation_results = [ValidationResult(f"VALIDATION_ATTEMPT_{attempt}", False, ValidationSeverity.CRITICAL, f"Validation failed: {e}")]
                all_passed = False
                break 

            attempt_duration = time.time() - attempt_start_time
            self.logger.info(f"    Attempt {attempt} completed in {attempt_duration:.2f}s. Validation passed: {all_passed}")

            # 4. Update generation state based on validation
            
            # Find sections that were tested and PASSED
            sections_that_passed = sections_to_generate - failed_sections
            
            for passed_section in sections_that_passed:
                locked_section_temps[passed_section] = temperature
                self.logger.info(f"    ✓ LOCKED: {passed_section.name} @ {temperature:.1f}")

            # Set the list for the *next* iteration
            sections_to_generate = failed_sections

            if not all_passed:
                self.logger.warning(f"    ✗ {len(failed_sections)} sections failed validation and will be retried: {[s.name for s in failed_sections]}")
                # Log the specific failures for context
                for vr in final_validation_results:
                    if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                         self.logger.warning(f"      - {vr.rule_id}: {vr.message}")
            
        # --- End of Loop ---

        # 5. Final Outcome
        
        # We need the full output dict, even if it failed
        artist_output = final_generation_state
        
        # Store the final successful validation results for downstream use
        self.validation_results = final_validation_results

        hop_checkpoint = self._create_checkpoint(
            "HOP-3", f"Artist Generation (final attempt {attempt})",
            final_validation_results, # Use results from the *last* validation run
            artist_output,
            start_time=hop_start_time,
            metadata={
                "attempts_made": attempt,
                "final_temperatures": {k.name: v for k, v in locked_section_temps.items()}
            }
        )
        self.hop_checkpoints.append(hop_checkpoint)

        if not all_passed:
            self.logger.error(f"  ✗ HOP-3 FAILED: Content validation failed after {attempt} attempts.")
            hop_checkpoint.status = HopStatus.FAIL
            critical_failures = [f for f in final_validation_results if not f.passed and f.severity == ValidationSeverity.CRITICAL]
            high_failures = [f for f in final_validation_results if not f.passed and f.severity == ValidationSeverity.HIGH]
            
            if critical_failures: reason = f"Critical Failure: {critical_failures[0].rule_id}"
            elif high_failures: reason = f"High Failure: {high_failures[0].rule_id}"
            else: reason = f"Validation failed after {attempt} attempts."
            
            hop_checkpoint.error_message = reason
            raise HopExecutionError(hop_checkpoint.error_message)
        else:
             self.logger.info(f"  ✓ HOP-3 successful after {attempt} attempt(s).")
             avg_temp = sum(locked_section_temps.values()) / len(locked_section_temps) if locked_section_temps else 0.0
             self.logger.info(f"    Final average locked temperature: {avg_temp:.2f}")
             self._check_hop_status(hop_checkpoint)

        return artist_output

    def _execute_hop_4_staging_and_sanitization(self, artist_output: Dict) -> ImmutableStagingBuffer:
        """Executes HOP-4 (Staging) and HOP-4.5 (Sanitization & Locking)."""
        # --- HOP-4: Staging ---
        hop4_start_time = datetime.now()
        self.logger.info("\n[HOP-4] Populating Staging Buffer...")
        staging_buffer = ImmutableStagingBuffer()
        sections_populated = 0
        try:
            for key, value in artist_output.items():
                # --- MODIFICATION: Only set non-None values ---
                # The artist_output from the stateful retry might have None 
                # for sections that were never successfully generated (if it failed)
                if value is not None:
                    staging_buffer.set(key, value)
                    sections_populated += 1
            # --- END MODIFICATION ---
            hop4_checkpoint = self._create_checkpoint(
                "HOP-4", "Staging Buffer Population", [],
                {"sections_populated": sections_populated},
                start_time=hop4_start_time
            )
            self.hop_checkpoints.append(hop4_checkpoint)
            self._check_hop_status(hop4_checkpoint)
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-4] FAILED: {e}", exc_info=True)
             hop4_checkpoint = self._create_checkpoint(
                 "HOP-4", "Staging Buffer Population",
                 [ValidationResult("HOP-4_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 artist_output, start_time=hop4_start_time, error_message=str(e)
             )
             hop_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop4_checkpoint)
             raise HopExecutionError(f"HOP-4 failed: {e}")

        # --- HOP-4.5: Sanitization & Locking ---
        hop45_start_time = datetime.now()
        self.logger.info("\n[HOP-4.5] Text Sanitization & Locking...")
        try:
            sanitizer = TextSanitizer()
            hop45_results, sanitized_data = sanitizer.sanitize_buffer(staging_buffer)

            temp_staging = ImmutableStagingBuffer()
            for key, value in sanitized_data.items():
                temp_staging.set(key, value)
            staging_buffer._data = temp_staging._data # Overwrite internal data before lock
            self.logger.info("  ✓ Staging buffer updated with sanitized content.")

            staging_buffer.lock()
            self.logger.info("  ✓ Staging buffer locked.")

            hop45_checkpoint = self._create_checkpoint(
                "HOP-4.5", "Text Sanitization & Lock", hop45_results,
                {"buffer_locked": True},
                start_time=hop45_start_time 
            )
            self.hop_checkpoints.append(hop45_checkpoint)
            self._check_hop_status(hop45_checkpoint)
            return staging_buffer
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-4.5] FAILED: {e}", exc_info=True)
            if not staging_buffer.is_locked(): staging_buffer.lock() 
            hop45_checkpoint = self._create_checkpoint(
                "HOP-4.5", "Text Sanitization & Lock",
                [ValidationResult("HOP-4.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                {"buffer_locked": staging_buffer.is_locked()},
                start_time=hop45_start_time, error_message=str(e)
            )
            hop45_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop45_checkpoint)
            raise HopExecutionError(f"HOP-4.5 failed: {e}")

    def _execute_hop_5_validation(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str) -> List[ValidationResult]:
        """
        Executes HOP-5: Pre-flight Validation.
        [REFACTORED] This now runs *after* the stateful retry loop in HOP-3.
        It serves as a *final* confirmation. The results from the *last*
        HOP-3 attempt are already stored in self.validation_results. This
        method just re-runs it one last time on the *sanitized* buffer
        for maximum safety.
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-5] Final Pre-flight Validation (Post-Sanitization)...")
        try:
            validator = PreFlightValidator(self.master_resume)
            # Run validation, but we don't need the `failed_sections` set here,
            # as the retry loop is already finished.
            hop_results, all_passed, _ = validator.validate(
                staging_buffer, thematic_analysis, job_description,
                sections_under_test=None # Not in a retry loop
            ) 
            
            # Overwrite self.validation_results with this *final* post-sanitization check
            self.validation_results = hop_results 

            hop_checkpoint = self._create_checkpoint(
                "HOP-5", "Pre-flight Validation", hop_results,
                {"all_rules_checked": len(validator.engine.rules), "all_passed": all_passed},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            
            # Check status based on CRITICAL/HIGH failures
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=False)
            
            return hop_results
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-5] FAILED during validation logic: {e}", exc_info=True)
             error_result = ValidationResult("HOP-5_EXECUTION", False, ValidationSeverity.CRITICAL, f"Validation execution failed: {e}")
             hop_checkpoint = self._create_checkpoint(
                 "HOP-5", "Pre-flight Validation", [error_result],
                 {"all_rules_checked": 0, "all_passed": False},
                 start_time=hop_start_time, error_message=str(e)
             )
             hop_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop_checkpoint)
             self.validation_results = [error_result]
             raise HopExecutionError(f"HOP-5 failed: {e}")

    def _execute_hop_6_gate_decision(self, hop5_results: List[ValidationResult]) -> GateDecision:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-6] Gate Decision...")
        try:
            gate_engine = GateDecisionEngine()
            gate_decision, gate_reason = gate_engine.decide(hop5_results)

            self.logger.info(f"  Decision: {gate_decision.value}")
            self.logger.info(f"  Reason: {gate_reason}")

            hop_checkpoint = self._create_checkpoint(
                "HOP-6", "Gate Decision", [],
                {"decision": gate_decision.value, "reason": gate_reason},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)

            if gate_decision == GateDecision.HALT:
                raise HopExecutionError(f"HALT decision at HOP-6: {gate_reason}")

            return gate_decision
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-6] FAILED during decision logic: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-6", "Gate Decision",
                 [ValidationResult("HOP-6_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 {"decision": GateDecision.HALT.value, "reason": f"Error in decision engine: {e}"},
                 start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-6 failed: {e}")

    def _execute_hop_7_rendering(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str, thematic_analysis: ThematicAnalysis, job_description: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7] Rendering Output Files...")
        try:
            renderer = FileRenderer(self.master_resume, self)
            file_paths, (hop_results, file_contents) = renderer.render(
                staging_buffer, company_name, job_title, thematic_analysis, job_description
            )

            self.rendered_output = {
                'file_paths': file_paths,
                'file_contents': file_contents
            }

            hop_checkpoint = self._create_checkpoint(
                "HOP-7", "File Rendering", hop_results,
                file_paths, 
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint) 

            return file_paths, file_contents
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-7] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-7", "File Rendering",
                 [ValidationResult("HOP-7_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 None, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-7 failed: {e}")

    def _execute_hop_7_5_deduplication(self, staging_buffer: ImmutableStagingBuffer):
        """Executes HOP-7.5: Deduplication Analysis (for QA report)."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7.5] Computing Deduplication Metrics...")
        try:
            analysis_performed = self._invoke_deduplication_analysis(staging_buffer)
            if analysis_performed:
                self.logger.info("  ✓ Deduplication analysis complete.")
            else:
                self.logger.warning("  ⚠️ Deduplication analysis skipped or incomplete (check logs).")

            hop_checkpoint = self._create_checkpoint(
                "HOP-7.5", "Deduplication Analysis", [],
                { 
                    "matrix_max_sim": self.similarity_matrix_data.get('max_similarity', 0.0) if self.similarity_matrix_data else 0.0,
                    "overview_max_sim": max([d.get('max_similarity', 0.0) for d in self.overview_similarity_data], default=0.0) if self.overview_similarity_data else 0.0,
                    "exec_summary_max_sim": max([d.get('max_similarity', 0.0) for d in self.executive_summary_similarity_data], default=0.0) if self.executive_summary_similarity_data else 0.0, 
                },
                start_time=hop_start_time,
                metadata={"analysis_timestamp": self.dedup_analysis_timestamp}
            )
            hop_checkpoint.status = HopStatus.PASS
            self.hop_checkpoints.append(hop_checkpoint)

        except Exception as e:
            self.logger.error(f"  ✗ [HOP-7.5] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-7.5", "Deduplication Analysis",
                 [ValidationResult("HOP-7.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 None, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            
    def _execute_hop_8_qa_report(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, hop5_results: List[ValidationResult]) -> str:
        """Executes HOP-8: QA Report Generation."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-8] Generating QA Report...")
        try:
            qa_report_validation_results, qa_report_text, updated_file_contents = self._generate_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            if self.rendered_output and 'file_contents' in self.rendered_output:
                self.rendered_output['file_contents']['qa_report'] = qa_report_text

            hop_checkpoint = self._create_checkpoint(
                "HOP-8", "QA Report Generation", qa_report_validation_results, 
                {"qa_report_generated": True, "report_length": len(qa_report_text)},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint)
            return qa_report_text
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-8] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-8", "QA Report Generation",
                 [ValidationResult("HOP-8_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 {"qa_report_generated": False}, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-8 failed: {e}")

    # --- Main Workflow Execution Method (Unchanged) ---
    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> Dict:
        """
        Execute complete multi-hop workflow.
        (This method's internal logic remains the same, calling the
         refactored _execute_hop_3_artist_generation)
        """
        workflow_start = datetime.now()
        company_name = company_name.strip() if company_name and company_name.strip() else "Target_Company"
        job_title = job_title.strip() if job_title and job_title.strip() else "Target_Role"

        self.logger.info("=" * 80)
        self.logger.info(f"RESUME GENERATION ENGINE v{__version__} - GEMINI API")
        self.logger.info("=" * 80)
        self.logger.info(f"Company: {company_name}")
        self.logger.info(f"Position: {job_title}")
        self.logger.info(f"Started: {workflow_start.isoformat()}")
        self.logger.info("=" * 80)

        thematic_analysis = None
        staging_buffer = None
        hop5_results = []
        file_paths = {}
        file_contents = {}
        qa_report_text = "[QA Report Not Generated]"
        gate_decision = GateDecision.PROCEED 


        try:
            self.logger.info("\n[GATE-0] JD Input Validation...")
            jd_validation = self.jd_enforcer.validate_jd_input(job_description, "GATE-0")
            failed_jd_validations = [r for r in jd_validation if not r.passed]
            if failed_jd_validations:
                self.logger.warning(f"  ⚠️ JD Input Validation warnings: {len(failed_jd_validations)}")
                for val in failed_jd_validations[:3]: self.logger.warning(f"    - {val.details}")
            else: self.logger.info("  ✓ JD input validation passed.")

            thematic_analysis = self._execute_hop_0_jd_analysis(job_description)

            self.logger.info("\n[GATE-1] JD Parsing Validation...")
            if thematic_analysis:
                try: parsed_jd_for_validation = asdict(thematic_analysis)
                except: parsed_jd_for_validation = {} 
                self.jd_enforcer.validate_jd_parsing(parsed_jd_for_validation, "GATE-1")
            else: self.logger.warning("  Skipping GATE-1: HOP-0 failed.")

            extracted_data = self._execute_hop_1_clerk_extraction()

            self.logger.info("\n[GATE-2] Thematic Analysis Content Validation...")
            if thematic_analysis:
                 self.jd_enforcer.validate_thematic_analysis(thematic_analysis, "GATE-2")
            else: self.logger.warning("  Skipping GATE-2: HOP-0 failed.")

            enriched_scaffold = self._execute_hop_2_enrichment(extracted_data, thematic_analysis)

            self.logger.info("\n[GATE-3] Enrichment Content Validation...")
            self.jd_enforcer.validate_enrichment(enriched_scaffold, "GATE-3")

            self.logger.info("\n[GATE-4] Artist Input Validation...")
            if thematic_analysis:
                 self.jd_enforcer.validate_artist_inputs(enriched_scaffold, thematic_analysis, "GATE-4")
            else: self.logger.warning("  Skipping GATE-4: HOP-0 failed.")

            # --- THIS IS THE REFACTORED CALL ---
            artist_output = self._execute_hop_3_artist_generation(
                enriched_scaffold, job_description, thematic_analysis
            )
            # --- END REFACTORED CALL ---

            staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)
            
            # --- THIS CALL IS NOW A FINAL CONFIRMATION ---
            # The *actual* pass/fail logic already happened in HOP-3.
            # self.validation_results is already populated by HOP-3.
            # We re-run validation here on the *sanitized* buffer.
            hop5_results = self._execute_hop_5_validation(staging_buffer, thematic_analysis, job_description)
            # --- END MODIFICATION ---

            self.logger.info("\n[GATE-5] Pre-flight Buffer JD Validation...")
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")

            # HOP-6 now uses the results from HOP-5 (the post-sanitization check)
            gate_decision = self._execute_hop_6_gate_decision(hop5_results) 

            file_paths, file_contents = self._execute_hop_7_rendering(
                staging_buffer, company_name, job_title, thematic_analysis, job_description
            )

            self.logger.info("\n[GATE-7] File Output Validation...")
            self.jd_enforcer.validate_file_output(file_paths, "GATE-7")

            self._execute_hop_7_5_deduplication(staging_buffer) 

            qa_report_text = self._execute_hop_8_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            self.logger.info("\n[GATE-8] QA Report Content Validation...")
            self.jd_enforcer.validate_qa_report({"report": qa_report_text}, "GATE-8")

            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()

            coc_ledger = self._build_coc_ledger(
                workflow_start, workflow_end, thematic_analysis
            ) if thematic_analysis else {}

            self.logger.info("\n" + "=" * 80)
            self.logger.info("WORKFLOW COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"Duration: {duration:.2f}s")
            self.logger.info(f"Gate Decision: {gate_decision.value}")
            self.logger.info(f"Output Files: {len(file_paths)}")

            final_result = {
                "status": "SUCCESS",
                "gate_decision": gate_decision.value,
                "file_paths": file_paths,
                "qa_report": qa_report_text, 
                "coc_ledger": coc_ledger,
                "resume_md_content": file_contents.get('resume_md', ''),
                "skills_content": file_contents.get('skills', ''),
                "cover_letter_content": file_contents.get('cover_letter', ''),
                "app_tracker_content": file_contents.get('app_tracker', '{}'),
                "qa_report_content": qa_report_text,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "hash_chain": self.hash_chain
            }
            self.rendered_output = final_result 
            return final_result

        except HopExecutionError as e:
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW HALTED: {str(e)}")

            gate_decision_val = GateDecision.HALT.value
            reason = str(e)
            if self.hop_checkpoints:
                 last_checkpoint = self.hop_checkpoints[-1]
                 if last_checkpoint.hop_id == "HOP-6": 
                     gate_decision_info = last_checkpoint.metadata
                     gate_decision_val = gate_decision_info.get("decision", GateDecision.HALT.value)
                     reason = gate_decision_info.get("reason", str(e))
                 elif last_checkpoint.status == HopStatus.FAIL: 
                      reason = last_checkpoint.error_message or str(e)

            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, _ = self._generate_qa_report(
                         staging_buffer, thematic_analysis, self.validation_results
                     )
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after halt: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after halt: {qa_e}]"
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after halt]"


            final_result = {
                "status": "HALTED",
                "gate_decision": gate_decision_val,
                "reason": reason,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text, 
                "hash_chain": self.hash_chain,
                "resume_md_content": file_contents.get('resume_md', ''),
                "skills_content": file_contents.get('skills', ''),
                "cover_letter_content": file_contents.get('cover_letter', ''),
                "app_tracker_content": file_contents.get('app_tracker', '{}'),
                "qa_report_content": qa_report_text,
            }
            self.rendered_output = final_result 
            return final_result

        except Exception as e:
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW FAILED UNEXPECTEDLY: {type(e).__name__}: {str(e)}", exc_info=True)

            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, _ = self._generate_qa_report(
                         staging_buffer, thematic_analysis, self.validation_results
                     )
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after failure: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after error: {qa_e}]"
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after failure]"


            final_result = {
                "status": "FAILED",
                "error": f"{type(e).__name__}: {str(e)}",
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text, 
                "hash_chain": self.hash_chain
            }
            self.rendered_output = final_result 
            return final_result

    # --- Helper Methods (Unchanged) ---

    def _create_jd_analyzer(self) -> EnhancedJobDescriptionAnalyzer:
        """Creates the HOP-0 JD Analyzer instance."""
        api_key = os.environ.get("GEMINI_API_KEY")
        rag_config = RAGConfig() if 'RAGConfig' in globals() else None
        return EnhancedJobDescriptionAnalyzer(self.master_resume, enable_web_search=True, api_key=api_key, config=rag_config)

    def _create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        validation_results: List[ValidationResult],
        output_data: Any, 
        start_time: datetime, 
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None 
    ) -> HopCheckpoint:
        """Creates a HopCheckpoint object, calculates duration and hash."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        status = HopStatus.PASS 
        if error_message: 
            status = HopStatus.FAIL
        elif validation_results:
            if any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in validation_results):
                status = HopStatus.FAIL
            elif any(not vr.passed and vr.severity == ValidationSeverity.HIGH for vr in validation_results):
                 status = HopStatus.FAIL
            elif any(not vr.passed for vr in validation_results): 
                 status = HopStatus.WARNING

        output_hash = None
        if output_data is not None:
            try:
                if isinstance(output_data, dict):
                    def default_serializer(o):
                        if hasattr(o, '__dataclass_fields__'): return asdict(o)
                        if isinstance(o, ThematicAnalysis): return asdict(o)
                        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
                    output_str = json.dumps(output_data, sort_keys=True, separators=(',', ':'), default=default_serializer)
                elif isinstance(output_data, list):
                     try: output_str = json.dumps(sorted([str(item) for item in output_data]))
                     except TypeError: output_str = json.dumps([str(item) for item in output_data]) 
                elif isinstance(output_data, ThematicAnalysis):
                    output_str = json.dumps(asdict(output_data), sort_keys=True, separators=(',', ':'))
                else:
                    output_str = str(output_data) 
                output_hash = hashlib.sha256(output_str.encode('utf-8')).hexdigest()[:16]
            except (TypeError, Exception) as e:
                self.logger.warning(f"Could not calculate output hash for {hop_id} due to serialization error: {e}")
                output_hash = f"ErrorHashing: {type(e).__name__}"

        checkpoint = HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            status=status,
            timestamp_start=start_time.isoformat(),
            timestamp_end=end_time.isoformat(),
            output_hash=output_hash,
            validation_results=[copy.deepcopy(vr) for vr in validation_results],
            metadata=copy.deepcopy(metadata) or {}, 
            error_message=error_message
        )

        checkpoint.metadata["duration_seconds"] = round(duration, 3)

        if self.hash_chain:
            prev_hash = self.hash_chain[-1]
            chain_input = f"{prev_hash}|{hop_id}|{status.value}|{output_hash}|{checkpoint.timestamp_end}"
            current_chain_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()[:16]
        else:
            current_chain_hash = output_hash or f"{hop_id}_START_{status.value}"

        self.hash_chain.append(current_chain_hash)
        checkpoint.metadata["chain_hash"] = current_chain_hash 

        return checkpoint

    def _check_hop_status(self, checkpoint: HopCheckpoint, allow_warnings: bool = False, check_critical_only: bool = False):
      
        effective_status = checkpoint.status
        severity_threshold = ValidationSeverity.HIGH 
        halt_reason_prefix = "HIGH/CRITICAL"

        if check_critical_only:
             severity_threshold = ValidationSeverity.CRITICAL
             halt_reason_prefix = "CRITICAL"
             if checkpoint.status == HopStatus.FAIL and not any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in checkpoint.validation_results):
                  effective_status = HopStatus.PASS 

        if effective_status == HopStatus.FAIL:
            failed_results = sorted(
                [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity.value >= severity_threshold.value],
                key=lambda x: x.severity.value, reverse=True
            )
            highest_failure = failed_results[0] if failed_results else None
            reason = checkpoint.error_message or \
                     (f"{highest_failure.rule_id}: {highest_failure.message(highest_failure.details) if callable(highest_failure.message) else highest_failure.message}" if highest_failure else "Unknown failure")

            error_msg = f"[{checkpoint.hop_id}] FAILED - Halting workflow. Reason: {reason}"
            self.logger.error(f"  ✗ {error_msg}")

            failures_to_log = failed_results[:3]
            for vr in failures_to_log:
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 self.logger.error(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")

            raise HopExecutionError(f"{checkpoint.hop_id} failed validation ({halt_reason_prefix}). Halting.")

        elif checkpoint.status == HopStatus.WARNING:
            warnings = [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            self.logger.warning(f"  ⚠️ [{checkpoint.hop_id}] completed with {len(warnings)} warnings.")
            if not allow_warnings:
                 error_msg = f"[{checkpoint.hop_id}] FAILED - Warnings detected and not allowed. Halting."
                 self.logger.error(f"  ✗ {error_msg}")
                 raise HopExecutionError(error_msg)
            else:
                 for vr in warnings[:2]:
                     msg = vr.message(vr.details) if callable(vr.message) else vr.message
                     self.logger.warning(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")
                 self.logger.info(f"  ✓ {checkpoint.hop_id} completed (with warnings).")

        elif checkpoint.status == HopStatus.PASS:
            self.logger.info(f"  ✓ {checkpoint.hop_id} completed successfully.")
        else:
             self.logger.error(f"  ? Unknown status encountered for {checkpoint.hop_id}: {checkpoint.status}")

    def _build_coc_ledger(
        self,
        workflow_start: datetime,
        workflow_end: datetime,
        thematic_analysis: Optional[ThematicAnalysis] 
    ) -> Dict:
        """Builds the Chain of Custody (CoC) ledger dictionary."""
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', 'UnknownCandidate')}".encode('utf-8')
        ).hexdigest()[:16]

        rag_metadata = {}
        if thematic_analysis: 
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            rag_metadata = {
                "signal_quality": getattr(thematic_analysis, 'signal_quality_score', 0.0),
                "retrieval_method": getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN'),
                "peer_jds_analyzed": getattr(comp_intel, 'peer_jds_analyzed_count', 0) if comp_intel else 0,
                "differentiator_keywords": getattr(comp_intel, 'differentiator_keywords', [])[:10] if comp_intel else [], 
                "jd_input_hash": self.jd_enforcer.jd_hash if hasattr(self, 'jd_enforcer') else None
            }

        overall_status = HopStatus.PASS.value 
        if any(hc.status == HopStatus.FAIL for hc in self.hop_checkpoints):
             overall_status = HopStatus.FAIL.value
        elif self.hop_checkpoints: 
             overall_status = self.hop_checkpoints[-1].status.value

        hops_executed_list = []
        for hc in self.hop_checkpoints:
             try: hops_executed_list.append(asdict(hc))
             except Exception as e:
                 self.logger.warning(f"Could not serialize checkpoint {hc.hop_id}: {e}")
                 hops_executed_list.append({
                     "hop_id": hc.hop_id, "hop_name": hc.hop_name, "status": hc.status.value,
                     "error": "Serialization failed"
                 })

        return {
            "workflow_id": workflow_id,
            "engine_version": f"v{__version__}",
            "architecture_version": f"Job_Workflow_v12.50_StatefulRetry", # <-- Updated Arch Version
            "timestamp_start_utc": workflow_start.utcnow().isoformat() + "Z",
            "timestamp_end_utc": workflow_end.utcnow().isoformat() + "Z",
            "duration_seconds": round((workflow_end - workflow_start).total_seconds(), 3),
            "master_resume_version": self.master_resume.get("schema_version", "Unknown"),
            "hops_executed": hops_executed_list,
            "hash_chain_final": self.hash_chain[-1] if self.hash_chain else None,
            "rag_metadata": rag_metadata,
            "jd_enforcement_summary": {
                "total_checks": len(getattr(self.jd_enforcer, 'enforcement_results', [])),
                "passed_checks": sum(1 for r in getattr(self.jd_enforcer, 'enforcement_results', []) if r.passed),
                "failed_rules": [r.rule.name for r in getattr(self.jd_enforcer, 'enforcement_results', []) if not r.passed]
            },
            "overall_status": overall_status
        }

    def _build_qa_section_1_signal_quality(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        lines = ["", "1. SIGNAL QUALITY (Per-Section Analysis vs. JD Keywords)", ""]
        max_signal_target = SignalControlConfig().SECTION_SIGNAL_SCORE_MAX
        section_configs = PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG
        total_weighted_score, total_weight = 0.0, 0.0
        total_weighted_temp, temp_weight = 0.0, 0.0
        lines.append("```markdown")
        
        # --- NEW: Get final temps from HOP-3 metadata ---
        hop3_checkpoint = next((c for c in reversed(self.hop_checkpoints) if c.hop_id == "HOP-3"), None)
        final_temps = hop3_checkpoint.metadata.get("final_temperatures", {}) if hop3_checkpoint else {}
        # Convert keys from str back to Enum for lookup
        final_temps_enum = {ResumeSection[k]: v for k, v in final_temps.items() if k in ResumeSection.__members__}

        for label, (section_enum, target_min_score, target_max_score, weight, reasoning_config) in section_configs.items():
            content = staging_buffer.get(section_enum.value)
            if content:
                score = calculate_signal_score(content, thematic_analysis)
                total_weighted_score += score * weight
                total_weight += weight
                
                # --- Use the *actual* final temperature ---
                temp = final_temps_enum.get(section_enum)
                if temp is None: # Fallback if not found (e.g., failed generation)
                    api_params = reasoning_config_to_api_params(reasoning_config)
                    sc_count = api_params.get('sc', 1)
                    temp = 0.9 if sc_count > 1 else api_params["generation_config"].temperature
                
                total_weighted_temp += temp * weight
                temp_weight += weight
                lines.append(self._format_ascii_bar_chart(label=label, value=score, target_min=target_min_score, target_max=target_max_score, temperature=temp))
            else:
                lines.append(f"{label:<25} [SKIPPED]{' '*23} (Target: {target_min_score:.0%}) -")
        if total_weight > 0:
            average_signal = total_weighted_score / total_weight
            average_temp = total_weighted_temp / temp_weight if temp_weight > 0 else 0.0
            overall_min_target = 0.70
            overall_max_target = 0.85
            summary_bar = self._format_ascii_bar_chart(label="Total Weighted Score", value=average_signal, target_min=overall_min_target, target_max=overall_max_target, temperature=average_temp, is_summary=True)
            lines.append("-" * 80)
            lines.append(summary_bar)
        lines.append("```")
        return lines

    def _build_qa_section_2_signal_flow_map(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        lines = ["", "2. HOP-0 RAG SIGNAL FLOW MAP (Consumed Signals)", ""] 
        lines.append("This table shows how RAG intelligence (columns) was consumed by each generated resume section (rows), based on validation metrics or confirmed use in generation logic.")
        lines.append("")
        lines.append("```markdown")
        headers = [ "Target Section", "Primary Theme\n(AI Technical\n Success)", "Differentiator\nKeywords (e.g.,\n GenAI adoption,\n SaaS delivery,\n retention)", "Role Archetype\n(Post-Sales_Success)", "Problem-Solution\nNarrative (e.g.,\n 'slow adoption')", "Secondary Themes\n(e.g., Team Scaling)", "Authenticity Patterns\n(Voice & Phrasing)" ]
        rows_config = [
            {"section": ResumeSection.K0_HEADLINE, "label": "K.0 (Headline)", "signals": ["Primary", "Diff_Pct", "Archetype", None, None, "Auth"]},
            {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "label": "K.1 (Exec Summary)", "signals": ["Primary", "Diff_Count", "Archetype", None, "Secondary", "Auth"]},
            {"section": ResumeSection.K5_UNIFY_BULLETS, "label": "K.5 (Unify Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K5_UNIFY_OVERVIEW, "label": "K.5 (Unify Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K6_IBM_BULLETS, "label": "K.6 (IBM Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K6_IBM_OVERVIEW, "label": "K.6 (IBM Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K7_TRADERSENSE_BULLETS, "label": "K.7 (TraderSense)", "signals": [None, None, None, None, None, None]}, 
            {"section": ResumeSection.K8_EY_BULLETS, "label": "K.8 (EY Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K8_EY_OVERVIEW, "label": "K.8 (EY Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K9_EARLY_CAREER_BULLETS, "label": "K.9 (Early Career Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "label": "K.9 (Early Career Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K10_COMPETENCIES, "label": "K.10 (Comp.)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K2_SKILLS, "label": "K.2 (Skills)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", None]},
            {"section": ResumeSection.K13_COVER_LETTER, "label": "K.13 (C.L.)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
        ]
        table_rows = []
        for row_cfg in rows_config:
            section_label = row_cfg["label"]
            signal_presence = row_cfg["signals"]
            content = staging_buffer.get(row_cfg["section"].value)
            row_data = [section_label]
            row_data.append("✓" if signal_presence[0] == "Primary" else "N/A")
            if signal_presence[1] == "Diff_Pct" and content:
                 score = calculate_signal_score(content, thematic_analysis) 
                 row_data.append(f"{score:.1%}")
            elif signal_presence[1] == "Diff_Count" and content:
                diff_count = 0
                differentiators = [] 
                if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
                    differentiators = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', []) or []
                if differentiators:
                    summary_lower = str(content).lower()
                    diff_count = sum(1 for kw in differentiators if kw and kw.lower() in summary_lower)
                row_data.append(f"{diff_count}/{len(differentiators)} Found")
            else:
                row_data.append("N/A")
            row_data.append("✓" if signal_presence[2] == "Archetype" else "N/A")
            row_data.append("✓" if signal_presence[3] == "Narrative" else "N/A")
            row_data.append("✓" if signal_presence[4] == "Secondary" else "N/A")
            row_data.append("✓" if signal_presence[5] == "Auth" else "✗")
            table_rows.append(row_data)
        col_widths = [20, 20, 18, 18, 18, 18, 20]
        lines.extend(self._format_plain_text_table(headers, table_rows, col_widths=col_widths, wrap_text=True))
        lines.append("```")
        lines.append("Legend: ✓ = Signal Consumed, ✗ = Signal Not Consumed, N/A = Not Applicable, Pct/Count = Validation Metric")
        return lines

    def _build_qa_section_3_hop_summary(self) -> List[str]:
        lines = ["", "3. HOP-BY-HOP EXECUTION SUMMARY", ""] 
        lines.append("```markdown")
        headers = ["Hop ID", "Hop Name", "Status", "Duration (s)", "Output Hash", "Chain Hash"]
        rows = []
        for hop in self.hop_checkpoints:
            duration = hop.metadata.get("duration_seconds", -1.0)
            chain_hash = hop.metadata.get("chain_hash", "N/A")
            rows.append([
                hop.hop_id, hop.hop_name, hop.status.value,
                f"{duration:.3f}" if duration >= 0 else "N/A",
                hop.output_hash or "N/A",
                chain_hash
            ])
        expected_rows = len(self.hop_checkpoints)
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} hop rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_4_word_count_distribution(self, validation_results: List[ValidationResult]) -> List[str]:
        lines = ["", "4. WORD COUNT & DISTRIBUTION COMPLIANCE", ""]
        lines.append("This section combines overall resume word count checks, key section constraints (Headline, Exec Summary, Cover Letter paragraphs), and distribution metrics (Unify/IBM) into a single table. Bullet length validation is covered in Section 6.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section", "Rule ID", "Value", "Target Range", "Status", "Message / Details"]
        rows = []
        rules_to_include = {
            "VG_TOTAL_WORD_COUNT": "Overall Resume",
            "VG_HEADLINE_WORD_COUNT": "Headline",
            "VG_WORD_COUNT_K1": "Executive Summary",
            "VG_SENTENCE_COUNT_K1": "Executive Summary",
            "WORD_DISTRIBUTION_UNIFY_IBM": "Experience Dist.",
            "UNIFY_IBM_RATIO": "Experience Dist.",
            "CL_P1_WORD_COUNT": "Cover Letter",
            "CL_P2_WORD_COUNT": "Cover Letter",
            "CL_P3_WORD_COUNT": "Cover Letter",
        }
        cl_structure_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_STRUCTURE"), None)
        cl_paragraph_details = {}
        if cl_structure_result and isinstance(cl_structure_result.details, dict):
             cl_paragraph_details = cl_structure_result.details
        for rule_id, section_label in rules_to_include.items():
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
            if rule_id.startswith("CL_P"):
                p_num = rule_id.split('_')[1] 
                p_key_wc = f"{p_num.lower()}_wc" 
                p_key_min = f"{p_num.lower()}_min"
                p_key_max = f"{p_num.lower()}_max"
                if not cl_structure_result or not cl_structure_result.passed:
                     specific_cl_rule = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
                     if specific_cl_rule:
                         wc = specific_cl_rule.details.get(p_key_wc, 0)
                         min_r = specific_cl_rule.details.get(p_key_min, 0)
                         max_r = specific_cl_rule.details.get(p_key_max, 0)
                         status = "PASS" if specific_cl_rule.passed else "FAIL"
                         msg = specific_cl_rule.message if not specific_cl_rule.passed else ""
                         value_str = f"{wc} words"
                         target_str = f"{min_r}-{max_r}"
                         rows.append([section_label, rule_id, value_str, target_str, status, msg])
                     else: 
                         rows.append([section_label, rule_id, "N/A", "N/A", "FAIL", "CL_STRUCTURE failed or details missing"])
                elif p_key_wc in cl_paragraph_details:
                    wc = cl_paragraph_details.get(p_key_wc, 0)
                    min_r = cl_paragraph_details.get(p_key_min, 0)
                    max_r = cl_paragraph_details.get(p_key_max, 0)
                    status = "PASS" if min_r <= wc <= max_r else "FAIL" 
                    msg = "" if status == "PASS" else f"{rule_id} count {wc} out of range {min_r}-{max_r}"
                    value_str = f"{wc} words"
                    target_str = f"{min_r}-{max_r}"
                    rows.append([section_label, rule_id, value_str, target_str, status, msg])
                else:
                    rows.append([section_label, rule_id, "N/A", "N/A", "WARN", f"Details missing for {rule_id}"])
            elif result:
                details = result.details or {}
                value_str = "N/A"
                if 'total_words' in details: value_str = f"{details['total_words']} words"
                elif 'word_count' in details: value_str = f"{details['word_count']} words"
                elif 'sentence_count' in details: value_str = f"{details['sentence_count']} sentences"
                elif 'percent' in details: value_str = f"{details['percent']:.1f}%"
                elif 'ratio' in details: value_str = f"{details.get('ratio', 'N/A')}"
                target_str = "N/A"
                if 'min' in details and 'max' in details:
                    target_str = f"{details['min']}-{details['max']}"
                    if '%' in value_str: target_str += "%"
                    elif 'sentences' in value_str: pass 
                    elif 'words' in value_str: pass 
                    else: 
                         if isinstance(details['min'], float): target_str = f"{details['min']:.1f}-{details['max']:.1f}"
                status = "PASS" if result.passed else "FAIL"
                msg = result.message if not result.passed else ""
                if callable(msg): msg = msg(details)
                rows.append([section_label, rule_id, value_str, target_str, status, msg])
            else:
                rows.append([section_label, rule_id, "N/A", "N/A", "WARN", "Validation result not found"])
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_5_provenance(self, staging_buffer: ImmutableStagingBuffer) -> List[str]:
        lines = ["", "5. BULLET PROVENANCE & WORD COUNT", ""]
        lines.append("```markdown")
        headers = ["Section", "Item", "Provenance", "Word Count", "Target Range", "Status", "Text Snippet"]
        rows = []
        master_avg_lengths = self._calculate_master_avg_bullet_length()
        logging.info(f"Using Master Averages for QA Sec 5: {master_avg_lengths}")
        tolerance = 0.20 
        for section_data in self.QA_PROVENANCE_SECTIONS:
            name = section_data["name"] 
            bullets_enum = section_data.get("bullets_enum")
            if bullets_enum:
                avg_key = name if name in master_avg_lengths else "Default"
                avg_len = master_avg_lengths.get(avg_key, 25.0) 
                logging.debug(f"Processing Section '{name}', using avg_key='{avg_key}', avg_len={avg_len:.1f}")
                bullets = staging_buffer.get(bullets_enum.value, [])
                if isinstance(bullets, list) and bullets:
                    for i, bullet_item in enumerate(bullets):
                        bullet_text, word_count, provenance = "", 0, "N/A" 
                        if isinstance(bullet_item, dict):
                            bullet_text = bullet_item.get('text', bullet_item.get('bullet_text','')) 
                            word_count = bullet_item.get('word_count', count_words_ms_word_style(bullet_text)) 
                            provenance = bullet_item.get('provenance', 'N/A')
                        elif isinstance(bullet_item, str):
                            bullet_text = bullet_item
                            word_count = count_words_ms_word_style(bullet_text)
                            provenance = BulletProvenance.Verbatim.value if bullets_enum == ResumeSection.K7_TRADERSENSE_BULLETS else "N/A"
                        else:
                            logging.warning(f"Unexpected item type in {bullets_enum.value}[{i}]: {type(bullet_item)}. Skipping.")
                            continue 
                        min_target = round(avg_len * (1 - tolerance))
                        max_target = round(avg_len * (1 + tolerance))
                        logging.debug(f"  Bullet {i+1}: WordCount={word_count}, Avg={avg_len:.1f}, Tol={tolerance:.0%}, Target={min_target}-{max_target}")
                        status, target_range_str = self._check_word_count(word_count, min_target, max_target)
                        rows.append([ name, str(i + 1), provenance, str(word_count), target_range_str, status, bullet_text[:60] + ("..." if len(bullet_text) > 60 else "") ])
                elif not isinstance(bullets, list):
                    logging.warning(f"Expected list for bullets in section '{name}' ({bullets_enum.value}), but got {type(bullets)}. Skipping.")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines
    
    def _build_qa_section_6_authenticity(self, validation_results: List[ValidationResult]) -> List[str]:
        lines = ["", "6. CONTENT AUTHENTICITY (Hallucination & Signal Check)", ""] 
        auth_results = [vr for hop in self.hop_checkpoints for vr in hop.validation_results if "HALLUCINATION" in vr.rule_id]
        auth_signal_check = next((vr for vr in validation_results if vr.rule_id == "VG_AUTHENTICITY_SIGNAL_CHECK"), None)
        if auth_signal_check: auth_results.append(auth_signal_check) 
        lines.append("```markdown")
        headers = ["Check ID", "Status", "Message / Details"]
        rows = []
        expected_rows = 0
        if auth_results:
             auth_results.sort(key=lambda vr: vr.rule_id) 
             expected_rows = len(auth_results)
             for vr in auth_results:
                  msg = vr.message(vr.details) if callable(vr.message) else vr.message
                  details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                  rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{msg}{details_str}"])
        else:
             rows = [["AUTHENTICITY_CHECKS", "PASS", "No hallucination checks run or all passed; Authenticity signal check passed or not run."]]
             expected_rows = 1
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} auth rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_7_exec_summary_similarity(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds the NEW QA Section 7 table: Exec Summary vs. Section Similarity."""
        lines = ["", "7. EXECUTIVE SUMMARY VS. SECTION CONTENT SIMILARITY", ""]
        lines.append("This table shows the cosine similarity between the Executive Summary (K.1) and the combined text (overview + bullets) of other key resume sections. High similarity scores relative to the threshold might indicate potential redundancy.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section Compared to Exec Summary", "Cosine Similarity", "Threshold", "Status"]
        rows = []

        # Define thresholds here, matching the validator logic
        thresholds = {
            "Competencies (K.10 Items)": 0.30,
            "Unify (K.5 Overview + Bullets)": 0.60,
            "IBM (K.6 Overview + Bullets)": 0.50,
            "EY (K.8 Overview + Bullets)": 0.30,
            "Early Career (K.9 Overview + Bullets)": 0.30,
        }

        # Find the specific validation result from the final validation run (self.validation_results)
        # Use self.validation_results as it holds the results from the final HOP-5 check
        final_validation_results = self.validation_results
        similarity_result = next((vr for vr in final_validation_results if vr.rule_id == "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY"), None)

        similarity_scores = {}
        # Parse failure details if the rule failed
        if similarity_result and not similarity_result.passed and isinstance(similarity_result.details, dict):
            failures_str = similarity_result.details.get("failures", "")
            # Example failure string: "Competencies (K.10 Items): 0.35 (Threshold: < 0.30); IBM (K.6 Overview + Bullets): 0.52 (Threshold: < 0.50)"
            if failures_str:
                parts = failures_str.split('; ')
                for part in parts:
                    match = re.match(r"^(.*?): (\d\.\d+)", part)
                    if match:
                        section_label = match.group(1).strip()
                        # Only store scores for sections defined in our thresholds dict
                        if section_label in thresholds:
                             score = float(match.group(2))
                             similarity_scores[section_label] = score

        # Populate rows based on thresholds and calculated/parsed scores
        for label, threshold in thresholds.items():
            score = similarity_scores.get(label) # Returns None if section passed or rule didn't run properly
            status = "FAIL" if score is not None else "PASS"
            # If it passed, we don't have the score from the failure message.
            # We could recalculate here, but for simplicity in the report, indicate it passed.
            # Or, we could attempt to calculate it on the fly if needed for reporting.
            # Let's show "N/A (PASS)" if the rule passed overall or specific section passed.
            # If the rule failed but *this specific section* passed, score is None.
            score_str = f"{score:.4f}" if score is not None else "N/A (PASS)"

            rows.append([
                label,
                score_str,
                f"< {threshold:.2f}",
                status
            ])

        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_8_pairwise_similarity(self) -> List[str]:
        lines = ["", "8. PAIRWISE BULLET SIMILARITY (Deduplication)", ""]
        lines.append("```markdown")
        headers = ["Bullet 1", "Bullet 2", "Similarity", "Status"]
        rows = []
        if not self.similarity_matrix_data:
            lines.append("(Pairwise similarity analysis was not performed or found no data.)")
            lines.append("```")
            return lines
        duplicates = self.similarity_matrix_data.get('duplicates_found', [])
        expected_rows = 0
        if duplicates:
            expected_rows = len(duplicates)
            for dup in duplicates:
                rows.append([dup['bullet_1'], dup['bullet_2'], f"{dup['similarity']:.4f}", "✗ FAIL"])
        lines.extend(self._format_plain_text_table(headers, rows))
        if len(rows) != expected_rows and duplicates:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} duplicate rows, got {len(rows)}")
        if not duplicates:
            # Clean up potential "(No data available)" line if needed
            if lines[-1] == "(No data available)": lines.pop()
            lines.append("  No duplicates found (Similarity < 0.90).")
        lines.append("\n-- Summary --")
        lines.append(f"  Total Comparisons Made: {self.similarity_matrix_data.get('total_comparisons', 0)}")
        lines.append(f"  Maximum Similarity Found: {self.similarity_matrix_data.get('max_similarity', 0.0):.4f}")
        lines.append(f"  Duplicates Found (>= 0.90): {len(duplicates)}")
        lines.append("```")
        return lines

    def _build_qa_section_9_pipeline_health(self) -> List[str]:
        lines = ["", "9. PIPELINE HEALTH (Resource Consumption)", ""] 
        lines.append("```markdown")
        headers = ["Hop ID", "Hop Name", "Status", "RAG API Calls", "LLM API Calls"]
        rows = []
        total_rag_calls, total_llm_api_calls = 0, 0
        for hop in self.hop_checkpoints:
            searches = hop.metadata.get('web_search_calls', 0)
            llm_calls = hop.metadata.get('llm_api_calls', 0)
            # --- START FIX: Add Hop 3 attempts to LLM calls ---
            if hop.hop_id == "HOP-3":
                 # Estimate calls based on attempts and locked sections
                 # This is an approximation. A more accurate way would be
                 # for the Artist to report how many calls it *actually* made.
                 # For now, use attempts_made * (avg sections per attempt)
                 # Let's use the 'attempts_made' metadata
                 llm_calls = hop.metadata.get('attempts_made', 0) 
            # --- END FIX ---
            rows.append([hop.hop_id, hop.hop_name, hop.status.value, str(searches), str(llm_calls)])
            total_rag_calls += searches
            total_llm_api_calls += llm_calls
        rows.append(["TOTAL", "", "", str(total_rag_calls), str(total_llm_api_calls)])
        expected_rows = len(self.hop_checkpoints) + 1
        if len(rows) != expected_rows:
            lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} health rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows, ['L', 'L', 'L', 'R', 'R']))
        lines.append("```")
        return lines

    def _build_qa_section_10_structural(self, validation_results: List[ValidationResult]) -> List[str]:
        lines = ["", "10. STRUCTURAL VALIDATION (Content Presence)", ""] 
        struct_rule_ids = [ "STRUCTURE_", "COVER_LETTER_SIGNATURE" ]
        struct_results = [vr for vr in validation_results if any(rid in vr.rule_id for rid in struct_rule_ids)]
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        expected_rows = 0
        if struct_results:
             struct_results.sort(key=lambda vr: vr.rule_id)
             expected_rows = len(struct_results)
             for vr in struct_results:
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                 final_msg = msg if not vr.passed else ""
                 rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg}{details_str}"])
        else:
             rows = [["N/A", "INFO", "No structural presence validation results found."]]
             expected_rows = 1
        if len(rows) != expected_rows and struct_results:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} structural rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines
    
    def _build_qa_section_11_prod_readiness(self, validation_results: List[ValidationResult]) -> List[str]:
        lines = ["", "11. PRODUCTION READINESS", ""] 
        lines.append("```markdown")
        all_results = validation_results + [vr for hop in self.hop_checkpoints for vr in hop.validation_results]
        critical_failures = [vr for vr in all_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
        high_failures = [vr for vr in all_results if not vr.passed and vr.severity == ValidationSeverity.HIGH]
        prod_ready = not critical_failures and not high_failures
        headers = ["Check", "Value", "Status"]
        rows = [
            ["Production Ready", str(prod_ready).upper(), "✅ PASS" if prod_ready else "❌ FAIL"],
            ["Critical Failures", len(critical_failures), "✅" if not critical_failures else "❌"],
            ["High Failures", len(high_failures), "✅" if not high_failures else "❌"]
        ]
        expected_rows = 3
        if len(rows) != expected_rows: rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"FAIL - Rows={len(rows)}"])
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if not prod_ready:
            lines.append("\n  Reason: Production readiness requires zero CRITICAL or HIGH severity failures.")
            if critical_failures:
                lines.append("  CRITICAL FAILURES:")
                for f in critical_failures[:3]:
                     msg = f.message(f.details) if callable(f.message) else f.message
                     lines.append(f"    - {f.rule_id}: {msg}")
            if high_failures:
                lines.append("  HIGH FAILURES:")
                for f in high_failures[:3]:
                     msg = f.message(f.details) if callable(f.message) else f.message
                     lines.append(f"    - {f.rule_id}: {msg}")
        return lines

    def _build_qa_section_12_cover_letter(self, validation_results: List[ValidationResult]) -> List[str]:
        lines = ["", "12. COVER LETTER QA", ""] 
        cl_results = [vr for vr in validation_results if "COVER_LETTER" in vr.rule_id and vr.rule_id != "COVER_LETTER_STRUCTURE"] 
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        expected_rows = 0
        if cl_results:
             cl_results.sort(key=lambda vr: vr.rule_id)
             expected_rows = len(cl_results)
             for vr in cl_results:
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                 rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{msg}{details_str}"])
        else:
             rows = [["N/A", "INFO", "No cover letter QA results (excluding paragraph counts) found."]]
             expected_rows = 1
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} CL rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_13_jd_enforcement(self) -> List[str]:
        lines = ["", "13. JD ENFORCEMENT VALIDATION", ""] 
        lines.append("```markdown")
        headers = ["Gate", "Rule", "Status", "Details"]
        enforcement_results = getattr(self.jd_enforcer, 'enforcement_results', [])
        rows = [[res.gate_id, res.rule.name, "PASS" if res.passed else "FAIL", res.details] for res in enforcement_results]
        expected_rows = len(enforcement_results)
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} JD rows, got {len(rows)}")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_14_final_format(
        self,
        validation_results: List[ValidationResult],
        file_contents: Dict[str, str]
    ) -> List[str]:
        lines = ["", "14. FORMATTING OF OUTPUTS", ""] 
        lines.append("Verifies the presence and correct formatting of all generated output files based on rendering logic and structural validation rules.") 
        lines.append("")
        lines.append("```markdown")
        headers = ["Artifact", "Check Type", "Requirement", "Status", "Failure Explanation"] 
        output_definitions = []
        resume_content = file_contents.get('resume_md', '')
        output_definitions.append(("**Resume**", "Presence/Type", "Raw Text / Markdown", "PASS" if resume_content else "FAIL", "" if resume_content else "Content missing."))
        if resume_content:
            name_pass = resume_content.startswith("## ")
            output_definitions.append(("**Resume**", "K.0 Name Format", "## Format", "PASS" if name_pass else "FAIL", "" if name_pass else "Name does not start with H2 (##)."))
            headline_match = re.search(r"^## .+\n+(\S.+)\n", resume_content)
            headline_text = headline_match.group(1).strip() if headline_match else ""
            headline_pass = headline_match is not None and not headline_text.startswith("#") and "|" in headline_text
            output_definitions.append(("**Resume**", "K.0 Headline Format", "Plain Text", "PASS" if headline_pass else "FAIL", "" if headline_pass else "Headline missing, uses Markdown, or missing pipes."))
            lb_pass = bool(re.search(r"^## .+\n\n\S.+\n", resume_content))
            output_definitions.append(("**Resume**", "Headline/Name Break", "Single Blank Line", "PASS" if lb_pass else "FAIL", "" if lb_pass else "Missing/incorrect blank line."))
            comma_check_result = next((vr for vr in validation_results if vr.rule_id == "VG_HEADLINE_NO_COMMAS"), None)
            comma_pass = comma_check_result.passed if comma_check_result else False
            output_definitions.append(("**Resume**", "Headline Commas", "VG_HEADLINE_NO_COMMAS", "PASS" if comma_pass else "FAIL", "" if comma_pass else comma_check_result.message if comma_check_result else "Check missing"))
            h2_check_result = next((vr for vr in validation_results if vr.rule_id == "VG_RESUME_HEADER_H2"), None)
            h2_pass = h2_check_result.passed if h2_check_result else True 
            output_definitions.append(("**Resume**", "Section Headers", "VG_RESUME_HEADER_H2", "PASS" if h2_pass else "FAIL", "" if h2_pass else h2_check_result.message if h2_check_result else "Check missing"))
            exp_render_result = next((vr for vr in validation_results if vr.rule_id == "VG_EXPERIENCE_RENDER_FORMAT"), None)
            exp_render_pass = exp_render_result.passed if exp_render_result else True
            output_definitions.append(("**Resume**", "Experience Header", "VG_EXPERIENCE_RENDER_FORMAT", "PASS" if exp_render_pass else "FAIL", "" if exp_render_pass else exp_render_result.message if exp_render_result else "Check missing"))
            exp_bullet_result = next((vr for vr in validation_results if vr.rule_id == "VG_EXPERIENCE_BULLET_STYLE"), None)
            exp_bullet_pass = exp_bullet_result.passed if exp_bullet_result else True
            output_definitions.append(("**Resume**", "Experience Bullets", "VG_EXPERIENCE_BULLET_STYLE", "PASS" if exp_bullet_pass else "FAIL", "" if exp_bullet_pass else exp_bullet_result.message if exp_bullet_result else "Check missing"))
            edu_cert_result = next((vr for vr in validation_results if vr.rule_id == "VG_EDU_CERTS_FORMAT"), None)
            edu_cert_pass = edu_cert_result.passed if edu_cert_result else True
            output_definitions.append(("**Resume**", "Edu/Cert Formatting", "VG_EDU_CERTS_FORMAT", "PASS" if edu_cert_pass else "FAIL", "" if edu_cert_pass else edu_cert_result.message if edu_cert_result else "Check missing"))
            comp_format_result = next((vr for vr in validation_results if vr.rule_id == "VG_COMPETENCIES_FORMATTING"), None)
            comp_format_pass = comp_format_result.passed if comp_format_result else True
            output_definitions.append(("**Resume**", "Competency Formatting", "VG_COMPETENCIES_FORMATTING", "PASS" if comp_format_pass else "FAIL", "" if comp_format_pass else comp_format_result.message if comp_format_result else "Check missing"))
            lb_count = resume_content.count('\n\n')
            expected_min_lbs = 10
            lb_pass = lb_count >= expected_min_lbs
            output_definitions.append(("**Resume**", "Line Breaks", "Proper Line Breaks", "PASS" if lb_pass else "WARN", "" if lb_pass else f"Found {lb_count} blank lines, expected ~{expected_min_lbs}+."))
        skills_content = file_contents.get('skills', '')
        output_definitions.append(("**Skills**", "Presence/Type", "Raw Text", "PASS" if skills_content else "FAIL", "" if skills_content else "Content missing."))
        if skills_content:
            skills_lines = [line.strip() for line in skills_content.strip().split('\n') if line.strip()]
            bullet_pass = all(line.startswith("• ") for line in skills_lines) if skills_lines else True 
            output_definitions.append(("**Skills**", "Bullet Format", "`• ` Used", "PASS" if bullet_pass else "FAIL", "" if bullet_pass else "Skills not using '• ' format."))
            newline_pass = skills_content.strip().count('\n') >= (len(skills_lines) - 1) if len(skills_lines) > 1 else True
            output_definitions.append(("**Skills**", "Line Breaks", "Newlines Between Skills", "PASS" if newline_pass else "FAIL", "" if newline_pass else "Missing newlines between skills."))
        cl_content = file_contents.get('cover_letter', '')
        output_definitions.append(("**Cover L.**", "Presence/Type", "Raw Text", "PASS" if cl_content else "FAIL", "" if cl_content else "Content missing."))
        if cl_content:
            cl_struct_result = next((vr for vr in validation_results if vr.rule_id == "VG_COVER_LETTER_FULL_STRUCTURE"), None)
            cl_struct_pass = cl_struct_result.passed if cl_struct_result else False
            output_definitions.append(("**Cover L.**", "Overall Structure", "Standard Letter Format Present", "PASS" if cl_struct_pass else "FAIL", "" if cl_struct_pass else cl_struct_result.message if cl_struct_result else "Check missing"))
            cl_sig_multi_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_SIGNATURE_MULTILINE"), None)
            cl_sig_multi_pass = cl_sig_multi_result.passed if cl_sig_multi_result else False
            output_definitions.append(("**Cover L.**", "Signature Format", "COVER_LETTER_SIGNATURE_MULTILINE", "PASS" if cl_sig_multi_pass else "FAIL", "" if cl_sig_multi_pass else cl_sig_multi_result.message if cl_sig_multi_result else "Check missing"))
        qa_content = file_contents.get('qa_report', '')
        output_definitions.append(("**QA Report**", "Presence/Type", "Fenced Markdown", "PASS" if qa_content else "FAIL", "" if qa_content else "Content missing."))
        if qa_content:
            fence_pass = "```markdown" in qa_content and qa_content.strip().endswith("```")
            output_definitions.append(("**QA Report**", "Markdown Fences", "Uses Fenced Markdown", "PASS" if fence_pass else "FAIL", "" if fence_pass else "Missing markdown fences."))
            table_pass = qa_content.count("```markdown") >= 2 
            output_definitions.append(("**QA Report**", "Table Format", "Uses Pre-formatted Tables", "PASS" if table_pass else "WARN", "" if table_pass else "Could not verify presence of pre-formatted tables."))
            section_headers = ["1. SIGNAL QUALITY", "2. HOP-0 RAG SIGNAL FLOW MAP", "3. HOP-BY-HOP", "13. JD ENFORCEMENT", "14. FORMATTING OF OUTPUTS"] 
            missing_qa_headers = [h for h in section_headers if h not in qa_content]
            structure_pass = not missing_qa_headers
            output_definitions.append(("**QA Report**", "Headers", "Consistent Section Structure", "PASS" if structure_pass else "FAIL", "" if structure_pass else f"Missing headers: {missing_qa_headers}"))
            sec1_content_match = re.search(r"1\. SIGNAL QUALITY\s*```markdown(.*?)```", qa_content, re.DOTALL)
            sec1_content = sec1_content_match.group(1) if sec1_content_match else ""
            sec1_bar_pass = '[█' in sec1_content
            output_definitions.append(("**QA Report**", "Sec 1 Chart", "Uses ASCII Bar Chart", "PASS" if sec1_bar_pass else "FAIL", "" if sec1_bar_pass else "Missing ASCII bar chart."))
            sec1_details_pass = '(Tgt:' in sec1_content and 'Signal' in sec1_content and ('(T:' in sec1_content or '(Avg T:' in sec1_content)
            output_definitions.append(("**QA Report**", "Sec 1 Details", "Includes Targets/Status/Temp", "PASS" if sec1_details_pass else "FAIL", "" if sec1_details_pass else "Missing Target/Status/Temp indicators."))
            sec1_avg_pass = 'Total Weighted Score' in sec1_content and '(Avg T:' in sec1_content
            output_definitions.append(("**QA Report**", "Sec 1 Average", "Includes Weighted Average", "PASS" if sec1_avg_pass else "FAIL", "" if sec1_avg_pass else "Missing Weighted Average or Avg Temp."))
            sec1_fence_pass = bool(sec1_content_match)
            output_definitions.append(("**QA Report**", "Sec 1 Fence", "Uses Code Fence", "PASS" if sec1_fence_pass else "FAIL", "" if sec1_fence_pass else "Section 1 not within ```markdown fence."))
        app_content = file_contents.get('app_tracker', '')
        output_definitions.append(("**App Trkr**", "Presence/Type", "JSON Block (Unfenced)", "PASS" if app_content else "FAIL", "" if app_content else "Content missing."))
        if app_content:
            is_fenced = app_content.strip().startswith("```json") and app_content.strip().endswith("```")
            fence_check_pass = not is_fenced
            json_valid, parsed_json_data, json_fail_reason = False, None, "Unknown JSON error"
            try:
                content_to_parse = app_content.strip()
                if is_fenced:
                    content_to_parse = content_to_parse[7:-3].strip()
                    output_definitions[-1] = ("**App Trkr**", "Presence/Type", "JSON Block (Unfenced)", "FAIL", "App Tracker incorrectly includes ```json fences.") 
                parsed_json_data = json.loads(content_to_parse)
                json_valid = True
            except json.JSONDecodeError as e: json_fail_reason = f"Invalid JSON: {e}"
            output_definitions.append(("**App Trkr**", "JSON Validity", "Valid JSON Structure", "PASS" if json_valid else "FAIL", "" if json_valid else json_fail_reason))
            schema_pass, schema_fail_reason = False, "Cannot check schema, JSON invalid."
            if json_valid and isinstance(parsed_json_data, dict):
                schema_keys, actual_keys = set(APP_TRACKER_SCHEMA_V4.keys()), set(parsed_json_data.keys())
                schema_pass = schema_keys == actual_keys
                missing_keys, extra_keys = schema_keys - actual_keys, actual_keys - schema_keys
                schema_fail_reason = ""
                if missing_keys: schema_fail_reason += f"Missing keys: {sorted(list(missing_keys))}. "
                if extra_keys: schema_fail_reason += f"Extra keys: {sorted(list(extra_keys))}."
                if not schema_fail_reason: schema_fail_reason = "Keys match schema."
            output_definitions.append(("**App Trkr**", "Schema", "Adheres to APP_TRACKER_SCHEMA_V4", "PASS" if schema_pass else "FAIL", schema_fail_reason.strip()))
        final_rows = [[item[0], item[1], item[2], item[3], item[4]] for item in output_definitions]
        col_widths = [13, 36, 34, 8, 0] 
        lines.extend(self._format_plain_text_table(headers, final_rows, alignments=['L', 'L', 'L', 'L', 'L'], col_widths=col_widths, wrap_text=False)) 
        lines.append("```")
        return lines
    
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]}, 
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]}, 
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]}, 
        {"method": "_build_qa_section_6_authenticity", "args": ["validation_results"]}, 
        {"method": "_build_qa_section_7_exec_summary_similarity", "args": []}, 
        {"method": "_build_qa_section_8_pairwise_similarity", "args": []}, 
        {"method": "_build_qa_section_9_pipeline_health", "args": []}, 
        {"method": "_build_qa_section_10_structural", "args": ["validation_results"]}, 
        {"method": "_build_qa_section_11_prod_readiness", "args": ["validation_results"]}, 
        {"method": "_build_qa_section_12_cover_letter", "args": ["validation_results"]}, 
        {"method": "_build_qa_section_13_jd_enforcement", "args": []}, 
        {"method": "_build_qa_section_14_final_format", "args": ["validation_results", "file_contents"]}, 
    ]

    def _generate_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> Tuple[List[ValidationResult], str, Dict[str, str]]: 
        """
        Generate full QA report by iterating through a configuration of section builders.
        (Unchanged from v12.10)
        """
        validation_results_out = []
        report_lines = [
            f"RESUME QA REPORT (v{__version__})", 
            f"Generated: {datetime.now().isoformat()}",
        ]
        current_file_contents = (self.rendered_output.get('file_contents', {})
                                 if hasattr(self, 'rendered_output') and self.rendered_output
                                 else {})
        available_args = {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "validation_results": validation_results,
            "file_contents": current_file_contents
        }
        pre_formatted_check_passed = True
        pre_formatted_check_messages = []
        qa_report_text = "" 
        for section_config in self.QA_REPORT_SECTIONS: 
            method_name = section_config["method"]
            arg_names = section_config["args"]
            try:
                builder_method = getattr(self, method_name)
                call_args = []
                for name in arg_names:
                     if name == "file_contents":
                         call_args.append(available_args["file_contents"])
                     elif name in available_args:
                         call_args.append(available_args[name])
                     else:
                         raise KeyError(f"Missing required argument '{name}' for method '{method_name}'")
                section_lines = builder_method(*call_args)
                if method_name != "_build_qa_section_14_final_format": 
                    section_text_block = "\n".join(section_lines)
                    is_section_1 = "1. SIGNAL QUALITY" in section_text_block 
                    md_blocks = re.findall(r"```markdown(.*?)```", section_text_block, re.DOTALL)
                    contains_markdown_table = False
                    for block in md_blocks:
                        if not is_section_1 and any("|" in line and "---" in block for line in block.split('\n')):
                            contains_markdown_table = True
                            break
                    if contains_markdown_table:
                        pre_formatted_check_passed = False
                        msg = f"QA Section '{method_name}' appears to contain Markdown table syntax instead of expected pre-formatted text."
                        pre_formatted_check_messages.append(msg)
                        logging.warning(msg)
                report_lines.extend(section_lines)
            except (AttributeError, KeyError, Exception) as e: 
                error_message = f"Error building QA section '{method_name}': {e}"
                logging.getLogger(__name__).error(error_message, exc_info=True)
                report_lines.append(f"\n--- {error_message} ---\n")
        validation_results_out.append(ValidationResult(
            rule_id="QA_TABLE_FORMAT_INVALID",
            passed=pre_formatted_check_passed,
            severity=ValidationSeverity.HIGH,
            message="; ".join(pre_formatted_check_messages) if not pre_formatted_check_passed else "All QA tables appear to use pre-formatted text.",
            details={"failed_sections": pre_formatted_check_messages}
        ))
        if len(report_lines) > 2:
             qa_report_text = "\n".join(report_lines).strip()
        else:
             qa_report_text = "\n".join(report_lines).strip()
        validation_results_out.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"QA Report generated ({len(report_lines)} lines)"
        ))
        final_file_contents = available_args["file_contents"]
        final_file_contents['qa_report'] = qa_report_text
        return validation_results_out, qa_report_text, final_file_contents

    def _format_ascii_bar_chart(self, label: str, value: float, target_min: float, target_max: float, temperature: float = 0.0, bar_length: int = 10, is_summary: bool = False) -> str:
        value = min(max(value, 0.0), 1.0) 
        filled_length = int(round(bar_length * value))
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)
        score_pct = f"{value:.1%}"
        status = "PASS" if target_min <= value <= target_max else "FAIL"
        temp_str = f"(T: {temperature:.1f})" if not is_summary else f"(Avg T: {temperature:.1f})"
        target_str = f"(Tgt: {target_min:.0%}-{target_max:.0%})"
        label_width = 25
        bar_width = bar_length + 2 
        score_width = 7
        target_width = len(target_str) + 1
        status_width = 7
        temp_width = len(temp_str) + 1
        total_width = 80
        current_width = label_width + bar_width + score_width + target_width + status_width + temp_width
        padding = " " * max(0, total_width - current_width)
        label_formatted = f"{label:<{label_width}}"[:label_width] 
        return f"{label_formatted} [{bar}] {score_pct:<{score_width}} {target_str:<{target_width}} {status:<{status_width}} {temp_str:<{temp_width}}{padding}"

    def _format_plain_text_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        alignments: Optional[List[str]] = None,
        col_widths: Optional[List[int]] = None, 
        wrap_text: bool = False 
    ) -> List[str]:
        if not headers and not rows:
            return ["(No data available)"]
        num_cols = len(headers) if headers else (len(rows[0]) if rows else 0)
        if num_cols == 0:
            return ["(No data available)"]
        if col_widths and len(col_widths) == num_cols:
            widths = col_widths
        else:
            widths = [0] * num_cols
            if headers:
                for i, header in enumerate(headers):
                    max_header_line_width = max(len(line) for line in str(header).split('\n'))
                    widths[i] = max(widths[i], max_header_line_width)
            for row in rows:
                for i, cell in enumerate(row):
                    if i < num_cols: 
                        widths[i] = max(widths[i], len(str(cell)))
        aligns = alignments or ['L'] * num_cols
        if len(aligns) < num_cols:
            aligns.extend(['L'] * (num_cols - len(aligns)))
        formatters = []
        for i in range(num_cols):
            align_char = '<' if aligns[i] == 'L' else '>' if aligns[i] == 'R' else '^'
            formatters.append(f"{{:{align_char}{widths[i]}}}")
        lines = []
        if headers:
            header_lines_split = [str(h).split('\n') for h in headers]
            max_header_lines = max(len(h_lines) for h_lines in header_lines_split)
            for line_idx in range(max_header_lines):
                line_parts = []
                for col_idx in range(num_cols):
                    header_part = header_lines_split[col_idx][line_idx] if line_idx < len(header_lines_split[col_idx]) else ""
                    line_parts.append(formatters[col_idx].format(header_part))
                lines.append("  ".join(line_parts))
            lines.append("  ".join("-" * widths[i] for i in range(num_cols)))
        if wrap_text:
            wrapped_rows = []
            for row in rows:
                 row_lines = [[] for _ in range(num_cols)] 
                 max_lines = 1
                 for i, cell in enumerate(row):
                     if i < num_cols:
                         cell_str = str(cell)
                         wrapped = self._wrap_cell_text(cell_str, widths[i])
                         row_lines[i].extend(wrapped)
                         max_lines = max(max_lines, len(wrapped))
                 for line_idx in range(max_lines):
                     line_parts = []
                     for col_idx in range(num_cols):
                         cell_part = row_lines[col_idx][line_idx] if line_idx < len(row_lines[col_idx]) else ""
                         line_parts.append(formatters[col_idx].format(cell_part))
                     wrapped_rows.append("  ".join(line_parts))
            lines.extend(wrapped_rows)
        else:
             for row in rows:
                 lines.append("  ".join(formatters[i].format(str(row[i])[:widths[i]]) for i in range(num_cols) if i < len(row)))
        return lines

    def _wrap_cell_text(self, text: str, width: int) -> List[str]:
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append("")
                continue
            current_line = ""
            for word in paragraph.split():
                 if not current_line:
                     current_line = word
                 elif len(current_line) + 1 + len(word) <= width:
                     current_line += " " + word
                 else:
                     lines.append(current_line)
                     current_line = word
            lines.append(current_line) 
        return lines

    def _check_word_count(self, count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        if min_target <= count <= max_target:
            status = "PASS"
        else:
            status = "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str

    def _invoke_deduplication_analysis(self, staging_buffer: ImmutableStagingBuffer) -> bool:
        """
        Gathers data and calls DuplicateDetector methods for QA report sections.
        (Unchanged from v12.10)
        """
        self.dedup_analysis_timestamp = datetime.now().isoformat()
        if not self.dup_detector:
            self.logger.warning("DuplicateDetector not available (likely HOP-2 failure). Skipping deduplication analysis.")
            return False
        sections_for_matrix = {} 
        overview_bullet_pairs = {} 
        exec_summary_text = staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        exec_summary_comparison_data = {} 
        section_map = { 
            ResumeSection.K1_EXECUTIVE_SUMMARY: "Exec Summary",
            ResumeSection.K5_UNIFY_OVERVIEW: "Unify Overview",
            ResumeSection.K5_UNIFY_BULLETS: "Unify Bullets",
            ResumeSection.K6_IBM_OVERVIEW: "IBM Overview",
            ResumeSection.K6_IBM_BULLETS: "IBM Bullets",
            ResumeSection.K7_TRADERSENSE_OVERVIEW: "TraderSense Overview",
            ResumeSection.K7_TRADERSENSE_BULLETS: "TraderSense Bullets",
            ResumeSection.K8_EY_OVERVIEW: "EY Overview",
            ResumeSection.K8_EY_BULLETS: "EY Bullets",
            ResumeSection.K9_EARLY_CAREER_OVERVIEW: "Early Career Overview",
            ResumeSection.K9_EARLY_CAREER_BULLETS: "Early Career Bullets",
            ResumeSection.K10_COMPETENCIES: "Competencies",
            ResumeSection.K2_SKILLS: "Skills",
            ResumeSection.K13_COVER_LETTER: "Cover Letter",
        }
        for section_enum, label in section_map.items():
            content = staging_buffer.get(section_enum.value)
            if not content: continue
            if "Overview" in label:
                 sections_for_matrix[label] = [content] if isinstance(content, str) else []
                 overview_bullet_pairs[label] = {"overview": content, "bullets": []} 
                 exec_summary_comparison_data[label] = content 
            elif "Bullets" in label or label == "Competencies":
                 bullet_texts = []
                 if isinstance(content, list):
                     for item in content:
                          if isinstance(item, dict):
                              bullet_texts.append(item.get('text', item.get('bullet_text','')))
                          elif isinstance(item, str): 
                              bullet_texts.append(item)
                 sections_for_matrix[label] = [b for b in bullet_texts if b]
                 exec_summary_comparison_data[label] = [b for b in bullet_texts if b] 
                 base_label = label.replace(" Bullets", "").replace(" Competencies", "")
                 overview_key = f"{base_label} Overview"
                 if overview_key in overview_bullet_pairs:
                      overview_bullet_pairs[overview_key]["bullets"].extend(sections_for_matrix[label])
                 elif base_label == "Competencies": 
                      pass 
            elif label == "Skills":
                 if isinstance(content, list):
                     sections_for_matrix[label] = [item for item in content if isinstance(item, str)]
                     exec_summary_comparison_data[label] = [item for item in content if isinstance(item, str)]
            elif label == "Cover Letter":
                 if isinstance(content, str):
                     paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                     sections_for_matrix[label] = paragraphs
                     exec_summary_comparison_data[label] = paragraphs 
        try:
            self.similarity_matrix_data = self.dup_detector.compute_similarity_matrix(sections_for_matrix)
        except Exception as e:
            self.logger.error(f"Error computing similarity matrix: {e}", exc_info=True)
            self.similarity_matrix_data = None
        try:
            self.overview_similarity_data = []
            for label, data in overview_bullet_pairs.items():
                 if data["overview"] and data["bullets"]:
                     sim_result = self.dup_detector.compute_overview_bullet_similarity(
                         data["overview"], data["bullets"], section_id=label 
                     )
                     self.overview_similarity_data.append(sim_result)
        except Exception as e:
            self.logger.error(f"Error computing overview vs bullet similarity: {e}", exc_info=True)
            self.overview_similarity_data = None
        try:
            self.executive_summary_similarity_data = self.dup_detector.compute_executive_summary_similarity(
                exec_summary_text, exec_summary_comparison_data
            )
        except Exception as e:
             self.logger.error(f"Error computing executive summary similarity: {e}", exc_info=True)
             self.executive_summary_similarity_data = None
        return True 

    def _calculate_master_avg_bullet_length(self) -> Dict[str, float]:
        """
        Helper to calculate average bullet length for sections in master resume using MS Word style counting.
        (Unchanged from v12.10)
        """
        avg_lengths = {}
        experience_sections = self.master_resume.get("professional_experience", [])
        experience_sections_to_avg = {
            "Unify": ("Unify Consulting", "bullet_pool"),
            "IBM": ("IBM", "bullet_pool"),
            "EY": ("Ernst & Young", "highlights"),
            "TraderSense": ("TraderSense", "highlights"), 
            "EarlyCareer": ("Early Career Roles", "highlights"),
        }
        default_avg = 25.0 
        for key, (company_name_part, bullets_key) in experience_sections_to_avg.items():
            total_words = 0
            bullet_count = 0
            exp = next((e for e in experience_sections if company_name_part in e.get("company", "")), None)
            if exp:
                bullets = exp.get(bullets_key, [])
                str_bullets = [b for b in bullets if isinstance(b, str)]
                if str_bullets:
                    total_words = sum(count_words_ms_word_style(b) for b in str_bullets)
                    bullet_count = len(str_bullets)
            avg_lengths[key] = (total_words / bullet_count) if bullet_count > 0 else default_avg
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        competencies_strings = [c for c in competencies_list if isinstance(c, str)]
        avg_lengths["Competencies"] = (sum(count_words_ms_word_style(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0 
        avg_lengths["Default"] = default_avg
        return avg_lengths

# ============================================================================
# HELPER DEFINITIONS FOR TEST COMPATIBILITY
# ============================================================================

class HopStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING" # Optional

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

class GateDecision(Enum):
    PROCEED = "PROCEED"
    ERROR_REPORT_ONLY = "ERROR_REPORT_ONLY"
    HALT = "HALT"

class HopExecutionError(Exception): pass
class StagingBufferError(Exception): pass

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    import copy
    from dataclasses import asdict

    # --- Configuration for the run ---
    # You can change these values to generate a resume for a different job
    my_company_name = "DataDog"
    my_job_title = "Director, Technology Alliances"
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
Datadog values people from all walks of life. We understand not everyone will meet all the above qualifications on day one. That's okay. If you’re passionate about technology and want to grow your skills, we encourage you to apply.

    """

    print("--- Starting Resume Generation Workflow ---")

    # Initialize the orchestrator with a deep copy of the master resume
    # This prevents the original MASTER_RESUME_JSON from being modified during the run
    orchestrator = WorkflowOrchestrator(copy.deepcopy(MASTER_RESUME_JSON))

    # Execute the workflow
    result = orchestrator.execute_workflow(
        job_description=my_job_description,
        company_name=my_company_name,
        job_title=my_job_title
    )

    print("\n--- Workflow Final Result ---")
    # Print a summary of the result
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'SUCCESS':
        print(f"Gate Decision: {result.get('gate_decision')}")
        print(f"File Paths: {result.get('file_paths')}")
    else:
        print(f"Reason: {result.get('reason', result.get('error', 'No reason provided.'))}")

    # Optionally, save the generated files to a directory
    if result.get('status') == 'SUCCESS':
        output_dir = "generated_resumes"
        os.makedirs(output_dir, exist_ok=True)
        for file_type, content in result.get('file_contents', {}).items():
            file_name = result['file_paths'].get(file_type)
            if file_name and content:
                with open(os.path.join(output_dir, file_name), 'w', encoding='utf-8') as f:
                    f.write(content)
        print(f"\nGenerated files saved to the '{output_dir}' directory.")

    print("\n--- Workflow Finished ---")
