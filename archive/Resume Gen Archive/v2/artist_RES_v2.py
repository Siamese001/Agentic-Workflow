# File: artist_RES_v2.py
# ArtistGenerator class - generates resume content sections
# Version: 17.02 (V2 Cleaned)

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
from collections import defaultdict # <-- IMPORT ADDED

import google.generativeai as genai

from models_RES import (
    ResumeSection, ThematicAnalysis, HopExecutionError,
    ValidationResult, ValidationSeverity, BulletProvenance
)
from gemini_service import GeminiService
# --- REFACTOR: Standardized global config and template imports ---
from config_RES_v2 import (
    CONFIG, DEFAULT_GENERATION_TEMPERATURE, # Import global CONFIG
    ReasoningConfig, # Keep ReasoningConfig as it's used as a type/enum
)
# --- END REFACTOR ---

# --- REFACTOR: Import global text_utils instance ---
from utils_RES_v2 import (
    text_utils, # Import the global instance
    reasoning_config_to_api_params, enhance_system_prompt_with_reasoning,
    TextSanitizer, build_generation_prompt_with_reinforced_constraints
)
from interpreter_RES_v2 import CodeInterpreterTool

logger = logging.getLogger(__name__)



class ArtistGenerator:

    # --- REFACTOR: Removed app_config parameter from __init__ ---
    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str, thematic_analysis: ThematicAnalysis, artist_specs: Dict, **kwargs):
        """
        Initialize ArtistGenerator with full application configuration.
        
        Args:
            master_resume: Master resume data
            enriched_scaffold: Enriched scaffold from HOP-2
            job_description: Raw job description text
            thematic_analysis: ThematicAnalysis from HOP-0
            artist_specs: artist_specs.json content
            **kwargs: Additional parameters (company_name, previous_failures, etc.)
        """
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.artist_specs = artist_specs
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        

        # --- FIX: (Confusing Alias) Use self.constraints directly ---
        self.constraints = CONFIG.constraints
        
        if kwargs:
            logging.debug(f"ArtistGenerator received extra kwargs: {list(kwargs.keys())}")
            self.previous_failures = kwargs.get('previous_failures', [])
            self.company_name = kwargs.get('company_name', 'Unknown Company')
            self.job_title = kwargs.get('job_title', 'Target Role')
        else:
            self.company_name = 'Unknown Company'
            self.job_title = 'Target Role'
        
        if not self.master_resume:
            raise ValueError("ArtistGenerator requires a master_resume to be provided.")

        # --- REFACTOR: Load prompts from global CONFIG ---
        self.PROMPT_TEMPLATES = CONFIG.prompts.prompts
        if not self.PROMPT_TEMPLATES:
            raise HopExecutionError("ArtistGenerator: prompts.json failed to load from CONFIG.")
        # --- END REFACTOR ---

        self.code_interpreter = CodeInterpreterTool()
        
        self.gemini_service = GeminiService(default_model=CONFIG.rag.model)

        self.GENERATION_DISPATCH = {
            "_copy_from_master": self._copy_from_master,
            "_copy_k0_contact": self._copy_k0_contact,
            "_generate_dummy_header": self._generate_dummy_header,
            "_generate_tailored_bullets_for_experience": self._generate_tailored_bullets_for_experience,
            "_generate_tailored_overview_for_experience": self._generate_tailored_overview_for_experience,
        }

        self.SECTION_GENERATION_SPECS = self._parse_specs(self.artist_specs)
        
        self.PROVENANCE_SPLIT_TARGETS = self._convert_config_keys_to_enums(
            self.constraints.provenance_split_targets
        )
        self.BULLET_WORD_COUNT_RANGES = self._convert_config_keys_to_enums(
            self.constraints.bullet_word_count_ranges
        )
        self.NARRATIVE_CONFIG = self._convert_config_keys_to_enums(
            self.constraints.narrative_config
        )

    def generate_section(self, prompt: str, system_prompt: str, reasoning_config: Any, temperature: float, section_id: str) -> str:
        """
        V2-aligned generate_section. It only calls the API with pre-built context.
        
        Args:
            prompt: Pre-built prompt from ContextRelayLayer
            system_prompt: System prompt from ContextRelayLayer
            reasoning_config: Reasoning configuration
            temperature: Temperature override
            section_id: Section identifier for logging
            
        Returns:
            Generated text from API
        """
        logging.info(f"  ArtistGenerator executing API call for {section_id}...")
        # This method now *only* calls the API via GeminiService
        # The model_to_use is set by the orchestrator
        # --- REFACTOR: Use global CONFIG for fallback model ---
        model = getattr(self, 'model_to_use', CONFIG.rag.model)
        # --- END REFACTOR ---

        generated_text, api_calls, _ = self.gemini_service.call_api(
            prompt=prompt,
            section_id=section_id,
            model=model,
            system_prompt=system_prompt,
            reasoning_config=reasoning_config,
            temperature=temperature
        )
        
        return generated_text
    
    def _convert_config_keys_to_enums(self, config_dict: Dict) -> Dict:
        # ... existing code ...
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
        # ... existing code ...
        try:
            reconstructed_specs = {}
            for section_name, spec in raw_specs.items():
                try:
                    # Try to get the ResumeSection enum
                    section_enum = ResumeSection[section_name]
                    
                    # 1. Validate the generation_type (the "How")
                    gen_type = spec.get("generation_method")
                    if gen_type and gen_type not in self.GENERATION_DISPATCH:
                        raise HopExecutionError(f"Invalid 'generation_method' ({gen_type}) for section '{section_name}'")

                    # 2. Validate Prompt Key (the "What")
                    if gen_type in ["_generate_section_generic", "_generate_section_macro_tot"]:
                        prompt_key = spec.get("prompt_template")
                        if not prompt_key or prompt_key not in self.PROMPT_TEMPLATES:
                            raise HopExecutionError(f"Invalid or missing 'prompt_template' key ({prompt_key}) for section '{section_name}'")

                    # 3. Validate ReasoningConfig
                    if 'reasoning_config' in spec and isinstance(spec.get('reasoning_config'), str):
                         config_name = spec['reasoning_config']
                         if hasattr(ReasoningConfig, config_name):
                             spec['reasoning_config'] = getattr(ReasoningConfig, config_name)
                         else:
                              raise AttributeError(f"ReasoningConfig has no attribute '{config_name}'")

                    if 'depends_on' in spec and isinstance(spec.get('depends_on'), str):
                        spec['depends_on'] = ResumeSection[spec['depends_on']]

                    # Successfully validated - add to reconstructed specs
                    reconstructed_specs[section_enum] = spec
                    
                except KeyError:
                    # Skip invalid keys like "$schema_version", "_metadata", etc.
                    logging.warning(f"Skipping unknown key '{section_name}' in artist_specs.json.")
                    continue
                    
                except AttributeError as e:
                    # Config validation error - this is fatal
                    logging.error(f"Error parsing spec entry for '{section_name}'. Offending spec snippet: {str(spec)[:200]}...")
                    if 'reasoning_config' in spec and isinstance(spec.get('reasoning_config'), str):
                        config_name = spec['reasoning_config']
                        logging.error(f"  Reason: ReasoningConfig attribute not found: '{config_name}'")
                    elif 'depends_on' in spec and isinstance(spec.get('depends_on'), str):
                        depends_name = spec['depends_on']
                        logging.error(f"  Reason: Depends_on ResumeSection name not found: '{depends_name}'")
                    else:
                        logging.error(f"  Reason: General AttributeError during parsing: {e}")
                    raise HopExecutionError(f"Error parsing spec for '{section_name}': Invalid enum or config name. Details: {e}")

            logging.info(f"Successfully loaded and parsed artist specs from 'artist_specs.json'. Sections loaded: {len(reconstructed_specs)}")
            return reconstructed_specs

        except HopExecutionError as he:
             logging.error(f"Spec parsing failed: {he}")
             raise he
        except Exception as e:
            logging.error(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}", exc_info=True)
            raise HopExecutionError(f"CRITICAL: An unexpected error occurred while parsing artist specs: {e}")

    def _mechanical_word_count_fix(
        # ... existing code ...
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
        # --- REFACTOR: Use global text_utils instance ---
        current_wc = text_utils.count_words_ms_word_style(text)
        # --- END REFACTOR ---
        
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
                        # --- REFACTOR: Use global text_utils instance ---
                        if text_utils.count_words_ms_word_style(text) <= max_wc:
                        # --- END REFACTOR ---
                            return text
        
        return text

    def _pre_flight_constraint_test(
        # ... existing code ...
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
            # --- REFACTOR: Use global CONFIG for fallback model ---
            response, _, _ = self.gemini_service.call_api(
                prompt=test_prompt,
                section_id=f"{section_enum.name}_ConstraintTest",
                model=getattr(self, 'model_to_use', CONFIG.rag.model),
                system_prompt="You are a constraint feasibility analyzer.",
                reasoning_config=ReasoningConfig.DEFAULT,
                temperature=0.2  # Low temp for analysis
            )
            # --- END REFACTOR ---
            
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


    def generate(
        # ... existing code ...
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
            raise he # <-- ADD THIS LINE to stop the workflow
            # return artist_output, validation_results, total_api_calls_this_pass

        except Exception as e:
            logging.error(f"Artist generation failed unexpectedly during selective run: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="ARTIST_GENERATION_ERROR", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Artist generation failed unexpectedly: {str(e)}",
                details={"error": str(e)}
            ))
            return artist_output, validation_results, total_api_calls_this_pass

    def _generate_artist_output(
        # ... existing code ...
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
            generation_method = self.GENERATION_DISPATCH.get(generation_method_name)

            if not generation_method:
                raise HopExecutionError(f"Internal Error: No dispatch method found for generation_method '{generation_method_name}'")

            section_api_calls = 0
            generated_content = None

            logging.info(f"  Generating section: {section_enum.name} (Method: {generation_method_name})")
            
            if generation_method_name in ["_copy_from_master", "_copy_k0_contact", "_generate_dummy_header"]:
                try:
                    if generation_method_name == "_copy_from_master":
                         output[section_enum.value] = generation_method(spec.get("master_data_key"))
                    else:
                         output[section_enum.value] = generation_method()
                    section_api_calls = 0
                except Exception as e:
                    raise HopExecutionError(f"Unexpected error in {generation_method_name} for {section_enum.value}: {e}") from e

            else:
                final_temp = temperature_overrides.get(section_enum)
                if final_temp is None:
                    # --- FIX: Use global default temp ---
                    final_temp = DEFAULT_GENERATION_TEMPERATURE
                    logging.warning(f"  {section_enum.name}: Temperature override NOT FOUND! Using default {final_temp}")
                    # --- END FIX ---

                try:
                    method_args = {
                        "temperature_override": final_temp,
                        "section_enum": section_enum
                    }
                    if generation_method_name == "_generate_tailored_bullets_for_experience":
                         method_args.update(spec.get("extra_args", {}))
                         method_args["provenance_targets"] = self.PROVENANCE_SPLIT_TARGETS.get(section_enum, {})
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)
                    elif generation_method_name == "_generate_tailored_overview_for_experience":
                         dependency_enum = spec.get("depends_on")
                         # --- FIX: Check self.drafts, not output ---
                         if dependency_enum and self.drafts.get(dependency_enum) is not None:
                              method_args["generated_bullets"] = self.drafts[dependency_enum]
                         # --- END FIX ---
                         else:
                              dep_name = dependency_enum.name if dependency_enum else "None"
                              dep_value = dependency_enum.value if dependency_enum else "None"
                              raise HopExecutionError(f"Dependency {dep_name} ({dep_value}) missing for {section_enum.name}")
                         method_args["word_count_range"] = self._get_overview_wc_range(section_enum)
                         method_args["reasoning_config"] = self._get_reasoning_config_for_section(section_enum)

                    # --- FIX: Call 'generation_method' (the function) ---
                    generated_content, section_api_calls = generation_method(**method_args)
                    # --- END FIX ---

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

    def _post_process_narrative(self, narrative_text: str, section_enum: ResumeSection) -> str:
        # ... existing code ...
        if section_enum not in self.SECTION_GENERATION_SPECS:
            logging.error(f"Cannot post-process narrative: Spec missing for {section_enum.name}")
            return narrative_text

        # --- FIX: This method is broken as _build_context_narrative is dead ---
        # --- We will rely on the validator to catch errors ---
        # spec = self.SECTION_GENERATION_SPECS[section_enum]
        # context = self._build_context_narrative(spec, section_enum=section_enum)
        # min_wc = context.get('min_wc', 0); max_wc = context.get('max_wc', float('inf')); target_sc = context.get('target_sc', 0)
        # ...
        # --- END FIX ---
        return narrative_text

    def _get_reasoning_config_for_section(self, section_enum: ResumeSection) -> ReasoningConfig:
        # ... existing code ...
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
        # ... existing code ...
        if section_enum == ResumeSection.K2_UNIFY_OVERVIEW:
             return (self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX)
        elif section_enum == ResumeSection.K3_IBM_OVERVIEW:
             return (self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX)
        else:
             logging.warning(f"No overview WC range explicitly defined for {section_enum.name}. Using default (25-40).")
             return (25, 40)

    # DEPRECATED: Removed _get_feedback_instruction (Spec 1.3)
    # This method is part of a deprecated retry strategy, superseded by
    # _build_generation_prompt_with_reinforced_constraints which modifies
    # prompts based on attempt number rather than specific failure types.

    # --- REFACTOR: Use imported COVER_LETTER_SIGNATURE_TEMPLATE ---
    def _get_expected_signature(self) -> str:
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})

        # --- FIX: (Misplaced Template) Load template from prompts ---
        # We removed the template from config_RES_v2.py. Now we load it
        # from the PROMPT_TEMPLATES dict, which is populated by prompts.json.
        # We will add the template to prompts.json in a later step.
        template = self.PROMPT_TEMPLATES.get("COVER_LETTER_SIGNATURE_TEMPLATE")
        if not template:
            # Fallback in case prompts.json isn't updated yet
            template = "Best regards,\n{name}"

        try:
            return template.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except KeyError as e: 
            raise HopExecutionError(f"Missing key in COVER_LETTER_SIGNATURE_TEMPLATE format: {e}")
    # --- END REFACTOR ---

    def _get_experience_snippets_for_cl(self) -> str:
        # ... existing code ...
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
        # ... existing code ...
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

        # --- BUG 4 FIX: Use prompt from prompts.json ---
        prompt_template = self.PROMPT_TEMPLATES.get("artist_overview_generation")
        if not prompt_template:
            raise HopExecutionError("artist_overview_generation prompt not found in prompts.json")

        prompt = prompt_template.format(
            bullet_summary_input=bullet_summary_input,
            theme_prompt_section=theme_prompt_section,
            min_wc=min_wc,
            max_wc=max_wc
        )
        # --- END FIX ---

        system_prompt = "You are an expert resume editor specializing in summarizing experience sections while incorporating key executive themes."
        # --- REFACTOR: Use self.generate_section wrapper ---
        synthesized_overview = self.generate_section(
                prompt=prompt,
                section_id=section_id,
                system_prompt=system_prompt,
                reasoning_config=reasoning_config,
                temperature=temperature_override
            )
        call_count = 1
        # --- END REFACTOR ---

        if "FINAL OVERVIEW" in synthesized_overview or "BULLETS TO SUMMARIZE" in synthesized_overview or "KEY THEMES" in synthesized_overview:
            raise HopExecutionError(f"{section_id} generation failed: Output contained prompt artifacts.")
        
        # --- REFACTOR: Use global text_utils instance ---
        final_wc = text_utils.count_words_ms_word_style(synthesized_overview); final_sc = text_utils.count_sentences(synthesized_overview)
        # --- END REFACTOR ---
        if not (min_wc <= final_wc <= max_wc): logging.warning(f"{section_id} overview WC ({final_wc}) outside target ({min_wc}-{max_wc}).")
        if not (1 <= final_sc <= 2): logging.warning(f"{section_id} overview SC ({final_sc}) outside target (1-2).")
        return synthesized_overview, call_count

    def _validate_llm_bullet_selection(self, selected_bullets_text: List[str], master_bullets_structured: List[Dict], expected_count: int, section_id_str: str) -> List[Dict]:
        # ... existing code ...
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
        # ... existing code ...
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
        ACCEPTABLE_MIN_WC = self.constraints.BULLETS_WORD_COUNT_ACCEPTABLE_MIN
        ACCEPTABLE_MAX_WC = self.constraints.BULLETS_WORD_COUNT_ACCEPTABLE_MAX
        # --- End new definitions ---

        # Get schedule from centralized config
        # If CONFIG.artist.retry_temperature_schedule exists, use it, otherwise use default
        default_schedule = [1.0, 0.8, 0.6, 0.4, 0.2]
        temperature_schedule = getattr(getattr(CONFIG, 'artist', None), 'retry_temperature_schedule', default_schedule)
        
        if temperature_override is not None:
            temperature_schedule = [temperature_override] + temperature_schedule[1:]
        
        last_rewritten_text = original_bullet_text
        # --- REFACTOR: Use global text_utils instance ---
        last_word_count = text_utils.count_words_ms_word_style(original_bullet_text)
        
        logging.info(f"  Attempting mechanical word count fix for {section_id_str} (zero cost)...")
        mechanical_fix = self._mechanical_word_count_fix(original_bullet_text, min_wc, max_wc)
        mechanical_wc = text_utils.count_words_ms_word_style(mechanical_fix)
        # --- END REFACTOR ---
        
        if min_wc <= mechanical_wc <= max_wc and mechanical_fix != original_bullet_text:
            logging.info(
                f"  ✓ MECHANICAL REPAIR SUCCESS for {section_id_str}: "
                # --- REFACTOR: Use global text_utils instance ---
                f"{text_utils.count_words_ms_word_style(original_bullet_text)} → {mechanical_wc} words (no API calls)"
                # --- END REFACTOR ---
            )
            return mechanical_fix, 0
        
        logging.info(f"  Mechanical fix {'did not help' if mechanical_fix == original_bullet_text else 'insufficient'}. Proceeding with LLM retries...")
        
        for attempt in range(max_retries):
            # ... existing code ...
            current_temp = temperature_schedule[min(attempt, len(temperature_schedule) - 1)]
            
            logging.info(
                f"  Bullet WC rewrite for {section_id_str}, Attempt {attempt + 1}/{max_retries}, "
                f"Temp: {current_temp:.1f}, Target: {min_wc}-{max_wc} words"
            )
            
            try:
                # --- FIX: Load prompt from template ---
                prompt_template = self.PROMPT_TEMPLATES.get("artist_bullet_rewrite_wc")
                if not prompt_template:
                    raise HopExecutionError("artist_bullet_rewrite_wc prompt not found")

                base_prompt = prompt_template.format(
                    original_bullet=original_bullet_text,
                    min_wc=min_wc,
                    max_wc=max_wc
                )
                # --- END FIX ---
                
                # --- REFACTOR: Use prompt reinforcement ---
                # This function *does* exist in utils_RES_v2.py
                enhanced_prompt = build_generation_prompt_with_reinforced_constraints(
                    base_prompt,
                    {'min_wc': min_wc, 'max_wc': max_wc},
                    attempt + 1
                )
                # --- END REFACTOR ---
                
                try:
                    reasoning_config = ReasoningConfig.DEFAULT
                except AttributeError:
                    logging.warning("ReasoningConfig.DEFAULT missing. Creating default.")
                    reasoning_config = ReasoningConfig()
                
                system_prompt = "You are an expert resume editor concisely rewriting bullets to meet strict word count targets."
                
                try:
                    # --- REFACTOR: Use self.generate_section wrapper ---
                    rewritten_text = self.generate_section(
                        prompt=enhanced_prompt,
                        section_id=f"{section_id_str}_RewriteWC_Attempt{attempt+1}",
                        system_prompt=system_prompt,
                        reasoning_config=reasoning_config,
                        temperature=current_temp
                    )
                    call_count = 1
                    # --- END REFACTOR ---
                    total_calls += call_count
                    
                    # --- REFACTOR: Use global text_utils instance ---
                    rewritten_wc = text_utils.count_words_ms_word_style(rewritten_text)
                    # --- END REFACTOR ---
                    last_rewritten_text = rewritten_text
                    last_word_count = rewritten_wc
                    
                    # Check against the WIDEST acceptable range to stop retries
                    if ACCEPTABLE_MIN_WC <= rewritten_wc <= ACCEPTABLE_MAX_WC:
                        log_level = logging.INFO
                        status = "SUCCESS"
                        # Add a warning if it's outside the ideal range but inside the acceptable one
                        if not (min_wc <= rewritten_wc <= max_wc):
                            log_level = logging.WARNING
                            status = "PASSED (TOLERANCE)"

                        logging.log(
                            log_level,
                            f"  ✓ Bullet WC rewrite {status} for {section_id_str} on attempt {attempt + 1}. "
                            f"Word count: {rewritten_wc} (Ideal: {min_wc}-{max_wc}, Acceptable: {ACCEPTABLE_MIN_WC}-{ACCEPTABLE_MAX_WC}), "
                            f"Total API calls: {total_calls}"
                        )
                        return rewritten_text, total_calls
                    else:
                        logging.warning(
                            f"  Bullet WC rewrite attempt {attempt + 1} FAILED for {section_id_str}. "
                            f"Got {rewritten_wc} words, target: {min_wc}-{max_wc} (Acceptable: {ACCEPTABLE_MIN_WC}-{ACCEPTABLE_MAX_WC}). "
                            f"{'Retrying...' if attempt < max_retries - 1 else 'No more retries.'}"
                        )
                        # Don't raise HopExecutionError here, let the loop finish
                
                except HopExecutionError as he:
                    # ... existing code ...
                    # Log the error but don't re-raise, allow loop to continue or fail gracefully
                    logging.error(f"  HopExecutionError during WC rewrite attempt {attempt + 1}: {he}")
                    if attempt == max_retries - 1:
                        # If it fails on the last try, we'll use the last known values
                        logging.error("  Last rewrite attempt failed. Proceeding to final tolerance check.")
                except Exception as e:
                    # ... existing code ...
                    logging.error(f"  Unexpected error during WC rewrite attempt {attempt + 1} for {section_id_str}: {e}")
                    if attempt == max_retries - 1:
                        # If it fails on the last try, we'll use the last known values
                        logging.error("  Last rewrite attempt failed unexpectedly. Proceeding to final tolerance check.")
            
            except Exception as outer_e:
                # ... existing code ...
                logging.error(f"  Outer loop error during WC rewrite for {section_id_str}: {outer_e}")
                if attempt == max_retries - 1:
                    break # Exit loop to go to final check

        # --- NEW LOGIC: Triage *after* all retries are exhausted ---
        # ... existing code ...
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
        # ... existing code ...
        final_bullets = []; total_rewrite_calls = 0; logging.info(f"  Validating word count for {section_id_str} ({min_target}-{max_target})")
        for i, bullet_data in enumerate(selected_bullets_structured):
            if not isinstance(bullet_data, dict): raise HopExecutionError(f"Invalid item in bullet list for {section_id_str}[{i}]")
            original_text = bullet_data.get('text', bullet_data.get('bullet_text', '')); original_provenance = bullet_data.get('provenance', BulletProvenance.Verbatim.value)
            # --- REFACTOR: Use global text_utils instance ---
            word_count = bullet_data.get('word_count', text_utils.count_words_ms_word_style(original_text))
            # --- END REFACTOR ---
            if not original_text: raise HopExecutionError(f"Empty bullet in {section_id_str}[{i}].")

            if not (min_target <= word_count <= max_target):
                logging.warning(
                    f"  WC Check FAIL for {section_id_str}[{i}]: Count={word_count} (Target: {min_target}-{max_target}). "
                    f"Attempting rewrite with enhanced temperature-based retry (temps: 1.0→0.8→0.6→0.4→0.2) for bullet: '{original_text[:50]}...'"
                )
                try:
                    rewritten_text, rewrite_calls = self._rewrite_bullet_for_word_count(original_text, (min_target, max_target), f"{section_id_str}_RewriteWC_{i}", temperature_override, max_retries=5)
                    total_rewrite_calls += rewrite_calls; 
                    # --- REFACTOR: Use global text_utils instance ---
                    rewritten_word_count = text_utils.count_words_ms_word_style(rewritten_text)
                    # --- END REFACTOR ---
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
        # ... existing code ...
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

            # --- FIX: Load prompt from template ---
            prompt_template = self.PROMPT_TEMPLATES.get("artist_customized_bullet")
            if not prompt_template:
                raise HopExecutionError("artist_customized_bullet prompt not found")
            
            prompt = prompt_template.format(
                bullets_input=bullets_input,
                context_keywords=", ".join(context_keywords),
                bullet_count=len(source_bullets_text)
            )
            # --- END FIX ---

            try: reasoning_config = ReasoningConfig.DEFAULT
            except AttributeError: logging.warning("ReasoningConfig.DEFAULT missing. Creating default."); reasoning_config = ReasoningConfig()

            system_prompt = "You are an expert resume editor subtly tailoring bullets..."
            # --- REFACTOR: Use self.generate_section wrapper ---
            response_text = self.generate_section(
                prompt=prompt,
                section_id=section_id_str,
                system_prompt=system_prompt,
                reasoning_config=reasoning_config,
                temperature=temperature_override
            )
            call_count = 1
            # --- END REFACTOR ---
            total_calls += call_count
            rewritten_bullets_text = [line.replace("• ", "").strip() for line in response_text.split('\n') if line.strip().startswith("• ")]
            if len(rewritten_bullets_text) != len(source_bullets_text): raise HopExecutionError(f"{section_id_str} LLM returned {len(rewritten_bullets_text)} customized bullets, expected {len(source_bullets_text)}.")
            # --- REFACTOR: Use global text_utils instance ---
            result_list = [{"text": b, "provenance": BulletProvenance.Customized.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in rewritten_bullets_text]
            # --- END REFACTOR ---
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} customization failed: {e}") from e

    def _generate_synthetic_bullets(self, count: int, company_name: str, job_description: str, thematic_analysis: ThematicAnalysis, context_bullets: str, reasoning_config: ReasoningConfig, section_id_str: str, temperature_override: Optional[float] = None) -> Tuple[List[Dict], int]:
        # ... existing code ...
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

            # --- FIX: Load prompt from template ---
            prompt_template = self.PROMPT_TEMPLATES.get("artist_synthetic_bullet")
            if not prompt_template:
                raise HopExecutionError("artist_synthetic_bullet prompt not found")

            prompt = prompt_template.format(
                company_name=company_name,
                primary_theme=primary_theme,
                context_keywords=", ".join(context_keywords),
                context_bullets=context_bullets,
                job_description=job_description[:500] + "...",
                count=count
            )
            # --- END FIX ---

            system_prompt = "You generate plausible, impactful, synthetic resume bullets..."
            # --- REFACTOR: Use self.generate_section wrapper ---
            response_text = self.generate_section(
                prompt=prompt,
                section_id=section_id_str,
                system_prompt=system_prompt,
                reasoning_config=reasoning_config,
                temperature=temperature_override
            )
            call_count = 1
            # --- END REFACTOR ---
            total_calls += call_count
            synthetic_bullets_text = [line.replace("* ", "").strip() for line in response_text.split('\n') if line.strip().startswith("* ")]
            if len(synthetic_bullets_text) != count: raise HopExecutionError(f"{section_id_str} LLM failed to generate exactly {count} synthetic bullets (got {len(synthetic_bullets_text)}).")
            # --- REFACTOR: Use global text_utils instance ---
            result_list = [{"text": b, "provenance": BulletProvenance.Synthetic.value, "word_count": text_utils.count_words_ms_word_style(b)} for b in synthetic_bullets_text]
            # --- END REFACTOR ---
            return result_list, total_calls
        except HopExecutionError as he: raise he
        except Exception as e: raise HopExecutionError(f"{section_id_str} synthetic generation failed: {e}") from e

    def _generate_tailored_bullets_for_experience(
            # ... existing code ...
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
                 # --- REFACTOR: Use global text_utils instance ---
                 master_bullets_structured.append({"bullet_text": cleaned_text, "text": cleaned_text, "provenance": BulletProvenance.Verbatim.value, "word_count": text_utils.count_words_ms_word_style(cleaned_text)})
                 # --- END REFACTOR ---
             else: logging.warning(f"Skipping empty master item for {company_name or 'Competencies'}")

        verbatim_count = provenance_targets.get('Verbatim', 0); customized_count = provenance_targets.get('Customized', 0); synthetic_count = provenance_targets.get('Synthetic', 0)
        total_expected_count = verbatim_count + customized_count + synthetic_count
        if not master_bullets_structured and (verbatim_count > 0 or customized_count > 0): raise HopExecutionError(f"{section_enum.name} Cannot select/customize: No valid master items found.")

        verbatim_bullets_selected = []
        if verbatim_count > 0:
            # ... existing code ...
            logging.info(f"    Selecting {verbatim_count} Verbatim items using CodeInterpreter (0 API calls)...")
            if len(master_bullets_structured) < verbatim_count:
                raise HopExecutionError(f"{section_enum.name} Cannot select {verbatim_count} Verbatim (only {len(master_bullets_structured)} available).")
            
            # Get keywords for selection
            keywords_for_selection = []
            comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                if isinstance(kw_raw, list):
                    keywords_for_selection = kw_raw[:10]
            
            # COST-OPTIMIZED: Use CodeInterpreterTool for selection (replaces 1 LLM call with 0)
            if not hasattr(self, 'code_interpreter') or not self.code_interpreter:
                logging.warning("CodeInterpreterTool not found. Falling back to random selection.")
                random.shuffle(master_bullets_structured)
                verbatim_bullets_selected = master_bullets_structured[:verbatim_count]
            else:
                try:
                    # Serialize data for the script
                    bullets_json = json.dumps(master_bullets_structured)
                    keywords_json = json.dumps(keywords_for_selection)
                    
                    # Define Python selection script
                    selection_script = f"""
import json

bullets_data = {bullets_json}
keywords = {keywords_json}
verbatim_count = {verbatim_count}

keywords_lower = [k.lower() for k in keywords if k]

def score_bullet(bullet_text):
    if not keywords_lower:
        return 0
    text_lower = bullet_text.lower()
    score = sum(1 for kw in keywords_lower if kw in text_lower)
    return score

for bullet in bullets_data:
    bullet['relevance_score'] = score_bullet(bullet.get('bullet_text', ''))

sorted_bullets = sorted(bullets_data, key=lambda x: x['relevance_score'], reverse=True)
selected_bullets = sorted_bullets[:verbatim_count]

# Remove temporary score
for b in selected_bullets:
    b.pop('relevance_score', None)

print(json.dumps(selected_bullets))
"""
                    # Run the script
                    success, output = self.code_interpreter.run(selection_script)
                    
                    if success:
                        verbatim_bullets_selected = json.loads(output)
                        logging.info(f"  ✓ Selected {len(verbatim_bullets_selected)} verbatim bullets (0 API calls)")
                    else:
                        logging.error(f"CodeInterpreter selection failed: {output}")
                        raise HopExecutionError(f"CodeInterpreter bullet selection failed: {output}")
                        
                except Exception as e:
                    logging.error(f"CodeInterpreter selection error: {e}")
                    raise HopExecutionError(f"{section_enum.name} Verbatim selection failed: {e}") from e
            
            final_bullets.extend(verbatim_bullets_selected)

        if customized_count > 0:
            # ... existing code ...
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
            # ... existing code ...
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
            # ... existing code ...
            logging.info(f"    Reordering {len(final_bullets)} bullets for impact...")
            current_bullets_text_list = [f"{i+1}. {bullet.get('text', '')}" for i, bullet in enumerate(final_bullets) if isinstance(bullet, dict)]
            current_bullets_text_input = '\n'.join(current_bullets_text_list)

            # --- REFACTOR: ELIMINATE WASTEFUL LLM CALL ---
            # The old logic made an LLM call just to sort.
            # The new logic uses the Code Interpreter for a free, fast, reliable sort.

            keywords_for_prompt = []
            comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
            if comp_intel:
                 kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
                 if isinstance(kw_raw, list): keywords_for_prompt = kw_raw[:10]

            if not hasattr(self, 'code_interpreter') or not self.code_interpreter:
                logging.warning("CodeInterpreterTool not found. Skipping bullet reordering.")
                return final_bullets, total_calls_for_section

            # 1. Serialize data for the script
            bullets_json = json.dumps(final_bullets)
            keywords_json = json.dumps(keywords_for_prompt)

            # 2. Define the Python sorting script
            sorting_script = f"""
import json

bullets_data = {bullets_json}
keywords = {keywords_json}
keywords_lower = [k.lower() for k in keywords if k]

def score_bullet(bullet_text):
    if not keywords_lower:
        return 0
    text_lower = bullet_text.lower()
    score = sum(1 for kw in keywords_lower if kw in text_lower)
    return score

for bullet in bullets_data:
    bullet['relevance_score'] = score_bullet(bullet.get('text', ''))

sorted_bullets = sorted(bullets_data, key=lambda x: x['relevance_score'], reverse=True)
print(json.dumps(sorted_bullets))
"""
            # 3. Run the script using the tool
            success, output = self.code_interpreter.run(sorting_script)

            if success:
                try:
                    final_ordered_bullets_dicts = json.loads(output)
                    logging.info(f"  ✓ Reordering complete for {section_enum.name} (0 API calls).")
                    # Remove the temporary score
                    for b in final_ordered_bullets_dicts: b.pop('relevance_score', None)
                    return final_ordered_bullets_dicts, total_calls_for_section  # 0 calls added
                except json.JSONDecodeError as e:
                    raise HopExecutionError(f"Code Interpreter sorting failed: Invalid JSON output. {e}")
            else:
                raise HopExecutionError(f"Code Interpreter sorting failed: {output}")
            # --- END REFACTOR ---
        else:
            logging.info(f"    Skipping reordering for Competencies section ({section_enum.name}).")
            if is_competencies:
                for item in final_bullets:
                    if isinstance(item, dict) and 'text' in item:
                        cleaned_text = re.sub(r'^\*\s*\*\*(.*?):\*\*\s*', r'\1:', item['text']).strip()
                        cleaned_text = re.sub(r'^[•*]\s*', '', cleaned_text).strip()
                        item['text'] = cleaned_text
                        # --- REFACTOR: Use global text_utils instance ---
                        item['word_count'] = text_utils.count_words_ms_word_style(cleaned_text)
                        # --- END REFACTOR ---
            return final_bullets, total_calls_for_section
