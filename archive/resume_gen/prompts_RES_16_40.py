# File: prompts.py
# Prompt Templates module for Resume Workflow
# Contains all static templates and dynamic prompt-builder functions

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# Import models needed for type hinting and context
# These are imported as strings to avoid circular dependencies if models imports prompts
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models_RES import RAGMission, MasterResumeIndex, ThematicAnalysis, CompetitiveAnalysisConfig
    from config_RES import ContentConstraintsConfig
    from models_RES import ThematicAnalysis as TheData # Use the real object


# ==============================================================================
# STATIC PROMPT TEMPLATES (from artist_specs.json)
#
# NOTE: Renamed to match the keys in artist_specs.json (e.g., K1_SUMMARY_TEMPLATE
# was renamed to K1_EXECUTIVE_SUMMARY_TEMPLATE) to fix the QA bug.
# ==============================================================================

K0_HEADLINE_TEMPLATE = """You are a professional resume writer creating a compelling headline for a resume.

Given the following information:
- Primary Theme: {primary_theme}
- Key Differentiators: {differentiators_str}

**Constraints (CRITICAL):**
1.  **Format:** Must be three components separated by pipes ( | ).
    Example: `[Role/Expertise] | [Key Skill/Domain] | [Key Accomplishment/Value]`
2.  **Total Word Count:** Must be **strictly** between {min_wc} and {max_wc} words.
3.  **Component Word Count:** Each component (between the pipes) must be between {comp_min_wc} and {comp_max_wc} words.
4.  **Content:** Must be grounded in the provided themes and differentiators.
5.  **Forbidden:** Do NOT use commas. Do NOT use generic titles like "Director" or "Manager" (e.g., "Director of AI").
6.  **Output:** Provide ONLY the headline text. No preamble, no explanation, no markdown.

Generate only the headline."""

K1_EXECUTIVE_SUMMARY_TEMPLATE = """You are an expert resume writer crafting a compelling executive summary.

**Context:**
- **Primary Theme:** {primary_theme}
- **Role Archetype Instruction:** {archetype_instruction}
- **Key Differentiators (Must include):** {differentiators_str}
- **Problem-Solution Narrative (Must frame):**
    - Problem: "{problem}"
    - Solution: "{solution}"
- **Experience Snippets (for context):**
{experience_snippets}

**Task:**
Write a professional resume summary that meets these **CRITICAL** constraints:
1.  **Sentence Count:** Must be **exactly** {min_sc} to {max_sc} sentences.
2.  **Word Count:** Must be **strictly** between {min_wc} and {max_wc} words.
3.  **Content (Mandatory):**
    - Must incorporate the **Primary Theme**.
    - Must align with the **Role Archetype Instruction**.
    - Must include at least {min_diff} of the **Key Differentiators**.
    - Must be framed around the **Problem-Solution Narrative**.
4.  **Format:**
    - Write in the third person.
    - Do NOT use "I", "my", or "me".
    - Do NOT use placeholders (e.g., "[X years]").
5.  **Output:** Provide ONLY the summary text. No preamble, no explanation, no markdown.

**Executive Summary:**
"""

# K4, K5, K6 Narratives use the same dynamic builder, but we keep the
# template keys here for mapping in artist_specs.json
K4_TRADERSENSE_NARRATIVE_TEMPLATE = "" # Handled by build_narrative_prompt
K5_EY_NARRATIVE_TEMPLATE = "" # Handled by build_narrative_prompt
K6_EARLY_CAREER_NARRATIVE_TEMPLATE = "" # Handled by build_narrative_prompt

K10_SKILLS_TEMPLATE = """You are an expert resume writer creating a "Strategic & Technical Competencies" section.

**Context:**
- **Target Job Keywords (for emphasis):** {combined_keywords_str}
- **Candidate's Master Skills (for grounding):** (Provided in system context, do not repeat)

**Task:**
Generate a list of **exactly 12** strategic and technical competencies, formatted as a bulleted list.

**CRITICAL Constraints:**
1.  **Count:** Must be **exactly 12** competencies.
2.  **Format:** Each competency must be a single line starting with an asterisk and a space (`* `).
3.  **Word Count:** Each competency must be **1-3 words** (e.g., "* Cloud Architecture", "* Strategic Partnerships", "* AI/ML Engineering").
4.  **Relevance:** Competencies must be a mix of strategic and technical skills, inspired by the Target Job Keywords.
5.  **Output:** Provide ONLY the 12 bullet points. No preamble, no headers, no explanation, no markdown fences.

**Competencies:**
"""

K11_COVER_LETTER_TEMPLATE = """You are writing a professional, impactful cover letter.

**Context:**
- **Current Date:** {current_date}
- **Primary Theme:** {primary_theme}
- **Key Differentiators:** {differentiators_str}
- **Problem-Solution Narrative:**
    - Problem: "{problem}"
    - Solution: "{solution}"
- **Candidate Experience Snippets:**
{experience_snippets}

**Task:**
Write a full-page cover letter (3-4 paragraphs) that meets these **CRITICAL** constraints:

**Structure (Must follow this exactly):**
1.  **Date:** `{current_date}`
2.  **Recipient Block:**
    Hiring Manager
    [Company Name]
3.  **Salutation:**
    Dear Hiring Manager,
4.  **Body Paragraph 1 (Hook):**
    - Express specific enthusiasm for the role and company.
    - Connect to the **Primary Theme** and the company's goals.
    - Word count: **Strictly {p1_min_wc}-{p1_max_wc} words.**
5.  **Body Paragraph 2 (Proof):**
    - Provide 1-2 specific examples of achievements, grounded in the **Experience Snippets**.
    - Frame these achievements using the **Problem-Solution Narrative**.
    - Word count: **Strictly {p2_min_wc}-{p2_max_wc} words.**
6.  **Body Paragraph 3 (Vision/Fit):**
    - Connect your skills (using **Key Differentiators**) to the company's future.
    - Reiterate enthusiasm and state your unique value.
    - Word count: **Strictly {p3_min_wc}-{p3_max_wc} words.**
7.  **Closing & Signature:**
    (Must match this exactly, including line breaks)
{expected_signature}

**Negative Constraints (CRITICAL):**
- Do NOT use placeholders (e.g., "[Company Name]", "[My Achievement]").
- Do NOT use generic phrases ("I am writing to apply...", "I believe I am a strong fit...").
- Do NOT simply list skills; narrate their impact.

**Output:**
Provide ONLY the complete cover letter text, adhering to all structure and content constraints.
"""

# ==============================================================================
# DYNAMIC PROMPT BUILDERS - RAG System (HOP-0)
# (Extracted from monolithic file)
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
    company_name: Optional[str] = None
) -> str:
    """Build Phase 1 RAG prompt for initial job market intelligence gathering."""
    
    candidate_context = _format_resume_index_summary(master_resume_index)
    tech_search_line = ""
    if mission.key_technologies:
        safe_tech = mission.key_technologies[0].replace('"', '')
        tech_search_line = f'3. Search for: `"{mission.target_company_name} press release {safe_tech}"`'

    return f"""You are a job market intelligence analyst. Research this role using web_search.

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE CONTEXT (Use to inform theme/keyword prioritization):
{candidate_context}

TASK:
1.  First, perform authoritative searches:
    1. Search for: `"{mission.target_company_name} engineering blog"`
    2. Search for: `"{mission.target_company_name} company values"`
    {tech_search_line}
2.  Then, perform 15-20 searches for similar job postings, prioritizing keywords: {', '.join(mission.key_technologies)}
3.  Analyze all results to identify:
    - Primary theme (main skill focus)
    - 4-5 Secondary themes
    - Role seniority and archetype (e.g., Executive_Leader, Technical_IC)
    - Trending keywords, required skills, and preferred skills.

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "searches_performed": <number of web_search calls>,
    "jds_analyzed": <number of unique JDs>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "thematic_analysis": {{
    "primary_theme": {{
      "name": "<theme name>",
      "confidence": <0.0-1.0>,
      "keywords": ["<keyword1>", "<keyword2>", ...],
      "market_prevalence": <0.0-1.0>
    }},
    "secondary_themes": [
      {{
        "name": "<theme name>",
        "relevance": <0.0-1.0>,
        "keywords": ["<keyword1>", ...]
      }}
    ],
    "trending_keywords": ["<keyword1>", ...],
    "required_skills": ["<skill1>", ...],
    "preferred_skills": ["<skill1>", ...]
  }},
  "role_classification": {{
    "seniority": "<entry|mid|senior|executive>",
    "function": "<function>",
    "industry_focus": "<industry>",
    "role_archetype": "<Executive_Leader|Technical_IC|Post-Sales_Customer_Success|Pre-Sales_GTM|Product_Management>"
  }}
}}

CRITICAL: Return ONLY valid JSON. No text before or after.
"""

def build_phase2_prompt(
    job_description: str,
    mission: 'RAGMission',
    industry: str
) -> str:
    """Build Phase 2 RAG prompt for authenticity patterns."""
    
    return f"""You are a LinkedIn profile analyst. Research this role using web_search:

TARGET ROLE: {mission.precise_role_title}
INDUSTRY: {industry}
GAP KEYWORDS TO FIND (Prioritize profiles mentioning these): {', '.join(mission.signal_gap_keywords)}

TASK:
1.  Execute authoritative search: `LinkedIn profile "{mission.precise_role_title}" at "{mission.target_company_name}"`
2.  Execute 10-15 additional searches for LinkedIn profiles/resumes for similar roles, prioritizing 'GAP KEYWORDS'.
3.  Analyze profiles to extract common patterns.

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "profiles_analyzed": <count>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "authenticity_patterns": {{
    "executive_summary_patterns": [
      "Built <ACHIEVEMENT> resulting in <IMPACT>",
      "Led <INITIATIVE> achieving <METRIC>",
      ...
    ],
    "achievement_verb_patterns": [
      "Drove", "Led", "Architected", ...
    ],
    "metric_presentation_patterns": [
      "$<NUMBER>M revenue",
      "<NUMBER>% growth",
      ...
    ],
    "competency_phrasing": [
      "<SKILL>: <CONTEXT>",
      ...
    ]
  }},
  "pattern_confidence": {{
    "executive_summary": <0.0-1.0>,
    "verbs": <0.0-1.0>,
    "metrics": <0.0-1.0>,
    "overall": <0.0-1.0>
  }}
}}

CRITICAL: Return ONLY valid JSON. Extract REAL patterns from profiles.
"""

def build_phase3_prompt(
    job_description: str,
    mission: 'RAGMission',
    master_resume_index: 'MasterResumeIndex',
    peer_companies: List[str],
    comp_config: 'CompetitiveAnalysisConfig',
    industry: str
) -> str:
    """Build Phase 3 RAG prompt for competitive positioning."""
    
    achievements_context = _format_resume_index_summary(master_resume_index)
    search_pattern_instruction = comp_config.search_pattern.format(
        role_title=mission.precise_role_title, peer_company="<peer_company>"
    )
    
    return f"""You are a competitive intelligence analyst. Research using web_search:

TARGET JD:
Company: {mission.target_company_name}
Role: {mission.precise_role_title}
Description: {job_description[:1000]}

PEER COMPANIES: {', '.join(peer_companies)}

CANDIDATE ACHIEVEMENTS (Use to validate differentiators):
{achievements_context}

TASK:
1.  Perform authoritative searches:
    1. `"Gartner Magic Quadrant for {industry}"`
    2. `"Forrester Wave {industry}"`
2.  Search for 10-15 similar roles at peer companies using patterns like: '{search_pattern_instruction}'.
3.  Analyze a minimum of {comp_config.min_peer_jds} JDs.
4.  Identify 'table stakes' (prevalence > {comp_config.table_stakes_threshold}) and 'differentiators' (uniqueness > {comp_config.differentiator_threshold}).

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "peer_jds_analyzed": <count>,
    "peer_companies": {json.dumps(peer_companies)},
    "sources": ["<url1>", ...]
  }},
  "competitive_analysis": {{
    "table_stakes_keywords": [
      {{"keyword": "<keyword>", "prevalence": <0.0-1.0>}}
    ],
    "differentiator_keywords": [
      {{"keyword": "<keyword>", "uniqueness_score": <0.0-1.0>}}
    ]
  }},
  "positioning_insight": "<2-3 sentence summary>"
}}

CRITICAL: Return ONLY valid JSON.
"""

def build_phase4_prompt(mission: 'RAGMission') -> str:
    """Build Phase 4 RAG prompt for narrative mining."""
    
    queries = [
        f'"challenges of {mission.core_responsibilities[0]} for {mission.key_technologies[0]}"' if mission.core_responsibilities and mission.key_technologies else f'"challenges of {mission.precise_role_title}"',
        f'"case study {mission.precise_role_title}"',
        f'"{mission.target_company_name} customer success stories"',
    ]
    
    return f"""You are a business narrative analyst. Find common "problem-solution" stories for this role.

TARGET ROLE: {mission.precise_role_title}
CORE RESPONSIBILITIES: {', '.join(mission.core_responsibilities)}
KEY TECHNOLOGIES: {', '.join(mission.key_technologies)}

TASK:
1. Execute 8-10 web searches using queries like these: {', '.join(queries)}.
2. Analyze articles and case studies to find recurring problems and their solutions.

Return ONLY this JSON structure:
{{
  "search_summary": {{
    "searches_performed": <number of web_search calls>,
    "sources": ["<url1>", "<url2>", ...]
  }},
  "problem_solution_narratives": {{
    "common_problems": [
      "Problem statement 1 (e.g., 'High cost of model inference at scale')"
    ],
    "solution_patterns": [
      "Solution narrative 1 (e.g., 'Implemented model quantization to reduce inference costs')"
    ]
  }}
}}

CRITICAL: Return ONLY valid JSON. Problems/solutions must be specific.
"""

# ==============================================================================
# DYNAMIC PROMPT BUILDERS - ArtistGenerator (HOP-3)
# (Extracted from monolithic file - fills QA gap)
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
    **kwargs # Accepts extra context
) -> str:
    """Builds the prompt for generating K4/K5/K6 narratives."""
    
    return f"""You are an expert resume writer creating a concise 2-3 sentence narrative for a past role.

**Role Context:**
- **Company:** {company_name}
- **Title:** {title}
- **Master Resume Highlights (Grounding):**
{master_context}

**Targeting Context:**
- **RAG Signals (Incorporate these):** {combined_signals_str}
- **K0 Themes (If relevant):** {k0_themes_str}
- **Focus Instruction:** {focus_instruction}

**Task:**
Write a narrative that summarizes the role's scope and impact, grounded in the **Master Resume Highlights** and subtly aligned with the **RAG Signals**.

**CRITICAL Constraints:**
1.  **Sentence Count:** Must be **exactly {target_sc}** sentences.
2.  **Word Count:** Must be **strictly** between {min_wc} and {max_wc} words.
3.  **Content:** Must be a high-level summary, NOT a bullet point.
4.  **Forbidden Phrases:** Do NOT start with "At [Company]", "As [Title]", "In this role", or "Responsible for".
5.  **Output:** Provide ONLY the narrative text. No preamble, no explanation, no markdown.

**Narrative ({target_sc} sentences, {min_wc}-{max_wc} words):**
"""

def build_verbatim_bullet_selection_prompt(
    master_bullets_text_list: List[str],
    verbatim_count: int,
    thematic_analysis: 'ThematicAnalysis'
) -> str:
    """Builds the prompt for selecting verbatim bullets."""
    
    keywords_for_prompt = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
         kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
         if isinstance(kw_raw, list): 
             keywords_for_prompt = kw_raw[:10]

    return f"""Select the {verbatim_count} most relevant bullet points from the list below based on the target keywords. 

**BULLET LIST:**
{chr(10).join([f"- {b}" for b in master_bullets_text_list])}

**TARGET KEYWORDS:** {', '.join(keywords_for_prompt) or 'N/A'}

**Instructions:**
1. Choose the {verbatim_count} bullets from the list that best align with the target keywords.
2. Output ONLY the selected bullet points, exactly as they appear in the list, one per line.
3. Do not add numbers, prefixes, or commentary.

**SELECTED BULLETS (Exactly {verbatim_count}, one per line, verbatim):**
"""

def build_customized_bullet_prompt(
    source_bullets_text: List[str],
    thematic_analysis: 'ThematicAnalysis'
) -> str:
    """Builds the prompt for customizing bullets."""
    
    primary_theme_kw = []
    if thematic_analysis and thematic_analysis.primary_theme:
         kw_raw = thematic_analysis.primary_theme.get('keywords', [])
         if isinstance(kw_raw, list): primary_theme_kw = kw_raw

    diff_kw = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
        kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
        if isinstance(kw_raw, list): diff_kw = kw_raw

    context_keywords = list(set(primary_theme_kw + diff_kw))[:7]
    bullets_input = "\n".join([f"• {b}" for b in source_bullets_text])

    return f"""Lightly rewrite the following resume bullet points to subtly align with target themes/keywords, preserving original meaning and metrics.

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

def build_synthetic_bullet_prompt(
    count: int,
    company_name: str,
    job_description: str,
    thematic_analysis: 'ThematicAnalysis',
    context_bullets: str
) -> str:
    """Builds the prompt for generating synthetic bullets."""
    
    primary_theme = thematic_analysis.primary_theme.get('name', 'key responsibilities') if thematic_analysis.primary_theme else 'key responsibilities'
    primary_theme_kw = []
    if thematic_analysis and thematic_analysis.primary_theme:
         kw_raw = thematic_analysis.primary_theme.get('keywords', [])
         if isinstance(kw_raw, list): primary_theme_kw = kw_raw

    diff_kw = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
        kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
        if isinstance(kw_raw, list): diff_kw = kw_raw
    context_keywords = list(set(primary_theme_kw + diff_kw))[:10]

    return f"""You are an expert resume writer tasked with generating synthetic, impactful resume bullet points.

**CONTEXT:**
* **Target Company/Role Context:** {company_name}
* **Primary Theme:** {primary_theme}
* **Target Keywords/Differentiators:** {', '.join(context_keywords)}
* **Existing Bullets (for style and context):**
{context_bullets}
* **Target Job Description Snippet:**
{job_description[:500]}...

**TASK:**
Generate EXACTLY {count} unique, plausible, and impactful SYNTHETIC resume bullet points relevant to the role context and keywords provided.

**ABSOLUTELY CRITICAL REQUIREMENTS:**
1.  Generate EXACTLY {count} bullet points.
2.  Each bullet MUST start with an asterisk and a space ('* ').
3.  Bullets should be concise, achievement-oriented, and include plausible metrics (e.g., "Reduced X by Y%", "Increased Z by $A million").
4.  Subtly align with the **Primary Theme** and **Target Keywords/Differentiators**.
5.  **Do NOT** start bullets with generic phrases like 'Responsible for...', 'Duties included...', 'At [Company]', 'As [Title]', etc. Use strong action verbs.
6.  Output ONLY the {count} bullet points, one per line. No preamble, no explanation, no markdown fences like ```.

**SYNTHETIC BULLETS (Exactly {count}):**
"""

def build_bullet_reorder_prompt(
    company_name: str,
    current_bullets_text_input: str,
    thematic_analysis: 'ThematicAnalysis',
    bullet_count: int
) -> str:
    """Builds the prompt for reordering bullets."""
    
    keywords_for_prompt = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
         kw_raw = getattr(comp_intel, 'differentiator_keywords', [])
         if isinstance(kw_raw, list): keywords_for_prompt = kw_raw[:10]

    return f"""Reorder the following resume bullet points for maximum impact and relevance based on the target keywords.

**Bullets to Reorder ({company_name}):**
{current_bullets_text_input}

**Target Job Description Keywords (Prioritize relevance to these):**
{', '.join(keywords_for_prompt) or 'N/A'}

**Instructions:**
1. Analyze the bullets and keywords. Determine the optimal order,
   placing the most relevant bullets first.
2. Output ONLY the reordered bullet points, exactly as provided (including the `1. `, `2. ` prefixes), 
   but in the new order, one per line.
3. Do not add commentary or markdown.

**REORDERED BULLETS (Exactly {bullet_count}, one per line, verbatim text with original prefix):**
"""

def build_bullet_rewrite_prompt(
    original_bullet: str,
    target_word_count_range: Tuple[int, int],
    **kwargs # Accept context/constraints but don't use them yet
) -> str:
    """Builds the prompt for rewriting a single bullet to a word count."""
    
    min_wc, max_wc = target_word_count_range
    
    return f"""Rewrite the following resume bullet point to meet a specific word count constraint, preserving core meaning, metrics, and tone.

ORIGINAL BULLET:
{original_bullet}

TARGET: {min_wc}-{max_wc} words

CORE REQUIREMENTS:
1. Preserve all metrics, numbers, and specific achievements.
2. Maintain professional resume tone.
3. **Do NOT start with 'At [Company]', 'As [Title]', etc.**
4. Output ONLY the rewritten bullet text. No markdown fences (```).
"""

def build_overview_generation_prompt(
    bullet_summary_input: str,
    word_count_range: Tuple[int, int],
    thematic_analysis: 'ThematicAnalysis',
    job_description: str,
    **kwargs
) -> str:
    """Builds the prompt for generating an experience overview."""
    
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

    return f"""You are an expert resume editor. Write a concise 1-2 sentence overview summarizing the key achievements from the bullets below, while also weaving in the specified high-level themes relevant to the overall target role.

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

def build_generation_prompt_with_reinforced_constraints(
    base_prompt: str,
    constraints: Dict[str, Any],
    attempt_number: int
) -> str:
    """
    Reinforces constraints progressively across attempts.
    (Extracted from resume_workflow_v16_20.py)
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
    
    synthesis_prompt = f"""You are a senior editor tasked with synthesizing multiple draft responses generated for the same prompt into a single, high-quality final answer that strictly adheres to all original constraints.

**ORIGINAL PROMPT (for context on constraints):**
---
{original_prompt}
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
    return synthesis_prompt

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_prompt_template(template_key: str) -> str:
    """
    Retrieve a prompt template by its key.
    """
    try:
        return globals()[template_key]
    except KeyError:
        raise AttributeError(f"Prompt template key '{template_key}' does not exist in prompts.py")


def list_available_templates() -> List[str]:
    """
    List all available prompt template keys.
    """
    return [
        name for name in globals()
        if name.isupper() and name.endswith('_TEMPLATE')
    ]


# ==============================================================================
# PROMPT_TEMPLATES DICTIONARY (for easy access)
# ==============================================================================

# Build dictionary of all template constants for easy lookup
PROMPT_TEMPLATES = {
    'K0_HEADLINE_TEMPLATE': K0_HEADLINE_TEMPLATE,
    'K1_SUMMARY_TEMPLATE': K1_EXECUTIVE_SUMMARY_TEMPLATE,
    'K1_EXECUTIVE_SUMMARY_TEMPLATE': K1_EXECUTIVE_SUMMARY_TEMPLATE,
    'K4_NARRATIVE_TEMPLATE': K4_TRADERSENSE_NARRATIVE_TEMPLATE,
    'K4_TRADERSENSE_NARRATIVE_TEMPLATE': K4_TRADERSENSE_NARRATIVE_TEMPLATE,
    'K5_NARRATIVE_TEMPLATE': K5_EY_NARRATIVE_TEMPLATE,
    'K5_EY_NARRATIVE_TEMPLATE': K5_EY_NARRATIVE_TEMPLATE,
    'K6_NARRATIVE_TEMPLATE': K6_EARLY_CAREER_NARRATIVE_TEMPLATE,
    'K6_EARLY_CAREER_NARRATIVE_TEMPLATE': K6_EARLY_CAREER_NARRATIVE_TEMPLATE,
    'K10_SKILLS_TEMPLATE': K10_SKILLS_TEMPLATE,
    'K11_COVER_LETTER_TEMPLATE': K11_COVER_LETTER_TEMPLATE,
}