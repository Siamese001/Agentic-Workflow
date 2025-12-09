# File: workflow.py
# Main Workflow module for Resume Generation System
# Orchestrates all hops from job description parsing to final resume rendering

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import random
import shutil
import signal
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
import functools
from functools import partial
from enum import Enum, auto
from typing import (
    Any, Callable, ClassVar, Dict, List, 
    Optional, Set, Tuple, TypeVar, Union
)

from dataclasses import asdict, dataclass, field, is_dataclass

# Import all refactored modules
from config import (
    CONFIG, AppConfig, ReasoningConfig, ContentConstraintsConfig,
    FilePathsConfig, ArtistConfig, PROMPT_ADDENDUM_CONFIG, DEFAULT_GENERATION_TEMPERATURE
)
from models import *
from utils import *
import prompts
from validation import (
    ValidationEngine, JDEnforcementValidator, AppTrackerQAValidator,
    PreFlightValidator, ValidationContext, ConstraintFailureClassifier, ValidationRule
)
from rag import EnhancedJobDescriptionAnalyzer

# Import Gemini if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai package not installed. API calls will fail.")

logger = logging.getLogger(__name__)

# ==============================================================================
# MODULE-LEVEL CONSTANTS
# ==============================================================================

__version__ = "16.11"

# Mock data indicators (for validation)
mock_indicators = {
    "mock", "test", "dummy", "example", "sample",
    "[placeholder", "[your name]", "[company name]",
    "[missing_context]", "[unserializable"
}

# ==============================================================================
# GLOBAL DATA LOADS
# ==============================================================================

# Use the utility function from utils.py to load data
try:
    MASTER_RESUME_DATA = _load_json_data(CONFIG.paths.master_resume, "Master Resume data")
    HYPHENATION_RULES_DATA = _load_json_data(CONFIG.paths.hyphenation_rules, "Hyphenation Rules")
    APP_TRACKER_SCHEMA_DATA = _load_json_data(CONFIG.paths.app_tracker_schema, "App Tracker Schema")
    ARTIST_SPECS_DATA = _load_json_data(CONFIG.paths.artist_specs, "Artist Generation Specs")
except Exception as load_error:
    print(f"FATAL ERROR during data loading: {load_error}")
    logging.critical(f"FATAL ERROR during data loading: {load_error}", exc_info=True)
    exit(1)


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class HopExecutionError(Exception):
    """Raised when a hop fails to execute successfully."""
    pass

class StagingBufferError(Exception):
    """Raised when staging buffer encounters data integrity issues."""
    pass


# ==============================================================================
# HOP 1: CLERK EXTRACTOR
# (Corrected Logic)
# ==============================================================================

class ClerkExtractor:
    """
    Hop 1: Extracts and validates master resume data.
    
    Responsibilities:
    - Parse the master_resume.json
    - Build initial data structures for experience, education, etc.
    - Perform initial validation of master resume structure
    """

    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self._validate_master_resume_structure()

    def extract(self) -> Tuple[Dict, List[ValidationResult]]:
        """
        Extracts data from the master resume.
        
        Returns:
            Tuple of (extracted_data_dict, validation_results_list)
        """
        validation_results = []

        try:
            experience_sections = self._build_experience_sections()
            
            # Create a flat list of all bullets for enrichment/duplicate checking later
            all_bullets = []
            for section in experience_sections:
                all_bullets.extend([bullet['bullet_text'] for bullet in section.get('bullets', [])])
            bullet_dicts = [{'bullet_text': b} for b in all_bullets]

            extracted_data = {
                "experience_sections": experience_sections,
                "all_bullets_flat": bullet_dicts, # Added for easier processing in Hop 2
                "header": self.master_resume.get("owner", {}), # Changed from "header" to "owner" to match resume schema
                "education": self.master_resume.get("education", []),
                "certifications": self.master_resume.get("certifications_and_credentials", []),
                "competencies_raw": self.master_resume.get("strategic_and_technical_competencies", [])
            }

            return extracted_data, validation_results
        
        except Exception as e:
            logger.error(f"ClerkExtractor failed during data extraction: {e}", exc_info=True)
            raise HopExecutionError(f"ClerkExtractor failed: {e}")

    def _validate_master_resume_structure(self):
        """Validates the structure of the loaded master_resume.json."""
        required_keys = ["owner", "professional_experience", "education", "certifications_and_credentials", "strategic_and_technical_competencies"]
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")

        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            raise ValueError(f"MASTER_RESUME_JSON is missing required keys: {', '.join(missing_keys)}")
        logger.info("  ✓ Master resume structure validated.")

    def _build_experience_sections(self) -> List[Dict]:
        """Builds the experience sections from the master resume."""
        experience_sections = []

        for exp in self.master_resume.get("professional_experience", []):
            bullets = []
            # Use "bullet_pool" if it exists, otherwise "highlights"
            bullet_source = exp.get("bullet_pool", exp.get("highlights", []))

            for bullet_text in bullet_source:
                bullets.append({
                    "bullet_text": bullet_text,
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.Verbatim.value # Set initial provenance
                })

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""),
                "end_date": exp.get("dates", {}).get("end", ""),
                "overview": exp.get("overview", ""), # This field is likely empty, will be generated by Artist
                "bullets": bullets,
                "highlights_raw": [bullet['bullet_text'] for bullet in bullets] # Keep raw list for narratives
            })

        return experience_sections

# ==============================================================================
# HOP 2: DATA ENRICHER
# (Corrected Logic)
# ==============================================================================

class DuplicateDetector:
    """Detects duplicate content in resume bullets."""
    
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            logging.error("sklearn not available. DuplicateDetector functionality will be limited/disabled.")
            self.vectorizer = None
        else:
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
        if self.vectorizer is None:
            logging.warning("Skipping duplicate detection: sklearn/TfidfVectorizer not available.")
            return []
        
        duplicates = []
        bullet_texts = [b.get("bullet_text", "") for b in bullets]
        
        if not bullet_texts:
            return []

        try:
            tfidf_matrix = self.vectorizer.fit_transform(bullet_texts)
            cosine_sim_matrix = cosine_similarity(tfidf_matrix)
            
            for i in range(len(bullet_texts)):
                for j in range(i + 1, len(bullet_texts)):
                    similarity = cosine_sim_matrix[i, j]
                    if similarity >= threshold:
                        duplicates.append((i, j, similarity))
        except Exception as e:
            logging.error(f"Error during duplicate detection: {e}", exc_info=True)
            # Fallback to pairwise comparison if matrix fails
            for i in range(len(bullets)):
                for j in range(i + 1, len(bullets)):
                    similarity = text_utils.calculate_similarity(
                        bullets[i].get("bullet_text", ""),
                        bullets[j].get("bullet_text", "")
                    )
                    if similarity >= threshold:
                        duplicates.append((i, j, similarity))

        return duplicates

class DataEnricher:
    """
    Hop 2: Enriches extracted data with canonical verbs and duplicate detection.
    
    Responsibilities:
    - Find canonical verbs for each bullet
    - Detect duplicate bullets across the entire resume
    """

    def __init__(self, enricher_config: EnricherConfig):
        self.duplicate_detector = DuplicateDetector()
        self.CANONICAL_VERBS = enricher_config.canonical_verbs
        if not self.CANONICAL_VERBS:
            logging.warning("EnricherConfig.canonical_verbs is empty. Verb enrichment will be skipped.")

    def _canonicalize_verbs(self, text: str) -> List[str]:
        """Finds canonical verbs present in the text."""
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(
        self,
        extracted_data: Dict,
        thematic_analysis: "ThematicAnalysis"
    ) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        
        Returns: (enriched_data, validation_results)
        """
        validation_results = []

        # Enrich experience section bullets
        experience_sections = extracted_data.get("experience_sections", [])
        all_bullets_for_dup_check = []
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                canonical_verbs = self._canonicalize_verbs(bullet.get("bullet_text", ""))
                bullet["canonical_verbs"] = canonical_verbs
                all_bullets_for_dup_check.append(bullet)

        # Enrich competency bullets
        competency_bullets = []
        for competency_text in extracted_data.get("competencies_raw", []):
            competency_bullets.append({
                "bullet_text": competency_text,
                "canonical_verbs": self._canonicalize_verbs(competency_text),
                "provenance": BulletProvenance.Verbatim.value
            })
        
        # Add competencies to the data structure for the Artist
        extracted_data["competency_bullets"] = competency_bullets
        all_bullets_for_dup_check.extend(competency_bullets)

        # Run duplicate detection across *all* bullets
        duplicates = self.duplicate_detector.find_duplicates(all_bullets_for_dup_check)
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

        # The enriched_scaffold is just the modified extracted_data
        enriched_scaffold = extracted_data

        return enriched_scaffold, validation_results


# ==============================================================================
# HOP 3: ARTIST GENERATOR
# (Corrected Logic: Re-wired to use prompts.py)
# ==============================================================================

class ArtistGenerator:
    """
    Hop 3: Generates customized resume content using LLM.
    
    Responsibilities:
    - Generate headline, summary, experience bullets
    - Apply section-specific constraints
    - Iterate until quality standards met
    - Uses prompts from prompts.py module
    """

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
        """Converts string keys in config dicts to ResumeSection enums."""
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
        """Parses the loaded artist_specs.json into a usable dictionary."""
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

    # --- REMOVED `_build_generation_prompt_with_reinforced_constraints` ---
    # This logic is now in `prompts.build_generation_prompt_with_reinforced_constraints`

    def _mechanical_word_count_fix(
        self,
        text: str,
        min_wc: int,
        max_wc: int
    ) -> str:
        """
        Attempts mechanical word count fixes without LLM calls (zero cost).
        Part of HOP-3 enhancement - try mechanical repair before expensive LLM retry.
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
        prompt: str,
        constraints: Dict
    ) -> bool:
        """
        Tests if constraints are ACHIEVABLE at temp=1.0 before full generation.
        Quick check with minimal token output to validate constraint feasibility.
        Part of HOP-3 enhancement.
        """
        test_prompt = f"""Given these constraints:
{json.dumps(constraints, indent=2)}

And this task:
{prompt[:200]}...

Can you meet ALL constraints simultaneously at temperature=1.0?
Respond with ONLY:
- "YES" if achievable
- "NO: [specific constraint]" if impossible
"""
        
        try:
            response, _ = self._call_gemini_api(
                test_prompt,
                ReasoningConfig.DEFAULT,
                f"{section_enum.name}_ConstraintTest",
                "You are a constraint feasibility analyzer.",
                temperature_override=0.2
            )
            
            if not response.strip().startswith("YES"):
                logging.warning(
                    f"Constraint pre-flight FAILED for {section_enum.name}: "
                    f"{response}. Adjusting prompt..."
                )
                return False
            
            return True
        except Exception as e:
            logging.warning(f"Constraint pre-flight test failed with error: {e}")
            return True

    def _call_gemini_api(self, prompt: str, reasoning_config: ReasoningConfig, section_id: str, system_prompt: str, temperature_override: Optional[float] = None) -> Tuple[str, int]:
        """Internal method to call the Gemini API with reasoning and error handling."""
        calls_made_this_invocation = 0
        try:
            if not GEMINI_AVAILABLE:
                raise HopExecutionError(f"{section_id}: GEMINI API is not available.")

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise HopExecutionError(f"{section_id}: GEMINI_API_KEY not set.")

            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
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

            # Self-Consistency (SC) Flow
            if sc_count > 1:
                logging.info(f"  Running Self-Consistency for {section_id} ({sc_count} candidates)...")
                if temperature_override is None: generation_config.temperature = 0.9
                generation_config.candidate_count = sc_count
                candidate_responses = []
                try:
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)

                    if hasattr(response, 'candidates') and response.candidates:
                        for c in response.candidates:
                            candidate_finish_reason = getattr(c, 'finish_reason', None)
                            if candidate_finish_reason == 2: # MAX_TOKENS
                                logging.warning(f"    SC Candidate for {section_id} stopped: MAX_TOKENS.")
                                continue
                            elif candidate_finish_reason is not None and candidate_finish_reason != 1: # 1 == STOP
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
                
                # Call prompt builder for synthesis
                synthesis_prompt = prompts.build_sc_synthesis_prompt(prompt, candidate_responses)
                
                synthesis_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=generation_config.max_output_tokens)
                try:
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

            # Standard (non-SC) Flow
            else:
                try:
                    calls_made_this_invocation += 1
                    response = model.generate_content(f"{enhanced_system}\n\n{prompt}", generation_config=generation_config)

                    finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
                    if finish_reason == 2: # MAX_TOKENS
                        raise HopExecutionError(f"{section_id} generation stopped: MAX_TOKENS.")
                    elif finish_reason is not None and finish_reason != 1: # 1 == STOP
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
        """
        Main generation loop for selected sections.
        """
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
                message=f"Content generation attempted/completed for: {generated_keys_str}",
                details={}
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
        """Internal loop to generate content for each section."""
        output = {}
        total_api_calls = 0
        ordered_sections = sorted(self.SECTION_GENERATION_SPECS.keys(), key=lambda x: (int(x.name.split('_')[0][1:]), x.name))

        for section_enum in ordered_sections:
            if section_enum not in sections_to_generate:
                output[section_enum.value] = None # Ensure key exists as None if not generated
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
            
            # Handle non-LLM generation methods (copying, simple functions)
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

            # Handle LLM-based generation methods
            else:
                final_temp = temperature_overrides.get(section_enum)
                if final_temp is None:
                    logging.error(f"  {section_enum.name}: Temperature override NOT FOUND! Halting.")
                    raise HopExecutionError(f"Misconfiguration: Temperature override missing for {section_enum.name}")

                try:
                    method = getattr(self, generation_method_name)

                    # Build argument list for the specific generation method
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

    # --- Simple Generation Methods ---

    def _copy_k0_contact(self) -> str:
        """Copies and formats contact info from master resume."""
        contact = self.master_resume.get("owner", {}).get("contact", {})
        parts = [f"Phone: {contact.get('phone', '')}", f"Email: {contact.get('email', '')}", f"LinkedIn: {contact.get('linkedin', '')}"]
        return " | ".join(p for p in parts if len(p.split(': ', 1)) > 1 and p.split(': ', 1)[1])

    def _copy_from_master(self, master_data_key: str) -> Any:
        """Copies data directly from master resume using a dot-notation key."""
        try:
            keys = master_data_key.split('.')
            value = self.master_resume
            for key in keys: value = value[key]
            return value
        except (KeyError, TypeError) as e:
            logging.warning(f"Could not copy master data using key '{master_data_key}': {e}")
            return None
            
    def _generate_dummy_header(self) -> str: 
        """Returns a placeholder for headers that are rendered in file generation."""
        return "HEADER_PLACEHOLDER"

    # --- Context Builder Methods ---

    def _get_differentiators(self, max_count: Optional[int] = None) -> List[str]:
        """Helper to safely get differentiators from thematic analysis."""
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if not comp_intel: return []
        diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
        if not isinstance(diff_kw, list): return []
        return diff_kw[:max_count] if max_count else diff_kw

    def _get_problem_solution(self) -> Tuple[str, str]:
        """Helper to safely get problem/solution narratives."""
        narratives = getattr(self.thematic_analysis, 'problem_solution_narratives', None)
        if not isinstance(narratives, dict): narratives = {}
        problem = (narratives.get('common_problems', ['solving key challenges'])[0] 
                   if narratives.get('common_problems') else 'solving key challenges')
        solution = (narratives.get('solution_patterns', ['delivering impactful results'])[0] 
                    if narratives.get('solution_patterns') else 'delivering impactful results')
        return problem, solution

    def _get_primary_theme(self, default: str = 'key skills') -> str:
        """Helper to safely get the primary theme name."""
        return (self.thematic_analysis.primary_theme.get('name', default) 
                if self.thematic_analysis.primary_theme else default)

    def _build_context_k0_headline(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        """Builds context for K0_HEADLINE prompt."""
        return {
            "primary_theme": self._get_primary_theme('Key Expertise'),
            "differentiators_str": ', '.join(self._get_differentiators(5)),
            "min_wc": self.constraints.HEADLINE_WORD_COUNT_MIN,
            "max_wc": self.constraints.HEADLINE_WORD_COUNT_MAX,
            "comp_min_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MIN,
            "comp_max_wc": self.constraints.HEADLINE_COMPONENT_WORDS_MAX
        }

    def _build_context_k1_summary(self, spec: Dict, section_enum: Optional[ResumeSection] = None) -> Dict:
        """Builds context for K1_EXECUTIVE_SUMMARY prompt."""
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
        """Builds context for K4, K5, K6 narrative prompts."""
        extra_args = spec.get("extra_args", {})
        if not isinstance(extra_args, dict):
            raise HopExecutionError(f"Invalid 'extra_args' format in spec for narrative generation.")

        company_match = extra_args.get("company_match")
        if not company_match:
            raise HopExecutionError(f"Missing 'company_match' in extra_args for narrative generation.")

        if section_enum is None or section_enum not in self.NARRATIVE_CONFIG:
            raise HopExecutionError(f"Missing/invalid config for narrative generation: {section_enum}")

        title = "Default Title"
        # Find the matching experience section from the *enriched scaffold*
        exp_section = next((exp for exp in self.enriched_scaffold.get('experience_sections', []) 
                           if company_match in exp.get('company', '')), None)
        master_highlights = []
        if exp_section:
            master_highlights = exp_section.get('highlights_raw', [])
            title = exp_section.get("title", title)

        if not master_highlights: 
            raise HopExecutionError(f"Cannot generate narrative for {company_match}: Master highlights/bullets not found or empty in scaffold.")
        
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
        """Builds context for K10_SKILLS prompt."""
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
        """Builds context for K11_COVER_LETTER prompt."""
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

    # --- Post-Processor Methods ---

    def _post_process_k10_skills(self, skills_text: str, section_enum: ResumeSection) -> List[str]:
        """Post-processes the raw text output for K10_SKILLS."""
        try:
            skills_list_final = []
            # Split by newline, remove bullet points and strip whitespace
            skills_intermediate = [re.sub(r'^[•*\-\d\.]+\s*', '', s).strip() for s in skills_text.split('\n') if s.strip()]
            malformed_count = 0
            for skill in skills_intermediate:
                word_count = text_utils.count_words_ms_word_style(skill)
                # Enforce that skills are concise (1-3 words)
                if 1 <= word_count <= 3:
                    skills_list_final.append(skill)
                else:
                    logging.warning(f"{section_enum.value}: Discarding malformed skill '{skill}' (words: {word_count})")
                    malformed_count += 1

            if len(skills_list_final) != 12: # Check against hardcoded constraint from prompt
                raise HopExecutionError(f"{section_enum.value} generation failed: Expected 12 valid skills, found {len(skills_list_final)}. Preview: {skills_text[:100]}...")
            if malformed_count > 0:
                 logging.warning(f"{section_enum.value}: Discarded {malformed_count} malformed skills.")

            return skills_list_final

        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_k11_cover_letter(self, cover_letter_text: str, section_enum: ResumeSection) -> str:
        """Post-processes and validates the structure of the K11_COVER_LETTER."""
        try:
            expected_signature = self._get_expected_signature()
            fixed_text = cover_letter_text.strip(); current_date_str = datetime.now().strftime("%B %d, %Y")
            
            # 1. Add Date if missing
            if not re.match(r"\w+ \d{1,2}, \d{4}", fixed_text): 
                fixed_text = f"{current_date_str}\n\n{fixed_text}"; 
                logging.warning(f"{section_enum.value}: Added missing date.")
            
            # 2. Add Recipient block if missing
            recipient_placeholder = "Hiring Manager\n[Company Name]"
            if recipient_placeholder not in fixed_text:
                fixed_text = re.sub(r"^(\w+ \d{1,2}, \d{4}\s*)", rf"\1\n{recipient_placeholder}\n", fixed_text, count=1, flags=re.MULTILINE)
                if recipient_placeholder not in fixed_text:
                     logging.warning(f"{section_enum.value}: Failed to add recipient placeholder.")

            # 3. Add Salutation if missing
            salutation = "Dear Hiring Manager,"
            if salutation not in fixed_text:
                fixed_text = re.sub(rf"({re.escape(recipient_placeholder)}\s*)", rf"\1\n{salutation}\n", fixed_text, count=1, flags=re.MULTILINE)
                if salutation not in fixed_text:
                     logging.warning(f"{section_enum.value}: Failed to add salutation.")

            # 4. Fix/Add Closing and Signature
            closing = "Sincerely,"
            if expected_signature in fixed_text and closing not in fixed_text.split(expected_signature)[0]:
                # Signature is present but closing is missing
                fixed_text = fixed_text.replace(expected_signature, f"\n\n{closing}\n\n{expected_signature}")
            elif closing in fixed_text and expected_signature not in fixed_text:
                 # Closing is present but signature is missing
                 fixed_text = fixed_text.rstrip() + f"\n\n{expected_signature}"
            elif closing not in fixed_text and expected_signature not in fixed_text:
                 # Both are missing
                 fixed_text = fixed_text.rstrip() + f"\n\n{closing}\n\n{expected_signature}"
            elif not fixed_text.rstrip().endswith(expected_signature.rstrip()):
                 # Something is wrong at the end, replace it all
                 logging.warning(f"{section_enum.value}: Signature block missing/malformed at end. Attempting fix...")
                 fixed_text = re.sub(r'\n*Sincerely,?[\s\S]*$', '', fixed_text.rstrip(), flags=re.MULTILINE)
                 fixed_text += f"\n\n{closing}\n\n{expected_signature}"

            if "[Placeholder" in fixed_text or "[Your Name]" in fixed_text: 
                raise HopExecutionError(f"{section_enum.value} generation failed (placeholder detected).")
            if not all(x in fixed_text for x in [current_date_str, recipient_placeholder, salutation, closing, expected_signature]): 
                logging.warning(f"{section_enum.value}: Structure may still be incomplete after fixes.")

            return fixed_text.strip()
        except HopExecutionError as he: raise he
        except Exception as e:
            logging.error(f"{section_enum.value} post-processing failed: {e}", exc_info=True)
            raise HopExecutionError(f"{section_enum.value} post-processing failed: {e}") from e

    def _post_process_narrative(self, narrative_text: str, section_enum: ResumeSection) -> str:
        """Post-processes and validates generated narratives (K4, K5, K6)."""
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

    # --- Generation Helper Methods ---

    def _get_reasoning_config_for_section(self, section_enum: ResumeSection) -> ReasoningConfig:
        """Finds the specific ReasoningConfig for a given section."""
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
        """Gets the word count range for an experience overview section."""
        if section_enum == ResumeSection.K2_UNIFY_OVERVIEW:
             return (self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX)
        elif section_enum == ResumeSection.K3_IBM_OVERVIEW:
             return (self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX)
        else:
             logging.warning(f"No overview WC range explicitly defined for {section_enum.name}. Using default (25-40).")
             return (25, 40)

    def _get_expected_signature(self) -> str:
        """Formats the cover letter signature from master resume data."""
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        
        # Define the template locally as it's only used here
        COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}""" # Added two spaces at the end of each line to force Markdown line breaks

        try:
            return COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except KeyError as e: 
            raise HopExecutionError(f"Missing key in COVER_LETTER_SIGNATURE_TEMPLATE format: {e}")

    def _get_experience_snippets_for_cl(self) -> str:
        """Gathers snippets of experience for the cover letter context."""
        exp_snippets = ""
        # Note: This relies on the enriched_scaffold, not the final artist_output.
        # This is a potential dependency issue if CL is generated before overviews/bullets.
        # However, K11 is last, so this *should* be fine.
        
        # Get K2 (Unify) data
        unify_overview = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_OVERVIEW.value, "")
        unify_bullets_raw = self.enriched_scaffold.get(ResumeSection.K2_UNIFY_BULLETS.value, [])
        if not unify_bullets_raw: # Fallback to scaffold
             unify_exp = next((e for e in self.enriched_scaffold.get('experience_sections', []) if "Unify" in e.get("company","")), None)
             if unify_exp: unify_bullets_raw = unify_exp.get('bullets', [])

        # Get K3 (IBM) data
        ibm_overview = self.enriched_scaffold.get(ResumeSection.K3_IBM_OVERVIEW.value, "")
        ibm_bullets_raw = self.enriched_scaffold.get(ResumeSection.K3_IBM_BULLETS.value, [])
        if not ibm_bullets_raw: # Fallback to scaffold
             ibm_exp = next((e for e in self.enriched_scaffold.get('experience_sections', []) if "IBM" in e.get("company","")), None)
             if ibm_exp: ibm_bullets_raw = ibm_exp.get('bullets', [])

        if unify_overview or unify_bullets_raw:
             exp_snippets += f"Recent Experience (Unify):\n{unify_overview or '(Overview not available)'}\n"
             unify_bullet_texts = [b.get('text', b.get('bullet_text', '')) for b in unify_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in unify_bullet_texts[:2] if text]) + "\n"
        if ibm_overview or ibm_bullets_raw:
             exp_snippets += f"Prior Experience (IBM):\n{ibm_overview or '(Overview not available)'}\n"
             ibm_bullet_texts = [b.get('text', b.get('bullet_text', '')) for b in ibm_bullets_raw if isinstance(b, dict)]
             exp_snippets += "\n".join([f"- {text}" for text in ibm_bullet_texts[:2] if text]) + "\n"

        return exp_snippets if exp_snippets.strip() else "Candidate has extensive experience in relevant areas.\n"

    # --- Core Generation Methods (Re-wired) ---

    def _generate_section_generic(self, spec: Dict, section_enum: ResumeSection, temperature_override: Optional[float]) -> Tuple[Any, int]:
        """Generic method to build context, format prompt, call LLM, and post-process."""
        context = {}
        if "context_builder" in spec and spec["context_builder"]:
            builder_method_name = spec["context_builder"]
            builder_method = getattr(self, builder_method_name, None)
            if builder_method:
                 context = builder_method(spec, section_enum=section_enum)
            else:
                 raise HopExecutionError(f"Context builder method '{builder_method_name}' not found for {section_enum.name}")

        # --- RE-WIRING ---
        # Get the template key from the spec
        prompt_template_key = spec.get("prompt_template_key")
        if not prompt_template_key: 
            raise HopExecutionError(f"Prompt template key missing in spec for {section_enum.name}")
        
        # Get the template string from the prompts module
        try:
            prompt_template = getattr(prompts, prompt_template_key)
        except AttributeError:
            raise HopExecutionError(f"Prompt template '{prompt_template_key}' not found in prompts.py for {section_enum.name}")
        # --- END RE-WIRING ---

        try: 
            prompt = prompt_template.format_map(defaultdict(lambda: '[MISSING_CONTEXT]', **context))
        except KeyError as ke: 
            raise HopExecutionError(f"Missing key '{ke}' in context for {section_enum.name} prompt.")
        except Exception as fmt_e: 
            raise HopExecutionError(f"Error formatting prompt for {section_enum.name}: {fmt_e}")

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

    # --- REMOVED `_rewrite_bullet_for_word_count` ---
    # Logic is now in `prompts.build_bullet_rewrite_prompt` and helper `_call_rewrite_bullet`

    def _call_rewrite_bullet(self, original_bullet_text: str, target_word_count_range: Tuple[int, int], section_id_str: str, temperature_override: Optional[float] = None, max_retries: int = 5) -> Tuple[str, int]:
        """Internal helper to manage the retry loop for bullet rewriting."""
        total_calls = 0
        min_wc, max_wc = target_word_count_range
        
        if temperature_override is not None:
            temperature_schedule = [temperature_override, 0.8, 0.6, 0.4, 0.2]
        else:
            temperature_schedule = [1.0, 0.8, 0.6, 0.4, 0.2]
        
        last_rewritten_text = None
        last_word_count = None
        
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
                # --- RE-WIRING ---
                # Call the prompt builder from prompts.py
                base_prompt = prompts.build_bullet_rewrite_prompt(
                    original_bullet_text=original_bullet_text,
                    target_word_count_range=target_word_count_range
                )
                
                # Call the constraint reinforcer from prompts.py
                enhanced_prompt = prompts.build_generation_prompt_with_reinforced_constraints(
                    base_prompt=base_prompt,
                    constraints={'min_wc': min_wc, 'max_wc': max_wc},
                    attempt_number=attempt + 1
                )
                # --- END RE-WIRING ---
                
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
                            f"{'Retrying with stronger constraints and lower temp...' if attempt < max_retries - 1 else 'No more retries.'}"
                        )
                        
                        if attempt == max_retries - 1:
                            raise HopExecutionError(
                                f"{section_id_str}_RewriteWC failed after {max_retries} attempts. "
                                f"Final word count: {rewritten_wc}, target: {min_wc}-{max_wc}. "
                                f"Temperature schedule used: {temperature_schedule[:max_retries]}. "
                                f"Total API calls: {total_calls}"
                            )
                
                except HopExecutionError:
                    raise
                except Exception as e:
                    logging.error(f"  Unexpected error during WC rewrite attempt {attempt + 1} for {section_id_str}: {e}")
                    if attempt == max_retries - 1:
                        raise HopExecutionError(
                            f"{section_id_str}_RewriteWC failed unexpectedly after {max_retries} attempts: {e}"
                        ) from e
            
            except HopExecutionError as he:
                if attempt == max_retries - 1:
                    raise he
        
        raise HopExecutionError(
            f"{section_id_str}_RewriteWC exhausted all {max_retries} attempts without success"
        )


    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id_str: str) -> List[Dict]:
        """Validates that the LLM returned real, unmodified, unique bullets from the master list."""
        if len(selected_bullets_text) != expected_count: 
            raise HopExecutionError(f"{section_id_str} LLM returned {len(selected_bullets_text)} bullets, expected {expected_count}.")
        
        validated_bullets = []
        master_texts_map = {b['bullet_text'].strip(): b for b in master_bullets_structured if 'bullet_text' in b and isinstance(b['bullet_text'], str)}
        returned_texts_set = set()
        
        for selected_text in selected_bullets_text:
            cleaned_text = selected_text.strip()
            matched_bullet = master_texts_map.get(cleaned_text) or master_texts_map.get(cleaned_text.rstrip('.'))
            
            if matched_bullet:
                original_text = matched_bullet['bullet_text'].strip()
                if original_text in returned_texts_set: 
                    raise HopExecutionError(f"{section_id_str} LLM returned duplicate bullet: '{original_text[:50]}...'")
                validated_bullets.append(matched_bullet)
                returned_texts_set.add(original_text)
            else:
                nearby_keys = [k[:50] for k in master_texts_map.keys() if k.startswith(cleaned_text[:10])]
                raise HopExecutionError(f"{section_id_str} LLM returned bullet not found/modified: '{cleaned_text[:50]}...'. Nearby: {nearby_keys}")
        
        if len(validated_bullets) != expected_count: 
            raise HopExecutionError(f"{section_id_str} failed validation: Expected {expected_count}, validated {len(validated_bullets)}.")
        
        logging.info(f"  ✓ {section_id_str}: Validated {len(validated_bullets)} verbatim bullets.")
        return validated_bullets

    def _validate_and_potentially_rewrite_bullets(self, selected_bullets_structured: List[Dict], min_target: int, max_target: int, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        """Iterates through bullets, checks WC, and calls the rewrite helper if needed."""
        final_bullets = []
        total_rewrite_calls = 0
        logging.info(f"  Validating word count for {section_id_str} ({min_target}-{max_target})")
        
        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict): 
                raise HopExecutionError(f"Invalid item in bullet list for {section_id_str}[{i}]")
            
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
            original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            word_count = bullet_data.get('word_count', text_utils.count_words_ms_word_style(original_text))
            
            if not original_text: 
                raise HopExecutionError(f"Empty bullet in {section_id_str}[{i}].")

            if not (min_target <= word_count <= max_target):
                logging.warning(
                    f"  WC Check FAIL for {section_id_str}[{i}]: Count={word_count} (Target: {min_target}-{max_target}). "
                    f"Attempting rewrite with enhanced temperature-based retry (temps: 1.0→0.8→0.6→0.4→0.2) for bullet: '{original_text[:50]}...'"
                )
                try:
                    # Call the dedicated rewrite helper
                    rewritten_text, rewrite_calls = self._call_rewrite_bullet(
                        original_text, (min_target, max_target), f"{section_id_str}_RewriteWC_{i}", 
                        temperature_override, max_retries=5
                    )
                    total_rewrite_calls += rewrite_calls
                    rewritten_word_count = text_utils.count_words_ms_word_style(rewritten_text)
                    
                    logging.info(
                        f"    Rewrite SUCCESS for {section_id_str}[{i}]. "
                        f"Old count: {word_count}, New count: {rewritten_word_count}, "
                        f"API calls: {rewrite_calls}"
                    )
                    
                    new_provenance = BulletProvenance.Customized.value if original_provenance == BulletProvenance.Verbatim.value else original_provenance
                    final_bullets.append({
                        "text": rewritten_text, 
                        "provenance": new_provenance, 
                        "word_count": rewritten_word_count, 
                        "original_text_if_rewritten": original_text
                    })
                except HopExecutionError as rewrite_he:
                    logging.error(f"    Rewrite FAILED for {section_id_str}[{i}]: {rewrite_he}")
                    raise HopExecutionError(f"Bullet WC correction failed for {section_id_str}[{i}]") from rewrite_he
                except Exception as e:
                    logging.error(f"Unexpected error during WC correction for {section_id_str}[{i}]: {e}", exc_info=True)
                    raise HopExecutionError(f"Unexpected error during bullet WC correction for {section_id_str}[{i}]") from e
            else:
                final_bullets.append({
                    "text": original_text, 
                    "provenance": original_provenance, 
                    "word_count": word_count
                })
        
        logging.info(f"  ✓ Word count validation/rewrite complete for {section_id_str}. Rewrite API Calls: {total_rewrite_calls}")
        return final_bullets, total_rewrite_calls

    def _generate_lightly_customized_bullets(self, source_bullets_text: List[str], section_id_str: str, thematic_analysis: ThematicAnalysis, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        """Calls the LLM to lightly customize a list of bullets."""
        total_calls = 0
        try:
            if not source_bullets_text: 
                return [], 0
            
            # --- RE-WIRING ---
            # Call the prompt builder from prompts.py
            prompt = prompts.build_customized_bullet_prompt(
                source_bullets_text=source_bullets_text,
                thematic_analysis=thematic_analysis
            )
            # --- END RE-WIRING ---

            try: 
                reasoning_config = ReasoningConfig.DEFAULT
            except AttributeError: 
                logging.warning("ReasoningConfig.DEFAULT missing. Creating default.")
                reasoning_config = ReasoningConfig()

            system_prompt = "You are an expert resume editor subtly tailoring bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            
            rewritten_bullets_text = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]
            if len(rewritten_bullets_text) != len(source_bullets_text): 
                raise HopExecutionError(f"{section_id_str} LLM returned {len(rewritten_bullets_text)} customized bullets, expected {len(source_bullets_text)}.")
            
            result_list = [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in rewritten_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: 
            raise he
        except Exception as e: 
            raise HopExecutionError(f"{section_id_str} customization failed: {e}") from e

    def _generate_synthetic_bullets(self, count: int, company_name: str, job_description: str, thematic_analysis: ThematicAnalysis, context_bullets: str, reasoning_config: ReasoningConfig, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        """Calls the LLM to generate new, synthetic bullets."""
        total_calls = 0
        try:
            if count <= 0: 
                return [], 0
            
            # --- RE-WIRING ---
            # Call the prompt builder from prompts.py
            prompt = prompts.build_synthetic_bullet_prompt(
                count=count,
                company_name=company_name,
                job_description=job_description,
                thematic_analysis=thematic_analysis,
                context_bullets=context_bullets
            )
            # --- END RE-WIRING ---

            system_prompt = "You generate plausible, impactful, synthetic resume bullets..."
            response_text, call_count = self._call_gemini_api(prompt, reasoning_config, section_id_str, system_prompt, temperature_override=temperature_override)
            total_calls += call_count
            
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]
            if len(synthetic_bullets_text) != count: 
                raise HopExecutionError(f"{section_id_str} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}).")
            
            result_list = [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in synthetic_bullets_text]
            return result_list, total_calls
        except HopExecutionError as he: 
            raise he
        except Exception as e: 
            raise HopExecutionError(f"{section_id_str} synthetic generation failed: {e}") from e

    # --- REMOVED `_generate_tailored_overview_for_experience` ---
    # Logic is now in `prompts.build_overview_prompt` and called via `_call_generate_overview`

    def _call_generate_overview(
        self,
        generated_bullets: List[Dict],
        word_count_range: Tuple[int, int],
        reasoning_config: ReasoningConfig,
        section_enum: ResumeSection, 
        temperature_override: Optional[float] = None, **kwargs
    ) -> Tuple[str, int]:
        """Internal helper to manage the call for overview generation."""
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
             if not text: 
                 logging.warning(f"Skipping empty/invalid bullet {i} for overview {section_id}"); 
                 continue
             bullet_texts.append(f"* {text.strip()}")
        
        if not bullet_texts: 
            raise HopExecutionError(f"Cannot generate overview for {section_id}: All bullets invalid.")

        bullet_summary_input = "\n".join(bullet_texts)
        min_wc, max_wc = word_count_range

        # --- RE-WIRING ---
        # Call the prompt builder from prompts.py
        prompt = prompts.build_overview_prompt(
            bullet_summary_input=bullet_summary_input,
            word_count_range=word_count_range,
            thematic_analysis=self.thematic_analysis,
            job_description=self.job_description
        )
        # --- END RE-WIRING ---

        system_prompt = "You are an expert resume editor specializing in summarizing experience sections while incorporating key executive themes."
        synthesized_overview, call_count = self._call_gemini_api(
            prompt, reasoning_config, section_id, system_prompt,
            temperature_override=temperature_override
        )

        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview or "KEY THEMES" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")
        
        final_wc = text_utils.count_words_ms_word_style(synthesized_overview); 
        final_sc = text_utils.count_sentences(synthesized_overview)
        if not (min_wc <= final_wc <= max_wc): 
            logging.warning(f"{section_id} overview WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if not (1 <= final_sc <= 2): 
            logging.warning(f"{section_id} overview SC ({final_sc}) outside target (1-2).")
        
        return synthesized_overview, call_count

    def _generate_tailored_bullets_for_experience(
            self,
            company_name: str,
            provenance_targets: Dict[str, int], 
            reasoning_config: ReasoningConfig, 
            section_enum: ResumeSection,
            temperature_override: Optional[float] = None, 
            is_competencies: bool = False, **kwargs
    ) -> Tuple[List[Dict], int]:
        """
        Core logic to generate a set of bullets (Verbatim, Customized, Synthetic)
        for an experience section or competencies.
        """
        section_id_str = section_enum.value
        logging.info(f"  Generating bullets for {section_enum.name} ({section_id_str}) (Targets: {provenance_targets})")
        total_calls_for_section = 0
        final_bullets = []

        # 1. Get Master Bullets from the scaffold
        master_bullets_structured = []
        if is_competencies:
             master_bullets_structured = self.enriched_scaffold.get("competency_bullets", [])
        else:
             exp_section = next((exp for exp in self.enriched_scaffold.get('experience_sections', []) if company_name in exp.get('company', '')), None)
             if not exp_section: 
                 raise HopExecutionError(f"Master data not found for '{company_name}' in enriched scaffold, needed by {section_enum.name}")
             master_bullets_structured = exp_section.get("bullets", [])

        if not master_bullets_structured:
             logging.warning(f"No master bullets found in scaffold for {section_enum.name}. Only synthetic bullets can be generated.")

        verbatim_count = provenance_targets.get('Verbatim', 0)
        customized_count = provenance_targets.get('Customized', 0)
        synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        
        if not master_bullets_structured and (verbatim_count > 0 or customized_count > 0): 
            raise HopExecutionError(f"{section_enum.name} Cannot select/customize: No valid master items found.")

        # 2. Select Verbatim Bullets
        verbatim_bullets_selected = []
        if verbatim_count > 0:
            logging.info(f"    Selecting {verbatim_count} Verbatim items...")
            if len(master_bullets_structured) < verbatim_count: 
                raise HopExecutionError(f"{section_enum.name} Cannot select {verbatim_count} Verbatim (only {len(master_bullets_structured)} available).")
            
            master_bullets_text_list = [b['bullet_text'] for b in master_bullets_structured]
            
            # --- RE-WIRING ---
            prompt_select = prompts.build_verbatim_bullet_selection_prompt(
                master_bullets_text_list=master_bullets_text_list,
                verbatim_count=verbatim_count,
                thematic_analysis=self.thematic_analysis
            )
            # --- END RE-WIRING ---

            system_prompt_select="You are an AI assistant that selects relevant resume bullet points based on keywords, outputting them verbatim."
            try:
                default_reasoning = ReasoningConfig.DEFAULT
                response_select, calls_v_select = self._call_gemini_api(
                    prompt_select, default_reasoning, f"{section_id_str}_SelectV", 
                    system_prompt_select, temperature_override=temperature_override
                )
                total_calls_for_section += calls_v_select
                selected_texts = [line.strip().lstrip('- ') for line in response_select.split('\n') if line.strip()]
                
                verbatim_bullets_selected = self._validate_llm_bullet_selection(
                    selected_texts, master_bullets_structured, verbatim_count, f"{section_id_str}_SelectV"
                )
                final_bullets.extend(verbatim_bullets_selected)
            except HopExecutionError as he: 
                raise he
            except Exception as e: 
                raise HopExecutionError(f"{section_enum.name} Verbatim selection failed unexpectedly: {e}") from e

        # 3. Select and Customize Bullets
        if customized_count > 0:
            logging.info(f"    Customizing {customized_count} items...")
            used_verbatim_texts = {b['bullet_text'] for b in verbatim_bullets_selected}
            available_for_custom = [b for b in master_bullets_structured if b['bullet_text'] not in used_verbatim_texts]
            
            if len(available_for_custom) < customized_count: 
                raise HopExecutionError(f"{section_enum.name} Cannot customize {customized_count}: Not enough unique items remaining ({len(available_for_custom)}).")
            
            random.shuffle(available_for_custom)
            candidates_for_custom = available_for_custom[:customized_count]
            source_texts_for_custom = [b['bullet_text'] for b in candidates_for_custom]
            
            try:
                customized_bullets, calls_c = self._generate_lightly_customized_bullets(
                    source_texts_for_custom, f"{section_id_str}_CustomC", self.thematic_analysis, temperature_override
                )
                total_calls_for_section += calls_c
                final_bullets.extend(customized_bullets)
            except HopExecutionError as he: 
                raise he
            except Exception as e: 
                raise HopExecutionError(f"{section_enum.name} Customization failed unexpectedly: {e}") from e

        # 4. Generate Synthetic Bullets
        if synthetic_count > 0:
            logging.info(f"    Generating {synthetic_count} Synthetic items...")
            context_bullets_text = '\n'.join([f"- {b.get('text', '')}" for b in final_bullets if isinstance(b, dict) and b.get('text')])
            try:
                synthetic_bullets, calls_s = self._generate_synthetic_bullets(
                    synthetic_count, company_name if not is_competencies else "Competencies", 
                    self.job_description, self.thematic_analysis, context_bullets_text, 
                    reasoning_config, f"{section_id_str}_SynthS", temperature_override
                )
                total_calls_for_section += calls_s
                final_bullets.extend(synthetic_bullets)
            except HopExecutionError as he: 
                raise he
            except Exception as e: 
                raise HopExecutionError(f"{section_enum.name} Synthetic generation failed unexpectedly: {e}") from e

        if len(final_bullets) != total_expected_count: 
            raise HopExecutionError(f"{section_enum.name} Internal Error: Generated {len(final_bullets)}, expected {total_expected_count}.")

        # 5. Validate Word Counts for all generated bullets
        target_range = self.BULLET_WORD_COUNT_RANGES.get(section_enum)
        if target_range is None: 
            raise HopExecutionError(f"Config Error: WC range not found for {section_enum.name}.")
        
        min_target, max_target = target_range
        logging.info(f"    Validating word counts ({min_target}-{max_target})...")
        try:
            final_bullets_validated, calls_rewrite = self._validate_and_potentially_rewrite_bullets(
                final_bullets, min_target, max_target, section_id_str, temperature_override
            )
            total_calls_for_section += calls_rewrite
            final_bullets = final_bullets_validated
        except HopExecutionError as he: 
            raise he
        except Exception as e: 
            raise HopExecutionError(f"{section_enum.name} Word count validation/rewrite failed unexpectedly: {e}") from e

        # 6. Reorder bullets (except for competencies)
        if section_enum != ResumeSection.K9_COMPETENCIES:
            logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
            current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets) if isinstance(bullet, dict)]
            current_bullets_text_input = '\n'.join(current_bullets_text_list)
            
            # --- RE-WIRING ---
            prompt_reorder = prompts.build_bullet_reorder_prompt(
                company_name=company_name,
                current_bullets_text_input=current_bullets_text_input,
                thematic_analysis=self.thematic_analysis,
                bullet_count=len(final_bullets)
            )
            # --- END RE-WIRING ---

            system_prompt_reorder = "You are an expert resume editor who reorders bullet points for maximum impact based on relevance to target keywords."
            try:
                default_reasoning = ReasoningConfig.DEFAULT
                response_reorder, calls_reorder = self._call_gemini_api(
                    prompt_reorder, default_reasoning, f"{section_id_str}_Reorder", 
                    system_prompt_reorder, temperature_override=temperature_override
                )
                total_calls_for_section += calls_reorder
                reordered_texts_raw = [line.strip() for line in response_reorder.split('\n') if line.strip()]
                reordered_texts = [re.sub(r"^\d+\.\s*", "", txt).strip() for txt in reordered_texts_raw]

                if len(reordered_texts) != total_expected_count: