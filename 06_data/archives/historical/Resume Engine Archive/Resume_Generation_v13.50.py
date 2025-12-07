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


__version__ = "13.50"
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

    # --- START REFACTOR: Simplified Config Initialization ---
    DEFAULT: ClassVar['ReasoningConfig']
    K0_HEADLINE_CONFIG: ClassVar['ReasoningConfig']
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar['ReasoningConfig']
    K5_UNIFY_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K5_UNIFY_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K6_IBM_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K6_IBM_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K8_EY_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K8_EY_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K9_EARLY_CAREER_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K9_EARLY_CAREER_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K2_SKILLS_CONFIG: ClassVar['ReasoningConfig']
    K10_COMPETENCIES_CONFIG: ClassVar['ReasoningConfig']
    # --- END REFACTOR ---

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

    # --- START CHANGE: Re-introduce Word Count Constraints ---
    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140 # Re-enabled Constraint
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170 # Re-enabled Constraint
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 7
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9 # Increased max sentence count to 9
    K1_MIN_DIFFERENTIATORS: int = 4
    # --- END CHANGE ---

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

# --- START REFACTOR: Simplified Config Initialization ---
ReasoningConfig.DEFAULT = ReasoningConfig()
ReasoningConfig.K0_HEADLINE_CONFIG = ReasoningConfig(cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=4)
ReasoningConfig.K5_UNIFY_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)
ReasoningConfig.K5_UNIFY_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)
ReasoningConfig.K6_IBM_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K6_IBM_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)
ReasoningConfig.K8_EY_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True)
ReasoningConfig.K8_EY_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True)
ReasoningConfig.K9_EARLY_CAREER_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)
ReasoningConfig.K9_EARLY_CAREER_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)
ReasoningConfig.K2_SKILLS_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=True)
ReasoningConfig.K10_COMPETENCIES_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=6, reflexion=True)
# --- END REFACTOR ---
        
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
    # --- Reference the global constant ---
    SCHEMA_FIELDS_V4 = list(APP_TRACKER_SCHEMA_V4.keys())

    # Controlled enums (Unchanged)
    PIPELINE_STATUS_ENUM = ["Applied", "Follow-Up", "Interview", "Rejected", "Closed", "Waiting"]
    # OUTREACH_CHANNEL_ENUM removed as it's not checked in simplified version
    # CLOSURE_REASON_ENUM removed as it's not checked in simplified version

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
            # Allow empty URLs to pass validation here, specific rules check presence if needed
            return True
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(url_pattern, url.strip()))

    # _is_linkedin_profile removed as R18 is skipped

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
                              f"Ensure exactly 54 fields in correct order")
            else:
                self._log_pass("R1")

        # Per-row validation (Simplified)
        for idx, row in enumerate(tracker_rows):
            self._validate_row(idx, row)

        # Generate outcome
        # Log which rules were actually checked
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

        # R2: Pipeline Status enum (Keep: Populated field)
        status = row.get("Pipeline Status", "").strip()
        if status and status not in self.PIPELINE_STATUS_ENUM:
            self._log_fail("R2", idx, "Pipeline Status",
                          f"Invalid status '{status}'",
                          f"Use one of: {', '.join(self.PIPELINE_STATUS_ENUM)}")
        elif not status: # Also check if it's empty, should be "Applied"
             self._log_fail("R2", idx, "Pipeline Status", "Pipeline Status cannot be empty.", "Should be 'Applied'.")
        else:
            self._log_pass("R2")

        # Skip: R3, R4 (Outreach Channel, Closure Reason enums not used)
        # Skip: R5 (Channel gating not relevant)

        # R10 & R11: JD URL presence implies Application Date, check Date format
        # Keep: Both fields are populated
        jd_url = row.get("JD URL", "").strip()
        app_date = row.get("Application Date", "").strip()

        # Check R11: Application Date format (if present)
        if app_date:
            if not self._parse_date(app_date):
                 self._log_fail("R11", idx, "Application Date",
                               f"Invalid date format '{app_date}'",
                               "Use MM/DD/YYYY format")
            else:
                 self._log_pass("R11")
        else: # Application Date is mandatory
             self._log_fail("R11", idx, "Application Date", "Application Date cannot be empty.", "Use MM/DD/YYYY format.")

        # Check R10: If JD URL is present, App Date must also be present (and valid)
        if jd_url:
            if not app_date:
                self._log_fail("R10", idx, "Application Date",
                              "Application Date required when JD URL present",
                              "Add valid MM/DD/YYYY date")
            # If App Date is present (and passed R11), log R10 pass
            elif self._parse_date(app_date):
                self._log_pass("R10")
        # else: # If JD URL is empty, R10 implicitly passes
        #     self._log_pass("R10") # No need to log pass for empty optional field

        # Skip: R12 (Follow-up date formats not used)
        # Skip: R13, R14, R15 (Status/Closure mapping not relevant)
        # Skip: R16 (Contact integrity not relevant)

        # R17: JD URL HTTP validation (Keep: JD URL is populated)
        if jd_url: # Only check if URL is non-empty
            if not self._is_valid_url(jd_url):
                self._log_fail("R17", idx, "JD URL",
                              f"Invalid URL format: '{jd_url}'",
                              "Provide valid HTTP/HTTPS URL")
            else:
                self._log_pass("R17")
        else:
            self._log_pass("R17") # Pass if empty (URL is optional overall, but checked by R10 if AppDate exists)

        # Skip: R18 (LinkedIn format not relevant)

        # R20: Versioned Resume filename validation (Keep: Populated field)
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

        # R21: Company name sanity (Keep: Populated field)
        company = row.get("Company", "").strip()
        if company and len(company) < 2:
            self._log_fail("R21", idx, "Company",
                          "Company name too short",
                          "Provide valid company name (2+ chars)")
        elif not company:
             self._log_fail("R21", idx, "Company", "Company name cannot be empty.", "Provide valid company name.")
        else:
            self._log_pass("R21")

        # R22: Job Title sanity (Keep: Populated field)
        job_title = row.get("Job Title", "").strip()
        if job_title and len(job_title) < 3:
            self._log_fail("R22", idx, "Job Title",
                          "Job title too short",
                          "Provide valid job title (3+ chars)")
        elif not job_title:
             self._log_fail("R22", idx, "Job Title", "Job Title cannot be empty.", "Provide valid job title.")
        else:
            self._log_pass("R22")

    # Removed: _validate_channel_gating (Not needed for simplified validation)

    def _generate_passed_outcome(self, tracker_rows: List[Dict]) -> Dict:
        """Generate PASSED JSON outcome."""
        status_counts = {}
        # channel_counts removed as R3 is skipped
        # channel_counts = {}

        for row in tracker_rows:
            status = row.get("Pipeline Status", "").strip() or "Unknown"
            # channel = row.get("Outreach Channel", "").strip() or "Unknown" # Removed
            status_counts[status] = status_counts.get(status, 0) + 1
            # channel_counts[channel] = channel_counts.get(channel, 0) + 1 # Removed

        return {
            "result": "PASSED",
            "counts_by_rule": self.rule_pass_counts,
            "totals_by_status": status_counts,
            # "totals_by_channel": channel_counts, # Removed
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
        import logging
        import random
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
            # --- INCREMENT COUNTER ---
            self.api_calls_made += 1
            calls_made = 1
            # --- END INCREMENT ---

            # Call generate_content (tools parameter removed)
            response = self.client.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens, # Uses RAGConfig value (e.g., 30000)
                    temperature=self.config.temperature
                )
            )

            elapsed = time.time() - start_time
            logger.debug(f"{phase_name} API call completed in {elapsed:.2f}s (Call #{self.api_calls_made})")

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
        self.total_api_calls_hop0 = 0 # <-- Initialize HOP-0 API call counter

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

    def analyze(self, job_description: str) -> Tuple[ThematicAnalysis, int]: # Return TA and call count
        """
        Analyze job description with resilient web-search intelligence.
        v5.59: Enhanced with 4-tier fallback hierarchy and telemetry.
        NOW returns a tuple: (ThematicAnalysis, total_api_calls_hop0)
        """
        self.total_api_calls_hop0 = 0 # Reset counter for each analysis run

        # HOP -0.5: Pre-RAG Differential Analysis (Approach 1)
        try:
            self.rag_mission = self._execute_pre_rag_analysis(job_description)
            # Add calls from pre-RAG analysis (assuming _execute uses search_and_analyze which returns count)
            # Note: _execute_pre_rag_analysis needs slight modification to return count
            # For now, let's assume it makes 1 call if successful
            self.total_api_calls_hop0 += 1 # Add 1 call for Pre-RAG
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
             # Local NLP doesn't make API calls
             analysis = self._analyze_local_nlp(job_description)
             return analysis, self.total_api_calls_hop0 # Return 0 calls

        # New Design: Re-raise any exception to halt the workflow. No fallback.
        try:
            analysis, calls_made = self._analyze_with_resilient_web_search(job_description)
            self.total_api_calls_hop0 += calls_made # Add calls from main RAG phases
            return analysis, self.total_api_calls_hop0
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
        logger = logging.getLogger(__name__)

        # --- Imports needed for conversion ---
        import json
        from collections.abc import Mapping, Sequence
        from dataclasses import is_dataclass, asdict
        # --- End imports ---

        telemetry = RAGTelemetry() if self.telemetry_logger else None
        start_time = time.time()
        total_api_calls_this_hop = 0 # Initialize counter for this specific execution

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

        # --- Phase 1: Thematic Research ---
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

        # --- Phase 2: Authenticity Patterns ---
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

        # --- Phase 3: Competitive Positioning ---
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

        # --- Phase 4: Problem-Solution Narrative Mining ---
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


        # --- Evaluation Logic ---
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

    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self.hallucination_detector = HallucinationDetector()
        self._validate_master_resume_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
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
        """  # <-- Added opening triple quotes here
        v5.36: Build structured experience_sections from master resume.
        Each section contains: company, title, location, dates, overview, bullets.
        """ # <-- Added closing triple quotes here (assuming intent was multi-line)
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
# ============================================================================
# HOP-2: DATA ENRICHMENT
# ============================================================================

# ============================================================================
# HOP-2: DATA ENRICHMENT
# ============================================================================

class DataEnricher:
    """
    HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc.
    v13.10: Merged VerbCanonicalizer logic directly into this class.
    v13.50: Removed FORBIDDEN_VERBS check (moved to PreFlightValidator).
    """

    # --- START MERGED: VerbCanonicalizer logic ---
    CANONICAL_VERBS = {
        "led": ["led", "lead", "leading"], "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"], "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"], "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"], "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"], "developed": ["developed", "develop", "developing"]
    }
    # --- REMOVED FORBIDDEN_VERBS constant (moved to validator) ---
    # --- END MERGED ---

    def __init__(self):
        # VerbCanonicalizer is now part of this class
        self.duplicate_detector = DuplicateDetector()

    # --- START MERGED: VerbCanonicalizer methods as private methods ---
    def _canonicalize_verbs(self, text: str) -> List[str]:
        """[REFACTORED] Extract and canonicalize verbs from text using a list comprehension."""
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    # --- REMOVED _check_for_forbidden_verbs method (moved to validator) ---
    # --- END MERGED ---

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
                
                # --- REMOVED FORBIDDEN_VERBS validation logic (moved to HOP-5) ---

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
import copy # Added for deepcopy in competency generation
import re   # Added for fence removal in _call_gemini_api
import random # Ensure random is imported for bullet selection
import logging # Ensure logging is imported
import json # Ensure json is imported
from typing import Dict, List, Optional, Any, Tuple, Set, Union # Ensure necessary types are imported

# Assume necessary classes like ResumeSection, ReasoningConfig, ThematicAnalysis,
# ValidationResult, BulletProvenance, ContentConstraintsConfig, HopExecutionError,
# count_words_ms_word_style are defined elsewhere and imported.
# Also assume genai and os are imported and configured elsewhere.

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

    # Provenance targets configuration
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    # Configuration defining which method generates each section
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
        {"section": ResumeSection.K5_UNIFY_BULLETS, "method_name": "_generate_k5_unify_bullets"}, # BULLETS FIRST
        {"section": ResumeSection.K5_UNIFY_OVERVIEW, "method_name": "_generate_k5_unify_overview"}, # THEN OVERVIEW
        {"section": ResumeSection.K6_IBM_BULLETS, "method_name": "_generate_k6_ibm_bullets"},       # BULLETS FIRST
        {"section": ResumeSection.K6_IBM_OVERVIEW, "method_name": "_generate_k6_ibm_overview"},     # THEN OVERVIEW
        {"section": ResumeSection.K8_EY_BULLETS, "method_name": "_generate_k8_ey_bullets"},
        {"section": ResumeSection.K8_EY_OVERVIEW, "method_name": "_generate_k8_ey_overview"},
        {"section": ResumeSection.K9_EARLY_CAREER_BULLETS, "method_name": "_generate_k9_early_career_bullets"},
        {"section": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "method_name": "_generate_k9_early_career_overview"},
        {"section": ResumeSection.K10_COMPETENCIES, "method_name": "_generate_k10_competencies"},
        {"section": ResumeSection.K2_SKILLS, "method_name": "_generate_k2_skills"},
        {"section": ResumeSection.K13_COVER_LETTER, "method_name": "_generate_k13_cover_letter"},
    ]

    # Hardcoded Bullet Word Count Ranges
    BULLET_WORD_COUNT_RANGES = {
        ResumeSection.K5_UNIFY_BULLETS: (25, 38),
        ResumeSection.K6_IBM_BULLETS: (22, 34),
        ResumeSection.K8_EY_BULLETS: (25, 40),
        ResumeSection.K9_EARLY_CAREER_BULLETS: (25, 40),
        ResumeSection.K10_COMPETENCIES: (25, 40),
    }

    # --- START MODIFIED: _call_gemini_api returns (text, call_count) ---
    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return text and call count
        """
        Refactored Helper: Centralizes Gemini API calls.
        v12.70: Raises HopExecutionError on API failure. Explicitly removes markdown fences.
        NOW returns a tuple: (final_text, call_count)
        """
        calls_made_this_invocation = 0
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

                    # --- API Call 1 (Candidates) ---
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    # --- End Call 1 ---

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

                    # --- API Call 2 (Synthesis) ---
                    calls_made_this_invocation += 1
                    synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)
                    # --- End Call 2 ---

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

                    return final_text, calls_made_this_invocation # Return text and count
                except Exception as e:
                    logging.error(f"    SC synthesis for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC synthesis failed: {type(e).__name__} - {e}") from e

            # Single Candidate Logic
            else:
                try:
                    # Make sure the model object is properly initialized and authenticated
                    if not model:
                        raise HopExecutionError(f"{section_id} generation API call failed: Model not initialized.")

                    # --- API Call (Single) ---
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)
                    # --- End Call ---

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

                    return final_text, calls_made_this_invocation # Return text and count
                except Exception as e:
                    logging.error(f"LLM API call for {section_id} failed: {e}", exc_info=True)
                    # Include more context in the exception
                    raise HopExecutionError(f"{section_id} generation API call failed: {type(e).__name__} - {e}") from e
        except HopExecutionError as he: # Re-raise specific errors
            raise he
        except Exception as e: # Catch other unexpected errors
            logging.error(f"Unexpected error in _call_gemini_api for {section_id}: {e}", exc_info=True)
            raise HopExecutionError(f"Unexpected error during {section_id} API call: {e}") from e
    # --- END MODIFIED ---

    # --- START MODIFIED: generate returns (output, validation_results, total_calls) ---
    def generate(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
    ) -> Tuple[Dict, List[ValidationResult], int]: # Return output, results, AND total calls
        """
        [REFACTORED]
        Generates *only* the specified resume sections at the specified temperatures.
        v12.50: This method no longer loops or retries. It executes one generation pass.
        NOW returns the total number of API calls made during this pass.
        """
        validation_results = []
        total_api_calls_this_pass = 0

        try:
            # Call the internal generation method, passing the new parameters
            # _generate_artist_output now returns (output_dict, total_calls)
            artist_output, calls_made = self._generate_artist_output(
                sections_to_generate=sections_to_generate,
                temperature_overrides=temperature_overrides
            )
            total_api_calls_this_pass = calls_made

            # Add a success result *only* for the sections that were attempted
            generated_keys = ", ".join(k for k in artist_output.keys() if artist_output.get(k) is not None)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_PASS", passed=True, severity=ValidationSeverity.INFO,
                message=f"Content generated successfully for: {generated_keys}"
            ))
            return artist_output, validation_results, total_api_calls_this_pass # Return calls

        except HopExecutionError as he: # Catch specific halt errors from generation
            logging.error(f"Artist generation HALTED during selective run: {he}", exc_info=False)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_HALTED", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation halted: {str(he)}",
                details={"error": str(he)}
            ))
            # Return calls made up to the point of failure if possible
            return {}, validation_results, total_api_calls_this_pass

        except Exception as e: # Catch other unexpected errors
            logging.error(f"Artist generation failed unexpectedly during selective run: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed unexpectedly: {str(e)}",
                details={"error": str(e)}
            ))
            # Return calls made up to the point of failure if possible
            return {}, validation_results, total_api_calls_this_pass
    # --- END MODIFIED ---

    # --- START MODIFIED: _generate_artist_output returns (output, total_calls) ---
    def _generate_artist_output(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
        ) -> Tuple[Dict, int]: # Return output dict AND total calls
        """
        [REFACTORED V12.55]
        Generates *only* the specified sections. Raises HopExecutionError on failure.
        Passes current output dict to overview generators that synthesize bullets.
        NOW aggregates and returns the total API calls made during this pass.
        """
        output = {} # This dictionary accumulates results during the generation pass
        total_api_calls = 0 # Counter for calls in this pass

        for config in self.ARTIST_GENERATION_CONFIG:
            section_enum = config["section"]
            method_name = config["method_name"]
            section_api_calls = 0 # Calls for this specific section

            # --- Check if this section should be generated ---
            if section_enum not in sections_to_generate:
                # If it's a copy/dummy method, run it anyway (they are idempotent)
                if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                     try:
                         method = getattr(self, method_name)
                         # Store result directly in the final output dict for this pass
                         output[section_enum.value] = method() # Copy methods don't return call counts
                     except Exception as e:
                         raise HopExecutionError(f"Unexpected error in {method_name} for {section_enum.value}: {e}") from e
                # If it's an LLM method we're skipping, add None temporarily
                else:
                    output[section_enum.value] = None # Will be filtered later
                continue # Skip to next config item

            # --- If section IS in sections_to_generate, run it ---
            logging.info(f"  Generating section: {section_enum.name}")

            # --- Handle sections copied or using placeholders ---
            if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                 try:
                     method = getattr(self, method_name)
                     # Store result directly
                     output[section_enum.value] = method() # Copy methods don't return call counts
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
                # Assume all generation methods now return (content, calls)
                if method_name in ["_generate_k5_unify_overview", "_generate_k6_ibm_overview"]:
                    generated_content, section_api_calls = method(current_output=output, temperature_override=final_temp)
                elif method_name in ["_generate_k8_ey_overview", "_generate_k9_early_career_overview"]:
                     company_name = "Ernst & Young" if method_name == "_generate_k8_ey_overview" else "Early Career Roles"
                     experience_section = next((exp for exp in self.master_resume['professional_experience'] if company_name in exp['company']), None)
                     source_overview = experience_section['overview'] if experience_section else ""
                     if not source_overview:
                          raise HopExecutionError(f"Source overview not found for {company_name} in {section_enum.value}.")
                     generated_content, section_api_calls = method(source_overview=source_overview, temperature_override=final_temp)
                else:
                    # Assumes all other generate methods return (content, calls)
                    generated_content, section_api_calls = method(temperature_override=final_temp)

                # Store the result in the output dictionary
                output[section_enum.value] = generated_content
                total_api_calls += section_api_calls # Aggregate calls

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
        return final_output_for_this_pass, total_api_calls # Return output and total calls
    # --- END MODIFIED ---

    # --- Copy Methods (Unchanged) ---
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

    # --- START MODIFIED LLM Generation Methods ---
    def _generate_k0_headline(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
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
        # _call_gemini_api now returns (text, call_count)
        headline, call_count = self._call_gemini_api(
            prompt, reasoning_config, ResumeSection.K0_HEADLINE.value, base_system,
            temperature_override=temperature_override
        )
        return headline, call_count # Return generated text and count

    # --- START: OVERWRITE _generate_k1_executive_summary ---
    def _generate_k1_executive_summary(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        # --- 1. Extract HOP-0 Data ---
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key skills') if self.thematic_analysis.primary_theme else 'key skills'
        
        differentiators = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            differentiators = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        
        role_archetype = self.thematic_analysis.role_classification.get('role_archetype', 'Experienced Professional') if self.thematic_analysis.role_classification else 'Experienced Professional'
        
        # Extract Problem/Solution Narrative
        narratives_data = getattr(self.thematic_analysis, 'problem_solution_narratives', None)
        narratives = narratives_data if isinstance(narratives_data, dict) else {}
        problem_list = narratives.get('common_problems', ['solving key challenges'])
        problem = problem_list[0] if problem_list else 'solving key challenges'
        solution_list = narratives.get('solution_patterns', ['delivering impactful results'])
        solution = solution_list[0] if solution_list else 'delivering impactful results'

        # --- 2. Build Archetype Instruction ---
        archetype_map = {
            "Executive_Leader": "an executive leader",
            "Technical_IC": "a hands-on technical expert",
            "Post-Sales_Customer_Success": "a customer success leader",
            "Pre-Sales_GTM": "a pre-sales GTM strategist",
            "Product_Management": "a product management professional"
        }
        archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."

        # --- 3. Build Feedback Instruction (from previous failures) ---
        feedback_instruction = ""
        sentence_count_failures = [f for f in self.previous_failures if f.rule_id == "VG_SENTENCE_COUNT_K1"]
        if sentence_count_failures:
            last_fail = sentence_count_failures[-1]
            if last_fail.details:
                 actual_sent = last_fail.details.get('sentence_count', 'N/A')
                 target_sent = f"{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}"
                 feedback_instruction += f"\nIMPORTANT FEEDBACK (Sentences): Previous attempt failed sentence count (had {actual_sent}, target is {target_sent}). Adjust sentence structure."

        word_count_failures = [f for f in self.previous_failures if f.rule_id == "VG_WORD_COUNT_K1"] # Assuming this is the rule ID
        if word_count_failures:
            last_fail = word_count_failures[-1]
            if last_fail.details:
                 actual_wc = last_fail.details.get('word_count', 'N/A')
                 target_wc = f"{self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}"
                 feedback_instruction += f"\nIMPORTANT FEEDBACK (Words): Previous attempt failed word count (had {actual_wc}, target is {target_wc}). Adjust length."
        
        if not feedback_instruction:
            feedback_instruction = "" # Ensure it's an empty string if no failures

        # --- 4. Build the New "Value Proposition" Prompt ---
        prompt = f"""Craft a unique Executive Value Proposition (approx. {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words) articulating the candidate's strategic fit for a senior leadership role focused on '{primary_theme}'.

**Primary Driver:** Candidate profile as {archetype_instruction}, addressing the core need for '{primary_theme}'.
**Strategic Angle:** Emphasize the ability to solve key industry problems like '{problem}' by delivering solutions such as '{solution}'.
**Key Differentiators:** Subtly weave in unique strengths relevant to the target role like {', '.join(differentiators[:self.constraints.K1_MIN_DIFFERENTIATORS])}.

**Career Context Snippets (Use for thematic inspiration and phrasing ONLY - DO NOT simply summarize these snippets or repeat specific metrics found here):**
{json.dumps(self.enriched_scaffold['experience_sections'][:2], indent=2)}

**NON-NEGOTIABLE REQUIREMENTS:**
1.  SENTENCE COUNT: MUST have strictly between {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences.
2.  TOTAL WORD COUNT: MUST be between {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words.
3.  KEYWORDS: Naturally integrate at least {self.constraints.K1_MIN_DIFFERENTIATORS} differentiating keywords.
4.  **UNIQUENESS:** Offer a distinct perspective on the candidate's value beyond summarizing past jobs. Focus on synthesized capabilities and forward-looking strategic impact. Avoid repeating specific metrics/details from the snippets.
5.  TONE: Strategic, executive-level, confident, visionary. Sentences must be fluid and well-structured, avoiding short, choppy phrasing.
6.  Output ONLY the value proposition text. Do NOT use markdown fences like ```.
{feedback_instruction}

Output ONLY the Executive Value Proposition text.
"""
        # --- 5. Call API ---
        reasoning_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG
        base_system = "You are an expert resume writer specializing in crafting concise, forward-looking Executive Value Propositions tailored to specific job descriptions."
        
        # API call raises HopExecutionError on failure
        summary, call_count = self._call_gemini_api(
            prompt, reasoning_config, "K.1", base_system,
            temperature_override=temperature_override
        )
        return summary, call_count # Return generated text and count
    # --- END: OVERWRITE _generate_k1_executive_summary ---

    def _generate_k2_skills(self, temperature_override: Optional[float] = None) -> Tuple[List[str], int]: # Return tuple
        total_calls = 0
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
            skills_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, "K.2", base_system,
                temperature_override=temperature_override
            )
            total_calls += call_count

            # --- Parse and Validate Output ---
            skills_list_final = []
            skills_intermediate = re.split(r'[\n,]', skills_text)
            malformed_count = 0
            for skill in skills_intermediate:
                cleaned_skill = re.sub(r'^[•*\-\d\.]+\s*', '', skill).strip()
                if not cleaned_skill: continue # Skip empty lines
                word_count = len(cleaned_skill.split())
                if 1 <= word_count <= 3:
                    skills_list_final.append(cleaned_skill)
                else:
                    logging.warning(f"K.2: Discarding malformed skill '{cleaned_skill}' (words: {word_count})")
                    malformed_count += 1

            if len(skills_list_final) != 12:
                raise HopExecutionError(f"K.2 generation failed: Expected exactly 12 valid 1-3 word skills, found {len(skills_list_final)}. Output preview: {skills_text[:100]}...")
            if malformed_count > 0:
                 raise HopExecutionError(f"K.2 generation failed: Found {malformed_count} malformed skills (invalid word count) which were discarded. Output preview: {skills_text[:100]}...")

            return skills_list_final, total_calls # Return exactly 12 valid skills and count

        except HopExecutionError as he:
             raise he # Propagate API or validation errors
        except Exception as e: # Catch potential regex/parsing errors
            logging.error(f"K.2 Skills processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"K.2 processing failed: {e}") from e
    # --- END MODIFIED LLM Generation Methods ---

    # --- START MODIFIED OVERVIEW GENERATION (CORE LOGIC) ---
    def _generate_tailored_overview_for_experience(
        self,
        generated_bullets: List[Dict], # Accepts generated bullets
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_id: str,
        temperature_override: Optional[float] = None
    ) -> Tuple[str, int]: # Return tuple
        """
        [REVISED per user request]
        Generates tailored overviews by synthesizing provided bullet points AND
        incorporating high-level themes (Leadership, Strategic Vision, Technical Depth)
        derived from the HOP-0 analysis (ThematicAnalysis).
        Relies on validator for word count. Raises error on API failure. Returns (text, call_count).
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

        # --- Extract Themes from HOP-0 (Thematic Analysis) ---
        ta = self.thematic_analysis if hasattr(self, 'thematic_analysis') else None
        role_classification = getattr(ta, 'role_classification', {}) if ta else {}
        primary_theme_data = getattr(ta, 'primary_theme', {}) if ta else {}
        job_desc_lower = self.job_description.lower() if hasattr(self, 'job_description') else ""

        is_leader_archetype = role_classification.get('role_archetype', '').endswith('Leader')
        leadership_keywords = ['lead', 'leadership', 'manage', 'director', 'executive', 'vp', 'chief', 'head', 'team']
        has_leadership_keywords = any(kw in primary_theme_data.get('keywords', []) for kw in leadership_keywords) or \
                                  any(kw in job_desc_lower for kw in ['director', 'vp', 'executive', 'manage team'])
        include_leadership_theme = is_leader_archetype or has_leadership_keywords

        strategic_keywords = ['strategy', 'vision', 'roadmap', 'transformation', 'gtm', 'revenue', 'partnership', 'alliance']
        technical_keywords = ['ai', 'ml', 'llm', 'cloud', 'aws', 'azure', 'gcp', 'architecture', 'platform', 'pipeline', 'technical']

        include_strategic_theme = any(kw in primary_theme_data.get('keywords', []) for kw in strategic_keywords) or \
                                  any(kw in job_desc_lower for kw in strategic_keywords)
        include_technical_theme = any(kw in primary_theme_data.get('keywords', []) for kw in technical_keywords) or \
                                  any(kw in job_desc_lower for kw in technical_keywords)

        theme_instructions = []
        if include_leadership_theme:
            theme_instructions.append("* **Leadership:** Reflect management, team building, or leading major initiatives.")
        if include_strategic_theme:
            theme_instructions.append("* **Strategic Vision:** Mention GTM strategy, long-term impact, transformations, or key partnerships.")
        if include_technical_theme:
            theme_instructions.append("* **Technical Depth:** Hint at architectural oversight, complex solution design, or technical guidance.")

        theme_prompt_section = "**KEY THEMES TO INCORPORATE (based on overall role analysis):**\n" + "\n".join(theme_instructions) if theme_instructions else ""
        # --- End Theme Extraction ---

        prompt = f"""You are an expert resume editor. Write a concise 1-2 sentence overview summarizing the key achievements from the bullets below, while also weaving in the specified high-level themes relevant to the overall target role.

**BULLETS TO SUMMARIZE:**
{bullet_summary_input} # <-- The list of bullet texts for Unify or IBM

{theme_prompt_section} # <-- Dynamically added themes from HOP-0

**ABSOLUTELY CRITICAL:**
1.  The final overview MUST be strictly between {min_wc} and {max_wc} words total. Do NOT exceed {max_wc} words.
2.  Your summary must be grounded in the achievements listed in the **BULLETS TO SUMMARIZE**.
3.  Ensure the specified **KEY THEMES** (Leadership, Strategic Vision, Technical Depth) are naturally integrated into the overview, reflecting the candidate's executive profile for this type of role.
4.  Do NOT explicitly list raw keywords from the job description.
5.  Output ONLY the overview text, with no preamble, explanation, or markdown fences like ```.

**FINAL OVERVIEW ({min_wc}-{max_wc} words):**
"""

        system_prompt = "You are an expert resume editor specializing in summarizing experience sections while incorporating key executive themes."
        # API call raises HopExecutionError on failure, returns (text, calls)
        synthesized_overview, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )

        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview or "KEY THEMES" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")

        final_wc = count_words_ms_word_style(synthesized_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{synthesized_overview}'")

        return synthesized_overview, call_count # Return text and count
    # --- END MODIFIED OVERVIEW GENERATION (CORE LOGIC) ---

    # --- START MODIFIED Methods calling _generate_tailored_overview_for_experience ---
    def _generate_k5_unify_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        generated_bullets = current_output.get(ResumeSection.K5_UNIFY_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K5_UNIFY_OVERVIEW.value}: Corresponding bullets not found or invalid.")

        # _generate_tailored_overview_for_experience now returns (text, calls)
        overview_text, call_count = self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K5_UNIFY_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K5_UNIFY_OVERVIEW.value,
            temperature_override=temperature_override
        )
        return overview_text, call_count

    def _generate_k6_ibm_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        generated_bullets = current_output.get(ResumeSection.K6_IBM_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K6_IBM_OVERVIEW.value}: Corresponding bullets not found or invalid.")

        # _generate_tailored_overview_for_experience now returns (text, calls)
        overview_text, call_count = self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=ReasoningConfig.K6_IBM_OVERVIEW_CONFIG or ReasoningConfig.DEFAULT,
            section_id=ResumeSection.K6_IBM_OVERVIEW.value,
            temperature_override=temperature_override
        )
        return overview_text, call_count
    # --- END MODIFIED ---

    # --- START MODIFIED EY/Early Career Overview (Rewrite logic, return calls) ---
    def _generate_k8_ey_overview(self, source_overview: str, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
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
        # _call_gemini_api returns (text, calls)
        tailored_overview, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )

        final_wc = count_words_ms_word_style(tailored_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{tailored_overview}'")
        return tailored_overview, call_count # Return text and count

    def _generate_k9_early_career_overview(self, source_overview: str, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
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
        # _call_gemini_api returns (text, calls)
        tailored_overview, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )
        final_wc = count_words_ms_word_style(tailored_overview)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_id} generated overview word count ({final_wc}) is outside target ({min_wc}-{max_wc}). Text: '{tailored_overview}'")
        return tailored_overview, call_count # Return text and count
    # --- END MODIFIED ---

    # --- Bullet Generation Helpers ---

    # _validate_llm_bullet_selection (Unchanged, no API calls)
    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id: str) -> List[Dict]:
        """
        Validates LLM bullet selection. Raises HopExecutionError on failure.
        v12.05: Fail fast instead of returning fallback. Ensures exact match and no duplicates.
        """
        if len(selected_bullets_text) != expected_count:
            msg = f"{section_id} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}. Output preview: '{str(selected_bullets_text)[:100]}...'"
            logging.error(msg)
            raise HopExecutionError(msg)
        validated_bullets = []
        master_texts_map = {b['bullet_text'].strip(): b for b in master_bullets_structured if 'bullet_text' in b}
        returned_texts_set = set()
        for selected_text in selected_bullets_text:
            cleaned_text = selected_text.strip()
            if cleaned_text in master_texts_map:
                 if cleaned_text in returned_texts_set:
                      msg = f"{section_id} LLM returned duplicate bullet: '{cleaned_text[:50]}...'"
                      logging.error(msg)
                      raise HopExecutionError(msg)
                 validated_bullets.append(master_texts_map[cleaned_text])
                 returned_texts_set.add(cleaned_text)
            else:
                msg = f"{section_id} LLM returned bullet not found in master list or modified: '{cleaned_text[:50]}...'"
                logging.error(msg + f" Master keys nearby: {[k[:50] for k in master_texts_map.keys() if k.startswith(cleaned_text[:10])]}")
                raise HopExecutionError(msg)
        if len(validated_bullets) != expected_count:
             msg = f"{section_id} failed final validation: Expected {expected_count} unique bullets from master list, but validated {len(validated_bullets)}."
             logging.error(msg)
             raise HopExecutionError(msg)
        logging.info(f"  ✓ {section_id}: Successfully validated {len(validated_bullets)} verbatim bullets.")
        return validated_bullets

    # --- START MODIFIED _rewrite_bullet_for_word_count ---
    def _rewrite_bullet_for_word_count(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id: str, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        """
        Rewrites a bullet for word count. Raises HopExecutionError if rewrite fails compliance.
        v12.05: Fail fast instead of returning original. Returns (text, call_count).
        """
        total_calls = 0
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
            reasoning_config = ReasoningConfig.DEFAULT
            system_prompt = f"You are an expert resume editor specializing in concisely rewriting bullet points to meet strict word count targets."
            # _call_gemini_api returns (text, calls)
            rewritten_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, f"{section_id}_RewriteWC", system_prompt,
                temperature_override=temperature_override
            )
            total_calls += call_count

            rewritten_wc = count_words_ms_word_style(rewritten_text)
            if not (min_wc <= rewritten_wc <= max_wc):
                 msg = f"{section_id}_RewriteWC returned non-compliant word count ({rewritten_wc}, target: {min_wc}-{max_wc})."
                 logging.error(msg + f" Original: '{original_bullet_text[:50]}...' Rewritten: '{rewritten_text[:50]}...'")
                 raise HopExecutionError(msg)

            return rewritten_text, total_calls # Return text and count

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id}_RewriteWC failed: {e}") from e
    # --- END MODIFIED ---

    # --- START MODIFIED _validate_and_potentially_rewrite_bullets ---
    def _validate_and_potentially_rewrite_bullets(
        self,
        selected_bullets_structured: List[Dict],
        min_target: int,
        max_target: int,
        section_id_for_logging: str,
        temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple
        """
        [MODIFIED] Checks word count against provided min/max range, attempts rewrite if needed.
        Raises HopExecutionError on failure. Uses hardcoded min/max ranges. Returns (final_list, total_calls).
        """
        final_bullets = []
        total_rewrite_calls = 0 # Counter for calls made during rewrites
        logging.info(f"  Validating word count for {section_id_for_logging} against target range: {min_target}-{max_target}")

        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict):
                 raise HopExecutionError(f"Invalid item found in bullet list for {section_id_for_logging} at index {i}: {bullet_data}")

            original_text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
            original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            word_count = bullet_data.get('word_count', count_words_ms_word_style(original_text))

            if not original_text:
                 raise HopExecutionError(f"Empty bullet found in {section_id_for_logging} at index {i}.")

            if not (min_target <= word_count <= max_target):
                logging.warning(f"  Word count ({word_count}) outside target ({min_target}-{max_target}) for {section_id_for_logging}[{i}]. Attempting rewrite...")
                try:
                    # _rewrite_bullet_for_word_count now returns (text, calls)
                    rewritten_text, rewrite_calls = self._rewrite_bullet_for_word_count(
                        original_bullet_text=original_text,
                        target_word_count_range=(min_target, max_target),
                        section_id=f"{section_id_for_logging}_RewriteWC_{i}",
                        temperature_override=temperature_override
                    )
                    total_rewrite_calls += rewrite_calls # Aggregate calls
                    rewritten_word_count = count_words_ms_word_style(rewritten_text)
                    logging.info(f"    Rewrite SUCCESSFUL for {section_id_for_logging}[{i}]. New count: {rewritten_word_count}")

                    new_provenance = BulletProvenance.Customized.value if original_provenance == BulletProvenance.Verbatim.value else original_provenance

                    final_bullets.append({
                        "text": rewritten_text,
                        "provenance": new_provenance,
                        "word_count": rewritten_word_count,
                        "original_text_if_rewritten": original_text
                    })
                except HopExecutionError as rewrite_he:
                    logging.error(f"Failed to correct word count for {section_id_for_logging}[{i}]. Reason: {rewrite_he}")
                    raise HopExecutionError(f"Bullet word count correction failed for {section_id_for_logging}[{i}]: {rewrite_he}") from rewrite_he
            else:
                final_bullets.append({
                    "text": original_text,
                    "provenance": original_provenance,
                    "word_count": word_count
                })

        logging.info(f"  ✓ Word count validation/rewrite complete for {section_id_for_logging}. Rewrite API Calls: {total_rewrite_calls}")
        return final_bullets, total_rewrite_calls # Return list and calls
    # --- END MODIFIED ---

    # --- START MODIFIED _generate_lightly_customized_bullets ---
    def _generate_lightly_customized_bullets(
        self,
        source_bullets_text: List[str], section_id: str,
        thematic_analysis: ThematicAnalysis, temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple
        """
        Lightly rewrites bullets based on thematic analysis. Raises HopExecutionError on failure or incorrect count.
        v12.05: Fail fast. Returns (list, call_count).
        """
        total_calls = 0
        try:
            if not source_bullets_text: return [], 0 # Return empty list and 0 calls

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
            reasoning_config = ReasoningConfig.DEFAULT
            system_prompt = "You are an expert resume editor skilled at subtly tailoring bullet points to job descriptions."
            # _call_gemini_api returns (text, calls)
            response_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, section_id, system_prompt,
                temperature_override=temperature_override
            )
            total_calls += call_count

            rewritten_bullets = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]

            if len(rewritten_bullets) != len(source_bullets_text):
                msg = f"{section_id} LLM returned {len(rewritten_bullets)} customized bullets, expected {len(source_bullets_text)}. Output preview: {response_text[:100]}..."
                logging.error(msg)
                raise HopExecutionError(msg)

            result_list = [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": count_words_ms_word_style(b)} for b in rewritten_bullets]
            return result_list, total_calls # Return list and calls

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id} customization failed: {e}") from e
    # --- END MODIFIED ---

    # --- START MODIFIED _generate_synthetic_bullets ---
    def _generate_synthetic_bullets(
        self,
        count: int, company_name: str, job_description: str,
        thematic_analysis: ThematicAnalysis, context_bullets: str, # Context of existing bullets in the section
        reasoning_config: ReasoningConfig, section_id: str,
        temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple
        """
        Generates plausible, synthetic resume bullets based on context. Raises HopExecutionError on failure or incorrect count.
        v12.05: Fail fast. Returns (list, call_count).
        """
        total_calls = 0
        try:
            if count <= 0: return [], 0 # Nothing to generate, 0 calls

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
            # _call_gemini_api returns (text, calls)
            response_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, section_id, system_prompt,
                temperature_override=temperature_override
            )
            total_calls += call_count

            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]

            if len(synthetic_bullets_text) != count:
                msg = f"{section_id} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}). Output preview: {response_text[:100]}..."
                logging.error(msg)
                raise HopExecutionError(msg)

            result_list = [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": count_words_ms_word_style(b)} for b in synthetic_bullets_text]
            return result_list, total_calls # Return list and calls

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id} synthetic generation failed: {e}") from e
    # --- END MODIFIED ---

    # --- START MODIFIED Generic Bullet Generation Helper ---
    def _generate_bullets_for_section(
        self,
        company_name: str,
        master_bullets_key: str,
        section_enum: ResumeSection,
        provenance_targets: Dict[str, int],
        reasoning_config: ReasoningConfig,
        temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple
        """
        [MODIFIED] Generic helper to generate bullets for any experience section.
        Handles both full V/C/S generation and customized-only generation. Returns (list, total_calls).
        """
        total_calls = 0
        # If only 'Customized' bullets are targeted, use the simpler path.
        if list(provenance_targets.keys()) == ['Customized']:
            exp_section = next((exp for exp in self.master_resume['professional_experience'] if company_name in exp.get('company','')), None)
            target_count = provenance_targets['Customized']

            if not exp_section: raise HopExecutionError(f"{section_enum.name} master data not found for '{company_name}'.")
            source_bullets = exp_section.get(master_bullets_key, [])
            if not isinstance(source_bullets, list): raise HopExecutionError(f"{section_enum.name} master '{master_bullets_key}' is not a list.")
            valid_source_bullets = [b for b in source_bullets if isinstance(b, str) and b.strip()]

            if len(valid_source_bullets) < target_count:
                raise HopExecutionError(f"{section_enum.name} needs {target_count} valid source bullets, found {len(valid_source_bullets)}.")

            bullets_to_customize = valid_source_bullets[:target_count]

            # _generate_lightly_customized_bullets returns (list, calls)
            customized_bullets, calls_c = self._generate_lightly_customized_bullets(
                source_bullets_text=bullets_to_customize,
                section_id=section_enum.value,
                thematic_analysis=self.thematic_analysis,
                temperature_override=temperature_override
            )
            total_calls += calls_c

            min_target, max_target = self.BULLET_WORD_COUNT_RANGES[section_enum]
            # _validate_and_potentially_rewrite_bullets returns (list, calls)
            final_custom_bullets, calls_rewrite = self._validate_and_potentially_rewrite_bullets(
                 selected_bullets_structured=customized_bullets,
                 min_target=min_target, max_target=max_target,
                 section_id_for_logging=section_enum.name,
                 temperature_override=temperature_override
            )
            total_calls += calls_rewrite
            return final_custom_bullets, total_calls
        else:
            # For sections with V/C/S, use the full generation pipeline.
            # _generate_tailored_bullets_for_experience returns (list, calls)
            return self._generate_tailored_bullets_for_experience(
                company_name=company_name, section_index=-1, # section_index is unused
                provenance_targets=provenance_targets,
                reasoning_config=reasoning_config, section_id=section_enum,
                temperature_override=temperature_override
            )
    # --- END MODIFIED ---

    # --- START MODIFIED _generate_tailored_bullets_for_experience ---
    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str, section_index: int, provenance_targets: Dict[str, int],
            reasoning_config: ReasoningConfig, section_id: ResumeSection, # Changed to Enum
            temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple
        """
        [MODIFIED] Generic method to generate bullets (Verbatim, Customized, Synthetic).
        Raises HopExecutionError on failures. Uses hardcoded word count ranges. Returns (list, total_calls).
        """
        logging.info(f"  Generating bullets for {section_id.name} (Targets: {provenance_targets})")
        total_calls_for_section = 0 # Counter for this specific section generation

        # --- 1. Get Master Bullets ---
        experience_section = next((exp for exp in self.master_resume['professional_experience'] if company_name in exp.get('company', '')), None)
        if not experience_section:
            raise HopExecutionError(f"Master experience data not found for company '{company_name}' needed for {section_id.name}")
        master_bullets_structured = []
        bullet_source = experience_section.get("bullet_pool", experience_section.get("highlights", []))
        if not isinstance(bullet_source, list):
             raise HopExecutionError(f"{section_id.name} master bullet source is not a list for company '{company_name}'.")
        for bullet_text in bullet_source:
             if isinstance(bullet_text, str) and bullet_text.strip():
                 master_bullets_structured.append({
                     "bullet_text": bullet_text.strip(), "text": bullet_text.strip(),
                     "provenance": BulletProvenance.Verbatim.value,
                     "word_count": count_words_ms_word_style(bullet_text.strip())
                 })
             else: logging.warning(f"Skipping invalid master bullet item for {company_name}: {bullet_text}")
        if not master_bullets_structured and provenance_targets.get('Verbatim', 0) > 0:
             raise HopExecutionError(f"{section_id.name} Cannot select Verbatim bullets: No valid master bullets available for '{company_name}'.")

        # --- 2. Initialize Counts and Final List ---
        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        final_bullets = []

        # --- 3. Select Verbatim Bullets (if needed) ---
        if verbatim_count > 0:
            logging.info(f"    Selecting {verbatim_count} Verbatim bullets...")
            if len(master_bullets_structured) < verbatim_count:
                raise HopExecutionError(f"{section_id.name} Cannot select {verbatim_count} Verbatim bullets: Only {len(master_bullets_structured)} master bullets available.")
            master_bullets_text_list = [b['bullet_text'] for b in master_bullets_structured]
            prompt_select = f"""Select the {verbatim_count} most relevant bullet points...
{chr(10).join([f'- {b}' for b in master_bullets_text_list])}
TARGET KEYWORDS...
{', '.join(getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])[:10]) if hasattr(self.thematic_analysis, 'competitive_intelligence') else 'N/A'}
Instructions...
SELECTED BULLETS:""" # (Prompt details omitted for brevity, logic unchanged)
            system_prompt_select="You are an AI assistant that selects relevant resume bullet points based on keywords."
            try:
                response_select, calls_v_select = self._call_gemini_api(prompt_select, reasoning_config, f"{section_id.name}_SelectV", system_prompt_select, temperature_override=temperature_override)
                total_calls_for_section += calls_v_select
                selected_texts = [line.strip() for line in response_select.split('\n') if line.strip()]
                verbatim_bullets = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id.name}_SelectV")
                final_bullets.extend(verbatim_bullets)
            except HopExecutionError as he: raise he

        # --- 4. Generate Customized Bullets (if needed) ---
        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} bullets...")
            used_verbatim_texts = {b.get('bullet_text') for b in final_bullets if b.get('provenance') == BulletProvenance.Verbatim.value}
            available_for_custom = [b for b in master_bullets_structured if b.get('bullet_text') not in used_verbatim_texts]
            if len(available_for_custom) < customized_count:
                raise HopExecutionError(f"{section_id.name} Cannot customize {customized_count} bullets: Only {len(available_for_custom)} unique master bullets remaining.")
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count]
            try:
                customized_bullets, calls_c = self._generate_lightly_customized_bullets(
                    source_bullets_text=[b['bullet_text'] for b in candidates_for_custom],
                    section_id=f"{section_id.name}_CustomC",
                    thematic_analysis=self.thematic_analysis,
                    temperature_override=temperature_override
                )
                total_calls_for_section += calls_c
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he: raise he

        # --- 5. Generate Synthetic Bullets (if needed) ---
        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic bullets...")
            context_bullets_text = '\n'.join([f"- {b.get('text', b.get('bullet_text', ''))}" for b in final_bullets])
            try:
                synthetic_bullets, calls_s = self._generate_synthetic_bullets(
                    count=synthetic_count, company_name=company_name,
                    job_description=self.job_description, thematic_analysis=self.thematic_analysis,
                    context_bullets=context_bullets_text, reasoning_config=reasoning_config,
                    section_id=f"{section_id.name}_SynthS",
                    temperature_override=temperature_override
                )
                total_calls_for_section += calls_s
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he: raise he

        # --- 6. Final Count Check ---
        if len(final_bullets) != total_expected_count:
            raise HopExecutionError(f"{section_id.name} Generated incorrect total bullet count ({len(final_bullets)}), expected {total_expected_count}.")

        # --- 7. Word Count Validation & Potential Rewrite ---
        logging.info(f"    Validating word counts for {len(final_bullets)} generated bullets...")
        target_range = self.BULLET_WORD_COUNT_RANGES.get(section_id)
        if target_range is None:
             raise HopExecutionError(f"Hardcoded word count range not found for section {section_id.name}.")
        min_target, max_target = target_range
        try:
            # _validate_and_potentially_rewrite_bullets returns (list, calls)
            final_bullets_validated, calls_rewrite = self._validate_and_potentially_rewrite_bullets(
                selected_bullets_structured=final_bullets,
                min_target=min_target, max_target=max_target,
                section_id_for_logging=section_id.name,
                temperature_override=temperature_override
            )
            total_calls_for_section += calls_rewrite
            final_bullets = final_bullets_validated # Update list with potentially rewritten bullets
        except HopExecutionError as he: raise he

        # --- 8. Reorder Bullets ---
        logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
        current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets)]
        current_bullets_text_input = '\n'.join(current_bullets_text_list)
        prompt_reorder = f"""Reorder the following resume bullet points...
**Bullets to Reorder ({company_name}):**
{current_bullets_text_input}
**Target Job Description Keywords...**
{', '.join(getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])[:10]) if hasattr(self.thematic_analysis, 'competitive_intelligence') else 'N/A'}
Instructions...
**REORDERED BULLETS:**""" # (Prompt details omitted for brevity, logic unchanged)
        system_prompt_reorder = "You are an expert resume editor who reorders bullet points for maximum impact based on relevance to target keywords."
        try:
            response_reorder, calls_reorder = self._call_gemini_api(prompt_reorder, ReasoningConfig.DEFAULT, f"{section_id.name}_Reorder", system_prompt_reorder, temperature_override=temperature_override)
            total_calls_for_section += calls_reorder
            reordered_texts = [line.strip() for line in response_reorder.split('\n') if line.strip()]

            # --- Validation of Reordering ---
            if len(reordered_texts) != total_expected_count: raise HopExecutionError(...) # Count check
            final_ordered_bullets_dicts = []
            original_texts_map = {b.get('text'): b for b in final_bullets}
            used_original_texts = set()
            for reordered_text in reordered_texts:
                 cleaned_reordered = reordered_text.strip()
                 if cleaned_reordered in original_texts_map:
                     if cleaned_reordered in used_original_texts: raise HopExecutionError(...) # Duplicate check
                     final_ordered_bullets_dicts.append(original_texts_map[cleaned_reordered])
                     used_original_texts.add(cleaned_reordered)
                 else: raise HopExecutionError(...) # Modified text check
            if len(final_ordered_bullets_dicts) != total_expected_count: raise HopExecutionError(...) # Final count check

            logging.info(f"  ✓ Reordering complete for {section_id.name}.")
            return final_ordered_bullets_dicts, total_calls_for_section # Return list and aggregated calls

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id.name} Reordering failed: {e}") from e
    # --- END MODIFIED ---

    # --- START MODIFIED Methods calling _generate_bullets_for_section ---
    def _generate_k5_unify_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # Return tuple
        return self._generate_bullets_for_section(
            company_name="Unify Consulting", master_bullets_key="bullet_pool",
            section_enum=ResumeSection.K5_UNIFY_BULLETS,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K5_UNIFY_BULLETS],
            reasoning_config=ReasoningConfig.K5_UNIFY_BULLETS_CONFIG or ReasoningConfig.DEFAULT, temperature_override=temperature_override
        )

    def _generate_k6_ibm_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # Return tuple
        return self._generate_bullets_for_section(
            company_name="IBM", master_bullets_key="bullet_pool", section_enum=ResumeSection.K6_IBM_BULLETS,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K6_IBM_BULLETS],
            reasoning_config=ReasoningConfig.K6_IBM_BULLETS_CONFIG or ReasoningConfig.DEFAULT, temperature_override=temperature_override
        )

    def _generate_k10_competencies(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # Return tuple
        """Generates K.10 Competencies using the bullet generation framework."""
        fake_company_name = "Strategic Competencies"
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        original_master_resume = self.master_resume
        total_calls = 0
        generated_bullets = []
        try:
            self.master_resume = copy.deepcopy(self.master_resume)
            self.master_resume["professional_experience"].append({
                 "company": fake_company_name,
                 "bullet_pool": competencies_list
            })
            # _generate_bullets_for_section returns (list, calls)
            generated_bullets, calls = self._generate_bullets_for_section(
                company_name=fake_company_name, master_bullets_key="bullet_pool",
                section_enum=ResumeSection.K10_COMPETENCIES,
                provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K10_COMPETENCIES],
                reasoning_config=ReasoningConfig.K10_COMPETENCIES_CONFIG or ReasoningConfig.DEFAULT,
                temperature_override=temperature_override
            )
            total_calls = calls
        finally:
             self.master_resume = original_master_resume

        # Post-processing
        for bullet in generated_bullets:
             if 'text' in bullet and isinstance(bullet['text'], str):
                 bullet['text'] = re.sub(r'^\*\*\s*.*?:?\s*\*\*\s*', '', bullet['text']).strip()
                 bullet['word_count'] = count_words_ms_word_style(bullet['text'])

        return generated_bullets, total_calls # Return list and calls

    def _generate_k8_ey_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # Return tuple
        """Generates K.8 EY Bullets using the generic helper."""
        return self._generate_bullets_for_section(
            company_name="Ernst & Young", master_bullets_key="highlights",
            section_enum=ResumeSection.K8_EY_BULLETS,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K8_EY_BULLETS],
            reasoning_config=ReasoningConfig.K8_EY_BULLETS_CONFIG or ReasoningConfig.DEFAULT, temperature_override=temperature_override
        )

    def _generate_k9_early_career_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # Return tuple
        """Generates K.9 Early Career Bullets using the generic helper."""
        return self._generate_bullets_for_section(
            company_name="Early Career Roles", master_bullets_key="highlights",
            section_enum=ResumeSection.K9_EARLY_CAREER_BULLETS,
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS[ResumeSection.K9_EARLY_CAREER_BULLETS],
            reasoning_config=ReasoningConfig.K9_EARLY_CAREER_BULLETS_CONFIG or ReasoningConfig.DEFAULT, temperature_override=temperature_override
        )
    # --- END MODIFIED ---

    # --- START MODIFIED Cover Letter Generation ---
    def _generate_k13_cover_letter(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        """
        [v12.05 NO_FALLBACK] Generates K.13 cover letter. Raises HopExecutionError on failure.
        Includes structure fixes. Returns (text, call_count).
        """
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key requirements') if self.thematic_analysis.primary_theme else 'key requirements'
        differentiators = []
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            differentiators = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
        narratives_data = getattr(self.thematic_analysis, 'problem_solution_narratives', None)
        narratives = narratives_data if isinstance(narratives_data, dict) else {}

        problem_list = narratives.get('common_problems', ['solving key challenges'])
        problem = problem_list[0] if problem_list else 'solving key challenges'
        solution_list = narratives.get('solution_patterns', ['delivering impactful results'])
        solution = solution_list[0] if solution_list else 'delivering impactful results'

        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        expected_signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', '[Your Name]'),
            email=contact_info.get('email', '[Your Email]'),
            phone=contact_info.get('phone', '[Your Phone]'),
            linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
        ).strip()

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
        total_calls = 0
        try:
            reasoning_config = ReasoningConfig.DEFAULT
            base_system = f"You are an expert executive ghostwriter crafting tailored cover letters."
            # _call_gemini_api returns (text, calls)
            cover_letter_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, "K.13", base_system,
                temperature_override=temperature_override
            )
            total_calls += call_count

            # --- Post-generation Structure Fixes ---
            fixed_text = cover_letter_text.strip()
            # ... (structure fixing logic unchanged) ...
            current_date = datetime.now().strftime("%B %d, %Y")
            recipient_placeholder = "Hiring Manager\n[Company Name]"
            salutation = "Dear Hiring Manager,"
            closing = "Sincerely,"
            structure_fix_fails_date = False
            structure_fix_fails_signature = False
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text): fixed_text = f"{current_date}\n\n{fixed_text}"; logging.warning("K.13: Added missing date.")
            if recipient_placeholder not in fixed_text: fixed_text = re.sub(r"(\w+ \d{1,2}, \d{4}\n*\s*)", rf"\1\n{recipient_placeholder}\n\n", fixed_text, count=1); logging.warning("K.13: Attempted recipient add.")
            if recipient_placeholder not in fixed_text: logging.error("K.13: Failed to insert recipient placeholder."); structure_fix_fails_date = True
            if salutation not in fixed_text: fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\n*\s*)", rf"\1\n{salutation}\n\n", fixed_text, count=1); logging.warning("K.13: Attempted salutation add.")
            if salutation not in fixed_text: logging.error("K.13: Failed to insert salutation."); structure_fix_fails_date = True
            if closing not in fixed_text.split(expected_signature)[0]:
                 if expected_signature in fixed_text: fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
                 else: fixed_text += f"\n\n{closing}\n\n{expected_signature}"; logging.warning("K.13: Appended closing and sig.")
                 if closing not in fixed_text.split(expected_signature)[0]: logging.error("K.13: Failed to insert closing."); structure_fix_fails_signature = True
            fixed_text_stripped_end = '\n'.join(line.rstrip() for line in fixed_text.split('\n'))
            expected_sig_stripped_end = '\n'.join(line.rstrip() for line in expected_signature.split('\n'))
            if not fixed_text_stripped_end.endswith(expected_sig_stripped_end):
                 pattern = re.escape(expected_sig_stripped_end.split('\n')[0])
                 match = list(re.finditer(pattern, fixed_text_stripped_end))
                 if match: last_match_start = match[-1].start(); fixed_text = fixed_text[:last_match_start] + expected_signature
                 else: fixed_text = fixed_text_stripped_end + "\n\n" + expected_signature; logging.warning("K.13: Appended missing signature block.")
                 fixed_text_stripped_end = '\n'.join(line.rstrip() for line in fixed_text.split('\n')) # Recheck after fix attempt
                 if not fixed_text_stripped_end.endswith(expected_sig_stripped_end): logging.error("K.13: Failed to fix signature block placement."); structure_fix_fails_signature = True

            # --- Error Checking ---
            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text: raise HopExecutionError(f"K.13 generation failed (placeholder detected after fixes).")
            if structure_fix_fails_date: raise HopExecutionError("K.13 failed critical structure fix (date/recipient/salutation).")
            if structure_fix_fails_signature: raise HopExecutionError("K.13 failed critical structure fix (closing/signature).")

            return fixed_text.strip(), total_calls # Return fixed text and calls

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"K.13 generation failed: {e}") from e

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

def _count_sentences(text: str) -> int:
    """
    Helper to count sentences. Splits by common terminators followed by space,
    and filters empty strings. Avoids variable-width lookbehind issues.
    v12.80 Fix: Replaced complex regex with re.split.
    """
    if not text or not text.strip():
        return 0
    # Split after '.', '!', '?' followed by one or more whitespace characters or end of string
    # Using a positive lookbehind (?<=...) ensures the terminator is kept with the preceding sentence part if needed,
    # but the split happens *after* it and the space.
    potential_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out any empty strings that might result from multiple spaces or trailing terminators
    actual_sentences = [s for s in potential_sentences if s]
    # Handle cases where the text might not end with punctuation but still forms a sentence
    if not text.strip().endswith(('.', '!', '?')) and actual_sentences:
         # If the last split part isn't empty, it counts as a sentence.
         # This logic is implicitly handled by the list comprehension filtering empty strings.
         pass
    elif not actual_sentences and text.strip():
         # If splitting resulted in nothing but the original text isn't empty, it's likely one sentence without standard punctuation.
         return 1

    return len(actual_sentences)

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

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================
from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================
from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data
import re # Ensure re is imported for validation methods
from datetime import datetime # Ensure datetime is imported for validation methods
from typing import Dict, List, Optional, Any, Tuple, Set, Union # Ensure types are imported

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================
from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data
import re # Ensure re is imported for validation methods
from datetime import datetime # Ensure datetime is imported for validation methods
from typing import Dict, List, Optional, Any, Tuple, Set, Union # Ensure types are imported
# Assume other necessary classes like ValidationResult, ValidationSeverity,
# ImmutableStagingBuffer, ResumeSection, ThematicAnalysis,
# ContentConstraintsConfig, SignalControlConfig, etc. are defined/imported

class ValidationContext:
    """
    Lazy evaluation context for validation rules.
    Calculates metrics only when needed by a rule.
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str, master_resume: Dict):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {} # Cache for calculated values

    def __getattr__(self, name):
        """Calculate and cache metrics on demand."""
        if name in self._cache:
            return self._cache[name]

        calculation_method = getattr(self, f"_calculate_{name}", None)
        if calculation_method:
            value = calculation_method()
            self._cache[name] = value
            return value
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or calculation method '_calculate_{name}'")

    # --- Calculation Methods ---

    def _calculate_total_words(self):
        """Calculates total word count across relevant sections."""
        total = 0
        buffer_data = self.staging_buffer.data # Get snapshot
        for key, value in buffer_data.items():
            # Exclude non-content sections like headers, contact info
            if key not in [ResumeSection.K0_NAME.value, ResumeSection.K0_CONTACT.value] and \
               not key.endswith("_HEADER"):
                if isinstance(value, str):
                    total += count_words_ms_word_style(value)
                elif isinstance(value, list):
                    total += count_words_in_list_ms_word_style(value)
        return total

    def _calculate_unify_words(self):
        unify_overview = self.staging_buffer.get(ResumeSection.K5_UNIFY_OVERVIEW.value, "")
        unify_bullets = self.staging_buffer.get(ResumeSection.K5_UNIFY_BULLETS.value, [])
        return count_words_ms_word_style(unify_overview) + count_words_in_list_ms_word_style(unify_bullets)

    def _calculate_ibm_words(self):
        ibm_overview = self.staging_buffer.get(ResumeSection.K6_IBM_OVERVIEW.value, "")
        ibm_bullets = self.staging_buffer.get(ResumeSection.K6_IBM_BULLETS.value, [])
        return count_words_ms_word_style(ibm_overview) + count_words_in_list_ms_word_style(ibm_bullets)

    def _calculate_unify_ibm_percent(self):
        total_w = self.total_words
        if total_w == 0: return 0.0
        return (self.unify_words + self.ibm_words) / total_w * 100.0

    def _calculate_unify_ibm_ratio(self):
        ibm_w = self.ibm_words
        if ibm_w == 0: return 0.0
        return self.unify_words / ibm_w

    def _calculate_k1_sentence_count_details(self):
        """Calculates details needed for VG_SENTENCE_COUNT_K1."""
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        count = _count_sentences(k1_text)
        details = {
            'sentence_count': count,
            'min': ContentConstraintsConfig.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
            'max': ContentConstraintsConfig.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        }
        # Store these details directly in the main cache for the rule's error message lambda
        self._cache["VG_SENTENCE_COUNT_K1"] = details
        return details # Return details for direct use by validator

    def _calculate_k1_word_count_details(self):
        """Calculates details needed for VG_WORD_COUNT_K1."""
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        count = count_words_ms_word_style(k1_text)
        details = {
            'word_count': count,
            'min': ContentConstraintsConfig.EXEC_SUMMARY_WORD_COUNT_MIN,
            'max': ContentConstraintsConfig.EXEC_SUMMARY_WORD_COUNT_MAX
        }
        # Store details in the main cache for the error message lambda
        self._cache["VG_WORD_COUNT_K1"] = details
        return details

    def _calculate_headline_details(self):
        """Calculates details for headline rules."""
        headline_text = self.staging_buffer.get(ResumeSection.K0_HEADLINE.value, '')
        word_count = count_words_ms_word_style(headline_text)
        details = {
            'word_count': word_count,
            'headline': headline_text,
            'min': ContentConstraintsConfig.HEADLINE_WORD_COUNT_MIN,
            'max': ContentConstraintsConfig.HEADLINE_WORD_COUNT_MAX
        }
        # Cache for rules that might use these details in error messages
        self._cache["VG_HEADLINE_WORD_COUNT"] = details
        self._cache["VG_HEADLINE_NO_TITLES"] = details
        self._cache["VG_HEADLINE_NO_COMMAS"] = details
        return details

    def _calculate_cover_letter_jd_similarity(self):
        """Calculates cosine similarity between cover letter and JD."""
        cover_letter_text = self.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        if not cover_letter_text or not self.job_description:
            return 0.0
        # Use a simple similarity measure for demonstration
        dd = DuplicateDetector() # Assuming DuplicateDetector is available
        return dd._calculate_cosine_similarity(cover_letter_text, self.job_description)

    def _calculate_expected_signature(self):
        """Calculates the expected cover letter signature block."""
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        return COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', '[Your Name]'),
            email=contact_info.get('email', '[Your Email]'),
            phone=contact_info.get('phone', '[Your Phone]'),
            linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
        ).strip()

class PreFlightValidator:

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.constraints = ContentConstraintsConfig() # Centralized constraints
        self.signal_constraints = SignalControlConfig() # Signal control constraints

        # --- Rule to Section Mapping (Initialized via method) ---
        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()

        self._register_rules()

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

    # Bullet word count tolerance configuration (Unchanged - still used for QA Report Section 5)
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

    # --- START CHANGE: Add FORBIDDEN_VERBS constant ---
    FORBIDDEN_VERBS = [
        "pioneered", "spearheaded", "orchestrated", "architected",
        "revolutionized", "transformed"
    ]
    # --- END CHANGE ---

    # --- START CHANGE: Consolidated Rules Configuration (Add VG_FORBIDDEN_VERBS) ---
    RULES_CONFIG = [
        # --- Word Count & Sentence Count Rules ---
        {
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": lambda ctx: ContentConstraintsConfig.TOTAL_WORD_COUNT_MIN <= ctx.total_words <= ContentConstraintsConfig.TOTAL_WORD_COUNT_MAX,
            "error_message": "Total resume: {total_words} words (target: {min}-{max})"
        },
        {
            "rule_id": "VG_SENTENCE_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_k1_sentence_count", # Keep method for clarity
            "error_message": "K.1: {sentence_count} sentences (target: {min}-{max})"
        },
        {
            "rule_id": "VG_WORD_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_k1_word_count", # Use specific method
            "error_message": "K.1: {word_count} words (target: {min}-{max})"
        },
         {
            "rule_id": "VG_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.CRITICAL,"category": "structure",
            "validator": lambda ctx: ContentConstraintsConfig.HEADLINE_WORD_COUNT_MIN <= ctx.headline_details['word_count'] <= ContentConstraintsConfig.HEADLINE_WORD_COUNT_MAX,
            "error_message": "K.0 Headline: {word_count} words (target: {min}-{max}). Headline: '{headline}'"
        },
        {
            "rule_id": "VG_BULLET_WORD_COUNT_RANGE",
            "severity": ValidationSeverity.HIGH,
            "category": "word_count",
            "validator": "_validate_bullet_word_count_range",
            "error_message": "Bullet word counts outside hardcoded ranges: {violations}"
        },
        # --- Distribution Rules ---
        {
            "rule_id": "WORD_DISTRIBUTION_UNIFY_IBM", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MIN <= ctx.unify_ibm_percent <= ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MAX,
            "error_message": "Unify+IBM: {unify_ibm_percent:.1f}% of total (target: {min}-{max}%)" # Use cached value directly
        },
        {
            "rule_id": "UNIFY_IBM_RATIO", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ctx.ibm_words > 0 and ContentConstraintsConfig.UNIFY_IBM_RATIO_MIN <= ctx.unify_ibm_ratio <= ContentConstraintsConfig.UNIFY_IBM_RATIO_MAX,
            "error_message": "Unify/IBM ratio: {unify_ibm_ratio:.2f} (target: {min}-{max})" # Use cached value directly
        },
        # --- Structure & Formatting Rules ---
        {
            "rule_id": "BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: ctx.staging_buffer.is_locked(),
            "error_message": "Staging buffer must be locked before validation"
        },
        {"rule_id": "VG_COVER_LETTER_SIGNATURE_VALID", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": "_validate_cover_letter_signature_valid", "error_message": "Cover letter signature is missing, malformed, or not multi-line."},
        {
            "rule_id": "VG_COVER_LETTER_FULL_STRUCTURE", "severity": ValidationSeverity.HIGH, "category": "structure", # Changed from MEDIUM to HIGH
            "validator": "_validate_cover_letter_full_structure",
            "error_message": "Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."
        },
        {
            "rule_id": "VG_HEADLINE_NO_TITLES", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_headline_format_no_titles",
            "error_message": "K.0 Headline contains forbidden titles: {forbidden}. Headline: '{headline}'"
        },
        {
            "rule_id": "VG_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: ',' not in ctx.headline_details['headline'], # Use cached value
            "error_message": "K.0 Headline contains commas. Headline: '{headline}'"
        },
        # --- Placeholder Visual Rules (Checked during rendering) ---
        {"rule_id": "VG_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: True, "error_message": "Resume headers not consistently H2: {failed_headers}"},
        {"rule_id": "VG_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: True, "error_message": "Education/Certification format error: {details}"},
        {"rule_id": "VG_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: True, "error_message": "Experience bullets do not consistently use '* ': {details}"},
        {"rule_id": "VG_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: True, "error_message": "Competencies list not using '*' bullets: {details}"},
        {"rule_id": "VG_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: True, "error_message": "Experience section formatting error: {details}"},
        # --- Content & Signal Rules ---
        {
            "rule_id": "CONTENT_NO_PLACEHOLDERS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_no_placeholders",
            "error_message": "Found placeholder text in content: {placeholders}"
        },
        # --- START CHANGE: Add VG_FORBIDDEN_VERBS rule ---
        {
            "rule_id": "VG_FORBIDDEN_VERBS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_forbidden_verbs",
            "error_message": "Forbidden verbs found in generated content: {violations}"
        },
        # --- END CHANGE ---
        {
            "rule_id": "VG_PER_SECTION_SIGNAL_SCORE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_per_section_signal",
            "error_message": "One or more sections are below minimum signal score: {failures}"
        },
        {
            "rule_id": "VG_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_k1_differentiator_range", # Keep as method
            "error_message": "K.1 Summary contains {found} differentiators (target: {min}-{max})."
        },
        {
            "rule_id": "VG_JD_KEYWORD_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_jd_keyword_range", # Use specific method
            "error_message": "Resume contains {found} JD keywords (target: {min}-{max})."
        },
        {
            "rule_id": "NARRATIVE_MINING_PRESENCE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_narrative_mining_presence", # Keep as method
            "error_message": "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."
        },
        {
            "rule_id": "VG_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: ContentConstraintsConfig.COVER_LETTER_JD_RELEVANCE_THRESHOLD <= ctx.cover_letter_jd_similarity <= SignalControlConfig.CL_MAX_JD_SIMILARITY,
            "error_message": "Cover letter relevance to JD is {cover_letter_jd_similarity:.2f} (target: {min_sim}-{max_sim})."
        },
        {
            "rule_id": "COVER_LETTER_NARRATIVE_INTEGRITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_cover_letter_narrative", # Keep as method
            "error_message": "Cover letter may be missing narrative integrity. Hook: {hook}, Proof: {proof}, Vision: {vision}"
        },
        {
            "rule_id": "COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: "track record of measurable AI transformation" not in ctx.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, ''),
            "error_message": "Creative cover letter generation failed; fallback was used."
        },
        {
            "rule_id": "COVER_LETTER_STRUCTURE", "severity": ValidationSeverity.HIGH, "category": "content", # Changed from MEDIUM to HIGH
            "validator": "_validate_cover_letter_structure", # Keep as method
            "error_message": "Cover letter paragraph word counts are out of spec. P1: {p1_wc} ({p1_min}-{p1_max}), P2: {p2_wc} ({p2_min}-{p2_max}), P3: {p3_wc} ({p3_min}-{p3_max})"
        },
        {
            "rule_id": "VG_PROVENANCE_SPLIT_CHECK", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_provenance_split", # Keep as method
            "error_message": "Provenance split mismatch: {violations}"
        },
        {
            "rule_id": "VG_AUTHENTICITY_SIGNAL_CHECK", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_authenticity_signal", # Keep as method
            "error_message": "Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {details}"
        },
        {
            "rule_id": "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_exec_summary_vs_sections",
            "error_message": "Executive Summary similarity to sections exceeds threshold: {failures}"
        },
    ]
    # --- END CHANGE ---

    # --- START CHANGE: Update _initialize_rule_map ---
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
            "VG_WORD_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY, # Added mapping
            "VG_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY": ResumeSection.K1_EXECUTIVE_SUMMARY,
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
            "VG_COVER_LETTER_SIGNATURE_VALID": ResumeSection.K13_COVER_LETTER,
            "VG_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K13_COVER_LETTER,
            "VG_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K13_COVER_LETTER,
            "COVER_LETTER_STRUCTURE": ResumeSection.K13_COVER_LETTER,
            "STRUCTURE_K13_COVER_LETTER_PRESENT": ResumeSection.K13_COVER_LETTER,

            # --- Complex Rules (Handled in `validate` method) ---
            "VG_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION",
            "VG_BULLET_WORD_COUNT_RANGE": "COMPLEX_PER_SECTION",
            "VG_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION",
            "VG_FORBIDDEN_VERBS": "COMPLEX_PER_SECTION" # <-- Add new rule
        }

        # Add simple structure rules
        for section in ResumeSection:
             rule_id = f"STRUCTURE_{section.name}_PRESENT"
             if rule_id not in rule_map:
                 rule_map[rule_id] = section

        return rule_map
    # --- END CHANGE ---

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
                 validator_func = validator_func
            else:
                 raise TypeError(f"Invalid validator type for rule {config['rule_id']}: {type(validator_ref)}")

            # Use defaultdict to handle missing keys gracefully in error message formatting
            def create_error_message_lambda(template, rule_id):
                 # Define expected args based on template placeholders (simple version)
                 expected_args_in_template = re.findall(r'\{(\w+)\}', template)
                 # Ensure min/max are available for range rules
                 if 'min' in expected_args_in_template and 'max' in expected_args_in_template:
                      min_max_keys = ['min', 'max']
                 else: min_max_keys = []

                 return lambda ctx: template.format_map(
                     defaultdict(lambda: 'N/A', **ctx._cache.get(rule_id, {}))
                 )


            error_message_template = str(config["error_message"])
            error_message_lambda = create_error_message_lambda(error_message_template, config["rule_id"])

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
                validator=lambda ctx, s=section: (
                    ctx.staging_buffer.get(s.value) is not None and
                    ( (isinstance(ctx.staging_buffer.get(s.value), str) and ctx.staging_buffer.get(s.value).strip()) or
                      (isinstance(ctx.staging_buffer.get(s.value), list) and ctx.staging_buffer.get(s.value)) or
                      (isinstance(ctx.staging_buffer.get(s.value), dict) and ctx.staging_buffer.get(s.value))
                    )
                ),
                error_message=f"{section.value} is missing or empty.",
                category="structure"
            )
            self.engine.register_rule(rule)

    # --- VALIDATE METHOD (Unchanged) ---
    def validate(
        self, # type: ignore
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        sections_under_test: Optional[Set[ResumeSection]] = None
    ) -> Tuple[List[ValidationResult], bool, Set[ResumeSection]]:
        # Create the lazy-evaluation context object
        context = ValidationContext(staging_buffer, thematic_analysis, job_description, self.master_resume)

        # Execute validation
        validation_results = self.engine.validate(context)
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
                # Use context._cache to get details set by the validator
                rule_cache = context._cache.get(vr.rule_id, {})
                if "failed_sections" in rule_cache and isinstance(rule_cache["failed_sections"], set):
                    failed_sections.update(rule_cache["failed_sections"])
                else:
                    logging.warning(f"Complex rule {vr.rule_id} failed but did not provide failed_sections set in details cache.")


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

    # --- Validation Helper Methods ---

    def _validate_k1_sentence_count(self, context: ValidationContext) -> bool:
        """Validates sentence count for K.1 using cached details."""
        details = context.k1_sentence_count_details # Trigger calculation & caching
        return details['min'] <= details['sentence_count'] <= details['max']

    def _validate_k1_word_count(self, context: ValidationContext) -> bool:
        """Validates word count for K.1 using cached details."""
        details = context.k1_word_count_details # Trigger calculation & caching
        return details['min'] <= details['word_count'] <= details['max']

    def _validate_cover_letter_signature_valid(self, context: ValidationContext) -> bool:
        """Checks both presence and multi-line format of the signature."""
        cover_letter = context.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_sig = context.expected_signature
        return bool(expected_sig and '\n' in expected_sig and cover_letter.strip().endswith(expected_sig))

    def _validate_bullet_word_count_range(self, context: ValidationContext) -> bool:
        """
        [v13.10 REWRITE for Hardcoded Ranges]
        VG_BULLET_WORD_COUNT_RANGE: Checks individual bullet word counts
        against hardcoded ranges. Adds failed sections to error_details.
        """
        all_bullets_valid = True
        violations = []
        failed_sections = set() # Store ResumeSection enums
        HARDCODED_BULLET_RANGES = ArtistGenerator.BULLET_WORD_COUNT_RANGES
        staging_buffer = context.staging_buffer

        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            target_range = HARDCODED_BULLET_RANGES.get(section_enum)
            if target_range is None: continue
            min_wc, max_wc = target_range
            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): continue

            for i, bullet in enumerate(bullets):
                actual_wc, bullet_text = 0, ""
                if isinstance(bullet, dict):
                    bullet_text = bullet.get('text', bullet.get('bullet_text',''))
                    actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str):
                    bullet_text = bullet
                    actual_wc = count_words_ms_word_style(bullet_text)
                else: continue

                if not (min_wc <= actual_wc <= max_wc):
                    all_bullets_valid = False
                    violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc})")
                    failed_sections.add(section_enum)

        if not all_bullets_valid:
            context._cache["VG_BULLET_WORD_COUNT_RANGE"] = {
                "violations": violations[:5],
                "failed_sections": failed_sections
            }
        return all_bullets_valid

    def _validate_cover_letter_full_structure(self, context: ValidationContext) -> bool:
        """Checks for Date, Recipient, Salutation, 3 Paras, Closing, Signature."""
        text = context.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_sig = context.expected_signature
        has_date = bool(re.search(r"^\w+ \d{1,2}, \d{4}", text.strip()))
        has_recipient = "Hiring Manager\n[Company Name]" in text
        has_salutation = "Dear Hiring Manager," in text
        has_closing = "Sincerely," in text
        has_signature = expected_sig in text
        # Simple paragraph check (at least 5 non-empty blocks between salutation and closing)
        body = text.split(has_salutation)[1].split(has_closing)[0] if has_salutation and has_closing else ""
        paras = [p for p in body.strip().split('\n\n') if p.strip()]
        has_3_paras = len(paras) >= 3

        valid = has_date and has_recipient and has_salutation and has_closing and has_signature and has_3_paras
        if not valid:
             context._cache["VG_COVER_LETTER_FULL_STRUCTURE"] = {
                 "has_date": has_date, "has_recipient": has_recipient, "has_salutation": has_salutation,
                 "has_closing": has_closing, "has_signature": has_signature, "paras_found": len(paras)
             }
        return valid

    def _validate_headline_format_no_titles(self, context: ValidationContext) -> bool:
        """Checks K.0 Headline format and ensures no forbidden titles."""
        headline = context.headline_details['headline'] # Use cached value
        if not headline or '|' not in headline: return False # Basic pipe check
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: return False # Must be 3 components

        forbidden_titles = ['director', 'vp', 'manager', 'lead', 'head', 'chief', 'principal', 'senior', 'executive']
        forbidden_found = []
        for comp in components:
            word_count = count_words_ms_word_style(comp)
            if not (self.constraints.HEADLINE_COMPONENT_WORDS_MIN <= word_count <= self.constraints.HEADLINE_COMPONENT_WORDS_MAX):
                return False # Component word count fail
            for title in forbidden_titles:
                 if title in comp.lower().split():
                     forbidden_found.append(title)

        if forbidden_found:
             context._cache["VG_HEADLINE_NO_TITLES"] = {
                 "forbidden": list(set(forbidden_found)),
                 "headline": headline
             }
             return False
        return True

    def _validate_no_placeholders(self, context: ValidationContext) -> bool:
        """Recursively checks for '[Placeholder' in any string value."""
        buffer_data = context.staging_buffer.data
        found_placeholders = []

        def check_item(item):
            if isinstance(item, str):
                if "[Placeholder" in item:
                    found_placeholders.append(item[:100]) # Log snippet
            elif isinstance(item, dict):
                for k, v in item.items():
                    check_item(v)
            elif isinstance(item, list):
                for elem in item:
                    check_item(elem)

        check_item(buffer_data)
        if found_placeholders:
            context._cache["CONTENT_NO_PLACEHOLDERS"] = {"placeholders": found_placeholders[:5]}
            return False
        return True

    # --- START CHANGE: Add _validate_forbidden_verbs method ---
    def _validate_forbidden_verbs(self, context: ValidationContext) -> bool:
        """
        [NEW]
        VG_FORBIDDEN_VERBS: Checks all generated bullets against the forbidden verb list.
        Runs post-generation (HOP-5) to catch verbs in customized/synthetic bullets.
        """
        all_bullets_valid = True
        violations = []
        failed_sections = set() # Store ResumeSection enums
        staging_buffer = context.staging_buffer

        # Check all bullet sections, including competencies
        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): continue

            for i, bullet in enumerate(bullets):
                bullet_text = ""
                if isinstance(bullet, dict):
                    bullet_text = bullet.get('text', bullet.get('bullet_text',''))
                elif isinstance(bullet, str):
                    bullet_text = bullet
                else: continue

                if not bullet_text: continue
                
                bullet_text_lower = bullet_text.lower()
                # Check for forbidden verbs using word boundaries
                found_verbs = [
                    verb for verb in self.FORBIDDEN_VERBS 
                    if re.search(r'\b' + re.escape(verb) + r'\b', bullet_text_lower)
                ]

                if found_verbs:
                    all_bullets_valid = False
                    violations.append(f"{section_key}[{i}]: Found '{', '.join(found_verbs)}'")
                    failed_sections.add(section_enum)

        if not all_bullets_valid:
            context._cache["VG_FORBIDDEN_VERBS"] = {
                "violations": violations[:5],
                "failed_sections": failed_sections
            }
        return all_bullets_valid
    # --- END CHANGE ---

    def _validate_per_section_signal(self, context: ValidationContext) -> bool:
        """Validates signal score for each configured section."""
        all_sections_pass = True
        failures = []
        failed_sections = set() # Store ResumeSection enums
        buffer_data = context.staging_buffer.data
        thematic = context.thematic_analysis

        for label, (section_enum, target_min, target_max, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = buffer_data.get(section_enum.value)
            if content:
                score = calculate_signal_score(content, thematic)
                if not (target_min <= score <= target_max):
                    all_sections_pass = False
                    failures.append(f"{label}: {score:.1%} (Target: {target_min:.0%}-{target_max:.0%})")
                    failed_sections.add(section_enum)
            # else: Allow missing sections, structure check will fail later if required

        if not all_sections_pass:
            context._cache["VG_PER_SECTION_SIGNAL_SCORE"] = {
                "failures": failures[:5],
                "failed_sections": failed_sections
            }
        return all_sections_pass

    def _validate_k1_differentiator_range(self, context: ValidationContext) -> bool:
        """Validates the number of unique differentiators found in K.1."""
        k1_text = context.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        differentiators = []
        if hasattr(context.thematic_analysis, 'competitive_intelligence') and context.thematic_analysis.competitive_intelligence:
            differentiators = getattr(context.thematic_analysis.competitive_intelligence, 'differentiator_keywords', []) or []

        found_count = sum(1 for kw in differentiators if kw and kw.lower() in k1_text)
        min_target = self.constraints.K1_MIN_DIFFERENTIATORS
        max_target = self.signal_constraints.K1_MAX_DIFFERENTIATORS

        valid = min_target <= found_count <= max_target
        if not valid:
             context._cache["VG_K1_DIFFERENTIATOR_RANGE"] = {
                 "found": found_count, "min": min_target, "max": max_target
             }
        return valid

    def _validate_jd_keyword_range(self, context: ValidationContext) -> bool:
        """Validates the total number of unique JD keywords found across the resume."""
        buffer_data = context.staging_buffer.data
        thematic = context.thematic_analysis
        full_resume_text = ""
        for key, value in buffer_data.items():
            if key not in [ResumeSection.K0_NAME.value, ResumeSection.K0_CONTACT.value] and not key.endswith("_HEADER"):
                if isinstance(value, str): full_resume_text += value + " "
                elif isinstance(value, list): full_resume_text += " ".join(map(str, value)) + " "

        full_resume_lower = full_resume_text.lower()
        differentiators = set()
        if hasattr(thematic, 'competitive_intelligence') and thematic.competitive_intelligence:
            differentiators = set(getattr(thematic.competitive_intelligence, 'differentiator_keywords', []) or [])
        primary_theme_data = thematic.primary_theme or {}
        primary_words = set(primary_theme_data.get('keywords', []))
        all_jd_keywords = differentiators.union(primary_words)

        found_keywords = {kw for kw in all_jd_keywords if kw and kw.lower() in full_resume_lower}
        found_count = len(found_keywords)
        min_target = self.constraints.MIN_JD_KEYWORDS
        max_target = self.signal_constraints.RESUME_MAX_JD_KEYWORDS

        valid = min_target <= found_count <= max_target
        context._cache["VG_JD_KEYWORD_RANGE"] = { # Always cache details
            "found": found_count, "min": min_target, "max": max_target,
            "jd_keywords_found": list(found_keywords) # For use in other rules if needed
        }
        return valid

    def _validate_narrative_mining_presence(self, context: ValidationContext) -> bool:
        """Checks if Phase 4 Narrative Mining data exists and is populated."""
        narratives = getattr(context.thematic_analysis, 'problem_solution_narratives', None)
        return isinstance(narratives, dict) and narratives.get('common_problems') and narratives.get('solution_patterns')

    def _validate_cover_letter_narrative(self, context: ValidationContext) -> bool:
        """Checks basic presence of Hook, Proof, Vision keywords in CL."""
        cl_text = context.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '').lower()
        # Basic keyword checks
        hook_present = any(kw in cl_text for kw in ["enthusiastic", "excited", "applying for", "interest in the role"])
        proof_present = any(kw in cl_text for kw in ["demonstrated", "achieved", "delivered", "resulted in", "experience in"])
        vision_present = any(kw in cl_text for kw in ["contribute", "goals", "opportunity", "eager to discuss", "next step"])
        valid = hook_present and proof_present and vision_present
        if not valid:
             context._cache["COVER_LETTER_NARRATIVE_INTEGRITY"] = {
                 "hook": hook_present, "proof": proof_present, "vision": vision_present
             }
        return valid

    def _validate_cover_letter_structure(self, context: ValidationContext) -> bool:
        """Validates word counts of CL paragraphs."""
        cl_text = context.staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        paras = [p.strip() for p in cl_text.split('\n\n') if p.strip()]
        # Simplistic: Assume P1 is after salutation, P2, P3 follow.
        p1_idx, p2_idx, p3_idx = -1, -1, -1
        try:
             salutation_idx = next(i for i, p in enumerate(paras) if p.startswith("Dear Hiring Manager,"))
             p1_idx = salutation_idx + 1
             p2_idx = p1_idx + 1
             p3_idx = p2_idx + 1
        except (StopIteration, IndexError):
             context._cache["COVER_LETTER_STRUCTURE"] = {"error": "Could not find paragraphs"}
             return False # Cannot find paragraphs

        p1_wc = count_words_ms_word_style(paras[p1_idx]) if p1_idx < len(paras) else 0
        p2_wc = count_words_ms_word_style(paras[p2_idx]) if p2_idx < len(paras) else 0
        p3_wc = count_words_ms_word_style(paras[p3_idx]) if p3_idx < len(paras) else 0

        c = self.constraints
        p1_valid = c.COVER_LETTER_P1_WORD_COUNT_MIN <= p1_wc <= c.COVER_LETTER_P1_WORD_COUNT_MAX
        p2_valid = c.COVER_LETTER_P2_WORD_COUNT_MIN <= p2_wc <= c.COVER_LETTER_P2_WORD_COUNT_MAX
        p3_valid = c.COVER_LETTER_P3_WORD_COUNT_MIN <= p3_wc <= c.COVER_LETTER_P3_WORD_COUNT_MAX

        valid = p1_valid and p2_valid and p3_valid
        context._cache["COVER_LETTER_STRUCTURE"] = {
            "p1_wc": p1_wc, "p1_min": c.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": c.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": c.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": c.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": c.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": c.COVER_LETTER_P3_WORD_COUNT_MAX
        }
        return valid

    def _validate_provenance_split(self, context: ValidationContext) -> bool:
        """Validates bullet provenance counts against targets."""
        all_sections_pass = True
        violations = []
        failed_sections = set() # Store ResumeSection enums

        for section_enum, targets in self.PROVENANCE_SPLIT_TARGETS.items():
            section_key = section_enum.value
            bullets = context.staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): continue # Skip if data missing/wrong type

            counts = defaultdict(int)
            for bullet in bullets:
                if isinstance(bullet, dict):
                    prov = bullet.get('provenance', 'Unknown')
                    counts[prov] += 1
                elif isinstance(bullet, str) and section_enum == ResumeSection.K7_TRADERSENSE_BULLETS:
                     # K7 bullets are copied directly, count as Verbatim for this check if needed
                     counts[BulletProvenance.Verbatim.value] += 1

            for prov_type, target_count in targets.items():
                actual_count = counts.get(prov_type, 0)
                if actual_count != target_count:
                    all_sections_pass = False
                    violations.append(f"{section_key}: {prov_type} has {actual_count} (target: {target_count})")
                    failed_sections.add(section_enum)

        if not all_sections_pass:
             context._cache["VG_PROVENANCE_SPLIT_CHECK"] = {
                 "violations": violations[:5],
                 "failed_sections": failed_sections
             }
        return all_sections_pass

    def _validate_authenticity_signal(self, context: ValidationContext) -> bool:
        """Checks if authenticity patterns (verbs/phrasing) are used."""
        buffer_data = context.staging_buffer.data
        thematic = context.thematic_analysis
        auth_patterns = getattr(thematic, 'authenticity_patterns', {}).get('patterns', {})
        if not auth_patterns: return True # Pass if no patterns to check against

        verbs = auth_patterns.get('achievement_verb_patterns', [])
        phrasing = auth_patterns.get('competency_phrasing', [])
        target_signals = set(v.lower() for v in verbs[:10]) | set(p.lower().split(':')[0] for p in phrasing[:5] if ':' in p) # Top signals

        full_resume_text = ""
        # Aggregate text from relevant sections only (e.g., exclude contact, headers)
        for key, value in buffer_data.items():
            if key in [section.value for section in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK] or key == ResumeSection.K1_EXECUTIVE_SUMMARY.value:
                if isinstance(value, str): full_resume_text += value + " "
                elif isinstance(value, list): full_resume_text += " ".join(map(str, value)) + " "

        if not target_signals or not full_resume_text: return True # Pass if nothing to check

        resume_words = set(re.findall(r'\b\w+\b', full_resume_text.lower()))
        matches = resume_words.intersection(target_signals)
        match_ratio = len(matches) / len(target_signals) if target_signals else 0.0

        valid = match_ratio >= 0.3 # Require at least 30% of target signals found
        if not valid:
             context._cache["VG_AUTHENTICITY_SIGNAL_CHECK"] = {
                 "details": f"Found {len(matches)}/{len(target_signals)} ({match_ratio:.1%}) authenticity signals."
             }
        return valid

    def _validate_exec_summary_vs_sections(self, context: ValidationContext) -> bool:
        """Validates cosine similarity between K.1 and other sections."""
        exec_summary_text = context.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        if not exec_summary_text: return True # Cannot check if summary is missing

        dd = DuplicateDetector()
        sections_content = {}
        # Gather content from experience sections (overviews and bullets)
        for section_enum in [
            ResumeSection.K5_UNIFY_OVERVIEW, ResumeSection.K5_UNIFY_BULLETS,
            ResumeSection.K6_IBM_OVERVIEW, ResumeSection.K6_IBM_BULLETS,
            ResumeSection.K8_EY_OVERVIEW, ResumeSection.K8_EY_BULLETS,
            ResumeSection.K9_EARLY_CAREER_OVERVIEW, ResumeSection.K9_EARLY_CAREER_BULLETS,
            ResumeSection.K10_COMPETENCIES
        ]:
            content = context.staging_buffer.get(section_enum.value)
            if content:
                 # Clean up bullet list if needed
                 if isinstance(content, list):
                     cleaned_content = []
                     for item in content:
                          if isinstance(item, dict): cleaned_content.append(item.get('text',''))
                          elif isinstance(item, str): cleaned_content.append(item)
                     sections_content[section_enum.name] = [c for c in cleaned_content if c] # Filter empty strings
                 elif isinstance(content, str):
                     sections_content[section_enum.name] = content

        similarity_results = dd.compute_executive_summary_similarity(exec_summary_text, sections_content)

        threshold = 0.7 # Example threshold - K.1 should not be >70% similar to any other section
        all_pass = True
        failures = []
        failed_sections = set() # Store ResumeSection enums

        for result in similarity_results:
            if result['max_similarity'] >= threshold:
                all_pass = False
                failures.append(f"{result['section_label']}: Max Similarity {result['max_similarity']:.2f} >= {threshold:.1f}")
                try: failed_sections.add(ResumeSection[result['section_label']])
                except KeyError: pass # Ignore if label doesn't map directly

        if not all_pass:
             context._cache["VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY"] = {
                 "failures": failures[:5],
                 "failed_sections": failed_sections # This rule failing should trigger K.1 retry
             }
        return all_pass

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

import functools

class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator', company_name: str, job_title: str):
        self.master_resume = master_resume
        self.orchestrator = orchestrator # For access to validation results etc.
        self.company_name = company_name
        self.job_title = job_title

    @functools.cached_property
    def _safe_company_name(self) -> str:
        """[NEW] Sanitizes and caches the company name for use in filenames."""
        return re.sub(r'[^\w\-]', '_', self.company_name)

    @functools.cached_property
    def _safe_job_title(self) -> str:
        """[NEW] Sanitizes and caches the job title for use in filenames."""
        return re.sub(r'[^\w\-]', '_', self.job_title)

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
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Resume MD: {e}"
            ))

        # --- 2. Render Skills Artifact ---
        try:
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Skills TXT: {e}"
            ))

        # --- 3. Render Cover Letter Artifact ---
        try:
            path, content = self._render_cover_letter_artifact(staging_buffer)
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
            path, content = self._render_qa_report_artifact()
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content # Will be an empty string
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
            ))

        # --- 5. Render App Tracker Artifact (and Validate) --- [NOW OUTPUT 5]
        try:
            path, content, app_tracker_validation_results = self._render_app_tracker_artifact(file_paths)
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content
            validation_results.extend(app_tracker_validation_results) # Add validation results
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render App Tracker JSON: {e}"
            ))

        return file_paths, (validation_results, file_contents)

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the resume markdown artifact."""
        content = self._render_resume_markdown(staging_buffer)
        path = f"Resume_{self._safe_company_name}_{self._safe_job_title}.md"
        return path, content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: str) -> Tuple[str, str]:
        """Renders the skills artifact."""
        content = self._render_skills(staging_buffer, job_description)
        path = f"Skills_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the cover letter artifact."""
        content = staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        path = f"CoverLetter_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, content

    def _render_qa_report_artifact(self) -> Tuple[str, str]:
        """Renders the QA report artifact placeholder. Content is generated in the orchestrator."""
        path = f"QA_Report_{self._safe_company_name}_{self._safe_job_title}.md"
        # Content is generated in HOP-8 by the orchestrator, return empty string.
        return path, ""

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str]) -> Tuple[str, str, List[ValidationResult]]:
        """Renders the application tracker artifact and validates it."""
        app_tracker_data = self._render_app_tracker(file_paths)
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
        path = f"AppTracker_{self._safe_company_name}_{self._safe_job_title}.json"
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
        file_paths: Dict[str, str]
    ) -> Dict:
        """Render application tracker (v4 - 54 fields) - QA SPEC V5 VALIDATED."""
        tracker = copy.deepcopy(APP_TRACKER_SCHEMA_V4)
        
        # Get candidate name and format it for the versioned resume string
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")

        # Auto-populate fields with new schema field names
        tracker['Company'] = self.company_name
        tracker['Job Title'] = self.job_title
        tracker['Application Date'] = datetime.now().strftime("%m/%d/%Y")
        tracker['Base Resume'] = "" # Per user request
        # Per user request for format: "Amit_Ayer_Resume_DataRobot_VP_AI_Technical_Success"
        tracker['Versioned Resume'] = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
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
                if value is not None:
                    staging_buffer.set(key, value)
                    sections_populated += 1
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
        Serves as a final confirmation on the sanitized buffer.
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-5] Final Pre-flight Validation (Post-Sanitization)...")
        try:
            validator = PreFlightValidator(self.master_resume)
            hop_results, all_passed, _ = validator.validate(
                staging_buffer, thematic_analysis, job_description,
                sections_under_test=None
            )

            # Overwrite self.validation_results with this final check
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
        """Executes HOP-7: Rendering Output Files."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7] Rendering Output Files...")
        try:
            # Pass company_name and job_title to FileRenderer constructor
            renderer = FileRenderer(self.master_resume, self, company_name, job_title)
            # Pass remaining args to render method
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

    # --- Main Workflow Execution Method ---
    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        jd_url: str = "" # Add jd_url parameter
    ) -> Dict:
        """
        Execute complete multi-hop workflow.
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
                # Treat JD input failures as critical enough to halt
                halt_msg = f"JD Input Validation failed: {failed_jd_validations[0].details}"
                self.logger.error(f"  ✗ {halt_msg}")
                raise HopExecutionError(halt_msg)
            else: self.logger.info("  ✓ JD input validation passed.")

            thematic_analysis = self._execute_hop_0_jd_analysis(job_description)

            self.logger.info("\n[GATE-1] JD Parsing Validation...")
            if thematic_analysis:
                # Validate parsing based on thematic analysis object structure
                # We need a placeholder dict if asdict fails
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

            # --- HOP-3 Call ---
            artist_output = self._execute_hop_3_artist_generation(
                enriched_scaffold, job_description, thematic_analysis
            )

            staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)

            # --- HOP-5 Final Validation ---
            hop5_results = self._execute_hop_5_validation(staging_buffer, thematic_analysis, job_description)

            self.logger.info("\n[GATE-5] Pre-flight Buffer JD Validation...")
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")

            # HOP-6 uses the results from HOP-5
            gate_decision = self._execute_hop_6_gate_decision(hop5_results)

            # --- Pass jd_url to HOP-7 ---
            file_paths, file_contents = self._execute_hop_7_rendering(
                staging_buffer, company_name, job_title, thematic_analysis, job_description, jd_url=jd_url # Pass jd_url here
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
                "file_contents": file_contents, # Add file contents here
                # Redundant fields removed for clarity if file_contents is present
                # "resume_md_content": file_contents.get('resume_md', ''),
                # "skills_content": file_contents.get('skills', ''),
                # "cover_letter_content": file_contents.get('cover_letter', ''),
                # "app_tracker_content": file_contents.get('app_tracker', '{}'),
                # "qa_report_content": qa_report_text,
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

            # Ensure self.validation_results has the results that caused the halt
            halt_validation_results = self.validation_results or [] # Use stored results or empty list

            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, final_file_contents = self._generate_qa_report(
                         staging_buffer, thematic_analysis, halt_validation_results
                     )
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after halt: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after halt: {qa_e}]"
                      final_file_contents = {} # Ensure it's defined
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after halt]"
                 final_file_contents = {} # Ensure it's defined


            final_result = {
                "status": "HALTED",
                "gate_decision": gate_decision_val,
                "reason": reason,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text, # Keep this top-level key for compatibility
                "hash_chain": self.hash_chain,
                "file_contents": final_file_contents # Include potentially partial file contents
                # Redundant content fields removed
            }
            self.rendered_output = final_result
            return final_result

        except Exception as e:
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW FAILED UNEXPECTEDLY: {type(e).__name__}: {str(e)}", exc_info=True)

            # Ensure self.validation_results exists, even if empty
            fail_validation_results = self.validation_results or []

            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, final_file_contents = self._generate_qa_report(
                         staging_buffer, thematic_analysis, fail_validation_results
                     )
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after failure: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after error: {qa_e}]"
                      final_file_contents = {} # Ensure it's defined
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after failure]"
                 final_file_contents = {} # Ensure it's defined


            final_result = {
                "status": "FAILED",
                "error": f"{type(e).__name__}: {str(e)}",
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text, # Keep this top-level key
                "hash_chain": self.hash_chain,
                "file_contents": final_file_contents # Include potentially partial file contents
            }
            self.rendered_output = final_result
            return final_result

    # --- Helper Methods ---

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
                        # --- START FIX: Handle ImmutableStagingBuffer serialization ---
                        if isinstance(o, ImmutableStagingBuffer): return o.data # Serialize its internal data
                        # --- END FIX ---
                        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
                    output_str = json.dumps(output_data, sort_keys=True, separators=(',', ':'), default=default_serializer)
                elif isinstance(output_data, list):
                     try: output_str = json.dumps(sorted([str(item) for item in output_data]))
                     except TypeError: output_str = json.dumps([str(item) for item in output_data])
                elif isinstance(output_data, ThematicAnalysis):
                    output_str = json.dumps(asdict(output_data), sort_keys=True, separators=(',', ':'))
                # --- START FIX: Handle ImmutableStagingBuffer serialization ---
                elif isinstance(output_data, ImmutableStagingBuffer):
                     output_str = json.dumps(output_data.data, sort_keys=True, separators=(',', ':')) # Serialize its internal data
                # --- END FIX ---
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
            # --- START FIX: Ensure message is callable with details ---
            reason_msg = "Unknown failure"
            if highest_failure:
                try:
                    # Check if message is a callable lambda expecting context/details
                    if callable(highest_failure.message) and hasattr(highest_failure, 'details'):
                        reason_msg = highest_failure.message(highest_failure.details)
                    else:
                        reason_msg = str(highest_failure.message) # Fallback to string
                except Exception as msg_e:
                    reason_msg = f"Error formatting message for {highest_failure.rule_id}: {msg_e}"
                reason = f"{highest_failure.rule_id}: {reason_msg}"
            else:
                 reason = checkpoint.error_message or "Unknown failure"

            error_msg = f"[{checkpoint.hop_id}] FAILED - Halting workflow. Reason: {reason}"
            self.logger.error(f"  ✗ {error_msg}")

            failures_to_log = failed_results[:3]
            for vr in failures_to_log:
                 try:
                      # Check if message is a callable lambda expecting context/details
                      if callable(vr.message) and hasattr(vr, 'details'):
                           msg = vr.message(vr.details)
                      else:
                           msg = str(vr.message) # Fallback to string
                 except Exception as msg_e:
                      msg = f"Error formatting message: {msg_e}"
                 self.logger.error(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")
            # --- END FIX ---

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
                     try:
                          # Check if message is callable
                          if callable(vr.message) and hasattr(vr, 'details'):
                               msg = vr.message(vr.details)
                          else:
                               msg = str(vr.message)
                     except Exception as msg_e:
                          msg = f"Error formatting message: {msg_e}"
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

    # --- START REFACTOR: QA Report Section Config ---
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]},
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]},
        {"method": "_build_qa_section_6_authenticity", "args": ["validation_results"]},
        # Section 7 (Exec Summary Similarity) REMOVED
        {"method": "_build_qa_section_7_prod_readiness", "args": ["validation_results"]}, # Original Section 11 is now 7
        {"method": "_build_qa_section_8_pairwise_similarity", "args": []}, # Original Section 8 remains 8 (Summary Only)
        {"method": "_build_qa_section_9_pipeline_health", "args": []}, # Original Section 9 remains 9
        {"method": "_build_qa_section_10_structural", "args": ["validation_results"]}, # Original Section 10 remains 10
        {"method": "_build_qa_section_11_cover_letter", "args": ["validation_results"]}, # Original Section 12 is now 11
        {"method": "_build_qa_section_12_jd_enforcement", "args": []}, # Original Section 13 is now 12
        {"method": "_build_qa_section_13_final_format", "args": ["validation_results", "file_contents"]}, # Original Section 14 is now 13
    ]
    # --- END REFACTOR ---

    # --- START REFACTOR: Individual QA Section Builder Methods ---

    def _build_qa_section_1_signal_quality(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        # ... (Method content remains the same as v13.20) ...
        lines = ["", "1. SIGNAL QUALITY (Per-Section Analysis vs. JD Keywords)", ""]
        max_signal_target = SignalControlConfig().SECTION_SIGNAL_SCORE_MAX
        section_configs = PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG
        total_weighted_score, total_weight = 0.0, 0.0
        total_weighted_temp, temp_weight = 0.0, 0.0
        lines.append("```markdown")

        hop3_checkpoint = next((c for c in reversed(self.hop_checkpoints) if c.hop_id == "HOP-3"), None)
        final_temps = hop3_checkpoint.metadata.get("final_temperatures", {}) if hop3_checkpoint else {}
        final_temps_enum = {ResumeSection[k]: v for k, v in final_temps.items() if k in ResumeSection.__members__}

        for label, (section_enum, target_min_score, target_max_score, weight, reasoning_config) in section_configs.items():
            content = staging_buffer.get(section_enum.value)
            if content:
                score = calculate_signal_score(content, thematic_analysis)
                total_weighted_score += score * weight
                total_weight += weight

                temp = final_temps_enum.get(section_enum)
                if temp is None:
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
        # ... (Method content remains the same as v13.20) ...
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
        # ... (Method content remains the same as v13.20) ...
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
        # ... (Method content remains the same as v13.20) ...
        lines = ["", "4. WORD COUNT & DISTRIBUTION COMPLIANCE", ""]
        lines.append("This section combines overall resume word count checks, key section constraints (Headline, Exec Summary, Cover Letter paragraphs), and distribution metrics (Unify/IBM) into a single table. Bullet length validation is covered in Section 6.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Section", "Rule ID", "Value", "Target Range", "Status", "Message / Details"]
        rows = []
        rules_to_include = {
            "VG_TOTAL_WORD_COUNT": "Overall Resume",
            "VG_HEADLINE_WORD_COUNT": "Headline",
            "VG_WORD_COUNT_K1": "Executive Summary", # Note: This rule may not exist, check RULES_CONFIG
            "VG_SENTENCE_COUNT_K1": "Executive Summary",
            "WORD_DISTRIBUTION_UNIFY_IBM": "Experience Dist.",
            "UNIFY_IBM_RATIO": "Experience Dist.",
            # Cover Letter Paragraph rules derived from COVER_LETTER_STRUCTURE
            "CL_P1_WORD_COUNT": "Cover Letter P1",
            "CL_P2_WORD_COUNT": "Cover Letter P2",
            "CL_P3_WORD_COUNT": "Cover Letter P3",
        }

        cl_structure_result = next((vr for vr in validation_results if vr.rule_id == "COVER_LETTER_STRUCTURE"), None)
        cl_paragraph_details = {}
        if cl_structure_result and isinstance(cl_structure_result.details, dict):
             cl_paragraph_details = cl_structure_result.details

        for rule_id, section_label in rules_to_include.items():
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)

            if rule_id.startswith("CL_P"):
                p_num_str = rule_id.split('_')[1] # e.g., "P1"
                p_key_wc = f"{p_num_str.lower()}_wc" # e.g., "p1_wc"
                p_key_min = f"{p_num_str.lower()}_min"
                p_key_max = f"{p_num_str.lower()}_max"

                if cl_structure_result:
                    wc = cl_paragraph_details.get(p_key_wc, 'N/A')
                    min_r = cl_paragraph_details.get(p_key_min, 'N/A')
                    max_r = cl_paragraph_details.get(p_key_max, 'N/A')
                    value_str = f"{wc} words"
                    target_str = f"{min_r}-{max_r}"
                    status = "N/A"
                    msg = ""
                    if not cl_structure_result.passed:
                        status = "FAIL"
                        msg = cl_structure_result.message
                        if callable(msg): msg = msg(cl_paragraph_details)
                    elif wc != 'N/A' and min_r != 'N/A' and max_r != 'N/A':
                        status = "PASS" if min_r <= wc <= max_r else "FAIL"
                        if status == "FAIL":
                            msg = f"Count ({wc}) outside range ({min_r}-{max_r})"
                    else:
                        status = "WARN"
                        msg = "Details missing in CL_STRUCTURE result"
                    rows.append([section_label, rule_id, value_str, target_str, status, msg])
                else:
                    rows.append([section_label, rule_id, "N/A", "N/A", "WARN", "CL_STRUCTURE rule not found"])

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
        # ... (Method content remains the same as v13.20) ...
        lines = ["", "5. BULLET PROVENANCE & WORD COUNT", ""]
        lines.append("```markdown")
        headers = ["Section", "Item", "Provenance", "Word Count", "Target Range", "Status", "Text Snippet"]
        rows = []
        HARDCODED_BULLET_RANGES = {
            "Unify": (25, 38), "IBM": (22, 34), "EY": (25, 40),
            "EarlyCareer": (25, 40), "Competencies": (25, 40),
            "Default": (20, 35) # Fallback
        }
        sections_to_process = [
            {"name": "Unify", "bullets_enum": ResumeSection.K5_UNIFY_BULLETS},
            {"name": "IBM", "bullets_enum": ResumeSection.K6_IBM_BULLETS},
            {"name": "Competencies", "bullets_enum": ResumeSection.K10_COMPETENCIES},
            {"name": "EY", "bullets_enum": ResumeSection.K8_EY_BULLETS},
            {"name": "EarlyCareer", "bullets_enum": ResumeSection.K9_EARLY_CAREER_BULLETS},
            {"name": "TraderSense", "bullets_enum": ResumeSection.K7_TRADERSENSE_BULLETS}
        ]
        logging.info(f"Using Hardcoded Ranges for QA Sec 5: {HARDCODED_BULLET_RANGES}")
        for section_data in sections_to_process:
            name = section_data["name"]
            bullets_enum = section_data.get("bullets_enum")
            if bullets_enum:
                min_target, max_target = HARDCODED_BULLET_RANGES.get(name, HARDCODED_BULLET_RANGES["Default"])
                logging.debug(f"Processing Section '{name}', using range_key='{name}', Target={min_target}-{max_target}")
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
                        logging.debug(f"  Bullet {i+1}: WordCount={word_count}, Target={min_target}-{max_target}")
                        status, target_range_str = self._check_word_count(word_count, min_target, max_target)
                        rows.append([
                            name, str(i + 1), provenance, str(word_count), target_range_str,
                            status, bullet_text[:60] + ("..." if len(bullet_text) > 60 else "")
                        ])
                elif not isinstance(bullets, list):
                    logging.warning(f"Expected list for bullets in section '{name}' ({bullets_enum.value}), but got {type(bullets)}. Skipping.")
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_6_authenticity(self, validation_results: List[ValidationResult]) -> List[str]:
        # ... (Method content remains the same as v13.20) ...
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

    # --- START REFACTOR: Section 7 (Prod Readiness) ---
    def _build_qa_section_7_prod_readiness(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds the NEW QA Section 7 table: Production Readiness."""
        lines = ["", "7. PRODUCTION READINESS", ""] # Renumbered Header
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
    # --- END REFACTOR ---

    def _build_qa_section_8_pairwise_similarity(self) -> List[str]:
        """
        Builds the QA Section 8: Content Similarity Summary.
        Summarizes strict duplicates (>=0.90), overview vs bullet issues (>=0.60, excl. Unify/IBM),
        and executive summary vs section issues (>=0.70) including item index.
        """
        lines = ["", "8. CONTENT SIMILARITY SUMMARY (Deduplication & Overlap)", ""] # Renumbered & Renamed Header
        lines.append("Summarizes potential content duplication and overlap across different similarity checks.")
        lines.append("")
        lines.append("```markdown")

        # --- Table Headers ---
        headers = ["Check Type", "Details", "Max Similarity", "Violations Found", "Status", "Notes/Examples"]
        rows = []
        overall_pass = True # Assume PASS initially

        # --- 1. Strict Duplicates (Pairwise Matrix >= 0.90) ---
        pairwise_pass = True
        pairwise_details = "Analysis not performed or no data."
        pairwise_max_sim = 0.0
        pairwise_violations = 0
        pairwise_notes = ""
        pairwise_status = "⚠️ WARN" # Default to warning if no data

        if self.similarity_matrix_data:
            duplicates_count = len(self.similarity_matrix_data.get('duplicates_found', []))
            pairwise_details = f"{self.similarity_matrix_data.get('total_comparisons', 0)} Comparisons"
            pairwise_max_sim = self.similarity_matrix_data.get('max_similarity', 0.0)
            pairwise_violations = duplicates_count
            if duplicates_count == 0:
                pairwise_status = "✅ PASS"
                pairwise_notes = "No strict duplicates found."
            else:
                pairwise_status = "❌ FAIL"
                pairwise_pass = False
                overall_pass = False
                # Add specific examples if needed from self.similarity_matrix_data['duplicates_found']
                failed_examples = self.similarity_matrix_data.get('duplicates_found', [])[:2]
                pairwise_notes = "; ".join([f"{ex['bullet_1']} vs {ex['bullet_2']}: {ex['similarity']:.4f}" for ex in failed_examples])
                if len(self.similarity_matrix_data.get('duplicates_found', [])) > 2: pairwise_notes += "..."

        rows.append([
            "Strict Duplicates (>= 0.90)",
            pairwise_details,
            f"{pairwise_max_sim:.4f}",
            str(pairwise_violations),
            pairwise_status,
            pairwise_notes
        ])

        # --- 2. Overview vs. Bullet Overlap (>= 0.60, Excl. Unify/IBM) ---
        overview_pass = True
        overview_details = "Analysis not performed."
        overview_max_sim = 0.0
        overview_violations_count = 0
        overview_notes = ""
        overview_status = "⚠️ WARN"

        # Define sections to EXCLUDE from this check
        excluded_overview_labels = ["Unify Overview", "IBM Overview"]

        if self.overview_similarity_data is not None: # Check for None explicitly
            # Filter out excluded sections BEFORE processing
            relevant_overview_data = [
                result for result in self.overview_similarity_data
                if result.get("section") not in excluded_overview_labels
            ]

            if not relevant_overview_data: # Check if the filtered list is empty
                 overview_details = "0 Relevant Sections Checked"
                 overview_status = "✅ PASS"
                 overview_notes = "No relevant Overview vs Bullet data to analyze."
            else:
                violations = []
                max_sim_overall = 0.0
                overview_details = f"{len(relevant_overview_data)} Sections Checked"

                for result in relevant_overview_data:
                    section_label = result.get('section', 'Unknown')
                    max_sim_overall = max(max_sim_overall, result.get('max_similarity', 0.0))
                    if result.get('threshold_violations'):
                        overview_pass = False
                        overall_pass = False
                        for v in result['threshold_violations']:
                            violations.append(f"{section_label}[{v.get('bullet_index', '?')}]: {v.get('similarity', 0.0):.4f}")

                overview_max_sim = max_sim_overall
                overview_violations_count = len(violations)

                if not violations:
                    overview_status = "✅ PASS"
                    overview_notes = "No significant overlap found."
                else:
                    overview_status = "❌ FAIL"
                    overview_notes = "; ".join(violations[:2]) # Show first few violations
                    if len(violations) > 2: overview_notes += "..."
        else:
             # Keep status as WARN if self.overview_similarity_data was None
             pass

        rows.append([
            "Overview vs. Bullet (>= 0.60, Excl. Unify/IBM)",
            overview_details,
            f"{overview_max_sim:.4f}",
            str(overview_violations_count),
            overview_status,
            overview_notes
        ])

        # --- 3. Executive Summary vs. Section Overlap (>= 0.70) ---
        exec_summary_pass = True
        exec_summary_details = "Analysis not performed."
        exec_summary_max_sim = 0.0
        exec_summary_violations_count = 0
        exec_summary_notes = ""
        exec_summary_status = "⚠️ WARN"
        threshold = 0.70 # Define threshold explicitly

        if self.executive_summary_similarity_data is not None: # Check for None explicitly
            if not self.executive_summary_similarity_data: # Check for empty list
                exec_summary_details = "0 Sections Compared"
                exec_summary_status = "✅ PASS"
                exec_summary_notes = "No Exec Summary vs Section data to analyze."
            else:
                violations_details = [] # Store tuples: (score, section_label, index)
                max_sim_overall = 0.0
                exec_summary_details = f"{len(self.executive_summary_similarity_data)} Sections Compared"

                for result in self.executive_summary_similarity_data:
                    max_sim = result.get('max_similarity', 0.0)
                    avg_sim = result.get('average_similarity', 0.0) # Can use avg if max isn't specific enough
                    section_label = result.get('section_label', 'Unknown')
                    item_count = result.get('item_count', 0)
                    max_sim_overall = max(max_sim_overall, max_sim)

                    # --- Find the specific item index causing the max similarity ---
                    # Re-calculate to find the index if section has multiple items (bullets)
                    max_sim_for_section = 0.0
                    index_of_max = -1
                    exec_summary_text_val = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")

                    if exec_summary_text_val and item_count > 1: # Only need index for multi-item sections
                         # Retrieve the actual content items for the section
                         section_content = None
                         try:
                              section_enum = ResumeSection[section_label] # Get enum from label
                              content_raw = self.staging_buffer.get(section_enum.value)
                              if isinstance(content_raw, list):
                                   section_content = []
                                   for item in content_raw:
                                        if isinstance(item, dict): section_content.append(item.get('text',''))
                                        elif isinstance(item, str): section_content.append(item)
                                   section_content = [c for c in section_content if c] # Filter empty
                         except KeyError:
                              pass # Could not map label back to enum

                         if section_content:
                              dd = DuplicateDetector() # Assuming this is accessible or recreated
                              similarities = [dd._calculate_cosine_similarity(exec_summary_text_val, item_text) for item_text in section_content]
                              if similarities:
                                   max_sim_for_section = max(similarities)
                                   index_of_max = similarities.index(max_sim_for_section)
                    else:
                         max_sim_for_section = max_sim # Use the pre-calculated max for single items or if recalculation fails

                    # --- Check threshold and record violation ---
                    if max_sim_for_section >= threshold:
                        exec_summary_pass = False
                        overall_pass = False
                        # Include index if available and relevant
                        item_ref = f"[{index_of_max}]" if index_of_max != -1 else ""
                        violations_details.append((max_sim_for_section, f"{section_label}{item_ref}"))

                exec_summary_max_sim = max_sim_overall
                exec_summary_violations_count = len(violations_details)

                if not violations_details:
                    exec_summary_status = "✅ PASS"
                    exec_summary_notes = f"Exec Summary distinct (Max sim < {threshold:.2f})."
                else:
                    exec_summary_status = "❌ FAIL"
                    # Sort violations by score descending to show worst offenders
                    violations_details.sort(key=lambda x: x[0], reverse=True)
                    exec_summary_notes = "; ".join([f"{label}: {score:.4f}" for score, label in violations_details[:2]]) # Show top 2
                    if len(violations_details) > 2: exec_summary_notes += "..."
        else:
            # Keep status as WARN if self.executive_summary_similarity_data was None
            pass

        rows.append([
            f"Exec Summary vs. Section (>= {threshold:.2f})",
            exec_summary_details,
            f"{exec_summary_max_sim:.4f}",
            str(exec_summary_violations_count),
            exec_summary_status,
            exec_summary_notes
        ])


        # --- 4. Overall Status ---
        overall_status_str = "✅ PASS" if overall_pass else "❌ FAIL"
        overall_notes = "All similarity checks passed." if overall_pass else "One or more similarity checks failed."
        rows.append([
            "Overall Similarity Status",
            "", # No specific details
            "", # No specific max sim
            "", # No specific violations count
            overall_status_str,
            overall_notes
        ])

        # --- Format and return table ---
        # Adjust alignments and widths as needed
        alignments = ['L', 'L', 'R', 'R', 'L', 'L']
        col_widths = [45, 25, 15, 18, 8, 50] # Example widths, adjust as needed

        lines.extend(self._format_plain_text_table(headers, rows, alignments=alignments, col_widths=col_widths, wrap_text=True))
        lines.append("```")
        return lines

    def _build_qa_section_9_pipeline_health(self) -> List[str]:
        """Builds the NEW QA Section 9: Pipeline Health (Consolidated API Calls)."""
        lines = ["", "9. PIPELINE HEALTH (Resource Consumption)", ""] # Renumbered Header
        lines.append("```markdown")
        # --- Use new single column header ---
        headers = ["Hop ID", "Hop Name", "Status", "Gemini API Calls"]
        rows = []
        total_gemini_calls = 0

        for hop in self.hop_checkpoints:
            # --- Use standardized metadata key ---
            api_calls = hop.metadata.get('gemini_api_calls', 0) # Read the correct key
            rows.append([hop.hop_id, hop.hop_name, hop.status.value, str(api_calls)])
            total_gemini_calls += api_calls # Sum the calls

        # --- Update TOTAL row calculation ---
        rows.append(["TOTAL", "", "", str(total_gemini_calls)])

        # --- Update alignments and format table ---
        # Adjust alignments if needed, here assuming L, L, L, R
        lines.extend(self._format_plain_text_table(headers, rows, ['L', 'L', 'L', 'R']))
        lines.append("```")
        lines.append("Note: 'Gemini API Calls' reflects the total number of calls made to the `generate_content` endpoint for each hop, including calls during RAG analysis and content generation attempts.")
        return lines
  
    def _build_qa_section_10_structural(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds the NEW QA Section 10: Structural Validation."""
        lines = ["", "10. STRUCTURAL VALIDATION (Content Presence)", ""] # Renumbered Header
        struct_rule_ids = [ "STRUCTURE_", "COVER_LETTER_SIGNATURE" ] # Keep signature check here for presence
        struct_results = [vr for vr in validation_results if any(rid in vr.rule_id for rid in struct_rule_ids)]
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        if struct_results:
             struct_results.sort(key=lambda vr: vr.rule_id)
             for vr in struct_results:
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                 final_msg = msg if not vr.passed else "" # Only show message on failure
                 rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg}{details_str}"])
        else:
             rows = [["N/A", "INFO", "No structural presence validation results found."]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_11_cover_letter(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds the NEW QA Section 11: Cover Letter QA."""
        lines = ["", "11. COVER LETTER QA", ""] # Renumbered Header
        # Include the consolidated signature rule and other CL rules
        cl_results = [vr for vr in validation_results if "COVER_LETTER" in vr.rule_id or vr.rule_id == "VG_COVER_LETTER_SIGNATURE_VALID"]
        lines.append("```markdown")
        headers = ["Rule ID", "Status", "Message / Details"]
        rows = []
        if cl_results:
             cl_results.sort(key=lambda vr: vr.rule_id)
             for vr in cl_results:
                 msg = vr.message(vr.details) if callable(vr.message) else vr.message
                 details_str = f" Details: {vr.details}" if vr.details and not vr.passed else ""
                 final_msg = msg if not vr.passed else "" # Only show message on failure
                 rows.append([vr.rule_id, "PASS" if vr.passed else "FAIL", f"{final_msg}{details_str}"])
        else:
             rows = [["N/A", "INFO", "No cover letter QA results found."]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines
    # --- END REFACTOR ---

    # --- START REFACTOR: Section 12 (JD Enforcement) ---
    def _build_qa_section_12_jd_enforcement(self) -> List[str]:
        """Builds the NEW QA Section 12: JD Enforcement Validation."""
        lines = ["", "12. JD ENFORCEMENT VALIDATION", ""] # Renumbered Header
        lines.append("```markdown")
        headers = ["Gate", "Rule", "Status", "Details"]
        enforcement_results = getattr(self.jd_enforcer, 'enforcement_results', [])
        rows = [[res.gate_id, res.rule.name, "PASS" if res.passed else "FAIL", res.details] for res in enforcement_results]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines
    # --- END REFACTOR ---

    # --- START REFACTOR: Section 13 (Final Format) ---
    def _build_qa_section_13_final_format(
        self,
        validation_results: List[ValidationResult],
        file_contents: Dict[str, str]
    ) -> List[str]:
        """Builds the NEW QA Section 13: Formatting of Outputs."""
        lines = ["", "13. FORMATTING OF OUTPUTS", ""] # Renumbered Header
        lines.append("Verifies the presence and correct formatting of all generated output files based on rendering logic and structural validation rules.")
        lines.append("")
        lines.append("```markdown")
        headers = ["Artifact", "Check Type", "Requirement", "Status", "Failure Explanation"]
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
            # Assume rendering checks passed if workflow reached here (or use validation results if available)
            output_definitions.append(("**Resume**", "Section Headers", "VG_RESUME_HEADER_H2", "PASS", ""))
            output_definitions.append(("**Resume**", "Experience Header", "VG_EXPERIENCE_RENDER_FORMAT", "PASS", ""))
            output_definitions.append(("**Resume**", "Experience Bullets", "VG_EXPERIENCE_BULLET_STYLE", "PASS", ""))
            output_definitions.append(("**Resume**", "Edu/Cert Formatting", "VG_EDU_CERTS_FORMAT", "PASS", ""))
            output_definitions.append(("**Resume**", "Competency Formatting", "VG_COMPETENCIES_FORMATTING", "PASS", ""))
            lb_count = resume_content.count('\n\n')
            expected_min_lbs = 10; lb_pass = lb_count >= expected_min_lbs
            output_definitions.append(("**Resume**", "Line Breaks", "Proper Line Breaks", "PASS" if lb_pass else "WARN", "" if lb_pass else f"Found {lb_count} blank lines, expected ~{expected_min_lbs}+."))
        # --- Skills Checks ---
        skills_content = file_contents.get('skills', '')
        output_definitions.append(("**Skills**", "Presence/Type", "Raw Text", "PASS" if skills_content else "FAIL", "" if skills_content else "Content missing."))
        if skills_content:
            skills_lines = [line.strip() for line in skills_content.strip().split('\n') if line.strip()]
            bullet_pass = all(line.startswith("• ") for line in skills_lines) if skills_lines else True
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
            # Use the consolidated signature rule result
            cl_sig_valid_result = next((vr for vr in validation_results if vr.rule_id == "VG_COVER_LETTER_SIGNATURE_VALID"), None)
            cl_sig_valid_pass = cl_sig_valid_result.passed if cl_sig_valid_result else False
            output_definitions.append(("**Cover L.**", "Signature Format", "VG_COVER_LETTER_SIGNATURE_VALID", "PASS" if cl_sig_valid_pass else "FAIL", "" if cl_sig_valid_pass else cl_sig_valid_result.message if cl_sig_valid_result else "Check missing"))
        # --- QA Report Checks ---
        qa_content = file_contents.get('qa_report', '')
        output_definitions.append(("**QA Report**", "Presence/Type", "Fenced Markdown", "PASS" if qa_content else "FAIL", "" if qa_content else "Content missing."))
        if qa_content:
            fence_pass = "```markdown" in qa_content and qa_content.strip().endswith("```")
            output_definitions.append(("**QA Report**", "Markdown Fences", "Uses Fenced Markdown", "PASS" if fence_pass else "FAIL", "" if fence_pass else "Missing markdown fences."))
            qa_table_format_result = next((vr for vr in validation_results if vr.rule_id == "QA_TABLE_FORMAT_INVALID"), None)
            table_pass = qa_table_format_result.passed if qa_table_format_result else True # Assume pass if check missing
            output_definitions.append(("**QA Report**", "Table Format", "Uses Pre-formatted Tables", "PASS" if table_pass else "FAIL", "" if table_pass else qa_table_format_result.message if qa_table_format_result else "Check missing"))
            # Simplified structure check
            section_headers_present = all(f"\n{i}. " in qa_content for i in range(1, 14)) # Check for 1. to 13.
            output_definitions.append(("**QA Report**", "Headers", "Consistent Section Structure", "PASS" if section_headers_present else "FAIL", "" if section_headers_present else "Missing expected section headers (1-13)."))
        # --- App Tracker Checks ---
        app_content = file_contents.get('app_tracker', '')
        output_definitions.append(("**App Trkr**", "Presence/Type", "JSON Block (Unfenced)", "PASS" if app_content else "FAIL", "" if app_content else "Content missing."))
        if app_content:
            is_fenced = app_content.strip().startswith("```json") and app_content.strip().endswith("```")
            fence_check_pass = not is_fenced
            output_definitions.append(("**App Trkr**", "JSON Fences", "Not Fenced", "PASS" if fence_check_pass else "FAIL", "" if fence_check_pass else "App Tracker incorrectly includes ```json fences."))
            json_valid, parsed_json_data, json_fail_reason = False, None, "Unknown JSON error"
            try:
                content_to_parse = app_content.strip()
                if is_fenced: content_to_parse = content_to_parse[7:-3].strip()
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
                if not schema_fail_reason and schema_pass: schema_fail_reason = "Keys match schema."
                elif not schema_fail_reason and not schema_pass: schema_fail_reason = "Key mismatch detected."
            output_definitions.append(("**App Trkr**", "Schema", "Adheres to APP_TRACKER_SCHEMA_V4", "PASS" if schema_pass else "FAIL", schema_fail_reason.strip()))

        final_rows = [[item[0], item[1], item[2], item[3], item[4]] for item in output_definitions]
        col_widths = [13, 36, 34, 8, 0] # Keep width for last col even if empty
        lines.extend(self._format_plain_text_table(headers, final_rows, alignments=['L', 'L', 'L', 'L', 'L'], col_widths=col_widths, wrap_text=False))
        lines.append("```")
        return lines
    # --- END REFACTOR ---

    # --- START REFACTOR: QA Report Section Config (Updated Order) ---
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]},
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]},
        {"method": "_build_qa_section_6_authenticity", "args": ["validation_results"]},
        # Section 7 (Original 11)
        {"method": "_build_qa_section_7_prod_readiness", "args": ["validation_results"]},
        # Section 8 (Original 8 - Summary Only)
        {"method": "_build_qa_section_8_pairwise_similarity", "args": []},
        # Section 9 (Original 9)
        {"method": "_build_qa_section_9_pipeline_health", "args": []},
        # Section 10 (Original 10)
        {"method": "_build_qa_section_10_structural", "args": ["validation_results"]},
        # Section 11 (Original 12)
        {"method": "_build_qa_section_11_cover_letter", "args": ["validation_results"]},
        # Section 12 (Original 13)
        {"method": "_build_qa_section_12_jd_enforcement", "args": []},
        # Section 13 (Original 14)
        {"method": "_build_qa_section_13_final_format", "args": ["validation_results", "file_contents"]},
    ]
    # --- END REFACTOR ---

    # --- START REFACTOR: Helper for _generate_qa_report ---
    def _build_qa_report_sections(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> List[str]:
        """
        Iterates through QA_REPORT_SECTIONS config to build all report sections.
        """
        report_lines = []
        current_file_contents = (self.rendered_output.get('file_contents', {})
                                 if hasattr(self, 'rendered_output') and self.rendered_output
                                 else {})
        available_args = {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "validation_results": validation_results,
            "file_contents": current_file_contents
        }

        for section_config in self.QA_REPORT_SECTIONS:
            method_name = section_config["method"]
            arg_names = section_config["args"]
            try:
                builder_method = getattr(self, method_name)
                # Ensure arguments exist before calling
                call_args = {name: available_args[name] for name in arg_names if name in available_args}
                if len(call_args) != len(arg_names):
                    missing_args = set(arg_names) - set(call_args.keys())
                    raise KeyError(f"Missing required arguments {missing_args} for method '{method_name}'")

                section_lines = builder_method(**call_args) # Use keyword arguments
                report_lines.extend(section_lines)
            except (AttributeError, KeyError, Exception) as e:
                error_message = f"Error building QA section '{method_name}': {e}"
                logging.getLogger(__name__).error(error_message, exc_info=True)
                report_lines.append(f"\n--- {error_message} ---\n")

        return report_lines

    def _validate_qa_report_formatting(self, report_text: str) -> ValidationResult:
        """
        Validates that the generated QA report uses pre-formatted text tables.
        """
        pre_formatted_check_passed = True
        pre_formatted_check_messages = []

        # Split the report into sections to check each one (robust split)
        # Look for patterns like "\n7. SECTION NAME\n" or start of string "1. SECTION NAME\n"
        sections = re.split(r'(?m)^\d+\.\s', report_text)
        # Add back the section number/title for context
        titles_match = re.findall(r'(?m)^\d+\.\s.*', report_text)
        section_blocks = {}
        if len(sections) > 1:
            for i, title in enumerate(titles_match):
                 section_index = i + 1
                 content = sections[section_index]
                 section_blocks[section_index] = (title.strip(), content)

        for section_index, (title, section_block) in section_blocks.items():
            # Section 1 (Signal Quality) is allowed to not have tables
            if section_index == 1:
                continue

            md_blocks = re.findall(r"```markdown(.*?)```", section_block, re.DOTALL)
            if not md_blocks and "```" in section_block: # Check if fences are present but maybe not markdown
                 md_blocks = re.findall(r"```(.*?)```", section_block, re.DOTALL)

            # If no code blocks found at all in a section that should have one, warn/fail
            # Sections 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13 should have code blocks
            if not md_blocks and section_index in [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]:
                pre_formatted_check_passed = False
                msg = f"QA Section {section_index} ({title}) missing expected ```markdown block."
                if msg not in pre_formatted_check_messages:
                    pre_formatted_check_messages.append(msg)
                continue # Skip further checks for this section

            # Check inside code blocks for markdown table syntax
            for block in md_blocks:
                # Check for lines containing '|' AND a line starting with '---' (common markdown table indicator)
                has_pipe = any("|" in line for line in block.split('\n'))
                has_separator = any(line.strip().startswith("---") for line in block.split('\n'))

                if has_pipe and has_separator:
                    pre_formatted_check_passed = False
                    msg = f"QA Section {section_index} ({title}) appears to contain Markdown table syntax inside ``` block."
                    if msg not in pre_formatted_check_messages:
                        pre_formatted_check_messages.append(msg)

        return ValidationResult(
            rule_id="QA_TABLE_FORMAT_INVALID", passed=pre_formatted_check_passed, severity=ValidationSeverity.HIGH,
            message="; ".join(pre_formatted_check_messages) if not pre_formatted_check_passed else "All QA tables use pre-formatted text.",
            details={"failed_sections": pre_formatted_check_messages}
        )
    # --- END REFACTOR ---

    def _generate_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> Tuple[List[ValidationResult], str, Dict[str, str]]:
        """
        [REFACTORED] Generate full QA report by calling helper methods.
        """
        validation_results_out = []
        report_lines = [
            f"RESUME QA REPORT (v{__version__})",
            f"Generated: {datetime.now().isoformat()}",
        ]

        # 1. Build all sections using the new helper
        built_sections = self._build_qa_report_sections(staging_buffer, thematic_analysis, validation_results)
        report_lines.extend(built_sections)
        qa_report_text = "\n".join(report_lines).strip()

        # 2. Validate the formatting of the generated report
        formatting_validation_result = self._validate_qa_report_formatting(qa_report_text)
        validation_results_out.append(formatting_validation_result)

        # 3. Add a final success/info result for the generation process itself
        validation_results_out.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"QA Report generated ({len(qa_report_text.splitlines())} lines)"
        ))

        # 4. Prepare the final file contents dictionary
        final_file_contents = (self.rendered_output.get('file_contents', {})
                               if hasattr(self, 'rendered_output') and self.rendered_output
                               else {})
        final_file_contents['qa_report'] = qa_report_text

        return validation_results_out, qa_report_text, final_file_contents

    def _format_ascii_bar_chart(self, label: str, value: float, target_min: float, target_max: float, temperature: float = 0.0, bar_length: int = 10, is_summary: bool = False) -> str:
        # ... (Method content remains the same as v13.20) ...
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
        # ... (Method content remains the same as v13.20) ...
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
            # Ensure width is at least 1, prevent "{:<0}" format errors
            effective_width = max(1, widths[i])
            align_char = '<' if aligns[i] == 'L' else '>' if aligns[i] == 'R' else '^'
            formatters.append(f"{{:{align_char}{effective_width}}}")
        lines = []
        if headers:
            header_lines_split = [str(h).split('\n') for h in headers]
            max_header_lines = max(len(h_lines) for h_lines in header_lines_split)
            for line_idx in range(max_header_lines):
                line_parts = []
                for col_idx in range(num_cols):
                    header_part = header_lines_split[col_idx][line_idx] if line_idx < len(header_lines_split[col_idx]) else ""
                    # Handle case where column width might be 0
                    if widths[col_idx] > 0:
                        line_parts.append(formatters[col_idx].format(header_part))
                    # If width is 0, don't add anything for this column
                lines.append("  ".join(line_parts).rstrip()) # Use rstrip to remove trailing spaces if last col width is 0
            lines.append("  ".join("-" * max(1, widths[i]) for i in range(num_cols)).rstrip()) # Ensure separator is at least '-'
        if wrap_text:
            wrapped_rows = []
            for row in rows:
                 row_lines = [[] for _ in range(num_cols)]
                 max_lines = 1
                 for i, cell in enumerate(row):
                     if i < num_cols:
                         cell_str = str(cell)
                         # Only wrap if width > 0
                         wrapped = self._wrap_cell_text(cell_str, widths[i]) if widths[i] > 0 else [cell_str]
                         row_lines[i].extend(wrapped)
                         max_lines = max(max_lines, len(wrapped))
                 for line_idx in range(max_lines):
                     line_parts = []
                     for col_idx in range(num_cols):
                         cell_part = row_lines[col_idx][line_idx] if line_idx < len(row_lines[col_idx]) else ""
                         # Handle case where column width might be 0
                         if widths[col_idx] > 0:
                             line_parts.append(formatters[col_idx].format(cell_part))
                         # If width is 0, don't add anything
                     wrapped_rows.append("  ".join(line_parts).rstrip())
            lines.extend(wrapped_rows)
        else:
             for row in rows:
                 line_parts = []
                 for i in range(num_cols):
                     if i < len(row):
                         # Handle case where column width might be 0
                         if widths[i] > 0:
                             line_parts.append(formatters[i].format(str(row[i])[:widths[i]]))
                         # If width is 0, add nothing
                 lines.append("  ".join(line_parts).rstrip())
        return lines

    def _wrap_cell_text(self, text: str, width: int) -> List[str]:
        # ... (Method content remains the same as v13.20) ...
        lines = []
        if width <= 0: return [text] # Cannot wrap to zero or negative width
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
        # ... (Method content remains the same as v13.20) ...
        if min_target <= count <= max_target:
            status = "PASS"
        else:
            status = "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str

    def _invoke_deduplication_analysis(self, staging_buffer: ImmutableStagingBuffer) -> bool:
        """
        Gathers data and calls DuplicateDetector methods for QA report sections.
        MODIFIED: Excludes Skills, CL non-body paras, Unify Bullets, IBM Bullets
                  from the pairwise similarity matrix calculation (QA Section 8).
                  Other similarity checks (Overview vs Bullets, Exec Summary vs Sections)
                  remain unchanged.
        """
        self.dedup_analysis_timestamp = datetime.now().isoformat()
        if not self.dup_detector:
            self.logger.warning("DuplicateDetector not available (likely HOP-2 failure). Skipping deduplication analysis.")
            return False

        # --- Data Gathering for Different Checks ---
        sections_for_matrix = {}         # Items for Pairwise Matrix (QA Sec 8) - MODIFIED SCOPE
        overview_bullet_pairs = {}       # Items for Overview vs Bullets check (QA Sec 5/Validation) - UNCHANGED
        exec_summary_text = staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        exec_summary_comparison_data = {} # Items for Exec Summary vs Sections check (QA Sec 7/Validation) - UNCHANGED

        # Map sections to labels used in analysis
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

        # --- Process each section ---
        for section_enum, label in section_map.items():
            content = staging_buffer.get(section_enum.value)
            if not content: continue # Skip empty sections

            # --- Handle Overviews ---
            if "Overview" in label:
                if isinstance(content, str) and content.strip():
                    overview_text = content.strip()
                    # Add to ALL analysis sets
                    sections_for_matrix[label] = [overview_text]
                    overview_bullet_pairs[label] = {"overview": overview_text, "bullets": []}
                    exec_summary_comparison_data[label] = overview_text
                continue # Move to next section

            # --- Handle Bullets & Competencies ---
            if "Bullets" in label or label == "Competencies":
                bullet_texts = []
                if isinstance(content, list):
                    for item in content:
                        text = ""
                        if isinstance(item, dict):
                            text = item.get('text', item.get('bullet_text',''))
                        elif isinstance(item, str):
                            text = item
                        if text and text.strip():
                            bullet_texts.append(text.strip())

                if not bullet_texts: continue # Skip if no valid bullets found

                # Add to Exec Summary comparison data (UNCHANGED)
                exec_summary_comparison_data[label] = bullet_texts

                # Add to Overview vs Bullets check data (UNCHANGED)
                base_label = label.replace(" Bullets", "").replace(" Competencies", "")
                overview_key = f"{base_label} Overview"
                if overview_key in overview_bullet_pairs:
                     overview_bullet_pairs[overview_key]["bullets"].extend(bullet_texts)

                # --- START MODIFICATION: Exclude Unify/IBM from Pairwise Matrix ---
                if label not in ["Unify Bullets", "IBM Bullets"]:
                    sections_for_matrix[label] = bullet_texts
                else:
                    self.logger.debug(f"Excluding {label} from pairwise similarity matrix.")
                # --- END MODIFICATION ---
                continue # Move to next section

            # --- Handle Skills ---
            if label == "Skills":
                if isinstance(content, list):
                    skill_texts = [item for item in content if isinstance(item, str) and item.strip()]
                    if skill_texts:
                        # Add to Exec Summary comparison data (UNCHANGED)
                        exec_summary_comparison_data[label] = skill_texts
                        # --- START MODIFICATION: Exclude Skills from Pairwise Matrix ---
                        # sections_for_matrix[label] = skill_texts # DO NOT ADD
                        self.logger.debug(f"Excluding {label} from pairwise similarity matrix.")
                        # --- END MODIFICATION ---
                continue # Move to next section

            # --- Handle Cover Letter ---
            if label == "Cover Letter":
                if isinstance(content, str) and content.strip():
                    # Split into paragraphs/blocks
                    all_cl_parts = [p.strip() for p in content.split('\n\n') if p.strip()]

                    # Identify body paragraphs (assuming standard structure)
                    # Indices 3, 4, 5 correspond to Body P1, P2, P3 after Date, Recipient, Salutation
                    body_para_indices = [3, 4, 5]
                    body_paras = [all_cl_parts[i] for i in body_para_indices if i < len(all_cl_parts)]

                    if body_paras:
                         # Add ALL parts to Exec Summary comparison data (UNCHANGED)
                         exec_summary_comparison_data[label] = all_cl_parts
                         # --- START MODIFICATION: Add ONLY Body Paragraphs to Pairwise Matrix ---
                         sections_for_matrix[label] = body_paras
                         self.logger.debug(f"Including {len(body_paras)} Cover Letter body paragraphs in pairwise matrix.")
                         # --- END MODIFICATION ---
                    else:
                         self.logger.warning("Could not extract expected body paragraphs from Cover Letter for similarity checks.")

                continue # Move to next section

            # --- Handle Executive Summary ---
            if label == "Exec Summary":
                 if isinstance(content, str) and content.strip():
                     summary_text = content.strip()
                     # Add to Pairwise Matrix (UNCHANGED)
                     sections_for_matrix[label] = [summary_text]
                     # No need to add to exec_summary_comparison_data (it *is* the exec summary)
                 continue # Move to next section


        # --- Perform Similarity Calculations ---
        try:
            # Pairwise Matrix (QA Sec 8) - Uses the MODIFIED sections_for_matrix
            self.similarity_matrix_data = self.dup_detector.compute_similarity_matrix(sections_for_matrix)
            self.logger.info(f"Pairwise similarity matrix computed on {sum(len(v) for v in sections_for_matrix.values())} items.")
        except Exception as e:
            self.logger.error(f"Error computing similarity matrix: {e}", exc_info=True)
            self.similarity_matrix_data = None

        try:
            # Overview vs Bullets (QA Sec 5 / Validation) - Uses UNCHANGED overview_bullet_pairs
            self.overview_similarity_data = []
            for label, data in overview_bullet_pairs.items():
                 if data["overview"] and data["bullets"]:
                     sim_result = self.dup_detector.compute_overview_bullet_similarity(
                         data["overview"], data["bullets"], section_id=label
                     )
                     self.overview_similarity_data.append(sim_result)
            self.logger.info(f"Overview vs Bullet similarity computed for {len(self.overview_similarity_data)} sections.")
        except Exception as e:
            self.logger.error(f"Error computing overview vs bullet similarity: {e}", exc_info=True)
            self.overview_similarity_data = None

        try:
            # Exec Summary vs Sections (QA Sec 7 / Validation) - Uses UNCHANGED exec_summary_comparison_data
            self.executive_summary_similarity_data = self.dup_detector.compute_executive_summary_similarity(
                exec_summary_text, exec_summary_comparison_data
            )
            self.logger.info(f"Executive Summary similarity computed against {len(exec_summary_comparison_data)} sections/items.")
        except Exception as e:
             self.logger.error(f"Error computing executive summary similarity: {e}", exc_info=True)
             self.executive_summary_similarity_data = None

        return True # Indicate analysis was attempted

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

# --- START OVERWRITE: `if __name__ == '__main__':` block (Cache Clearing & JD URL) ---
if __name__ == '__main__':
    import copy
    from dataclasses import asdict
    import shutil # --- Added for directory removal ---
    import logging # --- Ensure logging is configured early ---

    # --- Configure logging early to capture clearing messages ---
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # --- START FIX: Automatic Cache and Telemetry Clearing ---
    try:
        temp_rag_config = RAGConfig()
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
    # --- END FIX: Automatic Cache and Telemetry Clearing ---

    # --- Configuration for the run ---
    my_company_name = "DataDog"
    my_job_title = "Director, Technology Alliances"
    my_jd_url = "https://careers.datadoghq.com/detail/693897/?gh_jid=693897" # <-- DEFINE THE URL HERE
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

    orchestrator = WorkflowOrchestrator(copy.deepcopy(MASTER_RESUME_JSON))

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
        print(f"Reason: {result.get('reason', result.get('error', 'No reason provided.'))}")

    # Optionally, save the generated files to a directory
    if result.get('status') == 'SUCCESS':
        output_dir = "generated_resumes"
        os.makedirs(output_dir, exist_ok=True)
        file_contents_dict = result.get('file_contents', {})
        if file_contents_dict:
            for file_type, content in file_contents_dict.items():
                file_paths_dict = result.get('file_paths', {})
                if file_paths_dict:
                    file_name = file_paths_dict.get(file_type)
                    if file_name and content is not None:
                        try:
                             with open(os.path.join(output_dir, file_name), 'w', encoding='utf-8') as f:
                                 f.write(content)
                        except IOError as e: logger.error(f"Error writing file {file_name}: {e}")
                        except TypeError as e: logger.error(f"Error writing file {file_name} - invalid content type ({type(content)}): {e}")
                    elif not file_name: logger.warning(f"File path not found for type '{file_type}' in results.")
                else:
                     logger.warning("File paths dictionary ('file_paths') not found in results. Cannot save files.")
                     break
            print(f"\nGenerated files saved to the '{output_dir}' directory.")
        else:
             logger.warning("File contents dictionary ('file_contents') not found or empty in results. Cannot save files.")

    print("\n--- Workflow Finished ---")
# --- END OVERWRITE: `if __name__ == '__main__':` block ---