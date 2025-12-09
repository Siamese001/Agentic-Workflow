# File: validation_context.py
# Validation Context Module - V18 Architecture
# Version: 18.00
# Contains the ValidationContext class and all its lazy-loading calculation methods.
# Refactored from validator_RES_v3_8.py

import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Callable
from models_RES import ImmutableStagingBuffer, ThematicAnalysis, ResumeSection
from config_RES_v3_8 import CONFIG # Import the main config object
from utils_RES_v3_8 import text_utils, calculate_signal_score

class ValidationContext:
    """
    Holds all necessary data for the ValidationEngine to run checks.
    Uses lazy calculation for metrics.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str, master_resume: Dict, app_config: Any):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {}
        self.config = app_config # Use the main app_config
        self.constraints = app_config.constraints
        self.signal_constraints = app_config.signal_constraints
        self.logger = logging.getLogger(__name__)

    def get_details_for_rule(self, rule_id: str) -> Dict:
        """Retrieves cached details for a given rule ID."""
        return self._cache.get(rule_id, {})

    def _calculate_metric_details(self, section_enum: ResumeSection, metrics_to_calc: List[Tuple[str, Callable]], constraints: Dict[str, Any]) -> Dict:
        """Helper to calculate and cache metrics for a section."""
        text = self.staging_buffer.get(section_enum.value, '')
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
        Accessing `context.total_words` will call `_calculate_total_words`.
        Accessing `context.k1_sentence_count_details` will call `_calculate_k1_sentence_count_details`.
        """
        if name in self._cache:
            return self._cache[name]

        # For detail caches (e.g., "k1_sentence_count_details")
        if name.endswith('_details'):
            calculation_method_details = getattr(self, f"_calculate_{name}", None)
            if calculation_method_details:
                value = calculation_method_details()
                # self._cache[name] = value # The method itself handles caching the rule ID
                return value

        # For simple value caches (e.g., "total_words")
        calculation_method = getattr(self, f"_calculate_{name}", None)
        if calculation_method:
            value = calculation_method()
            self._cache[name] = value
            return value

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or calculation method '_calculate_{name}' or '_calculate_{name}_details'")

    # --- Lazy Calculation Methods ---

    def _calculate_total_words(self):
        total = 0
        buffer_data = self.staging_buffer.data
        for key_enum in ResumeSection:
            key = key_enum.value
            if key_enum not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT] and \
               not key.endswith("_HEADER"):
                value = buffer_data.get(key)
                if isinstance(value, str):
                    total += text_utils.count_words_ms_word_style(value)
                elif isinstance(value, list):
                    total += sum(text_utils.count_words_ms_word_style(item.get('text', str(item))) if isinstance(item, dict) else text_utils.count_words_ms_word_style(str(item)) for item in value)
        details = {'total_words': total, 'min': self.constraints.TOTAL_WORD_COUNT_MIN, 'max': self.constraints.TOTAL_WORD_COUNT_MAX}
        self._cache["H5_GLOBAL_TOTAL_WORD_COUNT"] = details
        return total

    def _calculate_k1_sentence_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('sentence_count', text_utils.count_sentences)],
            constraints={'min': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}
        )
        self._cache["H3_K1_SENTENCE_COUNT"] = details
        return details

    def _calculate_k1_word_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            # FIX 1: Use count_words_ms_word_style
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style)],
            constraints={'min': self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}
        )
        # FIX 2: Use correct cache key
        self._cache["H3_K1_WORD_COUNT"] = details
        return details

    def _calculate_k2_overview_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K2_UNIFY_OVERVIEW,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["H3_K2_OVERVIEW_WORD_COUNT"] = details
        self._cache["H3_K2_OVERVIEW_SENTENCE_COUNT"] = details
        return details

    def _calculate_k3_overview_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K3_IBM_OVERVIEW,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["H3_K3_OVERVIEW_WORD_COUNT"] = details
        self._cache["H3_K3_OVERVIEW_SENTENCE_COUNT"] = details
        return details

    def _calculate_headline_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K0_HEADLINE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('headline', lambda t: t)],
            constraints={'min': self.constraints.HEADLINE_WORD_COUNT_MIN, 'max': self.constraints.HEADLINE_WORD_COUNT_MAX}
        )
        self._cache["H3_K0_HEADLINE_WORD_COUNT"] = details
        self._cache["H3_K0_HEADLINE_NO_TITLES"] = details
        self._cache["H3_K0_HEADLINE_NO_COMMAS"] = details
        self._cache["H3_K0_HEADLINE_COMPONENT_WC"] = details
        return details

    def _calculate_cover_letter_jd_similarity(self):
        cover_letter_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        similarity = 0.0
        if cover_letter_text and self.job_description:
            try:
                # --- FIX: Call text_utils.calculate_similarity ---
                similarity = text_utils.calculate_similarity(cover_letter_text, self.job_description)
            except Exception as e:
                self.logger.warning(f"Error calculating cover letter similarity: {e}")
                similarity = 0.0

        details = {
            "cover_letter_jd_similarity": similarity,
            "min_sim": self.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD,
            "max_sim": self.signal_constraints.CL_MAX_JD_SIMILARITY
        }
        self._cache["H3_K11_COVER_LETTER_RELEVANCE_RANGE"] = details
        return similarity

    def _calculate_expected_signature(self):
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        # --- FIX: Remove broken import. Get template from config object ---
        try:
            template = self.config.COVER_LETTER_SIGNATURE_TEMPLATE
            return template.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except AttributeError:
             self.logger.error("Error: COVER_LETTER_SIGNATURE_TEMPLATE not found on config object.")
             return f"[Error: Missing signature template in config]"
        except KeyError as e:
            self.logger.error(f"Error formatting signature template: Missing key {e}")
            return f"[Error: Missing signature key {e}]"

    def _calculate_cover_letter_structure_details(self):
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        paras = [p.strip() for p in cl_text.split('\n\n') if p.strip()]
        p1_wc, p2_wc, p3_wc = 0, 0, 0
        error_msg = None
        try:
             salutation_idx = next(i for i, p in enumerate(paras) if p.startswith("Dear Hiring Manager,"))
             closing_idx = next((i for i, p in enumerate(paras) if p == "Sincerely,"), len(paras))
             p1_idx = salutation_idx + 1
             p2_idx = p1_idx + 1
             p3_idx = p2_idx + 1

             if p1_idx < closing_idx and p1_idx < len(paras): p1_wc = text_utils.count_words_ms_word_style(paras[p1_idx])
             if p2_idx < closing_idx and p2_idx < len(paras): p2_wc = text_utils.count_words_ms_word_style(paras[p2_idx])
             if p3_idx < closing_idx and p3_idx < len(paras): p3_wc = text_utils.count_words_ms_word_style(paras[p3_idx])
             if not (p1_idx < closing_idx and p2_idx < closing_idx and p3_idx < closing_idx and p3_idx < len(paras)):
                  error_msg = "Could not find expected 3 body paragraphs before closing"
        except (StopIteration, IndexError):
             error_msg = "Could not find expected salutation or closing"

        c = self.constraints
        details = {
            "p1_wc": p1_wc, "p1_min": c.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": c.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": c.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": c.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": c.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": c.COVER_LETTER_P3_WORD_COUNT_MAX,
            "error": error_msg
        }
        self._cache["H3_K11_COVER_LETTER_STRUCTURE"] = details
        return details

    def _calculate_k4_narrative_details(self):
        min_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN', 40)
        max_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX', 60)
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K4_TRADERSENSE_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': min_wc, 'max_wc': max_wc, 'target_sc': 3}
        )
        self._cache["H3_K4_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K4_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_k5_narrative_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K5_EY_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.EY_NARRATIVE_WORD_COUNT_MIN, 'max_wc': self.constraints.EY_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["H3_K5_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K5_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_k6_narrative_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN, 'max_wc': self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["H3_K6_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K6_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_cross_section_similarity_details(self) -> Dict:
        details = {"failures": [], "checked_pairs": 0, "max_similarity": 0.0, "scores": {}}
        threshold = 0.65
        sections_to_compare = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K9_COMPETENCIES,
        ]

        section_content = {}
        for section_enum in sections_to_compare:
            content = self.staging_buffer.get(section_enum.value)
            if isinstance(content, list) and section_enum == ResumeSection.K9_COMPETENCIES:
                 text_list = [item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in content]
                 section_content[section_enum] = "\n".join(text_list)
            elif isinstance(content, str):
                 section_content[section_enum] = content

        max_sim = 0.0
        for i in range(len(sections_to_compare)):
            for j in range(i + 1, len(sections_to_compare)):
                enum1 = sections_to_compare[i]
                enum2 = sections_to_compare[j]

                text1 = section_content.get(enum1)
                text2 = section_content.get(enum2)

                if text1 and text2:
                    try:
                        # --- FIX: Call text_utils.calculate_similarity ---
                        similarity = text_utils.calculate_similarity(text1, text2)
                        details["checked_pairs"] += 1
                        details["scores"][f"{enum1.name}_vs_{enum2.name}"] = similarity
                        max_sim = max(max_sim, similarity)
                        if similarity >= threshold:
                            details["failures"].append(f"{enum1.name} vs {enum2.name}: {similarity:.3f}")
                    except Exception as e:
                        self.logger.warning(f"Error calculating similarity between {enum1.name} and {enum2.name}: {e}")

        details["max_similarity"] = max_sim
        self._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = details
        return details

    def _calculate_k1_differentiator_range_details(self) -> Dict:
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            # Handle both dataclass and dict forms
            if hasattr(comp_intel, 'differentiator_keywords'):
                differentiators = getattr(comp_intel, 'differentiator_keywords', [])
            elif isinstance(comp_intel, dict):
                differentiators = comp_intel.get('differentiator_keywords', [])
                
        valid_diffs = [kw for kw in differentiators if kw and isinstance(kw, str)]
        found = sum(1 for kw in valid_diffs if kw.lower() in k1_text)
        min_target = self.constraints.K1_MIN_DIFFERENTIATORS
        max_target = self.signal_constraints.K1_MAX_DIFFERENTIATORS
        details = {"found": found, "min": min_target, "max": max_target}
        # FIX 4: Use correct cache key
        self._cache["H3_K1_DIFFERENTIATOR_RANGE"] = details
        return details

    def _calculate_cover_letter_narrative_details(self) -> Dict:
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').lower()
        hook = any(kw in cl_text for kw in ["enthusiastic", "excited", "apply for", "interest in", "compelling opportunity"])
        proof = any(kw in cl_text for kw in ["demonstrated", "achieved", "delivered", "resulted in", "experience", "proven ability", "track record"])
        vision = any(kw in cl_text for kw in ["contribute", "goals", "opportunity", "eager to discuss", "drive success", "valuable asset"])
        details = {"hook": hook, "proof": proof, "vision": vision, "valid": hook and proof and vision}
        self._cache["H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY"] = details
        return details

    def _calculate_narrative_vs_master_similarity_details(self) -> Dict:
        details = {
            "section_results": [],
            "failures": [],
            "min_threshold": 0.40,
            "max_threshold": 0.70
        }
        narrative_sections = {
            ResumeSection.K4_TRADERSENSE_NARRATIVE: 2,
            ResumeSection.K5_EY_NARRATIVE: 3,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE: 4,
        }
        master_experience = self.master_resume.get("professional_experience", [])

        for section_enum, master_index in narrative_sections.items():
            narrative_text = self.staging_buffer.get(section_enum.value)
            master_highlights = []
            section_result = {"section": section_enum.name, "avg_similarity": 0.0, "max_similarity": 0.0, "min_similarity": 1.0, "scores": [], "valid_range": True}

            if isinstance(narrative_text, str) and narrative_text.strip():
                if 0 <= master_index < len(master_experience):
                    exp = master_experience[master_index]
                    highlights_raw = exp.get('highlights', exp.get('bullet_pool', []))
                    if isinstance(highlights_raw, list):
                        master_highlights = [h for h in highlights_raw if isinstance(h, str) and h.strip()]

                if master_highlights:
                    similarities = []
                    for highlight in master_highlights:
                        try:
                            # --- FIX: Call text_utils.calculate_similarity ---
                            similarity = text_utils.calculate_similarity(narrative_text, highlight)
                            similarities.append(similarity)
                            section_result["scores"].append(round(similarity, 3))
                        except Exception as e:
                            self.logger.warning(f"Error calculating narrative similarity for {section_enum.name} vs highlight: {e}")

                    if similarities:
                        section_result["avg_similarity"] = sum(similarities) / len(similarities)
                        section_result["max_similarity"] = max(similarities)
                        section_result["min_similarity"] = min(similarities)

                        if not (details["min_threshold"] <= section_result["avg_similarity"] <= details["max_threshold"]):
                            section_result["valid_range"] = False
                            details["failures"].append(f"{section_enum.name} avg sim ({section_result['avg_similarity']:.3f}) outside range ({details['min_threshold']:.2f}-{details['max_threshold']:.2f})")
                    else:
                        section_result["valid_range"] = False
                        details["failures"].append(f"{section_enum.name}: Could not calculate similarities.")
                else:
                    section_result["valid_range"] = False
                    details["failures"].append(f"{section_enum.name}: Master highlights missing or empty.")
            else:
                section_result["valid_range"] = False
                details["failures"].append(f"{section_enum.name}: Generated narrative missing or empty.")

            details["section_results"].append(section_result)

        self._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = details
        return details

# ==============================================================================
# PRE-FLIGHT VALIDATOR
# ==============================================================================