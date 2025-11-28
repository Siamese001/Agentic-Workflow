# File: artist_RES_v3.8.py
# ArtistGenerator class - generates resume content sections
# Version: 18.0 (V2/V3.8 Agentic Migration)
# V3.8 UPDATE: All V1 generation logic has been excised.
# This class is now a pure "Tool" that only executes API calls
# as directed by the Governor/ContextRelayLayer.

import copy
import functools
import hashlib
import json
import logging
import os
import random
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import defaultdict 

import google.generativeai as genai

from models_RES import (
    ResumeSection, ThematicAnalysis, HopExecutionError,
    ValidationResult, ValidationSeverity, BulletProvenance
)
from gemini_service import GeminiService
# --- REFACTOR: Standardized global config and template imports ---
from config_RES_v3_8 import (
    CONFIG, DEFAULT_GENERATION_TEMPERATURE, # Import global CONFIG
    ReasoningConfig, # Keep ReasoningConfig as it's used as a type/enum
)
# --- END REFACTOR ---

# --- REFACTOR: Import global text_utils instance ---
from utils_RES_v3_8 import (
    text_utils, # Import the global instance
    reasoning_config_to_api_params, enhance_system_prompt_with_reasoning,
    TextSanitizer, build_generation_prompt_with_reinforced_constraints
)
# Note: CodeInterpreterTool is no longer used by the Artist.
# Validation/Scoring is now handled by the PreFlightValidator.

logger = logging.getLogger(__name__)



class ArtistGenerator:

    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, artist_specs: Dict, **kwargs):
        """
        Initialize ArtistGenerator.
        V3.8: This is now a lightweight "Tool" class.
        
        Args:
            master_resume: Master resume data
            enriched_scaffold: Enriched scaffold from HOP-2
            job_description: Raw job description text
            thematic_analysis: ThematicAnalysis from HOP-0
            artist_specs: artist_specs.json content
            **kwargs: Additional parameters (company_name, previous_failures, etc.)
        """
        # Store state provided by Orchestrator (for CRL)
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.artist_specs = artist_specs
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        
        # Store config references
        self.constraints = CONFIG.constraints
        self.PROMPT_TEMPLATES = CONFIG.prompts.prompts
        
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")
        if not self.PROMPT_TEMPLATES:
            raise HopExecutionError("ArtistGenerator: prompts.json failed to load from CONFIG.")

        # Initialize API service
        self.gemini_service = GeminiService(default_model=CONFIG.rag.model)

        # V1/V2 Logic Removed:
        # - self.GENERATION_DISPATCH (Removed)
        # - self.SECTION_GENERATION_SPECS (Removed)
        # - self.PROVENANCE_SPLIT_TARGETS (Removed)
        # - self.NARRATIVE_CONFIG (Removed)
        # - self.code_interpreter (Removed - Validator now handles scoring)
        
        logging.info("V3.8 ArtistGenerator (Tool) initialized.")


    def generate(self, prompt: str, system_prompt: str, reasoning_config: Any, temperature: float, section_id: str, model: str) -> Tuple[str, int]:
        """
        V2-aligned generate method. This is the *only* public generation
        function. It simply executes the API call with the exact context
        provided by the ContextRelayLayer (via the Governor).
        
        Args:
            prompt: Pre-built prompt from ContextRelayLayer
            system_prompt: System prompt from ContextRelayLayer
            reasoning_config: Reasoning configuration
            temperature: Temperature override
            section_id: Section identifier for logging
            model: The specific model selected by the CostRouter
            
        Returns:
            (Generated Text, API Call Count)
        """
        logging.info(f"  ArtistGenerator Tool executing API call for {section_id} on {model}...")

        generated_text, api_calls, _ = self.gemini_service.call_api(
            prompt=prompt,
            section_id=section_id,
            model=model,
            system_prompt=system_prompt,
            reasoning_config=reasoning_config,
            temperature=temperature
        )
        
        return generated_text, api_calls

    # ============================================================================
    # V1/V2 METHODS (EXCISED)
    # ============================================================================
    #
    # All V1-era methods previously in this file have been removed.
    # This includes:
    # - _convert_config_keys_to_enums
    # - _parse_specs
    # - _mechanical_word_count_fix
    # - _pre_flight_constraint_test
    # - The old V1 `generate` method (the one with the `sections_to_generate` loop)
    # - _generate_artist_output
    # - _post_process_narrative
    # - _get_reasoning_config_for_section
    # - _get_overview_wc_range
    # - _get_expected_signature
    # - _get_experience_snippets_for_cl
    # - _generate_tailored_overview_for_experience
    # - _validate_llm_bullet_selection
    # - _rewrite_bullet_for_word_count
    # - _validate_and_potentially_rewrite_bullets
    # - _generate_lightly_customized_bullets
    # - _generate_synthetic_bullets
    # - _generate_tailored_bullets_for_experience
    #
    # All prompt-building logic is now centralized in `prompts_RES_v3.8.py`.
    # All generation is handled by the single `generate` method above.