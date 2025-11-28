# File: validator_RES.py
# Core Validator Orchestrator Module - V18 Architecture (Wizard Patched)
# Version: 18.01 (Refactored & Patched)
# This file contains only the PreFlightValidator, which orchestrates
# the engine, context, and rules from its sub-modules.

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from collections import defaultdict
from functools import partial

# Import dependencies from new modules
from config_RES import CONFIG, COVER_LETTER_SIGNATURE_TEMPLATE
from models_RES import (
    ValidationResult, ValidationSeverity, ThematicAnalysis, ResumeSection,
    ImmutableStagingBuffer, GateDecision, BulletProvenance,
    FactualFailureException
)
from utils_RES import text_utils, calculate_signal_score

# --- V18 REFACTOR: Import from validation modules ---
from validation_engine import ValidationEngine, ValidationRule, ConstraintFailureClassifier
from validation_context import ValidationContext
import validation_rules as ValidationRules

# ==============================================================================
# PRE-FLIGHT VALIDATOR
# ==============================================================================

class PreFlightValidator:
    """
    The main validation orchestrator for HOP-5.
    Initializes all rules and runs them using ValidationContext.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, master_resume: Dict, app_config: Any):
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.config = app_config
        self.constraints = app_config.constraints
        self.signal_constraints = app_config.signal_constraints
        self.validator_config = app_config.validator
        
        self.FORBIDDEN_VERBS = self.validator_config.forbidden_verbs
        self.PIPELINE_STATUS_ENUM = self.validator_config.pipeline_status_enum
        
        self.REQUIRED_SECTIONS = self._convert_section_names_to_enums(
            self.validator_config.required_sections
        )
        self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK = self._convert_section_names_to_enums(
            self.validator_config.bullet_word_count_sections_to_check
        )
        self.PROVENANCE_SPLIT_TARGETS = self._convert_config_keys_to_enums(
            self.validator_config.provenance_split_targets
        )
        
        # This config was part of the class in the original file, so it's kept here.
        self.SECTION_SIGNAL_TARGETS_CONFIG = {
            "K1_Exec_Summary": (ResumeSection.K1_EXECUTIVE_SUMMARY, 0.85, 1.20, None, None),
            "K2_Unify": (ResumeSection.K2_UNIFY_OVERVIEW, 0.70, 1.00, None, None),
            "K3_IBM": (ResumeSection.K3_IBM_OVERVIEW, 0.70, 1.00, None, None),
            "K4_TraderSense": (ResumeSection.K4_TRADERSENSE_NARRATIVE, 0.60, 0.90, None, None),
            "K6_Narrative": (ResumeSection.K6_EARLY_CAREER_NARRATIVE, 0.70, 1.00, None, None),
        }

        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()
        self._register_rules()
        self.signal_constraints = app_config.signal_constraints
        self.logger = logging.getLogger(__name__)

    
    def _convert_section_names_to_enums(self, section_names: Set[str]) -> Set:
        """Converts a set of section name strings to ResumeSection enums."""
        result = set()
        for name in section_names:
            if isinstance(name, str):
                try:
                    enum_val = ResumeSection[name]
                    result.add(enum_val)
                except KeyError:
                    logging.warning(f"Unknown ResumeSection '{name}' in validator config, skipping")
            else:
                result.add(name) # Already an enum
        return result
    
    def _convert_config_keys_to_enums(self, config_dict: Dict) -> Dict:
        """Converts string keys in config dicts to ResumeSection enums."""
        result = {}
        for key, value in config_dict.items():
            if isinstance(key, str):
                try:
                    enum_key = ResumeSection[key]
                    result[enum_key] = value
                except KeyError:
                    logging.warning(f"Unknown ResumeSection key '{key}' in validator config, skipping")
            else:
                result[key] = value # Already an enum
        return result
    
    # --- Rule Definition Helpers ---

    @staticmethod
    def _mk_range(rule_id, sev, cat, getter, label, min_k, max_k, val_k):
        """Factory for creating a range-check rule config."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": lambda ctx: getter(ctx).get(min_k) <= getter(ctx).get(val_k) <= getter(ctx).get(max_k),
            "error_message": lambda ctx: f"{label}: {getter(ctx).get(val_k)} (target: {getter(ctx).get(min_k)}-{getter(ctx).get(max_k)})"
        }

    @staticmethod
    def _mk_method(rule_id, sev, cat, method_name, msg):
        """Factory for creating a method-based rule config."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": method_name,
            "error_message": msg
        }

    # --- RULES_CONFIG: The master list of all validation rules ---
    @property
    def RULES_CONFIG(self):
        return [
            {
                "rule_id": "H0_RAG_MIN_QUALITY", "severity": ValidationSeverity.CRITICAL, "category": "signal",
                "validator": lambda ctx: getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0) >= 0.50,
                "error_message": lambda ctx: f"Initial RAG Analysis Quality ({getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0):.1%}) is below the minimum threshold (50%)."
            },
            {
                "rule_id": "H5_GLOBAL_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
                "validator": lambda ctx: ctx.constraints.TOTAL_WORD_COUNT_MIN <= ctx.total_words <= ctx.constraints.TOTAL_WORD_COUNT_MAX,
                "error_message": lambda ctx: f"Total resume: {ctx.total_words} words (target: {ctx.constraints.TOTAL_WORD_COUNT_MIN}-{ctx.constraints.TOTAL_WORD_COUNT_MAX})"
            },
            self._mk_range("H3_K1_SENTENCE_COUNT", ValidationSeverity.CRITICAL, "structure", lambda ctx: ctx.k1_sentence_count_details, "K.1 Exec Summary sentences", 'min', 'max', 'sentence_count'),
            # FIX 3: Use correct Rule ID
            self._mk_range("H3_K1_WORD_COUNT", ValidationSeverity.MEDIUM, "word_count", lambda ctx: ctx.k1_word_count_details, "K.1 Exec Summary words", 'min', 'max', 'word_count'),
            {
                "rule_id": "H3_K0_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.MEDIUM,"category": "structure",
                "validator": lambda ctx: ctx.constraints.HEADLINE_WORD_COUNT_MIN <= ctx.headline_details['word_count'] <= ctx.constraints.HEADLINE_WORD_COUNT_MAX,
                "error_message": lambda ctx: f"K.0 Headline: {ctx.headline_details['word_count']} words (target: {ctx.headline_details['min']}-{ctx.headline_details['max']}). Headline: '{ctx.headline_details['headline']}'"
            },
            self._mk_range("H3_K2_OVERVIEW_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview words", 'min_wc', 'max_wc', 'word_count'),
            self._mk_range("H3_K2_OVERVIEW_SENTENCE_COUNT", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
            self._mk_range("H3_K3_OVERVIEW_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview words", 'min_wc', 'max_wc', 'word_count'),
            self._mk_range("H3_K3_OVERVIEW_SENTENCE_COUNT", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
            self._mk_range("H3_K4_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k4_narrative_details, "K.4 TraderSense Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K4_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k4_narrative_details['target_sc'] - 1 <= ctx.k4_narrative_details['sentence_count'] <= ctx.k4_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.4 TraderSense Narrative: {ctx.k4_narrative_details['sentence_count']} sentences (target range: {ctx.k4_narrative_details['target_sc']-1}-{ctx.k4_narrative_details['target_sc']+1})"
            },
            self._mk_range("H3_K5_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k5_narrative_details, "K.5 EY Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K5_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k5_narrative_details['target_sc'] - 1 <= ctx.k5_narrative_details['sentence_count'] <= ctx.k5_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.5 EY Narrative: {ctx.k5_narrative_details['sentence_count']} sentences (target range: {ctx.k5_narrative_details['target_sc']-1}-{ctx.k5_narrative_details['target_sc']+1})"
            },
            self._mk_range("H3_K6_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k6_narrative_details, "K.6 Early Career Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K6_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k6_narrative_details['target_sc'] - 1 <= ctx.k6_narrative_details['sentence_count'] <= ctx.k6_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.6 Early Career Narrative: {ctx.k6_narrative_details['sentence_count']} sentences (target range: {ctx.k6_narrative_details['target_sc']-1}-{ctx.k6_narrative_details['target_sc']+1})"
            },
            
            # --- ADDED SKILLS WORD COUNT RULE ---
            self._mk_method("H3_K10_SKILLS_WORD_COUNT", ValidationSeverity.CRITICAL, "word_count",
                            "_validate_skills_word_count",
                            lambda ctx: f"K.10 Skills word count outside range ({ctx.get_details_for_rule('H3_K10_SKILLS_WORD_COUNT').get('min', '?')}-{ctx.get_details_for_rule('H3_K10_SKILLS_WORD_COUNT').get('max', '?')}): {ctx.get_details_for_rule('H3_K10_SKILLS_WORD_COUNT').get('violations', 'N/A')}"),
            
            # --- NEW TIERED BULLET WORD COUNT RULES ---
            self._mk_method("H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL", ValidationSeverity.CRITICAL, "word_count",
                            "_validate_bullet_word_count_CRITICAL",
                            lambda ctx: f"Bullet word counts are CRITICAL (<15 or >50): {ctx.get_details_for_rule('H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL').get('violations', 'N/A')}"),
            # --- END TIERED RULES ---
            
            {
                "rule_id": "H5_BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
                "validator": lambda ctx: ctx.staging_buffer.is_locked(),
                "error_message": "Staging buffer must be locked before validation"
            },
            {
                "rule_id": "H3_K11_COVER_LETTER_SIGNATURE_VALID", "severity": ValidationSeverity.CRITICAL, "category": "structure",
                "validator": lambda ctx: bool(ctx.expected_signature and '\n' in ctx.expected_signature and ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').rstrip().endswith(ctx.expected_signature)),
                "error_message": "K.11 Cover letter signature is missing, malformed, or not multi-line."
            },
            self._mk_method("H3_K11_COVER_LETTER_FULL_STRUCTURE", ValidationSeverity.CRITICAL, "structure", "_validate_cover_letter_full_structure", "K.11 Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."),
            self._mk_method("H3_K0_HEADLINE_NO_TITLES", ValidationSeverity.CRITICAL, "structure", "_validate_headline_format_no_titles", lambda ctx: f"K.0 Headline contains forbidden titles: {ctx.get_details_for_rule('H3_K0_HEADLINE_NO_TITLES').get('forbidden', 'N/A')}. Headline: '{ctx.headline_details.get('headline', '')}'"),
            {"rule_id": "H3_K0_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: ',' not in ctx.headline_details.get('headline', ''), "error_message": lambda ctx: f"K.0 Headline contains commas. Headline: '{ctx.headline_details.get('headline', '')}'"},
            self._mk_method("H3_K0_HEADLINE_COMPONENT_WC", ValidationSeverity.HIGH, "structure", "_validate_headline_format_component_wc", lambda ctx: f"K.0 Headline component word count outside range ({ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('min', '?')}-{ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('max', '?')}). Violations: {ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('wc_violations_str', 'N/A')}. Headline: '{ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('headline', '')}'"),
            {"rule_id": "H7_VISUAL_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Resume headers not consistently H2"},
            {"rule_id": "H7_VISUAL_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Education/Certification format incorrect"},
            {"rule_id": "H7_VISUAL_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience bullets incorrect style"},
            {"rule_id": "H7_VISUAL_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Competencies list formatting incorrect"},
            {"rule_id": "H7_VISUAL_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience section formatting incorrect"},
            self._mk_method("H5_CONTENT_NO_PLACEHOLDERS", ValidationSeverity.CRITICAL, "content", "_validate_no_placeholders", lambda ctx: f"Found placeholder text in content: {ctx.get_details_for_rule('H5_CONTENT_NO_PLACEHOLDERS').get('placeholders', 'N/A')}"),
            self._mk_method("H3_CONTENT_NO_FORBIDDEN_VERBS", ValidationSeverity.CRITICAL, "content", "_validate_forbidden_verbs", lambda ctx: f"Forbidden verbs found in generated content: {ctx.get_details_for_rule('H3_CONTENT_NO_FORBIDDEN_VERBS').get('violations', 'N/A')}"),
            self._mk_method("H3_CONTENT_NO_INTRO_PHRASES", ValidationSeverity.CRITICAL, "content", "_validate_no_intro_phrases", lambda ctx: f"Banned introductory phrases found: {ctx.get_details_for_rule('H3_CONTENT_NO_INTRO_PHRASES').get('violations', 'N/A')}"),
            self._mk_method("H3_GLOBAL_PER_SECTION_SIGNAL_SCORE", ValidationSeverity.HIGH, "content", "_validate_per_section_signal_raw", lambda ctx: f"One or more sections outside target raw signal score range: {ctx.get_details_for_rule('H3_GLOBAL_PER_SECTION_SIGNAL_SCORE').get('failures', 'N/A')}"),
            # FIX 3: Use correct Rule ID
            {
                "rule_id": "H3_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
                "validator": lambda ctx: ctx.constraints.K1_MIN_DIFFERENTIATORS <= ctx._calculate_k1_differentiator_range_details()['found'] <= ctx.signal_constraints.K1_MAX_DIFFERENTIATORS,
                "error_message": lambda ctx: f"K.1 Summary contains {ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('found', '?')} differentiators (target: {ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('min', '?')}-{ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('max', '?')})."
            },
            self._mk_method("H5_GLOBAL_JD_KEYWORD_RANGE", ValidationSeverity.HIGH, "content", "_validate_jd_keyword_range", lambda ctx: f"Resume contains {ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('found', '?')} unique JD keywords (target: {ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('min', '?')}-{ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('max', '?')})."),
            self._mk_method("H0_NARRATIVE_MINING_PRESENCE", ValidationSeverity.HIGH, "content", "_validate_narrative_mining_presence", "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."),
            {
                "rule_id": "H3_K11_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
                "validator": lambda ctx: ctx.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD <= ctx.cover_letter_jd_similarity <= ctx.signal_constraints.CL_MAX_JD_SIMILARITY,
                "error_message": lambda ctx: f"K.11 Cover letter relevance to JD is {ctx.cover_letter_jd_similarity:.2f} (target: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_RELEVANCE_RANGE').get('min_sim', 0.0):.2f}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_RELEVANCE_RANGE').get('max_sim', 0.0):.2f})."
            },
            self._mk_method("H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY", ValidationSeverity.HIGH, "content", lambda ctx: ctx._calculate_cover_letter_narrative_details()['valid'], lambda ctx: f"K.11 Cover letter may be missing narrative integrity. Hook: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('hook', '?')}, Proof: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('proof', '?')}, Vision: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('vision', '?')}"),
            {
                "rule_id": "H3_K11_COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
                "validator": lambda ctx: "track record of measurable AI transformation" not in ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, ''),
                "error_message": "Creative cover letter generation failed; fallback likely used."
            },
            self._mk_method("H3_K11_COVER_LETTER_STRUCTURE", ValidationSeverity.MEDIUM, "content", "_validate_cover_letter_structure", lambda ctx: f"K.11 Cover letter paragraph word counts out of spec. P1: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_max','?')}), P2: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_max','?')}), P3: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_max','?')})"),
            self._mk_method("H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK", ValidationSeverity.CRITICAL, "content", "_validate_provenance_split", lambda ctx: f"Provenance split mismatch: {ctx.get_details_for_rule('H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK').get('violations', 'N/A')}"),
            self._mk_method("H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK", ValidationSeverity.HIGH, "content", "_validate_authenticity_signal", lambda ctx: f"Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {ctx.get_details_for_rule('H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK').get('details', 'N/A')}"),
            self._mk_method("H5_GLOBAL_CROSS_SECTION_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_cross_section_similarity", lambda ctx: f"High similarity (>=0.65) found between sections: {'; '.join(ctx.get_details_for_rule('H5_GLOBAL_CROSS_SECTION_SIMILARITY').get('failures', []))}"),
            self._mk_method("H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_narrative_vs_master_similarity", lambda ctx: f"Narrative similarity to master highlights outside range (0.40-0.70): {'; '.join(ctx.get_details_for_rule('H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY').get('failures', []))}"),
        ]

    # --- Regex Patterns for Validation ---
    PROMPT_CONTAMINATION_PATTERN = re.compile(r"\b(MUST|CRITICAL|ABSOLUTELY|Do NOT|Output ONLY|Return ONLY|JSON structure|Word count:|Sentence count:|Target range:|strictly between)\b", re.IGNORECASE)
    CONVERSATIONAL_FILLERS_PATTERN = re.compile(r"^(Here is the|Certainly,|I have generated|Below is the|Apologies,|Please note)\b", re.IGNORECASE | re.MULTILINE)
    EMPTY_LIST_ITEM_PATTERN = re.compile(r"^\s*[\*\-]\s*($|\n)", re.MULTILINE)
    BANNED_INTRO_PHRASES_PATTERN = re.compile(r"^(In my role as|As a|At \[Company\]|My responsibilities included|Responsible for)\b", re.IGNORECASE)

    def _initialize_rule_map(self) -> Dict[str, Union[ResumeSection, str]]:
        """Maps rule IDs to the resume section they primarily validate."""
        logger = logging.getLogger(__name__)
        rule_map = {
            "H5_GLOBAL_TOTAL_WORD_COUNT": "GLOBAL",
            "H5_GLOBAL_JD_KEYWORD_RANGE": "GLOBAL",
            "H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK": "GLOBAL", "H0_NARRATIVE_MINING_PRESENCE": "GLOBAL",
            "H5_CONTENT_NO_PLACEHOLDERS": "GLOBAL", "H5_BUFFER_LOCK_STATUS": "GLOBAL",
            "H0_RAG_MIN_QUALITY": "GLOBAL",
            "H5_GLOBAL_CROSS_SECTION_SIMILARITY": "GLOBAL",
            "H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY": "GLOBAL",
            "H7_VISUAL_RESUME_HEADER_H2": "VISUAL", "H7_VISUAL_EDU_CERTS_FORMAT": "VISUAL",
            "H5_CONTENT_NO_PROMPT_CONTAMINATION": "GLOBAL",
            "H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS": "GLOBAL",
            "H5_STRUCTURE_NO_EMPTY_LIST_ITEMS": "GLOBAL",
            "H5_STRUCTURE_MARKDOWN_HEADER_SPACING": "GLOBAL",
            "H7_VISUAL_EXPERIENCE_BULLET_STYLE": "VISUAL", "H7_VISUAL_COMPETENCIES_FORMATTING": "VISUAL",
            "H7_VISUAL_EXPERIENCE_RENDER_FORMAT": "VISUAL",
            "H3_K0_HEADLINE_WORD_COUNT": ResumeSection.K0_HEADLINE, "H3_K0_HEADLINE_NO_TITLES": ResumeSection.K0_HEADLINE,
            "H3_K0_HEADLINE_NO_COMMAS": ResumeSection.K0_HEADLINE, "H3_K0_HEADLINE_COMPONENT_WC": ResumeSection.K0_HEADLINE,
            "STRUCTURE_K0_HEADLINE_PRESENT": ResumeSection.K0_HEADLINE,
            "H3_K1_SENTENCE_COUNT": ResumeSection.K1_EXECUTIVE_SUMMARY, "H3_K1Word_COUNT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "H3_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K2_UNIFY_BULLETS_PRESENT": ResumeSection.K2_UNIFY_BULLETS, "STRUCTURE_K2_UNIFY_OVERVIEW_PRESENT": ResumeSection.K2_UNIFY_OVERVIEW,
            "H3_K2_OVERVIEW_WORD_COUNT": ResumeSection.K2_UNIFY_OVERVIEW, "H3_K2_OVERVIEW_SENTENCE_COUNT": ResumeSection.K2_UNIFY_OVERVIEW,
            "STRUCTURE_K3_IBM_BULLETS_PRESENT": ResumeSection.K3_IBM_BULLETS, "STRUCTURE_K3_IBM_OVERVIEW_PRESENT": ResumeSection.K3_IBM_OVERVIEW,
            "H3_K3_OVERVIEW_WORD_COUNT": ResumeSection.K3_IBM_OVERVIEW, "H3_K3_OVERVIEW_SENTENCE_COUNT": ResumeSection.K3_IBM_OVERVIEW,
            "STRUCTURE_K4_TRADERSENSE_NARRATIVE_PRESENT": ResumeSection.K4_TRADERSENSE_NARRATIVE, "H3_K4_NARRATIVE_WORD_COUNT": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "H3_K4_NARRATIVE_SENTENCE_COUNT": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "STRUCTURE_K5_EY_NARRATIVE_PRESENT": ResumeSection.K5_EY_NARRATIVE, "H3_K5_NARRATIVE_WORD_COUNT": ResumeSection.K5_EY_NARRATIVE,
            "H3_K5_NARRATIVE_SENTENCE_COUNT": ResumeSection.K5_EY_NARRATIVE,
            "STRUCTURE_K6_EARLY_CAREER_NARRATIVE_PRESENT": ResumeSection.K6_EARLY_CAREER_NARRATIVE, "H3_K6_NARRATIVE_WORD_COUNT": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "H3_K6_NARRATIVE_SENTENCE_COUNT": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "STRUCTURE_K9_COMPETENCIES_PRESENT": ResumeSection.K9_COMPETENCIES,
            "STRUCTURE_K10_SKILLS_PRESENT": ResumeSection.K10_SKILLS,
            "H3_K10_SKILLS_WORD_COUNT": ResumeSection.K10_SKILLS, # <-- ADDED RULE
            "H3_K11_COVER_LETTER_SIGNATURE_VALID": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "H3_K11_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K11_COVER_LETTER,
            "H3_K11_COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "STRUCTURE_K11_COVER_LETTER_PRESENT": ResumeSection.K11_COVER_LETTER,
            
            # --- NEW TIERED BULLET WORD COUNT RULES ---
            "H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL": "COMPLEX_PER_SECTION",

            # --- END TIERED RULES ---

            "H3_GLOBAL_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION", 
            "H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION", 
            "H3_CONTENT_NO_FORBIDDEN_VERBS": "COMPLEX_PER_SECTION",
            "H3_CONTENT_NO_INTRO_PHRASES": "COMPLEX_PER_SECTION"
        }

        # Dynamically add rules for required sections not explicitly in RULES_CONFIG
        config_rule_ids = {cfg["rule_id"] for cfg in self.RULES_CONFIG}
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if rule_id not in config_rule_ids and rule_id not in rule_map:
                rule_map[rule_id] = section_enum
                logger.debug(f"Dynamically mapped structure rule: {rule_id} -> {section_enum.name}")

        header_enums = [ 
            ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, ResumeSection.K0_EXPERIENCE_HEADER, 
            ResumeSection.K0_EDUCATION_HEADER, ResumeSection.K0_CERTIFICATIONS_HEADER, 
            ResumeSection.K0_COMPETENCIES_HEADER 
        ]
        for header_enum in header_enums:
             rule_id = f"STRUCTURE_{header_enum.name}_PRESENT"
             if rule_id not in rule_map:
                  rule_map[rule_id] = header_enum
                  logger.debug(f"Dynamically mapped header structure rule: {rule_id} -> {header_enum.name}")

        return rule_map

    def _register_rules(self):
        """Registers all rules from the RULES_CONFIG into the ValidationEngine."""
        logger = logging.getLogger(__name__)
        all_rules_config = list(self.RULES_CONFIG)

        # Dynamically add rules for required sections
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if not any(cfg["rule_id"] == rule_id for cfg in all_rules_config):
                all_rules_config.append({
                    "rule_id": rule_id,
                    "severity": ValidationSeverity.CRITICAL,
                    "category": "structure",
                    "validator": partial(ValidationRules._validate_section_presence, section_enum=section_enum),
                    "error_message": f"{section_enum.value} is missing, empty, or a placeholder."
                })

        # Add other dynamic/method-based rules
        all_rules_config.append(self._mk_method("H5_CONTENT_NO_PROMPT_CONTAMINATION", ValidationSeverity.HIGH, "content", "_validate_no_prompt_contamination", lambda ctx: f"Found prompt contamination keywords in content: {ctx.get_details_for_rule('H5_CONTENT_NO_PROMPT_CONTAMINATION').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS", ValidationSeverity.HIGH, "content", "_validate_no_conversational_fillers", lambda ctx: f"Found conversational filler phrases in content: {ctx.get_details_for_rule('H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H5_STRUCTURE_NO_EMPTY_LIST_ITEMS", ValidationSeverity.MEDIUM, "structure", "_validate_no_empty_list_items", lambda ctx: f"Found empty list items in sections: {ctx.get_details_for_rule('H5_STRUCTURE_NO_EMPTY_LIST_ITEMS').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H5_STRUCTURE_MARKDOWN_HEADER_SPACING", ValidationSeverity.MEDIUM, "structure", "_validate_markdown_header_spacing", lambda ctx: f"Found markdown headers with missing spaces: {ctx.get_details_for_rule('H5_STRUCTURE_MARKDOWN_HEADER_SPACING').get('violations', 'N/AR')}"))

        registered_rule_ids = set()
        rules_to_register = []
        
        for config in all_rules_config:
            rule_id = config["rule_id"]
            if rule_id in registered_rule_ids:
                 logger.warning(f"Duplicate rule ID found during registration: {rule_id}. Skipping re-registration.")
                 continue

            validator_ref = config["validator"]
            validator_func = None
            if isinstance(validator_ref, str):
                # --- V18 REFACTOR: Check ValidationRules module first ---
                validator_func = getattr(ValidationRules, validator_ref, None)
                if validator_func is None:
                    # Fallback to self for methods like _run_scoring_competition
                    validator_func = getattr(self, validator_ref, None)
                
                if validator_func is None:
                    msg = f"Validator method '{validator_ref}' not found for rule {rule_id}"
                    logger.error(msg)
                    # Create a dummy validator that will fail
                    validator_func = lambda ctx, rid=rule_id, m=msg: (logger.error(f"Executing dummy validator for missing method in rule {rid}: {m}"), False)[1]
            elif callable(validator_ref):
                 validator_func = validator_ref
            else:
                 logger.error(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}. Config: {config}")
                 raise TypeError(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}")

            # --- START FIX (Bug 3): This lambda now ONLY reads from the cache ---
            def create_error_message_lambda(template_func, rule_id_for_cache):
                def error_lambda(ctx: ValidationContext):
                    try:
                        if callable(template_func):
                            return str(template_func(ctx))
                        else:
                            details = ctx.get_details_for_rule(rule_id_for_cache)
                            return str(template_func).format_map(defaultdict(lambda: '[N/A]', **details))

                    except Exception as e:
                        logger.error(f"Error formatting error message for rule {rule_id_for_cache}: {e}. Template type: '{type(template_func)}'.", exc_info=False)
                        if "recursion depth" in str(e):
                            return f"[RECURSION ERROR formatting msg for {rule_id_for_cache}]"
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
            rules_to_register.append(rule)
            registered_rule_ids.add(rule_id)

        self.engine.register_rules(rules_to_register)
        logger.info(f"Registered {len(rules_to_register)} validation rules.")

    def validate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        sections_under_test: Optional[Set[ResumeSection]] = None
    ) -> Tuple[List[ValidationResult], GateDecision, Set[ResumeSection]]:
        """
        V2 Validator Interface. Runs validation engine and returns a GateDecision.
        
        Args:
            staging_buffer: Locked buffer with content to validate
            thematic_analysis: Thematic analysis from HOP-0
            job_description: Original job description
            sections_under_test: Optional set of sections to validate (for per-node validation)
                                If None, validates all sections
        
        Returns:
            Tuple of:
            - List[ValidationResult]: All validation results
            - GateDecision: PROCEED or HALT
            - Set[ResumeSection]: Sections that failed HIGH or CRITICAL rules
        """
        logger = logging.getLogger(__name__)
        
        # Build validation context
        context = ValidationContext(
            staging_buffer=staging_buffer,
            thematic_analysis=thematic_analysis,
            job_description=job_description,
            master_resume=self.master_resume,
            app_config=self.config
        )
        
        # Determine which rules to run
        rules_to_run = self.engine.rules
        
        if sections_under_test:
            logger.info(
                f"Validator: Validating specific sections: "
                f"{[s.name for s in sections_under_test]}"
            )
            
            # Filter rules to only those relevant to sections_under_test
            relevant_rule_ids = set()
            for section_enum in sections_under_test:
                if section_enum in self.RULE_TO_SECTION_MAP:
                    relevant_rule_ids.update(self.RULE_TO_SECTION_MAP[section_enum])
            
            # Also include global rules (rules not tied to specific sections)
            global_rule_ids = {
                "H5_BUFFER_LOCK_STATUS",
                "H5_CONTENT_NO_PLACEHOLDERS",
                "H5_CONTENT_NO_PROMPT_CONTAMINATION",
                "H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS",
                "H5_STRUCTURE_NO_EMPTY_LIST_ITEMS",
                "H5_STRUCTURE_MARKDOWN_HEADER_SPACING",
                "H3_GLOBAL_FORBIDDEN_VERBS"
            }
            relevant_rule_ids.update(global_rule_ids)
            
            # Filter rules
            rules_to_run = [
                r for r in self.engine.rules 
                if r.rule_id in relevant_rule_ids
            ]
            
            logger.debug(f"Running {len(rules_to_run)} rules for selected sections")
        else:
            logger.info("Validator: Validating ALL sections")
        
        # Run validation engine
        if rules_to_run is not self.engine.rules:
            # We are in a per-node test, run only the filtered rules
            self.logger.debug(f"Executing {len(rules_to_run)} filtered rules for this node.")
            all_results = [rule.execute(context) for rule in rules_to_run]
        else:
            # We are in a full run, run all rules
            self.logger.debug(f"Executing all {len(self.engine.rules)} rules.")
            all_results = self.engine.validate(context, categories=None)
        
        final_results_for_run = all_results

        
        # Check for high/critical failures
        has_critical_or_high_failures = self.engine.has_high_or_critical_failures(
            final_results_for_run
        )
        
        # Map to GateDecision
        decision = GateDecision.PROCEED if not has_critical_or_high_failures else GateDecision.HALT
        
        # Populate failed_sections_enums
        failed_sections_enums = set()
        
        if decision == GateDecision.HALT:
            logger.warning("Validation HALT: High or Critical failures detected")
            
            # Extract failed sections from validation results
            for vr in final_results_for_run:
                if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                    # Extract section from rule_id
                    # Rule IDs like "H3_K1_SENTENCE_COUNT" → K1_EXECUTIVE_SUMMARY
                    rule_id = vr.rule_id
                    
                    # Check if this rule is mapped to a section
                    # RULE_TO_SECTION_MAP is Dict[str, Union[ResumeSection, str]]
                    # where key is rule_id and value is either a ResumeSection enum or a string like "GLOBAL"
                    section_value = self.RULE_TO_SECTION_MAP.get(rule_id)
                    
                    if isinstance(section_value, ResumeSection):
                        failed_sections_enums.add(section_value)
        
        logger.info(
            f"Validation complete. Decision: {decision.name}. "
            f"Failed sections: {[s.name for s in failed_sections_enums]}"
        )
        
        return final_results_for_run, decision, failed_sections_enums