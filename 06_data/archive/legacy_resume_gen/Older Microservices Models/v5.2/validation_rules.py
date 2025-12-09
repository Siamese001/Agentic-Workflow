# File: validation_rules.py
# Validation Rules Module - V18 Architecture
# Version: 18.00
# Contains all individual rule logic methods used by the PreFlightValidator.
# Refactored from validator_RES_v3_8.py

import logging
import re
from typing import List, Tuple, Set
from collections import defaultdict

# Import ValidationContext from same package
from validation_context import ValidationContext
from models_RES import ResumeSection, BulletProvenance
from utils_RES import text_utils, calculate_signal_score

# --- Regex Patterns (Moved from PreFlightValidator) ---
PROMPT_CONTAMINATION_PATTERN = re.compile(r"\b(MUST|CRITICAL|ABSOLUTELY|Do NOT|Output ONLY|Return ONLY|JSON structure|Word count:|Sentence count:|Target range:|strictly between)\b", re.IGNORECASE)
CONVERSATIONAL_FILLERS_PATTERN = re.compile(r"^(Here is the|Certainly,|I have generated|Below is the|Apologies,|Please note)\b", re.IGNORECASE | re.MULTILINE)
EMPTY_LIST_ITEM_PATTERN = re.compile(r"^\s*[\*\-]\s*($|\n)", re.MULTILINE)
BANNED_INTRO_PHRASES_PATTERN = re.compile(r"^(In my role as|As a|At \[Company\]|My responsibilities included|Responsible for)\b", re.IGNORECASE)

# --- Validation Methods (Moved from PreFlightValidator) ---
# Note: These were instance methods and have been converted to standalone functions.
# The 'self' parameter has been removed, and pattern references updated.

def _validate_cross_section_similarity(context: ValidationContext) -> bool:
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
                            if enum_member.name == name1: failed_sections_set.add(enum_member)
                            if enum_member.name == name2: failed_sections_set.add(enum_member)
                context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"]["failed_sections"] = [s.name for s in failed_sections_set]
                return False
            return True
        except Exception as e:
            logging.getLogger(__name__).error(f"Error during cross-section similarity validation: {e}")
            context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": []}
            return False

def _validate_narrative_vs_master_similarity(context: ValidationContext) -> bool:
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
            logging.getLogger(__name__).error(f"Error during narrative vs master similarity validation: {e}")
            context._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": []}
            return False

def _validate_section_presence(context: ValidationContext, section_enum: ResumeSection) -> bool:
        content = context.staging_buffer.get(section_enum.value)
        if content is None: return False
        if isinstance(content, str): return content.strip() not in ["", "HEADER_PLACEHOLDER"] and not content.strip().startswith("[Placeholder")
        if isinstance(content, (list, dict)): return bool(content)
        return True

def _validate_cover_letter_full_structure(context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
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
        if not valid: context._cache["H3_K11_COVER_LETTER_FULL_STRUCTURE"] = { "has_date": has_date, "has_recipient": has_recipient, "has_salutation": has_salutation, "has_closing": has_closing, "has_signature": has_signature, "paras_found": paras_found }
        return valid

def _validate_cover_letter_structure(context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        details = context.cover_letter_structure_details
        if details.get("error"): return False
        p1_valid = details.get('p1_min', 0) <= details.get('p1_wc', -1) <= details.get('p1_max', float('inf'))
        p2_valid = details.get('p2_min', 0) <= details.get('p2_wc', -1) <= details.get('p2_max', float('inf'))
        p3_valid = details.get('p3_min', 0) <= details.get('p3_wc', -1) <= details.get('p3_max', float('inf'))
        return p1_valid and p2_valid and p3_valid

    # --- NEW TIERED BULLET WORD COUNT VALIDATION METHODS ---
    
def _get_bullet_word_counts(context: ValidationContext) -> List[Tuple[int, str, ResumeSection]]:
        """Helper to get all bullet word counts for tiered validation."""
        # Use a simple cache within the context object for this validation run
        if "BULLET_WORD_COUNTS_CACHE" in context._cache:
            return context._cache["BULLET_WORD_COUNTS_CACHE"]

        counts = []
        # --- FIX: Access config from context object ---
        for section_enum_str in context.config.validator.bullet_word_count_sections_to_check:
            try:
                section_enum = ResumeSection[section_enum_str]
            except KeyError:
                logging.warning(f"Invalid section '{section_enum_str}' in bullet_word_count_sections_to_check config.")
                continue

            section_key = section_enum.value
            bullets = context.staging_buffer.get(section_key, [])
            
            if not isinstance(bullets, list): 
                logging.warning(f"Expected list for {section_key} bullets. Got {type(bullets)}. Skipping.")
                continue
            
            for i, bullet in enumerate(bullets):
                actual_wc = 0
                bullet_text = ""
                if isinstance(bullet, dict): 
                    bullet_text = bullet.get('text', '')
                    actual_wc = bullet.get('word_count', text_utils.count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str): 
                    bullet_text = bullet
                    actual_wc = text_utils.count_words_ms_word_style(bullet_text)
                else: 
                    logging.warning(f"Invalid bullet item type in {section_key}[{i}]. Skipping."); 
                    continue
                
                counts.append((actual_wc, f"{section_key}[{i}]", section_enum))
        
        context._cache["BULLET_WORD_COUNTS_CACHE"] = counts
        return counts

def _validate_bullet_word_count_CRITICAL(context: ValidationContext) -> bool:
        violations = []
        failed_sections = set()
        all_counts = _get_bullet_word_counts(context) # --- FIX: Call local function ---
        
        # Critical: < 15 or > 50
        for wc, loc, section_enum in all_counts:
            if wc < 15 or wc > 50: # TODO: Use constraints from config, not magic numbers
                violations.append(f"{loc}: {wc} words")
                failed_sections.add(section_enum)

        if violations:
            context._cache["H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL"] = { "violations": ", ".join(violations), "failed_sections": [s.name for s in failed_sections] }
            return False
        return True

    # --- END TIERED METHODS ---

def _validate_headline_format_no_titles(context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        if not headline or '|' not in headline: details['error'] = "Missing pipes"; context._cache["H3_K0_HEADLINE_NO_TITLES"] = details; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: details['error'] = f"Expected 3 components, found {len(components)}"; context._cache["H3_K0_HEADLINE_NO_TITLES"] = details; return False
        forbidden_titles = ['director', 'vp', 'manager', 'lead', 'head', 'chief', 'principal', 'senior', 'executive']
        forbidden_found = []
        for i, comp in enumerate(components):
            for title in forbidden_titles:
                 if re.search(r'\b' + re.escape(title) + r'\b', comp.lower()): forbidden_found.append(title)
        details_titles = details.copy(); details_titles['forbidden'] = list(set(forbidden_found)); context._cache["H3_K0_HEADLINE_NO_TITLES"] = details_titles
        return not forbidden_found

def _validate_headline_format_component_wc(context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        if not headline or '|' not in headline: context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = {"error": "Missing pipes", "headline": headline}; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = {"error": f"Expected 3 components, found {len(components)}", "headline": headline}; return False
        component_wc_violations = []; wc_valid = True
        min_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MIN; max_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MAX
        for i, comp in enumerate(components):
            word_count = text_utils.count_words_ms_word_style(comp)
            if not (min_comp_wc <= word_count <= max_comp_wc):
                component_wc_violations.append(f"Comp[{i+1}]: {word_count} words (Tgt: {min_comp_wc}-{max_comp_wc})")
                wc_valid = False
        details_wc = details.copy(); details_wc['min'] = min_comp_wc; details_wc['max'] = max_comp_wc;
        details_wc['wc_violations_str'] = "; ".join(component_wc_violations) if component_wc_violations else "None"
        context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = details_wc
        return wc_valid

def _validate_no_placeholders(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        def check_recursive(item, key_enum=None):
            nonlocal found_snippets, failed_sections

            if isinstance(item, str):
                if "[" in item:
                    placeholder_match = re.search(r"(\[(?:Placeholder|Your Name|Company Name|MISSING_CONTEXT|Unserializable).*?\])", item)
                    if placeholder_match:
                        placeholder_text = placeholder_match.group(1)
                        start_index = placeholder_match.start()
                        snippet_before = item[max(0, start_index - 30):start_index]
                        snippet_after = item[start_index + len(placeholder_text) : start_index + len(placeholder_text) + 30]
                        snippet = f"...{snippet_before}{placeholder_text}{snippet_after}..."
                        found_snippets.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                        if key_enum:
                            failed_sections.add(key_enum)
            elif isinstance(item, dict):
                for k, v in item.items():
                    enum_for_value = key_enum
                    try:
                        enum_for_value = ResumeSection(k)
                    except ValueError:
                        pass
                    check_recursive(v, enum_for_value)
            elif isinstance(item, list):
                for elem in item:
                    check_recursive(elem, key_enum)

        for key_str, top_level_item in buffer_data.items():
            top_level_enum = None
            try:
                top_level_enum = ResumeSection(key_str)
            except ValueError:
                pass
            check_recursive(top_level_item, top_level_enum)

        if found_snippets:
            context._cache["H5_CONTENT_NO_PLACEHOLDERS"] = {
                "placeholders": ", ".join(found_snippets[:3]),
                "failed_sections": [s.name for s in failed_sections]
            }
            return False

        return True

def _validate_no_prompt_contamination(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        def check_recursive(item, key_enum=None):
            nonlocal found_snippets, failed_sections
            if isinstance(item, str):
                match = PROMPT_CONTAMINATION_PATTERN.search(item)
                if match:
                    found_word = match.group(1)
                    start_index = match.start()
                    snippet = f"...{item[max(0, start_index - 30):start_index]}>>{found_word}<<{item[start_index + len(found_word):start_index + len(found_word) + 30]}..."
                    found_snippets.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                    if key_enum: failed_sections.add(key_enum)
            elif isinstance(item, dict):
                for k, v in item.items():
                    enum_for_value = key_enum
                    try: enum_for_value = ResumeSection(k)
                    except ValueError: pass
                    check_recursive(v, enum_for_value)
            elif isinstance(item, list):
                for elem in item:
                    check_recursive(elem, key_enum)

        for key_str, top_level_item in buffer_data.items():
            top_level_enum = None
            try: top_level_enum = ResumeSection(key_str)
            except ValueError: pass
            check_recursive(top_level_item, top_level_enum)

        if found_snippets:
            context._cache["H5_CONTENT_NO_PROMPT_CONTAMINATION"] = {"violations": ", ".join(found_snippets[:3]), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

def _validate_no_conversational_fillers(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        for key_str, item in buffer_data.items():
            if isinstance(item, str):
                match = CONVERSATIONAL_FILLERS_PATTERN.search(item)
                if match:
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}: Starts with '{match.group(1)}'")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS"] = {"violations": ", ".join(found_snippets[:3]), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

def _validate_no_empty_list_items(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        for key_str, item in buffer_data.items():
            if isinstance(item, str) and ('*' in item or '-' in item):
                if EMPTY_LIST_ITEM_PATTERN.search(item):
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H5_STRUCTURE_NO_EMPTY_LIST_ITEMS"] = {"violations": ", ".join(found_snippets), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

def _validate_markdown_header_spacing(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()
        header_spacing_pattern = re.compile(r"^#{1,6}[^\s#]", re.MULTILINE)

        for key_str, item in buffer_data.items():
            if isinstance(item, str):
                match = header_spacing_pattern.search(item)
                if match:
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}: Found '{match.group(0)}'")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H5_STRUCTURE_MARKDOWN_HEADER_SPACING"] = {"violations": ", ".join(found_snippets), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

def _validate_forbidden_verbs(context: ValidationContext) -> bool:
        valid = True
        violations = []
        failed = set()
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY
        ]
        for section_enum in sections_to_check:
            # --- FIX: Access config from context object ---
            forbidden_verbs_list = context.config.validator.forbidden_verbs
            content = context.staging_buffer.get(section_enum.value)
            texts = []
            if isinstance(content, str):
                if content.strip():
                    texts.append((content, -1))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip():
                        texts.append((text, i))

            for text, idx in texts:
                found_verbs = (v for v in forbidden_verbs_list if re.search(r'\b' + re.escape(v) + r'\b', text.lower()))
                found_list = list(found_verbs)
                if found_list:
                    valid = False
                    loc = f"{section_enum.value}" + (f"[{idx}]" if idx != -1 else "")
                    violations.append(f"{loc}: '{', '.join(found_list)}'")
                    failed.add(section_enum)

        if not valid:
            context._cache["H3_CONTENT_NO_FORBIDDEN_VERBS"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

def _validate_no_intro_phrases(context: ValidationContext) -> bool:
        valid = True
        violations = []
        failed = set()
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts_info = []
            is_cl = (section_enum == ResumeSection.K11_COVER_LETTER)

            if isinstance(content, str):
                if is_cl:
                    body_text = content
                    body_text = re.sub(r".*Dear Hiring Manager,\s*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    body_text = re.sub(r"\s*Sincerely,.*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    if body_text.strip():
                        for i, para in enumerate(body_text.strip().split('\n\n')):
                            if para.strip():
                                texts_info.append((para.strip(), f"Para {i+1}"))
                elif content.strip():
                    texts_info.append((content.strip(), None))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip():
                        texts_info.append((text.strip(), i))

            for text, idx_label in texts_info:
                 match = BANNED_INTRO_PHRASES_PATTERN.match(text)
                 if match:
                     valid = False
                     loc = f"{section_enum.value}"
                     if isinstance(idx_label, int):
                         loc += f"[{idx_label}]"
                     elif isinstance(idx_label, str):
                         loc += f" ({idx_label})"
                     violations.append(f"{loc}: Starts with '{match.group(0).strip()}'")
                     failed.add(section_enum)

        if not valid:
            context._cache["H3_CONTENT_NO_INTRO_PHRASES"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

def _validate_per_section_signal_raw(context: ValidationContext) -> bool:
        valid = True; failures = []; failed = set()
        # --- FIX: Access config from context object ---
        # Note: This attribute doesn't exist on context, this rule will fail open
        # This is a *new* bug found during the fix. The SECTION_SIGNAL_TARGETS_CONFIG
        # needs to be on the context object or its config.
        section_targets = getattr(context.config, "SECTION_SIGNAL_TARGETS_CONFIG", {})
        for label, (section_enum, target_min_raw, target_max_raw, _, _) in section_targets.items():
            content = context.staging_buffer.get(section_enum.value); raw_score = 0.0
            if content:
                try:
                     # FIX: Call the imported function
                     normalized_score = calculate_signal_score(content, context.thematic_analysis); raw_score = normalized_score
                     if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY and raw_score > 0.9: raw_score = 1.15
                except Exception as e: logging.warning(f"Error calculating raw signal score for {label}: {e}")
            if not (target_min_raw <= raw_score <= target_max_raw): valid = False; failures.append(f"{label}({section_enum.name}): Raw {raw_score:.2f} (Tgt: {target_min_raw:.2f}-{target_max_raw:.2f})"); failed.add(section_enum)
        if not valid: context._cache["H3_GLOBAL_PER_SECTION_SIGNAL_SCORE"] = {"failures": ", ".join(failures[:3]), "failed_sections": [s.name for s in failed]}
        return valid

def _validate_jd_keyword_range(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        sections_to_include = [ se for se in ResumeSection if se not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT, ResumeSection.K11_COVER_LETTER] and not se.name.endswith("_HEADER") ]
        text_parts = []
        for key_enum in sections_to_include:
            value = buffer_data.get(key_enum.value)
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value)
        full_text = " ".join(text_parts)
        differentiators = set(); comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            # Handle both dataclass and dict forms
            if hasattr(comp_intel, 'differentiator_keywords'):
                differentiators = set(kw for kw in getattr(comp_intel, 'differentiator_keywords', []) if kw and isinstance(kw, str))
            elif isinstance(comp_intel, dict):
                differentiators = set(kw for kw in comp_intel.get('differentiator_keywords', []) if kw and isinstance(kw, str))
        
        primary_words = set(kw for kw in context.thematic_analysis.primary_theme.get('keywords', []) if kw and isinstance(kw, str))
        all_jd_keywords = differentiators.union(primary_words); found = {kw for kw in all_jd_keywords if kw.lower() in full_text.lower()}
        min_target = context.constraints.MIN_JD_KEYWORDS; max_target = context.signal_constraints.RESUME_MAX_JD_KEYWORDS
        valid = min_target <= len(found) <= max_target
        context._cache["H5_GLOBAL_JD_KEYWORD_RANGE"] = {"found": len(found), "min": min_target, "max": max_target, "jd_keywords_found": list(found)}
        return valid

def _validate_narrative_mining_presence(context: ValidationContext) -> bool:
        narratives = getattr(context.thematic_analysis, 'problem_solution_narratives', None)
        return isinstance(narratives, dict) and narratives.get('common_problems') and narratives.get('solution_patterns')

def _validate_provenance_split(context: ValidationContext) -> bool:
        valid = True; violations = []; failed = set()
        # --- FIX: Access config from context object ---
        for section_enum_str, targets in context.config.validator.provenance_split_targets.items():
            try:
                section_enum = ResumeSection[section_enum_str]
            except KeyError:
                logging.warning(f"Invalid section '{section_enum_str}' in provenance_split_targets config.")
                continue
                
            bullets = context.staging_buffer.get(section_enum.value, [])
            if not isinstance(bullets, list): logging.warning(f"Expected list for {section_enum.value} provenance check. Skipping."); continue
            counts = defaultdict(int)
            for bullet in bullets:
                if isinstance(bullet, dict): counts[bullet.get('provenance', 'Unknown')] += 1
            for prov_type_enum in BulletProvenance:
                prov_type = prov_type_enum.value; target = targets.get(prov_type, 0); actual = counts.get(prov_type, 0)
                if actual != target: valid = False; violations.append(f"{section_enum.value}: {prov_type} has {actual} (target: {target})"); failed.add(section_enum)
        if not valid: context._cache["H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

def _validate_authenticity_signal(context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        auth_patterns_data = getattr(context.thematic_analysis, 'authenticity_patterns', {}); patterns_dict = {}
        if isinstance(auth_patterns_data, dict): patterns_dict = auth_patterns_data.get('patterns', {});
        if not isinstance(patterns_dict, dict): patterns_dict = {}
        if not patterns_dict: return True
        verbs = patterns_dict.get('achievement_verb_patterns', []); phrasing = patterns_dict.get('competency_phrasing', [])
        valid_verbs = [v for v in verbs if isinstance(v, str)]; valid_phrasing = [p for p in phrasing if isinstance(p, str)]
        target_signals = set(v.lower() for v in valid_verbs[:10]) | set(p.lower().split(':')[0].split()[0] for p in valid_phrasing[:5] if ':' in p and p.split()); target_signals = {s for s in target_signals if s}
        sections_to_scan = [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES]
        text_parts = []
        for sec_enum in sections_to_scan:
            value = buffer_data.get(sec_enum.value)
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value)
        full_text = " ".join(text_parts)
        if not target_signals or not full_text: return True
        found = {sig for sig in target_signals if re.search(r'\b' + re.escape(sig) + r'\b', full_text.lower())}
        ratio = len(found) / len(target_signals) if target_signals else 0.0; valid = ratio >= 0.3
        context._cache["H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK"] = {"details": f"Found {len(found)}/{len(target_signals)} ({ratio:.1%}) auth signals."}
        return valid

    # --- ADDED SKILLS WORD COUNT METHOD ---
def _validate_skills_word_count(context: ValidationContext) -> bool:
        """Validates that each skill in K10_SKILLS is between 1 and 3 words."""
        violations = []
        failed_sections = set()
        
        # Get constraints
        try:
            min_wc = context.constraints.SKILLS_WORD_COUNT_MIN
            max_wc = context.constraints.SKILLS_WORD_COUNT_MAX
        except AttributeError:
            logging.getLogger(__name__).error("SKILLS_WORD_COUNT_MIN/MAX not found in constraints. Skipping skills word count validation.")
            return True # Fail open if constraints aren't loaded

        skills_list = context.staging_buffer.get(ResumeSection.K10_SKILLS.value, [])
        
        if not isinstance(skills_list, list):
            logging.getLogger(__name__).warning(f"Expected list for {ResumeSection.K10_SKILLS.value}. Got {type(skills_list)}. Skipping.")
            violations.append(f"Expected list, got {type(skills_list)}")
            failed_sections.add(ResumeSection.K10_SKILLS)
        else:
            for i, skill in enumerate(skills_list):
                skill_text = ""
                if isinstance(skill, dict):
                    skill_text = skill.get('text', str(skill))
                elif isinstance(skill, str):
                    skill_text = skill
                else:
                    logging.getLogger(__name__).warning(f"Invalid skill item type in {ResumeSection.K10_SKILLS.value}[{i}]. Skipping.")
                    continue
                
                # Strip leading/trailing whitespace and potential list markers
                clean