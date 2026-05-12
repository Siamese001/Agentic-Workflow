"""Section Specifications for apps_rg Golden State.

W3A: Design-time spec only - no runtime implementation.

Defines the canonical resume sections and their specifications
per the tiered section-priority model.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResumeSectionDefinition:
    """Definition of a single resume section."""
    section_id: str
    section_name: str
    priority_tier: str  # T1_CRITICAL, T2_HIGH, T3_STANDARD, T4_MINIMAL
    description: str
    
    # Content constraints
    min_length_chars: int
    max_length_chars: int
    target_length_chars: int
    
    # G22 factual grounding requirement (invariant)
    g22_factual_grounding_required: bool = True
    g22_factual_grounding_threshold: float = 0.950
    
    # Required elements
    required_elements: List[str] = field(default_factory=list)
    optional_elements: List[str] = field(default_factory=list)
    
    # Scoring profile reference
    scorer_profile_ref: Optional[str] = None
    benchmark_set_ref: Optional[str] = None
    seed_set_ref: Optional[str] = None


# Canonical resume sections per Golden State tiered model
CANONICAL_RESUME_SECTIONS: Dict[str, ResumeSectionDefinition] = {
    # T1_CRITICAL sections
    "executive_summary": ResumeSectionDefinition(
        section_id="executive_summary",
        section_name="Executive Summary",
        priority_tier="T1_CRITICAL",
        description="Positioning statement and value proposition for target role",
        min_length_chars=200,
        max_length_chars=800,
        target_length_chars=400,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "role_alignment_statement",
            "key_differentiator",
            "relevant_achievement_summary",
        ],
        optional_elements=[
            "industry_expertise_highlight",
            "leadership_philosophy",
        ],
        scorer_profile_ref="executive_positioning_scorer",
        benchmark_set_ref="executive_summary_benchmarks",
        seed_set_ref="executive_summary_seeds",
    ),
    
    "experience": ResumeSectionDefinition(
        section_id="experience",
        section_name="Professional Experience",
        priority_tier="T1_CRITICAL",
        description="Chronological work history with achievement bullets",
        min_length_chars=500,
        max_length_chars=3000,
        target_length_chars=1500,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "company_name",
            "role_title",
            "employment_dates",
            "achievement_bullets",
        ],
        optional_elements=[
            "company_description",
            "team_size",
            "budget_scope",
        ],
        scorer_profile_ref="experience_depth_scorer",
        benchmark_set_ref="experience_benchmarks",
        seed_set_ref="experience_seeds",
    ),
    
    # T2_HIGH sections
    "competencies": ResumeSectionDefinition(
        section_id="competencies",
        section_name="Core Competencies",
        priority_tier="T2_HIGH",
        description="Skills and capabilities relevant to target role",
        min_length_chars=100,
        max_length_chars=600,
        target_length_chars=300,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "technical_skills",
            "leadership_skills",
            "domain_expertise",
        ],
        optional_elements=[
            "certifications",
            "tools_platforms",
        ],
        scorer_profile_ref="competencies_alignment_scorer",
        benchmark_set_ref="competencies_benchmarks",
        seed_set_ref="competencies_seeds",
    ),
    
    "achievements": ResumeSectionDefinition(
        section_id="achievements",
        section_name="Key Achievements",
        priority_tier="T2_HIGH",
        description="Highlighted accomplishments across career",
        min_length_chars=150,
        max_length_chars=800,
        target_length_chars=400,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "quantified_results",
            "business_impact",
            "personal_contribution",
        ],
        optional_elements=[
            "awards_recognition",
            "metrics_timeline",
        ],
        scorer_profile_ref="achievement_impact_scorer",
        benchmark_set_ref="achievements_benchmarks",
        seed_set_ref="achievements_seeds",
    ),
    
    # T3_STANDARD sections
    "education": ResumeSectionDefinition(
        section_id="education",
        section_name="Education",
        priority_tier="T3_STANDARD",
        description="Academic credentials and degrees",
        min_length_chars=50,
        max_length_chars=400,
        target_length_chars=200,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "institution_name",
            "degree_earned",
            "graduation_date",
        ],
        optional_elements=[
            "gpa",
            "honors",
            "relevant_coursework",
        ],
        scorer_profile_ref="education_verification_scorer",
        benchmark_set_ref=None,  # Uses standard benchmarks
        seed_set_ref=None,
    ),
    
    "certifications": ResumeSectionDefinition(
        section_id="certifications",
        section_name="Certifications",
        priority_tier="T3_STANDARD",
        description="Professional certifications and credentials",
        min_length_chars=50,
        max_length_chars=300,
        target_length_chars=150,
        g22_factual_grounding_required=True,
        g22_factual_grounding_threshold=0.950,
        required_elements=[
            "certification_name",
            "issuing_body",
            "date_obtained",
        ],
        optional_elements=[
            "expiration_date",
            "credential_id",
        ],
        scorer_profile_ref="certification_validity_scorer",
        benchmark_set_ref=None,
        seed_set_ref=None,
    ),
    
    # T4_MINIMAL sections
    "header": ResumeSectionDefinition(
        section_id="header",
        section_name="Header / Contact",
        priority_tier="T4_MINIMAL",
        description="Name, title, and contact information",
        min_length_chars=30,
        max_length_chars=200,
        target_length_chars=100,
        g22_factual_grounding_required=False,  # Format only
        g22_factual_grounding_threshold=0.0,
        required_elements=[
            "full_name",
            "current_title",
            "contact_email",
            "phone_number",
        ],
        optional_elements=[
            "linkedin_url",
            "location",
        ],
        scorer_profile_ref="header_format_scorer",
        benchmark_set_ref=None,
        seed_set_ref=None,
    ),
}

# Section ordering for resume assembly
SECTION_ASSEMBLY_ORDER: List[str] = [
    "header",
    "executive_summary",
    "competencies",
    "experience",
    "achievements",
    "education",
    "certifications",
]

# Export
__all__ = [
    "ResumeSectionDefinition",
    "CANONICAL_RESUME_SECTIONS",
    "SECTION_ASSEMBLY_ORDER",
]
