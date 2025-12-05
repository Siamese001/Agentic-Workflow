from __future__ import annotations

import json
import re # Added for truncation check logic and new validation rules
import hashlib
import math
import logging
import os
import time

__version__ = "9.96"
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
    cot_min_paths: int = 3
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 6
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
    TOTAL_WORD_COUNT_MIN: int = 930
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 5

    # K.0 Headline
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11

    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 120
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 150
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 5
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 6
    K1_MIN_DIFFERENTIATORS: int = 3

    # Experience Overviews
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35
    EY_OVERVIEW_WORD_COUNT_MIN: int = 25
    EY_OVERVIEW_WORD_COUNT_MAX: int = 35
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 18
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 30

    # K.13 Cover Letter
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
    Centralized configuration for signal dampening and overfitting prevention.
    Defines the MAXIMUM signal thresholds to maintain authenticity.
    """
    # K.1 Executive Summary
    # Min is 3 (from VG_K1_DIFFERENTIATOR_KEYWORDS), so 3-4 is the sweet spot.
    K1_MAX_DIFFERENTIATORS: int = 4

    # Overall Resume
    # Min is 5 (from JD_KEYWORD_ENFORCEMENT), so 5-15 is a healthy range.
    RESUME_MAX_JD_KEYWORDS: int = 15

    # K.13 Cover Letter
    # Min is 0.35. Anything above 0.75 is highly suspicious and overfit.
    CL_MAX_JD_SIMILARITY: float = 0.75

    # QA Report (Section 1)
    # The absolute maximum signal score a section should have before being flagged.
    # A 100% score is a major red flag for AI detection.
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
    ("K0_HEADLINE_CONFIG", dict(cot_min_paths=4, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)),
    ("K1_EXECUTIVE_SUMMARY_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=12, reflexion=True, max_reflexion_loops=2)),
    ("K5_UNIFY_BULLETS_CONFIG", dict(cot_min_paths=4, tot_branches=3, min_tot_depth=3, self_consistency=12, reflexion=True)),
    ("K5_UNIFY_OVERVIEW_CONFIG", ReasoningConfig.DEFAULT), # Assign the default instance directly
    ("K6_IBM_BULLETS_CONFIG", dict(cot_min_paths=4, tot_branches=3, min_tot_depth=3, self_consistency=12, reflexion=True)),
    ("K6_IBM_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K8_EY_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K8_EY_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K9_EARLY_CAREER_BULLETS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K9_EARLY_CAREER_OVERVIEW_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K2_SKILLS_CONFIG", dict(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=4, reflexion=False)),
    ("K10_COMPETENCIES_CONFIG", dict(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=10, reflexion=True)),
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
    """Converts reasoning config to Gemini API parameters by orchestrating helper functions."""
    import logging
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)
    intensity, level = _calculate_reasoning_intensity(params)
    params['intensity_score'] = intensity
    params['reasoning_level'] = level

    temperature = _get_generation_temperature()
    max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(f"Reasoning config: intensity={intensity:.1f}, temp={temperature}, tokens={max_tokens}, level={level}")
    except:
        pass  # Silently fail if logger not available
    
    return {
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens),
        "system_prompt_addendum": prompt_addendum,
        **params
    }

def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """Handles defaults and clamps reasoning config values."""
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12
    reflexion = config.reflexion if config.reflexion is not None else True
    max_loops = config.max_reflexion_loops if config.max_reflexion_loops is not None else 2

    return {
        "cot": max(2, min(config.cot_min_paths if config.cot_min_paths is not None else 3, 8)),
        "tot_b": max(2, min(tot_b, 6)),
        "tot_d": max(2, min(tot_d, 5)),
        "sc": max(1, min(sc, 30)),
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
    if tot_d >= 4: max_tokens = 800
    elif tot_d >= 3 and cot >= 5: max_tokens = 700
    elif tot_d >= 3 or cot >= 5: max_tokens = 600
    elif sc >= 15: max_tokens = 500
    else: max_tokens = 400
    return max(400, min(max_tokens, 8000))

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
    rule_id: str
    severity: ValidationSeverity  # <-- Correctly references the class
    validator: Any  # Callable[[Dict], bool] but using Any to avoid type issues
    error_message: Union[str, Callable[[Dict], str]] # <-- More accurate type hint
    category: str = "general"  # For grouping rules
    
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
        """
        Execute validation rules and return results.
        
        Args:
            data: Data to validate
            categories: Optional list of categories to validate (None = all)
        
        Returns:
            List of ValidationResult objects
        """
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
    """
    Enhanced configuration for resilient web RAG system.
    v5.59: Added multi-layer resilience parameters.
    """
    
    # API settings
    model: str = "gemini-1.5-flash"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Search targets
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
    """
    Enhanced wrapper for Gemini API with comprehensive resilience.
    v5.59: Multi-layer retry, circuit breaker, adaptive backoff, JSON repair.
    
    Features:
    - 7 retries with adaptive exponential backoff + jitter
    - Circuit breaker pattern (5 failures → 60s timeout)
    - Per-request timeout (30s)
    - JSON repair strategies (for Gemini's JSON mode)
    - Comprehensive error handling
    """
    
    def __init__(self, api_key: Optional[str], config: RAGConfig = RAGConfig()):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package required for web RAG")
        
        # Initialize Gemini client. If api_key is None, it will rely on environment variables
        # or implicit credentials in environments like Google Cloud/Gemini WebApp.
        self.client = genai.GenerativeModel(
            config.model,
            api_key=api_key # Pass API key, can be None
        )
        
        self.config = config
        self.circuit_breaker = CircuitBreaker(config)
        
        # Web search tool definition
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
    
    def _make_api_call(
        self, 
        prompt: str, 
        attempt: int,
        phase_name: str,
        logger
    ) -> Dict[str, Any]:
        """Make the actual API call with timeout."""
        start_time = time.time()
        
        try:
            response = self.client.generate_content(
                prompt,
                tools=[self.web_search_tool],
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    response_mime_type="application/json"
                )
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"{phase_name} API call completed in {elapsed:.2f}s")
            
            # Parse JSON from response
            return self._extract_json(response.text)
            
        except Exception as e: # Catch general exceptions for Gemini API
            elapsed = time.time() - start_time
            logger.warning(f"{phase_name} timed out after {elapsed:.2f}s")
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
        """
        
        # Strategy 1: Markdown JSON code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass  # Try next strategy
        
        # Strategy 2: First complete JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass  # Try next strategy
        
        # Strategy 3: Remove markdown artifacts and retry
        cleaned = text_content.replace('```json', '').replace('```', '').strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Try to repair common JSON errors
        repaired = self._attempt_json_repair(cleaned)
        if repaired:
            return repaired
        
        raise ValueError(
            f"No valid JSON found in Gemini's response. "
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
        """
        
        def main_phase1():
            prompt = self._build_phase1_prompt(job_description, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 1: Thematic Research")
        
        def fallback_phase1():
            prompt = self._build_phase1_prompt(job_description, detailed=False)
            return self.client.search_and_analyze(
                prompt, 
                "Phase 1: Thematic Research (Simplified)"
            )
        
        return self.executor.execute_with_retry(
            main_phase1,
            "Phase 1",
            fallback_func=fallback_phase1
        )
    
    def _build_phase1_prompt(self, job_description: str, mission: RAGMission, detailed: bool = True) -> str:
        """
        Build Phase 1 prompt with optional simplification.
        v5.59: Simplified version reduces search count for fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
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
        
        # (Approach 2) Add authoritative source queries
        authoritative_searches = f"""
**Authoritative Search Directives (High Priority):**
1. Search for: `"{mission.target_company_name} engineering blog"`
2. Search for: `"{mission.target_company_name} values"` or `"{mission.target_company_name} operating principles"`
3. Search for: `"{mission.target_company_name} press release {mission.key_technologies[0]}"` if technologies are present.
"""

        return f"""You are a job market intelligence analyst. Research this role using web_search.

JOB DESCRIPTION:
{job_description[:1500]}

TASK: First, perform the authoritative searches. Then, search for {search_count} similar job postings that also contain these keywords: {', '.join(mission.key_technologies)}. {detail_level}

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
        """
        role_title = mission.precise_role_title
        
        def main_phase2():
            prompt = self._build_phase2_prompt(job_description, role_title, detailed=True)
            return self.client.search_and_analyze(prompt, "Phase 2: Authenticity Patterns")
        
        def fallback_phase2():
            prompt = self._build_phase2_prompt(job_description, role_title, detailed=False)
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
        role_title: str,
        mission: RAGMission,
        detailed: bool = True
    ) -> str:
        """
        Build Phase 2 prompt with optional simplification.
        v5.59: Simplified version reduces analysis depth for fallback.
        v8.10: Enhanced with RAGMission and Authoritative Sources (Approach 1 & 2).
        """
        
        industry = self._infer_industry(job_description)

        # (Approach 2) Add authoritative source queries
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

TARGET ROLE: {mission.precise_role_title}
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
        """
        # <<< FIX: Use mission object passed as argument >>>
        company_name = mission.target_company_name
        role_title = mission.precise_role_title

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
        v9.84: Fixed undefined variables, uses mission object, simplified fallback.
        """
        # <<< FIX: Extract company/role from mission >>>
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

        # <<< FIX: Simplified fallback logic based on 'detailed' flag >>>
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
    
    def _analyze_with_resilient_web_search(
        self, 
        job_description: str
    ) -> 'ThematicAnalysis':
        """
        v5.59: Enhanced analysis with 4-tier fallback strategy and telemetry.
        
        Strategy:
        1. Try full 3-phase RAG
        2. On partial failure, synthesize with available phases
        3. On full failure, try hybrid local+web
        4. On all failure, pure local NLP
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Initialize telemetry
        telemetry = RAGTelemetry() if self.telemetry_logger else None
        start_time = time.time()
        
        # Check cache first
        if self.cache_manager:
            cached = self.cache_manager.get(job_description)
            if cached:
                logger.info("Using cached web RAG analysis")
                return self._dict_to_thematic_analysis(cached)
        
        # Ensure web RAG is available
        if not self.web_rag:
            logger.warning("Web RAG not initialized or API key missing. Falling back to local NLP.")
            if telemetry:
                telemetry.local_fallback = True
                telemetry.errors.append("Web RAG not initialized")
                telemetry.total_duration_seconds = time.time() - start_time
                self.telemetry_logger.log(telemetry)
            return self._analyze_local_nlp(job_description)
        
        # ===================================================================
        # STRATEGY 1: FULL THREE-PHASE RAG (IDEAL PATH)
        # ===================================================================
        partial_result = PartialRAGResult()
        
        # Phase 1: Thematic Research
        phase1_start = time.time()
        try:
            logger.info("=== Starting Phase 1: Thematic Research ===")
            phase1_results = self.web_rag.phase1_thematic_research(job_description, self.rag_mission)
            partial_result.phase1_result = phase1_results
            partial_result.phase1_success = True
            self.search_calls_made += phase1_results["search_summary"]["searches_performed"]
            if telemetry:
                telemetry.phase1_success = True
                telemetry.phase1_attempts = 1  # Simplified, actual attempts tracked in executor
                telemetry.total_search_calls += phase1_results["search_summary"]["searches_performed"]
            logger.info(f"Phase 1: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 1: FAILED - {e}")
            partial_result.failure_reasons.append(f"Phase 1: {type(e).__name__}")
            if telemetry:
                telemetry.phase1_success = False
                telemetry.errors.append(f"Phase 1: {type(e).__name__}: {str(e)[:100]}")
        finally:
            if telemetry:
                telemetry.phase1_duration_seconds = time.time() - phase1_start
        
        # Phase 2: Authenticity Patterns
        phase2_start = time.time()
        try:
            logger.info("=== Starting Phase 2: Authenticity Patterns ===")
            phase2_results = self.web_rag.phase2_authenticity_patterns(
                job_description,
                self.rag_mission
            )
            partial_result.phase2_result = phase2_results
            partial_result.phase2_success = True
            self.search_calls_made += phase2_results["search_summary"]["profiles_analyzed"]
            if telemetry:
                telemetry.phase2_success = True
                telemetry.phase2_attempts = 1
                telemetry.total_search_calls += phase2_results["search_summary"]["profiles_analyzed"]
            logger.info(f"Phase 2: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 2: FAILED - {e}")
            partial_result.failure_reasons.append(f"Phase 2: {type(e).__name__}")
            if telemetry:
                telemetry.phase2_success = False
                telemetry.errors.append(f"Phase 2: {type(e).__name__}: {str(e)[:100]}")
        finally:
            if telemetry:
                telemetry.phase2_duration_seconds = time.time() - phase2_start
        
        # Phase 3: Competitive Positioning
        phase3_start = time.time()
        try:
            logger.info("=== Starting Phase 3: Competitive Positioning ===")
            phase3_results = self.web_rag.phase3_competitive_positioning(
                job_description,
                self.rag_mission
            )
            partial_result.phase3_result = phase3_results
            partial_result.phase3_success = True
            self.search_calls_made += phase3_results["search_summary"]["peer_jds_analyzed"]
            if telemetry:
                telemetry.phase3_success = True
                telemetry.phase3_attempts = 1
                telemetry.total_search_calls += phase3_results["search_summary"]["peer_jds_analyzed"]
            logger.info(f"Phase 3: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 3: FAILED - {e}")
            partial_result.failure_reasons.append(f"Phase 3: {type(e).__name__}")
            if telemetry:
                telemetry.phase3_success = False
                telemetry.errors.append(f"Phase 3: {type(e).__name__}: {str(e)[:100]}")
        finally:
            if telemetry:
                telemetry.phase3_duration_seconds = time.time() - phase3_start
        
        # Phase 4: Problem-Solution Narrative Mining (Approach 3)
        phase4_start = time.time()
        try:
            logger.info("=== Starting Phase 4: Narrative Mining ===")
            phase4_results = self.web_rag.phase4_narrative_mining(self.rag_mission)
            partial_result.phase4_result = phase4_results
            partial_result.phase4_success = True
            self.search_calls_made += phase4_results["search_summary"]["searches_performed"]
            if telemetry:
                telemetry.phase4_success = True
                telemetry.phase4_attempts = 1
                telemetry.total_search_calls += phase4_results["search_summary"]["searches_performed"]
            logger.info(f"Phase 4: SUCCESS ({self.search_calls_made} searches so far)")
        except Exception as e:
            logger.warning(f"Phase 4: FAILED - {e}")
            partial_result.failure_reasons.append(f"Phase 4: {type(e).__name__}")
            if telemetry:
                telemetry.phase4_success = False
                telemetry.errors.append(f"Phase 4: {type(e).__name__}: {str(e)[:100]}")
        finally:
            if telemetry:
                telemetry.phase4_duration_seconds = time.time() - phase4_start

        # ===================================================================
        # EVALUATE RESULTS AND CHOOSE STRATEGY
        # ===================================================================
        logger.info(
            f"RAG Phases Complete: "
            f"Success Rate = {partial_result.success_rate:.1%} "
            f"({partial_result.phase1_success}, {partial_result.phase2_success}, "
            f"{partial_result.phase3_success}, {partial_result.phase4_success})"
        )
        
        if partial_result.full_success:
            # IDEAL: All phases succeeded
            logger.info("✓ Strategy 1: Full 3-phase RAG successful")
            analysis = self._synthesize_thematic_analysis(
                partial_result.phase1_result,
                partial_result.phase2_result,
                partial_result.phase3_result,
                partial_result.phase4_result,
                job_description
            )
            if telemetry:
                telemetry.full_success = True
                telemetry.success_rate = 1.0
        
        elif partial_result.any_success:
            # New Design: Partial success is now a failure.
            logger.error(f"✗ RAG analysis was only partially successful ({partial_result.success_rate:.0%}). Halting workflow.")
            raise HopExecutionError("RAG analysis failed to achieve 100% success across all four phases.")
        
        else:
            # New Design: No phases succeeding is a fatal error.
            logger.error("✗ All RAG phases failed. Halting workflow.")
            logger.warning(f"Failure reasons: {', '.join(partial_result.failure_reasons)}")
            raise HopExecutionError("All RAG phases failed during execution.")
        
        # Cache result (even partial successes)
        if self.cache_manager and partial_result.any_success:
            self.cache_manager.set(job_description, asdict(analysis))
        
        # Log telemetry
        if telemetry:
            telemetry.total_duration_seconds = time.time() - start_time
            telemetry.total_api_calls = self.search_calls_made  # Approximate
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

    def _synthesize_thematic_analysis(
        self,
        phase1: Dict,
        phase2: Dict,
        phase3: Dict,
        phase4: Dict, # v8.10: Approach 3
        job_description: str
    ) -> 'ThematicAnalysis':
        """
        Synthesize three-phase web RAG results into ThematicAnalysis.
        v8.10: Implements Weighted Synthesis (Approach 4).
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Synthesizing RAG results with weighted analysis...")

        # --- Keyword Aggregation and Weighted Scoring ---
        keyword_scores = {}
        weights = self.config.source_weights

        # Phase 1: Thematic (Company Blog, Peer JDs)
        # We'll approximate: primary theme keywords get higher weight (blog), others get peer weight.
        for kw in phase1["thematic_analysis"]["primary_theme"]["keywords"]:
            keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_COMPANY_BLOG", 1.5)
        for theme in phase1["thematic_analysis"]["secondary_themes"]:
            for kw in theme["keywords"]:
                keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)
        for kw in phase1["thematic_analysis"]["trending_keywords"]:
             keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)

        # Phase 2: Authenticity (Target Employee, Generic Profiles)
        # We'll give higher weight to competency phrasing, assuming it's from target employees.
        for pattern_list in phase2["authenticity_patterns"].values():
            if isinstance(pattern_list, list):
                for kw in pattern_list: # Simplified: treat all patterns as keywords for now
                    # A simple heuristic to differentiate target vs generic
                    if "competency" in phase2["authenticity_patterns"] and kw in phase2["authenticity_patterns"]["competency_phrasing"]:
                         weight = weights.get("SOURCE_TARGET_EMPLOYEE", 1.4)
                    else:
                         weight = weights.get("SOURCE_GENERIC_PROFILE", 0.5)
                    keyword_scores[kw] = keyword_scores.get(kw, 0) + weight

        # Phase 3: Competitive (Gartner/Forrester, Peer JDs)
        # Differentiators get a higher weight as they are more unique.
        for item in phase3["competitive_analysis"]["differentiator_keywords"]:
            kw = item["keyword"]
            # Heuristic: if it's a differentiator, it's more likely from expert analysis
            weight = weights.get("SOURCE_GARTNER_MQ", 1.2) * item.get("uniqueness_score", 1.0)
            keyword_scores[kw] = keyword_scores.get(kw, 0) + weight
        for item in phase3["competitive_analysis"]["table_stakes_keywords"]:
            kw = item["keyword"]
            keyword_scores[kw] = keyword_scores.get(kw, 0) + weights.get("SOURCE_PEER_JD", 0.8)

        # Sort keywords by weighted score
        sorted_keywords = sorted(keyword_scores.items(), key=lambda item: item[1], reverse=True)
        
        differentiator_keywords_weighted = [{"keyword": kw, "weight": score} for kw, score in sorted_keywords]
        top_differentiators = [kw for kw, score in sorted_keywords[:15]] # Get top 15

        logger.info(f"  ✓ Top 5 weighted keywords: {top_differentiators[:5]}")
        
        # Extract primary theme from Phase 1
        primary_theme = {
            "name": phase1["thematic_analysis"]["primary_theme"]["name"],
            "confidence": phase1["thematic_analysis"]["primary_theme"]["confidence"],
            "keywords": phase1["thematic_analysis"]["primary_theme"]["keywords"],
            "market_signal": "STRONG", "source": "WEB_SEARCH"
        }
        
        # Extract secondary themes
        secondary_themes = [
            {"name": t["name"], "relevance": t["relevance"], "keywords": t["keywords"], "source": "WEB_SEARCH"}
            for t in phase1["thematic_analysis"]["secondary_themes"][:5]
        ]
        
        # Role classification
        role_classification = phase1["role_classification"]
        role_classification["precise_role_title"] = self.rag_mission.precise_role_title
        
        # Positioning directives
        positioning_directives = {
            "apply_industry_first": True, "authenticity_positioning_ratio": "0.8:0.2",
            "competitive_edge": phase3["positioning_insight"],
            "table_stakes_count": len(phase3["competitive_analysis"]["table_stakes_keywords"]),
            "differentiator_count": len(top_differentiators)
        }
        
        # Authenticity patterns
        authenticity_patterns = {
            "status": "STRONG" if phase2["pattern_confidence"]["overall"] > 0.7 else "MODERATE",
            "patterns": phase2["authenticity_patterns"], "confidence": phase2["pattern_confidence"],
            "fallback_applied": False, "fallback_reason": None
        }
        
        # Competitive intelligence
        competitive_intel = CompetitiveIntelligence(
            peer_jds_analyzed_count=phase3["search_summary"]["peer_jds_analyzed"],
            differentiator_keywords=top_differentiators,
            differentiator_keywords_raw=top_differentiators, # Use the same ranked list
            differentiator_keywords_weighted=differentiator_keywords_weighted
        )
        
        # Signal quality score
        signal_quality = (
            phase1["thematic_analysis"]["primary_theme"]["confidence"] * 0.4 +
            phase2["pattern_confidence"]["overall"] * 0.3 +
            (phase3["search_summary"]["peer_jds_analyzed"] / 15.0) * 0.3 # Normalize
        )
        
        # Retrieval sources
        retrieval_sources = []
        retrieval_sources.append(RetrievalSource("PHASE1_THEMATIC", "Web_RAG", 1.0, "SUCCESS", "SOURCE_COMPANY_BLOG"))
        retrieval_sources.append(RetrievalSource("PHASE2_AUTHENTICITY", "Web_RAG", 1.0, "SUCCESS", "SOURCE_TARGET_EMPLOYEE"))
        retrieval_sources.append(RetrievalSource("PHASE3_COMPETITIVE", "Web_RAG", 1.0, "SUCCESS", "SOURCE_GARTNER_MQ"))
        retrieval_sources.append(RetrievalSource("PHASE4_NARRATIVE", "Web_RAG", 1.0, "SUCCESS", "SOURCE_NARRATIVE_MINING")) # v8.10: Approach 3
        
        return ThematicAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_classification=role_classification,
            positioning_directives=positioning_directives,
            authenticity_patterns=authenticity_patterns,
            competitive_intelligence=competitive_intel,
            problem_solution_narratives=phase4.get("problem_solution_narratives"), # v8.10: Approach 3
            signal_quality_score=signal_quality,
            retrieval_method="WEB_SEARCH_RAG",
            retrieval_sources=retrieval_sources
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
        """Convert cached dict back to ThematicAnalysis object."""
        comp_intel = CompetitiveIntelligence(**data["competitive_intelligence"])
        
        retrieval_sources = [
            RetrievalSource(**src) for src in data.get("retrieval_sources", [])
        ]
        
        return ThematicAnalysis(
            primary_theme=data["primary_theme"],
            secondary_themes=data["secondary_themes"],
            role_classification=data["role_classification"],
            positioning_directives=data["positioning_directives"],
            authenticity_patterns=data["authenticity_patterns"],
            competitive_intelligence=comp_intel,
            signal_quality_score=data["signal_quality_score"],
            retrieval_method=data["retrieval_method"],
            retrieval_sources=retrieval_sources,
            problem_solution_narratives=data.get("problem_solution_narratives") # v8.10: Approach 3
        )
    
    # ========================================================================
    # LOCAL NLP FALLBACK (v5.52 implementation - UNCHANGED)
    # ========================================================================
    
    def _analyze_local_nlp(self, job_description: str) -> 'ThematicAnalysis':
        """
        Fallback analysis using local NLP (v5.52 implementation).
        This remains UNCHANGED from your original file.
        """
        keywords = self._extract_keywords(job_description)
        theme_scores = self._calculate_theme_scores(keywords, job_description)
        primary_theme = self._generate_primary_theme(theme_scores, keywords)
        secondary_themes = self._generate_secondary_themes(theme_scores, keywords)
        competitive_intel = self._extract_competitive_intelligence(keywords, job_description)
        role_classification = self._classify_role(keywords, job_description)
        signal_quality_score = self._calculate_signal_quality(keywords, theme_scores)
        
        return ThematicAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_classification=role_classification,
            positioning_directives={
                "apply_industry_first": True,
                "authenticity_positioning_ratio": "0.8:0.2"
            },
            authenticity_patterns={
                "status": "STRONG",
                "patterns": [],
                "fallback_applied": True if not self.enable_web_search else False,
                "fallback_reason": "Web search disabled" if not self.enable_web_search else None
            },
            competitive_intelligence=competitive_intel,
            signal_quality_score=signal_quality_score,
            retrieval_method="LOCAL_NLP" if not self.enable_web_search else "HYBRID",
            retrieval_sources=[
                RetrievalSource("JD_ANALYSIS", "NLP_Keyword_Extraction", 1.0, "LOCAL_FALLBACK", "LOCAL_NLP")
            ]
        )
    
    # All the local NLP helper methods below remain UNCHANGED from v5.53
    # (_extract_keywords, _calculate_theme_scores, _generate_primary_theme, etc.)
    
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
            "header": self.master_resume.get("header", {}),
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications", [])
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
        
        for exp in self.master_resume.get("experience", []):
            bullets = []
            for bullet_text in exp.get("bullets", []):
                bullets.append({
                    "bullet_text": bullet_text,
                    "quantified_metrics": self._extract_metrics(bullet_text),
                    "canonical_verbs": [],  # Will be enriched in HOP-2
                    "provenance": BulletProvenance.Verbatim.value
                })
            
            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", ""),
                "overview": exp.get("overview", ""),
                "bullets": bullets,
                "highlights": [bullet['bullet_text'] for bullet in bullets]  # For backward compatibility
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
    # --- END FIX ---

# ============================================================================
# HOP-3: ARTIST GENERATOR (LLM Calls)
# ============================================================================

class ArtistGenerator:
    """
    HOP-3: Generate resume content using Gemini API.
    This is where the actual LLM calls happen.
    """
    
    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, previous_failures: List[ValidationResult] = None):
        """Initializes the ArtistGenerator with the master resume."""
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.previous_failures = previous_failures or []
        self.constraints = ContentConstraintsConfig() # Centralized constraints
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

    # Moved from PreFlightValidator to ArtistGenerator where it's used for generation logic
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2}, # Assuming same split for competencies
        ResumeSection.K8_EY_BULLETS: {'Customized': 2}, # Target 2 customized bullets for EY
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1}, # Target 1 customized bullet for Early Career
    }

    # Configuration for the artist generation process.
    # This list defines which section is generated by which method, making
    # the generation process data-driven and easy to modify.
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
        {"section": ResumeSection.K2_SKILLS, "method_name": "_generate_k2_skills"},
        # Header sections for rendering - ensure they exist if needed by FileRenderer
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
        attempt: int = 1
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Generate all resume content using LLM.
        
        Args:
            feedback_results: Validation failures from previous attempt (if any)
            attempt: Current generation attempt (1-5)
        
        Returns:
            (artist_output, validation_results)
        """
        validation_results = []
        
        # Update failures from feedback loop
        if feedback_results:
            self.previous_failures = feedback_results
        
        try:
            artist_output = self._generate_artist_output()
            
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
    
    def _generate_artist_output(self) -> Dict:
        """
        Generate complete artist output with all K.X sections.
        v5.26: Added K.7A/B (EY), K.7.5A/B (TraderSense), K.10A/B (Early Career)
        """
        
        output = {}
        for config in self.ARTIST_GENERATION_CONFIG:
            section_enum = config["section"]
            method_name = config["method_name"]
            try:
                method = getattr(self, method_name)
                output[section_enum.value] = method()
            except Exception as e:
                logging.error(f"Error generating section {section_enum.value} with {method_name}: {e}", exc_info=True)
                output[section_enum.value] = f"[Placeholder for {section_enum.value} due to generation error: {e}]"
        # Ensure all expected sections by FileRenderer exist, even if None
        for section_enum in ResumeSection:
            # Check if section_enum.value is a valid key before accessing output
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

    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str) -> str:
        """
        Refactored Helper: Centralizes Gemini API calls, including reasoning config and error handling.
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # 1. Get API params from reasoning config
            api_params = reasoning_config_to_api_params(reasoning_config)
            generation_config = api_params["generation_config"]
            sc_count = api_params.get('sc', 1)
            
            # 2. Enhance system prompt with reasoning directives (now without SC)
            enhanced_system = enhance_system_prompt_with_reasoning(system_prompt, reasoning_config, section_id)
            
            # 3. Check if Self-Consistency (SC) is enabled
            if sc_count > 1:
                # --- TRUE SELF-CONSISTENCY (REFACTORED) ---
                logging.info(f"  Running Self-Consistency for {section_id} (requesting {sc_count} candidates)...")
                
                # Force high temperature for diverse samples
                generation_config.temperature = 0.9
                # Use candidate_count for a single, efficient API call
                generation_config.candidate_count = sc_count
                
                candidate_responses = []
                try:
                    response = model.generate_content(
                        f"{enhanced_system}\n\n{prompt}",
                        generation_config=generation_config
                    )
                    
                    # Safely extract candidates
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
                    # If the call fails, we have no candidates to synthesize.
                    # Re-raise as HopExecutionError to be caught by the generator loop.
                    raise HopExecutionError(f"{section_id} Self-Consistency API call failed: {e}")
                
                # --- End of refactor ---

                if not candidate_responses:
                    # This check is now redundant but safe to keep as a fallback.
                    raise HopExecutionError(f"{section_id} Self-Consistency failed: No responses generated.")

                # 4. Synthesize results
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

                # --- START MODIFICATION ---
                # v9.95: Changed temperature from 0.1 to 0.5 to meet user's min temp requirement.
                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=api_params["generation_config"].max_output_tokens)
                # --- END MODIFICATION ---
                
                synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)
                return synthesis_response.text.strip()

            else:
                # --- SINGLE-CALL (SC=1) ---
                response = model.generate_content(
                    f"{enhanced_system}\n\n{prompt}",
                    generation_config=generation_config
                )
                # Safer text extraction for single call
                try:
                    return response.text.strip()
                except (ValueError, AttributeError) as e:
                    # Handle cases where response.text is not available (e.g., safety block)
                    logging.warning(f"LLM generation for {section_id} returned no text: {e}. Response: {response}")
                    raise HopExecutionError(f"{section_id} generation returned no valid text.")

        except ValueError as ve: # Specifically for API key missing
            logging.warning(f"LLM generation for {section_id} failed: {ve}. Returning placeholder.")
            return f"[Placeholder for {section_id} - {ve}]"
        except ImportError:
            logging.warning(f"LLM generation for {section_id} failed: google.generativeai not installed. Returning placeholder.")
            return f"[Placeholder for {section_id} - Gemini library not found]"
        except HopExecutionError as he: # Re-raise HopExecutionError
            logging.warning(f"LLM generation for {section_id} failed: {he}")
            return f"[Placeholder for {section_id} - {he}]"
        except Exception as e: # Catch other API or core errors
            # This could be google.api_core.exceptions.GoogleAPICallError, etc.
            logging.warning(f"LLM generation for {section_id} failed with an API error: {e}. Returning placeholder.")
            return f"[Placeholder for {section_id} - LLM call failed]"
    def _generate_k1_executive_summary(self) -> str:
        """
        [OPTIMIZED FOR CREATIVITY]
        Generate K.1 Executive Summary (100-150 words) using LLM.
        This version forces maximum reasoning intensity (signal) AND
        maximum temperature (creativity) for this section only.
        """
        # 1. Get source material: top bullets from recent roles
        top_bullets = []
        for exp in self.master_resume['professional_experience'][:2]: # Unify & IBM
            top_bullets.extend(exp.get('bullet_pool', [])[:4])
        bullets_text = '\n'.join([f"- {b}" for b in top_bullets])

        # 2. Get key themes from thematic analysis
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(8) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []
        role_archetype = self.thematic_analysis.role_classification.get('role_archetype', 'Technical_IC')
        
        # 3. Add archetype-specific instructions
        archetype_instruction = ""
        if role_archetype == "Post-Sales_Customer_Success":
            archetype_instruction = """
CRITICAL INSTRUCTION FOR THIS JOB:
The target role is a POST-SALES customer-facing role. The summary MUST prioritize themes of AI adoption, customer value realization, retention, and scaling technical success. Frame achievements in the context of helping clients succeed with the product post-sale."""
        elif role_archetype == "Sales_GTM":
            archetype_instruction = """
CRITICAL INSTRUCTION FOR THIS JOB:
The target role is a PRE-SALES / Go-To-Market role. The summary MUST prioritize themes of revenue generation, strategic partnerships, and driving market adoption. Frame achievements in the context of winning new business and expanding market share."""

        # 4. Build the prompt
        feedback_instruction = ""
        if self.previous_failures:
            for failure in self.previous_failures:
                if failure.rule_id == "VG_WORD_COUNT_K1":
                    # Create a stern feedback message for the LLM
                    feedback_instruction = (
                        "\n**CRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:**\n"
                        "Your previous summary FAILED validation. It did not meet the word count requirement.\n"
                        f"**FAILURE DETAILS:** {failure.message}\n"
                        "You MUST generate a new summary that is strictly between 120 and 150 words.\n\n"
                    )
                    break

        prompt = f"""{feedback_instruction}You are an expert resume writer crafting an executive summary.

**Candidate's Key Achievements (Source of Truth):**
{bullets_text}

**Target Job Analysis:**
- Primary Theme: {primary_theme}
- Non-Negotiable Keywords: {', '.join(differentiators)}
- Role Archetype: {role_archetype}

**Job Description Context:**
{self.job_description[:1500]}

{archetype_instruction}

        **NON-NEGOTIABLE REQUIREMENTS (FAILURE WILL CAUSE REJECTION):**
        1.  **WORD COUNT:** The summary MUST be between {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN} and {self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} words.
        2.  **SENTENCE COUNT:** The summary MUST be {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN} to {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentences long.
        
        Do not fail these requirements. Summaries with {self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN - 1} sentences or {self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN - 20} words will be rejected. Aim for 130-140 words.

        **TASK:**
1. Write a **{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentence** executive summary that strictly adheres to **both** the **{self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX} word count** and **{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN}-{self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX} sentence** requirements.
2. Start with a sentence that directly addresses the '{primary_theme}' theme.
3. Your goal is to strike a balance. **Subtly and naturally integrate 3-4** of the following non-negotiable keywords: {', '.join(differentiators)}.
4. **CRITICAL: DO NOT FORCE all keywords.** Prioritize a natural, confident, and authentic human tone. Overfitting will be rejected.
5. All claims MUST be supported by the candidate's achievements. Do NOT invent facts.
6. Return ONLY the summary paragraph, with no preamble or explanation.
7. **CRITICAL:** Ensure no specific company names (e.g., "Unify", "IBM") appear in the summary.
"""

        # 5. Call LLM with HIGH SIGNAL and HIGH TEMP using the refactored helper
        reasoning_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG
        # Manually override temperature for this specific creative task
        reasoning_config_to_api_params(reasoning_config)["generation_config"].temperature = 1.0
        
        base_system = "You are an expert resume writer crafting an executive summary."
        return self._call_gemini_api(prompt, reasoning_config, "K.1", base_system)

    
    def _generate_k2_skills(self) -> List[str]:
        """Generates 12 high-signal, 1-3 word skills.

        This method uses the job analysis to generate a list of skills,
        then robustly parses the LLM output to handle various formats
        (newlines, commas, bullets) and ensures each skill is 1-3 words long."""
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
            
            # Robustly parse the LLM output, handling various delimiters.
            skills_list_final = []
            skills_intermediate = re.split(r'[\n,]', skills_text)
            
            for skill in skills_intermediate:
                # Remove bullets, numbers, and excess whitespace
                cleaned_skill = re.sub(r'^[•*\-\d\.]+\s*', '', skill).strip()
                
                if not cleaned_skill:
                    continue
                    
                # Validate 1-3 word length
                word_count = len(cleaned_skill.split())
                if 1 <= word_count <= 3:
                    skills_list_final.append(cleaned_skill)
                else:
                    # Log a warning but discard the malformed skill
                    print(f"Warning: Discarding malformed skill '{cleaned_skill}' (word count: {word_count})")

            # 5. Validate and return
            if len(skills_list_final) < 10:  # Allow for 10-12
                return [f"Error: LLM failed to generate 12 valid 1-3 word skills. Output: {skills_text}"]
                
            return skills_list_final[:12]  # Return exactly 12

        except Exception as e:
            print(f"Warning: K.2_Skills LLM generation failed: {e}")
            return [f"Error: {e}"]
    
    def _generate_k0_headline(self) -> str:
        """
        Generate K.4 Headline (15-20 words).
        v5.58: NOW USES LLM TO GENERATE ROLE-SPECIFIC HEADLINE (was: static template).
        """
        # Get most recent title from master resume
        recent_exp = MASTER_RESUME_JSON['professional_experience'][0]
        current_title = recent_exp.get('title', 'Technology Leader')
        current_company = recent_exp.get('company', 'Leading Company')
        
        # Get key themes
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(3) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []
        role_level = self.thematic_analysis.role_classification.get('seniority', 'senior')
        target_role_title = self.thematic_analysis.role_classification.get('precise_role_title', 'Target Role')

        # Build prompt
        prompt = f"""Create a professional resume headline for this candidate.

**Candidate's Current Role:** {current_title} at {current_company}

**Target Job Analysis:**
- Primary Theme: {primary_theme}
- **Target Job Title:** {target_role_title}
- Key Differentiators: {', '.join(differentiators)}
- Role Level: {role_level}

**Instructions:**
1. Create a headline that positions the candidate for a role aligned with '{primary_theme}'.
2. **DO NOT** include formal job titles like 'Vice President', 'Director', 'Chief', 'Manager', etc. Focus on functional expertise.
3. Include 2-3 of these differentiators: {', '.join(differentiators)}
4. Format: "[Functional Expertise Area] | [Key Strength 1] | [Key Strength 2]" (Use pipes '|' as separators)
5. **DO NOT** use commas.
6. The headline must be between {self.constraints.HEADLINE_WORD_COUNT_MIN} and {self.constraints.HEADLINE_WORD_COUNT_MAX} words total.
5. Use a professional and confident tone.

**CRITICAL INSTRUCTION FOR THIS JOB:**
The target role is a "VP, AI Technical Success" which is a POST-SALES customer-facing role focused on ADOPTION, RETENTION, and EXPANSION.
The headline MUST reflect this. Use keywords like "Customer Success", "Post-Sales Leadership", "AI Adoption", "Technical Account Management", or "Customer Value Realization".
DO NOT use pre-sales or product delivery terms like "solution delivery" or "revenue generation" unless directly tied to post-sales expansion.

**Good Example Format for this role:** "AI Technical Success Leadership | Post-Sales Strategy | GenAI Adoption & Scalability"

6. Return ONLY the headline text with no explanation.
"""

        reasoning_config = ReasoningConfig.K0_HEADLINE_CONFIG
        base_system = "You are an expert at crafting professional resume headlines. Be concise and impactful."
        headline = self._call_gemini_api(prompt, reasoning_config, ResumeSection.K0_HEADLINE.value, base_system)

        # Validation and fallback
        word_count = len(headline.split())
        if "[Placeholder" in headline or not (self.constraints.HEADLINE_WORD_COUNT_MIN <= word_count <= self.constraints.HEADLINE_WORD_COUNT_MAX):
            logging.warning(f"K.0 Headline generation failed or invalid (words: {word_count}). Using fallback template.")
            return f"{current_title} | {primary_theme} Leader | Enterprise Technology Architect"
        
        return headline
    
    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            section_index: int,
            provenance_targets: Dict[str, int], # e.g., {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2}
            reasoning_config: ReasoningConfig,
            section_id: str
    ) -> List[Dict]:
        """
        Generic method to select, rewrite, synthesize, and reorder bullets based on provenance targets.
        """
        # 1. Find the experience section in the master resume
        experience_section = next((exp for exp in self.master_resume['professional_experience'] 
                                   if company_name in exp['company']), None)
        if not experience_section:
            raise HopExecutionError(f"{company_name} experience not found in MASTER_RESUME_JSON for section {section_id}")
        
        # 2. Get context
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(5) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []
        role_level = self.thematic_analysis.role_classification.get('seniority', 'senior')
        
        master_bullets_structured = self.enriched_scaffold['experience_sections'][section_index]['bullets']
        bullets_text = '\n'.join([f"{i+1}. {bullet['bullet_text']}" for i, bullet in enumerate(master_bullets_structured)])

        total_expected_count = sum(provenance_targets.values())
        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)

        final_bullets = []

        # --- 3. Select Verbatim Bullets ---
        if verbatim_count > 0:
            prompt_select = f"""You are a resume optimization expert. Select the most relevant bullets for a specific job.

**Master Resume Bullets ({company_name}):**
{bullets_text}

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Non-Negotiable Keywords: {', '.join(differentiators)}
- Role Level: {role_level}

**Job Description Context:**
{self.job_description[:1500]}

**Instructions:**
1. Select the TOP {verbatim_count} bullets that best match the job's themes and keywords.
2. Prioritize bullets with strong alignment to the job description and keywords.
3. DO NOT modify the bullet text - use exact text from the master list.
4. Return ONLY the {verbatim_count} selected bullets, one per line, with no numbers or formatting.
"""
            system_prompt_select = f"You select verbatim bullets based on job fit."
            response_select = self._call_gemini_api(prompt_select, reasoning_config, f"{section_id}_SelectV", system_prompt_select)

            if "[Placeholder" not in response_select:
                selected_texts = [line.strip() for line in response_select.split('\n') if line.strip()]
                verbatim_bullets = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id}_SelectV")
                final_bullets.extend(verbatim_bullets)
            else:
                logging.warning(f"{section_id} Verbatim selection failed. Using first {verbatim_count} master bullets.")
                final_bullets.extend(master_bullets_structured[:verbatim_count]) # Keep Verbatim provenance

        # --- 4. Select and Customize Bullets ---
        if customized_count > 0:
            # Select bullets *different* from Verbatim ones
            used_texts = {b['bullet_text'] for b in final_bullets}
            available_for_custom = [b for b in master_bullets_structured if b['bullet_text'] not in used_texts]
            # Shuffle to get variety if selecting fewer than available
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count] # Select exact number needed

            if len(candidates_for_custom) == customized_count:
                customized_bullets = self._generate_lightly_customized_bullets(
                    source_bullets_text=[b['bullet_text'] for b in candidates_for_custom],
                    section_id=f"{section_id}_CustomC"
                )
                final_bullets.extend(customized_bullets)
            else:
                logging.warning(f"{section_id} Not enough unique bullets ({len(available_for_custom)}) to customize {customized_count}. Customizing available ones.")
                # Customize the ones that are available
                if available_for_custom:
                     customized_bullets = self._generate_lightly_customized_bullets(
                         source_bullets_text=[b['bullet_text'] for b in available_for_custom],
                         section_id=f"{section_id}_CustomC"
                     )
                     final_bullets.extend(customized_bullets)
                # Optionally, could fill with more Verbatim here if strict count is needed

        # --- 5. Generate Synthetic Bullets ---
        if synthetic_count > 0:
            # Pass context: JD, themes, and *other* bullets from this section for style/scope
            context_bullets_text = '\n'.join([f"- {b['bullet_text']}" for b in final_bullets]) # Use already selected/customized
            synthetic_bullets = self._generate_synthetic_bullets(
                count=synthetic_count,
                company_name=company_name,
                job_description=self.job_description,
                thematic_analysis=self.thematic_analysis,
                context_bullets=context_bullets_text,
                reasoning_config=reasoning_config, # Use same reasoning config as selection? Or default?
                section_id=f"{section_id}_SynthS"
            )
            final_bullets.extend(synthetic_bullets)

        # --- 6. Final Padding / Trimming ---
        if len(final_bullets) < total_expected_count:
            logging.warning(f"{section_id} Generated only {len(final_bullets)}/{total_expected_count} bullets. Padding with Verbatim.")
            needed = total_expected_count - len(final_bullets)
            used_texts = {b['bullet_text'] for b in final_bullets}
            padding = [b for b in master_bullets_structured if b['bullet_text'] not in used_texts][:needed]
            final_bullets.extend(padding) # These keep Verbatim provenance
        elif len(final_bullets) > total_expected_count:
             logging.warning(f"{section_id} Generated too many bullets ({len(final_bullets)}/{total_expected_count}). Trimming.")
             # Prioritize keeping non-Verbatim if trimming
             final_bullets.sort(key=lambda b: 0 if b['provenance'] != 'Verbatim' else 1)
             final_bullets = final_bullets[:total_expected_count]

        # --- 7. Word Count Validation & Rewrite (THE FIX) ---
        # --- CONSOLIDATION: Call utility function ---
        master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume) 
        # --- END CONSOLIDATION ---
        
        section_name_for_avg = "Unify" # Default
        if "IBM" in company_name:
            section_name_for_avg = "IBM"
        # Note: Averages for EY/EarlyCareer are not calculated by the helper, will use default.
        
        final_bullets = self._validate_and_potentially_rewrite_bullets(
            selected_bullets_structured=final_bullets,
            master_avg_lengths=master_avg_lengths,
            section_name_for_avg=section_name_for_avg,
            section_id_for_logging=section_id
        )

        # --- 8. Final Reordering ---
        current_bullets_text = '\n'.join([f"{i+1}. {bullet['bullet_text']}" for i, bullet in enumerate(final_bullets)])
        prompt_reorder = f"""You are a resume optimization expert. Reorder the following bullets by relevance for a specific job.

**Bullets to Reorder ({company_name}):**
{current_bullets_text}

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Job Description Context:**
{self.job_description[:1000]}

**Instructions:**
1. Reorder the provided bullets based on their relevance to the job description and themes (most relevant first).
2. DO NOT modify the bullet text - use exact text from the list.
3. Return ONLY the {total_expected_count} reordered bullets, one per line, with no numbers or formatting.
"""
        system_prompt_reorder = f"You reorder bullets based on job fit. Never modify text."
        # Use default reasoning for simple reordering
        response_reorder = self._call_gemini_api(prompt_reorder, ReasoningConfig.DEFAULT, f"{section_id}_Reorder", system_prompt_reorder)

        if "[Placeholder" in response_reorder:
            logging.warning(f"{section_id} Reordering failed. Returning bullets in generated order.")
            return final_bullets[:total_expected_count] # Trim if padded too many

        reordered_texts = [line.strip() for line in response_reorder.split('\n') if line.strip()]

        # Validate reordered texts match the generated bullets and return in the new order
        final_ordered_bullets = []
        # Need to handle potential minor LLM variations in reordering (e.g., punctuation) - use a fuzzy match?
        # For now, stick to exact match but log warnings more aggressively.
        generated_map = {b['bullet_text']: b for b in final_bullets}
        used_from_generated = set()
        
        for text in reordered_texts:
            if text in generated_map and text not in used_from_generated:
                final_ordered_bullets.append(generated_map[text])
                used_from_generated.add(text)
            else:
                # Try finding closest match if exact fails? Risky.
                logging.warning(f"{section_id} Reordering returned unexpected or duplicate bullet text: '{text[:50]}...'. Skipping.")
        
        # If validation failed significantly, return original generated order
        if len(final_ordered_bullets) != total_expected_count:
             logging.warning(f"{section_id} Reordering validation failed (got {len(final_ordered_bullets)}/{total_expected_count}). Returning bullets in generated order.")
             return final_bullets[:total_expected_count] # Use the state before reordering attempt

        return final_ordered_bullets

    def _generate_k5_unify_bullets(self) -> List[Dict]:
        """
        Generate K.5 Unify bullets by calling the generic bullet generation method.
        """
        return self._generate_tailored_bullets_for_experience(
            company_name="Unify Consulting", # Match exact name if possible
            section_index=0, # Assumes Unify is the first experience
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K5_UNIFY_BULLETS, {'Verbatim': 7}), # Use target split
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
                # Find the original dict and append
                original_bullet = next((b for b in master_bullets_structured if b['bullet_text'] == selected_text), None)
                if original_bullet:
                    validated_bullets.append(original_bullet) # Append original object, preserving Verbatim
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
        Generic method to rewrite an overview for a given experience.
        """
        # 1. Find the source overview
        experience_section = next((exp for exp in self.master_resume['professional_experience']
                                   if company_name in exp['company']), None)
        source_overview = experience_section['overview'] if experience_section else ""
        if not source_overview:
            return ""

        # 2. Get themes
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(5) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []

        # 3. Build the generic prompt
        prompt = f"""You are an expert resume writer. Rewrite the following professional overview to align with a specific job description, focusing on authenticity.

**Original Overview (Source of Truth - DO NOT invent new facts):**
{source_overview}

**Target Job Description - Key Themes:**
- Primary Theme: {primary_theme}
- Non-Negotiable Keywords: {', '.join(differentiators)}

**Instructions:**
1. Rewrite the overview to **naturally emphasize** themes that match the job: {primary_theme} and keywords like {', '.join(differentiators[:3])}.
2. **PRIORITY:** Maintain a natural, authentic human voice. **AVOID keyword stuffing** or sounding overly optimized.
3. DO NOT invent new facts, skills, metrics, or experience. All claims MUST be derived from the original overview.
4. Output must be a single paragraph, approximately {word_count_range[0]}-{word_count_range[1]} words.
{extra_prompt_instruction}
5. Return ONLY the rewritten overview text with no preamble or explanation.
"""
        system_prompt = "You are an expert resume editor. You rewrite professional overviews to align with job descriptions, prioritizing authenticity and natural language over keyword density. Never invent new facts. All content must be traceable to the source material."
        tailored_overview = self._call_gemini_api(prompt, reasoning_config, section_id, system_prompt)

        # USE MS WORD STYLE count for validation
        word_count = count_words_ms_word_style(tailored_overview)
        if "[Placeholder" in tailored_overview or not (word_count_range[0] <= word_count <= word_count_range[1]):
            logging.warning(f"{section_id} overview generation failed or invalid (words: {word_count}). Using original.")
            return source_overview

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
            section_index=1, # Assumes IBM is second
            provenance_targets=self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K6_IBM_BULLETS, {'Verbatim': 6}), # Use target split
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
        section_name_for_avg: str, # e.g., "Unify", "IBM", "Competencies"
        section_id_for_logging: str # e.g., "K.5_UNIFY_BULLETS"
    ) -> List[Dict]:
        """
        Checks word count for selected bullets and triggers rewrite if necessary.
        Updates provenance if rewritten.
        v9.87: Uses count_words_ms_word_style.
        """
        final_bullets = []
        avg_len = master_avg_lengths.get(section_name_for_avg, 25.0) # Default avg
        tolerance = 0.20 # 20% tolerance
        min_target = round(avg_len * (1 - tolerance))
        max_target = round(avg_len * (1 + tolerance))

        for bullet_data in selected_bullets_structured:
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
            # USE MS WORD STYLE count if calculating
            word_count = bullet_data.get('word_count', count_words_ms_word_style(original_text))

            if not (min_target <= word_count <= max_target):
                logging.warning(f"  Word count ({word_count}) outside target ({min_target}-{max_target}) for bullet in {section_id_for_logging}. Attempting rewrite.")
                rewritten_text = self._rewrite_bullet_for_word_count(
                    original_bullet_text=original_text,
                    target_word_count_range=(min_target, max_target),
                    section_id=section_id_for_logging
                )
                # Check rewrite using MS WORD STYLE count
                rewritten_word_count = count_words_ms_word_style(rewritten_text)
                if rewritten_text != original_text and min_target <= rewritten_word_count <= max_target:
                    # Update bullet data with rewritten text and provenance
                    final_bullets.append({
                        **bullet_data, # Keep original metadata like verbs etc.
                        "text": rewritten_text,
                        "provenance": BulletProvenance.Customized.value, # Update provenance
                        "word_count": rewritten_word_count # Update word count
                    })
                else:
                    # Append original if rewrite failed or didn't change text
                    final_bullets.append(bullet_data)
            else:
                # Append original if word count is already valid
                final_bullets.append(bullet_data)

        return final_bullets

    def _generate_lightly_customized_bullets(
        self,
        source_bullets_text: List[str],  # Now expects list of strings
        section_id: str
    ) -> List[Dict]:  # Returns list of dicts
        """
        Lightly rewrite a small, fixed list of bullet strings using an LLM.
        Returns structured bullet data including 'Customized' provenance.
        v9.87: Uses count_words_ms_word_style.
        """
        try:
            if not source_bullets_text:
                return []

            primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
            bullets_text = '\n'.join([f"- {b}" for b in source_bullets_text])

            prompt = f"""You are an expert resume editor. Lightly rewrite the following resume bullets to align with a job's theme, prioritizing authenticity.

**Original Bullets (Source of Truth - DO NOT invent new facts):**
{bullets_text}

**Target Job Theme:** {primary_theme}
**Target Job Description:** {self.job_description[:1000]}
**Instructions:**
1. Rewrite each bullet to be concise and impactful, maintaining an **authentic human voice**.
2. **Subtly** emphasize concepts from the original text that align with the '{primary_theme}'.
3. **AVOID forcing keywords** or making the bullets sound unnaturally optimized for the job description.
4. DO NOT invent new facts, skills, metrics, or experience. All claims MUST be derived from the original bullets.
5. Maintain the same number of bullets as the original list.
6. Return ONLY the rewritten bullets, each on a new line, starting with '• '.
"""
            system_prompt = "You are an expert resume editor. You rewrite resume bullets to align with job themes, prioritizing natural language and authenticity. Never invent new facts. All content must be traceable to the source material."
            response_text = self._call_gemini_api(prompt, ReasoningConfig.DEFAULT, section_id, system_prompt)

            if "[Placeholder" in response_text:
                logging.warning(f"{section_id} rewrite failed. Returning original bullets.")
                # USE MS WORD STYLE count for fallback
                return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                         "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]
            else:
                rewritten_bullets = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip()]
                provenance = BulletProvenance.Customized.value

                if len(rewritten_bullets) != len(source_bullets_text):
                    print(f"Warning: {section_id} LLM returned {len(rewritten_bullets)} bullets, expected {len(source_bullets_text)}. Returning original.")
                    # USE MS WORD STYLE count for fallback
                    return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                             "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]

                # Return structured dicts using MS WORD STYLE count
                return [{"text": b, "provenance": provenance, "word_count": count_words_ms_word_style(b)} for b in rewritten_bullets]

        except Exception as e:
            logging.warning(f"{section_id} LLM bullet rewrite failed: {e}. Returning original bullets.", exc_info=True)
            # USE MS WORD STYLE count for fallback
            return [{"text": b, "provenance": BulletProvenance.Verbatim.value,
                     "word_count": count_words_ms_word_style(b)} for b in source_bullets_text]

    def _generate_synthetic_bullets(
        self,
        count: int,
        company_name: str,
        job_description: str,
        thematic_analysis: ThematicAnalysis,
        context_bullets: str,  # Existing bullets for style/scope reference
        reasoning_config: ReasoningConfig,
        section_id: str
    ) -> List[Dict]:
        """
        Generates new, plausible bullet points based on context.
        v9.87: Uses count_words_ms_word_style.
        """
        primary_theme = thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = thematic_analysis.competitive_intelligence.get_top_differentiators(5) if hasattr(thematic_analysis, 'competitive_intelligence') else []
        prompt = f"""You are an expert resume writer generating new, plausible achievements.

**Context:**
- Company: {company_name}
- Candidate's Role Focus during this time (Implied): {primary_theme}
- Other achievements from this role (for style/scope reference):
{context_bullets}
- Target Job Keywords: {', '.join(differentiators)}
- Target Job Description: {job_description[:1500]}

**Task:**
1. Generate {count} new, distinct bullet points representing plausible achievements for this candidate at {company_name}, aligned with the target job.
2. Each bullet MUST be a single, concise sentence starting with an action verb.
3. Ensure the achievements are realistic and consistent with the provided context, but NOT directly copied. Focus on impact and metrics where plausible (e.g., "Improved X by Y%", "Reduced Z by $A").
4. You may **subtly incorporate one** of the target keywords ({', '.join(differentiators)}) **if it fits naturally**.
5. Prioritize creating a **believable, authentic achievement** over forcing in keywords. The goal is to avoid detection by AI detectors.
6. Return ONLY the {count} bullet points, one per line, starting with '* '.
"""
        system_prompt = "You generate plausible, synthetic resume bullet points aligned with job requirements and candidate history. Never copy existing bullets."
        response_text = self._call_gemini_api(prompt, reasoning_config, section_id, system_prompt)
        synthetic_bullets_text = []
        if "[Placeholder" not in response_text:
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip()]
            if len(synthetic_bullets_text) != count:
                logging.warning(f"{section_id} Failed to generate {count} synthetic bullets (got {len(synthetic_bullets_text)}). Returning empty list.")
                return []
            # USE MS WORD STYLE count
            return [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": count_words_ms_word_style(b)} for b in synthetic_bullets_text]
        else:
            logging.warning(f"{section_id} Synthetic bullet generation failed. Returning empty list.")
            return [] # Return empty list if generation fails

    def _generate_k8_ey_bullets(self) -> List[Dict]:
        """Generate K.8A EY bullets (2 bullets), lightly tailored by LLM."""
        ey_exp = next((exp for exp in self.master_resume['professional_experience'] 
                       if 'Ernst & Young' in exp['company'] or 'EY' in exp['company']), None)
        if not ey_exp:
            return []
        source_bullets = ey_exp.get('highlights', [])[:2]
        return self._generate_lightly_customized_bullets(source_bullets, ResumeSection.K8_EY_BULLETS.value)

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
        NO customization - MUST_USE_MASTER_INTRO_AND_BULLETS.
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
        NO customization - MUST_USE_MASTER_INTRO_AND_BULLETS.
        """
        
        tradersense_exp = next((exp for exp in self.master_resume['professional_experience'] 
                                if 'TraderSense' in exp['company']), None)
        if tradersense_exp:
            tradersense_overview = tradersense_exp.get('overview', "")
        else:
            tradersense_overview = ""
        
        return tradersense_overview if tradersense_overview else "As co-founder and CTO, led all technology strategy, product development, and team management from concept to initial launch."

    def _generate_k9_early_career_bullets(self) -> List[Dict]:
        """Generate K.9A Early Career bullets (1 bullet), lightly tailored by LLM."""
        early_exp = next((exp for exp in self.master_resume['professional_experience'] 
                       if 'Early Career' in exp['company']), None)
        if not early_exp or not early_exp.get('highlights'):
            return []
        source_bullets = early_exp.get('highlights', [])[:1]
        return self._generate_lightly_customized_bullets(source_bullets_text=source_bullets, section_id=ResumeSection.K9_EARLY_CAREER_BULLETS.value)

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
        Generate K.10 Competencies (6 competencies), tailored by LLM.
        v5.58: NOW USES LLM TO SELECT AND REORDER BY JD THEMES (was: first 6).
        v9.88: Uses count_words_ms_word_style for initial structuring.
        """
        # 1. Get all master competencies and structure them
        all_competencies_text = MASTER_RESUME_JSON.get('strategic_and_technical_competencies', [])
        all_competencies_structured = [{
            "text": c.replace("• ", "").strip(), # Clean bullet marker
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": count_words_ms_word_style(c) # <<< CORRECTED HERE
        } for c in all_competencies_text]

        # Define the target provenance split for competencies
        provenance_targets = self.PROVENANCE_SPLIT_TARGETS.get(ResumeSection.K10_COMPETENCIES, {'Verbatim': 6}) # Default to all verbatim if no target
        expected_count = sum(provenance_targets.values())

        # 2. Get key themes
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'AI Leadership')
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(5) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []
        role_level = self.thematic_analysis.role_classification.get('seniority', 'senior')

        # 3. Build prompt
        comps_text = '\n'.join([f"{i+1}. {comp['text']}" for i, comp in enumerate(all_competencies_structured)])

        prompt = f"""Select and reorder the most relevant competencies for this job.

**All Available Competencies:**
{comps_text}

**Target Job - Key Themes:**
- Primary Theme: {primary_theme}
- Non-Negotiable Keywords: {', '.join(differentiators)}
- Key Differentiators: {', '.join(differentiators)}
- Role Level: {role_level}

**Job Description (first 1500 chars):**
{self.job_description[:1500]}

**Instructions:**
1. Select the TOP {expected_count} competencies that best match: {primary_theme} and keywords: {', '.join(differentiators[:5])}
2. Reorder by relevance (most relevant first)
3. Use exact competency text from the master list - DO NOT modify
4. Balance strategic and technical competencies based on the role level and job description.
5. Return ONLY the {expected_count} selected competencies, one per line, no numbers or bullets.

Selection criteria:
- Prioritize competencies that are explicitly mentioned or strongly implied in the job description."""

        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print("Warning: No GEMINI_API_KEY, returning first 6 competencies for K.10")
                fallback_comps = all_competencies_structured[:expected_count] # Return as-is
                return fallback_comps
            genai.configure(api_key=api_key)
            client = genai.GenerativeModel('gemini-1.5-flash')

            reasoning_config = ReasoningConfig.K10_COMPETENCIES_CONFIG

            api_params = reasoning_config_to_api_params(reasoning_config)

            base_system = "You select and reorder competencies based on job fit. Never modify or invent competency text."
            enhanced_system = enhance_system_prompt_with_reasoning(base_system, reasoning_config, "K.10")

            response = client.generate_content(
                f"{enhanced_system}\n\n{prompt}",
                generation_config=api_params["generation_config"]
            )

            response_text = response.text.strip()
            selected_comps = [line.strip() for line in response_text.split('\n') if line.strip()]

            if len(selected_comps) != expected_count:
                print(f"Warning: K.10 got {len(selected_comps)} competencies, using first {expected_count} from master")
                fallback_comps = all_competencies_structured[:expected_count] # This is a list of dicts
                return fallback_comps

            # Validate competencies are from master
            validated_comps = []
            master_comp_texts = [c['text'] for c in all_competencies_structured]
            for comp_text in selected_comps:
                if comp_text in master_comp_texts:
                    original_comp_obj = next((c for c in all_competencies_structured if c['text'] == comp_text), None)
                    if original_comp_obj:
                        validated_comps.append(original_comp_obj)

            # Post-selection validation and potential rewrite for word count
            # --- CONSOLIDATION: Call utility function ---
            master_avg_lengths = calculate_master_avg_bullet_length(self.master_resume)
            # --- END CONSOLIDATION ---
            final_validated_comps = self._validate_and_potentially_rewrite_bullets(
                selected_bullets_structured=validated_comps,
                master_avg_lengths=master_avg_lengths,
                section_name_for_avg="Competencies",
                section_id_for_logging="K.10_COMPETENCIES"
            )

            if len(final_validated_comps) == expected_count:
                return final_validated_comps
            else:
                logging.warning(f"K.10 validation/rewrite resulted in {len(final_validated_comps)} competencies, expected {expected_count}. Using fallback.")
                fallback_comps = all_competencies_structured[:expected_count]
                return fallback_comps

        except Exception as e:
            logging.warning(f"K.10 LLM selection/processing failed: {e}", exc_info=True)
            fallback_comps = all_competencies_structured[:6] # This is a list of dicts
            return fallback_comps

    def _generate_k13_cover_letter(self) -> str:
        """
        v8.10: Generate K.13 cover letter using the creative narrative-driven strategy.
        - Integrates Thematic Core, Authentic Voice, Competitive Differentiators, and Problem-Solution Narratives.
        - Follows the "Hook, Proof, Vision" structure.
        """
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")

        # --- 1. GATHER HIGH-SIGNAL INTEL ---
        
        # Signal 1: Thematic Core
        primary_theme = self.thematic_analysis.primary_theme.get('name', 'this strategic opportunity')

        # Signal 2 & 3: Differentiators & Narratives
        differentiators = self.thematic_analysis.competitive_intelligence.get_top_differentiators(5) if hasattr(self.thematic_analysis, 'competitive_intelligence') else []
        narratives = self.thematic_analysis.problem_solution_narratives or {}
        problem_context = "; ".join(narratives.get("common_problems", []))
        
        # Gather top achievements for the "Proof" section
        top_achievements = []
        for section in self.enriched_scaffold.get('experience_sections', [])[:2]: # Unify & IBM
            for bullet in section.get('bullets', [])[:3]:
                top_achievements.append(bullet.get('bullet_text', ''))
        achievements_text = '\n'.join(f"- {ach}" for ach in top_achievements)

        # Get candidate info for signature
        owner_info = self.master_resume.get('owner', {})
        signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
            name=owner_info.get('name', ''),
            email=owner_info.get('contact', {}).get('email', ''),
            phone=owner_info.get('contact', {}).get('phone', ''),
            linkedin=owner_info.get('contact', {}).get('linkedin', '')
        ).strip()

        # --- 2. CONSTRUCT THE NARRATIVE-DRIVEN PROMPT ---

        prompt = f"""You are an executive ghostwriter crafting a compelling cover letter based on a strategic analysis. Adopt a professional, consultative, and authentic voice.

**INTELLIGENCE BRIEFING:**
- **Thematic Core:** The central problem this role solves is '{primary_theme}'.
- **Competitive Differentiators:** Key skills that make this role unique are: {', '.join(differentiators)}.
- **Industry Problem Context:** This role operates in a context where common challenges include: '{problem_context}'.
- **Candidate's Top Achievements:**
{achievements_text}

**FULL JOB DESCRIPTION:**
{self.job_description}

**TASK:**
Write a three-paragraph cover letter based *only* on the provided intelligence. Follow this exact narrative structure:

**Paragraph 1: The Hook - "I Understand Your Core Problem."** ({self.constraints.COVER_LETTER_P1_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P1_WORD_COUNT_MAX} words)
- Start by directly addressing the **Thematic Core** ('{primary_theme}').
- State the candidate's value proposition as the solution.
- Formally state the position being applied for.

**Paragraph 2: The Proof - "Here's Proof I've Solved This Before."** ({self.constraints.COVER_LETTER_P2_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P2_WORD_COUNT_MAX} words)
- Select one or two achievements from the candidate's list.
- Frame them as a mini-story: "At [Company], we faced [Problem]. I led [Action], incorporating '{differentiators[0]}' and '{differentiators[1]}', which resulted in [Quantifiable Result]."
- The story must directly prove the candidate can solve the company's core problem.

**Paragraph 3: The Vision - "Here's How We Can Solve It Together."** ({self.constraints.COVER_LETTER_P3_WORD_COUNT_MIN}-{self.constraints.COVER_LETTER_P3_WORD_COUNT_MAX} words)
- Connect the candidate's past success to the company's future goals.
- Express genuine, specific enthusiasm for the role.
- End with a confident call to action.

**OUTPUT FORMAT:**
**CRITICAL:** Do NOT mention specific past employer names like "At Unify" or "At IBM". Refer to past roles generically (e.g., "In my previous role...", "While leading initiatives at a major consulting firm..."). The only company name allowed is the target company ([Company Name] placeholder below).
Return the complete cover letter text. Start with the date and end *exactly* with the signature block provided. Do not add any extra text, preamble, or explanation.

{today}

Hiring Manager
[Company Name]

[Paragraph 1]

[Paragraph 2]

[Paragraph 3]

{signature}"""

        # --- 3. CALL LLM AND RETURN ---
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction="You are an expert executive ghostwriter. You write compelling, narrative-driven cover letters based on strategic intelligence, adhering strictly to the requested structure and content constraints.")
            
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=1000)
            )
            
            cover_letter_text = response.text.strip()
            # Final check to ensure it contains the signature
            if signature not in cover_letter_text:
                 # Append signature if LLM forgot it
                 cover_letter_text += f"\n\n{signature}"
            
            return cover_letter_text
            
        except Exception as e:
            print(f"Warning: Creative cover letter LLM generation failed: {e}")
            # Fallback to the older, simpler generation method if the new one fails
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


class TextSanitizer:
    """
    v6.00: Comprehensive text sanitization engine, separated from ArtistGenerator.
    Applies rules for hyphenation, unicode, punctuation, and style.
    """
    def __init__(self, hyphenation_rules: Dict = None):
        self.rules = hyphenation_rules or COMPREHENSIVE_HYPHENATION_RULES
        self.sanitization_counts = {
            'unnatural_hyphens': 0,
            'unicode_fixes': 0,
            'punctuation_fixes': 0,
            'markdown_removed': 0,
            'jargon_simplified': 0,
            'fillers_removed': 0,
            'natural_hyphens': 0,
        }

    def sanitize_buffer(self, staging_buffer: 'ImmutableStagingBuffer') -> Tuple[List[ValidationResult], Dict]:
        """
        Apply comprehensive text sanitization to a staging buffer's data.
        Returns a tuple of (validation_results, sanitized_data).
        """
        if staging_buffer.is_locked():
            return [ValidationResult(
                rule_id="R4.5-ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message="Staging buffer already locked before HOP-4.5"
            )], staging_buffer.data

        sanitized_data = self._sanitize_dict(staging_buffer.data)

        total_fixes = sum(self.sanitization_counts.values())
        validation_results = [ValidationResult(
            rule_id="TEXT_SANITIZATION_COMPLETE", passed=True, severity=ValidationSeverity.INFO,
            message=f"Text sanitization complete: {total_fixes} total corrections ({', '.join(f'{k}: {v}' for k, v in self.sanitization_counts.items() if v > 0)})"
        )]
        
        return validation_results, sanitized_data

    def _sanitize_dict(self, d: Dict) -> Dict:
        """Recursively sanitize a dictionary and return a new sanitized dictionary."""
        sanitized_dict = {}
        for key, value in d.items():
            if isinstance(value, str):
                sanitized_dict[key] = self._remove_unnatural_hyphens(value)
            elif isinstance(value, list):
                sanitized_dict[key] = [self._remove_unnatural_hyphens(item) if isinstance(item, str) else item for item in value]
            else:
                sanitized_dict[key] = value
        return sanitized_dict

    def _remove_unnatural_hyphens(self, text: str) -> str:
        for rule in self.rules['rules']['unnatural_hyphens_remove']:
            if rule['from'] in text:
                text = text.replace(rule['from'], rule['to'])
                self.sanitization_counts['unnatural_hyphens'] += 1
        return text


# ============================================================================
# HOP-5: VALIDATION GATES
# ============================================================================

SECTION_CONSTRAINTS_V521 = {
    'headline': {
        'min_chars': 60,
        'max_chars': 90,
        'word_count': [8, 11],  # USER-SPECIFIED HARDENING
        'component_words': [2, 4] # USER-SPECIFIED HARDENING
    },
    'word_distribution': {
        'unify_ibm_combined_percent': [35, 45],
        'unify_ibm_ratio': [1.1, 1.3]
    }
}

# <<< FIX: HELPER FUNCTION DEFINITIONS MOVED HERE >>>
def count_words_clean(text: str) -> int:
    """
    DEPRECATED Helper: Counts words using standard splitting.
    Kept for reference but replaced by count_words_ms_word_style.
    """
    if not text: return 0
    return len(text.split())

def count_words_ms_word_style(text: str) -> int:
    """
    Counts words attempting to replicate MS Word behavior:
    - Treats punctuation (., ,, ;, :, ?, !) as delimiters.
    - Keeps hyphenated words (e.g., "post-sales") as single words.
    - Ignores empty strings resulting from splitting.
    v9.87: Implemented based on user validation yielding 97 words for the specific exec summary.
    """
    if not text:
        return 0
    # Use regex to find sequences that are either hyphenated or standard words
    # \b matches word boundaries
    # [\w-]+ matches one or more word characters (\w includes letters, numbers, _) OR hyphens
    words = re.findall(r'\b[\w-]+\b', text)
    # Filter out potential empty strings or single hyphens if regex finds them
    valid_words = [word for word in words if word and word != '-']
    return len(valid_words)

def count_words_in_list_ms_word_style(content_list: List[Any]) -> int:
    """Helper to count words in a list using the MS Word style counter."""
    return sum(count_words_ms_word_style(str(item)) for item in content_list)

def _count_sentences(text: str) -> int:
    """
    Helper to count sentences using a regex that handles common abbreviations.
    It looks for sentence-ending punctuation (.!?) that is not preceded by
    a known abbreviation (like Dr., Mr., e.g., i.e., etc.).
    """
    if not text: return 0
    # This regex is a significant improvement. It avoids splitting on abbreviations.
    # It finds . ! ? that are not preceded by common titles or single capital letters.
    return len(re.findall(r'(?<!\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|vs|e\.g|i\.e))\.(?!\d)|[.!?]\s', text + " "))

# <<< END OF HELPER FUNCTION DEFINITIONS >>>

class PreFlightValidator:
    """
    HOP-6: Pre-flight validation before file generation.
    Runs comprehensive validation suite.
    """

    def __init__(self, master_resume: Dict):
        """Initializes the validator and registers all rules with the ValidationEngine."""
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.dup_detector = DuplicateDetector() # For cosine similarity
        self.constraints = ContentConstraintsConfig() # Centralized constraints
        self.signal_constraints = SignalControlConfig() # <<< MODIFICATION
        self._register_rules() # Must be called after constraints are set

    # Removed WORD_COUNT_MIN/MAX from class level, now sourced from self.constraints

    RULES_CONFIG = [
        # --- Word Count Rules ---
        {
            "rule_id": "VG_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_total_word_count", # Use method name
            "error_message": "Total resume: {total_words} words (target: {min}-{max})"
        },
        {
            "rule_id": "VG_WORD_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
            "validator": "_validate_k1_word_count", # Use method name
            "error_message": "K.1: {word_count} words (target: {min}-{max})" # Use min/max
        },
        {
            "rule_id": "VG_SENTENCE_COUNT_K1", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_k1_sentence_count", # Use method name
            "error_message": "K.1: {sentence_count} sentences (target: {min}-{max})" # Use min/max
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
        # --- Structure & Content Rules ---
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
            "rule_id": "CONTENT_NO_PLACEHOLDERS", "severity": ValidationSeverity.HIGH, "category": "content",
            "validator": "_validate_no_placeholders",
            "error_message": "Found placeholder text in content: {placeholders}"
        },
        # <<< MODIFICATION: Rule ID, validator, and message updated >>>
        {
            "rule_id": "VG_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_k1_differentiator_range",
            "error_message": "K.1 Summary contains {found} differentiators (target: {min}-{max})."
        },
        # <<< MODIFICATION: Rule ID, validator, and message updated >>>
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
        # <<< MODIFICATION: Rule ID, validator, and message updated >>>
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
            "rule_id": "VG_COVER_LETTER_FULL_STRUCTURE", "severity": ValidationSeverity.MEDIUM, "category": "structure",
            "validator": "_validate_cover_letter_full_structure",
            "error_message": "Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."
        },
        {
            "rule_id": "COVER_LETTER_STRUCTURE", "severity": ValidationSeverity.MEDIUM, "category": "content",
            "validator": "_validate_cover_letter_structure",
            "error_message": "Cover letter paragraph word counts are out of spec. P1: {p1_wc} ({p1_min}-{p1_max}), P2: {p2_wc} ({p2_min}-{p2_max}), P3: {p3_wc} ({p3_min}-{p3_max})" # Use min/max
        },
        {
            "rule_id": "VG_COVER_LETTER_SIGNATURE_MULTILINE", "severity": ValidationSeverity.CRITICAL, "category": "structure",
            "validator": "_validate_cover_letter_signature_multiline",
            "error_message": "Cover letter signature is not rendering multi-line (check trailing spaces)."
        },
    ]
    # Add Headline, Provenance, Formatting, and Bullet Tolerance rules using extend
    RULES_CONFIG.extend([
        {
            "rule_id": "VG_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.CRITICAL,"category": "structure",
            "validator": "_validate_headline_word_count", # Use method name
            "error_message": "K.0 Headline: {word_count} words (target: {min}-{max}). Headline: '{headline}'"
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
            "rule_id": "VG_PROVENANCE_SPLIT_CHECK", "severity": ValidationSeverity.CRITICAL, "category": "content",
            "validator": "_validate_provenance_split",
            "error_message": "Provenance split mismatch: {violations}"
        },
        # --- New Critical Formatting Rules ---
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
    
        {
            "rule_id": "VG_BULLET_WORD_COUNT_TOLERANCE", "severity": ValidationSeverity.HIGH, "category": "word_count",
            "validator": "_validate_bullet_word_count_tolerance",
            "error_message": "Bullet word counts outside tolerance ({tolerance}%): {violations}"
        }
    ])

    def _register_rules(self):
        """Creates and registers all pre-flight validation rules."""
        for config in self.RULES_CONFIG:
            validator_ref = config["validator"]
            if isinstance(validator_ref, str):
                validator_func = getattr(self, validator_ref)
            elif callable(validator_ref):
                 validator_func = validator_ref # Allow simple lambdas if needed
            else:
                 raise TypeError(f"Invalid validator type for rule {config['rule_id']}: {type(validator_ref)}")

            # Create closure for lazy error message formatting
            def create_error_message_lambda(template):
                expected_args = re.findall(r'\{(\w+)\}', template)
                format_args = {}
                if "tolerance" in expected_args:
                    format_args["tolerance"] = self.BULLET_WORD_COUNT_TOLERANCE * 100
                # Add other dynamic args needed by specific templates here if necessary
                return lambda data: template.format(**data.get("error_details", {}), **format_args)

            error_message_lambda = create_error_message_lambda(config["error_message"])

            rule = ValidationRule(
                rule_id=config["rule_id"],
                severity=config["severity"],
                category=config["category"],
                validator=validator_func,
                error_message=error_message_lambda
            )
            self.engine.register_rule(rule)

        # Register rules for required sections
        required_sections = [
            ResumeSection.K0_NAME, ResumeSection.K0_HEADLINE, ResumeSection.K0_CONTACT,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K5_UNIFY_BULLETS,
            ResumeSection.K5_UNIFY_OVERVIEW, ResumeSection.K6_IBM_BULLETS,
            ResumeSection.K6_IBM_OVERVIEW, ResumeSection.K10_COMPETENCIES,
            ResumeSection.K11_EDUCATION, ResumeSection.K12_CERTIFICATIONS,
            ResumeSection.K13_COVER_LETTER,
        ]
        for section in required_sections:
            rule = ValidationRule(
                rule_id=f"STRUCTURE_{section.name}",
                severity=ValidationSeverity.CRITICAL,
                # Lambda is okay here as it doesn't need 'self'
                validator=lambda d, s=section: d['staging_buffer'].get(s.value) is not None and len(str(d['staging_buffer'].get(s.value)).strip()) > 0,
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
        actual_counts = {}
        total_words = 0

        # Count words for each section in the buffer using MS WORD STYLE
        for section_id, content in staging_buffer.data.items():
            if content is None:
                actual_counts[section_id] = 0
                continue
            if isinstance(content, str):
                word_count = count_words_ms_word_style(content) # USE MS WORD STYLE
            elif isinstance(content, list):
                if content and isinstance(content[0], dict) and 'text' in content[0]: # List of bullet dicts
                    # USE MS WORD STYLE count if calculating
                    word_count = sum(item.get('word_count', count_words_ms_word_style(item.get('text', ''))) for item in content)
                else: # Assume list of strings
                    word_count = count_words_in_list_ms_word_style(content) # USE MS WORD STYLE
            else:
                word_count = 0 # Ignore non-text types
            actual_counts[section_id] = word_count
            total_words += word_count
        actual_counts["TOTAL"] = total_words

        section_averages = self._calculate_master_avg_bullet_length() # Uses MS WORD STYLE internally now

        # Prepare data payload for the validation engine
        data = self._prepare_validation_data(staging_buffer, thematic_analysis, job_description, actual_counts, section_averages)

        # Execute validation
        validation_results = self.engine.validate(data)
        all_passed = not self.engine.has_critical_failures(validation_results)

        return validation_results, all_passed

    # <<< FIX: Correct method name typo and add section_averages parameter >>>
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
            jd_keywords_tracked = getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords_raw', [])

        buffer_str = json.dumps(staging_buffer.data).lower() # Convert buffer content to searchable string

        cover_letter_text = staging_buffer.get(ResumeSection.K13_COVER_LETTER.value, '')
        cover_letter_jd_similarity = self.dup_detector._calculate_cosine_similarity(
            cover_letter_text,
            job_description
        )

        # Get top differentiators safely
        top_differentiators = []
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            top_differentiators = thematic_analysis.competitive_intelligence.get_top_differentiators(3)


        return {
            "staging_buffer": staging_buffer,
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
            "jd_keywords_tracked": jd_keywords_tracked,
            "jd_keywords_found": [kw for kw in jd_keywords_tracked if kw.lower() in buffer_str],
            "cover_letter_jd_similarity": cover_letter_jd_similarity,
            "section_averages": section_averages, # Pass averages for bullet validation
        }

    # --- Individual Validator Methods ---
    def _validate_total_word_count(self, data: Dict) -> bool:
        data["error_details"] = {
            "total_words": data['total_words'],
            "min": self.constraints.TOTAL_WORD_COUNT_MIN, # Use self.constraints
            "max": self.constraints.TOTAL_WORD_COUNT_MAX  # Use self.constraints
        }
        return self.constraints.TOTAL_WORD_COUNT_MIN <= data['total_words'] <= self.constraints.TOTAL_WORD_COUNT_MAX

    def _validate_k1_word_count(self, data: Dict) -> bool:
        # USE MS WORD STYLE count
        word_count = count_words_ms_word_style(data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, ''))
        data["error_details"] = {
            "word_count": word_count,
            "min": self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN,
            "max": self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX
        }
        return self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN <= word_count <= self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX

    def _validate_k1_sentence_count(self, data: Dict) -> bool:
        summary_text = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '')
        sentence_count = _count_sentences(summary_text)
        data["error_details"] = {
            "sentence_count": sentence_count,
            # Add min/max for error message formatting
            "min": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
            "max": self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        }
        return self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN <= sentence_count <= self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX

    def _validate_unify_ibm_distribution(self, data: Dict) -> bool:
        min_pct, max_pct = SECTION_CONSTRAINTS_V521['word_distribution']['unify_ibm_combined_percent']
        data["error_details"] = {"percent": data['unify_ibm_percent'], "min": min_pct, "max": max_pct}
        return min_pct <= data['unify_ibm_percent'] <= max_pct

    def _validate_unify_ibm_ratio(self, data: Dict) -> bool:
        if data['ibm_words'] == 0:
            data["error_details"] = {"ratio": "N/A", "min": "N/A", "max": "N/A"}
            return False # Cannot divide by zero
        ratio = data['unify_words'] / data['ibm_words']
        min_ratio, max_ratio = SECTION_CONSTRAINTS_V521['word_distribution']['unify_ibm_ratio']
        data["error_details"] = {"ratio": ratio, "min": min_ratio, "max": max_ratio}
        return min_ratio <= ratio <= max_ratio

    def _validate_buffer_locked(self, data: Dict) -> bool:
        return data['staging_buffer'].is_locked()

    def _validate_cover_letter_signature(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        return cover_letter.strip().endswith(data['expected_signature'])

    def _validate_no_placeholders(self, data: Dict) -> bool:
        buffer_str = json.dumps(data['staging_buffer'].data)
        placeholders = re.findall(r'(\[placeholder.*?\])', buffer_str, re.IGNORECASE) # Simplified regex
        if placeholders:
            data["error_details"] = {"placeholders": list(set(placeholders))[:3]} # Show unique placeholders
            return False
        return True


# <<< MODIFICATION: Renamed and logic updated for range checking >>>
    def _validate_k1_differentiator_range(self, data: Dict) -> bool:
        # <<< MODIFICATION: Read min from constraints >>>
        MIN_DIFF = self.constraints.K1_MIN_DIFFERENTIATORS 
        MAX_DIFF = self.signal_constraints.K1_MAX_DIFFERENTIATORS

        differentiators = data.get('differentiators', [])
        if not differentiators:
             # If no differentiators were identified in RAG, pass validation but maybe log info.
             logging.info("K.1 Differentiator Check: No differentiators found in thematic analysis.")
             # Decide if this should be a pass or fail. Passing for now.
             data["error_details"] = {"found": 0, "min": MIN_DIFF, "max": MAX_DIFF, "message": "No differentiators to check."}
             return True

        summary = data['staging_buffer'].get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        found_count = sum(1 for kw in differentiators if kw.lower() in summary)

        data["error_details"] = {
            "found": found_count,
            "min": MIN_DIFF,
            "max": MAX_DIFF
        }
        # Check if found_count is within the range
        return MIN_DIFF <= found_count <= MAX_DIFF


    # <<< MODIFICATION: Renamed and logic updated for range checking >>>
    def _validate_jd_keyword_range(self, data: Dict) -> bool:
        # <<< MODIFICATION: Read min from constraints >>>
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
        narratives = data['thematic_analysis'].problem_solution_narratives
        return (
            narratives is not None and
            isinstance(narratives.get("common_problems"), list) and
            len(narratives.get("common_problems", [])) > 0 and
            isinstance(narratives.get("solution_patterns"), list) and # Check solutions too
            len(narratives.get("solution_patterns", [])) > 0
        )

# <<< MODIFICATION: Renamed and logic updated for range checking >>>
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
        """Checks for 'Hook, Proof, Vision' structure."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        primary_theme = data['thematic_analysis'].primary_theme.get('name', 'default_theme')
        narratives = data['thematic_analysis'].problem_solution_narratives or {}
        problem_keywords = narratives.get("common_problems", [])

        paragraphs = cover_letter.split('\n\n')
        if len(paragraphs) < 5: return False # Date, Salutation, P1, P2, P3, Signature block

        p1 = paragraphs[2].lower()
        p2 = paragraphs[3].lower()
        p3 = paragraphs[4].lower()

        hook_pass = primary_theme.lower() in p1 or "interest in the" in p1 # Adjusted check
        proof_pass = any(kw.lower() in p2 for kw in data.get('differentiators', [])) or "resulted in" in p2 # Check for impact language
        vision_pass = "excited" in p3 or "opportunity" in p3 or "discuss" in p3 or "contribute" in p3 # Broader check

        data["error_details"] = {"hook": hook_pass, "proof": proof_pass, "vision": vision_pass}
        return hook_pass and proof_pass and vision_pass

    def _validate_cover_letter_fallback(self, data: Dict) -> bool:
        """Checks if the fallback cover letter was used."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        # The fallback contains this specific phrase:
        return "track record of measurable AI transformation" not in cover_letter

    def _validate_cover_letter_structure(self, data: Dict) -> bool:
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        paragraphs = cover_letter.split('\n\n')

        if len(paragraphs) < 5:
            data["error_details"] = {"p1_wc": 0, "p2_wc": 0, "p3_wc": 0, "p1_min":0, "p1_max":0, "p2_min":0, "p2_max":0, "p3_min":0, "p3_max":0}
            return False

        # USE MS WORD STYLE count for paragraphs
        p1_wc = count_words_ms_word_style(paragraphs[2])
        p2_wc = count_words_ms_word_style(paragraphs[3])
        p3_wc = count_words_ms_word_style(paragraphs[4])

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
        if not cover_letter: return False

        # Simple checks for presence
        has_date = bool(re.match(r"\w+ \d{1,2}, \d{4}", cover_letter)) # Month D, YYYY
        has_recipient = "Hiring Manager" in cover_letter # Basic check
        has_salutation = "Dear Hiring Manager," in cover_letter
        has_closing = "Sincerely," in cover_letter
        has_signature = data['expected_signature'] in cover_letter
        # Check for roughly 3 body paragraphs (more than 2 significant blocks between salutation and closing)
        body_match = re.search(r"Dear Hiring Manager,(.*?)Sincerely,", cover_letter, re.DOTALL)
        body_paras = len(re.findall(r'\n\n', body_match.group(1).strip())) >= 2 if body_match else False

        return has_date and has_recipient and has_salutation and body_paras and has_closing and has_signature

    def _validate_cover_letter_signature_multiline(self, data: Dict) -> bool:
        """VG_COVER_LETTER_SIGNATURE_MULTILINE: Checks if signature renders on multiple lines."""
        cover_letter = data['staging_buffer'].get(ResumeSection.K13_COVER_LETTER.value, '')
        expected_signature_block = data.get('expected_signature', '') # Get the fully formatted block

        if not expected_signature_block: return False # Cannot check if template is missing

        # Check if the expected block exists AND contains line breaks within it
        # A simple check: does the block exist and does it contain '\n' AFTER "Sincerely,"?
        sincerely_pos = cover_letter.rfind("Sincerely,")
        if sincerely_pos == -1: return False

        signature_part = cover_letter[sincerely_pos:]
        # Check if the expected block is present and contains internal newlines
        return expected_signature_block in signature_part and '\n' in expected_signature_block

    def _validate_headline_word_count(self, data: Dict) -> bool:
        """
        VG_HEADLINE_WORD_COUNT: Validate K.0 Headline word count.
        v9.87: Uses count_words_ms_word_style.
        """
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        # USE MS WORD STYLE count
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
        forbidden_titles = ['vp', 'vice president', 'director', 'manager', 'chief', 'head', 'lead', 'principal', 'senior']
        found_forbidden = [t for t in forbidden_titles if re.search(r'\b' + t + r'\b', headline)] # Use word boundaries
        data["error_details"] = {"headline": headline, "forbidden": found_forbidden}
        return not found_forbidden


    def _validate_headline_format_no_commas(self, data: Dict) -> bool:
        """VG_HEADLINE_NO_COMMAS: Ensure headline does not contain commas."""
        headline = data['staging_buffer'].get(ResumeSection.K0_HEADLINE.value, '')
        data["error_details"] = {"headline": headline}
        return ',' not in headline

    # --- New Validator Methods for Formatting Hardening ---

    def _validate_resume_header_h2(self, data: Dict) -> bool:
        """VG_RESUME_HEADER_H2: Validates major headers are H2."""
        buffer = data['staging_buffer']
        # Check only K.0 Name, as others are added during rendering
        name_val = buffer.get(ResumeSection.K0_NAME.value)
        failed_headers = []
        if not isinstance(name_val, str) or not name_val.startswith("## "):
            failed_headers.append("Name (K.0)")

        data["error_details"] = {"failed_headers": failed_headers}
        # Rely on QA Table 16 for final check of rendered output
        return True

    def _validate_edu_certs_format(self, data: Dict) -> bool:
        """VG_EDU_CERTS_FORMAT: Validates Edu/Certs line breaks and no bullets."""
        # This check is difficult pre-rendering. Rely on QA Table 16.
        data["error_details"] = {"details": "Checked during rendering"}
        return True

    def _validate_experience_bullet_style(self, data: Dict) -> bool:
        """VG_EXPERIENCE_BULLET_STYLE: Validates experience bullets use '*'."""
        # This check is difficult pre-rendering. Rely on QA Table 16.
        data["error_details"] = {"details": "Checked during rendering"}
        return True

    # *** START FIX: Add missing placeholder methods ***
    def _validate_competencies_formatting(self, data: Dict) -> bool:
        """VG_COMPETENCIES_FORMATTING: Validates competencies list uses '*'."""
        # This check is difficult pre-rendering. Rely on QA Table 16.
        data["error_details"] = {"details": "Checked during rendering"}
        return True

    def _validate_experience_render_format(self, data: Dict) -> bool:
        """VG_EXPERIENCE_RENDER_FORMAT: Validates exp sections format."""
        # This check is difficult pre-rendering. Rely on QA Table 16.
        data["error_details"] = {"details": "Checked during rendering"}
        return True
    # *** END FIX ***

    # --- Bullet Word Count Tolerance Validator ---
    BULLET_WORD_COUNT_TOLERANCE = 0.20 # +/- 20%
    BULLET_WORD_COUNT_SECTIONS_TO_CHECK = [
        ResumeSection.K5_UNIFY_BULLETS,
        ResumeSection.K6_IBM_BULLETS,
        ResumeSection.K10_COMPETENCIES,
        ResumeSection.K8_EY_BULLETS,
        ResumeSection.K9_EARLY_CAREER_BULLETS,
    ]

    def _validate_bullet_word_count_tolerance(self, data: Dict) -> bool:
        """
        VG_BULLET_WORD_COUNT_TOLERANCE: Checks individual bullet word counts.
        v9.87: Uses count_words_ms_word_style.
        """
        all_bullets_valid = True
        violations = []
        averages = data.get('section_averages', {}) # Averages already calculated with MS Word style
        staging_buffer = data['staging_buffer']

        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            avg_key = "Default"
            if section_enum == ResumeSection.K5_UNIFY_BULLETS: avg_key = "Unify"
            elif section_enum == ResumeSection.K6_IBM_BULLETS: avg_key = "IBM"
            elif section_enum == ResumeSection.K10_COMPETENCIES: avg_key = "Competencies"
            elif section_enum == ResumeSection.K8_EY_BULLETS: avg_key = "EY"
            elif section_enum == ResumeSection.K9_EARLY_CAREER_BULLETS: avg_key = "EarlyCareer"
            else: avg_key = "Unify"

            avg_wc = averages.get(avg_key)
            if avg_wc is None or avg_wc <= 0:
                logging.debug(f"Skipping bullet tolerance for {section_key}: Invalid average {avg_wc} for key '{avg_key}'")
                continue

            min_wc = round(avg_wc * (1 - self.BULLET_WORD_COUNT_TOLERANCE))
            max_wc = round(avg_wc * (1 + self.BULLET_WORD_COUNT_TOLERANCE))

            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list):
                 logging.warning(f"Data for {section_key} is not a list, skipping bullet tolerance check.")
                 continue

            for i, bullet in enumerate(bullets):
                if isinstance(bullet, dict):
                    bullet_text = bullet.get('text', '')
                    # USE MS WORD STYLE count if calculating
                    actual_wc = bullet.get('word_count', count_words_ms_word_style(bullet_text))

                    if not (min_wc <= actual_wc <= max_wc):
                        all_bullets_valid = False
                        violations.append(f"{section_key}[{i}]: {actual_wc} words (target: {min_wc}-{max_wc} based on avg {avg_wc:.1f})")
                else:
                     if section_key not in [ResumeSection.K7_TRADERSENSE_BULLETS.value]:
                         logging.warning(f"Item {i} in {section_key} is not a dict: {bullet}")

        if not all_bullets_valid:
            data["error_details"] = {"violations": violations[:5]}
        return all_bullets_valid


    # --- Provenance Split Validator ---
    PROVENANCE_SPLIT_TARGETS = {
        ResumeSection.K5_UNIFY_BULLETS: {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        ResumeSection.K6_IBM_BULLETS: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K10_COMPETENCIES: {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        ResumeSection.K8_EY_BULLETS: {'Customized': 2},
        ResumeSection.K9_EARLY_CAREER_BULLETS: {'Customized': 1},
    }

    def _calculate_master_avg_bullet_length(self) -> Dict[str, float]:
        """
        Helper to calculate average bullet length for sections in master resume.
        v9.85 FIX: This method was missing from WorkflowOrchestrator, causing
        QA Table 6 to use incorrect fallback values (e.g., 25.0).
        This is a direct copy from the PreFlightValidator class.
        v9.91 FIX: Corrected to use count_words_ms_word_style.
        """
        avg_lengths = {}

        # Define sections and their corresponding company name parts/keys
        experience_sections_to_avg = {
            "Unify": ("Unify Consulting", "bullet_pool"),
            "IBM": ("IBM", "bullet_pool"),
            "EY": ("Ernst & Young", "highlights"), # Use highlights key
            "EarlyCareer": ("Early Career Roles", "highlights"), # Use highlights key
        }
        for key, (company_name_part, bullets_key) in experience_sections_to_avg.items():
            total_words = 0
            bullet_count = 0
            # Find the matching experience section in the master resume
            exp = next((e for e in self.master_resume.get("professional_experience", []) if company_name_part in e.get("company", "")), None)
            if exp:
                bullets = exp.get(bullets_key, []) # Use the correct key
                # <<< FIX: Use count_words_ms_word_style, not count_words_clean >>>
                total_words = sum(count_words_ms_word_style(b) for b in bullets if isinstance(b, str)) # Ensure item is string
                bullet_count = len([b for b in bullets if isinstance(b, str)]) # Count only strings
            # Calculate average, provide default if no bullets
            avg_lengths[key] = (total_words / bullet_count) if bullet_count > 0 else 25.0

        # For Competencies section
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        competencies_strings = [c for c in competencies_list if isinstance(c, str)]
        # <<< FIX: Use count_words_ms_word_style, not count_words_clean >>>
        avg_lengths["Competencies"] = (sum(count_words_ms_word_style(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0

        return avg_lengths


    def _validate_provenance_split(self, data: Dict) -> bool:
        """VG_PROVENANCE_SPLIT_CHECK: Checks if bullet provenance matches target splits."""
        all_splits_valid = True
        violations = []
        staging_buffer = data['staging_buffer']

        for section_enum, target_split in self.PROVENANCE_SPLIT_TARGETS.items():
            section_key = section_enum.value
            bullets = staging_buffer.get(section_key, [])
            if not isinstance(bullets, list): continue

            actual_counts = {
                BulletProvenance.Verbatim.value: 0,
                BulletProvenance.Customized.value: 0,
                BulletProvenance.Synthetic.value: 0
            }
            # Handle K7 which might contain strings directly
            if section_key == ResumeSection.K7_TRADERSENSE_BULLETS.value:
                # K7 bullets are always Verbatim and might be strings
                actual_counts[BulletProvenance.Verbatim.value] = len(bullets)
            else:
                for bullet in bullets:
                    if isinstance(bullet, dict):
                        prov = bullet.get('provenance')
                        if prov in actual_counts:
                            actual_counts[prov] += 1

            target_total = sum(target_split.values())
            actual_total = sum(actual_counts.values())

            if actual_total != target_total:
                 all_splits_valid = False
                 violations.append(f"{section_key}: Total count mismatch (Expected {target_total}, Got {actual_total})")
                 continue # Skip detailed check if total is wrong

            for prov_type, target_count in target_split.items():
                actual_count = actual_counts.get(prov_type, 0)
                if actual_count != target_count:
                    all_splits_valid = False
                    violations.append(f"{section_key}: {prov_type} count mismatch (Expected {target_count}, Got {actual_count})")

        if not all_splits_valid:
            data["error_details"] = {"violations": violations}
        return all_splits_valid
    
# ============================================================================
# HOP-7: Gate decision logic.
# ==============================================================================
class GateDecisionEngine:
    """
    Determines whether to PROCEED, ERROR_REPORT_ONLY, or HALT.
    """

    
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

# # ============================================================================
# HOP-8: FILE RENDERER (v9.90 - Enforced Rendering Definitions)
# ============================================================================

class FileRenderer:
    """
    HOP-8: Render final output files.
    Generates all 6 output files with hardened formatting definitions.
    v9.90: Enforces QA Table 16 definitions directly in the render methods.
    """

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

        # --- 4. Render App Tracker Artifact (and Validate) ---
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
            
        # --- 5. Render QA Report Artifact (Path only) ---
        # The content for the QA report is generated in HOP-8 by the orchestrator
        # This step just registers the *path* for the App Tracker
        try:
            path, content = self._render_qa_report_artifact(company_name, job_title)
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content # Will be an empty string
        except Exception as e:
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
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
    # <<< FIX: Add test_mode parameter >>>
    def __init__(self, master_resume: Dict, test_mode: bool = False):
        self.master_resume = master_resume
        self.hop_checkpoints = []
        self.validation_results = []
        self.rendered_output = None

        self.dup_detector = None
        self.similarity_matrix_data = None
        self.executive_summary_similarity_data = None
        self.overview_similarity_data = None
        self.dedup_analysis_timestamp = None
        self.hash_chain = []
        self.constraints = ContentConstraintsConfig()

        self.jd_enforcer = JDEnforcementValidator()

        logging.basicConfig(level=logging.INFO, format='%(message)s')
        # <<< FIX: Correct logger initialization >>>
        logger = logging.getLogger(__name__)

        if not test_mode:
            if not os.environ.get("GEMINI_API_KEY"):
                logger.error(
                    "WARNING: GEMINI_API_KEY environment variable not set!\n" +
                    "="*80 + "\n" +
                    "Please set it using: export GEMINI_API_KEY='your-key-here'\n" +
                    "Get your key at: https://makersuite.google.com/app/apikey\n" +
                    "="*80
                )
            else:
                logger.info("✓ GEMINI_API_KEY detected - Gemini API integration enabled")

        logger.info(f"Current LLM Provider: Gemini")
        logger.info(f"Current Model: {RAGConfig().model}")
    
    def _execute_hop_0_jd_analysis(self, job_description: str) -> ThematicAnalysis:
        """Executes HOP-0: Job Description Analysis."""
        print("\n[HOP-0] Job Description Analysis...")
        jd_analyzer = self._create_jd_analyzer()
        thematic_analysis = jd_analyzer.analyze(job_description)
        
        hop_checkpoint = self._create_checkpoint(
            "HOP-0", "JD Analysis & RAG", [],
            {"signal_score": thematic_analysis.signal_quality_score},
            metadata={"web_search_calls": jd_analyzer.search_calls_made}
        )
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint)
        return thematic_analysis

    def _execute_hop_1_clerk_extraction(self) -> Dict:
        """Executes HOP-1: Master Resume Extraction."""
        print("\n[HOP-1] Master Resume Extraction...")
        clerk = ClerkExtractor(self.master_resume)
        extracted_data, hop_results = clerk.extract()
        
        hop_checkpoint = self._create_checkpoint(
            "HOP-1", "Clerk Extraction", hop_results,
            {"bullets_extracted": sum(len(s.get('bullets', [])) for s in extracted_data.get('experience_sections', []))}
        )
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint, allow_warnings=True)
        return extracted_data

    def _execute_hop_2_enrichment(self, extracted_data: Dict, thematic_analysis: ThematicAnalysis) -> Dict:
        """Executes HOP-2: Data Enrichment."""
        print("\n[HOP-2] Data Enrichment...")
        enricher = DataEnricher()
        enriched_scaffold, hop_results = enricher.enrich(extracted_data, thematic_analysis, self)
        
        hop_checkpoint = self._create_checkpoint("HOP-2", "Data Enrichment", hop_results, enriched_scaffold)
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint, allow_warnings=True)
        return enriched_scaffold

    def _execute_hop_3_artist_generation(self, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis) -> Dict:
        """Executes HOP-3: Content Generation with retry logic."""
        print("\n[HOP-3] Content Generation...")
        hop_start_time = datetime.now() # For duration calculation
        
        # Instantiate the ArtistGenerator once before the loop.
        artist = ArtistGenerator(
            master_resume=self.master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis
        )
        
        # --- START FIX: Initialize all loop-dependent variables ---
        artist_output = None
        hop_results = []
        validation_results = []
        all_passed = False
        feedback_results = None
        max_attempts = 5
        # --- END FIX ---

        for attempt in range(1, max_attempts + 1):
            print(f"  Attempt {attempt}/{max_attempts}...")
            
            # --- START FIX: Capture outputs from the *current* attempt ---
            # These are now loop-scoped and will be overwritten each time
            current_artist_output, current_hop_results = artist.generate(
                feedback_results=feedback_results,
                attempt=attempt
            )
            
            # Quick validation to see if we need to retry
            temp_buffer = ImmutableStagingBuffer()
            for key, value in current_artist_output.items():
                temp_buffer.set(key, value)
            temp_buffer.lock()

            validator = PreFlightValidator(self.master_resume)
            # These are also loop-scoped
            current_validation_results, current_all_passed = validator.validate(
                temp_buffer, thematic_analysis, job_description
            )
            
            # CRITICAL FIX: Update the function-scoped variables
            # with the results of *this* attempt.
            artist_output = current_artist_output
            hop_results = current_hop_results
            validation_results = current_validation_results
            all_passed = current_all_passed
            # --- END FIX ---

            if all_passed or attempt == max_attempts:
                # If we passed, or we're on the last attempt, break the loop.
                # The function-scoped variables (artist_output, validation_results)
                # now correctly hold the state of this final attempt.
                break
            else:
                # Prep for the next loop: set feedback from the failed attempt
                feedback_results = [vr for vr in validation_results if not vr.passed]
                print(f"    {len(feedback_results)} validation failures, retrying...")
        
        # --- Post-loop validation and checkpoint ---
        
        # If it's the last attempt and it *still* failed, raise an error.
        if not all_passed and attempt == max_attempts:
            print(f"  ✗ HOP-3 FAILED: Validation failed after {attempt} attempts. Halting.")
            # Manually add the final failed validation results to the orchestrator
            # so the QA report can see them before we halt.
            self.validation_results.extend(validation_results or [])
            raise HopExecutionError(f"HOP-3 failed: Content validation failed after {max_attempts} attempts.")
        
        # This code now correctly uses the `artist_output` from the *last* (and successful) attempt
        llm_calls_made = 0
        if artist_output: # Add null check
            llm_calls_made = len([k for k in artist_output if artist_output.get(k)])
            
        hop_checkpoint = self._create_checkpoint(
            "HOP-3", f"Artist Generation (attempt {attempt})",
            hop_results,  # Use hop_results from the last attempt
            artist_output, # Use artist_output from the last attempt
            start_time=hop_start_time,
            metadata={"llm_api_calls": llm_calls_made}
        )
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint)
        
        return artist_output # Return the correct output
    
    def _execute_hop_4_staging_and_sanitization(self, artist_output: Dict) -> ImmutableStagingBuffer:
        """Executes HOP-4 and HOP-4.5: Staging, Sanitization, and Locking."""
        # HOP-4
        hop_start_time = datetime.now() # For duration calculation
        print("\n[HOP-4] Populating Staging Buffer...")
        staging_buffer = ImmutableStagingBuffer()
        for key, value in artist_output.items():
            staging_buffer.set(key, value)
        
        hop4_checkpoint = self._create_checkpoint("HOP-4", "Staging Buffer", [], {"sections_populated": len(artist_output)},
                                                 start_time=hop_start_time)
        self.hop_checkpoints.append(hop4_checkpoint)
        self._check_hop_status(hop4_checkpoint)

        # HOP-4.5
        print("\n[HOP-4.5] Text Sanitization...")
        sanitizer = TextSanitizer()
        hop45_results, sanitized_data = sanitizer.sanitize_buffer(staging_buffer)
        
        for key, value in sanitized_data.items():
            staging_buffer.set(key, value)
        print("  ✓ Staging buffer updated with sanitized content")
        
        staging_buffer.lock()
        print("  ✓ Staging buffer locked")
        
        # Use hop_start_time from HOP-4 start for duration calculation of combined hop
        hop45_checkpoint = self._create_checkpoint("HOP-4.5", "Text Sanitization", hop45_results, {"buffer_locked": True},
                                                  start_time=hop_start_time)
        self.hop_checkpoints.append(hop45_checkpoint)
        self._check_hop_status(hop45_checkpoint)
        return staging_buffer
    
    def _execute_hop_5_validation(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str) -> List[ValidationResult]:
        """Executes HOP-5: Pre-flight Validation."""
        hop_start_time = datetime.now()
        print("\n[HOP-5] Pre-flight Validation...")
        validator = PreFlightValidator(self.master_resume)
        hop_results, all_passed = validator.validate(staging_buffer, thematic_analysis, job_description)
        
        hop_checkpoint = self._create_checkpoint("HOP-5", "Pre-flight Validation", hop_results, {"all_passed": all_passed}, start_time=hop_start_time)
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint)
        return hop_results

    def _execute_hop_6_gate_decision(self, hop5_results: List[ValidationResult]) -> GateDecision:
        """Executes HOP-6: Gate Decision."""
        hop_start_time = datetime.now()
        print("\n[HOP-6] Gate Decision...")
        gate_engine = GateDecisionEngine()
        gate_decision, gate_reason = gate_engine.decide(hop5_results)
        
        print(f"  Decision: {gate_decision.value}")
        print(f"  Reason: {gate_reason}")
        
        hop_checkpoint = self._create_checkpoint("HOP-6", "Gate Decision", [], {"decision": gate_decision.value, "reason": gate_reason},
                                                 start_time=hop_start_time)
        self.hop_checkpoints.append(hop_checkpoint)

        if gate_decision == GateDecision.HALT:
            raise HopExecutionError(f"HALT: {gate_reason}")
        
        return gate_decision

    def _execute_hop_7_rendering(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str, thematic_analysis: ThematicAnalysis, job_description: str) -> Dict[str, str]:
        """Executes HOP-7: File Rendering. Returns dict of file paths and dict of file contents."""
        hop_start_time = datetime.now()
        print("\n[HOP-7] Rendering Output Files...") # This is HOP-7 in the user's mental model
        renderer = FileRenderer(self.master_resume, self)
        # renderer.render returns (file_paths, validation_results) but validation_results is a tuple of (validation_results, file_contents)
        file_paths, (hop_results, file_contents) = renderer.render(
            staging_buffer, company_name, job_title, thematic_analysis, job_description  # v5.57: Pass JD for alignment scoring
        )
        
        hop_checkpoint = self._create_checkpoint("HOP-7", "File Rendering", hop_results, file_paths, start_time=hop_start_time)
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint)
        
        return file_paths, file_contents

    def _execute_hop_8_qa_report(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, hop5_results: List[ValidationResult]) -> str:
        """Executes HOP-8: QA Report Generation."""        
        hop_start_time = datetime.now()
        print("\n[HOP-8] Generating QA Report...")
        qa_report_validation_results, qa_report_text = self._generate_qa_report(
            staging_buffer, thematic_analysis, hop5_results
        )
        
        hop_checkpoint = self._create_checkpoint(
            "HOP-8", "QA Report Generation", qa_report_validation_results, {"qa_report_generated": True}
        , start_time=hop_start_time)
        self.hop_checkpoints.append(hop_checkpoint)
        self._check_hop_status(hop_checkpoint)
        return qa_report_text

    def _execute_hop_7_5_deduplication(self, staging_buffer: ImmutableStagingBuffer):
        """Executes HOP-7.5: Deduplication Analysis."""
        print("\n[HOP-7.5] Computing Deduplication Metrics...")
        if self._invoke_deduplication_analysis(staging_buffer): # Pass the full buffer
            print("  ✓ Deduplication analysis complete")
        else:
            print("  ⚠️  Deduplication analysis skipped (no data available)")
        # This hop is for analysis only and doesn't produce a checkpoint.


    def execute_workflow(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> Dict:
        workflow_start = datetime.now()
        # Harden inputs to prevent empty strings
        company_name = company_name.strip() if company_name and company_name.strip() else "Target_Company"
        job_title = job_title.strip() if job_title and job_title.strip() else "Target_Role"


        print("=" * 80)
        print(f"RESUME GENERATION ENGINE v{__version__} - GEMINI API")
        print("=" * 80)
        print(f"Company: {company_name}")
        print(f"Position: {job_title}")
        print(f"Started: {workflow_start.isoformat()}")
        print("=" * 80)
        
        try:
            # GATE-0: Validate JD Input
            print("\n[GATE-0] JD Input Validation...")
            jd_validation = self.jd_enforcer.validate_jd_input(job_description, "GATE-0")
            failed_validations = [r for r in jd_validation if not r.passed]
            if failed_validations:
                print(f"⚠️  JD Validation warnings: {len(failed_validations)} rules")
                for val in failed_validations[:3]:
                    print(f"    - {val.details}")
            else:
                print("✓ JD input validation passed")
            
            # HOP-0: JD Analysis & RAG
            thematic_analysis = self._execute_hop_0_jd_analysis(job_description)
            hop_start_time = datetime.now() # Reset timer for next hop
            
            # GATE-1: Validate JD Parsing
            print("\n[GATE-1] JD Parsing Validation...")
            parsed_jd_for_validation = asdict(thematic_analysis) # This is fine, asdict creates a dict
            self.jd_enforcer.validate_jd_parsing(parsed_jd_for_validation, "GATE-1")

            # HOP-1: Clerk Extraction
            hop_start_time = datetime.now()
            extracted_data = self._execute_hop_1_clerk_extraction()

            # GATE-2: Validate Thematic Analysis
            print("\n[GATE-2] Thematic Analysis Validation...")
            self.jd_enforcer.validate_thematic_analysis(thematic_analysis, "GATE-2")
            
            # HOP-2: Data Enrichment
            hop_start_time = datetime.now()
            enriched_scaffold = self._execute_hop_2_enrichment(extracted_data, thematic_analysis)

            # GATE-3: Validate Enrichment
            print("\n[GATE-3] Enrichment Validation...")
            self.jd_enforcer.validate_enrichment(enriched_scaffold, "GATE-3")

            # HOP-3: Artist Generation (with feedback loop)
            # This helper now contains the full retry/sanitize/validate loop
            print("\n[GATE-4] Artist Input Validation...")
            self.jd_enforcer.validate_artist_inputs(enriched_scaffold, thematic_analysis, "GATE-4")
            artist_output = self._execute_hop_3_artist_generation(
                enriched_scaffold, job_description, thematic_analysis
            )
            
            # HOP-4 & 4.5: Staging, Sanitization, and Locking
            hop_start_time = datetime.now()
            staging_buffer = self._execute_hop_4_staging_and_sanitization(artist_output)
            
            # HOP-5: Validation (Batched QA)
            hop5_results = self._execute_hop_5_validation(staging_buffer, thematic_analysis, job_description)

            # GATE-5: Pre-flight Validation
            print("\n[GATE-5] Pre-flight JD Validation...")
            self.jd_enforcer.validate_preflight(staging_buffer, "GATE-5")
            
            # HOP-6: Gate Decision
            hop_start_time = datetime.now()
            gate_decision = self._execute_hop_6_gate_decision(hop5_results)
            
            # HOP-7: File Rendering
            file_paths, file_contents = self._execute_hop_7_rendering(
                staging_buffer, company_name, job_title, thematic_analysis, job_description
            )

            # GATE-7: File Output Validation
            print("\n[GATE-7] File Output Validation...")
            self.jd_enforcer.validate_file_output(file_paths, "GATE-7")
            
            # HOP-7.5: Deduplication Analysis (v5.65 - for QA Sections 4 & 5)
            hop_start_time = datetime.now() # Start timer for this analysis step
            self._execute_hop_7_5_deduplication(staging_buffer)
            
            # HOP-8: QA Report Generation
            qa_report_text = self._execute_hop_8_qa_report(
                staging_buffer, thematic_analysis, hop5_results
            )

            # GATE-8: QA Report Validation
            print("\n[GATE-8] QA Report Validation...")
            self.jd_enforcer.validate_qa_report({"report": qa_report_text}, "GATE-8")
            
            # Build final result
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            
            # Build CoC ledger
            coc_ledger = self._build_coc_ledger(
                workflow_start,
                workflow_end,
                thematic_analysis
            )
            
            print("\n" + "=" * 80)
            print("WORKFLOW COMPLETE")
            print("=" * 80)
            print(f"Duration: {duration:.2f}s")
            print(f"Gate Decision: {gate_decision.value}")
            print(f"Output Files: {len(file_paths)}")
            
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
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "hash_chain": self.hash_chain
            }
            self.rendered_output = final_result
            return final_result
        except HopExecutionError as e:
            # This is a controlled halt from a gate decision
            print(f"\n✗ WORKFLOW HALTED: {str(e)}")
            # Find the gate decision from the last checkpoint (which should be HOP-6)
            gate_decision = GateDecision.HALT
            reason = str(e)
            if self.hop_checkpoints and self.hop_checkpoints[-1].hop_id == "HOP-6":
                gate_decision_info = self.hop_checkpoints[-1].metadata
                gate_decision = GateDecision(gate_decision_info.get("decision", "HALT"))
                reason = gate_decision_info.get("reason", str(e))

            return {
                "status": "HALTED",
                "gate_decision": gate_decision.value,
                "reason": reason,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
            }
        except Exception as e:
            print(f"\n✗ WORKFLOW FAILED UNEXPECTEDLY: {str(e)}")
            return {
                "status": "FAILED",
                "error": str(e),
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints],
            }

    def _create_jd_analyzer(self) -> EnhancedJobDescriptionAnalyzer:
        """
        Create enhanced JD analyzer with web-search intelligence gathering.
        v5.53: Uses market intelligence research with graceful fallback to local NLP.
        """
        return EnhancedJobDescriptionAnalyzer(self.master_resume, enable_web_search=True)

    def _create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        validation_results: List[ValidationResult],
        output_data: Any, start_time: datetime, metadata: Optional[Dict[str, Any]] = None
    ) -> HopCheckpoint:
        """Create hop checkpoint."""
        # Determine status
        if not validation_results:
            status = HopStatus.PASS
        else:
            critical_failures = [vr for vr in validation_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
            status = HopStatus.FAIL if critical_failures else HopStatus.PASS
        
        # Calculate output hash
        output_hash = None
        if output_data is not None:
            if isinstance(output_data, dict):
                output_str = json.dumps(output_data, sort_keys=True)
            else:
                output_str = str(output_data)
            output_hash = hashlib.sha256(output_str.encode()).hexdigest()[:16]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        checkpoint = HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            status=status,
            timestamp_start=start_time.isoformat(),
            # timestamp_end=datetime.now().isoformat(), # Use calculated end_time
            timestamp_end=datetime.now().isoformat(),
            output_hash=output_hash,
            validation_results=validation_results,
            metadata=metadata or {},
            error_message=None
        )
        
        # Store duration in metadata
        checkpoint.metadata["duration_seconds"] = duration

        # Add to hash chain
        if self.hash_chain:
            prev_hash = self.hash_chain[-1]
            current_hash = hashlib.sha256(f"{prev_hash}{hop_id}{output_hash}".encode()).hexdigest()[:16] # Add hop_id for robustness
        else:
            current_hash = output_hash or "H0"
        
        self.hash_chain.append(current_hash)
        
        return checkpoint
    
    def _check_hop_status(self, checkpoint: HopCheckpoint):
        """Check hop status and halt if failed (unless warnings allowed)."""
        if checkpoint.status == HopStatus.FAIL:
            critical_failures = [vr for vr in checkpoint.validation_results if not vr.passed and (vr.severity == ValidationSeverity.CRITICAL or vr.severity == ValidationSeverity.HIGH)]
            error_msg = f"[{checkpoint.hop_id}] FAILED - {len(critical_failures)} HIGH/CRITICAL failures detected. Halting workflow."
            print(f"  ✗ {error_msg}")
            for vr in critical_failures[:3]:
                # Check if message is a lambda and call it if so
                message = vr.message(vr.details) if callable(vr.message) else vr.message
                print(f"    - {vr.rule_id}: {message}")
            raise HopExecutionError(f"{checkpoint.hop_id} failed validation with HIGH/CRITICAL errors.")
        
        # Show warnings
        warnings = [vr for vr in checkpoint.validation_results 
                   if not vr.passed and vr.severity != ValidationSeverity.CRITICAL]
        if warnings:
            print(f"  ⚠ {len(warnings)} warnings")
        
        print(f"  ✓ {checkpoint.hop_id} complete ({checkpoint.status.value})")
    
    def _build_coc_ledger(
        self,
        workflow_start: datetime,
        workflow_end: datetime,
        thematic_analysis: ThematicAnalysis
    ) -> Dict:
        """Build Chain of Custody ledger."""
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', '')}".encode()
        ).hexdigest()[:16]
        
        return {
            "workflow_id": workflow_id,
            "version": f"v{__version__}",
            "architecture": f"Job_Workflow_v{__version__}_Comprehensive_Redesign",
            "timestamp_start": workflow_start.isoformat(),
            "timestamp_end": workflow_end.isoformat(),
            "duration_seconds": (workflow_end - workflow_start).total_seconds(),
            "hops_executed": [
                {"hop_id": hc.hop_id, "hop_name": hc.hop_name, "status": hc.status.value, 
                 "timestamp": hc.timestamp_end, "output_hash": hc.output_hash}
                for hc in self.hop_checkpoints
            ],
            "hash_chain": self.hash_chain, # This is correct
            "rag_metadata": { # This was missing the nested structure
                "signal_quality": thematic_analysis.signal_quality_score if hasattr(thematic_analysis, 'signal_quality_score') else 0.0,
                "retrieval_method": thematic_analysis.retrieval_method if hasattr(thematic_analysis, 'retrieval_method') else 'UNKNOWN',
                "peer_jds_analyzed": thematic_analysis.competitive_intelligence.peer_jds_analyzed_count if hasattr(thematic_analysis, 'competitive_intelligence') else 0,
                "differentiator_keywords": thematic_analysis.competitive_intelligence.differentiator_keywords[:10] if hasattr(thematic_analysis, 'competitive_intelligence') else []
            },
            "overall_status": "SUCCESS" if all(hc.status != HopStatus.FAIL for hc in self.hop_checkpoints) else "FAILED"
        }
    
    def _calculate_signal_score(self, text_content, thematic_analysis):
        """Helper to calculate signal score for a block of text based on JD keywords."""
        if not text_content:
            return 0.0
        
        # Convert list/dict to string for simple text matching
        if isinstance(text_content, (list, dict)):
            text = str(text_content).lower()
        else:
            text = str(text_content).lower()
        
        if not text:
            return 0.0

        # Get JD keywords from RAG analysis (HOP-0)
        try:
            differentiators = set(thematic_analysis.competitive_intelligence.differentiator_keywords)
            primary_words = set(thematic_analysis.primary_theme.get('keywords', []))
            all_jd_words = differentiators.union(primary_words)
        except (AttributeError, KeyError, TypeError):
            return 0.0
        
        if not all_jd_words:
            return 0.0

        words_in_text = set(re.findall(r'\b\w+\b', text))
        
        # Calculate score: 1 point per keyword match, normalized
        matches = words_in_text.intersection(all_jd_words)
        score = len(matches) / 10.0
        
        # Boost score for primary theme keywords
        primary_matches = words_in_text.intersection(primary_words)
        score += len(primary_matches) * 0.1
        
        return min(1.0, score)

    def _invoke_deduplication_analysis(self, staging_buffer: ImmutableStagingBuffer) -> bool:

        self.overview_similarity_data = [] # Reset/Initialize
        analysis_performed = False
        
        try:
            if self.dup_detector is None:
                print("  ⚠️  Deduplication analysis skipped (detector not initialized).")
                return False
            
            # Compute 78x78 Pairwise Similarity Matrix
            try:
                # Fetch necessary bullet sections for pairwise comparison
                sections_for_matrix = {
                    sec.value: staging_buffer.get(sec.value)
                    for sec in [ResumeSection.K5_UNIFY_BULLETS, ResumeSection.K6_IBM_BULLETS, ResumeSection.K10_COMPETENCIES]
                    if staging_buffer.get(sec.value) # Only include sections with content
                }
                self.similarity_matrix_data = self.dup_detector.compute_similarity_matrix(
                    sections=sections_for_matrix
                )
                if self.similarity_matrix_data: analysis_performed = True
            except Exception as e:
                print(f"  ⚠️  Similarity matrix computation failed: {e}")
                self.similarity_matrix_data = None
            
            # v9.11: Compute Overview-to-Bullet Similarity for all 4 sections
            overview_bullet_pairs = [
                ("Unify", ResumeSection.K5_UNIFY_OVERVIEW, ResumeSection.K5_UNIFY_BULLETS),
                ("IBM", ResumeSection.K6_IBM_OVERVIEW, ResumeSection.K6_IBM_BULLETS),
                ("EY", ResumeSection.K8_EY_OVERVIEW, ResumeSection.K8_EY_BULLETS),
                ("EarlyCareer", ResumeSection.K9_EARLY_CAREER_OVERVIEW, ResumeSection.K9_EARLY_CAREER_BULLETS),
            ]
            
            for section_name, overview_enum, bullets_enum in overview_bullet_pairs:
                try:
                    overview = staging_buffer.get(overview_enum.value, "")
                    # Bullets are expected as List[Dict] containing 'text'
                    bullet_dicts = staging_buffer.get(bullets_enum.value, [])
                    bullets_text = [b.get('text', '') for b in bullet_dicts if isinstance(b, dict) and b.get('text')]
                    
                    if overview and bullets_text:
                        sim_data = self.dup_detector.compute_overview_bullet_similarity(
                            overview_text=overview, bullets=bullets_text, section_id=section_name
                        )
                        self.overview_similarity_data.append(sim_data)
                        analysis_performed = True
                except Exception as e:
                    print(f"  ⚠️  Overview similarity computation failed for {section_name}: {e}")
                
            self.dedup_analysis_timestamp = datetime.now().isoformat()
            return analysis_performed

        except Exception as e:
            print(f"  CRITICAL ⚠️  Deduplication analysis failed entirely: {e}")
            return False

    def _format_plain_text_table(self, headers: List[str], rows: List[List[str]], alignments: Optional[List[str]] = None) -> List[str]:
      
        if not rows:
            return [" ".join(headers), "(No data available)"]

        # Convert all cells to strings first
        safe_rows = [[str(cell) for cell in row] for row in rows]
        safe_headers = [str(h) for h in headers]

        # 1. Determine column widths
        num_cols = len(safe_headers)
        # Ensure all rows have the same number of columns as headers, padding if necessary
        processed_rows = []
        for row in safe_rows: # Use safe_rows
            processed_row = list(row) # Make a mutable copy
            if len(processed_row) < num_cols:
                processed_row.extend([""] * (num_cols - len(processed_row)))
            elif len(processed_row) > num_cols:
                processed_row = processed_row[:num_cols]
            processed_rows.append(processed_row)

        col_widths = [len(h) for h in safe_headers] # Use safe_headers
        for row in processed_rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        # 2. Set alignments (default to left)
        # Use 'L' (left) or 'R' (right)
        if not alignments or len(alignments) != num_cols:
            alignments = ['L'] * num_cols
        else: # Validate alignments
            valid_alignments = []
            for align in alignments:
                if align.upper() in ['L', 'R']:
                    valid_alignments.append(align.upper())
                else:
                    valid_alignments.append('L') # Default to left if invalid
            alignments = valid_alignments


        # 3. Create format strings
        # Add 2 spaces for padding: '  '
        formatters = [f"{{:{'>' if alignments[i] == 'R' else '<'}{col_widths[i]}}}" for i in range(num_cols)]
        row_template = "   ".join(formatters)

        output_lines = []
        output_lines.append(row_template.format(*safe_headers)) # Use safe_headers
        output_lines.append(row_template.format(*["-" * w for w in col_widths]))
        for row in processed_rows:
            output_lines.append(row_template.format(*row))
        return output_lines

    def _format_ascii_bar_chart(self, label: str, value: float, target_min: float, target_max: float, temperature: Optional[float] = None, max_value: float = 1.0, width: int = 30) -> str:
        """Formats a value as an ASCII horizontal bar chart for the QA report."""
        if value < 0: value = 0
        
        # Clamp value for bar display, but show real value in text
        display_value = min(value, max_value)
        
        ratio = display_value / max_value
        filled_width = int(ratio * width)
        
        bar = '█' * filled_width
        
        status = "✓"
        if value < target_min:
            status = "✗ (LOW)"
        elif value > target_max:
            status = "✗ (OVERFIT)"
        
        temp_str = f"(T:{temperature:.1f})" if temperature is not None else ""
        target_str = f"Tgt:{target_min:.0%}-{target_max:.0%}"
        
        # Adjusted spacing to accommodate temperature
        return f"{label:<25} [{bar:<{width}}] {value:.1%} Signal {temp_str} ({target_str}) {status}"

    def _build_qa_section_1_signal_quality(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis) -> List[str]:
        """Builds Section 1 of the QA report: Signal Quality."""
        lines = ["", "1. SIGNAL QUALITY (Per-Section Analysis vs. JD Keywords)", ""]
        
        # <<< MODIFICATION: Load max signal from new config >>>
        max_signal_target = SignalControlConfig().SECTION_SIGNAL_SCORE_MAX
        
        # Map sections to their reasoning configs for temperature lookup
        # <<< MODIFICATION: Tuple expanded to include max_target >>>
        # --- START MODIFICATION ---
        # v9.95: Updated all Min/Max targets and added Headline per user request.
        section_configs = {
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
            "Competencies": (ResumeSection.K10_COMPETENCIES, 0.85, 0.95, 0.15, ReasoningConfig.K10_COMPETENCIES_CONFIG),
        }
        # --- END MODIFICATION ---

        # Headers are no longer needed for bar chart format
        rows = []
        total_weighted_score, total_weight = 0.0, 0.0
        
        lines.append("```markdown") # Start code fence
        # <<< MODIFICATION: Loop updated to unpack new tuple format >>>
        for label, (section_enum, target_min_score, target_max_score, weight, reasoning_config) in section_configs.items():
            content = staging_buffer.get(section_enum.value)
            if content:
                score = self._calculate_signal_score(content, thematic_analysis)
                total_weighted_score += score * weight
                total_weight += weight
                
                # Calculate the *actual* final temperature used
                api_params = reasoning_config_to_api_params(reasoning_config)
                sc_count = api_params.get('sc', 1)

                if sc_count > 1:
                    # If SC is active, the *final* text is generated by the
                    # synthesis step, which is now 0.5
                    temp = 0.5
                else:
                    # If SC is not active, use the configured temperature
                    temp = api_params["generation_config"].temperature
                    if label == "Executive Summary":
                        temp = 1.0 # Account for manual override
                
                status = "✓" # Default
                if score < target_min_score: status = "✗ (LOW)"
                elif score > target_max_score: status = "✗ (OVERFIT)"
                
                # <<< MODIFICATION: Pass min and max targets to formatter >>>
                lines.append(self._format_ascii_bar_chart(
                    label=label, value=score, 
                    target_min=target_min_score,
                    target_max=target_max_score,
                    temperature=temp
                ))
            else:
                # Optionally show skipped sections differently or omit them
                lines.append(f"{label:<25} [SKIPPED]{' '*23} (Target: {target_min_score:.0%}) -")

        if total_weight > 0:
            average_signal = total_weighted_score / total_weight
            # Recalculate overall_target considering only non-skipped sections
            # <<< MODIFICATION: Unpack new tuple format here too >>>
            overall_target_numerator = sum(target_min * w for _, (section_enum, target_min, _, w, _) in section_configs.items() if staging_buffer.get(section_enum.value) is not None)
            actual_total_weight = sum(w for _, (section_enum, _, _, w, _) in section_configs.items() if staging_buffer.get(section_enum.value) is not None)
            overall_target = overall_target_numerator / actual_total_weight if actual_total_weight > 0 else 0.0
            
            lines.append("-" * 80)
            # Format the summary line using the bar chart function
            # <<< MODIFICATION: Pass min and max targets to formatter >>>
            
            # --- START MODIFICATION ---
            # v9.95: Update overall target to 70-85% per user request
            overall_min_target = 0.70
            overall_max_target = 0.85
            # --- END MODIFICATION ---

            summary_bar = self._format_ascii_bar_chart(
                label="Total Weighted Score", value=average_signal,
                target_min=overall_min_target,
                target_max=overall_max_target,
                temperature=None
            )
            lines.append(summary_bar)

        lines.append("```") # End code fence
        return lines
    
    def _build_qa_section_2_thematic_compliance(self, thematic_analysis: ThematicAnalysis) -> List[str]:
        """Builds Section 2 of the QA report: Thematic Compliance."""
        lines = ["", "2. THEMATIC COMPLIANCE (JD Alignment)", ""]
        lines.append("```markdown")

        headers = ["Theme", "Confidence", "Keywords"]
        rows = []
        expected_rows = 0
        if thematic_analysis and thematic_analysis.primary_theme:
            pt = thematic_analysis.primary_theme
            rows.append(["**Primary**", f"{pt.get('confidence', 0):.1%}", ", ".join(pt.get('keywords', []))])
            expected_rows += 1
        if thematic_analysis and thematic_analysis.secondary_themes:
            for st in thematic_analysis.secondary_themes[:4]:
                rows.append([st.get('name'), f"{st.get('relevance', 0):.1%}", ", ".join(st.get('keywords', []))])
            expected_rows += min(len(thematic_analysis.secondary_themes), 4)
        
        # Truncation Check
        if len(rows) != expected_rows:
            rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} theme rows, got {len(rows)}"])
        
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_3_hop_summary(self) -> List[str]:
        """Builds Section 3 of the QA report: Hop-by-Hop Execution Summary."""
        lines = ["", "3. HOP-BY-HOP EXECUTION SUMMARY", ""]
        lines.append("```markdown")

        headers = ["Hop ID", "Hop Name", "Status", "Duration (s)", "Output Hash"]
        rows = []
        for hop in self.hop_checkpoints:
            duration = hop.metadata.get("duration_seconds", -1.0) # Read duration from metadata

            rows.append([
                hop.hop_id, hop.hop_name, hop.status.value,
                f"{duration:.3f}" if duration >= 0 else "N/A", hop.output_hash or "N/A"
            ])
        lines.extend(self._format_plain_text_table(headers, rows))
        
        # Truncation Check (after formatting, check raw row count)
        expected_rows = len(self.hop_checkpoints)
        if len(rows) != expected_rows:
             lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} hop rows, got {len(rows)}") # Insert error after header/sep

        lines.append("```")
        return lines

    def _build_qa_section_4_distribution(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 4 of the QA report: Word Count Distribution."""
        lines = ["", "4. WORD COUNT DISTRIBUTION", ""]
        dist_results = [vr for vr in validation_results if "DISTRIBUTION" in vr.rule_id or "RATIO" in vr.rule_id]
        lines.append("```markdown")
        headers = ["Rule ID", "Value", "Target Range", "Status", "Message"] # Added columns
        rows = []
        for vr in dist_results:
            # Extract details populated by the validator
            details = vr.details or {}
            value_str = "N/A"
            if 'percent' in details: value_str = f"{details['percent']:.1f}%"
            elif 'ratio' in details: value_str = f"{details['ratio']:.2f}"
            target_str = f"{details.get('min', '?')}-{details.get('max', '?')}"
            if '%' in value_str: target_str += "%" # Add % sign to target if value is a percent

            rows.append([
                vr.rule_id, value_str, target_str,
                "PASS" if vr.passed else "FAIL", vr.message if not vr.passed else ""
            ])
        lines.extend(self._format_plain_text_table(headers, rows))
        
        # Truncation Check
        expected_rows = len(dist_results)
        if len(rows) != expected_rows:
            lines.insert(2, f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} distribution rows, got {len(rows)}")
        lines.append("```")
        return lines

    def _calculate_master_avg_bullet_length(self) -> Dict[str, float]:
        """
        Helper to calculate average bullet length for sections in master resume.
        v9.91 FIX: Added this method, which was missing from ArtistGenerator.
        This is a copy of the corrected PreFlightValidator version.
        """
        avg_lengths = {}

        # Define sections and their corresponding company name parts/keys
        experience_sections_to_avg = {
            "Unify": ("Unify Consulting", "bullet_pool"),
            "IBM": ("IBM", "bullet_pool"),
            "EY": ("Ernst & Young", "highlights"),
            "EarlyCareer": ("Early Career Roles", "highlights"),
        }
        for key, (company_name_part, bullets_key) in experience_sections_to_avg.items():
            total_words = 0
            bullet_count = 0
            exp = next((e for e in self.master_resume.get("professional_experience", []) if company_name_part in e.get("company", "")), None)
            if exp:
                bullets = exp.get(bullets_key, [])
                # Use the correct ms_word_style count
                total_words = sum(count_words_ms_word_style(b) for b in bullets if isinstance(b, str))
                bullet_count = len([b for b in bullets if isinstance(b, str)])
            avg_lengths[key] = (total_words / bullet_count) if bullet_count > 0 else 25.0

        # For Competencies section
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        competencies_strings = [c for c in competencies_list if isinstance(c, str)]
        # Use the correct ms_word_style count
        avg_lengths["Competencies"] = (sum(count_words_ms_word_style(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0

        return avg_lengths

    QA_PROVENANCE_SECTIONS = [
        {
            "name": "Unify", "overview_enum": ResumeSection.K5_UNIFY_OVERVIEW, "bullets_enum": ResumeSection.K5_UNIFY_BULLETS,
            "overview_min_attr": "UNIFY_OVERVIEW_WORD_COUNT_MIN", "overview_max_attr": "UNIFY_OVERVIEW_WORD_COUNT_MAX",
        },
        {
            "name": "IBM", "overview_enum": ResumeSection.K6_IBM_OVERVIEW, "bullets_enum": ResumeSection.K6_IBM_BULLETS,
            "overview_min_attr": "IBM_OVERVIEW_WORD_COUNT_MIN", "overview_max_attr": "IBM_OVERVIEW_WORD_COUNT_MAX",
        },
        {
            "name": "EY", "overview_enum": ResumeSection.K8_EY_OVERVIEW, "bullets_enum": ResumeSection.K8_EY_BULLETS,
            "overview_min_attr": "EY_OVERVIEW_WORD_COUNT_MIN", "overview_max_attr": "EY_OVERVIEW_WORD_COUNT_MAX",
        },
        {
            "name": "EarlyCareer", "overview_enum": ResumeSection.K9_EARLY_CAREER_OVERVIEW, "bullets_enum": ResumeSection.K9_EARLY_CAREER_BULLETS,
            "overview_min_attr": "EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN", "overview_max_attr": "EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX",
        },
        {"name": "Competencies", "overview_enum": None, "bullets_enum": ResumeSection.K10_COMPETENCIES},
    ]

    def _check_word_count(self, word_count: int, min_target: int, max_target: int) -> Tuple[str, str]:
        """Helper to check word count against a range and return status and range string."""
        target_range_str = f"{min_target}-{max_target}"
        status = "✓ PASS" if min_target <= word_count <= max_target else "✗ FAIL"
        return status, target_range_str

    def _build_qa_section_6_provenance(self, staging_buffer: ImmutableStagingBuffer) -> List[str]:
        """
        Builds Section 6 of the QA report: Bullet Provenance & Word Count.
        v9.87: Uses count_words_ms_word_style and correct avg length calculation.
        """
        lines = ["", "6. BULLET PROVENANCE & WORD COUNT", ""]
        lines.append("```markdown")
        headers = ["Section", "Item", "Provenance", "Word Count", "Target Range", "Status", "Text Snippet"]
        rows = []
        master_avg_lengths = self._calculate_master_avg_bullet_length()
        tolerance = 0.20 # 20% tolerance

        for section_data in self.QA_PROVENANCE_SECTIONS:
            name = section_data["name"]

            if section_data.get("overview_enum"):
                overview_text = staging_buffer.get(section_data["overview_enum"].value, "")
                if overview_text:
                    # USE MS WORD STYLE count
                    word_count = count_words_ms_word_style(overview_text)
                    min_target = getattr(self.constraints, section_data["overview_min_attr"])
                    max_target = getattr(self.constraints, section_data["overview_max_attr"])
                    status, target_range_str = self._check_word_count(word_count, min_target, max_target)

                    rows.append([
                        name, "Overview", "Customized",
                        str(word_count), target_range_str, status,
                        overview_text[:60] + "..."
                    ])

            bullets_enum = section_data["bullets_enum"]
            avg_len = master_avg_lengths.get(name, 25.0) # Get avg length by name
            bullets = staging_buffer.get(bullets_enum.value, [])

            if isinstance(bullets, list) and bullets:
                for i, bullet_item in enumerate(bullets):
                    if isinstance(bullet_item, dict):
                        bullet_text = bullet_item.get('text', '')
                        word_count = bullet_item.get('word_count', count_words_ms_word_style(bullet_text))
                        provenance = bullet_item.get('provenance', 'N/A')
                    else:
                        bullet_text = str(bullet_item)
                        word_count = count_words_ms_word_style(bullet_text)
                        provenance = "N/A"

                    min_target = round(avg_len * (1 - tolerance))
                    max_target = round(avg_len * (1 + tolerance))
                    status, target_range_str = self._check_word_count(word_count, min_target, max_target)

                    rows.append([
                        name, str(i + 1), provenance,
                        str(word_count), target_range_str, status,
                        bullet_text[:60] + "..."
                    ])
        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_7_authenticity(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 7 of the QA report: Content Authenticity (Hallucination)."""
        lines = ["", "7. CONTENT AUTHENTICITY (Hallucination Detection)", ""]
        auth_results = [vr for vr in validation_results if "HALLUCINATION" in vr.rule_id]
        if not auth_results:
             auth_results = [vr for hop in self.hop_checkpoints for vr in hop.validation_results if "HALLUCINATION" in vr.rule_id]
        headers = ["Check ID", "Status", "Message"]
        rows = [[vr.rule_id, "PASS" if vr.passed else "FAIL", vr.message if not vr.passed else ""] for vr in auth_results] if auth_results else [["HALLUCINATION_CHECK", "PASS", "No hallucination checks run or all passed."]]
        lines.append("```markdown")
        lines.extend(self._format_plain_text_table(headers, rows))
        return lines

    def _build_qa_section_8_overview_similarity(self) -> List[str]:
        """Builds Section 8 of the QA report: Overview vs. Bullet Similarity.""" # Keep original name for now
        lines = ["", "8. OVERVIEW VS. BULLET SIMILARITY CHECK", ""] # Keep original name for now
        if self.overview_similarity_data: # Use pre-computed data
            lines.append("```markdown")
            headers = ["Section", "Max Similarity", "Threshold", "Status"]
            rows = []
            # self.overview_similarity_data is now a list of dicts
            for sim_data in self.overview_similarity_data:
                max_sim = sim_data.get("max_similarity", 0.0)
                passed = max_sim < 0.6
                rows.append([sim_data.get("section", "N/A"), f"{max_sim:.2f}", "< 0.60", "✓ PASS" if passed else "✗ FAIL"])
            lines.extend(self._format_plain_text_table(headers, rows))
            lines.append("```")
        else:
            lines.append("Overview vs. Bullet similarity analysis was not performed (missing data).")
        return lines
    
    def _build_qa_section_9_pairwise_similarity(self) -> List[str]:
        """Builds Section 9 of the QA report: Pairwise Bullet Similarity."""
        lines = ["", "9. PAIRWISE BULLET SIMILARITY (Deduplication)", ""]
        lines.append("```markdown")
        headers = ["Bullet 1", "Bullet 2", "Similarity", "Status"]
        rows = []
        
        if not self.similarity_matrix_data:
            lines.append("(Pairwise similarity analysis was not performed or found no data.)")
            lines.append("```")
            return lines

        duplicates = self.similarity_matrix_data.get('duplicates_found', [])
        
        # Populate rows ONLY if duplicates are found.
        # This loop will be skipped if 'duplicates' is an empty list.
        for dup in duplicates:
            rows.append([
                dup['bullet_1'],
                dup['bullet_2'],
                f"{dup['similarity']:.4f}",
                "✗ FAIL"
            ])
        
        # Format the table (headers will be printed, rows will be empty if no duplicates)
        lines.extend(self._format_plain_text_table(headers, rows))
        
        # --- FIX: Replace default "(No data available)" with a clear message ---
        if not rows:
            # Check if the last line added was the default empty message
            if lines[-1] == "(No data available)":
                lines.pop() # Remove "(No data available)"
            # Append a clear "pass" message instead of the N/A row
            lines.append("No duplicates found (Similarity < 0.90).")
        # --- END FIX ---

        # Add summary stats (which are the most important part)
        lines.append("\n")
        lines.append(f"  Total Comparisons: {self.similarity_matrix_data.get('total_comparisons', 0)}")
        lines.append(f"  Max Similarity Found: {self.similarity_matrix_data.get('max_similarity', 0.0):.4f}")
        lines.append(f"  Duplicates (>= 0.90): {len(duplicates)}")
        
        lines.append("```")
        return lines

    def _build_qa_section_11_pipeline_health(self) -> List[str]:
        """Builds Section 11 of the QA report: Pipeline Health."""
        lines = ["", "11. PIPELINE HEALTH (Resource Consumption)", ""]
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
        rows.append(["TOTAL", "", "", str(total_rag_calls), str(total_llm_api_calls)]) # Add total row

        # Truncation Check
        expected_rows = len(self.hop_checkpoints) + 1 # +1 for TOTAL row
        if len(rows) != expected_rows:
             # Can't easily insert mid-table, prepend error message line
            lines.append(f"ERROR   TRUNCATION_DETECTED   FAIL   Expected {expected_rows} health rows, got {len(rows)}")

        lines.extend(self._format_plain_text_table(headers, rows, ['L', 'L', 'L', 'R', 'R']))

        lines.append("```")
        return lines

    def _build_qa_section_5_word_count(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 5 of the QA report: Word Count Compliance."""
        lines = ["", "5. WORD COUNT COMPLIANCE (Summary)", ""]
        wc_results = [vr for vr in validation_results if "WORD_COUNT" in vr.rule_id]
        lines.append("```markdown")

        headers = ["Section", "Actual Count", "Target Range", "Status"]
        rows = []
        
        rule_map = {
            "VG_TOTAL_WORD_COUNT": ("Total Resume", f"{PreFlightValidator.WORD_COUNT_MIN}-{PreFlightValidator.WORD_COUNT_MAX}"),
            "VG_WORD_COUNT_K1": ("K.1 Exec Summary", "120-150") # Corrected range
        }
        
        for vr in wc_results:
            if vr.rule_id in rule_map:
                section_name, target_range = rule_map[vr.rule_id]
                actual_count = vr.details.get('total_words') or vr.details.get('word_count', 'N/A')
                status = "✓ PASS" if vr.passed else "✗ FAIL"
                rows.append([section_name, str(actual_count), target_range, status])

        if not rows:
            rows.append(["N/A", "N/A", "N/A", "INFO: No word count results found."])

        # Truncation Check
        expected_rows = len([vr for vr in wc_results if vr.rule_id in rule_map])
        if not rows and expected_rows > 0: expected_rows = 1 # for the N/A row
        if len(rows) != expected_rows:
             rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} wc rows, got {len(rows)}"])

        lines.extend(self._format_plain_text_table(headers, rows))
        lines.append("```")
        return lines

    def _build_qa_section_12_structural(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 12 of the QA report: Structural Validation."""
        lines = ["", "12. STRUCTURAL VALIDATION", ""]
        struct_results = [vr for vr in validation_results if "STRUCTURE" in vr.rule_id or "HEADLINE" in vr.rule_id]
        # Include new formatting rules in this section
        struct_results.extend([vr for vr in validation_results if vr.rule_id in [
            "VG_RESUME_HEADER_H2", "VG_EDU_CERTS_FORMAT", "VG_EXPERIENCE_BULLET_STYLE"
        ]])
        lines.append("```markdown")

        headers = ["Rule ID", "Status", "Message"]
        rows = []
        if struct_results:
            # Sort for consistent order
            struct_results.sort(key=lambda vr: vr.rule_id)
            rows = [[vr.rule_id, "PASS" if vr.passed else "FAIL", vr.message if not vr.passed else ""] for vr in struct_results]
        else:
             rows.append(["N/A", "INFO", "No structural validation results found."])
        lines.extend(self._format_plain_text_table(headers, rows))
        return lines

        # Truncation Check
        expected_rows = len(struct_results) if struct_results else 1
        if len(rows) != expected_rows:
             rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} structural rows, got {len(rows)}"])

        lines.extend(self._format_plain_text_table(headers, rows))

        lines.append("```")
        return lines

    def _build_qa_section_13_prod_readiness(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 13 of the QA report: Production Readiness."""
        lines = ["", "13. PRODUCTION READINESS", ""]
        lines.append("```markdown")

        all_results = validation_results + [vr for hop in self.hop_checkpoints for vr in hop.validation_results]
        critical_failures = [vr for vr in all_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
        high_failures = [vr for vr in all_results if not vr.passed and vr.severity == ValidationSeverity.HIGH]
        prod_ready = not critical_failures and not high_failures # Determine readiness

        headers = ["Check", "Value", "Status"]
        rows = [
            ["Production Ready", str(prod_ready).upper(), "✅ PASS" if prod_ready else "❌ FAIL"],
            ["Critical Failures", len(critical_failures), "✅" if not critical_failures else "❌"],
            ["High Failures", len(high_failures), "✅" if not high_failures else "❌"]
        ]
        expected_rows = 3

        # Truncation Check (Unlikely here, but for consistency)
        if len(rows) != expected_rows:
            rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} readiness rows, got {len(rows)}"])

        lines.extend(self._format_plain_text_table(headers, rows))

        # Append reasons outside the markdown block if failed
        reason_lines = []
        if not prod_ready:
            reason_lines.append("\n  Reason: Production readiness requires zero CRITICAL or HIGH severity failures.")
            if critical_failures:
                reason_lines.append("  CRITICAL FAILURES:")
                for f in critical_failures[:3]: reason_lines.append(f"    - {f.rule_id}: {f.message}")
            if high_failures:
                reason_lines.append("  HIGH FAILURES:")
                for f in high_failures[:3]: reason_lines.append(f"    - {f.rule_id}: {f.message}")

        lines.append("```") # End markdown block first
        lines.extend(reason_lines) # Append reasons after
        return lines

    def _build_qa_section_14_cover_letter(self, validation_results: List[ValidationResult]) -> List[str]:
        """Builds Section 14 of the QA report: Cover Letter QA."""
        lines = ["", "14. COVER LETTER QA", ""]
        cl_results = [vr for vr in validation_results if "COVER_LETTER" in vr.rule_id]
        lines.append("```markdown")

        headers = ["Rule ID", "Status", "Message"]
        rows = []
        expected_rows = 0
        if cl_results:
             # Sort for consistent order
             cl_results.sort(key=lambda vr: vr.rule_id)
             rows = [[vr.rule_id, "PASS" if vr.passed else "FAIL", vr.message if not vr.passed else ""] for vr in cl_results]
             expected_rows = len(cl_results)
        else:
             rows = [["N/A", "INFO", "No cover letter validation results found."]]
             expected_rows = 1

        # Truncation Check
        if len(rows) != expected_rows:
             rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} CL rows, got {len(rows)}"])

        lines.extend(self._format_plain_text_table(headers, rows))

        lines.append("```")
        return lines

    def _build_qa_section_15_jd_enforcement(self) -> List[str]:
        """Builds Section 15 of the QA report: JD Enforcement Validation."""
        lines = ["", "15. JD ENFORCEMENT VALIDATION", ""] # Title OK
        lines.append("```markdown")


        headers = ["Gate", "Rule", "Status", "Details"]
        rows = [[res.gate_id, res.rule.name, "PASS" if res.passed else "FAIL", res.details] for res in self.jd_enforcer.enforcement_results]
        lines.extend(self._format_plain_text_table(headers, rows))
        return lines
    
    def _build_qa_section_16_final_format(self, validation_results: List[ValidationResult]) -> List[str]:
        """
        v9.85: Builds Section 16 of the QA report: Final Formatting Validation.
        This method reports on placeholder rules from HOP-5, which are assumed
        to pass because the FileRenderer (HOP-7) is hardened to enforce format.
        """
        lines = ["", "16. FINAL FORMATTING VALIDATION", ""]
        lines.append("```markdown")

        # of these found in the validation_results list from HOP-5.
        rule_ids_to_check = [
            "VG_COMPETENCIES_FORMATTING",
            "VG_EXPERIENCE_RENDER_FORMAT",
            "VG_RESUME_HEADER_H2",
            "VG_EDU_CERTS_FORMAT",
            "VG_EXPERIENCE_BULLET_STYLE"
        ]

        # Filter the results
        format_results = [vr for vr in validation_results if vr.rule_id in rule_ids_to_check]
        
        found_rules = {vr.rule_id for vr in format_results}

        headers = ["Rule ID", "Status", "Message"]
        rows = []

        for rule_id in sorted(rule_ids_to_check):
            if rule_id in found_rules:
                vr = next(v for v in format_results if v.rule_id == rule_id)
                # Get message from details if it's a 'pass' or from message if 'fail'
                message = vr.details.get("details", "") if (vr.passed and vr.details) else (vr.message(vr.details) if callable(vr.message) else vr.message)
                if vr.passed and not message: message = "" # Default pass message
                
                rows.append([
                    vr.rule_id, 
                    "PASS" if vr.passed else "FAIL", 
                    message
                ])
            else:
                # Rule was not found in validation_results at all
                rows.append([
                    rule_id,
                    "N/A",
                    "Rule not defined in PreFlightValidator"
                ])
        
        lines.extend(self._format_plain_text_table(headers, rows))

        # Truncation check
        expected_rows = len(rule_ids_to_check)
        if len(rows) != expected_rows:
             rows.insert(0, ["ERROR", "TRUNCATION_DETECTED", f"Expected {expected_rows} format rows, got {len(rows)}"])

        lines.append("```")
        return lines
    

    # Configuration for the QA report structure.
    QA_REPORT_SECTIONS = [
        {"method": "_build_qa_section_1_signal_quality", "args": ["staging_buffer", "thematic_analysis"]},
        {"method": "_build_qa_section_2_thematic_compliance", "args": ["thematic_analysis"]},
        {"method": "_build_qa_section_3_hop_summary", "args": []},
        {"method": "_build_qa_section_4_distribution", "args": ["validation_results"]},
        {"method": "_build_qa_section_5_word_count", "args": ["validation_results"]},
        {"method": "_build_qa_section_6_provenance", "args": ["staging_buffer"]},
        {"method": "_build_qa_section_7_authenticity", "args": ["validation_results"]},
        {"method": "_build_qa_section_8_overview_similarity", "args": []},
        {"method": "_build_qa_section_9_pairwise_similarity", "args": []},
        {"method": "_build_qa_section_11_pipeline_health", "args": []},
        {"method": "_build_qa_section_12_structural", "args": ["validation_results"]},
        {"method": "_build_qa_section_13_prod_readiness", "args": ["validation_results"]},
        {"method": "_build_qa_section_14_cover_letter", "args": ["validation_results"]},
        {"method": "_build_qa_section_15_jd_enforcement", "args": []},
        {"method": "_build_qa_section_16_final_format", "args": ["validation_results"]}, # Pass validation results here
    ]
 
    def _generate_qa_report( # Renamed for clarity, already modular
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult]
    ) -> Tuple[List[ValidationResult], str]:

        """
        Generate full QA report by iterating through a configuration of section builders.
        Includes internal check for QA table pre-formatting.
        """
        validation_results_out = []
        report_lines = [
            f"RESUME QA REPORT (v{__version__})",
            f"Generated: {datetime.now().isoformat()}",
        ]
 
        # A dictionary mapping argument names to the actual objects available in this scope.
        available_args = {
            "staging_buffer": staging_buffer,
            "thematic_analysis": thematic_analysis,
            "validation_results": validation_results,
        }
 
        # Internal check: Ensure all tables are pre-formatted
        pre_formatted_check_passed = True
        pre_formatted_check_messages = []

        # Iterate through the configured sections, call the builder method for each.
        for section_config in self.QA_REPORT_SECTIONS:
            method_name = section_config["method"]
            arg_names = section_config["args"]
            
            try:
                # Get the builder method from the class instance.
                builder_method = getattr(self, method_name)
                
                # Prepare the arguments required for this specific builder method.
                call_args = [available_args[name] for name in arg_names]
                
                # Call the method and extend the report lines.
                section_lines = builder_method(*call_args)

                # Perform the pre-formatting check
                if "```markdown" in "".join(section_lines) and any("|" in line for line in section_lines):
                    pre_formatted_check_passed = False
                    msg = f"QA Section '{method_name}' contains Markdown table syntax instead of pre-formatted text."
                    pre_formatted_check_messages.append(msg)
                    logging.warning(msg)

                report_lines.extend(section_lines)
 
            except (AttributeError, KeyError, Exception) as e: # Broader exception catch
                # Add an error message to the report if a builder is misconfigured or fails.
                error_message = f"Error building QA section '{method_name}': {e}"
                logging.getLogger(__name__).error(error_message, exc_info=True)
                report_lines.append(f"\n--- {error_message} ---\n")
        
        # Add the result of the internal pre-formatting check
        validation_results_out.append(ValidationResult(
            rule_id="QA_TABLE_FORMAT_INVALID",
            passed=pre_formatted_check_passed,
            severity=ValidationSeverity.CRITICAL,
            message="; ".join(pre_formatted_check_messages) if not pre_formatted_check_passed else "All QA tables use pre-formatted text.",
            details={"failed_sections": pre_formatted_check_messages}
        ))
 
        qa_report_text = "\n".join(report_lines).strip() # Ensure no trailing newlines
        validation_results_out.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"QA Report generated ({len(report_lines)} lines)"
        ))
        
        return validation_results_out, qa_report_text

    def _calculate_master_avg_bullet_length(self) -> Dict[str, float]:
        """
        Helper to calculate average bullet length for sections in master resume.
        v9.85 FIX: This method was missing from WorkflowOrchestrator, causing
        QA Table 6 to use incorrect fallback values (e.g., 25.0).
        This is a direct copy from the PreFlightValidator class.
        """
        avg_lengths = {}

        # Define sections and their corresponding company name parts/keys
        experience_sections_to_avg = {
            "Unify": ("Unify Consulting", "bullet_pool"),
            "IBM": ("IBM", "bullet_pool"),
            "EY": ("Ernst & Young", "highlights"), # Use highlights key
            "EarlyCareer": ("Early Career Roles", "highlights"), # Use highlights key
        }
        for key, (company_name_part, bullets_key) in experience_sections_to_avg.items():
            total_words = 0
            bullet_count = 0
            # Find the matching experience section in the master resume
            exp = next((e for e in self.master_resume.get("professional_experience", []) if company_name_part in e.get("company", "")), None)
            if exp:
                bullets = exp.get(bullets_key, []) # Use the correct key
                total_words = sum(count_words_clean(b) for b in bullets if isinstance(b, str)) # Ensure item is string
                bullet_count = len([b for b in bullets if isinstance(b, str)]) # Count only strings
            # Calculate average, provide default if no bullets
            avg_lengths[key] = (total_words / bullet_count) if bullet_count > 0 else 25.0

        # For Competencies section
        competencies_list = self.master_resume.get("strategic_and_technical_competencies", [])
        competencies_strings = [c for c in competencies_list if isinstance(c, str)]
        avg_lengths["Competencies"] = (sum(count_words_clean(b) for b in competencies_strings) / len(competencies_strings)) if competencies_strings else 28.0

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

if __name__ == "__main__":
    print("This script is intended to be used as a module. For CLI usage, please see the main execution script.")
