# File: validation_stack.py
# Version: Consolidated 5.4 (Patched)
# Fixes: Restored missing validation rules (forbidden verbs, intro phrases)
# Zero-Loss Consolidation - The V18 Engine
# Merges: validation_context.py → validation_rules.py → validation_engine.py → validator_RES.py

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import json
import logging
import re
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from core.py (previously models_RES.py and config_RES.py)
from core import (
    # Models
    ImmutableStagingBuffer, ThematicAnalysis, ResumeSection, ValidationResult,
    ValidationSeverity, FactualFailureException, GenerationAttempt,
    # Config
    CONFIG, DEFAULT_GENERATION_TEMPERATURE, ACCEPTABLE_MIN_WC, ACCEPTABLE_MAX_WC,
    # Utils
    text_utils, fence_data, CodeInterpreterTool,
    # Prompts
    get_validation_prompt
)

logger = logging.getLogger(__name__)

# ============================================================================
# PART 1: VALIDATION CONTEXT (from validation_context.py)
# ============================================================================

def calculate_signal_score(text: str, job_desc: str, thematic_analysis: ThematicAnalysis) -> float:
    """Calculate signal quality score for text."""
    if not text or not job_desc:
        return 0.0
    
    # Extract keywords from JD
    jd_keywords = set(text_utils.extract_keywords(job_desc, 30))
    theme_keywords = set(thematic_analysis.themes) if thematic_analysis else set()
    all_keywords = jd_keywords.union(theme_keywords)
    
    # Calculate overlap
    text_keywords = set(text_utils.extract_keywords(text, 20))
    overlap = text_keywords.intersection(all_keywords)
    
    if len(all_keywords) == 0:
        return 0.5
    
    return len(overlap) / len(all_keywords)

class ValidationContext:
    """
    Holds all necessary data for the ValidationEngine to run checks.
    Uses lazy calculation for metrics.
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, 
                 job_description: str, master_resume: Dict, app_config: Any = None):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {}
        self.config = app_config or CONFIG
        
        # Handle constraints from config
        if hasattr(self.config, 'constraints'):
            self.constraints = self.config.constraints
        else:
            # Create default constraints
            self.constraints = type('Constraints', (), {
                'TOTAL_WORD_COUNT_MIN': 450,
                'TOTAL_WORD_COUNT_MAX': 650,
                'EXEC_SUMMARY_SENTENCE_COUNT_MIN': 4,
                'EXEC_SUMMARY_SENTENCE_COUNT_MAX': 6,
                'BULLET_WORD_COUNT_MIN': ACCEPTABLE_MIN_WC,
                'BULLET_WORD_COUNT_MAX': ACCEPTABLE_MAX_WC,
                'K9_COMPETENCIES_ITEMS_MIN': 3,
                'K9_COMPETENCIES_ITEMS_MAX': 6,
                'COVER_LETTER_WORD_COUNT_MIN': 250,
                'COVER_LETTER_WORD_COUNT_MAX': 400,
                'JD_SKILLS_OVERLAP_MIN': 3,
                'CROSS_SECTION_SIMILARITY_MAX': 0.60,
                'NARRATIVE_VS_MASTER_MIN': 0.40,
                'NARRATIVE_VS_MASTER_MAX': 0.80,
                'SIGNAL_SCORE_THRESHOLD': CONFIG.min_confidence_score
            })()
        
        # Handle signal constraints
        if hasattr(self.config, 'signal_constraints'):
            self.signal_constraints = self.config.signal_constraints
        else:
            self.signal_constraints = type('SignalConstraints', (), {
                'MIN_SIGNAL_SCORE': CONFIG.min_confidence_score,
                'MIN_JD_ALIGNMENT': CONFIG.min_relevance_score
            })()
        
        self.logger = logging.getLogger(__name__)
        
        # Expected signature for cover letter
        if master_resume and 'owner' in master_resume:
            self.expected_signature = master_resume['owner'].get('name', 'Your Name')
        else:
            self.expected_signature = 'Your Name'
    
    def get_details_for_rule(self, rule_id: str) -> Dict:
        """Retrieves cached details for a given rule ID."""
        return self._cache.get(rule_id, {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from staging buffer data."""
        if hasattr(self.staging_buffer, 'data'):
            return self.staging_buffer.data.get(key, default)
        elif hasattr(self.staging_buffer, 'hop_results'):
            # Search in hop results
            for result in self.staging_buffer.hop_results:
                if result.data and key in result.data:
                    return result.data[key]
        return default
    
    def _calculate_metric_details(self, section_enum: ResumeSection, 
                                 metrics_to_calc: List[Tuple[str, Callable]], 
                                 constraints: Dict[str, Any]) -> Dict:
        """Helper to calculate and cache metrics for a section."""
        text = self.get(section_enum.value, '')
        details = {}
        for metric_name, calc_func in metrics_to_calc:
            try:
                details[metric_name] = calc_func(text) if isinstance(text, (str, list)) else 0
            except Exception as e:
                self.logger.warning(f"Error calculating metric '{metric_name}' for section {section_enum.name}: {e}")
                details[metric_name] = "Error"
        
        details.update(constraints)
        return details
    
    def __getattr__(self, name):
        """
        Magic method for lazy calculation of metrics.
        """
        if name in self._cache:
            return self._cache[name]
        
        # For detail caches (e.g., "k1_sentence_count_details")
        if name.endswith('_details'):
            calculation_method_details = getattr(self, f"_calculate_{name}", None)
            if calculation_method_details:
                value = calculation_method_details()
                return value
        
        # For simple value caches (e.g., "total_words")
        calculation_method = getattr(self, f"_calculate_{name}", None)
        if calculation_method:
            value = calculation_method()
            self._cache[name] = value
            return value
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    # --- Lazy Calculation Methods ---
    
    def _calculate_total_words(self):
        total = 0
        for key_enum in ResumeSection:
            key = key_enum.value
            if key_enum not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT] and \
               not key.endswith("_HEADER"):
                value = self.get(key)
                if isinstance(value, str):
                    total += text_utils.count_words(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            text = item.get('text', str(item))
                        else:
                            text = str(item)
                        total += text_utils.count_words(text)
        
        details = {
            'total_words': total, 
            'min': self.constraints.TOTAL_WORD_COUNT_MIN, 
            'max': self.constraints.TOTAL_WORD_COUNT_MAX
        }
        self._cache["H5_GLOBAL_TOTAL_WORD_COUNT"] = details
        return total
    
    def _calculate_k1_sentence_count_details(self):
        def count_sentences(text):
            """Count sentences in text."""
            if not text:
                return 0
            sentences = re.split(r'[.!?]+', text)
            return len([s for s in sentences if s.strip()])
        
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('sentence_count', count_sentences)],
            constraints={
                'min': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN, 
                'max': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX
            }
        )
        self._cache["H3_K1_SENTENCE_COUNT"] = details
        return details
    
    def _calculate_k1_word_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('word_count', text_utils.count_words)],
            constraints={'min': 70, 'max': 120}
        )
        self._cache["H3_K1_WORD_COUNT"] = details
        return details
    
    def _calculate_bullet_word_counts_details(self):
        """Calculate word counts for all bullets."""
        bullet_sections = [ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS]
        all_bullets_wc = []
        violations = []
        
        for section_enum in bullet_sections:
            bullets = self.get(section_enum.value, [])
            if isinstance(bullets, list):
                for i, bullet in enumerate(bullets):
                    if isinstance(bullet, dict):
                        text = bullet.get('text', str(bullet))
                    else:
                        text = str(bullet)
                    wc = text_utils.count_words(text)
                    all_bullets_wc.append(wc)
                    if wc < self.constraints.BULLET_WORD_COUNT_MIN or wc > self.constraints.BULLET_WORD_COUNT_MAX:
                        violations.append(f"{section_enum.name}[{i}]: {wc} words")
        
        details = {
            'all_bullets_wc': all_bullets_wc,
            'violations': violations,
            'min': self.constraints.BULLET_WORD_COUNT_MIN,
            'max': self.constraints.BULLET_WORD_COUNT_MAX
        }
        self._cache["H4_BULLET_WORD_COUNTS"] = details
        return details
    
    def _calculate_cross_section_similarity_details(self):
        """Calculate similarity between sections."""
        sections_to_compare = [
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K9_COMPETENCIES
        ]
        
        failures = []
        for i, sec1 in enumerate(sections_to_compare):
            text1 = self.get(sec1.value, '')
            if not text1:
                continue
            for sec2 in sections_to_compare[i+1:]:
                text2 = self.get(sec2.value, '')
                if not text2:
                    continue
                similarity = text_utils.calculate_similarity(text1, text2)
                if similarity > self.constraints.CROSS_SECTION_SIMILARITY_MAX:
                    failures.append(f"{sec1.name} vs {sec2.name}: {similarity:.2%}")
        
        details = {
            'failures': failures,
            'threshold': self.constraints.CROSS_SECTION_SIMILARITY_MAX
        }
        self._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = details
        return details
    
    def _calculate_narrative_vs_master_similarity_details(self):
        """Calculate similarity between narratives and master resume."""
        narrative_sections = [
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE
        ]
        
        section_results = []
        failures = []
        
        # Create master text from all experience
        master_text = ""
        if self.master_resume and 'professional_experience' in self.master_resume:
            for exp in self.master_resume['professional_experience']:
                if 'bullet_pool' in exp:
                    master_text += " ".join(exp['bullet_pool'])
                if 'highlights' in exp:
                    master_text += " ".join(exp['highlights'])
        
        for section in narrative_sections:
            text = self.get(section.value, '')
            if text and master_text:
                similarity = text_utils.calculate_similarity(text, master_text)
                valid_range = (self.constraints.NARRATIVE_VS_MASTER_MIN <= similarity <= 
                              self.constraints.NARRATIVE_VS_MASTER_MAX)
                
                section_result = {
                    'section': section.name,
                    'similarity': similarity,
                    'valid_range': valid_range
                }
                section_results.append(section_result)
                
                if not valid_range:
                    failures.append(f"{section.name}: {similarity:.2%}")
        
        details = {
            'section_results': section_results,
            'failures': failures,
            'min': self.constraints.NARRATIVE_VS_MASTER_MIN,
            'max': self.constraints.NARRATIVE_VS_MASTER_MAX
        }
        self._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = details
        return details
    
    def _calculate_jd_skills_overlap_details(self):
        """Calculate overlap with JD skills."""
        jd_skills = set()
        if self.thematic_analysis and self.thematic_analysis.skills_required:
            jd_skills = set(s.lower() for s in self.thematic_analysis.skills_required)
        
        # Collect all text from resume
        resume_text = ""
        for section_enum in ResumeSection:
            content = self.get(section_enum.value, '')
            if isinstance(content, str):
                resume_text += " " + content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        resume_text += " " + item.get('text', str(item))
                    else:
                        resume_text += " " + str(item)
        
        resume_text_lower = resume_text.lower()
        found_skills = [skill for skill in jd_skills if skill in resume_text_lower]
        
        details = {
            'jd_skills': list(jd_skills),
            'found_skills': found_skills,
            'overlap_count': len(found_skills),
            'min_required': self.constraints.JD_SKILLS_OVERLAP_MIN
        }
        self._cache["S1_JD_SKILLS_OVERLAP"] = details
        return details

# ============================================================================
# PART 2: VALIDATION RULES (from validation_rules.py)
# ============================================================================

# Regex Patterns
PROMPT_CONTAMINATION_PATTERN = re.compile(
    r"\b(MUST|CRITICAL|ABSOLUTELY|Do NOT|Output ONLY|Return ONLY|JSON structure|Word count:|Sentence count:|Target range:|strictly between)\b", 
    re.IGNORECASE
)
CONVERSATIONAL_FILLERS_PATTERN = re.compile(
    r"^(Here is the|Certainly,|I have generated|Below is the|Apologies,|Please note)\b", 
    re.IGNORECASE | re.MULTILINE
)
EMPTY_LIST_ITEM_PATTERN = re.compile(r"^\s*[\*\-]\s*($|\n)", re.MULTILINE)
BANNED_INTRO_PHRASES_PATTERN = re.compile(
    r"^(In my role as|As a|At \[Company\]|My responsibilities included|Responsible for)\b", 
    re.IGNORECASE
)

# --- V5.4 FIX: FORBIDDEN VERBS PATTERN ---
FORBIDDEN_VERBS = [
    "spearheaded", "leveraged", "utilized", "facilitated", "orchestrated",
    "championed", "pioneered", "revolutionized", "transformed", "synergized"
]
FORBIDDEN_VERBS_PATTERN = re.compile(
    r"\b(" + "|".join(FORBIDDEN_VERBS) + r")\b", 
    re.IGNORECASE
)
# -----------------------------------------

# Validation Rule Functions

def _validate_cross_section_similarity(context: ValidationContext) -> bool:
    """Validate cross-section similarity is below threshold."""
    try:
        details = context.cross_section_similarity_details
        if details.get("failures"):
            failed_sections_set = set()
            sections_to_compare_map = {
                ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW,
                ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE,
                ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
                ResumeSection.K9_COMPETENCIES
            }
            for failure_str in details["failures"]:
                match = re.match(r"(\w+)\s+vs\s+(\w+):", failure_str)
                if match:
                    name1, name2 = match.groups()
                    for enum_member in sections_to_compare_map:
                        if enum_member.name == name1:
                            failed_sections_set.add(enum_member)
                        if enum_member.name == name2:
                            failed_sections_set.add(enum_member)
            context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"]["failed_sections"] = [s.name for s in failed_sections_set]
            return False
        return True
    except Exception as e:
        logger.error(f"Error during cross-section similarity validation: {e}")
        context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = {
            "failures": [f"Validation error: {e}"], 
            "failed_sections": []
        }
        return False

def _validate_narrative_vs_master_similarity(context: ValidationContext) -> bool:
    """Validate narrative similarity to master is within range."""
    try:
        details = context.narrative_vs_master_similarity_details
        if details.get("failures"):
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
                                break
            context._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"]["failed_sections"] = [s.name for s in failed_sections_set]
            return False
        return True
    except Exception as e:
        logger.error(f"Error during narrative vs master similarity validation: {e}")
        context._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = {
            "failures": [f"Validation error: {e}"], 
            "failed_sections": []
        }
        return False

def _validate_section_presence(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Validate that a section has content."""
    content = context.get(section_enum.value)
    if content is None:
        return False
    if isinstance(content, str):
        return content.strip() not in ["", "HEADER_PLACEHOLDER"] and not content.strip().startswith("[Placeholder")
    if isinstance(content, (list, dict)):
        return bool(content)
    return True

def _validate_cover_letter_full_structure(context: ValidationContext) -> bool:
    """Validate cover letter has all required structural elements."""
    text = context.get(ResumeSection.K11_COVER_LETTER.value, '')
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
    
    if not valid:
        context._cache["H3_K11_COVER_LETTER_FULL_STRUCTURE"] = {
            "has_date": has_date,
            "has_recipient": has_recipient,
            "has_salutation": has_salutation,
            "has_closing": has_closing,
            "has_signature": has_signature,
            "paras_found": paras_found
        }
    
    return valid

def _validate_no_prompt_contamination(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Check for LLM prompt contamination in output."""
    text = context.get(section_enum.value, '')
    if isinstance(text, list):
        text = ' '.join([item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in text])
    
    matches = PROMPT_CONTAMINATION_PATTERN.findall(text)
    if matches:
        context._cache[f"H2_NO_PROMPT_CONTAMINATION_{section_enum.name}"] = {"matches": matches}
        return False
    return True

def _validate_no_conversational_fillers(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Check for conversational fillers."""
    text = context.get(section_enum.value, '')
    if isinstance(text, list):
        text = ' '.join([item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in text])
    
    matches = CONVERSATIONAL_FILLERS_PATTERN.findall(text)
    if matches:
        context._cache[f"H2_NO_CONVERSATIONAL_FILLERS_{section_enum.name}"] = {"matches": matches}
        return False
    return True

def _validate_jd_skills_overlap(context: ValidationContext) -> bool:
    """Validate sufficient JD skills are included."""
    details = context.jd_skills_overlap_details
    return details.get('overlap_count', 0) >= details.get('min_required', 3)

def _validate_signal_score(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Validate signal score meets threshold."""
    text = context.get(section_enum.value, '')
    if isinstance(text, list):
        text = ' '.join([item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in text])
    
    score = calculate_signal_score(text, context.job_description, context.thematic_analysis)
    threshold = context.signal_constraints.MIN_SIGNAL_SCORE
    
    context._cache[f"S2_SIGNAL_SCORE_{section_enum.name}"] = {
        "score": score,
        "threshold": threshold
    }
    
    return score >= threshold

# --- V5.4 FIX: ADD MISSING VALIDATOR FUNCTIONS ---
def _validate_forbidden_verbs(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Check for forbidden verbs in a section."""
    text = context.get(section_enum.value, '')
    if isinstance(text, list):
        text = ' '.join([item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in text])
    
    matches = FORBIDDEN_VERBS_PATTERN.findall(text)
    if matches:
        # Cache details for error message
        context._cache[f"H2_NO_FORBIDDEN_VERBS_{section_enum.name}"] = {"matches": list(set(matches))}
        return False
    return True

def _validate_no_intro_phrases(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Check for banned introductory phrases."""
    text = context.get(section_enum.value, '')
    # Intro phrases usually only matter for narrative text, not bullet lists
    if isinstance(text, str):
        matches = BANNED_INTRO_PHRASES_PATTERN.findall(text)
        if matches:
            context._cache[f"H2_NO_INTRO_PHRASES_{section_enum.name}"] = {"matches": matches}
            return False
    return True

def _validate_canonical_verbs(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Check if section uses strong canonical verbs from enricher_rules."""
    text = context.get(section_enum.value, '')
    if not isinstance(text, str): return True
    
    # Load canonical verbs from CONFIG
    enricher_rules = context.config.enricher_rules.get('canonical_verbs', {})
    all_strong_verbs = set()
    for category in enricher_rules.values():
        all_strong_verbs.update([v.lower() for v in category])
        
    if not all_strong_verbs: return True # Skip if config missing
    
    # Rough check for at least SOME strong verbs in long sections
    if len(text.split()) > 50:
        text_lower = text.lower()
        strong_verb_count = sum(1 for verb in all_strong_verbs if f" {verb} " in text_lower)
        if strong_verb_count < 2: # Arbitrary low threshold for basic validation
             context._cache[f"QUALITY_WEAK_VERBS_{section_enum.name}"] = {"count": strong_verb_count}
             return False
    return True

def _validate_style_hyphenation(context: ValidationContext, section_enum: ResumeSection) -> bool:
    """Enforce hyphenation rules from config."""
    text = context.get(section_enum.value, '')
    if not isinstance(text, str): return True

    hyphen_rules = context.config.hyphenation_rules.get('rules', {})
    to_remove = hyphen_rules.get('unnatural_hyphens_remove', [])
    
    for rule in to_remove:
        if rule['from'] in text:
             context._cache[f"STYLE_HYPHEN_{section_enum.name}"] = {"violation": rule['from']}
             return False
    return True
# ------------------------------------------------

# ------------------------------------------------

# ============================================================================
# PART 3: VALIDATION ENGINE (from validation_engine.py)
# ============================================================================

class ValidationRule:
    """Represents a single executable validation rule."""
    
    def __init__(self, rule_id: str, severity: ValidationSeverity, 
                 validator: Any, error_message: Union[str, Callable[[Dict], str]], 
                 category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category
    
    def execute(self, data: Union[Dict, ValidationContext]) -> ValidationResult:
        """Executes the validation rule against the provided data."""
        try:
            # The validator function is called with the data/context
            passed = self.validator(data)
            
            error_msg = ""
            if not passed:
                if callable(self.error_message):
                    error_msg = self.error_message(data)
                else:
                    error_msg = self.error_message
            
            # Handle both Dict and ValidationContext for details
            if isinstance(data, dict):
                details = data.get('error_details', {})
            else:
                # ValidationContext object
                details = data.get_details_for_rule(self.rule_id)
            
            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=details
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
    """Manages the registration and execution of validation rules."""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = defaultdict(list)
    
    def register_rule(self, rule: ValidationRule) -> None:
        """Registers a single validation rule."""
        self.rules.append(rule)
        self.rules_by_category[rule.category].append(rule)
    
    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Registers a list of validation rules."""
        for rule in rules:
            self.register_rule(rule)
    
    def validate(self, data: ValidationContext, 
                categories: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validates the data against registered rules."""
        results = []
        
        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))
        
        for rule in rules_to_run:
            result = rule.execute(data)
            results.append(result)
        
        return results
    
    def has_high_or_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Checks if any high or critical failures are present."""
        return any(
            not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
            for r in results
        )

class ConstraintFailureClassifier:
    """Classifies validation failures to inform retry strategies."""
    
    @staticmethod
    def classify_failure(
        validation_result: ValidationResult,
        original_temperature: float
    ) -> str:
        """
        Returns failure category to determine optimal retry approach:
        - "MECHANICAL": Word count, format, structure (lower temp helps)
        - "CREATIVE": Placeholders, generic content (higher temp needed)  
        - "SEMANTIC": Forbidden verbs, intro phrases (prompt changes help)
        - "CONFLICT": Impossible constraint combination (needs redesign)
        """
        rule_id = validation_result.rule_id
        
        if any(keyword in rule_id for keyword in ["WORD_COUNT", "SENTENCE_COUNT", "FORMAT", "STRUCTURE"]):
            return "MECHANICAL"
        
        if any(keyword in rule_id for keyword in ["PLACEHOLDER", "GENERIC", "MOCK", "EMPTY"]):
            return "CREATIVE"
        
        if any(keyword in rule_id for keyword in ["FORBIDDEN_VERB", "INTRO_PHRASE", "NO_", "INVALID_"]):
            return "SEMANTIC"
        
        if original_temperature <= 0.4 and not validation_result.passed:
            return "CONFLICT"
        
        return "UNKNOWN"

# ============================================================================
# PART 4: PRE-FLIGHT VALIDATOR (from validator_RES.py)
# ============================================================================

class PreFlightValidator:
    """
    V3.8 Pre-Flight Validator - The Quality Guardian
    Implements comprehensive validation rules for resume generation.
    """
    
    def __init__(self, config: Any = None):
        self.config = config or CONFIG
        self.logger = logging.getLogger(__name__)
        self.engine = ValidationEngine()
        self._register_all_rules()
        self.execution_stats = {
            'total_validations': 0,
            'total_failures': 0,
            'rules_triggered': defaultdict(int),
            'average_execution_time': 0
        }
    
    def _register_all_rules(self):
        """Register all validation rules with the engine."""
        
        # H1: Section Presence Rules
        for section in ResumeSection:
            if not section.value.endswith("_HEADER"):
                self.engine.register_rule(ValidationRule(
                    rule_id=f"H1_SECTION_PRESENCE_{section.name}",
                    severity=ValidationSeverity.CRITICAL,
                    validator=lambda ctx, s=section: _validate_section_presence(ctx, s),
                    error_message=f"Section {section.name} is missing or empty",
                    category="presence"
                ))
        
        # H2: Content Quality Rules
        critical_sections = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K11_COVER_LETTER
        ]
        
        # Add narrative sections to critical list for Intro Phrases
        narrative_sections = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K11_COVER_LETTER
        ]
        
        for section in critical_sections:
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_NO_PROMPT_CONTAMINATION_{section.name}",
                severity=ValidationSeverity.HIGH,
                validator=lambda ctx, s=section: _validate_no_prompt_contamination(ctx, s),
                error_message=lambda ctx, s=section: f"Prompt contamination in {s.name}: {ctx.get_details_for_rule(f'H2_NO_PROMPT_CONTAMINATION_{s.name}').get('matches', [])}",
                category="quality"
            ))
            
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_NO_CONVERSATIONAL_FILLERS_{section.name}",
                severity=ValidationSeverity.HIGH,
                validator=lambda ctx, s=section: _validate_no_conversational_fillers(ctx, s),
                error_message=lambda ctx, s=section: f"Conversational fillers in {s.name}",
                category="quality"
            ))
        
        # --- V5.4 FIX: REGISTER MISSING RULES ---
        for section in ResumeSection:
            # Skip headers and short fields
            if section.value.endswith("_HEADER") or section in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT]:
                continue
                
            # Register FORBIDDEN VERBS for all substantive sections
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_NO_FORBIDDEN_VERBS_{section.name}",
                severity=ValidationSeverity.MEDIUM,
                validator=lambda ctx, s=section: _validate_forbidden_verbs(ctx, s),
                error_message=lambda ctx, s=section: f"Forbidden verbs found in {s.name}: {ctx.get_details_for_rule(f'H2_NO_FORBIDDEN_VERBS_{s.name}').get('matches', [])}",
                category="quality"
            ))

        for section in narrative_sections:
            # Register INTRO PHRASES for narrative sections
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_NO_INTRO_PHRASES_{section.name}",
                severity=ValidationSeverity.HIGH,
                validator=lambda ctx, s=section: _validate_no_intro_phrases(ctx, s),
                error_message=lambda ctx, s=section: f"Banned intro phrase found in {s.name}",
                category="style"
            ))
        # ----------------------------------------
            # Register CANONICAL VERBS (Enricher Config)
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_CANONICAL_VERBS_{section.name}",
                severity=ValidationSeverity.LOW,
                validator=lambda ctx, s=section: _validate_canonical_verbs(ctx, s),
                error_message=lambda ctx, s=section: f"Weak verb usage in {s.name}",
                category="quality"
            ))
            
            # Register HYPHENATION RULES (Style Config)
            self.engine.register_rule(ValidationRule(
                rule_id=f"H2_STYLE_HYPHEN_{section.name}",
                severity=ValidationSeverity.LOW,
                validator=lambda ctx, s=section: _validate_style_hyphenation(ctx, s),
                error_message=lambda ctx, s=section: f"Style violation (hyphenation) in {s.name}",
                category="style"
            ))
        
        # H3: Structure Rules
        self.engine.register_rule(ValidationRule(
            rule_id="H3_K1_SENTENCE_COUNT",
            severity=ValidationSeverity.HIGH,
            validator=lambda ctx: ctx.k1_sentence_count_details['sentence_count'] >= ctx.k1_sentence_count_details['min'] and
                                 ctx.k1_sentence_count_details['sentence_count'] <= ctx.k1_sentence_count_details['max'],
            error_message=lambda ctx: f"Executive Summary has {ctx.k1_sentence_count_details['sentence_count']} sentences (expected {ctx.k1_sentence_count_details['min']}-{ctx.k1_sentence_count_details['max']})",
            category="structure"
        ))
        
        self.engine.register_rule(ValidationRule(
            rule_id="H3_K11_COVER_LETTER_FULL_STRUCTURE",
            severity=ValidationSeverity.CRITICAL,
            validator=_validate_cover_letter_full_structure,
            error_message=lambda ctx: f"Cover letter missing structure: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_FULL_STRUCTURE')}",
            category="structure"
        ))
        
        # H4: Bullet Word Count Rules
        self.engine.register_rule(ValidationRule(
            rule_id="H4_BULLET_WORD_COUNTS",
            severity=ValidationSeverity.HIGH,
            validator=lambda ctx: len(ctx.bullet_word_counts_details.get('violations', [])) == 0,
            error_message=lambda ctx: f"Bullet word count violations: {ctx.bullet_word_counts_details['violations']}",
            category="formatting"
        ))
        
        # H5: Global Coherence Rules
        self.engine.register_rule(ValidationRule(
            rule_id="H5_GLOBAL_TOTAL_WORD_COUNT",
            severity=ValidationSeverity.HIGH,
            validator=lambda ctx: ctx.total_words >= ctx.constraints.TOTAL_WORD_COUNT_MIN and
                                 ctx.total_words <= ctx.constraints.TOTAL_WORD_COUNT_MAX,
            error_message=lambda ctx: f"Total word count {ctx.total_words} outside range [{ctx.constraints.TOTAL_WORD_COUNT_MIN}, {ctx.constraints.TOTAL_WORD_COUNT_MAX}]",
            category="global"
        ))
        
        self.engine.register_rule(ValidationRule(
            rule_id="H5_GLOBAL_CROSS_SECTION_SIMILARITY",
            severity=ValidationSeverity.HIGH,
            validator=_validate_cross_section_similarity,
            error_message=lambda ctx: f"High similarity between sections: {ctx.cross_section_similarity_details['failures']}",
            category="global"
        ))
        
        self.engine.register_rule(ValidationRule(
            rule_id="H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY",
            severity=ValidationSeverity.HIGH,
            validator=_validate_narrative_vs_master_similarity,
            error_message=lambda ctx: f"Narrative similarity outside range: {ctx.narrative_vs_master_similarity_details['failures']}",
            category="global"
        ))
        
        # S1: JD Alignment Rules
        self.engine.register_rule(ValidationRule(
            rule_id="S1_JD_SKILLS_OVERLAP",
            severity=ValidationSeverity.CRITICAL,
            validator=_validate_jd_skills_overlap,
            error_message=lambda ctx: f"Only {ctx.jd_skills_overlap_details['overlap_count']} JD skills found (min {ctx.jd_skills_overlap_details['min_required']})",
            category="signal"
        ))
        
        # S2: Signal Score Rules
        for section in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER]:
            self.engine.register_rule(ValidationRule(
                rule_id=f"S2_SIGNAL_SCORE_{section.name}",
                severity=ValidationSeverity.HIGH,
                validator=lambda ctx, s=section: _validate_signal_score(ctx, s),
                error_message=lambda ctx, s=section: f"Signal score for {s.name} below threshold",
                category="signal"
            ))
    
    def validate(self, staging_buffer: ImmutableStagingBuffer, 
                thematic_analysis: ThematicAnalysis,
                job_description: str,
                master_resume: Dict,
                categories: Optional[List[str]] = None) -> Tuple[bool, List[ValidationResult], float]:
        """
        Main validation entry point.
        Returns: (passed, results, signal_quality_score)
        """
        start_time = time.time()
        
        # Create validation context
        context = ValidationContext(
            staging_buffer=staging_buffer,
            thematic_analysis=thematic_analysis,
            job_description=job_description,
            master_resume=master_resume,
            app_config=self.config
        )
        
        # Run validation
        results = self.engine.validate(context, categories)
        
        # Update stats
        self.execution_stats['total_validations'] += 1
        failures = [r for r in results if not r.passed]
        self.execution_stats['total_failures'] += len(failures)
        
        for result in results:
            self.execution_stats['rules_triggered'][result.rule_id] += 1
        
        # Calculate signal quality score
        signal_score = self._calculate_overall_signal_score(context)
        
        # Check for critical failures
        has_critical = self.engine.has_high_or_critical_failures(results)
        passed = not has_critical and signal_score >= self.config.min_confidence_score
        
        execution_time = time.time() - start_time
        self.execution_stats['average_execution_time'] = (
            (self.execution_stats['average_execution_time'] * (self.execution_stats['total_validations'] - 1) + 
             execution_time) / self.execution_stats['total_validations']
        )
        
        return passed, results, signal_score
    
    def _calculate_overall_signal_score(self, context: ValidationContext) -> float:
        """Calculate overall signal quality score."""
        scores = []
        
        # Get signal scores from critical sections
        for section in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER]:
            text = context.get(section.value, '')
            if text:
                score = calculate_signal_score(text, context.job_description, context.thematic_analysis)
                scores.append(score)
        
        # Add JD skills overlap score
        jd_details = context.jd_skills_overlap_details
        if jd_details.get('jd_skills'):
            overlap_ratio = jd_details['overlap_count'] / len(jd_details['jd_skills'])
            scores.append(overlap_ratio)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def validate_with_retry(self, staging_buffer: ImmutableStagingBuffer,
                           thematic_analysis: ThematicAnalysis,
                           job_description: str,
                           master_resume: Dict,
                           max_retries: int = 3,
                           temperature_adjustments: bool = True) -> Tuple[bool, List[ValidationResult], List[GenerationAttempt]]:
        """
        Validate with intelligent retry logic based on failure classification.
        """
        attempts = []
        current_temp = DEFAULT_GENERATION_TEMPERATURE
        
        for attempt_num in range(max_retries):
            # Run validation
            passed, results, signal_score = self.validate(
                staging_buffer, thematic_analysis, job_description, master_resume
            )
            
            # Record attempt
            attempt = GenerationAttempt(
                temperature=current_temp,
                attempt_number=attempt_num + 1,
                content="",  # Would be populated by the generator
                passed=passed,
                validation_results=results,
                execution_time=self.execution_stats['average_execution_time'],
                metadata={'signal_score': signal_score}
            )
            attempts.append(attempt)
            
            if passed:
                return True, results, attempts
            
            # Classify failures and adjust temperature
            if temperature_adjustments and attempt_num < max_retries - 1:
                failure_types = defaultdict(int)
                for result in results:
                    if not result.passed:
                        failure_type = ConstraintFailureClassifier.classify_failure(result, current_temp)
                        failure_types[failure_type] += 1
                
                # Adjust temperature based on dominant failure type
                dominant_type = max(failure_types, key=failure_types.get)
                
                if dominant_type == "MECHANICAL":
                    current_temp = max(0.3, current_temp - 0.2)
                elif dominant_type == "CREATIVE":
                    current_temp = min(0.9, current_temp + 0.2)
                elif dominant_type == "SEMANTIC":
                    # No temperature change, needs prompt adjustment
                    pass
                
                self.logger.info(f"Retry {attempt_num + 1}: Dominant failure type '{dominant_type}', adjusting temp to {current_temp}")
        
        return False, results, attempts
    
    def generate_validation_report(self, results: List[ValidationResult], 
                                  signal_score: float) -> str:
        """Generate a detailed validation report."""
        report_lines = ["# Validation Report\n"]
        report_lines.append(f"Signal Score: {signal_score:.2%}\n")
        report_lines.append(f"Total Rules Checked: {len(results)}\n")
        
        # Group by severity
        by_severity = defaultdict(list)
        for result in results:
            by_severity[result.severity].append(result)
        
        # Report failures by severity
        for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH, 
                        ValidationSeverity.MEDIUM, ValidationSeverity.LOW]:
            failures = [r for r in by_severity[severity] if not r.passed]
            if failures:
                report_lines.append(f"\n## {severity.name} Issues ({len(failures)})\n")
                for result in failures:
                    report_lines.append(f"- [{result.rule_id}] {result.message}")
                    if result.details:
                        report_lines.append(f"  Details: {result.details}")
        
        # Summary stats
        report_lines.append("\n## Summary Statistics\n")
        report_lines.append(f"- Total Validations Run: {self.execution_stats['total_validations']}")
        report_lines.append(f"- Total Failures: {self.execution_stats['total_failures']}")
        report_lines.append(f"- Average Execution Time: {self.execution_stats['average_execution_time']:.3f}s")
        
        # Most triggered rules
        report_lines.append("\n## Most Triggered Rules\n")
        top_rules = sorted(self.execution_stats['rules_triggered'].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        for rule_id, count in top_rules:
            report_lines.append(f"- {rule_id}: {count} times")
        
        return "\n".join(report_lines)

# Export key classes and functions
__all__ = [
    'ValidationContext', 'ValidationRule', 'ValidationEngine',
    'ConstraintFailureClassifier', 'PreFlightValidator',
    'calculate_signal_score'
]
