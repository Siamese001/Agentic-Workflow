# File: prompts_RES.py
# Version: 16.31 (Phase 3: High-Signal RAG, Librarian Agent, Macro ToT)
# Prompt Templates module for Resume Workflow
# Contains all *logic* for loading and formatting prompts from prompts.json

import json
import logging

# Import models needed for type hinting
from typing import TYPE_CHECKING

# --- FIX: Import the DATA_DIR constant ---
from config.config import DATA_DIR

if TYPE_CHECKING:
    from apps_shared.rag.hardening.models import MasterResumeIndex, RAGMission, ThematicAnalysis
    from config.config import CompetitiveAnalysisConfig

# --- LOGIC: Load the 'Recipe Book' (prompts.json) at startup ---
try:
    # --- FIX: Build path relative to this file ---
    prompts_path = DATA_DIR / "prompts.json"
    with open(prompts_path, encoding="utf-8") as f:
        PROMPT_TEMPLATES = json.load(f)
    logging.info(f"Successfully loaded prompts.json from {prompts_path}")
except Exception as e:
    logging.critical(f"FATAL: Could not load prompts.json: {e}")
    PROMPT_TEMPLATES = {}  # Fallback to prevent crash, will error at runtime
# -----------------------------------------------------------------


def _get_prompt_template(key: str) -> str:
    """Helper to safely get a prompt template."""
    template = PROMPT_TEMPLATES.get(key)
    if not template:
        logging.error(f"Prompt template key '{key}' not found in prompts.json!")
        raise KeyError(f"Prompt template key '{key}' not found in prompts.json!")
    return template


# ==============================================================================
# LIBRARIAN AGENT PROMPTS (NEW - Phase 3)
# ==============================================================================


def build_librarian_mission_extraction_prompt(
    job_description: str,
    company_name: str,
    job_title: str,
) -> str:
    """
    Builds prompt for Librarian agent to extract RAGMission from JD.
    This is the HIGH-SIGNAL extraction that feeds the entire RAG pipeline.
    """
    template = _get_prompt_template("librarian_mission_extraction")

    return template.format(
        job_description=job_description,
        company_name=company_name,
        job_title=job_title,
    )


def build_librarian_strategic_analysis_prompt(
    job_description: str,
    rag_mission: "RAGMission",
    previous_context: str | None = None,
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
        key_technologies=", ".join(rag_mission.key_technologies),
        core_responsibilities=", ".join(rag_mission.core_responsibilities),
        context_section=context_section,
    )


def build_librarian_memory_query_prompt(query: str, context_type: str = "standard") -> str:
    """
    Builds prompt for querying Librarian's persistent memory (ChromaDB).
    Used to retrieve relevant past insights for current JD.
    """
    template = _get_prompt_template("librarian_memory_query")

    return template.format(query=query, context_type=context_type)


# ==============================================================================
# DYNAMIC PROMPT BUILDERS - RAG System (HOP-0)
# (Enhanced with high-signal extraction patterns)
# ==============================================================================


def _format_resume_index_summary(index: "MasterResumeIndex") -> str:
    """Helper to format resume index for prompt context. (This is pure logic, so it stays)"""
    summary_parts = []
    if hasattr(index, "recency_scores") and index.recency_scores:
        top_skills = sorted(index.recency_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        skills_list = [skill for skill, _ in top_skills]
        summary_parts.append(f"Top Candidate Skills (by recency): {', '.join(skills_list)}")

    if hasattr(index, "achievement_catalog") and index.achievement_catalog:
        ach_summary = [
            f"{a.get('value', 'N/A')} {a.get('metric_type', 'achievement')}"
            for a in index.achievement_catalog[:3]
        ]
        if ach_summary:
            summary_parts.append(f"Recent Achievements: {'; '.join(ach_summary)}")

    return "\n".join(summary_parts) if summary_parts else "Candidate profile context not available."


def build_phase1_prompt(
    job_description: str,
    mission: "RAGMission",
    master_resume_index: "MasterResumeIndex",
    company_name: str | None = None,
    librarian_context: str | None = None,
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
        safe_tech = mission.key_technologies[0].replace('"', "")
        tech_search_line = f'3. Search for: `"{mission.target_company_name} press release {safe_tech}"`'

    # 4. Add strategic priorities context if available
    strategic_context = ""
    if hasattr(mission, "strategic_priorities") and mission.strategic_priorities:
        strategic_context = f"\n**Strategic Priorities to Address:**\n{chr(10).join(['- ' + p for p in mission.strategic_priorities])}\n"

    # 5. DATA: Get the recipe card
    template = _get_prompt_template("rag_phase_1")

    # 6. LOGIC: Fill in the blanks and return
    return template.format(
        job_description=job_description[:1500],
        candidate_context=candidate_context,
        target_company_name=mission.target_company_name,
        tech_search_line=tech_search_line,
        key_technologies=", ".join(mission.key_technologies),
        librarian_section=librarian_section,
        strategic_context=strategic_context,
    )


def build_phase2_prompt(
    job_description: str,
    mission: "RAGMission",
    industry: str,
    librarian_context: str | None = None,
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
    if hasattr(mission, "competitors") and mission.competitors:
        competitors_section = f"\n**Known Competitors:**\n{', '.join(mission.competitors)}\n"

    return template.format(
        precise_role_title=mission.precise_role_title,
        industry=industry,
        signal_gap_keywords=", ".join(mission.signal_gap_keywords),
        target_company_name=mission.target_company_name,
        librarian_section=librarian_section,
        competitors_section=competitors_section,
    )


def build_phase3_prompt(
    job_description: str,
    mission: "RAGMission",
    master_resume_index: "MasterResumeIndex",
    peer_companies: list[str],
    comp_config: "CompetitiveAnalysisConfig",
    industry: str,
    librarian_context: str | None = None,
) -> str:
    """
    Build Phase 3 RAG prompt with competitive intelligence focus.
    Enhanced with Librarian insights and differentiator extraction.
    """
    template = _get_prompt_template("rag_phase_3")
    achievements_context = _format_resume_index_summary(master_resume_index)
    search_pattern_instruction = comp_config.search_pattern.format(
        role_title=mission.precise_role_title,
        peer_company="<peer_company>",
    )

    # Add Librarian context
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"

    # Add differentiators context if available
    differentiators_section = ""
    if hasattr(mission, "differentiators") and mission.differentiators:
        differentiators_section = f"\n**Key Differentiators to Emphasize:**\n{chr(10).join(['- ' + d for d in mission.differentiators])}\n"

    return template.format(
        target_company_name=mission.target_company_name,
        precise_role_title=mission.precise_role_title,
        job_description=job_description[:1000],
        peer_companies=", ".join(peer_companies),
        peer_companies_json=json.dumps(peer_companies),
        achievements_context=achievements_context,
        industry=industry,
        search_pattern_instruction=search_pattern_instruction,
        min_peer_jds=comp_config.min_peer_jds,
        table_stakes_threshold=comp_config.table_stakes_threshold,
        differentiator_threshold=comp_config.differentiator_threshold,
        librarian_section=librarian_section,
        differentiators_section=differentiators_section,
    )


def build_phase4_prompt(mission: "RAGMission", librarian_context: str | None = None) -> str:
    """
    Build Phase 4 RAG prompt with problem-solution narrative focus.
    Enhanced with Librarian context for pain point identification.
    """
    template = _get_prompt_template("rag_phase_4")

    # Build high-signal queries targeting pain points
    queries = [
        f'"challenges of {mission.core_responsibilities[0]} for {mission.key_technologies[0]}"'
        if mission.core_responsibilities and mission.key_technologies
        else f'"challenges of {mission.precise_role_title}"',
        f'"case study {mission.precise_role_title}"',
        f'"{mission.target_company_name} customer success stories"',
    ]

    # Add identified pain points if available
    pain_points_section = ""
    if hasattr(mission, "identified_pain_points") and mission.identified_pain_points:
        pain_points_section = f"\n**Identified Pain Points:**\n{chr(10).join(['- ' + p for p in mission.identified_pain_points])}\n"

    # Add Librarian context
    librarian_section = ""
    if librarian_context:
        librarian_section = f"\n**Librarian Intelligence:**\n{librarian_context}\n"

    return template.format(
        precise_role_title=mission.precise_role_title,
        core_responsibilities=", ".join(mission.core_responsibilities),
        key_technologies=", ".join(mission.key_technologies),
        queries=", ".join(queries),
        pain_points_section=pain_points_section,
        librarian_section=librarian_section,
    )


# ==============================================================================
# MACRO TREE-OF-THOUGHT PROMPTS (NEW - Phase 3)
# ==============================================================================


def build_macro_tot_generation_prompt(
    base_prompt: str,
    draft_number: int,
    total_drafts: int,
    variation_instruction: str = "",
) -> str:
    """
    Builds prompt for generating one draft in Macro ToT process.
    Adds variation instructions to encourage diverse approaches.
    """
    template = _get_prompt_template("macro_tot_generation")

    # Default variation instructions if not provided
    if not variation_instruction:
        if draft_number == 1:
            variation_instruction = "Focus on TECHNICAL DEPTH and concrete achievements."
        elif draft_number == 2:
            variation_instruction = "Focus on STRATEGIC VISION and leadership capabilities."
        else:
            variation_instruction = "Focus on BALANCED APPROACH combining technical and strategic elements."

    return template.format(
        base_prompt=base_prompt,
        draft_number=draft_number,
        total_drafts=total_drafts,
        variation_instruction=variation_instruction,
    )


def build_evaluator_scoring_prompt(
    drafts: list[str],
    criteria: dict[str, object],
    section_name: str,
) -> str:
    """
    Builds prompt for Evaluator Agent to score competing drafts.
    Note: This is a FALLBACK - Code Interpreter is preferred for deterministic scoring.
    """
    template = _get_prompt_template("evaluator_scoring")

    # Format drafts
    drafts_text = ""
    for i, draft in enumerate(drafts, 1):
        drafts_text += f"\n---\n**DRAFT {i}:**\n{draft}\n"

    # Format criteria
    criteria_text = json.dumps(criteria, indent=2)

    return template.format(
        section_name=section_name,
        drafts_text=drafts_text,
        criteria_text=criteria_text,
        num_drafts=len(drafts),
    )


def build_macro_tot_synthesis_prompt(
    original_prompt: str,
    scored_drafts: list[tuple[str, float]],
    top_k: int = 2,
) -> str:
    """
    Builds prompt for synthesizing the best elements from top-scoring drafts.
    Used when Code Interpreter scores indicate multiple strong candidates.
    """
    template = _get_prompt_template("macro_tot_synthesis")

    # Sort drafts by score and take top K
    sorted_drafts = sorted(scored_drafts, key=lambda x: x[1], reverse=True)[:top_k]

    # Format top drafts with scores
    top_drafts_text = ""
    for i, (draft, score) in enumerate(sorted_drafts, 1):
        top_drafts_text += f"\n---\n**DRAFT {i} (Score: {score:.1f}):**\n{draft}\n"

    return template.format(
        original_prompt=original_prompt,
        top_drafts_text=top_drafts_text,
        top_k=top_k,
    )


# ==============================================================================
# DYNAMIC PROMPT BUILDERS - ArtistGenerator (HOP-3)
# ==============================================================================


def build_narrative_prompt(
    company_name: str,
    title: str,
    target_sc: int,
    min_wc: int,
    max_wc: int,
    master_context: str,
    combined_signals_str: str,
    focus_instruction: str,
    k0_themes_str: str,
    **kwargs: object,  # Accepts extra context
) -> str:
    """Builds the prompt for generating K4/K5/K6 narratives."""
    template = _get_prompt_template("artist_narrative")
    return template.format(
        company_name=company_name,
        title=title,
        target_sc=target_sc,
        min_wc=min_wc,
        max_wc=max_wc,
        master_context=master_context,
        combined_signals_str=combined_signals_str,
        focus_instruction=focus_instruction,
        k0_themes_str=k0_themes_str,
    )


def build_verbatim_bullet_selection_prompt(
    master_bullets_text_list: list[str],
    verbatim_count: int,
    thematic_analysis: "ThematicAnalysis",
) -> str:
    """Builds the prompt for selecting verbatim bullets."""
    template = _get_prompt_template("artist_verbatim_bullet_selection")

    keywords_for_prompt = []
    comp_intel = getattr(thematic_analysis, "competitive_intelligence", None)
    if comp_intel:
        kw_raw = getattr(comp_intel, "differentiator_keywords", [])
        if isinstance(kw_raw, list):
            keywords_for_prompt = kw_raw[:10]

    bullets_list = chr(10).join([f"- {b}" for b in master_bullets_text_list])

    return template.format(
        bullets_list=bullets_list,
        verbatim_count=verbatim_count,
        keywords_str=", ".join(keywords_for_prompt) or "N/A",
    )


def build_customized_bullet_prompt(
    source_bullets_text: list[str],
    thematic_analysis: "ThematicAnalysis",
) -> str:
    """Builds the prompt for customizing bullets."""
    template = _get_prompt_template("artist_customized_bullet")

    primary_theme_kw = []
    if thematic_analysis and thematic_analysis.primary_theme:
        kw_raw = thematic_analysis.primary_theme.get("keywords", [])
        if isinstance(kw_raw, list):
            primary_theme_kw = kw_raw

    diff_kw = []
    comp_intel = getattr(thematic_analysis, "competitive_intelligence", None)
    if comp_intel:
        kw_raw = getattr(comp_intel, "differentiator_keywords", [])
        if isinstance(kw_raw, list):
            diff_kw = kw_raw

    context_keywords = list(set(primary_theme_kw + diff_kw))[:7]
    bullets_input = "\n".join([f"• {b}" for b in source_bullets_text])

    return template.format(
        bullets_input=bullets_input,
        context_keywords=", ".join(context_keywords),
        bullet_count=len(source_bullets_text),
    )


def build_synthetic_bullet_prompt(
    count: int,
    company_name: str,
    job_description: str,
    thematic_analysis: "ThematicAnalysis",
    context_bullets: str,
) -> str:
    """Builds the prompt for generating synthetic bullets."""
    template = _get_prompt_template("artist_synthetic_bullet")

    # LOGIC: Prepare the data
    primary_theme = (
        thematic_analysis.primary_theme.get("name", "key responsibilities")
        if thematic_analysis.primary_theme
        else "key responsibilities"
    )
    primary_theme_kw = []
    if thematic_analysis and thematic_analysis.primary_theme:
        kw_raw = thematic_analysis.primary_theme.get("keywords", [])
        if isinstance(kw_raw, list):
            primary_theme_kw = kw_raw

    diff_kw = []
    comp_intel = getattr(thematic_analysis, "competitive_intelligence", None)
    if comp_intel:
        kw_raw = getattr(comp_intel, "differentiator_keywords", [])
        if isinstance(kw_raw, list):
            diff_kw = kw_raw
    context_keywords = list(set(primary_theme_kw + diff_kw))[:10]

    return template.format(
        company_name=company_name,
        primary_theme=primary_theme,
        context_keywords=", ".join(context_keywords),
        context_bullets=context_bullets,
        job_description=job_description[:500],
        count=count,
    )


def build_bullet_reorder_prompt(
    current_bullets_text_input: str,
    company_name: str,
    bullet_count: int,
    thematic_analysis: "ThematicAnalysis",
) -> str:
    """
    Builds the prompt for reordering bullets.
    NOTE: Code Interpreter should be used instead for deterministic reordering.
    """
    template = _get_prompt_template("artist_bullet_reorder")

    keywords_for_prompt = []
    comp_intel = getattr(thematic_analysis, "competitive_intelligence", None)
    if comp_intel:
        kw_raw = getattr(comp_intel, "differentiator_keywords", [])
        if isinstance(kw_raw, list):
            keywords_for_prompt = kw_raw[:10]

    return template.format(
        current_bullets_text_input=current_bullets_text_input,
        company_name=company_name,
        keywords_str=", ".join(keywords_for_prompt) or "N/A",
        bullet_count=bullet_count,
    )


def build_bullet_rewrite_prompt(
    original_bullet: str,
    target_word_count_range: tuple[int, int],
    **kwargs: dict[str, any],
) -> str:
    """Builds the prompt for rewriting a single bullet to a word count."""
    template = _get_prompt_template("artist_bullet_rewrite_wc")
    min_wc, max_wc = target_word_count_range
    return template.format(original_bullet=original_bullet, min_wc=min_wc, max_wc=max_wc)


def build_overview_generation_prompt(
    bullet_summary_input: str,
    word_count_range: tuple[int, int],
    thematic_analysis: "ThematicAnalysis",
    job_description: str,
    **kwargs: dict[str, object],
) -> str:
    """Builds the prompt for generating an experience overview."""
    template = _get_prompt_template("artist_overview_generation")

    min_wc, max_wc = word_count_range

    job_desc_lower = job_description.lower()
    include_leadership_theme = any(
        kw in job_desc_lower for kw in ["lead", "manage", "director", "vp", "executive"]
    )
    include_strategic_theme = any(
        kw in job_desc_lower for kw in ["strategy", "roadmap", "vision", "partnership", "alliance"]
    )
    include_technical_theme = any(
        kw in job_desc_lower for kw in ["technical", "architect", "engineer", "platform", "cloud", "ai", "ml"]
    )

    theme_instructions = []
    if include_leadership_theme:
        theme_instructions.append("- Leadership and team building aspects")
    if include_strategic_theme:
        theme_instructions.append("- Strategic planning and partnership elements")
    if include_technical_theme:
        theme_instructions.append("- Technical depth and platform expertise")

    theme_prompt_section = (
        "**KEY THEMES TO INCORPORATE (if relevant and natural):**\n" + "\n".join(theme_instructions)
        if theme_instructions
        else ""
    )

    return template.format(
        bullet_summary_input=bullet_summary_input,
        theme_prompt_section=theme_prompt_section,
        min_wc=min_wc,
        max_wc=max_wc,
    )


def build_generation_prompt_with_reinforced_constraints(
    base_prompt: str,
    constraints: dict[str, object],
    attempt_number: int,
) -> str:
    """
    Reinforces constraints progressively across attempts.
    (Extracted from resume_workflow_v16_20.py)
    """
    min_wc = constraints.get("min_wc", constraints.get("min_word_count", 0))
    max_wc = constraints.get("max_wc", constraints.get("max_word_count", 999))

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


def build_sc_synthesis_prompt(original_prompt: str, candidate_responses: list[str]) -> str:
    """Builds the prompt for self-consistency synthesis."""
    template = _get_prompt_template("artist_sc_synthesis")

    # LOGIC: Format the list of candidate responses
    formatted_responses = ""
    for i, res in enumerate(candidate_responses):
        formatted_responses += f"\n---\n**DRAFT {i + 1}:**\n{res}\n---\n"

    return template.format(original_prompt=original_prompt, candidate_responses=formatted_responses)


# ==============================================================================
# VALIDATOR PROMPTS (NEW - Phase 3)
# ==============================================================================


def build_validator_factual_check_prompt(
    section_name: str,
    section_content: str,
    thematic_analysis: "ThematicAnalysis",
    job_description: str,
) -> str:
    """
    Builds prompt for Validator to perform high-signal factual checks.
    Used in HOP-5 to detect strategic/factual failures that trigger Slow Loop.
    """
    template = _get_prompt_template("validator_factual_check")

    # Extract key verification points
    primary_theme = (
        thematic_analysis.primary_theme.get("name", "N/A") if thematic_analysis.primary_theme else "N/A"
    )

    differentiators = []
    comp_intel = getattr(thematic_analysis, "competitive_intelligence", None)
    if comp_intel:
        diff_kw = getattr(comp_intel, "differentiator_keywords", [])
        if isinstance(diff_kw, list):
            differentiators = diff_kw[:5]

    return template.format(
        section_name=section_name,
        section_content=section_content,
        primary_theme=primary_theme,
        differentiators_str=", ".join(differentiators) or "N/A",
        job_description=job_description[:800],
    )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def get_prompt_template(template_key: str) -> str:
    """
    Retrieve a prompt template by its key.
    (This function is now redundant but kept for compatibility)
    """
    return _get_prompt_template(template_key)


def list_available_templates() -> list[str]:
    """
    List all available prompt template keys from the JSON file.
    """
    return list(PROMPT_TEMPLATES.keys())
