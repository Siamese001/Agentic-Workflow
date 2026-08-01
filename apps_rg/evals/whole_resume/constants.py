"""Governed identities and dimensions for whole-resume evaluation."""

from __future__ import annotations

INPUT_SCHEMA_VERSION = "apps_rg.whole_resume_input.v1"
RECEIPT_SCHEMA_VERSION = "apps_rg.whole_resume_evaluation_receipt.v1"
RUBRIC_ID = "apps_rg-whole-resume-quality-v1"
EXPECTED_PAIR_COUNT = 6
EXPECTED_REVIEWS_PER_PAIR = 2

W9_DIMENSIONS = (
    "target_relevance",
    "claim_naturalness",
    "executive_readability",
    "ats_keyword_coverage",
    "authenticity_factuality",
    "concision",
    "hiring_manager_usefulness",
)

REQUIRED_SECTION_IDS = ("headline", "executive_summary", "competencies")
EXPERIENCE_SECTION_SUFFIXES = ("_bullets", "_narrative")

LEADERSHIP_TERMS = (
    "chief",
    "enterprise-wide",
    "executive leader",
    "global leader",
    "headed",
    "led",
    "leadership",
)
SCOPE_TERMS = (
    "company-wide",
    "global",
    "industry-leading",
    "organization-wide",
    "owned",
    "transformed",
)

METRIC_NAMES = (
    "material_claim_grounding_rate",
    "critical_cross_section_inconsistency_count",
    "chronology_inconsistency_count",
    "employer_title_inconsistency_count",
    "duplicate_achievement_rate",
    "summary_experience_repetition_rate",
    "jd_concept_coverage",
    "relevant_achievement_coverage",
    "section_balance_score",
    "resume_word_count",
    "claim_density_per_100_words",
    "ats_structure_pass",
    "narrative_coherence",
    "evidence_backed_personalization",
    "jd_parroting_risk_count",
    "unnatural_keyword_insertion_count",
    "unsupported_leadership_inflation_count",
    "unsupported_scope_inflation_count",
    "human_grounding_no_worse_rate",
    "human_naturalness_no_worse_rate",
    "human_relevance_no_worse_rate",
    "candidate_preference_rate",
    "material_defect_count",
    "reviewer_agreement_rate",
)

__all__ = [
    "EXPECTED_PAIR_COUNT",
    "EXPECTED_REVIEWS_PER_PAIR",
    "EXPERIENCE_SECTION_SUFFIXES",
    "INPUT_SCHEMA_VERSION",
    "LEADERSHIP_TERMS",
    "METRIC_NAMES",
    "RECEIPT_SCHEMA_VERSION",
    "REQUIRED_SECTION_IDS",
    "RUBRIC_ID",
    "SCOPE_TERMS",
    "W9_DIMENSIONS",
]
