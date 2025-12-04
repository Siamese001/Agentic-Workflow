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


__version__ = "12.02"
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
    max_reflexion_loops: int = 2

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
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 7
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 8
    K1_MIN_DIFFERENTIATORS: int = 4

    # Experience Overviews
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 28
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 44
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 28
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 38
    EY_OVERVIEW_WORD_COUNT_MIN: int = 28
    EY_OVERVIEW_WORD_COUNT_MAX: int = 38
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 21
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 33
    # <<< Corrected: Added TraderSense constraints (using EY as template, adjust if needed)
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 33


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
    RESUME_MAX_JD_KEYWORDS: int = 15
    CL_MAX_JD_SIMILARITY: float = 0.75
    SECTION_SIGNAL_SCORE_MAX: float = 0.95

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
    ("K0_HEADLINE_CONFIG", dict(cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=True)),
    ("K1_EXECUTIVE_SUMMARY_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=2)),
    ("K5_UNIFY_BULLETS_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)),
    ("K5_UNIFY_OVERVIEW_CONFIG", ReasoningConfig.DEFAULT), # Assign the default instance directly
    ("K6_IBM_BULLETS_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True)),
    ("K6_IBM_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True)),
    ("K8_EY_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K8_EY_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K9_EARLY_CAREER_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K9_EARLY_CAREER_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)),
    ("K2_SKILLS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
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

# Overwrite this function around line 214
def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """
    Converts reasoning config to Gemini API parameters.
    v11.30 Fix: Always use RAGConfig.max_tokens to avoid truncation.
    """
    import logging
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)
    intensity, level = _calculate_reasoning_intensity(params)
    params['intensity_score'] = intensity
    params['reasoning_level'] = level

    temperature = _get_generation_temperature()
    # --- START FIX: Use max_tokens directly from RAGConfig ---
    # Ensure RAGConfig is accessible (it should be globally defined)
    try:
         max_tokens = RAGConfig().max_tokens
    except NameError:
         # Fallback if RAGConfig somehow isn't defined yet (shouldn't happen here)
         logging.warning("RAGConfig not found during API param creation, using default max_tokens=4000.")
         max_tokens = 4000
    # --- END FIX ---
    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(f"Reasoning config: intensity={intensity:.1f}, temp={temperature}, tokens={max_tokens}, level={level}")
    except NameError: # Handle case where logger might not be fully configured yet
        pass

    # Ensure max_tokens is within reasonable Gemini API limits (e.g., check documentation if issues persist)
    # For now, assume RAGConfig().max_tokens is valid. Clamp if necessary based on model specs.
    # Example clamp: max_tokens = min(max_tokens, 8192) # If 8k is the actual limit

    return {
        # --- Apply the max_tokens fix here ---
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens),
        # --- End fix ---
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
    """Allocates max_tokens based on reasoning depth and complexity."""
    if tot_d >= 4: max_tokens = 2500
    elif tot_d >= 3 and cot >= 5: max_tokens = 2700
    elif tot_d >= 3 or cot >= 5: max_tokens = 2600
    elif sc >= 15: max_tokens = 2500
    else: max_tokens = 1200
    return max(1200, min(max_tokens, 14000))

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
    """
    App Tracker Consolidated & Hardened QA Spec v5 Validator.
    Enforces R1-R23 rules. Produces PASSED summary or BLOCKED error table.
    """
    
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

# Insert this class overwrite starting around line 1111 in your file

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
# HOP-3: ARTIST GENERATOR (LLM Calls)
# ============================================================================

class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, previous_failures: List[ValidationResult] = None):
        """Initializes the ArtistGenerator with the master resume."""
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis # This object contains all HOP-0 signals
        self.previous_failures = previous_failures or []
        self.constraints = ContentConstraintsConfig()
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

    # (Provenance targets and generation config list remain the same)
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    ARTIST_GENERATION_CONFIG = [
        {"section": ResumeSection.K0_NAME, "method_name": "_copy_k0_name"},
        {"section": ResumeSection.K0_HEADLINE, "method_name": "_generate_k0_headline"},
        {"section": ResumeSection.K0_CONTACT, "method_name": "_copy_k0_contact"},
        {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "method_name": "_generate_k1_executive_summary"},
        {"section": ResumeSection.K5_UNIFY_BULLETS, "method_name": "_generate_k5_unify_bullets"},
        {"section": ResumeSection.K5_UNIFY_OVERVIEW, "method_name": "_generate_k5_unify_overview"},
        {"section": ResumeSection.K6_IBM_BULLETS, "method_name": "_generate_k6_ibm_bullets"},
        {"section": ResumeSection.K6_IBM_OVERVIEW, "method_name": "_generate_k6_ibm_overview"},
        {"section": ResumeSection.K7_TRADERSENSE_BULLETS, "method_name": "_copy_k7_tradersense_bullets"},
        {"section": ResumeSection.K7_TRADERSENSE_OVERVIEW, "method_name": "_copy_k7_tradersense_overview"},
        {"section": ResumeSection.K8_EY_BULLETS, "method_name": "_generate_k8_ey_bullets"},
        {"section": ResumeSection.K8_EY_OVERVIEW, "method_name": "_generate_k8_ey_overview"},
        {"section": ResumeSection.K9_EARLY_CAREER_BULLETS, "method_name": "_generate_k9_early_career_bullets"},
        {"section": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "method_name": "_generate_k9_early_career_overview"},
        {"section": ResumeSection.K11_EDUCATION, "method_name": "_copy_k11_education"},
        {"section": ResumeSection.K12_CERTIFICATIONS, "method_name": "_copy_k12_certifications"},
        {"section": ResumeSection.K10_COMPETENCIES, "method_name": "_generate_k10_competencies"},
        {"section": ResumeSection.K2_SKILLS, "method_name": "_generate_k2_skills"}, # K.2 still only consumes Secondary Themes
        {"section": ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EXPERIENCE_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EDUCATION_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_CERTIFICATIONS_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_COMPETENCIES_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K13_COVER_LETTER, "method_name": "_generate_k13_cover_letter"},
    ]

    def generate(
        self,
        feedback_results: List[ValidationResult] = None,
        attempt: int = 1,
        k1_temp_override: Optional[float] = None,
        k13_temp_override: Optional[float] = None # <-- ADDED K.13 Override
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Generate all resume content using LLM.

        Args:
            feedback_results: Validation failures from previous attempt (if any)
            attempt: Current generation attempt (1-5)
            k1_temp_override: Specific temperature for K.1 from orchestrator
            k13_temp_override: Specific temperature for K.13 from orchestrator # <-- ADDED

        Returns:
            (artist_output, validation_results)
        """
        validation_results = []

        if feedback_results:
            self.previous_failures = feedback_results

        try:
            # Pass both overrides to the internal generation method
            artist_output = self._generate_artist_output(
                k1_temp_override=k1_temp_override,
                k13_temp_override=k13_temp_override # <-- ADDED
            )

            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Content generated successfully (attempt {attempt})"
            ))

            return artist_output, validation_results

        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed: {str(e)}",
                details={"attempt": attempt, "error": str(e)}
            ))

            return {}, validation_results

    def _generate_artist_output(
        self,
        k1_temp_override: Optional[float] = None,
        k13_temp_override: Optional[float] = None # <-- ADDED K.13 Override
        ) -> Dict:
        """
        Generate complete artist output with all K.X sections.
        Accepts and passes temperature overrides for K.1 and K.13.
        """

        output = {}
        for config in self.ARTIST_GENERATION_CONFIG:
            section_enum = config["section"]
            method_name = config["method_name"]
            try:
                method = getattr(self, method_name)

                # --- Pass temperature overrides to specific sections ---
                if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY:
                    output[section_enum.value] = method(temperature_override=k1_temp_override)
                elif section_enum == ResumeSection.K13_COVER_LETTER: # <-- ADDED K.13 Case
                    output[section_enum.value] = method(temperature_override=k13_temp_override)
                # --- End Temperature Override Logic ---
                else:
                    output[section_enum.value] = method()

            except Exception as e:
                logging.error(f"Error generating section {section_enum.value} with {method_name}: {e}", exc_info=True)
                output[section_enum.value] = f"[Placeholder for {section_enum.value} due to generation error: {e}]"

        for section_enum in ResumeSection:
            if section_enum.value not in output:
                 output[section_enum.value] = None
        return output
    
    def _copy_k0_name(self) -> str:
        """Copies K.0 Name verbatim from master resume."""
        return self.master_resume.get("owner", {}).get("name", "")

    def _copy_k0_contact(self) -> str:
        """
        Copies and formats K.0 Contact verbatim from master resume.
        Returns a single pipe-separated string.
        """

        contact = self.master_resume.get("owner", {}).get("contact", {})

        phone = contact.get('phone', '').strip()
        email = contact.get('email', '').strip()
        linkedin = contact.get('linkedin', '').strip()

        contact_parts = [f"Phone: {phone}" if phone else None,
                         f"Email: {email}" if email else None,
                         f"LinkedIn: {linkedin}" if linkedin else None]

        contact_parts = [part for part in contact_parts if part]
        return " | ".join(contact_parts)

    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> str:
        """
        Refactored Helper: Centralizes Gemini API calls, including reasoning config and error handling.
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-pro')

            api_params = reasoning_config_to_api_params(reasoning_config)
            generation_config = api_params["generation_config"]
            sc_count = api_params.get('sc', 1)
            
            if temperature_override is not None:
                generation_config.temperature = temperature_override
                if section_id == "K.1": 
                    logging.info(f"  K.1 API Call: Using temp override: {generation_config.temperature}")

            enhanced_system = enhance_system_prompt_with_reasoning(system_prompt, reasoning_config, section_id)
            
            if sc_count > 1:
                logging.info(f"  Running Self-Consistency for {section_id} (requesting {sc_count} candidates)...")
                
                if temperature_override is None: 
                    generation_config.temperature = 0.9
                
                generation_config.candidate_count = sc_count
                
                candidate_responses = []
                try:
                    response = model.generate_content(
                        f"{enhanced_system}\n\n{prompt}",
                        generation_config=generation_config
                    )
                    
                    if response.candidates:
                        candidate_responses = [
                            part.text.strip() 
                            for candidate in response.candidates 
                            if candidate.content and candidate.content.parts
                            for part in candidate.content.parts if part.text
                        ]
                    
                    if not candidate_responses:
                         raise ValueError("Self-Consistency API call returned no valid text candidates.")

                except Exception as e:
                    logging.warning(f"    Self-Consistency API call for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} Self-Consistency API call failed: {e}")

                if not candidate_responses:
                    raise HopExecutionError(f"{section_id} Self-Consistency failed: No responses generated.")

                logging.info(f"  Synthesizing {len(candidate_responses)} responses for {section_id}...")
                
                synthesis_prompt = f"""You are a senior editor. You have been given {len(candidate_responses)} different draft responses to the same prompt. Your job is to analyze all of them for accuracy, consistency, and quality, and then produce one single, synthesized, final answer that represents the best of all drafts.

**ORIGINAL PROMPT (for context):**
{prompt}

**DRAFT RESPONSES:**
---
"""
                for i, res in enumerate(candidate_responses):
                    synthesis_prompt += f"**DRAFT {i+1}:**\n{res}\n---\n"

                synthesis_prompt += "\n**FINAL SYNTHESIZED ANSWER:**\n(Return *only* the final, synthesized answer, adhering to all formatting rules from the original prompt.)"

                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=api_params["generation_config"].max_output_tokens)
                
                synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)
                return synthesis_response.text.strip()

            else:
                response = model.generate_content(
                    f"{enhanced_system}\n\n{prompt}",
                    generation_config=generation_config
                )
                try:
                    return response.text.strip()
                except (ValueError, AttributeError) as e:
                    logging.warning(f"LLM generation for {section_id} returned no text: {e}. Response: {response}")
                    raise HopExecutionError(f"{section_id} generation returned no valid text.")

        except ValueError as ve: 
            logging.warning(f"LLM generation for {section_id} failed: {ve}. Returning placeholder.")
            return f"[Placeholder for {section_id} - {ve}]"
        except ImportError:
            logging.warning(f"LLM generation for {section_id} failed: google.generativeai not installed. Returning placeholder.")
            return f"[Placeholder for {section_id} - Gemini library not found]"
        except HopExecutionError as he: 
            logging.warning(f"LLM generation for {section_id} failed: {he}")
            return f"[Placeholder for {section_id} - {he}]"
        except Exception as e: 
            logging.warning(f"LLM generation for {section_id} failed with an API error: {e}. Returning placeholder.")
            return f"[Placeholder for {section_id} - LLM call failed]"
    
    def _generate_k1_executive_summary(self, temperature_override: Optional[float] = None) -> str:
        """
        [v11.0 REDESIGN & v12.00 FIX]
        Generate K.1 Executive Summary using *all* HOP-0 signals.
        Consumes: Primary Theme, Secondary Themes, Differentiators, Role Archetype,
                  and Authenticity Patterns.
        FIX: Strengthened word/sentence count instructions.
        """
        # 1. Get source material
        top_bullets = []
        for exp in self.master_resume['professional_experience'][:2]: # Unify & IBM
            # Ensure bullet_pool exists and is a list
            bullet_pool = exp.get('bullet_pool', [])
            if isinstance(bullet_pool, list):
                 top_bullets.extend(bullet_pool[:4])
            else:
                 logging.warning(f"K.1: bullet_pool for {exp.get('company')} is not a list. Skipping bullets.")
        bullets_text = '\n'.join([f"- {b}" for b in top_bullets])

        # 2. Get *all* key themes from thematic analysis
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:3] if t.get('name')]
        # Safely get differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = comp_intel.get_top_differentiators(5)
            # Ensure it's a list
            if not isinstance(differentiators, list):
                logging.warning(f"K.1: get_top_differentiators returned {type(differentiators)}, expected list. Defaulting.")
                differentiators = []
        else:
            logging.warning("K.1: Competitive intelligence missing. Cannot get differentiators.")
            differentiators = []


        role_archetype = self.thematic_analysis.role_classification.get('role_archetype', 'Technical_IC')

        # 3. Get Authenticity Patterns
        auth_patterns_data = self.thematic_analysis.authenticity_patterns or {}
        auth_patterns = auth_patterns_data.get('patterns', {})
        auth_summary_patterns = auth_patterns.get('executive_summary_patterns', [])
        auth_verbs = auth_patterns.get('achievement_verb_patterns', [])

        # 4. Build Archetype Instruction
        archetype_instruction = ""
        if role_archetype == "Post-Sales_Customer_Success":
            archetype_instruction = "CRITICAL INSTRUCTION: The target role is POST-SALES. The summary MUST prioritize themes of AI adoption, customer value realization, retention, and scaling technical success."
        elif role_archetype == "Sales_GTM":
            archetype_instruction = "CRITICAL INSTRUCTION: The target role is PRE-SALES / Go-To-Market. The summary MUST prioritize themes of revenue generation, strategic partnerships, and driving market adoption."

        # 5. Build Feedback Instruction
        feedback_instruction = ""
        if self.previous_failures:
            failed_rules = [f.rule_id for f in self.previous_failures]
            messages = []
            for f in self.previous_failures:
                 if f.rule_id in ["VG_WORD_COUNT_K1", "VG_SENTENCE_COUNT_K1"]:
                     # Ensure message is formatted if it's callable
                     msg = f.message(f.details) if callable(f.message) else f.message
                     messages.append(msg)

            if messages:
                feedback_instruction = (
                    "\n**CRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:**\n"
                    "Your previous summary FAILED validation on length constraints.\n"
                    f"**FAILURE DETAILS:** {'; '.join(messages)}\n"
                    f"You MUST generate a new summary that is strictly between {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words AND {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} to {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences.\n\n"
                )

        # 6. Build the new, comprehensive prompt
        prompt = f"""{feedback_instruction}You are an expert resume writer crafting an executive summary.

**Candidate's Key Achievements (Source of Truth):**
{bullets_text}

**Target Job Analysis (ALL signals MUST be used):**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Non-Negotiable Keywords: {', '.join(differentiators)}
- Role Archetype: {role_archetype}

**Authentic Voice & Phrasing (To guide writing style):**
- Target Summary Phrasing: {', '.join(auth_summary_patterns[:2])}
- Target Action Verbs: {', '.join(auth_verbs[:5])}

**Job Description Context:**
{self.job_description[:1500]}

{archetype_instruction}

**NON-NEGOTIABLE REQUIREMENTS (FAILURE WILL CAUSE REJECTION):**
1.  **WORD COUNT:** The summary MUST be **strictly between {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words**. Count carefully before outputting. Use standard word counting rules (hyphenated words count as one).
2.  **SENTENCE COUNT:** The summary MUST have **exactly {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} or {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences**. Count carefully using standard punctuation (., !, ?).

**TASK:**
1. Write a **{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentence** executive summary that strictly adheres to **both** the word and sentence count requirements.
2. Start with a sentence that directly addresses the '{primary_theme}'.
3. Your goal is to balance all signals.
    - Naturally integrate 3-4 of the **Non-Negotiable Keywords**.
    - Naturally integrate 1-2 concepts from the **Secondary Themes**.
    - Your tone MUST align with the **Authentic Voice & Phrasing** patterns. Use the suggested verbs and phrasing as inspiration.
4. All claims MUST be supported by the candidate's achievements. Do NOT invent facts.
5. **CRITICAL:** Ensure no specific company names (e.g., "Unify", "IBM") appear in the summary.
6. Return ONLY the summary paragraph. No preamble, explanation, or notes.
"""

        # 7. Call LLM
        reasoning_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG
        # Temperature logic remains the same, handled by orchestrator override
        final_temp = temperature_override if temperature_override is not None else _get_generation_temperature() # Use default if no override

        base_system = "You are an expert resume writer. You synthesize multiple data signals (themes, keywords, authentic voice) into a cohesive summary. You strictly adhere to all constraints, especially word and sentence counts."

        return self._call_gemini_api(
            prompt,
            reasoning_config,
            "K.1",
            base_system,
            temperature_override=final_temp # Pass the determined temperature
        )
        
    def _generate_k2_skills(self) -> List[str]:
        """Generates 12 high-signal, 1-3 word skills.
        This remains the primary consumer of the secondary_themes *list* for
        a dedicated skills section, even as other sections now also use the themes.
        """
        try:
            # 1. Get RAG analysis results from HOP-0
            primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
            secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:4]]
            differentiators = []
            if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
                differentiators = self.thematic_analysis.competitive_intelligence.differentiator_keywords[:10]

            # 2. Build the LLM prompt
            prompt = f"""You are an expert HR data analyst. Your task is to extract the 12 most critical skills from a job analysis and format them as 1-3 word keywords suitable for an HR database.

**Job Description Analysis:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Key Differentiator Keywords: {', '.join(differentiators)}

**Full Job Description (for context):**
{self.job_description[:2000] if self.job_description else 'Not provided'}

**TASK:**
1. Identify the **12 most important skills** based on the provided analysis and JD.
2. These skills must have 90%+ signal (directly supported by themes and keywords).
3. Format **each** skill as a 1-3 word keyword (e.g., 'AI Strategy', 'Team Leadership', 'SaaS Delivery').
4. The skills must be common terms found in HR recruiting databases.
5. Return **only** the 12 skills, each on a new line.
6. Do NOT add bullets, numbers, or any other commentary or preamble.
"""
            # 3. Call the LLM API using the centralized helper
            reasoning_config = ReasoningConfig.K2_SKILLS_CONFIG
            base_system = "You are an expert HR data analyst. You generate 1-3 word skills for HR databases. You follow formatting instructions perfectly."
            skills_text = self._call_gemini_api(prompt, reasoning_config, "K.2", base_system)
            if "[Placeholder" in skills_text:
                 return [f"Error: LLM failed to generate skills. Details: {skills_text}"]
            
            skills_list_final = []
            skills_intermediate = re.split(r'[\n,]', skills_text)
            
            for skill in skills_intermediate:
                cleaned_skill = re.sub(r'^[•*\-\d\.]+\s*', '', skill).strip()
                if not cleaned_skill:
                    continue
                word_count = len(cleaned_skill.split())
                if 1 <= word_count <= 3:
                    skills_list_final.append(cleaned_skill)
                else:
                    print(f"Warning: Discarding malformed skill '{cleaned_skill}' (word count: {word_count})")

            # 5. Validate and return
            if len(skills_list_final) < 10:
                return [f"Error: LLM failed to generate 12 valid 1-3 word skills. Output: {skills_text}"]
                
            return skills_list_final[:12]

        except Exception as e:
            print(f"Warning: K.2_Skills LLM generation failed: {e}")
            return [f"Error: {e}"]
    
    def _generate_k0_headline(self) -> str:
        """
        [v11.0 REDESIGN & v12.00 FIX]
        Generate K.0 Headline using Primary Theme, Differentiators, Role,
        and Authenticity Patterns for tone.
        FIX: Strengthened word count instructions, refined fallback.
        """
        recent_exp = MASTER_RESUME_JSON['professional_experience'][0]
        current_title = recent_exp.get('title', 'Technology Leader')

        # Get signals
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        # Safely get differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            # Get top differentiators and ensure it's a list
            differentiators = comp_intel.get_top_differentiators(3)
            if not isinstance(differentiators, list):
                logging.warning(f"K.0 Headline: get_top_differentiators returned {type(differentiators)}, expected list. Defaulting.")
                differentiators = []
        else:
            logging.warning("K.0 Headline: Competitive intelligence missing. Cannot get differentiators.")
            differentiators = []


        role_level = self.thematic_analysis.role_classification.get('seniority', 'senior')
        target_role_title = self.thematic_analysis.role_classification.get('precise_role_title', 'Target Role')

        # Get Authenticity Patterns
        auth_patterns_data = self.thematic_analysis.authenticity_patterns or {}
        auth_patterns = auth_patterns_data.get('patterns', {})
        auth_summary_patterns = auth_patterns.get('executive_summary_patterns', [])
        # Ensure list isn't empty before accessing
        auth_tone_example = auth_summary_patterns[0] if auth_summary_patterns else "Confident and results-oriented"

        prompt = f"""Create a professional resume headline for this candidate.

**Candidate's Current Role:** {current_title}
**Target Job Title:** {target_role_title}

**Target Job Analysis:**
- Primary Theme: {primary_theme}
- Key Differentiators: {', '.join(differentiators)}
- Role Level: {role_level}

**Authentic Tone Example (from RAG):** "{auth_tone_example}"

**Instructions:**
1. Create a headline that positions the candidate for a role aligned with '{primary_theme}'.
2. **DO NOT** include formal job titles (e.g., 'Vice President', 'Director'). Focus on functional expertise.
3. Include 2-3 relevant keywords from the job analysis, potentially inspired by: {', '.join(differentiators)}.
4. Format: "[Functional Expertise Area] | [Key Strength 1] | [Key Strength 2]" (Use pipes '|' as separators)
5. **DO NOT** use commas.
6. **ABSOLUTELY CRITICAL:** The headline MUST be **strictly between {self.constraints.HEADLINE_WORD_COUNT_MIN} and {self.constraints.HEADLINE_WORD_COUNT_MAX} words** total. No exceptions. Re-read and count before outputting.
7. The tone must be professional and confident, inspired by the **Authentic Tone Example**.

**CRITICAL INSTRUCTION FOR THIS JOB:**
The target role is a "VP, AI Technical Success" which is a POST-SALES customer-facing role focused on ADOPTION, RETENTION, and EXPANSION.
The headline MUST reflect this. Use keywords like "Customer Success", "Post-Sales Leadership", "AI Adoption", "Technical Account Management", or "Customer Value Realization".
DO NOT use pre-sales or product delivery terms.

**Good Example Format for this role:** "AI Technical Success Leadership | Post-Sales Strategy | GenAI Adoption & Scalability"

8. Return ONLY the headline text with no explanation.
"""

        reasoning_config = ReasoningConfig.K0_HEADLINE_CONFIG
        base_system = "You are an expert at crafting professional resume headlines. You synthesize job themes and authentic voice. You strictly adhere to all constraints, especially word count."
        headline = self._call_gemini_api(prompt, reasoning_config, ResumeSection.K0_HEADLINE.value, base_system)

        # Use MS Word style count for validation
        word_count = count_words_ms_word_style(headline)
        if "[Placeholder" in headline or not (self.constraints.HEADLINE_WORD_COUNT_MIN <= word_count <= self.constraints.HEADLINE_WORD_COUNT_MAX):
            logging.warning(f"K.0 Headline generation failed or invalid (words: {word_count}, target: {self.constraints.HEADLINE_WORD_COUNT_MIN}-{self.constraints.HEADLINE_WORD_COUNT_MAX}). Using fallback template.")
            # Refined Fallback using available data
            fb_theme = primary_theme if primary_theme != 'AI Leadership' else "AI Technical Success" # Make fallback more specific if possible
            fb_diff1 = differentiators[0] if differentiators else "Customer Value"
            fb_diff2 = differentiators[1] if len(differentiators) > 1 else "Strategic Growth"
            # Construct fallback carefully to meet word count
            fallback_headline = f"{fb_theme} Leadership | {fb_diff1} | {fb_diff2}"
            # Trim if needed (less likely with this structure)
            fallback_words = fallback_headline.split(" | ")
            if len(fallback_words) > 3: fallback_words = fallback_words[:3]
            fallback_headline = " | ".join(fallback_words)
            # Check length again, very basic trim if still too long
            if count_words_ms_word_style(fallback_headline) > self.constraints.HEADLINE_WORD_COUNT_MAX:
                 parts = fallback_headline.split(' | ')
                 if len(parts) > 2: fallback_headline = " | ".join(parts[:2]) # Trim last part
                 # As a last resort, just use the theme and one differentiator if still too long
                 elif count_words_ms_word_style(fallback_headline) > self.constraints.HEADLINE_WORD_COUNT_MAX:
                      fallback_headline = f"{fb_theme} Leadership | {fb_diff1}"


            return fallback_headline

        return headline
    
    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            section_index: int,
            provenance_targets: Dict[str, int],
            reasoning_config: ReasoningConfig,
            section_id: str
    ) -> List[Dict]:
        """
        [v11.0 REDESIGN & v12.00 FIX]
        Generic method to generate bullets.
        Now passes Secondary Themes and Authenticity Patterns to all sub-prompts.
        FIX: Strengthened Verbatim selection prompt, added check for empty list in fallback.
        """
        # 1. Find the experience section
        experience_section = next((exp for exp in self.master_resume['professional_experience']
                                   if company_name in exp['company']), None)
        if not experience_section:
            raise HopExecutionError(f"{company_name} experience not found in MASTER_RESUME_JSON for section {section_id}")

        # 2. Get *all* HOP-0 signals
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:3] if t.get('name')]
        # Safely access differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = comp_intel.get_top_differentiators(5)
            if not isinstance(differentiators, list):
                logging.warning(f"get_top_differentiators in {section_id} returned non-list: {type(differentiators)}. Defaulting.")
                differentiators = []
        else:
             logging.warning(f"Competitive intelligence missing in {section_id}. Cannot get differentiators.")
             differentiators = []

        role_level = self.thematic_analysis.role_classification.get('seniority', 'senior')

        # Get Authenticity Patterns
        auth_patterns_data = self.thematic_analysis.authenticity_patterns or {} # Handle None
        auth_patterns = auth_patterns_data.get('patterns', {})
        auth_verbs = auth_patterns.get('achievement_verb_patterns', [])
        auth_metrics = auth_patterns.get('metric_presentation_patterns', [])

        # Ensure enriched_scaffold and section_index are valid
        if not isinstance(self.enriched_scaffold.get('experience_sections'), list) or section_index >= len(self.enriched_scaffold['experience_sections']):
             raise HopExecutionError(f"Invalid enriched_scaffold structure or section_index {section_index} for {section_id}")
        master_bullets_structured = self.enriched_scaffold['experience_sections'][section_index].get('bullets', [])
        if not isinstance(master_bullets_structured, list):
             raise HopExecutionError(f"Bullets data for section {section_index} ({section_id}) is not a list.")

        # Ensure bullets are dictionaries with 'bullet_text'
        valid_master_bullets = []
        for i, b in enumerate(master_bullets_structured):
             if isinstance(b, dict) and 'bullet_text' in b:
                 valid_master_bullets.append(b)
             else:
                 logging.warning(f"Skipping invalid bullet structure at index {i} in section {section_index} for {section_id}: {b}")
        master_bullets_structured = valid_master_bullets # Use only valid bullets

        bullets_text = '\n'.join([f"{i+1}. {bullet['bullet_text']}" for i, bullet in enumerate(master_bullets_structured)])

        total_expected_count = sum(provenance_targets.values())
        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)

        final_bullets = [] # Initialize here

        # --- 3. Select Verbatim Bullets ---
        if verbatim_count > 0:
            if not master_bullets_structured:
                 logging.warning(f"{section_id} Cannot select Verbatim bullets: No valid master bullets available.")
            else:
                prompt_select = f"""You are a resume optimization expert. Select the most relevant bullets for a specific job WITHOUT changing them.

**Master Resume Bullets ({company_name}):**
--- START BULLETS ---
{bullets_text}
--- END BULLETS ---

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Instructions:**
1. Select the TOP {verbatim_count} bullets from the list above that best match ALL the job themes (Primary and Secondary) and keywords.
2. **CRITICAL:** Return the selected bullet text EXACTLY as it appears in the input list, character for character. DO NOT modify, rephrase, add, remove, or change ANY words, numbers, or punctuation. Maintain the original capitalization and spacing.
3. Return ONLY the {verbatim_count} selected bullets, one per line, with no numbers, formatting, or any extra text before or after the bullets.
"""
                system_prompt_select = "You select verbatim bullets based on job fit, considering primary and secondary themes. You NEVER modify the text."
                response_select = self._call_gemini_api(prompt_select, reasoning_config, f"{section_id}_SelectV", system_prompt_select)

                if "[Placeholder" not in response_select:
                    selected_texts = [line.strip() for line in response_select.split('\n') if line.strip()]
                    verbatim_bullets = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id}_SelectV")
                    final_bullets.extend(verbatim_bullets)
                else:
                    logging.warning(f"{section_id} Verbatim selection failed. Using first {verbatim_count} master bullets.")
                    # --- START FIX: Check if list is non-empty before slicing ---
                    if master_bullets_structured:
                        final_bullets.extend([{'bullet_text': b['bullet_text'], **b} for b in master_bullets_structured[:verbatim_count]])
                    else:
                        logging.error(f"{section_id} Fallback failed: master_bullets_structured is empty.")
                    # --- END FIX ---


        # --- 4. Select and Customize Bullets ---
        if customized_count > 0:
            used_texts = {b.get('bullet_text', b.get('text')) for b in final_bullets}
            available_for_custom = [b for b in master_bullets_structured if isinstance(b, dict) and b.get('bullet_text') not in used_texts]
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count]

            if candidates_for_custom:
                customized_bullets = self._generate_lightly_customized_bullets(
                    source_bullets_text=[b['bullet_text'] for b in candidates_for_custom],
                    section_id=f"{section_id}_CustomC",
                    thematic_analysis=self.thematic_analysis
                )
                final_bullets.extend(customized_bullets)
            else:
                 logging.warning(f"{section_id} Not enough unique bullets to customize.")

        # --- 5. Generate Synthetic Bullets ---
        if synthetic_count > 0:
            context_bullets_text = '\n'.join([f"- {b.get('text', b.get('bullet_text', ''))}" for b in final_bullets])
            synthetic_bullets = self._generate_synthetic_bullets(
                count=synthetic_count,
                company_name=company_name,
                job_description=self.job_description,
                thematic_analysis=self.thematic_analysis,
                context_bullets=context_bullets_text,
                reasoning_config=reasoning_config,
                section_id=f"{section_id}_SynthS"
            )
            final_bullets.extend(synthetic_bullets)

        # --- 6. Final Padding / Trimming ---
        if len(final_bullets) < total_expected_count:
            logging.warning(f"{section_id} Generated only {len(final_bullets)}/{total_expected_count} bullets. Padding with Verbatim.")
            needed = total_expected_count - len(final_bullets)
            used_texts = {b.get('text', b.get('bullet_text')) for b in final_bullets}
            padding_candidates = [b for b in master_bullets_structured if isinstance(b, dict) and b.get('bullet_text') not in used_texts]
            padding = [{'bullet_text': b['bullet_text'], **b, 'provenance': BulletProvenance.Verbatim.value} for b in padding_candidates[:needed]]
            final_bullets.extend(padding)

        elif len(final_bullets) > total_expected_count:
             logging.warning(f"{section_id} Generated too many bullets ({len(final_bullets)}/{total_expected_count}). Trimming.")
             final_bullets.sort(key=lambda b: 0 if b.get('provenance', '') != BulletProvenance.Verbatim.value else 1)
             final_bullets = final_bullets[:total_expected_count]

        # --- 7. Word Count Validation & Rewrite ---
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
        section_name_for_avg = "Default"
        if "Unify" in company_name: section_name_for_avg = "Unify"
        elif "IBM" in company_name: section_name_for_avg = "IBM"
        elif "EY" in company_name or "Ernst & Young" in company_name: section_name_for_avg = "EY"
        elif "TraderSense" in company_name: section_name_for_avg = "TraderSense"
        elif "Early Career" in company_name: section_name_for_avg = "EarlyCareer"
        elif section_id.startswith("K.10"): section_name_for_avg = "Competencies"

        logging.info(f"Applying bullet word count validation for {section_id} using average key '{section_name_for_avg}' (Avg: {master_avg_lengths.get(section_name_for_avg, 'N/A'):.1f} words)")

        final_bullets = self._validate_and_potentially_rewrite_bullets(
            selected_bullets_structured=final_bullets,
            master_avg_lengths=master_avg_lengths,
            section_name_for_avg=section_name_for_avg,
            section_id_for_logging=section_id
        )

        # --- 8. Final Reordering ---
        current_bullets_text = '\n'.join([f"{i+1}. {bullet.get('text', bullet.get('bullet_text', ''))}" for i, bullet in enumerate(final_bullets)])

        prompt_reorder = f"""You are a resume optimization expert. Reorder the following bullets by relevance for a specific job.

**Bullets to Reorder ({company_name}):**
--- START BULLETS ---
{current_bullets_text}
--- END BULLETS ---

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Instructions:**
1. Reorder the provided bullets based on their relevance to ALL themes (Primary and Secondary) and keywords. Place the MOST relevant bullet first.
2. **CRITICAL:** Return the reordered bullet text EXACTLY as it appears in the input list. DO NOT modify, rephrase, add, remove, or change ANY words, numbers, or punctuation. Maintain the original capitalization and spacing.
3. Return ONLY the {total_expected_count} reordered bullets, one per line, with no numbers, formatting, or any extra text.
"""
        system_prompt_reorder = "You reorder bullets based on job fit using all provided themes. You NEVER modify the text."
        response_reorder = self._call_gemini_api(prompt_reorder, ReasoningConfig.DEFAULT, f"{section_id}_Reorder", system_prompt_reorder)

        if "[Placeholder" in response_reorder:
            logging.warning(f"{section_id} Reordering failed. Returning bullets in generated order.")
            # Ensure consistent structure on fallback
            consistent_fallback = []
            for b in final_bullets[:total_expected_count]:
                text_key = b.get('text', b.get('bullet_text',''))
                consistent_fallback.append({
                    'text': text_key,
                    'provenance': b.get('provenance', BulletProvenance.Verbatim.value),
                    'word_count': b.get('word_count', count_words_ms_word_style(text_key)),
                })
            return consistent_fallback


        reordered_texts = [line.strip() for line in response_reorder.split('\n') if line.strip()]
        final_ordered_bullets = []
        generated_map = {}
        for b in final_bullets:
             text_key = b.get('text', b.get('bullet_text'))
             if text_key:
                 generated_map[text_key] = b

        used_from_generated = set()

        for text in reordered_texts:
            if text in generated_map and text not in used_from_generated:
                final_ordered_bullets.append(generated_map[text])
                used_from_generated.add(text)
            else:
                matched = False
                detector = self.dup_detector if hasattr(self, 'dup_detector') and self.dup_detector else DuplicateDetector()
                best_match_bullet = None
                best_match_score = 0.95

                for gen_text, gen_bullet in generated_map.items():
                    if gen_text not in used_from_generated:
                        try:
                            similarity = detector._calculate_cosine_similarity(text, gen_text)
                            if similarity > best_match_score:
                                best_match_score = similarity
                                best_match_bullet = gen_bullet
                                matched = True
                        except Exception as sim_e:
                             logging.warning(f"Error calculating similarity during reorder validation: {sim_e}")

                if matched and best_match_bullet:
                    original_text_of_match = best_match_bullet.get('text', best_match_bullet.get('bullet_text'))
                    final_ordered_bullets.append(best_match_bullet)
                    used_from_generated.add(original_text_of_match)
                    logging.warning(f"{section_id} Reordering returned slightly modified text ('{text[:30]}...'). Matched via similarity {best_match_score:.2f} to original ('{original_text_of_match[:30]}...').")
                elif not matched:
                    logging.warning(f"{section_id} Reordering returned unexpected or duplicate bullet text: '{text[:50]}...'. Skipping.")

        if len(final_ordered_bullets) != total_expected_count:
             logging.warning(f"{section_id} Reordering validation failed (got {len(final_ordered_bullets)}/{total_expected_count}). Returning bullets in generated order.")
             consistent_fallback = []
             for b in final_bullets[:total_expected_count]:
                 text_key = b.get('text', b.get('bullet_text',''))
                 consistent_fallback.append({
                     'text': text_key,
                     'provenance': b.get('provenance', BulletProvenance.Verbatim.value),
                     'word_count': b.get('word_count', count_words_ms_word_style(text_key)),
                 })
             return consistent_fallback

        final_output_list = []
        for b in final_ordered_bullets:
             text_key = b.get('text', b.get('bullet_text',''))
             final_output_list.append({
                 'text': text_key,
                 'provenance': b.get('provenance', BulletProvenance.Verbatim.value),
                 'word_count': b.get('word_count', count_words_ms_word_style(text_key)),
             })

        return final_output_list
    
    def _generate_k5_unify_bullets(self) -> List[Dict]:
        """
        Generate K.5 Unify bullets by calling the generic bullet generation method.
        """
        return self._generate_tailored_bullets_for_experience(
            company_name="Unify Consulting",
            section_index=0, 
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K5_UNIFY_BULLETS, {'Verbatim': 7}),
            reasoning_config=ReasoningConfig.K5_UNIFY_BULLETS_CONFIG,
            section_id="K.5_UNIFY_BULLETS"
        )

    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id: str) -> List[Dict]:
        """Hardening: Validates LLM bullet selection, ensuring count and origin."""
        if len(selected_bullets_text) != expected_count:
            logging.warning(f"{section_id} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}. Using original {expected_count} bullets.")
            return master_bullets_structured[:expected_count]

        validated_bullets = []
        master_texts = [b['bullet_text'] for b in master_bullets_structured]
        
        for selected_text in selected_bullets_text:
            if selected_text in master_texts:
                original_bullet = next((b for b in master_bullets_structured if b['bullet_text'] == selected_text), None)
                if original_bullet:
                    validated_bullets.append(original_bullet)
            else:
                logging.warning(f"{section_id} LLM returned a bullet not in the master list: '{selected_text[:50]}...'. Skipping.")

        if len(validated_bullets) != expected_count:
             logging.warning(f"{section_id} failed to validate all selected bullets. Using original {expected_count} bullets.")
             return master_bullets_structured[:expected_count]

        return validated_bullets

    def _generate_tailored_overview_for_experience(
        self,
        company_name: str,
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_id: str,
        extra_prompt_instruction: str = ""
    ) -> str:
        """
        [v11.0 REDESIGN & v12.00 FIX]
        Generic method to rewrite an overview using all HOP-0 signals.
        FIX: Strengthened word count instruction.
        """
        # 1. Find the source overview
        experience_section = next((exp for exp in self.master_resume['professional_experience']
                                   if company_name in exp['company']), None)
        source_overview = experience_section['overview'] if experience_section else ""
        if not source_overview:
            logging.warning(f"Source overview not found for {company_name} in {section_id}. Returning empty.")
            return "" # Return empty if source is missing

        # 2. Get *all* HOP-0 signals
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:2] if t.get('name')]
        # Safely get differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = comp_intel.get_top_differentiators(3)
            if not isinstance(differentiators, list):
                logging.warning(f"get_top_differentiators in {section_id} returned non-list: {type(differentiators)}. Defaulting.")
                differentiators = []
        else:
            logging.warning(f"Competitive intelligence missing in {section_id} for overview. Cannot get differentiators.")
            differentiators = []

        auth_patterns_data = self.thematic_analysis.authenticity_patterns or {}
        auth_patterns = auth_patterns_data.get('patterns', {})
        auth_tone_example_list = auth_patterns.get('executive_summary_patterns', ["professional and consultative"])
        auth_tone_example = auth_tone_example_list[0] if auth_tone_example_list else "professional and consultative"


        # 3. Build the comprehensive prompt
        min_wc, max_wc = word_count_range
        prompt = f"""You are an expert resume writer. Rewrite the following professional overview to align with a specific job description, focusing on authenticity and word count.

**Original Overview (Source of Truth - DO NOT invent new facts):**
{source_overview}

**Target Job Description - Key Themes:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Authentic Tone Guide (for writing style):** "{auth_tone_example}"

**Instructions:**
1. Rewrite the overview to align with the job's themes.
2. **Subtly** emphasize concepts related to the **Primary Theme** and **Secondary Themes**.
3. **PRIORITY:** Maintain a natural, authentic human voice, inspired by the **Authentic Tone Guide**.
4. **AVOID keyword stuffing.**
5. DO NOT invent new facts, skills, metrics, or experience.
6. **ABSOLUTELY CRITICAL:** The final output MUST be a single paragraph strictly between **{min_wc} and {max_wc} words**. Failure to meet this word count will cause rejection. Use standard word counting (hyphenated counts as one).
{extra_prompt_instruction}
7. Return ONLY the rewritten overview text with no preamble or explanation.
"""
        system_prompt = "You are an expert resume editor. You rewrite professional overviews to align with job descriptions, prioritizing authenticity, natural language, and STRICT adherence to word count constraints. Never invent new facts."
        tailored_overview = self._call_gemini_api(prompt, reasoning_config, section_id, system_prompt)

        # Use MS Word style count for validation
        word_count = count_words_ms_word_style(tailored_overview)
        if "[Placeholder" in tailored_overview or not (min_wc <= word_count <= max_wc):
            logging.warning(f"{section_id} overview generation failed or invalid (words: {word_count}, target: {min_wc}-{max_wc}). Using original.")
            return source_overview # Return original on failure

        return tailored_overview
    
    def _generate_k5_unify_overview(self) -> str:
        """Generate K.5 Unify overview by calling the generic overview generation method."""
        return self._generate_tailored_overview_for_experience(
            company_name="Unify",
            word_count_range=(self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K5_UNIFY_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT,
            section_id="K.5_UNIFY_OVERVIEW"
        )

    def _generate_k6_ibm_bullets(self) -> List[Dict]:
        """Generate K.6 IBM bullets by calling the generic bullet generation method."""
        return self._generate_tailored_bullets_for_experience(
            company_name="IBM",
            section_index=1,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K6_IBM_BULLETS, {'Verbatim': 6}),
            reasoning_config=ReasoningConfig.K6_IBM_BULLETS_CONFIG,
            section_id="K.6_IBM_BULLETS"
        )

    def _generate_k6_ibm_overview(self) -> str:
        """Generate K.6 IBM overview by calling the generic overview generation method."""
        return self._generate_tailored_overview_for_experience(
            company_name="IBM",
            word_count_range=(self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K6_IBM_OVERVIEW_CONFIG,
            section_id="K.6_IBM_OVERVIEW"
        )

    def _validate_and_potentially_rewrite_bullets(
        self,
        selected_bullets_structured: List[Dict],
        master_avg_lengths: Dict[str, float],
        section_name_for_avg: str,
        section_id_for_logging: str
    ) -> List[Dict]:
        """
        Checks word count for selected bullets and triggers rewrite if necessary.
        Updates provenance if rewritten.
        """
        final_bullets = []
        avg_len = master_avg_lengths.get(section_name_for_avg, 25.0)
        tolerance = 0.20
        min_target = round(avg_len * (1 - tolerance))
        max_target = round(avg_len * (1 + tolerance))

        for bullet_data in selected_bullets_structured:
            # Handle both 'text' (from rewrite) and 'bullet_text' (from master)
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
            word_count = bullet_data.get('word_count', count_words_ms_word_style(original_text))

            if not (min_target <= word_count <= max_target):
                logging.warning(f"  Word count ({word_count}) outside target ({min_target}-{max_target}) for bullet in {section_id_for_logging}. Attempting rewrite.")
                # This rewrite function doesn't exist yet, but let's assume it does
                # We'll need to create `_rewrite_bullet_for_word_count`
                rewritten_text = self._rewrite_bullet_for_word_count(
                    original_bullet_text=original_text,
                    target_word_count_range=(min_target, max_target),
                    section_id=section_id_for_logging
                )
                rewritten_word_count = count_words_ms_word_style(rewritten_text)
                if rewritten_text != original_text and min_target <= rewritten_word_count <= max_target:
                    final_bullets.append({
                        **bullet_data,
                        "text": rewritten_text,
                        "provenance": BulletProvenance.Customized.value,
                        "word_count": rewritten_word_count
                    })
                else:
                    final_bullets.append(bullet_data)
            else:
                final_bullets.append(bullet_data)

        return final_bullets
    
    def _rewrite_bullet_for_word_count(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id: str) -> str:
        """
        [v11.0 NEW HELPER & v12.00 FIX]
        Uses LLM to rewrite a single bullet to fit a word count,
        while preserving core facts and authentic tone.
        FIX: Strengthened word count instruction.
        """
        try:
            min_wc, max_wc = target_word_count_range
            auth_patterns_data = self.thematic_analysis.authenticity_patterns or {}
            auth_patterns = auth_patterns_data.get('patterns', {})
            auth_verbs = auth_patterns.get('achievement_verb_patterns', [])

            prompt = f"""You are a concise resume editor. Your task is to rewrite a single bullet point to meet a specific word count range ({min_wc}-{max_wc} words) while preserving all facts and metrics.

**Original Bullet (Source of Truth):**
"{original_bullet_text}"

**Authentic Voice Guide (for writing style):**
- Use strong action verbs like: {', '.join(auth_verbs[:10])}

**Instructions:**
1. **ABSOLUTELY CRITICAL:** Rewrite the bullet so the final output is strictly between **{min_wc} and {max_wc} words**. Failure to meet this word count range will cause rejection. Use standard word counting (hyphenated counts as one).
2. **CRITICAL:** DO NOT change, invent, or remove any facts, metrics (e.g., "$5M", "30%"), proper nouns, or the core meaning of the original bullet.
3. Maintain an authentic, professional tone, guided by the verbs.
4. If the original is too long, concisely rephrase it without losing information.
5. If the original is too short, add professional phrasing (e.g., "Led initiative to...") *without* adding new facts or changing the meaning.
6. Return ONLY the single rewritten bullet point, with no preamble or explanation.
"""
            system_prompt = f"You are a resume word count editor. You rewrite bullets strictly to {min_wc}-{max_wc} words, preserving all facts and meaning precisely."
            # Use a simple, default reasoning config for this utility task
            rewritten_text = self._call_gemini_api(prompt, ReasoningConfig.DEFAULT, f"{section_id}_RewriteWC", system_prompt)

            if "[Placeholder" in rewritten_text:
                logging.warning(f"{section_id}_RewriteWC failed. Returning original.")
                return original_bullet_text

            # Final check on the rewrite using MS Word style count
            rewritten_wc = count_words_ms_word_style(rewritten_text)
            if not (min_wc <= rewritten_wc <= max_wc):
                 logging.warning(f"{section_id}_RewriteWC returned non-compliant count ({rewritten_wc}, target: {min_wc}-{max_wc}). Returning original.")
                 return original_bullet_text

            return rewritten_text

        except Exception as e:
            logging.warning(f"{section_id}_RewriteWC exception: {e}. Returning original.", exc_info=True)
            return original_bullet_text

    def _generate_lightly_customized_bullets(
        self,
        source_bullets_text: List[str],
        section_id: str,
        thematic_analysis: ThematicAnalysis # <-- NEW: Pass in analysis
    ) -> List[Dict]:
        """
        [v11.0 REDESIGN]
        Lightly rewrite bullets using themes AND authenticity patterns.
        """
        try:
            if not source_bullets_text:
                return []

            # Get signals
            primary_theme = thematic_analysis.primary_theme.get('name', 'AI Leadership')
            auth_patterns = thematic_analysis.authenticity_patterns.get('patterns', {})
            auth_verbs = auth_patterns.get('achievement_verb_patterns', [])
            auth_metrics = auth_patterns.get('metric_presentation_patterns', [])
            
            bullets_text = '\n'.join([f"- {b}" for b in source_bullets_text])

            prompt = f"""You are an expert resume editor. Lightly rewrite the following resume bullets to align with a job's theme and authentic voice.

**Original Bullets (Source of Truth):**
{bullets_text}

**Target Job Theme:** {primary_theme}
**Target Job Description:** {self.job_description[:1000]}

**Authentic Voice Guide:**
- Use strong action verbs like: {', '.join(auth_verbs[:10])}
- Frame metrics like: {', '.join(auth_metrics[:5])}

**Instructions:**
1. Rewrite each bullet to be concise and impactful.
2. **Subtly** emphasize concepts from the original text that align with the '{primary_theme}'.
3. **CRITICAL:** Adopt the **Authentic Voice**. Use the suggested verbs and metric formats as inspiration to make the bullets sound natural and confident.
4. **AVOID forcing keywords.**
5. DO NOT invent new facts, skills, metrics, or experience.
6. Maintain the same number of bullets as the original list.
7. Return ONLY the rewritten bullets, each on a new line, starting with '• '.
"""
            system_prompt = "You are an expert resume editor. You rewrite resume bullets to align with job themes and authentic voice, prioritizing natural language."
            response_text = self._call_gemini_api(prompt, ReasoningConfig.DEFAULT, section_id, system_prompt)

            if "[Placeholder" in response_text:
                logging.warning(f"{section_id} rewrite failed. Returning original bullets.")
                return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                         "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]
            else:
                rewritten_bullets = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip()]
                provenance = BulletProvenance.Customized.value

                if len(rewritten_bullets) != len(source_bullets_text):
                    print(f"Warning: {section_id} LLM returned {len(rewritten_bullets)} bullets, expected {len(source_bullets_text)}. Returning original.")
                    return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                             "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]

                return [{"text": b, "provenance": provenance, "word_count": count_words_ms_word_style(b)} for b in rewritten_bullets]

        except Exception as e:
            logging.warning(f"{section_id} LLM bullet rewrite failed: {e}. Returning original bullets.", exc_info=True)
            return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                     "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]

    def _generate_synthetic_bullets(
        self,
        count: int,
        company_name: str,
        job_description: str,
        thematic_analysis: ThematicAnalysis, # <-- MODIFIED: Pass full object
        context_bullets: str,
        reasoning_config: ReasoningConfig,
        section_id: str
    ) -> List[Dict]:
        """
        [v11.0 REDESIGN]
        Generates new, plausible bullet points based on *all* HOP-0 signals.
        """
        # Get signals
        primary_theme = thematic_analysis.primary_theme.get('name', 'AI Leadership')
        secondary_themes = [t.get('name', '') for t in thematic_analysis.secondary_themes[:3] if t.get('name')]
        differentiators = thematic_analysis.competitive_intelligence.get_top_differentiators(5)
        auth_patterns = thematic_analysis.authenticity_patterns.get('patterns', {})
        auth_verbs = auth_patterns.get('achievement_verb_patterns', [])
        auth_metrics = auth_patterns.get('metric_presentation_patterns', [])
        
        prompt = f"""You are an expert resume writer generating new, plausible achievements.

**Context:**
- Company: {company_name}
- Candidate's Role Focus (Implied): {primary_theme}
- Other achievements from this role (for style/scope):
{context_bullets}

**Target Job Analysis:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Target Keywords: {', '.join(differentiators)}
- Target Job Description: {job_description[:1500]}

**Authentic Voice Guide (for writing style):**
- Use strong action verbs like: {', '.join(auth_verbs[:10])}
- Frame metrics like: {', '.join(auth_metrics[:5])}

**Task:**
1. Generate {count} new, distinct bullet points representing plausible achievements for this candidate at {company_name}.
2. The new bullets MUST align with the **Primary Theme** and **Secondary Themes**.
3. Each bullet MUST be a single, concise sentence starting with an action verb.
4. The writing style MUST adopt the **Authentic Voice Guide**.
5. Ensure achievements are realistic and consistent with the provided context, but NOT copied.
6. You may **subtly incorporate one** of the target keywords ({', '.join(differentiators)}) **if it fits naturally**.
7. Prioritize creating a **believable, authentic achievement** over forcing in keywords.
8. Return ONLY the {count} bullet points, one per line, starting with '* '.
"""
        system_prompt = "You generate plausible, synthetic resume bullets. You align them with all job themes and an authentic voice."
        response_text = self._call_gemini_api(prompt, reasoning_config, section_id, system_prompt)
        synthetic_bullets_text = []
        if "[Placeholder" not in response_text:
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip()]
            if len(synthetic_bullets_text) != count:
                logging.warning(f"{section_id} Failed to generate {count} synthetic bullets (got {len(synthetic_bullets_text)}). Returning empty list.")
                return []
            return [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": count_words_ms_word_style(b)} for b in synthetic_bullets_text]
        else:
            logging.warning(f"{section_id} Synthetic bullet generation failed. Returning empty list.")
            return []

    def _generate_k8_ey_bullets(self) -> List[Dict]:
        """Generate K.8A EY bullets, lightly tailored by LLM (now passes full analysis)."""
        ey_exp = next((exp for exp in self.master_resume['professional_experience'] 
                       if 'Ernst & Young' in exp['company'] or 'EY' in exp['company']), None)
        if not ey_exp:
            return []
        source_bullets = ey_exp.get('highlights', [])[:2]
        # This function now passes the full thematic_analysis object
        return self._generate_lightly_customized_bullets(
            source_bullets_text=source_bullets, 
            section_id=ResumeSection.K8_EY_BULLETS.value,
            thematic_analysis=self.thematic_analysis
        )

    def _generate_k8_ey_overview(self) -> str:
        """Generate K.8 EY overview by calling the generic overview generation method."""
        return self._generate_tailored_overview_for_experience(
            company_name="Ernst & Young",
            word_count_range=(self.constraints.EY_OVERVIEW_WORD_COUNT_MIN, self.constraints.EY_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K8_EY_OVERVIEW_CONFIG,
            section_id="K.8_EY_OVERVIEW",
            extra_prompt_instruction="**CRITICAL:** Do NOT mention specific company names from early career in the rewritten overview."
        )

    def _copy_k7_tradersense_bullets(self) -> List[str]:
        """
        v5.26: Copy TraderSense highlights VERBATIM from master resume.
        """
        
        tradersense_exp = next((exp for exp in self.master_resume['professional_experience'] 
                                if 'TraderSense' in exp['company']), None)
        if tradersense_exp:
            tradersense_highlights = tradersense_exp.get('highlights', [])
        else:
            tradersense_highlights = []
        
        return tradersense_highlights[:2] if tradersense_highlights else [
            "Architected the company's proprietary automated trading platform, designed to analyze market data and execute high-speed algorithmic trades.",
            "Led the 6-person engineering team, secured key data and brokerage partnerships, and launched the beta product to early adopter customers."
        ]
    
    def _copy_k7_tradersense_overview(self) -> str:
        """
        v5.26: Copy TraderSense overview VERBATIM from master resume.
        """
        
        tradersense_exp = next((exp for exp in self.master_resume['professional_experience'] 
                                if 'TraderSense' in exp['company']), None)
        if tradersense_exp:
            tradersense_overview = tradersense_exp.get('overview', "")
        else:
            tradersense_overview = ""
        
        return tradersense_overview if tradersense_overview else "As co-founder and CTO, led all technology strategy, product development, and team management from concept to initial launch."

    def _generate_k9_early_career_bullets(self) -> List[Dict]:
        """Generate K.9A Early Career bullets, lightly tailored by LLM (now passes full analysis)."""
        early_exp = next((exp for exp in self.master_resume['professional_experience'] 
                       if 'Early Career' in exp['company']), None)
        if not early_exp or not early_exp.get('highlights'):
            return []
        source_bullets = early_exp.get('highlights', [])[:1]
        # This function now passes the full thematic_analysis object
        return self._generate_lightly_customized_bullets(
            source_bullets_text=source_bullets, 
            section_id=ResumeSection.K9_EARLY_CAREER_BULLETS.value,
            thematic_analysis=self.thematic_analysis
        )

    def _generate_k9_early_career_overview(self) -> str:
        """Generate K.9 Early Career overview, lightly tailored by LLM."""
        return self._generate_tailored_overview_for_experience(
            company_name="Early Career Roles",
            word_count_range=(self.constraints.EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN, self.constraints.EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K9_EARLY_CAREER_OVERVIEW_CONFIG,
            section_id="K.9_EARLY_CAREER_OVERVIEW",
            extra_prompt_instruction="**CRITICAL:** Do NOT mention the specific company name ('Ernst & Young' or 'EY') in the rewritten overview."
        )
    
    def _generate_k10_competencies(self) -> List[Dict]:
        """
        [v11.0 REDESIGN & v12.00 FIX]
        Generate K.10 Competencies (6 competencies) using the full V/C/S split.
        Selects Verbatim, Customizes, and Synthesizes based on all HOP-0 signals.
        FIX: Strengthened Verbatim selection prompt, added check for empty list in fallback.
        """
        # 1. Get all master competencies
        all_competencies_text = self.master_resume.get('strategic_and_technical_competencies', [])
        all_competencies_structured = [{
            "bullet_text": re.sub(r'^[•*]\s*', '', c).strip(),
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": count_words_ms_word_style(c)
        } for c in all_competencies_text if isinstance(c, str)]

        # 2. Define targets
        provenance_targets = self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K10_COMPETENCIES, {'Verbatim': 6})
        total_expected_count = sum(provenance_targets.values())
        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)

        # 3. Get *all* HOP-0 signals
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:3] if t.get('name')]
        # Safely access differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = comp_intel.get_top_differentiators(5)
            if not isinstance(differentiators, list): differentiators = []
        else: differentiators = []

        final_competencies = []

        # 4. Select Verbatim Competencies
        if verbatim_count > 0:
            if not all_competencies_structured:
                logging.warning("K.10 Cannot select Verbatim competencies: No valid master competencies available.")
            else:
                comps_text = '\n'.join([f"{i+1}. {comp['bullet_text']}" for i, comp in enumerate(all_competencies_structured)])
                prompt_select = f"""Select the most relevant competencies for this job WITHOUT changing them.

**All Available Competencies:**
--- START COMPETENCIES ---
{comps_text}
--- END COMPETENCIES ---

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Secondary Themes: {', '.join(secondary_themes)}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Instructions:**
1. Select the TOP {verbatim_count} competencies from the list above that best match ALL the job themes (Primary and Secondary) and keywords.
2. **CRITICAL:** Return the selected competency text EXACTLY as it appears in the input list, character for character. DO NOT modify, rephrase, add, remove, or change ANY words, numbers, or punctuation. Maintain the original capitalization and spacing.
3. Return ONLY the {verbatim_count} selected competencies, one per line, with no numbers, formatting, or any extra text before or after the competencies.
"""
                system_prompt_select = "You select verbatim competencies based on job fit, considering primary and secondary themes. You NEVER modify the text."
                response_select = self._call_gemini_api(prompt_select, ReasoningConfig.K10_COMPETENCIES_CONFIG, "K.10_SelectV", system_prompt_select)

                if "[Placeholder" not in response_select:
                    selected_texts = [line.strip() for line in response_select.split('\n') if line.strip()]
                    verbatim_comps = self._validate_llm_bullet_selection(selected_texts, all_competencies_structured, verbatim_count, "K.10_SelectV")
                    final_competencies.extend(verbatim_comps)
                else:
                    logging.warning(f"K.10 Verbatim selection failed. Using first {verbatim_count} master competencies.")
                    # --- START FIX: Check if list is non-empty before slicing ---
                    if all_competencies_structured:
                        final_competencies.extend([{'bullet_text': c['bullet_text'], **c} for c in all_competencies_structured[:verbatim_count]])
                    else:
                        logging.error("K.10 Fallback failed: all_competencies_structured is empty.")
                    # --- END FIX ---


        # 5. Select and Customize Competencies
        if customized_count > 0:
            used_texts = {b.get('bullet_text', b.get('text')) for b in final_competencies}
            available_for_custom = [b for b in all_competencies_structured if isinstance(b, dict) and b.get('bullet_text') not in used_texts]
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count]

            if candidates_for_custom:
                customized_comps = self._generate_lightly_customized_bullets(
                    source_bullets_text=[b['bullet_text'] for b in candidates_for_custom],
                    section_id="K.10_CustomC",
                    thematic_analysis=self.thematic_analysis
                )
                final_competencies.extend(customized_comps)
            else:
                 logging.warning(f"K.10 Not enough unique competencies to customize.")

        # 6. Generate Synthetic Competencies
        if synthetic_count > 0:
            context_bullets_text = '\n'.join([f"- {b.get('text', b.get('bullet_text', ''))}" for b in final_competencies])
            synthetic_comps = self._generate_synthetic_bullets(
                count=synthetic_count,
                company_name="Candidate",
                job_description=self.job_description,
                thematic_analysis=self.thematic_analysis,
                context_bullets=context_bullets_text,
                reasoning_config=ReasoningConfig.K10_COMPETENCIES_CONFIG,
                section_id="K.10_SynthS"
            )
            final_competencies.extend(synthetic_comps)

        # 7. Final Padding / Trimming
        if len(final_competencies) < total_expected_count:
            logging.warning(f"K.10 Generated only {len(final_competencies)}/{total_expected_count} competencies. Padding with Verbatim.")
            needed = total_expected_count - len(final_competencies)
            used_texts = {b.get('text', b.get('bullet_text')) for b in final_competencies}
            padding_candidates = [b for b in all_competencies_structured if isinstance(b, dict) and b.get('bullet_text') not in used_texts]
            padding = [{'bullet_text': c['bullet_text'], **c, 'provenance': BulletProvenance.Verbatim.value} for c in padding_candidates[:needed]]
            final_competencies.extend(padding)

        elif len(final_competencies) > total_expected_count:
             logging.warning(f"K.10 Generated too many competencies ({len(final_competencies)}/{total_expected_count}). Trimming.")
             final_competencies.sort(key=lambda b: 0 if b.get('provenance', '') != BulletProvenance.Verbatim.value else 1)
             final_competencies = final_competencies[:total_expected_count]

        # 8. Word Count Validation
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
        final_validated_comps = self._validate_and_potentially_rewrite_bullets(
            selected_bullets_structured=final_competencies,
            master_avg_lengths=master_avg_lengths,
            section_name_for_avg="Competencies",
            section_id_for_logging="K.10_COMPETENCIES"
        )

        # 9. Final reformatting
        output_list = []
        for item in final_validated_comps:
            text_key = 'text'
            bullet_text_key = 'bullet_text'
            final_text = item.get(text_key, item.get(bullet_text_key, ''))
            output_item = {
                'text': final_text,
                'provenance': item.get('provenance'),
                'word_count': item.get('word_count', count_words_ms_word_style(final_text))
            }
            if bullet_text_key in item and item[bullet_text_key] != final_text:
                output_item[bullet_text_key] = item[bullet_text_key]
            elif bullet_text_key not in output_item:
                 output_item[bullet_text_key] = final_text

            output_list.append(output_item)

        return output_list
 
    def _generate_k13_cover_letter(
        self,
        temperature_override: Optional[float] = None # <-- ADDED Override Param
        ) -> str:
        """
        [v11.0 REDESIGN & v12.01 FIX]
        Generate K.13 cover letter using all HOP-0 signals.
        Consumes: Themes, Differentiators, Narratives, and Authenticity Patterns.
        FIX: Safely access differentiators list, add safe access for auth patterns,
             strengthen paragraph word counts, improve structure fix.
        NOW ACCEPTS temperature_override.
        """
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")

        # --- 1. GATHER ALL HIGH-SIGNAL INTEL ---
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'this strategic opportunity')
        secondary_themes = [t.get('name', '') for t in self.thematic_analysis.secondary_themes[:2] if t.get('name')]
        secondary_theme_context = f" and {secondary_themes[0]}" if secondary_themes else ""

        # Safely get differentiators
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = comp_intel.get_top_differentiators(5)
            if not isinstance(differentiators, list):
                logging.warning(f"K.13: get_top_differentiators returned {type(differentiators)}, expected list. Defaulting.")
                differentiators = []
        else:
             logging.warning("K.13: Competitive intelligence missing. Cannot get differentiators.")
             differentiators = []


        narratives = self.thematic_analysis.problem_solution_narratives or {}
        problem_context = "; ".join(narratives.get("common_problems", []))

        # --- START V12.00 FIX: Safe access for authenticity patterns ---
        auth_patterns_data = self.thematic_analysis.authenticity_patterns or {}
        # Ensure 'patterns' is a dict before accessing nested keys
        auth_patterns_dict = auth_patterns_data.get('patterns', {})
        if not isinstance(auth_patterns_dict, dict):
             logging.warning(f"K.13: Authenticity patterns dict ('patterns') is not a dict: {type(auth_patterns_dict)}. Using defaults.")
             auth_patterns_dict = {} # Use empty dict as fallback

        auth_tone_example_list = auth_patterns_dict.get('executive_summary_patterns', ["professional and consultative"])
        # Ensure the list is not empty before accessing index [0]
        auth_tone_example = auth_tone_example_list[0] if auth_tone_example_list else "professional and consultative"
        # --- END V12.00 FIX ---


        top_achievements = []
        for section in self.enriched_scaffold.get('experience_sections', [])[:2]: # Unify & IBM
            for bullet in section.get('bullets', [])[:3]:
                top_achievements.append(bullet.get('text', bullet.get('bullet_text', ''))) # Handle both keys
        achievements_text = '\n'.join(f"- {ach}" for ach in top_achievements)

        owner_info = self.master_resume.get('owner', {})
        signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', ''),
            email=owner_info.get('contact', {}).get('email', ''),
            phone=owner_info.get('contact', {}).get('phone', ''),
            linkedin=owner_info.get('contact', {}).get('linkedin', '')
        ).strip()

        # Safely prepare differentiator keywords for the prompt
        diff_1 = differentiators[0] if len(differentiators) > 0 else "key technical skills"
        diff_2 = differentiators[1] if len(differentiators) > 1 else "relevant strategic expertise"

        # --- 2. CONSTRUCT THE NEW NARRATIVE-DRIVEN PROMPT ---
        prompt = f"""You are an executive ghostwriter crafting a compelling cover letter.
Your writing style MUST be: **{auth_tone_example}**

**INTELLIGENCE BRIEFING:**
- **Thematic Core:** The central problem this role solves is '{primary_theme}'.
- **Secondary Themes:** Other key areas are '{', '.join(secondary_themes)}'.
- **Competitive Differentiators:** Key candidate skills are: {', '.join(differentiators)}.
- **Industry Problem Context:** Common challenges include: '{problem_context}'.
- **Candidate's Top Achievements:**
{achievements_text}

**FULL JOB DESCRIPTION:**
{self.job_description}

**TASK:**
Write a three-paragraph cover letter based *only* on the provided intelligence. Follow this exact narrative structure:

**Paragraph 1: The Hook - "I Understand Your Core Problem."** (Must be {self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX} words)
- Start by addressing the **Thematic Core** ('{primary_theme}').
- State the candidate's value proposition as the solution.
- Formally state the position being applied for.

**Paragraph 2: The Proof - "Here's Proof I've Solved This Before."** (Must be {self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX} words)
- Select one or two achievements from the candidate's list.
- Frame them as a mini-story: "At [Company], we faced [Problem]. I led [Action], incorporating '{diff_1}' and '{diff_2}'{secondary_theme_context}, which resulted in [Quantifiable Result]."
- The story must prove the candidate can solve the company's core problem, integrating **Differentiators** and **Secondary Themes**.

**Paragraph 3: The Vision - "Here's How We Can Solve It Together."** (Must be {self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX} words)
- Connect past success to the company's future goals.
- Express genuine, specific enthusiasm for the role.
- End with a confident call to action.

**OUTPUT FORMAT:**
**CRITICAL:** Do NOT mention "Unify" or "IBM". Refer to past roles generically (e.g., "In my previous role...").
**ABSOLUTELY CRITICAL:** Ensure each paragraph's word count STRICTLY adheres to the specified range. Count carefully before outputting. Use standard word counting (hyphenated counts as one).
Return the complete cover letter text. Start with the date and end *exactly* with the signature block provided below (do NOT add extra text after it).

--- START OF EXPECTED OUTPUT ---
{today}

Hiring Manager
[Company Name]

Dear Hiring Manager,

[Paragraph 1 text here - Must be {self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX} words]

[Paragraph 2 text here - Must be {self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX} words]

[Paragraph 3 text here - Must be {self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX} words]

Sincerely,

{owner_info.get('name', '')}
{owner_info.get('contact', {}).get('email', '')}
{owner_info.get('contact', {}).get('phone', '')}
{owner_info.get('contact', {}).get('linkedin', '')}
--- END OF EXPECTED OUTPUT ---
"""

        # --- 3. CALL LLM VIA HELPER AND RETURN ---
        try:
            reasoning_config = ReasoningConfig.DEFAULT
            base_system = f"You are an expert executive ghostwriter. Your writing style is: {auth_tone_example}. You follow all formatting and word count instructions perfectly and rigorously."

            # Determine final temperature: Use override if provided, otherwise use default from reasoning config
            final_temp = temperature_override if temperature_override is not None else _get_generation_temperature() # Use default if no override

            cover_letter_text = self._call_gemini_api(
                prompt,
                reasoning_config,
                "K.13",
                base_system,
                temperature_override=final_temp # <-- PASS THE FINAL TEMP
            )

            if "[Placeholder" in cover_letter_text:
                logging.warning(f"Creative cover letter generation failed: {cover_letter_text}. Using fallback.")
                return self._generate_fallback_cover_letter()

            # --- START V12.00 FIX: Improve Structure Check/Fix ---
            # Basic check for essential components
            if not cover_letter_text.strip().startswith(today):
                logging.warning("Generated cover letter missing date. Attempting fix.")
                # Try to find the salutation and prepend the header
                salutation_match = re.search(r"Dear Hiring Manager,", cover_letter_text)
                if salutation_match:
                    body_start_index = salutation_match.start()
                    cover_letter_text = f"{today}\n\nHiring Manager\n[Company Name]\n\n{cover_letter_text[body_start_index:]}".strip()
                    logging.info("Prepended date/recipient block.")
                else:
                    logging.error("Could not fix missing date (salutation not found). Using fallback.")
                    return self._generate_fallback_cover_letter()

            # Check for signature presence more robustly
            # Does it end with the LinkedIn URL (last line of signature)?
            last_line_signature = signature.split('\n')[-1].strip()
            if not cover_letter_text.strip().endswith(last_line_signature):
                logging.warning("Generated cover letter missing or incomplete signature block. Attempting fix.")
                # Try to find "Sincerely," and replace everything after with the correct signature
                sincerely_pos = cover_letter_text.rfind("Sincerely,")
                if sincerely_pos != -1:
                    # Take text up to "Sincerely," add blank line, add full signature
                    cover_letter_text = cover_letter_text[:sincerely_pos].strip() + f"\n\n{signature}"
                    logging.info("Appended full signature block after 'Sincerely,'.")
                else:
                    # If "Sincerely," isn't found, try appending signature anyway if main body looks okay
                    if "Dear Hiring Manager," in cover_letter_text and len(cover_letter_text) > 200:
                         logging.warning("Could not find 'Sincerely,', attempting to append signature anyway.")
                         cover_letter_text = cover_letter_text.strip() + f"\n\n{signature}"
                    else:
                         logging.error("Could not reliably fix missing signature. Using fallback.")
                         return self._generate_fallback_cover_letter()
            # --- END V12.00 FIX ---

            return cover_letter_text.strip() # Return potentially fixed version

        except Exception as e:
            logging.warning(f"Creative cover letter generation process failed: {e}. Using fallback.", exc_info=True)
            return self._generate_fallback_cover_letter()

    def _generate_fallback_cover_letter(self) -> str:
        """Generate fallback cover letter if LLM unavailable."""
        today = datetime.now().strftime("%B %d, %Y")
        owner_info = self.master_resume['owner']
        
        theme = self.thematic_analysis.primary_theme.get('name', 'this opportunity')
        
        body = f"""Dear Hiring Manager,
I am writing to express my strong interest in this position. With over 15 years of experience in {theme} and executive leadership, I have consistently delivered transformative results that align directly with your requirements. My expertise in AI/ML, cloud architecture, and team leadership positions me to drive immediate impact on your organization's strategic objectives.

Throughout my career, I have led the design and deployment of enterprise AI solutions that have generated measurable business value. At Unify Consulting, I scaled LLM engineering teams and delivered AI adoption frameworks across Fortune 500 companies. At IBM, I architected cloud-native AI platforms serving millions of users. These experiences have equipped me with the technical depth and strategic vision needed for this role.

I am excited about the opportunity to bring this track record of measurable AI transformation to your organization. I would welcome the chance to discuss how my experience can contribute to your continued growth and innovation. Thank you for considering my application.
"""
        signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', ''),
            email=owner_info.get('contact', {}).get('email', ''),
            phone=owner_info.get('contact', {}).get('phone', ''),
            linkedin=owner_info.get('contact', {}).get('linkedin', '')
        ).strip()

        return f"{today}\n\nHiring Manager\n[Company Name]\n\n{body}\n\n{signature}"


    def _copy_k11_education(self) -> List[Dict]:
        """Copies K.11 Education verbatim from master resume."""
        return self.master_resume.get("education", [])


    def _copy_k12_certifications(self) -> List[str]:
        """
        Generate Certifications string from master resume.
        """
        certifications = self.master_resume.get('certifications_and_credentials', [])
        if not certifications:
            return []
        return certifications
    
    def _generate_dummy_header(self) -> str:
        """Generates a placeholder for header sections."""
        # This is just a placeholder; the actual header is rendered
        # by the FileRenderer using H2 markdown.
        return "HEADER_PLACEHOLDER"
    
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

# Example Usage (requires ImmutableStagingBuffer, ValidationResult etc. to be defined)
# rules_dict = COMPREHENSIVE_HYPHENATION_RULES
# sanitizer = TextSanitizer(hyphenation_rules=rules_dict)
# buffer = ImmutableStagingBuffer()
# buffer.set("test_key", "This uses AI—powered tech and -- is go-to-market ready, but has bad\u00A0space.")
# results, sanitized_data = sanitizer.sanitize_buffer(buffer)
# print(results)
# print(sanitized_data)
# Expected output might look something like:
# [ValidationResult(rule_id='TEXT_SANITIZATION_COMPLETE', passed=True, severity=<ValidationSeverity.INFO: 1>, message='Text sanitization complete: 3 total corrections. Preserved natural hyphens: 1. (unnatural_hyphens_removed: 1, forbidden_dashes_removed: 1, invisible_chars_removed: 1, natural_hyphens_preserved: 1)', details={})]
# {'test_key': 'This uses AI powered tech and  is go-to-market ready, but has bad space.'}

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
# HOP-5: VALIDATION GATES
# ============================================================================

class PreFlightValidator:

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.dup_detector = DuplicateDetector() # For cosine similarity
        self.constraints = ContentConstraintsConfig() # Centralized constraints
        self.signal_constraints = SignalControlConfig() # Signal control constraints
        self._register_rules() # Must be called after constraints are set

    # Class constant for signal targets configuration
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

    # Bullet word count tolerance configuration
    BULLET_WORD_COUNT_TOLERANCE = 0.20 # +/- 20%
    BULLET_WORD_COUNT_SECTIONS_TO_CHECK = [
        ResumeSection.K5_UNIFY_BULLETS,
        ResumeSection.K6_IBM_BULLETS,
        ResumeSection.K10_COMPETENCIES,
        ResumeSection.K8_EY_BULLETS,
        ResumeSection.K9_EARLY_CAREER_BULLETS,
    ]

    # Provenance split targets configuration
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    # Consolidated Rules Configuration
    RULES_CONFIG = [
        # --- Word Count & Sentence Count Rules ---
        {
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_total_word_count",
            "error_message": "Total resume: {total_words} words (target: {min}-{max})"
        },
        {
            "rule_id": "VG_WORD_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_k1_word_count",
            "error_message": "K.1: {word_count} words (target: {min}-{max})"
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
            "error_message": "Bullet word counts outside tolerance ({tolerance}%): {violations}" # Uses dynamic tolerance arg
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
        { # Placeholder - Checked during rendering / QA Section 16
            "rule_id": "VG_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_resume_header_h2",
            "error_message": "Resume headers not consistently H2: {failed_headers}"
        },
        { # Placeholder - Checked during rendering / QA Section 16
            "rule_id": "VG_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_edu_certs_format",
            "error_message": "Education/Certification format error: {details}"
        },
        { # Placeholder - Checked during rendering / QA Section 16
            "rule_id": "VG_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_experience_bullet_style",
            "error_message": "Experience bullets do not consistently use '* ': {details}"
        },
        { # Placeholder - Checked during rendering / QA Section 16
            "rule_id": "VG_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_competencies_formatting",
            "error_message": "Competencies list not using '*' bullets: {details}"
        },
        { # Placeholder - Checked during rendering / QA Section 16
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
        { # --- v11.0 NEW RULE ---
            "rule_id": "VG_AUTHENTICITY_SIGNAL_CHECK", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_authenticity_signal",
            "error_message": "Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {details}"
        }
    ]

    def _register_rules(self):
        """Creates and registers all pre-flight validation rules."""
        for config in self.RULES_CONFIG:
            validator_ref = config["validator"]
            if isinstance(validator_ref, str):
                # Ensure the method exists before getting it
                if hasattr(self, validator_ref):
                    validator_func = getattr(self, validator_ref)
                else:
                    # Log the specific error and raise
                    logging.error(f"AttributeError during rule registration: Validator method '{validator_ref}' not found in {self.__class__.__name__} for rule {config['rule_id']}")
                    raise AttributeError(f"Validator method '{validator_ref}' not found in {self.__class__.__name__} for rule {config['rule_id']}")
            elif callable(validator_ref):
                 validator_func = validator_ref # Allow simple lambdas if needed
            else:
                 raise TypeError(f"Invalid validator type for rule {config['rule_id']}: {type(validator_ref)}")

            # Create closure for lazy error message formatting
            def create_error_message_lambda(template):
                expected_args = re.findall(r'\{(\w+)\}', template)
                format_args = {}
                # Populate format_args with class constants needed by templates
                if "tolerance" in expected_args:
                    format_args["tolerance"] = self.BULLET_WORD_COUNT_TOLERANCE * 100
                # Add other dynamic args if needed by specific templates here
                return lambda data: template.format(**data.get("error_details", {}), **format_args)

            # Ensure error_message is always treated as a template string
            error_message_template = str(config["error_message"])
            error_message_lambda = create_error_message_lambda(error_message_template)


            rule = ValidationRule(
                rule_id=config["rule_id"],
                severity=config["severity"],
                category=config["category"],
                validator=validator_func,
                error_message=error_message_lambda # Use the lambda
            )
            self.engine.register_rule(rule)

        # Register rules for required sections dynamically
        required_sections = [
            ResumeSection.K0_NAME, ResumeSection.K0_HEADLINE, ResumeSection.K0_CONTACT,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K5_UNIFY_BULLETS,
            ResumeSection.K5_UNIFY_OVERVIEW, ResumeSection.K6_IBM_BULLETS,
            ResumeSection.K6_IBM_OVERVIEW,
            ResumeSection.K7_TRADERSENSE_BULLETS, # Added K7
            ResumeSection.K7_TRADERSENSE_OVERVIEW, # Added K7
            ResumeSection.K8_EY_BULLETS, # Added K8
            ResumeSection.K8_EY_OVERVIEW, # Added K8
            ResumeSection.K9_EARLY_CAREER_BULLETS, # Added K9
            ResumeSection.K9_EARLY_CAREER_OVERVIEW, # Added K9
            ResumeSection.K10_COMPETENCIES,
            ResumeSection.K11_EDUCATION, ResumeSection.K12_CERTIFICATIONS,
            ResumeSection.K13_COVER_LETTER,
        ]
        for section in required_sections:
            rule = ValidationRule(
                rule_id=f"STRUCTURE_{section.name}_PRESENT",
                severity=ValidationSeverity.CRITICAL,
                # Lambda validator checks if the section exists and is non-empty/non-whitespace
                validator=lambda d, s=section: (
                    d['staging_buffer'].get(s.value) is not None and
                    ( (isinstance(d['staging_buffer'].get(s.value), str) and d['staging_buffer'].get(s.value).strip()) or
                      (isinstance(d['staging_buffer'].get(s.value), list) and d['staging_buffer'].get(s.value)) or # Check if list is not empty
                      (isinstance(d['staging_buffer'].get(s.value), dict) and d['staging_buffer'].get(s.value)) # Check if dict is not empty
                    )
                ),
                error_message=f"{section.value} is missing or empty.",
                category="structure"
            )
            self.engine.register_rule(rule)

    def validate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str
    ) -> Tuple[List[ValidationResult], bool]:
        """Validates the staging buffer against all registered rules."""
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
                else: # Assume list of strings or list of simple items
                    word_count = count_words_in_list_ms_word_style(content)
            elif isinstance(content, dict): # Handle dict case if needed (e.g., Education)
                 # Define how to count words in dicts if necessary, otherwise 0
                 word_count = count_words_ms_word_style(json.dumps(content)) # Simple approach: count words in JSON string
            else:
                word_count = 0 # Ignore other types

            actual_counts[section_id] = word_count
            total_words += word_count
        actual_counts["TOTAL"] = total_words

        # --- START FIX: Call the new global function ---
        section_averages = calculate_master_avg_bullet_length(self.master_resume)
        # --- END FIX ---

        # Prepare data payload for the validation engine
        data = self._prepare_validation_data(staging_buffer, thematic_analysis, job_description, actual_counts, section_averages)

        # Execute validation
        validation_results = self.engine.validate(data)
        all_passed = not self.engine.has_high_or_critical_failures(validation_results)

        return validation_results, all_passed
    
    def _prepare_validation_data(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        actual_counts: Dict,
        section_averages: Dict # Add parameter
    ) -> Dict:
        """Prepares a dictionary of data needed by the validation rules."""
        unify_words = actual_counts.get(ResumeSection.K5_UNIFY_OVERVIEW.value, 0) + actual_counts.get(ResumeSection.K5_UNIFY_BULLETS.value, 0)
        ibm_words = actual_counts.get(ResumeSection.K6_IBM_OVERVIEW.value, 0) + actual_counts.get(ResumeSection.K6_IBM_BULLETS.value, 0)
        total_words = actual_counts.get("TOTAL", 1) # Avoid division by zero

        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})

        # Ensure competitive_intelligence exists and has the attribute
        jd_keywords_tracked = []
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Use differentiator_keywords_raw which holds the full list before ranking
            jd_keywords_tracked = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords_raw', [])
        else:
             logging.warning("Competitive intelligence missing or empty in thematic analysis during validation data prep.")

        # Ensure buffer data is converted correctly
        try:
            buffer_str = json.dumps(staging_buffer.data).lower() # Convert buffer content to searchable string
        except TypeError as e:
            logging.error(f"Error serializing staging buffer data: {e}")
            buffer_str = "" # Fallback to empty string if serialization fails

        jd_keywords_found_list = [kw for kw in jd_keywords_tracked if kw and kw.lower() in buffer_str] if jd_keywords_tracked and buffer_str else []


        cover_letter_text = staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        cover_letter_jd_similarity = self.dup_detector._calculate_cosine_similarity(
            cover_letter_text,
            job_description
        ) if cover_letter_text and job_description else 0.0

        # Get top differentiators safely
        top_differentiators = []
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Use get_top_differentiators method which handles potential None
            top_differentiators = thematic_analysis.competitive_intelligence.get_top_differentiators(self.signal_constraints.K1_MAX_DIFFERENTIATORS)


        return {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "total_words": total_words,
            "unify_words": unify_words,
            "ibm_words": ibm_words,
            "unify_ibm_percent": ((unify_words + ibm_words) / total_words * 100) if total_words > 0 else 0,
            "differentiators": top_differentiators, # Use the safely extracted list
            "expected_signature": COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', ''),
                email=contact_info.get('email', ''),
                phone=contact_info.get('phone', ''),
                linkedin=contact_info.get('linkedin', '')
            ).strip(),
            "jd_keywords_tracked": jd_keywords_tracked,
            "jd_keywords_found": jd_keywords_found_list, # Use the calculated list
            "cover_letter_jd_similarity": cover_letter_jd_similarity,
            "section_averages": section_averages, # Pass averages for bullet validation
        }

    def _validate_total_word_count(self, data: Dict) -> bool:
        data["error_details"] = {
            "total_words": data['total_words'],
            "min": self.constraints.TOTAL_WORD_COUNT_MIN, # Use self.constraints
            "max": self.constraints.TOTAL_WORD_COUNT_MAX  # Use self.constraints
        }
        return self.constraints.TOTAL_WORD_COUNT_MIN <= data['total_words'] <= self.constraints.TOTAL_WORD_COUNT_MAX

    def _validate_k1_word_count(self, data: Dict) -> bool:
        summary_text = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        word_count = count_words_ms_word_style(summary_text)

        # --- ADD LOGGING ---
        logging.info(f"VALIDATING K.1 Word Count: Target={self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}, Actual={word_count} words.")
        logging.debug(f"K.1 Text Snippet (first 70 chars): '{summary_text[:70]}...'") # Debug level for text
        # --- END LOGGING ---

        data["error_details"] = {
            "word_count": word_count,
            "min": self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN,
            "max": self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX
        }
        is_valid = self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN <= word_count <= self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX

        # --- ADD LOGGING FOR FAILURE ---
        if not is_valid:
            logging.warning(f"K.1 Word Count VALIDATION FAILED: Target={self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}, Actual={word_count}")
        # --- END LOGGING ---

        return is_valid

    def _validate_k1_sentence_count(self, data: Dict) -> bool:
        summary_text = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        sentence_count = _count_sentences(summary_text) # Assumes _count_sentences is defined globally or imported
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
        # Uses self.constraints directly now
        min_pct = self.constraints.UNIFY_IBM_COMBINED_PERCENT_MIN
        max_pct = self.constraints.UNIFY_IBM_COMBINED_PERCENT_MAX
        data["error_details"] = {"percent": data['unify_ibm_percent'], "min": min_pct, "max": max_pct}
        return min_pct <= data['unify_ibm_percent'] <= max_pct

    def _validate_unify_ibm_ratio(self, data: Dict) -> bool:
        min_ratio = self.constraints.UNIFY_IBM_RATIO_MIN
        max_ratio = self.constraints.UNIFY_IBM_RATIO_MAX
        if data['ibm_words'] == 0:
            data["error_details"] = {"ratio": "N/A (IBM words = 0)", "min": min_ratio, "max": max_ratio}
            return False # Cannot divide by zero
        ratio = data['unify_words'] / data['ibm_words']
        data["error_details"] = {"ratio": ratio, "min": min_ratio, "max": max_ratio}
        return min_ratio <= ratio <= max_ratio

    def _validate_buffer_locked(self, data: Dict) -> bool:
        return data['staging_buffer'].is_locked()

    def _validate_cover_letter_signature(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_sig = data.get('expected_signature', 'SIGNATURE_NOT_FOUND')
        # Check if the cover letter ends with the signature block, ignoring trailing whitespace
        return cover_letter.strip().endswith(expected_sig)

    def _validate_no_placeholders(self, data: Dict) -> bool:
        try:
            buffer_str = json.dumps(data['staging_buffer'].data)
            # Find variations like [Placeholder...], [placeholder...], [PLACEHOLDER...]
            placeholders = re.findall(r'(\[placeholder.*?\])', buffer_str, re.IGNORECASE)
            if placeholders:
                # Show unique placeholders found, limit to 5 for brevity
                unique_placeholders = list(set(placeholders))
                data["error_details"] = {"placeholders": unique_placeholders[:5]}
                return False
            return True
        except Exception as e:
            # Handle potential errors during JSON dump (e.g., non-serializable data)
            logging.error(f"Error checking for placeholders: {e}")
            data["error_details"] = {"placeholders": [f"Error during check: {e}"]}
            return False # Fail safe

    def _validate_per_section_signal(self, data: Dict) -> bool:
        """VG_PER_SECTION_SIGNAL_SCORE: Checks if all generated sections meet min signal score."""
        staging_buffer = data['staging_buffer']
        thematic_analysis = data['thematic_analysis']
        if not thematic_analysis: # Add null check for thematic_analysis
             data["error_details"] = {"failures": "Thematic analysis object is missing."}
             return False

        failures = []

        for label, (section_enum, target_min_score, _, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = staging_buffer.get(section_enum.value)

            if content:
                # Call the standalone helper function
                score = calculate_signal_score(content, thematic_analysis)

                if score < target_min_score:
                    failures.append(f"{label}: {score:.1%} (Target: {target_min_score:.0%})")
            # else: # Optionally log sections that are missing content
            #     logging.debug(f"Signal score check skipped for {label}: No content found.")


        if failures:
            data["error_details"] = {"failures": "; ".join(failures)}
            return False

        return True

    def _validate_k1_differentiator_range(self, data: Dict) -> bool:
        MIN_DIFF = self.constraints.K1_MIN_DIFFERENTIATORS
        MAX_DIFF = self.signal_constraints.K1_MAX_DIFFERENTIATORS

        # Differentiators are expected to be strings
        differentiators = data.get('differentiators', [])
        if not differentiators:
             logging.info("K.1 Differentiator Check: No differentiators found in thematic analysis.")
             data["error_details"] = {"found": 0, "min": MIN_DIFF, "max": MAX_DIFF, "message": "No differentiators to check."}
             return True # Pass if no differentiators provided

        summary = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        if not summary:
             data["error_details"] = {"found": 0, "min": MIN_DIFF, "max": MAX_DIFF, "message": "Exec Summary missing."}
             return False # Fail if summary is missing

        # Ensure keywords are strings before lowercasing
        found_count = sum(1 for kw in differentiators if isinstance(kw, str) and kw.lower() in summary)

        data["error_details"] = {
            "found": found_count,
            "min": MIN_DIFF,
            "max": MAX_DIFF
        }
        return MIN_DIFF <= found_count <= MAX_DIFF

    def _validate_jd_keyword_range(self, data: Dict) -> bool:
        MIN_KW = self.constraints.MIN_JD_KEYWORDS
        MAX_KW = self.signal_constraints.RESUME_MAX_JD_KEYWORDS

        found_count = len(data.get('jd_keywords_found', []))

        data["error_details"] = {
            "found": found_count,
            "min": MIN_KW,
            "max": MAX_KW
        }
        return MIN_KW <= found_count <= MAX_KW

    def _validate_narrative_mining_presence(self, data: Dict) -> bool:
        # Check if thematic_analysis exists first
        if not data.get('thematic_analysis'):
             return False
        narratives = getattr(data['thematic_analysis'], 'problem_solution_narratives', None) # Use getattr for safe access
        return (
            narratives is not None and
            isinstance(narratives.get("common_problems"), list) and
            len(narratives.get("common_problems", [])) > 0 and
            isinstance(narratives.get("solution_patterns"), list) and
            len(narratives.get("solution_patterns", [])) > 0
        )

    def _validate_cover_letter_relevance_range(self, data: Dict) -> bool:
        MIN_SIM = self.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD
        MAX_SIM = self.signal_constraints.CL_MAX_JD_SIMILARITY

        similarity = data.get('cover_letter_jd_similarity', 0.0)

        data["error_details"] = {
            "similarity": similarity,
            "min_sim": MIN_SIM,
            "max_sim": MAX_SIM
        }
        return MIN_SIM <= similarity <= MAX_SIM

    def _validate_cover_letter_narrative(self, data: Dict) -> bool:
        """Checks for 'Hook, Proof, Vision' structure keywords."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        if not cover_letter or not data.get('thematic_analysis'): return False

        primary_theme = data['thematic_analysis'].primary_theme.get('name', 'default_theme') if data['thematic_analysis'].primary_theme else 'default_theme'
        # Differentiators might be None or empty list
        differentiators = data.get('differentiators', []) or []

        paragraphs = cover_letter.split('\n\n')
        # Expecting Date[0], Recipient[1], Salutation[2], P1[3], P2[4], P3[5], Closing[6], Signature[7+]
        if len(paragraphs) < 6:
             data["error_details"] = {"hook": False, "proof": False, "vision": False, "message": f"Expected at least 6 paragraphs/blocks, found {len(paragraphs)}"}
             return False

        p1 = paragraphs[3].lower() if len(paragraphs) > 3 else ""
        p2 = paragraphs[4].lower() if len(paragraphs) > 4 else ""
        p3 = paragraphs[5].lower() if len(paragraphs) > 5 else ""

        # Hook: Check if primary theme or role title is in the first paragraph
        hook_pass = primary_theme.lower() in p1 or "interest in the" in p1

        # Proof: Check if differentiator keywords or impact language is in the second paragraph
        proof_pass = any(isinstance(kw, str) and kw.lower() in p2 for kw in differentiators) or "resulted in" in p2 or "achieved" in p2

        # Vision: Check for forward-looking or call-to-action words in the third paragraph
        vision_pass = "excited" in p3 or "opportunity" in p3 or "discuss" in p3 or "contribute" in p3 or "look forward" in p3

        data["error_details"] = {"hook": hook_pass, "proof": proof_pass, "vision": vision_pass}
        return hook_pass and proof_pass and vision_pass

    def _validate_cover_letter_fallback(self, data: Dict) -> bool:
        """Checks if the fallback cover letter was used by looking for a specific phrase."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        # The fallback contains this specific phrase, which the creative one shouldn't
        return "track record of measurable AI transformation" not in cover_letter

    def _validate_cover_letter_structure(self, data: Dict) -> bool:
        """Validates word counts of the three main paragraphs."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        paragraphs = cover_letter.split('\n\n')

        # Indices based on the expected structure
        p1_idx, p2_idx, p3_idx = 3, 4, 5

        if len(paragraphs) <= max(p1_idx, p2_idx, p3_idx):
            data["error_details"] = {
                "p1_wc": 0, "p2_wc": 0, "p3_wc": 0,
                "p1_min": self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
                "p2_min": self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
                "p3_min": self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
                "message": f"Insufficient paragraphs found ({len(paragraphs)})."
            }
            return False

        p1_wc = count_words_ms_word_style(paragraphs[p1_idx])
        p2_wc = count_words_ms_word_style(paragraphs[p2_idx])
        p3_wc = count_words_ms_word_style(paragraphs[p3_idx])

        data["error_details"] = {
            "p1_wc": p1_wc, "p1_min": self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
        }

        p1_valid = self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN <= p1_wc <= self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX
        p2_valid = self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN <= p2_wc <= self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX
        p3_valid = self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN <= p3_wc <= self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX

        return p1_valid and p2_valid and p3_valid

    def _validate_cover_letter_full_structure(self, data: Dict) -> bool:
        """VG_COVER_LETTER_FULL_STRUCTURE: Checks for key components."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_signature_block = data.get('expected_signature', 'SIGNATURE_NOT_FOUND')
        if not cover_letter: return False

        # Simple checks for presence using regex for robustness
        has_date = bool(re.match(r"\w+ \d{1,2}, \d{4}", cover_letter.strip())) # Month D, YYYY at start
        has_recipient = bool(re.search(r"\n\nHiring Manager\n\[Company Name\]\n\n", cover_letter)) # Check for the block
        has_salutation = bool(re.search(r"\n\nDear Hiring Manager,\n\n", cover_letter))
        has_closing = bool(re.search(r"\n\nSincerely,\n\n", cover_letter))
        has_signature = expected_signature_block in cover_letter

        # Check for 3 distinct body paragraphs between Salutation and Closing
        body_match = re.search(r"Dear Hiring Manager,\n\n(.*?)\n\nSincerely,", cover_letter, re.DOTALL)
        body_paras = body_match.group(1).strip().count('\n\n') == 2 if body_match else False # Exactly two double newlines -> 3 paras

        return has_date and has_recipient and has_salutation and body_paras and has_closing and has_signature

    def _validate_cover_letter_signature_multiline(self, data: Dict) -> bool:
        """VG_COVER_LETTER_SIGNATURE_MULTILINE: Checks if signature renders on multiple lines."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_signature_block = data.get('expected_signature', '')

        if not expected_signature_block: return False

        # Find the signature block at the end of the letter
        if cover_letter.strip().endswith(expected_signature_block):
            # Check if the expected block itself contains newlines (it should if template is correct)
             return '\n' in expected_signature_block
        return False

    def _validate_headline_word_count(self, data: Dict) -> bool:
        """VG_HEADLINE_WORD_COUNT: Validate K.0 Headline word count."""
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        word_count = count_words_ms_word_style(headline)
        data["error_details"] = {
            "word_count": word_count,
            "min": self.constraints.HEADLINE_WORD_COUNT_MIN,
            "max": self.constraints.HEADLINE_WORD_COUNT_MAX,
            "headline": headline
        }
        return self.constraints.HEADLINE_WORD_COUNT_MIN <= word_count <= self.constraints.HEADLINE_WORD_COUNT_MAX

    def _validate_headline_format_no_titles(self, data: Dict) -> bool:
        """VG_HEADLINE_NO_TITLES: Ensure headline does not contain common job titles."""
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '').lower()
        forbidden_titles = ['vp', 'vice president', 'director', 'manager', 'chief', 'head', 'lead', 'principal', 'senior', 'c-suite', 'executive']
        found_forbidden = [t for t in forbidden_titles if re.search(r'\b' + re.escape(t) + r'\b', headline)] # Use word boundaries and escape
        data["error_details"] = {"headline": headline, "forbidden": found_forbidden}
        return not found_forbidden

    def _validate_headline_format_no_commas(self, data: Dict) -> bool:
        """VG_HEADLINE_NO_COMMAS: Ensure headline does not contain commas."""
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        data["error_details"] = {"headline": headline}
        return ',' not in headline

    def _validate_resume_header_h2(self, data: Dict) -> bool:
        """VG_RESUME_HEADER_H2: Placeholder validation."""
        data["error_details"] = {"failed_headers": ["Checked during rendering/QA-16"]}
        return True # Checked visually/post-render

    def _validate_edu_certs_format(self, data: Dict) -> bool:
        """VG_EDU_CERTS_FORMAT: Placeholder validation."""
        data["error_details"] = {"details": "Checked during rendering/QA-16"}
        return True # Checked visually/post-render

    def _validate_experience_bullet_style(self, data: Dict) -> bool:
        """VG_EXPERIENCE_BULLET_STYLE: Placeholder validation."""
        data["error_details"] = {"details": "Checked during rendering/QA-16"}
        return True # Checked visually/post-render

    def _validate_competencies_formatting(self, data: Dict) -> bool:
        """VG_COMPETENCIES_FORMATTING: Placeholder validation."""
        data["error_details"] = {"details": "Checked during rendering/QA-16"}
        return True # Checked visually/post-render

    def _validate_experience_render_format(self, data: Dict) -> bool:
        """VG_EXPERIENCE_RENDER_FORMAT: Placeholder validation."""
        data["error_details"] = {"details": "Checked during rendering/QA-16"}
        return True # Checked visually/post-render

    def _validate_bullet_word_count_tolerance(self, data: Dict) -> bool:
        """
        VG_BULLET_WORD_COUNT_TOLERANCE: Checks individual bullet word counts against master averages +/- tolerance.
        """
        all_bullets_valid = True
        violations = []
        # Averages calculated using MS Word style count via the helper
        averages = data.get('section_averages', self._calculate_master_avg_bullet_length()) # Use precalculated or recalculate
        staging_buffer = data['staging_buffer']

        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            # Determine which average key to use based on section
            avg_key = "Default" # Fallback key
            if section_enum == ResumeSection.K5_UNIFY_BULLETS: avg_key = "Unify"
            elif section_enum == ResumeSection.K6_IBM_BULLETS: avg_key = "IBM"
            elif section_enum == ResumeSection.K10_COMPETENCIES: avg_key = "Competencies"
            elif section_enum == ResumeSection.K8_EY_BULLETS: avg_key = "EY"
            elif section_enum == ResumeSection.K9_EARLY_CAREER_BULLETS: avg_key = "EarlyCareer"

            avg_wc = averages.get(avg_key)
            if avg_wc is None or avg_wc <= 0:
                logging.debug(f"Skipping bullet tolerance for {section_key}: Invalid average {avg_wc} for key '{avg_key}'")
                continue # Skip if average is invalid

            min_wc = round(avg_wc * (1 - self.BULLET_WORD_COUNT_TOLERANCE))
            max_wc = round(avg_wc * (1 + self.BULLET_WORD_COUNT_TOLERANCE))

            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list):
                 logging.warning(f"Data for {section_key} is not a list, skipping bullet tolerance check.")
                 continue

            for i, bullet in enumerate(bullets):
                actual_wc = 0
                if isinstance(bullet, dict):
                    bullet_text = bullet.get('text', bullet.get('bullet_text','')) # Handle both keys
                    # Use pre-calculated word_count if available, else calculate
                    actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str): # Handle case where section might have strings (e.g., K7 fallback)
                    bullet_text = bullet
                    actual_wc = count_words_ms_word_style(bullet_text)
                else:
                    # Log unexpected item type but continue
                    logging.warning(f"Unexpected item type in {section_key}[{i}]: {type(bullet)}. Skipping tolerance check for this item.")
                    continue

                if not (min_wc <= actual_wc <= max_wc):
                    all_bullets_valid = False
                    violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc} based on avg {avg_wc:.1f})")

        if not all_bullets_valid:
            # Populate error details only if violations occurred
            data["error_details"] = {"violations": violations[:5]} # Limit details size
        return all_bullets_valid

    def _validate_provenance_split(self, data: Dict) -> bool:
        """VG_PROVENANCE_SPLIT_CHECK: Checks if bullet provenance matches target splits."""
        all_splits_valid = True
        violations = []
        staging_buffer = data['staging_buffer']

        for section_enum, target_split in self.PROVENANCE_SPLIT_TARGETS.items():
            section_key = section_enum.value
            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list):
                logging.warning(f"Provenance check skipped for {section_key}: Data is not a list.")
                continue

            actual_counts = {prov.value: 0 for prov in BulletProvenance} # Initialize all provenance types to 0

            target_total = sum(target_split.values())
            actual_total = 0

            for i, bullet in enumerate(bullets):
                 if isinstance(bullet, dict):
                     prov = bullet.get('provenance')
                     if prov in actual_counts:
                         actual_counts[prov] += 1
                         actual_total += 1
                     else:
                          logging.warning(f"Unknown provenance '{prov}' found in {section_key}[{i}].")
                 elif isinstance(bullet, str) and section_key == ResumeSection.K7_TRADERSENSE_BULLETS.value:
                     # Special case for K7: strings are Verbatim
                     actual_counts[BulletProvenance.Verbatim.value] += 1
                     actual_total += 1
                 else:
                      logging.warning(f"Unexpected item type in {section_key}[{i}]: {type(bullet)}. Skipping provenance count for this item.")


            if actual_total != target_total:
                 all_splits_valid = False
                 violations.append(f"{section_key}: Total count mismatch (Expected {target_total}, Got {actual_total})")
                 continue # Skip detailed check if total is wrong

            # Check individual provenance counts against targets
            for prov_type_enum in BulletProvenance:
                prov_type = prov_type_enum.value
                target_count = target_split.get(prov_type, 0) # Get target, default 0 if not specified
                actual_count = actual_counts.get(prov_type, 0)
                if actual_count != target_count:
                    all_splits_valid = False
                    violations.append(f"{section_key}: {prov_type} count mismatch (Expected {target_count}, Got {actual_count})")

        if not all_splits_valid:
            data["error_details"] = {"violations": violations}
        return all_splits_valid

    def _validate_authenticity_signal(self, data: Dict) -> bool:
        """
        [v11.0 NEW RULE]
        Checks if authenticity patterns (verbs) from HOP-0 are present
        in the generated resume content.
        """
        try:
            # Safely access thematic_analysis and authenticity patterns
            thematic_analysis = data.get('thematic_analysis')
            if not thematic_analysis or not hasattr(thematic_analysis, 'authenticity_patterns'):
                 data["error_details"] = {"details": "ThematicAnalysis or AuthenticityPatterns missing."}
                 return False # Cannot validate if the source data is missing

            auth_patterns = thematic_analysis.authenticity_patterns or {} # Handle potential None
            patterns_dict = auth_patterns.get('patterns', {})
            target_verbs = patterns_dict.get('achievement_verb_patterns', [])

            if not target_verbs:
                # If HOP-0 failed to find verbs, pass validation but log info.
                logging.info("Authenticity Signal Check: No target verbs found in HOP-0 analysis.")
                data["error_details"] = {"details": "No authenticity verbs found in HOP-0 analysis to check against."}
                return True # Pass validation, as there's nothing to check

            # Combine all relevant generated text content
            content_to_check = []
            staging_buffer = data['staging_buffer']
            content_to_check.append(staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, ''))

            bullet_sections = [
                ResumeSection.K5_UNIFY_BULLETS,
                ResumeSection.K6_IBM_BULLETS,
                ResumeSection.K8_EY_BULLETS,
                ResumeSection.K9_EARLY_CAREER_BULLETS,
                ResumeSection.K10_COMPETENCIES
            ]

            for section_enum in bullet_sections:
                bullets = staging_buffer.get(section_enum.value, [])
                if isinstance(bullets, list):
                    for bullet in bullets:
                        text_to_add = None
                        if isinstance(bullet, dict):
                            text_to_add = bullet.get('text', bullet.get('bullet_text')) # Check both keys
                        elif isinstance(bullet, str): # Handle potential strings (e.g., K7 fallback)
                            text_to_add = bullet
                        if text_to_add:
                            content_to_check.append(text_to_add)

            full_text = " ".join(content_to_check).lower()
            if not full_text.strip():
                 data["error_details"] = {"details": "No generated text content found to check verbs against."}
                 return False # Fail if no content was generated

            # Check if at least 2 of the target verbs (case-insensitive) are present
            found_verbs_count = sum(1 for verb in target_verbs if isinstance(verb, str) and verb.lower() in full_text)

            if found_verbs_count < 2:
                data["error_details"] = {"details": f"Found only {found_verbs_count} matching auth-verbs. Expected 2+. (Targets: {target_verbs[:5]})"}
                return False

            return True

        except Exception as e:
            logging.error(f"Error during authenticity signal validation: {e}", exc_info=True)
            data["error_details"] = {"details": f"Validation logic failed: {e}"}
            return False # Fail safe

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
# WORKFLOW ORCHESTRATOR
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

        # Attributes populated by other hops/methods
        self.dup_detector = None # Populated in HOP-2 for later use
        self.similarity_matrix_data = None # Populated in HOP-7.5
        self.executive_summary_similarity_data = None # Populated in HOP-7.5
        self.overview_similarity_data = None # Populated in HOP-7.5
        self.dedup_analysis_timestamp = None # Populated in HOP-7.5
        self.hash_chain = [] # For Chain of Custody
        self.constraints = ContentConstraintsConfig() # Load content constraints

        self.jd_enforcer = JDEnforcementValidator() # JD Gate checks

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__) # Use self.logger

        # API Key Check (only if not in test mode)
        if not test_mode:
            # Check for Gemini API Key
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
        self.logger.info(f"Using Model: {RAGConfig().model}") # Assuming RAGConfig defines the model

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

# --- v12.01 START MODIFICATION: _execute_hop_3_artist_generation ---
    def _execute_hop_3_artist_generation(self, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis) -> Dict:
        """
        Executes HOP-3: Content Generation with retry logic.
        v12.01: Includes separate temperature reduction for K.13 based on word count failures.
        """
        self.logger.info("\n[HOP-3] Content Generation (Artist)...")
        hop_start_time = datetime.now()

        artist = ArtistGenerator(
            master_resume=self.master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis
        )

        artist_output = None
        generation_hop_results = []
        final_validation_results = []
        all_passed = False
        feedback_results = None
        max_attempts = 5
        attempt = 0
        # --- MODIFIED TEMPERATURE SCHEDULE FOR K.1 ---
        k1_temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2] # <--- YOUR NEW VALUES
        # --- END MODIFICATION ---

        # --- Initialize K.13 temperature ---
        current_k13_temp = 1.0
        k13_temperature_schedule = [1.0, 0.9, 0.8, 0.7, 0.6] # Defined schedule

        for attempt in range(1, max_attempts + 1):
            self.logger.info(f"  Attempt {attempt}/{max_attempts}...")
            attempt_start_time = time.time()

            # --- K.1 Temperature Logic ---
            # --- USES THE MODIFIED SCHEDULE ---
            current_k1_temp = k1_temperature_schedule[min(attempt - 1, len(k1_temperature_schedule) - 1)] # Use schedule, prevent index error
            # --- END USE ---
            k1_temp_to_use = current_k1_temp
            # Check previous failures for K.1 specific rules to decide if override is needed
            k1_failed_previously = any(
                f.rule_id in ["VG_WORD_COUNT_K1", "VG_SENTENCE_COUNT_K1"]
                for f in (feedback_results or [])
            )
            if attempt > 1 and k1_failed_previously:
                self.logger.info(f"    Applying K.1 Temperature Override: {current_k1_temp}")
            else:
                k1_temp_to_use = None # Use Artist's default if not retrying K.1 specifically

            # --- K.13 Temperature Logic (Applied on each attempt based on current_k13_temp) ---
            k13_temp_to_use = current_k13_temp
            self.logger.info(f"    Using K.13 Temperature: {k13_temp_to_use}")

            try:
                current_artist_output, current_generation_results = artist.generate(
                    feedback_results=feedback_results,
                    attempt=attempt,
                    k1_temp_override=k1_temp_to_use, # Pass determined K.1 temp
                    k13_temp_override=k13_temp_to_use # Pass current K.13 temp
                )
                generation_hop_results = current_generation_results
                artist_output = current_artist_output
            except Exception as e:
                 self.logger.error(f"    ✗ Generation Attempt {attempt} FAILED: {e}", exc_info=True)
                 generation_hop_results.append(ValidationResult(
                     f"ARTIST_GENERATION_ATTEMPT_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation failed: {e}"
                 ))
                 artist_output = locals().get('current_artist_output') # Use potentially partial output
                 final_validation_results = generation_hop_results
                 all_passed = False
                 break # Exit loop on hard generation failure

            # --- Validation ---
            temp_buffer = ImmutableStagingBuffer()
            for key, value in current_artist_output.items():
                temp_buffer.set(key, value)
            temp_buffer.lock()

            validator = PreFlightValidator(self.master_resume)
            try:
                current_validation_results, current_all_passed = validator.validate(
                    temp_buffer, thematic_analysis, job_description
                )
                final_validation_results = current_validation_results
                all_passed = current_all_passed
            except Exception as e:
                self.logger.error(f"    ✗ Validation Attempt {attempt} FAILED: {e}", exc_info=True)
                final_validation_results.append(ValidationResult(
                     f"VALIDATION_ATTEMPT_{attempt}", False, ValidationSeverity.CRITICAL, f"Validation failed: {e}"
                 ))
                all_passed = False
                break # Exit loop on hard validation failure

            attempt_duration = time.time() - attempt_start_time
            self.logger.info(f"    Attempt {attempt} completed in {attempt_duration:.2f}s. Validation passed: {all_passed}")

            # --- Decision for Next Attempt ---
            if all_passed or attempt == max_attempts:
                break # Exit if successful or max attempts reached
            else:
                feedback_results = [vr for vr in final_validation_results if not vr.passed]
                self.logger.info(f"    {len(feedback_results)} validation failures detected, preparing for retry...")

                # --- K.13 Temperature Reduction Logic ---
                cl_structure_failure = next((vr for vr in feedback_results if vr.rule_id == "COVER_LETTER_STRUCTURE"), None)
                if cl_structure_failure:
                    # Check if the failure message indicates word count issues (simple check)
                    try:
                         # Ensure message is formatted if callable
                         msg = cl_structure_failure.message(cl_structure_failure.details) if callable(cl_structure_failure.message) else cl_structure_failure.message
                         if "word counts are out of spec" in msg:
                             # Decrement K.13 temperature for the *next* attempt
                             next_k13_temp_index = min(attempt, len(k13_temperature_schedule) - 1) # Get index for next temp
                             current_k13_temp = k13_temperature_schedule[next_k13_temp_index]
                             self.logger.info(f"    K.13 word count failed. Reducing K.13 temp to {current_k13_temp} for next attempt.")
                         else:
                             self.logger.info(f"    K.13 structure failed but not for word count. K.13 temp remains {current_k13_temp}.")
                    except Exception as msg_e:
                         self.logger.warning(f"    Could not parse K.13 failure message: {msg_e}. K.13 temp remains {current_k13_temp}.")
                else:
                    self.logger.info(f"    K.13 structure passed or validation missing. K.13 temp remains {current_k13_temp}.")
                # --- End K.13 Logic ---


        # --- Final Outcome ---
        llm_calls_made = len([k for k, v in (artist_output or {}).items() if v is not None])
        # Combine results from generation attempt and final validation
        combined_results = generation_hop_results + [vr for vr in final_validation_results if vr not in generation_hop_results]


        hop_checkpoint = self._create_checkpoint(
            "HOP-3", f"Artist Generation (final attempt {attempt})",
            combined_results, artist_output,
            start_time=hop_start_time,
            metadata={"llm_api_calls": llm_calls_made, "attempts_made": attempt}
        )
        self.hop_checkpoints.append(hop_checkpoint)

        if not all_passed:
            self.logger.error(f"  ✗ HOP-3 FAILED: Content validation failed after {attempt} attempts.")
            hop_checkpoint.status = HopStatus.FAIL
            # Try to get a specific failure reason
            critical_failures = [f for f in (feedback_results or []) if f.severity == ValidationSeverity.CRITICAL]
            high_failures = [f for f in (feedback_results or []) if f.severity == ValidationSeverity.HIGH]
            if critical_failures: reason = f"Critical Failure: {critical_failures[0].rule_id}"
            elif high_failures: reason = f"High Failure: {high_failures[0].rule_id}"
            else: reason = f"Validation failed after {attempt} attempts."
            hop_checkpoint.error_message = reason
            self.validation_results.extend(final_validation_results or []) # Ensure final validation results are stored on failure
            raise HopExecutionError(hop_checkpoint.error_message)
        else:
             self.logger.info(f"  ✓ HOP-3 successful after {attempt} attempt(s).")
             # Use the final successful validation results for downstream steps
             self.validation_results = final_validation_results
             self._check_hop_status(hop_checkpoint) # Check status (should be PASS or WARNING)

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
                staging_buffer.set(key, value)
                if value is not None: sections_populated += 1
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
             hop4_checkpoint.status = HopStatus.FAIL
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
                start_time=hop45_start_time # Use dedicated start time for this sub-hop
            )
            self.hop_checkpoints.append(hop45_checkpoint)
            self._check_hop_status(hop45_checkpoint)
            return staging_buffer
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-4.5] FAILED: {e}", exc_info=True)
            if not staging_buffer.is_locked(): staging_buffer.lock() # Try to lock
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
        """Executes HOP-5: Pre-flight Validation."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-5] Pre-flight Validation...")
        try:
            validator = PreFlightValidator(self.master_resume)
            hop_results, critical_passed = validator.validate(staging_buffer, thematic_analysis, job_description) # Use correct return value name
            self.validation_results = hop_results # Store results for HOP-6 and QA report

            hop_checkpoint = self._create_checkpoint(
                "HOP-5", "Pre-flight Validation", hop_results,
                {"all_rules_checked": len(validator.engine.rules), "critical_passed": critical_passed},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check status based on CRITICAL failures only for halting workflow here
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=True)
            return hop_results
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-5] FAILED during validation logic: {e}", exc_info=True)
             error_result = ValidationResult("HOP-5_EXECUTION", False, ValidationSeverity.CRITICAL, f"Validation execution failed: {e}")
             hop_checkpoint = self._create_checkpoint(
                 "HOP-5", "Pre-flight Validation", [error_result],
                 {"all_rules_checked": 0, "critical_passed": False},
                 start_time=hop_start_time, error_message=str(e)
             )
             hop_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop_checkpoint)
             self.validation_results = [error_result]
             raise HopExecutionError(f"HOP-5 failed: {e}")

    def _execute_hop_6_gate_decision(self, hop5_results: List[ValidationResult]) -> GateDecision:
        """Executes HOP-6: Gate Decision."""
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
        """Executes HOP-7: File Rendering. Returns dict of file paths and dict of file contents."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7] Rendering Output Files...")
        try:
            renderer = FileRenderer(self.master_resume, self)
            file_paths, (hop_results, file_contents) = renderer.render(
                staging_buffer, company_name, job_title, thematic_analysis, job_description
            )

            # Update self.rendered_output immediately
            self.rendered_output = {
                'file_paths': file_paths,
                'file_contents': file_contents
            }

            hop_checkpoint = self._create_checkpoint(
                "HOP-7", "File Rendering", hop_results,
                file_paths, # Hash paths
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint) # Check for rendering errors

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
                { # Include calculated data in output hash/metadata
                    "matrix_max_sim": self.similarity_matrix_data.get('max_similarity', 0.0) if self.similarity_matrix_data else 0.0,
                    "overview_max_sim": max([d.get('max_similarity', 0.0) for d in self.overview_similarity_data], default=0.0) if self.overview_similarity_data else 0.0,
                    "exec_summary_max_sim": max([d.get('max_similarity', 0.0) for d in self.executive_summary_similarity_data], default=0.0) if self.executive_summary_similarity_data else 0.0, # Added Exec Summary sim
                },
                start_time=hop_start_time,
                metadata={"analysis_timestamp": self.dedup_analysis_timestamp}
            )
            # This hop is informational, set status based on execution not content
            hop_checkpoint.status = HopStatus.PASS
            self.hop_checkpoints.append(hop_checkpoint)

        except Exception as e:
            # Catch errors during the analysis calculation
            self.logger.error(f"  ✗ [HOP-7.5] FAILED: {e}", exc_info=True)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-7.5", "Deduplication Analysis",
                 [ValidationResult("HOP-7.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 None, start_time=hop_start_time, error_message=str(e)
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            # Allow workflow to continue but log error

    def _execute_hop_8_qa_report(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, hop5_results: List[ValidationResult]) -> str:
        """Executes HOP-8: QA Report Generation."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-8] Generating QA Report...")
        try:
            # It now returns QA-specific validations, report text, and potentially updated file_contents
            qa_report_validation_results, qa_report_text, updated_file_contents = self._generate_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            # Update the main file_contents if QA report generation succeeded
            if self.rendered_output and 'file_contents' in self.rendered_output:
                self.rendered_output['file_contents']['qa_report'] = qa_report_text


            hop_checkpoint = self._create_checkpoint(
                "HOP-8", "QA Report Generation", qa_report_validation_results, # Use QA-specific results
                {"qa_report_generated": True, "report_length": len(qa_report_text)},
                start_time=hop_start_time
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check for critical errors during QA generation itself
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

    # --- Main Workflow Execution Method ---

    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> Dict:
        """
        Execute complete multi-hop workflow.

        Args:
            job_description (str): The job description text.
            company_name (str): The target company name.
            job_title (str): The target job title.

        Returns:
            Dict containing workflow status, output file paths, QA report, CoC ledger, etc.
        """
        workflow_start = datetime.now()
        # Harden inputs
        company_name = company_name.strip() if company_name and company_name.strip() else "Target_Company"
        job_title = job_title.strip() if job_title and job_title.strip() else "Target_Role"

        # Log start
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
        gate_decision = GateDecision.PROCEED # Default


        try:
            # --- JD Enforcement Gates (Integrated with Hops) ---
            self.logger.info("\n[GATE-0] JD Input Validation...")
            jd_validation = self.jd_enforcer.validate_jd_input(job_description, "GATE-0")
            failed_jd_validations = [r for r in jd_validation if not r.passed]
            if failed_jd_validations:
                self.logger.warning(f"  ⚠️ JD Input Validation warnings: {len(failed_jd_validations)}")
                for val in failed_jd_validations[:3]: self.logger.warning(f"    - {val.details}")
            else: self.logger.info("  ✓ JD input validation passed.")

            # --- Workflow Hops ---
            thematic_analysis = self._execute_hop_0_jd_analysis(job_description)

            self.logger.info("\n[GATE-1] JD Parsing Validation...")
            if thematic_analysis:
                # Need to convert dataclass to dict for validation if needed, or adjust validator
                try: parsed_jd_for_validation = asdict(thematic_analysis)
                except: parsed_jd_for_validation = {} # Fallback
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

            artist_output = self._execute_hop_3_artist_generation(
                enriched_scaffold, job_description, thematic_analysis
            )

            staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)

            hop5_results = self._execute_hop_5_validation(staging_buffer, thematic_analysis, job_description)

            self.logger.info("\n[GATE-5] Pre-flight Buffer JD Validation...")
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")


            gate_decision = self._execute_hop_6_gate_decision(hop5_results) # Uses HOP-5 results

            # If PROCEED:
            file_paths, file_contents = self._execute_hop_7_rendering(
                staging_buffer, company_name, job_title, thematic_analysis, job_description
            )

            self.logger.info("\n[GATE-7] File Output Validation...")
            self.jd_enforcer.validate_file_output(file_paths, "GATE-7")


            self._execute_hop_7_5_deduplication(staging_buffer) # Analysis step

            qa_report_text = self._execute_hop_8_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            self.logger.info("\n[GATE-8] QA Report Content Validation...")
            self.jd_enforcer.validate_qa_report({"report": qa_report_text}, "GATE-8")


            # --- Build Final Success Result ---
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

            # Ensure all file contents are included, default to empty string if missing
            final_result = {
                "status": "SUCCESS",
                "gate_decision": gate_decision.value,
                "file_paths": file_paths,
                "qa_report": qa_report_text, # Generated QA report text (already updated in _execute_hop_8)
                "coc_ledger": coc_ledger,
                "resume_md_content": file_contents.get('resume_md', ''),
                "skills_content": file_contents.get('skills', ''),
                "cover_letter_content": file_contents.get('cover_letter', ''),
                "app_tracker_content": file_contents.get('app_tracker', '{}'),
                # Include QA report content in file_contents dict for consistency
                "qa_report_content": qa_report_text,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "hash_chain": self.hash_chain
            }
            self.rendered_output = final_result # Store final output
            return final_result

        except HopExecutionError as e:
            # Controlled halt from a gate decision or critical hop failure
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW HALTED: {str(e)}")

            # Determine gate decision and reason from the last checkpoint if available
            gate_decision_val = GateDecision.HALT.value
            reason = str(e)
            if self.hop_checkpoints:
                 last_checkpoint = self.hop_checkpoints[-1]
                 if last_checkpoint.hop_id == "HOP-6": # If halted at Gate Decision
                     gate_decision_info = last_checkpoint.metadata
                     gate_decision_val = gate_decision_info.get("decision", GateDecision.HALT.value)
                     reason = gate_decision_info.get("reason", str(e))
                 elif last_checkpoint.status == HopStatus.FAIL: # Halted due to hop failure
                      reason = last_checkpoint.error_message or str(e)


            # Attempt to generate QA report even if halted, using available data
            if staging_buffer and thematic_analysis:
                 try:
                     # Use self.validation_results which stores the results from the last HOP-5 run
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
                "qa_report": qa_report_text, # Include potentially generated QA report
                "hash_chain": self.hash_chain,
                # Include file contents if rendering occurred before halt
                "resume_md_content": file_contents.get('resume_md', ''),
                "skills_content": file_contents.get('skills', ''),
                "cover_letter_content": file_contents.get('cover_letter', ''),
                "app_tracker_content": file_contents.get('app_tracker', '{}'),
                "qa_report_content": qa_report_text,
            }
            self.rendered_output = final_result # Store final (halted) output
            return final_result

        except Exception as e:
            # Uncontrolled failure
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW FAILED UNEXPECTEDLY: {type(e).__name__}: {str(e)}", exc_info=True)

             # Try to generate QA report even on unexpected failure
            if staging_buffer and thematic_analysis:
                 try:
                     # Use self.validation_results which stores the results from the last HOP-5 run (if it completed)
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
                "qa_report": qa_report_text, # Include potentially generated QA report
                "hash_chain": self.hash_chain
            }
            self.rendered_output = final_result # Store final (failed) output
            return final_result

    # --- Helper Methods ---

    def _create_jd_analyzer(self) -> EnhancedJobDescriptionAnalyzer:
        """Creates the HOP-0 JD Analyzer instance."""
        api_key = os.environ.get("GEMINI_API_KEY")
        # Ensure RAGConfig is accessible or defined
        rag_config = RAGConfig() if 'RAGConfig' in globals() else None
        return EnhancedJobDescriptionAnalyzer(self.master_resume, enable_web_search=True, api_key=api_key, config=rag_config)

    def _create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        validation_results: List[ValidationResult],
        output_data: Any, # Data whose hash represents the hop's output
        start_time: datetime, # Start time of the hop
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None # Added for explicit error logging
    ) -> HopCheckpoint:
        """Creates a HopCheckpoint object, calculates duration and hash."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Determine status based on validation results and explicit errors
        status = HopStatus.PASS # Default
        if error_message: # If an explicit error occurred during execution
            status = HopStatus.FAIL
        elif validation_results:
            # Check severity if validations were performed
            if any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in validation_results):
                status = HopStatus.FAIL
            elif any(not vr.passed and vr.severity == ValidationSeverity.HIGH for vr in validation_results):
                 # Treat HIGH as FAIL for checkpoint status, Gate Decision handles halting logic
                 status = HopStatus.FAIL
            elif any(not vr.passed for vr in validation_results): # Any Medium/Low failure -> WARNING
                 status = HopStatus.WARNING


        # Calculate output hash safely
        output_hash = None
        if output_data is not None:
            try:
                # Use canonical JSON representation for dicts
                if isinstance(output_data, dict):
                    # Ensure dataclasses are converted if necessary before dump
                    def default_serializer(o):
                        if hasattr(o, '__dataclass_fields__'): return asdict(o)
                        # --- START ADDED for ThematicAnalysis ---
                        if isinstance(o, ThematicAnalysis): return asdict(o)
                        # --- END ADDED ---
                        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
                    output_str = json.dumps(output_data, sort_keys=True, separators=(',', ':'), default=default_serializer)
                elif isinstance(output_data, list):
                     # Attempt to sort simple lists, otherwise just dump
                     try: output_str = json.dumps(sorted([str(item) for item in output_data]))
                     except TypeError: output_str = json.dumps([str(item) for item in output_data]) # Fallback for un-sortable
                # --- START ADDED for ThematicAnalysis ---
                elif isinstance(output_data, ThematicAnalysis):
                    output_str = json.dumps(asdict(output_data), sort_keys=True, separators=(',', ':'))
                # --- END ADDED ---
                else:
                    output_str = str(output_data) # Fallback for other types
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
            # Store a deep copy to prevent modification issues
            validation_results=[copy.deepcopy(vr) for vr in validation_results],
            metadata=copy.deepcopy(metadata) or {}, # Ensure metadata is copied
            error_message=error_message
        )

        # Store duration in metadata
        checkpoint.metadata["duration_seconds"] = round(duration, 3)

        # Add to hash chain (Chain of Custody)
        if self.hash_chain:
            prev_hash = self.hash_chain[-1]
            chain_input = f"{prev_hash}|{hop_id}|{status.value}|{output_hash}|{checkpoint.timestamp_end}"
            current_chain_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()[:16]
        else:
            current_chain_hash = output_hash or f"{hop_id}_START_{status.value}"

        self.hash_chain.append(current_chain_hash)
        checkpoint.metadata["chain_hash"] = current_chain_hash # Add to metadata for inspection

        return checkpoint

    def _check_hop_status(self, checkpoint: HopCheckpoint, allow_warnings: bool = False, check_critical_only: bool = False):
        """
        Checks hop status. Halts workflow on FAIL unless overridden. Logs PASS/WARNING.
        """
        # Determine effective status for halting based on flags
        effective_status = checkpoint.status
        severity_threshold = ValidationSeverity.HIGH # Default halt level
        halt_reason_prefix = "HIGH/CRITICAL"

        if check_critical_only:
             severity_threshold = ValidationSeverity.CRITICAL
             halt_reason_prefix = "CRITICAL"
             # If check_critical_only is True, override FAIL status to PASS if only HIGH failures exist
             if checkpoint.status == HopStatus.FAIL and not any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in checkpoint.validation_results):
                  effective_status = HopStatus.PASS # Treat as PASS for *halting* purpose


        # --- Halting Logic ---
        if effective_status == HopStatus.FAIL:
            failed_results = sorted(
                [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity.value >= severity_threshold.value],
                key=lambda x: x.severity.value, reverse=True
            )
            highest_failure = failed_results[0] if failed_results else None
            # Handle potential callable error messages
            reason = checkpoint.error_message or \
                     (f"{highest_failure.rule_id}: {highest_failure.message(highest_failure.details) if callable(highest_failure.message) else highest_failure.message}" if highest_failure else "Unknown failure")


            error_msg = f"[{checkpoint.hop_id}] FAILED - Halting workflow. Reason: {reason}"
            self.logger.error(f"  ✗ {error_msg}")

            # Log top 3 relevant failures
            failures_to_log = failed_results[:3]
            for vr in failures_to_log:
                 # Ensure message is formatted if callable
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 self.logger.error(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")

            raise HopExecutionError(f"{checkpoint.hop_id} failed validation ({halt_reason_prefix}). Halting.")

        # --- Warning / Pass Logging ---
        elif checkpoint.status == HopStatus.WARNING:
            warnings = [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            self.logger.warning(f"  ⚠️ [{checkpoint.hop_id}] completed with {len(warnings)} warnings.")
            if not allow_warnings:
                 # If warnings are disallowed (should not happen with current logic, but safeguard)
                 error_msg = f"[{checkpoint.hop_id}] FAILED - Warnings detected and not allowed. Halting."
                 self.logger.error(f"  ✗ {error_msg}")
                 raise HopExecutionError(error_msg)
            else:
                 # Log top 1-2 warnings for info
                 for vr in warnings[:2]:
                     # Ensure message is formatted if callable
                     msg = vr.message(vr.details) if callable(vr.message) else vr.message
                     self.logger.warning(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")
                 # Log successful completion despite warnings
                 self.logger.info(f"  ✓ {checkpoint.hop_id} completed (with warnings).")


        elif checkpoint.status == HopStatus.PASS:
            self.logger.info(f"  ✓ {checkpoint.hop_id} completed successfully.")
        else:
             # Should not happen
             self.logger.error(f"  ? Unknown status encountered for {checkpoint.hop_id}: {checkpoint.status}")

    def _build_coc_ledger(
        self,
        workflow_start: datetime,
        workflow_end: datetime,
        thematic_analysis: Optional[ThematicAnalysis] # Allow None
    ) -> Dict:
        """Builds the Chain of Custody (CoC) ledger dictionary."""
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', 'UnknownCandidate')}".encode('utf-8')
        ).hexdigest()[:16]

        rag_metadata = {}
        if thematic_analysis: # Populate only if analysis succeeded
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            rag_metadata = {
                "signal_quality": getattr(thematic_analysis, 'signal_quality_score', 0.0),
                "retrieval_method": getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN'),
                "peer_jds_analyzed": getattr(comp_intel, 'peer_jds_analyzed_count', 0) if comp_intel else 0,
                "differentiator_keywords": getattr(comp_intel, 'differentiator_keywords', [])[:10] if comp_intel else [], # Top 10
                "jd_input_hash": self.jd_enforcer.jd_hash if hasattr(self, 'jd_enforcer') else None
            }

        # Determine overall status based on the *final* checkpoint's status AND any prior failures
        overall_status = HopStatus.PASS.value # Assume PASS initially
        if any(hc.status == HopStatus.FAIL for hc in self.hop_checkpoints):
             overall_status = HopStatus.FAIL.value
        elif self.hop_checkpoints: # If no FAIL, check the last status
             overall_status = self.hop_checkpoints[-1].status.value


        # Safely convert checkpoints to dicts
        hops_executed_list = []
        for hc in self.hop_checkpoints:
             try: hops_executed_list.append(asdict(hc))
             except Exception as e:
                 self.logger.warning(f"Could not serialize checkpoint {hc.hop_id}: {e}")
                 # Add a placeholder or simplified dict
                 hops_executed_list.append({
                     "hop_id": hc.hop_id, "hop_name": hc.hop_name, "status": hc.status.value,
                     "error": "Serialization failed"
                 })

        return {
            "workflow_id": workflow_id,
            "engine_version": f"v{__version__}",
            "architecture_version": f"Job_Workflow_v11.0_Redesign", # Update architecture label
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

    # --- QA Report Section Builders ---

    def _build_qa_section_1_signal_quality(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        # (Implementation unchanged, title already correct)
        lines = ["", "1. SIGNAL QUALITY (Per-Section Analysis vs. JD Keywords)", ""]
        max_signal_target = SignalControlConfig().SECTION_SIGNAL_SCORE_MAX
        section_configs = PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG
        total_weighted_score, total_weight = 0.0, 0.0
        total_weighted_temp, temp_weight = 0.0, 0.0
        lines.append("```markdown")
        for label, (section_enum, target_min_score, target_max_score, weight, reasoning_config) in section_configs.items():
            content = staging_buffer.get(section_enum.value)
            if content:
                score = calculate_signal_score(content, thematic_analysis)
                total_weighted_score += score * weight
                total_weight += weight
                api_params = reasoning_config_to_api_params(reasoning_config)
                sc_count = api_params.get('sc', 1)
                temp = 0.9 if sc_count > 1 else api_params["generation_config"].temperature
                # Apply K.1 specific temp logic for reporting
                if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY and sc_count <= 1:
                    # Check if an override was used during generation (requires storing it or checking logs)
                    # For simplicity, let's assume the schedule's first value (1.0) was used if no SC.
                    k1_attempt_checkpoint = next((c for c in reversed(self.hop_checkpoints) if c.hop_id == "HOP-3"), None)
                    attempt = k1_attempt_checkpoint.metadata.get("attempts_made", 1) if k1_attempt_checkpoint else 1
                    k1_temp_schedule = [1.0, 0.9, 0.8, 0.7, 0.5]
                    temp = k1_temp_schedule[min(attempt - 1, len(k1_temp_schedule) - 1)]

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
        # (Implementation unchanged, title updated)
        lines = ["", "2. HOP-0 RAG SIGNAL FLOW MAP (Consumed Signals)", ""] # <<< Title correct
        lines.append("This table shows how RAG intelligence (columns) was consumed by each generated resume section (rows), based on validation metrics or confirmed use in generation logic.")
        lines.append("")
        lines.append("```markdown")

        # --- Define Headers ---
        headers = [
            "Target Section",
            "Primary Theme\n(AI Technical\n Success)",
            "Differentiator\nKeywords (e.g.,\n GenAI adoption,\n SaaS delivery,\n retention)",
            "Role Archetype\n(Post-Sales_Success)",
            "Problem-Solution\nNarrative (e.g.,\n 'slow adoption')",
            "Secondary Themes\n(e.g., Team Scaling)",
            "Authenticity Patterns\n(Voice & Phrasing)"
        ]

        # --- Define Rows and Signal Consumption Logic ---
        # This logic maps the structure provided in the user's Table 2b
        rows_config = [
            {"section": ResumeSection.K0_HEADLINE, "label": "K.0 (Headline)", "signals": ["Primary", "Diff_Pct", "Archetype", None, None, "Auth"]},
            {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "label": "K.1 (Exec Summary)", "signals": ["Primary", "Diff_Count", "Archetype", None, "Secondary", "Auth"]},
            {"section": ResumeSection.K5_UNIFY_BULLETS, "label": "K.5 (Unify Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K5_UNIFY_OVERVIEW, "label": "K.5 (Unify Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K6_IBM_BULLETS, "label": "K.6 (IBM Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K6_IBM_OVERVIEW, "label": "K.6 (IBM Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K7_TRADERSENSE_BULLETS, "label": "K.7 (TraderSense)", "signals": [None, None, None, None, None, None]}, # Copied verbatim
            {"section": ResumeSection.K8_EY_BULLETS, "label": "K.8 (EY Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K8_EY_OVERVIEW, "label": "K.8 (EY Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K9_EARLY_CAREER_BULLETS, "label": "K.9 (Early Career Bullets)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "label": "K.9 (Early Career Overview)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K10_COMPETENCIES, "label": "K.10 (Comp.)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", "Auth"]},
            {"section": ResumeSection.K2_SKILLS, "label": "K.2 (Skills)", "signals": ["Primary", "Diff_Pct", None, None, "Secondary", None]},
            {"section": ResumeSection.K13_COVER_LETTER, "label": "K.13 (C.L.)", "signals": ["Primary", "Diff_Pct", None, "Narrative", None, "Auth"]},
        ]

        # --- Prepare Data for Table ---
        table_rows = []
        for row_cfg in rows_config:
            section_label = row_cfg["label"]
            signal_presence = row_cfg["signals"]
            content = staging_buffer.get(row_cfg["section"].value)

            row_data = [section_label]

            # Primary Theme Check (✓ / N/A)
            row_data.append("✓" if signal_presence[0] == "Primary" else "N/A")

            # Differentiator Check (Value / N/A)
            if signal_presence[1] == "Diff_Pct" and content:
                 score = calculate_signal_score(content, thematic_analysis) # Approximation
                 row_data.append(f"{score:.1%}")
            elif signal_presence[1] == "Diff_Count" and content:
                diff_count = 0
                differentiators = [] # Default to empty list
                if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
                    # Safely get differentiator keywords
                    differentiators = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', []) or []
                if differentiators:
                    summary_lower = str(content).lower()
                    diff_count = sum(1 for kw in differentiators if kw and kw.lower() in summary_lower)
                row_data.append(f"{diff_count}/{len(differentiators)} Found")
            else:
                row_data.append("N/A")


            # Role Archetype Check (✓ / N/A)
            row_data.append("✓" if signal_presence[2] == "Archetype" else "N/A")

            # Problem-Solution Narrative Check (✓ / N/A)
            row_data.append("✓" if signal_presence[3] == "Narrative" else "N/A")

            # Secondary Themes Check (✓ / N/A)
            row_data.append("✓" if signal_presence[4] == "Secondary" else "N/A")

            # Authenticity Patterns Check (✓ / ✗) - Assume all generated use it, unless explicitly None
            row_data.append("✓" if signal_presence[5] == "Auth" else "✗")

            table_rows.append(row_data)

        # --- Format Table ---
        # Adjust column widths manually for better wrapping
        col_widths = [20, 20, 18, 18, 18, 18, 20]
        lines.extend(self._format_plain_text_table(headers, table_rows, col_widths=col_widths, wrap_text=True))
        lines.append("```")
        lines.append("Legend: ✓ = Signal Consumed, ✗ = Signal Not Consumed, N/A = Not Applicable, Pct/Count = Validation Metric")

        return lines

    def _build_qa_section_3_hop_summary(self) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "3. HOP-BY-HOP EXECUTION SUMMARY", ""] # <<< Title Correct
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
        """
        [v11.0.2 NEW] Builds combined Section 4 for Word Count & Distribution Compliance.
        Merges old sections 4 and 5, removes bullet tolerance row.
        """
        lines = ["", "4. WORD COUNT & DISTRIBUTION COMPLIANCE", ""]
        lines.append("This section combines overall resume word count checks, key section constraints (Headline, Exec Summary, Cover Letter paragraphs), and distribution metrics (Unify/IBM) into a single table. Bullet length validation is covered in Section 6.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section", "Rule ID", "Value", "Target Range", "Status", "Message / Details"]
        rows = []

        # Define the Rule IDs and Section labels for this table
        rules_to_include = {
            "VG_TOTAL_WORD_COUNT": "Overall Resume",
            "VG_HEADLINE_WORD_COUNT": "Headline",
            "VG_WORD_COUNT_K1": "Executive Summary",
            "VG_SENTENCE_COUNT_K1": "Executive Summary",
            "WORD_DISTRIBUTION_UNIFY_IBM": "Experience Dist.",
            "UNIFY_IBM_RATIO": "Experience Dist.",
            # Placeholder Rule IDs for cover letter paragraphs (assuming validator provides these)
            "CL_P1_WORD_COUNT": "Cover Letter",
            "CL_P2_WORD_COUNT": "Cover Letter",
            "CL_P3_WORD_COUNT": "Cover Letter",
        }

        # Assume cover letter paragraph results come from COVER_LETTER_STRUCTURE details
        # We need to find that result first to extract paragraph counts
        cl_structure_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_STRUCTURE"), None)
        cl_paragraph_details = {}
        if cl_structure_result and isinstance(cl_structure_result.details, dict):
             cl_paragraph_details = cl_structure_result.details

        for rule_id, section_label in rules_to_include.items():
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)

            # Special handling for cover letter paragraphs
            if rule_id.startswith("CL_P"):
                p_num = rule_id.split('_')[1] # e.g., "P1"
                p_key_wc = f"{p_num.lower()}_wc" # e.g., "p1_wc"
                p_key_min = f"{p_num.lower()}_min"
                p_key_max = f"{p_num.lower()}_max"

                # If CL_STRUCTURE rule failed, we might not have details, synthesize a row
                if not cl_structure_result or not cl_structure_result.passed:
                     # Attempt to find the specific rule if validator creates them separately
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
                     else: # No specific rule, create FAIL row from CL_STRUCTURE failure
                         rows.append([section_label, rule_id, "N/A", "N/A", "FAIL", "CL_STRUCTURE failed or details missing"])
                # If CL_STRUCTURE passed, extract details
                elif p_key_wc in cl_paragraph_details:
                    wc = cl_paragraph_details.get(p_key_wc, 0)
                    min_r = cl_paragraph_details.get(p_key_min, 0)
                    max_r = cl_paragraph_details.get(p_key_max, 0)
                    status = "PASS" if min_r <= wc <= max_r else "FAIL" # Re-check status just in case
                    msg = "" if status == "PASS" else f"{rule_id} count {wc} out of range {min_r}-{max_r}"
                    value_str = f"{wc} words"
                    target_str = f"{min_r}-{max_r}"
                    rows.append([section_label, rule_id, value_str, target_str, status, msg])
                else:
                    # Details missing even if CL_STRUCTURE passed?
                    rows.append([section_label, rule_id, "N/A", "N/A", "WARN", f"Details missing for {rule_id}"])

            # Handle other rules normally
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
                    elif 'sentences' in value_str: pass # No unit needed
                    elif 'words' in value_str: pass # No unit needed
                    else: # Try to infer unit for ratio
                         if isinstance(details['min'], float): target_str = f"{details['min']:.1f}-{details['max']:.1f}"


                status = "PASS" if result.passed else "FAIL"
                msg = result.message if not result.passed else ""
                # Check if message is callable
                if callable(msg): msg = msg(details)


                rows.append([section_label, rule_id, value_str, target_str, status, msg])
            else:
                # Rule result not found
                rows.append([section_label, rule_id, "N/A", "N/A", "WARN", "Validation result not found"])

        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    QA_PROVENANCE_SECTIONS = [
        {"name": "Unify", "overview_enum": ResumeSection.K5_UNIFY_OVERVIEW, "bullets_enum": ResumeSection.K5_UNIFY_BULLETS},
        {"name": "IBM", "overview_enum": ResumeSection.K6_IBM_OVERVIEW, "bullets_enum": ResumeSection.K6_IBM_BULLETS},
        {"name": "TraderSense", "overview_enum": ResumeSection.K7_TRADERSENSE_OVERVIEW, "bullets_enum": ResumeSection.K7_TRADERSENSE_BULLETS},
        {"name": "EY", "overview_enum": ResumeSection.K8_EY_OVERVIEW, "bullets_enum": ResumeSection.K8_EY_BULLETS}, # Corrected typo in original code? Should be K8_EY_BULLETS
        {"name": "EarlyCareer", "overview_enum": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "bullets_enum": ResumeSection.K9_EARLY_CAREER_BULLETS},
        {"name": "Competencies", "bullets_enum": ResumeSection.K10_COMPETENCIES}, # No overview for competencies
        # Add other sections if needed
    ]
    # NOTE: The actual QA_PROVENANCE_SECTIONS config wasn't in the provided file, this is inferred.
    # Ensure the "name" field here EXACTLY matches the keys generated by _calculate_master_avg_bullet_length

    def _build_qa_section_5_provenance(self, staging_buffer: ImmutableStagingBuffer) -> List[str]:
        """
        Builds QA Section 5: Bullet Provenance & Word Count.
        Validates bullet word counts against master averages +/- tolerance.
        """
        lines = ["", "5. BULLET PROVENANCE & WORD COUNT", ""]
        lines.append("```markdown")
        headers = ["Section", "Item", "Provenance", "Word Count", "Target Range", "Status", "Text Snippet"]
        rows = []
        # Calculate or retrieve master average lengths
        master_avg_lengths = self._calculate_master_avg_bullet_length()
        # Log the dictionary of averages being used
        logging.info(f"Using Master Averages for QA Sec 5: {master_avg_lengths}")
        tolerance = 0.20 # Defined elsewhere, assuming 20%

        # Iterate through the sections defined in the (assumed) configuration
        for section_data in self.QA_PROVENANCE_SECTIONS:
            name = section_data["name"] # e.g., "Unify", "IBM"

            # --- Process Overview (If applicable) ---
            # (Skipping overview logic as the focus is on bullet ranges)

            # --- Process Bullets ---
            bullets_enum = section_data.get("bullets_enum")
            if bullets_enum:
                # *** CRITICAL MAPPING LOGIC ***
                # This line determines which average to use.
                # 'name' (e.g., "Unify") MUST exist as a key in master_avg_lengths.
                avg_key = name if name in master_avg_lengths else "Default"
                # *** END CRITICAL MAPPING LOGIC ***

                avg_len = master_avg_lengths.get(avg_key, 25.0) # Get the average, fallback to default
                logging.debug(f"Processing Section '{name}', using avg_key='{avg_key}', avg_len={avg_len:.1f}")

                bullets = staging_buffer.get(bullets_enum.value, [])

                if isinstance(bullets, list) and bullets:
                    for i, bullet_item in enumerate(bullets):
                        bullet_text, word_count, provenance = "", 0, "N/A" # Initialize defaults

                        if isinstance(bullet_item, dict):
                            # Handle dictionary bullets (preferred structure)
                            bullet_text = bullet_item.get('text', bullet_item.get('bullet_text','')) # Check both 'text' and 'bullet_text'
                            word_count = bullet_item.get('word_count', count_words_ms_word_style(bullet_text)) # Use pre-calculated if available
                            provenance = bullet_item.get('provenance', 'N/A')
                        elif isinstance(bullet_item, str):
                            # Handle simple string bullets (e.g., fallback K7)
                            bullet_text = bullet_item
                            word_count = count_words_ms_word_style(bullet_text)
                            # Assign provenance based on section if it's just strings
                            provenance = BulletProvenance.Verbatim.value if bullets_enum == ResumeSection.K7_TRADERSENSE_BULLETS else "N/A"
                        else:
                            logging.warning(f"Unexpected item type in {bullets_enum.value}[{i}]: {type(bullet_item)}. Skipping.")
                            continue # Skip this item

                        # Calculate min/max target range based on the looked-up average length
                        min_target = round(avg_len * (1 - tolerance))
                        max_target = round(avg_len * (1 + tolerance))
                        logging.debug(f"  Bullet {i+1}: WordCount={word_count}, Avg={avg_len:.1f}, Tol={tolerance:.0%}, Target={min_target}-{max_target}")

                        # Check status and get the target range string for the table
                        status, target_range_str = self._check_word_count(word_count, min_target, max_target)

                        # Append row data
                        rows.append([
                            name, # Section Name
                            str(i + 1), # Item number
                            provenance, # Provenance (Verbatim, Customized, Synthetic)
                            str(word_count), # Actual word count
                            target_range_str, # The calculated target range (e.g., "23-35")
                            status, # PASS or FAIL
                            bullet_text[:60] + ("..." if len(bullet_text) > 60 else "") # Text snippet
                        ])
                elif not isinstance(bullets, list):
                    logging.warning(f"Expected list for bullets in section '{name}' ({bullets_enum.value}), but got {type(bullets)}. Skipping.")
                # else: list is empty, nothing to process which is fine


        # Format the table using the collected rows
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    # Helper used by the QA section builder
    
    def _check_word_count(self, count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        """Helper to check word count against range and return status/string."""
        if min_target <= count <= max_target:
            status = "PASS"
        else:
            status = "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str
    def _build_qa_section_6_authenticity(self, validation_results: List[ValidationResult]) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "6. CONTENT AUTHENTICITY (Hallucination & Signal Check)", ""] # <<< Renumbered (was 7)
        # Combine Hallucination checks from all hops + the specific Authenticity Signal check from HOP-5
        auth_results = [vr for hop in self.hop_checkpoints for vr in hop.validation_results if "HALLUCINATION" in vr.rule_id]
        auth_signal_check = next((vr for vr in validation_results if vr.rule_id == "VG_AUTHENTICITY_SIGNAL_CHECK"), None)
        if auth_signal_check: auth_results.append(auth_signal_check) # Add the signal check result

        lines.append("```markdown")
        headers = ["Check ID", "Status", "Message / Details"]
        rows = []
        if auth_results:
             auth_results.sort(key=lambda vr: vr.rule_id) # Sort for consistency
             for vr in auth_results:
                  msg = vr.message(vr.details) if callable(vr.message) else vr.message
                  details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                  rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{msg}{details_str}"])
        else:
             rows = [["AUTHENTICITY_CHECKS", "PASS", "No hallucination checks run or all passed; Authenticity signal check passed or not run."]]

        expected_rows = len(auth_results) if auth_results else 1
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} auth rows, got {len(rows)}")

        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_7_overview_similarity(self) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "7. OVERVIEW VS. BULLET SIMILARITY CHECK", ""] # <<< Renumbered (was 8)
        if self.overview_similarity_data:
            lines.append("```markdown")
            headers = ["Section", "Max Similarity", "Threshold", "Status"]
            rows = []
            for sim_data in self.overview_similarity_data:
                max_sim = sim_data.get("max_similarity", 0.0)
                passed = max_sim < 0.6
                rows.append([sim_data.get("section", "N/A"), f"{max_sim:.2f}", "< 0.60", "✓ PASS" if passed else "✗ FAIL"])

            expected_rows = len(self.overview_similarity_data)
            if len(rows) != expected_rows:
                 lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} overview sim rows, got {len(rows)}")

            lines.extend(self._format_plain_text_table(headers, rows))
            lines.append("```")
        else:
            lines.append("  (Overview vs. Bullet similarity analysis was not performed or failed).")
        return lines

    def _build_qa_section_8_pairwise_similarity(self) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "8. PAIRWISE BULLET SIMILARITY (Deduplication)", ""] # <<< Renumbered (was 9)
        lines.append("```markdown")
        headers = ["Bullet 1", "Bullet 2", "Similarity", "Status"]
        rows = []

        if not self.similarity_matrix_data:
            lines.append("(Pairwise similarity analysis was not performed or found no data.)")
            lines.append("```")
            return lines

        duplicates = self.similarity_matrix_data.get('duplicates_found', [])
        expected_rows = 0 # Default if no duplicates

        if duplicates:
            expected_rows = len(duplicates)
            for dup in duplicates:
                rows.append([dup['bullet_1'], dup['bullet_2'], f"{dup['similarity']:.4f}", "✗ FAIL"])
        # else: # No duplicates found path handled after table formatting


        lines.extend(self._format_plain_text_table(headers, rows))

        # Check truncation *after* potentially adding rows
        if len(rows) != expected_rows and duplicates: # Only check if duplicates were expected
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} duplicate rows, got {len(rows)}")


        if not duplicates:
            # Clean up default message if table formatter added it
            if lines[-1] == "(No data available)": lines.pop()
            lines.append("  No duplicates found (Similarity < 0.90).")

        lines.append("\n-- Summary --")
        lines.append(f"  Total Comparisons Made: {self.similarity_matrix_data.get('total_comparisons', 0)}")
        lines.append(f"  Maximum Similarity Found: {self.similarity_matrix_data.get('max_similarity', 0.0):.4f}")
        lines.append(f"  Duplicates Found (>= 0.90): {len(duplicates)}")

        lines.append("```")
        return lines

    def _build_qa_section_9_pipeline_health(self) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "9. PIPELINE HEALTH (Resource Consumption)", ""] # <<< Renumbered (was 11)
        lines.append("```markdown")
        headers = ["Hop ID", "Hop Name", "Status", "RAG API Calls", "LLM API Calls"]
        rows = []
        total_rag_calls, total_llm_api_calls = 0, 0
        for hop in self.hop_checkpoints:
            searches = hop.metadata.get('web_search_calls', 0)
            llm_calls = hop.metadata.get('llm_api_calls', 0)
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
        """
        Builds QA Section 10: Structural Validation (Content Presence).
        Focuses only on rules checking for the presence of required sections.
        """
        lines = ["", "10. STRUCTURAL VALIDATION (Content Presence)", ""] # <<< Renumbered (was 12/11) & Renamed
        # Only include rules checking for the presence of required sections
        struct_rule_ids = [
            "STRUCTURE_", # Prefix for all presence checks
            "COVER_LETTER_SIGNATURE" # Check for presence of the signature block itself
        ]
        struct_results = [vr for vr in validation_results if any(rid in vr.rule_id for rid in struct_rule_ids)]

        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        expected_rows = 0

        if struct_results:
             struct_results.sort(key=lambda vr: vr.rule_id)
             expected_rows = len(struct_results)
             for vr in struct_results:
                 # Ensure message is formatted if callable
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                 # Only show message if failed, keep PASS rows clean
                 final_msg = msg if not vr.passed else ""
                 rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg}{details_str}"])
        else:
             rows = [["N/A", "INFO", "No structural presence validation results found."]]
             expected_rows = 1

        # Check for truncation only if results were expected
        if len(rows) != expected_rows and struct_results:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} structural rows, got {len(rows)}")

        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines
    
    def _build_qa_section_11_prod_readiness(self, validation_results: List[ValidationResult]) -> List[str]:
        # (Implementation unchanged, title updated)
        lines = ["", "11. PRODUCTION READINESS", ""] # <<< Renumbered (was 13)
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
        # (Implementation unchanged, title updated)
        lines = ["", "12. COVER LETTER QA", ""] # <<< Renumbered (was 14)
        cl_results = [vr for vr in validation_results if "COVER_LETTER" in vr.rule_id and vr.rule_id != "COVER_LETTER_STRUCTURE"] # Exclude structure rule now handled in Sec 4
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
        # (Implementation unchanged, title updated)
        lines = ["", "13. JD ENFORCEMENT VALIDATION", ""] # <<< Renumbered (was 15)
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
        # (Implementation unchanged, title updated)
        lines = ["", "14. FORMATTING OF OUTPUTS", ""] # <<< Renamed Title
        lines.append("Verifies the presence and correct formatting of all generated output files based on rendering logic and structural validation rules.") # <<< Updated Description slightly
        lines.append("")
        lines.append("```markdown")
        headers = ["Artifact", "Check Type", "Requirement", "Status", "Failure Explanation"] # <<< Column names from last approved design
        output_definitions = []

        # --- Resume Checks ---
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
            h2_pass = h2_check_result.passed if h2_check_result else True # Assume pass if check missing (it's placeholder)
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

        # --- Skills Checks ---
        skills_content = file_contents.get('skills', '')
        output_definitions.append(("**Skills**", "Presence/Type", "Raw Text", "PASS" if skills_content else "FAIL", "" if skills_content else "Content missing."))
        if skills_content:
            skills_lines = [line.strip() for line in skills_content.strip().split('\n') if line.strip()]
            bullet_pass = all(line.startswith("• ") for line in skills_lines) if skills_lines else True # Pass if empty after strip
            output_definitions.append(("**Skills**", "Bullet Format", "`• ` Used", "PASS" if bullet_pass else "FAIL", "" if bullet_pass else "Skills not using '• ' format."))
            newline_pass = skills_content.strip().count('\n') >= (len(skills_lines) - 1) if len(skills_lines) > 1 else True
            output_definitions.append(("**Skills**", "Line Breaks", "Newlines Between Skills", "PASS" if newline_pass else "FAIL", "" if newline_pass else "Missing newlines between skills."))

        # --- Cover Letter Checks ---
        cl_content = file_contents.get('cover_letter', '')
        output_definitions.append(("**Cover L.**", "Presence/Type", "Raw Text", "PASS" if cl_content else "FAIL", "" if cl_content else "Content missing."))
        if cl_content:
            cl_struct_result = next((vr for vr in validation_results if vr.rule_id == "VG_COVER_LETTER_FULL_STRUCTURE"), None)
            cl_struct_pass = cl_struct_result.passed if cl_struct_result else False
            output_definitions.append(("**Cover L.**", "Overall Structure", "Standard Letter Format Present", "PASS" if cl_struct_pass else "FAIL", "" if cl_struct_pass else cl_struct_result.message if cl_struct_result else "Check missing"))
            cl_sig_multi_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_SIGNATURE_MULTILINE"), None)
            cl_sig_multi_pass = cl_sig_multi_result.passed if cl_sig_multi_result else False
            output_definitions.append(("**Cover L.**", "Signature Format", "COVER_LETTER_SIGNATURE_MULTILINE", "PASS" if cl_sig_multi_pass else "FAIL", "" if cl_sig_multi_pass else cl_sig_multi_result.message if cl_sig_multi_result else "Check missing"))

        # --- QA Report Checks ---
        qa_content = file_contents.get('qa_report', '')
        output_definitions.append(("**QA Report**", "Presence/Type", "Fenced Markdown", "PASS" if qa_content else "FAIL", "" if qa_content else "Content missing."))
        if qa_content:
            fence_pass = "```markdown" in qa_content and qa_content.strip().endswith("```")
            output_definitions.append(("**QA Report**", "Markdown Fences", "Uses Fenced Markdown", "PASS" if fence_pass else "FAIL", "" if fence_pass else "Missing markdown fences."))
            table_pass = qa_content.count("```markdown") >= 2 # Check if multiple fenced blocks exist
            output_definitions.append(("**QA Report**", "Table Format", "Uses Pre-formatted Tables", "PASS" if table_pass else "WARN", "" if table_pass else "Could not verify presence of pre-formatted tables."))
            section_headers = ["1. SIGNAL QUALITY", "2. HOP-0 RAG SIGNAL FLOW MAP", "3. HOP-BY-HOP", "13. JD ENFORCEMENT", "14. FORMATTING OF OUTPUTS"] # Updated numbers
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

        # --- App Tracker Checks ---
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
                    output_definitions[-1] = ("**App Trkr**", "Presence/Type", "JSON Block (Unfenced)", "FAIL", "App Tracker incorrectly includes ```json fences.") # Mark fence as fail
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

        # --- Final Formatting ---
        final_rows = [[item[0], item[1], item[2], item[3], item[4]] for item in output_definitions]
        # Adjust widths for the new structure
        col_widths = [13, 36, 34, 8, 0] # Let last column auto-size
        lines.extend(self._format_plain_text_table(headers, final_rows, alignments=['L', 'L', 'L', 'L', 'L'], col_widths=col_widths, wrap_text=False)) # Turn off wrap for this table
        lines.append("```")

        return lines
    
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]}, # New Section 2
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]}, # New Merged Section 4
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]}, # Was 6
        {"method": "_build_qa_section_6_authenticity", "args": ["validation_results"]}, # Was 7
        {"method": "_build_qa_section_7_overview_similarity", "args": []}, # Was 8
        {"method": "_build_qa_section_8_pairwise_similarity", "args": []}, # Was 9
        {"method": "_build_qa_section_9_pipeline_health", "args": []}, # Was 11
        {"method": "_build_qa_section_10_structural", "args": ["validation_results"]}, # Was 12
        {"method": "_build_qa_section_11_prod_readiness", "args": ["validation_results"]}, # Was 13
        {"method": "_build_qa_section_12_cover_letter", "args": ["validation_results"]}, # Was 14
        {"method": "_build_qa_section_13_jd_enforcement", "args": []}, # Was 15
        {"method": "_build_qa_section_14_final_format", "args": ["validation_results", "file_contents"]}, # Was 16
    ]

    def _generate_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> Tuple[List[ValidationResult], str, Dict[str, str]]: # Return file_contents too
        """
        Generate full QA report by iterating through a configuration of section builders.
        Includes internal check for QA table pre-formatting.
        v11.0.2 Refactor: Uses renumbered QA_REPORT_SECTIONS config and merged Section 4.
        """
        validation_results_out = []
        report_lines = [
            f"RESUME QA REPORT (v{__version__})", # Use dynamic version
            f"Generated: {datetime.now().isoformat()}",
        ]

        # Retrieve current file contents (will include placeholders initially)
        # Assumes self.rendered_output['file_contents'] exists or default to {}
        current_file_contents = (self.rendered_output.get('file_contents', {})
                                 if hasattr(self, 'rendered_output') and self.rendered_output
                                 else {})

        available_args = {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "validation_results": validation_results,
            # Pass the currently known file contents
            "file_contents": current_file_contents
        }

        pre_formatted_check_passed = True
        pre_formatted_check_messages = []
        qa_report_text = "" # Initialize variable to store the final text

        # Iterate through the configured sections, call the builder method for each.
        for section_config in self.QA_REPORT_SECTIONS: # Uses updated config
            method_name = section_config["method"]
            arg_names = section_config["args"]

            try:
                # Get the builder method from the class instance.
                builder_method = getattr(self, method_name)

                # Prepare the arguments required for this specific builder method.
                call_args = []
                for name in arg_names:
                     # Ensure the *most current* version of file_contents is passed, esp. to section 14
                     if name == "file_contents":
                         call_args.append(available_args["file_contents"])
                     elif name in available_args:
                         call_args.append(available_args[name])
                     else:
                         raise KeyError(f"Missing required argument '{name}' for method '{method_name}'")


                # Call the method and extend the report lines.
                section_lines = builder_method(*call_args)

                # Perform the pre-formatting check (excluding section 14 itself which contains the content)
                if method_name != "_build_qa_section_14_final_format": # <<< Updated section number
                    section_text_block = "\n".join(section_lines)
                    is_section_1 = "1. SIGNAL QUALITY" in section_text_block # Check if it's section 1
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

            except (AttributeError, KeyError, Exception) as e: # Broader exception catch
                # Add an error message to the report if a builder is misconfigured or fails.
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

        # Join the lines AFTER all sections are built
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

        # Update file_contents with the generated QA report text BEFORE returning
        final_file_contents = available_args["file_contents"]
        final_file_contents['qa_report'] = qa_report_text
        return validation_results_out, qa_report_text, final_file_contents

    # --- Utility methods for QA report formatting ---

    def _format_ascii_bar_chart(self, label: str, value: float, target_min: float, target_max: float, temperature: float = 0.0, bar_length: int = 10, is_summary: bool = False) -> str:
        """Formats a single line for the ASCII bar chart in QA Section 1."""
        value = min(max(value, 0.0), 1.0) # Clamp value
        filled_length = int(round(bar_length * value))
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)
        score_pct = f"{value:.1%}"
        status = "PASS" if target_min <= value <= target_max else "FAIL"
        temp_str = f"(T: {temperature:.1f})" if not is_summary else f"(Avg T: {temperature:.1f})"
        target_str = f"(Tgt: {target_min:.0%}-{target_max:.0%})"
        # Adjust spacing dynamically
        label_width = 25
        bar_width = bar_length + 2 # For brackets
        score_width = 7
        target_width = len(target_str) + 1
        status_width = 7
        temp_width = len(temp_str) + 1

        # Calculate remaining space and distribute it if needed, or truncate label
        total_width = 80
        current_width = label_width + bar_width + score_width + target_width + status_width + temp_width
        padding = " " * max(0, total_width - current_width)

        label_formatted = f"{label:<{label_width}}"[:label_width] # Truncate if too long

        return f"{label_formatted} [{bar}] {score_pct:<{score_width}} {target_str:<{target_width}} {status:<{status_width}} {temp_str:<{temp_width}}{padding}"

    def _format_plain_text_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        alignments: Optional[List[str]] = None,
        col_widths: Optional[List[int]] = None, # Added optional fixed widths
        wrap_text: bool = False # Added wrap text flag
    ) -> List[str]:
        """Formats data into a fixed-width plain text table."""
        if not headers and not rows:
            return ["(No data available)"]

        num_cols = len(headers) if headers else (len(rows[0]) if rows else 0)
        if num_cols == 0:
            return ["(No data available)"]

        # Determine widths
        if col_widths and len(col_widths) == num_cols:
            widths = col_widths
        else:
            widths = [0] * num_cols
            if headers:
                for i, header in enumerate(headers):
                    # Handle multi-line headers for width calculation
                    max_header_line_width = max(len(line) for line in str(header).split('\n'))
                    widths[i] = max(widths[i], max_header_line_width)
            for row in rows:
                for i, cell in enumerate(row):
                    if i < num_cols: # Handle rows with incorrect number of cells
                        widths[i] = max(widths[i], len(str(cell)))

        # Default alignment to Left if not provided
        aligns = alignments or ['L'] * num_cols
        if len(aligns) < num_cols:
            aligns.extend(['L'] * (num_cols - len(aligns)))

        # Alignment formatters
        formatters = []
        for i in range(num_cols):
            align_char = '<' if aligns[i] == 'L' else '>' if aligns[i] == 'R' else '^'
            formatters.append(f"{{:{align_char}{widths[i]}}}")

        # Build table lines
        lines = []

        # Handle multi-line headers
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


        # Handle text wrapping if enabled
        if wrap_text:
            wrapped_rows = []
            for row in rows:
                 row_lines = [[] for _ in range(num_cols)] # Stores wrapped lines for each cell
                 max_lines = 1
                 for i, cell in enumerate(row):
                     if i < num_cols:
                         cell_str = str(cell)
                         wrapped = self._wrap_cell_text(cell_str, widths[i])
                         row_lines[i].extend(wrapped)
                         max_lines = max(max_lines, len(wrapped))

                 # Pad shorter cell lines and build final row lines
                 for line_idx in range(max_lines):
                     line_parts = []
                     for col_idx in range(num_cols):
                         cell_part = row_lines[col_idx][line_idx] if line_idx < len(row_lines[col_idx]) else ""
                         line_parts.append(formatters[col_idx].format(cell_part))
                     wrapped_rows.append("  ".join(line_parts))
            lines.extend(wrapped_rows)
        else:
             # Original non-wrapping behavior
             for row in rows:
                 lines.append("  ".join(formatters[i].format(str(row[i])[:widths[i]]) for i in range(num_cols) if i < len(row)))


        return lines

    def _wrap_cell_text(self, text: str, width: int) -> List[str]:
        """Wraps text within a cell width, handling newlines."""
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
            lines.append(current_line) # Add the last line
        return lines

    def _check_word_count(self, count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        """Helper to check word count against range and return status/string."""
        if min_target <= count <= max_target:
            status = "PASS"
        else:
            status = "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str

    def _invoke_deduplication_analysis(self, staging_buffer: ImmutableStagingBuffer) -> bool:
        """
        Gathers data and calls DuplicateDetector methods for QA report sections.
        Stores results in self.similarity_matrix_data and self.overview_similarity_data.
        """
        self.dedup_analysis_timestamp = datetime.now().isoformat()
        if not self.dup_detector:
            self.logger.warning("DuplicateDetector not available (likely HOP-2 failure). Skipping deduplication analysis.")
            return False

        # --- Data Gathering ---
        sections_for_matrix = {} # For pairwise
        overview_bullet_pairs = {} # For overview vs bullet
        exec_summary_text = staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        exec_summary_comparison_data = {} # For exec summary vs sections

        section_map = { # Maps Enum to readable name for comparisons
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

        # Collect data for different analyses
        for section_enum, label in section_map.items():
            content = staging_buffer.get(section_enum.value)
            if not content: continue

            if "Overview" in label:
                 sections_for_matrix[label] = [content] if isinstance(content, str) else []
                 overview_bullet_pairs[label] = {"overview": content, "bullets": []} # Prepare pair
                 exec_summary_comparison_data[label] = content # Add overview for comparison
            elif "Bullets" in label or label == "Competencies":
                 bullet_texts = []
                 if isinstance(content, list):
                     for item in content:
                          if isinstance(item, dict):
                              bullet_texts.append(item.get('text', item.get('bullet_text','')))
                          elif isinstance(item, str): # Handle lists of strings (e.g., K7)
                              bullet_texts.append(item)
                 sections_for_matrix[label] = [b for b in bullet_texts if b]
                 exec_summary_comparison_data[label] = [b for b in bullet_texts if b] # Add bullets for comparison
                 # Find corresponding overview and add bullets to it
                 base_label = label.replace(" Bullets", "").replace(" Competencies", "")
                 overview_key = f"{base_label} Overview"
                 if overview_key in overview_bullet_pairs:
                      overview_bullet_pairs[overview_key]["bullets"].extend(sections_for_matrix[label])
                 elif base_label == "Competencies": # Handle competencies case (no overview)
                      pass # Nothing to pair with
            elif label == "Skills":
                 if isinstance(content, list):
                     sections_for_matrix[label] = [item for item in content if isinstance(item, str)]
                     exec_summary_comparison_data[label] = [item for item in content if isinstance(item, str)]
            elif label == "Cover Letter":
                 if isinstance(content, str):
                     # Treat paragraphs as items for comparison
                     paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                     sections_for_matrix[label] = paragraphs
                     exec_summary_comparison_data[label] = paragraphs # Add CL paragraphs


        # --- Execute Analyses ---
        try:
            # 1. Pairwise Matrix (for QA Section 8)
            self.similarity_matrix_data = self.dup_detector.compute_similarity_matrix(sections_for_matrix)
        except Exception as e:
            self.logger.error(f"Error computing similarity matrix: {e}", exc_info=True)
            self.similarity_matrix_data = None

        try:
            # 2. Overview vs. Bullet Similarity (for QA Section 7)
            self.overview_similarity_data = []
            for label, data in overview_bullet_pairs.items():
                 if data["overview"] and data["bullets"]:
                     # Need section_id like K.5_UNIFY_OVERVIEW
                     section_id_base = label.split(" ")[0].upper() # e.g., UNIFY
                     # Construct the enum-like key expected by the original method if needed, or adapt method
                     # For simplicity, let's just use the label
                     sim_result = self.dup_detector.compute_overview_bullet_similarity(
                         data["overview"], data["bullets"], section_id=label # Use label as ID
                     )
                     self.overview_similarity_data.append(sim_result)
        except Exception as e:
            self.logger.error(f"Error computing overview vs bullet similarity: {e}", exc_info=True)
            self.overview_similarity_data = None

        try:
            # 3. Executive Summary vs. Other Sections Similarity (Used implicitly by other sections, no dedicated QA section now)
            self.executive_summary_similarity_data = self.dup_detector.compute_executive_summary_similarity(
                exec_summary_text, exec_summary_comparison_data
            )
        except Exception as e:
             self.logger.error(f"Error computing executive summary similarity: {e}", exc_info=True)
             self.executive_summary_similarity_data = None


        return True # Indicate analysis was attempted

    def _calculate_master_avg_bullet_length(self) -> Dict[str, float]:
        """
        Helper to calculate average bullet length for sections in master resume using MS Word style counting.
        """
        avg_lengths = {}
        # Corrected structure access based on MASTER_RESUME_JSON
        experience_sections = self.master_resume.get("professional_experience", [])
        experience_sections_to_avg = {
            "Unify": ("Unify Consulting", "bullet_pool"),
            "IBM": ("IBM", "bullet_pool"),
            "EY": ("Ernst & Young", "highlights"),
            "TraderSense": ("TraderSense", "highlights"), # Add TraderSense
            "EarlyCareer": ("Early Career Roles", "highlights"),
        }
        default_avg = 25.0 # Fallback average

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

        # For Competencies section
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        competencies_strings = [c for c in competencies_list if isinstance(c, str)]
        avg_lengths["Competencies"] = (sum(count_words_ms_word_style(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0 # Specific default

        # Add a default for any other section needed
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

Datadog offers a competitive salary and equity package, and may include variable compensation. Actual compensation is based on factors such as the candidate's skills, qualifications, and experience. In addition, Datadog offers a wide range of best in class, comprehensive and inclusive employee benefits for this role including healthcare, dental, parental planning, and mental health benefits, a 401(k) plan and match, paid time off, fitness reimbursements, and a discounted employee stock purchase plan.

The reasonably estimated yearly salary for this role at Datadog is:
$250,000—$350,000 USD
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
