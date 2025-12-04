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

__version__ = "13.90"
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
    HEADLINE_MIN_CHARS: int = 60 # Note: Not currently validated by rules
    HEADLINE_MAX_CHARS: int = 90 # Note: Not currently validated by rules
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 7
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9
    K1_MIN_DIFFERENTIATORS: int = 4 # Minimum differentiators to weave in

    # Experience Overviews (Synthesized for Unify/IBM)
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35

    # TraderSense Overview (Copied from Master)
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20 # Keep for validation if overview is copied
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 35 # Keep for validation if overview is copied

    # --- START CHANGES for EY and Early Career Narrative Blocks ---
    # EY_OVERVIEW_WORD_COUNT_MIN: int = 25 # Replaced by narrative block
    # EY_OVERVIEW_WORD_COUNT_MAX: int = 40 # Replaced by narrative block
    # EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 20 # Replaced by narrative block
    # EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 35 # Replaced by narrative block

    # NEW: Constraints for the 3-sentence narrative blocks
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40 # Total words for the 3 sentences
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50 # Total words for the 3 sentences
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70
    # --- END CHANGES ---

    # Word Distribution (Experience) - Based on combined overview + bullets
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
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35 # Minimum similarity to JD

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

# ============================================================================
# REASONING CONFIGURATION INSTANTIATION
# ============================================================================

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
  "schema_version": "master_resume_v2.15", # Keeping original schema version
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
      # "overview": "DELETED", # Field removed
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
      # "overview": "DELETED", # Field removed
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
      # "overview": "DELETED", # Field removed
      "highlights": [ # Replaced original highlights with 5 approved bullets
        "Architected and implemented a high-frequency trading platform using C++ and low-latency queues, achieving sub-millisecond order execution and incorporating real-time risk controls reducing potential slippage costs by an estimated 15%.",
        "Constructed a robust backtesting framework capable of simulating trading strategies against years of historical market data, enabling rapid validation of algorithm performance and iteration cycles reduced by an estimated 40%.",
        "Built and managed scalable cloud infrastructure (early AWS adoption) supporting data ingestion, backtesting, and live trading, maintaining >99.8% system uptime critical for continuous operations during market hours.",
        "Integrated multiple brokerage APIs via FIX protocol for seamless order routing and position management, enabling access to 3 major market centers and reducing manual trade entry errors by over 90%.",
        "Designed the data warehousing strategy for trade execution analysis, enabling detailed performance attribution and delivering daily capital efficiency reports essential for strategic business evaluation."
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
      # "overview": "DELETED", # Field removed
      "highlights": [ # Replaced original highlights with 10 approved, quantified bullets
        "Designed standardized model validation methodologies for derivative pricing and risk models across ~15 global banking clients, enhancing governance frameworks and reducing validation time by an estimated 20% while meeting emerging Basel III expectations.",
        "Developed stochastic models (Monte Carlo) projecting economic capital needs under Solvency II for 5+ multinational insurers (>$50B AUM), incorporating complex insurance guarantees and improving capital forecast accuracy by ~15%.",
        "Advised 10+ clients on implementing enterprise risk management (ERM) frameworks, aligning risk appetite with capital projection and stress testing (early CCAR), leading to an average 25% reduction in identified operational risk gaps.",
        "Managed the design and implementation of financial reporting solutions for FAS 133/157 compliance across derivative portfolios exceeding $100B in notional value, ensuring audit readiness and reducing manual reporting effort by ~30%.",
        "Built quantitative models for projecting capital adequacy ratios under various stress scenarios for regional and national banks, improving internal capital planning and reducing regulatory query cycles by an estimated 20%.",
        "Performed independent reviews of actuarial models for variable annuity guarantee products (GMxB) covering policyholder liabilities >$20B, identifying key model risks and improving hedge effectiveness calculations by ~10%.",
        "Guided financial institutions in developing economic capital allocation methodologies, linking risk metrics to performance for 5+ major business lines, enabling more risk-informed strategic decision-making.",
        "Designed validation frameworks for ~30 complex derivative pricing models (swaps, options, structured products), ensuring model integrity and reducing model risk findings by an average of 40% across engagements.",
        "Contributed to 3 published industry whitepapers on emerging regulatory requirements (Dodd-Frank, Basel III) related to market risk and counterparty credit risk capital, influencing client interpretation and implementation strategies.",
        "Presented complex modeling results and strategic risk recommendations to 20+ senior client committees (CROs, CFOs, Audit Committees), facilitating informed capital management decisions impacting billions in required capital."
      ]
    },
    { # --- START: Updated Early Career Section ---
      "company": "Early Career Roles",
      "location": "Philadelphia, PA",
      "title": "Actuarial Consultant and Quantitative Roles",
      "dates": {
        "start": "October 2002",
        "end": "September 2009"
      },
      # "overview": "DELETED", # Field removed
      "highlights": [ # Replaced original highlight with 4 approved bullets
        "Designed stochastic pricing models for variable annuities and path-dependent options while developing distributed computing systems on grid clusters to execute large-scale valuations for financial reporting.",
        "Developed actuarial projection models for variable annuity loss reserving and asset adequacy testing, incorporating dynamic policyholder behavior assumptions under diverse market scenarios.",
        "Conducted mortality and lapse experience studies on large variable annuity datasets to derive best-estimate assumptions, directly impacting pricing accuracy and reserve adequacy.",
        "Analyzed the effectiveness of variable annuity guarantee hedging programs using Greeks-based and stochastic methods, contributing to reports quantifying hedge P&L and basis risk exposure."
      ]
    } # --- END: Updated Early Career Section ---
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

from enum import Enum, auto

class ResumeSection(Enum):
    K0_NAME = "K.0_Name"
    K0_HEADLINE = "K.0_Headline"
    K0_CONTACT = "K.0_Contact"
    K0_EXECUTIVE_SUMMARY_HEADER = "K.0_Executive_Summary_Header"
    K0_EXPERIENCE_HEADER = "K.0_Experience_Header"
    K0_EDUCATION_HEADER = "K.0_Education_Header"
    K0_CERTIFICATIONS_HEADER = "K.0_Certifications_Header"
    K0_COMPETENCIES_HEADER = "K.0_Competencies_Header"
    K1_EXECUTIVE_SUMMARY = "K.1_Executive_Summary"
    K2_UNIFY_BULLETS = "K.2_Unify_Bullets"
    K2_UNIFY_OVERVIEW = "K.2_Unify_Overview"
    K3_IBM_BULLETS = "K.3_IBM_Bullets"
    K3_IBM_OVERVIEW = "K.3_IBM_Overview"
    K4_TRADERSENSE_NARRATIVE = "K.4_TraderSense_Narrative"
    K5_EY_NARRATIVE = "K.5_EY_Narrative"
    K6_EARLY_CAREER_NARRATIVE = "K.6_Early_Career_Narrative"
    K7_EDUCATION = "K.7_Education"
    K8_CERTIFICATIONS = "K.8_Certifications"
    K9_COMPETENCIES = "K.9_Competencies"
    K10_SKILLS = "K.10_Skills"
    K11_COVER_LETTER = "K.11_Cover_Letter"

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
# HOP-3: ARTIST GENERATOR (LLM Calls) - STATEFUL RETRY VERSION - RENUMBERED
# ============================================================================
import copy
import re
import random
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union

class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, previous_failures: List[ValidationResult] = None):
        """Initializes the ArtistGenerator."""
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.previous_failures = previous_failures or []
        self.constraints = ContentConstraintsConfig()
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K2_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K3_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K9_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
    }

    # --- FINAL CORRECTED CONFIG v3: Sorted K.0-K.11, Correct Narrative Enum Mapping ---
    ARTIST_GENERATION_CONFIG = [
        # --- K.0 ---
        {"section": ResumeSection.K0_NAME, "method_name": "_copy_k0_name"},
        {"section": ResumeSection.K0_CONTACT, "method_name": "_copy_k0_contact"},
        {"section": ResumeSection.K0_HEADLINE, "method_name": "_generate_k0_headline"},
        {"section": ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EXPERIENCE_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_EDUCATION_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_CERTIFICATIONS_HEADER, "method_name": "_generate_dummy_header"},
        {"section": ResumeSection.K0_COMPETENCIES_HEADER, "method_name": "_generate_dummy_header"},
        # --- K.1 ---
        {"section": ResumeSection.K1_EXECUTIVE_SUMMARY, "method_name": "_generate_k1_executive_summary"},
        # --- K.2 (Bullets & Overview) ---
        {"section": ResumeSection.K2_UNIFY_BULLETS, "method_name": "_generate_k2_unify_bullets"},
        {"section": ResumeSection.K2_UNIFY_OVERVIEW, "method_name": "_generate_k2_unify_overview"},
        # --- K.3 (Bullets & Overview) ---
        {"section": ResumeSection.K3_IBM_BULLETS, "method_name": "_generate_k3_ibm_bullets"},
        {"section": ResumeSection.K3_IBM_OVERVIEW, "method_name": "_generate_k3_ibm_overview"},
        # --- K.4 (Narrative Only) ---
        {"section": ResumeSection.K4_TRADERSENSE_NARRATIVE, "method_name": "_generate_k4_tradersense_narrative"}, # Use NARRATIVE enum
        # --- K.5 (Narrative Only) ---
        {"section": ResumeSection.K5_EY_NARRATIVE, "method_name": "_generate_k5_ey_narrative"}, # Use NARRATIVE enum
        # --- K.6 (Narrative Only) ---
        {"section": ResumeSection.K6_EARLY_CAREER_NARRATIVE, "method_name": "_generate_k6_early_career_narrative"}, # Use NARRATIVE enum
        # --- K.7 ---
        {"section": ResumeSection.K7_EDUCATION, "method_name": "_copy_k7_education"},
        # --- K.8 ---
        {"section": ResumeSection.K8_CERTIFICATIONS, "method_name": "_copy_k8_certifications"},
        # --- K.9 ---
        {"section": ResumeSection.K9_COMPETENCIES, "method_name": "_generate_k9_competencies"},
        # --- K.10 ---
        {"section": ResumeSection.K10_SKILLS, "method_name": "_generate_k10_skills"},
        # --- K.11 ---
        {"section": ResumeSection.K11_COVER_LETTER, "method_name": "_generate_k11_cover_letter"},
    ]
    # --- END FINAL CORRECTED CONFIG v3 ---

    BULLET_WORD_COUNT_RANGES = {
        ResumeSection.K2_UNIFY_BULLETS: (25, 38),
        ResumeSection.K3_IBM_BULLETS: (22, 34),
        ResumeSection.K9_COMPETENCIES: (25, 40),
    }

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

            # Model Initialization
            try:
                # Use gemini-1.5-pro as specified in this version
                model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception as model_init_e:
                raise HopExecutionError(f"Failed to initialize Gemini model for {section_id}: {model_init_e}")

            # Parameter Preparation
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

                    # Clean markdown fences and return
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

                    # Clean markdown fences and return
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

        # --- Use the SORTED K0-K11 config ---
        for config in self.ARTIST_GENERATION_CONFIG:
            section_enum = config["section"]
            method_name = config["method_name"]
            section_api_calls = 0

            # --- Skip section if not requested ---
            if section_enum not in sections_to_generate:
                # Run idempotent copy/dummy methods anyway if they exist in config
                if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                    try:
                        method = getattr(self, method_name)
                        output[section_enum.value] = method() # No calls
                    except Exception as e:
                        # Log error but don't halt if copy fails for non-requested section
                        logging.warning(f"Error in {method_name} for non-requested section {section_enum.value}: {e}")
                        output[section_enum.value] = None # Mark as None on error
                else: # Mark skipped LLM sections as None
                    output[section_enum.value] = None
                continue

            # --- Generate Section ---
            logging.info(f"  Generating section: {section_enum.name} ({section_enum.value})")

            # Handle copy/dummy sections (if requested)
            if method_name.startswith("_copy_") or method_name == "_generate_dummy_header":
                try:
                    method = getattr(self, method_name)
                    output[section_enum.value] = method() # No calls
                except Exception as e:
                    raise HopExecutionError(f"Unexpected error in {method_name} for {section_enum.value}: {e}") from e
                continue

            # --- LLM Generation ---
            # Determine Temperature
            final_temp = temperature_overrides.get(section_enum)
            if final_temp is None:
                logging.error(f"  {section_enum.name}: Temperature override NOT FOUND! Halting.")
                raise HopExecutionError(f"Misconfiguration: Temperature override missing for {section_enum.name}")

            # Call the generation method (expecting HopExecutionError on failure)
            try:
                method = getattr(self, method_name)
                generated_content = None # Initialize

                # --- Call method with appropriate arguments ---
                # Pass `current_output` ONLY to K2 and K3 overview methods in this version
                if method_name in ["_generate_k2_unify_overview", "_generate_k3_ibm_overview"]:
                    generated_content, section_api_calls = method(current_output=output, temperature_override=final_temp)
                # All other generation methods only need temp
                else:
                    generated_content, section_api_calls = method(temperature_override=final_temp)

                # Store result and aggregate calls
                output[section_enum.value] = generated_content
                total_api_calls += section_api_calls

                # Basic check for placeholders
                if isinstance(generated_content, str) and "[Placeholder" in generated_content:
                    logging.warning(f"{section_enum.value} generation returned placeholder: {generated_content[:100]}...")
                    # Optionally halt here by raising HopExecutionError

            except HopExecutionError as he: # Propagate halts
                logging.error(f"Generation HALTED at section {section_enum.value} ({method_name}): {he}", exc_info=False)
                raise he
            except AttributeError as ae: # Catch if method doesn't exist (config mismatch)
                 logging.error(f"AttributeError: Method '{method_name}' not found for section {section_enum.value}. Config mismatch?", exc_info=True)
                 raise HopExecutionError(f"Method '{method_name}' not found for {section_enum.value}. Check ARTIST_GENERATION_CONFIG.") from ae
            except Exception as e: # Catch unexpected errors during generation call
                logging.error(f"Unexpected Error generating section {section_enum.value} with {method_name} (Temp: {final_temp}): {e}", exc_info=True)
                raise HopExecutionError(f"Unexpected error during {section_enum.value} generation: {e}") from e

        # Filter out None values ONLY for sections that were MEANT to be generated in this pass
        final_output_for_this_pass = {
            k: v for k, v in output.items()
            # Keep if value is not None OR if the section wasn't supposed to be generated this pass
            if v is not None or ResumeSection(k) not in sections_to_generate
        }
        # Ensure all sections initially targeted *have* a key in the output, even if value is None (due to generation failure before assignment)
        for section in sections_to_generate:
             if section.value not in final_output_for_this_pass:
                 final_output_for_this_pass[section.value] = None # Mark explicitly as None if missing after attempt

        return final_output_for_this_pass, total_api_calls


    # --- Copy Methods (Renumbered for K0-K11 scheme) ---
    def _copy_k0_name(self) -> str: return self.master_resume.get("owner", {}).get("name", "")
    def _copy_k0_contact(self) -> str:
        contact = self.master_resume.get("owner", {}).get("contact", {})
        parts = [f"Phone: {contact.get('phone', '')}", f"Email: {contact.get('email', '')}", f"LinkedIn: {contact.get('linkedin', '')}"]
        # Filter out parts with empty values after the colon and space
        return " | ".join(p for p in parts if len(p.split(': ')) > 1 and p.split(': ')[1])
    def _copy_k7_education(self) -> List[Dict]: return self.master_resume.get("education", [])
    def _copy_k8_certifications(self) -> List[str]: return self.master_resume.get('certifications_and_credentials', [])
    def _generate_dummy_header(self) -> str: return "HEADER_PLACEHOLDER"

    # --- LLM Generation Methods (Renumbered K0-K11 scheme) ---

    def _generate_k0_headline(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'Key Expertise') if self.thematic_analysis.primary_theme else 'Key Expertise'
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            differentiators = getattr(comp_intel, 'differentiator_keywords', [])

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
6.  **Do NOT start the headline or any component with phrases like 'At [Company]', 'As [Title]', etc.**

{feedback_instruction}
Example Format: Skill Area 1 | Skill Area 2 | Outcome Focus

Generate Headline:
"""
        # Ensure K0_HEADLINE_CONFIG exists in ReasoningConfig
        try: reasoning_config = ReasoningConfig.K0_HEADLINE_CONFIG
        except AttributeError: logging.warning("K0_HEADLINE_CONFIG missing from ReasoningConfig. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        base_system = "You are an expert resume headline crafter specializing in concise, impactful, keyword-rich headlines without using job titles."
        headline, call_count = self._call_gemini_api(
            prompt, reasoning_config, ResumeSection.K0_HEADLINE.value, base_system,
            temperature_override=temperature_override
        )
        return headline, call_count

    def _generate_k1_executive_summary(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # Return tuple
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key skills') # ... etc (context gathering) ...
        differentiators = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None) # ... etc ...
        role_archetype = self.thematic_analysis.role_classification.get('role_archetype', 'Experienced Professional') # ... etc ...
        narratives_data = getattr(self.thematic_analysis, 'problem_solution_narratives', None); narratives = narratives_data if isinstance(narratives_data, dict) else {}
        problem = narratives.get('common_problems', ['solving key challenges'])[0] if narratives.get('common_problems') else 'solving key challenges'
        solution = narratives.get('solution_patterns', ['delivering impactful results'])[0] if narratives.get('solution_patterns') else 'delivering impactful results'
        archetype_map = { "Executive_Leader": "an executive leader", "Technical_IC": "a hands-on technical expert", "Post-Sales_Customer_Success": "a customer success leader", "Pre-Sales_GTM": "a pre-sales GTM strategist", "Product_Management": "a product management professional" }
        archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."

        feedback_instruction = "" # ... (feedback logic based on self.previous_failures) ...
        sentence_count_failures = [f for f in self.previous_failures if f.rule_id == "VG_SENTENCE_COUNT_K1"] # Assuming rule ID stays same
        if sentence_count_failures: # ... add sentence feedback ...
             last_fail = sentence_count_failures[-1]; # ... format feedback ...
             feedback_instruction += f"\nIMPORTANT FEEDBACK (Sentences): Previous failed (had {last_fail.details.get('sentence_count','N/A')}, target is {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}). Adjust."
        word_count_failures = [f for f in self.previous_failures if f.rule_id == "VG_WORD_COUNT_K1"] # Assuming rule ID stays same
        if word_count_failures: # ... add word count feedback ...
             last_fail = word_count_failures[-1]; # ... format feedback ...
             feedback_instruction += f"\nIMPORTANT FEEDBACK (Words): Previous failed (had {last_fail.details.get('word_count','N/A')}, target is {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}). Adjust."

        prompt = f"""Craft a unique Executive Value Proposition (approx. {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words) articulating the candidate's strategic fit for a senior leadership role focused on '{primary_theme}'.

**Primary Driver:** Candidate profile as {archetype_instruction}, addressing the core need for '{primary_theme}'.
**Strategic Angle:** Emphasize the ability to solve key industry problems like '{problem}' by delivering solutions such as '{solution}'.
**Key Differentiators:** Subtly weave in unique strengths relevant to the target role like {', '.join(differentiators[:self.constraints.K1_MIN_DIFFERENTIATORS])}.

**Career Context Snippets (Use for thematic inspiration and phrasing ONLY - DO NOT simply summarize these snippets or repeat specific metrics found here):**
{json.dumps(self.enriched_scaffold.get('experience_sections', [])[:2], indent=2)}

**NON-NEGOTIABLE REQUIREMENTS:**
1.  SENTENCE COUNT: MUST have strictly between {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences.
2.  TOTAL WORD COUNT: MUST be between {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words.
3.  KEYWORDS: Naturally integrate at least {self.constraints.K1_MIN_DIFFERENTIATORS} differentiating keywords.
4.  **UNIQUENESS:** Offer a distinct perspective on the candidate's value beyond summarizing past jobs. Focus on synthesized capabilities and forward-looking strategic impact. Avoid repeating specific metrics/details from the snippets.
5.  TONE: Strategic, executive-level, confident, visionary. Sentences must be fluid and well-structured, avoiding short, choppy phrasing.
6.  Output ONLY the value proposition text. Do NOT use markdown fences like ```.
7.  **Do NOT start any sentence with phrases like 'At [Company]', 'As [Title]', 'In my role as...', etc. Focus directly on the capability or value.**
{feedback_instruction}

Output ONLY the Executive Value Proposition text.
"""
        # Ensure K1_EXECUTIVE_SUMMARY_CONFIG exists
        try: reasoning_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG
        except AttributeError: logging.warning("K1_EXECUTIVE_SUMMARY_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        base_system = "You are an expert resume writer specializing in crafting concise, forward-looking Executive Value Propositions tailored to specific job descriptions."
        summary, call_count = self._call_gemini_api(
            prompt, reasoning_config, ResumeSection.K1_EXECUTIVE_SUMMARY.value, base_system,
            temperature_override=temperature_override
        )
        return summary, call_count

    def _generate_k10_skills(self, temperature_override: Optional[float] = None) -> Tuple[List[str], int]: # Now K.10
        total_calls = 0
        try:
            primary_theme_kw = self.thematic_analysis.primary_theme.get('keywords', []) # ... etc ...
            diff_kw = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None) # ... etc ...
            if comp_intel: diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
            combined_keywords = list(set(primary_theme_kw + diff_kw))[:15]

            prompt = f"""Based on the following key themes and keywords derived from a target job description, generate a list of exactly 12 relevant skills.

Key Themes/Keywords: {', '.join(combined_keywords)}

Requirements:
1.  Generate EXACTLY 12 skills.
2.  Each skill MUST be 1 to 3 words long.
3.  Focus on nouns and noun phrases (e.g., "Cloud Strategy", "GTM Execution", "AWS Partnerships"). Avoid verbs.
4.  Prioritize skills directly matching or closely related to the provided keywords.
5.  Output ONLY the list of skills, separated by newlines. Do not use bullets, numbers, markdown fences like ```, or any other formatting.
6.  **Do NOT include introductory phrases like 'Skills include:' etc.**

Example Output:
Skill One
Skill Two Name
Third Skill

Generate Skills List:
"""
            # Ensure K10_SKILLS_CONFIG exists
            try: reasoning_config = ReasoningConfig.K10_SKILLS_CONFIG
            except AttributeError: logging.warning("K10_SKILLS_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
            base_system = "You are an expert HR data analyst specializing in extracting concise, relevant skills from job requirements."
            skills_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, ResumeSection.K10_SKILLS.value, base_system, # Use K.10 enum
                temperature_override=temperature_override
            )
            total_calls += call_count

            # Parse and Validate Output
            skills_list_final = []
            skills_intermediate = [re.sub(r'^[•*\-\d\.]+\s*', '', s).strip() for s in skills_text.split('\n') if s.strip()]
            malformed_count = 0
            for skill in skills_intermediate:
                word_count = len(skill.split())
                if 1 <= word_count <= 3:
                    skills_list_final.append(skill)
                else:
                    logging.warning(f"{ResumeSection.K10_SKILLS.value}: Discarding malformed skill '{skill}' (words: {word_count})")
                    malformed_count += 1

            # Strict validation
            if len(skills_list_final) != 12:
                raise HopExecutionError(f"{ResumeSection.K10_SKILLS.value} generation failed: Expected 12 valid skills, found {len(skills_list_final)}. Preview: {skills_text[:100]}...")
            if malformed_count > 0:
                 raise HopExecutionError(f"{ResumeSection.K10_SKILLS.value} generation failed: Found {malformed_count} malformed skills discarded. Preview: {skills_text[:100]}...")

            return skills_list_final, total_calls

        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{ResumeSection.K10_SKILLS.value} processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{ResumeSection.K10_SKILLS.value} processing failed: {e}") from e

    # --- Overview Generation (K2, K3 - Uses K0-K11 scheme) ---
    def _generate_tailored_overview_for_experience(
        self,
        generated_bullets: List[Dict], # Accepts list of bullet dicts
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_id: str, # Should be the string value like "K.2_Unify_Overview"
        temperature_override: Optional[float] = None
    ) -> Tuple[str, int]: # Return tuple
        """
        Generates tailored overviews (K2, K3 in this version) by synthesizing bullets AND
        incorporating high-level themes from HOP-0.
        """
        if not generated_bullets:
            raise HopExecutionError(f"Cannot generate overview for {section_id}: No generated bullets provided.")

        # Extract bullet text robustly
        bullet_texts = []
        for i, bullet_data in enumerate(generated_bullets):
             text = (bullet_data.get('text', bullet_data.get('bullet_text', '')) if isinstance(bullet_data, dict) else str(bullet_data))
             if not text: logging.warning(f"Skipping empty bullet {i} for overview {section_id}"); continue
             bullet_texts.append(f"* {text.strip()}")
        if not bullet_texts: raise HopExecutionError(f"Cannot generate overview for {section_id}: All bullets invalid.")

        bullet_summary_input = "\n".join(bullet_texts)
        min_wc, max_wc = word_count_range

        # Extract Themes from HOP-0 (Same logic as v13.80)
        ta = self.thematic_analysis # ... (theme extraction logic remains the same) ...
        role_classification = getattr(ta, 'role_classification', {}) # ...
        primary_theme_data = getattr(ta, 'primary_theme', {}) # ...
        job_desc_lower = self.job_description.lower() # ...
        include_leadership_theme = False # ... determine themes ...
        include_strategic_theme = False # ...
        include_technical_theme = False # ...
        theme_instructions = [] # ... build theme instructions ...
        theme_prompt_section = "**KEY THEMES TO INCORPORATE...:**\n" + "\n".join(theme_instructions) if theme_instructions else ""

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

    def _generate_k2_unify_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.2
        generated_bullets = current_output.get(ResumeSection.K2_UNIFY_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K2_UNIFY_OVERVIEW.value}: Corresponding K.2 bullets missing/invalid.")

        # Ensure K2_UNIFY_OVERVIEW_CONFIG exists
        try: reasoning_config = ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG
        except AttributeError: logging.warning("K2_UNIFY_OVERVIEW_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT

        overview_text, call_count = self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=reasoning_config,
            section_id=ResumeSection.K2_UNIFY_OVERVIEW.value, # Pass K.2 value
            temperature_override=temperature_override
        )
        return overview_text, call_count

    def _generate_k3_ibm_overview(self, current_output: Dict, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.3
        generated_bullets = current_output.get(ResumeSection.K3_IBM_BULLETS.value)
        if not generated_bullets or not isinstance(generated_bullets, list):
             raise HopExecutionError(f"Cannot generate {ResumeSection.K3_IBM_OVERVIEW.value}: Corresponding K.3 bullets missing/invalid.")

        # Ensure K3_IBM_OVERVIEW_CONFIG exists
        try: reasoning_config = ReasoningConfig.K3_IBM_OVERVIEW_CONFIG
        except AttributeError: logging.warning("K3_IBM_OVERVIEW_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT

        overview_text, call_count = self._generate_tailored_overview_for_experience(
            generated_bullets=generated_bullets,
            word_count_range=(self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX),
            reasoning_config=reasoning_config,
            section_id=ResumeSection.K3_IBM_OVERVIEW.value, # Pass K.3 value
            temperature_override=temperature_override
        )
        return overview_text, call_count

    # --- Narrative Generation Methods (K4, K5, K6 - Uses K0-K11 scheme) ---
    def _generate_k4_tradersense_narrative(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.4
        min_wc = 45 # Example range, adjust if needed
        max_wc = 65
        target_sc = 3
        section_id = ResumeSection.K4_TRADERSENSE_NARRATIVE.value # Use K.4 value

        # Gather Context (Similar logic, find TraderSense highlights in master)
        ts_exp = next((exp for exp in self.master_resume.get('professional_experience', []) if 'TraderSense' in exp.get('company', '')), None)
        master_highlights = ts_exp.get('highlights', []) if ts_exp else []
        if not master_highlights: raise HopExecutionError(f"Cannot generate {section_id}: Master highlights for TraderSense not found.")
        master_context = "\n".join([f"- {h}" for h in master_highlights])
        # RAG signals (Similar logic)
        rag_keywords = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: rag_keywords = getattr(comp_intel, 'differentiator_keywords', [])[:5]
        rag_signals = ["high-frequency trading", "low-latency", "risk controls", "backtesting", "FIX protocol", "cloud infrastructure"] # Example relevant signals
        combined_signals = list(set(rag_keywords + rag_signals))[:7]

        # Build Prompt
        prompt = f"""Generate a concise narrative block (exactly {target_sc} sentences, total {min_wc}-{max_wc} words) summarizing the TraderSense CTO experience, bridging it towards roles involving {', '.join(combined_signals)}.

**Focus:** Emphasize the early adoption of cloud, low-latency systems, HFT, risk management, and quantitative analysis, linking them to broader technical leadership and system design capabilities relevant today. Use past tense.

**Master Resume Highlights (Context Only):**
{master_context}

**ABSOLUTELY CRITICAL:**
1.  Output EXACTLY {target_sc} sentences.
2.  Total word count MUST be strictly between {min_wc} and {max_wc} words.
3.  Bridge the specific HFT context to broader, transferable skills ({', '.join(combined_signals)}).
4.  Use PAST TENSE.
5.  **Do NOT start sentences with phrases like 'At TraderSense', 'As CTO', etc.**
6.  Output ONLY the {target_sc} sentences as a single paragraph. Do NOT use markdown fences or bullet points.

**Generated Narrative ({min_wc}-{max_wc} words total, {target_sc} sentences):**
"""
        # Ensure K4_TRADERSENSE_NARRATIVE_CONFIG exists
        try: reasoning_config = ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG
        except AttributeError: logging.warning("K4_TRADERSENSE_NARRATIVE_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        base_system = "You are an expert resume writer crafting concise narratives that bridge early startup technical leadership to current capabilities."

        narrative_text, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, base_system,
            temperature_override=temperature_override
        )

        # Basic post-check
        final_wc = count_words_ms_word_style(narrative_text); final_sc = _count_sentences(narrative_text)
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} narrative WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if final_sc != target_sc: logging.warning(f"{section_id} narrative SC ({final_sc}) is not {target_sc}.")

        return narrative_text, call_count

    def _generate_k5_ey_narrative(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.5
        min_wc = self.constraints.EY_NARRATIVE_WORD_COUNT_MIN
        max_wc = self.constraints.EY_NARRATIVE_WORD_COUNT_MAX
        target_sc = 3
        section_id = ResumeSection.K5_EY_NARRATIVE.value # Use K.5 value

        # Gather Context (Similar logic, find EY highlights in master)
        ey_exp = next((exp for exp in self.master_resume.get('professional_experience', []) if 'Ernst & Young' in exp.get('company', '')), None)
        master_highlights = ey_exp.get('highlights', []) if ey_exp else []
        if not master_highlights: raise HopExecutionError(f"Cannot generate {section_id}: Master highlights for EY not found.")
        master_context = "\n".join([f"- {h}" for h in master_highlights])
        # RAG / K.0 Themes (Similar logic)
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key capabilities')
        rag_keywords = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: rag_keywords = getattr(comp_intel, 'differentiator_keywords', [])[:5]
        k0_themes = ["Leadership", "Strategic Vision", "Executive Communication", "Risk Management", "Client Advisory"] # Example K.0 themes

        # Build Prompt
        prompt = f"""Generate a concise narrative block (exactly {target_sc} sentences, total {min_wc}-{max_wc} words) summarizing the Ernst & Young Principal experience.

**Focus (70%):** Emphasize how this experience built foundational capabilities in **{', '.join(k0_themes)}** and relates to current target themes like **{', '.join(rag_keywords)}**. Use past tense.

**Context (30%):** Ground the narrative in the technical/quantitative achievements from the master resume highlights below (e.g., model validation, risk frameworks, regulatory compliance - Basel III, Solvency II, CCAR).

**Master Resume Highlights (Context Only):**
{master_context}

**ABSOLUTELY CRITICAL:**
1.  Output EXACTLY {target_sc} sentences.
2.  Total word count MUST be strictly between {min_wc} and {max_wc} words.
3.  Weight content ~70% towards transferable executive themes/RAG signals, 30% towards specific technical context.
4.  Use PAST TENSE.
5.  **Do NOT start sentences with phrases like 'At Ernst & Young', 'As Principal', etc.**
6.  Output ONLY the {target_sc} sentences as a single paragraph. Do NOT use markdown fences or bullet points.

**Generated Narrative ({min_wc}-{max_wc} words total, {target_sc} sentences):**
"""
        # Ensure K5_EY_NARRATIVE_CONFIG exists
        try: reasoning_config = ReasoningConfig.K5_EY_NARRATIVE_CONFIG
        except AttributeError: logging.warning("K5_EY_NARRATIVE_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        base_system = "You are an expert resume writer crafting concise narratives that bridge past consulting experience to current executive capabilities."

        narrative_text, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, base_system,
            temperature_override=temperature_override
        )

        # Basic post-check
        final_wc = count_words_ms_word_style(narrative_text); final_sc = _count_sentences(narrative_text)
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} narrative WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if final_sc != target_sc: logging.warning(f"{section_id} narrative SC ({final_sc}) is not {target_sc}.")

        return narrative_text, call_count

    def _generate_k6_early_career_narrative(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.6
        min_wc = self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN
        max_wc = self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX
        target_sc = 3
        section_id = ResumeSection.K6_EARLY_CAREER_NARRATIVE.value # Use K.6 value

        # Gather Context (Similar logic, find Early Career highlights/overview in master)
        ec_exp = next((exp for exp in self.master_resume.get('professional_experience', []) if 'Early Career' in exp.get('company', '')), None)
        master_highlights = ec_exp.get('highlights', []) if ec_exp else []
        # Note: v13.80 master removed overview, rely only on highlights here
        if not master_highlights: raise HopExecutionError(f"Cannot generate {section_id}: Master highlights for Early Career not found.")
        master_context = "\n".join([f"- {h}" for h in master_highlights])
        # RAG signals (Similar logic)
        rag_keywords = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: rag_keywords = getattr(comp_intel, 'differentiator_keywords', [])[:5]
        rag_signals = ["quantitative analysis", "modeling", "data-driven", "problem-solving", "analytical foundation"] # Example signals
        combined_signals = list(set(rag_keywords + rag_signals))[:7]

        # Build Prompt
        prompt = f"""Generate a concise narrative block (exactly {target_sc} sentences, total {min_wc}-{max_wc} words) describing the Early Career actuarial experience and bridging it to a technology career.

**Weighting:**
* **1/3 Focus:** Ground the narrative in the specific technical work done (stochastic pricing, actuarial models, valuation, hedging analysis). Use context below.
* **2/3 Focus:** Tell the story of how this quantitative foundation prepared the candidate for a technology career, weaving in relevant concepts like **{', '.join(combined_signals)}**.

**Master Resume Highlights (Context Only):**
{master_context}

**ABSOLUTELY CRITICAL:**
1.  Output EXACTLY {target_sc} sentences.
2.  Total word count MUST be strictly between {min_wc} and {max_wc} words.
3.  Follow the 1/3 technical, 2/3 storytelling/bridge weighting.
4.  Use PAST TENSE.
5.  Do NOT include senior themes like 'Executive Leadership', 'Strategic Vision', etc.
6.  **Do NOT start sentences with phrases like 'During my early career', 'As an analyst', etc.**
7.  Output ONLY the {target_sc} sentences as a single paragraph. Do NOT use markdown fences or bullet points.

**Generated Narrative ({min_wc}-{max_wc} words total, {target_sc} sentences):**
"""
        # Ensure K6_EARLY_CAREER_NARRATIVE_CONFIG exists
        try: reasoning_config = ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG
        except AttributeError: logging.warning("K6_EARLY_CAREER_NARRATIVE_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        base_system = "You are an expert resume writer crafting concise narratives that bridge early quantitative experience to a technology career path."

        narrative_text, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, base_system,
            temperature_override=temperature_override
        )

        # Basic post-check
        final_wc = count_words_ms_word_style(narrative_text); final_sc = _count_sentences(narrative_text)
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} narrative WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if final_sc != target_sc: logging.warning(f"{section_id} narrative SC ({final_sc}) is not {target_sc}.")

        return narrative_text, call_count

    # --- Bullet Generation Helpers (_validate_llm_bullet_selection, _rewrite_bullet_for_word_count, _validate_and_potentially_rewrite_bullets, _generate_lightly_customized_bullets, _generate_synthetic_bullets - Used ONLY for K2, K3, K9 in this version) ---
    # These helpers remain functionally identical to the v13.80 versions, just called with different section IDs/enums.

    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id_str: str) -> List[Dict]:
        """Validates LLM bullet selection. Raises HopExecutionError on failure."""
        if len(selected_bullets_text) != expected_count: raise HopExecutionError(f"{section_id_str} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}.")
        validated_bullets = []; master_texts_map = {b['bullet_text'].strip(): b for b in master_bullets_structured if 'bullet_text' in b}; returned_texts_set = set()
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
        """Rewrites a bullet for word count. Raises HopExecutionError on failure."""
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
        """Checks word count, attempts rewrite if needed. Returns (final_list, total_rewrite_calls)."""
        final_bullets = []; total_rewrite_calls = 0; logging.info(f"  Validating word count for {section_id_str} ({min_target}-{max_target})")
        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict): raise HopExecutionError(f"Invalid item in bullet list for {section_id_str}[{i}]")
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', '')); original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            try: word_count = count_words_ms_word_style(original_text)
            except: word_count = bullet_data.get('word_count', 0) # Fallback to potentially stored count
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
        """Creates 'Customized' bullets for K.2, K.3, K.9."""
        total_calls = 0
        try:
            if not source_bullets_text: return [], 0
            primary_theme_kw = thematic_analysis.primary_theme.get('keywords', []) if thematic_analysis.primary_theme else []
            diff_kw = []
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
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
        """Creates 'Synthetic' bullets for K.2, K.3, K.9."""
        total_calls = 0
        try:
            if count <= 0: return [], 0
            primary_theme = thematic_analysis.primary_theme.get('name', 'key responsibilities') if thematic_analysis.primary_theme else 'key responsibilities'
            primary_theme_kw = thematic_analysis.primary_theme.get('keywords', []) if thematic_analysis.primary_theme else []
            diff_kw = []
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
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

    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            provenance_targets: Dict[str, int],
            reasoning_config: ReasoningConfig,
            section_id_enum: ResumeSection, # Use Enum object here
            temperature_override: Optional[float] = None
    ) -> Tuple[List[Dict], int]: # Return tuple (list_of_dicts, total_calls)
        """
        Orchestrator for V/C/S bullet generation (K.2, K.3, K.9 in this version).
        Raises HopExecutionError on failures. Returns (final_bullet_list, total_calls).
        """
        section_id_str = section_id_enum.value # Get string value for logging/API calls
        logging.info(f"  Generating bullets for {section_id_enum.name} ({section_id_str}) (Targets: {provenance_targets})")
        total_calls_for_section = 0
        final_bullets = [] # List to hold generated bullet dicts

        # --- 1. Get Master Bullets ---
        exp_section = next((exp for exp in self.master_resume.get('professional_experience', []) if company_name in exp.get('company', '')), None)
        if not exp_section: raise HopExecutionError(f"Master data not found for '{company_name}' needed by {section_id_enum.name}")
        master_bullets_key = "bullet_pool" if "bullet_pool" in exp_section else "highlights"
        master_bullets_source = exp_section.get(master_bullets_key, [])
        if not isinstance(master_bullets_source, list): raise HopExecutionError(f"{section_id_enum.name} master '{master_bullets_key}' not list.")
        master_bullets_structured = []
        for bullet_text in master_bullets_source: # Populate master_bullets_structured
             if isinstance(bullet_text, str) and bullet_text.strip():
                 cleaned_text = bullet_text.strip()
                 master_bullets_structured.append({"bullet_text": cleaned_text, "text": cleaned_text, "provenance": BulletProvenance.Verbatim.value, "word_count": count_words_ms_word_style(cleaned_text)})
             else: logging.warning(f"Skipping invalid master bullet for {company_name}: {bullet_text}")

        verbatim_count = provenance_targets.get('Verbatim', 0); customized_count = provenance_targets.get('Customized', 0); synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        if not master_bullets_structured and (verbatim_count > 0 or customized_count > 0): raise HopExecutionError(f"{section_id_enum.name} Cannot select/customize: No valid master bullets.")

        # --- 2. Select Verbatim Bullets ---
        verbatim_bullets_selected = []
        if verbatim_count > 0:
            logging.info(f"    Selecting {verbatim_count} Verbatim bullets...")
            if len(master_bullets_structured) < verbatim_count: raise HopExecutionError(f"{section_id_enum.name} Cannot select {verbatim_count} Verbatim.")
            master_bullets_text_list = [b['bullet_text'] for b in master_bullets_structured]; keywords_for_prompt = []
            if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
                 comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
                 if comp_intel: keywords_for_prompt = getattr(comp_intel, 'differentiator_keywords', [])[:10]
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
            except Exception as e: raise HopExecutionError(f"{section_id_enum.name} Verbatim selection failed unexpectedly: {e}") from e


        # --- 3. Generate Customized Bullets ---
        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} bullets...")
            used_verbatim_texts = {b['bullet_text'] for b in verbatim_bullets_selected}; available_for_custom = [b for b in master_bullets_structured if b['bullet_text'] not in used_verbatim_texts]
            if len(available_for_custom) < customized_count: raise HopExecutionError(f"{section_id_enum.name} Cannot customize {customized_count}: Not enough unique bullets remaining.")
            random.shuffle(available_for_custom); candidates_for_custom = available_for_custom[:customized_count]; source_texts_for_custom = [b['bullet_text'] for b in candidates_for_custom]
            try:
                customized_bullets, calls_c = self._generate_lightly_customized_bullets(source_texts_for_custom, f"{section_id_str}_CustomC", self.thematic_analysis, temperature_override)
                total_calls_for_section += calls_c
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he: raise he # Propagate customization errors
            except Exception as e: raise HopExecutionError(f"{section_id_enum.name} Customization failed unexpectedly: {e}") from e

        # --- 4. Generate Synthetic Bullets ---
        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic bullets...")
            context_bullets_text = '\n'.join([f"- {b.get('text', '')}" for b in final_bullets if b.get('text')])
            try:
                synthetic_bullets, calls_s = self._generate_synthetic_bullets(synthetic_count, company_name, self.job_description, self.thematic_analysis, context_bullets_text, reasoning_config, f"{section_id_str}_SynthS", temperature_override)
                total_calls_for_section += calls_s
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he: raise he # Propagate synthetic generation errors
            except Exception as e: raise HopExecutionError(f"{section_id_enum.name} Synthetic generation failed unexpectedly: {e}") from e

        # --- 5. Final Count Check ---
        if len(final_bullets) != total_expected_count: raise HopExecutionError(f"{section_id_enum.name} Internal Error: Generated {len(final_bullets)}, expected {total_expected_count}.")

        # --- 6. Word Count Validation & Rewrite ---
        target_range = self.BULLET_WORD_COUNT_RANGES.get(section_id_enum) # Use Enum object as key
        if target_range is None: raise HopExecutionError(f"Config Error: WC range not found for {section_id_enum.name}.")
        min_target, max_target = target_range; logging.info(f"    Validating word counts ({min_target}-{max_target})...")
        try:
            final_bullets_validated, calls_rewrite = self._validate_and_potentially_rewrite_bullets(final_bullets, min_target, max_target, section_id_str, temperature_override)
            total_calls_for_section += calls_rewrite
            final_bullets = final_bullets_validated
        except HopExecutionError as he: raise he # Propagate validation/rewrite errors
        except Exception as e: raise HopExecutionError(f"{section_id_enum.name} Word count validation/rewrite failed unexpectedly: {e}") from e

        # --- 7. Reorder Bullets (Skip for Competencies K.9 in this version) ---
        if section_id_enum != ResumeSection.K9_COMPETENCIES:
            logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
            current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets)]
            current_bullets_text_input = '\n'.join(current_bullets_text_list)
            keywords_for_prompt = []
            if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
                 comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
                 if comp_intel: keywords_for_prompt = getattr(comp_intel, 'differentiator_keywords', [])[:10]
            prompt_reorder = f"""Reorder the following resume bullet points for maximum impact and relevance based on the target keywords. Output ONLY the reordered bullet points, exactly as provided but in the new order, one per line. Do not add numbers, prefixes, commentary, or markdown.

**Bullets to Reorder ({company_name}):**
{current_bullets_text_input}

**Target Job Description Keywords (Prioritize relevance to these):**
{', '.join(keywords_for_prompt) or 'N/A'}

**Instructions:** Analyze the bullets and keywords. Determine the optimal order, placing the most relevant bullets first.

**REORDERED BULLETS (Exactly {len(final_bullets)}, one per line, verbatim text):**
"""
            system_prompt_reorder = "You are an expert resume editor who reorders bullet points for maximum impact based on relevance to target keywords."
            # --- START FIX: Correct indentation for except blocks ---
            try:
                # Ensure ReasoningConfig.DEFAULT exists
                try: default_reasoning = ReasoningConfig.DEFAULT
                except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); default_reasoning = ReasoningConfig() # Fallback

                response_reorder, calls_reorder = self._call_gemini_api(prompt_reorder, default_reasoning, f"{section_id_str}_Reorder", system_prompt_reorder, temperature_override=temperature_override)
                total_calls_for_section += calls_reorder
                reordered_texts_raw = [line.strip() for line in response_reorder.split('\n') if line.strip()]
                reordered_texts = [re.sub(r"^\d+\.\s*", "", txt).strip() for txt in reordered_texts_raw]

                # Validation of Reordering
                if len(reordered_texts) != total_expected_count: raise HopExecutionError(f"{section_id_enum.name} Reordering failed: Count mismatch (Expected {total_expected_count}, Got {len(reordered_texts)}). Preview: {reordered_texts_raw[:3]}")
                final_ordered_bullets_dicts = []; original_texts_map = {b.get('text'): b for b in final_bullets}; used_original_texts = set()
                for reordered_text in reordered_texts:
                    matched_dict = original_texts_map.get(reordered_text)
                    if matched_dict:
                        if reordered_text in used_original_texts: raise HopExecutionError(f"{section_id_enum.name} Reordering failed: Duplicate bullet found in output: '{reordered_text[:50]}...'")
                        final_ordered_bullets_dicts.append(matched_dict)
                        used_original_texts.add(reordered_text)
                    else: raise HopExecutionError(f"{section_id_enum.name} Reordering failed: LLM modified bullet text. Expected verbatim. Got: '{reordered_text[:50]}...'")
                if len(final_ordered_bullets_dicts) != total_expected_count: raise HopExecutionError(f"{section_id_enum.name} Reordering failed: Final count mismatch after matching ({len(final_ordered_bullets_dicts)} vs {total_expected_count}).")
                logging.info(f"  ✓ Reordering complete for {section_id_enum.name}.")
                return final_ordered_bullets_dicts, total_calls_for_section
            except HopExecutionError as he:
                raise he # Propagate reorder/validation errors
            except Exception as e:
                raise HopExecutionError(f"{section_id_enum.name} Reordering failed unexpectedly: {e}") from e
            # --- END FIX ---
        else:
            logging.info(f"    Skipping reordering for Competencies section ({section_id_enum.name}).")
            return final_bullets, total_calls_for_section # Return bullets without reordering for K.9
   
    def _generate_k2_unify_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # K.2
        targets = self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K2_UNIFY_BULLETS, {})
        if not targets: raise HopExecutionError("Provenance targets missing for K.2 Unify")
        # Ensure K2_UNIFY_BULLETS_CONFIG exists
        try: reasoning_config = ReasoningConfig.K2_UNIFY_BULLETS_CONFIG
        except AttributeError: logging.warning("K2_UNIFY_BULLETS_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        return self._generate_tailored_bullets_for_experience(
            company_name="Unify Consulting", provenance_targets=targets,
            reasoning_config=reasoning_config, section_id_enum=ResumeSection.K2_UNIFY_BULLETS, # Pass Enum
            temperature_override=temperature_override
        )

    def _generate_k3_ibm_bullets(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # K.3
        targets = self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K3_IBM_BULLETS, {})
        if not targets: raise HopExecutionError("Provenance targets missing for K.3 IBM")
        # Ensure K3_IBM_BULLETS_CONFIG exists
        try: reasoning_config = ReasoningConfig.K3_IBM_BULLETS_CONFIG
        except AttributeError: logging.warning("K3_IBM_BULLETS_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
        return self._generate_tailored_bullets_for_experience(
            company_name="IBM", provenance_targets=targets,
            reasoning_config=reasoning_config, section_id_enum=ResumeSection.K3_IBM_BULLETS, # Pass Enum
            temperature_override=temperature_override
        )

    def _generate_k9_competencies(self, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]: # K.9
        """Generates K.9 Competencies using the bullet generation framework."""
        fake_company_name = "Strategic Competencies Section"; competencies_list_source = self.master_resume.get("strategic_and_technical_competencies", [])
        if not competencies_list_source: raise HopExecutionError("Master resume missing 'strategic_and_technical_competencies'.")
        # Temporarily modify master resume structure
        temp_master_resume = copy.deepcopy(self.master_resume);
        if "professional_experience" not in temp_master_resume: temp_master_resume["professional_experience"] = []
        temp_master_resume["professional_experience"].append({"company": fake_company_name, "bullet_pool": competencies_list_source})
        original_master_resume = self.master_resume; self.master_resume = temp_master_resume
        total_calls = 0; generated_competencies = []
        try:
            targets = self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K9_COMPETENCIES, {})
            if not targets: raise HopExecutionError("Provenance targets missing for K.9 Competencies")
            # Ensure K9_COMPETENCIES_CONFIG exists
            try: reasoning_config = ReasoningConfig.K9_COMPETENCIES_CONFIG
            except AttributeError: logging.warning("K9_COMPETENCIES_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT

            generated_competencies, calls = self._generate_tailored_bullets_for_experience(
                company_name=fake_company_name, provenance_targets=targets,
                reasoning_config=reasoning_config, section_id_enum=ResumeSection.K9_COMPETENCIES, # Pass Enum
                temperature_override=temperature_override
            )
            total_calls = calls
        finally: self.master_resume = original_master_resume # Restore

        # Post-processing (Same logic)
        for item in generated_competencies:
            if isinstance(item, dict) and 'text' in item:
                cleaned_text = re.sub(r'^\*\s*\*\*(.*?):\*\*\s*', '', item['text']).strip()
                cleaned_text = re.sub(r'^[•*]\s*', '', cleaned_text).strip()
                item['text'] = cleaned_text
                item['word_count'] = count_words_ms_word_style(cleaned_text)

        return generated_competencies, total_calls

    # --- Cover Letter Generation (K11 - Uses K0-K11 scheme) ---
    def _generate_k11_cover_letter(self, temperature_override: Optional[float] = None) -> Tuple[str, int]: # K.11
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'key requirements') # ... etc (context gathering) ...
        differentiators = []; comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None) # ... etc ...
        if comp_intel: differentiators = getattr(comp_intel, 'differentiator_keywords', [])
        narratives_data = getattr(self.thematic_analysis, 'problem_solution_narratives', None); narratives = narratives_data if isinstance(narratives_data, dict) else {}
        problem = narratives.get('common_problems', ['solving key challenges'])[0] if narratives.get('common_problems') else 'solving key challenges'
        solution = narratives.get('solution_patterns', ['delivering impactful results'])[0] if narratives.get('solution_patterns') else 'delivering impactful results'

        owner_info = self.master_resume.get('owner', {}); contact_info = owner_info.get('contact', {})
        try: # Get expected signature (Same logic)
            expected_signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'), email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'), linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except NameError: raise HopExecutionError("COVER_LETTER_SIGNATURE_TEMPLATE not defined.")
        except KeyError as e: raise HopExecutionError(f"Missing key in COVER_LETTER_SIGNATURE_TEMPLATE format: {e}")

        # Get experience snippets (Use K.2/K.3 from enriched_scaffold in this version)
        exp_snippets = ""
        # Use K.2 Unify Overview/Bullets
        unify_overview = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        # Use K.3 IBM Overview/Bullets
        ibm_overview = self.enriched_scaffold.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets = self.enriched_scaffold.get(ResumeSection.K3_IBM_BULLETS.value, [])

        if unify_overview or unify_bullets:
             exp_snippets += f"Recent Experience (Unify):\n{unify_overview}\n"
             exp_snippets += "\n".join([f"- {b.get('text', '')}" for b in unify_bullets[:2] if b.get('text')]) + "\n"
        if ibm_overview or ibm_bullets:
             exp_snippets += f"Prior Experience (IBM):\n{ibm_overview}\n"
             exp_snippets += "\n".join([f"- {b.get('text', '')}" for b in ibm_bullets[:2] if b.get('text')]) + "\n"
        if not exp_snippets: exp_snippets = "Candidate has extensive experience in relevant areas.\n"

        prompt = f"""Write a professional cover letter for the candidate applying for a role focused on '{primary_theme}'.

JOB DESCRIPTION KEYWORDS/DIFFERENTIATORS: {', '.join(differentiators[:5])}
CANDIDATE'S RELEVANT EXPERIENCE (Snippets for context):
{exp_snippets}
NARRATIVE CONTEXT (Problem candidate solves): "{problem}" -> (Solution candidate provides): "{solution}"

INSTRUCTIONS:
1.  **Standard Letter Format:** Date ({datetime.now().strftime("%B %d, %Y")}), recipient placeholder, salutation, 3 body paragraphs, closing, EXACT signature block below.
2.  **Paragraph 1 (Hook):** State role, enthusiasm, connect expertise ('{primary_theme}') to requirements. Target: {self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX} words.
3.  **Paragraph 2 (Proof):** Examples solving "{problem}" with solutions like "{solution}", using snippets/keywords. Quantify. Weave in 2-3 differentiators. Target: {self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX} words.
4.  **Paragraph 3 (Vision/Fit):** Reiterate interest, connect to company goals, call to action. Target: {self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX} words.
5.  **Signature:** Append EXACTLY:
{expected_signature}

CRITICAL:
1. Adhere strictly to paragraph word counts.
2. Ensure exact signature block with forced line breaks.
3. Output ONLY complete cover letter text. No fences (```).
4. **Do NOT start paragraphs/sentences with 'At [Company]', 'As [Title]', etc.**

COVER LETTER:
"""
        total_calls = 0
        try:
            # Ensure K11_COVER_LETTER_CONFIG exists
            try: reasoning_config = ReasoningConfig.K11_COVER_LETTER_CONFIG
            except AttributeError: logging.warning("K11_COVER_LETTER_CONFIG missing. Using DEFAULT."); reasoning_config = ReasoningConfig.DEFAULT
            base_system = f"You are an expert executive ghostwriter crafting tailored cover letters."
            cover_letter_text, call_count = self._call_gemini_api(
                prompt, reasoning_config, ResumeSection.K11_COVER_LETTER.value, base_system, # Use K.11 value
                temperature_override=temperature_override
            )
            total_calls += call_count

            # Post-generation Structure Fixes (Same logic, use K.11 in logs)
            fixed_text = cover_letter_text.strip(); current_date_str = datetime.now().strftime("%B %d, %Y")
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text): fixed_text = f"{current_date_str}\n\n{fixed_text}"; logging.warning(f"{ResumeSection.K11_COVER_LETTER.value}: Added missing date.")
            recipient_placeholder = "Hiring Manager\n[Company Name]"
            if recipient_placeholder not in fixed_text: fixed_text = re.sub(r"(\w+ \d{1,2}, \d{4}\s*)", rf"\1\n{recipient_placeholder}\n\n", fixed_text, count=1); # ... log error if fails ...
            salutation = "Dear Hiring Manager,"
            if salutation not in fixed_text: fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\s*)", rf"\1\n{salutation}\n\n", fixed_text, count=1); # ... log error if fails ...
            closing = "Sincerely,"
            if expected_signature in fixed_text and closing not in fixed_text.split(expected_signature)[0]: fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
            if not fixed_text.rstrip().endswith(expected_signature.rstrip()): logging.warning(f"{ResumeSection.K11_COVER_LETTER.value}: Signature block missing/malformed. Fixing..."); fixed_text = re.sub(r'\n*Sincerely,?\n*.*$', '', fixed_text.rstrip(), flags=re.MULTILINE); fixed_text += f"\n\n{closing}\n\n{expected_signature}"; # ... log error if still fails ...

            # Final basic checks
            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text: raise HopExecutionError(f"{ResumeSection.K11_COVER_LETTER.value} generation failed (placeholder detected).")
            if not all(x in fixed_text for x in [current_date_str, recipient_placeholder, salutation, closing, expected_signature]): logging.warning(f"{ResumeSection.K11_COVER_LETTER.value}: Structure may still be incomplete after fixes.")

            return fixed_text.strip(), total_calls

        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{ResumeSection.K11_COVER_LETTER.value} generation failed unexpectedly: {e}") from e

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
# Validation Context (HELPER FOR HOP-5)
# ============================================================================
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
    Calculates metrics only when needed by a rule. (Updated for v13.90 K0-K11)
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
            # Fallback for accessing cached rule details directly (e.g., VG_TOTAL_WORD_COUNT)
            if name.startswith("VG_") or name.startswith("WORD_") or name.startswith("UNIFY_") or name.startswith("COVER_LETTER_"):
                 if name in self._cache:
                      return self._cache[name]

            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or calculation method '_calculate_{name}'")

    # --- Calculation Methods (Updated for K0-K11 Enums) ---

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
                    total += count_words_ms_word_style(value)
                elif isinstance(value, list):
                    # Handle lists which might contain strings or dicts (like bullets)
                    total += sum(count_words_ms_word_style(item.get('text', str(item))) if isinstance(item, dict) else count_words_ms_word_style(str(item)) for item in value)
        details = {'total_words': total, 'min': ContentConstraintsConfig.TOTAL_WORD_COUNT_MIN, 'max': ContentConstraintsConfig.TOTAL_WORD_COUNT_MAX}
        self._cache["VG_TOTAL_WORD_COUNT"] = details # Cache for rule
        return total # Return the count directly for other calculations

    def _calculate_unify_words(self):
        """Calculates total words for K.2 Unify (Overview + Bullets)."""
        # Use K.2 enums
        unify_overview = self.staging_buffer.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets = self.staging_buffer.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        overview_wc = count_words_ms_word_style(unify_overview)
        bullets_wc = sum(count_words_ms_word_style(b.get('text', '')) for b in unify_bullets if isinstance(b, dict))
        return overview_wc + bullets_wc

    def _calculate_ibm_words(self):
        """Calculates total words for K.3 IBM (Overview + Bullets)."""
        # Use K.3 enums
        ibm_overview = self.staging_buffer.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets = self.staging_buffer.get(ResumeSection.K3_IBM_BULLETS.value, [])
        overview_wc = count_words_ms_word_style(ibm_overview)
        bullets_wc = sum(count_words_ms_word_style(b.get('text', '')) for b in ibm_bullets if isinstance(b, dict))
        return overview_wc + bullets_wc

    def _calculate_unify_ibm_percent(self):
        """Calculates combined percentage for K.2 Unify + K.3 IBM."""
        total_w = self.total_words # Trigger total calculation
        if total_w == 0: return 0.0
        percent = (self.unify_words + self.ibm_words) / total_w * 100.0
        details = {'unify_ibm_percent': percent, 'min': ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MIN, 'max': ContentConstraintsConfig.UNIFY_IBM_COMBINED_PERCENT_MAX}
        self._cache["WORD_DISTRIBUTION_UNIFY_IBM"] = details # Cache for rule
        return percent

    def _calculate_unify_ibm_ratio(self):
        """Calculates ratio K.2 Unify / K.3 IBM."""
        ibm_w = self.ibm_words # Trigger IBM calculation
        unify_w = self.unify_words # Trigger Unify calculation
        if ibm_w == 0: ratio = 0.0
        else: ratio = unify_w / ibm_w
        details = {'unify_ibm_ratio': ratio, 'min': ContentConstraintsConfig.UNIFY_IBM_RATIO_MIN, 'max': ContentConstraintsConfig.UNIFY_IBM_RATIO_MAX}
        self._cache["UNIFY_IBM_RATIO"] = details # Cache for rule
        return ratio

    def _calculate_k1_sentence_count_details(self):
        """Calculates details needed for VG_SENTENCE_COUNT_K1."""
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        count = _count_sentences(k1_text)
        details = {
            'sentence_count': count,
            'min': ContentConstraintsConfig.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
            'max': ContentConstraintsConfig.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        }
        self._cache["VG_SENTENCE_COUNT_K1"] = details
        return details

    def _calculate_k1_word_count_details(self):
        """Calculates details needed for VG_WORD_COUNT_K1."""
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        count = count_words_ms_word_style(k1_text)
        details = {
            'word_count': count,
            'min': ContentConstraintsConfig.EXEC_SUMMARY_WORD_COUNT_MIN,
            'max': ContentConstraintsConfig.EXEC_SUMMARY_WORD_COUNT_MAX
        }
        self._cache["VG_WORD_COUNT_K1"] = details
        return details

    def _calculate_k2_overview_details(self):
        """Calculates details for K.2 Unify Overview rules."""
        text = self.staging_buffer.get(ResumeSection.K2_UNIFY_OVERVIEW.value, '')
        word_count = count_words_ms_word_style(text)
        sentence_count = _count_sentences(text)
        details = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'min_wc': ContentConstraintsConfig.UNIFY_OVERVIEW_WORD_COUNT_MIN,
            'max_wc': ContentConstraintsConfig.UNIFY_OVERVIEW_WORD_COUNT_MAX,
            'min_sc': 1, # Target is 1-2 sentences
            'max_sc': 2
        }
        self._cache["VG_WORD_COUNT_K2_OVERVIEW"] = details # Use K2 rule ID
        self._cache["VG_SENTENCE_COUNT_K2_OVERVIEW"] = details # Use K2 rule ID
        return details

    def _calculate_k3_overview_details(self):
        """Calculates details for K.3 IBM Overview rules."""
        text = self.staging_buffer.get(ResumeSection.K3_IBM_OVERVIEW.value, '')
        word_count = count_words_ms_word_style(text)
        sentence_count = _count_sentences(text)
        details = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'min_wc': ContentConstraintsConfig.IBM_OVERVIEW_WORD_COUNT_MIN,
            'max_wc': ContentConstraintsConfig.IBM_OVERVIEW_WORD_COUNT_MAX,
            'min_sc': 1, # Target is 1-2 sentences
            'max_sc': 2
        }
        self._cache["VG_WORD_COUNT_K3_OVERVIEW"] = details # Use K3 rule ID
        self._cache["VG_SENTENCE_COUNT_K3_OVERVIEW"] = details # Use K3 rule ID
        return details

    def _calculate_headline_details(self):
        """Calculates details for headline rules."""
        headline_text = self.staging_buffer.get(ResumeSection.K0_HEADLINE.value, '')
        word_count = count_words_ms_word_style(headline_text)
        details = {
            'word_count': word_count,
            'headline': headline_text,
            'min': ContentConstraintsConfig.HEADLINE_WORD_COUNT_MIN,
            'max': ContentConstraintsConfig.HEADLINE_WORD_COUNT_MAX,
            'comp_min': ContentConstraintsConfig.HEADLINE_COMPONENT_WORDS_MIN,
            'comp_max': ContentConstraintsConfig.HEADLINE_COMPONENT_WORDS_MAX
        }
        self._cache["VG_HEADLINE_WORD_COUNT"] = details
        self._cache["VG_HEADLINE_NO_TITLES"] = details
        self._cache["VG_HEADLINE_NO_COMMAS"] = details
        self._cache["VG_HEADLINE_COMPONENT_WC"] = details
        return details

    def _calculate_cover_letter_jd_similarity(self):
        """Calculates cosine similarity between cover letter (K.11) and JD."""
        cover_letter_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '') # Use K.11 enum
        if not cover_letter_text or not self.job_description:
            similarity = 0.0
        else:
            # Use DuplicateDetector for similarity calculation
            try:
                dd = DuplicateDetector()
                similarity = dd._calculate_cosine_similarity(cover_letter_text, self.job_description)
            except Exception as e:
                logging.warning(f"Error calculating cover letter similarity: {e}")
                similarity = 0.0 # Default on error

        details = {
            "cover_letter_jd_similarity": similarity,
            "min_sim": ContentConstraintsConfig.COVER_LETTER_JD_RELEVANCE_THRESHOLD,
            "max_sim": SignalControlConfig.CL_MAX_JD_SIMILARITY
        }
        self._cache["VG_COVER_LETTER_RELEVANCE_RANGE"] = details # Cache for rule
        return similarity

    def _calculate_expected_signature(self):
        """Calculates the expected cover letter signature block."""
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        # Ensure COVER_LETTER_SIGNATURE_TEMPLATE exists before formatting
        if 'COVER_LETTER_SIGNATURE_TEMPLATE' not in globals():
             logging.error("COVER_LETTER_SIGNATURE_TEMPLATE not found!")
             return "[Signature Template Missing]" # Provide a fallback
        try:
            return COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except KeyError as e:
            logging.error(f"Error formatting signature template: Missing key {e}")
            return f"[Error: Missing signature key {e}]" # Provide error info

    def _calculate_cover_letter_structure_details(self):
        """Calculates details for COVER_LETTER_STRUCTURE rule (using K.11)."""
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '') # Use K.11 enum
        paras = [p.strip() for p in cl_text.split('\n\n') if p.strip()]
        p1_wc, p2_wc, p3_wc = 0, 0, 0
        error_msg = None
        # Basic paragraph extraction (adjust if format is more complex)
        try:
             salutation_idx = next(i for i, p in enumerate(paras) if p.startswith("Dear Hiring Manager,"))
             p1_idx = salutation_idx + 1
             p2_idx = p1_idx + 1
             p3_idx = p2_idx + 1
             closing_idx = next((i for i, p in enumerate(paras) if p == "Sincerely,"), len(paras))

             if p1_idx < closing_idx: p1_wc = count_words_ms_word_style(paras[p1_idx])
             if p2_idx < closing_idx: p2_wc = count_words_ms_word_style(paras[p2_idx])
             if p3_idx < closing_idx: p3_wc = count_words_ms_word_style(paras[p3_idx])
             if not (p1_idx < closing_idx and p2_idx < closing_idx and p3_idx < closing_idx):
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

    # --- START UPDATED METHODS for K.4/K.5/K.6 Narrative Checks ---
    def _calculate_k4_narrative_details(self):
        """Calculates details for K.4 TraderSense Narrative rules."""
        text = self.staging_buffer.get(ResumeSection.K4_TRADERSENSE_NARRATIVE.value, '') # Use K.4 enum
        word_count = count_words_ms_word_style(text)
        sentence_count = _count_sentences(text)
        # Use defaults if specific constraints missing
        min_wc = getattr(ContentConstraintsConfig, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN', 45)
        max_wc = getattr(ContentConstraintsConfig, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX', 65)
        details = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'min_wc': min_wc,
            'max_wc': max_wc,
            'target_sc': 3 # Target is 3 sentences
        }
        self._cache["VG_NARRATIVE_WORD_COUNT_K4"] = details # Use K4 rule ID
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K4"] = details # Use K4 rule ID
        return details

    def _calculate_k5_narrative_details(self):
        """Calculates details for K.5 EY Narrative rules."""
        text = self.staging_buffer.get(ResumeSection.K5_EY_NARRATIVE.value, '') # Use K.5 enum
        word_count = count_words_ms_word_style(text)
        sentence_count = _count_sentences(text)
        details = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'min_wc': ContentConstraintsConfig.EY_NARRATIVE_WORD_COUNT_MIN,
            'max_wc': ContentConstraintsConfig.EY_NARRATIVE_WORD_COUNT_MAX,
            'target_sc': 3 # Target is 3 sentences
        }
        self._cache["VG_NARRATIVE_WORD_COUNT_K5"] = details # Use K5 rule ID
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K5"] = details # Use K5 rule ID
        return details

    def _calculate_k6_narrative_details(self):
        """Calculates details for K.6 Early Career Narrative rules."""
        text = self.staging_buffer.get(ResumeSection.K6_EARLY_CAREER_NARRATIVE.value, '') # Use K.6 enum
        word_count = count_words_ms_word_style(text)
        sentence_count = _count_sentences(text)
        details = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'min_wc': ContentConstraintsConfig.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN,
            'max_wc': ContentConstraintsConfig.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX,
            'target_sc': 3 # Target is 3 sentences
        }
        self._cache["VG_NARRATIVE_WORD_COUNT_K6"] = details # Use K6 rule ID
        self._cache["VG_NARRATIVE_SENTENCE_COUNT_K6"] = details # Use K6 rule ID
        return details
    # --- END UPDATED METHODS ---

# ============================================================================
# HOP-5: VALIDATION GATES (STATEFUL RETRY VERSION)
# ============================================================================
from collections import defaultdict # Added for error message formatting
import copy # Added for deepcopy in prepare_validation_data
import logging # Ensure logging is imported
import re # Ensure re is imported for validation methods
from datetime import datetime # Ensure datetime is imported for validation methods
from typing import Dict, List, Optional, Any, Tuple, Set, Union # Ensure types are imported

class PreFlightValidator:

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.constraints = ContentConstraintsConfig() # Uses updated constraints
        self.signal_constraints = SignalControlConfig() # Signal control constraints

        # --- Rule to Section Mapping (Initialized via method, Updated for K0-K11) ---
        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()

        self._register_rules() # Register rules based on updated config

    # Class constant for signal targets configuration (UPDATED for K0-K11)
    SECTION_SIGNAL_TARGETS_CONFIG = {
        # Label: (Enum, Min_Target, Max_Target, Weight, ReasoningConfig)
        "Headline": (ResumeSection.K0_HEADLINE, 0.70, 0.90, 0.05, ReasoningConfig.K0_HEADLINE_CONFIG),
        "Executive Summary": (ResumeSection.K1_EXECUTIVE_SUMMARY, 0.80, 0.90, 0.25, ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG),
        # Renumbered Unify/IBM sections
        "Unify Overview": (ResumeSection.K2_UNIFY_OVERVIEW, 0.70, 0.90, 0.05, ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG),
        "Unify Bullets": (ResumeSection.K2_UNIFY_BULLETS, 0.70, 0.90, 0.20, ReasoningConfig.K2_UNIFY_BULLETS_CONFIG),
        "IBM Overview": (ResumeSection.K3_IBM_OVERVIEW, 0.60, 0.80, 0.05, ReasoningConfig.K3_IBM_OVERVIEW_CONFIG),
        "IBM Bullets": (ResumeSection.K3_IBM_BULLETS, 0.65, 0.85, 0.20, ReasoningConfig.K3_IBM_BULLETS_CONFIG),
        # Narratives - Use lower targets, map config correctly
        "TraderSense Narrative": (ResumeSection.K4_TRADERSENSE_NARRATIVE, 0.40, 0.60, 0.025, ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG),
        "EY Narrative": (ResumeSection.K5_EY_NARRATIVE, 0.50, 0.70, 0.025, ReasoningConfig.K5_EY_NARRATIVE_CONFIG),
        "Early Career Narrative": (ResumeSection.K6_EARLY_CAREER_NARRATIVE, 0.40, 0.60, 0.025, ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG),
        # Renumbered Competencies
        "Competencies": (ResumeSection.K9_COMPETENCIES, 0.85, 0.95, 0.10, ReasoningConfig.K9_COMPETENCIES_CONFIG),
        # Note: Skills (K10) often have lower signal targets or aren't checked here. Add if needed.
        # "Skills": (ResumeSection.K10_SKILLS, 0.50, 0.70, 0.05, ReasoningConfig.K10_SKILLS_CONFIG),
    }

    # Bullet word count sections to check (UPDATED for K0-K11 - only K2, K3, K9 apply)
    BULLET_WORD_COUNT_SECTIONS_TO_CHECK = [
        ResumeSection.K2_UNIFY_BULLETS,
        ResumeSection.K3_IBM_BULLETS,
        ResumeSection.K9_COMPETENCIES,
        # Narratives K4, K5, K6 are checked separately by sentence/word count rules
    ]

    # Provenance split targets configuration (UPDATED for K0-K11)
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K2_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K3_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K9_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
    }

    # Forbidden Verbs constant (Unchanged)
    FORBIDDEN_VERBS = [
        "pioneered", "spearheaded", "orchestrated", "architected",
        "revolutionized", "transformed"
    ]

    # Banned Intro Phrases Pattern (Unchanged)
    BANNED_INTRO_PHRASES_PATTERN = re.compile(
        r"^\s*(?:(?:As|In my role as|While at|During my time at|At)\s+(?:a|an|the|my)?\s*(?:[A-Z][\w\s]+?|\w+))\b[,:]?\s+",
        re.IGNORECASE
    )

    # --- Consolidated Rules Configuration (UPDATED for K0-K11) ---
    RULES_CONFIG = [
        # --- Word Count & Sentence Count Rules ---
        { # Total Word Count
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": lambda ctx: ctx.constraints.TOTAL_WORD_COUNT_MIN <= ctx.total_words <= ctx.constraints.TOTAL_WORD_COUNT_MAX, # Direct lambda
            "error_message": lambda ctx: f"Total resume: {ctx.total_words} words (target: {ctx.constraints.TOTAL_WORD_COUNT_MIN}-{ctx.constraints.TOTAL_WORD_COUNT_MAX})"
        },
        { # K.1 Sentences
            "rule_id": "VG_SENTENCE_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: ctx.k1_sentence_count_details['min'] <= ctx.k1_sentence_count_details['sentence_count'] <= ctx.k1_sentence_count_details['max'], # Direct lambda
            "error_message": lambda ctx: f"K.1 Exec Summary: {ctx._cache['VG_SENTENCE_COUNT_K1']['sentence_count']} sentences (target: {ctx._cache['VG_SENTENCE_COUNT_K1']['min']}-{ctx._cache['VG_SENTENCE_COUNT_K1']['max']})"
        },
        { # K.1 Words
            "rule_id": "VG_WORD_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": lambda ctx: ctx.k1_word_count_details['min'] <= ctx.k1_word_count_details['word_count'] <= ctx.k1_word_count_details['max'], # Direct lambda
            "error_message": lambda ctx: f"K.1 Exec Summary: {ctx._cache['VG_WORD_COUNT_K1']['word_count']} words (target: {ctx._cache['VG_WORD_COUNT_K1']['min']}-{ctx._cache['VG_WORD_COUNT_K1']['max']})"
        },
        { # K.0 Headline Words
            "rule_id": "VG_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.CRITICAL,"category": "structure",
            "validator": lambda ctx: ctx.constraints.HEADLINE_WORD_COUNT_MIN <= ctx.headline_details['word_count'] <= ctx.constraints.HEADLINE_WORD_COUNT_MAX, # Direct lambda
            "error_message": lambda ctx: f"K.0 Headline: {ctx.headline_details['word_count']} words (target: {ctx.headline_details['min']}-{ctx.headline_details['max']}). Headline: '{ctx.headline_details['headline']}'"
        },
        { # K.2 Unify Overview Words
            "rule_id": "VG_WORD_COUNT_K2_OVERVIEW", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": lambda ctx: ctx.k2_overview_details['min_wc'] <= ctx.k2_overview_details['word_count'] <= ctx.k2_overview_details['max_wc'], # Direct lambda
            "error_message": lambda ctx: f"K.2 Unify Overview: {ctx._cache['VG_WORD_COUNT_K2_OVERVIEW']['word_count']} words (target: {ctx._cache['VG_WORD_COUNT_K2_OVERVIEW']['min_wc']}-{ctx._cache['VG_WORD_COUNT_K2_OVERVIEW']['max_wc']})"
        },
        { # K.2 Unify Overview Sentences
            "rule_id": "VG_SENTENCE_COUNT_K2_OVERVIEW", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k2_overview_details['min_sc'] <= ctx.k2_overview_details['sentence_count'] <= ctx.k2_overview_details['max_sc'], # Direct lambda
            "error_message": lambda ctx: f"K.2 Unify Overview: {ctx._cache['VG_SENTENCE_COUNT_K2_OVERVIEW']['sentence_count']} sentences (target: {ctx._cache['VG_SENTENCE_COUNT_K2_OVERVIEW']['min_sc']}-{ctx._cache['VG_SENTENCE_COUNT_K2_OVERVIEW']['max_sc']})"
        },
        { # K.3 IBM Overview Words
            "rule_id": "VG_WORD_COUNT_K3_OVERVIEW", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": lambda ctx: ctx.k3_overview_details['min_wc'] <= ctx.k3_overview_details['word_count'] <= ctx.k3_overview_details['max_wc'], # Direct lambda
            "error_message": lambda ctx: f"K.3 IBM Overview: {ctx._cache['VG_WORD_COUNT_K3_OVERVIEW']['word_count']} words (target: {ctx._cache['VG_WORD_COUNT_K3_OVERVIEW']['min_wc']}-{ctx._cache['VG_WORD_COUNT_K3_OVERVIEW']['max_wc']})"
        },
        { # K.3 IBM Overview Sentences
            "rule_id": "VG_SENTENCE_COUNT_K3_OVERVIEW", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k3_overview_details['min_sc'] <= ctx.k3_overview_details['sentence_count'] <= ctx.k3_overview_details['max_sc'], # Direct lambda
            "error_message": lambda ctx: f"K.3 IBM Overview: {ctx._cache['VG_SENTENCE_COUNT_K3_OVERVIEW']['sentence_count']} sentences (target: {ctx._cache['VG_SENTENCE_COUNT_K3_OVERVIEW']['min_sc']}-{ctx._cache['VG_SENTENCE_COUNT_K3_OVERVIEW']['max_sc']})"
        },
        # --- Narrative Block Rules ---
        { # K.4 Narrative Words
            "rule_id": "VG_NARRATIVE_WORD_COUNT_K4", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": lambda ctx: ctx.k4_narrative_details['min_wc'] <= ctx.k4_narrative_details['word_count'] <= ctx.k4_narrative_details['max_wc'], # Direct lambda
            "error_message": lambda ctx: f"K.4 TraderSense Narrative: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K4']['word_count']} words (target: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K4']['min_wc']}-{ctx._cache['VG_NARRATIVE_WORD_COUNT_K4']['max_wc']})"
        },
        { # K.4 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K4", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k4_narrative_details['sentence_count'] == ctx.k4_narrative_details['target_sc'], # Direct lambda
            "error_message": lambda ctx: f"K.4 TraderSense Narrative: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K4']['sentence_count']} sentences (target: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K4']['target_sc']})"
        },
        { # K.5 Narrative Words
            "rule_id": "VG_NARRATIVE_WORD_COUNT_K5", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": lambda ctx: ctx.k5_narrative_details['min_wc'] <= ctx.k5_narrative_details['word_count'] <= ctx.k5_narrative_details['max_wc'], # Direct lambda
            "error_message": lambda ctx: f"K.5 EY Narrative: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K5']['word_count']} words (target: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K5']['min_wc']}-{ctx._cache['VG_NARRATIVE_WORD_COUNT_K5']['max_wc']})"
        },
        { # K.5 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K5", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k5_narrative_details['sentence_count'] == ctx.k5_narrative_details['target_sc'], # Direct lambda
            "error_message": lambda ctx: f"K.5 EY Narrative: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K5']['sentence_count']} sentences (target: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K5']['target_sc']})"
        },
        { # K.6 Narrative Words
            "rule_id": "VG_NARRATIVE_WORD_COUNT_K6", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": lambda ctx: ctx.k6_narrative_details['min_wc'] <= ctx.k6_narrative_details['word_count'] <= ctx.k6_narrative_details['max_wc'], # Direct lambda
            "error_message": lambda ctx: f"K.6 Early Career Narrative: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K6']['word_count']} words (target: {ctx._cache['VG_NARRATIVE_WORD_COUNT_K6']['min_wc']}-{ctx._cache['VG_NARRATIVE_WORD_COUNT_K6']['max_wc']})"
        },
        { # K.6 Narrative Sentences
            "rule_id": "VG_NARRATIVE_SENTENCE_COUNT_K6", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": lambda ctx: ctx.k6_narrative_details['sentence_count'] == ctx.k6_narrative_details['target_sc'], # Direct lambda
            "error_message": lambda ctx: f"K.6 Early Career Narrative: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K6']['sentence_count']} sentences (target: {ctx._cache['VG_NARRATIVE_SENTENCE_COUNT_K6']['target_sc']})"
        },
        { # Bullet WC Range (Applies to K.2, K.3, K.9)
            "rule_id": "VG_BULLET_WORD_COUNT_RANGE", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": "_validate_bullet_word_count_range", # Keep complex validator method
            "error_message": lambda ctx: f"Bullet word counts outside hardcoded ranges: {ctx._cache['VG_BULLET_WORD_COUNT_RANGE'].get('violations', 'N/A')}"
        },
        # --- Distribution Rules (K.2/K.3) ---
        {
            "rule_id": "WORD_DISTRIBUTION_UNIFY_IBM", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ctx.constraints.UNIFY_IBM_COMBINED_PERCENT_MIN <= ctx.unify_ibm_percent <= ctx.constraints.UNIFY_IBM_COMBINED_PERCENT_MAX, # Direct lambda
            "error_message": lambda ctx: f"K.2(Unify)+K.3(IBM): {ctx.unify_ibm_percent:.1f}% of total (target: {ctx._cache['WORD_DISTRIBUTION_UNIFY_IBM']['min']}-{ctx._cache['WORD_DISTRIBUTION_UNIFY_IBM']['max']}%)"
        },
        {
            "rule_id": "UNIFY_IBM_RATIO", "severity": ValidationSeverity.HIGH, "category": "distribution",
            "validator": lambda ctx: ctx.ibm_words > 0 and ctx.constraints.UNIFY_IBM_RATIO_MIN <= ctx.unify_ibm_ratio <= ctx.constraints.UNIFY_IBM_RATIO_MAX, # Direct lambda
            "error_message": lambda ctx: f"K.2(Unify)/K.3(IBM) ratio: {ctx.unify_ibm_ratio:.2f} (target: {ctx._cache['UNIFY_IBM_RATIO']['min']}-{ctx._cache['UNIFY_IBM_RATIO']['max']})"
        },
        # --- Structure & Formatting Rules ---
        { # Buffer Lock
            "rule_id": "BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: ctx.staging_buffer.is_locked(), # Direct lambda
            "error_message": "Staging buffer must be locked before validation"
        },
        { # K.11 Cover Letter Signature
            "rule_id": "VG_COVER_LETTER_SIGNATURE_VALID", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: bool(ctx.expected_signature and '\n' in ctx.expected_signature and ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').rstrip().endswith(ctx.expected_signature)), # Direct lambda
            "error_message": "K.11 Cover letter signature is missing, malformed, or not multi-line."
        },
        { # K.11 Cover Letter Structure
            "rule_id": "VG_COVER_LETTER_FULL_STRUCTURE", "severity": ValidationSeverity.HIGH, "category": "structure",
            "validator": "_validate_cover_letter_full_structure", # Keep complex validator method
            "error_message": "K.11 Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."
        },
        { # K.0 Headline Titles
            "rule_id": "VG_HEADLINE_NO_TITLES", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_headline_format_no_titles", # Keep complex validator method
            "error_message": lambda ctx: f"K.0 Headline contains forbidden titles: {ctx._cache['VG_HEADLINE_NO_TITLES'].get('forbidden', 'N/A')}. Headline: '{ctx.headline_details['headline']}'"
        },
        { # K.0 Headline Commas
            "rule_id": "VG_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": lambda ctx: ',' not in ctx.headline_details['headline'], # Direct lambda
            "error_message": lambda ctx: f"K.0 Headline contains commas. Headline: '{ctx.headline_details['headline']}'"
        },
        # --- Placeholder Visual Rules --- (Keep as is, validation happens elsewhere)
        {"rule_id": "VG_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Resume headers not consistently H2"},
        {"rule_id": "VG_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Education/Certification format incorrect"},
        {"rule_id": "VG_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience bullets incorrect style"},
        {"rule_id": "VG_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Competencies list formatting incorrect"},
        {"rule_id": "VG_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience section formatting incorrect"},
        # --- Content & Signal Rules ---
        { # No Placeholders
            "rule_id": "CONTENT_NO_PLACEHOLDERS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_no_placeholders", # Keep complex validator method
            "error_message": lambda ctx: f"Found placeholder text in content: {ctx._cache['CONTENT_NO_PLACEHOLDERS'].get('placeholders', 'N/A')}"
        },
        { # Forbidden Verbs
            "rule_id": "VG_FORBIDDEN_VERBS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_forbidden_verbs", # Keep complex validator method
            "error_message": lambda ctx: f"Forbidden verbs found in generated content: {ctx._cache['VG_FORBIDDEN_VERBS'].get('violations', 'N/A')}"
        },
        { # Banned Intro Phrases
            "rule_id": "VG_NO_INTRO_PHRASES", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_no_intro_phrases", # Keep complex validator method
            "error_message": lambda ctx: f"Banned introductory phrases found: {ctx._cache['VG_NO_INTRO_PHRASES'].get('violations', 'N/A')}"
        },
        { # Per-Section Signal Score
            "rule_id": "VG_PER_SECTION_SIGNAL_SCORE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_per_section_signal", # Keep complex validator method
            "error_message": lambda ctx: f"One or more sections are below minimum signal score: {ctx._cache['VG_PER_SECTION_SIGNAL_SCORE'].get('failures', 'N/A')}"
        },
        { # K.1 Differentiators
            "rule_id": "VG_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": lambda ctx: ctx.constraints.K1_MIN_DIFFERENTIATORS <= ctx._calculate_k1_differentiator_range()['found'] <= ctx.signal_constraints.K1_MAX_DIFFERENTIATORS, # Direct lambda, triggers calculation
            "error_message": lambda ctx: f"K.1 Summary contains {ctx._cache['VG_K1_DIFFERENTIATOR_RANGE']['found']} differentiators (target: {ctx._cache['VG_K1_DIFFERENTIATOR_RANGE']['min']}-{ctx._cache['VG_K1_DIFFERENTIATOR_RANGE']['max']})."
        },
        { # JD Keyword Range (Global)
            "rule_id": "VG_JD_KEYWORD_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_jd_keyword_range", # Keep complex validator method
            "error_message": lambda ctx: f"Resume contains {ctx._cache['VG_JD_KEYWORD_RANGE']['found']} unique JD keywords (target: {ctx._cache['VG_JD_KEYWORD_RANGE']['min']}-{ctx._cache['VG_JD_KEYWORD_RANGE']['max']})."
        },
        { # Narrative Mining Presence
            "rule_id": "NARRATIVE_MINING_PRESENCE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_narrative_mining_presence",
            "error_message": "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."
        },
        { # K.11 Cover Letter Relevance
            "rule_id": "VG_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: ctx.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD <= ctx.cover_letter_jd_similarity <= ctx.signal_constraints.CL_MAX_JD_SIMILARITY,
            "error_message": lambda ctx: f"K.11 Cover letter relevance to JD is {ctx.cover_letter_jd_similarity:.2f} (target: {ctx._cache['VG_COVER_LETTER_RELEVANCE_RANGE']['min_sim']:.2f}-{ctx._cache['VG_COVER_LETTER_RELEVANCE_RANGE']['max_sim']:.2f})."
        },
        { # K.11 Cover Letter Narrative
            "rule_id": "COVER_LETTER_NARRATIVE_INTEGRITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: ctx._calculate_cover_letter_narrative()['valid'], # Direct lambda, triggers calculation
            "error_message": lambda ctx: f"K.11 Cover letter may be missing narrative integrity. Hook: {ctx._cache['COVER_LETTER_NARRATIVE_INTEGRITY']['hook']}, Proof: {ctx._cache['COVER_LETTER_NARRATIVE_INTEGRITY']['proof']}, Vision: {ctx._cache['COVER_LETTER_NARRATIVE_INTEGRITY']['vision']}"
        },
        { # K.11 Cover Letter Fallback Check (Simple string check)
            "rule_id": "COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": lambda ctx: "track record of measurable AI transformation" not in ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, ''), # Check K.11, Direct lambda
            "error_message": "Creative cover letter generation failed; fallback likely used."
        },
        { # K.11 Cover Letter Paragraph WC
            "rule_id": "COVER_LETTER_STRUCTURE", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_cover_letter_structure",
            "error_message": lambda ctx: f"K.11 Cover letter paragraph word counts out of spec. P1: {ctx._cache['COVER_LETTER_STRUCTURE']['p1_wc']} ({ctx._cache['COVER_LETTER_STRUCTURE']['p1_min']}-{ctx._cache['COVER_LETTER_STRUCTURE']['p1_max']}), P2: {ctx._cache['COVER_LETTER_STRUCTURE']['p2_wc']} ({ctx._cache['COVER_LETTER_STRUCTURE']['p2_min']}-{ctx._cache['COVER_LETTER_STRUCTURE']['p2_max']}), P3: {ctx._cache['COVER_LETTER_STRUCTURE']['p3_wc']} ({ctx._cache['COVER_LETTER_STRUCTURE']['p3_min']}-{ctx._cache['COVER_LETTER_STRUCTURE']['p3_max']})"
        },
        { # Provenance Split Check (Applies to K.2, K.3, K.9)
            "rule_id": "VG_PROVENANCE_SPLIT_CHECK", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_provenance_split", # Keep complex validator method
            "error_message": lambda ctx: f"Provenance split mismatch: {ctx._cache['VG_PROVENANCE_SPLIT_CHECK'].get('violations', 'N/A')}"
        },
        { # Authenticity Signal Check
            "rule_id": "VG_AUTHENTICITY_SIGNAL_CHECK", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_authenticity_signal", # Keep complex validator method
            "error_message": lambda ctx: f"Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {ctx._cache['VG_AUTHENTICITY_SIGNAL_CHECK'].get('details', 'N/A')}"
        },
        { # Exec Summary vs Section Similarity
            "rule_id": "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_exec_summary_vs_sections", # Keep complex validator method
            "error_message": lambda ctx: f"Executive Summary similarity to sections exceeds threshold: {ctx._cache['VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY'].get('failures', 'N/A')}"
        },
    ]

    def _initialize_rule_map(self) -> Dict[str, Union[ResumeSection, str]]:
        """
        Creates the mapping of Rule IDs to the ResumeSection they govern (UPDATED for K0-K11).
        """
        logger = logging.getLogger(__name__) # Use logger for warnings
        rule_map = {
            # Global Rules
            "VG_TOTAL_WORD_COUNT": "GLOBAL",
            "WORD_DISTRIBUTION_UNIFY_IBM": "GLOBAL",
            "UNIFY_IBM_RATIO": "GLOBAL",
            "VG_JD_KEYWORD_RANGE": "GLOBAL",
            "VG_AUTHENTICITY_SIGNAL_CHECK": "GLOBAL",
            "NARRATIVE_MINING_PRESENCE": "GLOBAL",
            "CONTENT_NO_PLACEHOLDERS": "GLOBAL",
            "BUFFER_LOCK_STATUS": "GLOBAL",
            # Visual Rules
            "VG_RESUME_HEADER_H2": "VISUAL", "VG_EDU_CERTS_FORMAT": "VISUAL",
            "VG_EXPERIENCE_BULLET_STYLE": "VISUAL", "VG_COMPETENCIES_FORMATTING": "VISUAL",
            "VG_EXPERIENCE_RENDER_FORMAT": "VISUAL",
            # K.0 Headline
            "VG_HEADLINE_WORD_COUNT": ResumeSection.K0_HEADLINE,
            "VG_HEADLINE_NO_TITLES": ResumeSection.K0_HEADLINE,
            "VG_HEADLINE_NO_COMMAS": ResumeSection.K0_HEADLINE,
            "STRUCTURE_K0_HEADLINE_PRESENT": ResumeSection.K0_HEADLINE,
            # K.1 Executive Summary
            "VG_SENTENCE_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_WORD_COUNT_K1": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY": ResumeSection.K1_EXECUTIVE_SUMMARY,
            # K.2 Unify (Was K.5)
            "STRUCTURE_K2_UNIFY_BULLETS_PRESENT": ResumeSection.K2_UNIFY_BULLETS,
            "STRUCTURE_K2_UNIFY_OVERVIEW_PRESENT": ResumeSection.K2_UNIFY_OVERVIEW,
            "VG_WORD_COUNT_K2_OVERVIEW": ResumeSection.K2_UNIFY_OVERVIEW,
            "VG_SENTENCE_COUNT_K2_OVERVIEW": ResumeSection.K2_UNIFY_OVERVIEW,
            # K.3 IBM (Was K.6)
            "STRUCTURE_K3_IBM_BULLETS_PRESENT": ResumeSection.K3_IBM_BULLETS,
            "STRUCTURE_K3_IBM_OVERVIEW_PRESENT": ResumeSection.K3_IBM_OVERVIEW,
            "VG_WORD_COUNT_K3_OVERVIEW": ResumeSection.K3_IBM_OVERVIEW,
            "VG_SENTENCE_COUNT_K3_OVERVIEW": ResumeSection.K3_IBM_OVERVIEW,
            # K.4 Narrative (TraderSense)
            "STRUCTURE_K4_TRADERSENSE_NARRATIVE_PRESENT": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "VG_NARRATIVE_WORD_COUNT_K4": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K4": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            # K.5 Narrative (EY)
            "STRUCTURE_K5_EY_NARRATIVE_PRESENT": ResumeSection.K5_EY_NARRATIVE,
            "VG_NARRATIVE_WORD_COUNT_K5": ResumeSection.K5_EY_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K5": ResumeSection.K5_EY_NARRATIVE,
            # K.6 Narrative (Early Career)
            "STRUCTURE_K6_EARLY_CAREER_NARRATIVE_PRESENT": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "VG_NARRATIVE_WORD_COUNT_K6": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "VG_NARRATIVE_SENTENCE_COUNT_K6": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            # K.9 Competencies (Was K.10)
            "STRUCTURE_K9_COMPETENCIES_PRESENT": ResumeSection.K9_COMPETENCIES,
            # K.10 Skills (Was K.2)
            "STRUCTURE_K10_SKILLS_PRESENT": ResumeSection.K10_SKILLS,
            # K.11 Cover Letter (Was K.13)
            "VG_COVER_LETTER_SIGNATURE_VALID": ResumeSection.K11_COVER_LETTER,
            "VG_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "VG_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K11_COVER_LETTER,
            "COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K11_COVER_LETTER,
            "COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K11_COVER_LETTER,
            "COVER_LETTER_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "STRUCTURE_K11_COVER_LETTER_PRESENT": ResumeSection.K11_COVER_LETTER,
            # Complex Rules (Mapping failure sections dynamically)
            "VG_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION",
            "VG_BULLET_WORD_COUNT_RANGE": "COMPLEX_PER_SECTION",
            "VG_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION",
            "VG_FORBIDDEN_VERBS": "COMPLEX_PER_SECTION",
            "VG_NO_INTRO_PHRASES": "COMPLEX_PER_SECTION"
        }

        # Add structure rules dynamically for sections defined in the K0-K11 Enum
        # This ensures all defined sections have a presence check rule generated.
        config_rule_ids = {cfg["rule_id"] for cfg in self.RULES_CONFIG}
        for section in ResumeSection:
             # Skip headers that might share base names (e.g., K0_EXECUTIVE_SUMMARY_HEADER vs K1_EXECUTIVE_SUMMARY)
             # if section.name.endswith("_HEADER"): continue # Keep header checks
             rule_id = f"STRUCTURE_{section.name}_PRESENT"

             # Only add dynamically if NOT already defined in RULES_CONFIG or the static part of rule_map
             if rule_id not in config_rule_ids and rule_id not in rule_map:
                 # Check if the base name rule exists (e.g., STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT)
                 base_rule_exists = any(r_id == rule_id for r_id in rule_map.keys())
                 if not base_rule_exists:
                     rule_map[rule_id] = section # Assign the section enum
                     logger.debug(f"Dynamically mapped structure rule: {rule_id} -> {section.name}")
        return rule_map

    def _register_rules(self):
        """Creates and registers all pre-flight validation rules based on RULES_CONFIG."""
        registered_rule_ids = set() # Track registered IDs

        for config in self.RULES_CONFIG:
            rule_id = config["rule_id"]
            if rule_id in registered_rule_ids:
                 logging.warning(f"Duplicate rule ID found in RULES_CONFIG: {rule_id}. Skipping re-registration.")
                 continue

            validator_ref = config["validator"]
            validator_func = None # Initialize
            if isinstance(validator_ref, str):
                # Check if it's a method name that *should* exist (complex validators)
                validator_func = getattr(self, validator_ref, None)
                if validator_func is None:
                    msg = f"Validator method '{validator_ref}' not found for rule {rule_id}"
                    logging.error(msg)
                    # Register a dummy validator that always fails to prevent runtime errors later
                    validator_func = lambda ctx: False # Always fail
                    raise AttributeError(msg)
            elif callable(validator_ref):
                 validator_func = validator_ref # Use the lambda directly
            else:
                 raise TypeError(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}")

            # Create error message lambda with safe formatting
            def create_error_message_lambda(template, rule_id_for_cache):
                # Ensure template is a string
                str_template = str(template)
                # Use a closure to capture template and rule_id
                def error_lambda(ctx: ValidationContext):
                    try:
                        # Fetch cached details for this rule, default to empty dict
                        details = ctx._cache.get(rule_id_for_cache, {})
                        # Use defaultdict to prevent KeyError on missing format keys
                        return str_template.format_map(defaultdict(lambda: '[N/A]', **details))
                    except Exception as e:
                        logging.error(f"Error formatting error message for rule {rule_id_for_cache}: {e}. Template: '{str_template}' Details: {details}")
                        return f"[Error formatting msg for {rule_id_for_cache}]" # Fallback message
                return error_lambda

            error_msg_lambda = create_error_message_lambda(config["error_message"], rule_id)

            rule = ValidationRule(
                rule_id=rule_id,
                severity=config["severity"],
                category=config.get("category", "general"), # Use .get for safety
                validator=validator_func,
                error_message=error_msg_lambda # Pass the created lambda
            )
            self.engine.register_rule(rule)
            registered_rule_ids.add(rule_id)


        # Dynamically register rules for required sections presence check (Using K0-K11 Enum)
        # Define which sections are absolutely required in the final output
        required_enums = [
            ResumeSection.K0_NAME, ResumeSection.K0_HEADLINE, ResumeSection.K0_CONTACT,
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_BULLETS, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K7_EDUCATION, ResumeSection.K8_CERTIFICATIONS,
            ResumeSection.K9_COMPETENCIES, ResumeSection.K10_SKILLS,
            ResumeSection.K11_COVER_LETTER,
            # Add header sections if needed
            ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, ResumeSection.K0_EXPERIENCE_HEADER,
            ResumeSection.K0_EDUCATION_HEADER, ResumeSection.K0_CERTIFICATIONS_HEADER,
            ResumeSection.K0_COMPETENCIES_HEADER
        ]

        for section in required_enums:
            rule_id = f"STRUCTURE_{section.name}_PRESENT"
            if rule_id not in registered_rule_ids: # Avoid duplicates
                # Define the validator lambda using the captured section enum
                def create_validator_lambda(section_enum: ResumeSection):
                    return lambda ctx: (
                        ctx.staging_buffer.get(section_enum.value) is not None and
                        # Check content isn't empty string, empty list, empty dict, or placeholder header
                        ( (isinstance(ctx.staging_buffer.get(section_enum.value), str) and ctx.staging_buffer.get(section_enum.value).strip() not in ["", "HEADER_PLACEHOLDER"]) or
                          (isinstance(ctx.staging_buffer.get(section_enum.value), list) and ctx.staging_buffer.get(section_enum.value)) or
                          (isinstance(ctx.staging_buffer.get(section_enum.value), dict) and ctx.staging_buffer.get(section_enum.value))
                        )
                    )

                rule = ValidationRule(
                    rule_id=rule_id,
                    severity=ValidationSeverity.CRITICAL,
                    validator=create_validator_lambda(section), # Pass section to lambda factory
                    error_message=f"{section.value} is missing, empty, or placeholder.",
                    category="structure"
                )
                self.engine.register_rule(rule)
                registered_rule_ids.add(rule_id)

    # --- Validation Helper Methods (Updated for K0-K11) ---

    # K.1 Methods (Rule IDs assumed unchanged)
    def _validate_cover_letter_full_structure(self, context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '') # Use K.11
        expected_sig = context.expected_signature
        has_date = bool(re.search(r"^\w+ \d{1,2}, \d{4}", text.strip()))
        has_recipient = bool(re.search(r"Hiring Manager\n\[Company Name\]", text))
        has_salutation = bool(re.search(r"Dear Hiring Manager,", text))
        has_closing = bool(re.search(r"\n\nSincerely,\n\n", text))
        has_signature = expected_sig in text and text.strip().endswith(expected_sig)
        body_match = re.search(r"Dear Hiring Manager,\s*(.*?)\s*Sincerely,", text, re.DOTALL)
        paras_found = len([p for p in body_match.group(1).strip().split('\n\n') if p.strip()]) if body_match else 0
        has_3_paras = paras_found >= 3
        valid = has_date and has_recipient and has_salutation and has_closing and has_signature and has_3_paras
        if not valid:
             context._cache["VG_COVER_LETTER_FULL_STRUCTURE"] = {
                 "has_date": has_date, "has_recipient": has_recipient, "has_salutation": has_salutation,
                 "has_closing": has_closing, "has_signature": has_signature, "paras_found": paras_found
             }
        return valid

    def _validate_cover_letter_structure(self, context: ValidationContext) -> bool:
        details = context.cover_letter_structure_details # Uses K.11 internally now
        if details.get("error"): return False
        p1_valid = details['p1_min'] <= details['p1_wc'] <= details['p1_max']
        p2_valid = details['p2_min'] <= details['p2_wc'] <= details['p2_max']
        p3_valid = details['p3_min'] <= details['p3_wc'] <= details['p3_max']
        return p1_valid and p2_valid and p3_valid

    # --- Other Helper Methods (Updated Enum Refs, Complex Logic) ---

    def _validate_bullet_word_count_range(self, context: ValidationContext) -> bool:
        """Checks bullet word counts (K.2, K.3, K.9) against ArtistGenerator ranges."""
        all_bullets_valid = True; violations = []; failed_sections = set()
        # Use updated BULLET_WORD_COUNT_SECTIONS_TO_CHECK for K0-K11
        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            # Get ranges directly from ArtistGenerator class for consistency
            target_range = ArtistGenerator.BULLET_WORD_COUNT_RANGES.get(section_enum)
            if target_range is None: continue # Skip if no range defined for this section
            min_wc, max_wc = target_range
            bullets = context.staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): continue

            for i, bullet in enumerate(bullets):
                actual_wc = 0; bullet_text = ""
                if isinstance(bullet, dict):
                    bullet_text = bullet.get('text', '')
                    actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str): # Should not happen for K2, K3, K9 but handle defensively
                    bullet_text = bullet; actual_wc = count_words_ms_word_style(bullet_text)
                else: continue

                if not (min_wc <= actual_wc <= max_wc):
                    all_bullets_valid = False
                    violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc})")
                    failed_sections.add(section_enum)

        if not all_bullets_valid:
            context._cache["VG_BULLET_WORD_COUNT_RANGE"] = {
                "violations": ", ".join(violations[:3]) + ('...' if len(violations)>3 else ''),
                "failed_sections": failed_sections
            }
        return all_bullets_valid

    def _validate_headline_format_no_titles(self, context: ValidationContext) -> bool:
        details = context.headline_details
        headline = details['headline']
        if not headline or '|' not in headline: return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: return False

        forbidden_titles = ['director', 'vp', 'manager', 'lead', 'head', 'chief', 'principal', 'senior', 'executive']
        forbidden_found = []
        component_wc_valid = True
        min_comp_wc = details['comp_min']; max_comp_wc = details['comp_max']

        for comp in components:
            word_count = count_words_ms_word_style(comp)
            if not (min_comp_wc <= word_count <= max_comp_wc): component_wc_valid = False
            for title in forbidden_titles:
                 if re.search(r'\b' + re.escape(title) + r'\b', comp.lower()): forbidden_found.append(title)

        if forbidden_found:
             context._cache["VG_HEADLINE_NO_TITLES"] = {"forbidden": list(set(forbidden_found)), "headline": headline}
             return False
        if not component_wc_valid:
             context._cache["VG_HEADLINE_COMPONENT_WC"] = {"headline": headline, "min": min_comp_wc, "max": max_comp_wc}
             return False # Also fail if component word count wrong
        return True

    def _validate_no_placeholders(self, context: ValidationContext) -> bool:
        """Checks recursively for '[Placeholder' strings in buffer data."""
        buffer_data = context.staging_buffer.data
        found = []
        failed = set()

        def check(item, key_enum=None):
            """Recursive helper function."""
            if isinstance(item, str) and "[Placeholder" in item:
                # Create a snippet around the placeholder for context
                parts = item.split("[Placeholder", 1)
                snippet_before = parts[0][-30:] # Last 30 chars before
                snippet_after = parts[1][:30]   # First 30 chars after
                snippet = f"...{snippet_before}[Placeholder{snippet_after}..."
                found.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                if key_enum:
                    failed.add(key_enum)
            elif isinstance(item, dict):
                for k, v in item.items():
                    enum_for_value = key_enum # Default to parent's enum
                    try:
                        # Attempt to map the dict key back to a ResumeSection enum
                        enum_for_value = ResumeSection(k)
                    except ValueError:
                        pass # If key doesn't match an enum value, keep parent's enum context
                    check(v, enum_for_value) # Recurse into value
            elif isinstance(item, list):
                for elem in item:
                    check(elem, key_enum) # Recurse into list element

        # Start the recursive check from the top-level buffer data
        check(buffer_data)

        # If any placeholders were found...
        if found:
            # Cache the findings for reporting/retry logic
            context._cache["CONTENT_NO_PLACEHOLDERS"] = {
                "placeholders": ", ".join(found[:3]), # Store first few found snippets
                "failed_sections": failed # Store enums of sections containing placeholders
            }
            return False # Validation fails

        # No placeholders found
        return True


    def _validate_forbidden_verbs(self, context: ValidationContext) -> bool:
        valid = True; violations = []; failed = set()
        # Check bullets (K2, K3, K9), narratives (K4, K5, K6), overviews (K2, K3), and K1
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts = []
            if isinstance(content, str): texts.append((content, -1))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text: texts.append((text, i))

            for text, idx in texts:
                found = [v for v in self.FORBIDDEN_VERBS if re.search(r'\b' + re.escape(v) + r'\b', text.lower())]
                if found:
                    valid = False; loc = f"{section_enum.value}" + (f"[{idx}]" if idx != -1 else "")
                    violations.append(f"{loc}: '{', '.join(found)}'"); failed.add(section_enum)
        if not valid: context._cache["VG_FORBIDDEN_VERBS"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_no_intro_phrases(self, context: ValidationContext) -> bool:
        valid = True; violations = []; failed = set()
        # Check bullets, narratives, overviews, K1, and K11 body
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts_info = [] # List of (text, index/label string)
            is_cl = (section_enum == ResumeSection.K11_COVER_LETTER)

            if isinstance(content, str):
                if is_cl:
                    body_match = re.search(r"Dear Hiring Manager,\s*(.*?)\s*Sincerely,", content, re.DOTALL)
                    if body_match:
                        for i, para in enumerate(body_match.group(1).strip().split('\n\n')):
                            if para.strip(): texts_info.append((para.strip(), f"Para {i+1}"))
                else: texts_info.append((content.strip(), None))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text: texts_info.append((text.strip(), i))

            for text, idx_label in texts_info:
                 match = self.BANNED_INTRO_PHRASES_PATTERN.match(text)
                 if match:
                     valid = False; loc = f"{section_enum.value}"
                     if isinstance(idx_label, int): loc += f"[{idx_label}]"
                     elif isinstance(idx_label, str): loc += f" ({idx_label})"
                     violations.append(f"{loc}: Starts with '{match.group(0).strip()}'"); failed.add(section_enum)
        if not valid: context._cache["VG_NO_INTRO_PHRASES"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_per_section_signal(self, context: ValidationContext) -> bool:
        """Validates signal score using updated SECTION_SIGNAL_TARGETS_CONFIG."""
        valid = True; failures = []; failed = set()
        # Use updated config mapping K0-K11 enums
        for label, (section_enum, target_min, target_max, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = context.staging_buffer.get(section_enum.value)
            if content:
                score = calculate_signal_score(content, context.thematic_analysis)
                # Check against strict target range
                if not (target_min <= score <= target_max):
                    valid = False
                    failures.append(f"{label}({section_enum.name}): {score:.1%} (Target: {target_min:.0%}-{target_max:.0%})")
                    failed.add(section_enum)
            # Missing content is handled by STRUCTURE rules

        if not valid: context._cache["VG_PER_SECTION_SIGNAL_SCORE"] = {"failures": ", ".join(failures[:3]), "failed_sections": failed}
        return valid

    def _calculate_k1_differentiator_range(self, context: ValidationContext) -> Dict:
        k1_text = context.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        differentiators = []; comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: differentiators = getattr(comp_intel, 'differentiator_keywords', [])
        found = sum(1 for kw in differentiators if kw and kw.lower() in k1_text)
        min_target = context.constraints.K1_MIN_DIFFERENTIATORS; max_target = context.signal_constraints.K1_MAX_DIFFERENTIATORS
        valid = min_target <= found <= max_target
        context._cache["VG_K1_DIFFERENTIATOR_RANGE"] = {"found": found, "min": min_target, "max": max_target}
        # Return the details dict for direct use in lambda
        return context._cache["VG_K1_DIFFERENTIATOR_RANGE"]

    def _validate_jd_keyword_range(self, context: ValidationContext) -> bool:
        full_text = ""; buffer_data = context.staging_buffer.data
        # Aggregate text, excluding headers/contact
        for key_enum in ResumeSection:
             if key_enum not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT] and not key_enum.name.endswith("_HEADER"):
                 value = buffer_data.get(key_enum.value); # ... (aggregate text logic remains same) ...
                 if isinstance(value, str): full_text += value + " "
                 elif isinstance(value, list): full_text += " ".join(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value) + " "

        differentiators = set(); comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel: differentiators = set(kw for kw in getattr(comp_intel, 'differentiator_keywords', []) if kw)
        primary_words = set(kw for kw in context.thematic_analysis.primary_theme.get('keywords', []) if kw)
        all_jd_keywords = differentiators.union(primary_words)
        found = {kw for kw in all_jd_keywords if kw.lower() in full_text.lower()}
        min_target = context.constraints.MIN_JD_KEYWORDS; max_target = context.signal_constraints.RESUME_MAX_JD_KEYWORDS
        valid = min_target <= len(found) <= max_target
        context._cache["VG_JD_KEYWORD_RANGE"] = {"found": len(found), "min": min_target, "max": max_target, "jd_keywords_found": list(found)}
        return valid

    def _validate_narrative_mining_presence(self, context: ValidationContext) -> bool:
        narratives = getattr(context.thematic_analysis, 'problem_solution_narratives', None)
        return isinstance(narratives, dict) and narratives.get('common_problems') and narratives.get('solution_patterns')

    def _calculate_cover_letter_narrative(self, context: ValidationContext) -> Dict:
        """Helper to calculate narrative details for lambda validation."""
        cl_text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').lower() # Use K.11
        hook = any(kw in cl_text for kw in ["enthusiastic", "excited", "apply for", "interest in"])
        proof = any(kw in cl_text for kw in ["demonstrated", "achieved", "delivered", "resulted in", "experience"])
        vision = any(kw in cl_text for kw in ["contribute", "goals", "opportunity", "eager to discuss"])
        details = {"hook": hook, "proof": proof, "vision": vision, "valid": hook and proof and vision}
        context._cache["COVER_LETTER_NARRATIVE_INTEGRITY"] = details
        return details

    def _validate_provenance_split(self, context: ValidationContext) -> bool:
        """Validates bullet provenance (K.2, K.3, K.9) against updated targets."""
        valid = True; violations = []; failed = set()
        # Use updated PROVENANCE_SPLIT_TARGETS for K0-K11
        for section_enum, targets in self.PROVENANCE_SPLIT_TARGETS.items():
            bullets = context.staging_buffer.get(section_enum.value, [])
            if not isinstance(bullets, list): continue
            counts = defaultdict(int)
            for bullet in bullets:
                if isinstance(bullet, dict): counts[bullet.get('provenance', 'Unknown')] += 1
                # Ignore non-dict bullets for provenance check

            for prov_type_enum in BulletProvenance:
                 prov_type = prov_type_enum.value
                 target = targets.get(prov_type, 0); actual = counts.get(prov_type, 0)
                 if actual != target:
                     valid = False
                     violations.append(f"{section_enum.value}: {prov_type} has {actual} (target: {target})")
                     failed.add(section_enum)
        if not valid: context._cache["VG_PROVENANCE_SPLIT_CHECK"] = {"violations": ", ".join(violations[:3]), "failed_sections": failed}
        return valid

    def _validate_authenticity_signal(self, context: ValidationContext) -> bool:
        auth_patterns_data = getattr(context.thematic_analysis, 'authenticity_patterns', {});
        auth_patterns = auth_patterns_data.get('patterns', {}) if isinstance(auth_patterns_data, dict) else {}
        if not auth_patterns: return True # Pass if no patterns

        verbs = auth_patterns.get('achievement_verb_patterns', []); phrasing = auth_patterns.get('competency_phrasing', [])
        target_signals = set(v.lower() for v in verbs[:10]) | set(p.lower().split(':')[0].split()[0] for p in phrasing[:5] if ':' in p and p.split())
        target_signals = {s for s in target_signals if s}

        full_text = ""; buffer_data = context.staging_buffer.data
        # Aggregate text from relevant sections (K.1, K.2, K.3, K.9)
        sections_to_scan = [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES]
        for sec_enum in sections_to_scan:
            value = buffer_data.get(sec_enum.value); # ... (aggregate text logic remains same) ...
            if isinstance(value, str): full_text += value + " "
            elif isinstance(value, list): full_text += " ".join(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value) + " "

        if not target_signals or not full_text: return True

        found = {sig for sig in target_signals if re.search(r'\b' + re.escape(sig) + r'\b', full_text.lower())}
        ratio = len(found) / len(target_signals) if target_signals else 0.0
        valid = ratio >= 0.3 # At least 30% match
        context._cache["VG_AUTHENTICITY_SIGNAL_CHECK"] = {"details": f"Found {len(found)}/{len(target_signals)} ({ratio:.1%}) auth signals."}
        return valid

    def _validate_exec_summary_vs_sections(self, context: ValidationContext) -> bool:
        """Validates K.1 similarity against other sections (using K0-K11 enums)."""
        exec_summary = context.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        if not exec_summary: return True

        dd = DuplicateDetector(); sections_content = {}
        # Gather content using K0-K11 enums
        enums_to_compare = [
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K2_UNIFY_BULLETS,
            ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K3_IBM_BULLETS,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES
        ]
        for sec_enum in enums_to_compare:
            content = context.staging_buffer.get(sec_enum.value)
            if content:
                 if isinstance(content, list): sections_content[sec_enum.name] = [str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in content if (str(item.get('text', str(item))) if isinstance(item,dict) else str(item))]
                 elif isinstance(content, str): sections_content[sec_enum.name] = content

        try: similarity_results = dd.compute_executive_summary_similarity(exec_summary, sections_content)
        except Exception as e: logging.warning(f"Exec summary similarity calc failed: {e}"); context._cache["VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY"] = {"failures": "Calc failed."}; return False

        threshold = 0.70; valid = True; failures = []; failed = set()
        for res in similarity_results:
            max_sim = res.get('max_similarity', 0.0)
            if max_sim >= threshold:
                valid = False; label = res.get('section_label', '?')
                failures.append(f"{label}: Max Sim {max_sim:.2f} >= {threshold:.2f}")
                try: failed.add(ResumeSection[label])
                except KeyError: pass # Ignore if label doesn't map back

        if not valid: context._cache["VG_EXEC_SUMMARY_VS_SECTION_SIMILARITY"] = {"failures": ", ".join(failures[:3]), "failed_sections": failed}
        return valid

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
import re
import json
import copy
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union # Ensure necessary types are imported

class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator', company_name: str, job_title: str):
        self.master_resume = master_resume
        self.orchestrator = orchestrator # For access to validation results etc.
        self.company_name = company_name
        self.job_title = job_title

    @functools.cached_property
    def _safe_company_name(self) -> str:
        """Sanitizes and caches the company name for use in filenames."""
        # Remove characters not suitable for filenames, replace spaces with underscores
        name = re.sub(r'[^\w\s-]', '', self.company_name)
        return re.sub(r'[-\s]+', '_', name).strip('_')

    @functools.cached_property
    def _safe_job_title(self) -> str:
        """Sanitizes and caches the job title for use in filenames."""
        # Remove characters not suitable for filenames, replace spaces with underscores
        title = re.sub(r'[^\w\s-]', '', self.job_title)
        return re.sub(r'[-\s]+', '_', title).strip('_')

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str, # Passed again for clarity, though stored in self
        job_title: str,    # Passed again for clarity, though stored in self
        thematic_analysis: ThematicAnalysis,
        job_description: str = None,
        jd_url: str = "" # Added jd_url parameter
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report, App Tracker).
        Uses K0-K11 Enum scheme.
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        """
        file_paths = {}
        file_contents = {}
        validation_results = [] # Collect results from rendering steps

        # --- 1. Render Resume Artifact ---
        try:
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=True, severity=ValidationSeverity.INFO,
                message="Resume MD rendered successfully."
            ))
        except Exception as e:
            logging.error(f"Error rendering Resume MD: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Resume MD: {e}"
            ))
            file_contents['resume_md'] = f"[ERROR: Resume Rendering Failed: {e}]" # Add error placeholder

        # --- 2. Render Skills Artifact (Uses K.10) ---
        try:
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=True, severity=ValidationSeverity.INFO,
                message="Skills TXT rendered successfully."
            ))
        except Exception as e:
            logging.error(f"Error rendering Skills TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Skills TXT: {e}"
            ))
            file_contents['skills'] = f"[ERROR: Skills Rendering Failed: {e}]"

        # --- 3. Render Cover Letter Artifact (Uses K.11) ---
        try:
            path, content = self._render_cover_letter_artifact(staging_buffer)
            file_paths['cover_letter'] = path
            file_contents['cover_letter'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=True, severity=ValidationSeverity.INFO,
                message="Cover Letter TXT rendered successfully."
            ))
        except Exception as e:
            logging.error(f"Error rendering Cover Letter TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Cover Letter TXT: {e}"
            ))
            file_contents['cover_letter'] = f"[ERROR: Cover Letter Rendering Failed: {e}]"

        # --- 4. Render QA Report Artifact (Path only) ---
        try:
            path, content_placeholder = self._render_qa_report_artifact()
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content_placeholder # Placeholder, content generated later
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=True, severity=ValidationSeverity.INFO,
                message="QA Report path generated."
            ))
        except Exception as e:
            logging.error(f"Error generating QA Report path: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
            ))

        # --- 5. Render App Tracker Artifact (and Validate) ---
        try:
            path, content, app_tracker_validation_results = self._render_app_tracker_artifact(file_paths, jd_url=jd_url) # Pass jd_url
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content
            validation_results.extend(app_tracker_validation_results) # Add validation results
            # Add overall AppTracker render status
            if any(not vr.passed for vr in app_tracker_validation_results if vr.rule_id.startswith("APP_TRACKER_")):
                 logging.warning("AppTracker rendering completed but failed validation.")
            else:
                 validation_results.append(ValidationResult(
                      rule_id="RENDER_APP_TRACKER", passed=True, severity=ValidationSeverity.INFO,
                      message="App Tracker JSON rendered and validated successfully."
                 ))

        except Exception as e:
            logging.error(f"Error rendering App Tracker JSON: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render App Tracker JSON: {e}"
            ))
            file_contents['app_tracker'] = f"[ERROR: App Tracker Rendering Failed: {e}]"

        return file_paths, (validation_results, file_contents)

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the resume markdown artifact."""
        content = self._render_resume_markdown(staging_buffer)
        # Use safe names for filename
        path = f"Resume_{self._safe_company_name}_{self._safe_job_title}.md"
        return path, content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: str) -> Tuple[str, str]:
        """Renders the skills artifact (using K.10)."""
        content = self._render_skills(staging_buffer, job_description)
        # Use safe names for filename
        path = f"Skills_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Renders the cover letter artifact (using K.11)."""
        content = staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '') # Use K.11
        # Use safe names for filename
        path = f"CoverLetter_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, content

    def _render_qa_report_artifact(self) -> Tuple[str, str]:
        """Renders the QA report artifact path and placeholder."""
        path = f"QA_Report_{self._safe_company_name}_{self._safe_job_title}.md"
        # Content generated in HOP-8, return placeholder.
        return path, "[QA Report Content Placeholder - Generated in HOP-8]"

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str], jd_url: str = "") -> Tuple[str, str, List[ValidationResult]]:
        """Renders the application tracker artifact and validates it."""
        app_tracker_data = self._render_app_tracker(file_paths, jd_url=jd_url) # Pass jd_url
        validation_results = []

        # Validate the generated tracker data
        try:
            validator = AppTrackerQAValidator()
            validation_result_dict = validator.validate_tracker_data([app_tracker_data]) # Expects list

            if "BLOCKED" in validation_result_dict.get("result", ""):
                errors = validation_result_dict.get('errors', [])
                for error in errors:
                    validation_results.append(ValidationResult(
                        rule_id=f"APP_TRACKER_{error.get('RULE_ID', 'UNKNOWN')}",
                        passed=False,
                        severity=ValidationSeverity.HIGH, # Treat AppTracker errors as HIGH
                        message=f"AppTracker Error (Row {error.get('row_index')} Field '{error.get('field')}'): {error.get('message')}",
                        details=error
                    ))
            else:
                validation_results.append(ValidationResult(
                    rule_id="APP_TRACKER_VALIDATION", passed=True, severity=ValidationSeverity.INFO,
                    message="AppTracker JSON passed validation rules."
                ))

        except Exception as e:
            logging.error(f"App tracker validation failed during execution: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="APP_TRACKER_VALIDATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"App tracker validation failed during execution: {e}"
            ))

        content = json.dumps(app_tracker_data, indent=2)
        path = f"AppTracker_{self._safe_company_name}_{self._safe_job_title}.json"
        return path, content, validation_results

    # --- UPDATED RESUME_RENDER_CONFIG for K0-K11 ---
    RESUME_RENDER_CONFIG = [
        # --- K.0 ---
        {"type": "simple", "source": ResumeSection.K0_NAME, "render_method": "_render_name"},
        {"type": "simple", "source": ResumeSection.K0_HEADLINE, "render_method": "_render_headline"},
        {"type": "simple", "source": ResumeSection.K0_CONTACT, "render_method": "_render_contact"},
        # --- K.1 ---
        {"type": "header", "text": "## EXECUTIVE SUMMARY"},
        {"type": "simple", "source": ResumeSection.K1_EXECUTIVE_SUMMARY, "render_method": "_render_paragraph"},
        # --- Experience Header ---
        {"type": "header", "text": "## PROFESSIONAL EXPERIENCE"},
        # --- K.2 Unify ---
        {"type": "experience", "master_index": 0, "overview_source": ResumeSection.K2_UNIFY_OVERVIEW, "bullets_source": ResumeSection.K2_UNIFY_BULLETS},
        # --- K.3 IBM ---
        {"type": "experience", "master_index": 1, "overview_source": ResumeSection.K3_IBM_OVERVIEW, "bullets_source": ResumeSection.K3_IBM_BULLETS},
        # --- K.4 TraderSense (Narrative) ---
        # Note: Master index 2 corresponds to TraderSense in MASTER_RESUME_JSON
        {"type": "experience_narrative", "master_index": 2, "narrative_source": ResumeSection.K4_TRADERSENSE_NARRATIVE},
        # --- K.5 EY (Narrative) ---
        # Note: Master index 3 corresponds to EY
        {"type": "experience_narrative", "master_index": 3, "narrative_source": ResumeSection.K5_EY_NARRATIVE},
        # --- K.6 Early Career (Narrative) ---
        # Note: Master index 4 corresponds to Early Career
        {"type": "experience_narrative", "master_index": 4, "narrative_source": ResumeSection.K6_EARLY_CAREER_NARRATIVE},
        # --- K.7 Education ---
        {"type": "header", "text": "## EDUCATION"},
        {"type": "education", "source": ResumeSection.K7_EDUCATION},
        # --- K.8 Certifications ---
        {"type": "header", "text": "## CERTIFICATIONS & CREDENTIALS"},
        {"type": "certifications", "source": ResumeSection.K8_CERTIFICATIONS},
        # --- K.9 Competencies ---
        {"type": "header", "text": "## STRATEGIC & TECHNICAL COMPETENCIES"},
        {"type": "competencies", "source": ResumeSection.K9_COMPETENCIES},
        # --- K.10 Skills (Not typically rendered in main resume MD) ---
    ]

    def _render_resume_markdown(self, staging_buffer: ImmutableStagingBuffer) -> str:
        """
        Render resume as Markdown, driven by the UPDATED RESUME_RENDER_CONFIG (K0-K11).
        Handles standard experience sections and narrative sections differently.
        """
        output_lines = []
        master_experience = self.master_resume.get("professional_experience", [])

        for config in self.RESUME_RENDER_CONFIG:
            render_type = config["type"]

            if render_type == "header":
                prefix = "\n" if output_lines else ""
                output_lines.append(f'{prefix}{config["text"]}')

            elif render_type == "simple":
                content = staging_buffer.get(config["source"].value)
                render_method = getattr(self, config["render_method"])
                if content: output_lines.append(render_method(content))

            elif render_type == "experience": # For K.2 (Unify), K.3 (IBM)
                master_index = config["master_index"]
                if master_index < len(master_experience):
                    master_exp = master_experience[master_index]
                    overview = staging_buffer.get(config["overview_source"].value)
                    bullets = staging_buffer.get(config["bullets_source"].value)
                    # Render using overview + bullets format
                    output_lines.append(self._render_experience_section_std(master_exp, overview, bullets))
                else: logging.warning(f"Master experience index {master_index} out of bounds.")

            elif render_type == "experience_narrative": # For K.4, K.5, K.6
                master_index = config["master_index"]
                if master_index < len(master_experience):
                    master_exp = master_experience[master_index]
                    narrative = staging_buffer.get(config["narrative_source"].value)
                    # Render using narrative format (no bullets/overview from buffer)
                    output_lines.append(self._render_experience_section_narrative(master_exp, narrative))
                else: logging.warning(f"Master experience index {master_index} out of bounds.")

            elif render_type == "education": # K.7
                content = staging_buffer.get(config["source"].value)
                if content: output_lines.append(self._render_education_section(content))

            elif render_type == "certifications": # K.8
                content = staging_buffer.get(config["source"].value)
                if content: output_lines.append(self._render_certifications_section(content))

            elif render_type == "competencies": # K.9
                content = staging_buffer.get(config["source"].value)
                if content: output_lines.append(self._render_competencies_section(content))

        return "\n".join(output_lines).strip() + "\n" # Ensure single trailing newline


    # --- Hardened Render Methods (v9.90 style, updated for narratives) ---

    def _render_name(self, content: str) -> str: return f"## {content.strip()}\n"
    def _render_headline(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_contact(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_paragraph(self, content: str) -> str: return f"{content.strip()}\n"

    def _render_experience_section_std(self, master_exp: Dict, overview: Optional[str], bullets: Optional[List[Union[str, Dict]]]) -> str:
        """ Renders standard experience sections (K.2, K.3) with Overview + Bullets. """
        lines = self._render_experience_header(master_exp) # Get common header lines

        # Overview
        if overview and isinstance(overview, str) and overview.strip():
            lines.append(f"\n{overview.strip()}") # Blank line before

        # Bullets
        bullet_lines = []
        bullets_list = bullets if isinstance(bullets, list) else []
        for bullet in bullets_list:
            text = (bullet.get('text', str(bullet)).strip() if isinstance(bullet, dict) else str(bullet).strip())
            if text: bullet_lines.append(f"* {text}") # Enforce '* '

        if bullet_lines:
            lines.append("\n" + "\n".join(bullet_lines)) # Blank line before

        return "\n".join(lines) + "\n" # Trailing blank line

    def _render_experience_section_narrative(self, master_exp: Dict, narrative: Optional[str]) -> str:
        """ Renders narrative experience sections (K.4, K.5, K.6). """
        lines = self._render_experience_header(master_exp) # Get common header lines

        # Narrative block
        if narrative and isinstance(narrative, str) and narrative.strip():
            lines.append(f"\n{narrative.strip()}") # Blank line before

        # Add master highlights if they exist (e.g., for TraderSense which has highlights in master)
        master_highlights = master_exp.get('highlights', [])
        highlight_lines = []
        if master_highlights and isinstance(master_highlights, list):
             for hl in master_highlights:
                  if isinstance(hl, str) and hl.strip():
                      highlight_lines.append(f"* {hl.strip()}") # Render master highlights as bullets

        if highlight_lines:
             # If narrative exists, add blank line before highlights, otherwise just add highlights
             prefix = "\n" if narrative and narrative.strip() else ""
             lines.append(prefix + "\n".join(highlight_lines))

        return "\n".join(lines) + "\n" # Trailing blank line

    def _render_experience_header(self, master_exp: Dict) -> List[str]:
        """ Helper to render the common Company/Location/Title/Dates header. """
        header_lines = []
        # Line 1: **Company | Location**
        company = master_exp.get('company', '').strip(); location = master_exp.get('location', '').strip()
        line1 = f"**{' | '.join(filter(None, [company, location]))}**"
        if line1 != "** **": header_lines.append(line1)

        # Line 2: **Title | Dates**
        title = master_exp.get('title', '').strip()
        start = master_exp.get('dates', {}).get('start', '').strip()
        end = master_exp.get('dates', {}).get('end', '').strip()
        date_str = " – ".join(filter(None, [start, end]))
        line2 = f"**{' | '.join(filter(None, [title, date_str]))}**"
        if line2 != "** **": header_lines.append(line2)

        return header_lines

    def _render_education_section(self, education_list: List[Dict]) -> str: # K.7
        lines = []
        if not isinstance(education_list, list): return ""
        for edu in education_list:
            if not isinstance(edu, dict): continue
            parts = [edu.get('degree', ''), edu.get('institution', '')]
            line = ", ".join(filter(None, [p.strip() for p in parts]))
            notes = edu.get('notes', '').strip()
            if notes: line += f" ({notes})"
            if line: lines.append(line)
        return "\n".join(lines) + "\n"

    def _render_certifications_section(self, certifications_list: List[str]) -> str: # K.8
        if not isinstance(certifications_list, list): return ""
        lines = [cert for cert in certifications_list if isinstance(cert, str) and cert.strip()]
        return "\n".join(lines) + "\n"

    def _render_competencies_section(self, competencies_list: List[Union[str, Dict]]) -> str: # K.9
        lines = []
        if not isinstance(competencies_list, list): return ""
        for comp in competencies_list:
            text = (comp.get('text', str(comp)).strip() if isinstance(comp, dict) else str(comp).strip())
            if text:
                text = re.sub(r'^[•*]\s*', '', text) # Remove existing bullets
                lines.append(f"* {text}") # Enforce '* '
        return "\n".join(lines) + "\n"

    # --- End of Hardened Render Methods ---

    def _render_skills(self, staging_buffer: ImmutableStagingBuffer, job_description: str = None) -> str:
        """ Render skills (K.10) with validation. """
        skills_list = staging_buffer.get(ResumeSection.K10_SKILLS.value) # Use K.10
        output_lines = []; valid_skills = []; malformed = []

        if not isinstance(skills_list, list) or not skills_list:
            return "• Error: K.10_Skills list not found or invalid in staging buffer."
        if isinstance(skills_list[0], str) and skills_list[0].startswith("Error:"):
            return "\n\n".join(skills_list) # Return error message from generation

        for skill in skills_list:
            if isinstance(skill, str):
                cleaned = skill.strip(); wc = len(cleaned.split())
                if 1 <= wc <= 3: valid_skills.append(f"• {cleaned}")
                else: malformed.append(f"• {cleaned} [Warning: Malformed - {wc} words]")
            else: malformed.append(f"• {str(skill).strip()} [Warning: Non-string skill]")

        output_lines.extend(valid_skills); output_lines.extend(malformed)
        return "\n\n".join(output_lines)

    def _render_app_tracker(self, file_paths: Dict[str, str], jd_url: str = "") -> Dict:
        """Render application tracker (v4 schema), including JD URL."""
        tracker = copy.deepcopy(APP_TRACKER_SCHEMA_V4) # Use global schema
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")

        tracker['Company'] = self.company_name
        tracker['Job Title'] = self.job_title
        tracker['JD URL'] = jd_url # Populate JD URL
        tracker['Application Date'] = datetime.now().strftime("%m/%d/%Y")
        tracker['Base Resume'] = ""
        # Construct versioned resume filename using safe names
        tracker['Versioned Resume'] = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        tracker['Pipeline Status'] = 'Applied'

        return tracker
 
# ============================================================================
# WORKFLOW ORCHESTRATOR (STATEFUL RETRY VERSION W/ REFACTORED QA)
# ============================================================================
from dataclasses import asdict # Ensure asdict is imported
import shutil # For cache clearing if needed in __init__
import time # For potential delays or timing

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

        # --- For Deduplication Analysis ---
        self.dup_detector = None # Will be set in HOP-2
        self.similarity_matrix_data = None
        self.executive_summary_similarity_data = None
        self.overview_similarity_data = None
        self.dedup_analysis_timestamp = None
        # --- End Deduplication ---

        self.hash_chain = [] # For CoC
        self.constraints = ContentConstraintsConfig() # For reference if needed
        self.jd_enforcer = JDEnforcementValidator() # For JD checks

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # API Key Check
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

        # Log LLM Provider Info (Assuming RAGConfig exists)
        try:
             # Make sure RAGConfig is accessible (defined or imported)
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

    # --- QA Report Section Configuration (Moved Inside Orchestrator) ---
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis", "validation_results"]},
        {"method": "_build_qa_section_2_signal_flow_map", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_word_count_distribution", "args": ["validation_results"]},
        {"method": "_build_qa_section_5_provenance", "args": ["staging_buffer"]},
        {"method": "_build_qa_section_6_authenticity", "args": ["validation_results"]},
        {"method": "_build_qa_section_7_prod_readiness", "args": ["validation_results"]},
        {"method": "_build_qa_section_8_pairwise_similarity", "args": []}, # Uses self attributes populated in HOP-7.5
        {"method": "_build_qa_section_9_pipeline_health", "args": []}, # Uses self attributes (hop_checkpoints)
        {"method": "_build_qa_section_10_structural", "args": ["validation_results"]},
        {"method": "_build_qa_section_11_cover_letter", "args": ["validation_results"]},
        {"method": "_build_qa_section_12_jd_enforcement", "args": []}, # Uses self attributes (jd_enforcer)
        {"method": "_build_qa_section_13_final_format", "args": ["validation_results", "file_contents"]},
    ]
    # --- End QA Config ---

    def _execute_hop_0_jd_analysis(self, job_description: str) -> Tuple[ThematicAnalysis, int]:
        """
        Executes HOP-0: Job Description Analysis & RAG.
        Returns (ThematicAnalysis, api_calls_made)
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-0] Job Description Analysis & RAG...")
        jd_analyzer = self._create_jd_analyzer()
        total_api_calls = 0
        thematic_analysis = None # Initialize
        try:
            # Analyze method now returns (analysis, call_count)
            thematic_analysis, api_calls = jd_analyzer.analyze(job_description)
            total_api_calls = api_calls # Store the count

            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG", [],
                {"signal_score": getattr(thematic_analysis, 'signal_quality_score', 0.0)},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": total_api_calls} # Store call count in metadata
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint) # Check status based on internal results if any
            return thematic_analysis, total_api_calls # Return analysis and count
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-0] FAILED: {e}", exc_info=False) # exc_info=False for brevity
            # Try to get call count even on failure
            calls_on_fail = getattr(jd_analyzer, 'total_api_calls_hop0', 0)
            hop_checkpoint = self._create_checkpoint(
                "HOP-0", "JD Analysis & RAG",
                [ValidationResult("HOP-0_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                None, start_time=hop_start_time, error_message=str(e),
                metadata={"gemini_api_calls": calls_on_fail} # Log calls even on failure
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-0 failed: {e}")

    def _execute_hop_1_clerk_extraction(self) -> Dict:
        """Executes HOP-1: Master Resume Extraction & Hallucination Check."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-1] Master Resume Extraction...")
        extracted_data = {} # Initialize
        try:
            clerk = ClerkExtractor(self.master_resume)
            extracted_data, hop_results = clerk.extract()
            bullets_extracted = sum(len(s.get('bullets', [])) for s in extracted_data.get('experience_sections', []))
            hop_checkpoint = self._create_checkpoint(
                "HOP-1", "Clerk Extraction", hop_results,
                {"bullets_extracted": bullets_extracted},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0} # No API calls here
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True) # Allow hallucination warnings
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
        """Executes HOP-2: Data Enrichment (Verbs, Duplicates)."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-2] Data Enrichment...")
        enriched_scaffold = {} # Initialize
        try:
            enricher = DataEnricher()
            # Pass orchestrator instance (`self`) to enricher for storing dup_detector
            enriched_scaffold, hop_results = enricher.enrich(extracted_data, thematic_analysis, orchestrator=self)
            # Ensure dup_detector is stored on self for HOP-7.5
            if not hasattr(self, 'dup_detector') or self.dup_detector is None:
                self.dup_detector = enricher.duplicate_detector # Store it
                self.logger.debug("Stored DuplicateDetector instance from HOP-2.")

            hop_checkpoint = self._create_checkpoint(
                "HOP-2", "Data Enrichment", hop_results,
                {"sections_enriched": len(enriched_scaffold.get('experience_sections',[]))},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0} # No API calls here
            )
            self.hop_checkpoints.append(hop_checkpoint)
            self._check_hop_status(hop_checkpoint, allow_warnings=True) # Allow duplicate warnings
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
        """
        Executes HOP-3: Content Generation with STATEFUL RETRY logic.
        Returns (final_artist_output, total_api_calls)
        """
        self.logger.info("\n[HOP-3] Content Generation (Artist) with Stateful Retry...")
        hop_start_time = datetime.now()
        total_api_calls_hop3 = 0 # Initialize counter for this hop

        artist = ArtistGenerator(
            master_resume=self.master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis,
            previous_failures=[] # Initial empty list
        )

        validator = PreFlightValidator(self.master_resume)

        temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2] # Standard schedule
        max_attempts = len(temperature_schedule)

        # State Tracking
        final_generation_state: Dict[str, Any] = {}
        locked_section_temps: Dict[ResumeSection, float] = {}
        copied_content: Dict[str, Any] = {}
        all_llm_sections = {
            config["section"] for config in artist.ARTIST_GENERATION_CONFIG
            if not config["method_name"].startswith("_copy_") and
               not config["method_name"] == "_generate_dummy_header"
        }
        sections_to_generate = all_llm_sections.copy()
        final_validation_results = []
        all_passed = False
        final_attempt_number = 0 # Track the final attempt number

        # Run copy/dummy methods ONCE
        try:
            dummy_sections = {
                config["section"] for config in artist.ARTIST_GENERATION_CONFIG
                if config["method_name"].startswith("_copy_") or
                   config["method_name"] == "_generate_dummy_header"
            }
            # Artist.generate now returns (output, results, calls)
            copied_output, _, calls_copy = artist.generate(
                sections_to_generate=dummy_sections,
                temperature_overrides={}
            )
            total_api_calls_hop3 += calls_copy # Should be 0, but track anyway
            copied_content.update(copied_output)
            final_generation_state.update(copied_output)
            self.logger.info(f"  ✓ Copied/Dummy sections generated: {list(copied_output.keys())}")
        except Exception as e:
            # Handle failure during copy - critical
            hop_checkpoint = self._create_checkpoint(
                 "HOP-3", "Artist Generation (Copy Phase)",
                 [ValidationResult("ARTIST_COPY_FAIL", False, ValidationSeverity.CRITICAL, f"Copy failed: {e}")],
                 None, start_time=hop_start_time, error_message=f"Initial content copy failed: {e}",
                 metadata={"gemini_api_calls": total_api_calls_hop3}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            raise HopExecutionError(f"HOP-3 failed during initial content copy: {e}")

        # --- Stateful Retry Loop ---
        for attempt, temperature in enumerate(temperature_schedule, 1):
            final_attempt_number = attempt
            if not sections_to_generate:
                self.logger.info(f"  All sections passed validation. Exiting generation loop.")
                all_passed = True # Set flag indicating successful completion
                break # All sections locked

            self.logger.info(f"  Attempt {attempt}/{max_attempts} @ Temp {temperature:.1f}...")
            self.logger.info(f"    Sections to generate: {[s.name for s in sections_to_generate]}")
            attempt_start_time = time.time()
            calls_this_attempt = 0

            # 1. Generate sections
            try:
                temp_overrides = {section: temperature for section in sections_to_generate}
                # generate returns (output, results, calls)
                newly_generated_content, generation_results, calls_gen = artist.generate(
                    sections_to_generate=sections_to_generate,
                    temperature_overrides=temp_overrides
                )
                calls_this_attempt += calls_gen
                total_api_calls_hop3 += calls_gen # Aggregate total calls for the hop

                # Check for immediate generation failure reported by artist.generate
                if not generation_results or not generation_results[0].passed:
                    generation_error = generation_results[0].message if generation_results else "Unknown generation error"
                    # Log the generation error before raising HopExecutionError
                    logging.error(f"    Artist.generate() reported failure on attempt {attempt}: {generation_error}")
                    # Store this as the final validation result for this hop
                    final_validation_results = generation_results
                    all_passed = False
                    # Stop the loop immediately on generation failure
                    raise HopExecutionError(f"Artist.generate() failed on attempt {attempt}: {generation_error}")

            except HopExecutionError as he: # Catch explicit halts from generation
                 self.logger.error(f"    ✗ Generation HALTED on Attempt {attempt}: {he}", exc_info=False)
                 # Store the halt reason
                 final_validation_results = [ValidationResult(f"ARTIST_GENERATION_HALT_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation halted: {he}")]
                 all_passed = False
                 break # Exit loop on hard generation failure
            except Exception as e:
                 self.logger.error(f"    ✗ Generation Attempt {attempt} FAILED unexpectedly: {e}", exc_info=False) # exc_info=False
                 final_validation_results = [ValidationResult(f"ARTIST_GENERATION_ERROR_{attempt}", False, ValidationSeverity.CRITICAL, f"Generation failed unexpectedly: {e}")]
                 all_passed = False
                 break # Exit loop on unexpected error

            # 2. Update current state
            final_generation_state.update(newly_generated_content)

            # 3. Validate entire state
            temp_buffer = ImmutableStagingBuffer()
            for key, value in final_generation_state.items():
                if value is not None: temp_buffer.set(key, value)
            temp_buffer.lock()

            try:
                # Pass sections_to_generate as sections_under_test
                current_validation_results, current_all_passed, failed_sections = validator.validate(
                    temp_buffer, thematic_analysis, job_description,
                    sections_under_test=sections_to_generate
                )
                # Store results of this attempt - will be overwritten if next attempt happens
                final_validation_results = current_validation_results
                all_passed = current_all_passed # Overall pass status for THIS attempt

            except Exception as e:
                self.logger.error(f"    ✗ Validation Attempt {attempt} FAILED during execution: {e}", exc_info=False) # exc_info=False
                final_validation_results = [ValidationResult(f"VALIDATION_EXECUTION_{attempt}", False, ValidationSeverity.CRITICAL, f"Validation logic failed: {e}")]
                all_passed = False
                break # Exit loop on validation execution error

            attempt_duration = time.time() - attempt_start_time
            self.logger.info(f"    Attempt {attempt} completed in {attempt_duration:.2f}s. Validation passed: {all_passed}. API Calls: {calls_this_attempt}")

            # 4. Update state based on validation
            sections_that_passed_this_attempt = sections_to_generate - failed_sections

            for passed_section in sections_that_passed_this_attempt:
                # Only lock if not already locked at a higher (or equal) temperature
                if passed_section not in locked_section_temps or temperature <= locked_section_temps[passed_section]:
                    locked_section_temps[passed_section] = temperature
                    self.logger.info(f"    ✓ LOCKED: {passed_section.name} @ {temperature:.1f}")

            # Set sections for the *next* iteration
            sections_to_generate = failed_sections

            if not all_passed:
                self.logger.warning(f"    ✗ {len(failed_sections)} sections failed validation and will be retried: {[s.name for s in failed_sections]}")
                # Log specific HIGH/CRITICAL failures for context
                for vr in final_validation_results:
                    if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                         try: msg = vr.message(vr.details) if callable(vr.message) else vr.message
                         except Exception: msg = str(vr.message)
                         self.logger.warning(f"      - [{vr.severity.name}] {vr.rule_id}: {msg}")

        # --- End of Loop ---

        # 5. Final Outcome
        artist_output = final_generation_state # The final state after all attempts
        self.validation_results = final_validation_results # Store results from the LAST attempt

        # Determine final status message based on whether the loop completed successfully or broke early
        if all_passed and not sections_to_generate: # Successfully completed all sections
            status_message = f"Artist Generation successful after {final_attempt_number} attempt(s)"
            hop_status = HopStatus.PASS
            error_msg = None
        else: # Loop ended due to failure or exhaustion
            status_message = f"Artist Generation FAILED after {final_attempt_number} attempt(s)"
            hop_status = HopStatus.FAIL
            # Determine primary reason for failure
            failed_val_rules = [vr for vr in final_validation_results if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value]
            if failed_val_rules:
                 primary_fail = failed_val_rules[0]
                 try: fail_reason = primary_fail.message(primary_fail.details) if callable(primary_fail.message) else primary_fail.message
                 except Exception: fail_reason = str(primary_fail.message)
                 error_msg = f"Validation Failed: {primary_fail.rule_id} - {fail_reason}"
            elif final_validation_results and not final_validation_results[0].passed: # If generation itself failed
                  error_msg = final_validation_results[0].message # Use the generation failure message
            else: # If loop exhausted
                  error_msg = f"Validation failed after all {max_attempts} attempts. Last failed sections: {[s.name for s in sections_to_generate]}"

        hop_checkpoint = self._create_checkpoint(
            "HOP-3", status_message,
            final_validation_results,
            {"sections_generated": len(all_llm_sections), "sections_copied": len(copied_content)}, # Summary output
            start_time=hop_start_time,
            metadata={
                "gemini_api_calls": total_api_calls_hop3, # Total calls for the hop
                "attempts_made": final_attempt_number,
                "final_temperatures": {k.name: v for k, v in locked_section_temps.items()}
            },
            error_message=error_msg # Include failure reason if applicable
        )
        hop_checkpoint.status = hop_status # Set status explicitly
        self.hop_checkpoints.append(hop_checkpoint)

        if hop_status == HopStatus.FAIL:
            self.logger.error(f"  ✗ HOP-3 FAILED: {error_msg}")
            raise HopExecutionError(error_msg or "HOP-3 failed content generation or validation.")
        else:
             avg_temp = sum(locked_section_temps.values()) / len(locked_section_temps) if locked_section_temps else 0.0
             self.logger.info(f"  ✓ HOP-3 successful after {final_attempt_number} attempt(s). Final avg. locked temp: {avg_temp:.2f}")

        return artist_output, total_api_calls_hop3 # Return final output and total calls


    def _execute_hop_4_staging_and_sanitization(self, artist_output: Dict) -> ImmutableStagingBuffer:
        """Executes HOP-4 (Staging) and HOP-4.5 (Sanitization & Locking)."""
        # --- HOP-4: Staging ---
        hop4_start_time = datetime.now()
        self.logger.info("\n[HOP-4] Populating Staging Buffer...")
        staging_buffer = ImmutableStagingBuffer()
        sections_populated = 0
        try:
            for key, value in artist_output.items():
                section_key_str = key
                try: section_key_str = ResumeSection(key).value # Use enum value if key matches enum name
                except ValueError: pass # Keep original key if not enum name

                if value is not None:
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
             hop4_checkpoint = self._create_checkpoint(
                 "HOP-4", "Staging Buffer Population",
                 [ValidationResult("HOP-4_STAGING_ERROR", False, ValidationSeverity.CRITICAL, str(sbe))],
                 None, start_time=hop4_start_time, error_message=str(sbe),
                 metadata={"gemini_api_calls": 0}
             )
             hop4_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop4_checkpoint)
             raise HopExecutionError(f"HOP-4 failed: {sbe}")
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-4] FAILED unexpectedly: {e}", exc_info=False)
             hop4_checkpoint = self._create_checkpoint(
                 "HOP-4", "Staging Buffer Population",
                 [ValidationResult("HOP-4_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 None, start_time=hop4_start_time, error_message=str(e),
                 metadata={"gemini_api_calls": 0}
             )
             hop4_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop4_checkpoint)
             raise HopExecutionError(f"HOP-4 failed: {e}")

        # --- HOP-4.5: Sanitization & Locking ---
        hop45_start_time = datetime.now()
        self.logger.info("\n[HOP-4.5] Text Sanitization & Locking...")
        sanitized_buffer = None # Initialize
        try:
            sanitizer = TextSanitizer()
            # Sanitize buffer returns (validation_results, sanitized_data_dict)
            hop45_results, sanitized_data = sanitizer.sanitize_buffer(staging_buffer)

            # Create a new buffer for sanitized data
            sanitized_buffer = ImmutableStagingBuffer()
            for key, value in sanitized_data.items():
                sanitized_buffer.set(key, value)
            self.logger.info(f"  ✓ Sanitization applied. Fixes: {sanitizer.sanitization_counts}")

            sanitized_buffer.lock()
            self.logger.info(f"  ✓ Sanitized buffer locked at {sanitized_buffer._lock_timestamp}.")

            hop45_checkpoint = self._create_checkpoint(
                "HOP-4.5", "Text Sanitization & Lock", hop45_results,
                {"buffer_locked": True},
                start_time=hop45_start_time,
                metadata={"gemini_api_calls": 0, "sanitization_counts": sanitizer.sanitization_counts}
            )
            self.hop_checkpoints.append(hop45_checkpoint)
            # Allow info results from sanitizer, but fail on critical errors during process
            self._check_hop_status(hop45_checkpoint, allow_warnings=True, check_critical_only=True)
            return sanitized_buffer # Return the new, sanitized, locked buffer

        except StagingBufferError as sbe: # Catch locking errors
             self.logger.error(f"  ✗ [HOP-4.5] Locking FAILED: {sbe}", exc_info=False)
             # Ensure the *original* buffer is locked if sanitization failed but buffer exists
             if staging_buffer and not staging_buffer.is_locked(): staging_buffer.lock()
             hop45_checkpoint = self._create_checkpoint(
                 "HOP-4.5", "Text Sanitization & Lock",
                 [ValidationResult("HOP-4.5_LOCK_ERROR", False, ValidationSeverity.CRITICAL, str(sbe))],
                 {"buffer_locked": staging_buffer.is_locked() if staging_buffer else False},
                 start_time=hop45_start_time, error_message=str(sbe),
                 metadata={"gemini_api_calls": 0}
             )
             hop45_checkpoint.status = HopStatus.FAIL
             self.hop_checkpoints.append(hop45_checkpoint)
             raise HopExecutionError(f"HOP-4.5 failed: {sbe}")
        except Exception as e:
            self.logger.error(f"  ✗ [HOP-4.5] FAILED unexpectedly: {e}", exc_info=False)
            # Ensure the original buffer is locked
            if staging_buffer and not staging_buffer.is_locked(): staging_buffer.lock()
            hop45_checkpoint = self._create_checkpoint(
                "HOP-4.5", "Text Sanitization & Lock",
                [ValidationResult("HOP-4.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                {"buffer_locked": staging_buffer.is_locked() if staging_buffer else False},
                start_time=hop45_start_time, error_message=str(e),
                 metadata={"gemini_api_calls": 0}
            )
            hop45_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop45_checkpoint)
            raise HopExecutionError(f"HOP-4.5 failed: {e}")


    def _execute_hop_5_validation(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str) -> List[ValidationResult]:
        """
        Executes HOP-5: Pre-flight Validation on the sanitized, locked buffer.
        Stores results in self.validation_results.
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-5] Final Pre-flight Validation (Post-Sanitization)...")
        if not staging_buffer.is_locked():
             self.logger.error("  ✗ CRITICAL: Buffer is not locked entering HOP-5!")
             staging_buffer.lock() # Force lock if somehow missed

        final_validation_results = [] # Initialize
        try:
            validator = PreFlightValidator(self.master_resume)
            # Validate method returns (results, all_passed_bool, failed_sections_set)
            # We don't need failed_sections_set here as retries are finished
            hop_results, all_passed, _ = validator.validate(
                staging_buffer, thematic_analysis, job_description,
                sections_under_test=None # Validate all sections
            )

            # Store final validation results on the orchestrator
            final_validation_results = hop_results
            self.validation_results = final_validation_results # Overwrite with these final results

            # Determine check counts for metadata
            total_rules_checked = len(validator.engine.rules)
            passed_rules = sum(1 for vr in hop_results if vr.passed)

            hop_checkpoint = self._create_checkpoint(
                "HOP-5", "Pre-flight Validation", hop_results,
                {"passed_rules": passed_rules, "total_rules": total_rules_checked, "all_passed": all_passed},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)

            # Check status based on CRITICAL/HIGH failures (zero tolerance for proceeding)
            # Allow_warnings=False ensures HIGH failures trigger halt via _check_hop_status
            self._check_hop_status(hop_checkpoint, allow_warnings=False, check_critical_only=False)

            return final_validation_results
        except Exception as e:
             self.logger.error(f"  ✗ [HOP-5] FAILED during validation logic: {e}", exc_info=False)
             error_result = ValidationResult("HOP-5_EXECUTION", False, ValidationSeverity.CRITICAL, f"Validation execution failed: {e}")
             # Ensure error result is stored
             final_validation_results = [error_result]
             self.validation_results = final_validation_results

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
        """Executes HOP-6: Gate Decision based on HOP-5 results."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-6] Gate Decision...")
        gate_decision = GateDecision.HALT # Default to HALT
        gate_reason = "Initialization error"
        try:
            gate_engine = GateDecisionEngine()
            gate_decision, gate_reason = gate_engine.decide(hop5_results) # Use final results from HOP-5

            self.logger.info(f"  Decision: {gate_decision.value}")
            self.logger.info(f"  Reason: {gate_reason}")

            hop_checkpoint = self._create_checkpoint(
                "HOP-6", "Gate Decision", [], # No new validations here
                {"decision": gate_decision.value, "reason": gate_reason},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)

            # Check status based on the decision itself
            if gate_decision == GateDecision.HALT:
                 hop_checkpoint.status = HopStatus.FAIL
                 hop_checkpoint.error_message = gate_reason
                 # Raise error to stop workflow here
                 raise HopExecutionError(f"HALT decision at HOP-6: {gate_reason}")
            else: # PROCEED
                 hop_checkpoint.status = HopStatus.PASS

            return gate_decision
        except Exception as e: # Catch errors within the decision engine itself
            self.logger.error(f"  ✗ [HOP-6] FAILED during decision logic: {e}", exc_info=False)
            error_reason = f"Error in decision engine: {e}"
            hop_checkpoint = self._create_checkpoint(
                 "HOP-6", "Gate Decision",
                 [ValidationResult("HOP-6_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 {"decision": GateDecision.HALT.value, "reason": error_reason},
                 start_time=hop_start_time, error_message=error_reason,
                 metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            # Ensure workflow halts if decision engine fails
            raise HopExecutionError(f"HOP-6 failed during decision logic: {e}")

    def _execute_hop_7_rendering(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str, thematic_analysis: ThematicAnalysis, job_description: str, jd_url: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Executes HOP-7: Rendering Output Files.
        Passes jd_url to the renderer.
        Returns (file_paths, file_contents)
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7] Rendering Output Files...")
        file_paths = {}
        file_contents = {}
        hop_results = [] # Store validation results from rendering (e.g., AppTracker)
        try:
            # Pass company_name and job_title to FileRenderer constructor
            renderer = FileRenderer(self.master_resume, self, company_name, job_title)
            # render method returns (file_paths, (validation_results, file_contents))
            file_paths, (hop_results, file_contents) = renderer.render(
                staging_buffer, company_name, job_title, thematic_analysis, job_description, jd_url=jd_url # Pass jd_url here
            )

            # Store rendered output for potential use in QA report or final return
            self.rendered_output = {
                'file_paths': file_paths,
                'file_contents': file_contents
            }

            hop_checkpoint = self._create_checkpoint(
                "HOP-7", "File Rendering", hop_results, # Include AppTracker validation results
                {"files_generated": list(file_paths.keys())},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check for critical rendering/validation errors reported in hop_results
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=True) # Allow info/warnings from AppTracker validation

            return file_paths, file_contents
        except Exception as e: # Catch errors during the rendering process itself
            self.logger.error(f"  ✗ [HOP-7] FAILED: {e}", exc_info=False)
            # Ensure results includes the execution error
            exec_error_result = ValidationResult("HOP-7_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))
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

    def _execute_hop_7_5_deduplication(self, staging_buffer: ImmutableStagingBuffer):
        """Executes HOP-7.5: Deduplication Analysis (populates attributes for QA report)."""
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-7.5] Computing Deduplication Metrics...")
        analysis_performed = False # Flag
        try:
            # Ensure dup_detector exists (set in HOP-2)
            if not hasattr(self, 'dup_detector') or self.dup_detector is None:
                 self.logger.warning("  ⚠️ DuplicateDetector not found. Skipping deduplication analysis.")
                 hop_checkpoint = self._create_checkpoint(
                      "HOP-7.5", "Deduplication Analysis",
                      [ValidationResult("DEDUP_SKIP", True, ValidationSeverity.INFO, "DuplicateDetector not initialized.")],
                      {"analysis_skipped": True}, start_time=hop_start_time,
                      metadata={"gemini_api_calls": 0}
                 )
                 # This hop is informational, so PASS even if skipped
                 hop_checkpoint.status = HopStatus.PASS
                 self.hop_checkpoints.append(hop_checkpoint)
                 return # Exit early


            # Proceed with analysis if detector exists
            analysis_performed = self._invoke_deduplication_analysis(staging_buffer)
            if analysis_performed:
                self.logger.info("  ✓ Deduplication analysis complete.")
            else:
                self.logger.warning("  ⚠️ Deduplication analysis incomplete (check logs).")


            # Create checkpoint with summary metrics
            # Ensure data exists before accessing keys
            matrix_max = self.similarity_matrix_data.get('max_similarity', 0.0) if self.similarity_matrix_data else 0.0
            overview_max = max([d.get('max_similarity', 0.0) for d in self.overview_similarity_data if d], default=0.0) if self.overview_similarity_data else 0.0
            exec_max = max([d.get('max_similarity', 0.0) for d in self.executive_summary_similarity_data if d], default=0.0) if self.executive_summary_similarity_data else 0.0

            hop_checkpoint = self._create_checkpoint(
                "HOP-7.5", "Deduplication Analysis", [], # No new validations here
                { # Output is the summary data stored on self
                    "matrix_max_sim": matrix_max,
                    "overview_max_sim": overview_max,
                    "exec_summary_max_sim": exec_max,
                },
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0, "analysis_timestamp": self.dedup_analysis_timestamp}
            )
            # This hop is informational, should generally pass unless the calculation fails
            hop_checkpoint.status = HopStatus.PASS
            self.hop_checkpoints.append(hop_checkpoint)

        except Exception as e: # Catch errors during the similarity calculations
            self.logger.error(f"  ✗ [HOP-7.5] FAILED: {e}", exc_info=False)
            hop_checkpoint = self._create_checkpoint(
                 "HOP-7.5", "Deduplication Analysis",
                 [ValidationResult("HOP-7.5_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))],
                 None, start_time=hop_start_time, error_message=str(e),
                 metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL # Treat calculation failure as hop failure
            self.hop_checkpoints.append(hop_checkpoint)
            # Do not halt workflow, but log the failure

    def _execute_hop_8_qa_report(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, hop5_results: List[ValidationResult]) -> str:
        """
        Executes HOP-8: QA Report Generation.
        Uses final validation results from HOP-5.
        Returns the generated QA report text.
        """
        hop_start_time = datetime.now()
        self.logger.info("\n[HOP-8] Generating QA Report...")
        qa_report_text = "[QA Report Not Generated]" # Default
        hop_results = [] # Store QA generation validation results
        try:
            # Generate report returns (validation_results, report_text, updated_file_contents)
            hop_results, qa_report_text, updated_file_contents = self._generate_qa_report(
                staging_buffer, thematic_analysis, hop5_results # Pass HOP-5 results
            )

            # Update the stored rendered output with the final QA report content
            if self.rendered_output and 'file_contents' in self.rendered_output:
                self.rendered_output['file_contents']['qa_report'] = qa_report_text
            elif self.rendered_output: # Should exist if HOP-7 ran
                 self.rendered_output['file_contents'] = {'qa_report': qa_report_text}
            else: # Fallback
                 self.rendered_output = {'file_contents': {'qa_report': qa_report_text}}

            # Create checkpoint
            hop_checkpoint = self._create_checkpoint(
                "HOP-8", "QA Report Generation", hop_results, # Include QA format validation results
                {"report_length": len(qa_report_text)},
                start_time=hop_start_time,
                metadata={"gemini_api_calls": 0}
            )
            self.hop_checkpoints.append(hop_checkpoint)
            # Check for critical errors during QA report generation/formatting
            self._check_hop_status(hop_checkpoint, allow_warnings=True, check_critical_only=True) # Allow info/warnings, halt on critical
            return qa_report_text
        except Exception as e: # Catch errors during QA report generation logic
            self.logger.error(f"  ✗ [HOP-8] FAILED: {e}", exc_info=False)
            error_reason = f"QA report generation failed: {e}"
            # Add execution error to results
            exec_error_result = ValidationResult("HOP-8_EXECUTION", False, ValidationSeverity.CRITICAL, str(e))
            if not any(vr.rule_id == "HOP-8_EXECUTION" for vr in hop_results):
                 hop_results.append(exec_error_result)

            hop_checkpoint = self._create_checkpoint(
                 "HOP-8", "QA Report Generation", hop_results,
                 {"report_length": 0}, start_time=hop_start_time, error_message=error_reason,
                 metadata={"gemini_api_calls": 0}
            )
            hop_checkpoint.status = HopStatus.FAIL
            self.hop_checkpoints.append(hop_checkpoint)
            # Don't halt the entire workflow, just return error placeholder
            return f"[QA Report Generation Failed: {e}]"


    # --- Main Workflow Execution Method (Updated) ---
    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        jd_url: str = "" # Add jd_url parameter
    ) -> Dict:
        """
        Execute complete multi-hop workflow.
        Returns a dictionary containing status, results, and artifacts.
        """
        workflow_start = datetime.now()
        # Sanitize inputs robustly
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

        # Initialize workflow variables
        thematic_analysis = None
        extracted_data = None
        enriched_scaffold = None
        artist_output = None
        staging_buffer = None
        hop5_results = []
        file_paths = {}
        file_contents = {}
        qa_report_text = "[QA Report Not Generated]"
        gate_decision = GateDecision.PROCEED
        total_api_calls = 0

        try:
            # --- JD Enforcement GATE-0 ---
            self.logger.info("\n[GATE-0] JD Input Validation...")
            jd_validation = self.jd_enforcer.validate_jd_input(job_description, "GATE-0")
            failed_jd_validations = [r for r in jd_validation if not r.passed]
            if failed_jd_validations:
                halt_msg = f"JD Input Validation failed: {failed_jd_validations[0].details}"
                self.logger.error(f"  ✗ {halt_msg}")
                raise HopExecutionError(halt_msg)
            else: self.logger.info("  ✓ JD input validation passed.")

            # --- HOP-0 ---
            thematic_analysis, calls_hop0 = self._execute_hop_0_jd_analysis(job_description)
            total_api_calls += calls_hop0

            # --- JD Enforcement GATE-1 ---
            self.logger.info("\n[GATE-1] JD Parsing Validation...")
            if thematic_analysis:
                # Use asdict for validation check, handle potential errors
                try: parsed_jd_for_validation = asdict(thematic_analysis)
                except Exception as e:
                    self.logger.warning(f"Could not convert ThematicAnalysis to dict for GATE-1: {e}")
                    parsed_jd_for_validation = {} # Use empty dict as fallback
                self.jd_enforcer.validate_jd_parsing(parsed_jd_for_validation, "GATE-1")
            else: # Should have halted in HOP-0 if thematic_analysis is None
                raise HopExecutionError("ThematicAnalysis missing after HOP-0.")

            # --- HOP-1 ---
            extracted_data = self._execute_hop_1_clerk_extraction()

            # --- JD Enforcement GATE-2 ---
            self.logger.info("\n[GATE-2] Thematic Analysis Content Validation...")
            self.jd_enforcer.validate_thematic_analysis(thematic_analysis, "GATE-2") # ThematicAnalysis should exist

            # --- HOP-2 ---
            enriched_scaffold = self._execute_hop_2_enrichment(extracted_data, thematic_analysis)

            # --- JD Enforcement GATE-3 ---
            self.logger.info("\n[GATE-3] Enrichment Content Validation...")
            self.jd_enforcer.validate_enrichment(enriched_scaffold, "GATE-3")

            # --- JD Enforcement GATE-4 ---
            self.logger.info("\n[GATE-4] Artist Input Validation...")
            self.jd_enforcer.validate_artist_inputs(enriched_scaffold, thematic_analysis, "GATE-4")

            # --- HOP-3 ---
            artist_output, calls_hop3 = self._execute_hop_3_artist_generation(
                enriched_scaffold, job_description, thematic_analysis
            )
            total_api_calls += calls_hop3

            # --- HOP-4 & 4.5 ---
            staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)

            # --- HOP-5 ---
            hop5_results = self._execute_hop_5_validation(staging_buffer, thematic_analysis, job_description)

            # --- JD Enforcement GATE-5 ---
            self.logger.info("\n[GATE-5] Pre-flight Buffer JD Validation...")
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")

            # --- HOP-6 ---
            gate_decision = self._execute_hop_6_gate_decision(hop5_results)
            # Workflow halts via exception if decision is HALT

            # --- HOP-7 ---
            file_paths, file_contents = self._execute_hop_7_rendering(
                staging_buffer, company_name, job_title, thematic_analysis, job_description, jd_url=jd_url
            )

            # --- JD Enforcement GATE-7 ---
            self.logger.info("\n[GATE-7] File Output Validation...")
            self.jd_enforcer.validate_file_output(file_paths, "GATE-7")

            # --- HOP-7.5 ---
            self._execute_hop_7_5_deduplication(staging_buffer)

            # --- HOP-8 ---
            qa_report_text = self._execute_hop_8_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            # --- JD Enforcement GATE-8 ---
            self.logger.info("\n[GATE-8] QA Report Content Validation...")
            qa_report_check_data = {"report": qa_report_text} if qa_report_text and "[Failed" not in qa_report_text else {}
            self.jd_enforcer.validate_qa_report(qa_report_check_data, "GATE-8")


            # --- Workflow Complete ---
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()

            coc_ledger = self._build_coc_ledger(
                workflow_start, workflow_end, thematic_analysis, total_api_calls
            )

            self.logger.info("\n" + "=" * 80)
            self.logger.info("WORKFLOW COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"Duration: {duration:.2f}s")
            self.logger.info(f"Gate Decision: {gate_decision.value}") # Should be PROCEED if reached here
            self.logger.info(f"Output Files: {len(file_paths)}")
            self.logger.info(f"Total Gemini API Calls: {total_api_calls}")

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
            self.rendered_output = final_result
            return final_result

        except HopExecutionError as e:
            # Handle controlled halts (validation failures, gate decisions, specific errors)
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW HALTED: {str(e)}")

            # Determine final gate decision and reason
            gate_decision_val = GateDecision.HALT.value
            reason = str(e)
            last_checkpoint = self.hop_checkpoints[-1] if self.hop_checkpoints else None
            if last_checkpoint:
                 # If halted at Gate Decision, use its reason
                 if last_checkpoint.hop_id == "HOP-6" and last_checkpoint.status == HopStatus.FAIL:
                     gate_info = last_checkpoint.metadata or {}
                     reason = gate_info.get("reason", str(e))
                 # Otherwise, use the error message from the failing hop
                 elif last_checkpoint.status == HopStatus.FAIL:
                      reason = last_checkpoint.error_message or str(e)

            # Use validation results stored on self (should be from HOP-5 if it ran)
            halt_validation_results = self.validation_results or []
            # Get potentially partial file contents
            final_file_contents = self.rendered_output.get('file_contents', {}) if self.rendered_output else {}

            # Attempt to generate QA report even on halt
            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, final_file_contents_updated = self._generate_qa_report(
                         staging_buffer, thematic_analysis, halt_validation_results
                     )
                     final_file_contents.update(final_file_contents_updated)
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after halt: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after halt: {qa_e}]"
                      final_file_contents['qa_report'] = qa_report_text
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after halt]"
                 final_file_contents['qa_report'] = qa_report_text

            # Attempt to build CoC ledger
            coc_ledger = {}
            try:
                 coc_ledger = self._build_coc_ledger(
                     workflow_start, workflow_end, thematic_analysis, total_api_calls
                 ) if thematic_analysis else {}
            except Exception as coc_e:
                 self.logger.error(f"Failed to build CoC ledger after halt: {coc_e}")

            final_result = {
                "status": "HALTED",
                "gate_decision": gate_decision_val,
                "reason": reason,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text,
                "coc_ledger": coc_ledger,
                "hash_chain": self.hash_chain,
                "file_contents": final_file_contents,
                "total_api_calls": total_api_calls
            }
            self.rendered_output = final_result
            return final_result

        except Exception as e:
            # Handle unexpected errors
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            self.logger.error(f"\n✗ WORKFLOW FAILED UNEXPECTEDLY: {type(e).__name__}: {str(e)}", exc_info=True)

            # Use any available validation results
            fail_validation_results = self.validation_results or []
            final_file_contents = self.rendered_output.get('file_contents', {}) if self.rendered_output else {}

            # Attempt QA report generation
            if staging_buffer and thematic_analysis:
                 try:
                     _, qa_report_text, final_file_contents_updated = self._generate_qa_report(
                         staging_buffer, thematic_analysis, fail_validation_results
                     )
                     final_file_contents.update(final_file_contents_updated)
                 except Exception as qa_e:
                      self.logger.error(f"  Failed to generate QA report after failure: {qa_e}")
                      qa_report_text = f"[QA Report generation failed after error: {qa_e}]"
                      final_file_contents['qa_report'] = qa_report_text
            else:
                 qa_report_text = "[QA Report could not be generated - insufficient data after failure]"
                 final_file_contents['qa_report'] = qa_report_text

            # Attempt CoC ledger
            coc_ledger = {}
            try:
                 coc_ledger = self._build_coc_ledger(
                      workflow_start, workflow_end, thematic_analysis, total_api_calls
                 ) if thematic_analysis else {}
            except Exception as coc_e:
                  self.logger.error(f"Failed to build CoC ledger after failure: {coc_e}")

            final_result = {
                "status": "FAILED",
                "error": f"{type(e).__name__}: {str(e)}",
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "qa_report": qa_report_text,
                "coc_ledger": coc_ledger,
                "hash_chain": self.hash_chain,
                "file_contents": final_file_contents,
                "total_api_calls": total_api_calls
            }
            self.rendered_output = final_result
            return final_result


    # --- Helper Methods ---

    def _create_jd_analyzer(self) -> EnhancedJobDescriptionAnalyzer:
        """Creates the HOP-0 JD Analyzer instance."""
        api_key = os.environ.get("GEMINI_API_KEY")
        rag_config = None
        try: # Ensure RAGConfig exists and handle potential NameError
             if 'RAGConfig' in globals():
                  rag_config = RAGConfig()
             else:
                  self.logger.warning("RAGConfig class not found, using default settings for JD Analyzer.")
        except NameError:
             self.logger.warning("RAGConfig class not found, using default settings for JD Analyzer.")
        except Exception as e:
             self.logger.error(f"Error initializing RAGConfig: {e}")

        # Ensure MASTER_RESUME_JSON is passed correctly
        return EnhancedJobDescriptionAnalyzer(self.master_resume, enable_web_search=True, api_key=api_key, config=rag_config)


    def _create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        validation_results: List[ValidationResult],
        output_data: Any, # Can be summary dict or complex object
        start_time: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> HopCheckpoint:
        """Creates a HopCheckpoint object, calculates duration and hash."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Determine status based on errors and validation results
        status = HopStatus.PASS # Default
        if error_message:
            status = HopStatus.FAIL
        elif validation_results:
            # Check for CRITICAL failures first
            if any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in validation_results):
                status = HopStatus.FAIL
            # Then check for HIGH failures
            elif any(not vr.passed and vr.severity == ValidationSeverity.HIGH for vr in validation_results):
                 status = HopStatus.FAIL # Treat HIGH as FAIL for hop status
            # Then check for any other failures (MEDIUM, LOW) -> WARNING
            elif any(not vr.passed for vr in validation_results):
                 status = HopStatus.WARNING

        # Calculate output hash robustly
        output_hash = None
        if output_data is not None:
            try:
                # Robust default serializer
                def default_serializer(o):
                    if isinstance(o, (datetime, ThematicAnalysis, HopCheckpoint, ValidationResult, Enum)): # Add Enum
                         try: return asdict(o) if not isinstance(o, Enum) else o.value # Use value for Enums
                         except Exception: return str(o)
                    elif isinstance(o, ImmutableStagingBuffer): return o.data # Serialize buffer data
                    elif hasattr(o, '__dict__'): return o.__dict__ # Generic object
                    try: json.dumps(o); return o # Check if directly serializable
                    except TypeError: return f"__Unserializable:{type(o).__name__}__"

                # Convert complex types if needed before dumping
                serializable_output = output_data
                if isinstance(output_data, ImmutableStagingBuffer): serializable_output = output_data.data
                elif isinstance(output_data, ThematicAnalysis): serializable_output = asdict(output_data)

                output_str = json.dumps(serializable_output, sort_keys=True, separators=(',', ':'), default=default_serializer)
                output_hash = hashlib.sha256(output_str.encode('utf-8')).hexdigest()[:16]

            except (TypeError, Exception) as e:
                self.logger.warning(f"Could not calculate output hash for {hop_id} due to serialization error: {e}")
                output_hash = f"ErrorHashing:_{type(e).__name__}" # Underscore prefix

        # Ensure metadata is serializable
        final_metadata = copy.deepcopy(metadata) or {}
        final_metadata["duration_seconds"] = round(duration, 3)
        if "gemini_api_calls" in final_metadata:
             final_metadata["gemini_api_calls"] = int(final_metadata["gemini_api_calls"])
        # Serialize counts if present
        if "sanitization_counts" in final_metadata:
             final_metadata["sanitization_counts"] = dict(final_metadata["sanitization_counts"]) # Ensure it's a plain dict


        # Create checkpoint
        # Make a deep copy of validation results to prevent modification issues
        copied_validation_results = []
        for vr in validation_results:
             try:
                  # Attempt deepcopy, fallback to shallow or string representation
                  copied_validation_results.append(copy.deepcopy(vr))
             except Exception as copy_e:
                  logging.warning(f"Could not deepcopy ValidationResult {vr.rule_id}: {copy_e}")
                  # Fallback: Create a new object with basic info
                  copied_validation_results.append(ValidationResult(
                       rule_id=vr.rule_id, passed=vr.passed, severity=vr.severity,
                       message=str(vr.message), # Convert potential lambda to string
                       details={"error": "Copy failed"}
                  ))


        checkpoint = HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            status=status,
            timestamp_start=start_time.isoformat(),
            timestamp_end=end_time.isoformat(),
            output_hash=output_hash,
            validation_results=copied_validation_results, # Use copied list
            metadata=final_metadata,
            error_message=error_message
        )

        # Calculate and add chain hash
        # Use output_hash or a placeholder if hashing failed
        hash_for_chain = output_hash if output_hash and not output_hash.startswith("ErrorHashing") else f"{hop_id}_Output"
        if self.hash_chain:
            prev_hash = self.hash_chain[-1]
            chain_input = f"{prev_hash}|{hop_id}|{status.value}|{hash_for_chain}|{checkpoint.timestamp_end}"
            current_chain_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()[:16]
        else: # First hop
            current_chain_hash = hash_for_chain or f"{hop_id}_START_{status.value}"

        self.hash_chain.append(current_chain_hash)
        checkpoint.metadata["chain_hash"] = current_chain_hash

        return checkpoint

    def _check_hop_status(self, checkpoint: HopCheckpoint, allow_warnings: bool = False, check_critical_only: bool = False):
        """
        Checks hop status and raises HopExecutionError if workflow should halt.
        Logs details about failures or warnings.
        """
        effective_status = checkpoint.status
        halt_severity = ValidationSeverity.HIGH # Default halt level
        halt_reason_prefix = "HIGH/CRITICAL"

        if check_critical_only:
             halt_severity = ValidationSeverity.CRITICAL
             halt_reason_prefix = "CRITICAL"
             # If status is FAIL but no CRITICAL errors, treat as non-halting
             if checkpoint.status == HopStatus.FAIL and not any(not vr.passed and vr.severity == ValidationSeverity.CRITICAL for vr in checkpoint.validation_results):
                  effective_status = HopStatus.PASS # Allow continuation

        # Check for HALT condition
        if effective_status == HopStatus.FAIL:
            # Find the highest severity failure causing the halt
            failed_results = sorted(
                [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity.value >= halt_severity.value],
                key=lambda x: x.severity.value, reverse=True
            )
            primary_failure = failed_results[0] if failed_results else None

            # Construct the reason message
            reason_msg = "Unknown failure"
            if primary_failure:
                try: # Attempt to format message using details (which might be complex)
                    # Create a simple context dict for the lambda if needed
                    simple_context = defaultdict(lambda: 'N/A', **(primary_failure.details or {}))
                    reason_msg = primary_failure.message(simple_context) if callable(primary_failure.message) else str(primary_failure.message)
                except Exception as msg_e:
                    reason_msg = f"{str(primary_failure.message)} (Msg format err: {msg_e})" # Include original msg str
                reason = f"{primary_failure.rule_id}: {reason_msg}"
            else:
                 reason = checkpoint.error_message or "Unknown hop failure"


            error_msg = f"[{checkpoint.hop_id}] FAILED ({halt_reason_prefix}) - Halting workflow. Reason: {reason}"
            self.logger.error(f"  ✗ {error_msg}")

            # Log first few specific validation failures for context
            failures_to_log = failed_results[:3]
            if failures_to_log: self.logger.error("    Specific Failures:")
            for vr in failures_to_log:
                 try:
                      simple_context = defaultdict(lambda: 'N/A', **(vr.details or {}))
                      msg = vr.message(simple_context) if callable(vr.message) else str(vr.message)
                 except Exception: msg = str(vr.message)
                 self.logger.error(f"      - [{vr.severity.name}] {vr.rule_id}: {msg}")

            raise HopExecutionError(f"{checkpoint.hop_id} failed validation ({halt_reason_prefix}). Halting.")

        # Handle WARNING status
        elif checkpoint.status == HopStatus.WARNING:
            warnings = [vr for vr in checkpoint.validation_results if not vr.passed and vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            self.logger.warning(f"  ⚠️ [{checkpoint.hop_id}] completed with {len(warnings)} warnings.")
            if not allow_warnings:
                 error_msg = f"[{checkpoint.hop_id}] FAILED - Warnings detected but not allowed. Halting."
                 self.logger.error(f"  ✗ {error_msg}")
                 raise HopExecutionError(error_msg)
            else:
                 # Log first few warnings
                 for vr in warnings[:2]:
                     try:
                          simple_context = defaultdict(lambda: 'N/A', **(vr.details or {}))
                          msg = vr.message(simple_context) if callable(vr.message) else str(vr.message)
                     except Exception: msg = str(vr.message)
                     self.logger.warning(f"    - [{vr.severity.name}] {vr.rule_id}: {msg}")
                 self.logger.info(f"  ✓ {checkpoint.hop_id} completed (with warnings).")

        # Handle PASS status
        elif checkpoint.status == HopStatus.PASS:
            self.logger.info(f"  ✓ {checkpoint.hop_id} completed successfully.")
        # Handle unexpected status
        else:
             self.logger.error(f"  ? Unknown status encountered for {checkpoint.hop_id}: {checkpoint.status}")


    def _build_coc_ledger(
        self,
        workflow_start: datetime,
        workflow_end: datetime,
        thematic_analysis: Optional[ThematicAnalysis],
        total_api_calls: int # Pass total API calls
    ) -> Dict:
        """Builds the Chain of Custody (CoC) ledger dictionary."""
        # Generate Workflow ID
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', 'UnknownCandidate')}".encode('utf-8')
        ).hexdigest()[:16]

        # Extract RAG Metadata
        rag_metadata = {}
        if thematic_analysis:
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            # Safely extract attributes from thematic_analysis and comp_intel
            primary_theme_name = getattr(getattr(thematic_analysis, 'primary_theme', {}), 'name', 'N/A')
            role_archetype = getattr(getattr(thematic_analysis, 'role_classification', {}), 'role_archetype', 'N/A')
            comp_intel_dict = asdict(comp_intel) if comp_intel and hasattr(comp_intel, '__dataclass_fields__') else {}

            rag_metadata = {
                "signal_quality": getattr(thematic_analysis, 'signal_quality_score', 0.0),
                "retrieval_method": getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN'),
                "primary_theme": primary_theme_name,
                "role_archetype": role_archetype,
                "peer_jds_analyzed": comp_intel_dict.get('peer_jds_analyzed_count', 0),
                "differentiator_keywords_top5": comp_intel_dict.get('differentiator_keywords', [])[:5],
                "jd_input_hash": self.jd_enforcer.jd_hash if hasattr(self, 'jd_enforcer') else None
            }

        # Determine Overall Status
        overall_status = HopStatus.PASS.value # Assume PASS
        if any(hc.status == HopStatus.FAIL for hc in self.hop_checkpoints):
             overall_status = HopStatus.FAIL.value
        elif any(hc.status == HopStatus.WARNING for hc in self.hop_checkpoints):
             overall_status = HopStatus.WARNING.value
        elif self.hop_checkpoints: # Use final hop status if no failures/warnings found yet
             overall_status = self.hop_checkpoints[-1].status.value


        # Serialize Hops Executed
        hops_executed_list = []
        for hc in self.hop_checkpoints:
             try:
                 # Convert HopCheckpoint dataclass to dict, handling potential non-serializable fields
                 checkpoint_dict = asdict(hc)
                 # Ensure enums are converted to values/names
                 checkpoint_dict['status'] = hc.status.value
                 for vr in checkpoint_dict.get('validation_results', []):
                      if isinstance(vr.get('severity'), Enum):
                           vr['severity'] = vr['severity'].name # Use name for severity enum
                 hops_executed_list.append(checkpoint_dict)
             except Exception as e:
                 self.logger.warning(f"Could not fully serialize checkpoint {hc.hop_id}: {e}")
                 # Append a simplified representation
                 hops_executed_list.append({
                     "hop_id": hc.hop_id, "hop_name": hc.hop_name, "status": hc.status.value,
                     "error": f"Serialization partial failure: {e}",
                     "metadata": {"duration_seconds": hc.metadata.get("duration_seconds", -1)} # Include duration if possible
                 })

        # Build Final Ledger Dictionary
        return {
            "workflow_id": workflow_id,
            "engine_version": f"v{__version__}", # Assumes __version__ is defined
            "architecture_version": "Job_Workflow_v13.40_QA_Refactor", # Update Arch Version
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
            "overall_status": overall_status,
            "total_gemini_api_calls": total_api_calls
        }


    # --- START REFACTORED QA Report Generation Method ---
    def _generate_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult] # Use final validation results from HOP-5
    ) -> Tuple[List[ValidationResult], str, Dict[str, str]]:
        """
        Generates the full QA report by calling individual section builder methods.
        Returns validation results specific to QA generation, the report text,
        and the updated file contents dictionary including the QA report.
        """
        qa_generation_validation_results = [] # Store results specific to QA generation/formatting
        report_lines = [
            f"RESUME QA REPORT (Engine: v{__version__}, Arch: Job_Workflow_v13.40_QA_Refactor)", # Updated Header
            f"Generated: {datetime.now().isoformat()}",
        ]
        self.logger.info("  Building QA Report Sections...")

        # --- Arguments for Builder Methods ---
        current_file_contents = (self.rendered_output.get('file_contents', {})
                                 if hasattr(self, 'rendered_output') and self.rendered_output
                                 else {})
        # Ensure staging buffer is passed if available, otherwise use an empty one? Or should fail earlier?
        buffer_to_use = staging_buffer if staging_buffer else ImmutableStagingBuffer()
        theme_to_use = thematic_analysis if thematic_analysis else ThematicAnalysis() # Use empty if missing

        available_args = {
            "staging_buffer": buffer_to_use,
            "thematic_analysis": theme_to_use,
            "validation_results": validation_results, # Use the final HOP-5 results
            "file_contents": current_file_contents # Pass current file contents for Section 13
        }

        # --- Build Sections Using Config ---
        for i, section_config in enumerate(self.QA_REPORT_SECTIONS, 1):
            method_name = section_config["method"]
            arg_names = section_config["args"]
            self.logger.debug(f"    Building QA Section {i}: {method_name}")
            try:
                builder_method = getattr(self, method_name)
                # Prepare arguments dynamically
                call_args = {name: available_args[name] for name in arg_names if name in available_args}
                if len(call_args) != len(arg_names):
                    missing_args = set(arg_names) - set(call_args.keys())
                    # Log warning but attempt to continue if possible
                    self.logger.warning(f"Missing arguments {missing_args} for method '{method_name}', section may be incomplete.")
                    # raise KeyError(f"Missing required arguments {missing_args}") # Optionally raise error

                section_lines = builder_method(**call_args)
                report_lines.extend(section_lines)
            except (AttributeError, KeyError, Exception) as e:
                error_message = f"Error building QA section {i} ('{method_name}'): {type(e).__name__} - {e}"
                self.logger.error(error_message, exc_info=False) # exc_info=False for brevity
                report_lines.append(f"\n--- ERROR GENERATING SECTION {i}: {error_message} ---\n")
                qa_generation_validation_results.append(ValidationResult(
                    rule_id=f"QA_SECTION_{i}_ERROR", passed=False, severity=ValidationSeverity.HIGH,
                    message=error_message
                ))

        # --- Finalize Report Text ---
        qa_report_text = "\n".join(report_lines).strip()
        self.logger.info(f"  ✓ QA Report sections built ({len(qa_report_text.splitlines())} lines).")

        # --- Validate Formatting (Ensure Tables are Pre-formatted) ---
        self.logger.info("  Validating QA Report table formatting...")
        formatting_validation_result = self._validate_qa_report_formatting(qa_report_text)
        qa_generation_validation_results.append(formatting_validation_result)
        if not formatting_validation_result.passed:
             self.logger.warning(f"  ⚠️ QA Report formatting validation failed: {formatting_validation_result.message}")
        else:
             self.logger.info("  ✓ QA Report table formatting validation passed.")


        # Add a final overall result for the generation process itself
        overall_qa_gen_status = all(vr.passed for vr in qa_generation_validation_results)
        qa_generation_validation_results.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION_OVERALL",
            passed=overall_qa_gen_status,
            severity=ValidationSeverity.INFO if overall_qa_gen_status else ValidationSeverity.HIGH,
            message="QA Report generated successfully." if overall_qa_gen_status else "QA Report generated with formatting/section errors."
        ))

        # --- Prepare Final File Contents ---
        final_file_contents = available_args["file_contents"]
        final_file_contents['qa_report'] = qa_report_text # Update/add the QA report content

        return qa_generation_validation_results, qa_report_text, final_file_contents
    # --- END REFACTORED QA Report Generation Method ---


    # --- START REFACTORED QA Report Section Helper Methods (Summary Format) ---

    def _build_qa_section_1_signal_quality(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 1: Signal Quality & Target Alignment."""
        lines = ["", "1. SIGNAL QUALITY & TARGET ALIGNMENT", ""]
        lines.append("Summarizes RAG analysis quality and alignment of generated content to JD keywords.")
        lines.append("")

        # RAG Signal Quality
        rag_quality = getattr(thematic_analysis, 'signal_quality_score', 0.0)
        retrieval_method = getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN')
        rag_status = "✅ STRONG" if rag_quality >= 0.7 else "⚠️ MODERATE" if rag_quality >= 0.4 else "❌ WEAK"
        lines.append(f"   RAG Analysis Quality: {rag_status} ({rag_quality:.1%}) via {retrieval_method}")

        # JD Keyword Integration
        jd_rule = next((vr for vr in validation_results if vr.rule_id == "VG_JD_KEYWORD_RANGE"), None)
        kw_status = "❌ FAIL"
        kw_details = "N/A"
        if jd_rule:
            kw_status = "✅ PASS" if jd_rule.passed else "❌ FAIL"
            kw_min = jd_rule.details.get('min', '?')
            kw_max = jd_rule.details.get('max', '?')
            kw_found = jd_rule.details.get('found', '?')
            kw_details = f"Found {kw_found} (Tgt: {kw_min}-{kw_max})"
        lines.append(f"   JD Keyword Integration: {kw_status} ({kw_details})")

        # Per-Section Signal Scores (ASCII Bar Chart)
        lines.append("\n   Per-Section Signal Score Alignment (vs JD):")
        total_score = 0.0
        total_weight = 0.0
        final_temps = {}
        artist_checkpoint = next((cp for cp in self.hop_checkpoints if cp.hop_id == 'HOP-3'), None)
        if artist_checkpoint and isinstance(artist_checkpoint.metadata.get('final_temperatures'), dict):
             final_temps = artist_checkpoint.metadata['final_temperatures']

        # Use updated SECTION_SIGNAL_TARGETS_CONFIG for K0-K11
        for label, (section_enum, target_min, target_max, weight, _) in PreFlightValidator.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = staging_buffer.get(section_enum.value)
            score = 0.0
            if content: score = calculate_signal_score(content, thematic_analysis)
            # Find temperature used for this section
            temp_used = final_temps.get(section_enum.name, 'N/A') # Use enum name to match dict key
            lines.append(self._format_ascii_bar_chart(label, score, target_min, target_max, temp_used))
            total_score += score * weight
            total_weight += weight

        # Weighted Average Score
        avg_score = total_score / total_weight if total_weight > 0 else 0.0
        # Use simple avg temperature if available
        avg_temp = sum(t for t in final_temps.values() if isinstance(t, float)) / len(final_temps) if final_temps else 'N/A'
        lines.append("-" * 80)
        lines.append(self._format_ascii_bar_chart("Weighted Average", avg_score, 0.70, 0.90, avg_temp, is_summary=True))
        lines.append("-" * 80)

        # Signal Score Failures
        signal_fail_rule = next((vr for vr in validation_results if vr.rule_id == "VG_PER_SECTION_SIGNAL_SCORE"), None)
        if signal_fail_rule and not signal_fail_rule.passed:
             lines.append("\n**Signal Score Failures:**")
             try: fail_msg = signal_fail_rule.message(signal_fail_rule.details) if callable(signal_fail_rule.message) else signal_fail_rule.message
             except Exception: fail_msg = str(signal_fail_rule.message)
             lines.append(f"  - {fail_msg}")

        return lines


    # REFACTORED Section 2 Method
    def _build_qa_section_2_signal_flow_map(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        """Builds QA Section 2: Signal Flow Map Summary."""
        lines = ["", "2. SIGNAL FLOW MAP SUMMARY (RAG Consumption)", ""]
        lines.append("Checks if key RAG intelligence signals (Theme, Differentiators, etc.) were used in generation based on validation rules.")
        lines.append("")
        lines.append("```markdown")
        signals_checked_count = 0
        signals_missing = []
        rules_to_check = [ # List relevant rules that confirm signal consumption
            "VG_K1_DIFFERENTIATOR_RANGE",
            "COVER_LETTER_NARRATIVE_INTEGRITY",
            "VG_AUTHENTICITY_SIGNAL_CHECK",
            "NARRATIVE_MINING_PRESENCE"
        ]
        for rule_id in rules_to_check:
            result = next((vr for vr in self.validation_results if vr.rule_id == rule_id), None)
            if result:
                signals_checked_count += 1
                if not result.passed:
                    try: msg = result.message(result.details) if callable(result.message) else result.message
                    except Exception: msg = str(result.message)
                    signals_missing.append(f"{rule_id}: {msg.split('.')[0]}") # Shorten message
            else:
                 logging.debug(f"QA Section 2: Rule {rule_id} not found.")

        overall_status = "✅ PASS" if not signals_missing else "❌ FAIL"
        details = f"{signals_checked_count} signal consumption checks performed."
        headers = ["Check Area", "Status", "Details"]
        rows = [["RAG Signal Consumption", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if signals_missing:
            lines.append("\n**Signal Consumption Failures:**")
            for failure in signals_missing: lines.append(f"  - {failure}")
        return lines

    # REFACTORED Section 3 Method
    def _build_qa_section_3_hop_summary(self) -> List[str]:
        """Builds QA Section 3: Hop Execution Summary."""
        lines = ["", "3. HOP EXECUTION SUMMARY", ""]
        lines.append("Summarizes the status of each workflow step (hop).")
        lines.append("")
        lines.append("```markdown")
        failed_hops_details = []
        warning_hops_details = []
        hops_run = len(self.hop_checkpoints)
        hops_passed = 0
        for hop in self.hop_checkpoints:
            if hop.status == HopStatus.FAIL:
                failed_hops_details.append(f"{hop.hop_id}: {hop.error_message or 'Unknown error'}")
            elif hop.status == HopStatus.WARNING:
                warning_detail = "Warnings present"
                warn_results = [vr for vr in hop.validation_results if not vr.passed and vr.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
                if warn_results:
                     try: msg = warn_results[0].message(warn_results[0].details) if callable(warn_results[0].message) else warn_results[0].message
                     except Exception: msg = str(warn_results[0].message)
                     warning_detail = f"{warn_results[0].rule_id}: {msg.split('.')[0]}"
                warning_hops_details.append(f"{hop.hop_id}: {warning_detail}")
                hops_passed += 1 # Warnings count as completed for this summary
            elif hop.status == HopStatus.PASS: hops_passed += 1
        overall_status = "✅ PASS" if not failed_hops_details and not warning_hops_details else \
                         "❌ FAIL" if failed_hops_details else "⚠️ WARN"
        details = f"{hops_passed}/{hops_run} hops completed." + \
                  (f" {len(failed_hops_details)} failed." if failed_hops_details else "") + \
                  (f" {len(warning_hops_details)} with warnings." if warning_hops_details else "")
        headers = ["Check Area", "Status", "Details"]
        rows = [["Workflow Hop Execution", overall_status, details.strip()]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failed_hops_details:
            lines.append("\n**Failed Hops:**"); lines.extend([f"  - {f}" for f in failed_hops_details])
        if warning_hops_details:
             lines.append("\n**Hops with Warnings:**"); lines.extend([f"  - {w}" for w in warning_hops_details])
        return lines

    # REFACTORED Section 4 Method
    def _build_qa_section_4_word_count_distribution(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 4: Word Count & Distribution Summary."""
        lines = ["", "4. WORD COUNT & DISTRIBUTION SUMMARY", ""]
        lines.append("Checks overall word count, key section constraints, and experience distribution.")
        lines.append("")
        lines.append("```markdown")
        rules_to_check = [ # Updated rules for K0-K11
            "VG_TOTAL_WORD_COUNT", "VG_HEADLINE_WORD_COUNT", "VG_WORD_COUNT_K1",
            "VG_SENTENCE_COUNT_K1",
            "VG_WORD_COUNT_K2_OVERVIEW", "VG_SENTENCE_COUNT_K2_OVERVIEW", # K.2 Unify
            "VG_WORD_COUNT_K3_OVERVIEW", "VG_SENTENCE_COUNT_K3_OVERVIEW", # K.3 IBM
            "VG_NARRATIVE_WORD_COUNT_K4", "VG_NARRATIVE_SENTENCE_COUNT_K4", # K.4 TraderSense
            "VG_NARRATIVE_WORD_COUNT_K5", "VG_NARRATIVE_SENTENCE_COUNT_K5", # K.5 EY
            "VG_NARRATIVE_WORD_COUNT_K6", "VG_NARRATIVE_SENTENCE_COUNT_K6", # K.6 Early Career
            "WORD_DISTRIBUTION_UNIFY_IBM", "UNIFY_IBM_RATIO",
            "COVER_LETTER_STRUCTURE", # Checks paragraph word counts
        ]
        failures = []
        checks_run = 0
        checks_passed = 0
        for rule_id in rules_to_check:
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
            if result:
                checks_run += 1
                if result.passed: checks_passed += 1
                else:
                    try: msg = result.message(result.details) if callable(result.message) else result.message
                    except Exception: msg = str(result.message)
                    short_msg = msg.split("(")[0].strip()
                    failures.append(f"{rule_id}: {short_msg}")
        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No checks found."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Word Count & Distribution", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # REFACTORED Section 5 Method
    def _build_qa_section_5_provenance(self, staging_buffer: ImmutableStagingBuffer) -> List[str]:
        """Builds QA Section 5: Bullet Provenance & Word Count Summary."""
        lines = ["", "5. BULLET PROVENANCE & WORD COUNT SUMMARY", ""]
        lines.append("Checks bullet origin (V/C/S) counts and individual bullet word counts against targets.")
        lines.append("")
        lines.append("```markdown")
        # Reuse validation rule results if available
        prov_result = next((vr for vr in self.validation_results if vr.rule_id == "VG_PROVENANCE_SPLIT_CHECK"), None)
        wc_result = next((vr for vr in self.validation_results if vr.rule_id == "VG_BULLET_WORD_COUNT_RANGE"), None)
        provenance_failures = []
        wc_failures = []
        prov_status = "⚠️ WARN"; wc_status = "⚠️ WARN" # Default if rules not found

        if prov_result:
            prov_status = "✅ PASS" if prov_result.passed else "❌ FAIL"
            if not prov_result.passed:
                try: provenance_failures.append(prov_result.message(prov_result.details) if callable(prov_result.message) else prov_result.message)
                except Exception: provenance_failures.append(str(prov_result.message))
        if wc_result:
             wc_status = "✅ PASS" if wc_result.passed else "❌ FAIL"
             if not wc_result.passed:
                 try: wc_failures.append(wc_result.message(wc_result.details) if callable(wc_result.message) else wc_result.message)
                 except Exception: wc_failures.append(str(wc_result.message))

        overall_status = "✅ PASS" if prov_status == "✅ PASS" and wc_status == "✅ PASS" else "❌ FAIL"
        details = f"Prov: {prov_status}, WC: {wc_status}"

        headers = ["Check Area", "Status", "Details"]
        rows = [["Bullet Provenance & WC", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if provenance_failures:
            lines.append("\n**Provenance Failures:**"); lines.extend([f"  - {f}" for f in provenance_failures])
        if wc_failures:
            lines.append("\n**Word Count Failures:**"); lines.extend([f"  - {f}" for f in wc_failures])
        return lines

    # REFACTORED Section 6 Method
    def _build_qa_section_6_authenticity(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 6: Content Authenticity & Style Check Summary."""
        lines = ["", "6. CONTENT AUTHENTICITY & STYLE CHECK SUMMARY", ""]
        lines.append("Checks for hallucinations, use of authenticity signals, banned intro phrases, and forbidden verbs.")
        lines.append("")
        lines.append("```markdown")
        rules_to_check = [
            "HALLUCINATION_CHECKS", # Placeholder
            "VG_AUTHENTICITY_SIGNAL_CHECK",
            "VG_NO_INTRO_PHRASES",
            "VG_FORBIDDEN_VERBS"
        ]
        failures = []
        checks_passed = 0
        checks_run = 0

        # Hallucination check (using combined logic)
        hallucination_failures = [vr for hop in self.hop_checkpoints for vr in hop.validation_results if "HALLUCINATION" in vr.rule_id and not vr.passed]
        hallucination_pass_check = next((vr for hop in self.hop_checkpoints for vr in hop.validation_results if vr.rule_id == "HALLUCINATION_CHECK"), None)
        if hallucination_pass_check or hallucination_failures:
             checks_run += 1
             if hallucination_failures:
                 fail_msg = f"Hallucinations: Found {len(hallucination_failures)} issues (e.g., {hallucination_failures[0].rule_id})"
                 failures.append(fail_msg)
             else: checks_passed += 1

        # Check other rules
        for rule_id in rules_to_check:
            if "HALLUCINATION" in rule_id: continue
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
            if result:
                checks_run += 1
                if result.passed: checks_passed += 1
                else:
                    try: msg = result.message(result.details) if callable(result.message) else result.message
                    except Exception: msg = str(result.message)
                    failures.append(f"{rule_id}: {msg.split('.')[0]}") # Shorten

        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No checks found."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Authenticity & Style", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # REFACTORED Section 7 Method
    def _build_qa_section_7_prod_readiness(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 7: Production Readiness Summary."""
        lines = ["", "7. PRODUCTION READINESS SUMMARY", ""]
        lines.append("Checks if any CRITICAL or HIGH severity failures occurred during final validation (HOP-5).")
        lines.append("")
        lines.append("```markdown")
        critical_failures = [vr for vr in validation_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
        high_failures = [vr for vr in validation_results if not vr.passed and vr.severity == ValidationSeverity.HIGH]
        prod_ready = not critical_failures and not high_failures
        overall_status = "✅ PASS" if prod_ready else "❌ FAIL"
        details = f"{len(critical_failures)} Critical, {len(high_failures)} High failures found." if not prod_ready else "No Critical or High failures."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Production Readiness", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if not prod_ready:
            lines.append("\n**Blocking Failures (from HOP-5):**")
            fail_map = {"Critical": critical_failures, "High": high_failures}
            for severity, fails in fail_map.items():
                 if fails:
                     lines.append(f"  *{severity}:*")
                     for f in fails[:2]: # Limit details
                         try: msg = f.message(f.details) if callable(f.message) else f.message
                         except Exception: msg = str(f.message)
                         lines.append(f"    - {f.rule_id}: {msg.split('.')[0]}")
                     if len(fails) > 2: lines.append(f"    - ... ({len(fails) - 2} more)")
        return lines

    # REFACTORED Section 8 Method
    def _build_qa_section_8_pairwise_similarity(self) -> List[str]:
        """Builds QA Section 8: Content Similarity Summary."""
        lines = ["", "8. CONTENT SIMILARITY SUMMARY (Deduplication & Overlap)", ""]
        lines.append("Summarizes checks for strict duplicates and excessive overlap between sections.")
        lines.append("")
        lines.append("```markdown")
        failures = []
        checks_run = 0
        checks_passed = 0

        # Strict Duplicates
        if self.similarity_matrix_data:
            checks_run += 1
            duplicates_count = len(self.similarity_matrix_data.get('duplicates_found', []))
            if duplicates_count == 0: checks_passed += 1
            else: failures.append(f"Strict Duplicates (>=0.90): Found {duplicates_count}")
        else: failures.append("Strict Duplicates: Analysis data missing (WARN)")

        # Overview vs. Bullet
        if self.overview_similarity_data is not None:
            checks_run += 1
            # Filter results for sections where the check applies (e.g., exclude K2, K3 overviews themselves)
            # This logic might need refinement based on exact sections stored in self.overview_similarity_data
            relevant_data = [r for r in self.overview_similarity_data if r.get("section") not in ["K.2_Unify_Overview", "K.3_IBM_Overview"]] # Example filter
            violations = sum(len(r.get('threshold_violations',[])) for r in relevant_data)
            if violations == 0: checks_passed += 1
            else: failures.append(f"Overview/Bullet Overlap (>=0.60): Found {violations}")
        else: failures.append("Overview/Bullet Overlap: Analysis data missing (WARN)")


        # Exec Summary vs. Section
        if self.executive_summary_similarity_data is not None:
            checks_run += 1
            threshold = 0.70
            violations_count = sum(1 for r in self.executive_summary_similarity_data if r.get('max_similarity', 0.0) >= threshold)
            if violations_count == 0: checks_passed += 1
            else: failures.append(f"Exec Summary Overlap (>=0.70): Found {violations_count}")
        else: failures.append("Exec Summary Overlap: Analysis data missing (WARN)")

        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        failure_ids = [f.split(':')[0].strip() for f in failures]
        details = f"{checks_passed}/{checks_run} checks passed." if overall_status == "✅ PASS" else f"Failures in: {', '.join(failure_ids)}" if failures else "Analysis incomplete."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Content Similarity", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # REFACTORED Section 9 Method
    def _build_qa_section_9_pipeline_health(self) -> List[str]:
        """Builds QA Section 9: Pipeline Health Summary (API Calls)."""
        lines = ["", "9. PIPELINE HEALTH SUMMARY (Resource Consumption)", ""]
        lines.append("Summarizes API calls made during the workflow.")
        lines.append("")
        lines.append("```markdown")
        total_gemini_calls = sum(hop.metadata.get('gemini_api_calls', 0) for hop in self.hop_checkpoints)
        hops_with_calls = [{'id': hop.hop_id, 'calls': hop.metadata.get('gemini_api_calls', 0)} for hop in self.hop_checkpoints if hop.metadata.get('gemini_api_calls', 0) > 0]
        status = "✅ INFO"
        details = f"Total Gemini API Calls: {total_gemini_calls}"
        headers = ["Check Area", "Status", "Details"]
        rows = [["API Consumption", status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if hops_with_calls:
            lines.append("\n**Calls per Hop:**"); lines.extend([f"  - {h['id']}: {h['calls']}" for h in hops_with_calls])
        return lines

    # REFACTORED Section 10 Method
    def _build_qa_section_10_structural(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 10: Structural Validation Summary."""
        lines = ["", "10. STRUCTURAL VALIDATION SUMMARY (Content Presence)", ""]
        lines.append("Checks if all required resume/cover letter sections are present and non-empty.")
        lines.append("")
        lines.append("```markdown")
        struct_rule_ids_prefix = "STRUCTURE_"
        struct_rule_ids_specific = ["VG_COVER_LETTER_SIGNATURE_VALID"] # Keep signature check
        failures = []
        checks_run = 0
        checks_passed = 0
        for vr in validation_results:
             if vr.rule_id.startswith(struct_rule_ids_prefix) or vr.rule_id in struct_rule_ids_specific:
                 checks_run += 1
                 if vr.passed: checks_passed += 1
                 else:
                     try: msg = vr.message(vr.details) if callable(vr.message) else vr.message
                     except Exception: msg = str(vr.message)
                     failures.append(f"{vr.rule_id}: {msg}")
        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No structure checks found."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Content Structure Presence", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # REFACTORED Section 11 Method
    def _build_qa_section_11_cover_letter(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds QA Section 11: Cover Letter QA Summary."""
        lines = ["", "11. COVER LETTER QA SUMMARY", ""]
        lines.append("Checks specific rules related to cover letter content and structure.")
        lines.append("")
        lines.append("```markdown")
        cl_rule_ids = [ # Use K.11 rules
            "VG_COVER_LETTER_SIGNATURE_VALID", "VG_COVER_LETTER_FULL_STRUCTURE",
            "VG_COVER_LETTER_RELEVANCE_RANGE", "COVER_LETTER_NARRATIVE_INTEGRITY",
            "COVER_LETTER_FALLBACK_DETECTED", "COVER_LETTER_STRUCTURE",
            "STRUCTURE_K11_COVER_LETTER_PRESENT" # Use K.11 enum name
            ]
        failures = []
        checks_run = 0
        checks_passed = 0
        for rule_id in cl_rule_ids:
            result = next((vr for vr in validation_results if vr.rule_id == rule_id), None)
            if result:
                 checks_run += 1
                 if result.passed: checks_passed += 1
                 else:
                     try: msg = result.message(result.details) if callable(result.message) else result.message
                     except Exception: msg = str(result.message)
                     short_msg = msg.split("(")[0].strip()
                     failures.append(f"{rule_id}: {short_msg}")
        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No cover letter checks found."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Cover Letter Quality", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # REFACTORED Section 12 Method
    def _build_qa_section_12_jd_enforcement(self) -> List[str]:
        """Builds QA Section 12: JD Enforcement Validation Summary."""
        lines = ["", "12. JD ENFORCEMENT VALIDATION SUMMARY", ""]
        lines.append("Checks if the Job Description was used throughout the workflow without fallbacks.")
        lines.append("")
        lines.append("```markdown")
        failures = []
        checks_run = 0
        checks_passed = 0
        enforcement_results = getattr(self.jd_enforcer, 'enforcement_results', [])
        checks_run = len(enforcement_results)
        for res in enforcement_results:
             if res.passed: checks_passed += 1
             else: failures.append(f"{res.gate_id} / {res.rule.name}")
        overall_status = "✅ PASS" if not failures and checks_run > 0 else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No enforcement checks found."
        headers = ["Check Area", "Status", "Details"]
        rows = [["JD Enforcement", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures[:5]]) # Limit details
            if len(failures) > 5: lines.append(f"  - ... ({len(failures) - 5} more)")
        return lines

    # REFACTORED Section 13 Method
    def _build_qa_section_13_final_format(
        self,
        validation_results: List[ValidationResult],
        file_contents: Dict[str, str]
    ) -> List[str]:
        """Builds QA Section 13: Final Output Formatting Summary."""
        lines = ["", "13. FINAL OUTPUT FORMATTING SUMMARY", ""]
        lines.append("Checks the presence, basic structure, and formatting of the final rendered files.")
        lines.append("")
        lines.append("```markdown")
        failures = []
        checks_run = 0
        checks_passed = 0
        expected_files = ['resume_md', 'skills', 'cover_letter', 'qa_report', 'app_tracker']

        # Check file presence
        for file_key in expected_files:
             checks_run += 1
             content = file_contents.get(file_key)
             if content: checks_passed += 1
             else: failures.append(f"File Missing: {file_key}")

        # Check specific formatting rules from validation results
        formatting_rule_ids = [
             "QA_TABLE_FORMAT_INVALID", # Generated in HOP-8 QA generation
             "APP_TRACKER_VALIDATION" # Represents JSON validity, schema, etc. from HOP-7 render
             # Add specific rules like VG_RESUME_HEADER_H2 etc. if they are run post-rendering
        ]
        # Include AppTracker rule failures from HOP-7 rendering
        app_tracker_failures = [vr for vr in self.hop_checkpoints[-1].validation_results # Check last checkpoint (HOP-8)
                                if vr.rule_id.startswith("APP_TRACKER_") and not vr.passed] \
                               if self.hop_checkpoints else []
        if app_tracker_failures:
            failures.append(f"AppTracker Validation: {len(app_tracker_failures)} issues found in HOP-7.")
        elif any(vr.rule_id == "APP_TRACKER_VALIDATION" for vr in validation_results): # Check if overall validation rule ran
            checks_run += 1; checks_passed += 1 # Assume passed if no specific failures found in HOP-7

        # Check QA table format rule result (should be in HOP-8 checkpoint)
        qa_format_result = next((vr for vr in self.hop_checkpoints[-1].validation_results
                                 if vr.rule_id == "QA_TABLE_FORMAT_INVALID"), None) \
                                 if self.hop_checkpoints else None
        if qa_format_result:
             checks_run += 1
             if qa_format_result.passed: checks_passed += 1
             else: failures.append(f"QA Report Format: Invalid table formatting detected.")
        else:
             # Check if the rule exists in HOP-5 results as fallback (less likely)
             qa_format_result_hop5 = next((vr for vr in validation_results if vr.rule_id == "QA_TABLE_FORMAT_INVALID"), None)
             if qa_format_result_hop5:
                 checks_run += 1
                 if qa_format_result_hop5.passed: checks_passed += 1
                 else: failures.append(f"QA Report Format (HOP-5): Invalid table formatting detected.")


        overall_status = "✅ PASS" if not failures and checks_run >= len(expected_files) else "❌ FAIL" if failures else "⚠️ WARN"
        details = f"{checks_passed}/{checks_run} checks passed." if checks_run > 0 else "No format checks performed."
        headers = ["Check Area", "Status", "Details"]
        rows = [["Output Formatting", overall_status, details]]
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        if failures:
            lines.append("\n**Failures:**"); lines.extend([f"  - {f}" for f in failures])
        return lines

    # --- END REFACTORED QA Report Section Helper Methods ---


    # --- QA Report Formatting Helpers (Unchanged from previous approval) ---
    def _validate_qa_report_formatting(self, report_text: str) -> ValidationResult:
        """Validates that QA report tables use pre-formatted text."""
        pre_formatted_check_passed = True
        pre_formatted_check_messages = []
        sections = re.split(r'(?m)^\d+\.\s', report_text)
        titles_match = re.findall(r'(?m)^\d+\.\s.*', report_text)
        section_blocks = {}
        if len(sections) > 1:
            for i, title in enumerate(titles_match):
                 section_index = i + 1
                 if section_index < len(sections): # Ensure index is valid
                      content = sections[section_index]
                      section_blocks[section_index] = (title.strip(), content)

        for section_index, (title, section_block) in section_blocks.items():
            if section_index == 1: continue # Skip Section 1 formatting check

            md_blocks = re.findall(r"```markdown(.*?)```", section_block, re.DOTALL)
            if not md_blocks and "```" in section_block:
                 md_blocks = re.findall(r"```(.*?)```", section_block, re.DOTALL)

            # Check if code blocks are missing where expected (Updated section indices)
            if not md_blocks and section_index in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
                pre_formatted_check_passed = False
                msg = f"QA Section {section_index} ({title}) missing expected ```markdown block."
                if msg not in pre_formatted_check_messages:
                    pre_formatted_check_messages.append(msg)
                continue

            # Check for markdown table syntax within code blocks
            for block in md_blocks:
                has_pipe = any("|" in line for line in block.split('\n'))
                # Check for --- separator, potentially with pipes
                has_separator = any(re.match(r"^\s*\|?(-+)\|?(-+\|?)*\s*$", line) for line in block.split('\n'))

                if has_pipe and has_separator:
                    pre_formatted_check_passed = False
                    msg = f"QA Section {section_index} ({title}) appears to contain Markdown table syntax inside ``` block."
                    if msg not in pre_formatted_check_messages:
                        pre_formatted_check_messages.append(msg)

        return ValidationResult(
            rule_id="QA_TABLE_FORMAT_INVALID", passed=pre_formatted_check_passed,
            severity=ValidationSeverity.HIGH if not pre_formatted_check_passed else ValidationSeverity.INFO,
            message="; ".join(pre_formatted_check_messages) if not pre_formatted_check_passed else "All QA tables use pre-formatted text.",
            details={"failed_sections": pre_formatted_check_messages} if not pre_formatted_check_passed else {}
        )

    def _format_ascii_bar_chart(self, label: str, value: float, target_min: float, target_max: float, temperature: Optional[Union[float, str]] = None, bar_length: int = 10, is_summary: bool = False) -> str:
        """Formats a single line ASCII bar chart for signal scores."""
        value = min(max(value, 0.0), 1.0)
        filled_length = int(round(bar_length * value))
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)
        score_pct = f"{value:.1%}"
        status = "PASS" if target_min <= value <= target_max else "FAIL"
        # Handle temperature display safely
        temp_str = "(T: N/A)" # Default
        if isinstance(temperature, float):
             temp_str = f"(T: {temperature:.1f})" if not is_summary else f"(Avg T: {temperature:.1f})"
        elif isinstance(temperature, str): # Handle cases where temp might be string 'N/A'
             temp_str = f"({temperature})"

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
        rows: List[List[Any]], # Allow Any type
        alignments: Optional[List[str]] = None,
        col_widths: Optional[List[int]] = None,
        wrap_text: bool = False
    ) -> List[str]:
        """Formats data into a plain text table suitable for markdown code blocks."""
        # Convert all cells to strings robustly
        str_rows = [[str(cell) for cell in row] for row in rows]
        str_headers = [str(h) for h in headers]
        if not str_headers and not str_rows: return ["(No data available)"]
        num_cols = len(str_headers) if str_headers else (len(str_rows[0]) if str_rows else 0)
        if num_cols == 0: return ["(No data available)"]

        if col_widths and len(col_widths) == num_cols:
            widths = [max(1, w) for w in col_widths]
        else:
            widths = [0] * num_cols
            if str_headers:
                for i, header in enumerate(str_headers):
                     # Handle potential multi-line headers
                     max_header_line = max(len(line) for line in header.split('\n')) if header else 0
                     widths[i] = max(widths[i], max_header_line)
            for row in str_rows:
                for i, cell in enumerate(row):
                    if i < num_cols: widths[i] = max(widths[i], len(cell))
            widths = [max(1, w) for w in widths] # Ensure min width 1

        aligns = alignments or ['L'] * num_cols
        if len(aligns) < num_cols: aligns.extend(['L'] * (num_cols - len(aligns)))

        formatters = []
        for i in range(num_cols):
            align_char = '<' if aligns[i] == 'L' else '>' if aligns[i] == 'R' else '^'
            formatters.append(f"{{:{align_char}{widths[i]}}}")

        lines = []
        # Handle multi-line headers
        if str_headers:
            header_lines_split = [h.split('\n') for h in str_headers]
            max_header_lines = max(len(h_lines) for h_lines in header_lines_split) if header_lines_split else 0
            for line_idx in range(max_header_lines):
                line_parts = []
                for col_idx in range(num_cols):
                    part = header_lines_split[col_idx][line_idx] if line_idx < len(header_lines_split[col_idx]) else ""
                    line_parts.append(formatters[col_idx].format(part))
                lines.append("  ".join(line_parts).rstrip())
            lines.append("  ".join("-" * widths[i] for i in range(num_cols)).rstrip())

        # Handle rows (with optional wrapping)
        if wrap_text:
             for row in str_rows:
                 # Wrap each cell and find max lines needed for this row
                 row_lines_data = [self._wrap_cell_text(cell, widths[i]) if i<num_cols else [""] for i, cell in enumerate(row)]
                 # Ensure row_lines_data has entry for every column
                 while len(row_lines_data) < num_cols: row_lines_data.append([""])

                 max_lines_in_row = max(len(lines_for_cell) for lines_for_cell in row_lines_data) if row_lines_data else 1

                 # Format each line of the wrapped row
                 for line_idx in range(max_lines_in_row):
                     line_parts = []
                     for col_idx in range(num_cols):
                         cell_part = row_lines_data[col_idx][line_idx] if line_idx < len(row_lines_data[col_idx]) else ""
                         line_parts.append(formatters[col_idx].format(cell_part))
                     lines.append("  ".join(line_parts).rstrip())
        else: # No wrapping
             for row in str_rows:
                 line_parts = []
                 for i in range(num_cols):
                     cell_content = row[i][:widths[i]] if i < len(row) else "" # Truncate if needed
                     line_parts.append(formatters[i].format(cell_content))
                 lines.append("  ".join(line_parts).rstrip())
        return lines


    def _wrap_cell_text(self, text: str, width: int) -> List[str]:
        """Wraps text within a cell to a given width."""
        lines = []
        if width <= 0: return [text]
        if not text: return [""] # Handle empty string
        # Simple approach using textwrap (more robust)
        import textwrap
        wrapped_lines = textwrap.wrap(text, width=width, break_long_words=True, replace_whitespace=False)
        return wrapped_lines if wrapped_lines else [""] # Ensure at least one empty line if wrap results in empty

    # --- Word Count Helpers (Unchanged) ---
    def _check_word_count(self, count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        """Checks word count against range, returns status and target string."""
        status = "PASS" if min_target <= count <= max_target else "FAIL"
        target_range_str = f"{min_target}-{max_target}"
        return status, target_range_str

    # --- Deduplication Analysis Method (Unchanged from previous approval) ---
    def _invoke_deduplication_analysis(self, staging_buffer: ImmutableStagingBuffer) -> bool:
        """
        Invokes all deduplication analyses (Pairwise, Overview, Exec Summary).
        Stores results in self.similarity_matrix_data, self.overview_similarity_data,
        and self.executive_summary_similarity_data.
        Returns True if analysis was attempted, False otherwise.
        """
        self.dedup_analysis_timestamp = datetime.now().isoformat()
        if not hasattr(self, 'dup_detector') or self.dup_detector is None:
            self.logger.warning("DuplicateDetector not available. Skipping deduplication analysis.")
            return False

        # --- Data Gathering ---
        sections_for_matrix = {}
        overview_bullet_pairs = {}
        exec_summary_text = staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        exec_summary_comparison_data = {}

        # Updated mapping for K0-K11
        section_map = {
            ResumeSection.K1_EXECUTIVE_SUMMARY: "Exec Summary",
            ResumeSection.K2_UNIFY_OVERVIEW: "Unify Overview",
            ResumeSection.K2_UNIFY_BULLETS: "Unify Bullets",
            ResumeSection.K3_IBM_OVERVIEW: "IBM Overview",
            ResumeSection.K3_IBM_BULLETS: "IBM Bullets",
            # K4 TraderSense (Narrative stored in buffer, master has highlights)
            ResumeSection.K4_TRADERSENSE_NARRATIVE: "TraderSense Narrative",
            # K5 EY (Narrative stored in buffer)
            ResumeSection.K5_EY_NARRATIVE: "EY Narrative",
            # K6 Early Career (Narrative stored in buffer)
            ResumeSection.K6_EARLY_CAREER_NARRATIVE: "Early Career Narrative",
            ResumeSection.K9_COMPETENCIES: "Competencies",
            ResumeSection.K10_SKILLS: "Skills",
            ResumeSection.K11_COVER_LETTER: "Cover Letter",
        }

        # --- Process Sections ---
        for section_enum, label in section_map.items():
            content = staging_buffer.get(section_enum.value)
            if not content: continue

            # Overviews (Unify, IBM)
            if label in ["Unify Overview", "IBM Overview"]:
                if isinstance(content, str) and content.strip():
                    overview_text = content.strip()
                    sections_for_matrix[label] = [overview_text] # Include in pairwise matrix
                    # Store for Exec Summary comparison
                    exec_summary_comparison_data[label] = overview_text
                continue

            # Bullets (Unify, IBM, Competencies)
            if label in ["Unify Bullets", "IBM Bullets", "Competencies"]:
                bullet_texts = []
                if isinstance(content, list):
                    for item in content:
                        text = (item.get('text', item.get('bullet_text','')) if isinstance(item, dict) else str(item))
                        if text and text.strip(): bullet_texts.append(text.strip())
                if not bullet_texts: continue

                sections_for_matrix[label] = bullet_texts # Include bullets in matrix
                exec_summary_comparison_data[label] = bullet_texts # Store for Exec Summary comparison
                # Overview vs Bullet check doesn't apply to K2/K3/K9 vs their own bullets
                continue

            # Narrative Blocks (TraderSense, EY, Early Career)
            if label in ["TraderSense Narrative", "EY Narrative", "Early Career Narrative"]:
                 if isinstance(content, str) and content.strip():
                      narrative_text = content.strip()
                      sections_for_matrix[label] = [narrative_text] # Include narratives in matrix
                      exec_summary_comparison_data[label] = narrative_text
                      # Overview vs Bullet Check (Treat narrative as 'overview' vs master highlights?)
                      # Find corresponding master highlights
                      master_index_map = {
                           "TraderSense Narrative": 2, "EY Narrative": 3, "Early Career Narrative": 4
                      }
                      master_idx = master_index_map.get(label)
                      master_highlights = []
                      if master_idx is not None and master_idx < len(self.master_resume.get("professional_experience", [])):
                           master_exp = self.master_resume["professional_experience"][master_idx]
                           master_highlights = [h for h in master_exp.get('highlights', []) if isinstance(h, str) and h.strip()]

                      if narrative_text and master_highlights:
                           # Add to pairs for overview check (Narrative vs Master Highlights)
                           overview_bullet_pairs[label] = {"overview": narrative_text, "bullets": master_highlights}
                 continue

            # Skills
            if label == "Skills":
                if isinstance(content, list):
                    skill_texts = [item for item in content if isinstance(item, str) and item.strip()]
                    if skill_texts:
                        exec_summary_comparison_data[label] = skill_texts
                        # Do not include skills in pairwise matrix
                        # sections_for_matrix[label] = skill_texts
                        self.logger.debug(f"Excluding {label} from pairwise similarity matrix.")
                continue

            # Cover Letter
            if label == "Cover Letter":
                if isinstance(content, str) and content.strip():
                    all_cl_parts = [p.strip() for p in content.split('\n\n') if p.strip()]
                    body_paras = []
                    try: # Simple extraction of body paragraphs
                        start_idx = next(i for i, p in enumerate(all_cl_parts) if p.startswith("Dear Hiring Manager,")) + 1
                        end_idx = next(i for i, p in enumerate(all_cl_parts) if p == "Sincerely,")
                        body_paras = all_cl_parts[start_idx:end_idx]
                    except StopIteration: body_paras = all_cl_parts[1:-1] # Fallback
                    if all_cl_parts: exec_summary_comparison_data[label] = all_cl_parts
                    if body_paras: sections_for_matrix[label] = body_paras # Include body in matrix
                continue

            # Exec Summary
            if label == "Exec Summary":
                 if isinstance(content, str) and content.strip():
                     sections_for_matrix[label] = [content.strip()]
                 continue


        # --- Perform Calculations ---
        try:
            self.similarity_matrix_data = self.dup_detector.compute_similarity_matrix(sections_for_matrix)
            self.logger.info(f"Pairwise matrix computed ({self.similarity_matrix_data.get('total_comparisons', 0)} comparisons).")
        except Exception as e:
            self.logger.error(f"Error computing similarity matrix: {e}", exc_info=False)
            self.similarity_matrix_data = None

        try:
            self.overview_similarity_data = []
            for label, data in overview_bullet_pairs.items(): # Contains narratives vs master highlights now
                 if data["overview"] and data["bullets"]:
                     sim_result = self.dup_detector.compute_overview_bullet_similarity(
                         data["overview"], data["bullets"], section_id=label
                     )
                     self.overview_similarity_data.append(sim_result)
            self.logger.info(f"Narrative vs Master Highlight similarity computed for {len(self.overview_similarity_data)} sections.")
        except Exception as e:
            self.logger.error(f"Error computing narrative vs highlight similarity: {e}", exc_info=False)
            self.overview_similarity_data = None

        try:
            # Ensure exec_summary_text is valid before proceeding
            if exec_summary_text:
                self.executive_summary_similarity_data = self.dup_detector.compute_executive_summary_similarity(
                    exec_summary_text, exec_summary_comparison_data
                )
                self.logger.info(f"Exec Summary similarity computed against {len(exec_summary_comparison_data)} sections.")
            else:
                 self.logger.warning("Skipping Exec Summary similarity calculation: Exec Summary text is empty.")
                 self.executive_summary_similarity_data = [] # Set to empty list

        except Exception as e:
             self.logger.error(f"Error computing exec summary similarity: {e}", exc_info=False)
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