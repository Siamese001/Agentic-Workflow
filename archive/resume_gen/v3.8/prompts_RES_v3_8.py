# File: prompts_RES_v3.8.py
# Version: 18.0 - Full V2/V3.8 Agentic Migration
# Prompt Templates module for Resume Workflow
# Contains all *logic* for loading and formatting prompts from prompts.json
# V3.8 UPDATE: All V1 prompt logic from ArtistGenerator has been migrated
# here. This module is now the single source of truth for all prompt context.

import re
import json
import logging
import os
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# --- REFACTOR: Import global CONFIG ---
from config_RES_v3_8 import CONFIG
# --- END REFACTOR ---

# Import models needed for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models_RES import RAGMission, MasterResumeIndex, ThematicAnalysis, ValidationResult, ResumeSection
    from config_RES_v3_8 import ContentConstraintsConfig, CompetitiveAnalysisConfig

# --- REFACTOR: Load 'Recipe Book' (prompts.json) from global CONFIG ---
try:
    PROMPT_TEMPLATES = CONFIG.prompts.prompts
    if not PROMPT_TEMPLATES:
        raise ValueError("PROMPT_TEMPLATES dictionary from CONFIG is empty.")
    logging.info(f"✓ Successfully loaded prompts from CONFIG.prompts.prompts")
except Exception as e:
    logging.critical(f"FATAL: Could not load prompts from CONFIG: {e}")
    PROMPT_TEMPLATES = {} # Fallback to prevent crash, will error at runtime
# -----------------------------------------------------------------

def _get_prompt_template(key: str) -> str:
    """Helper to safely get a prompt template."""
    template = PROMPT_TEMPLATES.get(key)
    if not template:
        logging.error(f"Prompt template key '{key}' not found in prompts.json!")
        raise KeyError(f"Prompt template key '{key}' not found in prompts.json!")
    return template

# ==============================================================================
# V2 ARCHITECTURE: CRL INTEGRATION HELPERS
# ==============================================================================

def build_crl_context_for_section(
    section_name: str,
    thematic_analysis: 'ThematicAnalysis',
    enriched_scaffold: Dict,
    **kwargs
) -> Dict[str, Any]:
    """
    V2 INTEGRATION: Builds context dictionary for ContextRelayLayer.
    
    This function centralizes context building logic that the CRL can call.
    Returns a dictionary of context variables ready for prompt formatting.
    
    Args:
        section_name: Section identifier (e.g., "K0_HEADLINE")
        thematic_analysis: ThematicAnalysis object
        enriched_scaffold: Enriched data scaffold
        **kwargs: Additional context (company_name, job_description, etc.)
        
    Returns:
        Dictionary of context variables
    """
    # Dispatch to specific context builder based on section type
    if "HEADLINE" in section_name:
        return _build_headline_context_dict(thematic_analysis, enriched_scaffold, **kwargs)
    elif "EXECUTIVE_SUMMARY" in section_name:
        return _build_executive_summary_context_dict(thematic_analysis, enriched_scaffold, **kwargs)
    elif "COVER_LETTER" in section_name:
        return _build_cover_letter_context_dict(thematic_analysis, enriched_scaffold, **kwargs)
    elif "BULLETS" in section_name:
        # --- V3.8 FIX: Use new V2 bullet context builder ---
        return _build_bullets_context_dict(thematic_analysis, enriched_scaffold, section_name, **kwargs)
    elif "NARRATIVE" in section_name:
        # --- V3.8 FIX: Use new V2 narrative context builder ---
        return _build_narrative_context_dict(thematic_analysis, enriched_scaffold, section_name, **kwargs)
    elif "COMPETENCIES" in section_name:
        # --- V3.8 FIX: Use new V2 competencies context builder ---
        return _build_competencies_context_dict(thematic_analysis, enriched_scaffold, section_name, **kwargs)
    elif "OVERVIEW" in section_name:
        # --- V3.8 FIX: Use new V2 overview context builder ---
        return _build_overview_context_dict(thematic_analysis, enriched_scaffold, section_name, **kwargs)
    elif "SKILLS" in section_name:
        return _build_skills_context_dict(thematic_analysis, enriched_scaffold, **kwargs)
    else:
        # Fallback for simple copy/header sections (though they won't call this)
        logging.warning(f"build_crl_context_for_section called for non-generation section: {section_name}")
        return {"section_name": section_name}


def _build_headline_context_dict(
    thematic_analysis: 'ThematicAnalysis', 
    scaffold: Dict,
    **kwargs
) -> Dict:
    """Build context dictionary for headline generation."""
    # --- REFACTOR: Source constraints from global CONFIG ---
    constraints = CONFIG.constraints
    # --- END REFACTOR ---

    # Extract keywords from positioning directives
    positioning = getattr(thematic_analysis, 'positioning_directives', {})
    resume_keywords = positioning.get('resume_keywords', []) if isinstance(positioning, dict) else []
    keywords_str = ', '.join(resume_keywords[:8]) if resume_keywords else "strategic leadership, innovation, growth"
    
    # Get differentiators
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    differentiators = []
    if comp_intel and hasattr(comp_intel, 'differentiator_keywords'):
        differentiators = comp_intel.differentiator_keywords[:5]
    
    # Get primary theme
    primary_theme = getattr(thematic_analysis, 'primary_theme', {})
    primary_theme_name = primary_theme.get('name', 'Key Expertise') if isinstance(primary_theme, dict) else 'Key Expertise'
    
    return {
        "company_name": kwargs.get('company_name', 'Target Company'),
        "primary_theme": primary_theme_name,
        "differentiators_str": ', '.join(differentiators),
        "keywords_str": keywords_str,
        "min_wc": constraints.HEADLINE_WORD_COUNT_MIN,
        "max_wc": constraints.HEADLINE_WORD_COUNT_MAX,
        "comp_min_wc": constraints.HEADLINE_COMPONENT_WORDS_MIN,
        "comp_max_wc": constraints.HEADLINE_COMPONENT_WORDS_MAX
    }


def _build_executive_summary_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    **kwargs
) -> Dict:
    """Build context dictionary for executive summary."""
    import json

    # --- REFACTOR: Source constraints & config from global CONFIG ---
    constraints = CONFIG.constraints
    config = CONFIG
    # --- END REFACTOR ---
    
    role_classification = getattr(thematic_analysis, 'role_classification', {})
    role_archetype = role_classification.get('role_archetype', 'Experienced Professional') if isinstance(role_classification, dict) else 'Experienced Professional'
    archetype_map = {
        "Executive_Leader": "an executive leader",
        "Technical_IC": "a hands-on technical expert",
        "Post-Sales_Customer_Success": "a customer success leader",
        "Pre-Sales_GTM": "a pre-sales GTM strategist",
        "Product_Management": "a product management professional"
    }
    archetype_instruction = f"Position the candidate as {archetype_map.get(role_archetype, 'an experienced professional')}."
    
    # Get problem/solution
    problem_solution = getattr(thematic_analysis, 'problem_solution_narratives', {})
    problem = problem_solution.get('problem', 'current business challenges') if isinstance(problem_solution, dict) else 'current business challenges'
    solution = problem_solution.get('solution', 'strategic solutions') if isinstance(problem_solution, dict) else 'strategic solutions'
    
    # Get differentiators
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    max_diff = config.signal_constraints.K1_MAX_DIFFERENTIATORS if hasattr(config, 'signal_constraints') else 4
    differentiators = []
    if comp_intel and hasattr(comp_intel, 'differentiator_keywords'):
        differentiators = comp_intel.differentiator_keywords[:max_diff]
    
    # Get primary theme
    primary_theme = getattr(thematic_analysis, 'primary_theme', {})
    primary_theme_name = primary_theme.get('name', 'key skills') if isinstance(primary_theme, dict) else 'key skills'
    
    # --- REFACTOR: Added missing context items ---
    achievement_patterns = getattr(thematic_analysis, 'authenticity_patterns', {}).get('patterns', {})
    achievement_patterns_str = ", ".join(achievement_patterns.get('achievement_verb_patterns', ['measurable outcomes']))
    
    positioning_directives = getattr(thematic_analysis, 'positioning_directives', {})
    keywords_str = ", ".join(positioning_directives.get('resume_keywords', [])[:8])
    # --- END REFACTOR ---
    
    return {
        "company_name": kwargs.get('company_name', 'Target Company'),
        "primary_theme": primary_theme_name,
        "secondary_themes_str": ', '.join([t.get('name', '') for t in getattr(thematic_analysis, 'secondary_themes', [])[:3]]),
        "differentiators_str": ', '.join(differentiators),
        "achievement_patterns_str": achievement_patterns_str, # REFACTORED
        "keywords_str": keywords_str, # REFACTORED
        "archetype_instruction": archetype_instruction,
        "problem": problem,
        "solution": solution,
        "experience_snippets": json.dumps(scaffold.get('experience_sections', [])[:2], indent=2),
        "min_sc": constraints.EXECUTIVE_SUMMARY_SENTENCE_COUNT_MIN,
        "max_sc": constraints.EXECUTIVE_SUMMARY_SENTENCE_COUNT_MAX,
        "min_wc": constraints.EXECUTIVE_SUMMARY_WORD_COUNT_MIN,
        "max_wc": constraints.EXECUTIVE_SUMMARY_WORD_COUNT_MAX
    }


def _build_skills_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    **kwargs
) -> Dict:
    """Build context dictionary for skills list."""
    try:
        # Get data from ThematicAnalysis
        primary_theme_name = "N/A"
        key_tech_list = []
        req_skills_list = []

        if thematic_analysis:
            # Get Primary Theme Name and Keywords (as Key Technologies)
            if thematic_analysis.primary_theme and isinstance(thematic_analysis.primary_theme, dict):
                primary_theme_name = thematic_analysis.primary_theme.get('name', 'N/A')
                key_tech_list = thematic_analysis.primary_theme.get('keywords', [])
            
            # Get Secondary Theme Keywords (as Required Skills)
            if thematic_analysis.secondary_themes and isinstance(thematic_analysis.secondary_themes, list) and len(thematic_analysis.secondary_themes) > 0:
                # Assuming first secondary theme is most relevant for skills
                req_skills_list = thematic_analysis.secondary_themes[0].get('keywords', [])

        # --- REFACTOR: Source job_description from kwargs ---
        job_description = kwargs.get('job_description', '')
        # --- END REFACTOR ---

        # Return the four keys the prompt expects
        return {
            "job_description": job_description[:2000],  # Truncate for prompt safety
            "primary_theme": primary_theme_name,
            "key_technologies": ", ".join(key_tech_list),
            "required_skills": ", ".join(req_skills_list)
        }

    except Exception as e:
        logging.error(f"Error building K10 context: {e}")
        # Return empty strings to make the failure obvious in the prompt
        return {
            "job_description": "",
            "primary_theme": "",
            "key_technologies": "",
            "required_skills": ""
        }


def _build_cover_letter_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    **kwargs
) -> Dict:
    """Build context dictionary for cover letter."""
    from datetime import datetime
    
    # --- REFACTOR: Source constraints and master_resume from kwargs/CONFIG ---
    constraints = CONFIG.constraints
    master_resume = kwargs.get('master_resume', {})
    if not master_resume:
        logging.warning("master_resume not found in kwargs for cover letter context")
    # --- END REFACTOR ---

    # Get problem/solution
    problem_solution = getattr(thematic_analysis, 'problem_solution_narratives', {})
    problem = problem_solution.get('problem', 'strategic challenges') if isinstance(problem_solution, dict) else 'strategic challenges'
    solution = problem_solution.get('solution', 'innovative approaches') if isinstance(problem_solution, dict) else 'innovative approaches'
    
    # Extract company mission from thematic analysis
    company_mission = "drive innovation and strategic growth"
    if hasattr(thematic_analysis, 'primary_theme'):
        theme = thematic_analysis.primary_theme
        if isinstance(theme, dict) and 'name' in theme:
            company_mission = f"advance {theme['name'].lower()}"
    
    # Build strengths from top differentiators
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    differentiators = []
    if comp_intel and hasattr(comp_intel, 'differentiator_keywords'):
        differentiators = comp_intel.differentiator_keywords[:5]
    strengths_str = ', '.join(differentiators) if differentiators else "strategic leadership, innovation, operational excellence"
    
    # Get primary theme
    primary_theme = getattr(thematic_analysis, 'primary_theme', {})
    primary_theme_name = primary_theme.get('name', 'key requirements') if isinstance(primary_theme, dict) else 'key requirements'
    
    # Get experience snippets
    experience_snippets = _extract_experience_snippets_for_cl(scaffold, master_resume)
    
    # Get signature
    expected_signature = get_expected_signature(master_resume)
    
    return {
        "company_name": kwargs.get('company_name', 'Target Company'),
        "job_title": kwargs.get('job_title', 'Target Role'),
        "company_mission": company_mission,
        "primary_theme": primary_theme_name,
        "problems_str": problem,
        "solutions_str": solution,
        "strengths_str": strengths_str,
        "differentiators_str": ', '.join(differentiators),
        "experience_snippets": experience_snippets,
        "current_date": datetime.now().strftime("%B %d, %Y"),
        "p1_min_wc": constraints.COVER_LETTER_P1_WORD_COUNT_MIN,
        "p1_max_wc": constraints.COVER_LETTER_P1_WORD_COUNT_MAX,
        "p2_min_wc": constraints.COVER_LETTER_P2_WORD_COUNT_MIN,
        "p2_max_wc": constraints.COVER_LETTER_P2_WORD_COUNT_MAX,
        "p3_min_wc": constraints.COVER_LETTER_P3_WORD_COUNT_MIN,
        "p3_max_wc": constraints.COVER_LETTER_P3_WORD_COUNT_MAX,
        "expected_signature": expected_signature
    }


def _build_narrative_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    section_name: str,
    **kwargs
) -> Dict:
    """
    Build context dictionary for narrative generation.
    LOGIC MIGRATED FROM artist_RES_v2.py
    """
    from models_RES import HopExecutionError, ResumeSection
    
    # --- REFACTOR: Source dependencies from kwargs/CONFIG ---
    master_resume = kwargs.get('master_resume', {})
    if not master_resume:
        logging.warning("master_resume not found in kwargs for narrative context")
    
    config = CONFIG
    constraints = CONFIG.constraints
    spec = kwargs.get('spec', {}) # Spec should be passed by CRL
    if not spec:
        raise HopExecutionError(f"Missing 'spec' in kwargs for narrative context {section_name}")
    # --- END REFACTOR ---
    
    extra_args = spec.get("extra_args", {})
    if not isinstance(extra_args, dict):
        raise HopExecutionError(f"Invalid 'extra_args' format in spec for narrative generation.")

    company_match = extra_args.get("company_match")
    if not company_match:
        raise HopExecutionError(f"Missing 'company_match' in extra_args for narrative generation.")

    # Get narrative config from artist_specs.json (loaded via CONFIG)
    narrative_config = config.artist_specs.get("narrative_config", {})
    
    # Convert string section_name to enum
    try:
        # Use the key from extra_args, which is guaranteed to be in narrative_config
        section_key = extra_args.get("section_enum") 
        if not section_key or section_key not in narrative_config:
             raise HopExecutionError(f"Missing/invalid config for narrative generation: {section_key}")
        section_enum = ResumeSection[section_key]
    except KeyError:
        raise HopExecutionError(f"Invalid section_enum '{section_key}' for narrative context")
    
    title = "Default Title"
    exp_section = next((exp for exp in master_resume.get('professional_experience', []) 
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
    
    # Get differentiators
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    rag_keywords = []
    if comp_intel and hasattr(comp_intel, 'differentiator_keywords'):
        rag_keywords = comp_intel.differentiator_keywords[:5]
    
    target_sc = 3 # Default narrative sentence count

    section_config = narrative_config[section_key]
    
    # --- FIX: Read constraints dynamically from the constraints object ---
    min_wc_key = f"{section_key}_WORD_COUNT_MIN"
    max_wc_key = f"{section_key}_WORD_COUNT_MAX"
    
    min_wc = getattr(constraints, min_wc_key, 40)
    max_wc = getattr(constraints, max_wc_key, 60)
    # --- END FIX ---
    
    combined_signals = list(set(rag_keywords + section_config.get("rag_signals", [])))[:7]
    focus_instruction = section_config.get("focus", "Focus on key achievements.")
    k0_themes = section_config.get("k0_themes", [])

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


def _build_bullets_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    section_name: str,
    **kwargs
) -> Dict:
    """
    Build context dictionary for V2 bullet generation.
    This replaces the complex V1 logic with a single, robust prompt context.
    LOGIC MIGRATED FROM artist_RES_v2.py
    """
    from models_RES import HopExecutionError, ResumeSection
    
    master_resume = kwargs.get('master_resume', {})
    spec = kwargs.get('spec', {})
    constraints = CONFIG.constraints
    
    extra_args = spec.get("extra_args", {})
    company_name = extra_args.get("company_name", "Unknown Company")
    is_competencies = extra_args.get("is_competencies", False)
    
    # Get Provenance Targets
    provenance_targets = constraints.provenance_split_targets.get(section_name, {})
    verbatim_count = provenance_targets.get('Verbatim', 2)
    customized_count = provenance_targets.get('Customized', 3)
    synthetic_count = provenance_targets.get('Synthetic', 2)
    total_bullets = verbatim_count + customized_count + synthetic_count

    # Get Master Bullets
    master_bullets_source = []
    if is_competencies:
         master_bullets_source_raw = master_resume.get("strategic_and_technical_competencies", [])
         if isinstance(master_bullets_source_raw, list):
             master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
    else:
         exp_section = next((exp for exp in master_resume.get('professional_experience', []) if company_name in exp.get('company', '')), None)
         if not exp_section: raise HopExecutionError(f"Master data not found for '{company_name}' needed by {section_name}")
         master_bullets_key = "bullet_pool" if "bullet_pool" in exp_section else "highlights"
         master_bullets_source_raw = exp_section.get(master_bullets_key, [])
         if isinstance(master_bullets_source_raw, list):
              master_bullets_source = [str(item) for item in master_bullets_source_raw if isinstance(item, str)]
    
    if not master_bullets_source:
        raise HopExecutionError(f"No master bullets/highlights found for {company_name}")

    master_bullets_str = "\n".join([f"- {b}" for b in master_bullets_source])

    # Get Thematic Context
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

    return {
        "company_name": company_name,
        "job_description": kwargs.get('job_description', '')[:1000],
        "primary_theme": primary_theme,
        "context_keywords_str": ", ".join(context_keywords),
        "master_bullets_str": master_bullets_str,
        "verbatim_count": verbatim_count,
        "customized_count": customized_count,
        "synthetic_count": synthetic_count,
        "total_bullets": total_bullets,
        "min_wc": constraints.BULLETS_WORD_COUNT_MIN,
        "max_wc": constraints.BULLETS_WORD_COUNT_MAX,
    }

def _build_competencies_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    section_name: str,
    **kwargs
) -> Dict:
    """
    Build context dictionary for V2 competencies generation.
    This is identical to bullet generation, just with different args.
    """
    # Competencies are just a special case of bullets
    return _build_bullets_context_dict(thematic_analysis, scaffold, section_name, **kwargs)


def _build_overview_context_dict(
    thematic_analysis: 'ThematicAnalysis',
    scaffold: Dict,
    section_name: str,
    **kwargs
) -> Dict:
    """
    Build context dictionary for V2 overview generation.
    LOGIC MIGRATED FROM artist_RES_v2.py
    """
    from models_RES import HopExecutionError, ResumeSection
    
    constraints = CONFIG.constraints
    spec = kwargs.get('spec', {})
    drafts = kwargs.get('drafts', {})
    
    dependency_enum = spec.get("depends_on") # e.g., ResumeSection.K2_UNIFY_BULLETS
    if not dependency_enum or not isinstance(dependency_enum, ResumeSection):
         raise HopExecutionError(f"Invalid 'depends_on' spec for {section_name}")

    generated_bullets = drafts.get(dependency_enum)
    if not generated_bullets:
        raise HopExecutionError(f"Cannot generate overview for {section_name}: Dependency {dependency_enum.name} not found in drafts.")

    bullet_texts = []
    for i, bullet_data in enumerate(generated_bullets):
         text = ""
         if isinstance(bullet_data, dict):
             text = bullet_data.get('text', bullet_data.get('bullet_text', ''))
         elif isinstance(bullet_data, str):
             text = bullet_data
         if not text: logging.warning(f"Skipping empty/invalid bullet {i} for overview {section_name}"); continue
         bullet_texts.append(f"* {text.strip()}")
    if not bullet_texts: raise HopExecutionError(f"Cannot generate overview for {section_name}: All dependency bullets were invalid.")

    bullet_summary_input = "\n".join(bullet_texts)
    
    # Get word count constraints
    if section_name == "K2_UNIFY_OVERVIEW":
         min_wc = constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN
         max_wc = constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX
    elif section_name == "K3_IBM_OVERVIEW":
         min_wc = constraints.IBM_OVERVIEW_WORD_COUNT_MIN
         max_wc = constraints.IBM_OVERVIEW_WORD_COUNT_MAX
    else:
         logging.warning(f"No overview WC range explicitly defined for {section_name}. Using default (25-40).")
         min_wc, max_wc = (25, 40)

    # Get themes
    job_desc_lower = kwargs.get('job_description', '').lower()
    include_leadership_theme = any(kw in job_desc_lower for kw in ['lead', 'manage', 'director', 'vp', 'executive'])
    include_strategic_theme = any(kw in job_desc_lower for kw in ['strategy', 'roadmap', 'vision', 'partnership', 'alliance'])
    include_technical_theme = any(kw in job_desc_lower for kw in ['technical', 'architect', 'engineer', 'platform', 'cloud', 'ai', 'ml'])

    theme_instructions = []
    if include_leadership_theme: theme_instructions.append("- Leadership and team building aspects")
    if include_strategic_theme: theme_instructions.append("- Strategic planning and partnership elements")
    if include_technical_theme: theme_instructions.append("- Technical depth and platform expertise")

    theme_prompt_section = "**KEY THEMES TO INCORPORATE (if relevant and natural):**\n" + "\n".join(theme_instructions) if theme_instructions else ""

    return {
        "bullet_summary_input": bullet_summary_input,
        "theme_prompt_section": theme_prompt_section,
        "min_wc": min_wc,
        "max_wc": max_wc
    }


def _extract_experience_snippets_for_cl(scaffold: Dict, master_resume: Dict) -> str:
    """Extract experience snippets for cover letter."""
    snippets = []
    # Use scaffold first
    scaffold_exp = scaffold.get('experience_sections', [])
    if scaffold_exp:
        for exp in scaffold_exp[:2]:
            company = exp.get('company', '')
            bullets = exp.get('bullets', [])
            if bullets:
                first_bullet_text = bullets[0].get('bullet_text', '') if isinstance(bullets[0], dict) else str(bullets[0])
                snippets.append(f"At {company}: {first_bullet_text[:100]}...")
    
    # Fallback to master_resume if scaffold is empty
    if not snippets and master_resume:
        for exp in master_resume.get('professional_experience', [])[:2]:
            company = exp.get('company', '')
            highlights = exp.get('highlights', exp.get('bullet_pool', []))
            if highlights:
                first_highlight = str(highlights[0])
                snippets.append(f"At {company}: {first_highlight[:100]}...")

    return '\n'.join(snippets) if snippets else "Candidate has extensive experience in relevant areas."


def get_expected_signature(master_resume: Dict) -> str:
    """Get expected cover letter signature."""
    owner = master_resume.get('owner', {})
    contact = owner.get('contact', {}) # Corrected from 'header'
    
    name = owner.get('name', 'Candidate Name')
    email = contact.get('email', 'email@example.com')
    phone = contact.get('phone', '(555) 123-4567')
    linkedin = contact.get('linkedin', 'linkedin.com/in/profile')
    
    # --- REFACTOR: Use imported template ---
    # Load from the prompt dictionary, not config
    template = PROMPT_TEMPLATES.get("COVER_LETTER_SIGNATURE_TEMPLATE")
    if not template:
        # --- FIX: Use correct fallback from config ---
        template = CONFIG.COVER_LETTER_SIGNATURE_TEMPLATE
        if not template:
             template = "Sincerely,\n\n{name}\n{email}\n{phone}\n{linkedin}" # Absolute Fallback
    # --- END REFACTOR ---

    try:
        return template.format(name=name, email=email, phone=phone, linkedin=linkedin).strip()
    except Exception as e:
        logging.error(f"Failed to format COVER_LETTER_SIGNATURE_TEMPLATE: {e}")
        return f"Sincerely,\n\n{name}\n{email}\n{phone}\n{linkedin}"


# Helper functions for context building
def _extract_recent_achievements_text(scaffold: Dict, limit: int = 5) -> str:
    """Extract recent achievements from scaffold as formatted text."""
    experiences = scaffold.get('experience_sections', [])
    achievements = []
    
    for exp in experiences[:2]:  # Most recent 2 companies
        for bullet in exp.get('bullets', [])[:limit]:
            text_to_add = bullet.get('bullet_text', '') if isinstance(bullet, dict) else str(bullet)
            achievements.append(text_to_add)
    
    return '\n'.join(f"- {a}" for a in achievements[:limit] if a) if achievements else "Recent leadership in AI/ML platform development"

def _extract_experience_for_section_text(scaffold: Dict, section_name: str) -> str:
    """Extract relevant experience data for a section as formatted text."""
    experiences = scaffold.get('experience_sections', [])
    
    # Match section to company
    company_map = {
        "K2_UNIFY": "Unify",
        "K3_IBM": "IBM"
    }
    
    target_company = None
    for key, company in company_map.items():
        if key in section_name:
            target_company = company
            break
    
    if not target_company:
        return "Experience data for current role"
    
    for exp in experiences:
        if target_company.lower() in exp.get('company', '').lower():
            bullets = exp.get('bullets', [])
            bullet_texts = [b.get('bullet_text', '') if isinstance(b, dict) else str(b) for b in bullets[:10]]
            return '\n'.join(f"- {b_text}" for b_text in bullet_texts if b_text)
    
    return "Experience data for selected role"

def _extract_historical_context_text(scaffold: Dict, section_name: str) -> str:
    """Extract historical context for narratives."""
    return f"Historical context bridging past experience to current capabilities for {section_name}"

# ==============================================================================
# V2 ARCHITECTURE: CRITIQUE PROMPT BUILDERS
# ==============================================================================

def build_critique_prompt(
    draft: str,
    validation_results: List['ValidationResult'],
    strategy: str,
    focus: str,
    emphasis: str
) -> str:
    """
    V2 NEW: Builds prompt for LLM-based critique generation.
    Used by CritiqueTool when advanced critique is needed.
    
    Args:
        draft: The failed draft text
        validation_results: List of validation failures
        strategy: Strategy type (mechanical_fix, creative_rewrite, etc.)
        focus: Focus area for improvement
        emphasis: Emphasis directive
        
    Returns:
        Formatted critique generation prompt
    """
    template = _get_prompt_template("v2_critique_generation")
    
    # Format validation failures
    failures_text = "\n".join([
        f"- {vr.rule_id}: {vr.message}"
        for vr in validation_results if not vr.passed
    ])
    
    # Build strategy-specific instructions
    strategy_instructions = {
        "mechanical_fix": "Focus on exact compliance with format, length, and structure constraints.",
        "strategic_reframe": "Focus on thematic alignment and positioning strategy.",
        "creative_rewrite": "Focus on quality, originality, and impact.",
        "creative_breakthrough": "Suggest a completely fresh approach and perspective."
    }
    
    strategy_guidance = strategy_instructions.get(strategy, "Provide comprehensive improvement guidance.")
    
    return template.format(
        draft=draft[:800],
        failures_text=failures_text,
        strategy_guidance=strategy_guidance,
        focus=focus,
        emphasis=emphasis
    )

def build_hil_brief_prompt(
    section_name: str,
    failed_draft: str,
    critique_context: str,
    validation_summary: str
) -> str:
    """
    VV2 NEW: Builds prompt for generating HIL escalation brief.
    Creates a concise summary for human reviewers.
    
    Args:
        section_name: Section that failed
        failed_draft: The failed draft text
        critique_context: Critique from previous attempts
        validation_summary: Summary of validation failures
        
    Returns:
        Formatted HIL brief
    """
    template = _get_prompt_template("v2_hil_brief")
    
    return template.format(
        section_name=section_name,
        failed_draft=failed_draft[:500],
        critique_context=critique_context[:300],
        validation_summary=validation_summary
    )

# ==============================================================================
# LIBRARIAN AGENT PROMPTS (Phase 3)
# ==============================================================================

def build_librarian_mission_extraction_prompt(
    job_description: str,
    company_name: str,
    job_title: str
) -> str:
    """
    Builds prompt for Librarian agent to extract RAGMission from JD.
    This is the HIGH-SIGNAL extraction that feeds the entire RAG pipeline.
    """
    template = _get_prompt_template("librarian_mission_extraction")
    
    return template.format(
        job_description=job_description,
        company_name=company_name,
        job_title=job_title
    )

def build_librarian_strategic_analysis_prompt(
    job_description: str,
    rag_mission: 'RAGMission',
    previous_context: Optional[str] = None
) -> str:
    """
    Builds prompt for Librarian to analyze strategic priorities and initiatives.
    Used in multi-hop RAG for deep context building.
    """
    template = _get_prompt_template("librarian_strategic_analysis")
    
    # Format previous context if available
    context_section = ""
    if previous_context:
        context_section = f"\n**Previous Analysis Context:**\n{previous_context}\n"
    
    return template.format(
        job_description=job_description,
        target_company_name=rag_mission.target_company_name,
        precise_role_title=rag_mission.precise_role_title,
        key_technologies=', '.join(rag_mission.key_technologies),
        core_responsibilities=', '.join(rag_mission.core_responsibilities),
        context_section=context_section
    )

def build_librarian_memory_query_prompt(
    query: str,
    context_type: str = "general"
) -> str:
    """
    Builds prompt for querying Librarian's persistent memory (ChromaDB).
    Used to retrieve relevant past insights for current JD.
    """
    template = _get_prompt_template("librarian_memory_query")
    
    return template.format(
        query=query,
        context_type=context_type
    )

# ==============================================================================
# DYNAMIC PROMPT BUILDERS - RAG System (HOP-0)
# (Enhanced with high-signal extraction patterns)
# ==============================================================================

def _format_resume_index_summary(index: 'MasterResumeIndex') -> str:
    """Helper to format resume index for prompt context."""
    summary_parts = []
    if hasattr(index, 'recency_scores') and index.recency_scores:
        top_skills = sorted(index.recency_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        skills_list = [skill for skill, _ in top_skills]
        summary_parts.append(f"Top Candidate Skills (by recency): {', '.join(skills_list)}")
    
    if hasattr(index, 'achievement_catalog') and index.achievement_catalog:
        ach_summary = [f"{a.get('value', 'N/A')} {a.get('metric_type', 'achievement')}" for a in index.achievement_catalog[:3]]
        if ach_summary:
            summary_parts.append(f"Recent Achievements: {'; '.join(ach_summary)}")
    
    return '\n'.join(summary_parts) if summary_parts else "Candidate profile context not available."

def build_phase1_prompt(
    job_description: str,
    mission: 'RAGMission',
    master_resume_index: 'MasterResumeIndex',
    company_name: Optional[str] = None,
    librarian_context: Optional[str] = None
) -> str:
    """
    Build Phase 1 RAG prompt with Librarian context integration.
    Enhanced with high-signal extraction patterns.
    """
    
    # 1. LOGIC: Prepare the data ("ingredients")
    candidate_context = _format_resume_index_summary(master_resume_index)
    
    # 2. Integrate Librarian context if available
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"
    
    # 3. Build high-signal search queries
    tech_search_line = ""
    if mission.key_technologies:
        safe_tech = mission.key_technologies[0].replace('"', '')
        tech_search_line = f'3. Search for: `"{mission.target_company_name} press release {safe_tech}"`'
    
    # 4. Add strategic priorities context if available
    strategic_context = ""
    if hasattr(mission, 'strategic_priorities') and mission.strategic_priorities:
        strategic_context = f"\n**Strategic Priorities to Address:**\n{chr(10).join(['- ' + p for p in mission.strategic_priorities])}\n"

    # 5. DATA: Get the recipe card
    template = _get_prompt_template("rag_phase_1")

    # 6. LOGIC: Fill in the blanks and return
    return template.format(
        job_description=job_description[:1500],
        candidate_context=candidate_context,
        target_company_name=mission.target_company_name,
        tech_search_line=tech_search_line,
        key_technologies=', '.join(mission.key_technologies),
        librarian_section=librarian_section,
        strategic_context=strategic_context
    )

def build_phase2_prompt(
    job_description: str,
    mission: 'RAGMission',
    industry: str,
    librarian_context: Optional[str] = None
) -> str:
    """
    Build Phase 2 RAG prompt with enhanced signal extraction.
    Focuses on identifying gaps and overlaps for positioning strategy.
    """
    template = _get_prompt_template("rag_phase_2")
    
    # Add Librarian context integration
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"
    
    # Add competitors context if available
    competitors_section = ""
    if hasattr(mission, 'competitors') and mission.competitors:
        competitors_section = f"\n**Known Competitors:**\n{', '.join(mission.competitors)}\n"
    
    return template.format(
        precise_role_title=mission.precise_role_title,
        industry=industry,
        signal_gap_keywords=', '.join(mission.signal_gap_keywords),
        target_company_name=mission.target_company_name,
        librarian_section=librarian_section,
        competitors_section=competitors_section
    )

def build_phase3_prompt(
    job_description: str,
    mission: 'RAGMission',
    master_resume_index: 'MasterResumeIndex',
    peer_companies: List[str],
    comp_config: 'CompetitiveAnalysisConfig',
    industry: str,
    librarian_context: Optional[str] = None
) -> str:
    """
    Build Phase 3 RAG prompt with competitive intelligence focus.
    Enhanced with Librarian insights and differentiator extraction.
    """
    template = _get_prompt_template("rag_phase_3")
    achievements_context = _format_resume_index_summary(master_resume_index)
    search_pattern_instruction = comp_config.search_pattern.format(
        role_title=mission.precise_role_title,
        peer_company=peer_companies[0] if peer_companies else "peer company"
    )
    
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"
    
    # Build differentiators section from signal_gap_keywords
    differentiators_section = ', '.join(mission.signal_gap_keywords[:10]) if mission.signal_gap_keywords else "competitive advantages, unique capabilities"
    
    return template.format(
        target_company_name=mission.target_company_name,
        precise_role_title=mission.precise_role_title,
        peer_companies=', '.join(peer_companies),
        search_pattern_instruction=search_pattern_instruction,
        achievements_context=achievements_context,
        industry=industry,
        librarian_section=librarian_section,
        differentiators_section=differentiators_section,
        min_peer_jds=comp_config.min_peer_jds,
        table_stakes_threshold=comp_config.table_stakes_threshold,
        differentiator_threshold=comp_config.differentiator_threshold
    )

def build_phase4_prompt(
    job_description: str,
    mission: 'RAGMission',
    phase1_result: Dict = None,
    phase2_result: Dict = None,
    phase3_result: Dict = None,
    librarian_context: Optional[str] = None
) -> str:
    """Build Phase 4 RAG prompt for problem-solution narrative extraction."""
    template = _get_prompt_template("rag_phase_4")
    
    # Build librarian section
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"
    
    # Extract core responsibilities from mission
    core_responsibilities = ', '.join(mission.core_responsibilities) if mission.core_responsibilities else "strategic leadership, operational excellence"
    
    # Extract key technologies from mission
    key_technologies = ', '.join(mission.key_technologies) if mission.key_technologies else "enterprise platforms"
    
    # Build pain points section from prior phases
    pain_points = []
    if phase1_result:
        primary_theme_kws = phase1_result.get('thematic_analysis', {}).get('primary_theme', {}).get('keywords', [])
        pain_points.extend(primary_theme_kws[:3])
    if phase2_result:
        gaps = phase2_result.get('positioning_directives', {}).get('gaps_to_fill', [])
        pain_points.extend(gaps[:3])
    
    pain_points_section = ', '.join(list(set(pain_points))[:5]) if pain_points else "operational inefficiencies, strategic gaps"
    
    # Build search queries
    query_list = [
        f"\"{mission.target_company_name} challenges {tech}\"" for tech in mission.key_technologies[:3]
    ] + [
        f"\"common problems {mission.precise_role_title}\"",
        f"\"{mission.precise_role_title} best practices\""
    ]
    queries = '\n   - '.join(query_list[:5])
    
    return template.format(
        precise_role_title=mission.precise_role_title,
        core_responsibilities=core_responsibilities,
        key_technologies=key_technologies,
        pain_points_section=pain_points_section,
        librarian_section=librarian_section,
        queries=queries
    )

# ==============================================================================
# ARTIST SECTION GENERATION PROMPTS
# ==============================================================================

def build_bullet_generation_prompt(
    company_name: str,
    primary_theme: str,
    context_bullets: str,
    job_description: str,
    count: int,
    differentiator_keywords: List[str]
) -> str:
    """
    Builds the prompt for generating tailored bullets.
    NOTE: This is the V1 prompt. The V2 agentic model should
    use a more robust prompt that incorporates provenance targets.
    """
    template = _get_prompt_template("artist_synthetic_bullet") # Re-using synthetic for V1
    
    primary_theme_kw = primary_theme.split()[:5] if primary_theme else []
    diff_kw = differentiator_keywords[:5] if differentiator_keywords else []
    context_keywords = list(set(primary_theme_kw + diff_kw))[:10]

    return template.format(
        company_name=company_name,
        primary_theme=primary_theme,
        context_keywords=', '.join(context_keywords),
        context_bullets=context_bullets,
        job_description=job_description[:500],
        count=count
    )

def build_bullet_rewrite_prompt(
    original_bullet: str,
    target_word_count_range: Tuple[int, int],
    **kwargs
) -> str:
    """Builds the prompt for rewriting a single bullet to a word count."""
    template = _get_prompt_template("artist_bullet_rewrite_wc")
    min_wc, max_wc = target_word_count_range
    return template.format(
        original_bullet=original_bullet,
        min_wc=min_wc,
        max_wc=max_wc
    )

def build_overview_generation_prompt(
    bullet_summary_input: str,
    word_count_range: Tuple[int, int],
    thematic_analysis: 'ThematicAnalysis',
    job_description: str,
    **kwargs
) -> str:
    """Builds the prompt for generating an experience overview."""
    template = _get_prompt_template("artist_overview_generation")
    
    min_wc, max_wc = word_count_range
    
    job_desc_lower = job_description.lower()
    include_leadership_theme = any(kw in job_desc_lower for kw in ['lead', 'manage', 'director', 'vp', 'executive'])
    include_strategic_theme = any(kw in job_desc_lower for kw in ['strategy', 'roadmap', 'vision', 'partnership', 'alliance'])
    include_technical_theme = any(kw in job_desc_lower for kw in ['technical', 'architect', 'engineer', 'platform', 'cloud', 'ai', 'ml'])

    theme_instructions = []
    if include_leadership_theme: theme_instructions.append("- Leadership and team building aspects")
    if include_strategic_theme: theme_instructions.append("- Strategic planning and partnership elements")
    if include_technical_theme: theme_instructions.append("- Technical depth and platform expertise")

    theme_prompt_section = "**KEY THEMES TO INCORPORATE (if relevant and natural):**\n" + "\n".join(theme_instructions) if theme_instructions else ""

    return template.format(
        bullet_summary_input=bullet_summary_input,
        theme_prompt_section=theme_prompt_section,
        min_wc=min_wc,
        max_wc=max_wc
    )

def build_generation_prompt_with_reinforced_constraints(
    base_prompt: str,
    constraints: Dict[str, Any],
    attempt_number: int
) -> str:
    """
    Reinforces constraints progressively across attempts.
    V2: Used for progressive constraint enforcement in retry loops.
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

def build_sc_synthesis_prompt(
    original_prompt: str,
    candidate_responses: List[str]
) -> str:
    """Builds the prompt for self-consistency synthesis."""
    template = _get_prompt_template("artist_sc_synthesis")
    
    # LOGIC: Format the list of candidate responses
    formatted_responses = ""
    for i, res in enumerate(candidate_responses):
        formatted_responses += f"\n---\n**DRAFT {i+1}:**\n{res}\n---\n"
        
    return template.format(
        original_prompt=original_prompt,
        candidate_responses=formatted_responses
    )

# ==============================================================================
# VALIDATOR PROMPTS
# ==============================================================================

def build_validator_factual_check_prompt(
    section_name: str,
    section_content: str,
    thematic_analysis: 'ThematicAnalysis',
    job_description: str
) -> str:
    """
    Builds prompt for Validator to perform high-signal factual checks.
    Used in HOP-5 to detect strategic/factual failures that trigger Slow Loop.
    """
    template = _get_prompt_template("validator_factual_check")
    
    # Extract key verification points
    primary_theme = thematic_analysis.primary_theme.get('name', 'N/A') if thematic_analysis.primary_theme else 'N/A'
    
    differentiators = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
        diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
        if isinstance(diff_kw, list):
            differentiators = diff_kw[:5]
    
    return template.format(
        section_name=section_name,
        section_content=section_content,
        primary_theme=primary_theme,
        differentiators_str=', '.join(differentiators) or 'N/A',
        job_description=job_description[:800]
    )

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_prompt_template(template_key: str) -> str:
    """
    Retrieve a prompt template by its key.
    """
    return _get_prompt_template(template_key)

def list_available_templates() -> List[str]:
    """
    List all available prompt template keys from the JSON file.
    """
    return list(PROMPT_TEMPLATES.keys())

def get_prompts_dict() -> Dict[str, str]:
    """
    V2 NEW: Get the complete prompts dictionary for CRL initialization.
    Used by ContextRelayLayer in governor.py.
    """
    return PROMPT_TEMPLATES.copy()

# ==============================================================================
# V2 ARCHITECTURE: VERSION INFO
# ==============================================================================

__version__ = "18.0"
__architecture__ = "v3.8"
__compatible_with__ = ["workflow_RES_v3.8.py", "governor_v3.8.py"]