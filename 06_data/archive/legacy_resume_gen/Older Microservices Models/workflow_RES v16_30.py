# File: workflow_RES.py
# Resume Generation Workflow - Complete Orchestration Module  
# Version: 16.30 (Resumable Architecture)

from __future__ import annotations

import copy
import functools
import hashlib
import json
import logging
import os
import random
import re
import time
import uuid
from enum import Enum
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import asdict, is_dataclass

# Import from modular components
from models_RES import (
    BulletProvenance, CircuitState, GateDecision, HopCheckpoint, HopStatus,
    ImmutableStagingBuffer, JDEnforcementResult, JDEnforcementRule,
    RAGState, RAGTelemetry, ResumeSection, ThematicAnalysis,
    ValidationResult, ValidationSeverity, HopExecutionError, StagingBufferError,
    CompetitiveIntelligence, RAGMission
)
from config_RES import (
    CONFIG, AppConfig, ArtistConfig, EnricherConfig, ContentConstraintsConfig,
    ReasoningConfig, reasoning_config_to_api_params, enhance_system_prompt_with_reasoning
)
from utils_RES import (
    TextUtils, calculate_signal_score, setup_workflow_logging,
    create_directory_if_missing, sanitize_filename,
    _load_json_data, WorkflowLogFilter, DuplicateDetector
)
from validation_RES import (
    PreFlightValidator, JDEnforcementValidator, QAReportGenerator, GateDecisionEngine,
    ConstraintFailureClassifier, AppTrackerQAValidator
)
from rag_RES import EnhancedJobDescriptionAnalyzer, WebSearchRAG
from state_manager_RES import StateSerializer, ManifestManager

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        logging.info("✓ Gemini API configured successfully")
    else:
        logging.warning("⚠️ GEMINI_API_KEY not found in environment")
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Warning: google-generativeai package not installed")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Warning: sklearn not installed")

__version__ = "16.30"

# Global utilities
text_utils = TextUtils()

# Load artist specs and other JSON data
try:
    ARTIST_SPECS_DATA = _load_json_data("artist_specs.json", "Artist Specs")
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.critical(f"FATAL: Could not load artist_specs.json: {e}")
    ARTIST_SPECS_DATA = {}  # Allow import but fail at runtime if used

try:
    APP_TRACKER_SCHEMA_DATA = _load_json_data("app_tracker_schema.json", "App Tracker Schema")
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.critical(f"FATAL: Could not load app_tracker_schema.json: {e}")
    APP_TRACKER_SCHEMA_DATA = {}  # Allow import but fail at runtime if used


# Cover letter signature template
COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}"""

logger = logging.getLogger(__name__)
# ============================================================================
# CLERKEXTRACTOR CLASS
# ============================================================================

class ClerkExtractor:

    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self._validate_master_resume_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        validation_results = []

        experience_sections = self._build_experience_sections()

        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([bullet['bullet_text'] for bullet in section.get('bullets', [])])

        bullet_dicts = [{'bullet_text': b} for b in all_bullets]

        extracted_data = {
            "experience_sections": experience_sections,
            "header": self.master_resume.get("header", {}),
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications_and_credentials", [])
        }

        return extracted_data, validation_results

    def _validate_master_resume_structure(self):
        required_keys = ["owner", "professional_experience", "education", "certifications_and_credentials", "strategic_and_technical_competencies"]
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")

        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            raise ValueError(f"MASTER_RESUME_JSON is missing required keys: {', '.join(missing_keys)}")
        print("  ✓ Master resume structure validated.")

    def _build_experience_sections(self) -> List[Dict]:
        experience_sections = []

        for exp in self.master_resume.get("professional_experience", []):
            bullets = []
            bullet_source = exp.get("bullet_pool", exp.get("highlights", []))

            for bullet_text in bullet_source:
                bullets.append({
                    "bullet_text": bullet_text,
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.Verbatim.value
                })

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""),
                "end_date": exp.get("dates", {}).get("end", ""),
                "overview": exp.get("overview", ""),
                "bullets": bullets,
                "highlights": [bullet['bullet_text'] for bullet in bullets]
            })

        return experience_sections

import re
from typing import List, Dict, Any, Optional

# ============================================================================
# DATAENRICHER CLASS
# ============================================================================

class DataEnricher:

    def __init__(self, enricher_config: EnricherConfig = None):
        self.duplicate_detector = DuplicateDetector()
        if enricher_config is None:
            enricher_config = EnricherConfig()
        self.CANONICAL_VERBS = enricher_config.canonical_verbs

    def _canonicalize_verbs(self, text: str) -> List[str]:
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

        experience_sections = extracted_data.get("experience_sections", [])

        all_bullets = []
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                canonical_verbs = self._canonicalize_verbs(bullet.get("bullet_text", ""))
                bullet["canonical_verbs"] = canonical_verbs

                all_bullets.append(bullet)

        duplicates = self.duplicate_detector.find_duplicates(all_bullets)
        if duplicates:
            validation_results.append(ValidationResult(
                rule_id="DUPLICATE_BULLETS",
                passed=False,
                severity=ValidationSeverity.HIGH,
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



# ============================================================================
# DUPLICATEDETECTOR CLASS
# ============================================================================

# ============================================================================
# CONSTRAINTFAILURECLASSIFIER CLASS
# ============================================================================


COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}""" # Added two spaces at the end of each line to force Markdown line breaks



# ============================================================================
# ARTISTGENERATOR CLASS
# ============================================================================

class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, artist_specs: Dict, artist_config: ArtistConfig, content_constraints: ContentConstraintsConfig, **kwargs):
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.artist_specs = artist_specs
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.constraints = content_constraints
        self.artist_config = artist_config
        
        if kwargs:
            logging.debug(f"ArtistGenerator received extra kwargs: {list(kwargs.keys())}")
            self.previous_failures = kwargs.get('previous_failures', [])
        
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

        self.SECTION_GENERATION_SPECS = self._parse_specs(self.artist_specs)
        
        self.PROVENANCE_SPLIT_TARGETS = self._convert_config_keys_to_enums(
            self.artist_config.provenance_split_targets
        )
        self.BULLET_WORD_COUNT_RANGES = self._convert_config_keys_to_enums(
            self.artist_config.bullet_word_count_ranges
        )
        self.NARRATIVE_CONFIG = self._convert_config_keys_to_enums(
            self.artist_config.narrative_config
        )
    
    def _convert_config_keys_to_enums(self, config_dict: Dict) -> Dict:
        result = {}
        for key, value in config_dict.items():
            if isinstance(key, str):
                try:
                    enum_key = ResumeSection[key]
                    result[enum_key] = value
                except KeyError:
                    logging.warning(f"Unknown ResumeSection key '{key}' in config, skipping")
            else:
                result[key] = value
        return result
    
    def _parse_specs(self, raw_specs: Dict) -> Dict['ResumeSection', Dict[str, Any]]:
        try:
            reconstructed_specs = {}
            for section_name, spec in raw_specs.items():
                try:
                    section_enum = ResumeSection[section_name]

                    if 'reasoning_config' in spec and isinstance(spec.get('reasoning_config'), str):
                         config_name = spec['reasoning_config']
                         if hasattr(ReasoningConfig, config_name):
                             spec['reasoning_config'] = getattr(ReasoningConfig, config_name)
                         else:
                              raise AttributeError(f"ReasoningConfig has no attribute '{config_name}'")

                    if 'depends_on' in spec and isinstance(spec.get('depends_on'), str):
                        spec['depends_on'] = ResumeSection[spec['depends_on']]

                    reconstructed_specs[section_enum] = spec
                except (KeyError, AttributeError) as e:
                    logging.error(f"Error parsing spec entry for '{section_name}'. Offending spec snippet: {str(spec)[:200]}...")
                    if isinstance(e, KeyError):
                        logging.error(f"  Reason: Invalid ResumeSection name used as key: '{section_name}'")
                    elif isinstance(e, AttributeError):
                        if 'reasoning_config' in spec and isinstance(spec.get('reasoning_config'), str):
                            config_name = spec['reasoning_config']
                            logging.error(f"  Reason: ReasoningConfig attribute not found: '{config_name}'")
                        elif 'depends_on' in spec and isinstance(spec.get('depends_on'), str):
                            depends_name = spec['depends_on']
                            logging.error(f"  Reason: Depends_on ResumeSection name not found: '{depends_name}'")
                        else:
                            logging.error(f"  Reason: General AttributeError during parsing: {e}")
                    raise HopExecutionError(f"Error parsing spec for '{section_name}': Invalid enum or config name. Details: {e}")

            logging.info("Successfully loaded and parsed artist specs from 'artist_specs.json'.")
            return reconstructed_specs

        except HopExecutionError as he:
             logging.error(f"Spec parsing failed: {he}")
             raise he
        except Exception as e:
            logging.error(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}", exc_info=True)
            raise HopExecutionError(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}")

    def _build_generation_prompt_with_reinforced_constraints(
        self,
        base_prompt: str,
        constraints: Dict[str, Any],
        attempt_number: int
    ) -> str:
        """
        Reinforces constraints progressively across attempts WITHOUT lowering temperature.
        Part of HOP-3 "No Cost/Time Tradeoffs" enhancement (v15_64).
        
        The key insight: Problem is constraint enforcement strength, NOT temperature direction.
        Makes prompts unbreakable even at temp=1.0 through progressive reinforcement.
        
        Args:
            base_prompt: Original generation prompt
            constraints: Dict with constraint parameters (min_wc, max_wc, format rules, etc.)
            attempt_number: Current attempt number (1-indexed)
            
        Returns:
            Enhanced prompt with appropriate constraint language for this attempt
        """
        min_wc = constraints.get('min_wc', constraints.get('min_word_count', 0))
        max_wc = constraints.get('max_wc', constraints.get('max_word_count', 999))
        
        if attempt_number == 1:
            constraint_language = f"""

**CONSTRAINTS (Strict Compliance Required):**
- Word count: MUST be {min_wc}-{max_wc} words (verify before output)
- Format: MUST NOT start with "At [Company]" or "As [Title]"
- Output: MUST be ONLY the requested content (no fences, no preamble)
"""
        
        elif attempt_number == 2:
            constraint_language = f"""

**CRITICAL CONSTRAINTS (Validation Will Reject Non-Compliance):**
❌ AUTOMATIC REJECTION if word count outside {min_wc}-{max_wc}
❌ AUTOMATIC REJECTION if starts with "At", "As", "In my role"
❌ AUTOMATIC REJECTION if contains markdown fences (```)

✓ Count words before submitting
✓ Review output format before submitting
"""
        
        elif attempt_number == 3:
            constraint_language = f"""

**VALIDATION CHECKLIST (Execute Before Output):**
[ ] Count words using MS Word rules: [actual_count]
[ ] Verify: {min_wc} ≤ [actual_count] ≤ {max_wc}
[ ] Check first 3 words: NOT ["At", "As", "In", "The", "This"]
[ ] Check last characters: NOT "```"
[ ] If ANY box unchecked: REGENERATE

OUTPUT ONLY AFTER ALL BOXES CHECKED.
"""
        
        else:
            constraint_language = f"""

**ALGORITHMIC CONSTRAINT ENFORCEMENT:**

STEP 1: Generate content naturally
STEP 2: Count words using: text.split()
STEP 3: IF count < {min_wc}: ADD content to shortest sentence
STEP 4: IF count > {max_wc}: REMOVE least-essential phrase
STEP 5: IF starts with forbidden pattern: DELETE first 2 words, RECAPITALIZE
STEP 6: VERIFY all constraints met
STEP 7: OUTPUT

DO NOT output until STEP 7.
"""
        
        return base_prompt + constraint_language

    def _mechanical_word_count_fix(
        self,
        text: str,
        min_wc: int,
        max_wc: int
    ) -> str:
        """
        Attempts mechanical word count fixes without LLM calls (zero cost).
        Part of HOP-3 enhancement - try mechanical repair before expensive LLM retry.
        
        Args:
            text: Original text to fix
            min_wc: Minimum word count target
            max_wc: Maximum word count target
            
        Returns:
            Mechanically repaired text (or original if mechanical fix not possible)
        """
        current_wc = text_utils.count_words_ms_word_style(text)
        
        if min_wc <= current_wc <= max_wc:
            return text
        
        if current_wc < min_wc:
            words_needed = min_wc - current_wc
            if words_needed <= 3:
                text = text.replace(" w/", " with")
                text = text.replace(" w/o", " without")
                text = text.replace("&", "and")
                return text
        
        elif current_wc > max_wc:
            words_to_remove = current_wc - max_wc
            if words_to_remove <= 3:
                fillers = [" very", " really", " quite", " actually", " basically", " essentially"]
                for filler in fillers:
                    if filler in text:
                        text = text.replace(filler, "", 1)
                        if text_utils.count_words_ms_word_style(text) <= max_wc:
                            return text
        
        return text

    def _pre_flight_constraint_test(
        self,
        section_enum: ResumeSection,
        prompt: str,  # Keep prompt for logging context, but don't use in new prompt
        constraints: Dict
    ) -> bool:
        """
        Tests if constraints are ACHIEVABLE before full generation.
        Quick check with minimal token output to validate constraint feasibility.
        v2: Simplified prompt to *only* analyze the constraints JSON, removing
        the ambiguous "And this task: ..." context that confused the model.
        
        Args:
            section_enum: Section being generated
            prompt: Original generation prompt (for logging only)
            constraints: Constraint dict
            
        Returns:
            True if constraints are achievable, False otherwise
        """
        
        # New, simplified prompt. It ONLY shows the constraints.
        test_prompt = f"""You are a constraint feasibility analyzer.
Your ONLY task is to determine if a set of constraints is logically achievable.

CONSTRAINTS TO ANALZE:
{json.dumps(constraints, indent=2)}

Analyze the constraints above. Are they logically achievable?
For example, is 'min_wc' less than 'max_wc'? Are there any obvious conflicts?

Respond with ONLY the single word 'YES' or the single word 'NO'.
"""
        
        try:
            response, _ = self._call_gemini_api(
                test_prompt,
                ReasoningConfig.DEFAULT, 
                f"{section_enum.name}_ConstraintTest",
                "You are a constraint feasibility analyzer.",
                temperature_override=0.2  # Low temp for analysis
            )
            
            response_clean = response.strip().upper()

            if response_clean == "YES":
                return True
            elif response_clean == "NO":
                logging.warning(
                    f"Constraint pre-flight FAILED for {section_enum.name}: "
                    f"Model responded 'NO', indicating constraints are impossible."
                )
                return False
            else:
                # This catches the original failure mode (AI returning junk)
                logging.warning(
                    f"Constraint pre-flight FAILED for {section_enum.name}: "
                    f"Model did not respond 'YES' or 'NO'. Response: {response[:200]}..."
                )
                return False
            
        except Exception as e:
            logging.warning(f"Constraint pre-flight test failed with error: {e}. Assuming 'YES' to proceed.")
            # Default to True to allow the main loop to run if the test itself fails
            return True

    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> Tuple[str, int]:
        calls_made_this_invocation = 0
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                try:
                    api_key = getattr(genai, '_config', {}).get('api_key', None)
                    if not api_key: raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set and genai not configured.")
                    else: logging.debug(f"Using globally configured Gemini API key for {section_id}.")
                except Exception:
                    raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set and failed to retrieve from genai config.")

            try:
                model = genai.GenerativeModel('gemini-2.5-pro')
            except Exception as model_init_e:
                raise HopExecutionError(f"Failed to initialize Gemini model for {section_id}: {model_init_e}")

            if reasoning_config is None:
                logging.warning(f"Missing reasoning_config for {section_id}. Using default.")
                reasoning_config = ReasoningConfig.DEFAULT
            api_params = reasoning_config_to_api_params(reasoning_config)
            generation_config = api_params["generation_config"]
            sc_count = api_params.get('sc', 1)

            if temperature_override is not None:
                generation_config.temperature = temperature_override
                logging.info(
                    f"  {section_id} API Call: Using Temp: {generation_config.temperature:.1f} (Override: True)"
                )
            else:
                logging.info(
                    f"  {section_id} API Call: Using Temp: {generation_config.temperature:.1f} (Override: False)"
                )

            enhanced_system = enhance_system_prompt_with_reasoning(system_prompt, reasoning_config, section_id)

            if sc_count > 1:
                logging.info(f"  Running Self-Consistency for {section_id} ({sc_count} candidates)...")
                if temperature_override is None: generation_config.temperature = 0.9
                generation_config.candidate_count = sc_count
                candidate_responses = []
                try:
                    if not model: raise HopExecutionError(f"{section_id} SC API call failed: Model not initialized.")
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)

                    if hasattr(response, 'candidates') and response.candidates:
                        for c in response.candidates:
                            candidate_finish_reason = getattr(c, 'finish_reason', None)
                            if candidate_finish_reason == 2:
                                logging.warning(f"    SC Candidate for {section_id} stopped: MAX_TOKENS.")
                                continue
                            elif candidate_finish_reason is not None and candidate_finish_reason != 1:
                                safety_ratings = getattr(c, 'safety_ratings', None)
                                logging.warning(f"    SC Candidate for {section_id} stopped. Finish Reason: {candidate_finish_reason}. Safety: {safety_ratings}")
                                continue

                            if hasattr(c, 'content') and hasattr(c.content, 'parts'):
                                for part in c.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        candidate_responses.append(part.text)

                    if not candidate_responses:
                        block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                        finish_reason = getattr(response.candidates[0], 'finish_reason', None) if hasattr(response, 'candidates') and response.candidates else None
                        raise HopExecutionError(f"{section_id} SC API call returned no valid text candidates. First Candidate Finish: {finish_reason}, Prompt Block: {block_reason}")

                except Exception as e:
                    logging.error(f"    SC API call for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC API call failed: {type(e).__name__} - {e}") from e

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
                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=generation_config.max_output_tokens)
                try:
                    if not model: raise HopExecutionError(f"{section_id} SC synthesis failed: Model not initialized.")
                    calls_made_this_invocation += 1
                    synthesis_response = model.generate_content(synthesis_prompt, generation_config=synthesis_config)

                    synth_finish_reason = getattr(synthesis_response.candidates[0], 'finish_reason', None) if synthesis_response.candidates else None
                    if synth_finish_reason == 2:
                        raise HopExecutionError(f"{section_id} SC synthesis stopped: MAX_TOKENS.")
                    elif synth_finish_reason is not None and synth_finish_reason != 1:
                        synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(synthesis_response, 'prompt_feedback') else 'Unknown'
                        raise HopExecutionError(f"{section_id} SC synthesis stopped. Finish Reason: {synth_finish_reason}. Block Reason: {synth_block_reason}")

                    raw_text = getattr(synthesis_response, 'text', None)
                    if not raw_text:
                        synth_block_reason = getattr(synthesis_response.prompt_feedback, 'block_reason', None) if hasattr(synthesis_response, 'prompt_feedback') else None
                        raise HopExecutionError(f"{section_id} SC synthesis produced no text. Block Reason: {synth_block_reason}")

                    final_text = text_utils.strip_markdown_fences(raw_text)
                    return final_text, calls_made_this_invocation

                except Exception as e:
                    logging.error(f"    SC synthesis for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} SC synthesis failed: {type(e).__name__} - {e}") from e

            else:
                try:
                    if not model: raise HopExecutionError(f"{section_id} generation API call failed: Model not initialized.")
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)

                    finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
                    if finish_reason == 2:
                        raise HopExecutionError(f"{section_id} generation stopped: MAX_TOKENS.")
                    elif finish_reason is not None and finish_reason != 1:
                        block_reason = getattr(response.prompt_feedback, 'block_reason', 'Unknown') if hasattr(response, 'prompt_feedback') else 'Unknown'
                        raise HopExecutionError(f"{section_id} generation stopped. Finish Reason: {finish_reason}. Block Reason: {block_reason}")

                    raw_text = getattr(response, 'text', None)
                    if not raw_text:
                        block_reason = getattr(response.prompt_feedback, 'block_reason', None) if hasattr(response, 'prompt_feedback') else None
                        raise HopExecutionError(f"{section_id} generation returned no text. Block Reason: {block_reason}")

                    final_text = text_utils.strip_markdown_fences(raw_text)
                    return final_text, calls_made_this_invocation

                except Exception as e:
                    logging.error(f"LLM API call for {section_id} failed: {e}", exc_info=True)
                    raise HopExecutionError(f"{section_id} generation API call failed: {type(e).__name__} - {e}") from e

        except HopExecutionError as he:
            raise he
        except Exception as e:
            logging.error(f"Unexpected error in _call_gemini_api for {section_id}: {e}", exc_info=True)
            raise HopExecutionError(f"Unexpected error during {section_id} API call: {e}") from e

    def generate(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
    ) -> Tuple[Dict, List[ValidationResult], int]:

        validation_results = []
        total_api_calls_this_pass = 0
        artist_output = {}

        try:
            artist_output, calls_made = self._generate_artist_output(
                sections_to_generate=sections_to_generate,
                temperature_overrides=temperature_overrides
            )
            total_api_calls_this_pass = calls_made

            generated_keys_str = ", ".join([k for k, v in artist_output.items() if v is not None]) or "None"
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_PASS", passed=True, severity=ValidationSeverity.INFO,
                message=f"Content generation attempted/completed for: {generated_keys_str}"
            ))
            return artist_output, validation_results, total_api_calls_this_pass

        except HopExecutionError as he:
            logging.error(f"Artist generation HALTED during selective run: {he}", exc_info=False)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_HALTED", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation halted: {str(he)}",
                details={"error": str(he)}
            ))
            return artist_output, validation_results, total_api_calls_this_pass

        except Exception as e:
            logging.error(f"Artist generation failed unexpectedly during selective run: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed unexpectedly: {str(e)}",
                details={"error": str(e)}
            ))
            return artist_output, validation_results, total_api_calls_this_pass

    def _generate_artist_output(
        self,
        sections_to_generate: Set[ResumeSection],
        temperature_overrides: Dict[ResumeSection, float]
        ) -> Tuple[Dict, int]:

        output = {}
        total_api_calls = 0
        ordered_sections = sorted(self.SECTION_GENERATION_SPECS.keys(), key=lambda x: (int(x.name.split('_')[0][1:]), x.name))

        for section_enum in ordered_sections:
            if section_enum not in sections_to_generate:
                output[section_enum.value] = None
                continue

            if section_enum not in self.SECTION_GENERATION_SPECS:
                logging.warning(f"No generation spec found for requested section {section_enum.name}. Skipping.")
                output[section_enum.value] = None
                continue
            spec = self.SECTION_GENERATION_SPECS[section_enum]
            generation_method_name = spec["generation_method"]
            section_api_calls = 0
            generated_content = None

            logging.info(f"  Generating section: {section_enum.name} ({section_enum.value})")
            if generation_method_name == "_copy_from_master" or generation_method_name == "_copy_k0_contact" or generation_method_name == "_generate_dummy_header":
                try:
                    method = getattr(self, generation_method_name)
                    if generation_method_name == "_copy_from_master":
                         output[section_enum.value] = method(spec.get("master_data_key"))
                    else:
                         output[section_enum.value] = method()
                    section_api_calls = 0
                except Exception as e:
                    raise HopExecutionError(f"Unexpected error in {generation_method_name} for {section_enum.value}: {e}") from e

            else:
                final_temp = temperature_overrides.get(section_enum)
                if final_temp is None:
                    logging.error(f"  {section_enum.name}: Temperature override NOT FOUND! Halting.")
                    raise HopExecutionError(f"Misconfiguration: Temperature override missing for {section_enum.name}")

                try:
                    method = getattr(self, generation_method_name)

                    method_args = {
                        "temperature_override": final_temp,
                        "section_enum": section_enum
                    }
                    if generation_method_name == "_generate_section_generic":
                        method_args["spec"] = spec
                    elif generation_method_name == "_generate_tailored_bullets_for_experience":
                         method_args.update(spec.get("extra_args", {}))
                         method_args["provenance_targets"] = self.PROVENANCE_SPLIT_TARGETS.get(section_enum, {})
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)
                    elif generation_method_name == "_generate_tailored_overview_for_experience":
                         dependency_enum = spec.get("depends_on")
                         if dependency_enum and output.get(dependency_enum.value) is not None:
                              method_args["generated_bullets"] = output[dependency_enum.value]
                         else:
                              dep_name = dependency_enum.name if dependency_enum else "None"
                              dep_value = dependency_enum.value if dependency_enum else "None"
                              raise HopExecutionError(f"Dependency {dep_name} ({dep_value}) missing for {section_enum.name}")
                         method_args["word_count_range"] = self._get_overview_wc_range(section_enum)
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)

                    generated_content, section_api_calls = method(**method_args)

                    output[section_enum.value] = generated_content
                    total_api_calls += section_api_calls

                    if isinstance(generated_content, str) and "[Placeholder" in generated_content:
                        logging.warning(f"{section_enum.value} generation returned placeholder: {generated_content[:100]}...")

                except HopExecutionError as he:
                    logging.error(f"Generation HALTED at section {section_enum.value} ({generation_method_name}): {he}", exc_info=False)
                    raise he
                except AttributeError as ae:
                     logging.error(f"AttributeError: Method '{generation_method_name}' not found for section {section_enum.value}. Config mismatch?", exc_info=True)
                     raise HopExecutionError(f"Method '{generation_method_name}' not found for {section_enum.value}. Check SECTION_GENERATION_SPECS.") from ae
                except Exception as e:
                    logging.error(f"Unexpected Error generating section {section_enum.value} with {generation_method_name} (Temp: {final_temp}): {e}", exc_info=True)
                    raise HopExecutionError(f"Unexpected error during {section_enum.value} generation: {e}") from e

        final_output_for_this_pass = output

        return final_output_for_this_pass, total_api_calls

    def _copy_k0_contact(self) -> str:
        contact = self.master_resume.get("owner", {}).get("contact", {})
        parts = [f"Phone: {contact.get('phone', '')}", f"Email: {contact.get('email', '')}", f"LinkedIn: {contact.get('linkedin', '')}"]
        return " | ".join(p for p in parts if len(p.split(': ', 1)) > 1 and p.split(': ', 1)[1])

    def _copy_from_master(self, master_data_key: str) -> Any:
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
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if not comp_intel: return []
        diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
        if not isinstance(diff_kw, list): return []
        return diff_kw[:max_count] if max_count else diff_kw

    def _get_problem_solution(self) -> Tuple[str, str]:
        narratives = getattr(self.thematic_analysis, 'problem_solution_narratives', None)
        if not isinstance(narratives, dict): narratives = {}
        problem = (narratives.get('common_problems', ['solving key challenges'])[0] 
                   if narratives.get('common_problems') else 'solving key challenges')
        solution = (narratives.get('solution_patterns', ['delivering impactful results'])[0] 
                    if narratives.get('solution_patterns') else 'delivering impactful results')
        return problem, solution

    def _get_primary_theme(self, default: str = 'key skills') -> str:
        return (self.thematic_analysis.primary_theme.get('name', default) 
                if self.thematic_analysis.primary_theme else default)

    def _build_context_k0_headline(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        return {
            "primary_theme": self._get_primary_theme('Key Expertise'),
            "differentiators_str": ', '.join(self._get_differentiators(5)),
            "min_wc": self.constraints.HEADLINE_WORD_COUNT_MIN,
            "max_wc": self.constraints.HEADLINE_WORD_COUNT_MAX,
            "comp_min_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MIN,
            "comp_max_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MAX
        }

    def _build_context_k1_summary(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        role_classification = getattr(self.thematic_analysis, 'role_classification', {})
        role_archetype = role_classification.get('role_archetype', 'Experienced Professional') if isinstance(role_classification, dict) else 'Experienced Professional'
        archetype_map = {"Executive_Leader": "an executive leader", "Technical_IC": "a hands-on technical expert", "Post-Sales_Customer_Success": "a customer success leader", "Pre-Sales_GTM": "a pre-sales GTM strategist", "Product_Management": "a product management professional"}
        archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."
        problem, solution = self._get_problem_solution()

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
            "min_diff": self.constraints.K1_MIN_DIFFERENTIATORS
        }

    def _build_context_narrative(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        extra_args = spec.get("extra_args", {})
        if not isinstance(extra_args, dict):
            raise HopExecutionError(f"Invalid 'extra_args' format in spec for narrative generation.")

        company_match = extra_args.get("company_match")
        if not company_match:
            raise HopExecutionError(f"Missing 'company_match' in extra_args for narrative generation.")

        if section_enum is None or section_enum not in self.NARRATIVE_CONFIG:
            raise HopExecutionError(f"Missing/invalid config for narrative generation: {section_enum}")

        title = "Default Title"
        exp_section = next((exp for exp in self.master_resume.get('professional_experience', []) 
                           if company_match in exp.get('company', '')), None)
        master_highlights = []
        if exp_section:
            master_highlights_raw = exp_section.get('highlights', exp_section.get('bullet_pool', []))
            if isinstance(master_highlights_raw, list):
                master_highlights = [str(h) for h in master_highlights_raw if isinstance(h, str)]
            title = exp_section.get("title", title)

        if not master_highlights: 
            raise HopExecutionError(f"Cannot generate narrative for {company_match}: Master highlights/bullets not found or empty.")
        
        master_context = "\n".join([f"- {h}" for h in master_highlights])
        rag_keywords = self._get_differentiators(5)
        target_sc = 3

        config = self.NARRATIVE_CONFIG[section_enum]
        min_wc = getattr(self.constraints, config["min_wc_key"], 40)
        max_wc = getattr(self.constraints, config["max_wc_key"], 60)
        combined_signals = list(set(rag_keywords + config["rag_signals"]))[:7]
        focus_instruction = config["focus"]
        k0_themes = config["k0_themes"]

        return {
            "company_name": company_match,
            "title": title,
            "target_sc": target_sc,
            "min_wc": min_wc,
            "max_wc": max_wc,
            "master_context": master_context,
            "combined_signals_str": ', '.join(combined_signals), 
            "focus_instruction": focus_instruction,
            "k0_themes_str": ', '.join(k0_themes), 
            "rag_keywords_str": ', '.join(rag_keywords),
        }

    def _build_context_k10_skills(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        try:
            primary_theme_kw = (self.thematic_analysis.primary_theme.get('keywords', []) 
                               if self.thematic_analysis and self.thematic_analysis.primary_theme else [])
            if not isinstance(primary_theme_kw, list): primary_theme_kw = []
            combined_keywords = list(set(primary_theme_kw + self._get_differentiators()))[:15]
            return {"combined_keywords_str": ', '.join(combined_keywords)}
        except Exception as e:
            logging.error(f"Error building K10 context: {e}")
            return {"combined_keywords_str": "relevant skills"}

    def _build_context_k11_cover_letter(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        problem, solution = self._get_problem_solution()
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
        try:
            skills_list_final = []
            skills_intermediate = [re.sub(r'^[•*\-\d\.]+\s*', '', s).strip() for s in skills_text.split('\n') if s.strip()]
            malformed_count = 0
            for skill in skills_intermediate:
                word_count = text_utils.count_words_ms_word_style(skill)
                if 1 <= word_count <= 3:
                    skills_list_final.append(skill)
                else:
                    logging.warning(f"{section_enum.value}: Discarding malformed skill '{skill}' (words: {word_count})")
                    malformed_count += 1

            if len(skills_list_final) != 12:
                raise HopExecutionError(f"{section_enum.value} generation failed: Expected 12 valid skills, found {len(skills_list_final)}. Preview: {skills_text[:100]}...")
            if malformed_count > 0:
                 logging.warning(f"{section_enum.value}: Discarded {malformed_count} malformed skills.")

            return skills_list_final

        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_k11_cover_letter(self, cover_letter_text: str, section_enum: ResumeSection) -> str:
        try:
            expected_signature = self._get_expected_signature()
            fixed_text = cover_letter_text.strip(); current_date_str = datetime.now().strftime("%B %d, %Y")
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text): fixed_text = f"{current_date_str}\n\n{fixed_text}"; logging.warning(f"{section_enum.value}: Added missing date.")
            recipient_placeholder = "Hiring Manager\n[Company Name]"
            if recipient_placeholder not in fixed_text:
                fixed_text = re.sub(r"^(\w+ \d{1,2}, \d{4}\s*)", rf"\1\n{recipient_placeholder}\n", fixed_text, count=1, flags=re.MULTILINE)
                if recipient_placeholder not in fixed_text:
                     logging.warning(f"{section_enum.value}: Failed to add recipient placeholder.")

            salutation = "Dear Hiring Manager,"
            if salutation not in fixed_text:
                fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\s*)", rf"\1\n{salutation}\n", fixed_text, count=1, flags=re.MULTILINE)
                if salutation not in fixed_text:
                     logging.warning(f"{section_enum.value}: Failed to add salutation.")

            closing = "Sincerely,"
            if expected_signature in fixed_text and closing not in fixed_text.split(expected_signature)[0]:
                fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
            elif closing in fixed_text and expected_signature not in fixed_text:
                 fixed_text = fixed_text.rstrip() + f"\n\n{expected_signature}"
            elif closing not in fixed_text and expected_signature not in fixed_text:
                 fixed_text = fixed_text.rstrip() + f"\n\n{closing}\n\n{expected_signature}"
            elif not fixed_text.rstrip().endswith(expected_signature.rstrip()):
                 logging.warning(f"{section_enum.value}: Signature block missing/malformed at end. Attempting fix...")
                 fixed_text = re.sub(r'\n*Sincerely,?[\s\S]*$', '', fixed_text.rstrip(), flags=re.MULTILINE)
                 fixed_text += f"\n\n{closing}\n\n{expected_signature}"

            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text: raise HopExecutionError(f"{section_enum.value} generation failed (placeholder detected).")
            if not all(x in fixed_text for x in [current_date_str, recipient_placeholder, salutation, closing, expected_signature]): logging.warning(f"{section_enum.value}: Structure may still be incomplete after fixes.")

            return fixed_text.strip()
        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_narrative(self, narrative_text: str, section_enum: ResumeSection) -> str:
        if section_enum not in self.SECTION_GENERATION_SPECS:
            logging.error(f"Cannot post-process narrative: Spec missing for {section_enum.name}")
            return narrative_text

        spec = self.SECTION_GENERATION_SPECS[section_enum]
        context = self._build_context_narrative(spec, section_enum=section_enum)
        min_wc = context.get('min_wc', 0); max_wc = context.get('max_wc', float('inf')); target_sc = context.get('target_sc', 0)

        final_wc = text_utils.count_words_ms_word_style(narrative_text); final_sc = text_utils.count_sentences(narrative_text)
        if not (min_wc <= final_wc <= max_wc):
             logging.warning(f"{section_enum.value} narrative WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if target_sc > 0 and not (target_sc -1 <= final_sc <= target_sc + 1):
             logging.warning(f"{section_enum.value} narrative SC ({final_sc}) outside target range ({target_sc-1}-{target_sc+1}).")
        return narrative_text

    def _get_reasoning_config_for_section(self, section_enum: ResumeSection) -> ReasoningConfig:
        config_name = f"{section_enum.name}_CONFIG"
        try:
            config = getattr(ReasoningConfig, config_name, None)
            if config: return config
            logging.warning(f"Specific reasoning config '{config_name}' missing from ReasoningConfig class. Using DEFAULT.")
            return ReasoningConfig.DEFAULT
        except AttributeError:
            logging.warning(f"ReasoningConfig class structure issue or DEFAULT missing. Returning new default.")
            return ReasoningConfig()

    def _get_overview_wc_range(self, section_enum: ResumeSection) -> Tuple[int, int]:
        if section_enum == ResumeSection.K2_UNIFY_OVERVIEW:
             return (self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX)
        elif section_enum == ResumeSection.K3_IBM_OVERVIEW:
             return (self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX)
        else:
             logging.warning(f"No overview WC range explicitly defined for {section_enum.name}. Using default (25-40).")
             return (25, 40)

    def _generate_section_generic(self, spec: Dict, section_enum: ResumeSection, temperature_override: Optional[float]) -> Tuple[Any, int]:
        context = {}
        if "context_builder" in spec and spec["context_builder"]:
            builder_method_name = spec["context_builder"]
            builder_method = getattr(self, builder_method_name, None)
            if builder_method:
                 context = builder_method(spec, section_enum=section_enum)
            else:
                 raise HopExecutionError(f"Context builder method '{builder_method_name}' not found for {section_enum.name}")

        prompt_template = spec.get("prompt_template")
        if not prompt_template: raise HopExecutionError(f"Prompt template missing in spec for {section_enum.name}")

        try: prompt = prompt_template.format_map(defaultdict(lambda: '[MISSING_CONTEXT]', **context))
        except KeyError as ke: raise HopExecutionError(f"Missing key '{ke}' in context for {section_enum.name} prompt.")
        except Exception as fmt_e: raise HopExecutionError(f"Error formatting prompt for {section_enum.name}: {fmt_e}")

        reasoning_config = self._get_reasoning_config_for_section(section_enum)
        system_prompt = spec.get("system_prompt", "You are a helpful assistant.")

        raw_output, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_enum.value, system_prompt,
            temperature_override=temperature_override
        )

        if "post_processor" in spec and spec["post_processor"]:
            processor_method_name = spec["post_processor"]
            processor_method = getattr(self, processor_method_name, None)
            if processor_method:
                 processed_output = processor_method(raw_output, section_enum)
                 return processed_output, call_count
            else:
                 raise HopExecutionError(f"Post-processor method '{processor_method_name}' not found for {section_enum.name}")
        else:
            return raw_output, call_count

    # DEPRECATED: Removed _get_feedback_instruction (Spec 1.3)
    # This method is part of a deprecated retry strategy, superseded by
    # _build_generation_prompt_with_reinforced_constraints which modifies
    # prompts based on attempt number rather than specific failure types.

    def _get_expected_signature(self) -> str:
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        try:
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
        exp_snippets = ""
        unify_overview = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets_raw = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        ibm_overview = self.enriched_scaffold.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets_raw = self.enriched_scaffold.get(ResumeSection.K3_IBM_BULLETS.value, [])

        if unify_overview or unify_bullets_raw:
             exp_snippets += f"Recent Experience (Unify):\n{unify_overview or '(Overview not available)'}\n"
             unify_bullet_texts = [b.get('text', '') for b in unify_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in unify_bullet_texts[:2] if text]) + "\n"
        if ibm_overview or ibm_bullets_raw:
             exp_snippets += f"Prior Experience (IBM):\n{ibm_overview or '(Overview not available)'}\n"
             ibm_bullet_texts = [b.get('text', '') for b in ibm_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in ibm_bullet_texts[:2] if text]) + "\n"

        return exp_snippets if exp_snippets.strip() else "Candidate has extensive experience in relevant areas.\n"

    def _generate_tailored_overview_for_experience(
        self,
        generated_bullets: List[Dict],
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_enum: ResumeSection, temperature_override: Optional[float] = None, **kwargs
    ) -> Tuple[str, int]:
        section_id = section_enum.value
        if not generated_bullets:
            raise HopExecutionError(f"Cannot generate overview for {section_id}: No generated bullets provided.")

        bullet_texts = []
        for i, bullet_data in enumerate(generated_bullets):
             text = ""
             if isinstance(bullet_data, dict):
                 text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
             elif isinstance(bullet_data, str):
                 text = bullet_data
             if not text: logging.warning(f"Skipping empty/invalid bullet {i} for overview {section_id}"); continue
             bullet_texts.append(f"* {text.strip()}")
        if not bullet_texts: raise HopExecutionError(f"Cannot generate overview for {section_id}: All bullets invalid.")

        bullet_summary_input = "\n".join(bullet_texts)
        min_wc, max_wc = word_count_range

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

        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview or "KEY THEMES" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")
        final_wc = text_utils.count_words_ms_word_style(synthesized_overview); final_sc = text_utils.count_sentences(synthesized_overview)
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} overview WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if not (1 <= final_sc <= 2): logging.warning(f"{section_id} overview SC ({final_sc}) outside target (1-2).")
        return synthesized_overview, call_count

    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id_str: str) -> List[Dict]:
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

    def _rewrite_bullet_for_word_count(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id_str: str, temperature_override: Optional[float] = None, max_retries: int = 5) -> Tuple[str, int]:
        total_calls = 0
        min_wc, max_wc = target_word_count_range # Ideal range, e.g., (25, 40)
        
        # --- NEW: Define tiered tolerances based on user request ---
        # Note: The "Low" (23-42) and "Medium" (21-44) tiers both "pass".
        # We use the widest "pass" tier as the acceptable range.
        # Halting tiers are "High" (15-50) and "Critical" (<15, >50).
        # This means the *actual* logic is:
        # - PASS if: 21 <= wc <= 44
        # - HALT if: wc < 21 or wc > 44
        # (The High/Critical distinction will be made in validation.py)
        
        # This is the "Medium" band, which is the widest acceptable range to PASS.
        ACCEPTABLE_MIN_WC = 21 
        ACCEPTABLE_MAX_WC = 44
        # --- End new definitions ---

        if temperature_override is not None:
            temperature_schedule = [temperature_override, 0.8, 0.6, 0.4, 0.2]
        else:
            temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2]
        
        last_rewritten_text = original_bullet_text
        last_word_count = text_utils.count_words_ms_word_style(original_bullet_text)
        
        logging.info(f"  Attempting mechanical word count fix for {section_id_str} (zero cost)...")
        mechanical_fix = self._mechanical_word_count_fix(original_bullet_text, min_wc, max_wc)
        mechanical_wc = text_utils.count_words_ms_word_style(mechanical_fix)
        
        if min_wc <= mechanical_wc <= max_wc and mechanical_fix != original_bullet_text:
            logging.info(
                f"  ✓ MECHANICAL REPAIR SUCCESS for {section_id_str}: "
                f"{text_utils.count_words_ms_word_style(original_bullet_text)} → {mechanical_wc} words (no API calls)"
            )
            return mechanical_fix, 0
        
        logging.info(f"  Mechanical fix {'did not help' if mechanical_fix == original_bullet_text else 'insufficient'}. Proceeding with LLM retries...")
        
        for attempt in range(max_retries):
            current_temp = temperature_schedule[min(attempt, len(temperature_schedule) - 1)]
            
            logging.info(
                f"  Bullet WC rewrite for {section_id_str}, Attempt {attempt + 1}/{max_retries}, "
                f"Temp: {current_temp:.1f}, Target: {min_wc}-{max_wc} words"
            )
            
            try:
                base_prompt = f"""Rewrite the following resume bullet point to meet a specific word count constraint, preserving core meaning, metrics, and tone.

ORIGINAL BULLET:
{original_bullet_text}

TARGET: {min_wc}-{max_wc} words

CORE REQUIREMENTS:
1. Preserve all metrics, numbers, and specific achievements.
2. Maintain professional resume tone.
3. **Do NOT start with 'At [Company]', 'As [Title]', etc.**
4. Output ONLY the rewritten bullet text. No markdown fences (```).
"""
                
                enhanced_prompt = self._build_generation_prompt_with_reinforced_constraints(
                    base_prompt,
                    {'min_wc': min_wc, 'max_wc': max_wc},
                    attempt + 1
                )
                
                try:
                    reasoning_config = ReasoningConfig.DEFAULT
                except AttributeError:
                    logging.warning("ReasoningConfig.DEFAULT missing. Creating default.")
                    reasoning_config = ReasoningConfig()
                
                system_prompt = "You are an expert resume editor concisely rewriting bullets to meet strict word count targets."
                
                try:
                    rewritten_text, call_count = self._call_gemini_api(
                        enhanced_prompt, reasoning_config, f"{section_id_str}_RewriteWC_Attempt{attempt+1}", 
                        system_prompt, temperature_override=current_temp
                    )
                    total_calls += call_count
                    
                    rewritten_wc = text_utils.count_words_ms_word_style(rewritten_text)
                    last_rewritten_text = rewritten_text
                    last_word_count = rewritten_wc
                    
                    if min_wc <= rewritten_wc <= max_wc:
                        logging.info(
                            f"  ✓ Bullet WC rewrite SUCCESS for {section_id_str} on attempt {attempt + 1}. "
                            f"Word count: {rewritten_wc} (target: {min_wc}-{max_wc}), "
                            f"Total API calls: {total_calls}"
                        )
                        return rewritten_text, total_calls
                    else:
                        logging.warning(
                            f"  Bullet WC rewrite attempt {attempt + 1} FAILED for {section_id_str}. "
                            f"Got {rewritten_wc} words, target: {min_wc}-{max_wc}. "
                            f"{'Retrying...' if attempt < max_retries - 1 else 'No more retries.'}"
                        )
                        # Don't raise HopExecutionError here, let the loop finish
                
                except HopExecutionError as he:
                    # Log the error but don't re-raise, allow loop to continue or fail gracefully
                    logging.error(f"  HopExecutionError during WC rewrite attempt {attempt + 1}: {he}")
                    if attempt == max_retries - 1:
                        # If it fails on the last try, we'll use the last known values
                        logging.error("  Last rewrite attempt failed. Proceeding to final tolerance check.")
                except Exception as e:
                    logging.error(f"  Unexpected error during WC rewrite attempt {attempt + 1} for {section_id_str}: {e}")
                    if attempt == max_retries - 1:
                        # If it fails on the last try, we'll use the last known values
                        logging.error("  Last rewrite attempt failed unexpectedly. Proceeding to final tolerance check.")
            
            except Exception as outer_e:
                logging.error(f"  Outer loop error during WC rewrite for {section_id_str}: {outer_e}")
                if attempt == max_retries - 1:
                    break # Exit loop to go to final check

        # --- NEW LOGIC: Triage *after* all retries are exhausted ---
        logging.info(f"  Rewrite retries exhausted for {section_id_str}. Final word count: {last_word_count}. Checking tolerance...")

        # Check against the widest "pass" range (Medium: 21-44)
        if ACCEPTABLE_MIN_WC <= last_word_count <= ACCEPTABLE_MAX_WC:
            logging.warning(
                f"  ✓ Bullet WC rewrite PASSED (TOLERANCE) for {section_id_str}. "
                f"Final count: {last_word_count} (Ideal: {min_wc}-{max_wc}, Acceptable: {ACCEPTABLE_MIN_WC}-{ACCEPTABLE_MAX_WC}). "
                f"Total API calls: {total_calls}"
            )
            return last_rewritten_text, total_calls
        else:
            # This is a High or Critical defect. HALT.
            logging.error(
                f"  ✗ Bullet WC rewrite FAILED (HALT) for {section_id_str}. "
                f"Final count: {last_word_count} is outside the acceptable tolerance ({ACCEPTABLE_MIN_WC}-{ACCEPTABLE_MAX_WC})."
            )
            raise HopExecutionError(
                f"{section_id_str}_RewriteWC failed after {max_retries} attempts. "
                f"Final word count: {last_word_count}, target: {min_wc}-{max_wc}, "
                f"acceptable range: {ACCEPTABLE_MIN_WC}-{ACCEPTABLE_MAX_WC}. "
                f"Temperature schedule used: {temperature_schedule[:max_retries]}. "
                f"Total API calls: {total_calls}"
            ) 
 
    def _validate_and_potentially_rewrite_bullets(self, selected_bullets_structured: List[Dict], min_target: int, max_target: int, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        final_bullets = []; total_rewrite_calls = 0; logging.info(f"  Validating word count for {section_id_str} ({min_target}-{max_target})")
        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict): raise HopExecutionError(f"Invalid item in bullet list for {section_id_str}[{i}]")
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', '')); original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            word_count = bullet_data.get('word_count', text_utils.count_words_ms_word_style(original_text))
            if not original_text: raise HopExecutionError(f"Empty bullet in {section_id_str}[{i}].")

            if not (min_target <= word_count <= max_target):
                logging.warning(
                    f"  WC Check FAIL for {section_id_str}[{i}]: Count={word_count} (Target: {min_target}-{max_target}). "
                    f"Attempting rewrite with enhanced temperature-based retry (temps: 1.0→0.8→0.6→0.4→0.2) for bullet: '{original_text[:50]}...'"
                )
                try:
                    rewritten_text, rewrite_calls = self._rewrite_bullet_for_word_count(original_text, (min_target, max_target), f"{section_id_str}_RewriteWC_{i}", temperature_override, max_retries=5)
                    total_rewrite_calls += rewrite_calls; rewritten_word_count = text_utils.count_words_ms_word_style(rewritten_text)
                    logging.info(
                        f"    Rewrite SUCCESS for {section_id_str}[{i}]. "
                        f"Old count: {word_count}, New count: {rewritten_word_count}, "
                        f"API calls: {rewrite_calls}"
                    )
                    new_provenance = BulletProvenance.Customized.value if original_provenance == BulletProvenance.Verbatim.value else original_provenance
                    final_bullets.append({"text": rewritten_text, "provenance": new_provenance, "word_count": rewritten_word_count, "original_text_if_rewritten": original_text})
                except HopExecutionError as rewrite_he:
                    logging.error(f"    Rewrite FAILED for {section_id_str}[{i}]: {rewrite_he}")
                    raise HopExecutionError(f"Bullet WC correction failed for {section_id_str}[{i}]") from rewrite_he
                except Exception as e:
                    logging.error(f"Unexpected error during WC correction for {section_id_str}[{i}]: {e}", exc_info=True)
                    raise HopExecutionError(f"Unexpected error during bullet WC correction for {section_id_str}[{i}]") from e
            else:
                final_bullets.append({"text": original_text, "provenance": original_provenance, "word_count": word_count})
        logging.info(f"  ✓ Word count validation/rewrite complete for {section_id_str}. Rewrite API Calls: {total_rewrite_calls}")
        return final_bullets, total_rewrite_calls

    def _generate_lightly_customized_bullets(self, source_bullets_text: List[str], section_id_str: str, thematic_analysis: ThematicAnalysis, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
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
            try: reasoning_config = ReasoningConfig.DEFAULT
            except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); reasoning_config = ReasoningConfig()

            system_prompt = "You are an expert resume editor subtly tailoring bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            rewritten_bullets_text = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]
            if len(rewritten_bullets_text) != len(source_bullets_text): raise HopExecutionError(f"{section_id_str} LLM returned {len(rewritten_bullets_text)} customized bullets, expected {len(source_bullets_text)}.")
            result_list = [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in rewritten_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} customization failed: {e}") from e

    def _generate_synthetic_bullets(self, count: int, company_name: str, job_description: str, thematic_analysis: ThematicAnalysis, context_bullets: str, reasoning_config: ReasoningConfig, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
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

            prompt = f"""You are an expert resume writer tasked with generating synthetic, impactful resume bullet points that align with a specific job description and existing resume content.

**CONTEXT:**
* **Target Company/Role Context:** {company_name} (details below)
* **Primary Theme:** {primary_theme}
* **Target Keywords/Differentiators:** {', '.join(context_keywords)}
* **Existing Bullets (for style and context):**
{context_bullets}
* **Target Job Description Snippet:**
{job_description[:500]}...

**TASK:**
Generate EXACTLY {count} unique, plausible, and impactful SYNTHETIC resume bullet points relevant to the role context and keywords provided. These should sound like real achievements but do not need to be based on specific facts from the existing bullets.

**ABSOLUTELY CRITICAL REQUIREMENTS:**
1.  Generate EXACTLY {count} bullet points.
2.  Each bullet MUST start with an asterisk and a space ('* ').
3.  Bullets should be concise and achievement-oriented, ideally incorporating metrics where plausible (e.g., "Reduced X by Y%", "Increased Z by $A million").
4.  Subtly align with the **Primary Theme** and **Target Keywords/Differentiators**.
5.  Ensure bullets sound authentic and professional for the target role level.
6.  **Do NOT** start bullets with generic phrases like 'Responsible for...', 'Duties included...', 'At [Company]', 'As [Title]', etc. Use strong action verbs.
7.  Output ONLY the {count} bullet points, one per line. No preamble, explanation, or markdown fences like ```.

**SYNTHETIC BULLETS (Exactly {count}):**
"""

            system_prompt = "You generate plausible, impactful, synthetic resume bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]
            if len(synthetic_bullets_text) != count: raise HopExecutionError(f"{section_id_str} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}).")
            result_list = [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in synthetic_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} synthetic generation failed: {e}") from e

    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            provenance_targets: Dict[str, int], reasoning_config: ReasoningConfig, section_enum: ResumeSection,
            temperature_override: Optional[float] = None, is_competencies: bool = False, **kwargs
    ) -> Tuple[List[Dict], int]:
        section_id_str = section_enum.value
        logging.info(f"  Generating bullets for {section_enum.name} ({section_id_str}) (Targets: {provenance_targets})")
        total_calls_for_section = 0
        final_bullets = []

        master_bullets_source = []
        if is_competencies:
             master_bullets_source_raw = self.master_resume.get("strategic_and_technical_competencies", [])
             if isinstance(master_bullets_source_raw, list):
                 master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
             else: logging.warning("Master 'strategic_and_technical_competencies' is not a list.")
        else:
             exp_section = next((exp for exp in self.master_resume.get('professional_experience', []) if company_name in exp.get('company', '')), None)
             if not exp_section: raise HopExecutionError(f"Master data not found for '{company_name}' needed by {section_enum.name}")
             master_bullets_key = "bullet_pool" if "bullet_pool" in exp_section else "highlights"
             master_bullets_source_raw = exp_section.get(master_bullets_key, [])
             if isinstance(master_bullets_source_raw, list):
                  master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
             else: logging.warning(f"Master '{master_bullets_key}' for {company_name} is not a list.")

        master_bullets_structured = []
        for bullet_text in master_bullets_source:
             if bullet_text and bullet_text.strip():
                 cleaned_text = bullet_text.strip()
                 master_bullets_structured.append({"bullet_text": cleaned_text, "text": cleaned_text, "provenance": BulletProvenance.Verbatim.value, "word_count": text_utils.count_words_ms_word_style(cleaned_text)})
             else: logging.warning(f"Skipping empty master item for {company_name or 'Competencies'}")

        verbatim_count = provenance_targets.get('Verbatim', 0); customized_count = provenance_targets.get('Customized', 0); synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        if not master_bullets_structured and (verbatim_count > 0 or customized_count > 0): raise HopExecutionError(f"{section_enum.name} Cannot select/customize: No valid master items found.")

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
                try: default_reasoning = ReasoningConfig.DEFAULT
                except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); default_reasoning = ReasoningConfig()

                response_select, calls_v_select = self._call_gemini_api(prompt_select, default_reasoning, f"{section_id_str}_SelectV", system_prompt_select, temperature_override=temperature_override)
                total_calls_for_section += calls_v_select
                selected_texts = [line.strip().lstrip('- ') for line in response_select.split('\n') if line.strip()]
                verbatim_bullets_selected = self._validate_llm_bullet_selection(selected_texts, master_bullets_structured, verbatim_count, f"{section_id_str}_SelectV")
                final_bullets.extend(verbatim_bullets_selected)
            except HopExecutionError as he: raise he
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Verbatim selection failed unexpectedly: {e}") from e

        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} items...")
            used_verbatim_texts = {b['bullet_text'] for b in verbatim_bullets_selected}; available_for_custom = [b for b in master_bullets_structured if b['bullet_text'] not in used_verbatim_texts]
            if len(available_for_custom) < customized_count: raise HopExecutionError(f"{section_enum.name} Cannot customize {customized_count}: Not enough unique items remaining ({len(available_for_custom)}).")
            random.shuffle(available_for_custom); candidates_for_custom = available_for_custom[:customized_count]; source_texts_for_custom = [b['bullet_text'] for b in candidates_for_custom]
            try:
                customized_bullets, calls_c = self._generate_lightly_customized_bullets(source_texts_for_custom, f"{section_id_str}_CustomC", self.thematic_analysis, temperature_override)
                total_calls_for_section += calls_c
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he: raise he
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Customization failed unexpectedly: {e}") from e

        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic items...")
            context_bullets_text = '\n'.join([f"- {b.get('text', '')}" for b in final_bullets if isinstance(b, dict) and b.get('text')])
            try:
                synthetic_bullets, calls_s = self._generate_synthetic_bullets(synthetic_count, company_name if not is_competencies else "Competencies", self.job_description, self.thematic_analysis, context_bullets_text, reasoning_config, f"{section_id_str}_SynthS", temperature_override)
                total_calls_for_section += calls_s
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he: raise he
            except Exception as e: raise HopExecutionError(f"{section_enum.name} Synthetic generation failed unexpectedly: {e}") from e

        if len(final_bullets) != total_expected_count: raise HopExecutionError(f"{section_enum.name} Internal Error: Generated {len(final_bullets)}, expected {total_expected_count}.")

        target_range = self.BULLET_WORD_COUNT_RANGES.get(section_enum)
        if target_range is None: raise HopExecutionError(f"Config Error: WC range not found for {section_enum.name}.")
        min_target, max_target = target_range; logging.info(f"    Validating word counts ({min_target}-{max_target})...")
        try:
            final_bullets_validated, calls_rewrite = self._validate_and_potentially_rewrite_bullets(final_bullets, min_target, max_target, section_id_str, temperature_override)
            total_calls_for_section += calls_rewrite
            final_bullets = final_bullets_validated
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_enum.name} Word count validation/rewrite failed unexpectedly: {e}") from e

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
                try: default_reasoning = ReasoningConfig.DEFAULT
                except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); default_reasoning = ReasoningConfig()

                response_reorder, calls_reorder = self._call_gemini_api(prompt_reorder, default_reasoning, f"{section_id_str}_Reorder", system_prompt_reorder, temperature_override=temperature_override)
                total_calls_for_section += calls_reorder
                reordered_texts_raw = [line.strip() for line in response_reorder.split('\n') if line.strip()]
                reordered_texts = [re.sub(r"^\d+\.\s*", "", txt).strip() for txt in reordered_texts_raw]

                if len(reordered_texts) != total_expected_count: raise HopExecutionError(f"{section_enum.name} Reordering failed: Count mismatch (Expected {total_expected_count}, Got {len(reordered_texts)}). Preview: {reordered_texts_raw[:3]}")
                final_ordered_bullets_dicts = []; original_texts_map = {b.get('text'): b for b in final_bullets if isinstance(b, dict) and b.get('text')}; used_original_texts = set()
                for reordered_text in reordered_texts:
                    matched_dict = original_texts_map.get(reordered_text)
                    if matched_dict:
                        if reordered_text in used_original_texts: raise HopExecutionError(f"{section_enum.name} Reordering failed: Duplicate bullet found in output: '{reordered_text[:50]}...'")
                        final_ordered_bullets_dicts.append(matched_dict)
                        used_original_texts.add(reordered_text)
                    else:
                         best_match = None; best_sim = 0.8
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
                raise he
            except Exception as e:
                raise HopExecutionError(f"{section_enum.name} Reordering failed unexpectedly: {e}") from e
        else:
            logging.info(f"    Skipping reordering for Competencies section ({section_enum.name}).")
            if is_competencies:
                for item in final_bullets:
                    if isinstance(item, dict) and 'text' in item:
                        cleaned_text = re.sub(r'^\*\s*\*\*(.*?):\*\*\s*', r'\1:', item['text']).strip()
                        cleaned_text = re.sub(r'^[•*]\s*', '', cleaned_text).strip()
                        item['text'] = cleaned_text
                        item['word_count'] = text_utils.count_words_ms_word_style(cleaned_text)
            return final_bullets, total_calls_for_section



# ============================================================================
# VALIDATIONCONTEXT CLASS
# ============================================================================

# ============================================================================
# GATEDECISIONENGINE CLASS
# ============================================================================

# ============================================================================
# TEXTSANITIZER CLASS
# ============================================================================

class TextSanitizer:
    """
    Sanitizes text content within the staging buffer.
    This class was missing from the refactored files.
    """
    def __init__(self):
        self.sanitization_counts = defaultdict(int)
        # TextUtils is already imported in workflow.py
        self.text_utils = TextUtils()

    def sanitize_buffer(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[List[ValidationResult], Dict[str, Any]]:
        """
        Iterates through the buffer and sanitizes all string content.
        """
        if not staging_buffer.is_locked():
            # This should not happen if called from HOP-4.5
            staging_buffer.lock()
            
        sanitized_data = {}
        validation_results = []
        
        for key, value in staging_buffer.data.items():
            sanitized_value, fixes = self._sanitize_item(value)
            sanitized_data[key] = sanitized_value
            if fixes > 0:
                self.sanitization_counts[key] += fixes
                
        total_fixes = sum(self.sanitization_counts.values())
        
        if total_fixes > 0:
            validation_results.append(ValidationResult(
                rule_id="H4.5_SANITIZATION_APPLIED",
                passed=True, # This is a fix, not a failure
                severity=ValidationSeverity.INFO,
                message=f"Sanitization applied, {total_fixes} fixes made.",
                details=dict(self.sanitization_counts)
            ))
        
        return validation_results, sanitized_data

    def _sanitize_item(self, item: Any) -> Tuple[Any, int]:
        """Recursively sanitizes an item (str, list, dict)."""
        total_fixes = 0
        if isinstance(item, str):
            sanitized_text = self.text_utils.sanitize_text(item)
            if sanitized_text != item:
                total_fixes = 1
            return sanitized_text, total_fixes
        elif isinstance(item, list):
            sanitized_list = []
            for sub_item in item:
                sanitized_sub_item, fixes = self._sanitize_item(sub_item)
                sanitized_list.append(sanitized_sub_item)
                total_fixes += fixes
            return sanitized_list, total_fixes
        elif isinstance(item, dict):
            sanitized_dict = {}
            for k, v in item.items():
                sanitized_v, fixes = self._sanitize_item(v)
                sanitized_dict[k] = sanitized_v
                total_fixes += fixes
            return sanitized_dict, total_fixes
        else:
            return item, 0


# ============================================================================
# FILERENDERER CLASS
# ============================================================================

class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator', company_name: str, job_title: str):
        self.master_resume = master_resume
        self.orchestrator = orchestrator
        self.company_name = company_name
        self.job_title = job_title
        self._initialize_render_dispatch()
        self.logger = logging.getLogger(__name__)

    @functools.cached_property
    def _safe_company_name(self) -> str:
        name = re.sub(r'[^\w\s-]', '', self.company_name)
        return re.sub(r'[-\s]+', '_', name).strip('_')

    @functools.cached_property
    def _safe_job_title(self) -> str:
        title = re.sub(r'[^\w\s-]', '', self.job_title)
        return re.sub(r'[-\s]+', '_', title).strip('_')

    def _strip_fences(self, content: str, artifact_name: str) -> str:
        stripped_content = text_utils.strip_markdown_fences(content)

        if len(stripped_content) < len(content):
            self.logger.warning(f"  ⚠️ Removed markdown fences ``` from final {artifact_name} content.")

        return stripped_content

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str,
        job_title: str,
        thematic_analysis: ThematicAnalysis,
        job_description: Optional[str] = None,
        jd_url: str = ""
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report, App Tracker).
        Uses K0-K11 Enum scheme. Includes fence stripping for relevant artifacts.
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        """
        file_paths = {}
        file_contents = {}
        validation_results = []

        try:
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content
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
            file_contents['resume_md'] = f"[ERROR: Resume Rendering Failed: {e}]"

        try:
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content
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
            file_contents['cover_letter'] = content
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
            file_contents['qa_report'] = content_placeholder
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
            path, content, app_tracker_validation_results = self._render_app_tracker_artifact(file_paths, jd_url=jd_url)
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content
            validation_results.extend(app_tracker_validation_results)
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

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        raw_content = self._render_resume_markdown(staging_buffer)
        final_content = self._strip_fences(raw_content, "Resume MD")

        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        base_filename = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        path = f"{base_filename}.md"

        return path, final_content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> Tuple[str, str]:
        raw_content = self._render_skills(staging_buffer, job_description)
        final_content = self._strip_fences(raw_content, "Skills TXT")
        path = f"Skills_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        raw_content = staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        final_content = self._strip_fences(raw_content, "Cover Letter TXT")
        path = f"CoverLetter_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_qa_report_artifact(self) -> Tuple[str, str]:
        path = f"QA_Report_{self._safe_company_name}_{self._safe_job_title}.md"
        return path, "[QA Report Content Placeholder - Generated in HOP-8]"

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str], jd_url: str = "") -> Tuple[str, str, List[ValidationResult]]:
        app_tracker_data = self._render_app_tracker(file_paths, jd_url=jd_url)
        validation_results = []
        try:
            validator = AppTrackerQAValidator(validator_config=self.config.validator)
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
        {"type": "education", "source": ResumeSection.K7_EDUCATION},
        {"type": "header", "text": "## CERTIFICATIONS & CREDENTIALS"},
        {"type": "certifications", "source": ResumeSection.K8_CERTIFICATIONS},
        {"type": "header", "text": "## STRATEGIC & TECHNICAL COMPETENCIES"},
        {"type": "competencies", "source": ResumeSection.K9_COMPETENCIES},
    ]

    def _initialize_render_dispatch(self):
        self._RENDER_DISPATCH = {
            "header": self._handle_render_header,
            "simple": self._handle_render_simple,
            "experience": self._handle_render_experience,
            "experience_narrative": self._handle_render_experience_narrative,
            "education": self._handle_render_list,
            "certifications": self._handle_render_list,
            "competencies": self._handle_render_list,
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
            item_prefix = "* "
            if config["source"] == ResumeSection.K7_EDUCATION:
                return self._render_list_section(content, item_prefix="")
            elif config["source"] == ResumeSection.K8_CERTIFICATIONS:
                return self._render_list_section(content, item_prefix="* ")
            elif config["source"] == ResumeSection.K9_COMPETENCIES:
                return self._render_list_section(content, item_prefix="")
            else:
                return self._render_list_section(content, item_prefix=config.get("item_prefix", "* "))
        elif not content:
             self.logger.warning(f"Content for list section {config['source'].name} is missing or empty.")
             return ""
        else:
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
                else: text_to_render = item.get('text', str(item)).strip()

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
                cleaned = skill.strip(); wc = text_utils.count_words_ms_word_style(cleaned)
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



# ============================================================================
# WORKFLOWORCHESTRATOR CLASS
# ============================================================================

# ============================================================================
# STATE SERIALIZATION LAYER
# ============================================================================

class WorkflowOrchestrator:
    """
    Main workflow orchestrator with resumable state-driven architecture.
    Supports both new runs and resume runs with idempotent hop functions.
    """

    def __init__(
        self,
        config: AppConfig,
        master_resume: dict,
        run_id: Optional[str] = None,
        job_input: Optional[dict] = None
    ):
        self.config = config
        self.master_resume = master_resume
        
        # Initialize state
        self.hop_checkpoints = []
        self.hash_chain = []
        self.validation_results = []
        self.rendered_output = None
        
        if run_id:
            # --- RESUME RUN MODE ---
            self.run_id = run_id
            self.run_path = os.path.join("workflow_outputs", self.run_id)
            
            if not os.path.exists(self.run_path):
                raise FileNotFoundError(f"Cannot resume: Run directory not found for ID {self.run_id}")
            
            # Load manifest
            manifest_path = os.path.join(self.run_path, "run_manifest.json")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            self.job_input = manifest['job_input']
            self.hop_checkpoints = self._load_checkpoints_from_manifest(manifest)
            
            # Verify resume integrity
            current_resume_hash = self._hash_resume(master_resume)
            if manifest['master_resume_hash'] != current_resume_hash:
                raise ValueError(f"Master resume has changed since run {self.run_id} was initiated.")
                
        elif job_input:
            # --- NEW RUN MODE ---
            self.run_id = str(uuid.uuid4())[:8]
            self.run_path = os.path.join("workflow_outputs", self.run_id)
            os.makedirs(self.run_path, exist_ok=True)
            
            self.job_input = job_input
            
            # Create initial manifest
            manifest = {
                "run_id": self.run_id,
                "engine_version": __version__,
                "start_time_utc": datetime.utcnow().isoformat() + "Z",
                "job_input": self.job_input,
                "master_resume_hash": self._hash_resume(master_resume),
                "hop_checkpoints": []
            }
            self._save_manifest(manifest)
            
        else:
            raise ValueError("Must provide either 'run_id' to resume or 'job_input' to start a new run.")

        # Setup logging and state serializer
        self.logger, self.log_file_path = self._setup_logging()
        self.state_serializer = StateSerializer(self.run_path, self.run_id)
        self.manifest_manager = ManifestManager(self.run_path)
        self.constraints = config.content_constraints
        
        # Initialize JD enforcer
        self.jd_enforcer = JDEnforcementValidator(
            job_description=self.job_input.get('job_description', ''),
            logger=self.logger
        )
        
        # Initialize JD analyzer (create instance for testing/mocking)
        if GEMINI_AVAILABLE:
            self.jd_analyzer = self._create_jd_analyzer()
        else:
            self.jd_analyzer = None
        
        # Define hop execution order
        self.HOP_EXECUTION_ORDER = [
            (0, self._execute_hop_0_jd_analysis),
            (1, self._execute_hop_1_clerk_extraction),
            (2, self._execute_hop_2_enrichment),
            (3, self._execute_hop_3_artist_generation),
            (4, self._execute_hop_4_staging_and_sanitization),
            (5, self._execute_hop_5_validation),
            (6, self._execute_hop_6_gate_decision),
            (7, self._execute_hop_7_rendering),
            (8, self._execute_hop_8_qa_report)
        ]
        
        if not GEMINI_AVAILABLE:
            self.logger.error(
                "CRITICAL: Gemini API is not available!\n" +
                "="*80 + "\n" +
                "Either the google-generativeai package is not installed,\n" +
                "or GEMINI_API_KEY environment variable is not set.\n" +
                "Workflow will fail.\n" +
                "="*80
            )

    def execute_workflow(
        self,
        start_hop: int = 0,
        force_rerun_from_hop: Optional[int] = None
    ) -> Dict:
        """
        Execute the workflow with resumability support.
        """
        workflow_start = datetime.now()
        
        company_name = self.job_input.get('company_name', 'Target_Company')
        job_title = self.job_input.get('job_title', 'Target_Role')
        
        self.logger.info("=" * 80)
        self.logger.info(f"RESUME GENERATION ENGINE v{__version__} - RESUMABLE ARCHITECTURE")
        self.logger.info("=" * 80)
        self.logger.info(f"Run ID: {self.run_id}")
        self.logger.info(f"Company: {company_name}")
        self.logger.info(f"Position: {job_title}")
        self.logger.info(f"Started: {workflow_start.isoformat()}")
        self.logger.info("=" * 80)
        
        if force_rerun_from_hop is not None:
            self.logger.info(f"Forcing rerun from HOP-{force_rerun_from_hop}. Deleting downstream cache files...")
            self._delete_downstream_hop_files(force_rerun_from_hop)

        try:
            for hop_num, hop_function in self.HOP_EXECUTION_ORDER:
                if hop_num < start_hop:
                    self.logger.info(f"Skipping HOP-{hop_num} as requested by start_hop.")
                    continue
                
                hop_function()
            
            # Build success result
            workflow_end = datetime.now()
            
            file_paths = self.state_serializer.load(7)
            thematic_analysis = self.state_serializer.load(0)
            
            total_api_calls = sum(
                hc.metadata.get("gemini_api_calls", 0) 
                for hc in self.hop_checkpoints
            )
            
            coc_ledger = self._build_coc_ledger(
                workflow_start, workflow_end, thematic_analysis, total_api_calls
            )
            
            result = {
                "status": "SUCCESS",
                "run_id": self.run_id,
                "gate_decision": GateDecision.PROCEED.value,
                "file_paths": file_paths,
                "log_file_path": self.log_file_path,
                "coc_ledger": coc_ledger,
                "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints]
            }
            
            self.logger.info("=" * 80)
            self.logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            self.logger.info(f"Run ID: {self.run_id}")
            self.logger.info("=" * 80)
            
            return result
            
        except HopExecutionError as e:
            return self._handle_workflow_termination(str(e), workflow_start, "HOP_FAILURE")
        except Exception as e:
            return self._handle_workflow_termination(str(e), workflow_start, "UNCAUGHT_EXCEPTION")

    # ========================================================================
    # IDEMPOTENT HOP FUNCTIONS
    # ========================================================================

    def _execute_hop_0_jd_analysis(self) -> None:
        """HOP-0: Job Description Analysis (Idempotent)"""
        hop_id_num = 0
        hop_id_str = "HOP-0"
        hop_name = "JD Analysis"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            # Use the instance jd_analyzer (or create if not available)
            if self.jd_analyzer is None:
                jd_analyzer = self._create_jd_analyzer()
            else:
                jd_analyzer = self.jd_analyzer
                
            thematic_analysis, total_api_calls = jd_analyzer.analyze(
                self.job_input['job_description']
            )
            
            self.state_serializer.save(hop_id_num, thematic_analysis)
            
            self.logger.info(f"  Signal Quality Score: {thematic_analysis.signal_quality_score:.3f}")
            self.logger.info(f"  Retrieval Method: {thematic_analysis.retrieval_method}")
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=[],
                output_data=asdict(thematic_analysis),
                start_time=hop_start_time,
                metadata={"gemini_api_calls": total_api_calls}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_1_clerk_extraction(self) -> None:
        """HOP-1: Clerk Extraction (Idempotent)"""
        hop_id_num = 1
        hop_id_str = "HOP-1"
        hop_name = "Clerk Extraction"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            clerk = ClerkExtractor(self.master_resume)
            extracted_data, validation_results = clerk.extract()
            
            self.state_serializer.save(hop_id_num, extracted_data)
            
            bullets_extracted = sum(len(s.get('bullets', [])) for s in extracted_data.get('experience_sections', []))
            self.logger.info(f"  Bullets Extracted: {bullets_extracted}")
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=validation_results,
                output_data=extracted_data,
                start_time=hop_start_time,
                metadata={"bullets_extracted": bullets_extracted}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_2_enrichment(self) -> None:
        """HOP-2: Data Enrichment (Idempotent)"""
        hop_id_num = 2
        hop_id_str = "HOP-2"
        hop_name = "Data Enrichment"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            thematic_analysis = self.state_serializer.load(0)
            extracted_data = self.state_serializer.load(1)
            
            enricher = DataEnricher(self.config.enricher)
            enriched_scaffold, validation_results = enricher.enrich(
                extracted_data, thematic_analysis, self.config.enricher
            )
            
            self.state_serializer.save(hop_id_num, enriched_scaffold)
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=validation_results,
                output_data=enriched_scaffold,
                start_time=hop_start_time,
                metadata={}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_3_artist_generation(self) -> None:
        """HOP-3: Artist Generation (Idempotent)"""
        hop_id_num = 3
        hop_id_str = "HOP-3"
        hop_name = "Artist Generation"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            thematic_analysis = self.state_serializer.load(0)
            enriched_scaffold = self.state_serializer.load(2)
            
            artist = ArtistGenerator(
                master_resume=self.master_resume,
                enriched_scaffold=enriched_scaffold,
                job_description=self.job_input['job_description'],
                thematic_analysis=thematic_analysis,
                artist_specs=ARTIST_SPECS_DATA,
                artist_config=self.config.artist,
                content_constraints=self.config.content_constraints
            )
            
            artist_output, total_api_calls = artist.generate()
            
            self.state_serializer.save(hop_id_num, artist_output)
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=[],
                output_data=artist_output,
                start_time=hop_start_time,
                metadata={"gemini_api_calls": total_api_calls}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_4_staging_and_sanitization(self) -> None:
        """HOP-4: Staging and Sanitization (Idempotent)"""
        hop_id_num = 4
        hop_id_str = "HOP-4"
        hop_name = "Staging & Sanitization"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            artist_output = self.state_serializer.load(3)
            
            staging_buffer = ImmutableStagingBuffer()
            sanitizer = TextSanitizer()
            
            for section_key, section_data in artist_output.items():
                if isinstance(section_data, dict):
                    content = section_data.get('content', '')
                else:
                    content = str(section_data)
                
                sanitized_content = sanitizer.sanitize(content)
                staging_buffer.set(section_key, sanitized_content)
            
            staging_buffer.lock()
            
            self.state_serializer.save(hop_id_num, staging_buffer.data)
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=[],
                output_data={"sections_count": len(staging_buffer.data)},
                start_time=hop_start_time,
                metadata={"buffer_locked": True}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_5_validation(self) -> None:
        """HOP-5: Validation (Idempotent)"""
        hop_id_num = 5
        hop_id_str = "HOP-5"
        hop_name = "Validation"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            self.validation_results = self.state_serializer.load(hop_id_num)
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            staging_buffer_data = self.state_serializer.load(4)
            staging_buffer = ImmutableStagingBuffer()
            for k, v in staging_buffer_data.items():
                staging_buffer.set(k, v)
            staging_buffer.lock()
            
            thematic_analysis = self.state_serializer.load(0)
            
            # Run comprehensive validation
            validation_results = self._run_comprehensive_validation(
                staging_buffer, thematic_analysis
            )
            
            self.validation_results = validation_results
            self.state_serializer.save(hop_id_num, validation_results)
            
            failures = [vr for vr in validation_results if not vr.passed]
            self.logger.info(f"  Validation complete: {len(failures)} failures out of {len(validation_results)} rules")
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=validation_results,
                output_data={"validation_count": len(validation_results)},
                start_time=hop_start_time,
                metadata={}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_6_gate_decision(self) -> None:
        """HOP-6: Gate Decision (No file output)"""
        hop_id_str = "HOP-6"
        hop_name = "Gate Decision"
        
        self.logger.info(f"Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            validation_results = self.state_serializer.load(5)
            
            gate_engine = GateDecisionEngine(self.config.gate)
            decision, decision_data = gate_engine.evaluate(validation_results, self.logger)
            
            if decision == GateDecision.HALT:
                checkpoint = self._create_checkpoint(
                    hop_id_str, hop_name,
                    validation_results=validation_results,
                    output_data=decision_data,
                    start_time=hop_start_time,
                    metadata={"decision": decision.value}
                )
                checkpoint.status = HopStatus.FAIL
                self._save_checkpoint_to_manifest(checkpoint)
                self.hop_checkpoints.append(checkpoint)
                raise HopExecutionError(f"Gate decision: HALT. Reason: {decision_data.get('reason', 'Validation failures')}")
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=[],
                output_data=decision_data,
                start_time=hop_start_time,
                metadata={"decision": decision.value}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed. Decision: {decision.value}")

        except HopExecutionError:
            raise
        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_7_rendering(self) -> None:
        """HOP-7: Document Rendering (Idempotent)"""
        hop_id_num = 7
        hop_id_str = "HOP-7"
        hop_name = "Document Rendering"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            staging_buffer_data = self.state_serializer.load(4)
            staging_buffer = ImmutableStagingBuffer()
            for k, v in staging_buffer_data.items():
                staging_buffer.set(k, v)
            staging_buffer.lock()
            
            company_name = self.job_input.get('company_name', 'Target_Company')
            job_title = self.job_input.get('job_title', 'Target_Role')
            
            renderer = FileRenderer(self.master_resume, self.config.content_constraints)
            file_paths, file_contents = renderer.render_all_formats(
                staging_buffer, company_name, job_title, output_dir=self.run_path
            )
            
            self.rendered_output = {
                "file_paths": file_paths,
                "file_contents": file_contents
            }
            
            self.state_serializer.save(hop_id_num, file_paths)
            
            self.logger.info(f"  Files generated: {list(file_paths.keys())}")
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=[],
                output_data={"files_generated": list(file_paths.keys())},
                start_time=hop_start_time,
                metadata={"file_count": len(file_paths)}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    def _execute_hop_8_qa_report(self) -> None:
        """HOP-8: QA Report Generation (Idempotent)"""
        hop_id_num = 8
        hop_id_str = "HOP-8"
        hop_name = "QA Report"
        output_path = self.state_serializer.get_path_for_hop(hop_id_num)
        
        if os.path.exists(output_path):
            self.logger.info(f"Cache hit for {hop_id_str}. Skipping.")
            return

        self.logger.info(f"Cache miss. Executing {hop_id_str}...")
        hop_start_time = datetime.now()
        
        try:
            staging_buffer_data = self.state_serializer.load(4)
            thematic_analysis = self.state_serializer.load(0)
            validation_results = self.state_serializer.load(5)
            
            staging_buffer = ImmutableStagingBuffer()
            for k, v in staging_buffer_data.items():
                staging_buffer.set(k, v)
            staging_buffer.lock()
            
            file_contents = self.rendered_output.get('file_contents', {}) if self.rendered_output else {}
            
            qa_generator = QAReportGenerator(self)
            qa_results, qa_report_text = qa_generator.generate(
                staging_buffer, thematic_analysis, validation_results, file_contents
            )
            
            qa_output = {
                "qa_report_text": qa_report_text,
                "qa_validation_results": [asdict(vr) for vr in qa_results]
            }
            
            self.state_serializer.save(hop_id_num, qa_output)
            
            checkpoint = self._create_checkpoint(
                hop_id_str, hop_name,
                validation_results=qa_results,
                output_data={"report_length": len(qa_report_text)},
                start_time=hop_start_time,
                metadata={}
            )
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            
            self.logger.info(f"✓ {hop_id_str} completed and saved.")

        except Exception as e:
            checkpoint = self._create_failed_checkpoint(hop_id_str, hop_name, str(e), hop_start_time)
            self._save_checkpoint_to_manifest(checkpoint)
            self.hop_checkpoints.append(checkpoint)
            raise HopExecutionError(f"{hop_id_str} failed: {e}") from e

    # ========================================================================
    # HELPER METHODS (kept from original, some modified for resumability)
    # ========================================================================

    def _create_jd_analyzer(self):
        """Create JD analyzer instance."""
        from rag_RES import EnhancedJobDescriptionAnalyzer
        return EnhancedJobDescriptionAnalyzer(
            self.master_resume,
            enable_web_search=True,
            config=self.config.rag,
            web_rag_config=self.config.web_rag
        )

    def _run_comprehensive_validation(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis
    ) -> List[ValidationResult]:
        """Run comprehensive validation on staging buffer."""
        validation_results = []
        
        # Word count validation
        for section_key, content in staging_buffer.data.items():
            word_count = len(content.split())
            if word_count > 500:
                validation_results.append(ValidationResult(
                    rule_id=f"VAL_{section_key}_LENGTH",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Section {section_key} exceeds maximum length",
                    details={"word_count": word_count, "max": 500}
                ))
        
        return validation_results

    def _setup_logging(self) -> Tuple[logging.Logger, str]:
        """Setup logging for this workflow run."""
        log_file_path = os.path.join(self.run_path, f"{self.run_id}_workflow.log")
        logger, _ = setup_workflow_logging(log_file_path, test_mode=False)
        return logger, log_file_path

    def _hash_resume(self, resume: dict) -> str:
        """Generate hash of master resume for integrity checking."""
        resume_str = json.dumps(resume, sort_keys=True)
        return hashlib.sha256(resume_str.encode('utf-8')).hexdigest()

    def _save_manifest(self, manifest_data: dict):
        """Saves the run_manifest.json file."""
        manifest_path = os.path.join(self.run_path, "run_manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)

    def _load_checkpoints_from_manifest(self, manifest: dict) -> List[HopCheckpoint]:
        """Load checkpoints from manifest."""
        checkpoints = []
        for cp_dict in manifest.get('hop_checkpoints', []):
            cp_dict['status'] = HopStatus[cp_dict['status']]
            
            validation_results = []
            for vr_dict in cp_dict.get('validation_results', []):
                vr_dict['severity'] = ValidationSeverity[vr_dict['severity']]
                validation_results.append(ValidationResult(**vr_dict))
            cp_dict['validation_results'] = validation_results
            
            checkpoints.append(HopCheckpoint(**cp_dict))
        return checkpoints

    def _save_checkpoint_to_manifest(self, checkpoint: HopCheckpoint):
        """Appends a new checkpoint to the manifest file."""
        manifest_path = os.path.join(self.run_path, "run_manifest.json")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        checkpoint_dict = asdict(checkpoint)
        checkpoint_dict['status'] = checkpoint.status.value
        
        for vr_dict in checkpoint_dict.get('validation_results', []):
            if isinstance(vr_dict.get('severity'), Enum):
                vr_dict['severity'] = vr_dict['severity'].name
        
        manifest_data['hop_checkpoints'].append(checkpoint_dict)
        self._save_manifest(manifest_data)

    def _delete_downstream_hop_files(self, start_hop_num: int):
        """Deletes all hop output files from start_hop_num onwards."""
        for hop_num, _ in self.HOP_EXECUTION_ORDER:
            if hop_num >= start_hop_num:
                try:
                    file_path = self.state_serializer.get_path_for_hop(hop_num)
                    if os.path.exists(file_path):
                        self.logger.warning(f"Deleting cached file: {file_path}")
                        os.remove(file_path)
                except ValueError:
                    # Hop 6 has no file
                    continue

    def _create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        validation_results: List[ValidationResult],
        output_data: Any,
        start_time: datetime,
        metadata: Dict,
        error_message: Optional[str] = None
    ) -> HopCheckpoint:
        """Create a checkpoint for a hop."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        critical_failures = [vr for vr in validation_results if not vr.passed and vr.severity == ValidationSeverity.CRITICAL]
        high_failures = [vr for vr in validation_results if not vr.passed and vr.severity == ValidationSeverity.HIGH]
        
        if critical_failures or high_failures:
            status = HopStatus.FAIL
        elif any(not vr.passed for vr in validation_results):
            status = HopStatus.WARNING
        else:
            status = HopStatus.PASS
        
        if output_data:
            output_hash = hashlib.sha256(json.dumps(output_data, sort_keys=True).encode('utf-8')).hexdigest()[:16]
            self.hash_chain.append(output_hash)
        else:
            output_hash = None
        
        metadata['duration_seconds'] = duration
        
        return HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            status=status,
            timestamp_start=start_time.isoformat(),
            timestamp_end=end_time.isoformat(),
            output_hash=output_hash,
            validation_results=validation_results,
            metadata=metadata,
            error_message=error_message
        )

    def _create_failed_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        error_message: str,
        start_time: datetime
    ) -> HopCheckpoint:
        """Create a failed checkpoint."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            status=HopStatus.FAIL,
            timestamp_start=start_time.isoformat(),
            timestamp_end=end_time.isoformat(),
            output_hash=None,
            validation_results=[],
            metadata={"duration_seconds": duration},
            error_message=error_message
        )

    def _handle_workflow_termination(
        self,
        error_message: str,
        workflow_start: datetime,
        termination_type: str
    ) -> Dict:
        """Handle workflow termination/failure."""
        workflow_end = datetime.now()
        
        self.logger.error("=" * 80)
        self.logger.error(f"WORKFLOW TERMINATED: {termination_type}")
        self.logger.error(f"Error: {error_message}")
        self.logger.error("=" * 80)
        
        total_api_calls = sum(
            hc.metadata.get("gemini_api_calls", 0) 
            for hc in self.hop_checkpoints
        )
        
        thematic_analysis = None
        try:
            thematic_analysis = self.state_serializer.load(0)
        except:
            pass
        
        coc_ledger = self._build_coc_ledger(
            workflow_start, workflow_end, thematic_analysis, total_api_calls
        )
        
        return {
            "status": "FAILURE",
            "run_id": self.run_id,
            "gate_decision": GateDecision.HALT.value,
            "reason": error_message,
            "termination_type": termination_type,
            "log_file_path": self.log_file_path,
            "coc_ledger": coc_ledger,
            "hop_checkpoints": [asdict(hc) for hc in self.hop_checkpoints]
        }

    def _build_coc_ledger(
        self,
        workflow_start: datetime,
        workflow_end: datetime,
        thematic_analysis: Optional[ThematicAnalysis],
        total_api_calls: int
    ) -> Dict:
        """Build chain-of-custody ledger."""
        workflow_id = hashlib.sha256(
            f"{workflow_start.isoformat()}{self.master_resume.get('owner', {}).get('name', 'UnknownCandidate')}".encode('utf-8')
        ).hexdigest()[:16]

        rag_metadata = {}
        if thematic_analysis:
            comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
            comp_intel_dict = asdict(comp_intel) if comp_intel and hasattr(comp_intel, '__dataclass_fields__') else {}
            
            rag_metadata = {
                "signal_quality": getattr(thematic_analysis, 'signal_quality_score', 0.0),
                "retrieval_method": getattr(thematic_analysis, 'retrieval_method', 'UNKNOWN'),
                "primary_theme": getattr(getattr(thematic_analysis, 'primary_theme', {}), 'name', 'N/A'),
                "jd_input_hash": self.jd_enforcer.jd_hash if hasattr(self, 'jd_enforcer') else None,
            }

        overall_status = HopStatus.PASS.value
        if any(hc.status == HopStatus.FAIL for hc in self.hop_checkpoints):
            overall_status = HopStatus.FAIL.value
        elif any(hc.status == HopStatus.WARNING for hc in self.hop_checkpoints):
            overall_status = HopStatus.WARNING.value

        hops_executed_list = []
        for hc in self.hop_checkpoints:
            checkpoint_dict = asdict(hc)
            checkpoint_dict['status'] = hc.status.value
            for vr_dict in checkpoint_dict.get('validation_results', []):
                if isinstance(vr_dict.get('severity'), Enum):
                    vr_dict['severity'] = vr_dict['severity'].name
            hops_executed_list.append(checkpoint_dict)

        return {
            "workflow_id": workflow_id,
            "run_id": self.run_id,
            "engine_version": f"v{__version__}",
            "timestamp_start_utc": workflow_start.isoformat() + "Z",
            "timestamp_end_utc": workflow_end.isoformat() + "Z",
            "duration_seconds": round((workflow_end - workflow_start).total_seconds(), 3),
            "master_resume_version": self.master_resume.get("schema_version", "Unknown"),
            "hops_executed": hops_executed_list,
            "hash_chain_final": self.hash_chain[-1] if self.hash_chain else None,
            "rag_metadata": rag_metadata,
            "overall_status": overall_status,
            "total_gemini_api_calls": total_api_calls,
        }


# ============================================================================
# MODULE-LEVEL DATA LOADING
# ============================================================================

def load_master_resume() -> Dict:
    """Load master resume from JSON file."""
    paths_to_try = [
        "master_resume.json",
        "/mnt/user-data/uploads/master_resume.json",
        os.path.join(os.path.dirname(__file__), "master_resume.json")
    ]
    
    for path in paths_to_try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logging.info(f"✓ Loaded master_resume.json from: {path}")
                return data
        except FileNotFoundError:
            continue
        except Exception as e:
            logging.error(f"Error loading master_resume.json from {path}: {e}")
            continue
    
    logging.error("Failed to load master_resume.json from any location")
    return {}

# Load master resume data at module level
MASTER_RESUME_DATA = load_master_resume()